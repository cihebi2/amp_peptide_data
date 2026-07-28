# Final Resolution Summary For 56 Unresolved Records

Generated: 2026-06-20
Scope: 56 `unresolved_record` rows in `reports/nar_resource_freeze_v1/unresolved_records_triage_latest.csv`.

## Decision

All 56 rows were processed through paper-level review reports and independent worker checks. No row was promoted to `source_verified` or `source_conflict` because current local primary/source-packet evidence does not support a safer row-level mapping.

The correct conservative release decision is to keep these rows as `unresolved_record`, keep their papers outside the public v1 candidate subset where already marked `blocked_missing_primary_material`, and route the blockers to source-staging / material recovery before any future status change.

## Per-paper outcomes

| paper_id | unresolved rows | action taken | final status change | blocker |
| --- | ---: | --- | --- | --- |
| `doi__10.1038_s41522-024-00637-y` | 30 | Independent worker report + local synthesis | none | missing Supplementary Table 1 / partner ambiguity / sequence evidence gap |
| `doi__10.1038_s41598-017-16784-6` | 24 | Independent worker report + local synthesis | none | missing MOESM1 PDF Tables S1-S2 for checkerboard FICI rows |
| `doi__10.21203_rs.3.rs-578319_v1` | 2 | Independent worker report + local synthesis | none | missing true supplementary PDF / unusable XML / row-level mapping gap |

## Detailed reports

- `reports/nar_resource_freeze_v1/unresolved_work/doi__10.1038_s41522-024-00637-y.md`
- `reports/nar_resource_freeze_v1/unresolved_work/doi__10.1038_s41598-017-16784-6.md`
- `reports/nar_resource_freeze_v1/unresolved_work/doi__10.21203_rs.3.rs-578319_v1.md`
- `reports/nar_resource_freeze_v1/unresolved_work/summary_latest.md`
- `reports/nar_resource_freeze_v1/unresolved_work/summary_latest.json`

## Reproducible validation

Run these commands from `/root/work/抗菌肽/数据库/batch/4-team`:

```bash
python scripts/triage_unresolved_records.py
python scripts/write_unresolved_resolution_reports.py
python scripts/build_nar_resource_freeze_v1.py
python scripts/validate_unresolved_processing.py
```

The three `<paper_id>.md` files listed above are hand-reviewed worker/source-review artifacts and are intentionally not overwritten by `scripts/write_unresolved_resolution_reports.py`. The script-generated per-paper summaries use `generated_<paper_id>.md/json`.

## Release wording

Use this wording in manuscripts/release notes:

> The 56 unresolved DBAASP audit rows were manually rechecked against available local primary/source packets. They concentrate in three papers and reflect missing supplementary tables/PDFs or row-level synergy/FICI mapping ambiguity. They were retained as unresolved rather than promoted to source-verified evidence.

## Next material actions

1. Source-stage the real supplementary PDF/table for `doi__10.1038_s41522-024-00637-y` Supplementary Table 1.
2. Source-stage `41598_2017_16784_MOESM1_ESM.pdf` for `doi__10.1038_s41598-017-16784-6`.
3. Source-stage `SIEngerbergFK13Cys2021.7.pdf` or equivalent primary table for `doi__10.21203_rs.3.rs-578319_v1`.
4. After source staging, rerun supplementary extraction and worker-4/worker-6 row-level database audit before changing statuses.
