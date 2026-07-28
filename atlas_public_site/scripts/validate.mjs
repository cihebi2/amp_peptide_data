import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const workerText = await readFile(resolve(root, "dist", "server", "index.js"), "utf8");
const workerUrl = `data:text/javascript;base64,${Buffer.from(workerText).toString("base64")}`;
const worker = (await import(workerUrl)).default;

async function request(path, options = {}) {
  return worker.fetch(new Request(`https://atlas.example${path}`, options), {});
}

function rpc(method, params = {}, id = 1) {
  return JSON.stringify({ jsonrpc: "2.0", id, method, params });
}

const legacyHeaders = {
  "content-type": "application/json",
  accept: "application/json, text/event-stream",
  "mcp-protocol-version": "2025-11-25",
};
const modernHeaders = (method, name) => ({
  "content-type": "application/json",
  accept: "application/json, text/event-stream",
  "mcp-protocol-version": "2026-07-28",
  "mcp-method": method,
  ...(name ? { "mcp-name": name } : {}),
});

const health = await request("/healthz");
assert.equal(health.status, 200);
const healthJson = await health.json();
assert.equal(healthJson.status, "ok");
assert.deepEqual(healthJson.mcp_protocols, ["2026-07-28", "2025-11-25"]);

const home = await request("/");
const html = await home.text();
assert.equal(home.status, 200);
for (const phrase of [
  "Rights-filtered public beta",
  "1,374",
  "Six layers",
  "Browse peptides and papers",
  "Database audit",
  "Grounding benchmark",
  "Streamable HTTP MCP",
  "Rights &amp; release governance",
]) {
  assert.match(html, new RegExp(phrase));
}
assert.doesNotMatch(html, /database_value|primary_source_value|source_final_path/);

const developers = await request("/developers");
assert.equal(developers.status, 200);
assert.match(await developers.text(), /Live MCP tool call/);

const canonicalStats = await request("/api/v1/system/stats");
const canonicalStatsJson = await canonicalStats.json();
assert.equal(canonicalStatsJson.data.papers, 1374);
assert.equal(canonicalStatsJson.data.peptides, 9263);
assert.equal(canonicalStatsJson.meta.rights_filtered, true);
assert.equal(canonicalStatsJson.links.self, "/api/v1/system/stats");

const legacyStats = await request("/api/v1/stats");
assert.equal((await legacyStats.json()).papers, 1374);

const peptides = await request(
  "/api/v1/catalog/peptides?endpoint=MIC&sort=activity_count&limit=5",
);
const peptidesJson = await peptides.json();
assert.equal(peptides.status, 200);
assert.equal(peptidesJson.data.items.length, 5);
assert.ok(
  peptidesJson.data.items.every((item) =>
    item.endpoints.some(([endpoint]) => endpoint.toLowerCase() === "mic"),
  ),
);
assert.ok(
  peptidesJson.data.items.every(
    (item, index, items) =>
      index === 0 || items[index - 1].activity_count >= item.activity_count,
  ),
);
assert.equal(peptidesJson.meta.pagination.limit, 5);

const search = await request("/api/v1/catalog/search?q=LL-37&limit=3");
const searchJson = await search.json();
assert.ok(searchJson.data.peptides.length > 0);
assert.ok(JSON.stringify(searchJson).length < 500_000);

const paperList = await request(
  "/api/v1/catalog/papers?sort=audit_count&min_activity_count=1&limit=3",
);
const paperListJson = await paperList.json();
assert.equal(paperListJson.data.items.length, 3);
assert.ok(paperListJson.data.items.every((item) => item.activity_count >= 1));

const schema = await request("/api/v1/schema/database");
const schemaJson = await schema.json();
assert.deepEqual(
  schemaJson.data.layers.map((layer) => layer.name),
  ["system", "governance", "catalog", "evidence", "evaluation", "api"],
);
assert.equal(schemaJson.data.public_safe, true);

const audit = await request("/api/v1/evidence/audit-summary?database=DBAASP");
const auditJson = await audit.json();
assert.deepEqual(Object.keys(auditJson.data.by_database_status), ["DBAASP"]);
assert.match(auditJson.data.interpretation, /not by itself/);

const benchmark = await request(
  "/api/v1/evaluation/benchmark?category=activity_value&limit=5",
);
const benchmarkJson = await benchmark.json();
assert.equal(benchmarkJson.data.items.length, 5);
assert.equal(benchmarkJson.data.total, 12);
assert.equal(
  benchmarkJson.meta.validation_status,
  "stratified_human_validation_incomplete",
);

const rights = await request("/api/v1/governance/rights");
const rightsJson = await rights.json();
assert.equal(rightsJson.data.source_database_raw_fields_exposed, false);
assert.equal(rightsJson.data.full_internal_v1_payload_publicly_redistributed, false);

const openapi = await request("/api/v1/schema/openapi.json");
const openapiJson = await openapi.json();
assert.equal(openapiJson.openapi, "3.1.0");
assert.ok(Object.keys(openapiJson.paths).length >= 14);

const etag = canonicalStats.headers.get("etag");
const notModified = await request("/api/v1/system/stats", {
  headers: { "if-none-match": etag },
});
assert.equal(notModified.status, 304);

