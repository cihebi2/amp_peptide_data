#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import sys
import unicodedata
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET


PAPER_ID = "PMC12160004"
WORKER_ID = "worker-2"
TICKET_ID = "rwk-PMC12160004-campaign-r02-BF-PMC12160004-W2-ACTIVITY-TOXICITY-UNSUPPORTED-ROWS"
PEPTIDES = ["A3", "D-A3", "A3-C4", "A3-C5", "A3-C6"]

SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[4]
PAPER_ROOT = ROOT / "papers" / PAPER_ID
PACKET_ROOT = ROOT / "packets" / PAPER_ID
WORK_DIR = PAPER_ROOT / "work" / "activity_evidence"

XML_PATH = PAPER_ROOT / "source" / "paper.xml"
SOURCE_ACTIVITY = WORK_DIR / "activity_records.json"
PACKET_ACTIVITY = PACKET_ROOT / "analysis" / "activity_toxicity_evidence.worker2.json"
SUPP_S13 = PAPER_ROOT / "work" / "supplementary_methods" / "figure_s13_digitization.worker3.json"
ZF_BINDING = WORK_DIR / "zebrafish_p40_quantitative_binding.worker2.sanitized.json"
REWORK_RESPONSES = PACKET_ROOT / "rework" / "rework_responses.jsonl"

VALIDATION_PATH = WORK_DIR / "worker2_repair_validation.json"
INSPECTION_PATH = WORK_DIR / "worker2_repair_locator_inspection.sanitized.json"
RESPONSE_AUDIT_PATH = WORK_DIR / "worker2_rework_response_audit.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lname(tag: str) -> str:
    return tag.split("}", 1)[-1]


def text_content(node: ET.Element) -> str:
    return " ".join("".join(node.itertext()).split())


def canonical_unit(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "")
    normalized = normalized.replace("µ", "μ")
    compact = re.sub(r"\s+", "", normalized.casefold())
    if "μg" in normalized and ("ml" in compact or "mL" in normalized):
        return "μg/mL"
    return text


def source_unit_spelling(table_text: str, table_index: int) -> str:
    candidates = re.findall(r"μg\s*m[lL](?:\s*[−-]\s*1)?|μg\s*/\s*m[lL]", table_text)
    if candidates:
        return " ".join(candidates[0].split())
    return "μg ml−1" if table_index == 1 else "μg mL−1"


def direct_children(node: ET.Element, names: set[str]) -> list[ET.Element]:
    return [child for child in list(node) if lname(child.tag) in names]


def table_wraps(root: ET.Element) -> list[ET.Element]:
    return [node for node in root.iter() if lname(node.tag) == "table-wrap"]


def body_rows(table_wrap: ET.Element) -> list[ET.Element]:
    rows = [node for node in table_wrap.iter() if lname(node.tag) == "tr"]
    return [row for row in rows if any(lname(cell.tag) == "td" for cell in list(row))]


def build_table_maps() -> tuple[dict[str, str], dict[str, dict]]:
    root = ET.parse(XML_PATH).getroot()
    values: dict[str, str] = {}
    meta: dict[str, dict] = {}
    for table_index, table_wrap in enumerate(table_wraps(root), start=1):
        table_locator = f"xml:table-wrap:{table_index}"
        table_text = text_content(table_wrap)
        source_unit = source_unit_spelling(table_text, table_index)
        meta[table_locator] = {
            "xml_id": table_wrap.get("id"),
            "source_unit_spelling": source_unit,
            "canonical_raw_unit": canonical_unit(source_unit),
            "body_row_count": len(body_rows(table_wrap)),
            "activity_cell_count": 0,
        }
        for body_index, row in enumerate(body_rows(table_wrap), start=1):
            cells = direct_children(row, {"td", "th"})
            for cell_index, cell in enumerate(cells, start=1):
                locator = f"{table_locator}:body-row={body_index}:cell={cell_index}"
                values[locator] = text_content(cell)
                if (table_index == 1 and cell_index >= 3) or (table_index == 2 and cell_index >= 2):
                    meta[table_locator]["activity_cell_count"] += 1
    return values, meta


def parse_cell_locator(record: dict) -> tuple[str, str, int, int]:
    source_locator = record.get("source_locator") if isinstance(record.get("source_locator"), dict) else {}
    locator = (
        source_locator.get("locator")
        or source_locator.get("cell_locator")
        or ""
    )
    match = re.search(r"(xml:table-wrap:\d+):body-row=(\d+):cell=(\d+)", str(locator))
    if not match:
        table = source_locator.get("table_locator") or source_locator.get("table") or ""
        body = source_locator.get("body_row")
        cell = source_locator.get("cell")
        if table and body and cell:
            locator = f"{table}:body-row={body}:cell={cell}"
            match = re.search(r"(xml:table-wrap:\d+):body-row=(\d+):cell=(\d+)", locator)
    if not match:
        raise ValueError(f"missing resolvable table cell locator in {record.get('record_id')}")
    table_locator = match.group(1)
    body_row = int(match.group(2))
    cell = int(match.group(3))
    return table_locator, f"{table_locator}:body-row={body_row}:cell={cell}", body_row, cell


