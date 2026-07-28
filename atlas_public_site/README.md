# AMP Evidence Atlas public-safe portal

Production portal, REST API and Streamable HTTP MCP server for
`amp-evidence-atlas-v1.0-public-safe-beta`.

This deployment is deliberately rights-filtered. It exposes project-created
aggregates, paper/peptide discovery indexes, the 40-item evidence benchmark and
governance metadata. It does **not** expose copied source-database fields,
primary full text, DRAMP patent content, or row-level database comparisons.

## Interfaces

### Portal

- `/` — complete resource overview
- `/explore` — peptide and paper catalog
- `/audit` — aggregate database-audit outcomes
- `/benchmark` — grounding benchmark preview
- `/developers` — API/MCP docs and live consoles
- `/governance` — rights and release policy

### Canonical REST API

Canonical endpoints use a stable `data / meta / links` response envelope:

- `/api/v1/system/release`
- `/api/v1/system/stats`
- `/api/v1/catalog/search?q=LL-37`
- `/api/v1/catalog/peptides?endpoint=MIC&sort=activity_count`
- `/api/v1/catalog/peptides/{encoded-name}`
- `/api/v1/catalog/papers?sort=audit_count`
- `/api/v1/catalog/papers/{encoded-paper-id}`
- `/api/v1/evidence/audit-summary?database=DBAASP`
- `/api/v1/evaluation/benchmark?category=activity_value`
- `/api/v1/governance/rights`
- `/api/v1/schema/database`
- `/api/v1/schema/openapi.json`

The original flat `/api/v1/stats`, `/api/v1/peptides`, and related routes remain
backward-compatible aliases.

### MCP for AI clients

Server URL:

```text
https://amp-evidence-atlas.daoyu7974.chatgpt.site/api/mcp
```

Generic remote-server configuration:

```json
{
  "mcpServers": {
    "amp-evidence-atlas": {
      "url": "https://amp-evidence-atlas.daoyu7974.chatgpt.site/api/mcp"
    }
  }
}
```

The endpoint is stateless and read-only. It supports:

- MCP `2026-07-28`: `server/discover`, standard modern headers, cache hints
  and per-response server metadata.
- MCP `2025-11-25`: `initialize`, `notifications/initialized`, `tools/list`
  and `tools/call`.

Ten bounded tools expose catalog search, peptide/paper browsing, audit
aggregates, benchmark items, rights policy and database schema. Inputs are
validated against closed JSON Schemas and all tools declare read-only,
non-destructive annotations.

Modern tool-list example:

```bash
curl -X POST https://amp-evidence-atlas.daoyu7974.chatgpt.site/api/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' \
  -H 'Mcp-Method: tools/list' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Normalized public database

The release builder also creates `atlas_public_safe.db`, a normalized SQLite
read model with six logical layers:

1. `system` — release identity and payload checksum
2. `governance` — source-rights decisions
3. `catalog` — paper, peptide, sequence, endpoint and relationship indexes
4. `evidence` — audit-status and difference-category aggregates
5. `evaluation` — benchmark items
6. `api` — stable public read views

The Worker uses the compact JSON projection at runtime; the SQLite file is a
downloadable/reproducible release artifact and is validated independently.

## Build and validate

```bash
npm test
tar -C . -czf amp-evidence-atlas-site.tar.gz dist
```

`npm test` covers the complete HTML portal, canonical and legacy APIs,
filtering, pagination, ETag/CORS, database-schema exposure, legacy MCP
lifecycle, modern MCP discovery/tools, origin checks, header mismatches and
error routes.
