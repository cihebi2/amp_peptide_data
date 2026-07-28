完成。没有重跑初始 workflow/bootstrap，只修了 `doi__10.3390_molecules26010165` 的 worker-2/4/6 层。

主要结果：
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3390_molecules26010165/final/activity_toxicity_evidence.json): 13 条 source-backed activity/toxicity 记录。
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3390_molecules26010165/final/database_record_verification.json): 19 条数据库审查，`source_verified=13`，`source_conflict=6`，冲突未抹平。
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3390_molecules26010165/final/review_report.json): `accepted_with_cautions`，`publication_grade=true`，原 ticket `rwk-complete-test-0001` 已关闭。
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3390_molecules26010165/work/review/quality_feedback.json): `issue_count=0`，无 open rework targets。
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.3390_molecules26010165/rework/rework_responses.jsonl): 已追加 source-reviewed repair response。

验证已重跑：
- `semantic_three_layer_gate.py`: `publication_grade_pass_count=1`, `fail_count=0`, `issues=[]`
- `check_three_layer_publication_quality.py`: `publication_grade_pass=true`, `risk_counts={}`

保留的层级事实：material packet 仍记录为 `material_extracted_with_gaps` 的历史层状态，但当前已无 open material blocker；无本地 supplementary assets 和图像曲线精确点值未表格化被记录为非阻断 `unrecoverable_material_gaps`，没有用来伪造数值。

