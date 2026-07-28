You are worker-2 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC11897483.
- Read and obey your worker skill: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-body-table-worker/SKILL.md
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11897483
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/analysis/activity_safe_candidate_handoff.json
- Leader preflight contracts: []
- Leader preflight evidence scaffolds: []
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-2: ["rwk-PMC11897483-campaign-r02-BF-PMC11897483-W2-P39-CFS-ENTITY-MISLINK"]
- Runtime-open ticket contracts assigned to worker-2: [
  {
    "acceptance_checks": [
      "A script over both final activity_toxicity_evidence.json mirrors finds zero accepted records with source_locator/source_locators containing xml:p:39 or xml:fig:5 and entity or peptide equal to Bacteriocin P7.",
      "The same script finds the nine p39/Figure 5 source values 15.96 ± 0.66, 12.24 ± 0.24, 12.12 ± 0.38, 13.96 ± 0.06, 11.92 ± 0.33, 10.05 ± 0.28, 23.78 ± 0.29, 22.56 ± 0.59, and 14.14 ± 0.39 retained only under a source-supported CFS/cell-free-supernatant entity scope.",
      "Table 2 still has exactly 26 numeric mm activity records and 10 dash exclusions, and toxicity exact Figure 10A values remain unchanged.",
      "The regenerated strict acceptance audit no longer reports publication_grade_ready around this p39 entity-scope check."
    ],
    "blocks": [
      "publication_grade_acceptance",
      "leader_semantic_pass",
      "independent_verifier_pass",
      "remaining_200_batch_progress"
    ],
    "created_at": "2026-07-27T23:47:40.344380Z",
    "evidence_paths": [
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/PMC11897483/20260727T233835836068Z.leader_semantic_auditor.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11897483/source/paper.xml",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11897483/source/paper.pdf",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/extracted/xml_sections.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/extracted/figure_captions.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11897483/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/final/activity_toxicity_evidence.json",
      "pipeline_v2/deepmine/dbaasp_strict_pilot/reports/PMC11897483_strict_acceptance_audit_latest.json"
    ],
    "leader_finding_fingerprint": "37bcd03e989e57cba53464c3f09956de90ed4f1e086dcea2a5cfb44621a1d64f",
    "leader_finding_id": "BF-PMC11897483-W2-P39-CFS-ENTITY-MISLINK",
    "owner_response_contract": "Append one evidence-bearing repair_ready_for_adjudication response; only a later fresh worker-6 may close this ticket.",
    "owner_worker": "worker-2",
    "paper_id": "PMC11897483",
    "reason": "Nine accepted p39/Figure 5 activity_records are not source-reviewable because their entity and peptide fields say Bacteriocin P7, while the primary source locator is the stability-results surface for CFS/cell-free supernatant. Source p39 discusses CFS antimicrobial activity under pH and UV treatments; Figure 5 is captioned as cell-free supernatant stability. Purified Bacteriocin P7 activity is reported later at xml:p:45/xml:p:47/xml:p:49. The current strict acceptance artifact reports zero hard findings, so it accepted around a material entity-scope error.",
    "requested_by": "structured_leader_field_level_semantic_audit",
    "required_actions": [
      "Re-open xml:p:39, xml:fig:5, and the PDF Figure 5 surface and rebuild the nine accepted stability records with entity/peptide/sample scope as CFS, cell-free supernatant, fermentation broth, or another exact source-supported term, not purified Bacteriocin P7.",
      "Preserve the existing p39 values, targets, units, exact-vs-approximate status, and pH/UV conditions only where the source binds them.",
      "Keep the separate purified Bacteriocin P7 records at xml:p:45, xml:p:47, xml:p:49, and xml:fig:10 distinct from CFS/stability records.",
      "Update paper and packet final activity_toxicity_evidence.json mirrors byte-identically and rerun strict source-level checks."
    ],
    "severity": "blocking",
    "source_locators": [
      "xml:p:39",
      "xml:fig:5",
      "pdf:page=6",
      "pdf:page=9:figure=5",
      "xml:p:45",
      "xml:p:47",
      "xml:p:49",
      "activity_toxicity_evidence.json activity_records[29-37]"
    ],
    "target_queue": "analysis",
    "ticket_id": "rwk-PMC11897483-campaign-r02-BF-PMC11897483-W2-P39-CFS-ENTITY-MISLINK"
  }
]

The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11897483/work/activity_evidence/activity_records.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/analysis/activity_toxicity_evidence.worker2.json
Rows must be source-located with endpoint, raw_value, raw_unit or no-unit rationale, target species/strain, assay conditions, evidence_ladder, and source_locator.
Every row must use normalization_status exactly as direct, converted, not_convertible, or ambiguous. Direct/converted rows require normalized_value and normalized_unit. Direct means no value or unit conversion: do not copy a stale normalized value, change the unit, or hide a conversion under direct; put any non-conversion or ambiguity reason in a dedicated normalization note/rationale.
Use the safe candidate handoff first:
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC11897483/analysis/activity_safe_candidate_handoff.json
Treat activity_table_locator_candidates as inspection hints only. Derive the endpoint, target, and unit from the cited table's own caption/header; table number or a machine label is never enough.
Do not emit activity rows from formulation/composition, FTIR/spectroscopy, TGA/thermal, contact-angle, tensile/mechanical, or reference columns.
Do not relabel a source unit to make a validator pass. If the source does not support an endpoint-specific unit, exclude or keep the candidate unresolved rather than inventing one.
Quantitative activity or toxicity evidence may be supported by an exact XML paragraph, figure/caption, or PDF-page locator. Lack of a source table is not a reason to discard it when treatment, endpoint, target, value, unit, and assay context are source-supported; emit the row or open a concrete ambiguity ticket instead of claiming no evidence.
Keep redundant record fields semantically identical: top-level concentration/concentration_unit must agree with any assay_conditions peptide/sample concentration copy. A stale nested scaffold value is a hard data conflict, not harmless metadata.
If a rework ticket asks about toxicity and all matched percentage surfaces are non-biological material measurements, write durable no-source-located-toxicity evidence in a nonterminal owner-repair response for your worker-2 ticket.
If a rework ticket declares expected_shape, expected_observation_counts, require_cell_locators, or expected_cell_observations, prove the full contract before marking your owner repair ready for worker-6 adjudication. Every expected_cell_observations locator must bind to that cell's named endpoint, value, unit, treatment, concentration/timepoint, and target fields; unique coordinates attached to the wrong existing rows are a hard failure. Do not satisfy a table ticket by attaching its base locator to unrelated existing rows, and do not mirror the same observation in both activity_records and toxicity_records.
Do not open raw paper XML/PDF, full xml_sections.json, full pdf_text.jsonl, or full table text in model context. If exact locator checking is needed, run a bounded local Python command that extracts only the requested locator IDs into a small JSON artifact under work/activity_evidence/, then read that small artifact. Terminal output must not contain source passages.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
