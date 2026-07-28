# Worker-1 Intake Report: PMC13036774

## Scope And Guardrails
- Lane: worker-1 paper intake / material extraction inventory.
- Internet used: no.
- Source-verified database claims made: no.
- Publication-grade claim made: no.
- DBAASP fallback rows: candidate machine evidence only.

## Packet Status
- Packet manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13036774/packet_manifest.json`
- Packet version: `dbaasp_strict_pilot_v1`
- Material queue status observed: `material_extracted_complete`
- Analysis queue status observed: `analysis_queued`
- Known missing/blocked materials in manifest: `0`

## Inventoried Material Counts
- Raw material files inventoried: `5`
- XML sections: `115`; XML extraction errors: `0`
- PDF text rows: `15`; PDF table objects: `0`
- Supplementary files indexed: `2`; supplementary text rows: `51`
- OCR text rows: `51`; archive records: `1`; archive members counted: `537`
- Locator count: `181`

## Database Provenance Inventory
- Database manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13036774/database/database_source_manifest.json`
- Authoritative match report: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13036774/database/authoritative_match_report.json`
- Linked authoritative article/assay/sequence/literature rows: `0`
- DBAASP machine candidate rows: `3`
- Database provenance status: `machine_candidates_only_no_authoritative_linked_rows`
- Machine rows were not promoted to source-reviewed evidence.

## Rework State
- Rework request rows: `0`
- Rework response rows: `0`
- Open worker-1/material tickets: `0`

## Worker-1 Decision
- Worker-1 status: `intake_source_inventory_complete_with_cautions`
- Analysis status changed by worker-1: `false`
- Cautions:
  - `database_machine_candidates_only` (caution)
  - `no_authoritative_source_record_links` (caution)
- Unresolved blockers: none for worker-1 intake material inventory.

Downstream layers must reopen packet sources and linked database snapshots before making database, activity, toxicity, or mechanism conclusions.
