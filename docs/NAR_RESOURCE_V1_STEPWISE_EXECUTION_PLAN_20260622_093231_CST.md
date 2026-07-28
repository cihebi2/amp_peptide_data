# AMP Evidence Atlas / NAR Resource v1 分步执行计划

创建时间：2026-06-22 09:32:31 CST  
工作目录：`/root/work/抗菌肽/数据库/batch/4-team`  
当前权威口径来源：`reports/nar_resource_freeze_v1/release_manifest_latest.json`  
当前 release id：`amp-evidence-audit-v1-freeze-candidate`  
当前状态：`freeze_candidate`，不能表述为 NAR-ready public database。

## 1. 目标

把当前内部论文审查和数据库审计成果，逐步推进为可复现、可公开审查、可支撑 NAR Database Resource 投稿的 v1 resource candidate。

本计划只定义分步执行和确认门槛。每一步完成后都要留下可复现产物、验证证据和是否进入下一步的判断，避免一次性推进过多导致口径漂移或质量不可控。

## 2. 当前最新快照

以下数字以 `reports/nar_resource_freeze_v1/release_manifest_latest.json` 为准，manifest 生成时间为 `2026-06-21T16:36:51+00:00`。

| 指标 | 当前值 |
| --- | ---: |
| paper final artifacts | 1471 |
| public v1 candidate papers | 1371 |
| excluded / non-publication-grade papers | 100 |
| database audit rows | 139259 |
| source-verified rows | 95941 |
| non-source-verified rows | 43318 |
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

当前 review status 快照：

| review status / flag | count |
| --- | ---: |
| `accepted_with_cautions` | 1371 |
| `needs_targeted_rework` | 29 |
| `blocked_missing_primary_material` | 67 |
| `publication_grade` | 2 |
| `publication_grade_ready` | 1 |
| `publication_grade_with_cautions` | 1 |

解释边界：

- `accepted_with_cautions` 不是 clean；caution、conflict、database-only 和 unresolved 必须公开保留。
- non-source-verified 不等于数据库错误，只表示当前原始文献证据层面存在冲突、来源缺口、修饰标准化问题、database-only 断言或无法判定。
- database denominators 是当前 final artifacts 中的 audit-row 分母，不是 APD6/DBAASP/DRAMP/CAMP/dbAMP 的原始全库分母。
- 当前 release 已有本地 preview/API、bulk downloads、schema/versioned package 和 manual stratified validation manifest；仍缺公开 HTTPS 部署、license/source-version table 完成稿、人工验证结果和 manuscript disclosure。

## 3. 已发现的优先问题

### 3.1 文档口径漂移

最新 README 已经反映 `1371 / 100 / 95941 / 43318 / 115184 / 4772`，但以下文档仍包含旧数字，需要作为第一步修复：

- `docs/NAR_FREEZE_V1_DATA_DICTIONARY.md`
- `docs/NAR_DATABASE_RESOURCE_ROADMAP.md`

已发现旧数字包括：

- `public_v1_candidate_papers = 1344`
- `excluded_or_non_publication_grade_papers = 127`
- `source_verified_rows = 95239`
- `non_source_verified_rows = 44020`
- `activity_records = 113873`
- `mechanism_claims = 4764`
- `source_conflict = 33332`
- `sequence_modified_not_normalized = 6382`
- `database_only_no_primary_source = 4250`

### 3.2 投稿表述风险

当前只能说：

> v1 freeze candidate evidence-audit snapshot。

不能说：

- NAR-ready public database；
- 所有 accepted 都是 clean；
- non-source-verified 都是数据库错误；
- 当前分母代表各数据库全量原始记录；
- AI 自动审查等同于人工金标准。

### 3.3 后续工作不应继续盲目加论文

目前更重要的是把已有成果变成可公开复核的资源包、差异例证、分层抽样审计和 NAR 写作材料。继续补论文只应针对高价值 blocker 或后续 release backlog。

## 4. 分步执行总览

| 步骤 | 状态 | 目标产物 | 是否允许推进下一步 |
| --- | --- | --- | --- |
| Step 0 | done | 本计划文档 | 已完成 |
| Step 1 | done | 修复 roadmap/data dictionary 的旧数字和口径漂移 | 已完成，见第 12 节 |
| Step 2 | done | 生成 versioned public release package 骨架 | 已完成，见第 12 节 |
| Step 3 | done | 生成数据库 vs 论文差异真实例子文档 | 已完成，见第 12 节 |
| Step 4 | done | 生成 manual stratified validation manifest | 已完成，见第 12 节 |
| Step 5 | done | 设计/生成 public website/API/downloads 最小资源形态 | 已完成，见第 12 节 |
| Step 6 | pilot20 true-source done | 对 public candidate 做 accepted sample audit / validation | 20 篇真实源材料复审已完成；发现 rework/best-effort 问题，420 条正式验证前需先修复流程 |
| Step 7 | pending | 形成 NAR manuscript disclosure skeleton | claims 与 release package 一致后推进 |

## 5. Step 1：统一 freeze 口径和文档数字

目标：

- 让 `docs/NAR_FREEZE_V1_DATA_DICTIONARY.md`、`docs/NAR_DATABASE_RESOURCE_ROADMAP.md` 和 `reports/nar_resource_freeze_v1/README.md` 与最新 manifest 一致。
- 明确所有数字从 `release_manifest_latest.json` 派生。
- 保留 `freeze_candidate`、非 clean、非错误断言、audit-row denominator 等解释边界。

拟执行：

