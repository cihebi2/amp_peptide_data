# Top 100 硬冲突（论文证据 vs 数据库）

生成日期：2026-05-22

筛选规则：优先保留 `organism_or_subject_conflict`、`other_source_conflict`、`unresolved_record`，其次保留 `sequence_modified_not_normalized` / `sequence_or_modification_conflict`；并限制每篇论文最多 5 条，避免单篇论文刷满榜单。

## 汇总
- Top100 覆盖论文数：43
- 状态分布：{'source_conflict': 97, 'sequence_modified_not_normalized': 3}
- 数据库分布：{'DBAASP': 61, 'CAMP': 17, 'dbAMP': 8, 'APD6': 7, 'DRAMP': 7}
- 最高频类别：{'organism_or_subject_conflict': 99, 'activity_value_or_unit_conflict': 91, 'citation_or_linkage_only': 82, 'sequence_or_modification_conflict': 63, 'figure_or_non_tabulated_quantification': 40, 'missing_material_or_supplement_gap': 12, 'other_source_conflict': 1}

## 代表论文（按入榜条数）
- `doi__10.1007_s00726-018-2575-x`: 5 条
- `doi__10.1016_j.csbj.2021.08.039`: 5 条
- `doi__10.1021_acsomega.4c01577`: 5 条
- `doi__10.1038_s41538-021-00109-z`: 5 条
- `doi__10.1038_s41598-017-10492-x`: 5 条
- `doi__10.1038_s41598-017-11832-7`: 5 条
- `doi__10.1038_s41598-022-16303-2`: 5 条
- `doi__10.1007_s00018-020-03755-w`: 4 条
- `doi__10.1016_j.btre.2020.e00583`: 4 条
- `doi__10.1021_acs.jmedchem.2c00270`: 4 条

## 前 20 条样例
1. `doi__10.1002_cbic.202100151` / `DBAASP` / `DBAASP:DBAASPS_18493`
   - 状态: `source_conflict`
   - 类别: `sequence_or_modification_conflict;figure_or_non_tabulated_quantification;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only;missing_material_or_supplement_gap`
   - 摘要: DBAASP peptide_name uses R4L,S4L while the primary paper consistently names and tests the variant as R4L S8L; activity values match the source table, but the variant label conflict is preserved.
2. `doi__10.1007_s00018-020-03755-w` / `CAMP` / `CAMP:CAMPSQ12854`
   - 状态: `source_conflict`
   - 类别: `sequence_or_modification_conflict;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: CAMP/dbAMP entry-level activity text aggregates Table 3 values rather than carrying one primary-source assay row per JSONL record; retained as a source-linked database conflict instead of promoted to row-level verified assay evidence.
3. `doi__10.1007_s00018-020-03755-w` / `CAMP` / `CAMP:CAMPSQ12855`
   - 状态: `source_conflict`
   - 类别: `sequence_or_modification_conflict;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: CAMP/dbAMP entry-level activity text aggregates Table 3 values rather than carrying one primary-source assay row per JSONL record; retained as a source-linked database conflict instead of promoted to row-level verified assay evidence.
4. `doi__10.1007_s00018-020-03755-w` / `dbAMP` / `dbAMP:dbAMP_33012`
   - 状态: `source_conflict`
   - 类别: `sequence_or_modification_conflict;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: CAMP/dbAMP entry-level activity text aggregates Table 3 values rather than carrying one primary-source assay row per JSONL record; retained as a source-linked database conflict instead of promoted to row-level verified assay evidence.
5. `doi__10.1007_s00018-020-03755-w` / `dbAMP` / `dbAMP:dbAMP_33013`
   - 状态: `source_conflict`
   - 类别: `sequence_or_modification_conflict;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: CAMP/dbAMP entry-level activity text aggregates Table 3 values rather than carrying one primary-source assay row per JSONL record; retained as a source-linked database conflict instead of promoted to row-level verified assay evidence.
6. `doi__10.1007_s00018-022-04440-w` / `DBAASP` / `DBAASP:DBAASPS_22793`
   - 状态: `source_conflict`
   - 类别: `sequence_or_modification_conflict;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only;missing_material_or_supplement_gap`
   - 摘要: source_conflict: primary source supports 10 µM CD4-PP biofilm prevention, but the database MBIC/MBIC50 endpoint label is not stated as an exact threshold term in the paper.
7. `doi__10.1007_s00253-023-12947-w` / `APD6` / `APD6:AP04047`
   - 状态: `source_conflict`
   - 类别: `activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: APD6 identity/citation are supported, but its free-text activity summary mixes row-level primary activity, stability-condition MIC loss, toxicity, and mechanism statements. The conflict is preserved instead of flattening the database summary into source_verified row-level evidence.
8. `doi__10.1007_s00262-014-1540-0` / `DRAMP` / `DRAMP:DRAMP31842`
   - 状态: `source_conflict`
   - 类别: `sequence_or_modification_conflict;figure_or_non_tabulated_quantification;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: Primary source supports LTX-328 sequence/name and an IC50 >350 µM B16F1 row, but does not support the DRAMP FEMX-I target assignment for LTX-328 in this paper.
