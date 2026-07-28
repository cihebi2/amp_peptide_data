Re-reviewed `doi__10.1155_2014_158546` and repaired the owned layers.

Updated worker-2/4/6 artifacts under packet/final/work paths:
- 6 source-located activity/toxicity rows
- 10 linked database rows adjudicated as `source_verified` with nonblocking cautions
- 3 mechanism/pharmacology claims constrained to supported evidence
- `rwk-complete-test-0001` resolved in [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1155_2014_158546/rework/rework_responses.jsonl)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1155_2014_158546/work/review/quality_feedback.json) now has `issue_count: 0`, no `qc_failure_reasons`, no open `rework_targets`

Final state is `accepted_with_cautions`, not clean acceptance. The cautions are nonblocking: no structured XML tables, no separate supplementary assets, no linked sequence snapshot rows, and no direct antimicrobial mechanism assay.

Verification:
- Semantic gate: `1/1` pass, `issue_count=0`
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`
- Message bus validation: `ok=true`
- Latest reports: [semantic](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1155_2014_158546.true_rework_queue_attempt_1.after_worker.semantic_gate.json), [publication](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1155_2014_158546.true_rework_queue_attempt_1.after_worker.publication_quality.json)

