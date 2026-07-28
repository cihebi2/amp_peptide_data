# Worker-6 Final Mirror / Re-adjudication

You are worker-6 (`paper-adjudicator-review-worker`) for one pilot20 dispatch.

## Hard constraints

- Use `gpt-5.5` with `reasoning_effort=xhigh`; runner command provides this.
- Preserve conflicts, cautions, database-only, unresolved, and material gaps.
- Do not mark `accepted_clean`.
- Do not mark publication-grade true if hard rework or missing material remains.
- Do not hide uncertainty by replacing blocked rows with guessed evidence.
- If action is `blocked_missing_material` or `needs_upstream_material`, write/confirm a blocked or needs-targeted-rework final status; do not force acceptance.

## Input

- dispatch_id: `dispatch-006-PILOT20-014-worker-5`
- paper_id: `doi__10.1016_j.isci.2020.101785`
- owner_worker: `worker-5_mechanism_ontology_extractor`
- owner action: `repair_ready`
- owner response: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-006-PILOT20-014-worker-5/owner_response.json`
- dispatch packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-006-PILOT20-014-worker-5/dispatch_packet.json`
- source review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-014__doi__10.1016_j.isci.2020.101785`
- write response JSON: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_final_mirror/dispatch-006-PILOT20-014-worker-5/worker6_final_response.json`
- response schema: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_final_mirror/dispatch-006-PILOT20-014-worker-5/worker6_final_response.schema.json`

Read these instructions before editing:

1. `.codex/skills/amp-three-layer-curation/SKILL.md`
2. `.codex/skills/paper-adjudicator-review-worker/SKILL.md`
3. `.codex/skills/amp-three-layer-curation/references/publication-grade-quality-gate.md`
4. `.codex/skills/amp-three-layer-curation/references/team-rework-message-contract.md`

## Task

1. Read the owner response and verify whether it performed an analysis-layer repair or only recommended a repair.
2. For `repair_ready`:
   - If local owner-updated analysis artifacts contain only allowed mechanism evidence classes, mirror them into packet final and `papers/<paper_id>/final/` mechanism artifacts where safe.
   - Update `papers/<paper_id>/final/review_report.json` and packet final review report with worker-6 provenance, checked inputs, semantic QA summary, caution findings, and no hard rework targets only if the final artifacts are now clean enough for `accepted_with_cautions`.
   - Preserve non-clean cautions. `accepted_with_cautions` is the highest allowed positive decision in this pilot.
3. For `blocked_missing_material` or `needs_upstream_material`:
   - Write/update `review_report.json` as `blocked_missing_primary_material` or `needs_targeted_rework`, `publication_grade: false`, and concrete `unrecoverable_material_gaps` / `rework_targets`.
   - Do not attempt to invent missing supplement/PDF/XML evidence.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_final_mirror/dispatch-006-PILOT20-014-worker-5/worker6_final_response.json` matching schema with:
   - `final_decision`
   - `files_updated`
   - `qc_summary`
   - `remaining_blockers`
   - `worker6_followup`

Use Python/JSON tools if helpful. Keep final response short and point to the response JSON.
