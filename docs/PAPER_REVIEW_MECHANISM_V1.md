# Batch 4-Team Paper Review Mechanism V1

This file adapts the copied Batch 2-Team skills into a Batch 4-Team operating contract and maps them onto the Codex CLI / Claude CLI workflow-orchestrator system described in `D:\runmi\公众号\miaobi\CODEX\docs\codex-claude-cli-workflow-template.md`.

## 1. Current Imported Skill Surface

The current folder now contains the project-local skills copied from `/root/work/抗菌肽/数据库/batch/2-team/.codex/skills` into `.codex/skills/`.

Use these copied skills as the governing paper-review contract for Batch 4-Team:

| Skill | Role in the review mechanism |
| --- | --- |
| `.codex/skills/amp-three-layer-curation/SKILL.md` | Overall AMP three-layer curation contract, status vocabulary, two-queue design, and acceptance rules. |
| `.codex/skills/paper-omx-team-extraction/SKILL.md` | OMX team launch, monitor, rescue, and final verification rules. |
| `.codex/skills/paper-batch-orchestrator/SKILL.md` | Batch manifests, controller reconciliation, helper scripts, and reporting rules. |
| `.codex/skills/paper-intake-worker/SKILL.md` | Worker 1: paper/database/source intake and packet setup. |
| `.codex/skills/paper-body-table-worker/SKILL.md` | Worker 2: main-text/table activity and toxicity evidence extraction. |
| `.codex/skills/paper-supp-evidence-worker/SKILL.md` | Worker 3: supplementary, OCR, archive, and office-file material extraction. |
| `.codex/skills/paper-database-record-auditor/SKILL.md` | Worker 4: database identity, sequence/modification, source traceability, and conflict audit. |
| `.codex/skills/paper-mechanism-ontology-worker/SKILL.md` | Worker 5: mechanism claim ontology and evidence-strength classification. |
| `.codex/skills/paper-adjudicator-review-worker/SKILL.md` | Worker 6: final adjudication, rework routing, and publication-grade decision. |
| `.codex/skills/paper-merge-review-worker/SKILL.md` | Legacy four-worker compatibility only; do not use as the main AMP three-layer review surface. |

The imported files still mention Batch 2-Team because they are the proven production contract. Batch 4-Team should treat those references as the baseline standard, not as a reason to weaken the gate.

## 2. Core Review Principle

Do not collapse different kinds of completion into one word such as "done" or "reviewed". Batch 4-Team must report four separate layers:

1. `material_packet_ready`: the paper packet is structurally complete or complete with named nonblocking gaps.
2. `validator_contract_ready`: scripts and schema checks pass.
3. `semantic_gate_ready`: source-grounded semantic checks pass without hard issues.
4. `publication_grade_ready`: worker-6 performed paper-specific source-reviewed adjudication and there are zero blocking rework targets.

A paper can be packet-ready but not publication-grade. A batch can be validator-clean but still not scientifically reviewed.

## 3. Two-Queue Operating Model

### Material Extraction Queue

Owned by workers 1-3.

Purpose: build a source-grounded packet, not final scientific conclusions.

Required outputs under each paper packet:

```text
packet_manifest.json
raw/paper.xml
raw/paper.pdf
raw/supplementary_original/
raw/oa_package/
extracted/xml_sections.json
extracted/pdf_text.jsonl
extracted/pdf_tables.json
extracted/figure_captions.json
extracted/supplementary_index.json
extracted/supplementary_text.jsonl
extracted/supplementary_tables.json
extracted/archive_manifest.json
extracted/ocr/
database/linked_sequence_records.jsonl
database/linked_literature_records.jsonl
database/linked_experiment_records.jsonl
database/linked_assay_records.jsonl
locators/locator_index.json
extraction/extraction_status.json
extraction/extraction_errors.jsonl
```

Allowed material statuses:

```text
material_queued
material_extracting
material_extracted_complete
material_extracted_with_gaps
material_needs_rework
material_blocked_missing_source
```

A material packet is not complete unless XML, PDF, OA package members, true supplementary files, archives, OCR/office attempts, and database-row snapshots are inventoried or explicitly marked unavailable with path/tool/failure evidence.

### Analysis And Adjudication Queue

Owned by workers 4-6.

Purpose: consume the packet, audit database records, extract/normalize evidence, classify mechanism claims, and adjudicate final acceptance.

Required outputs:

```text
analysis/database_record_audit.json
analysis/activity_toxicity_evidence.json
analysis/mechanism_evidence.json
analysis/adjudication_report.json
final/database_record_verification.json
final/activity_toxicity_evidence.json
final/mechanism_evidence.json
final/review_report.json
rework/rework_requests.jsonl
rework/rework_responses.jsonl
```

