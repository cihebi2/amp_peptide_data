#!/usr/bin/env python3
"""Local preview website/API for AMP Evidence Atlas v1 RC1.

No external dependencies are required. The server streams the large release TSVs
on demand, so the browser never has to download all audit rows for search.
"""

from __future__ import annotations

import argparse
import csv
import json
import mimetypes
import posixpath
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = Path(__file__).resolve().parent
STATIC_ROOT = WEB_ROOT / "static"
RELEASE_DIR = ROOT / "releases" / "amp_evidence_atlas_v1_rc1"
MANIFEST_PATH = RELEASE_DIR / "release_manifest.json"

MAX_LIMIT = 200
DEFAULT_LIMIT = 50

TABLES = {
    "papers": RELEASE_DIR / "papers.tsv",
    "database_records": RELEASE_DIR / "database_record_audits.tsv",
    "activities": RELEASE_DIR / "activity_observations.tsv",
    "mechanisms": RELEASE_DIR / "mechanism_claims.tsv",
    "conflicts": RELEASE_DIR / "conflicts_and_cautions.tsv",
    "excluded": RELEASE_DIR / "excluded_blocked_papers.tsv",
}

DOWNLOAD_ALLOWLIST = {
    path.name: path
    for path in RELEASE_DIR.iterdir()
    if path.is_file() and path.suffix.lower() in {".tsv", ".json", ".txt", ".md"}
}
DOWNLOAD_ALLOWLIST["LICENSES.tsv"] = RELEASE_DIR / "LICENSES.tsv"


def read_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def iter_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as fh:
        yield from csv.DictReader(fh, dialect="excel-tab")


def compact_row(row: dict, fields: list[str]) -> dict:
    return {field: row.get(field, "") for field in fields}


def parse_limit(params: dict[str, list[str]]) -> int:
    try:
        limit = int(params.get("limit", [str(DEFAULT_LIMIT)])[0])
    except ValueError:
        limit = DEFAULT_LIMIT
    return max(1, min(MAX_LIMIT, limit))


def text_match(row: dict, query: str, fields: list[str]) -> bool:
    if not query:
        return True
    needle = query.casefold()
    return any(needle in str(row.get(field, "")).casefold() for field in fields)


def filter_match(row: dict, params: dict[str, list[str]]) -> bool:
    for key in ("database", "status", "paper_id", "public_v1_included"):
        value = params.get(key, [""])[0]
        if value and row.get(key, "") != value:
            return False
    category = params.get("category", [""])[0]
    if category and category not in row.get("difference_categories", ""):
        return False
    return True


def search_rows(params: dict[str, list[str]]) -> dict:
    query = params.get("q", [""])[0].strip()
    table = params.get("table", ["database_records"])[0] or "database_records"
    limit = parse_limit(params)
    if table not in TABLES:
        table = "database_records"

    if table == "papers":
        path = TABLES["papers"]
        fields = [
            "paper_id", "doi", "review_status", "publication_grade", "public_v1_included",
            "database_audit_records", "activity_records", "mechanism_claims", "exclusion_reason",
        ]
        query_fields = ["paper_id", "doi", "review_status", "exclusion_reason"]
    elif table == "activities":
        path = TABLES["activities"]
        fields = [
            "activity_record_id", "paper_id", "doi", "entity", "peptide", "endpoint",
            "raw_value", "raw_unit", "target", "evidence_ladder", "source_final_path",
        ]
        query_fields = ["activity_record_id", "paper_id", "doi", "entity", "peptide", "endpoint", "target"]
    elif table == "mechanisms":
        path = TABLES["mechanisms"]
        fields = [
            "mechanism_claim_id", "paper_id", "doi", "evidence_class", "direct_assay_types",
            "claim_text", "limitations", "source_final_path",
        ]
        query_fields = ["mechanism_claim_id", "paper_id", "doi", "evidence_class", "claim_text", "limitations"]
    elif table == "conflicts":
        path = TABLES["conflicts"]
        fields = [
            "issue_id", "issue_scope", "paper_id", "doi", "database", "source_id", "status",
            "difference_categories", "severity_hint", "summary", "source_final_path",
        ]
        query_fields = ["issue_id", "paper_id", "doi", "database", "source_id", "status", "difference_categories", "summary"]
    else:
        path = TABLES["database_records"]
        fields = [
            "audit_record_id", "paper_id", "doi", "database", "source_id", "status",
            "difference_categories", "database_subject", "database_measure", "database_value",
            "primary_source_subject", "primary_source_value", "source_final_path",
        ]
        query_fields = [
            "audit_record_id", "paper_id", "doi", "database", "source_id", "status",
            "difference_categories", "database_subject", "database_measure", "primary_source_subject",
        ]

    results = []
    scanned = 0
    matched = 0
    for row in iter_tsv(path):
        scanned += 1
        if not filter_match(row, params):
            continue
        if not text_match(row, query, query_fields):
            continue
        matched += 1
        if len(results) < limit:
            results.append(compact_row(row, fields))
    return {
        "table": table,
        "query": query,
        "limit": limit,
        "scanned_rows": scanned,
        "matched_rows": matched,
        "returned_rows": len(results),
        "results": results,
    }