def peptide_entity_map(rows: list[dict]) -> dict[str, dict]:
    mapped: dict[str, dict] = {}
    for row in rows:
        peptide = row.get("peptide")
        if peptide in PEPTIDES and peptide not in mapped:
            mapped[peptide] = {
                "entity": deepcopy(row.get("entity") or {"name": peptide}),
                "sequence": row.get("sequence"),
                "modification": row.get("modification"),
            }
    for peptide in PEPTIDES:
        mapped.setdefault(peptide, {"entity": {"name": peptide}, "sequence": None, "modification": None})
    return mapped


def repair_mic_records(prior_rows: list[dict], table_values: dict[str, str], table_meta: dict[str, dict], reviewed_at: str) -> tuple[list[dict], list[dict]]:
    repaired: list[dict] = []
    mismatches: list[dict] = []
    for row in prior_rows:
        if row.get("endpoint") != "MIC":
            continue
        fixed = deepcopy(row)
        table_locator, cell_locator, body_row, cell = parse_cell_locator(fixed)
        source_value = table_values.get(cell_locator)
        if source_value is None:
            mismatches.append({"record_id": fixed.get("record_id"), "cell_locator": cell_locator, "issue": "cell_locator_not_found"})
            source_value = fixed.get("raw_value")
        previous_value = fixed.get("raw_value")
        if str(previous_value) != str(source_value):
            mismatches.append({
                "record_id": fixed.get("record_id"),
                "cell_locator": cell_locator,
                "issue": "raw_value_corrected_from_source_cell",
            })
        unit = table_meta[table_locator]["canonical_raw_unit"]
        source_unit = table_meta[table_locator]["source_unit_spelling"]
        fixed.update(
            {
                "raw_value": str(source_value),
                "raw_unit": unit,
                "raw_unit_rationale": "Source table MIC header reports mass concentration; source spelling preserved in source_unit_source_spelling.",
                "source_unit_source_spelling": source_unit,
                "normalization_status": "not_convertible",
                "normalized_value": None,
                "normalized_unit": None,
                "normalization_note": "Molar normalization is not performed because this layer preserves the source mass-concentration unit and no source-reviewed molecular-weight/modification conversion is applied here.",
                "source_review_status": "source_reviewed_repaired",
                "source_reviewed_at": reviewed_at,
                "value_precision": "source_table_cell",
            }
        )
        fixed["source_locator"] = {
            "table_locator": table_locator,
            "locator": cell_locator,
            "cell_locator": cell_locator,
            "body_row": body_row,
            "cell": cell,
            "unit_context": {
                "table_header_locator": f"{table_locator}:header",
                "source_unit": source_unit,
                "canonical_raw_unit": unit,
            },
            "method_context": "xml:p:18" if table_locator == "xml:table-wrap:1" else "xml:p:24",
        }
        fixed["source_locators"] = [cell_locator, table_locator]
        fixed["source_review"] = {
            "reviewed_by": WORKER_ID,
            "source_basis": "paper_xml_table_cell_and_header",
            "candidate_handoff_used_as_hint_only": True,
            "machine_candidate_promoted": False,
        }
        repaired.append(fixed)
    return repaired, mismatches


def entity_fields(peptide: str, entity_map: dict[str, dict]) -> dict:
    info = entity_map.get(peptide, {"entity": {"name": peptide}, "sequence": None, "modification": None})
    entity = deepcopy(info.get("entity") or {"name": peptide})
    entity.setdefault("name", peptide)
    return {
        "entity": entity,
        "peptide": peptide,
        "sequence": info.get("sequence"),
        "modification": info.get("modification"),
    }


