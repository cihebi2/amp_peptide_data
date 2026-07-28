Re-review completed for `doi__10.5713_ajas.18.0571`. I did not mark it accepted.

Changed/updated:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.5713_ajas.18.0571/final/activity_toxicity_evidence.json): 17 source-supported activity/microscopy rows recovered from XML/PDF/Figures 4-6.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.5713_ajas.18.0571/final/database_record_verification.json): APD6 row preserved as `source_conflict`; literature trace is `source_verified`.
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.5713_ajas.18.0571/final/mechanism_ontology_record.json): replaced generic automated mechanism notes with paper-specific membrane/envelope damage adjudication.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.5713_ajas.18.0571/final/review_report.json): `review_status=blocked_missing_primary_material`, `publication_grade=false`.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.5713_ajas.18.0571/work/review/quality_feedback.json): records the remaining blocker.
- [rework_requests.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.5713_ajas.18.0571/rework/rework_requests.jsonl) and [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.5713_ajas.18.0571/rework/rework_responses.jsonl): original broad ticket answered; one targeted worker-2 ticket remains open.

Gate evidence:
- Semantic gate rerun: failed as intended with 2 review issues: `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication QA rerun: failed as intended with `activity_records=17` and `open_rework_targets=1`.
- Reports written to `reports/doi__10.5713_ajas.18.0571.semantic_gate.json` and `reports/doi__10.5713_ajas.18.0571.publication_quality.json`.

Remaining blocker: exact Figure 4/Figure 5 point-level cell-survival values and SEMs are not locally tabulated in XML/PDF/OA package/supplement/database materials. I recorded this as `unrecoverable_material_gaps` and left the paper non-accepted.

