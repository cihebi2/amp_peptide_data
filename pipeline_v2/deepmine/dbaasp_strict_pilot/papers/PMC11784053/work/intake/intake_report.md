# Worker-1 Intake Report: PMC11784053

Reviewed at: 2026-07-15T09:21:12Z

## Status

- Lane: worker-1 intake/material linkage for `amp_three_layer_v2_dbaasp_strict_pilot`.
- Intake result: `material_inventory_reviewed_complete_with_cautions`.
- Targeted worker-1 rework required: `false`.
- `analysis_status.json` changed by worker-1 in this turn: `false`.
- Publication-grade claim by worker-1: `false`.
- Database identity verification claim by worker-1: `false`.

## Packet And Source Surfaces

- Paper root: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11784053`
- Packet root: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11784053`
- Primary XML/PDF/meta files are present in both `papers/.../source/` and `packets/.../raw/` and byte-match across the mirrored copies.
- Supplementary candidate file count from `supplementary_index.json`: `1`.
- Supplementary candidate `raw/supplementary_original/3.pdf` is byte-identical to `raw/paper.pdf`; recorded as a material caution, not as a new blocker.

## Extraction Inventory

- XML sections: `104`; XML parse status: `parsed`.
- PDF text rows: `6`; PDF table records: `3`.
- Figure caption records: `7`.
- Supplementary text rows: `6`; supplementary table records: `0`.
- Archive records: `0`; extraction error rows: `0`.
- Locator count: `116`.

## Database Provenance Boundary

- DBAASP machine candidate rows: `77`.
- Linked authoritative article/assay/sequence/literature rows: `0` total.
- Local authoritative match report has `source_record_links_present=false`; fallback rows remain candidate machine evidence only and are separate from paper-local evidence.

## Rework Ledger

- Rework request rows: `10`; response rows: `37`.
- Worker-1/material ticket IDs seen: `rwk-PMC11784053-authoritative-dbaasp-no-match-001`.
- Live worker-1/material ticket IDs after response-ledger closure check: `none`.
- Scoped packet gate return code: `0`; hard findings: `0`.
- Packet gate still reports historical request rows as open count `10`, but the scoped hard-finding count is zero under the response closure contract.

## Files

- Inventory JSON: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11784053/work/intake/source_inventory.json`
- Scoped packet gate JSON: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11784053/work/intake/packet_gate.worker1_scoped_20260715T091816Z.json`
- Scoped packet gate stdout log: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11784053/work/intake/packet_gate.worker1_scoped_20260715T091816Z.stdout.log`
- Scoped packet gate stderr log: `/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11784053/work/intake/packet_gate.worker1_scoped_20260715T091816Z.stderr.log`
