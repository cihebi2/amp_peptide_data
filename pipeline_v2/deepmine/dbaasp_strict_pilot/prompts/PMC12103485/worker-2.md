You are worker-2 for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id PMC12103485.
- Read and obey your worker skill: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-body-table-worker/SKILL.md
- Read and obey these strict references:
- /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/amp-three-layer-curation/SKILL.md
- /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/amp-three-layer-curation/references/publication-grade-source-review.md
- /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/amp-three-layer-curation/references/publication-grade-quality-gate.md
- /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/amp-three-layer-curation/references/team-rework-message-contract.md
- /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/amp-three-layer-curation/references/two-queue-paper-packet-contract.md
- Use source-reviewed, paper-local evidence from this packet. Treat DBAASP Codex fallback rows as candidate machine evidence only.
- Keep human/source-reviewed claims separate from machine extraction.
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
- Paper root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12103485
- Packet root: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485
- Packet manifest: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/packet_manifest.json
- XML sections: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/extracted/xml_sections.json
- PDF text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/extracted/pdf_text.jsonl
- Supplement index/text: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/extracted/supplementary_index.json and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/extracted/supplementary_text.jsonl
- Database snapshot: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/database/database_source_manifest.json
- DBAASP candidate rows: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/database/dbaasp_machine_extracted_rows.jsonl
- Safe worker-2 activity handoff: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/analysis/activity_safe_candidate_handoff.json
- Authoritative DBAASP/merged match report: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/database/authoritative_match_report.json
- Linked authoritative rows, if any: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/database/linked_article_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/database/linked_assay_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/database/linked_sequence_records.jsonl, /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/database/linked_literature_records.jsonl
- Codex session audit: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/database/codex_session_audit.jsonl
- Packet gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py
- Semantic gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py
- Publication gate script: /home/cihebi/抗菌肽/数据集/batch/5-team/.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py
- Rework requests/responses: /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/rework/rework_requests.jsonl and /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/rework/rework_responses.jsonl
- Runtime-open ticket IDs assigned to worker-2: []

If an open rework ticket targets your lane, either repair the requested artifact or write a concise owner-repair response row to rework_responses.jsonl explaining the durable gap evidence and whether analysis can resume. Every owner response is nonterminal: use response_status repair_ready_for_adjudication, identify your worker in response_by, and never use closed*, resolved*, or repaired_*_complete as a status. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to another lane's ticket.

Required outputs for this worker:

Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12103485/work/activity_evidence/activity_records.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/analysis/activity_toxicity_evidence.worker2.json
Rows must be source-located with endpoint, raw_value, raw_unit or no-unit rationale, target species/strain, assay conditions, evidence_ladder, and source_locator.
Every row must use normalization_status exactly as direct, converted, not_convertible, or ambiguous. Direct/converted rows require normalized_value and normalized_unit. Direct means no value or unit conversion: do not copy a stale normalized value, change the unit, or hide a conversion under direct; put any non-conversion or ambiguity reason in a dedicated normalization note/rationale.
Use the safe candidate handoff first:
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485/analysis/activity_safe_candidate_handoff.json
Treat activity_table_locator_candidates as inspection hints only. Derive the endpoint, target, and unit from the cited table's own caption/header; table number or a machine label is never enough.
Do not emit activity rows from formulation/composition, FTIR/spectroscopy, TGA/thermal, contact-angle, tensile/mechanical, or reference columns.
Do not relabel a source unit to make a validator pass. If the source does not support an endpoint-specific unit, exclude or keep the candidate unresolved rather than inventing one.
Quantitative activity or toxicity evidence may be supported by an exact XML paragraph, figure/caption, or PDF-page locator. Lack of a source table is not a reason to discard it when treatment, endpoint, target, value, unit, and assay context are source-supported; emit the row or open a concrete ambiguity ticket instead of claiming no evidence.
Keep redundant record fields semantically identical: top-level concentration/concentration_unit must agree with any assay_conditions peptide/sample concentration copy. A stale nested scaffold value is a hard data conflict, not harmless metadata.
If a rework ticket asks about toxicity and all matched percentage surfaces are non-biological material measurements, write durable no-source-located-toxicity evidence in a nonterminal owner-repair response for your worker-2 ticket.
If a rework ticket declares expected_shape, expected_observation_counts, require_cell_locators, or expected_cell_observations, prove the full contract before marking your owner repair ready for worker-6 adjudication. Every expected_cell_observations locator must bind to that cell's named endpoint, value, unit, treatment, concentration/timepoint, and target fields; unique coordinates attached to the wrong existing rows are a hard failure. Do not satisfy a table ticket by attaching its base locator to unrelated existing rows, and do not mirror the same observation in both activity_records and toxicity_records.
Do not open raw paper XML/PDF, full xml_sections.json, full pdf_text.jsonl, or full table text in model context. If exact locator checking is needed, run a bounded local Python command that extracts only the requested locator IDs into a small JSON artifact under work/activity_evidence/, then read that small artifact. Terminal output must not contain source passages.


Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
