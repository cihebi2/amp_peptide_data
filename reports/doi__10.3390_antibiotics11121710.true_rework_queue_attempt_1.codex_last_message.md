Re-reviewed exactly `doi__10.3390_antibiotics11121710` and did not rerun the initial bootstrap/workflow.

Updated owner-layer artifacts for worker-2/4/6:
- Worker-2: rebuilt activity/toxicity evidence with `280` records, including `264` MIC rows recovered from Supplementary Table S1 and source-text toxicity rows.
- Worker-4: rebuilt database audit with `490` row audits: `432 source_verified`, `58 source_conflict`.
- Worker-6: updated adjudication/review to `accepted_with_cautions`, cleared `rework_targets`, set `quality_feedback.issue_count = 0`, and appended a resolved response for `rwk-complete-test-0001`.

Validation passed:
- `reports/doi__10.3390_antibiotics11121710.semantic_gate.json`: `issue_count: 0`, pass.
- `reports/doi__10.3390_antibiotics11121710.publication_quality.json`: `publication_grade_pass: true`, `risk_counts: {}`.

Remaining nonblocking caution: full per-peptide HC50 values from Figure 2A are image-only, so I did not fabricate retabulated exact values; linked HC50 database rows without text/table support remain preserved as `source_conflict`.

