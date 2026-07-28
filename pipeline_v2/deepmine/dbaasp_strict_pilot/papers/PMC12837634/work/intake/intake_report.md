# Intake Report: PMC12837634

- Worker: worker-1 / paper-intake-worker
- Protocol: amp_three_layer_v2 DBAASP strict pilot
- Internet use: none
- Claim boundary: material/database provenance inventory only; no `source_verified` claims made.
- Lane status: `source_reviewed_inventory_complete_with_material_cautions`

## Files Written

- `papers/PMC12837634/work/intake/source_inventory.json`
- `papers/PMC12837634/work/intake/intake_report.md`

## Source Surface Inventory

- Packet raw XML present: `True`
- Packet raw PDF present: `True`
- Packet supplementary ZIP present: `True`
- XML section rows: `118`
- PDF text rows/pages: `14`
- Supplementary index files: `1`
- Supplementary text rows: `0`
- Supplementary table rows: `0`
- Archive records: `1`
- Locator count: `132`

## Database Snapshot Boundary

- DBAASP machine candidate rows: `42`
- Linked article rows: `0`
- Linked assay rows: `0`
- Linked sequence rows: `0`
- Linked literature rows: `0`
- DBAASP fallback rows remain candidate machine evidence only.

## Metadata Cross-Check

- `doi`: `consistent_present`; missing sources: `2`
- `pmid`: `consistent_present`; missing sources: `2`
- `pmcid`: `consistent_present`; missing sources: `0`
- `title`: `conflict_preserved`; missing sources: `2`
- `year`: `consistent_present`; missing sources: `3`

## Material Cautions / Blockers

- `oa_package_not_staged`: `caution`; affected surface `raw/oa_package`
- `supplementary_zip_member_not_extracted_to_packet_text`: `major`; affected surface `extracted/supplementary_text.jsonl`
- `authoritative_dbaasp_links_absent`: `major`; affected surface `database/linked_*_records.jsonl`
- `source_record_links_present_false`: `major`; affected surface `database_source_manifest and authoritative_match_report`

## Analysis Status

- Analysis status file left unchanged: `analysis_queued`
- No worker-1 rework ticket responses appended because no runtime-open worker-1 tickets were assigned.

## Strict Gate Position

- This intake lane does not assert publication-grade completion.
- The packet still needs downstream source review/adjudication and targeted material/database follow-up for the cautions above.
