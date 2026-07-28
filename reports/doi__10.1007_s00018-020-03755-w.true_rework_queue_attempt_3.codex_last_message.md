Re-reviewed `doi__10.1007_s00018-020-03755-w` without rerunning the initial bootstrap and did not mark it accepted.

Updated:
- [supplementary_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/work/supplementary_methods/supplementary_evidence.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/work/review/quality_feedback.json)
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/final/review_report.json)
- packet review/adjudication copies and [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1007_s00018-020-03755-w/rework/rework_responses.jsonl)

Result: still `blocked_missing_primary_material`, `publication_grade: false`. The open ticket remains `rwk-20260501-worker3-supplement-docx-unrecoverable-after-bounded-repair`. Local recheck found no DOC/DOCX/XLS/XLSX/archive supplement under packet/source/landed roots; the `.bin` supplementary assets are Springer HTML pages pointing to a DOCX that is not locally present.

Fresh gates:
- [semantic gate](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-020-03755-w.codex_re_review_20260501T020707Z.semantic_gate.json): fail as expected, `0/1` publication-grade pass, issues `review_status_not_publication_grade`, `publication_grade_not_true`.
- [publication gate](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-020-03755-w.codex_re_review_20260501T020707Z.publication_quality.json): `publication_grade_pass=false`, `open_rework_targets=1`.

Validation: updated JSON files parse cleanly, `rework_responses.jsonl` parses line-by-line, and both final gate report JSON files parse cleanly. `git diff --stat` was unavailable because this checkout is not a git repository.

