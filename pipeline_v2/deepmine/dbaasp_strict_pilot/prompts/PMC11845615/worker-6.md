You are worker-6 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC11845615.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-6: ["rwk-PMC11845615-campaign-r01-BF-PMC11845615-W1-MATERIALS-MANIFEST-MIRROR-STATUS-STALE", "rwk-PMC11845615-campaign-r01-BF-PMC11845615-W2-ACTIVITY-TARGET-LOCATOR-CONFLICT", "rwk-PMC11845615-campaign-r01-BF-PMC11845615-W2-MIC-CONDITIONS-LOCATORS", "rwk-PMC11845615-campaign-r01-BF-PMC11845615-W5-CURRENT-FINAL-MECHANISM-MIRROR-NONTERMINAL", "rwk-PMC11845615-campaign-r01-PMC11845615-BLOCKER-W2-ACTIVITY-TABLE-COVERAGE", "rwk-PMC11845615-campaign-r01-PMC11845615-BLOCKER-W4-DATABASE-SEQUENCE-PLACEHOLDER", "rwk-PMC11845615-campaign-r01-PMC11845615-BLOCKER-W5-MECHANISM-DIRECT-CLAIM-UNSUPPORTED", "rwk-PMC11845615-campaign-r02-BF-PMC11845615-W4-001-recursive-database-source-locators", "rwk-PMC11845615-campaign-r02-BF-PMC11845615-W5-001-mechanism-non-source-and-stale-ticket-", "rwk-PMC11845615-campaign-r03-PMC11845615-BF-W2-ENTITY-PRODUCER-GENUS-AND-SEQUENCE-PLACEHO"]
- Runtime-open ticket contracts assigned to worker-6: [
  {
    "acceptance_checks": [
      "A table parser over paper.xml Table 1 yields 26 accounted observations with counts 16 '+', 5 'GR', and 5 no-activity/excluded records.",
      "No accepted activity target_strain_or_isolate contains temperature, atmosphere, medium, '+', 'GR', or activity text.",
      "The MIC row remains a separate purified leucocyclicin C record with raw_value 3.288, raw_unit \u00191M, target_species Clostridium perfringens, target_strain_or_isolate EM124, and method/result locators xml:p:30/xml:sec:9.",
      "Every accepted or excluded Table 1 observation has a resolvable source_locator to xml:table-wrap:1 row coordinates."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T09:16:20.166911Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T090559867438Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/extracted/pdf_tables.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/work/activity_evidence/activity_records.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC11845615",
    "reason": "Layer-2 activity evidence is not publication-grade. Table 1 is a 26-row source table with separate Species, Strains, Temperature, Atmosphere, Media, and Inhibitory activity columns. The final activity records omit source-positive/GR observations and merge culture conditions/activity symbols into target_strain_or_isolate values such as 'DK279 37 Aerobic BHI +' and 'PA-01 37 Aerobic BHI +'. Several rows also leave treatment and assayed_entity as 'not reported' even though the source assay is L. lactis APC 3969 producer strain/CFSN, not generic unknown treatment.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Rebuild all Table 1 qualitative activity observations from the XML/PDF table structure, preserving species, strain/isolate, temperature, atmosphere, medium, and activity result in separate fields.",
      "Account for all 26 Table 1 rows: accepted activity, growth-reduction, no-activity/excluded, or explicit exclusion with source locator and reason; do not silently omit Clostridium tyrobutyricum DSM 663 or GR rows.",
      "Separate L. lactis APC 3969 producer-strain/CFSN/spot-on-lawn/WDA evidence from purified leucocyclicin C MIC evidence.",
      "Remove 'not reported' treatment/entity placeholders from accepted rows unless the source truly lacks the field and the row has an explicit no-source rationale."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:sec:2",
      "xml:table-wrap:1:row=3",
      "xml:table-wrap:1:row=7",
      "xml:table-wrap:1:row=10",
      "xml:table-wrap:1:row=22",
      "xml:table-wrap:1:row=23",
      "pdf:page=3",
      "xml:p:30",
      "xml:sec:9"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC11845615-campaign-r01-PMC11845615-BLOCKER-W2-ACTIVITY-TABLE-COVERAGE"
  },
  {
    "acceptance_checks": [
      "Recursive scan finds no sequence or candidate_sequence value equal to 'None' with a sequence_length field.",
      "For every object containing a plain one-letter sequence and sequence_length, residue count exactly equals sequence_length; cyclization is represented as a modification, not a residue.",
      "linked_article_records, linked_assay_records, linked_sequence_records, and linked_literature_records remain zero unless actual authoritative rows are present, and authoritative_dbaasp_ingest_ready remains false recursively.",
      "database_record_verification.json top-level review_model is gpt-5.5 and reasoning_effort is xhigh, with source_reviewed=true."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T09:16:20.170988Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T090559867438Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/dbaasp_machine_extracted_rows.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/authoritative_match_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.xml"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC11845615",
    "reason": "Layer-1 database verification is not source-reviewable as written. All five audits are fallback machine rows with stable_authoritative_database_record_id=null and candidate_sequence='None' plus candidate_sequence_length=4. The primary source states leucocyclicin C comprises 61 amino acids, llcA is a 63-aa precursor, the leader is MF, and the mature peptide is head-to-tail cyclized; the final record neither captures a valid sequence/modification boundary nor cleanly represents the zero-authoritative-row database state.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Rebuild the database audit to distinguish zero linked authoritative DBAASP rows from fallback machine candidates; do not present fallback rows as stable database records.",
      "Replace placeholder candidate_sequence='None'/candidate_sequence_length=4 with a structured null/not-reported state, or recover the actual source sequence from Fig. 3 and count residues exactly, excluding terminal cyclization chemistry from residue count.",
      "Preserve source identity fields for leucocyclicin C: mature 61-aa cyclic bacteriocin, llcA 63-aa precursor, MF leader, 6081.44 Da theoretical cyclic mass, producer Leuconostoc lactis APC 3969, DOI 10.1038/s41598-025-89450-x, PMCID PMC11845615.",
      "Make top-level worker-4 final provenance internally consistent with the current run_sequence gpt-5.5/xhigh evidence."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:abstract:1",
      "xml:p:18",
      "xml:table-wrap:4",
      "xml:p:40",
      "pdf:page=1",
      "pdf:page=4",
      "pdf:page=10"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC11845615-campaign-r01-PMC11845615-BLOCKER-W4-DATABASE-SEQUENCE-PLACEHOLDER"
  },
  {
    "acceptance_checks": [
      "direct_mechanism_claim_count is 0 unless an actual direct mechanism assay locator from this paper is present.",
      "No final mechanism claim contains 'ribosome binding assay', 'SPR binding assay', or source_locator xml:p:54.",
      "Every mechanism claim has claim_id, claim_text, evidence_class, source_locator, and direct_assay_types only when evidence_class is direct_mechanism.",
      "A search of XML/PDF/supplement surfaces for ribosome, SPR, binding, permeability, membrane potential, microscopy, ROS, docking, and enzyme assay terms is reconciled in the mechanism limitations."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T09:16:20.175589Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T090559867438Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/extracted/pdf_text.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/extracted/supplementary_text.jsonl"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-5",
    "paper_id": "PMC11845615",
    "reason": "Layer-3 mechanism ontology overstates evidence strength. The final mechanism claim PMC11845615-W5-MECH-001 classifies ribosome binding and SPR binding as direct_mechanism, but the cited source locators do not contain those assays: xml:p:18 describes a ribosome binding site upstream of llcA, and xml:p:54 is only the publisher note. The paper-local evidence supports antimicrobial phenotype, purification/mass/cyclization, stability/protease resistance, and inferred gene/immunity context, not a direct molecular target-binding assay for leucocyclicin C.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Remove or reclassify the ribosome-binding/SPR direct_mechanism claim unless a primary-source assay locator is found.",
      "Rebuild mechanism claims so MIC/Table 1 evidence is phenotype_supported, circularity/protease/pH/temperature stability is not promoted to direct antibacterial mechanism, and gene-cluster/immunity/ABC-transporter statements remain inferred_mechanism with limitations.",
      "Audit every mechanism source_locator to confirm it contains the claimed assay text, not merely background, figure captions, RBS terminology, or publisher/reference text."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:18",
      "xml:p:54",
      "xml:sec:2",
      "xml:p:30",
      "xml:p:35",
      "xml:p:38",
      "xml:p:40",
      "pdf:page=2",
      "pdf:page=10",
      "pdf:page=14"
    ],
    "target_queue": "mechanism",
    "ticket_id": "rwk-PMC11845615-campaign-r01-PMC11845615-BLOCKER-W5-MECHANISM-DIRECT-CLAIM-UNSUPPORTED"
  },
  {
    "acceptance_checks": [
      "A recursive source-locator scan over worker-4 work, packet analysis, paper final, and packet final database artifacts returns zero project paths in source_locator/source_locators.",
      "PMC11845615_strict_acceptance_audit_latest.json reports strict_worker_run_hard_finding_count 0 for recursive_non_source_locator_reference after rerun.",
      "Paper and packet final database_record_verification.json are byte-identical after repair.",
      "Database final still reports authoritative_dbaasp_ingest_ready false and fallback rows are not promoted."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T10:25:06.902125Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T101517605842Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11845615_strict_acceptance_audit_latest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/work/database_record_audit/record_identity_audit.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/analysis/database_record_audit.worker4.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/authoritative_match_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/linked_sequence_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/linked_assay_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/dbaasp_machine_extracted_rows.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.xml"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC11845615",
    "reason": "Current strict acceptance evidence contains 12 hard recursive_non_source_locator_reference findings in worker-4 database artifacts and their paper/packet final mirrors. Independent inspection confirmed $/cross_database_conflicts[0]/source_locators contains packets/PMC11845615/database/authoritative_match_report.json, linked_sequence_records.jsonl, and linked_assay_records.jsonl. Those are project artifact paths, not primary-source or allowed database-row source locators. The source-reviewed leucocyclicin C identity is supported by the paper XML/PDF, and zero linked authoritative DBAASP rows must remain database-provenance/caution evidence, not source_locator evidence.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Move packet/report file paths out of source_locator/source_locators fields into checked_inputs, evidence_paths, or provenance fields.",
      "Represent zero linked authoritative DBAASP rows as unresolved/caution database state without using packet artifacts as source locators.",
      "Regenerate worker-4 work, packet analysis, paper final, and packet final database artifacts from the repaired record.",
      "Keep authoritative_dbaasp_ingest_ready false and do not promote fallback rows to RC2, portal, or authoritative ingest unless real linked authoritative rows are added and source-reviewed."
    ],
    "severity": "blocking",
    "source_locators": [
      "strict_worker_run_gate.findings[0..11]",
      "$/cross_database_conflicts[0]/source_locators",
      "xml:abstract:1",
      "xml:p:18",
      "xml:p:40",
      "xml:fig:3",
      "xml:table-wrap:4",
      "pdf:page=1",
      "pdf:page=4",
      "pdf:page=5",
      "pdf:page=10",
      "database:dbaasp_machine_extracted_rows.jsonl:rows=1-5"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC11845615-campaign-r02-BF-PMC11845615-W4-001-recursive-database-source-locators"
  },
  {
    "acceptance_checks": [
      "No mechanism or review source_locator/source_locators value starts with worker, xml_sections, pdf_text, pipeline_v2, papers, packets, or work.",
      "Mechanism evidence_class_counts keep direct_mechanism at 0 and preserve phenotype_supported, inferred_mechanism, and unknown_or_not_tested with primary-source locators.",
      "Live packet open_rework_ticket_count equals all final mechanism/review ticket diagnostics.",
      "Paper and packet final mechanism mirrors remain byte-identical after repair."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T10:25:06.906366Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T101517605842Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/review_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/review_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/work/mechanism_ontology/mechanism_source_surface_scan.worker5.repair.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/analysis/analysis_status.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/packet_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/rework/rework_requests.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/rework/rework_responses.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/supplementary/41598_2025_89450_MOESM1_ESM.docx"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-5",
    "paper_id": "PMC11845615",
    "reason": "Final mechanism artifacts and mirrors preserve non-primary source locators: worker5_scan:mechanism_source_surface_scan.worker5.repair.json appears in excluded_or_nonpromoted_evidence[2].source_locator and mechanism_claims[2].source_locator, and the final review caution cites the same worker artifact. mechanism_claims[2].source_locator also uses aggregate extraction locators xml_sections:all=160 and pdf_text:pages=1-14 without exact primary-source coordinates. The mechanism final validation block also records packet_open_rework_ticket_count 3 and analysis_needs_analysis_rework 1 while the live packet state and final review have zero open rework targets. This keeps the mechanism/review final scientifically non-source-reviewable despite correct non-direct evidence classes.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Remove worker5_scan, xml_sections:all, and pdf_text aggregate values from source_locator/source_locators fields; move scan artifacts to checked_inputs or audit_provenance only.",
      "For unknown_or_not_tested and excluded/nonpromoted mechanism evidence, cite concrete XML/PDF/supplement locators or explicitly encode the exhaustive-surface scan outside source_locator fields.",
      "Refresh mechanism validation/ticket diagnostics so live packet open_rework_ticket_count, analysis_status, packet_manifest, and final review counts agree.",
      "Mirror the repaired mechanism record to paper final, packet final mechanism_ontology_record.json, and packet final mechanism_evidence.json."
    ],
    "severity": "blocking",
    "source_locators": [
      "$/mechanism_claims[2]/source_locator",
      "$/excluded_or_nonpromoted_evidence[2]/source_locator",
      "$/caution_findings[2]/source_locators",
      "$/validation/strict_gate_diagnostics/packet_open_rework_ticket_count",
      "xml:p:15",
      "xml:p:16",
      "xml:p:20",
      "xml:p:23",
      "xml:p:24",
      "xml:p:35",
      "xml:p:38",
      "xml:p:40",
      "xml:table-wrap:4",
      "xml:fig:7",
      "pdf:page=8",
      "pdf:page=9",
      "pdf:page=10",
      "pdf:page=12",
      "supp:41598_2025_89450_MOESM1_ESM.docx"
    ],
    "target_queue": "mechanism",
    "ticket_id": "rwk-PMC11845615-campaign-r02-BF-PMC11845615-W5-001-mechanism-non-source-and-stale-ticket-"
  },
  {
    "acceptance_checks": [
      "A recursive JSON scan over paper and packet final activity_toxicity_evidence.json returns zero occurrences of 'Lactococcus lactis APC 3969' and every Table 1 activity record with xml:table-wrap:1:row=3-28 has producer fields equal to 'Leuconostoc lactis APC 3969'.",
      "A Table 1 parser over paper.xml still yields 26 accounted body observations with 16 inhibitory symbols, 5 growth-reduction symbols, and 5 no-activity observations, and the final activity records map exactly to source rows 3-28 with no missing or duplicated row coordinates.",
      "The purified MIC record still has endpoint MIC, raw_value 3.288, raw_unit µM, target_species Clostridium perfringens, target_strain_or_isolate EM124, and source locators including xml:p:30 and xml:sec:9.",
      "A recursive scan finds no activity object whose sequence field contains a non-AA placeholder string; any object containing both sequence and sequence_length has len(sequence) exactly equal to sequence_length.",
      "Paper and packet final activity_toxicity_evidence.json are byte-identical after repair."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T11:09:25.601370Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T105904745553Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.pdf",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/work/activity_evidence/activity_records.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/database_record_verification.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC11845615",
    "reason": "Layer-2 activity evidence is not publication-grade because the final activity records conflate producer identity. The primary source identifies the bacteriocin-producing strain as Leuconostoc lactis APC 3969, while all 26 Table 1 activity records use Lactococcus lactis APC 3969 in assayed_entity, treatment, and assay_conditions producer fields. Lactococcus lactis HP/ATCC 11454 are indicator targets in Table 1, not the producer APC 3969. The purified MIC record also keeps assayed_entity.sequence as the placeholder string 'not reported' even though the current database final source-reviews the mature 61-residue leucocyclicin C sequence. These are unsupported field values in current final mirrors.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Rebuild the worker-2 activity artifact and both final mirrors so Table 1 assayed_entity, treatment, and assay_conditions producer fields identify Leuconostoc lactis APC 3969, while Lactococcus lactis HP and Lactococcus lactis ATCC 11454 remain only target/indicator organisms where sourced by Table 1.",
      "Remove the non-AA placeholder sequence value from the MIC activity record or replace it with a source-reviewed sequence representation that includes the 61-residue mature sequence and exact sequence_length; do not leave a string such as 'not reported' in a field named sequence.",
      "Rerun the activity/table contract and final mirror checks after repair without changing the accepted Table 1 row count, qualitative symbol counts, or the 3.288 µM MIC row."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:article-title:1",
      "xml:abstract:1",
      "xml:p:5",
      "xml:p:6",
      "xml:table-wrap:1:row=19",
      "xml:table-wrap:1:row=20",
      "xml:p:30",
      "xml:p:43",
      "xml:p:44",
      "xml:p:18",
      "xml:p:40",
      "pdf:page=1",
      "pdf:page=2",
      "pdf:page=3",
      "pdf:page=10",
      "pdf:page=5:fig=3A"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC11845615-campaign-r03-PMC11845615-BF-W2-ENTITY-PRODUCER-GENUS-AND-SEQUENCE-PLACEHO"
  },
  {
    "acceptance_checks": [
      "A script over final/activity_toxicity_evidence.json finds the MIC record for C. perfringens EM124 includes source locators xml:p:17 and xml:p:36 and does not cite xml:p:30 as a MIC method locator.",
      "The MIC record assay_conditions contain non-empty source-reported inoculum, duration, temperature, atmosphere, assay format, OD600 readout, dilution/starting-concentration context, and replicate count or explicit field-level no-source rationale.",
      "No MIC-like row has raw_unit missing, machine-only source_locator support, or assay conditions copied solely from dbaasp_machine_extracted_rows.jsonl."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T13:15:51.155244Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T130551722550Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/extracted/xml_sections.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC11845615",
    "reason": "The final purified leucocyclicin C MIC row is not publication-grade source-reviewable at field level. The source result says purified leucocyclicin C MIC against C. perfringens EM124 is 3.288 µM, and the MIC method reports approximately 1 x 10^5 CFU/ml, 96-well microtiter assay, OD600 hourly for 23 h, 37 C, anaerobic environment, two-fold dilution from 13.155 µM, and triplicate. The final row instead leaves inoculum as 'None', omits those source-reported assay conditions, and uses xml:p:30/xml:sec:9 as method locators; xml:p:30 is the CFSN well-diffusion assay for Clostridium indicators, not the purified peptide MIC microtiter assay.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Rebuild the purified leucocyclicin C MIC row from source paragraphs for both result and method rather than from fallback candidate fields.",
      "Replace or supplement the row locator set with exact result and method locators, including xml:p:17 and xml:p:36, and remove xml:p:30/xml:sec:9 as MIC method support unless clearly marked as non-MIC contextual WDA evidence.",
      "Populate source-reported MIC assay conditions: inoculum approximately 1 x 10^5 CFU/ml, 96-well microtiter format, OD600 measurement, 23-hour duration, 37 C, anaerobic environment, serial dilution context, and triplicate; preserve CRM/RCM wording with a source note rather than silently normalizing."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:17",
      "xml:p:30",
      "xml:p:36",
      "final/activity_toxicity_evidence.json activity_records[26].assay_conditions",
      "final/activity_toxicity_evidence.json activity_records[26].source_locator"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC11845615-campaign-r01-BF-PMC11845615-W2-MIC-CONDITIONS-LOCATORS"
  },
  {
    "acceptance_checks": [
      "No JSON under packets/PMC11845615/final contains artifact_role/status text indicating pending_worker6_readjudication, targeted_rework_needed, publication_grade_claim=false, or unresolved_blockers when review_report is accepted.",
      "The set of authoritative final mechanism artifacts is identical between papers/PMC11845615/final and packets/PMC11845615/final, or any packet-only diagnostic file is moved out of final and excluded by the acceptance manifest.",
      "Byte-hash comparison for all terminal final mirror pairs passes and the strict acceptance audit lists no packet-only nonterminal final records."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T13:15:51.159794Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T130551722550Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/analysis/mechanism_evidence.worker5.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/review_report.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-5",
    "paper_id": "PMC11845615",
    "reason": "A current packet final record remains nonterminal even though review_report claims terminal accepted_with_cautions. packets/PMC11845615/final/mechanism_evidence.json has artifact_role 'final_mechanism_ontology_record_pending_worker6_readjudication' and publication_grade_claim=false, is not mirrored in papers/PMC11845615/final, and is byte-unequal to packets/PMC11845615/analysis/mechanism_evidence.worker5.json. A publication-grade final surface cannot simultaneously contain a pending-worker6 mechanism final record.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Reconcile the mechanism final surfaces so there is one terminal mechanism ontology final contract across paper final and packet final mirrors.",
      "Either remove the non-authoritative pending mechanism_evidence.json from packet final scope or rebuild it into a terminal worker-6-adjudicated mirror whose publication_grade/status fields agree with review_report and mechanism_ontology_record.",
      "Re-run mirror equality checks over all current paper final and packet final JSON records after the repair."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:table-wrap:1",
      "xml:p:15",
      "xml:p:16",
      "xml:p:18",
      "xml:p:35",
      "xml:p:38",
      "xml:p:40",
      "xml:table-wrap:4",
      "xml:fig:7",
      "supp:41598_2025_89450_MOESM1_ESM.docx",
      "packet/final/mechanism_evidence.json $.artifact_role",
      "packet/final/mechanism_evidence.json $.publication_grade_claim"
    ],
    "target_queue": "mechanism",
    "ticket_id": "rwk-PMC11845615-campaign-r01-BF-PMC11845615-W5-CURRENT-FINAL-MECHANISM-MIRROR-NONTERMINAL"
  },
  {
    "acceptance_checks": [
      "papers/PMC11845615/final/materials_manifest.json, packet_manifest.json, analysis/analysis_status.json, and the strict acceptance audit all agree on analysis_queue_status/status and open_rework_ticket_count.",
      "If materials_manifest.json is a final record, a packet-final mirror exists and byte-hash equality passes; otherwise the acceptance manifest explicitly excludes it from final mirror requirements.",
      "A live ticket-state script over rework_requests.jsonl and rework_responses.jsonl computes open_rework_ticket_count=0 and matches final review_report and strict acceptance audit."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T13:15:51.164753Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T130551722550Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/materials_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/packet_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/analysis/analysis_status.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11845615_strict_acceptance_audit_latest.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-1",
    "paper_id": "PMC11845615",
    "reason": "The current paper final materials_manifest is stale relative to live packet state. papers/PMC11845615/final/materials_manifest.json has analysis_queue_status='analysis_queued' and no packet-final materials_manifest mirror, while packets/PMC11845615/analysis/analysis_status.json and the strict acceptance audit report analysis_source_reviewed_accepted with open_rework_ticket_count=0. This violates current final-record/mirror/status consistency even though the material files themselves are readable.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Regenerate or replace the final materials manifest from the live packet manifest and analysis_status state after terminal adjudication.",
      "Mirror the terminal materials manifest into the packet final area if it remains a current final record, or remove it from authoritative final scope consistently.",
      "Ensure final review_report open_rework_ticket_count/status fields agree with live packet rework_requests/rework_responses and analysis_status."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:article-meta",
      "xml:supplementary-material:MOESM1",
      "supp:41598_2025_89450_MOESM1_ESM.docx",
      "final/materials_manifest.json $.analysis_queue_status",
      "analysis/analysis_status.json $.status",
      "strict_acceptance_audit_latest.json $.status.open_rework_ticket_count"
    ],
    "target_queue": "paper",
    "ticket_id": "rwk-PMC11845615-campaign-r01-BF-PMC11845615-W1-MATERIALS-MANIFEST-MIRROR-STATUS-STALE"
  },
  {
    "acceptance_checks": [
      "A script parsing paper.xml verifies that every final record citing xml:table-wrap:2 has target_species Lactococcus lactis and target_strain_or_isolate HP, with treatments and R/S values matching rows 2-17 exactly.",
      "A script verifies the Fig. 6/fraction-51 WDA record cites xml:p:28 or xml:p:49 and has target_species Listeria innocua and target_strain_or_isolate DPC 3572, or is absent from accepted activity_records with a source-backed exclusion.",
      "A recursive scan of final activity_toxicity_evidence.json in both mirrors finds no accepted source_locator object whose source_group/support contains ticket_required_unresolved_locator, unsupported, or not supported.",
      "Paper and packet final activity_toxicity_evidence.json are byte-identical after repair; strict acceptance audit and final review_report no longer claim publication_grade=true until the repaired source comparison passes."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-28T00:08:19.465884Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T235904348291Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/analysis/activity_toxicity_evidence.worker2.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/work/activity_evidence/activity_records.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.pdf",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/extracted/xml_sections.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/extracted/pdf_text.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11845615_strict_acceptance_audit_latest.json"
    ],
    "leader_finding_fingerprint": "927276fb6f03c030ccb3b01f5ab000f727885629653e36566d28d80ece346252",
    "leader_finding_id": "BF-PMC11845615-W2-ACTIVITY-TARGET-LOCATOR-CONFLICT",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC11845615",
    "reason": "Layer-2 final activity evidence contains source-contradicted assay target fields and unsupported locator scaffolds. Records activity_records[27-42] cite xml:p:9/xml:table-wrap:2 for treatment/stability outcomes but set target_species=Clostridium perfringens and target_strain_or_isolate=EM124; xml:p:9 and xml:p:46 state these assays used Lactococcus lactis HP as the indicator strain. Record activity_records[43] cites xml:p:28/xml:fig:6 for fraction-51 WDA activity but sets the same C. perfringens EM124 target; xml:p:28 and xml:p:49 state L. innocua DPC 3572 was used to follow activity during purification. The MIC record activity_records[26] keeps xml:p:17 and xml:p:36 in source_locator objects while those same objects say the locators do not support MIC value or method conditions. This is a material endpoint/target/provenance conflict, so publication-grade PASS is not valid even though the current strict acceptance artifact reports zero hard findings.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Rebuild the affected Layer-2 activity records from source: set all Table 2 treatment/stability rows to Lactococcus lactis HP as the indicator target, or explicitly move them to a non-targeted stability/producer-activity category if the schema cannot represent indicator-strain context.",
      "Correct the Fig. 6 fraction-51 WDA activity record to Listeria innocua DPC 3572 as the indicator target, or exclude it from row-level antimicrobial target evidence if retained only as purification tracking.",
      "Keep the purified leucocyclicin C MIC row for Clostridium perfringens EM124 with source-supported result/method locators only; remove or relocate xml:p:17 and xml:p:36 from accepted source_locator fields unless they are clearly marked outside source evidence/provenance.",
      "Regenerate paper and packet final activity mirrors, then rerun semantic/publication checks and worker-6 adjudication so review_report rework_targets/open ticket state reflects this repair."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:9",
      "xml:table-wrap:2:rows=2-17",
      "xml:p:28",
      "xml:p:46",
      "xml:p:49",
      "xml:p:50",
      "xml:fig:6",
      "xml:fig:7",
      "pdf:page=7",
      "pdf:page=12"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC11845615-campaign-r01-BF-PMC11845615-W2-ACTIVITY-TARGET-LOCATOR-CONFLICT"
  }
]

For every currently open rework ticket, independently verify the repaired owner-lane artifact against the ticket contract, rebuild the final and packet-final mirrors, and run the packet, semantic, and publication gates without allow flags. The Runtime-open ticket IDs assigned to worker-6 list is authoritative: if a ticket is listed there, any earlier closed/repaired response is an invalid or superseded candidate under the current runtime contract and you must append a new complete terminal response after verification; never skip a listed ticket merely because rework_responses.jsonl already contains a closed-looking string. An owner-lane ticket must already have a nonterminal, evidence-bearing, analysis_can_resume response from every named owner worker; adjudication-owned tickets are exempt from that owner-response prerequisite. Only when the ticket contract is fully satisfied, all three strict gates pass, review_status is accepted_clean or accepted_with_cautions, publication_grade is true, and no hard rework target remains, append exactly one new valid terminal adjudication response to rework_responses.jsonl. The runtime closure schema is mandatory: status and response_status must both be exactly closed_repaired; response_by must be worker-6; analysis_can_resume and publication_grade must be true; review_status must be accepted_clean or accepted_with_cautions; created_at and final_counts must be present; final_counts must exactly include activity_records, toxicity_records, database_record_audits, mechanism_claims, and review_rework_targets; ticket_contract_evidence.overall_contract_pass must be true; gate_return_codes must contain packet, semantic, and publication values all equal to 0; gate_artifact_paths must identify fresh post-response reports with the formal pass schema for those three strict gates and the correct single-paper manifest; and verified_artifact_paths must contain both paper and packet final paths for activity_toxicity_evidence, database_record_verification, review_report, and the aligned mechanism final. The paper/packet final mirror pairs must be byte-identical. The packet gate may initially report only the exact ticket IDs being closed; after appending all terminal responses, rerun all three gates so the same artifact paths are newer than the response and the packet report has zero unrelated open tickets. This adjudication response may close a repaired owner-lane ticket; it does not replace the owner's nonterminal repair response. If any owner response, contract item, source proof, final rebuild, mirror, manifest binding, count, or strict gate is incomplete, leave the ticket open and write a concrete rework target instead. Never append another terminal response only when the runtime-open list confirms that ticket is already closed.

Required outputs for this worker:

Write final adjudication outputs:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/work/review/adjudication_report.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/work/review/quality_feedback.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/database_record_verification.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/activity_toxicity_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/mechanism_ontology_record.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/review_report.json
Also copy/align final mechanism to:
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/mechanism_evidence.json
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
