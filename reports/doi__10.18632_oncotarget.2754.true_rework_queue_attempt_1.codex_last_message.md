Re-reviewed `doi__10.18632_oncotarget.2754` and repaired the owned worker-2/4/6 layers.

Changed the paper-local outputs under:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.2754/final/activity_toxicity_evidence.json): recovered 8 source-backed HPRP-A1/HPRP-A2 Table 1 IC50/MHC rows.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.2754/final/database_record_verification.json): matched DBAASP rows, preserving `sequence_modified_not_normalized`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.2754/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.18632_oncotarget.2754/work/review/quality_feedback.json): final state is `accepted_with_cautions`, `issue_count: 0`, no open rework targets.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.18632_oncotarget.2754/rework/rework_responses.jsonl): closed `rwk-complete-test-0001`.
- Added [repair_doi_10_18632_oncotarget_2754_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_18632_oncotarget_2754_worker246.py) for reproducible single-paper repair.

Validation passed:
- Semantic gate: `pass_count=1`, `fail_count=0`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`, `activity_records=8`.
- Workflow context now has `open_rework_tickets: []`.

No `unrecoverable_material_gaps` remain. The retained cautions are nonblocking: terminal modification/stereochemistry preservation and not fabricating exact figure-only synergy panel values.

