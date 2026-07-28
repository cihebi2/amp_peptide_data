# Remaining 200 Strict Review Campaign Status

Generated: 2026-07-28T03:47:57.084181Z  
Supervisor PID: `2243091`  
Supervisor started: 2026-07-27T18:34:06.488568Z

## Current denominator

- Frozen queue: **200**
- Terminal scientific review complete: **9**
- Remaining nonterminal: **191**
- Strict materials ready: **200**
- Live open tickets: **22**

## Active work

- Sweep: **1834**
- Parallel capacity: **4**
- `PMC11845615` / attempt `4` / started `2026-07-28T03:04:49.074846Z`
- `PMC12162962` / attempt `1` / started `2026-07-28T00:56:07.307460Z`
- `PMC12606902` / attempt `4` / started `2026-07-28T03:45:31.092101Z`
- `PMC12812963` / attempt `2` / started `2026-07-28T01:29:56.367525Z`
- Latest result: `PMC11889930` / `awaiting_leader_field_semantic_audit` / campaign rc `1`

## Workflow states

- `awaiting_independent_verifier`: 1
- `awaiting_leader_field_semantic_audit`: 1
- `needs_targeted_semantic_rework`: 5
- `ready_for_six_worker_review`: 184
- `terminal_scientific_review_complete`: 9

## Quality boundary

Per paper: six unique sequential exact codex exec gpt-5.5/xhigh workers, fresh worker-6, current mechanical acceptance, zero open tickets, structured leader PASS, independent verifier PASS, recursive authority=false, and fallback release exclusion.

This file is a generated heartbeat. Terminal promotion is controlled only by
the frozen strict ledger at `pipeline_v2/deepmine/dbaasp_strict_pilot/manifests/remaining_200_strict_review_state_20260726.json`. Campaign attempts are
append-only in `pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_journal.jsonl`.
