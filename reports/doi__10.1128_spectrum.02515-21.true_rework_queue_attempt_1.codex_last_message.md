Re-reviewed and repaired `doi__10.1128_spectrum.02515-21` without rerunning bootstrap.

Updated the worker-owned artifacts for worker-2/4/6:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_spectrum.02515-21/final/activity_toxicity_evidence.json): 105 source-located activity/toxicity rows; Table 2 salt/serum MIC matrix repaired.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_spectrum.02515-21/final/database_record_verification.json): 165 source-verified assay/literature rows; 7 exact-sequence records preserved as database-only cautions.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_spectrum.02515-21/final/review_report.json): `accepted_with_cautions`, `publication_grade=true`, no open rework targets.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1128_spectrum.02515-21/work/review/quality_feedback.json): `issue_count=0`, `qc_failure_reasons=[]`.
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1128_spectrum.02515-21/rework/rework_responses.jsonl): appended closure for `rwk-complete-test-0001`.

Remaining caution is nonblocking: exact peptide sequence strings were not machine-readable in local XML/PDF/supplement text, so they remain database-only provenance with `blocks_publication_grade=false`.

Verification:
- Semantic gate: `publication_grade_pass_count=1`, `fail_count=0`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`.
- Latest report refreshed at [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1128_spectrum.02515-21.complete_message_test_report.json).

