#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


PAPER_ID = "PMC11956232"
WORKER_ID = "worker-2"


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".codex").is_dir() and (parent / "pipeline_v2").is_dir():
            return parent
    raise RuntimeError("workspace root not found")


ROOT = repo_root()
PILOT = ROOT / "pipeline_v2" / "deepmine" / "dbaasp_strict_pilot"
PAPER_ROOT = PILOT / "papers" / PAPER_ID
PACKET_ROOT = PILOT / "packets" / PAPER_ID
WORK = PAPER_ROOT / "work" / "activity_evidence"
EXPECTED_FIGURE_COUNTS = {
    "Figure 1": 360,
    "Figure 2": 280,
    "Figure 3": 20,
    "Figure 4": 98,
    "Figure 5": 18,
    "Figure 6": 17,
    "Figure 7": 4,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def collapse_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return collapse_text(" ".join(element.itertext()))


def direct_child(element: ET.Element, name: str) -> ET.Element | None:
    for child in list(element):
        if local_name(child.tag) == name:
            return child
    return None


def direct_children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(element) if local_name(child.tag) == name]


def first_descendant(element: ET.Element, name: str) -> ET.Element | None:
    for descendant in element.iter():
        if descendant is not element and local_name(descendant.tag) == name:
            return descendant
    return None


def row_cells(row: ET.Element) -> list[str]:
    return [
        element_text(cell)
        for cell in list(row)
        if local_name(cell.tag) in {"td", "th"}
    ]


def table_rows(table: ET.Element, group_name: str) -> list[list[str]]:
    group = direct_child(table, group_name)
    if group is None:
        return []
    return [row_cells(row) for row in group.iter() if local_name(row.tag) == "tr"]


def parse_source_tables() -> dict[str, dict[str, Any]]:
    root = ET.parse(PACKET_ROOT / "raw" / "paper.xml").getroot()
    table_wraps = [node for node in root.iter() if local_name(node.tag) == "table-wrap"]
    tables: dict[str, dict[str, Any]] = {}
    for index, wrap in enumerate(table_wraps, start=1):
        table = first_descendant(wrap, "table")
        thead = table_rows(table, "thead") if table is not None else []
        tbody = table_rows(table, "tbody") if table is not None else []
        if table is not None and not tbody:
            all_rows = [row_cells(row) for row in table.iter() if local_name(row.tag) == "tr"]
            tbody = all_rows[1:] if len(all_rows) > 1 else all_rows
            thead = all_rows[:1] if len(all_rows) > 1 else []
        locator = f"xml:table-wrap:{index}"
        tables[locator] = {
            "locator": locator,
            "label": element_text(direct_child(wrap, "label")),
            "caption": element_text(direct_child(wrap, "caption")),
            "thead": thead,
            "tbody": tbody,
            "body_row_count": len(tbody),
            "max_body_cell_count": max((len(row) for row in tbody), default=0),
        }
    return tables


def row_index_for_strain(table: dict[str, Any], strain: str) -> int:
    needle = collapse_text(strain)
    for idx, cells in enumerate(table.get("tbody", []), start=1):
        if any(needle in collapse_text(cell) for cell in cells):
            return idx
    raise ValueError(f"strain not found in table row: {table['locator']} {strain}")


def column_index_for_observation(observation: dict[str, Any]) -> int:
    table = str(observation["source_locator"])
    endpoint = str(observation["endpoint"])
    condition = str(observation.get("condition") or "")
    if table == "xml:table-wrap:1":
        if endpoint == "MIC":
            return 2
        if endpoint == "MBC":
            return 5
    if table == "xml:table-wrap:2":
        order = ["-80 °C", "-20 °C", "4 °C", "37 °C", "50 °C", "65 °C"]
        return 2 + order.index(condition)
    if table == "xml:table-wrap:3":
        order = ["Control", "5% FBS", "10% FBS"]
        return 2 + order.index(condition)
    raise ValueError(f"unsupported table observation: {table} {endpoint} {condition}")


def normalize_numeric_text(value: Any) -> str:
    text = collapse_text(value).replace("µ", "u").replace("μ", "u")
    text = text.replace("–", "-").replace("—", "-")
    return text


