Re-review completed. I did not rerun the initial bootstrap, and I left the paper non-accepted.

Result: `review_status=blocked_missing_primary_material`, `publication_grade=false`. The local XML/PDF are a SpringerPlus SOD thermostability paper, while APD6 `AP02766` is a Sus scrofa lysozyme antimicrobial record tied to a different PMID/title. No source-supported primary AMP activity/toxicity rows are locally recoverable.

Updated key artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_s40064-016-1854-9/final/activity_toxicity_evidence.json): `activity_records=[]`, database-only APD6 annotation preserved separately.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_s40064-016-1854-9/final/database_record_verification.json): `source_conflict=2`, `database_only_no_primary_source=1`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_s40064-016-1854-9/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_s40064-016-1854-9/work/review/quality_feedback.json): 3 blocking QC reasons and 3 `unrecoverable_material_gaps`.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1186_s40064-016-1854-9/rework/rework_responses.jsonl): old `rwk-complete-test-0001` closed/superseded; new `rwk-obtainable-gap-0002` remains open.

Gate evidence:
- Semantic gate: [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1186_s40064-016-1854-9.semantic_gate.json) fails intentionally on `review_status_not_publication_grade`, `publication_grade_not_true`, `missing_activity_records`.
- Publication QA: [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1186_s40064-016-1854-9.publication_quality.json) fails on `open_rework_targets=1`.
- Message bus validation passed; workflow state is `analysis_blocked` with open ticket `rwk-obtainable-gap-0002`.

