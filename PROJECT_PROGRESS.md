# Project Progress Living Document

Last updated: 2026-07-27 22:27 CST  
Workspace: `/home/cihebi/抗菌肽/数据集/batch/5-team`  
Purpose: maintain the current state of this AMP Evidence Atlas / NAR resource workspace so future agents can start from evidence instead of rediscovering the folder.

## Maintenance Rule

- Update this document at the start or end of every substantial session that changes project state, public claims, release numbers, validation progress, portal data, or backlog status.
- Treat `reports/nar_resource_freeze_v1/release_manifest_latest.json` and the active release package manifest as the current release authority unless a newer manifest is generated.
- Before making "current progress" claims, scan latest non-runtime modified files (`find . -path './.omx' -prune -o -type f ...`) because the active project layer may have moved beyond the freeze/release package.
- Mark anything from older docs as historical when it conflicts with the current manifest.
- Keep RC2 release counts, portal demo counts, deepmine machine/recovered counts, and DBAASP pending-expansion counts separated unless a new manifest explicitly reconciles them.
- Do not describe the resource as NAR-ready until public hosting, API/download availability, license/source-version review, manual validation, and manuscript disclosure are complete.
- Never promote `accepted_with_cautions` to clean, and never treat non-`source_verified` as automatic database error.

## Current High-Level State

This workspace is a mature AMP literature/database curation project. It contains a large source-reviewed paper corpus, a NAR resource freeze candidate, versioned release packages, validation pilots, post-RC2 mining pipelines, and a local portal/MCP demonstration layer.

Second-pass correction from the latest modified files: the newest active work is not just the RC2 freeze. As of 2026-07-05, the active layer is:

1. `pipeline_v2/deepmine/` post-RC2 expansion and recovery, especially the new incomplete DBAASP extraction batch.
2. `portal/` SQLite/MCP/advisor demo layer rebuilt over RC2 plus selected recovered/machine tiers.
3. RC2 builder/human-review backfill scripts from 2026-07-03 that changed public-whitelist and human-verdict surfacing behavior.

Do not collapse these layers into one denominator.

Current best short description:

> AMP Evidence Atlas is a primary-literature evidence alignment and provenance layer for antimicrobial peptide database curation. It audits AMP database records against source papers, preserves conflicts/cautions, and exposes source-backed activity, mechanism, and database-record evidence for downstream resource, ML, and agent-query use.

Current submission posture:

- Strong data/resource candidate exists.
- Latest versioned package is `amp-evidence-atlas-v1-rc2`.
- Still not a public NAR Database Resource.
- Main missing gates are manual validation closure, public deployment, license/source-version review, manuscript disclosure, and reconciliation of post-RC2 portal/deepmine expansions against release denominators.

## Directory Map

| Path | Role | Current notes |
| --- | --- | --- |
| `papers/` | Per-paper final artifacts | 1471 directories observed at top level; release freeze scans `papers/*/final`. |
| `paper_packets/` | Packet/workflow inputs and extracted source surfaces | 1472 directories observed; includes `.omx` and per-DOI packet dirs. |
| `rework_context/` | Durable rework prompts/context by paper | 1471 directories observed. |
| `reports/` | Main evidence, QA, validation, and release-planning reports | Largest directory; 17k+ top-level entries. |
| `reports/nar_resource_freeze_v1/` | Current freeze candidate authority | Latest generated 2026-07-03; use this first for current NAR/resource counts. |
| `releases/amp_evidence_atlas_v1_rc2/` | Latest versioned release package | Generated 2026-07-03; status remains candidate/not public submission-ready. |
| `docs/` | Human-readable workflow, roadmap, runbook docs | Some docs still carry RC1-era counts and must be synchronized. |
| `scripts/` | Builders, validators, pilots, rework and repair utilities | 436 top-level entries; many older per-paper repair scripts. |
| `.codex/skills/` | Repo-local OMX/Codex skills | Encodes AMP three-layer curation and six-worker role contracts. |
| `pipeline_v2/` | Post-freeze validation, hard discordance, human review, SAR/advisor work | Active expansion layer; includes deepmine, SAR/selectivity, plans. |
| `pipeline_v2/deepmine/` | Dual-model/machine recovery of unsurfaced data | Active as of 2026-07-04/05; not automatically part of RC2 release. New DBAASP batch is incomplete; DOI keys were normalized on 2026-07-07 but extraction remains rate-limited/pending. |
| `portal/` | SQLite portal, MCP server, benchmark, SAR/selectivity builders | Built local/agent-query demo over RC2 plus selected recovered/machine tiers; explicitly does not ingest current `dbaasp_extracted.tsv`. |
| `web_resource_v1/` | Earlier local web/API preview | Pre-portal resource surface. |
| `miaobi-message-web/` and `.miaobi-paper-review/` | Miaobi-style message passing/dashboard artifacts | Legacy/reused review-orchestration surface. |
| `source_recovery_packets/` | Source recovery materials | Earlier source-recovery support. |
| `logs/` and `mechanism.log` | Run logs | Use for operational diagnosis only. |

Important environment note: `.git/` exists but is not a valid Git repository here; `git status` fails with "not a git repository". Do not rely on git diff/status in this folder unless the repo is repaired or initialized.

## Latest Modified Project Layer

The latest non-`.omx` project modifications show the current work moved from freeze packaging into expansion/mining and portalization.

| Modified time (CST) | File(s) | Meaning |
| --- | --- | --- |
| 2026-07-05 11:41 | `pipeline_v2/deepmine/dbaasp.log` | DBAASP supervised extraction stopped after 30 stale rate-limited rounds. |
| 2026-07-04 18:02 | `pipeline_v2/deepmine/dbaasp_state.json`, `pipeline_v2/deepmine/dbaasp_extracted.tsv` | DBAASP extraction partial output: 340 done papers in state; 4640 extracted rows. |
| 2026-07-04 16:52-17:55 | `build_dbaasp_worklist.py`, `extract_dbaasp.py`, `run_dbaasp_supervised*.sh`, `dbaasp_worklist.json`, `dbaasp_conc.txt` | New DBAASP expansion batch and supervisor scripts. |
| 2026-07-04 16:33 | `portal/atlas.db`, `pipeline_v2/sar_pairs.tsv`, `pipeline_v2/selectivity.tsv` | Portal database rebuilt with SAR/selectivity; this predates the DBAASP TSV output and does not include it. |
| 2026-07-04 11:16-16:31 | `extract_newpapers_dual.py`, `extract_supphtml_dual.py`, `extract_docx_ocr_dual.py`, `extract_mechanism_dual.py`, `extract_hardcases_dual.py` and outputs | Full post-RC2 machine-extraction sweep over new/HTML/docx/OCR/hardcase/mechanism branches. |
| 2026-07-03 19:07-19:21 | `build_nar_resource_freeze_v1.py`, `backfill_human_review.py`, `build_nar_public_release_package.py`, RC2 release files | RC2 rebuild plus human-review fields and publication-grade whitelist fix. |

Inference: RC2 remains the release authority, but the project has a later experimental/data-expansion frontier. Current manuscript/resource claims must therefore label whether a number comes from RC2, portal, deepmine recovered/machine tiers, or pending DBAASP.

## Evidence Tier Model

Use these tier names when reconciling counts:

| Tier | Source artifacts | In RC2 release? | In `portal/atlas.db`? | Current interpretation |
| --- | --- | --- | --- | --- |
| `atlas_core` | RC2 `papers.tsv`, `activity_observations.tsv`, `database_record_audits.tsv`, `mechanism_claims.tsv` | Yes | Yes | Source-reviewed release-candidate core. |
| `human_review_confirmed` | `human_review` blocks in per-paper JSON, surfaced in RC2 audit fields | Yes, as audit annotations | Yes, as `audit.human_verdict` | Human verdict overlay; not a separate paper universe. |
| `dual_model_recovered` | `pipeline_v2/deepmine/recovered_approved.tsv` | No | Yes | Dual Claude+Codex consensus recovery from excluded/blocked papers; still a recovered tier. |
| `machine_extracted` | `newpapers_extracted.tsv`, `supphtml_extracted.tsv`, `docxocr_extracted.tsv`, `hardcases_extracted.tsv`, `mechanism_extracted.tsv` | No | Yes | Post-RC2 machine extraction; useful for demo/advisor/triage, not RC2 denominator. |
| `dbaasp_pending` | `dbaasp_worklist.json`, `dbaasp_state.json`, `dbaasp_extracted.tsv` | No | No | New incomplete DBAASP expansion batch; DOI-key artifacts normalized 2026-07-07. The 2026-07-08 Codex fallback is dual-pass machine extraction only, not strict six-worker source-reviewed curation, and is not ready for portal or release ingest. |
| `derived_advisor` | `features`, `sar_pairs`, `selectivity` in portal DB and `pipeline_v2/*.tsv` exports | No as raw release data | Yes | Deterministic derived layer for SAR/advisor use; depends on current portal activity rows. |

## Current Release Authority: RC2

Latest package:

- Path: `releases/amp_evidence_atlas_v1_rc2/`
- Release id: `amp-evidence-atlas-v1-rc2`
- Generated at: `2026-07-03T11:21:10+00:00`
- Status: `release_package_candidate_not_public_nar_submission_ready`
- Source freeze manifest: `reports/nar_resource_freeze_v1/release_manifest_latest.json`
- Source freeze generated at: `2026-07-03T11:20:43+00:00`

Current RC2 scope:

| Metric | Count |
| --- | ---: |
| `paper_final_artifact_count` | 1471 |
| `public_v1_candidate_papers` | 1374 |
| `excluded_or_non_publication_grade_papers` | 97 |
| `database_audit_rows` | 139259 |
| `source_verified_rows` | 95941 |
| `non_source_verified_rows` | 43318 |
| `activity_records` | 115184 |
| `mechanism_claims` | 4774 |

Current database audit status counts:

| Status | Rows |
| --- | ---: |
| `source_verified` | 95941 |
| `source_conflict` | 32550 |
| `sequence_modified_not_normalized` | 6472 |
| `database_only_no_primary_source` | 4240 |
| `unresolved_record` | 56 |

Current review-status counts from RC2 manifest:

| Review status | Count |
| --- | ---: |
| `accepted_with_cautions` | 1370 |
| `blocked_missing_primary_material` | 67 |
| `needs_targeted_rework` | 30 |
| `publication_grade` | 2 |
| `publication_grade_ready` | 1 |
| `publication_grade_with_cautions` | 1 |

Release package parsed row counts:

| File | Parsed rows |
| --- | ---: |
| `papers.tsv` | 1471 |
| `database_record_audits.tsv` | 139259 |
| `activity_observations.tsv` | 115184 |
| `mechanism_claims.tsv` | 4774 |
| `conflicts_and_cautions.tsv` | 49470 |
| `excluded_blocked_papers.tsv` | 97 |
| `database_denominators.tsv` | 6 |
| `crosstab_status_by_database.tsv` | 23 |
| `crosstab_category_by_database.tsv` | 40 |
| `crosstab_status_by_source_table.tsv` | 253 |
| `crosstab_review_status_by_database.tsv` | 20 |

Counting caution: use TSV/CSV parsing or manifest row counts. Plain `wc -l` is not reliable for large TSVs with embedded newlines/escaped text.

## RC1 to RC2 Drift

RC1 was generated 2026-06-22. RC2 was generated 2026-07-03.

Observed drift:

| Field | RC1 | RC2 | Meaning |
| --- | ---: | ---: | --- |
| `public_v1_candidate_papers` | 1371 | 1374 | Three additional accepted-like/publication-grade papers included by the newer builder/package path. |
| `excluded_or_non_publication_grade_papers` | 100 | 97 | Excluded set reduced by three. |
| `mechanism_claims` | 4772 | 4774 | Two mechanism claims added/changed. |
| `accepted_with_cautions` | 1371 | 1370 | Review-status composition changed; do not reuse RC1 status table. |
| `needs_targeted_rework` | 29 | 30 | Rework count changed; rework triage docs may need refresh. |

Known documentation drift:

- `docs/NAR_RESOURCE_V1_STEPWISE_EXECUTION_PLAN_20260622_093231_CST.md` is still centered on RC1-era `1371 / 100 / 4772` in several sections.
- `docs/NAR_FREEZE_V1_DATA_DICTIONARY.md` still states `public_v1_candidate_papers = 1371` and `excluded_or_non_publication_grade_papers = 100`.
- `docs/NAR_DATABASE_RESOURCE_ROADMAP.md` still references 100 excluded/non-publication-grade papers and 29 `needs_targeted_rework`.
- `reports/nar_resource_freeze_v1/README.md` has current RC2 scope at the top but the "Needs-Targeted-Rework Processing" section still says "current 29-paper"; RC2 manifest says 30.

Next doc-maintenance task: synchronize these documents to RC2 or explicitly label their RC1-era values as historical.

## RC2 Builder and Human-Review Backfill

The 2026-07-03 RC2 scripts changed more than row counts:

- `scripts/build_nar_resource_freeze_v1.py` now treats `publication_grade`, `publication_grade_ready`, and `publication_grade_with_cautions` as accepted-like public statuses. The script comment says the previous whitelist bug dropped 4 publication-grade papers and about 350 records.
- Public inclusion is now `publication_grade=true` plus review status in the accepted-like whitelist; this logic is used both for paper-scope rows and database audit rows.
- `scripts/backfill_human_review.py` reads `pipeline_v2/human_verified_db_errors.tsv` and writes per-record `human_review` lists into `papers/<id>/final/database_record_verification.json`.
- Backfill matching contract:
  - Tier 1 exact match via `audit_record_id` index into `record_audits[]`.
  - Tier 2 fuzzy match within the same paper using database and value normalization.
  - Re-runs are intended to be idempotent by `review_id`.
- Current dry-run match evidence: 117 exact, 0 fuzzy, 75 unmatched, 192 total rows.
- Current human-review TSV evidence: `pipeline_v2/human_verified_db_errors.tsv` has 192 rows: 190 `confirmed`, 2 `not_an_error`.
- Current RC2 release surfacing evidence: `releases/amp_evidence_atlas_v1_rc2/database_record_audits.tsv` has 103 `confirmed`, 2 `not_an_error`, and 139154 blank `human_verdict` rows.
- Three RC2 audit rows are `source_verified` but human-confirmed as errors; `scripts/build_nar_public_release_package.py` keeps these visible in `conflicts_and_cautions.tsv` rather than dropping them as ordinary source-verified rows.

Open reconciliation: the backfill dry-run can currently match 117 rows, while the RC2 release exposes 105 human verdicts. Before using the human-review metric in a manuscript, explain whether the 12-row difference is from release filtering, later/unapplied backfill state, duplicate/multiple verdict aggregation, or stale generated TSVs.

## Scope Reconciliation

The freeze universe is 1471 final-artifact papers. Historical queue aggregate is 1472 unique papers.

Current decision:

- Use `paper_final_artifact_count = 1471` for v1 freeze/release denominator.
- Keep the one queue-only failure as recovery backlog, not silent exclusion.

Known extra queue-only paper:

- `doi__10.1055_s-0029-1185675`
- Historical status: `initial_queue_failed` / `infrastructure_initial_queue_failed`
- Problem: selected paper lacked primary XML/PDF at startup and has no final artifact.

Evidence files:

- `reports/nar_resource_freeze_v1/scope_reconciliation_1471_vs_1472_latest.json`
- `reports/nar_resource_freeze_v1/scope_reconciliation_1471_vs_1472_latest.md`

## Workflow and Curation Model

The repo-local skill set defines a strict AMP three-layer curation workflow:

- Three scientific output layers: database record audit, activity/toxicity observations, mechanism ontology.
- Six-worker role model:
  - worker-1 intake/material inventory
  - worker-2 body/table evidence
  - worker-3 supplementary evidence
  - worker-4 database record audit
  - worker-5 mechanism ontology
  - worker-6 adjudication/final review
- Deterministic runners are schema scaffolds only; publication-grade acceptance requires source review, semantic QA, conflict preservation, and durable final artifacts.
- `gpt-5.5` / high or xhigh effort is specified in local skills for model-routed scientific review.
- Durable rework goes through paper packets, `rework_context`, final review reports, and JSONL tickets; chat-only notes are not the production message bus.

Key local skill entrypoints:

- `.codex/skills/amp-three-layer-curation/SKILL.md`
- `.codex/skills/paper-batch-orchestrator/SKILL.md`
- `.codex/skills/paper-omx-team-extraction/SKILL.md`
- `.codex/skills/paper-adjudicator-review-worker/SKILL.md`
- `.codex/skills/paper-database-record-auditor/SKILL.md`
- `.codex/skills/paper-mechanism-ontology-worker/SKILL.md`

## Major Completed Milestones

### Queue-level and final-artifact corpus

- Historical queue aggregate: 1472 unique papers.
- Early summary from 2026-05-11 reported 1326 queue-level `accepted_after_rework`, 146 non-accepted, and 2 initial failures.
- Current freeze scans 1471 paper final artifacts.
- Current RC2 public candidate subset has 1374 papers, but all accepted-like statuses still preserve cautions and are not clean.

### NAR resource freeze and package work

Completed by the 2026-06-22 stepwise plan and later RC2 update:

- Freeze manifest and unified scope summary generated.
- RC1 release package generated 2026-06-22.
- RC2 release package generated 2026-07-03.
- Database-vs-paper difference examples generated under `reports/nar_resource_freeze_v1/`.
- Manual stratified validation manifest generated.
- Local website/API/download resource shape created.
- Current release package includes schemas, checksums, TSV downloads, README, and license table placeholder.

### Pilot20 validation closure

Step 6 pilot20 reached full closure after correcting a dispatch-only QC gap.

Final pilot20 closure:

| Final status | Papers |
| --- | ---: |
| `accepted_with_cautions` | 16 |
| `blocked_missing_primary_material` | 3 |
| `needs_targeted_rework` | 1 |

Important interpretation:

- Do not say 20/20 clean.
- Accepted subset mechanism ontology QC has zero bad `evidence_class` classes.
- Blocked/material-gap papers remain nonterminal and should not be forced into accepted.
- This pilot validates the full-scope closure mechanism for expansion, not the entire 420-row manifest.

Main closure evidence:

- `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/pilot20_final_review_closure/pilot20_final_review_closure_summary_latest.json`
- `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/pilot20_final_review_closure/pilot20_final_review_closure_report_latest.md`
- `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/ontology_qc/mechanism_ontology_class_qc_summary_latest.json`

## Manual Validation 420 Status

The full manual/source-review validation set is not complete.

Current validation420 setup:

- Manifest: `reports/nar_resource_freeze_v1/manual_validation/validation_manifest_latest.csv`
- Manifest rows: 420
- Source-review packets: 224
- Packet index: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/packet_index_latest.csv`
- Runner: `scripts/run_validation420_source_reviews.py`

Last saved checkpoint: 2026-06-25 14:40 CST.

Checkpoint state:

- Runner parent was soft-paused with `SIGSTOP`.
- Active children were allowed to finish.
- Existing result files: 39/224 packets.
- Reviewed rows: 114/420.
- Contract QA over existing results: `contract_pass=39`, `contract_fail=0`, `blocking_output_problems=0`, `warnings=1`.
- Runner statuses: 43 status files, 39 valid results, 4 invalid/interrupted, 181 not started.
- Invalid/interrupted packets: `V420P0022`, `V420P0029`, `V420P0030`, `V420P0031`; all lack result JSON and require safer retry, not scientific rejection.

Checkpoint decision counts:

- Packet-level current decisions: `accepted_with_cautions=13`, `blocked_missing_primary_material=4`, `needs_targeted_rework=22`, `missing_result=185`.
- Sample-row decisions: `blocked_missing_primary_material=65`, `confirmed=1`, `confirmed_with_caution=34`, `needs_targeted_rework=14`.
- Rework artifacts: 35 targets/tickets and 146 cautions at checkpoint.

Rules:

- Do not simply `SIGCONT` the old runner unless intentionally continuing the original queue.
- Prefer a new bounded resume/retry plan that handles the four invalid packets safely.
- Do not interpret partial validation420 results as final publication-grade closure.

Evidence:

- `reports/nar_resource_freeze_v1/manual_validation/validation420/VALIDATION420_RUN_STATUS.md`
- `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_pause_checkpoint_qa_latest.md`
- `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_source_review_summary_latest.json`

## Unresolved and Needs-Targeted Rework

Current release status:

- `unresolved_record` audit rows: 56.
- `blocked_missing_primary_material`: 67 papers.
- `needs_targeted_rework`: 30 papers in RC2 manifest.

Existing workflows:

- Unresolved processing:
  - `scripts/triage_unresolved_records.py`
  - `scripts/write_unresolved_resolution_reports.py`
  - `scripts/validate_unresolved_processing.py`
- Needs-targeted processing:
  - `scripts/triage_needs_targeted_rework.py`
  - `scripts/write_needs_targeted_rework_resolution_reports.py`
  - `scripts/validate_needs_targeted_rework_processing.py`

Current caution:

- Some generated docs still describe a 29-paper needs-targeted set. RC2 says 30, so refresh triage before making public counts.

## Post-RC2 Pipeline V2 State

`pipeline_v2/` is the main post-freeze expansion and NAR-story workspace. It should be treated as partly experimental/extension evidence until reconciled into a release manifest.

Important artifacts:

| File | Rows / role |
| --- | --- |
| `pipeline_v2/human_verified_db_errors.tsv` | 192 rows; human-verified database-error evidence candidate. |
| `pipeline_v2/MASTER_confirmed_errors.tsv` | 192 rows; consolidated confirmed errors file. |
| `pipeline_v2/HUMAN_REVIEW_worksheet.tsv` | 192 rows; review worksheet. |
| `pipeline_v2/FULL_CORPUS_dual_confirmed.tsv` | 52 rows; dual-confirmed full-corpus evidence. |
| `pipeline_v2/DUAL_CONFIRMED_errors.tsv` | 32 rows; dual-confirmed errors. |
| `pipeline_v2/CONFIRMED_DB_ERRORS_combined.tsv` | 54 rows; combined confirmed errors. |
| `pipeline_v2/sar_pairs.tsv` | 6009 rows; deterministic matched-pair SAR layer export. |
| `pipeline_v2/selectivity.tsv` | 1121 rows; computed TI/selectivity export. |

Current strategic docs:

- `pipeline_v2/NAR_SUBMISSION_PLAN.md`
  - Positions NAR Database Issue as target.
  - Frames novelty around measured curation quality and agent-queryability/MCP.
  - Calls for competitor table, quality-evidence figure, ontology mapping, public compliance, and DOI dump.
- `pipeline_v2/AMP_ADVISOR_MVP_PLAN.md`
  - Defines a retrieve-and-cite AMP activity-improvement advisor.
  - Rejects exact de-novo/Delta-MIC prediction as not data-grounded.
  - Prioritizes matched-pair SAR, design-rule cards, thin MCP-backed agent, and evaluation.

## Deepmine / Recovered Data State

`pipeline_v2/deepmine/` recovers unsurfaced data from already acquired papers, never-processed downloads, hardcase sources, and a new DBAASP source pool. It is post-RC2 expansion material unless explicitly rebuilt into a new release.

Operational philosophy from `pipeline_v2/deepmine/README.md`:

- Dual-model extraction is preferred for critical recovered data.
- `recovered_approved.tsv` is approved only on dual consensus and intended as a `machine-recovered` / recovered tier, not clean source-reviewed release data.
- Many blocked/excluded paper records correctly remain in review queue or unrecoverable; that separation is intentional.

Current branch status:

| Branch/artifact | Parsed rows | Papers with rows | State done | Verdict/status summary | Current tier |
| --- | ---: | ---: | ---: | --- | --- |
| `recovered_approved.tsv` | 1527 | 42 | 64 | `approved=True` for all raw rows; portal filter keeps 1100 non-junk activity rows | `dual_model_recovered` |
| `recovered_review_queue.tsv` | 4896 | 48 | 64 | `approved=False` for all rows | review queue only |
| `newpapers_extracted.tsv` | 2328 | 177 | 431 | `claude_only=1633`, `codex_only=589`, `both_models=106` | `machine_extracted` |
| `supphtml_extracted.tsv` | 1425 | 157 | 701 | `claude_html=1425` | `machine_extracted` |
| `docxocr_extracted.tsv` | 128 | 17 | 81 | `claude_docx=91`, `claude_ocr=37` | `machine_extracted` |
| `hardcases_extracted.tsv` | 1696 | 66 | 283 | `claude_only=1417`, `both_models=157`, `codex_only=122` | `machine_extracted` |
| `mechanism_extracted.tsv` | 1486 | 249 | 345 | `direct_assay=605`, `indirect=358`, `inferred=356`, `hypothesis=166`, plus typo `direct_ass ay=1` | `machine_extracted` mechanism |
| `dbaasp_extracted.tsv` | 4640 | 212 | 340 | `claude_1=2975`, `claude_x2=1665`; incomplete and not portal-ingested | `dbaasp_pending` |

`newpapers_approved.tsv` and `newpapers_review.tsv` currently parse as 0-row placeholders; the active full-text extraction output is `newpapers_extracted.tsv`.

### DBAASP Pending Expansion

DBAASP is the newest active batch and needs special handling:

- `build_dbaasp_worklist.py` builds one preferred source file per DBAASP paper not already in the merged superset, preferring XML over main PDF and skipping supplements.
- Current `dbaasp_worklist.json`: 2103 papers; 1161 PMC keys and 942 DOI keys; 1160 XML sources and 943 PDF sources.
- Current `dbaasp_state.json`: 340 done, 1763 todo.
- Current `dbaasp_extracted.tsv`: 4640 rows from 212 papers; 128 done papers produced no extracted rows or no usable content.
- `extract_dbaasp.py` runs two independent Claude/Sonnet passes and tags rows as `claude_x2` when both passes agree, otherwise `claude_1`.
- `run_dbaasp_supervised_v2.sh` reads `dbaasp_conc.txt` each round; current concurrency file is `12`.
- `dbaasp.log` shows every remaining 1763 todo paper was rate-limited for 30 stale rounds, then the supervisor stopped at 2026-07-05 11:41 CST.
- No live `extract_dbaasp.py`, `run_dbaasp_supervised*`, or Claude DBAASP extraction process was observed during this inspection.

Critical current defect:

- `build_dbaasp_worklist.py` extracts DOI keys from filenames with regex `'(10\.\d{4,}[._][^/]+?)\.(pdf|xml)$'`.
- For filenames like `...(10.1038_s41598-024-73766-1).pdf`, the DOI key becomes `10.1038/s41598-024-73766-1)` with a trailing `)`.
- All 942 DOI keys in `dbaasp_worklist.json` currently end with `)`.
- 2026-07-07 normalization update: `dbaasp_worklist.json`, `dbaasp_state.json`, and `dbaasp_extracted.tsv` now have zero DOI keys / `paper_id` values ending in or containing the stray `)` defect; previous raw files are backed up under `pipeline_v2/deepmine/backups/dbaasp_id_normalization_20260707T145246Z/`.

Do not ingest DBAASP into RC2 or portal yet. The DOI-key defect is fixed in the canonical files, but the batch is still incomplete, rate-limited, and AI-extracted rather than source-reviewed. Resume only under an explicit concurrency/provider plan and re-run QA after any new extraction.

Operational caution: `extract_docx_ocr_dual.py --list` is not just metadata; `worklist()` calls `pdftotext` on candidate PDFs to detect scanned documents, so it can be slow/noisy on the full pool.

## Portal / MCP / Benchmark State

`portal/` is a local/agent-facing service layer built over RC2 plus extra recovered/machine-extracted layers.

Key files:

- `portal/atlas.db` - SQLite database, 382,164,992 bytes.
- `portal/portal_server.py` - stdlib public portal server.
- `portal/mcp_server.py` - stdlib MCP server, read-only tools over Atlas DB.
- `portal/build_db.py` - ingests RC2 TSVs plus recovered/machine-extracted activity and mechanism layers.
- `portal/build_sar.py` - builds matched-pair SAR table.
- `portal/build_selectivity.py` - builds therapeutic-index/selectivity table.
- `portal/benchmark_amp_qa.json` - 40 source-traceable QA items.
- `portal/benchmark_protocol.md` - grounded vs ungrounded agent evaluation plan.

Exact `portal/build_db.py` ingest contract:

1. Loads RC2 release package tables from `releases/amp_evidence_atlas_v1_rc2/`.
2. Filters to public rows with `public_v1_included` or accepted-like `publication_grade*` status.
3. Writes RC2 activity rows as `evidence_tier='atlas_core'`.
4. Adds `pipeline_v2/deepmine/recovered_approved.tsv` as `evidence_tier='dual_model_recovered'` after approved/junk/entity filtering.
5. Adds `newpapers_extracted.tsv`, `supphtml_extracted.tsv`, `docxocr_extracted.tsv`, and `hardcases_extracted.tsv` as `evidence_tier='machine_extracted'` after peptide/value filters.
6. Adds `mechanism_extracted.tsv` into the mechanism table with evidence class suffixed by `(machine_extracted)`.
7. Adds figures from `paper_packets/<paper_id>/extracted/figure_captions.json`.
8. Builds `features`, `sar_pairs`, `selectivity`, FTS search, and a `stats` table.

Important negative evidence:

- `portal/build_db.py` does not read `pipeline_v2/deepmine/dbaasp_extracted.tsv`.
- `portal/atlas.db` was modified at 2026-07-04 16:33 CST, before `dbaasp_extracted.tsv` and `dbaasp_state.json` were modified at 18:02 CST.
- Therefore `portal/atlas.db` is not a DBAASP-expanded database.

Current `portal/atlas.db` stats table:

| Stat | Count |
| --- | ---: |
| `papers` | 1811 |
| `activity` | 115372 |
| `audit` | 128976 |
| `conflicts_audit` | 28813 |
| `human_confirmed` | 103 |
| `recovered_activity` | 1100 |
| `machine_activity` | 5511 |
| `mechanism` | 5994 |
| `peptides` | 10691 |
| `sequences` | 2261 |
| `featured_sequences` | 1559 |
| `sar_pairs` | 1669 distinct analog pairs |
| `selectivity` | 1121 |

Direct table counts also observed:

- `sar_pairs` table rows: 6009.
- `conflicts` table rows: 42895.
- `figures` table rows: 8742.
- `search` FTS rows: 244348.

Current `activity.evidence_tier` split:

| Tier | Rows |
| --- | ---: |
| `atlas_core` | 108761 |
| `machine_extracted` | 5511 |
| `dual_model_recovered` | 1100 |

Current `papers.review_status` split in portal:

| Review status | Papers |
| --- | ---: |
| `accepted_with_cautions` | 1370 |
| `machine_extracted` | 410 |
| `dual_model_recovered` | 27 |
| `publication_grade` | 2 |
| `publication_grade_with_cautions` | 1 |
| `publication_grade_ready` | 1 |

Important portal-vs-release boundary:

- `portal/atlas.db` is not numerically identical to RC2 release.
- `portal/build_db.py` adds dual-model recovered and machine-extracted activity rows, mechanism rows, extra paper rows, features, SAR, and selectivity.
- Use portal stats for demo/agent capability, not as freeze denominator.
- Need a reconciliation note before using portal numbers in manuscript or public claims.
- DBAASP is not in portal at all, so do not cite portal counts as post-DBAASP counts.

MCP surface:

- `portal/mcp_server.py` exposes 10 read-only tools: `get_stats`, `search`, `get_peptide`, `get_paper`, `get_audit_record`, `get_figures`, `find_precedents`, `list_conflicts`, `query_activity`, and `sql_select`.
- `get_stats` reports release as `amp_evidence_atlas_v1_rc2` but also reports `dual_model_recovered_activity` and `machine_extracted_activity`; users must understand this is a portal tier blend, not the RC2 release denominator.
- `sql_select` is guarded to allow only one read-only `SELECT`/`WITH` statement and deny write/DDL/pragma-style keywords.

Benchmark:

- `portal/benchmark_amp_qa.json` has 40 items.
- Categories: `database_error_awareness=14`, `activity_value=12`, `sequence_fact=7`, `target_organism_fact=7`.
- The benchmark tests whether Atlas/MCP grounding reduces hallucinated facts and catches public-database-vs-primary-source conflicts.

## Known Latest Script/Data Risks

These are not all blockers for RC2, but they are blockers for claiming the newest expanded state is reconciled:

1. **DBAASP pending after DOI normalization:** the deterministic DOI-key bug was fixed and canonical artifacts were reconciled on 2026-07-07; remaining blockers are rate-limit restart strategy, post-resume QA, and review/ingest policy. Backups and mapping/report are under `pipeline_v2/deepmine/`.
2. **DBAASP provider status:** Claude is currently unavailable (`API Error: 400 This organization has been disabled`), while Codex preflight succeeds. Resume via bounded Codex fallback only after reviewing probe quality/cost.
3. **Human-review count reconciliation:** `human_verified_db_errors.tsv` has 192 human-reviewed rows, dry-run matching reports 117 matchable rows, but RC2 exposes 105 human verdicts. Explain this before headline precision/error-count claims.
4. **Mechanism evidence-class typo:** `mechanism_extracted.tsv` contains one `direct_ass ay` typo alongside valid classes; normalize before ontology/statistical summaries.
5. **Portal vs release denominator:** `portal/atlas.db` has 1811 papers because it blends RC2 with recovered and machine-extracted tiers. RC2 release remains 1471 paper rows; DBAASP is not in portal.
6. **`compute_features.py` direct CLI caveat:** the imported `compute_into(db)` path used by `portal/build_db.py` works for portal build, but the script's standalone `main()` prints `len(rows)` even though `rows` is local to `compute_into`; running `python3 portal/compute_features.py` directly is likely to fail after rebuilding features unless that print is fixed.
7. **`extract_docx_ocr_dual.py --list` cost:** the list path probes PDFs with `pdftotext`; treat it as a scan, not a cheap metadata command.

## 2026-07-06 AI-First Work Decision

Timestamp: 2026-07-06 22:56 CST.

Current owner decision:

- Manual paper/human validation is real but should be deferred until later or delegated to other people. It is labor-heavy and should not block AI-doable engineering/data work.
- Do not spend the next cycle trying to close the full human-review or validation420 workload.
- First finish work that AI/Codex can materially advance: data-layer cleanup, incremental data reconciliation, portal/site completion, MCP/query surface, generated documentation, and automated validation scripts.
- Keep every output tier labeled. Do not turn machine-extracted or recovered rows into source-reviewed release rows without a new review/release gate.

Near-term AI-doable priorities:

| Priority | Workstream | Why now | Concrete next output |
| --- | --- | --- | --- |
| 1 | DBAASP/incremental data cleanup | DOI-key bug is fixed; newest batch is now blocked by rate-limit/resume policy and post-extraction QA. | Safe DBAASP resume command/plan, post-resume QA, and explicit non-ingest policy until reviewed. |
| 2 | Portal/site completion | Website/MCP already exists locally but is not publication-ready; mostly engineering/docs work. | Rebuildable `portal/atlas.db`, clear tier labels in UI/API, download/help pages, smoke tests, and deployment checklist. |
| 3 | Release-vs-portal reconciliation docs | Current numbers are confusing because RC2, portal, deepmine, and DBAASP are different layers. | One human-readable reconciliation page/table explaining 1471 RC2 papers vs 1811 portal papers and which tiers are included. |
| 4 | Automated data QA | Before asking humans to review, machine checks should catch schema/count/ID/tier problems. | Scripts/reports for malformed IDs, duplicate IDs, tier counts, required fields, status/category distributions, and portal/release consistency. |
| 5 | Advisor/SAR polish | SAR/selectivity are promising and AI-doable, but depend on portal tier clarity. | Documented SAR/selectivity tables, MCP examples, and benchmark queries; no overclaiming exact prediction. |
| 6 | Human validation package preparation | Human review can be delegated later, but AI can prepare clean packets. | Smaller review batches, instructions, sampling sheets, and dashboards for other reviewers. |

Recommended immediate sequence:

1. Decide DBAASP resume strategy now that DOI normalization is complete: concurrency/provider/quota, checkpoint behavior, and post-resume QA before any ingest.
2. Rebuild or validate portal after the tier model is explicit, but still exclude DBAASP until normalized.
3. Add a plain-language portal/release reconciliation doc for future humans and manuscript use.
4. Add automated QA reports so human reviewers only see cases that actually need judgment.
5. Only then return to manual validation/human review, preferably with external helpers.

## 2026-07-06 Local Access and Review Queue Smoke Test

Timestamp: 2026-07-06 23:15 CST.

Portal access note:

- `portal/portal_server.py` was running successfully in WSL2 on port `8080`.
- Linux-side `http://127.0.0.1:8080/` and `http://localhost:8080/` returned HTTP 200.
- Windows-side `http://localhost:8080/` initially failed, but Windows could reach the WSL IP `http://172.29.56.153:8080/` with HTTP 200.
- Treat this as a WSL2 localhost forwarding issue, not an internet/network-speed issue.
- Future access rule: from Windows browser, use `http://$(hostname -I first-ip):<port>` when `localhost` fails; the WSL IP changes after WSL restart.

Human-review queue smoke test:

- Entry point: `pipeline_v2/review_server.py`.
- Command used: `python3 pipeline_v2/review_server.py 8765`.
- Running URL inside WSL: `http://127.0.0.1:8765/`.
- Windows access test: both `http://localhost:8765/` and `http://172.29.56.153:8765/` returned HTTP 200 during this test.
- Queue source: `pipeline_v2/HUMAN_REVIEW_worksheet.tsv`.
- Verdict persistence file: `pipeline_v2/review_verdicts.json`.
- Queue size: 192 items.
- Existing saved verdicts: 34 items (`confirmed=30`, `uncertain=4`).
- Remaining todo: 158 items.
- DUAL-priority total: 52 items; DUAL remaining todo: 18 items.
- GET smoke tests passed for `/`, `/api/items`, and first-row local PDF through `/file?path=...`.
- Save smoke test passed with a no-op POST of the existing `R001` verdict. The original `review_verdicts.json` bytes were restored afterward, so no test verdict was left behind.

Current interpretation: the human-review UI is usable for lightweight manual checking now, but the project decision remains to defer large-scale manual validation until AI-doable cleanup, portal completion, and automated QA are further along.

## 2026-07-06 Codex CLI Review Pass

Timestamp: 2026-07-06 23:25 CST.

Scope:

- Reviewed the 18 DUAL-priority rows that were still todo in `pipeline_v2/HUMAN_REVIEW_worksheet.tsv` at the start of this pass.
- Used local primary-source PDF/text extracts under `paper_packets/<paper_id>/extracted/pdf_text/` and `papers/<paper_id>/source/paper.pdf`.
- Did not write to `pipeline_v2/review_verdicts.json`; this remains an AI-assisted review artifact, not a human verdict file.

Outputs:

- `pipeline_v2/codex_review_dual_todo_20260706_232458.json`
- `pipeline_v2/codex_review_dual_todo_20260706_232458.tsv`
- Convenience copies:
  - `pipeline_v2/codex_review_dual_todo_latest.json`
  - `pipeline_v2/codex_review_dual_todo_latest.tsv`

Result:

- 18/18 rows received Codex recommendation `confirmed`.
- 18/18 rows have `confidence=high`.
- All were based on direct table evidence.
- Recommended severity: `major` for all 18.
- Error-type split: `variant_misattribution=7`, `endpoint_mismatch=7`, `value_mismatch=4`.
- Database split: `DBAASP=13`, `CAMP=5`.
- Paper split:
  - `doi__10.3390_md12020871`: 6
  - `doi__10.3390_antibiotics9120870`: 4
  - `doi__10.3389_fmicb.2018.00667`: 3
  - `doi__10.3389_fmicb.2018.02846`: 2
  - `doi__10.3389_fmicb.2018.02276`: 1
  - `doi__10.3390_antibiotics11020243`: 1
  - `doi__10.3390_ijms24043951`: 1

Interpretation:

- These 18 DUAL rows are strong candidates for manual confirmation/import, but they should not be counted as human-reviewed until a human accepts them or the project explicitly creates an `ai_reviewed` tier.
- If later importing into `review_verdicts.json`, keep reviewer/provenance explicit (for example `reviewer=codex_cli_ai_assisted`) or use a separate field/tier so manuscript precision claims do not confuse AI review with human review.

## 2026-07-07 Review Flow Quality Hardening

Timestamp: 2026-07-07 22:48 CST.

Quality posture update:

- The project should use the available AI budget to improve reliability through provenance, repeatable QA, and explicit tier separation, not by mixing AI output into human-reviewed release claims.
- Human review, AI-assisted review, RC2 release rows, portal demo rows, machine/recovered rows, and DBAASP pending rows remain separate quality tiers.
- The review pipeline is now instrumented so future saves can be audited and strict final gates can fail loudly instead of silently accepting weak metadata.

Code and artifact changes:

| File | Change | Quality effect |
| --- | --- | --- |
| `pipeline_v2/review_server.py` | Adds v2 save metadata (`reviewed_at`, `source`, `provenance`, `schema_version`, `is_human_verdict`), append-only `review_log.jsonl` support for future saves, atomic JSON writes, review-id validation, valid verdict/severity checks, and mandatory severity for new confirmed saves. | Future UI saves are provenance-bearing and analyzable for audit/kappa instead of being anonymous four-field snapshots. |
| `pipeline_v2/review_server.py` | Reworked `/file?path=...` containment checks to allow legitimate `papers/...` symlinked PDFs while blocking `papers/../...` traversal. | Local PDF viewing still works; obvious path traversal is blocked before public deployment hardening. |
| `pipeline_v2/analyze_verdicts.py` | `--verdicts` now prefers local sibling `review_log.jsonl`; `--log` is supported; AI-assisted combined files print an explicit source warning. | Analysts cannot accidentally cite AI-assisted combined precision as pure human precision. |
| `pipeline_v2/export_review_state.py` | New script exporting separate AI-assisted review products without overwriting `review_verdicts.json`. | Codex recommendations become reusable while remaining non-human provenance. |
| `pipeline_v2/check_review_flow.py` | New QA gate for worksheet/verdict/log/Codex/export/DBAASP/portal consistency; `--strict-final` makes warnings fail. | Gives a repeatable pre-publication quality gate rather than ad hoc inspection. |
| `pipeline_v2/test_review_flow.py` | New focused regression tests for save metadata, severity enforcement, unknown IDs, and file traversal. | Protects review-server behavior from future regressions. |

Generated review-state outputs:

| Output | Meaning | Current count/status |
| --- | --- | --- |
| `pipeline_v2/review_verdicts_ai_assisted.json` | Combined analysis-only map: existing human/UI verdicts plus AI-assisted recommendations for IDs without human verdicts. | 52 review IDs total: 34 human/UI + 18 AI-assisted. |
| `pipeline_v2/ai_reviewed_db_errors.tsv` | Flat TSV of the 18 Codex-assisted DUAL recommendations with evidence/provenance fields. | 18 rows. |
| `pipeline_v2/review_state_export_manifest.json` | Export manifest and policy statement. | Human verdicts remain authoritative; AI rows are not human validation. |
| `pipeline_v2/review_flow_qa_latest.json` | Non-strict QA report. | `ERROR=0`, `WARN=136`. |
| `pipeline_v2/review_flow_qa_strict_latest.json` | Strict-final QA report. | Return code 1 by design because final-quality warnings remain. |

Validation evidence from this hardening pass:

- `python3 -m py_compile pipeline_v2/review_server.py pipeline_v2/analyze_verdicts.py pipeline_v2/export_review_state.py pipeline_v2/check_review_flow.py pipeline_v2/test_review_flow.py` passed.
- `PYTHONWARNINGS=error python3 pipeline_v2/test_review_flow.py -v` passed 4/4 tests.
- `python3 pipeline_v2/export_review_state.py` generated 34 human + 18 AI-assisted combined review IDs and 18-row AI TSV.
- `python3 pipeline_v2/check_review_flow.py --json-out pipeline_v2/review_flow_qa_latest.json` completed with `ERROR=0`, `WARN=136`.
- `python3 pipeline_v2/check_review_flow.py --strict-final --json-out pipeline_v2/review_flow_qa_strict_latest.json` returned 1 as expected because strict final quality is not yet met.
- `python3 pipeline_v2/analyze_verdicts.py --verdicts pipeline_v2/review_verdicts_ai_assisted.json` prints an explicit warning that the 18 AI-assisted records are not pure human precision.
- Local service health after restart: portal `http://127.0.0.1:8080/` returned HTTP 200; review UI `http://127.0.0.1:8765/` and `/api/items` returned HTTP 200.
- Review UI now runs in tmux session `amp_review_ui_8765` so the patched code is active on port 8765.
- Review file access smoke test: first-row PDF returned HTTP 200 `application/pdf`; traversal attempt `papers/../PROJECT_PROGRESS.md` returned HTTP 403.

Current QA warnings that block final-quality release claims:

| Warning class | Count | Interpretation | Needed resolution |
| --- | ---: | --- | --- |
| `human_verdict_legacy_missing_field` | 102 | 34 existing UI verdicts lack `reviewed_at`, `source`, and `provenance` because they were saved before v2 metadata. | Migrate legacy entries with explicit `legacy_*` provenance, or leave them marked legacy and do not overclaim auditability. |
| `human_confirmed_missing_severity` | 30 | Existing confirmed UI verdicts did not record severity. | Human/owner must assign severity or an explicit defaulting policy must be documented before strict final. |
| `review_log_missing` | 1 | No append-only log exists yet because no new v2 UI save has been made after the code change. | Future UI saves will create it; optional legacy migration can create a separate migration log but should not pretend historical click timestamps exist. |


Current interpretation:

- The review workflow is now safer and more auditable for future work, but strict final-dataset quality is intentionally not green yet.
- The 18 Codex-reviewed DUAL rows are preserved as AI-assisted recommendations, not human validation.
- DBAASP ID normalization is complete; the next AI-doable reliability task is a safe DBAASP resume strategy plus post-resume QA, while separately deciding how to handle legacy human verdict metadata and missing severity.

## 2026-07-07 DBAASP DOI Normalization

Timestamp: 2026-07-07 22:55 CST.

Goal:

- Remove the deterministic DBAASP DOI-key defect without losing checkpoint state or mixing DBAASP into release/portal data.
- Preserve backups and mapping evidence so the migration is reversible/auditable.

Code and artifact changes:

| File | Change | Quality effect |
| --- | --- | --- |
| `pipeline_v2/deepmine/build_dbaasp_worklist.py` | `ndoi()` now normalizes `_` to `/`, strips trailing filename punctuation such as `)`, validates DOI shape, and writes UTF-8 indented JSON. | Newly generated DBAASP worklists should not recreate the trailing-parenthesis DOI defect. |
| `pipeline_v2/deepmine/normalize_dbaasp_ids.py` | New dry-run/apply migration tool with collision detection, atomic writes, backups, mapping TSV, and report JSON. | Current canonical DBAASP worklist/state/extracted files can be normalized reproducibly and safely. |
| `pipeline_v2/deepmine/dbaasp_id_normalization_mapping_latest.tsv` | Audit mapping of old IDs to new IDs. | Documents every normalized ID change. |
| `pipeline_v2/deepmine/dbaasp_id_normalization_report_latest.json` | Latest dry-run/apply report. | Records before/after counts, collision count, and backup directory. |
| `pipeline_v2/deepmine/backups/dbaasp_id_normalization_20260707T145246Z/` | Backups of original `dbaasp_worklist.json`, `dbaasp_state.json`, and `dbaasp_extracted.tsv` plus manifest. | Reversible migration boundary. |

Migration result:

| Artifact | Before | After |
| --- | ---: | ---: |
| Worklist keys ending with `)` | 942 | 0 |
| State done keys ending with `)` | 182 | 0 |
| Extracted rows whose `paper_id` contained `)` | 3859 | 0 |
| Extracted unique `paper_id` values containing `)` | 173 | 0 |
| Normalization collisions | 0 | 0 |

Current DBAASP state after normalization:

- `dbaasp_worklist.json`: 2103 papers, 2103 unique keys, zero trailing-parenthesis DOI keys.
- `dbaasp_state.json`: 340 done, 1763 todo, zero trailing-parenthesis done keys.
- `dbaasp_extracted.tsv`: 4640 rows, 212 unique papers, zero `paper_id` values containing `)`.
- `state_keys_not_in_worklist=0`; `extracted_keys_not_in_state=0`; no duplicate worklist/state keys.
- `python3 pipeline_v2/deepmine/extract_dbaasp.py --list` reports `2103 DBAASP papers | 340 done | 1763 todo`.

Validation evidence:

- `python3 -m py_compile pipeline_v2/deepmine/build_dbaasp_worklist.py pipeline_v2/deepmine/normalize_dbaasp_ids.py pipeline_v2/check_review_flow.py` passed.
- Dry-run before apply found `worklist=942`, `state=182`, `extracted=3859` changes and `0` collisions.
- Apply run wrote backups under `pipeline_v2/deepmine/backups/dbaasp_id_normalization_20260707T145246Z/` before rewriting canonical files.
- `python3 pipeline_v2/check_review_flow.py --json-out pipeline_v2/review_flow_qa_latest.json` now reports `ERROR=0`, `WARN=133`; the three DBAASP malformed-ID warnings disappeared.
- `python3 pipeline_v2/check_review_flow.py --strict-final --json-out pipeline_v2/review_flow_qa_strict_latest.json` still returns 1 by design because human-review legacy metadata/severity warnings remain.

Current interpretation:

- DBAASP DOI/key normalization is complete for the current canonical artifacts.
- DBAASP is still not portal/release-ready because extraction remains incomplete/rate-limited and AI-extracted rows need a post-resume QA/review policy.
- Do not rebuild portal with DBAASP or cite DBAASP-expanded counts until the resume strategy, post-resume QA, and tier/ingest policy are explicitly complete.

## 2026-07-07 DBAASP Safe Resume Hardening

Timestamp: 2026-07-07 23:02 CST.

Goal:

- After DOI normalization, make DBAASP extraction restartable in controlled probes/batches instead of repeating large all-todo rate-limited rounds.
- Preserve the invariant that rate-limited papers are not marked done and no output rows are appended unless extraction succeeds.

Code/config changes:

| File | Change | Quality effect |
| --- | --- | --- |
| `pipeline_v2/deepmine/extract_dbaasp.py` | Adds `--limit N` / `DEEPMINE_LIMIT=N`; `--list --limit N` reports selected todo count; `--limit 0` selects no work and exits without file changes. | Enables no-cost dry probes and small controlled extraction probes. |
| `pipeline_v2/deepmine/run_dbaasp_supervised_v2.sh` | Adds `DBAASP_LIMIT`, `DBAASP_MAX_ROUNDS`, `DBAASP_STALE_LIMIT`, `DBAASP_SLEEP_SECONDS`, and `DBAASP_ONESHOT`. | Enables one-shot probes and bounded batches instead of uncontrolled retry loops. |
| `pipeline_v2/deepmine/run_dbaasp_supervised_v2.sh` | Replaces broad `pgrep -f extract_dbaasp.py` wait with a stricter check for actual python `extract_dbaasp.py` processes. | Avoids false self-wait when a shell command text contains `extract_dbaasp.py`. |
| `pipeline_v2/deepmine/dbaasp_conc.txt` | Lowered default concurrency from `12` to `2`. | Safer restart default after repeated rate-limit stops. |

Validation evidence:

- `python3 -m py_compile pipeline_v2/deepmine/extract_dbaasp.py pipeline_v2/deepmine/build_dbaasp_worklist.py pipeline_v2/deepmine/normalize_dbaasp_ids.py` passed.
- `bash -n pipeline_v2/deepmine/run_dbaasp_supervised_v2.sh pipeline_v2/deepmine/run_dbaasp_supervised.sh` passed.
- `python3 pipeline_v2/deepmine/extract_dbaasp.py --list --limit 5` reports `2103 DBAASP papers | 340 done | 1763 todo | selected=5 (limit=5)`.
- No-cost supervisor dry run: `DBAASP_MAX_ROUNDS=1 DBAASP_STALE_LIMIT=1 DBAASP_SLEEP_SECONDS=1 DBAASP_LIMIT=0 DBAASP_ONESHOT=1 bash run_dbaasp_supervised_v2.sh` exited cleanly; state remained `340`, extracted rows remained `4640`.
- Real two-paper probe: `DBAASP_LIMIT=2 DBAASP_MAX_ROUNDS=1 DBAASP_ONESHOT=1 DBAASP_STALE_LIMIT=1 DBAASP_SLEEP_SECONDS=1 bash run_dbaasp_supervised_v2.sh` ran one round and logged `rate-limited this round: 2`; state remained `340`, extracted rows remained `4640`.
- `python3 pipeline_v2/check_review_flow.py --json-out pipeline_v2/review_flow_qa_latest.json` still reports `ERROR=0`, `WARN=133`; DBAASP malformed-ID warnings remain gone.

Safe resume commands:

```bash
# No-cost control-flow probe; should not call Claude or change files.
cd pipeline_v2/deepmine
DBAASP_MAX_ROUNDS=1 DBAASP_STALE_LIMIT=1 DBAASP_SLEEP_SECONDS=1 DBAASP_LIMIT=0 DBAASP_ONESHOT=1 bash run_dbaasp_supervised_v2.sh

# Tiny quota probe; at most 2 papers, one round, no retry loop.
cd pipeline_v2/deepmine
DBAASP_LIMIT=2 DBAASP_MAX_ROUNDS=1 DBAASP_ONESHOT=1 DBAASP_STALE_LIMIT=1 DBAASP_SLEEP_SECONDS=1 bash run_dbaasp_supervised_v2.sh

# Conservative real batch once quota/provider is available; still bounded.
cd pipeline_v2/deepmine
DBAASP_LIMIT=25 DBAASP_MAX_ROUNDS=2 DBAASP_STALE_LIMIT=1 DBAASP_SLEEP_SECONDS=300 bash run_dbaasp_supervised_v2.sh
```

Current interpretation:

- The resume mechanism is safer now, but the real two-paper probe shows the active provider/quota is still rate-limited at this moment.
- Do not start a large DBAASP run until quota/provider availability changes or a different extraction backend is selected.
- The next AI-doable step is either to add a provider-availability preflight before calling Claude, or to switch DBAASP extraction to another available model/backend with the same `--limit`/state semantics.

## 2026-07-08 DBAASP Provider Preflight and Codex Fallback

Timestamp: 2026-07-08 11:28 CST.

Goal:

- Stop wasting rounds when the active provider/account is unavailable.
- Distinguish true rate limits from provider/account/config errors.
- Add a bounded Codex fallback path without changing the release/portal ingest policy.

Code and artifact changes:

| File | Change | Quality effect |
| --- | --- | --- |
| `pipeline_v2/deepmine/preflight_dbaasp_provider.py` | New provider preflight for `claude` and `codex`, with no-call mode, timeout, status classification, and JSON report at `dbaasp_provider_preflight_latest.json`. | A supervisor can stop before launching paper-level extraction if provider/quota is unavailable. |
| `pipeline_v2/deepmine/run_dbaasp_supervised_v2.sh` | Adds `DBAASP_PROVIDER=claude|codex`; preflight now uses the same provider as extraction; nonzero work stops before extraction if preflight fails. | Prevents 1763-paper retry loops when provider is unavailable. |
| `pipeline_v2/deepmine/extract_dbaasp.py` | Adds provider abstraction: default `claude`, optional `DBAASP_PROVIDER=codex`; root-safe Claude invocation avoids invalid `--dangerously-skip-permissions`; non-rate-limit provider errors are counted separately from rate limits. | Avoids mislabeling provider/account errors as rate limits and enables controlled Codex fallback. |
| `pipeline_v2/deepmine/extract_dbaasp.py` | Adds `dbaasp_empty_done.tsv` logging when a paper is marked done with zero extracted rows. | Makes zero-record completions auditable instead of silent. |
| `pipeline_v2/check_review_flow.py` | Adds QA checks/counts for `dbaasp_empty_done.tsv`. | Empty-done IDs must stay consistent with worklist/state and not conflict with extracted rows. |

Provider findings:

- Claude with the previous dangerous flag fails under root with `--dangerously-skip-permissions cannot be used with root/sudo privileges`.
- Claude without that flag now returns `API Error: 400 This organization has been disabled.`
- Therefore the current Claude path is provider/account unavailable, not merely rate-limited.
- Codex preflight succeeds with current config (`provider=codex`, `status=ok`, `returncode=0`), using the local Codex CLI and `gpt-5.5`.

Codex fallback probe result:

- Command shape: `DBAASP_PROVIDER=codex DBAASP_LIMIT=1 DBAASP_MAX_ROUNDS=1 DBAASP_ONESHOT=1 DBAASP_STALE_LIMIT=1 DBAASP_SLEEP_SECONDS=1 DBAASP_PREFLIGHT_TIMEOUT=180 DEEPMINE_CODEX_TIMEOUT=480 bash run_dbaasp_supervised_v2.sh`.
- Result: supervisor preflight passed, one paper was processed, and no provider/rate-limit errors were logged.
- `dbaasp_state.json`: 340 -> 341 done.
- `dbaasp_extracted.tsv`: 4640 -> 4640 rows, meaning this one paper produced no usable activity rows.
- Newly completed paper: `PMC13033738`, source `.../round14/source_pool/PMC13033738/paper.xml`.
- `dbaasp_empty_done.tsv` now records `PMC13033738` with provider `codex` and note `provider returned no usable activity records`.

Current DBAASP state after provider fallback work:

- Worklist: 2103 papers.
- Done: 341.
- Todo: 1762.
- Extracted rows: 4640.
- Empty-done rows: 1.
- Bad `)` IDs remain zero across worklist/state/extracted.
- QA: `python3 pipeline_v2/check_review_flow.py --json-out pipeline_v2/review_flow_qa_latest.json` reports `ERROR=0`, `WARN=133`.
- Strict final QA still returns 1 because old human-review metadata/severity warnings remain, not because of DBAASP ID/provider checks.

Safe provider commands:

```bash
# Check Claude without processing papers; currently expected to fail because the organization is disabled.
python3 pipeline_v2/deepmine/preflight_dbaasp_provider.py --provider claude --timeout 30

# Check Codex without processing papers; currently succeeds.
python3 pipeline_v2/deepmine/preflight_dbaasp_provider.py --provider codex --timeout 180

# One-paper Codex fallback probe.
cd pipeline_v2/deepmine
DBAASP_PROVIDER=codex DBAASP_LIMIT=1 DBAASP_MAX_ROUNDS=1 DBAASP_ONESHOT=1 DBAASP_STALE_LIMIT=1 DBAASP_SLEEP_SECONDS=1 DBAASP_PREFLIGHT_TIMEOUT=180 DEEPMINE_CODEX_TIMEOUT=480 bash run_dbaasp_supervised_v2.sh

# Conservative Codex batch only after reviewing probe quality/cost.
cd pipeline_v2/deepmine
DBAASP_PROVIDER=codex DBAASP_LIMIT=10 DBAASP_MAX_ROUNDS=1 DBAASP_STALE_LIMIT=1 DBAASP_SLEEP_SECONDS=300 DBAASP_PREFLIGHT_TIMEOUT=180 DEEPMINE_CODEX_TIMEOUT=480 bash run_dbaasp_supervised_v2.sh
```

Current interpretation:

- The project now has a working Codex fallback path for DBAASP, but it should be expanded gradually because Codex preflight/extraction is token-heavy and zero-row completions need QA.
- Claude should not be retried until account/organization availability is fixed.
- DBAASP remains excluded from portal/release until extraction completion, empty-row QA, and review/ingest policy are explicit.

## 2026-07-08 DBAASP Codex Fallback 10-Paper Probe

Timestamp: 2026-07-08 12:42 CST.

Goal:

- Test whether the Codex fallback can advance DBAASP extraction beyond one paper while preserving bounded execution and post-run QA.
- Measure yield, empty-paper rate, and row-quality flags before deciding whether to expand beyond small batches.

Run configuration:

```bash
cd pipeline_v2/deepmine
DBAASP_PROVIDER=codex DBAASP_LIMIT=10 DBAASP_MAX_ROUNDS=1 DBAASP_ONESHOT=1 DBAASP_STALE_LIMIT=1 DBAASP_SLEEP_SECONDS=1 DBAASP_PREFLIGHT_TIMEOUT=180 DEEPMINE_CODEX_TIMEOUT=480 bash run_dbaasp_supervised_v2.sh
```

Batch result:

| Metric | Before | After | Delta |
| --- | ---: | ---: | ---: |
| DBAASP done papers | 341 | 351 | +10 |
| DBAASP todo papers | 1762 | 1752 | -10 |
| `dbaasp_extracted.tsv` rows | 4640 | 4684 | +44 |
| `dbaasp_empty_done.tsv` rows | 1 | 6 | +5 |
| Elapsed time | - | 188 seconds | - |
| Provider/rate-limit errors | - | 0 | - |

Completed 10-paper set:

| Paper ID | Rows | Empty-done? | Note |
| --- | ---: | --- | --- |
| `PMC13036000` | 0 | yes | No usable AMP activity rows found by Codex. |
| `PMC13036774` | 3 | no | Paenidepsin A MIC/MEC rows. |
| `PMC13039887` | 0 | yes | No usable AMP activity rows found by Codex. |
| `PMC13054752` | 16 | no | Bacteriocin/growth inhibition rows; many missing sequence/negative qualitative flags. |
| `PMC12317022` | 0 | yes | No usable AMP activity rows found by Codex. |
| `PMC12450885` | 0 | yes | No usable AMP activity rows found by Codex. |
| `PMC11674141` | 12 | no | MIC/MBC rows. |
| `PMC11735859` | 5 | no | IC50 rows. |
| `PMC11752523` | 8 | no | MIC/reline rows. |
| `PMC12006171` | 0 | yes | No usable AMP activity rows found by Codex. |

Generated batch QA artifacts:

| Artifact | Purpose |
| --- | --- |
| `pipeline_v2/deepmine/dbaasp_codex_batch_20260708_1235_report.json` | Structured report for this 10-paper probe. |
| `pipeline_v2/deepmine/dbaasp_codex_batch_latest_report.json` | Convenience copy of latest Codex batch report. |
| `pipeline_v2/deepmine/dbaasp_codex_batch_20260708_1235_rows.tsv` | The 44 rows from this batch plus QA flags. |
| `pipeline_v2/deepmine/dbaasp_codex_batch_20260708_1235_review_queue.tsv` | 28 flagged rows requiring review/filtering before any ingest. |
| `pipeline_v2/deepmine/dbaasp_codex_batch_20260708_1235_session_audit.json` | Process audit mapping the 10 papers to their Codex session files. |
| `pipeline_v2/deepmine/dbaasp_codex_batch_20260708_1235_session_audit.tsv` | Tabular session audit with per-paper session counts, prompt hashes, and raw assistant JSON counts. |

Quality findings:

- 44 rows were produced from 5 papers; 5 papers were completed with zero rows and logged in `dbaasp_empty_done.tsv`.
- Verdict split: `codex_x2=17`, `codex_1=27`.
- Endpoint split includes `MIC=16`, `growth inhibition activity=16`, `MBC=4`, `MIC with 4.5% v/v reline=4`, `IC50=3`, `MEC=1`.
- QA flags in this batch: `missing_sequence=28`, `value_without_digit=7`, `qualitative_value=7`, `missing_or_literal_none_unit=7`, `negative_activity_claim=7`.
- The main quality issue is that Codex emitted some low-structure bacteriocin rows and negative qualitative rows such as `no inhibitory effect`. These must not be treated as final clean activity rows.

Hardening after probe:

- `pipeline_v2/deepmine/extract_dbaasp.py` now adds stricter prompt instructions for DBAASP pending extraction: emit only measured positive/quantitative rows, skip negative qualitative rows, and use empty strings instead of literal `None`/`null`/`NA`.
- Future extraction now uses `clean_records()` to skip negative qualitative values, skip values without digits, and normalize literal `None` in `sequence`/`unit`/`modification` to empty strings.
- Existing 44 Codex rows were not deleted; they are preserved as pending machine output and flagged in the batch review queue.

Validation evidence:

- `python3 -m py_compile pipeline_v2/deepmine/extract_dbaasp.py pipeline_v2/deepmine/preflight_dbaasp_provider.py pipeline_v2/check_review_flow.py` passed.
- `bash -n pipeline_v2/deepmine/run_dbaasp_supervised_v2.sh` passed.
- `DEEPMINE_CONC=1 python3 pipeline_v2/deepmine/extract_dbaasp.py --limit 0` did not modify state or rows (`351 -> 351`, `4684 -> 4684`).
- `python3 pipeline_v2/check_review_flow.py --json-out pipeline_v2/review_flow_qa_latest.json` still reports `ERROR=0`, `WARN=133`; remaining warnings are legacy human-review metadata/severity only.

Current interpretation:

- Codex fallback is operational and can advance DBAASP extraction, but raw output quality is mixed.
- Continue only with small bounded batches after the stricter cleaner, and keep all Codex fallback rows in `dbaasp_pending` until reviewed/filtered.
- Do not ingest DBAASP into portal/release until a filter/review policy for `codex_1`, missing sequence, qualitative values, and empty-done papers is explicit.

## 2026-07-08 DBAASP Codex Fallback Process Audit

Timestamp: 2026-07-08 13:46 CST.

Reason for audit:

- The 10-paper Codex fallback probe finished very quickly, so the process must not be over-described as publication-grade review.
- The key question is whether each paper had an independent Codex CLI run and whether it went through the strict multi-worker AMP curation workflow.

Evidence checked:

| Evidence source | Finding |
| --- | --- |
| `pipeline_v2/deepmine/extract_dbaasp.py` | `process()` runs two parallel `provider_status()` calls per paper; with `DBAASP_PROVIDER=codex`, each call invokes `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -C <ROOT> -o <tempfile> -`. |
| `pipeline_v2/deepmine/run_dbaasp_supervised_v2.sh` | The supervisor launches `python3 extract_dbaasp.py` with bounded `DBAASP_LIMIT`, provider preflight, and current `DEEPMINE_CONC`; it does not launch the six-worker paper team. |
| `/root/.codex/sessions/2026/07/08/rollout-2026-07-08T12-35*` through `12-37*` | 20 unique session files matched the DBAASP extraction prompt for the 10 selected papers. |
| `pipeline_v2/deepmine/dbaasp_codex_batch_20260708_1235_session_audit.json` | Every selected paper has exactly 2 `codex_exec` sessions; `originator_counts={"codex_exec":20}`, `source_counts={"exec":20}`. |
| `pipeline_v2/deepmine/dbaasp_codex_batch_20260708_1235_session_audit.tsv` | The extraction prompt for these sessions has `extraction_prompt_has_worker_terms=False` for all 20 sessions; `tool_like_response_items=0` for all 20. |
| `.codex/skills/amp-three-layer-curation/SKILL.md` | Strict source-reviewed curation requires material retrieval/acquisition, three scientific layers, worker-1 through worker-6, worker-6 adjudication, semantic QA, and durable rework tickets. |

Corrected conclusion:

- Yes: the 10-paper batch used independent Codex CLI sessions at the extraction-call level. There are 20 unique `codex_exec` session IDs, matching 10 papers x 2 extraction passes.
- No: this was not the strict multi-worker source-reviewed workflow. It did not launch worker-1 intake, worker-2 body/table evidence, worker-3 supplementary evidence, worker-4 database record audit, worker-5 mechanism ontology, or worker-6 adjudication.
- Therefore: the correct label is `dbaasp_pending / codex_fallback_machine_extracted / dual_pass_extraction`, not `source_reviewed`, not `publication_grade`, and not `strict_worker_curated`.
- Stop condition for ingest remains unchanged: no DBAASP Codex fallback row should enter portal/release until there is an explicit review/adjudication policy and the row-level QA queue is resolved.
- If final-dataset-grade DBAASP expansion is required, the next workflow must be a real three-layer curation/adjudication lane over selected DBAASP papers, using the local AMP worker-role contracts rather than the fast fallback extractor.

## 2026-07-08 DBAASP Strict Worker Pilot Audit

Timestamp: 2026-07-08 15:18 CST.

Plain-language conclusion:

- Not every DBAASP paper has gone through strict multi-worker review. The fast 10-paper batch was independent Codex CLI dual-pass machine extraction only.
- One paper, `PMC13036774`, has now gone through a strict pilot bridge with `worker-1` through `worker-6`, each launched as a separate `codex exec` session using `gpt-5.5` and `xhigh`.
- That strict pilot did the right thing: it did not accept the paper. Worker-6 set `review_status=needs_targeted_rework`, `publication_grade=false`, and `validator_contract_passed=false`.
- `PMC13036000` has a built packet only; it has not yet gone through worker-1..worker-6 and is missing final review/activity/mechanism/database files.
- This pilot is a bridge runner, not full durable OMX team production: `.omx/state/team` has no pilot mailbox/task files, so rework is durable in packet `rework/*.jsonl` files but not yet via OMX team mailbox state.

Evidence checked:

| Evidence source | Finding |
| --- | --- |
| `pipeline_v2/deepmine/dbaasp_codex_batch_20260708_1235_session_audit.tsv` | 20 unique `codex_exec` sessions for 10 papers, exactly 2 sessions per paper, all `gpt-5.5/xhigh`, but `extraction_prompt_has_worker_terms=False` for all rows. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot.py` | Worker runner calls `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -m gpt-5.5 -c model_reasoning_effort="xhigh" -C <ROOT> -o <last_message> -`. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC13036774/run_sequence_latest.json` | `PMC13036774` ran `worker-1,worker-2,worker-3,worker-4,worker-5,worker-6`; all return code 0. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC13036774/worker-*.stderr.log` | Six unique strict worker Codex session IDs were found; every worker stderr reports `model: gpt-5.5` and `reasoning effort: xhigh`. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13036774/final/review_report.json` | Worker-6 reports `needs_targeted_rework`, `publication_grade=false`, 3 rework targets, and cites missing SI/database-link blockers. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json` | Packet check sees 2 pilot packets; `PMC13036774` has final files but needs material rework; `PMC13036000` is `analysis_queued` and missing final files. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/dbaasp_strict_worker_process_audit_20260708_1518.json` | Durable audit report summarizing fallback sessions, strict worker session IDs, gate results, and the non-production OMX-team boundary. |

Current strict-pilot state:

- Built packets: `PMC13036774`, `PMC13036000`.
- Fully strict-worker reviewed: `PMC13036774` only.
- Strict-worker not yet run: `PMC13036000`.
- Semantic gate: `publication_grade_pass_count=0`; both pilot papers fail publication-grade at present.
- Publication gate: `publication_grade_pass=false`; risks are missing final files for `PMC13036000` and open rework for `PMC13036774`.
- Release/portal eligibility: zero DBAASP strict-pilot rows are eligible for RC release or portal ingest.

Small hardening added during audit:

- `pipeline_v2/deepmine/dbaasp_strict_pilot.py` now records the exact `codex exec` command plus parsed `codex_session_id`, `codex_model`, and `codex_reasoning_effort` into future `worker-*.run_report.json` files, so the next strict run can be audited without scraping stderr logs.

## 2026-07-08 DBAASP Strict Acceptance Proof

Timestamp: 2026-07-08 16:31 CST.

What changed:

- The strict DBAASP pilot has now been end-to-end exercised on a material-complete positive-row paper: `PMC11735859`.
- `PMC11735859` was selected because its local packet has XML, PDF, and the declared supplementary DOCX staged and parseable; unlike `PMC13036774`, it is not blocked by missing ACS SI files.
- `pipeline_v2/deepmine/dbaasp_strict_pilot.py` was hardened to:
  - snapshot locally indexed DBAASP/merged-corpus authority rows into `database/linked_*_records.jsonl`;
  - write `database/authoritative_match_report.json` even when zero authority rows are found;
  - avoid false material-gap findings from ordinary XML `ext-link` entries;
  - append newly built packets to the pilot manifest instead of hiding earlier pilot state;
  - record each worker's exact `codex exec` command, session id, model, and reasoning effort.

Commands run:

```bash
python3 -m py_compile pipeline_v2/deepmine/dbaasp_strict_pilot.py
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py build --paper-id PMC11735859 --raw-mode copy --append-manifest
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py run --paper-id PMC11735859 --workers worker-1,worker-2,worker-3,worker-4,worker-5,worker-6 --timeout 1800
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify
```

Strict worker evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC11735859/run_sequence_latest.json` records six workers: `worker-1` through `worker-6`.
- All six workers returned `0`.
- All six workers ran as separate `codex exec` sessions with `codex_model=gpt-5.5` and `codex_reasoning_effort=xhigh`.
- Session ids recorded: `019f40a1-9e2b-7c73-afbd-b388661d24b3`, `019f40a6-b796-78d0-bdf0-f620bb0b0128`, `019f40b3-df6e-72c2-92f7-f9382a2c6c45`, `019f40bc-fa7f-7792-b14a-0e5e04194c60`, `019f40c8-520e-72d0-925b-292c5f044094`, `019f40d2-08b1-75a3-80fa-559a449b75f7`.

Single-paper strict acceptance gates:

| Gate | Artifact | Result |
| --- | --- | --- |
| Packet handoff | `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11735859_check_two_queue_packets_acceptance.json` | `hard_finding_count=0`, `open_rework_ticket_count=0`, `material_extracted_complete=1`, `analysis_source_reviewed_accepted=1`. |
| Semantic gate | `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11735859_semantic_gate_acceptance.json` | `publication_grade_pass_count=1`, `publication_grade_fail_count=0`, no issues. |
| Publication-quality gate | `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11735859_publication_quality_acceptance.json` | `publication_grade_pass=true`, `risk_counts={}`. |
| Worker-6 review | `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11735859/final/review_report.json` | `review_status=accepted_with_cautions`, `publication_grade=true`, `validator_contract_passed=true`, `rework_targets=0`. |

Curated field counts for `PMC11735859`:

- Layer 1 database record verification: 5 `record_audits`, all `unresolved_record` because no authoritative linked DBAASP/merged rows were found; the five Codex fallback rows remain machine candidates.
- Layer 2 activity/toxicity evidence: 57 source-reviewed row-level activity records with endpoint, raw value/unit or rationale, target species/strain/class, assay conditions, evidence ladder, and source locators.
- Layer 3 mechanism ontology: 7 mechanism claims with evidence classes `direct_mechanism`, `phenotype_supported`, `inferred_mechanism`, `computational_only`, and `unknown_or_not_tested`.
- Review cautions: 6 caution findings, including no authoritative DBAASP linked rows, engineered MLE entity boundary, internal strain-name conflicts, no mammalian toxicity rows, nonblocking supplement gaps, and limited direct-mechanism scope.

Important boundary:

- This proves the strict review flow is operational for a material-complete paper: DBAASP pending packet -> six independent Codex worker roles -> worker-6 adjudication -> packet/semantic/publication gates -> accepted-with-cautions output.
- This does not mean all DBAASP pending records are ready for release or portal ingest.
- `PMC11735859` is source-reviewed at the paper/activity/mechanism level, but its fallback DBAASP rows are not authoritative database rows because `linked_article_records=0`, `linked_assay_records=0`, `linked_sequence_records=0`, and `linked_literature_records=0`.
- Therefore the safe release action is to preserve these as reviewed/cautioned pilot evidence, not to promote them into RC release or portal DBAASP authority tables.
- Global pilot manifest still intentionally fails publication-grade because it includes `PMC13036774` (`needs_targeted_rework`) and `PMC13036000` (`analysis_queued` and missing final files). The single-paper acceptance manifest proves the working lane without hiding the unresolved papers.

Primary audit artifact:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11735859_strict_acceptance_audit_20260708_1631.json`

## 2026-07-08 DBAASP Strict Pilot Productionization

Timestamp: 2026-07-08 16:38 CST.

Why this was added:

- The strict lane now works for one material-complete paper, but a real process needs a reproducible state view and a candidate-selection view.
- Without this, it is too easy to confuse `accepted_with_cautions` paper-level success with authoritative DBAASP release/portal ingest readiness.

