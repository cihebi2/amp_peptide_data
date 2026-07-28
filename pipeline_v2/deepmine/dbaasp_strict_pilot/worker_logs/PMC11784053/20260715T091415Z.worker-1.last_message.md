Completed worker-1 intake update for `PMC11784053`.

Files written:
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11784053/work/intake/source_inventory.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11784053/work/intake/intake_report.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11784053/work/intake/worker1_one_paper_manifest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11784053/work/intake/packet_gate.worker1_scoped_20260715T091816Z.json`
- scoped packet-gate stdout/stderr logs and latest summary in the same intake directory

Validation:
- `source_inventory.json` parses as valid JSON.
- Scoped packet gate return code: `0`.
- Scoped packet gate hard findings: `0`.
- Live worker-1/material rework tickets after response-ledger check: `0`.
- `analysis_status.json` was not changed.

Unresolved blockers: none for worker-1. Cautions remain recorded: zero authoritative linked database rows in the local packet, 77 DBAASP fallback rows kept as candidate machine evidence only, and the staged supplementary candidate PDF is byte-identical to the primary PDF.

Lane status: worker-1 intake is source-reviewed complete with cautions; no targeted rework needed. No publication-grade or database identity-verification claim was made.