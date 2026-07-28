#!/usr/bin/env python3
"""Recover activity records from EXCLUDED papers with dual-model verification + approval gate.

The 97 excluded papers (blocked / needs-rework) hold ~6,423 already-extracted activity records that
never entered the public release. This driver re-verifies each record against the PRIMARY paper with
TWO independent models and only APPROVES a record for recovery when BOTH agree it is supported —
disagreements go to a human review queue (the 复核审批 gate).

  • claude -p (sonnet)  — fast: the paper's source text is inlined into the prompt.
  • codex exec (agentic) — deep: told to READ the paper's source file itself and check each value.

A record is APPROVED iff claude_verdict == codex_verdict == "supported".
Others (disagree / not_supported / uncertain) → review queue.

Lanes: 5 codex + 5 claude (set DEEPMINE_CONC=5 → 5 papers in flight, each running claude+codex).
RUN IN CLOUD SHELL (codex ~4-5 min/paper; ~64 papers with records):
  cd /home/cihebi/抗菌肽/数据集/batch/5-team
  python3 pipeline_v2/deepmine/recover_excluded_dual.py --list
  python3 pipeline_v2/deepmine/recover_excluded_dual.py --limit 2        # smoke test
  python3 pipeline_v2/deepmine/recover_excluded_dual.py                  # full, resumable
  python3 pipeline_v2/deepmine/recover_excluded_dual.py --models claude  # fast claude-only pass
Outputs (pipeline_v2/deepmine/):
  recovered_approved.tsv     — dual-consensus "supported" records (ready to ingest as a tier)
  recovered_review_queue.tsv — disagreements / not_supported / uncertain (need human 审批)
  recovered_state.json       — done paper_ids (resume)
"""
import os, sys, re, json, csv, subprocess, tempfile, glob, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

csv.field_size_limit(10**9)
ROOT = Path(__file__).resolve().parents[2]
REL = ROOT / "releases" / "amp_evidence_atlas_v1_rc2"
OUT_APP = ROOT / "pipeline_v2" / "deepmine" / "recovered_approved.tsv"
OUT_REV = ROOT / "pipeline_v2" / "deepmine" / "recovered_review_queue.tsv"
STATE = ROOT / "pipeline_v2" / "deepmine" / "recovered_state.json"
COLS = ["paper_id", "record_id", "entity", "endpoint", "raw_value", "raw_unit", "target",
        "claude_verdict", "codex_verdict", "approved", "evidence", "corrected_value"]
CLAUDE_TIMEOUT = int(os.environ.get("DEEPMINE_CLAUDE_TIMEOUT", "180"))
CODEX_TIMEOUT = int(os.environ.get("DEEPMINE_CODEX_TIMEOUT", "480"))
PAPER_CONC = int(os.environ.get("DEEPMINE_CONC", "5"))       # 5 papers → 5 codex + 5 claude lanes
REC_PER_CALL = int(os.environ.get("DEEPMINE_REC_PER_CALL", "40"))
_lock = threading.Lock()

RECOVERED_4 = {"doi__10.1038_s41422-022-00617-x", "doi__10.1038_s41423-020-0374-2",
               "doi__10.1080_22221751.2021.1937329", "doi__10.3390_v11010031"}


def worklist():
    excl = set()
    for r in csv.DictReader((REL / "papers.tsv").open(encoding="utf-8"), delimiter="\t"):
        pub = (r.get("public_v1_included", "") or "").lower() in ("true", "1", "yes")
        if not pub and r["paper_id"] not in RECOVERED_4:
            excl.add(r["paper_id"])
    items = []
    for pid in sorted(excl):
        recs = load_records(pid)
        if recs:
            items.append((pid, recs))
    return items


_JUNK_ENTITY = {"mic", "mbc", "ic50", "ec50", "hc50", "cc50", "mbec", "mbic", "fici", "ki", "kd",
                "ec90", "mic50", "mic90", "n/a", "na", "nd", "nt", "-", "", "value", "peptide",
                "control", "none", "compound", "sample"}


def is_junk_entity(e):
    e = (e or "").strip()
    if not e or e.lower() in _JUNK_ENTITY or len(e) < 2:
        return True
    return not re.search(r"[A-Za-z]", e)  # must contain a letter (a peptide name, not a bare number)


