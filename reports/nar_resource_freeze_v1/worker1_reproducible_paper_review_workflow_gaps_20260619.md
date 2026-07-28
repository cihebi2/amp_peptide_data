# Worker 1: Reproducible Paper-Review Workflow Gaps For NAR AMP Evidence Resource v1

Generated: 2026-06-19
Team: nar-amp-evidence-reso-09fa0b58
Task: 1
Scope: read current Batch 4-Team docs and summarize reproducible paper-review workflow gaps that matter before NAR AMP evidence resource v1 freeze.

## Executive Summary

The current docs already define a strong source-reviewed AMP paper workflow: strict input eligibility, two-queue material/analysis separation, durable rework tickets, semantic/publication gates, and conservative status vocabulary. The main reproducibility gaps are not missing principles; they are freeze-level packaging gaps: no single v1 manifest binds docs, scripts, source roots, status vocabularies, denominator definitions, gate outputs, and known exclusions into one citable release; denominator semantics remain open; early-batch quality evidence is heterogeneous; and the workflow docs describe commands but not a machine-checkable release contract for NAR-style public reuse.

## Evidence Base Read

- `.omx/context/nar-resource-freeze-v1-20260619T151113Z.md:3` states the freeze goal: document a zero-to-one reproducible multi-worker review workflow and produce v1 freeze statistics/tables.
- `.omx/context/nar-resource-freeze-v1-20260619T151113Z.md:20` records key constraints: do not label non-`source_verified` as database errors, do not call `accepted_with_cautions` clean, and do not claim full-database/full-human-gold coverage.
- `docs/PAPER_REVIEW_REPRODUCIBLE_RUNBOOK_20260511.md:6` describes current queue reproduction from paper selection through audit and summary.
- `docs/PAPER_REVIEW_MECHANISM_V1.md:28` requires separating material readiness, validator readiness, semantic readiness, and publication-grade readiness.
- `docs/MIAOBI_MESSAGE_TRANSFER_CONTRACT.md:30` defines source-of-truth rules that keep chat/state messages separate from scientific evidence.
- `docs/QUALITY_REWORK_LOOP_20260429.md:7` defines the non-negotiable four-layer acceptance rule after real-material rework testing.

## Workflow Gaps Blocking A Clean NAR v1 Freeze

1. No single freeze manifest connects all reproducibility inputs and outputs.
   - Current docs identify desired outputs (`v1 freeze manifest`, denominator table, crosstabs) but the actual release contract is still contextual rather than a generated artifact (`.omx/context/nar-resource-freeze-v1-20260619T151113Z.md:6`).
   - The runbook gives operational commands, but it does not define a machine-readable v1 release manifest with doc versions, script checksums, source roots, result files, denominator policy, schema versions, exclusion policy, and generated table paths.
   - NAR impact: a reviewer/new AI can replay steps, but cannot yet verify that a specific public v1 snapshot is complete and internally consistent.

2. Denominator semantics are explicitly unresolved.
   - The freeze context lists `1471 vs 1472`, whether 127 non-publication-grade papers enter the main release, and database denominator calculation limits as open questions (`.omx/context/nar-resource-freeze-v1-20260619T151113Z.md:27`).
   - Results currently report 1472 deduplicated reviewed papers, 1326 queue-accepted, 146 non-accepted, and 127 `publication_grade=false` final reviews (`docs/PAPER_REVIEW_RESULTS_SUMMARY_20260511.md:10`, `docs/PAPER_REVIEW_RESULTS_SUMMARY_20260511.md:108`).
   - NAR impact: all tables must expose denominator labels such as `reviewed_papers_dedup`, `queue_accepted`, `publication_grade_true`, `blocked_or_failed`, and `database_rows_with_primary_source_locator`; otherwise percentages will be ambiguous.

3. Acceptance status layers are documented but not yet packaged as a public schema table.
   - The mechanism forbids collapsing statuses into `done` and names four readiness layers (`docs/PAPER_REVIEW_MECHANISM_V1.md:26`).
   - The runbook status table distinguishes `accepted_after_rework`, `accepted_with_cautions`, audit pass, semantic pass, publication QA pass, and blocked states (`docs/PAPER_REVIEW_REPRODUCIBLE_RUNBOOK_20260511.md:48`).
   - Gap: there is no freeze-facing status vocabulary table with public definitions, allowed transitions, denominator inclusion rules, and whether each status can support claims such as `source-reviewed`, `publication-grade`, `database discrepancy`, or `excluded/sensitivity`.

