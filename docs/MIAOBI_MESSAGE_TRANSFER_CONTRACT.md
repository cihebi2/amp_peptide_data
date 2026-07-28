# 妙笔消息传递契约 for Batch 4-Team Paper Review

## 1. 定位

妙笔消息传递机制是论文审查的外层控制面：负责状态推进、消息回放、artifact 索引、失败回跳和前端展示。

它不是论文证据本体。论文证据本体仍然是：

```text
paper_packets/<paper_id>/
papers/<paper_id>/packet/
final/*.json
analysis/*.json
rework/*.jsonl
locators/locator_index.json
```

## 2. 妙笔数据面与论文审查映射

| 妙笔概念 | 论文审查中的用途 | 本地桥接文件 |
| --- | --- | --- |
| `workflow_runs` | 一篇论文或一个批次的流程实例 | `workflow_context.json` |
| `workflow_context` | 跨 state 传递的轻量状态和 artifact path | `workflow_context.json` |
| `state_executions` | 每个 state 的 provider/model/prompt/output/耗时审计 | `state_executions.jsonl` |
| `agent_logs` | CLI、工具、OCR、解析、gate debug 摘要 | `agent_logs.jsonl` |
| `chat_messages` | 前端聊天区的人类可读简短进度 | `chat_messages.jsonl` |
| `artifacts` | packet、gate report、final report、ticket 的路径索引 | `artifacts.jsonl` |
| WebSocket events | 前端状态变化和实时回放 | `events.jsonl` |

## 3. Source-of-Truth 规则

1. `workflow_context.json` 只能保存摘要、路径和状态；不能保存大段论文正文、长序列、协议全文或替代证据。
2. `artifacts.jsonl` 登记 artifact path；artifact 内容仍以文件本体为准。
3. `chat_messages.jsonl` 只用于人类阅读，不能作为验收依据。
4. `state_executions.jsonl` 是执行审计，不是科学证据；科学证据必须能从 packet locator 回溯。
5. `rework_ticket` 是失败回跳的唯一机器可执行消息；口头反馈必须落成 ticket 才能进入生产回路。

## 4. Workflow Context 最小形状

```json
{
  "workflow_id": "paper-review-doi__10_xxxx",
  "paper_id": "doi__10.xxxx_xxxx",
  "paper_dir_name": "doi__10.xxxx_xxxx",
  "packet_root": "paper_packets/doi__10.xxxx_xxxx",
  "current_state": "material_intake",
  "queue_status": {
    "material": "material_extracting",
    "analysis": "analysis_queued"
  },
  "gate_summary": {
    "structural_ready": false,
    "validator_contract_ready": false,
    "semantic_gate_ready": false,
    "publication_grade_ready": false
  },
  "open_rework_tickets": [],
  "artifacts": {
    "packet_manifest": "paper_packets/doi__10.xxxx_xxxx/packet_manifest.json"
  }
}
```

## 5. State 消息输出要求

每个审查 state 完成后至少写入：

1. `state_execution`：state、role、provider、model、status、output summary、耗时、artifact refs。
2. `event`：`state_started`、`state_completed`、`state_failed`、`artifact_created`、`rework_opened` 等。
3. `artifact`：如果该 state 产生或修改了 packet/final/gate/ticket 文件。
4. `chat_message`：给前端的短进度，禁止粘贴论文长摘录。
5. `agent_log`：只记录工具/CLI/debug 摘要和路径，禁止把 OCR 长文本或源文献大段内容灌入消息层。

## 6. State 到 State 的传递载荷

推荐只传这个载荷给下一个 state：

```json
{
  "paper_id": "doi__10.xxxx_xxxx",
  "packet_root": "paper_packets/doi__10.xxxx_xxxx",
  "workflow_context": ".miaobi-paper-review/workflows/doi__10.xxxx_xxxx/workflow_context.json",
  "packet_manifest": "paper_packets/doi__10.xxxx_xxxx/packet_manifest.json",
  "locator_index": "paper_packets/doi__10.xxxx_xxxx/locators/locator_index.json",
  "open_rework_tickets": [],
  "required_gate": "semantic_gate"
}
```

下一个 state 必须重新打开 artifact path 核查，不得把上一 state 的自然语言总结当作证据。

## 7. Rework 回跳规则

`rework_ticket.target_queue` 决定回跳：

