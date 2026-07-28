Done. Wrote [owner_response.json](/root/work/抗菌肽/数据库/batch/4-team/reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch-008-PILOT20-017-worker-5/owner_response.json).

Set `action_taken` to `repair_ready`. Recommended mappings are:

- `mech-001`: `computational_model` -> `computational_only`
- `mech-002`: `phenotypic_resistance_assay` -> `phenotype_supported`
- `mech-003`: remains `direct_mechanism`
- `mech-004`: `contextual_mechanism_assay` -> `phenotype_supported`

I checked the true review result, ticket, dispatch packet, current mechanism artifact, review report, Fig. 3/Fig. 5 captions, and Methods lines `1587-1607`. No missing mechanism-critical material was found. Canonical `papers/.../final/` files were not edited; `worker6_followup_required` is `true`.

Validation: `jq -e` required-field/action check passed.

