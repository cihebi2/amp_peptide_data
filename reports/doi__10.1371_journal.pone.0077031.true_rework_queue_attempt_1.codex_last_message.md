Re-reviewed `doi__10.1371_journal.pone.0077031` without rerunning the initial bootstrap.

Updated status is `accepted_with_cautions`, with `rwk-complete-test-0001` closed. The material layer remains separate as `material_extracted_with_gaps`; the analysis/review layer is now `analysis_accepted_with_cautions`.

Key repaired outputs:
- [final review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0077031/final/review_report.json)
- [final activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0077031/final/activity_toxicity_evidence.json)
- [final database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0077031/final/database_record_verification.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1371_journal.pone.0077031/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0077031/rework/rework_responses.jsonl)

What changed:
- Worker-2: extracted `18` source-supported Table 2 LC/MFC rows; preserved `2` not-determined cells.
- Worker-4: reconciled `47` database audit rows: `39 source_verified`, `7 source_conflict`, `1 database_only_no_primary_source`.
- Worker-6: rewrote final adjudication/review, cleared `qc_failure_reasons`, `rework_targets`, and `unrecoverable_material_gaps`.

Verification passed:
- [semantic gate](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0077031.semantic_gate.json): `publication_grade_pass_count=1`, `issue_count=0`.
- [publication QA](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0077031.publication_quality.json): `publication_grade_pass=true`, `risk_counts={}`.
- JSON/JSONL sanity checks passed for updated artifacts and workflow state.

Cautions preserved: Phd-1/Phd-3 activity values are Table 2 values footnoted to prior reference `[23]`; CAMP/dbAMP broad or unsupported rows remain conflict/database-only, not smoothed into source-verified records.