```bash
python scripts/build_nar_resource_freeze_v1.py
python -m json.tool reports/nar_resource_freeze_v1/release_manifest_latest.json >/dev/null
python -m json.tool reports/nar_resource_freeze_v1/unified_scope_summary_latest.json >/dev/null
rg -n "1344|127|95239|44020|113873|4764|33332|6382|4250" docs/NAR_FREEZE_V1_DATA_DICTIONARY.md docs/NAR_DATABASE_RESOURCE_ROADMAP.md
```

完成条件：

- 旧数字不再出现在需要当前快照口径的上下文中。
- 如果保留历史数字，必须标注为 historical/previous snapshot，不能混入当前 freeze。
- 文档中明确当前 snapshot 是 `1371 / 100 / 95941 / 43318 / 115184 / 4772`。

停止条件：

- 如果 `build_nar_resource_freeze_v1.py` 重新生成出不同数字，先暂停并解释 drift 来源，不继续改文档。

## 6. Step 2：生成 v1 RC public release package

目标：

建立一个 versioned release 目录，例如：

```text
releases/amp_evidence_atlas_v1_rc1/
```

建议包含：

```text
README.md
release_manifest.json
checksums.txt
LICENSES.tsv
schemas/
papers.tsv
database_record_audits.tsv
activity_observations.tsv
mechanism_claims.tsv
conflicts_and_cautions.tsv
excluded_blocked_papers.tsv
```

原则：

- 发布事实性抽取、locator、状态标签、派生字段和 schema。
- 不发布受版权保护的全文、PDF、原始补充表格或大段原文。
- 每个导出文件必须能追溯到 `papers/*/final/` 或 `reports/nar_resource_freeze_v1/`。

完成条件：

- release package 有固定目录、manifest、checksums。
- TSV/JSON schema 可读。
- 文件行数与 freeze summary 可解释对应。

## 7. Step 3：生成数据库 vs 论文差异真实例子

目标：

用真实案例向审稿人说明“数据库标注”和“论文证据审查”到底差在哪里。

建议输出：

```text
reports/nar_resource_freeze_v1/database_vs_paper_difference_examples_v1_<timestamp>.md
reports/nar_resource_freeze_v1/database_vs_paper_difference_examples_v1_<timestamp>.csv
```

至少覆盖：

- sequence / modification / terminal chemistry 差异；
- activity value / unit / endpoint 差异；
- target / organism 粒度差异；
- mechanism / claim scope 差异；
- database-only / no primary-source support；
- source conflict 但不能直接判数据库错误的谨慎案例。

每个例子应包含：

- paper_id / DOI / PMID；
- database / database accession or row id；
- 数据库原标注；
- 论文审查得到的字段；
- source locator 或 final artifact path；
- status；
- 为什么是差异，不应如何过度解释。

完成条件：

- 每个例子能从本地 final artifact 或报告追溯。
- 不使用无 locator 的概括性断言。

## 8. Step 4：生成 manual stratified validation manifest

目标：

为 NAR 投稿准备误差估计，而不是继续无边界地全量重跑。

建议抽样：

- 300-500 条 database audit rows；
- 按 `database x status x difference_category` 分层；
- 包含 high-risk categories：activity value/unit、sequence/modification、mechanism scope、database-only、unresolved。

建议输出：

```text
reports/nar_resource_freeze_v1/manual_validation/validation_manifest_<timestamp>.csv
reports/nar_resource_freeze_v1/manual_validation/validation_protocol_<timestamp>.md
```

完成条件：

- 抽样逻辑可复现；
- 每条样本有 paper_id、database、status、category、source artifact path；
- 明确 reviewer 判定字段：pass、minor_error、major_error、critical_error、needs_rework、unverifiable。

## 9. Step 5：设计 public website / API / downloads 最小资源形态

目标：

让资源具备 NAR Database Issue 需要的可公开使用形态。

最小页面：

- Landing：范围、版本、引用、限制；
- Search：按 peptide、database ID、DOI/PMID、organism、target、endpoint、mechanism、status 查询；
- Record detail：数据库字段、论文审查字段、source locator、status、caution、provenance；
- Downloads：TSV/JSONL/SQLite/schema/checksum；
- Methods：两队列、六 worker、打回机制、质量门槛；
- Help：状态解释和示例查询。

最小 API：

```text
GET /api/v1/releases
GET /api/v1/search?q=...
GET /api/v1/papers/{paper_id}
GET /api/v1/database-records/{source}/{accession}
GET /api/v1/activities
GET /api/v1/mechanisms
GET /api/v1/conflicts
GET /api/v1/downloads/{release}
GET /api/v1/schemas/{name}
```

完成条件：

- 本地 preview 能打开；
- 至少可搜索 paper/database/status；
- downloads 页面能指向 release package。

## 10. Step 6：accepted/public subset 的质量抽样审计

目标：

给 `1371` 篇 public v1 candidate 和 `139259` 条 audit rows 提供可发表的质量边界。

必须区分：

- paper-level accepted-with-cautions；
- database-row source_verified/source_conflict/database_only 等状态；
- activity row；
- mechanism claim；
- unresolved/backlog。

完成条件：

- 产生 validation summary；
- 给出 precision/error-rate/risk categories；
- 对失败样本进行 targeted rework 或明确降级为 caution/exclusion；
- 不把抽样通过外推成全量 clean。

## 11. Step 7：NAR manuscript disclosure skeleton

目标：

形成一份可供论文写作的骨架，避免夸大。

建议章节：

- Resource overview；
- Data sources and versioning；
- Primary literature evidence alignment；
- Curation workflow and worker roles；
- Evidence status ontology；
- Release scope and denominators；
- Database-vs-literature discordance examples；
- Validation and limitations；
- Availability, license, maintenance；
- AI/Codex assistance disclosure；
- Backlog and future releases。

完成条件：

