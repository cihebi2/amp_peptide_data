#!/usr/bin/env python3
"""Public-network smoke test for the AMP Evidence Atlas portal, API and MCP."""

from __future__ import annotations

import argparse
import json
import ssl
import time
import urllib.error
import urllib.request
from typing import Any


DEFAULT_BASE = "https://amp-evidence-atlas.daoyu7974.chatgpt.site"


def fetch(
    base: str,
    path: str,
    *,
    attempts: int = 6,
    method: str = "GET",
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, bytes, dict[str, str]]:
    error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(
                base.rstrip("/") + path,
                data=body,
                method=method,
                headers={
                    "user-agent": "amp-evidence-atlas-release-smoke/2.0",
                    **(headers or {}),
                },
            )
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.status, response.read(), dict(response.headers.items())
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            if exc.code < 500 or attempt + 1 == attempts:
                return exc.code, payload, dict(exc.headers.items())
            error = exc
        except (urllib.error.URLError, TimeoutError, ssl.SSLError) as exc:
            error = exc
        if attempt + 1 < attempts:
            time.sleep(2 + attempt)
    raise RuntimeError(f"failed after {attempts} attempts: {method} {path}: {error}")


def get_json(base: str, path: str) -> tuple[int, dict[str, Any], dict[str, str]]:
    status, body, headers = fetch(base, path)
    return status, json.loads(body), headers


