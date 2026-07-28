# Validation420 True Source Review Prompt

You are a fresh Codex CLI worker-6 reviewer for AMP Evidence Atlas / NAR Resource v1.
This packet reviews one paper and all validation-manifest rows sampled for that paper.

## Required model/provenance

- The runner launches `codex exec -m gpt-5.5 -c model_reasoning_effort="xhigh"`.
- Record `review_model: "gpt-5.5"` and `reasoning_effort: "xhigh"` in the result.
- Treat the runner command/header as sufficient model/effort provenance unless a runtime status contradicts it.

## Working directory

`/root/work/抗菌肽/数据库/batch/4-team`

## Packet

- paper_id: `doi__10.3390_antibiotics9080457`
- review_sample_id: `V420P0177`
- sampled validation rows for this paper: `1`
- packet directory: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0177__doi__10.3390_antibiotics9080457`
- validation samples: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0177__doi__10.3390_antibiotics9080457/validation_samples.json`
- release rows: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0177__doi__10.3390_antibiotics9080457/release_rows.json`
- sample final records: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0177__doi__10.3390_antibiotics9080457/sample_final_records.json`
- source locator hints: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0177__doi__10.3390_antibiotics9080457/source_locator_hints.json`
- material inventory: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0177__doi__10.3390_antibiotics9080457/material_inventory.json`
- result schema: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0177__doi__10.3390_antibiotics9080457/true_review_result.schema.json`
- write result JSON: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0177__doi__10.3390_antibiotics9080457/true_review_result.json`
- if hard failures exist, write tickets JSONL: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0177__doi__10.3390_antibiotics9080457/rework_tickets.jsonl`

## Instructions to read before deciding

1. `.codex/skills/amp-three-layer-curation/SKILL.md`
2. `.codex/skills/paper-adjudicator-review-worker/SKILL.md`
3. `.codex/skills/amp-three-layer-curation/references/publication-grade-source-review.md`
4. `.codex/skills/amp-three-layer-curation/references/publication-grade-quality-gate.md`
5. `.codex/skills/amp-three-layer-curation/references/team-rework-message-contract.md`
6. `.codex/skills/amp-three-layer-curation/references/two-queue-paper-packet-contract.md`
7. Owner skills if relevant: `paper-database-record-auditor`, `paper-body-table-worker`, `paper-supp-evidence-worker`, `paper-mechanism-ontology-worker`.

## Review task

Use only local materials; do not browse the web.

1. Re-open `material_inventory.json`, the packet sources, final artifacts, database JSONL rows, and source locators relevant to the sampled rows.
2. For every row in `validation_samples.json`, decide whether the row is source-backed, caution-preserving, repairable, blocked by missing material, or only best-effort unverifiable.
3. Check layer 1 database identity/status, layer 2 activity/toxicity row-level evidence, and layer 3 mechanism ontology where relevant to sampled rows.
4. Act as worker-6 for this paper: preserve conflicts and uncertainty; do not convert database-only or conflict rows into clean source_verified.
5. Do not edit canonical `papers/<paper_id>/final/` artifacts in this phase. This is validation/source-review evidence collection. Hard failures must be tickets, not silent edits.

## Decision rules

Each `sample_row_decisions[]` item should include:

- `sample_id`
- `audit_record_id`
- `row_decision`: `confirmed`, `confirmed_with_caution`, `needs_targeted_rework`, `blocked_missing_primary_material`, `unverifiable_best_effort`, or `not_applicable`
- `evidence_summary`
- `locators_checked`
- `cautions`
- `rework_target_ids`

Use one paper-level `final_decision`:

- `accepted_clean`: all sampled rows confirmed, no hard rework and no cautions.
- `accepted_with_cautions`: no hard rework, but conflicts/cautions/material limits are preserved.
- `needs_targeted_rework`: one or more repairable defects exist.
- `blocked_missing_primary_material`: required local primary/supplementary material is absent/unreadable after best effort.
- `unverifiable_best_effort`: bounded effort could not decide; explain exactly what was inspected and why it remains unresolved.
- `deferred_not_safe_to_edit`: runner/source inconsistency prevents safe judgement.

Hard failures requiring `needs_targeted_rework` include missing primary-source locator for `source_verified`, unsupported unresolved/database-only reason, sentence-fragment targets, generic endpoints, MIC-like rows without unit/rationale, non-standard mechanism evidence classes in accepted outputs, direct mechanism without direct assay type, templated worker-6 review, missing provenance, or open hard rework targets.

If any row has `needs_targeted_rework` or `blocked_missing_primary_material`, write `rework_tickets.jsonl` with durable tickets containing target_queue, owner worker, reason, requested_outputs, blocks, and created_at.

Write `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0177__doi__10.3390_antibiotics9080457/true_review_result.json` as JSON matching the schema. Keep final chat response short and point to the result path.
