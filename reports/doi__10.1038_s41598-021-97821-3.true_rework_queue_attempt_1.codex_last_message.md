Done. Repaired the worker-4/worker-6 layers for `doi__10.1038_s41598-021-97821-3`.

Key state now:
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-021-97821-3/final/review_report.json): `review_status=accepted_with_cautions`, `publication_grade=true`, `rework_targets=[]`
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-021-97821-3/work/review/quality_feedback.json): `issue_count=0`, no QC failures, no unrecoverable gaps
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-021-97821-3/final/database_record_verification.json): all 162 linked rows reviewed; `source_verified=122`, `source_conflict=40`
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-021-97821-3/rework/rework_responses.jsonl): ticket `rwk-complete-test-0001` closed as `resolved_accepted_with_cautions`

Validation:
- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-021-97821-3.semantic_gate.json): pass `1/1`, `issues=[]`
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-021-97821-3.publication_quality.json): `publication_grade_pass=true`, `risk_counts={}`
- [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-021-97821-3.complete_message_test_report.json): `terminal_status=accepted_with_cautions`, `open_rework_ticket_count=0`

Remaining cautions are preserved, not hidden: database toxicity label conflicts, CAMP/dbAMP aggregate unit/context ambiguity, missing linked sequence snapshot, and local “supplementary” `.bin` assets being HTML landing pages rather than recoverable supplement tables.

