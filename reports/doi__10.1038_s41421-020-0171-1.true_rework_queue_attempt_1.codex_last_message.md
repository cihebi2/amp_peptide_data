Re-review completed for `doi__10.1038_s41421-020-0171-1`.

Status is now `accepted_with_cautions`, `publication_grade=true`, with material/analysis layers still separated: material remains `material_extracted_with_gaps`, while analysis is `analysis_adjudicated_with_cautions`. I did not make it clean acceptance; cautions preserve unsupported DRAMP antimicrobial/MIC/hemolysis labels, modified stapled-sequence notation, and graph-only effect-size limits.

Updated the owned worker-2/4/6 surfaces, including:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41421-020-0171-1/final/activity_toxicity_evidence.json): 7 source-located activity records
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41421-020-0171-1/final/database_record_verification.json): 12 DRAMP rows, `6 source_conflict`, `6 source_verified`
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41421-020-0171-1/final/mechanism_ontology_record.json): 3 corrected beta-catenin/Wnt mechanism claims
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41421-020-0171-1/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41421-020-0171-1/work/review/quality_feedback.json): no QC failures or rework targets
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41421-020-0171-1/rework/rework_responses.jsonl): closed `rwk-complete-test-0001` with checked paths/tools and remaining cautions

Verification:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- Message bus validate: `ok=true`
- Open tickets: `[]`
- JSON/JSONL syntax: 44 files checked, 0 errors

Git status could not run because this directory is not a git repository.

