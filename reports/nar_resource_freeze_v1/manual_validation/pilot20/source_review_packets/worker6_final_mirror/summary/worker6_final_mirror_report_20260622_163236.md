# Pilot20 Worker-6 Final Mirror Summary

Generated at: `2026-06-22T08:32:36Z`

This report summarizes worker-6 final mirror/re-adjudication after owner-worker rework responses. It distinguishes accepted papers from nonterminal blocked/rework cases.

## Counts

| metric | value |
| --- | ---: |
| selected dispatches | 11 |
| valid worker-6 responses | 11 |
| accepted_with_cautions | 7 |
| nonterminal | 4 |
| publication_grade true | 7 |
| accepted files with bad mechanism classes | 0 |
| nonterminal files with bad mechanism classes | 13 |
| review-report validation problems | 0 |

## Final Decisions

| final decision | count |
| --- | ---: |
| `accepted_with_cautions` | 7 |
| `blocked_missing_primary_material` | 3 |
| `needs_targeted_rework` | 1 |

## Per Dispatch

| dispatch | paper | final decision | pub-grade | rework targets | cautions | bad-class files | validation problems |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `dispatch-001-PILOT20-002-worker-5` | `doi__10.1002_cmdc.201900465` | `accepted_with_cautions` | `True` | 0 | 5 | 0 | 0 |
| `dispatch-002-PILOT20-003-worker-5` | `doi__10.1038_s41598-018-29444-0` | `accepted_with_cautions` | `True` | 0 | 4 | 0 | 0 |
| `dispatch-003-PILOT20-010-worker-5` | `doi__10.1021_acsomega.0c01462` | `accepted_with_cautions` | `True` | 0 | 5 | 0 | 0 |
| `dispatch-004-PILOT20-011-worker-5` | `doi__10.1155_2015_197608` | `accepted_with_cautions` | `True` | 0 | 4 | 0 | 0 |
| `dispatch-005-PILOT20-012-worker-5` | `doi__10.2174_1381612822666161027120518` | `needs_targeted_rework` | `False` | 2 | 5 | 4 | 0 |
| `dispatch-006-PILOT20-014-worker-5` | `doi__10.1016_j.isci.2020.101785` | `accepted_with_cautions` | `True` | 0 | 6 | 0 | 0 |
| `dispatch-007-PILOT20-016-worker-5` | `doi__10.1038_srep24000` | `accepted_with_cautions` | `True` | 0 | 9 | 0 | 0 |
| `dispatch-008-PILOT20-017-worker-5` | `doi__10.1038_s41467-023-42434-9` | `accepted_with_cautions` | `True` | 0 | 3 | 0 | 0 |
| `dispatch-009-PILOT20-018-worker-5` | `doi__10.1038_s41522-024-00637-y` | `blocked_missing_primary_material` | `False` | 2 | 3 | 4 | 0 |
| `dispatch-010-PILOT20-019-worker-2` | `doi__10.1038_s41598-017-16784-6` | `blocked_missing_primary_material` | `False` | 1 | 2 | 1 | 0 |
| `dispatch-011-PILOT20-020-worker-2` | `doi__10.21203_rs.3.rs-578319_v1` | `blocked_missing_primary_material` | `False` | 1 | 5 | 4 | 0 |

## Interpretation

- The 7 accepted papers are accepted with cautions, not clean; preserved cautions remain part of the result.
- The 3 blocked papers stay `blocked_missing_primary_material` and must not be counted as accepted until missing primary/supplementary materials are recovered.
- The 1 `needs_targeted_rework` paper remains nonterminal because owner repair was not actually applied and mechanism class vocabulary is still invalid.
- Ontology QC now reports bad classes by final decision; accepted files have zero non-standard mechanism evidence classes.
