# 文献证据 vs 原数据库信息冲突汇总

生成时间：2026-05-11T02:38:16Z

本报告聚合现有 worker-4/final database audit artifacts；不是新一轮人工重审。`source_verified` 以外的状态表示原数据库字段不能被当前本地文献证据完全支持。

## 总览

| 指标 | 数量 |
| --- | ---: |
| 论文范围 | 1472 |
| 数据库记录审计行 | 139259 |
| source_verified 记录 | 95239 |
| 非 source_verified / 冲突记录 | 44020 |
| 含冲突/非完全验证记录的论文 | 1304 |
| 缺 database audit artifact 的论文 | 1 |

## 按状态

| 状态 | 记录数 | 论文数 |
| --- | ---: | ---: |
| `source_conflict` | 33332 | 1215 |
| `sequence_modified_not_normalized` | 6382 | 186 |
| `database_only_no_primary_source` | 4250 | 268 |
| `unresolved_record` | 56 | 3 |

## 按冲突类别

| 类别 | 记录数 | 论文数 |
| --- | ---: | ---: |
| `activity_value_or_unit_conflict` | 43382 | 1297 |
| `citation_or_linkage_only` | 26161 | 960 |
| `sequence_or_modification_conflict` | 25373 | 893 |
| `figure_or_non_tabulated_quantification` | 16970 | 739 |
| `missing_material_or_supplement_gap` | 13147 | 424 |
| `organism_or_subject_conflict` | 9369 | 570 |
| `database_only_no_primary_source` | 4250 | 268 |
| `unresolved_record` | 56 | 3 |
| `other_source_conflict` | 21 | 2 |

## 按数据库来源

| 数据库 | 冲突记录数 | 涉及论文数 |
| --- | ---: | ---: |
| `DBAASP` | 34793 | 909 |
| `DRAMP` | 5323 | 373 |
| `CAMP` | 1825 | 479 |
| `dbAMP` | 1331 | 382 |
| `APD6` | 747 | 294 |
| `unknown` | 1 | 1 |

## 按 source_table

| source_table | 冲突记录数 | 涉及论文数 |
| --- | ---: | ---: |
| `linked_assay_records.jsonl` | 16411 | 849 |
| `linked_experiment_records.jsonl` | 14375 | 742 |
| `assay_refs.csv` | 6241 | 279 |
| `linked_dramp_activity_records.jsonl` | 1330 | 181 |
| `general_amps.txt` | 1108 | 167 |
| `camp_r4_export/data/sequences.csv` | 602 | 186 |
| `linked_literature_records.jsonl` | 562 | 95 |
| `data/dbamp3_detail_basic.csv` | 501 | 171 |
| `Antimicrobial_amps.txt` | 428 | 83 |
| `Antibacterial_amps.txt` | 250 | 50 |
| `peptides.csv` | 213 | 117 |
| `packet/database/linked_experiment_records.jsonl` | 190 | 7 |
| `Anti-Gram-_amps.txt` | 169 | 29 |
| `Antiviral_amps.txt` | 169 | 25 |
| `Anti-SARS-CoV-2_amps.txt` | 159 | 20 |
| `unknown` | 154 | 19 |
| `Anti-Gram-positive_amps.txt` | 146 | 36 |
| `linked_experiment_records` | 146 | 9 |
| `linked_assay_records` | 123 | 11 |
| `packet/database/linked_assay_records.jsonl` | 114 | 4 |

## 示例

### source_conflict

- `doi__10.3389_fmicb.2016.01682` / `DBAASP` / `DBAASPR_8298`：Activity fields agree with primary Figure 3/Table 2 at the claim level, but exact database row quantification/identity is database-derived and the paper does not provide a machine-readable source table for every value.
- `doi__10.3389_fmicb.2016.01801` / `DBAASP` / `DBAASPS_9765`：conflict: database target is Penicillium chrysogenum AS3.4356, while local primary XML Table 2 and supplementary Fig. S7 support Penicillium notatum AS3.4356 for the matching value/strain context.
- `doi__10.3389_fmicb.2016.01844` / `DBAASP` / `DBAASP:DBAASPR_3481`：Primary text/Figure 5 supports C. albicans biofilm inhibition and threshold concentrations, but the linked database MBEC/antibiofilm row is not fully reconstructible as an exact primary-source numeric row.
- `doi__10.3389_fmicb.2016.02006` / `DRAMP` / `DRAMP31983`：source_conflict: DRAMP aggregates antimicrobial/anticancer labels and uses a tumor-cell unit string that is not directly supported by the primary source; source-supported non-cytotoxicity and hemolysis are preserved as f...
- `doi__10.3389_fmicb.2017.00051` / `APD6` / `APD6:AP02787`：source_conflict: APD6 row partly matches NCR247 MIC values in Table 3, but its Candida claims are not supported by local XML/PDF for this paper and are preserved as database-only claims.

