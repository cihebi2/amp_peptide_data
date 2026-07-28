# Intake report: PMC11889930

- Worker: worker-1 / paper-intake-worker
- Generated: 2026-07-27T11:00:36Z
- Scope: checkout-local packet and paper roots only
- Claim boundary: intake inventory only; no source_verified or publication-grade claim

## Status

- Packet material queue status: `material_extracted_complete`
- Extraction status: `material_extracted_complete`
- Packet analysis queue status: `analysis_queued`
- Analysis status file: `analysis_queued`
- Publication-grade claimed by intake: `false`

## Inventoried Materials

- Paper XML source/raw mirror hash match: `True`
- Paper PDF source/raw mirror hash match: `True`
- Supplementary source/raw directory child count match: `True`
- XML sections/tables: `214` / `3`
- PDF pages: `17`
- Supplementary files/text/table counts: `3` / `1` / `1`
- Locator count: `235`
- Extraction quality error count: `0`

## Metadata Crosscheck

- Identifier crosscheck summary: `identifiers_consistent_where_present`
- DOI present consistently where available: `consistent_where_present`
- PMID present consistently where available: `consistent_where_present`
- PMCID present consistently where available: `consistent_all_sources`
- Title present in packet/raw/XML sources: `yes` / `no` / `yes`

## Database Provenance Boundary

- DBAASP machine candidate rows: `3`
- Linked authoritative article/assay/sequence/literature rows: `0` / `0` / `0` / `0`
- Source record links present: `False`
- Interpretation: machine candidate rows remain candidate evidence only.

## Rework State

- Runtime-open worker-1 tickets assigned: `0`
- Owner response appended: `false`
- Rework request rows: `0`
- Rework response rows: `0`

## Validation

- Packet gate exit code: `2`
- Packet gate manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11889930/work/intake/validation/one_paper_manifest.PMC11889930.json`
- Packet gate JSON: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11889930/work/intake/validation/check_two_queue_packets.PMC11889930.json`
- Packet gate hard finding: `missing_final_files`
- Packet gate interpretation: downstream final analysis/adjudication artifacts are absent; no packet files are missing.
- Source inventory JSON valid: `true`

## Cautions And Gaps

- Caution `packet_gate_missing_final_analysis_artifacts`: `downstream_analysis_adjudication_incomplete`
- Caution `dbaasp_codex_fallback_rows_candidate_only`: `preserved_candidate_machine_evidence`
- Caution `no_linked_authoritative_rows_present`: `database_snapshot_gap_preserved`
- Caution `image_supplement_present`: `staged_binary_asset_inventory_only`
- Caution `image_supplement_present`: `staged_binary_asset_inventory_only`
- No unresolved material blockers recorded by intake.

## Files Written

- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11889930/work/intake/source_inventory.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11889930/work/intake/intake_report.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11889930/work/intake/validation/check_two_queue_packets.PMC11889930.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11889930/work/intake/validation/check_two_queue_packets.PMC11889930.stdout.txt`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11889930/work/intake/validation/check_two_queue_packets.PMC11889930.stderr.txt`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11889930/work/intake/validation/one_paper_manifest.PMC11889930.json`
