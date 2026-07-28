const DATA = /*__ATLAS_DATA__*/null;

const RELEASE_ID = DATA.release.release_id;
const RELEASE_HASH = DATA.release.source_payload_checksum_manifest_sha256;
const ETAG = `W/"${RELEASE_HASH.slice(0, 24)}-portal-v2"`;
const MAX_LIMIT = 100;
const MCP_TOOL_LIMIT = 20;
const MCP_PROTOCOL_MODERN = "2026-07-28";
const MCP_PROTOCOL_LEGACY = "2025-11-25";
const MCP_PUBLIC_PATH = "/api/mcp";
const MCP_PROTOCOLS = [
  MCP_PROTOCOL_MODERN,
  MCP_PROTOCOL_LEGACY,
  "2025-06-18",
  "2025-03-26",
];
const SERVER_INFO = {
  name: "amp-evidence-atlas",
  title: "AMP Evidence Atlas",
  version: "1.0.0-public-safe-beta.2",
  websiteUrl: "https://amp-evidence-atlas.daoyu7974.chatgpt.site",
};
const MCP_INSTRUCTIONS =
  "Read-only access to the rights-filtered AMP Evidence Atlas. Treat audit conflicts as curation statuses, not automatically confirmed database errors. Human validation remains incomplete.";

function baseHeaders(cache = true) {
  return {
    "access-control-allow-origin": "*",
    "cache-control": cache ? "public, max-age=300" : "no-store",
    etag: ETAG,
    "referrer-policy": "strict-origin-when-cross-origin",
    "x-content-type-options": "nosniff",
  };
}

function json(value, status = 200, extraHeaders = {}, cache = status === 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: {
      ...baseHeaders(cache),
      "content-type": "application/json; charset=utf-8",
      ...extraHeaders,
    },
  });
}

function text(value, contentType = "text/plain; charset=utf-8", status = 200) {
  return new Response(value, {
    status,
    headers: {
      ...baseHeaders(status === 200),
      "content-type": contentType,
      "content-security-policy":
        "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; object-src 'none'",
      "x-frame-options": "DENY",
    },
  });
}

function apiSuccess(data, url, meta = {}, status = 200) {
  return json(
    {
      data,
      meta: {
        release_id: RELEASE_ID,
        rights_filtered: true,
        ...meta,
      },
      links: { self: `${url.pathname}${url.search}` },
    },
    status,
  );
}

function apiError(url, status, code, message, details) {
  return json(
    {
      error: {
        code,
        message,
        ...(details === undefined ? {} : { details }),
      },
      meta: { release_id: RELEASE_ID, rights_filtered: true },
      links: { self: `${url.pathname}${url.search}` },
    },
    status,
    {},
    false,
  );
}

