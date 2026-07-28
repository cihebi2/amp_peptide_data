# Five Paper True Re-review Summary (2026-04-29)

Execution contract: true re-review used new Codex CLI processes with the paper-local `CODEX_REVIEW_PROMPT.md` contract embedded or passed directly; worker-owned repairs were made before worker-6 gate decisions.

- Combined semantic gate exit code: 1 (expected nonzero when any paper still has open rework).
- Combined publication-quality exit code: 2 (expected nonzero when any paper still has open rework).
- Manifest: `reports/five_paper_true_rereview_manifest_20260429.json`
- Combined semantic report: `reports/five_paper_true_rereview.semantic_gate.json`
- Combined publication report: `reports/five_paper_true_rereview.publication_quality.json`

| Paper | Outcome | Semantic | Publication QA | Miaobi | QC / rework reason |
| --- | --- | --- | --- | --- | --- |
| `doi__10.1002_cmdc.201900465` | needs_targeted_rework / publication_grade=false / rework_targets=1 | fail issue_count=2 | fail {'open_rework_targets': 1} | pass | table1_image_matrix_not_fully_transcribed, database_conflicts_preserved_after_partial_reconciliation, worker6_final_approval_blocked_by_open_ticket |
| `doi__10.1002_advs.202205301` | accepted_with_cautions / publication_grade=true / rework_targets=0 | pass | pass | pass | none |
| `doi__10.1002_advs.202401793` | needs_targeted_rework / publication_grade=false / rework_targets=4 | fail issue_count=2 | fail {'open_rework_targets': 1} | pass | activity_table_entity_mapping_incomplete, database_non_mic_rows_require_source_review, mechanism_ontology_pending_review, worker6_final_adjudication_not_accepting_open_rework |
| `doi__10.1002_cbic.202100609` | needs_targeted_rework / publication_grade=false / rework_targets=4 | fail issue_count=2 | fail {'open_rework_targets': 1} | pass | supplementary_table_s5_not_structured, figure4_cytotoxicity_not_quantified, database_conflicts_preserved_pending_source_review, final_adjudication_blocked_by_open_analysis_rework |
| `doi__10.1002_cbic.202100151` | accepted_with_cautions / publication_grade=true / rework_targets=0 | pass | pass | pass | none |
