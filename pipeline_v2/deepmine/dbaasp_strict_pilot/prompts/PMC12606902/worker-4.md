You are worker-4 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12606902.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12606902
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-4: ["rwk-PMC12606902-campaign-r03-BF-PMC12606902-W4-DATABASE-VALIDATION-SUMMARY-STALE"]
- Runtime-open ticket contracts assigned to worker-4: [
  {
    "acceptance_checks": [
      "A recursive JSON audit over both final mirrors counts every object containing both one-letter sequence and sequence_length and reports exact residue-count agreement, with terminal modifications excluded from residue counts.",
      "database_record_verification.json validation_summary counts match that recursive audit and do not report worker6 rebuild pending after the final mirror rebuild is complete.",
      "Live rework ticket state remains open=0 and any final open_rework_ticket_count field, if present, equals the live packet ticket state."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T20:10:29.389908Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12606902/20260727T195702941726Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12606902/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/rework/rework_requests.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/rework/rework_responses.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/rework/closure_receipts.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/analysis/analysis_status.json"
    ],
    "leader_finding_fingerprint": "60cce7670f6ce693f6cd5b76d3628efb821692320d8a9e89987a6dcd68929784",
    "leader_finding_id": "BF-PMC12606902-W4-DATABASE-VALIDATION-SUMMARY-STALE",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC12606902",
    "reason": "The database final preserves fallback rows as unresolved, which is scientifically correct, but its current validation_summary still asserts final_mirror_sequence_length_issue_count=12, final_mirror_sequence_placeholder_issue_count=12, worker6_rebuild_required_for_final_mirrors=true, and an unresolved worker6_final_mirror_rebuild_pending blocker. The independent recursive review found zero current final objects containing both sequence and sequence_length, so these final database metadata fields are stale and inconsistent with the live packet state.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Recompute worker-4 database validation_summary against the current final files after mirror rebuild, rather than carrying historical final-mirror issue counts.",
      "Keep the daptomycin DBAASP fallback rows unresolved/candidate-only unless authoritative linked sequence and modification evidence are source-located.",
      "Remove or resolve stale unresolved_blockers that no longer reflect the live rework/closure state."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:table-wrap:1",
      "database:dbaasp_machine_extracted_rows:rows=1-2",
      "final database_record_verification.json:validation_summary",
      "final database_record_verification.json:unresolved_blockers"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC12606902-campaign-r03-BF-PMC12606902-W4-DATABASE-VALIDATION-SUMMARY-STALE"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12606902/work/database_record_audit/record_identity_audit.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/analysis/database_record_audit.worker4.json
Use only statuses: source_verified, source_conflict, database_only_no_primary_source, sequence_modified_not_normalized, unresolved_record. Preserve DBAASP machine rows as candidate/database provenance until source-reviewed.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
