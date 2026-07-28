# NAR Freeze v1 数据字典与复现口径

更新时间：2026-06-22  
工作目录：`/root/work/抗菌肽/数据库/batch/4-team`

本文档定义当前 AMP Evidence Atlas / NAR database resource v1 freeze candidate 的数据集、字段、分母和交叉表口径。交给新的 AI 时，应先读本文件，再运行 freeze builder。

## 1. 一键复现

```bash
cd /root/work/抗菌肽/数据库/batch/4-team
python scripts/generate_database_literature_difference_report.py
python scripts/build_nar_resource_freeze_v1.py
python -m json.tool reports/nar_resource_freeze_v1/release_manifest_latest.json >/dev/null
python -m json.tool reports/nar_resource_freeze_v1/unified_scope_summary_latest.json >/dev/null
```

核心输出目录：

```text
reports/nar_resource_freeze_v1/
```

## 2. Release 状态

当前 release id：`amp-evidence-audit-v1-freeze-candidate`

当前状态只能称为 `freeze_candidate`，不能称为 NAR-ready public database。投稿前还缺：

- public website / HTTPS URL / search interface；
- bulk download；
- API 或机器可读接口；
- schema 文档和版本化 release package；
- manual stratified validation；
- 数据源版本、license、维护计划；
- `1471` vs `1472` reconciliation 说明写入 manuscript。

## 3. Inclusion / Exclusion 口径

### 3.1 paper-level universe

`paper_final_artifact_count = 1471`

定义：当前 `papers/*/final/` 下存在 final review/database/activity/mechanism artifact 的论文集合，由 `scripts/build_nar_resource_freeze_v1.py` 扫描得到。

### 3.2 public v1 candidate subset

`public_v1_candidate_papers = 1371`

纳入条件：

- `papers/<paper_id>/final/review_report.json` 中 `publication_grade = true`；
- `review_status` 属于：`accepted`, `accepted_clean`, `accepted_with_cautions`。

注意：当前 1371 篇全部是 `accepted_with_cautions`；这不是 clean，只表示没有硬性阻塞，caution 仍需公开展示。

### 3.3 excluded / non-publication-grade subset

`excluded_or_non_publication_grade_papers = 100`

当前构成：

- `needs_targeted_rework = 29`；
- `blocked_missing_primary_material = 67`；
- `review_status_not_in_public_set = 4`，包括 `publication_grade` 2 篇、`publication_grade_ready` 1 篇、`publication_grade_with_cautions` 1 篇。它们虽然含 publication-grade 相关标记，但不满足 public v1 accepted-like review_status 纳入规则。

这 100 篇不能进入主 release candidate 的 source-reviewed 主分析，但应进入 excluded/backlog/sensitivity 表。

### 3.4 legacy queue aggregate

旧队列汇总中 `unique_paper_count = 1472`，而当前 final artifact 扫描为 `1471`。差异已定位：

- `1471`：当前 freeze builder 从 `papers/*/final` 实际扫描到的 final artifact universe；
- `1472`：历史 queue terminal aggregate 的去重论文数；
- 多出的 1 篇为 `doi__10.1055_s-0029-1185675`；
- 该论文在历史队列中为 `initial_queue_failed` / `infrastructure_initial_queue_failed`，启动前报错为 `selected paper must have xml and pdf`；
- landed assets 目录存在，但只有 supplementary/local fallback，缺 primary `xml/` 和 `pdf/` 目录；
- 当前无 `papers/doi__10.1055_s-0029-1185675/final/review_report.json`，因此不进入 v1 final-artifact universe；
- manuscript 中必须保留 reconciliation note，不能静默把两者混为一个数字。

机器可读 reconciliation 输出：

```text
reports/nar_resource_freeze_v1/scope_reconciliation_1471_vs_1472_latest.json
reports/nar_resource_freeze_v1/scope_reconciliation_1471_vs_1472_latest.md
```

## 4. 核心输出文件

