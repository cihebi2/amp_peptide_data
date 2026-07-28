You are worker-5 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12162962.
- Read and obey your worker skill: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-mechanism-ontology-worker/SKILL.md
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12162962
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-5: ["rwk-PMC12162962-campaign-r02-BF-PMC12162962-W5-MECHANISM-QPCR-AND-RECURSIVE-LOCATORS"]
- Runtime-open ticket contracts assigned to worker-5: [
  {
    "acceptance_checks": [
      "A recursive scan of keys containing locator in paper and packet mechanism_ontology_record.json and packet mechanism_evidence.json returns zero source/support locator values containing packet_analysis:, .json, .jsonl, work/, extracted/, papers/, packets/, or pipeline_v2/.",
      "A read-only query finds a qPCR/virulence-gene mechanism claim or explicit nonpromotion object with source_locators including xml:p:52 and xml:fig:9 or xml:caption:14.",
      "Mechanism mirrors are byte-identical for paper-final mechanism_ontology_record.json, packet-final mechanism_ontology_record.json, and packet-final mechanism_evidence.json after repair."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-28T03:11:53.343318Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12162962/20260728T030111910078Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12162962/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/extracted/xml_sections.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/extracted/figure_captions.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12162962/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/final/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/database/dbaasp_machine_extracted_rows.jsonl"
    ],
    "leader_finding_fingerprint": "166e5fc745adf3737f093ffb9a2a77e0d238f61ea9d341fff3e26fc4af250ad5",
    "leader_finding_id": "BF-PMC12162962-W5-MECHANISM-QPCR-AND-RECURSIVE-LOCATORS",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-5",
    "paper_id": "PMC12162962",
    "reason": "The mechanism final is not source-reviewable at publication grade. It omits the source-local qPCR/virulence-factor mechanism surface: xml:p:52 reports suppression of galF, ompW, and fiu expression, and Figure 9/caption 14 locates the qPCR result. The same final also contains recursive locator values: mechanism_claims[1] and [3] use packet_analysis:activity_toxicity_evidence.worker2.json as supporting_source_locators, and excluded_or_nonpromoted_evidence[5].source_locator uses database:dbaasp_machine_extracted_rows.jsonl.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Add a source-located qPCR/virulence-gene expression mechanism claim or explicit nonpromotion object with correct evidence class, entity scope, limitations, and source locators.",
      "Replace packet_analysis and .json/.jsonl locator values in source/support locator fields with concrete primary-source locators or row-level database provenance; move artifact paths to checked_inputs or reviewed_surfaces metadata.",
      "Preserve ontology boundaries among SEM direct morphology evidence, MIC/time-kill/biofilm phenotypes, CD/LPS biophysical evidence, qPCR gene-expression evidence, and database fallback rows."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:52",
      "xml:fig:9",
      "xml:caption:14",
      "mechanism_ontology_record.json $.mechanism_claims[1].supporting_source_locators[3]",
      "mechanism_ontology_record.json $.mechanism_claims[3].supporting_source_locators[3]",
      "mechanism_ontology_record.json $.excluded_or_nonpromoted_evidence[5].source_locator[0]"
    ],
    "target_queue": "mechanism",
    "ticket_id": "rwk-PMC12162962-campaign-r02-BF-PMC12162962-W5-MECHANISM-QPCR-AND-RECURSIVE-LOCATORS"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12162962/work/mechanism_ontology/mechanism_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/analysis/mechanism_evidence.worker5.json
Every mechanism_claim must have claim_id, claim_text, entity_scope, evidence_class, source_locator, and direct_assay_types when direct.
Set review_model exactly to gpt-5.5 and reasoning_effort exactly to xhigh in both required artifacts; the independent run report is the runtime proof.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
