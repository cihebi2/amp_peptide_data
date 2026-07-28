Re-reviewed `doi__10.3389_fmicb.2025.1669022` and repaired the owned layers only.

Updated the worker-2/4/6 artifacts under `paper_packets/.../analysis`, `papers/.../final`, and `papers/.../work/review`. The paper is now `accepted_with_cautions`, not `accepted_clean`: APD6 PMID/linkage conflicts and the negative intracellular activity result are preserved as cautions. No unrecoverable material gaps were needed.

Key outputs:
- Rework response appended: `paper_packets/doi__10.3389_fmicb.2025.1669022/rework/rework_responses.jsonl`
- QC cleared: `papers/doi__10.3389_fmicb.2025.1669022/work/review/quality_feedback.json`
- Semantic gate: `issue_count: 0`, `publication_grade_pass: true`
- Publication gate: `publication_grade_pass: true`, `risk_counts: {}`

Validation run:
- `semantic_three_layer_gate.py --root . --paper-id doi__10.3389_fmicb.2025.1669022 --json`
- `check_three_layer_publication_quality.py --manifest reports/doi__10.3389_fmicb.2025.1669022.complete_message_test_manifest.json --root .`

Final layer state: material packet remains `material_extracted_with_gaps`, validator contract is ready, semantic gate passes, and publication-grade review passes as `accepted_with_cautions`.

