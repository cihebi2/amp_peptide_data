Re-reviewed `doi__10.1038_s41598-020-60623-0` and repaired only worker-2/4/6-owned layers.

Final state is `accepted_with_cautions`, `publication_grade=true`, with `open_rework_ticket_count=0`. The old ticket `rwk-complete-test-0001` is closed in [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-020-60623-0/rework/rework_responses.jsonl).

Changed key artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-60623-0/final/activity_toxicity_evidence.json): 104 source-located Table 3/4 activity/MIC records.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-60623-0/final/database_record_verification.json): 54 audits, `source_verified=52`, `source_conflict=2`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-60623-0/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-60623-0/work/review/quality_feedback.json): no `qc_failure_reasons`, no `rework_targets`, no `unrecoverable_material_gaps`.

Validation:
- [semantic gate](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-020-60623-0.semantic_gate.json): `pass_count=1`, `issue_count=0`.
- [publication quality](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-020-60623-0.publication_quality.json): `publication_grade_pass=true`, `risk_counts={}`.
- [complete report](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-020-60623-0.complete_message_test_report.json): `terminal_status=publication_grade_ready`.

Material layer remains separate as `material_extracted_with_gaps`; the gap is now documented as nonblocking for this worker-2/4/6 repair.