const preflight = await request("/api/mcp", {
  method: "OPTIONS",
  headers: { origin: "https://atlas.example" },
});
assert.equal(preflight.status, 204);
assert.match(preflight.headers.get("access-control-allow-methods"), /POST/);

const descriptor = await request("/api/mcp");
const descriptorJson = await descriptor.json();
assert.equal(descriptorJson.transport.url, "https://atlas.example/api/mcp");
assert.equal(descriptorJson.capabilities.tools.count, 10);
assert.equal(descriptorJson.authentication.required, false);

const initialize = await request("/api/mcp", {
  method: "POST",
  headers: legacyHeaders,
  body: rpc("initialize", {
    protocolVersion: "2025-11-25",
    capabilities: {},
    clientInfo: { name: "validator", version: "1" },
  }),
});
const initializeJson = await initialize.json();
assert.equal(initialize.status, 200);
assert.equal(initializeJson.result.protocolVersion, "2025-11-25");
assert.equal(initializeJson.result.serverInfo.name, "amp-evidence-atlas");

const notification = await request("/api/mcp", {
  method: "POST",
  headers: legacyHeaders,
  body: JSON.stringify({
    jsonrpc: "2.0",
    method: "notifications/initialized",
    params: {},
  }),
});
assert.equal(notification.status, 202);
assert.equal(await notification.text(), "");

const legacyTools = await request("/api/mcp", {
  method: "POST",
  headers: legacyHeaders,
  body: rpc("tools/list"),
});
const legacyToolsJson = await legacyTools.json();
assert.equal(legacyToolsJson.result.tools.length, 10);
assert.ok(
  legacyToolsJson.result.tools.every(
    (tool) =>
      tool.annotations.readOnlyHint === true &&
      tool.inputSchema.additionalProperties === false,
  ),
);

const legacyCall = await request("/api/mcp", {
  method: "POST",
  headers: legacyHeaders,
  body: rpc("tools/call", {
    name: "atlas.search",
    arguments: { query: "LL-37", limit: 2 },
  }),
});
const legacyCallJson = await legacyCall.json();
assert.equal(legacyCallJson.result.isError, false);
assert.ok(legacyCallJson.result.structuredContent.peptides.length > 0);

const badToolArguments = await request("/api/mcp", {
  method: "POST",
  headers: legacyHeaders,
  body: rpc("tools/call", {
    name: "atlas.search",
    arguments: { query: "LL-37", limit: 200 },
  }),
});
assert.equal((await badToolArguments.json()).result.isError, true);

const discover = await request("/api/mcp", {
  method: "POST",
  headers: modernHeaders("server/discover"),
  body: rpc("server/discover", {
    _meta: { "io.modelcontextprotocol/protocolVersion": "2026-07-28" },
  }),
});
const discoverJson = await discover.json();
assert.equal(discover.status, 200);
assert.ok(discoverJson.result.supportedVersions.includes("2026-07-28"));
assert.equal(discoverJson.result.resultType, "complete");
assert.equal(
  discoverJson.result._meta["io.modelcontextprotocol/serverInfo"].name,
  "amp-evidence-atlas",
);

const modernTools = await request("/api/mcp", {
  method: "POST",
  headers: modernHeaders("tools/list"),
  body: rpc("tools/list", {
    _meta: { "io.modelcontextprotocol/protocolVersion": "2026-07-28" },
  }),
});
const modernToolsJson = await modernTools.json();
assert.equal(modernToolsJson.result.cacheScope, "public");
assert.equal(modernToolsJson.result.ttlMs, 300000);

const modernCall = await request("/api/mcp", {
  method: "POST",
  headers: modernHeaders("tools/call", "atlas.describe"),
  body: rpc("tools/call", {
    name: "atlas.describe",
    arguments: {},
    _meta: { "io.modelcontextprotocol/protocolVersion": "2026-07-28" },
  }),
});
const modernCallJson = await modernCall.json();
assert.equal(modernCallJson.result.isError, false);
assert.equal(modernCallJson.result.structuredContent.stats.papers, 1374);
assert.equal(modernCallJson.result.resultType, "complete");

const headerMismatch = await request("/api/mcp", {
  method: "POST",
  headers: modernHeaders("tools/list"),
  body: rpc("tools/call", {
    name: "atlas.describe",
    arguments: {},
    _meta: { "io.modelcontextprotocol/protocolVersion": "2026-07-28" },
  }),
});
assert.equal(headerMismatch.status, 400);
assert.equal((await headerMismatch.json()).error.code, -32020);

const invalidOrigin = await request("/api/mcp", {
  method: "POST",
  headers: { ...legacyHeaders, origin: "https://evil.example" },
  body: rpc("tools/list"),
});
assert.equal(invalidOrigin.status, 403);

const sseGet = await request("/api/mcp", {
  headers: { accept: "text/event-stream" },
});
assert.equal(sseGet.status, 405);

const missing = await request("/not-found");
assert.equal(missing.status, 404);
const missingJson = await missing.json();
assert.equal(missingJson.error.code, "not_found");

console.log(
  "Validated complete portal, canonical and legacy APIs, filters, normalized schema, ETag/CORS, legacy MCP lifecycle, modern MCP discovery/tools, security checks, and error routes.",
);
