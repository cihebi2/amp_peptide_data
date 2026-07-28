You are worker-2 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC11845615.
- Read and obey your worker skill: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-body-table-worker/SKILL.md
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
- Runtime-open ticket IDs assigned to worker-2: ["rwk-PMC11845615-campaign-r01-BF-PMC11845615-W2-ACTIVITY-TARGET-LOCATOR-CONFLICT", "rwk-PMC11845615-campaign-r01-BF-PMC11845615-W2-MIC-CONDITIONS-LOCATORS", "rwk-PMC11845615-campaign-r01-PMC11845615-BLOCKER-W2-ACTIVITY-TABLE-COVERAGE", "rwk-PMC11845615-campaign-r03-PMC11845615-BF-W2-ENTITY-PRODUCER-GENUS-AND-SEQUENCE-PLACEHO"]
- Runtime-open ticket contracts assigned to worker-2: [
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

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/work/activity_evidence/activity_records.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/analysis/activity_toxicity_evidence.worker2.json
Rows must be source-located with endpoint, raw_value, raw_unit or no-unit rationale, target species/strain, assay conditions, evidence_ladder, and source_locator.
Every row must use normalization_status exactly as direct, converted, not_convertible, or ambiguous. Direct/converted rows require normalized_value and normalized_unit. Direct means no value or unit conversion: do not copy a stale normalized value, change the unit, or hide a conversion under direct; put any non-conversion or ambiguity reason in a dedicated normalization note/rationale.
Use the safe candidate handoff first:
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/analysis/activity_safe_candidate_handoff.json
Treat activity_table_locator_candidates as inspection hints only. Derive the endpoint, target, and unit from the cited table's own caption/header; table number or a machine label is never enough.
Do not emit activity rows from formulation/composition, FTIR/spectroscopy, TGA/thermal, contact-angle, tensile/mechanical, or reference columns.
Do not relabel a source unit to make a validator pass. If the source does not support an endpoint-specific unit, exclude or keep the candidate unresolved rather than inventing one.
Quantitative activity or toxicity evidence may be supported by an exact XML paragraph, figure/caption, or PDF-page locator. Lack of a source table is not a reason to discard it when treatment, endpoint, target, value, unit, and assay context are source-supported; emit the row or open a concrete ambiguity ticket instead of claiming no evidence.
Keep redundant record fields semantically identical: top-level concentration/concentration_unit must agree with any assay_conditions peptide/sample concentration copy. A stale nested scaffold value is a hard data conflict, not harmless metadata.
If a rework ticket asks about toxicity and all matched percentage surfaces are non-biological material measurements, write durable no-source-located-toxicity evidence in a nonterminal owner-repair response for your worker-2 ticket.
If a rework ticket declares expected_shape, expected_observation_counts, require_cell_locators, or expected_cell_observations, prove the full contract before marking your owner repair ready for worker-6 adjudication. Every expected_cell_observations locator must bind to that cell's named endpoint, value, unit, treatment, concentration/timepoint, and target fields; unique coordinates attached to the wrong existing rows are a hard failure. Do not satisfy a table ticket by attaching its base locator to unrelated existing rows, and do not mirror the same observation in both activity_records and toxicity_records.
Do not open raw paper XML/PDF, full xml_sections.json, full pdf_text.jsonl, or full table text in model context. If exact locator checking is needed, run a bounded local Python command that extracts only the requested locator IDs into a small JSON artifact under work/activity_evidence/, then read that small artifact. Terminal output must not contain source passages.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
