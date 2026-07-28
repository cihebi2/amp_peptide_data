#!/usr/bin/env python3
"""pipeline_v2 /loop worker: recover figure-bound values with codex VISION, re-audit, then
cross-check each confirmed error with claude CLI (independent proofreader). Append agreed errors.

codex = primary (vision extract + audit); claude = final proofreader. Both read images.
Processes the next BATCH papers from the worklist that are not yet in the state file.
"""
import json, subprocess, sys, shlex, re
from pathlib import Path
import importlib.util

import os
ROOT = Path(__file__).resolve().parents[1]
SCR = Path("/tmp/claude-1001/-home-cihebi---------batch-5-team/116a3aaf-1ac6-4814-8939-d02f5b1b2511/scratchpad")
STATE = ROOT / os.environ.get("VISION_STATE", "pipeline_v2/vision_loop_state.json")
WORKLIST = SCR / os.environ.get("VISION_WORKLIST", "vision_worklist.json")
OUT = ROOT / "pipeline_v2/vision_recovered_errors.tsv"
BATCH = int(sys.argv[1]) if len(sys.argv) > 1 else 2
MAX_FIGS = 6
FIG_OFFSET = int(os.environ.get("FIG_OFFSET", "0"))      # phase-2: sample figures [OFFSET:OFFSET+MAX]
FORCE_VISION = os.environ.get("FORCE_VISION", "") == "1"  # phase-2: re-run vision even if pack has cells

spec = importlib.util.spec_from_file_location("adj", str(ROOT / "pipeline_v2/adjudicate_v2.py"))
adj = importlib.util.module_from_spec(spec); spec.loader.exec_module(adj)
POS = {"value_mismatch", "endpoint_mismatch", "variant_misattribution"}
UND = {"cannot_determine", "not_in_provided_tables", "organism_absent", "MISSING"}


def sh(cmd, inp=None, timeout=700):
    return subprocess.run(cmd, input=inp, capture_output=True, text=True, timeout=timeout, shell=True, executable="/bin/bash")


def arr(t):
    s = t.find("["); e = t.rfind("]"); return json.loads(t[s:e + 1]) if s >= 0 else []


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {"processed": []}


CHUNK = 20

def _run_codex(prompt_path, out_path):
    cmd = (f'sudo HOME=/root codex exec -C {shlex.quote(str(ROOT))} --skip-git-repo-check --add-dir {shlex.quote(str(ROOT))} '
           f'-m gpt-5.5 -c \'approval_policy="never"\' -c \'model_reasoning_effort="xhigh"\' '
           f'-o {shlex.quote(str(out_path))} -')
    sh(cmd, inp=Path(prompt_path).read_text(), timeout=750)


def codex_audit_chunked(wd):
    """Always chunk (V2_CHUNK_SIZE) so codex fully enumerates; merge positionally into v2_vis.md."""
    chunks = sorted(wd.glob("v2_prompt_c*.md"), key=lambda x: int(x.stem.split("_c")[1].split(".")[0]))
    if chunks:
        merged = []
        for cf in chunks:
            n = int(cf.stem.split("_c")[1].split(".")[0])
            of = wd / f"v2_vis_c{n}.md"
            try:
                _run_codex(cf, of)
            except Exception:
                pass  # per-chunk timeout/error must not lose the whole paper; just skip this chunk
            sh(f"sudo chown {shlex.quote(str(of))}", timeout=30)
            try:
                vs = arr(Path(of).read_text())
            except Exception:
                vs = []
            for i, v in enumerate(vs):
                v["assertion_index"] = n * CHUNK + i   # positional global index
                merged.append(v)
        (wd / "v2_vis.md").write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
    else:
        _run_codex(wd / "v2_prompt.md", wd / "v2_vis.md")


