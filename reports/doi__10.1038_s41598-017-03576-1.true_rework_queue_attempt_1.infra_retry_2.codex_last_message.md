Re-review completed for `doi__10.1038_s41598-017-03576-1`.

Final state is `accepted_with_cautions`, not clean acceptance. I closed `rwk-complete-test-0001` in [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-017-03576-1/rework/rework_responses.jsonl), cleared open ticket IDs in packet/status/final review surfaces, and updated [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-03576-1/work/review/quality_feedback.json) to `issue_count: 0`.

Repairs made:
- Rebuilt source-reviewed activity/toxicity rows: `69 -> 186`.
- Preserved database audit split: `302 source_verified`, `22 source_conflict`.
- Kept exact DBAASP hemolysis percentages as nonblocking `source_conflict`, not fabricated/source-verified.
- Replaced automated mechanism locator notes with `4` bounded source-reviewed mechanism claims.
- Updated packet/final/work review artifacts and latest reports.

Validation:
- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-03576-1.semantic_gate.json): `issue_count=0`, pass `1/1`.
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1038_s41598-017-03576-1.publication_quality.json): `publication_grade_pass=true`, `risk_counts={}`.
- Packet check has `hard_finding_count=0`; its `open_rework_ticket_count=1` is the historical request-line counter, while actual open IDs are cleared and the closure is recorded in `rework_responses.jsonl`.

