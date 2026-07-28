---
name: paper-adjudicator-review-worker
description: Strict worker-6 role for AMP three-layer curation; compares outputs from workers 1-5, preserves conflicts, sends targeted rework, and writes final database/activity/mechanism review artifacts.
---

# Paper Adjudicator Review Worker

Use this skill for `worker-6` in the `amp_three_layer_v2` six-worker workflow.

## Batch 2-Team hard gate

- Use `gpt-5.5` with `reasoning_effort=xhigh` whenever this worker is model-routed.
- Treat `paper_worker_v1.py run-role` as a schema scaffold only; worker-6 must independently compare workers 1-5 against primary sources before accepting.
- `review_report.json` must be paper-specific and include `reviewed_at`, `review_model: gpt-5.5`, `reasoning_effort: xhigh`, checked inputs, semantic QA checks, per-layer decision rationale, and a non-templated summary.
- `review_report.json` must include `publication_grade`, `validator_contract_passed`, `source_review_depth`, and `materials_exhausted`; absence of these fields is a hard semantic gate failure.
- If review text is generic, timestamps/model provenance are missing, accelerator/fallback events exist without source-reviewed repair, or semantic QA flags remain, write `needs_targeted_rework`.
- Worker-6 must prove deep retrieval, deep acquisition, and reliable result for
  the specific paper. Do not accept copied `final/` files, packet existence,
  `analysis_accepted`, validator success, or batch check success as evidence.
- If semantic gate or publication QA fails, close as `needs_targeted_rework` or
  `blocked_missing_primary_material`, not accepted.
- If bounded owner-worker attempts exhaust local recoverable materials, write
  `unrecoverable_material_gaps` plus concrete `qc_failure_reasons`, keep the
  paper non-publication-grade, and allow the controller to advance to the next
  paper instead of reopening the same blocker indefinitely.
- Durable rework must use `work/review/quality_feedback.json`, `final/review_report.json` `rework_targets`, and OMX team mailbox/state; native subagent notes or chat replies are not the production message bus.
- In two-queue mode, durable rework must also append structured tickets to the packet `rework/rework_requests.jsonl`, with `target_queue` set to `material_extraction`, `analysis`, or `adjudication`.


## Scope

Read:

- canonical outputs from workers 1-5.
- paper-local `source/paper.xml`, `source/paper.pdf`, OA/package archives, true supplementary assets, and merged database rows needed to adjudicate conflicts.
- `papers/<paper_id>/packet/` when two-queue packet mode is active.

Write only:

- `papers/<paper_id>/work/review/`
- `papers/<paper_id>/final/`
- `papers/<paper_id>/packet/analysis/` when two-queue packet mode is active
- `papers/<paper_id>/packet/final/` when two-queue packet mode is active
- `papers/<paper_id>/packet/rework/rework_requests.jsonl` when targeted rework is required
- `papers/<paper_id>/packet/rework/rework_responses.jsonl` only when closing an adjudication-owned ticket, or when appending a final adjudication closure for a repaired owner-lane ticket after independently verifying its contract against rebuilt final artifacts and strict gates

## Stable execution path

