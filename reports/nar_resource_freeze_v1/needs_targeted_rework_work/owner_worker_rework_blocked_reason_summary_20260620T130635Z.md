# Owner-Worker Rework Blocked Reason Summary

- generated_at: `2026-06-20T13:43:55Z`
- runs: `20260620T090048Z, 20260620T130635Z`
- attempt_rows: `41`; unique_papers: `30`
- latest accepted: `18`; latest blocked/non-publication-grade: `12`
- accepted sample audit: `18/18 passed` (`14/14` for 20260620T090048Z, `4/4` for 20260620T130635Z)

## Latest Paper-Level Counts
- `accepted_after_rework_attempt1`: `13`
- `accepted_clean_initial_gate_pass`: `5`
- `blocked_model_prompt_safety_restriction_quality_gates_open`: `11`
- `blocked_source_gap_missing_external_supplement`: `1`

## Attempt-Level Counts
- `accepted_after_rework_attempt1`: `13`
- `accepted_clean_initial_gate_pass`: `5`
- `blocked_model_prompt_safety_restriction_quality_gates_open`: `22`
- `blocked_source_gap_missing_external_supplement`: `1`

## Current Freeze / Queue State
- `paper_final_artifact_count`: `1471`
- `public_v1_candidate_papers`: `1362`
- `excluded_or_non_publication_grade_papers`: `109`
- `database_audit_rows`: `139259`
- `source_verified_rows`: `95941`
- `non_source_verified_rows`: `43318`
- `activity_records`: `115169`
- `mechanism_claims`: `4772`
- `needs_targeted_rework_count`: `40`
- `owner_worker_rework_queue_count`: `5`
- `material_or_digitization_backlog_count`: `35`

## Real Blocked Reasons
- `infrastructure_model_policy_blocked`: 11 latest papers. Owner-worker Codex review was interrupted by model prompt/content safety restriction while strict semantic/publication gates remained open. This is a runtime/prompting blocker, not evidence that the paper has no usable information.
- `blocked_source_gap_missing_external_supplement`: 1 latest paper. The local material packet lacks the specific supplementary material needed for publication-grade closure; retry only after source staging.

## Latest Blocked Papers
| paper_id | latest_run | refined_status | in_current_owner_queue | key evidence codes | next action |
| --- | --- | --- | --- | --- | --- |
| `doi__10.1038_s41422-020-0305-x` | `20260620T130635Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `True` | codex_worker_nonzero_exit, database_conflicts_require_adjudication, full_source_review_not_completed, missing_activity_records, no_supported_activity_rows_extracted, obtainable_only_source_gap_documented, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1038_s41422-022-00617-x` | `20260620T090048Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | codex_worker_nonzero_exit, invalid_review_status, missing_activity_records, missing_rework_targets_for_hard_gate_issues, missing_source_review_depth_merged_database_rows, missing_target_species, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1038_s41423-020-0374-2` | `20260620T090048Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | codex_worker_nonzero_exit, invalid_review_status, missing_activity_records, missing_rework_targets_for_hard_gate_issues, missing_target_species, open_rework_targets, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1080_22221751.2021.1937329` | `20260620T130635Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | codex_worker_nonzero_exit, direct_mechanism_without_assay, invalid_review_status, missing_activity_records, missing_rework_targets_for_hard_gate_issues, missing_target_species, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1093_infdis_jiv325` | `20260620T130635Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `True` | codex_api_or_network_error, codex_worker_nonzero_exit, database_conflicts_require_adjudication, full_source_review_not_completed, missing_activity_records, no_supported_activity_rows_extracted, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1126_science.abd9909` | `20260620T130635Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `True` | codex_api_or_network_error, codex_worker_nonzero_exit, database_conflicts_require_adjudication, full_source_review_not_completed, missing_activity_records, no_supported_activity_rows_extracted, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1126_science.abf4896` | `20260620T090048Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | codex_worker_nonzero_exit, database_rows_preserved_as_source_conflict, direct_mechanism_without_assay, local_supplementary_dc1_absent, missing_activity_records, missing_target_species, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1186_1743-422x-6-187` | `20260620T090048Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | codex_worker_nonzero_exit, database_identity_not_amp_sequence_supported, missing_activity_records, missing_source_review_depth_supplementary_assets, missing_target_species, no_primary_amp_sequence_or_peptide_identity, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1371_journal.pone.0080050` | `20260620T130635Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `True` | codex_worker_interrupted, codex_worker_nonzero_exit, database_conflicts_require_adjudication, full_source_review_not_completed, missing_activity_records, no_supported_activity_rows_extracted, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.3390_v11010031` | `20260620T130635Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `False` | codex_worker_nonzero_exit, invalid_review_status, missing_activity_records, missing_rework_targets_for_hard_gate_issues, missing_target_species, open_rework_targets, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.3390_v11010056` | `20260620T130635Z` | `blocked_model_prompt_safety_restriction_quality_gates_open` | `True` | activity_extraction_requires_worker2_rework, codex_worker_nonzero_exit, database_conflicts_require_adjudication, full_source_review_not_completed, missing_activity_records, no_supported_activity_rows_extracted, ... | `retry_with_policy_safe_minimized_context_or_manual_queue` |
| `doi__10.1038_s41467-019-10754-4` | `20260620T090048Z` | `blocked_source_gap_missing_external_supplement` | `False` | missing_activity_records, missing_local_moesm_supplementary_assets, obtainable_only_source_gap_documented, open_rework_targets, publication_grade_blocked_by_unrecoverable_material_gap, publication_grade_not_true, ... | `retry_only_after_source_staging` |

## Optimization Items Recorded
- Add/use `safe_prompt_rework_needed` follow-up queue for model-safety-interrupted papers; retry with minimized paper-local evidence context and avoid dumping long antiviral/therapeutic text into the prompt.
- Keep strict gate semantics: accepted-after-rework is not clean; every accepted paper must still pass accepted sample audit before publication-grade claims.
- Do not treat database-only rows as source-verified; preserve source conflicts and value mismatches as cautions/conflicts.
- For the five current owner-worker rows, the real next repair target is worker-2 activity extraction/table parsing, not broad full-paper rediscovery.
- For the material/digitization backlog, stage missing source or digitize figures before sending back to owner-worker review.

## Evidence Paths
- `refined_090048`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/owner_worker_rework_refined_status_20260620T090048Z.json`
- `refined_130635`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/owner_worker_rework_refined_status_20260620T130635Z.json`
- `accepted_audit_090048`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/accepted_sample_audit_20260620T090048Z/accepted_sample_audit_latest.json`
- `accepted_audit_130635`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/accepted_sample_audit_20260620T130635Z/accepted_sample_audit_latest.json`
- `safe_prompt_queue_090048`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/followup_queues/owner_worker_rework_20260620T090048Z_safe_prompt_rework_needed.json`
- `safe_prompt_queue_130635`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/followup_queues/owner_worker_rework_20260620T130635Z_safe_prompt_rework_needed.json`
- `owner_worker_queue_latest`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/owner_worker_rework_queue_latest.csv`
- `material_or_digitization_backlog_latest`: `reports/nar_resource_freeze_v1/needs_targeted_rework_work/material_or_digitization_backlog_latest.csv`
- `release_manifest_latest`: `reports/nar_resource_freeze_v1/release_manifest_latest.json`
- `unified_scope_summary_latest`: `reports/nar_resource_freeze_v1/unified_scope_summary_latest.json`
