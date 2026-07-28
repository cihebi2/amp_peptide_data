Completed the DOI-local re-review for `doi__10.1016_j.isci.2021.102480`.

The paper remains **non-accepted**: `review_status=blocked_missing_primary_material`, `publication_grade=false`. Repaired evidence now preserves `17` source-supported activity rows, and database adjudication has `9` audits: `5 source_conflict`, `4 sequence_modified_not_normalized`, `0 source_verified`.

Updated/confirmed:
- `papers/.../final/review_report.json`
- `papers/.../work/review/quality_feedback.json`
- packet/final activity and database artifacts
- `paper_packets/.../rework/rework_requests.jsonl`
- `paper_packets/.../rework/rework_responses.jsonl`
- `.miaobi-paper-review/.../workflow_context.json`

Gate results:
- Semantic gate: failed as expected, exit `1`; only hard issues are `review_status_not_publication_grade` and `publication_grade_not_true`.
- Publication QA: failed as expected, exit `2`; `activity_records=17`, `mechanism_claims=3`, `open_rework_targets=1`.
- Fresh reports written under `reports/doi__10.1016_j.isci.2021.102480.codex_rereview_20260502.*.json`.

The old broad ticket `rwk-complete-test-0001` is closed/superseded. The remaining open ticket is `rwk-codex-20260502-0001`, with explicit `omission_code=dbaasp_exact_activity_values_not_primary_source_supported`, owner `worker-4 + worker-6`, artifact path, and source paths to check.

Validation passed:
- `jq_json_valid=1`
- `miaobi_message_bridge.py validate` returned `ok: true`
- This checkout is not a git repository, so no git diff/status evidence is available.

