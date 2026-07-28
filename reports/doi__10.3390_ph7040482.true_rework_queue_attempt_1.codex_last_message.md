Re-reviewed and repaired `doi__10.3390_ph7040482` for worker-4/worker-6 only.

Key results:
- Rebuilt worker-4 database audit: `80` linked DBAASP rows, all `source_verified`.
- Rebuilt worker-6 final activity/toxicity: `36` source-located records (`32` MIC + `4` hemolysis).
- Replaced placeholder mechanism notes with `5` bounded source-reviewed mechanism claims.
- Closed `rwk-complete-test-0001` in `rework_responses.jsonl`.
- `quality_feedback.json` now has `issue_count: 0`, no `qc_failure_reasons`, no open `rework_targets`.
- Paper status is `accepted_with_cautions`; no unrecoverable material gap was needed.

Verification:
- Semantic gate: `publication_grade_pass_count=1`, `fail_count=0`, `issue_count=0`.
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`.
- Packet status: `analysis_accepted`, `open_rework_ticket_ids=[]`.
- Also ran `python -m py_compile scripts/repair_doi_10_3390_ph7040482_worker46.py`.
- `git status` could not run because this directory is not a git repo.

Main touched paths include `papers/doi__10.3390_ph7040482/final/*`, `papers/doi__10.3390_ph7040482/work/review/quality_feedback.json`, `paper_packets/doi__10.3390_ph7040482/analysis/*`, `paper_packets/doi__10.3390_ph7040482/rework/rework_responses.jsonl`, and the gate reports under `reports/`.

