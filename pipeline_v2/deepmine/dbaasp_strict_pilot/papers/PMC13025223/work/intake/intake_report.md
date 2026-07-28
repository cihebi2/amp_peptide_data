# Intake Report: PMC13025223

- worker_id: worker-1
- generated_at: 2026-07-27T19:26:02Z
- internet_used: false
- source_verified_claims_made: false
- material_queue_status_observed: material_extracted_complete
- extraction_status_observed: material_extracted_complete
- analysis_status_observed: analysis_needs_analysis_rework
- analysis_status_update_written: false

## Materials Inventory

- paper_source_asset_count: 3
- packet_raw_asset_count: 3
- source_to_packet_raw_sha256_checks_passed: 3 / 3
- locator_count: 112
- extraction_error_record_count: 0
- supplementary_file_count: 0

## Database Provenance Boundary

- dbaasp_machine_candidate_row_count: 2
- machine_candidate_rows_status: candidate_machine_evidence_only
- linked_article_record_count: 0
- linked_assay_record_count: 0
- linked_sequence_record_count: 0
- linked_literature_record_count: 0

## Final Inventory Repair

- materials_manifest_analysis_queue_status: analysis_needs_analysis_rework
- materials_manifest_open_rework_ticket_count: 2
- final_inventory_uncontracted_difference_count: 0
- final_inventory_contract_passed: true
- contracted_alias_files: materials_manifest.json, mechanism_evidence.json

## Rework Response

- ticket_id: rwk-PMC13025223-campaign-r01-BF-PMC13025223-W1-001-final-materials-status-and-mirror-inve
- response_status: repair_ready_for_adjudication
- analysis_can_resume: true
- live_open_rework_ticket_count_after_response: 2
- terminal_closure_required_by: worker-6

## Validation

- check_two_queue_packets_returncode: 0
- semantic_three_layer_gate_returncode: 0
- check_three_layer_publication_quality_returncode: 0
- source_inventory: pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/intake/source_inventory.json
- final_inventory_mirror_check: pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/intake/final_inventory_mirror_check.worker1.json
- worker1_single_paper_manifest: pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/intake/worker1_single_paper_manifest.json

## Lane Status

- worker_1_lane_status: repair_ready_for_adjudication
- unresolved_worker_1_blockers: none known after this repair
- unresolved_external_blockers: non-worker-1 open rework remains and worker-6 terminal adjudication is required
