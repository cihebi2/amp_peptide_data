# Batch 4-Team Quality Rework Loop Fixes - 2026-04-29

This document records the concrete problems found in the 10-paper real-material
test and the fixes required for the Batch 4-Team review mechanism. It is the
operational contract for "打回 -> 上下文传递 -> 新 Codex CLI 复审 -> 再 gate" loops.

## 1. Non-Negotiable Quality Rule

The 10-paper capped run proved the message/rework guard, not publication-grade
scientific acceptance. A paper remains non-accepted until all four layers pass:

1. material packet ready,
2. validator contract ready,
3. semantic gate ready,
4. worker-6 publication-grade adjudication ready.

`analysis_accepted`, file presence, or `contract_issue_count=0` are not enough.
Final QC must preserve the exact failure reason and route the paper back to the
owning worker instead of force-accepting.

## 2. Problems Found In The 10-Paper Audit

Audit source: `reports/ten_paper_real_rework_reason_audit_latest.json`.

| Paper | Main real reason to keep rework open | Owner worker(s) |
| --- | --- | --- |
| `doi__10.1002_cmdc.201900465` | Gate falsely treated valid abbreviated species such as `A. baumannii` as sentence fragments; activity parser also produced unsafe target rows from non-target tables; database conflicts still need adjudication. | worker-2, worker-4, worker-6 |
| `doi__10.1002_advs.202205301` | No strong non-review semantic blocker in the audit; still blocked because worker-6 source adjudication and database conflict review are incomplete. | worker-4, worker-6 |
| `doi__10.1002_advs.202401793` | Same: activity appears structurally plausible, but publication-grade worker-6/database adjudication is not complete. | worker-4, worker-6 |
| `doi__10.1002_cbic.202100609` | Activity parser quality issue around row/column orientation; database conflicts remain unresolved. | worker-2, worker-4, worker-6 |
| `doi__10.1002_cbic.202100151` | Parser previously missed MIC table rows with range/statistic values. | worker-2, worker-6 |
| `doi__10.1002_cmdc.201600498` | Parser previously extracted only a small subset; IC50 cell-line table needs source-grounded re-extraction and scope adjudication. | worker-2, worker-6 |
| `doi__10.1002_cmdc.202200291` | Parser treated method/property columns as assay rows and mixed endpoints/units; table requires target-aware parsing. | worker-2, worker-6 |
| `doi__10.1002_gch2.202200213` | Zero activity rows from supported table shapes; likely activity is in prose/figures/supplements and must be inspected, not fabricated. | worker-2, worker-3, worker-6 |
| `doi__10.1002_anie.201901589` | MIC table exists but target context is not safely represented by the table-only parser; worker must inspect source context before row creation. | worker-2, worker-6 |
| `doi__10.1002_advs.202507457` | Parser treated model/property table columns as activity rows because endpoint matching was substring-based. | worker-2, worker-6 |

## 3. Process Fixes

### 3.1 Final QC Must Record Why It Failed

Worker-6 or the `quality_gate` state must write structured reasons in:

- `papers/<paper_id>/work/review/quality_feedback.json`
- `papers/<paper_id>/final/review_report.json`
- `paper_packets/<paper_id>/rework/rework_requests.jsonl`

Required fields:

```json
{
  "qc_failure_reasons": [
    {
      "code": "activity_extraction_requires_worker2_rework",
      "severity": "major",
      "owner_worker": "worker-2",
      "reason": "Activity-bearing table could not be safely converted to target/entity/value rows.",
      "artifact_path": "papers/<paper_id>/final/activity_toxicity_evidence.json"
    }
  ],
  "rework_context_packet_required": true
}
```

### 3.2 Rework Context Packet Is Mandatory

Every major/blocking QC failure must create:

```text
rework_context/<paper_id>/
  handoff_context.json
  CODEX_REVIEW_PROMPT.md
  artifact_manifest.json
```

Generate it with:

```bash
python scripts/build_rework_context_packet.py --paper-id <paper_id>
```

The packet must include:

- paper ID, source roots, packet root, workflow context path,
- historical artifacts to reopen,
- exact failure reasons and gate issue codes,
- previous final/work/packet paths,
- open ticket IDs,
- owner worker skill paths,
- a prompt that can be sent to a new Codex CLI worker.

