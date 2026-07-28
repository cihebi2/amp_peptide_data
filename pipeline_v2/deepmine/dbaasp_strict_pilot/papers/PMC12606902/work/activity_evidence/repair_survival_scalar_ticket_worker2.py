#!/usr/bin/env python3
"""Focused worker-2 repair for the current survival-scalar rework ticket.

The script keeps terminal output to counts/paths only. It does not emit source
passages; source XML is read only to build boolean/token locator audits.
"""

from __future__ import annotations

import copy
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "PMC12606902"
WORKER_ID = "worker-2"
TICKET_ID = "rwk-PMC12606902-campaign-r02-BF-PMC12606902-W2-UNSUPPORTED-IN-VIVO-SURVIVAL-SCALARS"

REPO_ROOT = Path(__file__).resolve().parents[7]
PAPER_ROOT = REPO_ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot/papers" / PAPER_ID
PACKET_ROOT = REPO_ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot/packets" / PAPER_ID
WORK_DIR = PAPER_ROOT / "work/activity_evidence"

PAPER_XML = PAPER_ROOT / "source/paper.xml"
LOCATOR_INDEX = PACKET_ROOT / "locators/locator_index.json"
REWORK_RESPONSES = PACKET_ROOT / "rework/rework_responses.jsonl"

ACTIVITY_PATHS = [
    PAPER_ROOT / "work/activity_evidence/activity_records.json",
    PACKET_ROOT / "analysis/activity_toxicity_evidence.worker2.json",
    PAPER_ROOT / "final/activity_toxicity_evidence.json",
    PACKET_ROOT / "final/activity_toxicity_evidence.json",
]
PAPER_FINAL_ACTIVITY = PAPER_ROOT / "final/activity_toxicity_evidence.json"
PACKET_FINAL_ACTIVITY = PACKET_ROOT / "final/activity_toxicity_evidence.json"
REVIEW_PATHS = [
    PAPER_ROOT / "final/review_report.json",
    PACKET_ROOT / "final/review_report.json",
]

SURVIVAL_AUDIT_PATH = WORK_DIR / "survival_scalar_ticket_locator_audit.worker2.json"
LOCATOR_AUDIT_PATH = WORK_DIR / "final_locator_integrity.worker2_survival_ticket.json"
VALIDATION_PATH = WORK_DIR / "current_ticket_acceptance_validation.worker2.json"
WRITE_SUMMARY_PATH = WORK_DIR / "survival_scalar_ticket_repair_write_summary.worker2.json"
ONE_PAPER_MANIFEST = WORK_DIR / "worker2_single_paper_manifest.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def local_name(elem: ET.Element) -> str:
    return elem.tag.rsplit("}", 1)[-1]


def compact_text(elem: ET.Element) -> str:
    return re.sub(r"\s+", " ", " ".join(elem.itertext())).strip()


def xml_locator_texts() -> dict[str, str]:
    root = ET.parse(PAPER_XML).getroot()
    out: dict[str, str] = {}
    counters: Counter[str] = Counter()
    for elem in root.iter():
        name = local_name(elem)
        if name not in {"p", "fig", "sec", "table-wrap"}:
            continue
        counters[name] += 1
        locator_name = {"table-wrap": "table-wrap"}.get(name, name)
        out[f"xml:{locator_name}:{counters[name]}"] = compact_text(elem)
    return out


def percent_token_flags(text: str, values: list[str]) -> dict[str, Any]:
    lower = text.lower()
    flags: dict[str, Any] = {
        "percent_values_present": sorted(set(re.findall(r"([<>~]?\s*\d+(?:\.\d+)?)\s*%", text))),
        "contains_confidence_interval_token": bool(re.search(r"confidence\s+interval|\bci\b", lower)),
        "contains_log_rank_or_p_value_token": bool(re.search(r"log[- ]?rank|p\s*[<=>]", lower)),
        "contains_survival_token": bool(re.search(r"surviv|survival", lower)),
        "value_contexts": {},
    }
    for value in values:
        contexts: list[dict[str, bool]] = []
        for match in re.finditer(re.escape(value) + r"\s*%", text):
            start = max(0, match.start() - 120)
            end = min(len(text), match.end() + 120)
            window = text[start:end].lower()
            contexts.append(
                {
                    "near_confidence_interval_token": bool(re.search(r"confidence\s+interval|\bci\b", window)),
                    "near_log_rank_or_p_value_token": bool(re.search(r"log[- ]?rank|p\s*[<=>]", window)),
                    "near_survival_token": bool(re.search(r"surviv|survival", window)),
                    "accepted_as_exact_survival_endpoint": bool(
                        re.search(r"surviv|survival", window)
                        and not re.search(r"confidence\s+interval|\bci\b|log[- ]?rank|p\s*[<=>]", window)
                    ),
                }
            )
        flags["value_contexts"][value] = contexts
    return flags


