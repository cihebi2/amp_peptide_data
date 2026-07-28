Complete for `doi__10.1038_s41598-017-01474-0`.

The worker-4/worker-6 repair is in place and I refreshed the strict gates. Current state:
- `rwk-complete-test-0001` closed as `closed_accepted_with_cautions`
- `quality_feedback.json`: `issue_count=0`, no `qc_failure_reasons`, no `rework_targets`
- Database audit: `209 source_verified`, `2 source_conflict` preserved
- Activity/toxicity: `118` activity records, `9` toxicity records
- Mechanism: `3` claims
- Open rework tickets: `0`
- Nonblocking material gap recorded: local supplementary assets are landing HTML only, `blocks_publication_grade=false`

Fresh gate evidence:
- `reports/doi__10.1038_s41598-017-01474-0.semantic_gate.json`: `publication_grade_pass_count=1`, `fail_count=0`, `issue_count=0`
- `reports/doi__10.1038_s41598-017-01474-0.publication_quality.json`: `publication_grade_pass=true`, `risk_counts={}`

I did not rerun the initial workflow/bootstrap. No next paper was touched.

