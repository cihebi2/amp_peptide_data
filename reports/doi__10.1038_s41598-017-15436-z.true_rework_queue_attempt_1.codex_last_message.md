Re-review completed for `doi__10.1038_s41598-017-15436-z`.

I repaired the worker-4/worker-6 layers and left the paper non-accepted. Final state is `review_status=blocked_missing_primary_material`, `publication_grade=false`.

Key updates:
- Worker-4 database audit rebuilt: [database_record_audit.json](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-017-15436-z/analysis/database_record_audit.json)
- Worker-6 final review/feedback rebuilt: [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-15436-z/final/review_report.json), [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-15436-z/work/review/quality_feedback.json)
- Rework response appended: [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-017-15436-z/rework/rework_responses.jsonl)
- Targeted open tickets now preserved:
  - `rwk-worker46-20260504-supplement-doc-unrecoverable`
  - `rwk-worker46-20260504-database-sequence-dbamp-conflict`

Remaining blockers recorded as `unrecoverable_material_gaps`:
- `supplementary_dataset_1_doc_not_locally_recoverable`
- `exact_peptide_sequence_not_in_primary_or_linked_sequence_snapshot`

Gate evidence:
- Semantic gate rerun: `publication_grade_pass_count=0`, `issue_count=2`, only review-layer non-acceptance issues remain.
- Publication QA rerun: `publication_grade_pass=false`, `open_rework_targets=1`.
- JSON validation passed for repaired artifacts and reports.

I also added the reproducible repair script at [repair_doi_10_1038_s41598_017_15436_z_worker46.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1038_s41598_017_15436_z_worker46.py). `git status` could not run because this directory is not a git repository.

