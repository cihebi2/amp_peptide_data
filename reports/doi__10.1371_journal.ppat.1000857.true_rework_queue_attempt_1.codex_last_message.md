Completed the re-review for `doi__10.1371_journal.ppat.1000857`.

What changed:
- Rebuilt worker-2 activity evidence with `25` source-backed GKY25 MIC rows from local OA-package supplement material.
- Rebuilt worker-4 database adjudication: `44` linked rows, now `29 source_verified` and `15 source_conflict`, preserving toxicity/DRAMP/database-only conflicts as cautions.
- Rebuilt worker-6 final review as `accepted_with_cautions`, not `accepted_clean`.
- Closed `rwk-complete-test-0001` in `rework_responses.jsonl` and workflow context.
- Updated `quality_feedback.json` to `issue_count: 0`, no open rework targets, no unrecoverable gaps.

Key files:
- [repair script](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1371_journal_ppat_1000857_worker246.py)
- [activity evidence](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.ppat.1000857/final/activity_toxicity_evidence.json)
- [database verification](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.ppat.1000857/final/database_record_verification.json)
- [review report](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.ppat.1000857/final/review_report.json)
- [rework response](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.ppat.1000857/rework/rework_responses.jsonl)

Validation:
- Semantic gate: `pass_count=1`, `fail_count=0`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`, `activity_records=25`.
- Message bus validate: `ok=true`.
- Workflow context now has `open_rework_tickets=[]` and all four readiness gates true.

I used memory only to confirm the Batch 4 local contract/message-bus baseline; source and artifact evidence was reopened from disk for this paper.

