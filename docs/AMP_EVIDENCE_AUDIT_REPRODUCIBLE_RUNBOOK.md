# AMP Evidence Audit 可复现流程手册

更新时间：2026-06-19
工作目录：`/root/work/抗菌肽/数据库/batch/4-team`

## 1. 目的

本文档把当前多 worker 论文审查系统沉淀为一个可从零复现的流程。新的 AI、人工 curator 或项目维护者应能依据本文档理解：

- 数据来自哪里；
- 每篇论文如何进入 material packet；
- 多 worker 如何分工；
- 最终生成哪些三层审查 artifact；
- 如何判断 accepted、caution、blocked、unresolved；
- 如何生成数据库-论文证据差异报告；
- 如何冻结 NAR-facing v1 数据版本。

本流程的目标不是创建“全新真值 AMP 数据库”，而是构建一个 primary-literature-grounded evidence audit layer，用于审计 APD6、DBAASP、DRAMP、CAMP、dbAMP 等抗菌肽数据库记录与原始论文证据之间的关系。

## 2. 关键原则

- `source_verified` 表示当前论文证据支持数据库记录。
- 非 `source_verified` 不等于数据库错误；它可能是粒度压缩、缺失材料、数据库-only 引用、单位/数值差异、序列修饰未标准化或机制标签过宽。
- `accepted_with_cautions` 不是 clean；它表示没有硬性 rework 阻塞，但仍有保留冲突或 caution。
- material packet ready、validator clean、semantic gate pass、publication-grade acceptance 必须分开报告。
- 不得把 packet 结构通过校验当作论文审查完成。
- 不得把 database-only claims 升格为 primary-source evidence。
- 缺失材料必须标成 blocked/unresolved，不得猜测补齐。

## 3. 输入数据层

### 3.1 合并数据库输出

常用输入根目录：

```text
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output
/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets
```

关键文件包括：

```text
output/sequences/all_sequences.csv
output/literature/sequence_literature_links.csv
output/literature/unique_literature_availability.csv
output/experiments/all_experimental_records.csv
output/experiments/dbaasp_assay_records.csv
output/experiments/apd6_activity_text_records.csv
output/experiments/dramp_activity_text_records.csv
landed_assets/manifests/landed_sources.csv
landed_assets/manifests/landed_asset_manifest.csv
landed_assets/manifests/landed_metadata_manifest.csv
landed_assets/manifests/summary.json
landed_assets/papers/<paper_id>/metadata.json
landed_assets/papers/<paper_id>/pdf/
landed_assets/papers/<paper_id>/xml/
landed_assets/papers/<paper_id>/package/
landed_assets/papers/<paper_id>/supplementary/
```

### 3.2 本地审查工作区

核心路径：

```text
papers/<paper_id>/source/
papers/<paper_id>/work/
papers/<paper_id>/final/
paper_packets/<paper_id>/raw/
paper_packets/<paper_id>/database/
paper_packets/<paper_id>/extracted/
paper_packets/<paper_id>/locators/
paper_packets/<paper_id>/rework/
reports/
scripts/
docs/
```

## 4. Paper Packet 合同

每篇论文进入 analysis 之前，应有 packet 或兼容映射。典型 packet 包含：

```text
paper_packets/<paper_id>/packet_manifest.json
paper_packets/<paper_id>/raw/paper.xml
paper_packets/<paper_id>/raw/paper.pdf
paper_packets/<paper_id>/raw/supplementary_original/
paper_packets/<paper_id>/extracted/xml_sections.json
paper_packets/<paper_id>/extracted/pdf_text/*.txt
paper_packets/<paper_id>/extracted/figure_captions.json
paper_packets/<paper_id>/extracted/supplementary_index.json
paper_packets/<paper_id>/extracted/supplementary_tables.json
paper_packets/<paper_id>/database/linked_assay_records.jsonl
paper_packets/<paper_id>/database/linked_experiment_records.jsonl
paper_packets/<paper_id>/database/linked_literature_records.jsonl
paper_packets/<paper_id>/database/linked_sequence_records.jsonl
paper_packets/<paper_id>/locators/locator_index.json
paper_packets/<paper_id>/extraction/extraction_status.json
paper_packets/<paper_id>/rework/rework_requests.jsonl
paper_packets/<paper_id>/rework/rework_responses.jsonl
```

