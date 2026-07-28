Re-review completed for `doi__10.1371_journal.pbio.0030038`.

Outcome: non-accepted, controlled blocked state. Local XML/PDF/OA/supplement/database materials support rice genome/duplication/domain-count evidence, but no primary AMP activity/toxicity assay rows. I kept `activity_records=[]`, preserved 7 database-only activity annotations, audited 8 database records as `7 database_only_no_primary_source + 1 source_verified` literature trace, and recorded `unrecoverable_material_gaps`.

Updated the owned-layer artifacts under:

- `paper_packets/doi__10.1371_journal.pbio.0030038/analysis/`
- `paper_packets/doi__10.1371_journal.pbio.0030038/final/`
- `papers/doi__10.1371_journal.pbio.0030038/final/`
- `papers/doi__10.1371_journal.pbio.0030038/work/review/quality_feedback.json`
- `paper_packets/doi__10.1371_journal.pbio.0030038/rework/rework_requests.jsonl`
- `paper_packets/doi__10.1371_journal.pbio.0030038/rework/rework_responses.jsonl`

Rework state:

- Responded to `rwk-complete-test-0001`.
- Added/kept open targeted ticket `rwk-obtainable-gap-0002` for worker-2.
- `review_status=blocked_missing_primary_material`
- `publication_grade=false`

Gate evidence:

- JSON validation passed.
- Semantic gate rerun wrote `reports/doi__10.1371_journal.pbio.0030038.semantic_gate.json`; expected fail with 3 hard issues: `review_status_not_publication_grade`, `publication_grade_not_true`, `missing_activity_records`.
- Publication quality gate rerun wrote `reports/doi__10.1371_journal.pbio.0030038.publication_quality.json`; expected fail with `open_rework_targets=1`.
- Refreshed `reports/doi__10.1371_journal.pbio.0030038.complete_message_test_report.json` to `blocked_after_bounded_best_effort`.

