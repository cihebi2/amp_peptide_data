You are worker-3 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC11956232.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: ["/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/source_surface_preflight_contract_20260726.json"]
- Leader preflight evidence scaffolds: ["/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/figure_crop_manifest.json", "/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/figure_page_map.json", "/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/leader_color_digitized_figures1_2.json", "/home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/rendered_page_manifest.json"]
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-3: ["rwk-PMC11956232-quantitative-figure-exhaustion-001"]
- Runtime-open ticket contracts assigned to worker-3: [
  {
    "ticket_id": "rwk-PMC11956232-quantitative-figure-exhaustion-001",
    "paper_id": "PMC11956232",
    "created_at": "2026-07-26T15:43:37.952747Z",
    "requested_by": "leader_field_level_semantic_audit",
    "target_queue": "analysis",
    "owner_worker": "worker-3",
    "severity": "blocking",
    "reason": "The accepted final omitted all 757 contract-required quantitative figure observations. Worker-3 acknowledged that it only verified a scaffold/hash and did not independently source-review or terminally digitize Figures 1-7.",
    "blocks": [
      "supplementary_evidence",
      "activity_toxicity_evidence",
      "review_report",
      "publication_grade_acceptance",
      "remaining_200_batch_progress"
    ],
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_semantic_audit_20260726.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/validate_candidate19_terminal_contract.py",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_final_pre_rework_fail.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/source_surface_preflight_contract_20260726.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_worker3_pre_rework_fail.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/leader_preflight/leader_color_digitized_figures1_2.json"
    ],
    "required_actions": {
      "independent_source_review": "Independently inspect the packet XML/PDF plus all seven 300-dpi figure crops. The leader scaffold is candidate evidence only; verify every retained value against the source and do not copy it blindly.",
      "standardized_output": "Write top-level figure_quantitative_observations and figure_surface_exhaustion into both work/supplementary_methods/supplementary_evidence.json and packet analysis/supplementary_evidence.worker3.json. Every observation needs a unique observation_id, Figure 1-7 surface, semantic group coordinates, raw_value/raw_unit, source_locator, source_reviewed=true or source_review_status, exact_vs_approximate_status, calibration/uncertainty where applicable, and source_reviewed_by=worker-3.",
      "figure_counts": {
        "Figure 1": 360,
        "Figure 2": 280,
        "Figure 3": 20,
        "Figure 4": 98,
        "Figure 5": 18,
        "Figure 6": 17,
        "Figure 7": 4
      },
      "figure12_nulls": "Account for all 640 treatment observations. A source-resolved numeric value is preferred. If an individual curve point is occluded/overlapped and cannot be separately read, retain null only with a terminal_resolution_status accepted by the immutable leader validator, a concrete missing_reason, source review proof, and numeric_value_not_fabricated=true.",
      "figure3_7": "Digitize all 20 Figure-3 bars, all 98 Figure-4 heatmap cells, all 18 Figure-5 bars, all 17 Figure-6 bars, and the four exact plotted Figure-7 day-7 plateaus PBS=100%, Control=10%, 1xMIC=80%, 2xMIC=70%. Preserve calibration and uncertainty and the semantic evidence boundaries in the preflight contract.",
      "leader_validator": "Run python3 pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/validate_candidate19_terminal_contract.py --mode worker3 --output pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/review/leader_candidate19_worker3_post_rework.json; require exit code 0, passed=true, and zero blocking failures. Do not edit, replace, weaken, or bypass the leader-owned validator (expected pre-rework SHA-256 b7c17eb745b65f64d8834491a50e2a585e02b8570c666a318344e898b59e0a64).",
      "owner_response": "Append one nonterminal evidence-bearing repair_ready_for_adjudication response for this exact ticket only after the leader validator passes."
    },
    "acceptance_checks": {
      "worker3_leader_validator_pass": true,
      "figure_quantitative_observation_count": 757,
      "figure1_2_treatment_count": 640,
      "figure3_7_count": 117,
      "figure7_day7_plateaus": {
        "PBS": 100,
        "Control": 10,
        "1xMIC": 80,
        "2xMIC": 70
      },
      "fabricated_numeric_fill_count": 0
    }
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/supplementary_methods/supplementary_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11956232/analysis/supplementary_evidence.worker3.json
Inventory every staged or referenced supplement; record exact missing/unparsed material and impact.
When a blocking ticket requires quantitative figure observations, inspect the staged figure asset and recover every requested visible bar/point with axis calibration, approximate raw value, raw unit, uncertainty, image coordinates or equivalent calibration evidence, exact-vs-approximate status, and treatment/control role. A null raw_value or raw_unit is not a completed digitization when the plotted mark and axis can be calibrated. If the asset or scale is genuinely insufficient, leave the ticket open and record the exact material gap instead of emitting null placeholders as a repaired result.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
