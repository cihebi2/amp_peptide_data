Completed the one-paper re-review for `doi__10.3389_fmicb.2017.00994` without rerunning the initial bootstrap.

I repaired worker-2/4/6 layers and closed `rwk-complete-test-0001` only after gates passed. Final state is `accepted_with_cautions`, not clean acceptance.

Key results:
- Activity/toxicity repaired: 52 source-reviewed rows in [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2017.00994/final/activity_toxicity_evidence.json)
- Database adjudication repaired: 77 audits, preserving `source_conflict=14` and `sequence_modified_not_normalized=2` in [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2017.00994/final/database_record_verification.json)
- Worker-6 review updated: [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2017.00994/final/review_report.json)
- QC feedback now has `issue_count=0`, `rework_targets=[]`: [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2017.00994/work/review/quality_feedback.json)
- Rework response appended: [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.3389_fmicb.2017.00994/rework/rework_responses.jsonl)

Validation:
- Semantic gate: `pass_count=1`, `fail_count=0`, `issue_count=0`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- Reports: [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.3389_fmicb.2017.00994.semantic_gate.json), [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.3389_fmicb.2017.00994.publication_quality.json)
- JSON sanity checks passed on repaired packet/final/work artifacts.

Remaining cautions are explicitly preserved: retro-inverso sequence normalization, database rows whose exact thresholds are not printed as primary figure labels, nonlocal aggregate database claims, HTML-only supplementary landing assets, and unresolved molecular mode of action.