function number(value, fallback = 0) {
  const parsed = Number.parseInt(value ?? "", 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function normalized(value) {
  return String(value ?? "").trim().toLocaleLowerCase();
}

function pageFrom(url, maximum = MAX_LIMIT, defaultLimit = 25) {
  return {
    offset: Math.max(0, number(url.searchParams.get("offset"), 0)),
    limit: Math.min(
      maximum,
      Math.max(1, number(url.searchParams.get("limit"), defaultLimit)),
    ),
  };
}

function paginate(items, offset, limit) {
  return {
    total: items.length,
    offset,
    limit,
    has_more: offset + limit < items.length,
    items: items.slice(offset, offset + limit),
  };
}

function peptideMatches(item, query) {
  if (!query) return true;
  return (
    normalized(item.name).includes(query) ||
    item.sequences.some((sequence) => normalized(sequence).includes(query)) ||
    item.paper_examples.some((paper) => normalized(paper).includes(query))
  );
}

function paperMatches(item, query) {
  if (!query) return true;
  return normalized(item.id).includes(query) || normalized(item.doi).includes(query);
}

function pairHas(items, wanted) {
  return !wanted || items.some(([name]) => normalized(name) === wanted);
}

function filterPeptides(params = {}) {
  const query = normalized(params.q);
  const endpoint = normalized(params.endpoint);
  const evidenceTier = normalized(params.evidence_tier);
  const minimumActivity = Math.max(0, number(params.min_activity_count, 0));
  const minimumPapers = Math.max(0, number(params.min_paper_count, 0));
  const items = DATA.peptides.filter(
    (item) =>
      peptideMatches(item, query) &&
      pairHas(item.endpoints, endpoint) &&
      pairHas(item.evidence_tiers, evidenceTier) &&
      item.activity_count >= minimumActivity &&
      item.paper_count >= minimumPapers,
  );
  const sort = normalized(params.sort);
  if (sort === "activity_count") {
    items.sort((a, b) => b.activity_count - a.activity_count || a.name.localeCompare(b.name));
  } else if (sort === "paper_count") {
    items.sort((a, b) => b.paper_count - a.paper_count || a.name.localeCompare(b.name));
  }
  return items;
}

function filterPapers(params = {}) {
  const query = normalized(params.q);
  const reviewStatus = normalized(params.review_status);
  const publicationGrade = normalized(params.publication_grade);
  const minimumActivity = Math.max(0, number(params.min_activity_count, 0));
  const items = DATA.papers.filter(
    (item) =>
      paperMatches(item, query) &&
      (!reviewStatus || normalized(item.review_status) === reviewStatus) &&
      (!publicationGrade || normalized(item.publication_grade) === publicationGrade) &&
      item.activity_count >= minimumActivity,
  );
  const sort = normalized(params.sort);
  if (sort === "activity_count") {
    items.sort((a, b) => b.activity_count - a.activity_count || a.id.localeCompare(b.id));
  } else if (sort === "audit_count") {
    items.sort((a, b) => b.audit_count - a.audit_count || a.id.localeCompare(b.id));
  }
  return items;
}

function benchmarkItems(params = {}) {
  const id = normalized(params.id);
  const category = normalized(params.category);
  return DATA.benchmark.filter(
    (item) =>
      (!id || normalized(item.id) === id) &&
      (!category || normalized(item.category) === category),
  );
}

function auditSummary(params = {}) {
  const database = normalized(params.database);
  const status = normalized(params.status);
  const byDatabaseStatus = {};
  for (const [databaseName, statuses] of Object.entries(
    DATA.audit_summary.by_database_status,
  )) {
    if (database && normalized(databaseName) !== database) continue;
    const selected = {};
    for (const [statusName, count] of Object.entries(statuses)) {
      if (!status || normalized(statusName) === status) selected[statusName] = count;
    }
    if (Object.keys(selected).length) byDatabaseStatus[databaseName] = selected;
  }
  return {
    by_database_status: byDatabaseStatus,
    difference_categories: DATA.audit_summary.difference_categories,
    interpretation:
      "Aggregate curation statuses only; source_conflict does not by itself establish a human-confirmed database error.",
  };
}

function combinedSearch(query, limit = 10) {
  const q = normalized(query);
  return {
    query: String(query ?? ""),
    peptides: filterPeptides({ q }).slice(0, limit),
    papers: filterPapers({ q }).slice(0, limit),
  };
}

function openapi(origin) {
  const parameter = (name, description, schema = { type: "string" }) => ({
    name,
    in: "query",
    description,
    schema,
  });
  const paged = [
    parameter("limit", "Page size", {
      type: "integer",
      minimum: 1,
      maximum: MAX_LIMIT,
      default: 25,
    }),
    parameter("offset", "Zero-based offset", {
      type: "integer",
      minimum: 0,
      default: 0,
    }),
  ];
  const get = (summary, parameters = []) => ({
    get: {
      summary,
      parameters,
      responses: {
        200: { description: "Rights-filtered JSON response" },
        400: { description: "Invalid request" },
      },
    },
  });
  return {
    openapi: "3.1.0",
    info: {
      title: "AMP Evidence Atlas public-safe API",
      version: "1.1.0-beta",
      description:
        "Read-only API over project-created indexes and aggregates. Copied source-database fields, primary full text and row-level audit comparisons are excluded.",
    },
    servers: [{ url: origin }],
    tags: [
      { name: "system" },
      { name: "catalog" },
      { name: "evidence" },
      { name: "evaluation" },
      { name: "governance" },
      { name: "schema" },
    ],
    paths: {
      "/healthz": get("Health check"),
      "/api/v1/system/release": get("Release metadata"),
      "/api/v1/system/stats": get("Aggregate statistics"),
      "/api/v1/catalog/search": get("Combined catalog search", [
        parameter("q", "Name, sequence, paper ID or DOI"),
        parameter("limit", "Maximum results per entity", {
          type: "integer",
          minimum: 1,
          maximum: 25,
          default: 10,
        }),
      ]),
      "/api/v1/catalog/peptides": get("Browse derived peptide summaries", [
        parameter("q", "Name, sequence or paper example"),
        parameter("endpoint", "Exact endpoint label"),
        parameter("evidence_tier", "Exact evidence-tier label"),
        parameter("min_activity_count", "Minimum aggregate activity count", {
          type: "integer",
          minimum: 0,
        }),
        parameter("min_paper_count", "Minimum linked-paper count", {
          type: "integer",
          minimum: 0,
        }),
        parameter("sort", "name, activity_count or paper_count"),
        ...paged,
      ]),
      "/api/v1/catalog/peptides/{name}": get("Get an exact peptide summary"),
      "/api/v1/catalog/papers": get("Browse paper summaries", [
        parameter("q", "Paper ID or DOI"),
        parameter("review_status", "Exact review status"),
        parameter("publication_grade", "Exact publication grade"),
        parameter("min_activity_count", "Minimum activity count", {
          type: "integer",
          minimum: 0,
        }),
        parameter("sort", "id, activity_count or audit_count"),
        ...paged,
      ]),
      "/api/v1/catalog/papers/{paper_id}": get("Get an exact paper summary"),
      "/api/v1/evidence/audit-summary": get("Aggregate audit outcomes", [
        parameter("database", "Exact database name"),
        parameter("status", "Exact audit status"),
      ]),
      "/api/v1/evaluation/benchmark": get("Project-authored benchmark items", [
        parameter("id", "Exact benchmark item ID"),
        parameter("category", "Exact benchmark category"),
        ...paged,
      ]),
      "/api/v1/governance/rights": get("Rights and field-filter policy"),
      "/api/v1/schema/database": get("Normalized public database hierarchy"),
      "/api/v1/schema/openapi.json": get("This OpenAPI 3.1 document"),
      "/api/mcp": get("MCP server descriptor; POST handles JSON-RPC"),
    },
  };
}

const MCP_TOOLS = [
  {
    name: "atlas.describe",
    title: "Describe AMP Evidence Atlas",
    description:
      "Return release scope, aggregate statistics and the normalized public database hierarchy.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "atlas.search",
    title: "Search the public-safe catalog",
    description:
      "Search peptide names, displayed sequence variants, paper IDs and DOIs.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", minLength: 1, maxLength: 200 },
        limit: { type: "integer", minimum: 1, maximum: MCP_TOOL_LIMIT, default: 10 },
      },
      required: ["query"],
      additionalProperties: false,
    },
  },
  {
    name: "atlas.list_peptides",
    title: "List peptide summaries",
    description:
      "Browse and filter rights-safe derived peptide summaries with bounded pagination.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", maxLength: 200 },
        endpoint: { type: "string", maxLength: 80 },
        evidence_tier: { type: "string", maxLength: 80 },
        min_activity_count: { type: "integer", minimum: 0 },
        min_paper_count: { type: "integer", minimum: 0 },
        sort: { type: "string", enum: ["name", "activity_count", "paper_count"] },
        limit: { type: "integer", minimum: 1, maximum: MCP_TOOL_LIMIT, default: 10 },
        offset: { type: "integer", minimum: 0, default: 0 },
      },
      additionalProperties: false,
    },
  },
  {
    name: "atlas.get_peptide",
    title: "Get one peptide",
    description: "Return the exact public-safe summary for a peptide name.",
    inputSchema: {
      type: "object",
      properties: { name: { type: "string", minLength: 1, maxLength: 160 } },
      required: ["name"],
      additionalProperties: false,
    },
  },
  {
    name: "atlas.list_papers",
    title: "List paper summaries",
    description:
      "Browse paper identifiers and project-created review/count metadata.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", maxLength: 200 },
        review_status: { type: "string", maxLength: 80 },
        publication_grade: { type: "string", maxLength: 80 },
        min_activity_count: { type: "integer", minimum: 0 },
        sort: { type: "string", enum: ["id", "activity_count", "audit_count"] },
        limit: { type: "integer", minimum: 1, maximum: MCP_TOOL_LIMIT, default: 10 },
        offset: { type: "integer", minimum: 0, default: 0 },
      },
      additionalProperties: false,
    },
  },
  {
    name: "atlas.get_paper",
    title: "Get one paper",
    description: "Return the exact public-safe summary for a paper ID.",
    inputSchema: {
      type: "object",
      properties: { paper_id: { type: "string", minLength: 1, maxLength: 220 } },
      required: ["paper_id"],
      additionalProperties: false,
    },
  },
  {
    name: "atlas.get_audit_summary",
    title: "Get aggregate audit outcomes",
    description:
      "Return database/status and difference-category aggregates, optionally filtered.",
    inputSchema: {
      type: "object",
      properties: {
        database: { type: "string", maxLength: 80 },
        status: { type: "string", maxLength: 80 },
      },
      additionalProperties: false,
    },
  },
  {
    name: "atlas.get_benchmark",
    title: "Get benchmark items",
    description:
      "Return bounded project-authored grounding benchmark items and answer keys.",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", maxLength: 80 },
        category: { type: "string", maxLength: 80 },
        limit: { type: "integer", minimum: 1, maximum: MCP_TOOL_LIMIT, default: 10 },
        offset: { type: "integer", minimum: 0, default: 0 },
      },
      additionalProperties: false,
    },
  },
  {
    name: "atlas.get_rights_policy",
    title: "Get rights policy",
    description:
      "Return source-rights decisions, excluded components and open permission follow-up.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "atlas.get_database_schema",
    title: "Get public database schema",
    description:
      "Return layers, entities, views and relationships of the normalized rights-safe read model.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
].map((tool) => ({
  ...tool,
  annotations: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: false,
  },
}));

