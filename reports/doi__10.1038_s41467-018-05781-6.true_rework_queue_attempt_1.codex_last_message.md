Re-reviewed `doi__10.1038_s41467-018-05781-6` without rerunning the initial workflow/bootstrap.

Repaired worker-2/4/6 surfaces:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41467-018-05781-6/final/activity_toxicity_evidence.json): rebuilt to 128 source-located activity/toxicity rows.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41467-018-05781-6/final/database_record_verification.json): 60 linked database audits, preserving `source_conflict` and `sequence_modified_not_normalized` cases.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41467-018-05781-6/final/review_report.json): final status is `accepted_with_cautions`, not clean acceptance.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41467-018-05781-6/work/review/quality_feedback.json): `issue_count: 0`, no open rework targets.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41467-018-05781-6/rework/rework_responses.jsonl): closed `rwk-complete-test-0001`.

Remaining findings are caution-level only: database hemolysis precision not directly recoverable as a table-exact source value, database condition text conflicts, and APD6 Orn-to-K modified-sequence normalization. No `unrecoverable_material_gaps` were needed.

Validation:
- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41467-018-05781-6.semantic_gate.json): `pass=1`, `fail=0`, `issue_count=0`.
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41467-018-05781-6.publication_quality.json): `publication_grade_pass=true`, `risk_counts={}`.
- [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41467-018-05781-6.complete_message_test_report.json): updated to `accepted_with_cautions`, open rework count `0`.

