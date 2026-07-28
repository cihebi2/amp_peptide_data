# AMP Evidence Atlas v1 RC1：数据库标注 vs 论文审查差异例子

生成时间：2026-06-22 10:34:20

本报告从 `releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv` 选择真实案例，
用于说明数据库原标注与 primary-literature source-reviewed 审查结果之间的差异类型。
它不是新一轮全文重审，也不把 non-source-verified 自动解释为数据库错误。

## 当前 release 口径

| 指标 | 数值 |
| --- | ---: |
| `paper_final_artifact_count` | 1471 |
| `public_v1_candidate_papers` | 1371 |
| `excluded_or_non_publication_grade_papers` | 100 |
| `database_audit_rows` | 139259 |
| `source_verified_rows` | 95941 |
| `non_source_verified_rows` | 43318 |
| `activity_records` | 115184 |
| `mechanism_claims` | 4772 |

## 选择和解释边界

- 只选择 `status != source_verified` 的记录作为差异案例。
- 每条案例都保留 `release_table_path` 和 `final_artifact_path`，便于复核。
- locator 只保留路径/定位信息，不复制论文全文、PDF、图片或补充材料原件。
- 一条记录可有多个差异标签；本报告为阅读方便给每条案例指定一个主展示类别。
- `source_conflict`、`database_only_no_primary_source`、`unresolved_record` 都不能被简单说成数据库错误。

## 当前非 source-verified 记录中的差异类别规模

| 类别 | 非 source-verified rows | 本报告例子数 |
| --- | ---: | ---: |
| `sequence_or_modification` / 序列/修饰/端基/构型 | 37131 | 3 |
| `activity_value_or_unit` / 活性数值/单位/endpoint | 42542 | 3 |
| `target_or_organism` / 靶标/物种/菌株粒度 | 15941 | 3 |
| `mechanism_or_claim_scope` / 机制标签/证据范围 | 1729 | 3 |
| `database_only_no_primary_source` / 数据库有断言但 primary source 不支持 | 7049 | 3 |
| `row_granularity` / 数据库行粒度 vs 论文行粒度 | 5231 | 3 |
| `unresolved_or_missing_material` / 材料缺失或仍无法判定 | 912 | 3 |

## 代表性例子

