Re-reviewed only `doi__10.1128_jvi.00635-20` and did not rerun the initial bootstrap/workflow.

Updated the worker-4/worker-6 layer artifacts:
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_jvi.00635-20/final/database_record_verification.json): 171 database audits, `source_verified=88`, `source_conflict=83`.
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_jvi.00635-20/final/activity_toxicity_evidence.json): corrected final activity to 36 true Table 1 IC50 rows; removed parser rows that treated helix/Tm values as activity.
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_jvi.00635-20/final/mechanism_ontology_record.json): replaced placeholder mechanism notes with source-reviewed fusion/HR1-HR2/cholesterol-conjugation claims.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_jvi.00635-20/final/review_report.json): final status is `accepted_with_cautions`, not clean acceptance.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_jvi.00635-20/work/review/quality_feedback.json): `issue_count=0`, no open rework targets.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1128_jvi.00635-20/rework/rework_responses.jsonl): closed `rwk-complete-test-0001`.

Preserved cautions include DRAMP modification metadata conflicts, CAMP generic entry/assay-label conflicts, DBAASP IPB05 VSV value conflict, no primary-source toxicity/hemolysis values, and the activity parser correction.

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication quality gate: `publication_grade_pass=true`, `risk_counts={}`.
- Complete report updated: [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1128_jvi.00635-20.complete_message_test_report.json).

