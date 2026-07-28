Re-reviewed `doi__10.1021_cb500340w` without rerunning the initial bootstrap.

Updated owner-layer artifacts under:

- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1021_cb500340w/final/activity_toxicity_evidence.json): 118 source-located activity/binding records recovered.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1021_cb500340w/final/database_record_verification.json): 26 DRAMP rows preserved as `source_conflict`, 13 literature rows `source_verified`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1021_cb500340w/final/review_report.json): now `accepted_with_cautions`, `publication_grade: true`, no open rework targets.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1021_cb500340w/work/review/quality_feedback.json): `issue_count: 0`, no QC failure reasons.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1021_cb500340w/rework/rework_responses.jsonl): resolved `rwk-complete-test-0001`.

Remaining caution is preserved, not hidden: DRAMP’s antimicrobial label is unsupported by the primary paper and stays as `source_conflict`; the supported local evidence is Mcl-1/Bcl-2 binding and BH3-profiling depolarization.

Validation passed:

- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication-quality gate: `publication_grade_pass=true`, `risk_counts={}`.
- Message bus validate: `ok=true`.
- Workflow now has `open_rework_tickets: []` and `final_approval` completed.