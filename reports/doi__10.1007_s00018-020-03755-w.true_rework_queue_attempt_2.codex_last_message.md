Re-review complete for `doi__10.1007_s00018-020-03755-w`.

I repaired the worker-owned artifacts and kept the paper non-accepted:

- Rebuilt Table 3 activity evidence to `56` source-reviewed records with corrected peptide/antibiotic entities in [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/final/activity_toxicity_evidence.json).
- Replaced pending-review mechanism placeholders with `3` source-located mechanism claims in [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/final/mechanism_ontology_record.json).
- Updated final adjudication/QC to `blocked_missing_primary_material`, with worker-2 and worker-5 tickets closed and one worker-3 supplementary blocker open in [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00018-020-03755-w/work/review/quality_feedback.json).
- Appended a rework response and updated durable worker-3 unrecoverable ticket in `paper_packets/.../rework/*.jsonl`.

Validation:

- Semantic gate rerun: fails only expected review-layer blockers, `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication gate rerun: fails only `open_rework_targets=1`.
- Activity sanity check: `56` records, `bad_entity_count=0`, `missing_unit_count=0`, `missing_locator_count=0`.
- Mechanism sanity check: `pending_review_count=0`, `direct_without_assay=0`.

Gate reports:
- [semantic gate](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-020-03755-w.single_paper_re_review_20260501T014913Z.semantic_gate.json)
- [publication quality](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00018-020-03755-w.single_paper_re_review_20260501T014913Z.publication_quality.json)

Git status could not be checked because this directory is not a git repository.

