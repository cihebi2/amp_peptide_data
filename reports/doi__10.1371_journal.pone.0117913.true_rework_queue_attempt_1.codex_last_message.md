Completed the bounded worker-2/4/6 re-review for `doi__10.1371_journal.pone.0117913`.

Repaired artifacts:
- Rebuilt worker-2 activity/toxicity evidence: 86 source-supported rows from XML/PDF Table 2, Table 3, Table 4, and exact Results prose.
- Rebuilt worker-4 database audit: 152 linked rows, `source_verified=76`, `source_conflict=76`, with conflicts preserved instead of flattened.
- Rebuilt worker-6 final adjudication: `review_status=accepted_with_cautions`, `publication_grade=true`, `rework_targets=[]`, `qc_failure_reasons=[]`.
- Updated [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0117913/rework/rework_responses.jsonl) closing `rwk-complete-test-0001`.
- Added reproducible repair script: [repair_doi_10_1371_journal_pone_0117913_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1371_journal_pone_0117913_worker246.py).

Key status:
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0117913/final/review_report.json): accepted with cautions, no open rework.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0117913/work/review/quality_feedback.json): `issue_count=0`.
- Packet manifest now has `open_rework_ticket_ids=[]`, `closed_rework_ticket_ids=["rwk-complete-test-0001"]`.

Verification:
- Semantic gate: `publication_grade_pass_count=1`, `fail_count=0`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`.
- Canonical reports updated:
  - [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0117913.semantic_gate.json)
  - [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0117913.publication_quality.json)

Cautions preserved: database-only/label-mismatched rows remain `source_conflict`; landed “supplementary” files were HTML/landing pages rather than true supplementary tables; full figure curve series were not digitized, and no figure-only values were fabricated.

