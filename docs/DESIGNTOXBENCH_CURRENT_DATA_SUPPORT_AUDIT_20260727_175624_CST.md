# DesignToxBench 当前数据支持度审计

- 审计时间：2026-07-27 18:02 CST
- 口径修订：已剔除 `biofilm_cell_viability` 等微生物疗效记录
- 课题：天然肽模型向人工设计肽的分布外泛化
- 暂定题目：**DesignToxBench：人工设计短肽安全性预测的分布偏移基准**
- 统计权威层：`releases/amp_evidence_atlas_v1_rc2/`
- 可复现结果：`reports/designtoxbench_support_audit_20260727T175225_CST/summary.json`
- 候选论文清单：`reports/designtoxbench_support_audit_20260727T175225_CST/design_candidate_papers.tsv`
- 复现脚本：`scripts/assess_designtoxbench_support.py`

## 一句话结论

**当前数据足以立即启动该课题，并可先建立一个 141 条短肽的设计安全性候选核心；但目前还没有任何一条记录满足“已经发布为 DesignToxBench 最终金标准”的完整合同。**

原因不是实验数据完全不够，而是设计来源、母体关系、修饰、标签阈值、删失符号、同源簇和正式切分表尚未统一。

## 1. 大白话数字

### 1.1 真正可以先动手的核心

在 RC2 的公开、源审查记录中：

| 指标 | 当前数量 |
|---|---:|
| 标题明确属于生成、机器学习、理性设计或 de novo 设计的论文候选 | **91 篇** |
| 其中有明确安全性 endpoint 的论文 | **59 篇** |
| 其中已有可直接用于序列模型的短标准序列论文 | **12 篇** |
| 明确安全性实验记录 | **659 条** |
| 有效标准 20-AA 字母且长度不超过 50 aa 的安全性短肽 | **141 条唯一序列** |
| 同一论文、同一序列同时具有活性和安全性观察 | **136 条唯一序列** |
| 带不等号、上/下界或删失状态的安全记录 | **255 条** |
| 安全记录带原始值 | **659/659** |
| 安全记录带来源定位 | **659/659** |
| 安全记录带规范化数值 | **324/659** |

这 141 条是**建集起点**，不是已经冻结的最终测试集。论文中可能同时包含天然母体和设计变体，仍需做实体级判定。

### 1.2 最新严格 DBAASP 增量

RC2 之外，严格六 worker 队列已经终审一篇明确的生成式设计论文：

- `PMC12125351`
- DOI：`10.1038/s42003-025-08282-7`
- 题目：AMPGen diffusion-driven generative model for de novo AMP design
- 活性记录：**130**
- 毒性记录：**126**
- 当前已落地短标准序列：**0**

所以跨 RC2 与最新严格增量，已经源审查的高置信设计安全证据为：

- **60 篇有安全结果的设计论文**
- **785 条安全记录**
- 但序列模型可直接读取的核心仍是 **12 篇、141 条唯一短序列**

AMPGen 的 126 条毒性记录需要先补齐序列，且该增量不能静默混入 RC2。

### 1.3 补判定后可扩展的上限

将 analogue、derivative、substitution、hybrid、stapled、optimization 等论文也纳入候选挖掘：

| 指标 | 宽候选上限 |
|---|---:|
| 设计/改造候选论文 | **214 篇** |
| 有安全 endpoint 的候选论文 | **139 篇** |
| 已有短标准安全序列的论文 | **25 篇** |
| 安全记录 | **1,691 条** |
| 安全性短标准序列 | **220 条唯一序列** |
| 同论文同序列同时有活性和安全性 | **202 条唯一序列** |
| 删失或不等式安全记录 | **427 条** |

其中 analogue/optimization 层单独包含：

- 123 篇候选论文
- 80 篇有安全结果
- 13 篇已有短标准安全序列
- 1,032 条安全记录
- 79 条唯一安全短序列

该层是扩展候选，不应在未看原文前直接标为人工设计。

## 2. 最重要的三个口径

| 口径 | 数量 | 能否直接对外称为 benchmark |
|---|---:|---|
| 已经冻结的 DesignToxBench 最终金标准 | **0** | 否 |
| 可立即开始实体审查和标签构建的核心 | **12 篇 / 141 序列 / 659 安全记录** | 可建 v0.1，不可直接发布 |
| 经 analogue、sequence recovery 和原文判定后的 RC2 候选上限 | **25 篇 / 220 序列 / 1,691 安全记录** | 需要补字段和终审 |