def build_survival_source_audit() -> dict[str, Any]:
    locator_text = xml_locator_texts()
    requested = ["xml:p:56", "xml:p:59", "xml:fig:9", "xml:fig:10"]
    locators: dict[str, Any] = {}
    for locator in requested:
        text = locator_text.get(locator, "")
        locators[locator] = {
            "locator_resolved": bool(text),
            "source_text_not_emitted": True,
            "token_audit": percent_token_flags(text, ["90", "95"]),
        }
    return {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "ticket_id": TICKET_ID,
        "generated_at": utc_now(),
        "source_text_not_emitted": True,
        "locators": locators,
        "worker2_interpretation": {
            "xml_fig_9_exact_95_survival_endpoint_supported": False,
            "xml_fig_10_exact_95_survival_endpoint_supported": False,
            "xml_p_59_exact_90_survival_endpoint_retained": True,
            "confidence_interval_text_not_endpoint_value": True,
        },
    }


def has_digitized_or_approximate_provenance(row: dict[str, Any]) -> bool:
    blob = json.dumps(row, ensure_ascii=False).lower()
    return any(token in blob for token in ("digitized", "approximate", "curve coordinate", "panel coordinate"))


def is_unsupported_survival_95_row(row: dict[str, Any]) -> bool:
    raw_value = str(row.get("raw_value") or "").strip().rstrip("%")
    raw_unit = str(row.get("raw_unit") or "").strip()
    endpoint = str(row.get("endpoint") or "").strip().lower()
    locator = str(row.get("source_locator") or "")
    return (
        endpoint == "host survival"
        and raw_value == "95"
        and raw_unit == "%"
        and locator in {"xml:fig:9", "xml:fig:10"}
        and not has_digitized_or_approximate_provenance(row)
    )


def update_summary_counts(artifact: dict[str, Any]) -> dict[str, int]:
    activity_records = artifact.get("activity_records") if isinstance(artifact.get("activity_records"), list) else []
    toxicity_records = artifact.get("toxicity_records") if isinstance(artifact.get("toxicity_records"), list) else []
    activity_exclusions = artifact.get("activity_exclusions") if isinstance(artifact.get("activity_exclusions"), list) else []
    toxicity_exclusions = artifact.get("toxicity_exclusions") if isinstance(artifact.get("toxicity_exclusions"), list) else []
    counts = {
        "activity_exclusions": len(activity_exclusions),
        "activity_records": len(activity_records),
        "in_vivo_activity_records": sum(1 for row in activity_records if row.get("evidence_ladder") == "in_vivo_tested"),
        "mic_activity_records": sum(1 for row in activity_records if str(row.get("endpoint") or "").upper() == "MIC"),
        "toxicity_exclusions": len(toxicity_exclusions),
        "toxicity_records": len(toxicity_records),
    }
    artifact["summary_counts"] = counts
    return counts


def direct_rows_have_normalized_values(artifact: dict[str, Any]) -> bool:
    for bucket in ("activity_records", "toxicity_records"):
        for row in artifact.get(bucket, []):
            if row.get("normalization_status") in {"direct", "converted"}:
                if row.get("normalized_value") in (None, "") or row.get("normalized_unit") in (None, ""):
                    return False
    return True


def normalization_statuses_valid(artifact: dict[str, Any]) -> bool:
    allowed = {"direct", "converted", "not_convertible", "ambiguous"}
    return all(
        row.get("normalization_status") in allowed
        for bucket in ("activity_records", "toxicity_records")
        for row in artifact.get(bucket, [])
    )


