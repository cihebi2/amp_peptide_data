Completed the bounded re-review for `doi__10.1038_s41467-023-37003-z`. I did not mark it accepted.

Updated the owner-layer artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41467-023-37003-z/final/activity_toxicity_evidence.json): recovered `29` source-supported rows from XML/PDF/table/figure captions.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41467-023-37003-z/final/database_record_verification.json): audited `55` linked DBAASP rows, `21 source_verified`, `34 source_conflict`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41467-023-37003-z/final/review_report.json): set `review_status=blocked_missing_primary_material`, `publication_grade=false`.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41467-023-37003-z/work/review/quality_feedback.json): records `3` blocking QC reasons and `2` `unrecoverable_material_gaps`.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41467-023-37003-z/rework/rework_responses.jsonl): appended the bounded-repair response; ticket `rwk-complete-test-0001` remains open as blocked/unrecoverable.

Gate results:
- Semantic gate: `publication_grade_pass_count=0/1`, `issue_count=2`; only review-level blockers remain.
- Publication QA: `publication_grade_pass=false`, `risk_counts={"open_rework_targets": 1}`.
- Message bus validation: `ok=true`.

The blocker is concrete: local supplementary assets are HTML landing captures, not the actual MOESM PDF/XLSX source-data files, so the full peptide/pathogen source-data matrix cannot be recovered locally under obtainable-only mode.

