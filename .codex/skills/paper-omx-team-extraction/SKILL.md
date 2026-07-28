---
name: paper-omx-team-extraction
description: Run, recover, monitor, or audit OMX paper teams with source-backed quality gates. Batch 2-Team mode requires gpt-5.5 xhigh, per-paper source-reviewed publication-grade three-layer curation, and semantic QA beyond deterministic rescue or final_ready.
---

# Paper OMX Team Extraction

Use this skill for the repo-local paper extraction system under `workspace-guide/team-paper-sample/`.

Prefer this skill when the task is any of:

- launch or monitor `omx team` extraction for one paper
- run or resume a batch controller loop
- inspect why a paper team is stalled, blocked, or drifted
- recover a paper by re-running a specific worker lane with `paper_worker_v1.py run-role`
- verify `final/` artifacts against the repo's quality gate
- summarize recurring extraction failures for later fixes

If the task is only one worker lane, prefer the narrower worker skills:

- `$paper-intake-worker`
- `$paper-body-table-worker`
- `$paper-supp-evidence-worker`
- `$paper-merge-review-worker`
- `$paper-database-record-auditor`
- `$paper-mechanism-ontology-worker`
- `$paper-adjudicator-review-worker`

## Batch 2-Team publication-grade mode

- Use `gpt-5.5` with `reasoning_effort=xhigh` whenever model routing is under agent control. For native subagents use `model="gpt-5.5"` and `reasoning_effort="xhigh"`; for OMX worker launch args use equivalent `--model gpt-5.5 --reasoning-effort xhigh` when supported.
- `paper_worker_v1.py run-role` is a schema scaffold/rescue only. It must be followed by paper-local source review and corrected outputs before terminal acceptance.
- Do not accept accelerator auto-close, deterministic bootstrap, fallback materialization, `batch_sample_completed`, or `final_ready` as publication-grade completion.
- For AMP three-layer teams, pair controller validation with the semantic publication checker in `$paper-batch-orchestrator`.
- In split production mode, launch durable material extraction and analysis/adjudication as separate `$team` / `omx team ...` queues connected by `../amp-three-layer-curation/references/two-queue-paper-packet-contract.md`.
- Use `$ralph` / `omx ralph ...` only as a separate persistence supervisor over the manifest and tickets; do not use the removed `omx team ralph` form.
- Every paper must reach deep retrieval, deep acquisition, and reliable-result
  adjudication before it is counted as source-reviewed complete. Packet checks,
  copied legacy finals, or `analysis_accepted` strings are not enough.


## Quick start

Work from repo root:

```bash
cd /root/work/抗菌肽/数据库
```

Most common legacy paper-audit commands:

```bash
python workspace-guide/team-paper-sample/launch_paper_team_v2.py --paper-id <PMC...> --source-pool-root <source_pool_root>
python workspace-guide/team-paper-sample/paper_batch_v1.py manifest --limit 10 --output <manifest.json>
python workspace-guide/team-paper-sample/paper_batch_controller.py once --manifest <manifest.json> --issues <issues.jsonl>
python workspace-guide/team-paper-sample/paper_batch_controller.py loop --manifest <manifest.json> --issues <issues.jsonl> --interval-seconds 15
omx team status audit-real-paper-<pmcid-lower>-w --json
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-1|worker-2|worker-3|worker-4
```

For AMP three-layer curation over landed APD6/DBAASP/DRAMP literature, use the six-worker protocol:

```bash
python workspace-guide/team-paper-sample/launch_paper_team_v2.py \
  --paper-id <landed-paper-folder-or-PMCID> \
  --source-pool-root /mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers \
  --protocol amp_three_layer_v2
```

Load these references only as needed:

- `references/commands.md` for launch/monitor/recovery commands
- `references/quality-and-recovery.md` for quality gates, common failures, and rescue rules
- `references/troubleshooting-by-symptom.md` for symptom -> command -> recovery lookup
- `../amp-three-layer-curation/references/two-queue-paper-packet-contract.md` for packet layout, OCR/archive use, split queue boundaries, and rework-ticket routing

## Workflow

### 1. Choose the operating mode

Use the lightest lane that fits:

- **One paper, fresh run**: launch a single team with `launch_paper_team_v2.py`
- **Batch progression**: build or reuse a manifest, then run controller `once` or `loop`
- **Material queue**: run packet extraction over many papers; stop each paper at `material_extracted_complete`, `material_extracted_with_gaps`, or `material_blocked_missing_source`
- **Analysis queue**: consume ready packets and write final database/activity/mechanism/adjudication outputs
- **Stalled or noisy team**: inspect team status, task files, mailbox, and real artifact freshness before trusting tmux idle/stalled nudges
- **Worker-specific rescue**: re-run the exact worker lane with `paper_worker_v1.py run-role`
- **Post-run verification**: validate final artifacts and quality issues before declaring success

### 2. Respect the fixed role matrix

For legacy `paper_audit_v1`, keep the fixed four-lane contract:

- `worker-1` -> intake -> writes `work/intake/` and `final/materials_manifest.json`
- `worker-2` -> body/table evidence -> writes `work/body_evidence/` and `work/table_evidence/`
- `worker-3` -> supplementary evidence -> writes `work/supp_evidence/`
- `worker-4` -> merge/review -> writes `work/mechanism_merge/`, `work/formal_mapping/`, `work/review/`, and `final/`