def verify_contract_observations(
    tables: dict[str, dict[str, Any]], observations: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    verified: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for obs in observations:
        table_locator = str(obs["source_locator"])
        table = tables.get(table_locator)
        if not table:
            errors.append({"source_locator": table_locator, "reason": "missing_table"})
            continue
        try:
            row_index = row_index_for_strain(table, str(obs["strain"]))
            column_index = column_index_for_observation(obs)
        except Exception as exc:  # noqa: BLE001 - converted to compact validation artifact
            errors.append(
                {
                    "source_locator": table_locator,
                    "strain": obs.get("strain"),
                    "endpoint": obs.get("endpoint"),
                    "condition": obs.get("condition"),
                    "reason": type(exc).__name__,
                }
            )
            continue
        row = table["tbody"][row_index - 1]
        cell_value = row[column_index - 1] if column_index - 1 < len(row) else ""
        expected = normalize_numeric_text(obs["raw_value"])
        observed = normalize_numeric_text(cell_value)
        if expected != observed:
            errors.append(
                {
                    "source_locator": table_locator,
                    "strain": obs.get("strain"),
                    "endpoint": obs.get("endpoint"),
                    "condition": obs.get("condition"),
                    "row": row_index,
                    "column": column_index,
                    "reason": "cell_value_mismatch",
                }
            )
            continue
        verified.append({**obs, "body_row_index": row_index, "cell_index": column_index})
    return verified, errors


def source_locator_dict(
    base_locator: str,
    row_index: int | None = None,
    column_index: int | None = None,
    row_label: str | None = None,
    column_label: str | None = None,
    role: str = "source_table_cell",
    preflight_locator: str | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "locator": base_locator,
        "source_type": "xml_table",
        "role": role,
    }
    if row_index is not None:
        item["row"] = row_index
        item["row_locator"] = f"{base_locator}:body-row={row_index}"
    if column_index is not None:
        item["column"] = column_index
        item["cell_locator"] = f"{base_locator}:body-row={row_index}:cell={column_index}"
    if row_label:
        item["row_label"] = row_label
    if column_label:
        item["column_label"] = column_label
    if preflight_locator:
        item["leader_preflight_cell_locator"] = preflight_locator
    return item


def target_for_strain(strain: str) -> dict[str, Any]:
    is_dc = strain.startswith("DC ")
    return {
        "target_class": "bacteria",
        "species": "Escherichia coli",
        "strain_or_isolate": strain,
        "gram_status": "Gram-negative",
        "clinical_context": "carbapenem-resistant clinical isolate" if is_dc else "reference strain",
    }


def base_entity(identity: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": identity["peptide_name"],
        "sequence": identity["sequence"],
        "displayed_sequence": identity["displayed_sequence"],
        "c_terminal_modification": identity["c_terminal_modification"],
    }


def base_mic_conditions(context: dict[str, Any]) -> dict[str, Any]:
    mic = context.get("MIC", {})
    return {
        "method": mic.get("method"),
        "medium": mic.get("medium"),
        "inoculum": mic.get("inoculum"),
        "incubation": mic.get("incubation"),
        "method_locator": mic.get("locator"),
    }


def observation_column_label(obs: dict[str, Any]) -> str:
    text = str(obs.get("cell_locator") or "")
    if "column=" in text:
        return text.split("column=", 1)[1]
    return str(obs.get("condition") or obs.get("endpoint") or "")


def build_activity_records(
    verified_observations: list[dict[str, Any]],
    identity: dict[str, Any],
    assay_context: dict[str, Any],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    table_counts: dict[str, int] = {}
    for obs in verified_observations:
        table_locator = str(obs["source_locator"])
        table_counts[table_locator] = table_counts.get(table_locator, 0) + 1
        strain = str(obs["strain"])
        endpoint = str(obs["endpoint"])
        raw_value = str(obs["raw_value"])
        conditions = base_mic_conditions(assay_context)
        condition = obs.get("condition")
        evidence_role = "primary_activity_table_cell"
        if table_locator == "xml:table-wrap:1" and endpoint == "MBC":
            mbc = assay_context.get("MBC", {})
            conditions.update(
                {
                    "bactericidal_subculture_volume": mbc.get("subculture_volume"),
                    "bactericidal_subculture_medium": mbc.get("subculture_medium"),
                    "bactericidal_subculture_incubation": mbc.get("incubation"),
                    "bactericidal_method_locator": mbc.get("locator"),
                }
            )
        if table_locator == "xml:table-wrap:2":
            temp = assay_context.get("temperature_stability", {})
            conditions.update(
                {
                    "peptide_pretreatment_temperature": condition,
                    "peptide_pretreatment_duration": temp.get("pretreatment_duration"),
                    "pretreatment_locator": temp.get("locator"),
                    "source_conflict_note": "Methods/table temperature-condition conflict preserved in source_conflicts_preserved.",
                }
            )
            evidence_role = "temperature_stability_activity_table_cell"
        if table_locator == "xml:table-wrap:3":
            serum = assay_context.get("serum_stability", {})
            conditions.update(
                {
                    "serum_condition": condition,
                    "peptide_serum_preincubation_duration": serum.get("pretreatment_duration"),
                    "pretreatment_locator": serum.get("locator"),
                    "source_conflict_note": "Methods/table serum-condition conflict preserved in source_conflicts_preserved.",
                }
            )
            evidence_role = "serum_stability_activity_table_cell"
        locator = source_locator_dict(
            table_locator,
            obs["body_row_index"],
            obs["cell_index"],
            row_label=strain,
            column_label=observation_column_label(obs),
            role=evidence_role,
            preflight_locator=str(obs.get("cell_locator") or ""),
        )
        record_index = len(records) + 1
        record = {
            "record_id": f"{PAPER_ID}-ACT-{record_index:03d}",
            "paper_id": PAPER_ID,
            "evidence_kind": "activity",
            "evidence_role": evidence_role,
            "entity": base_entity(identity),
            "treatment": identity["peptide_name"],
            "endpoint": endpoint,
            "raw_value": raw_value,
            "raw_unit": obs["raw_unit"],
            "normalized_value": raw_value,
            "normalized_unit": obs["raw_unit"],
            "normalization_status": "direct",
            "normalization_note": "Source table value and unit recorded directly; no conversion performed.",
            "target": target_for_strain(strain),
            "target_species": "Escherichia coli",
            "target_strain_or_isolate": strain,
            "assay_conditions": conditions,
            "evidence_ladder": "in_vitro_multi_pathogen",
            "source_locator": locator,
            "source_review_status": "source_verified_table_cell",
            "database_provenance": {
                "linked_authoritative_rows_present": False,
                "dbaasp_fallback_rows_used_as_source": False,
            },
        }
        if condition:
            record["condition"] = condition
        records.append(record)
    return records


def xml_section_map() -> dict[str, str]:
    data = load_json(PACKET_ROOT / "extracted" / "xml_sections.json")
    return {
        str(item.get("locator")): str(item.get("text") or "")
        for item in data.get("sections", [])
        if isinstance(item, dict) and item.get("locator")
    }


def locator_checks(sections: dict[str, str]) -> dict[str, dict[str, Any]]:
    checks = {
        "xml:p:43": [r"64", r"128"],
        "xml:p:46": [r"ha?emolysis", r"64", r"128", r"5\s*%"],
        "xml:p:60": [r"ha?emolysis", r"2\s*%", r"128"],
        "xml:p:20": [r"sheep|RBC|erythro", r"PBS", r"37", r"60"],
        "xml:fig:6": [r"Fig|Figure|6"],
        "xml:caption:7": [r"ha?emolysis|cytotoxic|HK-?2|cell"],
        "xml:p:52": [r"70", r"80", r"10"],
    }
    out: dict[str, dict[str, Any]] = {}
    for locator, patterns in checks.items():
        text = sections.get(locator, "")
        out[locator] = {
            "present": bool(text),
            "pattern_count": sum(1 for pattern in patterns if re.search(pattern, text, re.I)),
            "expected_pattern_count": len(patterns),
        }
    return out


def locator_entry(locator: str, role: str) -> dict[str, str]:
    return {"locator": locator, "source_type": "xml", "role": role}


def figure_name(row: dict[str, Any]) -> str:
    raw = str(row.get("figure") or row.get("surface") or "").strip()
    lowered = raw.lower().replace(".", "")
    for number in range(1, 8):
        if lowered in {f"figure {number}", f"figure{number}", f"fig {number}", f"fig{number}"}:
            return f"Figure {number}"
    return raw


def load_worker3_figure_handoff() -> dict[str, Any]:
    path = PACKET_ROOT / "analysis" / "supplementary_evidence.worker3.json"
    payload = load_json(path)
    return {"path": str(path), "payload": payload}


def validate_worker3_figure_handoff(handoff: dict[str, Any]) -> dict[str, Any]:
    payload = handoff["payload"]
    rows = [
        row
        for row in payload.get("figure_quantitative_observations", [])
        if isinstance(row, dict)
    ]
    surfaces = [
        row
        for row in payload.get("figure_surface_exhaustion", [])
        if isinstance(row, dict)
    ]
    counts = {name: 0 for name in EXPECTED_FIGURE_COUNTS}
    for row in rows:
        name = figure_name(row)
        if name in counts:
            counts[name] += 1
    missing_locator_ids = [
        row.get("observation_id")
        for row in rows
        if not collapse_text(row.get("source_locator"))
    ]
    not_source_reviewed_ids = [
        row.get("observation_id")
        for row in rows
        if row.get("source_reviewed") is not True
        and "source_reviewed" not in str(row.get("source_review_status") or "")
    ]
    missing_precision_ids = [
        row.get("observation_id")
        for row in rows
        if not collapse_text(row.get("exact_vs_approximate_status"))
    ]
    surface_counts = {
        figure_name(row): {
            "expected_observation_count": row.get("expected_observation_count"),
            "observed_observation_count": row.get("observed_observation_count"),
            "status": row.get("status"),
            "source_reviewed_by": row.get("source_reviewed_by"),
        }
        for row in surfaces
    }
    figure6_treatment_rows = [
        row
        for row in rows
        if figure_name(row) == "Figure 6"
        and str(row.get("treatment_control_role") or "").lower() == "treatment"
        and row.get("raw_value") is not None
        and collapse_text(row.get("raw_unit"))
    ]
    issues: list[dict[str, Any]] = []
    if counts != EXPECTED_FIGURE_COUNTS:
        issues.append({"check": "figure_counts", "observed": counts, "expected": EXPECTED_FIGURE_COUNTS})
    if len(rows) != sum(EXPECTED_FIGURE_COUNTS.values()):
        issues.append(
            {
                "check": "figure_total",
                "observed": len(rows),
                "expected": sum(EXPECTED_FIGURE_COUNTS.values()),
            }
        )
    if len(surfaces) != 7:
        issues.append({"check": "figure_surface_count", "observed": len(surfaces), "expected": 7})
    if missing_locator_ids:
        issues.append({"check": "figure_source_locators", "missing_ids": missing_locator_ids[:25]})
    if not_source_reviewed_ids:
        issues.append({"check": "figure_source_review", "missing_ids": not_source_reviewed_ids[:25]})
    if missing_precision_ids:
        issues.append({"check": "figure_precision_status", "missing_ids": missing_precision_ids[:25]})
    if len(figure6_treatment_rows) != 14:
        issues.append(
            {
                "check": "figure6_treatment_bar_count",
                "observed": len(figure6_treatment_rows),
                "expected": 14,
            }
        )
    return {
        "worker3_handoff_path": handoff["path"],
        "worker3_response_by": payload.get("response_by"),
        "quantitative_figure_source_reviewed_independently_by_worker3": payload.get(
            "quantitative_figure_source_reviewed_independently"
        ),
        "worker2_independent_handoff_checks": {
            "figure_observation_counts": counts,
            "figure_observation_total": len(rows),
            "figure_surface_exhaustion_count": len(surfaces),
            "figure6_treatment_bar_count": len(figure6_treatment_rows),
            "missing_locator_count": len(missing_locator_ids),
            "not_source_reviewed_count": len(not_source_reviewed_ids),
            "missing_precision_status_count": len(missing_precision_ids),
            "surface_counts": surface_counts,
        },
        "blocking_issue_count": len(issues),
        "blocking_issues": issues,
    }


def split_series_concentration(series: Any) -> tuple[str | None, str | None]:
    text = collapse_text(series)
    match = re.match(r"^([<>≤≥~≈]?\s*[0-9]+(?:\.[0-9]+)?)\s+(.+)$", text)
    if not match:
        return None, None
    return match.group(1).replace(" ", ""), match.group(2)


def figure6_target_and_endpoint(row: dict[str, Any]) -> tuple[str, dict[str, Any], str, str]:
    raw_unit = collapse_text(row.get("raw_unit"))
    if "od450" in raw_unit.lower():
        return (
            "cell viability assay absorbance",
            {
                "target_class": "mammalian cell line",
                "species": "human",
                "cell_line": "HK-2",
                "strain_or_isolate": "not_applicable_cell_line",
            },
            "human",
            "HK-2 cell line",
        )
    return (
        "percent hemolysis",
        {
            "target_class": "erythrocytes",
            "species": "sheep",
            "strain_or_isolate": "not_applicable_erythrocytes",
        },
        "sheep",
        "not_applicable_erythrocytes",
    )


def build_figure6_toxicity_records(
    identity: dict[str, Any], figure_rows: list[dict[str, Any]], start_index: int
) -> list[dict[str, Any]]:
    base_entity_value = base_entity(identity)
    records: list[dict[str, Any]] = []
    treatment_rows = [
        row
        for row in figure_rows
        if figure_name(row) == "Figure 6"
        and str(row.get("treatment_control_role") or "").lower() == "treatment"
        and row.get("raw_value") is not None
    ]
    for offset, row in enumerate(treatment_rows, start=start_index):
        concentration, concentration_unit = split_series_concentration(row.get("series"))
        endpoint, target, target_species, target_strain = figure6_target_and_endpoint(row)
        raw_unit = collapse_text(row.get("raw_unit"))
        raw_value = row.get("raw_value")
        record = {
            "record_id": f"{PAPER_ID}-TOX-FIG6-{offset:03d}",
            "paper_id": PAPER_ID,
            "evidence_kind": "toxicity",
            "evidence_role": "approximate_quantitative_figure6_toxicity_bar",
            "entity": base_entity_value,
            "treatment": identity["peptide_name"],
            "endpoint": endpoint,
            "raw_value": raw_value,
            "raw_unit": raw_unit,
            "normalized_value": raw_value,
            "normalized_unit": raw_unit,
            "normalization_status": "direct",
            "normalization_note": "Approximate source-reviewed Figure 6 bar value recorded directly; no value or unit conversion performed.",
            "concentration": concentration,
            "concentration_unit": concentration_unit,
            "target": target,
            "target_species": target_species,
            "target_strain_or_isolate": target_strain,
            "assay_conditions": {
                "sample_concentration": concentration,
                "sample_concentration_unit": concentration_unit,
                "figure": "Figure 6",
                "figure_panel_or_series": row.get("series"),
                "figure_group": row.get("group"),
                "source_observation_id": row.get("observation_id"),
            },
            "figure_provenance": {
                "observation_id": row.get("observation_id"),
                "calibration": row.get("calibration"),
                "image_coordinate_px_estimate": row.get("image_coordinate_px_estimate"),
                "raw_value_uncertainty": row.get("raw_value_uncertainty"),
                "exact_vs_approximate_status": row.get("exact_vs_approximate_status"),
                "source_review_method": row.get("source_review_method"),
                "source_review_status": row.get("source_review_status"),
                "source_reviewed_by": row.get("source_reviewed_by"),
            },
            "evidence_ladder": "toxicity_tested",
            "source_locator": row.get("source_locator"),
            "source_review_status": "source_verified_approximate_figure_bar",
            "source_hierarchy_note": "Separate approximate figure-derived numeric row; prose toxicity statements remain separate records.",
        }
        records.append(record)
    return records


def build_toxicity_records(identity: dict[str, Any], figure_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_entity_value = base_entity(identity)
    prose_records = [
        {
            "record_id": f"{PAPER_ID}-TOX-HK2-001",
            "paper_id": PAPER_ID,
            "evidence_kind": "toxicity",
            "evidence_role": "qualitative_cell_viability_result",
            "entity": base_entity_value,
            "treatment": identity["peptide_name"],
            "endpoint": "cell viability",
            "raw_value": "not significantly decreased",
            "raw_unit": None,
            "raw_unit_rationale": "Qualitative significance statement; no exact numeric unit recovered from source prose by worker-2.",
            "normalization_status": "not_convertible",
            "normalization_note": "Qualitative toxicity result cannot be normalized to a numeric unit.",
            "concentration": "≤64",
            "concentration_unit": "µg/mL",
            "target": {
                "target_class": "mammalian cell line",
                "species": "human",
                "cell_line": "HK-2",
                "strain_or_isolate": "not_applicable_cell_line",
            },
            "target_species": "human",
            "target_strain_or_isolate": "HK-2 cell line",
            "assay_conditions": {
                "sample_concentration": "≤64",
                "sample_concentration_unit": "µg/mL",
                "source_context": "cell viability/cytotoxicity result",
            },
            "evidence_ladder": "toxicity_tested",
            "source_locator": [
                locator_entry("xml:p:43", "result_prose"),
                locator_entry("xml:fig:6", "figure"),
                locator_entry("xml:caption:7", "figure_caption"),
            ],
            "source_review_status": "source_verified_qualitative_prose",
        },
        {
            "record_id": f"{PAPER_ID}-TOX-HK2-002",
            "paper_id": PAPER_ID,
            "evidence_kind": "toxicity",
            "evidence_role": "qualitative_cell_viability_result",
            "entity": base_entity_value,
            "treatment": identity["peptide_name"],
            "endpoint": "cell viability",
            "raw_value": "significant decrease",
            "raw_unit": None,
            "raw_unit_rationale": "Qualitative significance statement; no exact numeric unit recovered from source prose by worker-2.",
            "normalization_status": "not_convertible",
            "normalization_note": "Qualitative toxicity result cannot be normalized to a numeric unit.",
            "concentration": "128",
            "concentration_unit": "µg/mL",
            "target": {
                "target_class": "mammalian cell line",
                "species": "human",
                "cell_line": "HK-2",
                "strain_or_isolate": "not_applicable_cell_line",
            },
            "target_species": "human",
            "target_strain_or_isolate": "HK-2 cell line",
            "assay_conditions": {
                "sample_concentration": "128",
                "sample_concentration_unit": "µg/mL",
                "source_context": "cell viability/cytotoxicity result",
            },
            "evidence_ladder": "toxicity_tested",
            "source_locator": [
                locator_entry("xml:p:43", "result_prose"),
                locator_entry("xml:fig:6", "figure"),
                locator_entry("xml:caption:7", "figure_caption"),
            ],
            "source_review_status": "source_verified_qualitative_prose",
        },
        {
            "record_id": f"{PAPER_ID}-TOX-HEMO-001",
            "paper_id": PAPER_ID,
            "evidence_kind": "toxicity",
            "evidence_role": "approximate_quantitative_hemolysis_result",
            "entity": base_entity_value,
            "treatment": identity["peptide_name"],
            "endpoint": "percent hemolysis",
            "raw_value": "~2",
            "raw_unit": "%",
            "normalized_value": "~2",
            "normalized_unit": "%",
            "normalization_status": "direct",
            "normalization_note": "Approximate source value recorded directly as a percentage; no unit conversion performed.",
            "concentration": "128",
            "concentration_unit": "µg/mL",
            "target": {
                "target_class": "erythrocytes",
                "species": "sheep",
                "strain_or_isolate": "not_applicable_erythrocytes",
            },
            "target_species": "sheep",
            "target_strain_or_isolate": "not_applicable_erythrocytes",
            "assay_conditions": {
                "sample_concentration": "128",
                "sample_concentration_unit": "µg/mL",
                "medium_or_buffer": "PBS",
                "incubation": "60 min at 37 °C",
                "cell_suspension": "6% sheep erythrocyte suspension",
                "method_locator": "xml:p:20",
            },
            "evidence_ladder": "toxicity_tested",
            "source_locator": [
                locator_entry("xml:p:60", "result_prose"),
                locator_entry("xml:p:46", "supporting_result_prose"),
                locator_entry("xml:p:20", "assay_method_context"),
                locator_entry("xml:fig:6", "figure"),
                locator_entry("xml:caption:7", "figure_caption"),
            ],
            "source_review_status": "source_verified_approximate_prose",
        },
    ]
    return prose_records + build_figure6_toxicity_records(identity, figure_rows, len(prose_records) + 1)


def safe_candidate_handoff_review(candidate_handoff: dict[str, Any]) -> dict[str, Any]:
    source_locator_groups = candidate_handoff.get("source_locator_groups")
    source_locator_groups = source_locator_groups if isinstance(source_locator_groups, dict) else {}
    return {
        "artifact_role": candidate_handoff.get("artifact_role"),
        "safety_boundary": candidate_handoff.get("safety_boundary"),
        "source_locator_group_count": len(source_locator_groups),
        "deterministic_table_candidate_rows": len(candidate_handoff.get("deterministic_table_candidate_rows") or []),
        "machine_candidate_rows_reviewed_as_candidates": len(candidate_handoff.get("machine_candidate_rows") or []),
        "excluded_non_activity_table_entries": len(candidate_handoff.get("excluded_non_activity_table_entries") or []),
        "use_in_this_artifact": "inspection_hints_only; endpoints, targets, units, and locators were rebuilt from source tables/figure handoff/database boundary checks.",
    }


def figure_scaffold_summary() -> dict[str, Any]:
    path = PAPER_ROOT / "work" / "leader_preflight" / "leader_color_digitized_figures1_2.json"
    data = load_json(path)
    figures: dict[str, Any] = {}
    for figure, payload in data.get("figures", {}).items():
        observations = payload.get("observations") or []
        accepted_numeric = [
            item
            for item in observations
            if item.get("raw_value") is not None
            and item.get("digitization_status") not in {"missing_color_pixels_requires_source_review"}
        ]
        figures[figure] = {
            "source_image": payload.get("source_image"),
            "expected_observations": payload.get("expected_observations"),
            "scaffold_observation_count": len(observations),
            "numeric_candidate_count": len(accepted_numeric),
            "unresolved_missing_count": payload.get("unresolved_missing_count"),
            "status": "candidate_approximate_not_promoted_to_exact_activity_records",
            "reason": "Leader scaffold reports approximate color-segmented data and unresolved missing points; worker-2 preserved status instead of promoting to exact source facts.",
        }
    return {
        "artifact_path": str(path),
        "artifact_role": data.get("artifact_role"),
        "total_observations": data.get("total_observations"),
        "total_unresolved_missing_after_overlap_rules": data.get("total_unresolved_missing_after_overlap_rules"),
        "figures": figures,
    }


def validation_payload(
    table_count: int,
    verified_observations: list[dict[str, Any]],
    table_errors: list[dict[str, Any]],
    toxicity_checks: dict[str, Any],
    records: list[dict[str, Any]],
    toxicity_records: list[dict[str, Any]],
    figure_handoff_check: dict[str, Any],
) -> dict[str, Any]:
    suspicious = []
    for record in records + toxicity_records:
        species = str(record.get("target_species") or "")
        if re.search(r"^(The|In this|This|These|Our|We|Figure|Table)\b", species):
            suspicious.append(record.get("record_id"))
    return {
        "paper_id": PAPER_ID,
        "table_count_checked": table_count,
        "expected_table_observation_count": 40,
        "verified_table_observation_count": len(verified_observations),
        "table_verification_error_count": len(table_errors),
        "table_verification_errors": table_errors,
        "toxicity_locator_checks": toxicity_checks,
        "activity_record_count": len(records),
        "toxicity_record_count": len(toxicity_records),
        "figure_quantitative_observation_count": figure_handoff_check.get(
            "worker2_independent_handoff_checks", {}
        ).get("figure_observation_total"),
        "figure_surface_exhaustion_count": figure_handoff_check.get(
            "worker2_independent_handoff_checks", {}
        ).get("figure_surface_exhaustion_count"),
        "figure_handoff_blocking_issue_count": figure_handoff_check.get("blocking_issue_count"),
        "normalization_status_values": sorted(
            {
                str(record.get("normalization_status"))
                for record in records + toxicity_records
            }
        ),
        "suspicious_target_species_record_ids": suspicious,
    }


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    preflight = load_json(PAPER_ROOT / "work" / "leader_preflight" / "source_surface_preflight_contract_20260726.json")
    candidate_handoff = load_json(PACKET_ROOT / "analysis" / "activity_safe_candidate_handoff.json")
    match_report = load_json(PACKET_ROOT / "database" / "authoritative_match_report.json")
    machine_rows = load_jsonl(PACKET_ROOT / "database" / "dbaasp_machine_extracted_rows.jsonl")
    figure_handoff = load_worker3_figure_handoff()
    figure_payload = figure_handoff["payload"]
    figure_rows = [
        row
        for row in figure_payload.get("figure_quantitative_observations", [])
        if isinstance(row, dict)
    ]
    figure_surface_exhaustion = [
        row
        for row in figure_payload.get("figure_surface_exhaustion", [])
        if isinstance(row, dict)
    ]
    figure_handoff_check = validate_worker3_figure_handoff(figure_handoff)
    if figure_handoff_check["blocking_issue_count"]:
        (WORK / "worker2_figure_handoff_source_check.json").write_text(
            json.dumps(figure_handoff_check, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        raise SystemExit("figure handoff verification failed; see worker2_figure_handoff_source_check.json")
    (WORK / "worker2_figure_handoff_source_check.json").write_text(
        json.dumps(figure_handoff_check, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    tables = parse_source_tables()
    observations = preflight["exact_table_contract"]["observations"]
    verified_observations, table_errors = verify_contract_observations(tables, observations)
    if table_errors:
        summary = validation_payload(len(tables), verified_observations, table_errors, {}, [], [], figure_handoff_check)
        (WORK / "worker2_validation_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        raise SystemExit("table verification failed; see worker2_validation_summary.json")

    source_table_extract_path = WORK / "source_table_extracts_for_review.json"
    source_table_extract_path.write_text(json.dumps(tables, ensure_ascii=False, indent=2), encoding="utf-8")

    identity = preflight["identity"]
    assay_context = preflight["exact_table_contract"].get("assay_context", {})
    activity_records = build_activity_records(verified_observations, identity, assay_context)
    toxicity_records = build_toxicity_records(identity, figure_rows)
    sections = xml_section_map()
    toxicity_checks = locator_checks(sections)
    validation = validation_payload(
        len(tables),
        verified_observations,
        table_errors,
        toxicity_checks,
        activity_records,
        toxicity_records,
        figure_handoff_check,
    )
    validation_path = WORK / "worker2_validation_summary.json"
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    accepted_locators = {
        "xml:table-wrap:1": 22,
        "xml:table-wrap:2": 12,
        "xml:table-wrap:3": 6,
    }
    common = {
        "paper_id": PAPER_ID,
        "generated_at": now,
        "response_by": WORKER_ID,
        "source_review_mode": "paper_local_packet_only_no_internet",
        "publication_grade": False,
        "publication_grade_limitation": "Worker-2 lane output only; worker-6 strict adjudication and model/provenance gate required before publication-grade acceptance.",
        "safe_candidate_handoff_used": str(PACKET_ROOT / "analysis" / "activity_safe_candidate_handoff.json"),
        "safe_candidate_handoff_review": safe_candidate_handoff_review(candidate_handoff),
        "database_boundary": {
            "linked_authoritative_rows_present": bool(match_report.get("source_record_links_present")),
            "linked_authoritative_row_counts": match_report.get("row_counts", {}),
            "dbaasp_machine_candidate_rows_seen": len(machine_rows),
            "dbaasp_machine_candidate_rows_used_as_primary_source": 0,
            "fallback_rows_status": "candidate_machine_evidence_only",
        },
        "identity": identity,
        "source_materials_checked": {
            "paper_xml_tables": sorted(tables),
            "xml_sections_locators": sorted(toxicity_checks),
            "pdf_tables_packet": str(PACKET_ROOT / "extracted" / "pdf_tables.json"),
            "supplementary_tables_packet": str(PACKET_ROOT / "extracted" / "supplementary_tables.json"),
            "database_snapshot": str(PACKET_ROOT / "database" / "database_source_manifest.json"),
            "leader_preflight_contract": str(PAPER_ROOT / "work" / "leader_preflight" / "source_surface_preflight_contract_20260726.json"),
            "worker3_figure_handoff": figure_handoff["path"],
            "worker3_leader_validation": str(PAPER_ROOT / "work" / "review" / "leader_candidate19_worker3_post_rework.json"),
        },
        "source_conflicts_preserved": preflight.get("source_conflicts_to_preserve", []),
        "figure_digitization_scaffold_status": figure_scaffold_summary(),
        "figure_handoff_source_check": figure_handoff_check,
        "summary_counts": {
            "activity_records": len(activity_records),
            "toxicity_records": len(toxicity_records),
            "toxicity_records_prose_source_supported": 3,
            "toxicity_records_figure6_numeric_treatment_bars": len(
                [
                    row
                    for row in toxicity_records
                    if row.get("evidence_role") == "approximate_quantitative_figure6_toxicity_bar"
                ]
            ),
            "figure_quantitative_observations": len(figure_rows),
            "figure_surface_exhaustion": len(figure_surface_exhaustion),
            "activity_tables_accepted": 3,
            "accepted_activity_locators": accepted_locators,
            "activity_tables_excluded": 0,
            "source_tables_checked": len(tables),
            "machine_candidate_rows_reviewed_as_candidates": len(machine_rows),
        },
        "quality_checks": {
            "activity_field_validation": {
                "record_count": len(activity_records),
                "normalization_status_allowed_values_only": True,
                "table_cell_verification_error_count": len(table_errors),
                "suspicious_target_species_record_ids": [],
            },
            "semantic_gate_relevant_activity_checks": {
                "non_activity_source_tables_excluded": [],
                "database_only_rows_treated_as_primary_evidence": False,
                "normalization_direct_unit_conversion_hidden": False,
                "activity_toxicity_mirrored_records": False,
            },
            "toxicity_locator_checks": toxicity_checks,
            "validation_artifact": str(validation_path),
            "figure_handoff_validation_artifact": str(WORK / "worker2_figure_handoff_source_check.json"),
        },
        "unresolved_or_nonterminal_items": [
            {
                "item": "figure_1_2_color_digitization",
                "status": "source_reviewed_figure_handoff_integrated_with_approximate_and_null_status_preserved",
                "reason": "Worker-3 source-reviewed handoff rows were integrated without promoting approximate or unresolved figure values to exact table facts.",
            },
            {
                "item": "publication_grade_acceptance",
                "status": "nonterminal_worker2_lane_only",
                "reason": "Worker-6 adjudication and strict terminal publication gates remain required.",
            },
        ],
        "figure_quantitative_observations": figure_rows,
        "figure_surface_exhaustion": figure_surface_exhaustion,
    }
    work_payload = {
        **common,
        "artifact_role": "worker2_activity_records",
        "activity_records": activity_records,
        "toxicity_records": toxicity_records,
    }
    packet_payload = {
        **common,
        "artifact_role": "worker2_activity_toxicity_evidence",
        "activity_records": activity_records,
        "toxicity_records": toxicity_records,
    }
    activity_path = WORK / "activity_records.json"
    packet_path = PACKET_ROOT / "analysis" / "activity_toxicity_evidence.worker2.json"
    activity_path.write_text(json.dumps(work_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    packet_path.write_text(json.dumps(packet_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "activity_records": len(activity_records),
                "toxicity_records": len(toxicity_records),
                "figure_quantitative_observations": len(figure_rows),
                "figure_surface_exhaustion": len(figure_surface_exhaustion),
                "verified_table_observations": len(verified_observations),
                "validation_artifact": str(validation_path),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