def load_records(pid):
    f = ROOT / "papers" / pid / "final" / "activity_toxicity_evidence.json"
    if not f.exists():
        return []
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    for a in (d.get("activity_records") or []):
        if is_junk_entity(a.get("entity", "")):
            continue  # no usable peptide identity — skip (don't waste verification on it)
        tgt = a.get("target")
        tgt = json.dumps(tgt, ensure_ascii=False) if isinstance(tgt, (dict, list)) else str(tgt or "")
        out.append({"record_id": a.get("record_id", ""), "entity": a.get("entity", ""),
                    "endpoint": a.get("endpoint", ""), "raw_value": str(a.get("raw_value", "")),
                    "raw_unit": a.get("raw_unit", ""), "target": tgt})
    return out


_PRIORITY = re.compile(r"result|activ|table|mic|toxic|hemol|cytotox|inhibit|potenc|assay|discussion", re.I)


def source_text(pid, cap=18000):
    f = ROOT / "paper_packets" / pid / "extracted" / "xml_sections.json"
    if not f.exists():
        return ""
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return ""
    secs = d.get("sections") or d.get("body") or d
    if isinstance(secs, dict):
        secs = list(secs.values())
    seen, uniq = set(), []
    for s in (secs if isinstance(secs, list) else []):
        if not isinstance(s, dict):
            s = {"text": str(s)}
        t = (s.get("text") or "").strip()
        title = str(s.get("title") or s.get("heading") or s.get("label") or "")
        if not t or t in seen:
            continue
        seen.add(t)
        # priority score: results/activity/table sections first, then keyword hits in body
        pri = 0 if _PRIORITY.search(title) else (1 if _PRIORITY.search(t[:400]) else 2)
        uniq.append((pri, title, t))
    uniq.sort(key=lambda x: x[0])
    out, n = [], 0
    # figure/table captions first — numeric activity values often live in tables/figures
    fc = ROOT / "paper_packets" / pid / "extracted" / "figure_captions.json"
    if fc.exists():
        try:
            figs = (json.loads(fc.read_text(encoding="utf-8")).get("figures") or [])
            caps = "\n".join(f"[{f.get('label','')}] {f.get('caption','')}" for f in figs if f.get("caption"))
            if caps:
                out.append("## FIGURE/TABLE CAPTIONS\n" + caps); n += len(caps)
        except Exception:
            pass
    for _pri, title, t in uniq:
        block = (f"## {title}\n{t}" if title else t)
        out.append(block); n += len(block)
        if n >= cap:
            break
    return ("\n".join(out))[:cap]


def parse_arr(text):
    if not text:
        return []
    best = []
    for mi in re.finditer(r"\[", text):
        i = mi.start(); depth = 0
        for k in range(i, len(text)):
            if text[k] == "[":
                depth += 1
            elif text[k] == "]":
                depth -= 1
                if depth == 0:
                    try:
                        d = json.loads(text[i:k + 1])
                        if isinstance(d, list) and len(d) >= len(best):
                            best = d
                    except Exception:
                        pass
                    break
    return best


RULES = ("For each record decide whether the paper SUPPORTS the exact (entity, endpoint, raw_value, "
         "raw_unit, target). Return ONLY a JSON array; one object per record_id: "
         '{"record_id","verdict":"supported"|"not_supported"|"uncertain","evidence":"short quote or table/loc",'
         '"corrected_value":""}. Base it strictly on the paper; do not guess.')


def claude_prompt(pid, recs, text):
    rj = json.dumps(recs, ensure_ascii=False)
    return (f"You are verifying extracted antimicrobial-peptide activity records against the source paper.\n{RULES}\n\n"
            f"PAPER {pid} — source text (may be truncated):\n{text}\n\nRECORDS:\n{rj}")


def codex_prompt(pid, recs):
    rj = json.dumps(recs, ensure_ascii=False)
    return (f"You are verifying extracted antimicrobial-peptide activity records against the source paper.\n"
            f"READ ONLY this file for evidence: papers/{pid}/source/paper.xml (fall back to "
            f"papers/{pid}/source/paper.pdf if the xml is absent). Do NOT explore other files.\n{RULES}\n\n"
            f"RECORDS:\n{rj}")


def run_claude(prompt):
    try:
        r = subprocess.run(["claude", "-p", prompt, "--model", "sonnet", "--dangerously-skip-permissions"],
                           capture_output=True, text=True, timeout=CLAUDE_TIMEOUT)
        return parse_arr(r.stdout)
    except Exception:
        return []


