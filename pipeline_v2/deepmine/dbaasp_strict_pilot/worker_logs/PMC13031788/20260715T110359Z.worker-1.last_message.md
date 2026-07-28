Completed worker-1 intake refresh for `PMC13031788`.

Files written/updated:
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13031788/work/intake/source_inventory.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13031788/work/intake/intake_report.md`
- validation artifacts under `.../work/intake/`: `single_paper_manifest.worker1.refresh.json` and `check_two_queue_packets.worker1.refresh.*`

`analysis_status.json` was not changed; current status is already `analysis_source_reviewed_accepted`.

Validation evidence:
- scoped packet gate `rc=0`
- hard findings `0`
- open rework tickets `0`
- JSON/JSONL syntax checks passed

Unresolved worker-1 blockers: none. Five intake cautions are recorded, including authoritative linked DBAASP rows absent and DBAASP fallback rows treated as candidate machine evidence only.

Lane status: worker-1 intake/material lane is source-reviewed complete for inventory purposes and does not need targeted rework. No `source_verified` or worker-1 publication-grade claim was made.

