# AMP Evidence Atlas / NAR Database Resource 路线图

更新时间：2026-06-22

## 1. 战略定位

本课题不应表述为“又一个更大的抗菌肽数据库”。推荐定位为：

> AMP Evidence Atlas: a primary-literature evidence alignment and provenance layer for antimicrobial peptide database curation.

中文表述：

> 本研究构建一个面向抗菌肽数据库的原始文献证据校准资源，对 APD6、DBAASP、DRAMP、CAMP、dbAMP 等数据库记录进行 source-located 审计，系统保留文献支持、文献冲突、序列/修饰未标准化、database-only 和 unresolved 等证据状态。

## 2. 为什么这是独立课题

- 现有 AMP 数据库通常以 peptide/activity/target 为中心，缺少逐条 primary-source evidence status。
- AMP 数据复用的关键难点不是只有“收录多少条”，而是序列修饰、D/L 构型、C 端酰胺化、单位换算、靶标粒度、机制标签是否被原文支持。
- 当前资源的创新是把数据库记录和论文原文证据之间的关系变成可查询、可下载、可复核的数据层。
- 该资源可服务数据库维护者、机器学习训练集构建者、AMP 机制研究者和系统评价作者。

## 3. 当前证据基础

当前核心报告：

```text
reports/database_vs_literature_difference_summary_latest.json
reports/database_vs_literature_difference_examples_latest.md
reports/database_vs_literature_difference_records_latest.csv
reports/source_recovery/material_source_recovery_status_latest.json
reports/all_reviewed_papers_aggregate_latest.json
```

当前强数字：

- 1471 篇有 database audit artifact 的论文；
- 139259 条数据库审计记录；
- 95941 条 `source_verified`；
- 43318 条非完全验证记录；
- 1304 篇论文含至少一条差异记录；
- 32550 条 `source_conflict`；
- 6472 条 `sequence_modified_not_normalized`；
- 4240 条 `database_only_no_primary_source`；
- 56 条 `unresolved_record`。

范围 reconciliation：历史队列 aggregate 为 1472 篇，但 v1 freeze 的 final-artifact universe 为 1471 篇。差出的 1 篇是 `doi__10.1055_s-0029-1185675`，其队列状态为 `initial_queue_failed` / `infrastructure_initial_queue_failed`，启动前缺 primary XML/PDF，当前无 final artifact。主 release 分母使用 1471；该论文进入 source-staging/infra-recovery backlog。

解释限制：

- 这些数字来自当前本地材料和 source-reviewed artifacts。
- 非 `source_verified` 不等于数据库错误。
- 差异类别是多标签，不能相加为 unique record 总数。
- 跨数据库差异绝对数不能直接解释为数据库质量排序。

## 4. NAR Database Issue 需要补齐的条件

NAR Database Issue 更看重公开数据库资源，而不是一次性分析报告。因此投稿前至少需要：

- 免费、无需登录、投稿时可完整审查的公开网站；
- 稳定 HTTPS URL；
- bulk download；
- API 或清晰的机器读取接口；
- schema 文档；
- release version；
- data availability 和 license；
- 维护计划；
- 和相似资源相比 substantially better 的说明；
- AI/Codex 使用披露；
- 人工验证和误差估计。

## 5. 最小可投稿资源形态

### 5.1 Public website

页面：

- Landing：范围、版本、引用方式、维护计划、限制；
- Search：按 peptide、database ID、DOI/PMID、organism、target、endpoint、mechanism、status、conflict type 查询；
- Record detail：展示数据库原字段、论文审查字段、source locator、status、caution、review provenance；
- Downloads：TSV/JSONL/SQLite/schema/checksum；
- Methods：两队列、六 worker、打回机制、质量门槛；
- Help：状态解释、示例查询、如何引用。

### 5.2 Public schema

建议表：

- `release_manifest`
- `paper`
- `peptide_entity`
- `database_record_assertion`
- `activity_observation`
- `mechanism_claim`
- `source_locator`
- `curation_decision`
- `conflict_or_caution`
- `blocked_or_excluded_paper`
- `schema_version`

### 5.3 Downloads

```text
amp_evidence_release_<version>.jsonl
papers.tsv
peptides.tsv
database_record_audits.tsv
activity_observations.tsv
mechanism_claims.tsv
conflicts_and_cautions.tsv
excluded_blocked_papers.tsv
schemas/*.json
checksums.txt
README.md
LICENSES.tsv
```

