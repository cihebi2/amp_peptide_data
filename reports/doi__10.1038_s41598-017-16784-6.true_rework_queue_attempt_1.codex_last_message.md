Re-review completed for `doi__10.1038_s41598-017-16784-6`. I loaded the worker-2/4/6 skills, reopened the handoff packet/source artifacts, and did not rerun the initial queue bootstrap.

Updated artifacts include:
- [final/activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-16784-6/final/activity_toxicity_evidence.json): rebuilt to 161 source-located rows; Table 4 MBIC now has 15 parsed rows and parser issue count is 0.
- [final/database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-16784-6/final/database_record_verification.json): rebuilt with `source_verified=26`, `source_conflict=24`, `unresolved_record=24`.
- [final/review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-16784-6/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-16784-6/work/review/quality_feedback.json): kept non-accepted as `blocked_missing_primary_material`.

The remaining blocker is explicit: `local_moesm1_supplement_pdf_absent`. Local source has XML/PDF and duplicate publisher HTML pages, but not the actual `41598_2017_16784_MOESM1_ESM.pdf`, so supplement-only Tables S1/S2 checkerboard/FICI rows cannot be source-verified locally. I recorded this in `unrecoverable_material_gaps`, appended/kept a targeted ticket `rwk-unrecoverable-local-supplement-0002`, and updated [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-017-16784-6/rework/rework_responses.jsonl).

Gate evidence:
- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-16784-6.semantic_gate.json): fails expected, `issue_count=2`, only review-level non-publication issues.
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-16784-6.publication_quality.json): fails expected, `open_rework_targets=1`.
- 13 updated JSON files parsed successfully.

I also added [repair_doi_10_1038_s41598_017_16784_6_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1038_s41598_017_16784_6_worker246.py) so this repair/gate refresh is reproducible. Git status could not be shown because this directory is not a git repository.

