# Two-Queue Paper Packet Contract

Use this contract when Batch 2-Team AMP curation is split into a durable
material-extraction queue and a durable analysis/adjudication queue.

The queues are operationally independent, but they are not isolated. They
communicate through one per-paper packet directory plus structured rework
tickets. Do not use chat-only feedback as the production handoff between the
queues.

## Queue split

### Material extraction queue

The material queue prepares a source-grounded paper packet. It does not make
final database, mechanism, or publication-grade conclusions.

Responsibilities:

- stage XML, PDF, OA package, supplementary files, and metadata.
- extract text, tables, figure captions, supplementary tables, and OCR output.
- unpack archives and legacy office files before declaring material absent.
- build a locator index for every extracted claim surface.
- snapshot all linked APD6/DBAASP/DRAMP/database rows for the paper.
- record missing files, OCR failures, parse failures, and unextracted assets.
- emit extraction status only: complete, complete-with-gaps, or blocked.

Deep retrieval is mandatory for every paper. A material packet is not complete
just because XML/PDF paths exist; it must also enumerate OA package members,
supplementary files, archive members, OCR/office extraction attempts, database
row snapshots, and unresolved material gaps with tool/path/failure evidence.

### Analysis and adjudication queue

The analysis queue consumes paper packets. It should not rediscover materials
except when a packet gap blocks analysis; in that case it writes a rework ticket
to the material queue.

Responsibilities:

- audit database identity, sequence, modification, organism, citation, and
  cross-database conflicts.
- extract or normalize activity/toxicity evidence from packet materials and
  linked database rows.
- classify mechanism evidence strength without promoting inference or
  computation to direct mechanism.
- preserve conflicts and unresolved database-only rows.
- write final database/activity/mechanism/review artifacts only after
  source-reviewed packet evidence supports them.

Deep acquisition is mandatory for every paper. Existing packet `analysis/` or
`final/` files are prior artifacts only until an analysis worker re-opens the
packet sources, linked database rows, locators, and supplements for that paper
and records source-review provenance. Copied final files must never be promoted
to accepted analysis status by existence alone.

## Packet layout

Use one packet root per paper. The preferred future root is:

```text
paper_packets/<paper_id>/
```

When the existing workflow still writes under `papers/<paper_id>/`, mirror this
layout under `papers/<paper_id>/packet/` or map the existing `source/`, `work/`,
and `final/` files into the packet manifest. Do not require downstream analysis
workers to search unrelated folders.

Recommended layout:

```text
paper_packets/<paper_id>/
  packet_manifest.json
  raw/
    paper.xml
    paper.pdf
    supplementary_original/
    oa_package/
  extracted/
    xml_sections.json
    pdf_text.jsonl
    pdf_tables.json
    figure_captions.json
    supplementary_index.json
    supplementary_text.jsonl
    supplementary_tables.json
    archive_manifest.json
    ocr/
  database/
    linked_sequence_records.jsonl
    linked_literature_records.jsonl
    linked_experiment_records.jsonl
    linked_assay_records.jsonl
    database_source_manifest.json
  locators/
    locator_index.json
    citation_map.json
  extraction/
    extraction_status.json
    extraction_quality_report.json
    extraction_errors.jsonl
  analysis/
    database_record_audit.json
    activity_toxicity_evidence.json
    mechanism_evidence.json
    adjudication_report.json
  final/
    database_record_verification.json
    activity_toxicity_evidence.json
    mechanism_evidence.json
    final_conclusion.json
    review_report.json
  rework/
    rework_requests.jsonl
    rework_responses.jsonl
```

## Required packet metadata

`packet_manifest.json` should include:

- `paper_id`
- DOI, PMID, PMCID, title, journal, year when available.
- source roots and original paths for every staged file.
- packet version and update timestamp.
- material queue status and analysis queue status.
- database snapshot inputs and row counts.
- locator index path.
- open rework ticket IDs.
- known missing or blocked materials.

`extraction/extraction_status.json` should use only:

- `material_queued`
- `material_extracting`
- `material_extracted_complete`
- `material_extracted_with_gaps`
- `material_needs_rework`
- `material_blocked_missing_source`

`analysis/analysis_status.json` should use only:

- `analysis_queued`
- `analysis_running`
- `analysis_artifacts_present`
- `analysis_needs_material_rework`
- `analysis_needs_analysis_rework`
- `analysis_adjudicated_with_cautions`
- `analysis_source_reviewed_accepted`
- `analysis_accepted`
- `analysis_blocked`

