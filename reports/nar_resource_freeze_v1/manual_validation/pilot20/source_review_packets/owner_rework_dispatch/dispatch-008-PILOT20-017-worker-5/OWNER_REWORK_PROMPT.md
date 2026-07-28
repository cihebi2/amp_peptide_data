# Pilot20 Owner-Worker Rework Prompt

You are `worker-5_mechanism_ontology_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.1038_s41467-023-42434-9`
- Audit record: `doi__10.1038_s41467-023-42434-9:database_audit:304`
- Ticket id: `pilot20-017-rwk-20260622-001`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-017__doi__10.1038_s41467-023-42434-9`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-017__doi__10.1038_s41467-023-42434-9/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-017__doi__10.1038_s41467-023-42434-9/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-017__doi__10.1038_s41467-023-42434-9/rework_ticket.json",
  "audit_record_id": "doi__10.1038_s41467-023-42434-9:database_audit:304",
  "blocks": [
    "layer3_mechanism_review",
    "worker6_publication_grade_confirmation_for_pilot20_sample"
  ],
  "created_at": "2026-06-22T04:21:07Z",
  "paper_id": "doi__10.1038_s41467-023-42434-9",
  "reason": "Layer-3 mechanism final artifact uses non-canonical top-level evidence_class values (computational_model, phenotypic_resistance_assay, contextual_mechanism_assay) instead of the AMP three-layer ontology. Source locators are present and the direct PI/microscopy claim has direct_assay_types, so this is a targeted ontology repair rather than missing primary material.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "artifact": "papers/doi__10.1038_s41467-023-42434-9/final/mechanism_ontology_record.json",
      "need": "Map mechanism_claims[0], [1], and [3] to canonical evidence_class values: direct_mechanism, phenotype_supported, inferred_mechanism, computational_only, or unknown_or_not_tested. Preserve subtype detail in a separate field or limitations note.",
      "required_locators": [
        "xml:fig=3:Fig. 3",
        "xml:fig=5:Fig. 5",
        "pdf:Methods:Mode of action assay and microscopy using propidium iodide lines 1587-1607"
      ]
    },
    {
      "artifact": "papers/doi__10.1038_s41467-023-42434-9/final/review_report.json",
      "need": "Re-adjudicate after mechanism ontology repair and keep APD6 AP03779 database_only_no_primary_source caution unchanged."
    }
  ],
  "severity": "major",
  "target_queue": "analysis",
  "ticket_id": "pilot20-017-rwk-20260622-001"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-008-PILOT20-017-worker-5/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
