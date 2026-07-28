#!/usr/bin/env python3
"""Stage 3 of "process ALL documents": docx-supplementary papers + scanned (image-only) PDFs.

  • docx: unzip word/document.xml → strip tags → text.
  • scanned PDF (pdftotext yields ~nothing): pdftoppm → PNG pages → tesseract OCR → text.
Then the same validated claude extraction. Recovers the last content-bearing papers that the
PDF/XML and HTML stages could not read.

Outputs: docxocr_extracted.tsv, docxocr_state.json
  python3 pipeline_v2/deepmine/extract_docx_ocr_dual.py --list
  python3 pipeline_v2/deepmine/extract_docx_ocr_dual.py --limit 3
  python3 pipeline_v2/deepmine/extract_docx_ocr_dual.py           # full, DEEPMINE_CONC lanes
"""
import os, sys, re, json, glob, zipfile, tempfile, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import extract_newpapers_dual as base

ROOT = base.ROOT
POOL = base.POOL
OUT = ROOT / "pipeline_v2" / "deepmine" / "docxocr_extracted.tsv"
STATE = ROOT / "pipeline_v2" / "deepmine" / "docxocr_state.json"
CONC = int(os.environ.get("DEEPMINE_CONC", "6"))
OCR_PAGES = int(os.environ.get("DEEPMINE_OCR_PAGES", "10"))
CAP = 42000


def docx_text(f):
    try:
        xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8', errors='replace')
        xml = re.sub(r'</w:p>', '\n', xml)
        return re.sub(r'\s+\n', '\n', re.sub(r'<[^>]+>', '', xml)).strip()[:CAP]
    except Exception:
        return ""


def ocr_pdf(pdf):
    with tempfile.TemporaryDirectory() as td:
        pref = os.path.join(td, "pg")
        try:
            subprocess.run(["pdftoppm", "-png", "-r", "180", "-l", str(OCR_PAGES), pdf, pref],
                           capture_output=True, timeout=300)
        except Exception:
            return ""
        out = []
        for png in sorted(glob.glob(pref + "*.png")):
            try:
                r = subprocess.run(["tesseract", png, "-", "--psm", "6"], capture_output=True, text=True, timeout=120)
                out.append(r.stdout)
            except Exception:
                pass
        return "\n".join(out)[:CAP]


def source_text(pid):
    files = glob.glob(f"{POOL}/{pid}/**/*", recursive=True)
    dx = [f for f in files if f.lower().endswith('.docx') and os.path.getsize(f) > 10000]
    if dx:
        t = docx_text(max(dx, key=lambda p: os.path.getsize(p)))
        if len(t) > 800:
            return t, "docx"
    pdfs = [f for f in files if f.lower().endswith('.pdf')]
    if pdfs:
        try:
            plain = subprocess.run(["pdftotext", "-q", pdfs[0], "-"], capture_output=True, text=True, timeout=30).stdout
        except Exception:
            plain = ""
        if len(plain.strip()) < 500:   # scanned → OCR
            return ocr_pdf(pdfs[0]), "ocr"
    return "", ""


def worklist():
    done = set(os.listdir(ROOT / "papers"))
    attempted = set()
    for s in ("newpapers_state.json", "supphtml_state.json"):
        p = ROOT / "pipeline_v2" / "deepmine" / s
        if p.exists():
            attempted |= set(json.loads(p.read_text()))
    items = []
    for d in sorted(os.listdir(POOL)):
        if not d.startswith("doi__") or d in done:
            continue
        files = glob.glob(f"{POOL}/{d}/**/*", recursive=True)
        has_docx = any(f.lower().endswith('.docx') and os.path.getsize(f) > 10000 for f in files)
        pdfs = [f for f in files if f.lower().endswith('.pdf')]
        is_scanned = False
        if pdfs:   # scanned PDFs need OCR even if stage-1 already "attempted" them (its pdftotext read was empty)
            try:
                is_scanned = len(subprocess.run(["pdftotext", "-q", pdfs[0], "-"], capture_output=True, text=True, timeout=30).stdout.strip()) < 500
            except Exception:
                is_scanned = False
        if has_docx or is_scanned:
            items.append(d)
    return items


def load_state():
    return set(json.loads(STATE.read_text())) if STATE.exists() else set()


def process(pid):
    text, kind = source_text(pid)
    if len(text) < 800:
        return []
    recs = base._clean(base.run_claude_extract(text))
    out, seen = [], set()
    for r in recs:
        k = base._key(r)
        if k in seen:
            continue
        seen.add(k); out.append(base._row(pid, r, f"claude_{kind}"))
    return out


def main():
    args = sys.argv[1:]
    items = worklist()
    done = load_state()
    todo = [p for p in items if p not in done]
    if "--limit" in args:
        todo = todo[:int(args[args.index("--limit") + 1])]
    if "--list" in args:
        print(f"{len(items)} docx/scanned papers | {len(done)} done | {len(todo)} todo")
        return
    print(f"docx+OCR extraction: todo={len(todo)}/{len(items)} | lanes={CONC}")

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