### 序列/修饰/端基/构型

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX016 | `doi__10.1002_cbic.202100151` | `DBAASP / DBAASP:DBAASPS_18493` | `source_conflict` | database=DBAASP; source_id=DBAASP:DBAASPS_18493; record_name=R4L S8L; subject=Horse erythrocytes; measure=0-10% Hemolysis | matched_activity=doi__10.1002_cbic.202100151:table3:R4L_S8L:no_hemolysis_threshold \| conflict_context: DBAASP peptide_name uses R4L,S4L while the primary paper consistently names and tests the variant as R4L S8L; activity values match the source table, but the variant label conflict is preserved. \| review_notes: Preserved as source_conflict for the database variant label typo; do not smooth to source_verified. \| seq... | 数据库的序列、变体名、修饰或端基信息与论文审查结果不能安全等同。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1002_cbic.202100151/final/database_record_verification.json |
| EX017 | `doi__10.1002_cbic.202100151` | `DBAASP / DBAASP:DBAASPS_18493` | `source_conflict` | database=DBAASP; source_id=DBAASP:DBAASPS_18493; record_name=R4L S8L; subject=Acinetobacter baumannii ATCC 19606; measure=MIC | conflict_context: DBAASP peptide_name uses R4L,S4L while the primary paper consistently names and tests the variant as R4L S8L; activity values match the source table, but the variant label conflict is preserved. \| review_notes: Preserved as source_conflict for the database variant label typo; do not smooth to source_verified. \| sequence_check: {"database_sequence": "", "primary_source_sequence": "", "primary_source... | 数据库的序列、变体名、修饰或端基信息与论文审查结果不能安全等同。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1002_cbic.202100151/final/database_record_verification.json |
| EX018 | `doi__10.1002_cbic.202100151` | `DBAASP / DBAASP:DBAASPS_18493` | `source_conflict` | database=DBAASP; source_id=DBAASP:DBAASPS_18493; record_name=R4L S8L; subject=Staphylococcus aureus ATCC 29213; measure=MIC | conflict_context: DBAASP peptide_name uses R4L,S4L while the primary paper consistently names and tests the variant as R4L S8L; activity values match the source table, but the variant label conflict is preserved. \| review_notes: Preserved as source_conflict for the database variant label typo; do not smooth to source_verified. \| sequence_check: {"database_sequence": "", "primary_source_sequence": "", "primary_source... | 数据库的序列、变体名、修饰或端基信息与论文审查结果不能安全等同。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1002_cbic.202100151/final/database_record_verification.json |

### 活性数值/单位/endpoint

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX019 | `doi__10.1002_cbic.202100151` | `DBAASP / DBAASP:DBAASPS_18493` | `source_conflict` | database=DBAASP; source_id=DBAASP:DBAASPS_18493; record_name=R4L S8L; subject=Staphylococcus aureus ATCC 6538; measure=MIC | conflict_context: DBAASP peptide_name uses R4L,S4L while the primary paper consistently names and tests the variant as R4L S8L; activity values match the source table, but the variant label conflict is preserved. \| review_notes: Preserved as source_conflict for the database variant label typo; do not smooth to source_verified. \| sequence_check: {"database_sequence": "", "primary_source_sequence": "", "primary_source... | 数据库的活性 endpoint、数值、单位或阈值与论文行级证据存在差异或需要保留 caution。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1002_cbic.202100151/final/database_record_verification.json |
| EX020 | `doi__10.1007_s12602-025-10542-1` | `DBAASP / DBAASPR_23863` | `sequence_modified_not_normalized` | database=DBAASP; source_id=DBAASPR_23863; record_name=Bombinin-like peptide 7S, BLP-7S; sequence=SIGGALLSAGKSALKGLAKGLAEHFAN | primary_sequence=SIGGALLSAGKSALKGLAKGLAEHFAN-NH2 \| conflict_context: Primary table includes a C-terminal amidation marker while the database sequence row stores only the amino-acid core; preserve as sequence_modified_not_normalized. \| review_notes: Primary Table 1 and merged sequence/literature rows support identity; terminal-amidation normalization caveat preserved where applicable. \| sequence_check: {"conflict_fla... | 数据库的活性 endpoint、数值、单位或阈值与论文行级证据存在差异或需要保留 caution。 当前状态为 `sequence_modified_not_normalized`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1007_s12602-025-10542-1/final/database_record_verification.json |
| EX021 | `doi__10.1007_s12602-025-10542-1` | `DBAASP / DBAASPR_23863` | `sequence_modified_not_normalized` | database=DBAASP; source_id=DBAASPR_23863; record_name=Bombinin-like peptide 7S, BLP-7S; subject=Staphylococcus aureus NCTC 12493; measure=MIC; value=4; unit=µM | matched_activity=doi__10.1007_s12602-025-10542-1:xml:table_3:row_3:column_2:blp7s:MIC \| conflict_context: Activity value is source-matched; sequence identity carries terminal-amidation normalization caveat from Table 1. \| review_notes: Database assay value and target matched a primary-source activity/toxicity record. \| sequence_check: {"conflict_flags": ["primary_table_reports_C_terminal_NH2_but_database_sequence_fi... | 数据库的活性 endpoint、数值、单位或阈值与论文行级证据存在差异或需要保留 caution。 当前状态为 `sequence_modified_not_normalized`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1007_s12602-025-10542-1/final/database_record_verification.json |

### 靶标/物种/菌株粒度

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX013 | `doi__10.1007_s12602-025-10542-1` | `DBAASP / DBAASPR_23863` | `source_conflict` | database=DBAASP; source_id=DBAASPR_23863; record_name=Bombinin-like peptide 7S, BLP-7S; subject=Horse erythrocytes; measure=50% Hemolysis; value=111.9; unit=µM | conflict_context: Database assay row could not be matched to a primary-source row with the same peptide, endpoint, target, and value; preserve as source_conflict rather than fabricating a value. \| review_notes: Database assay row could not be matched to a primary-source row with the same peptide, endpoint, target, and value; preserve as source_conflict rather than fabricating a value. \| sequence_check: {"conflict_fl... | 数据库的物种、菌株、分离株、细胞系或对象粒度与论文证据不完全一致。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1007_s12602-025-10542-1/final/database_record_verification.json |
| EX014 | `doi__10.1007_s12602-025-10542-1` | `DBAASP / DBAASPR_23863` | `sequence_modified_not_normalized` | database=DBAASP; source_id=DBAASPR_23863; record_name=Bombinin-like peptide 7S, BLP-7S; subject=Staphylococcus aureus ATCC 6538; measure=MIC; value=8; unit=µM | matched_activity=doi__10.1007_s12602-025-10542-1:xml:table_3:row_2:column_2:blp7s:MIC \| conflict_context: Activity value is source-matched; sequence identity carries terminal-amidation normalization caveat from Table 1. \| review_notes: Database assay value and target matched a primary-source activity/toxicity record. \| sequence_check: {"conflict_flags": ["primary_table_reports_C_terminal_NH2_but_database_sequence_fi... | 数据库的物种、菌株、分离株、细胞系或对象粒度与论文证据不完全一致。 当前状态为 `sequence_modified_not_normalized`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1007_s12602-025-10542-1/final/database_record_verification.json |
| EX015 | `doi__10.1007_s12602-025-10542-1` | `DBAASP / DBAASPR_23863` | `sequence_modified_not_normalized` | database=DBAASP; source_id=DBAASPR_23863; record_name=Bombinin-like peptide 7S, BLP-7S; subject=Staphylococcus aureus ATCC 6538; measure=MBC; value=8; unit=µM | matched_activity=doi__10.1007_s12602-025-10542-1:xml:table_3:row_2:column_2:blp7s:MBC \| conflict_context: Activity value is source-matched; sequence identity carries terminal-amidation normalization caveat from Table 1. \| review_notes: Database assay value and target matched a primary-source activity/toxicity record. \| sequence_check: {"conflict_flags": ["primary_table_reports_C_terminal_NH2_but_database_sequence_fi... | 数据库的物种、菌株、分离株、细胞系或对象粒度与论文证据不完全一致。 当前状态为 `sequence_modified_not_normalized`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1007_s12602-025-10542-1/final/database_record_verification.json |

### 机制标签/证据范围

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX007 | `doi__10.3389_fmicb.2017.00051` | `APD6 / APD6:AP02787` | `source_conflict` | database=APD6; source_id=APD6:AP02787; subject=Comparative Analysis of the Bacterial Membrane Disruption Effect of Two Natural Plant Antimicrobial Peptides.; measure=Unknown | matched_activity=doi__10.3389_fmicb.2017.00051-table3-ncr247-salmonella_enterica-mic,doi__10.3389_fmicb.2017.00051-table3-ncr247-listeri... \| conflict_context: source_conflict: APD6 row partly matches NCR247 MIC values in Table 3, but its Candida claims are not supported by local XML/PDF for this paper and are preserved as database-only claims. \| review_notes: source_conflict: APD6 row partly matches NCR247 MIC valu... | 数据库或记录层面的功能/机制标签宽于、窄于或不同于论文中的直接机制证据。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3389_fmicb.2017.00051/final/database_record_verification.json |
| EX008 | `doi__10.1007_s00018-022-04440-w` | `DBAASP / DBAASP:DBAASPS_22793` | `source_conflict` | database=DBAASP; source_id=DBAASP:DBAASPS_22793; record_name=CD4-PP; subject=Escherichia coli CFT073; measure=MBIC; unit=µM | matched_activity=doi__10.1007_s00018-022-04440-w:biofilm_prevention:e_coli_cft073 \| conflict_context: source_conflict: primary source supports 10 µM CD4-PP biofilm prevention, but the database MBIC/MBIC50 endpoint label is not stated as an exact threshold term in the paper. \| review_notes: Value and target are source-supported as treatment conditions; endpoint label remains a database normalization caution. \| sequen... | 数据库或记录层面的功能/机制标签宽于、窄于或不同于论文中的直接机制证据。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1007_s00018-022-04440-w/final/database_record_verification.json |
| EX009 | `doi__10.1007_s00018-022-04440-w` | `DBAASP / DBAASP:DBAASPS_22793` | `source_conflict` | database=DBAASP; source_id=DBAASP:DBAASPS_22793; record_name=CD4-PP; subject=Pseudomonas aeruginosa ATCC 27853; measure=MBIC50; unit=µM | matched_activity=doi__10.1007_s00018-022-04440-w:biofilm_prevention:p_aeruginosa_atcc27853 \| conflict_context: source_conflict: primary source supports 10 µM CD4-PP biofilm prevention, but the database MBIC/MBIC50 endpoint label is not stated as an exact threshold term in the paper. \| review_notes: Value and target are source-supported as treatment conditions; endpoint label remains a database normalization caution.... | 数据库或记录层面的功能/机制标签宽于、窄于或不同于论文中的直接机制证据。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1007_s00018-022-04440-w/final/database_record_verification.json |

### 数据库有断言但 primary source 不支持

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX004 | `doi__10.3390_antibiotics11010076` | `DBAASP / DBAASP:DBAASPR_919` | `database_only_no_primary_source` | database=DBAASP; source_id=DBAASP:DBAASPR_919; subject=Klebsiella pneumoniae; measure=MIC; unit=µg/ml | conflict_context: database-only row retained as provenance, not promoted to a primary-source assay row. \| review_notes: Database row is linked to this paper but does not provide a record-level activity value; primary XML activity is preserved separately. \| sequence_check: {"peptide": "hBD-3", "source_locator": {"locator": "xml:table=1:row=2", "primary_source_statement": "Table 1 provides peptide sequence and physico... | 数据库断言无法在当前 primary source 中定位支持。 当前状态为 `database_only_no_primary_source`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3390_antibiotics11010076/final/database_record_verification.json |
| EX005 | `doi__10.3390_antibiotics11010076` | `DBAASP / DBAASP:DBAASPR_919` | `database_only_no_primary_source` | database=DBAASP; source_id=DBAASP:DBAASPR_919; subject=Klebsiella pneumoniae CR; measure=MIC; unit=µg/ml | conflict_context: database-only row retained as provenance, not promoted to a primary-source assay row. \| review_notes: Database row is linked to this paper but does not provide a record-level activity value; primary XML activity is preserved separately. \| sequence_check: {"peptide": "hBD-3", "source_locator": {"locator": "xml:table=1:row=2", "primary_source_statement": "Table 1 provides peptide sequence and physico... | 数据库断言无法在当前 primary source 中定位支持。 当前状态为 `database_only_no_primary_source`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3390_antibiotics11010076/final/database_record_verification.json |
| EX006 | `doi__10.3390_antibiotics11010076` | `DBAASP / DBAASP:DBAASPR_919` | `database_only_no_primary_source` | database=DBAASP; source_id=DBAASP:DBAASPR_919; subject=Klebsiella aerogenes; measure=MIC; unit=µg/ml | conflict_context: database-only row retained as provenance, not promoted to a primary-source assay row. \| review_notes: Database row is linked to this paper but does not provide a record-level activity value; primary XML activity is preserved separately. \| sequence_check: {"peptide": "hBD-3", "source_locator": {"locator": "xml:table=1:row=2", "primary_source_statement": "Table 1 provides peptide sequence and physico... | 数据库断言无法在当前 primary source 中定位支持。 当前状态为 `database_only_no_primary_source`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3390_antibiotics11010076/final/database_record_verification.json |

### 数据库行粒度 vs 论文行粒度

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX010 | `doi__10.1038_srep09761` | `DBAASP / DBAASPS_10050` | `source_conflict` | database=DBAASP; source_id=DBAASPS_10050; subject=Streptococcus pneumoniae; measure=MIC | conflict_context: DBAASP FIC row links to Table 4 but lacks the partner peptide and/or PRSP/PISP/PSSP group needed for exact row-level promotion. \| review_notes: DBAASP FIC row links to Table 4 but lacks the partner peptide and/or PRSP/PISP/PSSP group needed for exact row-level promotion. \| sequence_check: {"agreement": "sequence_letters_match_primary_source; terminal_amidation_not_normalized_in_snapshot", "database... | 数据库把论文多行、多个 isolate 或多个条件压缩为单行/范围/文本摘要。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1038_srep09761/final/database_record_verification.json |
| EX011 | `doi__10.1038_srep09761` | `DBAASP / DBAASPS_10050` | `source_conflict` | database=DBAASP; source_id=DBAASPS_10050; subject=Streptococcus pneumoniae; measure=MIC | conflict_context: DBAASP FIC row links to Table 4 but lacks the partner peptide and/or PRSP/PISP/PSSP group needed for exact row-level promotion. \| review_notes: DBAASP FIC row links to Table 4 but lacks the partner peptide and/or PRSP/PISP/PSSP group needed for exact row-level promotion. \| sequence_check: {"agreement": "sequence_letters_match_primary_source; terminal_amidation_not_normalized_in_snapshot", "database... | 数据库把论文多行、多个 isolate 或多个条件压缩为单行/范围/文本摘要。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1038_srep09761/final/database_record_verification.json |
| EX012 | `doi__10.1038_srep09761` | `DBAASP / DBAASPS_10050` | `source_conflict` | database=DBAASP; source_id=DBAASPS_10050; subject=Streptococcus pneumoniae; measure=MIC | conflict_context: DBAASP FIC row links to Table 4 but lacks the partner peptide and/or PRSP/PISP/PSSP group needed for exact row-level promotion. \| review_notes: DBAASP FIC row links to Table 4 but lacks the partner peptide and/or PRSP/PISP/PSSP group needed for exact row-level promotion. \| sequence_check: {"agreement": "sequence_letters_match_primary_source; terminal_amidation_not_normalized_in_snapshot", "database... | 数据库把论文多行、多个 isolate 或多个条件压缩为单行/范围/文本摘要。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1038_srep09761/final/database_record_verification.json |

### 材料缺失或仍无法判定

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX001 | `doi__10.1038_s41598-017-16784-6` | `DBAASP / DBAASPR_3442` | `unresolved_record` | database=DBAASP; source_id=DBAASPR_3442; subject=Staphylococcus aureus 547582; measure=MIC | conflict_context: The current paper text routes these checkerboard MIC/FICI values to Tables S1/S2, but the local packet lacks the MOESM1 PDF that should contain those supplement tables. \| review_notes: The current paper text routes these checkerboard MIC/FICI values to Tables S1/S2, but the local packet lacks the MOESM1 PDF that should contain those supplement tables. \| sequence_check: {"database_sequence": "", "mo... | 关键补充材料、图表精确值或行级映射不足，当前不能安全判定。 当前状态为 `unresolved_record`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1038_s41598-017-16784-6/final/database_record_verification.json |
| EX002 | `doi__10.1038_s41598-017-16784-6` | `DBAASP / DBAASPR_3442` | `unresolved_record` | database=DBAASP; source_id=DBAASPR_3442; subject=Staphylococcus aureus 547582; measure=MIC | conflict_context: The current paper text routes these checkerboard MIC/FICI values to Tables S1/S2, but the local packet lacks the MOESM1 PDF that should contain those supplement tables. \| review_notes: The current paper text routes these checkerboard MIC/FICI values to Tables S1/S2, but the local packet lacks the MOESM1 PDF that should contain those supplement tables. \| sequence_check: {"database_sequence": "", "mo... | 关键补充材料、图表精确值或行级映射不足，当前不能安全判定。 当前状态为 `unresolved_record`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1038_s41598-017-16784-6/final/database_record_verification.json |
| EX003 | `doi__10.1038_s41598-017-16784-6` | `DBAASP / DBAASPR_3442` | `unresolved_record` | database=DBAASP; source_id=DBAASPR_3442; subject=Staphylococcus aureus 547582; measure=MIC | conflict_context: The current paper text routes these checkerboard MIC/FICI values to Tables S1/S2, but the local packet lacks the MOESM1 PDF that should contain those supplement tables. \| review_notes: The current paper text routes these checkerboard MIC/FICI values to Tables S1/S2, but the local packet lacks the MOESM1 PDF that should contain those supplement tables. \| sequence_check: {"database_sequence": "", "mo... | 关键补充材料、图表精确值或行级映射不足，当前不能安全判定。 当前状态为 `unresolved_record`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1038_s41598-017-16784-6/final/database_record_verification.json |

## 可用于论文写作的谨慎表述

可以说：

> The resource preserves source-verified records separately from evidence discordance, provenance gaps, modification-normalization issues, database-only assertions, and unresolved records.

不应说：

- “所有 non-source-verified 记录都是数据库错误”；
- “accepted_with_cautions 等于 clean”；
- “数据库行数等于各数据库原始全库分母”；
- “缺失材料的图表精确值已经被补齐”。
