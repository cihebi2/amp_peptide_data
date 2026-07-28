You are worker-3 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12812963.
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
- Runtime-open ticket IDs assigned to worker-3: ["rwk-PMC12812963-campaign-r01-worker3-unrecovered-supplement-payloads-without-blocking-tic"]
- Runtime-open ticket contracts assigned to worker-3: [
  {
    "acceptance_checks": [
      "Run file-type checks showing Image_1.tif is an image payload and Presentation_1.pptx is a valid office/zip payload, or verify a blocking rework_requests.jsonl ticket exists for each unavailable true payload.",
      "Assert supplementary_text.jsonl or supplementary_tables.json contains extracted source material when the payload is recovered, or assert review_status is not accepted_clean/accepted_with_cautions when recovery remains impossible.",
      "Assert worker-3 lane_completion_assessment.source_reviewed_complete is true only after payload recovery or a source-backed nonimpact determination."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T22:53:53.027024Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC12812963/20260727T224149683171Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/source/supplementary/Image_1.tif",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/source/supplementary/Presentation_1.pptx",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/supplementary_index.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/supplementary_text.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extracted/supplementary_tables.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/extraction/extraction_errors.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/supplementary_methods/supplementary_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/rework/rework_requests.jsonl"
    ],
    "leader_finding_fingerprint": "dafbd1d068d34ea90667543f3a53b9af9e9ccbfbc966e89c78e186d25c981f6b",
    "leader_finding_id": "worker3_unrecovered_supplement_payloads_without_blocking_ticket",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-3",
    "paper_id": "PMC12812963",
    "reason": "Both staged supplementary files are readable but are not the declared scientific payloads: file inspection shows HTML documents saved as Image_1.tif and Presentation_1.pptx, supplementary_text.jsonl is empty, and supplementary_tables.json contains no tables. Worker-3 recorded source_reviewed_complete=false, needs_targeted_rework=true, and analysis_can_resume=false for supplement-dependent claims, but live rework_requests.jsonl is empty and final review accepted the paper with only cautions.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Recover the true supplementary TIF/PPTX payloads, or keep this paper non-publication-grade with a blocking material ticket that names the unavailable payloads and attempted commands.",
      "Populate extracted supplementary text/table/image evidence where recoverable, or explicitly prove that the missing payloads cannot affect activity, identity, mechanism, methods, or toxicity fields.",
      "Update packet material status and final review status so unresolved supplement payload gaps cannot be accepted as publication-grade complete."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:supplementary-material:id=SM1",
      "xml:supplementary-material:id=SM2",
      "source/supplementary/Image_1.tif HTML title Preparing to download",
      "source/supplementary/Presentation_1.pptx HTML title Preparing to download"
    ],
    "target_queue": "material",
    "ticket_id": "rwk-PMC12812963-campaign-r01-worker3-unrecovered-supplement-payloads-without-blocking-tic"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12812963/work/supplementary_methods/supplementary_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12812963/analysis/supplementary_evidence.worker3.json
Inventory every staged or referenced supplement; record exact missing/unparsed material and impact.
When a blocking ticket requires quantitative figure observations, inspect the staged figure asset and recover every requested visible bar/point with axis calibration, approximate raw value, raw unit, uncertainty, image coordinates or equivalent calibration evidence, exact-vs-approximate status, and treatment/control role. A null raw_value or raw_unit is not a completed digitization when the plotted mark and axis can be calibrated. If the asset or scale is genuinely insufficient, leave the ticket open and record the exact material gap instead of emitting null placeholders as a repaired result.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
