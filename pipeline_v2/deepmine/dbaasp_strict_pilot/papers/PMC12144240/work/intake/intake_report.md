# Worker-1 Intake Report: PMC12144240

- generated_at: `2026-07-08T21:43:46+00:00`
- lane: `worker-1/intake_linkage`
- scope: checkout-local packet and paper source assets only; no internet browsing
- claim boundary: material/provenance inventory only; no `source_verified` claims and no scientific/database conclusions

## Status

- packet_version: `dbaasp_strict_pilot_v1`
- material_queue_status: `material_extracted_complete`
- extraction_status: `material_extracted_complete`
- analysis_status: `analysis_queued`
- staged_files: `8` total, `8` present
- known_missing_or_blocked_materials: `0`
- open_worker1_or_material_rework_tickets: `0`

## Paper And Packet Roots

- paper_root: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12144240`
- source_root: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12144240/source`
- packet_root: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12144240`
- packet_manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12144240/packet_manifest.json`

## Material Inventory Counts

- source_files: `4`
- packet_raw_files: `4`
- xml_sections: `118`
- xml_tables: `0`
- pdf_pages: `12`
- pdf_text_jsonl_rows: `12`
- supplementary_files: `1`
- supplementary_text_jsonl_rows: `5`
- ocr_output_jsonl_rows: `5`
- archive_count: `0`
- extraction_errors: `0`
- locator_count: `135`

## Database Snapshot Boundary

- dbaasp_machine_extracted_rows: `24`
- linked_article_records: `0`
- linked_assay_records: `0`
- linked_sequence_records: `0`
- linked_literature_records: `0`
- source_record_links_present: `False`
- interpretation: DBAASP fallback rows are machine-candidate evidence only and remain separate from authoritative linked rows.

## Hash/Path Checks

- source_to_packet_basename_pairs_checked: `4`
- source_to_packet_sha256_matches: `4`
- detailed file paths, sizes, and hashes are in `source_inventory.json`.

## Cautions / Blockers

- no open rework ticket currently targets worker-1/material extraction
- no authoritative linked article/assay/sequence/literature records are present in the packet snapshot
- DBAASP fallback rows must remain machine candidates until downstream source review establishes primary-source locators or database-only status
- PDF and supplementary table extraction files have zero parsed table rows; downstream lane should use packet locators or create a material rework ticket if table-level evidence is required

## Worker-1 Outcome

- lane_outcome: `intake_material_inventory_complete_with_database_linkage_caution`
- analysis_status_updated: `false`
- publication_grade_claim: `false`
- source_verified_claims: `false`
