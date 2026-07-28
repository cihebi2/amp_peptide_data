#!/usr/bin/env python3
"""Repair worker-2 SD10 strain conflict metadata for PMC12125351."""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


PAPER_ID = "PMC12125351"
WORKER_ID = "worker-2"
TICKET_ID = "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W2-SD10-STRAIN-CONFLICT-METADATA"

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[7]
BASE = REPO_ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot"
PAPER_ROOT = BASE / "papers" / PAPER_ID
PACKET_ROOT = BASE / "packets" / PAPER_ID
WORK_DIR = PAPER_ROOT / "work/activity_evidence"

WORK_ACTIVITY = WORK_DIR / "activity_records.json"
ANALYSIS_WORKER2 = PACKET_ROOT / "analysis/activity_toxicity_evidence.worker2.json"
PAPER_FINAL = PAPER_ROOT / "final/activity_toxicity_evidence.json"
PACKET_FINAL = PACKET_ROOT / "final/activity_toxicity_evidence.json"
LOCATOR_INDEX = PACKET_ROOT / "locators/locator_index.json"
REWORK_RESPONSES = PACKET_ROOT / "rework/rework_responses.jsonl"
XLSX_PATH = PAPER_ROOT / "source/supplementary/42003_2025_8282_MOESM2_ESM.xlsx"

ARTIFACT_PATHS = [WORK_ACTIVITY, ANALYSIS_WORKER2, PAPER_FINAL, PACKET_FINAL]
HEADER_LOCATOR = "supp:42003_2025_8282_MOESM2_ESM.xlsx:sheet=Supplementary Data 10:row=2:cell=E2"
COLUMN_E_LOCATOR = "supp:42003_2025_8282_MOESM2_ESM.xlsx:sheet=Supplementary Data 10:column=E"
XML_VALUE_PROVENANCE_LOCATORS = ["xml:p:25", "xml:caption:4"]

