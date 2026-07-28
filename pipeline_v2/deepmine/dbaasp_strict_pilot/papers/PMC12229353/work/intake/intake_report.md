# Worker-1 Intake Report: PMC12229353

- Generated: 2026-07-08T16:27:50Z
- Scope: local checkout packet/material inventory only; no internet access used.
- Boundary: no `source_verified`, activity, toxicity, mechanism, or publication-grade claims are made by worker-1.
- DBAASP Codex fallback rows: treated as candidate machine evidence only.

## Status

- Intake lane status: `source_reviewed_complete_with_intake_cautions`
- Packet material queue status observed: `material_extracted_complete`
- Packet analysis queue status observed: `analysis_queued` / status file `analysis_queued`
- Open rework tickets targeting intake/material: `0`
- Unresolved intake blockers: `0`
- Publication-grade status: not claimed; downstream strict semantic/publication gates and worker-6 adjudication remain required.

## Inventoried Material Surfaces

| Surface | Status | Count / evidence |
| --- | --- | --- |
| XML raw/source | present | source/raw hash match: `True` |
| PDF raw/source | present | source/raw hash match: `True` |
| Paper metadata raw/source | present | source/raw hash match: `True` |
| Supplementary originals | present | packet files: `1` |
| OA package directory | absent | package source declared: `False` |
| Locator index | present | locators: `191` |
| Extraction errors | inventoried | errors: `0` |

## Extracted Surface Counts

| Artifact | Count / status |
| --- | --- |
| XML sections | `177` sections; errors `0` |
| PDF text JSONL | `13` records |
| PDF tables JSON | `2` tables |
| Figure captions JSON | `17` entries |
| Supplementary index | `1` files |
| Supplementary text JSONL | `1` records |
| Supplementary tables JSON | `0` tables |
| Archive manifest | `0` archives |

## Database Snapshot Boundary

| Row source | Count | Interpretation |
| --- | ---: | --- |
| linked_article_records | `0` | linked authoritative snapshot or empty |
| linked_assay_records | `0` | linked authoritative snapshot or empty |
| linked_sequence_records | `0` | linked authoritative snapshot or empty |
| linked_literature_records | `0` | linked authoritative snapshot or empty |
| dbaasp_machine_extracted_rows | `36` | candidate machine evidence only |
| codex_session_audit | `0` | audit metadata only |

## Cautions

- `oa_package_not_staged`: packet raw/oa_package is absent and staging_metadata.package_source is absent; Recorded as an intake caution. XML/PDF/supplement/database surfaces remain inventoried; no publication-grade claim is made by worker-1.
- `packet_manifest_known_missing_empty_despite_intake_caution`: known_missing_or_blocked_materials is empty in packet_manifest.json; Downstream adjudication should decide whether packet manifest needs targeted material rework.

## Output Files

- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12229353/work/intake/source_inventory.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12229353/work/intake/intake_report.md`

## Downstream Handoff

- Downstream workers should use packet locators and paper-local extracted artifacts only.
- Any database identity or assay claim must remain unresolved or database-only until verified by the appropriate analysis lane.
- Worker-6 adjudication and strict gates are still required before any publication-grade statement.
