Re-reviewed and repaired `doi__10.3389_fchem.2017.00051` without rerunning the initial workflow/bootstrap.

Updated the worker-2/4/6 artifacts, including:
- Rebuilt activity evidence to 26 records: corrected all 16 Table 2 MIC rows, added 8 Table 3 hemolysis rows, plus source-supported survival/MBC records.
- Reworked APD6 adjudication: AP03153 exact sequence is preserved as `database_only_no_primary_source`; literature/activity claims are source-reviewed.
- Rewrote worker-6 final review as `accepted_with_cautions`, with no open rework targets.
- Closed `rwk-complete-test-0001` in `rework_responses.jsonl`, `workflow_context.json`, `packet_manifest.json`, and the complete report.
- Added the repair script: [repair_doi_10_3389_fchem_2017_00051_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_3389_fchem_2017_00051_worker246.py).

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication-quality gate: `publication_grade_pass=true`, `risk_counts={}`.
- `quality_feedback.json`: `issue_count=0`, no remaining open tickets.
- `py_compile` passed for the repair script.

The repo status check could not run because `/root/work/抗菌肽/数据库/batch/4-team` is not a git repository.

