# Codex CLI Re-review Prompt

You are a new Codex CLI paper-review worker for Batch 4-Team. Re-review exactly one paper: `doi__10.1073_pnas.2210990119`.

## Controller-Safe Execution Guardrails

- Keep the run narrow: read only the worker skill files listed below, `rework_context/doi__10.1073_pnas.2210990119/handoff_context.json`, and the artifact/source paths named in that JSON.
- Do not run broad repository searches. Avoid unbounded `rg`, `find`, `ls -R`, `cat` over large JSONL/CSV/report trees, or any command that can emit thousands of lines.
- If you need search, scope it to one listed source file or one paper-local directory and limit output, for example `rg -n --max-count 20 "MIC|IC50" <listed-path>`.
- This checkout may not contain `AGENTS.md` or a `.git` repository. Do not fail on missing `AGENTS.md`, and do not run `git status` as a completion check.
- Keep tool output small. Prefer Python snippets that print counts, selected keys, and short examples instead of dumping whole JSON/JSONL files.
- Do not inspect unrelated papers. Your write scope is only `papers/doi__10.1073_pnas.2210990119/`, `paper_packets/doi__10.1073_pnas.2210990119/`, `.miaobi-paper-review/workflows/doi__10.1073_pnas.2210990119/`, and paper-specific `reports/doi__10.1073_pnas.2210990119.*` gate outputs.
- A valid run must finish with a final assistant message. End with a concise final line starting `DONE doi__10.1073_pnas.2210990119` and include one of: `accepted_clean`, `accepted_with_cautions`, `needs_targeted_rework`, or `blocked_missing_primary_material`.
- Do not spend time discovering quality-gate script locations. The only gate commands for this checkout are the exact commands in "Gate Commands To Run" below.

## Immediate Contract

- Read the listed worker skill files before editing.
- Reopen source artifacts from paths; do not trust chat summaries as evidence.
- Fix only the owned layer(s): worker-2, worker-4, worker-6.
- Preserve separate layers: material packet, validator contract, semantic gate, publication-grade review.
- Do not mark the paper accepted while any blocking/major issue or open rework ticket remains.
- Write a rework response and rerun gates after repair; if quality is still not controllable, keep the ticket open.
- The initial queue has already been started once. Do not rerun the initial workflow/bootstrap unless the leader explicitly asks for a reset.

## Worker Skills To Load

- worker-2: `.codex/skills/paper-body-table-worker/SKILL.md` (body/table activity-toxicity repair)
- worker-4: `.codex/skills/paper-database-record-auditor/SKILL.md` (database record adjudication)
- worker-6: `.codex/skills/paper-adjudicator-review-worker/SKILL.md` (final adjudication and quality gate)

## Single Queue + Bounded Best-Effort Source Recovery Contract

- Treat `rework_context/doi__10.1073_pnas.2210990119/handoff_context.json` as the message packet and reopen the source/artifact paths listed there.
- Do best-effort recovery from paper-local materials: XML/NXML, PDF text/tables, OA package members, supplementary files, archives, spreadsheets, office files, images/OCR outputs, locator indexes, and linked database snapshots.
- Use local tools only where relevant to the blocker; prioritize sources that can change the gate result.
- Do not fabricate missing values. If sequence/activity/toxicity/mechanism/database evidence cannot be recovered from local material, write `unrecoverable_material_gaps` with `gap_code`, `source_paths_checked`, `tools_attempted`, `why_unrecoverable`, `impact`, `owner_worker`, and `blocks_publication_grade`.
- Stop after a bounded repair attempt. The controller caps the paper at 5 total rework attempts; if still uncontrollable, mark blocked/unrecoverable and move to the next paper instead of looping.

## Obtainable-Only Mode

- Success means: extract every value and claim that is supported by local material, then explicitly mark what local material cannot support.
- Do not keep chasing absent external supplements, unsupported scans, or figure-only exact values after the relevant local paths have been opened.
- If a blocker is a true material gap, write `unrecoverable_material_gaps` and leave the paper non-accepted; the controller will move to the next paper.
- Keep partial recoveries: supported activity/database/mechanism rows should remain recorded even when another layer is `source_conflict` or unresolved.


## Why The Previous QC Failed