- manuscript claims 与 release package manifest 一致；
- 所有关键数字可由 manifest 或 exported tables 复现；
- 清楚披露 `freeze_candidate` 到 public database 之间的剩余工作。

## 12. 当前确认状态

当前已确认并执行到 Step 5：

- [x] 读取当前 freeze manifest。
- [x] 核对当前最新分母和状态数字。
- [x] 发现并记录文档旧数字漂移。
- [x] 写入本分步执行计划。
- [x] Step 1 已修改 `docs/NAR_FREEZE_V1_DATA_DICTIONARY.md` 和 `docs/NAR_DATABASE_RESOURCE_ROADMAP.md` 的当前快照口径。
- [x] Step 2 已生成 `releases/amp_evidence_atlas_v1_rc1/` public release package 骨架和初版下载表。
- [x] Step 3 已生成数据库 vs 论文差异真实例子 CSV/Markdown。
- [x] Step 4 已生成 manual stratified validation manifest、protocol 和 summary。
- [x] Step 5 已生成 local public website/API/downloads 最小资源形态。
- [x] Step 6 已执行 20 篇 workflow pilot；注意这只是结构化/status-evidence pilot，不等同于完整人工/源材料复审。
- [x] Step 6 已执行 20 篇 Codex CLI true source-review pilot，见第 12 节新增记录。
- [x] Step 6 pilot20 已完成 worker-6 full closure：16 篇 `accepted_with_cautions`、3 篇 `blocked_missing_primary_material`、1 篇 `needs_targeted_rework`；accepted subset 机制 ontology bad class 为 0。
- [ ] Step 6 的 420 条 manual validation manifest 尚未完整人工/worker 复审。
- [ ] Step 7 尚未生成 manuscript disclosure skeleton。

### Step 1 执行记录

执行时间：2026-06-22 09:37:15 CST

已执行：

```bash
python scripts/build_nar_resource_freeze_v1.py
python -m json.tool reports/nar_resource_freeze_v1/release_manifest_latest.json >/dev/null
python -m json.tool reports/nar_resource_freeze_v1/unified_scope_summary_latest.json >/dev/null
```

确认当前 manifest 口径稳定为：

- `paper_final_artifact_count = 1471`
- `public_v1_candidate_papers = 1371`
- `excluded_or_non_publication_grade_papers = 100`
- `database_audit_rows = 139259`
- `source_verified_rows = 95941`
- `non_source_verified_rows = 43318`
- `activity_records = 115184`
- `mechanism_claims = 4772`

同步修复：

- `docs/NAR_FREEZE_V1_DATA_DICTIONARY.md`
- `docs/NAR_DATABASE_RESOURCE_ROADMAP.md`

同时更新 `excluded_or_non_publication_grade_papers = 100` 的构成：

- `needs_targeted_rework = 29`
- `blocked_missing_primary_material = 67`
- `review_status_not_in_public_set = 4`

### Step 2 执行记录

执行时间：2026-06-22 09:48:42 CST

新增可复现构建脚本：

```text
scripts/build_nar_public_release_package.py
```

安全护栏：该脚本只覆盖带有本脚本生成标记或同 release id manifest 的目标目录，避免误删手工目录。

已执行：

```bash
python scripts/build_nar_resource_freeze_v1.py
python -m py_compile scripts/build_nar_public_release_package.py
python scripts/build_nar_public_release_package.py
python -m json.tool releases/amp_evidence_atlas_v1_rc1/release_manifest.json >/dev/null
(cd releases/amp_evidence_atlas_v1_rc1 && sha256sum -c checksums.txt)
```

生成目录：

```text
releases/amp_evidence_atlas_v1_rc1/
```

核心文件：

```text
README.md
release_manifest.json
checksums.txt
LICENSES.tsv
schemas/
papers.tsv
database_record_audits.tsv
activity_observations.tsv
mechanism_claims.tsv
conflicts_and_cautions.tsv
excluded_blocked_papers.tsv
database_denominators.tsv
crosstab_status_by_database.tsv
crosstab_category_by_database.tsv
crosstab_status_by_source_table.tsv
crosstab_review_status_by_database.tsv
```

验证行数：

| 文件 | 行数 |
| --- | ---: |
| `papers.tsv` | 1471 |
| `database_record_audits.tsv` | 139259 |
| `activity_observations.tsv` | 115184 |
| `mechanism_claims.tsv` | 4772 |
| `conflicts_and_cautions.tsv` | 49438 |
| `excluded_blocked_papers.tsv` | 100 |
| `database_denominators.tsv` | 6 |
| `crosstab_status_by_database.tsv` | 23 |
| `crosstab_category_by_database.tsv` | 40 |
| `crosstab_status_by_source_table.tsv` | 253 |
| `crosstab_review_status_by_database.tsv` | 20 |

验证结论：

- `release_manifest.json` JSON 校验通过。
- `schemas/*.json` JSON 校验通过。
- `sha256sum -c checksums.txt` 通过。
- `releases/amp_evidence_atlas_v1_rc1/.generated_by_build_nar_public_release_package` 已写入，用于后续安全覆盖判断。
- manifest 行数与实际 TSV 行数一致。
- release 目录未复制 PDF、XML、JPG、PNG、TIFF 等源材料文件。
- 当前状态仍是 `release_package_candidate_not_public_nar_submission_ready`，不能表述为已公开 NAR-ready resource。

### Step 3 执行记录

执行时间：2026-06-22 10:36:46 CST

新增可复现案例生成脚本：

```text
scripts/generate_nar_difference_examples_v1.py
```

已执行：

```bash
python -m py_compile scripts/generate_nar_difference_examples_v1.py
python scripts/generate_nar_difference_examples_v1.py --per-category 5
```

