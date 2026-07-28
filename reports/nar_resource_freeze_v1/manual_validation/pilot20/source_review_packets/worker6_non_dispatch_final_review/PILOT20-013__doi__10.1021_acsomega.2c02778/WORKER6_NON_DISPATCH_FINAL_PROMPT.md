# Worker-6 Final Review For Non-Dispatch Pilot20 Paper

You are worker-6 (`paper-adjudicator-review-worker`) for one pilot20 paper that never entered owner dispatch.

## Hard constraints

- Use `gpt-5.5` with `reasoning_effort=xhigh`; runner command provides this. Treat runner command/header as model/effort provenance unless contradicted.
- Preserve conflicts, cautions, database-only, unresolved, and material gaps.
- Do not mark `accepted_clean` in this pilot.
- Do not mark publication-grade true if hard rework, non-standard mechanism evidence classes in accepted artifacts, missing material, or open rework remains.
- Do not invent missing supplement/PDF/XML evidence.
- If the only prior blocker was model self-proof and source/material/ontology gates now pass, you may write `accepted_with_cautions` with preserved cautions.
- If mechanism evidence classes use labels outside the five-class ontology, repair only if the local source evidence and claim text make the mapping safe; otherwise write `needs_targeted_rework` with concrete owner target.

Allowed mechanism evidence classes: `direct_mechanism`, `phenotype_supported`, `inferred_mechanism`, `computational_only`, `unknown_or_not_tested`.

## Input

- pilot_sample_id: `PILOT20-013`
- paper_id: `doi__10.1021_acsomega.2c02778`
- readjudicated_decision: `needs_targeted_rework`
- readjudication_reason_code: `worker6_text_mentions_rework`
- original_decision: `unverifiable_best_effort`
- audit_record_id: `doi__10.1021_acsomega.2c02778:database_audit:1`
- true review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-013__doi__10.1021_acsomega.2c02778/true_review_result.json`
- review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-013__doi__10.1021_acsomega.2c02778`
- current paper final dir: `papers/doi__10.1021_acsomega.2c02778/final/`
- packet final dir: `paper_packets/doi__10.1021_acsomega.2c02778/final/`
- write response JSON: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_non_dispatch_final_review/PILOT20-013__doi__10.1021_acsomega.2c02778/worker6_non_dispatch_final_response.json`
- response schema: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_non_dispatch_final_review/PILOT20-013__doi__10.1021_acsomega.2c02778/worker6_non_dispatch_final_response.schema.json`

Read these instructions before editing:

1. `.codex/skills/amp-three-layer-curation/SKILL.md`
2. `.codex/skills/paper-adjudicator-review-worker/SKILL.md`
3. `.codex/skills/amp-three-layer-curation/references/publication-grade-source-review.md`
4. `.codex/skills/amp-three-layer-curation/references/publication-grade-quality-gate.md`
5. `.codex/skills/amp-three-layer-curation/references/team-rework-message-contract.md`
6. `.codex/skills/amp-three-layer-curation/references/two-queue-paper-packet-contract.md`

## Task

1. Re-open the true review result, source review packet, packet materials, current final artifacts, and relevant source locators/database rows.
2. Decide whether the previous non-dispatch state can be finalized or must remain nonterminal.
3. For safe acceptance:
   - Mirror/repair mechanism artifacts so accepted files use only the five allowed evidence classes.
   - Update `papers/doi__10.1021_acsomega.2c02778/final/review_report.json` and `paper_packets/doi__10.1021_acsomega.2c02778/final/review_report.json` with worker-6 provenance, checked inputs, semantic QA summary, preserved cautions, and zero hard rework targets.
   - Highest positive decision allowed is `accepted_with_cautions`.
4. For nonterminal outcomes:
   - Write/update review reports as `needs_targeted_rework` or `blocked_missing_primary_material`, `publication_grade: false`, and concrete `rework_targets` / `unrecoverable_material_gaps`.
   - Include owner worker, artifact path, failing claim/row/record, failure code, source evidence to check, required action, and acceptance check.
5. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_non_dispatch_final_review/PILOT20-013__doi__10.1021_acsomega.2c02778/worker6_non_dispatch_final_response.json` matching schema with `final_decision`, `files_updated`, `qc_summary`, `remaining_blockers`, and `worker6_followup`.

Use Python/JSON tools if helpful. Keep final response short and point to the response JSON.
