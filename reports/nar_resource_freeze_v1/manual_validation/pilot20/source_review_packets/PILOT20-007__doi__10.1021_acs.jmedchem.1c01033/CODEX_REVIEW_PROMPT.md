# Pilot20 True Source Review Prompt

You are a fresh Codex CLI reviewer for AMP Evidence Atlas / NAR Resource v1.
This is a true source-review packet, not the previous automated structural pass.

## Required model/provenance

- Use `gpt-5.5` with `model_reasoning_effort=xhigh`.
- Record `review_model: "gpt-5.5"` and `reasoning_effort: "xhigh"` in the result.
- If you cannot prove model/effort, write `decision: "unverifiable_best_effort"` and explain the limitation.

## Working directory

`/root/work/抗菌肽/数据库/batch/4-team`

## Packet

- packet directory: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033`
- validation sample: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/validation_sample.json`
- release row: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/release_row.json`
- sample final record: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/sample_final_record.json`
- source locator hints: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/source_locator_hints.json`
- material inventory: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/material_inventory.json`
- result schema: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/true_review_result.schema.json`
- write final result to: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/true_review_result.json`
- if hard failure, write rework ticket to: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/rework_ticket.json`

## Sample identity

- pilot_sample_id: `PILOT20-007`
- paper_id: `doi__10.1021_acs.jmedchem.1c01033`
- database/source_id: `dbAMP / dbAMP:dbAMP_32907`
- audit_record_id: `doi__10.1021_acs.jmedchem.1c01033:database_audit:239`
- status under review: `source_conflict`
- categories: `activity_value_or_unit;database_only_no_primary_source;row_granularity;sequence_or_modification;target_or_organism`
- owner lanes: `worker-4/database_record_auditor, worker-2/main_text_assay_extractor, worker-6/adjudicator_review`

Current packet signals to verify, not trust blindly:

- material_queue_status: `material_extracted_with_gaps`
- analysis_queue_status: `analysis_source_reviewed_accepted_with_cautions`
- existing final review_status: `accepted_with_cautions`
- existing publication_grade: `True`
- known risks: `material_queue_status_contains_gaps; packet_manifest_has_test_scope_note; packet_rework_requests_present; paper_quality_feedback_present`

## Skills/instructions to read before reviewing

Read these local files yourself before making a terminal decision:

1. `.codex/skills/amp-three-layer-curation/SKILL.md`
2. `.codex/skills/amp-three-layer-curation/references/publication-grade-source-review.md`
3. `.codex/skills/amp-three-layer-curation/references/publication-grade-quality-gate.md`
4. `.codex/skills/amp-three-layer-curation/references/team-rework-message-contract.md`
5. `.codex/skills/amp-three-layer-curation/references/two-queue-paper-packet-contract.md`
6. `.codex/skills/paper-adjudicator-review-worker/SKILL.md`
7. If the owner lane is worker-4, read `.codex/skills/paper-database-record-auditor/SKILL.md`.
8. If the owner lane includes worker-2/3/5, read the corresponding worker skill under `.codex/skills/`.

## Review task

Perform a best-effort source review for this one sampled audit row and its
paper-level final artifacts. Use only local materials; do not browse the web.

Do all of the following:

1. Re-open `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/material_inventory.json` and verify which XML/PDF/OA/supplement/database-row surfaces actually exist.
2. Re-open the packet sources referenced by source locators, especially XML tables/sections, PDF text, supplementary index/tables/text, and database JSONL rows.
3. Verify the sampled release row against `sample_final_record.json` and the primary material.
4. For layer 1, decide whether the status `source_conflict` is justified. Do not turn conflicts into clean source_verified.
5. For layer 2, spot-check whether activity/toxicity values, units, endpoint, target species/strain, and locators are source-backed when relevant to this row.
6. For layer 3, check whether mechanism claims stay in the correct evidence class and direct mechanisms have direct assay types and locators.
7. Act as worker-6 for this sample: decide whether the existing final artifact can be confirmed, must be cautioned, needs targeted rework, is blocked by missing primary material, or is only best-effort unverifiable.

## Decision rules

Use exactly one `decision` value:

- `pass_source_review`: sampled row and relevant layers are source-backed; no blocking cautions remain for this sample.
- `accepted_with_cautions_confirmed`: no hard repair is needed, but source conflict, database-only, unresolved, material-gap, or non-clean caution remains and must be preserved.
- `needs_targeted_rework`: a repairable worker-owned defect exists. Write `rework_targets`.
- `blocked_missing_primary_material`: source/supplement/raw material required for this sample is absent or unreadable after best effort.
- `unverifiable_best_effort`: you made a bounded best effort but cannot decide; explain what was inspected and why it remains unresolved. Do not loop indefinitely.

Hard failures requiring `needs_targeted_rework` include:

- `source_verified` without primary-source locator support.
- unresolved/database-only status without a source-backed reason or material-gap evidence.
- activity rows with sentence-fragment target/species, generic endpoint, missing raw value, missing raw unit for MIC-like rows, or missing locator.
- mechanism claims without claim_id, claim_text, evidence_class, locator, or direct assay type for direct mechanisms.
- templated worker-6 review, missing reviewed_at/model/reasoning provenance, or open rework targets.
- copied/fallback artifacts accepted without fresh source-review evidence.

## Output requirements

Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/true_review_result.json` as JSON matching `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/true_review_result.schema.json`.

If `decision` is `needs_targeted_rework` or `blocked_missing_primary_material`, also write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-007__doi__10.1021_acs.jmedchem.1c01033/rework_ticket.json` with:

- `ticket_id`
- `paper_id`
- `audit_record_id`
- `target_queue`: one of `material_extraction`, `analysis`, `adjudication`
- `severity`: `blocking`, `major`, `minor`, or `caution`
- `requested_by`: `pilot20_true_source_review`
- `reason`
- `requested_outputs`
- `blocks`
- `created_at`

Keep evidence concise: cite paths and locators; do not copy long source text.
If exact source text is needed, quote only short snippets and prefer locator IDs.

Final chat response should be brief and point to the JSON result path.
