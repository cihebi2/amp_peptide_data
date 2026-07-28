Re-review complete for `doi__10.3389_fmicb.2020.01146`.

I repaired the worker-2/4/6 layers and closed `rwk-complete-test-0001` after verification. Current state is `accepted_with_cautions`, `publication_grade=true`, `open_rework_tickets=[]`.

Key outputs:
- Activity rebuilt: `126` source-located records in `papers/doi__10.3389_fmicb.2020.01146/final/activity_toxicity_evidence.json`
- Database audit repaired: `18 source_verified`, `2 source_conflict` preserved in `final/database_record_verification.json`
- Worker-6 review updated: `rework_targets=[]`, `qc_failure_reasons=[]`
- `quality_feedback.json`: `issue_count=0`
- Rework response appended in `paper_packets/doi__10.3389_fmicb.2020.01146/rework/rework_responses.jsonl`
- Workflow context now has `semantic_gate_ready=true`, `publication_grade_ready=true`

Verification:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- Message bridge validation: `ok=true`
- `open_ticket_ids(...)` returns `[]`

I also added the reusable repair script at `scripts/repair_doi_10_3389_fmicb_2020_01146_worker246.py`.

