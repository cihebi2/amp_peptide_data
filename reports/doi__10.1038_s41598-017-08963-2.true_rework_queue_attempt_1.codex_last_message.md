Re-review completed for `doi__10.1038_s41598-017-08963-2`. I did not rerun the initial workflow/bootstrap.

I repaired the worker-2/4/6 layers and closed `rwk-complete-test-0001` via [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-017-08963-2/rework/rework_responses.jsonl). Final status is `accepted_with_cautions`, not `accepted_clean`: DRAMP sequence/modification and database-only toxicity annotations are preserved as cautions rather than promoted as primary-source rows.

Key results:
- Worker-2: 4 source-supported MCF-7 `IC50` rows written to packet/final activity artifacts.
- Worker-4: database audit now has `sequence_modified_not_normalized=2`, `source_verified=1`.
- Worker-6: [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-08963-2/final/review_report.json) has `publication_grade=true`, `review_status=accepted_with_cautions`, and `rework_targets=[]`.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-08963-2/work/review/quality_feedback.json) now has `issue_count=0`.

Verification:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`.
- Repair script py-compiled successfully: [repair_doi_10_1038_s41598_017_08963_2_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_1038_s41598_017_08963_2_worker246.py).

Updated reports are [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-08963-2.semantic_gate.json), [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-08963-2.publication_quality.json), and [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-08963-2.complete_message_test_report.json).

