#!/usr/bin/env python3
"""Check PMC13066039 Fig. 8b/c CCK-8 viability row coverage.

This script inspects the repaired activity/toxicity JSON only. It does not read
or emit paper source text.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PANELS = {
    "Fig. 8b": {
        "target_cell_line": "NIH-3T3",
        "locator_tokens": ("xml:fig:8", "Fig. 8b"),
    },
    "Fig. 8c": {
        "target_cell_line": "HCT-116",
        "locator_tokens": ("xml:fig:8", "Fig. 8c"),
    },
}
TREATMENTS = ("Nisin", "NP-AgNPs2", "P-AgNPs")
GROUPS = ("CK", "0.2", "0.4", "0.8", "1.6", "3.2")


def locator_text(row: dict[str, Any]) -> str:
    value = row.get("source_locator") or row.get("source_locators") or []
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def row_group(row: dict[str, Any]) -> str | None:
    conditions = row.get("assay_conditions") if isinstance(row.get("assay_conditions"), dict) else {}
    if row.get("concentration") is None:
        rationale = " ".join(
            str(value or "")
            for value in (
                row.get("concentration_not_reported_reason"),
                conditions.get("concentration_not_reported_reason"),
                conditions.get("dose_group"),
            )
        )
        return "CK" if "CK" in rationale else None
    return str(row.get("concentration")).rstrip("0").rstrip(".")


def treatment_series(row: dict[str, Any]) -> str | None:
    conditions = row.get("assay_conditions") if isinstance(row.get("assay_conditions"), dict) else {}
    series = conditions.get("treatment_series")
    if series:
        return str(series)
    treatment = str(row.get("treatment") or "")
    for expected in TREATMENTS:
        if expected in treatment:
            return expected
    return None


def valid_row(row: dict[str, Any], panel: str, treatment: str, group: str) -> list[str]:
    errors: list[str] = []
    if row.get("endpoint") != "cell viability":
        errors.append("endpoint")
    if row.get("raw_unit") != "%":
        errors.append("raw_unit")
    if row.get("normalization_status") != "direct":
        errors.append("normalization_status")
    if row.get("normalized_unit") != "%":
        errors.append("normalized_unit")
    if row.get("raw_value") is None:
        errors.append("raw_value")
    if row.get("normalized_value") is None:
        errors.append("normalized_value")
    if group == "CK":
        if "CK" not in str(row.get("concentration_not_reported_reason") or ""):
            errors.append("ck_control_rationale")
    else:
        if row.get("concentration_unit") != "mg/mL":
            errors.append("concentration_unit")
    target = str(row.get("target_cell_line") or row.get("target_species") or row.get("target") or "")
    if PANELS[panel]["target_cell_line"] not in target:
        errors.append("target_cell_line")
    locators = locator_text(row)
    if not all(token in locators for token in PANELS[panel]["locator_tokens"]):
        errors.append("source_locator")
    conditions = row.get("assay_conditions") if isinstance(row.get("assay_conditions"), dict) else {}
    nested_conc = conditions.get("sample_concentration")
    nested_unit = conditions.get("sample_concentration_unit")
    if group == "CK":
        if nested_conc is not None or nested_unit is not None:
            errors.append("nested_concentration_conflict")
    else:
        if str(nested_conc).rstrip("0").rstrip(".") != group or nested_unit != "mg/mL":
            errors.append("nested_concentration_conflict")
    if treatment_series(row) != treatment:
        errors.append("treatment_series")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--activity-json", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.activity_json).read_text())
    rows = payload.get("toxicity_records") if isinstance(payload.get("toxicity_records"), list) else []
    exclusions = payload.get("explicit_source_backed_exclusions")
    if not isinstance(exclusions, list):
        exclusions = []

    indexed: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        if not isinstance(row, dict) or row.get("endpoint") != "cell viability":
            continue
        conditions = row.get("assay_conditions") if isinstance(row.get("assay_conditions"), dict) else {}
        panel = conditions.get("figure_panel")
        group = row_group(row)
        treatment = treatment_series(row)
        if panel in PANELS and group in GROUPS and treatment in TREATMENTS:
            indexed.setdefault((panel, treatment, group), []).append(row)

    missing = []
    invalid = []
    duplicates = []
    for panel in PANELS:
        for treatment in TREATMENTS:
            for group in GROUPS:
                key = (panel, treatment, group)
                matches = indexed.get(key, [])
                if not matches:
                    missing.append({"panel": panel, "treatment": treatment, "group": group})
                    continue
                if len(matches) > 1:
                    duplicates.append({"panel": panel, "treatment": treatment, "group": group, "count": len(matches)})
                errors = valid_row(matches[0], panel, treatment, group)
                if errors:
                    invalid.append({"panel": panel, "treatment": treatment, "group": group, "errors": errors})

    fig8bc_exclusions = [
        exclusion
        for exclusion in exclusions
        if isinstance(exclusion, dict)
        and ("Fig. 8b" in json.dumps(exclusion, ensure_ascii=False) or "Fig. 8c" in json.dumps(exclusion, ensure_ascii=False))
    ]
    report = {
        "paper_id": "PMC13066039",
        "status": "clean" if not (missing or invalid or duplicates) else "findings",
        "expected_observations": len(PANELS) * len(TREATMENTS) * len(GROUPS),
        "covered_observations": len(indexed),
        "fig8bc_explicit_exclusions": len(fig8bc_exclusions),
        "missing": missing,
        "invalid": invalid,
        "duplicates": duplicates,
        "source_text_omitted": True,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"wrote {args.out} status={report['status']} covered={report['covered_observations']}")
    return 0 if report["status"] == "clean" else 1


if __name__ == "__main__":
    raise SystemExit(main())
