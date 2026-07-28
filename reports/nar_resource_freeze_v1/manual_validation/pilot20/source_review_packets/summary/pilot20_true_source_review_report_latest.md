# Pilot20 True Source-Review Summary

Generated at: `2026-06-22T04:33:33Z`

This summarizes fresh Codex CLI source-review results for the 20-paper pilot. It supersedes the earlier structural/status-evidence `pass=20` interpretation for these 20 papers.

## Headline

- Result JSON files: `20` / 20.
- Runner validation: see `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/runner/true_source_review_summary_latest.json`.
- Clean `pass_source_review`: `0`.
- Accepted with cautions confirmed: `1`.
- Needs targeted rework: `5`.
- Unverifiable after best effort: `14`.
- Consolidated rework/material tickets: `11`.

## Decision Counts

| decision | count |
| --- | ---: |
| `accepted_with_cautions_confirmed` | 1 |
| `needs_targeted_rework` | 5 |
| `unverifiable_best_effort` | 14 |

## Substantive Flags

| flag | count |
| --- | ---: |
| `accepted_with_cautions_substantive` | 8 |
| `has_rework_targets_despite_best_effort` | 6 |
| `needs_targeted_rework` | 5 |
| `worker6_mentions_needs_targeted_rework` | 1 |

## Per-Paper Results

| pilot | status | database | paper | decision | substantive flag | rework | cautions | limits |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `PILOT20-001` | `source_verified` | `DBAASP` | `doi__10.1007_s12539-016-0163-x` | `unverifiable_best_effort` | `accepted_with_cautions_substantive` | 0 | 6 | 4 |
| `PILOT20-002` | `source_verified` | `DRAMP` | `doi__10.1002_cmdc.201900465` | `unverifiable_best_effort` | `has_rework_targets_despite_best_effort` | 2 | 3 | 3 |
| `PILOT20-003` | `source_verified` | `dbAMP` | `doi__10.1038_s41598-018-29444-0` | `needs_targeted_rework` | `needs_targeted_rework` | 1 | 4 | 3 |
| `PILOT20-004` | `source_verified` | `APD6` | `doi__10.1002_pro.5088` | `unverifiable_best_effort` | `accepted_with_cautions_substantive` | 0 | 6 | 3 |
| `PILOT20-005` | `source_conflict` | `DBAASP` | `doi__10.1038_s41598-017-03576-1` | `unverifiable_best_effort` | `worker6_mentions_needs_targeted_rework` | 0 | 4 | 4 |
| `PILOT20-006` | `source_conflict` | `DRAMP` | `doi__10.1038_s41467-017-00419-5` | `accepted_with_cautions_confirmed` | `accepted_with_cautions_substantive` | 0 | 6 | 4 |
| `PILOT20-007` | `source_conflict` | `dbAMP` | `doi__10.1021_acs.jmedchem.1c01033` | `unverifiable_best_effort` | `accepted_with_cautions_substantive` | 0 | 4 | 2 |
| `PILOT20-008` | `source_conflict` | `APD6` | `doi__10.3390_molecules23112943` | `unverifiable_best_effort` | `accepted_with_cautions_substantive` | 0 | 4 | 4 |
| `PILOT20-009` | `source_conflict` | `CAMP` | `doi__10.3389_fmicb.2021.693725` | `unverifiable_best_effort` | `accepted_with_cautions_substantive` | 0 | 5 | 4 |
| `PILOT20-010` | `sequence_modified_not_normalized` | `DBAASP` | `doi__10.1021_acsomega.0c01462` | `unverifiable_best_effort` | `has_rework_targets_despite_best_effort` | 1 | 4 | 4 |
| `PILOT20-011` | `sequence_modified_not_normalized` | `DRAMP` | `doi__10.1155_2015_197608` | `needs_targeted_rework` | `needs_targeted_rework` | 1 | 5 | 2 |
| `PILOT20-012` | `sequence_modified_not_normalized` | `dbAMP` | `doi__10.2174_1381612822666161027120518` | `needs_targeted_rework` | `needs_targeted_rework` | 2 | 5 | 3 |
| `PILOT20-013` | `sequence_modified_not_normalized` | `APD6` | `doi__10.1021_acsomega.2c02778` | `unverifiable_best_effort` | `accepted_with_cautions_substantive` | 0 | 5 | 4 |
| `PILOT20-014` | `database_only_no_primary_source` | `DBAASP` | `doi__10.1016_j.isci.2020.101785` | `needs_targeted_rework` | `needs_targeted_rework` | 2 | 4 | 3 |
| `PILOT20-015` | `database_only_no_primary_source` | `DRAMP` | `doi__10.1371_journal.pone.0138911` | `unverifiable_best_effort` | `accepted_with_cautions_substantive` | 0 | 3 | 1 |
| `PILOT20-016` | `database_only_no_primary_source` | `dbAMP` | `doi__10.1038_srep24000` | `unverifiable_best_effort` | `has_rework_targets_despite_best_effort` | 2 | 5 | 3 |
| `PILOT20-017` | `database_only_no_primary_source` | `APD6` | `doi__10.1038_s41467-023-42434-9` | `needs_targeted_rework` | `needs_targeted_rework` | 1 | 4 | 3 |
| `PILOT20-018` | `unresolved_record` | `DBAASP` | `doi__10.1038_s41522-024-00637-y` | `unverifiable_best_effort` | `has_rework_targets_despite_best_effort` | 3 | 5 | 5 |
| `PILOT20-019` | `unresolved_record` | `DBAASP` | `doi__10.1038_s41598-017-16784-6` | `unverifiable_best_effort` | `has_rework_targets_despite_best_effort` | 1 | 4 | 3 |
| `PILOT20-020` | `unresolved_record` | `DBAASP` | `doi__10.21203_rs.3.rs-578319_v1` | `unverifiable_best_effort` | `has_rework_targets_despite_best_effort` | 2 | 5 | 3 |

## Interpretation

- The earlier `pilot20` structural checker proved evidence pointers were usable; it did not prove scientific acceptance.
- Fresh source review found no clean `pass_source_review` cases in this pilot.
- Most nonterminal results are not proof that the database row is wrong; they mean the reviewer found preserved cautions, material limits, ontology repair needs, or insufficient proof to promote the row to clean acceptance.
- Several `unverifiable_best_effort` decisions are affected by model-provenance self-verification caution even though the runner command and stderr header record `gpt-5.5` and `xhigh`; the prompt should be revised before scaling to 420 rows so the reviewer can treat runner provenance as sufficient runtime evidence.
- Rows with `needs_targeted_rework` or non-empty rework targets must be sent back to the owner lane and then re-adjudicated by worker-6 before publication-grade acceptance.

## Outputs

- Results CSV: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/summary/pilot20_true_source_review_results_latest.csv`
- Consolidated tickets JSONL: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/summary/pilot20_true_source_review_rework_tickets_latest.jsonl`
- Summary JSON: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/summary/pilot20_true_source_review_summary_latest.json`
