Re-reviewed `doi__10.1186_s40409-017-0119-6` and closed `rwk-complete-test-0001`.

Key result: final status is now `accepted_with_cautions`, with layers still separated:
- material: `material_extracted_with_gaps`
- analysis: `analysis_accepted_with_cautions`
- semantic gate: pass, `issue_count=0`
- publication QA: pass, `risk_counts={}`

Repairs made:
- Worker-2: rebuilt Table 1 into 20 source-supported activity/toxicity rows.
- Worker-4: reconciled database rows as `source_verified=29`, `source_conflict=11`; preserved DRAMP/dbAMP later-paper conflicts.
- Worker-6: rewrote final adjudication, cleared QC failures, closed the rework ticket, and kept bounded mechanism cautions.

Updated main artifacts include:
- `paper_packets/.../analysis/*`
- `papers/.../final/*`
- `papers/.../work/review/quality_feedback.json`
- `paper_packets/.../rework/rework_responses.jsonl`
- `reports/doi__10.1186_s40409-017-0119-6.semantic_gate.json`
- `reports/doi__10.1186_s40409-017-0119-6.publication_quality.json`
- workflow context/report files

Validation evidence:
`semantic_three_layer_gate.py` -> `publication_grade_pass_count=1`, `issue_count=0`.
`check_three_layer_publication_quality.py` -> `publication_grade_pass=true`, `risk_counts={}`.

