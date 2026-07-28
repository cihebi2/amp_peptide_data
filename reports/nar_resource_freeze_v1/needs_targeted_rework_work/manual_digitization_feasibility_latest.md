# Manual Digitization Processing Report

Generated at: `2026-06-21T16:34:56Z`

Completion claim: `manual_digitization_feasibility_audit_only_no_publication_grade_change`

## Counts

- `controlled_digitization_possible_but_requires_human_calibration`: 4
- `not_digitizable_missing_source_data`: 3
- `analysis_rework_from_existing_material`: 1
- `analysis_rework_candidate_count`: 1
- `controlled_digitization_candidate_count`: 4
- `missing_source_blocker_count`: 3

## Per Paper

| paper_id | classification | queue | images | tables | tasks | action |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `doi__10.1002_cbic.202100609` | `controlled_digitization_possible_but_requires_human_calibration` | `manual_digitization_controlled_task` | 23 | 0 | 2 | Image evidence exists, but exact values require calibrated digitization and independent QA before any owner-worker can promote them. |
| `doi__10.1016_j.virol.2010.11.014` | `controlled_digitization_possible_but_requires_human_calibration` | `manual_digitization_controlled_task` | 15 | 0 | 1 | Image evidence exists, but exact values require calibrated digitization and independent QA before any owner-worker can promote them. |
| `doi__10.1038_s41467-024-51933-2` | `not_digitizable_missing_source_data` | `still_unrecoverable_backlog` | 1 | 0 | 1 | Do not launch owner-worker from the current packet; acquire missing source data/sequence/exact table material first, otherwise keep conflict/unresolved. |
| `doi__10.1038_s42003-022-03899-4` | `analysis_rework_from_existing_material` | `analysis_rework_candidate_not_auto_queued` | 1 | 5 | 4 | Existing packet tables/locators or analysis tickets support targeted owner-worker repair; this is not a blind figure-digitization task. |
| `doi__10.1128_mbio.01935-20` | `controlled_digitization_possible_but_requires_human_calibration` | `manual_digitization_controlled_task` | 20 | 0 | 2 | Image evidence exists, but exact values require calibrated digitization and independent QA before any owner-worker can promote them. |
| `doi__10.1128_spectrum.02013-21` | `not_digitizable_missing_source_data` | `still_unrecoverable_backlog` | 33 | 0 | 1 | Do not launch owner-worker from the current packet; acquire missing source data/sequence/exact table material first, otherwise keep conflict/unresolved. |
| `doi__10.1186_s12866-016-0799-z` | `controlled_digitization_possible_but_requires_human_calibration` | `manual_digitization_controlled_task` | 23 | 0 | 2 | Image evidence exists, but exact values require calibrated digitization and independent QA before any owner-worker can promote them. |
| `doi__10.3390_pharmaceutics14040693` | `not_digitizable_missing_source_data` | `still_unrecoverable_backlog` | 11 | 0 | 1 | Do not launch owner-worker from the current packet; acquire missing source data/sequence/exact table material first, otherwise keep conflict/unresolved. |

## Quality Boundary

- These artifacts are task packets only; they do not promote exact figure values.
- A digitized value can be used only after calibrated extraction, independent QA, owner-worker source review, worker-6 adjudication, semantic gate, and publication-quality gate.
- Missing source/sequence/source-data cases remain non-publication-grade until new primary material is acquired.
