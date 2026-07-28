# Intake Report: PMC12715223

## Scope
- Worker: worker-1 / paper intake material inventory.
- Boundary: material inventory and provenance only; no `source_verified` database or scientific claims are made.
- Internet use: none; only this checkout was inspected.
- Machine evidence: DBAASP Codex fallback rows are retained as candidate machine evidence only.

## Identifier Cross-Check
- PMCID/PMID/DOI status: consistent where present across XML, packet manifest, and database source manifest.
- Raw metadata status: sparse for DOI/year/title; recorded as incomplete metadata, not as a conflict.

## Material Inventory
- Staged source/raw asset entries checked: 8.
- Source-vs-packet checksum mirror checks passing: 7/7.
- XML sections extracted: 158; XML extraction errors: 0.
- PDF text lines/pages: 13/13.
- Figure caption records: 18.
- Supplementary originals staged: 4; supplementary text lines: 61.
- Supplementary table records in normalized table artifact: 0.
- OCR JSONL outputs: 3.
- Archive members recorded: 0.
- Locator index count: 232.

## Database Snapshot
- DBAASP machine candidate rows: 7.
- Linked authoritative article/assay/literature/sequence rows: {'linked_article_records': 0, 'linked_assay_records': 0, 'linked_sequence_records': 0, 'linked_literature_records': 0}.
- Source-record links present: False.

## Cautions And Gaps
- No intake blockers found for the staged XML/PDF/supplement/database inventory.
- CAUTION `oa_package_directory_not_staged_in_checkout_packet`: explicitly_absent_in_local_packet; Primary XML/PDF and supplementary originals are staged; OA package members cannot be independently enumerated from this checkout-only run.
- CAUTION `supplementary_xlsx_row_level_tables_not_extracted_here`: workbook_level_inventory_only; Workbook readability and dimensions are recorded, but cell-level source evidence is not promoted to activity or mechanism evidence by worker-1.

## Rework State
- Runtime-open ticket IDs assigned to worker-1: none.
- Rework response appended: no, because no worker-1 ticket was assigned.

## Validation
- JSON validation: passed for `source_inventory.json` and current `analysis_status.json`.
- Packet gate artifact: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12715223/work/intake/check_two_queue_packets_worker1.json`.
- Packet gate result: material status `material_extracted_complete`, analysis status `analysis_queued`, locator count 232, hard finding `missing_final_files`.
- Interpretation: `missing_final_files` is downstream analysis/adjudication scope, not an intake material blocker.

## Status
- Intake lane status: `source_reviewed_intake_complete_with_cautions`.
- Publication-grade status: not claimed by worker-1.
- Analysis status file: unchanged by this run.
