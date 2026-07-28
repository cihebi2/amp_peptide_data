#!/usr/bin/env python3
"""Exhaust the residual conflicts (>20/paper) by sliding a 20-wide window across each high-conflict
paper's source_conflict list. For each offset window, claude (Sonnet, conc 5) audits papers that still
have conflicts at that depth. Appends to residual_errors.tsv. (codex dual-check is a separate later pass.)
"""
import csv, json, collections, os, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCR = Path("/tmp/claude-1001/-home-cihebi---------batch-5-team/116a3aaf-1ac6-4814-8939-d02f5b1b2511/scratchpad")
csv.field_size_limit(10**9)

rows = list(csv.DictReader(open(ROOT / "releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv"), delimiter='\t'))
conf = collections.Counter(r['paper_id'] for r in rows if r['status'] == 'source_conflict')
maxc = max(conf.values())
print(f"max conflicts/paper = {maxc}; windows 20..{maxc} step 20", flush=True)

for off in range(20, maxc, 20):
    papers = [p for p, n in conf.items() if n > off and (ROOT / f"papers/{p}/source/paper.xml").exists()]
    if not papers:
        continue
    wl = SCR / f"residual_wl_o{off}.json"
    wl.write_text(json.dumps(papers))
    env = {**os.environ,
           "CLAUDE_MODEL": "sonnet", "CLAUDE_CONC": "5", "ENGINE": "claude",
           "BUILD_IF_MISSING": "1", "FORCE_BUILD": "1", "EXP_MAX": "20", "V2_OFFSET": str(off),
           "CLAUDE_WORKLIST": wl.name,
           "CLAUDE_STATE": f"pipeline_v2/residual_state_o{off}.json",
           "CLAUDE_OUT": "pipeline_v2/residual_errors.tsv"}
    print(f"=== window offset={off}: {len(papers)} papers ===", flush=True)
    subprocess.run(["python3", str(ROOT / "pipeline_v2/claude_audit.py")], env=env)
print("RESIDUAL_EXHAUST_DONE", flush=True)
