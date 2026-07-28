# Worker-1 Intake Report: PMC13031788

- Generated at: `2026-07-15T11:11:50Z`
- Lane: `worker-1` intake/material inventory only.
- Source text excerpts embedded: `false`. Source-verified claims made: `false`. Publication-grade claimed by worker-1: `false`.

## Packet Materials
- Material status: `material_extracted_complete`; extraction status: `material_extracted_complete`.
- Source/raw hash comparisons: `4/4` matched.
- Staged manifest entries: `8`; all marked present: `True`.
- Extracted XML sections: `157`; PDF text rows: `30`; PDF tables: `5`; figure captions: `29`.
- Supplementary raw workbooks: `1`; supplementary extracted text rows: `0`; supplementary extracted tables: `0`.
- Locator count: `187`; extraction error rows: `0`.

## Database Provenance
- Authoritative linked row files: article `0`, assay `0`, sequence `0`, literature `0`.
- DBAASP machine fallback rows: `35`; treatment: candidate machine evidence only.
- `source_record_links_present`: `False`; `authoritative_dbaasp_ingest_ready`: `False`.

## Rework
- Packet open rework ticket count: `0`.
- Worker-1 target ticket IDs: `rwk-PMC13031788-w6-002`.
- Worker-1 ticket closure markers: `rwk-PMC13031788-w6-002`.
- Analysis can resume after worker-1 response: `True`.

## Validation
- Packet gate return code: `0`.
- Packet gate hard findings: `0`; open tickets from gate: `0`.
- Gate JSON: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13031788/work/intake/check_two_queue_packets.worker1.refresh.json`.
- `analysis_status.json` update performed: `false`; current status: `analysis_source_reviewed_accepted`.

## Cautions
- `authoritative_linked_database_rows_absent` (downstream_database_audit).
- `machine_fallback_rows_present` (all_analysis_lanes).
- `supplementary_workbook_raw_only_in_packet_extracts` (material_and_activity_lanes).
- `downstream_acceptance_observed_not_worker1_claim` (worker-1).
- `authoritative_dbaasp_ingest_ready_false` (database_pipeline).

## Boundaries
- Worker-1 does not make database identity, activity, toxicity, mechanism, `source_verified`, or publication-grade claims.
- DBAASP fallback rows remain machine candidates until downstream source review.
- Overall downstream acceptance fields observed in packet files are recorded only as packet state, not as a worker-1 claim.
