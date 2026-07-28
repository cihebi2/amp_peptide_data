# Strict Independent Codex Worker Audit - 2026-07-08 19:31:45 CST

## Bottom Line

- Current strict pilot papers all have evidence of six separate Codex CLI worker sessions (`worker-1`..`worker-6`) in stderr logs.
- Only 2/4 papers pass strict paper-level source-reviewed completion: `PMC11735859` and `PMC13054752`.
- `PMC13036774` had a clean six-worker run but Worker-6 rejected it as `needs_targeted_rework` because declared ACS supplementary material/database links are missing.
- `PMC13036000` launched six Codex CLI sessions, but worker-2 and worker-6 failed with `model_safety_content_filter`; it must not be counted even though final semantic/publication artifacts can over-pass.
- 0/4 papers are authoritative DBAASP-ingest-ready because linked authoritative rows are absent.

## Evidence Table

| paper | strict verdict | workers | unique sessions | gpt-5.5/xhigh | all return 0 | review | acceptance | failed workers |
| --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| `PMC13036774` | `independent_workers_ran_but_worker6_rejected_for_rework` | 6 | 6 | True | True | `needs_targeted_rework` | False | - |
| `PMC13036000` | `codex_sessions_launched_but_worker_run_not_clean` | 6 | 6 | True | False | `accepted_with_cautions` | False | worker-2:model_safety_content_filter, worker-6:model_safety_content_filter |
| `PMC11735859` | `strict_paper_level_source_review_passed` | 6 | 6 | True | True | `accepted_with_cautions` | True | - |
| `PMC13054752` | `strict_paper_level_source_review_passed` | 6 | 6 | True | True | `accepted_with_cautions` | True | - |

## Gate Evidence

- `status`: paper_count=4, paper_level_source_reviewed_complete=2, authoritative_dbaasp_ingest_ready=0.
- `verify strict_worker_run_gate`: returncode=1, hard_finding_count=2, hard_finding_papers=['PMC13036000'].
- Single-paper `acceptance` was re-run for all four papers in this audit; only `PMC11735859` and `PMC13054752` returned ready=true.

## Important Limits

- PMC13036774 older run_report JSON lacks stored command/session/model fields, but stderr logs contain OpenAI Codex headers, unique session ids, model gpt-5.5, and xhigh effort; current script backfills metadata from stderr.
- This pilot uses sequential independent codex exec workers and packet/rework files, not a currently active durable omx team mailbox state for DBAASP.
- PMC13036000 final review artifacts were written despite worker-2 and worker-6 safety-filter failures; strict_worker_run_gate correctly prevents counting it as complete.
- No accepted paper is authoritative DBAASP-ingest-ready because linked authoritative row counts are zero.

## Reproducible Files

- `script`: `pipeline_v2/deepmine/dbaasp_strict_pilot.py`
- `status_latest`: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `verify_latest`: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `strict_worker_run_gate_latest`: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`
- `worker_logs_root`: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs`
- full audit JSON: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_independent_codex_worker_audit_20260708_193145.json`
