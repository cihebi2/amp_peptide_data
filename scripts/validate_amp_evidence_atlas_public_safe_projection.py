#!/usr/bin/env python3
"""Validate the rights-filtered public beta projection before deployment."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public_exports" / "amp_evidence_atlas_v1_0_public_safe"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.add(key)
            found.update(keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(keys(child))
    return found


def strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def main() -> None:
    manifest = json.loads((OUTPUT / "manifest.json").read_text(encoding="utf-8"))
    data_path = OUTPUT / "public_safe_data.json"
    database_path = OUTPUT / "atlas_public_safe.db"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    failures = []
    checks = {}

    file_checks = []
    for row in manifest["files"]:
        path = OUTPUT / row["path"]
        ok = (
            path.is_file()
            and path.stat().st_size == row["size_bytes"]
            and sha256(path) == row["sha256"]
        )
        file_checks.append(ok)
    checks["manifest_file_hashes"] = all(file_checks)

    forbidden = set(manifest["forbidden_source_fields"])
    exposed_forbidden = sorted(keys(data) & forbidden)
    checks["forbidden_source_fields_absent"] = not exposed_forbidden
    if exposed_forbidden:
        failures.append({"forbidden_source_fields": exposed_forbidden})

    local_paths = sorted(
        {
            text
            for text in strings(data)
            if text.startswith(("/mnt/", "/home/", "papers/", "paper_packets/"))
        }
    )
    checks["local_paths_absent"] = not local_paths
    if local_paths:
        failures.append({"local_paths": local_paths[:10]})

    scope = data["release"]["scope"]
    checks["scope_counts"] = (
        len(data["papers"]) == scope["papers"] == 1374
        and len(data["peptides"]) == scope["peptides"] == 9263
        and len(data["benchmark"]) == scope["benchmark_examples"] == 40
        and scope["row_level_audit_records_exposed"] == 0
        and scope["source_database_raw_records_exposed"] == 0
    )
    checks["rights_gate"] = (
        data["rights"]["source_database_raw_fields_exposed"] is False
        and data["rights"]["full_internal_v1_payload_publicly_redistributed"] is False
        and data["release"]["status"] == "public_safe_beta_projection"
        and manifest["public_scope_is_limited"] is True
    )
    checks["worker_bundle_size_budget"] = data_path.stat().st_size < 5 * 1024 * 1024

    connection = sqlite3.connect(f"file:{database_path}?mode=ro", uri=True)
    database_objects = {
        (row[0], row[1])
        for row in connection.execute(
            """SELECT type,name FROM sqlite_master
               WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'"""
        )
    }
    expected_tables = {
        "system_release",
        "governance_source_rights",
        "catalog_paper",
        "catalog_peptide",
        "catalog_peptide_sequence",
        "catalog_peptide_endpoint",
        "catalog_peptide_target_example",
        "catalog_peptide_evidence_tier",
        "catalog_peptide_paper",
        "evidence_audit_aggregate",
        "evidence_difference_category",
        "evaluation_benchmark_item",
    }
    expected_views = {"api_peptide_summary", "api_paper_summary"}
    checks["database_layer_hierarchy"] = (
        {name for kind, name in database_objects if kind == "table"}
        == expected_tables
        and {name for kind, name in database_objects if kind == "view"}
        == expected_views
        and [layer["name"] for layer in data["database_schema"]["layers"]]
        == ["system", "governance", "catalog", "evidence", "evaluation", "api"]
    )
    database_columns = {
        row[1]
        for table in expected_tables
        for row in connection.execute(f'PRAGMA table_info("{table}")')
    }
    exposed_database_forbidden = sorted(database_columns & forbidden)
    checks["database_forbidden_columns_absent"] = not exposed_database_forbidden
    if exposed_database_forbidden:
        failures.append({"forbidden_database_columns": exposed_database_forbidden})
    checks["database_integrity"] = (
        connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        and not connection.execute("PRAGMA foreign_key_check").fetchall()
    )
    checks["database_scope_counts"] = (
        connection.execute("SELECT COUNT(*) FROM catalog_paper").fetchone()[0]
        == scope["papers"]
        and connection.execute("SELECT COUNT(*) FROM catalog_peptide").fetchone()[0]
        == scope["peptides"]
        and connection.execute(
            "SELECT COUNT(*) FROM evaluation_benchmark_item"
        ).fetchone()[0]
        == scope["benchmark_examples"]
        and connection.execute(
            "SELECT COALESCE(SUM(record_count),0) FROM evidence_audit_aggregate"
        ).fetchone()[0]
        == scope["audit_records_aggregated"]
    )
    checks["database_public_read_model_only"] = (
        not any("raw" in name or "row_level" in name for _, name in database_objects)
        and data["database_schema"]["public_safe"] is True
    )
    connection.close()

    for name, passed in checks.items():
        if not passed:
            failures.append({"check": name})
    result = {
        "release_id": manifest["release_id"],
        "passed": not failures,
        "check_count": len(checks),
        "failure_count": len(failures),
        "checks": checks,
        "failures": failures,
        "data_size_bytes": data_path.stat().st_size,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
