Re-reviewed `doi__10.1038_s41598-017-01267-5` and left it non-accepted.

Repaired worker-2/4/6 artifacts:
- Added 8 source-located non-MIC mode-of-action treatment rows to activity evidence.
- Downgraded `DRAMP18062` to `database_only_no_primary_source`.
- Rewrote final mechanism/adjudication to source-located cell-wall assay claims.
- Added `unrecoverable_material_gaps` and a targeted open ticket: `rwk-codex-rereview-20260503-0002`.
- Appended a rework response for `rwk-complete-test-0001`.

Gate results:
- Semantic gate rerun: failed only on expected non-accepted review state: `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication gate rerun: failed on `open_rework_targets=1`.
- The prior `missing_activity_records` gate failure is resolved.

Reports:
- `reports/doi__10.1038_s41598-017-01267-5.codex_rereview_20260503.semantic_gate.json`
- `reports/doi__10.1038_s41598-017-01267-5.codex_rereview_20260503.publication_quality.json`

The paper remains `blocked_missing_primary_material` because local XML/PDF/supplement/database material does not support primary AMP MIC/toxicity rows or a source-verified DRAMP18062 sequence/activity record.

