# NAR Resource Freeze v1 Candidate

Generated at: `2026-07-03T11:20:43+00:00`
Release id: `amp-evidence-audit-v1-freeze-candidate`
Status: `freeze_candidate`

This directory is a conservative release-planning snapshot. It is not a
submission-ready public NAR database package until the public website/API,
bulk downloads, manual stratified validation, database source licenses, and
the 1471-vs-1472 scope reconciliation is disclosed in the manuscript.

## Scope

| Metric | Count |
| --- | ---: |
| `paper_final_artifact_count` | 1471 |
| `public_v1_candidate_papers` | 1374 |
| `excluded_or_non_publication_grade_papers` | 97 |
| `database_audit_rows` | 139259 |
| `source_verified_rows` | 95941 |
| `non_source_verified_rows` | 43318 |
| `activity_records` | 115184 |
| `mechanism_claims` | 4774 |

## Core Outputs

| File | Rows | Purpose |
| --- | ---: | --- |
| `reports/nar_resource_freeze_v1/release_manifest_latest.json` | 1 | Release inputs, checksums, output paths, and inclusion rule. |
| `reports/nar_resource_freeze_v1/unified_scope_summary_latest.json` | 1 | Unified paper/record/activity/mechanism scope summary. |
| `reports/nar_resource_freeze_v1/paper_scope_latest.csv` | 1471 | One row per paper final artifact with inclusion and artifact counts. |
| `reports/nar_resource_freeze_v1/excluded_or_non_publication_grade_papers_latest.csv` | 97 | Papers excluded from the public v1 candidate subset. |
| `reports/nar_resource_freeze_v1/database_denominators_latest.csv` | 6 | Audit-row denominators by database; not raw source-database universe sizes. |
| `reports/nar_resource_freeze_v1/crosstab_status_by_database_latest.csv` | 23 | Database audit status cross-tab by database. |
| `reports/nar_resource_freeze_v1/crosstab_category_by_database_latest.csv` | 40 | Multilabel difference-category cross-tab by database. |
| `reports/nar_resource_freeze_v1/crosstab_status_by_source_table_latest.csv` | 253 | Audit status cross-tab by source table. |
| `reports/nar_resource_freeze_v1/crosstab_review_status_by_database_latest.csv` | 20 | Paper review-status cross-tab over audit rows by database. |
| `reports/nar_resource_freeze_v1/scope_reconciliation_1471_vs_1472_latest.md` | 1 | Explains why legacy queue count is 1472 while final-artifact universe is 1471. |
| `reports/nar_resource_freeze_v1/unresolved_records_triage_latest.md` | 56 | Triage of unresolved audit rows by paper, database, blocker class, and next queue. |
| `reports/nar_resource_freeze_v1/needs_targeted_rework_triage_latest.md` | 29 | Triage of needs-targeted-rework papers into owner-worker queue versus material/digitization backlog. |

## Interpretation Guardrails

- `public_v1_candidate_papers` requires `publication_grade=true` and accepted-like `review_status` in `papers/*/final/review_report.json`.
- `accepted_with_cautions` is not clean; cautions and conflicts remain visible.
- Non-`source_verified` rows are evidence discordance/provenance gaps, not automatically database errors.
- Difference categories are multilabel and must not be summed as unique record counts.
- Denominators are audit-row denominators from existing final artifacts, not the full raw universe of APD6/DBAASP/DRAMP/CAMP/dbAMP.
- The `1471` vs `1472` gap is one queue-only initial failure without final artifacts; see the scope reconciliation files.
- The 56 `unresolved_record` rows are triaged separately; they should not be promoted to `source_verified` without primary-source evidence.

## Rebuild

```bash
python scripts/build_nar_resource_freeze_v1.py
```

Validate with:

```bash
python -m json.tool reports/nar_resource_freeze_v1/release_manifest_latest.json >/dev/null
python -m json.tool reports/nar_resource_freeze_v1/unified_scope_summary_latest.json >/dev/null
```

## Unresolved Record Processing

Rebuild and validate the unresolved-record closure package with:

```bash
python scripts/triage_unresolved_records.py
python scripts/write_unresolved_resolution_reports.py
python scripts/build_nar_resource_freeze_v1.py
python scripts/validate_unresolved_processing.py
```

The three `<paper_id>.md` files under `reports/nar_resource_freeze_v1/unresolved_work/` are hand-reviewed worker/source-review artifacts. The `generated_<paper_id>.*` files are script-generated summaries and may be safely regenerated.

## Needs-Targeted-Rework Processing

Rebuild and validate the current 29-paper needs-targeted-rework closure package with:

```bash
python scripts/triage_needs_targeted_rework.py
python scripts/write_needs_targeted_rework_resolution_reports.py
python scripts/build_nar_resource_freeze_v1.py
python scripts/validate_needs_targeted_rework_processing.py
```

This package does not promote papers to accepted/publication-grade. It separates the current-packet owner-worker rework queue from source-staging/digitization backlog.

The current owner-worker rework queue is split into 5 lanes at `reports/nar_resource_freeze_v1/needs_targeted_rework_work/owner_worker_rework_manifest_latest.json`; each paper has a refreshed `rework_context/<paper_id>/CODEX_REVIEW_PROMPT.md`.