def claude_proofread(e):
    q = (f"Independent proofread of a claimed antimicrobial-peptide DATABASE error.\n"
         f"Database={e['database']} peptide={e['db_peptide']!r} organism={e['db_organism']!r} "
         f"db_endpoint={e['db_endpoint']!r} db_value={e['db_value']!r}.\n"
         f"Primary-source evidence extracted from a FIGURE in paper {e['paper_id']}: "
         f"row={e['source_row']!r} col={e['source_col']!r} value={e['source_value']!r}. error_type={e['error_type']}.\n"
         f"Given ONLY this, is the database annotation genuinely WRONG vs the source figure value? "
         f"Answer one word REAL / NOTREAL / UNSURE then a 12-word reason.")
    r = sh(f"claude -p --model sonnet {shlex.quote(q)}", timeout=180)
    out = (r.stdout or "").strip()
    verdict = "UNSURE"
    for k in ("NOTREAL", "REAL", "UNSURE"):
        if re.search(rf"\b{k}\b", out.upper()):
            verdict = k; break
    return verdict, out[:160].replace("\t", " ").replace("\n", " ")


def process(paper):
    wd = ROOT / f"pipeline_v2/work/{paper}"
    # skip re-extraction/vision if this pack already carries codex-vision cells (avoid paying vision cost twice)
    pack_path = wd / "evidence_pack.json"
    has_vision = False
    if pack_path.exists():
        try:
            has_vision = any(t.get("source") == "codex_vision" for t in json.loads(pack_path.read_text())["tables"])
        except Exception:
            has_vision = False
    if not has_vision or FORCE_VISION:
        if not has_vision:
            sh(f"python3 {shlex.quote(str(ROOT/'pipeline_v2/extract_evidence_pack.py'))} {shlex.quote(paper)}", timeout=120)
        allf = [f for f in sorted((ROOT / f"paper_packets/{paper}/extracted").rglob("*.jpg"))
                if "thumb" not in f.name.lower()]
        figs = allf[FIG_OFFSET:FIG_OFFSET + MAX_FIGS]   # phase-2 reads the next window of figures
        if figs:
            sh(f"python3 {shlex.quote(str(ROOT/'pipeline_v2/vision_recover.py'))} {shlex.quote(paper)} "
               + " ".join(shlex.quote(str(f)) for f in figs), timeout=700 * len(figs))
    for old in wd.glob("v2_prompt_c*.md"): old.unlink()
    for old in wd.glob("v2_vis_c*.md"): old.unlink()
    sh(f"V2_SELECT=genuine V2_MAX_ASSERTIONS=400 V2_CHUNK_SIZE={CHUNK} python3 {shlex.quote(str(ROOT/'pipeline_v2/build_v2_task.py'))} {shlex.quote(paper)}", timeout=120)
    codex_audit_chunked(wd)
    sh(f"sudo chown -R cihebi:cihebi {shlex.quote(str(wd))}", timeout=60)
    try:
        pack = json.loads((wd / "evidence_pack.json").read_text())
        chosen = json.loads((wd / "chosen_assertions.json").read_text())
        verd = arr((wd / "v2_vis.md").read_text())
    except Exception as ex:
        return [], f"parse_fail:{ex}"
    idx = adj.cell_index(pack); byi = {v.get("assertion_index", n): v for n, v in enumerate(verd)}
    vis_tables = {t["table_index"] for t in pack["tables"] if t.get("source") == "codex_vision"}
    errs = []
    for a in chosen:
        v = byi.get(a["assertion_index"], {}); outc = v.get("verification_outcome"); err = bool(v.get("is_database_error"))
        ok = err and outc in POS and adj.roundtrip(v.get("evidence"), idx) == "ok"
        if ok and outc == "variant_misattribution" and not adj.peptide_identity(a).strip(): ok = False
        if ok and outc == "value_mismatch" and adj.value_consistent((v.get("db_claimed") or {}).get("value"), (v.get("evidence") or {}).get("source_value")): ok = False
        if ok and outc == "endpoint_mismatch" and not adj.endpoint_mismatch_reliable((v.get("db_claimed") or {}).get("endpoint"), (v.get("evidence") or {}).get("col_header")): ok = False
        if not ok:
            continue
        ev = v.get("evidence") or {}; dc = v.get("db_claimed") or {}
        from_fig = ev.get("table_index") in vis_tables
        # figure-read values carry chart-estimate imprecision: a value_mismatch within 15% off a figure
        # cell is not a trustworthy error (likely read tolerance), drop it
        if from_fig and outc == "value_mismatch":
            import re as _re
            dn = _re.findall(r"\d+\.?\d*", str(dc.get("value", "")))
            sn = _re.findall(r"\d+\.?\d*", str(ev.get("source_value", "")))
            if dn and sn:
                d0, s0 = float(dn[0]), float(sn[0])
                if max(d0, s0) > 0 and abs(d0 - s0) / max(d0, s0) <= 0.15:
                    continue
        errs.append({"paper_id": paper, "database": a["database"], "source_id": a.get("source_id", ""),
                     "error_type": outc, "db_peptide": dc.get("peptide", "") or adj.peptide_identity(a),
                     "db_organism": dc.get("organism", ""), "db_endpoint": dc.get("endpoint", ""),
                     "db_value": dc.get("value", ""), "source_table": ev.get("table_index", ""),
                     "source_row": ev.get("row_label", ""), "source_col": ev.get("col_header", ""),
                     "source_value": ev.get("source_value", ""), "from_figure": from_fig,
                     "reason": (v.get("short_reason", "") or "")[:160]})
    return errs, "ok"