Do not blur these write boundaries when rescuing a paper.

For `amp_three_layer_v2`, use the six-lane contract:

- material queue: `worker-1` -> `intake_linkage`
- material queue: `worker-2` -> `main_text_assay_extractor`
- material queue: `worker-3` -> `supplementary_methods_extractor`
- analysis queue: `worker-4` -> `database_record_auditor`
- analysis queue: `worker-5` -> `mechanism_ontology_extractor`
- analysis queue: `worker-6` -> `adjudicator_review`

Workers 1-5 write layer-specific `work/` artifacts; worker-6 owns final adjudicated JSON outputs and targeted rework.

In two-queue mode, workers 1-3 prepare packet materials and candidate evidence surfaces; they do not make final scientific acceptance decisions. Workers 4-6 consume packet evidence and write analysis/adjudication outputs. If workers 4-6 need missing material, they must write a structured rework ticket instead of searching unrelated folders or guessing.

For strict production runs, assign workers 4-6 enough scope to inspect each
paper's packet sources and database rows, not just to run batch-wide check
scripts. Existing `analysis/` or `final/` files are prior evidence until a
worker records paper-specific source-review provenance.

### 3. Trust repo-local evidence over noisy runtime hints

When tmux or OMX says a worker is stalled, verify in this order:

1. `omx team status <team> --json`
2. `tasks/task-1.json` through `tasks/task-4.json`
3. worker mailbox messages under `.omx/state/team/<team>/mailbox/`
4. actual paper artifacts under `papers/<paper_id>/work/` and `papers/<paper_id>/final/`

Treat old tmux injections as advisory only.

### 4. Use deterministic role-runner rescue deliberately

Use `paper_worker_v1.py run-role` when a worker lane is the blocker and you need stable repo-local outputs.

Typical rescue pattern:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-2
python workspace-guide/team-paper-sample/paper_batch_controller.py once --manifest <manifest.json> --issues <issues.jsonl>
```

Use the smallest rescue that unblocks the current paper. Do not rerun the whole batch when one worker lane is enough.

### 5. Enforce source-backed quality, not file-count theater

Do not treat generated files alone as success.

Require all of:

- final JSON files exist and parse
- `final_artifacts_structurally_ready(...) == True`
- `final_artifacts_quality_issues(...) == []`
- no blocking review findings such as `worker_deterministic_generated`
- supplementary outputs match staged source materials

## Non-negotiable rules

- Prefer original paper-local source materials over summaries and stale cache.
- Do not accept controller fallback, deterministic worker output, or accelerator closure as final unless later source-reviewed, semantically checked, and normalized.
- Do not force `worker-4` when task 1/2/3 artifacts are not accepted yet.
- Do not call a team stalled until status, task files, mailbox, and artifacts agree.
- Prefer `paper_batch_controller.py once` to let the controller reconcile state after a repair.
- When summarizing incidents, cite the runbook, checklist, incidents doc, and batch issue log rather than memory alone.
- Do not let analysis queues depend on implicit paper folders; require a packet manifest or explicit compatibility mapping.
- Do not close analysis queues from `check_two_queue_packets.py`,
  `--allow-findings`, `--allow-risk`, or `|| true` diagnostics. Close as
  accepted only after paper-by-paper source review, semantic pass, publication
  QA pass, and worker-6 adjudication.

## References to consult

- Stable workflow overview: `workspace-guide/team-paper-sample/README.md`
- Operator runbook: `workspace-guide/team-paper-sample/HOME_DL_RUNBOOK_V1.md`
- Strict processing and quality rules: `workspace-guide/team-paper-sample/BATCH_PAPER_PROCESSING_RUNBOOK_ZH.md`
- Known incidents: `workspace-guide/team-paper-sample/HOME_DL_INCIDENTS_V1.md`
- Stabilization backlog: `workspace-guide/team-paper-sample/STABILITY_REMEDIATION_CHECKLIST.md`
- Local issue summary: `workspace-guide/team-paper-sample/extraction-issues-20260423/README.md`

## Three-Layer AMP Curation Mode

If the user mentions merged APD6/DBAASP/DRAMP records, database-record verification, evidence ladders, mechanism ontology, or the three-layer audit, also use `$amp-three-layer-curation`.

When the user asks for durable queues, run the material queue and analysis queue as separate OMX teams. Keep one manifest-level status view that shows packet material status, analysis status, and open rework tickets. Ralph may supervise this status view until no papers remain pending or in progress.

Three-layer mode uses the fixed six-lane protocol:

- material queue worker-1 maps database/literature/source assets and preserves database provenance in the packet.
- material queue worker-2 extracts main-text/table source surfaces and candidate row-level activity/toxicity evidence with locators.
- material queue worker-3 extracts evidence-critical supplementary identity/activity/toxicity/mechanism details, including OCR/archive recovery attempts.
- analysis queue worker-4 audits database record identity and cross-database conflicts.
- analysis queue worker-5 builds mechanism evidence ontology.
- analysis queue worker-6 adjudicates conflicts, sends targeted rework, and writes final database/activity/mechanism/review outputs.

Use the merged corpus roots in WSL when available:

```text
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers
```

Do not run a paper-only conclusion-preservation workflow when the task is asking whether a database record itself is correct.

`landed_assets` is mutable: the user may add new papers later, so refresh `manifests/summary.json` and `manifests/landed_sources.csv` before choosing or summarizing a batch.
