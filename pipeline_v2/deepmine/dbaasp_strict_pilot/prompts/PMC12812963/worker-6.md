You are worker-6 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12812963.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-6: ["rwk-PMC12812963-campaign-r01-worker1-stale-material-final-and-packet-mirror-state", "rwk-PMC12812963-campaign-r01-worker2-activity-target-strain-mismatch", "rwk-PMC12812963-campaign-r01-worker3-unrecovered-supplement-payloads-without-blocking-tic", "rwk-PMC12812963-campaign-r01-worker4-database-layer-publication-grade-claim-without-autho", "rwk-PMC12812963-campaign-r01-worker5-recursive-non-source-mechanism-locator"]
- Runtime-open ticket contracts assigned to worker-6: [
  {
    "acceptance_checks": [
      "Assert papers/PMC12812963/final/materials_manifest.json reports the same known_missing_or_blocked_materials count as packets/PMC12812963/packet_manifest.json or explicitly records its deprecation.",
      "Assert packet and paper final material status fields are not contradictory for material_queue_status and analysis_queue_status.",
      "Assert live rework_requests.jsonl open ticket count equals any final-review open_rework_ticket_count field or gate summary count."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T22:53:53.017891Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12812963/20260727T224149683171Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/final/materials_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/packet_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/intake/source_inventory.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/rework",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12812963_strict_acceptance_audit_latest.json"
    ],
    "leader_finding_fingerprint": "33ee41b07a2cbea39d61af23a5c5efaa263ec706be618cbde0812d75cdff2329",
    "leader_finding_id": "worker1_stale_material_final_and_packet_mirror_state",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-1",
    "paper_id": "PMC12812963",
    "reason": "The current paper final materials_manifest is stale relative to the live packet and review state: it reports analysis_queued and no known_missing_or_blocked_materials, while the live packet manifest reports analysis_source_reviewed_accepted with two unrecoverable supplement gaps and updated_at 2026-07-27T22:41:48Z. This is not an unreadable-path infrastructure failure; it is a final-record consistency failure for a readable current final JSON record.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Refresh the material final record from the live packet state or remove it from the publication-grade final set if it is not authoritative.",
      "Ensure the paper and packet final mirrors expose the same material gap/status counts for this paper.",
      "Keep live packet ticket counts and final review material counts synchronized before any publication-grade claim."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:supplementary-material:id=SM1",
      "xml:supplementary-material:id=SM2",
      "papers/final/materials_manifest.json $.analysis_queue_status=analysis_queued",
      "papers/final/materials_manifest.json $.known_missing_or_blocked_materials=[]",
      "packets/PMC12812963/packet_manifest.json $.known_missing_or_blocked_materials count=2"
    ],
    "target_queue": "paper",
    "ticket_id": "rwk-PMC12812963-campaign-r01-worker1-stale-material-final-and-packet-mirror-state"
  },
  {
    "acceptance_checks": [
      "Parse final activity_records and assert no accepted record has target_strain_or_isolate=1080.",
      "Assert records PMC12812963-W2-ACT-0033 and PMC12812963-W2-ACT-0041 have target_strain_or_isolate=10802c.",
      "Assert a caution or conflict object references xml:sec6 and xml:table-wrap:4 for the 4162/4612 discrepancy."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T22:53:53.022481Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12812963/20260727T224149683171Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/source/paper.pdf",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/pdf_tables.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/activity_evidence/activity_records.json"
    ],
    "leader_finding_fingerprint": "106382d38fea653bc4acc3a423ad50c6aa416290a5747cd420d7a395c5ed9788",
    "leader_finding_id": "worker2_activity_target_strain_mismatch",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC12812963",
    "reason": "Accepted activity records PMC12812963-W2-ACT-0033 and PMC12812963-W2-ACT-0041 cite Table 4 cell 8 but record target_strain_or_isolate as 1080. The primary XML/PDF Table 4 header for that column is 10802c. The same source region also has an unresolved methods/Table 4 conflict where methods list 4162 while Table 4 lists 4612; this should be preserved rather than silently normalized.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Correct Table 4 column 8 activity records to target_strain_or_isolate=10802c.",
      "Add a source-conflict caution for the methods 4162 versus Table 4 4612 discrepancy, or justify the chosen value with a primary-source locator.",
      "Rerun row-level activity validation against parsed XML/PDF table grids and update paper/packet final mirrors."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:table-wrap:4:row=1:cell=8 header=10802c",
      "xml:table-wrap:4:row=2:cell=8 MIC value 16",
      "xml:table-wrap:4:row=3:cell=8 IC50 value 9",
      "xml:sec6 methods lists P. gingivalis isolates 4162, 5607, 8012, 10802c",
      "pdf:page=6 Table 4 header 10802c and 4612"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC12812963-campaign-r01-worker2-activity-target-strain-mismatch"
  },
  {
    "acceptance_checks": [
      "Run file-type checks showing Image_1.tif is an image payload and Presentation_1.pptx is a valid office/zip payload, or verify a blocking rework_requests.jsonl ticket exists for each unavailable true payload.",
      "Assert supplementary_text.jsonl or supplementary_tables.json contains extracted source material when the payload is recovered, or assert review_status is not accepted_clean/accepted_with_cautions when recovery remains impossible.",
      "Assert worker-3 lane_completion_assessment.source_reviewed_complete is true only after payload recovery or a source-backed nonimpact determination."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T22:53:53.027024Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12812963/20260727T224149683171Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/source/supplementary/Image_1.tif",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/source/supplementary/Presentation_1.pptx",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/supplementary_index.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/supplementary_text.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/supplementary_tables.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extraction/extraction_errors.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/supplementary_methods/supplementary_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/rework/rework_requests.jsonl"
    ],
    "leader_finding_fingerprint": "dafbd1d068d34ea90667543f3a53b9af9e9ccbfbc966e89c78e186d25c981f6b",
    "leader_finding_id": "worker3_unrecovered_supplement_payloads_without_blocking_ticket",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-3",
    "paper_id": "PMC12812963",
    "reason": "Both staged supplementary files are readable but are not the declared scientific payloads: file inspection shows HTML documents saved as Image_1.tif and Presentation_1.pptx, supplementary_text.jsonl is empty, and supplementary_tables.json contains no tables. Worker-3 recorded source_reviewed_complete=false, needs_targeted_rework=true, and analysis_can_resume=false for supplement-dependent claims, but live rework_requests.jsonl is empty and final review accepted the paper with only cautions.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Recover the true supplementary TIF/PPTX payloads, or keep this paper non-publication-grade with a blocking material ticket that names the unavailable payloads and attempted commands.",
      "Populate extracted supplementary text/table/image evidence where recoverable, or explicitly prove that the missing payloads cannot affect activity, identity, mechanism, methods, or toxicity fields.",
      "Update packet material status and final review status so unresolved supplement payload gaps cannot be accepted as publication-grade complete."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:supplementary-material:id=SM1",
      "xml:supplementary-material:id=SM2",
      "source/supplementary/Image_1.tif HTML title Preparing to download",
      "source/supplementary/Presentation_1.pptx HTML title Preparing to download"
    ],
    "target_queue": "material",
    "ticket_id": "rwk-PMC12812963-campaign-r01-worker3-unrecovered-supplement-payloads-without-blocking-tic"
  },
  {
    "acceptance_checks": [
      "Assert linked_article_records, linked_assay_records, linked_sequence_records, and linked_literature_records contain authoritative rows before any record is source_verified.",
      "If linked rows remain zero, assert final database_record_verification.json publication_grade=false and review_report publication_grade=false.",
      "Assert database_candidate_boundary.fallback_rows_promoted_to_source_verified remains false."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T22:53:53.031448Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12812963/20260727T224149683171Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/database_source_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/authoritative_match_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_article_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_assay_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_sequence_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_literature_records.jsonl"
    ],
    "leader_finding_fingerprint": "d2ed88606b88f48ebb51c4aa3b1e7c4b3b94cac05b24a443931b60e97d99b4cd",
    "leader_finding_id": "worker4_database_layer_publication_grade_claim_without_authoritative_records",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC12812963",
    "reason": "The final database layer claims publication_grade=true even though authoritative linked database row counts are all zero, every one of the 5 record audits is unresolved_record, and source_verified count is 0. The fallback rows are correctly excluded from authoritative ingest, but a database-record verification layer with no authoritative records cannot be publication-grade source verified.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Either recover authoritative APD6/DBAASP/DRAMP/merged database linkage rows for the paper and re-audit each record, or downgrade the database layer and paper publication-grade claim to non-ready while preserving unresolved_record statuses.",
      "Keep DBAASP fallback rows as candidate-only and excluded from RC2/portal/authoritative ingest unless stable authoritative links are present.",
      "Update final review/report fields so publication_grade_ready is false when database verification remains unresolved."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:article-id pub-id-type=doi 10.3389/fmicb.2025.1709243",
      "xml:article-id pub-id-type=pmid 41561022",
      "xml:table-wrap:1",
      "xml:fig:3",
      "xml:table-wrap:4",
      "database_record_verification.json $.summary_counts.unresolved_record=5",
      "authoritative_match_report.json $.row_counts all zero"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC12812963-campaign-r01-worker4-database-layer-publication-grade-claim-without-autho"
  },
  {
    "acceptance_checks": [
      "Recursively scan final/work/analysis mechanism JSON and assert source_locator/supporting_source_locators values do not contain pipeline_v2 paths.",
      "Assert strict_acceptance_audit_latest.json strict_worker_run_gate.hard_finding_count is 0 for PMC12812963.",
      "Assert recursive_authority_boundary_false is true only after the recursive locator findings are cleared."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T22:53:53.036056Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12812963/20260727T224149683171Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/final/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/analysis/mechanism_evidence.worker5.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/mechanism_ontology/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12812963_strict_acceptance_audit_latest.json"
    ],
    "leader_finding_fingerprint": "a9e1e52eaedf354e7d8a724553e3aff701935528f8ec1d272bfffe28e1541538",
    "leader_finding_id": "worker5_recursive_non_source_mechanism_locator",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-5",
    "paper_id": "PMC12812963",
    "reason": "The current strict acceptance artifact records 5 hard recursive_non_source_locator_reference findings for the mechanism layer. Mechanism claim 2 in work, analysis, packet-final, and paper-final artifacts lists pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/analysis/activity_toxicity_evidence.worker2.json under supporting_source_locators; that is a derivative worker artifact, not a primary XML/PDF/table/supplement/database locator.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Move worker-artifact paths out of source-locator fields and into provenance or checked-input fields.",
      "Replace mechanism claim 2 supporting_source_locators with primary source locators such as xml:table-wrap:1, xml:table-wrap:2, and xml:table-wrap:4.",
      "Rerun the strict worker-run recursive-authority gate and do not claim publication-grade readiness until hard_finding_count is zero."
    ],
    "severity": "blocking",
    "source_locators": [
      "$/mechanism_claims/1/supporting_source_locators/0",
      "xml:table-wrap:1",
      "xml:table-wrap:2",
      "xml:table-wrap:4",
      "xml:sec15",
      "xml:fig:4",
      "pdf:page=6 Table 4",
      "pdf:page=7 Figure 4"
    ],
    "target_queue": "mechanism",
    "ticket_id": "rwk-PMC12812963-campaign-r01-worker5-recursive-non-source-mechanism-locator"
  }
]

