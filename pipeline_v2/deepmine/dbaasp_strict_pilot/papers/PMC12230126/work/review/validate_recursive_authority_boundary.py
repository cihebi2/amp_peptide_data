#!/usr/bin/env python3
"""Validate the leader-owned recursive DBAASP authority boundary contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PAPER_ID = "PMC12230126"


def true_locations(value: Any, pointer: str = "$") -> list[str]:
    locations: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = f"{pointer}/{key}"
            if key == "authoritative_dbaasp_ingest_ready" and child is True:
                locations.append(child_pointer)
            locations.extend(true_locations(child, child_pointer))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            locations.extend(true_locations(child, f"{pointer}/{index}"))
    return locations


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def validate(base: Path) -> dict[str, Any]:
    paper = base / "papers" / PAPER_ID
    packet = base / "packets" / PAPER_ID
    worker_paths = [
        paper / "work/database_record_audit/record_identity_audit.json",
        packet / "analysis/database_record_audit.worker4.json",
    ]
    final_paths = [
        paper / "final/database_record_verification.json",
        paper / "final/activity_toxicity_evidence.json",
        paper / "final/mechanism_ontology_record.json",
        paper / "final/review_report.json",
        packet / "final/database_record_verification.json",
        packet / "final/activity_toxicity_evidence.json",
        packet / "final/mechanism_evidence.json",
        packet / "final/review_report.json",
    ]
    required = worker_paths + final_paths + [
        packet / "database/database_source_manifest.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    payloads = {str(path): read(path) for path in required if path.exists()}
    worker_true = {
        str(path): true_locations(payloads.get(str(path), {}))
        for path in worker_paths
    }
    final_true = {
        str(path): true_locations(payloads.get(str(path), {}))
        for path in final_paths
    }
    db_manifest = payloads.get(str(packet / "database/database_source_manifest.json"), {})
    row_counts = db_manifest.get("row_counts")
    row_counts = row_counts if isinstance(row_counts, dict) else {}
    linked_keys = [
        "linked_article_records",
        "linked_assay_records",
        "linked_sequence_records",
        "linked_literature_records",
    ]
    linked_total = sum(int(row_counts.get(key) or 0) for key in linked_keys)

    worker_mirrors_identical = bool(
        all(path.exists() for path in worker_paths)
        and hashlib.sha256(worker_paths[0].read_bytes()).hexdigest()
        == hashlib.sha256(worker_paths[1].read_bytes()).hexdigest()
    )
    checks = {
        "all_required_artifacts_present": not missing,
        "worker4_recursive_authority_true_count_is_0": not any(worker_true.values()),
        "final_recursive_authority_true_count_is_0": not any(final_true.values()),
        "linked_authoritative_row_total_is_0": linked_total == 0,
        "fallback_rows_not_promoted_to_authoritative_ingest": not any(
            true_locations(payload) for payload in payloads.values()
        ),
        "worker4_paper_packet_artifacts_byte_identical": worker_mirrors_identical,
    }
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "paper_id": PAPER_ID,
        "contract": "leader_recursive_authority_boundary_rework_20260726",
        "contract_pass": not failed,
        "checks": checks,
        "failed_checks": failed,
        "missing_paths": missing,
        "worker4_true_locations": worker_true,
        "final_true_locations": final_true,
        "linked_authoritative_row_total": linked_total,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base",
        type=Path,
        default=Path(__file__).resolve().parents[4],
    )
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = validate(args.base)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["contract_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
