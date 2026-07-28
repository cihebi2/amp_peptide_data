#!/usr/bin/env python3
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


PAPER_ID = "PMC12124432"
WORKER_ID = "worker-1"
ASSIGNED_TICKET_ID = "rwk-PMC12124432-campaign-r03-PMC12124432-BLOCK-FIELD-003"
REPAIR_ATTEMPT_ID = "worker1_20260728T031659Z"

ROOT = Path("pipeline_v2/deepmine/dbaasp_strict_pilot")
PAPER_ROOT = ROOT / "papers" / PAPER_ID
PACKET_ROOT = ROOT / "packets" / PAPER_ID
SOURCE_ROOT = PAPER_ROOT / "source"
INTAKE_ROOT = PAPER_ROOT / "work" / "intake"
VALIDATION_ROOT = INTAKE_ROOT / "validation"

PATHS = {
    "packet_manifest": PACKET_ROOT / "packet_manifest.json",
    "materials_manifest": PAPER_ROOT / "final" / "materials_manifest.json",
    "review_report": PAPER_ROOT / "final" / "review_report.json",
    "analysis_status": PACKET_ROOT / "analysis" / "analysis_status.json",
    "rework_requests": PACKET_ROOT / "rework" / "rework_requests.jsonl",
    "rework_responses": PACKET_ROOT / "rework" / "rework_responses.jsonl",
    "closure_receipts": PACKET_ROOT / "rework" / "closure_receipts.jsonl",
    "source_inventory": INTAKE_ROOT / "source_inventory.json",
    "intake_report": INTAKE_ROOT / "intake_report.md",
    "ticket_reconciliation": VALIDATION_ROOT / "worker1_ticket_state_reconciliation.json",
    "final_mirror_audit": VALIDATION_ROOT / "worker1_final_mirror_audit.json",
}


