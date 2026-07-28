#!/usr/bin/env python3
"""Batch 1: extract the ~1,340 NEW DBAASP full-text papers (mostly PMC OA — clean XML/PDF).

claude-only with cross-validation (two independent passes; codex is rate-limited). RATE-LIMIT
RESILIENT: if claude is rate-limited, the paper is NOT marked done, so a supervising re-run picks
it up once quota resets. XML tables are converted to grids (structure preserved) for high yield.

Outputs: dbaasp_extracted.tsv, dbaasp_state.json  (reads dbaasp_worklist.json)
Env: DEEPMINE_CONC (lanes, default 24)
"""
import os, sys, re, json, subprocess, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import tempfile
import extract_newpapers_dual as base

ROOT = base.ROOT
WORK = ROOT / "pipeline_v2" / "deepmine" / "dbaasp_worklist.json"
OUT = ROOT / "pipeline_v2" / "deepmine" / "dbaasp_extracted.tsv"
STATE = ROOT / "pipeline_v2" / "deepmine" / "dbaasp_state.json"
EMPTY_DONE = ROOT / "pipeline_v2" / "deepmine" / "dbaasp_empty_done.tsv"
CONC = int(os.environ.get("DEEPMINE_CONC", "24"))
PROVIDER = os.environ.get("DBAASP_PROVIDER", "claude").strip().lower()
CODEX_TIMEOUT = int(os.environ.get("DEEPMINE_CODEX_TIMEOUT", "420"))
CAP = 46000
_lock = threading.Lock()
_RL = re.compile(r'rate limit|usage limit|429|overloaded|quota|too many requests|please try again|resource_exhausted|exceeded', re.I)
EMPTY_COLS = ["paper_id", "provider", "source_path", "source_kind", "completed_at", "note"]
_BAD_LITERAL = {"none", "n/a", "na", "null"}
_NEGATIVE_VALUE = re.compile(r"\b(no inhibitory effect|inactive|not active|no activity|none detected)\b", re.I)


def now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def append_empty_done(key, path, kind, note="provider returned no usable activity records"):
    with _lock:
        new = not EMPTY_DONE.exists()
        with EMPTY_DONE.open("a", encoding="utf-8") as f:
            if new:
                f.write("\t".join(EMPTY_COLS) + "\n")
            row = {
                "paper_id": key,
                "provider": PROVIDER,
                "source_path": path,
                "source_kind": kind,
                "completed_at": now_iso(),
                "note": note,
            }
            f.write("\t".join(str(row.get(c, "")).replace("\t", " ").replace("\n", " ") for c in EMPTY_COLS) + "\n")


def table_grid(block):
    rows = []
    for tr in re.findall(r'(?is)<tr.*?</tr>', block):
        cells = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', c)).strip()
                 for c in re.findall(r'(?is)<(?:t[hd]|entry).*?>(.*?)</(?:t[hd]|entry)>', tr)]
        if any(cells):
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def source_text(path, kind):
    try:
        raw = open(path, encoding="utf-8", errors="replace").read() if kind == "xml" else \
            subprocess.run(["pdftotext", "-q", path, "-"], capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return ""
    if kind == "xml":
        grids = [table_grid(t) for t in re.findall(r'(?is)<table.*?</table>', raw)]
        body = re.sub(r'(?is)<(ref-list|back|table).*?</\1>', ' ', raw)
        body = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body)).strip()
        txt = "TEXT:\n" + body[:34000] + "\n\nDATA TABLES:\n" + "\n\n---\n\n".join(g for g in grids if g)
        return txt[:CAP]
    return raw[:CAP]


def claude_cmd(prompt):
    cmd = ["claude", "-p", prompt, "--model", "sonnet"]
    if os.geteuid() != 0 or os.environ.get("DEEPMINE_CLAUDE_DANGEROUS") == "1":
        cmd.append("--dangerously-skip-permissions")
    return cmd


def claude_status(text):
    """Return (records, status) — status 'ok' | 'ratelimited' | 'error'."""
    prompt = ("You are extracting AMP activity data from a paper.\n" + base.EXTRACT_RULES + "\n"
              "DBAASP pending-layer strictness: emit only measured positive/quantitative rows with a numeric, "
              "comparator, or range value. Do not emit negative qualitative rows such as 'no inhibitory effect' "
              "or 'inactive'. Use an empty string instead of literal None/null/NA.\n"
              "\n\nPAPER:\n" + text)
    try:
        r = subprocess.run(claude_cmd(prompt), capture_output=True, text=True, timeout=200)
    except Exception:
        return [], "error"
    blob = (r.stdout or "") + " " + (r.stderr or "")
    recs = base.parse_arr(r.stdout)
    if recs:
        return recs, "ok"
    if _RL.search(blob):
        return [], "ratelimited"
    if r.returncode != 0:
        return [], "error"
    return [], "ok"   # genuine empty (model saw text, found nothing)