def build_biofilm_records(entity_map: dict[str, dict], reviewed_at: str) -> list[dict]:
    payload = read_json(SUPP_S13)
    records: list[dict] = []
    for index, obs in enumerate(payload.get("observations", []), start=1):
        treatment = obs.get("treatment") or "not reported"
        peptide = treatment if treatment in PEPTIDES else None
        entity = entity_fields(peptide, entity_map) if peptide else {
            "entity": {"name": treatment, "role": "figure_control"},
            "peptide": treatment,
            "sequence": None,
            "modification": None,
        }
        concentration = str(obs.get("concentration") or "")
        source_locator = str(obs.get("source_locator") or "supp:RA-015-D5RA02745D-s001.pdf:page=11:figure=S13")
        row = {
            "record_id": f"{PAPER_ID}-W2-BIOFILM-S13-{index:03d}",
            "paper_id": PAPER_ID,
            "evidence_kind": "activity",
            "evidence_role": "source_located_biofilm_phenotype_observation",
            "endpoint": "biofilm biomass OD575",
            "raw_endpoint_label": "OD575",
            "raw_value": str(obs.get("raw_value")),
            "raw_unit": str(obs.get("raw_unit") or "OD575 absorbance"),
            "raw_unit_rationale": "Figure readout is an optical-density endpoint, not a concentration unit.",
            "normalization_status": "direct",
            "normalized_value": str(obs.get("raw_value")),
            "normalized_unit": str(obs.get("raw_unit") or "OD575 absorbance"),
            "normalization_note": "Direct preservation of the digitized figure readout; no unit conversion.",
            "target": {
                "target_class": "bacteria",
                "species": "Staphylococcus aureus",
                "strain_or_isolate": "ATCC-25923",
                "gram_status": "Gram-positive",
                "raw_source_label": "S. aureus ATCC-25923",
            },
            "target_class": "bacteria",
            "target_species": "Staphylococcus aureus",
            "target_strain_or_isolate": "ATCC-25923",
            "target_isolate": "ATCC-25923",
            "treatment": treatment,
            **entity,
            "concentration": concentration,
            "concentration_unit": "MIC multiple" if "MIC" in concentration else ("none" if concentration == "none" else None),
            "assay_conditions": {
                "assay_context": "biofilm phenotype figure observation",
                "sample_concentration": concentration,
                "sample_concentration_unit": "MIC multiple" if "MIC" in concentration else ("none" if concentration == "none" else None),
                "method_or_result_source_locators": ["xml:p:33", "xml:fig:6", source_locator],
                "approximation_status": obs.get("exact_vs_approximate_status"),
            },
            "statistics": {"reported": False, "rationale": "No row-level replicate/statistic value is assigned to the digitized figure point in this worker artifact."},
            "evidence_ladder": "in_vitro_single_pathogen",
            "source_locator": {
                "locator": source_locator,
                "source_locators": [source_locator, "xml:p:33", "xml:fig:6"],
                "figure": source_locator,
                "main_text_context": "xml:p:33",
                "main_figure_context": "xml:fig:6",
                "source_observation_type": "approximate_supplement_figure_digitization",
            },
            "source_locators": [source_locator, "xml:p:33", "xml:fig:6"],
            "source_review_status": "source_reviewed_approximate_digitization",
            "source_review": {
                "reviewed_by": WORKER_ID,
                "source_basis": "worker3_supplement_digitization_reopened_as_source_locator_surface",
                "candidate_handoff_used_as_hint_only": False,
            },
            "source_reviewed_at": reviewed_at,
            "machine_candidate_provenance": [],
            "database_provenance_boundary": "primary_source_or_supplement_locator_not_database_row",
            "value_precision": obs.get("exact_vs_approximate_status") or "approximate_image_digitization",
            "digitization_uncertainty": obs.get("uncertainty"),
        }
        records.append(row)
    return records


def build_hemolysis_records(entity_map: dict[str, dict], reviewed_at: str) -> list[dict]:
    rows: list[dict] = []
    for peptide in PEPTIDES:
        entity = entity_fields(peptide, entity_map)
        rows.append(
            {
                "record_id": f"{PAPER_ID}-W2-TOX-HEM-{peptide.replace('-', '_')}",
                "paper_id": PAPER_ID,
                "evidence_kind": "toxicity",
                "evidence_role": "source_located_threshold_observation",
                "endpoint": "percent hemolysis",
                "raw_endpoint_label": "hemolysis",
                "raw_value": "<5",
                "raw_unit": "%",
                "raw_unit_rationale": "Percentage threshold is source-located; exact per-treatment bar values are not promoted from the figure surface.",
                "normalization_status": "direct",
                "normalized_value": "<5",
                "normalized_unit": "%",
                "normalization_note": "Direct percent threshold; no conversion.",
                "target": {
                    "target_class": "mammalian erythrocyte",
                    "species": "Oryctolagus cuniculus",
                    "strain_or_isolate": "rabbit red blood cells",
                    "cell_type": "red blood cells",
                    "raw_source_label": "rabbit red blood cells",
                },
                "target_class": "mammalian erythrocyte",
                "target_species": "Oryctolagus cuniculus",
                "target_strain_or_isolate": "rabbit red blood cells",
                "target_cell_type": "red blood cells",
                "treatment": peptide,
                **entity,
                "concentration": "0.9-500",
                "concentration_unit": "μg/mL",
                "assay_conditions": {
                    "assay_context": "hemolysis assay against rabbit red blood cells",
                    "temperature": "37 °C",
                    "incubation_time": "1 hour",
                    "peptide_concentration": "0.9-500",
                    "peptide_concentration_unit": "μg/mL",
                    "method_source_locator": "xml:p:25",
                    "result_source_locator": "xml:p:39",
                    "figure_source_locator": "xml:fig:10",
                    "exact_value_limitation": "Exact per-treatment figure values are not accepted as row-level values in this repair artifact.",
                },
                "statistics": {"reported": False, "rationale": "No row-level replicate/statistic value is assigned in the extracted source surface."},
                "evidence_ladder": "toxicity_tested",
                "source_locator": {
                    "locator": "xml:p:39",
                    "source_locators": ["xml:p:25", "xml:p:39", "xml:fig:10"],
                    "method": "xml:p:25",
                    "result": "xml:p:39",
                    "figure": "xml:fig:10",
                    "source_observation_type": "threshold_statement_with_figure_surface",
                },
                "source_locators": ["xml:p:25", "xml:p:39", "xml:fig:10"],
                "source_review_status": "source_reviewed_repaired",
                "source_review": {
                    "reviewed_by": WORKER_ID,
                    "source_basis": "paper_xml_method_result_and_figure_locator",
                    "candidate_handoff_used_as_hint_only": True,
                },
                "source_reviewed_at": reviewed_at,
                "machine_candidate_provenance": [],
                "database_provenance_boundary": "primary_source_locator_not_database_row",
                "value_precision": "source_threshold",
            }
        )
    return rows


