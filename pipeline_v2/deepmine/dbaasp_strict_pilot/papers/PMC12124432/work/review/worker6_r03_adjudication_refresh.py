#!/usr/bin/env python3
"""Refresh worker-6 adjudication finals for PMC12124432.

This script is intentionally paper-local and offline. It repairs final JSON
field state from packet-local artifacts, preserves unresolved material gaps, and
mirrors paper/packet finals byte-identically.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "PMC12124432"
RUNTIME_TICKETS = [
    "rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-001",
    "rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-002",
    "rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-003",
]

ROOT = Path("/home/cihebi/抗菌肽/数据集/batch/5-team")
PILOT = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot"
PAPER = PILOT / "papers" / PAPER_ID
PACKET = PILOT / "packets" / PAPER_ID
PAPER_FINAL = PAPER / "final"
PACKET_FINAL = PACKET / "final"
WORK_REVIEW = PAPER / "work/review"
VALIDATION = WORK_REVIEW / "validation"

GATE_PATHS = {
    "packet": str((VALIDATION / "packet_gate.worker6_runtime_strict.json").relative_to(ROOT)),
    "semantic": str((VALIDATION / "semantic_gate.worker6_runtime_strict.json").relative_to(ROOT)),
    "publication": str((VALIDATION / "publication_gate.worker6_runtime_strict.json").relative_to(ROOT)),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def marker_check(path: Path) -> dict[str, Any]:
    markers = [b"<html", b"Preparing to download", b"POW_CHALLENGE"]
    data = path.read_bytes() if path.exists() else b""
    return {
        "path": rel(path),
        "exists": path.exists(),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest() if data else None,
        "placeholder_markers_present": [
            marker.decode("utf-8") for marker in markers if marker.lower() in data.lower()
        ],
        "real_csv_recovered": bool(data) and not any(marker.lower() in data.lower() for marker in markers),
    }


def contains_s001_gap(path: Path) -> dict[str, Any]:
    data = load_json(path)
    s001_mentions = 0
    gap_markers = 0

    def walk(value: Any) -> None:
        nonlocal s001_mentions, gap_markers
        if isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
        elif isinstance(value, str):
            lower = value.lower()
            if "anie-64-e202501299-s001.csv" in lower or "s001.csv" in lower:
                s001_mentions += 1
            if any(term in lower for term in ("placeholder", "source_gap", "unrecoverable", "pow_challenge", "html")):
                gap_markers += 1

    walk(data)
    return {
        "path": rel(path),
        "s001_reference_count": s001_mentions,
        "gap_marker_count": gap_markers,
        "preserves_gap": s001_mentions > 0 and gap_markers > 0,
    }


def repair_database_sequences(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    repaired = copy.deepcopy(data)
    changed_paths: list[str] = []

    def patch_dict(obj: dict[str, Any], path: str) -> None:
        for key, value in list(obj.items()):
            child_path = f"{path}.{key}" if path else key
            if isinstance(value, str) and value.strip().lower() == "none" and "sequence" in key.lower():
                obj[key] = None
                obj.setdefault("raw_fallback_placeholder_literal_present", True)
                obj.setdefault("raw_fallback_placeholder_kind", "missing_candidate_value_placeholder")
                changed_paths.append(child_path)
            elif isinstance(value, dict):
                patch_dict(value, child_path)
            elif isinstance(value, list):
                patch_list(value, child_path)

        sequence_keys = (
            "sequence",
            "candidate_sequence",
            "plain_one_letter_sequence",
            "source_sequence",
            "source_sequence_notation",
        )
        has_null_sequence = any(key in obj and obj.get(key) is None for key in sequence_keys)
        has_no_plain_sequence = obj.get("plain_one_letter_sequence") is None or obj.get("plain_one_letter_sequence_emitted") is False
        if has_null_sequence or has_no_plain_sequence:
            for length_key in ("sequence_length", "candidate_sequence_length"):
                if isinstance(obj.get(length_key), int):
                    obj[length_key] = None
                    changed_paths.append(f"{path}.{length_key}" if path else length_key)
            for count_key in ("sequence_length_independent_count", "candidate_sequence_length_independent_count", "independent_count"):
                if isinstance(obj.get(count_key), int):
                    obj[count_key] = None
                    changed_paths.append(f"{path}.{count_key}" if path else count_key)
            for sha_key in ("sequence_sha1_12", "candidate_sequence_sha1_12"):
                if isinstance(obj.get(sha_key), str):
                    obj[sha_key] = None
                    changed_paths.append(f"{path}.{sha_key}" if path else sha_key)
            if "sequence_length_check_passed" in obj:
                obj["sequence_length_check_passed"] = False
                obj["sequence_length_check_status"] = "not_applicable_no_plain_one_letter_sequence"
                changed_paths.append(f"{path}.sequence_length_check_passed" if path else "sequence_length_check_passed")
            if "passes" in obj and ("candidate_sequence_length" in obj or "independent_count" in obj):
                obj["passes"] = False
                obj["status"] = "not_applicable_no_plain_one_letter_sequence"
                changed_paths.append(f"{path}.passes" if path else "passes")

    def patch_list(items: list[Any], path: str) -> None:
        for idx, item in enumerate(items):
            child_path = f"{path}[{idx}]"
            if isinstance(item, dict):
                patch_dict(item, child_path)
            elif isinstance(item, list):
                patch_list(item, child_path)

    patch_dict(repaired, "")

    repaired["field_level_repair"] = {
        "updated_at": utc_now(),
        "updated_by": "worker-6",
        "ticket_id": "rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-002",
        "action": "replaced literal placeholder sequence values with JSON null and not-applicable length checks",
        "changed_path_count": len(changed_paths),
        "changed_path_examples": changed_paths[:12],
        "machine_candidate_boundary": "DBAASP Codex fallback values remain candidate machine evidence only and are not source_verified.",
    }
    repaired["publication_grade"] = False
    repaired["authoritative_ingest_ready"] = False
    repaired["authoritative_dbaasp_ingest_ready"] = False
    repaired.setdefault("summary_counts", {})["source_verified_records"] = 0

    scan = scan_database_sequence_fields(repaired)
    return repaired, {
        "changed_path_count": len(changed_paths),
        "changed_path_examples": changed_paths[:12],
        "post_repair_scan": scan,
    }


def scan_database_sequence_fields(data: Any) -> dict[str, Any]:
    literal_none_paths: list[str] = []
    plain_sequence_checks = 0
    plain_sequence_check_failures = 0
    placeholder_length_paths: list[str] = []

    def walk(value: Any, path: str) -> None:
        nonlocal plain_sequence_checks, plain_sequence_check_failures
        if isinstance(value, dict):
            seq = value.get("sequence") or value.get("candidate_sequence") or value.get("plain_one_letter_sequence")
            length = value.get("sequence_length") or value.get("candidate_sequence_length")
            if isinstance(seq, str) and seq.isalpha() and isinstance(length, int):
                plain_sequence_checks += 1
                if len(seq) != length:
                    plain_sequence_check_failures += 1
            if (value.get("sequence") is None or value.get("candidate_sequence") is None) and isinstance(length, int):
                placeholder_length_paths.append(path)
            for key, child in value.items():
                child_path = f"{path}.{key}" if path else key
                if isinstance(child, str) and child.strip().lower() == "none" and "sequence" in key.lower():
                    literal_none_paths.append(child_path)
                walk(child, child_path)
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                walk(child, f"{path}[{idx}]")

    walk(data, "")
    return {
        "literal_none_sequence_field_count": len(literal_none_paths),
        "literal_none_sequence_field_examples": literal_none_paths[:12],
        "plain_sequence_length_check_count": plain_sequence_checks,
        "plain_sequence_length_check_fail_count": plain_sequence_check_failures,
        "placeholder_derived_sequence_length_count": len(placeholder_length_paths),
        "placeholder_derived_sequence_length_examples": placeholder_length_paths[:12],
    }


def summarize_live_rework() -> dict[str, Any]:
    requests = read_jsonl(PACKET / "rework/rework_requests.jsonl")
    responses = read_jsonl(PACKET / "rework/rework_responses.jsonl")
    closures = read_jsonl(PACKET / "rework/closure_receipts.jsonl")
    response_by_ticket: dict[str, list[dict[str, Any]]] = {}
    for row in responses:
        response_by_ticket.setdefault(row.get("ticket_id", ""), []).append(row)

    owner_prereqs: dict[str, Any] = {}
    for ticket_id in RUNTIME_TICKETS:
        request = next((row for row in reversed(requests) if row.get("ticket_id") == ticket_id), {})
        owner = request.get("owner_worker")
        owner_responses = [
            row for row in response_by_ticket.get(ticket_id, [])
            if row.get("response_by") == owner
            and row.get("response_status") == "repair_ready_for_adjudication"
            and row.get("analysis_can_resume") is True
        ]
        owner_prereqs[ticket_id] = {
            "owner_worker": owner,
            "owner_nonterminal_repair_present": bool(owner_responses),
            "owner_response_count": len(owner_responses),
            "owner_response_evidence_count": len(owner_responses[-1].get("evidence_paths", [])) if owner_responses else 0,
            "owner_response_created_at": owner_responses[-1].get("created_at") if owner_responses else None,
        }

    return {
        "runtime_open_ticket_ids": RUNTIME_TICKETS,
        "runtime_open_ticket_count": len(RUNTIME_TICKETS),
        "request_row_count": len(requests),
        "response_row_count": len(responses),
        "closure_receipt_row_count": len(closures),
        "owner_repair_prerequisites": owner_prereqs,
    }


def load_gate_summary() -> dict[str, Any]:
    path = VALIDATION / "worker6_runtime_strict_gate_summary.json"
    if not path.exists():
        return {
            "gate_return_codes": {"packet": None, "semantic": None, "publication": None},
            "gate_artifact_paths": GATE_PATHS,
            "gate_result_summary": {"status": "strict gates pending post-refresh execution"},
        }
    summary = load_json(path)
    if all(key in summary for key in ("packet", "semantic", "publication")):
        return {
            "gate_return_codes": {
                "packet": summary.get("packet"),
                "semantic": summary.get("semantic"),
                "publication": summary.get("publication"),
            },
            "gate_artifact_paths": GATE_PATHS,
            "gate_result_summary": {
                "status": "strict_gates_failed_nonterminal"
                if any(summary.get(key) for key in ("packet", "semantic", "publication"))
                else "strict_gates_passed",
                "summary_path": rel(path),
                "artifacts": summary.get("artifacts", {}),
            },
        }
    return {
        "gate_return_codes": summary.get("gate_return_codes", {"packet": None, "semantic": None, "publication": None}),
        "gate_artifact_paths": summary.get("gate_artifact_paths", GATE_PATHS),
        "gate_result_summary": summary.get("gate_result_summary", {}),
    }


def final_count(activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], rework_targets: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "activity_records": len(activity.get("activity_records", [])),
        "toxicity_records": len(activity.get("toxicity_records", [])),
        "database_record_audits": len(database.get("record_audits", [])),
        "mechanism_claims": len(mechanism.get("mechanism_claims", [])),
        "review_rework_targets": len(rework_targets),
    }


def build_rework_targets() -> list[dict[str, Any]]:
    return [
        {
            "ticket_id": "rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-001",
            "worker": "worker-3",
            "layer": "material",
            "artifact_path": rel(PACKET / "raw/supplementary_original/ANIE-64-e202501299-s001.csv"),
            "failing_object": "supplementary asset ANIE-64-e202501299-s001.csv",
            "failure_code": "true_s001_csv_not_recovered_placeholder_html_present",
            "source_evidence_to_check": [
                "xml:p:27",
                "media:xlink:href=ANIE-64-e202501299-s001.csv",
                rel(PAPER / "source/supplementary/ANIE-64-e202501299-s001.csv"),
                rel(PACKET / "raw/supplementary_original/ANIE-64-e202501299-s001.csv"),
            ],
            "required_action": "Restage the real text/plain S1 CSV from a valid local source pool or keep the durable source-gap blocker; do not claim publication_grade while only the placeholder asset is available.",
            "acceptance_check": "S1 CSV byte/content marker check has no placeholder markers and packet extraction_status can move to material_extracted_complete, or the paper remains blocked_missing_primary_material with publication_grade=false.",
        },
        {
            "ticket_id": "rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-002",
            "worker": "worker-6",
            "layer": "database",
            "artifact_path": rel(PAPER_FINAL / "database_record_verification.json"),
            "failing_object": "runtime terminal closure for repaired database placeholder ticket",
            "failure_code": "terminal_closure_blocked_by_global_strict_gates",
            "source_evidence_to_check": [
                rel(PACKET / "database/dbaasp_machine_extracted_rows.jsonl"),
                rel(PACKET / "database/authoritative_match_report.json"),
                rel(PAPER_FINAL / "database_record_verification.json"),
                rel(PACKET_FINAL / "database_record_verification.json"),
            ],
            "required_action": "Keep source_verified_records at 0 and authoritative_ingest_ready false; after the S1 material blocker is resolved, rerun worker-6 strict gates before appending any closed_repaired response.",
            "acceptance_check": "Recursive sequence scan remains clean and all three strict gates pass without allow flags before runtime closure.",
        },
        {
            "ticket_id": "rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-003",
            "worker": "worker-6",
            "layer": "adjudication",
            "artifact_path": rel(PAPER_FINAL / "review_report.json"),
            "failing_object": "runtime terminal closure for live ticket-state reconciliation",
            "failure_code": "terminal_closure_blocked_by_open_runtime_tickets",
            "source_evidence_to_check": [
                rel(PACKET / "packet_manifest.json"),
                rel(PAPER_FINAL / "materials_manifest.json"),
                rel(PAPER_FINAL / "review_report.json"),
                rel(PACKET / "rework/rework_requests.jsonl"),
                rel(PACKET / "rework/rework_responses.jsonl"),
            ],
            "required_action": "Keep paper and packet manifests aligned to the current runtime-open ticket list; rerun closure only after no hard material/database/adjudication target remains.",
            "acceptance_check": "Packet manifest, materials_manifest, review_report, and rework ledger agree on the same live open ticket count before terminal closure.",
        },
    ]


def mirror_audit() -> list[dict[str, Any]]:
    pairs = [
        ("activity_toxicity_evidence", PAPER_FINAL / "activity_toxicity_evidence.json", PACKET_FINAL / "activity_toxicity_evidence.json"),
        ("database_record_verification", PAPER_FINAL / "database_record_verification.json", PACKET_FINAL / "database_record_verification.json"),
        ("mechanism_ontology_record", PAPER_FINAL / "mechanism_ontology_record.json", PACKET_FINAL / "mechanism_ontology_record.json"),
        ("mechanism_evidence_alias", PAPER_FINAL / "mechanism_ontology_record.json", PACKET_FINAL / "mechanism_evidence.json"),
        ("review_report", PAPER_FINAL / "review_report.json", PACKET_FINAL / "review_report.json"),
        ("materials_manifest", PAPER_FINAL / "materials_manifest.json", PACKET_FINAL / "materials_manifest.json"),
    ]
    rows: list[dict[str, Any]] = []
    for name, paper_path, packet_path in pairs:
        rows.append({
            "name": name,
            "paper_path": rel(paper_path),
            "packet_path": rel(packet_path),
            "paper_exists": paper_path.exists(),
            "packet_exists": packet_path.exists(),
            "byte_identical": paper_path.exists() and packet_path.exists() and paper_path.read_bytes() == packet_path.read_bytes(),
            "paper_sha256": sha256_file(paper_path),
            "packet_sha256": sha256_file(packet_path),
        })
    return rows


def main() -> None:
    now = utc_now()
    VALIDATION.mkdir(parents=True, exist_ok=True)
    PACKET_FINAL.mkdir(parents=True, exist_ok=True)

    activity = load_json(PAPER / "work/activity_evidence/activity_records.json")
    activity["finalized_by"] = "worker-6"
    activity["finalized_at"] = now
    activity["source_reviewed_by_worker6"] = True
    activity["publication_grade_claim"] = False
    activity["publication_grade_note"] = "Final activity/toxicity evidence remains non-publication-grade while S1 supplementary CSV is a blocking source gap."

    database_source = load_json(PAPER / "work/database_record_audit/record_identity_audit.json")
    database, database_scan = repair_database_sequences(database_source)
    database["finalized_by"] = "worker-6"
    database["finalized_at"] = now

    mechanism = load_json(PAPER / "work/mechanism_ontology/mechanism_evidence.json")
    mechanism["finalized_by"] = "worker-6"
    mechanism["finalized_at"] = now
    mechanism["publication_grade_claim"] = False
    mechanism["publication_grade_note"] = "Mechanism evidence is source-reviewed for available packet materials, but the paper remains non-publication-grade because S1 is unrecovered."

    packet_manifest = load_json(PACKET / "packet_manifest.json")
    packet_manifest["open_rework_ticket_ids"] = RUNTIME_TICKETS
    packet_manifest["open_rework_ticket_count"] = len(RUNTIME_TICKETS)
    packet_manifest["analysis_queue_status"] = "analysis_needs_analysis_rework"
    packet_manifest["material_queue_status"] = "material_extracted_with_gaps"
    packet_manifest["blocking_source_gap_count"] = 1
    packet_manifest.setdefault("blocking_source_gap_ids", ["source_gap_placeholder_html_s001_csv"])
    packet_manifest["extraction_error_count"] = max(1, int(packet_manifest.get("extraction_error_count") or 0))
    packet_manifest["updated_at"] = now
    packet_manifest["updated_by"] = "worker-6"

    write_json(PAPER_FINAL / "activity_toxicity_evidence.json", activity)
    write_json(PACKET_FINAL / "activity_toxicity_evidence.json", activity)
    write_json(PAPER_FINAL / "database_record_verification.json", database)
    write_json(PACKET_FINAL / "database_record_verification.json", database)
    write_json(PAPER_FINAL / "mechanism_ontology_record.json", mechanism)
    write_json(PACKET_FINAL / "mechanism_ontology_record.json", mechanism)
    write_json(PACKET_FINAL / "mechanism_evidence.json", mechanism)
    write_json(PAPER_FINAL / "materials_manifest.json", packet_manifest)
    write_json(PACKET_FINAL / "materials_manifest.json", packet_manifest)

    rework_targets = build_rework_targets()
    live_rework = summarize_live_rework()
    gate_summary = load_gate_summary()

    paper_csv = marker_check(PAPER / "source/supplementary/ANIE-64-e202501299-s001.csv")
    packet_csv = marker_check(PACKET / "raw/supplementary_original/ANIE-64-e202501299-s001.csv")
    supp_gap = contains_s001_gap(PAPER / "work/supplementary_methods/supplementary_evidence.json")
    packet_supp_gap = contains_s001_gap(PACKET / "analysis/supplementary_evidence.worker3.json")
    supplementary_index_gap = contains_s001_gap(PACKET / "extracted/supplementary_index.json")

    db_counts = database.get("summary_counts", {})
    authoritative_counts = {
        "linked_article_records": jsonl_count(PACKET / "database/linked_article_records.jsonl"),
        "linked_assay_records": jsonl_count(PACKET / "database/linked_assay_records.jsonl"),
        "linked_sequence_records": jsonl_count(PACKET / "database/linked_sequence_records.jsonl"),
        "linked_literature_records": jsonl_count(PACKET / "database/linked_literature_records.jsonl"),
        "dbaasp_machine_candidate_rows": jsonl_count(PACKET / "database/dbaasp_machine_extracted_rows.jsonl"),
    }

    ticket_contract_evidence = {
        RUNTIME_TICKETS[0]: {
            "ticket_id": RUNTIME_TICKETS[0],
            "owner_worker": "worker-3",
            "owner_nonterminal_repair_present": live_rework["owner_repair_prerequisites"][RUNTIME_TICKETS[0]]["owner_nonterminal_repair_present"],
            "checks": {
                "paper_csv_marker_check": paper_csv,
                "packet_csv_marker_check": packet_csv,
                "supplementary_evidence_preserves_gap": supp_gap,
                "packet_supplementary_evidence_preserves_gap": packet_supp_gap,
                "supplementary_index_preserves_gap": supplementary_index_gap,
                "material_status_with_gaps": packet_manifest.get("material_queue_status") == "material_extracted_with_gaps",
                "review_publication_grade_false": True,
            },
            "contract_pass": False,
            "closure_blocked_reasons": [
                "real_s001_csv_not_recovered",
                "blocking_source_gap_count_is_nonzero",
                "publication_grade_must_remain_false",
            ],
        },
        RUNTIME_TICKETS[1]: {
            "ticket_id": RUNTIME_TICKETS[1],
            "owner_worker": "worker-4",
            "owner_nonterminal_repair_present": live_rework["owner_repair_prerequisites"][RUNTIME_TICKETS[1]]["owner_nonterminal_repair_present"],
            "checks": {
                "recursive_sequence_scan": database_scan["post_repair_scan"],
                "source_verified_records": db_counts.get("source_verified_records"),
                "authoritative_ingest_ready": database.get("authoritative_ingest_ready"),
                "authoritative_row_counts": authoritative_counts,
            },
            "contract_pass": database_scan["post_repair_scan"]["literal_none_sequence_field_count"] == 0
            and database_scan["post_repair_scan"]["placeholder_derived_sequence_length_count"] == 0
            and db_counts.get("source_verified_records") == 0
            and database.get("authoritative_ingest_ready") is False,
            "closure_blocked_reasons": ["global_strict_gates_do_not_pass_while_s001_gap_remains"],
        },
        RUNTIME_TICKETS[2]: {
            "ticket_id": RUNTIME_TICKETS[2],
            "owner_worker": "worker-1",
            "owner_nonterminal_repair_present": live_rework["owner_repair_prerequisites"][RUNTIME_TICKETS[2]]["owner_nonterminal_repair_present"],
            "checks": {
                "packet_manifest_open_ticket_count": packet_manifest.get("open_rework_ticket_count"),
                "packet_manifest_open_ticket_ids": packet_manifest.get("open_rework_ticket_ids"),
                "materials_manifest_expected_to_mirror_packet_manifest": True,
                "review_report_open_ticket_count": len(RUNTIME_TICKETS),
                "extraction_error_count": packet_manifest.get("extraction_error_count"),
            },
            "contract_pass": True,
            "closure_blocked_reasons": ["runtime_open_ticket_list_still_contains_all_three_r03_tickets"],
        },
    }

    final_counts = final_count(activity, database, mechanism, rework_targets)
    materials_exhausted = {
        "paper_xml": {"checked": True, "paths": [rel(PAPER / "source/paper.xml"), rel(PACKET / "raw/paper.xml")]},
        "paper_pdf": {"checked": True, "paths": [rel(PAPER / "source/paper.pdf"), rel(PACKET / "raw/paper.pdf")]},
        "oa_package": {"checked": True, "paths": [rel(PACKET / "extracted/archive_manifest.json")], "status": "no_additional_recovered_s001_csv"},
        "supplementary_assets": {
            "reviewed": True,
            "exhausted_for_publication": False,
            "status": "blocking_source_gap",
            "blocking_gap_ids": packet_manifest.get("blocking_source_gap_ids", []),
            "unavailable_assets": ["ANIE-64-e202501299-s001.csv"],
        },
        "merged_database_rows": {
            "checked": True,
            "paths": [
                rel(PACKET / "database/authoritative_match_report.json"),
                rel(PACKET / "database/dbaasp_machine_extracted_rows.jsonl"),
                rel(PACKET / "database/linked_article_records.jsonl"),
                rel(PACKET / "database/linked_assay_records.jsonl"),
                rel(PACKET / "database/linked_sequence_records.jsonl"),
                rel(PACKET / "database/linked_literature_records.jsonl"),
            ],
        },
        "database_authoritative_linkage": {
            "checked": True,
            "linked_authoritative_row_total": sum(
                authoritative_counts[key]
                for key in ("linked_article_records", "linked_assay_records", "linked_sequence_records", "linked_literature_records")
            ),
            "accepted_with_caution": True,
        },
        "blocking_source_gap_count": packet_manifest.get("blocking_source_gap_count"),
        "blocking_source_gap_ids": packet_manifest.get("blocking_source_gap_ids", []),
        "extraction_error_count": packet_manifest.get("extraction_error_count"),
        "open_rework_ticket_count": len(RUNTIME_TICKETS),
        "open_rework_ticket_ids": RUNTIME_TICKETS,
    }

    verified_artifact_paths = {
        "activity_toxicity_evidence": {
            "paper": rel(PAPER_FINAL / "activity_toxicity_evidence.json"),
            "packet": rel(PACKET_FINAL / "activity_toxicity_evidence.json"),
        },
        "database_record_verification": {
            "paper": rel(PAPER_FINAL / "database_record_verification.json"),
            "packet": rel(PACKET_FINAL / "database_record_verification.json"),
        },
        "mechanism_ontology_record": {
            "paper": rel(PAPER_FINAL / "mechanism_ontology_record.json"),
            "packet": rel(PACKET_FINAL / "mechanism_ontology_record.json"),
            "packet_record_alias": rel(PACKET_FINAL / "mechanism_evidence.json"),
        },
        "review_report": {
            "paper": rel(PAPER_FINAL / "review_report.json"),
            "packet": rel(PACKET_FINAL / "review_report.json"),
        },
        "materials_manifest": {
            "paper": rel(PAPER_FINAL / "materials_manifest.json"),
            "packet": rel(PACKET_FINAL / "materials_manifest.json"),
        },
    }

    review_report = {
        "paper_id": PAPER_ID,
        "artifact_role": "worker6_final_review_report",
        "reviewed_at": now,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "source_review_complete_for_publication": False,
        "review_status": "blocked_missing_primary_material",
        "publication_grade": False,
        "validator_contract_passed": False,
        "adjudication_summary": "Worker-6 refreshed the three-layer finals from current worker artifacts and preserved the runtime-open S1 CSV source gap. Database placeholder sequence fields were repaired to null/unresolved candidate state, but the unrecovered S1 supplementary CSV keeps the paper non-publication-grade and blocks terminal ticket closure.",
        "checked_inputs": [
            rel(PACKET / "packet_manifest.json"),
            rel(PACKET / "extracted/xml_sections.json"),
            rel(PACKET / "extracted/pdf_text.jsonl"),
            rel(PACKET / "extracted/supplementary_index.json"),
            rel(PACKET / "extracted/supplementary_text.jsonl"),
            rel(PACKET / "database/authoritative_match_report.json"),
            rel(PACKET / "database/dbaasp_machine_extracted_rows.jsonl"),
            rel(PAPER / "work/activity_evidence/activity_records.json"),
            rel(PAPER / "work/database_record_audit/record_identity_audit.json"),
            rel(PAPER / "work/mechanism_ontology/mechanism_evidence.json"),
            rel(PAPER / "work/supplementary_methods/supplementary_evidence.json"),
        ],
        "source_review_depth": {
            "paper_xml": materials_exhausted["paper_xml"],
            "paper_pdf": materials_exhausted["paper_pdf"],
            "oa_package": materials_exhausted["oa_package"],
            "supplementary_assets": materials_exhausted["supplementary_assets"],
            "merged_database_rows": materials_exhausted["merged_database_rows"],
        },
        "materials_exhausted": materials_exhausted,
        "material_queue_status": packet_manifest.get("material_queue_status"),
        "analysis_queue_status": packet_manifest.get("analysis_queue_status"),
        "blocking_source_gap_count": packet_manifest.get("blocking_source_gap_count"),
        "blocking_source_gap_ids": packet_manifest.get("blocking_source_gap_ids", []),
        "extraction_error_count": packet_manifest.get("extraction_error_count"),
        "open_rework_ticket_count": len(RUNTIME_TICKETS),
        "open_rework_ticket_ids": RUNTIME_TICKETS,
        "semantic_quality_checks": {
            "activity_toxicity_rebuilt_from_current_worker2_repair": True,
            "database_rebuilt_from_current_worker4_repair": True,
            "database_placeholder_sequence_fields_repaired": ticket_contract_evidence[RUNTIME_TICKETS[1]]["contract_pass"],
            "mechanism_rebuilt_from_current_worker5_repair": True,
            "machine_candidate_rows_not_promoted_to_authoritative": True,
            "owner_repair_responses_present_for_assigned_tickets": all(
                item["owner_nonterminal_repair_present"]
                for item in live_rework["owner_repair_prerequisites"].values()
            ),
            "worker3_s001_csv_gap_preserved": {
                "status": "blocking_source_gap",
                "ticket_id": RUNTIME_TICKETS[0],
                "publication_grade_allowed": False,
            },
            "paper_packet_final_mirrors_byte_identical_at_write": True,
            "hard_rework_targets_remaining": True,
            "strict_gates_required_post_write": True,
        },
        "per_layer_decision_rationale": {
            "material": "XML/PDF and supplementary surfaces were inventoried, but S1 CSV remains placeholder HTML at both staged locations and is a blocking source gap.",
            "database": "DBAASP linked authoritative rows are absent; fallback rows are preserved as machine candidates only, with placeholder sequence fields nulled and source_verified_records kept at zero.",
            "activity_toxicity": "Current worker-2 activity/toxicity arrays were carried forward with locators and raw values, but they remain non-publication-grade while the S1 material surface is unrecovered.",
            "mechanism": "Current worker-5 mechanism evidence preserves evidence classes and locators for available packet material without promoting inferred evidence to direct mechanism.",
            "adjudication": "Worker-6 cannot append terminal closed_repaired responses because the runtime-open tickets remain listed and strict gates cannot pass while the material gap is unresolved.",
        },
        "ticket_contract_evidence": ticket_contract_evidence,
        "owner_repair_prerequisites": live_rework["owner_repair_prerequisites"],
        "rework_targets": rework_targets,
        "caution_findings": [
            {
                "caution_id": "PMC12124432-DBAASP-AUTH-NOMATCH",
                "severity": "caution",
                "field": "authoritative_database_linkage",
                "status": "preserved_database_only_boundary",
                "ticket_id": RUNTIME_TICKETS[1],
                "impact": "No authoritative DBAASP linked article/assay/sequence/literature rows are present; machine fallback rows are not ingest-ready.",
            },
            {
                "caution_id": "PMC12124432-S001-SOURCE-GAP",
                "severity": "blocking",
                "field": "supplementary_asset",
                "status": "blocking_missing_primary_material",
                "ticket_id": RUNTIME_TICKETS[0],
                "impact": "The paper remains non-publication-grade until the real S1 CSV is recovered or the controller accepts the durable source gap as blocked.",
            },
        ],
        "strict_gate": {
            "runtime_open_ticket_ids_under_adjudication": RUNTIME_TICKETS,
            "open_rework_ticket_count": len(RUNTIME_TICKETS),
            "required_rework_count": len(rework_targets),
            "hard_rework_targets_remaining": True,
        },
        "final_counts": final_counts,
        "gate_artifact_paths": gate_summary["gate_artifact_paths"],
        "gate_return_codes": gate_summary["gate_return_codes"],
        "gate_result_summary": gate_summary["gate_result_summary"],
        "verified_artifact_paths": verified_artifact_paths,
    }

    quality_feedback = {
        "paper_id": PAPER_ID,
        "artifact_role": "worker6_quality_feedback",
        "generated_at": now,
        "review_status": review_report["review_status"],
        "publication_grade": False,
        "hard_rework_targets": rework_targets,
        "rework_targets": rework_targets,
        "ticket_feedback": {
            ticket_id: {
                "owner_worker": evidence["owner_worker"],
                "owner_nonterminal_repair_present": evidence["owner_nonterminal_repair_present"],
                "contract_pass": evidence["contract_pass"],
                "closure_blocked_reasons": evidence["closure_blocked_reasons"],
                "next_action": next(
                    target["required_action"] for target in rework_targets if target["ticket_id"] == ticket_id
                ),
            }
            for ticket_id, evidence in ticket_contract_evidence.items()
        },
        "quality_gate_plan": GATE_PATHS,
        "caution_findings": review_report["caution_findings"],
    }

    adjudication_report = {
        "paper_id": PAPER_ID,
        "artifact_role": "worker6_adjudication_report",
        "reviewed_at": now,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": review_report["review_status"],
        "publication_grade": False,
        "checked_inputs": review_report["checked_inputs"],
        "runtime_open_ticket_ids_reviewed": RUNTIME_TICKETS,
        "owner_repair_prerequisites": live_rework["owner_repair_prerequisites"],
        "ticket_contract_evidence": ticket_contract_evidence,
        "semantic_quality_checks": review_report["semantic_quality_checks"],
        "per_layer_decision_rationale": review_report["per_layer_decision_rationale"],
        "rework_targets": rework_targets,
        "caution_findings": review_report["caution_findings"],
        "final_counts": final_counts,
        "gate_artifact_paths": gate_summary["gate_artifact_paths"],
        "gate_return_codes": gate_summary["gate_return_codes"],
        "gate_result_summary": gate_summary["gate_result_summary"],
        "verified_artifact_paths": verified_artifact_paths,
        "database_field_repair_audit": database_scan,
        "source_gap_audit": {
            "paper_csv": paper_csv,
            "packet_csv": packet_csv,
            "supplementary_evidence": supp_gap,
            "packet_supplementary_evidence": packet_supp_gap,
            "supplementary_index": supplementary_index_gap,
        },
    }

    write_json(PAPER_FINAL / "review_report.json", review_report)
    write_json(PACKET_FINAL / "review_report.json", review_report)
    write_json(WORK_REVIEW / "quality_feedback.json", quality_feedback)
    write_json(WORK_REVIEW / "adjudication_report.json", adjudication_report)

    # Re-write manifest mirrors after all final paths exist.
    write_json(PAPER_FINAL / "materials_manifest.json", packet_manifest)
    write_json(PACKET_FINAL / "materials_manifest.json", packet_manifest)
    audit = {
        "paper_id": PAPER_ID,
        "generated_at": now,
        "runtime_open_ticket_ids": RUNTIME_TICKETS,
        "mirror_pairs": mirror_audit(),
        "database_field_repair_audit": database_scan,
        "source_gap_audit": adjudication_report["source_gap_audit"],
        "live_rework_state": live_rework,
    }
    write_json(WORK_REVIEW / "worker6_source_review_audit.json", audit)

    print(json.dumps({
        "paper_id": PAPER_ID,
        "review_status": review_report["review_status"],
        "publication_grade": False,
        "rework_targets": len(rework_targets),
        "database_literal_none_sequence_fields": database_scan["post_repair_scan"]["literal_none_sequence_field_count"],
        "mirror_pairs": len(audit["mirror_pairs"]),
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
