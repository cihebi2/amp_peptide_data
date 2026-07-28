Re-reviewed `doi__10.1038_s41598-021-89485-w` and repaired only worker-2/4/6 layers.

Key status:
- Final status: `accepted_with_cautions`
- Open rework tickets: `0`
- Closed ticket: `rwk-complete-test-0001`
- Activity rows: `24` peptide rows plus `4` PMB control rows
- Database audit: `27 source_verified`, `35 source_conflict`, `1 database_only_no_primary_source`
- Mechanism claims: `3`
- Nonblocking unrecoverable gaps recorded: landing `.bin` files are HTML-only; no host toxicity/hemolysis assay in local material

Updated main artifacts:
- `paper_packets/doi__10.1038_s41598-021-89485-w/analysis/*`
- `papers/doi__10.1038_s41598-021-89485-w/final/*`
- `papers/doi__10.1038_s41598-021-89485-w/work/review/quality_feedback.json`
- `paper_packets/doi__10.1038_s41598-021-89485-w/rework/rework_responses.jsonl`
- `reports/doi__10.1038_s41598-021-89485-w.semantic_gate.json`
- `reports/doi__10.1038_s41598-021-89485-w.publication_quality.json`

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `fail_count=0`, `issue_count=0`
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`
- JSON parse checks passed for repaired packet/final review/activity/database artifacts

I also added reproducible helper script:
`scripts/repair_doi_10_1038_s41598_021_89485_w_worker246.py`

