Re-reviewed `doi__10.1038_srep13595` and repaired the owned worker-2/4/6 layers.

Final state: `accepted_with_cautions`, `publication_grade=true`, ticket `rwk-complete-test-0001` closed. The material layer remains separate as `material_extracted_with_gaps`; no `unrecoverable_material_gaps` were needed.

Key outputs updated:
- `papers/doi__10.1038_srep13595/final/activity_toxicity_evidence.json`: 40 source-backed rows
- `papers/doi__10.1038_srep13595/final/database_record_verification.json`: 6 audits, preserving 4 `source_conflict` DRAMP rows
- `papers/doi__10.1038_srep13595/final/review_report.json`: source-reviewed worker-6 adjudication
- `papers/doi__10.1038_srep13595/work/review/quality_feedback.json`: `issue_count=0`
- `paper_packets/doi__10.1038_srep13595/rework/rework_responses.jsonl`: closeout response added
- Gate reports refreshed under `reports/doi__10.1038_srep13595.*`

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- JSON parse checks passed for touched packet/final/work artifacts

One caution preserved: DRAMP half-life/matrix context conflicts are explicit, and figure-only exact IC50 values not printed in local text were not fabricated.

