# Worker-1 Intake Report: PMC12812963

Generated: 2026-07-28T03:24:47Z

## Material Mirror Repair
- Ticket: `rwk-PMC12812963-campaign-r01-worker1-stale-material-final-and-packet-mirror-state`
- Status: `repair_ready_for_adjudication`
- Packet manifest material status: `material_extracted_with_gaps`
- Packet manifest analysis status: `analysis_needs_analysis_rework`
- Known missing/blocked materials: packet manifest `8`, paper final mirror `8`, packet final mirror `8`
- Open rework tickets: live requests `5`, analysis status field `5`
- Analysis status file changed: `false`
- Terminal closure: deferred to `worker-6`

## Inventory Counts
- Staged files in packet manifest: `8`
- Paper source supplementary files: `2`
- Packet raw supplementary files: `2`
- XML section records: `114`
- PDF text records: `11`
- Supplementary index records: `2`
- Extraction error records: `8`
- Linked database JSONL line counts recorded in `source_inventory.json`

## Boundaries
- Internet used: `false`
- DBAASP fallback rows remain candidate machine evidence only.
- Worker-1 made no `source_verified` claims.
- Publication-grade completion is not claimed by this lane.

## Files Written
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/intake/source_inventory.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/intake/intake_report.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/intake/worker1_material_mirror_validation.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/final/materials_manifest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/final/materials_manifest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/rework/rework_responses.jsonl` appended with one owner response row

## Unresolved Blockers
- `5` open rework ticket IDs remain in `rework_requests.jsonl` and packet status.
- `8` known missing/blocked material entries remain explicit packet gaps.
- Worker-6 must re-adjudicate before any terminal closure or publication-grade acceptance.

## Validation
- Mirror validation artifact: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/intake/worker1_material_mirror_validation.json`
- Packet gate return code: `0`
- Semantic gate return code: `1`
- Publication gate return code: `2`
- Gate outputs are diagnostic only for this worker-1 repair and do not close the assigned ticket.
