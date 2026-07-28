---
name: paper-mechanism-ontology-worker
description: Strict worker-5 role for AMP three-layer curation; extracts mechanism evidence into an evidence-strength ontology without promoting inferred or computational claims to direct mechanisms.
---

# Paper Mechanism Ontology Worker

Use this skill for `worker-5` in the `amp_three_layer_v2` six-worker workflow.

## Batch 2-Team hard gate

- Use `gpt-5.5` with `reasoning_effort=xhigh` whenever this worker is model-routed.
- Treat `paper_worker_v1.py run-role` as a schema scaffold only; every mechanism claim must be verified from source text/table/figure/supplement evidence.
- Each claim must include stable `claim_id`, claim text, entity scope, evidence class, source locator, and direct assay type when classed as `direct_mechanism`.
- Do not promote MIC/growth inhibition, charge, hydrophobicity, family membership, or discussion-only language to direct mechanism.
- In two-queue mode, this is an analysis queue role. Use packet locators and extracted source surfaces; write a material rework ticket when mechanism-critical figures, supplements, OCR, or tables are absent.
- Deep acquisition is required: re-open mechanism-relevant XML/PDF/table/figure/
  supplement/packet locators for the paper. Existing mechanism JSON is a prior
  scaffold only and cannot be copied forward as accepted evidence.


## Scope

Read:

- `papers/<paper_id>/source/`
- `papers/<paper_id>/work/body_evidence/`
- `papers/<paper_id>/work/table_evidence/`
- `papers/<paper_id>/work/supplementary_methods/`
- `papers/<paper_id>/packet/` when two-queue packet mode is active

Write only:

- `papers/<paper_id>/work/mechanism_ontology/`
- `papers/<paper_id>/packet/analysis/` when two-queue packet mode is active
- `papers/<paper_id>/packet/rework/rework_requests.jsonl` only when missing packet evidence blocks mechanism classification

## Stable execution path

Use this command as a schema scaffold only, then source-review and refine from primary evidence:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <paper_id> --worker worker-5 --protocol amp_three_layer_v2
```

Expected canonical output:

- `papers/<paper_id>/work/mechanism_ontology/mechanism_evidence.json`

## Evidence classes

- `direct_mechanism`: direct experiments such as permeability, membrane potential, TEM/SEM, NMR, SPR, ITC, pull-down, enzyme assay, ribosome binding, DNA/RNA binding.
- `phenotype_supported`: time-kill, MIC/growth phenotype, biofilm, ROS, morphology without direct mechanism closure.
- `inferred_mechanism`: charge, hydrophobicity, secondary structure, family, or discussion-only inference.
- `computational_only`: docking, MD, AlphaFold, simulation without experimental closure.
- `unknown_or_not_tested`: no mechanism experiment in the source.

## Required claim fields

Each `mechanism_claims[]` item must include `claim_id`, `claim_text`, `entity_scope`, `evidence_class`, `source_locator`, and `direct_assay_types` when direct. Add limitation notes for model-membrane-only, phenotype-only, computational-only, or inferred evidence.

## Rules

- Use the strongest supported class, not the most exciting class.
- Record direct assay type and locator when class is `direct_mechanism`.
- Keep phenotype, inference, and computation separate.
- If the paper only reports activity, use `unknown_or_not_tested` or `phenotype_supported`, not generic membrane disruption.
- Do not search outside the packet to rescue missing mechanism evidence unless the leader explicitly assigns material repair; route the gap to `target_queue: material_extraction`.
- Do not mark the lane accepted while mechanism claims lack IDs, source locators,
  evidence classes, or direct assay types for direct claims.
