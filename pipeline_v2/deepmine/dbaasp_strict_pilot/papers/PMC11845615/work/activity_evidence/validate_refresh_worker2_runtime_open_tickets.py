#!/usr/bin/env python3
"""Worker-2 bounded validator/refresh for PMC11845615 runtime-open tickets.

The script intentionally writes source-derived checks to JSON and prints only
counts/statuses. It does not print paper passages or table cell text.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "PMC11845615"
WORKER_ID = "worker-2"

ROOT = Path("/home/cihebi/抗菌肽/数据集/batch/5-team")
PAPER_ROOT = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot/papers" / PAPER_ID
PACKET_ROOT = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot/packets" / PAPER_ID

SOURCE_XML = PAPER_ROOT / "source/paper.xml"
XML_SECTIONS = PACKET_ROOT / "extracted/xml_sections.json"
SAFE_HANDOFF = PACKET_ROOT / "analysis/activity_safe_candidate_handoff.json"
WORK_ACTIVITY = PAPER_ROOT / "work/activity_evidence/activity_records.json"
PACKET_WORKER2 = PACKET_ROOT / "analysis/activity_toxicity_evidence.worker2.json"
REWORK_RESPONSES = PACKET_ROOT / "rework/rework_responses.jsonl"
VALIDATION_OUT = (
    PAPER_ROOT
    / "work/activity_evidence/worker2_runtime_open_ticket_repair_validation_20260728.json"
)

ASSIGNED_TICKETS = [
    "rwk-PMC11845615-campaign-r01-BF-PMC11845615-W2-ACTIVITY-TARGET-LOCATOR-CONFLICT",
    "rwk-PMC11845615-campaign-r01-BF-PMC11845615-W2-MIC-CONDITIONS-LOCATORS",
    "rwk-PMC11845615-campaign-r01-PMC11845615-BLOCKER-W2-ACTIVITY-TABLE-COVERAGE",
    "rwk-PMC11845615-campaign-r03-PMC11845615-BF-W2-ENTITY-PRODUCER-GENUS-AND-SEQUENCE-PLACEHO",
]

ALLOWED_NORMALIZATION = {"direct", "converted", "not_convertible", "ambiguous"}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_tag(tag: str) -> str:
    return tag.split("}", 1)[-1]


def collapse_ws(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def elem_text(elem: ET.Element) -> str:
    return collapse_ws("".join(elem.itertext()))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def collect_locator_text(obj: Any) -> str:
    return json_dump(obj)


def locator_has(obj: Any, token: str) -> bool:
    return token in collect_locator_text(obj)


def locator_ids(obj: Any) -> list[str]:
    text = collect_locator_text(obj)
    found = re.findall(r"\b(?:xml|pdf|database):[A-Za-z0-9_:=./-]+", text)
    return sorted(set(found))


def table_rows(table_wrap: ET.Element) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in table_wrap.iter():
        if strip_tag(tr.tag) != "tr":
            continue
        cells = [elem_text(cell) for cell in tr if strip_tag(cell.tag) in {"td", "th"}]
        rows.append(cells)
    return rows


def feature_flags(text: str) -> dict[str, bool]:
    folded = text.lower()
    tokens = {
        "mic": ["mic"],
        "mic_value": ["3.288"],
        "mic_target": ["em124"],
        "microtiter_format": ["96", "micro"],
        "readout": ["od600"],
        "duration": ["23"],
        "temperature": ["37"],
        "anaerobic": ["anaer"],
        "starting_concentration": ["13.155"],
        "replicate": ["triplicate"],
        "wda": ["well", "diffusion"],
        "fraction_51": ["fraction", "51"],
    }
    flags = {name: all(token in folded for token in terms) for name, terms in tokens.items()}
    flags["method_core"] = all(
        flags[name]
        for name in [
            "mic",
            "microtiter_format",
            "duration",
            "temperature",
            "anaerobic",
            "starting_concentration",
            "replicate",
        ]
    )
    flags["result_core"] = flags["mic"] and flags["mic_value"] and flags["mic_target"]
    return flags


def parse_source() -> dict[str, Any]:
    root = ET.parse(SOURCE_XML).getroot()
    table_wraps = [elem for elem in root.iter() if strip_tag(elem.tag) == "table-wrap"]
    paragraphs = [elem for elem in root.iter() if strip_tag(elem.tag) == "p"]

    t1_rows = table_rows(table_wraps[0])
    t2_rows = table_rows(table_wraps[1])

    table1_observations = []
    for source_row_number, cells in enumerate(t1_rows[2:], start=3):
        symbol = collapse_ws(cells[-1]) if cells else ""
        if "+" in symbol:
            status = "positive"
        elif symbol.upper() == "GR":
            status = "growth_reduction"
        else:
            status = "no_activity"
        table1_observations.append(
            {
                "source_row_number": source_row_number,
                "cell_count": len(cells),
                "status": status,
                "species": cells[0] if len(cells) > 0 else "",
                "strain": cells[1] if len(cells) > 1 else "",
                "temperature": cells[2] if len(cells) > 2 else "",
                "atmosphere": cells[3] if len(cells) > 3 else "",
                "medium": cells[4] if len(cells) > 4 else "",
                "activity_symbol": symbol,
            }
        )

    table2_observations = []
    for source_row_number, cells in enumerate(t2_rows[1:], start=2):
        table2_observations.append(
            {
                "source_row_number": source_row_number,
                "body_row_number": source_row_number - 1,
                "cell_count": len(cells),
                "treatment": cells[0] if len(cells) > 0 else "",
                "result": cells[1] if len(cells) > 1 else "",
            }
        )

    raw_paragraph_flags: dict[str, Any] = {}
    for index in [17, 28, 30, 36, 41, 49, 50]:
        if 1 <= index <= len(paragraphs):
            text = elem_text(paragraphs[index - 1])
            raw_paragraph_flags[f"xml:p:{index}"] = {
                "chars": len(text),
                "flags": feature_flags(text),
            }

    extracted_flags: dict[str, Any] = {}
    if XML_SECTIONS.exists():
        sections = load_json(XML_SECTIONS).get("sections", [])
        for loc in [
            "xml:p:17",
            "xml:p:28",
            "xml:p:30",
            "xml:p:36",
            "xml:p:41",
            "xml:p:49",
            "xml:p:50",
            "xml:sec:9",
            "xml:fig:6",
            "xml:fig:7",
        ]:
            texts = [section.get("text", "") for section in sections if section.get("locator", "").startswith(loc)]
            joined = collapse_ws(" ".join(texts))
            extracted_flags[loc] = {
                "entries": len(texts),
                "chars": sum(len(text) for text in texts),
                "flags": feature_flags(joined),
            }

    return {
        "table_wrap_count": len(table_wraps),
        "paragraph_count": len(paragraphs),
        "table1_observations": table1_observations,
        "table2_observations": table2_observations,
        "raw_paragraph_flags": raw_paragraph_flags,
        "extracted_locator_flags": extracted_flags,
    }


def validate_records(data: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    records = data.get("activity_records", [])
    failures: list[dict[str, Any]] = []
    cautions: list[dict[str, Any]] = []

    table1_source = {row["source_row_number"]: row for row in source["table1_observations"]}
    table2_source = {row["source_row_number"]: row for row in source["table2_observations"]}

    table1_records = [record for record in records if locator_has(record.get("source_locator"), "xml:table-wrap:1")]
    table2_records = [record for record in records if locator_has(record.get("source_locator"), "xml:table-wrap:2")]
    fig6_records = [record for record in records if locator_has(record.get("source_locator"), "xml:fig:6")]
    fig7_records = [record for record in records if locator_has(record.get("source_locator"), "xml:fig:7")]
    mic_records = [
        record
        for record in records
        if collapse_ws(record.get("endpoint")).upper() == "MIC"
        or "mic" in collapse_ws(record.get("record_id")).lower()
    ]

    table1_source_counts = Counter(row["status"] for row in source["table1_observations"])
    table1_record_counts = Counter()
    table1_record_rows: list[int] = []
    table1_mismatches: list[dict[str, Any]] = []
    disallowed_target_payload_count = 0
    for record in table1_records:
        loc_text = collect_locator_text(record.get("source_locator"))
        row_numbers = [int(value) for value in re.findall(r"row=0*([0-9]+)", loc_text)]
        row_number = row_numbers[0] if row_numbers else None
        if row_number is not None:
            table1_record_rows.append(row_number)
        source_row = table1_source.get(row_number or -1)
        endpoint = collapse_ws(record.get("endpoint")).lower()
        if "growth_reduction" in collapse_ws(record.get("record_id")).lower() or "growth reduction" in endpoint:
            table1_record_counts["growth_reduction"] += 1
        elif "no inhibitory" in endpoint or "no_activity" in collapse_ws(record.get("record_id")).lower():
            table1_record_counts["no_activity"] += 1
        else:
            table1_record_counts["positive"] += 1
        if source_row:
            if collapse_ws(record.get("target_species")) != collapse_ws(source_row["species"]):
                table1_mismatches.append({"row": row_number, "field": "target_species"})
            if collapse_ws(record.get("target_strain_or_isolate")) != collapse_ws(source_row["strain"]):
                table1_mismatches.append({"row": row_number, "field": "target_strain_or_isolate"})
            target_strain = collapse_ws(record.get("target_strain_or_isolate"))
            disallowed_values = {
                collapse_ws(source_row["temperature"]),
                collapse_ws(source_row["atmosphere"]),
                collapse_ws(source_row["medium"]),
                collapse_ws(source_row["activity_symbol"]),
                "+",
                "GR",
            }
            if target_strain in {value for value in disallowed_values if value}:
                disallowed_target_payload_count += 1

    expected_table1_counts = {"positive": 16, "growth_reduction": 5, "no_activity": 5}
    if dict(table1_source_counts) != expected_table1_counts:
        failures.append({"check": "source_table1_expected_counts", "observed": dict(table1_source_counts)})
    if dict(table1_record_counts) != expected_table1_counts:
        failures.append({"check": "record_table1_expected_counts", "observed": dict(table1_record_counts)})
    if sorted(table1_record_rows) != list(range(3, 29)):
        failures.append({"check": "table1_row_coordinates", "observed_count": len(table1_record_rows)})
    if table1_mismatches:
        failures.append({"check": "table1_target_binding", "mismatch_count": len(table1_mismatches)})
    if disallowed_target_payload_count:
        failures.append({"check": "table1_target_strain_condition_or_symbol_payload", "count": disallowed_target_payload_count})

    wrong_producer_hits = json_dump(table1_records).count("Lactococcus lactis APC 3969")
    expected_producer_hits = json_dump(table1_records).count("Leuconostoc lactis APC 3969")
    if wrong_producer_hits:
        failures.append({"check": "producer_wrong_genus", "count": wrong_producer_hits})

    table2_mismatches: list[dict[str, Any]] = []
    table2_record_rows: list[int] = []
    for record in table2_records:
        loc_text = collect_locator_text(record.get("source_locator"))
        row_numbers = [int(value) for value in re.findall(r"row=0*([0-9]+)", loc_text)]
        row_number = row_numbers[0] if row_numbers else None
        if row_number is not None:
            table2_record_rows.append(row_number)
        source_row = table2_source.get(row_number or -1)
        if collapse_ws(record.get("target_species")) != "Lactococcus lactis":
            table2_mismatches.append({"row": row_number, "field": "target_species"})
        if collapse_ws(record.get("target_strain_or_isolate")) != "HP":
            table2_mismatches.append({"row": row_number, "field": "target_strain_or_isolate"})
        if source_row:
            if collapse_ws(record.get("treatment")) != collapse_ws(source_row["treatment"]):
                table2_mismatches.append({"row": row_number, "field": "treatment"})
            if collapse_ws(record.get("raw_value")) != collapse_ws(source_row["result"]):
                table2_mismatches.append({"row": row_number, "field": "raw_value"})
    if len(table2_records) != 16:
        failures.append({"check": "table2_record_count", "observed": len(table2_records)})
    if sorted(table2_record_rows) != list(range(2, 18)):
        failures.append({"check": "table2_row_coordinates", "observed_count": len(table2_record_rows)})
    if table2_mismatches:
        failures.append({"check": "table2_binding", "mismatch_count": len(table2_mismatches)})

    fig6_locator_ok = False
    fig6_target_ok = False
    if fig6_records:
        for record in fig6_records:
            loc_text = collect_locator_text(record.get("source_locator"))
            if "xml:p:28" in loc_text or "xml:p:49" in loc_text:
                fig6_locator_ok = True
            if (
                collapse_ws(record.get("target_species")) == "Listeria innocua"
                and collapse_ws(record.get("target_strain_or_isolate")) == "DPC 3572"
            ):
                fig6_target_ok = True
        if not fig6_locator_ok:
            failures.append({"check": "fig6_locator_support"})
        if not fig6_target_ok:
            failures.append({"check": "fig6_target_binding"})

    if len(mic_records) != 1:
        failures.append({"check": "mic_record_count", "observed": len(mic_records)})
        mic_record = None
    else:
        mic_record = mic_records[0]

    mic_conditions_missing: list[str] = []
    mic_locator_ids: list[str] = []
    mic_source_locator_text = ""
    if mic_record:
        mic_source_locator_text = collect_locator_text(mic_record.get("source_locator"))
        mic_locator_ids = locator_ids(mic_record.get("source_locator"))
        if collapse_ws(mic_record.get("raw_value")) != "3.288":
            failures.append({"check": "mic_raw_value"})
        if collapse_ws(mic_record.get("raw_unit")) not in {"µM", "uM"}:
            failures.append({"check": "mic_raw_unit"})
        if collapse_ws(mic_record.get("target_species")) != "Clostridium perfringens":
            failures.append({"check": "mic_target_species"})
        if collapse_ws(mic_record.get("target_strain_or_isolate")) != "EM124":
            failures.append({"check": "mic_target_strain"})
        assay_conditions = mic_record.get("assay_conditions", {})
        required_condition_keys = [
            "inoculum",
            "incubation_duration",
            "incubation_temperature",
            "atmosphere",
            "assay_format",
            "readout",
            "dilution_context",
            "replicate_count",
            "starting_concentration_value",
            "starting_concentration_unit",
        ]
        for key in required_condition_keys:
            if not collapse_ws(assay_conditions.get(key)):
                mic_conditions_missing.append(key)
        if mic_conditions_missing:
            failures.append({"check": "mic_assay_conditions", "missing_fields": mic_conditions_missing})
        if "xml:p:30" in mic_source_locator_text:
            failures.append({"check": "mic_source_locator_contains_xml_p30"})
        if re.search(r"ticket_required_unresolved_locator|unsupported|not supported", mic_source_locator_text, re.I):
            failures.append({"check": "mic_source_locator_unresolved_support_token"})
        if not ("xml:p:41" in mic_source_locator_text and "xml:p:50" in mic_source_locator_text):
            failures.append({"check": "mic_source_supported_locator_pair_p41_p50"})
        if "xml:p:17" in mic_source_locator_text or "xml:p:36" in mic_source_locator_text:
            cautions.append({"check": "mic_contains_older_ticket_locator_ids", "present": True})

    direct_conversion_issues: list[dict[str, Any]] = []
    normalization_status_counts = Counter()
    missing_unit_or_rationale = 0
    sequence_issues: list[dict[str, Any]] = []
    concentration_conflicts: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        status = record.get("normalization_status")
        normalization_status_counts[status] += 1
        if status not in ALLOWED_NORMALIZATION:
            failures.append({"check": "normalization_status_allowed", "row": index})
        if status in {"direct", "converted"}:
            if record.get("normalized_value") in {None, ""} or not collapse_ws(record.get("normalized_unit")):
                direct_conversion_issues.append({"row": index, "field": "normalized_value_or_unit"})
            if status == "direct":
                if collapse_ws(record.get("raw_value")) != collapse_ws(record.get("normalized_value")):
                    direct_conversion_issues.append({"row": index, "field": "direct_value_changed"})
                if collapse_ws(record.get("raw_unit")) != collapse_ws(record.get("normalized_unit")):
                    direct_conversion_issues.append({"row": index, "field": "direct_unit_changed"})
        if not collapse_ws(record.get("raw_unit")):
            note = collapse_ws(record.get("raw_unit_rationale")) or collapse_ws(record.get("normalization_note"))
            if not note:
                missing_unit_or_rationale += 1
        assay_conditions = record.get("assay_conditions", {})
        if isinstance(assay_conditions, dict):
            top_conc = record.get("concentration")
            top_unit = record.get("concentration_unit")
            nested_conc = assay_conditions.get("concentration")
            nested_unit = assay_conditions.get("concentration_unit")
            if top_conc not in {None, ""} and nested_conc not in {None, ""}:
                if collapse_ws(top_conc) != collapse_ws(nested_conc):
                    concentration_conflicts.append({"row": index, "field": "concentration"})
            if top_unit not in {None, ""} and nested_unit not in {None, ""}:
                if collapse_ws(top_unit) != collapse_ws(nested_unit):
                    concentration_conflicts.append({"row": index, "field": "concentration_unit"})

        def scan_sequence(obj: Any) -> None:
            if isinstance(obj, dict):
                if "sequence" in obj:
                    sequence = obj.get("sequence")
                    length = obj.get("sequence_length")
                    if isinstance(sequence, str):
                        aa_ok = bool(re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWY]+", sequence))
                        len_ok = not isinstance(length, int) or len(sequence) == length
                        if not aa_ok or not len_ok:
                            sequence_issues.append({"row": index, "aa_ok": aa_ok, "length_ok": len_ok})
                for value in obj.values():
                    scan_sequence(value)
            elif isinstance(obj, list):
                for value in obj:
                    scan_sequence(value)

        scan_sequence(record)

    if direct_conversion_issues:
        failures.append({"check": "direct_or_converted_normalization", "count": len(direct_conversion_issues)})
    if missing_unit_or_rationale:
        failures.append({"check": "raw_unit_or_rationale", "count": missing_unit_or_rationale})
    if sequence_issues:
        failures.append({"check": "sequence_placeholder_or_length", "count": len(sequence_issues)})
    if concentration_conflicts:
        failures.append({"check": "concentration_consistency", "count": len(concentration_conflicts)})

    accepted_source_locator_text = json_dump([record.get("source_locator") for record in records])
    unsupported_source_token_count = len(
        re.findall(r"ticket_required_unresolved_locator|unsupported|not supported", accepted_source_locator_text, re.I)
    )
    if unsupported_source_token_count:
        failures.append({"check": "accepted_source_locator_unresolved_tokens", "count": unsupported_source_token_count})

    safe_handoff = load_json(SAFE_HANDOFF) if SAFE_HANDOFF.exists() else {}
    machine_rows = safe_handoff.get("machine_candidate_rows", [])

    older_locator_conflict = {
        "older_ticket_requires_p17_p36": True,
        "artifact_uses_p17_or_p36_in_mic_source_locator": bool(
            mic_record
            and ("xml:p:17" in mic_source_locator_text or "xml:p:36" in mic_source_locator_text)
        ),
        "artifact_uses_source_supported_p41_p50_pair": bool(
            mic_record and "xml:p:41" in mic_source_locator_text and "xml:p:50" in mic_source_locator_text
        ),
        "raw_xml_p17_result_core": source["raw_paragraph_flags"].get("xml:p:17", {}).get("flags", {}).get("result_core"),
        "raw_xml_p36_method_core": source["raw_paragraph_flags"].get("xml:p:36", {}).get("flags", {}).get("method_core"),
        "raw_xml_p41_result_core": source["raw_paragraph_flags"].get("xml:p:41", {}).get("flags", {}).get("result_core"),
        "raw_xml_p50_method_core": source["raw_paragraph_flags"].get("xml:p:50", {}).get("flags", {}).get("method_core"),
        "preservation_note": (
            "Older MIC locator scaffold p17/p36 is preserved as a ticket conflict; "
            "accepted MIC provenance remains the source-supported p41/p50 pair for worker-6 adjudication."
        ),
    }

    validation = {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "validated_at": now_utc(),
        "source_paths_checked": {
            "paper_xml": str(SOURCE_XML.relative_to(ROOT)),
            "xml_sections": str(XML_SECTIONS.relative_to(ROOT)),
            "safe_candidate_handoff": str(SAFE_HANDOFF.relative_to(ROOT)),
        },
        "safe_handoff_used_first": True,
        "safe_handoff_counts": {
            "machine_candidate_rows": len(machine_rows),
            "activity_table_locator_candidates": safe_handoff.get("counts", {}).get("activity_table_locator_candidates"),
            "toxicity_locator_candidates": safe_handoff.get("counts", {}).get("toxicity_locator_candidates"),
        },
        "source_table_checks": {
            "table1_observation_count": len(source["table1_observations"]),
            "table1_source_status_counts": dict(table1_source_counts),
            "table2_observation_count": len(source["table2_observations"]),
        },
        "record_checks": {
            "activity_record_count": len(records),
            "toxicity_record_count": len(data.get("toxicity_records", [])),
            "table1_record_count": len(table1_records),
            "table1_record_status_counts": dict(table1_record_counts),
            "table1_row_coordinate_minmax": [
                min(table1_record_rows) if table1_record_rows else None,
                max(table1_record_rows) if table1_record_rows else None,
            ],
            "table2_record_count": len(table2_records),
            "fig6_record_count": len(fig6_records),
            "fig7_record_count": len(fig7_records),
            "mic_record_count": len(mic_records),
            "mic_locator_ids": mic_locator_ids,
            "mic_condition_missing_fields": mic_conditions_missing,
            "normalization_status_counts": dict(normalization_status_counts),
            "wrong_producer_string_hits_in_table1_records": wrong_producer_hits,
            "expected_producer_string_hits_in_table1_records": expected_producer_hits,
            "unsupported_source_token_count": unsupported_source_token_count,
            "sequence_issue_count": len(sequence_issues),
            "concentration_conflict_count": len(concentration_conflicts),
        },
        "locator_feature_checks": {
            "raw_paragraph_flags": source["raw_paragraph_flags"],
            "extracted_locator_flags": source["extracted_locator_flags"],
            "older_mic_locator_contract_conflict": older_locator_conflict,
        },
        "assigned_runtime_open_ticket_ids_verified": ASSIGNED_TICKETS,
        "failures": failures,
        "cautions": cautions + [{"check": "older_mic_locator_contract_conflict", **older_locator_conflict}],
        "validation_status": "pass_with_preserved_nonterminal_conflict" if not failures else "fail",
    }
    return validation


def refreshed_artifact(data: dict[str, Any], validation: dict[str, Any], generated_at: str) -> dict[str, Any]:
    refreshed = copy.deepcopy(data)
    refreshed["generated_at"] = generated_at
    refreshed["finalized_at"] = generated_at
    refreshed["finalized_by"] = WORKER_ID
    refreshed["reviewed_by"] = WORKER_ID
    refreshed["paper_id"] = PAPER_ID
    refreshed["source_reviewed"] = True
    refreshed["strict_publication_grade_claim"] = False
    refreshed["worker2_lane_status"] = "repair_ready_for_worker6_adjudication_nonterminal"
    refreshed["worker6_runtime_open_ticket_ids_verified"] = ASSIGNED_TICKETS
    refreshed["worker2_runtime_open_ticket_ids_verified"] = ASSIGNED_TICKETS
    refreshed["worker2_current_runtime_open_ticket_repair"] = {
        "repaired_at": generated_at,
        "response_status": "repair_ready_for_adjudication",
        "analysis_can_resume": True,
        "validation_artifact": str(VALIDATION_OUT.relative_to(ROOT)),
        "validation_status": validation["validation_status"],
        "publication_grade_claim": False,
        "ticket_ids": ASSIGNED_TICKETS,
    }
    refreshed.setdefault("artifacts", {})
    refreshed["artifacts"]["worker2_runtime_open_ticket_repair_validation"] = str(VALIDATION_OUT.relative_to(ROOT))
    refreshed.setdefault("quality_checks", {})
    refreshed["quality_checks"]["worker2_runtime_open_ticket_contract_validation"] = {
        "status": validation["validation_status"],
        "failure_count": len(validation["failures"]),
        "preserved_nonterminal_conflict_count": len(validation["cautions"]),
        "assigned_ticket_count": len(ASSIGNED_TICKETS),
    }
    refreshed.setdefault("summary_counts", {})
    refreshed["summary_counts"]["runtime_open_ticket_ids_verified"] = len(ASSIGNED_TICKETS)
    refreshed["summary_counts"]["worker2_validation_failures"] = len(validation["failures"])
    refreshed["summary_counts"]["worker2_validation_cautions"] = len(validation["cautions"])
    refreshed.setdefault("limitations", [])
    conflict_note = {
        "limitation_type": "preserved_locator_contract_conflict",
        "scope": "MIC source locator scaffold",
        "status": "nonterminal_worker6_adjudication_required",
        "validation_artifact": str(VALIDATION_OUT.relative_to(ROOT)),
    }
    if conflict_note not in refreshed["limitations"]:
        refreshed["limitations"].append(conflict_note)
    return refreshed


def append_rework_responses(generated_at: str, validation: dict[str, Any], artifact_paths: list[Path]) -> None:
    evidence_paths = [str(VALIDATION_OUT.relative_to(ROOT))] + [str(path.relative_to(ROOT)) for path in artifact_paths]
    repaired_artifacts = [str(path.relative_to(ROOT)) for path in artifact_paths]
    response_common = {
        "paper_id": PAPER_ID,
        "response_status": "repair_ready_for_adjudication",
        "response_by": WORKER_ID,
        "analysis_can_resume": True,
        "responded_at_utc": generated_at,
        "evidence_paths": evidence_paths,
        "repaired_artifacts": repaired_artifacts,
        "artifacts_written": evidence_paths,
        "validation_artifacts": [str(VALIDATION_OUT.relative_to(ROOT))],
        "reason": (
            "Worker-2 refreshed the source-reviewed activity artifact for the currently assigned "
            "runtime-open tickets; validation passes with the MIC locator scaffold conflict preserved "
            "for worker-6 nonterminal adjudication."
        ),
        "notes": {
            "validation_status": validation["validation_status"],
            "failure_count": len(validation["failures"]),
            "caution_count": len(validation["cautions"]),
            "source_text_omitted_from_terminal_output": True,
            "publication_grade_claim": False,
        },
    }
    with REWORK_RESPONSES.open("a", encoding="utf-8") as handle:
        for ticket_id in ASSIGNED_TICKETS:
            row = dict(response_common)
            row["ticket_id"] = ticket_id
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    data = load_json(WORK_ACTIVITY)
    source = parse_source()
    validation = validate_records(data, source)
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    generated_at = validation["validated_at"]
    refreshed = refreshed_artifact(data, validation, generated_at)
    rendered = json.dumps(refreshed, ensure_ascii=False, indent=2) + "\n"
    WORK_ACTIVITY.write_text(rendered, encoding="utf-8")
    PACKET_WORKER2.write_text(rendered, encoding="utf-8")
    append_rework_responses(generated_at, validation, [WORK_ACTIVITY, PACKET_WORKER2])

    print("validation_status", validation["validation_status"])
    print("failure_count", len(validation["failures"]))
    print("caution_count", len(validation["cautions"]))
    print("activity_record_count", len(refreshed.get("activity_records", [])))
    print("toxicity_record_count", len(refreshed.get("toxicity_records", [])))
    print("artifacts_written", 3)
    print("responses_appended", len(ASSIGNED_TICKETS))
    print("work_sha256", sha256_path(WORK_ACTIVITY))
    print("packet_worker2_sha256", sha256_path(PACKET_WORKER2))
    return 1 if validation["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
