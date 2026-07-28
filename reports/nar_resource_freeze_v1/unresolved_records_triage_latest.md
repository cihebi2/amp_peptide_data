# Unresolved Record Triage

Generated at: `2026-06-20T02:53:46+00:00`

## Summary

| Metric | Count |
| --- | ---: |
| unresolved records | 56 |
| papers with unresolved records | 3 |

## By Database

| database | count |
| --- | ---: |
| `DBAASP` | 56 |

## By Blocker Class

| blocker_class | count | target |
| --- | ---: | --- |
| `material_gap_unspecified` | 2 | `source_staging` |
| `missing_or_unparsed_supplement` | 28 | `source_staging_or_supplement_recovery` |
| `row_level_source_mapping_ambiguous` | 1 | `database_row_mapping_rework` |
| `synergy_partner_or_fici_mapping_ambiguous` | 25 | `database_row_mapping_rework` |

## Top Papers

| paper_id | unresolved rows |
| --- | ---: |
| `doi__10.1038_s41522-024-00637-y` | 30 |
| `doi__10.1038_s41598-017-16784-6` | 24 |
| `doi__10.21203_rs.3.rs-578319_v1` | 2 |

## Next Action Policy

- Do not convert `unresolved_record` to `source_verified` without locating primary-source evidence.
- Missing supplements or row-level ambiguity should be routed to source staging / database-row mapping rework.
- If the required material remains unavailable after best effort, keep unresolved and disclose it in the release notes.
