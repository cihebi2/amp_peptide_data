---
name: paper-intake-worker
description: Strict paper intake worker role for one-paper audit runs
---

# Paper Intake Worker

Use this skill for `worker-1` intake runs in the paper-audit workflow.

## Batch 2-Team hard gate

- Use `gpt-5.5` with `reasoning_effort=xhigh` whenever this worker is model-routed.
- Treat `paper_worker_v1.py run-role` as a schema scaffold only; after it runs, inspect paper-local source assets and correct the output before marking the lane source-reviewed.
- Intake is publication-grade only when every staged XML/PDF/package/supplement path is inventoried, DOI/PMID/PMCID metadata is cross-checked, landed/database provenance is separated from paper provenance, and missing assets are explicit blockers or cautions.
- Do not assert source verification here; prepare traceable inputs for downstream workers.
- In two-queue mode, this is a material-extraction queue role. It creates or updates the paper packet and database-row snapshot, but it does not make final database or mechanism conclusions.
- Deep retrieval starts here: every packet must record original source roots,
  landed/source fallback decisions, raw asset paths, database snapshot inputs,
  and missing-material blockers so downstream analysis can audit one declared
  evidence surface without guessing.


## Scope

- Read only `papers/<paper_id>/source/`
- Write only:
  - `papers/<paper_id>/work/intake/`
  - `papers/<paper_id>/packet/` when two-queue packet mode is active
  - `papers/<paper_id>/final/materials_manifest.json`

## Stable execution path

Use the deterministic role runner only as a schema scaffold:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <paper_id> --worker worker-1
```

Then verify the canonical outputs exist:

- `papers/<paper_id>/work/intake/source_inventory.json`
- `papers/<paper_id>/work/intake/package_inventory.json`
- `papers/<paper_id>/work/intake/downstream_packet.json`
- `papers/<paper_id>/work/intake/intake_report.md`
- `papers/<paper_id>/final/materials_manifest.json`

## Rules

- Do not claim any task except task `1`
- Stay inside the intake write boundary
- Do not inspect unrelated repo files

## Three-Layer Curation Addendum

When a task mentions database-level AMP curation, merged APD6/DBAASP/DRAMP data, or the three-layer audit, pair this intake role with `$amp-three-layer-curation`.

Additional read-only inputs may include:

- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/manifests/landed_sources.csv`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/manifests/landed_asset_manifest.csv`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/<paper-folder>/metadata.json`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/literature/sequence_literature_links.csv`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/literature/unique_literature_availability.csv`

Additional intake duties in three-layer mode:

- Preserve database provenance separately from paper provenance.
- Refresh landed-asset manifests first; `landed_assets` is the preferred mutable selection pool and may receive new papers later.
- Map sequence records to DOI/PMID/PMCID and local landed asset folder when possible.
- Do not claim source verification; only prepare the record/paper/source inventory for downstream verification.
- Flag missing primary sources as `database_only_no_primary_source` candidates.
- In two-queue mode, write linked database rows under the packet `database/` directory or provide a manifest-compatible mapping to `work/database_linkage/source_record_links.json`.
- Record packet material status using the vocabulary in `amp-three-layer-curation/references/two-queue-paper-packet-contract.md`.
- If an adjudicator sends an intake/database-linkage rework ticket, update only the requested packet manifest or database snapshot fields and append a nonterminal owner-repair response with the new packet version. Keep the ticket open for worker-6 final rebuild and strict adjudication.
- Do not mark material status complete if XML/PDF/OA/supplement/database inputs
  were skipped rather than inventoried or explicitly recorded as unavailable.

Three-layer scaffold command:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <paper_id> --worker worker-1 --protocol amp_three_layer_v2
```

Additional output:

- `papers/<paper_id>/work/database_linkage/source_record_links.json`

Two-queue packet outputs when active:

- `papers/<paper_id>/packet/packet_manifest.json`
- `papers/<paper_id>/packet/raw/`
- `papers/<paper_id>/packet/database/database_source_manifest.json`
- `papers/<paper_id>/packet/database/linked_sequence_records.jsonl`
- `papers/<paper_id>/packet/database/linked_literature_records.jsonl`
- `papers/<paper_id>/packet/database/linked_experiment_records.jsonl`

If the workflow still uses `papers/<paper_id>/source/`, `work/`, and `final/`
as canonical locations, the packet manifest must map those legacy paths so
analysis workers can consume one declared packet surface.