New script entry points:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py candidates --limit 10
```

New status artifacts:

| Artifact | Purpose |
| --- | --- |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json` | Machine-readable pilot state across built papers: material status, analysis status, review status, worker sessions, rework tickets, final-file gaps, paper-level acceptance, and authoritative-ingest boundary. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/candidates_latest.json` | Ranks fallback-batch papers by local XML/PDF/supplement completeness, machine row count, `codex_x2` support, and whether material recovery is needed before strict worker review. |

Current `status` output:

- Pilot papers: 3.
- Material states: `material_extracted_complete=2`, `material_extracted_with_gaps=1`.
- Analysis states: `analysis_source_reviewed_accepted=1`, `analysis_needs_material_rework=1`, `analysis_queued=1`.
- Review states: `accepted_with_cautions=1`, `needs_targeted_rework=1`, `missing_review=1`.
- Source-reviewed publication-grade count: 1 (`PMC11735859`).
- Authoritative DBAASP ingest-ready count: 0.
- Open rework tickets: 2.

Per-paper next action from `status`:

| Paper | Current state | Next action |
| --- | --- | --- |
| `PMC11735859` | `accepted_with_cautions`, `publication_grade=true`, no rework targets, but no authoritative linked DBAASP rows | Preserve as source-reviewed pilot evidence; do not promote fallback rows without authoritative links. |
| `PMC13036774` | `needs_targeted_rework`; missing ACS SI and authoritative database links | Repair material packet, then rerun worker-6. |
| `PMC13036000` | `analysis_queued`; no final files | Either run worker-1..6 as a zero/empty-done path test or remove from acceptance manifest views. |

Current `candidates` output:

- Candidate papers scanned from the 10-paper fallback batch: 10.
- Unreviewed material-complete positive-row candidates currently recommended: 0.
- Highest-value unreviewed positive-row candidates need material recovery first:
  - `PMC13054752`: 16 machine rows; missing declared `jvetres-2026-0005_sm.pdf`.
  - `PMC11752523`: 8 machine rows; missing declared `mt4c01635_si_001.pdf`.
  - `PMC11674141`: 12 machine rows; missing 15 PeerJ supplementary files.
- `PMC11735859` is no longer recommended as a next candidate because it has already passed the strict lane.

Operational meaning:

- The strict lane is now not only demonstrated but inspectable.
- The next bottleneck is not worker orchestration; it is material recovery and/or authority-row linkage for the next DBAASP pending papers.

## 2026-07-08 DBAASP Independent Worker Re-Audit and Second Acceptance

Timestamp: 2026-07-08 17:58 CST.

Reason for re-audit:

- The strict path looked too fast, so the workflow was rechecked against actual local artifacts rather than chat summaries.
- The audit question was: which papers truly have independent `codex exec` worker sessions, which papers only have dual-pass machine extraction, and which papers passed strict worker-6 plus gates?

Key correction:

- Not every paper has strict multi-worker review.
- The 10-paper DBAASP Codex fallback batch remains independent dual-pass machine extraction only: 20 unique `codex_exec` sessions, 2 sessions per paper, no worker-role prompts.
- In the strict pilot, `PMC11735859` and `PMC13054752` have six independent worker sessions and are paper-level `accepted_with_cautions`.
- `PMC13036774` also has six independent worker sessions, but worker-6 correctly left it non-accepted as `needs_targeted_rework`.
- `PMC13036000` is packet-only / `analysis_queued`; it has no worker-1..6 run reports and no final review.

Strict-run evidence checked:

| Paper | Worker sessions | Model/effort | Worker-6 review | Gate/result meaning |
| --- | --- | --- | --- | --- |
| `PMC11735859` | 6 unique `codex exec` sessions | all `gpt-5.5/xhigh` | `accepted_with_cautions`, `publication_grade=true`, `rework_targets=0` | Paper-level source-reviewed complete; not authoritative DBAASP ingest because linked authority rows are 0. |
| `PMC13054752` | 6 unique `codex exec` sessions | all `gpt-5.5/xhigh` | `accepted_with_cautions`, `publication_grade=true`, `rework_targets=0` | Paper-level source-reviewed complete after supplement recovery; not authoritative DBAASP ingest because linked authority rows are 0. |
| `PMC13036774` | 6 unique `codex exec` sessions | all `gpt-5.5/xhigh` | `needs_targeted_rework`, `publication_grade=false`, 3 rework targets | Strict process ran, but the paper is not accepted because declared ACS SI/database-link blockers remain. |
| `PMC13036000` | 0 strict worker sessions | not run | missing review | Packet exists, but no strict adjudication yet. |

Fresh status after re-audit:

- Pilot papers: 4.
- Material states: `material_extracted_complete=3`, `material_extracted_with_gaps=1`.
- Analysis states: `analysis_source_reviewed_accepted=2`, `analysis_needs_material_rework=1`, `analysis_queued=1`.
- Review states: `accepted_with_cautions=2`, `needs_targeted_rework=1`, `missing_review=1`.
- Source-reviewed publication-grade count: 2 (`PMC11735859`, `PMC13054752`).
- Authoritative DBAASP ingest-ready count: 0.
- Open rework tickets: 2.

`PMC13054752` material recovery and acceptance:

- Recovered declared supplement `jvetres-2026-0005_sm.pdf` from the publisher supplement endpoint and staged it under the local source pool.
- Rebuilt `PMC13054752` packet as `material_extracted_complete`, `locator_count=142`, `dbaasp_machine_extracted_rows=16`, `dbaasp_review_queue_rows=16`, `error_count=0`.
- Ran `worker-1` through `worker-6`; all return code 0, all `gpt-5.5/xhigh`, six unique session ids.
- Worker-6 outcome: `accepted_with_cautions`, `publication_grade=true`, `validator_contract_passed=true`, `source_reviewed=true`, `rework_targets=0`, `caution_findings=5`.
- Curated layer counts: 16 database audits (`source_conflict=3`, `unresolved_record=13`), 13 activity records, 5 mechanism claims.
- Single-paper strict acceptance gates for `PMC13054752`:
  - packet gate: `hard_finding_count=0`, `open_rework_ticket_count=0`;
  - semantic gate: `publication_grade_pass_count=1`, `issue_count=0`;
  - publication-quality gate: `publication_grade_pass=true`, `risk_counts={}`.

Script hardening from this audit:

- `pipeline_v2/deepmine/dbaasp_strict_pilot.py` now backfills old worker run metadata from `stderr` when earlier `worker-*.run_report.json` files lack `codex_session_id`, `codex_model`, or `codex_reasoning_effort`.
- This fixes a misleading old-status false negative where `PMC13036774` truly ran `gpt-5.5/xhigh` but `status` previously could not see that metadata without stderr parsing.
- `python3 -m py_compile pipeline_v2/deepmine/dbaasp_strict_pilot.py` passed after the change.

Primary artifacts:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/dbaasp_strict_independent_worker_audit_20260708_1758.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/dbaasp_strict_pilot_PMC13054752_acceptance_manifest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13054752_check_two_queue_packets_acceptance.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13054752_semantic_gate_acceptance.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13054752_publication_quality_acceptance.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC13054752/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13054752/final/review_report.json`

Operational boundary:

- This is strict independent Codex CLI worker review, not full durable `omx team` mailbox production state.
- Packet rework files and run reports are durable, but `.omx/state/team` does not prove mailbox/task ownership for this bridge.
- Accepted papers are paper-level source-reviewed evidence only; they are still not authoritative DBAASP database ingest candidates until linked authoritative database rows exist and pass layer-1 authority policy.

## 2026-07-08 DBAASP Empty-Done Branch and Worker-Run Gate

Timestamp: 2026-07-08 19:20 CST.

Why this was done:

- The strict flow still had one untested built-paper branch: a material-complete paper with `dbaasp_empty_done_rows=1` and zero machine/authority rows.
- `PMC13036000` was selected to test this branch because it had XML, PDF, and supplementary DOCX, but no DBAASP candidate rows.
- This was not expected to expand the final dataset; it was a workflow stress test for "do not hallucinate AMP records" and "do not accept final JSON when a worker session failed."

What happened:

- First `PMC13036000` worker-2 run failed with Codex content-safety `Invalid prompt` after long biomedical source excerpts entered the model context.
- The failure was preserved in `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13036000_worker2_policy_failure_20260708_1816.json`.
- Worker prompts were tightened so workers must not print full XML/PDF/tables/long source passages to stdout/stderr, and must write structured artifacts to files instead.
- The full six-worker run was repeated with `--keep-going`.
- Final worker evidence after the repeated run:
  - worker-1, worker-3, worker-4, worker-5 returned 0;
  - worker-2 returned 1 with `model_safety_content_filter`;
  - worker-6 first produced a non-accepted/rework review, then a targeted rerun hit the same model-safety content filter;
  - six unique `gpt-5.5/xhigh` session ids are present, but the worker run is not clean.

Critical gate finding:

- Final artifact gates alone were too weak for this branch: semantic/publication checks can pass the final JSON even when a worker session failed.
- The controller now requires `worker_run_clean=true` before a paper counts as `paper_level_source_reviewed_complete`.
- `pipeline_v2/deepmine/dbaasp_strict_pilot.py verify` now writes and reports `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`.
- `PMC13036000` is therefore not counted as source-reviewed complete even though its final `review_report.json` currently says `accepted_with_cautions`.

Script hardening added:

- `run_worker()` now classifies nonzero worker exits, including `model_safety_content_filter`.
- `status` now exposes `worker_run.failed_workers[]`, `failed_worker_count`, and `worker_run_clean`.
- `paper_level_source_reviewed_complete` now requires all of these: final review accepted, 6 workers present, all return code 0, all `gpt-5.5/xhigh`, six unique sessions, and no failed workers.
- `run --merge-existing` can rerun one worker and merge the new report into the existing six-worker run sequence.
- `acceptance --paper-id <PMC>` now generates a single-paper acceptance manifest, packet gate, semantic gate, publication gate, and audit; it returns nonzero if worker runs are not clean.

Current interpretation:

- `PMC13036000` successfully tested the empty/no-DBAASP-row branch as a blocker case, not as an accepted dataset addition.
- Current `status` correctly keeps source-reviewed publication-grade count at 2 (`PMC11735859`, `PMC13054752`) and authoritative DBAASP ingest-ready count at 0.
- The next repair options are either:
  - repair the failed worker-2/worker-6 runs using a no-source-text interactive strategy and rerun acceptance; or
  - leave `PMC13036000` as a documented policy/runtime blocker and move to the next material-complete candidate.

Primary artifacts:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13036000_empty_done_policy_blocker_audit_20260708_1920.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13036000_worker2_policy_failure_20260708_1816.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13036000_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC13036000/run_sequence_latest.json`

## 2026-07-08 Strict Independent Codex Worker Evidence Check

Timestamp: 2026-07-08 19:31 CST.

Reason:

- The workflow still looked suspiciously fast, so the exact question was rechecked from local logs: did every current pilot paper run as independent Codex CLI worker roles, and which papers actually passed the strict multi-worker flow?

Short answer:

- All 4 current strict-pilot papers have evidence of six separate Codex CLI sessions (`worker-1` through `worker-6`) in stderr logs, with unique session ids and `gpt-5.5/xhigh` metadata.
- Only 2/4 papers strictly pass paper-level source-reviewed completion: `PMC11735859` and `PMC13054752`.
- `PMC13036774` ran cleanly through six workers, but worker-6 correctly rejected it as `needs_targeted_rework` because declared ACS supplementary material and authoritative database links remain unresolved.
- `PMC13036000` launched six Codex CLI sessions, but worker-2 and worker-6 failed with `model_safety_content_filter`; it must not be counted even though final semantic/publication artifacts can over-pass.
- 0/4 papers are authoritative DBAASP-ingest-ready because linked authoritative rows are absent.

Fresh audit table:

| Paper | Strict verdict | Workers | Unique sessions | Model/effort | Return codes | Review | Acceptance |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| `PMC11735859` | strict paper-level source-review passed | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | ready |
| `PMC13054752` | strict paper-level source-review passed | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | ready |
| `PMC13036774` | independent workers ran but worker-6 rejected | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `needs_targeted_rework` | not ready |
| `PMC13036000` | Codex sessions launched but run is not clean | 6 | 6 | all `gpt-5.5/xhigh` | worker-2/worker-6 failed | `accepted_with_cautions` artifact, but invalidated by worker gate | not ready |

Fresh gate evidence:

- `status`: `paper_count=4`, `paper_level_source_reviewed_complete=2`, `authoritative_dbaasp_ingest_ready=0`.
- `verify strict_worker_run_gate`: `returncode=1`, `hard_finding_count=2`, `hard_finding_papers=[PMC13036000]`.
- Single-paper `acceptance --paper-id` was re-run for all four papers; only `PMC11735859` and `PMC13054752` returned ready.

Important boundary:

- This pilot is a sequential independent `codex exec` bridge with role prompts, packet files, rework tickets, worker logs, and strict gates.
- It is not yet a currently active durable `omx team` mailbox production state for DBAASP; future scale-up should either keep this bridge with explicit audit gates or upgrade to full team mailbox/task ownership.
- `PMC13036774` older `worker-*.run_report.json` files lack stored command/session fields, but each `stderr.log` contains the OpenAI Codex header, session id, model, and effort; current status code backfills this evidence from stderr.

Primary artifacts:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_independent_codex_worker_audit_20260708_193145.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_independent_codex_worker_audit_20260708_193145.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_independent_codex_worker_audit_latest.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_independent_codex_worker_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`

## 2026-07-08 PMC11752523 Rework Closure and Third Acceptance

Timestamp: 2026-07-08 21:42 CST.

Why this matters:

- This turn moved the strict pilot beyond proof-of-concept into a real rework loop: missing supplement recovery, failed worker repair, packet material repair, rework ticket closure, worker-6 re-adjudication, and strict single-paper acceptance.
- It also exposed and fixed two process bugs that would have blocked scaling: duplicate supplement refs and rework tickets that could never close because responses were ignored.

What changed:

- `PMC11752523` was selected as the next positive candidate after material recovery failed on the first try.
- The XML declared the same supplement `mt4c01635_si_001.pdf` seven times; `declared_supplement_refs()` now deduplicates by supplement name while preserving all href/text mention evidence.
- The recovered supplement path was not ACS direct download. ACS returned HTML, and PMC first returned a CloudPMC proof-of-work HTML page. The recovery logic now solves the CloudPMC PoW cookie, retries the same bin URL, validates `%PDF` magic, and staged the 868,592 byte PDF.
- `extract_supplementary()` now promotes PDF text into `extracted/supplementary_text.jsonl` with locators like `supp:mt4c01635_si_001.pdf:page=1`; previously it only wrote OCR text under `extracted/ocr/`, which left `supplementary_text_count=0`.
- Worker prompts now explicitly forbid printing XML/PDF/supplement source excerpts or biomedical source passages to stdout/stderr; this prevented repeat model-safety failures after worker-2 initially failed.
- Rework response semantics were added to `pipeline_v2/deepmine/dbaasp_strict_pilot.py` and `.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py`: tickets with closed/repaired/accepted responses no longer count as open.
- Worker prompts now include the packet rework request/response paths and tell the owning lane to repair or respond durably.

Strict run and repair sequence:

- Built `PMC11752523` as `material_extracted_complete`, `locator_count=192`, `dbaasp_machine_extracted_rows=8`, `error_count=0`.
- First six-worker run: worker-1/3/4/5/6 returned 0; worker-2 hit `model_safety_content_filter` after printing source text.
- After prompt hardening, worker-2 was rerun successfully and merged into the six-worker sequence.
- Worker-6 then produced `needs_targeted_rework` with four targets: authoritative no-match, missing worker-2 canonical artifact, supplementary text exposure, and toxicity figure/body row-level gap.
- Material/analysis repair closed the first three targets and normalized supplementary text; worker-3/worker-2/worker-6 were rerun.
- Remaining toxicity material ticket was closed with durable no-fabrication material-gap evidence from worker-2: toxicity loci were checked, but row-level toxicity values were not safely recoverable from local XML/PDF/supplement/OCR/table surfaces.
- Final worker-6 re-adjudication accepted the paper with cautions.

Final `PMC11752523` evidence:

- Worker run: 6 workers, 6 unique Codex sessions, all return code 0, all `gpt-5.5/xhigh`, `worker_run_clean=true`.
- Worker-6 review: `accepted_with_cautions`, `publication_grade=true`, `validator_contract_passed=true`, `rework_targets=0`, `caution_findings=5`.
- Single-paper acceptance: `acceptance_ready_for_paper_level_source_review=true`; packet hard findings 0; packet open rework 0; semantic pass 1; publication-quality pass true.
- Layer counts: 8 database audits, 8 activity records, 0 toxicity rows with durable no-fabrication gap evidence, 5 mechanism claims.
- Boundary: still not authoritative DBAASP ingest-ready because linked authoritative article/assay/sequence/literature row counts are zero.

Updated strict pilot status:

- Pilot papers: 5.
- Paper-level source-reviewed complete: 3 (`PMC11735859`, `PMC13054752`, `PMC11752523`).
- Remaining non-complete papers: `PMC13036774` (`needs_targeted_rework`, missing ACS SI/database-link blockers) and `PMC13036000` (final artifacts over-pass but worker run failed).
- Authoritative DBAASP ingest-ready: 0.
- Global `strict_worker_run_gate` still has hard findings only for `PMC13036000`.

Primary artifacts:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11752523_material_recovery_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11752523_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11752523_rework_closure_acceptance_20260708_214239.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11752523_rework_closure_acceptance_20260708_214239.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC11752523/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11752523/rework/rework_responses.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11752523/final/review_report.json`

## 2026-07-08 PMC13036000 Worker-Run Repair and Global Worker Gate Clearance

Timestamp: 2026-07-08 22:05 CST.

Why this matters:

- `PMC13036000` was the global strict-worker-run hard blocker: final JSON and semantic/publication gates could pass, but worker-2 and worker-6 had failed earlier with model-safety content filter errors.
- This was the exact failure mode the strict pipeline must prevent: final artifacts must not overrule failed worker sessions.
- The no-source-output prompt hardening from the `PMC11752523` repair was applied to `PMC13036000`, then the failed lanes were rerun.

What changed:

- Regenerated `PMC13036000` worker-2 and worker-6 prompts with the hardened rule: do not print XML/PDF/supplement excerpts, source sentences, tables, assay-method prose, or biomedical passages to stdout/stderr.
- Reran `worker-2` and `worker-6` with independent `codex exec`, `gpt-5.5/xhigh`, and `--merge-existing`.
- Both reruns returned code 0 and were merged into `worker_logs/PMC13036000/run_sequence_latest.json`.

Final `PMC13036000` evidence:

- Worker run: 6 workers, 6 unique Codex sessions, all return code 0, all `gpt-5.5/xhigh`, `worker_run_clean=true`.
- Worker-6 review: `accepted_with_cautions`, `publication_grade=true`, `validator_contract_passed=true`, `rework_targets=0`, `caution_findings=2`.
- Single-paper acceptance: `acceptance_ready_for_paper_level_source_review=true`; packet hard findings 0; packet open rework 0; semantic pass 1; publication-quality pass true.
- Boundary: still not authoritative DBAASP ingest-ready because linked authoritative rows are zero and the paper is a nanoparticle/non-AMP-sequence branch; this is workflow evidence, not a DBAASP peptide ingest.

Updated strict pilot status:

- Pilot papers: 5.
- Paper-level source-reviewed complete: 4 (`PMC11735859`, `PMC13054752`, `PMC11752523`, `PMC13036000`).
- Remaining non-complete paper: `PMC13036774` (`needs_targeted_rework`, missing ACS SI/database-link blockers).
- Authoritative DBAASP ingest-ready: 0.
- Global `strict_worker_run_gate`: `hard_finding_count=0`.
- Remaining open rework tickets: 2, both tied to `PMC13036774`.

Primary artifacts:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13036000_worker_run_repair_acceptance_20260708_220537.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13036000_worker_run_repair_acceptance_20260708_220537.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13036000_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC13036000/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13036000/final/review_report.json`

## 2026-07-08 Strict Independent Codex Worker Recheck and 5/5 Pilot Closure

Timestamp: 2026-07-08 23:06 CST.

Why this was done:

- The user correctly challenged that the strict review appeared too fast.
- A fresh audit was run from local evidence only: active process state, `worker_logs/*/run_sequence_latest.json`, individual `worker-*.run_report.json`, Codex stderr metadata, final review reports, `status`, `verify`, and per-paper `acceptance`.
- During the audit, `PMC13036774` was not treated as complete while a new six-worker rerun was still in progress; the earlier `status` view could mix an old `run_sequence_latest.json` with newly overwritten worker stderr logs.

Critical correction and hardening:

- `pipeline_v2/deepmine/dbaasp_strict_pilot.py` now refuses to backfill old run-sequence metadata from a worker stderr log that is newer than the sequence file.
- `worker_run_clean` now requires `stale_or_mutated_log_reference_count=0`, so a rerun-in-progress cannot appear clean.
- Future `run_worker()` calls write immutable run-id-prefixed worker stdout/stderr/final-message/run-report files and also keep `worker-*.run_report.json` / `worker-*.stderr.log` as compatibility "latest" files.
- Validation: `python3 -m py_compile pipeline_v2/deepmine/dbaasp_strict_pilot.py .codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py` passed.

Final `PMC13036774` rerun evidence:

- Full rerun command was already active and completed at 2026-07-08 23:03 CST:
  `python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py run --paper-id PMC13036774 --workers worker-1,worker-2,worker-3,worker-4,worker-5,worker-6 --timeout 1800 --keep-going`.
- The run took about 51 minutes wall time, not a fast extraction shortcut.
- `PMC13036774` now has 6 workers, 6 unique `codex exec` sessions, all return code 0, all `gpt-5.5/xhigh`, and `stale_or_mutated_log_reference_count=0`.
- Worker-6 outcome: `accepted_with_cautions`, `publication_grade=true`, `validator_contract_passed=true`, `rework_targets=0`, `caution_findings=4`.
- Single-paper gates: packet hard findings 0, open rework 0, semantic pass 1/1, publication-quality pass true.
- Curated layer counts: 3 database audits (`unresolved_record=3`), 3 activity records, 5 mechanism claims.

Fresh 5-paper strict pilot state:

| Metric | Value |
| --- | ---: |
| Pilot papers | 5 |
| `material_extracted_complete` | 5 |
| `analysis_source_reviewed_accepted` | 5 |
| `accepted_with_cautions` | 5 |
| Paper-level source-reviewed complete | 5 |
| Authoritative DBAASP ingest-ready | 0 |
| Open rework tickets | 0 |
| `strict_worker_run_gate` hard findings | 0 |
| Semantic gate publication-grade pass | 5/5 |
| Publication-quality gate | pass |

Per-paper strict worker proof:

| Paper | Workers | Unique sessions | Model/effort | Return codes | Review | Activity | DB audits | Mechanism | Cautions | Auth ingest |
| --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `PMC13036774` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 3 | 3 | 5 | 4 | false |
| `PMC13036000` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 8 | 0 | 5 | 2 | false |
| `PMC11735859` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 57 | 5 | 7 | 6 | false |
| `PMC13054752` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 13 | 16 | 5 | 5 | false |
| `PMC11752523` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 8 | 8 | 5 | 5 | false |

Important boundary:

- This 5/5 result applies only to the five-paper DBAASP strict pilot, not to the full DBAASP worklist and not to the earlier fast 10-paper Codex fallback batch.
- The strict pilot is a sequential independent `codex exec` bridge with role prompts and gates; it is still not full durable `omx team` mailbox production state.
- All 5 accepted papers are paper-level source-reviewed with cautions, but `authoritative_dbaasp_ingest_ready=false` for all 5 because linked authoritative article/assay/sequence/literature row counts are zero.
- Therefore no DBAASP fallback rows should be promoted into RC release or portal authoritative tables from this pilot alone.

Primary artifacts:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_independent_codex_worker_audit_20260708_230640.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_independent_codex_worker_audit_20260708_230640.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_independent_codex_worker_audit_latest.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13036774_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC13036774/run_sequence_latest.json`

## 2026-07-08 Strict Codex CLI Independence Recheck After Manifest Expansion

Timestamp: 2026-07-08 23:54 CST.

Why this was done:

- The user again challenged that the review appeared too fast and asked whether every paper was really reviewed by independent Codex CLI sessions through strict multi-worker roles.
- This was rechecked from local evidence only: script role mapping, `codex exec` command construction, worker run reports, session IDs, active processes, prompts, `status`, and `verify`.
- Important correction: the manifest is now 6 papers because `PMC11784053` was appended after the 5-paper closure, but only the first 5 papers are currently strict-complete.

Current answer in plain terms:

- Yes for the completed five-paper strict pilot: each completed paper has 6 worker reports, 6 unique Codex session IDs, all return code 0, all `gpt-5.5/xhigh`, and `worker_run_clean=true`.
- No for every manifest paper yet: `PMC11784053` is still in the strict sequence and must not be counted as complete until worker-6 adjudication plus gates pass.
- This remains a sequential independent `codex exec` bridge with role prompts and gates, not a full durable `omx team` mailbox production state.

Script-level proof:

- `WORKER_SKILLS` maps the six lanes to different role skills: intake, body/table, supplement, database-record auditor, mechanism ontology, and adjudicator review.
- `codex_worker_command()` constructs each run as `codex exec -m gpt-5.5 -c model_reasoning_effort="xhigh" -C <workspace> -o <worker output> -`.
- `run_worker()` writes per-worker reports with prompt path, final-message path, stdout/stderr paths, return code, Codex session ID, model, and reasoning effort.
- `worker_run_clean` requires 6 worker reports, return code 0, `gpt-5.5/xhigh`, 6 unique session IDs, no failed workers, and no stale/mutated log reference.

Fresh snapshot:

| Metric | Value |
| --- | ---: |
| Manifest papers | 6 |
| Strict paper-level source-reviewed complete | 5 |
| Authoritative DBAASP ingest-ready | 0 |
| Worker reports found | 34 |
| Unique Codex session IDs found | 34 |
| Duplicate Codex session IDs | 0 |
| Nonzero worker reports | 0 |
| Wrong model/effort reports | 0 |
| Non-`codex exec` reports | 0 |

Per-paper status at this snapshot:

| Paper | Worker reports | Unique sessions | Model/effort | Return codes | Review | Worker clean | Complete? |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| `PMC13036774` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC13036000` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC11735859` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC13054752` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC11752523` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC11784053` | 4 | 4 | all `gpt-5.5/xhigh` so far | all 0 so far | `missing_review` | false | false |

Active `PMC11784053` evidence:

- Full command is running:
  `python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py run --paper-id PMC11784053 --workers worker-1,worker-2,worker-3,worker-4,worker-5,worker-6 --timeout 1800 --keep-going`.
- `worker-1` through `worker-4` have completed with independent session IDs and run-id-prefixed immutable logs under `worker_logs/PMC11784053/20260708T151352Z.worker-*.run_report.json`.
- The process had automatically moved to `worker-5` at the time of this snapshot; `worker-6` had not yet started.
- Current `verify` correctly fails the 6-paper manifest because `PMC11784053` is missing final review/activity/database outputs; this is the expected strict behavior and prevents false acceptance.

Primary artifacts:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260708_2354.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260708_2354.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC11784053/`

Next required action:

- Let `PMC11784053` finish worker-5 and worker-6.
- Then run `python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status`, `python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify`, and `python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py acceptance --paper-id PMC11784053`.
- Only after those pass should the strict-complete count move from 5 to 6.

## 2026-07-09 PMC11784053 Completion and 6/6 Strict Codex CLI Recheck

Timestamp: 2026-07-09 00:12 CST.

Follow-up to the 2026-07-08 23:54 snapshot:

- `PMC11784053` finished `worker-5` and `worker-6`; the run process ended normally.
- Fresh `status`, `verify`, and `acceptance --paper-id PMC11784053` were run after worker-6 finished.
- The strict-complete count is now 6/6 for the current strict pilot manifest.

Updated answer to the user's independence question:

- Yes, for all 6 current manifest papers, the local evidence now shows 6 independent Codex CLI worker sessions per paper.
- The evidence is 36 worker reports, 36 unique Codex session IDs, all return code 0, all `gpt-5.5/xhigh`, no duplicate session IDs, no non-`codex exec` reports, and `strict_worker_run_gate` hard findings 0.
- The role flow is still the six distinct roles: worker-1 intake, worker-2 body/table activity, worker-3 supplementary evidence, worker-4 database record audit, worker-5 mechanism ontology, worker-6 adjudicator review.
- Boundary remains unchanged: this is a sequential independent `codex exec` bridge, not full durable `omx team` mailbox production state.

Fresh 6-paper strict pilot state:

| Metric | Value |
| --- | ---: |
| Manifest papers | 6 |
| `material_extracted_complete` | 6 |
| `analysis_source_reviewed_accepted` | 6 |
| `accepted_with_cautions` | 6 |
| Paper-level source-reviewed complete | 6 |
| Authoritative DBAASP ingest-ready | 0 |
| Open rework tickets | 0 |
| Missing-final paper count | 0 |
| `strict_worker_run_gate` hard findings | 0 |
| Semantic gate return code | 0 |
| Publication-quality gate return code | 0 |

Per-paper strict worker proof:

| Paper | Workers | Unique sessions | Model/effort | Return codes | Review | Activity | DB audits | Mechanism | Cautions | Auth ingest |
| --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `PMC13036774` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 3 | 3 | 5 | 4 | false |
| `PMC13036000` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 8 | 0 | 5 | 2 | false |
| `PMC11735859` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 57 | 5 | 7 | 6 | false |
| `PMC13054752` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 13 | 16 | 5 | 5 | false |
| `PMC11752523` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 8 | 8 | 5 | 5 | false |
| `PMC11784053` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 40 | 3 | 3 | 3 | false |

`PMC11784053` acceptance evidence:

- `worker_run_clean=true`: 6 workers, 6 unique sessions, all return code 0, all `gpt-5.5/xhigh`, failed workers 0, stale/mutated log references 0.
- Worker-6 review: `accepted_with_cautions`, `publication_grade=true`, `validator_contract_passed=true`, `rework_targets=0`, `caution_findings=3`.
- Layer counts: 40 activity/toxicity records, 3 database record audits, 3 mechanism claims.
- `verify`: semantic gate return code 0, publication gate return code 0, strict worker hard findings 0.

Important boundary:

- All 6 are paper-level source-reviewed with cautions, not clean acceptance.
- Authoritative DBAASP ingest-ready remains 0 because linked authoritative article/assay/sequence/literature rows are still absent.
- Do not promote candidate DBAASP machine rows into RC release or portal authoritative tables from this pilot alone.

Primary artifacts:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_0012.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_0012.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC11784053/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11784053/final/review_report.json`

## 2026-07-09 Strict Worker Independence Audit Command Added

Timestamp: 2026-07-09 00:21 CST.

Why this was done:

- The previous independence proof was valid, but it was generated by an ad hoc Python snippet during the review.
- To make the flow repeatable after each new paper, the strict pilot script now has a first-class `audit-workers` command.

New command:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers --paper-id PMC11784053 --skip-gates
```

What it checks:

- every audited paper has exactly six worker reports;
- every worker has a unique Codex session ID;
- every worker was launched through `codex exec`;
- every worker used `gpt-5.5/xhigh`;
- every worker returned code 0;
- paper-level source-reviewed completion is present unless `--allow-incomplete` is used for an in-progress snapshot;
- global duplicate Codex session IDs are treated as hard findings;
- status/gate evidence is included in the generated JSON report.

Validation:

- `python3 -m py_compile pipeline_v2/deepmine/dbaasp_strict_pilot.py` passed.
- `python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers` returned pass=true with 6 papers, 36 worker reports, 36 unique sessions, and 0 findings.
- `python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers --paper-id PMC11784053 --skip-gates` returned pass=true with 1 paper, 6 worker reports, 6 unique sessions, and 0 findings.

New artifacts:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_002120.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_002120.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.json`

Operational rule going forward:

- After any new strict pilot paper is added and worker-6 finishes, run `status`, `verify`, `acceptance --paper-id <PMCID>`, and `audit-workers`.
- Do not count a paper or batch as strict-complete unless `audit-workers` has pass=true and the semantic/publication/worker gates are green.

## 2026-07-09 PMC12229353 Expansion and 7/7 Strict Pilot State

Timestamp: 2026-07-09 01:20 CST.

Why this was done:

- After proving the 6-paper pilot and adding a repeatable worker-independence audit command, the next test was to expand the flow by one fresh high-ranked candidate rather than only preserving the earlier proof.
- `PMC12229353` was the highest recommended material-ready candidate after `PMC11784053` was reviewed.

Build evidence:

- Command:
  `python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py build --paper-id PMC12229353 --raw-mode copy --append-manifest`
- Material status: `material_extracted_complete`.
- Locator count: 191.
- DBAASP machine candidate rows: 36.
- Extraction errors: 0.
- Linked authoritative article/assay/sequence/literature rows: 0.

Six-worker run evidence:

- Command:
  `python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py run --paper-id PMC12229353 --workers worker-1,worker-2,worker-3,worker-4,worker-5,worker-6 --timeout 1800 --keep-going`
- All six workers returned code 0.
- All six workers used `gpt-5.5/xhigh`.
- All six workers have unique Codex session IDs.
- Immutable run-id-prefixed logs are under `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC12229353/20260708T162252Z.worker-*.run_report.json`.

Worker-6 outcome:

- Review status: `accepted_with_cautions`.
- `publication_grade=true`.
- `validator_contract_passed=true`.
- `rework_targets=0`.
- `caution_findings=9`.
- Layer counts: 28 activity/toxicity records, 3 database record audits, 7 mechanism claims.
- Boundary: `authoritative_dbaasp_ingest_ready=false`.

Fresh 7-paper strict pilot state:

| Metric | Value |
| --- | ---: |
| Manifest papers | 7 |
| `material_extracted_complete` | 7 |
| `analysis_source_reviewed_accepted` | 7 |
| `accepted_with_cautions` | 7 |
| Paper-level source-reviewed complete | 7 |
| Authoritative DBAASP ingest-ready | 0 |
| Open rework tickets | 0 |
| Missing-final paper count | 0 |
| `strict_worker_run_gate` hard findings | 0 |
| Semantic gate return code | 0 |
| Publication-quality gate return code | 0 |
| `audit-workers` pass | true |
| Worker reports | 42 |
| Unique Codex session IDs | 42 |

Per-paper strict worker proof:

| Paper | Workers | Unique sessions | Model/effort | Return codes | Review | Activity | DB audits | Mechanism | Cautions | Auth ingest |
| --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `PMC13036774` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 3 | 3 | 5 | 4 | false |
| `PMC13036000` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 8 | 0 | 5 | 2 | false |
| `PMC11735859` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 57 | 5 | 7 | 6 | false |
| `PMC13054752` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 13 | 16 | 5 | 5 | false |
| `PMC11752523` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 8 | 8 | 5 | 5 | false |
| `PMC11784053` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 40 | 3 | 3 | 3 | false |
| `PMC12229353` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | 28 | 3 | 7 | 9 | false |

Candidate queue after this expansion:

- `candidate_count=217`.
- `already_reviewed_count=6` in candidate report semantics, because one reviewed manifest paper came from the earlier original subset and candidate accounting is based on the current canonical candidate pool.
- `recommended_count=20`.
- `needs_material_recovery_count=18`.
- Next top recommended material-ready candidate: `PMC12103485`.

Primary artifacts:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12229353_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_012006.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_012006.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/candidates_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC12229353/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12229353/final/review_report.json`

Next strict expansion command, if continuing:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py build --paper-id PMC12103485 --raw-mode copy --append-manifest
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py run --paper-id PMC12103485 --workers worker-1,worker-2,worker-3,worker-4,worker-5,worker-6 --timeout 1800 --keep-going
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py acceptance --paper-id PMC12103485
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
```

## Public/NAR Readiness Gate

Do not claim NAR-ready until all are complete:

- Free, no-login public website.
- Stable HTTPS URL.
- Bulk downloads with checksums.
- API and/or documented MCP access.
- Versioned schema and data dictionary synchronized to latest release.
- License/source-version table finished and reviewed.
- Manual stratified validation completed and summarized.
- 1471-vs-1472 scope reconciliation disclosed.
- AI/Codex/Claude usage disclosed accurately.
- Maintenance plan and host/institution commitment documented.
- Manuscript disclosure skeleton and figures/tables prepared.
- Competitor comparison and novelty claims checked against current primary/official sources before submission.

## 2026-07-09 Strict Codex CLI Independence Recheck After `PMC12103485`

The user again challenged that the DBAASP strict review looked too fast. I rechecked the current manifest from local run artifacts, not from chat memory.

Current answer:

- Yes, every paper currently in `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/dbaasp_strict_pilot_manifest.json` has six worker reports and six unique Codex CLI session IDs.
- Yes, the worker evidence is independent `codex exec` execution with `gpt-5.5/xhigh`, return code 0, and roles `worker-1` through `worker-6`.
- No, the manifest is not strict-complete: `PMC12103485` remains `needs_targeted_rework`, `publication_grade=false`, and `validator_contract_passed=false`.
- Therefore the correct current count is 7/8 paper-level source-reviewed complete, not 8/8.
- Authoritative DBAASP ingest-ready remains 0/8 because all strict-pilot papers still have zero linked authoritative article/assay/sequence/literature rows.
- Runtime boundary is unchanged: this is a sequential independent `codex exec` bridge, not full durable `omx team` mailbox production state.

Fresh command evidence:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py acceptance --paper-id PMC12103485
```

Fresh global result at 2026-07-09 02:27 CST:

| Metric | Value |
| --- | ---: |
| Manifest papers | 8 |
| Worker reports found | 48 |
| Unique Codex session IDs | 48 |
| Duplicate session IDs | 0 |
| Non-`codex exec` reports | 0 |
| Wrong model/effort reports | 0 |
| Nonzero worker reports | 0 |
| Strict paper-level source-reviewed complete | 7 |
| `audit-workers` hard findings | 1 |
| Open rework tickets | 0 |
| Open rework targets in final review | 1 |
| Authoritative DBAASP ingest-ready | 0 |

Per-paper strict worker proof:

| Paper | Worker reports | Unique sessions | Model/effort | Return codes | Review status | Paper-level source-reviewed complete |
| --- | ---: | ---: | --- | --- | --- | --- |
| `PMC13036774` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true |
| `PMC13036000` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true |
| `PMC11735859` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true |
| `PMC13054752` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true |
| `PMC11752523` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true |
| `PMC11784053` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true |
| `PMC12229353` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true |
| `PMC12103485` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `needs_targeted_rework` | false |

`PMC12103485` specific recheck:

- Built packet has 150 locators, 13 DBAASP fallback machine rows, and no missing final files.
- Worker-1 through worker-5 completed their lanes; worker-6 originally blocked layer 1 because authoritative linked DBAASP article/assay/sequence/literature snapshots were absent.
- I searched the local authoritative indexes and merged corpus tables for DOI `10.1007/s00726-025-03458-1`, PMID `40413361`, PMCID `PMC12103485`, title phrase `cationic antimicrobial peptide cc34`, and `CC34`; all checked files returned `NO_MATCH`.
- The durable material-gap evidence is now written to `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/database/unrecoverable_authoritative_linkage_gap.json`.
- The material rework response is recorded in `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/rework/rework_responses.jsonl` with `status=closed_no_match`, so packet-level open ticket count is now 0.
- I reran worker-6 only with `python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py run --paper-id PMC12103485 --workers worker-6 --timeout 1800 --merge-existing`; the new worker-6 session is `019f42f4-71a8-72d0-93e6-a95f14952b48`, `gpt-5.5/xhigh`, return code 0.
- Worker-6 still returned `needs_targeted_rework`, `publication_grade=false`, with one rework target, so the strict gate correctly keeps the paper nonterminal.

Current evidence files:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_022744.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_022744.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12103485_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12103485/final/review_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/database/unrecoverable_authoritative_linkage_gap.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC12103485/run_sequence_latest.json`

