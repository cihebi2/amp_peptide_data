# Intake Report: PMC11531597

## Scope

- Worker lane: worker-1 / intake_linkage.
- Review boundary: local packet and paper files only; no internet access used.
- Output boundary: material inventory and provenance separation only; no database record verification or publication-grade conclusion is asserted.

## Material Inventory Status

- Packet material status before/after this intake review: `material_extracted_complete`.
- Analysis status was not changed: `analysis_queued`.
- Required paper source assets present: XML `true`, PDF `true`, supplementary files `1`.
- Required packet raw assets present: XML `true`, PDF `true`, supplementary files `1`.
- Supplementary files indexed: `1`; structured supplementary table rows: `0`.
- Extraction counts: XML sections `155`, XML tables `2`, PDF pages `12`, locator count `168`, extraction errors `0`.

## Database Provenance

- DBAASP Codex fallback candidate rows: `27`.
- Authoritative linked article/assay/sequence/literature row counts: `{'linked_article_records': 0, 'linked_assay_records': 0, 'linked_sequence_records': 0, 'linked_literature_records': 0}`.
- Fallback rows are retained as candidate machine evidence only and are not promoted to primary-source or authoritative database evidence by this lane.

## Rework State

- Rework request rows: `0`; response rows: `0`.
- Open intake-targeted tickets: `0`.

## Cautions And Blockers

- `oa_package_not_staged` (caution): No OA package members beyond the staged XML/PDF/supplementary assets are available from this packet; downstream workers should rely on declared packet materials only or request material rework if package members are required.
- `supplementary_tables_not_extracted` (caution): Supplementary file text/OCR surfaces are staged, but no structured supplementary table rows are present; downstream assay work may need table-specific material rework if it depends on supplementary tables.
- `authoritative_database_links_absent` (caution): Authoritative linked article/assay/sequence/literature snapshots are empty; DBAASP Codex fallback rows remain machine candidates only.
- `machine_rows_candidate_only` (caution): Fallback rows can seed downstream review but cannot support primary-source or database-record acceptance without source review by the analysis lanes.

- No blocking intake-owned gaps were found.

## Lane Decision

- Worker-1 lane status: `intake_source_reviewed_complete_with_cautions`.
- This is an intake/material-inventory decision only. Downstream database, activity, mechanism, and adjudication lanes must reopen packet sources and database rows before making scientific acceptance claims.
