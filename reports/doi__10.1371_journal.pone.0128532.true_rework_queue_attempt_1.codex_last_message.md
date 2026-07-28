Completed the re-review closeout for `doi__10.1371_journal.pone.0128532`.

I verified the worker-4/worker-6 repairs from live artifacts, did not rerun the initial bootstrap, and added a fresh `closed_verified_after_rerun` entry to [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1371_journal.pone.0128532/rework/rework_responses.jsonl). Current state:

- Database audit: `415` linked rows, `291 source_verified`, `124 source_conflict`.
- Activity/toxicity: `135` source-located activity records.
- Mechanism: `3` claims, with direct, computational, and contextual evidence separated.
- `quality_feedback.json`: `issue_count=0`, no `qc_failure_reasons`, no `rework_targets`.
- Workflow context: no open rework tickets; `rwk-complete-test-0001` is resolved.
- Cautions preserved: database/source conflicts and figure-only toxicity values were not fabricated into exact structured values.

Fresh gates passed:

- [semantic_gate.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0128532.semantic_gate.json): `publication_grade_pass_count=1`, `fail_count=0`, `issue_count=0`.
- [publication_quality.json](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1371_journal.pone.0128532.publication_quality.json): `publication_grade_pass=true`, `risk_counts={}`.

JSON integrity also passed for 18 JSON files plus both rework JSONL ledgers. No targeted rework ticket or `unrecoverable_material_gaps` entry is needed for this paper now.