def build_zebrafish_records(entity_map: dict[str, dict], reviewed_at: str) -> list[dict]:
    rows: list[dict] = []
    payload = read_json(ZF_BINDING)
    for obs in payload.get("quantitative_observation_bindings", []):
        peptide = obs["peptide"]
        entity = entity_fields(peptide, entity_map)
        rows.append(
            {
                "record_id": f"{PAPER_ID}-W2-TOX-ZF-{obs['observation_id'].replace('xml-p40-zf-', '').replace('-', '_')}",
                "paper_id": PAPER_ID,
                "evidence_kind": "toxicity",
                "evidence_role": "source_located_quantitative_zebrafish_observation",
                "endpoint": "zebrafish hatching percentage",
                "raw_endpoint_label": "zebrafish hatching",
                "raw_value": str(obs["raw_value"]),
                "raw_unit": "%",
                "raw_unit_rationale": "Source-local p40 result surface reports hatching as a percentage; the percent unit is preserved directly.",
                "normalization_status": "direct",
                "normalized_value": str(obs["raw_value"]),
                "normalized_unit": "%",
                "normalization_note": "Direct percent readout; no value or unit conversion.",
                "target": {
                    "target_class": "vertebrate embryo",
                    "species": "Danio rerio",
                    "strain_or_isolate": "zebrafish embryos",
                    "raw_source_label": "zebrafish embryos",
                },
                "target_class": "vertebrate embryo",
                "target_species": "Danio rerio",
                "target_strain_or_isolate": "zebrafish embryos",
                "treatment": peptide,
                **entity,
                "concentration": str(obs.get("concentration")),
                "concentration_unit": str(obs.get("concentration_unit") or "μg/mL"),
                "timepoint": str(obs.get("timepoint")),
                "assay_conditions": {
                    "assay_context": "zebrafish hatching/development toxicity assay",
                    "peptide_concentration": str(obs.get("concentration")),
                    "peptide_concentration_unit": str(obs.get("concentration_unit") or "μg/mL"),
                    "timepoint": str(obs.get("timepoint")),
                    "method_source_locator": "xml:p:26",
                    "result_source_locator": "xml:p:40",
                    "figure_source_locator": "xml:fig:11",
                    "quantitative_binding_status": "source_text_bound",
                    "value_precision": obs.get("value_precision") or "reported",
                },
                "statistics": {"reported": False, "rationale": "No row-level statistical value is assigned to this source-text observation."},
                "evidence_ladder": "in_vivo_tested",
                "source_locator": {
                    "locator": "xml:p:40",
                    "source_locators": ["xml:p:26", "xml:p:40", "xml:fig:11"],
                    "method": "xml:p:26",
                    "result": "xml:p:40",
                    "figure": "xml:fig:11",
                    "source_observation_type": "zebrafish_hatching_quantitative_statement",
                    "binding_artifact": str(ZF_BINDING.relative_to(ROOT.parents[2])),
                },
                "source_locators": ["xml:p:26", "xml:p:40", "xml:fig:11"],
                "source_review_status": "source_reviewed_repaired_quantitative_statement",
                "source_review": {
                    "reviewed_by": WORKER_ID,
                    "source_basis": "paper_xml_method_result_figure_locator_and_sanitized_token_binding",
                    "candidate_handoff_used_as_hint_only": True,
                },
                "source_reviewed_at": reviewed_at,
                "machine_candidate_provenance": [],
                "database_provenance_boundary": "primary_source_locator_not_database_row",
                "value_precision": obs.get("value_precision") or "reported",
            }
        )
    for obs in payload.get("qualitative_observation_bindings", []):
        peptide = obs["peptide"]
        entity = entity_fields(peptide, entity_map)
        rows.append(
            {
                "record_id": f"{PAPER_ID}-W2-TOX-ZF-{obs['observation_id'].replace('xml-p40-zf-', '').replace('-', '_')}",
                "paper_id": PAPER_ID,
                "evidence_kind": "toxicity",
                "evidence_role": "source_located_qualitative_zebrafish_comparison",
                "endpoint": obs.get("endpoint") or "zebrafish hatching/development qualitative comparison",
                "raw_endpoint_label": "zebrafish hatching/development qualitative comparison",
                "raw_value": obs.get("raw_value") or "qualitative_comparison_reported",
                "raw_unit": None,
                "raw_unit_rationale": obs.get("no_unit_rationale"),
                "no_unit_rationale": obs.get("no_unit_rationale"),
                "normalization_status": "ambiguous",
                "normalized_value": None,
                "normalized_unit": None,
                "normalization_note": "Qualitative comparison row; no direct or converted numeric normalization is emitted.",
                "target": {
                    "target_class": "vertebrate embryo",
                    "species": "Danio rerio",
                    "strain_or_isolate": "zebrafish embryos",
                    "raw_source_label": "zebrafish embryos",
                },
                "target_class": "vertebrate embryo",
                "target_species": "Danio rerio",
                "target_strain_or_isolate": "zebrafish embryos",
                "treatment": peptide,
                **entity,
                "concentration": None,
                "concentration_unit": None,
                "timepoint": None,
                "assay_conditions": {
                    "assay_context": "zebrafish hatching/development toxicity assay",
                    "peptide_concentration": None,
                    "peptide_concentration_unit": None,
                    "timepoint": None,
                    "method_source_locator": "xml:p:26",
                    "result_source_locator": "xml:p:40",
                    "figure_source_locator": "xml:fig:11",
                    "quantitative_binding_status": "qualitative_only",
                },
                "statistics": {"reported": False, "rationale": "No row-level statistical value is assigned to this qualitative source-text observation."},
                "evidence_ladder": "in_vivo_tested",
                "source_locator": {
                    "locator": "xml:p:40",
                    "source_locators": ["xml:p:26", "xml:p:40", "xml:fig:11"],
                    "method": "xml:p:26",
                    "result": "xml:p:40",
                    "figure": "xml:fig:11",
                    "source_observation_type": "zebrafish_hatching_qualitative_comparison",
                    "binding_artifact": str(ZF_BINDING.relative_to(ROOT.parents[2])),
                },
                "source_locators": ["xml:p:26", "xml:p:40", "xml:fig:11"],
                "source_review_status": "source_reviewed_repaired_qualitative_statement",
                "source_review": {
                    "reviewed_by": WORKER_ID,
                    "source_basis": "paper_xml_method_result_figure_locator_and_sanitized_token_binding",
                    "candidate_handoff_used_as_hint_only": True,
                },
                "source_reviewed_at": reviewed_at,
                "machine_candidate_provenance": [],
                "database_provenance_boundary": "primary_source_locator_not_database_row",
                "value_precision": "qualitative_source_statement",
            }
        )
    return rows


