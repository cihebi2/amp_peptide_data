# Worker-1 Intake Report: PMC12230126

## Status
- Lane status: `source_reviewed_intake_complete_with_cautions`.
- Publication-grade claimed: `false`.
- Analysis acceptance claimed: `false`.
- Source-verified/database/mechanism claims made: `false`.
- Internet used: `false`.
- Worker-1 assigned rework tickets this turn: `0`.

## Inventoried Material Surfaces
- Paper source root: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/source`.
- Packet raw root: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/raw`.
- XML, PDF, metadata, and one supplementary PDF are present in both paper source and packet raw locations with matching hashes.
- Optional OA package directory present: `false`.

## Extracted Surface Counts
- XML sections: `128`; XML extraction errors: `0`.
- PDF text JSONL rows: `16`.
- Supplementary index files: `1`; supplementary text JSONL rows: `7`.
- Locator count: `151`.
- Extraction quality errors: `0`.

## Database Snapshot Boundary
- DBAASP machine fallback rows: `22`.
- Linked authoritative article/assay/sequence/literature rows: `{'linked_article_records': 0, 'linked_assay_records': 0, 'linked_sequence_records': 0, 'linked_literature_records': 0}`.
- Source-record links present: `false`.
- Fallback rows remain candidate machine evidence only; worker-1 does not promote them to human/source-reviewed evidence.

## Rework State
- Rework request rows: `1`.
- Rework response rows: `0`.
- Worker-1 owner responses appended: `0`.

## Cautions
- `oa_package_not_staged`: No packet raw/oa_package directory and no package_source declared in local metadata; XML/PDF/supplement/database materials are inventoried, but worker-1 does not claim publication-grade deep retrieval.
- `packet_manifest_known_missing_empty_despite_oa_package_absent`: packet_manifest.json lists no known missing or blocked materials while the optional OA package directory is absent; downstream adjudication should decide whether a material rework ticket is needed.
- `authoritative_linked_rows_absent`: Authoritative DBAASP/merged linked row files are present but empty; machine fallback rows remain candidate evidence only.
- `non_intake_rework_request_present`: A packet rework request exists, but it is not assigned to worker-1 in the current authoritative ticket list; no owner response was appended by worker-1.

## Validation
- JSON syntax: `ok`.
- Packet gate artifact: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/intake/check_two_queue_packets_worker1_corrected.json`; exit code `2`; hard finding: `missing_final_files`; missing packet files: `0`; locator count: `151`.
- Semantic gate artifact: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/intake/semantic_three_layer_gate_worker1.json`; exit code `1`; issue codes: `missing_review_report`, `missing_activity_records`, `missing_database_record_verification`.
- Publication gate artifact: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/intake/check_three_layer_publication_quality_worker1.json`; exit code `2`; risk counts: `missing_final_file=4`.
- Gate failures are downstream analysis/adjudication blockers, not worker-1 source-material blockers.

## Output Files
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/intake/source_inventory.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/intake/intake_report.md`

## Downstream Handoff
- Intake is complete for material inventory purposes with the cautions above.
- Analysis workers should use packet locators and database snapshot files from the packet root only.
- `analysis/analysis_status.json` was not updated by worker-1 in this pass.
