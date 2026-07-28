Completed the re-review for `doi__10.1128_spectrum.02013-21`.

I repaired the worker-4/worker-6 artifacts and kept the paper non-accepted. The database audit now preserves `82 source_verified`, `8 source_conflict`, and `4 database_only_no_primary_source` rows. The remaining blockers are recorded as `unrecoverable_material_gaps`: figure-only toxicity exact values and unsupported database activity scope.

Updated key artifacts:
- [database_record_audit.json](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1128_spectrum.02013-21/analysis/database_record_audit.json)
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_spectrum.02013-21/final/review_report.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_spectrum.02013-21/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1128_spectrum.02013-21/rework/rework_responses.jsonl)

Gate reruns:
- Semantic gate: failed as expected, `0/1` publication-grade pass, `2` review-level issues.
- Publication gate: failed as expected, `publication_grade_pass=false`, `open_rework_targets=1`.

Ticket `rwk-complete-test-0001` remains open and targeted. I also added [repair_doi_10_1128_spectrum_02013_21_worker46.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1128_spectrum_02013_21_worker46.py) to make the repair reproducible. This directory is not a git repository, so there was no git diff/status to report.

