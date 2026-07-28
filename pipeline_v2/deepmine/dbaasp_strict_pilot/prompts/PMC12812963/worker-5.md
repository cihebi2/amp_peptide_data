You are worker-5 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12812963.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-5: ["rwk-PMC12812963-campaign-r01-worker5-recursive-non-source-mechanism-locator"]
- Runtime-open ticket contracts assigned to worker-5: [
  {
    "acceptance_checks": [
      "Recursively scan final/work/analysis mechanism JSON and assert source_locator/supporting_source_locators values do not contain pipeline_v2 paths.",
      "Assert strict_acceptance_audit_latest.json strict_worker_run_gate.hard_finding_count is 0 for PMC12812963.",
      "Assert recursive_authority_boundary_false is true only after the recursive locator findings are cleared."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T22:53:53.036056Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12812963/20260727T224149683171Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/final/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/final/mechanism_ontology_record.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/analysis/mechanism_evidence.worker5.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/mechanism_ontology/mechanism_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC12812963_strict_acceptance_audit_latest.json"
    ],
    "leader_finding_fingerprint": "a9e1e52eaedf354e7d8a724553e3aff701935528f8ec1d272bfffe28e1541538",
    "leader_finding_id": "worker5_recursive_non_source_mechanism_locator",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-5",
    "paper_id": "PMC12812963",
    "reason": "The current strict acceptance artifact records 5 hard recursive_non_source_locator_reference findings for the mechanism layer. Mechanism claim 2 in work, analysis, packet-final, and paper-final artifacts lists pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/analysis/activity_toxicity_evidence.worker2.json under supporting_source_locators; that is a derivative worker artifact, not a primary XML/PDF/table/supplement/database locator.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Move worker-artifact paths out of source-locator fields and into provenance or checked-input fields.",
      "Replace mechanism claim 2 supporting_source_locators with primary source locators such as xml:table-wrap:1, xml:table-wrap:2, and xml:table-wrap:4.",
      "Rerun the strict worker-run recursive-authority gate and do not claim publication-grade readiness until hard_finding_count is zero."
    ],
    "severity": "blocking",
    "source_locators": [
      "$/mechanism_claims/1/supporting_source_locators/0",
      "xml:table-wrap:1",
      "xml:table-wrap:2",
      "xml:table-wrap:4",
      "xml:sec15",
      "xml:fig:4",
      "pdf:page=6 Table 4",
      "pdf:page=7 Figure 4"
    ],
    "target_queue": "mechanism",
    "ticket_id": "rwk-PMC12812963-campaign-r01-worker5-recursive-non-source-mechanism-locator"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/mechanism_ontology/mechanism_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/analysis/mechanism_evidence.worker5.json
Every mechanism_claim must have claim_id, claim_text, entity_scope, evidence_class, source_locator, and direct_assay_types when direct.
Set review_model exactly to gpt-5.5 and reasoning_effort exactly to xhigh in both required artifacts; the independent run report is the runtime proof.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
