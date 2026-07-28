# Pilot20 Owner-Worker Rework Prompt

You are `worker-5_mechanism_ontology_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.1002_cmdc.201900465`
- Audit record: `doi__10.1002_cmdc.201900465:database_audit:305`
- Ticket id: `pilot20-002-rwk-mechanism-ontology-001`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-002__doi__10.1002_cmdc.201900465`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-002__doi__10.1002_cmdc.201900465/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-002__doi__10.1002_cmdc.201900465/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-002__doi__10.1002_cmdc.201900465/rework_ticket.json",
  "audit_record_id": "doi__10.1002_cmdc.201900465:database_audit:305",
  "blocks": [
    "layer3_mechanism_review",
    "worker6_publication_grade_confirmation",
    "pilot20_terminal_source_review_confirmation"
  ],
  "created_at": "2026-06-22T03:49:55Z",
  "paper_id": "doi__10.1002_cmdc.201900465",
  "reason": "The sampled DRAMP activity row is source-backed, but the paper-level final mechanism artifact uses non-ontology evidence_class values (mechanism_context_pending_review) and states the claims are automated locator notes, not publication-grade mechanism adjudication. Worker-6 final acceptance cannot be confirmed until worker-5 rebuilds the mechanism ontology and worker-6 re-adjudicates.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "artifact": "paper_packets/doi__10.1002_cmdc.201900465/analysis/mechanism_evidence.json",
      "need": "Rebuild mechanism_claims using only direct_mechanism, phenotype_supported, inferred_mechanism, computational_only, or unknown_or_not_tested.",
      "required_locators": [
        "source/paper.xml mechanism-relevant sections",
        "paper_packets/doi__10.1002_cmdc.201900465/extracted/pdf_text.jsonl",
        "paper_packets/doi__10.1002_cmdc.201900465/extracted/supplementary_text.jsonl"
      ]
    },
    {
      "artifact": "papers/doi__10.1002_cmdc.201900465/final/review_report.json",
      "need": "Worker-6 re-adjudication after mechanism repair; publication_grade must not remain true if non-ontology mechanism evidence classes persist."
    }
  ],
  "severity": "major",
  "target_queue": "analysis",
  "ticket_id": "pilot20-002-rwk-mechanism-ontology-001"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-001-PILOT20-002-worker-5/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
