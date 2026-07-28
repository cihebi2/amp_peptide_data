---
name: paper-batch-orchestrator
description: Build manifests, run controllers, and audit batches for source-reviewed publication-grade paper/AMP curation. Batch 2-Team mode requires gpt-5.5 xhigh, semantic QA beyond final_ready, and no terminal acceptance from accelerator or fallback output alone.
---

# Paper Batch Orchestrator

Use this skill for batch-wide control of the paper extraction system under `workspace-guide/team-paper-sample/`.

Prefer this skill when the task is any of:

- create or update a batch manifest
- start, resume, or inspect a controller `once` / `loop` run
- decide which papers are complete, blocked, or reopened across a batch
- reconcile repeated quality-gate failures or issue-log patterns
- produce a batch progress summary or audit for many papers at once

If the task is only one paper or one worker lane, prefer `$paper-omx-team-extraction` or the narrower worker skills.

## Batch 2-Team publication-grade mode

- Use `gpt-5.5` with `reasoning_effort=xhigh` for model-routed workers/subagents. When using OMX launch args and supported by the runtime, use `--model gpt-5.5 --reasoning-effort xhigh`.
- Build manifests from real eligible source-pool counts; do not pad batches to a requested size.
- Do not treat `batch_sample_completed`, `final_ready`, or accelerator/controller auto-close as terminal scientific acceptance.
- Any issue-log `accelerator auto-closed`, deterministic bootstrap, fallback materialization, schema scaffold output, or templated worker-6 review requires semantic QA plus paper-level source-reviewed repair before publication-grade claims.
- For split production runs, keep the material extraction queue and analysis/adjudication queue as separate OMX teams connected by the paper-packet contract in `../amp-three-layer-curation/references/two-queue-paper-packet-contract.md`.
- Use `$ralph` / `omx ralph ...` as a separate supervisor only when the manifest must persist until every packet is accepted, cautioned, or durably blocked; do not use the removed `omx team ralph` form.
- Production batch contexts must require per-paper deep retrieval, deep
  acquisition, and reliable-result adjudication. A context that only tells the
  analysis queue to copy existing finals, run packet checks, or summarize
  semantic failures is a diagnostic handoff, not an acceptance run.
- `--allow-findings`, `--allow-risk`, and `|| true` are allowed only in
  diagnostic commands whose outputs keep the paper nonterminal. They must not be
  used in the terminal completion path for strict production runs.
- For AMP three-layer batches, run the publication QA checker after validator success:

```bash
python batch/2-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py \
  --manifest <manifest.json> \
  --issues <issues.jsonl>
python batch/2-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py \
  --manifest <manifest.json>
```


## Quick start

Common batch commands:

```bash
python workspace-guide/team-paper-sample/paper_batch_v1.py manifest --limit 10 --output workspace-guide/team-paper-sample/batch-v1/<manifest>.json
python workspace-guide/team-paper-sample/paper_batch_controller.py once --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
python workspace-guide/team-paper-sample/paper_batch_controller.py loop --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl --interval-seconds 15
python workspace-guide/team-paper-sample/aggregate_batch_results.py --help
python workspace-guide/team-paper-sample/quality_audit_batch.py --help
```

Helpful repo-local helper scripts in this skill:

```bash
python .codex/skills/paper-batch-orchestrator/scripts/verify_batch.py --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json
python .codex/skills/paper-batch-orchestrator/scripts/check_locator_coverage.py --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json
python .codex/skills/paper-batch-orchestrator/scripts/summarize_issue_log.py --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
python .codex/skills/paper-batch-orchestrator/scripts/build_two_queue_packets.py --manifest <manifest.json> --packet-root <packet-root> --limit 5
python .codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py --packet-root <packet-root> --manifest <manifest.json>
python batch/2-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py --manifest <manifest.json> --issues <issues.jsonl>
python batch/2-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py --manifest <manifest.json>
```

Read these references as needed:

- `references/batch-commands.md` for manifest/controller/monitoring commands
- `references/batch-triage.md` for deciding whether a batch needs rescue, rerun, or just reconciliation
- `references/full-recovery-playbook.md` for the real recovery ladder used in long-running batches
- `references/low-level-team-rescue.md` for rare `team_api_json.py` control-plane interventions
- `../amp-three-layer-curation/references/two-queue-paper-packet-contract.md` for split material/analysis queue operation, packet layout, OCR/archive requirements, and rework tickets

## Workflow

### 1. Establish the batch contract

Before touching runtime, identify:

- manifest path
- issues log path
- source pool root
- whether the batch is strict worker review or a looser recovery lane
- whether the current run is a material queue, analysis queue, or Ralph-supervised manifest run
- packet root and rework ticket paths when the run is split

Keep every summary tied to a concrete manifest and issues log.

### 1.5. Keep split queues explicit

In two-queue mode, report and monitor these counts separately:

- material queued, extracting, extracted complete, extracted with gaps, blocked missing source.
- analysis queued, running, needs material rework, needs analysis rework, accepted with cautions, accepted, blocked.
- open rework tickets by `target_queue` and `severity`.

The material queue may keep advancing to the next paper after a packet is complete or complete-with-gaps. The analysis queue consumes only packets with enough locator-backed material for the requested analysis; otherwise it writes a structured rework ticket and moves to another ready packet.

Do not collapse these counts into a single `completed/100`. Report at least:

- packet material surfaces ready.
- analysis artifacts present from prior/copy paths.
- source-reviewed adjudication complete.
- semantic gate pass.
- publication-grade pass.

### 2. Prefer controller reconciliation over ad hoc mass intervention

For batch work, the normal rhythm is:

1. inspect manifest + issue log
2. run controller `once`
3. inspect the changed state
4. repeat only if evidence shows more reconciliation is needed

Do not restart the whole batch just because one or two papers reopened.

### 3. Separate batch-level diagnosis from paper-level rescue

At batch level, answer these first:

- how many papers are complete?
- how many have active teams?
- how many are blocked by quality gate?
- which issue types are repeating?
- is the batch failing because of one paper, one worker lane, or one systemic pattern?

Only drop to a paper-level rescue after that classification.

### 4. Trust fresh local evidence

When producing batch health statements, ground them in:

- current manifest contents
- current issue log rows
- current final artifact validation results
- current team sessions or `.omx/state/team/` state

Do not rely on old monitor rows if a stale background process may have appended them.

### 5. End every batch pass with an explicit status statement

State one of:

- batch complete
- batch progressing normally
- batch blocked by specific papers
- batch blocked by systemic runtime issue

Include the exact manifest and issue log you used.

## Non-negotiable rules

- Do not report batch completion without fresh validation over the current manifest.
- Do not reopen a paper unless fresh local validation actually fails.
- Prefer issue-log evidence and validator output over stale tmux injections.
- When many papers share the same failure, document the pattern instead of repeating one-off rescues blindly.
- Keep batch summaries reproducible: include file paths and counts.

## References to consult

- `workspace-guide/team-paper-sample/README.md`
- `workspace-guide/team-paper-sample/HOME_DL_RUNBOOK_V1.md`
- `workspace-guide/team-paper-sample/BATCH_PAPER_PROCESSING_RUNBOOK_ZH.md`
- `workspace-guide/team-paper-sample/extraction-issues-20260423/README.md`
- `workspace-guide/team-paper-sample/batch-v1/`

## Scripts in this skill

- `scripts/verify_batch.py` -> fresh manifest-wide ready/problem summary
- `scripts/check_locator_coverage.py` -> body/final locator coverage summary
- `scripts/summarize_issue_log.py` -> issue-type counts, example papers, example messages
- `scripts/build_two_queue_packets.py` -> build per-paper packet directories from staged XML/PDF/supplement/database artifacts for a material-queue pilot
- `scripts/check_two_queue_packets.py` -> summarize packet material status, analysis status, locators, database snapshots, and open rework tickets
- `scripts/check_three_layer_publication_quality.py` -> strict semantic/provenance QA for `amp_three_layer_v2` outputs
- `scripts/semantic_three_layer_gate.py` -> publication-grade hard gate for review provenance, material exhaustion, source locators, activity rows, supplementary extraction, and mechanism claims