生成文件：

```text
reports/nar_resource_freeze_v1/database_vs_paper_difference_examples_v1_20260622_103619.csv
reports/nar_resource_freeze_v1/database_vs_paper_difference_examples_v1_20260622_103619.md
reports/nar_resource_freeze_v1/database_vs_paper_difference_examples_v1_latest.csv
reports/nar_resource_freeze_v1/database_vs_paper_difference_examples_v1_latest.md
```

案例覆盖：

| 类别 | 例子数 |
| --- | ---: |
| `sequence_or_modification` | 5 |
| `activity_value_or_unit` | 5 |
| `target_or_organism` | 5 |
| `mechanism_or_claim_scope` | 5 |
| `database_only_no_primary_source` | 5 |
| `row_granularity` | 5 |
| `unresolved_or_missing_material` | 5 |

验证结论：

- 共 35 条真实案例。
- 7 个目标差异类别全部覆盖。
- 每条案例都有 `release_table_path` 和 `final_artifact_path`。
- 所有 `release_table_path` 和 `final_artifact_path` 均存在。
- 无重复 `paper_id + source_id` 组合，避免同一数据库记录重复占位。
- 输出未复制 PDF、XML、图片、补充材料原件；只保留 release 表路径、final artifact 路径和 locator 摘要。
- 输出中未保留 `primary_source_statement`、`primary_source_support`、`quoted_text`、`raw_text`、`support_text`、`supports` 等源文本 JSON 键。

### Step 4 执行记录

执行时间：2026-06-22 10:43:09 CST

新增可复现抽样脚本：

```text
scripts/generate_manual_stratified_validation_manifest.py
```

已执行：

```bash
python -m py_compile scripts/generate_manual_stratified_validation_manifest.py
python scripts/generate_manual_stratified_validation_manifest.py
python -m json.tool reports/nar_resource_freeze_v1/manual_validation/validation_summary_latest.json >/dev/null
```

生成文件：

```text
reports/nar_resource_freeze_v1/manual_validation/validation_manifest_20260622_104222.csv
reports/nar_resource_freeze_v1/manual_validation/validation_protocol_20260622_104222.md
reports/nar_resource_freeze_v1/manual_validation/validation_summary_20260622_104222.json
reports/nar_resource_freeze_v1/manual_validation/validation_manifest_latest.csv
reports/nar_resource_freeze_v1/manual_validation/validation_protocol_latest.md
reports/nar_resource_freeze_v1/manual_validation/validation_summary_latest.json
```

抽样设计：

- 样本数：420，位于预设 300-500 范围内。
- deterministic seed：`amp-evidence-atlas-v1-rc1-validation-20260622`。
- 分层轴：database、audit status、primary validation category。
- 状态配额：`source_verified=120`、`source_conflict=120`、`sequence_modified_not_normalized=70`、`database_only_no_primary_source=60`、`unresolved_record=50`。
- 数据库最低覆盖：`APD6>=25`、`CAMP>=25`、`DRAMP>=45`、`dbAMP>=25`、`unknown>=3`。

实际样本分布：

| 维度 | 分布 |
| --- | --- |
| status | `source_verified=120`; `source_conflict=120`; `sequence_modified_not_normalized=70`; `database_only_no_primary_source=60`; `unresolved_record=50` |
| database | `DBAASP=254`; `DRAMP=73`; `APD6=33`; `CAMP=31`; `dbAMP=26`; `unknown=3` |
| primary category | `source_verified_baseline=120`; `database_only_no_primary_source=74`; `activity_value_or_unit=62`; `unresolved_or_missing_material=56`; `mechanism_or_claim_scope=47`; `sequence_or_modification=24`; `row_granularity=21`; `target_or_organism=15`; `other=1` |

验证结论：

- `validation_manifest_latest.csv` 共 420 条。
- 状态配额完全匹配。
- 数据库最低覆盖均满足。
- raw multilabel categories 覆盖 `activity_value_or_unit`、`sequence_or_modification`、`target_or_organism`、`database_only_no_primary_source`、`row_granularity`、`unresolved_or_missing_material`、`mechanism_or_claim_scope`。
- 所有 `release_table_path` 和 `final_artifact_path` 均存在。
- 无重复 `audit_record_id`。
- `reviewer_decision`、`reviewer_error_class`、`reviewer_notes`、`reviewed_by`、`reviewed_at` 保持空白，等待人工/复审填写。

### Step 5 执行记录

执行时间：2026-06-22 10:52:28 CST

新增本地 preview/API：

```text
web_resource_v1/server.py
web_resource_v1/static/index.html
web_resource_v1/static/styles.css
web_resource_v1/static/app.js
web_resource_v1/README.md
```

设计选择：

- 使用 Python 标准库 `ThreadingHTTPServer`，不引入 npm/pip 依赖。
- 服务端流式读取 `releases/amp_evidence_atlas_v1_rc1/*.tsv`，避免浏览器一次性加载 233MB `database_record_audits.tsv`。
- UI 提供 Landing、Search、Downloads、Methods、Help。
- Search 支持 `paper_id`、`database`、`status`、`category`、文本 query、limit。
- Downloads 只开放 release package 内的 `.tsv`、`.json`、`.txt`、`.md` 文件，不开放 PDF/XML/图片/补充材料原件。

运行命令：

```bash
python web_resource_v1/server.py --host 127.0.0.1 --port 8989
```

本地地址：

```text
http://127.0.0.1:8989
```

API 覆盖：

