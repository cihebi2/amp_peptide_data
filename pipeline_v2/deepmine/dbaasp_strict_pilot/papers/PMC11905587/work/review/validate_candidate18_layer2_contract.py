#!/usr/bin/env python3
"""Validate the leader-owned PMC11905587 worker-2 repair contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EXPECTED_SEQUENCE = "MTPFWRAVGNKPVGAYCQQGLECTTKVCRRRHCSFLQHNWS"
EXPECTED_POSITIVE_ROWS = {
    3: ("Shigella flexneri", "ATCC12022", "3.125"),
    4: ("Vibrio alginolyticus", "ATCC17749", "3.125"),
    5: ("Salmonella enterica", "ATCC13076", "6.25"),
    11: ("Staphylococcus aureus", "ATCC6538", "50"),
    12: ("Staphylococcus warneri", "ATCC49454", "100"),
}
EXPECTED_NO_ACTIVITY_ROWS = {
    6: ("Proteus mirabilis", "ATCC25933"),
    7: ("Aeromonas hydrophila", "ATCC7966"),
    8: ("Pseudomonas aeruginosa", "ATCC27853"),
    9: ("Escherichia coli", "K12"),
    13: ("Staphylococcus saprophyticus", "ATCC49907"),
    14: ("Listeria monocytogenes", "ATCC19115"),
}


def compact(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def normalized(value: Any) -> str:
    return re.sub(r"\s+", "", compact(value)).lower().replace("×", "x")


def locator_row(value: Any) -> int | None:
    match = re.search(r"(?:body-?row|row)\s*[=:]\s*(\d+)", compact(value), re.I)
    return int(match.group(1)) if match else None


def contains_all(value: Any, terms: list[str]) -> bool:
    text = normalized(value)
    return all(normalized(term) in text for term in terms)


def conflict_items(payload: dict[str, Any]) -> list[Any]:
    items: list[Any] = []
    for key, value in payload.items():
        if "conflict" not in key.lower() and "caution" not in key.lower():
            continue
        if isinstance(value, list):
            items.extend(value)
        elif isinstance(value, dict):
            items.append(value)
    return items


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    activity = payload.get("activity_records")
    toxicity = payload.get("toxicity_records")
    exclusions = payload.get("excluded_non_activity_table_entries")
    activity = activity if isinstance(activity, list) else []
    toxicity = toxicity if isinstance(toxicity, list) else []
    exclusions = exclusions if isinstance(exclusions, list) else []

    checks: dict[str, bool] = {
        "activity_records_count_is_5": len(activity) == 5,
        "toxicity_records_count_is_0": len(toxicity) == 0,
    }

    seen_positive_rows: dict[int, tuple[str, str, str]] = {}
    identity_ok = True
    assay_context_ok = True
    replication_ok = True
    structured_inoculum_not_unreported = True
    no_machine_gt1000_primary = True

    for record in activity:
        if not isinstance(record, dict):
            identity_ok = assay_context_ok = replication_ok = False
            continue
        row = locator_row(record.get("source_locator")) or locator_row(record.get("source_locator_detail"))
        if row is not None:
            seen_positive_rows[row] = (
                compact(record.get("target_species")),
                compact(record.get("target_strain_or_isolate") or record.get("target_isolate")),
                compact(record.get("raw_value")),
            )

        entity = record.get("entity")
        identity_ok &= isinstance(entity, dict)
        identity_ok &= contains_all(record.get("sample"), ["QsLEAP2", "mature peptide"])
        identity_ok &= contains_all(record.get("treatment"), ["QsLEAP2", "mature peptide"])
        identity_ok &= isinstance(entity, dict) and contains_all(entity, ["QsLEAP2", "mature peptide"])
        identity_ok &= isinstance(entity, dict) and EXPECTED_SEQUENCE in compact(entity)

        conditions = record.get("assay_conditions")
        conditions = conditions if isinstance(conditions, dict) else {}
        inoculum = normalized(conditions.get("inoculum"))
        assay_context_ok &= "cfu/ml" in inoculum and "10" in inoculum and "5" in inoculum
        unreported_fields = conditions.get("not_reported_or_not_structured_fields")
        unreported_fields = unreported_fields if isinstance(unreported_fields, list) else []
        structured_inoculum_not_unreported &= "inoculum" not in {
            normalized(field) for field in unreported_fields
        }
        assay_context_ok &= contains_all(conditions.get("incubation_time"), ["24", "h"])
        assay_context_ok &= "od600" in normalized(conditions)

        replication_surface = {
            "assay_conditions": conditions,
            "statistics": record.get("statistics"),
            "replication": record.get("replication"),
        }
        replication_ok &= contains_all(
            replication_surface,
            ["triplicate", "independent biological repeat"],
        )

        raw_value = normalized(record.get("raw_value"))
        evidence_role = normalized(record.get("evidence_role"))
        if ">1000" in raw_value and ("primary" in evidence_role or "source" in evidence_role):
            no_machine_gt1000_primary = False

    checks["all_activity_rows_bind_QsLEAP2_name_and_exact_41aa_sequence"] = identity_ok
    checks["all_activity_rows_preserve_inoculum_OD600_and_24h"] = assay_context_ok
    checks["all_activity_rows_preserve_triplicates_and_independent_repeats"] = replication_ok
    checks["structured_inoculum_is_not_listed_as_unreported"] = structured_inoculum_not_unreported
    checks["machine_gt1000_promoted_as_primary_count_is_0"] = no_machine_gt1000_primary

    expected_positive_ok = set(seen_positive_rows) == set(EXPECTED_POSITIVE_ROWS)
    if expected_positive_ok:
        for row, expected in EXPECTED_POSITIVE_ROWS.items():
            observed = seen_positive_rows[row]
            expected_positive_ok &= normalized(observed[0]) == normalized(expected[0])
            expected_positive_ok &= normalized(observed[1]) == normalized(expected[1])
            expected_positive_ok &= normalized(observed[2]) == normalized(expected[2])
    checks["five_positive_rows_match_table1_cells"] = expected_positive_ok

    seen_negative_rows: dict[int, tuple[str, str, str]] = {}
    for item in exclusions:
        if not isinstance(item, dict):
            continue
        row = locator_row(item.get("source_locator")) or locator_row(item.get("locator"))
        raw = compact(item.get("raw_value") if "raw_value" in item else item.get("raw_table_value"))
        if row in EXPECTED_NO_ACTIVITY_ROWS and raw.strip() == "-":
            seen_negative_rows[row] = (
                compact(item.get("target_species") or item.get("target")),
                compact(item.get("target_strain_or_isolate") or item.get("target_isolate") or item.get("strain")),
                raw,
            )
    negative_ok = set(seen_negative_rows) == set(EXPECTED_NO_ACTIVITY_ROWS)
    if negative_ok:
        for row, expected in EXPECTED_NO_ACTIVITY_ROWS.items():
            observed = seen_negative_rows[row]
            negative_ok &= normalized(observed[0]) == normalized(expected[0])
            negative_ok &= normalized(observed[1]) == normalized(expected[1])
            negative_ok &= observed[2] == "-"
    checks["six_explicit_no_activity_rows_match_table1_cells"] = negative_ok

    conflict_ok = any(
        contains_all(
            item,
            [
                "1000",
                "31.25",
                "3.125",
                "6.25",
                "xml:p:44",
                "xml:table-wrap:1",
            ],
        )
        for item in conflict_items(payload)
    )
    checks["dilution_range_conflict_caution_is_explicit"] = conflict_ok
    maximum_conflict_ok = any(
        contains_all(
            item,
            [
                "1000",
                "100",
                "maximum",
                "xml:p:44",
                "xml:table-wrap:1",
            ],
        )
        for item in conflict_items(payload)
    )
    checks["method_1000_vs_table_footnote_100_maximum_conflict_is_explicit"] = maximum_conflict_ok

    failed = [name for name, passed in checks.items() if not passed]
    return {
        "paper_id": "PMC11905587",
        "contract": "leader_candidate18_layer2_repair_20260726",
        "checks": checks,
        "failed_checks": failed,
        "contract_pass": not failed,
        "observed_counts": {
            "activity_records": len(activity),
            "toxicity_records": len(toxicity),
            "explicit_no_activity_rows": len(seen_negative_rows),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.artifact.read_text(encoding="utf-8"))
    report = validate(payload)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["contract_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
