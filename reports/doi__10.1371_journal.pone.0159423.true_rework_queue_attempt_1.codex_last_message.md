完成。`doi__10.1371_journal.pone.0159423` 已按 worker-4/worker-6 重审并关闭 `rwk-complete-test-0001`。

结果：
- `review_status`: `accepted_with_cautions`
- `publication_grade`: `true`
- `quality_feedback.issue_count`: `0`
- `open_rework_ticket_ids`: `[]`
- `unrecoverable_material_gaps`: `[]`

修复要点：
- 重新锚定数据库审计：40 个原先未闭合的 DBAASP assay conflict 已匹配到本地 XML/PDF 的 Table 3 / Table 4 source locators。
- 保留 27 个 DRAMP `No MICs found` 元数据行为非阻断 `source_conflict` caution，不再作为 pending rework。
- final activity 增加本地可恢复的 Table 4 Tetrahymena `PCmin` / `PC100` 行，final activity 总数为 180。
- final mechanism 从自动占位改为 worker-6 source-reviewed 的 3 条 bounded claims。
- 已追加 rework response 到 [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0159423/rework/rework_responses.jsonl)。

验证：
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- 更新了 [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0159423.complete_message_test_report.json)。

