Re-reviewed `doi__10.3389_fpls.2021.753217` and repaired the worker-2/4/6 layers.

Key outputs:
- Wrote 167 source-located activity rows in `activity_toxicity_evidence.json` from XML Tables 2/4/5/6/7.
- Rebuilt database audit: 261 rows, `237 source_verified`, `24 source_conflict` preserving the Dickeya/Erwinia taxonomy mismatch.
- Replaced framework-test adjudication with source-reviewed `accepted_with_cautions`, not `accepted_clean`.
- Closed `rwk-complete-test-0001` in `rework_responses.jsonl`.
- Cleared `quality_feedback.json`: `issue_count: 0`, no rework targets, no unrecoverable gaps.

Validation:
- `semantic_three_layer_gate.py`: pass `1/1`, `issue_count: 0`
- `check_three_layer_publication_quality.py`: `publication_grade_pass: true`, `risk_counts: {}`

Remaining cautions are preserved, not blockers: Dickeya/Erwinia database taxonomy conflict, SP10-5 comparator has no local sequence row, and no paper-local toxicity assay rows were fabricated.

