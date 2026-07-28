Re-review completed for `doi__10.3389_fimmu.2022.821070`.

I repaired the worker-2/4/6 artifacts and closed `rwk-complete-test-0001` in `rework_responses.jsonl`. The final state is `accepted_with_cautions`, not clean acceptance.

Key results:
- Activity/toxicity: 17 source-located records, including 10 recovered MIC rows from Table 3.
- Database audit: 48 linked rows adjudicated, `25 source_verified`, `23 source_conflict`.
- Review/QC: `quality_feedback.json` now has `issue_count: 0`, no open `rework_targets`, and no unrecoverable material gaps.
- Workflow context: `open_rework_tickets: []`, `publication_grade_ready: true`.

Validation rerun:
- `semantic_three_layer_gate.py`: `publication_grade_pass=1/1`
- `check_three_layer_publication_quality.py`: `publication_grade_pass: true`, `risk_counts: {}`

Also added the reusable repair script:
`scripts/repair_doi_10_3389_fimmu_2022_821070_worker246.py`

