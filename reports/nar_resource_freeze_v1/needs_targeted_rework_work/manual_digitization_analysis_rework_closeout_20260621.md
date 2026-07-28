# Manual Digitization / Analysis Rework Closeout 2026-06-21

## Scope

This closeout covers the 10 papers that were previously grouped under `manual_digitization_or_keep_backlog` / figure-exact-value triage.

The workflow did not promote any figure-only exact value by script. It created task packets, split true analysis rework from controlled digitization, launched true owner-worker rework only where existing packet sources supported analysis repair, then re-ran strict gates and accepted sample audit.

## Initial 10-Paper Split

Before owner-worker rework:

- `analysis_rework_from_existing_material`: 1
  - `doi__10.1038_s42003-022-03899-4`
- `mixed_analysis_rework_plus_controlled_digitization_gap`: 2
  - `doi__10.1021_acsomega.8b01876`
  - `doi__10.3390_antibiotics11081080`
- `controlled_digitization_possible_but_requires_human_calibration`: 4
  - `doi__10.1002_cbic.202100609`
  - `doi__10.1016_j.virol.2010.11.014`
  - `doi__10.1128_mbio.01935-20`
  - `doi__10.1186_s12866-016-0799-z`
- `not_digitizable_missing_source_data`: 3
  - `doi__10.1038_s41467-024-51933-2`
  - `doi__10.1128_spectrum.02013-21`
  - `doi__10.3390_pharmaceutics14040693`

## True Owner-Worker Run

Command label:

- `manual_digitization_analysis_rework_20260621`

Run summary:

- `reports/true_rework_queue_manual_digitization_analysis_rework_20260621_latest.json`
- terminal statuses:
  - `accepted_after_rework`: 2
  - `blocked_after_best_effort`: 1

Per-paper outcome:

| paper_id | outcome | review_status | publication_grade | note |
| --- | --- | --- | --- | --- |
| `doi__10.1021_acsomega.8b01876` | accepted after rework | `accepted_with_cautions` | true | Worker-2 activity-axis and worker-5 mechanism placeholder defects repaired; conflicts preserved as cautions. |
| `doi__10.3390_antibiotics11081080` | accepted after rework | `accepted_with_cautions` | true | Activity table orientation and mechanism context repaired; unsupported exact curve values were not promoted. |
| `doi__10.1038_s42003-022-03899-4` | blocked after best effort | `needs_targeted_rework` | false | Actual supplementary/source-data assets needed for unresolved database-only rows are not locally present; 2 open rework targets remain. |

Accepted sample audit:

- `reports/nar_resource_freeze_v1/needs_targeted_rework_work/accepted_sample_audit_manual_digitization_analysis_rework_20260621/accepted_sample_audit_latest.json`
- `paper_count=2`, `passed_count=2`, `failed_count=0`

## Post-Run Backlog

After rebuilding release and re-running triage/audits:

- `public_v1_candidate_papers`: 1371
- `excluded_or_non_publication_grade_papers`: 100
- `needs_targeted_rework_count`: 29
- material/digitization backlog audit:
  - `analysis_rework_candidate_not_auto_queued`: 1
  - `manual_digitization_candidate`: 4
  - `source_staging_candidate`: 1
  - `still_unrecoverable_backlog`: 23

Remaining manual/digitization cohort in `manual_digitization_processing_latest` has 8 papers because the 2 accepted papers left the backlog.

## Quality Notes

- No exact figure-only values were inserted by automation.
- Controlled digitization candidates are task packets only until calibrated extraction and independent QA exist.
- Missing source-data/sequence cases remain non-publication-grade.
- `doi__10.1038_s42003-022-03899-4` remains a real blocker, not an infrastructure failure.
