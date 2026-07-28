Re-reviewed `doi__10.1038_s41598-022-08247-4` and repaired the owned worker-2/4/6 layers.

Key results:
- Worker-2 activity/toxicity evidence now has `106` rows: `42` Table 3 MIC rows, `12` Table 5 MBEC rows, and `4` MHC toxicity rows.
- Worker-4 database audit now has `103` rows: `96 source_verified`, `7 source_conflict`.
- Worker-6 final review is now `accepted_with_cautions`, `publication_grade=true`, `rework_targets=[]`.
- `quality_feedback.json` is now `issue_count=0`.
- Appended a closing response for `rwk-complete-test-0001` in `rework_responses.jsonl`.

Gate evidence:
- Semantic gate: `issue_count=0`, `publication_grade_pass_count=1`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`.
- Reports updated:
  - [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-022-08247-4.semantic_gate.json)
  - [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-022-08247-4.publication_quality.json)
  - [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-022-08247-4.complete_message_test_report.json)

Remaining caution, not blocker: exact RAW264.7 killing percentages in database rows are graph-only locally, so they are preserved as `source_conflict` instead of fabricated as primary table values.

