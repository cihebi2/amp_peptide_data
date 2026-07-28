Re-reviewed `doi__10.1007_s00018-020-03755-w` for worker-3/4/6 only. I left the paper non-accepted: `review_status=blocked_missing_primary_material`, `publication_grade=false`, with the worker-3 ticket still open for `supplementary_moesm1_docx_missing_from_local_packet`.

Updated the durable artifacts, mainly:
- [supplementary_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/work/supplementary_methods/supplementary_evidence.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/work/review/quality_feedback.json)
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/final/review_report.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1007_s00018-020-03755-w/rework/rework_responses.jsonl)

Source recovery result: local supplementary `.bin` files still inspect as Springer HTML landing pages, and exact local search found no `18_2020_3755_MOESM1_ESM.docx`. Worker-4 database status is retained as complete: `113 source_verified`, `28 source_conflict`.

Gate evidence:
- Semantic gate: [report](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-020-03755-w.codex_cli_rereview_20260502T101815Z.semantic_gate.json), return code `1`, `issue_count=2`.
- Publication QA: [report](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-020-03755-w.codex_cli_rereview_20260502T101815Z.publication_quality.json), return code `2`, `publication_grade_pass=false`, `open_rework_targets=1`.
- JSON validation passed for 11 JSON files and all 11 JSONL response lines.

