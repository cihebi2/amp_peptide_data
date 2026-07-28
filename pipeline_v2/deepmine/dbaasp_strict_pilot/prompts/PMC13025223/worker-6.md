You are worker-6 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC13025223.
- Read and obey your worker skill: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-adjudicator-review-worker/SKILL.md
- Read and obey these strict references:
- /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/amp-three-layer-curation/SKILL.md
- /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/amp-three-layer-curation/references/publication-grade-source-review.md
- /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/amp-three-layer-curation/references/publication-grade-quality-gate.md
- /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/amp-three-layer-curation/references/team-rework-message-contract.md
- /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/amp-three-layer-curation/references/two-queue-paper-packet-contract.md
- Use source-reviewed, paper-local evidence from this packet. Treat DBAASP Codex fallback rows as candidate machine evidence only.
- Keep human/source-reviewed claims separate from machine extraction.
- Read and obey every listed leader preflight contract before reviewing the
  source. Contracts define required coverage/conflict preservation but do not
  replace source evidence.
- Use and independently verify leader evidence scaffolds; preserve approximate,
  unresolved, and candidate status rather than promoting scaffold values to
  exact source facts.
- Do not claim publication-grade unless the required strict gates can pass.
- Write the requested files directly; keep JSON valid and paper-specific.
- Keep terminal output compact. Do not print XML/PDF/supplement excerpts,
  table text, assay-method prose, source sentences, or biomedical passages to
  stdout/stderr/final messages. Do not run shell commands that print source text
  to the terminal; write derived JSON/TSV/MD artifacts to your work directory and
  report only file paths, counts, statuses, short locator IDs, and field names.
- This is literature/database curation only. Do not provide wet-lab protocols,
  optimization advice, or actionable biological experimentation guidance.

