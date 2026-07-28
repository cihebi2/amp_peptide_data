Completed the bounded re-review for `doi__10.1038_s41598-017-13685-6`. I did **not** mark it accepted.

Repairs made:
- Worker-2: rebuilt activity/toxicity evidence from primary XML/PDF Tables 4-7. Final activity now has `262` rows, including `18` Table 6 SC50 hemolysis rows and `14` Table 7 inhibition rows.
- Worker-4: rebuilt database adjudication with `423` audit rows: `69 source_verified`, `194 source_conflict`, `160 database_only_no_primary_source`.
- Worker-6: updated final review to `review_status=blocked_missing_primary_material`, `publication_grade=false`, with `unrecoverable_material_gaps` for missing local `41598_2017_13685_MOESM1_ESM.pdf`.

Key updated artifacts:
- [final/review_report.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-13685-6/final/review_report.json)
- [final/activity_toxicity_evidence.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-13685-6/final/activity_toxicity_evidence.json)
- [final/database_record_verification.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-13685-6/final/database_record_verification.json)
- [quality_feedback.json](/root/work/抗菌肽/数据库/batch/4-team/papers/doi__10.1038_s41598-017-13685-6/work/review/quality_feedback.json)
- [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1038_s41598-017-13685-6/rework/rework_responses.jsonl)

Gate results:
- Semantic gate rerun: failed only on intentional non-publication-grade status: `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication gate rerun: failed only on `open_rework_targets`.
- Reports written to `reports/doi__10.1038_s41598-017-13685-6.semantic_gate.json` and `reports/doi__10.1038_s41598-017-13685-6.publication_quality.json`.

A new targeted ticket `rwk-codex-rereview-20260505-0001` and response `rsp-codex-rereview-20260505-0001` were appended. The stop condition is source exhaustion: main-table values were recovered, but supplementary-only database values cannot be verified from local material.

