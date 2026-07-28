# PMC11956232 Worker-1 Intake Report

- Generated: 2026-07-26T14:34:29Z
- Worker: worker-1
- Internet used: false
- Source-verified claims made: false
- Lane status: source_reviewed_complete_for_intake_with_cautions
- Publication-grade status: not claimed by worker-1

## Contracts Reviewed
- Worker/strict skill and reference files: 6
- Leader preflight contracts: 1
- Leader evidence scaffold files: 4

## Metadata Cross-Check
- doi: sources=4, consistent=True, sources_present=authoritative_match_report_terms,database_source_manifest_identifiers,packet_manifest_metadata,paper_xml_article_meta
- pmid: sources=4, consistent=True, sources_present=authoritative_match_report_terms,database_source_manifest_identifiers,packet_manifest_metadata,paper_xml_article_meta
- pmcid: sources=5, consistent=True, sources_present=authoritative_match_report_terms,database_source_manifest_identifiers,packet_manifest_metadata,paper_meta_json,paper_xml_article_meta
- year: sources=3, consistent=False, sources_present=database_source_manifest_identifiers,packet_manifest_metadata,paper_xml_article_meta
- title_sha256: sources=4, consistent=False, sources_present=authoritative_match_report_terms,database_source_manifest_identifiers,packet_manifest_metadata,paper_xml_article_meta
- journal_sha256: sources=3, consistent=True, sources_present=database_source_manifest_identifiers,packet_manifest_metadata,paper_xml_article_meta

## Paper And Packet Materials
- Paper source assets inventoried: 4
- Packet raw assets inventoried: 4
- Raw mirror hash-matched assets: 4/4
- XML element counts: sections=33, table_wraps=3, figures=7, supplementary_material_refs=1
- PDF pages from pdfinfo: 11
- Supplementary source assets: 2 inventory entries across paper source and packet raw mirrors
- OA package: not_staged_in_checkout_recorded_unavailable

## Extracted Packet Surfaces
- XML sections artifact: sections=177, errors=0
- PDF text artifact: rows=11, pages=11, bad_lines=0
- PDF tables artifact: tables=3, rows=0, cells=0
- Figure captions artifact: figures=18
- Supplementary index/text/tables: files=1, text_rows=1, tables=2
- Locator index: declared=207, actual=207

## Database Provenance Boundary
- Candidate DBAASP machine rows: 12
- Linked authoritative row total: 0
- Machine extraction remains candidate evidence only; no database row is source-verified by this lane.

## Leader Scaffold Handling
- Figure crop files present: 7
- Rendered page files present: 7
- Figure/page/digitization scaffolds were checked for local file resolution only; approximate values remain unresolved scaffold material.

## Validation
- Packet gate artifact: pipeline_v2/deepmine/dbaasp_strict_pilot/papers/PMC11956232/work/intake/packet_gate_check.json
- Packet gate exit code: 2
- Packet gate paper count: 1
- Packet material status count: material_extracted_complete=1
- Packet hard findings for this paper: missing_final_files
- Interpretation: packet/material handoff files are present; the hard finding is for downstream final analysis artifacts outside worker-1 intake scope.

## Rework State
- Runtime-open ticket IDs assigned to worker-1: 0
- Packet rework request rows: 0
- Packet rework response rows: 0
- Owner repair response appended: false

## Blockers And Cautions
- Blockers: 0
- Cautions: 7
  - no_local_oa_package_directory_or_package_file_staged; recorded as unavailable in this intake artifact
  - linked_authoritative_database_rows_absent; dbaasp fallback rows remain candidate machine evidence only
  - one_or_more_leader_scaffold_file_references_do_not_resolve_locally
  - leader_figure_digitization_and_page_maps_are_scaffolds_only_not_exact_source_facts
  - terminal_publication_grade_not_asserted_by_worker_1; downstream source review_and_worker_6_adjudication_required
  - model_gate_not_independently_provable_from_artifact_context; publication_grade_status_not_claimed
  - packet_gate_reports_missing_final_files_for_downstream_analysis; not treated_as_worker_1_intake_material_blocker

## Analysis Status
- Existing analysis status: analysis_queued
- analysis_status.json action: unchanged