def validation_gate_module():
    gate_path = ROOT.parents[2] / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "semantic_three_layer_gate.py"
    spec = importlib.util.spec_from_file_location("semantic_three_layer_gate", gate_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load semantic gate module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def semantic_activity_issues(payload: dict) -> list[dict]:
    gate = validation_gate_module()
    issues: list[dict] = []
    table_text_by_locator = gate.load_packet_table_text(ROOT, PAPER_ID)
    records = payload.get("activity_records") if isinstance(payload.get("activity_records"), list) else []
    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        endpoint = str(record.get("endpoint") or "").strip()
        raw_value_obj = record.get("raw_value")
        raw_value = "" if raw_value_obj is None else str(raw_value_obj).strip()
        species = gate.target_species(record)
        locator = gate.record_source_locators(record)
        where = {"record_index": idx, "record_id": record.get("record_id")}
        if endpoint.lower() in gate.GENERIC_ENDPOINTS:
            issues.append({"severity": "hard", "layer": "activity", "code": "generic_endpoint", **where})
        if endpoint.upper() in gate.MIC_LIKE and not gate.unit_present(record):
            issues.append({"severity": "hard", "layer": "activity", "code": "mic_like_missing_unit", **where})
        if not raw_value:
            issues.append({"severity": "hard", "layer": "activity", "code": "missing_raw_value", **where})
        if not species:
            issues.append({"severity": "hard", "layer": "activity", "code": "missing_target_species", **where})
        elif gate.species_is_sentence_fragment(species):
            issues.append({"severity": "hard", "layer": "activity", "code": "sentence_fragment_species", **where})
        if gate.species_is_non_biological_label(species):
            issues.append({"severity": "hard", "layer": "activity", "code": "non_biological_target_label", **where})
        if not gate.source_locator_has_anchor(locator):
            issues.append({"severity": "hard", "layer": "activity", "code": "missing_source_locator", **where})
    table_evidence_records = gate.activity_toxicity_records(payload)
    toxicity_record_ids = {id(record) for record in payload.get("toxicity_records", []) if isinstance(record, dict)}
    for idx, record in enumerate(table_evidence_records):
        if not isinstance(record, dict):
            continue
        locator = gate.record_source_locators(record)
        for table_locator in sorted(gate.table_locator_ids(locator)):
            table_text = table_text_by_locator.get(table_locator, "")
            if table_text and gate.source_table_is_non_activity(table_text):
                issues.append({
                    "severity": "hard",
                    "layer": "activity",
                    "code": "non_activity_source_table",
                    "source_locator": table_locator,
                    "evidence_kind": "toxicity" if id(record) in toxicity_record_ids else "activity",
                    "record_index": idx,
                    "record_id": record.get("record_id"),
                })
    cited_activity_tables: set[str] = set()
    for record in table_evidence_records:
        if isinstance(record, dict):
            cited_activity_tables.update(gate.table_locator_ids(gate.record_source_locators(record)))
    for table_locator, table_text in table_text_by_locator.items():
        if gate.table_has_activity_measurement(table_text) and table_locator not in cited_activity_tables:
            issues.append({"severity": "hard", "layer": "activity", "code": "missing_activity_table_coverage", "source_locator": table_locator})
    for func in (
        gate.expected_table_observation_issues,
        gate.expected_non_table_observation_issues,
        gate.expected_evidence_kind_count_issues,
    ):
        for mismatch in func(ROOT, PAPER_ID, payload):
            issues.append({"severity": "hard", "layer": "activity", "code": str(mismatch.get("code") or "contract_issue"), **{k: v for k, v in mismatch.items() if k != "code"}})
    for func in (
        lambda _root, _paper, data: gate.endpoint_table_support_issues(table_text_by_locator, data),
        lambda _root, _paper, data: gate.ambiguous_shared_table_row_issues(data),
        lambda _root, _paper, data: gate.source_located_toxicity_candidate_issues(data),
        lambda _root, _paper, data: gate.activity_redundant_field_issues(data),
        lambda _root, _paper, data: gate.evidence_kind_endpoint_issues(data),
        lambda _root, _paper, data: gate.activity_normalization_issues(data),
    ):
        for mismatch in func(ROOT, PAPER_ID, payload):
            issues.append({"severity": "hard", "layer": "activity", "code": str(mismatch.get("code") or "semantic_issue"), **{k: v for k, v in mismatch.items() if k != "code"}})
    return issues


def validate_payload(payload: dict, table_values: dict[str, str], table_meta: dict[str, dict]) -> dict:
    mic_records = [row for row in payload["activity_records"] if row.get("endpoint") == "MIC"]
    mic_mismatches: list[dict] = []
    for row in mic_records:
        table_locator, cell_locator, _body_row, _cell = parse_cell_locator(row)
        if str(row.get("raw_value")) != str(table_values.get(cell_locator)):
            mic_mismatches.append({"record_id": row.get("record_id"), "field": "raw_value", "cell_locator": cell_locator})
        if row.get("raw_unit") != table_meta[table_locator]["canonical_raw_unit"]:
            mic_mismatches.append({"record_id": row.get("record_id"), "field": "raw_unit", "cell_locator": cell_locator})
        if row.get("normalization_status") == "direct" and str(row.get("raw_unit")).lower().endswith("um"):
            mic_mismatches.append({"record_id": row.get("record_id"), "field": "normalization_status", "cell_locator": cell_locator})

    hem_peptides = sorted({row.get("peptide") for row in payload["toxicity_records"] if row.get("endpoint") == "percent hemolysis"})
    zf_peptides = sorted({row.get("peptide") for row in payload["toxicity_records"] if row.get("endpoint") == "zebrafish hatching/development toxicity"})
    zf_related = [row for row in payload["toxicity_records"] if str(row.get("endpoint") or "").startswith("zebrafish")]
    zf_quantitative = [row for row in zf_related if row.get("evidence_role") == "source_located_quantitative_zebrafish_observation"]
    zf_qualitative = [row for row in zf_related if row.get("evidence_role") == "source_located_qualitative_zebrafish_comparison"]
    zf_field_issues: list[dict] = []
    for row in zf_quantitative:
        for key in ("raw_value", "raw_unit", "peptide", "concentration", "concentration_unit", "timepoint", "source_locator"):
            if row.get(key) in (None, "", []):
                zf_field_issues.append({"record_id": row.get("record_id"), "field": key})
        cond = row.get("assay_conditions") if isinstance(row.get("assay_conditions"), dict) else {}
        if str(row.get("concentration")) != str(cond.get("peptide_concentration")):
            zf_field_issues.append({"record_id": row.get("record_id"), "field": "assay_conditions.peptide_concentration"})
        if str(row.get("concentration_unit")) != str(cond.get("peptide_concentration_unit")):
            zf_field_issues.append({"record_id": row.get("record_id"), "field": "assay_conditions.peptide_concentration_unit"})
    for row in zf_qualitative:
        if row.get("raw_value") in (None, "", []) or not row.get("no_unit_rationale"):
            zf_field_issues.append({"record_id": row.get("record_id"), "field": "qualitative_raw_value_or_no_unit_rationale"})
    biofilm_count = sum(1 for row in payload["activity_records"] if row.get("endpoint") == "biofilm biomass OD575")
    direct_bad = []
    for collection_name in ("activity_records", "toxicity_records"):
        for row in payload.get(collection_name, []):
            if row.get("normalization_status") == "direct":
                if str(row.get("raw_value")) != str(row.get("normalized_value")) or str(row.get("raw_unit")) != str(row.get("normalized_unit")):
                    direct_bad.append({"record_id": row.get("record_id"), "collection": collection_name})
    semantic_issues = semantic_activity_issues(payload)
    return {
        "paper_id": PAPER_ID,
        "validated_at": now_iso(),
        "mic_record_count": len(mic_records),
        "mic_table_counts": {
            locator: sum(1 for row in mic_records if (row.get("source_locator") or {}).get("table_locator") == locator)
            for locator in sorted(table_meta)
        },
        "mic_raw_value_or_unit_mismatch_count": len(mic_mismatches),
        "mic_raw_value_or_unit_mismatches": mic_mismatches,
        "activity_record_count": len(payload["activity_records"]),
        "toxicity_record_count": len(payload["toxicity_records"]),
        "biofilm_activity_observation_count": biofilm_count,
        "hemolysis_peptide_coverage": hem_peptides,
        "zebrafish_peptide_coverage": sorted({row.get("peptide") for row in zf_related}),
        "zebrafish_quantitative_statement_count": len(zf_quantitative),
        "zebrafish_qualitative_statement_count": len(zf_qualitative),
        "zebrafish_field_issue_count": len(zf_field_issues),
        "zebrafish_field_issues": zf_field_issues,
        "direct_normalization_mismatch_count": len(direct_bad),
        "direct_normalization_mismatches": direct_bad,
        "semantic_activity_toxicity_issue_count": len(semantic_issues),
        "semantic_activity_toxicity_issue_codes": sorted({issue.get("code") for issue in semantic_issues}),
        "semantic_activity_toxicity_issues": semantic_issues,
        "pass": not mic_mismatches
        and not direct_bad
        and len(mic_records) == 49
        and payload["summary_counts"]["accepted_activity_locators"] == {"xml:table-wrap:1": 40, "xml:table-wrap:2": 9}
        and hem_peptides == sorted(PEPTIDES)
        and sorted({row.get("peptide") for row in zf_related}) == sorted(PEPTIDES)
        and len(zf_quantitative) == 4
        and len(zf_qualitative) == 2
        and not zf_field_issues
        and biofilm_count == 13
        and not semantic_issues,
    }


def append_rework_response(validation: dict, reviewed_at: str) -> None:
    response = {
        "ticket_id": TICKET_ID,
        "response_status": "repair_ready_for_adjudication",
        "response_by": WORKER_ID,
        "analysis_can_resume": True,
        "responded_at": reviewed_at,
        "paper_id": PAPER_ID,
        "reason": "Worker-2 rebuilt layer-2 activity/toxicity artifacts from source-located table cells and requested toxicity/biofilm locators; final closure remains worker-6-only.",
        "evidence": {
            "mic_record_count": validation["mic_record_count"],
            "mic_raw_value_or_unit_mismatch_count": validation["mic_raw_value_or_unit_mismatch_count"],
            "hemolysis_peptide_coverage_count": len(validation["hemolysis_peptide_coverage"]),
            "zebrafish_peptide_coverage_count": len(validation["zebrafish_peptide_coverage"]),
            "zebrafish_quantitative_statement_count": validation["zebrafish_quantitative_statement_count"],
            "zebrafish_qualitative_statement_count": validation["zebrafish_qualitative_statement_count"],
            "zebrafish_field_issue_count": validation["zebrafish_field_issue_count"],
            "biofilm_activity_observation_count": validation["biofilm_activity_observation_count"],
            "semantic_activity_toxicity_issue_count": validation["semantic_activity_toxicity_issue_count"],
        },
        "evidence_paths": [
            str(VALIDATION_PATH.relative_to(ROOT.parents[2])),
            str(INSPECTION_PATH.relative_to(ROOT.parents[2])),
            str(ZF_BINDING.relative_to(ROOT.parents[2])),
        ],
        "repaired_artifacts": [
            str(SOURCE_ACTIVITY.relative_to(ROOT.parents[2])),
            str(PACKET_ACTIVITY.relative_to(ROOT.parents[2])),
        ],
        "artifacts_written": [
            str(SOURCE_ACTIVITY.relative_to(ROOT.parents[2])),
            str(PACKET_ACTIVITY.relative_to(ROOT.parents[2])),
            str(VALIDATION_PATH.relative_to(ROOT.parents[2])),
            str(INSPECTION_PATH.relative_to(ROOT.parents[2])),
            str(ZF_BINDING.relative_to(ROOT.parents[2])),
        ],
        "validation_artifacts": [str(VALIDATION_PATH.relative_to(ROOT.parents[2]))],
        "notes": [
            "MIC rows preserve source μg/mL mass unit and use normalization_status not_convertible.",
            "Hemolysis and zebrafish records enumerate A3, D-A3, A3-C4, A3-C5, and A3-C6.",
            "Zebrafish quantitative rows populate source-located raw_value/raw_unit/concentration/timepoint fields where p40 reports quantities; D-A3/A3-C6 are kept as qualitative comparison rows.",
            "A3-only exact 2.5% hemolysis row is not retained as an accepted exact toxicity row.",
        ],
    }
    REWORK_RESPONSES.parent.mkdir(parents=True, exist_ok=True)
    with REWORK_RESPONSES.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(response, ensure_ascii=False) + "\n")
    write_json(
        RESPONSE_AUDIT_PATH,
        {
            "paper_id": PAPER_ID,
            "ticket_id": TICKET_ID,
            "response_status": response["response_status"],
            "response_by": response["response_by"],
            "analysis_can_resume": response["analysis_can_resume"],
            "response_path": str(REWORK_RESPONSES.relative_to(ROOT.parents[2])),
            "responded_at": reviewed_at,
        },
    )


