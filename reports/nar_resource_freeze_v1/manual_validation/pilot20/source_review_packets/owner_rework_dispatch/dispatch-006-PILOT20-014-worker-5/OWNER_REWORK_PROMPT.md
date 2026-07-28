# Pilot20 Owner-Worker Rework Prompt

You are `worker-5_mechanism_ontology_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.1016_j.isci.2020.101785`
- Audit record: `doi__10.1016_j.isci.2020.101785:database_audit:12`
- Ticket id: `pilot20-014-true-review-rwk-001`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-014__doi__10.1016_j.isci.2020.101785`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-014__doi__10.1016_j.isci.2020.101785/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-014__doi__10.1016_j.isci.2020.101785/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-014__doi__10.1016_j.isci.2020.101785/rework_ticket.json",
  "audit_record_id": "doi__10.1016_j.isci.2020.101785:database_audit:12",
  "blocks": [
    "publication_grade_ready",
    "final_review_confirmation",
    "layer3_mechanism_ontology_acceptance"
  ],
  "created_at": "2026-06-22T04:16:46Z",
  "paper_id": "doi__10.1016_j.isci.2020.101785",
  "reason": "The sampled DBAASP database-only row is justified, but the paper-level final mechanism ontology remains a pending/test-scope scaffold: mechanism_claims use nonstandard evidence_class mechanism_context_pending_review and the artifact states it is not publication-grade mechanism adjudication. Worker-6 review currently over-accepts this final artifact as publication_grade.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "artifact": "papers/doi__10.1016_j.isci.2020.101785/final/mechanism_ontology_record.json",
      "need": "Rebuild mechanism_claims from local XML/PDF/supplement/figure-caption evidence using only standard ontology classes: direct_mechanism, phenotype_supported, inferred_mechanism, computational_only, or unknown_or_not_tested. Include direct assay types only for direct_mechanism claims.",
      "owner": "worker-5"
    },
    {
      "artifact": "papers/doi__10.1016_j.isci.2020.101785/final/review_report.json",
      "need": "Re-adjudicate layer 3 after mechanism repair and update review_status/publication_grade/rework_targets based on the repaired source-reviewed mechanism artifact.",
      "owner": "worker-6"
    }
  ],
  "severity": "blocking",
  "target_queue": "analysis",
  "ticket_id": "pilot20-014-true-review-rwk-001"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-006-PILOT20-014-worker-5/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
