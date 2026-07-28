# Pilot20 Owner-Worker Rework Prompt

You are `worker-5_mechanism_ontology_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.1038_srep24000`
- Audit record: `doi__10.1038_srep24000:database_audit:167`
- Ticket id: `pilot20-016-true-review-rwk-001`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-016__doi__10.1038_srep24000`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-016__doi__10.1038_srep24000/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-016__doi__10.1038_srep24000/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-016__doi__10.1038_srep24000/rework_ticket.json",
  "audit_record_id": "doi__10.1038_srep24000:database_audit:167",
  "blocks": [
    "publication_grade_confirmation_for_pilot20_true_source_review",
    "final_review_report_acceptance_without_caution_reconciliation",
    "mechanism_ontology_record_acceptance"
  ],
  "created_at": "2026-06-22T04:20:14Z",
  "paper_id": "doi__10.1038_srep24000",
  "reason": "Bounded true source review could not terminally confirm publication-grade status because the runtime model/effort provenance was not independently verifiable, and the paper-level mechanism/adjudication artifacts contain repairable hard issues: mechanism claims mech-001 and mech-003 use non-standard evidence_class value mechanistic_context, and packet-level status metadata still carries analysis-needs-rework/test-scope/open-ticket signals while finals claim publication_grade=true.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "acceptance_check": "All mechanism_claims evidence_class values are one of direct_mechanism, phenotype_supported, inferred_mechanism, computational_only, or unknown_or_not_tested; direct_mechanism claims retain direct_assay_types and locators.",
      "artifact": "papers/doi__10.1038_srep24000/final/mechanism_ontology_record.json",
      "need": "Replace non-standard mechanism evidence classes with allowed ontology values while preserving source locators and limitations.",
      "required_locators": [
        "xml:sec=4:Cytotoxicity assay",
        "xml:sec=5:Cell membrane constituents assays",
        "xml:sec=10:Discussion"
      ]
    },
    {
      "acceptance_check": "Packet manifest, analysis status, rework state, and final review_report agree on terminal status with no contradictory open rework/test-scope indicators.",
      "artifact": "paper_packets/doi__10.1038_srep24000/packet_manifest.json",
      "need": "Reconcile packet terminal metadata with analysis_status, rework request/response records, and final review_report after mechanism repair.",
      "required_locators": [
        "paper_packets/doi__10.1038_srep24000/analysis/analysis_status.json",
        "paper_packets/doi__10.1038_srep24000/rework/rework_requests.jsonl",
        "paper_packets/doi__10.1038_srep24000/rework/rework_responses.jsonl",
        "papers/doi__10.1038_srep24000/final/review_report.json"
      ]
    }
  ],
  "severity": "blocking",
  "target_queue": "analysis",
  "ticket_id": "pilot20-016-true-review-rwk-001"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-007-PILOT20-016-worker-5/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
