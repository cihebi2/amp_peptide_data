---
name: paper-body-table-worker
description: Strict body/table evidence worker role for one-paper audit runs
---

# Paper Body/Table Worker

Use this skill for `worker-2` body/table evidence runs in the paper-audit workflow.

## Batch 2-Team hard gate

- Use `gpt-5.5` with `reasoning_effort=xhigh` whenever this worker is model-routed.
- Treat `paper_worker_v1.py run-role` as a schema scaffold only; it must be corrected against `paper.xml`, tables, figure captions, PDFs, and supplements before acceptance.
- Every activity/toxicity row must have a concrete endpoint, raw value, raw unit or explicit no-unit rationale, target class, species, strain/isolate when available, conditions/statistics when available, evidence ladder, and source locator.
- Reject or rework rows where species/strain is a sentence fragment such as `The minimal`, `The plot`, `In this`, or narrative prose.
- Database-only activity annotations may be preserved as provenance but must not masquerade as primary-source assay rows.
- In two-queue mode, this role is a material-extraction lane unless explicitly reassigned to analysis. Material-mode output is locator-backed source surfaces and candidate rows; final activity/toxicity conclusions belong to the analysis/adjudication queue.
- Deep retrieval/acquisition is required: inspect XML, PDF text/tables, figure
  captions, supplementary tables, and linked experiment rows for the assigned
  paper before declaring no row-level activity/toxicity evidence.
- Use bounded best effort: prioritize source surfaces that can change the gate,
  record `unrecoverable_material_gaps` with checked paths/tools/impact when a
  value cannot be recovered locally, and move the paper onward rather than
  retrying indefinitely or fabricating rows.


## Scope

- Read:
  - `papers/<paper_id>/source/`
  - `papers/<paper_id>/final/materials_manifest.json`
- Write only:
  - `papers/<paper_id>/work/body_evidence/`
  - `papers/<paper_id>/work/table_evidence/`
  - `papers/<paper_id>/packet/extracted/` when two-queue packet mode is active
  - `papers/<paper_id>/packet/analysis/` when explicitly assigned to analysis-mode activity/toxicity evidence
  - `papers/<paper_id>/packet/locators/` when two-queue packet mode is active
  - `papers/<paper_id>/packet/rework/rework_requests.jsonl` only when missing packet evidence blocks analysis

## Stable execution path

Use the deterministic role runner only as a schema scaffold:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <paper_id> --worker worker-2
```

Expected canonical outputs:

- `papers/<paper_id>/work/body_evidence/evidence.json`
- `papers/<paper_id>/work/table_evidence/evidence.json`

## Rules

- Do not claim any task except task `2`
- Stay inside the body/table write boundary
- Do not inspect unrelated repo files

## Three-Layer Curation Addendum

When three-layer AMP curation is active, body/table extraction must produce row-level experimental evidence rather than only narrative claims.

In two-queue mode:

- material queue assignment: extract XML/PDF/table text, candidate activity/toxicity rows, source locators, table structure, and parse/OCR gaps into the packet.
- analysis queue assignment: consume packet candidate rows and database rows to produce adjudication-ready activity/toxicity evidence.
- if an analysis assignment finds missing body/table material, write a rework ticket to `packet/rework/rework_requests.jsonl` with `target_queue: material_extraction`.
- copied activity/final JSON may be compared as prior work, but it must be
  rechecked against packet locators before acceptance.

Additional read-only inputs may include:

- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/all_experimental_records.csv`
- database-specific experiment files under `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/`

Additional expected outputs when requested by the workflow:

- `papers/<paper_id>/work/activity_evidence/activity_records.json`
- `papers/<paper_id>/packet/extracted/xml_sections.json`
- `papers/<paper_id>/packet/extracted/pdf_text.jsonl`
- `papers/<paper_id>/packet/extracted/pdf_tables.json`
- `papers/<paper_id>/packet/locators/locator_index.json`

Three-layer scaffold command:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <paper_id> --worker worker-2 --protocol amp_three_layer_v2
```

For every activity/toxicity row, extract when available:

- endpoint: MIC, MBC, IC50, EC50, MFC, MBIC, HC50, MHC, CC50, percent hemolysis, cell viability.
- raw value/unit and safe normalized value/unit.
- target class, species, strain/accession/isolate, and Gram status when applicable.
- assay conditions: medium, salt, serum, pH, temperature, incubation time.
- replicate/statistics: n, SD/SEM/CI, statistical test.
- source locator to primary text/table/supplement and, if applicable, source database row.

Use `normalization_status` values `direct`, `converted`, `not_convertible`, or `ambiguous`. Never convert ug/mL to uM without sufficient molecular-weight/modification support.

Before delivery, grep/sample the rows for suspicious target strings (`The`, `In this`, `minimal`, `plot`, long narrative phrases), generic endpoints, missing units on MIC-like rows, and database-only annotations. Any hit requires source review and correction or explicit targeted rework.

Do not close the lane as reliable while semantic QA would still flag sentence
fragments, generic endpoints, missing MIC-like units, database-only rows treated
as primary evidence, or locator gaps.
