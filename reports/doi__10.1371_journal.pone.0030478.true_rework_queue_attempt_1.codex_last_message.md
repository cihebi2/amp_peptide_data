Re-review completed for `doi__10.1371_journal.pone.0030478`. I left it non-accepted.

Updated the worker-2/4/6 artifacts to preserve recoverable evidence without fabricating primary-source support:
- `activity_toxicity_evidence.json`: now records 12 MIC rows as `database_only_no_primary_source`.
- `database_record_verification.json`: 22 linked activity/experiment rows are `database_only_no_primary_source`; 2 literature/context rows remain `source_verified`.
- `review_report.json` and `quality_feedback.json`: now set `review_status: blocked_missing_primary_material`, `publication_grade: false`, and include `unrecoverable_material_gaps`.

Durable rework updates:
- Appended a response to `paper_packets/.../rework/rework_responses.jsonl`.
- Kept the original ticket open and added `rwk-codex-20260503-database-only-primary-gap`.

Gate results after repair:
- Semantic gate: fails only on intentional non-publication status: `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication QA: `publication_grade_pass: false`, with `open_rework_targets: 1`.
- Reports written to `reports/doi__10.1371_journal.pone.0030478.codex_worker246_20260503.semantic_gate.json` and `reports/doi__10.1371_journal.pone.0030478.codex_worker246_20260503.publication_quality.json`.

Key local-source conclusion: local XML/PDF/DOCX/database packet supports database-only preservation of the MIC rows, but does not support treating those values as primary-source activity evidence for this paper.