| `target_queue` | 回跳 state |
| --- | --- |
| `material_extraction` | `material_qc`，再按 failure code 路由到 `material_intake` / `main_text_extract` / `supplement_extract` |
| `analysis` | `database_audit` / `activity_toxicity_audit` / `mechanism_audit` |
| `adjudication` | `adjudication` |

`severity=blocking` 或 `major` 时，不允许进入 `publication_grade_ready=true`。

硬约束：消息桥接层必须拒绝 `final_approval status=completed`，除非同时满足：

1. `open_rework_tickets=[]`。
2. `structural_ready=true`、`validator_contract_ready=true`、`semantic_gate_ready=true`、`publication_grade_ready=true`。
3. `queue_status.material` 与 `queue_status.analysis` 不处于 rework/blocking 状态。

若任一条件不满足，`final_approval` 只能写为 `needs_rework` 或 `blocked`，并把论文停在 `rework_queue`，等待 owner lane 修复后重新进入 gate。

## 8. 前端展示建议

前端不要只展示“完成”。建议显示：

```text
Paper ID
Current state
Provider / model / attempt / duration
Material status
Analysis status
Structural ready
Validator-contract ready
Semantic gate ready
Publication-grade ready
Open rework tickets
Latest artifacts
Latest gate failures
```

## 9. 本地桥接目录

没有真实妙笔后端数据库时，用本地目录模拟消息总线：

```text
.miaobi-paper-review/workflows/<paper_dir_name>/
  workflow_context.json
  chat_messages.jsonl
  state_executions.jsonl
  agent_logs.jsonl
  artifacts.jsonl
  events.jsonl
```

等接入真实妙笔后端时，这些 JSON/JSONL 字段可以直接映射到数据库表或 API payload。

## 10. Quality Failure 与新 Codex CLI 打回载荷

当 final QC / worker-6 判定不合格时，消息层必须同时记录三类东西：

1. `qc_failure_reasons`：为什么不合格，包含 code、severity、owner_worker、reason、artifact_path。
2. `rework_ticket`：机器可执行的回跳票据，进入 `paper_packets/<paper_id>/rework/rework_requests.jsonl`。
3. `rework_context_packet`：给前序 worker 或新的 Codex CLI 重新审查的上下文包。

本地上下文包位置：

```text
rework_context/<paper_id>/
  handoff_context.json
  CODEX_REVIEW_PROMPT.md
  artifact_manifest.json
```

生成命令：

```bash
python scripts/build_rework_context_packet.py --paper-id <paper_id>
```

`handoff_context.json` 必须包含：

```json
{
  "paper_id": "doi__10.xxxx_xxxx",
  "source_roots": {},
  "artifacts": {"paths": {}},
  "gate_failures": {},
  "failure_reasons": [],
  "rework_requests": [],
  "quality_feedback": {},
  "owner_workers": ["worker-2", "worker-6"],
  "owner_worker_skills": {
    "worker-2": {
      "skill_path": ".codex/skills/paper-body-table-worker/SKILL.md"
    }
  },
  "codex_cli_command": "cd <repo> && codex \"$(cat rework_context/<paper_id>/CODEX_REVIEW_PROMPT.md)\""
}
```

`CODEX_REVIEW_PROMPT.md` 是唯一允许发给新 Codex CLI 的自然语言载荷。
它只能传路径、失败原因、worker 技能和操作要求；不得复制论文长摘录、长序列或协议全文。

消息总线登记要求：

- `artifacts.jsonl` 记录 `rework_context_packet` 与 `codex_re_review_prompt`。
- `agent_logs.jsonl` 记录上下文包生成摘要和路径。
- `state_executions.jsonl` 记录 `rework_context_prepared status=needs_rework`。
- `workflow_context.json.open_rework_tickets` 保持 ticket open，直到 owner worker 修复并由 gate 证实通过。

如果第 5 次打回后仍不能控制质量，状态必须是 `blocked` 或
`capped_rework_limit_reached`，不能写成 `completed`。

## 11. Start-Once Queue And Best-Effort Stop Rule

生产队列的启动与打回必须分离：

1. 初始队列/工作流对每篇论文或 manifest 只启动一次。
2. 打回时只传递 `workflow_context`、open tickets、artifact paths、gate
   failures 和 `rework_context/<paper_id>/CODEX_REVIEW_PROMPT.md`。