Use this command as a schema scaffold only, then independently source-review upstream evidence before acceptance:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <paper_id> --worker worker-6 --protocol amp_three_layer_v2
```

Expected canonical outputs:

- `papers/<paper_id>/work/review/adjudication_report.json`
- `papers/<paper_id>/work/review/quality_feedback.json`
- `papers/<paper_id>/final/database_record_verification.json`
- `papers/<paper_id>/final/activity_toxicity_evidence.json`
- `papers/<paper_id>/final/mechanism_ontology_record.json`
- `papers/<paper_id>/final/review_report.json`

## Required review provenance

`final/review_report.json` and `work/review/adjudication_report.json` must include `reviewed_at`, `review_model`, `reasoning_effort`, `source_reviewed: true`, `semantic_quality_checks`, `per_layer_decision_rationale`, `checked_inputs`, `caution_findings`, and `rework_targets`. A repeated template summary is a failure.

## Adjudication gates

Before accepting final outputs, verify:

- the packet manifest exists or a legacy-path compatibility mapping is explicit.
- material extraction status is complete or complete-with-gaps with nonblocking gaps only.
- database record statuses use the layer-1 vocabulary and unsupported rows remain unresolved.
- activity/toxicity rows preserve raw values, units, strain, assay conditions, and locators where available.
- mechanism ontology evidence class does not overclaim.
- cross-database conflicts are preserved.
- checked inputs prove XML/PDF/OA/supplement/database retrieval was exhausted or
  unresolved gaps are routed with durable tickets.
- analysis outputs were re-acquired from packet sources and database rows, not
  just copied from existing `work/` or `final/` artifacts.
- missing fields generate targeted rework to the owning worker.

Strict acceptance is not a file-presence check. Worker-6 must write
`needs_targeted_rework` plus concrete `rework_targets` when any hard gate fails:

- `worker-4`: record-level `unresolved_record` remains without a source-backed
  reason, `sequence_modified_not_normalized` lacks explicit modification
  evidence, or `source_verified` lacks a precise sequence/table/figure/supplement
  locator.
- `worker-2`: activity/toxicity rows are database-only, use generic labels such
  as `activity`, or lack endpoint/raw value/target/source locator core fields.
- `worker-3`: supplementary output is only inventory/linkage/runtime-limitations
  while XML or local assets show supplementary materials exist.
- `worker-5`: mechanism claims lack valid evidence classes, source locators, or
  direct assay types for `direct_mechanism`.

`source_conflict` can be a valid final curation outcome only when the conflict is
preserved as a caution with record identifiers and evidence context; do not hide
it by converting it to `source_verified`.

In two-queue mode, route rework by ownership:

- `target_queue: material_extraction` for missing XML/PDF/supplement/OCR/archive/table locators or absent database-row snapshots.
- `target_queue: analysis` for incorrect database audit, activity/toxicity interpretation, mechanism classification, or conflict handling.
- `target_queue: adjudication` for final review/report provenance or summary defects.

Do not reopen the material queue for a scientific disagreement when packet
evidence is already sufficient; send that to the analysis queue.

## Rules

- Do not resolve conflicts by majority vote across databases.
- Do not overwrite worker evidence to hide uncertainty.
- Do not claim completion when source locators are missing for `source_verified` records.
- Write targeted `quality_feedback.json` whenever a lane must be repaired.
- Write packet rework tickets whenever split queues are active.
- An owner worker repairs its own ticket first. Worker-6 may append the terminal
  `closed_repaired` adjudication response for that owner-lane ticket only after
  independently checking the ticket contract, rebuilding both final mirrors,
  passing packet, semantic, and publication gates without allow flags, and
  confirming that no hard rework target remains. The response must identify
  worker-6, set `analysis_can_resume: true`, and preserve the verified artifacts,
  final counts, and gate results. Runtime closure also requires exactly one
  terminal response for the ticket, both `status` and `response_status` equal to
  `closed_repaired`, `ticket_contract_evidence.overall_contract_pass: true`,
  existing JSON gate artifacts, and byte-identical paper/packet final mirrors.
  The gate artifacts must use their formal pass schemas, bind to the correct
  single-paper manifest and current final counts, and be newer than the terminal
  response/final rebuild. Every named owner worker must already have an
  evidence-bearing, nonterminal `analysis_can_resume` repair response; owner
  responses never close the ticket. Otherwise leave the ticket open.
- Run or satisfy `paper-batch-orchestrator/scripts/semantic_three_layer_gate.py` before final publication-grade acceptance.
- Treat any terminal-path `--allow-findings`, `--allow-risk`, or `|| true` gate
  result as diagnostic only until a strict pass clears the paper.
