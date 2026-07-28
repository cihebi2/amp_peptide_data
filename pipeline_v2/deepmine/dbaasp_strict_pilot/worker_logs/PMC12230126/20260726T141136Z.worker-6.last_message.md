Completed worker-6 adjudication for `PMC12230126`.

Files written/updated:
- `papers/PMC12230126/work/review/adjudication_report.json`
- `papers/PMC12230126/work/review/quality_feedback.json`
- `papers/PMC12230126/final/database_record_verification.json`
- `papers/PMC12230126/final/activity_toxicity_evidence.json`
- `papers/PMC12230126/final/mechanism_ontology_record.json`
- `papers/PMC12230126/final/review_report.json`
- Packet final mirrors under `packets/PMC12230126/final/`, including aligned `mechanism_evidence.json`
- Appended one worker-6 terminal `closed_repaired` response for `rwk-PMC12230126-recursive-authority-boundary-007`
- Verification/gate reports under `papers/PMC12230126/work/review/`, including `worker6_ticket007_terminal_closure_verification.json`

Final checks:
- Packet gate: `hard=0`, `open=0`
- Semantic gate: pass `1`, fail `0`
- Publication gate: pass `true`, risk counts `{}`
- Paper/packet final mirrors: byte-identical
- Recursive `authoritative_dbaasp_ingest_ready=true` count: `0`
- Ticket 007 worker-6 terminal response count: `1`

Unresolved blockers: none. Lane status is source-reviewed complete with cautions: authoritative DBAASP ingest remains `false` because linked authoritative DBAASP rows are absent, and fallback rows remain candidate-only.