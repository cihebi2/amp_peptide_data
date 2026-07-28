# AMP Evidence Atlas v1 RC1：数据库标注 vs 论文审查差异例子

生成时间：2026-06-22 10:35:19

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
| EX001 | `doi__10.1002_cbic.202100151` | `DBAASP / DBAASP:DBAASPS_18493` | `source_conflict` | database=DBAASP; source_id=DBAASP:DBAASPS_18493; record_name=R4L S8L; subject=Horse erythrocytes; measure=0-10% Hemolysis | matched_activity=doi__10.1002_cbic.202100151:table3:R4L_S8L:no_hemolysis_threshold \| conflict_context: DBAASP peptide_name uses R4L,S4L while the primary paper consistently names and tests the variant as R4L S8L; activity values match the source table, but the variant label conflict is preserved. \| review_notes: Preserved as source_conflict for the database variant label typo; do not smooth to source_verified. \| seq... | 数据库的序列、变体名、修饰或端基信息与论文审查结果不能安全等同。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1002_cbic.202100151/final/database_record_verification.json |
| EX002 | `doi__10.1002_advs.202507457` | `APD6 / APD6:AP05698` | `source_conflict` | database=APD6; source_id=APD6:AP05698; subject=Controllable Generation of Pathogen-Specific Antimicrobial Peptides Through Knowledge-Aware Prompt Diffusion Model.; measure=Sequence analysis: APD analysis reveals that this sequence is similar (42.11%) to synthetic CGS9. W: 17%, R: 28%. Activ... | matched_activity=doi__10.1002_advs.202507457:figure6b:Pep9:escherichia_coli:MIC;doi__10.1002_advs.202507457:figure6b:Pep9:staphylococcus... \| conflict_context: APD6 AP05698 sequence letters match primary Pep9, but APD6 sequence_length is 18 while the sequence and DBAASP primary row are 19 residues; preserve length-field conflict. \| review_notes: APD6 AP05698 sequence letters match primary Pep9, but APD6 sequence_len... | 数据库的序列、变体名、修饰或端基信息与论文审查结果不能安全等同。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1002_advs.202507457/final/database_record_verification.json |
| EX003 | `doi__10.1002_advs.202507457` | `APD6 / APD6:AP05696` | `source_conflict` | database=APD6; source_id=APD6:AP05696; subject=Controllable Generation of Pathogen-Specific Antimicrobial Peptides Through Knowledge-Aware Prompt Diffusion Model.; measure=Sequence analysis: APD analysis reveals that this sequence is similar (41.67%) to synthetic CGS14. S: 14%, R: 29%. Acti... | matched_activity=doi__10.1002_advs.202507457:figure6b:Pep3:escherichia_coli:MIC;doi__10.1002_advs.202507457:figure6b:Pep3:staphylococcus... \| conflict_context: APD6 AP05696 is linked as Pep3 but its sequence has R at the position where primary Figure 6a/DBAASP Pep3 has P; activity text matches the paper but the APD6 sequence is not exact. \| review_notes: APD6 AP05696 is linked as Pep3 but its sequence has R at the p... | 数据库的序列、变体名、修饰或端基信息与论文审查结果不能安全等同。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1002_advs.202507457/final/database_record_verification.json |

