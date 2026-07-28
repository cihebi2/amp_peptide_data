# Pilot 20-Paper Validation Report

Generated at: `2026-06-22T03:12:51Z`

This is a 20-paper pilot over the v1 RC1 manual-validation manifest. It checks release-row/final-artifact consistency and status-specific evidence heuristics. It is not the final 420-row manual validation result.

## Scope

| Metric | Value |
| --- | ---: |
| selected papers | 20 |
| selected validation rows | 20 |
| pass | 20 |
| minor_error | 0 |
| major_error | 0 |
| critical_error | 0 |
| needs_rework | 0 |
| unverifiable | 0 |
| rework tickets | 0 |

## Status Coverage

| status | rows |
| --- | ---: |
| `database_only_no_primary_source` | 4 |
| `sequence_modified_not_normalized` | 4 |
| `source_conflict` | 5 |
| `source_verified` | 4 |
| `unresolved_record` | 3 |

## Database Coverage

| database | rows |
| --- | ---: |
| `APD6` | 4 |
| `CAMP` | 1 |
| `DBAASP` | 7 |
| `DRAMP` | 4 |
| `dbAMP` | 4 |

## Pilot Results

| pilot | paper | database/source | status | decision | notes |
| --- | --- | --- | --- | --- | --- |
| `PILOT20-001` | `doi__10.1007_s12539-016-0163-x` | `DBAASP / DBAASP:DBAASPS_12357` | `source_verified` | `pass` | status-specific evidence and paths passed |
| `PILOT20-002` | `doi__10.1002_cmdc.201900465` | `DRAMP / DRAMP:DRAMP32180` | `source_verified` | `pass` | status-specific evidence and paths passed |
| `PILOT20-003` | `doi__10.1038_s41598-018-29444-0` | `dbAMP / dbAMP:dbAMP_17348` | `source_verified` | `pass` | status-specific evidence and paths passed |
| `PILOT20-004` | `doi__10.1002_pro.5088` | `APD6 / AP04748` | `source_verified` | `pass` | status-specific evidence and paths passed |
| `PILOT20-005` | `doi__10.1038_s41598-017-03576-1` | `DBAASP / DBAASP:DBAASPS_10486` | `source_conflict` | `pass` | status-specific evidence and paths passed |
| `PILOT20-006` | `doi__10.1038_s41467-017-00419-5` | `DRAMP / DRAMP:DRAMP32082` | `source_conflict` | `pass` | status-specific evidence and paths passed |
| `PILOT20-007` | `doi__10.1021_acs.jmedchem.1c01033` | `dbAMP / dbAMP:dbAMP_32907` | `source_conflict` | `pass` | status-specific evidence and paths passed |
| `PILOT20-008` | `doi__10.3390_molecules23112943` | `APD6 / AP03030` | `source_conflict` | `pass` | status-specific evidence and paths passed |
| `PILOT20-009` | `doi__10.3389_fmicb.2021.693725` | `CAMP / CAMPSQ13698` | `source_conflict` | `pass` | status-specific evidence and paths passed |
| `PILOT20-010` | `doi__10.1021_acsomega.0c01462` | `DBAASP / DBAASP:DBAASPS_16976` | `sequence_modified_not_normalized` | `pass` | status-specific evidence and paths passed |
| `PILOT20-011` | `doi__10.1155_2015_197608` | `DRAMP / DRAMP:DRAMP35528` | `sequence_modified_not_normalized` | `pass` | status-specific evidence and paths passed |
| `PILOT20-012` | `doi__10.2174_1381612822666161027120518` | `dbAMP / dbAMP:dbAMP_18779` | `sequence_modified_not_normalized` | `pass` | status-specific evidence and paths passed |
| `PILOT20-013` | `doi__10.1021_acsomega.2c02778` | `APD6 / APD6:AP03820` | `sequence_modified_not_normalized` | `pass` | status-specific evidence and paths passed |
| `PILOT20-014` | `doi__10.1016_j.isci.2020.101785` | `DBAASP / DBAASP:DBAASPR_20591` | `database_only_no_primary_source` | `pass` | status-specific evidence and paths passed |
| `PILOT20-015` | `doi__10.1371_journal.pone.0138911` | `DRAMP / DRAMP31921` | `database_only_no_primary_source` | `pass` | status-specific evidence and paths passed |
| `PILOT20-016` | `doi__10.1038_srep24000` | `dbAMP / dbAMP_27310` | `database_only_no_primary_source` | `pass` | status-specific evidence and paths passed |
| `PILOT20-017` | `doi__10.1038_s41467-023-42434-9` | `APD6 / AP03779` | `database_only_no_primary_source` | `pass` | status-specific evidence and paths passed |
| `PILOT20-018` | `doi__10.1038_s41522-024-00637-y` | `DBAASP / DBAASP:DBAASPS_11338` | `unresolved_record` | `pass` | status-specific evidence and paths passed |
| `PILOT20-019` | `doi__10.1038_s41598-017-16784-6` | `DBAASP / DBAASPR_3442` | `unresolved_record` | `pass` | status-specific evidence and paths passed |
| `PILOT20-020` | `doi__10.21203_rs.3.rs-578319_v1` | `DBAASP / DBAASP:DBAASPS_17498` | `unresolved_record` | `pass` | status-specific evidence and paths passed |

## Interpretation

- `pass` means the pilot checker found matching release/final rows and enough status-specific rationale for this row.
- `unverifiable` for unresolved sentinel rows means the material gap must remain visible rather than being guessed away.
- Any `major_error`, `critical_error`, or `needs_rework` row is written to the pilot rework-ticket JSONL for owner-worker repair and worker-6 adjudication.
- This pilot does not prove the full 420-row validation set passed; it tests the validation workflow on 20 unique papers.
