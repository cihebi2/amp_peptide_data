Re-reviewed `doi__10.1371_journal.pone.0061614` without rerunning bootstrap.

Updated the worker-2/4/6 artifacts. Key results:
- Activity/toxicity: 294 source-located rows from Tables 2-4 in [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0061614/final/activity_toxicity_evidence.json).
- Database audit: 311 linked rows adjudicated in [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0061614/final/database_record_verification.json): `source_verified=246`, `source_conflict=62`, `database_only_no_primary_source=3`.
- Worker-6 review: [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0061614/final/review_report.json) is now `accepted_with_cautions`, `publication_grade: true`, with no open `rework_targets`.
- Rework response: closed `rwk-complete-test-0001` in [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0061614/rework/rework_responses.jsonl).
- QC feedback: [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0061614/work/review/quality_feedback.json) now has `issue_count: 0`.

Validation passed:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0` in [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0061614.semantic_gate.json).
- Publication QA: `publication_grade_pass=true`, `risk_counts={}` in [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0061614.publication_quality.json).

No `unrecoverable_material_gaps` remain for the requested worker-2/4/6 repair scope.

