You are worker-3 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12124432.
- Read and obey your worker skill: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-supp-evidence-worker/SKILL.md
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
- Runtime-open ticket IDs assigned to worker-3: ["rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-001"]
- Runtime-open ticket contracts assigned to worker-3: [
  {
    "acceptance_checks": [
      "A byte/content check on ANIE-64-e202501299-s001.csv fails if it contains '<html', 'Preparing to download', or 'POW_CHALLENGE'.",
      "extraction_status.json either has material_extracted_complete with the real CSV extracted or material_extracted_with_gaps with publication_grade=false in final review_report.",
      "supplementary_evidence.json and review_report cite the CSV as recovered/extracted or explicitly preserve a blocking source gap without claiming publication-grade source exhaustion."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T21:33:13.224951Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12124432/20260727T212323249023Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12124432/source/supplementary/ANIE-64-e202501299-s001.csv",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/raw/supplementary_original/ANIE-64-e202501299-s001.csv",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/extracted/supplementary_index.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/extraction/extraction_quality_report.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/extraction/extraction_errors.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12124432/source/paper.xml"
    ],
    "leader_finding_fingerprint": "39abbe2bd1a8a7b9adef6b5ec806fa12f6706a76a66556383b72c1edad646862",
    "leader_finding_id": "PMC12124432-BLOCK-FIELD-001",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-3",
    "paper_id": "PMC12124432",
    "reason": "The staged S1 CSV is not a source-reviewable supplement. The path is readable, so this is not an infrastructure/access failure, but its content is HTML proof-of-work placeholder text rather than the XML-declared text/plain supplementary material. Because the paper states that supporting data are in the supplementary material, accepting publication_grade=true around this missing surface is not scientifically valid.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Restage the real ANIE-64-e202501299-s001.csv or write a durable source-gap record that explicitly proves the true CSV is unavailable after source-pool/package checks.",
      "If the real CSV is recovered, extract and compare it against existing activity, identity, and mechanism surfaces; if unavailable, keep publication_grade false or accepted_with_caution non-publication-grade until the missing surface is adjudicated under the source-review contract.",
      "Update supplementary_index, extraction_status, extraction_quality_report, and final review/material summaries so the CSV is not treated as exhausted source data."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:27",
      "media:xlink:href=ANIE-64-e202501299-s001.csv",
      "supp:ANIE-64-e202501299-s001.csv:source_gap=placeholder_html"
    ],
    "target_queue": "material",
    "ticket_id": "rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-001"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12124432/work/supplementary_methods/supplementary_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12124432/analysis/supplementary_evidence.worker3.json
Inventory every staged or referenced supplement; record exact missing/unparsed material and impact.
When a blocking ticket requires quantitative figure observations, inspect the staged figure asset and recover every requested visible bar/point with axis calibration, approximate raw value, raw unit, uncertainty, image coordinates or equivalent calibration evidence, exact-vs-approximate status, and treatment/control role. A null raw_value or raw_unit is not a completed digitization when the plotted mark and axis can be calibrated. If the asset or scale is genuinely insufficient, leave the ticket open and record the exact material gap instead of emitting null placeholders as a repaired result.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
