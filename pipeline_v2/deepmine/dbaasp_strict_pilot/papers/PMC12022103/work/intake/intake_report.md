# Worker-1 Intake Report - PMC12022103

## Scope
- Worker lane: `worker-1` / paper intake.
- Paper root: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12022103`.
- Packet root: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12022103`.
- Web access used: `false`; all checks were local checkout/packet checks.
- Boundary: no `source_verified` database claims, no mechanism conclusions, no publication-grade acceptance, and no wet-lab guidance.

## Paper Identity
- PMCID present: `True`; PMID present: `True`; DOI present: `True`.
- Title/journal/year present in packet manifest: `True` / `True` / `True`.
- Metadata cross-check: packet manifest and database_source_manifest have matching present identifier fields; raw `paper_meta.json` is staging-oriented and minimal.

## Source Assets
- Paper source assets inventoried: `4` files.
- Packet raw assets inventoried: `4` files.
- Supplementary files staged: paper source `1`, packet raw `1`.
- Packet material queue status: `material_extracted_complete`; extraction status: `material_extracted_complete`.

## Extracted Surfaces
- XML sections: `135`; XML extraction errors: `0`.
- PDF text rows/pages: `12` / `12`; PDF tables: `2`.
- Figure captions: `15`.
- Supplementary index files: `1`; supplementary text rows: `4`; OCR text rows: `4`; supplementary tables: `0`.
- Archive members: `0`; extraction error rows: `0`.
- Locator count: `151`; locator source classes: `3`.

## Database Provenance
- Database manifest source: `DBAASP pending Codex fallback artifacts`.
- Machine candidate rows: `49`.
- Authoritative linked rows: article `0`, assay `0`, sequence `0`, literature `0`.
- Interpretation: DBAASP Codex fallback rows are candidate machine evidence only and require downstream paper-local source review before any scientific/database conclusion.

## Rework
- Open rework tickets for this paper: `0`.
- No worker-1-targeted rework response was written because no open ticket exists in the local rework request file.

## Cautions And Gaps
- `raw_paper_meta_minimal` (caution): Use packet_manifest/database_source_manifest metadata for DOI/PMID/PMCID cross-checks; do not treat raw paper_meta as a complete bibliographic record.
- `oa_package_not_staged` (caution): The packet has XML/PDF/supplement files, but no extra OA package/archive member surface to inspect.
- `supplementary_tables_not_normalized` (caution): Worker-3 should treat supplementary table absence as a review point before final activity/mechanism acceptance.
- `citation_map_not_normalized` (caution): Downstream workers should cite packet locators and database rows directly instead of relying on citation map normalization.
- `no_authoritative_dbaasp_or_merged_links` (major): DBAASP Codex fallback rows remain candidate machine evidence only; worker-4/6 cannot claim source_verified database linkage from authoritative rows.
- `machine_rows_candidate_only` (caution): Machine rows may seed review only after paper-local source checking; they are not primary-source evidence.

## Handoff Status
- Intake status: `source_reviewed_intake_complete_with_cautions` for material/source inventory only.
- Analysis status file was not changed; it remains owned by downstream analysis/adjudication lanes unless intake status changes require a queue update.
- Next owner lanes: `worker-2`, `worker-3`, `worker-4`, `worker-5`, `worker-6`.
