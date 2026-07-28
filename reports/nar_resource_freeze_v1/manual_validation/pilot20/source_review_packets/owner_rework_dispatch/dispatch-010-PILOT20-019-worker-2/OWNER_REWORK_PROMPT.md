# Pilot20 Owner-Worker Rework Prompt

You are `worker-2_main_text_assay_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.1038_s41598-017-16784-6`
- Audit record: `doi__10.1038_s41598-017-16784-6:database_audit:10`
- Ticket id: `pilot20-019-rwk-moesm1-local-supplement-absent`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-019__doi__10.1038_s41598-017-16784-6`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-019__doi__10.1038_s41598-017-16784-6/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-019__doi__10.1038_s41598-017-16784-6/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-019__doi__10.1038_s41598-017-16784-6/rework_ticket.json",
  "audit_record_id": "doi__10.1038_s41598-017-16784-6:database_audit:10",
  "blocks": [
    "database_record_verification:DBAASP:DBAASPR_3442:assay_498",
    "activity_toxicity_evidence:DBAASP_checkerboard_FICI_rows",
    "publication_grade_ready",
    "final_approval"
  ],
  "created_at": "2026-06-22T12:24:23+08:00",
  "paper_id": "doi__10.1038_s41598-017-16784-6",
  "reason": "Sampled DBAASP assay 498 is a supplement-dependent checkerboard MIC/FICI row. The XML references 41598_2017_16784_MOESM1_ESM.pdf and Tables S1/S2, but local packet, paper directory, and landed-asset paper root contain no MOESM1 PDF or parsed supplementary table; only HTML landing .bin files were found.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "asset": "41598_2017_16784_MOESM1_ESM.pdf",
      "need": "Recover or stage the real supplementary PDF locally.",
      "required_locators": [
        "supp:MOESM1",
        "supp:MOESM1:table=S1",
        "supp:MOESM1:table=S2"
      ]
    },
    {
      "asset": "paper_packets/doi__10.1038_s41598-017-16784-6/extracted/supplementary_tables.json",
      "need": "Parse Tables S1/S2 into row-level checkerboard MIC/FICI evidence for DBAASP synergy rows, including assay 498.",
      "required_locators": [
        "database:linked_assay_records.jsonl:row=10",
        "xml:sec=13:Synergistic effect of Macropin and antibiotics"
      ]
    }
  ],
  "severity": "blocking",
  "target_queue": "material_extraction",
  "ticket_id": "pilot20-019-rwk-moesm1-local-supplement-absent"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-010-PILOT20-019-worker-2/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
