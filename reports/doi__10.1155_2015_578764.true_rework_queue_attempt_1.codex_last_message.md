Re-reviewed and repaired `doi__10.1155_2015_578764`.

Changed owner-layer outputs under packet/final/work, including:
- [repair script](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1155_2015_578764_worker46.py)
- [final activity](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1155_2015_578764/final/activity_toxicity_evidence.json)
- [final database](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1155_2015_578764/final/database_record_verification.json)
- [final mechanism](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1155_2015_578764/final/mechanism_ontology_record.json)
- [final review](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1155_2015_578764/final/review_report.json)
- [quality feedback](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1155_2015_578764/work/review/quality_feedback.json)
- [rework responses](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1155_2015_578764/rework/rework_responses.jsonl)

Key repair: corrected the Table 5 peptide-column shift, rebuilt 43 source-located activity/toxicity records, re-adjudicated 100 database rows, preserved 31 `source_conflict` rows as cautions, and replaced framework-test mechanism placeholders with 3 source-classified mechanism claims.

Final state: `accepted_with_cautions`, not `accepted_clean`. Open rework tickets are now `[]`; `rwk-complete-test-0001` is resolved. No `unrecoverable_material_gaps` were needed because local XML/PDF/OA/database material was sufficient.

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- Message bridge validate: `ok=true`

