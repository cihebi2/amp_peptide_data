#!/usr/bin/env python3
"""Deep-mine driver: recover UNSURFACED AMP data from already-acquired supplementary spreadsheets.

~53 papers carry parsed supplementary sheets in
    paper_packets/<paper_id>/extracted/supplementary_tables.json
(≈675 sheets / ≈431k rows total). These rows never made it into the curated corpus. This driver
walks every sheet, chunks the rows, and asks the claude CLI (Sonnet — high concurrency, cheap;
NOT Opus, per project norm) to convert the raw cells into structured AMP activity/property records
(peptide, sequence, endpoint, value, unit, target, source sheet/row). Recovered rows are appended
to supp_recovered.tsv; processed paper_ids are checkpointed in supp_recovered_state.json so a
re-run resumes exactly where it stopped.

Design mirrors pipeline_v2/claude_audit.py + residual_driver.py:
  * ThreadPoolExecutor over papers (per-paper is the unit of parallelism + resumability)
  * `arr()` = tolerant JSON-array extraction from CLI stdout
  * Sonnet model, subprocess with hard timeout, try/except per paper AND per chunk so one bad
    sheet never crashes the batch
  * rows for a paper are buffered and appended only after the WHOLE paper finishes, then the paper
    is marked done — so an interrupted paper leaves no half-written TSV rows and is simply retried.

Dependency-free (stdlib only). WRITES nothing until claude returns; this script never runs anything
other than the `claude` CLI.

Usage (see deepmine/README.md for the full cloud-shell recipe):
    python3 pipeline_v2/deepmine/extract_supp_tables.py --list
    python3 pipeline_v2/deepmine/extract_supp_tables.py --limit 3      # smoke test
    python3 pipeline_v2/deepmine/extract_supp_tables.py                # full run (resumable)
"""
import argparse
import csv
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]                 # .../5-team
PACKETS = ROOT / "paper_packets"
OUT_TSV = ROOT / "pipeline_v2/deepmine/supp_recovered.tsv"
STATE = ROOT / "pipeline_v2/deepmine/supp_recovered_state.json"

# ---- tunables (env-overridable, same convention as claude_audit.py) ----
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "sonnet")     # Sonnet for concurrency, never Opus
CONC = int(os.environ.get("DEEPMINE_CONC", "6"))           # papers processed in parallel
ROWS_PER_CALL = int(os.environ.get("DEEPMINE_ROWS", "120"))  # rows per claude call
MAX_ROWS_PER_SHEET = int(os.environ.get("DEEPMINE_MAX_ROWS", "3000"))  # cost cap per sheet
MAX_CELL = int(os.environ.get("DEEPMINE_MAX_CELL", "200"))  # truncate long cell text
CLI_TIMEOUT = int(os.environ.get("DEEPMINE_TIMEOUT", "420"))  # seconds per claude call

COLS = ["paper_id", "peptide", "sequence", "endpoint", "value", "unit",
        "target", "source_sheet", "source_row", "notes"]

PROMPT_HEADER = """You are extracting antimicrobial-peptide (AMP) data from a raw supplementary
spreadsheet sheet that was parsed straight from an author's Excel/CSV file. The rows below are
literal cell lists (each row = a list of cell values, in column order). They may contain instrument
dumps, headers, footnotes, or genuine data.

Extract ONLY genuine AMP activity or physicochemical property records. For each real record emit one
JSON object with these keys (use "" for anything not present in the row — never invent values):
  peptide   : peptide / compound name or identifier as written
  sequence  : amino-acid sequence if present (else "")
  endpoint  : measured quantity, e.g. MIC, MBC, IC50, EC50, hemolysis, net charge, MW, HC50, GRAVY
  value     : the numeric or textual result (keep ranges like "4-8" verbatim)
  unit      : unit of the value, e.g. ug/mL, uM, mm, %, Da (else "")
  target    : organism / strain / cell line / assay context the value refers to (else "")
  source_row: the 0-based index of the source row within THIS chunk (see [row N] prefixes)
  notes     : brief clarification if the mapping is non-obvious (else "")

Rules:
- Skip instrument metadata (User:, Path:, Test ID:, Date:, plate maps, raw OD/absorbance grids),
  section titles, and pure header rows — emit nothing for them.
- One object per (peptide, endpoint, target, value). Split multi-value rows into multiple objects.
- If the sheet has NO extractable AMP records, return exactly [].
Output ONLY a JSON array (starting with [ and ending with ]). No prose, no markdown fences.

paper_id: {paper_id}
sheet_name: {sheet_name}
--- rows (chunk offset {offset}) ---
{rows}
"""


def arr(text):
    """Tolerantly pull the first JSON array out of CLI stdout (same helper style as claude_audit)."""
    if not text:
        return []
    s = text.find("[")
    e = text.rfind("]")
    if s < 0 or e <= s:
        return []
    try:
        v = json.loads(text[s:e + 1])
        return v if isinstance(v, list) else []
    except Exception:
        return []


def run_claude(prompt_text):
    """Call the claude CLI (Sonnet) with the prompt on stdin; return parsed JSON array."""
    r = subprocess.run(
        ["claude", "-p", "--dangerously-skip-permissions", "--model", CLAUDE_MODEL],
        input=prompt_text, capture_output=True, text=True, timeout=CLI_TIMEOUT,
    )
    return arr(r.stdout)


