# Pilot20 Owner-Worker Rework Prompt

You are `worker-5_mechanism_ontology_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.1038_s41598-018-29444-0`
- Audit record: `doi__10.1038_s41598-018-29444-0:database_audit:61`
- Ticket id: `pilot20-003-true-review-rwk-001`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-003__doi__10.1038_s41598-018-29444-0`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-003__doi__10.1038_s41598-018-29444-0/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-003__doi__10.1038_s41598-018-29444-0/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-003__doi__10.1038_s41598-018-29444-0/rework_ticket.json",
  "audit_record_id": "doi__10.1038_s41598-018-29444-0:database_audit:61",
  "blocks": [
    "layer3_mechanism_review",
    "paper_level_final_artifact_confirmation",
    "publication_grade_confirmation"
  ],
  "created_at": "2026-06-22T03:51:44Z",
  "paper_id": "doi__10.1038_s41598-018-29444-0",
  "reason": "The sampled dbAMP row is source-backed, but the paper-level mechanism final contains claim_id=mech-003 with non-standard evidence_class mechanistic_inference_with_direct_biophysical_support. The allowed ontology is direct_mechanism, phenotype_supported, inferred_mechanism, computational_only, or unknown_or_not_tested.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "artifact": "papers/doi__10.1038_s41598-018-29444-0/final/mechanism_ontology_record.json",
      "need": "Revise mechanism_claims[2] so evidence_class uses the standard ontology, preserving locators and limitations."
    },
    {
      "artifact": "paper_packets/doi__10.1038_s41598-018-29444-0/final/mechanism_evidence.json",
      "need": "Mirror the same mechanism ontology correction in the packet final artifact."
    },
    {
      "artifact": "papers/doi__10.1038_s41598-018-29444-0/final/review_report.json",
      "need": "Have worker-6 re-adjudicate after the mechanism ontology repair and update review status/provenance if accepted."
    }
  ],
  "severity": "major",
  "target_queue": "analysis",
  "ticket_id": "pilot20-003-true-review-rwk-001"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-002-PILOT20-003-worker-5/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
