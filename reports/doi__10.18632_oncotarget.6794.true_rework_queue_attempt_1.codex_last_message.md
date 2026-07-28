Completed the bounded re-review for `doi__10.18632_oncotarget.6794` and left it non-accepted.

Updated:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.6794/final/activity_toxicity_evidence.json): 57 activity/toxicity rows preserved with source locators and explicit source-conflict limits.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.6794/final/database_record_verification.json): 173 linked DB rows audited; 150 `source_conflict`, 23 `source_verified`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.6794/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.6794/work/review/quality_feedback.json): status is `blocked_missing_primary_material`.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.18632_oncotarget.6794/rework/rework_responses.jsonl): appended the worker-2/4/6 response.

Created/kept open tickets:
- `rwk-complete-test-0001`
- `rwk-oncotarget-6794-worker2-figure-exact-values-unrecoverable`
- `rwk-oncotarget-6794-worker4-database-activity-source-conflict`

Gate results after repair:
- Semantic gate: failed as expected, only `review_status_not_publication_grade` and `publication_grade_not_true`.
- Publication QA: failed as expected, `open_rework_targets: 2`.
- JSON/JSONL validation passed.

Main blocker: local material supports assay context and database-row preservation, but not exact graph-derived activity percentages as primary-source text/table/source-data values.

