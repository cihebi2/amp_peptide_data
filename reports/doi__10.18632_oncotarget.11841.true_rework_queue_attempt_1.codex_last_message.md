Re-reviewed `doi__10.18632_oncotarget.11841` and repaired the owned worker-2/4/6 layers.

Changed key artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.11841/final/activity_toxicity_evidence.json): 92 source-located Table 1 activity rows, 98 ND entries preserved separately, 1 qualitative toxicity row.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.11841/final/database_record_verification.json): 14 linked rows adjudicated: `source_verified=9`, `source_conflict=4`, `database_only_no_primary_source=1`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.11841/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.11841/work/review/quality_feedback.json): ticket `rwk-complete-test-0001` closed, `issue_count=0`, no `rework_targets`, no `unrecoverable_material_gaps`.

I preserved the unsupported exact database IC50 values as `source_conflict`, and the CAMP antimicrobial row as `database_only_no_primary_source`; they are explicit nonblocking cautions, not fabricated primary-source values.

Verification:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`.
- Complete report now shows `terminal_status=accepted_with_cautions`, open rework tickets `0`.
- `git status` could not run because this cwd is not a git repository.

