# 32-paper timeout retry aggregate (1800s watchdog)

- Generated: `2026-05-02T05:05:01Z`
- Source manifest: `reports/true_rework_queue_manifest_100_obtainable_timeout_retry_32_20260502.json`
- Lane latest summaries: `5`
- Integrity: `ok=True`, `paper_count=32`, `manifest_count=32`

## Counts

- terminal `blocked_after_best_effort`: 6
- terminal `accepted_after_rework`: 26

- result `blocked_figure_chart_value_gap`: 3
- result `accepted_after_rework`: 26
- result `blocked_missing_external_supplement`: 1
- result `blocked_watchdog_timeout_retryable`: 1
- result `blocked_activity_table_extraction_gap`: 1

## Conversion

- `previous_timeout_retryable_count`: 32
- `accepted_after_1800s_retry`: 26
- `still_blocked_after_1800s_retry`: 6
- `still_timeout_retryable`: 1
- `converted_to_non_timeout_gap`: 5

## Blocked after retry

- lane1 `doi__10.1002_cbic.202100609`: `blocked_figure_chart_value_gap` / `figure_or_chart_exact_value_unrecoverable` / retryability `retry_only_with_digitization_or_external_source`
- lane1 `doi__10.1007_s00018-020-03755-w`: `blocked_missing_external_supplement` / `missing_external_supplement` / retryability `retry_only_after_source_staging`
- lane1 `doi__10.1007_s00253-020-10685-x`: `blocked_figure_chart_value_gap` / `figure_or_chart_exact_value_unrecoverable` / retryability `retry_only_with_digitization_or_external_source`
- lane2 `doi__10.1016_j.cell.2024.07.027`: `blocked_watchdog_timeout_retryable` / `codex_worker_timeout` / retryability `retry_with_longer_watchdog_or_narrower_owner_prompt`
- lane3 `doi__10.1016_j.isci.2021.102480`: `blocked_activity_table_extraction_gap` / `activity_table_rows_not_safely_extracted` / retryability `retry_with_worker2_table_shape_or_manual_vision_fallback`
- lane5 `doi__10.1016_j.virol.2010.11.014`: `blocked_figure_chart_value_gap` / `figure_or_chart_exact_value_unrecoverable` / retryability `retry_only_with_digitization_or_external_source`