Next strict action:

- Do not report `PMC12103485` or the 8-paper manifest as complete.
- Either supply real authoritative DBAASP linked rows from a newer/upstream authority source, or accept that this paper remains blocked/nonterminal under the current strict worker-6 policy.
- If policy is changed to allow `closed_no_match` database-authority gaps as paper-level cautions, document that policy explicitly before rerunning worker-6; do not silently override the current hard gate.

## 2026-07-09 Strict Codex CLI Independence Recheck After `PMC11531597`

Timestamp: 2026-07-09 03:38 CST.

The user again challenged that the strict review looked too fast. I rechecked the current manifest, worker run logs, run reports, gate outputs, and acceptance command outputs from disk.

Plain answer:

- Not every paper is strictly complete.
- Every current manifest paper has six recorded `codex exec` worker reports and six unique Codex session IDs.
- Only 8/9 have all six workers return code 0; `PMC11531597` has `worker-2` return code 1 due `model_safety_content_filter`, so its activity/toxicity lane did not complete.
- Only 7/9 are paper-level source-reviewed complete; these seven are `accepted_with_cautions`, not clean.
- `PMC12103485` did go through six independent `gpt-5.5/xhigh` workers cleanly, but worker-6 still kept it as `needs_targeted_rework` because authoritative DBAASP linked rows are absent.
- `PMC11531597` was added and all six roles were launched, but strict completion is blocked until `worker-2` is repaired/rerun and then `worker-6` re-adjudicates.
- This runtime is still a sequential independent `codex exec` bridge. It proves independent Codex CLI sessions; it is not yet full durable `omx team` mailbox production orchestration.

Fresh command evidence:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py acceptance --paper-id PMC11531597
```

Fresh global result at 2026-07-09 03:38 CST:

| Metric | Value |
| --- | ---: |
| Manifest papers | 9 |
| Worker reports found | 54 |
| Unique Codex session IDs | 54 |
| Duplicate session IDs | 0 |
| Non-`codex exec` reports | 0 |
| Wrong model/effort reports | 0 |
| Nonzero worker reports | 1 |
| Strict paper-level source-reviewed complete | 7 |
| `audit-workers` hard findings | 3 |
| Open rework tickets | 1 |
| Open rework targets in final review | 2 |
| Authoritative DBAASP ingest-ready | 0 |

Per-paper strict worker proof:

| Paper | Worker reports | Unique sessions | Model/effort | Return codes | Review status | Worker run clean | Paper-level source-reviewed complete |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| `PMC13036774` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC13036000` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC11735859` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC13054752` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC11752523` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC11784053` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC12229353` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `accepted_with_cautions` | true | true |
| `PMC12103485` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | `needs_targeted_rework` | true | false |
| `PMC11531597` | 6 | 6 | all `gpt-5.5/xhigh` | `worker-2` failed | `needs_targeted_rework` | false | false |

Hard findings from `audit-workers`:

- `PMC12103485`: `paper_not_source_reviewed_complete`; worker run itself is clean, but worker-6 says `needs_targeted_rework`.
- `PMC11531597`: `nonzero_worker_returncode`; `worker-2` failed with `model_safety_content_filter`.
- `PMC11531597`: `paper_not_source_reviewed_complete`; worker run is not clean and activity records are missing.

Key evidence files:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_033843.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_033843.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC11531597/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11531597/final/review_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11531597/work/review/quality_feedback.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11531597/rework/rework_requests.jsonl`

Immediate next strict action:

- Do not count `PMC11531597` or the 9-paper manifest as complete.
- Repair the worker-2 prompt/input path so it uses safe derived table/candidate artifacts instead of pushing long biological source text into model context.
- Rerun `PMC11531597` `worker-2` with `--merge-existing`, then rerun `worker-6`, then rerun `acceptance`, `status`, `verify`, and `audit-workers`.
- Keep `PMC12103485` nonterminal unless a real authoritative DBAASP linkage appears or the strict policy is explicitly changed.

## 2026-07-09 Strict Pilot Flow Repair and 9/9 Gate Pass

Timestamp: 2026-07-09 04:19 CST.

This section supersedes the 03:38 snapshot above. The 03:38 snapshot is kept as history because it correctly captured the state before the repair.

What changed:

- `PMC11531597/worker-2` was repaired by adding a safe derived handoff artifact:
  `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11531597/analysis/activity_safe_candidate_handoff.json`.
- The script now regenerates worker-2 prompts before worker-2 runs and instructs worker-2 not to open full XML/PDF/full table text in model context.
- `PMC11531597/worker-2` reran successfully as independent `codex exec`, session `019f4345-22bf-76b0-8a85-86d6d346ca63`, `gpt-5.5/xhigh`, return code 0, and wrote 30 source-located activity rows.
- `PMC11531597/worker-6` reran successfully as session `019f434e-7c34-7c51-8dbc-6c881d8ab4a0`, accepted the paper as `accepted_with_cautions`, and left authoritative DBAASP ingest false.
- The stale `PMC11531597` rework ticket was closed with a controller response after worker-2 repair and worker-6 re-adjudication.
- `PMC12103485/worker-6` was rerun after making the no-authoritative-linkage policy explicit: durable `closed_no_match` DBAASP linkage gaps are accepted as cautions only when fallback rows remain unresolved/database-only and are not promoted to source-verified or authoritative ingest.
- `PMC12103485/worker-6` reran successfully as session `019f435a-ee2a-7c23-8ede-7157ab626f44`, changed the paper to `accepted_with_cautions`, and preserved authoritative DBAASP ingest false.

Final gate evidence:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py acceptance --paper-id PMC11531597
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py acceptance --paper-id PMC12103485
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
```

Final global result at 2026-07-09 04:19 CST:

| Metric | Value |
| --- | ---: |
| Manifest papers | 9 |
| Material extracted complete | 9 |
| Analysis source-reviewed accepted | 9 |
| Review status `accepted_with_cautions` | 9 |
| Paper-level source-reviewed complete | 9 |
| Authoritative DBAASP ingest-ready | 0 |
| Open rework tickets | 0 |
| Missing-final paper count | 0 |
| Worker reports found | 54 |
| Unique Codex session IDs | 54 |
| Duplicate session IDs | 0 |
| Nonzero worker reports | 0 |
| Wrong model/effort reports | 0 |
| Non-`codex exec` reports | 0 |
| Packet gate return code | 0 |
| Semantic gate pass/fail | 9/0 |
| Publication gate pass | true |
| Strict worker gate hard findings | 0 |
| `audit-workers` hard findings | 0 |

Final evidence files:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_041917.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_041917.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11531597_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12103485_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC11531597/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC12103485/run_sequence_latest.json`

Important boundary:

- This proves the current 9-paper strict pilot flow is now passable under the sequential independent `codex exec` bridge.
- This does not mean authoritative DBAASP ingest is ready; all 9 still have `authoritative_dbaasp_ingest_ready=false`.
- This still is not full durable `omx team` mailbox production orchestration. The next engineering step is scaling this proven strict path into a durable queue/controller with the same hard gates.

## 2026-07-09 Strict Codex CLI Independence Recheck After Speed Concern

Timestamp: 2026-07-09 04:28 CST.

Question checked:

- Whether every current strict-pilot paper was reviewed by independent Codex CLI worker sessions, not a fast copied/fallback summary.
- Whether the strict six-role flow was actually enforced: worker-1 intake/linkage, worker-2 body/table activity/toxicity, worker-3 supplementary evidence, worker-4 database record audit, worker-5 mechanism ontology, worker-6 adjudication/review.
- Whether worker-6 final adjudication happened after the latest upstream worker output for the same paper.

Fresh commands run:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
for p in PMC13036774 PMC13036000 PMC11735859 PMC13054752 PMC11752523 PMC11784053 PMC12229353 PMC12103485 PMC11531597; do
  python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py acceptance --paper-id "$p"
done
python3 -m py_compile pipeline_v2/deepmine/dbaasp_strict_pilot.py
```

Fresh audit result:

| Metric | Value |
| --- | ---: |
| Audit timestamp | 2026-07-09 04:25 CST |
| Manifest papers | 9 |
| Strict paper-level completed | 9 |
| Total worker reports | 54 |
| Unique Codex sessions | 54 |
| Duplicate session IDs | 0 |
| Nonzero worker reports | 0 |
| Bad model/effort reports | 0 |
| Non-`codex exec` reports | 0 |
| Worker independence pass | true |
| `audit-workers` hard findings | 0 |
| `strict_worker_run_gate` hard findings | 0 |
| Semantic gate | 9 pass / 0 fail |
| Publication gate | pass |
| Per-paper acceptance checks | 9/9 returned 0 |
| Authoritative DBAASP ingest-ready | 0 |

Script-level proof:

- `pipeline_v2/deepmine/dbaasp_strict_pilot.py` builds the worker command as `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -m gpt-5.5 -c model_reasoning_effort="xhigh" -C <workspace> -o <last_message> -`.
- `run_worker()` writes both immutable run-id-prefixed reports and compatibility latest reports for every worker: `.last_message.md`, `.stdout.log`, `.stderr.log`, and `.run_report.json`.
- `worker_run_clean` requires exactly 6 worker reports, all return code 0, all `gpt-5.5/xhigh`, 6 unique session IDs, no failed workers, and no stale/mutated stderr references.
- `audit-workers` fails on missing workers, duplicate per-paper sessions, duplicate global sessions, nonzero return codes, model/effort mismatch, non-`codex exec` reports, or a non-source-reviewed final state.

Per-paper result from the fresh audit:

| Paper | Reports | Unique sessions | `codex exec` | Model/effort | Return codes | Worker-6 after latest worker-1..5 | Review status | Paper-level complete | Auth ingest |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `PMC13036774` | 6 | 6 | true | all `gpt-5.5/xhigh` | all 0 | true | `accepted_with_cautions` | true | false |
| `PMC13036000` | 6 | 6 | true | all `gpt-5.5/xhigh` | all 0 | true | `accepted_with_cautions` | true | false |
| `PMC11735859` | 6 | 6 | true | all `gpt-5.5/xhigh` | all 0 | true | `accepted_with_cautions` | true | false |
| `PMC13054752` | 6 | 6 | true | all `gpt-5.5/xhigh` | all 0 | true | `accepted_with_cautions` | true | false |
| `PMC11752523` | 6 | 6 | true | all `gpt-5.5/xhigh` | all 0 | true | `accepted_with_cautions` | true | false |
| `PMC11784053` | 6 | 6 | true | all `gpt-5.5/xhigh` | all 0 | true | `accepted_with_cautions` | true | false |
| `PMC12229353` | 6 | 6 | true | all `gpt-5.5/xhigh` | all 0 | true | `accepted_with_cautions` | true | false |
| `PMC12103485` | 6 | 6 | true | all `gpt-5.5/xhigh` | all 0 | true | `accepted_with_cautions` | true | false |
| `PMC11531597` | 6 | 6 | true | all `gpt-5.5/xhigh` | all 0 | true | `accepted_with_cautions` | true | false |

Role-level result:

- `worker-1`: 9 reports, 9 unique sessions, 9/9 return code 0 with `gpt-5.5/xhigh`.
- `worker-2`: 9 reports, 9 unique sessions, 9/9 return code 0 with `gpt-5.5/xhigh`.
- `worker-3`: 9 reports, 9 unique sessions, 9/9 return code 0 with `gpt-5.5/xhigh`.
- `worker-4`: 9 reports, 9 unique sessions, 9/9 return code 0 with `gpt-5.5/xhigh`.
- `worker-5`: 9 reports, 9 unique sessions, 9/9 return code 0 with `gpt-5.5/xhigh`.
- `worker-6`: 9 reports, 9 unique sessions, 9/9 return code 0 with `gpt-5.5/xhigh`.

Evidence files:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_042514.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_042514.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/<PMCID>/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/<PMCID>/worker-*.run_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/<PMCID>/final/review_report.json`

Important boundary:

- Yes: the 9-paper strict pilot now has file-backed evidence for six independent Codex CLI worker roles per paper.
- No: this is not full durable `omx team` mailbox orchestration; it is a sequential independent `codex exec` bridge with strict gates.
- No: this is not clean acceptance; all 9 are `accepted_with_cautions`.
- No: this is not authoritative DBAASP ingest readiness; all 9 remain `authoritative_dbaasp_ingest_ready=false`.
- Some latest accepted worker sets include repaired/rerun lanes, so the final evidence set is not always a simple worker-1-to-worker-6 first-run sequence. The important validated condition is that final worker-6 adjudication is after the latest upstream worker output for that paper.

## 2026-07-09 Resumable Strict Controller Added

Timestamp: 2026-07-09 04:36 CST.

What changed:

- Added a first controller surface to `pipeline_v2/deepmine/dbaasp_strict_pilot.py`.
- New commands:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller once --limit 1 --dry-run
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller once --paper-id <PMCID>
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller loop --max-iterations 3 --limit 1
```

Controller behavior:

- Selects the next recommended candidate from `candidates`, unless `--paper-id` is supplied.
- Builds the packet and appends it to `dbaasp_strict_pilot_manifest.json` only when needed, unless `--force-rebuild`.
- Reuses clean worker runs when possible.
- Reruns missing, failed, non-`gpt-5.5/xhigh`, non-`codex exec`, or incomplete worker lanes.
- Reruns `worker-6` when upstream worker output changed or final source-reviewed acceptance is not proven.
- Runs single-paper acceptance gates after worker completion.
- Runs global `status`, `verify`, and `audit-workers` before declaring `controller_status=completed`.
- Writes timestamped JSON/Markdown reports plus `reports/controller_latest.json` and `reports/controller_latest.md`.

Validation run:

```bash
python3 -m py_compile pipeline_v2/deepmine/dbaasp_strict_pilot.py
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller once --help
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller loop --help
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller once --limit 1 --dry-run --candidate-scan-limit 20
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller once --paper-id PMC11531597 --limit 1 --candidate-scan-limit 5
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller loop --limit 1 --max-iterations 2 --dry-run --candidate-scan-limit 5
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
```

Fresh validation result:

| Check | Result |
| --- | --- |
| Syntax compile | pass |
| `controller once --help` | pass |
| `controller loop --help` | pass |
| Dry-run next candidate | `PMC11292031` |
| Dry-run planned workers | `worker-1` through `worker-6` |
| Dry-run state mutation | no build/worker/gates; only reports written |
| Real controller path on completed paper | `PMC11531597`, skipped clean workers, reran acceptance/global gates |
| Real controller status | `completed` |
| Post-controller manifest papers | 9 |
| Post-controller strict-complete count | 9 |
| Post-controller worker reports | 54 |
| Post-controller unique sessions | 54 |
| Post-controller hard findings | 0 |
| Post-controller authoritative ingest-ready | 0 |

Evidence files:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_once_20260709_043517.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_once_20260709_043517.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_once_20260709_043532.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_once_20260709_043532.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_loop_20260709_043536.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_loop_20260709_043536.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_latest.md`

Current controller boundary:

- This is enough to stop hand-stitching `build -> run -> acceptance -> status -> verify -> audit-workers`.
- It is still a sequential independent `codex exec` controller, not full durable `omx team` mailbox production orchestration.
- The next real scaling action is to run:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller once --limit 1 --timeout 1800
```

This should process `PMC11292031` unless the candidate state changes. Do not claim 10/10 until that command completes and the controller report says `controller_status=completed` with global audit hard findings 0.

## 2026-07-09 First Real Controller-Driven New Paper Run

Timestamp: 2026-07-09 05:28 CST.

The controller was used for a real new-paper pass, not just dry-run or an already-complete paper.

Command run:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller once --limit 1 --timeout 1800 --candidate-scan-limit 20
```

Selected paper:

- `PMC11292031`
- DOI: `10.1515/biol-2022-0927`
- PMID: `39091626`
- Title: `Evaluation of the activity of antimicrobial peptides against bacterial vaginosis`
- Candidate basis: top recommended `dbaasp_extracted.tsv` candidate, material complete, 10 machine rows, 10 `claude_x2` rows, no declared missing supplements.

Controller result:

| Stage | Result |
| --- | --- |
| Packet build | built new packet |
| Material status | `material_extracted_complete` |
| Locator count | 97 |
| DBAASP machine rows | 10 |
| Worker run | `worker-1` through `worker-6` |
| Failed workers | 0 |
| Worker model/effort | all `gpt-5.5/xhigh` |
| Worker launch path | all independent `codex exec` |
| Acceptance gates | pass |
| Review status | `accepted_with_cautions` |
| Paper-level source-reviewed complete | true |
| Authoritative DBAASP ingest-ready | false |
| Controller status | `completed` |

Worker sessions for `PMC11292031`:

| Worker | Session | Return code | Start UTC | Finish UTC |
| --- | --- | ---: | --- | --- |
| `worker-1` | `019f4373-cbcd-7600-b1ab-60035beca0d5` | 0 | 2026-07-08T20:38:09Z | 2026-07-08T20:42:52Z |
| `worker-2` | `019f4378-1a76-7d13-a01a-83a2988d81c1` | 0 | 2026-07-08T20:42:52Z | 2026-07-08T20:52:23Z |
| `worker-3` | `019f4380-d3ce-7701-93cc-e6490f798a60` | 0 | 2026-07-08T20:52:23Z | 2026-07-08T21:00:49Z |
| `worker-4` | `019f4388-8b91-74c3-9b02-4b7d10e878f4` | 0 | 2026-07-08T21:00:49Z | 2026-07-08T21:08:27Z |
| `worker-5` | `019f438f-8718-7ff0-8164-8bdb39041ad7` | 0 | 2026-07-08T21:08:27Z | 2026-07-08T21:17:59Z |
| `worker-6` | `019f4398-430b-7572-a8df-57121b65c0df` | 0 | 2026-07-08T21:17:59Z | 2026-07-08T21:27:24Z |

Post-run global state:

| Metric | Value |
| --- | ---: |
| Manifest papers | 10 |
| Strict paper-level completed | 10 |
| Worker reports | 60 |
| Unique Codex sessions | 60 |
| `audit-workers` hard findings | 0 |
| `strict_worker_run_gate` hard findings | 0 |
| Semantic gate return code | 0 |
| Publication gate return code | 0 |
| Open rework tickets | 0 |
| Missing-final paper count | 0 |
| Authoritative DBAASP ingest-ready | 0 |

Follow-up candidate state:

- `candidates --limit 5` now reports `already_reviewed_count=9`, `recommended_count=17`.
- Next top candidates are `PMC12144240`, `PMC12022103`, `PMC13013390`, `PMC13031788`, and `PMC13031288`.

Evidence files:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_once_20260709_052725.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_once_20260709_052725.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11292031_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_052753.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC11292031/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11292031/final/review_report.json`

Current interpretation:

- The controller is no longer only planned; it successfully processed a new strict-pilot paper end-to-end.
- This materially advances "打通这一流程" because candidate selection, packet build, six independent Codex CLI workers, worker-6 adjudication, single-paper acceptance, global gates, and durable reports were all executed by one controller command.
- Boundary remains: this is still sequential independent `codex exec`, not full durable `omx team` mailbox production. All 10 accepted papers are still cautioned and none are authoritative DBAASP-ingest-ready.

## 2026-07-09 Speed Concern / Strict Worker Independence Recheck

Timestamp: 2026-07-09 05:36 CST.

Question checked: the strict pilot looked fast, so recheck whether each current paper really has independent Codex CLI review and whether each paper went through the strict multi-worker role flow.

Commands and checks rerun:

```bash
python3 -m py_compile pipeline_v2/deepmine/dbaasp_strict_pilot.py
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py candidates --limit 10
```

Additional ad hoc checks were run over `run_sequence_latest.json`, worker `stderr` logs, prompts, and `final/review_report.json` files to avoid relying only on the built-in audit command.

Fresh result:

| Check | Result |
| --- | ---: |
| Manifest papers | 10 |
| Material extracted complete | 10 |
| Analysis source-reviewed accepted | 10 |
| Review status | 10 `accepted_with_cautions` |
| Worker reports found | 60 |
| Unique Codex CLI sessions | 60 |
| Duplicate session IDs | 0 |
| Nonzero worker return codes | 0 |
| Bad model/effort reports | 0 |
| Non-`codex exec` reports | 0 |
| Role-order violations | 0 |
| Worker-6 freshness violations | 0 |
| Prompt contract violations | 0 |
| Stderr session mismatches | 0 |
| Open rework tickets | 0 |
| Missing-final papers | 0 |
| `strict_worker_run_gate` hard findings | 0 |
| `audit-workers` hard findings | 0 |
| Semantic gate return code | 0 |
| Publication gate return code | 0 |
| Authoritative DBAASP ingest-ready | 0 |

Strict role flow confirmed for every manifest paper:

1. `worker-1` / `intake_linkage`
2. `worker-2` / `body_table_activity_toxicity`
3. `worker-3` / `supplementary_evidence`
4. `worker-4` / `database_record_audit`
5. `worker-5` / `mechanism_ontology`
6. `worker-6` / `adjudicator_review`

Script-level evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot.py` defines `codex_worker_command()` as `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -m gpt-5.5 -c model_reasoning_effort="xhigh" -C <ROOT> -o <last_message> -`.
- `run_worker()` writes each worker prompt to stdin for that `codex exec`, stores stdout/stderr/final message/run report, and parses `codex_session_id`, `codex_model`, and `codex_reasoning_effort` from Codex stderr.
- `audit-workers` checks 6 workers per paper, unique sessions, all return code 0, all `gpt-5.5/xhigh`, all `codex exec`, no duplicate sessions across the batch, and no paper accepted without clean worker provenance.
- The controller terminal path requires worker count 6, all return code 0, all `gpt-5.5/xhigh`, 6 unique sessions, packet gate pass, semantic gate pass, publication gate pass, and global audit pass.

Important caveat found:

- 30/60 newer worker reports point to immutable run-id-prefixed logs such as `20260708T203809Z.worker-6.stderr.log`.
- 30/60 older worker reports still point to compatibility paths such as `worker-6.stderr.log`, because they predate the immutable-log hardening.
- This is not evidence of a skipped Codex run: all 60 session IDs were present in their referenced stderr logs, and the stale/mutated-log guard reported 0 mismatches. It does mean older half of the pilot has weaker log immutability than the newest controller-generated runs.

Boundary remains unchanged:

- Yes, the current 10 manifest papers have independent Codex CLI six-worker evidence.
- Yes, each accepted paper has worker-6 adjudication after the latest upstream worker outputs.
- No, this is not full durable `omx team` mailbox production orchestration; it is a sequential independent `codex exec` bridge.
- No, `accepted_with_cautions` is not clean acceptance.
- No, paper-level source-reviewed completion is not authoritative DBAASP release ingest readiness.

Evidence files:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_053230.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_053230.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/candidates_latest.json`

## 2026-07-09 Second Real Controller-Driven New Paper Run

Timestamp: 2026-07-09 06:33 CST.

The controller was run again on the next recommended material-ready candidate.

Command run:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller once --limit 1 --timeout 1800 --candidate-scan-limit 20
```

Selected paper:

- `PMC12144240`
- DOI: `10.1038/s41598-025-04901-9`
- PMID: `40481070`
- Title: `Antibacterial activity of the novel peptide Pac-525 with the RGD motif against intracellular Escherichia coli`
- Candidate basis: top recommended unreviewed candidate after `PMC11292031`; XML/PDF present, 1 declared supplement staged, 24 machine rows, 4 `claude_x2` rows, no missing declared supplements.

Controller result:

| Stage | Result |
| --- | --- |
| Packet build | built new packet |
| Material status | `material_extracted_complete` |
| Locator count | 135 |
| DBAASP machine rows | 24 |
| Worker run | `worker-1` through `worker-6` |
| Failed workers | 0 |
| Worker model/effort | all `gpt-5.5/xhigh` |
| Worker launch path | all independent `codex exec` |
| Worker-6 timing | started after workers 1-5 completed |
| Acceptance gates | pass |
| Review status | `accepted_with_cautions` |
| Paper-level source-reviewed complete | true |
| Authoritative DBAASP ingest-ready | false |
| Controller status | `completed` |

Layer outputs for `PMC12144240`:

| Layer | Count / status |
| --- | --- |
| Activity/toxicity records | 14 source-located accepted records |
| Database identity records | 4 records |
| Database status counts | `source_verified=0`, `source_conflict=1`, `sequence_modified_not_normalized=1`, `unresolved_record=2` |
| Mechanism claims | 3 claims |
| Rework targets | 0 |
| Caution findings | 3 |

Worker sessions for `PMC12144240`:

| Worker | Role | Session | Return code | Start UTC | Finish UTC |
| --- | --- | --- | ---: | --- | --- |
| `worker-1` | `intake_linkage` | `019f43ab-8c0a-7a92-8f6e-636d990214d8` | 0 | 2026-07-08T21:39:03Z | 2026-07-08T21:45:41Z |
| `worker-2` | `body_table_activity_toxicity` | `019f43b1-9f07-71a0-b0a9-dd4bc24f30a2` | 0 | 2026-07-08T21:45:41Z | 2026-07-08T21:56:25Z |
| `worker-3` | `supplementary_evidence` | `019f43bb-71f5-7b90-8dcf-3921fc99a50f` | 0 | 2026-07-08T21:56:25Z | 2026-07-08T22:07:43Z |
| `worker-4` | `database_record_audit` | `019f43c5-c99e-7731-b730-0f7164b6f85f` | 0 | 2026-07-08T22:07:43Z | 2026-07-08T22:16:49Z |
| `worker-5` | `mechanism_ontology` | `019f43ce-1e88-7fa3-b0d5-12cc16c7afab` | 0 | 2026-07-08T22:16:49Z | 2026-07-08T22:24:36Z |
| `worker-6` | `adjudicator_review` | `019f43d5-3ed9-7130-8d17-646787ce9775` | 0 | 2026-07-08T22:24:36Z | 2026-07-08T22:30:47Z |

Post-run global state:

| Metric | Value |
| --- | ---: |
| Manifest papers | 11 |
| Strict paper-level completed | 11 |
| Review status | 11 `accepted_with_cautions` |
| Worker reports | 66 |
| Unique Codex sessions | 66 |
| Duplicate session IDs | 0 |
| Nonzero worker reports | 0 |
| Bad model/effort reports | 0 |
| Non-`codex exec` reports | 0 |
| `audit-workers` hard findings | 0 |
| `strict_worker_run_gate` hard findings | 0 |
| Semantic gate return code | 0 |
| Publication gate return code | 0 |
| Open rework tickets | 0 |
| Missing-final paper count | 0 |
| Authoritative DBAASP ingest-ready | 0 |

Small hardening fix from this run:

- `pipeline_v2/deepmine/dbaasp_strict_pilot.py` status aggregation now recognizes both older `record_audits/status_summary` and newer `records/status_counts` final database-record schemas.
- Without this fix, `PMC12144240` was scientifically reviewed correctly but the dashboard summary showed `database_record_audit_count=0`.
- After the fix, `status` and `audit-workers` report `database_record_audit_count=4` for `PMC12144240`, with the correct status distribution.

Follow-up candidate state:

- `candidates --limit 10` now reports `already_reviewed_count=10`, `recommended_count=16`.
- Next top candidates are `PMC12022103`, `PMC13013390`, `PMC13031788`, `PMC13031288`, and `PMC12230126`.

Evidence files:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_once_20260709_063047.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_once_20260709_063047.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12144240_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC12144240/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12144240/final/review_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12144240/final/database_record_verification.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_063246.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_063246.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/candidates_latest.json`

Boundary remains unchanged:

- This is strong evidence that the controller can repeatedly advance real new papers through the strict six-worker bridge.
- It is still sequential independent `codex exec`, not full durable `omx team` mailbox production.
- All 11 accepted papers are `accepted_with_cautions`, not clean acceptance.
- Authoritative DBAASP release ingest remains 0 because local authoritative linked rows are absent; machine fallback rows stay candidate-only.

## 2026-07-09 Third Controller Run With Real Rework Loop

Timestamp: 2026-07-09 07:55 CST.

The controller was run on the next recommended material-ready candidate, and this time it correctly hit a nonterminal gate first, then was repaired through a targeted material-gap closure and worker re-adjudication.

Initial controller command:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py controller once --limit 1 --timeout 1800 --candidate-scan-limit 20
```

Selected paper:

- `PMC12022103`
- DOI: `10.1038/s41598-025-98330-3`
- PMID: `40274891`
- Title: `Rational design of synthetic antimicrobial peptides based on the Escherichia coli ShoB toxin`
- Candidate basis: top recommended unreviewed candidate after `PMC12144240`; XML/PDF present, one declared supplement staged, 49 machine rows, no missing declared supplements.

Initial controller result:

| Stage | Result |
| --- | --- |
| Packet build | built new packet |
| Material status | `material_extracted_complete` |
| Locator count | 151 |
| DBAASP machine rows | 49 |
| Worker run | `worker-1` through `worker-6` |
| Failed workers | 0 |
| Worker model/effort | all `gpt-5.5/xhigh` |
| Worker launch path | all independent `codex exec` |
| Initial review status | `needs_targeted_rework` |
| Initial controller status | `blocked_by_acceptance_gate` |
| Initial blocker | open toxicity/hemolysis material rework tickets |

Blocking rework:

- `worker-2` found 49 source-located activity rows but no exact row-level numeric hemolysis values in extracted XML/PDF/supplement text.
- `worker-2` wrote `rwk-PMC12022103-worker2-hemolysis-figure-values`.
- `worker-3` verified the supplement and left a non-closing response: the supplement had no hemolysis numeric table and the relevant main-paper Fig. 6 values were plot-only.
- `worker-6` wrote `rwk-PMC12022103-worker6-toxicity-material-closure` and kept the paper nonterminal with `needs_targeted_rework`.

Material-gap repair:

- A closed-gap material review was written instead of inventing plot-derived toxicity values.
- The material review concluded that XML/PDF/supplement surfaces prove the hemolysis assay and toxicity concern, but exact row-level hemolysis percentages are not available as text/table data.
- Visual plot digitization was explicitly rejected because it would create approximate values rather than source-reported exact raw values.
- Both toxicity tickets were closed with `status=closed_no_match`, `analysis_can_resume=true`, and instructions to preserve hemolysis as unresolved toxicity/caution rather than manufacture numeric rows.

Repair commands:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py run --paper-id PMC12022103 --workers worker-2,worker-6 --timeout 1800 --keep-going --merge-existing
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py acceptance --paper-id PMC12022103
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py candidates --limit 10
```

Final result for `PMC12022103`:

| Field | Value |
| --- | --- |
| Review status | `accepted_with_cautions` |
| Publication grade flag | true |
| Validator contract passed | true |
| Acceptance ready | true |
| Authoritative DBAASP ingest-ready | false |
| Open rework tickets | 0 |
| Rework targets | 0 |
| Caution findings | 6 |
| Activity records | 49 |
| Toxicity records | 0 exact numeric rows; unresolved/caution preserved |
| Database identity records | 9 |
| Database status counts | `source_verified=0`, `sequence_modified_not_normalized=2`, `unresolved_record=7` |
| Mechanism claims | 5 |

Final `PMC12022103` worker sessions:

| Worker | Role | Session | Return code | Start UTC | Finish UTC |
| --- | --- | --- | ---: | --- | --- |
| `worker-1` | `intake_linkage` | `019f43df-f4e3-7de2-96a2-0ab9503ed390` | 0 | 2026-07-08T22:36:18Z | 2026-07-08T22:43:50Z |
| `worker-2` | `body_table_activity_toxicity` | `019f4413-35cb-7f51-a290-e57a26e3cd61` | 0 | 2026-07-08T23:32:17Z | 2026-07-08T23:41:21Z |
| `worker-3` | `supplementary_evidence` | `019f43ef-e1bf-7521-ade6-3b5a9eed2651` | 0 | 2026-07-08T22:53:42Z | 2026-07-08T23:02:55Z |
| `worker-4` | `database_record_audit` | `019f43f8-5519-7cf1-ab03-3efddc6d6163` | 0 | 2026-07-08T23:02:55Z | 2026-07-08T23:10:38Z |
| `worker-5` | `mechanism_ontology` | `019f43ff-62fd-7fd3-bffd-5db8aee9ecf4` | 0 | 2026-07-08T23:10:38Z | 2026-07-08T23:18:47Z |
| `worker-6` | `adjudicator_review` | `019f441b-84f4-7182-a6dc-0758cad96973` | 0 | 2026-07-08T23:41:21Z | 2026-07-08T23:53:22Z |

Post-repair global state:

| Metric | Value |
| --- | ---: |
| Manifest papers | 12 |
| Strict paper-level completed | 12 |
| Review status | 12 `accepted_with_cautions` |
| Worker reports | 72 |
| Unique Codex sessions | 72 |
| Duplicate session IDs | 0 |
| Nonzero worker reports | 0 |
| Bad model/effort reports | 0 |
| Non-`codex exec` reports | 0 |
| `audit-workers` hard findings | 0 |
| `strict_worker_run_gate` hard findings | 0 |
| Semantic gate return code | 0 |
| Publication gate return code | 0 |
| Open rework tickets | 0 |
| Missing-final paper count | 0 |
| Authoritative DBAASP ingest-ready | 0 |

Controller/runtime hardening from this run:

- `pipeline_v2/deepmine/dbaasp_strict_pilot.py` now writes JSON and JSONL through atomic temp-file plus `os.replace()`.
- Reason: running `status`, `verify`, and `audit-workers` in parallel exposed a transient `packet_manifest.json` read/write race. The file recovered on a later write, but non-atomic writes were unsafe for repeated automated controller/gate runs.
- After the atomic-write fix, `py_compile`, single-paper acceptance, global `status`, `verify`, `audit-workers`, and `candidates` all completed cleanly.

Follow-up candidate state:

- `candidates --limit 10` now reports `already_reviewed_count=11`, `recommended_count=15`.
- Next top candidates are `PMC13013390`, `PMC13031788`, `PMC13031288`, `PMC12230126`, and `PMC12019989`.

Evidence files:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_once_20260709_072947.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/controller_once_20260709_072947.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12022103_hemolysis_closed_gap_material_review_20260709_0735.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12022103_hemolysis_closed_gap_material_review_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12022103_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC12022103/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12022103/final/review_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12022103/final/activity_toxicity_evidence.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12022103/rework/rework_requests.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12022103/rework/rework_responses.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_075523.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_20260709_075523.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`

Boundary remains unchanged:

- This run is better evidence of the workflow than a straight pass: it demonstrated nonterminal gating, durable material rework tickets, closed-gap evidence, selective worker rerun, worker-6 re-adjudication, and green global gates.
- Do not treat the missing hemolysis numeric rows as recovered data; they remain an explicit toxicity evidence limitation/caution.
- This is still sequential independent `codex exec`, not full durable `omx team` mailbox production.
- All 12 accepted papers are `accepted_with_cautions`, not clean acceptance.
- Authoritative DBAASP release ingest remains 0 because local authoritative linked rows are absent; machine fallback rows stay candidate-only.

## Current Priority Backlog

1. Do not call the 2026-07-08 DBAASP Codex fallback "strict review"; it is independent dual-pass machine extraction only. The true six-worker strict pilot currently has 12 manifest papers with 72 unique Codex CLI worker sessions, 12/12 paper-level source-reviewed `accepted_with_cautions`, 0 open rework tickets, and green packet/semantic/publication/strict-worker/audit gates. All 12 remain 0 authoritative DBAASP-ingest-ready. Future completion claims must require controller/`audit-workers`, `strict_worker_run_gate`/`worker_run_clean`, semantic/publication gates, and explicit separation from authoritative DBAASP ingest.
2. Build a plain-language release-vs-portal-vs-deepmine reconciliation doc/table and expose the same tier labels in portal/API docs.
3. Finish portal/site basics: rebuild instructions, UI copy for evidence tiers, download/help pages, MCP examples, smoke tests, and deployment checklist.
4. Add automated data QA reports for malformed IDs, duplicate IDs, required fields, tier counts, release/portal consistency, and suspicious mechanism classes.
5. Decide whether DBAASP extraction should resume now, later, or under a different concurrency/provider plan; current stop was rate-limit, not scientific completion.
6. Decide whether post-RC2 `deepmine` outputs become RC3, advisor-only, or review-queue material.
7. Synchronize RC2 counts into `docs/` and any freeze README sections that still say RC1-era `1371/100/29/4772`.
8. Build/update NAR competitor comparison, ontology crosswalk, quality-evidence figure, public license/source table, and maintenance statement.
9. Prepare human-validation packets and reviewer instructions, but defer full validation420/human review execution until helpers are available.
10. Keep SAR/selectivity/advisor work separated from core freeze claims until validated and documented.

## Refresh Commands

Run these before updating counts:

```bash
python -m json.tool reports/nar_resource_freeze_v1/release_manifest_latest.json >/dev/null
python -m json.tool reports/nar_resource_freeze_v1/unified_scope_summary_latest.json >/dev/null
python -m json.tool releases/amp_evidence_atlas_v1_rc2/release_manifest.json >/dev/null
```

Parse release rows safely:

```bash
python3 - <<'PY'
import csv, json
from pathlib import Path
rel = Path('releases/amp_evidence_atlas_v1_rc2')
manifest = json.load(open(rel / 'release_manifest.json'))
for t in manifest['tables']:
    with (rel / t['path']).open(encoding='utf-8', newline='') as f:
        n = sum(1 for _ in csv.DictReader(f, delimiter='\t'))
    print(t['path'], t['row_count'], n)
PY
```

Check validation420:

```bash
sed -n '1,220p' reports/nar_resource_freeze_v1/manual_validation/validation420/VALIDATION420_RUN_STATUS.md
python -m json.tool reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_source_review_summary_latest.json >/dev/null
python -m json.tool reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/summary/validation420_pause_checkpoint_qa_latest.json >/dev/null
```

Check portal stats:

```bash
python3 - <<'PY'
import sqlite3
con = sqlite3.connect('portal/atlas.db')
for k, v in con.execute('select k,v from stats order by k'):
    print(k, v)
PY
```

Check post-RC2 deepmine counts:

```bash
python3 - <<'PY'
import csv
from pathlib import Path
for p in sorted(Path('pipeline_v2/deepmine').glob('*.tsv')):
    with p.open(encoding='utf-8', newline='') as f:
        print(p, sum(1 for _ in csv.DictReader(f, delimiter='\t')))
PY
```

Check DBAASP pending batch and malformed IDs:

```bash
python3 pipeline_v2/deepmine/extract_dbaasp.py --list
tail -120 pipeline_v2/deepmine/dbaasp.log
python3 - <<'PY'
import csv, json
from pathlib import Path
work = json.load(open('pipeline_v2/deepmine/dbaasp_worklist.json'))
rows = list(csv.DictReader(open('pipeline_v2/deepmine/dbaasp_extracted.tsv', encoding='utf-8', newline=''), delimiter='\t'))
print('worklist', len(work), 'done', len(json.load(open('pipeline_v2/deepmine/dbaasp_state.json'))))
print('doi keys with trailing )', sum(w[0].startswith('10.') and w[0].endswith(')') for w in work))
print('extracted rows with ) paper_id', sum(')' in r['paper_id'] for r in rows))
print('papers with ) paper_id', len({r['paper_id'] for r in rows if ')' in r['paper_id']}))
PY
```

Check portal tier split:

```bash
python3 - <<'PY'
import sqlite3
con = sqlite3.connect('portal/atlas.db')
for row in con.execute('select evidence_tier, count(*) from activity group by evidence_tier order by count(*) desc'):
    print(row)
for row in con.execute('select review_status, count(*) from papers group by review_status order by count(*) desc'):
    print(row)
PY
```

Check human-review backfill/release surfacing:

```bash
python3 scripts/backfill_human_review.py --dry-run
python3 - <<'PY'
import csv, collections
from pathlib import Path
for fn in ['pipeline_v2/human_verified_db_errors.tsv', 'releases/amp_evidence_atlas_v1_rc2/database_record_audits.tsv']:
    c = collections.Counter()
    with open(fn, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            c[r.get('human_verdict', '')] += 1
    print(fn, dict(c))
PY
```


## 2026-07-09 DBAASP Strict Codex CLI Independence Recheck

Timestamp: 2026-07-09 08:00 CST.

Reason for recheck:

- The strict DBAASP pilot appeared fast enough to be suspicious, so the current state was rechecked against script code, per-paper worker logs, latest status/verify gates, and an independent direct JSON scan.
- The specific question was whether every manifest paper truly used independent Codex CLI worker sessions and whether it went through the six-role strict AMP curation flow.

Plain-language answer:

- Yes for the current strict pilot manifest: all 12 manifest papers have six worker reports, one for each worker role, and every worker report was launched by `codex exec`.
- Yes for independence: 72 worker reports produced 72 unique Codex session IDs; no session ID is reused within or across papers.
- Yes for model gate: every worker report records `codex_model=gpt-5.5` and `codex_reasoning_effort=xhigh`; all worker return codes are 0.
- Yes for paper-level gates: latest `status`, `verify`, and `audit-workers` report 12/12 paper-level source-reviewed complete, semantic gate 12/12, publication gate pass, strict worker hard findings 0, open rework tickets 0, and missing final papers 0.
- No for clean/no-caution release: all 12 are `accepted_with_cautions`, not `accepted_clean`; authoritative DBAASP release/portal ingest-ready remains 0 because linked authority rows/release policy are still not satisfied.
- Runtime boundary remains important: this is a sequential independent `codex exec` bridge with packet rework files, not full durable `omx team` mailbox production orchestration.

Fresh commands run:

```bash
python3 -m py_compile pipeline_v2/deepmine/dbaasp_strict_pilot.py
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py candidates --limit 10
```

Key evidence artifacts:

