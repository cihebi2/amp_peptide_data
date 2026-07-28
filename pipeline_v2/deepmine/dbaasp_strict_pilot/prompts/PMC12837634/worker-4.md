You are worker-4 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12837634.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12837634
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-4: ["rwk-PMC12837634-campaign-r01-BF-PMC12837634-worker4-database-final-unresolved-blocker-sta"]
- Runtime-open ticket contracts assigned to worker-4: [
  {
    "acceptance_checks": [
      "database_record_verification unresolved_blockers is empty or contains only explicitly nonblocking caution fields separated from blockers.",
      "review_report rework_targets, open_rework_ticket_count, database publication_grade, and targeted_rework_needed all agree with the live packet ticket state.",
      "All 42 fallback records remain unresolved/non-authoritative, candidate_sequence values remain null, source_verified count remains zero, and no object containing both plain sequence and sequence_length has a residue-count mismatch."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T20:12:49.038039Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12837634/20260727T195829615319Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12837634/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12837634/final/review_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/authoritative_match_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/dbaasp_machine_extracted_rows.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/linked_article_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/linked_assay_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/linked_sequence_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/database/linked_literature_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/extracted/xml_sections.json"
    ],
    "leader_finding_fingerprint": "8291470ea709ec1b66588f7c887e05bf9540bad547f3f959701cdd7565091fda",
    "leader_finding_id": "BF-PMC12837634-worker4-database-final-unresolved-blocker-state",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC12837634",
    "reason": "The database audit correctly excludes all 42 fallback rows from authoritative ingest, nulls placeholder-like candidate sequences, and records zero source_verified database records, but the accepted final database artifact still contains unresolved_blockers including final_artifact_requires_worker6_rebuild. That unresolved blocker state is inconsistent with publication_grade true, targeted_rework_needed false, final review_report zero rework targets, and live open ticket count zero.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Rebuild or adjudicate the database final state so unresolved hard blockers are not present in an accepted publication-grade final artifact.",
      "If authority and sequence absence are intended accepted limitations, move them to cautions/release-boundary fields and keep authoritative ingest disabled.",
      "If any unresolved_blockers remain, align review_report, rework_targets, targeted_rework_needed, and publication_grade flags with that blocking state."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:10",
      "xml:p:24",
      "pdf:page=3",
      "pdf:page=8",
      "database:authoritative_match_report row_counts linked_* zero"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC12837634-campaign-r01-BF-PMC12837634-worker4-database-final-unresolved-blocker-sta"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12837634/work/database_record_audit/record_identity_audit.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12837634/analysis/database_record_audit.worker4.json
Use only statuses: source_verified, source_conflict, database_only_no_primary_source, sequence_modified_not_normalized, unresolved_record. Preserve DBAASP machine rows as candidate/database provenance until source-reviewed.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
