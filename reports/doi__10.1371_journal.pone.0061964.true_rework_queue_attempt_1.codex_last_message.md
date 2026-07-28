Done for `doi__10.1371_journal.pone.0061964`.

Outcome: `accepted_with_cautions`, `publication_grade=true`, `rwk-complete-test-0001` closed, no open rework targets, no `qc_failure_reasons`, no `unrecoverable_material_gaps`. The material layer remains separate as `material_extracted_with_gaps`; analysis is now `analysis_accepted`.

Key repaired artifacts:
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0061964/final/database_record_verification.json): 30 DBAASP-linked rows source-reviewed; prior wrong Table 2 peptide/strain mappings corrected.
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0061964/final/activity_toxicity_evidence.json): 159 source-reviewed records from Tables 2-4; toxicity explicitly not locally reported.
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0061964/final/mechanism_ontology_record.json): 4 bounded claims; no direct mechanism overclaim.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0061964/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0061964/work/review/quality_feedback.json): final QC clean.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0061964/rework/rework_responses.jsonl): appended the closure response.

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `publication_grade_fail_count=0`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`.
- Updated reports: [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0061964.semantic_gate.json), [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0061964.publication_quality.json), [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0061964.complete_message_test_report.json).

I also added [repair_doi_10_1371_journal_pone_0061964_worker46.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1371_journal_pone_0061964_worker46.py) as the reproducible repair script.

