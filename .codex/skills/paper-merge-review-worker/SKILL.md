---
name: paper-merge-review-worker
description: Strict merge/review worker role for one-paper audit runs
---

# Paper Merge/Review Worker

Use this skill for `worker-4` merge/review runs in the paper-audit workflow.

## Batch 2-Team hard gate

- Use `gpt-5.5` with `reasoning_effort=xhigh` whenever this worker is model-routed.
- For legacy four-worker paper audit, deterministic merge output is only a scaffold; final artifacts must be source-reviewed and conclusion-bearing.
- For `amp_three_layer_v2`, do not use this skill as worker-4; use the database-record, mechanism-ontology, and adjudicator skills instead.
- In two-queue AMP production, this legacy merge/review skill is not the main analysis surface. Use it only for `paper_audit_v1` conclusion preservation or for compatibility with older paper-only packets.


## Scope

- Read only canonical upstream evidence for the current paper
- Write only:
  - `papers/<paper_id>/work/mechanism_merge/`
  - `papers/<paper_id>/work/formal_mapping/`
  - `papers/<paper_id>/work/review/`
  - `papers/<paper_id>/final/`

## Stable execution path

Use the deterministic role runner only as a schema scaffold after upstream artifacts exist:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <paper_id> --worker worker-4
```

Expected canonical outputs:

- `papers/<paper_id>/final/mechanism_record.json`
- `papers/<paper_id>/final/vc_projection.json`
- `papers/<paper_id>/final/review_report.json`

## Rules

- Do not claim any task except task `4`
- Stay inside the merge/review write boundary
- Do not inspect unrelated repo files
- If a split packet is active and material is missing, write a rework target rather than inventing a conclusion from incomplete extraction.

## Three-Layer Curation Addendum

In the versioned `amp_three_layer_v2` six-worker protocol, this legacy merge/review skill is not the worker-4 surface. Use:

- `paper-database-record-auditor` for `worker-4`.
- `paper-mechanism-ontology-worker` for `worker-5`.
- `paper-adjudicator-review-worker` for `worker-6`.

This legacy skill remains for `paper_audit_v1` four-worker conclusion preservation.

For two-queue AMP curation, the material queue prepares packet evidence and the
analysis queue uses `paper-database-record-auditor`,
`paper-mechanism-ontology-worker`, and `paper-adjudicator-review-worker`.
Do not collapse those responsibilities back into this legacy worker.

Layer-1 status values:

- `source_verified`
- `source_conflict`
- `database_only_no_primary_source`
- `sequence_modified_not_normalized`
- `unresolved_record`

Layer-2 evidence ladder values:

- `predicted_only`
- `in_silico_filtered`
- `in_vitro_single_pathogen`
- `in_vitro_multi_pathogen`
- `toxicity_tested`
- `mechanism_assayed`
- `in_vivo_tested`
- `therapeutic_window_supported`

Layer-3 mechanism evidence classes:

- `direct_mechanism`
- `phenotype_supported`
- `inferred_mechanism`
- `computational_only`
- `unknown_or_not_tested`

Do not hide database conflicts. If APD6/DBAASP/DRAMP disagree on sequence, modification, name, source organism, activity, or citation, preserve the conflict in the final review and route it to `source_conflict` or `sequence_modified_not_normalized` as appropriate.
