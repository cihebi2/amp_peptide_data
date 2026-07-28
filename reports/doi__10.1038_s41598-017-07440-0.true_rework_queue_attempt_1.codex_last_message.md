Re-review complete for `doi__10.1038_s41598-017-07440-0`.

I repaired the worker-2/4/6 layers and closed `rwk-complete-test-0001` with `accepted_with_cautions`, not clean acceptance. The open blocker is cleared: `quality_feedback.json` now has `issue_count: 0`, `rework_targets: []`, and the response log has one closure entry.

Key updated artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-07440-0/final/activity_toxicity_evidence.json): 476 source-located rows, including repaired Table 3/4 MIC matrices.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-07440-0/final/database_record_verification.json): 315 linked DB rows adjudicated, with conflicts/database-only values preserved.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-07440-0/final/review_report.json): `accepted_with_cautions`, `publication_grade: true`, no open rework targets.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-017-07440-0/rework/rework_responses.jsonl): closure response appended.

Remaining cautions are explicitly recorded, not hidden: exact MBEC50 values remain `database_only_no_primary_source`, two mixed dbAMP rows remain `source_conflict`, and local supplementary assets were landing HTML rather than structured supplementary PDF/XLSX tables.

Verification:
- Semantic gate: pass `1/1`, `issue_count: 0` in [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-07440-0.semantic_gate.json).
- Publication QA: `publication_grade_pass: true`, `risk_counts: {}` in [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-07440-0.publication_quality.json).
- JSON validity check passed for all updated paper-local packet/final/work/report JSON files.