```text
GET /api/v1/releases
GET /api/v1/search?q=...&database=...&status=...&category=...
GET /api/v1/papers/{paper_id}
GET /api/v1/database-records/{database}/{source_id}
GET /api/v1/activities
GET /api/v1/mechanisms
GET /api/v1/conflicts
GET /api/v1/downloads
GET /api/v1/downloads/{filename}
GET /api/v1/schemas
GET /api/v1/schemas/{name}
```

Smoke test 证据：

- 首页 GET 成功返回 `<!doctype html>`。
- `/api/v1/releases` 返回 `amp-evidence-atlas-v1-rc1 / v1_rc1 / release_package_candidate_not_public_nar_submission_ready`。
- release scope 返回 `paper_final_artifact_count=1471`、`public_v1_candidate_papers=1371`、`database_audit_rows=139259`、`non_source_verified_rows=43318`。
- `/api/v1/search?q=DBAASPS_18493&status=source_conflict&limit=3` 返回 `matched_rows=4`、`returned_rows=3`、`scanned_rows=139259`。
- `/api/v1/downloads` 返回 15 个 allowlisted 下载文件。
- `/api/v1/schemas` 返回 11 个 schema。
- `/api/v1/papers/doi__10.1002_cbic.202100151` 返回 paper detail，review status 为 `accepted_with_cautions`，并返回 database/conflict 子结果。

当前限制：

- 这是 local preview，不是公开 HTTPS deployment。
- 搜索为本地 TSV 流式扫描，适合审查和演示；若要公网服务，需要后续改成 SQLite/Parquet/Postgres 或预建索引。
- 仍不能称为 NAR-ready public database，直到公开部署、许可/source-version 表、人工验证结果和 manuscript disclosure 完成。

### Step 6 Pilot 20 执行记录

执行时间：2026-06-22 11:12:51 CST

新增可复现 pilot 脚本：

```text
scripts/run_validation_pilot20.py
```

已执行：

```bash
python -m py_compile scripts/run_validation_pilot20.py
python scripts/run_validation_pilot20.py
python -m json.tool reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_summary_latest.json >/dev/null
```

生成文件：

```text
reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_manifest_20260622_111251.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_results_20260622_111251.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_summary_20260622_111251.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_report_20260622_111251.md
reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_rework_tickets_20260622_111251.jsonl
reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_manifest_latest.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_results_latest.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_report_latest.md
reports/nar_resource_freeze_v1/manual_validation/pilot20/pilot20_rework_tickets_latest.jsonl
```

抽样说明：

- 目标是测试 Step 6 validation workflow 的结构化可用性，不是完整 420 条人工验证。
- 原计划每个 status 各取 4 篇；但 validation manifest 中 `unresolved_record` 只有 3 篇唯一 paper 可作为 sentinel，因此最终分配为 `source_verified=4`、`source_conflict=5`、`sequence_modified_not_normalized=4`、`database_only_no_primary_source=4`、`unresolved_record=3`。
- 选择逻辑加入 database round-robin，避免 pilot 被单一数据库过度占据。

Pilot 结果：

| metric | value |
| --- | ---: |
| selected unique papers | 20 |
| selected validation rows | 20 |
| `pass` | 20 |
| `minor_error` | 0 |
| `major_error` | 0 |
| `critical_error` | 0 |
| `needs_rework` | 0 |
| `unverifiable` | 0 |
| rework tickets | 0 |

状态覆盖：

| status | rows |
| --- | ---: |
| `source_verified` | 4 |
| `source_conflict` | 5 |
| `sequence_modified_not_normalized` | 4 |
| `database_only_no_primary_source` | 4 |
| `unresolved_record` | 3 |

数据库覆盖：

| database | rows |
| --- | ---: |
| `DBAASP` | 7 |
| `DRAMP` | 4 |
| `dbAMP` | 4 |
| `APD6` | 4 |
| `CAMP` | 1 |

复核命令：

```bash
python - <<'PY'
import csv, json
from pathlib import Path
base=Path('reports/nar_resource_freeze_v1/manual_validation/pilot20')
manifest=base/'pilot20_manifest_latest.csv'
results=base/'pilot20_results_latest.csv'
tickets=base/'pilot20_rework_tickets_latest.jsonl'
summary=json.loads((base/'pilot20_summary_latest.json').read_text())
rows=list(csv.DictReader(manifest.open()))
res=list(csv.DictReader(results.open()))
print('manifest_rows', len(rows))
print('unique_papers', len({r['paper_id'] for r in rows}))
print('results_rows', len(res))
print('reviewer_decisions', {d: sum(1 for r in res if r['reviewer_decision']==d) for d in sorted({r['reviewer_decision'] for r in res})})
print('tickets_bytes', tickets.stat().st_size)
print('summary_selected_paper_count', summary['selected_paper_count'])
print('summary_ticket_count', summary['ticket_count'])
PY
```

复核结论：

- `pilot20_manifest_latest.csv` 有 20 行，覆盖 20 篇唯一 paper。
- `pilot20_results_latest.csv` 有 20 行，`reviewer_decision=pass` 为 20。
- `pilot20_rework_tickets_latest.jsonl` 大小为 0 bytes，表示本轮 structural/status-evidence pilot 未生成 rework ticket。
- 本轮 `pass` 只表示 release row、final artifact、review report、record-in-final 和 status-specific rationale 的结构化检查通过；不能外推为每篇原始材料都已被重新人工/worker 深读，也不能外推为 420 条 validation manifest 全部通过。

### Step 6 True Source-Review Pilot 20 执行记录

执行时间：2026-06-22 11:42-12:31 CST

新增可复现脚本：

```text
scripts/generate_pilot20_true_review_packets.py
scripts/run_pilot20_true_source_reviews.py
scripts/summarize_pilot20_true_source_reviews.py
```

执行命令：

