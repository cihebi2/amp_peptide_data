Re-review completed for `doi__10.1038_s42003-022-04164-4`.

I did not mark it accepted. The paper is now `blocked_missing_primary_material` with `publication_grade=false` because local supplementary assets are only Nature HTML landing pages, while the actual Supplementary Information PDFs/Figshare raw-data zip are absent.

Updated key artifacts:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s42003-022-04164-4/final/activity_toxicity_evidence.json): rebuilt 291 source-located Table 1-3 MIC/hemolysis rows.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s42003-022-04164-4/final/database_record_verification.json): 477 database audits, `143 source_verified`, `302 database_only_no_primary_source`, `32 source_conflict`.
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s42003-022-04164-4/final/mechanism_ontology_record.json): 4 bounded source-located mechanism/phenotype claims.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s42003-022-04164-4/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s42003-022-04164-4/work/review/quality_feedback.json): record the blocking `unrecoverable_material_gaps`.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s42003-022-04164-4/rework/rework_responses.jsonl): appended the worker-2/4/6 response.
- [rework_requests.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s42003-022-04164-4/rework/rework_requests.jsonl): added `rwk-unrecoverable-material-0002`.

Validation:
- Semantic gate rerun: [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s42003-022-04164-4.semantic_gate.json) fails only because review status is non-publication-grade and `publication_grade=false`.
- Publication QA rerun: [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s42003-022-04164-4.publication_quality.json) fails with `open_rework_targets=1`.
- JSON sanity pass succeeded; activity row target/unit check found `0` bad target/unit rows.

