#!/usr/bin/env python3
"""Dual-model supplementary-table extractor (claude + codex) with cross-review confidence.

For each of the ~53 papers that have a non-empty extracted/supplementary_tables.json, this runs
BOTH CLIs on the same sheet and reconciles them:
  • claude -p (sonnet)  — fast first pass. Conservative: on header-less sheets it returns raw
    value strings and leaves endpoint/target blank rather than guessing.
  • codex exec (agentic) — deep resolver. It reads the source paper to recover headers, real
    sequences, endpoints, targets and units (verified accurate in spot-checks).
codex records are primary; a codex record is tagged confidence=high when claude's output
corroborates the same peptide+value, else codex_only. claude-only peptides codex missed are kept low.

Output: pipeline_v2/deepmine/supp_recovered.tsv
  columns: paper_id, sheet, peptide, sequence, endpoint, value, unit, target, confidence, models, note
State:  pipeline_v2/deepmine/supp_recovered_state.json  (done paper_ids — re-runs resume)

RUN IN CLOUD SHELL (not a 2-min-capped session — codex is ~4-5 min/paper):
  cd /home/cihebi/抗菌肽/数据集/batch/5-team
  python3 pipeline_v2/deepmine/extract_supp_dual.py            # all papers, resumable
  python3 pipeline_v2/deepmine/extract_supp_dual.py --list     # preview worklist (no CLI)
  python3 pipeline_v2/deepmine/extract_supp_dual.py --limit 3  # smoke test
  python3 pipeline_v2/deepmine/extract_supp_dual.py --models claude   # single-model (faster)

Auth: claude uses this machine's login; codex uses root creds via `sudo -n HOME=/root codex`.
"""
import json, os, re, sys, subprocess, tempfile, glob, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
OUT_TSV = ROOT / "pipeline_v2" / "deepmine" / "supp_recovered.tsv"
STATE = ROOT / "pipeline_v2" / "deepmine" / "supp_recovered_state.json"
COLS = ["paper_id", "sheet", "peptide", "sequence", "endpoint", "value", "unit", "target", "confidence", "models", "note"]
CLAUDE_TIMEOUT = int(os.environ.get("DEEPMINE_CLAUDE_TIMEOUT", "180"))
CODEX_TIMEOUT = int(os.environ.get("DEEPMINE_CODEX_TIMEOUT", "480"))
PAPER_CONC = int(os.environ.get("DEEPMINE_CONC", "3"))
MAX_ROWS = int(os.environ.get("DEEPMINE_MAX_ROWS", "400"))
_lock = threading.Lock()

PROMPT_HEAD = (
    "You are extracting antimicrobial-peptide EXPERIMENTAL activity/toxicity records from a supplementary "
    "spreadsheet. Return ONLY a JSON array (no prose). Each element keys: peptide, sequence, endpoint, value, "
    "unit, target, note.\nRules:\n"
    "- Extract ONLY measured experimental values (MIC, MBC, IC50, EC50, CC50, HC50, TI, hemolysis, etc.). One "
    "record per (peptide, endpoint, target) cell — do NOT merge multiple values into one string.\n"
    "- If the sheet lacks headers, resolve column meaning from the paper if you can; otherwise leave endpoint/"
    "target blank and put the raw value in value.\n"
    "- If the sheet is NOT experimental activity data (DNA primers, strain lists, computational prediction "
    "scores, instrument dumps), return exactly [].\n"
    "- Never invent values. Use \"\" for unknown fields.\n\n"
)


def worklist():
    items = []
    for p in sorted(glob.glob(str(ROOT / "paper_packets/*/extracted/supplementary_tables.json"))):
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except Exception:
            continue
        tabs = [t for t in (d.get("tables") or []) if (t.get("rows") or [])]
        if tabs:
            items.append((d.get("paper_id") or Path(p).parts[-3], p, tabs))
    return items


def sheet_prompt(pid, tab):
    rows = (tab.get("rows") or [])[:MAX_ROWS]
    body = "\n".join("\t".join(str(c) for c in r) for r in rows)
    return f"{PROMPT_HEAD}Paper: {pid}   Sheet: {tab.get('sheet_name') or 'sheet'}\nRows (tab-separated):\n{body[:8000]}"


def parse_arr(text):
    """Return the largest valid JSON array-of-objects in text (robust to surrounding log noise)."""
    if not text:
        return []
    best = []
    for mi in re.finditer(r"\[", text):
        i = mi.start()
        depth = 0
        for k in range(i, len(text)):
            ch = text[k]
            if ch == "[":
                depth += 1
            elif ch == "]":
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


def run_claude(prompt):
    try:
        r = subprocess.run(["claude", "-p", prompt, "--model", "sonnet", "--dangerously-skip-permissions"],
                           capture_output=True, text=True, timeout=CLAUDE_TIMEOUT)
        return parse_arr(r.stdout)
    except Exception:
        return []


def run_codex(prompt):
    # run from an empty temp dir so the agent doesn't scan the big repo; write final msg to -o file
    with tempfile.TemporaryDirectory() as td:
        outf = os.path.join(td, "final.txt")
        try:
            r = subprocess.run(
                ["sudo", "-n", "HOME=/root", "codex", "exec", "--skip-git-repo-check",
                 "--dangerously-bypass-approvals-and-sandbox", "-o", outf, prompt],
                capture_output=True, text=True, timeout=CODEX_TIMEOUT, cwd=td)
        except subprocess.TimeoutExpired as e:
            # codex sometimes finishes the answer but is killed during cleanup — salvage stdout
            return parse_arr((e.stdout or "") if isinstance(e.stdout, str) else "")
        except Exception:
            return []
        txt = ""
        if os.path.exists(outf):
            txt = Path(outf).read_text(encoding="utf-8", errors="replace")
        return parse_arr(txt) or parse_arr(r.stdout)