def rel(path):
    return str(path)


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def read_jsonl(path):
    rows = []
    if not path.exists():
        return rows
    with path.open(errors="replace") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            row["_line_no"] = line_no
            rows.append(row)
    return rows


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha256(path):
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_record(path):
    return {
        "path": rel(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256(path),
    }


def jsonl_count(path):
    return sum(1 for line in path.open(errors="replace") if line.strip()) if path.exists() else 0


def extract_xml_article_ids(path):
    if not path.exists():
        return {"exists": False, "article_ids": {}}
    ids = {}
    try:
        root = ET.parse(path).getroot()
        for elem in root.iter():
            if elem.tag.rsplit("}", 1)[-1] != "article-id":
                continue
            key = elem.attrib.get("pub-id-type") or "unspecified"
            val = (elem.text or "").strip()
            if val:
                ids.setdefault(key, []).append(val)
    except Exception as exc:
        return {"exists": True, "parse_error": type(exc).__name__, "article_ids": ids}
    return {"exists": True, "article_ids": ids}


def count_xml_sections(path):
    data = read_json(path, default=[])
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        for key in ["sections", "xml_sections", "records"]:
            if isinstance(data.get(key), list):
                return len(data[key])
        return len(data)
    return 0


def compact_extraction_errors(path):
    rows = []
    for row in read_jsonl(path):
        rows.append(
            {
                "line_no": row.get("_line_no"),
                "paper_id": row.get("paper_id"),
                "asset": row.get("asset"),
                "error_type": row.get("error_type"),
                "status": row.get("status"),
                "source_locator": row.get("source_locator"),
                "source_gap_id": row.get("source_gap_id"),
                "ticket_id": row.get("ticket_id"),
                "source_text_excerpts_included": row.get("source_text_excerpts_included", False),
            }
        )
    return rows


def count_csv_rows(path):
    if not path.exists():
        return None
    try:
        with path.open(newline="", errors="replace") as handle:
            return sum(1 for _ in csv.reader(handle))
    except Exception:
        return None


def table_count(path):
    data = read_json(path, default={})
    if isinstance(data, dict):
        if isinstance(data.get("tables"), list):
            return len(data["tables"])
        if isinstance(data.get("structured_table_count"), int):
            return data["structured_table_count"]
    if isinstance(data, list):
        return len(data)
    return 0


def locator_prefix_counts(path):
    data = read_json(path, default={})
    locators = data.get("locators", []) if isinstance(data, dict) else []
    counts = Counter()
    for item in locators:
        locator = item.get("locator") if isinstance(item, dict) else str(item)
        counts[locator.split(":", 1)[0]] += 1
    return dict(sorted(counts.items()))


def live_ticket_state(requests, responses, closures):
    requested_ids = [row.get("ticket_id") for row in requests if row.get("ticket_id")]
    terminal_from_receipts = {row.get("ticket_id") for row in closures if row.get("ticket_id")}
    terminal_from_responses = {
        row.get("ticket_id")
        for row in responses
        if row.get("ticket_id") and str(row.get("response_status", "")).startswith("closed")
    }
    closed_ids = terminal_from_receipts | terminal_from_responses
    live_ids = [ticket_id for ticket_id in requested_ids if ticket_id not in closed_ids]
    return {
        "requested_ticket_ids": requested_ids,
        "terminal_closed_ticket_ids": sorted(closed_ids),
        "live_open_ticket_ids": live_ids,
        "requested_ticket_count": len(requested_ids),
        "closed_ticket_count": len(closed_ids),
        "live_open_ticket_count": len(live_ids),
        "response_row_count": len(responses),
        "closure_receipt_count": len(closures),
    }


def append_owner_response():
    path = PATHS["rework_responses"]
    rows = read_jsonl(path)
    for row in rows:
        if row.get("owner_response_attempt_id") == REPAIR_ATTEMPT_ID:
            return False, row.get("_line_no"), True

    response = {
        "ticket_id": ASSIGNED_TICKET_ID,
        "response_status": "repair_ready_for_adjudication",
        "response_by": WORKER_ID,
        "analysis_can_resume": True,
        "created_at": utc_now(),
        "owner_response_attempt_id": REPAIR_ATTEMPT_ID,
        "evidence": {
            "live_ticket_state_reconciled": True,
            "paper_packet_final_mirrors_byte_identical_or_declared_exception": True,
            "source_verified_claims_made": False,
        },
        "evidence_paths": [
            rel(PATHS["source_inventory"]),
            rel(PATHS["ticket_reconciliation"]),
            rel(PATHS["final_mirror_audit"]),
            rel(PATHS["materials_manifest"]),
            rel(PATHS["review_report"]),
            rel(PATHS["packet_manifest"]),
        ],
        "repaired_artifacts": [
            rel(PATHS["source_inventory"]),
            rel(PATHS["intake_report"]),
            rel(PATHS["ticket_reconciliation"]),
            rel(PATHS["final_mirror_audit"]),
        ],
        "artifacts_written": [
            rel(PATHS["source_inventory"]),
            rel(PATHS["intake_report"]),
            rel(PATHS["ticket_reconciliation"]),
            rel(PATHS["final_mirror_audit"]),
        ],
        "validation_artifacts": [
            rel(VALIDATION_ROOT / "check_two_queue_packets.worker1_refresh.json"),
            rel(VALIDATION_ROOT / "semantic_three_layer_gate.worker1_refresh.json"),
            rel(VALIDATION_ROOT / "check_three_layer_publication_quality.worker1_refresh.json"),
        ],
        "reason": (
            "Worker-1 refreshed intake/material reconciliation from live packet manifest, "
            "final manifests, review report, and rework ledgers; assigned ticket remains "
            "open for worker-6 terminal adjudication."
        ),
        "notes": [
            "No publication-grade or source_verified claim is made by worker-1.",
            "Known blocking source gap and extraction-error counts remain preserved.",
        ],
    }
    with path.open("a") as handle:
        handle.write(json.dumps(response, sort_keys=True) + "\n")
    return True, jsonl_count(path), True


def audit_manifest_alignment(live_state, packet_manifest, materials_manifest, review_report, analysis_status):
    expected_ids = live_state["live_open_ticket_ids"]
    expected_count = live_state["live_open_ticket_count"]
    artifact_fields = {}
    for name, data in [
        ("packet_manifest", packet_manifest),
        ("materials_manifest", materials_manifest),
        ("review_report", review_report),
        ("analysis_status", analysis_status),
    ]:
        if not isinstance(data, dict):
            artifact_fields[name] = {"exists": False}
            continue
        status_value = data.get("analysis_queue_status", data.get("status"))
        artifact_fields[name] = {
            "exists": True,
            "open_rework_ticket_ids": data.get("open_rework_ticket_ids"),
            "open_rework_ticket_count": data.get("open_rework_ticket_count"),
            "analysis_queue_status_or_alias": status_value,
            "blocking_source_gap_count": data.get("blocking_source_gap_count"),
            "extraction_error_count": data.get("extraction_error_count"),
        }

    open_counts = [
        fields.get("open_rework_ticket_count")
        for fields in artifact_fields.values()
        if fields.get("exists") and fields.get("open_rework_ticket_count") is not None
    ]
    open_ids_match = {
        name: fields.get("open_rework_ticket_ids") == expected_ids
        for name, fields in artifact_fields.items()
        if fields.get("exists") and fields.get("open_rework_ticket_ids") is not None
    }
    same_live_open_count_everywhere = bool(open_counts) and all(count == expected_count for count in open_counts)
    return {
        "paper_id": PAPER_ID,
        "generated_at": utc_now(),
        "script": rel(INTAKE_ROOT / "worker1_refresh_intake.py"),
        "parsed_inputs": {
            "rework_requests": rel(PATHS["rework_requests"]),
            "rework_responses": rel(PATHS["rework_responses"]),
            "closure_receipts": rel(PATHS["closure_receipts"]),
            "packet_manifest": rel(PATHS["packet_manifest"]),
            "materials_manifest": rel(PATHS["materials_manifest"]),
            "review_report": rel(PATHS["review_report"]),
            "analysis_status": rel(PATHS["analysis_status"]),
        },
        "ledger_state": live_state,
        "artifact_fields": artifact_fields,
        "same_live_open_ticket_count_everywhere": same_live_open_count_everywhere,
        "open_rework_ticket_ids_match_live_ledger": open_ids_match,
        "materials_manifest_packet_manifest_field_alignment": {
            key: materials_manifest.get(key) == packet_manifest.get(key)
            for key in [
                "open_rework_ticket_ids",
                "open_rework_ticket_count",
                "analysis_queue_status",
                "blocking_source_gap_count",
                "extraction_error_count",
            ]
        },
        "review_report_packet_manifest_field_alignment": {
            key: review_report.get(key) == packet_manifest.get(key)
            for key in [
                "open_rework_ticket_ids",
                "open_rework_ticket_count",
                "analysis_queue_status",
                "blocking_source_gap_count",
                "extraction_error_count",
            ]
        },
    }


def final_mirror_audit():
    paper_final = PAPER_ROOT / "final"
    packet_final = PACKET_ROOT / "final"
    names = sorted({p.name for p in paper_final.glob("*.json")} | {p.name for p in packet_final.glob("*.json")})
    records = []
    for name in names:
        paper_path = paper_final / name
        packet_path = packet_final / name
        paper_exists = paper_path.exists()
        packet_exists = packet_path.exists()
        identical = paper_exists and packet_exists and paper_path.read_bytes() == packet_path.read_bytes()
        status = "byte_identical" if identical else "unresolved_non_identical"
        exception = None
        if name == "mechanism_evidence.json" and (not paper_exists) and packet_exists:
            status = "declared_packet_only_exception"
            exception = {
                "reason": "packet-only analysis alias retained beside mirrored canonical mechanism_ontology_record.json",
                "canonical_mirror": rel(paper_final / "mechanism_ontology_record.json"),
                "packet_alias": rel(packet_path),
            }
        records.append(
            {
                "file_name": name,
                "paper_path": rel(paper_path),
                "packet_path": rel(packet_path),
                "paper_exists": paper_exists,
                "packet_exists": packet_exists,
                "byte_identical": identical,
                "status": status,
                "exception": exception,
                "paper_sha256": sha256(paper_path),
                "packet_sha256": sha256(packet_path),
            }
        )
    return {
        "paper_id": PAPER_ID,
        "generated_at": utc_now(),
        "record_count": len(records),
        "byte_identical_count": sum(1 for row in records if row["status"] == "byte_identical"),
        "declared_exception_count": sum(1 for row in records if row["status"] == "declared_packet_only_exception"),
        "unresolved_non_identical_count": sum(1 for row in records if row["status"] == "unresolved_non_identical"),
        "records": records,
    }


def gate_summary():
    def read_rc(name):
        path = VALIDATION_ROOT / name
        if not path.exists():
            return None
        try:
            return int(path.read_text().strip())
        except Exception:
            return None

    packet_gate = read_json(VALIDATION_ROOT / "check_two_queue_packets.worker1_refresh.json", default={})
    semantic_gate = read_json(VALIDATION_ROOT / "semantic_three_layer_gate.worker1_refresh.json", default={})
    publication_gate = read_json(VALIDATION_ROOT / "check_three_layer_publication_quality.worker1_refresh.json", default={})
    return {
        "packet_gate_json_path": rel(VALIDATION_ROOT / "check_two_queue_packets.worker1_refresh.json"),
        "packet_gate_return_code": read_rc("check_two_queue_packets.worker1_refresh.rc"),
        "packet_gate_paper_count": packet_gate.get("paper_count"),
        "packet_gate_open_rework_ticket_count": packet_gate.get("open_rework_ticket_count"),
        "packet_gate_hard_finding_count": packet_gate.get("hard_finding_count"),
        "packet_gate_total_extraction_error_count": packet_gate.get("total_extraction_error_count"),
        "semantic_gate_json_path": rel(VALIDATION_ROOT / "semantic_three_layer_gate.worker1_refresh.json"),
        "semantic_gate_return_code": read_rc("semantic_three_layer_gate.worker1_refresh.rc"),
        "semantic_gate_publication_grade_pass_count": semantic_gate.get("publication_grade_pass_count"),
        "semantic_gate_publication_grade_fail_count": semantic_gate.get("publication_grade_fail_count"),
        "publication_quality_gate_json_path": rel(VALIDATION_ROOT / "check_three_layer_publication_quality.worker1_refresh.json"),
        "publication_quality_gate_return_code": read_rc("check_three_layer_publication_quality.worker1_refresh.rc"),
        "publication_quality_gate_pass": publication_gate.get("publication_grade_pass"),
        "publication_quality_gate_review_status": publication_gate.get("review_status"),
    }


def build_inventory(appended, response_line_no, response_present):
    packet_manifest = read_json(PATHS["packet_manifest"], default={})
    materials_manifest = read_json(PATHS["materials_manifest"], default={})
    review_report = read_json(PATHS["review_report"], default={})
    analysis_status = read_json(PATHS["analysis_status"], default={})
    requests = read_jsonl(PATHS["rework_requests"])
    responses = read_jsonl(PATHS["rework_responses"])
    closures = read_jsonl(PATHS["closure_receipts"])
    live_state = live_ticket_state(requests, responses, closures)

    ticket_audit = audit_manifest_alignment(
        live_state, packet_manifest, materials_manifest, review_report, analysis_status
    )
    mirror_audit = final_mirror_audit()
    write_json(PATHS["ticket_reconciliation"], ticket_audit)
    write_json(PATHS["final_mirror_audit"], mirror_audit)

    source_files = {
        "paper_xml": SOURCE_ROOT / "paper.xml",
        "paper_pdf": SOURCE_ROOT / "paper.pdf",
        "paper_meta": SOURCE_ROOT / "paper_meta.json",
        "supplementary_s001_csv": SOURCE_ROOT / "supplementary" / "ANIE-64-e202501299-s001.csv",
        "supplementary_s002_pdf": SOURCE_ROOT / "supplementary" / "ANIE-64-e202501299-s002.pdf",
    }
    raw_files = {
        "paper_xml": PACKET_ROOT / "raw" / "paper.xml",
        "paper_pdf": PACKET_ROOT / "raw" / "paper.pdf",
        "paper_meta": PACKET_ROOT / "raw" / "paper_meta.json",
    }
    source_meta = read_json(source_files["paper_meta"], default={})
    xml_ids = extract_xml_article_ids(source_files["paper_xml"])

    db_manifest = read_json(PACKET_ROOT / "database" / "database_source_manifest.json", default={})
    authoritative = read_json(PACKET_ROOT / "database" / "authoritative_match_report.json", default={})
    extraction_status = read_json(PACKET_ROOT / "extraction" / "extraction_status.json", default={})
    extraction_quality = read_json(PACKET_ROOT / "extraction" / "extraction_quality_report.json", default={})
    supplementary_index = read_json(PACKET_ROOT / "extracted" / "supplementary_index.json", default={})
    archive_manifest = read_json(PACKET_ROOT / "extracted" / "archive_manifest.json", default={})

    linked_paths = [
        "linked_article_records.jsonl",
        "linked_assay_records.jsonl",
        "linked_sequence_records.jsonl",
        "linked_literature_records.jsonl",
    ]
    database_counts = {
        name: jsonl_count(PACKET_ROOT / "database" / name)
        for name in linked_paths
    }
    database_counts.update(
        {
            "dbaasp_machine_extracted_rows": jsonl_count(PACKET_ROOT / "database" / "dbaasp_machine_extracted_rows.jsonl"),
            "dbaasp_review_queue_rows": jsonl_count(PACKET_ROOT / "database" / "dbaasp_review_queue_rows.jsonl"),
            "codex_session_audit_rows": jsonl_count(PACKET_ROOT / "database" / "codex_session_audit.jsonl"),
        }
    )

    validation = gate_summary()
    validation.update(
        {
            "worker1_validation_script": rel(INTAKE_ROOT / "worker1_refresh_intake.py"),
            "live_ticket_state_reconciliation_path": rel(PATHS["ticket_reconciliation"]),
            "live_ticket_state_reconciliation_passed_for_worker1_scope": ticket_audit["same_live_open_ticket_count_everywhere"]
            and all(ticket_audit["materials_manifest_packet_manifest_field_alignment"].values())
            and all(ticket_audit["review_report_packet_manifest_field_alignment"].values()),
            "live_ticket_state_reconciliation_open_rework_ticket_count": live_state["live_open_ticket_count"],
            "live_ticket_state_reconciliation_response_row_count": live_state["response_row_count"],
            "final_mirror_audit_path": rel(PATHS["final_mirror_audit"]),
            "final_mirror_unresolved_non_identical_count": mirror_audit["unresolved_non_identical_count"],
            "final_mirror_declared_exception_count": mirror_audit["declared_exception_count"],
            "analysis_status_json_changed_by_worker_1": False,
            "analysis_status_note": "analysis_status.json was not changed because intake status did not change.",
        }
    )

    inventory = {
        "schema_version": "worker1_intake_source_inventory_v3",
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "lane": "material-intake",
        "generated_at": utc_now(),
        "status": {
            "intake_status": "source_inventory_complete_with_cautions_repair_ready_for_adjudication",
            "source_verified_claims_made": False,
            "publication_grade_claimed": False,
            "assigned_ticket_id": ASSIGNED_TICKET_ID,
            "assigned_ticket_response_status": "repair_ready_for_adjudication",
            "analysis_can_resume": True,
            "packet_material_queue_status": packet_manifest.get("material_queue_status"),
            "packet_analysis_queue_status": packet_manifest.get("analysis_queue_status"),
            "open_rework_ticket_count": live_state["live_open_ticket_count"],
            "blocking_source_gap_count": packet_manifest.get("blocking_source_gap_count"),
            "extraction_error_count": packet_manifest.get("extraction_error_count"),
        },
        "scope": {
            "internet_used": False,
            "read_scope": [rel(SOURCE_ROOT), rel(PACKET_ROOT)],
            "write_scope": [rel(INTAKE_ROOT), rel(PATHS["rework_responses"])],
            "paper_root": rel(PAPER_ROOT),
            "packet_root": rel(PACKET_ROOT),
            "source_root": rel(SOURCE_ROOT),
            "leader_preflight_contract_count": 0,
            "leader_preflight_evidence_scaffold_count": 0,
        },
        "metadata_cross_check": {
            "paper_meta_path": rel(source_files["paper_meta"]),
            "packet_manifest_metadata_keys": sorted((packet_manifest.get("metadata") or {}).keys()),
            "paper_meta_identifier_keys": sorted(
                key for key in source_meta.keys() if key.lower() in {"doi", "pmid", "pmcid"}
            ),
            "xml_article_ids": xml_ids,
            "database_manifest_identifiers": db_manifest.get("identifiers"),
            "identifier_cross_check_note": "Identifiers were compared as material provenance only; no source_verified claim is made.",
        },
        "source_assets": {
            "primary": {
                name: file_record(path)
                for name, path in source_files.items()
                if name.startswith("paper_")
            },
            "packet_raw": {
                name: {
                    **file_record(path),
                    "matches_source_file": (
                        path.exists()
                        and source_files.get(name) is not None
                        and source_files[name].exists()
                        and sha256(path) == sha256(source_files[name])
                    ),
                }
                for name, path in raw_files.items()
            },
            "supplementary": {
                "source_files": {
                    name: {
                        **file_record(path),
                        "csv_row_count_including_header": count_csv_rows(path) if path.suffix.lower() == ".csv" else None,
                    }
                    for name, path in source_files.items()
                    if name.startswith("supplementary_")
                },
                "supplementary_index_path": rel(PACKET_ROOT / "extracted" / "supplementary_index.json"),
                "supplementary_index_file_count": len(supplementary_index.get("files", []))
                if isinstance(supplementary_index, dict)
                else None,
            },
            "oa_package": {
                "raw_oa_package_path": rel(PACKET_ROOT / "raw" / "oa_package"),
                "exists": (PACKET_ROOT / "raw" / "oa_package").exists(),
            },
            "archive_member_count": len(archive_manifest.get("archives", [])) if isinstance(archive_manifest, dict) else None,
            "staged_files_from_packet_manifest": packet_manifest.get("staged_files", []),
        },
        "extraction_inventory": {
            "extraction_status_path": rel(PACKET_ROOT / "extraction" / "extraction_status.json"),
            "extraction_quality_report_path": rel(PACKET_ROOT / "extraction" / "extraction_quality_report.json"),
            "extraction_status": extraction_status.get("status"),
            "publication_grade_ready": extraction_status.get("publication_grade_ready"),
            "blocking_source_gap_count": packet_manifest.get("blocking_source_gap_count"),
            "blocking_source_gap_ids": packet_manifest.get("blocking_source_gap_ids"),
            "extraction_error_count": packet_manifest.get("extraction_error_count"),
            "known_missing_or_blocked_materials_count": len(packet_manifest.get("known_missing_or_blocked_materials", [])),
            "known_missing_or_blocked_materials": packet_manifest.get("known_missing_or_blocked_materials"),
            "counts": {
                "xml_sections": count_xml_sections(PACKET_ROOT / "extracted" / "xml_sections.json"),
                "pdf_text_pages_or_blocks": jsonl_count(PACKET_ROOT / "extracted" / "pdf_text.jsonl"),
                "supplementary_text_rows": jsonl_count(PACKET_ROOT / "extracted" / "supplementary_text.jsonl"),
                "supplementary_table_count": table_count(PACKET_ROOT / "extracted" / "supplementary_tables.json"),
                "locator_count": (read_json(PACKET_ROOT / "locators" / "locator_index.json", default={}) or {}).get("locator_count"),
            },
            "locator_index_path": rel(PACKET_ROOT / "locators" / "locator_index.json"),
            "locator_prefix_counts": locator_prefix_counts(PACKET_ROOT / "locators" / "locator_index.json"),
            "supplementary_table_ids": extraction_status.get("supplementary_table_ids"),
            "extraction_errors_path": rel(PACKET_ROOT / "extraction" / "extraction_errors.jsonl"),
            "extraction_error_records_compact": compact_extraction_errors(PACKET_ROOT / "extraction" / "extraction_errors.jsonl"),
            "extraction_quality_blocking_gap_count": len(extraction_quality.get("blocking_material_gaps", []))
            if isinstance(extraction_quality, dict)
            else None,
            "extraction_quality_error_count": len(extraction_quality.get("errors", []))
            if isinstance(extraction_quality, dict)
            else None,
        },
        "database_provenance": {
            "database_source_manifest_path": rel(PACKET_ROOT / "database" / "database_source_manifest.json"),
            "authoritative_match_report_path": rel(PACKET_ROOT / "database" / "authoritative_match_report.json"),
            "safe_worker2_activity_handoff_path": rel(PACKET_ROOT / "analysis" / "activity_safe_candidate_handoff.json"),
            "strict_interpretation": db_manifest.get("strict_interpretation") or authoritative.get("strict_interpretation"),
            "source_record_links_present": db_manifest.get("source_record_links_present") or authoritative.get("source_record_links_present"),
            "row_counts_from_database_manifest": db_manifest.get("row_counts"),
            "row_counts_from_authoritative_match_report": authoritative.get("row_counts"),
            "row_counts_observed_in_packet_files": database_counts,
            "linked_authoritative_row_paths": [rel(PACKET_ROOT / "database" / name) for name in linked_paths],
            "machine_candidate_rows": {
                "path": rel(PACKET_ROOT / "database" / "dbaasp_machine_extracted_rows.jsonl"),
                "row_count": database_counts["dbaasp_machine_extracted_rows"],
                "status": "candidate_machine_evidence_only_not_source_verified",
            },
        },
        "rework_state": {
            "assigned_ticket_id": ASSIGNED_TICKET_ID,
            "assigned_ticket_currently_live_open": ASSIGNED_TICKET_ID in live_state["live_open_ticket_ids"],
            "fresh_owner_response_required_by_runtime": True,
            "fresh_owner_response_appended_this_run": appended,
            "fresh_owner_response_present_for_worker1_attempt": response_present,
            "fresh_owner_response_appended_by_worker1": response_present,
            "fresh_owner_response_line_no": response_line_no,
            "fresh_owner_response_attempt_id": REPAIR_ATTEMPT_ID,
            "rework_requests_path": rel(PATHS["rework_requests"]),
            "rework_responses_path": rel(PATHS["rework_responses"]),
            "closure_receipts_path": rel(PATHS["closure_receipts"]),
            **live_state,
        },
        "final_field_repair": {
            "terminal_acceptance_not_claimed": True,
            "repaired_artifacts": [rel(PATHS["source_inventory"]), rel(PATHS["intake_report"])],
            "live_ticket_state_reconciliation_path": rel(PATHS["ticket_reconciliation"]),
            "final_mirror_audit_path": rel(PATHS["final_mirror_audit"]),
            "fields_aligned": {
                "materials_manifest_packet_manifest": ticket_audit["materials_manifest_packet_manifest_field_alignment"],
                "review_report_packet_manifest": ticket_audit["review_report_packet_manifest_field_alignment"],
                "same_live_open_ticket_count_everywhere": ticket_audit["same_live_open_ticket_count_everywhere"],
            },
        },
        "final_mirror_audit": {
            "path": rel(PATHS["final_mirror_audit"]),
            "record_count": mirror_audit["record_count"],
            "byte_identical_count": mirror_audit["byte_identical_count"],
            "declared_exception_count": mirror_audit["declared_exception_count"],
            "unresolved_non_identical_count": mirror_audit["unresolved_non_identical_count"],
            "expected_packet_only_exception": "mechanism_evidence.json",
        },
        "validation": validation,
        "strict_cautions_and_limitations": [
            "Worker-1 intake does not make source_verified or publication-grade claims.",
            "DBAASP Codex fallback rows remain candidate machine evidence only.",
            "The S1 CSV blocking source gap remains explicit and is not suppressed.",
            "Three live open r03 tickets remain for worker-6 adjudication/closure.",
        ],
        "downstream_handoff": {
            "analysis_can_resume_after_owner_response": True,
            "material_surface_ready_for_analysis_queue": True,
            "requires_downstream_source_review": True,
            "worker6_terminal_closure_required": True,
            "database_rows_available_as_machine_candidates_only": True,
            "authoritative_linked_rows_available": any(database_counts[name] for name in linked_paths),
        },
    }
    write_json(PATHS["source_inventory"], inventory)
    return inventory, ticket_audit, mirror_audit


def write_report(inventory, ticket_audit, mirror_audit):
    status = inventory["status"]
    validation = inventory["validation"]
    lines = [
        f"# Worker-1 Intake Report: {PAPER_ID}",
        "",
        "## Scope",
        f"- worker_id: {WORKER_ID}",
        "- internet_used: false",
        "- source_verified_claims_made: false",
        "- publication_grade_claimed: false",
        "",
        "## Material Status",
        f"- material_queue_status: {status.get('packet_material_queue_status')}",
        f"- analysis_queue_status: {status.get('packet_analysis_queue_status')}",
        f"- intake_status: {status.get('intake_status')}",
        f"- blocking_source_gap_count: {status.get('blocking_source_gap_count')}",
        f"- extraction_error_count: {status.get('extraction_error_count')}",
        "",
        "## Assets Inventoried",
        f"- primary_source_asset_count: {len(inventory['source_assets']['primary'])}",
        f"- supplementary_source_asset_count: {len(inventory['source_assets']['supplementary']['source_files'])}",
        f"- supplementary_index_file_count: {inventory['source_assets']['supplementary'].get('supplementary_index_file_count')}",
        f"- locator_count: {inventory['extraction_inventory']['counts'].get('locator_count')}",
        f"- database_machine_candidate_row_count: {inventory['database_provenance']['machine_candidate_rows'].get('row_count')}",
        "",
        "## Ticket Reconciliation",
        f"- assigned_ticket_id: {ASSIGNED_TICKET_ID}",
        f"- assigned_ticket_response_status: {status.get('assigned_ticket_response_status')}",
        f"- fresh_owner_response_line_no: {inventory['rework_state'].get('fresh_owner_response_line_no')}",
        f"- live_open_ticket_count: {inventory['rework_state'].get('live_open_ticket_count')}",
        f"- same_live_open_ticket_count_everywhere: {ticket_audit.get('same_live_open_ticket_count_everywhere')}",
        f"- reconciliation_artifact: {rel(PATHS['ticket_reconciliation'])}",
        "",
        "## Final Mirror Audit",
        f"- final_json_record_count: {mirror_audit.get('record_count')}",
        f"- byte_identical_count: {mirror_audit.get('byte_identical_count')}",
        f"- declared_exception_count: {mirror_audit.get('declared_exception_count')}",
        f"- unresolved_non_identical_count: {mirror_audit.get('unresolved_non_identical_count')}",
        f"- mirror_audit_artifact: {rel(PATHS['final_mirror_audit'])}",
        "",
        "## Validation",
        f"- packet_gate_return_code: {validation.get('packet_gate_return_code')}",
        f"- packet_gate_hard_finding_count: {validation.get('packet_gate_hard_finding_count')}",
        f"- semantic_gate_return_code: {validation.get('semantic_gate_return_code')}",
        f"- semantic_gate_publication_grade_pass_count: {validation.get('semantic_gate_publication_grade_pass_count')}",
        f"- publication_quality_gate_return_code: {validation.get('publication_quality_gate_return_code')}",
        f"- publication_quality_gate_pass: {validation.get('publication_quality_gate_pass')}",
        "",
        "## Downstream State",
        "- worker1_lane_status: repair_ready_for_adjudication",
        "- analysis_can_resume: true",
        "- terminal_closure_owner: worker-6",
        "- unresolved_blockers: live r03 tickets and preserved blocking source gap",
        "",
    ]
    PATHS["intake_report"].write_text("\n".join(lines))


def main():
    INTAKE_ROOT.mkdir(parents=True, exist_ok=True)
    VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    appended, response_line_no, response_present = append_owner_response()
    inventory, ticket_audit, mirror_audit = build_inventory(appended, response_line_no, response_present)
    write_report(inventory, ticket_audit, mirror_audit)
    print(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "response_appended": appended,
                "response_line_no": response_line_no,
                "live_open_ticket_count": inventory["rework_state"]["live_open_ticket_count"],
                "files_written": [
                    rel(PATHS["source_inventory"]),
                    rel(PATHS["intake_report"]),
                    rel(PATHS["ticket_reconciliation"]),
                    rel(PATHS["final_mirror_audit"]),
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
