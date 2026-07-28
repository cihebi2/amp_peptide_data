已完成 `doi__10.3389_fmicb.2018.02249` 单篇重审修复，并只动 worker-2/4/6 相关层。

结果：
- worker-2：重建 [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2018.02249/final/activity_toxicity_evidence.json)，现在有 9 条源定位记录：7 条 Table 1 MIC + 2 条毒性/溶血记录。
- worker-4：重建 [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2018.02249/final/database_record_verification.json)，21 条数据库关联记录中 `source_verified=19`，`source_conflict=2`，冲突作为 caution 保留。
- worker-6：更新 [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2018.02249/final/review_report.json) 为 `accepted_with_cautions`、`publication_grade=true`，不是 `accepted_clean`。
- 关闭 ticket：追加了 [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.3389_fmicb.2018.02249/rework/rework_responses.jsonl)，并把 workflow/packet 的 open ticket 清为 `[]`。
- QC 状态：[quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fmicb.2018.02249/work/review/quality_feedback.json) 现在 `issue_count=0`，无 `qc_failure_reasons`，无 `rework_targets`。

验证：
- semantic gate: `pass=1/1`, `issue_count=0`
- publication-quality gate: `publication_grade_pass=true`, `risk_counts={}`
- 最新状态写入 [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.3389_fmicb.2018.02249.complete_message_test_report.json)

补充：本目录不是 git repository，`git status` 无法运行。  