```bash
python -m py_compile scripts/generate_pilot20_true_review_packets.py scripts/run_pilot20_true_source_reviews.py scripts/summarize_pilot20_true_source_reviews.py
python scripts/generate_pilot20_true_review_packets.py
bash reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/run_true_source_reviews_20.sh
python scripts/summarize_pilot20_true_source_reviews.py
```

运行设置：

- `codex exec`
- model：`gpt-5.5`
- reasoning：`model_reasoning_effort="xhigh"`
- 并发：4 路
- 每篇 timeout：3600 秒
- 输入：`reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/packet_index_latest.csv`
- 输出：每个 packet 目录下的 `true_review_result.json`；必要时写 `rework_ticket.json`

生成/汇总文件：

```text
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/packet_index_latest.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/packet_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/runner/true_source_review_status_latest.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/runner/true_source_review_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/summary/pilot20_true_source_review_results_latest.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/summary/pilot20_true_source_review_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/summary/pilot20_true_source_review_report_latest.md
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/summary/pilot20_true_source_review_rework_tickets_latest.jsonl
```

Runner 结果：

| metric | value |
| --- | ---: |
| selected papers | 20 |
| valid result JSON | 20 |
| runner `completed_valid_result` | 20 |
| clean `pass_source_review` | 0 |
| `accepted_with_cautions_confirmed` | 1 |
| `needs_targeted_rework` | 5 |
| `unverifiable_best_effort` | 14 |
| consolidated rework/material tickets | 11 |
| total rework targets | 18 |
| total cautions | 91 |
| total best-effort limits | 65 |

按原始 validation status 的结果：

| status | true source-review outcome |
| --- | --- |
| `source_verified` | `needs_targeted_rework=1`; `unverifiable_best_effort=3` |
| `source_conflict` | `accepted_with_cautions_confirmed=1`; `unverifiable_best_effort=4` |
| `sequence_modified_not_normalized` | `needs_targeted_rework=2`; `unverifiable_best_effort=2` |
| `database_only_no_primary_source` | `needs_targeted_rework=2`; `unverifiable_best_effort=2` |
| `unresolved_record` | `unverifiable_best_effort=3` |

解释：

- 早先 structural/status-evidence pilot 的 `pass=20` 只表示路径和结构可用。
- 这次 true source-review 没有任何一篇达到 clean `pass_source_review`。
- 这不表示 20 篇数据库标注都错；多数是 caution、材料限制、机制 ontology 修复、补充材料/定位证据不足，或不能把结果提升为 clean acceptance。
- `needs_targeted_rework` 或非空 `rework_targets` 必须回传给 owner worker 修复，再由 worker-6 重新把关。
- 本轮还暴露一个流程问题：旧 prompt 要求 reviewer 自证模型/effort，导致 14 篇被降级为 `unverifiable_best_effort`；但 runner stderr/header 已记录 `model: gpt-5.5`、`reasoning effort: xhigh`。`scripts/generate_pilot20_true_review_packets.py` 已修复未来 prompt：runner 命令/运行头可作为模型证明，除非运行状态相互矛盾。
- 现有 20 篇结果保留原始 reviewer decision，不事后改写；后续扩展到 420 条前，应先用修复后的 prompt 对这 20 篇做一次 targeted rerun 或 worker-6 re-adjudication，确认 model-provenance 误判不再主导结果。

当前 Step 6 判断：

- true source-review pilot 已完成；
- Step 6 不能进入 420 条正式验证扩展，直到：
  - consolidated tickets 被分派到 owner lane；
  - 至少完成 `needs_targeted_rework=5` 和非空 rework target 的打回闭环；
  - 修复后的 prompt 在 pilot 上不再系统性产生 model-provenance downgrade；
  - worker-6 对修复后结果重新判定并写入 summary。

### Step 6 Owner Dispatch / Worker-6 Readjudication 执行记录

执行时间：2026-06-22 13:02:38 CST

新增可复现脚本：

```text
scripts/dispatch_pilot20_rework_packets.py
scripts/readjudicate_pilot20_after_provenance_fix.py
```

执行命令：

```bash
python -m py_compile scripts/dispatch_pilot20_rework_packets.py scripts/readjudicate_pilot20_after_provenance_fix.py
python scripts/dispatch_pilot20_rework_packets.py
python scripts/readjudicate_pilot20_after_provenance_fix.py
```

生成 durable owner-worker handoff：

```text
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch_index_latest.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/dispatch_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/<dispatch-id>/dispatch_packet.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/<dispatch-id>/OWNER_REWORK_PROMPT.md
```

Dispatch 结果：

| metric | value |
| --- | ---: |
| dispatch packets | 11 |
| `worker-5_mechanism_ontology_extractor` | 9 |
| `worker-2_main_text_assay_extractor` | 2 |
| severity `blocking` | 5 |
| severity `major` | 6 |
| target queue `analysis` | 8 |
| target queue `material_extraction` | 3 |

Worker-6 provenance 修复后重裁定：

```text
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_readjudication/pilot20_worker6_readjudication_latest.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_readjudication/pilot20_worker6_readjudication_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_readjudication/pilot20_worker6_readjudication_report_latest.md
```

重裁定逻辑：

- 只有当 packet 的 `codex_exec.stderr.log` 运行头证明 `model: gpt-5.5` 和 `reasoning effort: xhigh` 时，才移除 model-provenance downgrade。
- 任何非空 `rework_targets` 仍强制为 `needs_targeted_rework`。
- `accepted_with_cautions_confirmed` 不是 clean，只表示 conflict/caution 可保留且无结构化 hard rework target。
- 本重裁定不编辑 `papers/<paper_id>/final/`，只给出批量 worker-6 风险归类。

