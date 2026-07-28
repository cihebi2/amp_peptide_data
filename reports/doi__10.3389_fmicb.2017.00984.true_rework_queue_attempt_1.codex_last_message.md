Re-reviewed `doi__10.3389_fmicb.2017.00984` and repaired the worker-2/4/6 layers.

Changed artifacts include the packet/final activity evidence, database audit, mechanism/adjudication reports, `quality_feedback.json`, `rework_responses.jsonl`, packet status, workflow context, and gate reports. The paper is now `accepted_with_cautions`, with APD6/CAMP database conflicts preserved as cautions rather than hidden.

Validation evidence:
- `semantic_three_layer_gate.py`: pass, `issue_count: 0`
- `check_three_layer_publication_quality.py`: pass, `risk_counts: {}`
- Complete report: `publication_grade_ready: true`, `open_rework_ticket_count: 0`
- Activity rows: `20`
- Database statuses: `source_verified: 2`, `source_conflict: 2`
- Rework ticket `rwk-complete-test-0001`: closed/resolved

I also added the repair runner at `scripts/repair_doi_10_3389_fmicb_2017_00984_worker246.py` and verified it compiles.

