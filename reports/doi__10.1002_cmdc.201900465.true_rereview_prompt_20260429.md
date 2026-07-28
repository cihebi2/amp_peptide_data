你是一个新的 Codex CLI 复审 worker。现在执行“真正复审”，不是流程烟测。

强约束：
- 只复审这一篇：doi__10.1002_cmdc.201900465。
- 逐层修复，不允许批量改其他论文。
- 不要把论文长摘录、长序列、协议全文写进聊天/最终回答；只写路径、ID、计数、短原因。
- 必须打开 source/paper.xml、final/work/packet/rework 文件和数据库快照；不要只信现有总结。
- 若不能达到 publication-grade，必须保留 rework，更新 quality_feedback.json / review_report.json / rework_requests.jsonl / rework_responses.jsonl，写清楚为什么不合格和下一 owner。
- 若修复了 worker-2 activity 问题和 worker-4 数据库问题，也必须由 worker-6 重新把关；只有 semantic gate 与 publication quality gate 都通过且 open ticket=0 才能接受。
- 结束前运行本篇 semantic gate、publication quality gate、miaobi validate，并在最终消息列出修改文件和验证结果。

下面是本篇的上下文包提示，请严格执行：

# Codex CLI Re-review Prompt

You are a new Codex CLI paper-review worker for Batch 4-Team. Re-review exactly one paper: `doi__10.1002_cmdc.201900465`.

## Immediate Contract

- Read the listed worker skill files before editing.
- Reopen source artifacts from paths; do not trust chat summaries as evidence.
- Fix only the owned layer(s): worker-2, worker-4, worker-6.
- Preserve separate layers: material packet, validator contract, semantic gate, publication-grade review.
- Do not mark the paper accepted while any blocking/major issue or open rework ticket remains.
- Write a rework response and rerun gates after repair; if quality is still not controllable, keep the ticket open.

## Worker Skills To Load

- worker-2: `.codex/skills/paper-body-table-worker/SKILL.md` (body/table activity-toxicity repair)
- worker-4: `.codex/skills/paper-database-record-auditor/SKILL.md` (database record adjudication)
- worker-6: `.codex/skills/paper-adjudicator-review-worker/SKILL.md` (final adjudication and quality gate)

## Why The Previous QC Failed

- review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
- gate/parser issue: valid abbreviated organism names such as A. baumannii are flagged by the sentence-fragment heuristic and must be normalized or the gate fixed
- activity parser quality issue: some extracted rows use peptide IDs/method labels/properties as target species or MIC rows, so row-level activity needs repair before acceptance
- database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
- material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion
- The framework test inventories real material but does not complete worker-6 source-reviewed adjudication.
- Linked database rows include source_conflict/database-only cases that must be preserved or resolved by source review.
- One or more activity-bearing tables could not be safely parsed into target/entity/value rows.
- The framework test inventories real material but does not complete worker-6 source-reviewed adjudication.
- Linked database rows include source_conflict/database-only cases that must be preserved or resolved by source review.
- One or more activity-bearing tables could not be safely parsed into target/entity/value rows.

## Artifact Paths To Reopen

- packet_manifest: `paper_packets/doi__10.1002_cmdc.201900465/packet_manifest.json`
- locator_index: `paper_packets/doi__10.1002_cmdc.201900465/locators/locator_index.json`
- extraction_status: `paper_packets/doi__10.1002_cmdc.201900465/extraction/extraction_status.json`
- extraction_quality_report: `paper_packets/doi__10.1002_cmdc.201900465/extraction/extraction_quality_report.json`
- analysis_status: `paper_packets/doi__10.1002_cmdc.201900465/analysis/analysis_status.json`
- packet_activity: `paper_packets/doi__10.1002_cmdc.201900465/analysis/activity_toxicity_evidence.json`
- packet_database: `paper_packets/doi__10.1002_cmdc.201900465/analysis/database_record_audit.json`
- packet_mechanism: `paper_packets/doi__10.1002_cmdc.201900465/analysis/mechanism_evidence.json`
- packet_adjudication: `paper_packets/doi__10.1002_cmdc.201900465/analysis/adjudication_report.json`
- rework_requests: `paper_packets/doi__10.1002_cmdc.201900465/rework/rework_requests.jsonl`
- rework_responses: `paper_packets/doi__10.1002_cmdc.201900465/rework/rework_responses.jsonl`
- final_review_report: `papers/doi__10.1002_cmdc.201900465/final/review_report.json`
- final_activity: `papers/doi__10.1002_cmdc.201900465/final/activity_toxicity_evidence.json`
- final_database: `papers/doi__10.1002_cmdc.201900465/final/database_record_verification.json`
- final_mechanism: `papers/doi__10.1002_cmdc.201900465/final/mechanism_ontology_record.json`
- quality_feedback: `papers/doi__10.1002_cmdc.201900465/work/review/quality_feedback.json`
- workflow_context: `.miaobi-paper-review/workflows/doi__10.1002_cmdc.201900465/workflow_context.json`
- state_executions: `.miaobi-paper-review/workflows/doi__10.1002_cmdc.201900465/state_executions.jsonl`
- chat_messages: `.miaobi-paper-review/workflows/doi__10.1002_cmdc.201900465/chat_messages.jsonl`
- agent_logs: `.miaobi-paper-review/workflows/doi__10.1002_cmdc.201900465/agent_logs.jsonl`
- latest_complete_report: `reports/doi__10.1002_cmdc.201900465.complete_message_test_report.json`
- latest_capped_rework_report: `reports/doi__10.1002_cmdc.201900465.capped_rework_test_report.json`

## Required Output

1. Repair the owner-layer artifact(s) under the paper-local packet/final/work paths.
2. Update `paper_packets/doi__10.1002_cmdc.201900465/rework/rework_responses.jsonl` with what was checked and what remains.
3. Update `papers/doi__10.1002_cmdc.201900465/work/review/quality_feedback.json` if final QC still fails, with concrete `qc_failure_reasons`.
4. Rerun semantic and publication gates for this paper.
5. If gates still fail, create/keep a targeted rework ticket with owner worker, omission code, artifact path, and source paths to check.