重裁定结果：

| decision | count |
| --- | ---: |
| `accepted_with_cautions_confirmed` | 5 |
| `needs_targeted_rework` | 15 |
| clean `pass_source_review` | 0 |

解释：

- 模型 provenance 误判已从主结论中剥离；20/20 的 runner header 都证明了 `gpt-5.5/xhigh`。
- 剥离后仍有 15/20 需要 targeted rework，说明真实问题不只是 prompt 自证误判。
- 目前 owner dispatch 只是 durable handoff，不等于 owner worker 已完成修复。
- 下一步应先处理 11 个 dispatch packets，其中 9 个机制 ontology 修复、2 个 activity/material 相关修复；修复后再由 worker-6 更新/重审对应 final artifacts。

### Step 6 Owner-Worker Response / Ontology QC 执行记录

执行时间：2026-06-22 13:09-13:34 CST

新增可复现脚本：

```text
scripts/run_pilot20_owner_rework_responses.py
scripts/summarize_pilot20_owner_responses.py
scripts/check_pilot20_mechanism_ontology_classes.py
```

执行命令：

```bash
python -m py_compile scripts/run_pilot20_owner_rework_responses.py scripts/summarize_pilot20_owner_responses.py scripts/check_pilot20_mechanism_ontology_classes.py
python scripts/run_pilot20_owner_rework_responses.py --parallel 3 --timeout-seconds 3600 --force
python scripts/summarize_pilot20_owner_responses.py
python scripts/check_pilot20_mechanism_ontology_classes.py
```

生成文件：

```text
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/owner_runner/owner_runner_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/owner_response_summary/owner_response_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/owner_response_summary/owner_response_report_latest.md
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/ontology_qc/mechanism_ontology_class_qc_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/ontology_qc/mechanism_ontology_class_qc_report_latest.md
```

Owner-worker response 结果：

| action | count |
| --- | ---: |
| `repair_ready` | 8 |
| `needs_upstream_material` | 1 |
| `blocked_missing_material` | 2 |

Owner 分布：

| owner | count |
| --- | ---: |
| `worker-5_mechanism_ontology_extractor` | 9 |
| `worker-2_main_text_assay_extractor` | 2 |

关键解释：

- 8 个 `repair_ready` 表示 owner worker 已经找到安全修复路径，部分已在 packet analysis 层写入修复；但 worker-6 仍需镜像/刷新 final artifacts 并重新裁定。
- 3 个非 repair-ready：
  - `dispatch-009 / doi__10.1038_s41522-024-00637-y`：机制/补充材料相关，`blocked_missing_material`。
  - `dispatch-010 / doi__10.1038_s41598-017-16784-6`：缺真实 supplement PDF / checkerboard MIC/FICI 表，`needs_upstream_material`。
  - `dispatch-011 / doi__10.21203_rs.3.rs-578319_v1`：Research Square supplement / article XML 不可恢复，`blocked_missing_material`。
- 这 3 个不能通过 worker-6 硬改为 accepted，必须保留 blocked/material-gap 状态，或者先补源材料。

机制 ontology QC：

| metric | value |
| --- | ---: |
| papers checked | 11 |
| mechanism files checked | 44 |
| files with non-standard evidence_class | 32 |

主要非标准 class 包括：

```text
mechanism_context_pending_review
mechanism_scope_guard
mechanistic_context
phenotypic_antibiofilm_activity
phenotypic_resistance_development_assay
computational_model
phenotypic_resistance_assay
contextual_mechanism_assay
background_mechanism_context
indirect_mechanism_context
phenotypic_synergy_context
structural_supporting_mechanism
supportive_activity_mechanism
immunomodulatory_cell_phenotype
mechanism_hypothesis_context
phenotype_activity_context
toxicity_selectivity_context
```

当前判断：

- owner response 已完成，但 final-level 机制 ontology 仍未闭环。
- 420 条正式 validation 仍不能启动。
- 下一步应运行 worker-6 final mirror/re-adjudication：
  - 对 8 个 `repair_ready`，将 owner-approved analysis repair 镜像到 packet final 和 `papers/<paper_id>/final/`，更新 `review_report.json`，再做 ontology QC。
  - 对 3 个 material-blocked，写入 final/review_report 的 `blocked_missing_primary_material` 或 `needs_targeted_rework`，保留具体缺失材料，不再无限重试。
  - worker-6 后必须重新运行 `scripts/check_pilot20_mechanism_ontology_classes.py`，目标是 repair-ready 8 篇的 final bad class 降为 0；blocked 3 篇保留 material-gap 而非 publication-grade。

### Step 6 Worker-6 Final Mirror / Full Pilot20 Closure 执行记录

执行时间：`2026-06-22T16:05-17:05 CST`

本轮目标：

- 对 owner response 的 11 个 dispatch 做真正 worker-6 final mirror / re-adjudication。
- 重新运行机制 ontology QC，确认 accepted 集合中没有非标准 `evidence_class`。
- 发现并修复一个更深的流程缺口：此前 QC 只覆盖 dispatch papers，漏掉 9 篇 non-dispatch pilot papers，其中 4 篇 readjudication 为 `needs_targeted_rework` 但没有结构化 ticket，另有 5 篇未进入 owner dispatch 的 `accepted_with_cautions_confirmed` 仍需要 final-level 复审。

执行命令：

