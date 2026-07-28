Re-review completed for `doi__10.1371_journal.pone.0110809`.

I repaired the worker-2/4/6 artifacts and left the paper non-accepted. The key finding is that the staged DOI assets resolve to a non-Muscin PLOS ONE bioconversion paper, while the AMP database rows describe Muscin. I preserved APD6/DBAASP/DRAMP values as database-only/source-conflict evidence and did not promote them into primary-source activity rows.

Updated main artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0110809/final/activity_toxicity_evidence.json)
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0110809/final/database_record_verification.json)
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0110809/final/mechanism_ontology_record.json)
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0110809/final/review_report.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0110809/work/review/quality_feedback.json)
- `paper_packets/.../rework/rework_requests.jsonl` now has 2 tickets.
- `paper_packets/.../rework/rework_responses.jsonl` now has the bounded-attempt response.

Status after repair:
- `review_status`: `blocked_missing_primary_material`
- `publication_grade`: `false`
- activity primary rows: `0`
- database statuses: `source_conflict=2`, `database_only_no_primary_source=1`, `source_verified=0`
- unrecoverable gap: `primary_muscin_source_not_locally_recovered`

Verification:
- `py_compile` passed for the repair script.
- `jq empty` passed on updated JSON artifacts and reports.
- Semantic gate rerun: failed as expected with `review_status_not_publication_grade`, `publication_grade_not_true`, `missing_activity_records`.
- Publication QA rerun: failed as expected with `open_rework_targets=1`.
- `git status` could not run because this directory is not a git repository.

