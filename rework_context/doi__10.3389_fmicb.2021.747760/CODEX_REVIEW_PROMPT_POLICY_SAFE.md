# Policy-Safe Minimal Codex Re-review Prompt

Review exactly one paper: `doi__10.3389_fmicb.2021.747760`.

This is a source-backed curation repair, not a request to design, optimize, or provide operational biomedical methods. Keep biomedical source content out of the chat/terminal.

## Mandatory Narrow Scope

- Read only the worker skill files listed below and `rework_context/doi__10.3389_fmicb.2021.747760/policy_safe_handoff_context.json`.
- Use that JSON as a path index. Open only paper-local artifact/source paths named there.
- Do not run broad repository searches, `git status`, unbounded `find`, or large `cat`/JSONL dumps.
- If search is needed, scope to one listed file/directory and print only counts/keys/locator IDs, not source prose.
- Your write scope is only `papers/doi__10.3389_fmicb.2021.747760/`, `paper_packets/doi__10.3389_fmicb.2021.747760/`, `.miaobi-paper-review/workflows/doi__10.3389_fmicb.2021.747760/`, and `reports/doi__10.3389_fmicb.2021.747760.*`.

## Content-Safe Output Rules

- Do not print or quote peptide sequences, detailed protocols, dose-response prose, antiviral/therapeutic narrative text, or long assay snippets.
- Do not paste source text into the final answer. Put recovered evidence in the required JSON artifacts with locators.
- Terminal output should show only short status lines, counts, field names, issue codes, and gate pass/fail results.
- If a local source cannot be reviewed safely or cannot support the missing field, keep the paper non-accepted and record the blocker; do not guess.

## Worker Skills To Load

- worker-2: `.codex/skills/paper-body-table-worker/SKILL.md` (body/table activity-toxicity repair)
- worker-5: `.codex/skills/paper-mechanism-ontology-worker/SKILL.md` (mechanism ontology repair)
- worker-6: `.codex/skills/paper-adjudicator-review-worker/SKILL.md` (final adjudication and quality gate)

## Repair Target

- Owner layer(s): worker-2, worker-5, worker-6.
- Main objective: repair locally supportable activity/toxicity table evidence and then rerun worker-4/worker-6 adjudication as needed.
- Preserve database conflicts and database-only rows; do not convert them to source-verified without a primary-source locator.
- Do not mark accepted while open hard rework targets or strict gate issues remain.
- Stop after a bounded best-effort pass; controller cap is `5` attempts.

## Artifact Paths To Reopen

- packet_manifest: `paper_packets/doi__10.3389_fmicb.2021.747760/packet_manifest.json`
- locator_index: `paper_packets/doi__10.3389_fmicb.2021.747760/locators/locator_index.json`
- extraction_status: `paper_packets/doi__10.3389_fmicb.2021.747760/extraction/extraction_status.json`
- extraction_quality_report: `paper_packets/doi__10.3389_fmicb.2021.747760/extraction/extraction_quality_report.json`
- analysis_status: `paper_packets/doi__10.3389_fmicb.2021.747760/analysis/analysis_status.json`
- packet_activity: `paper_packets/doi__10.3389_fmicb.2021.747760/analysis/activity_toxicity_evidence.json`
- packet_database: `paper_packets/doi__10.3389_fmicb.2021.747760/analysis/database_record_audit.json`
- packet_mechanism: `paper_packets/doi__10.3389_fmicb.2021.747760/analysis/mechanism_evidence.json`
- packet_adjudication: `paper_packets/doi__10.3389_fmicb.2021.747760/analysis/adjudication_report.json`
- rework_requests: `paper_packets/doi__10.3389_fmicb.2021.747760/rework/rework_requests.jsonl`
- rework_responses: `paper_packets/doi__10.3389_fmicb.2021.747760/rework/rework_responses.jsonl`
- final_review_report: `papers/doi__10.3389_fmicb.2021.747760/final/review_report.json`
- final_activity: `papers/doi__10.3389_fmicb.2021.747760/final/activity_toxicity_evidence.json`
- final_database: `papers/doi__10.3389_fmicb.2021.747760/final/database_record_verification.json`
- final_mechanism: `papers/doi__10.3389_fmicb.2021.747760/final/mechanism_ontology_record.json`
- quality_feedback: `papers/doi__10.3389_fmicb.2021.747760/work/review/quality_feedback.json`
- workflow_context: `.miaobi-paper-review/workflows/doi__10.3389_fmicb.2021.747760/workflow_context.json`
- state_executions: `.miaobi-paper-review/workflows/doi__10.3389_fmicb.2021.747760/state_executions.jsonl`
- chat_messages: `.miaobi-paper-review/workflows/doi__10.3389_fmicb.2021.747760/chat_messages.jsonl`
- agent_logs: `.miaobi-paper-review/workflows/doi__10.3389_fmicb.2021.747760/agent_logs.jsonl`
- latest_complete_report: `reports/doi__10.3389_fmicb.2021.747760.complete_message_test_report.json`

## Gate Commands To Run

Use exactly:

```bash
python .codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py --root . --manifest reports/doi__10.3389_fmicb.2021.747760.true_rework_queue_manifest.json --json > reports/doi__10.3389_fmicb.2021.747760.owner_worker.semantic_gate.json
python .codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py --root . --manifest reports/doi__10.3389_fmicb.2021.747760.true_rework_queue_manifest.json --json-out reports/doi__10.3389_fmicb.2021.747760.owner_worker.publication_quality.json
```

If the manifest path is absent, create `reports/doi__10.3389_fmicb.2021.747760.true_rework_queue_manifest.json` containing `{"paper_ids":["doi__10.3389_fmicb.2021.747760"]}`.

## Required Local Writes

1. Update paper-local final/work artifacts for only the source-supported repair.
2. Append `paper_packets/doi__10.3389_fmicb.2021.747760/rework/rework_responses.jsonl` with paths checked, fields repaired, and remaining blockers.
3. If gates still fail, update `papers/doi__10.3389_fmicb.2021.747760/work/review/quality_feedback.json` with concrete codes/owners/artifact paths, not long source prose.
4. Leave unresolved or unsupported facts as conflicts/gaps; do not fabricate values.
5. End final assistant message with `DONE doi__10.3389_fmicb.2021.747760 <status>` where status is one of `accepted_clean`, `accepted_with_cautions`, `needs_targeted_rework`, `blocked_missing_primary_material`.
