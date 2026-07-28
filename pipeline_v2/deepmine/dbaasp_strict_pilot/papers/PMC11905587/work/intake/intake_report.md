# Worker-1 Intake Report: PMC11905587

Generated: 2026-07-16T14:07:32Z

## Scope
- Worker: worker-1 / intake
- Paper root: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587`
- Packet root: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11905587`
- Internet use: none
- Layer-1 identity, activity, mechanism, and terminal publication-grade decisions: not made in this lane

## Lane Status
- Worker-1 intake status: `source_reviewed_intake_complete_with_cautions`
- Current packet material status: `material_extracted_complete`
- Current packet analysis status: `analysis_queued`
- `analysis_status.json` update: not modified
- Worker-1 targeted rework required now: no
- Publication-grade claim: no

## Metadata Cross-Check
- Identifier fields checked across packet manifest, packet raw metadata, paper source metadata, final materials manifest metadata, and database source manifest: `doi`, `pmid`, `pmcid`
- DOI values match where present: `True`
- PMID values match where present: `True`
- PMCID values match where present: `True`
- Title presence was checked by hash only; no title text is repeated in this report.

## Paper-Local Source Surfaces
- Packet raw files inventoried: `5`
- Paper `source/` files inventoried: `5`
- Packet/source hash mirror match for all raw files: `True`
- XML sections: `138`
- XML tables: `2`
- PDF pages: `12`
- PDF tables: `2`
- Figure locator records: `22`
- Supplementary originals: `2`
- Supplementary text records: `2`
- Supplementary tables: `1`
- Archive members recorded: `0`
- Extraction error records: `0`
- Locator count: `221`

## Database Snapshot Separation
- Database source manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11905587/database/database_source_manifest.json`
- Authoritative match report: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11905587/database/authoritative_match_report.json`
- Linked article records: `0`
- Linked assay records: `0`
- Linked sequence records: `0`
- Linked literature records: `0`
- DBAASP fallback candidate rows: `5`
- DBAASP candidate row fields: `assay_medium, endpoint, evidence, inoculum, modification, paper_id, peptide, sequence, target, unit, value, verdict`
- Interpretation: DBAASP fallback rows remain machine candidates only; this lane does not convert them into primary-source-reviewed database evidence.

## Rework
- Runtime-open ticket IDs assigned to worker-1: none
- Rework request rows present: `0`
- Rework response rows appended by worker-1 in this run: none

## Cautions / Blockers
- OA package directory: absent from packet and inventoried as absent; raw XML, PDF, and supplements are present.
- Linked authoritative database row files: empty; downstream Layer-1 audit must rely on explicit database-only or unresolved statuses unless primary locators are established.
- Documented scaffold runner path: unavailable in this checkout; failure is logged at `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/work/intake/role_runner_worker1.log`.
- Required gpt-5.5/xhigh runtime provenance: not proven in this worker lane; no publication-grade terminal acceptance is claimed.

## Artifacts
- Source inventory JSON: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/work/intake/source_inventory.json`
- Intake report: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/work/intake/intake_report.md`
- Packet gate JSON target: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/work/intake/check_two_queue_packets_worker1.json`
- Packet gate log target: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/work/intake/check_two_queue_packets_worker1.log`
## Validation
- `source_inventory.json` JSON validation: passed
- `intake_report.md` non-empty check: passed
- Packet gate manifest: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/work/intake/packet_gate_manifest_worker1.json`
- Packet gate JSON: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/work/intake/check_two_queue_packets_worker1.json`
- Packet gate exit code: `2`
- Packet gate paper count: `1`
- Packet gate material status: `material_extracted_complete`
- Packet gate analysis status: `analysis_queued`
- Packet gate locator count: `221`
- Packet gate extraction error count: `0`
- Packet gate hard findings: `missing_final_files`
- Packet gate missing packet files: `0`
- Packet gate missing final files: `4`
- Interpretation: material packet is structurally present for worker-1 intake, but terminal structural/publication readiness is blocked by absent downstream final analysis artifacts.
