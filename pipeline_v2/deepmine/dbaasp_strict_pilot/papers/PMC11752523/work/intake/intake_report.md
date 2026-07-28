# Worker-1 Intake Report: PMC11752523

- Generated: `2026-07-15T11:37:36Z`
- Scope: checkout-local packet only; internet not used.
- Worker boundary: material/intake provenance only; no database identity, activity, mechanism, publication-grade, or source-verified claims are made here.

## Status

- Intake lane status: `material_inventory_complete_with_cautions`.
- Packet material status: `material_extracted_complete`; extraction status: `material_extracted_complete`.
- Blocking material gaps from worker-1 inventory: `0`.
- `analysis_status.json` not updated because the intake status did not change.
- Runtime-assigned ticket handled by this lane: `PMC11752523-rwk-0001`; fresh owner response is appended separately after artifact validation.

## Material Inventory

- Raw/staged source asset entries checked: `8`.
- Paper-source to packet-raw hash pairs checked: `4`; all matched: `True`.
- XML section container entries: `4`.
- PDF text rows: `13`.
- Supplementary text rows: `7`.
- Supplementary OCR rows: `7`.
- Extraction error rows: `0`.
- Locator entries: `3`; manifest locator count: `199`.

## Database Snapshot Boundary

- Database manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11752523/database/database_source_manifest.json`.
- Authoritative match report: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11752523/database/authoritative_match_report.json`.
- Linked authoritative JSONL row counts: `{'linked_article_records': 0, 'linked_assay_records': 0, 'linked_sequence_records': 0, 'linked_literature_records': 0}`.
- DBAASP fallback machine-candidate rows: `8`.
- Strict interpretation: linked authoritative files are present but empty; fallback rows are candidate machine evidence only.

## Rework Reconciliation

- Rework requests observed: `10`; responses before this pass: `37`.
- Assigned request records for `PMC11752523-rwk-0001`: `1`.
- Prior responses for assigned ticket before this pass: `2`.
- Packet manifest open ticket IDs: `[]`.
- Strict packet gate open rework ticket count: `10`.

## Validation Evidence

- Packet gate artifact: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11752523/work/intake/validation_packet_gate.worker1.current.json`; hard findings: `0`; locator count: `199`.
- Semantic gate artifact: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11752523/work/intake/validation_semantic_gate.worker1.current.json`; publication-grade pass count: `0`; fail count: `1`.
- Publication gate artifact: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11752523/work/intake/validation_publication_gate.worker1.current.json`; publication-grade pass: `False`; risk counts: `{'open_rework_targets': 1}`.

## Remaining Limits

- Worker-1 has no unresolved material blocker after this pass.
- Runtime-open ticket still requires worker-6 terminal adjudication; this lane can only return `repair_ready_for_adjudication`.
- Publication-grade completion is not claimed by worker-1.
- No biomedical source excerpts are embedded in this report.

