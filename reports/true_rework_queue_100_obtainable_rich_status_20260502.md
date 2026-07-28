# 100 篇 obtainable-only richer result status - 2026-05-02

- Paper count: 100
- Legacy terminal_status_counts: `{'accepted_after_rework': 52, 'blocked_after_best_effort': 48}`
- Rich result_status_counts: `{'accepted_after_rework': 52, 'blocked_watchdog_timeout_retryable': 32, 'blocked_missing_external_supplement': 1, 'blocked_activity_table_extraction_gap': 14, 'blocked_no_primary_assay_source': 1}`
- Rich result_category_counts: `{'accepted': 52, 'blocked_process_timeout': 32, 'blocked_source_gap': 2, 'blocked_parser_or_manual_extraction_gap': 14}`

## Watchdog policy

- Future/retry watchdog should be `1800` seconds.
- Existing 900s timeout papers are marked `blocked_watchdog_timeout_retryable`, not source gaps.
- Timeout retry manifest: `reports/true_rework_queue_manifest_100_obtainable_timeout_retry_32_20260502.json`

## Status meanings

- `blocked_watchdog_timeout_retryable`: process/scope timeout; retry with 1800s and/or narrower owner prompt.
- `blocked_activity_table_extraction_gap`: worker-2/manual table extraction needed.
- `blocked_missing_external_supplement`: source gap; retry only after staging supplement.
- `blocked_figure_chart_value_gap`: source gap; retry only with controlled digitization or structured source.
- `blocked_no_primary_assay_source`: review/database-only evidence; keep non-accepted unless primary source appears.
- `accepted_after_rework`: gates passed after owner review.

## Per-paper statuses

| Paper | Legacy terminal | Rich status | Category | Retryability |
| --- | --- | --- | --- | --- |
| `doi__10.1002_advs.202205301` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_advs.202401793` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_advs.202507457` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_advs.202516470` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_anie.201901589` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_cbic.202100151` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_cmdc.201600498` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_cmdc.201900465` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_gch2.202200213` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_mbo3.606` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_mlf2.12123` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_open.201800130` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_pep2.24269` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_pld3.42` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1002_pro.5088` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00018-022-04440-w` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00018-023-04795-8` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00253-012-4578-y` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00253-016-7400-4` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00253-023-12887-5` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00253-023-12947-w` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00262-014-1540-0` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00438-026-02390-7` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00726-012-1388-6` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00726-017-2449-7` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00726-017-2473-7` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s00726-018-2575-x` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s10295-013-1259-5` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s10526-022-10132-y` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s10989-014-9423-y` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s10989-015-9494-4` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s11274-016-2171-8` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s12539-016-0163-x` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s12602-018-9444-5` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s12602-025-10542-1` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s13238-014-0061-0` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1007_s13659-014-0037-z` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.antiviral.2013.11.013` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.antiviral.2017.11.021` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.antiviral.2022.105270` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.bbrc.2004.04.141` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.btre.2020.e00583` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.csbj.2023.05.006` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.jare.2024.09.017` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.jbc.2021.100657` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.jbc.2022.101822` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.jbc.2022.102724` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.jsps.2023.04.001` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.omtn.2020.05.006` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.psj.2023.102695` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.toxrep.2015.06.011` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.vetmic.2020.108708` | `accepted_after_rework` | `accepted_after_rework` | `accepted` | `not_needed` |
| `doi__10.1016_j.antiviral.2005.10.005` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.antiviral.2008.10.001` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.apsb.2021.07.026` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.bbrc.2004.05.046` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.celrep.2020.108254` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.celrep.2021.108959` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.isci.2020.100999` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.jacbts.2020.10.003` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.jmb.2009.10.032` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.peptides.2011.05.015` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.virol.2006.01.029` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.virol.2017.07.033` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_j.virusres.2006.03.001` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1016_s0140-6736(04)15788-7` | `blocked_after_best_effort` | `blocked_activity_table_extraction_gap` | `blocked_parser_or_manual_extraction_gap` | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1007_s12602-022-10036-4` | `blocked_after_best_effort` | `blocked_missing_external_supplement` | `blocked_source_gap` | `retry_only_after_source_staging` |
| `doi__10.1016_j.tibtech.2009.07.004` | `blocked_after_best_effort` | `blocked_no_primary_assay_source` | `blocked_source_gap` | `retry_only_with_primary_source_or_database_snapshot` |
| `doi__10.1002_cbic.202100609` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1002_cmdc.202200291` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1007_s00018-020-03755-w` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1007_s00253-020-10685-x` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1007_s12602-018-9501-0` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.bbrep.2024.101747` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.biomaterials.2013.01.075` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.biomaterials.2013.12.049` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.cell.2024.07.027` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.csbj.2021.08.039` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.csbj.2023.11.031` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.csbj.2024.05.020` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.csbj.2024.09.006` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.dib.2019.104538` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.ebiom.2020.102775` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.fob.2014.01.007` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.heliyon.2021.e07980` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.isci.2020.101785` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.isci.2021.102480` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.isci.2024.110404` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.isci.2025.113286` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.jare.2024.01.023` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.jare.2024.02.016` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.jare.2025.01.005` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.jare.2025.01.029` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.omto.2019.12.001` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.peptides.2003.07.025` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.peptides.2008.04.022` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.tibtech.2024.09.008` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.ultsonch.2021.105676` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.virol.2010.11.014` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
| `doi__10.1016_j.yjsbx.2023.100091` | `blocked_after_best_effort` | `blocked_watchdog_timeout_retryable` | `blocked_process_timeout` | `retry_with_longer_watchdog_or_narrower_owner_prompt` |
