Re-reviewed and repaired `doi__10.1126_sciadv.aav4580` for worker-2/4/6.

Changed/updated:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1126_sciadv.aav4580/final/activity_toxicity_evidence.json): 22 source-backed rows, including 16 `IC50` rows and 6 `CC50` cytotoxicity rows.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1126_sciadv.aav4580/final/database_record_verification.json): 204 adjudicated rows, `source_verified=173`, `source_conflict=31`.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1126_sciadv.aav4580/final/review_report.json): `accepted_with_cautions`, `publication_grade=true`, no open `rework_targets`.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1126_sciadv.aav4580/work/review/quality_feedback.json): `issue_count=0`, ticket `rwk-complete-test-0001` closed.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1126_sciadv.aav4580/rework/rework_responses.jsonl): one closed response with checked sources and gate evidence.
- Added repair helper: [repair_doi_10_1126_sciadv_aav4580_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1126_sciadv_aav4580_worker246.py).

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`.
- JSON sanity check: 12 key artifacts parsed successfully.
- No unrecoverable material gaps were needed; remaining database/source conflicts are preserved as cautions.