function validateToolArguments(tool, args) {
  if (args === undefined) args = {};
  if (!args || typeof args !== "object" || Array.isArray(args)) {
    return "arguments must be a JSON object";
  }
  const schema = tool.inputSchema;
  const allowed = new Set(Object.keys(schema.properties ?? {}));
  const unknown = Object.keys(args).filter((key) => !allowed.has(key));
  if (unknown.length) return `unknown argument(s): ${unknown.join(", ")}`;
  for (const required of schema.required ?? []) {
    if (args[required] === undefined || String(args[required]).trim() === "") {
      return `missing required argument: ${required}`;
    }
  }
  for (const [name, value] of Object.entries(args)) {
    const definition = schema.properties[name];
    if (definition.type === "string") {
      if (typeof value !== "string") return `${name} must be a string`;
      if (definition.minLength && value.trim().length < definition.minLength) {
        return `${name} is too short`;
      }
      if (definition.maxLength && value.length > definition.maxLength) {
        return `${name} exceeds ${definition.maxLength} characters`;
      }
      if (definition.enum && !definition.enum.includes(value)) {
        return `${name} must be one of: ${definition.enum.join(", ")}`;
      }
    }
    if (definition.type === "integer") {
      if (!Number.isInteger(value)) return `${name} must be an integer`;
      if (definition.minimum !== undefined && value < definition.minimum) {
        return `${name} must be at least ${definition.minimum}`;
      }
      if (definition.maximum !== undefined && value > definition.maximum) {
        return `${name} must be at most ${definition.maximum}`;
      }
    }
  }
  return null;
}

function callTool(name, args = {}) {
  const tool = MCP_TOOLS.find((candidate) => candidate.name === name);
  if (!tool) {
    return {
      error: `Unknown tool: ${name}`,
      available_tools: MCP_TOOLS.map((candidate) => candidate.name),
    };
  }
  const invalid = validateToolArguments(tool, args);
  if (invalid) return { error: invalid, tool: name };
  if (name === "atlas.describe") {
    return {
      release: DATA.release,
      stats: DATA.stats,
      database_schema: DATA.database_schema,
    };
  }
  if (name === "atlas.search") {
    return combinedSearch(args.query, args.limit ?? 10);
  }
  if (name === "atlas.list_peptides") {
    const items = filterPeptides({
      q: args.query,
      endpoint: args.endpoint,
      evidence_tier: args.evidence_tier,
      min_activity_count: args.min_activity_count,
      min_paper_count: args.min_paper_count,
      sort: args.sort,
    });
    return paginate(items, args.offset ?? 0, args.limit ?? 10);
  }
  if (name === "atlas.get_peptide") {
    const item = DATA.peptides.find(
      (candidate) => normalized(candidate.name) === normalized(args.name),
    );
    return item ? { item } : { error: `Peptide not found: ${args.name}` };
  }
  if (name === "atlas.list_papers") {
    const items = filterPapers({
      q: args.query,
      review_status: args.review_status,
      publication_grade: args.publication_grade,
      min_activity_count: args.min_activity_count,
      sort: args.sort,
    });
    return paginate(items, args.offset ?? 0, args.limit ?? 10);
  }
  if (name === "atlas.get_paper") {
    const item = DATA.papers.find((candidate) => candidate.id === args.paper_id);
    return item ? { item } : { error: `Paper not found: ${args.paper_id}` };
  }
  if (name === "atlas.get_audit_summary") {
    return auditSummary(args);
  }
  if (name === "atlas.get_benchmark") {
    return paginate(
      benchmarkItems(args),
      args.offset ?? 0,
      args.limit ?? 10,
    );
  }
  if (name === "atlas.get_rights_policy") return DATA.rights;
  if (name === "atlas.get_database_schema") return DATA.database_schema;
  return { error: `Tool has no implementation: ${name}` };
}

function toolResult(name, args) {
  const value = callTool(name, args);
  const isError = Object.prototype.hasOwnProperty.call(value, "error");
  return {
    content: [{ type: "text", text: JSON.stringify(value) }],
    structuredContent: value,
    isError,
  };
}

function modernResult(result) {
  return {
    ...result,
    resultType: "complete",
    _meta: {
      ...(result._meta ?? {}),
      "io.modelcontextprotocol/serverInfo": SERVER_INFO,
      "io.modelcontextprotocol/protocolVersion": MCP_PROTOCOL_MODERN,
    },
  };
}

function rpcResult(id, result, modern = false) {
  return {
    jsonrpc: "2.0",
    id,
    result: modern ? modernResult(result) : result,
  };
}

function rpcError(id, code, message, data) {
  return {
    jsonrpc: "2.0",
    id: id ?? null,
    error: {
      code,
      message,
      ...(data === undefined ? {} : { data }),
    },
  };
}

function allowedOrigin(request, url) {
  const origin = request.headers.get("origin");
  if (!origin) return true;
  if (origin === url.origin) return true;
  if (["https://chatgpt.com", "https://chat.openai.com", "https://claude.ai"].includes(origin)) {
    return true;
  }
  try {
    const parsed = new URL(origin);
    return (
      ["localhost", "127.0.0.1", "::1"].includes(parsed.hostname) &&
      ["http:", "https:"].includes(parsed.protocol)
    );
  } catch {
    return false;
  }
}

function mcpDescriptor(origin) {
  return {
    name: SERVER_INFO.name,
    title: SERVER_INFO.title,
    description:
      "Read-only AI access to the rights-filtered AMP Evidence Atlas catalog, audit aggregates, benchmark and governance metadata.",
    version: SERVER_INFO.version,
    website_url: origin,
    transport: { type: "streamable-http", url: `${origin}${MCP_PUBLIC_PATH}` },
    protocol_versions: [MCP_PROTOCOL_MODERN, MCP_PROTOCOL_LEGACY],
    authentication: { required: false },
    capabilities: { tools: { count: MCP_TOOLS.length, read_only: true } },
    rights_url: `${origin}/api/v1/governance/rights`,
    limitations: DATA.release.limitations,
  };
}

