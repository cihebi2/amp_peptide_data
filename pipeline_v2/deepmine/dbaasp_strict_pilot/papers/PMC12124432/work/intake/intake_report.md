# Worker-1 Intake Report: PMC12124432

## Scope
- worker_id: worker-1
- internet_used: false
- source_verified_claims_made: false
- publication_grade_claimed: false

## Material Status
- material_queue_status: material_extracted_with_gaps
- analysis_queue_status: analysis_needs_analysis_rework
- intake_status: source_inventory_complete_with_cautions_repair_ready_for_adjudication
- blocking_source_gap_count: 1
- extraction_error_count: 3

## Assets Inventoried
- primary_source_asset_count: 3
- supplementary_source_asset_count: 2
- supplementary_index_file_count: 2
- locator_count: 196
- database_machine_candidate_row_count: 37

## Ticket Reconciliation
- assigned_ticket_id: rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-003
- assigned_ticket_response_status: repair_ready_for_adjudication
- fresh_owner_response_line_no: 28
- live_open_ticket_count: 3
- same_live_open_ticket_count_everywhere: True
- reconciliation_artifact: pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12124432/work/intake/validation/worker1_ticket_state_reconciliation.json

## Final Mirror Audit
- final_json_record_count: 6
- byte_identical_count: 5
- declared_exception_count: 1
- unresolved_non_identical_count: 0
- mirror_audit_artifact: pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12124432/work/intake/validation/worker1_final_mirror_audit.json

## Validation
- packet_gate_return_code: 0
- packet_gate_hard_finding_count: 0
- semantic_gate_return_code: 1
- semantic_gate_publication_grade_pass_count: 0
- publication_quality_gate_return_code: 2
- publication_quality_gate_pass: False

## Downstream State
- worker1_lane_status: repair_ready_for_adjudication
- analysis_can_resume: true
- terminal_closure_owner: worker-6
- unresolved_blockers: live r03 tickets and preserved blocking source gap