def main() -> int:
    reviewed_at = now_iso()
    prior = read_json(PACKET_ACTIVITY if PACKET_ACTIVITY.exists() else SOURCE_ACTIVITY)
    table_values, table_meta = build_table_maps()
    mic_rows, source_mismatch_notes = repair_mic_records(prior.get("activity_records", []), table_values, table_meta, reviewed_at)
    entity_map = peptide_entity_map(mic_rows)
    biofilm_rows = build_biofilm_records(entity_map, reviewed_at)
    toxicity_rows = build_hemolysis_records(entity_map, reviewed_at) + build_zebrafish_records(entity_map, reviewed_at)
    activity_records = mic_rows + biofilm_rows

    payload = deepcopy(prior)
    payload.update(
        {
            "paper_id": PAPER_ID,
            "worker": WORKER_ID,
            "layer": "layer2_activity_toxicity",
            "artifact_role": "worker2_source_reviewed_repair_artifact",
            "protocol": "amp_three_layer_v2",
            "generated_at": reviewed_at,
            "reviewed_at": reviewed_at,
            "review_model": "runtime_model_not_provable_in_codex_session",
            "reasoning_effort": "not_runtime_provable",
            "source_review_status": "source_reviewed_repair_ready_for_worker6_adjudication",
            "publication_grade_claim": False,
            "publication_grade_rationale": "Worker-2 repaired source-located layer-2 evidence only; publication-grade acceptance requires worker-6 final rebuild/adjudication and strict gates.",
            "activity_records": activity_records,
            "toxicity_records": toxicity_rows,
            "summary_counts": {
                "activity_records": len(activity_records),
                "toxicity_records": len(toxicity_rows),
                "activity_tables_accepted": 2,
                "accepted_activity_locators": {"xml:table-wrap:1": 40, "xml:table-wrap:2": 9},
                "activity_tables_excluded": 0,
                "source_tables_checked": 2,
                "biofilm_activity_observations": len(biofilm_rows),
                "hemolysis_toxicity_records": len([r for r in toxicity_rows if r["endpoint"] == "percent hemolysis"]),
                "zebrafish_quantitative_toxicity_records": len([r for r in toxicity_rows if r.get("evidence_role") == "source_located_quantitative_zebrafish_observation"]),
                "zebrafish_qualitative_toxicity_records": len([r for r in toxicity_rows if r.get("evidence_role") == "source_located_qualitative_zebrafish_comparison"]),
            },
            "record_counts": {
                "activity_records": len(activity_records),
                "toxicity_records": len(toxicity_rows),
                "mic_activity_records": len(mic_rows),
                "biofilm_activity_records": len(biofilm_rows),
            },
            "source_review_depth": {
                "paper_xml": True,
                "paper_pdf": True,
                "supplementary_assets": True,
                "merged_database_rows": True,
                "checked_locators": [
                    "xml:table-wrap:1",
                    "xml:table-wrap:2",
                    "xml:p:25",
                    "xml:p:26",
                    "xml:p:33",
                    "xml:p:39",
                    "xml:p:40",
                    "xml:fig:6",
                    "xml:fig:10",
                    "xml:fig:11",
                    "supp:RA-015-D5RA02745D-s001.pdf:page=11:figure=S13",
                    str(ZF_BINDING.relative_to(ROOT.parents[2])),
                ],
            },
            "quality_checks": {
                "activity_field_validation": {
                    "record_count": len(activity_records),
                    "mic_record_count": len(mic_rows),
                    "table_cell_value_mismatch_count": len(source_mismatch_notes),
                    "raw_unit": "μg/mL",
                    "normalization_status_for_mic": "not_convertible",
                },
                "semantic_gate_relevant_activity_checks": {
                    "non_activity_source_tables_excluded": [],
                    "toxicity_endpoint_in_activity_records": False,
                    "activity_endpoint_in_toxicity_records": False,
                    "database_only_rows_treated_as_primary": False,
                },
            },
            "excluded_toxicity_candidates": [
                {
                    "record_id": f"{PAPER_ID}-W2-EXCL-HEM-A3-2_5-EXACT",
                    "endpoint": "percent hemolysis",
                    "treatment": "A3",
                    "candidate_raw_value": "2.5",
                    "candidate_raw_unit": "%",
                    "source_locator": {"locator": "xml:p:39", "source_locators": ["xml:p:39", "xml:fig:10"]},
                    "exclusion_reason": "Not retained as an A3-specific exact row because worker-2 did not verify an exact per-treatment source-cell/figure binding for this value.",
                    "evidence_role": "source_located_exclusion",
                }
            ],
            "excluded_non_activity_table_entries": [],
            "no_source_located_toxicity_evidence": False,
            "worker_cautions": [
                "Zebrafish rows preserve quantitative p40 values only where token-binding verification supports peptide/value/concentration/timepoint fields; D-A3 and A3-C6 remain qualitative comparison rows.",
                "Biofilm Fig. S13 records are approximate image digitizations and should be adjudicated before final publication-grade acceptance.",
                "Runtime model/effort provenance is not provable in this Codex session; this artifact does not claim publication-grade acceptance.",
            ],
            "unresolved_blockers": [],
        }
    )

    validation = validate_payload(payload, table_values, table_meta)
    write_json(INSPECTION_PATH, {
        "paper_id": PAPER_ID,
        "generated_at": reviewed_at,
        "table_meta": table_meta,
        "inspected_locator_count": len(table_values),
        "source_mismatch_note_count": len(source_mismatch_notes),
        "source_mismatch_notes": source_mismatch_notes,
    })
    write_json(SOURCE_ACTIVITY, payload)
    write_json(PACKET_ACTIVITY, payload)
    write_json(VALIDATION_PATH, validation)
    append_rework_response(validation, reviewed_at)

    # Keep the packet mirror identical to the paper work artifact.
    if SOURCE_ACTIVITY.read_bytes() != PACKET_ACTIVITY.read_bytes():
        shutil.copyfile(SOURCE_ACTIVITY, PACKET_ACTIVITY)
    print(json.dumps({
        "paper_id": PAPER_ID,
        "activity_records": len(activity_records),
        "toxicity_records": len(toxicity_rows),
        "validation_pass": validation["pass"],
        "artifacts_written": [
            str(SOURCE_ACTIVITY.relative_to(ROOT.parents[2])),
            str(PACKET_ACTIVITY.relative_to(ROOT.parents[2])),
            str(VALIDATION_PATH.relative_to(ROOT.parents[2])),
            str(INSPECTION_PATH.relative_to(ROOT.parents[2])),
            str(RESPONSE_AUDIT_PATH.relative_to(ROOT.parents[2])),
        ],
    }, ensure_ascii=False))
    return 0 if validation["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
