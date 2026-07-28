# Worker-1 Intake Report: PMC13031288

Generated: `2026-07-15T14:56:54Z`  
Protocol: `amp_three_layer_v2_dbaasp_strict_pilot`  
Lane status: `intake_inventory_complete_with_cautions`  
Publication-grade claimed: `false`  
Source-verified claims made: `false`

## Scope

- Checkout-only run; no internet browsing used.
- Paper root: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13031288`
- Packet root: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13031288`
- Runtime-open ticket IDs assigned to worker-1: `[]`
- `analysis/analysis_status.json` was not changed; current status is `analysis_queued`.

## Metadata Cross-Check

- Parsed XML metadata matched packet/database manifest DOI/PMID/PMCID where present.
- Packet/database manifest DOI: `10.1038/s41598-026-40997-3`
- Packet/database manifest PMID: `41735465`
- Packet/database manifest PMCID: `PMC13031288`
- `raw/paper_meta.json` has null top-level DOI/title/year; staged-file provenance is still present.

## Raw Material Inventory

| Asset | Paper source exists | Packet raw exists | Hash match | Packet bytes |
| --- | --- | --- | --- | --- |
| `paper_xml` | true | true | true | 100295 |
| `paper_pdf` | true | true | true | 2393491 |
| `supplementary_original:41598_2026_40997_MOESM1_ESM.docx` | true | true | true | 29778 |
| `supplementary_original:41598_2026_40997_MOESM2_ESM.docx` | true | true | true | 39561 |
| `supplementary_original:41598_2026_40997_MOESM3_ESM.docx` | true | true | true | 26574 |

- PMC/OA package: `not_staged_not_available_in_packet`; `package_source` is null and `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13031288/raw/oa_package` is absent.
- Known missing or blocked materials in packet manifest: `0`.

## Extracted Material Inventory

- Material queue status: `material_extracted_complete`.
- XML sections: `121`; XML tables: `1`.
- PDF pages/text rows: `25` / `25`.
- Supplementary files/text rows/tables: `3` / `3` / `3`.
- Archive members: `0`.
- Locator count: `196`.
- Extraction errors: `0`.

## Database Provenance

- Database manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13031288/database/database_source_manifest.json`.
- DBAASP machine-extracted fallback rows: `34`; treated as candidate machine evidence only.
- Linked article/assay/sequence/literature rows: `0` / `0` / `0` / `0`.
- Codex session audit rows: `0`.

## Rework State

- Open ticket count observed by packet gate: `1`.
- Open ticket IDs observed: `rwk-PMC13031288-full-supplement-cell-coverage-001`.
- No worker-1 owner-repair response was appended because the authoritative assigned runtime-open ticket list is empty.

## Validation Artifacts

- Packet gate artifact: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13031288/work/intake/two_queue_packet_check_scoped.json`; return code `2`, hard findings `['missing_final_files']`.
- Semantic gate observation: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13031288/work/intake/semantic_three_layer_gate_observation.json`; return code `1`.
- Publication quality gate observation: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13031288/work/intake/publication_quality_gate_observation.json`; return code `2`.

## Unresolved Blockers / Cautions

- Final database/activity/mechanism/review artifacts are missing, so terminal semantic/publication gates do not pass.
- One open rework ticket remains in the packet, but it is not assigned to worker-1 in the runtime-open assignment list.
- No source verification or publication-grade acceptance is claimed from this intake lane.
