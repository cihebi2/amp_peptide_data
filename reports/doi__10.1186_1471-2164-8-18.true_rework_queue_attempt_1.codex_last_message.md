Re-review completed for `doi__10.1186_1471-2164-8-18`.

I did not mark it accepted. The repaired state is `blocked_missing_primary_material` / `refused_needs_rework`.

Key updates:
- Repaired worker-2 activity layer with `activity_records: 0` and explicit `unrecoverable_material_gaps`.
- Repaired worker-4 database layer: `source_conflict: 16`, `database_only_no_primary_source: 4`, no `source_verified` overclaim.
- Repaired worker-6 final adjudication/review, quality feedback, and mechanism final to remove framework-test language and preserve non-acceptance.
- Appended durable rework response(s) and added targeted ticket `rwk-complete-test-0001-unrecoverable`.

Gate evidence:
- Semantic gate: failed as intended with 3 issues: `review_status_not_publication_grade`, `publication_grade_not_true`, `missing_activity_records`.
- Publication gate: failed as intended with `open_rework_targets: 1`.
- Final report now records `structural_ready=true`, `validator_contract_ready=true`, `semantic_gate_ready=false`, `publication_grade_ready=false`.

Primary updated paths include:
- `papers/doi__10.1186_1471-2164-8-18/final/*`
- `papers/doi__10.1186_1471-2164-8-18/work/review/quality_feedback.json`
- `paper_packets/doi__10.1186_1471-2164-8-18/analysis/*`
- `paper_packets/doi__10.1186_1471-2164-8-18/rework/rework_responses.jsonl`
- `reports/doi__10.1186_1471-2164-8-18.semantic_gate.json`
- `reports/doi__10.1186_1471-2164-8-18.publication_quality.json`
- `reports/doi__10.1186_1471-2164-8-18.complete_message_test_report.json`

Note: this directory is not a git repository, so there was no git diff/status to report.

