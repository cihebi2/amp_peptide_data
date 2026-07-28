---
name: paper-supp-evidence-worker
description: Strict supplementary evidence worker role for one-paper audit runs
---

# Paper Supplementary Worker

Use this skill for `worker-3` supplementary-evidence runs in the paper-audit workflow.

## Batch 2-Team hard gate

- Use `gpt-5.5` with `reasoning_effort=xhigh` whenever this worker is model-routed.
- Treat `paper_worker_v1.py run-role` as a schema scaffold only; source-review every declared or staged supplement before acceptance.
- Inventory-only output is not publication-grade when XML, package, or local assets indicate supplementary sequence, activity, toxicity, method, or mechanism evidence may exist.
- For unsupported binary/image/archive formats, record exact file/member paths, extraction limits, and whether the limit affects identity, activity/toxicity, mechanism, or only peripheral context.
- In two-queue mode, this is a material-extraction queue role. It exhausts supplementary material and records locators/gaps; it does not make final mechanism or database conclusions.
- Deep retrieval is required for every assigned paper: inspect XML supplement
  references, OA package members, staged supplementary files, archives, images,
  spreadsheets, and legacy office files before declaring supplementary evidence
  absent or nonblocking.
- Use bounded best effort: try relevant local recovery tools for evidence-bearing
  files, record `unrecoverable_material_gaps` with checked paths/tools/impact
  when recovery fails, and move the paper onward instead of looping.


## Scope

- Read only supplementary sources under `papers/<paper_id>/source/`
- Write only:
  - `papers/<paper_id>/work/supp_evidence/`
  - `papers/<paper_id>/packet/extracted/` when two-queue packet mode is active
  - `papers/<paper_id>/packet/extraction/` when two-queue packet mode is active
  - `papers/<paper_id>/packet/locators/` when two-queue packet mode is active
  - `papers/<paper_id>/packet/rework/rework_responses.jsonl` only for a nonterminal `repair_ready_for_adjudication` owner response

## Stable execution path

Use the deterministic role runner only as a schema scaffold:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <paper_id> --worker worker-3
```

Expected canonical outputs:

- `papers/<paper_id>/work/supp_evidence/evidence.json`
- `papers/<paper_id>/work/supp_evidence/inspection_summary.md`

## Rules

- Do not claim any task except task `3`
- Stay inside the supplementary-evidence write boundary
- Do not inspect unrelated repo files

## Three-Layer Curation Addendum

When three-layer AMP curation is active, supplementary review should be evidence-critical-first rather than inventory-only.

Three-layer scaffold command:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <paper_id> --worker worker-3 --protocol amp_three_layer_v2
```

Additional output:

- `papers/<paper_id>/work/supplementary_methods/supplementary_evidence.json`
- `papers/<paper_id>/packet/extracted/supplementary_index.json`
- `papers/<paper_id>/packet/extracted/supplementary_text.jsonl`
- `papers/<paper_id>/packet/extracted/supplementary_tables.json`
- `papers/<paper_id>/packet/extracted/archive_manifest.json`
- `papers/<paper_id>/packet/extracted/ocr/`
- `papers/<paper_id>/packet/extraction/extraction_errors.jsonl`

Prioritize supplementary extraction in this order:

1. sequence and modification tables.
2. activity tables and MIC/MBC/IC50/EC50 rows.
3. toxicity tables and HC50/MHC/CC50/cell-viability rows.
4. mechanism figures/tables and direct assay evidence.
5. assay methods details such as medium, salt, serum, pH, temperature, incubation time, and statistics.

If only inventory is possible, record whether the unextracted supplement affects identity, activity/toxicity, mechanism, or only peripheral context. Do not label a missing or unparsed supplement as harmless unless the primary evidence is sufficient.

Before declaring supplementary evidence unavailable, try local recovery tools
when present: `/root/software/PaddleOCR/.venv/bin/python -m paddleocr`,
`/root/software/rar-tools/7zz`, `/root/software/rar-tools/extract-rar`,
`antiword`, `catdoc`, and `xls2csv`. Record every attempted command, output
path, and failure text in the packet extraction errors. Windows-facing tool
notes may refer to `Z:\root\software`; in WSL use `/root/software`.

When responding to analysis/adjudication feedback, only repair the requested
material gap and append a nonterminal owner-repair response with the new packet
version. Keep the ticket open for worker-6 final rebuild and strict adjudication;
worker-3 must not write a terminal closure status.

For a blocking quantitative-figure ticket, inspect the staged figure and recover
every requested visible bar or point with axis calibration, approximate raw
value, raw unit, uncertainty, image coordinates or equivalent calibration
evidence, exact-vs-approximate status, and treatment/control role. A null value
or unit is not a completed digitization when the plotted mark and axis can be
calibrated. If the asset or scale is genuinely insufficient, keep the ticket
open and record the exact material gap instead of using null placeholders as a
repair.

Do not close supplementary extraction as reliable when an evidence-bearing
supplement remains unparsed without OCR/archive/office recovery attempts and a
paper-specific impact assessment.
