Completed the bounded re-review for `doi__10.1186_gb-2004-6-1-r6` and left it non-accepted.

I repaired the worker-2/4/6 layers by preserving 3 MIC rows as `database_only_no_primary_source`, auditing 12 linked database rows as `database_only_no_primary_source`, and changing the final decision to `blocked_missing_primary_material` with 3 `unrecoverable_material_gaps`. The old ticket remains, and I added `rwk-unrecoverable-local-primary-support-0001` with owner, omission code, artifact path, and checked source paths.

Key updated artifacts:
- [final review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_gb-2004-6-1-r6/final/review_report.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_gb-2004-6-1-r6/work/review/quality_feedback.json)
- [final activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_gb-2004-6-1-r6/final/activity_toxicity_evidence.json)
- [final database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1186_gb-2004-6-1-r6/final/database_record_verification.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1186_gb-2004-6-1-r6/rework/rework_responses.jsonl)

Validation:
- JSON parse check passed for updated packet/final/work artifacts.
- Semantic gate rerun: failed as intended with 2 review-layer issues only; `missing_activity_records` is gone.
- Publication-quality gate rerun: failed as intended due `open_rework_targets: 1`.
- Reports: [semantic](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1186_gb-2004-6-1-r6.codex_worker246_rereview_20260503.semantic_gate.json), [publication quality](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1186_gb-2004-6-1-r6.codex_worker246_rereview_20260503.publication_quality.json)

I did not rerun the initial workflow/bootstrap.

