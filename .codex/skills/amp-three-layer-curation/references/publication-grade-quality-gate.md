# Publication-Grade AMP Three-Layer Quality Gate

Use this reference for batch/2-team skill work. The goal is not validator-contract completion; the goal is per-paper source-reviewed, human-level, publication-grade curation.

## Mandatory Runtime Standard

- Use `gpt-5.5` with `xhigh` reasoning for substantive source review, adjudication, repair decisions, and quality-gate redesign.
- If the runtime cannot launch or run the responsible reviewer with `gpt-5.5` and `xhigh`, mark the paper or batch as blocked by `model_capability_mismatch`; do not silently downgrade.
- Deterministic `run-role` output is only a schema scaffold. It may seed fields, but final acceptance requires source-reviewed refinement from paper-local XML/PDF/OA package/supplements and merged database rows.
- Use `omx team` state, worker inboxes, task files, and `omx team api ... --json`
  for production worker handoffs. Native subagents may support bounded
  diagnostic spot checks only; they are not a substitute for durable
  worker-to-worker message passing, blocker tracking, or acceptance state.

## Publication-Grade Completion Definition

A paper is publication-grade complete only when all three layers are source-reviewed and worker-6 has independently adjudicated them:

0. **Deep retrieval and acquisition**
   - Material retrieval has exhausted XML, PDF, OA package, supplementary,
     archive, OCR/office, figure/table, and database-row surfaces, or has
     durable gap evidence for each unavailable source.
   - Analysis acquisition has re-opened the packet and database rows for this
     paper. Prior `work/` or `final/` JSON may be compared, but cannot be copied
     forward as acceptance without source-review provenance.
1. **Layer 1 database record verification**
   - Every linked APD6/DBAASP/DRAMP record has a status: `source_verified`, `source_conflict`, `database_only_no_primary_source`, `sequence_modified_not_normalized`, or `unresolved_record`.
   - `source_verified` requires a primary-source locator to sequence/name/modification evidence, not just a database link.
   - Cross-database disagreement is preserved as conflict/caution; never smooth by majority vote.
2. **Layer 2 activity/toxicity evidence**
   - Rows are source-located and row-level, not prose summaries.
   - Core fields: endpoint, raw value, raw unit or explicit not-reported reason, target species/class/strain when reported, assay conditions when reported, source locator.
   - Hard failures: sentence-fragment species (`The plot`, `In this`, `Defensins constitute`), generic endpoint labels (`activity`) where a concrete endpoint is recoverable, database-only rows treated as primary evidence, MIC-like rows without unit or table-level unit locator.
   - A no-primary-assay paper must explicitly say no primary activity/toxicity
     rows were found; it must not manufacture MIC-like rows from background
     text, peptide names, figure captions, or cited-paper comparisons.
3. **Layer 3 mechanism ontology**
   - Every claim has `claim_id`, `claim_text`, evidence class, source locator, and direct assay types for `direct_mechanism`.
   - Evidence classes remain distinct: `direct_mechanism`, `phenotype_supported`, `inferred_mechanism`, `computational_only`, `unknown_or_not_tested`.
   - Do not promote computational, family-based, charge/hydrophobicity, or discussion-only claims to direct mechanism.

## Worker-6 Hard Rework Rules

Worker-6 must output `needs_targeted_rework` and concrete `rework_targets` when any of these occur:

- layer-1 `source_verified` lacks a primary-source sequence/name/modification locator.
- any `unresolved_record` lacks a source-backed reason or missing-material blocker.
- activity rows are database-only, sentence-fragment targets, generic endpoint placeholders, missing raw value, missing target, missing locator, or MIC-like with no raw unit/table unit locator.
- supplementary assets exist but worker-3 output is only inventory/linkage/runtime limitation, or contains publisher boilerplate instead of evidence-critical content.
- mechanism claims lack `claim_id`, `claim_text`, valid evidence class, source locator, or direct assay types for direct claims.
- review report is templated without paper-specific adjudication evidence, lacks reviewer/model/provenance/timestamp fields, or only says no structural blockers.
- material retrieval lacks per-asset exhaustion evidence, or analysis accepted
  copied existing artifacts without a paper-specific source-review pass.
- terminal batch commands used `--allow-findings`, `--allow-risk`, or `|| true`
  and no later strict pass cleared the same paper.

When Worker-6 outputs `needs_targeted_rework`, it must also write
`work/review/quality_feedback.json` and dispatch the failure to the owner lane
through team state/mailbox. A final chat reply, native subagent transcript, or
tmux nudge is not durable delivery. See `team-rework-message-contract.md`.

## Review Provenance Fields

Every publication-grade `final/review_report.json` should include:

- `review_status`: `accepted_clean`, `accepted_with_cautions`, `needs_targeted_rework`, or `blocked_missing_primary_material`.
- `publication_grade`: boolean.
- `validator_contract_passed`: boolean.
- `reviewed_at` timestamp.
- `review_model`: `gpt-5.5`.
- `reasoning_effort`: `xhigh`.
- `source_review_depth`: `paper_xml`, `paper_pdf`, `oa_package`, `supplementary_assets`, `merged_database_rows`, and any unavailable sources.
- `materials_exhausted`: explicit booleans or per-asset entries showing whether
  paper XML, PDF, OA package, true supplementary files, and database rows were
  inspected.
- paper-specific `adjudication_summary`, not a template string.
- `rework_targets` with worker, artifact path, row/record/claim example, failure type, and required action.
- `caution_findings` with conflict identifiers and evidence context.

## Batch Reporting Rule

Report four separate numbers; never merge them:

- structurally ready count.
- validator-contract ready count.
- semantic gate pass count.
- publication-grade pass count.

Use `completed/100` only for the appropriate tier. Publication-grade completion requires semantic gate pass plus worker-6 source-reviewed acceptance.

If a batch has `100/100` packet handoff but fewer semantic or publication-grade
passes, call it `structural_handoff_complete`, not source-reviewed completion.
