Re-reviewed `doi__10.1038_s41467-024-53309-y` under worker-2/4/6 only.

Result: left the paper **non-accepted** as `blocked_missing_primary_material` / `blocked_after_best_effort`. The stale blocker “no activity rows” is now obsolete: the artifacts preserve `236` source-located activity/toxicity records. The remaining blockers are documented as unrecoverable from local materials:

- `missing_declared_supplementary_source_data` (`worker-6`): XML declares MOESM PDF/XLSX files, but local supplement assets are HTML landing captures.
- `linked_sequence_records_absent_database_identity_unresolved` (`worker-4`): `linked_sequence_records.jsonl` has `0` rows, so full database identity verification is not controllable.

Updated paper-local artifacts include packet/final activity, database, adjudication, review, analysis status, `quality_feedback.json`, `rework_requests.jsonl`, `rework_responses.jsonl`, and reports. I also added the bounded repair script at `scripts/repair_doi_10_1038_s41467_024_53309_y_worker246_blocked.py`.

Validation:
- Semantic gate rerun: failed as expected with `review_status_not_publication_grade`, `publication_grade_not_true`.
- Publication gate rerun: failed as expected with open rework target; activity count recognized as `236`.
- JSON parse check: passed.
- `miaobi_message_bridge.py validate`: passed.

Open targeted tickets now are:
- `rwk-20260505-worker6-missing-moesm`
- `rwk-20260505-worker4-linked-sequence-absent`