Allowed analysis statuses:

```text
analysis_queued
analysis_running
analysis_artifacts_present
analysis_needs_material_rework
analysis_needs_analysis_rework
analysis_adjudicated_with_cautions
analysis_source_reviewed_accepted
analysis_accepted
analysis_blocked
```

`analysis_artifacts_present` only means files exist. It is not acceptance. Strict new runs should prefer `analysis_source_reviewed_accepted` over the legacy alias `analysis_accepted`.

## 4. Codex CLI / Claude CLI Workflow Mapping

The Codex/Claude system should be used as an orchestrated workflow, not as direct Codex-to-Claude chat.

Key rule from the workflow template: each state selects exactly one Provider. The Orchestrator advances states, builds prompts and schemas, calls `runAgent()`, logs `state_executions`, writes `agent_logs`, and broadcasts WebSocket events.

Recommended provider split for paper review:

| Workflow state | Provider | Reason |
| --- | --- | --- |
| `select_paper` | `codex-cli` | Deterministic manifest and asset inspection. |
| `material_intake` | `codex-cli` | File-system/tool-heavy packet construction. |
| `main_text_extract` | `codex-cli` | Structured XML/table extraction with locators. |
| `supplement_extract` | `codex-cli` | OCR/archive/office recovery and error logging. |
| `material_qc` | `codex-cli` | Structural packet verification. |
| `database_audit` | `codex-cli` | Source/database conflict reasoning and JSON output. |
| `activity_toxicity_audit` | `codex-cli` | Row-level evidence normalization and semantic checks. |
| `mechanism_audit` | `codex-cli` | Ontology classification and overclaim prevention. |
| `adjudication` | `codex-cli` | Final source-reviewed acceptance/rework decision. |
| `reader_report` | `claude-cli` optional | Human-readable narrative summary only, never the source-of-truth gate. |
| `final_approval` | `codex-cli` | Strict schema/semantic/publication-grade gate. |

Use Claude for readable summaries, editorial polish, or a reviewer-facing report after Codex has produced source-grounded artifacts. Do not let Claude narrative output override worker-6 adjudication, semantic gate results, or rework tickets.

## 5. Proposed State Machine

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

Rework transitions:

```text
material_qc FAIL -> material_intake | main_text_extract | supplement_extract
adjudication NEEDS_MATERIAL_REWORK -> material_intake | main_text_extract | supplement_extract
adjudication NEEDS_ANALYSIS_REWORK -> database_audit | activity_toxicity_audit | mechanism_audit
semantic_gate FAIL -> targeted owner state from failure_code
publication_quality_gate FAIL -> adjudication
final_approval APPROVE -> __complete__
final_approval REVISE -> targeted owner state
final_approval BLOCK -> __blocked__
```

Implementation guard: `scripts/miaobi_message_bridge.py` rejects any attempt to record `final_approval status=completed` while an open rework ticket exists, any required gate is false, or material/analysis queue status is a rework/blocking state. In those cases the state must be `needs_rework` or `blocked`, and the current state should become `rework_queue`.

## 6. Hard Acceptance Gate

A paper is `publication_grade_ready` only if all conditions are true:

1. Deep retrieval is proven for paper XML, PDF, OA package, true supplements, archives, OCR/office extraction, figures/tables, and linked database rows.
2. Deep acquisition is proven: workers 4-6 reopened packet sources and database rows for this paper instead of copying `work/` or `final/` artifacts.
3. Layer 1 database records use only the accepted status vocabulary: `source_verified`, `source_conflict`, `database_only_no_primary_source`, `sequence_modified_not_normalized`, or `unresolved_record`.
4. `source_verified` records have primary-source locators, not only database links.
5. Layer 2 activity/toxicity rows are row-level and include endpoint, raw value, raw unit or explicit no-unit rationale, target class/species/strain when reported, conditions/statistics when reported, evidence ladder, and locator.
6. Layer 3 mechanism claims include `claim_id`, `claim_text`, evidence class, locator, and direct assay type when classed as `direct_mechanism`.
7. Cross-database conflicts remain visible as cautions or conflicts; they are not smoothed into source-verified acceptance.
8. `final/review_report.json` includes paper-specific worker-6 provenance: `reviewed_at`, `review_model`, `reasoning_effort`, `checked_inputs`, `materials_exhausted`, `semantic_quality_checks`, `per_layer_decision_rationale`, `rework_targets`, and `caution_findings`.
9. `rework_targets` is empty for `accepted_clean` and `accepted_with_cautions`.
10. Strict semantic and publication-quality gates pass without `--allow-findings`, `--allow-risk`, or `|| true` terminal shortcuts.

