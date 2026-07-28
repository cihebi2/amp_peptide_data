Completed the one-paper re-review for `doi__10.1016_j.isci.2020.101785`.

I repaired the worker-2/4/6 artifacts by rebuilding six source-supported MIC rows from Document S1 Table S5, reconciling linked DBAASP/DRAMP rows with cautions instead of fabricating unsupported values, and updating final adjudication to `accepted_with_cautions`.

Key updated artifacts:
- [final activity](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1016_j.isci.2020.101785/final/activity_toxicity_evidence.json)
- [final database](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1016_j.isci.2020.101785/final/database_record_verification.json)
- [final review](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1016_j.isci.2020.101785/final/review_report.json)
- [quality feedback](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1016_j.isci.2020.101785/work/review/quality_feedback.json)
- [rework responses](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1016_j.isci.2020.101785/rework/rework_responses.jsonl)

Validation passed:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`
- Message bus validate: `ok=true`
- Open rework tickets: `[]`; `rwk-complete-test-0001` closed

Reports written:
- [semantic gate](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1016_j.isci.2020.101785.semantic_gate.json)
- [publication quality](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1016_j.isci.2020.101785.publication_quality.json)

Remaining status is `accepted_with_cautions`, not `accepted_clean`: database-only rows without exact source values, broad DRAMP labels, and figure-only heatmap quantification are preserved as cautions rather than promoted into fabricated activity rows.

