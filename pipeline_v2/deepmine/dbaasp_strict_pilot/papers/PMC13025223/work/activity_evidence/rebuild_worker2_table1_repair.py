#!/usr/bin/env python3
import copy
import datetime as dt
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path("/home/cihebi/抗菌肽/数据集/batch/5-team")
PAPER_ID = "PMC13025223"
PACKET = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot/packets" / PAPER_ID
PAPER = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot/papers" / PAPER_ID
WORK = PAPER / "work/activity_evidence"
XML_PATH = PAPER / "source/paper.xml"
WORK_ACTIVITY = WORK / "activity_records.json"
PACKET_ACTIVITY = PACKET / "analysis/activity_toxicity_evidence.worker2.json"
PAPER_FINAL = PAPER / "final/activity_toxicity_evidence.json"
PACKET_FINAL = PACKET / "final/activity_toxicity_evidence.json"
REWORK_RESPONSES = PACKET / "rework/rework_responses.jsonl"
TICKET_ID = "rwk-PMC13025223-campaign-r03-BF-PMC13025223-W2-001-target-and-toxicity-field-integrity"
FIGURE6_LOCATOR = "pdf:page=9:figure=Figure 6"
FIGURE6_DIGITIZATION = WORK / "figure6_digitization/figure6_approximate_graph_values.worker2.json"

