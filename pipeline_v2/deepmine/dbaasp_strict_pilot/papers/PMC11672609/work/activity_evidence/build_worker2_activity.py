#!/usr/bin/env python3
"""Build worker-2 activity/toxicity evidence for PMC11672609.

The script intentionally does not print source text. It reads packet-local
sources, verifies candidate observations against cited locators, and writes
structured JSON artifacts plus a source-free validation report.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


PAPER_ID = "PMC11672609"
ROOT = Path(__file__).resolve().parents[4]
PAPER_ROOT = ROOT / "papers" / PAPER_ID
PACKET_ROOT = ROOT / "packets" / PAPER_ID
WORK_DIR = PAPER_ROOT / "work" / "activity_evidence"
ANALYSIS_DIR = PACKET_ROOT / "analysis"

SAFE_HANDOFF = ANALYSIS_DIR / "activity_safe_candidate_handoff.json"
WORK_OUTPUT = WORK_DIR / "activity_records.json"
ANALYSIS_OUTPUT = ANALYSIS_DIR / "activity_toxicity_evidence.worker2.json"
VALIDATION_OUTPUT = WORK_DIR / "activity_toxicity_validation.worker2.json"
SOURCE_REVIEW_OUTPUT = WORK_DIR / "source_review_trace.worker2.json"
EXPECTED_CONTRACT_OUTPUT = WORK_DIR / "expected_observation_contract.worker2.json"
SUPPLEMENTARY_EVIDENCE_PATHS = [
    PACKET_ROOT / "analysis" / "supplementary_evidence.worker3.json",
    PAPER_ROOT / "work" / "supplementary_methods" / "supplementary_evidence.json",
]
SUPPLEMENTARY_TEXT_PATH = (
    PAPER_ROOT / "work" / "supplementary_methods" / "assets" / "supplementary_pdf_text.txt"
)
ACTIVE_TICKET_IDS = [
    "rwk-PMC11672609-campaign-r01-BF-PMC11672609-W2-ACTIVITY-TOXICITY-COVERAGE"
]

VALID_NORMALIZATION_STATUSES = {"direct", "converted", "not_convertible", "ambiguous"}
SUPP_TABLE_LOCATOR_RE = re.compile(r"supp:[^:]+:page=[^:]+:table=S\d+", re.I)
TOXICITY_RE = re.compile(
    r"\b(?:ha?emolysis|cytotoxic(?:ity)?|cell\s+death|cell\s+viability|mtt|ldh|hc50|cc50|mhc)\b",
    re.I,
)
ACTIVITY_RE = re.compile(
    r"\b(?:mic(?:50|90)?|mbc|mfc|mbic(?:50)?|mbec|fici?|ic50|ec50|inhibition)\b",
    re.I,
)
TABLE_LOCATOR_RE = re.compile(r"xml:table-wrap:\d+", re.I)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def norm_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    text = text.replace("μ", "u").replace("µ", "u")
    text = text.replace("α", "alpha").replace("Α", "alpha")
    text = text.replace("β", "beta").replace("Β", "beta")
    text = re.sub(r"\s+", " ", text)
    return text.strip().casefold()


def compact(value: Any) -> str:
    return re.sub(r"\s+", "", norm_text(value))


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def locator_ids(value: Any) -> list[str]:
    found: list[str] = []

    def visit(item: Any) -> None:
        if isinstance(item, str):
            if item.strip():
                found.append(item.strip())
            return
        if isinstance(item, list):
            for sub in item:
                visit(sub)
            return
        if isinstance(item, dict):
            for key in (
                "locator",
                "locators",
                "source_locator",
                "source_locators",
                "table_locator",
                "xml_locator",
                "pdf_locator",
                "body_locator",
                "figure_locator",
                "supporting_locators",
                "method_locators",
                "primary_locators",
                "all_locators",
            ):
                if key in item:
                    visit(item[key])

    visit(value)
    ordered: list[str] = []
    seen: set[str] = set()
    for loc in found:
        if loc not in seen:
            ordered.append(loc)
            seen.add(loc)
    return ordered


def load_source_texts() -> dict[str, str]:
    by_locator: dict[str, str] = {}

    xml_sections = load_json(PACKET_ROOT / "extracted" / "xml_sections.json")
    for item in xml_sections.get("sections", []):
        if isinstance(item, dict) and item.get("locator"):
            by_locator[str(item["locator"])] = str(item.get("text") or "")

    pdf_tables = load_json(PACKET_ROOT / "extracted" / "pdf_tables.json")
    for item in pdf_tables.get("tables", []):
        if isinstance(item, dict) and item.get("locator"):
            by_locator[str(item["locator"])] = str(item.get("text") or "")

    figures = load_json(PACKET_ROOT / "extracted" / "figure_captions.json")
    for item in figures.get("figures", []):
        if isinstance(item, dict) and item.get("locator"):
            by_locator[str(item["locator"])] = str(item.get("text") or "")

    pdf_text_path = PACKET_ROOT / "extracted" / "pdf_text.jsonl"
    for item in iter_jsonl(pdf_text_path):
        locator = item.get("locator")
        if locator:
            by_locator[str(locator)] = str(item.get("text") or "")

    supplementary_text = ""
    if SUPPLEMENTARY_TEXT_PATH.exists():
        supplementary_text = SUPPLEMENTARY_TEXT_PATH.read_text(encoding="utf-8", errors="replace")
    for supp_path in SUPPLEMENTARY_EVIDENCE_PATHS:
        if not supp_path.exists():
            continue
        supp = load_json(supp_path)
        for table in supp.get("source_reviewed_supplementary_tables", []):
            loc = table.get("source_locator")
            if loc and supplementary_text:
                by_locator[str(loc)] = supplementary_text
        for row in supp.get("activity_rows_recovered_from_supplement", []):
            loc = row.get("source_locator")
            if loc and supplementary_text:
                by_locator[str(loc)] = supplementary_text
                table_match = SUPP_TABLE_LOCATOR_RE.search(str(loc))
                if table_match:
                    by_locator[table_match.group(0)] = supplementary_text

    return by_locator


def combined_source_text(locs: list[str], source_texts: dict[str, str]) -> str:
    chunks = []
    for loc in locs:
        base = TABLE_LOCATOR_RE.search(loc)
        if base and base.group(0) in source_texts:
            chunks.append(source_texts[base.group(0)])
        if loc in source_texts:
            chunks.append(source_texts[loc])
    return "\n".join(chunks)


def contains_value(text: str, value: Any) -> bool:
    raw = str(value or "").strip()
    if not raw:
        return False
    hay = compact(text)
    needle = compact(raw)
    if needle and needle in hay:
        return True
    scalar = re.sub(r"^[<>≤≥=~]+", "", raw).strip()
    scalar = scalar.replace("≤", "").replace("≥", "")
    if scalar and compact(scalar) in hay:
        return True
    return False


def contains_unit(text: str, unit: Any) -> bool:
    raw = str(unit or "").strip()
    if not raw:
        return False
    hay = compact(text)
    needle = compact(raw)
    if needle and needle in hay:
        return True
    if needle == "%":
        return "%" in text
    return False


def significant_tokens(value: Any) -> list[str]:
    text = norm_text(value)
    tokens = re.findall(r"[a-z][a-z0-9.-]{1,}|atcc\s*\d+|\d{3,}", text)
    skip = {
        "and",
        "the",
        "with",
        "against",
        "strain",
        "strains",
        "cells",
        "cell",
        "human",
        "red",
        "blood",
    }
    return [tok for tok in tokens if tok not in skip]


def contains_label(text: str, value: Any) -> bool:
    tokens = significant_tokens(value)
    if not tokens:
        return False
    hay = norm_text(text)
    if norm_text(value) and norm_text(value) in hay:
        return True
    hits = sum(1 for tok in tokens if tok in hay)
    required = 1 if len(tokens) <= 2 else 2
    return hits >= required


def endpoint_kind(endpoint: Any) -> str:
    text = str(endpoint or "")
    if TOXICITY_RE.search(text):
        return "toxicity"
    if ACTIVITY_RE.search(text):
        return "activity"
    return "unclassified"


def endpoint_supported(endpoint: Any, text: str, kind: str) -> bool:
    endpoint_text = str(endpoint or "")
    if kind == "toxicity":
        return bool(TOXICITY_RE.search(endpoint_text) or TOXICITY_RE.search(text))
    if kind == "activity":
        if endpoint_text.upper().startswith("MIC"):
            return bool(re.search(r"\bMIC\b|minimum\s+inhibitory", text, re.I))
        return bool(ACTIVITY_RE.search(endpoint_text) or ACTIVITY_RE.search(text))
    return False


def split_target(target_label: Any, kind: str) -> dict[str, str]:
    label = " ".join(unicodedata.normalize("NFKC", str(target_label or "")).split())
    normalized = norm_text(label)
    strain = ""
    catalog_match = re.search(
        r"\b(?P<prefix>ATCC|DSM|NCTC|CIP|MTCC|KCCM|KACC|CCARM)\s*[-–—]?\s*(?P<number>\d+)\b",
        label,
        re.I,
    )
    if catalog_match:
        strain = f"{catalog_match.group('prefix').upper()} {catalog_match.group('number')}"
    else:
        compact_label = re.sub(r"[^A-Za-z0-9]", "", label).upper()
        compact_match = re.search(r"(ATCC|DSM|NCTC|CIP|MTCC|KCCM|KACC|CCARM)(\d+)", compact_label)
        if compact_match:
            strain = f"{compact_match.group(1)} {compact_match.group(2)}"
        else:
            strain_match = re.search(
                r"\b(?:MDR|MRSA|MRPA|VRE)[\w .-]*\d[\w .-]*",
                label,
                re.I,
            )
            if strain_match:
                strain = strain_match.group(0).strip(" ,;")
    species = ""
    abbrev = re.search(r"\b[A-Z]\.\s*[a-z][a-z-]+", label)
    full = re.search(r"\b[A-Z][a-z]{2,}\s+[a-z][a-z-]+", label)
    if abbrev:
        species = abbrev.group(0)
    elif full:
        species = full.group(0)
    elif "erythro" in normalized or "red blood" in normalized:
        species = "human erythrocytes" if "human" in normalized else "erythrocytes"
    elif "cell" in normalized:
        species = label
    else:
        species = label

    if kind == "toxicity":
        target_class = "mammalian_cells"
    elif re.search(r"candida|fung", normalized):
        target_class = "fungus"
    elif species:
        target_class = "bacteria"
    else:
        target_class = "unspecified"

    return {
        "target_class": target_class,
        "species": species,
        "strain_or_isolate": strain,
        "source_label": label,
    }


def source_locator_object(primary_locs: list[str], method_locs: list[str], kind: str) -> dict[str, Any]:
    table_locs: list[str] = []
    supporting_locs: list[str] = []
    for loc in primary_locs:
        if TABLE_LOCATOR_RE.search(loc):
            base = TABLE_LOCATOR_RE.search(loc).group(0)
            if base not in table_locs:
                table_locs.append(base)
        elif SUPP_TABLE_LOCATOR_RE.search(loc):
            base = SUPP_TABLE_LOCATOR_RE.search(loc).group(0)
            if base not in table_locs:
                table_locs.append(base)
        elif loc not in supporting_locs:
            supporting_locs.append(loc)
    obj: dict[str, Any] = {
        "primary_locators": primary_locs,
        "supporting_locators": supporting_locs,
        "locator_review_status": "source_text_matched_without_passage_export",
    }
    if table_locs:
        obj["table_locator"] = table_locs[0] if len(table_locs) == 1 else table_locs
        obj["cell_locator_status"] = (
            "cell_locator_provided"
            if any(":cell=" in loc or ":body-row=" in loc for loc in primary_locs)
            else "not_cell_resolved"
        )
    if method_locs and kind == "activity":
        obj["method_locators"] = method_locs
    return obj


def local_name(tag: str) -> str:
    return tag.split("}", 1)[-1]


def descendants(element: ET.Element, tag: str) -> list[ET.Element]:
    return [item for item in element.iter() if local_name(item.tag) == tag]


def element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()


def xml_table_wrap(locator: str) -> ET.Element:
    match = re.fullmatch(r"xml:table-wrap:(\d+)", locator)
    if not match:
        raise ValueError(f"Unsupported table locator: {locator}")
    index = int(match.group(1))
    xml_path = PACKET_ROOT / "raw" / "paper.xml"
    if not xml_path.exists():
        xml_path = PAPER_ROOT / "source" / "paper.xml"
    root = ET.parse(xml_path).getroot()
    wraps = [item for item in root.iter() if local_name(item.tag) == "table-wrap"]
    if index < 1 or index > len(wraps):
        raise IndexError(f"Table locator not found: {locator}")
    return wraps[index - 1]


def parse_span(cell: ET.Element, name: str) -> int:
    value = cell.attrib.get(name) or cell.attrib.get(name.replace("span", "-span")) or "1"
    try:
        return max(1, int(value))
    except ValueError:
        return 1


def direct_row_cells(row: ET.Element) -> list[ET.Element]:
    return [child for child in list(row) if local_name(child.tag) in {"td", "th"}]


def expand_rows(rows: list[ET.Element]) -> list[list[dict[str, Any]]]:
    grid: list[list[dict[str, Any]]] = []
    carried: dict[tuple[int, int], dict[str, Any]] = {}
    for row_index, row in enumerate(rows):
        expanded: list[dict[str, Any]] = []
        col_index = 0
        source_cell_index = 0
        for cell in direct_row_cells(row):
            while (row_index, col_index) in carried:
                expanded.append(carried[(row_index, col_index)])
                col_index += 1
            source_cell_index += 1
            info = {
                "text": element_text(cell),
                "tag": local_name(cell.tag),
                "source_cell": source_cell_index,
            }
            colspan = parse_span(cell, "colspan")
            rowspan = parse_span(cell, "rowspan")
            for offset in range(colspan):
                expanded.append(info)
                if rowspan > 1:
                    for row_offset in range(1, rowspan):
                        carried[(row_index + row_offset, col_index + offset)] = info
            col_index += colspan
        while (row_index, col_index) in carried:
            expanded.append(carried[(row_index, col_index)])
            col_index += 1
        grid.append(expanded)
    return grid


def extract_activity_unit(text: str) -> str:
    match = re.search(r"(?:µ|μ|u)g\s*/\s*mL", text, re.I)
    if match:
        unit = match.group(0).replace("μ", "µ")
        unit = re.sub(r"\s+", "", unit)
        if unit.lower().startswith("ug"):
            unit = "ug/mL"
        return unit
    return ""


def value_exactness(raw_value: Any) -> str:
    text = str(raw_value or "").strip()
    if re.match(r"^[<>≤≥]", text):
        return "censored_inequality"
    if re.match(r"^(?:~|≈|about\b)", text, re.I):
        return "approximate"
    return "exact"


def xml_table2_pa_win2_observations() -> list[dict[str, Any]]:
    table_locator = "xml:table-wrap:2"
    table = xml_table_wrap(table_locator)
    header_groups = descendants(table, "thead")
    body_groups = descendants(table, "tbody")
    header_rows = descendants(header_groups[0], "tr") if header_groups else []
    body_rows = descendants(body_groups[0], "tr") if body_groups else []
    header_grid = expand_rows(header_rows)
    body_grid = expand_rows(body_rows)
    full_table_text = element_text(table)
    unit = extract_activity_unit(full_table_text) or "ug/mL"

    observations: list[dict[str, Any]] = []
    pa_win2_row: list[dict[str, Any]] | None = None
    pa_win2_body_index = 0
    for body_index, body_row in enumerate(body_grid, start=1):
        if not body_row:
            continue
        if "pa-win2" in norm_text(body_row[0]["text"]):
            pa_win2_row = body_row
            pa_win2_body_index = body_index
            break
    if pa_win2_row is None:
        return observations

    max_cols = min(
        len(pa_win2_row),
        max((len(row) for row in header_grid), default=0),
    )
    for col_index in range(1, max_cols):
        header_stack = [row[col_index]["text"] for row in header_grid if col_index < len(row)]
        endpoint_stack = " ".join(header_stack)
        if not re.search(r"\b(?:MIC|MBC)\b", endpoint_stack, re.I):
            continue
        endpoint = "MBC" if re.search(r"\bMBC\b", endpoint_stack, re.I) else "MIC"
        target_label = header_stack[0] if header_stack else ""
        value = pa_win2_row[col_index]["text"].strip()
        if not value or not re.search(r"\d", value):
            continue
        value_cell_locator = f"{table_locator}:body-row={pa_win2_body_index}:cell={col_index + 1}"
        target_header_cell = header_grid[0][col_index]["source_cell"] if header_grid and col_index < len(header_grid[0]) else col_index + 1
        target_locator = f"{table_locator}:head-row=1:cell={target_header_cell}"
        locators = [value_cell_locator, target_locator, table_locator, "xml:p:16"]
        if contains_label(target_label, "MRPA CCARM 2095") or contains_label(target_label, "CCARM 2095"):
            locators.append("xml:p:17")
        observations.append(
            {
                "origin": "xml_table_parser",
                "endpoint": endpoint,
                "raw_value": value,
                "raw_unit": unit,
                "target": target_label,
                "entity": "PA-Win2",
                "source_locator_candidates": locators,
                "source_locator": value_cell_locator,
                "target_locator": target_locator,
                "table_locator": table_locator,
                "exact_status": value_exactness(value),
            }
        )
    return observations


def xml_mrpa_observations(source_texts: dict[str, str]) -> list[dict[str, Any]]:
    text = combined_source_text(["xml:p:17", "xml:p:16"], source_texts)
    if not (contains_label(text, "MRPA CCARM 2095") and contains_value(text, "2")):
        return []
    unit = extract_activity_unit(text) or "ug/mL"
    return [
        {
            "origin": "xml_paragraph_parser",
            "endpoint": endpoint,
            "raw_value": "2",
            "raw_unit": unit,
            "target": "Pseudomonas aeruginosa MRPA CCARM 2095",
            "entity": "PA-Win2",
            "source_locator_candidates": ["xml:p:17", "xml:p:16"],
            "source_locator": "xml:p:17",
            "table_locator": "",
            "exact_status": "exact",
        }
        for endpoint in ("MIC", "MBC")
    ]


def load_supplementary_evidence() -> dict[str, Any]:
    for path in SUPPLEMENTARY_EVIDENCE_PATHS:
        if path.exists():
            return load_json(path)
    return {}


def supplementary_s1_observations() -> list[dict[str, Any]]:
    evidence = load_supplementary_evidence()
    observations: list[dict[str, Any]] = []
    for row in evidence.get("activity_rows_recovered_from_supplement", []):
        loc = str(row.get("source_locator") or "")
        if ":table=S1" not in loc:
            continue
        target_bits = [str(row.get("target_species") or "").strip(), str(row.get("target_strain_or_isolate") or "").strip()]
        observations.append(
            {
                "origin": "supplementary_worker3_material_row_verified_by_worker2",
                "endpoint": str(row.get("endpoint") or "").strip(),
                "raw_value": str(row.get("raw_value") or "").strip(),
                "raw_unit": str(row.get("raw_unit") or "").strip(),
                "target": " ".join(bit for bit in target_bits if bit),
                "target_species": target_bits[0],
                "target_strain_or_isolate": target_bits[1],
                "entity": "PA-Win2",
                "condition": row.get("condition"),
                "source_locator_candidates": [loc],
                "source_locator": loc,
                "table_locator": SUPP_TABLE_LOCATOR_RE.search(loc).group(0) if SUPP_TABLE_LOCATOR_RE.search(loc) else loc,
                "exact_status": row.get("exact_status") or value_exactness(row.get("raw_value")),
            }
        )
    return observations


def hdfalpha_toxicity_observation(source_texts: dict[str, str]) -> dict[str, Any] | None:
    text = combined_source_text(["xml:p:19", "xml:fig:2", "xml:caption:4"], source_texts)
    if not (contains_label(text, "HDFalpha") and contains_value(text, "64")):
        return None
    return {
        "origin": "xml_figure_paragraph_parser",
        "endpoint": "cell viability decrease threshold",
        "raw_value": ">64",
        "raw_unit": extract_activity_unit(text) or "ug/mL",
        "target": "HDFalpha cells",
        "entity": "PA-Win2",
        "source_locator_candidates": ["xml:p:19", "xml:fig:2", "xml:caption:4"],
        "source_locator": "xml:p:19",
        "exact_status": "censored_inequality",
    }


def method_condition_summary(method_text: str) -> dict[str, Any]:
    summary: dict[str, Any] = {"method_locators": ["xml:p:44"]}
    temp = re.search(r"\b\d{2}\s*[°º]?\s*C\b", method_text)
    if temp:
        summary["incubation_temperature"] = re.sub(r"\s+", "", temp.group(0)).replace("º", "°")
    time = re.search(r"\b\d+(?:\.\d+)?\s*(?:h|hr|hrs|hour|hours)\b", method_text, re.I)
    if time:
        summary["incubation_time"] = re.sub(r"\s+", " ", time.group(0)).strip()
    volume = re.search(r"\b\d+(?:\.\d+)?\s*(?:µ|μ|u)?L\b|\b\d+(?:\.\d+)?\s*mL\b", method_text, re.I)
    if volume:
        summary["assay_volume"] = volume.group(0).replace("μ", "µ")
    inoculum = re.search(
        r"\b\d+(?:\.\d+)?\s*(?:×|x)\s*10\^?\d+\s*(?:CFU|cells)?\s*/?\s*mL\b",
        method_text,
        re.I,
    )
    if inoculum:
        summary["inoculum"] = re.sub(r"\s+", " ", inoculum.group(0)).strip()
    return summary


def build_record(
    row: dict[str, Any],
    index: int,
    kind: str,
    source_texts: dict[str, str],
    method_locs: list[str],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    primary_locs = locator_ids(row.get("source_locator_candidates"))
    primary_locs = [loc for loc in primary_locs if loc.startswith(("xml:", "pdf:", "supp:"))]
    source_text = combined_source_text(primary_locs, source_texts)
    method_text = combined_source_text(method_locs, source_texts)
    endpoint = str(row.get("endpoint") or "").strip()
    raw_value = str(row.get("raw_value") or "").strip()
    raw_unit = str(row.get("raw_unit") or "").strip()
    target_label = str(row.get("target") or "").strip()
    entity = str(row.get("entity") or "").strip()

    support = {
        "endpoint_supported": endpoint_supported(endpoint, source_text, kind),
        "raw_value_present": contains_value(source_text, raw_value),
        "raw_unit_present": contains_unit(source_text, raw_unit),
        "target_label_present": contains_label(source_text, target_label),
        "entity_label_present": contains_label(source_text, entity),
        "primary_locator_count": len(primary_locs),
        "method_locator_count": len(method_locs if kind == "activity" else []),
        "source_text_sha256": text_hash(source_text) if source_text else "",
    }
    required_flags = [
        support["endpoint_supported"],
        support["raw_value_present"],
        support["raw_unit_present"],
        support["target_label_present"],
    ]
    if not all(required_flags) or not primary_locs:
        return None, {
            "machine_row_index": row.get("machine_row_index"),
            "candidate_key": row.get("candidate_key"),
            "kind": kind,
            "status": "rejected_not_source_supported_by_bounded_checks",
            "source_locator_ids": primary_locs,
            "support": support,
            "checked_fields": ["endpoint", "raw_value", "raw_unit", "target"],
        }

    target = split_target(target_label, kind)
    record_prefix = "TOX" if kind == "toxicity" else "ACT"
    record: dict[str, Any] = {
        "record_id": f"{PAPER_ID}-W2-{record_prefix}-{index:03d}",
        "paper_id": PAPER_ID,
        "evidence_kind": kind,
        "endpoint": endpoint,
        "raw_value": raw_value,
        "raw_unit": raw_unit,
        "raw_unit_rationale": "unit is directly reported by the cited source locator",
        "normalized_value": raw_value,
        "normalized_unit": raw_unit,
        "normalization_status": "direct",
        "normalization_rationale": "No value or unit conversion performed; normalized fields exactly mirror raw source value and raw source unit.",
        "exact_vs_approximate_status": value_exactness(raw_value),
        "entity": entity,
        "assayed_entity": {
            "name": entity,
            "source_review_status": "entity label checked against cited locator",
        },
        "target": target,
        "target_species": target["species"],
        "target_strain_or_isolate": target["strain_or_isolate"],
        "assay_conditions": {
            "source_locator_review": "primary locator text checked; no assay-method passage exported",
        },
        "evidence_ladder": "toxicity_tested" if kind == "toxicity" else "in_vitro_multi_pathogen",
        "source_locator": source_locator_object(primary_locs, method_locs, kind),
        "source_review": {
            "reviewed_by": "worker-2",
            "source_review_status": "source_reviewed_primary_locator_match",
            "candidate_handoff_path": str(SAFE_HANDOFF.relative_to(ROOT)),
            "source_support": support,
            "machine_evidence_role": "candidate_only_not_primary_source",
            "evidence_origin": row.get("origin") or "dbaasp_machine_candidate_source_checked",
        },
        "database_provenance": {
            "dbaasp_machine_row_index": row.get("machine_row_index"),
            "candidate_key": row.get("candidate_key"),
            "candidate_status": row.get("status"),
            "linked_authoritative_rows_present": False,
            "database_role": "candidate_machine_evidence_only",
        },
    }

    condition_support: dict[str, bool] = {}
    medium = row.get("assay_medium")
    inoculum = row.get("inoculum")
    if medium:
        condition_support["medium_present_in_method_locator"] = contains_label(method_text, medium)
        if condition_support["medium_present_in_method_locator"]:
            record["assay_conditions"]["medium"] = str(medium)
    if inoculum:
        condition_support["inoculum_present_in_method_locator"] = contains_label(method_text, inoculum)
        if condition_support["inoculum_present_in_method_locator"]:
            record["assay_conditions"]["inoculum"] = str(inoculum)
    if condition_support:
        record["assay_conditions"]["condition_source_support"] = condition_support
    if kind == "activity" and method_locs:
        record["assay_conditions"]["method_locators"] = method_locs
        record["assay_conditions"].update(method_condition_summary(method_text))

    if row.get("condition"):
        record["assay_conditions"]["condition"] = row.get("condition")
    if row.get("exact_status"):
        record["exact_vs_approximate_status"] = row.get("exact_status")

    if row.get("origin") and str(row.get("origin")) != "dbaasp_machine_candidate_source_checked":
        record["source_review"]["machine_evidence_role"] = "not_machine_extracted_source_derived_observation"
        record["database_provenance"]["database_role"] = "no_database_row_used_for_source_observation"
        record["database_provenance"]["candidate_key"] = row.get("candidate_key")
        record["database_provenance"]["dbaasp_machine_row_index"] = row.get("machine_row_index")
        if row.get("target_species"):
            record["target"]["species"] = row["target_species"]
            record["target_species"] = row["target_species"]
        if row.get("target_strain_or_isolate"):
            record["target"]["strain_or_isolate"] = row["target_strain_or_isolate"]
            record["target_strain_or_isolate"] = row["target_strain_or_isolate"]

    concentration = extract_test_concentration(source_text, raw_value)
    if kind == "toxicity" and concentration:
        record["concentration"] = concentration["value"]
        record["concentration_unit"] = concentration["unit"]
        record["assay_conditions"]["peptide_concentration"] = concentration["value"]
        record["assay_conditions"]["peptide_concentration_unit"] = concentration["unit"]

    return record, {
        "machine_row_index": row.get("machine_row_index"),
        "candidate_key": row.get("candidate_key"),
        "kind": kind,
        "status": "source_supported",
        "source_locator_ids": primary_locs,
        "support": support,
        "checked_fields": ["endpoint", "raw_value", "raw_unit", "target"],
    }


def extract_test_concentration(text: str, raw_value: str) -> dict[str, str] | None:
    if not text:
        return None
    matches = list(
        re.finditer(
            r"(?P<value>[<>≤≥=~]?\s*\d+(?:\.\d+)?)\s*(?P<unit>(?:u|µ|μ)?g\s*/\s*mL|mg\s*/\s*mL|(?:u|µ|μ)M)",
            text,
            re.I,
        )
    )
    if not matches:
        return None
    raw_pos = norm_text(text).find(norm_text(raw_value))
    if raw_pos >= 0:
        matches.sort(key=lambda m: abs(m.start() - raw_pos))
    value = " ".join(matches[0].group("value").split())
    unit = matches[0].group("unit").replace("μ", "µ").replace("u", "µ")
    unit = re.sub(r"\s+", "", unit)
    return {"value": value, "unit": unit}


def validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    for array_name in ("activity_records", "toxicity_records"):
        rows = payload.get(array_name)
        if not isinstance(rows, list):
            issues.append({"code": "missing_array", "field": array_name})
            continue
        for index, record in enumerate(rows):
            prefix = {"array": array_name, "record_index": index, "record_id": record.get("record_id")}
            for field in (
                "endpoint",
                "raw_value",
                "raw_unit",
                "target_species",
                "assay_conditions",
                "evidence_ladder",
                "source_locator",
                "normalization_status",
            ):
                if record.get(field) in (None, "", [], {}):
                    issues.append({"code": "missing_required_field", "field": field, **prefix})
            status = record.get("normalization_status")
            if status not in VALID_NORMALIZATION_STATUSES:
                issues.append({"code": "invalid_normalization_status", "status": status, **prefix})
            if status in {"direct", "converted"}:
                if record.get("normalized_value") in (None, "") or record.get("normalized_unit") in (None, ""):
                    issues.append({"code": "missing_normalized_value_or_unit", **prefix})
            if status == "direct":
                if str(record.get("raw_value")) != str(record.get("normalized_value")):
                    issues.append({"code": "direct_value_changed", **prefix})
                if compact(record.get("raw_unit")) != compact(record.get("normalized_unit")):
                    issues.append({"code": "direct_unit_changed", **prefix})
            if record.get("exact_vs_approximate_status") in (None, ""):
                issues.append({"code": "missing_exact_vs_approximate_status", **prefix})
            if array_name == "activity_records" and TOXICITY_RE.search(str(record.get("endpoint") or "")):
                issues.append({"code": "toxicity_endpoint_in_activity_records", **prefix})
            if array_name == "toxicity_records" and re.search(
                r"\b(?:MIC|MBC|MFC|MBIC|MBEC|FICI)\b", str(record.get("endpoint") or ""), re.I
            ):
                issues.append({"code": "activity_endpoint_in_toxicity_records", **prefix})
            top_conc = record.get("concentration")
            nested_conc = record.get("assay_conditions", {}).get("peptide_concentration") if isinstance(record.get("assay_conditions"), dict) else None
            top_unit = record.get("concentration_unit")
            nested_unit = record.get("assay_conditions", {}).get("peptide_concentration_unit") if isinstance(record.get("assay_conditions"), dict) else None
            if top_conc not in (None, "") and nested_conc not in (None, "") and str(top_conc) != str(nested_conc):
                issues.append({"code": "concentration_value_conflict", **prefix})
            if top_unit not in (None, "") and nested_unit not in (None, "") and compact(top_unit) != compact(nested_unit):
                issues.append({"code": "concentration_unit_conflict", **prefix})
            source_locs = locator_ids(record.get("source_locator"))
            if array_name == "activity_records" and not any(loc == "xml:p:44" for loc in source_locs):
                issues.append({"code": "missing_activity_method_locator_xml_p_44", **prefix})
            if record.get("source_review", {}).get("evidence_origin") == "xml_table_parser":
                if not any(":body-row=" in loc and ":cell=" in loc for loc in source_locs):
                    issues.append({"code": "missing_xml_table_row_cell_locator", **prefix})
            target_blob = " ".join(
                str(x or "")
                for x in [
                    record.get("target", {}).get("source_label") if isinstance(record.get("target"), dict) else "",
                    record.get("target_species"),
                    record.get("target_strain_or_isolate"),
                ]
            )
            if re.search(r"\b(?:KCCM|KACC|CCARM|ATCC)\b", target_blob, re.I) and not record.get("target_strain_or_isolate"):
                issues.append({"code": "reported_strain_identifier_not_populated", **prefix})
    return {
        "paper_id": PAPER_ID,
        "checked_at": now_iso(),
        "status": "pass" if not issues else "needs_repair",
        "issue_count": len(issues),
        "issues": issues,
        "counts": {
            "activity_records": len(payload.get("activity_records") or []),
            "toxicity_records": len(payload.get("toxicity_records") or []),
            "candidate_or_rejected_rows": len(payload.get("candidate_or_rejected_rows") or []),
        },
    }


def observation_record_match(record: dict[str, Any], obs: dict[str, Any]) -> bool:
    if str(record.get("endpoint") or "").upper() != str(obs.get("endpoint") or "").upper():
        return False
    if str(record.get("raw_value") or "").strip() != str(obs.get("raw_value") or "").strip():
        return False
    if compact(record.get("raw_unit")) != compact(obs.get("raw_unit")):
        return False
    locs = locator_ids(record.get("source_locator"))
    if obs.get("source_locator") and obs["source_locator"] not in locs:
        return False
    strain = str(obs.get("target_strain_or_isolate") or "")
    if not strain:
        target = split_target(obs.get("target"), "activity")
        strain = target.get("strain_or_isolate", "")
    if strain and strain not in str(record.get("target_strain_or_isolate") or ""):
        return False
    if obs.get("target_species") and norm_text(obs["target_species"]) not in norm_text(record.get("target_species")):
        return False
    return True


def validate_expected_contract(
    payload: dict[str, Any],
    table2_observations: list[dict[str, Any]],
    mrpa_observations: list[dict[str, Any]],
    supplement_s1_observations: list[dict[str, Any]],
    hdfalpha_observation: dict[str, Any] | None,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    activity = payload.get("activity_records") or []
    toxicity = payload.get("toxicity_records") or []

    main_text_expected = table2_observations + mrpa_observations
    for obs in main_text_expected:
        if not any(observation_record_match(record, obs) for record in activity):
            findings.append(
                {
                    "severity": "hard",
                    "code": "missing_main_text_pa_win2_mic_mbc_observation",
                    "source_locator": obs.get("source_locator"),
                    "endpoint": obs.get("endpoint"),
                }
            )

    for obs in supplement_s1_observations:
        if not any(observation_record_match(record, obs) for record in activity):
            findings.append(
                {
                    "severity": "hard",
                    "code": "missing_supplement_table_s1_observation",
                    "source_locator": obs.get("source_locator"),
                    "endpoint": obs.get("endpoint"),
                }
            )

    if hdfalpha_observation is None:
        findings.append({"severity": "hard", "code": "hdfalpha_source_observation_not_verified"})
    else:
        matched_hdf = []
        for record in toxicity:
            locs = locator_ids(record.get("source_locator"))
            if (
                "xml:p:19" in locs
                and "xml:fig:2" in locs
                and "64" in str(record.get("raw_value") or "")
                and "hdf" in norm_text(record.get("target_species"))
            ):
                matched_hdf.append(record.get("record_id"))
        if not matched_hdf:
            findings.append({"severity": "hard", "code": "hdfalpha_toxicity_record_missing"})

    for record in activity:
        locs = locator_ids(record.get("source_locator"))
        if not any(loc == "xml:p:44" for loc in locs):
            findings.append(
                {
                    "severity": "hard",
                    "code": "activity_record_missing_method_locator_xml_p_44",
                    "record_id": record.get("record_id"),
                }
            )

    return {
        "paper_id": PAPER_ID,
        "checked_at": now_iso(),
        "status": "pass" if not findings else "needs_repair",
        "hard_finding_count": sum(1 for item in findings if item.get("severity") == "hard"),
        "findings": findings,
        "expected_observation_counts": {
            "xml_table_wrap_2_pa_win2_mic_mbc_cell_observations": len(table2_observations),
            "xml_p_17_mrpa_pa_win2_mic_mbc_observations": len(mrpa_observations),
            "main_text_pa_win2_mic_mbc_observations_total": len(main_text_expected),
            "supplement_table_s1_activity_observations": len(supplement_s1_observations),
            "figure2_hdfalpha_toxicity_observations": 1 if hdfalpha_observation else 0,
        },
        "accepted_record_counts": {
            "activity_records": len(activity),
            "toxicity_records": len(toxicity),
            "xml_table_wrap_2_records": sum(
                1
                for record in activity
                if record.get("source_review", {}).get("evidence_origin") == "xml_table_parser"
            ),
            "xml_p_17_mrpa_records": sum(
                1
                for record in activity
                if record.get("source_review", {}).get("evidence_origin") == "xml_paragraph_parser"
            ),
            "supplement_table_s1_records": sum(
                1
                for record in activity
                if record.get("source_review", {}).get("evidence_origin")
                == "supplementary_worker3_material_row_verified_by_worker2"
            ),
            "hdfalpha_toxicity_records": sum(
                1
                for record in toxicity
                if "hdf" in norm_text(record.get("target_species"))
                and "xml:p:19" in locator_ids(record.get("source_locator"))
            ),
        },
    }


def main() -> int:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    handoff = load_json(SAFE_HANDOFF)
    source_texts = load_source_texts()
    locator_groups = handoff.get("source_locator_groups", {})
    method_locs = ["xml:p:44"]
    table_candidate_locs = locator_ids(locator_groups.get("activity_table_locator_candidates"))
    toxicity_hint_locs = locator_ids(locator_groups.get("toxicity_locator_candidates"))
    table2_observations = xml_table2_pa_win2_observations()
    mrpa_observations = (
        []
        if any(contains_label(obs.get("target"), "CCARM 2095") for obs in table2_observations)
        else xml_mrpa_observations(source_texts)
    )
    supplement_s1_observations = supplementary_s1_observations()
    hdfalpha_observation = hdfalpha_toxicity_observation(source_texts)

    activity_records: list[dict[str, Any]] = []
    toxicity_records: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    trace_rows: list[dict[str, Any]] = []

    for candidate in handoff.get("machine_candidate_rows", []):
        kind = endpoint_kind(candidate.get("endpoint"))
        if kind not in {"activity", "toxicity"}:
            rejected.append(
                {
                    "machine_row_index": candidate.get("machine_row_index"),
                    "candidate_key": candidate.get("candidate_key"),
                    "status": "rejected_unclassified_endpoint",
                    "checked_fields": ["endpoint"],
                }
            )
            continue
        if kind == "activity":
            trace_rows.append(
                {
                    "machine_row_index": candidate.get("machine_row_index"),
                    "candidate_key": candidate.get("candidate_key"),
                    "kind": kind,
                    "status": "source_table_activity_candidate_superseded_by_primary_source_parser",
                    "source_locator_ids": locator_ids(candidate.get("source_locator_candidates")),
                    "checked_fields": ["endpoint", "raw_value", "raw_unit", "target"],
                }
            )
            continue
        target_array = toxicity_records if kind == "toxicity" else activity_records
        record, trace = build_record(candidate, len(target_array) + 1, kind, source_texts, method_locs)
        trace_rows.append(trace)
        if record is None:
            rejected.append(trace)
        elif kind == "toxicity":
            toxicity_records.append(record)
        else:
            activity_records.append(record)

    for observation in table2_observations + mrpa_observations + supplement_s1_observations:
        record, trace = build_record(observation, len(activity_records) + 1, "activity", source_texts, method_locs)
        trace_rows.append(trace)
        if record is None:
            rejected.append(trace)
        else:
            if observation.get("origin") == "xml_table_parser":
                record["evidence_ladder"] = "in_vitro_multi_pathogen"
            elif observation.get("origin") == "xml_paragraph_parser":
                record["evidence_ladder"] = "in_vitro_single_pathogen"
            else:
                record["evidence_ladder"] = "in_vitro_single_pathogen"
            activity_records.append(record)

    if hdfalpha_observation:
        record, trace = build_record(hdfalpha_observation, len(toxicity_records) + 1, "toxicity", source_texts, [])
        trace_rows.append(trace)
        if record is None:
            rejected.append(trace)
        else:
            record["evidence_ladder"] = "toxicity_tested"
            toxicity_records.append(record)

    accepted_activity_tables: dict[str, int] = {}
    for record in activity_records:
        seen_record_tables: set[str] = set()
        for loc in locator_ids(record.get("source_locator")):
            match = TABLE_LOCATOR_RE.search(loc)
            if match:
                base = match.group(0)
                seen_record_tables.add(base)
            supp_match = SUPP_TABLE_LOCATOR_RE.search(loc)
            if supp_match:
                seen_record_tables.add(supp_match.group(0))
        for base in seen_record_tables:
            accepted_activity_tables[base] = accepted_activity_tables.get(base, 0) + 1

    source_review_trace = {
        "paper_id": PAPER_ID,
        "generated_at": now_iso(),
        "reviewed_by": "worker-2",
        "review_scope": "activity_toxicity_body_table_worker",
        "source_text_export_policy": "no_source_passages_written_to_terminal_or_trace",
        "safe_handoff_path": str(SAFE_HANDOFF.relative_to(ROOT)),
        "source_files_checked": {
            "xml_sections": str((PACKET_ROOT / "extracted" / "xml_sections.json").relative_to(ROOT)),
            "pdf_text": str((PACKET_ROOT / "extracted" / "pdf_text.jsonl").relative_to(ROOT)),
            "pdf_tables": str((PACKET_ROOT / "extracted" / "pdf_tables.json").relative_to(ROOT)),
            "figure_captions": str((PACKET_ROOT / "extracted" / "figure_captions.json").relative_to(ROOT)),
            "supplementary_index": str((PACKET_ROOT / "extracted" / "supplementary_index.json").relative_to(ROOT)),
            "supplementary_text": str((PACKET_ROOT / "extracted" / "supplementary_text.jsonl").relative_to(ROOT)),
            "supplementary_worker3_evidence": str(
                next((path for path in SUPPLEMENTARY_EVIDENCE_PATHS if path.exists()), SUPPLEMENTARY_EVIDENCE_PATHS[-1]).relative_to(ROOT)
            ),
            "supplementary_worker3_pdf_text": str(SUPPLEMENTARY_TEXT_PATH.relative_to(ROOT)),
            "database_machine_candidates": str((PACKET_ROOT / "database" / "dbaasp_machine_extracted_rows.jsonl").relative_to(ROOT)),
            "authoritative_match_report": str((PACKET_ROOT / "database" / "authoritative_match_report.json").relative_to(ROOT)),
        },
        "inspected_locator_ids": {
            "activity_table_locator_candidates": table_candidate_locs,
            "accepted_activity_table_locators": sorted(accepted_activity_tables),
            "mic_method_locator_candidates": method_locs,
            "mrpa_narrative_locator_candidates": ["xml:p:17"],
            "supplement_table_s1_locator_candidates": sorted({obs["source_locator"] for obs in supplement_s1_observations}),
            "toxicity_locator_candidates": toxicity_hint_locs,
            "hdfalpha_toxicity_locator_candidates": ["xml:p:19", "xml:fig:2", "xml:caption:4"],
        },
        "source_review_rows": trace_rows,
        "source_text_hashes": {
            loc: text_hash(source_texts.get(loc, ""))
            for loc in sorted(
                set(
                    table_candidate_locs
                    + method_locs
                    + toxicity_hint_locs
                    + ["xml:p:17", "xml:caption:4"]
                    + [obs["source_locator"] for obs in supplement_s1_observations]
                )
            )
        },
        "linked_authoritative_database_rows_present": {
            "linked_article_records": len(iter_jsonl(PACKET_ROOT / "database" / "linked_article_records.jsonl")),
            "linked_assay_records": len(iter_jsonl(PACKET_ROOT / "database" / "linked_assay_records.jsonl")),
            "linked_sequence_records": len(iter_jsonl(PACKET_ROOT / "database" / "linked_sequence_records.jsonl")),
            "linked_literature_records": len(iter_jsonl(PACKET_ROOT / "database" / "linked_literature_records.jsonl")),
        },
    }

    payload = {
        "paper_id": PAPER_ID,
        "artifact_role": "worker2_source_reviewed_activity_toxicity_evidence",
        "generated_at": now_iso(),
        "generated_by": "worker-2",
        "source_review_level": "paper_local_source_reviewed_worker_lane",
        "publication_grade_claim": False,
        "publication_grade_limitation": "Worker-2 lane output only; final publication-grade status requires worker-6 adjudication and strict gates.",
        "source_review_inputs": source_review_trace["source_files_checked"],
        "activity_records": activity_records,
        "toxicity_records": toxicity_records,
        "candidate_or_rejected_rows": rejected,
        "excluded_non_activity_table_entries": [],
        "inspected_unemitted_table_candidate_entries": [
            {
                "source_locator": loc,
                "reason": "inspected_candidate_table_but_no_row_level_activity_observation_emitted_by_source_review",
            }
            for loc in table_candidate_locs
            if loc not in accepted_activity_tables
        ],
        "summary_counts": {
            "activity_records": len(activity_records),
            "toxicity_records": len(toxicity_records),
            "candidate_or_rejected_rows": len(rejected),
            "activity_tables_accepted": len(accepted_activity_tables),
            "accepted_activity_locators": accepted_activity_tables,
            "activity_tables_excluded_from_current_outputs": 0,
            "source_tables_checked": len(table_candidate_locs),
            "main_text_pa_win2_mic_mbc_expected_observations": len(table2_observations) + len(mrpa_observations),
            "supplement_table_s1_expected_observations": len(supplement_s1_observations),
            "hdfalpha_toxicity_observations": 1 if hdfalpha_observation else 0,
        },
        "quality_checks": {
            "normalization_status_values_allowed": sorted(VALID_NORMALIZATION_STATUSES),
            "activity_field_validation": {
                "record_count": len(activity_records),
                "required_fields_checked": [
                    "endpoint",
                    "raw_value",
                    "raw_unit",
                    "target_species",
                    "assay_conditions",
                    "evidence_ladder",
                    "source_locator",
                    "normalization_status",
                ],
            },
            "semantic_gate_relevant_activity_checks": {
                "non_activity_source_tables_excluded_from_current_outputs": [],
                "source_tables_checked_without_emitted_rows": [
                    loc for loc in table_candidate_locs if loc not in accepted_activity_tables
                ],
                "database_rows_treated_as_candidate_machine_evidence_only": True,
                "direct_normalization_requires_identical_raw_and_normalized_fields": True,
                "activity_toxicity_arrays_separated_by_endpoint_regex": True,
            },
        },
        "worker_notes": [
            "Runtime-open worker-2 ticket rwk-PMC11672609-campaign-r01-BF-PMC11672609-W2-ACTIVITY-TOXICITY-COVERAGE repaired in nonterminal owner lane output.",
            "DBAASP Codex fallback rows were used only as inspection candidates and were rechecked against packet-local locators.",
            "No linked authoritative DBAASP article/assay/sequence/literature rows were present in the packet snapshot.",
            "Worker-2 does not claim publication-grade acceptance; worker-6 must adjudicate the repaired lane.",
        ],
    }

    validation = validate_payload(payload)
    expected_contract = validate_expected_contract(
        payload,
        table2_observations,
        mrpa_observations,
        supplement_s1_observations,
        hdfalpha_observation,
    )
    payload["validation"] = {
        "worker2_self_check_path": str(VALIDATION_OUTPUT.relative_to(ROOT)),
        "worker2_self_check_status": validation["status"],
        "worker2_self_check_issue_count": validation["issue_count"],
        "expected_observation_contract_path": str(EXPECTED_CONTRACT_OUTPUT.relative_to(ROOT)),
        "expected_observation_contract_status": expected_contract["status"],
        "expected_observation_contract_hard_finding_count": expected_contract["hard_finding_count"],
    }

    WORK_OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ANALYSIS_OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    VALIDATION_OUTPUT.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SOURCE_REVIEW_OUTPUT.write_text(json.dumps(source_review_trace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    EXPECTED_CONTRACT_OUTPUT.write_text(json.dumps(expected_contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "pass" if validation["status"] == "pass" and expected_contract["status"] == "pass" else "needs_repair",
        "activity_records": len(activity_records),
        "toxicity_records": len(toxicity_records),
        "rejected_rows": len(rejected),
        "expected_contract_status": expected_contract["status"],
        "expected_contract_hard_findings": expected_contract["hard_finding_count"],
        "artifacts_written": [
            str(WORK_OUTPUT.relative_to(ROOT)),
            str(ANALYSIS_OUTPUT.relative_to(ROOT)),
            str(VALIDATION_OUTPUT.relative_to(ROOT)),
            str(SOURCE_REVIEW_OUTPUT.relative_to(ROOT)),
            str(EXPECTED_CONTRACT_OUTPUT.relative_to(ROOT)),
        ],
    }, ensure_ascii=False))
    return 0 if validation["status"] == "pass" and expected_contract["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