3. 新 Codex CLI owner worker 必须重新打开路径并尽力从本地材料恢复证据：
   XML/NXML、PDF、OA package、supplement、archive、office/spreadsheet、OCR/image
   output、locator index 和 linked database snapshots。
4. 若本地材料不能恢复证据，不得编造；必须写入
   `unrecoverable_material_gaps`，字段包含 `gap_code`、`owner_worker`、
   `source_paths_checked`、`tools_attempted`、`why_unrecoverable`、`impact`、
   `blocks_publication_grade` 和 `next_action`。
5. 到达 `max_rework_attempts` 后，保留兼容字段 `blocked_after_best_effort` /
   `analysis_blocked`，同时写入更细的 `result_status`、`result_category`、
   `result_reason_code`、`retryability`；保留 ticket/gap，然后处理下一篇；不要无限循环。
6. watchdog 默认/推荐至少为 1800 秒；900 秒 timeout 只能标注为
   `blocked_watchdog_timeout_retryable`，不能直接当作真实材料缺失。

推荐控制器：

```bash
python scripts/run_true_rework_queue.py \
  --manifest reports/five_paper_true_rereview_manifest_20260429.json \
  --max-rework 5
```

## 12. Refined Status And Follow-Up Queue Contract

`accepted_after_rework` 不是 clean。生产队列必须保留兼容的
`terminal_status`，同时把 `refined_status` 作为一等输出写入 lane summary，
避免把复审后通过误报为初始 clean。

必需状态层：

```text
terminal_status       # 兼容旧脚本
result_status         # 机器可读停止原因
result_category       # accepted / blocked_source_gap / infrastructure...
refined_status        # 精细状态，不允许省略
refined_category      # 精细大类
recommended_next_action
```

固定的 accepted 细分：

```text
accepted_clean_initial_gate_pass
accepted_after_rework_attempt1
accepted_after_rework_attempt1_with_infra_retry
accepted_after_rework_multi_attempt
accepted_after_rework_multi_attempt_with_infra_retry
```

固定的 blocked / recovery 细分：

```text
blocked_process_timeout_1800s_retryable
blocked_source_gap_figure_chart_exact_value
blocked_source_gap_missing_external_supplement
blocked_parser_gap_activity_table
blocked_quality_gate_rework_cap_unresolved
infrastructure_retry_exhausted_api_or_network
infrastructure_retry_exhausted_worker_nonzero_exit
infrastructure_retry_exhausted_worker_interrupted
infrastructure_retry_exhausted_paper_runtime
```

每次 `scripts/run_true_rework_queue.py` 完成后，必须自动写入
`reports/followup_queues/` 下的后续队列 manifest：

```text
infra_recovery
watchdog_retry
source_staging_needed
parser_manual_extraction_needed
owner_context_rework_needed
```

前四个是主后续队列；`owner_context_rework_needed` 是兜底质量门队列，
防止 bounded rework 后仍未闭合的论文被静默丢失。

当前可回放命令：

```bash
python scripts/refine_true_rework_queue_status.py \
  --lane-glob 'reports/true_rework_queue_queue_next500_1800_lane*_latest.json'
```

后续队列的统一入口：

```bash
python scripts/run_followup_queues.py
```

默认只生成执行计划。只有明确要启动恢复波次时才加 `--execute`。支持直接执行
`infra_recovery`、`watchdog_retry`、`owner_context_rework_needed` 和
`source_staging_needed` 的前置诊断，以及 `accepted_sample_audit` 的严格 gate /
review provenance 抽样核验；`parser_manual_extraction_needed` 会生成任务
manifest，等待 worker-2/人工/vision fallback 专项处理。
可用 `--queue <queue_name>` 限定单个后续队列，避免一次启动所有恢复分支。

source staging 前置诊断入口：

```bash
python scripts/source_staging_preflight.py \
  --manifest reports/followup_queues/<run>_source_staging_needed.json
```

accepted 也要抽样 QA。`scripts/refine_true_rework_queue_status.py` 会自动生成
`accepted_sample_audit` manifest：覆盖所有带 infra retry / multi-attempt 的 accepted，
再加入确定性 baseline sample。这个队列只证明需要抽样复核，不代表 accepted 论文
已经 publication-grade clean。
