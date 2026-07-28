# Pilot20 Worker-6 Readjudication After Provenance Fix

Generated at: `2026-06-22T05:02:38Z`

This is a batch-level worker-6 style readjudication of the 20 true-review results after treating the `codex exec` runner header as valid model/effort provenance. It does not repair paper artifacts.

## Counts

| decision | count |
| --- | ---: |
| `accepted_with_cautions_confirmed` | 5 |
| `needs_targeted_rework` | 15 |

## Per-Paper

| pilot | status | paper | original | readjudicated | reason |
| --- | --- | --- | --- | --- | --- |
| `PILOT20-001` | `source_verified` | `doi__10.1007_s12539-016-0163-x` | `unverifiable_best_effort` | `accepted_with_cautions_confirmed` | `cautions_preserved` |
| `PILOT20-002` | `source_verified` | `doi__10.1002_cmdc.201900465` | `unverifiable_best_effort` | `needs_targeted_rework` | `rework_targets_present` |
| `PILOT20-003` | `source_verified` | `doi__10.1038_s41598-018-29444-0` | `needs_targeted_rework` | `needs_targeted_rework` | `rework_targets_present` |
| `PILOT20-004` | `source_verified` | `doi__10.1002_pro.5088` | `unverifiable_best_effort` | `accepted_with_cautions_confirmed` | `cautions_preserved` |
| `PILOT20-005` | `source_conflict` | `doi__10.1038_s41598-017-03576-1` | `unverifiable_best_effort` | `needs_targeted_rework` | `worker6_text_mentions_rework` |
| `PILOT20-006` | `source_conflict` | `doi__10.1038_s41467-017-00419-5` | `accepted_with_cautions_confirmed` | `accepted_with_cautions_confirmed` | `cautions_preserved` |
| `PILOT20-007` | `source_conflict` | `doi__10.1021_acs.jmedchem.1c01033` | `unverifiable_best_effort` | `accepted_with_cautions_confirmed` | `cautions_preserved` |
| `PILOT20-008` | `source_conflict` | `doi__10.3390_molecules23112943` | `unverifiable_best_effort` | `needs_targeted_rework` | `worker6_text_mentions_rework` |
| `PILOT20-009` | `source_conflict` | `doi__10.3389_fmicb.2021.693725` | `unverifiable_best_effort` | `needs_targeted_rework` | `worker6_text_mentions_rework` |
| `PILOT20-010` | `sequence_modified_not_normalized` | `doi__10.1021_acsomega.0c01462` | `unverifiable_best_effort` | `needs_targeted_rework` | `rework_targets_present` |
| `PILOT20-011` | `sequence_modified_not_normalized` | `doi__10.1155_2015_197608` | `needs_targeted_rework` | `needs_targeted_rework` | `rework_targets_present` |
| `PILOT20-012` | `sequence_modified_not_normalized` | `doi__10.2174_1381612822666161027120518` | `needs_targeted_rework` | `needs_targeted_rework` | `rework_targets_present` |
| `PILOT20-013` | `sequence_modified_not_normalized` | `doi__10.1021_acsomega.2c02778` | `unverifiable_best_effort` | `needs_targeted_rework` | `worker6_text_mentions_rework` |
| `PILOT20-014` | `database_only_no_primary_source` | `doi__10.1016_j.isci.2020.101785` | `needs_targeted_rework` | `needs_targeted_rework` | `rework_targets_present` |
| `PILOT20-015` | `database_only_no_primary_source` | `doi__10.1371_journal.pone.0138911` | `unverifiable_best_effort` | `accepted_with_cautions_confirmed` | `cautions_preserved` |
| `PILOT20-016` | `database_only_no_primary_source` | `doi__10.1038_srep24000` | `unverifiable_best_effort` | `needs_targeted_rework` | `rework_targets_present` |
| `PILOT20-017` | `database_only_no_primary_source` | `doi__10.1038_s41467-023-42434-9` | `needs_targeted_rework` | `needs_targeted_rework` | `rework_targets_present` |
| `PILOT20-018` | `unresolved_record` | `doi__10.1038_s41522-024-00637-y` | `unverifiable_best_effort` | `needs_targeted_rework` | `rework_targets_present` |
| `PILOT20-019` | `unresolved_record` | `doi__10.1038_s41598-017-16784-6` | `unverifiable_best_effort` | `needs_targeted_rework` | `rework_targets_present` |
| `PILOT20-020` | `unresolved_record` | `doi__10.21203_rs.3.rs-578319_v1` | `unverifiable_best_effort` | `needs_targeted_rework` | `rework_targets_present` |

## Interpretation

- Model-provenance downgrade was removed only when the packet `codex_exec.stderr.log` header proved `model: gpt-5.5` and `reasoning effort: xhigh`.
- Any non-empty `rework_targets` still forces `needs_targeted_rework`.
- `accepted_with_cautions_confirmed` is not clean; it means cautions/conflicts remain publication-visible.
- This readjudication does not edit `papers/<paper_id>/final/`; owner-worker repair and worker-6 artifact update remain separate steps.
