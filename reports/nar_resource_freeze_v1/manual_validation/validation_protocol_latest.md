# Manual Stratified Validation Protocol: AMP Evidence Atlas v1 RC1

Generated at: `2026-06-22T10:42:22`
Release id: `amp-evidence-atlas-v1-rc1`
Release version: `v1_rc1`

## Purpose

This manifest defines a reproducible 300-500 row validation sample for
estimating quality boundaries before public NAR Database Resource claims.
It validates curation decisions; it does not reopen every source paper.

## Inputs

- Source release table: `releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv`
- Validation manifest: `reports/nar_resource_freeze_v1/manual_validation/validation_manifest_20260622_104222.csv`
- Machine-readable summary: `reports/nar_resource_freeze_v1/manual_validation/validation_summary_20260622_104222.json`

## Sampling Design

- Total sample rows: `420`
- Deterministic seed recorded in every manifest row.
- Stratification axes: database, audit status, and primary validation category.
- `source_verified` rows are sampled as a baseline false-positive/false-negative check.
- Non-source-verified statuses are deliberately oversampled because they define the resource novelty and risk boundary.
- Rare `unresolved_record` rows are high-priority because they test whether material gaps are correctly preserved.

## Sample Counts by Status

| status | sampled rows |
| --- | ---: |
| `database_only_no_primary_source` | 60 |
| `sequence_modified_not_normalized` | 70 |
| `source_conflict` | 120 |
| `source_verified` | 120 |
| `unresolved_record` | 50 |

## Sample Counts by Database

| database | sampled rows |
| --- | ---: |
| `APD6` | 33 |
| `CAMP` | 31 |
| `DBAASP` | 254 |
| `DRAMP` | 73 |
| `dbAMP` | 26 |
| `unknown` | 3 |

## Sample Counts by Primary Validation Category

| category | sampled rows |
| --- | ---: |
| `activity_value_or_unit` | 62 |
| `database_only_no_primary_source` | 74 |
| `mechanism_or_claim_scope` | 47 |
| `other` | 1 |
| `row_granularity` | 21 |
| `sequence_or_modification` | 24 |
| `source_verified_baseline` | 120 |
| `target_or_organism` | 15 |
| `unresolved_or_missing_material` | 56 |

## Reviewer Instructions

For each row, the reviewer should open the release row and final artifact, then check whether the recorded status and extracted database/paper fields are supported by the available source locators.

Fill these columns:

| column | allowed values / meaning |
| --- | --- |
| `reviewer_decision` | `pass`, `minor_error`, `major_error`, `critical_error`, `needs_rework`, `unverifiable` |
| `reviewer_error_class` | `none`, `source_locator_error`, `status_misclassification`, `database_field_mismatch`, `paper_field_mismatch`, `normalization_error`, `missing_material`, `overclaim`, `other` |
| `reviewer_notes` | Short evidence-backed note. Do not paste copyrighted text. |
| `reviewed_by` | Reviewer identifier. |
| `reviewed_at` | ISO timestamp. |

Decision guidance:

- `pass`: status and key fields are supported by the final artifact and locators.
- `minor_error`: typo or presentation issue that does not change status/category.
- `major_error`: field or locator problem that changes interpretation for this row.
- `critical_error`: row should not support a manuscript/resource claim without repair.
- `needs_rework`: send to owner-worker or adjudicator for targeted correction.
- `unverifiable`: local material is insufficient; preserve the gap instead of guessing.

## Guardrails

- Do not infer exact values from plots unless controlled digitization and QA exist.
- Do not convert `database_only_no_primary_source` or `unresolved_record` into source-verified without primary-source evidence.
- Do not treat `accepted_with_cautions` as clean.
- Do not describe all non-source-verified rows as database errors.
- Do not copy full text, PDFs, images, or supplementary tables into the validation output.
