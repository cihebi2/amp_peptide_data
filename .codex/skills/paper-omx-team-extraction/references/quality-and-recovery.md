# Quality And Recovery

## Final acceptance rules

Treat a paper as complete only when the repo's validator logic agrees.

Read and use:

- `workspace-guide/team-paper-sample/BATCH_PAPER_PROCESSING_RUNBOOK_ZH.md`
- `workspace-guide/team-paper-sample/paper_batch_controller.py`

Key acceptance points:

- `materials_manifest.json`, `mechanism_record.json`, `vc_projection.json`, and `review_report.json` all exist
- final JSON parses cleanly
- `final_artifacts_structurally_ready(root, paper_id) == True`
- `final_artifacts_quality_issues(root, paper_id) == []`

## Blocking patterns

These are common reasons a paper is not actually done even if files exist:

- `controller_fallback_generated`
- `worker_deterministic_generated`
- `source_direct_fallback`
- supplementary output says `no local supplementary asset` even though staged files exist
- lead entity is generic or title-like
- final schema is ad hoc rather than canonical

## Common recovery patterns

### Worker contract / bootstrap drift

Symptoms:

- team exists but inbox/task text looks generic
- issue log records `contract_rewrite_rescue` or `worker_bootstrap_rescue`

Response:

- re-run the stable launcher or controller reconciliation path
- prefer controller reconciliation before manual worker pokes
- if one lane is the true blocker, re-run that lane with `run-role`

### Claim drift

Symptoms:

- final artifacts are present
- task remains `in_progress` or closes under the wrong worker
- issue log records `task4_claim_drift` or `task*_claim_drift_repair`

Response:

- validate the actual artifacts first
- run controller `once` so it can auto-close or repair the drift
- avoid manually forcing unrelated workers to claim the task

### Worker-3 supplementary mismatch

Symptoms:

- staged supplementary files exist under `source/supplementary/`
- `work/supp_evidence/evidence.json` still reports no local supplementary asset
- merge/review emits warnings such as `supp_evidence_fallback_missed_local_pdf`

Response:

- reopen or re-run task 3 only
- verify XML linkage, package inventory, and staged source files agree
- re-run controller once before letting task 4 proceed

### Worker-4 blocked forever

Check in order:

1. task-4 JSON
2. `quality_feedback.json`
3. upstream artifacts from task 1/2/3
4. validator result for final files

Do not force task 4 if upstream evidence is not accepted.

## Recommended incident sources

Use these when writing postmortems or repair docs:

- `workspace-guide/team-paper-sample/HOME_DL_INCIDENTS_V1.md`
- `workspace-guide/team-paper-sample/STABILITY_REMEDIATION_CHECKLIST.md`
- `workspace-guide/team-paper-sample/extraction-issues-20260423/README.md`
- `workspace-guide/team-paper-sample/batch-v1/issues_fresh50_strict_reaudit_excluding_final_ready_20260422.jsonl`
