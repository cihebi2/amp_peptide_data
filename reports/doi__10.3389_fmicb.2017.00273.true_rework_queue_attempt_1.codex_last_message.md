Re-reviewed `doi__10.3389_fmicb.2017.00273` without rerunning bootstrap.

Updated the worker-2/4/6 artifacts and closed `rwk-complete-test-0001`:
- Recovered `6` activity/toxicity rows: `4` MBC + `2` hemolysis.
- Reconciled `9` linked DBAASP/database rows as `source_verified`.
- Rewrote worker-6 review as `accepted_with_cautions`, with no open rework targets.
- Recorded nonblocking material gaps for un-tabulated figure curve points, absent linked sequence snapshot, and supplementary captures with no structured assay tables.

Key paths updated include:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2017.00273/final/activity_toxicity_evidence.json)
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2017.00273/final/database_record_verification.json)
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2017.00273/final/review_report.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2017.00273/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.3389_fmicb.2017.00273/rework/rework_responses.jsonl)
- [workflow_context.json](/root/work/抗菌肽/数据库/batch/4-team/.miaobi-paper-review/workflows/doi__10.3389_fmicb.2017.00273/workflow_context.json)

Validation:
- Semantic gate: `publication_grade_pass=1/1`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- JSON sanity check passed on updated artifacts.
- Workspace is not a git repository, so there is no git diff/status.

I also added the reproducible repair script: [repair_doi_10_3389_fmicb_2017_00273_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_3389_fmicb_2017_00273_worker246.py).

