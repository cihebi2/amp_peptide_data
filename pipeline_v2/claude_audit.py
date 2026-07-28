#!/usr/bin/env python3
"""Independent claude-CLI audit lane (claude has more quota than codex). Runs claude -p over the SAME
genuine v2 prompts as a SECOND independent auditor, applies the same 5 deterministic guards, and writes
claude_audit_errors.tsv. Cross-compare with the codex confirmed set -> dual-model-confirmed errors.

High concurrency (claude quota is ample). Reuses existing v2_prompt(.md / _c*.md) files read-only.
"""
import json, subprocess, sys, re, os, csv
from pathlib import Path
import importlib.util
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
SCR = Path("/tmp/claude-1001/-home-cihebi---------batch-5-team/116a3aaf-1ac6-4814-8939-d02f5b1b2511/scratchpad")
CONC = int(os.environ.get("CLAUDE_CONC", "16"))
CHUNK = 20
spec = importlib.util.spec_from_file_location("adj", str(ROOT / "pipeline_v2/adjudicate_v2.py"))
adj = importlib.util.module_from_spec(spec); spec.loader.exec_module(adj)
POS = {"value_mismatch", "endpoint_mismatch", "variant_misattribution"}


def arr(t):
    s = t.find("["); e = t.rfind("]"); return json.loads(t[s:e + 1]) if s >= 0 else []


CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "sonnet")  # Sonnet for high-concurrency claude audit, not Opus
ENGINE = os.environ.get("ENGINE", "claude")             # claude | codex

def run_claude(prompt_text):
    if ENGINE == "codex":
        import shlex, tempfile
        # codex needs -o inside workspace; use a temp file under pipeline_v2/work
        of = ROOT / f"pipeline_v2/work/.codex_audit_{abs(hash(prompt_text)) % 10**8}.md"
        cmd = (f'sudo HOME=/root codex exec -C {shlex.quote(str(ROOT))} --skip-git-repo-check '
               f'-m gpt-5.5 -c \'approval_policy="never"\' -c \'model_reasoning_effort="xhigh"\' '
               f'-o {shlex.quote(str(of))} -')
        subprocess.run(cmd, input=prompt_text, capture_output=True, text=True, timeout=750, shell=True, executable="/bin/bash")
        try:
            out = of.read_text(encoding="utf-8", errors="replace")
        finally:
            try: of.unlink()
            except OSError: pass
        return arr(out)
    r = subprocess.run(["claude", "-p", "--model", CLAUDE_MODEL, prompt_text], capture_output=True, text=True, timeout=600)
    return arr(r.stdout)


def audit_paper(paper):
    wd = ROOT / f"pipeline_v2/work/{paper}"
    # build-if-missing (expansion mode: base pack + all_conflict prompt, chunked)
    force_build = os.environ.get("FORCE_BUILD") == "1"
    need_build = os.environ.get("BUILD_IF_MISSING") == "1" and (force_build or (not (wd / "v2_prompt.md").exists() and not list(wd.glob("v2_prompt_c*.md"))))
    if need_build:
        if force_build:
            for old in wd.glob("v2_prompt*.md"): old.unlink()
        if not (wd / "evidence_pack.json").exists():
            subprocess.run(["python3", str(ROOT / "pipeline_v2/extract_evidence_pack.py"), paper], capture_output=True, timeout=180)
        env = {**os.environ, "V2_SELECT": "all_conflict", "V2_MAX_ASSERTIONS": os.environ.get("EXP_MAX", "20"),
               "V2_CHUNK_SIZE": "20", "V2_OFFSET": os.environ.get("V2_OFFSET", "0")}
        subprocess.run(["python3", str(ROOT / "pipeline_v2/build_v2_task.py"), paper], capture_output=True, timeout=180, env=env)
    chunks = sorted(wd.glob("v2_prompt_c*.md"), key=lambda x: int(x.stem.split("_c")[1].split(".")[0]))
    verd = []
    try:
        if chunks:
            for cf in chunks:
                n = int(cf.stem.split("_c")[1].split(".")[0])
                try:
                    vs = run_claude(cf.read_text(encoding="utf-8"))
                except Exception:
                    vs = []
                for i, v in enumerate(vs):
                    v["assertion_index"] = n * CHUNK + i
                    verd.append(v)
        else:
            pf = wd / "v2_prompt.md"
            if not pf.exists():
                return paper, [], "no_prompt"
            verd = run_claude(pf.read_text(encoding="utf-8"))
        (wd / "v2_claude.md").write_text(json.dumps(verd, ensure_ascii=False), encoding="utf-8")
        pack = json.loads((wd / "evidence_pack.json").read_text())
        chosen = json.loads((wd / "chosen_assertions.json").read_text())
    except Exception as ex:
        return paper, [], f"exc:{ex}"
    idx = adj.cell_index(pack); byi = {v.get("assertion_index", n): v for n, v in enumerate(verd)}
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
        errs.append({"paper_id": paper, "database": a["database"], "error_type": outc,
                     "db_peptide": dc.get("peptide", "") or adj.peptide_identity(a), "db_organism": dc.get("organism", ""),
                     "db_endpoint": dc.get("endpoint", ""), "db_value": dc.get("value", ""),
                     "source_table": ev.get("table_index", ""), "source_row": ev.get("row_label", ""),
                     "source_col": ev.get("col_header", ""), "source_value": ev.get("source_value", ""),
                     "reason": (v.get("short_reason", "") or "")[:160]})
    return paper, errs, "ok"


def main():
    papers = json.loads((SCR / os.environ.get("CLAUDE_WORKLIST", "genuine_papers.json")).read_text())
    state_f = ROOT / os.environ.get("CLAUDE_STATE", "pipeline_v2/claude_audit_state.json")
    done = set(json.loads(state_f.read_text())["processed"]) if state_f.exists() else set()
    todo = [p for p in papers if p not in done]
    if not todo:
        print("CLAUDE_AUDIT_COMPLETE"); return
    out = ROOT / os.environ.get("CLAUDE_OUT", "pipeline_v2/claude_audit_errors.tsv")
    cols = ["paper_id", "database", "error_type", "db_peptide", "db_organism", "db_endpoint", "db_value",
            "source_table", "source_row", "source_col", "source_value", "reason"]
    allnew = []
    with ThreadPoolExecutor(max_workers=CONC) as ex:
        for fut in as_completed([ex.submit(audit_paper, p) for p in todo]):
            paper, errs, status = fut.result()
            allnew.extend(errs); done.add(paper)
            state_f.write_text(json.dumps({"processed": sorted(done)}))
            print(f"{paper.split('__')[-1]}: status={status} claude_errors={len(errs)}")
    write_header = not out.exists()
    with out.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        if write_header: w.writeheader()
        for e in allnew: w.writerow(e)
    print(f"CLAUDE_BATCH_DONE new={len(allnew)} processed={len(done)}/{len(papers)}")


if __name__ == "__main__":
    main()
