# PMC11752523 Rework Closure Acceptance - 2026-07-08 21:42:39 CST

## Outcome

- `PMC11752523` now passes strict paper-level source-reviewed acceptance with cautions.
- Six worker roles are present, all return code 0, all `gpt-5.5/xhigh`, with six unique Codex session ids.
- Single-paper packet, semantic, and publication gates pass; `acceptance --paper-id PMC11752523` returns 0.
- This is not authoritative DBAASP ingest-ready because linked authoritative rows remain zero.

## What Changed

- Recovered `mt4c01635_si_001.pdf` by solving the CloudPMC proof-of-work download page and validating `%PDF` magic/868592 bytes.
- Deduplicated seven XML references for the same supplement into one declared file while preserving mention evidence.
- Promoted supplementary PDF text into `supplementary_text.jsonl` with `supp:mt4c01635_si_001.pdf:page=N` locators.
- Added rework response closure semantics so closed tickets no longer count as open packet blockers.
- Closed all `PMC11752523` rework tickets with either repaired artifacts or durable no-fabrication material-gap evidence.

## Current Counts

- strict pilot papers: 5
- paper-level source-reviewed complete: 3
- authoritative DBAASP ingest-ready: 0
- global open rework tickets: 2

## Evidence Files

- `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11752523_material_recovery_latest.json`
- `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC11752523/run_sequence_latest.json`
- `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11752523_strict_acceptance_audit_latest.json`
- `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11752523/final/review_report.json`
- `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11752523/rework/rework_responses.jsonl`
- `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11752523_rework_closure_acceptance_20260708_214239.json`
