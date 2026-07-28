Re-reviewed `doi__10.1038_srep46541` and repaired only worker-2/4/6 surfaces.

Updated the paper to `accepted_with_cautions`, `publication_grade=true`, with no open rework targets:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_srep46541/final/activity_toxicity_evidence.json): 12 source-supported activity/toxicity rows.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_srep46541/final/database_record_verification.json): 18 audits, `source_verified=7`, `source_conflict=11`.
- [mechanism_ontology_record.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_srep46541/final/mechanism_ontology_record.json): 3 source-located mechanism claims.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_srep46541/final/review_report.json): final worker-6 adjudication.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_srep46541/work/review/quality_feedback.json): `issue_count=0`.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_srep46541/rework/rework_responses.jsonl): closed `rwk-complete-test-0001`.

Important preserved cautions: exact DBAASP LC50 values are database/figure-derived rather than text-table-labeled, DRAMP’s `Synthetic` source conflicts with the paper’s Brevibacillus origin, and the local XML/supplement packet has no tables. No `unrecoverable_material_gaps` were needed.

Validation passed:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`.
- JSON parse check passed for updated artifacts.
- Repair script [repair_doi_10_1038_srep46541_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1038_srep46541_worker246.py:1) compiles.

The cwd is not a git repository, so I validated with artifact checks and the two gates rather than git diff.