## 7. Durable Rework Ticket Contract

Every hard failure must become a packet rework ticket. Chat-only feedback is not enough.

Minimum ticket fields:

```json
{
  "ticket_id": "rwk-0001",
  "paper_id": "paper-id",
  "target_queue": "material_extraction",
  "severity": "blocking",
  "requested_by": "worker-6",
  "failure_code": "missing_supplementary_table_locator",
  "reason": "Activity rows cite Table S2 but supplementary table extraction is absent.",
  "artifact_path": "final/activity_toxicity_evidence.json",
  "failing_object": "activity_records[12]",
  "source_evidence_to_check": ["raw/supplementary_original/s001.pdf"],
  "requested_outputs": [
    {
      "asset": "raw/supplementary_original/s001.pdf",
      "need": "OCR/extract Table S2 row-level MIC records.",
      "required_locators": ["supp:s001.pdf:table=S2"]
    }
  ],
  "blocks": ["activity_toxicity_evidence", "review_report"],
  "created_at": "ISO-8601 timestamp"
}
```

Valid `target_queue` values: `material_extraction`, `analysis`, `adjudication`.

Valid `severity` values: `blocking`, `major`, `minor`, `caution`.

## 8. Batch-Level Dashboard Metrics

Batch 4-Team should show these counts separately:

| Metric | Meaning |
| --- | --- |
| `pending` | Papers not yet claimed or queued. |
| `material_extracting` | Material queue currently working. |
| `material_extracted_complete` | Packet structurally complete. |
| `material_extracted_with_gaps` | Packet usable but with named nonblocking gaps. |
| `material_blocked_missing_source` | Missing local primary/supplementary source prevents packet completion. |
| `analysis_running` | Workers 4-6 are reviewing packet evidence. |
| `analysis_needs_material_rework` | Analysis found a missing material/locator gap. |
| `analysis_needs_analysis_rework` | Analysis/adjudication output must be repaired. |
| `semantic_gate_pass` | Strict semantic script found no hard issues. |
| `publication_grade_ready` | Worker-6 source-reviewed acceptance and all gates pass. |
| `accepted_with_cautions` | Publication-grade with preserved nonblocking conflicts/cautions. |
| `blocked` | Durable blocker ticket exists and no local recovery path remains. |

Never summarize a batch with only `completed/total` unless the layer is named, such as `material_packet_complete=50/50` or `publication_grade_ready=9/100`.

## 9. Workflow-System Implementation Notes

Use the workflow template system like this:

1. Create roles for `material_worker`, `analysis_worker`, `adjudicator`, `quality_gate`, and optional `reader_report_writer`.
2. Set source-grounded states to `codex-cli` with the strongest approved Codex model/effort available. If the runtime cannot prove the required model/effort for publication-grade review, mark the result as non-publication-grade or blocked by model capability.
3. Use `claude-cli` only for optional readable reporting states after strict artifacts exist.
4. Attach JSON schemas to states that write packets, review reports, or rework tickets.
5. Persist every state in `state_executions` and every final artifact path in workflow artifacts.
6. The front end should display Provider/model, attempt count, tokens, elapsed time, and the artifact/rework status per state.
7. Retry should rerun the failed state or targeted owner state, not the whole paper, unless packet manifest corruption is detected.

A template starter is provided in `docs/workflow-templates/amp-paper-review-codex-claude.yaml`.

## 10. Immediate Batch 4-Team Setup Checklist

Before launching real papers in this folder:

1. Confirm the merged corpus roots exist, especially `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets` and `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output`.
2. Refresh `landed_assets/manifests/summary.json`, `landed_sources.csv`, `landed_asset_manifest.csv`, and `landed_metadata_manifest.csv`.
3. Build a Batch 4 manifest from landed assets; do not rely on stale Batch 2 manifests.
4. Launch or configure the material queue first; do not start analysis on papers without packet manifests.
5. Run packet structural checks after material extraction.
6. Run analysis/adjudication only from verified packets.
7. Run semantic and publication-quality gates before claiming any paper as source-reviewed accepted.
8. Publish a batch report with the layered counts in section 8.

## 11. Minimal Verification Commands

The copied helper scripts are under `.codex/skills/paper-batch-orchestrator/scripts/`.

Use these when matching inputs exist:

```bash
python .codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py --help
python .codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py --help
python .codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py --help
python .codex/skills/paper-batch-orchestrator/scripts/verify_batch.py --help
```

For this newly prepared Batch 4-Team folder, the first verification target is that the copied scripts compile and the workflow/mechanism files are present. Real scientific verification requires a manifest and paper packets.

## 12. 妙笔消息传递控制面