### 活性数值/单位/endpoint

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX004 | `doi__10.3390_md16090290` | `DBAASP / DBAASP:DBAASPR_20074` | `source_conflict` | database=DBAASP; source_id=DBAASP:DBAASPR_20074; subject=Murine colon acarcinoma CT26; measure=IC50; value=12; unit=ug/ml | matched_activity=activity-nocardiotide-a-ic50-ct26 \| conflict_context: The primary XML/PDF reports the same IC50 numeric value and target but prints the unit as uM/mL, while DBAASP stores ug/ml. The row is therefore preserved as source_conflict rather than source_verified. \| review_notes: Numeric cytotoxicity value and cell-line target are source-supported; unit mismatch remains a nonblocking database conflict. \| se... | 数据库的活性 endpoint、数值、单位或阈值与论文行级证据存在差异或需要保留 caution。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3390_md16090290/final/database_record_verification.json |
| EX005 | `doi__10.3390_ijms22136679` | `DBAASP / DBAASP:DBAASPS_10746` | `sequence_modified_not_normalized` | database=DBAASP; source_id=DBAASP:DBAASPS_10746; subject=Human keratinocytes HaCat; measure=IC50; value=>50; unit=µg/ml | matched_activity=doi__10.3390_ijms22136679-table4-r3-c14-IC50 \| conflict_context: Primary activity value is matched, but the database sequence/name normalizes or omits N-terminal lipidation, PEG/carnosine, D-residue, or parent-compound details; preserved as a caution instead of silently normalizing. \| review_notes: Primary activity value is matched, but the database sequence/name normalizes or omits N-terminal lipid... | 数据库的活性 endpoint、数值、单位或阈值与论文行级证据存在差异或需要保留 caution。 当前状态为 `sequence_modified_not_normalized`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3390_ijms22136679/final/database_record_verification.json |
| EX006 | `doi__10.1007_s12539-016-0163-x` | `dbAMP / dbAMP:dbAMP_17886` | `source_conflict` | database=dbAMP; source_id=dbAMP:dbAMP_17886; subject=Candida tropicalis ATCC MYA-3404 (MIC=100.66 ± 0.95μg/ml) Candida tropicalis (MIC=127.37 ± 0.51μg/ml) Listeria monocyto...; measure=text | conflict_context: dbAMP dbAMP_17886 preserves the CGA-N12 sequence/title link, but its activity text lists organisms and ug/ml MIC values not found in the local primary XML/PDF Table 4 or methods. The paper-supported CGA-N12 Table 4 activity and HC5 rows ar... \| review_notes: Worker-4/6 preserve this dbAMP activity text as a database-source conflict while accepting the primary-source CGA-N12 Table 4 values. \| sequen... | 数据库的活性 endpoint、数值、单位或阈值与论文行级证据存在差异或需要保留 caution。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1007_s12539-016-0163-x/final/database_record_verification.json |

