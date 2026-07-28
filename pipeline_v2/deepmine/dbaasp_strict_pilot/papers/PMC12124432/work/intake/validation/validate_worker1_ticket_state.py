#!/usr/bin/env python3
"""Validate worker-1 ticket/material field reconciliation for PMC12124432."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TERMINAL_PREFIXES = ("closed", "resolved")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        row["_line_no"] = line_no
        rows.append(row)
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def ticket_closed_by_response(rows: list[dict[str, Any]]) -> set[str]:
    closed: set[str] = set()
    for row in rows:
        status = str(row.get("response_status") or row.get("status") or "")
        if status.startswith(TERMINAL_PREFIXES):
            ticket_id = row.get("ticket_id")
            if ticket_id:
                closed.add(str(ticket_id))
    return closed


def ticket_closed_by_receipt(rows: list[dict[str, Any]]) -> set[str]:
    return {str(row["ticket_id"]) for row in rows if row.get("ticket_id")}


def field_subset(data: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "open_rework_ticket_count",
        "open_rework_ticket_ids",
        "analysis_queue_status",
        "blocking_source_gap_count",
        "blocking_source_gap_ids",
        "extraction_error_count",
        "material_queue_status",
    ]
    return {key: data.get(key) for key in keys if key in data}


def final_mirror_audit(root: Path, paper_id: str) -> dict[str, Any]:
    paper_final = root / "papers" / paper_id / "final"
    packet_final = root / "packets" / paper_id / "final"
    names = sorted({p.name for p in paper_final.glob("*.json")} | {p.name for p in packet_final.glob("*.json")})
    records: list[dict[str, Any]] = []
    byte_identical_count = 0
    declared_exception_count = 0
    unresolved_non_identical_count = 0
    for name in names:
        paper_path = paper_final / name
        packet_path = packet_final / name
        record: dict[str, Any] = {
            "file_name": name,
            "paper_final_path": rel(paper_path, root) if paper_path.exists() else None,
            "packet_final_path": rel(packet_path, root) if packet_path.exists() else None,
            "paper_exists": paper_path.exists(),
            "packet_exists": packet_path.exists(),
            "byte_identical": False,
            "declared_exception": None,
        }
        if paper_path.exists():
            record["paper_sha256"] = sha256(paper_path)
        if packet_path.exists():
            record["packet_sha256"] = sha256(packet_path)
        if paper_path.exists() and packet_path.exists() and paper_path.read_bytes() == packet_path.read_bytes():
            record["byte_identical"] = True
            byte_identical_count += 1
        elif name == "mechanism_evidence.json" and packet_path.exists() and not paper_path.exists():
            record["declared_exception"] = (
                "packet-only compatibility alias; paper final canonical mechanism record is "
                "mechanism_ontology_record.json and is mirrored byte-identically"
            )
            declared_exception_count += 1
        else:
            unresolved_non_identical_count += 1
        records.append(record)
    return {
        "paper_id": paper_id,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generated_by": "worker-1",
        "paper_final_dir": rel(paper_final, root),
        "packet_final_dir": rel(packet_final, root),
        "record_count": len(records),
        "byte_identical_count": byte_identical_count,
        "declared_exception_count": declared_exception_count,
        "unresolved_non_identical_count": unresolved_non_identical_count,
        "records": records,
        "strict_boundary": "mirror audit only; no source_verified or publication-grade claim",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="pipeline_v2/deepmine/dbaasp_strict_pilot")
    parser.add_argument("--paper-id", default="PMC12124432")
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--mirror-out", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    paper_id = args.paper_id
    packet_root = root / "packets" / paper_id
    paper_root = root / "papers" / paper_id
    rework_root = packet_root / "rework"

    requests = read_jsonl(rework_root / "rework_requests.jsonl")
    responses = read_jsonl(rework_root / "rework_responses.jsonl")
    closures = read_jsonl(rework_root / "closure_receipts.jsonl")
    closed_ids = ticket_closed_by_response(responses) | ticket_closed_by_receipt(closures)
    requested_ids = [str(row["ticket_id"]) for row in requests if row.get("ticket_id")]
    live_open_ids = [ticket_id for ticket_id in requested_ids if ticket_id not in closed_ids]

    packet_manifest = read_json(packet_root / "packet_manifest.json")
    paper_materials = read_json(paper_root / "final" / "materials_manifest.json")
    packet_materials = read_json(packet_root / "final" / "materials_manifest.json")
    paper_review = read_json(paper_root / "final" / "review_report.json")
    packet_review = read_json(packet_root / "final" / "review_report.json")
    analysis_status = read_json(packet_root / "analysis" / "analysis_status.json")
    extraction_status = read_json(packet_root / "extraction" / "extraction_status.json")
    extraction_error_rows = read_jsonl(packet_root / "extraction" / "extraction_errors.jsonl")

    live_count = len(live_open_ids)
    tracked_artifacts = {
        "packet_manifest": packet_manifest,
        "paper_final_materials_manifest": paper_materials,
        "packet_final_materials_manifest": packet_materials,
        "paper_final_review_report": paper_review,
        "packet_final_review_report": packet_review,
        "packet_analysis_status": analysis_status,
    }
    observed_fields = {name: field_subset(data) for name, data in tracked_artifacts.items()}
    ticket_alignment = {
        name: {
            "count_matches_live_ledger": data.get("open_rework_ticket_count") == live_count,
            "ids_match_live_ledger": data.get("open_rework_ticket_ids") == live_open_ids,
        }
        for name, data in tracked_artifacts.items()
    }
    field_alignment = {
        "packet_manifest_vs_paper_materials": field_subset(packet_manifest) == field_subset(paper_materials),
        "packet_manifest_vs_packet_materials": field_subset(packet_manifest) == field_subset(packet_materials),
        "paper_materials_vs_paper_review": field_subset(paper_materials) == field_subset(paper_review),
        "packet_review_vs_paper_review": field_subset(packet_review) == field_subset(paper_review),
    }
    expected_error_count = len(extraction_error_rows)
    extraction_error_alignment = {
        "expected_error_count_from_jsonl": expected_error_count,
        "extraction_status_error_count": extraction_status.get("error_count"),
        "packet_manifest_extraction_error_count": packet_manifest.get("extraction_error_count"),
        "paper_materials_extraction_error_count": paper_materials.get("extraction_error_count"),
        "packet_materials_extraction_error_count": packet_materials.get("extraction_error_count"),
        "paper_review_extraction_error_count": paper_review.get("extraction_error_count"),
        "packet_review_extraction_error_count": packet_review.get("extraction_error_count"),
    }
    extraction_values = list(extraction_error_alignment.values())
    extraction_aligned = all(value == expected_error_count for value in extraction_values)
    mirror = final_mirror_audit(root, paper_id)

    report = {
        "paper_id": paper_id,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generated_by": "worker-1",
        "parsed_inputs": {
            "rework_requests": rel(rework_root / "rework_requests.jsonl", root),
            "rework_responses": rel(rework_root / "rework_responses.jsonl", root),
            "closure_receipts": rel(rework_root / "closure_receipts.jsonl", root),
            "packet_manifest": rel(packet_root / "packet_manifest.json", root),
            "paper_materials_manifest": rel(paper_root / "final" / "materials_manifest.json", root),
            "packet_materials_manifest": rel(packet_root / "final" / "materials_manifest.json", root),
            "paper_review_report": rel(paper_root / "final" / "review_report.json", root),
            "packet_review_report": rel(packet_root / "final" / "review_report.json", root),
            "analysis_status": rel(packet_root / "analysis" / "analysis_status.json", root),
            "extraction_status": rel(packet_root / "extraction" / "extraction_status.json", root),
            "extraction_errors": rel(packet_root / "extraction" / "extraction_errors.jsonl", root),
        },
        "ledger_counts": {
            "requested_ticket_count": len(requested_ids),
            "response_row_count": len(responses),
            "closure_receipt_count": len(closures),
            "closed_ticket_count": len(closed_ids),
            "live_open_ticket_count": live_count,
            "live_open_ticket_ids": live_open_ids,
        },
        "observed_fields": observed_fields,
        "ticket_alignment": ticket_alignment,
        "field_alignment": field_alignment,
        "extraction_error_alignment": extraction_error_alignment,
        "final_mirror_audit_path": rel(Path(args.mirror_out), root),
        "final_mirror_summary": {
            "record_count": mirror["record_count"],
            "byte_identical_count": mirror["byte_identical_count"],
            "declared_exception_count": mirror["declared_exception_count"],
            "unresolved_non_identical_count": mirror["unresolved_non_identical_count"],
        },
        "pass": (
            all(item["count_matches_live_ledger"] and item["ids_match_live_ledger"] for item in ticket_alignment.values())
            and all(field_alignment.values())
            and extraction_aligned
            and mirror["unresolved_non_identical_count"] == 0
        ),
        "strict_boundary": "field reconciliation and mirror validation only; source verification and terminal closure remain reserved for downstream/adjudication lanes",
    }

    Path(args.json_out).write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.mirror_out).write_text(json.dumps(mirror, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "pass": report["pass"],
        "live_open_ticket_count": live_count,
        "final_mirror_unresolved_non_identical_count": mirror["unresolved_non_identical_count"],
        "json_out": args.json_out,
        "mirror_out": args.mirror_out,
    }, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