若 XML/PDF/supplement 缺失，packet 必须记录具体缺失、尝试过的获取方式、失败原因和是否阻塞 analysis。

## 5. 六 worker 审查职责

### Material queue

- `worker-1 / intake_linkage`：定位论文资产、DOI/PMID/PMCID、数据库链接行、packet manifest。
- `worker-2 / main_text_assay_extractor`：抽取主文/XML/PDF/table 的活性、毒性、实验条件、locator。
- `worker-3 / supplementary_methods_extractor`：抽取补充材料、表格、方法、序列、机制证据、OCR/archive 输出。

### Analysis queue

- `worker-4 / database_record_auditor`：审计数据库记录身份、序列、修饰、来源、引用和冲突。
- `worker-5 / mechanism_ontology_extractor`：把机制证据分成 direct mechanism、phenotype supported、inferred、computational only、unknown/not tested。
- `worker-6 / adjudicator_review`：综合 1-5 的输出，保留冲突，写最终 review report；必要时打回 material 或 analysis queue。

## 6. 最终 artifact

每篇论文的核心最终文件：

```text
papers/<paper_id>/final/database_record_verification.json
papers/<paper_id>/final/activity_toxicity_evidence.json
papers/<paper_id>/final/mechanism_ontology_record.json
papers/<paper_id>/final/review_report.json
```

### 6.1 `database_record_verification.json`

关键字段：

- `paper_id`, `doi`
- `review_model`, `reasoning_effort`, `source_reviewed`
- `database_row_counts`
- `status_counts` / `status_summary`
- `record_audits[]`
- `record_audits[].database`
- `record_audits[].source_id`
- `record_audits[].sequence_key`
- `record_audits[].source_table`
- `record_audits[].status`
- `record_audits[].database_subject`
- `record_audits[].database_measure`
- `record_audits[].database_value`
- `record_audits[].database_unit`
- `record_audits[].source_locator`
- `record_audits[].conflict_context`
- `record_audits[].review_notes`

状态枚举：

- `source_verified`
- `source_conflict`
- `sequence_modified_not_normalized`
- `database_only_no_primary_source`
- `unresolved_record`

### 6.2 `activity_toxicity_evidence.json`

关键字段：

- `activity_records[]`
- `record_id`
- `peptide` / `entity`
- `endpoint`
- `raw_value`, `raw_unit`
- `normalized_value`, `normalized_unit`, `normalization_status`
- `target.species`, `target.strain`, `target.gram_status`, `target.target_class`
- `assay_conditions`
- `replicates_statistics`
- `evidence_ladder`
- `source_locator`

### 6.3 `mechanism_ontology_record.json`

关键字段：

- `mechanism_claims[]`
- `claim_id`
- `claim_text`
- `entity_scope`
- `evidence_class`
- `direct_assay_types`
- `source_locator`
- `limitations`

证据等级：

- `direct_mechanism`
- `phenotype_supported`
- `inferred_mechanism`
- `computational_only`
- `unknown_or_not_tested`

### 6.4 `review_report.json`

关键字段：

- `review_status`
- `publication_grade`
- `validator_contract_passed`
- `final_layer_outputs_ready`
- `source_review_depth`
- `materials_exhausted`
- `checked_inputs`
- `semantic_quality_checks`
- `per_layer_decision_rationale`
- `caution_findings`
- `qc_failure_reasons`
- `rework_targets`
- `final_outputs`

可见状态：

- `accepted_clean`
- `accepted_with_cautions`
- `needs_targeted_rework`
- `blocked_missing_primary_material`

## 7. 打回机制

打回不通过聊天口头完成，必须落到 packet 或 team state：

```text
paper_packets/<paper_id>/rework/rework_requests.jsonl
paper_packets/<paper_id>/rework/rework_responses.jsonl
quality_feedback.json
CODEX_REVIEW_PROMPT.md
```

