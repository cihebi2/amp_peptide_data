# Refined True-Rework Queue Status

- generated_at: `2026-06-20T13:40:52Z`
- source_lane_summary_count: `5`
- paper_count: `30`
- completion_claim: `refined_status_interpretation_not_blanket_publication_grade_clean_acceptance`
- clean_initial_pass_count: `5`
- post_rework_acceptance_count: `9`
- blocked_or_infrastructure_count: `16`

## Refined Status Counts
- `accepted_after_rework_attempt1`: `9` - One owner-worker re-review repaired the paper and strict gates passed.
- `accepted_clean_initial_gate_pass`: `5` - Strict gates already passed before owner-worker rework.
- `blocked_model_prompt_safety_restriction_quality_gates_open`: `15` - Codex owner-worker hit a model prompt/content safety restriction while strict scientific gates remained open; this is not proof that source material is absent.
- `blocked_source_gap_missing_external_supplement`: `1` - A specific supplementary source/table is absent or only present as a non-data placeholder.

## Refined Category Counts
- `accepted_after_rework`: `9`
- `accepted_clean`: `5`
- `blocked_source_gap`: `1`
- `infrastructure_model_policy_blocked`: `15`

## Recommended Next Actions
- `none`: `5`
- `retry_only_after_source_staging`: `1`
- `retry_with_policy_safe_minimized_context_or_manual_queue`: `15`
- `sample_audit_only`: `9`

## Follow-Up Queue Manifests
- `infra_recovery`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/followup_queues/owner_worker_rework_20260620T090048Z_infra_recovery.json`
- `owner_context_rework_needed`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/followup_queues/owner_worker_rework_20260620T090048Z_owner_context_rework_needed.json`
- `parser_manual_extraction_needed`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/followup_queues/owner_worker_rework_20260620T090048Z_parser_manual_extraction_needed.json`
- `safe_prompt_rework_needed`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/followup_queues/owner_worker_rework_20260620T090048Z_safe_prompt_rework_needed.json`
- `source_staging_needed`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/followup_queues/owner_worker_rework_20260620T090048Z_source_staging_needed.json`
- `watchdog_retry`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/followup_queues/owner_worker_rework_20260620T090048Z_watchdog_retry.json`

## Accepted Sample Audit
- `accepted_sample_audit`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/followup_queues/owner_worker_rework_20260620T090048Z_accepted_sample_audit.json`

## Lane Sources
- lane1: papers=`6` path=`reports/true_rework_queue_needs_targeted_owner_nonzero_gate_return_lane01_20260620T090048Z_latest.json`
- lane2: papers=`6` path=`reports/true_rework_queue_needs_targeted_owner_nonzero_gate_return_lane02_20260620T090048Z_latest.json`
- lane3: papers=`6` path=`reports/true_rework_queue_needs_targeted_owner_nonzero_gate_return_lane03_20260620T090048Z_latest.json`
- lane4: papers=`6` path=`reports/true_rework_queue_needs_targeted_owner_nonzero_gate_return_lane04_20260620T090048Z_latest.json`
- lane5: papers=`6` path=`reports/true_rework_queue_needs_targeted_owner_nonzero_gate_return_lane05_20260620T090048Z_latest.json`
