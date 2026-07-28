Re-reviewed `doi__10.1038_s41598-018-20912-1` and repaired the owned worker-2/4/6 layers.

Updated the activity matrix to 49 source-located rows, including the previously blocked Table 3 MBEC, Table 4 hemolysis, and Table 7 H5(61-90) MIC records. Re-adjudicated database rows with conflict preservation: 83 `source_verified`, 43 `source_conflict`. Closed `rwk-complete-test-0001` in `rework_responses.jsonl`, cleared `quality_feedback.json`, and set the final review to `accepted_with_cautions`, not clean acceptance.

Validation passed:
- Semantic gate: `issue_count=0`, `publication_grade_fail_count=0`
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`
- Mirrored packet/final artifacts compare identical for activity, database, mechanism, and review files
- JSONL rework files parse cleanly

Key updated paths include:
- `/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-018-20912-1/analysis/activity_toxicity_evidence.json`
- `/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-018-20912-1/analysis/database_record_audit.json`
- `/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-018-20912-1/final/review_report.json`
- `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-018-20912-1.semantic_gate.json`
- `/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-018-20912-1.publication_quality.json`

Remaining cautions are preserved, not blockers: full-length H5 exact sequence is not primary-source verified, VRE species naming is database-over-specific, and the supplement surface is methods-only/no extra result table.

