Re-reviewed `doi__10.3389_fmicb.2020.563030` for worker-4/worker-6 only.

Updated:
- `paper_packets/doi__10.3389_fmicb.2020.563030/rework/rework_responses.jsonl`
- `papers/doi__10.3389_fmicb.2020.563030/final/review_report.json`
- `papers/doi__10.3389_fmicb.2020.563030/work/review/quality_feedback.json`
- `reports/doi__10.3389_fmicb.2020.563030.semantic_gate.json`
- `reports/doi__10.3389_fmicb.2020.563030.publication_quality.json`

Result:
- Rework ticket `rwk-complete-test-0001` now has a durable response.
- Worker-4 database audit remains source-reviewed: 376 rows, 171 `source_verified`, 201 `sequence_modified_not_normalized`, 4 preserved `source_conflict`.
- Worker-6 final status is `accepted_with_cautions`, with no open `rework_targets`, no `qc_failure_reasons`, and no `unrecoverable_material_gaps`.

Validation:
- Semantic gate: `publication_grade_pass_count: 1/1`, `issue_count: 0`.
- Publication QA: `publication_grade_pass: true`, `risk_counts: {}`.
- JSON validation passed for the edited JSON/JSONL files.

Note: `git status` could not run because this directory is not a git repository.

