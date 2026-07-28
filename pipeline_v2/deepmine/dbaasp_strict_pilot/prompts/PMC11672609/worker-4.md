You are worker-4 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC11672609.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11672609
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-4: ["rwk-PMC11672609-campaign-r02-BF-PMC11672609-W4-DB-CANDIDATE-LOCATOR-DOUBLE-PREFIX"]
- Runtime-open ticket contracts assigned to worker-4: [
  {
    "acceptance_checks": [
      "A recursive Python check over both final database mirrors reports malformed_candidate_locator_count == 0 for prefixes xml:xml:, pdf:pdf:, and supp:supp:.",
      "Every locator under record_audits[].source_review.candidate_name_locator_ids and candidate_sequence_locator_ids resolves to locator_index.json, xml_sections.json, pdf_text.jsonl, or a declared database locator.",
      "database_record_verification.json status_summary remains source_verified=0 and unresolved_record=13, and authoritative_dbaasp_ingest_ready remains false.",
      "Paper-final and packet-final database_record_verification.json remain byte-identical after the repair."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T23:24:30.456053Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11672609/20260727T231530730523Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11672609/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/locators/locator_index.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/extracted/xml_sections.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/extracted/pdf_text.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11672609/source/paper.xml"
    ],
    "leader_finding_fingerprint": "f45e03024912ae21020f074d287848ea485af000027dfce4b9f85d32bd3643aa",
    "leader_finding_id": "BF-PMC11672609-W4-DB-CANDIDATE-LOCATOR-DOUBLE-PREFIX",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC11672609",
    "reason": "The current paper and packet final database_record_verification.json records contain 117 non-resolving candidate locator values under record_audits[0..12].source_review.candidate_name_locator_ids and candidate_sequence_locator_ids. Examples include xml:xml:article-title:1, xml:xml:abstract:1, xml:xml:p:3, xml:xml:sec:4, xml:xml:sec:5, xml:xml:table-wrap:1, and pdf:pdf:page=3, while the source surfaces resolve at xml:article-title:1, xml:abstract:1, xml:p:3, xml:sec:4, xml:sec:5, xml:table-wrap:1, and pdf:page=3. Because those objects also assert candidate_name_locator_match=true and candidate_sequence_locator_match=true, the database identity artifact is not field-level source-reviewable even though the fallback rows remain correctly unresolved and excluded from authoritative ingest.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Normalize or remove the redundant malformed candidate_name_locator_ids and candidate_sequence_locator_ids in the worker-4 database artifact and both final mirrors; use canonical packet locators, not double-prefixed strings.",
      "Preserve all 13 DBAASP fallback candidate rows as unresolved_record and keep authoritative_dbaasp_ingest_ready=false unless linked authoritative rows are added and source-reviewed.",
      "Re-run a resolver check against locator_index.json, xml_sections.json, and pdf_text.jsonl over record_audits[].source_review candidate locator arrays after repair."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:article-title:1",
      "xml:abstract:1",
      "xml:p:3",
      "xml:sec:4",
      "xml:sec:5",
      "xml:table-wrap:1",
      "pdf:page=3"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC11672609-campaign-r02-BF-PMC11672609-W4-DB-CANDIDATE-LOCATOR-DOUBLE-PREFIX"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11672609/work/database_record_audit/record_identity_audit.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/analysis/database_record_audit.worker4.json
Use only statuses: source_verified, source_conflict, database_only_no_primary_source, sequence_modified_not_normalized, unresolved_record. Preserve DBAASP machine rows as candidate/database provenance until source-reviewed.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
