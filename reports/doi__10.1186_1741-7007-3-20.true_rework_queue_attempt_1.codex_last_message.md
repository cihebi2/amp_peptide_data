Re-review completed for `doi__10.1186_1741-7007-3-20`. I did not mark it accepted.

Worker-2/4/6 artifacts now record a bounded source-reviewed nonacceptance: `activity_records=0` because local XML/PDF/S1/database material does not support primary AMP activity/toxicity assay rows; linked DRAMP/dbAMP rows are preserved as `7 database_only_no_primary_source`, `1 source_conflict`, and `1 source_verified` literature link only; worker-6 status is `blocked_missing_primary_material`.

Updated key files:
- [final/review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_1741-7007-3-20/final/review_report.json)
- [final/activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_1741-7007-3-20/final/activity_toxicity_evidence.json)
- [final/database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_1741-7007-3-20/final/database_record_verification.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_1741-7007-3-20/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1186_1741-7007-3-20/rework/rework_responses.jsonl)

Gate results:
- Semantic gate rerun: failed expectedly, `issue_count=3`: `review_status_not_publication_grade`, `publication_grade_not_true`, `missing_activity_records`.
- Publication QA rerun: `publication_grade_pass=false`, open rework risk present.
- JSON/JSONL validation: `53` files checked, `0` syntax errors.
- Message bus validation: `ok=true`.

Open targeted tickets now remain for worker-2, worker-4, and worker-6, with `unrecoverable_material_gaps` documenting the local source exhaustion. The packet/report state is `analysis_blocked_unrecoverable_material_gaps` / `blocked_missing_primary_material`.

