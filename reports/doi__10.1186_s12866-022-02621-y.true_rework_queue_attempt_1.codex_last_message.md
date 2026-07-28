Re-review completed for `doi__10.1186_s12866-022-02621-y`. I did not rerun the initial bootstrap/workflow.

Updated the owned layers and kept the paper non-accepted:
- Added 4 source-supported activity/toxicity rows in [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_s12866-022-02621-y/final/activity_toxicity_evidence.json).
- Re-adjudicated 21 DBAASP-linked rows in [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_s12866-022-02621-y/final/database_record_verification.json): `source_verified=7`, `database_only_no_primary_source=14`.
- Rewrote worker-6 review/adjudication with `blocked_missing_primary_material` in [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_s12866-022-02621-y/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_s12866-022-02621-y/work/review/quality_feedback.json).
- Appended the rework response and narrowed the remaining blocker to `rwk-local-source-gap-ll1-supplement-20260503` in [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1186_s12866-022-02621-y/rework/rework_responses.jsonl) and [rework_requests.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1186_s12866-022-02621-y/rework/rework_requests.jsonl).

Remaining blocker: local materials do not contain the MOESM1/MOESM2 TIF payloads or MOESM3 DOCX Table S1 payload. I recorded this as `unrecoverable_material_gaps`; unsupported non-E. coli MIC values remain database-only, not fabricated as primary-source rows.

Validation:
- JSON/JSONL integrity: passed.
- Semantic gate rerun: failed only on expected non-publication-grade review status: `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication QA rerun: failed as expected with `open_rework_targets=1`.

