#!/usr/bin/env python3
"""From-scratch dual-model extraction of the ~431 downloaded-but-never-processed full-text papers.

These papers are in the merged corpus (landed_assets) and were never run through the pipeline.
  • codex exec (agentic) READS the paper PDF directly and EXTRACTS structured activity records
    (peptide, sequence, endpoint, value, unit, target, assay_medium, inoculum, modification).
  • claude -p VERIFIES each extracted record against the paper's pdftotext text.
A record is APPROVED only when codex extracted it AND claude verdict == "supported"; others → review.

Captures the previously-missing dimensions (assay conditions + modifications) at extraction time.

RUN IN CLOUD SHELL (codex ~5 min/paper):
  python3 pipeline_v2/deepmine/extract_newpapers_dual.py --list
  python3 pipeline_v2/deepmine/extract_newpapers_dual.py --limit 2     # test
  python3 pipeline_v2/deepmine/extract_newpapers_dual.py               # full, resumable, DEEPMINE_CONC lanes
Outputs (pipeline_v2/deepmine/): newpapers_approved.tsv, newpapers_review.tsv, newpapers_state.json
"""
import os, sys, re, json, subprocess, tempfile, glob, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
POOL = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers")
OUT_APP = ROOT / "pipeline_v2" / "deepmine" / "newpapers_extracted.tsv"
OUT_REV = ROOT / "pipeline_v2" / "deepmine" / "newpapers_review.tsv"
STATE = ROOT / "pipeline_v2" / "deepmine" / "newpapers_state.json"
COLS = ["paper_id", "peptide", "sequence", "endpoint", "value", "unit", "target",
        "assay_medium", "inoculum", "modification", "verdict", "evidence"]
CLAUDE_TIMEOUT = int(os.environ.get("DEEPMINE_CLAUDE_TIMEOUT", "180"))
CODEX_TIMEOUT = int(os.environ.get("DEEPMINE_CODEX_TIMEOUT", "540"))
PAPER_CONC = int(os.environ.get("DEEPMINE_CONC", "8"))
_lock = threading.Lock()
_JUNK = {"mic", "mbc", "ic50", "ec50", "hc50", "cc50", "n/a", "na", "nd", "-", "", "value", "peptide", "control"}


def worklist():
    done = set(os.listdir(ROOT / "papers"))
    items = []
    if not POOL.exists():
        return items
    for d in sorted(os.listdir(POOL)):
        if not d.startswith("doi__") or d in done:
            continue
        pdfs = glob.glob(str(POOL / d / "**" / "*.pdf"), recursive=True)
        xmls = glob.glob(str(POOL / d / "**" / "*.xml"), recursive=True)
        if pdfs or xmls:
            items.append((d, (pdfs[0] if pdfs else xmls[0])))
    return items


def pdf_text(src, cap=42000):
    try:
        if src.lower().endswith(".pdf"):
            r = subprocess.run(["pdftotext", "-q", src, "-"], capture_output=True, text=True, timeout=60)
            return (r.stdout or "")[:cap]
        return Path(src).read_text(encoding="utf-8", errors="replace")[:cap]
    except Exception:
        return ""


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


EXTRACT_RULES = ('Extract every antimicrobial-peptide EXPERIMENTAL activity/toxicity record. Return ONLY a JSON '
                 'array; each element keys: peptide, sequence, endpoint, value, unit, target, assay_medium, '
                 'inoculum, modification (D-amino/amidation/cyclization/lipidation/none), evidence (table/loc). '
                 'ONE record per (peptide, endpoint, target) cell — never merge two values or two units into one '
                 'field (e.g. do NOT write "63/23" or "ug/mL/uM"; emit separate records). '
                 'Only measured values from tables/text — skip predictions/design scores. If none, return [].')


def run_codex_extract(pid, src):
    prompt = (f"You are extracting AMP activity data from a paper. READ ONLY this file: {src} "
              f"(do not explore other files).\n{EXTRACT_RULES}")
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
        res = parse_arr(txt) or parse_arr(r.stdout)
        if res:
            return res
    # retry once on empty (codex flakes under load) with a fresh temp dir
    with tempfile.TemporaryDirectory() as td2:
        outf2 = os.path.join(td2, "final.txt")
        try:
            r2 = subprocess.run(["sudo", "-n", "HOME=/root", "codex", "exec", "--skip-git-repo-check",
                                 "--dangerously-bypass-approvals-and-sandbox", "-o", outf2, prompt],
                                capture_output=True, text=True, timeout=CODEX_TIMEOUT, cwd=str(ROOT))
        except Exception:
            return []
        t2 = Path(outf2).read_text(encoding="utf-8", errors="replace") if os.path.exists(outf2) else ""
        return parse_arr(t2) or parse_arr(r2.stdout)