def paper_detail(paper_id: str) -> dict:
    paper = None
    for row in iter_tsv(TABLES["papers"]):
        if row.get("paper_id") == paper_id:
            paper = row
            break
    if paper is None:
        return {"error": "not_found", "paper_id": paper_id}

    params = {"paper_id": [paper_id], "limit": ["25"]}
    return {
        "paper": paper,
        "database_records": search_rows({**params, "table": ["database_records"]}),
        "activities": search_rows({**params, "table": ["activities"]}),
        "mechanisms": search_rows({**params, "table": ["mechanisms"]}),
        "conflicts": search_rows({**params, "table": ["conflicts"]}),
    }


def database_record_detail(database: str, source_id: str, params: dict[str, list[str]]) -> dict:
    limit = parse_limit(params)
    database_decoded = unquote(database)
    source_decoded = unquote(source_id).casefold()
    results = []
    scanned = 0
    for row in iter_tsv(TABLES["database_records"]):
        scanned += 1
        if row.get("database") != database_decoded:
            continue
        row_source = row.get("source_id", "")
        row_short = row_source.split(":")[-1]
        if source_decoded not in {row_source.casefold(), row_short.casefold()}:
            continue
        results.append(row)
        if len(results) >= limit:
            break
    return {
        "database": database_decoded,
        "source_id": unquote(source_id),
        "limit": limit,
        "scanned_rows_until_limit": scanned,
        "returned_rows": len(results),
        "results": results,
    }


def table_endpoint(table: str, params: dict[str, list[str]]) -> dict:
    params = dict(params)
    params["table"] = [table]
    return search_rows(params)


def downloads_payload() -> dict:
    rows = []
    for name, path in sorted(DOWNLOAD_ALLOWLIST.items()):
        rows.append({
            "name": name,
            "size_bytes": path.stat().st_size,
            "url": f"/downloads/{name}",
        })
    return {"release_dir": str(RELEASE_DIR.relative_to(ROOT)), "files": rows}


def schemas_payload(name: str | None = None):
    schemas_dir = RELEASE_DIR / "schemas"
    if name:
        safe_name = Path(name).name
        path = schemas_dir / safe_name
        if not path.exists() or path.suffix != ".json":
            return {"error": "not_found", "schema": name}
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    rows = []
    for path in sorted(schemas_dir.glob("*.json")):
        rows.append({"name": path.name, "url": f"/api/v1/schemas/{path.name}", "size_bytes": path.stat().st_size})
    return {"schemas": rows}


class Handler(BaseHTTPRequestHandler):
    server_version = "AMPEvidenceAtlasPreview/0.1"

    def log_message(self, fmt, *args):
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), fmt % args))

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path, download_name: str | None = None):
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "file not found")
            return
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(path.stat().st_size))
        if download_name:
            self.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
        self.end_headers()
        with path.open("rb") as fh:
            while True:
                chunk = fh.read(1024 * 1024)
                if not chunk:
                    break
                self.wfile.write(chunk)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        try:
            if path == "/api/v1/releases":
                manifest = read_manifest()
                self.send_json({
                    "release_id": manifest.get("release_id"),
                    "release_version": manifest.get("release_version"),
                    "status": manifest.get("status"),
                    "source_freeze_summary": manifest.get("source_freeze_summary", {}),
                    "tables": manifest.get("tables", []),
                    "guardrails": manifest.get("package_policy", {}),
                })
            elif path == "/api/v1/search":
                self.send_json(search_rows(params))
            elif path.startswith("/api/v1/papers/"):
                paper_id = unquote(path.removeprefix("/api/v1/papers/"))
                self.send_json(paper_detail(paper_id))
            elif path.startswith("/api/v1/database-records/"):
                tail = path.removeprefix("/api/v1/database-records/")
                parts = tail.split("/", 1)
                if len(parts) != 2:
                    self.send_json({"error": "expected /api/v1/database-records/{database}/{source_id}"}, HTTPStatus.BAD_REQUEST)
                else:
                    self.send_json(database_record_detail(parts[0], parts[1], params))
            elif path == "/api/v1/activities":
                self.send_json(table_endpoint("activities", params))
            elif path == "/api/v1/mechanisms":
                self.send_json(table_endpoint("mechanisms", params))
            elif path == "/api/v1/conflicts":
                self.send_json(table_endpoint("conflicts", params))
            elif path == "/api/v1/downloads":
                self.send_json(downloads_payload())
            elif path.startswith("/api/v1/downloads/") or path.startswith("/downloads/"):
                name = Path(unquote(path.rsplit("/", 1)[-1])).name
                file_path = DOWNLOAD_ALLOWLIST.get(name)
                if not file_path:
                    self.send_error(HTTPStatus.NOT_FOUND, "download not allowlisted")
                else:
                    self.send_file(file_path, name)
            elif path == "/api/v1/schemas":
                self.send_json(schemas_payload())
            elif path.startswith("/api/v1/schemas/"):
                self.send_json(schemas_payload(path.rsplit("/", 1)[-1]))
            else:
                self.serve_static(path)
        except BrokenPipeError:
            return
        except Exception as exc:  # keep local preview debuggable
            self.send_json({"error": "server_error", "message": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def serve_static(self, path: str):
        if path in {"", "/"}:
            path = "/index.html"
        safe = posixpath.normpath(unquote(path)).lstrip("/")
        file_path = (STATIC_ROOT / safe).resolve()
        if not str(file_path).startswith(str(STATIC_ROOT.resolve())):
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        self.send_file(file_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8989)
    args = parser.parse_args()
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"missing release manifest: {MANIFEST_PATH}")
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"AMP Evidence Atlas preview: http://{args.host}:{args.port}")
    print(f"Release package: {RELEASE_DIR}")
    server.serve_forever()


if __name__ == "__main__":
    main()
