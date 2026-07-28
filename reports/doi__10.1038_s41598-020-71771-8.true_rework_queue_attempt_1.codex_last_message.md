Done. Repaired `doi__10.1038_s41598-020-71771-8` for worker-2/4/6 and left it accepted only after the open ticket was closed and both strict gates passed.

Key outputs:
- Worker-2: rebuilt 365 source-located MIC/IC50 activity/toxicity records in [final/activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-71771-8/final/activity_toxicity_evidence.json).
- Worker-4: reconciled 453 linked DBAASP/database rows, all `source_verified`, in [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-71771-8/final/database_record_verification.json).
- Worker-6: rewrote [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-71771-8/final/review_report.json), [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-71771-8/work/review/quality_feedback.json), packet analysis/final mirrors, and status files.
- Rework response: [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-020-71771-8/rework/rework_responses.jsonl) now has one closed response for `rwk-complete-test-0001`.

Validation:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`.
- Final review: `accepted_with_cautions`, `publication_grade=true`, `rework_targets=[]`, `qc_failure_reasons=[]`.
- Packet manifest: `analysis_accepted_with_cautions`, `open_rework_ticket_ids=[]`, `known_missing_or_blocked_materials=[]`.

I also added the reproducible repair script at [scripts/repair_doi_10_1038_s41598_020_71771_8_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1038_s41598_020_71771_8_worker246.py).

