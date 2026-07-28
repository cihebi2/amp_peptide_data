Re-reviewed `doi__10.1128_msystems.01358-23` and repaired the worker-2/4/6 layers.

What changed:
- Replaced the bogus Table 1 classifier-metric “MIC” rows with 45 source-backed Table 2 activity/toxicity rows in [final/activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_msystems.01358-23/final/activity_toxicity_evidence.json).
- Reconciled 105 linked APD6/DBAASP rows in [final/database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_msystems.01358-23/final/database_record_verification.json): `source_verified=98`, `source_conflict=7`.
- Closed `rwk-complete-test-0001` via [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1128_msystems.01358-23/rework/rework_responses.jsonl).
- Cleared stale QC failures in [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_msystems.01358-23/work/review/quality_feedback.json).

Remaining cautions are nonblocking: one DBAASP peptide-4 E. coli MIC conflict is preserved, APD6-only free-text annotations are not promoted to source facts, and mechanism evidence is indirect only.

Verification:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- Updated report: [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1128_msystems.01358-23.complete_message_test_report.json)

