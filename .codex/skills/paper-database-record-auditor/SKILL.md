---
name: paper-database-record-auditor
description: Strict worker-4 role for AMP three-layer curation; audits APD6/DBAASP/DRAMP database records against primary literature identity evidence, preserving sequence, modification, source, citation, and cross-database conflicts.
---

# Paper Database Record Auditor

Use this skill for `worker-4` in the `amp_three_layer_v2` six-worker workflow.

## Batch 2-Team hard gate

- Use `gpt-5.5` with `reasoning_effort=xhigh` whenever this worker is model-routed.
- Treat `paper_worker_v1.py run-role` as a schema scaffold only; every APD6/DBAASP/DRAMP row must be rechecked against primary paper sources and linked database rows.
- `source_verified` requires exact primary-source evidence for sequence/name/modification/source/citation; otherwise use `source_conflict`, `database_only_no_primary_source`, `sequence_modified_not_normalized`, or `unresolved_record`.
- Do not smooth conflicts across databases; conflict preservation is part of the publishable result.
- In two-queue mode, this is an analysis queue role. Consume the paper packet database snapshot and locator-backed material; if required evidence is missing, write a material rework ticket instead of hunting unrelated folders.
- Deep acquisition is required: re-open the packet XML/PDF/supplement locators and
  linked database rows for this paper. Existing database audit or final JSON is
  prior evidence only, never acceptance by itself.


## Scope

Read:

- `papers/<paper_id>/source/`
- `papers/<paper_id>/work/database_linkage/source_record_links.json`
- `papers/<paper_id>/packet/` when two-queue packet mode is active
- read-only merged corpus rows under `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/`

Write only:

- `papers/<paper_id>/work/database_record_audit/`
- `papers/<paper_id>/packet/analysis/` when two-queue packet mode is active
- `papers/<paper_id>/packet/rework/rework_requests.jsonl` only when a missing material or analysis blocker must be routed

## Stable execution path

Use this command as a schema scaffold only, then source-review and refine from primary source plus database evidence:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <paper_id> --worker worker-4 --protocol amp_three_layer_v2
```

Expected canonical output:

- `papers/<paper_id>/work/database_record_audit/record_identity_audit.json`

## Required checks

For every candidate AMP/database record, answer:

- sequence agreement with primary source.
- name/synonym agreement.
- N-terminal and C-terminal modifications.
- D-amino acid, cyclization, disulfide, amidation, lipidation.
- source organism agreement.
- source DOI/PMID/PMCID traceability.
- APD6/DBAASP/DRAMP conflicts.

## Status vocabulary

Use only:

- `source_verified`
- `source_conflict`
- `database_only_no_primary_source`
- `sequence_modified_not_normalized`
- `unresolved_record`

## Rules

- Do not mark `source_verified` without a primary-source locator.
- Do not silently normalize modified sequences.
- Preserve conflicts as evidence, not noise.
- Do not write final adjudicated outputs; worker-6 owns final files.
- Do not mutate packet database snapshots; add audit findings under analysis outputs.
- Use `target_queue: material_extraction` only for missing source/locator gaps, and `target_queue: analysis` for database-audit self-rework.
- Do not mark the lane accepted from copied artifacts, batch packet checks, or
  validator pass; record source-review provenance for every verified record.
