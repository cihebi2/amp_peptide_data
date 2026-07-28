Re-review complete. I left `doi__10.1186_gb-2003-4-5-r31` non-accepted.

Updated the worker-2/4/6 artifacts to reflect source-reviewed obtainable-only truth:

- Activity: [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_gb-2003-4-5-r31/final/activity_toxicity_evidence.json) keeps `activity_records: []`, preserves 14 database-only activity annotations, and records `no_primary_activity_toxicity_assay_rows_in_local_material`.
- Database: [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_gb-2003-4-5-r31/final/database_record_verification.json) now has 16 reviewed rows: 12 `source_conflict`, 2 `database_only_no_primary_source`, 2 `source_verified` literature links.
- Adjudication/QC: [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_gb-2003-4-5-r31/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_gb-2003-4-5-r31/work/review/quality_feedback.json) set `review_status: blocked_missing_primary_material`, `publication_grade: false`, and add targeted ticket `rwk-obtainable-gap-0002`.
- Rework response was appended to [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1186_gb-2003-4-5-r31/rework/rework_responses.jsonl).

Validation evidence:

- JSON validation passed for edited final/packet/work JSON files.
- Semantic gate rerun: [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1186_gb-2003-4-5-r31.semantic_gate.json) fails as expected with 3 issues: non-publication review status, `publication_grade=false`, and missing activity records.
- Publication gate rerun: [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1186_gb-2003-4-5-r31.publication_quality.json) fails as expected with `open_rework_targets: 1`.
- Message bus validation passed; workflow is now `analysis_blocked` with open tickets `rwk-complete-test-0001` and `rwk-obtainable-gap-0002`.

I did not rerun the initial workflow/bootstrap. The stop condition is controlled non-acceptance: local materials were exhausted, missing activity rows are a true source gap, and no unsupported assay values were fabricated.