SD10_E_LOC_RE = re.compile(
    r"^supp:42003_2025_8282_MOESM2_ESM\.xlsx:sheet=Supplementary Data 10:row=(?P<row>\d+):cell=E(?P=row)$"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    return [value]


def add_unique(values: list[Any], item: Any) -> list[Any]:
    if item not in values:
        values.append(item)
    return values


def sd10_column_e_row(record: dict[str, Any]) -> int | None:
    match = SD10_E_LOC_RE.match(str(record.get("source_locator", "")))
    if not match:
        return None
    row = int(match.group("row"))
    if 3 <= row <= 11 and record.get("endpoint") == "MIC":
        return row
    return None


def values_equal(a: Any, b: Any) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return float(a) == float(b)
    return str(a) == str(b)


def locator_ids(locator_index: dict[str, Any]) -> set[str]:
    locators = locator_index.get("locators", locator_index)
    ids: set[str] = set()
    if isinstance(locators, list):
        for entry in locators:
            if not isinstance(entry, dict):
                continue
            for key in ("locator", "id", "source_locator"):
                value = entry.get(key)
                if isinstance(value, str):
                    ids.add(value)
    elif isinstance(locators, dict):
        ids.update(locators)
    return ids


def add_missing_workbook_locator(locator_index: dict[str, Any], locator: str, preview: Any) -> bool:
    ids = locator_ids(locator_index)
    if locator in ids:
        return False
    locators = locator_index.setdefault("locators", [])
    if not isinstance(locators, list):
        raise TypeError("locator_index locators must be a list for this repair")
    locators.append(
        {
            "locator": locator,
            "preview": "" if preview is None else str(preview),
            "source": "extracted/supplementary_tables.json",
            "tag": "xlsx-cell",
        }
    )
    locator_index["locator_count"] = len(locator_ids(locator_index))
    locator_index["updated_at"] = now_iso()
    summary = locator_index.setdefault("workbook_locator_summary", {})
    if isinstance(summary, dict):
        summary["worker2_sd10_strain_conflict_repair_added_locators"] = sorted(
            set(summary.get("worker2_sd10_strain_conflict_repair_added_locators", [])) | {locator}
        )
    return True


def explicit_or_indexed(locator: str, ids: set[str]) -> bool:
    return locator in ids or locator.startswith(("xml:", "pdf:", "database:"))


def filter_locators(values: list[Any], ids: set[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        if value == COLUMN_E_LOCATOR:
            continue
        if explicit_or_indexed(value, ids):
            add_unique(out, value)
    return out


def repair_object(obj: dict[str, Any], repaired_at: str, header_label: str, source_values: dict[int, Any], ids: set[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    obj = deepcopy(obj)
    affected_ids: list[str] = []
    value_mismatch_ids: list[str] = []
    unresolved_after_repair: dict[str, list[str]] = {}

    for record in obj.get("activity_records", []):
        row_num = sd10_column_e_row(record)
        if row_num is None:
            continue

        record_id = str(record.get("record_id", ""))
        affected_ids.append(record_id)
        if not values_equal(record.get("raw_value"), source_values[row_num]):
            value_mismatch_ids.append(record_id)

        existing_supporting = ensure_list(record.get("supporting_source_locators"))
        supporting = filter_locators(existing_supporting, ids)
        for locator in [HEADER_LOCATOR, str(record.get("source_locator", "")), *XML_VALUE_PROVENANCE_LOCATORS]:
            if explicit_or_indexed(locator, ids):
                add_unique(supporting, locator)
        record["supporting_source_locators"] = supporting

        existing_conflicts = ensure_list(record.get("source_conflicts"))
        value_provenance_locators = filter_locators(
            [
                *XML_VALUE_PROVENANCE_LOCATORS,
                *[
                    loc
                    for conflict in existing_conflicts
                    if isinstance(conflict, dict)
                    for loc in ensure_list(conflict.get("value_provenance_locators"))
                ],
            ],
            ids,
        )
        leader_hint_locators = filter_locators(
            [
                loc
                for conflict in existing_conflicts
                if isinstance(conflict, dict)
                for loc in ensure_list(conflict.get("leader_hint_locators_checked"))
            ],
            ids,
        )
        contrasting_locators = filter_locators(
            [
                loc
                for conflict in existing_conflicts
                if isinstance(conflict, dict)
                for loc in ensure_list(conflict.get("contrasting_label_candidate_locators"))
            ],
            ids,
        )

        record["raw_endpoint_label"] = header_label
        record["target_strain_or_isolate"] = "ATCC 29213"
        record["target_strain_or_isolate_source"] = "value_provenance_interpretation_with_preserved_source_label_conflict"
        record["source_reported_target_strain_or_isolate"] = "ATCC 25923"
        record["value_provenance_target_strain_or_isolate"] = "ATCC 29213"
        record["target_strain_conflict_status"] = "source_conflict_preserved"
        record["source_conflicts"] = [
            {
                "assigned_value": "ATCC 29213",
                "assigned_value_basis": "value_provenance_interpretation",
                "caution": "Source label and value-provenance target assignment conflict is preserved for worker-6 adjudication.",
                "conflict_type": "target_strain_label_value_provenance_divergence",
                "field": "target_strain_or_isolate",
                "leader_hint_locators_checked": leader_hint_locators,
                "source_label_locator": HEADER_LOCATOR,
                "source_label_value": "ATCC 25923",
                "source_reported_target_strain_or_isolate": "ATCC 25923",
                "status": "source_conflict_preserved",
                "value_provenance_locators": value_provenance_locators,
                "value_provenance_match_status": "source_basis_preserved_for_worker6_adjudication",
                "value_provenance_target_strain_or_isolate": "ATCC 29213",
                "contrasting_label_candidate_locators": contrasting_locators,
            }
        ]
        record["source_review_status"] = "source_reviewed_worker_repair_ready_for_adjudication"
        record["source_reviewed_at"] = repaired_at
        record["worker2_ticket_repair"] = {
            "fields_repaired": [
                "raw_endpoint_label",
                "source_reported_target_strain_or_isolate",
                "source_conflicts.source_label_locator",
                "source_conflicts.source_label_value",
                "supporting_source_locators",
                "target_strain_or_isolate_source",
                "target_strain_conflict_status",
            ],
            "repair_status": "repair_ready_for_adjudication",
            "repaired_at": repaired_at,
            "source_basis_locators": [HEADER_LOCATOR, str(record.get("source_locator", "")), *value_provenance_locators],
            "ticket_id": TICKET_ID,
        }

        row_locators = [str(record.get("source_locator", "")), *record["supporting_source_locators"]]
        for conflict in record["source_conflicts"]:
            row_locators.append(str(conflict.get("source_label_locator", "")))
            row_locators.extend(ensure_list(conflict.get("value_provenance_locators")))
            row_locators.extend(ensure_list(conflict.get("leader_hint_locators_checked")))
            row_locators.extend(ensure_list(conflict.get("contrasting_label_candidate_locators")))
        unresolved = [loc for loc in row_locators if isinstance(loc, str) and loc.startswith("supp:") and not explicit_or_indexed(loc, ids)]
        if unresolved:
            unresolved_after_repair[record_id] = sorted(set(unresolved))

    validation_artifacts = ensure_list(obj.get("validation_artifacts"))
    for rel_path in [
        "papers/PMC12125351/work/activity_evidence/worker2_sd10_strain_conflict_repair_validation.json",
        "papers/PMC12125351/work/activity_evidence/worker2_sd10_strain_conflict_locator_checks.json",
        "papers/PMC12125351/work/activity_evidence/worker2_sd10_strain_conflict_mirror_consistency.json",
    ]:
        add_unique(validation_artifacts, rel_path)

    obj["reviewed_at"] = repaired_at
    obj["updated_at"] = repaired_at
    obj["source_review_status"] = "source_reviewed_worker_repair_ready_for_adjudication"
    obj["publication_grade_claim"] = False
    obj["publication_grade_rationale"] = (
        "Worker-2 repaired the assigned SD10 strain-conflict metadata; terminal publication-grade closure "
        "requires a fresh worker-6 adjudication and strict gate pass."
    )
    obj["worker2_rework_response_status"] = "repair_ready_for_adjudication"
    obj["worker2_ticket_repair_summary"] = {
        "analysis_can_resume": True,
        "affected_activity_record_count": len(affected_ids),
        "raw_value_mismatch_count": len(value_mismatch_ids),
        "repaired_at": repaired_at,
        "supplementary_data_10_column_e_header_locator": HEADER_LOCATOR,
        "ticket_id": TICKET_ID,
        "unresolved_locator_record_count": len(unresolved_after_repair),
    }
    obj["validation_artifacts"] = validation_artifacts

    return obj, {
        "affected_record_ids": affected_ids,
        "value_mismatch_ids": value_mismatch_ids,
        "unresolved_after_repair": unresolved_after_repair,
    }


def row_source_locators(record: dict[str, Any]) -> list[str]:
    locators: list[str] = []
    for key in ("source_locator", "source_label_locator"):
        value = record.get(key)
        if isinstance(value, str):
            locators.append(value)
    locators.extend([loc for loc in ensure_list(record.get("supporting_source_locators")) if isinstance(loc, str)])
    for conflict in ensure_list(record.get("source_conflicts")):
        if not isinstance(conflict, dict):
            continue
        for key in ("source_locator", "source_label_locator"):
            value = conflict.get(key)
            if isinstance(value, str):
                locators.append(value)
        for key in ("supporting_source_locators", "value_provenance_locators", "leader_hint_locators_checked", "contrasting_label_candidate_locators"):
            locators.extend([loc for loc in ensure_list(conflict.get(key)) if isinstance(loc, str)])
    return locators


def validate_repaired(obj: dict[str, Any], header_label: str, source_values: dict[int, Any], ids: set[str]) -> dict[str, Any]:
    activity = obj.get("activity_records", [])
    toxicity = obj.get("toxicity_records", [])
    affected = [(idx, record, sd10_column_e_row(record)) for idx, record in enumerate(activity) if sd10_column_e_row(record) is not None]
    affected_checks: list[dict[str, Any]] = []
    normalization_bad_ids: list[str] = []
    direct_conflict_ids: list[str] = []
    concentration_conflict_ids: list[str] = []

    for record in activity + toxicity:
        record_id = record.get("record_id")
        status = record.get("normalization_status")
        if status not in {"direct", "converted", "not_convertible", "ambiguous"}:
            normalization_bad_ids.append(record_id)
        if status in {"direct", "converted"} and ("normalized_value" not in record or "normalized_unit" not in record):
            normalization_bad_ids.append(record_id)
        if status == "direct" and (record.get("normalized_value") != record.get("raw_value") or record.get("normalized_unit") != record.get("raw_unit")):
            direct_conflict_ids.append(record_id)
        assay_conditions = record.get("assay_conditions") or {}
        if "concentration" in record or "concentration_unit" in record:
            if (
                record.get("concentration") != assay_conditions.get("peptide_concentration")
                or record.get("concentration_unit") != assay_conditions.get("peptide_concentration_unit")
            ):
                concentration_conflict_ids.append(record_id)

    for index, record, row_num in affected:
        assert row_num is not None
        locators = row_source_locators(record)
        conflicts = [item for item in ensure_list(record.get("source_conflicts")) if isinstance(item, dict)]
        conflict_text = " ".join(
            str(value)
            for conflict in conflicts
            for value in conflict.values()
            if not isinstance(value, (dict, list))
        )
        unresolved = sorted(
            set(
                loc
                for loc in locators
                if isinstance(loc, str)
                and loc.startswith("supp:")
                and not explicit_or_indexed(loc, ids)
            )
        )
        affected_checks.append(
            {
                "activity_index": index,
                "record_id": record.get("record_id"),
                "conflict_metadata_contains_ATCC_25923": "ATCC 25923" in conflict_text,
                "conflict_metadata_contains_ATCC_29213": "ATCC 29213" in conflict_text,
                "has_column_E_locator": COLUMN_E_LOCATOR in locators,
                "has_header_locator_E2": HEADER_LOCATOR in locators,
                "normalization_status": record.get("normalization_status"),
                "raw_endpoint_label_matches_header_cell": record.get("raw_endpoint_label") == header_label,
                "raw_value_matches_workbook_cell": values_equal(record.get("raw_value"), source_values[row_num]),
                "source_locator": record.get("source_locator"),
                "source_reported_target_strain_or_isolate": record.get("source_reported_target_strain_or_isolate"),
                "target_strain_or_isolate": record.get("target_strain_or_isolate"),
                "unresolved_locator_count": len(unresolved),
                "unresolved_locators": unresolved,
                "value_provenance_target_strain_or_isolate": record.get("value_provenance_target_strain_or_isolate"),
            }
        )

    return {
        "activity_record_count": len(activity),
        "toxicity_record_count": len(toxicity),
        "affected_sd10_column_e_record_count": len(affected),
        "affected_checks": affected_checks,
        "all_affected_rows_pass": all(
            item["conflict_metadata_contains_ATCC_25923"]
            and item["conflict_metadata_contains_ATCC_29213"]
            and not item["has_column_E_locator"]
            and item["has_header_locator_E2"]
            and item["raw_endpoint_label_matches_header_cell"]
            and item["raw_value_matches_workbook_cell"]
            and item["source_reported_target_strain_or_isolate"] == "ATCC 25923"
            and item["target_strain_or_isolate"] == "ATCC 29213"
            and item["unresolved_locator_count"] == 0
            and item["value_provenance_target_strain_or_isolate"] == "ATCC 29213"
            for item in affected_checks
        ),
        "normalization_bad_count": len(set(normalization_bad_ids)),
        "normalization_bad_record_ids": sorted(set(normalization_bad_ids)),
        "direct_conversion_conflict_count": len(direct_conflict_ids),
        "direct_conversion_conflict_record_ids": direct_conflict_ids,
        "concentration_conflict_count": len(concentration_conflict_ids),
        "concentration_conflict_record_ids": concentration_conflict_ids,
    }


def append_rework_response(repaired_at: str, validation_path: Path, locator_path: Path, mirror_path: Path) -> None:
    response = {
        "analysis_can_resume": True,
        "artifacts_written": [
            validation_path.relative_to(REPO_ROOT).as_posix(),
            locator_path.relative_to(REPO_ROOT).as_posix(),
            mirror_path.relative_to(REPO_ROOT).as_posix(),
        ],
        "evidence": [
            {
                "check": "assigned SD10 column E strain-conflict rows",
                "status": "nine_rows_repaired_with_header_cell_locator_and_preserved_value_provenance_conflict",
            },
            {
                "check": "source-cell and locator validation",
                "status": "raw_values_match_workbook_cells_and_affected_supporting_locators_resolve",
            },
            {
                "check": "mirror validation",
                "status": "paper_work_packet_worker2_and_final_activity_toxicity_artifacts_byte_identical",
            },
        ],
        "evidence_paths": [
            validation_path.relative_to(REPO_ROOT).as_posix(),
            locator_path.relative_to(REPO_ROOT).as_posix(),
            mirror_path.relative_to(REPO_ROOT).as_posix(),
        ],
        "paper_id": PAPER_ID,
        "reason": "Repaired the runtime-open worker-2 SD10 strain-conflict metadata ticket using packet-local workbook/XML locators.",
        "repaired_artifacts": [path.relative_to(REPO_ROOT).as_posix() for path in ARTIFACT_PATHS],
        "response_by": WORKER_ID,
        "response_status": "repair_ready_for_adjudication",
        "responded_at": repaired_at,
        "ticket_id": TICKET_ID,
        "validation_artifacts": [
            validation_path.relative_to(REPO_ROOT).as_posix(),
            locator_path.relative_to(REPO_ROOT).as_posix(),
            mirror_path.relative_to(REPO_ROOT).as_posix(),
        ],
        "notes": "Nonterminal owner response only; worker-6 must perform fresh adjudication before any terminal closure.",
    }
    with REWORK_RESPONSES.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(response, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    repaired_at = now_iso()
    wb = load_workbook(XLSX_PATH, data_only=True, read_only=True)
    ws10 = wb["Supplementary Data 10"]
    header_label = str(ws10["E2"].value)
    if "ATCC 25923" not in header_label:
        raise RuntimeError("SD10 E2 header did not contain the expected source-reported strain token")
    source_values = {row: ws10[f"E{row}"].value for row in range(3, 12)}

    locator_index = load_json(LOCATOR_INDEX)
    added_locator_ids: list[str] = []
    ws3 = wb["Supplementary Data 3"]
    n9_locator = "supp:42003_2025_8282_MOESM2_ESM.xlsx:sheet=Supplementary Data 3:row=9:cell=N9"
    if add_missing_workbook_locator(locator_index, n9_locator, ws3["N9"].value):
        added_locator_ids.append(n9_locator)
        write_json(LOCATOR_INDEX, locator_index)
    ids = locator_ids(locator_index)
    wb.close()

    if HEADER_LOCATOR not in ids:
        raise RuntimeError("SD10 E2 header locator is not indexed")
    missing_data_locators = [
        f"supp:42003_2025_8282_MOESM2_ESM.xlsx:sheet=Supplementary Data 10:row={row}:cell=E{row}"
        for row in range(3, 12)
        if f"supp:42003_2025_8282_MOESM2_ESM.xlsx:sheet=Supplementary Data 10:row={row}:cell=E{row}" not in ids
    ]
    if missing_data_locators:
        raise RuntimeError("SD10 data cell locators are not fully indexed")

    canonical = load_json(PAPER_FINAL)
    repaired, repair_summary = repair_object(canonical, repaired_at, header_label, source_values, ids)
    validation = validate_repaired(repaired, header_label, source_values, ids)
    validation.update(
        {
            "all_ticket_acceptance_checks_passed": (
                validation["activity_record_count"] == 130
                and validation["toxicity_record_count"] == 126
                and validation["affected_sd10_column_e_record_count"] == 9
                and validation["all_affected_rows_pass"]
                and validation["normalization_bad_count"] == 0
                and validation["direct_conversion_conflict_count"] == 0
                and validation["concentration_conflict_count"] == 0
            ),
            "artifact_role": "worker2_sd10_strain_conflict_repair_validation",
            "paper_id": PAPER_ID,
            "repair_summary": repair_summary,
            "ticket_id": TICKET_ID,
            "validated_at": repaired_at,
        }
    )
    if not validation["all_ticket_acceptance_checks_passed"]:
        validation_path = WORK_DIR / "worker2_sd10_strain_conflict_repair_validation.json"
        write_json(validation_path, validation)
        raise RuntimeError("repair validation failed")

    for path in ARTIFACT_PATHS:
        write_json(path, repaired)

    mirror_hashes = {
        path.relative_to(REPO_ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in ARTIFACT_PATHS
    }
    mirror = {
        "all_activity_toxicity_artifacts_byte_identical": len(set(mirror_hashes.values())) == 1,
        "artifact_role": "worker2_sd10_strain_conflict_mirror_consistency",
        "hashes": mirror_hashes,
        "paper_id": PAPER_ID,
        "ticket_id": TICKET_ID,
        "validated_at": repaired_at,
    }
    locator_validation = {
        "added_locator_ids": added_locator_ids,
        "affected_source_label_locator": HEADER_LOCATOR,
        "artifact_role": "worker2_sd10_strain_conflict_locator_checks",
        "column_level_locator_removed": True,
        "indexed_data_cell_locator_count": 9,
        "paper_id": PAPER_ID,
        "ticket_id": TICKET_ID,
        "validated_at": repaired_at,
    }

    validation_path = WORK_DIR / "worker2_sd10_strain_conflict_repair_validation.json"
    locator_path = WORK_DIR / "worker2_sd10_strain_conflict_locator_checks.json"
    mirror_path = WORK_DIR / "worker2_sd10_strain_conflict_mirror_consistency.json"
    write_json(validation_path, validation)
    write_json(locator_path, locator_validation)
    write_json(mirror_path, mirror)
    if not mirror["all_activity_toxicity_artifacts_byte_identical"]:
        raise RuntimeError("activity/toxicity mirrors are not byte-identical")

    append_rework_response(repaired_at, validation_path, locator_path, mirror_path)
    print(
        json.dumps(
            {
                "affected_rows": validation["affected_sd10_column_e_record_count"],
                "locator_index_added": len(added_locator_ids),
                "mirror_identical": mirror["all_activity_toxicity_artifacts_byte_identical"],
                "response_appended": True,
                "validation_pass": validation["all_ticket_acceptance_checks_passed"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
