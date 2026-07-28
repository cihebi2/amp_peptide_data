Re-reviewed `doi__10.3389_fphar.2021.731056` and repaired the worker-4/worker-6 layer artifacts.

Key outcomes:
- `review_status`: `accepted_with_cautions`
- `publication_grade`: `true`
- `quality_feedback.issue_count`: `0`
- `rework_targets`: `0`
- `rwk-complete-test-0001`: closed via [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.3389_fphar.2021.731056/rework/rework_responses.jsonl)
- No blocking `unrecoverable_material_gaps`

Main repaired artifacts:
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fphar.2021.731056/final/database_record_verification.json): 40 linked rows reviewed, `28 source_verified`, `12 source_conflict` preserved as cautions.
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fphar.2021.731056/final/activity_toxicity_evidence.json): 14 source-reviewed FM-CATH activity/toxicity records.
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fphar.2021.731056/final/mechanism_ontology_record.json): 4 bounded mechanism claims.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fphar.2021.731056/final/review_report.json): final worker-6 adjudication with cautions and closed-ticket status.

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication-quality gate: `publication_grade_pass=true`, `risk_counts={}`
- Reports updated at:
  - [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.3389_fphar.2021.731056.semantic_gate.json)
  - [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.3389_fphar.2021.731056.publication_quality.json)

I also aligned status-only metadata in the packet manifest and complete-message report so they no longer advertise the stale open ticket.

