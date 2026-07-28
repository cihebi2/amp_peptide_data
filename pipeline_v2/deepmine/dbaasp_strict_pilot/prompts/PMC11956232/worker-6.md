You are worker-6 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC11956232.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: ["/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/source_surface_preflight_contract_20260726.json"]
- Leader preflight evidence scaffolds: ["/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/figure_crop_manifest.json", "/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/figure_page_map.json", "/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/leader_color_digitized_figures1_2.json", "/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/rendered_page_manifest.json"]
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-6: ["rwk-PMC11956232-campaign-r01-BF-W2-SEQUENCE-LENGTH-STRICT-HARD-FINDINGS", "rwk-PMC11956232-layer2-figure-toxicity-integration-002", "rwk-PMC11956232-leader-verifier-sequence-length-20260727", "rwk-PMC11956232-quantitative-figure-exhaustion-001"]
- Runtime-open ticket contracts assigned to worker-6: [
  {
    "acceptance_checks": {
      "fabricated_numeric_fill_count": 0,
      "figure1_2_treatment_count": 640,
      "figure3_7_count": 157,
      "figure7_day7_plateaus": {
        "1xMIC": 80,
        "2xMIC": 70,
        "Control": 10,
        "PBS": 100
      },
      "figure_quantitative_observation_count": 797,
      "worker3_leader_validator_pass": true
    },
    "blocks": [
      "supplementary_evidence",
      "activity_toxicity_evidence",
      "review_report",
      "publication_grade_acceptance",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-26T15:43:37.952747Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_semantic_audit_20260726.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/validate_candidate19_terminal_contract.py",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_final_pre_rework_fail.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/source_surface_preflight_contract_20260726.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_worker3_pre_rework_fail.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/leader_color_digitized_figures1_2.json"
    ],
    "leader_contract_correction": {
      "corrected_at": "2026-07-26T16:04:00Z",
      "corrected_by": "leader",
      "field_corrections": {
        "figure3_7_count": {
          "from": 117,
          "to": 157
        },
        "figure_quantitative_observation_count": {
          "from": 757,
          "to": 797
        }
      },
      "reason": "Arithmetic correction: 360+280+20+98+18+17+4=797 and Figures 3-7 sum to 157; per-figure counts and immutable validator were already correct."
    },
    "owner_worker": "worker-3",
    "paper_id": "PMC11956232",
    "reason": "The accepted final omitted all 797 contract-required quantitative figure observations. Worker-3 acknowledged that it only verified a scaffold/hash and did not independently source-review or terminally digitize Figures 1-7.",
    "requested_by": "leader_field_level_semantic_audit",
    "required_actions": {
      "figure12_nulls": "Account for all 640 treatment observations. A source-resolved numeric value is preferred. If an individual curve point is occluded/overlapped and cannot be separately read, retain null only with a terminal_resolution_status accepted by the immutable leader validator, a concrete missing_reason, source review proof, and numeric_value_not_fabricated=true.",
      "figure3_7": "Digitize all 20 Figure-3 bars, all 98 Figure-4 heatmap cells, all 18 Figure-5 bars, all 17 Figure-6 bars, and the four exact plotted Figure-7 day-7 plateaus PBS=100%, Control=10%, 1xMIC=80%, 2xMIC=70%. Preserve calibration and uncertainty and the semantic evidence boundaries in the preflight contract.",
      "figure_counts": {
        "Figure 1": 360,
        "Figure 2": 280,
        "Figure 3": 20,
        "Figure 4": 98,
        "Figure 5": 18,
        "Figure 6": 17,
        "Figure 7": 4
      },
      "independent_source_review": "Independently inspect the packet XML/PDF plus all seven 300-dpi figure crops. The leader scaffold is candidate evidence only; verify every retained value against the source and do not copy it blindly.",
      "leader_validator": "Run python3 pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/validate_candidate19_terminal_contract.py --mode worker3 --output pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_worker3_post_rework.json; require exit code 0, passed=true, and zero blocking failures. Do not edit, replace, weaken, or bypass the leader-owned validator (expected pre-rework SHA-256 b7c17eb745b65f64d8834491a50e2a585e02b8570c666a318344e898b59e0a64).",
      "owner_response": "Append one nonterminal evidence-bearing repair_ready_for_adjudication response for this exact ticket only after the leader validator passes.",
      "standardized_output": "Write top-level figure_quantitative_observations and figure_surface_exhaustion into both work/supplementary_methods/supplementary_evidence.json and packet analysis/supplementary_evidence.worker3.json. Every observation needs a unique observation_id, Figure 1-7 surface, semantic group coordinates, raw_value/raw_unit, source_locator, source_reviewed=true or source_review_status, exact_vs_approximate_status, calibration/uncertainty where applicable, and source_reviewed_by=worker-3."
    },
    "severity": "blocking",
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC11956232-quantitative-figure-exhaustion-001"
  },
  {
    "acceptance_checks": {
      "authoritative_dbaasp_ingest_ready": false,
      "exact_table_activity_records": 40,
      "figure6_bar_count": 17,
      "figure6_numeric_peptide_toxicity_records_minimum": 14,
      "figure_quantitative_observation_count": 797,
      "source_conflict_ids": [
        "C1_temperature_method_table",
        "C2_serum_method_units",
        "C3_safety_threshold_wording",
        "C4_in_vivo_unassigned_range"
      ],
      "worker2_leader_validator_pass": true
    },
    "blocks": [
      "activity_toxicity_evidence",
      "review_report",
      "publication_grade_acceptance",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-26T15:43:37.952747Z",
    "depends_on_ticket_ids": [
      "rwk-PMC11956232-quantitative-figure-exhaustion-001"
    ],
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_semantic_audit_20260726.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/validate_candidate19_terminal_contract.py",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_final_pre_rework_fail.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/source_surface_preflight_contract_20260726.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_worker2_pre_rework_fail.json"
    ],
    "leader_contract_correction": {
      "corrected_at": "2026-07-26T16:04:00Z",
      "corrected_by": "leader",
      "field_corrections": {
        "figure_quantitative_observation_count": {
          "from": 757,
          "to": 797
        }
      },
      "reason": "Arithmetic correction aligned to the unchanged explicit per-figure counts and immutable validator."
    },
    "owner_worker": "worker-2",
    "paper_id": "PMC11956232",
    "reason": "Layer-2/final retained only the 40 exact table cells and 3 prose toxicity statements. It omitted the source-reviewed quantitative figure dataset, including all Figure-6 treatment bars and exact plotted Figure-7 endpoints.",
    "requested_by": "leader_field_level_semantic_audit",
    "required_actions": {
      "dependency": "Start only after the fresh worker-3 owner output and its leader worker3 validator report pass.",
      "exact_tables": "Preserve exactly 40 Table 1-3 activity records with 40 unique physical cell locators and the 40 exact leader_preflight_cell_locator values/raw values/units.",
      "figure_integration": "Independently source-check worker-3 evidence, then integrate exactly 797 rows into top-level figure_quantitative_observations and seven terminal figure_surface_exhaustion rows in both work/activity_evidence/activity_records.json and packet analysis/activity_toxicity_evidence.worker2.json.",
      "leader_validator": "Run python3 pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/validate_candidate19_terminal_contract.py --mode worker2 --output pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_worker2_post_rework.json; require exit code 0, passed=true, and zero blocking failures. Do not edit, replace, weaken, or bypass the leader-owned validator.",
      "owner_response": "Append one nonterminal evidence-bearing repair_ready_for_adjudication response for this exact ticket only after worker-2 leader validation passes.",
      "semantic_boundaries": "Keep Figure 3 membrane assays as direct mechanism-supporting quantitative evidence, Figure 4 as functional LPS-assay evidence with the binding limitation, Figure 5 as anti-inflammatory phenotype rather than direct antimicrobial mechanism, and Figure 7 as in-vivo efficacy. Preserve C1-C4 and recursive authority=false.",
      "toxicity_integration": "Create at least 14 numeric Figure-6 peptide-treatment toxicity_records (seven concentrations for HK-2 and seven for hemolysis), with approximate figure provenance/calibration/uncertainty. Preserve the three prose-supported toxicity records as separate source-hierarchy evidence; do not replace prose values with less authoritative digitized estimates."
    },
    "severity": "blocking",
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC11956232-layer2-figure-toxicity-integration-002"
  },
  {
    "ticket_id": "rwk-PMC11956232-leader-verifier-sequence-length-20260727",
    "paper_id": "PMC11956232",
    "created_at": "2026-07-26T17:05:08.574144Z",
    "requested_by": "leader_rejection_of_unsupported_PASS_plus_independent_verifier_FAIL",
    "target_queue": "analysis",
    "owner_worker": "worker-2",
    "severity": "blocking",
    "reason": "The source sequence RRWQWRPKRIVKLIKKWLR contains 19 residues; C-terminal amidation (-NH2) is a separate modification, but six current Layer-2/work/final mirrors declare sequence_length=20. The independent verifier rejected the leader PASS. In addition, final review_report.semantic_quality_checks.open_rework_ticket_count=2 conflicts with the live zero-open-ticket state and must be refreshed by the later adjudication merge.",
    "source_locators": [
      "xml:p:8",
      "xml:p:10",
      "pdf:page=2"
    ],
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/final/review_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11956232_strict_acceptance_audit_latest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11956232/20260726T165430943729Z.independent_paper_verifier.json"
    ],
    "required_actions": [
      "Worker-2 independently recount the source-supported one-letter sequence and set sequence_length=19 in its canonical activity evidence and every worker-2-owned derivative without changing the sequence or C-terminal amidation.",
      "Preserve all 40 activity rows, 17 toxicity rows, 797 figure observations, locators, units, exact/approximate semantics, conflicts, and recursive authority=false.",
      "Append an evidence-bearing repair_ready_for_adjudication owner response; do not self-close the ticket.",
      "A fresh later worker-6 must adjudicate the repair, synchronize paper/packet final mirrors, and refresh final review_report live open-ticket semantics before terminal closure."
    ],
    "acceptance_checks": [
      "The strict single-paper acceptance report has zero sequence_length_mismatch findings.",
      "Every plain sequence RRWQWRPKRIVKLIKKWLR paired with sequence_length declares 19; -NH2 remains represented only as a terminal modification/display suffix.",
      "The later fresh worker-6 final review report open_rework_ticket_count agrees with live packet ticket state at terminal closure.",
      "Paper/packet mirrors remain byte-identical and all scientific record counts and authority boundaries remain unchanged.",
      "Only a fresh worker-6 later than this owner response may close the ticket, followed by fresh structured leader and independent verifier PASS."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket."
  },
  {
    "acceptance_checks": [
      "Recursive JSON scan over the paper work, packet, final mirrors, worker log, and strict report finds zero objects where plain one-letter sequence RRWQWRPKRIVKLIKKWLR has sequence_length other than 19.",
      "reports/PMC11956232_strict_acceptance_audit_latest.json has strict_worker_run_gate.hard_finding_count=0 and no sequence_length_mismatch findings for PMC11956232.",
      "final/review_report.json semantic_quality_checks.open_rework_ticket_count still equals the live packet rework state after the sequence repair is re-adjudicated."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-26T17:36:07.662971Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11956232/20260726T172635416592Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11956232_strict_acceptance_audit_latest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/activity_evidence/preflight_non_table_surface_contract.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/source_surface_preflight_contract_20260726.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/source/paper.pdf"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC11956232",
    "reason": "The current strict acceptance artifact still has two hard sequence_length_mismatch findings. The primary source displays Lf-KR as RRWQWRPKRIVKLIKKWLR-NH2, so the plain one-letter sequence RRWQWRPKRIVKLIKKWLR independently counts to 19 residues; C-terminal amidation is a separate terminal modification. Two current work/preflight JSON surfaces still declare sequence_length=20 for that same plain sequence, so publication-grade PASS cannot be issued around the hard findings even though the final activity/database records now use length 19.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Repair or supersede the worker-2/preflight sequence-length evidence surfaces so every object pairing a plain one-letter sequence with sequence_length reports 19 for RRWQWRPKRIVKLIKKWLR.",
      "Preserve C-terminal amidation only in modification/display fields, not as an additional residue in sequence_length.",
      "Regenerate the strict acceptance audit after repair; do not mark publication-grade ready while strict_worker_run_gate.hard_finding_count remains nonzero."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:9",
      "pdf:page=2",
      "strict_acceptance_audit_latest.json:strict_worker_run_gate.findings[0]",
      "strict_acceptance_audit_latest.json:strict_worker_run_gate.findings[1]"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC11956232-campaign-r01-BF-W2-SEQUENCE-LENGTH-STRICT-HARD-FINDINGS"
  }
]

For every currently open rework ticket, independently verify the repaired owner-lane artifact against the ticket contract, rebuild the final and packet-final mirrors, and run the packet, semantic, and publication gates without allow flags. The Runtime-open ticket IDs assigned to worker-6 list is authoritative: if a ticket is listed there, any earlier closed/repaired response is an invalid or superseded candidate under the current runtime contract and you must append a new complete terminal response after verification; never skip a listed ticket merely because rework_responses.jsonl already contains a closed-looking string. An owner-lane ticket must already have a nonterminal, evidence-bearing, analysis_can_resume response from every named owner worker; adjudication-owned tickets are exempt from that owner-response prerequisite. Only when the ticket contract is fully satisfied, all three strict gates pass, review_status is accepted_clean or accepted_with_cautions, publication_grade is true, and no hard rework target remains, append exactly one new valid terminal adjudication response to rework_responses.jsonl. The runtime closure schema is mandatory: status and response_status must both be exactly closed_repaired; response_by must be worker-6; analysis_can_resume and publication_grade must be true; review_status must be accepted_clean or accepted_with_cautions; created_at and final_counts must be present; final_counts must exactly include activity_records, toxicity_records, database_record_audits, mechanism_claims, and review_rework_targets; ticket_contract_evidence.overall_contract_pass must be true; gate_return_codes must contain packet, semantic, and publication values all equal to 0; gate_artifact_paths must identify fresh post-response reports with the formal pass schema for those three strict gates and the correct single-paper manifest; and verified_artifact_paths must contain both paper and packet final paths for activity_toxicity_evidence, database_record_verification, review_report, and the aligned mechanism final. The paper/packet final mirror pairs must be byte-identical. The packet gate may initially report only the exact ticket IDs being closed; after appending all terminal responses, rerun all three gates so the same artifact paths are newer than the response and the packet report has zero unrelated open tickets. This adjudication response may close a repaired owner-lane ticket; it does not replace the owner's nonterminal repair response. If any owner response, contract item, source proof, final rebuild, mirror, manifest binding, count, or strict gate is incomplete, leave the ticket open and write a concrete rework target instead. Never append another terminal response only when the runtime-open list confirms that ticket is already closed.

Required outputs for this worker:

Write final adjudication outputs:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/adjudication_report.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/quality_feedback.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/final/database_record_verification.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/final/activity_toxicity_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/final/mechanism_ontology_record.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/final/review_report.json
Also copy/align final mechanism to:
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/final/mechanism_evidence.json
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
