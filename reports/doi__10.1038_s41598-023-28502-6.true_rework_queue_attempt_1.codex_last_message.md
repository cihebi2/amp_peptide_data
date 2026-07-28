Re-reviewed and repaired `doi__10.1038_s41598-023-28502-6`.

Status is now `accepted_with_cautions`, not `accepted_clean`. The material layer remains separate as `material_extracted_with_gaps`; the owner-layer rework is closed because the missing activity/database/review evidence was recoverable from local XML/PDF/database artifacts.

Updated the worker-2/4/6 surfaces:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-023-28502-6/final/activity_toxicity_evidence.json): 13 source-located activity rows
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-023-28502-6/final/database_record_verification.json): 10 linked rows, all `source_verified`
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-023-28502-6/final/mechanism_ontology_record.json): 3 bounded membrane-assay claims
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-023-28502-6/final/review_report.json): `publication_grade=true`, `review_status=accepted_with_cautions`
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-023-28502-6/work/review/quality_feedback.json): `issue_count=0`, no open targets
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-023-28502-6/rework/rework_responses.jsonl): `rwk-complete-test-0001` closed after gate validation

Validation evidence:
- Semantic gate: [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-023-28502-6.semantic_gate.json) has `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-023-28502-6.publication_quality.json) has `publication_grade_pass=true`, `risk_counts={}`
- Message bus validation passed; workflow context is `final_approval`, gates true, open rework tickets empty
- Updated latest report: [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-023-28502-6.complete_message_test_report.json)

No `unrecoverable_material_gaps` were recorded because the owner-layer missing values were recoverable locally. The supplementary `landing-*.bin` files were checked and preserved as a nonblocking caution because they are HTML article captures, not structured supplementary tables.