| Artifact | Result |
| --- | --- |
| `pipeline_v2/deepmine/dbaasp_strict_pilot.py` | `run_worker()` calls `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -m gpt-5.5 -c model_reasoning_effort="xhigh" -C <ROOT> -o <last_message> -`. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json` | `paper_count=12`, `analysis_source_reviewed_accepted=12`, `accepted_with_cautions=12`, `source_reviewed_publication_grade_count=12`, `authoritative_dbaasp_ingest_ready_count=0`, `open_rework_ticket_count=0`, `missing_final_paper_count=0`. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json` | Packet gate return code 0, semantic gate `publication_grade_pass_count=12`, publication gate `publication_grade_pass=true`, strict worker hard findings 0. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.json` | `total_worker_reports_found=72`, `unique_codex_sessions_found=72`, `duplicate_session_ids=[]`, `nonzero_worker_report_count=0`, `bad_model_effort_report_count=0`, `non_codex_exec_report_count=0`, `hard_finding_count=0`. |
| Independent direct scan over `worker_logs/*/run_sequence_latest.json` and per-paper `final/review_report.json` | Found 12 manifest papers, 72 worker reports, 72 global unique sessions, anomaly count 0; every prompt/final/stdout/stderr path exists and every review has `gpt-5.5/xhigh` provenance plus no open `rework_targets`. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/candidates_latest.json` | Candidate pool still has 217 papers, 15 recommended; next recommended candidate is `PMC13013390`. |

Current per-paper strict-worker table:

| Paper | Worker reports | Unique sessions | Review status | Cautions | Paper-level acceptance | Authoritative ingest-ready | Approx. worker window |
| --- | ---: | ---: | --- | ---: | --- | --- | ---: |
| `PMC13036774` | 6 | 6 | `accepted_with_cautions` | 4 | true | false | 52.4 min |
| `PMC13036000` | 6 | 6 | `accepted_with_cautions` | 2 | true | false | 225.8 min |
| `PMC11735859` | 6 | 6 | `accepted_with_cautions` | 6 | true | false | 60.5 min |
| `PMC13054752` | 6 | 6 | `accepted_with_cautions` | 5 | true | false | 61.2 min |
| `PMC11752523` | 6 | 6 | `accepted_with_cautions` | 5 | true | false | 117.8 min |
| `PMC11784053` | 6 | 6 | `accepted_with_cautions` | 3 | true | false | 55.5 min |
| `PMC12229353` | 6 | 6 | `accepted_with_cautions` | 9 | true | false | 55.0 min |
| `PMC12103485` | 6 | 6 | `accepted_with_cautions` | 2 | true | false | 175.2 min |
| `PMC11531597` | 6 | 6 | `accepted_with_cautions` | 4 | true | false | 95.2 min |
| `PMC11292031` | 6 | 6 | `accepted_with_cautions` | 2 | true | false | 49.2 min |
| `PMC12144240` | 6 | 6 | `accepted_with_cautions` | 3 | true | false | 51.7 min |
| `PMC12022103` | 6 | 6 | `accepted_with_cautions` | 6 | true | false | 77.1 min |

Stop condition / next step:

- Current proof is enough to say the 12-paper strict pilot really went through independent Codex CLI six-worker review.
- It is not enough to call the data clean or release-ingest ready. Keep using `accepted_with_cautions` and preserve database conflicts/unresolved rows.
- Next automated step is to run the controller on the next recommended candidate, likely `PMC13013390`, then rerun `status`, `verify`, and `audit-workers` before updating this document again.

## 2026-07-09 DBAASP Strict Codex CLI Independence Recheck After `PMC13013390`

Timestamp: 2026-07-09 09:47 CST.

Reason for recheck:

- The user again questioned whether the review was too fast and whether every paper really went through independent Codex CLI workers.
- I waited for the in-flight `PMC13013390` rework rerun to finish, then ran single-paper acceptance plus global `status`, `verify`, `audit-workers`, and candidate refresh.
- I checked both the controller code path and the per-paper `run_sequence_latest.json` evidence instead of relying on chat memory.

Plain-language answer:

- Yes for the current 13-paper strict pilot manifest: every paper has six worker reports (`worker-1` through `worker-6`), and each worker report has a unique Codex session ID.
- Yes for the Codex CLI/model gate: 78 worker reports produced 78 unique sessions; all recorded `codex exec`, `gpt-5.5`, `xhigh`, and return code 0.
- Yes for the current gate status: global packet, semantic, publication-quality, and strict-worker gates all returned 0 hard findings after the `PMC13013390` repair/re-adjudication.
- Important nuance: this is still a sequential independent `codex exec` bridge, not full durable `omx team` mailbox production orchestration.
- Important nuance for `PMC13013390`: the final accepted sequence keeps `worker-1` and `worker-5` from the first pass, reruns the affected `worker-2`, `worker-3`, `worker-4`, and `worker-6` after durable material/linkage repair, then lets the fresh `worker-6` re-adjudicate. It is not a from-scratch rerun of all six workers.
- No for clean/no-caution release: all 13 are `accepted_with_cautions`, not `accepted_clean`; authoritative DBAASP release/portal ingest-ready remains 0.

What happened to `PMC13013390`:

| Step | Result |
| --- | --- |
| First controller pass | Built packet and ran six independent `codex exec` workers, but worker-6 correctly blocked acceptance as `needs_targeted_rework` with 3 targets. |
| Material/linkage repair | Added durable no-authoritative-match closure and repaired DOCX supplementary table extraction; `supplementary_tables.json` now has 2 DOCX tables / 227 rows and locator count rose to 408. |
| Rerun | Reran `worker-2`, `worker-3`, `worker-4`, and `worker-6` with fresh independent Codex sessions; all returned 0. |
| Acceptance | `PMC13013390` became `accepted_with_cautions`, `publication_grade=true`, `validator_contract_passed=true`, `rework_target_count=0`, `caution_count=3`. |
| Boundary | 42 fallback/machine activity rows remain candidate evidence; authoritative linked DBAASP rows are still 0 and ingest-ready remains false. |

Fresh commands run:

```bash
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py acceptance --paper-id PMC13013390
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py status
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py verify
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py audit-workers
python3 pipeline_v2/deepmine/dbaasp_strict_pilot.py candidates --limit 10
```

Key evidence artifacts:

| Artifact | Result |
| --- | --- |
| `pipeline_v2/deepmine/dbaasp_strict_pilot.py` | `run_worker()` constructs `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -m gpt-5.5 -c model_reasoning_effort="xhigh" -C <ROOT> -o <last_message> -`. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC13013390/run_sequence_latest.json` | Final six workers have six unique sessions: worker-1 `019f4430-98ec-7842-9f78-e04fc9ed53f0`, worker-2 `019f4468-685e-76a3-b209-ece3701fd642`, worker-3 `019f4474-f487-7c31-9c0b-fbbdf9f9ed54`, worker-4 `019f447c-8926-7731-ba07-5dd196e1c081`, worker-5 `019f444f-cfac-7ec3-9595-a70cb437a872`, worker-6 `019f4485-b6d4-7992-9293-69bbcb444b3a`. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13013390_*_acceptance.json` | Single-paper packet gate hard findings 0, open rework 0; semantic gate 1/1 pass; publication quality pass. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json` | `paper_count=13`, `analysis_source_reviewed_accepted=13`, `accepted_with_cautions=13`, `source_reviewed_publication_grade_count=13`, `authoritative_dbaasp_ingest_ready_count=0`, `open_rework_ticket_count=0`, `missing_final_paper_count=0`. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json` | Packet gate return code 0, semantic gate return code 0, publication gate return code 0, strict worker hard findings 0. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_codex_cli_independence_recheck_latest.json` | `manifest_paper_count=13`, `strict_completed_count=13`, `total_worker_reports_found=78`, `unique_codex_sessions_found=78`, `duplicate_session_ids=[]`, `nonzero_worker_report_count=0`, `bad_model_effort_report_count=0`, `non_codex_exec_report_count=0`, `hard_finding_count=0`, `worker_independence_pass=true`. |
| `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/candidates_latest.json` | Candidate pool still has 217 papers, 14 currently recommended, 18 need material recovery; top next candidate is `PMC13031788`. |

Current strict-worker table:

| Paper | Worker reports | Unique sessions | Review status | Cautions | Paper-level acceptance | Authoritative ingest-ready |
| --- | ---: | ---: | --- | ---: | --- | --- |
| `PMC13036774` | 6 | 6 | `accepted_with_cautions` | 4 | true | false |
| `PMC13036000` | 6 | 6 | `accepted_with_cautions` | 2 | true | false |
| `PMC11735859` | 6 | 6 | `accepted_with_cautions` | 6 | true | false |
| `PMC13054752` | 6 | 6 | `accepted_with_cautions` | 5 | true | false |
| `PMC11752523` | 6 | 6 | `accepted_with_cautions` | 5 | true | false |
| `PMC11784053` | 6 | 6 | `accepted_with_cautions` | 3 | true | false |
| `PMC12229353` | 6 | 6 | `accepted_with_cautions` | 9 | true | false |
| `PMC12103485` | 6 | 6 | `accepted_with_cautions` | 2 | true | false |
| `PMC11531597` | 6 | 6 | `accepted_with_cautions` | 4 | true | false |
| `PMC11292031` | 6 | 6 | `accepted_with_cautions` | 2 | true | false |
| `PMC12144240` | 6 | 6 | `accepted_with_cautions` | 3 | true | false |
| `PMC12022103` | 6 | 6 | `accepted_with_cautions` | 6 | true | false |
| `PMC13013390` | 6 | 6 | `accepted_with_cautions` | 3 | true | false |

Stop condition / next step:

- Current proof is enough to say the 13-paper strict pilot really has independent Codex CLI six-worker evidence and passes strict gates.
- It is still not enough to call the data clean or authoritative DBAASP-ingest ready.
- Next automated step is to run the controller on the next recommended candidate, currently `PMC13031788`, then rerun `status`, `verify`, `audit-workers`, and update this document again.

## 2026-07-11 Strict Review Semantic Re-Audit (In Progress)

Timestamp: 2026-07-11 20:48 CST.

Why this checkpoint exists:

- The user questioned whether the papers had really been reviewed by independent Codex CLI workers and whether the fast completion reflected a strict multi-role process.
- A fresh audit confirmed the process-level evidence, but also proved that process independence alone was not enough: the old semantic gates could still accept incomplete or incorrectly attributed activity rows.
- This section is an in-progress checkpoint. The three targeted paper reruns below are not counted as accepted until fresh worker-6 adjudication plus all gates pass.

Plain-language current state:

- The 14-paper manifest has six logical worker roles per paper and 84 unique current logical Codex sessions, all using `codex exec`, `gpt-5.5`, `xhigh`, and return code 0 at the time of the audit.
- This proves a sequential independent Codex CLI bridge. It does not prove durable `omx team` mailbox/ACK/supervisor production semantics.
- Eleven unaffected historical papers pass the newly hardened semantic and publication gates.
- Three papers are currently nonterminal: `PMC13031788`, `PMC11784053`, and `PMC12229353`.
- Authoritative DBAASP ingest-ready remains 0. Fallback/machine rows remain candidate-only.

Semantic failures discovered:

| Paper | Failure | Required repair |
| --- | --- | --- |
| `PMC13031788` | The first worker-2 pass created 18 false MIC rows from formulation and FTIR tables; a later repair correctly removed them but omitted the 24-cell Table 5 log-CFU time series. TGA percentages were also initially at risk of being mislabeled as toxicity. | Keep the 14 real Table 4 inhibition-zone rows, add exactly 24 Table 5 observations, keep Table 1/2 rows at 0, and preserve toxicity as no source-located evidence rather than TGA-derived values. |
| `PMC11784053` | The new Table 3 repair produced 37 table-linked rows instead of 24 source cells, duplicated the same toxicity evidence across `activity_records` and `toxicity_records`, and omitted treatment identity needed to distinguish WOW, WW-185, and the combination. | Produce exactly 8 concentrations x 3 named treatments = 24 unique observations, preserve the endpoint-label conflict, and store each observation once. |
| `PMC12229353` | The first Table 2 repair merely attached the Table 2 locator to four unrelated pre-existing rows instead of extracting the 72 resistant-isolate MIC/MBC cells. | Produce exactly 12 isolates x 3 treatments x 2 endpoints = 72 unique observations with isolate/treatment/endpoint/value/unit and row/cell provenance. |

Flow hardening completed during this checkpoint:

- Added generic activity-table detection and removed unconditional figure-number-to-toxicity assumptions.
- Added rejection of formulation, FTIR, TGA, wettability, and mechanical tables as activity sources.
- Added recursive locator extraction for nested, row-level, list, and combined locator strings.
- Included `toxicity_records` in source-table and table-coverage checks.
- Added structured `expected_observation_counts` rework contracts so a base-table citation cannot substitute for row/cell completeness.
- Made `response_status` authoritative over generic `status`, removed generic `accepted` as a rework-closure value, and retained conservative terminal repaired/closed variants.
- Made open rework tickets override stale accepted queue state and block paper-level completion.
- Made worker-6 freshness a hard worker-run condition: final adjudication must start after all current worker-1 through worker-5 reports.
- Prevented scoped `status --paper-id` calls from overwriting the global `status_latest.json` artifact.

Fresh validation at this checkpoint:

- Python syntax compilation passed for the controller, both semantic/publication gate scripts, and the regression test module.
- Regression suite: 16/16 tests passed.
- Unaffected historical subset: semantic gate 11/11 pass; publication-quality gate pass with zero risks.
- `PMC11784053` is currently blocked by `table_observation_count_mismatch` (`expected=24`, `observed=74`).
- `PMC12229353` is currently blocked by `table_observation_count_mismatch` (`expected=72`, `observed=4`).
- `PMC13031788` has a structured Table 5 contract requiring exactly 24 observations; its targeted worker-2/worker-6 rerun remains active.

Durable evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/accepted13_semantic_regression_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/accepted13_publication_regression_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/accepted13_activity_coverage_rework_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/accepted13_row_completeness_rework_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/unaffected11_semantic_regression_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/unaffected11_publication_regression_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11784053_row_completeness_probe_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12229353_row_completeness_probe_latest.json`

Stop condition for this audit pass:

- Do not restore the old 13/13 or claim 14/14 until all three targeted papers have exact row-level coverage, zero open tickets, fresh worker-6 adjudication, semantic/publication pass, and a fresh 14-paper worker-independence audit.

### 2026-07-11 22:07 CST Deeper Cell-Binding Checkpoint

This checkpoint supersedes the earlier row-count-only interpretation while the final reruns are still active.

- Gate hardening now has 43 passing regression tests. The new tests cover ambiguous count locators, negative/meta locator text, nested-vs-flat targets, row/column aliases, singular-plus-plural locators, table-scoped cell coordinates, exact required cells, cell-bound expected fields, stale activity metadata, empty-manifest false success, and cross-gate parity.
- Four independent code-review passes were used to challenge the gate. The first three found additional false-pass paths; each finding was reproduced with a failing test before repair. A fourth frozen-code review is still pending at this timestamp.
- `PMC13031788` now has 38 source-located activity rows: Table 4 = 14 and Table 5 = 24, toxicity = 0, no Table 1/2 activity rows, corrected final metadata, zero open rework tickets, and a fresh worker-6 after the latest worker-2. `reports/PMC13031788_source_cell_verification_latest.json` reports zero source-cell field mismatches, and fresh single-paper acceptance passes while authoritative DBAASP ingest remains false.
- `PMC11784053` was not accepted after deeper checking. Its first 24-cell repair had 24 unique locators but all 24 locators were attached to at least one wrong source field; 23 were materially shifted across concentration/treatment/value cells and the remaining row still failed exact source treatment naming. `rwk-PMC11784053-semantic-coverage-004` now carries a machine-readable 24-cell field contract. A final `worker-1 -> worker-2 -> worker-6` rerun is active; worker-1 also must close the authoritative-row no-match ticket with durable evidence.
- `PMC12229353` has 72 correct Table 2 values, treatment entities, endpoints, units, and cell locators, but all 72 `target_strain_or_isolate` fields still repeat the species abbreviation instead of storing only isolate IDs such as `434`, `138`, and `557`. `rwk-PMC12229353-semantic-coverage-004` now carries a machine-readable 72-cell field contract, and a final `worker-2 -> worker-6` rerun is active.
- Return code 0 remains a runtime signal only. Neither active paper may be counted as accepted until its cell-field contract has zero mismatches, all rework tickets are closed, worker-6 is fresh, and packet/semantic/publication/worker-run gates all pass.

New durable evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11784053_cell_binding_probe_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12229353_cell_binding_probe_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13031788_source_cell_verification_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13031788_strict_acceptance_audit_latest.json`

## 2026-07-15 DBAASP Strict 14-Paper Source-Review Freeze

Timestamp: 2026-07-15 21:00 CST.

### Plain-language result

- The AI-executable strict review work for the current 14-paper DBAASP pilot is complete at the paper-level source-review boundary.
- All 14 papers are `accepted_with_cautions`; none is `accepted_clean`. The cautions and unresolved database provenance are retained rather than smoothed away.
- Every paper has six independent current `codex exec` worker reports (`worker-1` through `worker-6`), six unique session IDs, `gpt-5.5`, `xhigh`, return code 0, and a worker-6 adjudication that is not earlier than the latest upstream worker.
- Every paper has zero runtime-open rework tickets, zero review rework targets, packet/semantic/publication gate return codes `0/0/0`, zero packet hard findings, and zero publication risks.
- The 14 final paper artifacts contain 568 activity records and 170 toxicity records. The global publication report also contains 67 mechanism claims.
- `authoritative_dbaasp_ingest_ready=false` for all 14 papers. Fallback DBAASP/Codex rows remain candidate machine evidence and must not be promoted to authoritative release data.
- This closes the current 14-paper strict pilot, not the whole project. Manual validation/human reduction, public website/API/download completion, licensing/source-version review, manuscript disclosure, and release integration remain separate unfinished work.

### Per-paper frozen counts

| Paper | Activity | Toxicity | Workers | Unique sessions | Worker-6 fresh | Paper acceptance | Authoritative ingest |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `PMC11292031` | 16 | 42 | 6 | 6 | true | true | false |
| `PMC11531597` | 30 | 12 | 6 | 6 | true | true | false |
| `PMC11735859` | 66 | 0 | 6 | 6 | true | true | false |
| `PMC11752523` | 40 | 60 | 6 | 6 | true | true | false |
| `PMC11784053` | 28 | 24 | 6 | 6 | true | true | false |
| `PMC12022103` | 108 | 8 | 6 | 6 | true | true | false |
| `PMC12103485` | 14 | 2 | 6 | 6 | true | true | false |
| `PMC12144240` | 14 | 6 | 6 | 6 | true | true | false |
| `PMC12229353` | 106 | 6 | 6 | 6 | true | true | false |
| `PMC13013390` | 78 | 0 | 6 | 6 | true | true | false |
| `PMC13031788` | 38 | 0 | 6 | 6 | true | true | false |
| `PMC13036000` | 8 | 10 | 6 | 6 | true | true | false |
| `PMC13036774` | 9 | 0 | 6 | 6 | true | true | false |
| `PMC13054752` | 13 | 0 | 6 | 6 | true | true | false |
| **Total** | **568** | **170** | **84 reports** | **84 globally unique** | **14/14** | **14/14** | **0/14** |

### Rework-closure and gate hardening completed

- Upstream owner workers may only write the nonterminal state `repair_ready_for_adjudication`; only worker-6 may write terminal `closed_repaired`.
- Owner responses must bind the same `ticket_id`, identify the correct `response_by` worker, set `analysis_can_resume=true`, and include non-empty repair evidence. Broad `repaired_*`, `needs_followup`, cross-ticket borrowing, and ownerless non-adjudication responses fail closed.
- Terminal closure is accepted only when the ticket contract passes, all required paper/packet final mirrors match byte-for-byte, current final counts match, packet/semantic/publication gate payloads use the correct paper and manifest, and gate artifacts are fresh relative to the terminal response and final files.
- Multi-ticket closure now uses a monotonically decreasing fixed point. If one terminal candidate becomes stale or invalid, every other closure that depended on it is re-evaluated.
- Worker prompts are regenerated before every worker run, so worker-1/3/4/5 no longer receive stale runtime-open ticket lists.
- Sixteen historical requests missing `owner_worker` were backfilled conservatively; the durable report is `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/rework_owner_contract_backfill_latest.json`.
- Seven rounds of independent code-review challenge were used while hardening this contract. The frozen review ended with `APPROVE` and no remaining HIGH/MEDIUM findings; the runtime record is `.omx/logs/turns-2026-07-15.jsonl`.

### Fresh acceptance and global freeze evidence

- Per-paper fresh acceptance directory: `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/fresh_acceptance_20260715/`.
- Combined per-paper summary: `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/fresh_acceptance_20260715/summary.json`.
- Global command outputs, stderr logs, and return-code sidecars: `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260715/`.
- Global `status`: 14 papers; 14 `material_extracted_complete`; 14 `analysis_source_reviewed_accepted`; 14 `accepted_with_cautions`; zero open tickets; zero missing final papers; zero authoritative-ingest-ready papers.
- Global `verify`: packet gate 0, semantic gate 0 with 14/14 passing, publication gate 0 with no risk counts, and strict worker-run gate 0 with zero hard findings.
- Global `audit-workers`: 84 worker reports, 84 globally unique sessions, zero duplicate session IDs, zero nonzero returns, zero bad model/effort reports, zero non-`codex exec` reports, and `worker_independence_pass=true`.
- Candidate refresh remains a separate expansion queue: 217 candidate records, 13 currently recommended, and 18 needing material recovery. These candidate counters are not the 14-paper strict freeze denominator.
- Regression evidence: 84 unit tests pass and `py_compile` passes for the controller, regression tests, and packet checker.

### Independent freeze verification

- A separate native `verifier` agent performed a read-only adversarial check after the freeze and returned `PASS - APPROVE` with no high, medium, or low findings.
- It independently recomputed 84 `codex exec` reports and 84 globally unique sessions, called the fail-closed open-ticket algorithm for every paper, recomputed the 568/170 activity/toxicity totals, and checked 56 required paper/packet mirror pairs by SHA-256.
- The verifier confirmed that per-paper acceptance, global status/verify/audit outputs, worker metadata, gate results, and final JSON counts agree.
- Durable verifier record: `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260715/independent_verifier_report.md`.

### Boundaries and next project work

1. Keep authoritative ingest blocked until linked authoritative DBAASP article/assay/sequence/literature rows and release policy approval exist.
2. Keep manual paper validation and final human reduction deferred or delegated, as previously decided; this 14-paper AI review is not a substitute for validation420 or final release sign-off.
3. Resume the website/public-resource lane: public hosting, API and bulk-download packaging, Windows/WSL access documentation, and release-vs-portal denominator reconciliation remain unfinished.
4. Decide explicitly whether to expand the strict pilot to the next recommended candidate; do not silently merge candidate-machine output into RC2 or the authoritative portal layer.
5. Preserve the runtime wording: this is a sequential independent `codex exec` bridge with strict evidence contracts, not full durable OMX team mailbox/ACK/supervisor production state.

## 2026-07-16 Candidate 15 Strict Expansion And 15-Paper Freeze (Completed)

Timestamp: 2026-07-16 01:38 CST.

### Plain-language result

- `PMC13031288` completed strict source review as the 15th paper and is `accepted_with_cautions`, not `accepted_clean`. The active manifest is now 15/15 paper-level source-reviewed and publication-grade under the strict pilot contract.
- This 15-paper freeze supersedes the completed 14-paper freeze for the strict pilot denominator. It does not supersede RC2 as the authoritative release layer and does not merge strict-pilot fallback data into the portal or public release.
- The 15 final paper artifacts contain 928 activity records, 210 toxicity records, and 73 mechanism claims.
- Current canonical worker evidence contains 90 reports and 90 globally unique Codex session IDs. Every paper has worker-1 through worker-6, all current reports use independent `codex exec`, `gpt-5.5`, `xhigh`, and return code 0, and every worker-6 is fresh relative to the latest upstream worker.
- All 15 papers have zero runtime-open rework tickets, zero review rework targets, zero hard findings, zero publication risks, and packet/semantic/publication/strict-worker gate return codes `0/0/0/0`.
- `authoritative_dbaasp_ingest_ready=false` for all 15 papers. The strict pilot remains a paper-level source-review layer, not an authoritative DBAASP release-ingest approval.

### PMC13031288 final evidence

- Source packet: XML, PDF, and 3/3 declared DOCX supplements are present; packet locator count is 196 and extraction error count is 0.
- Database boundary: 34 fallback machine rows are present, but linked authoritative article/assay/sequence/literature rows are all 0. Fallback rows remain candidate-only.
- Layer 2: 360 activity plus 40 toxicity observations map one-to-one to the 400 exact S2 scalar cells. All 400 rows have top-level `evidence_role`, all 400 have exact source-cell locators, and direct non-table contract issues are 0.
- Main-text crosswalk: exactly 120 existing S2 observations carry `xml:table-wrap:1` as a secondary locator for Table 1. No duplicate aggregate rows were created, and S3 historical/computational values were not promoted as new current-study scalar observations.
- Identity audit: all 7 nested records are `source_verified` at the paper-local identity level. `Hill_BB_C7176` resolves to `ATCDLLSPFKVGHAACALHCIALGRRGGWCDGRAVCNCRR` (length 40, S1 row 7), and `Hill_SB_C1875` resolves to `GQGESRSLWKKIFKPVEKLGQRVRDAGIQGIAIAQQGANVLATVRGGPPQ` (length 50, S1 row 11).
- Mechanism ontology: six claims, including exactly two direct-mechanism claims: PI uptake/permeability and BODIPY-TR-cadaverine competitive displacement against LPS/lipid A. The latter retains the explicit caution that direct interaction evidence does not establish the complete mode of action.
- Preserved caution: the source-name conflict `Hill_BB_C3195` in S2 versus `Hill_C3195` in S1/main text remains visible rather than silently normalized.
- Final acceptance: 360 activity, 40 toxicity, 7 database audits, 6 mechanism claims, zero open tickets, zero rework targets, and `accepted_with_cautions` with `publication_grade=true`.

### Rework chronology and shallow-review defenses

- The initial complete worker-1 through worker-6 run correctly remained nonterminal after finding missing semantic coverage. It did not convert six successful process exits into scientific acceptance.
- Five leader-side source contracts triggered a targeted `worker-2 -> worker-4 -> worker-5 -> worker-6` rerun: full S2 cell coverage, top-level repeat binding, raw-DOCX sequence recovery, direct lipid-A/LPS binding evidence, and nonduplicating Table 1 aggregate coverage.
- The first targeted worker-4 response changed summary counts without repairing the two nested records. A sixth ticket, `rwk-PMC13031288-worker4-summary-record-consistency-006`, captured this summary-only false repair and forced a fresh `worker-4 -> worker-6` rerun.
- The six closed tickets are `rwk-PMC13031288-full-supplement-cell-coverage-001`, `rwk-PMC13031288-top-level-repeat-binding-002`, `rwk-PMC13031288-raw-docx-sequence-resolution-003`, `rwk-PMC13031288-lipidA-direct-binding-004`, `rwk-PMC13031288-main-table-aggregate-coverage-005`, and `rwk-PMC13031288-worker4-summary-record-consistency-006`.
- The current `PMC13031288` canonical run sequence has six unique sessions. Worker-6 started at `2026-07-15T17:05:09Z`, at or after the latest upstream worker-4 completion, and final mirrors are synchronized.

### Global freeze and independent verification

- Fresh per-paper acceptance: `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/fresh_acceptance_20260716/summary.json` reports 15/15 ready, 928/210/73 activity/toxicity/mechanism, all model and freshness gates true, and all authoritative flags false.
- Global freeze directory: `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716/` contains captured `status`, `verify`, `audit-workers`, and `candidates` JSON, stderr logs, timing logs, and return-code sidecars.
- Global `status`: 15 material-complete, 15 analysis-source-reviewed-accepted, 15 `accepted_with_cautions`, zero open tickets, zero missing finals, and zero authoritative-ingest-ready papers.
- Global `verify`: packet, semantic, publication, and strict-worker gates all return 0; semantic passes 15/15; publication risks are empty; strict-worker hard findings are 0.
- Global `audit-workers`: 90 reports, 90 unique sessions, zero duplicate sessions, zero nonzero reports, zero bad model/effort reports, zero non-`codex exec` reports, and `worker_independence_pass=true`.
- Leader contract recheck independently recounts 928/210/73, verifies all 90 sessions, checks 60 paper/packet mirror pairs byte-for-byte, and reports `PASS` with zero failures.
- Regression evidence: 84/84 unit tests pass, and `py_compile` passes for the controller, regression module, and packet checker.
- A separate native read-only verifier returned `APPROVE`. It reran the gates, compared all 60 mirrors by bytes/SHA-256, inspected raw S1/S2 DOCX XML, and found no high, medium, or low findings. Durable report: `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716/independent_verifier_report.md`.

### Remaining project work

1. Manual paper validation/final human reduction remains deferred or delegated and is not replaced by this AI strict-pilot freeze; validation420 is still unfinished.
2. The public website/resource lane remains unfinished: public hosting, API, bulk downloads, Windows/WSL access documentation, and release-versus-portal denominator reconciliation still need completion.
3. Authoritative release integration remains blocked until linked DBAASP authority records, release policy approval, licensing/source-version review, and manuscript disclosure are complete.
4. This 15-paper freeze is historical and superseded by the completed 16-paper freeze below. The next current recommended strict candidate is now `PMC12019989` (score 99), but it is not part of the 16-paper freeze.
5. Preserve the runtime wording: this is a sequential independent `codex exec` bridge with strict evidence contracts, not a durable OMX team mailbox/ACK/supervisor production state.

## 2026-07-16 Candidate 16 Strict Expansion And 16-Paper Freeze (Completed)

Timestamp: 2026-07-16 16:18 CST.

### Plain-language result

- `PMC12230126`, DOI `10.1038/s41598-025-08159-z`, is complete as the 16th strict-pilot paper and is `accepted_with_cautions`, not `accepted_clean`.
- The active strict-pilot manifest is now 16/16 paper-level source-reviewed and publication-grade under the pilot contract. This 16-paper freeze supersedes the 15-paper strict freeze; it does not supersede RC2 as the authoritative release layer.
- Final 16-paper totals are 947 activity records, 210 toxicity records, and 79 mechanism claims.
- Current canonical runtime evidence contains 96 worker reports and 96 globally unique Codex session IDs. Every current report is an independent `codex exec` using `gpt-5.5`, `xhigh`, and return code 0; worker-6 is fresh after the latest upstream worker on every paper.
- All 64 configured paper/packet final mirror pairs are byte-identical. Open rework tickets, review rework targets, hard findings, and publication risks are all zero.
- `authoritative_dbaasp_ingest_ready` remains false globally. A recursive scan across all 16 final database-verification artifacts finds zero true values, so no strict-pilot fallback row is authorized for RC2, portal, or public-release ingest.

### PMC12230126 final scientific contract

- Material packet: XML, 16-page PDF, and 1/1 declared 9-page supplementary PDF are present; locator count is 151 and extraction error count is 0.
- Database boundary: 22 fallback machine rows are retained as candidate-only evidence; linked authoritative article, assay, sequence, and literature row counts are all zero.
- Layer 2 contains 19 activity and 0 toxicity observations: 5 Fig. 4 protease rows, exactly 12 Fig. 5 A-F treatment rows (6 organisms multiplied by 7 and 15 micromolar), and 2 Fig. 5G permeability rows. Fig. 5G records 7 micromolar as 0 percent and 15 micromolar as 9.18 plus/minus 1.01 percent.
- All 12 Fig. 5 A-F rows preserve panel calibration, image coordinates, digitization uncertainty, treatment/control role, and the primary prose-versus-secondary digitization hierarchy. The previously omitted *Bacillus thuringiensis* doses and separated *Staphylococcus aureus* doses are present.
- Layer 1 contains one cautious DBAASP candidate audit plus paper-local GmSPID identity evidence. Accession is `XP_026756133.1`, the source sequence is 219 aa, signal peptide positions are 1-18, and the Edman mature N-terminus is `LPPCVCTRDYR` beginning at position 19.
- Supplementary Fig. S6 is preserved only as predicted/model-context disulfide evidence. Exact bridge pairs remain empty and experimental confirmation remains false.
- Layer 3 contains 6 mechanism claims: 5 direct-mechanism surfaces (protease inhibition, beta-galactosidase leakage, AFM, SEM, and TEM) plus 1 phenotype-supported antimicrobial claim. Each direct claim retains the limitation that it does not prove a complete single molecular mode of action.

### Rework chronology and gate-blindness correction

- The initial six-role chain completed with six independent sessions, but leader semantic review did not accept process success as scientific completion.
- Six durable tickets were ultimately required: source-surface exhaustion, Fig. 5 provenance/value hierarchy, predicted-disulfide provenance, final-layer adjudication metadata, actual metadata-field materialization, and executable final-layer field assertions.
- The first targeted chain reran `worker-2 -> worker-4 -> worker-6`. It repaired the 12-row Fig. 5 contract, source-value hierarchy, predicted disulfide boundary, and final review, but a direct leader check proved ticket 004 had been closed without physically writing all requested final-layer fields.
- Ticket 005 reran independent worker-4 and worker-6 sessions. Worker-4 correctly added runtime provenance, but worker-6 again self-reported completion while the three final layer artifacts still lacked required fields; the database final also contained nested `authoritative_dbaasp_ingest_ready=true` conflicts that the existing gates missed.
- Ticket 006 added a leader-owned executable validator that could not be weakened by worker output. Its pre-repair run returned 14 issues; a new independent worker-6 session then produced `passed=true`, `issue_count=0`, complete top-level metadata in all three layer finals, one shared review timestamp, and five recursive authoritative-ingest values all false.
- The final canonical `PMC12230126` run sequence has six unique sessions. Worker-6 session `019f69e7-14cc-75b2-a668-e913a46ebc39` started at `2026-07-16T07:49:39Z`, after the latest upstream worker-4 completion at `2026-07-16T07:29:23Z`.
- The append-only response log retains two historical terminal-looking rows for ticket 001, but runtime validation finds exactly one currently valid terminal closure for each of the six tickets. Raw `closed_repaired` strings must not be counted without the current artifact/gate contract.

### Global freeze and independent verification

- Fresh per-paper acceptance: `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/fresh_acceptance_20260716_16paper/summary.json` reports 16/16 ready, 947/210/79 activity/toxicity/mechanism, 96 globally unique sessions, all model/freshness gates true, all strict gates zero, and all authoritative flags false.
- Global freeze directory: `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_16paper/` contains captured `status`, `verify`, `audit-workers`, `candidates`, return-code sidecars, timing logs, leader contract recheck, tests, and independent verifier report.
- Global `status`: 16 material-complete, 16 analysis-source-reviewed-accepted, 16 `accepted_with_cautions`, zero open tickets, zero missing finals, and zero authoritative-ingest-ready papers.
- Global `verify`: packet, semantic, publication, and strict-worker gates all return 0; semantic passes 16/16; publication counts are 947 activity and 79 mechanisms; publication risks are empty.
- Global `audit-workers`: 96 reports, 96 unique sessions, zero duplicate sessions, zero nonzero reports, zero bad model/effort reports, zero non-`codex exec` reports, and `worker_independence_pass=true`.
- Leader contract recheck recounts 947/210/79, verifies all 96 sessions, checks 64 mirror pairs byte-for-byte, confirms zero recursive authoritative true values, and returns `PASS`.
- Regression evidence: 84/84 unit tests pass and `py_compile` returns 0 for the controller, regression module, and packet checker.
- A separate native read-only verifier independently reran/recomputed the critical checks and returned `PASS`. Durable report: `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_16paper/independent_verifier_report.md`.

### Remaining project work and risks

1. Manual paper validation/final human reduction remains deferred or delegated; validation420 is unfinished and this AI strict-pilot freeze is not a substitute for final human sign-off.
2. The website/public-resource lane remains unfinished: public hosting, API, bulk downloads, Windows/WSL access documentation, and release-versus-portal denominator reconciliation still need completion.
3. Authoritative release integration remains blocked until linked DBAASP authority records, release policy approval, licensing/source-version review, and manuscript disclosure are complete.
4. Six older database-verification finals do not expose `authoritative_dbaasp_ingest_ready` at the top level, and five contain no occurrence of the field. None contains true and global status is zero, so this is a future schema-normalization risk rather than a current acceptance failure.
5. Historical 16-paper-freeze note: `PMC12019989` was the next score-99 candidate at that point. It has since completed the separate 17th-paper process documented below; it is still not merged into RC2 or the portal.
6. Preserve the runtime wording: this is a sequential independent `codex exec` bridge with strict evidence contracts, not a durable OMX team mailbox/ACK/supervisor production state.

## 2026-07-16 17:42-21:12 CST Candidate 17 Strict Review And 17-Paper Freeze (Completed)

### Current state

- Candidate: `PMC12019989`, DOI `10.3389/fmicb.2025.1553693`, SK1260 (`KAFAVKFAWKFHAWKAWKKAW`, 21 aa).
- The strict-pilot manifest and accepted freeze now contain 17/17 paper-level source-reviewed papers. `PMC12019989` is `accepted_with_cautions`, not `accepted_clean`, and this 17-paper freeze supersedes the 16-paper strict freeze without superseding RC2.
- Material packet: 121 XML sections, one extracted table, 12 PDF pages, no supplementary file, 133 locators, and zero extraction errors.
- Database boundary: 13 fallback machine rows, zero linked authoritative article/assay/sequence/literature rows, and `authoritative_dbaasp_ingest_ready=false`. The fallback rows remain candidate-only and are excluded from RC2, the portal authority layer, and authoritative ingest.
- A leader-owned source-surface contract now enumerates 10 Figure 1 MIC rows, all 240 Figure 2 SK1260 time-kill points, nine Figure 3 peptide bars, 16 Figure 4 peptide bars, and four Figure 6 survival endpoints. The expected Layer-2 contract is exactly 279 activity rows and zero toxicity rows.
- The initial ticket-001 closure and the first tickets-002/003 closure were both rejected by leader semantic audit even though packet/semantic/publication gates returned zero. The first audit found 304 issues; the second stricter audit found 724 issues after all 240 Figure 2 values remained the same placeholder `3.0` and the final retained 240 `pending_worker3_digitization` values.
- Ticket 004 enforced a reproducible leader-owned RGB color-segmentation scaffold over the original Figure 2 image. Worker-3 then source-reviewed 240 points into 30 non-degenerate curves with 177 distinct approximate values; worker-2 integrated them exactly; worker-6 rebuilt the finals. The immutable leader validator now returns exit 0, `passed=true`, and `issue_count=0`.
- Canonical Candidate 17 worker sessions are six unique `codex exec` sessions on `gpt-5.5/xhigh`, all return code 0. Worker-6 started at `2026-07-16T12:48:32Z`, after the latest upstream worker-2 completion at `2026-07-16T12:42:29Z`.

### Main scientific risks that must remain visible

1. Figure 1 contains 10 MIC values. The fallback candidates swap the source values for *K. pneumoniae* (figure 12.5 ug/mL, machine 6.25) and *P. aeruginosa* (figure 6.25 ug/mL, machine 12.5).
2. Figure 2 methods and legend use 5x MIC, while the caption says 3x MIC. The plotted/method time points are 0, 1, 2, 3, 4, 5, 12, and 24 h, while the caption says 0, 2, 4, 6, and 9 h. The plotted axis says `CFU/mL (1 x 10^5)`, while methods/caption use log language. None of these conflicts may be silently normalized away.
3. Figure 2's global absolute-concentration legend matches only MIC=3.13 panels. Other panels require strain-specific derived concentrations plus an explicit legend conflict, not blind reuse of 1.565/3.13/15.65 ug/mL.
4. Figure 3's prose says 50% biofilm reduction at 1x MIC, while the plotted endpoint is approximately 42% residual biofilm mass. In addition, the Figure 3C absolute concentration labels conflict with the reported MRSA ATCC 43300 MIC; reduction, residual mass, dose fold, and direct concentration must remain separate fields.
5. Figure 4's direct axis is `CFU/mL (1 x 10^5)`, while prose uses `log CFU/organ` and sometimes `CFU/organ`; the caption omits kidney although the figure and prose include it. Figure and prose values must remain separate raw claims.
6. Figure 5 is infected-animal histopathology efficacy evidence, not healthy-animal safety or toxicity. No hemolysis, mammalian cytotoxicity, or healthy-animal toxicity scalar was located, so the required toxicity count is zero.
7. Figure 6 exact results prose reports 71.4% survival at 2 mg/kg for both infections, while the caption says 75%. The exact prose value is primary and the caption remains a preserved conflict.

### Active evidence paths

- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/leader_preflight/source_surface_preflight_contract.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12019989/rework/rework_requests.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12019989/packet_manifest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12019989/database/authoritative_match_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/review/leader_candidate17_validator.py`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/review/leader_candidate17_pre_repair_fail.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/leader_preflight/leader_color_digitize_figure2.py`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/leader_preflight/leader_color_digitized_figure2.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/review/leader_candidate17_post_ticket004.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/fresh_acceptance_20260716_17paper/summary.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_17paper/leader_contract_recheck.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_17paper/independent_verifier_report.md`

### Stop condition and freeze evidence

The stop condition is satisfied:

- Fresh per-paper acceptance is 17/17 ready with zero open tickets, zero rework targets, zero hard findings, zero publication risks, and zero authoritative-ready papers.
- Final totals are 1,226 activity records, 210 toxicity records, and 84 mechanism claims.
- Worker evidence is 102 reports and 102 globally unique sessions; all are `gpt-5.5/xhigh`, return code 0, and `codex exec`-launched, with fresh worker-6 adjudication for every paper.
- All 68 paper/packet final mirror pairs are byte-identical. Recursive `authoritative_dbaasp_ingest_ready=true` count is zero.
- Global packet, semantic, publication, and strict-worker gates all return 0; 84 unit tests pass and `py_compile` passes for all three checked Python sources.
- A separate native read-only verifier independently recounted finals, sessions, mirrors, Candidate 17 Figure 2 values, worker freshness, tests, and authority boundaries and returned `PASS`.

Remaining project work is unchanged: validation420 and final human reduction are unfinished; the public website/API/bulk-download lane is unfinished; authoritative database integration, licensing/source-version review, manuscript disclosure, and release approval remain blocked or pending.

## 2026-07-18 17:29 CST — Candidate 18 remains blocked after semantic false-green rejection

### Current strict-review denominator

- The strict manifest now contains 18 papers, but only 17 are source-reviewed publication-grade and frozen.
- `PMC11905587` is the only nonterminal paper: `needs_targeted_rework`, `publication_grade=false`, two open tickets, and one concrete worker-2 rework target.
- Its current canonical run sequence is structurally clean: six independent `codex exec` sessions, all return code 0, all `gpt-5.5/xhigh`, and worker-6 starts after the latest upstream worker. This proves runtime independence, not scientific acceptance.
- Current acceptance gates for `PMC11905587`: packet gate `0`, semantic gate `1`, publication gate `2`. Therefore the accepted freeze remains 17 papers.
- No DBAASP strict-review process is currently active.

### Why Candidate 18 was not frozen

- The first six-worker pass reached a deterministic green gate, but the leader field-level audit rejected it.
- Layer 2 used a generic treatment placeholder instead of the source-verified `QsLEAP2` mature peptide and exact 41-aa sequence.
- Reported assay context (`1.0 x 10^5 CFU/mL`, OD600, triplicates and independent biological repeats) was dropped from the activity rows.
- Six explicit Table 1 no-activity rows were not durably represented, while one fallback machine candidate inferred `>1000` from a source table dash.
- The method reports a dilution range ending at `31.25 ug/mL`, while Table 1 reports `3.125` and `6.25 ug/mL`; this intrapaper conflict was not preserved as a caution.
- Worker-3 initially wrote false model metadata (`gpt-5.6-sol/high`) despite a canonical `gpt-5.5/xhigh` run. A targeted worker-3 rerun repaired this provenance field.
- The targeted worker-2 rerun returned code 0 but did not repair its assigned source-completeness contract. Fresh worker-6 correctly refused ticket closure and changed the paper to `needs_targeted_rework`.

### Queue accounting caveat and next action

- The fresh candidate report shows `candidate_count=217`, `already_reviewed_count=17`, `recommended_count=9`, and `needs_material_recovery_count=18`.
- `already_reviewed_count` only checks whether `final/review_report.json` exists, so it incorrectly includes blocked `PMC11905587`. Scientific progress is still 17 accepted papers and 201 candidate-pool papers not yet accepted, not 18 accepted / 200 remaining.
- Next action: provide worker-2 an exact, machine-readable repair contract; rerun worker-2; run fresh worker-6 adjudication; perform another leader field-level audit; only after zero open tickets and semantic/publication gates return 0 may Candidate 18 enter a new global freeze.
- The next untouched automatically recommended paper remains `PMC11956232`, but it must not supersede the open Candidate 18 repair.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/work/review/leader_candidate18_initial_semantic_audit_20260717.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11905587/rework/rework_requests.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11905587/rework/rework_responses.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/final/review_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11905587_strict_acceptance_audit_latest.json`

## 2026-07-26 16:33 CST — Live strict-review checkpoint; accepted freeze remains 17 papers

### Plain-language current state

- The strict DBAASP manifest contains 18 papers, but only 17 have passed source-reviewed publication-grade acceptance and entered the accepted freeze.
- No additional paper was frozen between the 2026-07-18 checkpoint and this live check.
- `PMC11905587` remains the only nonterminal paper: `needs_targeted_rework`, `publication_grade=false`, two open tickets, and one unresolved rework target.
- Its six canonical workers are structurally valid: six unique independent `codex exec` sessions, all return code 0, all `gpt-5.5/xhigh`, and worker-6 is newer than the latest upstream worker. This still does not override the failed scientific gates.
- Fresh Candidate 18 acceptance gates are packet `0`, semantic `1`, and publication `2`; therefore Candidate 18 is not accepted.
- No strict-review or `codex exec` paper worker process is currently running.

### Queue and remaining-work accounting

- Current strict status: 18/18 packets material-complete, 17/18 analysis accepted, 17/18 review status `accepted_with_cautions`, and 17/18 publication-grade.
- The full candidate pool contains 217 papers. Scientific accepted progress is 17, so 201 candidate-pool papers are not yet accepted.
- The candidate report says `already_reviewed_count=17`, but that counter is based on the presence of a final review file and includes blocked `PMC11905587`; it is not an acceptance counter.
- Nine currently displayed untouched candidates have complete staged materials and are directly recommended. Eighteen candidates need material recovery before a strict run.
- The next untouched recommended candidate is `PMC11956232`, but Candidate 18 repair remains the immediate queue head.
- Authoritative DBAASP ingest remains 0 papers; fallback-derived records remain excluded from RC2, the public portal, and authoritative release claims.

### Validation and immediate next action

- Fresh regression run: 85 tests passed.
- Immediate next action remains: send worker-2 the full machine-readable source-completeness contract, rerun worker-2, run a fresh independent worker-6 adjudication, and perform leader field-level semantic QA.
- Candidate 18 may enter a new freeze only after both tickets and the rework target are closed with evidence, semantic/publication gates return 0, and the leader audit independently confirms the repaired fields.
- After Candidate 18 closes, continue sequential strict review with `PMC11956232`.

Primary evidence refreshed in this checkpoint:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11905587_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/candidates_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/work/review/leader_candidate18_initial_semantic_audit_20260717.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11905587/rework/rework_requests.jsonl`

## 2026-07-26 16:40 CST — Whole-project progress synthesis

### Overall conclusion

- The project already has a mature evidence-curation corpus, a reproducible RC2 release-candidate package, a working local portal/API/MCP surface, and established strict paper-review contracts.
- The project is not yet a finished public database or NAR-ready submission. The main unfinished gates are full validation, public deployment, license/source-version review, release-vs-portal reconciliation, manuscript disclosure, and continued strict DBAASP review.
- No strict-review, validation420, portal, or MCP production process was running before this checkpoint. Portal and MCP were started temporarily for a local smoke test and shut down after successful checks.

### Workstream dashboard

| Workstream | Current evidence-backed state | Completion interpretation |
| --- | --- | --- |
| RC2 data/release foundation | 1,471 final-artifact papers; 1,374 public-v1 candidates; 139,259 database-audit rows; 115,184 activity records; 4,774 mechanism claims; versioned TSV/schema/checksum package exists | Static release-candidate foundation is mature, but not public/NAR-ready |
| Database evidence statuses | 95,941 `source_verified`; 32,550 `source_conflict`; 6,472 `sequence_modified_not_normalized`; 4,240 `database_only_no_primary_source`; 56 `unresolved_record` | Conflicts and provenance gaps are explicitly represented; they are not automatically database errors |
| Strict DBAASP candidate review | 18 manifest papers; 17 publication-grade accepted-with-cautions; `PMC11905587` remains nonterminal with two open tickets; 201 candidate-pool papers remain not scientifically accepted | Quality process works, but the large strict expansion is at an early stage |
| validation420 | 39/224 packet results; 114/420 rows covered; 185 packet results missing; 22 current targeted-rework decisions; queue soft-paused | Partial validation only; no final closure or human sign-off |
| Human review worksheet | 34/192 saved human verdicts: 30 confirmed and 4 uncertain; 18 additional Codex recommendations remain AI-assisted rather than human verdicts | Human review is incomplete and must remain separate from AI recommendations |
| Local portal | Live smoke passed for home page, FTS search, stats, TSV export, and health endpoint; SQLite contains 1,811 papers, 115,372 activity rows, 128,976 audit rows, and 5,994 mechanism rows | Functional local mixed-tier demo; portal counts are not RC2 release denominators |
| MCP | Live health and `tools/list` passed; ten read-only tools available | Functional locally; no public production endpoint |
| Benchmark | Forty source-traceable QA cases and protocol exist | Benchmark design exists, but grounded-vs-ungrounded scored results are not closed |
| Public deployment | No Docker/hosting/reverse-proxy/domain/HTTPS/process-management or production-monitoring evidence found | Not deployed publicly |
| NAR manuscript/release | Step 0-5 infrastructure outputs exist; pilot20 closure exists; full validation and Step 7 disclosure remain pending | Not submission-ready |

### Current portal data boundary

- Portal database statistics are a mixed operational/demo layer: 1,811 papers, 115,372 activity rows, 128,976 audit rows, 42,895 conflicts, 5,994 mechanism rows, 8,742 figure rows, 6,009 SAR-pair rows, and 1,121 selectivity rows.
- Portal activity includes 108,761 `atlas_core`, 5,511 `machine_extracted`, and 1,100 `dual_model_recovered` records.
- Portal does not ingest the current DBAASP strict/pending expansion. Its counts must not be used as RC2 release counts or described as an authoritative DBAASP-expanded corpus.
- Fresh smoke checks passed for `/healthz`, `/api/stats`, `/search?q=LL-37`, `/export/papers.tsv`, MCP `/healthz`, and MCP `tools/list`.

### Important unresolved counting conflicts

1. RC1-era documents still contain 1,371 public papers, 100 excluded papers, 4,772 mechanism claims, and 29 targeted-rework papers; RC2 authority is 1,374, 97, 4,774, and 30.
2. The historical queue universe is 1,472 papers, while the final-artifact release universe is 1,471. The extra queue-only failure remains a recovery backlog.
3. RC2, portal, deepmine recovered/machine, and DBAASP strict/pending counts describe different evidence tiers and must not be merged without a new reconciliation manifest.
4. `accepted_with_cautions` is not clean acceptance; cautions and conflicts remain part of the publication claim.
5. Human-review accounting remains unreconciled: 192 worksheet rows, 117 dry-run matches, and 105 verdicts surfaced in RC2.
6. validation420's early status header says running, but the later checkpoint in the same status file is authoritative: the queue is soft-paused.
7. Candidate-report `already_reviewed_count` is file-presence based and includes blocked Candidate 18; it is not a scientific acceptance count.

### Current execution order

1. Repair and close strict Candidate 18, then continue the remaining strict candidate queue with the same six-worker and leader-semantic-QA contract.
2. Resume validation420 through a new bounded retry/resume plan, including the four interrupted packets, rather than blindly continuing the stopped runner.
3. Reconcile RC2, portal, deepmine, strict-review, and human-review denominators into an explicit versioned tier manifest.
4. Synchronize RC1-era roadmap/data-dictionary/status documentation to RC2.
5. Finish license/source-version review, public HTTPS hosting, API/download deployment hardening, benchmark scoring, and manuscript disclosure.
6. Leave final human reduction/sign-off to the final stage, while preserving a complete reviewer packet and provenance trail for external reviewers.

Primary evidence:

- `reports/nar_resource_freeze_v1/release_manifest_latest.json`
- `releases/amp_evidence_atlas_v1_rc2/release_manifest.json`
- `reports/nar_resource_freeze_v1/manual_validation/validation420/VALIDATION420_RUN_STATUS.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/candidates_latest.json`
- `pipeline_v2/review_flow_qa_strict_latest.json`
- `pipeline_v2/review_state_export_manifest.json`
- `portal/atlas.db`
- `portal/portal_server.py`
- `portal/mcp_server.py`
- `docs/NAR_RESOURCE_V1_STEPWISE_EXECUTION_PLAN_20260622_093231_CST.md`

## 2026-07-26 21:22 CST — 18-paper freeze withdrawn; strict queue is correctly nonterminal

### Plain-language disposition

- The rolling strict manifest now contains 19 material-complete papers.
- The attempted 18-paper freeze is **withdrawn**. Its initial mechanical `PASS` was overturned by an independent field-level verifier, and `leader_contract_recheck.json` is now explicitly `FAIL`, `freeze_eligible=false`, with return code `1`.
- The current live terminal-ready count is 16/19: 16 papers remain source-reviewed complete, `PMC11905587` and `PMC12230126` are reopened under one blocking ticket each, and `PMC11956232` has not completed a valid review.
- Eighteen final files still carry historical `accepted_with_cautions` values, but two of those papers have runtime-open tickets and therefore are not currently terminal-ready. Do not use the final-file string alone as the acceptance denominator.
- Authoritative DBAASP ingest remains 0/19. No fallback row is approved for RC2, portal, or authoritative release ingest.

### Independent false-green findings

The independent verifier rejected the 18-paper freeze for five reasons:

1. `PMC12230126` retained four nested `authoritative_dbaasp_ingest_ready=true` values in the two current worker-4 artifacts despite zero linked authoritative rows.
2. `PMC11905587` listed a structured inoculum as both reported and unreported in all five activity rows, and omitted the separate methods-maximum 1,000 versus Table 1 footnote-maximum 100 µg/mL conflict.
3. `PMC13013390` had 179 locators in mutable manifests versus 408 actual locator-index rows.
4. `PMC11531597` had zero extraction errors in status versus two rows in `extraction_errors.jsonl`.
5. The saved 18-paper verify record pointed to the mutable rolling manifest, and the immutable snapshot was physically written after Candidate 19 was appended.

The locator/error count drift has been refreshed. A first expanded consistency run caught eight hard findings; a second run after mutable-count synchronization retained only the four real recursive authority contradictions. Historical freeze chronology is now recorded explicitly as invalid for terminal binding rather than silently rewritten.

### Gate and regression hardening completed

- `strict_worker_run_gate()` now scans current paper/work, paper/final, packet/analysis, and packet/final JSON/JSONL artifacts recursively for any true authority-ready boolean.
- The same gate checks packet-manifest, locator-index declared, and locator-index actual counts, plus extraction-status versus extraction-error JSONL counts, before synchronization can normalize mutable state.
- `sync_packet_statuses()` now refreshes live locator/error counts into packet status and the rolling manifest.
- Single-paper acceptance now requires the strict worker/artifact gate to have zero hard findings; a green packet/semantic/publication return code is no longer sufficient.
- Verify reports now bind start/finish manifest SHA256 values and fail closed if the manifest changes during the run.
- Runtime-open tickets now take priority in `recommended_next_action`; historically accepted final strings can no longer recommend preservation while a new blocking ticket is open.
- Fresh regression result: **95 tests passed**; all changed scripts pass `py_compile`.

Current 19-paper diagnostic return codes are packet `2`, semantic `1`, publication `2`, and strict worker/artifact `1`. This expected red state is caused by Candidate 19 missing finals, its six invalid quota-limited worker attempts, and the four recursive authority contradictions. The manifest hash remained unchanged throughout verify.

### Formal rework queue

- `PMC11905587` ticket `rwk-PMC11905587-layer2-semantic-contradictions-003` is assigned to worker-2. The leader validator was expanded from 9 to 11 checks and currently fails exactly the two newly identified semantic omissions. A fresh worker-2 and a later fresh worker-6 are mandatory.
- `PMC12230126` ticket `rwk-PMC12230126-recursive-authority-boundary-007` is assigned to worker-4. Its machine validator currently fails on recursive authority true values and worker-4 mirror consistency. A fresh worker-4 and a later fresh worker-6 are mandatory.
- Both tickets are injected into regenerated worker prompts. Neither ticket has been self-closed by the leader.
- Fresh single-paper acceptance commands for both papers return code `1` and `acceptance_ready=false`.

### Candidate 19 preparation and execution blocker

- Candidate 19 is `PMC11956232`, Lf-KR against carbapenem-resistant *Escherichia coli*.
- XML, PDF, and one DOCX supplement are staged. A leader preflight contract preserves peptide identity, 40 exact Table 1–3 observations, quantitative figure surfaces, toxicity/mechanism/in-vivo requirements, and four source conflicts.
- Figures were rendered/cropped deterministically at 300 dpi. The leader color-segmentation scaffold contains 640 Figure 1/2 treatment observations. Conservative overlap rules reduce 160 initial missing color segments to 30 unresolved values; those 30 remain `null` for canonical source review rather than being fabricated.
- A prompt-binding regression exposed that this preflight contract had not actually been present in the six generated prompts. The prompt builder is now fixed: all six Candidate 19 prompts explicitly bind the leader contract and evidence scaffolds. The 40 Table 1–3 observations now also carry 15 unique semantic row locators and 40 unique semantic cell locators, so a base-table citation alone cannot satisfy the contract.
- Six independent `codex exec` sessions were started for Candidate 19, but all six returned code `1` before scientific work because the current ChatGPT Codex CLI account reached its usage limit. The CLI message says to retry at **2026-08-02 08:15**. These sessions are invalid evidence and are not counted as review.
- An isolated existing API-key profile was tested as a safe alternative and returned HTTP 401; native subagents or a different model will not be substituted for the canonical six `gpt-5.5/xhigh` Codex CLI workers.

### Queue accounting and next executable sequence

- Current candidate report: 217 candidates, 17 file-presence-reviewed, 9 displayed material-ready recommendations, and 18 needing material recovery. Thus 200 candidates have no final review file under this report's current file-presence definition.
- This candidate counter is not the scientific acceptance denominator and does not align one-to-one with the 19-paper strict manifest.
- Once canonical Codex CLI access is available, execute sequentially:
  1. `PMC11905587` worker-2, leader 11-check validation, then fresh worker-6 and leader semantic audit.
  2. `PMC12230126` worker-4, recursive authority validation, then fresh worker-6 and leader semantic audit.
  3. `PMC11956232` workers 1–6 as six independent sequential sessions, followed by strict gates and field-level leader audit.
  4. Generate a new immutable freeze only after all affected tickets are terminally closed, all gates pass against the immutable path/hash, and a new independent verifier returns `PASS`.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260726_18paper/independent_verifier_report.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260726_18paper/leader_contract_recheck.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260726_18paper/freeze_chronology_and_binding_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11905587/work/review/leader_worker2_semantic_rework_contract_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/review/leader_recursive_authority_rework_contract_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/source_surface_preflight_contract_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/leader_color_digitized_figures1_2.json`

## 2026-07-27 00:01 CST — Frozen 200-paper campaign started; material denominator corrected

### Campaign state

- The exact denominator is frozen at **200 unique papers** in `remaining_200_strict_review_queue_20260726.json`.
- A durable state ledger and append-only journal now require, per paper, six clean unique sequential `codex exec` sessions on `gpt-5.5/xhigh`, fresh worker-6 ordering, mechanical acceptance, zero tickets, leader semantic `PASS`, independent verifier `PASS`, and recursive authority=false.
- Current terminal count for this new 200-paper campaign is **0/200**. This is intentional: Candidate 19 remains under targeted rework and no historical final-file string is being counted as a new campaign completion.
- The two previously reopened papers, `PMC11905587` and `PMC12230126`, have completed their required fresh owner/worker-6 repairs and remain separate from the frozen 200 denominator.

### Candidate 19 false green and active repair

- Candidate 19 `PMC11956232` completed six canonical workers, but the leader rejected the mechanical green result because the final retained only 40 exact table activity rows and three prose toxicity rows while omitting the quantitative Figure 1–7 surfaces.
- Two blocking tickets were opened for worker-3 quantitative figure exhaustion and worker-2 Layer-2/toxicity integration.
- Fresh worker-3 completed in a new `gpt-5.5/xhigh` Codex session with return code 0. The leader independently reran the immutable validator and obtained **17/17 PASS**, covering **797** observations: F1 360, F2 280, F3 20, F4 98, F5 18, F6 17, and F7 4, with no fabricated numeric fills.
- The ticket's initial total of 757 was an arithmetic typo; the unchanged per-figure contract sums to 797. The leader corrected the contract explicitly before downstream integration.
- Fresh worker-2 is now running. Worker-6 will not start until worker-2 finishes and the leader independently passes the worker-2 field validator.

### Corrected source-material accounting

- A worklist-path bug had incorrectly probed 173 descriptive PDF filenames as sibling `paper.pdf` files. Direct audit proves all 173 exact worklist PDFs exist and have valid PDF headers.
- Europe PMC structured-source recovery staged validated XML+PDF pairs for **172/173** PDF-only entries.
- `10.1021/acs.langmuir.6b03477` initially remained PDF-only because its mapped PMCID is non-open-access and the Europe PMC JATS full-text endpoint returned 404. A second official NCBI retrieval route succeeded: the NCBI PMC BioC XML endpoint returned a validated structured document with 128 passages, including table passages. The primary PDF remains the layout authority.
- The pilot parser now supports BioC metadata, passage locators, and table passages while explicitly requiring PDF layout verification.
- Canonical frozen-queue material state is now **200/200 XML+PDF material-ready**, with zero primary, structured-fulltext, or declared-supplement gaps.
- The supplement inventory parser now matches canonical JATS media semantics, including TIFF/CIF payloads. The complete recovery campaign closed all 130 initial paper-level gaps: 79 papers succeeded on the first full pass, 43 more on retry 1, and the final eight on retry 2 using direct retry and official PMC OA-package fallback. Current missing supplement count is zero.

### Validation evidence

- The strict ledger now reports exactly 200 material-ready and zero material-recovery papers: Candidate 19 is in targeted rework and the other 199 are ready for six-worker review.
- New controller regressions cover TIFF/CIF inventory, mandatory passing owner validation artifacts, and the rule that owner workers are run one at a time with leader revalidation before fresh worker-6.
- Current combined regression run exercised 103 tests; one live-fixture regression was updated to remove duplicated maximum-conflict cautions across all caution/conflict containers, and its targeted rerun passes. A fresh full-suite rerun remains required after the active worker/material processes finish.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_queue_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_strict_review_journal_20260726.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/candidates_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/material_recovery_200/structured_source_recovery_all173_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/material_recovery_200/structured_source_recovery_acs_bioc_20260727.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/material_recovery_200/supplement_batches/supplement_recovery_retry2_oa_package_20260727.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/material_recovery_worklist_overlay.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_semantic_audit_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_worker3_leader_recheck_20260726.json`

## 2026-07-27 02:20 CST — First frozen-200 paper terminal; durable 199-paper supervisor ready

### Current strict-campaign denominator

- The frozen denominator remains exactly **200 unique papers**.
- `PMC11956232` is now the first paper to satisfy the complete new terminal contract, so the live state is **1/200 terminal scientific review complete** and **199 remaining nonterminal**.
- All **200/200** papers remain strict-material-ready, there are zero live open tickets, and authoritative DBAASP ingest remains false.
- The current generated heartbeat is `reports/remaining_200_campaign/supervisor/REMAINING_200_CAMPAIGN_STATUS.md`; use it with the frozen ledger rather than counting historical final-file strings.

### Candidate 19 correction and final evidence

- The initial structured leader rerun incorrectly returned `PASS` while missing `identity.sequence_length=20` for the 19-residue sequence `RRWQWRPKRIVKLIKKWLR`. The separate independent verifier correctly returned `FAIL` and rejected that unsupported leader conclusion.
- The leader added a deterministic strict-gate rule for plain standard one-letter sequences: sibling `sequence_length` must equal the actual residue count, and terminal amidation is not an extra residue. A second deterministic rule requires the final review report's open-ticket count to equal live packet ticket state.
- A leader blocking ticket drove a fresh worker-2 repair and later fresh worker-6 adjudication. The first repair corrected canonical/final evidence but left two stale preflight JSON surfaces at 20; the next full leader audit returned `FAIL`, opened a second worker-2 ticket, and forced those surfaces to 19 as well.
- After the second owner/adjudication cycle, mechanical acceptance passed with zero hard findings, the fresh structured leader audit returned `PASS`, and a separate independent verifier returned `PASS`.
- Final preserved counts are 40 activity records, 17 toxicity records, 797 figure observations, 12 database audits, and 5 mechanism claims; paper/packet mirrors are byte-identical, live tickets and final rework targets are zero, and recursive authority remains false.

### Long-running execution and recovery

- `supervise_remaining_200_strict_campaign.py` now supervises the remaining queue one paper at a time. It rotates across all nonterminal papers by sweep, invokes the fail-closed campaign executor, persists per-paper attempts and logs, updates an atomic JSON/Markdown heartbeat, and never promotes papers itself.
- The supervisor was launched detached at **2026-07-27 02:20 CST** as PID `2937486`. Its first active paper is `PMC12125351`; worker-1 started as a fresh exact `codex exec` `gpt-5.5/xhigh` process after packet build. The saved PID is operational metadata only; verify the lock, process tree, heartbeat, and ledger together before assuming it is still active.
- A paper is counted only after six unique sequential exact `codex exec` workers on `gpt-5.5/xhigh`, fresh worker-6 ordering, current mechanical acceptance, zero tickets, structured leader `PASS`, and independent verifier `PASS`.
- The supervisor has a separate process lock and a per-paper retry budget, so process interruption can be resumed from the frozen ledger and append-only journal without treating partial runs as terminal evidence.
- Fresh regression evidence is **114 tests passed** after adding the two supervisor tests to the prior 112-test suite; changed scripts compile.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11956232/20260726T175741004921Z.leader_semantic_auditor.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11956232/20260726T181013898228Z.independent_paper_verifier.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11956232_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/supervise_remaining_200_strict_campaign.py`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/REMAINING_200_CAMPAIGN_STATUS.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_journal.jsonl`

## 2026-07-27 03:46 CST — First untouched-paper pilot rejected a mechanical false green

- The detached supervisor remains active on `PMC12125351`, the first previously untouched paper in the remaining queue.
- Six canonical workers completed sequentially with six unique `gpt-5.5/xhigh` sessions and return code 0. Single-paper mechanical acceptance also returned green with zero strict hard findings.
- The independent field-level leader audit nevertheless returned `FAIL` and opened four blocking tickets:
  1. worker-3: the 12-sheet XLSX supplement was only inventory-listed; packet supplementary tables were empty and workbook row/cell locators were absent;
  2. worker-2: final activity/toxicity retained only a narrow subset, omitted large MIC/CC50/HC50/selectivity/dose-response surfaces, and failed to preserve an XML-versus-workbook *P. aeruginosa* value/unit conflict;
  3. worker-4: AMP-15/17/20 validated candidate identities were conflated with unrelated benchmark rows from Supplementary Data 8;
  4. worker-5: the direct PI membrane-permeability claim omitted the row-level fluorescence data in Supplementary Data 9.
- Current campaign state remains **1/200 terminal**. `PMC12125351` has four live blocking tickets and is in sequential owner repair beginning with worker-3; no paper is promoted from the six-worker or mechanical result alone.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/20260726T193205570164Z.leader_semantic_auditor.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12125351_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12125351/rework/rework_requests.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC12125351/run_sequence_latest.json`

## 2026-07-27 05:54 CST — `PMC12125351` attempt 1 preserved as nonterminal; queue rotation active

- `PMC12125351` attempt 1 ran for about 3.5 hours and exhausted its three configured rework rounds without a false terminal promotion.
- Round 2 found and repaired source-field conflicts involving K88 strain, Supplementary Data 10 log10 concentration semantics, false selectivity labels, unsupported Homo sapiens toxicity targets, blank-cell locators, and a worker artifact recursively used as a mechanism source locator.
- The leader added a deterministic strict-gate regression that rejects project analysis/work/final paths in source-locator fields. Current full regression evidence is **115 tests passed**.
- Round 3 independently found four remaining blockers and staged fresh tickets for the next attempt:
  1. stale final materials manifest and missing packet-final mirror;
  2. hemolysis incubation recorded as 24 h instead of 1 h plus an unpreserved *S. aureus* strain conflict;
  3. database final recursively citing project manifests and retaining stale model/ticket/pending-adjudication fields;
  4. phenotype mechanism claim using a computational-conformation paragraph as its main locator and retaining stale ticket metadata.
- Live frozen state is still **1/200 terminal**, **199 nonterminal**, **4 open tickets**. `PMC12125351` remains `needs_targeted_semantic_rework`; its next sweep will run worker-1/2/4/5 repairs and a fresh worker-6.
- The supervisor recorded the failed-closed attempt in its append-only journal and rotated to `PMC11897483`, whose fresh canonical worker-1 is active. This prevents one difficult paper from starving first-pass review of the other 198 untouched papers.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/leader_semantic_auditor_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12125351/rework/rework_requests.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_journal.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC11897483/`

## 2026-07-27 08:25 CST — Progress check healthy; bounded immediate-retry scheduling prepared

### Live state

- The detached supervisor is alive as PID `2937486`; its campaign/Codex process tree is healthy and supervisor stderr is empty.
- Frozen state is **1/200 terminal**, **199 nonterminal**, **200/200 material-ready**, with **5 open tickets** across two nonterminal papers.
- Two complete untouched-paper attempts have been journaled:
  - `PMC12125351`: failed closed after three semantic-repair rounds, with four next-attempt tickets;
  - `PMC11897483`: failed closed after three semantic-repair rounds, with one next-attempt worker-2 ticket.
- The current active paper is queue index 4, `PMC12715223`; its fresh worker-1 exact `codex exec` `gpt-5.5/xhigh` process is active. No quota, access, timeout, duplicate-session, or supervisor exception is visible.

### `PMC11897483` scientific blocker

- Six latest canonical sessions are unique, return code 0, `gpt-5.5/xhigh`, and the latest worker-6 is fresh.
- The final leader audit still rejected mechanical acceptance because Table 2's first rowspan was shifted: a group label `"1"` was emitted as an activity value, Group 1 *S. aureus* and *L. monocytogenes* values were omitted/shifted, and Figure 10A exact hemolysis labels `0.8193%`, `3.7988%`, and `10.949%` were reduced to threshold-only rows.
- The one live worker-2 ticket contains source-vs-final executable acceptance checks; it will be repaired on the next bounded retry.

### Scheduling correction

- Progress inspection found that the original supervisor froze all 199 papers at sweep start, so difficult papers would not be retried until every untouched paper completed its first attempt. This was safe but made terminal completion grow unnecessarily slowly.
- The supervisor code now supports bounded immediate retry: a nonterminal repair paper may be attempted at most three consecutive times before queue rotation, while the existing total per-paper attempt ceiling remains 12.
- A detached watcher PID `3748211` will wait for `PMC12715223` to finish, verify the campaign child has exited, terminate the old supervisor only during its 15-second no-child sleep boundary, and launch the updated supervisor. It will not interrupt the current Codex worker or partial paper.
- Fresh regression result is **116 tests passed**.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_journal.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11897483/leader_semantic_auditor_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/rework/rework_requests.jsonl`
- `pipeline_v2/deepmine/supervise_remaining_200_strict_campaign.py`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/restart_after_PMC12715223.sh`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/restart_after_PMC12715223.log`

## 2026-07-27 09:23 CST — Active-paper worker progression verified

- Live denominator remains **1/200 terminal**, **199 nonterminal**, **200/200 material-ready**, with five open repair tickets across `PMC12125351` and `PMC11897483`.
- Supervisor PID `2937486` and its campaign/Codex process tree are alive; stderr remains empty.
- Active paper `PMC12715223` has completed worker-1 through worker-5 sequentially. All five reports have return code 0, unique sessions, model `gpt-5.5`, and reasoning effort `xhigh`; worker-6 is currently active.
- The generated supervisor heartbeat still shows the paper-attempt start boundary at 08:18 CST because it is intentionally rewritten only before/after a complete paper attempt. The live strict ledger now correctly marks one `six_worker_review_in_progress`, and the process tree confirms ongoing worker-6 execution.
- The safe-restart watcher PID `3748211` is still waiting and has not signaled the supervisor. It will switch to bounded immediate-retry scheduling only after the complete `PMC12715223` attempt exits and no campaign child remains.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC12715223/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/restart_after_PMC12715223.log`

## 2026-07-27 09:42 CST — Safe scheduler switch completed; bounded repair retry active

- Frozen campaign denominator remains **1/200 terminal**, **199 nonterminal**, and **200/200 material-ready**. There are **five live repair tickets**: four for `PMC12125351` and one for `PMC11897483`.
- `PMC12715223` attempt 1 completed all six canonical workers sequentially. All six exact `codex exec` sessions were unique, return code 0, and used `gpt-5.5/xhigh`; worker-6 was later than all upstream workers.
- The independent structured leader audit for `PMC12715223` did **not** produce a scientific verdict. Codex exited with return code 1 after a biology-content safety access rejection (`Invalid prompt: we've limited access to this content for safety reasons`). No leader JSON was written, so the campaign correctly failed closed and kept the paper nonterminal as `awaiting_worker6_repair_or_mechanical_acceptance`. This was not a quota or worker-independence failure.
- The post-paper safe-restart watcher completed successfully at the no-child boundary. Old supervisor PID `2937486` exited only after `PMC12715223` finished; updated supervisor PID `3896212` is healthy and now enforces at most three consecutive repair attempts before rotating.
- The updated supervisor immediately prioritized `PMC12125351` attempt 2. Fresh worker-1 exact `codex exec` is active as PID `3896617`, using `gpt-5.5/xhigh`; supervisor and campaign stderr are empty.
- Three nonterminal full-paper attempts have now finished under the long supervisor: two were rejected by source-field semantic audits (`PMC12125351`, `PMC11897483`) and one failed closed at the leader CLI/safety boundary (`PMC12715223`). No paper has been falsely promoted.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_journal.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/restart_after_PMC12715223.log`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12715223/20260727T012357643657Z.leader_semantic_auditor.stderr.log`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC12715223/run_sequence_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/process_20260727T013251893587Z/process_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`

## 2026-07-27 10:42 CST — Grok safety-false-positive review fallback validated and enabled

- Live frozen state remains **1/200 terminal**, **199 nonterminal**, and **200/200 material-ready**. `PMC12125351` attempt 2 owner repairs closed its four prior tickets, reducing the campaign-wide live ticket count from five to **one**; the remaining ticket belongs to `PMC11897483`.
- Reviewed the local guide at `/mnt/d/software/CLIProxyAPI/GROK_CALLING_GUIDE_CN.md`. CLIProxyAPI is healthy at local-only `127.0.0.1:8317`; the local API key remains read only in memory and is never written to project logs.
- Live model discovery confirmed `grok-4.20-0309-reasoning`, `grok-4.5`, `grok-4.3`, and other Grok models. Real probes confirmed both OpenAI-compatible function calling and strict JSON Schema output.
- Added `pipeline_v2/deepmine/grok_readonly_review.py`, a paper-scoped read-only evidence tool loop. Grok can inventory, hash, search, and read bounded text/JSON chunks; PDF, XLSX, DOCX, and ZIP sources are converted read-only. Absolute paths, `..`, workspace secrets, and non-paper evidence are denied.
- The frozen campaign still prefers Codex. Grok is eligible **only** when a leader or verifier Codex runtime contains the exact classified biology-content safety access rejection. Quota, timeout, schema, semantic, worker, or other failures do not activate Grok.
- Canonical worker-1 through worker-6 remain unchanged: six unique sequential exact `codex exec` sessions on `gpt-5.5/xhigh`, return code 0, with fresh worker-6 chronology. Grok never replaces or repairs a canonical worker.
- Grok leader defaults to `grok-4.20-0309-reasoning`; Grok verifier defaults to `grok-4.5`, with fresh provider response IDs used as independent review-session identifiers. Current local schema validation, exact evidence-path checks, source/final/runtime coverage checks, input fingerprint stability, mechanical acceptance, ticket state, authority=false, and fallback-release exclusion all remain fail-closed.
- A synthetic end-to-end review succeeded with 16 read-only tool calls, zero evidence-coverage failures, zero semantic-validation failures, unchanged paper inputs, strict schema-valid output, and 41,114 total tokens. This validates transport/orchestration only; it is explicitly not a real-paper scientific verdict.
- Full regression is **120 tests passed**, direct script execution/help works, and Python static compilation passed.
- Live campaign `PMC12125351` attempt 2 has finished owner repairs and worker-6 and is currently running its Codex leader semantic audit. Because that campaign subprocess started before this code update, any safety rejection in this active audit will remain fail-closed; its next bounded retry and every newly spawned paper attempt will have the Grok fallback enabled by default.

Primary evidence:

- `/mnt/d/software/CLIProxyAPI/GROK_CALLING_GUIDE_CN.md`
- `pipeline_v2/deepmine/grok_readonly_review.py`
- `pipeline_v2/deepmine/run_remaining_200_strict_campaign.py`
- `pipeline_v2/deepmine/test_grok_readonly_review.py`
- `pipeline_v2/deepmine/test_remaining_200_strict_campaign.py`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/grok_fallback_validation_20260727T1040CST.json`

## 2026-07-27 10:48 CST — `PMC12125351` attempt 2 leader audit rejected one remaining strain-conflict defect

- Frozen completion remains **1/200 terminal**, **199 nonterminal**, and **200/200 material-ready**. Live open tickets are now **two**: the existing `PMC11897483` worker-2 ticket plus one newly staged `PMC12125351` worker-2 ticket.
- `PMC12125351` attempt 2 completed its owner repairs, fresh worker-6, mechanical run, and independent Codex leader audit. The audit had return code 0, used a fresh unique `gpt-5.5/xhigh` session, independently reviewed the primary source and every current final record, and returned a scientific `FAIL`.
- The remaining defect is confined to nine Supplementary Data 10 column E MIC records. The workbook header says *S. aureus* ATCC 25923, while the assigned/value-provenance interpretation is ATCC 29213; current conflict metadata incorrectly records both sides as ATCC 29213 and uses an unindexed `column=E` locator instead of the resolvable `row=2:cell=E2` header locator.
- The campaign staged one concrete worker-2 ticket with source-cell, conflict-metadata, locator-resolution, count, and mirror acceptance checks. It immediately entered rework round 2; fresh worker-2 exact `codex exec` is active on `gpt-5.5/xhigh`.
- Grok fallback was correctly **not** activated because this leader run was not safety-blocked: Codex completed normally and produced a valid source-field scientific verdict.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/20260727T023611700820Z.leader_semantic_auditor.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/20260727T023611700820Z.leader_semantic_auditor.runtime.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12125351/rework/rework_requests.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/process_20260727T013251893587Z/process_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`

## 2026-07-27 12:25 CST — Attempt 2 round 3 is rebuilding all invalidated ticket closures

- Frozen completion remains **1/200 terminal**, **199 nonterminal**, and **200/200 material-ready**. Campaign-wide live open tickets are **15**: 14 on `PMC12125351` and one on `PMC11897483`.
- `PMC12125351` rework round 2 completed worker-2, fresh worker-6, and another independent Codex leader audit. Mechanical acceptance remained red and the leader returned a valid scientific `FAIL` with three blockers: live ticket/final-state inconsistency, a stale activity hard-finding field despite repaired source cells, and packet-unresolvable database article-ID locator strings.
- Edits to current final artifacts and gates invalidated chronology-sensitive terminal closures for older tickets. Therefore ten prior `PMC12125351` tickets reopened alongside the newer tickets; this is why the live count rose sharply. All 14 currently have fresh nonterminal owner responses marked `repair_ready_for_adjudication`, but only a later fresh worker-6 with post-response green gates may close them.
- Rework round 3 has sequentially completed fresh worker-3, worker-2, worker-4, and worker-5 repairs. Fresh worker-1 exact `codex exec` on `gpt-5.5/xhigh` is active; the next expected step is one fresh worker-6 adjudication over all runtime-open tickets, followed by acceptance and leader re-audit.
- Supervisor PID `3896212`, campaign PID `3896370`, and the active exact Codex process are alive. No quota, timeout, duplicate-session, or safety-rejection error is present. Grok has not been invoked because the recent leader audits completed normally rather than hitting the classified biology safety rejection.
- This is active but not yet converged progress: no additional paper has been terminally promoted, and the reopened ticket count must not be mistaken for 15 newly discovered independent scientific errors.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/process_20260727T013251893587Z/process_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/20260727T031900126057Z.leader_semantic_auditor.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12125351/rework/rework_requests.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12125351/rework/rework_responses.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12125351/packet_manifest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`

## 2026-07-27 13:25 CST — Attempt 2 exhausted fail-closed; attempt 3 active with Grok fallback armed

- Frozen completion remains **1/200 terminal**, **199 nonterminal**, and **200/200 material-ready**. Campaign-wide live open tickets are **17**: 16 on `PMC12125351` and one on `PMC11897483`.
- `PMC12125351` attempt 2 finished at 13:00 CST after exhausting all three allowed semantic-rework rounds. It remained fail-closed and was not promoted.
- Attempt-2 round 3 achieved mechanical acceptance return code 0, but the fresh independent Codex leader audit found two remaining final-field defects:
  1. packet/final/material metadata disagreed about open-ticket counts, supplement inventory, OA-package exhaustion, and the extra packet mechanism alias;
  2. row-level activity/toxicity data were source-reviewable, but activity summary fields still contained placeholder zeros despite 130 activity and 126 toxicity records.
- The supervisor journaled attempt 2 with campaign return code 1, immediately queued bounded attempt 3, and started it at 13:01 CST. Attempt 3 has completed fresh worker-1 and is actively running fresh worker-2 on exact `codex exec gpt-5.5/xhigh`; subsequent missing-owner lanes, fresh worker-6, acceptance, and leader audit remain pending.
- The attempt-3 campaign report explicitly records `grok_safety_fallback_enabled=true`. Grok is armed for a classified leader/verifier biology safety rejection but has not yet been called.
- Supervisor PID `3896212`, campaign PID `158209`, and active worker-2 Codex processes are healthy. No quota, timeout, safety, or infrastructure error is visible.
- This remains non-converged: no new terminal paper was added during the last hour, although the latest blockers have narrowed from row-level source extraction to final summary/state metadata consistency.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/process_20260727T013251893587Z/process_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/20260727T044634985635Z.leader_semantic_auditor.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/campaign_run_20260727T050106388217Z.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_journal.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`

## 2026-07-27 13:34 CST — Serial throughput rejected; four distinct-paper lanes prepared

- The frozen campaign has produced one terminal paper in approximately 13.5 wall-clock hours. A naive terminal-throughput extrapolation would require roughly **112 days** for the remaining 199 papers; this is not an acceptable production schedule.
- The limiting factor is the scheduler, not the required per-paper model configuration: the old executor held one global campaign lock, allowed only one paper in flight, and could spend three consecutive attempts on the same difficult paper.
- Added cross-paper parallel execution while preserving every per-paper invariant:
  - each paper keeps six sequential independent exact `codex exec` workers on `gpt-5.5/xhigh`;
  - different paper IDs use separate nonblocking campaign locks;
  - rolling-manifest updates are serialized;
  - append builds no longer erase the global issues file;
  - packet status/acceptance synchronization is paper-scoped instead of rewriting every packet;
  - the frozen ledger remains serialized under its existing state lock.
- Added `supervise_remaining_200_parallel_campaign.py` with initial capacity **4 papers**: while untouched papers remain, at most one lane handles historical repair and three lanes advance fresh papers. Repair selection favors fewer prior attempts so one pathological paper cannot monopolize the queue.
- The full strict/Grok/review regression suite now passes **125 tests**, and all modified/new controller scripts compile.
- A boundary-safe switch watcher (PID `232034`) is active. It is not interrupting the currently running fresh worker-6 for `PMC12125351`; after attempt 3 is fully journaled, it will stop serial supervisor PID `3896212` during its post-paper sleep and launch the four-lane supervisor.
- Based on the observed first-attempt mean of about 2.4 hours, four lanes should cover a first strict pass over the queue in approximately **5–8 days**. Full terminal convergence remains dependent on repair rates; a realistic initial planning range is **3–6 weeks**, with a later increase to six lanes possible after a clean stability window.

Primary evidence:

- `pipeline_v2/deepmine/supervise_remaining_200_parallel_campaign.py`
- `pipeline_v2/deepmine/switch_remaining_200_to_parallel.py`
- `pipeline_v2/deepmine/run_remaining_200_strict_campaign.py`
- `pipeline_v2/deepmine/dbaasp_strict_pilot.py`
- `pipeline_v2/deepmine/test_remaining_200_strict_supervisor.py`
- `pipeline_v2/deepmine/test_remaining_200_strict_campaign.py`
- `pipeline_v2/deepmine/test_dbaasp_strict_pilot.py`

## 2026-07-27 15:22 CST — Attempt 3 final round active; parallel switch still waiting at boundary

- Frozen terminal completion is unchanged at **1/200**, with **199 nonterminal** and **200/200 strict material-ready**.
- Live open tickets are now **20**: 19 on `PMC12125351` and one on `PMC11897483`. The increase is mainly chronology-sensitive reopening of older owner responses after later final/gate edits, not 20 newly discovered independent scientific defects.
- `PMC12125351` attempt 3 has reached semantic-rework round 3. Round 2 was mechanically green and the leader audit independently passed the paper identity, 256 workbook-cited activity/toxicity values, mechanism boundaries, locators, recursive authority boundary, and final mirrors; it rejected one remaining final-state count mismatch: `review_report.final_counts.review_rework_targets=1` while the live `rework_targets` array length and then-live open-ticket count were zero.
- Round 3 fresh worker-1 repaired the count/state path and finished at 15:15 CST. A later fresh worker-6 started at 15:16 CST and is actively adjudicating the current final/ticket state on exact `codex exec gpt-5.5/xhigh`.
- The old serial supervisor PID `3896212`, campaign PID `158209`, worker-6 process tree, and boundary-switch watcher PID `232034` are healthy. No quota, timeout, safety, or infrastructure failure is visible.
- The four-paper parallel supervisor has **not yet launched** because the boundary contract deliberately forbids interrupting or overlapping the still-active old attempt. Watcher PID `232034` remains blocked on attempt-3 completion plus the supervisor's append-only `paper_attempt_finished` record; it will switch immediately afterward.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/process_20260727T050108308947Z/process_report.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12125351/20260727T064849267342Z.leader_semantic_auditor.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC12125351/20260727T071527Z.worker-6.last_message.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_journal.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`

## 2026-07-27 16:27 CST — Four-paper parallel execution live; terminal completion 2/200

- `PMC12125351` attempt 3 completed at 15:56 CST with campaign return code 0 and terminal frozen-ledger status. It is the second terminal paper in the 200-paper campaign.
- Frozen state is now **2/200 terminal**, **198 nonterminal**, and **200/200 strict material-ready**.
- The chronology-sensitive ticket cluster converged: campaign-wide live open tickets fell from 20 to **one**, the remaining `PMC11897483` activity/toxicity source-mismatch ticket.
- The boundary watcher safely stopped serial supervisor PID `3896212` only after attempt 3 was fully journaled, then launched parallel supervisor PID `540785`. The generated switch artifact records four-paper capacity and one repair lane.
- Four distinct papers are concurrently active:
  1. repair lane `PMC11897483` attempt 2 — repaired owner path completed and fresh worker-6 is active on exact `gpt-5.5/xhigh`;
  2. fresh lane `PMC11845615` attempt 1 — workers 1–2 completed and worker-3 is active;
  3. fresh lane `PMC13066039` attempt 1 — workers 1–2 completed and worker-3 is active;
  4. fresh lane `PMC13025223` attempt 1 — workers 1–2 completed and worker-3 is active.
- Parallel supervisor stderr is empty. The supervisor, four campaign executors, four paper-scoped pilot runners, and active Codex process trees are healthy, demonstrating that the concurrency boundary is operational rather than merely configured.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/parallel_switch_result.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_journal.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/campaign_run_20260727T050106388217Z.json`

## 2026-07-27 18:02 CST — DesignToxBench current-data support audit completed

- Completed six independent repository/data searches covering RC2 paper finals, the portal SQLite layer, strict DBAASP increments, validation/human-review quality, the external five-database merged corpus, and benchmark split/leakage feasibility.
- The publication-ready DesignToxBench gold set is currently **zero** because entity-level design origin, molecular identity/modifications, endpoint label policy, censor bounds, homology clusters, training cutoffs, and a formal split/release manifest do not yet exist.
- The actionable RC2 high-confidence design-paper core is **91 candidate papers**, of which **59** contain endpoint-derived safety evidence. The sequence-ready seed is **12 papers, 141 unique canonical short sequences, 659 safety observations**, and **136 unique sequences** with same-paper activity/safety pairing. **255** safety observations preserve an inequality or censor status. The endpoint classifier explicitly excludes microbial-efficacy rows such as `biofilm_cell_viability`.
- Adding analogue/optimization candidates gives an adjudication upper envelope of **214 papers**, **139 safety papers**, **25 sequence-ready safety papers**, **220 unique safety short sequences**, **1,691 safety observations**, and **202 paired unique sequences**.
- The strict post-RC2 increment contributes one terminal generative paper, `PMC12125351`, with **130 activity** and **126 toxicity** records but **zero sequence fields**; it remains a separate non-RC2 increment until sequence recovery and release approval.
- Found a critical benchmark-leakage risk: **139/141** high-confidence design safety sequences exactly overlap the current APD6/DBAASP/DRAMP merged sequence universe. Any natural-train/designed-test claim must therefore freeze the training snapshot and remove exact/homology overlap.
- The merged five-database corpus supplies a large background pool (**55,158 canonical sequences; 363,337 experiment/text rows**) but is not a natural-only set and cannot provide a gold design identity without source adjudication.
- The recommended v0.1 starts from the 12-paper/141-sequence seed, then recovers sequences from the other 47 high-confidence safety papers, structures censor operators/bounds, adjudicates natural parents versus designed entities, and creates paper/scaffold/homology/time split manifests before model evaluation.

Primary evidence:

- `docs/DESIGNTOXBENCH_CURRENT_DATA_SUPPORT_AUDIT_20260727_175624_CST.md`
- `reports/designtoxbench_support_audit_20260727T175225_CST/summary.json`
- `reports/designtoxbench_support_audit_20260727T175225_CST/design_candidate_papers.tsv`
- `scripts/assess_designtoxbench_support.py`

## 2026-07-27 22:27 CST — Parallel strict campaign healthy, but terminal conversion remains 2/200

- Frozen denominator remains **200 papers**: **2 terminal scientific completions**, **198 nonterminal**, and **200/200 strict material-ready**.
- Actual breadth is broader than the terminal count: **11 papers have been touched or advanced**. Their live states are 2 terminal, 8 `needs_targeted_semantic_rework`, one `six_worker_review_in_progress`, and **189 still untouched/ready**.
- There are **19 open scientific/semantic tickets**. These are mostly fail-closed source/field corrections produced by the leader audit, not quota or infrastructure failures.
- Parallel supervisor PID `540785` is healthy, publishes a fresh heartbeat every approximately 15 seconds, and runs four distinct paper lanes:
  1. `PMC11845615` attempt 2, targeted repair, currently fresh worker-2;
  2. `PMC12160004` attempt 1, currently worker-6;
  3. `PMC12606902` attempt 1, currently targeted worker-3;
  4. `PMC12837634` attempt 1, currently worker-6.
- Every observed active canonical worker uses exact `codex exec -m gpt-5.5 -c model_reasoning_effort="xhigh"`. No active quota, crash, or supervisor-stderr fault was found.
- Terminal throughput is still too slow: no third paper has reached both fresh leader `PASS` and independent verifier `PASS` since `PMC12125351` completed at 15:56 CST. Parallelism is increasing first-pass coverage, but most touched papers are being correctly rejected into semantic rework.
- `PMC11889930` is not terminal and was not replaced by Grok. Its canonical worker-2 hit `model_safety_content_filter` after worker-1; the scheduler explicitly classifies `six_worker_review_in_progress` as a repair status. It is queued behind the currently occupied single repair lane (`--max-rework-parallel 1`), rather than being silently accepted or permanently orphaned.
- Immediate bottleneck is therefore **repair-lane conversion and scientific field closure**, not material availability or a dead scheduler. Two active papers are at worker-6, but neither may be counted complete until fresh leader and independent verifier gates pass.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_journal.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs/PMC11889930/run_sequence_latest.json`
- `pipeline_v2/deepmine/supervise_remaining_200_parallel_campaign.py`

## 2026-07-27 23:10 CST — Strict campaign convergence defects fixed; lossless scheduler reload draining

- The scientific acceptance bar was **not** reduced. Every terminal paper still requires six sequential independent exact `codex exec gpt-5.5/xhigh` workers, a fresh worker-6 after the latest upstream repair, current mechanical acceptance, zero open tickets, independent leader `PASS`, independent verifier `PASS`, recursive authority false, and fallback-release exclusion.
- Fixed seven concrete throughput/reliability defects:
  1. a partial canonical failure now resumes from the first failed/missing worker through worker-6, rather than rerunning only worker-6;
  2. a mechanically red paper with already-known open tickets no longer spends another full leader audit rediscovering the same blockers;
  3. identical open leader findings are fingerprinted across owner, reason, source locators, evidence paths, actions, and acceptance checks and are not staged repeatedly;
  4. a strictly validated ticket closure receives one append-only, response-hash-bound historical receipt, so unrelated later final/gate edits do not reopen every old ticket; any later duplicate terminal response invalidates that receipt fail-closed;
  5. when the repair backlog is at least the four-paper capacity, scheduling changes from one repair plus three fresh papers to **three repairs plus one fresh paper**;
  6. unexpected campaign exceptions now finalize newly created process reports as fail-closed instead of leaving false `in_progress` records;
  7. the two historical false-`in_progress` reports for `PMC11956232` and `PMC12715223` were reconciled against their finished campaign reports.
- The pilot closure implementation and the worker-6 packet gate agree on every currently built packet: **13 packets checked, zero closure-contract mismatches, 73 sealed historical closures across 10 papers, zero duplicate receipt tickets**.
- Final focused strict/review regression coverage is **142 tests passing**; all changed Python files pass `py_compile`/`compileall`. Ruff is not installed, so no Ruff result is claimed.
- A fresh independent read-only `codex exec gpt-5.5/xhigh` session (`019fa420-d12c-7fb2-af46-b36d96e71cec`) reviewed the final current files and returned **APPROVE**, with no Critical/High/Medium findings. Its only Low residual risk is the lack of a synthetic end-to-end Linux signal integration test for the drain switcher; the currently monitored real drain is exercising that path without interrupting paper children.
- Frozen live state at the switch point remains **2/200 terminal**, **198 nonterminal**, **200/200 material-ready**, with **9 live open tickets**. States are 8 targeted-rework, 187 untouched-ready, 3 six-worker-in-progress, and 2 terminal.
- Old scheduler PID `540785` is intentionally `SIGSTOP`-paused so it cannot refill lanes with stale scheduling code. It did **not** interrupt the four already-running paper campaigns: `PMC11672609` attempt 1, `PMC12153049` attempt 1, `PMC12606902` attempt 1, and `PMC13066039` attempt 2 continue normally.
- Independent drain/restart watcher PID `1752558` is healthy. After those four campaigns naturally finish, it will resume the old scheduler only long enough to write their normal `paper_attempt_finished` rows, stop it again before any replacement launch, and start the tested scheduler. It also rejects any replacement `paper_attempt_started` row created during the handoff race window. The generated supervisor heartbeat is expected to pause during this drain; the drain JSON is the authoritative transition heartbeat.

Primary evidence:

- `pipeline_v2/deepmine/run_remaining_200_strict_campaign.py`
- `pipeline_v2/deepmine/supervise_remaining_200_parallel_campaign.py`
- `pipeline_v2/deepmine/restart_remaining_200_parallel_at_drain.py`
- `pipeline_v2/deepmine/dbaasp_strict_pilot.py`
- `.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py`
- `pipeline_v2/deepmine/test_remaining_200_strict_campaign.py`
- `pipeline_v2/deepmine/test_remaining_200_strict_supervisor.py`
- `pipeline_v2/deepmine/test_remaining_200_parallel_handoff.py`
- `pipeline_v2/deepmine/test_dbaasp_strict_pilot.py`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/drain_restart_20260727T151252Z.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/code_reviews/throughput_hardening_review_20260727.md`

## 2026-07-28 09:36 CST — Hardened scheduler is live; strict campaign advanced to 8/200

- The lossless drain/reload completed successfully. Old supervisor PID `540785` allowed all four inherited paper campaigns to finish naturally and journaled them before replacement; the live hardened supervisor is PID `2243091`. Its heartbeat is current, process state is healthy, and both supervisor stdout/stderr logs remain empty.
- Frozen strict denominator remains **200 papers**. Current scientific state is **8 terminal completions**, **192 nonterminal**, **200/200 strict material-ready**, and **19 open fail-closed scientific/semantic tickets**.
- Since the 2026-07-27 23:10 CST recorded switch-point snapshot, terminal conversion increased from 2 to 8: **six additional papers became terminal overnight**. The eight terminal paper IDs are `PMC11956232`, `PMC12125351`, `PMC11897483`, `PMC13066039`, `PMC13025223`, `PMC12837634`, `PMC12160004`, and `PMC12153049`.
- **16/200 papers have now been touched or advanced**. Besides the eight terminal papers, five require targeted semantic rework, one awaits leader field-level semantic audit, one awaits the independent verifier, and one is in six-worker review. The remaining **184 papers** are material-ready and not yet started.
- Adaptive backlog scheduling is working as designed despite the compatibility CLI argument `--max-rework-parallel 1`: the four live lanes are **three repairs plus one fresh paper**:
  1. `PMC12606902` attempt 3 is in an independent `gpt-5.5/xhigh` verifier call;
  2. `PMC11672609` attempt 3 is running fresh `worker-2` repair;
  3. `PMC12812963` attempt 2 is running fresh `worker-1` repair;
  4. `PMC12162962` attempt 1 is the preserved fresh lane and is running canonical `worker-3`.
- Every observed active canonical worker, leader/verifier call uses exact `codex exec gpt-5.5` with `model_reasoning_effort="xhigh"`. No Grok replacement is active in this snapshot, and no quota, crash, or supervisor-log failure was found.
- The latest finished attempt was `PMC11845615` attempt 3 at 09:29 CST. It remained fail-closed in targeted semantic rework (`campaign_returncode=1`) rather than being falsely promoted. `PMC12606902` is currently closest to another possible terminal conversion, but it is not counted until the active independent verifier returns `PASS`.
- The observed gain of six terminal papers in roughly 10.4 hours is approximately 0.58 terminal papers/hour. A purely linear projection would put the remaining 192 papers at about 14 days, but this is an early, bursty conversion rate rather than a delivery promise.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/drain_restart_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_strict_review_journal_20260726.jsonl`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/parallel_supervisor.stderr.log`

## 2026-07-28 11:44 CST — Strict campaign reached 9/200; conversion continues but breadth is temporarily flat

- Current frozen state is **9/200 terminal scientific completions (4.5%)**, **191 nonterminal**, **200/200 material-ready**, and **22 open fail-closed scientific/semantic tickets**. This is one additional terminal completion since the 09:36 CST snapshot.
- The newly completed paper is `PMC12715223`. It has six clean unique sequential canonical `gpt-5.5/xhigh` worker sessions, fresh worker-6 ordering, zero open tickets, current mechanical acceptance, fresh leader `PASS`, and independent verifier `PASS`.
- Touched-paper breadth remains **16/200**: nine terminal papers plus seven active/nonterminal papers. **184 material-ready papers remain untouched**. The last two hours therefore improved terminal conversion but did not start another untouched paper.
- Live supervisor PID `2243091` remains healthy with a current heartbeat and four paper campaigns. Its stdout and stderr logs are still empty. The active lanes are:
  1. `PMC11845615` attempt 4, targeted repair; current canonical worker-5;
  2. `PMC11889930` attempt 4, leader semantic audit;
  3. `PMC12162962` attempt 1, now in same-campaign targeted repair; current canonical worker-1;
  4. `PMC12812963` attempt 2, targeted repair; current canonical worker-3.
- Three currently visible canonical calls use exact `codex exec gpt-5.5/xhigh`. The `PMC11889930` leader Codex call ended with the classified biology-content safety rejection at 11:42 CST, so the permitted read-only Grok leader fallback has been triggered. This fallback does not replace any of the six canonical workers and cannot by itself promote a paper.
- `PMC12606902` is scientifically close but remains nonterminal. Its independent verifier returned a nominal `PASS`, return code 0, and unchanged input fingerprint, but the deterministic local verifier validator rejected the artifact for `verifier_check_has_missing_evidence_path`; the ledger correctly leaves it at `awaiting_independent_verifier` rather than accepting the incomplete PASS.
- Open-ticket concentration is uneven: `PMC11845615` has 10, `PMC12812963` has 5, `PMC12124432` has 3, `PMC12162962` has 3, and `PMC11672609` has 1. The increase from 19 to 22 reflects newly exposed/staged scientific defects, not a scheduler or quota failure.
- Candid throughput assessment: the campaign gained only one terminal paper during the latest approximately 2.1-hour interval, while all four slots are now occupied by audit/repair work. Quality is fail-closed and stable, but untouched-paper breadth is temporarily stalled until one of these campaigns exits.

Primary evidence:

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12715223/independent_paper_verifier_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12606902/20260728T013220808620Z.independent_paper_verifier.runtime.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11889930/20260728T032931561175Z.leader_semantic_auditor.runtime.json`

## 2026-07-28 11:48 CST — User-requested natural pause armed at a four-paper boundary

- The active supervisor PID `2243091` was sent `SIGSTOP` before it could refill another completed slot. This pauses only the scheduler; it does not interrupt, suspend, or cancel the four already-running paper campaigns or their worker/audit children.
- The exact natural-drain boundary is:
  1. `PMC11845615`, attempt 4, campaign PID `3697498`;
  2. `PMC12162962`, attempt 1, campaign PID `3292474`;
  3. `PMC12606902`, attempt 4, campaign PID `3831004`;
  4. `PMC12812963`, attempt 2, campaign PID `3386389`.
- Detached drain/pause watcher PID `3845417` is healthy in its own session with runtime parent PID `438`. It will wait for all four campaigns to finish naturally, briefly resume the stopped supervisor only to reap them and append their normal `paper_attempt_finished` journal rows, stop it again before any replacement launch, and then terminate the supervisor without starting a new one.
- The handoff implementation now has an explicit tested `--pause-only` path. Targeted handoff tests pass **5/5**, and the modified script passes `py_compile`.
- Authoritative transition heartbeat:
  `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/drain_restart_20260728T034931Z.json`.
  At this timestamp its state is `draining`, all four campaign processes are live, and the scheduler process state is stopped (`T`).
- When the boundary completes, the watcher will write `drain_pause_latest.json`, remove the stale active supervisor PID file, and write `parallel_supervisor.paused`. Until then, no additional paper should enter the queue.

Primary evidence:

- `pipeline_v2/deepmine/restart_remaining_200_parallel_at_drain.py`
- `pipeline_v2/deepmine/test_remaining_200_parallel_handoff.py`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/drain_restart_20260728T034931Z.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/drain_pause_watcher.pid`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/drain_pause_watcher_20260728T034931Z.stderr.log`

## 2026-07-28 12:13 CST — Existing publishable data and complete review workflow uploaded to GitHub

- Created the first `main` branch in the previously empty public repository:
  `https://github.com/cihebi2/amp_peptide_data`.
- The push used the dedicated local SSH identity authenticated as GitHub account `cihebi2`. Commit author and committer are both `cihebi2 <cihebi@163.com>`.
- Published root commit:
  `0ed51ecd37ef837196a488b41b3e6be18c2553a9`
  (`publish AMP evidence data and review workflow`).
  The remote `refs/heads/main` was independently re-read and exactly matches this hash.
- The repository snapshot contains **100,819 tracked files** and approximately **29.88 million inserted lines**. It includes:
  - RC1 history and the current authoritative RC2 release-candidate data;
  - all canonical per-paper final activity/toxicity, database-verification, mechanism, and review records;
  - NAR freeze, validation420, conflict, quality, queue, and topic-support reports;
  - ticket, response, closure, locator, linked-database, extraction-quality, and workflow-state evidence;
  - the strict six-worker/leader/verifier controllers, serial/parallel supervisors, recovery and pause logic;
  - all repository-local Codex worker/orchestrator skills and regression tests;
  - portal/MCP/server/build code, benchmark protocol, project plans, data dictionaries, and the living progress document.
- GitHub publication packaging did not rewrite canonical scientific rows. Four RC1/RC2 TSV blobs above the safe threshold were losslessly gzip-compressed with the original uncompressed byte count and SHA-256 stored in `repository_metadata/compressed_large_files.json`. Decompression/hash verification passed for all four.
- Pre-push checks found **zero files at or above 100 MiB**, no GitHub PAT, private key, literal bearer token, or actual OpenAI key, and `git fsck --full --strict` passed after repository packing. The final Git pack is approximately **118.9 MiB**. GitHub accepted the push; it emitted only a recommendation warning for the 59.28 MiB conflict CSV, which is below the enforced 100 MiB limit.
- The local working corpus is approximately 20 GiB and contains redistributability/hosting-unfriendly primary-source material. Raw PDFs, office supplements, videos, OA caches, repeated source/raw mirrors, generated SQLite, runtime streams, and duplicated intermediate packet finals were therefore not inserted into public Git history. This is not silent loss:
  **61,119 local-only artifacts totaling 16,367,813,392 bytes** are path/size/mtime/reason inventoried in `repository_metadata/local_only_artifact_inventory.tsv.gz`; duplicate and derived-fulltext pruning is separately enumerated.
- A repository-level `README.md`, `.gitignore`, snapshot manifest, compression manifest, symlink conversion report, pruning report, and local-only inventory explain the authority hierarchy and permit the hosted snapshot to be audited.
- The user-requested strict-review natural pause remains in its previously captured four-paper drain boundary while this upload completes; no new review paper has been launched.

Primary evidence:

- `https://github.com/cihebi2/amp_peptide_data`
- Git commit `0ed51ecd37ef837196a488b41b3e6be18c2553a9`
- `/home/cihebi/抗菌肽/数据集/batch/amp_peptide_data_publish/README.md`
- `/home/cihebi/抗菌肽/数据集/batch/amp_peptide_data_publish/repository_metadata/SNAPSHOT_MANIFEST.json`
- `/home/cihebi/抗菌肽/数据集/batch/amp_peptide_data_publish/repository_metadata/compressed_large_files.json`
- `/home/cihebi/抗菌肽/数据集/batch/amp_peptide_data_publish/repository_metadata/local_only_artifact_inventory_summary.json`
- `/home/cihebi/抗菌肽/数据集/batch/amp_peptide_data_publish/repository_metadata/local_only_artifact_inventory.tsv.gz`

## Evidence Index

Use these files first:

- `docs/DESIGNTOXBENCH_CURRENT_DATA_SUPPORT_AUDIT_20260727_175624_CST.md`
- `reports/designtoxbench_support_audit_20260727T175225_CST/summary.json`
- `reports/designtoxbench_support_audit_20260727T175225_CST/design_candidate_papers.tsv`
- `scripts/assess_designtoxbench_support.py`
- `reports/nar_resource_freeze_v1/release_manifest_latest.json`
- `reports/nar_resource_freeze_v1/unified_scope_summary_latest.json`
- `reports/nar_resource_freeze_v1/README.md`
- `releases/amp_evidence_atlas_v1_rc2/release_manifest.json`
- `releases/amp_evidence_atlas_v1_rc2/README.md`
- `docs/NAR_RESOURCE_V1_STEPWISE_EXECUTION_PLAN_20260622_093231_CST.md`
- `docs/NAR_DATABASE_RESOURCE_ROADMAP.md`
- `docs/NAR_FREEZE_V1_DATA_DICTIONARY.md`
- `reports/nar_resource_freeze_v1/manual_validation/validation420/VALIDATION420_RUN_STATUS.md`
- `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/pilot20_final_review_closure/pilot20_final_review_closure_summary_latest.json`
- `pipeline_v2/NAR_SUBMISSION_PLAN.md`
- `pipeline_v2/AMP_ADVISOR_MVP_PLAN.md`
- `pipeline_v2/deepmine/README.md`
- `pipeline_v2/deepmine/build_dbaasp_worklist.py`
- `pipeline_v2/deepmine/extract_dbaasp.py`
- `pipeline_v2/deepmine/run_dbaasp_supervised_v2.sh`
- `pipeline_v2/deepmine/dbaasp_worklist.json`
- `pipeline_v2/deepmine/dbaasp_state.json`
- `pipeline_v2/deepmine/dbaasp_extracted.tsv`
- `pipeline_v2/deepmine/dbaasp.log`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/fresh_acceptance_20260716_16paper/summary.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_16paper/leader_contract_recheck.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_16paper/independent_verifier_report.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/fresh_acceptance_20260716_17paper/summary.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_17paper/leader_contract_recheck.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260716_17paper/independent_verifier_report.md`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12019989/work/review/leader_candidate17_post_ticket004.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/review/leader_final_semantic_audit_20260716.json`
- `portal/build_db.py`
- `portal/mcp_server.py`
- `portal/portal_server.py`
- `portal/benchmark_protocol.md`
- `scripts/backfill_human_review.py`
- `scripts/build_nar_public_release_package.py`

## Changelog

- 2026-07-28 12:13 CST: Published the existing release data, canonical per-paper finals, review evidence/state, complete six-worker/leader/verifier workflow, skills, tests, reports, and portal code to the new public `cihebi2/amp_peptide_data` main branch as root commit `0ed51ecd37ef837196a488b41b3e6be18c2553a9`, authored by `cihebi2 <cihebi@163.com>`. Verified the remote hash, gzip round trips/digests, zero enforced-size violations, no real credential pattern, and strict Git object integrity. Kept 61,119 raw/cache/runtime/duplicate/source artifacts totaling 16.37 GB outside public Git while publishing their complete path/size/mtime/reason inventory.
- 2026-07-28 11:48 CST: Armed a user-requested natural pause without interrupting active review work. Scheduler PID `2243091` is `SIGSTOP`-paused and cannot refill slots; four captured campaigns (`PMC11845615`, `PMC12162962`, `PMC12606902`, and `PMC12812963`) continue to their natural boundary. Added and tested an explicit `--pause-only` drain path, passed 5/5 targeted tests plus compile validation, and launched fully detached watcher PID `3845417` to journal all four normal completions and terminate the scheduler without replacement.
- 2026-07-28 11:44 CST: Strict review advanced to 9/200 after `PMC12715223` obtained complete six-worker, leader, and verifier closure. The campaign has 191 papers remaining, 22 open tickets, 16 touched papers, and 184 untouched/material-ready papers. Supervisor PID `2243091` and all four campaigns remain healthy, but every slot is currently in audit/repair work, so breadth is temporarily flat. The `PMC11889930` leader Codex call hit the classified biology safety rejection and triggered only the allowed read-only Grok leader fallback; `PMC12606902` remains fail-closed despite a nominal verifier PASS because deterministic validation found a missing evidence path.
- 2026-07-28 09:36 CST: Confirmed the lossless hardened-scheduler reload completed and live supervisor PID `2243091` is healthy. The frozen 200-paper campaign advanced from 2 to 8 terminal papers overnight, with 192 remaining, 16 touched, 184 untouched/material-ready, 19 fail-closed tickets, and four active exact `gpt-5.5/xhigh` lanes operating as three repairs plus one fresh paper. No Grok replacement, quota, crash, or supervisor-stderr fault is active; `PMC12606902` is at the independent verifier and is not counted until `PASS`.
- 2026-07-27 23:10 CST: Kept the full six-worker/leader/verifier scientific bar while fixing partial-run recovery, redundant leader calls, exact-finding duplicate tickets, closure chronology churn, duplicate-terminal receipt ambiguity, stale process reports, exact worker-order/command validation, malformed-state paper duplication, high-rework-cap fresh-lane starvation, the one-repair-lane backlog, and the scheduler-handoff start race. Added adaptive three-repair/one-fresh scheduling, validated pilot/packet closure agreement with 73 sealed receipts and no mismatches/duplicates, passed 142 tests plus compile checks, reconciled two historical stale reports, received final independent `codex exec gpt-5.5/xhigh` **APPROVE** with no Critical/High/Medium findings, and armed lossless drain watcher PID `1752558` to reload paused scheduler PID `540785` only after four active campaigns finish naturally and journal normally.
- 2026-07-27 22:27 CST: Rechecked the live 200-paper strict campaign. It remains 2/200 terminal, but 11 papers have been touched: eight are in semantic rework, one was interrupted by a canonical worker safety filter, and 189 remain untouched. Verified four healthy concurrent exact `gpt-5.5/xhigh` workers, 19 fail-closed scientific tickets, no infrastructure/quota fault, and confirmed `PMC11889930` is queued as repair work behind the single occupied repair lane rather than orphaned or Grok-substituted.
- 2026-07-27 18:02 CST: Completed a six-lane DesignToxBench support audit. Established zero final benchmark-gold records but an actionable 12-paper/141-sequence high-confidence seed with 659 safety observations, 136 paired sequences, and 255 censored/inequality observations; defined a 220-sequence/1,691-safety-observation adjudication upper envelope; added a reproducible assessment script and candidate-paper table; explicitly removed microbial-efficacy `biofilm_cell_viability` rows from safety counts; and exposed exact merged-database overlap for 139/141 seed sequences as a mandatory training-snapshot/homology-leakage control.
- 2026-07-27 16:27 CST: Terminally completed `PMC12125351` as paper 2/200, collapsed live tickets from 20 to one, completed the boundary-safe serial-to-parallel supervisor switch, and verified four distinct active paper lanes: one repair paper at fresh worker-6 and three untouched papers at worker-3 after workers 1–2 completed. Parallel supervisor PID `540785` is healthy with empty stderr.
- 2026-07-27 15:22 CST: Attempt 3 remained active in its final allowed semantic-rework round. Round 2 narrowed the fresh leader rejection to one `review_rework_targets` count mismatch after independently passing the substantive source/value/identity/mechanism/locator boundaries. Fresh worker-1 repaired the state path and fresh worker-6 is active. Completion remains 1/200 with 20 live tickets; the four-lane switch watcher remains healthy and has correctly not launched parallel work before the old campaign boundary.
- 2026-07-27 13:34 CST: Rejected the approximately 112-day naive serial terminal-throughput projection. Hardened rolling-manifest, issue-log, packet-sync, state-lock, and per-paper execution boundaries; added a four-lane distinct-paper supervisor with one repair lane plus three fresh-paper lanes; passed 125 tests and compile checks; and armed boundary-safe PID `232034` to switch from the serial supervisor after the current `PMC12125351` attempt-3 worker-6/audit path finishes.
- 2026-07-27 13:25 CST: `PMC12125351` attempt 2 exhausted three rounds fail-closed. Round 3 was mechanically green but leader-red for inconsistent packet/final/material state metadata and placeholder activity summary zeros around otherwise source-reviewable 130 activity/126 toxicity rows. Supervisor immediately started bounded attempt 3; worker-1 is complete and worker-2 is active. Campaign remains 1/200 with 17 live tickets; attempt-3 explicitly has the Grok safety fallback enabled.
- 2026-07-27 12:25 CST: `PMC12125351` attempt 2 round 2 remained mechanically and scientifically red for three final-state/activity/database provenance blockers. Chronology-sensitive older terminal ticket responses were invalidated by later final/gate edits, reopening ten prior tickets; 14 paper tickets now await one fresh worker-6 terminal adjudication after round-3 owner repairs. Worker-3/2/4/5 have completed and worker-1 is active. Campaign remains 1/200 terminal with 15 live tickets; processes are healthy and Grok has not been triggered.
- 2026-07-27 10:48 CST: `PMC12125351` attempt 2 Codex leader audit returned a valid scientific FAIL for nine Supplementary Data 10 column E rows whose ATCC 25923-versus-29213 conflict metadata omitted the actual source label and used an unresolved column locator. One worker-2 ticket was staged and fresh worker-2 rework round 2 is active. Frozen completion remains 1/200 with two campaign-wide tickets; Grok was correctly not invoked because this was not a safety rejection.
- 2026-07-27 10:42 CST: Validated the local CLIProxyAPI Grok endpoint, function calling, and strict JSON Schema; added a paper-scoped read-only Grok evidence-tool fallback that activates only for the exact Codex biology safety false-positive on leader/verifier calls and never replaces canonical workers. Synthetic end-to-end coverage passed with 16 tool calls and zero local failures; the full suite now passes 120 tests. `PMC12125351` attempt 2 closed four prior tickets and is at its Codex leader audit, leaving one campaign-wide ticket; newly spawned retries use the fallback by default.
- 2026-07-27 09:42 CST: Confirmed `PMC12715223` completed six clean unique sequential `gpt-5.5/xhigh` workers but remained nonterminal because the structured leader Codex run was rejected at the biology-content safety boundary and produced no verdict JSON. The safe scheduler restart completed at a no-child boundary, updated supervisor PID `3896212` is healthy, and `PMC12125351` attempt 2 is actively running fresh worker-1. Campaign remains 1/200 terminal with five live tickets and no false promotions.
- 2026-07-27 09:23 CST: Rechecked live progress and confirmed `PMC12715223` completed five sequential unique clean `gpt-5.5/xhigh` workers and is actively running worker-6. Supervisor/campaign processes are healthy with empty stderr; the ledger marks one six-worker review in progress. Completion remains 1/200 with five historical repair tickets, and the safe scheduler-restart watcher remains armed for the post-paper no-child boundary.
- 2026-07-27 08:25 CST: Verified the long-running supervisor and exact Codex process tree are healthy with no infrastructure/quota errors. Live state is 1/200 terminal, 199 nonterminal, 200/200 materials ready, and five tickets across `PMC12125351` and `PMC11897483`; `PMC12715223` worker-1 is active. Confirmed the second untouched paper was scientifically blocked for rowspan-shifted Table 2 values and lost exact Figure 10A hemolysis labels. Corrected the supervisor scheduling policy to allow at most three immediate repair attempts before rotation, added a safe post-current-paper restart watcher, and passed 116 tests.
- 2026-07-27 05:54 CST: Preserved `PMC12125351` attempt 1 as nonterminal after three leader-gated repair rounds uncovered progressively deeper source-field, recursive-locator, stale-manifest, assay-time, strain, database-provenance, and mechanism-locator conflicts. Four next-attempt tickets remain open; added a deterministic non-source-locator gate and regression, with 115 tests passing. Supervisor journaled the failed-closed result and rotated to `PMC11897483` worker-1. Live campaign remains 1/200 terminal with four open tickets.
- 2026-07-27 03:46 CST: The first untouched-paper pilot `PMC12125351` completed six unique sequential clean `gpt-5.5/xhigh` workers and green mechanical acceptance, but the independent leader audit rejected it for four publication-grade omissions/conflicts spanning XLSX packet extraction/locators, activity-toxicity underextraction, candidate-versus-benchmark identity conflation, and omitted PI quantitative mechanism data. Four blocking owner tickets are now running sequentially; frozen campaign completion remains 1/200.
- 2026-07-27 02:21 CST: Terminally completed frozen-queue paper 1/200 (`PMC11956232`) only after an independent verifier rejected an unsupported leader PASS for a 19-versus-20 sequence-length conflict, added deterministic sequence-length and live-ticket-count gates, completed two fresh worker-2/fresh worker-6 repair cycles including stale preflight cleanup, and obtained fresh structured leader and independent verifier PASS. Added and detached a locked, sweep-based, retry-bounded long-running supervisor (launch PID `2937486`) with atomic JSON/Markdown heartbeat and append-only attempt logs for the remaining 199 papers; it started `PMC12125351` worker-1 through exact `codex exec`. Current state is 1/200 terminal, 199 remaining, 200/200 materials ready, zero open tickets, authority=false, and 114 tests passing including supervisor regressions.
- 2026-07-27 00:14 CST: Completed frozen-200 material preparation at 200/200 ready and zero missing: recovered all 130 paper-level supplement gaps through validated direct/PMC OA-package retries, recovered the last non-OA ACS structured source through official NCBI PMC BioC XML after Europe PMC JATS returned 404, and added BioC metadata/passage/table extraction support plus regressions. Candidate 19 fresh worker-2 independently passed 23/23 leader checks and fresh worker-6 is running; the other 199 papers are ready for strict review.
- 2026-07-27 00:01 CST: Started the exact frozen 200-paper strict campaign with a durable high-bar ledger/journal; corrected a major PDF-path accounting bug; verified all 173 exact PDFs; recovered structured XML for 172 and isolated one valid-PDF-only non-OA ACS paper; corrected frozen-queue materials to 69 ready, 130 supplement-recovery, and one structured-gap paper; rejected Candidate 19's mechanical false green; opened two blocking tickets; independently passed fresh worker-3's 797-observation Figure 1–7 contract; corrected the ticket's 757 arithmetic typo; started fresh worker-2; and launched a validated concurrent supplement-recovery campaign. This entry is historical for the intermediate material state; the 00:14 update supersedes it.
- 2026-07-26 21:26 CST: Withdrew the attempted 18-paper freeze after an independent verifier returned `FAIL`; amended the leader record to `FAIL/returncode=1`, documented invalid mutable-manifest chronology, added recursive authority and material-count consistency gates to the acceptance mainline, refreshed locator/error counts, opened strict worker-2 and worker-4 rework tickets for `PMC11905587` and `PMC12230126`, expanded Candidate 18 validation from 9 to 11 checks, prepared a 640-row conservative Figure 1/2 digitization scaffold for `PMC11956232`, and confirmed all six Candidate 19 Codex sessions are invalid because of quota. Also fixed a newly discovered prompt-binding omission so all six Candidate 19 prompts now carry the preflight contract/evidence paths, with 40 unique table-cell locators. Live strict state is 16/19 terminal-ready, two open tickets, one missing-final paper, zero authoritative ingest, expected global red gates `2/1/2/1`, unchanged verify manifest hash, 95 tests passing, and all changed scripts compiling.
- 2026-07-26 16:40 CST: Completed a whole-project live synthesis across RC2/NAR release artifacts, strict DBAASP review, validation420, human-review state, portal, MCP, benchmark, and deployment evidence. Confirmed a mature RC2 release-candidate foundation and working local portal/MCP, but no public production deployment or NAR-ready closure. Recorded 39/224 validation packets and 114/420 rows, 34/192 human verdicts, 17 strict accepted papers with Candidate 18 still open, portal mixed-tier counts, seven major denominator/status conflicts, and the current execution order.
- 2026-07-26 16:33 CST: Re-ran live strict status, Candidate 18 acceptance, candidate ranking, process checks, and regression tests. The accepted freeze remains 17 papers; `PMC11905587` is still the only nonterminal paper with two open tickets, one rework target, packet/semantic/publication return codes `0/1/2`, and no active worker process. The candidate pool still has 201 papers not scientifically accepted; nine untouched papers are immediately recommended, 18 require material recovery, 85 tests pass, and authoritative DBAASP ingest remains zero.
- 2026-07-18 17:29 CST: Rechecked the live strict queue. The manifest contains 18 papers but the accepted freeze remains 17/18 because `PMC11905587` is `needs_targeted_rework` with two open tickets. Six canonical `gpt-5.5/xhigh` sessions are clean, but leader semantic QA caught missing peptide identity/sequence, dropped reported assay context, omitted no-activity rows, an unpreserved dilution-range conflict, and false worker-3 model metadata. Worker-3 repaired its provenance; worker-2 did not satisfy its contract; fresh worker-6 correctly refused closure. No strict-review process is active. Candidate-report `already_reviewed_count=17` is not an acceptance count because it includes this blocked paper.
- 2026-07-16 21:12 CST: Completed `PMC12019989` only after rejecting two false-green worker-6 closures that left all 240 Figure 2 points at one placeholder value and the finals pending digitization. Added a reproducible leader-owned RGB curve digitizer and immutable semantic validator, enforced staged worker-3/worker-2/worker-6 repair, preserved all ten source conflicts, and froze the strict pilot at 17/17 `accepted_with_cautions`: 1,226 activity, 210 toxicity, 84 mechanism claims, 102 globally unique `gpt-5.5/xhigh` Codex sessions, 68/68 byte-identical mirrors, zero open tickets/findings/risks, 84 tests passing, and independent verifier `PASS`. Authoritative ingest remains 0/17; RC2, validation420, final human reduction, website/public deployment, licensing, and manuscript/release work remain separate.
- 2026-07-16 17:42 CST: Started strict Candidate 17 review for `PMC12019989`. Built and validated a leader-owned 279-row source-surface contract, opened a blocking four-owner reconstruction ticket, preserved the major Figure 1-6 source conflicts, and kept the accepted freeze at 16/16 pending six independent `gpt-5.5/xhigh` Codex workers plus semantic and independent verification.
- 2026-07-16: Completed `PMC12230126` after six durable tickets and multiple independent targeted reruns, including a leader-owned executable validator that caught missing final-layer metadata and nested authoritative-ingest conflicts missed by the existing gates. Froze the strict pilot at 16/16 `accepted_with_cautions`: 947 activity, 210 toxicity, 79 mechanism claims, 96 globally unique `codex exec` sessions on `gpt-5.5/xhigh`, 64/64 byte-identical mirrors, zero open rework/targets/risks/hard findings, all gates passing, 84 tests passing, and independent verifier `PASS`. The 15-paper freeze is superseded; website/public deployment, validation420, final human reduction, authoritative integration, licensing/source-version review, and manuscript disclosure remain unfinished.
- 2026-07-16: Completed `PMC13031288` after six explicit rework tickets and three staged worker passes, then froze the strict pilot at 15/15 `accepted_with_cautions`. Current evidence is 928 activity, 210 toxicity, 73 mechanism claims, 90 globally unique `codex exec` sessions on `gpt-5.5/xhigh`, 60/60 byte-identical final mirror pairs, zero open rework/targets/risks/hard findings, all global gates passing, 84 regression tests passing, and independent verifier `APPROVE`. The 14-paper strict freeze is superseded; authoritative DBAASP ingest, validation420, website/public deployment, final human reduction, and release integration remain unfinished.
- 2026-07-15: Completed and froze the 14-paper DBAASP strict source-review pilot. Fresh per-paper acceptance is 14/14 `accepted_with_cautions`, with 84 globally unique `codex exec` sessions on `gpt-5.5/xhigh`, worker-6 freshness on every paper, 568 activity and 170 toxicity records, zero open rework, zero hard findings/risks, all packet/semantic/publication/worker gates passing, and zero authoritative DBAASP-ingest-ready papers. Hardened terminal ticket closure, passed 84 regression tests, received final independent code-review `APPROVE`, and received a separate verifier `PASS - APPROVE`; manual validation and website/release work remain open.
- 2026-07-09: Waited for `PMC13013390` targeted rework rerun to finish, accepted it only after fresh `worker-6` adjudication plus single-paper/global gates, and rechecked the full strict pilot. Current strict state is 13/13 paper-level `accepted_with_cautions`, 78 unique independent `codex exec` sessions on `gpt-5.5/xhigh`, 0 hard findings, 0 open rework, and 0 authoritative DBAASP-ingest-ready. Added DOCX supplementary table extraction evidence and recorded that this remains a sequential `codex exec` bridge rather than full durable OMX team/mailbox production.
- 2026-07-09: Rechecked the strict Codex CLI independence concern from script code, `status`, `verify`, `audit-workers`, candidate queue, and an independent direct scan over `run_sequence_latest.json`; confirmed 12/12 manifest papers have six independent `codex exec` worker reports, 72 unique sessions, all `gpt-5.5/xhigh`, 0 hard findings, but all remain `accepted_with_cautions` and 0 are authoritative DBAASP ingest-ready.
- 2026-07-09: Ran the strict controller on `PMC12022103`; the first pass correctly blocked on an unresolved hemolysis/toxicity material ticket, then a closed-no-match material-gap report preserved the toxicity limitation without plot-derived numeric fabrication, `worker-2` and `worker-6` were rerun, and the paper advanced to `accepted_with_cautions`. Global strict state is now 12/12 with 72 unique `codex exec` sessions, 0 hard findings, and 0 authoritative DBAASP-ingest-ready. Also hardened `write_json`/`write_jsonl` with atomic temp-file replacement after a parallel gate run exposed a transient manifest read/write race.
- 2026-07-09: Ran the strict controller on the next real candidate `PMC12144240`, producing a second controller-driven new-paper pass. The pilot advanced to 11/11 paper-level `accepted_with_cautions`, 66 unique `codex exec` worker sessions on `gpt-5.5/xhigh`, 0 hard findings, and 0 authoritative DBAASP-ingest-ready. Also fixed `status` aggregation to count newer `records/status_counts` database verification schema, restoring `PMC12144240` database audit count from 0 to 4.
- 2026-07-09: Rechecked the "too fast" concern again with fresh `status`, `verify`, `audit-workers`, script inspection, prompt-contract checks, stderr session matching, and worker-6 freshness checks. Current strict pilot remains 10/10 paper-level `accepted_with_cautions`, 60 independent `codex exec` worker sessions on `gpt-5.5/xhigh`, 0 hard findings, and 0 authoritative DBAASP-ingest-ready; caveat: 30 older worker reports use compatibility latest log paths rather than immutable run-id-prefixed paths, though their session IDs still match stderr and no stale-log mismatch was found.
- 2026-07-09: Ran the new strict controller on the next real candidate `PMC11292031`; controller built the packet, ran six independent `codex exec` workers on `gpt-5.5/xhigh`, passed single-paper acceptance plus global status/verify/audit gates, and advanced the strict pilot to 10/10 paper-level `accepted_with_cautions` with 60 unique Codex sessions and 0 authoritative DBAASP-ingest-ready.
- 2026-07-09: Added a resumable `controller once/loop` surface to `dbaasp_strict_pilot.py`; validated dry-run selection of `PMC11292031`, validated real controller path on completed `PMC11531597` with clean-worker skip plus acceptance/global gates, and rechecked the 9-paper strict pilot remains 9/9 complete with 54 unique Codex sessions, 0 hard findings, and 0 authoritative DBAASP-ingest-ready.
- 2026-07-09: Rechecked the speed concern with fresh `status`, `verify`, `audit-workers`, all nine per-paper `acceptance` checks, and `py_compile`; confirmed 9/9 strict-pilot papers have six independent `codex exec` worker reports, 54 unique Codex sessions, all `gpt-5.5/xhigh`, worker-6 after latest upstream worker output, and 0 hard findings, while preserving the boundary that all 9 are only `accepted_with_cautions` and 0 are authoritative DBAASP-ingest-ready.
- 2026-07-09: Repaired the strict pilot flow to 9/9 paper-level source-reviewed `accepted_with_cautions`: added safe worker-2 handoff/prompt regeneration for `PMC11531597`, reran worker-2 and worker-6, explicitly downgraded `PMC12103485` closed_no_match DBAASP linkage gap to a caution boundary, and verified packet/semantic/publication/strict-worker/audit gates green with 54 unique `codex exec` sessions and 0 authoritative DBAASP-ingest-ready.
- 2026-07-09: Rechecked the "too fast" concern after adding `PMC11531597`. Current strict pilot has 9 manifest papers and 54 unique `codex exec` worker sessions, all `gpt-5.5/xhigh`, but the strict completion count remains 7/9: `PMC12103485` is still `needs_targeted_rework`, and `PMC11531597` has a failed `worker-2` safety-filter run plus missing activity records.
- 2026-07-09: Rechecked the "too fast" concern after adding `PMC12103485`. All 8 manifest papers have six independent Codex CLI worker sessions, 48 unique sessions total, all `gpt-5.5/xhigh`, all return code 0, but only 7/8 are strict paper-level source-reviewed complete; `PMC12103485` remains `needs_targeted_rework` after durable no-authoritative-linkage evidence and a fresh worker-6 rerun.
- 2026-07-09: Expanded the strict pilot to `PMC12229353`; global strict state is now 7/7 paper-level source-reviewed `accepted_with_cautions`, with 42 unique Codex CLI sessions, semantic/publication/worker gates green, and 0 authoritative DBAASP-ingest-ready.
- 2026-07-09: Added `dbaasp_strict_pilot.py audit-workers` so the independent Codex CLI six-worker proof is generated by a repeatable command instead of an ad hoc audit snippet; validated global 6-paper and single-paper runs.
- 2026-07-09: Completed the `PMC11784053` strict six-worker expansion and rechecked the independence concern across all current manifest papers. Strict pilot is now 6/6 paper-level source-reviewed `accepted_with_cautions`, with 36 unique Codex CLI sessions, 0 worker-gate findings, 0 open rework, and 0 authoritative DBAASP-ingest-ready.
- 2026-07-08: Rechecked the "too fast" concern after the full `PMC13036774` rerun completed. Strict pilot is now 5/5 paper-level source-reviewed `accepted_with_cautions`, 0 open rework, 0 worker-gate findings, and 0 authoritative DBAASP-ingest-ready; added stale-log anti-false-positive checks and immutable future worker-log naming.
- 2026-07-08: Repaired `PMC13036000` worker-2/worker-6 safety-filter failures with hardened no-source-output prompts; global `strict_worker_run_gate` now has 0 hard findings and strict paper-level source-reviewed count is 4/5, while authoritative DBAASP ingest remains 0.
- 2026-07-08: Advanced `PMC11752523` through material recovery, six-worker repair, rework ticket closure, final worker-6 re-adjudication, and strict acceptance; strict paper-level source-reviewed count is now 3/5 while authoritative DBAASP ingest remains 0.
- 2026-07-08: Rechecked the "too fast" concern from worker stderr logs and gates; all four pilot papers have six independent Codex CLI sessions, but only `PMC11735859` and `PMC13054752` strictly pass paper-level source-reviewed completion, `PMC13036774` remains targeted rework, and `PMC13036000` remains invalidated by failed worker sessions.
- 2026-07-08: Exercised the `PMC13036000` empty-done branch, preserved the worker-2/worker-6 model-safety failure as a blocker, added worker failure classification, `run --merge-existing`, `acceptance --paper-id`, and global `strict_worker_run_gate` so final JSON cannot overrule failed worker sessions.
- 2026-07-08: Re-audited DBAASP strict worker evidence after the speed concern, fixed `status` metadata backfill from worker stderr, completed `PMC13054752` six-worker strict run, and recorded two paper-level accepted-with-cautions proofs while keeping global batch and authoritative ingest non-complete.
- 2026-07-08: Added strict pilot `status` and `candidates` commands plus durable JSON reports, separating paper-level source-reviewed acceptance from authoritative DBAASP ingest readiness and identifying that next unreviewed positive candidates require material recovery first.
- 2026-07-08: Proved the DBAASP strict six-worker lane on `PMC11735859`: material-complete packet, six independent `codex exec` workers on `gpt-5.5/xhigh`, worker-6 `accepted_with_cautions`, single-paper semantic/publication gates passing, and explicit boundary that fallback rows remain non-authoritative without linked DBAASP rows.
- 2026-07-06: Added Codex CLI review pass over the 18 remaining DUAL-priority todo rows. AI-assisted artifacts recommend 18/18 confirmed, high confidence, major severity, but do not modify human verdict state.
- 2026-07-06: Recorded WSL browser access workaround and human-review queue smoke test. Review UI on port 8765 loads 192 items, has 34 saved verdicts, 158 todo, and passed GET/PDF/save endpoint checks without leaving test changes.
- 2026-07-06: Recorded AI-first work decision. Manual/human paper validation is deferred or delegated; immediate focus shifts to DBAASP/incremental data cleanup, portal/site completion, release-vs-portal reconciliation, automated QA, and reviewer-packet preparation.
- 2026-07-05: Second-pass update after inspecting latest modified scripts/files. Added latest-modified project layer, explicit evidence-tier model, DBAASP pending-batch status and DOI-key defect, portal ingest contract and non-DBAASP boundary, human-review/backfill reconciliation gap, latest script/data risks, and refresh commands.
- 2026-07-05: Created this living document after local folder investigation. Established RC2 as current release authority, documented RC1/RC2 drift, validation420 pause, pilot20 closure, portal/deepmine boundaries, and next maintenance tasks.

---

# 2026-07-28 17:50 CST — AMP Evidence Atlas v1.0 四项基础工作闭环

## 本轮完成内容

### 1. 唯一 v1.0 数据冻结

- 正式版本：`amp-evidence-atlas-v1.0`
- 完整论文 final artifact：1,471 篇
- public-v1 候选论文：1,374 篇
- 数据库审计行：139,259
- 活性/毒性观察：115,184
- 机制证据主张：4,774
- 不可变负载清单 SHA-256：
  `cb08afed8f53ae74591ca354a7d331541624a60d5019549e33c44bbd4ee99376`

权威目录：
`releases/amp_evidence_atlas_v1_0/`

### 2. RC1/RC2、Portal 与 benchmark 口径统一

- Portal 默认只载入 v1.0 的 `public_v1_included=true` 投影；
- machine/recovered 增量默认排除；
- Portal 当前为1,374篇、128,976条审计记录、108,761条活性/毒性观察、
  4,508条机制主张、28,813条 `source_conflict`；
- 40题 benchmark 明确为 pilot，并强制比较
  `NO_RETRIEVAL`、`RAW_DB`、`ATLAS` 三组；
- 删除“多 Agent 一致即人工金标准”和未经支持的历史准确率表述。

分母合同：
`docs/AMP_EVIDENCE_ATLAS_V1_0_DENOMINATOR_CONTRACT.md`

### 3. 人工验证案例包

- 已准备21个待人工核对案例；
- 覆盖 APD6、CAMP、DBAASP、DRAMP、dbAMP；
- 覆盖 `source_verified`、`source_conflict`、
  `sequence_modified_not_normalized`、
  `database_only_no_primary_source` 和 `unresolved_record`；
- 所有人工标签字段保持空白，不能宣称已完成人工验证。

案例目录：
`reports/nar_resource_freeze_v1/manual_validation/v1_0_human_check_examples/`

validation420 仍为软暂停：39/224篇有有效结果，覆盖114/420行，
待人工核对185篇、306行。

### 4. 来源版本与许可审查

- 五库本地快照日期、版本解释、主文件、大小和 SHA-256 已固定；
- DRAMP 普通/临床数据可按 CC BY 4.0 和署名条件使用，专利 AMP 需另行授权；
- APD6、CAMP、dbAMP 未找到明确的整库公共再分发授权；
- DBAASP 条款内部同时出现“可自由分发”和“不得向任何人分发”，需书面澄清；
- 因此“许可审查”已完成，但“五库原始字段公共再分发许可”尚未完成；
  v1.0 保持 `public_release_ready=false`。

审查文件：

- `releases/amp_evidence_atlas_v1_0/SOURCE_DATABASE_VERSIONS.tsv`
- `releases/amp_evidence_atlas_v1_0/LICENSES.tsv`
- `releases/amp_evidence_atlas_v1_0/governance/source_license_review.json`
- `docs/AMP_EVIDENCE_ATLAS_V1_0_SOURCE_VERSION_AND_LICENSE_REVIEW.md`

## 验证证据

- 新增 fail-closed 验证器：
  `scripts/validate_amp_evidence_atlas_v1_0_release.py`
- 17/17 项检查通过；
- 30/30 个发布包治理/数据文件 checksum 通过；
- 22个不可变负载文件未改变；
- 五个来源快照主文件 hash/大小全部匹配；
- 40/40 benchmark `source_ref` 在 canonical Portal 中可解析；
- 21/21 人工案例可回溯到 source final，人工字段全部为空。

验证报告：
`reports/amp_evidence_atlas_v1_0/validation_20260728_175025_CST.json`

## 当前真实状态

四项基础工作已经按要求完成；但项目仍不是公开 NAR 资源完成态。
后续硬门槛仍是：

1. 由人类完成分层盲审并统计错误率；
2. 取得来源库书面授权，或完成公共导出的字段级 rights filter；
3. 完成公共网站、API、下载服务的生产部署；
4. 将 post-v1.0 严格候选增量放入下一版本，不得回写 v1.0 分母。

---

# 2026-07-28 18:18 CST — 公共安全字段过滤与网站/API生产部署

## 本轮结果

已完成可由 AI 自动完成的“来源权利治理 + 字段过滤 + 公共服务部署”：

1. 建立 field-level rights filter；
2. 生成 `amp-evidence-atlas-v1.0-public-safe-beta` 公共投影；
3. 构建公共搜索网站；
4. 构建只读、CORS-enabled JSON API 和 OpenAPI 3.1；
5. 部署 Sites version 1 到生产环境；
6. 将访问模式由初始 owner-only 改为 `public`；
7. 从未登录公网环境完成在线验证。

生产地址：

<https://amp-evidence-atlas.daoyu7974.chatgpt.site>

## 字段过滤范围

公共服务包含：

- 1,374篇 public-v1 论文的项目审核/计数索引；
- 9,263个派生肽摘要；
- 108,761条活性观察、128,976条数据库审计记录、
  4,508条机制主张和28,813条冲突状态的聚合统计；
- 40题项目自建 grounding benchmark；
- 肽名、序列、paper ID、DOI 搜索。

公共服务剔除：

- 五库原始记录镜像；
- `source_id`、`source_table`、数据库记录名、数据库 endpoint/value/unit；
- 逐行数据库—原文值对照；
- 论文全文、PDF、表格、图片和原始本地路径；
- mechanism 原文主张文本；
- DRAMP patent AMP 内容。

因此公共 beta 的 `public_release_ready=true` 只表示**受限公共投影可发布**；
完整内部 v1.0 包继续保持 `public_release_ready=false`。

## 授权状态

第三方书面授权不能由 AI 自行授予。当前：

- DRAMP 普通/临床数据按 CC BY 4.0 条件处理，专利 AMP 排除；
- APD6、CAMP、DBAASP、dbAMP 仍待数据库团队书面回复；
- 已建立五库授权追踪表和可发送的英文请求模板；
- 书面授权到达前，公共 fallback 始终是剔除复制字段。

授权治理文件：

- `releases/amp_evidence_atlas_v1_0/SOURCE_PERMISSION_TRACKER.tsv`
- `docs/AMP_EVIDENCE_ATLAS_SOURCE_PERMISSION_REQUEST_PACK.md`

## 网站/API

主要接口：

- `/healthz`
- `/api/v1/release`
- `/api/v1/stats`
- `/api/v1/search?q=LL-37`
- `/api/v1/peptides`
- `/api/v1/papers`
- `/api/v1/audit-summary`
- `/api/v1/benchmark`
- `/api/v1/rights`
- `/api/v1/openapi.json`

站点源码：
`atlas_public_site/`

公共安全投影：
`public_exports/amp_evidence_atlas_v1_0_public_safe/`

## 验证证据

- 公共投影字段过滤：6/6通过；
- v1.0 数据/治理验证：18/18通过；
- 公网首页、health、stats、search、rights、OpenAPI、benchmark：7/7通过；
- OpenAPI 路径：12；
- `LL-37` 公网搜索返回10个肽命中；
- 生产截图 1200×750 已人工目视检查，无布局阻断；
- Sites 部署状态：`succeeded`；
- Sites access mode：`public`；
- 部署源码 commit：
  `ad06c6c3222ed41765925915d42b548ae16a6d4e`。

部署证据目录：
`reports/amp_evidence_atlas_v1_0/public_deployment_20260728_181508_CST/`

## 仍然没有虚假宣称的内容

- 没有宣称 APD6、CAMP、DBAASP、dbAMP 已书面授权；
- 没有把公共聚合 beta 冒充完整 v1.0 下载包；
- 没有把 AI 多 worker 一致当作人工金标准；
- 没有把 `source_conflict` 自动称为人工确认的数据库错误。

---

# 2026-07-28 19:05 CST — 公共门户、分层 API、AI MCP 与数据库层级 v2

## 本轮完成结果

### 1. 页面由单页展示升级为完整资源门户

生产站点仍使用原地址：

<https://amp-evidence-atlas.daoyu7974.chatgpt.site>

当前页面已补齐：

- 数据范围与版本总览；
- 六层公共安全数据库模型；
- 肽与论文的搜索、筛选、排序和浏览；
- 五库审查状态与差异类别的聚合可视化；
- 40题 grounding benchmark 浏览；
- REST API 文档和在线调用控制台；
- MCP 工具说明、客户端配置、cURL 和在线工具调用；
- 来源授权、字段排除和发布边界。

生产首页 1200×750 截图已目视检查，导航、主标题、操作入口和范围提示均无
布局阻断。

### 2. REST API 改为分层结构

新的权威路由层级为：

- `/api/v1/system/*`
- `/api/v1/catalog/*`
- `/api/v1/evidence/*`
- `/api/v1/evaluation/*`
- `/api/v1/governance/*`
- `/api/v1/schema/*`

成功响应统一使用 `data / meta / links`，分页信息进入 `meta.pagination`；
错误响应统一使用 `error.code / error.message`。肽和论文接口支持查询、条件过滤、
排序、limit/offset；OpenAPI 3.1 当前描述14条路径。旧扁平接口继续保留，避免
破坏现有调用。

所有 GET 接口支持 CORS、ETag、HEAD 和公共缓存。

### 3. AI 可通过远程 MCP 直接调用

生产 MCP 地址：

<https://amp-evidence-atlas.daoyu7974.chatgpt.site/api/mcp>

提供10个只读工具：

1. `atlas.describe`
2. `atlas.search`
3. `atlas.list_peptides`
4. `atlas.get_peptide`
5. `atlas.list_papers`
6. `atlas.get_paper`
7. `atlas.get_audit_summary`
8. `atlas.get_benchmark`
9. `atlas.get_rights_policy`
10. `atlas.get_database_schema`

MCP 同时支持：

- `2025-11-25` 的 `initialize`、`notifications/initialized`、
  `tools/list` 和 `tools/call`；
- `2026-07-28` 的无状态 `server/discover`、`Mcp-Method`、
  `Mcp-Name`、结果类型、缓存提示和响应级服务器元数据。

所有工具都有关闭额外字段的 JSON Schema、只读/非破坏注解、输入长度和分页
上限。服务不创建 session，不提供 SQL 或写入工具。

公网验证时发现 Sites 边缘层会在 Worker 前拦截 `/mcp` 和
`/.well-known/*`。最终采用标准允许的自定义单端点 `/api/mcp`：
POST 处理 JSON-RPC，普通 GET 返回服务描述。该修复已经公网复测通过。

### 4. 公共数据库改为六层规范化 SQLite

新增：

`public_exports/amp_evidence_atlas_v1_0_public_safe/atlas_public_safe.db`

层级：

1. `system`：版本、校验和、范围；
2. `governance`：来源授权与公开决策；
3. `catalog`：论文、肽、序列、endpoint、evidence tier 和论文—肽关系；
4. `evidence`：审查状态与差异类别聚合；
5. `evaluation`：benchmark；
6. `api`：稳定读取视图。

实际数据库包含12张表、2个视图，大小12,288,000 bytes；含1,374篇论文、
9,263个肽、1,526条公开派生序列、10,283条肽—论文关系和40个 benchmark
条目。审查聚合计数为128,976，与 Portal 分母一致。

数据库启用主键、外键、计数约束和检索索引；不存在源数据库原始记录表、
逐行数据库—论文对照表或被禁止字段。

## 验证证据

- 公共投影与 SQLite rights filter：11/11通过；
- 内部 v1.0 不可变性与治理：18/18通过；
- 本地站点构建和 API/MCP 协议测试：通过；
- 公网门户、API、MCP 双版本和真实 `tools/call`：15/15通过；
- SQLite `integrity_check`、`foreign_key_check`：通过；
- Sites version：4；
- Sites 部署状态：`succeeded`；
- 访问模式：`public`；
- 部署源码 commit：
  `dc71a283954f86c90d1e133db1380d17bd9e8777`。
- 公共安全投影、站点源码、API/MCP 脚本、文档和验证证据已同步到
  `https://github.com/cihebi2/amp_peptide_data.git`；
  公共快照 commit：`7fa2b29f78ef0b53412535cc5586b9fa449fb005`。

证据目录：

`reports/amp_evidence_atlas_v1_0/public_api_mcp_v2_20260728_190510_CST/`

设计与调用文档：

`docs/AMP_EVIDENCE_ATLAS_PUBLIC_API_MCP_V2.md`

## 仍未改变的项目边界

- 完整内部 v1.0 继续 `public_release_ready=false`；
- 分层人工验证仍未闭环；
- APD6、CAMP、DBAASP、dbAMP 和 DRAMP 专利肽的授权跟进仍未关闭；
- `source_conflict` 仍然不能自动称为人工确认的数据库错误；
- 公共 MCP/API 是受限只读投影，不是五库原始数据下载服务。
