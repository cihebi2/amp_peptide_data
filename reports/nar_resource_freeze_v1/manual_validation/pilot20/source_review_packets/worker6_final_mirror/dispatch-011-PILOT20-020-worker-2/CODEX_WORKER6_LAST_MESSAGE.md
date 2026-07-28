Completed worker-6 final mirror for `dispatch-011-PILOT20-020-worker-2`.

Wrote the required response JSON here: [worker6_final_response.json](/root/work/抗菌肽/数据库/batch/4-team/reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_final_mirror/dispatch-011-PILOT20-020-worker-2/worker6_final_response.json)

Outcome: `blocked_missing_primary_material`. The owner response only confirmed missing material; it did not perform an analysis-layer repair. I refreshed worker-6 provenance in both final review reports while preserving `publication_grade: false`, open blockers, and unchanged scientific layer artifacts.

Validation:
- Response JSON meets the provided schema’s required fields and `final_decision` enum.
- Updated review reports remain `blocked_missing_primary_material`.
- No `accepted_clean` or `accepted_with_cautions` markers present.
- Strict semantic gate fails as expected for non-publication-grade blocked status.

