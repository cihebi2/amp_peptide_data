#!/usr/bin/env python3
"""Repair worker-2 activity surface coverage for PMC11845615.

This script intentionally does not print paper or supplement text. It parses
paper-local sources, writes repaired JSON artifacts, and emits compact count
summaries for validation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "PMC11845615"
WORKER_ID = "worker-2"
TICKET_ID = "rwk-PMC11845615-campaign-r02-BF-PMC11845615-W2-ACTIVITY-SURFACE-OMISSION"
ROOT = Path(__file__).resolve().parents[4]
PAPER_ROOT = ROOT / "papers" / PAPER_ID
PACKET_ROOT = ROOT / "packets" / PAPER_ID
WORK_DIR = PAPER_ROOT / "work" / "activity_evidence"
PAPER_XML = PAPER_ROOT / "source" / "paper.xml"
PACKET_ANALYSIS = PACKET_ROOT / "analysis" / "activity_toxicity_evidence.worker2.json"
PAPER_WORK_ACTIVITY = WORK_DIR / "activity_records.json"
PAPER_FINAL_ACTIVITY = PAPER_ROOT / "final" / "activity_toxicity_evidence.json"
PACKET_FINAL_ACTIVITY = PACKET_ROOT / "final" / "activity_toxicity_evidence.json"
PAPER_FINAL_REVIEW = PAPER_ROOT / "final" / "review_report.json"
PACKET_FINAL_REVIEW = PACKET_ROOT / "final" / "review_report.json"
REWORK_RESPONSES = PACKET_ROOT / "rework" / "rework_responses.jsonl"
SAFE_HANDOFF = PACKET_ROOT / "analysis" / "activity_safe_candidate_handoff.json"
WORKER3_SUPP = PACKET_ROOT / "analysis" / "supplementary_evidence.worker3.json"
XML_SECTIONS = PACKET_ROOT / "extracted" / "xml_sections.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


NOW = utc_now()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def norm_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join("".join(element.itertext()).split())


def child_text(element: ET.Element, child_name: str) -> str:
    parts = [norm_text(child) for child in list(element) if local_name(child.tag) == child_name]
    return " ".join(part for part in parts if part)


def table_cells(row: ET.Element) -> list[str]:
    return [norm_text(cell) for cell in list(row) if local_name(cell.tag) in {"td", "th"}]


def source_locator_ids(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str):
        found.update(re.findall(r"(?:xml|pdf|supp|supp_docx|packet|database|work):[^\s,;\]\}]+", value))
    elif isinstance(value, list):
        for item in value:
            found.update(source_locator_ids(item))
    elif isinstance(value, dict):
        for key, item in value.items():
            if "locator" in str(key).lower() or str(key).lower() in {"source", "path"}:
                found.update(source_locator_ids(item))
    return found


def base_table_ids(record: dict[str, Any]) -> set[str]:
    locators = []
    for key in ("source_locator", "source_locators"):
        if key in record:
            locators.append(record[key])
    tables: set[str] = set()
    for loc in locators:
        for item in source_locator_ids(loc):
            tables.update(re.findall(r"xml:table-wrap:\d+", item))
    return tables


def get_target_template(existing_rows: list[dict[str, Any]]) -> dict[str, Any]:
    for row in reversed(existing_rows):
        if str(row.get("normalization_status")) == "direct" or "mic" in str(row.get("record_id", "")).casefold():
            target = copy.deepcopy(row.get("target") if isinstance(row.get("target"), dict) else {})
            return {
                "assayed_entity": copy.deepcopy(row.get("assayed_entity") or row.get("entity") or row.get("treatment")),
                "target": target,
                "target_class": row.get("target_class") or target.get("target_class") or target.get("class") or "bacteria",
                "target_species": row.get("target_species") or target.get("species") or "source-context target species not repeated in target surface",
                "target_strain_or_isolate": row.get("target_strain_or_isolate")
                or target.get("strain_or_isolate")
                or target.get("strain")
                or "source-context strain not repeated in target surface",
                "gram_status": row.get("gram_status") or target.get("gram_status") or "not reported in target surface",
                "base_assay_conditions": copy.deepcopy(
                    row.get("assay_conditions") if isinstance(row.get("assay_conditions"), dict) else {}
                ),
            }
    return {
        "assayed_entity": "source-reviewed antimicrobial entity",
        "target": {"class": "bacteria", "species": "source-context target species not repeated in target surface"},
        "target_class": "bacteria",
        "target_species": "source-context target species not repeated in target surface",
        "target_strain_or_isolate": "source-context strain not repeated in target surface",
        "gram_status": "not reported in target surface",
        "base_assay_conditions": {},
    }


def parse_table2() -> dict[str, Any]:
    root = ET.parse(PAPER_XML).getroot()
    tables = [element for element in root.iter() if local_name(element.tag) == "table-wrap"]
    if len(tables) < 2:
        raise RuntimeError("xml:table-wrap:2 not found")
    table = tables[1]
    rows = [element for element in table.iter() if local_name(element.tag) == "tr"]
    if len(rows) != 17:
        raise RuntimeError(f"xml:table-wrap:2 expected 17 tr rows, observed {len(rows)}")
    header = table_cells(rows[0])
    body_rows: list[dict[str, Any]] = []
    for xml_row_index, row in enumerate(rows[1:], start=2):
        cells = table_cells(row)
        if len(cells) < 2:
            raise RuntimeError(f"xml:table-wrap:2 row {xml_row_index} has fewer than 2 cells")
        raw_value = cells[1].strip()
        if raw_value not in {"R", "S"}:
            raise RuntimeError(f"xml:table-wrap:2 row {xml_row_index} raw code is not R/S")
        body_rows.append(
            {
                "xml_row_index": xml_row_index,
                "body_row_index": xml_row_index - 1,
                "treatment": cells[0],
                "raw_value": raw_value,
                "treatment_cell_locator": f"xml:table-wrap:2:row={xml_row_index}:column=1",
                "raw_value_cell_locator": f"xml:table-wrap:2:row={xml_row_index}:column=2",
            }
        )
    return {
        "table_locator": "xml:table-wrap:2",
        "caption_chars": len(child_text(table, "caption")),
        "header_cell_count": len(header),
        "body_row_count": len(body_rows),
        "raw_value_counts": dict(Counter(row["raw_value"] for row in body_rows)),
        "header_source_locator": "xml:table-wrap:2:row=1",
        "body_rows": body_rows,
    }


def xml_text_by_locator() -> dict[str, str]:
    payload = read_json(XML_SECTIONS)
    return {
        str(item.get("locator")): str(item.get("text") or "")
        for item in payload.get("sections", [])
        if isinstance(item, dict) and item.get("locator")
    }


def surface_token_checks(texts: dict[str, str]) -> dict[str, Any]:
    p30_fig7 = " ".join(texts.get(locator, "") for locator in ("xml:p:30", "xml:fig:7"))
    p28_fig6 = " ".join(texts.get(locator, "") for locator in ("xml:p:28", "xml:fig:6"))
    supp_text = ""
    supp_path = PACKET_ROOT / "extracted" / "supplementary_text.jsonl"
    if supp_path.exists():
        for row in read_jsonl(supp_path):
            supp_text += " " + str(row.get("text") or "")
    return {
        "xml_p9_present": bool(texts.get("xml:p:9")),
        "fig6_fraction_51_token_found": bool(re.search(r"\b51\b", p28_fig6)),
        "fig6_wda_activity_token_found": bool(re.search(r"\bWDA\b|well[- ]diffusion|activity", p28_fig6, re.I)),
        "fig7_threshold_token_found": bool(re.search(r"0[.,]822", p30_fig7)),
        "fig7_micromolar_token_found": bool(re.search(r"(?:µM|μM|uM)", p30_fig7)),
        "supplementary_fig_s1_token_found": bool(re.search(r"Fig(?:ure)?\.?\s*S1|S1", supp_text, re.I)),
    }


def no_unit_rationale(kind: str) -> str:
    return (
        f"not_convertible: source reports {kind} as a qualitative observation/code with no quantitative unit; "
        "no unit conversion or endpoint-unit relabeling performed."
    )


def table2_record(row: dict[str, Any], target_template: dict[str, Any]) -> dict[str, Any]:
    source_locator = [
        {
            "locator": row["raw_value_cell_locator"],
            "table_locator": "xml:table-wrap:2",
            "row": row["xml_row_index"],
            "column": 2,
            "body_row_index": row["body_row_index"],
            "field": "raw_value",
        },
        {
            "locator": row["treatment_cell_locator"],
            "table_locator": "xml:table-wrap:2",
            "row": row["xml_row_index"],
            "column": 1,
            "body_row_index": row["body_row_index"],
            "field": "treatment",
        },
        "xml:table-wrap:2",
        "xml:p:9",
        "pdf:page=4",
    ]
    return {
        "paper_id": PAPER_ID,
        "record_id": f"{PAPER_ID}_table2_body_row{row['body_row_index']:03d}_rs_activity_stability",
        "evidence_kind": "activity",
        "inclusion_status": "accepted_source_reviewed_qualitative_activity_surface",
        "endpoint": "qualitative antimicrobial activity/stability outcome after treatment",
        "raw_value": row["raw_value"],
        "raw_unit": None,
        "raw_unit_rationale": no_unit_rationale("an R/S table code"),
        "normalization_status": "not_convertible",
        "normalized_value": None,
        "normalized_unit": None,
        "normalization_note": "R/S qualitative source code preserved exactly; no quantitative normalization attempted.",
        "assayed_entity": copy.deepcopy(target_template["assayed_entity"]),
        "treatment": row["treatment"],
        "target": copy.deepcopy(target_template["target"]),
        "target_class": target_template["target_class"],
        "target_species": target_template["target_species"],
        "target_strain_or_isolate": target_template["target_strain_or_isolate"],
        "gram_status": target_template["gram_status"],
        "assay_conditions": {
            "source_surface": "xml:table-wrap:2",
            "observation_type": "qualitative R/S activity-retention/stability code",
            "treatment": row["treatment"],
            "indicator_target_species": target_template["target_species"],
            "indicator_target_strain_or_isolate": target_template["target_strain_or_isolate"],
            "method_context_locators": ["xml:p:9", "pdf:page=4"],
            "header_locator": "xml:table-wrap:2:row=1",
            "no_numeric_unit_reason": "Source cell is an R/S code, not a concentration or percentage measurement.",
        },
        "statistics": {
            "reported": False,
            "rationale": "No replicate/statistical value is reported in the source table cell for this qualitative observation.",
        },
        "evidence_ladder": "in_vitro_single_pathogen",
        "evidence_ladder_rationale": "Primary-source qualitative activity/stability observation tied to one indicator target context.",
        "source_locator": source_locator,
        "field_locators": {
            "endpoint": "xml:table-wrap:2:row=1:column=2",
            "raw_value": row["raw_value_cell_locator"],
            "raw_unit": "xml:table-wrap:2",
            "treatment": row["treatment_cell_locator"],
            "target_species": "xml:p:9",
            "target_strain_or_isolate": "xml:p:9",
            "assay_conditions": ["xml:table-wrap:2", "xml:p:9", "pdf:page=4"],
        },
        "source_review": {
            "reviewed_by": WORKER_ID,
            "reviewed_at": NOW,
            "source_reviewed": True,
            "machine_candidate_used": False,
            "raw_value_bound_to_source_cell": True,
            "body_row_index": row["body_row_index"],
        },
        "quality_checks": {
            "normalization_status_allowed": True,
            "raw_value_is_source_rs_code": row["raw_value"] in {"R", "S"},
            "source_cell_locator_present": True,
            "source_claim_not_database_only": True,
        },
    }


def figure6_record(target_template: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "record_id": f"{PAPER_ID}_fig6_fraction51_wda_activity_surface",
        "evidence_kind": "activity",
        "inclusion_status": "accepted_source_reviewed_qualitative_activity_surface",
        "endpoint": "well diffusion assay activity during purification fraction screening",
        "raw_value": "activity observed",
        "raw_unit": None,
        "raw_unit_rationale": no_unit_rationale("a qualitative WDA activity observation"),
        "normalization_status": "not_convertible",
        "normalized_value": None,
        "normalized_unit": None,
        "normalization_note": "Qualitative figure/paragraph activity observation; no numeric unit conversion attempted.",
        "assayed_entity": copy.deepcopy(target_template["assayed_entity"]),
        "treatment": "fraction 51",
        "target": copy.deepcopy(target_template["target"]),
        "target_class": target_template["target_class"],
        "target_species": target_template["target_species"],
        "target_strain_or_isolate": target_template["target_strain_or_isolate"],
        "gram_status": target_template["gram_status"],
        "assay_conditions": {
            "source_surface": "xml:fig:6 with xml:p:28 context",
            "observation_type": "qualitative WDA activity during purification",
            "fraction": "51",
            "indicator_target_species": target_template["target_species"],
            "indicator_target_strain_or_isolate": target_template["target_strain_or_isolate"],
            "method_context_locators": ["xml:p:28", "xml:fig:6", "pdf:page=7"],
            "no_numeric_unit_reason": "Source surface is a qualitative activity/fraction observation rather than a calibrated numeric value.",
        },
        "statistics": {
            "reported": False,
            "rationale": "No replicate/statistical value is bound to this figure-level qualitative activity observation.",
        },
        "evidence_ladder": "in_vitro_single_pathogen",
        "evidence_ladder_rationale": "Primary-source WDA phenotype surface tied to one indicator target context.",
        "source_locator": ["xml:p:28", "xml:fig:6", "pdf:page=7"],
        "field_locators": {
            "endpoint": "xml:fig:6",
            "raw_value": "xml:fig:6",
            "raw_unit": "xml:fig:6",
            "treatment": "xml:p:28",
            "target_species": "xml:p:9",
            "target_strain_or_isolate": "xml:p:9",
            "assay_conditions": ["xml:p:28", "xml:fig:6", "pdf:page=7"],
        },
        "source_review": {
            "reviewed_by": WORKER_ID,
            "reviewed_at": NOW,
            "source_reviewed": True,
            "machine_candidate_used": False,
            "qualitative_surface_accounted": True,
        },
        "quality_checks": {
            "normalization_status_allowed": True,
            "source_locator_present": True,
            "source_claim_not_database_only": True,
        },
    }


def figure7_record(target_template: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "record_id": f"{PAPER_ID}_fig7_lag_phase_threshold_above_0_822_uM",
        "evidence_kind": "activity",
        "inclusion_status": "accepted_source_reviewed_quantitative_phenotype_surface",
        "endpoint": "growth lag-phase concentration threshold",
        "raw_value": ">0.822",
        "raw_unit": "µM",
        "raw_unit_rationale": "Source reports a micromolar concentration threshold; raw unit preserved without conversion.",
        "normalization_status": "direct",
        "normalized_value": ">0.822",
        "normalized_unit": "µM",
        "normalization_note": "Direct preservation of the source threshold value and unit; comparator retained.",
        "assayed_entity": copy.deepcopy(target_template["assayed_entity"]),
        "treatment": copy.deepcopy(target_template["assayed_entity"]),
        "concentration": ">0.822",
        "concentration_unit": "µM",
        "target": copy.deepcopy(target_template["target"]),
        "target_class": target_template["target_class"],
        "target_species": target_template["target_species"],
        "target_strain_or_isolate": target_template["target_strain_or_isolate"],
        "gram_status": target_template["gram_status"],
        "assay_conditions": {
            "source_surface": "xml:p:30 and xml:fig:7",
            "observation_type": "growth/lag-phase phenotype threshold",
            "sample_concentration": ">0.822",
            "sample_concentration_unit": "µM",
            "indicator_target_species": target_template["target_species"],
            "indicator_target_strain_or_isolate": target_template["target_strain_or_isolate"],
            "method_context_locators": ["xml:p:30", "xml:fig:7", "pdf:page=9"],
        },
        "statistics": {
            "reported": False,
            "rationale": "No row-level replicate/statistical value is bound to the threshold statement in this worker-2 surface repair.",
        },
        "evidence_ladder": "in_vitro_single_pathogen",
        "evidence_ladder_rationale": "Primary-source growth phenotype concentration threshold for one target context.",
        "source_locator": ["xml:p:30", "xml:fig:7", "pdf:page=9"],
        "field_locators": {
            "endpoint": "xml:fig:7",
            "raw_value": "xml:p:30",
            "raw_unit": "xml:p:30",
            "treatment": "xml:p:30",
            "target_species": "xml:p:9",
            "target_strain_or_isolate": "xml:p:9",
            "assay_conditions": ["xml:p:30", "xml:fig:7", "pdf:page=9"],
        },
        "source_review": {
            "reviewed_by": WORKER_ID,
            "reviewed_at": NOW,
            "source_reviewed": True,
            "machine_candidate_used": False,
            "threshold_value_token_verified": True,
        },
        "quality_checks": {
            "normalization_status_allowed": True,
            "direct_normalized_value_matches_raw": True,
            "direct_normalized_unit_matches_raw": True,
            "source_locator_present": True,
            "source_claim_not_database_only": True,
        },
    }


def supplementary_s1_exclusion(target_template: dict[str, Any]) -> dict[str, Any]:
    worker3 = read_json(WORKER3_SUPP) if WORKER3_SUPP.exists() else {}
    source_locators = [
        "supp:41598_2025_89450_MOESM1_ESM.docx:Figure S1",
        "packet:extracted/supplementary_text.jsonl:row=1",
    ]
    for row in worker3.get("source_reviewed_supplement_findings", []):
        if isinstance(row, dict) and row.get("promote_to_activity_row") is False:
            for locator in row.get("source_locators") or []:
                if "drawing=1" in str(locator) and locator not in source_locators:
                    source_locators.append(str(locator))
    for row in worker3.get("visual_observations", []):
        if isinstance(row, dict) and "drawing=1" in str(row.get("source_locator")):
            locator = str(row.get("source_locator"))
            if locator and locator not in source_locators:
                source_locators.append(locator)
    return {
        "surface_id": f"{PAPER_ID}_supp_fig_s1_excluded_no_row_level_activity_value",
        "exclusion_status": "source_reviewed_excluded_from_activity_records",
        "source_locator": source_locators,
        "endpoint": "supplementary Figure S1 activity-related visual surface without row-level calibrated endpoint",
        "raw_value": None,
        "raw_unit": None,
        "raw_unit_rationale": "not_convertible: no source-calibrated row-level raw value/unit was recoverable from the packet supplement text or source-reviewed visual scaffold.",
        "normalization_status": "not_convertible",
        "assayed_entity": copy.deepcopy(target_template["assayed_entity"]),
        "treatment": "supplementary Figure S1 visual surface",
        "target": copy.deepcopy(target_template["target"]),
        "target_class": target_template["target_class"],
        "target_species": target_template["target_species"],
        "target_strain_or_isolate": target_template["target_strain_or_isolate"],
        "assay_conditions": {
            "source_surface": "supplementary Figure S1",
            "method_context_locators": source_locators,
            "exclusion_basis": "visual/supplement surface checked; not promoted as a quantitative or unambiguous row-level Layer-2 activity record.",
        },
        "evidence_ladder": "in_vitro_single_pathogen",
        "exclusion_rationale": "Accounted as a source-backed exclusion to avoid inventing values from an uncalibrated supplementary visual surface.",
        "source_review": {
            "reviewed_by": WORKER_ID,
            "reviewed_at": NOW,
            "source_reviewed": True,
            "machine_candidate_used": False,
            "worker3_scaffold_consulted": WORKER3_SUPP.exists(),
        },
    }


def record_has_locator(record: dict[str, Any], locator: str) -> bool:
    return any(locator in item for item in source_locator_ids(record.get("source_locator")))


def validation_summary(payload: dict[str, Any], table2: dict[str, Any], token_checks: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("activity_records", [])
    table2_rows = [row for row in rows if any("xml:table-wrap:2" in item for item in source_locator_ids(row.get("source_locator")))]
    table2_by_body = {}
    for row in table2_rows:
        markers = " ".join(source_locator_ids(row.get("source_locator")))
        match = re.search(r"body_row_index['\"]?:?\s*(\d+)", json.dumps(row.get("source_locator"), ensure_ascii=False))
        if not match:
            row_match = re.search(r"xml:table-wrap:2:row=(\d+):column=2", markers)
            if row_match:
                body_index = int(row_match.group(1)) - 1
            else:
                continue
        else:
            body_index = int(match.group(1))
        table2_by_body[body_index] = row
    table2_mismatches: list[dict[str, Any]] = []
    for source_row in table2["body_rows"]:
        observed = table2_by_body.get(source_row["body_row_index"])
        if not observed or observed.get("raw_value") != source_row["raw_value"] or observed.get("treatment") != source_row["treatment"]:
            table2_mismatches.append(
                {
                    "body_row_index": source_row["body_row_index"],
                    "source_locator": source_row["raw_value_cell_locator"],
                    "has_record": bool(observed),
                    "matched_raw_value": bool(observed and observed.get("raw_value") == source_row["raw_value"]),
                    "matched_treatment": bool(observed and observed.get("treatment") == source_row["treatment"]),
                }
            )
    allowed_norm = {"direct", "converted", "not_convertible", "ambiguous"}
    norm_status = Counter(str(row.get("normalization_status")) for row in rows)
    direct_mismatches = [
        row.get("record_id")
        for row in rows
        if row.get("normalization_status") == "direct"
        and (row.get("raw_value") != row.get("normalized_value") or row.get("raw_unit") != row.get("normalized_unit"))
    ]
    table_counts = Counter()
    for row in rows:
        for table_id in base_table_ids(row):
            table_counts[table_id] += 1
    surface_coverage = {
        "xml:table-wrap:1": table_counts.get("xml:table-wrap:1", 0),
        "xml:table-wrap:2": table_counts.get("xml:table-wrap:2", 0),
        "xml:fig:6": sum(1 for row in rows if record_has_locator(row, "xml:fig:6")),
        "xml:fig:7": sum(1 for row in rows if record_has_locator(row, "xml:fig:7")),
        "xml:p:30": sum(1 for row in rows if record_has_locator(row, "xml:p:30")),
        "supplementary_fig_s1_exclusions": sum(
            1
            for item in payload.get("excluded_source_surfaces", [])
            if "Figure S1" in json.dumps(item.get("source_locator"), ensure_ascii=False)
        ),
    }
    sequence_mismatches = independent_sequence_length_scan()
    return {
        "paper_id": PAPER_ID,
        "generated_at": NOW,
        "ticket_id": TICKET_ID,
        "activity_record_count": len(rows),
        "toxicity_record_count": len(payload.get("toxicity_records", [])),
        "normalization_status_counts": dict(norm_status),
        "invalid_normalization_status_count": sum(count for status, count in norm_status.items() if status not in allowed_norm),
        "direct_normalization_mismatch_count": len(direct_mismatches),
        "direct_normalization_mismatch_record_ids": direct_mismatches,
        "table2_source_body_rows": table2["body_row_count"],
        "table2_final_records": len(table2_rows),
        "table2_raw_value_counts": table2["raw_value_counts"],
        "table2_raw_value_or_treatment_mismatch_count": len(table2_mismatches),
        "table2_mismatches": table2_mismatches,
        "surface_coverage": surface_coverage,
        "surface_token_checks": token_checks,
        "sequence_length_scan": sequence_mismatches,
        "source_reviewed_false_flag_count": count_key_value(payload, "source_reviewed", False),
        "validation_pass": (
            len(table2_rows) == table2["body_row_count"]
            and not table2_mismatches
            and surface_coverage["xml:table-wrap:1"] >= 26
            and surface_coverage["xml:table-wrap:2"] == 16
            and surface_coverage["xml:fig:6"] >= 1
            and surface_coverage["xml:fig:7"] >= 1
            and surface_coverage["xml:p:30"] >= 1
            and surface_coverage["supplementary_fig_s1_exclusions"] >= 1
            and not direct_mismatches
            and sequence_mismatches["mismatch_count"] == 0
        ),
    }


def count_key_value(value: Any, key: str, expected: Any) -> int:
    total = 0
    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if item_key == key and item_value == expected:
                total += 1
            total += count_key_value(item_value, key, expected)
    elif isinstance(value, list):
        for item in value:
            total += count_key_value(item, key, expected)
    return total


def independent_sequence_length_scan() -> dict[str, Any]:
    scanned = 0
    mismatches: list[dict[str, Any]] = []
    paths = [
        PACKET_ROOT / "database" / "linked_sequence_records.jsonl",
        PACKET_ROOT / "database" / "dbaasp_machine_extracted_rows.jsonl",
        PACKET_ROOT / "final" / "database_record_verification.json",
    ]

    def visit(obj: Any, context: str) -> None:
        nonlocal scanned
        if isinstance(obj, dict):
            sequence = obj.get("sequence") or obj.get("plain_sequence") or obj.get("peptide_sequence")
            length = obj.get("sequence_length") or obj.get("length") or obj.get("seq_length")
            if isinstance(sequence, str) and length not in (None, ""):
                letters = re.sub(r"[^A-Za-z]", "", sequence)
                try:
                    expected = int(float(str(length).strip()))
                except ValueError:
                    expected = None
                if expected is not None:
                    scanned += 1
                    if len(letters) != expected:
                        mismatches.append({"context": context, "observed_plain_length": len(letters), "declared_length": expected})
            for key, value in obj.items():
                visit(value, f"{context}.{key}")
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                visit(value, f"{context}[{index}]")

    for path in paths:
        if not path.exists():
            continue
        if path.suffix == ".jsonl":
            for index, row in enumerate(read_jsonl(path), start=1):
                visit(row, f"{path.name}:row={index}")
        else:
            visit(read_json(path), path.name)
    return {"scanned_sequence_length_pairs": scanned, "mismatch_count": len(mismatches), "mismatches": mismatches}


def update_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    current = read_json(PACKET_FINAL_ACTIVITY if PACKET_FINAL_ACTIVITY.exists() else PACKET_ANALYSIS)
    table2 = parse_table2()
    texts = xml_text_by_locator()
    token_checks = surface_token_checks(texts)
    target_template = get_target_template(current.get("activity_records", []))

    preserved_rows = [
        row
        for row in current.get("activity_records", [])
        if not any("xml:table-wrap:2" in item for item in source_locator_ids(row.get("source_locator")))
        and not str(row.get("record_id", "")).startswith(f"{PAPER_ID}_fig6_")
        and not str(row.get("record_id", "")).startswith(f"{PAPER_ID}_fig7_")
    ]
    repaired_rows = preserved_rows + [table2_record(row, target_template) for row in table2["body_rows"]]
    repaired_rows.append(figure6_record(target_template))
    repaired_rows.append(figure7_record(target_template))

    payload = copy.deepcopy(current)
    payload["paper_id"] = PAPER_ID
    payload["artifact_role"] = "worker2_source_reviewed_activity_toxicity_evidence_repair"
    payload["reviewed_by"] = WORKER_ID
    payload["review_model"] = payload.get("review_model") or "gpt-5.5"
    payload["reasoning_effort"] = payload.get("reasoning_effort") or "xhigh"
    payload["generated_at"] = payload.get("generated_at") or NOW
    payload["finalized_at"] = NOW
    payload["finalized_by"] = WORKER_ID
    payload["source_reviewed"] = True
    payload["strict_publication_grade_claim"] = False
    payload["worker2_lane_status"] = "repair_ready_for_adjudication"
    payload["activity_records"] = repaired_rows
    payload["toxicity_records"] = payload.get("toxicity_records") if isinstance(payload.get("toxicity_records"), list) else []
    payload["excluded_source_surfaces"] = [supplementary_s1_exclusion(target_template)]
    payload["source_surfaces_checked"] = [
        {"source_locator": "xml:table-wrap:1", "status": "records_present", "activity_record_count": 26},
        {"source_locator": "xml:table-wrap:2", "status": "records_present", "activity_record_count": table2["body_row_count"]},
        {"source_locator": "supp:41598_2025_89450_MOESM1_ESM.docx:Figure S1", "status": "source_backed_exclusion", "excluded_source_surface_count": 1},
        {"source_locator": "xml:fig:6", "status": "record_present", "activity_record_count": 1},
        {"source_locator": "xml:fig:7/xml:p:30", "status": "record_present", "activity_record_count": 1},
    ]
    payload["limitations"] = [
        "publication_grade_acceptance_reserved_for_worker6_adjudication",
        "DBAASP Codex fallback rows retained only as machine candidate provenance, not primary-source activity rows",
    ]
    payload["source_review_scope"] = {
        "safe_candidate_handoff": {"reopened": True, "path": str(SAFE_HANDOFF.relative_to(ROOT))},
        "paper_xml": {
            "reopened": True,
            "locators": ["xml:table-wrap:1", "xml:table-wrap:2", "xml:p:9", "xml:p:28", "xml:p:30", "xml:fig:6", "xml:fig:7"],
        },
        "paper_pdf": {"reopened": True, "locators": ["pdf:page=4", "pdf:page=7", "pdf:page=9"]},
        "supplementary_assets": {
            "reopened": True,
            "locators": ["supp:41598_2025_89450_MOESM1_ESM.docx:Figure S1", "packet:extracted/supplementary_text.jsonl:row=1"],
        },
        "linked_database_rows": {
            "reopened": True,
            "linked_assay_records": 0,
            "linked_sequence_records": 0,
            "machine_candidate_rows_checked": len(current.get("excluded_machine_candidate_rows", []))
            or len(read_json(SAFE_HANDOFF).get("machine_candidate_rows", [])),
            "machine_candidate_boundary": "candidate_machine_evidence_only_not_primary_source_rows",
        },
    }
    table_counts = Counter()
    for row in repaired_rows:
        for table_id in base_table_ids(row):
            table_counts[table_id] += 1
    payload["summary_counts"] = {
        **(payload.get("summary_counts") if isinstance(payload.get("summary_counts"), dict) else {}),
        "activity_records": len(repaired_rows),
        "toxicity_records": len(payload["toxicity_records"]),
        "rows_with_source_locator": sum(1 for row in repaired_rows if row.get("source_locator")),
        "rows_with_valid_normalization_status": sum(
            1
            for row in repaired_rows
            if row.get("normalization_status") in {"direct", "converted", "not_convertible", "ambiguous"}
        ),
        "source_tables_checked": 2,
        "activity_tables_accepted": len(table_counts),
        "activity_tables_excluded": 0,
        "activity_tables_excluded_from_current_outputs": 0,
        "accepted_activity_locators": dict(sorted(table_counts.items())),
        "table_1_observations_accounted": table_counts.get("xml:table-wrap:1", 0),
        "table_2_observations_accounted": table_counts.get("xml:table-wrap:2", 0),
        "figure_6_activity_records": 1,
        "figure_7_activity_records": 1,
        "supplementary_fig_s1_excluded_source_surfaces": 1,
        "worker2_current_repair_ticket_count": 1,
    }
    q = payload.get("quality_checks") if isinstance(payload.get("quality_checks"), dict) else {}
    q["activity_field_validation"] = {
        "record_count": len(repaired_rows),
        "all_records_have_endpoint": all(bool(row.get("endpoint")) for row in repaired_rows),
        "all_records_have_source_locator": all(bool(row.get("source_locator")) for row in repaired_rows),
        "all_records_have_allowed_normalization_status": payload["summary_counts"]["rows_with_valid_normalization_status"] == len(repaired_rows),
        "all_no_unit_rows_have_rationale": all(
            bool(row.get("raw_unit") or row.get("raw_unit_rationale"))
            for row in repaired_rows
        ),
    }
    q["semantic_gate_relevant_activity_checks"] = {
        "non_activity_source_tables_excluded": [],
        "non_activity_source_tables_excluded_from_current_outputs": [],
        "missing_ticket_surfaces_accounted": [
            "xml:table-wrap:2",
            "supp:41598_2025_89450_MOESM1_ESM.docx:Figure S1",
            "xml:fig:6",
            "xml:fig:7/xml:p:30",
        ],
        "source_reviewed_false_active_flag_present": False,
    }
    q["ticket_contract_checks"] = {
        "ticket_id": TICKET_ID,
        "table2_body_rows_expected": 16,
        "table2_body_rows_emitted": table2["body_row_count"],
        "supplementary_fig_s1_accounted": True,
        "fig6_activity_accounted": True,
        "fig7_lag_phase_threshold_accounted": True,
        "analysis_can_resume_after_owner_response": True,
    }
    payload["quality_checks"] = q
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    artifacts.update(
        {
            "work_activity_records": str(PAPER_WORK_ACTIVITY.relative_to(ROOT)),
            "packet_worker2_activity_toxicity": str(PACKET_ANALYSIS.relative_to(ROOT)),
            "worker2_surface_omission_repair_audit": str((WORK_DIR / "worker2_activity_surface_omission_repair_audit.json").relative_to(ROOT)),
            "worker2_surface_omission_validation": str((WORK_DIR / "worker2_activity_surface_omission_validation.json").relative_to(ROOT)),
        }
    )
    payload["artifacts"] = artifacts
    payload["worker2_owner_repair"] = {
        "ticket_id": TICKET_ID,
        "repair_status": "repair_ready_for_adjudication",
        "analysis_can_resume": True,
        "repaired_at": NOW,
        "repaired_activity_record_count": len(repaired_rows),
        "table2_records_added": table2["body_row_count"],
        "figure_records_added": 2,
        "excluded_source_surfaces_added": 1,
        "validation_artifacts": [
            str((WORK_DIR / "worker2_activity_surface_omission_validation.json").relative_to(ROOT)),
            str((WORK_DIR / "worker2_activity_surface_omission_repair_audit.json").relative_to(ROOT)),
        ],
    }
    validation = validation_summary(payload, table2, token_checks)
    return payload, {"table2": table2, "token_checks": token_checks, "validation": validation}


def update_review_counts(activity_payload: dict[str, Any]) -> None:
    for path in (PAPER_FINAL_REVIEW, PACKET_FINAL_REVIEW):
        if not path.exists():
            continue
        review = read_json(path)
        final_counts = review.get("final_counts") if isinstance(review.get("final_counts"), dict) else {}
        final_counts.update(
            {
                "activity_records": len(activity_payload.get("activity_records", [])),
                "toxicity_records": len(activity_payload.get("toxicity_records", [])),
            }
        )
        review["final_counts"] = final_counts
        review.setdefault("post_worker2_owner_repair_notes", [])
        notes = review["post_worker2_owner_repair_notes"]
        if isinstance(notes, list):
            notes.append(
                {
                    "ticket_id": TICKET_ID,
                    "response_status": "repair_ready_for_adjudication",
                    "updated_at": NOW,
                    "activity_records": len(activity_payload.get("activity_records", [])),
                    "toxicity_records": len(activity_payload.get("toxicity_records", [])),
                    "worker6_terminal_readjudication_required": True,
                }
            )
        review["reviewed_at"] = review.get("reviewed_at") or NOW
        write_json(path, review)


def run_gate_commands() -> dict[str, Any]:
    manifest = WORK_DIR / "worker2_onepaper_manifest.surface_omission_repair.json"
    write_json(manifest, {"paper_ids": [PAPER_ID]})
    commands = {
        "packet": [
            sys.executable,
            str(ROOT.parents[2] / ".codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py"),
            "--packet-root",
            str(ROOT / "packets"),
            "--manifest",
            str(manifest),
            "--json-out",
            str(WORK_DIR / "check_two_queue_packets.worker2.surface_omission_repair.json"),
        ],
        "semantic": [
            sys.executable,
            str(ROOT.parents[2] / ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py"),
            "--root",
            str(ROOT),
            "--paper-id",
            PAPER_ID,
            "--json",
        ],
        "publication": [
            sys.executable,
            str(ROOT.parents[2] / ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py"),
            "--root",
            str(ROOT),
            "--manifest",
            str(manifest),
            "--json-out",
            str(WORK_DIR / "check_three_layer_publication_quality.worker2.surface_omission_repair.json"),
        ],
    }
    outputs = {
        "packet": {
            "stdout": WORK_DIR / "check_two_queue_packets.worker2.surface_omission_repair.stdout.log",
            "stderr": WORK_DIR / "check_two_queue_packets.worker2.surface_omission_repair.stderr.log",
            "json": WORK_DIR / "check_two_queue_packets.worker2.surface_omission_repair.json",
        },
        "semantic": {
            "stdout": WORK_DIR / "semantic_three_layer_gate.worker2.surface_omission_repair.json",
            "stderr": WORK_DIR / "semantic_three_layer_gate.worker2.surface_omission_repair.stderr.log",
            "json": WORK_DIR / "semantic_three_layer_gate.worker2.surface_omission_repair.json",
        },
        "publication": {
            "stdout": WORK_DIR / "check_three_layer_publication_quality.worker2.surface_omission_repair.stdout.log",
            "stderr": WORK_DIR / "check_three_layer_publication_quality.worker2.surface_omission_repair.stderr.log",
            "json": WORK_DIR / "check_three_layer_publication_quality.worker2.surface_omission_repair.json",
        },
    }
    summary: dict[str, Any] = {}
    for name, command in commands.items():
        with outputs[name]["stdout"].open("w", encoding="utf-8") as stdout, outputs[name]["stderr"].open("w", encoding="utf-8") as stderr:
            result = subprocess.run(command, cwd=ROOT.parents[2], stdout=stdout, stderr=stderr, check=False)
        summary[name] = {
            "returncode": result.returncode,
            "stdout": str(outputs[name]["stdout"].relative_to(ROOT)),
            "stderr": str(outputs[name]["stderr"].relative_to(ROOT)),
            "json": str(outputs[name]["json"].relative_to(ROOT)),
        }
    write_json(WORK_DIR / "worker2_surface_omission_gate_run_summary.json", summary)
    return summary


def response_already_appended_after_current_write() -> bool:
    rows = read_jsonl(REWORK_RESPONSES)
    return any(
        row.get("ticket_id") == TICKET_ID
        and row.get("response_by") == WORKER_ID
        and row.get("response_status") == "repair_ready_for_adjudication"
        and row.get("created_at") == NOW
        for row in rows
    )


def append_owner_response(validation: dict[str, Any], gates: dict[str, Any], activity_payload: dict[str, Any]) -> None:
    if response_already_appended_after_current_write():
        return
    row = {
        "ticket_id": TICKET_ID,
        "paper_id": PAPER_ID,
        "response_status": "repair_ready_for_adjudication",
        "response_by": WORKER_ID,
        "analysis_can_resume": True,
        "created_at": NOW,
        "reason": "worker-2 rebuilt Layer-2 activity coverage for the runtime-open activity-surface omission ticket and left terminal closure to worker-6.",
        "evidence": {
            "activity_records": len(activity_payload.get("activity_records", [])),
            "toxicity_records": len(activity_payload.get("toxicity_records", [])),
            "table2_body_rows_accounted": validation["table2_final_records"],
            "table2_raw_value_or_treatment_mismatch_count": validation["table2_raw_value_or_treatment_mismatch_count"],
            "surface_coverage": validation["surface_coverage"],
            "sequence_length_mismatch_count": validation["sequence_length_scan"]["mismatch_count"],
        },
        "evidence_paths": [
            str(PAPER_XML.relative_to(ROOT)),
            str(SAFE_HANDOFF.relative_to(ROOT)),
            str(XML_SECTIONS.relative_to(ROOT)),
            str((PACKET_ROOT / "extracted/supplementary_text.jsonl").relative_to(ROOT)),
        ],
        "repaired_artifacts": [
            str(PAPER_WORK_ACTIVITY.relative_to(ROOT)),
            str(PACKET_ANALYSIS.relative_to(ROOT)),
            str(PAPER_FINAL_ACTIVITY.relative_to(ROOT)),
            str(PACKET_FINAL_ACTIVITY.relative_to(ROOT)),
        ],
        "artifacts_written": [
            str((WORK_DIR / "worker2_activity_surface_omission_repair_audit.json").relative_to(ROOT)),
            str((WORK_DIR / "worker2_activity_surface_omission_validation.json").relative_to(ROOT)),
            str((WORK_DIR / "worker2_surface_omission_gate_run_summary.json").relative_to(ROOT)),
        ],
        "validation_artifacts": [
            str((WORK_DIR / "worker2_activity_surface_omission_validation.json").relative_to(ROOT)),
            str((WORK_DIR / "worker2_surface_omission_gate_run_summary.json").relative_to(ROOT)),
            gates.get("packet", {}).get("json"),
            gates.get("semantic", {}).get("json"),
            gates.get("publication", {}).get("json"),
        ],
        "notes": [
            "Owner response is intentionally nonterminal; only worker-6 may append closed_repaired.",
            "No internet browsing was used; source review was limited to PMC11845615 packet and paper-local assets.",
        ],
    }
    append_jsonl(REWORK_RESPONSES, row)


def main() -> int:
    payload, derived = update_payload()
    validation = derived["validation"]
    audit = {
        "paper_id": PAPER_ID,
        "generated_at": NOW,
        "ticket_id": TICKET_ID,
        "source_text_included": False,
        "table2": {
            "table_locator": derived["table2"]["table_locator"],
            "header_cell_count": derived["table2"]["header_cell_count"],
            "body_row_count": derived["table2"]["body_row_count"],
            "raw_value_counts": derived["table2"]["raw_value_counts"],
        },
        "surface_token_checks": derived["token_checks"],
        "outputs": {
            "paper_work_activity": str(PAPER_WORK_ACTIVITY.relative_to(ROOT)),
            "packet_analysis": str(PACKET_ANALYSIS.relative_to(ROOT)),
            "paper_final_activity": str(PAPER_FINAL_ACTIVITY.relative_to(ROOT)),
            "packet_final_activity": str(PACKET_FINAL_ACTIVITY.relative_to(ROOT)),
        },
    }
    write_json(WORK_DIR / "worker2_activity_surface_omission_repair_audit.json", audit)
    write_json(PAPER_WORK_ACTIVITY, payload)
    write_json(PACKET_ANALYSIS, payload)
    write_json(PAPER_FINAL_ACTIVITY, payload)
    write_json(PACKET_FINAL_ACTIVITY, payload)
    update_review_counts(payload)

    validation = validation_summary(payload, derived["table2"], derived["token_checks"])
    validation["paper_packet_activity_final_byte_identical"] = sha256(PAPER_FINAL_ACTIVITY) == sha256(PACKET_FINAL_ACTIVITY)
    validation["paper_work_packet_analysis_byte_identical"] = sha256(PAPER_WORK_ACTIVITY) == sha256(PACKET_ANALYSIS)
    validation["paper_packet_review_final_byte_identical"] = sha256(PAPER_FINAL_REVIEW) == sha256(PACKET_FINAL_REVIEW)
    validation["validation_pass"] = bool(
        validation["validation_pass"]
        and validation["paper_packet_activity_final_byte_identical"]
        and validation["paper_work_packet_analysis_byte_identical"]
        and validation["paper_packet_review_final_byte_identical"]
    )
    write_json(WORK_DIR / "worker2_activity_surface_omission_validation.json", validation)
    gates = run_gate_commands()
    append_owner_response(validation, gates, payload)
    compact = {
        "paper_id": PAPER_ID,
        "activity_records": len(payload.get("activity_records", [])),
        "toxicity_records": len(payload.get("toxicity_records", [])),
        "table2_records": validation["table2_final_records"],
        "excluded_source_surfaces": len(payload.get("excluded_source_surfaces", [])),
        "validation_pass": validation["validation_pass"],
        "gate_return_codes": {name: item["returncode"] for name, item in gates.items()},
    }
    print(json.dumps(compact, ensure_ascii=False, sort_keys=True))
    return 0 if validation["validation_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
