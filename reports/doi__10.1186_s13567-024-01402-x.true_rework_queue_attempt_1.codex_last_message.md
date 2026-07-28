Re-reviewed `doi__10.1186_s13567-024-01402-x` without rerunning the initial bootstrap.

Updated worker-owned layers:
- Worker-2: 251 source-located activity/toxicity rows from Tables 2-6.
- Worker-4: 209 DBAASP audit rows, with `127 source_verified` and `82 source_conflict` preserved.
- Worker-6: final review now `accepted_with_cautions`, `publication_grade: true`, no open rework targets.

Key outputs updated:
- `paper_packets/.../analysis/*`
- `papers/.../final/*`
- `papers/.../work/review/quality_feedback.json`
- `paper_packets/.../rework/rework_responses.jsonl`
- `paper_packets/.../packet_manifest.json`

Validation passed:
- Semantic gate: `issue_count: 0`, `publication_grade_pass: true`
- Publication QA: `publication_grade_pass: true`, `risk_counts: {}`
- Fresh reports:
  - `reports/doi__10.1186_s13567-024-01402-x.codex_rereview_20260503.semantic_gate.json`
  - `reports/doi__10.1186_s13567-024-01402-x.codex_rereview_20260503.publication_quality.json`

The material layer remains separate: `material_queue_status` is still `material_extracted_with_gaps`, with a nonblocking caution that local supplementary entries are HTML/link pages rather than local DOCX payloads. No `unrecoverable_material_gaps` were needed for the accepted local-source-supported claims.

