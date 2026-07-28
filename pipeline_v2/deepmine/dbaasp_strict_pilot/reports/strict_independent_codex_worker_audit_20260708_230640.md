# Strict Independent Codex Worker Audit (2026-07-08T23:06:40+08:00 CST)

## Plain-Language Answer

- Yes for the 5-paper DBAASP strict pilot: every pilot paper now has `worker-1` through `worker-6`, six unique `codex exec` session IDs, all return code 0, all `gpt-5.5/xhigh`, and no stale/mutated log references.
- No for the broader DBAASP universe: the earlier 10-paper Codex fallback batch was only dual-pass machine extraction, and the 2103-paper DBAASP worklist has not gone through six-worker review.
- The current strict pilot is a sequential independent Codex CLI bridge, not a full durable OMX team mailbox production run.
- The scientific result is paper-level source-reviewed `accepted_with_cautions` for all 5 pilot papers; authoritative DBAASP ingest-ready remains 0 because linked authoritative DBAASP/merged rows are absent.

## Global Gate Result

| Metric | Value |
| --- | ---: |
| Pilot papers | 5 |
| Material extracted complete | 5 |
| Analysis source-reviewed accepted | 5 |
| Review accepted_with_cautions | 5 |
| Paper-level source-reviewed complete | 5 |
| Authoritative DBAASP ingest-ready | 0 |
| Open rework tickets | 0 |
| Strict worker gate hard findings | 0 |

## Per-Paper Worker Evidence

| Paper | Workers | Unique sessions | Model/effort | Return codes | Stale logs | Review | Activity | DB audits | Mechanism | Cautions | Auth ingest |
| --- | ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| `PMC13036774` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | 0 | `accepted_with_cautions` | 3 | 3 | 5 | 4 | False |
| `PMC13036000` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | 0 | `accepted_with_cautions` | 8 | 0 | 5 | 2 | False |
| `PMC11735859` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | 0 | `accepted_with_cautions` | 57 | 5 | 7 | 6 | False |
| `PMC13054752` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | 0 | `accepted_with_cautions` | 13 | 16 | 5 | 5 | False |
| `PMC11752523` | 6 | 6 | all `gpt-5.5/xhigh` | all 0 | 0 | `accepted_with_cautions` | 8 | 8 | 5 | 5 | False |

## Important Boundary

- `accepted_with_cautions` means the strict paper-level source-review workflow accepted the paper with preserved cautions; it is not a clean/no-conflict label.
- `authoritative_dbaasp_ingest_ready=false` for all 5 papers because linked authoritative article/assay/sequence/literature row counts are zero; fallback machine rows remain candidate provenance, not release authority.
- The bridge now has stronger anti-false-positive checks: stale log backfill is blocked, worker-run cleanliness requires no stale/mutated log references, and future runs write immutable run-id-prefixed worker logs.

## Evidence Files

- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/status_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/verify_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_worker_run_gate_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13036774_strict_acceptance_audit_latest.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/worker_logs`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/strict_independent_codex_worker_audit_20260708_230640.json`
