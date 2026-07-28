# Worker-1 Intake Report: PMC13013390

- Generated at: `2026-07-15T11:10:00Z`
- Lane: `worker-1` material intake/linkage only.
- Scope: checkout-local packet and paper roots for `PMC13013390`; no internet access used.
- Boundary: no `source_verified` database claims and no publication-grade terminal claim.

## Status

- Intake material inventory status: `source_reviewed_complete_for_worker1_intake`
- Material queue status observed: `material_extracted_complete`
- Extraction status observed: `material_extracted_complete`
- Analysis queue status observed: `analysis_source_reviewed_accepted` (downstream observation only)
- Worker-1 open rework targets: `0`
- Blockers: `0`
- Cautions: `5`

## Material Inventory Counts

- Paper-local assets inventoried: `6`
- Packet raw assets inventoried: `6`
- Mirrored source/raw asset pairs checked: `6`
- XML section records: `160`
- PDF text JSONL rows: `16`
- PDF table records: `3`
- Figure caption records: `16`
- Supplementary index file records: `3`
- Supplementary text JSONL rows: `3`
- Supplementary structured table records: `2`
- Archive manifest entries: `0`
- Extraction error rows: `0`
- Locator index entries: `408`

## Database Snapshot Boundary

- DBAASP fallback machine candidate rows: `42`
- Linked article rows: `0`
- Linked assay rows: `0`
- Linked sequence rows: `0`
- Linked literature rows: `0`
- Interpretation: fallback rows are candidate machine evidence only; linked authoritative snapshots remain separate from paper-local source evidence.

## Rework State

- Rework request rows: `4`
- Rework response rows: `10`
- Open material-extraction ticket IDs: `[]`

## Cautions

- `no_linked_authoritative_database_rows`
- `machine_candidate_rows_present` (count=42)
- `packet_manifest_locator_count_mismatch` (packet_manifest_locator_count=179, locator_index_entry_count=408)
- `supplementary_file_without_structured_tables` (count=1)
- `model_gate_not_publication_grade_asserted_by_worker1`

## Blockers

- None for worker-1 intake.

## Files Written

- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13013390/work/intake/source_inventory.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13013390/work/intake/intake_report.md`
## Validation

- JSON validation paths: `3`
- Single-paper packet gate return code: `0`
- Packet gate paper count: `1`
- Packet gate hard findings: `0`
- Packet gate open rework tickets: `0`
- Packet gate JSON: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13013390/work/intake/gate_two_queue_packets.worker1.single.json`
