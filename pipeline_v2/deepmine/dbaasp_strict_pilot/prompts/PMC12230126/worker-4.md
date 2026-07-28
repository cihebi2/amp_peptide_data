You are worker-4 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12230126.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: ["/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/leader_preflight/source_surface_preflight_contract.json"]
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-4: ["rwk-PMC12230126-recursive-authority-boundary-007"]
- Runtime-open ticket contracts assigned to worker-4: [
  {
    "ticket_id": "rwk-PMC12230126-recursive-authority-boundary-007",
    "paper_id": "PMC12230126",
    "created_at": "2026-07-26T13:17:43.548036Z",
    "requested_by": "independent_verifier_followup_leader",
    "target_queue": "analysis",
    "owner_worker": "worker-4",
    "severity": "blocking",
    "reason": "Four nested authority-ready true values contradict zero linked authoritative DBAASP rows and the project-wide false authority boundary.",
    "blocks": [
      "database_record_audit",
      "review_report",
      "18paper_freeze",
      "publication_grade_acceptance"
    ],
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/global_freeze_20260726_18paper/independent_verifier_report.md",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/review/leader_recursive_authority_rework_contract_20260726.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/review/validate_recursive_authority_boundary.py",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/database_record_audit/record_identity_audit.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/analysis/database_record_audit.worker4.json"
    ],
    "required_actions": [
      {
        "finding_id": "F8_RECURSIVE_AUTHORITY_TRUE_IN_CURRENT_WORKER4_ARTIFACTS",
        "observed_true_count": 4,
        "affected_artifacts": [
          "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/database_record_audit/record_identity_audit.json",
          "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/analysis/database_record_audit.worker4.json"
        ],
        "required_repair": "Set every recursive authoritative_dbaasp_ingest_ready boolean to false in both current worker-4 artifacts, preserve zero linked authoritative rows and fallback candidate-only status, then rebuild finals under a fresh worker-6 adjudication."
      }
    ],
    "acceptance_checks": {
      "worker4_recursive_authority_true_count": 0,
      "final_recursive_authority_true_count": 0,
      "linked_authoritative_row_total": 0,
      "fallback_rows_promoted_to_authoritative_ingest": false,
      "worker4_paper_packet_artifacts_byte_identical": true,
      "paper_packet_final_mirrors_byte_identical": true,
      "fresh_worker4_gpt55_xhigh_rc0_codex_exec": true,
      "fresh_worker6_after_latest_worker4": true,
      "leader_validator_pass": true,
      "strict_worker_run_gate_hard_finding_count": 0,
      "strict_gates_all_zero_after_terminal_closure": true,
      "authoritative_dbaasp_ingest_ready": false
    },
    "leader_machine_readable_contract": "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/review/leader_recursive_authority_rework_contract_20260726.json",
    "leader_acceptance_validator": "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/review/validate_recursive_authority_boundary.py"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12230126/work/database_record_audit/record_identity_audit.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12230126/analysis/database_record_audit.worker4.json
Use only statuses: source_verified, source_conflict, database_only_no_primary_source, sequence_modified_not_normalized, unresolved_record. Preserve DBAASP machine rows as candidate/database provenance until source-reviewed.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
