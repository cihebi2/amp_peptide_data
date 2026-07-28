# Pilot20 Owner-Worker Rework Prompt

You are `worker-5_mechanism_ontology_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.1021_acsomega.0c01462`
- Audit record: `doi__10.1021_acsomega.0c01462:database_audit:31`
- Ticket id: `pilot20-010-rwk-20260622-mechanism-evidence-class`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-010__doi__10.1021_acsomega.0c01462`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-010__doi__10.1021_acsomega.0c01462/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-010__doi__10.1021_acsomega.0c01462/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-010__doi__10.1021_acsomega.0c01462/rework_ticket.json",
  "audit_record_id": "doi__10.1021_acsomega.0c01462:database_audit:31",
  "blocks": [
    "mechanism_ontology_record",
    "publication_grade_confirmation_for_pilot20_sample",
    "pass_source_review_or_accepted_with_cautions_confirmed_decision"
  ],
  "created_at": "2026-06-22T04:07:09Z",
  "paper_id": "doi__10.1021_acsomega.0c01462",
  "reason": "Mechanism claims mech-002 and mech-003 are source-located phenotype claims, but their evidence_class values are non-standard strings rather than the required top-level ontology value phenotype_supported. The primary material is present; this is a repairable worker-5/analysis ontology normalization defect.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "artifact": "paper_packets/doi__10.1021_acsomega.0c01462/analysis/mechanism_evidence.json",
      "need": "Set mechanism_claims[1].evidence_class and mechanism_claims[2].evidence_class to phenotype_supported while preserving claim_id, claim_text, entity_scope, locators, and limitations."
    },
    {
      "artifact": "papers/doi__10.1021_acsomega.0c01462/final/mechanism_ontology_record.json",
      "need": "Mirror the corrected evidence_class vocabulary in the final mechanism ontology artifact."
    },
    {
      "artifact": "papers/doi__10.1021_acsomega.0c01462/final/review_report.json",
      "need": "Re-run or update worker-6 adjudication after mechanism evidence_class repair and preserve the existing sequence_modified_not_normalized caution."
    }
  ],
  "severity": "major",
  "target_queue": "analysis",
  "ticket_id": "pilot20-010-rwk-20260622-mechanism-evidence-class"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-003-PILOT20-010-worker-5/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
