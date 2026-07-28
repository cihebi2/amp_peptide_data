Re-reviewed `doi__10.1128_msphere.00390-17` and repaired the owned worker-2/4/6 layers.

Updated the final and packet artifacts. Key results:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_msphere.00390-17/final/activity_toxicity_evidence.json): 46 source-backed activity records from XML/PDF tables, figure captions, and OA package assets.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_msphere.00390-17/final/database_record_verification.json): 21 database audits, preserving 18 `source_conflict` rows and 3 citation-only `source_verified` rows.
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_msphere.00390-17/final/mechanism_ontology_record.json): 4 bounded mechanism claims, no overclaimed direct target.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_msphere.00390-17/work/review/quality_feedback.json): `issue_count: 0`, no rework targets.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1128_msphere.00390-17/rework/rework_responses.jsonl): ticket `rwk-complete-test-0001` closed with gate evidence.

Final status is `accepted_with_cautions`, `publication_grade: true`. No `unrecoverable_material_gaps` were needed.

Verification:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`.
- Miaobi bridge validation: `ok=true`.

