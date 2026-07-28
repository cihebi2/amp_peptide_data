You are worker-3 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12606902.
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
- Runtime-open ticket IDs assigned to worker-3: ["rwk-PMC12606902-campaign-r01-worker3-supplementary-surface-not-exhausted", "rwk-PMC12606902-campaign-r02-BF-PMC12606902-W3-SUPPLEMENT-EMBEDDED-OLE-GAP"]
- Runtime-open ticket contracts assigned to worker-3: [
  {
    "acceptance_checks": [
      "supplementary_text.jsonl and supplementary_tables.json must either contain the recovered source surfaces with locators or rework_requests.jsonl must contain an open ticket for the unresolved OLE/figure surface.",
      "analysis_status.open_rework_ticket_count must equal the live non-closed ticket count in rework_requests.jsonl/rework_responses.jsonl.",
      "Final review materials_exhausted.supplementary_assets must not be true while a material-impacting unclassified supplement object remains unresolved."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T12:16:48.870809Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12606902/20260727T120713495065Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12606902/source/supplementary/12866_2025_4475_MOESM1_ESM.xls",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12606902/source/supplementary/12866_2025_4475_MOESM2_ESM.doc",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/extracted/supplementary_index.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/extracted/supplementary_text.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/extracted/supplementary_tables.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12606902/work/supplementary_methods/supplementary_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/rework/rework_requests.jsonl"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-3",
    "paper_id": "PMC12606902",
    "reason": "Supplementary extraction is not publication-grade exhausted. The packet records both supplements as inventory-only/empty extracted surfaces, and worker-3 reports an unclassified embedded OLE object in the legacy DOC with possible activity/mechanism impact, but no live rework ticket is open and the final review marks supplementary assets exhausted.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Move recovered supplementary text/table surfaces into packet extracted artifacts with resolvable supplement locators, or preserve the material gap as a blocking/major ticket assigned to material extraction.",
      "Classify or render the embedded OLE object, or document tool failure with impact and keep material status as extracted_with_gaps rather than exhausted if it can affect curated claims.",
      "Ensure supplement-derived claims are supported by inspectable text/table/figure surfaces."
    ],
    "severity": "blocking",
    "source_locators": [
      "supplementary_index.json $.files[*].extraction_status",
      "supplementary_evidence.json $.unrecoverable_material_gaps[0]",
      "review_report.json $.materials_exhausted.supplementary_assets"
    ],
    "target_queue": "material",
    "ticket_id": "rwk-PMC12606902-campaign-r01-worker3-supplementary-surface-not-exhausted"
  },
  {
    "acceptance_checks": [
      "extraction_status.json has supplementary_unparsed_embedded_object_count equal 0, or the remaining object is explicitly non-material with evidence.",
      "review_report.json has no worker-3 supplementary rework target and materials_exhausted.supplementary_assets.exhausted is true.",
      "locator_index.json resolves the embedded object content or records a non-material demotion locator."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T13:46:13.659454Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12606902/20260727T133607228682Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12606902/source/supplementary/12866_2025_4475_MOESM2_ESM.doc",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/extracted/archive_manifest.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/extraction/extraction_errors.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12606902/work/supplementary_methods/recovered_surfaces/MOESM2_embedded_object_classification.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/analysis/supplementary_evidence.worker3.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12606902/final/review_report.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-3",
    "paper_id": "PMC12606902",
    "reason": "Supplementary source exhaustion is incomplete. The staged MOESM2 DOC contains a ChemDraw embedded OLE object at ObjectPool/_1234567890; it is classified from OLE metadata but not rendered or source-reviewed. The final review keeps materials_exhausted.supplementary_assets false and carries a rework target for this material gap, so publication-grade PASS is not valid.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Render or otherwise source-review the ChemDraw embedded object, or write source-backed evidence that it is non-material for identity, activity/toxicity, mechanism, and assay conditions.",
      "Expose any recovered embedded-object content through packet supplementary_text or supplementary_tables with locator-index entries.",
      "Update materials_manifest and review_report only after the unresolved object count is zero or explicitly demoted as non-material."
    ],
    "severity": "blocking",
    "source_locators": [
      "supp:12866_2025_4475_MOESM2_ESM.doc:ole:ObjectPool/_1234567890",
      "supp:12866_2025_4475_MOESM2_ESM.doc:antiword:p=1..26",
      "supp:12866_2025_4475_MOESM2_ESM.doc:docbook:table=1..10"
    ],
    "target_queue": "material",
    "ticket_id": "rwk-PMC12606902-campaign-r02-BF-PMC12606902-W3-SUPPLEMENT-EMBEDDED-OLE-GAP"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12606902/work/supplementary_methods/supplementary_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12606902/analysis/supplementary_evidence.worker3.json
Inventory every staged or referenced supplement; record exact missing/unparsed material and impact.
When a blocking ticket requires quantitative figure observations, inspect the staged figure asset and recover every requested visible bar/point with axis calibration, approximate raw value, raw unit, uncertainty, image coordinates or equivalent calibration evidence, exact-vs-approximate status, and treatment/control role. A null raw_value or raw_unit is not a completed digitization when the plotted mark and axis can be calibrated. If the asset or scale is genuinely insufficient, leave the ticket open and record the exact material gap instead of emitting null placeholders as a repaired result.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
