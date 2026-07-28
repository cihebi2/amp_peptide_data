已完成 `doi__10.2147_idr.s165179` 单篇 re-review/repair。

核心结果：
- Worker-2：重建 activity/toxicity，恢复 Table 2、Table 3、Table S1 和关键图文/体内效果值，共 `28` 条记录。
- Worker-4：重审数据库行，共 `44` 条，`source_verified=40`，保留 `source_conflict=4`。
- Worker-6：重写 adjudication/review，关闭 `rwk-complete-test-0001`，状态为 `accepted_with_cautions`，`publication_grade=true`。
- 保留 1 个非阻断 `unrecoverable_material_gaps`：Figure S1/S2 精确曲线点本地材料未提供表格坐标，`blocks_publication_grade=false`。

主要更新文件：
- [repair script](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_2147_idr_s165179_worker246.py)
- [activity final](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.2147_idr.s165179/final/activity_toxicity_evidence.json)
- [database final](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.2147_idr.s165179/final/database_record_verification.json)
- [review report](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.2147_idr.s165179/final/review_report.json)
- [quality feedback](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.2147_idr.s165179/work/review/quality_feedback.json)
- [rework responses](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.2147_idr.s165179/rework/rework_responses.jsonl)

验证已通过：
- `semantic_three_layer_gate.py`: `pass_count=1`, `fail_count=0`, `issue_count=0`
- `check_three_layer_publication_quality.py`: `publication_grade_pass=true`, `risk_counts={}`
- [complete report](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.2147_idr.s165179.complete_message_test_report.json) 现在为 `source_reviewed_publication_grade_ready`，open rework ticket 为 `0`。

