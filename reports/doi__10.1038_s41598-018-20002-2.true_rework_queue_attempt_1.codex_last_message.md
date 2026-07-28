Re-reviewed and repaired `doi__10.1038_s41598-018-20002-2` for worker-2/4/6 only.

Key results:
- Worker-2 activity evidence rebuilt to `43` source-backed rows, including repaired Table 2 `N. crassa` germination/germ-tube rows.
- Worker-4 database audit rebuilt to `55` rows: `52 source_verified`, `3 source_conflict`, preserving the PAFB Candida killing mismatch.
- Worker-6 final review is now `accepted_with_cautions`, `publication_grade: true`, with `rework_targets: []`.
- Rework response appended to [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-018-20002-2/rework/rework_responses.jsonl).
- Nonblocking `unrecoverable_material_gaps` recorded for missing local supplementary PDF and absent linked sequence snapshot rows.

Primary updated artifacts include:
[activity](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-018-20002-2/final/activity_toxicity_evidence.json), [database](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-018-20002-2/final/database_record_verification.json), [review](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-018-20002-2/final/review_report.json), and [quality_feedback](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-018-20002-2/work/review/quality_feedback.json).

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`.
- Reports updated at [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-018-20002-2.semantic_gate.json) and [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-018-20002-2.publication_quality.json).

Note: this directory is not a git repository, so there is no git diff/status summary available.

