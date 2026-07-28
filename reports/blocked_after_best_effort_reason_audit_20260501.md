# 50-Paper blocked_after_best_effort Reason Audit - 2026-05-01

Source aggregate: `reports/true_rework_queue_50_aggregate_progress_20260501.json`.

## Summary

- Blocked papers: 11 / 50
- `worker_timeout_or_overbroad_prompt`: 5
- `activity_table_extraction_gap`: 3
- `missing_external_supplement`: 2
- `figure_chart_values_unrecoverable`: 1

## Per-Paper Reasons

| Paper | Attempts | Category | Primary reason | Gate evidence |
| --- | ---: | --- | --- | --- |
| `doi__10.1002_cmdc.202200291` | 1 | `worker_timeout_or_overbroad_prompt` | Owner Codex worker timed out after 900s; controller blocked and advanced. | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1002_cmdc.202200291.true_rework_queue_attempt_1.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1002_cmdc.202200291.true_rework_queue_attempt_1.after_worker.publication_quality.json` |
| `doi__10.1007_s00018-022-04440-w` | 1 | `worker_timeout_or_overbroad_prompt` | Owner Codex worker timed out after 900s; controller blocked and advanced. | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-022-04440-w.true_rework_queue_attempt_1.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-022-04440-w.true_rework_queue_attempt_1.after_worker.publication_quality.json` |
| `doi__10.1007_s00253-020-10685-x` | 1 | `worker_timeout_or_overbroad_prompt` | Owner Codex worker timed out after 900s; controller blocked and advanced. | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00253-020-10685-x.true_rework_queue_attempt_1.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00253-020-10685-x.true_rework_queue_attempt_1.after_worker.publication_quality.json` |
| `doi__10.1007_s10989-015-9494-4` | 1 | `worker_timeout_or_overbroad_prompt` | Owner Codex worker timed out after 900s; controller blocked and advanced. | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s10989-015-9494-4.true_rework_queue_attempt_1.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s10989-015-9494-4.true_rework_queue_attempt_1.after_worker.publication_quality.json` |
| `doi__10.1007_s12602-018-9501-0` | 1 | `worker_timeout_or_overbroad_prompt` | Owner Codex worker timed out after 900s; controller blocked and advanced. | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s12602-018-9501-0.true_rework_queue_attempt_1.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s12602-018-9501-0.true_rework_queue_attempt_1.after_worker.publication_quality.json` |
| `doi__10.1002_cbic.202100609` | 5 | `figure_chart_values_unrecoverable` | Local primary material contains Figure 4 as a bar-chart image plus caption/method text, but no source table or embedded data with exact HepG2/HEK293 percentages. Exact database percentages cannot be source-promoted without a structured primary source table or validated manual digitization. | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1002_cbic.202100609.true_rework_queue_attempt_5.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1002_cbic.202100609.true_rework_queue_attempt_5.after_worker.publication_quality.json` |
| `doi__10.1007_s12602-022-10036-4` | 5 | `missing_external_supplement` | Attempt 5 bounded worker-3/4/6 re-review reopened the handoff, raw packet symlinks, XML/PDF/PDF text, supplementary index/tables/text/archive artifacts, all eight local landing-*.bin supplementary assets, landed asset manifests, landed_assets_current, and linked database rows. No true Springer XLSX/DOCX supplement is present locally; landing-*.bin files are HTML article pages with remote MOESM links only, packet supplementary_tables remains empty, and no paper-local office/archive/image supplement exists for OCR... | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s12602-022-10036-4.true_rework_queue_attempt_5.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s12602-022-10036-4.true_rework_queue_attempt_5.after_worker.publication_quality.json` |
| `doi__10.1016_j.antiviral.2005.10.005` | 5 | `activity_table_extraction_gap` | One or more activity-bearing tables could not be safely parsed into target/entity/value rows.; No parser-supported activity/toxicity rows were extracted; worker must inspect XML/PDF/prose/figures/supplements before acceptance. | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1016_j.antiviral.2005.10.005.true_rework_queue_attempt_5.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1016_j.antiviral.2005.10.005.true_rework_queue_attempt_5.after_worker.publication_quality.json` |
| `doi__10.1016_j.antiviral.2008.10.001` | 5 | `activity_table_extraction_gap` | No parser-supported activity/toxicity rows were extracted; worker must inspect XML/PDF/prose/figures/supplements before acceptance. | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1016_j.antiviral.2008.10.001.true_rework_queue_attempt_5.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1016_j.antiviral.2008.10.001.true_rework_queue_attempt_5.after_worker.publication_quality.json` |
| `doi__10.1016_j.apsb.2021.07.026` | 5 | `activity_table_extraction_gap` | No parser-supported activity/toxicity rows were extracted; worker must inspect XML/PDF/prose/figures/supplements before acceptance. | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1016_j.apsb.2021.07.026.true_rework_queue_attempt_5.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1016_j.apsb.2021.07.026.true_rework_queue_attempt_5.after_worker.publication_quality.json` |
| `doi__10.1007_s00018-020-03755-w` | 5 | `missing_external_supplement` | Final bounded local re-review found only Springer HTML landing pages for the available supplementary assets. The local HTML points to 18_2020_3755_MOESM1_ESM.docx, but that DOCX is absent from packet, paper source, landed_assets, downloaded_assets, landed_assets_current, and merged-output surfaces checked locally. | `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-020-03755-w.true_rework_queue_attempt_5.after_worker.semantic_gate.json`; `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-020-03755-w.true_rework_queue_attempt_5.after_worker.publication_quality.json` |

