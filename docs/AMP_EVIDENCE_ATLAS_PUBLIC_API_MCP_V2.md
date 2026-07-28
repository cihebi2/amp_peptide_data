# AMP Evidence Atlas 公共 API、MCP 与数据库分层 v2

更新时间：2026-07-28（Asia/Shanghai）

## 1. 目标

公共服务只提供“项目自产的索引、统计和评测内容”，不把受限制的源数据库
字段、论文全文或逐行数据库审计结果重新发布。网站、REST API 和 MCP 使用同一
份 `amp-evidence-atlas-v1.0-public-safe-beta` 投影，因此三种入口的口径一致。

## 2. 数据库层级

公开安全 SQLite：  
`public_exports/amp_evidence_atlas_v1_0_public_safe/atlas_public_safe.db`

| 层 | 用途 | 主要实体 |
|---|---|---|
| system | 版本、校验和、范围与限制 | `system_release` |
| governance | 各数据库授权判断和公开决策 | `governance_source_rights` |
| catalog | 论文、肽、序列、终点和论文—肽关系 | `catalog_*` |
| evidence | 数据库审查状态和差异类别汇总 | `evidence_*` |
| evaluation | 40 题项目自建 benchmark | `evaluation_benchmark_item` |
| api | 面向 API/AI 的稳定读取视图 | `api_*` |

数据库启用了主键、外键、计数约束和检索索引。公开库中没有源数据库原始记录表，
也没有逐行 database-versus-paper 对照表。

## 3. REST API

生产域名：  
`https://amp-evidence-atlas.daoyu7974.chatgpt.site`

推荐使用新的分层路由：

```text
/api/v1/system/*
/api/v1/catalog/*
/api/v1/evidence/*
/api/v1/evaluation/*
/api/v1/governance/*
/api/v1/schema/*
```

成功响应统一为：

```json
{
  "data": {},
  "meta": {
    "release_id": "amp-evidence-atlas-v1.0-public-safe-beta",
    "rights_filtered": true
  },
  "links": {
    "self": "/api/v1/..."
  }
}
```

错误响应统一为：

```json
{
  "error": {
    "code": "peptide_not_found",
    "message": "..."
  },
  "meta": {
    "release_id": "amp-evidence-atlas-v1.0-public-safe-beta",
    "rights_filtered": true
  }
}
```

旧的扁平路由仍保留为兼容别名。所有 GET 响应支持 CORS、ETag 和 5 分钟公共缓存。

## 4. MCP

远程 MCP 地址：

```text
https://amp-evidence-atlas.daoyu7974.chatgpt.site/api/mcp
```

实现为无状态、只读的 Streamable HTTP 服务：

- Sites 边缘层保留 `/mcp`，所以公开端点使用不冲突的 `/api/mcp`；
- 对 `/api/mcp` 发普通 GET 可读取服务描述；不依赖同样被边缘限制的
  `/.well-known/*` 路径；
- 兼容 `2025-11-25` 初始化流程；
- 支持 `2026-07-28` 的 `server/discover`、`Mcp-Method`、`Mcp-Name`、
  结果类型、缓存提示和响应级服务器元数据；
- 校验 `Origin`、协议版本、JSON-RPC、Content-Type、参数 Schema 和请求大小；
- 不创建 session，不提供写入工具；
- 每个列表工具最多返回 20 项，避免 AI 一次拉取过大结果。

公开工具：

1. `atlas.describe`
2. `atlas.search`
3. `atlas.list_peptides`
4. `atlas.get_peptide`
5. `atlas.list_papers`
6. `atlas.get_paper`
7. `atlas.get_audit_summary`
8. `atlas.get_benchmark`
9. `atlas.get_rights_policy`
10. `atlas.get_database_schema`

## 5. 科学解释边界

- `source_conflict` 是审查状态，不自动等于“数据库被人工确认错误”。
- 多 Agent 一致不等于人工金标准。
- 分层人工验证尚未闭环。
- 完整内部 v1.0 包仍然 `public_release_ready=false`。
- APD6、CAMP、DBAASP、dbAMP 和 DRAMP 专利肽的授权跟进仍未关闭。