For every currently open rework ticket, independently verify the repaired owner-lane artifact against the ticket contract, rebuild the final and packet-final mirrors, and run the packet, semantic, and publication gates without allow flags. The Runtime-open ticket IDs assigned to worker-6 list is authoritative: if a ticket is listed there, any earlier closed/repaired response is an invalid or superseded candidate under the current runtime contract and you must append a new complete terminal response after verification; never skip a listed ticket merely because rework_responses.jsonl already contains a closed-looking string. An owner-lane ticket must already have a nonterminal, evidence-bearing, analysis_can_resume response from every named owner worker; adjudication-owned tickets are exempt from that owner-response prerequisite. Only when the ticket contract is fully satisfied, all three strict gates pass, review_status is accepted_clean or accepted_with_cautions, publication_grade is true, and no hard rework target remains, append exactly one new valid terminal adjudication response to rework_responses.jsonl. The runtime closure schema is mandatory: status and response_status must both be exactly closed_repaired; response_by must be worker-6; analysis_can_resume and publication_grade must be true; review_status must be accepted_clean or accepted_with_cautions; created_at and final_counts must be present; final_counts must exactly include activity_records, toxicity_records, database_record_audits, mechanism_claims, and review_rework_targets; ticket_contract_evidence.overall_contract_pass must be true; gate_return_codes must contain packet, semantic, and publication values all equal to 0; gate_artifact_paths must identify fresh post-response reports with the formal pass schema for those three strict gates and the correct single-paper manifest; and verified_artifact_paths must contain both paper and packet final paths for activity_toxicity_evidence, database_record_verification, review_report, and the aligned mechanism final. The paper/packet final mirror pairs must be byte-identical. The packet gate may initially report only the exact ticket IDs being closed; after appending all terminal responses, rerun all three gates so the same artifact paths are newer than the response and the packet report has zero unrelated open tickets. This adjudication response may close a repaired owner-lane ticket; it does not replace the owner's nonterminal repair response. If any owner response, contract item, source proof, final rebuild, mirror, manifest binding, count, or strict gate is incomplete, leave the ticket open and write a concrete rework target instead. Never append another terminal response only when the runtime-open list confirms that ticket is already closed.

Required outputs for this worker:

Write final adjudication outputs:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/review/adjudication_report.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/review/quality_feedback.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/final/database_record_verification.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/final/activity_toxicity_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/final/mechanism_ontology_record.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/final/review_report.json
Also copy/align final mechanism to:
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/final/mechanism_evidence.json
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