For strict production runs, treat `build_two_queue_packets.py` and
`check_two_queue_packets.py` as structural packet tools only. They may prove that
materials and prior artifacts are assembled, but they do not prove that each
paper has been deeply reviewed or accepted.

## Three-Layer AMP Curation Batch Mode

If a batch task targets merged APD6/DBAASP/DRAMP records, evidence ladders, cross-database conflicts, or mechanism ontology, also use `$amp-three-layer-curation`.

For durable production, prefer two OMX team queues plus optional Ralph supervision:

- **Material team**: builds `paper_packets/<paper_id>/` or mapped `papers/<paper_id>/packet/` directories with raw assets, extracted source surfaces, locators, database-row snapshots, extraction status, and extraction errors.
- **Analysis team**: consumes packet directories to produce database record audits, activity/toxicity evidence, mechanism ontology, adjudication reports, and final conclusions.
- **Ralph supervisor**: tracks manifest-level completion, open tickets, team status, and semantic gates until all papers are accepted, accepted with cautions, or blocked with a durable ticket.

Do not launch analysis work against an implicit pile of files. It must have a packet manifest or an explicit compatibility mapping from the legacy `papers/<paper_id>/source/`, `work/`, and `final/` layout.

Batch-level contract in three-layer mode:

- Build manifests from database/literature links, not only PMC paper folders.
- Keep each summary tied to both a paper/source manifest and a database-record manifest.
- Keep material-extraction status separate from analysis/adjudication status.
- Treat rework ticket counts as first-class batch state.
- Report counts for layer-1 statuses: `source_verified`, `source_conflict`, `database_only_no_primary_source`, `sequence_modified_not_normalized`, `unresolved_record`.
- Report layer-2 evidence ladder coverage and missing row-level fields.
- Report layer-3 mechanism evidence classes and direct assay types.
- Treat cross-database conflict counts as first-class batch outcomes, not as noise.

Publication-grade batch acceptance must report four separate states: structural readiness, validator-contract readiness, semantic-gate pass, and paper-level source-reviewed acceptance. Only the last may be described as human-level or publication-grade.

Do not close a three-layer batch as publication-grade while any paper has templated review summaries, missing review timestamps/model provenance, suspicious target species strings, generic activity endpoints, MIC-like rows without units or explicit rationale, mechanism claims without IDs/text, or unresolved fallback/accelerator provenance.

Do not close an analysis/adjudication queue as accepted while those issues
remain either. The queue may close only as `diagnostic_handoff_complete`,
`needs_targeted_rework`, or `blocked_with_tickets` unless every selected paper
has paper-specific worker-6 review provenance and passes the semantic and
publication-quality gates.

Use the versioned six-worker launcher for pilot papers:

```bash
python workspace-guide/team-paper-sample/launch_paper_team_v2.py \
  --paper-id <landed-paper-folder-or-PMCID> \
  --source-pool-root /mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers \
  --protocol amp_three_layer_v2
```

The six roles are `intake_linkage`, `main_text_assay_extractor`, `supplementary_methods_extractor`, `database_record_auditor`, `mechanism_ontology_extractor`, and `adjudicator_review`. The legacy four-worker controller remains available for paper-only conclusion-preservation batches.

Relevant merged corpus roots in WSL:

```text
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers
```

Do not claim database-level completion from `final_ready_count` alone; paper final readiness proves paper extraction, not database-record verification.

`landed_assets` is mutable: the user may add new papers later, so refresh `manifests/summary.json` and `manifests/landed_sources.csv` before choosing or summarizing a batch.