## Optimization Backlog

| Priority | Area | Observed from | Recommendation |
| --- | --- | --- | --- |
| P0 | controller watchdog and lane resilience | 5 blocked papers with codex_worker_timeout in lane1 retry | Keep TimeoutExpired handling, add periodic per-paper heartbeat, persist partial stdout/stderr, and classify timeout as retryable-narrow-owner work rather than true material absence. |
| P0 | owner-specific prompt slicing | timeout papers still carried broad worker-6/database/activity obligations | Generate separate worker-2/3/4/5/6 prompts from the same ticket instead of a single all-owner prompt; run only the highest-value owner first. |
| P1 | unsupported activity table extraction | no_supported_activity_rows_extracted / activity_extraction_requires_worker2_rework in antiviral and applied microbiology papers | Improve worker-2 parsers for peptide/virus IC50 tables, MIC/MBC matrices, antibiofilm tables, and target-row/entity-row layouts; when parser fails, emit structured table-shape JSON for manual/vision fallback. |
| P1 | supplement resolver for landing pages | Springer MOESM DOCX/XLSX assets present only as HTML landing-*.bin pages in two blocked papers | Detect HTML disguised as .bin/.xlsx/.zip, extract remote supplementary hrefs, stage true DOCX/XLSX/PDF assets when available, or mark external_source_needed before repeated worker loops. |
| P1 | figure/bar-chart numeric recovery policy | Figure 4 cytotoxicity exact percentages unavailable for doi__10.1002_cbic.202100609 | Add a controlled chart-digitization/OCR lane for figure-only values; otherwise preserve exact database percentages as source_conflict and avoid blocking unrelated accepted evidence. |
| P1 | mechanism ontology cleanup | mechanism_framework_notes_not_source_reviewed in doi__10.1007_s10989-015-9494-4 | Reject framework-note artifacts before worker-6; require worker-5 to replace scaffold notes with source-located mechanism class or explicit unknown. |
| P2 | automatic aggregate reporting | manual aggregation was needed after lane1 retry | Add a merge script that reads all lane summaries plus pre-split papers, validates 50/50 after-worker gates, and writes one final aggregate report automatically. |

## Notes

- `blocked_after_best_effort` is a controlled non-acceptance status, not a publication-grade result.
- Timeout-driven blocks should be treated as process/prompt optimization targets before being interpreted as true source absence.
- Source-material gaps such as missing DOCX/XLSX supplements or figure-only exact values require external-source acquisition or a dedicated recovery lane.