def repair_activity_artifact(base: dict[str, Any], now: str, survival_audit: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    artifact = copy.deepcopy(base)
    original_records = artifact.get("activity_records", [])
    removed = [row for row in original_records if is_unsupported_survival_95_row(row)]
    artifact["activity_records"] = [row for row in original_records if not is_unsupported_survival_95_row(row)]
    counts = update_summary_counts(artifact)
    artifact["owner_repair_applied_at"] = now
    artifact["owner_repair_applied_by"] = WORKER_ID
    artifact["requires_fresh_worker6_adjudication"] = True
    artifact["publication_grade_claim"] = False
    artifact["lane_status"] = "repair_ready_for_worker6_adjudication"
    artifact["generated_at"] = now
    artifact.setdefault("verification_artifacts", {})["survival_scalar_ticket_locator_audit"] = rel(SURVIVAL_AUDIT_PATH)
    artifact.setdefault("verification_artifacts", {})["locator_integrity_audit"] = rel(LOCATOR_AUDIT_PATH)
    artifact.setdefault("verification_artifacts", {})["current_ticket_acceptance_validation"] = rel(VALIDATION_PATH)
    artifact.setdefault("adjudication_contract_audits", {})[TICKET_ID] = {
        "ticket_id": TICKET_ID,
        "worker_id": WORKER_ID,
        "checked_at": now,
        "status": "repair_ready_for_adjudication",
        "removed_activity_records": [
            {
                "record_id": row.get("record_id"),
                "endpoint": row.get("endpoint"),
                "raw_value": row.get("raw_value"),
                "raw_unit": row.get("raw_unit"),
                "source_locator": row.get("source_locator"),
            }
            for row in removed
        ],
        "retained_source_supported_activity_records": [
            {
                "record_id": row.get("record_id"),
                "endpoint": row.get("endpoint"),
                "raw_value": row.get("raw_value"),
                "raw_unit": row.get("raw_unit"),
                "source_locator": row.get("source_locator"),
            }
            for row in artifact["activity_records"]
            if row.get("endpoint") == "host survival" and row.get("source_locator") == "xml:p:59"
        ],
        "confidence_interval_text_not_used_as_endpoint_value": True,
        "validation_artifact": rel(VALIDATION_PATH),
    }
    artifact.setdefault("quality_checks", {})["survival_scalar_ticket_contract"] = {
        "unsupported_fig9_fig10_exact_95_rows_removed": len(removed) == 2,
        "xml_p59_90_survival_row_retained": any(
            row.get("endpoint") == "host survival"
            and str(row.get("raw_value")) == "90"
            and row.get("raw_unit") == "%"
            and row.get("source_locator") == "xml:p:59"
            for row in artifact["activity_records"]
        ),
        "direct_rows_have_normalized_value_unit": direct_rows_have_normalized_values(artifact),
        "normalization_status_allowed": normalization_statuses_valid(artifact),
        "activity_record_count_after_repair": counts["activity_records"],
    }
    scope = artifact.setdefault("source_review_scope", {})
    if isinstance(scope, dict):
        checked = scope.setdefault("bounded_review_artifacts", [])
        if isinstance(checked, list):
            for item in (rel(SURVIVAL_AUDIT_PATH), rel(LOCATOR_AUDIT_PATH), rel(VALIDATION_PATH)):
                if item not in checked:
                    checked.append(item)
    return artifact, removed


def collect_locator_values(payload: Any, path: str = "$") -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            next_path = f"{path}.{key}"
            normalized = str(key).lower()
            if normalized in {"source_locator", "cell_locator", "locator", "table_locator"} and isinstance(value, str) and value.strip():
                found.append({"json_path": next_path, "field": str(key), "locator": value.strip()})
            elif normalized == "source_locators" and isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, str) and item.strip():
                        found.append({"json_path": f"{next_path}[{idx}]", "field": str(key), "locator": item.strip()})
            found.extend(collect_locator_values(value, next_path))
    elif isinstance(payload, list):
        for idx, value in enumerate(payload):
            found.extend(collect_locator_values(value, f"{path}[{idx}]"))
    return found


def xml_locator_counts() -> dict[str, int]:
    root = ET.parse(PAPER_XML).getroot()
    counts: Counter[str] = Counter()
    for elem in root.iter():
        name = local_name(elem)
        if name in {"p", "fig", "sec", "table-wrap"}:
            counts[name] += 1
    return dict(counts)


def load_indexed_locators() -> set[str]:
    data = read_json(LOCATOR_INDEX)
    return {
        str(item.get("locator"))
        for item in data.get("locators", [])
        if isinstance(item, dict) and str(item.get("locator") or "").strip()
    }


