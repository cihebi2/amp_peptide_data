Re-review completed for `doi__10.1038_s41598-017-11396-6`. I loaded the worker-4 and worker-6 skills, reopened the paper-local packet/source/database artifacts, and did not mark the paper accepted.

Repaired outputs include:
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-11396-6/final/database_record_verification.json): 42 linked rows reviewed, now `source_verified=20`, `source_conflict=22`.
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-11396-6/final/activity_toxicity_evidence.json): 21 activity rows and 10 toxicity rows retained from local XML/main-text evidence.
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-11396-6/final/mechanism_ontology_record.json): replaced automated placeholders with 3 source-located direct-assay mechanism claims.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-11396-6/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-11396-6/work/review/quality_feedback.json): set `review_status=blocked_missing_primary_material`, `publication_grade=false`.

The original `rwk-complete-test-0001` is answered in [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-017-11396-6/rework/rework_responses.jsonl). I added/kept one targeted open material ticket in [rework_requests.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-017-11396-6/rework/rework_requests.jsonl): `rwk-worker46-20260504-supplementary-pdf-missing`.

Validation:
- `jq empty` passed for repaired JSON/report files.
- Semantic gate rerun: `issue_count=2`, only `review_status_not_publication_grade` and `publication_grade_not_true`.
- Publication gate rerun: `publication_grade_pass=false`, `open_rework_targets=1`.

The remaining blocker is explicit: local assets contain XML/PDF plus supplementary landing HTML `.bin` files, but not the actual `41598_2017_11396_MOESM1_ESM.pdf`; exact supplementary table/figure extraction is therefore unrecoverable from local material.

