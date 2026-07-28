Re-review completed for `doi__10.1038_s41598-021-81394-2`.

I did not mark the paper accepted. The final review is now `blocked_missing_primary_material` with `publication_grade: false`, because the local packet contains only supplementary landing-page HTML; the actual MOESM1 DOCX supplement needed for exact Supplementary Table 2 clinical-isolate values is absent locally.

Updated key artifacts:
- [database_record_audit.json](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-021-81394-2/analysis/database_record_audit.json): 88 linked rows adjudicated.
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-021-81394-2/final/activity_toxicity_evidence.json): 42 source-supported Table 1 rows with corrected units.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-021-81394-2/final/review_report.json): non-accepted final adjudication.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-021-81394-2/work/review/quality_feedback.json): concrete QC failures, targeted ticket, and `unrecoverable_material_gaps`.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-021-81394-2/rework/rework_responses.jsonl): appended worker-6 response.

Gate evidence:
- Semantic gate rerun: fails only on review-layer non-acceptance: `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication gate rerun: `publication_grade_pass: false`, `open_rework_targets: 1`, with 42 activity records and 3 mechanism claims counted.

The open ticket is now targeted to the missing local MOESM1 DOCX supplement rather than a vague worker-6 redo.