def classify_locator(locator: str, indexed: set[str], xml_counts: dict[str, int]) -> dict[str, Any]:
    if locator in indexed:
        return {"review_status": "indexed_exact", "exact_vs_approximate": "exact_indexed_locator", "accepted": True}
    table_match = re.match(r"^(xml:table-wrap:(\d+))(?::.*)?$", locator)
    if table_match and table_match.group(1) in indexed:
        return {
            "review_status": "accepted_validated_coordinate",
            "exact_vs_approximate": "exact_table_coordinate_or_table_child_locator",
            "accepted": True,
        }
    xml_match = re.match(r"^xml:(p|fig|sec|table-wrap):(\d+)(?::.*)?$", locator)
    if xml_match:
        elem_name = xml_match.group(1)
        idx = int(xml_match.group(2))
        if idx <= int(xml_counts.get(elem_name, 0)):
            return {
                "review_status": "accepted_validated_xml_locator",
                "exact_vs_approximate": "exact_xml_locator",
                "accepted": True,
            }
    if locator.startswith("supp:"):
        supp_root = PACKET_ROOT / "raw/supplementary_original"
        source_name = locator.split(":", 2)[1] if ":" in locator else ""
        if source_name and (supp_root / source_name).exists():
            return {
                "review_status": "accepted_validated_supplement_locator",
                "exact_vs_approximate": "exact_supplement_file_locator",
                "accepted": True,
            }
    return {"review_status": "unreviewed_or_unindexed", "exact_vs_approximate": "unresolved", "accepted": False}


def build_locator_audit(artifact: dict[str, Any], now: str) -> dict[str, Any]:
    indexed = load_indexed_locators()
    counts = xml_locator_counts()
    occurrences = collect_locator_values(artifact)
    by_locator: dict[str, dict[str, Any]] = {}
    for occurrence in occurrences:
        locator = occurrence["locator"]
        item = by_locator.setdefault(
            locator,
            {
                "locator": locator,
                "occurrence_count": 0,
                "fields": sorted(set()),
                "sample_json_paths": [],
            },
        )
        item["occurrence_count"] += 1
        item["fields"] = sorted(set(item["fields"]) | {occurrence["field"]})
        if len(item["sample_json_paths"]) < 5:
            item["sample_json_paths"].append(occurrence["json_path"])
    locator_rows: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for locator, item in sorted(by_locator.items()):
        status = classify_locator(locator, indexed, counts)
        row = {**item, **status}
        locator_rows.append(row)
        if not status["accepted"]:
            unresolved.append(row)
    return {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "ticket_id": TICKET_ID,
        "generated_at": now,
        "source_text_not_emitted": True,
        "locator_field_occurrence_count": len(occurrences),
        "unique_locator_count": len(locator_rows),
        "unreviewed_or_unindexed_count": len(unresolved),
        "unreviewed_or_unindexed_locators": unresolved,
        "locators": locator_rows,
    }


def update_review_report(base: dict[str, Any], activity: dict[str, Any], now: str) -> dict[str, Any]:
    report = copy.deepcopy(base)
    final_counts = dict(report.get("final_counts") or {})
    final_counts["activity_records"] = len(activity.get("activity_records", []))
    final_counts["toxicity_records"] = len(activity.get("toxicity_records", []))
    report["updated_at"] = now
    report["publication_grade"] = False
    report["validator_contract_passed"] = False
    report["review_status"] = "needs_targeted_rework"
    report["adjudication_summary"] = (
        "Worker-2 repaired the layer-2 survival-scalar ticket; final publication-grade status is pending fresh worker-6 adjudication."
    )
    target = {
        "worker": "worker-6",
        "layer": "adjudication",
        "artifact_path": rel(PAPER_ROOT / "final/review_report.json"),
        "failure_type": "fresh_worker6_adjudication_required",
        "source_evidence_to_check": [
            rel(PAPER_ROOT / "final/activity_toxicity_evidence.json"),
            rel(PACKET_ROOT / "final/activity_toxicity_evidence.json"),
            rel(SURVIVAL_AUDIT_PATH),
            rel(LOCATOR_AUDIT_PATH),
            rel(VALIDATION_PATH),
        ],
        "required_action": "Fresh worker-6 strict adjudication of the worker-2 survival-scalar repair before any terminal closure.",
        "acceptance_check": "Only worker-6 may append closed_repaired for the current runtime-open ticket after strict validation.",
    }
    report["rework_targets"] = [target]
    final_counts["review_rework_targets"] = len(report["rework_targets"])
    report["final_counts"] = final_counts
    strict_gate = dict(report.get("strict_gate") or {})
    strict_gate["required_rework_count"] = 1
    strict_gate["runtime_open_ticket_ids_reviewed"] = [TICKET_ID]
    strict_gate["gate_artifact_paths"] = sorted(
        set(strict_gate.get("gate_artifact_paths") or [])
        | {rel(SURVIVAL_AUDIT_PATH), rel(LOCATOR_AUDIT_PATH), rel(VALIDATION_PATH)}
    )
    report["strict_gate"] = strict_gate
    sem = dict(report.get("semantic_quality_checks") or {})
    sem["hard_rework_targets_remaining"] = True
    sem["ticket_contract_checked"] = True
    sem["current_worker2_ticket_repair_ready"] = True
    report["semantic_quality_checks"] = sem
    checked_inputs = report.setdefault("checked_inputs", [])
    if isinstance(checked_inputs, list):
        for item in (rel(SURVIVAL_AUDIT_PATH), rel(LOCATOR_AUDIT_PATH), rel(VALIDATION_PATH)):
            if item not in checked_inputs:
                checked_inputs.append(item)
    return report


