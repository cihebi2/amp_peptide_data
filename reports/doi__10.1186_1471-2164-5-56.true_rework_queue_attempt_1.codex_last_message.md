Re-review completed for `doi__10.1186_1471-2164-5-56` only.

I left the paper non-accepted: `review_status=blocked_missing_primary_material`, `publication_grade=false`. The local XML/PDF/OA package/supplement landing assets/database rows do not support primary activity/toxicity assay rows, so I recorded an `unrecoverable_material_gaps` entry instead of fabricating rows.

Changed/updated:
- [final activity](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_1471-2164-5-56/final/activity_toxicity_evidence.json): `activity_records=0`, source-exhausted gap recorded.
- [final database](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_1471-2164-5-56/final/database_record_verification.json): 95 rows preserved as `source_conflict=76`, `database_only_no_primary_source=10`, `source_verified=9`.
- [final review](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_1471-2164-5-56/final/review_report.json): worker-6 adjudication set to blocked, with targeted rework.
- [quality feedback](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_1471-2164-5-56/work/review/quality_feedback.json): concrete QC reasons and unrecoverable gap recorded.
- [rework responses](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1186_1471-2164-5-56/rework/rework_responses.jsonl): response appended.
- [rework requests](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1186_1471-2164-5-56/rework/rework_requests.jsonl): targeted ticket `rwk-codex-worker246-20260503-001` kept open.

Validation:
- Semantic gate rerun: `0/1` pass, 3 hard issues: `review_status_not_publication_grade`, `publication_grade_not_true`, `missing_activity_records`.
- Publication QA rerun: `publication_grade_pass=false`, `open_rework_targets=1`.
- Edited JSON artifacts parse cleanly.
- No final/packet review artifact is marked accepted.

