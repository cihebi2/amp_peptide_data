已完成 `doi__10.1371_journal.pone.0096222` 单篇 re-review。

结果：`accepted_with_cautions`，无 open rework ticket。原 ticket `rwk-complete-test-0001` 已在 [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0096222/rework/rework_responses.jsonl) 记录为 resolved。

主要修复：
- Worker-2：补回 7 条 source-supported activity/host-cell rows，写入 packet/final activity artifacts。
- Worker-4：复核 12 条 linked database/literature rows，保留 10 条 `source_conflict`，2 条 literature `source_verified`。
- Worker-6：重写 source-reviewed adjudication/final review，保留数据库 target 过宽、sequence 未从 primary text clean verified、figure exact values 未数字化的 caution。
- 更新 [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0096222/work/review/quality_feedback.json)：`issue_count=0`，`rework_targets=[]`。
- 更新 workflow/packet/report 状态：analysis accepted，open tickets 清零。

验证：
- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0096222.semantic_gate.json): `issue_count=0`, `publication_grade_fail_count=0`
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0096222.publication_quality.json): `publication_grade_pass=true`, `risk_counts={}`
- [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0096222.complete_message_test_report.json): `open_rework_ticket_count=0`, `final_approval_status=accepted_with_cautions`

新增了可复现修复脚本：[repair_doi_10_1371_journal_pone_0096222_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1371_journal_pone_0096222_worker246.py)。

