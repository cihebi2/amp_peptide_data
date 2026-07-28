Completed the bounded worker-2/4/6 re-review for `doi__10.1371_journal.pone.0212447`.

Changed:
- Added reproducible repair script: `scripts/repair_doi_10_1371_journal_pone_0212447_worker246.py`
- Rebuilt activity/toxicity evidence to 198 records:
  - Table 2: 57 MIC rows recovered
  - Table 3: 63 MIC rows rebuilt
  - Table 4: 70 MIC rows rebuilt
  - Toxicity text rows: 8
- Rebuilt database audit: `sequence_modified_not_normalized=382`, `source_conflict=12`, `source_verified=19`
- Rewrote worker-6 adjudication/final review as `accepted_with_cautions`, with database/modification cautions preserved
- Appended rework response closing `rwk-complete-test-0001`
- Cleared open rework tickets in packet/workflow/quality surfaces

Validation:
- Semantic gate: `pass_count=1`, `fail_count=0`, `issues=0`
- Publication gate: `publication_grade_pass=true`, `risk_counts={}`
- Complete report now says `publication_grade_ready=true`, `open_rework_ticket_count=0`
- JSON parse check passed for 14 updated/report artifacts

Key reports:
- `reports/doi__10.1371_journal.pone.0212447.semantic_gate.json`
- `reports/doi__10.1371_journal.pone.0212447.publication_quality.json`
- `reports/doi__10.1371_journal.pone.0212447.complete_message_test_report.json`

