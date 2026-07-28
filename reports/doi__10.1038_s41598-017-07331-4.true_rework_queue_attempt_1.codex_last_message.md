Re-reviewed and repaired `doi__10.1038_s41598-017-07331-4` for worker-2/4/6.

Updated the paper-local artifacts, including [final activity](</root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-07331-4/final/activity_toxicity_evidence.json>), [final database audit](</root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-07331-4/final/database_record_verification.json>), [final review](</root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-07331-4/final/review_report.json>), [quality feedback](</root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-07331-4/work/review/quality_feedback.json>), packet analysis/final mirrors, and [rework responses](</root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-017-07331-4/rework/rework_responses.jsonl>). I also added the reproducible repair script at [repair_doi_10_1038_s41598_017_07331_4_worker246.py](</root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1038_s41598_017_07331_4_worker246.py>).

Result:
- `review_status`: `accepted_with_cautions`
- `publication_grade`: `true`
- open rework tickets: `0`
- activity rows: `9` source-supported MIC rows
- database rows audited: `60` total, with `18 source_verified`, `2 source_conflict`, `40 database_only_no_primary_source`
- `quality_feedback.issue_count`: `0`
- nonblocking unrecoverable gap recorded: local supplementary assets are HTML landing pages, not the XML-referenced supplement PDF

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`, `activity_records=9`, `mechanism_claims=1`

Reports updated at [semantic gate](</root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-07331-4.semantic_gate.json>) and [publication quality](</root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-07331-4.publication_quality.json>).

