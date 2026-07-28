#!/usr/bin/env python3
"""Leader-owned field validator for the PMC11956232 terminal contract.

This validator is intentionally independent of worker-authored packet,
semantic, and publication gates.  It must not be weakened or replaced by a
worker.  It validates either worker-3's quantitative-figure handoff or the
final worker-6 adjudicated artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


PAPER_ID = "PMC11956232"
FIGURE_COUNTS = {
    "Figure 1": 360,
    "Figure 2": 280,
    "Figure 3": 20,
    "Figure 4": 98,
    "Figure 5": 18,
    "Figure 6": 17,
    "Figure 7": 4,
}
TERMINAL_FIGURE_STATUSES = {
    "source_reviewed_exhausted",
    "source_reviewed_terminal",
    "terminal_source_reviewed",
}
TERMINAL_NULL_STATUSES = {
    "source_reviewed_not_individually_resolvable_due_to_curve_overlap",
    "source_reviewed_not_individually_resolvable_due_to_occlusion",
    "source_reviewed_terminal_non_numeric",
}


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recursive_true_paths(value: Any, key: str, prefix: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for child_key, child in value.items():
            path = f"{prefix}.{child_key}"
            if child_key == key and child is True:
                found.append(path)
            found.extend(recursive_true_paths(child, key, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(recursive_true_paths(child, key, f"{prefix}[{index}]"))
    return found


def locator_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(locator_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(locator_text(item) for item in value.values())
    return ""


def figure_name(row: dict[str, Any]) -> str:
    raw = str(row.get("figure") or row.get("surface") or "").strip()
    lowered = raw.lower().replace(".", "")
    for number in range(1, 8):
        if lowered in {f"figure {number}", f"figure{number}", f"fig {number}", f"fig{number}"}:
            return f"Figure {number}"
    return raw


def source_reviewed(row: dict[str, Any]) -> bool:
    status = str(row.get("source_review_status") or row.get("review_status") or "").lower()
    return row.get("source_reviewed") is True or "source_reviewed" in status or "source_verified" in status


def numeric(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(float(value)) else None
    text = str(value).strip().lstrip("~≈<>≤≥ ")
    try:
        parsed = float(text)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    passed: bool,
    observed: Any,
    expected: Any,
    severity: str = "blocking",
) -> None:
    checks.append(
        {
            "check_id": check_id,
            "passed": bool(passed),
            "severity": severity,
            "observed": observed,
            "expected": expected,
        }
    )


def validate_figure_payload(
    payload: dict[str, Any], checks: list[dict[str, Any]], role: str
) -> list[dict[str, Any]]:
    observations = payload.get("figure_quantitative_observations")
    if not isinstance(observations, list):
        observations = []
    rows = [row for row in observations if isinstance(row, dict)]
    add_check(
        checks,
        f"{role}_figure_observation_total",
        len(rows) == sum(FIGURE_COUNTS.values()),
        len(rows),
        sum(FIGURE_COUNTS.values()),
    )

    ids = [str(row.get("observation_id") or "") for row in rows]
    add_check(
        checks,
        f"{role}_figure_observation_ids_unique",
        len(ids) == len(rows) and all(ids) and len(set(ids)) == len(ids),
        {"rows": len(rows), "nonempty_ids": sum(bool(item) for item in ids), "unique_ids": len(set(ids))},
        {"rows": len(rows), "nonempty_ids": len(rows), "unique_ids": len(rows)},
    )

    counts = {name: 0 for name in FIGURE_COUNTS}
    for row in rows:
        name = figure_name(row)
        if name in counts:
            counts[name] += 1
    for name, expected in FIGURE_COUNTS.items():
        add_check(
            checks,
            f"{role}_{name.lower().replace(' ', '_')}_count",
            counts[name] == expected,
            counts[name],
            expected,
        )

    invalid_source_review = [
        row.get("observation_id") for row in rows if not source_reviewed(row)
    ]
    add_check(
        checks,
        f"{role}_all_figure_rows_independently_source_reviewed",
        not invalid_source_review,
        invalid_source_review[:25],
        [],
    )
    missing_locator = [
        row.get("observation_id") for row in rows if not locator_text(row.get("source_locator"))
    ]
    add_check(
        checks,
        f"{role}_all_figure_rows_have_source_locator",
        not missing_locator,
        missing_locator[:25],
        [],
    )
    missing_precision = [
        row.get("observation_id")
        for row in rows
        if not str(row.get("exact_vs_approximate_status") or "").strip()
    ]
    add_check(
        checks,
        f"{role}_all_figure_rows_preserve_exact_vs_approximate_status",
        not missing_precision,
        missing_precision[:25],
        [],
    )

    figure12 = [row for row in rows if figure_name(row) in {"Figure 1", "Figure 2"}]
    terminal_null_issues: list[dict[str, Any]] = []
    for row in figure12:
        if row.get("raw_value") is not None:
            continue
        status = str(row.get("terminal_resolution_status") or "")
        if (
            status not in TERMINAL_NULL_STATUSES
            or row.get("numeric_value_not_fabricated") is not True
            or not str(row.get("missing_reason") or "").strip()
            or not source_reviewed(row)
        ):
            terminal_null_issues.append(
                {
                    "observation_id": row.get("observation_id"),
                    "terminal_resolution_status": status,
                    "numeric_value_not_fabricated": row.get("numeric_value_not_fabricated"),
                }
            )
    add_check(
        checks,
        f"{role}_figure12_nulls_have_terminal_source_disposition",
        not terminal_null_issues,
        terminal_null_issues[:25],
        [],
    )

    inventory = payload.get("figure_surface_exhaustion")
    inventory = inventory if isinstance(inventory, list) else []
    inventory_by_name = {
        figure_name(row): row for row in inventory if isinstance(row, dict)
    }
    inventory_issues: list[dict[str, Any]] = []
    for name, expected in FIGURE_COUNTS.items():
        row = inventory_by_name.get(name)
        if (
            row is None
            or str(row.get("status") or "") not in TERMINAL_FIGURE_STATUSES
            or row.get("expected_observation_count") != expected
            or row.get("observed_observation_count") != expected
            or row.get("source_reviewed_by") != "worker-3"
        ):
            inventory_issues.append({"figure": name, "row": row})
    add_check(
        checks,
        f"{role}_all_seven_figure_surfaces_terminally_exhausted",
        not inventory_issues,
        inventory_issues,
        [],
    )

    day7 = [row for row in rows if figure_name(row) == "Figure 7"]
    expected_day7 = {"pbs": 100.0, "control": 10.0, "1xmic": 80.0, "2xmic": 70.0}
    observed_day7: dict[str, float | None] = {}
    for row in day7:
        group = str(
            row.get("group")
            or row.get("series")
            or row.get("treatment")
            or row.get("condition")
            or ""
        ).lower()
        normalized_group = "".join(ch for ch in group if ch.isalnum())
        for key in expected_day7:
            if normalized_group == key:
                observed_day7[key] = numeric(row.get("raw_value"))
    add_check(
        checks,
        f"{role}_figure7_day7_plateaus",
        observed_day7 == expected_day7,
        observed_day7,
        expected_day7,
    )
    return rows


def validate_worker3(args: argparse.Namespace, checks: list[dict[str, Any]]) -> dict[str, Any]:
    payload = read_json(args.worker3_path)
    validate_figure_payload(payload, checks, "worker3")
    add_check(
        checks,
        "worker3_response_identity",
        payload.get("response_by") == "worker-3" or payload.get("worker_role") == "worker-3",
        {"response_by": payload.get("response_by"), "worker_role": payload.get("worker_role")},
        "worker-3",
    )
    add_check(
        checks,
        "worker3_independent_digitization_claim",
        payload.get("quantitative_figure_source_reviewed_independently") is True,
        payload.get("quantitative_figure_source_reviewed_independently"),
        True,
    )
    return {"worker3_path": str(args.worker3_path)}


def validate_layer2_payload(
    activity: dict[str, Any],
    contract: dict[str, Any],
    checks: list[dict[str, Any]],
    role: str,
) -> list[dict[str, Any]]:
    activity_records = activity.get("activity_records")
    activity_records = activity_records if isinstance(activity_records, list) else []
    expected_cells = {
        str(row.get("cell_locator")): (str(row.get("raw_value")), str(row.get("raw_unit")))
        for row in (contract.get("exact_table_contract") or {}).get("observations", [])
        if isinstance(row, dict)
    }
    observed_cells: dict[str, tuple[str, str]] = {}
    physical_cells: set[str] = set()
    for row in activity_records:
        if not isinstance(row, dict):
            continue
        locator = row.get("source_locator")
        locator = locator if isinstance(locator, dict) else {}
        semantic = str(locator.get("leader_preflight_cell_locator") or "")
        if semantic:
            observed_cells[semantic] = (str(row.get("raw_value")), str(row.get("raw_unit")))
        physical = str(locator.get("cell_locator") or "")
        if physical:
            physical_cells.add(physical)
    add_check(
        checks,
        f"{role}_exact_table_record_count",
        len(activity_records) == 40,
        len(activity_records),
        40,
    )
    add_check(
        checks,
        f"{role}_exact_table_semantic_cell_locators",
        len(observed_cells) == 40 and observed_cells == expected_cells,
        {
            "unique_semantic_cell_locators": len(observed_cells),
            "mismatched_cells": sorted(
                key for key in set(observed_cells) | set(expected_cells)
                if observed_cells.get(key) != expected_cells.get(key)
            ),
        },
        {"unique_semantic_cell_locators": 40, "mismatched_cells": []},
    )
    add_check(
        checks,
        f"{role}_exact_table_physical_cell_locators_unique",
        len(physical_cells) == 40,
        len(physical_cells),
        40,
    )

    figure_rows = validate_figure_payload(activity, checks, role)

    toxicity_records = activity.get("toxicity_records")
    toxicity_records = toxicity_records if isinstance(toxicity_records, list) else []
    quantitative_toxicity = []
    for row in toxicity_records:
        if not isinstance(row, dict):
            continue
        if numeric(row.get("raw_value")) is None:
            continue
        if "fig:6" in locator_text(row.get("source_locator")).lower() or "figure 6" in locator_text(
            row.get("source_locator")
        ).lower():
            quantitative_toxicity.append(row)
    add_check(
        checks,
        f"{role}_toxicity_records_include_all_14_peptide_bars",
        len(quantitative_toxicity) >= 14,
        len(quantitative_toxicity),
        "at least 14 Figure-6 peptide-treatment quantitative rows",
    )
    figure6 = [row for row in figure_rows if figure_name(row) == "Figure 6"]
    add_check(
        checks,
        f"{role}_figure6_complete_controls_and_treatments",
        len(figure6) == 17,
        len(figure6),
        17,
    )

    conflicts = activity.get("source_conflicts_preserved")
    conflicts = conflicts if isinstance(conflicts, list) else []
    conflict_ids = {
        str(row.get("id") or row.get("conflict_id") or "")
        for row in conflicts
        if isinstance(row, dict)
    }
    add_check(
        checks,
        f"{role}_source_conflicts_c1_c4_preserved",
        conflict_ids.issuperset(
            {
                "C1_temperature_method_table",
                "C2_serum_method_units",
                "C3_safety_threshold_wording",
                "C4_in_vivo_unassigned_range",
            }
        ),
        sorted(conflict_ids),
        [
            "C1_temperature_method_table",
            "C2_serum_method_units",
            "C3_safety_threshold_wording",
            "C4_in_vivo_unassigned_range",
        ],
    )
    add_check(
        checks,
        f"{role}_recursive_authority_boundary_false",
        not recursive_true_paths(activity, "authoritative_dbaasp_ingest_ready"),
        recursive_true_paths(activity, "authoritative_dbaasp_ingest_ready"),
        [],
    )
    return figure_rows


def validate_worker2(args: argparse.Namespace, checks: list[dict[str, Any]]) -> dict[str, Any]:
    activity = read_json(args.worker2_path)
    contract = read_json(args.contract_path)
    validate_layer2_payload(activity, contract, checks, "worker2")
    add_check(
        checks,
        "worker2_response_identity",
        activity.get("response_by") == "worker-2"
        or activity.get("worker") == "worker-2"
        or activity.get("worker_role") == "worker-2",
        {
            "response_by": activity.get("response_by"),
            "worker": activity.get("worker"),
            "worker_role": activity.get("worker_role"),
        },
        "worker-2",
    )
    return {"worker2_path": str(args.worker2_path)}


def validate_final(args: argparse.Namespace, checks: list[dict[str, Any]]) -> dict[str, Any]:
    activity = read_json(args.activity_path)
    mechanism = read_json(args.mechanism_path)
    database = read_json(args.database_path)
    review = read_json(args.review_path)
    contract = read_json(args.contract_path)

    validate_layer2_payload(activity, contract, checks, "final")

    claims = mechanism.get("mechanism_claims")
    claims = claims if isinstance(claims, list) else []
    fig3_direct = False
    fig4_direct_limited = False
    for row in claims:
        if not isinstance(row, dict):
            continue
        locators = locator_text(row.get("source_locator")).lower()
        evidence_class = str(row.get("evidence_class") or "")
        limitation = str(row.get("limitation_notes") or "").lower()
        if "fig:3" in locators and evidence_class == "direct_mechanism":
            fig3_direct = True
        if (
            "fig:4" in locators
            and evidence_class == "direct_mechanism"
            and any(token in limitation for token in ("does not", "not establish", "limitation"))
        ):
            fig4_direct_limited = True
    add_check(checks, "final_figure3_direct_membrane_evidence_preserved", fig3_direct, fig3_direct, True)
    add_check(
        checks,
        "final_figure4_lps_assay_preserved_with_limitation",
        fig4_direct_limited,
        fig4_direct_limited,
        True,
    )

    authority_true_paths = {
        "activity": recursive_true_paths(activity, "authoritative_dbaasp_ingest_ready"),
        "database": recursive_true_paths(database, "authoritative_dbaasp_ingest_ready"),
        "mechanism": recursive_true_paths(mechanism, "authoritative_dbaasp_ingest_ready"),
        "review": recursive_true_paths(review, "authoritative_dbaasp_ingest_ready"),
    }
    add_check(
        checks,
        "final_recursive_authority_boundary_false",
        not any(authority_true_paths.values()),
        authority_true_paths,
        {"activity": [], "database": [], "mechanism": [], "review": []},
    )
    add_check(
        checks,
        "final_review_terminal_status",
        review.get("review_status") in {"accepted_clean", "accepted_with_cautions"}
        and review.get("publication_grade") is True
        and not (review.get("rework_targets") or []),
        {
            "review_status": review.get("review_status"),
            "publication_grade": review.get("publication_grade"),
            "rework_target_count": len(review.get("rework_targets") or []),
        },
        {
            "review_status": "accepted_clean or accepted_with_cautions",
            "publication_grade": True,
            "rework_target_count": 0,
        },
    )

    mirror_pairs = [
        (args.activity_path, args.packet_root / "final/activity_toxicity_evidence.json"),
        (args.database_path, args.packet_root / "final/database_record_verification.json"),
        (args.mechanism_path, args.packet_root / "final/mechanism_ontology_record.json"),
        (args.review_path, args.packet_root / "final/review_report.json"),
    ]
    mirror_results = []
    for paper_path, packet_path in mirror_pairs:
        same = packet_path.exists() and sha256(paper_path) == sha256(packet_path)
        mirror_results.append(
            {
                "paper": str(paper_path),
                "packet": str(packet_path),
                "byte_identical": same,
            }
        )
    add_check(
        checks,
        "final_paper_packet_mirrors_byte_identical",
        all(row["byte_identical"] for row in mirror_results),
        mirror_results,
        "four byte-identical mirror pairs",
    )
    return {
        "activity_path": str(args.activity_path),
        "database_path": str(args.database_path),
        "mechanism_path": str(args.mechanism_path),
        "review_path": str(args.review_path),
    }


def main() -> int:
    script = Path(__file__).resolve()
    paper_root = script.parents[2]
    base = paper_root.parents[1]
    packet_root = base / "packets" / PAPER_ID
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("worker3", "worker2", "final"), default="final")
    parser.add_argument(
        "--worker3-path",
        type=Path,
        default=paper_root / "work/supplementary_methods/supplementary_evidence.json",
    )
    parser.add_argument(
        "--worker2-path",
        type=Path,
        default=paper_root / "work/activity_evidence/activity_records.json",
    )
    parser.add_argument(
        "--activity-path",
        type=Path,
        default=paper_root / "final/activity_toxicity_evidence.json",
    )
    parser.add_argument(
        "--database-path",
        type=Path,
        default=paper_root / "final/database_record_verification.json",
    )
    parser.add_argument(
        "--mechanism-path",
        type=Path,
        default=paper_root / "final/mechanism_ontology_record.json",
    )
    parser.add_argument(
        "--review-path",
        type=Path,
        default=paper_root / "final/review_report.json",
    )
    parser.add_argument(
        "--contract-path",
        type=Path,
        default=paper_root / "work/leader_preflight/source_surface_preflight_contract_20260726.json",
    )
    parser.add_argument("--packet-root", type=Path, default=packet_root)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    try:
        if args.mode == "worker3":
            inputs = validate_worker3(args, checks)
        elif args.mode == "worker2":
            inputs = validate_worker2(args, checks)
        else:
            inputs = validate_final(args, checks)
        exception = None
    except Exception as error:  # Keep a durable failure artifact on malformed outputs.
        inputs = {}
        exception = f"{type(error).__name__}: {error}"
        add_check(checks, "validator_execution", False, exception, "no exception")

    blocking_failures = [
        row["check_id"]
        for row in checks
        if not row["passed"] and row["severity"] == "blocking"
    ]
    report = {
        "paper_id": PAPER_ID,
        "validator": str(script),
        "validator_role": "leader_owned_independent_field_validator",
        "mode": args.mode,
        "passed": not blocking_failures,
        "blocking_failure_count": len(blocking_failures),
        "blocking_failure_ids": blocking_failures,
        "check_count": len(checks),
        "passed_check_count": sum(row["passed"] for row in checks),
        "inputs": inputs,
        "exception": exception,
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
