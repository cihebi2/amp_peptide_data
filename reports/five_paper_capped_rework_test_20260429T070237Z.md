# Five-Paper Capped Rework Test - 2026-04-29

Source summary: `reports/ten_paper_capped_rework_test_latest.json`

Papers: 5
Terminal status counts: `{'capped_rework_limit_reached': 5}`
Rework counts: `{'accepted_papers': 0, 'open_rework_tickets': 5, 'total_rework_decisions': 25, 'uncontrolled_papers': 5}`

| Paper | Terminal | Rework decisions | Activity rows/issues | Owner workers | Final blockers |
| --- | --- | ---: | ---: | --- | --- |
| `doi__10.1002_cmdc.201900465` | `capped_rework_limit_reached` | 5 | 246/2 | `worker-2, worker-4, worker-6` | `publication_grade_not_true, review_status_not_publication_grade` |
| `doi__10.1002_advs.202205301` | `capped_rework_limit_reached` | 5 | 77/0 | `worker-4, worker-6` | `publication_grade_not_true, review_status_not_publication_grade` |
| `doi__10.1002_advs.202401793` | `capped_rework_limit_reached` | 5 | 60/0 | `worker-4, worker-6` | `publication_grade_not_true, review_status_not_publication_grade` |
| `doi__10.1002_cbic.202100609` | `capped_rework_limit_reached` | 5 | 29/0 | `worker-2, worker-4, worker-6` | `publication_grade_not_true, review_status_not_publication_grade` |
| `doi__10.1002_cbic.202100151` | `capped_rework_limit_reached` | 5 | 30/0 | `worker-2, worker-4, worker-6` | `publication_grade_not_true, review_status_not_publication_grade` |

All five papers kept open rework tickets and were not accepted. Each paper has a `handoff_context.json` and `CODEX_REVIEW_PROMPT.md` for a new Codex CLI re-review.
