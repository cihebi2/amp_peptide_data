Completed worker-6 adjudication for `PMC12837634`.

Files written/updated:
- Required worker-6 finals and review files under `papers/PMC12837634/work/review/` and `papers/PMC12837634/final/`
- Packet mirrors under `packets/PMC12837634/final/`, including aligned `mechanism_evidence.json`
- Live packet status: `packet_manifest.json` and `analysis/analysis_status.json`
- Appended exactly one worker-6 terminal `closed_repaired` response for the assigned ticket in `rework/rework_responses.jsonl`
- Fresh gate artifacts under `papers/PMC12837634/work/review/gates/live_materials_manifest_*`

Verification:
- Packet gate: exit `0`, `hard_finding_count=0`, `open_rework_ticket_count=0`
- Semantic gate: exit `0`, `publication_grade_pass_count=1`, `issue_count=0`
- Publication gate: exit `0`, `publication_grade_pass=true`, `risk_counts={}`
- Final mirror pairs are byte-identical.
- Final counts: `activity_records=38`, `toxicity_records=33`, `database_record_audits=42`, `mechanism_claims=3`, `review_rework_targets=0`

Unresolved blockers: none.

Lane status: source-reviewed complete, `accepted_with_cautions`, `publication_grade=true`. Cautions preserved for absent authoritative DBAASP linked rows and approximate figure-derived values.