async function handleMcp(request, url) {
  if (request.method === "GET") {
    if ((request.headers.get("accept") ?? "").includes("text/event-stream")) {
      return json(
        rpcError(null, -32000, "SSE listening is not enabled on this stateless server"),
        405,
        { allow: "POST, OPTIONS" },
        false,
      );
    }
    return json(mcpDescriptor(url.origin));
  }
  if (request.method === "DELETE") {
    return json(
      rpcError(null, -32000, "This server does not issue MCP sessions"),
      405,
      { allow: "GET, POST, OPTIONS" },
      false,
    );
  }
  if (request.method !== "POST") {
    return json(
      rpcError(null, -32600, "Method not allowed"),
      405,
      { allow: "GET, POST, OPTIONS" },
      false,
    );
  }
  if (!allowedOrigin(request, url)) {
    return json(rpcError(null, -32001, "Origin is not allowed"), 403, {}, false);
  }
  const contentType = request.headers.get("content-type") ?? "";
  if (!contentType.toLowerCase().includes("application/json")) {
    return json(rpcError(null, -32600, "Content-Type must be application/json"), 415, {}, false);
  }
  const accept = request.headers.get("accept") ?? "";
  if (accept && !accept.includes("application/json")) {
    return json(rpcError(null, -32600, "Accept must include application/json"), 406, {}, false);
  }
  const contentLength = number(request.headers.get("content-length"), 0);
  if (contentLength > 1024 * 1024) {
    return json(rpcError(null, -32600, "Request exceeds 1 MiB"), 413, {}, false);
  }
  let bodyText;
  let message;
  try {
    bodyText = await request.text();
    if (bodyText.length > 1024 * 1024) throw new Error("Request exceeds 1 MiB");
    message = JSON.parse(bodyText);
  } catch (error) {
    return json(rpcError(null, -32700, "Parse error", error.message), 400, {}, false);
  }
  if (
    !message ||
    Array.isArray(message) ||
    typeof message !== "object" ||
    message.jsonrpc !== "2.0"
  ) {
    return json(rpcError(message?.id, -32600, "Invalid JSON-RPC 2.0 request"), 400, {}, false);
  }
  if (typeof message.method !== "string") {
    return new Response(null, { status: 202, headers: baseHeaders(false) });
  }
  const protocolHeader = request.headers.get("mcp-protocol-version");
  if (protocolHeader && !MCP_PROTOCOLS.includes(protocolHeader)) {
    return json(
      rpcError(message.id, -32002, `Unsupported MCP protocol: ${protocolHeader}`, {
        supported: [MCP_PROTOCOL_MODERN, MCP_PROTOCOL_LEGACY],
      }),
      400,
      {},
      false,
    );
  }
  const modern =
    protocolHeader === MCP_PROTOCOL_MODERN || message.method === "server/discover";
  if (modern) {
    if (protocolHeader !== MCP_PROTOCOL_MODERN) {
      return json(
        rpcError(message.id, -32002, `MCP-Protocol-Version must be ${MCP_PROTOCOL_MODERN}`),
        400,
        {},
        false,
      );
    }
    const methodHeader = request.headers.get("mcp-method");
    if (methodHeader !== message.method) {
      return json(
        rpcError(message.id, -32020, "Mcp-Method header does not match JSON-RPC method"),
        400,
        {},
        false,
      );
    }
    if (
      message.method === "tools/call" &&
      request.headers.get("mcp-name") !== message.params?.name
    ) {
      return json(
        rpcError(message.id, -32020, "Mcp-Name header does not match params.name"),
        400,
        {},
        false,
      );
    }
    const metadataVersion =
      message.params?._meta?.["io.modelcontextprotocol/protocolVersion"];
    if (metadataVersion && metadataVersion !== MCP_PROTOCOL_MODERN) {
      return json(
        rpcError(message.id, -32020, "Protocol version in _meta does not match header"),
        400,
        {},
        false,
      );
    }
  }
  if (message.id === undefined || message.id === null) {
    return new Response(null, { status: 202, headers: baseHeaders(false) });
  }
  let payload;
  if (message.method === "server/discover") {
    payload = rpcResult(
      message.id,
      {
        supportedVersions: [MCP_PROTOCOL_MODERN, MCP_PROTOCOL_LEGACY],
        capabilities: { tools: {} },
        instructions: MCP_INSTRUCTIONS,
        ttlMs: 300000,
        cacheScope: "public",
      },
      true,
    );
  } else if (message.method === "initialize") {
    const requested = message.params?.protocolVersion;
    const selected = MCP_PROTOCOLS.slice(1).includes(requested)
      ? requested
      : MCP_PROTOCOL_LEGACY;
    payload = rpcResult(message.id, {
      protocolVersion: selected,
      capabilities: { tools: { listChanged: false } },
      serverInfo: SERVER_INFO,
      instructions: MCP_INSTRUCTIONS,
    });
  } else if (message.method === "ping") {
    payload = rpcResult(message.id, {}, modern);
  } else if (message.method === "tools/list") {
    payload = rpcResult(
      message.id,
      {
        tools: MCP_TOOLS,
        ...(modern ? { ttlMs: 300000, cacheScope: "public" } : {}),
      },
      modern,
    );
  } else if (message.method === "tools/call") {
    const name = message.params?.name;
    if (typeof name !== "string") {
      payload = rpcError(message.id, -32602, "params.name must be a tool name");
    } else {
      payload = rpcResult(
        message.id,
        toolResult(name, message.params?.arguments),
        modern,
      );
    }
  } else {
    payload = rpcError(message.id, -32601, `Method not found: ${message.method}`);
  }
  return json(payload, 200, {
    "mcp-protocol-version": modern
      ? MCP_PROTOCOL_MODERN
      : protocolHeader ?? MCP_PROTOCOL_LEGACY,
  }, false);
}

function safeHtml(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[character],
  );
}

