Done. I re-reviewed `doi__10.7150_thno.40971` without rerunning the initial bootstrap and repaired only worker-2/4/6-owned layers.

Updated core artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.7150_thno.40971/final/activity_toxicity_evidence.json)
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.7150_thno.40971/final/database_record_verification.json)
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.7150_thno.40971/final/review_report.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.7150_thno.40971/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.7150_thno.40971/rework/rework_responses.jsonl)

Result: `accepted_with_cautions`, `publication_grade: true`, `open_rework_targets: 0`, `qc_failure_reasons: 0`. Worker-2 now has 8 source-located activity/toxicity records. Worker-4 preserves 2 `source_conflict` DRAMP cautions and 1 `source_verified` literature row. No `unrecoverable_material_gaps` were needed.

Validation:
- Semantic gate: `issue_count=0`, `publication_grade_pass_count=1`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- Complete report now shows `terminal_status=accepted_with_cautions`

