#!/usr/bin/env python3
"""Extract mechanism-of-action claims from the newly-processed papers (machine tier).

The activity extractors captured MIC/target data but not mechanism claims. This pass reads the
same papers that yielded activity records and pulls mechanism-of-action statements (membrane
permeabilization, LPS binding, intracellular target, etc.) with an evidence class, so the new
papers contribute to the mechanism table too.

Source text: PDF → pdftotext; HTML(.bin) → strip; claude-only extraction.
Output: mechanism_extracted.tsv, mechanism_state.json
  python3 pipeline_v2/deepmine/extract_mechanism_dual.py --limit 3
  python3 pipeline_v2/deepmine/extract_mechanism_dual.py
"""
import os, sys, re, json, glob, csv, subprocess, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import extract_newpapers_dual as base

ROOT = base.ROOT
POOL = base.POOL
OUT = ROOT / "pipeline_v2" / "deepmine" / "mechanism_extracted.tsv"
STATE = ROOT / "pipeline_v2" / "deepmine" / "mechanism_state.json"
COLS = ["paper_id", "claim_text", "evidence_class", "direct_assay_types", "limitations"]
CONC = int(os.environ.get("DEEPMINE_CONC", "10"))
CAP = 40000
_lock = threading.Lock()

RULES = ('Extract every MECHANISM-OF-ACTION claim about an antimicrobial peptide in this paper. '
         'Return ONLY a JSON array; each element keys: claim_text (one sentence), '
         'evidence_class (direct_assay|indirect|inferred|hypothesis), '
         'direct_assay_types (e.g. "membrane permeabilization, DNA binding"; "" if none), '
         'limitations (caveats or ""). Only claims the paper actually makes/supports. If none, [].')


def strip_html(h):
    h = re.sub(r'(?is)<(script|style|head|nav|footer|header|svg).*?</\1>', ' ', h)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)).strip()


def get_text(pid):
    files = glob.glob(f"{POOL}/{pid}/**/*", recursive=True)
    pdfs = [f for f in files if f.lower().endswith('.pdf')]
    if pdfs:
        try:
            t = subprocess.run(["pdftotext", "-q", pdfs[0], "-"], capture_output=True, text=True, timeout=60).stdout
            if len(t.strip()) > 500:
                return t[:CAP]
        except Exception:
            pass
    bins = [f for f in files if f.lower().endswith(('.bin', '.html'))]
    best = ""
    for b in sorted(bins, key=lambda p: -os.path.getsize(p))[:1]:
        try:
            best = strip_html(open(b, encoding="utf-8", errors="replace").read())
        except Exception:
            pass
    return best[:CAP]


def papers_with_content():
    pids = set()
    for f in ("newpapers_extracted.tsv", "supphtml_extracted.tsv", "docxocr_extracted.tsv"):
        p = ROOT / "pipeline_v2" / "deepmine" / f
        if p.exists():
            for r in csv.DictReader(p.open(encoding="utf-8"), delimiter="\t"):
                if r.get("paper_id"):
                    pids.add(r["paper_id"])
    return sorted(pids)


def load_state():
    return set(json.loads(STATE.read_text())) if STATE.exists() else set()


def extract(text):
    prompt = RULES + "\n\nPAPER TEXT:\n" + text
    try:
        r = subprocess.run(["claude", "-p", prompt, "--model", "sonnet", "--dangerously-skip-permissions"],
                           capture_output=True, text=True, timeout=180)
        return base.parse_arr(r.stdout)
    except Exception:
        return []


def process(pid):
    text = get_text(pid)
    if len(text) < 500:
        return []
    out = []
    for m in extract(text):
        if isinstance(m, dict) and (m.get("claim_text") or "").strip():
            out.append({"paper_id": pid, "claim_text": m.get("claim_text", ""),
                        "evidence_class": m.get("evidence_class", ""),
                        "direct_assay_types": m.get("direct_assay_types", ""),
                        "limitations": m.get("limitations", "")})
    return out


def append(rows):
    with _lock:
        new = not OUT.exists()
        with OUT.open("a", encoding="utf-8") as f:
            if new:
                f.write("\t".join(COLS) + "\n")
            for r in rows:
                f.write("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ") for c in COLS) + "\n")


def main():
    args = sys.argv[1:]
    items = papers_with_content()
    done = load_state()
    todo = [p for p in items if p not in done]
    if "--limit" in args:
        todo = todo[:int(args[args.index("--limit") + 1])]
    if "--list" in args:
        print(f"{len(items)} content papers | {len(done)} done | {len(todo)} todo")
        return
    print(f"mechanism extraction: todo={len(todo)}/{len(items)} | lanes={CONC}")

    def work(pid):
        try:
            rows = process(pid)
            append(rows)
            with _lock:
                d = load_state(); d.add(pid); STATE.write_text(json.dumps(sorted(d)))
            if rows:
                print(f"  ✓ {pid}: {len(rows)} claims")
        except Exception as ex:
            print(f"  ✗ {pid}: {ex}")

    with ThreadPoolExecutor(max_workers=CONC) as ex:
        list(ex.map(work, todo))
    print(f"done -> {OUT}")


if __name__ == "__main__":
    main()
