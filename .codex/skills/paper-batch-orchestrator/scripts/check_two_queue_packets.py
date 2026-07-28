#!/usr/bin/env python3
"""Check two-queue packet directories for structural handoff readiness.

This checker reports packet/material/artifact state. It does not certify
source-reviewed analysis acceptance or publication-grade completion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

REQUIRED_PACKET_FILES = [
    "packet_manifest.json",
    "extraction/extraction_status.json",
    "extraction/extraction_quality_report.json",
    "extraction/extraction_errors.jsonl",
    "database/database_source_manifest.json",
    "locators/locator_index.json",
    "analysis/analysis_status.json",
    "rework/rework_requests.jsonl",
    "rework/rework_responses.jsonl",
]
REQUIRED_FINAL_FILES = [
    "final/database_record_verification.json",
    "final/activity_toxicity_evidence.json",
    "final/mechanism_evidence.json",
    "final/review_report.json",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def rework_response_is_closed(row: dict[str, Any]) -> bool:
    codes = row.get("gate_return_codes")
    contract = row.get("ticket_contract_evidence")
    verified = row.get("verified_artifact_paths")
    gate_artifacts = row.get("gate_artifact_paths")
    return bool(
        str(row.get("status") or "").strip().lower() == "closed_repaired"
        and str(row.get("response_status") or "").strip().lower() == "closed_repaired"
        and str(row.get("response_by") or "").strip().lower() == "worker-6"
        and row.get("analysis_can_resume") is True
        and row.get("publication_grade") is True
        and str(row.get("review_status") or "").strip().lower()
        in {"accepted_clean", "accepted_with_cautions"}
        and bool(str(row.get("created_at") or "").strip())
        and isinstance(row.get("final_counts"), dict)
        and isinstance(contract, dict)
        and contract.get("overall_contract_pass") is True
        and isinstance(codes, dict)
        and all(codes.get(name, codes.get(f"{name}_gate")) == 0 for name in ("packet", "semantic", "publication"))
        and isinstance(verified, dict)
        and bool(verified)
        and isinstance(gate_artifacts, dict)
        and bool(gate_artifacts)
    )


def _workspace_root(packet: Path) -> Path:
    for candidate in (packet, *packet.parents):
        if (candidate / "pipeline_v2").is_dir() and (candidate / ".codex").is_dir():
            return candidate
    return packet.parent.parent


def _resolve_rework_artifact_path(value: Any, packet: Path) -> Path | None:
    text = str(value or "").strip()
    if not text:
        return None
    path = Path(text)
    if path.is_absolute():
        return path
    root = _workspace_root(packet)
    candidates = [root / path, packet.parent.parent / path, packet / path]
    return next((candidate for candidate in candidates if candidate.exists()), candidates[0])


def _artifact_path_values(value: Any) -> list[Any]:
    if isinstance(value, dict):
        return [item for nested in value.values() for item in _artifact_path_values(nested)]
    if isinstance(value, list):
        return [item for nested in value for item in _artifact_path_values(nested)]
    return [value]


def _response_epoch(row: dict[str, Any]) -> float | None:
    text = str(row.get("created_at") or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _gate_payloads_valid(
    row: dict[str, Any], packet: Path, closing_ticket_ids: set[str]
) -> tuple[bool, list[Path]]:
    gate_artifacts = row.get("gate_artifact_paths") or {}
    payloads: dict[str, dict[str, Any]] = {}
    paths: list[Path] = []
    for name in ("packet", "semantic", "publication"):
        value = gate_artifacts.get(name, gate_artifacts.get(f"{name}_gate"))
        path = _resolve_rework_artifact_path(value, packet)
        if path is None or not path.exists():
            return False, []
        try:
            payload = read_json(path)
        except (OSError, json.JSONDecodeError):
            return False, []
        if not isinstance(payload, dict):
            return False, []
        payloads[name] = payload
        paths.append(path)

    paper_id = packet.name
    packet_gate = payloads["packet"]
    packet_results = packet_gate.get("results")
    if not (
        packet_gate.get("paper_count") == 1
        and packet_gate.get("hard_finding_count") == 0
        and packet_gate.get("hard_finding_papers") in ([], None)
        and isinstance(packet_results, list)
        and len(packet_results) == 1
        and packet_results[0].get("paper_id") == paper_id
        and packet_results[0].get("hard_findings") in ([], None)
        and packet_results[0].get("missing_packet_files") in ([], None)
        and packet_results[0].get("missing_final_files") in ([], None)
    ):
        return False, []
    packet_open_ids = {
        str(item)
        for item in (packet_results[0].get("open_rework_ticket_ids") or [])
        if str(item)
    }
    if not packet_open_ids.issubset(closing_ticket_ids):
        return False, []
    if packet_gate.get("open_rework_ticket_count") != len(packet_open_ids):
        return False, []

    semantic = payloads["semantic"]
    semantic_results = semantic.get("results")
    if not (
        semantic.get("paper_count") == 1
        and semantic.get("publication_grade_pass_count") == 1
        and semantic.get("publication_grade_fail_count") == 0
        and semantic.get("failed_papers") in ([], None)
        and isinstance(semantic_results, list)
        and len(semantic_results) == 1
        and semantic_results[0].get("paper_id") == paper_id
        and semantic_results[0].get("publication_grade_pass") is True
        and semantic_results[0].get("issue_count") == 0
        and semantic_results[0].get("issues") in ([], None)
    ):
        return False, []

    publication = payloads["publication"]
    risk_counts = publication.get("risk_counts")
    manifest_path = _resolve_rework_artifact_path(publication.get("manifest"), packet)
    if not (
        publication.get("paper_count") == 1
        and publication.get("publication_grade_pass") is True
        and isinstance(risk_counts, dict)
        and not any(int(value or 0) for value in risk_counts.values())
        and manifest_path is not None
        and manifest_path.exists()
    ):
        return False, []
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError):
        return False, []
    if not isinstance(manifest, dict) or manifest.get("paper_ids") != [paper_id]:
        return False, []
    return True, paths


def _first_list_field(data: dict[str, Any], names: list[str]) -> list[Any]:
    for name in names:
        value = data.get(name)
        if isinstance(value, list):
            return value
    return []


def _terminal_final_state(
    row: dict[str, Any], packet: Path
) -> tuple[list[tuple[Path, Path]], dict[str, int]] | None:
    if not rework_response_is_closed(row):
        return None
    pilot_base = packet.parent.parent if packet.parent.name == "packets" else packet.parent
    paper_root = pilot_base / "papers" / packet.name
    expected_pairs = [
        (
            paper_root / "final/activity_toxicity_evidence.json",
            packet / "final/activity_toxicity_evidence.json",
        ),
        (
            paper_root / "final/database_record_verification.json",
            packet / "final/database_record_verification.json",
        ),
        (paper_root / "final/review_report.json", packet / "final/review_report.json"),
        (
            paper_root / "final/mechanism_ontology_record.json",
            packet / "final/mechanism_evidence.json",
        ),
    ]
    verified = row.get("verified_artifact_paths") or {}
    verified_paths = {
        path.resolve()
        for value in _artifact_path_values(verified)
        if (path := _resolve_rework_artifact_path(value, packet)) is not None
    }
    required_paths = {path.resolve() for pair in expected_pairs for path in pair}
    if not required_paths.issubset(verified_paths):
        return None
    if any(not left.exists() or not right.exists() or left.read_bytes() != right.read_bytes() for left, right in expected_pairs):
        return None

    activity = read_json(expected_pairs[0][0])
    database = read_json(expected_pairs[1][0])
    review = read_json(expected_pairs[2][0])
    mechanism = read_json(expected_pairs[3][0])
    counts = row.get("final_counts") or {}
    actual_counts = {
        "activity_records": len(activity.get("activity_records") if isinstance(activity.get("activity_records"), list) else []),
        "toxicity_records": len(activity.get("toxicity_records") if isinstance(activity.get("toxicity_records"), list) else []),
        "database_record_audits": len(_first_list_field(database, ["record_audits", "records", "database_record_audits", "audit_records"])),
        "mechanism_claims": len(mechanism.get("mechanism_claims") if isinstance(mechanism.get("mechanism_claims"), list) else []),
        "review_rework_targets": len(review.get("rework_targets") if isinstance(review.get("rework_targets"), list) else []),
    }
    if any(counts.get(name) != value for name, value in actual_counts.items()):
        return None
    return expected_pairs, actual_counts


def terminal_rework_response_preconditions_valid(row: dict[str, Any], packet: Path) -> bool:
    return _terminal_final_state(row, packet) is not None


def terminal_rework_response_artifacts_valid(
    row: dict[str, Any], packet: Path, closing_ticket_ids: set[str] | None = None
) -> bool:
    final_state = _terminal_final_state(row, packet)
    if final_state is None:
        return False
    expected_pairs, actual_counts = final_state
    if closing_ticket_ids is None:
        closing_ticket_ids = {str(row.get("ticket_id") or "")}
    gate_valid, gate_paths = _gate_payloads_valid(row, packet, closing_ticket_ids)
    if not gate_valid:
        return False
    response_epoch = _response_epoch(row)
    if response_epoch is None or any(path.stat().st_mtime < response_epoch - 1 for path in gate_paths):
        return False
    latest_final_mtime = max(path.stat().st_mtime for pair in expected_pairs for path in pair)
    if any(path.stat().st_mtime + 1 < latest_final_mtime for path in gate_paths):
        return False
    publication = read_json(gate_paths[2])
    publication_counts = publication.get("counts") or {}
    if publication_counts.get("activity_records") != actual_counts["activity_records"]:
        return False
    if publication_counts.get("mechanism_claims") != actual_counts["mechanism_claims"]:
        return False
    return True


def _response_has_repair_evidence(row: dict[str, Any]) -> bool:
    return any(
        row.get(key)
        for key in (
            "evidence",
            "evidence_paths",
            "repaired_artifacts",
            "artifacts_written",
            "added_files",
            "validation_artifacts",
            "closure_basis",
            "reason",
            "notes",
        )
    )


def owner_repair_response_present(
    request: dict[str, Any], prior_responses: list[dict[str, Any]]
) -> bool:
    ticket_id = str(request.get("ticket_id") or "")
    declared_workers = set(re.findall(r"worker-[1-6]", str(request.get("owner_worker") or "").lower()))
    owner_workers = declared_workers - {"worker-6"}
    target_queue = str(request.get("target_queue") or "").lower()
    if declared_workers == {"worker-6"}:
        return True
    if not declared_workers and target_queue == "adjudication":
        return True
    if not owner_workers:
        return False
    eligible = [
        row
        for row in prior_responses
        if str(row.get("ticket_id") or "") == ticket_id
        and str(row.get("response_status") or "").strip().lower()
        == "repair_ready_for_adjudication"
        and re.fullmatch(r"worker-[1-5]", str(row.get("response_by") or "").strip().lower())
        and row.get("analysis_can_resume") is True
        and not rework_response_is_closed(row)
        and _response_has_repair_evidence(row)
    ]
    if owner_workers:
        found = {str(row.get("response_by")).strip().lower() for row in eligible}
        return owner_workers.issubset(found)
    return bool(eligible)


def terminal_response_sha256(row: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def sealed_closure_ticket_ids(
    packet: Path,
    requests: list[dict[str, Any]],
    responses: list[dict[str, Any]],
) -> set[str]:
    requests_by_id = {
        str(request.get("ticket_id") or ""): request
        for request in requests
        if request.get("ticket_id")
    }
    terminal_indices_by_ticket: dict[str, list[int]] = {}
    for index, response in enumerate(responses):
        ticket_id = str(response.get("ticket_id") or "")
        if ticket_id and rework_response_is_closed(response):
            terminal_indices_by_ticket.setdefault(ticket_id, []).append(index)
    valid_by_ticket: dict[str, list[dict[str, Any]]] = {}
    for receipt in read_jsonl(
        packet / "rework/closure_receipts.jsonl"
    ):
        if (
            receipt.get("schema_version")
            != "strict_ticket_closure_receipt_v1"
            or receipt.get("overall_contract_pass") is not True
        ):
            continue
        ticket_id = str(receipt.get("ticket_id") or "")
        request = requests_by_id.get(ticket_id)
        try:
            response_index = int(receipt.get("terminal_response_index"))
        except (TypeError, ValueError):
            continue
        if (
            request is None
            or response_index < 0
            or response_index >= len(responses)
            or terminal_indices_by_ticket.get(ticket_id) != [response_index]
        ):
            continue
        response = responses[response_index]
        if (
            str(response.get("ticket_id") or "") != ticket_id
            or not rework_response_is_closed(response)
            or terminal_response_sha256(response)
            != receipt.get("terminal_response_sha256")
            or not owner_repair_response_present(
                request, responses[:response_index]
            )
        ):
            continue
        valid_by_ticket.setdefault(ticket_id, []).append(receipt)
    return {
        ticket_id
        for ticket_id, receipts in valid_by_ticket.items()
        if len(receipts) == 1
    }


def open_rework_tickets(packet: Path) -> list[dict[str, Any]]:
    requests = read_jsonl(packet / "rework/rework_requests.jsonl")
    responses = read_jsonl(packet / "rework/rework_responses.jsonl")
    terminal_by_ticket: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, row in enumerate(responses):
        ticket_id = str(row.get("ticket_id") or "")
        if ticket_id and rework_response_is_closed(row):
            terminal_by_ticket.setdefault(ticket_id, []).append((index, row))
    requests_by_id = {str(row.get("ticket_id") or ""): row for row in requests}
    prevalidated_terminal_by_ticket: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for ticket_id, rows in terminal_by_ticket.items():
        request = requests_by_id.get(ticket_id)
        if request is None:
            continue
        for index, row in rows:
            if owner_repair_response_present(request, responses[:index]) and terminal_rework_response_preconditions_valid(
                row, packet
            ):
                prevalidated_terminal_by_ticket.setdefault(ticket_id, []).append((index, row))
    closing_ticket_ids = set(prevalidated_terminal_by_ticket)
    while True:
        valid_terminal_by_ticket: dict[str, list[dict[str, Any]]] = {}
        for ticket_id, rows in prevalidated_terminal_by_ticket.items():
            for index, row in rows:
                if terminal_rework_response_artifacts_valid(row, packet, closing_ticket_ids):
                    valid_terminal_by_ticket.setdefault(ticket_id, []).append(row)
        next_closing_ticket_ids = {
            ticket_id
            for ticket_id, rows in valid_terminal_by_ticket.items()
            if len(rows) == 1
        } & closing_ticket_ids
        if next_closing_ticket_ids == closing_ticket_ids:
            break
        closing_ticket_ids = next_closing_ticket_ids
    closed = closing_ticket_ids | sealed_closure_ticket_ids(
        packet, requests, responses
    )
    return [row for row in requests if str(row.get("ticket_id") or "") not in closed]


def paper_ids_from_manifest(path: Path | None, packet_root: Path) -> list[str]:
    if path:
        try:
            data = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"invalid or missing manifest: {path}: {exc}") from exc
        if not isinstance(data, dict):
            raise SystemExit(f"manifest is not a JSON object: {path}")
        ids = data.get("paper_ids")
        if not isinstance(ids, list):
            raise SystemExit(f"manifest has no paper_ids list: {path}")
        paper_ids = [str(item).strip() for item in ids if str(item).strip()]
        if not paper_ids:
            raise SystemExit(f"manifest has no paper ids: {path}")
        return paper_ids
    return sorted(p.name for p in packet_root.iterdir() if p.is_dir())


def check_packet(packet: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_PACKET_FILES if not (packet / rel).exists()]
    missing_final = [rel for rel in REQUIRED_FINAL_FILES if not (packet / rel).exists()]
    manifest = read_json(packet / "packet_manifest.json") if (packet / "packet_manifest.json").exists() else {}
    extraction = read_json(packet / "extraction/extraction_status.json") if (packet / "extraction/extraction_status.json").exists() else {}
    analysis = read_json(packet / "analysis/analysis_status.json") if (packet / "analysis/analysis_status.json").exists() else {}
    locators = read_json(packet / "locators/locator_index.json") if (packet / "locators/locator_index.json").exists() else {}
    db = read_json(packet / "database/database_source_manifest.json") if (packet / "database/database_source_manifest.json").exists() else {}
    open_tickets = open_rework_tickets(packet)
    error_count = int(extraction.get("error_count") or count_jsonl(packet / "extraction/extraction_errors.jsonl"))
    material_status = str(manifest.get("material_queue_status") or extraction.get("status") or "unknown")
    analysis_status = str(manifest.get("analysis_queue_status") or analysis.get("status") or "unknown")
    hard = []
    if missing:
        hard.append("missing_packet_files")
    if material_status == "material_blocked_missing_source":
        hard.append("material_blocked_missing_source")
    if int(locators.get("locator_count") or 0) == 0:
        hard.append("no_locators")
    if missing_final:
        hard.append("missing_final_files")
    return {
        "paper_id": packet.name,
        "packet_root": str(packet),
        "material_status": material_status,
        "analysis_status": analysis_status,
        "missing_packet_files": missing,
        "missing_final_files": missing_final,
        "locator_count": int(locators.get("locator_count") or 0),
        "extraction_error_count": error_count,
        "open_rework_ticket_count": len(open_tickets),
        "open_rework_ticket_ids": [row.get("ticket_id") for row in open_tickets if row.get("ticket_id")],
        "database_row_counts": db.get("row_counts") or {},
        "hard_findings": hard,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check two-queue packet readiness.")
    parser.add_argument("--packet-root", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--allow-findings", action="store_true")
    args = parser.parse_args()

    packet_root = args.packet_root.resolve()
    manifest = args.manifest.resolve() if args.manifest else None
    paper_ids = paper_ids_from_manifest(manifest, packet_root)
    results = [check_packet(packet_root / pid) for pid in paper_ids]
    material_counts = Counter(item["material_status"] for item in results)
    analysis_counts = Counter(item["analysis_status"] for item in results)
    hard = [item for item in results if item["hard_findings"]]
    summary = {
        "packet_root": str(packet_root),
        "paper_count": len(results),
        "material_status_counts": dict(material_counts),
        "analysis_status_counts": dict(analysis_counts),
        "open_rework_ticket_count": sum(item["open_rework_ticket_count"] for item in results),
        "total_locator_count": sum(item["locator_count"] for item in results),
        "total_extraction_error_count": sum(item["extraction_error_count"] for item in results),
        "hard_finding_count": len(hard),
        "hard_finding_papers": [item["paper_id"] for item in hard],
        "results": results,
    }
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if args.allow_findings or not hard else 2


if __name__ == "__main__":
    raise SystemExit(main())
