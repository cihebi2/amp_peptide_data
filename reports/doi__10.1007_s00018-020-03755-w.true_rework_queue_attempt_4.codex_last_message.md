Re-reviewed `doi__10.1007_s00018-020-03755-w` without rerunning bootstrap. The paper remains **not accepted**: `review_status=blocked_missing_primary_material`, `publication_grade=false`, `final_layer_outputs_ready=false`.

Updated:
- `paper_packets/.../rework/rework_responses.jsonl` with `rsp-20260501-worker3-worker4-worker6-20260501T022111Z`
- `papers/.../work/supplementary_methods/supplementary_evidence.json`
- `papers/.../work/review/quality_feedback.json`
- `papers/.../final/review_report.json`
- `paper_packets/.../analysis/adjudication_report.json`
- `paper_packets/.../final/review_report.json`

Evidence:
- Worker-3 blocker remains: local supplement files are HTML landing pages, not DOCX; no DOC/DOCX/XLS/XLSX/archive candidate was found under packet/source/landed paths.
- Worker-4 remains complete: `113 source_verified`, `28 source_conflict`, `0 unresolved_record`.
- Open ticket kept: `rwk-20260501-worker3-supplement-docx-unrecoverable-after-bounded-repair`.

Gate results:
- Semantic gate report: `reports/doi__10.1007_s00018-020-03755-w.codex_re_review_20260501T022111Z.semantic_gate.json`
  - strict fail, `publication_grade_pass_count=0`, `publication_grade_fail_count=1`
  - issue codes: `review_status_not_publication_grade`, `publication_grade_not_true`
- Publication-quality report: `reports/doi__10.1007_s00018-020-03755-w.codex_re_review_20260501T022111Z.publication_quality.json`
  - `publication_grade_pass=false`, `open_rework_targets=1`

Validation: changed JSON files and the JSONL response stream parse cleanly with `jq`.