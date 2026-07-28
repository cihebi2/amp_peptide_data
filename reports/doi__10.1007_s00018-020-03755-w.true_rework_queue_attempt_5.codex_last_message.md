Done. I re-reviewed only `doi__10.1007_s00018-020-03755-w` and left it non-accepted.

The final state is controlled blocked, not publication-grade:
- Open ticket: `rwk-20260501-worker3-supplement-docx-unrecoverable-after-bounded-repair`
- `review_status`: `blocked_missing_primary_material`
- `publication_grade`: `false`
- Worker-4 remains complete: `113 source_verified`, `28 source_conflict` retained as cautions/conflicts
- Worker-3 remains blocked: local supplementary files are HTML landing pages; no local DOCX/XLSX/archive/image supplement was recoverable

Updated key artifacts:
- [supplementary_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/work/supplementary_methods/supplementary_evidence.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/work/review/quality_feedback.json)
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/final/review_report.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1007_s00018-020-03755-w/rework/rework_responses.jsonl)
- [workflow_context.json](/root/work/抗菌肽/数据库/batch/4-team/.miaobi-paper-review/workflows/doi__10.1007_s00018-020-03755-w/workflow_context.json)

Gate reruns:
- Semantic: [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-020-03755-w.codex_re_review_20260501T023912Z.semantic_gate.json), failed as expected with `review_status_not_publication_grade` and `publication_grade_not_true`
- Publication QA: [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-020-03755-w.codex_re_review_20260501T023912Z.publication_quality.json), `publication_grade_pass=false`, `open_rework_targets=1`

Validation passed: modified JSON/JSONL parsed cleanly, and `miaobi_message_bridge.py validate` returned `ok=true`. `git status` could not run because this directory is not a git repository.

