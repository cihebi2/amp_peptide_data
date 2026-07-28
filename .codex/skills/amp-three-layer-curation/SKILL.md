---
name: amp-three-layer-curation
description: "Audit AMP database records against primary literature using a three-layer workflow. Batch 2-Team hardening requires gpt-5.5 xhigh, per-paper source-reviewed human-level publication-grade curation, semantic QA beyond validator success, and conflict-preserving adjudication."
---

# AMP Three-Layer Curation

Use this skill when the task is not only paper-level conclusion preservation, but AMP database curation across APD6, DBAASP, DRAMP, or later CAMP/dbAMP inputs.

## Batch 2-Team Publication-Grade Mode

This working copy is not a fast scaffold workflow. When operating under `batch/2-team`, use `gpt-5.5` with `reasoning_effort=xhigh` whenever model routing is under agent control, and enforce per-paper source-reviewed, human-level, publication-grade three-layer curation.

Read `references/publication-grade-source-review.md`, `references/publication-grade-quality-gate.md`, `references/team-rework-message-contract.md`, and `references/two-queue-paper-packet-contract.md` before launching, repairing, or accepting any AMP three-layer paper. They define the terminal acceptance gate, model gate, semantic QA expectations, durable team rework protocol, and material-vs-analysis queue boundary.

Treat deterministic role-runner output as a schema scaffold only. Do not use `final_ready`, `batch_sample_completed`, deterministic role-runner output, or accelerator auto-close as terminal evidence by itself. These are only structural signals until worker outputs have been source-reviewed and semantically checked.

## Deep Retrieval / Deep Acquisition / Reliable Result Gate

Every paper in a production batch must pass three separate gates before it can be
counted as accepted:

1. **Deep retrieval** - the material queue has exhaustively retrieved and
   indexed paper-local XML, PDF, OA package members, supplementary files,
   archives, legacy office files, OCR outputs, figure/table surfaces, and linked
   database rows. Any unavailable source must be named with the attempted tool,
   command, path, and failure reason.
2. **Deep acquisition** - the analysis queue has re-opened the packet sources
   and database rows for that specific paper, then written fresh or explicitly
   source-reviewed layer outputs. Existing `work/` or `final/` JSON may be used
   only as prior scaffolding; copied file presence is never analysis acceptance.
3. **Reliable result** - worker-6 has produced a paper-specific adjudication
   with provenance, semantic QA, material-exhaustion evidence, and either
   `accepted_clean`, `accepted_with_cautions`, `needs_targeted_rework`, or
   `blocked_missing_primary_material`. Semantic gate failure or publication QA
   failure prevents terminal acceptance.

Do not use batch size, runtime speed, packet existence, copied legacy finals,
`analysis_accepted` strings, `--allow-findings`, `--allow-risk`, or `|| true`
as a terminal completion path. Those may only create diagnostic reports or
nonterminal queue state.

## Two-Queue Paper Packet Mode

For long-running Batch 2-Team production, split work into two durable queues:

- **Material extraction queue**: continuously builds or repairs per-paper packets from XML, PDF, OA packages, supplementary files, OCR, archive extraction, and linked database-row snapshots. It marks locators, errors, missing materials, and extraction status; it does not make final database or mechanism conclusions.
- **Analysis and adjudication queue**: consumes those packets to audit database records, extract/normalize activity and toxicity evidence, classify mechanism evidence strength, preserve conflicts, and write final conclusions.

The queues communicate through the packet layout and `rework/*.jsonl` tickets defined in `references/two-queue-paper-packet-contract.md`. Do not rely on chat-only feedback when material gaps must be routed back from analysis/adjudication to extraction.

Use `$team` / `omx team ...` for durable queue workers. Use `$ralph` / `omx ralph ...` only as a separate persistence supervisor when the overall manifest must keep running until every paper is accepted, cautioned, or blocked by a durable ticket. Do not use the removed `omx team ralph` form.

## Data Roots

In this workspace, the merged corpus is usually on the Windows D drive. For paper selection and source review, prefer `landed_assets` because it contains literature materials that have already landed with extracted XML and split supplementary assets. In WSL use:

```text
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output
```

Windows equivalents:

```text
D:\work\抗菌肽\数据库\merged_amp_corpus\landed_assets
D:\work\抗菌肽\数据库\merged_amp_corpus\landed_assets\papers
D:\work\抗菌肽\数据库\merged_amp_corpus\output
```

Use `downloaded_assets/papers` only as a broader fallback/archive when a needed record is not yet present in `landed_assets`. The user may add new materials to `landed_assets`; always refresh its manifests/counts at the start of a batch instead of relying on stale counts.

Expected corpus files include:

- `output/sequences/all_sequences.csv` - APD6 / DBAASP / DRAMP sequence records.
- `output/literature/sequence_literature_links.csv` - sequence-to-literature mapping.
- `output/literature/unique_literature_availability.csv` - DOI/PMID/PMCID and asset availability.
- `output/experiments/all_experimental_records.csv` - unified experimental record rows.
- `output/experiments/dbaasp_assay_records.csv` - DBAASP assay-level rows.
- `output/experiments/apd6_activity_text_records.csv` - APD6 activity text rows.
- `output/experiments/dramp_activity_text_records.csv` - DRAMP source-table rows.
- `landed_assets/manifests/landed_sources.csv` - the current first-pass selection pool of landed papers.
- `landed_assets/manifests/landed_asset_manifest.csv` - file-level PDF/XML/package/supplement inventory for landed papers.
- `landed_assets/manifests/landed_metadata_manifest.csv` - metadata/asset manifest inventory for landed papers.
- `landed_assets/manifests/summary.json` - live landed-asset counts; refresh this because the folder is incrementally updated.
- `landed_assets/papers/<dedupe-or-doi-folder>/metadata.json` plus `pdf/`, `xml/`, `package/`, and `supplementary/` folders.
- `downloaded_assets/papers/<dedupe-or-doi-folder>/metadata.json` is fallback-only when landed assets are absent.

If `landed_assets` and `output` are absent, report that the merged corpus is unavailable instead of inventing database facts from paper finals.

## Three-Layer Contract

### Layer 1 - Database Record Verification

For each AMP record, answer with source locators where possible:

- sequence matches primary source?
- name and synonyms match?
- N-terminal and C-terminal modifications preserved?
- D-amino acid, cyclization, disulfide, amidation, lipidation preserved?
- source organism correct?
- which database record points to which primary paper?
- DOI / PMID / PMCID traceable?
- cross-database conflicts present?

Use these statuses:

- `source_verified`
- `source_conflict`
- `database_only_no_primary_source`
- `sequence_modified_not_normalized`
- `unresolved_record`

Recommended output:

```text
papers/<paper_id>/work/database_record_audit/record_identity_audit.json
papers/<paper_id>/final/database_record_verification.json
```

### Layer 2 - Experimental Evidence Verification

Extract row-level records, not only prose summaries. Each activity/toxicity row should preserve:

- endpoint: MIC, MBC, IC50, EC50, MFC, MBIC, HC50, MHC, CC50, percent hemolysis, cell viability, etc.
- raw value and raw unit.
- normalized value/unit when safe; otherwise `normalization_status` explains why not.
- target class and strain: bacteria/fungus/virus/cancer/mammalian/parasitic; Gram status; species; strain/accession/isolate.
- assay conditions: medium, salt, serum, pH, temperature, incubation time, and other reported modifiers.
- replicate/statistics fields when reported.
- hemolysis/cytotoxicity/in vivo evidence where present.
- source locator to XML paragraph/table, PDF/supplement, or database row.

Evidence ladder values:

- `predicted_only`
- `in_silico_filtered`
- `in_vitro_single_pathogen`
- `in_vitro_multi_pathogen`
- `toxicity_tested`
- `mechanism_assayed`
- `in_vivo_tested`
- `therapeutic_window_supported`

Recommended output:

```text
papers/<paper_id>/work/activity_evidence/activity_records.json
papers/<paper_id>/final/activity_toxicity_evidence.json
```

### Layer 3 - Mechanism Evidence Ontology

Mechanism labels must be evidence-strength aware. Do not flatten every mechanism to generic `membrane disruption`.

Use this top-level evidence class:

- `direct_mechanism` - direct experiments such as permeability, membrane potential, TEM/SEM, NMR, SPR, ITC, pull-down, enzyme assay, ribosome binding, DNA/RNA binding.
- `phenotype_supported` - MIC, time-kill, biofilm, ROS, morphology, or growth phenotype without direct mechanism closure.
- `inferred_mechanism` - inferred from charge, hydrophobicity, secondary structure, family, or discussion.
- `computational_only` - docking, MD, AlphaFold, or simulation without experimental closure.
- `unknown_or_not_tested` - no mechanism evidence in the primary source.

Recommended output:

```text
papers/<paper_id>/final/mechanism_ontology_record.json
```

### Worker-6 strict adjudication

Worker-6 must distinguish publishable acceptance from inventory-level completion and must write paper-specific adjudication, not template text. Required review provenance includes `reviewed_at`, `review_model: gpt-5.5`, `reasoning_effort: xhigh`, checked inputs, semantic QA summary, and a per-layer decision rationale.

Worker-6 must distinguish publishable acceptance from inventory-level completion:

- `accepted_clean` - no hard rework targets and no preserved conflict cautions.
- `accepted_with_cautions` - no hard rework targets, but preserved conflicts or
  caution findings remain.
- `needs_targeted_rework` - at least one worker must repair missing or weak
  evidence before the paper counts as complete.
- `blocked_missing_primary_material` - required primary/supplementary material is
  absent from local assets and cannot be repaired by extraction alone.

Hard rework targets should include the worker, record/row examples, missing
field or locator type, and a concrete required action. Do not count a paper as
complete merely because final JSON files exist.

## Workflow

1. Refresh `landed_assets/manifests/summary.json` and `landed_assets/manifests/landed_sources.csv`; select papers from landed assets first.
2. Material queue: resolve the primary paper using canonical DOI/PMID/PMCID and local asset metadata under `landed_assets/papers/`; fall back to `downloaded_assets/papers/` only when needed.
3. Material queue: build or update the paper packet with XML/PDF/supplement/OA package extraction, OCR/archive attempts, locator indexes, extraction gaps, and linked database-row snapshots.
4. Analysis queue: for each paper, re-open packet sources and build layer-1 identity verification from packet database rows plus primary-source evidence. Do not accept copied layer-1 finals without source-review proof.
5. Analysis queue: for each paper, re-open packet source tables/text and database experiment rows to build layer-2 activity/toxicity evidence. Do not accept rows that have not been checked against paper-local locators.
6. Analysis queue: for each paper, re-open mechanism-relevant text, figures, tables, supplements, and database rows to build layer-3 mechanism ontology from direct assay evidence, phenotype evidence, computational evidence, and explicit unknowns.
7. Adjudication: report conflicts rather than smoothing them away; if packet evidence is insufficient, write a structured rework ticket to `rework/rework_requests.jsonl` instead of silently guessing.
8. Run `paper-batch-orchestrator/scripts/semantic_three_layer_gate.py` or an equivalent controller gate that checks target species strings, units, generic endpoints, mechanism claim IDs/text, review timestamps/model provenance, material exhaustion, fallback/accelerator issue-log events, and non-templated worker-6 rationale.
9. Only call a paper publication-grade when all hard gates in `references/publication-grade-source-review.md`, `references/publication-grade-quality-gate.md`, and `references/two-queue-paper-packet-contract.md` pass.

## Six-Worker Protocol

For source-backed curation teams, launch the versioned six-worker protocol instead of the legacy four-worker conclusion-preservation flow:

```bash
python workspace-guide/team-paper-sample/launch_paper_team_v2.py \
  --paper-id <landed-paper-folder-or-PMCID> \
  --source-pool-root /mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers \
  --protocol amp_three_layer_v2
```

Role split:

- Material queue: `worker-1` / `intake_linkage` stages paper-local assets, maps landed/database provenance, and snapshots linked rows into the packet.
- Material queue: `worker-2` / `main_text_assay_extractor` extracts main-text/XML/table source surfaces and locator-backed candidate activity/toxicity evidence.
- Material queue: `worker-3` / `supplementary_methods_extractor` extracts supplement methods, sequence, assay, toxicity, mechanism source surfaces, OCR, and archive-derived evidence.
- Analysis queue: `worker-4` / `database_record_auditor` audits database identity, source traceability, and conflicts from the packet.
- Analysis queue: `worker-5` / `mechanism_ontology_extractor` classifies mechanism evidence strength and assay types from the packet.
- Analysis queue: `worker-6` / `adjudicator_review` compares all layers, preserves conflicts, sends targeted packet rework, and writes final outputs.

The legacy `paper_audit_v1` four-worker protocol remains available for paper-only conclusion preservation. Use `amp_three_layer_v2` when database-record verification, evidence ladders, or mechanism ontology are required.

## Non-Negotiable Rules

- Do not treat a database row as source verified without a primary-source locator or explicit database-only status.
- Do not normalize modified sequences by silently removing amidation, D-residues, cyclization, disulfides, lipidation, or terminal caps.
- Do not convert units without enough molecular-weight or sequence/modification support.
- Do not promote computational or inferred mechanisms to direct mechanisms.
- Keep database provenance separate from paper evidence provenance.
- Keep material extraction acceptance separate from analysis/adjudication acceptance.
- Preserve cross-database conflicts as data; they are part of the scientific contribution.
- Treat `landed_assets` as a mutable live pool; refresh manifests before selecting records or reporting counts.
- Do not let analysis workers hunt through unrelated folders when the packet is incomplete; route missing evidence through a rework ticket to the material queue.
- Do not let analysis workers close from packet checks alone. A queue can report
  `structural_handoff_complete`, but terminal analysis acceptance requires
  paper-by-paper source review and worker-6 adjudication.