def fmt_rows(rows, offset):
    """Serialize a chunk of raw cell-list rows into a compact, index-labelled block."""
    lines = []
    for i, row in enumerate(rows):
        if isinstance(row, (list, tuple)):
            cells = [str(c)[:MAX_CELL] for c in row]
        else:
            cells = [str(row)[:MAX_CELL]]
        lines.append(f"[row {offset + i}] " + " | ".join(cells))
    return "\n".join(lines)


def load_worklist():
    """Return [(paper_id, supp_json_path, n_sheets, n_rows), ...] for papers with real tables."""
    work = []
    for pkt in sorted(PACKETS.glob("*/extracted/supplementary_tables.json")):
        try:
            d = json.loads(pkt.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        tables = d.get("tables") or []
        if not tables:
            continue
        nrows = sum(len(t.get("rows") or []) for t in tables)
        pid = d.get("paper_id") or pkt.parents[1].name
        work.append((pid, pkt, len(tables), nrows))
    return work


def process_paper(pid, pkt):
    """Extract all sheets of one paper. Returns (pid, rows[list of dict], status)."""
    try:
        d = json.loads(pkt.read_text(encoding="utf-8", errors="replace"))
    except Exception as ex:
        return pid, [], f"read_error:{ex}"
    out = []
    n_sheets = 0
    for t in (d.get("tables") or []):
        sheet = t.get("sheet_name", "")
        rows = t.get("rows") or []
        if not rows:
            continue
        if len(rows) > MAX_ROWS_PER_SHEET:
            rows = rows[:MAX_ROWS_PER_SHEET]  # cost cap; raise DEEPMINE_MAX_ROWS to go deeper
        n_sheets += 1
        for off in range(0, len(rows), ROWS_PER_CALL):
            chunk = rows[off:off + ROWS_PER_CALL]
            prompt = PROMPT_HEADER.format(
                paper_id=pid, sheet_name=sheet, offset=off, rows=fmt_rows(chunk, off))
            try:
                recs = run_claude(prompt)
            except subprocess.TimeoutExpired:
                continue                      # skip this chunk, keep the paper alive
            except Exception:
                continue
            for r in recs:
                if not isinstance(r, dict):
                    continue
                out.append({
                    "paper_id": pid,
                    "peptide": str(r.get("peptide", ""))[:300],
                    "sequence": str(r.get("sequence", ""))[:600],
                    "endpoint": str(r.get("endpoint", ""))[:120],
                    "value": str(r.get("value", ""))[:120],
                    "unit": str(r.get("unit", ""))[:60],
                    "target": str(r.get("target", ""))[:300],
                    "source_sheet": sheet[:200],
                    "source_row": r.get("source_row", ""),
                    "notes": str(r.get("notes", ""))[:300],
                })
    return pid, out, f"ok sheets={n_sheets}"


def append_rows(rows):
    write_header = not OUT_TSV.exists()
    with OUT_TSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, delimiter="\t", extrasaction="ignore")
        if write_header:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def load_done():
    if STATE.exists():
        try:
            return set(json.loads(STATE.read_text()).get("processed", []))
        except Exception:
            return set()
    return set()


def save_done(done):
    STATE.write_text(json.dumps({"processed": sorted(done)}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="Deep-mine supplementary tables into AMP records.")
    ap.add_argument("--limit", type=int, default=0,
                    help="process at most N not-yet-done papers this run (0 = all)")
    ap.add_argument("--list", action="store_true",
                    help="list the worklist (paper_id, sheets, rows, done?) and exit")
    args = ap.parse_args()

    work = load_worklist()
    done = load_done()

    if args.list:
        tot_s = sum(w[2] for w in work)
        tot_r = sum(w[3] for w in work)
        print(f"{'DONE':<5} {'SHEETS':>7} {'ROWS':>9}  PAPER_ID")
        for pid, _pkt, ns, nr in sorted(work, key=lambda x: -x[3]):
            print(f"{'yes' if pid in done else '-':<5} {ns:>7} {nr:>9}  {pid}")
        print(f"\n{len(work)} papers  |  {tot_s} sheets  |  {tot_r} rows  |  "
              f"{len(done & {w[0] for w in work})} done")
        return

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    todo = [(pid, pkt) for pid, pkt, _ns, _nr in work if pid not in done]
    if args.limit:
        todo = todo[:args.limit]
    if not todo:
        print("DEEPMINE_SUPP_COMPLETE (nothing to do)")
        return

    print(f"deep-mining {len(todo)} papers  model={CLAUDE_MODEL} conc={CONC} "
          f"rows/call={ROWS_PER_CALL} cap/sheet={MAX_ROWS_PER_SHEET}", flush=True)
    total_new = 0
    with ThreadPoolExecutor(max_workers=CONC) as ex:
        futs = {ex.submit(process_paper, pid, pkt): pid for pid, pkt in todo}
        for fut in as_completed(futs):
            pid = futs[fut]
            try:
                pid, rows, status = fut.result()
            except Exception as ex2:
                print(f"{pid}: FAILED {ex2}", flush=True)
                continue
            if rows:
                append_rows(rows)             # append BEFORE marking done (crash-safe ordering)
            done.add(pid)
            save_done(done)
            total_new += len(rows)
            print(f"{pid}: {status} recovered={len(rows)}", flush=True)

    print(f"DEEPMINE_BATCH_DONE new_rows={total_new} processed={len(done)}/{len(work)} "
          f"-> {OUT_TSV}", flush=True)


if __name__ == "__main__":
    main()
