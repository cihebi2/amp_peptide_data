Re-reviewed `doi__10.1186_1471-2164-8-326` without rerunning the initial workflow/bootstrap.

Updated the worker-2/4/6 artifacts. The paper is now `accepted_with_cautions`, with `rwk-complete-test-0001` closed and no open rework targets. Key retained cautions: activity rows are whole-hemolymph Figure 1 antibacterial activity, not peptide-specific MICs; Figure 1 values are explicitly approximate visual estimates; DRAMP/dbAMP antimicrobial labels are preserved as source conflicts where the primary paper does not support peptide-specific assay claims.

Validation passed:

- Semantic gate: `issue_count=0`, `publication_grade_pass_count=1`
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`
- Final report: `terminal_status=accepted_with_cautions`, `open_rework_ticket_count=0`

Primary updated outputs include:

- `papers/doi__10.1186_1471-2164-8-326/final/review_report.json`
- `papers/doi__10.1186_1471-2164-8-326/final/activity_toxicity_evidence.json`
- `papers/doi__10.1186_1471-2164-8-326/final/database_record_verification.json`
- `papers/doi__10.1186_1471-2164-8-326/work/review/quality_feedback.json`
- `paper_packets/doi__10.1186_1471-2164-8-326/rework/rework_responses.jsonl`
- `reports/doi__10.1186_1471-2164-8-326.semantic_gate.json`
- `reports/doi__10.1186_1471-2164-8-326.publication_quality.json`
- `reports/doi__10.1186_1471-2164-8-326.complete_message_test_report.json`

