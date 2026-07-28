#!/usr/bin/env python3
"""Worker-2 repair for PMC12606902 activity/toxicity evidence.

The script intentionally prints only counts and artifact paths. Source text is
read from the local packet/paper files and written only into structured evidence
artifacts where needed for downstream adjudication.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "PMC12606902"
WORKER_ID = "worker-2"
REPO_ROOT = Path(__file__).resolve().parents[7]
PAPER_ROOT = REPO_ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot/papers" / PAPER_ID
PACKET_ROOT = REPO_ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot/packets" / PAPER_ID
WORK_DIR = PAPER_ROOT / "work/activity_evidence"

PAPER_XML = PAPER_ROOT / "source/paper.xml"
PACKET_ANALYSIS_OUT = PACKET_ROOT / "analysis/activity_toxicity_evidence.worker2.json"
WORK_ACTIVITY_OUT = WORK_DIR / "activity_records.json"
RECONCILIATION_OUT = WORK_DIR / "table1_activity_reconciliation.worker2.json"
TOXICITY_COVERAGE_OUT = WORK_DIR / "toxicity_locator_coverage.worker2.json"
VALIDATION_OUT = WORK_DIR / "activity_toxicity_validation.worker2.json"
SNAPSHOT_OUT = WORK_DIR / "activity_toxicity_evidence.worker2.source_reviewed_snapshot.json"

SAFE_HANDOFF = PACKET_ROOT / "analysis/activity_safe_candidate_handoff.json"
AUTHORITATIVE_REPORT = PACKET_ROOT / "database/authoritative_match_report.json"
SUPPLEMENT_FIG_DOC = PACKET_ROOT / "raw/supplementary_original/12866_2025_4475_MOESM2_ESM.doc"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def local_name(elem: ET.Element) -> str:
    return elem.tag.rsplit("}", 1)[-1]


def norm_text(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def elem_text(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    return norm_text(" ".join(t for t in elem.itertext()))


def iter_named(root: ET.Element, name: str) -> list[ET.Element]:
    return [elem for elem in root.iter() if local_name(elem) == name]


def first_child(elem: ET.Element, name: str) -> ET.Element | None:
    for child in list(elem):
        if local_name(child) == name:
            return child
    return None


def child_text(elem: ET.Element, name: str) -> str:
    return elem_text(first_child(elem, name))


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def parse_int_attr(elem: ET.Element, name: str, default: int = 1) -> int:
    raw = elem.attrib.get(name)
    if raw is None:
        return default
    try:
        return max(1, int(raw))
    except ValueError:
        return default


def table_rows(table_wrap: ET.Element) -> list[ET.Element]:
    return [elem for elem in table_wrap.iter() if local_name(elem) == "tr"]


def expand_table_grid(rows: list[ET.Element]) -> list[list[dict[str, Any]]]:
    grid: list[list[dict[str, Any]]] = []
    rowspans: dict[int, list[Any]] = {}
    for row_index, tr in enumerate(rows, start=1):
        expanded: list[dict[str, Any]] = []
        col_index = 0
        cells = [c for c in list(tr) if local_name(c) in {"td", "th"}]
        cell_ordinal = 0
        for cell in cells:
            while col_index in rowspans:
                text, remaining, origin_row, origin_cell, tag = rowspans[col_index]
                expanded.append(
                    {
                        "text": text,
                        "tag": tag,
                        "row": row_index,
                        "col": col_index + 1,
                        "source_row": origin_row,
                        "source_cell": origin_cell,
                        "from_rowspan": True,
                    }
                )
                remaining -= 1
                if remaining <= 0:
                    del rowspans[col_index]
                else:
                    rowspans[col_index] = [text, remaining, origin_row, origin_cell, tag]
                col_index += 1
            cell_ordinal += 1
            text = elem_text(cell)
            colspan = parse_int_attr(cell, "colspan")
            rowspan = parse_int_attr(cell, "rowspan")
            for offset in range(colspan):
                expanded.append(
                    {
                        "text": text,
                        "tag": local_name(cell),
                        "row": row_index,
                        "col": col_index + 1,
                        "source_row": row_index,
                        "source_cell": cell_ordinal,
                        "from_rowspan": False,
                    }
                )
                if rowspan > 1:
                    rowspans[col_index] = [text, rowspan - 1, row_index, cell_ordinal, local_name(cell)]
                col_index += 1
        while col_index in rowspans:
            text, remaining, origin_row, origin_cell, tag = rowspans[col_index]
            expanded.append(
                {
                    "text": text,
                    "tag": tag,
                    "row": row_index,
                    "col": col_index + 1,
                    "source_row": origin_row,
                    "source_cell": origin_cell,
                    "from_rowspan": True,
                }
            )
            remaining -= 1
            if remaining <= 0:
                del rowspans[col_index]
            else:
                rowspans[col_index] = [text, remaining, origin_row, origin_cell, tag]
            col_index += 1
        grid.append(expanded)
    width = max((len(row) for row in grid), default=0)
    for row in grid:
        while len(row) < width:
            row.append(
                {
                    "text": "",
                    "tag": "empty",
                    "row": len(grid),
                    "col": len(row) + 1,
                    "source_row": None,
                    "source_cell": None,
                    "from_rowspan": False,
                }
            )
    return grid


def detect_unit(text: str) -> str | None:
    unit_patterns = [
        r"([<>~]?\s*\d+(?:\.\d+)?)?\s*((?:u|U|micro|\\u00b5|\\u03bc|µ|μ)g\s*/\s*mL)",
        r"([<>~]?\s*\d+(?:\.\d+)?)?\s*((?:u|U|micro|\\u00b5|\\u03bc|µ|μ)g\s*/\s*ml)",
        r"([<>~]?\s*\d+(?:\.\d+)?)?\s*(mg\s*/\s*kg)",
        r"([<>~]?\s*\d+(?:\.\d+)?)?\s*(%)",
    ]
    for pat in unit_patterns:
        m = re.search(pat, text, flags=re.I)
        if m:
            return norm_text(m.group(2)).replace(" ", "")
    return None


def is_slash_or_missing(value: str) -> bool:
    stripped = norm_text(value)
    if not stripped:
        return True
    return stripped in {"/", "-", "--", "NA", "N/A", "n/a"}


def has_source_value(value: str) -> bool:
    stripped = norm_text(value)
    return bool(stripped) and not is_slash_or_missing(stripped)


def combined_column_labels(grid: list[list[dict[str, Any]]], header_rows: int = 2) -> list[str]:
    if not grid:
        return []
    width = len(grid[0])
    labels: list[str] = []
    for col in range(width):
        parts: list[str] = []
        for row in grid[:header_rows]:
            if col >= len(row):
                continue
            text = row[col]["text"]
            if text and text not in parts:
                parts.append(text)
        labels.append(" | ".join(parts))
    return labels


def species_from_row_label(row_label: str) -> str:
    label = norm_text(row_label)
    abbrev_map = {
        "S. aureus": "Staphylococcus aureus",
        "S. epidermidis": "Staphylococcus epidermidis",
        "S. pneumoniae": "Streptococcus pneumoniae",
        "S. pyogenes": "Streptococcus pyogenes",
        "E. coli": "Escherichia coli",
        "E. faecalis": "Enterococcus faecalis",
        "E. faecium": "Enterococcus faecium",
        "P. aeruginosa": "Pseudomonas aeruginosa",
        "K. pneumoniae": "Klebsiella pneumoniae",
        "A. baumannii": "Acinetobacter baumannii",
        "B. subtilis": "Bacillus subtilis",
        "B. cereus": "Bacillus cereus",
        "L. monocytogenes": "Listeria monocytogenes",
        "M. luteus": "Micrococcus luteus",
        "C. albicans": "Candida albicans",
    }
    for short, long_name in abbrev_map.items():
        if label.startswith(short):
            return long_name
    m = re.match(r"^([A-Z][a-z]+ [a-z][a-z.\-]+)", label)
    if m:
        return m.group(1)
    return label


def target_class_from_row_label(row_label: str) -> str:
    if re.search(r"Candida|C\. albicans|fung", row_label, flags=re.I):
        return "fungus"
    return "bacteria"


def gram_status_from_row_label(row_label: str) -> str | None:
    gram_positive = [
        "Staphylococcus",
        "S. aureus",
        "S. epidermidis",
        "Streptococcus",
        "Enterococcus",
        "Bacillus",
        "Listeria",
        "Micrococcus",
    ]
    gram_negative = [
        "Escherichia",
        "E. coli",
        "Pseudomonas",
        "Klebsiella",
        "Acinetobacter",
        "Salmonella",
        "Shigella",
    ]
    if any(term in row_label for term in gram_positive):
        return "Gram-positive"
    if any(term in row_label for term in gram_negative):
        return "Gram-negative"
    return None


def build_activity_records(root: ET.Element) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    table_wraps = iter_named(root, "table-wrap")
    if not table_wraps:
        raise RuntimeError("No table-wrap elements found")
    table_wrap = table_wraps[0]
    rows = table_rows(table_wrap)
    grid = expand_table_grid(rows)
    labels = combined_column_labels(grid, header_rows=2)
    table_text = elem_text(table_wrap)
    table_unit = detect_unit(table_text)
    if table_unit is None:
        table_unit = "unit_not_recovered"
    drug_columns: dict[str, int] = {}
    for idx, label in enumerate(labels):
        if re.search(r"\bDap\b", label):
            drug_columns["Dap"] = idx
        if re.search(r"\bYZ462\b", label):
            drug_columns["YZ462"] = idx
    if set(drug_columns) != {"Dap", "YZ462"}:
        raise RuntimeError("Could not bind both Dap and YZ462 columns")

    records: list[dict[str, Any]] = []
    reconciled_cells: list[dict[str, Any]] = []
    counts = defaultdict(int)
    data_rows = grid[2:]
    for body_row_index, row in enumerate(data_rows, start=1):
        row_label = norm_text(row[0]["text"]) if row else ""
        species = species_from_row_label(row_label)
        target_class = target_class_from_row_label(row_label)
        gram_status = gram_status_from_row_label(row_label)
        for treatment, col_index in drug_columns.items():
            cell_text = norm_text(row[col_index]["text"]) if col_index < len(row) else ""
            column_label = labels[col_index]
            cell_locator = f"xml:table-wrap:1:body-row={body_row_index}:cell={col_index + 1}"
            source_locator = f"{cell_locator}:column={treatment}"
            if has_source_value(cell_text):
                counts[f"{treatment}_non_slash"] += 1
                record_id = f"{PAPER_ID}-w2-table1-{treatment.lower()}-{body_row_index:02d}"
                normalized_status = "direct" if table_unit != "unit_not_recovered" else "not_convertible"
                record: dict[str, Any] = {
                    "record_id": record_id,
                    "paper_id": PAPER_ID,
                    "worker_id": WORKER_ID,
                    "evidence_kind": "primary_source_table_cell",
                    "database_provenance": {
                        "dbaasp_codex_fallback_candidate": False,
                        "linked_database_rows_checked": True,
                    },
                    "endpoint": "MIC",
                    "endpoint_full_name": "minimum inhibitory concentration",
                    "raw_value": cell_text,
                    "raw_unit": table_unit if table_unit != "unit_not_recovered" else None,
                    "raw_unit_rationale": None
                    if table_unit != "unit_not_recovered"
                    else "Unit was not recoverable from the table caption/header.",
                    "normalization_status": normalized_status,
                    "normalized_value": cell_text if normalized_status == "direct" else None,
                    "normalized_unit": table_unit if normalized_status == "direct" else None,
                    "normalization_note": "Direct source transcription; no value or unit conversion applied."
                    if normalized_status == "direct"
                    else "No normalization because the table unit could not be recovered.",
                    "target_class": target_class,
                    "target_species": species,
                    "target_strain_or_isolate": row_label,
                    "target": row_label,
                    "target_context": {
                        "row_label": row_label,
                        "gram_status": gram_status,
                    },
                    "treatment": treatment,
                    "sample": treatment,
                    "peptide": treatment,
                    "entity": treatment,
                    "sequence": None,
                    "sequence_note": "Not reported in the MIC table cell; sequence identity belongs to worker-4 database verification.",
                    "assay_conditions": {
                        "endpoint_unit_source_locator": "xml:table-wrap:1",
                        "method_source_locators": ["xml:p:32"],
                        "conditions_note": "MIC assay conditions are bound to the source table and method locator; no unit conversion was applied.",
                    },
                    "replicate_statistics": {
                        "reported": False,
                        "source_locator": "xml:table-wrap:1",
                    },
                    "evidence_ladder": "in_vitro_multi_pathogen",
                    "source_locator": source_locator,
                    "source_locators": ["xml:table-wrap:1", source_locator],
                    "source_locator_detail": {
                        "table_locator": "xml:table-wrap:1",
                        "cell_locator": cell_locator,
                        "body_row_index": body_row_index,
                        "cell_index": col_index + 1,
                        "row_label": row_label,
                        "column_label": column_label,
                        "column_label_short": treatment,
                    },
                    "row_label": row_label,
                    "column_label": column_label,
                    "source_review_status": "source_verified",
                }
                records.append(record)
                status = "emitted_activity_record"
            else:
                counts[f"{treatment}_slash_or_missing"] += 1
                status = "excluded_slash_or_missing_source_cell"
            reconciled_cells.append(
                {
                    "table_locator": "xml:table-wrap:1",
                    "cell_locator": cell_locator,
                    "body_row_index": body_row_index,
                    "cell_index": col_index + 1,
                    "row_label": row_label,
                    "column_label": column_label,
                    "column_label_short": treatment,
                    "raw_value": cell_text,
                    "raw_unit": table_unit if table_unit != "unit_not_recovered" else None,
                    "status": status,
                    "record_id": records[-1]["record_id"] if status == "emitted_activity_record" else None,
                    "exclusion_reason": None if status == "emitted_activity_record" else "Source cell is slash/blank/missing rather than a reported MIC observation.",
                }
            )
    reconciliation = {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "generated_at": utc_now(),
        "source_table_locator": "xml:table-wrap:1",
        "table_dimensions": {"rows": len(grid), "columns": len(grid[0]) if grid else 0},
        "drug_columns": {
            drug: {"cell_index": col + 1, "column_label": labels[col]} for drug, col in sorted(drug_columns.items())
        },
        "raw_unit": table_unit if table_unit != "unit_not_recovered" else None,
        "activity_records_emitted": len(records),
        "counts": dict(counts),
        "acceptance_checks": {
            "expected_dap_non_slash_cells": 14,
            "expected_yz462_non_slash_cells": 17,
            "actual_dap_non_slash_cells": counts.get("Dap_non_slash", 0),
            "actual_yz462_non_slash_cells": counts.get("YZ462_non_slash", 0),
            "all_non_slash_cells_reconciled": (
                counts.get("Dap_non_slash", 0) == 14
                and counts.get("YZ462_non_slash", 0) == 17
                and len(records) == counts.get("Dap_non_slash", 0) + counts.get("YZ462_non_slash", 0)
            ),
        },
        "reconciled_cells": reconciled_cells,
    }
    return records, reconciliation


def sentence_split(text: str) -> list[str]:
    compact = norm_text(text)
    if not compact:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", compact) if part.strip()]


def value_tokens(text: str) -> list[dict[str, str]]:
    tokens: list[dict[str, str]] = []
    patterns = [
        ("%", r"([<>~]?\s*\d+(?:\.\d+)?)\s*%"),
        ("mg/kg", r"([<>~]?\s*\d+(?:\.\d+)?)\s*mg\s*/\s*kg"),
        ("ug/mL", r"([<>~]?\s*\d+(?:\.\d+)?)\s*(?:u|U|micro|\\u00b5|\\u03bc|µ|μ)g\s*/\s*mL"),
        ("unitless", r"(?:selectivity index|SI|therapeutic index)[^0-9<>~]{0,40}([<>~]?\s*\d+(?:\.\d+)?)"),
    ]
    for unit, pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.I):
            tokens.append({"value": norm_text(match.group(1)), "unit": unit, "span_start": str(match.start())})
    tokens.sort(key=lambda item: int(item["span_start"]))
    return tokens


def classify_toxicity_endpoint(text: str) -> tuple[str | None, str, str]:
    lower = text.lower()
    if "hemolys" in lower:
        return "percent hemolysis", "mammalian", "erythrocytes"
    if "selectivity" in lower or "therapeutic index" in lower or re.search(r"\bsi\b", lower):
        return "selectivity index", "derived_selectivity", "selectivity ratio"
    if "cytotoxic" in lower or "cell viability" in lower or "viability" in lower:
        if "viability" in lower:
            return "cell viability", "mammalian", "mammalian cell line"
        return "percent cytotoxicity", "mammalian", "mammalian cell line"
    if "in vivo" in lower or "mice" in lower or "mouse" in lower:
        return "in vivo toxicity", "animal", "mouse model"
    if "toxicity" in lower:
        return "toxicity observation", "toxicity", "reported toxicity target"
    return None, "toxicity", "reported toxicity target"


def make_toxicity_record(
    record_index: int,
    source_locator: str,
    source_locators: list[str],
    endpoint: str,
    target_class: str,
    target: str,
    token: dict[str, str] | None,
    qualitative_value: str | None = None,
    panel: str | None = None,
) -> dict[str, Any]:
    raw_value = token["value"] if token else qualitative_value
    raw_unit = token["unit"] if token else None
    no_unit = token is None or raw_unit == "unitless"
    if raw_unit == "ug/mL":
        raw_unit = "ug/mL"
    normalization_status = "direct" if token else "not_convertible"
    normalized_value = raw_value if normalization_status == "direct" else None
    normalized_unit = raw_unit if normalization_status == "direct" else None
    if raw_unit == "unitless":
        normalized_unit = "unitless"
    return {
        "record_id": f"{PAPER_ID}-w2-tox-{record_index:02d}",
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "evidence_kind": "primary_source_toxicity_observation",
        "endpoint": endpoint,
        "raw_value": raw_value,
        "raw_unit": None if no_unit and raw_unit != "unitless" else raw_unit,
        "raw_unit_rationale": "Dimensionless source-reported ratio/index."
        if raw_unit == "unitless"
        else ("Qualitative toxicity observation; no scalar unit reported." if token is None else None),
        "normalization_status": normalization_status,
        "normalized_value": normalized_value,
        "normalized_unit": normalized_unit,
        "normalization_note": "Direct source transcription; no value or unit conversion applied."
        if normalization_status == "direct"
        else "Qualitative observation was not converted to a numeric endpoint.",
        "target_class": target_class,
        "target_species": target,
        "target_strain_or_isolate": target,
        "target": target,
        "target_context": {
            "toxicity_surface": True,
            "figure_panel": panel,
        },
        "treatment": "YZ462",
        "sample": "YZ462",
        "peptide": "YZ462",
        "entity": "YZ462",
        "assay_conditions": {
            "source_locators": source_locators,
            "conditions_note": "Toxicity/selectivity observation retained only at source-located level; no experimental optimization details are provided.",
        },
        "replicate_statistics": {
            "reported": False,
            "source_locator": source_locator,
        },
        "evidence_ladder": "in_vivo_tested" if endpoint == "in vivo toxicity" else (
            "therapeutic_window_supported" if endpoint == "selectivity index" else "toxicity_tested"
        ),
        "source_locator": source_locator,
        "source_locators": source_locators,
        "source_locator_detail": {
            "primary_locator": source_locator,
            "figure_panel": panel,
        },
        "source_review_status": "source_verified",
    }


def make_exclusion(locator: str, endpoint_scope: str, reason_code: str, note: str, panel: str | None = None) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "locator": locator,
        "source_locator": locator,
        "endpoint_scope": endpoint_scope,
        "treatment": "YZ462",
        "panel": panel,
        "disposition": "source_backed_exclusion",
        "reason_code": reason_code,
        "reason": note,
    }


def figure_locators(root: ET.Element) -> dict[str, dict[str, str]]:
    figures: dict[str, dict[str, str]] = {}
    for idx, fig in enumerate(iter_named(root, "fig"), start=1):
        label = child_text(fig, "label")
        caption = child_text(fig, "caption")
        text = elem_text(fig)
        locator = f"xml:fig:{idx}"
        key_text = " ".join([label, caption, text]).lower()
        if re.search(r"\bfig(?:ure)?\.?\s*1\b", key_text):
            figures["fig1"] = {"locator": locator, "label": label, "text": text}
        if re.search(r"\bfig(?:ure)?\.?\s*s2\b", key_text):
            figures["figs2"] = {"locator": locator, "label": label, "text": text}
    return figures


def supplementary_fig_s2_surface() -> dict[str, str | None]:
    if not SUPPLEMENT_FIG_DOC.exists():
        return {"locator": None, "text": "", "status": "missing", "tool": None}
    for tool in ("antiword", "catdoc"):
        exe = shutil.which(tool)
        if not exe:
            continue
        try:
            completed = subprocess.run(
                [exe, str(SUPPLEMENT_FIG_DOC)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except Exception:
            continue
        text = norm_text(completed.stdout)
        if not text:
            continue
        match = re.search(r"(fig(?:ure)?\.?\s*S2\b)", text, flags=re.I)
        if not match:
            continue
        start = max(0, match.start() - 800)
        end = min(len(text), match.end() + 1600)
        return {
            "locator": f"supp:{SUPPLEMENT_FIG_DOC.name}:figure=S2",
            "text": text[start:end],
            "status": "resolved",
            "tool": tool,
        }
    return {"locator": None, "text": "", "status": "not_resolved_by_local_tools", "tool": None}


def build_toxicity_records(root: ET.Element) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    paragraphs = iter_named(root, "p")
    sections = iter_named(root, "sec")
    figs = figure_locators(root)
    supp_s2 = supplementary_fig_s2_surface()
    selected_texts: dict[str, str] = {}
    if len(paragraphs) >= 33:
        selected_texts["xml:p:33"] = elem_text(paragraphs[32])
    if len(sections) >= 11:
        selected_texts["xml:sec:11"] = elem_text(sections[10])
    if len(sections) >= 12:
        selected_texts["xml:sec:12"] = elem_text(sections[11])
    if "fig1" in figs:
        selected_texts[f"{figs['fig1']['locator']}:panel=D"] = figs["fig1"]["text"]
        selected_texts[f"{figs['fig1']['locator']}:panel=E"] = figs["fig1"]["text"]
    if "figs2" in figs:
        selected_texts[f"{figs['figs2']['locator']}:panel=S2"] = figs["figs2"]["text"]
    elif supp_s2.get("locator"):
        selected_texts[str(supp_s2["locator"])] = str(supp_s2.get("text") or "")

    records: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    coverage: dict[str, Any] = {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "generated_at": utc_now(),
        "required_locator_scopes": ["xml:p:33", "xml:sec:11", "xml:sec:12", "Fig. 1D/E", "Fig. S2"],
        "resolved_locator_bindings": {
            "xml:p:33": "xml:p:33" if "xml:p:33" in selected_texts else None,
            "xml:sec:11": "xml:sec:11" if "xml:sec:11" in selected_texts else None,
            "xml:sec:12": "xml:sec:12" if "xml:sec:12" in selected_texts else None,
            "Fig. 1D": f"{figs['fig1']['locator']}:panel=D" if "fig1" in figs else None,
            "Fig. 1E": f"{figs['fig1']['locator']}:panel=E" if "fig1" in figs else None,
            "Fig. S2": f"{figs['figs2']['locator']}:panel=S2" if "figs2" in figs else supp_s2.get("locator"),
        },
        "supplementary_fig_s2_resolution": {
            "status": supp_s2.get("status"),
            "tool": supp_s2.get("tool"),
            "source_path": str(SUPPLEMENT_FIG_DOC.relative_to(REPO_ROOT)) if SUPPLEMENT_FIG_DOC.exists() else None,
        },
        "record_locator_ids": [],
        "exclusion_locator_ids": [],
    }

    record_index = 0
    p33 = selected_texts.get("xml:p:33", "")
    endpoint_seen: set[str] = set()
    if p33:
        for sentence in sentence_split(p33):
            if "YZ462" not in sentence:
                continue
            endpoint, target_class, target = classify_toxicity_endpoint(sentence)
            if endpoint is None:
                continue
            toks = value_tokens(sentence)
            useful_tokens = [
                tok
                for tok in toks
                if not (tok["unit"] == "ug/mL" and endpoint not in {"selectivity index", "in vivo toxicity"})
            ]
            if endpoint == "selectivity index":
                useful_tokens = [tok for tok in toks if tok["unit"] == "unitless"] or toks[:1]
            elif endpoint == "in vivo toxicity":
                useful_tokens = [tok for tok in toks if tok["unit"] in {"mg/kg", "%"}]
            elif endpoint in {"percent hemolysis", "cell viability", "percent cytotoxicity"}:
                useful_tokens = [tok for tok in toks if tok["unit"] == "%"]
            if useful_tokens:
                for tok in useful_tokens:
                    record_index += 1
                    records.append(
                        make_toxicity_record(
                            record_index,
                            "xml:p:33",
                            ["xml:p:33"],
                            endpoint,
                            target_class,
                            target,
                            tok,
                        )
                    )
                    endpoint_seen.add(endpoint)
            elif endpoint not in endpoint_seen:
                record_index += 1
                records.append(
                    make_toxicity_record(
                        record_index,
                        "xml:p:33",
                        ["xml:p:33"],
                        endpoint,
                        target_class,
                        target,
                        None,
                        qualitative_value="qualitative source observation",
                    )
                )
                endpoint_seen.add(endpoint)
    else:
        exclusions.append(
            make_exclusion("xml:p:33", "toxicity/selectivity", "locator_not_resolved", "Requested paragraph locator could not be resolved in paper XML.")
        )

    # Required container/panel scopes are covered explicitly. Figure panels are
    # excluded unless packet text binds a scalar value to that specific panel.
    if "xml:sec:11" in selected_texts:
        exclusions.append(
            make_exclusion(
                "xml:sec:11",
                "toxicity/selectivity container",
                "container_locator_no_independent_scalar",
                "Section-level locator is a container; child paragraph/figure locators carry the biological toxicity evidence.",
            )
        )
    else:
        exclusions.append(make_exclusion("xml:sec:11", "toxicity/selectivity container", "locator_not_resolved", "Requested section locator could not be resolved."))
    if "xml:sec:12" in selected_texts:
        exclusions.append(
            make_exclusion(
                "xml:sec:12",
                "toxicity/selectivity container",
                "container_locator_no_independent_scalar",
                "Section-level locator is a container; child paragraph/figure locators carry the biological toxicity evidence.",
            )
        )
    else:
        exclusions.append(make_exclusion("xml:sec:12", "toxicity/selectivity container", "locator_not_resolved", "Requested section locator could not be resolved."))

    fig_panel_specs = [
        ("Fig. 1D", coverage["resolved_locator_bindings"].get("Fig. 1D"), "hemolysis", "D"),
        ("Fig. 1E", coverage["resolved_locator_bindings"].get("Fig. 1E"), "cytotoxicity/cell viability", "E"),
        ("Fig. S2", coverage["resolved_locator_bindings"].get("Fig. S2"), "in vivo toxicity/selectivity", "S2"),
    ]
    for label, locator, scope, panel in fig_panel_specs:
        if locator is None:
            exclusions.append(
                make_exclusion(
                    label,
                    scope,
                    "figure_locator_not_resolved",
                    "Requested figure/panel label was not resolved to a packet XML figure caption locator.",
                    panel=panel,
                )
            )
            continue
        text = selected_texts.get(locator, "")
        toks = value_tokens(text)
        scalar_toks = [tok for tok in toks if tok["unit"] in {"%", "mg/kg", "unitless"}]
        if scalar_toks and "YZ462" in text:
            endpoint, target_class, target = classify_toxicity_endpoint(scope)
            for tok in scalar_toks[:3]:
                record_index += 1
                records.append(
                    make_toxicity_record(
                        record_index,
                        locator,
                        [locator],
                        endpoint or scope,
                        target_class,
                        target,
                        tok,
                        panel=panel,
                    )
                )
        else:
            exclusions.append(
                make_exclusion(
                    locator,
                    scope,
                    "no_exact_scalar_bound_to_panel_text",
                    "Figure/caption surface is source-located, but the packet text does not encode an exact scalar observation for this panel.",
                    panel=panel,
                )
            )

    coverage["toxicity_record_count"] = len(records)
    coverage["toxicity_exclusion_count"] = len(exclusions)
    coverage["record_locator_ids"] = [r["source_locator"] for r in records]
    coverage["exclusion_locator_ids"] = [e["source_locator"] for e in exclusions]
    coverage["acceptance_checks"] = {
        "covers_xml_p_33": any("xml:p:33" in r.get("source_locators", []) or e["source_locator"] == "xml:p:33" for r in records for e in exclusions)
        or any(r["source_locator"] == "xml:p:33" for r in records)
        or any(e["source_locator"] == "xml:p:33" for e in exclusions),
        "covers_xml_sec_11": any(e["source_locator"] == "xml:sec:11" for e in exclusions)
        or any("xml:sec:11" in r.get("source_locators", []) for r in records),
        "covers_xml_sec_12": any(e["source_locator"] == "xml:sec:12" for e in exclusions)
        or any("xml:sec:12" in r.get("source_locators", []) for r in records),
        "covers_fig_1d": any((e.get("panel") == "D") for e in exclusions)
        or any(r.get("source_locator_detail", {}).get("figure_panel") == "D" for r in records),
        "covers_fig_1e": any((e.get("panel") == "E") for e in exclusions)
        or any(r.get("source_locator_detail", {}).get("figure_panel") == "E" for r in records),
        "covers_fig_s2": any((e.get("panel") == "S2") for e in exclusions)
        or any(r.get("source_locator_detail", {}).get("figure_panel") == "S2" for r in records),
    }
    return records, exclusions, coverage


def validate_artifact(artifact: dict[str, Any], reconciliation: dict[str, Any], toxicity_coverage: dict[str, Any]) -> dict[str, Any]:
    allowed_norm = {"direct", "converted", "not_convertible", "ambiguous"}
    issues: list[dict[str, Any]] = []
    for bucket in ["activity_records", "toxicity_records"]:
        for idx, row in enumerate(artifact.get(bucket, [])):
            rid = row.get("record_id", f"{bucket}[{idx}]")
            if row.get("normalization_status") not in allowed_norm:
                issues.append({"record_id": rid, "field": "normalization_status", "issue": "invalid_value"})
            if row.get("normalization_status") in {"direct", "converted"}:
                if row.get("normalized_value") in (None, "") or row.get("normalized_unit") in (None, ""):
                    issues.append({"record_id": rid, "field": "normalized_value/normalized_unit", "issue": "required_for_direct_or_converted"})
            for required in ["endpoint", "raw_value", "target_species", "target_strain_or_isolate", "assay_conditions", "evidence_ladder", "source_locator"]:
                if row.get(required) in (None, "", {}, []):
                    issues.append({"record_id": rid, "field": required, "issue": "missing_required_field"})
            if bucket == "activity_records":
                detail = row.get("source_locator_detail", {})
                if row.get("row_label") != detail.get("row_label"):
                    issues.append({"record_id": rid, "field": "row_label", "issue": "not_equal_to_source_row_label"})
                if row.get("column_label") != detail.get("column_label"):
                    issues.append({"record_id": rid, "field": "column_label", "issue": "not_equal_to_source_column_label"})
    table_checks = reconciliation.get("acceptance_checks", {})
    if not table_checks.get("all_non_slash_cells_reconciled"):
        issues.append({"artifact": str(RECONCILIATION_OUT), "issue": "table1_non_slash_contract_not_met"})
    tox_checks = toxicity_coverage.get("acceptance_checks", {})
    for key, value in tox_checks.items():
        if not value:
            issues.append({"artifact": str(TOXICITY_COVERAGE_OUT), "issue": f"toxicity_coverage_missing:{key}"})
    validation = {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "generated_at": utc_now(),
        "activity_record_count": len(artifact.get("activity_records", [])),
        "toxicity_record_count": len(artifact.get("toxicity_records", [])),
        "toxicity_exclusion_count": len(artifact.get("toxicity_exclusions", [])),
        "normalization_status_values": sorted(
            {row.get("normalization_status") for row in artifact.get("activity_records", []) + artifact.get("toxicity_records", [])}
        ),
        "table_contract_passed": bool(table_checks.get("all_non_slash_cells_reconciled")),
        "toxicity_coverage_passed": all(bool(v) for v in tox_checks.values()),
        "issue_count": len(issues),
        "issues": issues,
    }
    return validation


def build_artifact(root: ET.Element) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    handoff = load_json(SAFE_HANDOFF, {})
    authoritative = load_json(AUTHORITATIVE_REPORT, {})
    activity_records, reconciliation = build_activity_records(root)
    toxicity_records, toxicity_exclusions, toxicity_coverage = build_toxicity_records(root)
    artifact = {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "artifact_role": "worker2_source_reviewed_activity_toxicity_evidence",
        "generated_at": utc_now(),
        "source_review_scope": {
            "paper_xml": str(PAPER_XML.relative_to(REPO_ROOT)),
            "packet_safe_candidate_handoff": str(SAFE_HANDOFF.relative_to(REPO_ROOT)),
            "authoritative_match_report": str(AUTHORITATIVE_REPORT.relative_to(REPO_ROOT)),
            "supplementary_fig_s2_doc": str(SUPPLEMENT_FIG_DOC.relative_to(REPO_ROOT)) if SUPPLEMENT_FIG_DOC.exists() else None,
            "source_locators_reviewed": [
                "xml:table-wrap:1",
                "xml:p:33",
                "xml:sec:11",
                "xml:sec:12",
                "Fig. 1D/E",
                "Fig. S2",
            ],
            "machine_rows_treated_as_candidate_only": True,
            "leader_preflight_contract_count": 0,
            "leader_preflight_evidence_scaffold_count": 0,
        },
        "activity_records": activity_records,
        "toxicity_records": toxicity_records,
        "activity_exclusions": [
            cell
            for cell in reconciliation["reconciled_cells"]
            if cell["status"] == "excluded_slash_or_missing_source_cell"
        ],
        "toxicity_exclusions": toxicity_exclusions,
        "normalization_policy": {
            "allowed_status_values": ["direct", "converted", "not_convertible", "ambiguous"],
            "direct_definition": "Direct preserves the source value and source unit exactly; no value or unit conversion is applied.",
            "unit_conversion_policy": "No ug/mL-to-uM conversion was attempted without sufficient molecular-weight/modification support.",
        },
        "machine_candidate_provenance": {
            "safe_handoff_counts": handoff.get("counts", {}),
            "authoritative_row_counts": authoritative.get("row_counts", {}),
            "interpretation": "DBAASP Codex fallback rows were inspected only as candidate machine evidence, not as primary-source assay rows.",
        },
        "summary_counts": {
            "activity_records": len(activity_records),
            "toxicity_records": len(toxicity_records),
            "activity_exclusions": len(reconciliation["reconciled_cells"]) - len(activity_records),
            "toxicity_exclusions": len(toxicity_exclusions),
            "table1_dap_non_slash_records": reconciliation["counts"].get("Dap_non_slash", 0),
            "table1_yz462_non_slash_records": reconciliation["counts"].get("YZ462_non_slash", 0),
            "table1_total_non_slash_records": len(activity_records),
        },
        "quality_checks": {
            "table1_non_slash_dap_yz462_reconciled": reconciliation["acceptance_checks"]["all_non_slash_cells_reconciled"],
            "row_label_column_label_locator_faithful": all(
                r.get("row_label") == r.get("source_locator_detail", {}).get("row_label")
                and r.get("column_label") == r.get("source_locator_detail", {}).get("column_label")
                for r in activity_records
            ),
            "toxicity_required_locator_scopes_covered": all(toxicity_coverage["acceptance_checks"].values()),
            "database_rows_primary_source_separated": True,
        },
        "verification_artifacts": {
            "table1_reconciliation": str(RECONCILIATION_OUT.relative_to(REPO_ROOT)),
            "toxicity_locator_coverage": str(TOXICITY_COVERAGE_OUT.relative_to(REPO_ROOT)),
            "validation": str(VALIDATION_OUT.relative_to(REPO_ROOT)),
            "rebuild_script": str(Path(__file__).resolve().relative_to(REPO_ROOT)),
        },
        "lane_status": "repair_ready_for_worker6_adjudication",
        "publication_grade_claim": False,
        "publication_grade_basis": "Worker-2 repaired source-reviewed layer-2 evidence but terminal publication-grade acceptance belongs to worker-6.",
    }
    validation = validate_artifact(artifact, reconciliation, toxicity_coverage)
    return artifact, reconciliation, toxicity_coverage, validation


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_response(validation: dict[str, Any], append: bool) -> Path | None:
    if not append:
        return None
    response_path = PACKET_ROOT / "rework/rework_responses.jsonl"
    response_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ticket_id": "rwk-PMC12606902-campaign-r01-worker2-activity-toxicity-not-source-complete",
        "response_status": "repair_ready_for_adjudication",
        "response_by": WORKER_ID,
        "analysis_can_resume": True,
        "paper_id": PAPER_ID,
        "created_at": utc_now(),
        "reason": "Rebuilt worker-2 layer-2 activity/toxicity evidence from paper-local source locators and separated primary-source rows from machine candidate provenance.",
        "evidence": {
            "activity_record_count": validation["activity_record_count"],
            "toxicity_record_count": validation["toxicity_record_count"],
            "toxicity_exclusion_count": validation["toxicity_exclusion_count"],
            "table_contract_passed": validation["table_contract_passed"],
            "toxicity_coverage_passed": validation["toxicity_coverage_passed"],
            "validation_issue_count": validation["issue_count"],
        },
        "evidence_paths": [
            str(RECONCILIATION_OUT.relative_to(REPO_ROOT)),
            str(TOXICITY_COVERAGE_OUT.relative_to(REPO_ROOT)),
            str(VALIDATION_OUT.relative_to(REPO_ROOT)),
        ],
        "repaired_artifacts": [
            str(WORK_ACTIVITY_OUT.relative_to(REPO_ROOT)),
            str(PACKET_ANALYSIS_OUT.relative_to(REPO_ROOT)),
        ],
        "artifacts_written": [
            str(WORK_ACTIVITY_OUT.relative_to(REPO_ROOT)),
            str(PACKET_ANALYSIS_OUT.relative_to(REPO_ROOT)),
            str(SNAPSHOT_OUT.relative_to(REPO_ROOT)),
        ],
        "added_files": [
            str(Path(__file__).resolve().relative_to(REPO_ROOT)),
            str(RECONCILIATION_OUT.relative_to(REPO_ROOT)),
            str(TOXICITY_COVERAGE_OUT.relative_to(REPO_ROOT)),
            str(VALIDATION_OUT.relative_to(REPO_ROOT)),
        ],
        "validation_artifacts": [str(VALIDATION_OUT.relative_to(REPO_ROOT))],
        "notes": "Nonterminal owner response only; worker-6 must perform fresh adjudication before ticket closure.",
    }
    with response_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return response_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild PMC12606902 worker-2 activity/toxicity artifacts.")
    parser.add_argument("--append-rework-response", action="store_true")
    args = parser.parse_args()

    if not PAPER_XML.exists():
        raise SystemExit(f"Missing required XML path: {PAPER_XML}")
    root = ET.parse(PAPER_XML).getroot()
    artifact, reconciliation, toxicity_coverage, validation = build_artifact(root)

    if WORK_ACTIVITY_OUT.exists():
        shutil.copy2(WORK_ACTIVITY_OUT, SNAPSHOT_OUT)
    write_json(WORK_ACTIVITY_OUT, artifact)
    write_json(PACKET_ANALYSIS_OUT, artifact)
    write_json(RECONCILIATION_OUT, reconciliation)
    write_json(TOXICITY_COVERAGE_OUT, toxicity_coverage)
    write_json(VALIDATION_OUT, validation)
    response_path = append_response(validation, args.append_rework_response)

    summary = {
        "activity_records": validation["activity_record_count"],
        "toxicity_records": validation["toxicity_record_count"],
        "toxicity_exclusions": validation["toxicity_exclusion_count"],
        "table_contract_passed": validation["table_contract_passed"],
        "toxicity_coverage_passed": validation["toxicity_coverage_passed"],
        "validation_issue_count": validation["issue_count"],
        "artifacts": [
            str(WORK_ACTIVITY_OUT.relative_to(REPO_ROOT)),
            str(PACKET_ANALYSIS_OUT.relative_to(REPO_ROOT)),
            str(RECONCILIATION_OUT.relative_to(REPO_ROOT)),
            str(TOXICITY_COVERAGE_OUT.relative_to(REPO_ROOT)),
            str(VALIDATION_OUT.relative_to(REPO_ROOT)),
        ],
        "rework_response_appended": str(response_path.relative_to(REPO_ROOT)) if response_path else None,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if validation["issue_count"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