### 靶标/物种/菌株粒度

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX007 | `doi__10.1007_s12602-025-10542-1` | `DBAASP / DBAASPR_23863` | `source_conflict` | database=DBAASP; source_id=DBAASPR_23863; record_name=Bombinin-like peptide 7S, BLP-7S; subject=Horse erythrocytes; measure=50% Hemolysis; value=111.9; unit=µM | conflict_context: Database assay row could not be matched to a primary-source row with the same peptide, endpoint, target, and value; preserve as source_conflict rather than fabricating a value. \| review_notes: Database assay row could not be matched to a primary-source row with the same peptide, endpoint, target, and value; preserve as source_conflict rather than fabricating a value. \| sequence_check: {"conflict_fl... | 数据库的物种、菌株、分离株、细胞系或对象粒度与论文证据不完全一致。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1007_s12602-025-10542-1/final/database_record_verification.json |
| EX008 | `doi__10.3389_fmicb.2016.01801` | `DBAASP / DBAASPS_9765` | `source_conflict` | database=DBAASP; source_id=DBAASPS_9765; subject=Penicillium chrysogenum AS3.4356; measure=MIC | matched_activity=doi__10.3389_fmicb.2016.01801-table2-r5-linear_heptapeptide-MIC \| conflict_context: conflict: database target is Penicillium chrysogenum AS3.4356, while local primary XML Table 2 and supplementary Fig. S7 support Penicillium notatum AS3.4356 for the matching value/strain context. \| review_notes: Numeric MIC value and strain context are recoverable, but the database target species name conflicts with... | 数据库的物种、菌株、分离株、细胞系或对象粒度与论文证据不完全一致。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3389_fmicb.2016.01801/final/database_record_verification.json |
| EX009 | `doi__10.1021_acsomega.0c00442` | `DBAASP / DBAASPS_22113` | `source_conflict` | database=DBAASP; source_id=DBAASPS_22113; subject=Staphylococcus aureus ATCC 12600; measure=EC50; value=16.6; unit=µg/ml | matched_activity=doi__10.1021_acsomega.0c00442-tables3-DBAASPS_22113-3-EC50 \| conflict_context: database_value=16.6 µg/ml; primary_source_value=16.5 µg/mL; source table retained as primary evidence \| review_notes: Conflict preserved: database EC50 value does not exactly match the primary supplemental EC50 table for the same peptide and target. \| sequence_check: {"name": "SP3", "primary_sequence": "WKRLRWRRFF", "sequ... | 数据库的物种、菌株、分离株、细胞系或对象粒度与论文证据不完全一致。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1021_acsomega.0c00442/final/database_record_verification.json |

### 机制标签/证据范围

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX010 | `doi__10.1007_s00018-022-04440-w` | `DBAASP / DBAASP:DBAASPS_22793` | `source_conflict` | database=DBAASP; source_id=DBAASP:DBAASPS_22793; record_name=CD4-PP; subject=Escherichia coli CFT073; measure=MBIC; unit=µM | matched_activity=doi__10.1007_s00018-022-04440-w:biofilm_prevention:e_coli_cft073 \| conflict_context: source_conflict: primary source supports 10 µM CD4-PP biofilm prevention, but the database MBIC/MBIC50 endpoint label is not stated as an exact threshold term in the paper. \| review_notes: Value and target are source-supported as treatment conditions; endpoint label remains a database normalization caution. \| sequen... | 数据库或记录层面的功能/机制标签宽于、窄于或不同于论文中的直接机制证据。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1007_s00018-022-04440-w/final/database_record_verification.json |
| EX011 | `doi__10.1016_j.isci.2024.110404` | `APD6 / APD6:AP04731` | `source_conflict` | database=APD6; source_id=APD6:AP04731; sequence=KIGQKIKNFFRKLL; subject=TC-14 (TC-33 analog, synthetic AMPs, Lys-rich, XXA, UCLL1c; BBMm); measure=APD6 entry-text MIC claims mostly match primary Table 2, but S. aureus ATCC6538 is listed as 4.68 μg/mL in APD6 versus ... | primary_sequence=KIGQKIKNFFRKLL-NH2 \| conflict_context: APD6 TC-14 row is source-linked and mostly source-supported, but it rounds/transcribes the S. aureus Table 2 MIC as 4.68 rather than 4.69 μg/mL and says S. aureus did not become resistant after 60 generations despite primary text reporting... \| review_notes: Keep APD6 as source_conflict for the discrepant S. aureus MIC/resistance wording while preserving source... | 数据库或记录层面的功能/机制标签宽于、窄于或不同于论文中的直接机制证据。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1016_j.isci.2024.110404/final/database_record_verification.json |
| EX012 | `doi__10.1021_acsinfecdis.4c00130` | `DBAASP / DBAASPS_1023` | `source_conflict` | database=DBAASP; source_id=DBAASPS_1023; subject=Staphylococcus aureus; measure=MBEC50; value=75; unit=µM | primary_subject=S. aureus #4 biofilm \| conflict_context: DBAASP reports MBEC50=75 μM for a generic S. aureus biofilm row, but the primary paper only provides Figure 1 bars for S. aureus #4 and does not tabulate a 75 μM endpoint. The database-only interpolated value is preserved as source_conflic... \| review_notes: DBAASP reports MBEC50=75 μM for a generic S. aureus biofilm row, but the primary paper only provides Fi... | 数据库或记录层面的功能/机制标签宽于、窄于或不同于论文中的直接机制证据。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1021_acsinfecdis.4c00130/final/database_record_verification.json |

### 数据库有断言但 primary source 不支持

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX013 | `doi__10.3390_antibiotics11010076` | `DBAASP / DBAASP:DBAASPR_919` | `database_only_no_primary_source` | database=DBAASP; source_id=DBAASP:DBAASPR_919; subject=Klebsiella pneumoniae; measure=MIC; unit=µg/ml | conflict_context: database-only row retained as provenance, not promoted to a primary-source assay row. \| review_notes: Database row is linked to this paper but does not provide a record-level activity value; primary XML activity is preserved separately. \| sequence_check: {"peptide": "hBD-3", "source_locator": {"locator": "xml:table=1:row=2", "source_path": "papers/doi__10.3390_antibiotics11010076/source/paper.xml"}} | 数据库断言无法在当前 primary source 中定位支持。 当前状态为 `database_only_no_primary_source`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3390_antibiotics11010076/final/database_record_verification.json |
| EX014 | `doi__10.3389_fmicb.2017.00051` | `APD6 / APD6:AP02787` | `source_conflict` | database=APD6; source_id=APD6:AP02787; subject=Comparative Analysis of the Bacterial Membrane Disruption Effect of Two Natural Plant Antimicrobial Peptides.; measure=Unknown | matched_activity=doi__10.3389_fmicb.2017.00051-table3-ncr247-salmonella_enterica-mic,doi__10.3389_fmicb.2017.00051-table3-ncr247-listeri... \| conflict_context: source_conflict: APD6 row partly matches NCR247 MIC values in Table 3, but its Candida claims are not supported by local XML/PDF for this paper and are preserved as database-only claims. \| review_notes: source_conflict: APD6 row partly matches NCR247 MIC valu... | 数据库断言无法在当前 primary source 中定位支持。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3389_fmicb.2017.00051/final/database_record_verification.json |
| EX015 | `doi__10.3389_fmicb.2018.00329` | `dbAMP / dbAMP_03323` | `database_only_no_primary_source` | database=dbAMP; source_id=dbAMP_03323; subject=Bacillus cereus (MIC=>100μg/ml) Escherichia coli (MIC=>100μg/ml) Leuconostoc lactis (MIC=50μg/ml) Listeria innocua (MIC...; measure=text | conflict_context: dbAMP row is a Maculatin/frog peptide entry that carries PMID 29551999 in a mixed reference list but does not match any peptide in Table 2; preserved as database-only contamination rather than merged into this paper. \| review_notes: dbAMP row is a Maculatin/frog peptide entry that carries PMID 29551999 in a mixed reference list but does not match any peptide in Table 2; preserved as database-only c... | 数据库断言无法在当前 primary source 中定位支持。 当前状态为 `database_only_no_primary_source`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3389_fmicb.2018.00329/final/database_record_verification.json |

### 数据库行粒度 vs 论文行粒度

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX016 | `doi__10.1038_srep09761` | `DBAASP / DBAASPS_10050` | `source_conflict` | database=DBAASP; source_id=DBAASPS_10050; subject=Streptococcus pneumoniae; measure=MIC | conflict_context: DBAASP FIC row links to Table 4 but lacks the partner peptide and/or PRSP/PISP/PSSP group needed for exact row-level promotion. \| review_notes: DBAASP FIC row links to Table 4 but lacks the partner peptide and/or PRSP/PISP/PSSP group needed for exact row-level promotion. \| sequence_check: {"agreement": "sequence_letters_match_primary_source; terminal_amidation_not_normalized_in_snapshot", "database... | 数据库把论文多行、多个 isolate 或多个条件压缩为单行/范围/文本摘要。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1038_srep09761/final/database_record_verification.json |
| EX017 | `doi__10.1038_s41586-019-1791-1` | `DBAASP / DBAASP:DBAASPR_17389` | `source_conflict` | database=DBAASP; source_id=DBAASP:DBAASPR_17389; subject=Escherichia coli; measure=MIC; value=2; unit=µg/ml | matched_activity=doi__10.1038_s41586-019-1791-1-supptable1-e-coli-1042752-dar-mic \| conflict_context: Database row collapses clinical-isolate data to MIC 2 ug/mL and notes 8 clinical isolates, while local Supplementary Table 1 lists 10 E. coli isolates with darobactin MIC values of 1-2 ug/mL. Individual source values are retained in final ... \| review_notes: Database row collapses clinical-isolate data to MIC 2 ug/m... | 数据库把论文多行、多个 isolate 或多个条件压缩为单行/范围/文本摘要。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1038_s41586-019-1791-1/final/database_record_verification.json |
| EX018 | `doi__10.3892_mmr.2017.7418` | `DRAMP / DRAMP35619` | `source_conflict` | database=DRAMP; source_id=DRAMP35619; subject=Not available; measure=Antimicrobial, Anticancer | conflict_context: Primary article supports anticancer/prostate-cell activity for SCH-P9/SCH-P10 but does not report antimicrobial assays; DRAMP aggregate antimicrobial/synthetic labels are preserved as database conflicts. \| review_notes: Sequence/name are source-supported, but the DRAMP activity/source annotation is broader than the paper-local evidence and remains a caution. \| sequence_check: {"modification_check":... | 数据库把论文多行、多个 isolate 或多个条件压缩为单行/范围/文本摘要。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3892_mmr.2017.7418/final/database_record_verification.json |

### 材料缺失或仍无法判定

| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EX019 | `doi__10.1038_s41598-017-16784-6` | `DBAASP / DBAASPR_3442` | `unresolved_record` | database=DBAASP; source_id=DBAASPR_3442; subject=Staphylococcus aureus 547582; measure=MIC | conflict_context: The current paper text routes these checkerboard MIC/FICI values to Tables S1/S2, but the local packet lacks the MOESM1 PDF that should contain those supplement tables. \| review_notes: The current paper text routes these checkerboard MIC/FICI values to Tables S1/S2, but the local packet lacks the MOESM1 PDF that should contain those supplement tables. \| sequence_check: {"database_sequence": "", "mo... | 关键补充材料、图表精确值或行级映射不足，当前不能安全判定。 当前状态为 `unresolved_record`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1038_s41598-017-16784-6/final/database_record_verification.json |
| EX020 | `doi__10.1038_s41522-024-00637-y` | `DBAASP / DBAASP:DBAASPS_11338` | `unresolved_record` | database=DBAASP; source_id=DBAASP:DBAASPS_11338; subject=Pseudomonas aeruginosa LESB58; measure=MIC; fici=0.5 | conflict_context: DBAASP DJK-5 synergy rows do not identify the partner drug in the local snapshot. Some FICI values overlap Table 1, while additional values appear to require the missing supplementary table. \| review_notes: DBAASP DJK-5 synergy rows do not identify the partner drug in the local snapshot. Some FICI values overlap Table 1, while additional values appear to require the missing supplementary table. \| s... | 关键补充材料、图表精确值或行级映射不足，当前不能安全判定。 当前状态为 `unresolved_record`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.1038_s41522-024-00637-y/final/database_record_verification.json |
| EX021 | `doi__10.3389_fmicb.2019.02740` | `DBAASP / DBAASPS_1728` | `source_conflict` | database=DBAASP; source_id=DBAASPS_1728; subject=Pseudomonas aeruginosa 910; measure=FIC | primary_value=0.5 \| matched_activity=doi__10.3389_fmicb.2019.02740-table4-s-w33-pmb-fic-pa910 \| conflict_context: Conflict: DBAASP row has blank peptide_name/identity snapshot for source_id DBAASPS_1728; values match the source paper S-W33 row but identity is preserved as unresolved database metadata. \| review_notes: DBAASP synergy FIC matches the primary paper FIC table for this peptide/antibiotic/strain. Value evi... | 关键补充材料、图表精确值或行级映射不足，当前不能安全判定。 当前状态为 `source_conflict`。 | releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv ; papers/doi__10.3389_fmicb.2019.02740/final/database_record_verification.json |

## 可用于论文写作的谨慎表述

可以说：

> The resource preserves source-verified records separately from evidence discordance, provenance gaps, modification-normalization issues, database-only assertions, and unresolved records.

不应说：

- “所有 non-source-verified 记录都是数据库错误”；
- “accepted_with_cautions 等于 clean”；
- “数据库行数等于各数据库原始全库分母”；
- “缺失材料的图表精确值已经被补齐”。