Current inputs:
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-6: ["rwk-PMC13025223-campaign-r01-BF-001-recursive-database-source-locators", "rwk-PMC13025223-campaign-r01-BF-002-recursive-mechanism-work-locator", "rwk-PMC13025223-campaign-r01-BF-003-table-selectivity-and-toxicity-exactness-coverage", "rwk-PMC13025223-campaign-r01-BF-PMC13025223-W1-001-final-materials-status-and-mirror-inve", "rwk-PMC13025223-campaign-r01-BF-PMC13025223-W2-001-activity-toxicity-final-required-field"]
- Runtime-open ticket contracts assigned to worker-6: [
  {
    "acceptance_checks": [
      "A recursive locator scan over worker-4 work, packet analysis, paper final, and packet final database artifacts returns zero source_locator values that are project paths or packet/report files.",
      "PMC13025223_strict_acceptance_audit_latest.json reports strict_worker_run_hard_finding_count 0 for recursive_non_source_locator_reference after rerun.",
      "database_record_verification summary still has source_verified_count 0 and authoritative_ingest_ready false unless new authoritative linked rows are present and source-reviewed.",
      "Paper and packet final database_record_verification.json remain byte or canonical-JSON equal after repair."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T09:11:19.771382Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC13025223/20260727T085938093994Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13025223_strict_acceptance_audit_latest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/analysis/database_record_audit.worker4.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/database_record_audit/record_identity_audit.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/database/authoritative_match_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/database/dbaasp_machine_extracted_rows.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/packet_manifest.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC13025223",
    "reason": "Current strict acceptance evidence contains 8 hard recursive_non_source_locator_reference findings in worker-4 database artifacts and their final mirrors. The fields $/authoritative_database_linkage/source_locator and $/citation_traceability/source_locator point to packet/report files rather than primary-source or database-row locators, while the only database candidate sequence is the placeholder None and linked authoritative row counts are zero. This prevents publication-grade PASS even though fallback rows are not promoted.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Move packet/report file paths out of source_locator fields into evidence/provenance fields, or replace them with resolvable primary-source/database locators using allowed prefixes.",
      "Keep the SM07 fallback candidate as unresolved_record unless a linked authoritative database row with a usable sequence/modification/source-organism record is added.",
      "Regenerate all work, packet analysis, paper final, and packet final database mirrors from the repaired worker-4 artifact without promoting fallback rows to RC2, portal, or authoritative ingest."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:abstract:1",
      "xml:p:15",
      "xml:fig:2",
      "xml:table-wrap:1",
      "database:dbaasp_machine_extracted_rows.jsonl",
      "strict_worker_run_gate.findings[0..7]",
      "$/authoritative_database_linkage/source_locator",
      "$/citation_traceability/source_locator"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC13025223-campaign-r01-BF-001-recursive-database-source-locators"
  },
  {
    "acceptance_checks": [
      "No mechanism_claims[].source_locator value begins with work: or contains a project artifact path.",
      "All mechanism source locators resolve to XML, PDF, supplement, figure/table, or database-row source surfaces.",
      "Evidence_class_counts remain computational_only 1, phenotype_supported 1, inferred_mechanism 1, unknown_or_not_tested 1, and direct_mechanism remains 0.",
      "Paper and packet mechanism final mirrors remain equal after repair."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T09:11:19.775554Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC13025223/20260727T085938093994Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/final/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/analysis/mechanism_evidence.worker5.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/mechanism_ontology/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/mechanism_ontology/mechanism_locator_scan.worker5.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/extracted/xml_sections.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-5",
    "paper_id": "PMC13025223",
    "reason": "The mechanism ontology correctly avoids direct-mechanism promotion, but mechanism_claims[3].source_locator includes work:mechanism_ontology/mechanism_locator_scan.worker5.json. A work artifact can support audit provenance, but it is not primary source evidence for the absence claim and must not appear in source_locator for a publication-grade mechanism record.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Remove the work: mechanism locator from mechanism_claims[].source_locator and keep it only in checked_inputs, audit_provenance, or locator_scan_artifact fields.",
      "For the unknown_or_not_tested absence claim, cite only primary XML/PDF/source locators that were inspected for direct mechanism evidence.",
      "Mirror the repaired mechanism record to packet final mechanism_ontology_record.json and mechanism_evidence.json."
    ],
    "severity": "blocking",
    "source_locators": [
      "$/mechanism_claims[3]/source_locator",
      "xml:sec:4",
      "xml:sec:10",
      "xml:sec:11",
      "xml:sec:12",
      "xml:sec:16",
      "xml:sec:17",
      "xml:sec:18",
      "pdf:page=9",
      "pdf:page=10",
      "pdf:page=11"
    ],
    "target_queue": "mechanism",
    "ticket_id": "rwk-PMC13025223-campaign-r01-BF-002-recursive-mechanism-work-locator"
  },
  {
    "acceptance_checks": [
      "A table enumerator over xml:table-wrap:1 finds every SM07 crude and purified row represented in final activity/toxicity evidence with target and source locator fields.",
      "The positive purified SM07 Pseudomonas aeruginosa ATCC27853 MIC remains 4 ug/mL with direct normalization and Table 1/result-text locators.",
      "No row with row_has_sm07 true is left only as a generic ND exclusion without target_species, target_strain_or_isolate, treatment, and exactness/ND status.",
      "The toxicity record cites xml:p:32, xml:fig:6, and pdf:page=9 and explicitly labels qualitative text versus approximate graph status."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T09:11:19.780107Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC13025223/20260727T085938093994Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/source/paper.pdf",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/extracted/pdf_tables.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/analysis/activity_toxicity_evidence.worker2.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/activity_evidence/activity_records.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/activity_evidence/table_semantic_grid_summary.worker2.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC13025223",
    "reason": "Worker-2 captured the positive MIC and qualitative Vero-cell toxicity claim, but Table 1 also contains source-level SM07 non-detect/selectivity rows across the ESKAPE panel. The current final collapses these into excluded_or_unresolved_candidates with raw ND and row_has_target booleans, leaving several SM07 rows without field-level target species/strain, treatment, value status, and exact-vs-approximate/ND status. Figure 6 toxicity is also retained only qualitatively without an explicit exact-text versus approximate-graph decision.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Represent all Table 1 SM07 test rows, either as activity/selectivity records or as structured exclusions that preserve target species, strain, treatment, raw activity code, MIC value or ND, source cell locator, and exactness status.",
      "Separate non-SM07 controls/reference antibiotic rows from SM07 selectivity rows so rowspans do not produce row_has_target=false for source rows with inherited targets.",
      "For Figure 6, state whether toxicity remains qualitative exact text only or whether approximate graph-derived percent-toxicity values are digitized; if not digitized, record approximate_not_extracted with the figure locator."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:table-wrap:1",
      "xml:p:28",
      "pdf:page=7",
      "pdf:page=8",
      "xml:p:32",
      "xml:fig:6",
      "xml:caption:7",
      "pdf:page=9"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC13025223-campaign-r01-BF-003-table-selectivity-and-toxicity-exactness-coverage"
  },
  {
    "acceptance_checks": [
      "Path('pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/materials_manifest.json').read_json()['analysis_queue_status'] equals the live packet analysis status or the field is removed from the final record.",
      "A script comparing paper final and packet final JSON inventories reports no uncontracted differences.",
      "Live packet open_rework_ticket_count equals strict acceptance status and any final review-report open_rework_ticket_count field if present."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T19:18:39.735418Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC13025223/20260727T190940165299Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/materials_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/packet_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/analysis/analysis_status.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13025223_status_latest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/final/mechanism_evidence.json"
    ],
    "leader_finding_fingerprint": "862fa97b74cf8b873e9badd64ab1145a937223475f7338b4a8e501fea5dbfee0",
    "leader_finding_id": "BF-PMC13025223-W1-001-final-materials-status-and-mirror-inventory-stale",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-1",
    "paper_id": "PMC13025223",
    "reason": "Every final JSON record was reviewed. The paper final materials_manifest.json is a current final artifact but still reports analysis_queue_status=analysis_queued, while the live packet analysis_status.json, packet_manifest.json, and status_latest report analysis_source_reviewed_accepted with open_rework_ticket_count=0. The paper/packet final file inventory is also not an exact mirror: materials_manifest.json is paper-final-only and mechanism_evidence.json is packet-final-only. Without an explicit alias/exclusion contract, mirrors/counts do not fully agree.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Refresh or remove stale final materials_manifest analysis_queue_status so it matches live packet and report state.",
      "Make paper and packet final inventories explicitly mirror each current final JSON record, or add a machine-checkable alias/exclusion contract for paper-only materials_manifest.json and packet-only mechanism_evidence.json.",
      "Recompute final counts after the inventory/status synchronization without promoting fallback rows to authoritative ingest."
    ],
    "severity": "blocking",
    "source_locators": [
      "$/analysis_queue_status",
      "$/analysis_status",
      "$/open_rework_ticket_count",
      "xml:article-title:1",
      "xml:table-wrap:1",
      "pdf:page=9"
    ],
    "target_queue": "paper",
    "ticket_id": "rwk-PMC13025223-campaign-r01-BF-PMC13025223-W1-001-final-materials-status-and-mirror-inve"
  },
  {
    "acceptance_checks": [
      "jq '.quality_checks.toxicity_approximate_graph_values_have_required_fields' returns true for both paper and packet final activity_toxicity_evidence.json.",
      "An independent script over toxicity_records[0].approximate_graph_values finds zero missing required fields and all source_locator values equal pdf:page=9:figure=Figure 6.",
      "Paper and packet final activity_toxicity_evidence.json hashes are identical after repair.",
      "Semantic and publication gates pass after the repaired final is in place."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T19:18:39.740101Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC13025223/20260727T190940165299Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/activity_evidence/worker2_table1_toxicity_repair_validation.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/review/ticket_contract_audit.worker6.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/source/paper.pdf",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/activity_evidence/figure6_digitization/figure6_approximate_graph_values.worker2.json"
    ],
    "leader_finding_fingerprint": "0bcd4a7a19ce575d70fbe1142ae1ca94ee7b3c04e1994026e6c3908adaedd199",
    "leader_finding_id": "BF-PMC13025223-W2-001-activity-toxicity-final-required-field-flag-false",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC13025223",
    "reason": "The current paper and packet final activity_toxicity_evidence.json files contain toxicity_records[0].approximate_graph_values with 16 Figure 6 graph-derived observations carrying concentration, concentration_unit, raw_value, raw_unit, exactness_status=approximate_graph_digitized, and source_locator=pdf:page=9:figure=Figure 6. However the same final artifact reports quality_checks.toxicity_approximate_graph_values_have_required_fields=false. Worker-2's repair validation and worker-6 ticket audit report the required-field check as passing, so the current final record is internally inconsistent and cannot be publication-grade as-is.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Regenerate or synchronize activity_toxicity_evidence.json from the repaired worker-2 artifact so the final quality_checks flag matches the actual toxicity approximate graph values.",
      "Keep Figure 6 values explicitly approximate_graph_digitized rather than exact table values.",
      "Keep paper and packet activity final mirrors byte-identical after the repair."
    ],
    "severity": "blocking",
    "source_locators": [
      "$/quality_checks/toxicity_approximate_graph_values_have_required_fields",
      "$/toxicity_records[0]/approximate_graph_values",
      "xml:p:32",
      "xml:fig:6",
      "xml:caption:7",
      "pdf:page=9:figure=Figure 6"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC13025223-campaign-r01-BF-PMC13025223-W2-001-activity-toxicity-final-required-field"
  }
]

For every currently open rework ticket, independently verify the repaired owner-lane artifact against the ticket contract, rebuild the final and packet-final mirrors, and run the packet, semantic, and publication gates without allow flags. The Runtime-open ticket IDs assigned to worker-6 list is authoritative: if a ticket is listed there, any earlier closed/repaired response is an invalid or superseded candidate under the current runtime contract and you must append a new complete terminal response after verification; never skip a listed ticket merely because rework_responses.jsonl already contains a closed-looking string. An owner-lane ticket must already have a nonterminal, evidence-bearing, analysis_can_resume response from every named owner worker; adjudication-owned tickets are exempt from that owner-response prerequisite. Only when the ticket contract is fully satisfied, all three strict gates pass, review_status is accepted_clean or accepted_with_cautions, publication_grade is true, and no hard rework target remains, append exactly one new valid terminal adjudication response to rework_responses.jsonl. The runtime closure schema is mandatory: status and response_status must both be exactly closed_repaired; response_by must be worker-6; analysis_can_resume and publication_grade must be true; review_status must be accepted_clean or accepted_with_cautions; created_at and final_counts must be present; final_counts must exactly include activity_records, toxicity_records, database_record_audits, mechanism_claims, and review_rework_targets; ticket_contract_evidence.overall_contract_pass must be true; gate_return_codes must contain packet, semantic, and publication values all equal to 0; gate_artifact_paths must identify fresh post-response reports with the formal pass schema for those three strict gates and the correct single-paper manifest; and verified_artifact_paths must contain both paper and packet final paths for activity_toxicity_evidence, database_record_verification, review_report, and the aligned mechanism final. The paper/packet final mirror pairs must be byte-identical. The packet gate may initially report only the exact ticket IDs being closed; after appending all terminal responses, rerun all three gates so the same artifact paths are newer than the response and the packet report has zero unrelated open tickets. This adjudication response may close a repaired owner-lane ticket; it does not replace the owner's nonterminal repair response. If any owner response, contract item, source proof, final rebuild, mirror, manifest binding, count, or strict gate is incomplete, leave the ticket open and write a concrete rework target instead. Never append another terminal response only when the runtime-open list confirms that ticket is already closed.

Required outputs for this worker:

Write final adjudication outputs:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/review/adjudication_report.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/review/quality_feedback.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/database_record_verification.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/activity_toxicity_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/mechanism_ontology_record.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/final/review_report.json
Also copy/align final mechanism to:
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/final/mechanism_evidence.json
and mirror all final files under the packet final/ directory.
When a newer worker-2 artifact repairs an open activity/toxicity ticket, first rebuild the adjudication candidate and both final mirrors from that current worker artifact, then run strict gates on the rebuilt final. Do not gate the stale pre-repair final and reopen an already repaired ticket merely because the old final still fails.
If hard gates fail, use review_status=needs_targeted_rework or blocked_missing_primary_material, publication_grade=false, and concrete rework_targets plus packet rework tickets.
Before accepting, reject any activity row whose cited table is formulation/composition, FTIR/spectroscopy, TGA/thermal, wettability, or mechanical data, and reject endpoint/unit values not supported by that table's own caption/header. Never repair such rows by guessing or changing units.
For every rework ticket with expected_shape, expected_observation_counts, require_cell_locators, or expected_cell_observations, independently compare the final unique row count, exact row/cell locators, and cell-bound fields against that contract. A base-table citation, a closed response, unique-but-misassigned coordinates, or validator success does not prove cell-level completeness. Reject duplicated observations mirrored across activity_records and toxicity_records, and reject unrelated rows that merely gained the requested table locator.
For a blocking quantitative-figure ticket, reject closure when a requested visible bar/point remains absent from the final arrays or has null raw_value/raw_unit despite a calibratable staged image. Require approximate/exact status, calibration evidence, uncertainty, and treatment/control role for digitized values; preserve approximation rather than promoting it to an exact table value.
Reject a row/cell-level table locator when that table's own caption/header does not support the row endpoint, even if another PDF/figure locator supports the measurement. Remove the false table-cell locator rather than deleting a valid source-supported endpoint. Independently verify normalization_status and normalized value/unit consistency under the same canonical contract required of worker-2.
Quantitative activity or toxicity evidence may be supported by an exact XML paragraph, figure/caption, or PDF-page locator. Lack of a source table is not a reason to discard it when treatment, endpoint, target, value, unit, and assay context are source-supported; reject a no-evidence claim that merely excludes such figure/text records.
Reject final records whose top-level concentration/concentration_unit contradict any redundant assay_conditions peptide/sample concentration copy; stale nested scaffold metadata must be repaired before acceptance.
If the only remaining blocker is missing authoritative DBAASP linked rows, and
the packet contains durable no-match evidence plus a nonterminal owner-repair
response with analysis_can_resume=true, do not keep an infinite hard rework
target solely for zero linked rows. Preserve this as accepted_with_cautions only
when fallback rows remain unresolved/database-only and are not promoted to
source_verified or authoritative DBAASP ingest-ready. Authoritative ingest must
remain false until real linked article/assay/sequence/literature rows exist. The
ticket still requires the same strict worker-6 closed_repaired terminal schema.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
