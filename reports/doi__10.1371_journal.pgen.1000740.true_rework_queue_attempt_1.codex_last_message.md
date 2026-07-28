Re-reviewed `doi__10.1371_journal.pgen.1000740` and left it non-accepted.

I repaired the worker-2/4/6 artifacts to reflect the source-reviewed result: local XML/PDF/OA package, figure captions, Word supplements, landing assets, and linked database rows do not support primary AMP activity/toxicity rows. DRAMP/dbAMP rows are preserved as `source_conflict` / `database_only_no_primary_source`, with citation-only verification separated from sequence/activity support.

Updated key artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pgen.1000740/final/activity_toxicity_evidence.json)
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pgen.1000740/final/database_record_verification.json)
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pgen.1000740/final/review_report.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pgen.1000740/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pgen.1000740/rework/rework_responses.jsonl)

Final state:
- `review_status=blocked_missing_primary_material`
- `publication_grade=false`
- `unrecoverable_material_gaps`: `primary_activity_toxicity_rows_absent`, `database_sequence_activity_primary_support_absent`, `primary_amp_mechanism_absent`
- Open targeted tickets: worker-2, worker-4, worker-6

Validation:
- JSON validation passed for edited JSON artifacts.
- JSONL validation passed: `rework_requests.jsonl` has 2 valid rows, `rework_responses.jsonl` has 1 valid row.
- Semantic gate rerun: failed as expected, `issue_count=3`: `review_status_not_publication_grade`, `publication_grade_not_true`, `missing_activity_records`.
- Publication QA rerun: failed as expected, `publication_grade_pass=false`, `open_rework_targets=3`.

No git diff/status is available because this cwd is not a git repository.

