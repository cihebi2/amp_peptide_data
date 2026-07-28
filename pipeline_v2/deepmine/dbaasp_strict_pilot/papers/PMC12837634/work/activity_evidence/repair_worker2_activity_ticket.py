#!/usr/bin/env python3
"""Repair PMC12837634 worker-2 activity evidence for the assigned rework ticket.

The script reads only packet-local artifacts and source-derived fact summaries.
It does not print source passages or table text.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path("pipeline_v2/deepmine/dbaasp_strict_pilot")
PAPER_ID = "PMC12837634"
TICKET_ID = (
    "rwk-PMC12837634-campaign-r01-"
    "BF-PMC12837634-worker2-pseudomonas-botramp14-conflict-and-me"
)
PAPER = ROOT / "papers" / PAPER_ID
PACKET = ROOT / "packets" / PAPER_ID
WORK = PAPER / "work" / "activity_evidence"
OWNER_ACTIVITY = PACKET / "analysis" / "activity_toxicity_evidence.worker2.json"
WORK_ACTIVITY = WORK / "activity_records.json"
PAPER_FINAL_ACTIVITY = PAPER / "final" / "activity_toxicity_evidence.json"
PACKET_FINAL_ACTIVITY = PACKET / "final" / "activity_toxicity_evidence.json"
FACTS_PATH = WORK / "source_locator_fact_summary_no_passages.json"
VALIDATION_PATH = WORK / "worker2_pseudomonas_botramp14_ticket_validation.json"

P13 = "xml:p:13"
P16 = "xml:p:16"
MIC_METHOD = "xml:p:26"
MBC_METHOD = "xml:p:27"
TABLE = "xml:table-wrap:1"
CONFLICT_CELL = "xml:table-wrap:1:body-row=6:cell=3"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return out


def record_locator_ids(record: dict[str, Any]) -> set[str]:
    found: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, str):
            if value.startswith(("xml:", "pdf:", "supp:", "database:")):
                found.add(value)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)

    walk(record.get("source_locator"))
    walk(record.get("source_locators"))
    return found


def record_table_cell_locators(record: dict[str, Any]) -> list[str]:
    return sorted(
        loc
        for loc in record_locator_ids(record)
        if loc.startswith(TABLE + ":body-row=") and ":cell=" in loc
    )


def ensure_source_locator(record: dict[str, Any], locator: str, role: str, **extra: Any) -> None:
    source_locators = record.setdefault("source_locators", [])
    if not isinstance(source_locators, list):
        source_locators = []
        record["source_locators"] = source_locators
    for item in source_locators:
        if isinstance(item, dict) and item.get("locator") == locator and item.get("role") == role:
            item.update(extra)
            return
    payload = {"locator": locator, "role": role}
    payload.update(extra)
    source_locators.append(payload)


def method_locators_for(record: dict[str, Any], endpoint: str) -> list[str]:
    assay_conditions = record.setdefault("assay_conditions", {})
    if not isinstance(assay_conditions, dict):
        assay_conditions = {}
        record["assay_conditions"] = assay_conditions
    current = assay_conditions.get("method_locators") or []
    if not isinstance(current, list):
        current = [str(current)] if current else []
    current = [str(item) for item in current if str(item) != P16]
    if endpoint == "MIC":
        current.append(MIC_METHOD)
    elif endpoint == "MBC":
        current.append(MBC_METHOD)
    current.append(TABLE)
    current.extend(record_table_cell_locators(record))
    return ordered_unique(current)


def repair_payload(payload: dict[str, Any], now: str) -> dict[str, Any]:
    data = deepcopy(payload)
    method_rows_repaired = 0
    conflict_rows_repaired = 0

    for record in data.get("activity_records", []):
        if not isinstance(record, dict):
            continue
        endpoint = str(record.get("endpoint") or "")
        if endpoint in {"MIC", "MBC"}:
            before = list((record.get("assay_conditions") or {}).get("method_locators") or [])
            after = method_locators_for(record, endpoint)
            record["assay_conditions"]["method_locators"] = after
            if before != after:
                method_rows_repaired += 1

        locators = record_locator_ids(record)
        if endpoint in {"MIC", "MBC"} and CONFLICT_CELL in locators:
            conflict_rows_repaired += 1
            ensure_source_locator(
                record,
                P13,
                "primary_source_prose_conflict",
                conflict_type="prose_below_threshold_vs_table_exact_cell",
                paired_table_cell_locator=CONFLICT_CELL,
                conflict_value_summary={"operator": "below", "value": "0.78", "unit": "µM"},
            )
            ensure_source_locator(
                record,
                CONFLICT_CELL,
                "primary_source_table_cell_value",
                paired_prose_locator=P13,
            )
            record["source_review_status"] = "source_reviewed_conflict_preserved"
            record["raw_value_exactness"] = "source_conflict_table_exact_vs_prose_below_0.78_uM"
            record["normalization_status"] = "ambiguous"
            record["normalized_value"] = ""
            record["normalized_unit"] = ""
            record["normalization_note"] = (
                "Table cell raw value/unit preserved, but the same primary source also "
                "reports a below-threshold prose value; exact normalized interpretation "
                "is conflict-preserved rather than flattened."
            )
            record["source_conflict"] = {
                "status": "preserved_source_conflict",
                "conflict_type": "prose_below_threshold_vs_table_exact_cell",
                "prose_locator": P13,
                "table_cell_locator": CONFLICT_CELL,
                "prose_value_summary": {"operator": "below", "value": "0.78", "unit": "µM"},
                "table_value_summary": {"value": "0.78", "unit": "µM"},
                "curation_action": (
                    "retain the source table cell as the raw table observation while "
                    "marking exact interpretation ambiguous and preserving the prose conflict"
                ),
            }

    data["updated_at"] = now
    provenance = data.setdefault("source_review_provenance", {})
    if not isinstance(provenance, dict):
        provenance = {}
        data["source_review_provenance"] = provenance
    provenance["pseudomonas_botramp14_conflict_and_method_locator_repair"] = {
        "ticket_id": TICKET_ID,
        "reviewed_by": "worker-2",
        "reviewed_at": now,
        "source_text_printed_to_terminal": False,
        "source_locators_checked": [P13, CONFLICT_CELL, P16, MIC_METHOD, MBC_METHOD, "pdf:page=4"],
        "verification_artifact": str(VALIDATION_PATH),
        "disposition": "repair_ready_for_worker6_adjudication",
    }
    validation_artifacts = provenance.setdefault("validation_artifacts", [])
    if isinstance(validation_artifacts, list) and str(VALIDATION_PATH) not in validation_artifacts:
        validation_artifacts.append(str(VALIDATION_PATH))

    quality = data.setdefault("quality_checks", {})
    if not isinstance(quality, dict):
        quality = {}
        data["quality_checks"] = quality
    quality["pseudomonas_botramp14_conflict_and_method_locator_repair"] = {
        "ticket_id": TICKET_ID,
        "method_rows_repaired": method_rows_repaired,
        "conflict_rows_repaired": conflict_rows_repaired,
        "p13_conflict_locator_preserved": True,
        "table_cell_conflict_locator_preserved": True,
        "mic_method_locator": MIC_METHOD,
        "mbc_method_locator": MBC_METHOD,
        "removed_method_locator": P16,
        "validation_artifact": str(VALIDATION_PATH),
    }

    summary = data.setdefault("summary_counts", {})
    if isinstance(summary, dict):
        summary["activity_records"] = len(data.get("activity_records") or [])
        summary["toxicity_records"] = len(data.get("toxicity_records") or [])
        summary["pseudomonas_botramp14_conflict_rows_repaired"] = conflict_rows_repaired
        summary["mic_mbc_method_locator_rows_repaired"] = method_rows_repaired
        summary["mic_mbc_records_with_p16_method_locator_after_repair"] = 0

    notes = data.setdefault("notes", [])
    if isinstance(notes, list):
        note = (
            "Worker-2 repair preserves the P. aeruginosa BotrAMP14 prose/table value "
            "conflict with xml:p:13 plus xml:table-wrap:1:body-row=6:cell=3 and "
            "corrects MIC/MBC method provenance to xml:p:26/xml:p:27."
        )
        if note not in notes:
            notes.append(note)

    return data


def validate(payload: dict[str, Any], facts: dict[str, Any], artifact_label: str) -> dict[str, Any]:
    endpoint_counts = Counter()
    bad_status: list[str] = []
    direct_missing_normalized: list[str] = []
    mic_mbc_with_p16: list[str] = []
    mic_missing_p26: list[str] = []
    mbc_missing_p27: list[str] = []
    conflict_records: list[str] = []
    conflict_records_with_p13 = 0
    conflict_records_with_cell = 0
    allowed = {"direct", "converted", "not_convertible", "ambiguous"}

    for record in payload.get("activity_records", []):
        if not isinstance(record, dict):
            continue
        rid = str(record.get("record_id") or "")
        endpoint = str(record.get("endpoint") or "")
        endpoint_counts[endpoint] += 1
        status = str(record.get("normalization_status") or "")
        if status not in allowed:
            bad_status.append(rid)
        if status in {"direct", "converted"}:
            if not str(record.get("normalized_value") or "").strip() or not str(record.get("normalized_unit") or "").strip():
                direct_missing_normalized.append(rid)
        method_locators = (record.get("assay_conditions") or {}).get("method_locators") or []
        locators = record_locator_ids(record)
        if endpoint in {"MIC", "MBC"} and P16 in method_locators:
            mic_mbc_with_p16.append(rid)
        if endpoint == "MIC" and MIC_METHOD not in method_locators:
            mic_missing_p26.append(rid)
        if endpoint == "MBC" and MBC_METHOD not in method_locators:
            mbc_missing_p27.append(rid)
        if endpoint in {"MIC", "MBC"} and CONFLICT_CELL in locators:
            conflict_records.append(rid)
            if P13 in locators:
                conflict_records_with_p13 += 1
            if CONFLICT_CELL in locators:
                conflict_records_with_cell += 1

    fact_checks = {
        "all_required_locators_present": all(
            facts.get("locator_presence", {}).get(locator)
            for locator in [P13, P16, MIC_METHOD, MBC_METHOD, TABLE]
        ),
        "p13_mentions_below_0_78_uM": bool(
            facts.get("p13_conflict_indicators", {}).get("mentions_below_0_78_uM")
        ),
        "p16_is_not_mic_mbc_method": bool(
            facts.get("p16_role_indicators", {}).get("mentions_time_kill_keywords")
        ),
        "p26_supports_mic_method": bool(
            facts.get("p26_role_indicators", {}).get("mentions_MIC_method_keywords")
        ),
        "p27_supports_mbc_method": bool(
            facts.get("p27_role_indicators", {}).get("mentions_MBC_method_keywords")
        ),
    }
    checks = {
        "normalization_status_allowed_values_only": not bad_status,
        "direct_or_converted_rows_have_normalized_value_and_unit": not direct_missing_normalized,
        "no_mic_or_mbc_method_locator_xml_p16": not mic_mbc_with_p16,
        "all_mic_rows_cite_xml_p26": not mic_missing_p26,
        "all_mbc_rows_cite_xml_p27": not mbc_missing_p27,
        "conflict_records_have_required_locators": bool(conflict_records)
        and conflict_records_with_p13 == len(conflict_records)
        and conflict_records_with_cell == len(conflict_records),
        "p13_conflict_and_method_fact_checks": all(fact_checks.values()),
    }
    return {
        "paper_id": PAPER_ID,
        "ticket_id": TICKET_ID,
        "artifact_label": artifact_label,
        "checked_artifacts": [str(OWNER_ACTIVITY), str(WORK_ACTIVITY), str(FACTS_PATH)],
        "endpoint_counts": dict(sorted(endpoint_counts.items())),
        "activity_record_count": len(payload.get("activity_records") or []),
        "toxicity_record_count": len(payload.get("toxicity_records") or []),
        "conflict_record_count": len(conflict_records),
        "conflict_record_ids": conflict_records,
        "fact_checks": fact_checks,
        "checks": checks,
        "failure_counts": {
            "bad_normalization_status": len(bad_status),
            "direct_missing_normalized": len(direct_missing_normalized),
            "mic_mbc_with_p16_method": len(mic_mbc_with_p16),
            "mic_missing_p26": len(mic_missing_p26),
            "mbc_missing_p27": len(mbc_missing_p27),
        },
        "pass": all(checks.values()),
    }


def main() -> None:
    facts = load_json(FACTS_PATH)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    owner = load_json(OWNER_ACTIVITY)
    repaired = repair_payload(owner, now)
    write_json(OWNER_ACTIVITY, repaired)
    write_json(WORK_ACTIVITY, repaired)
    final_validations: dict[str, Any] = {}
    for label, path in (
        ("paper_final_activity", PAPER_FINAL_ACTIVITY),
        ("packet_final_activity", PACKET_FINAL_ACTIVITY),
    ):
        if path.exists():
            final_payload = repair_payload(load_json(path), now)
            write_json(path, final_payload)
            final_validations[label] = validate(final_payload, facts, label)
    validation = validate(repaired, facts, "worker2_owner_activity")
    if final_validations:
        validation["final_mirror_validations"] = final_validations
        validation["final_mirrors_pass"] = all(item.get("pass") for item in final_validations.values())
    write_json(VALIDATION_PATH, validation)
    print("wrote", OWNER_ACTIVITY.as_posix())
    print("wrote", WORK_ACTIVITY.as_posix())
    if PAPER_FINAL_ACTIVITY.exists():
        print("wrote", PAPER_FINAL_ACTIVITY.as_posix())
    if PACKET_FINAL_ACTIVITY.exists():
        print("wrote", PACKET_FINAL_ACTIVITY.as_posix())
    print("wrote", VALIDATION_PATH.as_posix())
    print("pass", validation["pass"])


if __name__ == "__main__":
    main()