每个 rework ticket 应至少包含：

- `ticket_id`
- `paper_id`
- `target_queue`
- `severity`
- `blocker_type`
- `required_action`
- `acceptance_check`
- `source`
- `created_at`

质量把关 worker 必须说明：为什么不合格、缺哪个字段/locator、对应前序 worker 应该修什么、最多打回次数和最终 blocked 条件。

## 8. 常用状态口径

- `accepted_after_rework`：队列终态，不等于 clean truth。
- `accepted_with_cautions`：可纳入 source-reviewed release，但 caution 仍需展示。
- `blocked_after_best_effort`：尽力从材料中获取后仍无法安全补齐。
- `metadata_only`：只有元数据，无可用 primary source。
- `weak_source`：有 partial/weak materials，可做宽松抽取或进一步补源。
- `database_only_no_primary_source`：数据库有记录，但当前论文原文不能验证。
- `unresolved_record`：材料或链接不足，不能判定。

## 9. 复现命令

### 9.1 汇总材料恢复状态

```bash
python scripts/summarize_material_source_recovery.py
```

输出：

```text
reports/source_recovery/material_source_recovery_status_latest.json
```

### 9.2 生成数据库-论文差异报告

```bash
python scripts/generate_database_literature_difference_report.py
```

输出：

```text
reports/database_vs_literature_difference_summary_latest.json
reports/database_vs_literature_difference_examples_latest.md
reports/database_vs_literature_difference_examples_latest.csv
reports/database_vs_literature_difference_records_latest.csv
```

### 9.3 冻结 NAR-facing v1 候选版本

```bash
python scripts/build_nar_resource_freeze_v1.py
```

输出目录：

```text
reports/nar_resource_freeze_v1/
```

核心输出：

```text
release_manifest_latest.json
README.md
unified_scope_summary_latest.json
paper_scope_latest.csv
excluded_or_non_publication_grade_papers_latest.csv
database_denominators_latest.csv
crosstab_status_by_database_latest.csv
crosstab_category_by_database_latest.csv
crosstab_status_by_source_table_latest.csv
crosstab_review_status_by_database_latest.csv
scope_reconciliation_1471_vs_1472_latest.json
scope_reconciliation_1471_vs_1472_latest.md
```

字段、分母和交叉表口径见：

```text
docs/NAR_FREEZE_V1_DATA_DICTIONARY.md
reports/nar_resource_freeze_v1/README.md
```

## 10. 从零复现建议流程

1. 刷新 merged corpus manifests。
2. 建立 paper manifest：从数据库-文献链接、landed_assets、downloaded fallback 生成候选。
3. 运行 material queue：为每篇建立 packet，抽取 XML/PDF/supplement/database rows/locators。
4. 运行 analysis queue：worker-4/5/6 分别生成 database audit、mechanism ontology、review report。
5. 对不合格论文写 rework tickets，不得静默接受。
6. 重跑 targeted rework，最多打回固定次数；仍不可获取的信息标为 blocked/unresolved。
7. 生成差异报告和全量 CSV。
8. 运行 v1 freeze builder。
9. 人工分层抽样复核。
10. 将 release package 发布到公开网站/API/download。

## 11. 当前 v1 的保守解释

当前 v1 freeze candidate 应解释为：

- 一个 evidence-audit release candidate；
- 不是 NAR submission-ready public database；
- 主数据可优先使用 `publication_grade=true` 且 review_status 为 accepted-like 的子集；
- 非 publication-grade、blocked、unresolved、metadata-only、weak-source 应单独发布为 backlog/excluded 表；
- 任何非 `source_verified` 都只能称为 evidence discordance/provenance gap，不能直接称为 database error。
- `1471` 是当前 final-artifact universe；历史队列 `1472` 多出的 1 篇是 `doi__10.1055_s-0029-1185675`，其初始队列启动失败且没有 final artifact，应路由到 source-staging/infra-recovery，而不是纳入当前 v1 主分母。
