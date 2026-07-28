# Pilot20 Owner-Worker Rework Prompt

You are `worker-2_main_text_assay_extractor` for the AMP Evidence Atlas pilot20 true source-review rework queue.

## Scope

- Work only on this paper and ticket.
- Do not mark publication-grade acceptance yourself unless you are worker-6.
- Preserve conflicts and cautions; do not convert uncertainty into clean source_verified.
- If material is insufficient after best effort, write that explicitly and stop.

## Inputs

- Paper: `doi__10.21203_rs.3.rs-578319_v1`
- Audit record: `doi__10.21203_rs.3.rs-578319_v1:database_audit:18`
- Ticket id: `pilot20-020-rwk-20260622-true-supplement-gap`
- Review packet: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-020__doi__10.21203_rs.3.rs-578319_v1`
- Source review result: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-020__doi__10.21203_rs.3.rs-578319_v1/true_review_result.json`
- Original ticket source: `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-020__doi__10.21203_rs.3.rs-578319_v1/rework_ticket.json`

Ticket:

```json
{
  "_source_ticket_path": "reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-020__doi__10.21203_rs.3.rs-578319_v1/rework_ticket.json",
  "audit_record_id": "doi__10.21203_rs.3.rs-578319_v1:database_audit:18",
  "blocks": [
    "sample_source_verification",
    "activity_value_or_unit_resolution",
    "publication_grade_ready"
  ],
  "created_at": "2026-06-22T04:27:55Z",
  "paper_id": "doi__10.21203_rs.3.rs-578319_v1",
  "reason": "Sample DBAASP:DBAASPS_17498 remains unresolved because exact uperin 3.5 I13C sequence/activity verification depends on primary supplementary material that is absent locally. The primary PDF lists SIEngerbergFK13Cys2021.7.pdf and D1292113255valreportfullP1.pdf, but local supplementary landing-*.bin files are Research Square HTML pages and supplementary_tables.json contains zero tables.",
  "requested_by": "pilot20_true_source_review",
  "requested_outputs": [
    {
      "asset": "SIEngerbergFK13Cys2021.7.pdf",
      "need": "Recover/extract true supplementary figures/tables, especially Supplementary Table 5 rows for uperin 3.5, I13C, and S11C MIC/DTT evidence.",
      "required_locators": [
        "supp:SIEngerbergFK13Cys2021.7.pdf:table=Supplementary Table 5"
      ]
    },
    {
      "asset": "D1292113255valreportfullP1.pdf",
      "need": "Recover/check validation report only if it affects source identity, supplement provenance, or sequence/activity interpretation.",
      "required_locators": [
        "supp:D1292113255valreportfullP1.pdf"
      ]
    },
    {
      "asset": "paper_packets/doi__10.21203_rs.3.rs-578319_v1/raw/paper.xml",
      "need": "Replace or explicitly gap-record the current RSS/browse XML with usable article XML if available locally.",
      "required_locators": [
        "xml:article-body",
        "xml:article-tables"
      ]
    }
  ],
  "severity": "blocking",
  "target_queue": "material_extraction",
  "ticket_id": "pilot20-020-rwk-20260622-true-supplement-gap"
}
```

## Required action

1. Re-open the source review result and the cited packet materials.
2. Repair only the owned layer if local evidence is sufficient.
3. If repair is not safe, write a best-effort blocker with exact missing material or locator.
4. Write `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-011-PILOT20-020-worker-2/owner_response.json` as JSON with:
   - `ticket_id`
   - `paper_id`
   - `owner_worker`
   - `action_taken`: `repair_ready`, `blocked_missing_material`, `needs_upstream_material`, or `defer_to_worker6`
   - `files_to_update_or_review`
   - `source_inputs_checked`
   - `remaining_gaps`
   - `worker6_followup_required`: boolean

Do not edit canonical `papers/<paper_id>/final/` in this dispatch pass unless explicitly running a repair task. This prompt is the durable owner-worker handoff packet.
