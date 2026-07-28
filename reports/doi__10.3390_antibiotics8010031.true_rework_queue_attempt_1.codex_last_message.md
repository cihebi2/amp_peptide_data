Re-reviewed exactly `doi__10.3390_antibiotics8010031` and left it non-accepted.

Updated the worker-2/4/6 artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3390_antibiotics8010031/final/activity_toxicity_evidence.json): kept `activity_records: []`, recorded source-reviewed context, and added blocking `unrecoverable_material_gaps`.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3390_antibiotics8010031/final/database_record_verification.json): changed DRAMP29328 to `database_only_no_primary_source`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3390_antibiotics8010031/final/review_report.json): `publication_grade=false`, `review_status=needs_targeted_rework`.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3390_antibiotics8010031/work/review/quality_feedback.json): `issue_count=2`, concrete blocking reasons.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.3390_antibiotics8010031/rework/rework_responses.jsonl): added the bounded repair response and gate evidence.

Reran gates:
- Semantic: failed as expected with `review_status_not_publication_grade`, `publication_grade_not_true`, `missing_activity_records`.
- Publication QA: failed as expected with `open_rework_targets=1`.

Stop condition: local XML/PDF/OA package/supplement/database surfaces were exhausted; no primary activity/toxicity endpoint rows are locally supportable without fabrication, so ticket `rwk-complete-test-0001` remains open as `open_blocking_unrecoverable`.

