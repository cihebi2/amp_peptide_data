Re-reviewed `doi__10.1128_spectrum.01664-21` and repaired the owned worker-2/4/6 layers.

Changed:
- Rebuilt activity rows in `paper_packets/.../analysis/activity_toxicity_evidence.json` and `papers/.../final/activity_toxicity_evidence.json`: `544` source-located records, `0` extraction issues.
- Rebuilt database audit/final verification: `426` linked rows, with `165 source_verified`, `229 source_conflict`, `32 database_only_no_primary_source`.
- Rewrote worker-6 adjudication/review/quality artifacts; `rwk-complete-test-0001` is closed, `quality_feedback.issue_count=0`, no open rework targets.
- Added helper: `scripts/repair_doi_10_1128_spectrum_01664_21_worker246.py`.

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`.
- JSON sanity checks passed for repaired packet/final/work artifacts.
- Script compile check passed.

Final paper state is `accepted_with_cautions` with source conflicts preserved, not flattened.

