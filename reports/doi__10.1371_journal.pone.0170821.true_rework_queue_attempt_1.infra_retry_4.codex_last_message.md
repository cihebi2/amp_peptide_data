Re-reviewed `doi__10.1371_journal.pone.0170821` without rerunning bootstrap.

I verified the repaired worker-2/4/6 artifacts from local XML/PDF/OA/supplement/database surfaces, then fixed the remaining stale mirror/control state: `paper_packets/.../final/review_report.json` had still shown `needs_targeted_rework`, so I synced it to the source-reviewed final report. I also appended a current rework response resolving both tickets and refreshed the packet manifest, workflow context, and complete report.

Key status now:
- Final: `accepted_with_cautions`, `publication_grade=true`
- Activity/toxicity: `120` source-located records
- Database: `129` audits, `123 source_verified`, `6 source_conflict`
- Mechanism: `4` source-located claims
- Open rework tickets: `0`
- `quality_feedback.json`: `issue_count=0`, no `qc_failure_reasons`, no `unrecoverable_material_gaps`

Validation passed:
- Semantic gate: `publication_grade_pass_count=1`, `issue_count=0`
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`
- Message bus validate: `ok=true`
- JSON/JSONL syntax: `51` files checked, `0` errors
- Packet final review report now matches paper final review report

Updated main files include:
- [packet_manifest.json](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0170821/packet_manifest.json)
- [packet final review_report.json](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0170821/final/review_report.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0170821/rework/rework_responses.jsonl)
- [workflow_context.json](/root/work/抗菌肽/数据库/batch/4-team/.miaobi-paper-review/workflows/doi__10.1371_journal.pone.0170821/workflow_context.json)
- [complete_message_test_report.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0170821.complete_message_test_report.json)
- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0170821.semantic_gate.json)
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0170821.publication_quality.json)

