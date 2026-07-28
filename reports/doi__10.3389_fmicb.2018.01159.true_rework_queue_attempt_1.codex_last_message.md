Completed the re-review for `doi__10.3389_fmicb.2018.01159`.

I repaired the worker-4/worker-6 artifacts and closed `rwk-complete-test-0001` via `rework_responses.jsonl`. Key outcomes:

- Database audit now has `142` linked-row audits: `77 source_verified`, `65 source_conflict`.
- Final activity evidence rebuilt from primary Table 1 with `88` source-located MIC rows.
- Final mechanism record now has `4` source-located, non-overclaimed mechanism/counterevidence claims.
- `quality_feedback.json` now has `issue_count: 0`, no `qc_failure_reasons`, no `rework_targets`.
- Workflow/report state now has `open_rework_tickets: []` and `publication_grade_ready: true`.

Validation passed:

- Semantic gate: `publication_grade_pass_count=1`, `fail_count=0`, `issue_count=0`
- Publication quality gate: `publication_grade_pass=true`, `risk_counts={}`
- JSON/JSONL parse validation passed for the updated artifacts and message-bus files.

Primary updated paths include:

- `papers/doi__10.3389_fmicb.2018.01159/final/review_report.json`
- `papers/doi__10.3389_fmicb.2018.01159/final/database_record_verification.json`
- `papers/doi__10.3389_fmicb.2018.01159/final/activity_toxicity_evidence.json`
- `papers/doi__10.3389_fmicb.2018.01159/final/mechanism_ontology_record.json`
- `papers/doi__10.3389_fmicb.2018.01159/work/review/quality_feedback.json`
- `paper_packets/doi__10.3389_fmicb.2018.01159/rework/rework_responses.jsonl`
- `reports/doi__10.3389_fmicb.2018.01159.semantic_gate.json`
- `reports/doi__10.3389_fmicb.2018.01159.publication_quality.json`
- `reports/doi__10.3389_fmicb.2018.01159.complete_message_test_report.json`

