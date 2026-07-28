Re-reviewed `doi__10.1038_hdy.2016.117` and repaired the owned worker-2/4/6 layers.

Current status: `accepted_with_cautions`, `publication_grade=true`, `open_rework_ticket_count=0`.

Key updates:
- Rebuilt activity/toxicity evidence with `204` source-backed rows from XML Tables 2/3 plus Figure 9.
- Rebuilt database adjudication with `304` rows: `298 source_verified`, `6 source_conflict` preserved for CAMP/dbAMP aggregate identifier cautions.
- Updated final review, quality feedback, packet analysis/final copies, and complete report.
- Closed `rwk-complete-test-0001` in both `rework_requests.jsonl` and `rework_responses.jsonl`.

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication-quality gate: `publication_grade_pass=true`, `risk_counts={}`

Main reports:
- `reports/doi__10.1038_hdy.2016.117.semantic_gate.json`
- `reports/doi__10.1038_hdy.2016.117.publication_quality.json`
- `reports/doi__10.1038_hdy.2016.117.complete_message_test_report.json`

Note: this directory is not a git repository, so no git diff/status summary is available.

