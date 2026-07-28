# Pilot20 Owner-Worker Rework Prompt

You are `worker-5_mechanism_ontology_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.2174_1381612822666161027120518`
- Audit record: `doi__10.2174_1381612822666161027120518:database_audit:138`
- Ticket id: `pilot20-012-rwk-001`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-012__doi__10.2174_1381612822666161027120518`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-012__doi__10.2174_1381612822666161027120518/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-012__doi__10.2174_1381612822666161027120518/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-012__doi__10.2174_1381612822666161027120518/rework_ticket.json",
  "audit_record_id": "doi__10.2174_1381612822666161027120518:database_audit:138",
  "blocks": [
    "layer3_mechanism_review",
    "worker6_publication_grade_confirmation",
    "final_source_review_acceptance_for_PILOT20-012"
  ],
  "created_at": "2026-06-22T04:11:28Z",
  "paper_id": "doi__10.2174_1381612822666161027120518",
  "reason": "Layer-3 mechanism claims are source-located and do not overclaim direct mechanisms, but mechanism_claims[*].evidence_class uses custom labels instead of the required ontology values. This prevents confirming publication-grade acceptance from the current final artifact.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "artifact": "paper_packets/doi__10.2174_1381612822666161027120518/final/mechanism_evidence.json",
      "need": "Rewrite mechanism_claims[*].evidence_class using only direct_mechanism, phenotype_supported, inferred_mechanism, computational_only, or unknown_or_not_tested; preserve claim_id, claim_text, source_locator, and limitation notes.",
      "required_locators": [
        "xml:sec=3.4:Antimicrobial Activity",
        "xml:table=2",
        "xml:sec=3.5:Hemolytic Activity and Membranolytic Selectivity",
        "xml:table=3",
        "xml:sec=3.6:Chemotaxis",
        "xml:sec=4:Discussion"
      ]
    },
    {
      "artifact": "paper_packets/doi__10.2174_1381612822666161027120518/final/review_report.json",
      "need": "Re-adjudicate after mechanism ontology repair and preserve remaining cautions, especially sequence_modified_not_normalized and no direct molecular mechanism assay."
    }
  ],
  "severity": "major",
  "target_queue": "analysis",
  "ticket_id": "pilot20-012-rwk-001"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-005-PILOT20-012-worker-5/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