function home(route = "/") {
  const stats = DATA.stats;
  const fmt = (value) => Number(value).toLocaleString("en-US");
  const layers = DATA.database_schema.layers
    .map(
      (layer, index) =>
        `<article class="layer"><div class="layer-no">0${index + 1}</div><h3>${safeHtml(layer.name)}</h3><p>${safeHtml(layer.purpose)}</p><div class="chips">${(layer.tables ?? layer.views ?? []).map((name) => `<code>${safeHtml(name)}</code>`).join("")}</div></article>`,
    )
    .join("");
  const decisions = Object.entries(DATA.rights.database_decisions)
    .map(
      ([database, decision]) =>
        `<tr><th>${safeHtml(database)}</th><td>${safeHtml(decision.assessment)}</td><td><span class="decision">${safeHtml(decision.public_hosting_decision)}</span></td><td><a href="${safeHtml(decision.terms_url)}" target="_blank" rel="noopener noreferrer">Terms ↗</a></td></tr>`,
    )
    .join("");
  const toolCards = MCP_TOOLS.map(
    (tool) =>
      `<article class="tool-card"><code>${safeHtml(tool.name)}</code><h3>${safeHtml(tool.title)}</h3><p>${safeHtml(tool.description)}</p></article>`,
  ).join("");
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Rights-filtered AMP evidence catalog, database audit aggregates, benchmark, API and MCP server.">
<title>AMP Evidence Atlas · Public-safe beta</title>
<style>
:root{--ink:#122236;--muted:#5f6f81;--line:#d9e2ea;--bg:#f3f6f8;--card:#fff;--navy:#0b2747;--blue:#1766a8;--teal:#087d7d;--mint:#d9f3ec;--amber:#a26400;--soft:#eaf1f6;--shadow:0 14px 38px rgba(17,48,78,.08)}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:82px}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.58 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--blue)}button,input,select,textarea{font:inherit}
.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:12px;z-index:99;background:#fff;padding:10px}
.top{position:sticky;top:0;z-index:20;background:rgba(11,39,71,.95);backdrop-filter:blur(12px);color:#fff;border-bottom:1px solid #ffffff20}.nav,.hero,.wrap,.footer-in{max-width:1200px;margin:auto;padding-left:24px;padding-right:24px}.nav{min-height:68px;display:flex;align-items:center;gap:24px}.brand{font-weight:790;font-size:18px;letter-spacing:-.2px;color:#fff;text-decoration:none}.navlinks{margin-left:auto;display:flex;gap:20px}.navlinks a{color:#d9e9f5;text-decoration:none;font-size:13px}.navlinks a:hover{color:#fff}.beta{border:1px solid #76d7c5;border-radius:999px;color:#bdf4e8;padding:4px 9px;font-size:11px}
.hero-bg{background:radial-gradient(circle at 84% 16%,#1a9b9588 0,transparent 28%),linear-gradient(125deg,#081f3b,#104d7b 65%,#076e72);color:#fff;overflow:hidden}.hero{padding-top:76px;padding-bottom:82px;position:relative}.eyebrow{text-transform:uppercase;letter-spacing:1.8px;color:#a9ece1;font-weight:750;font-size:12px}.hero h1{font-size:clamp(39px,6vw,70px);line-height:1.01;letter-spacing:-2.7px;margin:16px 0;max-width:920px}.hero-copy{max-width:790px;color:#dcebf5;font-size:19px}.actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}.btn{display:inline-flex;align-items:center;justify-content:center;border:1px solid #ffffff40;border-radius:8px;padding:11px 16px;color:#fff;text-decoration:none;font-weight:720;background:#ffffff10}.btn.primary{background:#fff;color:var(--navy)}.scope{margin-top:28px;max-width:940px;padding:13px 16px;border:1px solid #ffffff35;background:#031b2c44;border-radius:9px;color:#d5e6f1;font-size:13px}
.wrap{padding-top:52px;padding-bottom:66px}.section{margin-top:72px}.section:first-child{margin-top:0}.section-head{display:grid;grid-template-columns:1fr minmax(260px,520px);gap:30px;align-items:end;margin-bottom:22px}.kicker{text-transform:uppercase;letter-spacing:1.5px;color:var(--teal);font-weight:800;font-size:11px}.section h2{font-size:clamp(28px,3.5vw,42px);line-height:1.12;letter-spacing:-1.2px;margin:7px 0}.lead{color:var(--muted);font-size:16px;margin:0}
.metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-top:-30px;position:relative}.metric{background:#fff;border:1px solid var(--line);border-radius:11px;padding:18px;box-shadow:var(--shadow)}.metric b{display:block;font-size:28px;letter-spacing:-1px;color:var(--blue)}.metric span{color:var(--muted);font-size:12px}
.layers{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.layer{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:19px;min-height:190px}.layer-no{font:700 11px ui-monospace,monospace;color:var(--teal)}.layer h3{text-transform:capitalize;margin:16px 0 4px;font-size:20px}.layer p{color:var(--muted);margin:0 0 13px}.chips{display:flex;flex-wrap:wrap;gap:5px}.chips code,.tool-card code,.endpoint code{font:11px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--soft);padding:4px 6px;border-radius:5px;overflow-wrap:anywhere}
.panel{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:22px;box-shadow:var(--shadow)}.toolbar{display:grid;grid-template-columns:130px minmax(180px,1fr) 150px 150px auto;gap:8px}.field{display:flex;flex-direction:column;gap:5px}.field label{font-size:11px;color:var(--muted);font-weight:700}.field input,.field select,.field textarea,.tester input,.tester select,.tester textarea{border:1px solid #b9c8d4;border-radius:7px;background:#fff;padding:10px 11px;min-width:0}.run{align-self:end;border:0;border-radius:7px;background:var(--blue);color:#fff;padding:11px 17px;font-weight:760;cursor:pointer}.status{color:var(--muted);font-size:13px;margin:14px 0 2px}.results{display:grid;grid-template-columns:repeat(2,1fr);gap:9px;margin-top:14px}.result{border:1px solid var(--line);border-radius:9px;padding:14px;min-width:0}.result h3{font-size:15px;margin:0 0 5px}.result p{margin:5px 0;color:var(--muted);font-size:13px}.seq{font:11px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;word-break:break-all;color:#31536d}.tagrow{display:flex;flex-wrap:wrap;gap:5px;margin-top:9px}.pill{background:var(--soft);color:#35516a;border-radius:999px;padding:3px 7px;font-size:10px}
.audit-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.audit-list,.category-list{display:flex;flex-direction:column;gap:9px}.bar-row{display:grid;grid-template-columns:120px 1fr 80px;gap:9px;align-items:center;font-size:12px}.bar{height:8px;background:#e7edf2;border-radius:999px;overflow:hidden}.bar i{height:100%;display:block;background:linear-gradient(90deg,var(--blue),var(--teal));border-radius:999px}.caution{border:1px solid #ead6a1;background:#fff8e8;color:#624a13;border-radius:8px;padding:12px 14px;font-size:13px;margin-top:13px}
.benchmark-list{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.question{border:1px solid var(--line);border-radius:10px;padding:15px;background:#fff}.question h3{font-size:14px;margin:7px 0}.question details{color:var(--muted);font-size:12px}.filters{display:flex;gap:8px;align-items:end;margin-bottom:14px}.filters .field{min-width:220px}
.dev-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.endpoint-list{display:flex;flex-direction:column;gap:7px}.endpoint{display:grid;grid-template-columns:54px 1fr;gap:8px;align-items:center;border:1px solid var(--line);border-radius:7px;padding:8px}.method{background:var(--mint);color:#065f5d;font-weight:800;font-size:10px;text-align:center;border-radius:4px;padding:3px}.codebox{background:#0c2135;color:#dcecf5;border-radius:8px;padding:13px;font:12px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;overflow:auto;min-height:86px}.copy{border:1px solid var(--line);background:#fff;border-radius:6px;padding:6px 9px;cursor:pointer;font-size:11px}.tool-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:13px}.tool-card{border:1px solid var(--line);border-radius:9px;padding:13px}.tool-card h3{font-size:14px;margin:9px 0 3px}.tool-card p{color:var(--muted);font-size:12px;margin:0}.tester{display:grid;gap:8px;margin-top:14px}.tester-row{display:grid;grid-template-columns:1fr auto;gap:8px}.output{max-height:360px;min-height:120px}
.rights-table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);font-size:12px}.rights-table th,.rights-table td{text-align:left;padding:10px;border-bottom:1px solid var(--line);vertical-align:top}.rights-table th{font-weight:800}.decision{display:inline-block;background:#fff2d5;color:#735000;border-radius:5px;padding:2px 5px}.governance-grid{display:grid;grid-template-columns:2fr 1fr;gap:14px}.plain-list{margin:8px 0 0;padding-left:19px;color:var(--muted)}
footer{background:var(--navy);color:#bad0df}.footer-in{padding-top:34px;padding-bottom:38px;display:flex;justify-content:space-between;gap:20px}.footer-in code{color:#d9eee9;font:11px ui-monospace,monospace}.footer-in a{color:#c7e7f4}
@media(max-width:980px){.metrics{grid-template-columns:repeat(3,1fr)}.layers{grid-template-columns:repeat(2,1fr)}.toolbar{grid-template-columns:1fr 2fr 1fr}.toolbar .run{grid-column:3}.audit-grid,.dev-grid,.governance-grid{grid-template-columns:1fr}.navlinks{display:none}}
@media(max-width:650px){.hero{padding-top:54px;padding-bottom:60px}.hero h1{letter-spacing:-1.7px}.wrap{padding-left:16px;padding-right:16px}.metrics,.layers,.results,.benchmark-list,.tool-grid{grid-template-columns:1fr}.section-head{grid-template-columns:1fr}.toolbar{grid-template-columns:1fr}.toolbar .run{grid-column:auto}.nav{padding-left:16px;padding-right:16px}.beta{margin-left:auto}.bar-row{grid-template-columns:95px 1fr 58px}.footer-in{flex-direction:column}.rights-table{display:block;overflow-x:auto}}
</style>
</head>
<body data-route="${safeHtml(route)}">
<a class="skip" href="#main">Skip to content</a>
<div class="top"><nav class="nav" aria-label="Primary"><a class="brand" href="/">AMP Evidence Atlas</a><div class="navlinks"><a href="/#architecture">Data model</a><a href="/#explore">Explore</a><a href="/#audit">Audit</a><a href="/#benchmark">Benchmark</a><a href="/developers">API &amp; MCP</a><a href="/#governance">Governance</a></div><span class="beta">PUBLIC-SAFE BETA</span></nav></div>
<header class="hero-bg"><div class="hero"><div class="eyebrow">Evidence reconstruction · database audit · AI-ready access</div><h1>Traceable AMP evidence,<br>served responsibly.</h1><p class="hero-copy">Explore project-created peptide and paper indexes, inspect aggregate database-audit outcomes, evaluate grounding questions, or connect an AI agent through a read-only MCP server.</p><div class="actions"><a class="btn primary" href="#explore">Explore catalog</a><a class="btn" href="#developers">Connect an AI agent</a><a class="btn" href="/api/v1/schema/openapi.json">OpenAPI 3.1</a></div><div class="scope"><b>Public scope:</b> no bulk copied APD6, CAMP, DBAASP or dbAMP fields; no DRAMP patent content; no article full text; and no row-level database comparisons. Human validation remains incomplete.</div></div></header>
<main class="wrap" id="main">
<section class="metrics" aria-label="Release statistics"><div class="metric"><b>${fmt(stats.papers)}</b><span>papers indexed</span></div><div class="metric"><b>${fmt(stats.peptides)}</b><span>peptide summaries</span></div><div class="metric"><b>${fmt(stats.activity_observations_aggregated)}</b><span>activity rows aggregated</span></div><div class="metric"><b>${fmt(stats.audit_records_aggregated)}</b><span>audit rows aggregated</span></div><div class="metric"><b>${fmt(stats.source_conflicts_aggregated)}</b><span>conflict statuses</span></div></section>

<section class="section" id="architecture"><div class="section-head"><div><div class="kicker">Normalized database</div><h2>Six layers, one rights-safe read model.</h2></div><p class="lead">System provenance, source governance, discovery catalogs, evidence aggregates, evaluation items and stable API views are separated so public clients cannot accidentally cross into restricted raw records.</p></div><div class="layers">${layers}</div></section>

<section class="section" id="explore"><div class="section-head"><div><div class="kicker">Catalog</div><h2>Browse peptides and papers.</h2></div><p class="lead">Search and filter derived summaries. Counts describe the internal evidence corpus, while the public response intentionally omits copied source fields and row-level comparisons.</p></div><div class="panel"><form class="toolbar" id="explore-form"><div class="field"><label for="entity">Entity</label><select id="entity"><option value="peptides">Peptides</option><option value="papers">Papers</option></select></div><div class="field"><label for="catalog-q">Query</label><input id="catalog-q" placeholder="LL-37, KTA, DOI or paper ID" autocomplete="off"></div><div class="field peptide-filter"><label for="endpoint">Endpoint</label><select id="endpoint"><option value="">Any endpoint</option><option>MIC</option><option>MBC</option><option>IC50</option><option>EC50</option><option>CC50</option></select></div><div class="field"><label for="catalog-sort">Sort</label><select id="catalog-sort"><option value="">Identifier / name</option><option value="activity_count">Activity count</option><option value="paper_count">Paper count</option><option value="audit_count">Audit count</option></select></div><button class="run">Run query</button></form><div class="status" id="catalog-status">Loading public-safe summaries…</div><div class="results" id="catalog-results" aria-live="polite"></div></div></section>

<section class="section" id="audit"><div class="section-head"><div><div class="kicker">Database audit</div><h2>See disagreement patterns, not verdicts.</h2></div><p class="lead">The atlas preserves source-verified, source-conflict and other review states. Here they are exposed only as aggregates and must not be read as automatically human-confirmed database errors.</p></div><div class="audit-grid"><div class="panel"><h3>Audit status by database</h3><div class="audit-list" id="audit-databases">Loading…</div></div><div class="panel"><h3>Most frequent difference categories</h3><div class="category-list" id="audit-categories">Loading…</div></div></div><div class="caution"><b>Interpretation boundary.</b> Multi-agent agreement is not a human gold standard. Stratified manual validation and source-permission follow-up remain release blockers for the unrestricted resource.</div></section>

<section class="section" id="benchmark"><div class="section-head"><div><div class="kicker">Evaluation</div><h2>Grounding benchmark preview.</h2></div><p class="lead">Forty project-authored questions test whether a model can recover activity values, sequence details, database–paper conflicts and evidence limitations. This pilot is not yet a resource-grade gold standard.</p></div><div class="panel"><div class="filters"><div class="field"><label for="benchmark-category">Category</label><select id="benchmark-category"><option value="">All categories</option></select></div><button class="run" id="benchmark-run">Load items</button></div><div class="benchmark-list" id="benchmark-list">Loading…</div></div></section>

<section class="section" id="developers"><div class="section-head"><div><div class="kicker">Developer &amp; AI access</div><h2>One corpus, two stable interfaces.</h2></div><p class="lead">Use hierarchical REST endpoints for applications, or let an AI client discover and invoke ten bounded read-only tools through the same-origin Streamable HTTP MCP endpoint.</p></div><div class="dev-grid"><div class="panel"><h3>REST API v1</h3><p class="lead">Canonical endpoints return a consistent <code>data / meta / links</code> envelope. Legacy flat paths remain aliases.</p><div class="endpoint-list"><div class="endpoint"><span class="method">GET</span><code>/api/v1/system/stats</code></div><div class="endpoint"><span class="method">GET</span><code>/api/v1/catalog/peptides</code></div><div class="endpoint"><span class="method">GET</span><code>/api/v1/catalog/papers</code></div><div class="endpoint"><span class="method">GET</span><code>/api/v1/evidence/audit-summary</code></div><div class="endpoint"><span class="method">GET</span><code>/api/v1/evaluation/benchmark</code></div><div class="endpoint"><span class="method">GET</span><code>/api/v1/schema/database</code></div></div><p><a href="/api/v1/schema/openapi.json">Open OpenAPI 3.1 schema →</a></p></div><div class="panel"><h3>Streamable HTTP MCP</h3><p class="lead">Stateless endpoint at <code>/api/mcp</code>, supporting modern <code>2026-07-28</code> discovery and legacy <code>2025-11-25</code> initialization. No authentication or write tools.</p><div class="codebox" id="mcp-config">{"mcpServers":{"amp-evidence-atlas":{"url":"${SERVER_INFO.websiteUrl}/api/mcp"}}}</div><p><button class="copy" data-copy="mcp-config">Copy generic client config</button> <a href="/api/mcp">Server descriptor</a></p><div class="codebox" id="mcp-curl">curl -X POST ${SERVER_INFO.websiteUrl}/api/mcp \\
  -H 'Content-Type: application/json' \\
  -H 'Accept: application/json, text/event-stream' \\
  -H 'MCP-Protocol-Version: 2026-07-28' \\
  -H 'Mcp-Method: tools/list' \\
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'</div><p><button class="copy" data-copy="mcp-curl">Copy cURL</button></p></div></div>
<div class="tool-grid">${toolCards}</div>
<div class="dev-grid" style="margin-top:14px"><div class="panel"><h3>Live API console</h3><div class="tester"><div class="tester-row"><input id="api-path" aria-label="API path" value="/api/v1/catalog/peptides?q=LL-37&amp;limit=3"><button class="run" id="api-run">GET</button></div><pre class="codebox output" id="api-output">Run a rights-safe API request.</pre></div></div><div class="panel"><h3>Live MCP tool call</h3><div class="tester"><select id="mcp-tool" aria-label="MCP tool">${MCP_TOOLS.map((tool) => `<option>${safeHtml(tool.name)}</option>`).join("")}</select><textarea id="mcp-args" rows="3" aria-label="MCP tool arguments">{}</textarea><button class="run" id="mcp-run">Call tool</button><pre class="codebox output" id="mcp-output">Call a modern stateless MCP tool.</pre></div></div></div></section>

<section class="section" id="governance"><div class="section-head"><div><div class="kicker">Rights &amp; release governance</div><h2>Public by derivation, limited by design.</h2></div><p class="lead">This beta publishes project-created metadata and aggregates while the immutable full evidence package stays internal until permissions, validation and publication review close.</p></div><div class="governance-grid"><div class="panel" style="overflow:auto"><table class="rights-table"><thead><tr><th>Source</th><th>Assessment</th><th>Public decision</th><th>Reference</th></tr></thead><tbody>${decisions}</tbody></table></div><div class="panel"><h3>Never exposed here</h3><ul class="plain-list">${DATA.rights.not_public_components.map((item) => `<li>${safeHtml(item)}</li>`).join("")}</ul><h3>Open permission follow-up</h3><div class="chips">${DATA.rights.permission_follow_up_still_required.map((item) => `<code>${safeHtml(item)}</code>`).join("")}</div><p><a href="/api/v1/governance/rights">Machine-readable policy →</a></p></div></div></section>
</main>
<footer><div class="footer-in"><div><b>AMP Evidence Atlas</b><br>Rights-filtered public beta · ${safeHtml(DATA.release.generated_at)}</div><div>Release <code>${safeHtml(RELEASE_ID)}</code><br>Payload <code>${safeHtml(RELEASE_HASH.slice(0, 18))}…</code></div><div><a href="/healthz">Status</a> · <a href="/api/v1/schema/openapi.json">OpenAPI</a> · <a href="/api/mcp">MCP</a> · <a href="/api/v1/governance/rights">Rights</a></div></div></footer>
<script>
const esc=function(value){return String(value==null?"":value).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})};
async function getData(path){const response=await fetch(path);const payload=await response.json();if(!response.ok)throw new Error(payload.error&&payload.error.message||response.statusText);return payload.data===undefined?payload:payload.data}
function pretty(value){return JSON.stringify(value,null,2)}
const catalogForm=document.getElementById("explore-form"),entity=document.getElementById("entity"),catalogResults=document.getElementById("catalog-results"),catalogStatus=document.getElementById("catalog-status");
function renderCatalog(data,type){catalogStatus.textContent=data.total.toLocaleString()+" matching "+type+" · showing "+data.items.length;catalogResults.innerHTML=data.items.map(function(item){if(type==="peptides"){return '<article class="result"><h3>'+esc(item.name)+'</h3><div class="seq">'+esc(item.sequences.join(" · ")||"No displayed sequence")+'</div><p>'+item.activity_count.toLocaleString()+' aggregate activities across '+item.paper_count+' papers</p><div class="tagrow">'+item.endpoints.slice(0,4).map(function(pair){return '<span class="pill">'+esc(pair[0])+' · '+pair[1]+'</span>'}).join("")+'</div></article>'}return '<article class="result"><h3>'+esc(item.id)+'</h3><div class="seq">'+esc(item.doi||"DOI unavailable")+'</div><p>'+item.activity_count.toLocaleString()+' activities · '+item.audit_count.toLocaleString()+' audits · '+item.mechanism_count.toLocaleString()+' mechanism claims</p><div class="tagrow"><span class="pill">'+esc(item.review_status)+'</span><span class="pill">'+esc(item.publication_grade)+'</span></div></article>'}).join("")||'<p class="lead">No public-safe summary matched.</p>'}
async function loadCatalog(){const type=entity.value;document.querySelector(".peptide-filter").style.display=type==="peptides"?"flex":"none";catalogStatus.textContent="Loading…";const q=document.getElementById("catalog-q").value.trim(),sort=document.getElementById("catalog-sort").value;let path="/api/v1/catalog/"+type+"?limit=8";if(q)path+="&q="+encodeURIComponent(q);if(sort&&!(type==="papers"&&sort==="paper_count"))path+="&sort="+encodeURIComponent(sort);if(type==="peptides"&&document.getElementById("endpoint").value)path+="&endpoint="+encodeURIComponent(document.getElementById("endpoint").value);try{renderCatalog(await getData(path),type)}catch(error){catalogStatus.textContent="Query failed: "+error.message}}
catalogForm.addEventListener("submit",function(event){event.preventDefault();loadCatalog()});entity.addEventListener("change",loadCatalog);
async function loadAudit(){try{const data=await getData("/api/v1/evidence/audit-summary");const rows=[];Object.keys(data.by_database_status).forEach(function(database){Object.keys(data.by_database_status[database]).forEach(function(status){rows.push([database+" · "+status,data.by_database_status[database][status]])})});const max=Math.max.apply(null,rows.map(function(row){return row[1]}));document.getElementById("audit-databases").innerHTML=rows.map(function(row){return '<div class="bar-row"><span>'+esc(row[0])+'</span><span class="bar"><i style="width:'+Math.max(1,row[1]/max*100)+'%"></i></span><b>'+row[1].toLocaleString()+'</b></div>'}).join("");const categories=data.difference_categories.slice(0,12),catMax=categories[0][1];document.getElementById("audit-categories").innerHTML=categories.map(function(row){return '<div class="bar-row"><span>'+esc(row[0])+'</span><span class="bar"><i style="width:'+Math.max(1,row[1]/catMax*100)+'%"></i></span><b>'+row[1].toLocaleString()+'</b></div>'}).join("")}catch(error){document.getElementById("audit-databases").textContent=error.message}}
const categorySelect=document.getElementById("benchmark-category");async function loadBenchmark(){try{let path="/api/v1/evaluation/benchmark?limit=8";if(categorySelect.value)path+="&category="+encodeURIComponent(categorySelect.value);const data=await getData(path);document.getElementById("benchmark-list").innerHTML=data.items.map(function(item){return '<article class="question"><span class="pill">'+esc(item.category)+'</span><h3>'+esc(item.question)+'</h3><details><summary>Show answer and source reference</summary><p>'+esc(item.answer)+'</p><div class="seq">'+esc(item.source_ref)+'</div></details></article>'}).join("");if(categorySelect.options.length===1){const all=await getData("/api/v1/evaluation/benchmark?limit=40");Array.from(new Set(all.items.map(function(item){return item.category}))).sort().forEach(function(category){const option=document.createElement("option");option.value=category;option.textContent=category;categorySelect.appendChild(option)})}}catch(error){document.getElementById("benchmark-list").textContent=error.message}}
document.getElementById("benchmark-run").addEventListener("click",loadBenchmark);
document.querySelectorAll("[data-copy]").forEach(function(button){button.addEventListener("click",async function(){await navigator.clipboard.writeText(document.getElementById(button.dataset.copy).textContent);button.textContent="Copied";setTimeout(function(){button.textContent=button.dataset.copy==="mcp-curl"?"Copy cURL":"Copy generic client config"},1300)})});
document.getElementById("api-run").addEventListener("click",async function(){const output=document.getElementById("api-output");try{const path=document.getElementById("api-path").value;if(!path.startsWith("/api/"))throw new Error("Only same-origin /api/ paths are allowed");output.textContent=pretty(await (await fetch(path)).json())}catch(error){output.textContent=error.message}});
document.getElementById("mcp-run").addEventListener("click",async function(){const output=document.getElementById("mcp-output"),name=document.getElementById("mcp-tool").value;try{const args=JSON.parse(document.getElementById("mcp-args").value||"{}"),response=await fetch("/api/mcp",{method:"POST",headers:{"content-type":"application/json","accept":"application/json, text/event-stream","mcp-protocol-version":"2026-07-28","mcp-method":"tools/call","mcp-name":name},body:JSON.stringify({jsonrpc:"2.0",id:1,method:"tools/call",params:{name:name,arguments:args,_meta:{"io.modelcontextprotocol/protocolVersion":"2026-07-28"}}})});output.textContent=pretty(await response.json())}catch(error){output.textContent=error.message}});
loadCatalog();loadAudit();loadBenchmark();if(document.body.dataset.route==="/developers"){setTimeout(function(){document.getElementById("developers").scrollIntoView()},60)}
</script>
</body></html>`;
}

function canonicalApi(url) {
  const path = url.pathname;
  if (path === "/api/v1/system/release") return apiSuccess(DATA.release, url);
  if (path === "/api/v1/system/stats") return apiSuccess(DATA.stats, url);
  if (path === "/api/v1/governance/rights") return apiSuccess(DATA.rights, url);
  if (path === "/api/v1/schema/database") {
    return apiSuccess(DATA.database_schema, url);
  }
  if (path === "/api/v1/schema/openapi.json") {
    return json(openapi(url.origin));
  }
  if (path === "/api/v1/evidence/audit-summary") {
    return apiSuccess(
      auditSummary({
        database: url.searchParams.get("database"),
        status: url.searchParams.get("status"),
      }),
      url,
    );
  }
  if (path === "/api/v1/catalog/search") {
    const limit = Math.min(
      25,
      Math.max(1, number(url.searchParams.get("limit"), 10)),
    );
    return apiSuccess(combinedSearch(url.searchParams.get("q"), limit), url);
  }
  if (path === "/api/v1/catalog/peptides") {
    const { offset, limit } = pageFrom(url);
    const items = filterPeptides({
      q: url.searchParams.get("q"),
      endpoint: url.searchParams.get("endpoint"),
      evidence_tier: url.searchParams.get("evidence_tier"),
      min_activity_count: url.searchParams.get("min_activity_count"),
      min_paper_count: url.searchParams.get("min_paper_count"),
      sort: url.searchParams.get("sort"),
    });
    const data = paginate(items, offset, limit);
    return apiSuccess(data, url, {
      pagination: {
        total: data.total,
        offset: data.offset,
        limit: data.limit,
        has_more: data.has_more,
      },
    });
  }
  const peptidePath = path.match(/^\/api\/v1\/catalog\/peptides\/(.+)$/);
  if (peptidePath) {
    let name;
    try {
      name = decodeURIComponent(peptidePath[1]);
    } catch {
      return apiError(url, 400, "invalid_path_encoding", "Invalid peptide-name encoding");
    }
    const item = DATA.peptides.find(
      (candidate) => normalized(candidate.name) === normalized(name),
    );
    return item
      ? apiSuccess(item, url)
      : apiError(url, 404, "peptide_not_found", `No peptide summary named ${name}`);
  }
  if (path === "/api/v1/catalog/papers") {
    const { offset, limit } = pageFrom(url);
    const items = filterPapers({
      q: url.searchParams.get("q"),
      review_status: url.searchParams.get("review_status"),
      publication_grade: url.searchParams.get("publication_grade"),
      min_activity_count: url.searchParams.get("min_activity_count"),
      sort: url.searchParams.get("sort"),
    });
    const data = paginate(items, offset, limit);
    return apiSuccess(data, url, {
      pagination: {
        total: data.total,
        offset: data.offset,
        limit: data.limit,
        has_more: data.has_more,
      },
    });
  }
  const paperPath = path.match(/^\/api\/v1\/catalog\/papers\/(.+)$/);
  if (paperPath) {
    let id;
    try {
      id = decodeURIComponent(paperPath[1]);
    } catch {
      return apiError(url, 400, "invalid_path_encoding", "Invalid paper-ID encoding");
    }
    const item = DATA.papers.find((candidate) => candidate.id === id);
    return item
      ? apiSuccess(item, url)
      : apiError(url, 404, "paper_not_found", `No paper summary with ID ${id}`);
  }
  if (path === "/api/v1/evaluation/benchmark") {
    const { offset, limit } = pageFrom(url, 40, 20);
    const data = paginate(
      benchmarkItems({
        id: url.searchParams.get("id"),
        category: url.searchParams.get("category"),
      }),
      offset,
      limit,
    );
    data.status = "pilot_not_resource_quality_gold_standard";
    return apiSuccess(data, url, {
      validation_status: "stratified_human_validation_incomplete",
    });
  }
  return null;
}

function legacyApi(url) {
  const query = normalized(url.searchParams.get("q"));
  if (url.pathname === "/api/v1/release") return json(DATA.release);
  if (url.pathname === "/api/v1/stats") return json(DATA.stats);
  if (url.pathname === "/api/v1/rights") return json(DATA.rights);
  if (url.pathname === "/api/v1/audit-summary") return json(DATA.audit_summary);
  if (url.pathname === "/api/v1/openapi.json") return json(openapi(url.origin));
  if (url.pathname === "/api/v1/search") {
    const limit = Math.min(25, Math.max(1, number(url.searchParams.get("limit"), 10)));
    return json({ ...combinedSearch(query, limit), rights_filtered: true });
  }
  if (url.pathname === "/api/v1/peptides") {
    const { offset, limit } = pageFrom(url);
    return json(paginate(filterPeptides({ q: query }), offset, limit));
  }
  if (url.pathname === "/api/v1/peptide") {
    const name = normalized(url.searchParams.get("name"));
    const item = DATA.peptides.find((candidate) => normalized(candidate.name) === name);
    return item ? json(item) : json({ error: "peptide_not_found" }, 404);
  }
  if (url.pathname === "/api/v1/papers") {
    const { offset, limit } = pageFrom(url);
    return json(paginate(filterPapers({ q: query }), offset, limit));
  }
  if (url.pathname === "/api/v1/paper") {
    const id = url.searchParams.get("id") ?? "";
    const item = DATA.papers.find((candidate) => candidate.id === id);
    return item ? json(item) : json({ error: "paper_not_found" }, 404);
  }
  if (url.pathname === "/api/v1/benchmark") {
    const items = benchmarkItems({ category: url.searchParams.get("category") });
    return json({
      total: items.length,
      items,
      status: "pilot_not_resource_quality_gold_standard",
    });
  }
  return null;
}

async function handle(request) {
  const url = new URL(request.url);
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        ...baseHeaders(false),
        "access-control-allow-methods": "GET, HEAD, POST, OPTIONS",
        "access-control-allow-headers":
          "accept, content-type, mcp-protocol-version, mcp-method, mcp-name",
        "access-control-max-age": "86400",
      },
    });
  }
  if ([MCP_PUBLIC_PATH, "/mcp"].includes(url.pathname)) return handleMcp(request, url);
  if (!["GET", "HEAD"].includes(request.method)) {
    return apiError(url, 405, "method_not_allowed", "Only GET, HEAD and OPTIONS are supported");
  }
  if (request.headers.get("if-none-match") === ETAG) {
    return new Response(null, { status: 304, headers: baseHeaders(true) });
  }
  let response;
  if (
    url.pathname === "/" ||
    url.pathname === "/index.html" ||
    ["/explore", "/audit", "/benchmark", "/developers", "/governance"].includes(
      url.pathname,
    )
  ) {
    response = text(home(url.pathname), "text/html; charset=utf-8");
  } else if (url.pathname === "/healthz") {
    response = json({
      status: "ok",
      release_id: RELEASE_ID,
      scope: "public_safe_beta",
      api_version: "v1.1",
      mcp_protocols: [MCP_PROTOCOL_MODERN, MCP_PROTOCOL_LEGACY],
    });
  } else if (url.pathname === "/robots.txt") {
    response = text("User-agent: *\nAllow: /\n");
  } else if (url.pathname === "/.well-known/mcp.json") {
    response = json(mcpDescriptor(url.origin));
  } else if (url.pathname.startsWith("/api/v1/")) {
    response =
      canonicalApi(url) ??
      legacyApi(url) ??
      apiError(url, 404, "route_not_found", "No API route matches this path");
  } else {
    response = apiError(url, 404, "not_found", "No resource matches this path");
  }
  if (request.method === "HEAD") {
    return new Response(null, { status: response.status, headers: response.headers });
  }
  return response;
}

export default { fetch: handle };