def _safe_process(paper):
    try:
        return paper, process(paper)
    except Exception as ex:
        return paper, ([], f"exc:{ex}")


def main():
    from concurrent.futures import ThreadPoolExecutor, as_completed
    CONC = int(os.environ.get("CONCURRENCY", "10"))
    work = json.loads(WORKLIST.read_text())
    st = load_state(); done = set(st["processed"])
    todo = [p for p in work if p not in done][:BATCH]
    if not todo:
        print("VISION_LOOP_COMPLETE all done"); return
    all_new = []
    # 1) process papers concurrently (each paper thread = sequential subprocess chain -> ~CONC concurrent CLIs)
    results = {}
    with ThreadPoolExecutor(max_workers=CONC) as ex:
        for fut in as_completed([ex.submit(_safe_process, p) for p in todo]):
            paper, (errs, status) = fut.result()
            results[paper] = errs
            st["processed"].append(paper); STATE.write_text(json.dumps(st))
            print(f"{paper.split('__')[-1]}: status={status} codex_errors={len(errs)} from_figure={sum(1 for e in errs if e['from_figure'])}")
    flat = [e for errs in results.values() for e in errs]
    # 2) claude proofread ALL candidate errors in parallel
    with ThreadPoolExecutor(max_workers=CONC) as ex:
        futs = {ex.submit(claude_proofread, e): e for e in flat}
        for fut in as_completed(futs):
            e = futs[fut]
            try:
                v, txt = fut.result()
            except Exception:
                v, txt = "UNSURE", "proofread_error"
            e["claude_verdict"] = v; e["claude_note"] = txt
    all_new = flat
    # append
    cols = ["paper_id", "database", "source_id", "error_type", "db_peptide", "db_organism", "db_endpoint",
            "db_value", "source_table", "source_row", "source_col", "source_value", "from_figure",
            "claude_verdict", "claude_note", "reason"]
    new = not OUT.exists()
    import csv
    with OUT.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t")
        if new: w.writeheader()
        for e in all_new: w.writerow({k: e.get(k, "") for k in cols})
    print(f"BATCH_DONE processed={len(todo)} new_errors={len(all_new)} agreed={sum(1 for e in all_new if e.get('claude_verdict')=='REAL')} total_processed={len(st['processed'])}/{len(work)}")


if __name__ == "__main__":
    main()