4. Early and late batches have different closure evidence.
   - The result summary says early queues have no complete post-run latest audit, while later runs have full artifact/sample/semantic evidence (`docs/PAPER_REVIEW_RESULTS_SUMMARY_20260511.md:30`).
   - The same summary cautions that 230/230 recent accepted sample audits prove only sampled accepted sets, not all earlier accepted records (`docs/PAPER_REVIEW_RESULTS_SUMMARY_20260511.md:46`).
   - NAR impact: v1 needs a release column or sensitivity stratum distinguishing `post_run_closure_verified`, `sample_audited`, `semantic_gate_checked`, `legacy_queue_only`, and `blocked`.

5. Public resource claims need stricter wording than internal workflow claims.
   - The freeze context forbids calling non-`source_verified` rows database errors and forbids claiming a full human gold standard (`.omx/context/nar-resource-freeze-v1-20260619T151113Z.md:20`).
   - The mechanism requires preserving database conflicts/cautions instead of smoothing them into source-verified acceptance (`docs/PAPER_REVIEW_MECHANISM_V1.md:177`).
   - Gap: no dedicated NAR wording guide yet maps internal categories (`source_conflict`, `database_only_no_primary_source`, `sequence_modified_not_normalized`, `unresolved_record`) to public labels and manuscript/table phrasing.

6. Rework and failure recovery are reproducible, but release inclusion policy is not.
   - The quality loop says major/blocking failures must create context packets and keep tickets open until gate evidence passes (`docs/QUALITY_REWORK_LOOP_20260429.md:65`).
   - After the rework cap, papers remain non-accepted and continue to the next paper (`docs/QUALITY_REWORK_LOOP_20260429.md:105`).
   - Gap: v1 must specify whether capped/blocked papers are included as negative evidence, excluded from main release, included only in sensitivity tables, or published as a separate `not_publication_grade` ledger.

7. Message-bus artifacts are well-defined internally but not normalized for external reproducibility.
   - The message contract says `workflow_context.json` stores summaries/paths only, artifacts remain source-of-truth, and chat messages cannot support acceptance (`docs/MIAOBI_MESSAGE_TRANSFER_CONTRACT.md:30`).
   - The workflow template lists forbidden acceptance evidence, including natural-language summaries and copied final files without source review (`docs/workflow-templates/amp-paper-review-codex-claude.yaml:23`).
   - Gap: NAR release docs need a mapping from local `.miaobi-paper-review` files to public provenance fields, with explicit redaction/size policy for logs, OCR snippets, and source-text excerpts.

8. Gate verification commands exist, but freeze verification is not one-command reproducible.
   - The mechanism lists helper script `--help` checks and says real scientific verification requires a manifest and packets (`docs/PAPER_REVIEW_MECHANISM_V1.md:274`).
   - The runbook has separate commands for semantic/publication gates, stale ticket repair, full artifact audit, and sample audit (`docs/PAPER_REVIEW_REPRODUCIBLE_RUNBOOK_20260511.md:416`, `docs/PAPER_REVIEW_REPRODUCIBLE_RUNBOOK_20260511.md:444`, `docs/PAPER_REVIEW_REPRODUCIBLE_RUNBOOK_20260511.md:481`).
   - Gap: v1 needs a top-level `make freeze-v1`-style or single Python entrypoint that verifies expected input files, regenerates all tables, writes latest pointers, and fails closed on missing/ambiguous denominators.

9. Source availability limits are recorded per workflow but not summarized at release level.
   - Material packets are incomplete unless XML, PDF, OA package, supplements, archives, OCR/office attempts, and database snapshots are inventoried or explicitly marked unavailable (`docs/PAPER_REVIEW_MECHANISM_V1.md:71`).
   - Best-effort recovery must record `unrecoverable_material_gaps` with paths, tools, reason, impact, and next action (`docs/QUALITY_REWORK_LOOP_20260429.md:135`).
   - Gap: the NAR v1 freeze needs aggregate counts of source gaps by type and impact so users can distinguish database/literature disagreement from local source unavailability.

10. AI/model disclosure exists operationally but not yet as a NAR-ready release section.
    - The runbook records model, reasoning effort, timeout/retry parameters, and configuration checks (`docs/PAPER_REVIEW_REPRODUCIBLE_RUNBOOK_20260511.md:18`).
    - The freeze context explicitly requires public website/API/download/schema/versioning/maintenance/manual validation/AI disclosure (`.omx/context/nar-resource-freeze-v1-20260619T151113Z.md:18`).
    - Gap: NAR-facing docs still need a concise AI assistance disclosure that separates deterministic scripts, Codex worker extraction/adjudication, manual review checkpoints, and limitations.


## Integrated Subagent Risk Addendum

The delayed review probe independently confirmed and sharpened these high-risk freeze gaps:

- Freeze v1 is a reproducible candidate snapshot, not yet a NAR-submission-ready resource; `docs/NAR_DATABASE_RESOURCE_ROADMAP.md` still requires public website/API/download, release versioning, license/maintenance, AI/Codex disclosure, and human validation, while `scripts/build_nar_resource_freeze_v1.py` emits `freeze_candidate` and a `not_submission_ready_until` list.
- The paper denominator remains internally ambiguous: result docs report 1472 deduplicated reviewed papers, roadmap P0 still requires resolving `1471 vs 1472`, and the freeze builder keeps that reconciliation as a blocker.
- Queue-level acceptance must stay separate from publication-grade evidence; runbook and rework-loop contracts both forbid treating `accepted_after_rework`, file presence, or capped best-effort cases as clean acceptance.
- Provenance vocabulary is not fully canonical across prose and schema: mechanism docs expect explicit checked-input provenance, while the final-review schema emphasizes `source_review_depth`, `materials_exhausted`, and `semantic_quality_checks`; v1 should define one public provenance field set.
- Message-bus logs remain audit/control-plane records, not acceptance evidence; the freeze should cite packet-local locators, final reports, and gates instead of chat/state summaries.
- Blocked edge cases must remain split by cause (`figure_chart_value_gap`, missing external supplement, activity-table extraction gap, watchdog/infra exhaustion) rather than collapsed into one public bucket.
- Latest-pointer drift remains a watch item: the freeze builder hashes key inputs and emits manifests, but the release must archive the emitted manifest/checksums rather than relying on mutable `latest` inputs.

## Recommended v1 Freeze Documentation Sections

1. `Release Snapshot And Manifest`
   - Inputs: repo root, source roots, docs version, scripts, schemas, papers/packets roots, reports used.
   - Outputs: manifest JSON, summary JSON/CSV/MD, denominator table, crosstabs, examples, source recovery status.
   - Checks: generated timestamp, row counts, expected latest pointers, and failed-closed validation status.

2. `Denominator And Inclusion Policy`
   - Define every denominator used in manuscript/resource tables.
   - Resolve `1471 vs 1472` and document whether 127 non-publication-grade papers are excluded, included as sensitivity, or published separately.
   - Define database-row denominators from final audit rows vs packet linked rows and name their limitations.

3. `Evidence Status Vocabulary`
   - Public table for `source_verified`, `source_conflict`, `sequence_modified_not_normalized`, `database_only_no_primary_source`, `unresolved_record`, `accepted_with_cautions`, and blocked classes.
   - For each status: allowed claim, public label, denominator inclusion, and whether it can be called discrepancy/error.

4. `Paper-Review Workflow Reproduction`
   - Short, zero-to-one flow from source material eligibility through packet construction, worker roles, rework, gates, and final artifacts.
   - Link to the detailed runbook rather than duplicating long command blocks.

5. `Quality Gates And Release Verification`
   - List required gates and acceptance thresholds.
   - Include one command/script that regenerates or verifies all v1 release tables and fails if denominators/statuses disagree.

6. `Source Recovery And Known Limitations`
   - Aggregate missing external supplements, figure-only exact-value gaps, table parser gaps, watchdog/infra failures, and capped rework.
   - Explain why unresolved records are not promoted to source-verified claims.

7. `Public Resource Interface Plan`
   - Website/API/download/schema/versioning/maintenance plan.
   - Map local artifact paths to public fields and privacy/copyright-safe provenance fields.

8. `AI Assistance, Manual Validation, And Maintenance`
   - Disclose model/tool roles, deterministic scripts, human/manual validation touchpoints, no full-human-gold-standard claim, and planned update cadence.

## Minimal Next Actions For Leader Integration

1. Have Task 2 generate/verify the denominator table with explicit denominator names and sensitivity strata.
2. Have Task 3/leader convert the recommended sections into a NAR planning doc or manuscript resource outline.
3. Add or identify a freeze-v1 verification script that validates manifest, denominator table, crosstabs, latest pointers, and status vocabulary consistency.
4. Keep blocked/non-publication-grade records visible as limitations or sensitivity records, not as clean accepted evidence.

## Coordination Notes

- Coordination protocol: coordinated - checked handoff boundaries against Task 2 denominator/crosstab scope, Task 3 doc-section advisory scope, and Task 4 evidence-path scope; this artifact is worker-1-owned and does not modify shared planning docs.
- Subagent spawn evidence: 2, review probe 019ee070-8943-79e2-b72f-396551208642 and change-slice/doc-section probe 019ee070-aa16-7cf0-836e-126ffd8ab931; integrated the completed change-slice finding to keep detailed gap inventory out of normative mechanism/plans files and use this worker-owned report as the detailed addendum, with roadmap/runbook/results-summary pointers left for leader/doc-owner integration; review probe returned during finalization and its risk findings were integrated in the subagent risk addendum.
- Serial searches before spawn: 3.

