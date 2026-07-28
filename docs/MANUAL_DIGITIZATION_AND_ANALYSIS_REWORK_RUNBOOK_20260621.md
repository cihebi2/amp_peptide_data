# Manual Digitization And Analysis Rework Runbook 2026-06-21

This runbook records the bounded handling path for `needs_targeted_rework` papers whose remaining blockers were previously grouped as figure exact-value or manual-digitization candidates. It is a reproducible workflow note; it is not an acceptance certificate.

## Quality Boundary

- Manual digitization is a material/evidence-recovery task, not publication-grade acceptance.
- Exact values from figures, curves, bar plots, or images must not be promoted unless a controlled digitization record includes axis calibration, raw extracted points/bars, uncertainty, independent QA, and then passes owner-worker source review plus worker-6 adjudication.
- If primary source data, source tables, sequence tables, or machine-readable values are absent, preserve `source_conflict`, `database_only_no_primary_source`, or unresolved gap status and move on.
- Analysis/table/entity rework is separate from image digitization. Existing XML/table/database/locator evidence may justify a fresh owner-worker rework run, but final acceptance still requires strict gates.
- Scripts in this runbook may create task packets and queues; they never set `publication_grade=true` by themselves.

## Inputs

Core freeze artifacts:

- `reports/nar_resource_freeze_v1/needs_targeted_rework_triage_latest.csv`
- `reports/nar_resource_freeze_v1/needs_targeted_rework_work/material_or_digitization_backlog_latest.csv`
- `reports/nar_resource_freeze_v1/needs_targeted_rework_work/manual_digitization_candidates_latest.csv`
- `papers/<paper_id>/final/review_report.json`
- `papers/<paper_id>/work/review/quality_feedback.json`
- `paper_packets/<paper_id>/packet_manifest.json`
- `paper_packets/<paper_id>/locators/locator_index.json`
- `paper_packets/<paper_id>/extracted/*`
- `paper_packets/<paper_id>/database/*`

Required model/runtime for true owner-worker review:

- model: `gpt-5.5`
- reasoning: `xhigh`
- worker timeout: `1800` seconds or longer
- infra retry: up to `5`
- prompt mode: `policy_safe_minimal`

## Reproducible Command Sequence

Run from `/root/work/抗菌肽/数据库/batch/4-team`.

1. Refresh release and needs-targeted resolution inputs.

```bash
python scripts/build_nar_resource_freeze_v1.py
python scripts/triage_needs_targeted_rework.py
python scripts/write_needs_targeted_rework_resolution_reports.py
```

2. Generate manual-digitization task packets from the full material/digitization backlog. Use the target-queue filter to preserve the original 10-paper manual/digitization cohort even after the audit later subdivides it.

```bash
python scripts/audit_manual_digitization_candidates.py \
  --candidates reports/nar_resource_freeze_v1/needs_targeted_rework_work/material_or_digitization_backlog_latest.csv \
  --filter-target-queue manual_digitization_or_keep_backlog
```

Outputs:

- `reports/nar_resource_freeze_v1/needs_targeted_rework_work/manual_digitization_processing_latest.json`
- `reports/nar_resource_freeze_v1/needs_targeted_rework_work/manual_digitization_processing_latest.csv`
- `reports/nar_resource_freeze_v1/needs_targeted_rework_work/manual_digitization_processing_latest.md`
- `reports/nar_resource_freeze_v1/needs_targeted_rework_work/manual_digitization_task_manifest_latest.json`
- `reports/nar_resource_freeze_v1/needs_targeted_rework_work/manual_digitization_analysis_rework_candidates_latest.csv`
- `reports/nar_resource_freeze_v1/needs_targeted_rework_work/manual_digitization_controlled_tasks_latest.csv`
- `reports/nar_resource_freeze_v1/needs_targeted_rework_work/manual_digitization_not_digitizable_latest.csv`
- `paper_packets/<paper_id>/manual_digitization/feasibility.json`
- `paper_packets/<paper_id>/manual_digitization/manual_digitization_tasks.json`
- `paper_packets/<paper_id>/manual_digitization/digitization_evidence.json`

3. Re-audit the material/digitization backlog so the release-facing queues are split more precisely.

```bash
python scripts/audit_material_digitization_backlog.py
```

Expected split for the 2026-06-21 run:

- `manual_digitization_candidate`: local figure/chart assets exist, but controlled calibrated extraction is still required.
- `analysis_rework_candidate_not_auto_queued`: current packet has analysis-owned table/entity/mechanism repair targets and should be explicitly routed to owner-worker rework.
- `still_unrecoverable_backlog`: missing primary source data, sequence tables, or exact database material; do not relaunch owner-worker from the same packet.
- `source_staging_candidate`: material staging/source acquisition is required before review.

4. Dry-run true owner-worker review for analysis candidates before launching real workers.

