You are worker-6 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC13066039.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-6: ["rwk-PMC13066039-campaign-r01-worker2-incomplete-activity-toxicity-surface-and-bad-target-", "rwk-PMC13066039-campaign-r01-worker4-placeholder-database-candidates-not-publication-grad", "rwk-PMC13066039-campaign-r01-worker5-recursive-mechanism-locator-and-unsupported-direct-a", "rwk-PMC13066039-campaign-r02-BF-PMC13066039-W2-TOXICITY-COUNT-METADATA-DRIFT"]
- Runtime-open ticket contracts assigned to worker-6: [
  {
    "acceptance_checks": [
      "A deterministic source-vs-final coverage script over xml:p:32, xml:p:44, xml:p:45, xml:fig:8, pdf:page=8, pdf:page=11, and pdf:page=12 reports no missing source-reported quantitative activity/toxicity/selectivity surfaces or unreviewed explicit exclusions.",
      "No final toxicity/activity row has generic target_species when the cited source locator names a cell line or bacterial strain.",
      "Every MIC-like row has raw_value, raw_unit, treatment, target species, strain when reported, exact/approximate status, and a paper-local source_locator.",
      "Final worker-2 output and mirrors pass semantic checks without relying on fallback rows as primary evidence."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T09:04:40.149323Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC13066039/20260727T085618747469Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/work/activity_evidence/bounded_result_assay_paragraphs.worker2.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/work/activity_evidence/machine_candidate_source_verification.worker2.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/analysis/activity_safe_candidate_handoff.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/source/paper.pdf"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC13066039",
    "reason": "Final activity/toxicity evidence is not publication-grade source coverage. Source paragraph xml:p:32 and PDF page 8 report nisin no inhibition against E. coli across 0-533.3 µg/mL, nisin MIC 266.7 µg/mL against S. aureus, P-AgNPs MIC 533.3 µg/mL against both strains, and NP-AgNPs2 MIC 16.7/33.3 µg/mL against E. coli/S. aureus. The final keeps only the nisin S. aureus MIC. Source toxicity paragraphs xml:p:44-45 and PDF pages 11-12 report nisin NIH-3T3 viability range, NP-AgNPs2/P-AgNPs NIH-3T3 values 77.3/18.2% at 0.4 mg/mL, and HCT-116 values 62.6/83.2% at 0.2 mg/mL; the final omits these NP/P and HCT-116 records and adds a generic mammalian-cell nisin 95.2% row unsupported by the cited locator. The accepted S. aureus activity row also says strain_or_isolate not reported while target_species embeds strain 186335.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Rebuild activity_records and toxicity_records from paper-local XML/PDF locators, not from the three-row fallback scaffold alone.",
      "Emit row-level records or explicit source-backed exclusions for every source-reported MIC/no-inhibition, cytotoxicity, HCT-116 selectivity, and hemolysis surface listed in the cited locators.",
      "Normalize target species and strain into separate fields; do not embed strain in target_species while marking target_strain_or_isolate as not reported.",
      "Remove the unsupported generic mammalian-cell 95.2% duplicate or replace it with a source-supported NIH-3T3 row."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:13",
      "xml:p:14",
      "xml:p:32",
      "xml:p:44",
      "xml:p:45",
      "xml:fig:4",
      "xml:fig:8",
      "pdf:page=8",
      "pdf:page=11",
      "pdf:page=12"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC13066039-campaign-r01-worker2-incomplete-activity-toxicity-surface-and-bad-target-"
  },
  {
    "acceptance_checks": [
      "Every final database record has a stable authoritative database identifier or an explicit database_only_no_primary_source/unresolved status without placeholder sequence fields.",
      "For every object with sequence and sequence_length, a script counts one-letter residues and matches sequence_length exactly; terminal modifications are not counted as residues.",
      "No source_verified status is used without a primary-source sequence/name/modification locator.",
      "Authoritative linked row counts and final database record statuses agree, and fallback candidate rows remain excluded from release/portal ingest."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T09:04:40.153671Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC13066039/20260727T085618747469Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/dbaasp_machine_extracted_rows.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/authoritative_match_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/linked_article_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/linked_assay_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/linked_sequence_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/database/linked_literature_records.jsonl"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC13066039",
    "reason": "The final database record verification contains three unresolved DBAASP fallback machine candidates with no authoritative linked DBAASP/APD/DRAMP row IDs and no source-located one-letter sequence. Each record has candidate_sequence \"None\" and candidate_sequence_length 4, which is a placeholder/string length, not a residue count. Primary source locators identify nisin as a 34-amino-acid peptide and material reagent, but do not provide an exact one-letter sequence/modification record to validate these candidate database objects.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Resolve each fallback candidate against authoritative database rows, or keep it out of publication-grade final database records as candidate-only provenance.",
      "Replace candidate_sequence \"None\" and candidate_sequence_length 4 with a real source/database sequence plus exact residue count, or mark the record unresolved without placeholder sequence fields.",
      "Do not set publication_grade/source-reviewed acceptance for database records until identity, sequence/modification, source organism, citation linkage, and conflict status are source-reviewable.",
      "Preserve authoritative_ingest_ready false and fallback exclusion from RC2/portal/authoritative ingest until stable authoritative rows exist."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:8",
      "xml:p:10",
      "xml:p:32",
      "pdf:page=2",
      "pdf:page=3",
      "pdf:page=8"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC13066039-campaign-r01-worker4-placeholder-database-candidates-not-publication-grad"
  },
  {
    "acceptance_checks": [
      "strict_worker_run_gate.hard_finding_count is 0 for PMC13066039.",
      "No mechanism_claims[*].source_locator or supporting_source_locators entry begins with a project work/final path unless it is explicitly a non-authoritative checked input outside source locators.",
      "Direct mechanism claims list only direct assay types supported by their cited primary-source locators.",
      "Packet and paper final mechanism mirrors remain byte-identical after correction."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T09:04:40.158080Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC13066039/20260727T085618747469Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC13066039_strict_acceptance_audit_latest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/analysis/mechanism_evidence.worker5.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/final/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/work/mechanism_ontology/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/work/mechanism_ontology/mechanism_source_scan.worker5.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-5",
    "paper_id": "PMC13066039",
    "reason": "The current strict acceptance audit reports five hard recursive_non_source_locator_reference findings because mechanism_claims[4].supporting_source_locators includes a worker artifact path instead of a primary-source or packet locator in worker5 analysis, packet final mechanism_evidence, packet final mechanism_ontology_record, paper final mechanism_ontology_record, and work mechanism_evidence. Independently, mechanism_claims[0] lists TEM as a direct assay type, but the bacterial morphology method/result and Fig. 6 source locators describe SEM only.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Replace non-source worker artifact paths in mechanism_claims supporting_source_locators with primary XML/PDF, packet locator, or database locator entries only; move worker artifact references to checked_inputs or evidence_paths, not source_locators.",
      "Remove TEM from direct_assay_types unless a concrete source locator supports TEM for the bacterial morphology mechanism claim.",
      "Rerun the strict recursive-authority gate and regenerate all mirrored mechanism artifacts from the corrected source-locator set."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:15",
      "xml:p:37",
      "xml:fig:6",
      "xml:p:39",
      "xml:p:40",
      "xml:p:41",
      "xml:fig:7",
      "xml:sec:19",
      "strict_worker_run_gate.findings[0-4]"
    ],
    "target_queue": "mechanism",
    "ticket_id": "rwk-PMC13066039-campaign-r01-worker5-recursive-mechanism-locator-and-unsupported-direct-a"
  },
  {
    "acceptance_checks": [
      "A script asserts len(activity_toxicity_evidence.toxicity_records) == summary_counts.toxicity_records == quality_checks.toxicity_field_validation.record_count == review_report.final_counts.toxicity_records == 42 in both paper and packet finals.",
      "final_consistency.worker6_runtime.json expected_counts.toxicity_records is 42 after regeneration.",
      "check_two_queue_packets.py, semantic_three_layer_gate.py, and check_three_layer_publication_quality.py pass without --allow-findings, --allow-risk, or ignored return codes."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T16:33:22.672054Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC13066039/20260727T162345087901Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/work/review/final_consistency.worker6_runtime.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/work/activity_evidence/fig8bc_coverage_report.json"
    ],
    "leader_finding_fingerprint": "09529b46d95e1a410764bdc8ac371fcee2193b33eb8a7a73beaa4c444a5c82b5",
    "leader_finding_id": "BF-PMC13066039-W2-TOXICITY-COUNT-METADATA-DRIFT",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC13066039",
    "reason": "The current activity/toxicity final is not count-consistent: it contains 42 toxicity_records and reports summary_counts/review final_counts of 42, but quality_checks.toxicity_field_validation.record_count remains 11, and worker6 final_consistency.worker6_runtime.json also still expects 11 toxicity_records. This makes the final validation metadata stale for the Fig. 8 hemolysis/CCK-8 toxicity surface and fails the required counts-current condition.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Re-run worker-2 activity/toxicity field validation across all 42 current toxicity_records, including the 6 hemolysis rows and 36 Fig. 8b/c CCK-8 rows.",
      "Update activity_toxicity_evidence quality_checks so toxicity_field_validation.record_count equals the live toxicity_records length, or split the validation into explicitly named complete subcounts that sum to 42.",
      "Regenerate downstream final consistency/review evidence so expected toxicity_records is 42 before claiming publication-grade readiness."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:18",
      "xml:p:20",
      "xml:p:42",
      "xml:p:44",
      "xml:p:45",
      "xml:fig:8",
      "xml:caption:8",
      "pdf:page=12 Fig. 8a",
      "pdf:page=12 Fig. 8b",
      "pdf:page=12 Fig. 8c"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC13066039-campaign-r02-BF-PMC13066039-W2-TOXICITY-COUNT-METADATA-DRIFT"
  }
]

For every currently open rework ticket, independently verify the repaired owner-lane artifact against the ticket contract, rebuild the final and packet-final mirrors, and run the packet, semantic, and publication gates without allow flags. The Runtime-open ticket IDs assigned to worker-6 list is authoritative: if a ticket is listed there, any earlier closed/repaired response is an invalid or superseded candidate under the current runtime contract and you must append a new complete terminal response after verification; never skip a listed ticket merely because rework_responses.jsonl already contains a closed-looking string. An owner-lane ticket must already have a nonterminal, evidence-bearing, analysis_can_resume response from every named owner worker; adjudication-owned tickets are exempt from that owner-response prerequisite. Only when the ticket contract is fully satisfied, all three strict gates pass, review_status is accepted_clean or accepted_with_cautions, publication_grade is true, and no hard rework target remains, append exactly one new valid terminal adjudication response to rework_responses.jsonl. The runtime closure schema is mandatory: status and response_status must both be exactly closed_repaired; response_by must be worker-6; analysis_can_resume and publication_grade must be true; review_status must be accepted_clean or accepted_with_cautions; created_at and final_counts must be present; final_counts must exactly include activity_records, toxicity_records, database_record_audits, mechanism_claims, and review_rework_targets; ticket_contract_evidence.overall_contract_pass must be true; gate_return_codes must contain packet, semantic, and publication values all equal to 0; gate_artifact_paths must identify fresh post-response reports with the formal pass schema for those three strict gates and the correct single-paper manifest; and verified_artifact_paths must contain both paper and packet final paths for activity_toxicity_evidence, database_record_verification, review_report, and the aligned mechanism final. The paper/packet final mirror pairs must be byte-identical. The packet gate may initially report only the exact ticket IDs being closed; after appending all terminal responses, rerun all three gates so the same artifact paths are newer than the response and the packet report has zero unrelated open tickets. This adjudication response may close a repaired owner-lane ticket; it does not replace the owner's nonterminal repair response. If any owner response, contract item, source proof, final rebuild, mirror, manifest binding, count, or strict gate is incomplete, leave the ticket open and write a concrete rework target instead. Never append another terminal response only when the runtime-open list confirms that ticket is already closed.

Required outputs for this worker:

Write final adjudication outputs:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/work/review/adjudication_report.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/work/review/quality_feedback.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/final/database_record_verification.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/final/activity_toxicity_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/final/mechanism_ontology_record.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13066039/final/review_report.json
Also copy/align final mechanism to:
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13066039/final/mechanism_evidence.json
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
