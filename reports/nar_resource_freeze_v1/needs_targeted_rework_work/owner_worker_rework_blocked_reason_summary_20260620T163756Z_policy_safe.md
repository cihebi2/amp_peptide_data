# Owner-Worker Rework Blocked Reason Summary After Policy-Safe Pass

- generated_at: `2026-06-20T17:14:42Z`
- runs: `20260620T090048Z, 20260620T130635Z, 20260620T163756Z_policy_safe`
- attempt_rows: `46`; unique_papers: `30`
- latest accepted: `21`; latest blocked/non-publication-grade: `9`
- accepted sample audit: `21/21 passed`

## Latest Paper-Level Counts
- `accepted_after_rework_attempt1`: `16`
- `accepted_clean_initial_gate_pass`: `5`
- `blocked_model_prompt_safety_restriction_quality_gates_open`: `6`
- `blocked_parser_gap_activity_table`: `1`
- `blocked_source_gap_missing_external_supplement`: `2`

## Attempt-Level Counts
- `accepted_after_rework_attempt1`: `16`
- `accepted_clean_initial_gate_pass`: `5`
- `blocked_model_prompt_safety_restriction_quality_gates_open`: `22`
- `blocked_parser_gap_activity_table`: `1`
- `blocked_source_gap_missing_external_supplement`: `2`

## Current Freeze / Queue State
- `paper_final_artifact_count`: `1471`
- `public_v1_candidate_papers`: `1365`
- `excluded_or_non_publication_grade_papers`: `106`
- `database_audit_rows`: `139259`
- `source_verified_rows`: `95941`
- `non_source_verified_rows`: `43318`
- `activity_records`: `115184`
- `mechanism_claims`: `4772`
- `needs_targeted_rework_count`: `37`
- `owner_worker_rework_queue_count`: `0`
- `material_or_digitization_backlog_count`: `37`

## What Changed In Policy-Safe Pass
- The safety-minimized prompt path removed the systematic `Invalid prompt` blocker for the current owner queue.
- Five current owner-worker papers were re-reviewed: `3` accepted after rework and passed accepted audit; `2` remained blocked for source/parser reasons.
- The owner-worker queue is now empty; remaining `37` needs-targeted-rework papers require source staging, digitization, or backlog handling before another owner-worker pass.

## Real Blocked Reasons Now
- `blocked_model_prompt_safety_restriction_quality_gates_open`: `6`
- `blocked_parser_gap_activity_table`: `1`
- `blocked_source_gap_missing_external_supplement`: `2`

## Latest Blocked Papers
| paper_id | latest_run | refined_status | in_owner_queue | in_material_backlog | key evidence codes | next action |
| --- | --- | --- | --- | --- | --- | --- |
| `doi__10.1038_s41422-022-00617-x` | `20260620T090048Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | `False` | codex_worker_nonzero_exit, invalid_review_status, missing_activity_records, missing_rework_targets_for_hard_gate_issues, missing_source_review_depth_merged_database_rows, missing_target_species, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1038_s41423-020-0374-2` | `20260620T090048Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | `False` | codex_worker_nonzero_exit, invalid_review_status, missing_activity_records, missing_rework_targets_for_hard_gate_issues, missing_target_species, open_rework_targets, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1080_22221751.2021.1937329` | `20260620T130635Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | `False` | codex_worker_nonzero_exit, direct_mechanism_without_assay, invalid_review_status, missing_activity_records, missing_rework_targets_for_hard_gate_issues, missing_target_species, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1126_science.abf4896` | `20260620T090048Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | `False` | codex_worker_nonzero_exit, database_rows_preserved_as_source_conflict, direct_mechanism_without_assay, local_supplementary_dc1_absent, missing_activity_records, missing_target_species, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1186_1743-422x-6-187` | `20260620T090048Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | `False` | codex_worker_nonzero_exit, database_identity_not_amp_sequence_supported, missing_activity_records, missing_source_review_depth_supplementary_assets, missing_target_species, no_primary_amp_sequence_or_peptide_identity, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.3390_v11010031` | `20260620T130635Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | `False` | codex_worker_nonzero_exit, invalid_review_status, missing_activity_records, missing_rework_targets_for_hard_gate_issues, missing_target_species, open_rework_targets, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1038_s41422-020-0305-x` | `20260620T163756Z_policy_safe` | `blocked_parser_gap_activity_table` | `False` | `True` | codex_worker_nonzero_exit, missing_activity_records, missing_concrete_rework_targets, missing_rework_targets_for_hard_gate_issues, missing_target_species, obtainable_only_source_gap_documented, ... | `retry_with_worker2_table_shape_or_manual_vision_fallback` |
| `doi__10.1038_s41467-019-10754-4` | `20260620T090048Z` | `blocked_source_gap_missing_external_supplement` | `False` | `False` | missing_activity_records, missing_local_moesm_supplementary_assets, obtainable_only_source_gap_documented, open_rework_targets, publication_grade_blocked_by_unrecoverable_material_gap, publication_grade_not_true, ... | `retry_only_after_source_staging` |
| `doi__10.1371_journal.pone.0080050` | `20260620T163756Z_policy_safe` | `blocked_source_gap_missing_external_supplement` | `False` | `True` | database_only_activity_not_primary_source_verified, missing_activity_records, no_source_supported_amp_activity_rows, obtainable_only_source_gap_documented, open_rework_targets, publication_grade_blocked_by_activity_primary_source_gap, ... | `retry_only_after_source_staging` |

## Optimization Items Recorded
- Keep `policy_safe_minimal` as the default retry mode for papers that previously hit prompt/content safety restrictions.
- Do not send source-rich biomedical prose or assay snippets through prompts/logs; use local artifacts plus locators and gate outputs.
- Since owner-worker queue is now `0`, do not launch more analysis workers until missing sources/digitization are staged.
- The two policy-safe nonaccepted examples need different paths: one parser/manual table fallback, one source staging for missing external supplement/primary activity support.

## Evidence Paths
- `refined_090048`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/owner_worker_rework_refined_status_20260620T090048Z.json`
- `refined_130635`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/owner_worker_rework_refined_status_20260620T130635Z.json`
- `refined_policy_safe`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/owner_worker_rework_refined_status_20260620T163756Z_policy_safe.json`
- `accepted_audit_090048`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/accepted_sample_audit_20260620T090048Z/accepted_sample_audit_latest.json`
- `accepted_audit_130635`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/accepted_sample_audit_20260620T130635Z/accepted_sample_audit_latest.json`
- `accepted_audit_policy_safe`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/accepted_sample_audit_20260620T163756Z_policy_safe/accepted_sample_audit_latest.json`
- `owner_worker_queue_latest`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/owner_worker_rework_queue_latest.csv`
- `material_or_digitization_backlog_latest`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/material_or_digitization_backlog_latest.csv`
- `release_manifest_latest`: `reports/nar_resource_freeze_v1/release_manifest_latest.json`
- `unified_scope_summary_latest`: `reports/nar_resource_freeze_v1/unified_scope_summary_latest.json`