不能把“0 条最终金标准”误解成“项目没有数据”；也不能把“220 条候选”误写成“220 条已经确认的人工设计肽”。

## 3. 当前最能支持哪些设计肽

### 3.1 生成模型或机器学习设计肽

这是当前最强的一层：

| 指标 | 数量 |
|---|---:|
| 论文候选 | **14 篇** |
| 有安全记录 | **9 篇** |
| 已有短标准安全序列 | **6 篇** |
| 安全记录 | **184 条** |
| 安全短序列 | **98 条** |
| 同论文同序列活性—安全配对 | **96 条** |
| 删失或不等式安全记录 | **119 条** |

已覆盖 diffusion、RNN、deep learning、GPT 等来源。

### 3.2 理性设计、计算设计和 de novo 设计肽

| 指标 | 数量 |
|---|---:|
| 论文候选 | **77 篇** |
| 有安全记录 | **50 篇** |
| 已有短标准安全序列 | **6 篇** |
| 安全记录 | **475 条** |
| 安全短序列 | **43 条** |
| 同论文同序列活性—安全配对 | **40 条** |

这一层论文多，但序列字段下沉不足，说明主要工作是 sequence recovery 和实体级母体/变体判定。

### 3.3 analogue、derivative 和优化肽

有较大扩展潜力，但天然母体、实验合成和真正人工改造容易混淆。该层应标为：

```text
natural_derivative_or_mutant
```

而不是简单并入：

```text
designed_explicit
```

### 3.4 CPP、抗癌肽和靶向结合肽

- 已发现人工细胞穿透/嵌合肽及相应安全记录，但当前数量少。
- 抗癌肽已有安全和活性证据；必须把“对癌细胞的细胞毒性”解释为疗效，而不是宿主安全性。
- 靶向结合肽、病毒融合抑制肽、miniprotein 和 stapled peptide 有论文候选，但普通细胞安全性覆盖不足。

因此 v0.1 最适合以**人工设计 AMP 为主，CPP/ACP/靶向肽作为分层扩展**。

## 4. 141 条核心序列来自哪些论文

| paper_id | 年份 | 类型 | 安全短序列 |
|---|---:|---|---:|
| `doi__10.1002_pro.5088` | 2024 | RNN de novo design | 58 |
| `doi__10.1038_s41598-019-47568-9` | 2019 | in silico ACP design | 31 |
| `doi__10.1038_s41467-023-42434-9` | 2023 | deep learning de novo development | 22 |
| `doi__10.1002_advs.202507457` | 2025 | prompt diffusion | 10 |
| `doi__10.3390_antibiotics11030411` | 2022 | RNN design | 4 |
| `doi__10.1038_s41598-018-32981-3` | 2018 | engineered AMP | 4 |
| `doi__10.1038_s41598-018-34684-1` | 2018 | cell-permeable chimeric peptide | 3 |
| `doi__10.3390_ijms232415594` | 2022 | de novo ACP | 2 |
| `doi__10.1155_2020_2131535` | 2020 | rationally designed AMP | 2 |
| `doi__10.1080_19490976.2025.2523811` | 2025 | BroadAMP-GPT | 2 |
| `doi__10.1038_s41467-025-64378-y` | 2025 | DLFea4AMPGen | 2 |
| `doi__10.1002_cbic.202100151` | 2021 | rational design | 1 |

前三篇贡献 **111/141（78.7%）**。因此：

- 随机按序列或记录切分会严重高估泛化；
- leave-paper-out 必须是主结果；
- 需要从剩余 47 篇有安全结果但无短标准序列的高置信设计论文中继续恢复序列。

## 5. 安全数据及四象限能做到什么

### 5.1 已经有的数据

高置信设计论文中的 659 条安全记录包括：

- 溶血：**556**
- 细胞毒性或非癌细胞活力：**100**
- 其他明确安全 endpoint：**3**

136 条短序列在同一论文内同时具有活性和安全性观察，因此具备构建以下四象限的原始条件：

1. 活性且安全；
2. 活性但有毒；
3. 无活性但安全；
4. 无活性且有毒。

### 5.2 当前不能直接给出的数字

四象限的最终样本数现在不能严谨统计，原因是尚未冻结：

- 活性的 endpoint 特异阈值；
- 安全/有毒的物种、细胞、浓度、时间阈值；
- `>`、`<`、区间和检测上限的处理；
- 同一肽多条件冲突时的标签规则。

错误做法是把 MIC、HC50、percent hemolysis、CC50、cell viability 和癌细胞 IC50 全部压成一个二元标签。