| 文件 | 当前行数 | 粒度 | 用途 |
| --- | ---: | --- | --- |
| `release_manifest_latest.json` | 1 | release | 输入文件、checksum、输出路径、纳入规则、not-ready 条件。 |
| `unified_scope_summary_latest.json` | 1 | release | 统一范围统计、状态统计、多标签差异统计。 |
| `paper_scope_latest.csv` | 1471 | paper | 每篇 final artifact 的纳入状态、review status、三层 artifact 计数。 |
| `excluded_or_non_publication_grade_papers_latest.csv` | 100 | paper | 未进入 public v1 candidate 的论文和排除原因。 |
| `database_denominators_latest.csv` | 6 | database | 按数据库统计 audit-row 分母和 source/non-source verified 状态。 |
| `crosstab_status_by_database_latest.csv` | 23 | database x status | 数据库审计状态交叉表。 |
| `crosstab_category_by_database_latest.csv` | 40 | database x multilabel category | 多标签差异类别交叉表。 |
| `crosstab_status_by_source_table_latest.csv` | 253 | source_table x status | 原始 source table 与审计状态交叉表。 |
| `crosstab_review_status_by_database_latest.csv` | 20 | database x paper review_status | 按 audit row 连接 paper review status 的交叉表。 |
| `scope_reconciliation_1471_vs_1472_latest.json/md` | 1 | release | 解释历史队列 1472 与 final artifact 1471 的差异。 |
| `unresolved_records_triage_latest.csv/json/md` | 56 | unresolved audit row | 56 条 unresolved record 的 blocker 分类和下一步队列建议。 |

## 5. `paper_scope_latest.csv` 字段

| 字段 | 含义 |
| --- | --- |
| `paper_id` | 本地论文 ID，通常为 DOI/PMID 派生安全字符串。 |
| `doi` | final artifact 中记录的 DOI；可能为空。 |
| `review_status` | worker-6 / final review 给出的论文审查状态。 |
| `publication_grade` | 是否达到当前 publication-grade gate。 |
| `source_reviewed` | 是否经过 source-reviewed 审查；不能单独替代 publication_grade。 |
| `public_v1_included` | 是否进入 public v1 candidate 主子集。 |
| `exclusion_reason` | 未纳入主子集的原因；纳入时为空。 |
| `database_audit_records` | 该论文 `database_record_verification.json` 中 record audit 数。 |
| `activity_records` | 该论文 `activity_toxicity_evidence.json` 中 activity/toxicity 记录数。 |
| `mechanism_claims` | 该论文 `mechanism_ontology_record.json` 中机制 claim 数。 |
| `database_final_exists` | database final artifact 是否存在。 |
| `activity_final_exists` | activity final artifact 是否存在。 |
| `mechanism_final_exists` | mechanism final artifact 是否存在。 |
| `review_report_exists` | review report 是否存在。 |

## 6. `database_denominators_latest.csv` 字段

重要：这里的分母是 `final/database_record_verification.json` 的 audit-row 分母，不是 APD6/DBAASP/DRAMP/CAMP/dbAMP 原始数据库全量记录数。

| 字段 | 含义 |
| --- | --- |
| `database` | 推断或显式数据库名。 |
| `total_audit_rows_denominator` | 当前 final artifacts 中该数据库 audit rows 总数。 |
| `paper_count_with_rows` | 至少含该数据库 audit row 的论文数。 |
| `source_verified` | 原文证据支持的 audit rows 数。 |
| `source_conflict` | 原文证据与数据库字段存在冲突或粒度差异的 rows 数。 |
| `sequence_modified_not_normalized` | 序列/修饰/端基/构型未标准化或不能直接等同的 rows 数。 |
| `database_only_no_primary_source` | 数据库有断言但当前 primary source 不能验证的 rows 数。 |
| `unresolved_record` | 材料或链接不足，不能安全判定的 rows 数。 |
| `non_source_verified` | 非 `source_verified` 总数。 |
| `non_source_verified_rate` | `non_source_verified / total_audit_rows_denominator`。 |
| `public_v1_audit_rows` | public v1 candidate papers 内该数据库 audit rows 数。 |
| `public_v1_non_source_verified` | public v1 candidate papers 内非 `source_verified` rows 数。 |
| `denominator_note` | 固定解释：audit-row denominator，不是 raw database universe。 |

当前 database denominator 快照：

