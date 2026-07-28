# Pilot20 Owner-Worker Rework Prompt

You are `worker-5_mechanism_ontology_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.1155_2015_197608`
- Audit record: `doi__10.1155_2015_197608:database_audit:6`
- Ticket id: `pilot20-011-rwk-mechanism-class-20260622T041006Z`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-011__doi__10.1155_2015_197608`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-011__doi__10.1155_2015_197608/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-011__doi__10.1155_2015_197608/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-011__doi__10.1155_2015_197608/rework_ticket.json",
  "audit_record_id": "doi__10.1155_2015_197608:database_audit:6",
  "blocks": [
    "mechanism_ontology_record",
    "publication_grade_confirmation",
    "pilot20_true_source_review_acceptance"
  ],
  "created_at": "2026-06-22T04:10:06Z",
  "paper_id": "doi__10.1155_2015_197608",
  "reason": "The sampled DRAMP35528 row is correctly preserved as sequence_modified_not_normalized, but the paper-level mechanism artifact stores mechanism_claims[2] with evidence_class='mechanism_scope_guard', which is outside the required five-class mechanism ontology. This prevents confirming the existing accepted_with_cautions/publication_grade artifact as-is.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "artifact": "papers/doi__10.1155_2015_197608/final/mechanism_ontology_record.json",
      "need": "Move the molecular-target scope guard out of mechanism_claims or reclassify it with a standard ontology value.",
      "required_locators": [
        "xml:sec=10:3.2",
        "xml:sec=1:1. Introduction"
      ]
    },
    {
      "artifact": "papers/doi__10.1155_2015_197608/final/review_report.json",
      "need": "Update worker-6 adjudication/gate evidence after mechanism ontology repair.",
      "required_locators": [
        "papers/doi__10.1155_2015_197608/final/mechanism_ontology_record.json::mechanism_claims[2]"
      ]
    }
  ],
  "severity": "major",
  "target_queue": "analysis",
  "ticket_id": "pilot20-011-rwk-mechanism-class-20260622T041006Z"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-004-PILOT20-011-worker-5/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
