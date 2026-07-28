# Next500 obtainable queue aggregate

- generated_at_local: `2026-05-04 15:18:14 CST (+0800)`
- manifest: `reports/true_rework_queue_manifest_next500_obtainable_20260502.json`
- lane_summary_count: `10`
- total_papers: `500`
- completion_claim: `queue_control_and_rework_execution_report_not_blanket_publication_grade_acceptance`

## Terminal status counts
- `accepted_after_rework`: `425`
- `blocked_after_best_effort`: `75`

## Result status counts
- `accepted_after_rework`: `425`
- `blocked_activity_table_extraction_gap`: `3`
- `blocked_figure_chart_value_gap`: `22`
- `blocked_missing_external_supplement`: `17`
- `blocked_rework_cap_unresolved`: `2`
- `blocked_watchdog_timeout_retryable`: `20`
- `infrastructure_codex_worker_retry_exhausted`: `11`

## Result category counts
- `accepted`: `425`
- `blocked_parser_or_manual_extraction_gap`: `3`
- `blocked_process_timeout`: `20`
- `blocked_quality_gate_unresolved`: `2`
- `blocked_source_gap`: `39`
- `infrastructure_retry_exhausted`: `11`

## Retry logs
- `reports/worker_infra_retries_20260503.jsonl` rows=`90` papers=`29` exhausted=`11` codes=`{'codex_worker_nonzero_exit': 52, 'codex_api_or_network_error': 36, 'codex_worker_interrupted': 2}`

## Lane summaries
- lane1: papers=`50` terminal={'accepted_after_rework': 35, 'blocked_after_best_effort': 15} result={'accepted_after_rework': 35, 'blocked_figure_chart_value_gap': 7, 'blocked_missing_external_supplement': 1, 'blocked_watchdog_timeout_retryable': 7} path=`reports/true_rework_queue_queue_next500_1800_lane1_latest.json`
- lane2: papers=`50` terminal={'accepted_after_rework': 38, 'blocked_after_best_effort': 12} result={'accepted_after_rework': 38, 'blocked_figure_chart_value_gap': 3, 'blocked_missing_external_supplement': 5, 'blocked_watchdog_timeout_retryable': 4} path=`reports/true_rework_queue_queue_next500_1800_lane2_latest.json`
- lane3: papers=`50` terminal={'accepted_after_rework': 39, 'blocked_after_best_effort': 11} result={'accepted_after_rework': 39, 'blocked_figure_chart_value_gap': 2, 'blocked_missing_external_supplement': 2, 'blocked_rework_cap_unresolved': 1, 'blocked_watchdog_timeout_retryable': 5, 'infrastructure_codex_worker_retry_exhausted': 1} path=`reports/true_rework_queue_queue_next500_1800_lane3_latest.json`
- lane4: papers=`50` terminal={'accepted_after_rework': 47, 'blocked_after_best_effort': 3} result={'accepted_after_rework': 47, 'blocked_rework_cap_unresolved': 1, 'blocked_watchdog_timeout_retryable': 1, 'infrastructure_codex_worker_retry_exhausted': 1} path=`reports/true_rework_queue_queue_next500_1800_lane4_latest.json`
- lane5: papers=`50` terminal={'accepted_after_rework': 43, 'blocked_after_best_effort': 7} result={'accepted_after_rework': 43, 'blocked_figure_chart_value_gap': 2, 'blocked_missing_external_supplement': 1, 'infrastructure_codex_worker_retry_exhausted': 4} path=`reports/true_rework_queue_queue_next500_1800_lane5_latest.json`
- lane6: papers=`50` terminal={'accepted_after_rework': 45, 'blocked_after_best_effort': 5} result={'accepted_after_rework': 45, 'blocked_figure_chart_value_gap': 1, 'blocked_watchdog_timeout_retryable': 1, 'infrastructure_codex_worker_retry_exhausted': 3} path=`reports/true_rework_queue_queue_next500_1800_lane6_latest.json`
- lane7: papers=`50` terminal={'accepted_after_rework': 43, 'blocked_after_best_effort': 7} result={'accepted_after_rework': 43, 'blocked_activity_table_extraction_gap': 2, 'blocked_figure_chart_value_gap': 1, 'blocked_missing_external_supplement': 3, 'blocked_watchdog_timeout_retryable': 1} path=`reports/true_rework_queue_queue_next500_1800_lane7_latest.json`
- lane8: papers=`50` terminal={'accepted_after_rework': 43, 'blocked_after_best_effort': 7} result={'accepted_after_rework': 43, 'blocked_activity_table_extraction_gap': 1, 'blocked_figure_chart_value_gap': 4, 'blocked_missing_external_supplement': 1, 'infrastructure_codex_worker_retry_exhausted': 1} path=`reports/true_rework_queue_queue_next500_1800_lane8_latest.json`
- lane9: papers=`50` terminal={'accepted_after_rework': 45, 'blocked_after_best_effort': 5} result={'accepted_after_rework': 45, 'blocked_figure_chart_value_gap': 1, 'blocked_missing_external_supplement': 3, 'blocked_watchdog_timeout_retryable': 1} path=`reports/true_rework_queue_queue_next500_1800_lane9_latest.json`
- lane10: papers=`50` terminal={'accepted_after_rework': 47, 'blocked_after_best_effort': 3} result={'accepted_after_rework': 47, 'blocked_figure_chart_value_gap': 1, 'blocked_missing_external_supplement': 1, 'infrastructure_codex_worker_retry_exhausted': 1} path=`reports/true_rework_queue_queue_next500_1800_lane10_latest.json`