| database | total audit rows | non-source verified | rate |
| --- | ---: | ---: | ---: |
| APD6 | 2283 | 747 | 0.327201 |
| CAMP | 2837 | 1824 | 0.642933 |
| DBAASP | 123721 | 34211 | 0.276517 |
| DRAMP | 8458 | 5207 | 0.615630 |
| dbAMP | 1954 | 1328 | 0.679632 |
| unknown | 6 | 1 | 0.166667 |

## 7. 审计状态解释

| status | 可说什么 | 不能说什么 |
| --- | --- | --- |
| `source_verified` | 当前 primary literature evidence 支持该数据库记录。 | 不能说全数据库、全历史版本都已验证。 |
| `source_conflict` | 当前原文证据与数据库字段存在冲突、粒度压缩、数值/对象/单位差异。 | 不能自动说数据库错误；需逐条看 context。 |
| `sequence_modified_not_normalized` | 序列、修饰、端基、D/L 构型或变体标签未被标准化到可直接等同。 | 不能直接归为活性冲突。 |
| `database_only_no_primary_source` | 数据库断言当前 primary source 中没有可定位支持。 | 不能说原断言一定不存在或错误。 |
| `unresolved_record` | 材料/链接/补充信息不足，不能判定。 | 不能猜测补齐。 |

## 8. 差异类别口径

`difference_category_counts_multilabel` 和 `crosstab_category_by_database_latest.csv` 是多标签扫描：一条 audit row 可同时属于多个 category。因此：

- 可以用来描述问题类型分布；
- 不能把类别计数相加当作 unique record 总数；
- 不能直接等同于数据库错误数。

当前类别包括：

- `activity_value_or_unit`
- `sequence_or_modification`
- `mechanism_or_claim_scope`
- `target_or_organism`
- `row_granularity`
- `database_only_no_primary_source`
- `unresolved_or_missing_material`
- `other`

## 9. 论文/数据库差异主数字

当前 freeze summary：

| 指标 | 数值 |
| --- | ---: |
| paper final artifacts | 1471 |
| public v1 candidate papers | 1371 |
| excluded/non-publication-grade papers | 100 |
| database audit rows | 139259 |
| source verified rows | 95941 |
| non-source verified rows | 43318 |
| activity records | 115184 |
| mechanism claims | 4772 |

数据库审计状态：

| status | rows |
| --- | ---: |
| `source_verified` | 95941 |
| `source_conflict` | 32550 |
| `sequence_modified_not_normalized` | 6472 |
| `database_only_no_primary_source` | 4240 |
| `unresolved_record` | 56 |

## 10. 对外写作口径

推荐说法：

> We froze a v1 candidate evidence-audit snapshot comprising 1,471 paper-level final artifacts and 139,259 database audit rows. The public v1 candidate subset contains 1,371 accepted-with-cautions papers. Among audit rows, 95,941 were source-verified and 43,318 retained evidence discordance, provenance gaps, modification-normalization issues, database-only assertions, or unresolved status.

避免说法：

- “我们证明 43,318 条数据库记录错误”；
- “1371 篇都是 clean”；
- “这是完整 APD6/DBAASP/DRAMP/CAMP/dbAMP 全库分母”；
- “AI 自动完成了人工金标准审查”。

## 11. 下一步质量动作

冻结前三步完成后，建议按顺序做：

1. 按 `reports/nar_resource_freeze_v1/unresolved_records_triage_latest.*` 清理 56 条 `unresolved_record`；
2. 处理 29 篇 `needs_targeted_rework` 的材料/数字化/不可恢复 backlog；
3. 对 67 篇 `blocked_missing_primary_material` 写材料缺失原因分类；
4. 对 4 篇 `review_status_not_in_public_set` 的 publication-grade 标记做状态命名复核；
5. 将 `doi__10.1055_s-0029-1185675` 路由到 source-staging/infra-recovery；
6. 做 300-500 条 stratified manual validation；
7. 生成 public schema/download/API/website。

当前 unresolved triage 结论：

| 维度 | 结果 |
| --- | --- |
| unresolved records | 56 |
| 涉及论文 | 3 |
| 涉及数据库 | DBAASP only |
| top paper | `doi__10.1038_s41522-024-00637-y`，30 rows |
| 主要 blocker | missing/unparsed supplement 28；synergy/FICI mapping ambiguous 25；material gap 2；row-level mapping 1 |
