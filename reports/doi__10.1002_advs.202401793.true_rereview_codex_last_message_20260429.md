完成复审；没有把本篇标记为 publication-grade。

我修复了 worker-4/worker-6 层的本篇 artifacts：DBAASP MIC 行已重新指向正确 peptide 列，错误用 MIC 行证明 MBIC/MBEC 的记录已降级为 `source_conflict`。数据库审计现在是 `source_verified=99`、`source_conflict=24`、错误 MIC 列 locator 数 `0`。但仍保留 rework，因为 activity 表列标签、补充 DOC 图值提取、mechanism ontology 仍不够 publication-grade。

修改文件：
- `paper_packets/doi__10.1002_advs.202401793/analysis/database_record_audit.json`
- `paper_packets/doi__10.1002_advs.202401793/final/database_record_verification.json`
- `papers/doi__10.1002_advs.202401793/final/database_record_verification.json`
- `paper_packets/doi__10.1002_advs.202401793/analysis/adjudication_report.json`
- `paper_packets/doi__10.1002_advs.202401793/final/review_report.json`
- `papers/doi__10.1002_advs.202401793/final/review_report.json`
- `papers/doi__10.1002_advs.202401793/work/review/quality_feedback.json`
- `paper_packets/doi__10.1002_advs.202401793/rework/rework_requests.jsonl`
- `paper_packets/doi__10.1002_advs.202401793/rework/rework_responses.jsonl`
- `reports/doi__10.1002_advs.202401793.true_rereview.semantic_gate.json`
- `reports/doi__10.1002_advs.202401793.true_rereview.publication_quality.json`
- `reports/doi__10.1002_advs.202401793.true_rereview.miaobi_validate.json`

验证结果：
- semantic gate：失败，`publication_grade_pass_count=0/1`；原因是 `needs_targeted_rework` 和 `publication_grade=false`。
- publication quality gate：失败，`publication_grade_pass=false`，`open_rework_targets=1`。
- miaobi validate：通过，`ok=true`。
- JSON 解析检查：上述修改的 JSON 报告和 artifacts 都通过解析。

`rwk-complete-test-0001` 已保留并改成更具体的 open ticket，下一步 owner 包括 worker-2/3/4/5，完成后必须再交 worker-6 复审。