```bash
python -m py_compile scripts/run_pilot20_worker6_final_mirror.py
python scripts/run_pilot20_worker6_final_mirror.py --parallel 3 --timeout-seconds 3600

python -m py_compile scripts/check_pilot20_mechanism_ontology_classes.py
python scripts/check_pilot20_mechanism_ontology_classes.py

python -m py_compile scripts/summarize_pilot20_worker6_final_mirror.py
python scripts/summarize_pilot20_worker6_final_mirror.py

python -m py_compile scripts/run_pilot20_worker6_non_dispatch_final_review.py
python scripts/run_pilot20_worker6_non_dispatch_final_review.py --parallel 3 --timeout-seconds 3600

python scripts/check_pilot20_mechanism_ontology_classes.py

python -m py_compile scripts/summarize_pilot20_final_review_closure.py
python scripts/summarize_pilot20_final_review_closure.py
```

新增/修复脚本：

- `scripts/check_pilot20_mechanism_ontology_classes.py`
  - 从 dispatch-only QC 修复为默认覆盖 `packet_index_latest.csv` 的 20 篇 pilot paper。
  - final decision 采用优先级：`worker6_readjudication` 初始值 -> `worker6_non_dispatch_final_review` -> `worker6_final_mirror`。
  - 输出 `accepted_files_with_bad_classes` 与 `nonterminal_files_with_bad_classes`，防止把 blocked/rework 的坏类误解为 accepted 质量问题。
- `scripts/summarize_pilot20_worker6_final_mirror.py`
  - 汇总 11 个 dispatch 的 worker-6 final mirror，检查 response、review_report、ontology QC 一致性。
- `scripts/run_pilot20_worker6_non_dispatch_final_review.py`
  - 对没有进入 owner dispatch 的 9 篇 pilot paper 重新启动 worker-6 final review。
  - 用 runner command/header 作为 `gpt-5.5` / `xhigh` provenance，除非产物相互矛盾。
  - 对安全可修复的机制 ontology label 做 final-level 修复；不能修复时必须保留 nonterminal 状态。
- `scripts/summarize_pilot20_final_review_closure.py`
  - 汇总完整 20 篇 pilot 的最终状态，作为后续扩展前的 closure 入口。

关键输出：

```text
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_final_mirror/runner/worker6_final_runner_status_latest.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_final_mirror/runner/worker6_final_runner_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_non_dispatch_final_review/runner/worker6_non_dispatch_status_latest.csv
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/worker6_non_dispatch_final_review/runner/worker6_non_dispatch_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/ontology_qc/mechanism_ontology_class_qc_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/ontology_qc/mechanism_ontology_class_qc_report_latest.md
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/pilot20_final_review_closure/pilot20_final_review_closure_summary_latest.json
reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/pilot20_final_review_closure/pilot20_final_review_closure_report_latest.md
```

worker-6 final mirror 11 个 dispatch 结果：

```text
selected_count=11
valid_worker6_response=11
accepted_with_cautions=7
blocked_missing_primary_material=3
needs_targeted_rework=1
```

non-dispatch worker-6 final review 9 篇结果：

```text
selected_count=9
valid_worker6_response=9
accepted_with_cautions=9
```

完整 pilot20 closure 结果：

```text
paper_count=20
accepted_with_cautions=16
blocked_missing_primary_material=3
needs_targeted_rework=1
publication_grade_true_count=16
review_report_validation_problem_count=0
accepted_files_with_bad_classes=0
nonterminal_files_with_bad_classes=13
```

仍保留的非终端论文：

| paper | final decision | 原因 |
| --- | --- | --- |
| `doi__10.1038_s41522-024-00637-y` | `blocked_missing_primary_material` | true supplementary table/figures、OA package、DJK-5 exact sequence/modification evidence 本地不可恢复。 |
| `doi__10.1038_s41598-017-16784-6` | `blocked_missing_primary_material` | 缺失 `41598_2017_16784_MOESM1_ESM.pdf`，checkerboard MIC/FICI supplement-dependent row 不能 source-verify。 |
| `doi__10.21203_rs.3.rs-578319_v1` | `blocked_missing_primary_material` | Research Square 本地 XML 不是可用 article XML，named supplementary PDFs 不在本地，Supplementary Table 5 exact values 不可恢复。 |
| `doi__10.2174_1381612822666161027120518` | `needs_targeted_rework` | owner response 未实际编辑机制 artifact；final/packet mechanism evidence 仍有非标准 evidence_class，需要 worker-5 重新修复或 worker-6 再判定为不可修复。 |

本轮修复后的判断：

- pilot20 accepted subset 已达到当前机制 ontology QC 要求：accepted 文件中非标准 `evidence_class` 为 0。
- pilot20 不能说 20/20 clean；应表述为 `16 accepted_with_cautions + 3 blocked_missing_primary_material + 1 needs_targeted_rework`。
- 420 条正式 validation 可以使用这套修复后的 full-scope QC / non-dispatch review 机制继续扩展，但必须保留同样的 nonterminal 状态分层，不能把 blocked 或 rework 论文计入 accepted。

## 13. 下一步入口

旧入口 `accepted_sample_audit.py` 只适合结构化抽样，不适合在当前状态下直接扩展。当前 pilot20 的完整 closure 入口应从以下文件开始：

```bash
python -m json.tool reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/pilot20_final_review_closure/pilot20_final_review_closure_summary_latest.json
python -m json.tool reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/owner_rework_dispatch/ontology_qc/mechanism_ontology_class_qc_summary_latest.json
```

扩展到 420 条 manual validation 前，必须沿用以下入口和检查：

- worker-6 对 dispatch papers 的 final mirror；
- worker-6 对 non-dispatch papers 的 final review；
- full pilot paper source 的 ontology QC，而不是 dispatch-only QC；
- closure summary 中 `review_report_validation_problem_count=0`；
- accepted subset 的 `accepted_files_with_bad_classes=0`；
- blocked/rework 论文保留 nonterminal 状态；
- 仍然不能把抽样通过外推为全量 clean。
