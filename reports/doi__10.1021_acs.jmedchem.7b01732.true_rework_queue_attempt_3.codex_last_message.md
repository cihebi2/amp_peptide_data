Re-review completed for `doi__10.1021_acs.jmedchem.7b01732`.

Updated the worker-2/4/6 layers:
- Activity evidence now has `46` row-level EC50/CC50 records from Table 1, Table 2, and SI Table S1.
- Database audit now has `140 source_verified`, `40 sequence_modified_not_normalized`, and `15 source_conflict` rows, preserving database cautions instead of hiding them.
- Worker-6 final review is `accepted_with_cautions`, `publication_grade=true`, with `qc_failure_reasons=[]`, `rework_targets=[]`, and `unrecoverable_material_gaps=[]`.
- `rwk-complete-test-0001` is closed in `paper_packets/.../rework/rework_responses.jsonl`.

Validation passed:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`.
- JSON validation passed for repaired packet/final/work/report surfaces.

Key updated reports:
- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1021_acs.jmedchem.7b01732.semantic_gate.json)
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1021_acs.jmedchem.7b01732.publication_quality.json)
- [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1021_acs.jmedchem.7b01732.complete_message_test_report.json)

Material layer remains separate as `material_extracted_with_gaps`; analysis/review is now accepted with cautions.

