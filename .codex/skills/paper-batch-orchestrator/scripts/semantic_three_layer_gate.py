#!/usr/bin/env python3
"""Semantic risk gate for batch/2-team AMP three-layer curation artifacts.

This script is intentionally stricter than the repo validator. It flags review
provenance gaps and common scaffold artifacts that should trigger worker-6
rework before a paper is called publication-grade.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from decimal import Decimal
from pathlib import Path
from typing import Any

MIC_LIKE = {"MIC", "MBC", "MFC", "IC50", "EC50", "HC50", "CC50", "MBIC", "MBEC", "MHC", "MIC50", "MIC90"}
GENERIC_ENDPOINTS = {"activity", "antimicrobial activity", "antimicrobial", "anticancer"}
VALID_NORMALIZATION_STATUSES = {"direct", "converted", "not_convertible", "ambiguous"}
SIMPLE_NORMALIZED_VALUE_RE = re.compile(
    r"^(?P<operator>[<>]=?)?(?P<value>(?:\d+(?:\.\d+)?|\.\d+|nd|n/?a))$",
    re.I,
)
SENTENCE_FRAGMENT_RE = re.compile(
    r"^(?:The|In this|However|This|These|Those|Our|We|An|Defensins|Figure|Table|Results|Discussion|Conclusion)\b"
    r"|^A\b(?!\.)",
    re.I,
)
NON_BIOLOGICAL_TARGET_RE = re.compile(
    r"(?:components?\s+and\s+concentration|solvent\s+system|main\s+ftir|assignments?|reference|"
    r"tensile\s+strength|young['’]?s\s+modulus|elongation\s+at\s+break|thickness|contact\s+angle|"
    r"weight\s+loss|thermal\s+(?:stability|decomposition))",
    re.I,
)
ACTIVITY_TABLE_RE = re.compile(
    r"\b(?:antibacterial|antimicrobial|inhibition\s+zone|MIC|MBC|MFC|CFU(?:/mL)?|"
    r"colony[- ]forming|hemolysis|haemolysis|cytotoxicity|cell\s+viability)\b",
    re.I,
)
NON_ACTIVITY_TABLE_RE = re.compile(
    r"\b(?:film[- ]forming\s+solution|solvent\s+system|FTIR|absorption\s+bands?|spectroscop|"
    r"thermogravimetric|thermal\s+(?:stability|decomposition)|contact\s+angle|surface\s+wettability|"
    r"tensile\s+strength|young['’]?s\s+modulus|mechanical\s+properties|elongation\s+at\s+break)\b",
    re.I,
)
TOXICITY_ENDPOINT_RE = re.compile(
    r"\b(?:ha?emolysis|cytotoxic(?:ity)?|cell\s+death|cell\s+viability|mtt|ldh|hc50|cc50|mhc)\b",
    re.I,
)
ANTIMICROBIAL_ENDPOINT_RE = re.compile(
    r"\b(?:MIC(?:50|90)?|MBC|MFC|MBIC(?:50)?|MBEC|FICI?)\b",
    re.I,
)
TABLE_LOCATOR_RE = re.compile(r"xml:table-wrap:\d+", re.I)
LOCATOR_BEARING_KEYS = {
    "locator",
    "locators",
    "source_locator",
    "source_locators",
    "source_file",
    "source_path",
    "path",
    "paper_xml",
    "paper_pdf",
    "xml_path",
    "supplementary_sources",
    "body_locator",
    "figure_locator",
    "table_locator",
    "xml_locator",
    "pdf_locator",
    "pdf_table_locator",
    "unit_locator",
    "endpoint_unit_locator",
    "method_locators",
    "supporting_locators",
    "all_locators",
    "primary_locators",
    "name_locators",
    "modification_locators",
    "synthetic_origin_locators",
    "combination_name_locators",
    "individual_identity_locators",
    "representative_checked_locators",
    "exact_modified_sequence_locators",
    "free_text_modification_locators",
}
EXPECTED_CELL_OBSERVATION_FIELDS = {
    "evidence_kind",
    "evidence_role",
    "endpoint",
    "raw_value",
    "raw_unit",
    "treatment",
    "concentration",
    "concentration_unit",
    "timepoint",
    "target_species",
    "target_strain_or_isolate",
}
TAXON_ABBREVIATION_RE = re.compile(r"^[A-Z]\.\s*[a-z][a-z-]+(?:\b|[\s,;()/])")
FULL_TAXON_RE = re.compile(r"^[A-Z][a-z]{2,}\s+[a-z][a-z-]+(?:\b|[\s,;()/])")
BOILERPLATE_RE = re.compile(
    r"(?:Skip to|Advertisement|Login|Javascript|Request Support|Citations to This Article|similar content being viewed|Sign in|LinkedIn|Altmetric|Metrics details)",
    re.I,
)
TEMPLATE_SUMMARY = "six-worker adjudication found no structural blockers"
PUBLICATION_GRADE_STATUSES = {"accepted_clean", "accepted_with_cautions"}
VALID_REVIEW_STATUSES = PUBLICATION_GRADE_STATUSES | {
    "needs_targeted_rework",
    "blocked_missing_primary_material",
}
SOURCE_DEPTH_SYNONYMS = {
    "paper_xml": ("paper_xml", "xml", "paper.xml", "article_xml"),
    "paper_pdf": ("paper_pdf", "pdf", "paper.pdf", "article_pdf"),
    "oa_package": ("oa_package", "pmc_oa_package", "package", "oa package", "archive"),
    "supplementary_assets": ("supplementary_assets", "supplement", "supplementary", "supplementary_files"),
    "merged_database_rows": ("merged_database_rows", "database_rows", "apd6", "dbaasp", "dramp", "merged rows"),
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"_missing": True}
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {"_parse_error": str(exc)}
    return data if isinstance(data, dict) else {"_not_object": True}


def source_locator_has_anchor(locator: Any) -> bool:
    if isinstance(locator, str):
        return bool(locator.strip())
    if isinstance(locator, list):
        return any(source_locator_has_anchor(item) for item in locator)
    if not isinstance(locator, dict):
        return False
    return any(
        locator_bearing_key(key) and source_locator_has_anchor(value)
        for key, value in locator.items()
    )


def text_blob(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False).lower()
    except TypeError:
        return str(value).lower()


def looks_like_taxon_label(value: str) -> bool:
    """Allow valid organism abbreviations before sentence-fragment checks.

    The old `A` sentence-starter heuristic treated `A. baumannii` as prose.
    Genus abbreviations are common in MIC tables and must not be converted into
    false hard failures.
    """
    species = " ".join(str(value or "").split())
    return bool(TAXON_ABBREVIATION_RE.search(species) or FULL_TAXON_RE.search(species))


def species_is_sentence_fragment(value: str) -> bool:
    species = " ".join(str(value or "").split())
    if not species:
        return False
    if looks_like_taxon_label(species):
        return False
    return bool(SENTENCE_FRAGMENT_RE.search(species))


def species_is_non_biological_label(value: str) -> bool:
    return bool(NON_BIOLOGICAL_TARGET_RE.search(" ".join(str(value or "").split())))


def source_locator_id(locator: Any) -> str:
    if isinstance(locator, str):
        return locator.strip()
    if isinstance(locator, dict):
        return str(locator.get("locator") or "").strip()
    return ""


def locator_bearing_key(key: Any) -> bool:
    normalized = str(key or "").strip().lower().replace("-", "_")
    return normalized in LOCATOR_BEARING_KEYS


def source_locator_ids(locator: Any) -> set[str]:
    if isinstance(locator, str):
        return {locator.strip()} if locator.strip() else set()
    if isinstance(locator, list):
        found: set[str] = set()
        for item in locator:
            found.update(source_locator_ids(item))
        return found
    if isinstance(locator, dict):
        found: set[str] = set()
        for key, value in locator.items():
            if locator_bearing_key(key):
                found.update(source_locator_ids(value))
        return found
    return set()


def base_table_locator(locator: str) -> str:
    match = TABLE_LOCATOR_RE.search(str(locator or ""))
    return match.group(0) if match else str(locator or "")


def table_locator_ids(locator: Any) -> set[str]:
    found: set[str] = set()
    for locator_id in source_locator_ids(locator):
        found.update(match.group(0) for match in TABLE_LOCATOR_RE.finditer(locator_id))
    return found


def activity_toxicity_records(payload: dict[str, Any]) -> list[Any]:
    records: list[Any] = []
    for key in ("activity_records", "toxicity_records"):
        value = payload.get(key)
        if isinstance(value, list):
            records.extend(value)
    return records


def record_source_locators(record: dict[str, Any]) -> list[Any]:
    return [
        value
        for key in ("source_locator", "source_locators")
        if (value := record.get(key)) not in (None, "", [], {})
    ]


def table_observation_contract(
    root: Path, paper_id: str
) -> tuple[
    dict[str, int],
    dict[str, set[tuple[str, ...]]],
    dict[tuple[str, tuple[str, ...]], dict[str, Any]],
    list[dict[str, Any]],
]:
    path = root / "packets" / paper_id / "rework" / "rework_requests.jsonl"
    expected: dict[str, int] = {}
    require_cells: dict[str, set[tuple[str, ...]]] = {}
    expected_cell_observations: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
    issues: list[dict[str, Any]] = []
    if not path.exists():
        return expected, require_cells, expected_cell_observations, issues
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            issues.append({"code": "invalid_rework_request_json", "line_number": line_number})
            continue
        if not isinstance(row, dict):
            issues.append({"code": "invalid_rework_request_schema", "line_number": line_number})
            continue
        if "expected_observation_counts" in row:
            counts = row.get("expected_observation_counts")
            if not isinstance(counts, dict):
                issues.append(
                    {
                        "code": "invalid_expected_observation_counts_schema",
                        "line_number": line_number,
                        "ticket_id": row.get("ticket_id"),
                    }
                )
            else:
                if not counts:
                    issues.append(
                        {
                            "code": "empty_expected_observation_counts",
                            "line_number": line_number,
                            "ticket_id": row.get("ticket_id"),
                        }
                    )
                for locator, raw_count in counts.items():
                    if isinstance(raw_count, int) and not isinstance(raw_count, bool):
                        count = raw_count
                    elif isinstance(raw_count, str) and re.fullmatch(r"[+-]?\d+", raw_count.strip()):
                        count = int(raw_count)
                    else:
                        count = None
                    table_matches = [match.group(0) for match in TABLE_LOCATOR_RE.finditer(str(locator))]
                    if len(table_matches) > 1:
                        issues.append(
                            {
                                "code": "ambiguous_expected_observation_locator",
                                "line_number": line_number,
                                "ticket_id": row.get("ticket_id"),
                                "source_locator": locator,
                                "table_locators": table_matches,
                            }
                        )
                        continue
                    table_locator = table_matches[0] if table_matches else ""
                    if count is None or count < 0 or not table_locator.startswith("xml:table-wrap:"):
                        issues.append(
                            {
                                "code": "invalid_expected_observation_count",
                                "line_number": line_number,
                                "ticket_id": row.get("ticket_id"),
                                "source_locator": locator,
                                "value": raw_count,
                            }
                        )
                        continue
                    if table_locator in expected and expected[table_locator] != count:
                        issues.append(
                            {
                                "code": "conflicting_expected_observation_counts",
                                "line_number": line_number,
                                "ticket_id": row.get("ticket_id"),
                                "source_locator": table_locator,
                                "previous_count": expected[table_locator],
                                "new_count": count,
                            }
                        )
                        continue
                    expected[table_locator] = count

        if "require_cell_locators" in row:
            requirements = row.get("require_cell_locators")
            if not isinstance(requirements, dict):
                issues.append(
                    {
                        "code": "invalid_require_cell_locators_schema",
                        "line_number": line_number,
                        "ticket_id": row.get("ticket_id"),
                    }
                )
            else:
                if not requirements:
                    issues.append(
                        {
                            "code": "empty_require_cell_locators",
                            "line_number": line_number,
                            "ticket_id": row.get("ticket_id"),
                        }
                    )
                for locator, required in requirements.items():
                    table_matches = [match.group(0) for match in TABLE_LOCATOR_RE.finditer(str(locator))]
                    if len(table_matches) > 1:
                        issues.append(
                            {
                                "code": "ambiguous_required_cell_locator",
                                "line_number": line_number,
                                "ticket_id": row.get("ticket_id"),
                                "source_locator": locator,
                                "table_locators": table_matches,
                            }
                        )
                        continue
                    if not isinstance(required, bool) or not table_matches:
                        issues.append(
                            {
                                "code": "invalid_required_cell_locator",
                                "line_number": line_number,
                                "ticket_id": row.get("ticket_id"),
                                "source_locator": locator,
                                "value": required,
                            }
                        )
                        continue
                    if required:
                        table_locator = table_matches[0]
                        markers = source_cell_identity(str(locator))
                        rows = [item for item in markers if item.startswith("row=")]
                        columns = [item for item in markers if item.startswith("column=")]
                        if bool(rows) != bool(columns) or len(rows) > 1 or len(columns) > 1:
                            issues.append(
                                {
                                    "code": "invalid_required_cell_locator",
                                    "line_number": line_number,
                                    "ticket_id": row.get("ticket_id"),
                                    "source_locator": locator,
                                    "value": required,
                                }
                            )
                            continue
                        required_set = require_cells.setdefault(table_locator, set())
                        if rows and columns:
                            required_set.add(tuple(rows + columns))
        if "expected_cell_observations" in row:
            cell_observations = row.get("expected_cell_observations")
            if not isinstance(cell_observations, dict):
                issues.append(
                    {
                        "code": "invalid_expected_cell_observations_schema",
                        "line_number": line_number,
                        "ticket_id": row.get("ticket_id"),
                    }
                )
            else:
                if not cell_observations:
                    issues.append(
                        {
                            "code": "empty_expected_cell_observations",
                            "line_number": line_number,
                            "ticket_id": row.get("ticket_id"),
                        }
                    )
                for locator, fields in cell_observations.items():
                    table_matches = [match.group(0) for match in TABLE_LOCATOR_RE.finditer(str(locator))]
                    if len(table_matches) != 1 or not isinstance(fields, dict) or not fields:
                        issues.append(
                            {
                                "code": "invalid_expected_cell_observation",
                                "line_number": line_number,
                                "ticket_id": row.get("ticket_id"),
                                "source_locator": locator,
                            }
                        )
                        continue
                    table_locator = table_matches[0]
                    cell_ids = table_source_cell_identities(str(locator), table_locator)
                    invalid_fields = (
                        set(fields) - EXPECTED_CELL_OBSERVATION_FIELDS
                        or {
                            field
                            for field, value in fields.items()
                            if value is None or (isinstance(value, str) and not value.strip())
                        }
                    )
                    if fields.get("evidence_kind") not in (None, "activity", "toxicity"):
                        invalid_fields.add("evidence_kind")
                    if invalid_fields:
                        issues.append(
                            {
                                "code": "invalid_expected_cell_observation_fields",
                                "line_number": line_number,
                                "ticket_id": row.get("ticket_id"),
                                "source_locator": locator,
                                "invalid_fields": sorted(invalid_fields),
                            }
                        )
                        continue
                    if len(cell_ids) != 1 or any(
                        isinstance(value, (dict, list)) for value in fields.values()
                    ):
                        issues.append(
                            {
                                "code": "invalid_expected_cell_observation",
                                "line_number": line_number,
                                "ticket_id": row.get("ticket_id"),
                                "source_locator": locator,
                            }
                        )
                        continue
                    cell_id = next(iter(cell_ids))
                    key = (table_locator, cell_id)
                    previous_fields = expected_cell_observations.get(key, {})
                    conflicting_fields = sorted(
                        field
                        for field in previous_fields.keys() & fields.keys()
                        if previous_fields[field] != fields[field]
                    )
                    if conflicting_fields:
                        issues.append(
                            {
                                "code": "conflicting_expected_cell_observation",
                                "line_number": line_number,
                                "ticket_id": row.get("ticket_id"),
                                "source_locator": locator,
                                "conflicting_fields": conflicting_fields,
                            }
                        )
                        continue
                    expected_cell_observations[key] = {**previous_fields, **fields}
                    require_cells.setdefault(table_locator, set()).add(cell_id)
    for table_locator, exact_cells in sorted(require_cells.items()):
        if table_locator not in expected:
            issues.append(
                {
                    "code": "missing_expected_count_for_required_cells",
                    "source_locator": table_locator,
                }
            )
        if exact_cells and table_locator in expected and len(exact_cells) != expected[table_locator]:
            issues.append(
                {
                    "code": "required_cell_locator_count_conflict",
                    "source_locator": table_locator,
                    "expected_count": expected[table_locator],
                    "required_cell_count": len(exact_cells),
                }
            )
    for table_locator, _cell_id in expected_cell_observations:
        if table_locator not in expected:
            issues.append(
                {
                    "code": "missing_expected_count_for_cell_observations",
                    "source_locator": table_locator,
                }
            )
    return expected, require_cells, expected_cell_observations, issues


def expected_table_observation_contract(root: Path, paper_id: str) -> tuple[dict[str, int], list[dict[str, Any]]]:
    expected, _require_cells, _expected_cells, issues = table_observation_contract(root, paper_id)
    return expected, issues


def normalized_identity_value(value: Any) -> Any:
    if isinstance(value, str):
        return " ".join(value.split()).casefold()
    return value


def target_species(record: dict[str, Any]) -> str:
    target_value = record.get("target")
    target = target_value if isinstance(target_value, dict) else {}
    species = target.get("species") or record.get("target_species")
    if not species and isinstance(target_value, str):
        species = target_value
    if isinstance(species, dict):
        species = species.get("species") or ""
    return str(species or "").strip()


def target_identity(record: dict[str, Any]) -> dict[str, Any]:
    target_value = record.get("target")
    target = target_value if isinstance(target_value, dict) else {}
    species = target_species(record)
    return {
        "class": normalized_identity_value(
            target.get("target_class") or target.get("class") or record.get("target_class")
        ),
        "species": normalized_identity_value(species),
        "strain_or_isolate": normalized_identity_value(
            target.get("strain_or_isolate")
            or target.get("strain")
            or target.get("isolate")
            or record.get("target_strain_or_isolate")
            or record.get("target_strain")
            or record.get("target_isolate")
        ),
        "cell_line": normalized_identity_value(target.get("cell_line") or record.get("target_cell_line")),
    }


def observation_identity(record: dict[str, Any], table_locator: str) -> str:
    identity = {
        "table_locator": table_locator,
        "source_cell": source_cell_identity(record_source_locators(record)),
        "endpoint": record.get("endpoint"),
        "raw_value": record.get("raw_value"),
        "raw_unit": record.get("raw_unit"),
        "target": target_identity(record),
        "entity": record.get("entity"),
        "sample": record.get("sample"),
        "treatment": record.get("treatment"),
        "peptide": record.get("peptide"),
        "concentration": record.get("concentration"),
        "timepoint": record.get("timepoint") or record.get("time"),
        "assay_conditions": record.get("assay_conditions"),
    }
    return json.dumps(identity, ensure_ascii=False, sort_keys=True, default=str)


def canonical_cell_axis(axis: Any) -> str:
    normalized_axis = str(axis).lower().replace("-", "_")
    if normalized_axis in {"row", "row_index", "body_row", "body_row_index", "tr", "tr_index"}:
        return "row"
    if normalized_axis in {
        "cell",
        "cell_index",
        "col",
        "col_index",
        "column",
        "column_index",
        "td",
        "td_index",
    }:
        return "column"
    if normalized_axis in {"timepoint", "time_point"}:
        return "timepoint"
    return ""


def canonical_coordinate_value(raw_value: Any) -> str:
    if isinstance(raw_value, bool):
        return str(raw_value).lower()
    if isinstance(raw_value, int):
        return str(raw_value)
    if isinstance(raw_value, float) and raw_value.is_integer():
        return str(int(raw_value))
    value = str(raw_value).strip()
    if re.fullmatch(r"[+-]?\d+", value):
        return str(int(value))
    if re.fullmatch(r"[+-]?\d+\.0+", value):
        return str(int(float(value)))
    return value


def coordinate_value_is_valid(raw_value: Any) -> bool:
    if isinstance(raw_value, bool):
        return False
    if isinstance(raw_value, int):
        return True
    if isinstance(raw_value, float):
        return raw_value.is_integer()
    return bool(re.fullmatch(r"[+-]?\d+(?:\.0+)?", str(raw_value).strip()))


def source_cell_identity(locator: Any) -> list[str]:
    markers: set[str] = set()

    def add_marker(axis: str, raw_value: Any) -> None:
        canonical_axis = canonical_cell_axis(axis)
        if not canonical_axis:
            return
        if coordinate_value_is_valid(raw_value):
            markers.add(f"{canonical_axis}={canonical_coordinate_value(raw_value)}")

    def visit(value: Any) -> None:
        if isinstance(value, str):
            for match in re.finditer(
                r"(?P<axis>body[-_]?row|row|tr|cell|col(?:umn)?|td|time[-_]?point)(?:[-_]?index)?\s*[=:]\s*(?P<value>\d+)",
                value,
                re.I,
            ):
                add_marker(match.group("axis"), match.group("value"))
            return
        if isinstance(value, list):
            for item in value:
                visit(item)
            return
        if not isinstance(value, dict):
            return
        for key, item in value.items():
            normalized_key = str(key).lower().replace("-", "_")
            add_marker(normalized_key, item)
            if locator_bearing_key(key):
                visit(item)

    visit(locator)
    return sorted(markers)


def table_source_cell_identities(locator: Any, table_locator: str) -> set[tuple[str, ...]]:
    identities: set[tuple[str, ...]] = set()

    def add_complete(markers: list[str]) -> None:
        rows = [item for item in markers if item.startswith("row=")]
        columns = [item for item in markers if item.startswith("column=")]
        timepoints = [item for item in markers if item.startswith("timepoint=")]
        if rows and columns:
            identities.add(tuple(rows + columns + timepoints))

    def visit(value: Any) -> None:
        if isinstance(value, str):
            for segment in re.split(r"\s*;\s*", value):
                if table_locator_ids(segment) == {table_locator}:
                    add_complete(source_cell_identity(segment))
            return
        if isinstance(value, list):
            for item in value:
                visit(item)
            return
        if not isinstance(value, dict):
            return

        direct_markers: set[str] = set()
        parent_has_coordinates = False
        direct_table_reference = False
        nested_locator_values: list[Any] = []
        for key, item in value.items():
            axis = canonical_cell_axis(key)
            if axis and coordinate_value_is_valid(item):
                parent_has_coordinates = True
                direct_markers.add(f"{axis}={canonical_coordinate_value(item)}")
            if not locator_bearing_key(key):
                continue
            if isinstance(item, (dict, list)):
                nested_locator_values.append(item)
            else:
                if table_locator_ids(item) == {table_locator}:
                    direct_table_reference = True
                for segment in re.split(r"\s*;\s*", str(item)):
                    if table_locator_ids(segment) == {table_locator}:
                        add_complete(source_cell_identity(segment))

        if direct_table_reference or (
            parent_has_coordinates and table_locator_ids(value) == {table_locator}
        ):
            add_complete(sorted(direct_markers))
        for nested in nested_locator_values:
            visit(nested)

    visit(locator)
    return identities


def table_source_row_identities(locator: Any, table_locator: str) -> set[str]:
    identities: set[str] = set()

    def add_rows(markers: list[str]) -> None:
        identities.update(item for item in markers if item.startswith("row="))

    def visit(value: Any) -> None:
        if isinstance(value, str):
            for segment in re.split(r"\s*;\s*", value):
                if table_locator_ids(segment) == {table_locator}:
                    add_rows(source_cell_identity(segment))
            return
        if isinstance(value, list):
            for item in value:
                visit(item)
            return
        if not isinstance(value, dict):
            return

        direct_markers: set[str] = set()
        parent_has_coordinates = False
        direct_table_reference = False
        nested_locator_values: list[Any] = []
        for key, item in value.items():
            axis = canonical_cell_axis(key)
            if axis and coordinate_value_is_valid(item):
                parent_has_coordinates = True
                direct_markers.add(f"{axis}={canonical_coordinate_value(item)}")
            if not locator_bearing_key(key):
                continue
            if isinstance(item, (dict, list)):
                nested_locator_values.append(item)
            else:
                if table_locator_ids(item) == {table_locator}:
                    direct_table_reference = True
                for segment in re.split(r"\s*;\s*", str(item)):
                    if table_locator_ids(segment) == {table_locator}:
                        add_rows(source_cell_identity(segment))

        if direct_table_reference or (
            parent_has_coordinates and table_locator_ids(value) == {table_locator}
        ):
            add_rows(sorted(direct_markers))
        for nested in nested_locator_values:
            visit(nested)

    visit(locator)
    return identities


def table_observation_summary(payload: dict[str, Any]) -> tuple[dict[str, int], list[dict[str, Any]]]:
    seen: dict[str, dict[str, dict[str, Any]]] = {}
    duplicates: list[dict[str, Any]] = []
    for record in activity_toxicity_records(payload):
        if not isinstance(record, dict):
            continue
        locators = record_source_locators(record)
        for table_locator in table_locator_ids(locators):
            key = observation_identity(record, table_locator)
            table_seen = seen.setdefault(table_locator, {})
            if key in table_seen:
                duplicates.append(
                    {
                        "source_locator": table_locator,
                        "first_record_id": table_seen[key].get("record_id"),
                        "duplicate_record_id": record.get("record_id"),
                    }
                )
            else:
                table_seen[key] = record
    return {table: len(records) for table, records in seen.items()}, duplicates


def table_observation_counts(payload: dict[str, Any]) -> dict[str, int]:
    counts, _duplicates = table_observation_summary(payload)
    return counts


def record_contract_field(record: dict[str, Any], field: str) -> Any:
    if field == "evidence_role":
        return (
            record.get("evidence_role")
            or record.get("observation_role")
            or record.get("inclusion_role")
        )
    if field == "treatment":
        value = (
            record.get("treatment")
            or record.get("entity")
            or record.get("assayed_entity")
        )
        if isinstance(value, dict):
            value = (
                value.get("name")
                or value.get("bacteriocin")
                or value.get("treatment")
                or value.get("sample")
                or value.get("source_table_row_label")
            )
        return value
    if field == "concentration":
        value = record.get("concentration")
        if isinstance(value, dict):
            value = value.get("value") or value.get("raw_value")
        if value in (None, ""):
            conditions = record.get("assay_conditions") if isinstance(record.get("assay_conditions"), dict) else {}
            value = (
                conditions.get("peptide_concentration")
                or conditions.get("concentration")
                or conditions.get("sample_concentration")
            )
        return value
    if field == "concentration_unit":
        value = record.get("concentration_unit")
        if value in (None, ""):
            conditions = record.get("assay_conditions") if isinstance(record.get("assay_conditions"), dict) else {}
            value = (
                conditions.get("peptide_concentration_unit")
                or conditions.get("concentration_unit")
                or conditions.get("sample_concentration_unit")
            )
        return value
    if field == "timepoint":
        value = record.get("timepoint") or record.get("time")
        unit = record.get("timepoint_unit") or record.get("time_unit")
        if value in (None, ""):
            conditions = record.get("assay_conditions") if isinstance(record.get("assay_conditions"), dict) else {}
            value = conditions.get("timepoint") or conditions.get("time")
            unit = unit or conditions.get("timepoint_unit") or conditions.get("time_unit")
        if value not in (None, "") and unit not in (None, ""):
            value_text = str(value).strip()
            unit_text = str(unit).strip()
            if unit_text.casefold() not in value_text.casefold().split():
                return f"{value_text} {unit_text}"
        return value
    if field == "target_species":
        return target_species(record)
    if field == "target_strain_or_isolate":
        target = record.get("target") if isinstance(record.get("target"), dict) else {}
        return (
            target.get("strain_or_isolate")
            or target.get("strain")
            or target.get("isolate")
            or record.get("target_strain_or_isolate")
            or record.get("target_strain")
            or record.get("target_isolate")
        )
    return record.get(field)


def normalize_contract_field(value: Any) -> str:
    return " ".join(str(value or "").split()).casefold()


def non_table_contract_field_matches(field: str, observed: Any, expected: Any) -> bool:
    if field in {"raw_unit", "concentration_unit"}:
        return canonical_normalization_unit(observed) == canonical_normalization_unit(expected)
    if field == "raw_value":
        observed_scalar = canonical_direct_scalar(observed)
        expected_scalar = canonical_direct_scalar(expected)
        if observed_scalar is not None and expected_scalar is not None:
            return observed_scalar == expected_scalar
    return normalize_contract_field(observed) == normalize_contract_field(expected)


def evidence_kind_count_contract(
    root: Path, paper_id: str
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    path = root / "packets" / paper_id / "rework" / "rework_requests.jsonl"
    expected: dict[str, int] = {}
    issues: list[dict[str, Any]] = []
    if not path.exists():
        return expected, issues
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            issues.append(
                {"code": "invalid_rework_request_json", "line_number": line_number}
            )
            continue
        if not isinstance(row, dict):
            issues.append(
                {"code": "invalid_rework_request_schema", "line_number": line_number}
            )
            continue
        if "expected_evidence_kind_counts" not in row:
            continue
        counts = row.get("expected_evidence_kind_counts")
        if not isinstance(counts, dict) or not counts:
            issues.append(
                {
                    "code": "invalid_expected_evidence_kind_counts",
                    "line_number": line_number,
                    "ticket_id": row.get("ticket_id"),
                }
            )
            continue
        for evidence_kind, raw_count in counts.items():
            if (
                evidence_kind not in {"activity", "toxicity"}
                or not isinstance(raw_count, int)
                or isinstance(raw_count, bool)
                or raw_count < 0
            ):
                issues.append(
                    {
                        "code": "invalid_expected_evidence_kind_count",
                        "line_number": line_number,
                        "ticket_id": row.get("ticket_id"),
                        "evidence_kind": evidence_kind,
                        "value": raw_count,
                    }
                )
                continue
            if evidence_kind in expected and expected[evidence_kind] != raw_count:
                issues.append(
                    {
                        "code": "conflicting_expected_evidence_kind_count",
                        "line_number": line_number,
                        "ticket_id": row.get("ticket_id"),
                        "evidence_kind": evidence_kind,
                        "previous_count": expected[evidence_kind],
                        "new_count": raw_count,
                    }
                )
                continue
            expected[evidence_kind] = raw_count
    return expected, issues


def expected_evidence_kind_count_issues(
    root: Path, paper_id: str, payload: dict[str, Any]
) -> list[dict[str, Any]]:
    expected, issues = evidence_kind_count_contract(root, paper_id)
    for evidence_kind, expected_count in sorted(expected.items()):
        records = payload.get(f"{evidence_kind}_records")
        observed_count = len(records) if isinstance(records, list) else 0
        if observed_count != expected_count:
            issues.append(
                {
                    "code": "evidence_kind_record_count_mismatch",
                    "evidence_kind": evidence_kind,
                    "expected_count": expected_count,
                    "observed_count": observed_count,
                }
            )
    return issues


def non_table_observation_contract(
    root: Path, paper_id: str
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    path = root / "packets" / paper_id / "rework" / "rework_requests.jsonl"
    expected: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, Any]] = []
    if not path.exists():
        return expected, issues
    allowed = EXPECTED_CELL_OBSERVATION_FIELDS | {
        "evidence_kind",
        "required_locator_any",
    }
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            issues.append(
                {"code": "invalid_rework_request_json", "line_number": line_number}
            )
            continue
        if not isinstance(row, dict):
            issues.append(
                {"code": "invalid_rework_request_schema", "line_number": line_number}
            )
            continue
        if "expected_non_table_observations" not in row:
            continue
        observations = row.get("expected_non_table_observations")
        if not isinstance(observations, dict) or not observations:
            issues.append(
                {
                    "code": "invalid_expected_non_table_observations",
                    "line_number": line_number,
                    "ticket_id": row.get("ticket_id"),
                }
            )
            continue
        for observation_id, specification in observations.items():
            invalid = (
                not str(observation_id).strip()
                or not isinstance(specification, dict)
                or not specification
                or bool(set(specification or {}) - allowed)
            )
            kind = specification.get("evidence_kind") if isinstance(specification, dict) else None
            required_locators = (
                specification.get("required_locator_any")
                if isinstance(specification, dict)
                else None
            )
            if (
                invalid
                or kind not in {"activity", "toxicity"}
                or not isinstance(required_locators, list)
                or not required_locators
                or any(not isinstance(item, str) or not item.strip() for item in required_locators)
            ):
                issues.append(
                    {
                        "code": "invalid_expected_non_table_observation",
                        "line_number": line_number,
                        "ticket_id": row.get("ticket_id"),
                        "observation_id": observation_id,
                    }
                )
                continue
            key = str(observation_id).strip()
            normalized = dict(specification)
            if key in expected and expected[key] != normalized:
                issues.append(
                    {
                        "code": "conflicting_expected_non_table_observation",
                        "line_number": line_number,
                        "ticket_id": row.get("ticket_id"),
                        "observation_id": key,
                    }
                )
                continue
            expected[key] = normalized
    return expected, issues


def expected_non_table_observation_issues(
    root: Path, paper_id: str, payload: dict[str, Any]
) -> list[dict[str, Any]]:
    expected, issues = non_table_observation_contract(root, paper_id)
    for observation_id, specification in sorted(expected.items()):
        kind = str(specification["evidence_kind"])
        records = payload.get(f"{kind}_records")
        records = records if isinstance(records, list) else []
        expected_fields = {
            key: value
            for key, value in specification.items()
            if key not in {"evidence_kind", "required_locator_any"}
        }
        matches = [
            record
            for record in records
            if isinstance(record, dict)
            and all(
                non_table_contract_field_matches(
                    field, record_contract_field(record, field), expected_value
                )
                for field, expected_value in expected_fields.items()
            )
        ]
        if len(matches) != 1:
            issues.append(
                {
                    "code": "non_table_observation_record_count_mismatch",
                    "observation_id": observation_id,
                    "evidence_kind": kind,
                    "expected_count": 1,
                    "observed_count": len(matches),
                    "record_ids": [record.get("record_id") for record in matches],
                }
            )
            continue
        actual_locators = {
            segment.strip()
            for locator in source_locator_ids(record_source_locators(matches[0]))
            for segment in re.split(r"\s*;\s*", locator)
            if segment.strip()
        }
        required_locators = set(specification["required_locator_any"])
        if actual_locators.isdisjoint(required_locators):
            issues.append(
                {
                    "code": "non_table_observation_locator_mismatch",
                    "observation_id": observation_id,
                    "record_id": matches[0].get("record_id"),
                    "required_locator_any": sorted(required_locators),
                    "observed_locators": sorted(actual_locators),
                }
            )
    return issues


def canonical_normalization_unit(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return re.sub(r"\s+", "", text.replace("μ", "u").replace("µ", "u"))


def canonical_direct_scalar(value: Any) -> str | None:
    text = unicodedata.normalize("NFKC", str(value if value is not None else ""))
    text = re.sub(r"\s+", "", text.replace("≥", ">=").replace("≤", "<="))
    match = SIMPLE_NORMALIZED_VALUE_RE.fullmatch(text)
    if not match:
        return None
    scalar = match.group("value").casefold()
    if scalar in {"nd", "na", "n/a"}:
        return f"{match.group('operator') or ''}{scalar}"
    return f"{match.group('operator') or ''}{Decimal(scalar).normalize()}"


def activity_normalization_issues(payload: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for evidence_kind in ("activity", "toxicity"):
        rows = payload.get(f"{evidence_kind}_records")
        if not isinstance(rows, list):
            continue
        for record_index, record in enumerate(rows):
            if not isinstance(record, dict):
                continue
            where = {
                "evidence_kind": evidence_kind,
                "record_index": record_index,
                "record_id": record.get("record_id"),
            }
            status = str(record.get("normalization_status") or "").strip().casefold()
            if status not in VALID_NORMALIZATION_STATUSES:
                issues.append(
                    {
                        "code": "invalid_normalization_status",
                        "normalization_status": record.get("normalization_status"),
                        **where,
                    }
                )
                continue
            normalized_value = record.get("normalized_value")
            normalized_unit = record.get("normalized_unit")
            if status in {"direct", "converted"} and isinstance(
                normalized_value, (dict, list, bool)
            ):
                issues.append(
                    {
                        "code": "invalid_normalized_value_shape",
                        "normalized_value_type": type(normalized_value).__name__,
                        **where,
                    }
                )
                continue
            if status in {"direct", "converted"}:
                if normalized_value is None or not str(normalized_value).strip():
                    issues.append({"code": "missing_normalized_value", **where})
                if normalized_unit is None or not str(normalized_unit).strip():
                    issues.append({"code": "missing_normalized_unit", **where})
            if status != "direct" or normalized_value is None:
                continue
            raw_scalar = canonical_direct_scalar(record.get("raw_value"))
            normalized_scalar = canonical_direct_scalar(normalized_value)
            raw_unit = canonical_normalization_unit(record.get("raw_unit"))
            direct_unit = canonical_normalization_unit(normalized_unit)
            if raw_unit and direct_unit and raw_unit != direct_unit:
                issues.append(
                    {
                        "code": "direct_normalized_unit_mismatch",
                        "raw_unit": record.get("raw_unit"),
                        "normalized_unit": normalized_unit,
                        **where,
                    }
                )
            if raw_scalar is not None and normalized_scalar is not None and raw_scalar != normalized_scalar:
                issues.append(
                    {
                        "code": "direct_normalized_value_mismatch",
                        "raw_value": record.get("raw_value"),
                        "normalized_value": normalized_value,
                        **where,
                    }
                )
    return issues


def activity_metadata_consistency_issues(payload: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    activity_records = payload.get("activity_records") if isinstance(payload.get("activity_records"), list) else []
    toxicity_records = payload.get("toxicity_records") if isinstance(payload.get("toxicity_records"), list) else []
    summary = payload.get("summary_counts") if isinstance(payload.get("summary_counts"), dict) else {}
    cited_activity_tables: set[str] = set()
    activity_table_counts: dict[str, int] = {}
    for record in activity_records:
        if not isinstance(record, dict):
            continue
        for table_locator in table_locator_ids(record_source_locators(record)):
            cited_activity_tables.add(table_locator)
            activity_table_counts[table_locator] = activity_table_counts.get(table_locator, 0) + 1

    for field, observed_count in (
        ("activity_records", len(activity_records)),
        ("toxicity_records", len(toxicity_records)),
    ):
        declared = summary.get(field)
        if isinstance(declared, int) and not isinstance(declared, bool) and declared != observed_count:
            issues.append(
                {
                    "code": f"{field[:-1]}_summary_count_mismatch",
                    "declared_count": declared,
                    "observed_count": observed_count,
                }
            )

    declared_tables = summary.get("activity_tables_accepted")
    if (
        isinstance(declared_tables, int)
        and not isinstance(declared_tables, bool)
        and declared_tables != len(cited_activity_tables)
    ):
        issues.append(
            {
                "code": "activity_table_summary_mismatch",
                "declared_count": declared_tables,
                "observed_count": len(cited_activity_tables),
                "observed_tables": sorted(cited_activity_tables),
            }
        )

    declared_locators = summary.get("accepted_activity_locators")
    if isinstance(declared_locators, dict):
        normalized_declared: dict[str, int] = {}
        for locator, raw_count in declared_locators.items():
            matches = [match.group(0) for match in TABLE_LOCATOR_RE.finditer(str(locator))]
            if len(matches) == 1 and isinstance(raw_count, int) and not isinstance(raw_count, bool):
                normalized_declared[matches[0]] = raw_count
        if normalized_declared != activity_table_counts:
            issues.append(
                {
                    "code": "accepted_activity_locator_count_mismatch",
                    "declared_counts": normalized_declared,
                    "observed_counts": activity_table_counts,
                }
            )

    quality = payload.get("quality_checks") if isinstance(payload.get("quality_checks"), dict) else {}
    field_validation = quality.get("activity_field_validation") if isinstance(quality.get("activity_field_validation"), dict) else {}
    validated_count = field_validation.get("record_count")
    if (
        isinstance(validated_count, int)
        and not isinstance(validated_count, bool)
        and validated_count != len(activity_records)
    ):
        issues.append(
            {
                "code": "activity_field_validation_count_mismatch",
                "declared_count": validated_count,
                "observed_count": len(activity_records),
            }
        )

    semantic_checks = quality.get("semantic_gate_relevant_activity_checks") if isinstance(
        quality.get("semantic_gate_relevant_activity_checks"), dict
    ) else {}
    excluded: set[str] = set()
    for key in ("non_activity_source_tables_excluded", "non_activity_source_tables_excluded_from_current_outputs"):
        values = semantic_checks.get(key)
        if isinstance(values, list):
            for value in values:
                excluded.update(table_locator_ids(value))
    conflict = cited_activity_tables & excluded
    if conflict:
        issues.append(
            {
                "code": "cited_activity_table_marked_non_activity",
                "source_locators": sorted(conflict),
            }
        )
    exclusion_fields = ("activity_tables_excluded", "activity_tables_excluded_from_current_outputs")
    table_metadata_declared = any(
        key in summary
        for key in (
            "activity_tables_accepted",
            "accepted_activity_locators",
            "activity_tables_excluded",
            "activity_tables_excluded_from_current_outputs",
            "source_tables_checked",
        )
    ) or any(key in semantic_checks for key in (
        "non_activity_source_tables_excluded",
        "non_activity_source_tables_excluded_from_current_outputs",
    ))
    if table_metadata_declared:
        declared_field = next((field for field in exclusion_fields if field in summary), None)
        declared_excluded = summary.get(declared_field) if declared_field else None
        if (
            not isinstance(declared_excluded, int)
            or isinstance(declared_excluded, bool)
            or declared_excluded != len(excluded)
        ):
            issues.append(
                {
                    "code": "activity_table_excluded_summary_mismatch",
                    "field": declared_field,
                    "declared_count": declared_excluded,
                    "observed_count": len(excluded),
                    "observed_tables": sorted(excluded),
                }
            )
        declared_checked = summary.get("source_tables_checked")
        minimum_checked = len(cited_activity_tables | excluded)
        if (
            not isinstance(declared_checked, int)
            or isinstance(declared_checked, bool)
            or declared_checked < minimum_checked
        ):
            issues.append(
                {
                    "code": "source_tables_checked_summary_mismatch",
                    "declared_count": declared_checked,
                    "minimum_expected_count": minimum_checked,
                    "observed_tables": sorted(cited_activity_tables | excluded),
                }
            )
    return issues


def expected_table_observation_issues(root: Path, paper_id: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    expected, require_cells, expected_cell_observations, issues = table_observation_contract(root, paper_id)
    issues.extend(activity_metadata_consistency_issues(payload))
    observed, duplicates = table_observation_summary(payload)
    for duplicate in duplicates:
        if duplicate["source_locator"] in expected:
            issues.append({"code": "duplicate_table_observation", **duplicate})
    for table_locator, expected_count in sorted(expected.items()):
        if observed.get(table_locator, 0) != expected_count:
            issues.append(
                {
                    "code": "table_observation_count_mismatch",
                    "source_locator": table_locator,
                    "expected_count": expected_count,
                    "observed_count": observed.get(table_locator, 0),
                }
            )
    if require_cells:
        required_tables = set(require_cells)
        records_by_table: dict[str, list[dict[str, Any]]] = {table: [] for table in required_tables}
        for record in activity_toxicity_records(payload):
            if not isinstance(record, dict):
                continue
            for table_locator in table_locator_ids(record_source_locators(record)) & required_tables:
                records_by_table[table_locator].append(record)
        for table_locator in sorted(required_tables):
            records = records_by_table[table_locator]
            complete_record_count = 0
            unique_cells: set[tuple[str, ...]] = set()
            missing_record_ids: list[Any] = []
            for record in records:
                record_cells = table_source_cell_identities(
                    record_source_locators(record), table_locator
                )
                if not record_cells:
                    missing_record_ids.append(record.get("record_id"))
                    continue
                complete_record_count += 1
                unique_cells.update(record_cells)
            exact_required_cells = require_cells[table_locator]
            expected_cell_count = (
                len(exact_required_cells)
                if exact_required_cells
                else expected.get(table_locator, 0)
            )
            matched_required_cells = {
                required_cell
                for required_cell in exact_required_cells
                if any(set(required_cell).issubset(set(cell)) for cell in unique_cells)
            }
            missing_required_cells = exact_required_cells - matched_required_cells
            unexpected_cells = (
                {
                    cell
                    for cell in unique_cells
                    if not any(
                        set(required_cell).issubset(set(cell))
                        for required_cell in exact_required_cells
                    )
                }
                if exact_required_cells
                else set()
            )
            observed_cell_count = (
                len(matched_required_cells)
                if exact_required_cells
                else len(unique_cells)
            )
            if (
                complete_record_count != len(records)
                or (exact_required_cells and (missing_required_cells or unexpected_cells))
                or (not exact_required_cells and len(unique_cells) != expected_cell_count)
            ):
                issues.append(
                    {
                        "code": "cell_locator_coverage_mismatch",
                        "source_locator": table_locator,
                        "expected_cell_count": expected_cell_count,
                        "citing_record_count": len(records),
                        "complete_cell_locator_count": complete_record_count,
                        "unique_cell_locator_count": observed_cell_count,
                        "missing_record_ids": missing_record_ids,
                        "missing_required_cells": ["|".join(item) for item in sorted(missing_required_cells)],
                        "unexpected_cells": ["|".join(item) for item in sorted(unexpected_cells)],
                    }
                )
    if expected_cell_observations:
        records = [
            (evidence_kind, record)
            for evidence_kind in ("activity", "toxicity")
            for record in (payload.get(f"{evidence_kind}_records") or [])
            if isinstance(record, dict)
        ]
        for (table_locator, cell_id), expected_fields in sorted(expected_cell_observations.items()):
            matches = [
                (evidence_kind, record)
                for evidence_kind, record in records
                if any(
                    set(cell_id).issubset(set(record_cell_id))
                    for record_cell_id in table_source_cell_identities(
                        record_source_locators(record), table_locator
                    )
                )
            ]
            locator_label = f"{table_locator}:{'|'.join(cell_id)}"
            if len(matches) != 1:
                issues.append(
                    {
                        "code": "cell_observation_record_count_mismatch",
                        "source_locator": locator_label,
                        "expected_count": 1,
                        "observed_count": len(matches),
                        "record_ids": [record.get("record_id") for _, record in matches],
                    }
                )
                continue
            evidence_kind, record = matches[0]
            field_mismatches = [
                field
                for field, expected_value in expected_fields.items()
                if normalize_contract_field(
                    evidence_kind
                    if field == "evidence_kind"
                    else record_contract_field(record, field)
                )
                != normalize_contract_field(expected_value)
            ]
            if field_mismatches:
                issues.append(
                    {
                        "code": "cell_observation_field_mismatch",
                        "source_locator": locator_label,
                        "record_id": record.get("record_id"),
                        "field_mismatches": field_mismatches,
                        "expected_fields": expected_fields,
                        "observed_fields": {
                            field: (
                                evidence_kind
                                if field == "evidence_kind"
                                else record_contract_field(record, field)
                            )
                            for field in expected_fields
                        },
                    }
                )
    return issues


def load_packet_table_text(root: Path, paper_id: str) -> dict[str, str]:
    payload = load_json(root / "packets" / paper_id / "extracted" / "pdf_tables.json")
    tables = payload.get("tables") if isinstance(payload.get("tables"), list) else []
    return {
        str(item.get("locator")): str(item.get("text") or "")
        for item in tables
        if isinstance(item, dict) and item.get("locator")
    }


def source_table_is_non_activity(text: str) -> bool:
    return bool(NON_ACTIVITY_TABLE_RE.search(text)) and not bool(ACTIVITY_TABLE_RE.search(text))


def table_has_activity_measurement(text: str) -> bool:
    normalized = " ".join(str(text or "").split())
    checks = (
        (r"inhibition\s+zone", r"\bmm\b"),
        (r"\bCFU(?:/mL)?\b|colony[- ]forming", r"(?:\d|<\s*\d)"),
        (r"\b(?:MIC|MBC|MFC)\b|minimum\s+(?:inhibitory|bactericidal|fungicidal)", r"(?:\d|ND|not detected)"),
        (r"\b(?:hemolysis|haemolysis|cytotoxicity|cell\s+viability)\b", r"%|percent|HC50|CC50|MHC"),
    )
    return any(re.search(signal, normalized, re.I) and re.search(value, normalized, re.I) for signal, value in checks)


def endpoint_supported_by_table(endpoint: Any, table_text: Any) -> bool:
    endpoint_text = " ".join(str(endpoint or "").split())
    table = " ".join(str(table_text or "").split())
    upper = endpoint_text.upper()
    endpoint_codes = (
        "MBIC50", "MBEC50", "MIC50", "MIC90", "MBC50", "MBC90",
        "MBIC", "MBEC", "MIC", "MBC", "MFC", "IC50", "EC50", "HC50", "CC50", "MHC",
    )
    for code in endpoint_codes:
        if upper == code or upper.startswith(f"{code} ") or upper.startswith(f"{code}_"):
            letters = re.match(r"[A-Z]+", code).group(0)
            digits = code[len(letters) :]
            pattern = rf"\b{re.escape(letters)}\s*{re.escape(digits)}\b" if digits else rf"\b{re.escape(code)}\b"
            return bool(re.search(pattern, table, re.I))
    lowered = endpoint_text.casefold().replace("_", " ")
    if "hemolysis" in lowered or "haemolysis" in lowered:
        return bool(re.search(r"\bha?emolysis\b", table, re.I))
    if "inhibition" in lowered and "zone" in lowered:
        return bool(re.search(r"\binhibition\b", table, re.I) and re.search(r"\bzone\b", table, re.I))
    if "cfu" in lowered or "viable count" in lowered:
        return bool(re.search(r"\bCFU(?:/mL)?\b|colony[- ]forming", table, re.I))
    if lowered == "fici" or "fractional inhibitory concentration" in lowered:
        return bool(re.search(r"\bFICI?\b|fraction(?:al)?\s+inhibitory\s+concentration", table, re.I))
    return True


def endpoint_table_support_issues(
    table_text_by_locator: dict[str, str], payload: dict[str, Any]
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for record in activity_toxicity_records(payload):
        if not isinstance(record, dict):
            continue
        locators = record_source_locators(record)
        endpoint = record.get("endpoint")
        for table_locator in sorted(table_locator_ids(locators)):
            if not table_source_cell_identities(locators, table_locator):
                continue
            table_text = table_text_by_locator.get(table_locator, "")
            if table_text and not endpoint_supported_by_table(endpoint, table_text):
                issues.append(
                    {
                        "code": "cell_endpoint_not_supported_by_cited_table",
                        "record_id": record.get("record_id"),
                        "endpoint": endpoint,
                        "source_locator": table_locator,
                    }
                )
    return issues


def ambiguous_shared_table_row_issues(payload: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[tuple[int, dict[str, Any]]]] = {}
    for record_index, record in enumerate(activity_toxicity_records(payload)):
        if not isinstance(record, dict):
            continue
        locators = record_source_locators(record)
        for table_locator in sorted(table_locator_ids(locators)):
            complete_cells = table_source_cell_identities(locators, table_locator)
            complete_rows = {
                marker
                for cell in complete_cells
                for marker in cell
                if marker.startswith("row=")
            }
            for row_identity in table_source_row_identities(locators, table_locator):
                if row_identity not in complete_rows:
                    grouped.setdefault((table_locator, row_identity), []).append(
                        (record_index, record)
                    )

    issues: list[dict[str, Any]] = []
    for (table_locator, row_identity), records in sorted(grouped.items()):
        unique_records: dict[int, dict[str, Any]] = {
            record_index: record for record_index, record in records
        }
        if len(unique_records) < 2:
            continue
        ordered_records = [unique_records[index] for index in sorted(unique_records)]
        issues.append(
            {
                "code": "ambiguous_shared_table_row_locator",
                "source_locator": f"{table_locator}:{row_identity}",
                "record_count": len(ordered_records),
                "record_ids": [record.get("record_id") for record in ordered_records],
            }
        )
    return issues


def source_located_toxicity_candidate_issues(payload: dict[str, Any]) -> list[dict[str, Any]]:
    toxicity_records = payload.get("toxicity_records")
    if isinstance(toxicity_records, list) and toxicity_records:
        return []
    issues: list[dict[str, Any]] = []
    for container_name in (
        "excluded_machine_candidate_rows",
        "candidate_or_rejected_rows",
        "rejected_activity_records",
    ):
        candidates = payload.get(container_name)
        if not isinstance(candidates, list):
            continue
        for candidate_index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                continue
            endpoint = str(
                candidate.get("candidate_endpoint")
                or candidate.get("endpoint")
                or candidate.get("raw_endpoint_label")
                or ""
            )
            if not TOXICITY_ENDPOINT_RE.search(endpoint):
                continue
            if not source_locator_ids(record_source_locators(candidate)):
                continue
            issues.append(
                {
                    "code": "source_located_toxicity_candidate_excluded_without_records",
                    "container": container_name,
                    "candidate_index": candidate_index,
                    "record_id": candidate.get("record_id"),
                    "endpoint": endpoint,
                }
            )
    return issues


def activity_redundant_field_issues(payload: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for evidence_kind in ("activity", "toxicity"):
        records = payload.get(f"{evidence_kind}_records")
        if not isinstance(records, list):
            continue
        for record_index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            conditions = (
                record.get("assay_conditions")
                if isinstance(record.get("assay_conditions"), dict)
                else {}
            )
            top_concentration = record_contract_field(record, "concentration")
            nested_concentration = (
                conditions.get("peptide_concentration")
                or conditions.get("concentration")
                or conditions.get("sample_concentration")
            )
            if top_concentration not in (None, "") and nested_concentration not in (None, ""):
                top_scalar = canonical_direct_scalar(top_concentration)
                nested_scalar = canonical_direct_scalar(nested_concentration)
                values_match = (
                    top_scalar == nested_scalar
                    if top_scalar is not None and nested_scalar is not None
                    else normalize_contract_field(top_concentration)
                    == normalize_contract_field(nested_concentration)
                )
                if not values_match:
                    issues.append(
                        {
                            "code": "assay_condition_concentration_mismatch",
                            "evidence_kind": evidence_kind,
                            "record_index": record_index,
                            "record_id": record.get("record_id"),
                            "top_level_concentration": top_concentration,
                            "assay_condition_concentration": nested_concentration,
                        }
                    )
            top_unit = record.get("concentration_unit")
            nested_unit = (
                conditions.get("peptide_concentration_unit")
                or conditions.get("concentration_unit")
                or conditions.get("sample_concentration_unit")
            )
            if (
                top_unit not in (None, "")
                and nested_unit not in (None, "")
                and canonical_normalization_unit(top_unit)
                != canonical_normalization_unit(nested_unit)
            ):
                issues.append(
                    {
                        "code": "assay_condition_concentration_unit_mismatch",
                        "evidence_kind": evidence_kind,
                        "record_index": record_index,
                        "record_id": record.get("record_id"),
                        "top_level_concentration_unit": top_unit,
                        "assay_condition_concentration_unit": nested_unit,
                    }
                )
    return issues


def evidence_kind_endpoint_issues(payload: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for record_index, record in enumerate(payload.get("activity_records") or []):
        if not isinstance(record, dict):
            continue
        endpoint = str(record.get("endpoint") or "")
        if TOXICITY_ENDPOINT_RE.search(endpoint):
            issues.append(
                {
                    "code": "toxicity_endpoint_in_activity_records",
                    "record_index": record_index,
                    "record_id": record.get("record_id"),
                    "endpoint": endpoint,
                }
            )
    for record_index, record in enumerate(payload.get("toxicity_records") or []):
        if not isinstance(record, dict):
            continue
        endpoint = str(record.get("endpoint") or "")
        if ANTIMICROBIAL_ENDPOINT_RE.search(endpoint):
            issues.append(
                {
                    "code": "activity_endpoint_in_toxicity_records",
                    "record_index": record_index,
                    "record_id": record.get("record_id"),
                    "endpoint": endpoint,
                }
            )
    return issues


def source_review_depth_covers(depth: Any, key: str) -> bool:
    if not depth:
        return False
    synonyms = SOURCE_DEPTH_SYNONYMS[key]
    if isinstance(depth, dict):
        for synonym in synonyms:
            if synonym in depth:
                return True
        unavailable = depth.get("unavailable_sources") or depth.get("unavailable")
        if unavailable and any(synonym in text_blob(unavailable) for synonym in synonyms):
            return True
    return any(synonym in text_blob(depth) for synonym in synonyms)


def source_assets_present(base: Path) -> dict[str, bool]:
    source = base / "source"
    supplementary = source / "supplementary"
    return {
        "paper_xml": (source / "paper.xml").exists(),
        "paper_pdf": (source / "paper.pdf").exists(),
        "oa_package": any(source.glob("*package*")) or any(source.glob("*.tar.gz")) or any(source.glob("*.zip")),
        "supplementary_assets": supplementary.exists() and any(path.is_file() for path in supplementary.rglob("*")),
    }


def concrete_rework_targets(targets: Any) -> list[dict[str, Any]]:
    if not isinstance(targets, list):
        return []
    concrete: list[dict[str, Any]] = []
    for target in targets:
        if not isinstance(target, dict):
            continue
        worker = str(target.get("worker") or target.get("owner") or target.get("lane") or "").strip()
        action = any(str(target.get(key) or "").strip() for key in ("required_action", "action", "fix", "request"))
        subject = any(
            str(target.get(key) or "").strip()
            for key in (
                "artifact_path",
                "path",
                "record_id",
                "row_id",
                "claim_id",
                "failure_type",
                "code",
                "example",
            )
        )
        if worker.startswith("worker-") and action and subject:
            concrete.append(target)
    return concrete


def record_status(record: dict[str, Any]) -> str:
    return str(record.get("layer1_status") or record.get("status") or record.get("overall_status") or "").strip()


def sequence_locator_is_weak(record: dict[str, Any]) -> bool:
    sequence_check = record.get("sequence_check") if isinstance(record.get("sequence_check"), dict) else {}
    locator = sequence_check.get("source_locator")
    if not source_locator_has_anchor(locator):
        return True
    if isinstance(locator, dict):
        figure_locator = str(locator.get("figure_locator") or "").strip()
        supps = locator.get("supplementary_sources")
        has_supp = isinstance(supps, list) and any(str(item).strip() for item in supps)
        statement = str(locator.get("primary_source_statement") or "")
        if not figure_locator and not has_supp and re.search(r"exact sequence is not embedded|not embedded in extracted xml", statement, re.I):
            return True
    return False


def conflict_context_present(record: dict[str, Any]) -> bool:
    if record.get("conflict_flags"):
        return True
    for key in ("review_notes", "conflict_reason", "conflict_context", "caution", "notes"):
        value = record.get(key)
        if value and "conflict" in text_blob(value):
            return True
    for key in (
        "source_organism_check",
        "source_organism_agreement",
        "name_check",
        "sequence_check",
        "identity_assessment",
        "primary_source_identity_evidence",
    ):
        if "conflict" in text_blob(record.get(key)):
            return True
    return False


def unresolved_reason_present(record: dict[str, Any]) -> bool:
    if conflict_context_present(record):
        return True
    return any(
        str(record.get(key) or "").strip()
        for key in (
            "not_source_verified_reason",
            "worker4_disposition",
            "unresolved_reason",
            "status_reason",
            "review_notes",
        )
    )


def unit_present(record: dict[str, Any]) -> bool:
    if str(record.get("raw_unit") or "").strip():
        return True
    context = record.get("source_column_context") if isinstance(record.get("source_column_context"), dict) else {}
    for value in context.values():
        if re.search(r"(?:ug/ml|µg/ml|μg/ml|uM|µM|μM|mg/L|%|OD|mm)", str(value), re.I):
            return True
    locator = record.get("source_locator")
    if isinstance(locator, dict) and re.search(r"(?:ug/ml|µg/ml|μg/ml|uM|µM|μM|mg/L|%)", json.dumps(locator, ensure_ascii=False), re.I):
        return True
    return False


def paper_ids_from_manifest(path: Path) -> list[str]:
    data = load_json(path)
    if any(key in data for key in ("_missing", "_parse_error", "_not_object")):
        raise SystemExit(f"invalid or missing manifest: {path}")
    ids = data.get("paper_ids")
    if isinstance(ids, list):
        out = [str(item) for item in ids if str(item).strip()]
        if not out:
            raise SystemExit(f"manifest has no paper ids: {path}")
        return out
    papers = data.get("papers")
    if isinstance(papers, list):
        out: list[str] = []
        for item in papers:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                value = item.get("paper_id") or item.get("id") or item.get("pmcid")
                if value:
                    out.append(str(value))
        if out:
            return out
    raise SystemExit(f"manifest has no paper ids: {path}")


def check_paper(root: Path, paper_id: str) -> dict[str, Any]:
    base = root / "papers" / paper_id
    issues: list[dict[str, Any]] = []
    table_text_by_locator = load_packet_table_text(root, paper_id)
    review: dict[str, Any] = {}
    review_status = ""
    rework_targets: Any = None

    review = load_json(base / "final" / "review_report.json")
    if review.get("_missing"):
        issues.append({"severity": "hard", "layer": "review", "code": "missing_review_report"})
    else:
        review_status = str(review.get("review_status") or "").strip()
        rework_targets = review.get("rework_targets")
        summary = str(review.get("summary") or review.get("adjudication_summary") or "")
        if summary.strip() == TEMPLATE_SUMMARY:
            issues.append({"severity": "hard", "layer": "review", "code": "templated_review_summary"})
        if not (review.get("reviewed_at") or review.get("updated_at") or review.get("created_at")):
            issues.append({"severity": "hard", "layer": "review", "code": "missing_review_timestamp"})
        if review.get("review_model") not in {"gpt-5.5", "GPT-5.5"}:
            issues.append({"severity": "hard", "layer": "review", "code": "missing_gpt55_review_model"})
        if str(review.get("reasoning_effort") or "").lower() != "xhigh":
            issues.append({"severity": "hard", "layer": "review", "code": "missing_xhigh_reasoning_effort"})
        if review_status == "accepted_clean" and review.get("caution_findings"):
            issues.append({"severity": "hard", "layer": "review", "code": "accepted_clean_with_cautions"})
        if review_status not in VALID_REVIEW_STATUSES:
            issues.append({"severity": "hard", "layer": "review", "code": "invalid_review_status", "value": review.get("review_status")})
        if review_status not in PUBLICATION_GRADE_STATUSES:
            issues.append({"severity": "hard", "layer": "review", "code": "review_status_not_publication_grade", "value": review.get("review_status")})
        if review.get("publication_grade") is not True:
            issues.append({"severity": "hard", "layer": "review", "code": "publication_grade_not_true", "value": review.get("publication_grade")})
        if review_status == "needs_targeted_rework" and not concrete_rework_targets(rework_targets):
            issues.append({"severity": "hard", "layer": "review", "code": "missing_concrete_rework_targets"})
        if review_status in PUBLICATION_GRADE_STATUSES and concrete_rework_targets(rework_targets):
            issues.append({"severity": "hard", "layer": "review", "code": "accepted_review_has_unresolved_rework_targets"})
        depth = review.get("source_review_depth")
        if not depth:
            issues.append({"severity": "hard", "layer": "review", "code": "missing_source_review_depth"})
        else:
            assets = source_assets_present(base)
            for key in ("paper_xml", "paper_pdf", "oa_package", "supplementary_assets", "merged_database_rows"):
                if not source_review_depth_covers(depth, key):
                    issue = {"severity": "hard", "layer": "review", "code": f"missing_source_review_depth_{key}"}
                    if key in assets:
                        issue["source_asset_present"] = assets[key]
                    issues.append(issue)
        materials = review.get("materials_exhausted")
        if not materials:
            issues.append({"severity": "hard", "layer": "review", "code": "missing_materials_exhausted"})
        else:
            for key in ("paper_xml", "paper_pdf", "oa_package", "supplementary_assets", "merged_database_rows"):
                if not source_review_depth_covers(materials, key):
                    issues.append({"severity": "hard", "layer": "review", "code": f"missing_materials_exhausted_{key}"})

    activity = load_json(base / "final" / "activity_toxicity_evidence.json")
    records = activity.get("activity_records") if isinstance(activity.get("activity_records"), list) else []
    table_evidence_records = activity_toxicity_records(activity)
    if not records:
        issues.append({"severity": "hard", "layer": "activity", "code": "missing_activity_records"})
    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        endpoint = str(record.get("endpoint") or "").strip()
        raw_value_obj = record.get("raw_value")
        raw_value = "" if raw_value_obj is None else str(raw_value_obj).strip()
        species = target_species(record)
        locator = record_source_locators(record)
        where = {"record_index": idx, "record_id": record.get("record_id")}
        if endpoint.lower() in GENERIC_ENDPOINTS:
            issues.append({"severity": "hard", "layer": "activity", "code": "generic_endpoint", **where})
        if endpoint.upper() in MIC_LIKE and not unit_present(record):
            issues.append({"severity": "hard", "layer": "activity", "code": "mic_like_missing_unit", **where})
        if not raw_value:
            issues.append({"severity": "hard", "layer": "activity", "code": "missing_raw_value", **where})
        if not species:
            issues.append({"severity": "hard", "layer": "activity", "code": "missing_target_species", **where})
        elif species_is_sentence_fragment(species):
            issues.append({"severity": "hard", "layer": "activity", "code": "sentence_fragment_species", "species": species[:80], **where})
        if species_is_non_biological_label(species):
            issues.append({"severity": "hard", "layer": "activity", "code": "non_biological_target_label", "species": species[:80], **where})
        if not source_locator_has_anchor(locator):
            issues.append({"severity": "hard", "layer": "activity", "code": "missing_source_locator", **where})
    toxicity_records = activity.get("toxicity_records") if isinstance(activity.get("toxicity_records"), list) else []
    toxicity_record_ids = {id(record) for record in toxicity_records}
    for idx, record in enumerate(table_evidence_records):
        if not isinstance(record, dict):
            continue
        locator = record_source_locators(record)
        for table_locator in sorted(table_locator_ids(locator)):
            table_text = table_text_by_locator.get(table_locator, "")
            if table_text and source_table_is_non_activity(table_text):
                issues.append(
                    {
                        "severity": "hard",
                        "layer": "activity",
                        "code": "non_activity_source_table",
                        "source_locator": table_locator,
                        "evidence_kind": "toxicity" if id(record) in toxicity_record_ids else "activity",
                        "record_index": idx,
                        "record_id": record.get("record_id"),
                    }
                )
    cited_activity_tables: set[str] = set()
    for record in table_evidence_records:
        if not isinstance(record, dict):
            continue
        cited_activity_tables.update(table_locator_ids(record_source_locators(record)))
    for table_locator, table_text in table_text_by_locator.items():
        if table_has_activity_measurement(table_text) and table_locator not in cited_activity_tables:
            issues.append(
                {
                    "severity": "hard",
                    "layer": "activity",
                    "code": "missing_activity_table_coverage",
                    "source_locator": table_locator,
                }
            )
    for mismatch in expected_table_observation_issues(root, paper_id, activity):
        code = str(mismatch.get("code") or "table_observation_contract_invalid")
        issues.append(
            {
                "severity": "hard",
                "layer": "activity",
                "code": code,
                **{key: value for key, value in mismatch.items() if key != "code"},
            }
        )
    for mismatch in expected_non_table_observation_issues(root, paper_id, activity):
        code = str(mismatch.get("code") or "non_table_observation_contract_invalid")
        issues.append(
            {
                "severity": "hard",
                "layer": "activity",
                "code": code,
                **{key: value for key, value in mismatch.items() if key != "code"},
            }
        )
    for mismatch in expected_evidence_kind_count_issues(root, paper_id, activity):
        code = str(mismatch.get("code") or "evidence_kind_count_contract_invalid")
        issues.append(
            {
                "severity": "hard",
                "layer": "activity",
                "code": code,
                **{key: value for key, value in mismatch.items() if key != "code"},
            }
        )
    for mismatch in endpoint_table_support_issues(table_text_by_locator, activity):
        code = str(mismatch.get("code") or "cell_endpoint_table_support_invalid")
        issues.append(
            {
                "severity": "hard",
                "layer": "activity",
                "code": code,
                **{key: value for key, value in mismatch.items() if key != "code"},
            }
        )
    for mismatch in ambiguous_shared_table_row_issues(activity):
        code = str(mismatch.get("code") or "ambiguous_shared_table_row_locator")
        issues.append(
            {
                "severity": "hard",
                "layer": "activity",
                "code": code,
                **{key: value for key, value in mismatch.items() if key != "code"},
            }
        )
    for mismatch in source_located_toxicity_candidate_issues(activity):
        code = str(
            mismatch.get("code")
            or "source_located_toxicity_candidate_excluded_without_records"
        )
        issues.append(
            {
                "severity": "hard",
                "layer": "toxicity",
                "code": code,
                **{key: value for key, value in mismatch.items() if key != "code"},
            }
        )
    for mismatch in activity_redundant_field_issues(activity):
        code = str(mismatch.get("code") or "activity_redundant_field_mismatch")
        issues.append(
            {
                "severity": "hard",
                "layer": "activity",
                "code": code,
                **{key: value for key, value in mismatch.items() if key != "code"},
            }
        )
    for mismatch in evidence_kind_endpoint_issues(activity):
        code = str(mismatch.get("code") or "evidence_kind_endpoint_mismatch")
        issues.append(
            {
                "severity": "hard",
                "layer": "activity",
                "code": code,
                **{key: value for key, value in mismatch.items() if key != "code"},
            }
        )
    for mismatch in activity_normalization_issues(activity):
        code = str(mismatch.get("code") or "activity_normalization_invalid")
        issues.append(
            {
                "severity": "hard",
                "layer": "activity",
                "code": code,
                **{key: value for key, value in mismatch.items() if key != "code"},
            }
        )

    database = load_json(base / "final" / "database_record_verification.json")
    audits = database.get("record_audits") if isinstance(database.get("record_audits"), list) else []
    if database.get("_missing"):
        issues.append({"severity": "hard", "layer": "database", "code": "missing_database_record_verification"})
    for idx, record in enumerate(audits):
        if not isinstance(record, dict):
            continue
        status = record_status(record)
        where = {"record_index": idx, "record_id": record.get("sequence_key") or record.get("source_id")}
        if status == "source_verified" and sequence_locator_is_weak(record):
            issues.append({"severity": "hard", "layer": "database", "code": "source_verified_without_primary_sequence_locator", **where})
        if status == "source_conflict" and not conflict_context_present(record):
            issues.append({"severity": "hard", "layer": "database", "code": "source_conflict_missing_context", **where})
        if status in {"unresolved_record", "database_only_no_primary_source", "sequence_modified_not_normalized"}:
            if not unresolved_reason_present(record) and not source_locator_has_anchor(record.get("traceability") or record.get("citation_traceability")):
                issues.append({"severity": "hard", "layer": "database", "code": "unresolved_record_missing_reason", **where})

    mechanism = load_json(base / "final" / "mechanism_ontology_record.json")
    claims = mechanism.get("mechanism_claims") if isinstance(mechanism.get("mechanism_claims"), list) else []
    for idx, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        where = {"claim_index": idx, "claim_id": claim.get("claim_id")}
        if not claim.get("claim_id"):
            issues.append({"severity": "hard", "layer": "mechanism", "code": "missing_claim_id", **where})
        if not str(claim.get("claim_text") or "").strip():
            issues.append({"severity": "hard", "layer": "mechanism", "code": "missing_claim_text", **where})
        if claim.get("evidence_class") == "direct_mechanism" and not claim.get("direct_assay_types"):
            issues.append({"severity": "hard", "layer": "mechanism", "code": "direct_mechanism_without_assay", **where})
        if not source_locator_has_anchor(record_source_locators(claim)):
            issues.append({"severity": "hard", "layer": "mechanism", "code": "missing_mechanism_locator", **where})

    supp = load_json(base / "work" / "supplementary_methods" / "supplementary_evidence.json")
    for idx, item in enumerate(supp.get("evidence_items") if isinstance(supp.get("evidence_items"), list) else []):
        if not isinstance(item, dict):
            continue
        text = " ".join(str(item.get(k) or "") for k in ("summary", "evidence_text", "notes"))
        if BOILERPLATE_RE.search(text):
            issues.append({"severity": "hard", "layer": "supplementary", "code": "publisher_boilerplate_supplement_text", "item_index": idx})

    hard_issues = [issue for issue in issues if issue.get("severity") == "hard"]
    hard_non_review_issues = [issue for issue in hard_issues if issue.get("layer") != "review"]
    if review and not review.get("_missing"):
        if review_status in PUBLICATION_GRADE_STATUSES and hard_non_review_issues:
            issues.append({"severity": "hard", "layer": "review", "code": "accepted_despite_hard_gate_issues"})
        if hard_non_review_issues and not concrete_rework_targets(rework_targets):
            issues.append({"severity": "hard", "layer": "review", "code": "missing_rework_targets_for_hard_gate_issues"})

    return {
        "paper_id": paper_id,
        "publication_grade_pass": not any(issue.get("severity") == "hard" for issue in issues),
        "issue_count": len(issues),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run strict semantic gate over AMP three-layer artifacts.")
    parser.add_argument("--root", default=".")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--manifest")
    group.add_argument("--paper-id")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    paper_ids = [args.paper_id] if args.paper_id else paper_ids_from_manifest(root / args.manifest)
    results = [check_paper(root, pid) for pid in paper_ids]
    failed = [item for item in results if not item["publication_grade_pass"]]
    summary = {
        "paper_count": len(results),
        "publication_grade_pass_count": len(results) - len(failed),
        "publication_grade_fail_count": len(failed),
        "failed_papers": [item["paper_id"] for item in failed],
        "results": results,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"publication_grade_pass={summary['publication_grade_pass_count']}/{summary['paper_count']}")
        if failed:
            print("failed_papers:")
            for item in failed[:50]:
                codes = ", ".join(issue["code"] for issue in item["issues"][:8])
                print(f"- {item['paper_id']}: {item['issue_count']} issues ({codes})")
            if len(failed) > 50:
                print(f"... {len(failed)-50} more")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