### 5.3 失败候选和区间记录

失败信息确实被保留，但没有统一字段：

- 高置信设计安全记录中已有 **255 条**不等式或删失候选；
- 宽设计候选中有 **427 条**；
- 整个 release 的文本扫描还能找到 `no activity`、`inactive`、`not detected`、`censor` 等记录，但这些关键词彼此重叠且语义不同。

需要新增：

```text
value_operator
lower_bound
upper_bound
is_censored
observation_status
```

并保留原始值，不得把 `>128` 强制改成精确的 `128`。

## 6. OOD 切分当前能做到哪里

| 评价方式 | 当前状态 | 说明 |
|---|---|---|
| leave-paper-out | **可直接做** | 使用 `paper_id`，不可只依赖 DOI |
| 精确序列去重 | **部分可做** | 序列缺失和化学修饰仍需补齐 |
| 天然训练、设计测试 | **不能直接冻结** | 缺 `natural_or_designed` 和实体来源 |
| 低同源测试 | **可计算但尚无合同** | 缺标准分子身份、同源簇和阈值 |
| 按发表时间划分 | **元数据可恢复** | 年份在 XML 中，未下沉到 release 主表 |
| 模型训练时期之后发表的数据 | **尚不能证明** | 还需模型训练数据版本和 cutoff |
| 按设计方法分层 | **论文候选可分，实体标签未完成** | 生成/ML、理性/de novo、analogue 三层 |
| 校准、风险—覆盖、高置信错误 | **属于模型评价层** | 需模型概率、置信度、拒判分数和错误裁定 |

### 时间候选

高置信设计且有安全结果的论文中：

| 时间口径 | 论文 | 已有安全短序列的论文 | 安全短序列 | 安全记录 |
|---|---:|---:|---:|---:|
| 2023 年及以后 | 15 | 5 | 94 | 199 |
| 2024 年及以后 | 8 | 4 | 72 | 93 |
| 2025 年及以后 | 4 | 3 | 14 | 19 |

这些可用于时间 holdout 候选，但“某模型训练以后”仍必须绑定该模型真实的训练截止时间。

## 7. 最大风险：训练集污染

外部合并数据库当前包含：

- 5 库序列记录：127,542
- 唯一 canonical 20-AA 序列：55,158
- 实验/文本记录：363,337
- 唯一文献来源：7,274

这些数据适合做训练池或候选挖掘，但不是天然肽纯集合，也没有统一的设计身份。

更关键的是：

- 141 条高置信设计安全短序列中；
- **139 条与当前 APD6/DBAASP/DRAMP 合并序列文件精确重叠；**
- 只有 2 条在该三库文件中无精确匹配。

这不代表只有 2 条低同源肽，而是说明如果直接用“当前数据库全量”训练，再用这 141 条测试，几乎必然发生数据泄漏。

必须记录：

```text
training_dataset_name
training_dataset_version
training_snapshot_date
model_training_cutoff
exact_overlap_removed
homology_cluster_id
max_train_test_identity
```

## 8. 当前已有字段和缺失字段

### 8.1 已有测量字段

```text
paper_id
activity_record_id
entity
peptide
sequence
entity_type
endpoint
raw_value
raw_unit
normalized_value
normalized_unit
normalization_status
target
assay_conditions
replicates_statistics
evidence_ladder
source_locator
database_traceability
curation_notes
review_status
publication_grade
public_v1_included
```

### 8.2 必须新增或统一的字段

```text
benchmark_record_id
canonical_peptide_id
standardized_sequence
modification
stereochemistry
cyclicity
lipidation_or_conjugation
publication_date
data_publication_date
natural_or_designed
entity_design_origin
design_method
design_model
parent_sequence
scaffold_or_library_id
safety_endpoint_family
activity_endpoint_family
value_operator
lower_bound
upper_bound
is_censored
label_definition
homology_cluster_id
max_train_test_identity
split_group
training_dataset_version
model_training_cutoff
```

建议设计来源不要只做二元值，至少采用：

```text
natural_explicit
designed_explicit
generated_explicit
natural_derivative_or_mutant
synthetic_only_unknown_origin
unknown
```

## 9. 数据冲突和不能混用的层

