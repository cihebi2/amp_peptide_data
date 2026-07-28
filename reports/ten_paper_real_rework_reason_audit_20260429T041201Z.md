# 10 Paper Real Rework Reason Audit

- Generated: 2026-04-29T04:12:01Z
- Correction: capped rework test was a workflow guard test; below separates generic review-ticket blockers from paper-specific evidence problems.
- Original material root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/<paper_id>/`
- Database root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/`

## doi__10.1002_cmdc.201900465
- Title: Proline-Rich Peptides with Improved Antimicrobial Activity against E. coli, K. pneumoniae, and A. baumannii.
- Source root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1002_cmdc.201900465`
- Material inventory: `{'package_files': 2, 'pdf_files': 2, 'supplementary_files': 3, 'xml_files': 3}`
- Extraction counts: `{'xml_section_count': 29, 'xml_table_count': 3, 'figure_caption_count': 5, 'package_member_count': 32, 'supplementary_asset_count': 3, 'supplement_parse_count': 3, 'supplementary_table_count': 0, 'quality_status': 'complete_with_targeted_analysis_rework'}`
- Semantic issue groups: `{'activity:sentence_fragment_species': 18, 'review:review_status_not_publication_grade': 1, 'review:publication_grade_not_true': 1}`
- Publication risk counts: `{'open_rework_targets': 1}`
- DB status summary: `{'source_conflict': 232, 'source_verified': 221}`
- Activity records: 157; activity sanity issues: 5; mechanism claims: 3
- Activity sanity examples: `[{'record_id': 'doi__10.1002_cmdc.201900465-table2-r2-c3-MIC', 'endpoint': 'MIC', 'entity': '32', 'raw_value': '32', 'raw_unit': '%', 'target_species': 'wt'}, {'record_id': 'doi__10.1002_cmdc.201900465-table2-r2-c4-MIC', 'endpoint': 'MIC', 'entity': 'Viab% 108', 'raw_value': '108', 'raw_unit': '%', 'target_species': 'wt'}, {'record_id': 'doi__10.1002_cmdc.201900465-table2-r2-c5-MIC', 'endpoint': 'MIC', 'entity': 'Code 277', 'raw_value': '277', 'raw_unit': '%', 'target_species': 'wt'}, {'record_id': 'doi__10.1002_cmdc.201900465-table2-r2-c8-MIC', 'endpoint': 'MIC', 'entity': '8', 'raw_value': '8', 'raw_unit': '%', 'target_species': 'wt'}, {'record_id': 'doi__10.1002_cmdc.201900465-table2-r2-c9-MIC', 'endpoint': 'MIC', 'entity': 'Viab% 99', 'raw_value': '99', 'raw_unit': '%', 'target_species': 'wt'}]`
- Real reasons:
  - review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
  - gate/parser issue: valid abbreviated organism names such as A. baumannii are flagged by the sentence-fragment heuristic and must be normalized or the gate fixed
  - activity parser quality issue: some extracted rows use peptide IDs/method labels/properties as target species or MIC rows, so row-level activity needs repair before acceptance
  - database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
  - material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion

## doi__10.1002_advs.202205301
- Title: Combating Escherichia coli O157:H7 with Functionalized Chickpea-Derived Antimicrobial Peptides.
- Source root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1002_advs.202205301`
- Material inventory: `{'package_files': 1, 'pdf_files': 1, 'supplementary_files': 2, 'xml_files': 2}`
- Extraction counts: `{'xml_section_count': 46, 'xml_table_count': 1, 'figure_caption_count': 9, 'package_member_count': 24, 'supplementary_asset_count': 2, 'supplement_parse_count': 2, 'supplementary_table_count': 4, 'quality_status': 'complete_with_targeted_analysis_rework'}`
- Semantic issue groups: `{'review:review_status_not_publication_grade': 1, 'review:publication_grade_not_true': 1}`
- Publication risk counts: `{'open_rework_targets': 1}`
- DB status summary: `{'database_only_no_primary_source': 1, 'source_conflict': 27, 'source_verified': 217}`
- Activity records: 77; activity sanity issues: 0; mechanism claims: 3
- Real reasons:
  - review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
  - database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
  - material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion

## doi__10.1002_advs.202401793
- Title: Dual-Mechanism Peptide SR25 has Broad Antimicrobial Activity and Potential Application for Healing Bacteria-infected Diabetic Wounds.
- Source root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1002_advs.202401793`
- Material inventory: `{'package_files': 1, 'pdf_files': 1, 'supplementary_files': 2, 'xml_files': 2}`
- Extraction counts: `{'xml_section_count': 57, 'xml_table_count': 1, 'figure_caption_count': 7, 'package_member_count': 20, 'supplementary_asset_count': 2, 'supplement_parse_count': 1, 'supplementary_table_count': 1, 'quality_status': 'complete_with_targeted_analysis_rework'}`
- Semantic issue groups: `{'review:review_status_not_publication_grade': 1, 'review:publication_grade_not_true': 1}`
- Publication risk counts: `{'open_rework_targets': 1}`
- DB status summary: `{'database_only_no_primary_source': 4, 'source_conflict': 16, 'source_verified': 103}`
- Activity records: 80; activity sanity issues: 0; mechanism claims: 3
- Real reasons:
  - review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
  - database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
  - material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion

## doi__10.1002_cbic.202100609
- Title: Effect of Amino Acid Substitutions on 70S Ribosomal Binding, Cellular Uptake, and Antimicrobial Activity of Oncocin Onc112.
- Source root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1002_cbic.202100609`
- Material inventory: `{'package_files': 2, 'pdf_files': 2, 'supplementary_files': 3, 'xml_files': 3}`
- Extraction counts: `{'xml_section_count': 30, 'xml_table_count': 1, 'figure_caption_count': 5, 'package_member_count': 30, 'supplementary_asset_count': 3, 'supplement_parse_count': 3, 'supplementary_table_count': 0, 'quality_status': 'complete_with_targeted_analysis_rework'}`
- Semantic issue groups: `{'review:review_status_not_publication_grade': 1, 'review:publication_grade_not_true': 1}`
- Publication risk counts: `{'open_rework_targets': 1}`
- DB status summary: `{'source_conflict': 449, 'source_verified': 105}`
- Activity records: 40; activity sanity issues: 10; mechanism claims: 3
- Activity sanity examples: `[{'record_id': 'doi__10.1002_cbic.202100609-table1-r3-c1-MIC', 'endpoint': 'MIC', 'entity': '[mg/L] K. pneumoniae DSM 681', 'raw_value': '8', 'raw_unit': 'mg/L', 'target_species': 'Onc112'}, {'record_id': 'doi__10.1002_cbic.202100609-table1-r3-c2-MIC', 'endpoint': 'MIC', 'entity': 'A. baumannii DSM 30008', 'raw_value': '2', 'raw_unit': 'mg/L', 'target_species': 'Onc112'}, {'record_id': 'doi__10.1002_cbic.202100609-table1-r3-c3-MIC', 'endpoint': 'MIC', 'entity': 'P. aeruginosa DSM 1117', 'raw_value': '32', 'raw_unit': 'mg/L', 'target_species': 'Onc112'}, {'record_id': 'doi__10.1002_cbic.202100609-table1-r3-c4-MIC', 'endpoint': 'MIC', 'entity': 'S. aureus DSM 6247', 'raw_value': '64', 'raw_unit': 'mg/L', 'target_species': 'Onc112'}, {'record_id': 'doi__10.1002_cbic.202100609-table1-r3-c5-MIC', 'endpoint': 'MIC', 'entity': 'column_5', 'raw_value': '64', 'raw_unit': 'mg/L', 'target_species': 'Onc112'}]`
- Real reasons:
  - review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
  - activity parser quality issue: some extracted rows use peptide IDs/method labels/properties as target species or MIC rows, so row-level activity needs repair before acceptance
  - database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
  - material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion

## doi__10.1002_cbic.202100151
- Title: Molecular Basis of Selectivity and Activity for the Antimicrobial Peptide Lynronne-1 Informs Rational Design of Peptide with Improved Activity.
- Source root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1002_cbic.202100151`
- Material inventory: `{'package_files': 1, 'pdf_files': 1, 'supplementary_files': 1, 'xml_files': 2}`
- Extraction counts: `{'xml_section_count': 11, 'xml_table_count': 3, 'figure_caption_count': 6, 'package_member_count': 17, 'supplementary_asset_count': 1, 'supplement_parse_count': 1, 'supplementary_table_count': 0, 'quality_status': 'complete_with_targeted_analysis_rework'}`
- Semantic issue groups: `{'review:review_status_not_publication_grade': 1, 'review:publication_grade_not_true': 1, 'activity:missing_activity_records': 1}`
- Publication risk counts: `{'open_rework_targets': 1}`
- DB status summary: `{'source_conflict': 39, 'source_verified': 4}`
- Activity records: 0; activity sanity issues: 0; mechanism claims: 2
- Real reasons:
  - review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
  - activity extraction gap: source tables/prose expose activity endpoints but current parser produced zero activity records
  - database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
  - material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion

## doi__10.1002_cmdc.201600498
- Title: Characterization of a Cell-Penetrating Peptide with Potential Anticancer Activity.
- Source root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1002_cmdc.201600498`
- Material inventory: `{'package_files': 1, 'pdf_files': 1, 'supplementary_files': 1, 'xml_files': 2}`
- Extraction counts: `{'xml_section_count': 10, 'xml_table_count': 2, 'figure_caption_count': 6, 'package_member_count': 16, 'supplementary_asset_count': 1, 'supplement_parse_count': 1, 'supplementary_table_count': 0, 'quality_status': 'complete_with_targeted_analysis_rework'}`
- Semantic issue groups: `{'review:review_status_not_publication_grade': 1, 'review:publication_grade_not_true': 1}`
- Publication risk counts: `{'open_rework_targets': 1}`
- DB status summary: `{'source_conflict': 34, 'source_verified': 2}`
- Activity records: 1; activity sanity issues: 1; mechanism claims: 2
- Activity sanity examples: `[{'record_id': 'doi__10.1002_cmdc.201600498-table2-r27-c2-IC50', 'endpoint': 'IC50', 'entity': '[μm][a] 3.9±0.8', 'raw_value': '>50', 'raw_unit': 'μM', 'target_species': 'Normal fibroblasts'}]`
- Real reasons:
  - review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
  - activity parser quality issue: some extracted rows use peptide IDs/method labels/properties as target species or MIC rows, so row-level activity needs repair before acceptance
  - database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
  - material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion

## doi__10.1002_cmdc.202200291
- Title: Machine Learning Guided Discovery of Non-Hemolytic Membrane Disruptive Anticancer Peptides.
- Source root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1002_cmdc.202200291`
- Material inventory: `{'package_files': 1, 'pdf_files': 1, 'supplementary_files': 1, 'xml_files': 2}`
- Extraction counts: `{'xml_section_count': 18, 'xml_table_count': 1, 'figure_caption_count': 4, 'package_member_count': 13, 'supplementary_asset_count': 1, 'supplement_parse_count': 1, 'supplementary_table_count': 0, 'quality_status': 'complete_with_targeted_analysis_rework'}`
- Semantic issue groups: `{'review:review_status_not_publication_grade': 1, 'review:publication_grade_not_true': 1}`
- Publication risk counts: `{'open_rework_targets': 1}`
- DB status summary: `{'source_conflict': 144, 'source_verified': 252}`
- Activity records: 253; activity sanity issues: 249; mechanism claims: 2
- Activity sanity examples: `[{'record_id': 'doi__10.1002_cmdc.202200291-table1-r3-c4-MIC', 'endpoint': 'MIC', 'entity': '[d] μg/mL hRBC', 'raw_value': '>200', 'raw_unit': 'μg/mL', 'target_species': 'A1'}, {'record_id': 'doi__10.1002_cmdc.202200291-table1-r3-c5-MIC', 'endpoint': 'MIC', 'entity': 'CD[e] PAO1', 'raw_value': '8', 'raw_unit': 'μM', 'target_species': 'A1'}, {'record_id': 'doi__10.1002_cmdc.202200291-table1-r3-c6-MIC', 'endpoint': 'MIC', 'entity': '% Vesicle leakage[f] A. baumannii', 'raw_value': '8', 'raw_unit': '%', 'target_species': 'A1'}, {'record_id': 'doi__10.1002_cmdc.202200291-table1-r3-c7-MIC', 'endpoint': 'MIC', 'entity': '% α‐helix', 'raw_value': '72', 'raw_unit': '%', 'target_species': 'A1'}, {'record_id': 'doi__10.1002_cmdc.202200291-table1-r3-c8-MIC', 'endpoint': 'MIC', 'entity': 'PC', 'raw_value': '79', 'raw_unit': 'μM', 'target_species': 'A1'}]`
- Real reasons:
  - review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
  - activity parser quality issue: some extracted rows use peptide IDs/method labels/properties as target species or MIC rows, so row-level activity needs repair before acceptance
  - database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
  - material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion

## doi__10.1002_gch2.202200213
- Title: A Discovery from a Computational Peptide Library, In Silico Anticancer Peptide Screening and In Vitro Experimental Validation
- Source root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1002_gch2.202200213`
- Material inventory: `{'package_files': 1, 'pdf_files': 1, 'supplementary_files': 2, 'xml_files': 1}`
- Extraction counts: `{'xml_section_count': 35, 'xml_table_count': 2, 'figure_caption_count': 5, 'package_member_count': 15, 'supplementary_asset_count': 2, 'supplement_parse_count': 2, 'supplementary_table_count': 0, 'quality_status': 'complete_with_targeted_analysis_rework'}`
- Semantic issue groups: `{'review:review_status_not_publication_grade': 1, 'review:publication_grade_not_true': 1, 'activity:missing_activity_records': 1}`
- Publication risk counts: `{'open_rework_targets': 1}`
- DB status summary: `{'source_conflict': 2, 'source_verified': 1}`
- Activity records: 0; activity sanity issues: 0; mechanism claims: 3
- Real reasons:
  - review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
  - activity extraction gap: current final has zero activity records; likely activity is in figures/prose/supplement rather than parser-supported XML table shape
  - database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
  - material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion

## doi__10.1002_anie.201901589
- Title: Synthetic Lugdunin Analogues Reveal Essential Structural Motifs for Antimicrobial Action and Proton Translocation Capability.
- Source root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1002_anie.201901589`
- Material inventory: `{'package_files': 1, 'pdf_files': 1, 'supplementary_files': 1, 'xml_files': 2}`
- Extraction counts: `{'xml_section_count': 2, 'xml_table_count': 1, 'figure_caption_count': 6, 'package_member_count': 16, 'supplementary_asset_count': 1, 'supplement_parse_count': 1, 'supplementary_table_count': 0, 'quality_status': 'complete_with_targeted_analysis_rework'}`
- Semantic issue groups: `{'review:review_status_not_publication_grade': 1, 'review:publication_grade_not_true': 1, 'activity:missing_activity_records': 1}`
- Publication risk counts: `{'open_rework_targets': 1}`
- DB status summary: `{'database_only_no_primary_source': 10, 'source_conflict': 76, 'source_verified': 24}`
- Activity records: 0; activity sanity issues: 0; mechanism claims: 1
- Real reasons:
  - review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
  - activity extraction gap: source tables/prose expose activity endpoints but current parser produced zero activity records
  - database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
  - material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion

## doi__10.1002_advs.202507457
- Title: Controllable Generation of Pathogen-Specific Antimicrobial Peptides Through Knowledge-Aware Prompt Diffusion Model.
- Source root: `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1002_advs.202507457`
- Material inventory: `{'package_files': 2, 'pdf_files': 1, 'supplementary_files': 2, 'xml_files': 2}`
- Extraction counts: `{'xml_section_count': 18, 'xml_table_count': 1, 'figure_caption_count': 6, 'package_member_count': 34, 'supplementary_asset_count': 2, 'supplement_parse_count': 2, 'supplementary_table_count': 0, 'quality_status': 'complete_with_targeted_analysis_rework'}`
- Semantic issue groups: `{'review:review_status_not_publication_grade': 1, 'review:publication_grade_not_true': 1}`
- Publication risk counts: `{'open_rework_targets': 1}`
- DB status summary: `{'database_only_no_primary_source': 4, 'source_conflict': 60, 'source_verified': 14}`
- Activity records: 102; activity sanity issues: 102; mechanism claims: 1
- Activity sanity examples: `[{'record_id': 'doi__10.1002_advs.202507457-table1-r4-c2-MIC', 'endpoint': 'MIC', 'entity': 'Instability ↓', 'raw_value': '48.96', 'raw_unit': 'not_reported_in_header', 'target_species': 'Positive‐only learning'}, {'record_id': 'doi__10.1002_advs.202507457-table1-r4-c3-MIC', 'endpoint': 'MIC', 'entity': 'TM_tend ↓', 'raw_value': '57.33', 'raw_unit': 'not_reported_in_header', 'target_species': 'Positive‐only learning'}, {'record_id': 'doi__10.1002_advs.202507457-table1-r4-c4-MIC', 'endpoint': 'MIC', 'entity': 'Physicochemical property Charge', 'raw_value': '51.03', 'raw_unit': 'not_reported_in_header', 'target_species': 'Positive‐only learning'}, {'record_id': 'doi__10.1002_advs.202507457-table1-r4-c5-MIC', 'endpoint': 'MIC', 'entity': 'Isoelectric', 'raw_value': '53.77', 'raw_unit': 'not_reported_in_header', 'target_species': 'Positive‐only learning'}, {'record_id': 'doi__10.1002_advs.202507457-table1-r4-c6-MIC', 'endpoint': 'MIC', 'entity': 'Hydrophobic', 'raw_value': '0.694', 'raw_unit': 'not_reported_in_header', 'target_species': 'Positive‐only learning'}]`
- Real reasons:
  - review layer is deliberately not publication-grade: review_status=needs_targeted_rework, publication_grade=false, open rework ticket remains
  - activity parser quality issue: some extracted rows use peptide IDs/method labels/properties as target species or MIC rows, so row-level activity needs repair before acceptance
  - database adjudication still needs worker-6 decision: source_conflict/database-only rows are preserved but not publication-grade resolved
  - material packet is usable but marked complete_with_targeted_analysis_rework, not final source-reviewed completion

