# Refined True-Rework Queue Status

- generated_at: `2026-05-05T05:00:26Z`
- source_lane_summary_count: `10`
- paper_count: `500`
- completion_claim: `refined_status_interpretation_not_blanket_publication_grade_clean_acceptance`
- clean_initial_pass_count: `0`
- post_rework_acceptance_count: `425`
- blocked_or_infrastructure_count: `75`

## Refined Status Counts
- `accepted_after_rework_attempt1`: `407` - One owner-worker re-review repaired the paper and strict gates passed.
- `accepted_after_rework_attempt1_with_infra_retry`: `16` - One owner-worker re-review eventually passed after transient Codex/API/process retry noise.
- `accepted_after_rework_multi_attempt`: `1` - More than one bounded rework attempt was needed before strict gates passed.
- `accepted_after_rework_multi_attempt_with_infra_retry`: `1` - Multiple rework attempts plus transient infra retries were needed before strict gates passed.
- `blocked_parser_gap_activity_table`: `3` - Activity/toxicity rows are present or expected but unsafe under current parser/table handling.
- `blocked_process_timeout_1800s_retryable`: `20` - Owner-worker hit the 1800s watchdog; this is retryable and not proof that material is absent.
- `blocked_quality_gate_rework_cap_unresolved`: `2` - Strict gates remained blocked after the bounded obtainable-only rework cap.
- `blocked_source_gap_figure_chart_exact_value`: `22` - Remaining exact values are figure/chart-only or not safely promotable from local structured material.
- `blocked_source_gap_missing_external_supplement`: `17` - A specific supplementary source/table is absent or only present as a non-data placeholder.
- `infrastructure_retry_exhausted_api_or_network`: `3` - Codex/API/network-like failures exhausted the configured infra retry cap.
- `infrastructure_retry_exhausted_worker_nonzero_exit`: `8` - Codex worker exited non-zero until the configured infra retry cap was exhausted.

## Refined Category Counts
- `accepted_after_rework`: `408`
- `accepted_after_rework_with_infra_noise`: `17`
- `blocked_parser_or_manual_extraction_gap`: `3`
- `blocked_process_timeout`: `20`
- `blocked_quality_gate_unresolved`: `2`
- `blocked_source_gap`: `39`
- `infrastructure_retry_exhausted`: `11`

## Recommended Next Actions
- `defer_to_infrastructure_recovery_queue`: `11`
- `retry_only_after_source_staging`: `17`
- `retry_only_with_digitization_or_external_source`: `22`
- `retry_only_with_more_specific_owner_context`: `2`
- `retry_with_longer_watchdog_or_narrower_prompt`: `20`
- `retry_with_worker2_table_shape_or_manual_vision_fallback`: `3`
- `sample_audit_only`: `407`
- `sample_audit_plus_infra_log_check`: `16`
- `targeted_sample_audit`: `1`
- `targeted_sample_audit_plus_infra_log_check`: `1`

## Follow-Up Queue Manifests
- `infra_recovery`: `reports/followup_queues/true_rework_queue_next500_obtainable_20260505_infra_recovery.json`
- `owner_context_rework_needed`: `reports/followup_queues/true_rework_queue_next500_obtainable_20260505_owner_context_rework_needed.json`
- `parser_manual_extraction_needed`: `reports/followup_queues/true_rework_queue_next500_obtainable_20260505_parser_manual_extraction_needed.json`
- `source_staging_needed`: `reports/followup_queues/true_rework_queue_next500_obtainable_20260505_source_staging_needed.json`
- `watchdog_retry`: `reports/followup_queues/true_rework_queue_next500_obtainable_20260505_watchdog_retry.json`

## Accepted Sample Audit
- `accepted_sample_audit`: `reports/followup_queues/true_rework_queue_next500_obtainable_20260505_accepted_sample_audit.json`

## Lane Sources
- lane1: papers=`50` path=`reports/true_rework_queue_queue_next500_1800_lane1_latest.json`
- lane2: papers=`50` path=`reports/true_rework_queue_queue_next500_1800_lane2_latest.json`
- lane3: papers=`50` path=`reports/true_rework_queue_queue_next500_1800_lane3_latest.json`
- lane4: papers=`50` path=`reports/true_rework_queue_queue_next500_1800_lane4_latest.json`
- lane5: papers=`50` path=`reports/true_rework_queue_queue_next500_1800_lane5_latest.json`
- lane6: papers=`50` path=`reports/true_rework_queue_queue_next500_1800_lane6_latest.json`
- lane7: papers=`50` path=`reports/true_rework_queue_queue_next500_1800_lane7_latest.json`
- lane8: papers=`50` path=`reports/true_rework_queue_queue_next500_1800_lane8_latest.json`
- lane9: papers=`50` path=`reports/true_rework_queue_queue_next500_1800_lane9_latest.json`
- lane10: papers=`50` path=`reports/true_rework_queue_queue_next500_1800_lane10_latest.json`
