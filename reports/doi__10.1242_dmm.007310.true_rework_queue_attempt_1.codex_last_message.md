Re-reviewed `doi__10.1242_dmm.007310` and closed `rwk-complete-test-0001` as `accepted_with_cautions`, not clean acceptance.

Repaired artifacts:
- Worker-2: added `253` source-backed activity/toxicity rows from Table 1, Table 2, and Supplementary Table S1.
- Worker-4: re-adjudicated `285` database rows: `248 source_verified`, `35 source_conflict`, `2 sequence_modified_not_normalized`.
- Worker-6: updated final adjudication, quality feedback, mechanism final, and packet/final mirrors; open rework targets are now `0`.

Validation:
- Semantic gate: pass, `issue_count=0` at [semantic gate report](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1242_dmm.007310.codex_worker246_rereview_20260503.semantic_gate.json)
- Publication QA: pass, `risk_counts={}` at [publication QA report](/root/work/抗菌肽/数据库/batch/4-team/reports/doi__10.1242_dmm.007310.codex_worker246_rereview_20260503.publication_quality.json)
- Rework response appended at [rework_responses.jsonl](/root/work/抗菌肽/数据库/batch/4-team/paper_packets/doi__10.1242_dmm.007310/rework/rework_responses.jsonl)

No unrecoverable material gap was needed; remaining caveats are preserved as cautions/conflicts rather than hidden.