### 3.3 New Codex CLI Re-Review Loop

The handoff prompt must instruct the new worker to:

1. read the listed worker skill files,
2. reopen the artifact paths,
3. fix only the owner layer,
4. update rework responses and quality feedback,
5. rerun semantic/publication gates,
6. keep the ticket open if quality is still not controllable.

No prompt or chat message may replace paper-local source locators.

### 3.4 Max Rework Attempts

For capped automated tests, the loop is:

```text
gate fail -> record qc_failure_reasons -> build context packet -> send to owner -> retry gate
```

After `max_rework=5`, do not accept. Mark:

```text
terminal_status=capped_rework_limit_reached
analysis=analysis_blocked
publication_grade_ready=false
```

### 3.5 Start-Once Queue + Bounded Best-Effort Rework

The production loop must start the queue only once for a paper/manifest. A
retry must not rerun the initial workflow or rebuild acceptance from scratch
unless the leader explicitly requests a reset. The normal retry payload is:

```text
existing workflow_context + open tickets
-> rework_context/<paper_id>/handoff_context.json
-> rework_context/<paper_id>/CODEX_REVIEW_PROMPT.md
-> fresh Codex CLI owner worker
-> strict gates
```

Owner workers must do best-effort recovery from local materials before giving
up: packet manifest, locator index, XML/NXML, PDF text/tables, OA package,
declared supplements, archives, office/spreadsheet files, image/OCR outputs,
and linked database snapshots. They should prioritize sources that can change
the gate outcome and should not spend repeated attempts on peripheral gaps.

If the missing evidence is not locally recoverable, the worker must not
fabricate a value. It must record:

```json
{
  "unrecoverable_material_gaps": [
    {
      "gap_code": "missing_supplementary_table_after_local_recovery",
      "owner_worker": "worker-3",
      "source_paths_checked": ["paper_packets/<paper_id>/raw/supplementary_original/s001.pdf"],
      "tools_attempted": ["pdftotext", "PaddleOCR"],
      "why_unrecoverable": "The local supplement is image-only and OCR did not recover a readable table.",
      "impact": "activity rows cannot be made publication-grade from local material",
      "blocks_publication_grade": true,
      "next_action": "record_and_continue"
    }
  ]
}
```

After the cap (`max_rework=5` by default), the controller must mark the paper
`blocked_after_best_effort` / `analysis_blocked`, keep the paper non-accepted,
and continue with the next paper. Quality is maximized by source exhaustion and
precise gap labels, not by infinite retries.

## 4. Script Fixes Implemented

| Script | Fix |
| --- | --- |
| `.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py` | Allows valid genus abbreviations such as `A. baumannii`, `E. coli`, `S. aureus` before sentence-fragment checks. |
| `scripts/run_one_paper_complete_message_test.py` | Uses endpoint regexes instead of substring matching, rejects property/model tables, parses target-row and entity-row assay matrices, supports range/statistic values, records unsupported activity-table issues instead of fake rows. |
| `scripts/run_one_paper_complete_message_test.py` | Writes `qc_failure_reasons`, `activity_extraction_issues`, and `rework_context_packet_required` into review/quality/rework artifacts. |
| `scripts/build_rework_context_packet.py` | Builds `handoff_context.json`, `CODEX_REVIEW_PROMPT.md`, and artifact manifests for a new Codex CLI worker; records the context in the Miaobi-style message bus when available. |
| `scripts/run_ten_paper_capped_rework_tests.py` | On failed retry gates, builds a rework context packet and records it as an artifact so the next worker receives exact failure context. |
| `scripts/run_true_rework_queue.py` | Runs the start-once bounded queue: reuse/initialize workflow once, launch fresh Codex CLI workers from `CODEX_REVIEW_PROMPT.md`, rerun gates, mark `blocked_after_best_effort` after the cap, then advance. |

## 5. Worker Guidance

- worker-2 must not parse peptide IDs, method names, model metrics, or property
  columns as target species. Unsupported activity-bearing tables become
  rework issues, not fabricated rows.
- worker-3 must explicitly state whether supplementary/OCR/archive gaps affect
  identity, activity/toxicity, mechanism, or only peripheral context.
