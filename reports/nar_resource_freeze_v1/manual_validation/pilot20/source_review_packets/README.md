# Pilot20 True Source-Review Packets

Generated at: `2026-06-22T03:45:25Z`

These packets are inputs for fresh Codex CLI source-review runs. They do not prove scientific acceptance by themselves.

## Run all 20 with 4-way concurrency

```bash
bash reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/run_true_source_reviews_20.sh
```

## Run one packet manually

```bash
bash reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-001__*/run_codex_review.sh
```

Each reviewer must write `true_review_result.json`; hard failures also write `rework_ticket.json`.
