# AMP Evidence Atlas v1 RC1 Release Package

Release id: `amp-evidence-atlas-v1-rc1`
Generated at: `2026-06-22T01:50:05+00:00`
Status: `release_package_candidate_not_public_nar_submission_ready`

This directory is a versioned derived-data package for review and resource
planning. It is not yet a hosted public NAR Database Resource. Public
submission still requires a website/API, manual stratified validation,
database source-version/license review, and manuscript disclosure.

## Scope

| Metric | Count |
| --- | ---: |
| `paper_final_artifact_count` | 1471 |
| `public_v1_candidate_papers` | 1371 |
| `excluded_or_non_publication_grade_papers` | 100 |
| `database_audit_rows` | 139259 |
| `source_verified_rows` | 95941 |
| `non_source_verified_rows` | 43318 |
| `activity_records` | 115184 |
| `mechanism_claims` | 4772 |

## Downloads

| File | Rows | Description |
| --- | ---: | --- |
| `papers.tsv` | 1471 | Paper-level review and inclusion metadata. |
| `database_record_audits.tsv` | 139259 | Database record audit rows with evidence status and sanitized locators. |
| `activity_observations.tsv` | 115184 | Activity/toxicity observations extracted from source-reviewed final artifacts. |
| `mechanism_claims.tsv` | 4772 | Mechanism evidence claims and direct-assay classifications. |
| `conflicts_and_cautions.tsv` | 49438 | Database discordance/provenance gaps plus paper-level cautions and blockers. |
| `excluded_blocked_papers.tsv` | 100 | Excluded or non-publication-grade papers and reasons. |
| `database_denominators.tsv` | 6 | Freeze support denominator/crosstab table. |
| `crosstab_status_by_database.tsv` | 23 | Freeze support denominator/crosstab table. |
| `crosstab_category_by_database.tsv` | 40 | Freeze support denominator/crosstab table. |
| `crosstab_status_by_source_table.tsv` | 253 | Freeze support denominator/crosstab table. |
| `crosstab_review_status_by_database.tsv` | 20 | Freeze support denominator/crosstab table. |

## Guardrails

- `accepted_with_cautions` is not clean; cautions and conflicts remain visible.
- Non-`source_verified` rows are evidence discordance/provenance gaps, not automatically database errors.
- Difference categories are multilabel and must not be summed as unique record counts.
- Denominators are audit-row denominators from existing final artifacts, not raw source-database universe sizes.
- This package does not redistribute PDFs, XML full text, figures, images, or supplementary files.

## Rebuild

```bash
python scripts/build_nar_resource_freeze_v1.py
python scripts/build_nar_public_release_package.py
```

Validate with:

```bash
python -m json.tool releases/amp_evidence_atlas_v1_rc1/release_manifest.json >/dev/null
(cd releases/amp_evidence_atlas_v1_rc1 && sha256sum -c checksums.txt)
```