def validate_repair(activity: dict[str, Any], removed: list[dict[str, Any]], locator_audit: dict[str, Any], now: str) -> dict[str, Any]:
    rows = activity.get("activity_records", [])
    unsupported_remaining = [
        {
            "record_id": row.get("record_id"),
            "endpoint": row.get("endpoint"),
            "raw_value": row.get("raw_value"),
            "raw_unit": row.get("raw_unit"),
            "source_locator": row.get("source_locator"),
        }
        for row in rows
        if is_unsupported_survival_95_row(row)
    ]
    p59_rows = [
        row
        for row in rows
        if row.get("endpoint") == "host survival"
        and str(row.get("raw_value") or "") == "90"
        and row.get("raw_unit") == "%"
        and row.get("source_locator") == "xml:p:59"
    ]
    final_counts_match = True
    review_counts: dict[str, Any] = {}
    for path in REVIEW_PATHS:
        report = read_json(path)
        fc = report.get("final_counts") or {}
        review_counts[rel(path)] = fc
        if fc.get("activity_records") != len(activity.get("activity_records", [])):
            final_counts_match = False
        if fc.get("toxicity_records") != len(activity.get("toxicity_records", [])):
            final_counts_match = False
        if fc.get("review_rework_targets") != len(report.get("rework_targets") or []):
            final_counts_match = False
    paper_packet_activity_identical = PAPER_FINAL_ACTIVITY.read_bytes() == PACKET_FINAL_ACTIVITY.read_bytes()
    paper_packet_review_identical = REVIEW_PATHS[0].read_bytes() == REVIEW_PATHS[1].read_bytes()
    issues: list[dict[str, Any]] = []
    if len(removed) not in {0, 2}:
        issues.append({"code": "unexpected_removed_row_count", "count": len(removed)})
    if unsupported_remaining:
        issues.append({"code": "unsupported_95_rows_remaining", "count": len(unsupported_remaining)})
    if len(p59_rows) != 1:
        issues.append({"code": "xml_p59_90_survival_row_count_not_one", "count": len(p59_rows)})
    if not final_counts_match:
        issues.append({"code": "review_final_counts_mismatch"})
    if not paper_packet_activity_identical:
        issues.append({"code": "paper_packet_activity_final_not_byte_identical"})
    if not paper_packet_review_identical:
        issues.append({"code": "paper_packet_review_final_not_byte_identical"})
    if locator_audit.get("unreviewed_or_unindexed_count") != 0:
        issues.append({"code": "unreviewed_or_unindexed_locators", "count": locator_audit.get("unreviewed_or_unindexed_count")})
    if not direct_rows_have_normalized_values(activity):
        issues.append({"code": "direct_or_converted_rows_missing_normalized_fields"})
    if not normalization_statuses_valid(activity):
        issues.append({"code": "invalid_normalization_status"})
    return {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "ticket_id": TICKET_ID,
        "generated_at": now,
        "status": "pass" if not issues else "fail",
        "overall_issue_count": len(issues),
        "issues": issues,
        "validated_paths": [rel(path) for path in ACTIVITY_PATHS + REVIEW_PATHS],
        "path_results": {
            "activity_record_count": len(activity.get("activity_records", [])),
            "toxicity_record_count": len(activity.get("toxicity_records", [])),
            "removed_unsupported_activity_record_count": len(removed),
            "unsupported_95_rows_previously_or_currently_removed": len(unsupported_remaining) == 0,
            "unsupported_95_rows_remaining": unsupported_remaining,
            "xml_p59_90_host_survival_row_count": len(p59_rows),
            "final_counts_match_live_json": final_counts_match,
            "review_final_counts": review_counts,
            "paper_packet_activity_final_byte_identical": paper_packet_activity_identical,
            "paper_packet_review_final_byte_identical": paper_packet_review_identical,
            "unreviewed_or_unindexed_locator_count": locator_audit.get("unreviewed_or_unindexed_count"),
            "normalization_status_values": sorted(
                {
                    row.get("normalization_status")
                    for bucket in ("activity_records", "toxicity_records")
                    for row in activity.get(bucket, [])
                }
            ),
        },
    }


