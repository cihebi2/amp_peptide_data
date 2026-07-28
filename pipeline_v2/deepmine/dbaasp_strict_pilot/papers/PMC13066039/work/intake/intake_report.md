# PMC13066039 worker-1 intake report

Generated: 2026-07-27T08:04:40+00:00

## Status

- Intake lane status: `intake_material_inventory_complete_with_cautions`.
- Packet material queue status observed: `material_extracted_complete`.
- Packet analysis queue status observed: `analysis_queued`; this file was not updated by worker-1.
- Scope: material/source inventory and database provenance only. No `source_verified` biological, activity, mechanism, or database identity claims are made here.
- Leader preflight contracts: none listed. Runtime-open worker-1 rework tickets: none listed.

## Source And Packet Roots

- Paper source root: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/source`.
- Packet root: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039`.
- Packet manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/packet_manifest.json`.
- Database source manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/database_source_manifest.json`.

## Material Coverage

- XML source and packet raw XML present: `True` / `True`; SHA-256 match: `True`.
- PDF source and packet raw PDF present: `True` / `True`; SHA-256 match: `True`.
- Metadata source and packet raw metadata present: `True` / `True`; SHA-256 match: `True`.
- XML extracted rows: `112`; selected tag counts are recorded in `source_inventory.json`.
- PDF text rows/pages: `14` / `14`.
- Figure caption entries: `16`.
- Extracted PDF tables / supplementary tables: `0` / `0`.
- Supplementary files/text rows/archives listed: `0` / `0` / `0`.
- Locator index rows: `126`.
- Extraction error rows: `0`. Packet-declared missing/blocked material entries: `0`.

## Metadata Cross-Check

- Observed metadata fields with agreement among available sources: `doi, pmcid, pmid, year, title, journal`.
- Observed metadata fields with conflicting values: `none`.
- Exact observed metadata values are in `source_inventory.json`; this report does not reproduce source text.

## Database Provenance

- Authoritative linked article/assay/sequence/literature rows: `0` / `0` / `0` / `0`.
- DBAASP fallback machine candidate rows: `3`.
- Database row counts match `database_source_manifest.json`: `True`.
- DBAASP fallback rows are recorded only as candidate machine evidence. They are not human/source-reviewed claims.

## Cautions And Blockers

- No worker-1 blocking material gaps were found in the current packet inventory.
- Material note `oa_package`: `not_staged_in_current_packet`.
- Material note `supplementary_assets`: `none_listed_in_packet`.
- Material note `archives`: `none_listed_in_packet`.
- Caution `no_authoritative_linked_database_rows`: `caution`.
- Caution `dbaasp_fallback_rows_candidate_only`: `caution`.

## Handoff

- Worker-2 safe activity candidate handoff present: `True`; status: `candidate_handoff_only_for_worker_2`.
- Material inventory ready for downstream workers: `True`.
- Downstream workers must reopen packet sources and preserve database/machine candidate boundaries before making analysis claims.

## Validation

- `source_inventory.json` passed JSON validation.
- Packet gate scoped to one paper wrote `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/work/intake/packet_gate_worker1.json` and exited `2` with hard findings: `missing_final_files`.
- Interpretation: material packet files are present with zero extraction errors; the hard finding is downstream `missing_final_files` while analysis is still queued.
