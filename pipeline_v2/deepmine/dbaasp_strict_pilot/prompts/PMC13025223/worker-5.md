You are worker-5 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC13025223.
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
- Runtime-open ticket IDs assigned to worker-5: ["rwk-PMC13025223-campaign-r01-BF-002-recursive-mechanism-work-locator"]
- Runtime-open ticket contracts assigned to worker-5: [
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
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC13025223/work/mechanism_ontology/mechanism_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC13025223/analysis/mechanism_evidence.worker5.json
Every mechanism_claim must have claim_id, claim_text, entity_scope, evidence_class, source_locator, and direct_assay_types when direct.
Set review_model exactly to gpt-5.5 and reasoning_effort exactly to xhigh in both required artifacts; the independent run report is the runtime proof.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