`analysis_artifacts_present` means prior or copied layer/final artifacts exist;
it is not acceptance. `analysis_accepted` is valid only as a legacy alias for
`analysis_source_reviewed_accepted` when the review provenance proves deep
acquisition and worker-6 adjudication. New strict runs should prefer
`analysis_source_reviewed_accepted`.

## Locator requirements

Every extracted evidence item must carry a locator that can be resolved from
the packet, for example:

- `xml:sec=results:p=12`
- `pdf:page=7:block=3`
- `supp:s001.pdf:page=4:table=S2:row=5`
- `supp:s002.xlsx:sheet=MIC:row=12`
- `database:DBAASP:record=<id>`

Final analysis outputs must cite packet locators, not vague source names.
Claims without locators can be preserved only as unresolved or database-only
provenance.

## Local OCR and archive tools

Before declaring scanned/image/archive supplementary material unavailable, the
material queue should try the local recovery tools when present:

```text
/root/software/PaddleOCR/.venv/bin/python -m paddleocr
/root/software/rar-tools/7zz
/root/software/rar-tools/extract-rar
antiword
catdoc
xls2csv
```

Windows-facing notes may refer to `Z:\root\software`; in WSL this corresponds
to `/root/software`. Record the exact command attempted, source file, output
path, and failure text in `extraction/extraction_errors.jsonl`.

## Rework ticket contract

Quality control and analysis workers route feedback through packet rework
tickets. A ticket must say which queue owns the repair.

Required fields:

```json
{
  "ticket_id": "rwk-0001",
  "paper_id": "paper-id",
  "target_queue": "material_extraction",
  "severity": "blocking",
  "requested_by": "adjudicator",
  "reason": "Table S2 is cited by activity rows but is missing from extracted supplementary tables.",
  "requested_outputs": [
    {
      "asset": "raw/supplementary_original/s001.pdf",
      "need": "OCR and extract Table S2 row-level MIC records.",
      "required_locators": ["supp:s001.pdf:table=S2"]
    }
  ],
  "blocks": ["activity_toxicity_evidence", "final_conclusion"],
  "created_at": "ISO-8601 timestamp"
}
```

Valid `target_queue` values:

- `material_extraction`
- `analysis`
- `adjudication`

Valid `severity` values:

- `blocking`
- `major`
- `minor`
- `caution`

For quantitative table repairs, tickets may add machine-enforced observation
contracts:

```json
{
  "expected_observation_counts": {"xml:table-wrap:3": 24},
  "require_cell_locators": {"xml:table-wrap:3": true},
  "expected_cell_observations": {
    "xml:table-wrap:3:body-row=1:cell=2": {
      "endpoint": "percent hemolysis",
      "raw_value": "90",
      "raw_unit": "%",
      "treatment": "WOW peptide",
      "concentration": "5"
    }
  }
}
```

Each count key must contain exactly one table locator. A required cell table
must also have an explicit expected count. `expected_cell_observations` accepts
only `endpoint`, `raw_value`, `raw_unit`, `treatment`, `concentration`,
`target_species`, and `target_strain_or_isolate`, with non-empty scalar values.
The gate binds these fields to the named source cell; unique coordinates pasted
onto the wrong rows do not satisfy the contract.

Material rework closes with a response that records the new packet version,
added files, remaining gaps, and whether analysis can resume.

## OMX team and Ralph runtime rule

Use `$team` / `omx team ...` to run durable queue workers. Do not replace the
queue runtime with in-process fanout when durable shared state, mailbox, or
long-running tmux workers are needed.

Use `$ralph` / `omx ralph ...` as a separate persistence and verification
supervisor when the queue run must continue until every manifest item is either
accepted, explicitly cautioned, or blocked with a durable ticket. Do not use the
removed `omx team ralph` form.

Recommended operational split:

- material teams own packet creation and material rework tickets.
- analysis teams own database/activity/mechanism/adjudication from packets.
- Ralph supervises manifests, open tickets, team status, and final quality
  gates; it does not erase the queue boundary.

## Acceptance rule

Material acceptance means the packet is sufficiently extracted and all gaps are
explicit. It is not scientific acceptance.

Analysis acceptance means final artifacts are source-reviewed against the
packet, database rows, and locators. It is not proven by file existence,
`final_ready`, validator pass, deterministic role-runner output, or accelerator
auto-close.

Reliable-result acceptance additionally requires semantic gate pass,
publication-quality pass, paper-specific worker-6 provenance, material
exhaustion, and zero blocking rework targets. If a batch uses
`--allow-findings`, `--allow-risk`, or `|| true`, the result is diagnostic unless
the same paper later passes a strict non-allowing terminal gate.
