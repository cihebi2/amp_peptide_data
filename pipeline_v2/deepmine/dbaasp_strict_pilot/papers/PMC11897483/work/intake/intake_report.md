# Worker-1 Intake Report: PMC11897483

- generated_at: 2026-07-28T00:05:54Z
- worker: worker-1
- lane: material/intake inventory and ticket-state repair only
- source_verified_claims: none
- publication_grade_claim_by_worker1: false

## Material Inventory
- paper source files present: xml=True, pdf=True, meta=True
- packet raw mirrors match by sha256: xml=True, pdf=True, meta=True
- staged file entries inventoried: 8
- extraction status: material_extracted_complete
- extracted counts: xml_sections=182, xml_tables=4, pdf_pages=15, supplementary_files=0, supplementary_tables=0, extraction_errors=0
- locator count: 197

## Database Provenance
- database source manifest present: True
- authoritative match report present: True
- source record links present: False
- DBAASP fallback rows status: candidate_machine_evidence_only_not_source_verified_by_worker1

## Rework Ticket State
- assigned worker-1 tickets: 1
- owner-open tickets after worker-1 response: 0
- strict packet gate terminal-open tickets after worker-1 response: 2
- appended response status: repair_ready_for_adjudication
- packet_manifest open ticket count: 2
- analysis_status open ticket count: 2
- final materials manifests byte-identical: True
- final materials match strict terminal-open state: False

## Validation
- packet gate rc: 0
- semantic gate rc: 0
- publication gate rc: 0
- packet gate hard findings: 0

## Unresolved Blockers
- strict packet gate still counts two terminal-open tickets pending worker-6 closure/adjudication.
- final acceptance state needs worker-6/leader rebuild before publication-grade acceptance can be current.

## Cautions
- Worker-1 did not adjudicate database identity, activity/toxicity evidence, mechanism evidence, or publication-grade acceptance.
- Terminal ticket closure remains worker-6-only.
- Candidate machine database rows remain separate from source-reviewed claims.

## Artifacts
- source_inventory: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11897483/work/intake/source_inventory.json
- ticket_state_validation: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11897483/work/intake/validation/worker1_ticket_state_repair.json
- gate_run_summary: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11897483/work/intake/validation/worker1_gate_run_summary.json
- final_mirror_validation: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11897483/work/intake/validation/final_mirror_status_validation.json
