完成。`doi__10.1371_journal.pone.0095737` 已重审并修复为 `accepted_with_cautions`，`publication_grade=true`，`rwk-complete-test-0001` 已通过 `rework_responses.jsonl` 关闭，当前 `workflow_context.open_rework_tickets=[]`。

关键修复：
- Worker-4：数据库审查改为 `18 source_verified + 1 source_conflict`，保留 APD6 毒性文本未被本地原文支持的冲突。
- Worker-6：最终 activity 修复为 20 条 Table 1 MIC/MBC 记录，补回 `Vibrio MPV19`；未伪造毒性值。
- Worker-6：机制证据改为 3 条，直接膜通透/成孔证据与结构、epibiont 表型证据分层保存。
- 更新了 final/packet/work/report/workflow/rework 响应文件。

验证结果：
- `semantic_three_layer_gate.py`: `pass_count=1`, `fail_count=0`, `issue_count=0`
- `check_three_layer_publication_quality.py`: `publication_grade_pass=true`, `risk_counts={}`
- JSON 解析检查通过。

主要证据文件：
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0095737/final/review_report.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0095737/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0095737/rework/rework_responses.jsonl)
- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0095737.semantic_gate.json)
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0095737.publication_quality.json)

保留的非阻塞 caution：APD6 的 no-hemolysis/no-cytotoxicity 文本没有本地原文支持，因此作为 `source_conflict` 保存；图中曲线/柱状的精确数值未从图片中硬造。

