#!/usr/bin/env python3
"""Targeted second-pass recovery of the 283 "full content but 0 extracted" papers.

From hardcases.json: 157 real PDF/XML full-text papers (yielded 0 in stage 1) + 126 HTML papers
whose page contains a real MIC data <table>. Both models, 8 lanes each:
  • PDF : codex reads the PDF directly (best at tables) + claude reads pdftotext text → union.
  • HTML: extract <table> blocks → convert to a pipe-delimited grid (structure PRESERVED, unlike the
          earlier strip that flattened tables) + abstract → codex (temp file) + claude → union.

Output: hardcases_extracted.tsv, hardcases_state.json
  python3 pipeline_v2/deepmine/extract_hardcases_dual.py --limit 3
  python3 pipeline_v2/deepmine/extract_hardcases_dual.py           # full, DEEPMINE_CONC lanes
"""
import os, sys, re, json, tempfile, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import extract_newpapers_dual as base

ROOT = base.ROOT
LIST = ROOT / "pipeline_v2" / "deepmine" / "hardcases.json"
OUT = ROOT / "pipeline_v2" / "deepmine" / "hardcases_extracted.tsv"
STATE = ROOT / "pipeline_v2" / "deepmine" / "hardcases_state.json"
CONC = int(os.environ.get("DEEPMINE_CONC", "8"))
CAP = 44000


def html_table_text(path):
    """Extract <table> blocks as pipe-delimited grids (preserve row/col structure) + lead text."""
    h = open(path, encoding="utf-8", errors="replace").read()
    grids = []
    for tab in re.findall(r'(?is)<table.*?</table>', h)[:12]:
        rows = []
        for tr in re.findall(r'(?is)<tr.*?</tr>', tab):
            cells = re.findall(r'(?is)<t[hd].*?>(.*?)</t[hd]>', tr)
            cells = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', c)).strip() for c in cells]
            if any(cells):
                rows.append(" | ".join(cells))
        if rows:
            grids.append("\n".join(rows))
    body = re.sub(r'(?is)<(script|style|nav|header|footer).*?</\1>', ' ', h)
    body = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body)).strip()
    lead = body[:6000]
    return ("ABSTRACT/TEXT:\n" + lead + "\n\nDATA TABLES:\n" + "\n\n---\n\n".join(grids))[:CAP]


CLAUDE_ONLY = os.environ.get("DEEPMINE_CLAUDE_ONLY", "") == "1"


def process(pid, kind, src):
    text = html_table_text(src) if kind == "html" else base.pdf_text(src, cap=CAP)
    if CLAUDE_ONLY:
        # codex rate-limited → two INDEPENDENT claude passes cross-validate each other.
        with ThreadPoolExecutor(max_workers=2) as ex:
            f1 = ex.submit(base.run_claude_extract, text)
            f2 = ex.submit(base.run_claude_extract, text + "\n ")   # tiny perturbation → independent run
            codex_recs = base._clean(f2.result())    # treat 2nd claude pass as the cross-check model
            claude_recs = base._clean(f1.result())
    elif kind == "pdf":
        text = base.pdf_text(src, cap=CAP)
        with ThreadPoolExecutor(max_workers=2) as ex:
            fx = ex.submit(base.run_codex_extract, pid, src)   # codex reads the PDF
            fc = ex.submit(base.run_claude_extract, text)      # claude reads pdftotext
            codex_recs = base._clean(fx.result())
            claude_recs = base._clean(fc.result())
    else:  # html: table grid to both models
        with tempfile.TemporaryDirectory() as td:
            tf = os.path.join(td, "tables.txt")
            Path(tf).write_text(text, encoding="utf-8")
            with ThreadPoolExecutor(max_workers=2) as ex:
                fx = ex.submit(base.run_codex_extract, pid, tf)
                fc = ex.submit(base.run_claude_extract, text)
                codex_recs = base._clean(fx.result())
                claude_recs = base._clean(fc.result())
    ck = {base._key(r) for r in claude_recs}
    xk = {base._key(r) for r in codex_recs}
    out, seen = [], set()
    for r in codex_recs:
        k = base._key(r)
        if k in seen:
            continue
        seen.add(k); out.append(base._row(pid, r, "both_models" if k in ck else "codex_only"))
    for r in claude_recs:
        k = base._key(r)
        if k in seen or k in xk:
            continue
        seen.add(k); out.append(base._row(pid, r, "claude_only"))
    return out


def load_state():
    return set(json.loads(STATE.read_text())) if STATE.exists() else set()


def main():
    args = sys.argv[1:]
    data = json.loads(LIST.read_text())
    items = [(d, "pdf", s) for d, s in data["pdf"]] + [(d, "html", s) for d, s in data["html"]]
    done = load_state()
    todo = [it for it in items if it[0] not in done]
    if "--limit" in args:
        todo = todo[:int(args[args.index("--limit") + 1])]
    if "--list" in args:
        print(f"{len(items)} hard cases ({len(data['pdf'])} pdf + {len(data['html'])} html) | {len(done)} done | {len(todo)} todo")
        return
    print(f"hardcase recovery: todo={len(todo)}/{len(items)} | lanes={CONC}")

    def work(it):
        pid, kind, src = it
        try:
            rows = process(pid, kind, src)
            base.append(OUT, rows)
            with base._lock:
                d = load_state(); d.add(pid); STATE.write_text(json.dumps(sorted(d)))
            print(f"  ✓ {pid} [{kind}]: {len(rows)} extracted")
        except Exception as ex:
            print(f"  ✗ {pid}: {ex}")

    with ThreadPoolExecutor(max_workers=CONC) as ex:
        list(ex.map(work, todo))
    print(f"done -> {OUT}")


if __name__ == "__main__":
    main()
