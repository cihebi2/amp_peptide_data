Wrote the worker-1 intake artifacts for `PMC11735859`:

- [source_inventory.json](/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11735859/work/intake/source_inventory.json)
- [intake_report.md](/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11735859/work/intake/intake_report.md)

I did not update `analysis_status.json`; it remains `analysis_queued` because intake status did not change.

Unresolved blockers: none for worker-1 material intake. Cautions recorded: no OA package path declared, supplementary DOCX text is extracted but structured supplementary table rows are absent, and authoritative DBAASP/merged linked rows are all zero while five Codex fallback rows remain machine candidates only.

Validation: `source_inventory.json` passes `jq`; no disallowed verified-record status terms were introduced in the two new files; analysis status remains unchanged. Lane status: source-reviewed complete for worker-1 intake/material inventory only, with cautions; no targeted worker-1 rework needed.