# Pilot20 Owner-Worker Rework Prompt

You are `worker-5_mechanism_ontology_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.1038_s41522-024-00637-y`
- Audit record: `doi__10.1038_s41522-024-00637-y:database_audit:1`
- Ticket id: `pilot20-018-true-review-rwk-001`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-018__doi__10.1038_s41522-024-00637-y`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-018__doi__10.1038_s41522-024-00637-y/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-018__doi__10.1038_s41522-024-00637-y/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-018__doi__10.1038_s41522-024-00637-y/rework_ticket.json",
  "audit_record_id": "doi__10.1038_s41522-024-00637-y:database_audit:1",
  "blocks": [
    "publication_grade_confirmation_for_pilot20_true_source_review",
    "source_verified_status_for_DBAASP_DBAASPS_11338",
    "supplement_dependent_activity_or_mechanism_exact_value_confirmation"
  ],
  "created_at": "2026-06-22T04:24:04Z",
  "paper_id": "doi__10.1038_s41522-024-00637-y",
  "reason": "Best-effort local source review confirms that the sampled DBAASP unresolved_record should remain non-publication-grade: true supplementary Table 1/Figs. 1-13 are absent from local materials, the OA package is absent after recorded fetch failure, all ten supplementary landing-*.bin files are HTML landing pages, and exact DJK-5 sequence/modification evidence is absent from both local primary XML/PDF and linked_sequence_records.jsonl.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "acceptance_check": "supplementary_tables.json or supplementary_text.jsonl contains source-reviewable table/figure material instead of indexed_only landing pages.",
      "artifact": "paper_packets/doi__10.1038_s41522-024-00637-y/raw/oa_package or raw/supplementary_original",
      "need": "Recover true supplementary files, especially Supplementary Table 1 and Supplementary Figs. 1-13, not article landing HTML.",
      "required_locators": [
        "supp:Supplementary Table 1",
        "supp:Supplementary Fig. 1-13"
      ]
    },
    {
      "acceptance_check": "DBAASP:DBAASPS_11338 is not marked source_verified unless exact sequence/modification evidence is locally available.",
      "artifact": "paper_packets/doi__10.1038_s41522-024-00637-y/database/linked_sequence_records.jsonl or primary XML/PDF locator",
      "need": "Provide exact DJK-5 sequence/modification evidence or explicitly preserve database-only/unresolved status.",
      "required_locators": [
        "database:linked_sequence_records:DBAASP:DBAASPS_11338",
        "xml/pdf locator for exact DJK-5 sequence/modification if present"
      ]
    },
    {
      "artifact": "papers/doi__10.1038_s41522-024-00637-y/final/review_report.json",
      "need": "Worker-6 re-adjudication after any recovered material; otherwise keep blocked_missing_primary_material and publication_grade=false."
    }
  ],
  "severity": "blocking",
  "target_queue": "material_extraction",
  "ticket_id": "pilot20-018-true-review-rwk-001"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-009-PILOT20-018-worker-5/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