def run_codex(prompt):
    with tempfile.TemporaryDirectory() as td:
        outf = os.path.join(td, "final.txt")
        try:
            r = subprocess.run(["sudo", "-n", "HOME=/root", "codex", "exec", "--skip-git-repo-check",
                                "--dangerously-bypass-approvals-and-sandbox", "-o", outf, prompt],
                               capture_output=True, text=True, timeout=CODEX_TIMEOUT, cwd=str(ROOT))
        except subprocess.TimeoutExpired as e:
            return parse_arr(e.stdout if isinstance(e.stdout, str) else "")
        except Exception:
            return []
        txt = Path(outf).read_text(encoding="utf-8", errors="replace") if os.path.exists(outf) else ""
        return parse_arr(txt) or parse_arr(r.stdout)


def verdict_map(arr):
    m = {}
    for o in arr:
        if isinstance(o, dict) and o.get("record_id"):
            m[o["record_id"]] = o
    return m


def process_paper(pid, recs, models):
    approved, review = [], []
    for i in range(0, len(recs), REC_PER_CALL):
        chunk = recs[i:i + REC_PER_CALL]
        with ThreadPoolExecutor(max_workers=2) as ex:
            fc = ex.submit(run_claude, claude_prompt(pid, chunk, source_text(pid))) if models in ("both", "claude") else None
            fx = ex.submit(run_codex, codex_prompt(pid, chunk)) if models in ("both", "codex") else None
            cl = verdict_map(fc.result()) if fc else {}
            cx = verdict_map(fx.result()) if fx else {}
        for r in chunk:
            rid = r["record_id"]
            cv = (cl.get(rid, {}) or {}).get("verdict", "") if models in ("both", "claude") else "n/a"
            xv = (cx.get(rid, {}) or {}).get("verdict", "") if models in ("both", "codex") else "n/a"
            ev = (cx.get(rid, {}) or {}).get("evidence", "") or (cl.get(rid, {}) or {}).get("evidence", "")
            corr = (cx.get(rid, {}) or {}).get("corrected_value", "") or (cl.get(rid, {}) or {}).get("corrected_value", "")
            if models == "both":
                ok = (cv == "supported" and xv == "supported")
            else:
                ok = ((cv if models == "claude" else xv) == "supported")
            row = {**r, "paper_id": pid, "claude_verdict": cv, "codex_verdict": xv, "approved": ok,
                   "evidence": str(ev)[:300], "corrected_value": str(corr)[:80]}
            (approved if ok else review).append(row)
    return approved, review


def load_state():
    return set(json.loads(STATE.read_text())) if STATE.exists() else set()


def append(path, rows, header_written):
    with _lock:
        new = not path.exists()
        with path.open("a", encoding="utf-8") as f:
            if new:
                f.write("\t".join(COLS) + "\n")
            for r in rows:
                f.write("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ") for c in COLS) + "\n")


def mark_done(pid):
    with _lock:
        done = load_state(); done.add(pid); STATE.write_text(json.dumps(sorted(done)))


def main():
    args = sys.argv[1:]
    models = args[args.index("--models") + 1] if "--models" in args else "both"
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    items = worklist()
    done = load_state()
    todo = [it for it in items if it[0] not in done]
    if limit:
        todo = todo[:limit]
    if "--list" in args:
        tot = sum(len(r) for _, r in items)
        print(f"{len(items)} excluded papers with records | {tot} records | {len(done)} done")
        for pid, recs in items[:70]:
            print(f"  {'DONE' if pid in done else '-   '} recs={len(recs):5d}  {pid}")
        return
    print(f"models={models} todo={len(todo)}/{len(items)} papers  lanes={PAPER_CONC}(×2 models)  approval=dual-consensus")

    def work(it):
        pid, recs = it
        try:
            app, rev = process_paper(pid, recs, models)
            append(OUT_APP, app, True)
            append(OUT_REV, rev, True)
            mark_done(pid)
            print(f"  ✓ {pid}: {len(app)} approved / {len(rev)} → review  (of {len(recs)})")
        except Exception as ex:
            print(f"  ✗ {pid}: {ex}")

    with ThreadPoolExecutor(max_workers=PAPER_CONC) as ex:
        list(ex.map(work, todo))
    print(f"done. approved → {OUT_APP} | review queue → {OUT_REV}")


if __name__ == "__main__":
    main()
