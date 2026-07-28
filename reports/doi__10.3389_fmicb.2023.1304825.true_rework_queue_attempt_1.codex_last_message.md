Re-reviewed `doi__10.3389_fmicb.2023.1304825` without rerunning the initial bootstrap.

Updated worker-2/4/6 artifacts and closed `rwk-complete-test-0001` via `rework_responses.jsonl`. Final state is `accepted_with_cautions`, not clean acceptance:
- material packet: still `material_extracted_with_gaps`
- analysis: `source_reviewed_publication_grade_ready`
- semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- publication QA: `publication_grade_pass=true`, `risk_counts={}`
- quality feedback: `issue_count=0`, no `qc_failure_reasons`, no `rework_targets`, no `unrecoverable_material_gaps`

Key repaired outputs:
- `papers/doi__10.3389_fmicb.2023.1304825/final/activity_toxicity_evidence.json`: 50 records, including 26 Table 3 rows, 22 Table 7 stability MIC rows, and 2 Figure 5 safety rows.
- `papers/doi__10.3389_fmicb.2023.1304825/final/database_record_verification.json`: 79 linked database rows adjudicated, with 56 `source_conflict` rows preserved.
- `papers/doi__10.3389_fmicb.2023.1304825/final/review_report.json`: `publication_grade=true`, `review_status=accepted_with_cautions`, no open rework targets.
- Added repair helper: `scripts/repair_doi_10_3389_fmicb_2023_1304825_worker246.py`.

Verification rerun:
- `semantic_three_layer_gate.py --paper-id doi__10.3389_fmicb.2023.1304825 --json`: passed, 0 issues.
- `check_three_layer_publication_quality.py --manifest reports/doi__10.3389_fmicb.2023.1304825.complete_message_test_manifest.json`: passed, no risks.
- JSON parse checks passed for the modified packet/final/work/report artifacts.

