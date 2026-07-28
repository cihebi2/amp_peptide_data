#!/usr/bin/env python3
"""Stage 2 of "process ALL documents": the ~725 papers whose only landed asset is HTML (.bin).

These papers' download captured the publisher HTML page (mislabeled .bin), not a clean PDF/XML.
The HTML still holds real content (abstract + often full-text/tables). We strip tags → text and
run the SAME validated union extraction (claude from text; codex from a temp .txt of that text).
Papers whose HTML is a pure paywall stub yield nothing — that's expected and recorded.

Outputs: supphtml_extracted.tsv, supphtml_state.json  (separate from the full-text stage)
  python3 pipeline_v2/deepmine/extract_supphtml_dual.py --list
  python3 pipeline_v2/deepmine/extract_supphtml_dual.py --limit 3
  python3 pipeline_v2/deepmine/extract_supphtml_dual.py           # full, DEEPMINE_CONC lanes
"""
import os, sys, re, json, glob, tempfile, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import extract_newpapers_dual as base   # reuse EXTRACT_RULES, parse_arr, _clean, _key, _row, run_claude_extract, run_codex_extract

ROOT = base.ROOT
POOL = base.POOL
OUT = ROOT / "pipeline_v2" / "deepmine" / "supphtml_extracted.tsv"
STATE = ROOT / "pipeline_v2" / "deepmine" / "supphtml_state.json"
COLS = base.COLS
CONC = int(os.environ.get("DEEPMINE_CONC", "8"))
MIN_TEXT = 4000            # below this the HTML is a stub, skip extraction
CAP = 42000


def strip_html(h):
    h = re.sub(r'(?is)<(script|style|head|nav|footer|header|svg).*?</\1>', ' ', h)
    h = re.sub(r'(?s)<[^>]+>', ' ', h)
    h = re.sub(r'&[a-z]+;', ' ', h)
    return re.sub(r'\s+', ' ', h).strip()


def html_source(pid):
    cands = glob.glob(f"{POOL}/{pid}/**/*.bin", recursive=True) + glob.glob(f"{POOL}/{pid}/**/*.html", recursive=True)
    best = ""
    for c in sorted(set(cands), key=lambda p: -os.path.getsize(p)):
        try:
            t = strip_html(open(c, encoding="utf-8", errors="replace").read())
        except Exception:
            continue
        if len(t) > len(best):
            best = t
    return best[:CAP]


def worklist():
    done = set(os.listdir(ROOT / "papers"))
    items = []
    for d in sorted(os.listdir(POOL)):
        if not d.startswith("doi__") or d in done:
            continue
        files = glob.glob(f"{POOL}/{d}/**/*", recursive=True)
        if any(f.lower().endswith(('.pdf', '.xml')) for f in files):
            continue   # handled by the full-text stage
        if any(f.lower().endswith(('.bin', '.html')) for f in files):
            items.append(d)
    return items


def load_state():
    return set(json.loads(STATE.read_text())) if STATE.exists() else set()


def process(pid):
    text = html_source(pid)
    if len(text) < MIN_TEXT:
        return []   # paywall stub / no content
    # claude-only: it reads the stripped HTML text directly and is the reliable text extractor;
    # codex adds nothing here (same text) and is slow on a plain .txt. Most HTML is paywalled → 0.
    claude_recs = base._clean(base.run_claude_extract(text))
    out, seen = [], set()
    for r in claude_recs:
        k = base._key(r)
        if k in seen:
            continue
        seen.add(k); out.append(base._row(pid, r, "claude_html"))
    return out


def main():
    args = sys.argv[1:]
    items = worklist()
    done = load_state()
    todo = [p for p in items if p not in done]
    if "--limit" in args:
        todo = todo[:int(args[args.index("--limit") + 1])]
    if "--list" in args:
        print(f"{len(items)} HTML-only papers | {len(done)} done | {len(todo)} todo")
        return
    print(f"supp-HTML extraction: todo={len(todo)}/{len(items)} | lanes={CONC}")

    def work(pid):
        try:
            rows = process(pid)
            base.append(OUT, rows)
            with base._lock:
                d = load_state(); d.add(pid); STATE.write_text(json.dumps(sorted(d)))
            print(f"  ✓ {pid}: {len(rows)} extracted")
        except Exception as ex:
            print(f"  ✗ {pid}: {ex}")

    with ThreadPoolExecutor(max_workers=CONC) as ex:
        list(ex.map(work, todo))
    print(f"done -> {OUT}")


if __name__ == "__main__":
    main()
