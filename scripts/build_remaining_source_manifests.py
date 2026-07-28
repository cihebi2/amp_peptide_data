#!/usr/bin/env python3
"""Build recovery manifests for unreviewed landed source papers.

This script mirrors the strict-fresh exclusion policy from the Batch 4-Team
runbook, then separates the remaining source pool into:

- strict_fresh: metadata + primary xml/*.xml + primary pdf/*.pdf
- weak_source: metadata plus some XML/PDF, but not both primary XML and PDF
- metadata_only: metadata with no XML/PDF surface yet

It intentionally does not launch paper review workers. The output is a material
recovery handoff for staging primary XML/PDF or writing explicit material-gap
packets.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_POOL = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers")
DEFAULT_OUT_DIR = Path("reports/source_recovery")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:  # noqa: BLE001 - report parse failures, do not abort inventory
        return {"_parse_error": str(exc), "_path": str(path)}
    return data if isinstance(data, dict) else {"_not_object": True, "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "paper_id",
        "category",
        "recommended_action",
        "source_path",
        "title",
        "year",
        "journal",
        "doi",
        "pmid",
        "pmcid",
        "primary_xml_count",
        "primary_pdf_count",
        "any_xml_count",
        "any_pdf_count",
        "package_file_count",
        "supplementary_file_count",
        "availability_level",
        "availability_reasons",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            metadata = row.get("metadata") or {}
            asset_counts = row.get("asset_counts") or {}
            identifiers = row.get("identifiers") or {}
            writer.writerow(
                {
                    "paper_id": row.get("paper_id"),
                    "category": row.get("category"),
                    "recommended_action": row.get("recommended_action"),
                    "source_path": row.get("source_path"),
                    "title": metadata.get("title"),
                    "year": metadata.get("year"),
                    "journal": metadata.get("journal"),
                    "doi": identifiers.get("doi"),
                    "pmid": identifiers.get("pmid"),
                    "pmcid": identifiers.get("pmcid"),
                    "primary_xml_count": asset_counts.get("primary_xml_count"),
                    "primary_pdf_count": asset_counts.get("primary_pdf_count"),
                    "any_xml_count": asset_counts.get("any_xml_count"),
                    "any_pdf_count": asset_counts.get("any_pdf_count"),
                    "package_file_count": asset_counts.get("package_file_count"),
                    "supplementary_file_count": asset_counts.get("supplementary_file_count"),
                    "availability_level": metadata.get("availability_level"),
                    "availability_reasons": ";".join(str(x) for x in metadata.get("availability_reasons") or []),
                }
            )


def safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def asset_counts(path: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    # Prefer metadata asset counts to avoid expensive recursive scans over the
    # mounted source pool. Direct primary directory checks stay cheap and are
    # the strict queue gate.
    raw_counts = metadata.get("asset_counts") if isinstance(metadata.get("asset_counts"), dict) else {}
    # Keep the strict queue gate identical to the current runbook:
    # primary xml/*.xml plus primary pdf/*.pdf. NXML is still counted under
    # any_xml_count and routed through source recovery/packetization first.
    primary_xml_count = sum(1 for item in (path / "xml").glob("*") if item.is_file() and item.suffix.lower() == ".xml")
    primary_pdf_count = sum(1 for item in (path / "pdf").glob("*") if item.is_file() and item.suffix.lower() == ".pdf")
    supplementary_pdf_count = sum(1 for item in (path / "supplementary").glob("*") if item.is_file() and item.suffix.lower() == ".pdf")
    any_xml_count = safe_int(raw_counts.get("xml_files")) or primary_xml_count
    any_pdf_count = safe_int(raw_counts.get("pdf_files")) or primary_pdf_count or supplementary_pdf_count
    package_file_count = safe_int(raw_counts.get("package_files"))
    supplementary_file_count = safe_int(raw_counts.get("supplementary_files"))
    return {
        "metadata_present": (path / "metadata.json").exists(),
        "primary_xml_count": primary_xml_count,
        "primary_pdf_count": primary_pdf_count,
        "any_xml_count": any_xml_count,
        "any_pdf_count": any_pdf_count,
        "supplementary_pdf_count": supplementary_pdf_count,
        "package_file_count": package_file_count,
        "supplementary_file_count": supplementary_file_count,
        "all_file_count": any_xml_count + any_pdf_count + package_file_count + supplementary_file_count,
    }


def identifiers(metadata: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, canonical_key in (("doi", "canonical_doi"), ("pmid", "canonical_pmid"), ("pmcid", "canonical_pmcid")):
        value = metadata.get(canonical_key) or metadata.get(key)
        if value:
            out[key] = str(value)
    if metadata.get("title"):
        out["title"] = str(metadata["title"])
    return out


def categorize(counts: dict[str, Any]) -> str:
    has_meta = bool(counts["metadata_present"])
    has_primary_xml = counts["primary_xml_count"] > 0
    has_primary_pdf = counts["primary_pdf_count"] > 0
    if has_meta and has_primary_xml and has_primary_pdf:
        return "strict_fresh"
    if has_meta and (counts["any_xml_count"] > 0 or counts["any_pdf_count"] > 0):
        return "weak_source"
    if has_meta:
        return "metadata_only"
    return "missing_metadata"


def recommended_action(category: str, counts: dict[str, Any]) -> str:
    if category == "strict_fresh":
        return "eligible_for_review_queue_after_overlap_check"
    if category == "weak_source":
        missing = []
        if counts["primary_xml_count"] == 0:
            missing.append("primary_xml")
        if counts["primary_pdf_count"] == 0:
            missing.append("primary_pdf")
        return "recover_or_stage_" + "_and_".join(missing) + "_then_build_material_packet"
    if category == "metadata_only":
        if counts["supplementary_file_count"] or counts["package_file_count"]:
            return "attempt_external_primary_fulltext_then_inventory_existing_supplementary_assets"
        return "attempt_external_primary_fulltext_pdf_xml_before_review"
    return "repair_metadata_before_any_queue"


def collect_exclusion_sets(repo: Path, source_ids: set[str]) -> dict[str, set[str]]:
    sets: dict[str, set[str]] = {}
    for key, rel in (
        ("paper_packets_dirs", "paper_packets"),
        ("papers_dirs", "papers"),
        ("rework_context_dirs", "rework_context"),
    ):
        base = repo / rel
        sets[key] = {path.name for path in base.iterdir() if path.is_dir()} if base.exists() else set()

    workflow_root = repo / ".miaobi-paper-review" / "workflows"
    sets["workflow_ids"] = {path.name for path in workflow_root.iterdir() if path.is_dir()} if workflow_root.exists() else set()

    report_ids: set[str] = set()
    reports = repo / "reports"
    if reports.exists():
        for path in reports.glob("*.json"):
            name = path.name
            if name.startswith(("doi__", "pmid__")):
                paper_id = name.split(".complete_message_test_report.json")[0]
                paper_id = paper_id.split(".true_rework_queue_attempt_")[0]
                paper_id = paper_id.split(".semantic_gate.json")[0]
                paper_id = paper_id.split(".publication_quality.json")[0]
                if paper_id.startswith(("doi__", "pmid__")):
                    report_ids.add(paper_id)
        # The aggregate is small and already deduplicated; avoid reading every
        # lane status JSON because those files are numerous and can be large.
        aggregate = read_json(reports / "all_reviewed_papers_aggregate_latest.json")
        if isinstance(aggregate.get("papers"), list):
            report_ids.update(
                str(item.get("paper_id"))
                for item in aggregate["papers"]
                if isinstance(item, dict) and item.get("paper_id")
            )
        for path in reports.glob("true_rework_queue_manifest_*.json"):
            data = read_json(path)
            if isinstance(data.get("paper_ids"), list):
                report_ids.update(str(item) for item in data["paper_ids"] if isinstance(item, str))
            if isinstance(data.get("papers"), list):
                for item in data["papers"]:
                    if isinstance(item, str):
                        report_ids.add(item)
                    elif isinstance(item, dict) and item.get("paper_id"):
                        report_ids.add(str(item["paper_id"]))
        accepted_audit = reports / "accepted_sample_audit"
        if accepted_audit.exists():
            for path in accepted_audit.glob("*.json"):
                data = read_json(path)
                for key in ("items", "results"):
                    if isinstance(data.get(key), list):
                        report_ids.update(
                            str(item.get("paper_id"))
                            for item in data[key]
                            if isinstance(item, dict) and item.get("paper_id")
                        )
    sets["json_reports_or_manifests"] = report_ids

    # Keep only source-pool IDs in the diagnostic counts, while returning full
    # sets so future source additions still get filtered by existing artifacts.
    sets["_source_ids"] = source_ids
    return sets


def row_for_source(path: Path) -> dict[str, Any]:
    metadata = read_json(path / "metadata.json")
    counts = asset_counts(path, metadata)
    category = categorize(counts)
    return {
        "paper_id": path.name,
        "source_path": str(path),
        "category": category,
        "recommended_action": recommended_action(category, counts),
        "asset_counts": counts,
        "identifiers": identifiers(metadata),
        "metadata": {
            "title": metadata.get("title"),
            "year": metadata.get("year"),
            "journal": metadata.get("journal"),
            "first_author": metadata.get("first_author"),
            "availability_level": metadata.get("availability_level"),
            "availability_reasons": metadata.get("availability_reasons") or [],
            "source_databases": metadata.get("source_databases") or [],
            "metadata_parse_error": metadata.get("_parse_error"),
        },
    }


def manifest_payload(
    *,
    generated_at: str,
    source_pool: Path,
    category: str,
    rows: list[dict[str, Any]],
    selection_policy: str,
) -> dict[str, Any]:
    return {
        "generated_at": generated_at,
        "source_pool": str(source_pool),
        "category": category,
        "paper_count": len(rows),
        "paper_ids": [row["paper_id"] for row in rows],
        "items": rows,
        "selection_policy": selection_policy,
        "completion_claim": "material_recovery_manifest_only_not_review_completion",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pool", type=Path, default=DEFAULT_SOURCE_POOL)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--stamp", default=None)
    parser.add_argument(
        "--requested",
        type=int,
        default=None,
        help="Optional verification guard: fail if the unreviewed source count differs from this value.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = args.repo_root.resolve()
    source_pool = args.source_pool
    stamp = args.stamp or safe_stamp()
    generated_at = utc_now()
    out_dir = args.out_dir

    source_dirs = sorted((path for path in source_pool.iterdir() if path.is_dir()), key=lambda path: path.name)
    source_ids = {path.name for path in source_dirs}
    exclusions = collect_exclusion_sets(repo, source_ids)
    excluded = set().union(*(value for key, value in exclusions.items() if not key.startswith("_")))
    rows_all = [row_for_source(path) for path in source_dirs]
    unreviewed = [row for row in rows_all if row["paper_id"] not in excluded]

    by_category: dict[str, list[dict[str, Any]]] = {
        "strict_fresh": [row for row in unreviewed if row["category"] == "strict_fresh"],
        "weak_source": [row for row in unreviewed if row["category"] == "weak_source"],
        "metadata_only": [row for row in unreviewed if row["category"] == "metadata_only"],
        "missing_metadata": [row for row in unreviewed if row["category"] == "missing_metadata"],
    }
    category_counts = {key: len(value) for key, value in by_category.items()}
    all_category_counts = dict(Counter(row["category"] for row in rows_all))
    source_exclusion_counts = {
        key: len(value & source_ids)
        for key, value in exclusions.items()
        if not key.startswith("_")
    }
    strict_ids = {row["paper_id"] for row in rows_all if row["category"] == "strict_fresh"}
    strict_exclusion_counts = {
        key: len(value & strict_ids)
        for key, value in exclusions.items()
        if not key.startswith("_")
    }

    selection_policy = (
        "unreviewed means absent from local papers/, paper_packets/, rework_context/, "
        ".miaobi-paper-review/workflows, prior queue manifests/reports, and accepted sample audits"
    )
    summary = {
        "generated_at": generated_at,
        "source_pool": str(source_pool),
        "source_dirs_total": len(source_dirs),
        "source_metadata_count": sum(1 for row in rows_all if row["asset_counts"]["metadata_present"]),
        "all_source_category_counts": all_category_counts,
        "excluded_source_ids_reviewed_or_attempted": len(source_ids & excluded),
        "exclusion_sources_on_source_all": source_exclusion_counts,
        "exclusion_sources_on_strict_eligible": strict_exclusion_counts,
        "all_unreviewed_source_ids": len(unreviewed),
        "remaining_category_counts": category_counts,
        "strict_fresh_examples": [row["paper_id"] for row in by_category["strict_fresh"][:20]],
        "weak_source_examples": [row["paper_id"] for row in by_category["weak_source"][:20]],
        "metadata_only_examples": [row["paper_id"] for row in by_category["metadata_only"][:20]],
        "missing_metadata_examples": [row["paper_id"] for row in by_category["missing_metadata"][:20]],
        "selection_policy": selection_policy,
        "completion_claim": "remaining_source_inventory_not_review_completion",
        "requested_unreviewed_count": args.requested,
        "requested_unreviewed_count_matches": args.requested is None or len(unreviewed) == args.requested,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    all_manifest = manifest_payload(
        generated_at=generated_at,
        source_pool=source_pool,
        category="all_unreviewed",
        rows=unreviewed,
        selection_policy=selection_policy,
    )
    all_manifest["summary"] = summary

    writes = {
        f"remaining_unreviewed_sources_{stamp}.json": all_manifest,
        "remaining_unreviewed_sources_latest.json": all_manifest,
        f"strict_fresh_manifest_{stamp}.json": manifest_payload(
            generated_at=generated_at,
            source_pool=source_pool,
            category="strict_fresh",
            rows=by_category["strict_fresh"],
            selection_policy=selection_policy,
        ),
        "strict_fresh_manifest_latest.json": manifest_payload(
            generated_at=generated_at,
            source_pool=source_pool,
            category="strict_fresh",
            rows=by_category["strict_fresh"],
            selection_policy=selection_policy,
        ),
        f"weak_source_manifest_{stamp}.json": manifest_payload(
            generated_at=generated_at,
            source_pool=source_pool,
            category="weak_source",
            rows=by_category["weak_source"],
            selection_policy=selection_policy,
        ),
        "weak_source_manifest_latest.json": manifest_payload(
            generated_at=generated_at,
            source_pool=source_pool,
            category="weak_source",
            rows=by_category["weak_source"],
            selection_policy=selection_policy,
        ),
        f"metadata_only_manifest_{stamp}.json": manifest_payload(
            generated_at=generated_at,
            source_pool=source_pool,
            category="metadata_only",
            rows=by_category["metadata_only"],
            selection_policy=selection_policy,
        ),
        "metadata_only_manifest_latest.json": manifest_payload(
            generated_at=generated_at,
            source_pool=source_pool,
            category="metadata_only",
            rows=by_category["metadata_only"],
            selection_policy=selection_policy,
        ),
    }
    for name, payload in writes.items():
        write_json(out_dir / name, payload)

    write_csv(out_dir / f"remaining_unreviewed_sources_{stamp}.csv", unreviewed)
    write_csv(out_dir / "remaining_unreviewed_sources_latest.csv", unreviewed)
    write_csv(out_dir / f"weak_source_manifest_{stamp}.csv", by_category["weak_source"])
    write_csv(out_dir / "weak_source_manifest_latest.csv", by_category["weak_source"])
    write_csv(out_dir / f"metadata_only_manifest_{stamp}.csv", by_category["metadata_only"])
    write_csv(out_dir / "metadata_only_manifest_latest.csv", by_category["metadata_only"])

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if args.requested is not None and len(unreviewed) != args.requested:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
