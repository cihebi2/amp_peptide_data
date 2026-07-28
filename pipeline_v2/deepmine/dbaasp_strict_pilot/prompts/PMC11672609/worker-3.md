You are worker-3 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC11672609.
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
- Runtime-open ticket IDs assigned to worker-3: ["rwk-PMC11672609-campaign-r01-BF-PMC11672609-W3-SUPPLEMENT-PACKET-SURFACES"]
- Runtime-open ticket contracts assigned to worker-3: [
  {
    "acceptance_checks": [
      "packets/PMC11672609/extracted/supplementary_text.jsonl has nonzero records for the recovered supplementary PDF.",
      "packets/PMC11672609/extracted/supplementary_tables.json contains S1, S2, and S3 with row/table locators and exact/approximate status where relevant.",
      "packets/PMC11672609/locators/locator_index.json contains every supp locator cited by final activity/mechanism artifacts.",
      "A packet-only replay can resolve S1/S2/S3 and S1 activity rows without reading work/supplementary_methods as the authoritative source surface."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T16:06:44.327166Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11672609/20260727T155525413652Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11672609/source/supplementary/antibiotics-13-01113-s001.zip",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11672609/work/supplementary_methods/assets/antibiotics-3288224-supplementary.pdf",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11672609/work/supplementary_methods/assets/supplementary_pdf_text.txt",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11672609/work/supplementary_methods/supplementary_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/extracted/supplementary_text.jsonl",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/extracted/supplementary_tables.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/locators/locator_index.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/packet_manifest.json"
    ],
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-3",
    "paper_id": "PMC11672609",
    "reason": "The staged supplement was readable and parsed in worker-3 work artifacts, but the packet material surfaces remain empty: supplementary_text.jsonl has zero lines, supplementary_tables.json has no tables, and locator_index.json has no supplementary locators. Final mechanism and activity evidence therefore rely on work-only/recovered supplement context rather than packet-resolvable supplementary surfaces, while the packet is marked material_extracted_complete.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Promote recovered supplementary PDF text, table rows, figure/table labels, and stable source locators into the packet extracted surfaces and locator index.",
      "Declare any supplement locator alias policy explicitly, or replace supp:s001.pdf with the actual staged member name across finals.",
      "Update extraction/material status only after packet supplementary_text, supplementary_tables, and locator_index contain the recovered surfaces or durable gap evidence.",
      "Route downstream worker-2/worker-5 re-consumption of packet-resolvable supplementary locators after the packet refresh."
    ],
    "severity": "blocking",
    "source_locators": [
      "supp:antibiotics-3288224-supplementary.pdf:page=2:figure=S1",
      "supp:antibiotics-3288224-supplementary.pdf:page=3:figure=S2",
      "supp:antibiotics-3288224-supplementary.pdf:page=4:figure=S3",
      "supp:antibiotics-3288224-supplementary.pdf:page=5:figure=S4",
      "supp:antibiotics-3288224-supplementary.pdf:page=6:table=S1",
      "supp:antibiotics-3288224-supplementary.pdf:page=7-8:table=S2",
      "supp:antibiotics-3288224-supplementary.pdf:page=9:table=S3"
    ],
    "target_queue": "material",
    "ticket_id": "rwk-PMC11672609-campaign-r01-BF-PMC11672609-W3-SUPPLEMENT-PACKET-SURFACES"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11672609/work/supplementary_methods/supplementary_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11672609/analysis/supplementary_evidence.worker3.json
Inventory every staged or referenced supplement; record exact missing/unparsed material and impact.
When a blocking ticket requires quantitative figure observations, inspect the staged figure asset and recover every requested visible bar/point with axis calibration, approximate raw value, raw unit, uncertainty, image coordinates or equivalent calibration evidence, exact-vs-approximate status, and treatment/control role. A null raw_value or raw_unit is not a completed digitization when the plotted mark and axis can be calibrated. If the asset or scale is genuinely insufficient, leave the ticket open and record the exact material gap instead of emitting null placeholders as a repaired result.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
