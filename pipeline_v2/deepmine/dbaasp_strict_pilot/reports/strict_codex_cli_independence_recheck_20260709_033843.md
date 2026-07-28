# Strict Codex CLI Independence Recheck

Timestamp: 2026-07-09T03:38:43+08:00 CST.

## Short Answer

- No: at least one audited paper does not currently satisfy the strict worker-independence/source-review gate.
- Hard findings: 3.
- Paper-level source-reviewed complete: 7/9.
- Authoritative DBAASP ingest-ready: 0.
- Runtime boundary: sequential independent `codex exec` bridge, not full durable `omx team` mailbox production state.

## Current Counts

| Metric | Value |
| --- | ---: |
| Manifest papers | 9 |
| Paper-level source-reviewed complete | 7 |
| Authoritative DBAASP ingest-ready | 0 |
| Open rework tickets | 1 |
| Missing-final paper count | 0 |
| Worker reports found | 54 |
| Unique Codex session IDs found | 54 |
| Duplicate Codex session IDs | 0 |
| Nonzero worker reports | 1 |
| Wrong model/effort reports | 0 |
| Non-`codex exec` reports | 0 |
| Hard findings | 3 |

## Per-Paper Proof

| Paper | Workers | Unique sessions | Model/effort | Return codes | Review | Activity | DB audits | Mechanism | Cautions | Auth ingest |
| --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `PMC13036774` | 6 | 6 | all gpt-5.5/xhigh | all 0 | `accepted_with_cautions` | 3 | 3 | 5 | 4 | False |
| `PMC13036000` | 6 | 6 | all gpt-5.5/xhigh | all 0 | `accepted_with_cautions` | 8 | 0 | 5 | 2 | False |
| `PMC11735859` | 6 | 6 | all gpt-5.5/xhigh | all 0 | `accepted_with_cautions` | 57 | 5 | 7 | 6 | False |
| `PMC13054752` | 6 | 6 | all gpt-5.5/xhigh | all 0 | `accepted_with_cautions` | 13 | 16 | 5 | 5 | False |
| `PMC11752523` | 6 | 6 | all gpt-5.5/xhigh | all 0 | `accepted_with_cautions` | 8 | 8 | 5 | 5 | False |
| `PMC11784053` | 6 | 6 | all gpt-5.5/xhigh | all 0 | `accepted_with_cautions` | 40 | 3 | 3 | 3 | False |
| `PMC12229353` | 6 | 6 | all gpt-5.5/xhigh | all 0 | `accepted_with_cautions` | 28 | 3 | 7 | 9 | False |
| `PMC12103485` | 6 | 6 | all gpt-5.5/xhigh | all 0 | `needs_targeted_rework` | 13 | 13 | 4 | 3 | False |
| `PMC11531597` | 6 | 6 | all gpt-5.5/xhigh | problem | `needs_targeted_rework` | 0 | 27 | 6 | 3 | False |

## Findings

- `paper_not_source_reviewed_complete`: {"paper_id": "PMC12103485", "severity": "hard", "code": "paper_not_source_reviewed_complete", "review_status": "needs_targeted_rework", "worker_run_clean": true}
- `nonzero_worker_returncode`: {"paper_id": "PMC11531597", "severity": "hard", "code": "nonzero_worker_returncode", "workers": [{"worker": "worker-2", "returncode": 1, "failure_code": "model_safety_content_filter"}]}
- `paper_not_source_reviewed_complete`: {"paper_id": "PMC11531597", "severity": "hard", "code": "paper_not_source_reviewed_complete", "review_status": "needs_targeted_rework", "worker_run_clean": false}

## Boundary

- This proves worker-session independence and paper-level source-reviewed completion only when the pass flag is true.
- It does not make candidate DBAASP machine rows authoritative release/portal ingest rows.
- Full production queue semantics still require durable OMX team/mailbox orchestration.