- worker-4 must preserve `source_conflict`, `database_only_no_primary_source`,
  `sequence_modified_not_normalized`, and `unresolved_record` rather than
  smoothing database conflicts.
- worker-5 must not promote phenotype, model-membrane, family, or computational
  language into direct mechanism without a direct assay locator.
- worker-6 must reject generic review summaries and must write concrete
  `qc_failure_reasons` plus targeted rework tickets before any打回.
- all workers must stop bounded attempts when local evidence is exhausted;
  unresolved evidence becomes `unrecoverable_material_gaps` plus a blocked or
  needs-rework status, not an infinite loop or a fabricated value.

## 6. Acceptance Evidence Required After Repair

For each re-reviewed paper, retain paths to:

```text
papers/<paper_id>/work/review/quality_feedback.json
paper_packets/<paper_id>/rework/rework_requests.jsonl
paper_packets/<paper_id>/rework/rework_responses.jsonl
reports/<paper_id>.semantic_gate.json
reports/<paper_id>.publication_quality.json
rework_context/<paper_id>/handoff_context.json
reports/true_rework_queue_latest.json
```

Only report publication-grade acceptance if the open-ticket list is empty,
semantic gate passes, publication-quality gate passes, and worker-6 explicitly
records `publication_grade=true`.

## 7. 2026-05-01 50-Paper Blocked Reason Audit And Optimization Backlog

Detailed outputs:

- `reports/blocked_after_best_effort_reason_audit_20260501.json`
- `reports/blocked_after_best_effort_reason_audit_20260501.md`
- `reports/blocked_after_best_effort_reason_audit_20260501_zh.md`
- `reports/true_rework_queue_50_aggregate_progress_20260501.json`

Observed blocked distribution from the 50-paper start-once bounded run:

- `worker_timeout_or_overbroad_prompt`: 5 papers.
- `activity_table_extraction_gap`: 3 papers.
- `missing_external_supplement`: 2 papers.
- `figure_chart_values_unrecoverable`: 1 paper.

Per-paper blocked reason record is maintained in `reports/blocked_after_best_effort_reason_audit_20260501_zh.md`. The 11 papers split into these actionable buckets: 5 timeout/overbroad-prompt cases, 3 activity-table parser gaps, 2 missing external supplementary-source cases, and 1 figure-only exact-value gap. Timeout cases are retryable process defects unless a narrower owner pass proves a true source gap. Missing supplementary and figure-only exact-value cases remain non-accepted until external source acquisition or a controlled digitization policy exists.

Optimization records:

1. Keep controller timeout handling as a hard guard: a Codex worker timeout must write `codex_worker_timeout` / `blocked_after_best_effort` and advance the queue, never crash a lane.
2. Split overbroad owner prompts into narrower worker-2/3/4/5/6 prompts so timeout cases can be retried by the actual owner rather than a whole-paper worker-6 pass.
3. Improve worker-2 table extraction for peptide/virus IC50 tables, MIC/MBC matrices, antibiofilm tables, and unsupported target/entity/value layouts.
4. Add supplementary landing-page resolution for Springer/HTML `landing-*.bin` files and missing MOESM DOCX/XLSX/PDF assets; if the asset cannot be staged, mark `external_source_needed` early.
5. Add a controlled chart-digitization/OCR lane or explicit source-conflict policy for figure-only exact percentages, such as cytotoxicity bar-chart values.
6. Reject mechanism framework-note artifacts before worker-6 by requiring worker-5 source-located mechanism classes or explicit unknown.
7. Add an automatic lane-summary merger so parallel runs always produce one final aggregate without manual reconciliation.


## 8. 2026-05-01 Obtainable-Only 100-Paper Queue Optimization

The 100-paper queue should now run in `--obtainable-only` mode:

- Extract only facts that can be supported by local paper material: XML/NXML, PDF text/tables, OA package members, supplements, archives, office files, images/OCR outputs, locator indexes, and linked database snapshots.
- Preserve partial recoveries even when another value remains `source_conflict` or unresolved.
- Do not fabricate exact sequence/activity/toxicity/mechanism/database values for missing external supplements, image-only charts, unsupported scans, or absent primary sources.
- Once the relevant local source paths are exhausted, write `unrecoverable_material_gaps`, keep the paper non-accepted, and advance to the next paper.
- Timeout/material-gap cases are controlled queue outcomes, not publication-grade acceptance.

