# Validation420 Pause Checkpoint QA

Generated at: `2026-06-25T06:40:06Z`

This checks source-review output contracts for existing packet results only. It is not final closure and does not replace owner rework plus worker-6 final adjudication.

## Counts

| metric | value |
| --- | ---: |
| packets | 224 |
| result files | 39 |
| missing results | 185 |
| reviewed sample rows | 114 |
| manifest sample rows | 420 |
| contract pass among result files | 39 |
| contract fail among result files | 0 |
| blocking output problems | 0 |
| warnings | 1 |
| runner status files | 43 |
| runner valid results | 39 |
| runner invalid/interrupted | 4 |
| runner no status | 181 |
| rework targets | 35 |
| tickets | 35 |
| cautions | 146 |

## Final Decisions

| decision | count | example packets |
| --- | ---: | --- |
| `accepted_with_cautions` | 13 | V420P0002, V420P0003, V420P0005, V420P0007, V420P0011 |
| `blocked_missing_primary_material` | 4 | V420P0032, V420P0037, V420P0041, V420P0042 |
| `missing_result` | 185 |  |
| `needs_targeted_rework` | 22 | V420P0001, V420P0004, V420P0006, V420P0008, V420P0009 |

## Sample Row Decisions

| row decision | count |
| --- | ---: |
| `blocked_missing_primary_material` | 65 |
| `confirmed` | 1 |
| `confirmed_with_caution` | 34 |
| `needs_targeted_rework` | 14 |

## Contract Failures

- None among existing result files.

## Runner Invalid / Interrupted

- `V420P0022` `doi__10.1021_acsinfecdis.2c00456`: `codex_finished_no_valid_result` / `missing_result_json` / returncode `1`
- `V420P0029` `doi__10.1038_s41422-020-0305-x`: `codex_finished_no_valid_result` / `missing_result_json` / returncode `1`
- `V420P0030` `doi__10.1038_s41422-022-00617-x`: `codex_finished_no_valid_result` / `missing_result_json` / returncode `1`
- `V420P0031` `doi__10.1038_s41467-017-00419-5`: `codex_finished_no_valid_result` / `missing_result_json` / returncode `1`

## Missing Results

- 185 packets have not produced `true_review_result.json` yet.
