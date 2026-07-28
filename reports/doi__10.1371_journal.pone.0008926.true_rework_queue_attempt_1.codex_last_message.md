Done. Re-reviewed `doi__10.1371_journal.pone.0008926` and left it non-accepted.

Updated the owned layers and control artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0008926/final/activity_toxicity_evidence.json): 3 source-supported PeiR rows retained; unsupported Cas2/database-only AMP claims not promoted.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0008926/final/database_record_verification.json): `source_conflict=6`, `database_only_no_primary_source=1`, `source_verified=1`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0008926/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0008926/work/review/quality_feedback.json): `review_status=blocked_missing_primary_material`, `publication_grade=false`, 3 `unrecoverable_material_gaps`.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0008926/rework/rework_responses.jsonl) and [rework_requests.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0008926/rework/rework_requests.jsonl): ticket `rwk-complete-test-0001` kept open as `open_blocked_unrecoverable_local_gap` with owner workers, omission code, artifact path, and source paths.

Gate evidence:
- Semantic gate rerun: failed expectedly with `review_status_not_publication_grade` and `publication_grade_not_true`; no `missing_activity_records`.
- Publication quality gate rerun: `publication_grade_pass=false`, `activity_records=3`, `mechanism_claims=3`, `open_rework_targets=1`.

All touched JSON/JSONL artifacts validate with `jq`.

