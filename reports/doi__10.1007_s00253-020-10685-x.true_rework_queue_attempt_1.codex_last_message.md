Re-reviewed `doi__10.1007_s00253-020-10685-x` and kept it non-accepted.

Updated the owner-layer artifacts under:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00253-020-10685-x/final/activity_toxicity_evidence.json): now 34 source-located activity/toxicity records; previous missing activity blocker is repaired.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00253-020-10685-x/final/database_record_verification.json): 9 database rows preserved as `source_conflict`, 1 literature link `source_verified`.
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00253-020-10685-x/final/mechanism_ontology_record.json): replaced placeholder mechanism notes with 4 bounded source-located claims.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00253-020-10685-x/final/review_report.json) and [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1007_s00253-020-10685-x/work/review/quality_feedback.json): status is `blocked_missing_primary_material_after_re_review`.

I appended an updated rework request and response in [rework_requests.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1007_s00253-020-10685-x/rework/rework_requests.jsonl) / [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1007_s00253-020-10685-x/rework/rework_responses.jsonl). Remaining blocker is `primary_sequence_not_embedded_for_database_identity`: the local primary paper and packet database do not contain an exact sequence/modification record for the linked DBAASP/CAMP peptide identity.

Gates rerun:
- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00253-020-10685-x.semantic_gate.json): fails intentionally with 2 review-layer issues only; `missing_activity_records` is gone.
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1007_s00253-020-10685-x.publication_quality.json): `publication_grade_pass=false`, `activity_records=34`, `mechanism_claims=4`, `open_rework_targets=1`.

JSON validation passed for 19 JSON files; rework JSONL parses with 2 request lines and 3 response lines.