### 5.4 API

```text
GET /api/v1/releases
GET /api/v1/search?q=...
GET /api/v1/peptides/{id}
GET /api/v1/papers/{paper_id}
GET /api/v1/database-records/{source}/{accession}
GET /api/v1/activities
GET /api/v1/mechanisms
GET /api/v1/conflicts
GET /api/v1/downloads/{release}
GET /api/v1/schemas/{name}
```

## 6. 投稿前优先级

### P0：冻结 v1 数据版本

- 生成 `release_manifest`；
- 披露 1471 vs 1472 reconciliation；
- 明确 inclusion/exclusion；
- 输出 checksums；
- 不再让公开数字随内部队列漂移。

### P0：统一统计口径和分母

必须报告：

- paper-level；
- database audit row-level；
- peptide/entity-level；
- activity/toxicity row-level；
- mechanism claim-level；
- database-specific denominators。

当前冻结候选版的字段字典、分母定义和交叉表解释已经沉淀在：

```text
docs/NAR_FREEZE_V1_DATA_DICTIONARY.md
reports/nar_resource_freeze_v1/README.md
```

### P1：人工分层验证

建议 300-500 条记录，按 database × status × difference type 分层。报告：

- precision；
- false positive rate；
- false negative rate；
- inter-annotator agreement；
- critical/major/minor error。

### P1：处理非 publication-grade 子集

当前应单独列出：

- `needs_targeted_rework`；
- `blocked_missing_primary_material`；
- metadata-only；
- weak-source；
- unresolved rows。

主分析优先使用 publication-grade 子集，其他作为 sensitivity/backlog。

### P1：公开网站和下载包

没有公开资源，不建议投 NAR Database Issue。

### P2：数据库维护者反馈

向 APD6、DBAASP、DRAMP、CAMP、dbAMP 发送 discrepancy package，记录反馈与修正。

### P2：许可与版权

只发布事实性抽取、locator、状态标签和可再分发派生字段；不发布受版权保护全文/PDF/表格原件。

## 7. 还要不要继续补论文/序列/材料

### 应补

- 16 篇 recovered partial source：材料已恢复，应完成审计或逐篇说明 blocker。
- 56 条 unresolved_record：数量小，投稿前应逐条清理或解释。
- 100 篇 excluded / non-publication-grade：优先处理 29 篇 `needs_targeted_rework` 的材料/数字化/不可恢复 backlog，67 篇 `blocked_missing_primary_material` 明确材料原因，4 篇 `review_status_not_in_public_set` 做状态命名复核。
- high-signal weak-source 子集：优先 quantitative endpoint + direct mechanism assay + multi-database linkage。
- sequence/modification schema：比单纯增加序列数更重要。

### 可不全补

- 739 篇 metadata-only：可作为 best-effort unrecovered backlog。
- 所有 weak-source 长尾：可进入 next release queue。
- 受版权/缺失 supplement 阻塞的图表 exact value：保留 unresolved 即可。

## 8. 论文叙事

推荐标题：

- `AMP Evidence Atlas: a primary-literature evidence layer for antimicrobial peptide database curation`
- `Reconciling antimicrobial peptide database annotations with primary literature evidence`
- `A provenance-aware audit resource for antimicrobial peptide databases`

核心摘要句：

> We present a primary-literature-grounded evidence alignment resource for antimicrobial peptide databases that separates source-supported annotations from evidence discordance, missing provenance, modification-normalization issues, and database-only assertions.

## 9. 必须披露

- AI/Codex 辅助了抽取、审查或质量控制；
- 人工 curator 和验证流程如何约束 AI 输出；
- 非 `source_verified` 不等于错误；
- `accepted_with_cautions` 不是 clean；
- 缺失材料和不可恢复记录如何处理；
- 差异类别是多标签；
- 许可和再发布边界；
- 长期维护和更新计划。

## 10. 第一阶段执行清单

本阶段先完成：

1. 文档沉淀：本路线图和可复现 runbook；
2. v1 freeze candidate；
3. 统一口径 summary；
4. 数据库分母表；
5. 交叉表：status × database、category × database、status × source_table、review_status × database。

后续阶段再做：

1. 100 篇 excluded / non-publication-grade 清理；
2. 16 篇 recovered partial 审计；
3. 人工分层验证；
4. public schema/release builder；
5. website/API/download；
6. NAR pre-submission inquiry。
