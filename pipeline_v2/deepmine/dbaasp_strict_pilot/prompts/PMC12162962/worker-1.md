You are worker-1 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12162962.
- Read and obey your worker skill: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-intake-worker/SKILL.md
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
- Runtime-open ticket IDs assigned to worker-1: ["rwk-PMC12162962-campaign-r02-BF-PMC12162962-W1-FINAL-MATERIALS-MANIFEST-STALE"]
- Runtime-open ticket contracts assigned to worker-1: [
  {
    "acceptance_checks": [
      "materials_manifest.json $.analysis_queue_status equals packet_manifest.json $.analysis_queue_status and packets/PMC12162962/analysis/analysis_status.json $.status.",
      "No current final JSON contains stale strict_boundary text saying the paper is not source-reviewed after review_report claims publication_grade true.",
      "All same-name paper-final and packet-final JSON files are byte-identical, and any packet-only alias such as mechanism_evidence.json is declared or byte-identical to its canonical mechanism final."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-28T03:11:53.347962Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12162962/20260728T030111910078Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12162962/final/materials_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/final/materials_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/packet_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/analysis/analysis_status.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12162962/final/review_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12162962_strict_acceptance_audit_latest.json"
    ],
    "leader_finding_fingerprint": "800d169170216db5a7a63248549be0e489ccd1fc3ba4ff52b6778219e6278b72",
    "leader_finding_id": "BF-PMC12162962-W1-FINAL-MATERIALS-MANIFEST-STALE",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-1",
    "paper_id": "PMC12162962",
    "reason": "The current final materials_manifest is stale in both final mirrors. It reports analysis_queue_status=analysis_queued and strict_boundary='packet handoff only; not source-reviewed until workers 4-6 and strict gates pass', while packet_manifest and analysis_status report analysis_source_reviewed_accepted and review_report/strict acceptance report claim publication_grade true. This contradicts the current final state and prevents reviewed_every_current_final_record from being publication-grade ready.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Regenerate or reclassify final/materials_manifest.json so material and analysis statuses match current packet/review state, or remove it from the authoritative final record set with an explicit mirror policy.",
      "Update strict_boundary wording so current final records do not contradict source-reviewed acceptance state.",
      "Mirror the repaired material manifest to packet final and rerun final file-set/hash/count consistency checks."
    ],
    "severity": "blocking",
    "source_locators": [
      "materials_manifest.json $.analysis_queue_status",
      "materials_manifest.json $.strict_boundary",
      "packet_manifest.json $.analysis_queue_status",
      "analysis_status.json $.status",
      "review_report.json $.publication_grade",
      "reports/PMC12162962_strict_acceptance_audit_latest.json $.status.analysis_status",
      "xml:article-id[pub-id-type=pmcid]=PMC12162962",
      "xml:article-id[pub-id-type=doi]=10.3389/fmicb.2025.1569719"
    ],
    "target_queue": "paper",
    "ticket_id": "rwk-PMC12162962-campaign-r02-BF-PMC12162962-W1-FINAL-MATERIALS-MANIFEST-STALE"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write or update:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12162962/work/intake/source_inventory.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12162962/work/intake/intake_report.md
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12162962/analysis/analysis_status.json only if intake status changes
Do not make source_verified claims.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