### database_only_no_primary_source

- `doi__10.3389_fmicb.2016.01682` / `APD6` / `AP02754`：Linked literature/entry row cites the paper but does not itself contain a primary-source-verifiable assay value in the local packet.
- `doi__10.3389_fmicb.2017.00774` / `DBAASP` / `DBAASP:DBAASPR_5278`：Exact sequence string is not printed in the current article; activity/name/citation are source-located in the paper, while exact comparator sequence is retained from local merged database catalogs. Preserved as a nonbloc...
- `doi__10.3389_fmicb.2018.00329` / `dbAMP` / `dbAMP_03323`：dbAMP row is a Maculatin/frog peptide entry that carries PMID 29551999 in a mixed reference list but does not match any peptide in Table 2; preserved as database-only contamination rather than merged into this paper.
- `doi__10.3389_fmicb.2018.02153` / `DRAMP` / `DRAMP:DRAMP29099`：database_only_no_primary_source conflict context: Database row could not be reduced to a paper-local primary-source row after bounded review; it is retained as database-only context and not promoted as a final source-sup...
- `doi__10.3389_fmicb.2018.02600` / `CAMP` / `CAMP:CAMPSQ11756`：CAMP row is a database-only summary without a linked sequence/literature snapshot in this packet; it is not promoted to a primary-source assay row.

### sequence_modified_not_normalized

- `doi__10.3389_fmicb.2016.01844` / `dbAMP` / `dbAMP:dbAMP_01777`：Primary Table 1 records C-terminal amidation for this peptide, while the linked database row stores the unmodified amino-acid string or omits modification metadata.
- `doi__10.3389_fmicb.2017.00994` / `DRAMP` / `DRAMP:DRAMP35617`：sequence_modified_not_normalized; primary_source_retro_inverso_d_amino_acid_peptide_vs_database_l_stereochemistry_representation
- `doi__10.3389_fmicb.2018.00325` / `DBAASP` / `DBAASP:DBAASPS_12378:DBAASPS_12378:20`：P1m assay value matches Table 2; identity is source-supported as Thr11Leu mutant but the full sequence is not printed as a standalone row.
- `doi__10.3389_fmicb.2018.00329` / `DBAASP` / `DBAASPS_10107`：Primary paper table verifies the reported activity value and identifies the peptide as a branched/Ahx-linked construct; sequence is intentionally not flattened into a linear unmodified sequence.
- `doi__10.3389_fmicb.2018.01440` / `dbAMP` / `dbAMP:dbAMP_27187`：dbAMP title lists a D-arginine 150-177/150-177 entry, while the primary-source modified lead peptide is D-150-177C with C-terminal cysteine in Figure 1 and Table 2; retained without normalization.

### unresolved_record

- `doi__10.21203_rs.3.rs-578319_v1` / `DBAASP` / `DBAASP:DBAASPS_17498`：DBAASP links this source_id to the paper, but local primary material only gives qualitative uperin/I13C/S11C activity text and the true Supplementary Table 5 PDF is not locally recoverable.
- `doi__10.1038_s41522-024-00637-y` / `DBAASP` / `DBAASP:DBAASPS_11338`：DBAASP DJK-5 synergy rows do not identify the partner drug in the local snapshot. Some FICI values overlap Table 1, while additional values appear to require the missing supplementary table.
- `doi__10.1038_s41598-017-16784-6` / `DBAASP` / `DBAASPR_3442`：The current paper text routes these checkerboard MIC/FICI values to Tables S1/S2, but the local packet lacks the MOESM1 PDF that should contain those supplement tables.

