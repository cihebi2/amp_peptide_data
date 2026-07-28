Re-reviewed `doi__10.3390_molecules20022775` and repaired the owned worker-2/4/6 layers.

Updated artifacts include the packet/final activity, database, mechanism, adjudication/review, `quality_feedback.json`, `packet_manifest.json`, `analysis_status.json`, and `rework_responses.jsonl`. The repair recovered 20 source-located ED50 activity rows, reconciled 10 DBAASP rows, and preserved 2 `source_conflict` rows rather than smoothing them.

Gate results:
- Semantic gate: `issue_count=0`, `publication_grade_fail_count=0`
- Publication-quality gate: `publication_grade_pass=true`, `risk_counts={}`
- Final status: `accepted_with_cautions`
- Open rework targets/tickets: none
- `unrecoverable_material_gaps`: none

Remaining cautions are preserved in the artifacts: the Temporin L amastigote database decimal conflict, a Table 2 vs conclusion inconsistency for Temporin 1Sa, no direct molecular mechanism assay, and no host-toxicity table in local material.

