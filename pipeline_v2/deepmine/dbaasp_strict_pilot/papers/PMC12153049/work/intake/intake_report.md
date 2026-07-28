# Worker-1 Intake Report: PMC12153049

- generated_at: 2026-07-27T17:22:04Z
- worker: worker-1 / paper-intake-worker
- internet_used: false
- scope: packet-local material inventory and W1 stale-status ticket repair only
- scientific_identity_or_activity_verification_claims: false
- publication_grade_claimed: false

## Status

- intake_lane_status: intake_inventory_reviewed_complete_with_cautions
- material_queue_status_from_packet: material_extracted_complete
- analysis_queue_status_from_packet: analysis_needs_analysis_rework
- analysis_status_file_status: analysis_needs_analysis_rework
- analysis_status_updated_by_worker1: false

## Materials Inventoried

- primary_xml: exists=true, sections=57, xml_tables=0
- primary_pdf: exists=true, pdf_text_rows=11, pdf_pages=11
- supplementary_files: 1, supplementary_text_rows=19, supplementary_tables=1
- figures_or_captions_indexed: 12
- locator_count: 87
- extraction_error_rows: 0

## Database Provenance Boundary

- machine_candidate_rows: 12
- linked_authoritative_article_rows: 0
- linked_authoritative_assay_rows: 0
- linked_authoritative_sequence_rows: 0
- linked_authoritative_literature_rows: 0
- boundary: machine extraction/database snapshots are candidate provenance only for this lane

## Ticket Repair

- assigned_ticket: rwk-PMC12153049-campaign-r02-BF-PMC12153049-W1-FINAL-STATUS-AND-TICKET-STATE-STALE
- response_status_appended: repair_ready_for_adjudication
- current_open_rework_ticket_count_after_worker1_response: 3
- current_open_rework_ticket_ids_after_worker1_response: rwk-PMC12153049-campaign-r02-BF-PMC12153049-W1-FINAL-STATUS-AND-TICKET-STATE-STALE, rwk-PMC12153049-campaign-r02-BF-PMC12153049-W2-ACTIVITY-TOXICITY-EXACT-APPROX-STATUS-OMIT, rwk-PMC12153049-campaign-r02-BF-PMC12153049-W3-SUPPLEMENTARY-EXTRACTION-STATUS-COUNT-STAL
- terminal_closure_authority: worker-6 only

## Files Written

- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12153049/work/intake/source_inventory.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12153049/work/intake/intake_report.md
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12153049/final/materials_manifest.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12153049/final/materials_manifest.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12153049/final/review_report.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12153049/final/review_report.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12153049/rework/rework_responses.jsonl

## Validation

- packet_gate_return_code: 0
- semantic_gate_return_code: 0
- publication_gate_return_code: 0
- packet_gate_open_rework_ticket_count: 3
- semantic_publication_grade_pass_count: 1
- publication_gate_pass: True

## Unresolved Blockers

- none for worker-1 material inventory completeness within the supplied checkout
- terminal publication-grade acceptance remains outside worker-1 authority until worker-6 adjudicates/terminal-closes open r02 tickets
- r02 W2/W3 tickets are observed in packet state but are outside worker-1 response scope