- The framework test inventories real material but does not complete worker-6 source-reviewed adjudication.
- Linked database rows include source_conflict/database-only cases that must be preserved or resolved by source review.
- No parser-supported activity/toxicity rows were extracted; worker must inspect XML/PDF/prose/figures/supplements before acceptance.
- Codex owner-worker failed due to API/process/interruption infrastructure problems; controller retried 5 time(s), tagged the paper for later infrastructure recovery, and advanced.
- Codex owner-worker failed due to API/process/interruption infrastructure problems; controller retried 5 time(s), tagged the paper for later infrastructure recovery, and advanced.
- Codex owner-worker exited non-zero after bounded review, and strict gates still did not pass; controller retried 1 time(s), tagged the paper for later infrastructure recovery, and advanced. If the worker wrote partial artifacts, the after_worker gate reports above remain the scientific source of truth.
- The framework test inventories real material but does not complete worker-6 source-reviewed adjudication.
- Linked database rows include source_conflict/database-only cases that must be preserved or resolved by source review.
- No parser-supported activity/toxicity rows were extracted; worker must inspect XML/PDF/prose/figures/supplements before acceptance.

## Artifact Paths To Reopen

- packet_manifest: `paper_packets/doi__10.1073_pnas.2210990119/packet_manifest.json`
- locator_index: `paper_packets/doi__10.1073_pnas.2210990119/locators/locator_index.json`
- extraction_status: `paper_packets/doi__10.1073_pnas.2210990119/extraction/extraction_status.json`
- extraction_quality_report: `paper_packets/doi__10.1073_pnas.2210990119/extraction/extraction_quality_report.json`
- analysis_status: `paper_packets/doi__10.1073_pnas.2210990119/analysis/analysis_status.json`
- packet_activity: `paper_packets/doi__10.1073_pnas.2210990119/analysis/activity_toxicity_evidence.json`
- packet_database: `paper_packets/doi__10.1073_pnas.2210990119/analysis/database_record_audit.json`
- packet_mechanism: `paper_packets/doi__10.1073_pnas.2210990119/analysis/mechanism_evidence.json`
- packet_adjudication: `paper_packets/doi__10.1073_pnas.2210990119/analysis/adjudication_report.json`
- rework_requests: `paper_packets/doi__10.1073_pnas.2210990119/rework/rework_requests.jsonl`
- rework_responses: `paper_packets/doi__10.1073_pnas.2210990119/rework/rework_responses.jsonl`
- final_review_report: `papers/doi__10.1073_pnas.2210990119/final/review_report.json`
- final_activity: `papers/doi__10.1073_pnas.2210990119/final/activity_toxicity_evidence.json`
- final_database: `papers/doi__10.1073_pnas.2210990119/final/database_record_verification.json`
- final_mechanism: `papers/doi__10.1073_pnas.2210990119/final/mechanism_ontology_record.json`
- quality_feedback: `papers/doi__10.1073_pnas.2210990119/work/review/quality_feedback.json`
- workflow_context: `.miaobi-paper-review/workflows/doi__10.1073_pnas.2210990119/workflow_context.json`
- state_executions: `.miaobi-paper-review/workflows/doi__10.1073_pnas.2210990119/state_executions.jsonl`
- chat_messages: `.miaobi-paper-review/workflows/doi__10.1073_pnas.2210990119/chat_messages.jsonl`
- agent_logs: `.miaobi-paper-review/workflows/doi__10.1073_pnas.2210990119/agent_logs.jsonl`
- latest_complete_report: `reports/doi__10.1073_pnas.2210990119.complete_message_test_report.json`

## Gate Commands To Run

Use these exact commands after any repair. Do not try historical paths such as `paper-batch-orchestrator/scripts/...` or `workspace-guide/...`; those are not valid in this scoped checkout.

```bash
python .codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py --root . --manifest reports/doi__10.1073_pnas.2210990119.true_rework_queue_manifest.json --json > reports/doi__10.1073_pnas.2210990119.owner_worker.semantic_gate.json
python .codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py --root . --manifest reports/doi__10.1073_pnas.2210990119.true_rework_queue_manifest.json --json-out reports/doi__10.1073_pnas.2210990119.owner_worker.publication_quality.json
```

If the manifest path is absent, create `reports/doi__10.1073_pnas.2210990119.true_rework_queue_manifest.json` containing `{"paper_ids":["doi__10.1073_pnas.2210990119"]}` before running the gates.

## Required Output

1. Repair the owner-layer artifact(s) under the paper-local packet/final/work paths.
2. Update `paper_packets/doi__10.1073_pnas.2210990119/rework/rework_responses.jsonl` with what was checked and what remains.
3. Update `papers/doi__10.1073_pnas.2210990119/work/review/quality_feedback.json` if final QC still fails, with concrete `qc_failure_reasons`.
4. Rerun semantic and publication gates for this paper.
5. If gates still fail, create/keep a targeted rework ticket with owner worker, omission code, artifact path, and source paths to check.
6. If the local source cannot support the missing value after best effort, record `unrecoverable_material_gaps` and leave the paper non-accepted rather than retrying indefinitely.
