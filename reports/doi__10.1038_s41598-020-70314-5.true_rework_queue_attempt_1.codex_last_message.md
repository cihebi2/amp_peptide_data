Re-review completed for `doi__10.1038_s41598-020-70314-5`.

Updated owner-layer artifacts for worker-2/4/6:
- [activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-70314-5/final/activity_toxicity_evidence.json): 36 source-supported rows.
- [database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-70314-5/final/database_record_verification.json): 2 APD6 records preserved as `source_conflict` with primary-source sequence verification.
- [review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-70314-5/final/review_report.json): `accepted_with_cautions`, `publication_grade: true`, no open rework targets.
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-020-70314-5/work/review/quality_feedback.json): `issue_count: 0`.

Rework response was recorded in [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-020-70314-5/rework/rework_responses.jsonl), and live workflow state now has `open_rework_tickets: []`.

Verification:
- Semantic gate: passed `1/1`, `issue_count=0`.
- Publication-quality gate: `publication_grade_pass=true`, `risk_counts={}`.
- Message-bus validation: `ok=true`.
- Packet structural gate: `hard_finding_count=0`; material layer remains separately `material_extracted_with_gaps`, with one historical request line but no live open ticket.

Remaining cautions are nonblocking and preserved: APD6 human-RBC/candidacidal free-text conflicts vs primary source, and Figure 4 exact antifungal bar percentages not available in extracted text.