Implementation surfaces:

- `scripts/build_rework_context_packet.py` now supports `--obtainable-only` and injects an obtainable-only worker contract into `CODEX_REVIEW_PROMPT.md`.
- `scripts/run_true_rework_queue.py` now supports `--obtainable-only`, passes it to context generation, and stops a paper early when `quality_feedback.json` / final review artifacts document unrecoverable source gaps.
- The 100-paper run is split into 5 lane manifests of 20 papers each, with lane-specific `--run-label` values so summaries do not race on one `latest.json`.

## 9. 2026-05-02 100-Paper Obtainable-Only Post-Repair Audit

Initialization repair:

- `doi__10.1016_s0140-6736(04)15788-7` failed because the message bridge stores workflow directories using `safe_dir_name()` while the queue/bootstrap scripts read `.miaobi-paper-review/workflows/<raw-paper-id>/workflow_context.json` directly.
- Fixed scripts to use the same safe workflow directory rule: `scripts/run_true_rework_queue.py`, `scripts/run_one_paper_complete_message_test.py`, `scripts/initialize_real_paper_review.py`, and `scripts/build_rework_context_packet.py`.
- Re-ran the repaired paper via `reports/true_rework_queue_queue100_obtainable_repair_initial_failed_latest.json`; initialization now succeeds and the paper reaches a controlled `blocked_after_best_effort` outcome, not `initial_queue_failed`.

Post-repair queue state:

- `reports/true_rework_queue_100_obtainable_post_repair_aggregate_20260502.json`
- Current terminal counts: 52 `accepted_after_rework`, 48 `blocked_after_best_effort`, 0 `initial_queue_failed`.
- Original requested 47-paper blocked audit: `reports/blocked_after_best_effort_100_obtainable_reason_audit_20260502.json` and `reports/blocked_after_best_effort_100_obtainable_reason_audit_20260502.md`.
- Post-repair 48-paper blocked audit: `reports/blocked_after_best_effort_100_obtainable_reason_audit_post_repair_20260502.json`.

Original 47 blocked reason buckets:

- `worker_timeout_or_overbroad_prompt`: 32 papers. Treat as process/prompt scope blockers, not proof of material absence.
- `activity_table_extraction_gap`: 13 papers. Worker-2/manual table-shape recovery remains the main scientific target.
- `missing_external_supplement`: 1 paper. Keep exact values blocked/source-conflict until the true supplement is staged.
- `review_or_database_only_no_primary_assay`: 1 paper. Local evidence lacks primary assay/sequence rows sufficient for source-verified acceptance.

## 10. 2026-05-02 Rich Result Status And 1800s Watchdog Policy

The queue now keeps the old `terminal_status` field for compatibility, but also writes richer machine-readable fields on every new result:

- `result_status`: why this paper stopped, for example `accepted_after_rework`, `blocked_watchdog_timeout_retryable`, `blocked_activity_table_extraction_gap`, `blocked_missing_external_supplement`, `blocked_no_primary_assay_source`, or infrastructure failures.
- `result_category`: coarse bucket such as `accepted`, `blocked_process_timeout`, `blocked_source_gap`, `blocked_parser_or_manual_extraction_gap`, or `infrastructure_failed`.
- `result_reason_code`, `result_reason_summary`, and `retryability`: short machine/human guidance for whether to retry with a narrower worker, stage more source, or keep the paper blocked.
- `terminal_status` remains the backward-compatible coarse lane state; do not use it alone for scientific interpretation.

Watchdog policy:

- Future and retry runs should use `--worker-timeout-seconds 1800`.
- The previous 100-paper run used 900s for the 32 timeout papers; these are now labeled `blocked_watchdog_timeout_retryable`, not source gaps.
- Timeout retry manifest: `reports/true_rework_queue_manifest_100_obtainable_timeout_retry_32_20260502.json`.
- Enriched status reports: `reports/true_rework_queue_100_obtainable_rich_status_20260502.json` and `reports/true_rework_queue_100_obtainable_rich_status_20260502.md`.
