# AMP Evidence Atlas public deployment — 2026-07-28 18:15 CST

Production URL:

<https://amp-evidence-atlas.daoyu7974.chatgpt.site>

Status:

- Sites version: 1
- deployment: succeeded
- access: public
- field filter: 6/6 checks passed
- public-network smoke test: 7/7 checks passed
- visual screenshot: inspected at 1200×750 with no observed layout blocker

The deployment is the deliberately limited
`amp-evidence-atlas-v1.0-public-safe-beta` projection. It does not publish the
unrestricted internal v1.0 TSV payload.

API examples:

```text
GET /healthz
GET /api/v1/stats
GET /api/v1/search?q=LL-37
GET /api/v1/rights
GET /api/v1/openapi.json
```
