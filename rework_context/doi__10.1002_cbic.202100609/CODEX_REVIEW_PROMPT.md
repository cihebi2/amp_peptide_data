# Codex CLI Re-review Prompt

You are a new Codex CLI paper-review worker for Batch 4-Team. Re-review exactly one paper: `doi__10.1002_cbic.202100609`.

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

- Treat `rework_context/doi__10.1002_cbic.202100609/handoff_context.json` as the message packet and reopen the source/artifact paths listed there.
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

- review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
- activity parser quality issue: some extracted rows use peptide IDs/method labels/properties as target species or MIC rows, so row-level activity needs repair before acceptance
- database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
- material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion
- Supplementary Table S5 was recovered from the local supplement PDF text and structured into 336 row-level MIC records covering 48 peptides across seven bacterial strains.
- Figure 4 is available locally as an image bar chart plus caption/method text, but no structured primary source table provides exact HepG2/HEK293 percentages; exact database percentages cannot be source-promoted without fabrication.
- Database MIC rows matching Supplementary Table S5 were source-verified, but HEK293/HepG2 cytotoxicity/killing rows remain source_conflict because exact Figure 4 percentages are not locally recoverable.
- Bounded source recovery exhausted local materials for the remaining Figure 4 exact-value gap, so worker-6 must keep the paper non-publication-grade and non-accepted.
- Obtainable-only mode: local source-supported evidence was preserved, but the remaining blocker is documented as not recoverable from local materials; controller marked the paper blocked_after_best_effort and advanced.
- Supplementary Table S5 was recovered from the local supplement PDF text and structured into 336 row-level MIC records covering 48 peptides across seven bacterial strains.
- Figure 4 is available locally as an image bar chart plus caption/method text, but no structured primary source table provides exact HepG2/HEK293 percentages; exact database percentages cannot be source-promoted without fabrication.
- Database MIC rows matching Supplementary Table S5 were source-verified, but HEK293/HepG2 cytotoxicity/killing rows remain source_conflict because exact Figure 4 percentages are not locally recoverable.

## Artifact Paths To Reopen

- packet_manifest: `paper_packets/doi__10.1002_cbic.202100609/packet_manifest.json`
- locator_index: `paper_packets/doi__10.1002_cbic.202100609/locators/locator_index.json`
- extraction_status: `paper_packets/doi__10.1002_cbic.202100609/extraction/extraction_status.json`
- extraction_quality_report: `paper_packets/doi__10.1002_cbic.202100609/extraction/extraction_quality_report.json`
- analysis_status: `paper_packets/doi__10.1002_cbic.202100609/analysis/analysis_status.json`
- packet_activity: `paper_packets/doi__10.1002_cbic.202100609/analysis/activity_toxicity_evidence.json`
- packet_database: `paper_packets/doi__10.1002_cbic.202100609/analysis/database_record_audit.json`
- packet_mechanism: `paper_packets/doi__10.1002_cbic.202100609/analysis/mechanism_evidence.json`
- packet_adjudication: `paper_packets/doi__10.1002_cbic.202100609/analysis/adjudication_report.json`
- rework_requests: `paper_packets/doi__10.1002_cbic.202100609/rework/rework_requests.jsonl`
- rework_responses: `paper_packets/doi__10.1002_cbic.202100609/rework/rework_responses.jsonl`
- final_review_report: `papers/doi__10.1002_cbic.202100609/final/review_report.json`
- final_activity: `papers/doi__10.1002_cbic.202100609/final/activity_toxicity_evidence.json`
- final_database: `papers/doi__10.1002_cbic.202100609/final/database_record_verification.json`
- final_mechanism: `papers/doi__10.1002_cbic.202100609/final/mechanism_ontology_record.json`
- quality_feedback: `papers/doi__10.1002_cbic.202100609/work/review/quality_feedback.json`
- workflow_context: `.miaobi-paper-review/workflows/doi__10.1002_cbic.202100609/workflow_context.json`
- state_executions: `.miaobi-paper-review/workflows/doi__10.1002_cbic.202100609/state_executions.jsonl`
- chat_messages: `.miaobi-paper-review/workflows/doi__10.1002_cbic.202100609/chat_messages.jsonl`
- agent_logs: `.miaobi-paper-review/workflows/doi__10.1002_cbic.202100609/agent_logs.jsonl`
- latest_complete_report: `reports/doi__10.1002_cbic.202100609.complete_message_test_report.json`
- latest_capped_rework_report: `reports/doi__10.1002_cbic.202100609.capped_rework_test_report.json`

## Required Output

1. Repair the owner-layer artifact(s) under the paper-local packet/final/work paths.
2. Update `paper_packets/doi__10.1002_cbic.202100609/rework/rework_responses.jsonl` with what was checked and what remains.
3. Update `papers/doi__10.1002_cbic.202100609/work/review/quality_feedback.json` if final QC still fails, with concrete `qc_failure_reasons`.
4. Rerun semantic and publication gates for this paper.
5. If gates still fail, create/keep a targeted rework ticket with owner worker, omission code, artifact path, and source paths to check.
6. If the local source cannot support the missing value after best effort, record `unrecoverable_material_gaps` and leave the paper non-accepted rather than retrying indefinitely.
