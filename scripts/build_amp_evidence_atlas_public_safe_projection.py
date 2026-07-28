#!/usr/bin/env python3
"""Build a rights-filtered public projection from the canonical v1.0 Portal DB.

The projection intentionally excludes copied source-database record fields. It is
suited to a public beta website/API, not a replacement for the immutable internal
v1.0 evidence package.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "portal" / "atlas.db"
DEFAULT_RELEASE = ROOT / "releases" / "amp_evidence_atlas_v1_0"
DEFAULT_OUTPUT = (
    ROOT / "public_exports" / "amp_evidence_atlas_v1_0_public_safe"
)
BENCHMARK = ROOT / "portal" / "benchmark_amp_qa.json"

PUBLIC_RELEASE_ID = "amp-evidence-atlas-v1.0-public-safe-beta"
FORBIDDEN_SOURCE_FIELDS = [
    "source_id",
    "sequence_key",
    "source_table",
    "record_name",
    "database_subject",
    "database_measure",
    "database_value",
    "database_unit",
    "primary_source_subject",
    "primary_source_value",
    "primary_source_unit",
    "database_traceability",
    "full_text",
    "claim_text",
    "source_final_path",
]


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def write_json(path: Path, value: Any, *, pretty: bool = False) -> None:
    text = (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
        if pretty
        else compact_json(value)
    )
    path.write_text(text + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def top(counter: Counter[str], limit: int) -> list[list[Any]]:
    return [[name, count] for name, count in counter.most_common(limit) if name]


def clean(value: Any) -> str:
    return str(value or "").strip()


def clipped(value: Any, limit: int) -> str:
    text = clean(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def public_target(value: Any) -> str:
    text = clean(value)
    if not text:
        return ""
    try:
        parsed = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return clipped(text, 120)
    if not isinstance(parsed, dict):
        return clipped(text, 120)
    parts = []
    for key in ("species", "strain_or_isolate", "raw_target_label"):
        candidate = clean(parsed.get(key))
        if candidate and candidate not in parts:
            parts.append(candidate)
    return clipped(" · ".join(parts), 120)


def database_schema() -> dict[str, Any]:
    return {
        "schema_version": "2.0",
        "engine": "SQLite 3",
        "public_safe": True,
        "description": (
            "Normalized, rights-filtered read model. It contains project-created "
            "indexes and aggregates only; it is not a mirror of source databases."
        ),
        "layers": [
            {
                "name": "system",
                "purpose": "Release identity, provenance checksum and scope flags.",
                "tables": ["system_release"],
            },
            {
                "name": "governance",
                "purpose": "Per-source redistribution decisions and terms links.",
                "tables": ["governance_source_rights"],
            },
            {
                "name": "catalog",
                "purpose": "Derived paper and peptide discovery indexes.",
                "tables": [
                    "catalog_paper",
                    "catalog_peptide",
                    "catalog_peptide_sequence",
                    "catalog_peptide_endpoint",
                    "catalog_peptide_target_example",
                    "catalog_peptide_evidence_tier",
                    "catalog_peptide_paper",
                ],
            },
            {
                "name": "evidence",
                "purpose": "Aggregate audit outcomes; no row-level source comparison.",
                "tables": [
                    "evidence_audit_aggregate",
                    "evidence_difference_category",
                ],
            },
            {
                "name": "evaluation",
                "purpose": "Project-authored benchmark questions and answer keys.",
                "tables": ["evaluation_benchmark_item"],
            },
            {
                "name": "api",
                "purpose": "Stable read views used by API and AI/MCP clients.",
                "views": ["api_peptide_summary", "api_paper_summary"],
            },
        ],
        "relationships": [
            {
                "from": "catalog_peptide_sequence.peptide_id",
                "to": "catalog_peptide.peptide_id",
                "cardinality": "many-to-one",
            },
            {
                "from": "catalog_peptide_endpoint.peptide_id",
                "to": "catalog_peptide.peptide_id",
                "cardinality": "many-to-one",
            },
            {
                "from": "catalog_peptide_paper.peptide_id",
                "to": "catalog_peptide.peptide_id",
                "cardinality": "many-to-one",
            },
            {
                "from": "catalog_peptide_paper.paper_id",
                "to": "catalog_paper.paper_id",
                "cardinality": "many-to-one",
            },
        ],
        "excluded": [
            "source-database raw records and copied source fields",
            "row-level database-versus-paper comparisons",
            "primary article full text and local file paths",
            "DRAMP patent AMP content",
        ],
    }


def build_public_sqlite(
    output: Path,
    release_summary: dict[str, Any],
    rights: dict[str, Any],
    papers: list[dict[str, Any]],
    peptide_rows: dict[str, dict[str, Any]],
    audit_by_database_status: dict[str, dict[str, int]],
    category_counts: Counter[str],
    benchmark: list[dict[str, Any]],
) -> Path:
    destination = output / "atlas_public_safe.db"
    temporary = output / ".atlas_public_safe.db.tmp"
    if temporary.exists():
        temporary.unlink()
    connection = sqlite3.connect(temporary)
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA user_version=200")
    connection.executescript(
        """
        CREATE TABLE system_release (
            key TEXT PRIMARY KEY,
            value_json TEXT NOT NULL
        );
        CREATE TABLE governance_source_rights (
            database_name TEXT PRIMARY KEY,
            assessment TEXT NOT NULL,
            public_hosting_decision TEXT NOT NULL,
            terms_url TEXT NOT NULL
        );
        CREATE TABLE catalog_paper (
            paper_id TEXT PRIMARY KEY,
            doi TEXT NOT NULL,
            review_status TEXT NOT NULL,
            publication_grade TEXT NOT NULL,
            audit_count INTEGER NOT NULL CHECK(audit_count >= 0),
            activity_count INTEGER NOT NULL CHECK(activity_count >= 0),
            mechanism_count INTEGER NOT NULL CHECK(mechanism_count >= 0),
            caution_count INTEGER NOT NULL CHECK(caution_count >= 0)
        );
        CREATE TABLE catalog_peptide (
            peptide_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            normalized_name TEXT NOT NULL UNIQUE,
            sequence_variant_count INTEGER NOT NULL CHECK(sequence_variant_count >= 0),
            activity_count INTEGER NOT NULL CHECK(activity_count >= 0),
            paper_count INTEGER NOT NULL CHECK(paper_count >= 0)
        );
        CREATE TABLE catalog_peptide_sequence (
            peptide_id INTEGER NOT NULL REFERENCES catalog_peptide(peptide_id)
                ON DELETE CASCADE,
            sequence TEXT NOT NULL,
            PRIMARY KEY (peptide_id, sequence)
        );
        CREATE TABLE catalog_peptide_endpoint (
            peptide_id INTEGER NOT NULL REFERENCES catalog_peptide(peptide_id)
                ON DELETE CASCADE,
            endpoint TEXT NOT NULL,
            observation_count INTEGER NOT NULL CHECK(observation_count > 0),
            PRIMARY KEY (peptide_id, endpoint)
        );
        CREATE TABLE catalog_peptide_target_example (
            peptide_id INTEGER NOT NULL REFERENCES catalog_peptide(peptide_id)
                ON DELETE CASCADE,
            target_label TEXT NOT NULL,
            observation_count INTEGER NOT NULL CHECK(observation_count > 0),
            PRIMARY KEY (peptide_id, target_label)
        );
        CREATE TABLE catalog_peptide_evidence_tier (
            peptide_id INTEGER NOT NULL REFERENCES catalog_peptide(peptide_id)
                ON DELETE CASCADE,
            evidence_tier TEXT NOT NULL,
            observation_count INTEGER NOT NULL CHECK(observation_count > 0),
            PRIMARY KEY (peptide_id, evidence_tier)
        );
        CREATE TABLE catalog_peptide_paper (
            peptide_id INTEGER NOT NULL REFERENCES catalog_peptide(peptide_id)
                ON DELETE CASCADE,
            paper_id TEXT NOT NULL REFERENCES catalog_paper(paper_id) ON DELETE CASCADE,
            PRIMARY KEY (peptide_id, paper_id)
        );
        CREATE TABLE evidence_audit_aggregate (
            database_name TEXT NOT NULL,
            status TEXT NOT NULL,
            record_count INTEGER NOT NULL CHECK(record_count >= 0),
            PRIMARY KEY (database_name, status)
        );
        CREATE TABLE evidence_difference_category (
            category TEXT PRIMARY KEY,
            record_count INTEGER NOT NULL CHECK(record_count >= 0)
        );
        CREATE TABLE evaluation_benchmark_item (
            item_id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            source_ref TEXT NOT NULL
        );
        CREATE INDEX idx_catalog_peptide_name
            ON catalog_peptide(normalized_name);
        CREATE INDEX idx_catalog_peptide_activity
            ON catalog_peptide(activity_count DESC, normalized_name);
        CREATE INDEX idx_catalog_sequence
            ON catalog_peptide_sequence(sequence);
        CREATE INDEX idx_catalog_paper_doi
            ON catalog_paper(doi);
        CREATE INDEX idx_catalog_paper_activity
            ON catalog_paper(activity_count DESC, paper_id);
        CREATE INDEX idx_catalog_peptide_paper_paper
            ON catalog_peptide_paper(paper_id, peptide_id);
        CREATE INDEX idx_benchmark_category
            ON evaluation_benchmark_item(category, item_id);
        CREATE VIEW api_peptide_summary AS
            SELECT peptide_id, name, sequence_variant_count, activity_count, paper_count
            FROM catalog_peptide;
        CREATE VIEW api_paper_summary AS
            SELECT paper_id, doi, review_status, publication_grade, audit_count,
                   activity_count, mechanism_count, caution_count
            FROM catalog_paper;
        """
    )
    connection.executemany(
        "INSERT INTO system_release(key,value_json) VALUES (?,?)",
        [
            (key, compact_json(value))
            for key, value in sorted(release_summary.items())
        ],
    )
    connection.executemany(
        """INSERT INTO governance_source_rights
           (database_name,assessment,public_hosting_decision,terms_url)
           VALUES (?,?,?,?)""",
        [
            (
                database_name,
                clean(decision["assessment"]),
                clean(decision["public_hosting_decision"]),
                clean(decision["terms_url"]),
            )
            for database_name, decision in sorted(
                rights["database_decisions"].items()
            )
        ],
    )
    connection.executemany(
        """INSERT INTO catalog_paper
           (paper_id,doi,review_status,publication_grade,audit_count,activity_count,
            mechanism_count,caution_count)
           VALUES (:id,:doi,:review_status,:publication_grade,:audit_count,
                   :activity_count,:mechanism_count,:caution_count)""",
        papers,
    )
    paper_ids = {paper["id"] for paper in papers}
    for peptide_id, key in enumerate(sorted(peptide_rows), start=1):
        item = peptide_rows[key]
        connection.execute(
            """INSERT INTO catalog_peptide
               (peptide_id,name,normalized_name,sequence_variant_count,
                activity_count,paper_count) VALUES (?,?,?,?,?,?)""",
            (
                peptide_id,
                item["name"],
                key,
                len(item["sequences"]),
                item["activity_count"],
                len(item["papers"]),
            ),
        )
        connection.executemany(
            "INSERT INTO catalog_peptide_sequence(peptide_id,sequence) VALUES (?,?)",
            [(peptide_id, sequence) for sequence in sorted(item["sequences"])],
        )
        connection.executemany(
            """INSERT INTO catalog_peptide_endpoint
               (peptide_id,endpoint,observation_count) VALUES (?,?,?)""",
            [
                (peptide_id, endpoint, count)
                for endpoint, count in sorted(item["endpoints"].items())
                if endpoint
            ],
        )
        connection.executemany(
            """INSERT INTO catalog_peptide_target_example
               (peptide_id,target_label,observation_count) VALUES (?,?,?)""",
            [
                (peptide_id, target, count)
                for target, count in item["targets"].most_common(20)
                if target
            ],
        )
        connection.executemany(
            """INSERT INTO catalog_peptide_evidence_tier
               (peptide_id,evidence_tier,observation_count) VALUES (?,?,?)""",
            [
                (peptide_id, tier, count)
                for tier, count in sorted(item["evidence_tiers"].items())
                if tier
            ],
        )
        connection.executemany(
            "INSERT INTO catalog_peptide_paper(peptide_id,paper_id) VALUES (?,?)",
            [
                (peptide_id, paper_id)
                for paper_id in sorted(item["papers"])
                if paper_id in paper_ids
            ],
        )
    connection.executemany(
        """INSERT INTO evidence_audit_aggregate
           (database_name,status,record_count) VALUES (?,?,?)""",
        [
            (database_name, status, count)
            for database_name, statuses in sorted(
                audit_by_database_status.items()
            )
            for status, count in sorted(statuses.items())
        ],
    )
    connection.executemany(
        """INSERT INTO evidence_difference_category(category,record_count)
           VALUES (?,?)""",
        sorted(category_counts.items()),
    )
    connection.executemany(
        """INSERT INTO evaluation_benchmark_item
           (item_id,category,question,answer,source_ref)
           VALUES (:id,:category,:question,:answer,:source_ref)""",
        benchmark,
    )
    connection.commit()
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_key_failures = connection.execute("PRAGMA foreign_key_check").fetchall()
    if integrity != "ok" or foreign_key_failures:
        raise RuntimeError(
            f"public SQLite validation failed: integrity={integrity!r}, "
            f"foreign_keys={len(foreign_key_failures)}"
        )
    connection.execute("VACUUM")
    connection.close()
    temporary.replace(destination)
    return destination


def build(db_path: Path, release: Path, output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    metadata = dict(connection.execute("SELECT k,v FROM metadata"))
    stats = {row["k"]: int(row["v"]) for row in connection.execute("SELECT k,v FROM stats")}
    if metadata.get("release_id") != "amp-evidence-atlas-v1.0":
        raise RuntimeError(f"unexpected Portal release: {metadata.get('release_id')}")
    if metadata.get("experimental_increments_included") != "false":
        raise RuntimeError("public-safe projection refuses experimental increments")

    papers = [
        {
            "id": row["paper_id"],
            "doi": clean(row["doi"]),
            "review_status": clean(row["review_status"]),
            "publication_grade": clean(row["publication_grade"]),
            "audit_count": int(row["n_audit"]),
            "activity_count": int(row["n_activity"]),
            "mechanism_count": int(row["n_mechanism"]),
            "caution_count": int(row["caution_count"]),
        }
        for row in connection.execute(
            """SELECT paper_id,doi,review_status,publication_grade,n_audit,n_activity,
                      n_mechanism,caution_count FROM papers ORDER BY paper_id"""
        )
    ]

    peptide_rows: dict[str, dict[str, Any]] = {}
    for row in connection.execute(
        """SELECT paper_id,peptide,sequence,endpoint,target,evidence_tier
             FROM activity WHERE peptide<>'' ORDER BY lower(peptide),paper_id"""
    ):
        key = clean(row["peptide"]).casefold()
        item = peptide_rows.get(key)
        if item is None:
            item = {
                "name": clipped(row["peptide"], 160),
                "sequences": set(),
                "papers": set(),
                "activity_count": 0,
                "endpoints": Counter(),
                "targets": Counter(),
                "evidence_tiers": Counter(),
            }
            peptide_rows[key] = item
        item["activity_count"] += 1
        if clean(row["sequence"]):
            item["sequences"].add(clipped(row["sequence"], 160))
        item["papers"].add(clean(row["paper_id"]))
        item["endpoints"][clipped(row["endpoint"], 80)] += 1
        item["targets"][public_target(row["target"])] += 1
        item["evidence_tiers"][clean(row["evidence_tier"])] += 1

    peptides = []
    for key in sorted(peptide_rows):
        item = peptide_rows[key]
        papers_sorted = sorted(item["papers"])
        peptides.append(
            {
                "name": item["name"],
                "sequences": sorted(item["sequences"])[:3],
                "sequence_variant_count": len(item["sequences"]),
                "activity_count": item["activity_count"],
                "paper_count": len(item["papers"]),
                "paper_examples": papers_sorted[:4],
                "endpoints": top(item["endpoints"], 6),
                "target_examples": [name for name, _ in top(item["targets"], 3)],
                "evidence_tiers": top(item["evidence_tiers"], 3),
            }
        )

    audit_by_database_status: dict[str, dict[str, int]] = defaultdict(dict)
    for row in connection.execute(
        "SELECT database,status,COUNT(*) c FROM audit GROUP BY database,status"
    ):
        audit_by_database_status[clean(row["database"])][clean(row["status"])] = int(
            row["c"]
        )
    category_counts: Counter[str] = Counter()
    for row in connection.execute("SELECT difference_categories FROM audit"):
        for category in clean(row["difference_categories"]).split(";"):
            if category:
                category_counts[category] += 1

    benchmark_source = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    benchmark = [
        {
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "answer": item["ground_truth"],
            "source_ref": item["source_ref"],
        }
        for item in benchmark_source["items"]
    ]

    license_rows = read_tsv(release / "LICENSES.tsv")
    rights = {
        "policy": "rights_filtered_public_beta",
        "legal_advice": False,
        "full_internal_v1_payload_publicly_redistributed": False,
        "source_database_raw_fields_exposed": False,
        "excluded_field_names": FORBIDDEN_SOURCE_FIELDS,
        "public_components": [
            "project-created aggregate statistics",
            "paper identifiers and project review/count metadata",
            "derived peptide/sequence activity-count index",
            "derived audit status/category aggregates",
            "40 project-authored evidence benchmark examples",
        ],
        "not_public_components": [
            "bulk source-database record mirrors",
            "source-database record names, values, units and source IDs",
            "primary article full text, PDFs, tables and figures",
            "bulk row-level database audit comparisons",
            "DRAMP patent AMP content",
        ],
        "database_decisions": {
            row["database"]: {
                "assessment": row["redistribution_assessment"],
                "public_hosting_decision": row["public_hosting_decision"],
                "terms_url": row["official_terms_url"],
            }
            for row in license_rows
        },
        "permission_follow_up_still_required": [
            "APD6",
            "CAMP",
            "DBAASP",
            "dbAMP",
            "DRAMP patent AMPs",
        ],
    }
    release_manifest = json.loads(
        (release / "release_manifest.json").read_text(encoding="utf-8")
    )
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    release_summary = {
        "release_id": PUBLIC_RELEASE_ID,
        "source_release_id": release_manifest["release_id"],
        "source_payload_checksum_manifest_sha256": release_manifest[
            "payload_checksum_manifest_sha256"
        ],
        "generated_at": generated_at,
        "status": "public_safe_beta_projection",
        "scope": {
            "papers": len(papers),
            "peptides": len(peptides),
            "benchmark_examples": len(benchmark),
            "activity_observations_aggregated": stats["activity"],
            "audit_records_aggregated": stats["audit"],
            "mechanism_claims_aggregated": stats["mechanism"],
            "row_level_audit_records_exposed": 0,
            "source_database_raw_records_exposed": 0,
        },
        "limitations": [
            "This public beta is a rights-filtered projection, not the unrestricted full v1.0 evidence package.",
            "Stratified human validation remains incomplete.",
            "Audit conflicts are curation statuses and are not automatically human-confirmed database errors.",
            "Permission follow-up remains open for four source databases and all patent-origin content.",
        ],
    }
    schema = database_schema()
    data = {
        "release": release_summary,
        "rights": rights,
        "stats": {
            "papers": len(papers),
            "peptides": len(peptides),
            "activity_observations_aggregated": stats["activity"],
            "audit_records_aggregated": stats["audit"],
            "source_conflicts_aggregated": stats["conflicts_audit"],
            "mechanism_claims_aggregated": stats["mechanism"],
        },
        "papers": papers,
        "peptides": peptides,
        "audit_summary": {
            "by_database_status": dict(sorted(audit_by_database_status.items())),
            "difference_categories": top(category_counts, 30),
        },
        "benchmark": benchmark,
        "database_schema": schema,
    }
    build_public_sqlite(
        output,
        release_summary,
        rights,
        papers,
        peptide_rows,
        audit_by_database_status,
        category_counts,
        benchmark,
    )
    connection.close()

    files = {
        "public_safe_data.json": data,
        "release.json": release_summary,
        "rights.json": rights,
        "database_schema.json": schema,
    }
    for name, value in files.items():
        write_json(output / name, value, pretty=name != "public_safe_data.json")
    manifest_files = []
    for name in sorted([*files, "atlas_public_safe.db"]):
        path = output / name
        manifest_files.append(
            {"path": name, "sha256": sha256(path), "size_bytes": path.stat().st_size}
        )
    manifest = {
        "schema": "amp_evidence_atlas_public_safe_projection_manifest_v2",
        "release_id": PUBLIC_RELEASE_ID,
        "generated_at": generated_at,
        "source_release_id": release_manifest["release_id"],
        "source_payload_checksum_manifest_sha256": release_manifest[
            "payload_checksum_manifest_sha256"
        ],
        "files": manifest_files,
        "forbidden_source_fields": FORBIDDEN_SOURCE_FIELDS,
        "field_filter_enforced": True,
        "public_release_ready": True,
        "public_scope_is_limited": True,
    }
    write_json(output / "manifest.json", manifest, pretty=True)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--release", type=Path, default=DEFAULT_RELEASE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = build(args.db.resolve(), args.release.resolve(), args.output.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
