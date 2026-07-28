# Scope Reconciliation: 1471 vs 1472

This note reconciles the historical queue aggregate paper count with the current
freeze final-artifact paper universe.

| Count | Value |
| --- | ---: |
| Legacy queue unique papers | 1472 |
| Current final artifact papers | 1471 |
| Only in legacy queue | 1 |
| Only in final artifacts | 0 |

## Decision

The v1 freeze paper universe uses current `papers/*/final/review_report.json`
artifacts, so the main release count remains 1471. Historical queue-only
items remain visible in this reconciliation note and should be routed to
source staging or infrastructure recovery before they can enter a future
publication-grade release.

## Queue-only papers

| paper_id | terminal_status | result_status | action | material state |
| --- | --- | --- | --- | --- |
| `doi__10.1055_s-0029-1185675` | `initial_queue_failed` | `infrastructure_initial_queue_failed` | `defer_to_infrastructure_recovery_queue` | landed=True; primary_xml=False; primary_pdf=False; supplementary=True |

## Interpretation

The legacy queue aggregate includes papers that reached terminal queue status even when bootstrap failed before final paper artifacts were created. The freeze paper universe is defined by current papers/*/final review artifacts.
