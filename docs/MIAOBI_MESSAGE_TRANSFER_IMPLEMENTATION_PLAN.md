# 妙笔消息传递机制接入论文审查流程 - 修改方案

## 目标

把妙笔的 Orchestrator / Provider / `state_executions` / `agent_logs` / `chat_messages` / artifact 回放机制引入 Batch 4-Team 论文审查流程，让论文审查从“聊天驱动”升级为“状态机 + artifact + rework ticket 驱动”。

## 设计原则

1. **证据不搬家**：论文事实、locator、packet、final report、rework ticket 仍落在本地 `paper_packets/` 或 `papers/<paper_id>/packet/`；妙笔只传路径、状态、摘要和 gate 结果。
2. **消息不替代证据**：`chat_messages` 只面向人类显示；`workflow_context`、`artifacts`、`state_executions`、`rework/*.jsonl` 才是机器可追踪链路。
3. **状态单向推进，失败精准回跳**：每个 state 只接收上一 state 的上下文和 artifact path；失败时根据 `failure_code` / `target_queue` 回到 owner state。
4. **Provider 责任分离**：Codex CLI 负责结构化审查、工具执行、schema gate 和 final approval；Claude CLI 只做可选可读报告，不参与最终科学裁决。
5. **四层完成度分开显示**：material packet、validator contract、semantic gate、publication-grade 分别计数和展示。

## 修改范围

### A. 文档层

- 新增消息传递契约文档，定义妙笔侧数据表/事件与论文审查 artifact 的映射。
- 更新 `docs/PAPER_REVIEW_MECHANISM_V1.md`，加入妙笔消息总线章节。
- 更新 workflow template，让每个 state 声明输入上下文、输出 artifact、事件和回跳规则。

### B. Schema 层

新增 schema：

- `workflow_context.schema.json`：跨 state 传递的轻量上下文。
- `state_execution_record.schema.json`：等价妙笔 `state_executions` 的本地审计记录。
- `artifact_record.schema.json`：artifact path、类型、生产 state、校验状态。
- `chat_message_record.schema.json`：前端聊天区摘要消息。
- `agent_log_record.schema.json`：CLI/tool/debug 日志摘要。
- `workflow_event.schema.json`：WebSocket / event replay 事件。

已有 schema 继续保留：

- `packet_manifest.schema.json`
- `final_review_report.schema.json`
- `rework_ticket.schema.json`

### C. 本地桥接脚本层

新增 `scripts/miaobi_message_bridge.py`，在没有真实妙笔后端数据库时，提供本地等价消息总线：

```text
.miaobi-paper-review/workflows/<paper_id>/
  workflow_context.json
  chat_messages.jsonl
  state_executions.jsonl
  agent_logs.jsonl
  artifacts.jsonl
  events.jsonl
```

脚本能力：

- `init-paper`：初始化某篇论文的 workflow context 和消息日志。
- `record-state`：记录 state 执行、artifact、事件和上下文状态变化。
- `add-artifact`：登记 packet / gate report / final report / rework ticket。
- `add-chat`：写入前端可读摘要。
- `add-log`：写入 debug/tool/CLI 日志摘要。
- `validate`：检查上下文和 JSONL 结构，防止断链。

### D. 运行流程层

把现有论文审查流程改成 artifact-first：

```text
select_paper
  -> material_intake
  -> main_text_extract
  -> supplement_extract
  -> material_qc
  -> database_audit
  -> activity_toxicity_audit
  -> mechanism_audit
  -> adjudication
  -> semantic_gate
  -> publication_quality_gate
  -> final_approval
```

每一步都写：

- `state_execution`：谁、用哪个 provider/model、输入上下文、输出摘要、耗时、状态。
- `artifact`：产生/更新了哪些文件。
- `event`：给前端或 orchestrator 的状态变化。
- `chat_message`：人类可读短消息。
- 必要时 `rework_ticket`：精准回跳。

## 实施步骤

1. 写入 `docs/MIAOBI_MESSAGE_TRANSFER_CONTRACT.md`，明确妙笔消息表与论文审查 artifact 的映射。
2. 扩展 `docs/PAPER_REVIEW_MECHANISM_V1.md`，把妙笔消息传递设为 Batch 4-Team 外层控制面。
3. 新增六个消息传递 schema。
4. 更新 `docs/workflow-templates/amp-paper-review-codex-claude.yaml`，增加 state 的 `context_inputs`、`artifacts_out` 和 `messages_out`。
5. 新增 `scripts/miaobi_message_bridge.py`。
6. 用临时目录执行 smoke test：初始化 demo paper、记录一个 state、登记 artifact、验证消息总线。
7. 做 JSON/schema 解析和 Python 语法验证。

## 验收标准

- 可以从一个 `paper_id` 初始化本地妙笔式 workflow 消息目录。
- 每个 state 的执行记录、artifact、chat、agent log、event 都能落盘为 JSONL。
- `workflow_context.json` 能持续记录 paper、packet、queue status、gate summary 和 open rework tickets。
- 所有新增 JSON schema 可解析。
- 桥接脚本不依赖第三方包。
- 论文审查主文档明确：妙笔是状态/消息/回放层，packet/final/rework 仍是证据层。