def append_rework_response(validation: dict[str, Any], removed: list[dict[str, Any]], now: str) -> None:
    response = {
        "ticket_id": TICKET_ID,
        "response_status": "repair_ready_for_adjudication",
        "response_by": WORKER_ID,
        "analysis_can_resume": True,
        "paper_id": PAPER_ID,
        "created_at": now,
        "reason": (
            "Verified/repaired the current activity artifact so unsupported exact 95% host-survival rows tied to figure confidence-interval locators are absent, "
            "the source-supported xml:p:59 90% host-survival row is retained, final counts are refreshed, and locator integrity validation is written."
        ),
        "evidence": {
            "removed_unsupported_activity_record_count": len(removed),
            "activity_record_count_after_repair": validation["path_results"]["activity_record_count"],
            "toxicity_record_count_after_repair": validation["path_results"]["toxicity_record_count"],
            "xml_p59_90_host_survival_row_count": validation["path_results"]["xml_p59_90_host_survival_row_count"],
            "unreviewed_or_unindexed_locator_count": validation["path_results"]["unreviewed_or_unindexed_locator_count"],
            "validation_issue_count": validation["overall_issue_count"],
        },
        "evidence_paths": [rel(SURVIVAL_AUDIT_PATH), rel(LOCATOR_AUDIT_PATH), rel(VALIDATION_PATH)],
        "repaired_artifacts": [rel(path) for path in ACTIVITY_PATHS + REVIEW_PATHS],
        "artifacts_written": [rel(path) for path in ACTIVITY_PATHS + REVIEW_PATHS + [SURVIVAL_AUDIT_PATH, LOCATOR_AUDIT_PATH, VALIDATION_PATH, WRITE_SUMMARY_PATH]],
        "added_files": [rel(Path(__file__)), rel(SURVIVAL_AUDIT_PATH), rel(LOCATOR_AUDIT_PATH), rel(VALIDATION_PATH), rel(WRITE_SUMMARY_PATH)],
        "validation_artifacts": [rel(VALIDATION_PATH)],
        "notes": "Nonterminal owner repair response only; fresh worker-6 adjudication is required before terminal closure.",
    }
    append_jsonl(REWORK_RESPONSES, response)


def main() -> int:
    now = utc_now()
    survival_audit = build_survival_source_audit()
    write_json(SURVIVAL_AUDIT_PATH, survival_audit)

    base = read_json(PAPER_FINAL_ACTIVITY)
    repaired, removed = repair_activity_artifact(base, now, survival_audit)
    for path in ACTIVITY_PATHS:
        write_json(path, repaired)

    locator_audit = build_locator_audit(repaired, now)
    write_json(LOCATOR_AUDIT_PATH, locator_audit)

    review_base = read_json(REVIEW_PATHS[0])
    review = update_review_report(review_base, repaired, now)
    for path in REVIEW_PATHS:
        write_json(path, review)

    write_json(ONE_PAPER_MANIFEST, {"paper_ids": [PAPER_ID]})

    validation = validate_repair(repaired, removed, locator_audit, now)
    write_json(VALIDATION_PATH, validation)
    append_rework_response(validation, removed, now)

    summary = {
        "paper_id": PAPER_ID,
        "ticket_id": TICKET_ID,
        "removed_unsupported_activity_record_count": len(removed),
        "activity_record_count_after_repair": len(repaired.get("activity_records", [])),
        "toxicity_record_count_after_repair": len(repaired.get("toxicity_records", [])),
        "validation_issue_count": validation["overall_issue_count"],
        "artifacts_written": [
            rel(ACTIVITY_PATHS[0]),
            rel(ACTIVITY_PATHS[1]),
            rel(ACTIVITY_PATHS[2]),
            rel(ACTIVITY_PATHS[3]),
            rel(VALIDATION_PATH),
        ],
    }
    write_json(WRITE_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if validation["overall_issue_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