9. `doi__10.1007_s00726-017-2473-7` / `APD6` / `AP04794`
   - 状态: `source_conflict`
   - 类别: `activity_value_or_unit_conflict;organism_or_subject_conflict`
   - 摘要: source_conflict: APD6 free-text row mixes primary-paper activity/structure statements with database-only similarity or external-context annotations; primary Table 1/Table 2 support is preserved but broad database text is not promoted to fully source_verified.
10. `doi__10.1007_s00726-018-2575-x` / `CAMP` / `CAMPSQ16590`
   - 状态: `source_conflict`
   - 类别: `activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: conflict: CAMP row is a broad qualitative activity annotation with a species-list spelling discrepancy and no quantitative table values; primary sequence and broad antibacterial scope are source-backed.
11. `doi__10.1007_s00726-018-2575-x` / `CAMP` / `CAMPSQ16591`
   - 状态: `source_conflict`
   - 类别: `activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: conflict: CAMP row is a broad qualitative activity annotation with a species-list spelling discrepancy and no quantitative table values; primary sequence and broad antibacterial scope are source-backed.
12. `doi__10.1007_s00726-018-2575-x` / `CAMP` / `CAMPSQ16592`
   - 状态: `source_conflict`
   - 类别: `activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: conflict: CAMP row is a broad qualitative activity annotation with a species-list spelling discrepancy and no quantitative table values; primary sequence and broad antibacterial scope are source-backed.
13. `doi__10.1007_s00726-018-2575-x` / `CAMP` / `CAMPSQ16593`
   - 状态: `source_conflict`
   - 类别: `activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: conflict: CAMP row is a broad qualitative activity annotation with a species-list spelling discrepancy and no quantitative table values; primary sequence and broad antibacterial scope are source-backed.
14. `doi__10.1007_s00726-018-2575-x` / `CAMP` / `CAMPSQ16594`
   - 状态: `source_conflict`
   - 类别: `activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: conflict: CAMP row is a broad qualitative activity annotation with a species-list spelling discrepancy and no quantitative table values; primary sequence and broad antibacterial scope are source-backed.
15. `doi__10.1007_s10526-022-10132-y` / `DBAASP` / `DBAASPR_11558`
   - 状态: `source_conflict`
   - 类别: `sequence_or_modification_conflict;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: Database target spelling has Fusarium boothii, while the primary Table 1 row in local XML/PDF is Fusarium boothi; value and strain otherwise match, so the spelling discrepancy is preserved as source_conflict.
16. `doi__10.1007_s10526-022-10132-y` / `DBAASP` / `DBAASPS_22245`
   - 状态: `source_conflict`
   - 类别: `sequence_or_modification_conflict;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: Database target spelling has Fusarium boothii, while the primary Table 1 row in local XML/PDF is Fusarium boothi; value and strain otherwise match, so the spelling discrepancy is preserved as source_conflict.
17. `doi__10.1016_j.antiviral.2022.105270` / `DBAASP` / `DBAASP:DBAASPN_21372`
   - 状态: `sequence_modified_not_normalized`
   - 类别: `sequence_or_modification_conflict;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: Activity value is primary-source supported, but exact plitidepsin sequence/noncanonical modification identity is not embedded in this current primary article; preserve as sequence_modified_not_normalized instead of source_verified.
18. `doi__10.1016_j.btre.2020.e00583` / `DBAASP` / `DBAASP:DBAASPS_17528`
   - 状态: `source_conflict`
   - 类别: `figure_or_non_tabulated_quantification;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: Database target label uses Salmonella typhimurium ATCC 19430, while the primary paper methods and tables identify the tested strain as Salmonella enterica subsp. enterica serovar Typhi / S. typhi ATCC 19430.
19. `doi__10.1016_j.btre.2020.e00583` / `DBAASP` / `DBAASP:DBAASPS_17529`
   - 状态: `source_conflict`
   - 类别: `figure_or_non_tabulated_quantification;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: Database target label uses Salmonella typhimurium ATCC 19430, while the primary paper methods and tables identify the tested strain as Salmonella enterica subsp. enterica serovar Typhi / S. typhi ATCC 19430.
20. `doi__10.1016_j.btre.2020.e00583` / `DBAASP` / `DBAASP:DBAASPS_17530`
   - 状态: `source_conflict`
   - 类别: `figure_or_non_tabulated_quantification;activity_value_or_unit_conflict;organism_or_subject_conflict;citation_or_linkage_only`
   - 摘要: Database target label uses Salmonella typhimurium ATCC 19430, while the primary paper methods and tables identify the tested strain as Salmonella enterica subsp. enterica serovar Typhi / S. typhi ATCC 19430.

## 文件
- CSV: `/root/work/抗菌肽/数据库/batch/4-team/reports/database_literature_hard_conflicts_top100_20260522.csv`