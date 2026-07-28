# Codex CLI Re-review Prompt

You are a new Codex CLI paper-review worker for Batch 4-Team. Re-review exactly one paper: `doi__10.1039_c8ra08065h`.

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

- Treat `rework_context/doi__10.1039_c8ra08065h/handoff_context.json` as the message packet and reopen the source/artifact paths listed there.
- Do best-effort recovery from paper-local materials: XML/NXML, PDF text/tables, OA package members, supplementary files, archives, spreadsheets, office files, images/OCR outputs, locator indexes, and linked database snapshots.
- Use local tools only where relevant to the blocker; prioritize sources that can change the gate result.
- Do not fabricate missing values. If sequence/activity/toxicity/mechanism/database evidence cannot be recovered from local material, write `unrecoverable_material_gaps` with `gap_code`, `source_paths_checked`, `tools_attempted`, `why_unrecoverable`, `impact`, `owner_worker`, and `blocks_publication_grade`.
- Stop after a bounded repair attempt. The controller caps the paper at 3 total rework attempts; if still uncontrollable, mark blocked/unrecoverable and move to the next paper instead of looping.

## Obtainable-Only Mode

- Success means: extract every value and claim that is supported by local material, then explicitly mark what local material cannot support.
- Do not keep chasing absent external supplements, unsupported scans, or figure-only exact values after the relevant local paths have been opened.
- If a blocker is a true material gap, write `unrecoverable_material_gaps` and leave the paper non-accepted; the controller will move to the next paper.
- Keep partial recoveries: supported activity/database/mechanism rows should remain recorded even when another layer is `source_conflict` or unresolved.


## Why The Previous QC Failed

- The framework test inventories real material but does not complete worker-6 source-reviewed adjudication.
- Linked database rows include source_conflict/database-only cases that must be preserved or resolved by source review.
- One or more activity-bearing tables could not be safely parsed into target/entity/value rows.
- No parser-supported activity/toxicity rows were extracted; worker must inspect XML/PDF/prose/figures/supplements before acceptance.
- The framework test inventories real material but does not complete worker-6 source-reviewed adjudication.
- Linked database rows include source_conflict/database-only cases that must be preserved or resolved by source review.
- One or more activity-bearing tables could not be safely parsed into target/entity/value rows.
- No parser-supported activity/toxicity rows were extracted; worker must inspect XML/PDF/prose/figures/supplements before acceptance.

## Artifact Paths To Reopen

- packet_manifest: `paper_packets/doi__10.1039_c8ra08065h/packet_manifest.json`
- locator_index: `paper_packets/doi__10.1039_c8ra08065h/locators/locator_index.json`
- extraction_status: `paper_packets/doi__10.1039_c8ra08065h/extraction/extraction_status.json`
- extraction_quality_report: `paper_packets/doi__10.1039_c8ra08065h/extraction/extraction_quality_report.json`
- analysis_status: `paper_packets/doi__10.1039_c8ra08065h/analysis/analysis_status.json`
- packet_activity: `paper_packets/doi__10.1039_c8ra08065h/analysis/activity_toxicity_evidence.json`
- packet_database: `paper_packets/doi__10.1039_c8ra08065h/analysis/database_record_audit.json`
- packet_mechanism: `paper_packets/doi__10.1039_c8ra08065h/analysis/mechanism_evidence.json`
- packet_adjudication: `paper_packets/doi__10.1039_c8ra08065h/analysis/adjudication_report.json`
- rework_requests: `paper_packets/doi__10.1039_c8ra08065h/rework/rework_requests.jsonl`
- rework_responses: `paper_packets/doi__10.1039_c8ra08065h/rework/rework_responses.jsonl`
- final_review_report: `papers/doi__10.1039_c8ra08065h/final/review_report.json`
- final_activity: `papers/doi__10.1039_c8ra08065h/final/activity_toxicity_evidence.json`
- final_database: `papers/doi__10.1039_c8ra08065h/final/database_record_verification.json`
- final_mechanism: `papers/doi__10.1039_c8ra08065h/final/mechanism_ontology_record.json`
- quality_feedback: `papers/doi__10.1039_c8ra08065h/work/review/quality_feedback.json`
- workflow_context: `.miaobi-paper-review/workflows/doi__10.1039_c8ra08065h/workflow_context.json`
- state_executions: `.miaobi-paper-review/workflows/doi__10.1039_c8ra08065h/state_executions.jsonl`
- chat_messages: `.miaobi-paper-review/workflows/doi__10.1039_c8ra08065h/chat_messages.jsonl`
- agent_logs: `.miaobi-paper-review/workflows/doi__10.1039_c8ra08065h/agent_logs.jsonl`
- latest_complete_report: `reports/doi__10.1039_c8ra08065h.complete_message_test_report.json`

## Required Output

1. Repair the owner-layer artifact(s) under the paper-local packet/final/work paths.
2. Update `paper_packets/doi__10.1039_c8ra08065h/rework/rework_responses.jsonl` with what was checked and what remains.
3. Update `papers/doi__10.1039_c8ra08065h/work/review/quality_feedback.json` if final QC still fails, with concrete `qc_failure_reasons`.
4. Rerun semantic and publication gates for this paper.
5. If gates still fail, create/keep a targeted rework ticket with owner worker, omission code, artifact path, and source paths to check.
6. If the local source cannot support the missing value after best effort, record `unrecoverable_material_gaps` and leave the paper non-accepted rather than retrying indefinitely.