```bash
python scripts/run_true_rework_queue.py \
  --paper-id doi__10.1021_acsomega.8b01876 \
  --paper-id doi__10.1038_s42003-022-03899-4 \
  --paper-id doi__10.3390_antibiotics11081080 \
  --max-rework 5 \
  --model gpt-5.5 \
  --reasoning-effort xhigh \
  --sandbox danger-full-access \
  --codex-bypass-approvals-and-sandbox \
  --worker-timeout-seconds 1800 \
  --worker-infra-retries 5 \
  --retry-worker-timeouts \
  --paper-runtime-retries 5 \
  --obtainable-only \
  --prompt-mode policy_safe_minimal \
  --run-label manual_digitization_analysis_rework_YYYYMMDD_dryrun \
  --dry-run
```

5. Launch real owner-worker review only for analysis candidates, not for missing-source blockers or raw figure-only candidates lacking controlled digitization evidence.

```bash
python scripts/run_true_rework_queue.py \
  --paper-id doi__10.1021_acsomega.8b01876 \
  --paper-id doi__10.1038_s42003-022-03899-4 \
  --paper-id doi__10.3390_antibiotics11081080 \
  --max-rework 5 \
  --model gpt-5.5 \
  --reasoning-effort xhigh \
  --sandbox danger-full-access \
  --codex-bypass-approvals-and-sandbox \
  --worker-timeout-seconds 1800 \
  --worker-infra-retries 5 \
  --retry-worker-timeouts \
  --paper-runtime-retries 5 \
  --obtainable-only \
  --prompt-mode policy_safe_minimal \
  --run-label manual_digitization_analysis_rework_YYYYMMDD
```

6. Rebuild and validate after owner-worker results finish.

```bash
python scripts/build_nar_resource_freeze_v1.py
python scripts/triage_needs_targeted_rework.py
python scripts/write_needs_targeted_rework_resolution_reports.py
python scripts/audit_material_digitization_backlog.py
python scripts/audit_manual_digitization_candidates.py \
  --candidates reports/nar_resource_freeze_v1/needs_targeted_rework_work/material_or_digitization_backlog_latest.csv \
  --filter-target-queue manual_digitization_or_keep_backlog
python scripts/build_nar_resource_freeze_v1.py
python scripts/validate_needs_targeted_rework_processing.py
python -m json.tool reports/nar_resource_freeze_v1/release_manifest_latest.json >/tmp/release_manifest_check
python -m json.tool reports/nar_resource_freeze_v1/unified_scope_summary_latest.json >/tmp/unified_scope_summary_check
```

If any paper becomes accepted, run accepted sample audit for the accepted subset before counting it as public-v1 publication-grade.

## Status Vocabulary

`analysis_rework_from_existing_material`
: Existing packet tables/locators/database rows support owner-worker repair. Example: entity-target alignment from supplementary tables.

`mixed_analysis_rework_plus_controlled_digitization_gap`
: Analysis repair can proceed, but figure-only exact values remain unresolved unless controlled digitization is later attached.

`controlled_digitization_possible_but_requires_human_calibration`
: Image assets exist and a figure/curve/bar plot is the remaining target. No exact value is promoted until calibrated digitization plus independent QA is recorded.

`not_digitizable_missing_source_data`
: The unresolved field requires missing source data, sequence table, or authoritative exact material. Keep as source gap.

`manual_digitization_task_packaging_only_no_publication_grade_change`
: Output is a task/evidence packet only; no acceptance state changed.

## 2026-06-21 Ten-Paper Split

The 10-paper manual/digitization cohort was split as follows after task packaging:

- 1 `analysis_rework_from_existing_material`: `doi__10.1038_s42003-022-03899-4`
- 2 `mixed_analysis_rework_plus_controlled_digitization_gap`: `doi__10.1021_acsomega.8b01876`, `doi__10.3390_antibiotics11081080`
- 4 `controlled_digitization_possible_but_requires_human_calibration`: `doi__10.1002_cbic.202100609`, `doi__10.1016_j.virol.2010.11.014`, `doi__10.1128_mbio.01935-20`, `doi__10.1186_s12866-016-0799-z`
- 3 `not_digitizable_missing_source_data`: `doi__10.1038_s41467-024-51933-2`, `doi__10.1128_spectrum.02013-21`, `doi__10.3390_pharmaceutics14040693`

Release-facing `audit_material_digitization_backlog.py` then split the overall 31-paper backlog into:

- 3 `analysis_rework_candidate_not_auto_queued`
- 4 `manual_digitization_candidate`
- 1 `source_staging_candidate`
- 23 `still_unrecoverable_backlog`

## Stop Conditions

Stop processing a paper and move on when any of these are true:

- Max rework attempts are exhausted.
- The blocker is missing source data/sequence/table material and no local source exists.
- Figure-only exact values cannot be calibrated with a controlled method and QA.
- Worker-6 keeps non-empty hard `rework_targets`.
- Semantic or publication-quality gates fail without a new source-backed repair.

Do not loop indefinitely on the same paper. The scientifically honest outcome is to preserve a conflict or unresolved state with a named blocker.