def codex_status(text):
    """Return (records, status) for the Codex fallback provider."""
    prompt = ("You are extracting AMP activity data from a paper text. "
              "Use ONLY the text in this prompt; do not inspect files or run shell commands.\n"
              + base.EXTRACT_RULES + "\n"
              "DBAASP pending-layer strictness: emit only measured positive/quantitative rows with a numeric, "
              "comparator, or range value. Do not emit negative qualitative rows such as 'no inhibitory effect' "
              "or 'inactive'. Use an empty string instead of literal None/null/NA.\n"
              "\n\nPAPER TEXT:\n" + text)
    with tempfile.TemporaryDirectory() as td:
        outf = Path(td) / "dbaasp_codex_extract.txt"
        cmd = [
            "codex", "exec", "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox",
            "-C", str(ROOT), "-o", str(outf), "-",
        ]
        try:
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=CODEX_TIMEOUT)
        except subprocess.TimeoutExpired as ex:
            recs = base.parse_arr(ex.stdout if isinstance(ex.stdout, str) else "")
            return (recs, "ok") if recs else ([], "error")
        except Exception:
            return [], "error"
        out_text = outf.read_text(encoding="utf-8", errors="replace") if outf.exists() else ""
    blob = out_text + "\n" + (r.stdout or "") + "\n" + (r.stderr or "")
    recs = base.parse_arr(out_text) or base.parse_arr(r.stdout)
    if recs:
        return recs, "ok"
    if _RL.search(blob):
        return [], "ratelimited"
    if r.returncode != 0:
        return [], "error"
    return [], "ok"


def provider_status(text):
    if PROVIDER == "claude":
        return claude_status(text)
    if PROVIDER == "codex":
        return codex_status(text)
    raise SystemExit(f"unsupported DBAASP_PROVIDER={PROVIDER!r}; expected claude or codex")


def clean_records(recs):
    cleaned = []
    for rec in base._clean(recs):
        out = dict(rec)
        for field in ("sequence", "unit", "modification"):
            if str(out.get(field, "")).strip().lower() in _BAD_LITERAL:
                out[field] = ""
        value = str(out.get("value", "")).strip()
        if _NEGATIVE_VALUE.search(value):
            continue
        if not re.search(r"\d", value):
            continue
        cleaned.append(out)
    return cleaned


def load_state():
    return set(json.loads(STATE.read_text())) if STATE.exists() else set()


def parse_limit(args):
    raw = os.environ.get("DEEPMINE_LIMIT", "")
    if "--limit" in args:
        raw = args[args.index("--limit") + 1]
    if raw == "":
        return None
    try:
        limit = int(raw)
    except ValueError:
        raise SystemExit(f"invalid --limit/DEEPMINE_LIMIT: {raw!r}")
    if limit < 0:
        raise SystemExit("--limit/DEEPMINE_LIMIT must be >= 0")
    return limit


def process(key, path, kind):
    text = source_text(path, kind)
    if len(text) < 400:
        return [], "ok"   # no content → done (nothing to extract)
    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(provider_status, text)
        f2 = ex.submit(provider_status, text + "\n ")
        r1, s1 = f1.result()
        r2, s2 = f2.result()
    if s1 != "ok" and s2 != "ok":
        return None, "ratelimited" if "ratelimited" in (s1, s2) else "error"
    a = clean_records(r1); b = clean_records(r2)
    bk = {base._key(x) for x in b}
    out, seen = [], set()
    for x in a:
        k = base._key(x)
        if k in seen:
            continue
        seen.add(k); out.append(base._row(key, x, f"{PROVIDER}_x2" if k in bk else f"{PROVIDER}_1"))
    for x in b:
        k = base._key(x)
        if k in seen:
            continue
        seen.add(k); out.append(base._row(key, x, f"{PROVIDER}_1"))
    return out, "ok"


def main():
    args = sys.argv[1:]
    work = json.loads(WORK.read_text())
    done = load_state()
    todo_all = [w for w in work if w[0] not in done]
    limit = parse_limit(args)
    todo = todo_all[:limit] if limit is not None else todo_all
    if "--list" in args:
        suffix = f" | selected={len(todo)} (limit={limit})" if limit is not None else ""
        print(f"{len(work)} DBAASP papers | {len(done)} done | {len(todo_all)} todo{suffix}")
        return
    print(f"DBAASP extraction: todo={len(todo)}/{len(work)} | total_todo={len(todo_all)} | lanes={CONC} | provider={PROVIDER}"
          + (f" | limit={limit}" if limit is not None else ""))
    if not todo:
        print("nothing selected; no files modified")
        return
    rl = {"n": 0}
    errors = {"n": 0}

    def work_one(w):
        key, path, kind = w
        try:
            rows, status = process(key, path, kind)
            if status == "ratelimited":
                with _lock:
                    rl["n"] += 1
                return
            if status == "error":
                with _lock:
                    errors["n"] += 1
                return
            base.append(OUT, rows)
            if not rows:
                append_empty_done(key, path, kind)
            with _lock:
                d = load_state(); d.add(key); STATE.write_text(json.dumps(sorted(d)))
            if rows:
                print(f"  ✓ {key}: {len(rows)}")
        except Exception as ex:
            print(f"  ✗ {key}: {ex}")

    with ThreadPoolExecutor(max_workers=CONC) as ex:
        list(ex.map(work_one, todo))
    print(f"round done. rate-limited this round: {rl['n']} | provider/errors this round: {errors['n']} | total done: {len(load_state())}/{len(work)}")


if __name__ == "__main__":
    main()
