Re-reviewed `doi__10.1038_srep32121` and kept the result at `accepted_with_cautions`, not clean acceptance.

Changed the active packet/final state to remove stale open-ticket markers and preserve only caution-level issues:
- [packet_manifest.json](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_srep32121/packet_manifest.json): `open_rework_ticket_ids: []`, resolved `rwk-complete-test-0001`, no blocking missing materials.
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_srep32121/final/activity_toxicity_evidence.json): tightened HepG2 toxicity wording to preserve the `23.5 uM` methods vs `24.3 uM` supplement-caption mismatch and figure-only exact values.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_srep32121/final/review_report.json): source-reviewed worker-6 adjudication remains `publication_grade: true`, `accepted_with_cautions`, no rework targets.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_srep32121/work/review/quality_feedback.json): `issue_count: 0`, no QC failures, caution list retained.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_srep32121/rework/rework_responses.jsonl): appended a fresh re-review response with checked paths, tools, remaining cautions, and gate results.

Verification:
- Semantic gate rerun: `publication_grade_pass_count=1`, `publication_grade_fail_count=0`, `issue_count=0` in [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_srep32121.semantic_gate.json).
- Publication QA rerun: `publication_grade_pass=true`, `risk_counts={}` in [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_srep32121.publication_quality.json).
- JSON/JSONL validation passed for touched packet/final/work/report files.

Remaining status: no blocking or major issue, no open rework target, no unrecoverable material gap. Cautions remain for APD6 database-only computed prose, DRAMP qualitative rows without exact database values, HepG2 figure-only exact values/range mismatch, and `accepted_with_cautions_not_clean`.

