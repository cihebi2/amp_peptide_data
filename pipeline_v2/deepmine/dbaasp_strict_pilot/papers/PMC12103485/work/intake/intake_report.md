# Worker-1 Intake Report - PMC12103485

- Generated: `2026-07-15T10:34:24Z`
- Lane: `worker-1` / `intake_linkage`
- Scope: local checkout packet only; internet not used.
- Claim boundary: no `source_verified` database claims, no activity conclusions, no mechanism conclusions, no publication-grade claim.

## Intake Decision

- Material queue status: `material_extracted_complete`
- Worker-1 intake source-reviewed complete: `true`
- Downstream material handoff ready: `true`
- Analysis status observed but not modified by worker-1: `analysis_source_reviewed_accepted`
- Analysis status file updated: `false`

## Roots

- Paper root: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12103485`
- Packet root: `pipeline_v2/deepmine/dbaasp_strict_pilot/packets/PMC12103485`
- Source root: `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12103485/source`

## Metadata Cross-Check

- Identifier fields checked: `doi, pmid, pmcid, pmcid-ver, pmcaid, pmcaiid, journal, year`
- Identifier match statuses: `{"doi": "all_present_values_match", "journal": "all_present_values_match", "pmcaid": "all_present_values_match", "pmcaiid": "all_present_values_match", "pmcid": "all_present_values_match", "pmcid-ver": "all_present_values_match", "pmid": "all_present_values_match", "year": "all_present_values_match"}`
- Title present in local metadata/XML: `true`

## Material Inventory Counts

- archive_count: `0`
- extraction_error_rows: `0`
- figure_captions: `15`
- locator_count: `150`
- pdf_tables: `1`
- pdf_text_rows: `13`
- supplementary_files: `0`
- supplementary_tables: `0`
- supplementary_text_rows: `0`
- xml_sections: `137`

## Database Snapshot

- Manifest row count fields: `{"codex_exec_sessions": 0, "dbaasp_empty_done_rows": 0, "dbaasp_machine_extracted_rows": 13, "dbaasp_review_queue_rows": 0, "linked_article_records": 0, "linked_assay_records": 0, "linked_literature_records": 0, "linked_sequence_records": 0}`
- Observed JSONL row counts: `{"codex_session_audit": 0, "dbaasp_empty_done_rows": 0, "dbaasp_machine_extracted_rows": 13, "dbaasp_review_queue_rows": 0, "linked_article_records": 0, "linked_assay_records": 0, "linked_literature_records": 0, "linked_sequence_records": 0}`
- DBAASP Codex fallback rows: candidate machine evidence only.
- Linked authoritative article/assay/sequence/literature JSONL rows are inventoried separately from paper-local evidence.

## Rework State

- Rework request rows: `5`
- Rework response rows: `16`
- Manifest open rework ticket IDs: `[]`
- Worker-1/material tickets unresolved: `0`
- Non-intake tickets not modified by worker-1: `4`

## Blockers And Cautions

- Unresolved worker-1 blockers: `0`
- Caution: Authoritative linked DBAASP row JSONL files have zero rows in this packet; candidate machine rows remain machine evidence only.
- Caution: Final analysis acceptance is outside worker-1 scope and must remain separated from material intake completion.

## Files Written

- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12103485/work/intake/source_inventory.json`
- `pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC12103485/work/intake/intake_report.md`