Batch 4-Team 现在把妙笔消息传递机制作为论文审查外层控制面。具体契约见 `docs/MIAOBI_MESSAGE_TRANSFER_CONTRACT.md`，本地桥接脚本见 `scripts/miaobi_message_bridge.py`。

### 消息层和证据层分工

- 妙笔消息层负责 state 推进、Provider/model 记录、前端回放、artifact 索引、失败回跳和人类可读进度。
- 论文证据层仍然是 packet、locator、analysis、final 和 rework 文件。
- State 之间只传 `workflow_context`、artifact path、gate summary 和 open ticket id；下游 state 必须重新打开 artifact 核查。
- `chat_messages` 不能作为验收证据；只有 packet-local source locator、final report、semantic gate 和 publication gate 能支撑接受结论。

### 本地消息目录

在真实妙笔后端接入前，用本地目录模拟：

```text
.miaobi-paper-review/workflows/<paper_dir_name>/
  workflow_context.json
  chat_messages.jsonl
  state_executions.jsonl
  agent_logs.jsonl
  artifacts.jsonl
  events.jsonl
```

初始化一篇论文：

```bash
python scripts/miaobi_message_bridge.py init-paper \
  --paper-id doi__10.xxxx_xxxx \
  --packet-root paper_packets/doi__10.xxxx_xxxx
```

记录一个 state：

```bash
python scripts/miaobi_message_bridge.py record-state \
  --paper-id doi__10.xxxx_xxxx \
  --state material_intake \
  --role material_worker \
  --provider codex-cli \
  --model gpt-5.5 \
  --reasoning-effort xhigh \
  --status completed \
  --set-status material=material_extracting \
  --artifact packet_manifest=paper_packets/doi__10.xxxx_xxxx/packet_manifest.json \
  --chat "material_intake complete; packet manifest updated"
```

校验消息链：

```bash
python scripts/miaobi_message_bridge.py validate --paper-id doi__10.xxxx_xxxx
```

### 接入真实妙笔时的映射

| 本地桥接文件 | 妙笔后端建议映射 |
| --- | --- |
| `workflow_context.json` | `workflow_runs.workflow_context` 或独立 context 表 |
| `state_executions.jsonl` | `state_executions` |
| `agent_logs.jsonl` | `agent_logs` |
| `chat_messages.jsonl` | `chat_messages` |
| `artifacts.jsonl` | `artifacts` |
| `events.jsonl` | WebSocket event replay / debug event 表 |

### 新的验收要求

任何论文在进入 `publication_grade_ready=true` 之前，消息层也必须满足：

1. 有 `workflow_context.json`，且包含 packet path、queue status、gate summary、open tickets。
2. 每个已执行 state 至少有一条 `state_execution`。
3. 关键产物在 `artifacts.jsonl` 中登记：packet manifest、locator index、gate report、final review report、rework ticket。
4. 若出现 `needs_targeted_rework`，必须有 rework ticket artifact 和 `rework_opened` 或失败事件。
5. final approval state 必须由 `codex-cli` 记录并检查四层完成度，不能由 Claude 可读报告直接闭环。

## 13. 2026-04-29 Quality Rework Loop Addendum

The 10-paper capped rework run exposed workflow, gate, and parser problems that
must be treated as production blockers before broader review. The detailed
record and repair contract is `docs/QUALITY_REWORK_LOOP_20260429.md`.

New hard rules:

1. Final QC must write concrete `qc_failure_reasons`; generic "not
   publication-grade" is not enough.
2. Every blocking/major QC failure must build a context packet under
   `rework_context/<paper_id>/` with historical artifact paths, omission codes,
   open tickets, gate failures, and owner worker skill paths.
3. The context packet prompt is the approved payload to send to a new Codex CLI
   worker for targeted re-review.
4. The owner worker repairs only its layer, writes a rework response, and reruns
   the gates; worker-6 then re-adjudicates.
5. If quality remains uncontrollable after five rework decisions, mark the paper
   blocked/capped instead of accepting it.
6. Start the initial queue once only. Rework loops must consume
   `rework_context/<paper_id>/CODEX_REVIEW_PROMPT.md` and must not rerun the
   bootstrap unless explicitly reset.
7. Owner workers must do bounded best-effort recovery from paper-local materials
   before giving up. If local evidence cannot be recovered, write
   `unrecoverable_material_gaps` with source paths, tools attempted, reason,
   impact, and owner worker, then continue to the next paper.

Use this command whenever a paper is打回:

```bash
python scripts/build_rework_context_packet.py --paper-id <paper_id>
```

Use this controller when the queue should run start-once with fresh Codex CLI
owner workers and a hard attempt cap:

```bash
python scripts/run_true_rework_queue.py --manifest <manifest.json> --max-rework 5
```
