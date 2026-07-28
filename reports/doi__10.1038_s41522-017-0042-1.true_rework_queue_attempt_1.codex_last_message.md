Re-reviewed `doi__10.1038_s41522-017-0042-1` and repaired the worker-4/worker-6 layers.

Final status is `accepted_with_cautions` / `publication_grade=true`. The material layer remains separate as `material_extracted_with_gaps`; analysis is now `analysis_adjudicated_with_cautions`.

Key updates:
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41522-017-0042-1/final/database_record_verification.json): rebuilt 442 database audits: `227 source_verified`, `139 sequence_modified_not_normalized`, `76 source_conflict`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41522-017-0042-1/final/review_report.json): replaced framework-test status with worker-6 source-reviewed adjudication.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41522-017-0042-1/work/review/quality_feedback.json): `issue_count=0`, `rework_targets=[]`.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41522-017-0042-1/rework/rework_responses.jsonl): resolved `rwk-complete-test-0001`.

Preserved one nonblocking `unrecoverable_material_gaps` entry for figure-only exact toxicity values not tabulated locally; those database values remain explicit source conflicts, not fabricated.

Validation passed:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- Message bus validate: `ok=true`
- JSON/JSONL syntax check: `50` files checked, `0` syntax errors