1. `synthesis_type=Synthetic` 只表示合成制备，不等于序列是人工设计。
2. 设计论文可能同时报告天然母体和设计变体；论文级身份不能替代实体级身份。
3. 癌细胞毒性可能是抗癌疗效，不能自动当作宿主毒性。
4. 同一安全语义存在多种 endpoint 拼写，且实验物种、细胞、时间和浓度不同。
5. `activity` 与 `audit.status` 缺少可靠的一对一外键；不能仅按 paper 级状态假定每个数据库值无冲突。
6. Portal 的 1,811 篇和 115,372 条记录混合了 RC2 core、双模型恢复和机器抽取；不能把它当成 RC2 权威分母。
7. `dual_model_recovered` 与 `machine_extracted` 适合候选层，不得无标记并入最终标签。
8. validation420 只完成 39/224 篇、114/420 行严格源审查，不能整体作为独立金标准。
9. 旧数据字典的公开论文分母与最新 RC2 不一致；本审计使用最新 RC2 的 1,374 篇公开候选。
10. `paper_scope_latest.csv` 的 1,472 与 RC2 `papers.tsv` 的 1,471 仍是历史分母冲突；模型基准应冻结独立 manifest。

## 10. 推荐执行规划

### 阶段 A：DesignToxBench v0.1 核心

1. 冻结 12 篇、141 条短序列候选。
2. 逐实体判定天然母体、设计变体、生成候选和实验对照。
3. 恢复并统一修饰、D/L 构型、环化、脂化和末端修饰。
4. 将 659 条安全记录映射到统一 endpoint family。
5. 将 255 条不等式/删失记录结构化，保留原始值。
6. 冻结 activity/safety 标签政策后再统计四象限。

### 阶段 B：扩大论文独立性

1. 从 47 篇“已有安全结果但无短标准序列”的高置信设计论文恢复序列。
2. 补齐 AMPGen 的生成序列，将其 126 条毒性和 130 条活性记录纳入独立增量候选。
3. 审查 80 篇 analogue/optimization 安全论文，区分天然衍生、人工改造和仅合成测定。
4. 优先审查严格队列中的 `PMC12160004` 和 `PMC11672609`。

### 阶段 C：无泄漏切分

1. 先按 canonical molecule 去重。
2. 再按 parent/scaffold/library 分组。
3. 建立序列同源簇和最大 train-test identity。
4. 生成 natural-train/designed-test、leave-paper-out、时间切分和设计方法分层 manifest。
5. 训练数据必须固定版本并从测试集删除 exact/homology overlap。

### 阶段 D：模型评价

1. 比较天然测试集与设计肽测试集性能落差。
2. 报告 AUROC/AUPRC 之外的校准误差、Brier/NLL。
3. 报告风险—覆盖和拒判策略。
4. 单独分析高置信错误、设计方法、母体相似度、修饰类型和论文来源。

## 11. 课题可行性判断

### 可以支持的结论

- 当前数据足以构建一个严格、来源可追溯的 DesignToxBench 初始版本。
- 现成核心规模不大，符合“独立实验测试集而非大而全训练集”的课题定位。
- 数据中已经包含生成模型、机器学习、理性设计、de novo 和改造肽。
- 已保留大量不等式和失败候选语义，适合研究拒判与风险控制。
- 当前数据库重叠本身就是证明传统随机切分和静态数据库测试不可靠的重要证据。

### 现在不能支持的表述

- 不能声称已有 220 条全部确认的人工设计肽。
- 不能声称 141 条都是低同源或模型训练后数据。
- 不能声称四象限标签已经完成。
- 不能声称 validation420 已构成独立人工金标准。
- 不能声称当前 portal 混合层都是 publication-grade 标签。

### 最终判断

**建议启动。**

141 条短序列、136 条活性—安全配对和 255 条删失安全记录已足以做高质量 v0.1；真正决定论文质量的不是继续无边界扩量，而是完成实体来源判定、无泄漏切分、时间/训练版本追踪和高置信错误分析。安全 endpoint 统计已明确剔除 `biofilm_cell_viability` 等微生物疗效记录。

当前最大不足是 141 条序列集中于 12 篇论文，且前三篇贡献 78.7%。因此下一阶段应优先恢复更多独立论文，而不是继续堆同一论文中的 assay 行。

## 12. 复现

```bash
cd /home/cihebi/抗菌肽/数据集/batch/5-team

python -m py_compile scripts/assess_designtoxbench_support.py

python scripts/assess_designtoxbench_support.py \
  --output-json \
    reports/designtoxbench_support_audit_20260727T175225_CST/summary.json \
  --output-candidates-tsv \
    reports/designtoxbench_support_audit_20260727T175225_CST/design_candidate_papers.tsv
```
