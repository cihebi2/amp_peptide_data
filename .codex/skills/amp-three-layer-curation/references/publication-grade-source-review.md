# Publication-Grade Source Review Contract

Use this reference for the Batch 2-Team working-copy skills when the task is AMP three-layer curation. The goal is per-paper, source-reviewed, human-level, publication-grade evidence, not validator theater.

## Model Gate

- Use `gpt-5.5` with `reasoning_effort=xhigh` whenever model routing is under agent control.
- If launching native subagents, set `model="gpt-5.5"` and `reasoning_effort="xhigh"`.
- If launching OMX workers through launch args, set the equivalent model flags, for example `--model gpt-5.5 --reasoning-effort xhigh` when the runtime supports them.
- If the runtime cannot prove the model/effort, record that as a blocker or a non-publication-grade limitation.

## Terminal Acceptance Gate

A paper is terminal only when all of these are true:

1. Deep retrieval is proven: XML, PDF, OA package, supplementary files, archive
   members, OCR/office extraction attempts, database rows, and unresolved gaps
   are all inventoried with concrete paths or failure evidence.
2. Deep acquisition is proven: the responsible analysis worker re-opened the
   packet sources and linked database rows for this paper, not merely copied or
   summarized existing `work/` or `final/` JSON.
3. Every accepted claim is grounded in paper-local primary material or a linked
   database row with a concrete locator.
4. Deterministic/fallback output has been treated only as a schema scaffold and then source-reviewed, corrected, and normalized.
5. Worker-6 writes a paper-specific adjudication with `reviewed_at`, reviewer/model provenance, non-templated summary, checked inputs, decision rationale, and targeted rework or cautions.
6. Activity/toxicity rows do not contain sentence fragments or endpoint labels as species/strain/target fields.
7. Mechanism claims include stable `claim_id`, claim text, evidence class, source locator, and direct assay type when classed as `direct_mechanism`.
8. Cross-database conflicts remain visible as `source_conflict` or `sequence_modified_not_normalized`; they are not smoothed into `source_verified`.
9. Batch-level `final_ready`, `batch_sample_completed`, packet check success, copied final artifacts, or current validator success is corroborated by semantic QA and paper-by-paper source review.
10. Semantic gate and publication-quality gate both pass without terminal-path `--allow-findings`, `--allow-risk`, or `|| true`.

## Required Evidence By Layer

### Layer 1 - Database Record Verification

For every APD6/DBAASP/DRAMP record linked to the paper, preserve:

- database id and sequence key;
- source DOI/PMID/PMCID match;
- primary-source sequence/name/modification/source-organism evidence;
- exact conflict type when database and source disagree;
- `source_locator` with XML section/table/figure, supplement path/member, PDF page, or database row provenance.

### Layer 2 - Activity And Toxicity Evidence

For every row, preserve endpoint, raw value, raw unit, target class, species, strain/isolate, assay conditions, statistics, evidence ladder, and source locator when available.

Reject or rework rows when:

- species is a sentence fragment such as `The minimal`, `The plot`, `In this`, or narrative prose;
- endpoint is only `activity`, `antimicrobial`, or a database-only annotation without a primary-source assay row;
- MIC/MBC/MFC/IC50/EC50/HC50/CC50-like rows lack a reported unit and no explicit no-unit rationale is present;
- target or value is inferred from unrelated text rather than a table/sentence about that assay.

### Layer 3 - Mechanism Ontology

For each mechanism claim, write:

- `claim_id` stable within the paper;
- `claim_text` or concise source-backed claim;
- `entity_scope`;
- `evidence_class` from the standard ontology;
- `direct_assay_types` when `evidence_class=direct_mechanism`;
- `source_locator` pointing to the exact body/table/figure/supplement evidence;
- limitation notes when evidence is model-membrane-only, phenotype-only, computational-only, or inferred.

Do not promote MIC, growth inhibition, charge, hydrophobicity, or discussion-only statements to direct mechanism.