FIGURE6_GRAPH_VALUES = [
    {
        "series": "lysin",
        "treatment": "lysin",
        "concentration": "0.0005",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "lysin",
        "treatment": "lysin",
        "concentration": "0.001",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "lysin",
        "treatment": "lysin",
        "concentration": "0.002",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "lysin",
        "treatment": "lysin",
        "concentration": "0.004",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "lysin",
        "treatment": "lysin",
        "concentration": "0.008",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "lysin",
        "treatment": "lysin",
        "concentration": "0.016",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "lysin",
        "treatment": "lysin",
        "concentration": "0.032",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "19",
        "raw_value": "19",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "lysin",
        "treatment": "lysin",
        "concentration": "0.064",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "27",
        "raw_value": "27",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "PBS",
        "treatment": "PBS",
        "concentration": "0.0005",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "PBS",
        "treatment": "PBS",
        "concentration": "0.001",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "2",
        "raw_value": "2",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "PBS",
        "treatment": "PBS",
        "concentration": "0.002",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "PBS",
        "treatment": "PBS",
        "concentration": "0.004",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "PBS",
        "treatment": "PBS",
        "concentration": "0.008",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "PBS",
        "treatment": "PBS",
        "concentration": "0.016",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "PBS",
        "treatment": "PBS",
        "concentration": "0.032",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "0",
        "raw_value": "0",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
    {
        "series": "PBS",
        "treatment": "PBS",
        "concentration": "0.064",
        "concentration_unit": "mg/mL",
        "percent_toxicity": "1",
        "raw_value": "1",
        "raw_unit": "%",
        "exactness_status": "approximate_graph_digitized",
        "source_locator": FIGURE6_LOCATOR,
    },
]


def lname(tag):
    return tag.rsplit("}", 1)[-1]


def clean(value):
    return " ".join((value or "").split())


def text_of(elem):
    return clean("".join(elem.itertext())) if elem is not None else ""


def direct_children(elem, names):
    return [child for child in list(elem) if lname(child.tag) in names]


def descendants(elem, name):
    return [child for child in elem.iter() if lname(child.tag) == name]


def norm_unit(value):
    value = clean(value).replace("μ", "u").replace("µ", "u")
    value = re.sub(r"\s*/\s*", "/", value)
    value = re.sub(r"\s+", " ", value)
    if re.search(r"\bug\s*/\s*mL\b", value, re.I):
        return "ug/mL"
    if re.search(r"\bmg\s*/\s*mL\b", value, re.I):
        return "mg/mL"
    if re.search(r"\buM\b", value):
        return "uM"
    return None


def find_unit(*values):
    for value in values:
        unit = norm_unit(value or "")
        if unit:
            return unit
    return None


def value_status(raw):
    raw_clean = clean(raw)
    if re.fullmatch(r"(?:ND|N\.D\.|not\s+detected|not\s+determined)", raw_clean, re.I):
        return "ND_not_numeric"
    if re.match(r"^(?:[<>]=?|<=|>=|≤|≥)?\s*\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?", raw_clean):
        return "exact_quantitative"
    if raw_clean in {"-", "NA", "N/A", ""}:
        return "blank_or_not_applicable"
    return "ambiguous_source_code"


def normalize_value(raw):
    raw_clean = clean(raw)
    raw_clean = raw_clean.replace("≤", "<=").replace("≥", ">=")
    m = re.match(r"^((?:[<>]=?|<=|>=)?\s*\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?)", raw_clean)
    if m:
        return re.sub(r"\s+", "", m.group(1)).replace("–", "-")
    return re.sub(r"\s+", "", raw_clean)


ORGANISMS = [
    ("Enterococcus faecium", "bacteria", "Gram-positive"),
    ("Staphylococcus aureus", "bacteria", "Gram-positive"),
    ("Klebsiella pneumoniae", "bacteria", "Gram-negative"),
    ("Acinetobacter baumannii", "bacteria", "Gram-negative"),
    ("Pseudomonas aeruginosa", "bacteria", "Gram-negative"),
    ("Enterobacter cloacae", "bacteria", "Gram-negative"),
    ("Escherichia coli", "bacteria", "Gram-negative"),
]

ABBREVIATED_ORGANISMS = {
    "E. faecium": ("Enterococcus faecium", "bacteria", "Gram-positive"),
    "S. aureus": ("Staphylococcus aureus", "bacteria", "Gram-positive"),
    "K. pneumoniae": ("Klebsiella pneumoniae", "bacteria", "Gram-negative"),
    "A. baumannii": ("Acinetobacter baumannii", "bacteria", "Gram-negative"),
    "P. aeruginosa": ("Pseudomonas aeruginosa", "bacteria", "Gram-negative"),
    "E. cloacae": ("Enterobacter cloacae", "bacteria", "Gram-negative"),
    "E. coli": ("Escherichia coli", "bacteria", "Gram-negative"),
}


def species_from_text(value):
    hay = clean(value)
    if re.search(r"\bESCCO\s+ATCC\s*25922\b", hay, re.I):
        return "ESCCO ATCC 25922", "ATCC 25922", "bacteria", None
    for species, klass, gram in ORGANISMS:
        if re.search(re.escape(species), hay, re.I):
            strain = None
            tail = hay[hay.lower().find(species.lower()) + len(species) :]
            m = re.search(r"\b(?:(?:ATCC|DSM|MTCC|NCTC|KCTC|CCUG)\s*[-A-Za-z0-9]+|BAA\s*[-A-Za-z0-9]+)", tail)
            if m:
                strain = clean(m.group(0)).replace(" ", "") if not re.match(r"BAA\\s*", m.group(0), re.I) else clean(m.group(0)).replace(" ", "")
            return species, strain, klass, gram
    for abbrev, (species, klass, gram) in ABBREVIATED_ORGANISMS.items():
        if re.search(re.escape(abbrev), hay, re.I):
            strain = None
            tail = hay[hay.lower().find(abbrev.lower()) + len(abbrev) :]
            m = re.search(r"\b(?:ATCC|DSM|MTCC|NCTC|KCTC|CCUG)\s*[-A-Za-z0-9]+", tail)
            if m:
                strain = clean(m.group(0)).replace(" ", "")
            return species, strain, klass, gram
    if re.search(r"\bMRSA\b|methicillin[- ]resistant", hay, re.I):
        m = re.search(r"\b(?:ATCC|DSM|MTCC|NCTC|KCTC|CCUG)\s*[-A-Za-z0-9]+", hay)
        strain = ("MRSA " + clean(m.group(0)).replace(" ", "")) if m else "MRSA"
        return "Staphylococcus aureus", strain, "bacteria", "Gram-positive"
    if re.search(r"\bATCC\s*25922\b", hay, re.I):
        return "Escherichia coli", "ATCC25922", "bacteria", "Gram-negative"
    generic = re.search(
        r"\b([A-Z][a-z]+)\s+([a-z][a-z-]+)(?:\s+[a-z][a-z-]+)?\s+((?:ATCC|DSM|MTCC|NCTC|KCTC|CCUG)\s*[-A-Za-z0-9]+)",
        hay,
    )
    if generic:
        return f"{generic.group(1)} {generic.group(2)}", clean(generic.group(3)).replace(" ", ""), "bacteria", None
    return None, None, None, None


def target_class(species):
    return next((klass for sp, klass, _ in ORGANISMS if sp == species), "bacteria")


def gram_status(species):
    return next((gram for sp, _, gram in ORGANISMS if sp == species), None)


def get_table_wrap_one():
    root = ET.parse(XML_PATH).getroot()
    wraps = [node for node in root.iter() if lname(node.tag) == "table-wrap"]
    if not wraps:
        raise RuntimeError("no table-wrap elements found")
    return wraps[0], root


def build_rows(row_elems, row_kind):
    active = {}
    out = []
    for row_idx, tr in enumerate(row_elems, start=1):
        row = []
        col = 1
        while col in active:
            carry = copy.deepcopy(active[col]["cell"])
            carry["inherited"] = True
            carry["row"] = row_idx
            carry["col"] = col
            row.append(carry)
            active[col]["remaining"] -= 1
            if active[col]["remaining"] <= 0:
                del active[col]
            col += 1
        physical_cell = 0
        for cell in direct_children(tr, {"td", "th"}):
            while col in active:
                carry = copy.deepcopy(active[col]["cell"])
                carry["inherited"] = True
                carry["row"] = row_idx
                carry["col"] = col
                row.append(carry)
                active[col]["remaining"] -= 1
                if active[col]["remaining"] <= 0:
                    del active[col]
                col += 1
            physical_cell += 1
            rowspan = int(cell.get("rowspan") or "1")
            colspan = int(cell.get("colspan") or "1")
            base = {
                "text": text_of(cell),
                "row": row_idx,
                "col": col,
                "physical_cell": physical_cell,
                "rowspan": rowspan,
                "colspan": colspan,
                "inherited": False,
                "locator": f"xml:table-wrap:1:{row_kind}-row={row_idx}:cell={physical_cell}",
            }
            for span_col in range(col, col + colspan):
                entry = copy.deepcopy(base)
                entry["col"] = span_col
                row.append(entry)
                if rowspan > 1:
                    active[span_col] = {"remaining": rowspan - 1, "cell": entry}
            col += colspan
        out.append(row)
    return out


def table_context():
    table_wrap, root = get_table_wrap_one()
    label = " ".join(text_of(x) for x in direct_children(table_wrap, {"label"}))
    caption = " ".join(text_of(x) for x in direct_children(table_wrap, {"caption"}))
    tables = descendants(table_wrap, "table")
    table = tables[0] if tables else table_wrap
    thead = next((x for x in direct_children(table, {"thead"})), None)
    tbody = next((x for x in direct_children(table, {"tbody"})), None)
    head_rows = direct_children(thead, {"tr"}) if thead is not None else []
    body_rows = direct_children(tbody, {"tr"}) if tbody is not None else []
    if not body_rows:
        all_rows = descendants(table, "tr")
        body_rows = all_rows[len(head_rows) :]
    head_grid = build_rows(head_rows, "header")
    body_grid = build_rows(body_rows, "body")
    header_by_col = {}
    for row in head_grid:
        for cell in row:
            header_by_col.setdefault(cell["col"], [])
            if cell["text"] and cell["text"] not in header_by_col[cell["col"]]:
                header_by_col[cell["col"]].append(cell["text"])
    all_text = " ".join([label, caption] + [" ".join(v) for v in header_by_col.values()])
    return {
        "label": label,
        "caption": caption,
        "header_by_col": header_by_col,
        "body_grid": body_grid,
        "unit": find_unit(all_text),
    }


def is_result_cell(cell, header_by_col):
    header = " ".join(header_by_col.get(cell["col"], []))
    if re.search(r"\bMIC\b|minimum inhibitory", header, re.I):
        return True
    raw = clean(cell["text"])
    return bool(re.fullmatch(r"(?:ND|N\.D\.|[<>]=?|<=|>=|≤|≥)?\s*\d+(?:\.\d+)?", raw, re.I))


def treatment_from_row(row, result_col):
    candidates = []
    for cell in row:
        if cell["col"] == result_col:
            continue
        value = clean(cell["text"])
        if not value:
            continue
        if species_from_text(value)[0]:
            continue
        if re.search(r"\bMIC\b|minimum inhibitory|ug\s*/\s*mL|µg\s*/\s*mL|μg\s*/\s*mL", value, re.I):
            continue
        candidates.append((value, cell["locator"]))
    sm07 = [x for x in candidates if re.search(r"\bSM[-\s]?07\b|SM07", x[0], re.I)]
    if sm07:
        return sm07[0]
    return candidates[0] if candidates else (None, None)


def row_target(row):
    for cell in row:
        species, strain, klass, gram = species_from_text(cell["text"])
        if species:
            return {
                "species": species,
                "strain": strain,
                "class": klass,
                "gram": gram,
                "locator": cell["locator"],
                "raw_text": clean(cell["text"]),
                "normalization_status": "ambiguous" if species == "ESCCO ATCC 25922" else None,
                "normalization_note": (
                    "source target label is preserved as ambiguous; no source-backed normalization to a canonical species was applied"
                    if species == "ESCCO ATCC 25922"
                    else None
                ),
            }
    return {"species": None, "strain": None, "class": None, "gram": None, "locator": None, "raw_text": None}


def make_common(
    record_id,
    kind,
    endpoint,
    treatment,
    raw_value,
    raw_unit,
    target,
    source_locator,
    source_locators,
    treatment_locator=None,
    value_locator=None,
    table_body_row=None,
):
    status = value_status(raw_value)
    normalized_value = normalize_value(raw_value) if status == "exact_quantitative" and raw_unit else None
    normalization_status = target.get("normalization_status") or ("direct" if normalized_value is not None else "not_convertible")
    if normalization_status == "ambiguous":
        normalized_value = None
    strain_or_isolate = target["strain"] or ("not_reported" if target["species"] else None)
    target_payload = {
        "class": target["class"] or "bacteria",
        "species": target["species"],
        "strain_or_isolate": strain_or_isolate,
        "gram_status": target["gram"],
    }
    if target.get("normalization_status") == "ambiguous":
        target_payload["normalization_status"] = "ambiguous"
        target_payload["normalization_note"] = target.get("normalization_note")
    if target["species"] and not target["strain"]:
        target_payload["strain_or_isolate_rationale"] = "source target cell did not report a strain/isolate token"
    return {
        "record_id": record_id,
        "paper_id": PAPER_ID,
        "evidence_kind": kind,
        "endpoint": endpoint,
        "entity": treatment,
        "peptide": treatment,
        "treatment": treatment,
        "raw_value": normalize_value(raw_value) if status == "exact_quantitative" else clean(raw_value),
        "raw_unit": raw_unit,
        "raw_unit_rationale": None if raw_unit else "No endpoint-specific source unit was bound to this row.",
        "raw_source_target": target.get("raw_text"),
        "raw_source_treatment": treatment,
        "raw_source_value": clean(raw_value),
        "value_status": status,
        "exactness_status": status,
        "normalization_status": normalization_status,
        "normalized_value": normalized_value if normalization_status in {"direct", "converted"} else None,
        "normalized_unit": raw_unit if normalization_status in {"direct", "converted"} and normalized_value is not None else None,
        "normalization_note": (
            target.get("normalization_note")
            if normalization_status == "ambiguous"
            else
            "direct transcription from source table; no value or unit conversion applied"
            if normalized_value is not None
            else "source row is a non-numeric or ambiguous table code; no quantitative normalization applied"
        ),
        "target_class": target["class"] or "bacteria",
        "target_species": target["species"],
        "target_strain_or_isolate": strain_or_isolate,
        "target_strain_or_isolate_rationale": target_payload.get("strain_or_isolate_rationale"),
        "target": target_payload,
        "assay_conditions": {
            "method_locator": "xml:p:17",
            "source_table_locator": "xml:table-wrap:1",
            "endpoint_unit_source": "xml:table-wrap:1:caption_or_header_unit" if raw_unit else None,
        },
        "statistics": {
            "reported": False,
            "notes": "No row-level replicate/statistic field was bound to this Table 1 cell.",
        },
        "evidence_ladder": "in_vitro_single_pathogen",
        "source_locator": source_locator,
        "source_locators": source_locators,
        "source_cell_locator": value_locator or source_locator,
        "source_cell_locators": {
            "target": target.get("locator"),
            "treatment": treatment_locator,
            "value": value_locator or source_locator,
        },
        "source_target_cell_locator": target.get("locator"),
        "source_treatment_cell_locator": treatment_locator,
        "source_value_cell_locator": value_locator or source_locator,
        "table_body_row": table_body_row,
        "ticket_row_id": f"xml:table-wrap:1:body-row={table_body_row}" if table_body_row else None,
        "evidence_source": "paper_local_primary_table",
        "database_provenance": None,
        "source_review_status": "source_reviewed_from_xml_table_wrap_1",
    }


def load_existing():
    if PACKET_ACTIVITY.exists():
        return json.loads(PACKET_ACTIVITY.read_text())
    if WORK_ACTIVITY.exists():
        return json.loads(WORK_ACTIVITY.read_text())
    return {}


def repair_toxicity(existing):
    existing_records = existing.get("toxicity_records") or []
    if existing_records:
        tox = copy.deepcopy(existing_records[0])
    else:
        tox = {
            "record_id": "PMC13025223-W2-TOX-001",
            "paper_id": PAPER_ID,
            "evidence_kind": "toxicity",
            "endpoint": "cell viability",
            "entity": "SM07",
            "peptide": "SM07",
            "treatment": "SM07",
            "raw_value": "qualitative source statement",
            "raw_unit": None,
            "raw_unit_rationale": "Qualitative toxicity observation; no exact numeric source value/unit extracted.",
            "target_class": "mammalian_cell_line",
            "target_species": "Vero cell line",
            "target_strain_or_isolate": "Vero",
            "target_cell_line": "Vero",
            "target": {
                "class": "mammalian_cell_line",
                "species": "Vero cell line",
                "strain_or_isolate": "Vero",
                "cell_line": "Vero",
            },
            "assay_conditions": {"source_context": "bounded XML/PDF toxicity locators"},
            "statistics": {"reported": False},
            "evidence_ladder": "toxicity_tested",
            "evidence_source": "paper_local_primary_text_or_figure",
            "database_provenance": None,
        }
    tox["normalization_status"] = "not_convertible"
    tox["normalized_value"] = None
    tox["normalized_unit"] = None
    tox["normalization_note"] = "top-level qualitative toxicity text retained; nested graph observations are approximate figure digitizations and are not exact source-table values"
    tox["toxicity_exactness_decision"] = "qualitative_text_plus_approximate_graph_digitization"
    tox["figure_digitization_status"] = "approximate_graph_digitized"
    tox["approximate_graph_values"] = copy.deepcopy(FIGURE6_GRAPH_VALUES)
    tox["approximate_graph_status"] = {
        "status": "approximate_graph_digitized",
        "reason": "Values are approximate graph-read observations from the bounded Figure 6 crop, retained with graph-derived exactness status.",
        "source_locator": FIGURE6_LOCATOR,
        "digitization_artifact": str(FIGURE6_DIGITIZATION),
    }
    locs = list(
        dict.fromkeys((tox.get("source_locators") or []) + ["xml:p:32", "xml:fig:6", "xml:caption:7", "pdf:page=9", FIGURE6_LOCATOR])
    )
    tox["source_locator"] = FIGURE6_LOCATOR
    tox["source_locators"] = locs
    tox["source_review_status"] = "source_reviewed_qualitative_text_with_approximate_graph_digitization"
    if tox.get("concentration") in (None, ""):
        tox.pop("concentration", None)
        tox.pop("concentration_unit", None)
    assay = tox.setdefault("assay_conditions", {})
    assay["toxicity_exactness_decision"] = tox["toxicity_exactness_decision"]
    assay["figure_digitization_status"] = tox["figure_digitization_status"]
    assay["figure_digitization_artifact"] = str(FIGURE6_DIGITIZATION)
    if assay.get("sample_concentration") in (None, ""):
        assay.pop("sample_concentration", None)
        assay.pop("sample_concentration_unit", None)
    return [tox]


def build_payload():
    existing = load_existing()
    ctx = table_context()
    unit = ctx["unit"] or "ug/mL"
    activity_records = []
    excluded = []
    table_rows = []
    sm07_rows = 0
    sm07_nd_rows = 0
    sm07_numeric_rows = 0
    non_sm07_rows = 0
    missing_target_rows = 0
    for row in ctx["body_grid"]:
        result_cells = [cell for cell in row if is_result_cell(cell, ctx["header_by_col"])]
        if not result_cells:
            continue
        result_cell = result_cells[-1]
        treatment, treatment_locator = treatment_from_row(row, result_cell["col"])
        target = row_target(row)
        raw_value = clean(result_cell["text"])
        status = value_status(raw_value)
        has_sm07 = bool(treatment and re.search(r"\bSM[-\s]?07\b|SM07", treatment, re.I))
        row_summary = {
            "body_row": result_cell["row"],
            "source_locator": result_cell["locator"],
            "target_species_present": bool(target["species"]),
            "target_strain_present": bool(target["strain"]),
            "treatment_has_sm07": has_sm07,
            "value_status": status,
        }
        table_rows.append(row_summary)
        locators = list(
            dict.fromkeys(
                [
                    "xml:table-wrap:1",
                    target["locator"],
                    treatment_locator,
                    result_cell["locator"],
                    "xml:table-wrap:1:caption_or_header_unit",
                    "xml:p:28",
                    "pdf:page=8",
                ]
            )
        )
        locators = [x for x in locators if x]
        if not target["species"]:
            missing_target_rows += 1
        if has_sm07:
            sm07_rows += 1
            if status == "exact_quantitative" and target["species"]:
                sm07_numeric_rows += 1
                rec = make_common(
                    f"PMC13025223-W2-ACT-{len(activity_records)+1:03d}",
                    "activity",
                    "MIC",
                    treatment,
                    raw_value,
                    unit,
                    target,
                    result_cell["locator"],
                    locators,
                    treatment_locator=treatment_locator,
                    value_locator=result_cell["locator"],
                    table_body_row=result_cell["row"],
                )
                rec["row_has_sm07"] = True
                rec["row_has_target"] = bool(target["species"])
                rec["row_type"] = "sm07_quantitative_activity"
                activity_records.append(rec)
            else:
                if status == "ND_not_numeric":
                    sm07_nd_rows += 1
                exclusion = make_common(
                    f"PMC13025223-W2-EXCL-{len(excluded)+1:03d}",
                    "activity_selectivity_exclusion",
                    "MIC",
                    treatment,
                    raw_value,
                    unit,
                    target,
                    result_cell["locator"],
                    locators,
                    treatment_locator=treatment_locator,
                    value_locator=result_cell["locator"],
                    table_body_row=result_cell["row"],
                )
                if exclusion["normalization_status"] != "ambiguous":
                    exclusion["normalization_status"] = "not_convertible"
                    exclusion["normalized_value"] = None
                    exclusion["normalized_unit"] = None
                exclusion["reason"] = "SM07 Table 1 source row retained as non-quantitative selectivity/ND evidence rather than promoted to an activity MIC record."
                exclusion["row_has_sm07"] = True
                exclusion["row_has_target"] = bool(target["species"])
                exclusion["row_type"] = "sm07_structured_exclusion"
                excluded.append(exclusion)
        else:
            non_sm07_rows += 1
            exclusion = make_common(
                f"PMC13025223-W2-REF-{non_sm07_rows:03d}",
                "reference_or_control_exclusion",
                "MIC",
                treatment,
                raw_value,
                unit,
                target,
                result_cell["locator"],
                locators,
                treatment_locator=treatment_locator,
                value_locator=result_cell["locator"],
                table_body_row=result_cell["row"],
            )
            exclusion["reason"] = "Non-SM07 reference/control Table 1 row kept separate from SM07 activity/selectivity evidence."
            exclusion["row_has_sm07"] = False
            exclusion["row_has_target"] = bool(target["species"])
            exclusion["row_type"] = "non_sm07_reference_or_control"
            if value_status(raw_value) != "exact_quantitative" and exclusion["normalization_status"] != "ambiguous":
                exclusion["normalization_status"] = "not_convertible"
                exclusion["normalized_value"] = None
                exclusion["normalized_unit"] = None
            excluded.append(exclusion)

    toxicity_records = repair_toxicity(existing)
    machine_rows = []
    machine_path = PACKET / "database/dbaasp_machine_extracted_rows.jsonl"
    if machine_path.exists():
        for idx, line in enumerate(machine_path.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            obj = json.loads(line)
            machine_rows.append(
                {
                    "machine_row_index": idx,
                    "peptide": obj.get("peptide"),
                    "endpoint": obj.get("endpoint"),
                    "value": obj.get("value"),
                    "unit": obj.get("unit"),
                    "target": obj.get("target"),
                    "verdict": obj.get("verdict"),
                    "status": "candidate_machine_evidence_not_primary_source",
                }
            )

    now = dt.datetime.now(dt.timezone.utc).isoformat()
    payload = {
        "paper_id": PAPER_ID,
        "artifact_role": "worker2_activity_toxicity_evidence",
        "generated_at": now,
        "reviewed_by": "worker-2",
        "source_review_scope": {
            "paper_xml": str(PACKET / "raw/paper.xml"),
            "paper_pdf_text": str(PACKET / "extracted/pdf_text.jsonl"),
            "pdf_tables": str(PACKET / "extracted/pdf_tables.json"),
            "supplementary_text": str(PACKET / "extracted/supplementary_text.jsonl"),
            "safe_candidate_handoff": str(PACKET / "analysis/activity_safe_candidate_handoff.json"),
            "database_machine_candidates": str(PACKET / "database/dbaasp_machine_extracted_rows.jsonl"),
            "linked_authoritative_rows_present": False,
            "bounded_extract_artifact": str(WORK / "bounded_source_extract.worker2.repair.json"),
            "table_repair_grid_summary": str(WORK / "table1_sm07_repair_grid.worker2.json"),
            "figure6_digitization_artifact": str(FIGURE6_DIGITIZATION),
            "figure6_crop_artifact": str(WORK / "figure6_digitization/figure6_crop.png"),
        },
        "material_surfaces_checked": {
            "xml_table_wraps_checked": ["xml:table-wrap:1"],
            "result_text_locators_checked": ["xml:p:28", "pdf:page=8"],
            "toxicity_locators_checked": ["xml:p:32", "xml:fig:6", "xml:caption:7", "pdf:page=9", FIGURE6_LOCATOR],
            "supplementary_text_rows_checked": 0,
            "linked_dbaasp_authoritative_rows_checked": 0,
        },
        "summary_counts": {
            "activity_records": len(activity_records),
            "toxicity_records": len(toxicity_records),
            "excluded_or_unresolved_candidates": len(excluded),
            "table1_body_rows_enumerated": len(table_rows),
            "table1_sm07_rows_enumerated": sm07_rows,
            "table1_sm07_numeric_activity_rows": sm07_numeric_rows,
            "table1_sm07_nd_or_non_numeric_structured_exclusions": sm07_rows - sm07_numeric_rows,
            "table1_non_sm07_reference_or_control_rows_separated": non_sm07_rows,
            "table1_rows_missing_target_after_rowspan_resolution": missing_target_rows,
        },
        "activity_records": activity_records,
        "toxicity_records": toxicity_records,
        "excluded_or_unresolved_candidates": excluded,
        "reference_or_non_amp_table_surfaces_excluded": {
            "non_sm07_table1_rows": non_sm07_rows,
            "reason": "reference/control rows are not SM07 primary activity records but retain target/treatment/source locator in structured exclusions",
            "source_locator": "xml:table-wrap:1",
        },
        "machine_extraction_kept_separate": machine_rows,
        "toxicity_source_assessment": {
            "biological_toxicity_signal_in_bounded_locators": bool(toxicity_records),
            "toxicity_record_emitted": bool(toxicity_records),
            "toxicity_exactness_decision": "qualitative_text_plus_approximate_graph_digitization",
            "figure_digitization_status": "approximate_graph_digitized",
            "figure_locator": FIGURE6_LOCATOR,
            "approximate_graph_value_count": len(toxicity_records[0].get("approximate_graph_values", [])) if toxicity_records else 0,
            "required_locators_present": all(
                loc in toxicity_records[0].get("source_locators", []) for loc in ["xml:p:32", "xml:fig:6", "pdf:page=9", FIGURE6_LOCATOR]
            )
            if toxicity_records
            else False,
        },
        "quality_checks": {
            "normalization_status_values_allowed": ["direct", "converted", "not_convertible", "ambiguous"],
            "normalization_status_values_observed": sorted(
                {r.get("normalization_status") for r in activity_records + toxicity_records + excluded}
            ),
            "direct_rows_have_normalized_value_and_unit": all(
                r.get("normalization_status") != "direct" or (r.get("normalized_value") is not None and r.get("normalized_unit"))
                for r in activity_records + toxicity_records + excluded
            ),
            "direct_rows_preserve_raw_and_normalized_unit": all(
                r.get("normalization_status") != "direct" or r.get("raw_unit") == r.get("normalized_unit")
                for r in activity_records + toxicity_records + excluded
            ),
            "all_sm07_rows_have_target_treatment_value_status_and_locator": all(
                r.get("target_species")
                and r.get("target_strain_or_isolate")
                and r.get("treatment")
                and r.get("value_status")
                and r.get("source_locator")
                for r in activity_records + [x for x in excluded if x.get("row_has_sm07") is True]
            ),
            "positive_purified_sm07_mic_direct_row_count": sum(
                1
                for r in activity_records
                if r.get("normalization_status") == "direct"
                and r.get("normalized_value") == "4"
                and r.get("normalized_unit") == "ug/mL"
                and r.get("target_species") == "Pseudomonas aeruginosa"
                and r.get("target_strain_or_isolate") == "ATCC27853"
            ),
            "toxicity_required_locators_present": all(
                loc in toxicity_records[0].get("source_locators", []) for loc in ["xml:p:32", "xml:fig:6", "pdf:page=9", FIGURE6_LOCATOR]
            )
            if toxicity_records
            else False,
            "toxicity_approximate_graph_values_present": bool(
                toxicity_records and toxicity_records[0].get("approximate_graph_values")
            ),
            "toxicity_approximate_graph_values_have_required_fields": all(
                all(
                    value.get(field) not in (None, "")
                    for field in (
                        "concentration",
                        "concentration_unit",
                        "percent_toxicity",
                        "exactness_status",
                        "source_locator",
                    )
                )
                and value.get("exactness_status") == "approximate_graph_digitized"
                and value.get("source_locator") == FIGURE6_LOCATOR
                for record in toxicity_records
                for value in record.get("approximate_graph_values", [])
            )
            if toxicity_records
            else False,
        },
    }
    return payload, table_rows


def validate_payload(payload):
    allowed = {"direct", "converted", "not_convertible", "ambiguous"}
    issues = []
    for section in ("activity_records", "toxicity_records", "excluded_or_unresolved_candidates"):
        for idx, rec in enumerate(payload.get(section, [])):
            prefix = f"{section}[{idx}]"
            if rec.get("normalization_status") not in allowed:
                issues.append(f"{prefix}.normalization_status")
            if rec.get("normalization_status") in {"direct", "converted"}:
                if rec.get("normalized_value") is None or not rec.get("normalized_unit"):
                    issues.append(f"{prefix}.normalized_required")
            for field in ("endpoint", "raw_value", "target_species", "source_locator", "evidence_ladder"):
                if not rec.get(field):
                    issues.append(f"{prefix}.{field}")
            if rec.get("row_has_sm07") is True and not rec.get("target_strain_or_isolate"):
                issues.append(f"{prefix}.target_strain_or_isolate")
            if not (rec.get("raw_unit") or rec.get("raw_unit_rationale")):
                issues.append(f"{prefix}.unit_or_rationale")
            if rec.get("assay_conditions", {}).get("sample_concentration") != rec.get("concentration") and rec.get("concentration") is not None:
                issues.append(f"{prefix}.concentration_mismatch")
    if payload["quality_checks"]["positive_purified_sm07_mic_direct_row_count"] != 1:
        issues.append("positive_purified_sm07_mic_direct_row_count")
    if not payload["quality_checks"]["toxicity_required_locators_present"]:
        issues.append("toxicity_required_locators_present")
    if not payload["quality_checks"]["all_sm07_rows_have_target_treatment_value_status_and_locator"]:
        issues.append("all_sm07_rows_have_target_treatment_value_status_and_locator")
    if not payload["quality_checks"]["toxicity_approximate_graph_values_present"]:
        issues.append("toxicity_approximate_graph_values_present")
    if not payload["quality_checks"]["toxicity_approximate_graph_values_have_required_fields"]:
        issues.append("toxicity_approximate_graph_values_have_required_fields")
    return issues


def build_final_payload(payload):
    final_payload = copy.deepcopy(payload)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    final_payload.update(
        {
            "finalized_at": now,
            "finalized_by": "worker-2_nonterminal_repair",
            "publication_grade_layer_accepted": False,
            "source_reviewed_by_worker6": False,
            "machine_rows_promoted_to_source_verified": False,
            "worker6_rebuild_basis": {
                "owner_artifact": str(PACKET_ACTIVITY),
                "owner_work_artifact": str(WORK_ACTIVITY),
                "rebuild_note": "worker-2 repaired activity/toxicity target fields and Figure 6 graph observations; worker-6 adjudication is still required",
                "ticket_contract_audit": str(WORK / "table1_target_field_audit.worker2.r03.json"),
            },
        }
    )
    return final_payload


def build_ticket_audit(payload, final_payload):
    all_rows = payload.get("activity_records", []) + payload.get("excluded_or_unresolved_candidates", [])
    by_id = {row.get("record_id"): row for row in all_rows}

    def row_check(record_id):
        row = by_id.get(record_id)
        if not row:
            return {"present": False}
        nested = row.get("target") or {}
        raw_target = row.get("raw_source_target") or ""
        return {
            "present": True,
            "has_raw_source_target": bool(raw_target),
            "has_source_cell_locator": bool(row.get("source_cell_locator")),
            "has_target_treatment_value_locators": all(
                (row.get("source_cell_locators") or {}).get(field) for field in ("target", "treatment", "value")
            ),
            "raw_target_mentions_baa747": bool(re.search(r"\bBAA\\s*747\b", raw_target, re.I)),
            "nested_target_strain_not_reported": nested.get("strain_or_isolate") == "not_reported",
            "raw_target_mentions_escco": bool(re.search(r"\bESCCO\\s+ATCC\\s*25922\b", raw_target, re.I)),
            "nested_target_species_is_escherichia_coli": nested.get("species") == "Escherichia coli",
            "normalization_status": row.get("normalization_status"),
        }

    open_ticket_count = 0
    request_path = PACKET / "rework/rework_requests.jsonl"
    response_path = PACKET / "rework/rework_responses.jsonl"
    if request_path.exists():
        terminal_statuses = {"closed_repaired", "closed_unrepaired", "closed_obsolete"}
        closed = set()
        if response_path.exists():
            for line in response_path.read_text().splitlines():
                if not line.strip():
                    continue
                try:
                    response = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if response.get("response_status") in terminal_statuses:
                    closed.add(response.get("ticket_id"))
        for line in request_path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue
            if request.get("ticket_id") not in closed:
                open_ticket_count += 1

    audit = {
        "paper_id": PAPER_ID,
        "ticket_id": TICKET_ID,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_surface": "xml:table-wrap:1 and pdf:page=9:figure=Figure 6",
        "parser": "xml table row-span propagation plus bounded Figure 6 crop digitization",
        "source_shape": {
            "table_wrap_count": 1,
            "body_rows": payload["summary_counts"]["table1_body_rows_enumerated"],
            "sm07_source_row_count": payload["summary_counts"]["table1_sm07_rows_enumerated"],
        },
        "artifact_checks": {
            "sm07_output_row_count": payload["summary_counts"]["table1_sm07_rows_enumerated"],
            "sm07_required_fields_present": payload["quality_checks"]["all_sm07_rows_have_target_treatment_value_status_and_locator"],
            "work_packet_worker2_byte_identical": WORK_ACTIVITY.read_bytes() == PACKET_ACTIVITY.read_bytes()
            if WORK_ACTIVITY.exists() and PACKET_ACTIVITY.exists()
            else False,
            "paper_packet_final_byte_identical": PAPER_FINAL.read_bytes() == PACKET_FINAL.read_bytes()
            if PAPER_FINAL.exists() and PACKET_FINAL.exists()
            else False,
            "normalization_status_values_allowed": set(payload["quality_checks"]["normalization_status_values_observed"]).issubset(
                set(payload["quality_checks"]["normalization_status_values_allowed"])
            ),
            "normalization_status_values_observed": payload["quality_checks"]["normalization_status_values_observed"],
            "toxicity_approximate_graph_value_count": payload["toxicity_source_assessment"]["approximate_graph_value_count"],
            "toxicity_approximate_graph_values_have_required_fields": payload["quality_checks"][
                "toxicity_approximate_graph_values_have_required_fields"
            ],
            "final_publication_grade_layer_accepted": final_payload.get("publication_grade_layer_accepted"),
            "packet_open_rework_ticket_count_before_worker6": open_ticket_count,
        },
        "ticket_row_checks": {
            "EXCL-004": row_check("PMC13025223-W2-EXCL-004"),
            "EXCL-005": row_check("PMC13025223-W2-EXCL-005"),
            "EXCL-009": row_check("PMC13025223-W2-EXCL-009"),
            "EXCL-010": row_check("PMC13025223-W2-EXCL-010"),
        },
        "summary_counts": payload["summary_counts"],
        "issue_count": 0,
        "issues": [],
        "status": "repair_ready_for_worker6_adjudication",
        "artifacts_checked": [
            str(WORK_ACTIVITY),
            str(PACKET_ACTIVITY),
            str(PAPER_FINAL),
            str(PACKET_FINAL),
            str(FIGURE6_DIGITIZATION),
        ],
    }
    for record_id, check in audit["ticket_row_checks"].items():
        if not check.get("present"):
            audit["issues"].append(f"{record_id}.missing")
        if check.get("raw_target_mentions_baa747") and check.get("nested_target_strain_not_reported"):
            audit["issues"].append(f"{record_id}.nested_target_strain_not_reported")
        if check.get("raw_target_mentions_escco") and check.get("nested_target_species_is_escherichia_coli"):
            audit["issues"].append(f"{record_id}.escco_silently_normalized")
    if audit["issues"]:
        audit["issue_count"] = len(audit["issues"])
        audit["status"] = "fail"
    return audit


def append_response(payload, validation_path):
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    response = {
        "ticket_id": TICKET_ID,
        "paper_id": PAPER_ID,
        "target_queue": "analysis",
        "response_status": "repair_ready_for_adjudication",
        "response_by": "worker-2",
        "analysis_can_resume": True,
        "responded_at_utc": now,
        "evidence": {
            "activity_records": len(payload.get("activity_records", [])),
            "toxicity_records": len(payload.get("toxicity_records", [])),
            "table1_body_rows_enumerated": payload["summary_counts"]["table1_body_rows_enumerated"],
            "table1_sm07_rows_enumerated": payload["summary_counts"]["table1_sm07_rows_enumerated"],
            "table1_sm07_structured_exclusions": payload["summary_counts"][
                "table1_sm07_nd_or_non_numeric_structured_exclusions"
            ],
            "positive_purified_sm07_mic_direct_row_count": payload["quality_checks"][
                "positive_purified_sm07_mic_direct_row_count"
            ],
            "toxicity_exactness_decision": payload["toxicity_source_assessment"]["toxicity_exactness_decision"],
            "figure_digitization_status": payload["toxicity_source_assessment"]["figure_digitization_status"],
            "approximate_graph_value_count": payload["toxicity_source_assessment"]["approximate_graph_value_count"],
            "normalization_status_values_observed": payload["quality_checks"]["normalization_status_values_observed"],
        },
        "evidence_paths": [
            str(WORK / "bounded_source_extract.worker2.repair.json"),
            str(WORK / "table1_sm07_repair_grid.worker2.json"),
            str(WORK / "table1_target_field_audit.worker2.r03.json"),
            str(FIGURE6_DIGITIZATION),
            str(validation_path),
        ],
        "repaired_artifacts": [str(WORK_ACTIVITY), str(PACKET_ACTIVITY), str(PAPER_FINAL), str(PACKET_FINAL)],
        "artifacts_written": [
            str(WORK_ACTIVITY),
            str(PACKET_ACTIVITY),
            str(PAPER_FINAL),
            str(PACKET_FINAL),
            str(WORK / "table1_sm07_repair_grid.worker2.json"),
            str(WORK / "worker2_table1_toxicity_repair_validation.json"),
            str(WORK / "table1_target_field_audit.worker2.r03.json"),
            str(FIGURE6_DIGITIZATION),
            str(WORK / "activity_generation_summary.worker2.json"),
        ],
        "added_files": [
            str(WORK / "table1_sm07_repair_grid.worker2.json"),
            str(WORK / "worker2_table1_toxicity_repair_validation.json"),
            str(WORK / "table1_target_field_audit.worker2.r03.json"),
            str(FIGURE6_DIGITIZATION),
        ],
        "validation_artifacts": [str(validation_path)],
        "reason": "Rebuilt worker-2 activity/toxicity evidence from bounded paper-local Table 1 and toxicity locators, preserving all SM07 rows as either the direct positive MIC row or structured source-located exclusions and adding approximate Figure 6 graph-derived toxicity observations.",
        "notes": [
            "This worker-2 response is nonterminal; worker-6 must perform fresh adjudication before closing the ticket.",
            "DBAASP Codex fallback rows remain candidate machine evidence only.",
            "No web access was used.",
        ],
    }
    with REWORK_RESPONSES.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(response, ensure_ascii=False, sort_keys=False) + "\n")
    return response


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    FIGURE6_DIGITIZATION.parent.mkdir(parents=True, exist_ok=True)
    payload, table_rows = build_payload()
    validation_issues = validate_payload(payload)
    final_payload = build_final_payload(payload)
    grid_path = WORK / "table1_sm07_repair_grid.worker2.json"
    validation_path = WORK / "worker2_table1_toxicity_repair_validation.json"
    audit_path = WORK / "table1_target_field_audit.worker2.r03.json"
    FIGURE6_DIGITIZATION.write_text(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "source_locator": FIGURE6_LOCATOR,
                "generated_at": payload["generated_at"],
                "digitization_status": "approximate_graph_digitized",
                "exactness_status": "approximate_graph_digitized",
                "plot_crop_artifact": str(WORK / "figure6_digitization/figure6_crop.png"),
                "page_render_artifact": str(WORK / "figure6_digitization/page9-09.png"),
                "axis_calibration": {
                    "x_axis": "log10 concentration, mg/mL",
                    "y_axis": "percent toxicity, 0 to 150",
                    "digitization_note": "bounded plot-crop visual calibration; values are approximate graph-read observations",
                },
                "approximate_graph_values": FIGURE6_GRAPH_VALUES,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    grid_path.write_text(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "source_locator": "xml:table-wrap:1",
                "generated_at": payload["generated_at"],
                "rows": table_rows,
                "summary_counts": payload["summary_counts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    for path in (WORK_ACTIVITY, PACKET_ACTIVITY):
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    for path in (PAPER_FINAL, PACKET_FINAL):
        path.write_text(json.dumps(final_payload, ensure_ascii=False, indent=2))
    audit = build_ticket_audit(payload, final_payload)
    if audit["issues"]:
        validation_issues.extend(audit["issues"])
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2))
    validation = {
        "paper_id": PAPER_ID,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "pass" if not validation_issues else "fail",
        "issue_count": len(validation_issues),
        "issue_fields": validation_issues,
        "artifact_paths": [str(WORK_ACTIVITY), str(PACKET_ACTIVITY), str(PAPER_FINAL), str(PACKET_FINAL), str(grid_path)],
        "summary_counts": payload["summary_counts"],
        "quality_checks": payload["quality_checks"],
        "ticket_audit": str(audit_path),
    }
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2))
    response_appended = False
    if not validation_issues:
        append_response(payload, validation_path)
        response_appended = True
    summary = {
        "paper_id": PAPER_ID,
        "written": [str(WORK_ACTIVITY), str(PACKET_ACTIVITY)],
        "finals_written": [str(PAPER_FINAL), str(PACKET_FINAL)],
        "validation": str(validation_path),
        "ticket_audit": str(audit_path),
        "figure6_digitization": str(FIGURE6_DIGITIZATION),
        "status": validation["status"],
        "activity_records": len(payload["activity_records"]),
        "toxicity_records": len(payload["toxicity_records"]),
        "approximate_graph_values": payload["toxicity_source_assessment"]["approximate_graph_value_count"],
        "structured_exclusions": len(payload["excluded_or_unresolved_candidates"]),
        "sm07_rows": payload["summary_counts"]["table1_sm07_rows_enumerated"],
        "response_appended": response_appended,
    }
    summary_path = WORK / "activity_generation_summary.worker2.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps({"status": validation["status"], "summary_path": str(summary_path), "response_appended": response_appended}))
    if validation_issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
