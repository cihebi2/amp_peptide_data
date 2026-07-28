完成。`doi__10.3389_fmicb.2016.02006` 已按 worker-4/worker-6 重新源审并修复。

结果：
- `review_status=accepted_with_cautions`
- `publication_grade=true`
- `open_rework_ticket_ids=[]`
- `unrecoverable_material_gaps=[]`
- 数据库审计保留 `source_verified=14`、`source_conflict=4`
- 活性/毒性最终记录 6 条，机制直接证据 claims 3 条

主要更新：
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2016.02006/final/review_report.json)
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2016.02006/final/database_record_verification.json)
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2016.02006/final/activity_toxicity_evidence.json)
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2016.02006/final/mechanism_ontology_record.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2016.02006/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.3389_fmicb.2016.02006/rework/rework_responses.jsonl)

验证已通过：
- Semantic gate: [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.3389_fmicb.2016.02006.semantic_gate.json) reports `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.3389_fmicb.2016.02006.publication_quality.json) reports `publication_grade_pass=true`, `risk_counts={}`
- 最新汇总已刷新：[complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.3389_fmicb.2016.02006.complete_message_test_report.json)

保留的不是 blocker，而是 caution：DRAMP/CAMP/dbAMP 中部分 anticancer/额外靶菌/单位信息无法由本地原文直接支持，已作为 `source_conflict` 保留，没有硬归一化。