def rpc(
    base: str,
    method: str,
    params: dict[str, Any],
    *,
    modern: bool,
    name: str | None = None,
    request_id: int = 1,
) -> tuple[int, dict[str, Any], dict[str, str]]:
    protocol = "2026-07-28" if modern else "2025-11-25"
    headers = {
        "content-type": "application/json",
        "accept": "application/json, text/event-stream",
        "mcp-protocol-version": protocol,
    }
    if modern:
        headers["mcp-method"] = method
        if name:
            headers["mcp-name"] = name
        params = {
            **params,
            "_meta": {
                **params.get("_meta", {}),
                "io.modelcontextprotocol/protocolVersion": protocol,
            },
        }
    body = json.dumps(
        {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
    ).encode()
    status, payload, response_headers = fetch(
        base, "/api/mcp", method="POST", body=body, headers=headers
    )
    return status, json.loads(payload), response_headers


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    checks: dict[str, bool] = {}
    observations: dict[str, Any] = {}

    home_status, home_body, _ = fetch(base, "/")
    home = home_body.decode("utf-8")
    checks["complete_portal"] = home_status == 200 and all(
        phrase in home
        for phrase in (
            "Six layers",
            "Browse peptides and papers",
            "Database audit",
            "Grounding benchmark",
            "Streamable HTTP MCP",
            "Rights &amp; release governance",
        )
    )
    observations["homepage_bytes"] = len(home_body)

    health_status, health, _ = get_json(base, "/healthz")
    checks["health"] = (
        health_status == 200
        and health.get("status") == "ok"
        and "2026-07-28" in health.get("mcp_protocols", [])
    )
    observations["health"] = health

    stats_status, stats_payload, stats_headers = get_json(
        base, "/api/v1/system/stats"
    )
    stats = stats_payload.get("data", {})
    checks["canonical_api_envelope"] = (
        stats_status == 200
        and stats.get("papers") == 1374
        and stats.get("peptides") == 9263
        and stats.get("audit_records_aggregated") == 128976
        and stats_payload.get("meta", {}).get("rights_filtered") is True
        and bool(stats_headers.get("ETag") or stats_headers.get("Etag"))
    )
    observations["stats"] = stats

    peptide_status, peptide_payload, _ = get_json(
        base,
        "/api/v1/catalog/peptides?endpoint=MIC&sort=activity_count&limit=5",
    )
    peptide_items = peptide_payload.get("data", {}).get("items", [])
    checks["catalog_filters"] = (
        peptide_status == 200
        and len(peptide_items) == 5
        and all(
            any(str(pair[0]).lower() == "mic" for pair in item.get("endpoints", []))
            for item in peptide_items
        )
    )
    observations["top_mic_activity_counts"] = [
        item.get("activity_count") for item in peptide_items
    ]

    schema_status, schema_payload, _ = get_json(base, "/api/v1/schema/database")
    layers = [
        layer.get("name")
        for layer in schema_payload.get("data", {}).get("layers", [])
    ]
    checks["database_hierarchy"] = (
        schema_status == 200
        and layers
        == ["system", "governance", "catalog", "evidence", "evaluation", "api"]
        and schema_payload.get("data", {}).get("public_safe") is True
    )
    observations["database_layers"] = layers

    audit_status, audit_payload, _ = get_json(
        base, "/api/v1/evidence/audit-summary?database=DBAASP"
    )
    checks["audit_aggregates"] = (
        audit_status == 200
        and list(
            audit_payload.get("data", {}).get("by_database_status", {}).keys()
        )
        == ["DBAASP"]
        and "not by itself"
        in audit_payload.get("data", {}).get("interpretation", "")
    )

    benchmark_status, benchmark_payload, _ = get_json(
        base, "/api/v1/evaluation/benchmark?category=activity_value&limit=5"
    )
    benchmark = benchmark_payload.get("data", {})
    checks["benchmark"] = (
        benchmark_status == 200
        and benchmark.get("total") == 12
        and len(benchmark.get("items", [])) == 5
        and benchmark_payload.get("meta", {}).get("validation_status")
        == "stratified_human_validation_incomplete"
    )

    rights_status, rights_payload, _ = get_json(
        base, "/api/v1/governance/rights"
    )
    rights = rights_payload.get("data", {})
    checks["rights"] = (
        rights_status == 200
        and rights.get("source_database_raw_fields_exposed") is False
        and rights.get("full_internal_v1_payload_publicly_redistributed") is False
    )

    spec_status, spec, _ = get_json(base, "/api/v1/schema/openapi.json")
    checks["openapi"] = (
        spec_status == 200
        and spec.get("openapi") == "3.1.0"
        and len(spec.get("paths", {})) >= 14
    )
    observations["openapi_paths"] = len(spec.get("paths", {}))

    descriptor_status, descriptor, _ = get_json(base, "/api/mcp")
    checks["mcp_descriptor"] = (
        descriptor_status == 200
        and descriptor.get("transport", {}).get("url") == f"{base}/api/mcp"
        and descriptor.get("capabilities", {}).get("tools", {}).get("count") == 10
        and descriptor.get("authentication", {}).get("required") is False
    )

    init_status, initialize, _ = rpc(
        base,
        "initialize",
        {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "public-smoke", "version": "2"},
        },
        modern=False,
    )
    checks["mcp_legacy_initialize"] = (
        init_status == 200
        and initialize.get("result", {}).get("protocolVersion") == "2025-11-25"
        and initialize.get("result", {}).get("serverInfo", {}).get("name")
        == "amp-evidence-atlas"
    )

    legacy_tools_status, legacy_tools, _ = rpc(
        base, "tools/list", {}, modern=False
    )
    checks["mcp_legacy_tools"] = (
        legacy_tools_status == 200
        and len(legacy_tools.get("result", {}).get("tools", [])) == 10
        and all(
            tool.get("annotations", {}).get("readOnlyHint") is True
            for tool in legacy_tools.get("result", {}).get("tools", [])
        )
    )

    discover_status, discover, _ = rpc(
        base, "server/discover", {}, modern=True
    )
    checks["mcp_modern_discover"] = (
        discover_status == 200
        and "2026-07-28"
        in discover.get("result", {}).get("supportedVersions", [])
        and discover.get("result", {}).get("resultType") == "complete"
        and discover.get("result", {})
        .get("_meta", {})
        .get("io.modelcontextprotocol/serverInfo", {})
        .get("name")
        == "amp-evidence-atlas"
    )

    modern_tools_status, modern_tools, _ = rpc(
        base, "tools/list", {}, modern=True
    )
    checks["mcp_modern_tools"] = (
        modern_tools_status == 200
        and len(modern_tools.get("result", {}).get("tools", [])) == 10
        and modern_tools.get("result", {}).get("cacheScope") == "public"
        and modern_tools.get("result", {}).get("ttlMs") == 300000
    )

    call_status, tool_call, _ = rpc(
        base,
        "tools/call",
        {"name": "atlas.search", "arguments": {"query": "LL-37", "limit": 2}},
        modern=True,
        name="atlas.search",
    )
    structured = tool_call.get("result", {}).get("structuredContent", {})
    checks["mcp_ai_tool_call"] = (
        call_status == 200
        and tool_call.get("result", {}).get("isError") is False
        and bool(structured.get("peptides"))
        and len(structured.get("peptides", [])) <= 2
    )
    observations["mcp_search_peptide_hits"] = len(structured.get("peptides", []))

    result = {
        "base_url": base,
        "passed": all(checks.values()),
        "check_count": len(checks),
        "failure_count": sum(not passed for passed in checks.values()),
        "checks": checks,
        "observations": observations,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
