# Validation420 Source-Review Run Status

Last updated: `2026-06-25T10:34:53+08:00`

## Current Run

- Manifest: `reports/nar_resource_freeze_v1/manual_validation/validation_manifest_latest.csv`
- Packet index: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/packet_index_latest.csv`
- Packet count / unique papers: `224`
- Manifest rows covered: `420`
- Runner: `scripts/run_validation420_source_reviews.py`
- Active command: `python scripts/run_validation420_source_reviews.py --packet-index reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/packet_index_latest.csv --offset 20 --parallel 4 --timeout-seconds 3600`
- Active session id in this Codex run: `17482`
- Status: `running_remaining_204_after_initial_20`

## Completed Initial Batch

- Completed packets: `20`
- Reviewed validation rows: `31`
- Valid result JSON: `20/20`
- Final decisions: `accepted_with_cautions=7`, `needs_targeted_rework=13`
- Sample row decisions: `confirmed=1`, `confirmed_with_caution=17`, `needs_targeted_rework=13`
- Rework tickets: `18`
- Cautions: `74`

## Progress Check 2026-06-25T10:34:53+08:00

- Runner process: `active`, PID `3373866`.
- Active worker slots: `4`, currently on `V420P0036`-`V420P0039`.
- Result files present: `33/224` paper packets, covering `55/420` validation rows.
- Runner-status valid results: `31`; active result files awaiting runner-status recovery: `2` (`V420P0036`, `V420P0038`).
- Runner invalid/interrupted statuses: `4` packets / `12` validation rows, all `codex_finished_no_valid_result` + `missing_result_json`; treat as infra/safety-policy interruption pending safer retry, not scientific rejection.
- Current source-review decisions from result files: `accepted_with_cautions=12`, `needs_targeted_rework=20`, `blocked_missing_primary_material=1`, `missing_result=191`.
- Sample-row decisions: `confirmed=1`, `confirmed_with_caution=29`, `needs_targeted_rework=14`, `blocked_missing_primary_material=11`.
- Rework tickets currently summarized: `28`; cautions: `123`.
- Summary evidence: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_source_review_summary_latest.json`.

## Current Evidence Files

- Packet summary: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/packet_summary_latest.json`
- Runner latest summary: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/runner/validation420_source_review_summary_latest.json`
- Source-review summary: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_source_review_summary_latest.json`
- Source-review report: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_source_review_report_latest.md`
- Rework tickets: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_rework_tickets_latest.jsonl`

## Rules

- Do not interpret current source-review results as final closure.
- `needs_targeted_rework` rows require owner-lane repair and worker-6 final adjudication before publication-grade acceptance.
- `accepted_with_cautions` remains non-clean; cautions/conflicts must be preserved.
- After the active runner stops, run `python scripts/summarize_validation420_source_reviews.py` to refresh aggregate counts.

## Queue Soft Pause Requested 2026-06-25T10:48:14+08:00

- Runner parent PID `3373866` was stopped with `SIGSTOP` only; active Codex children were not killed.
- No new packet dispatch can occur while the parent remains stopped.
- Active child PIDs at pause: `3451417,3451772,3455547,3457913`.
- Watcher PID: `3469905`; watcher records completion after those children exit.
- Pause marker: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/runner/validation420_queue_pause_marker_latest.json`.

## Saved Pause Checkpoint 2026-06-25T14:38:08+08:00

- Queue state: `soft_paused_active_children_finished_parent_still_stopped`; parent runner PID `3373866` remains stopped, so no new packets are dispatched.
- Existing result files: `39/224` packets; reviewed rows `114/420`.
- Source-review contract QA over existing results: `contract_pass=39`, `contract_fail=0`, `blocking_output_problems=0`, `warnings=1`.
- Current decisions: `{"accepted_with_cautions": 13, "blocked_missing_primary_material": 4, "missing_result": 185, "needs_targeted_rework": 22}`.
- Sample-row decisions: `{"blocked_missing_primary_material": 65, "confirmed": 1, "confirmed_with_caution": 34, "needs_targeted_rework": 14}`.
- Rework artifacts: `targets=35`, `tickets=35`, `cautions=146`.
- Known non-blocking QA warning: `V420P0001` references one historical rework id not duplicated in packet-level `rework_targets`; current packet still has validation420 rework tickets.
- Checkpoint QA JSON: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_pause_checkpoint_qa_latest.json`.
- Checkpoint QA Markdown: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_pause_checkpoint_qa_latest.md`.

## Runner/QA Detail Refresh 2026-06-25T14:40:25+08:00

- Runner statuses: `status_files=43`, `valid_result=39`, `invalid_or_interrupted=4`, `no_status_not_started=181`.
- Runner state counts: `{"codex_finished_no_valid_result": 4, "completed_valid_result": 35, "paused_child_completed_valid_result": 4}`.
- Invalid/interrupted packets: `V420P0022`, `V420P0029`, `V420P0030`, `V420P0031`; all lack result JSON and require safer retry later, not scientific rejection.
- Latest QA report: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_pause_checkpoint_qa_latest.md`.
