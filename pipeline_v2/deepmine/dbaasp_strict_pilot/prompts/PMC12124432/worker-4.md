You are worker-4 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12124432.
- Read and obey your worker skill: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-database-record-auditor/SKILL.md
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12124432
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-4: ["rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-002"]
- Runtime-open ticket contracts assigned to worker-4: [
  {
    "acceptance_checks": [
      "Recursive JSON scan over paper and packet database_record_verification finds no sequence field equal to 'None' and no sequence_length derived from placeholder text.",
      "Every object with a plain one-letter sequence and sequence_length has len(sequence)==sequence_length with terminal modifications excluded.",
      "summary_counts.source_verified_records remains 0 and authoritative_ingest_ready remains false unless linked_sequence_records/linked_literature_records are nonempty and source-verified."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T21:33:13.227897Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12124432/20260727T212323249023Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12124432/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12124432/work/database_record_audit/record_identity_audit.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/database/dbaasp_machine_extracted_rows.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/database/authoritative_match_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/extracted/supplementary_text.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12124432/source/supplementary/ANIE-64-e202501299-s002.pdf"
    ],
    "leader_finding_fingerprint": "a4eecd15f7d836e8bb07b5a3c9a633424d160e5a4d953041fa0e6b66d28f2205",
    "leader_finding_id": "PMC12124432-BLOCK-FIELD-002",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC12124432",
    "reason": "Database identity fields contain placeholder-like sequence values. The current final database record has candidate sequence='None', sequence_length=4, and sequence_length_check_passed=true for candidate records/groups, while the primary supplement contains modified sequence notation for PMB2 and the EB macrocycles. The release boundary is preserved because these fallback rows are not source_verified, but the final database JSON is not publication-grade field-clean.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Replace literal placeholder strings such as sequence='None' with JSON null plus explicit unresolved/database-candidate rationale, or separate them into a non-sequence raw fallback field.",
      "For source notations such as FA5-A3-Lys-Asn-Dab(*)-Lys-H2-Lys-C3-Lys-* preserve a modified_sequence_notation/source_notation field with Table S1/S2 locators instead of pretending it is a one-letter sequence.",
      "Set sequence_length_check_passed to false/not_applicable when no plain one-letter residue sequence exists; keep source_verified_records at 0 unless authoritative linked database rows are actually present."
    ],
    "severity": "blocking",
    "source_locators": [
      "supp:ANIE-64-e202501299-s002.pdf:page=16:Table S1",
      "supp:ANIE-64-e202501299-s002.pdf:page=18:Table S2",
      "$.record_audits[*].candidate_identity_fields.sequence",
      "$.record_audits[*].candidate_identity_fields.sequence_length",
      "$.candidate_identity_groups[*].candidate_sequence"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-002"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12124432/work/database_record_audit/record_identity_audit.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/analysis/database_record_audit.worker4.json
Use only statuses: source_verified, source_conflict, database_only_no_primary_source, sequence_modified_not_normalized, unresolved_record. Preserve DBAASP machine rows as candidate/database provenance until source-reviewed.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
