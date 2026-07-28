已完成 `doi__10.3389_fimmu.2020.00347` 的 worker-2/4/6 re-review 修复。

结果：
- Worker-2: [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fimmu.2020.00347/final/activity_toxicity_evidence.json) 更新为 89 条 source-reviewed 记录：MIC 34、cell_viability 52、antiviral_activity 3。
- Worker-4: [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fimmu.2020.00347/final/database_record_verification.json) 更新为 9 条 APD6/DBAASP/DRAMP 记录，保留数据库 provenance/caution。
- Worker-6: [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fimmu.2020.00347/final/review_report.json) 现在是 `accepted_with_cautions` / `publication_grade=true`，`rework_targets=[]`。
- Rework response 已写入 [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.3389_fimmu.2020.00347/rework/rework_responses.jsonl)，ticket `rwk-complete-test-0001` 已关闭。
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.3389_fimmu.2020.00347/work/review/quality_feedback.json) 现在 `issue_count=0`，无 `qc_failure_reasons`，无 `unrecoverable_material_gaps`。

验证：
- Semantic gate: pass `1/1`, `issue_count=0` in [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.3389_fimmu.2020.00347.semantic_gate.json)
- Publication QA: `publication_grade_pass=true`, `risk_counts={}` in [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.3389_fimmu.2020.00347.publication_quality.json)
- Complete report updated to `accepted_with_cautions`, `open_rework_ticket_count=0`.

I also left the reproducible repair runner at [repair_doi_10_3389_fimmu_2020_00347_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_3389_fimmu_2020_00347_worker246.py).

