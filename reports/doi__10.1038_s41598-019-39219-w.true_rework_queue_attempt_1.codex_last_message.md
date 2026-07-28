Re-review completed for `doi__10.1038_s41598-019-39219-w`.

I repaired the owned worker layers and left the paper non-accepted. The activity layer now has 393 XML-backed primary rows. The database audit now has 457 row audits: `331 source_verified`, `88 database_only_no_primary_source`, `18 source_conflict`, and `20 sequence_modified_not_normalized`. The blocker is recorded as `supplementary_tables_15_16_not_locally_recoverable`.

Updated key artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-019-39219-w/final/activity_toxicity_evidence.json)
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-019-39219-w/final/database_record_verification.json)
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-019-39219-w/final/review_report.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-019-39219-w/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-019-39219-w/rework/rework_responses.jsonl)

Validation:
- JSON/JSONL parse check passed.
- Activity rows: `duplicate_activity_ids=0`, `missing_core=0`.
- Semantic gate rerun: failed only on intentional review-layer status: `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication QA rerun: failed only on `open_rework_targets=1`.

Gate reports:
- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-019-39219-w.codex_re_review.semantic_gate.json)
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-019-39219-w.codex_re_review.publication_quality.json)

The open targeted ticket is `rwk-codex-20260503-0001`. The paper remains `blocked_missing_primary_material`, not accepted.

