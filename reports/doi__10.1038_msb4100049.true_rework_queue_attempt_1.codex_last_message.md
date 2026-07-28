Re-reviewed `doi__10.1038_msb4100049` and left it **non-accepted**.

Result: `blocked_missing_primary_material`, `publication_grade=false`, with open targeted ticket `rwk-codex-rereview-20260502-0001`. Bounded source recovery found no local primary AMP activity/toxicity rows, so I did not fabricate activity records.

Updated key artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_msb4100049/final/activity_toxicity_evidence.json): 0 records, unrecoverable local-material gap recorded.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_msb4100049/final/database_record_verification.json): 8 audits, preserving `6 source_conflict`, `1 database_only_no_primary_source`, `1 source_verified` citation link.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_msb4100049/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_msb4100049/work/review/quality_feedback.json): concrete QC reasons and `unrecoverable_material_gaps`.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_msb4100049/rework/rework_responses.jsonl): response appended; old ticket superseded by the targeted gap ticket.

Gate evidence:
- Semantic gate: failed as intended, `issue_count=3`: `review_status_not_publication_grade`, `publication_grade_not_true`, `missing_activity_records`.
- Publication QA: failed as intended, `open_rework_targets=1`.
- Message bus validation passed. JSON/JSONL validation passed.
- `git status` could not run because this directory is not a git repository.

