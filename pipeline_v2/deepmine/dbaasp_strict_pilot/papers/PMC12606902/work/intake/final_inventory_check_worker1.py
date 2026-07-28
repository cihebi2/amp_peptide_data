#!/usr/bin/env python3
"""Worker-1 final mirror/status inventory for PMC12606902.

The check is intentionally content-safe: it records file names, sizes, hashes,
status fields, and counts, but never emits source text or biomedical passages.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "PMC12606902"
ROOT = Path("pipeline_v2/deepmine/dbaasp_strict_pilot")
EXPECTED_FINAL_FILES = [
    "activity_toxicity_evidence.json",
    "database_record_verification.json",
    "materials_manifest.json",
    "mechanism_evidence.json",
    "mechanism_ontology_record.json",
    "review_report.json",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_entry(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256(path) if path.exists() else None,
    }


def collect_status_paths(value: Any, path: str = "$") -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            key_lower = key.lower()
            if isinstance(child, (str, bool, int, float)) or child is None:
                if (
                    key_lower in {
                        "status",
                        "analysis_status",
                        "analysis_queue_status",
                        "material_queue_status",
                        "review_status",
                        "publication_grade",
                        "validator_contract_passed",
                        "worker6_review_status",
                        "worker6_publication_grade",
                    }
                    or key_lower.endswith("_status")
                    or key_lower.endswith("_grade")
                ):
                    hits.append({"path": child_path, "field": key, "value": child})
            else:
                hits.extend(collect_status_paths(child, child_path))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            hits.extend(collect_status_paths(child, f"{path}[{idx}]"))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", required=True)
    args = parser.parse_args()

    root = ROOT
    paper_root = root / "papers" / PAPER_ID
    packet_root = root / "packets" / PAPER_ID
    paper_final = paper_root / "final"
    packet_final = packet_root / "final"
    status_latest_path = root / "reports" / f"{PAPER_ID}_status_latest.json"

    paper_files = sorted(p.name for p in paper_final.glob("*.json"))
    packet_files = sorted(p.name for p in packet_final.glob("*.json"))

    mirrored_artifacts: dict[str, Any] = {}
    for name in EXPECTED_FINAL_FILES:
        paper_path = paper_final / name
        packet_path = packet_final / name
        mirrored_artifacts[name] = {
            "paper": file_entry(paper_path),
            "packet": file_entry(packet_path),
            "byte_equal": paper_path.exists()
            and packet_path.exists()
            and sha256(paper_path) == sha256(packet_path),
        }

    final_status_hits: dict[str, list[dict[str, Any]]] = {}
    current_analysis_queued_hits: list[dict[str, str]] = []
    historical_analysis_queued_hits: list[dict[str, str]] = []
    for base_label, base in [("paper", paper_final), ("packet", packet_final)]:
        for json_path in sorted(base.glob("*.json")):
            rel = f"{base_label}:{json_path.name}"
            try:
                hits = collect_status_paths(read_json(json_path))
            except Exception as exc:  # pragma: no cover - diagnostic path
                hits = [{"path": "$", "field": "json_read_error", "value": type(exc).__name__}]
            final_status_hits[rel] = hits
            for hit in hits:
                if hit.get("value") == "analysis_queued":
                    item = {"artifact": rel, "path": str(hit.get("path"))}
                    if "before" in str(hit.get("field", "")).lower() or "before" in str(hit.get("path", "")).lower():
                        historical_analysis_queued_hits.append(item)
                    else:
                        current_analysis_queued_hits.append(item)

    packet_manifest = read_json(packet_root / "packet_manifest.json")
    analysis_status = read_json(packet_root / "analysis" / "analysis_status.json")
    review_report = read_json(paper_final / "review_report.json")
    materials_manifest = read_json(paper_final / "materials_manifest.json")
    status_latest = read_json(status_latest_path) if status_latest_path.exists() else {}
    paper_entry = {}
    for candidate in status_latest.get("papers", []):
        if candidate.get("paper_id") == PAPER_ID:
            paper_entry = candidate
            break

    status_alignment = {
        "materials_manifest_analysis_queue_status": materials_manifest.get("analysis_queue_status"),
        "packet_manifest_analysis_queue_status": packet_manifest.get("analysis_queue_status"),
        "analysis_status_file_status": analysis_status.get("status"),
        "review_report_status": review_report.get("review_status"),
        "review_report_publication_grade": review_report.get("publication_grade"),
        "status_latest_analysis_status": paper_entry.get("analysis_status"),
        "status_latest_review_status": paper_entry.get("review_status"),
        "status_latest_publication_grade": paper_entry.get("publication_grade"),
        "analysis_status_matches": analysis_status.get("status")
        == packet_manifest.get("analysis_queue_status")
        == materials_manifest.get("analysis_queue_status")
        == paper_entry.get("analysis_status"),
        "review_status_matches": review_report.get("review_status") == paper_entry.get("review_status"),
        "publication_grade_matches": review_report.get("publication_grade") == paper_entry.get("publication_grade"),
    }

    result = {
        "paper_id": PAPER_ID,
        "generated_at": now_utc(),
        "expected_final_files": EXPECTED_FINAL_FILES,
        "paper_final_files": paper_files,
        "packet_final_files": packet_files,
        "paper_final_file_set_exact": paper_files == EXPECTED_FINAL_FILES,
        "packet_final_file_set_exact": packet_files == EXPECTED_FINAL_FILES,
        "paper_packet_file_sets_match": paper_files == packet_files,
        "mirrored_artifacts": mirrored_artifacts,
        "all_expected_mirrors_byte_equal": all(
            entry["byte_equal"] for entry in mirrored_artifacts.values()
        ),
        "current_analysis_queued_status_hits": current_analysis_queued_hits,
        "historical_analysis_queued_status_hits": historical_analysis_queued_hits,
        "no_current_analysis_queued_status": not current_analysis_queued_hits,
        "status_alignment": status_alignment,
        "final_inventory_passed": (
            paper_files == EXPECTED_FINAL_FILES
            and packet_files == EXPECTED_FINAL_FILES
            and all(entry["byte_equal"] for entry in mirrored_artifacts.values())
            and not current_analysis_queued_hits
            and status_alignment["analysis_status_matches"]
            and status_alignment["review_status_matches"]
            and status_alignment["publication_grade_matches"]
        ),
        "source_text_emitted": False,
    }

    out = Path(args.json_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "paper_id": PAPER_ID,
        "final_inventory_passed": result["final_inventory_passed"],
        "expected_file_count": len(EXPECTED_FINAL_FILES),
        "all_expected_mirrors_byte_equal": result["all_expected_mirrors_byte_equal"],
        "no_current_analysis_queued_status": result["no_current_analysis_queued_status"],
    }, sort_keys=True))
    return 0 if result["final_inventory_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
