You are worker-4 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC11845615.
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
- Runtime-open ticket IDs assigned to worker-4: ["rwk-PMC11845615-campaign-r01-PMC11845615-BLOCKER-W4-DATABASE-SEQUENCE-PLACEHOLDER", "rwk-PMC11845615-campaign-r02-BF-PMC11845615-W4-001-recursive-database-source-locators"]
- Runtime-open ticket contracts assigned to worker-4: [
  {
    "acceptance_checks": [
      "Recursive scan finds no sequence or candidate_sequence value equal to 'None' with a sequence_length field.",
      "For every object containing a plain one-letter sequence and sequence_length, residue count exactly equals sequence_length; cyclization is represented as a modification, not a residue.",
      "linked_article_records, linked_assay_records, linked_sequence_records, and linked_literature_records remain zero unless actual authoritative rows are present, and authoritative_dbaasp_ingest_ready remains false recursively.",
      "database_record_verification.json top-level review_model is gpt-5.5 and reasoning_effort is xhigh, with source_reviewed=true."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T09:16:20.170988Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T090559867438Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/dbaasp_machine_extracted_rows.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/authoritative_match_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.xml"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC11845615",
    "reason": "Layer-1 database verification is not source-reviewable as written. All five audits are fallback machine rows with stable_authoritative_database_record_id=null and candidate_sequence='None' plus candidate_sequence_length=4. The primary source states leucocyclicin C comprises 61 amino acids, llcA is a 63-aa precursor, the leader is MF, and the mature peptide is head-to-tail cyclized; the final record neither captures a valid sequence/modification boundary nor cleanly represents the zero-authoritative-row database state.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Rebuild the database audit to distinguish zero linked authoritative DBAASP rows from fallback machine candidates; do not present fallback rows as stable database records.",
      "Replace placeholder candidate_sequence='None'/candidate_sequence_length=4 with a structured null/not-reported state, or recover the actual source sequence from Fig. 3 and count residues exactly, excluding terminal cyclization chemistry from residue count.",
      "Preserve source identity fields for leucocyclicin C: mature 61-aa cyclic bacteriocin, llcA 63-aa precursor, MF leader, 6081.44 Da theoretical cyclic mass, producer Leuconostoc lactis APC 3969, DOI 10.1038/s41598-025-89450-x, PMCID PMC11845615.",
      "Make top-level worker-4 final provenance internally consistent with the current run_sequence gpt-5.5/xhigh evidence."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:abstract:1",
      "xml:p:18",
      "xml:table-wrap:4",
      "xml:p:40",
      "pdf:page=1",
      "pdf:page=4",
      "pdf:page=10"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC11845615-campaign-r01-PMC11845615-BLOCKER-W4-DATABASE-SEQUENCE-PLACEHOLDER"
  },
  {
    "acceptance_checks": [
      "A recursive source-locator scan over worker-4 work, packet analysis, paper final, and packet final database artifacts returns zero project paths in source_locator/source_locators.",
      "PMC11845615_strict_acceptance_audit_latest.json reports strict_worker_run_hard_finding_count 0 for recursive_non_source_locator_reference after rerun.",
      "Paper and packet final database_record_verification.json are byte-identical after repair.",
      "Database final still reports authoritative_dbaasp_ingest_ready false and fallback rows are not promoted."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T10:25:06.902125Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11845615/20260727T101517605842Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11845615_strict_acceptance_audit_latest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/work/database_record_audit/record_identity_audit.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/analysis/database_record_audit.worker4.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/final/database_record_verification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/authoritative_match_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/linked_sequence_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/linked_assay_records.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/database/dbaasp_machine_extracted_rows.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/source/paper.xml"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-4",
    "paper_id": "PMC11845615",
    "reason": "Current strict acceptance evidence contains 12 hard recursive_non_source_locator_reference findings in worker-4 database artifacts and their paper/packet final mirrors. Independent inspection confirmed $/cross_database_conflicts[0]/source_locators contains packets/PMC11845615/database/authoritative_match_report.json, linked_sequence_records.jsonl, and linked_assay_records.jsonl. Those are project artifact paths, not primary-source or allowed database-row source locators. The source-reviewed leucocyclicin C identity is supported by the paper XML/PDF, and zero linked authoritative DBAASP rows must remain database-provenance/caution evidence, not source_locator evidence.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Move packet/report file paths out of source_locator/source_locators fields into checked_inputs, evidence_paths, or provenance fields.",
      "Represent zero linked authoritative DBAASP rows as unresolved/caution database state without using packet artifacts as source locators.",
      "Regenerate worker-4 work, packet analysis, paper final, and packet final database artifacts from the repaired record.",
      "Keep authoritative_dbaasp_ingest_ready false and do not promote fallback rows to RC2, portal, or authoritative ingest unless real linked authoritative rows are added and source-reviewed."
    ],
    "severity": "blocking",
    "source_locators": [
      "strict_worker_run_gate.findings[0..11]",
      "$/cross_database_conflicts[0]/source_locators",
      "xml:abstract:1",
      "xml:p:18",
      "xml:p:40",
      "xml:fig:3",
      "xml:table-wrap:4",
      "pdf:page=1",
      "pdf:page=4",
      "pdf:page=5",
      "pdf:page=10",
      "database:dbaasp_machine_extracted_rows.jsonl:rows=1-5"
    ],
    "target_queue": "database",
    "ticket_id": "rwk-PMC11845615-campaign-r02-BF-PMC11845615-W4-001-recursive-database-source-locators"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11845615/work/database_record_audit/record_identity_audit.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11845615/analysis/database_record_audit.worker4.json
Use only statuses: source_verified, source_conflict, database_only_no_primary_source, sequence_modified_not_normalized, unresolved_record. Preserve DBAASP machine rows as candidate/database provenance until source-reviewed.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
