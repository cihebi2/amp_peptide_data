#!/usr/bin/env python3
"""Validate worker-3 supplementary status/count and locator repair.

This check intentionally reports only counts, field names, and locator IDs.
It does not print source passages or table/figure content.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_SURFACE_LOCATORS = {
    "Table S1": "supp:RA-015-D5RA02932E-s001.pdf:page=13:table=S1",
    "Figure S14": "supp:RA-015-D5RA02932E-s001.pdf:page=16:figure=S14",
    "Figure S15": "supp:RA-015-D5RA02932E-s001.pdf:page=17:figure=S15",
    "Figure S16": "supp:RA-015-D5RA02932E-s001.pdf:page=17:figure=S16",
    "Figure S17": "supp:RA-015-D5RA02932E-s001.pdf:page=18:figure=S17",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def locator_strings(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str):
        if value.strip():
            found.add(value.strip())
    elif isinstance(value, list):
        for item in value:
            found.update(locator_strings(item))
    elif isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in {"locator", "source_locator", "source_locators", "locators"}:
                found.update(locator_strings(item))
            else:
                found.update(locator_strings(item))
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--json-out", required=True, type=Path)
    args = parser.parse_args()

    packet = args.packet.resolve()
    status = read_json(packet / "extraction/extraction_status.json")
    supp_tables = read_json(packet / "extracted/supplementary_tables.json")
    locator_index = read_json(packet / "locators/locator_index.json")

    table_count = len(supp_tables.get("tables") or [])
    figure_surface_count = len(supp_tables.get("figure_surfaces") or [])
    structured_surface_count = table_count + figure_surface_count
    table_cell_observation_count = int(supp_tables.get("table_cell_observation_count") or 0)
    figure_observation_count = int(supp_tables.get("figure_observation_count") or 0)

    errors: list[str] = []
    expected_status = {
        "supplementary_table_count": table_count,
        "supplementary_figure_surface_count": figure_surface_count,
        "structured_supplementary_surface_count": structured_surface_count,
        "supplementary_table_cell_observation_count": table_cell_observation_count,
        "supplementary_quantitative_figure_observation_count": figure_observation_count,
    }
    for field, expected in expected_status.items():
        if status.get(field) != expected:
            errors.append(f"status_mismatch:{field}")

    table_locators = locator_strings(supp_tables.get("tables") or [])
    figure_locators = locator_strings(supp_tables.get("figure_surfaces") or [])
    packet_locators = locator_strings(locator_index.get("locators") or [])

    required_status: dict[str, dict[str, bool]] = {}
    for label, locator in REQUIRED_SURFACE_LOCATORS.items():
        in_tables = locator in table_locators or locator in figure_locators
        in_locator_index = locator in packet_locators
        required_status[label] = {
            "supplementary_tables": in_tables,
            "locator_index": in_locator_index,
        }
        if not in_tables:
            errors.append(f"missing_supplementary_tables_locator:{label}")
        if not in_locator_index:
            errors.append(f"missing_locator_index_locator:{label}")

    payload = {
        "paper_id": packet.name,
        "pass": not errors,
        "errors": errors,
        "counts": {
            "supplementary_tables_json_table_count": table_count,
            "supplementary_tables_json_figure_surface_count": figure_surface_count,
            "structured_supplementary_surface_count": structured_surface_count,
            "table_cell_observation_count": table_cell_observation_count,
            "figure_observation_count": figure_observation_count,
            "locator_index_count": int(locator_index.get("locator_count") or 0),
        },
        "status_fields_checked": sorted(expected_status),
        "required_locator_status": required_status,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