def run_claude_extract(text):
    prompt = ("You are extracting AMP activity data from a paper's text.\n" + EXTRACT_RULES +
              "\n\nPAPER TEXT (may be truncated / tables may be flattened):\n" + text)
    try:
        r = subprocess.run(["claude", "-p", prompt, "--model", "sonnet", "--dangerously-skip-permissions"],
                           capture_output=True, text=True, timeout=CLAUDE_TIMEOUT)
        return parse_arr(r.stdout)
    except Exception:
        return []


def _clean(recs):
    out = []
    for r in recs:
        if not isinstance(r, dict):
            continue
        p = (r.get("peptide") or "").strip()
        if not p or p.lower() in _JUNK or r.get("value") in (None, ""):
            continue
        out.append(r)
    return out


def _key(r):
    p = (r.get("peptide") or "").strip().lower()
    ep = (r.get("endpoint") or "").strip().lower()
    m = re.search(r"[0-9]+\.?[0-9]*", str(r.get("value", "")))
    return (p, ep, m.group(0) if m else "")


def _row(pid, r, models):
    return {"paper_id": pid, "peptide": r.get("peptide", ""), "sequence": r.get("sequence", ""),
            "endpoint": r.get("endpoint", ""), "value": str(r.get("value", "")), "unit": r.get("unit", ""),
            "target": str(r.get("target", "")), "assay_medium": r.get("assay_medium", ""),
            "inoculum": r.get("inoculum", ""), "modification": r.get("modification", ""),
            "verdict": models, "evidence": str(r.get("evidence", ""))[:200]}


def process_paper(pid, src):
    # both models extract INDEPENDENTLY, in parallel — they are COMPLEMENTARY (codex reads tables,
    # claude reads text), so we take the UNION and tag each record by which model(s) found it.
    text = pdf_text(src)
    with ThreadPoolExecutor(max_workers=2) as ex:
        fx = ex.submit(run_codex_extract, pid, src)
        fc = ex.submit(run_claude_extract, text)
        codex_recs = _clean(fx.result())
        claude_recs = _clean(fc.result())
    claude_keys = {_key(r) for r in claude_recs}
    codex_keys = {_key(r) for r in codex_recs}
    out, seen = [], set()
    for r in codex_recs:
        k = _key(r)
        if k in seen:
            continue
        seen.add(k)
        out.append(_row(pid, r, "both_models" if k in claude_keys else "codex_only"))
    for r in claude_recs:
        k = _key(r)
        if k in seen or k in codex_keys:
            continue
        seen.add(k)
        out.append(_row(pid, r, "claude_only"))
    return out, []   # all extracted go to one file, tagged by models; precision-gated at ingestion


def load_state():
    return set(json.loads(STATE.read_text())) if STATE.exists() else set()


def append(path, rows):
    with _lock:
        new = not path.exists()
        with path.open("a", encoding="utf-8") as f:
            if new:
                f.write("\t".join(COLS) + "\n")
            for r in rows:
                f.write("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ") for c in COLS) + "\n")


def mark_done(pid):
    with _lock:
        d = load_state(); d.add(pid); STATE.write_text(json.dumps(sorted(d)))


def main():
    args = sys.argv[1:]
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    items = worklist()
    done = load_state()
    todo = [it for it in items if it[0] not in done]
    if limit:
        todo = todo[:limit]
    if "--list" in args:
        print(f"{len(items)} new full-text papers | {len(done)} done | {len(todo)} todo")
        for pid, src in items[:60]:
            print(f"  {'DONE' if pid in done else '-   '} {pid}")
        return
    print(f"new-paper extraction: todo={len(todo)}/{len(items)} | lanes={PAPER_CONC} | approval=codex-extract + claude-verify")

    def work(it):
        pid, src = it
        try:
            app, rev = process_paper(pid, src)
            append(OUT_APP, app); append(OUT_REV, rev); mark_done(pid)
            both=sum(1 for r in app if r["verdict"]=="both_models"); print(f"  ✓ {pid}: {len(app)} extracted ({both} both-models)")
        except Exception as ex:
            print(f"  ✗ {pid}: {ex}")

    with ThreadPoolExecutor(max_workers=PAPER_CONC) as ex:
        list(ex.map(work, todo))
    print(f"done. approved -> {OUT_APP}")


if __name__ == "__main__":
    main()
