Re-review complete for `doi__10.1002_cbic.202100609`.

I kept the paper non-accepted: `review_status=needs_targeted_rework`, `publication_grade=false`. Table S5 remains repaired/structured, but Figure 4 exact HEK293/HepG2 cytotoxicity percentages are still not recoverable from local XML/PDF text/caption/image/supplement/database materials, so the database cytotoxicity rows remain `source_conflict`.

Updated artifacts:
- [final review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1002_cbic.202100609/final/review_report.json)
- [packet final review_report.json](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1002_cbic.202100609/final/review_report.json)
- [packet adjudication_report.json](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1002_cbic.202100609/analysis/adjudication_report.json)
- [analysis_status.json](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1002_cbic.202100609/analysis/analysis_status.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1002_cbic.202100609/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1002_cbic.202100609/rework/rework_responses.jsonl)

Message bus now has only the active ticket open:
`rwk-cbic202100609-figure4-exact-cytotoxicity-unrecoverable-0003`.
The two superseded tickets were closed in workflow context.

Verification:
- Semantic gate rerun: failed as expected with 2 review-layer issues: `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication gate rerun: failed as expected with `open_rework_targets=1`.
- Message bus validation passed.
- Edited JSON files parse cleanly.

New gate reports:
- [semantic gate](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1002_cbic.202100609.single_paper_re_review_20260501T013012Z.semantic_gate.json)
- [publication quality](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1002_cbic.202100609.single_paper_re_review_20260501T013012Z.publication_quality.json)

