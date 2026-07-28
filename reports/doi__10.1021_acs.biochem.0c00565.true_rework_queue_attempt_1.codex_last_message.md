**Result**
Re-reviewed `doi__10.1021_acs.biochem.0c00565` and repaired only worker-2/4/6 layers. I did not rerun the initial workflow/bootstrap.

Key updates:
- Rebuilt activity evidence to 149 source-backed records in [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1021_acs.biochem.0c00565/final/activity_toxicity_evidence.json).
- Rebuilt database audit to 328 rows: `source_verified=274`, `source_conflict=54`, preserving nonblocking cautions in [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1021_acs.biochem.0c00565/final/database_record_verification.json).
- Replaced generic mechanism notes with source-located mechanism claims in [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1021_acs.biochem.0c00565/final/mechanism_ontology_record.json).
- Updated worker-6 final adjudication to `accepted_with_cautions`, `publication_grade=true`, `rework_targets=[]` in [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1021_acs.biochem.0c00565/final/review_report.json).
- Closed `rwk-complete-test-0001` in [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1021_acs.biochem.0c00565/rework/rework_responses.jsonl); no unrecoverable material gaps remain.

Validation:
- Semantic gate: `pass=1/1`, `issue_count=0` in [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1021_acs.biochem.0c00565.semantic_gate.json).
- Publication QA: `publication_grade_pass=true`, `risk_counts={}` in [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1021_acs.biochem.0c00565.publication_quality.json).
- Message bus validation passed; workflow context has `open_rework_tickets=[]` and all gate flags true.

