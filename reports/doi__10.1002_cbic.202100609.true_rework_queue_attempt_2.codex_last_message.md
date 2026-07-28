Re-reviewed exactly `doi__10.1002_cbic.202100609` and left it non-accepted.

Updated the owner-layer artifacts under:
- `paper_packets/.../analysis/adjudication_report.json`
- `paper_packets/.../analysis/analysis_status.json`
- `papers/.../final/review_report.json`
- `papers/.../work/review/quality_feedback.json`
- `paper_packets/.../rework/rework_responses.jsonl`
- refreshed gate reports under `reports/doi__10.1002_cbic.202100609.*`

Result: Table S5 remains structured as 336 MIC rows, final activity has 376 rows total, database audit remains `415 source_verified / 139 source_conflict`, and Figure 4 exact HepG2/HEK293 cytotoxicity percentages remain an unrecoverable local-material gap. The active ticket is `rwk-cbic202100609-figure4-exact-cytotoxicity-unrecoverable-0003`; superseded tickets were closed in the message-bus context.

Validation:
- Semantic gate rerun: fails expected with `review_status_not_publication_grade` and `publication_grade_not_true`.
- Publication gate rerun: fails expected with `open_rework_targets=1`.
- Activity row QC: `FINAL_ACTIVITY_BAD_COUNT=0`.
- Verified database locator gaps: `0`.
- Message bus validate: `ok=true`.

`review_status` remains `needs_targeted_rework`, `publication_grade=false`.