def _num(s):
    m = re.search(r"[-+]?\d*\.?\d+", str(s))
    return m.group(0) if m else ""


def reconcile(pid, sheet, claude_recs, codex_recs):
    # index claude values per peptide (its value may be a joined string of the row)
    cl = {}
    for r in claude_recs:
        pep = (r.get("peptide") or "").strip().lower()
        cl.setdefault(pep, "")
        cl[pep] += " " + str(r.get("value", ""))
    rows = []
    seen = set()
    for r in codex_recs:
        pep = (r.get("peptide") or "").strip()
        val = str(r.get("value", "")).strip()
        seen.add(pep.lower())
        corrob = _num(val) and _num(val) in (cl.get(pep.lower(), ""))
        rows.append({"paper_id": pid, "sheet": sheet, "peptide": pep,
                     "sequence": r.get("sequence", ""), "endpoint": r.get("endpoint", ""),
                     "value": val, "unit": r.get("unit", ""), "target": r.get("target", ""),
                     "confidence": "high" if corrob else "codex_only",
                     "models": "both" if corrob else "codex", "note": r.get("note", "")})
    # claude-only peptides codex missed
    for r in claude_recs:
        pep = (r.get("peptide") or "").strip()
        if pep.lower() and pep.lower() not in seen:
            rows.append({"paper_id": pid, "sheet": sheet, "peptide": pep, "sequence": r.get("sequence", ""),
                         "endpoint": r.get("endpoint", ""), "value": str(r.get("value", "")), "unit": r.get("unit", ""),
                         "target": r.get("target", ""), "confidence": "claude_only", "models": "claude",
                         "note": r.get("note", "")})
    return rows


def process_paper(pid, tabs, models):
    out = []
    for tab in tabs:
        prompt = sheet_prompt(pid, tab)
        sheet = tab.get("sheet_name") or "sheet"
        with ThreadPoolExecutor(max_workers=2) as ex:
            fc = ex.submit(run_claude, prompt) if models in ("both", "claude") else None
            fx = ex.submit(run_codex, prompt) if models in ("both", "codex") else None
            claude_recs = fc.result() if fc else []
            codex_recs = fx.result() if fx else []
        if models == "claude":
            out += [{"paper_id": pid, "sheet": sheet, "peptide": r.get("peptide", ""), "sequence": r.get("sequence", ""),
                     "endpoint": r.get("endpoint", ""), "value": str(r.get("value", "")), "unit": r.get("unit", ""),
                     "target": r.get("target", ""), "confidence": "claude_only", "models": "claude",
                     "note": r.get("note", "")} for r in claude_recs]
        elif models == "codex":
            out += [{"paper_id": pid, "sheet": sheet, "peptide": r.get("peptide", ""), "sequence": r.get("sequence", ""),
                     "endpoint": r.get("endpoint", ""), "value": str(r.get("value", "")), "unit": r.get("unit", ""),
                     "target": r.get("target", ""), "confidence": "codex_only", "models": "codex",
                     "note": r.get("note", "")} for r in codex_recs]
        else:
            out += reconcile(pid, sheet, claude_recs, codex_recs)
    return out


def load_state():
    return set(json.loads(STATE.read_text())) if STATE.exists() else set()


def save_row_batch(rows):
    with _lock:
        new = not OUT_TSV.exists()
        with OUT_TSV.open("a", encoding="utf-8") as f:
            if new:
                f.write("\t".join(COLS) + "\n")
            for r in rows:
                f.write("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ") for c in COLS) + "\n")


def mark_done(pid):
    with _lock:
        done = load_state()
        done.add(pid)
        STATE.write_text(json.dumps(sorted(done)))


def main():
    args = sys.argv[1:]
    models = "both"
    if "--models" in args:
        models = args[args.index("--models") + 1]
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    items = worklist()
    done = load_state()
    todo = [it for it in items if it[0] not in done]
    if limit:
        todo = todo[:limit]
    total_rows = sum(len(t.get("rows") or []) for _, _, tabs in items for t in tabs)
    if "--list" in args:
        print(f"{len(items)} papers | {sum(len(tabs) for _,_,tabs in items)} sheets | {total_rows} rows | {len(done)} done")
        for pid, _, tabs in items[:60]:
            print(f"  {'DONE' if pid in done else '-   '} rows={sum(len(t.get('rows') or []) for t in tabs):6d}  {pid}")
        return
    print(f"models={models}  todo={len(todo)}/{len(items)} papers (done={len(done)})  paper_conc={PAPER_CONC}")

    def work(it):
        pid, _, tabs = it
        try:
            rows = process_paper(pid, tabs, models)
            save_row_batch(rows)
            mark_done(pid)
            print(f"  ✓ {pid}: {len(rows)} rows "
                  f"({sum(1 for r in rows if r['confidence']=='high')} high-conf)")
        except Exception as ex:
            print(f"  ✗ {pid}: {ex}")

    with ThreadPoolExecutor(max_workers=PAPER_CONC) as ex:
        list(ex.map(work, todo))
    print(f"done. output → {OUT_TSV}")


if __name__ == "__main__":
    main()
