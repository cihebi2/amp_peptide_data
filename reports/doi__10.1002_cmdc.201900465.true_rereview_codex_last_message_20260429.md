已完成本篇 `doi__10.1002_cmdc.201900465` 真复审。结论：**未接受，保留 rework**。

我修复了 worker-2/4/6 层中可安全修复的部分：
- activity：Table 2/3 从 XML 重建为 193 条 source-located 记录，移除旧的 126 条错误 Table 3 MBC 派生记录；Table 1 图片矩阵只完成数据库相关单元格核对，未全量转写。
- database：重新按 primary locator 匹配数据库行，结果为 `source_verified=361`、`source_conflict=92`，冲突保留。
- worker-6：更新最终审查为 `needs_targeted_rework`、`publication_grade=false`、`open ticket=1`。

主要修改文件：
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1002_cmdc.201900465/final/activity_toxicity_evidence.json)
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1002_cmdc.201900465/final/database_record_verification.json)
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1002_cmdc.201900465/final/review_report.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1002_cmdc.201900465/work/review/quality_feedback.json)
- [rework_requests.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1002_cmdc.201900465/rework/rework_requests.jsonl)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1002_cmdc.201900465/rework/rework_responses.jsonl)
- 同步更新了 packet analysis/final、`packet_manifest.json`、`analysis_status.json`、Miaobi workflow context/logs。

验证结果：
- semantic gate：失败，`issue_count=2`，原因仅为 `review_status_not_publication_grade` 和 `publication_grade_not_true`。
- publication quality gate：失败，`open_rework_targets=1`。
- miaobi validate：通过，`ok=true`。
- 报告已写入 `reports/doi__10.1002_cmdc.201900465.true_rereview.semantic_gate.json` 和 `reports/doi__10.1002_cmdc.201900465.true_rereview.publication_quality.json`。

保留的下一 owner：`worker-2 -> worker-4 -> worker-6`。核心原因是 Table 1 图片矩阵还没有全量 row-level 转写，且 92 条数据库冲突仍需后续 source-reviewed adjudication。

