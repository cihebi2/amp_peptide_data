# AMP Peptide Data

抗菌肽文献证据数据、审查记录、自动化审查流程与本地检索网站代码的可复现快照。

## 当前版本与公开边界

- 内部数据权威版本已冻结为 `amp-evidence-atlas-v1.0`；由于来源授权仍未全部
  关闭，完整 v1.0 不作为五库原始字段公共下载包发布。
- `public_exports/amp_evidence_atlas_v1_0_public_safe/`：v1.0 的字段级
  rights-filtered 公共投影，包含项目自产索引、统计、benchmark 和规范化 SQLite。
- `releases/amp_evidence_atlas_v1_rc2/`：历史 RC2 快照，用于追溯，不再代表
  当前公开服务口径。
- `papers/`：逐论文的最终结构化审查结果，包括活性/毒性、数据库记录核验、机制证据和审查报告。
- `reports/nar_resource_freeze_v1/`：NAR 资源冻结、统一口径、validation420 与人工核验状态。
- `reports/`：数据库—文献冲突、质量检查、后续队列和数据审计结果。

RC1/RC2 仅用于历史追溯；生产网站默认读取公共安全 v1.0 投影。

## 审查流程

- `.codex/skills/`：六角色论文审查规范和批次编排技能。
- `pipeline_v2/deepmine/dbaasp_strict_pilot.py`：严格单篇控制器。
- `pipeline_v2/deepmine/run_remaining_200_strict_campaign.py`：单篇六 worker、leader 和 verifier 闭环。
- `pipeline_v2/deepmine/supervise_remaining_200_parallel_campaign.py`：不同论文并行、单篇内部顺序执行的调度器。
- `pipeline_v2/deepmine/grok_readonly_review.py`：仅在分类后的 Codex 生物内容安全误拦截中使用的只读 leader/verifier fallback；不能替代六个 canonical worker。
- `pipeline_v2/deepmine/test_*.py`：流程、冻结、调度、gate 和恢复路径的回归测试。
- `scripts/`：RC2/NAR 构建、核验、发布与专题数据评估脚本。

严格终态要求六个独立顺序 `codex exec gpt-5.5/xhigh` worker、最新 worker-6、机械 gate、零开放 ticket、独立 leader `PASS` 和独立 verifier `PASS`。fallback 数据不会自动进入权威 DBAASP ingest 或公开发布层。

## 网站与接口

- 生产门户：https://amp-evidence-atlas.daoyu7974.chatgpt.site
- 分层 REST API：https://amp-evidence-atlas.daoyu7974.chatgpt.site/api/v1/schema/openapi.json
- AI MCP：https://amp-evidence-atlas.daoyu7974.chatgpt.site/api/mcp
- `atlas_public_site/`：生产门户、API 与 Streamable HTTP MCP 源码和测试。
- `portal/portal_server.py`：本地数据网站。
- `portal/mcp_server.py`：MCP 查询接口。
- `portal/build_db.py`：从结构化数据重建 `portal/atlas.db`。
- `portal/benchmark_protocol.md`：基准与数据使用边界。

本地完整 `portal/atlas.db` 不直接提交。公共安全
`public_exports/.../atlas_public_safe.db` 是经过字段过滤和独立校验的例外。

## 大文件

GitHub 普通 Git 对单个对象强制执行 100 MiB 上限，并对单次 push 执行 2 GB 上限。因此，超过安全阈值的结构化表被无损转换为可复现的 `*.gz`：

```bash
gzip -dk releases/amp_evidence_atlas_v1_rc2/activity_observations.tsv.gz
gzip -dk releases/amp_evidence_atlas_v1_rc2/database_record_audits.tsv.gz
```

原始路径、字节数和 SHA-256 位于：

- `repository_metadata/compressed_large_files.json`

GitHub 官方限制说明：

- https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits
- https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github

## 未直接托管的本地材料

仓库保留全部发布数据、逐论文最终结果、审查状态、ticket、locator、数据库链接记录、流程代码和回归测试。以下材料不直接嵌入公共 Git 历史：

- 原始论文 PDF、补充材料二进制和视频；
- OA package/cache 及重复 source/raw 镜像；
- 可重建的 `portal/atlas.db`；
- stdout/stderr、OMX 状态和本机运行缓存；
- 与 `papers/` canonical final 重复的中间 `paper_packets/*/analysis`、`paper_packets/*/final`；
- 完整论文/补充材料的派生全文表面。

这些材料的本地路径、规模和排除原因记录在：

- `repository_metadata/local_only_artifact_inventory.tsv.gz`
- `repository_metadata/local_only_artifact_inventory_summary.json`
- `repository_metadata/pruned_duplicate_and_source_surfaces.json`

此边界既满足 GitHub 强制限制，也避免把没有统一再分发许可的论文原文作为数据集公开发布。packet manifest、hash、locator 和最终证据记录仍可用于来源追踪。

## 项目进展

- `PROJECT_PROGRESS.md`：带时间戳的持续维护进度文档。
- `docs/`：数据字典、执行计划、专题审计与项目路线图。

发布或论文引用前，请以最新冻结 manifest 和独立 verifier 结果为准，不要把 `candidate`、`accepted_with_cautions` 或机器 fallback 等同于权威数据库入库。
