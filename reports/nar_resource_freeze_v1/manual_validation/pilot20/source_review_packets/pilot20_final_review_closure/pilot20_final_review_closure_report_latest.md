# Pilot20 Final Review Closure

Generated at: `2026-06-22T09:05:27Z`

This is the full pilot20 closure state after worker-6 final mirror for dispatch papers and worker-6 final review for non-dispatch papers.

## Counts

| metric | value |
| --- | ---: |
| papers | 20 |
| publication_grade true | 16 |
| accepted files with bad mechanism classes | 0 |
| nonterminal files with bad mechanism classes | 13 |
| review-report validation problems | 0 |

## Final Decisions

| final decision | count |
| --- | ---: |
| `accepted_with_cautions` | 16 |
| `blocked_missing_primary_material` | 3 |
| `needs_targeted_rework` | 1 |

## Per Paper

| paper | decision | source | pub-grade | rework targets | cautions | bad-class files | validation problems |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `doi__10.1002_cmdc.201900465` | `accepted_with_cautions` | `worker6_final_mirror` | `True` | 0 | 5 | 0 | 0 |
| `doi__10.1002_pro.5088` | `accepted_with_cautions` | `worker6_non_dispatch_final_review` | `True` | 0 | 5 | 0 | 0 |
| `doi__10.1007_s12539-016-0163-x` | `accepted_with_cautions` | `worker6_non_dispatch_final_review` | `True` | 0 | 5 | 0 | 0 |
| `doi__10.1016_j.isci.2020.101785` | `accepted_with_cautions` | `worker6_final_mirror` | `True` | 0 | 6 | 0 | 0 |
| `doi__10.1021_acs.jmedchem.1c01033` | `accepted_with_cautions` | `worker6_non_dispatch_final_review` | `True` | 0 | 6 | 0 | 0 |
| `doi__10.1021_acsomega.0c01462` | `accepted_with_cautions` | `worker6_final_mirror` | `True` | 0 | 5 | 0 | 0 |
| `doi__10.1021_acsomega.2c02778` | `accepted_with_cautions` | `worker6_non_dispatch_final_review` | `True` | 0 | 3 | 0 | 0 |
| `doi__10.1038_s41467-017-00419-5` | `accepted_with_cautions` | `worker6_non_dispatch_final_review` | `True` | 0 | 7 | 0 | 0 |
| `doi__10.1038_s41467-023-42434-9` | `accepted_with_cautions` | `worker6_final_mirror` | `True` | 0 | 3 | 0 | 0 |
| `doi__10.1038_s41522-024-00637-y` | `blocked_missing_primary_material` | `worker6_final_mirror` | `False` | 2 | 3 | 4 | 0 |
| `doi__10.1038_s41598-017-03576-1` | `accepted_with_cautions` | `worker6_non_dispatch_final_review` | `True` | 0 | 4 | 0 | 0 |
| `doi__10.1038_s41598-017-16784-6` | `blocked_missing_primary_material` | `worker6_final_mirror` | `False` | 1 | 2 | 1 | 0 |
| `doi__10.1038_s41598-018-29444-0` | `accepted_with_cautions` | `worker6_final_mirror` | `True` | 0 | 4 | 0 | 0 |
| `doi__10.1038_srep24000` | `accepted_with_cautions` | `worker6_final_mirror` | `True` | 0 | 9 | 0 | 0 |
| `doi__10.1155_2015_197608` | `accepted_with_cautions` | `worker6_final_mirror` | `True` | 0 | 4 | 0 | 0 |
| `doi__10.1371_journal.pone.0138911` | `accepted_with_cautions` | `worker6_non_dispatch_final_review` | `True` | 0 | 6 | 0 | 0 |
| `doi__10.21203_rs.3.rs-578319_v1` | `blocked_missing_primary_material` | `worker6_final_mirror` | `False` | 1 | 5 | 4 | 0 |
| `doi__10.2174_1381612822666161027120518` | `needs_targeted_rework` | `worker6_final_mirror` | `False` | 2 | 5 | 4 | 0 |
| `doi__10.3389_fmicb.2021.693725` | `accepted_with_cautions` | `worker6_non_dispatch_final_review` | `True` | 0 | 6 | 0 | 0 |
| `doi__10.3390_molecules23112943` | `accepted_with_cautions` | `worker6_non_dispatch_final_review` | `True` | 0 | 5 | 0 | 0 |

## Interpretation

- `accepted_with_cautions` is not clean acceptance; preserved cautions/conflicts remain part of the curated record.
- Nonterminal papers keep `publication_grade=false` and concrete rework/material blockers.
- The pilot20 accepted subset now has zero non-standard mechanism evidence classes after full-scope ontology QC.
- Scaling to the 420-row validation set should use this full-scope QC, not the earlier dispatch-only QC.
