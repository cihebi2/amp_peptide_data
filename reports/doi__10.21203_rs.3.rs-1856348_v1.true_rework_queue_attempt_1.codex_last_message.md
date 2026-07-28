完成了 `doi__10.21203_rs.3.rs-1856348_v1` 的 worker-2/4/6 re-review。

关键结果：
- worker-2: 从 PDF Table 2 重建了 `8` 条 MIC activity rows，写入 packet 和 final activity artifacts。
- worker-4: 重审 APD6 linked rows，保留 `source_conflict=1`，`source_verified=1`。
- worker-6: 重写 final adjudication，状态为 `accepted_with_cautions`，`publication_grade=true`。
- rework ticket `rwk-complete-test-0001` 已在 `rework_responses.jsonl` 关闭；`workflow_context.open_rework_tickets=[]`。
- `unrecoverable_material_gaps=[]`。保留两个非阻断 caution：APD6/论文 cysteine-count conflict；本地 supplementary `.bin` 是 Research Square/help/privacy HTML，不是科学补充表。

主要更新：
- [final review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.21203_rs.3.rs-1856348_v1/final/review_report.json)
- [final activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.21203_rs.3.rs-1856348_v1/final/activity_toxicity_evidence.json)
- [final database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.21203_rs.3.rs-1856348_v1/final/database_record_verification.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.21203_rs.3.rs-1856348_v1/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.21203_rs.3.rs-1856348_v1/rework/rework_responses.jsonl)
- Added repair driver: [repair_doi_10_21203_rs_3_rs_1856348_v1_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_21203_rs_3_rs_1856348_v1_worker246.py)

Verification:
- Semantic gate: `publication_grade_pass_count=1/1`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`, `activity_records=8`, `mechanism_claims=2`.
- JSON/JSONL parse check passed for target artifacts.
- Repair script `py_compile` passed.

