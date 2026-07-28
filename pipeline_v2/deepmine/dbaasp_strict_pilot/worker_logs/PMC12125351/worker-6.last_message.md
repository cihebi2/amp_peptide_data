Completed worker-6 adjudication for `PMC12125351` without browsing.

Wrote/updated:
- `work/review/adjudication_report.json`
- `work/review/quality_feedback.json`
- `final/activity_toxicity_evidence.json`
- `final/database_record_verification.json`
- `final/mechanism_ontology_record.json`
- `final/review_report.json`
- packet final mirrors, including `packets/PMC12125351/final/mechanism_evidence.json`
- appended 19 new strict `worker-6` `closed_repaired` terminal responses to `rework_responses.jsonl`

Verification:
- Packet gate: `0`, `open_rework_ticket_count=0`, `hard_finding_count=0`
- Semantic gate: `0`, `publication_grade_pass_count=1`, `issue_count=0`
- Publication gate: `0`, `publication_grade_pass=true`
- Final counts: `activity_records=130`, `toxicity_records=126`, `database_record_audits=4`, `mechanism_claims=4`, `review_rework_targets=0`
- Paper/packet mirrors are byte-identical, including the mechanism alias.

Unresolved blockers: none. Lane status is source-reviewed complete with cautions: `review_status=accepted_with_cautions`, `publication_grade=true`. Remaining cautions are nonblocking preserved conflicts/database-only fallback rows, with authoritative DBAASP ingest kept false.