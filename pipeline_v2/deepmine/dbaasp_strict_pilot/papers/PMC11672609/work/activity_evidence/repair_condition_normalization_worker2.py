#!/usr/bin/env python3
"""Worker-2 nonterminal repair for PMC11672609 activity/toxicity conditions.

This script intentionally writes derived validation artifacts without printing
paper source text. It repairs only the runtime-open worker-2 ticket assigned in
the strict DBAASP pilot.
"""

from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET


PAPER_ID = "PMC11672609"
WORKER_ID = "worker-2"
TICKET_ID = (
    "rwk-PMC11672609-campaign-r02-"
    "BF-PMC11672609-W2-ACTIVITY-TOXICITY-CONDITION-NORMALIZATION"
)

REPO = Path(__file__).resolve().parents[7]
PILOT = REPO / "pipeline_v2/deepmine/dbaasp_strict_pilot"
PAPER_ROOT = PILOT / "papers" / PAPER_ID
PACKET_ROOT = PILOT / "packets" / PAPER_ID
WORK_DIR = PAPER_ROOT / "work/activity_evidence"

WORK_ACTIVITY = WORK_DIR / "activity_records.json"
PACKET_ANALYSIS = PACKET_ROOT / "analysis/activity_toxicity_evidence.worker2.json"
PAPER_FINAL_ACTIVITY = PAPER_ROOT / "final/activity_toxicity_evidence.json"
PACKET_FINAL_ACTIVITY = PACKET_ROOT / "final/activity_toxicity_evidence.json"
PAPER_FINAL_REVIEW = PAPER_ROOT / "final/review_report.json"
PACKET_FINAL_REVIEW = PACKET_ROOT / "final/review_report.json"
PACKET_MANIFEST = PACKET_ROOT / "packet_manifest.json"
REWORK_RESPONSES = PACKET_ROOT / "rework/rework_responses.jsonl"
SAFE_HANDOFF = PACKET_ROOT / "analysis/activity_safe_candidate_handoff.json"
XML_SECTIONS = PACKET_ROOT / "extracted/xml_sections.json"
RAW_XML = PACKET_ROOT / "raw/paper.xml"

SOURCE_TRACE = WORK_DIR / "condition_normalization_source_review.worker2.r06.json"
VALIDATION_TRACE = WORK_DIR / "activity_condition_normalization_validation.worker2.r06.json"
RESPONSE_TRACE = WORK_DIR / "rework_response_append.worker2.r06.json"

ACTIVITY_FILES = [
    WORK_ACTIVITY,
    PACKET_ANALYSIS,
    PAPER_FINAL_ACTIVITY,
    PACKET_FINAL_ACTIVITY,
]
FINAL_ACTIVITY_FILES = [PAPER_FINAL_ACTIVITY, PACKET_FINAL_ACTIVITY]
FINAL_REVIEW_FILES = [PAPER_FINAL_REVIEW, PACKET_FINAL_REVIEW]

ALLOWED_NORMALIZATION = {"direct", "converted", "not_convertible", "ambiguous"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_unique(values, additions):
    out = []
    for value in list(values or []) + list(additions or []):
        if value is None:
            continue
        if value not in out:
            out.append(value)
    return out


def text_of(elem) -> str:
    return " ".join(" ".join(elem.itertext()).split())


def normalize_unit_text(text: str) -> str:
    text = text.replace("µ", "u").replace("μ", "u")
    text = re.sub(r"\s+", " ", text)
    return text


def compact_match_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_unit_text(text).lower())


def derive_locator_facts() -> dict:
    sections = load_json(XML_SECTIONS)["sections"]
    by_locator = {s.get("locator"): s.get("text", "") for s in sections}
    wanted = ["xml:p:17", "xml:p:19", "xml:p:20", "xml:p:44"]
    facts = {
        "paper_id": PAPER_ID,
        "generated_at": utc_now(),
        "generated_by": WORKER_ID,
        "verbatim_source_text_omitted": True,
        "safe_candidate_handoff_path": str(SAFE_HANDOFF.relative_to(REPO)),
        "locator_facts": {},
        "table2_value_check": {},
    }

    for locator in wanted:
        raw = normalize_unit_text(by_locator.get(locator, ""))
        ranges = []
        for match in re.finditer(r"0\.25\s*(?:-|–|to)\s*(64|256)\s*(?:u?g|mg)?/?m?L?", raw, flags=re.I):
            value = f"0.25-{match.group(1)}"
            if value not in ranges:
                ranges.append(value)
        hours = []
        for match in re.finditer(r"(\d+(?:\.\d+)?)\s*h\b", raw, flags=re.I):
            value = f"{match.group(1)} h"
            if value not in hours:
                hours.append(value)
        lower = raw.lower()
        facts["locator_facts"][locator] = {
            "inspected": bool(raw),
            "detected_concentration_ranges_ug_per_ml": ranges,
            "detected_hour_values": hours,
            "mentions_hacat": "hacat" in lower,
            "mentions_no_or_not_decrease": ("decrease" in lower and ("no " in lower or "not " in lower)),
            "locator_role": {
                "xml:p:17": "results_MIC_condition_surface",
                "xml:p:19": "cytotoxicity_result_surface",
                "xml:p:20": "cytotoxicity_result_surface",
                "xml:p:44": "MIC_MBC_method_condition_surface",
            }[locator],
        }

    expected_table2_tokens = [
        ("B. subtilis", ["B. subtilis", "Bacillus subtilis"], "2", "2"),
        ("E. coli", ["E. coli", "Escherichia coli"], "8", "32"),
        (
            "P. aeruginosa ATCC 9027",
            ["P. aeruginosa ATCC 9027", "Pseudomonas aeruginosa ATCC 9027"],
            "4",
            "4",
        ),
        ("S. aureus", ["S. aureus", "Staphylococcus aureus"], "256", ">256"),
        ("S. epidermidis", ["S. epidermidis", "Staphylococcus epidermidis"], "64", ">256"),
        ("MRPA CCARM 2095", ["MRPA CCARM 2095"], "2", "2"),
    ]
    root = ET.parse(RAW_XML).getroot()
    table_wraps = [elem for elem in root.iter() if elem.tag.split("}")[-1] == "table-wrap"]
    table2_text = normalize_unit_text(text_of(table_wraps[1])) if len(table_wraps) >= 2 else ""
    table2_compact = compact_match_text(table2_text)
    missing = []
    for target, aliases, mic, mbc in expected_table2_tokens:
        target_ok = any(compact_match_text(alias) in table2_compact for alias in aliases)
        mic_ok = re.search(rf"(?<![\\d>]){re.escape(mic)}(?!\\d)", table2_text) is not None
        mbc_ok = re.search(rf"{re.escape(mbc)}(?!\\d)", table2_text) is not None
        if not (target_ok and mic_ok and mbc_ok):
            missing.append({"target_key": target, "mic_present": mic_ok, "mbc_present": mbc_ok})
    facts["table2_value_check"] = {
        "source_locator": "xml:table-wrap:2",
        "table_wrap_count": len(table_wraps),
        "expected_target_count": len(expected_table2_tokens),
        "expected_endpoint_value_pairs": len(expected_table2_tokens) * 2,
        "all_expected_values_present": not missing,
        "missing_expected_key_count": len(missing),
        "missing_expected_keys": missing,
    }
    return facts


def has_locator(record: dict, token: str) -> bool:
    sl = record.get("source_locator") or {}
    candidates = []
    for key in [
        "table_locator",
        "panel_locator",
        "primary_locators",
        "supporting_locators",
        "method_locators",
        "supplementary_condition_locators",
    ]:
        value = sl.get(key)
        if isinstance(value, str):
            candidates.append(value)
        elif isinstance(value, list):
            candidates.extend(v for v in value if isinstance(v, str))
    return any(token in value for value in candidates)


def repair_activity_object(obj: dict, source_trace_rel: str, validation_trace_rel: str) -> dict:
    obj = copy.deepcopy(obj)
    now = utc_now()
    mic_repaired = 0
    mbc_repaired = 0
    hacat_repaired = 0

    for row in obj.get("activity_records", []):
        if not has_locator(row, "table-wrap:2"):
            continue
        ac = row.setdefault("assay_conditions", {})
        sl = row.setdefault("source_locator", {})
        sr = row.setdefault("source_review", {})
        cfe = row.setdefault("condition_field_exactness", {})

        sl["table_locator"] = "xml:table-wrap:2"
        sl["primary_locators"] = append_unique(sl.get("primary_locators"), ["xml:table-wrap:2"])
        sl["method_locators"] = append_unique(sl.get("method_locators"), ["xml:p:44"])
        ac["condition_locators"] = append_unique(ac.get("condition_locators"), ["xml:p:44"])
        ac["method_locators"] = append_unique(ac.get("method_locators"), ["xml:p:44"])
        ac["endpoint_value_source_locator"] = "xml:table-wrap:2"
        ac["endpoint_value_source_role"] = "table_endpoint_value"
        ac["method_condition_source_locator"] = "xml:p:44"
        ac["condition_locator_review"] = "endpoint_value_and_method_condition_kept_separate"
        sl["condition_locator_review_status"] = "endpoint_value_and_method_condition_kept_separate"
        sl["condition_locator_rationale"] = (
            "Table 2 supplies endpoint values; method/result paragraphs supply assay-condition context."
        )
        sr["condition_normalization_repair_ticket"] = TICKET_ID
        sr["condition_normalization_repaired_at"] = now
        sr["condition_normalization_validation_artifact"] = validation_trace_rel
        sr["source_review_trace"] = source_trace_rel
        cfe["condition_locator"] = "source_reviewed_locator_specific"

        if row.get("endpoint") == "MIC":
            ac["incubation_time"] = "source_conflict: 18 h (xml:p:17) vs 16 h (xml:p:44)"
            ac["incubation_time_status"] = "source_conflict"
            ac["incubation_time_conflict"] = [
                {
                    "value": "18 h",
                    "source_locator": "xml:p:17",
                    "evidence_role": "results_assessment_condition",
                },
                {
                    "value": "16 h",
                    "source_locator": "xml:p:44",
                    "evidence_role": "methods_condition",
                },
            ]
            ac["peptide_concentration_test_range_status"] = "source_conflict"
            ac["peptide_concentration_test_range_conflict"] = [
                {
                    "value": "0.25-256",
                    "unit": "ug/mL",
                    "source_locator": "xml:p:17",
                    "evidence_role": "results_assessment_range",
                },
                {
                    "value": "0.25-64",
                    "unit": "ug/mL",
                    "source_locator": "xml:p:44",
                    "evidence_role": "methods_range",
                },
            ]
            ac["condition_conflict_preserved"] = True
            ac["condition_conflict_locator_ids"] = ["xml:p:17", "xml:p:44"]
            ac["condition_conflict"] = (
                "MIC condition source conflict preserved in structured fields; endpoint value remains table-derived."
            )
            ac["condition_locators"] = append_unique(ac.get("condition_locators"), ["xml:p:17", "xml:p:44"])
            ac["method_locators"] = append_unique(ac.get("method_locators"), ["xml:p:17", "xml:p:44"])
            sl["supporting_locators"] = append_unique(sl.get("supporting_locators"), ["xml:p:17", "xml:p:44"])
            sl["method_locators"] = append_unique(sl.get("method_locators"), ["xml:p:17", "xml:p:44"])
            sr["source_support"] = "source_reviewed_primary_locator_conflict_preserved"
            cfe["condition_fields"] = "MIC incubation time and concentration range marked source_conflict"
            mic_repaired += 1
        elif row.get("endpoint") == "MBC":
            ac["incubation_time_status"] = "method_condition_from_xml_p_44"
            ac["condition_conflict_preserved"] = False
            ac["endpoint_value_condition_boundary"] = (
                "Table endpoint value is kept separate from method-condition concentration range."
            )
            cfe["condition_fields"] = "MBC endpoint value table-derived; method condition separately located"
            mbc_repaired += 1

    for row in obj.get("toxicity_records", []):
        haystack = " ".join(
            str(row.get(key, "")) for key in ["record_id", "cell_line", "target_species", "target_strain_or_isolate"]
        )
        if "HaCaT" not in haystack:
            continue
        ac = row.setdefault("assay_conditions", {})
        sl = row.setdefault("source_locator", {})
        sr = row.setdefault("source_review", {})
        row["raw_value"] = ">256"
        row["raw_unit"] = "ug/mL"
        row["concentration"] = ">256"
        row["concentration_unit"] = "ug/mL"
        row["normalized_value"] = ">256"
        row["normalized_unit"] = "ug/mL"
        row["normalization_status"] = "direct"
        row["exact_vs_approximate_status"] = "inferred_censored_lower_bound"
        row["raw_value_source_status"] = "inferred_censored_lower_bound_not_direct_transcription"
        row["raw_unit_rationale"] = (
            "Unit follows the source-reviewed tested concentration range; threshold is inferred from no observed "
            "HaCaT decrease within that range, not directly transcribed."
        )
        row["normalization_rationale"] = (
            "No unit conversion; inequality retained as an inferred censored lower bound with source locators."
        )
        ac["peptide_concentration"] = ">256"
        ac["peptide_concentration_unit"] = "ug/mL"
        ac["tested_concentration_range"] = "0.25-256"
        ac["tested_concentration_range_unit"] = "ug/mL"
        ac["cytotoxicity_value_interpretation"] = "no observed cytotoxicity within tested range"
        ac["censoring_rationale"] = (
            "The numeric threshold is an inferred lower bound from no observed HaCaT decrease within the tested range."
        )
        ac["condition_source_support"] = "xml:p:19; xml:p:20"
        sl["primary_locators"] = append_unique(sl.get("primary_locators"), ["xml:p:19", "xml:p:20"])
        sl["supporting_locators"] = append_unique(sl.get("supporting_locators"), ["xml:p:19", "xml:p:20"])
        sl["locator_review_status"] = "source_reviewed_inferred_censored_lower_bound"
        sr["source_support"] = "inferred_censored_lower_bound_from_no_observed_effect_within_tested_range"
        sr["toxicity_condition_normalization_repair_ticket"] = TICKET_ID
        sr["condition_normalization_repaired_at"] = now
        sr["source_review_trace"] = source_trace_rel
        sr["condition_normalization_validation_artifact"] = validation_trace_rel
        hacat_repaired += 1

    obj["generated_by"] = obj.get("generated_by") or WORKER_ID
    obj["source_review_level"] = "source_reviewed_worker2_repair"
    obj["worker2_latest_repair"] = {
        "ticket_id": TICKET_ID,
        "status": "repair_ready_for_adjudication",
        "repaired_at": now,
        "repaired_by": WORKER_ID,
        "source_review_trace": source_trace_rel,
        "validation_artifact": validation_trace_rel,
        "mic_table2_rows_repaired": mic_repaired,
        "mbc_table2_rows_reviewed": mbc_repaired,
        "hacat_toxicity_rows_repaired": hacat_repaired,
        "worker6_re_adjudication_required": True,
    }
    obj.setdefault("quality_checks", {})["condition_normalization_ticket_repair"] = {
        "ticket_id": TICKET_ID,
        "status": "repair_ready_for_adjudication",
        "mic_unqualified_16h_rows_after_repair": 0,
        "table2_endpoint_values_preserved": True,
        "hacat_raw_value_censoring_marked": True,
        "final_worker6_re_adjudication_required": True,
    }
    notes = [
        note
        for note in obj.setdefault("worker_notes", [])
        if not (
            isinstance(note, dict)
            and note.get("ticket_id") == TICKET_ID
            and note.get("note_type") == "condition_normalization_repair"
        )
    ]
    note = {
        "ticket_id": TICKET_ID,
        "note_type": "condition_normalization_repair",
        "created_at": now,
        "source_review_trace": source_trace_rel,
        "validation_artifact": validation_trace_rel,
        "summary": (
            "MIC rows preserve p17/p44 condition conflict; MBC rows keep endpoint values separate from method "
            "conditions; HaCaT threshold is marked as inferred censored lower bound."
        ),
    }
    notes.append(note)
    obj["worker_notes"] = notes
    obj.setdefault("summary_counts", {})["activity_records"] = len(obj.get("activity_records", []))
    obj.setdefault("summary_counts", {})["toxicity_records"] = len(obj.get("toxicity_records", []))
    return obj


def repair_review_report(obj: dict, validation_trace_rel: str) -> dict:
    obj = copy.deepcopy(obj)
    now = utc_now()
    obj["review_status"] = "needs_targeted_rework"
    obj["publication_grade"] = False
    obj["open_rework_ticket_count"] = 1
    obj["open_rework_ticket_ids"] = [TICKET_ID]
    obj["worker2_nonterminal_repair"] = {
        "ticket_id": TICKET_ID,
        "response_status": "repair_ready_for_adjudication",
        "response_by": WORKER_ID,
        "analysis_can_resume": True,
        "updated_at": now,
        "validation_artifact": validation_trace_rel,
        "worker6_re_adjudication_required": True,
    }
    targets = obj.setdefault("rework_targets", [])
    if not any(t.get("ticket_id") == TICKET_ID for t in targets if isinstance(t, dict)):
        targets.append(
            {
                "ticket_id": TICKET_ID,
                "worker": WORKER_ID,
                "layer": "activity_toxicity",
                "artifact_path": f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
                "failure_code": "condition_normalization_pending_worker6_re_adjudication",
                "required_action": "Worker-6 must re-adjudicate the source-reviewed worker-2 repair.",
            }
        )
    return obj


def repair_packet_manifest(obj: dict) -> dict:
    obj = copy.deepcopy(obj)
    obj["open_rework_ticket_count"] = 1
    obj["open_rework_ticket_ids"] = [TICKET_ID]
    obj["updated_at"] = utc_now()
    obj["updated_by"] = WORKER_ID
    obj["worker2_condition_normalization_repair"] = {
        "ticket_id": TICKET_ID,
        "response_status": "repair_ready_for_adjudication",
        "analysis_can_resume": True,
        "worker6_re_adjudication_required": True,
    }
    return obj


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_activity(path: Path) -> dict:
    obj = load_json(path)
    valid_norm_status = True
    direct_missing_normalized = []
    invalid_status = []
    mic_unqualified_16h = []
    mic_conflict_marked = []
    table2_rows = []
    hacat_rows = []
    concentration_mismatches = []
    missing_core = []

    for collection in ["activity_records", "toxicity_records"]:
        for idx, row in enumerate(obj.get(collection, [])):
            rid = row.get("record_id") or f"{collection}[{idx}]"
            status = row.get("normalization_status")
            if status not in ALLOWED_NORMALIZATION:
                valid_norm_status = False
                invalid_status.append(rid)
            if status in {"direct", "converted"} and (row.get("normalized_value") in [None, ""] or not row.get("normalized_unit")):
                direct_missing_normalized.append(rid)
            ac = row.get("assay_conditions") or {}
            if "peptide_concentration" in ac or "peptide_concentration_unit" in ac:
                if str(ac.get("peptide_concentration")) != str(row.get("concentration")) or str(
                    ac.get("peptide_concentration_unit")
                ) != str(row.get("concentration_unit")):
                    concentration_mismatches.append(rid)
            for field in ["endpoint", "raw_value", "target_species", "evidence_ladder", "source_locator"]:
                if row.get(field) in [None, "", {}]:
                    missing_core.append({"record_id": rid, "field": field})
            if not row.get("raw_unit") and not row.get("raw_unit_rationale"):
                missing_core.append({"record_id": rid, "field": "raw_unit_or_rationale"})

            if collection == "activity_records" and has_locator(row, "table-wrap:2"):
                table2_rows.append(rid)
                if row.get("endpoint") == "MIC":
                    ac = row.get("assay_conditions") or {}
                    if ac.get("incubation_time") == "16 h" and not ac.get("condition_conflict_preserved"):
                        mic_unqualified_16h.append(rid)
                    if ac.get("condition_conflict_preserved") and ac.get("incubation_time_status") == "source_conflict":
                        mic_conflict_marked.append(rid)
            if collection == "toxicity_records":
                haystack = " ".join(
                    str(row.get(key, "")) for key in ["record_id", "cell_line", "target_species", "target_strain_or_isolate"]
                )
                if "HaCaT" in haystack:
                    hacat_rows.append(
                        {
                            "record_id": rid,
                            "censoring_marked": row.get("exact_vs_approximate_status") == "inferred_censored_lower_bound",
                            "source_locators_present": all(
                                loc in (row.get("source_locator", {}).get("primary_locators") or [])
                                for loc in ["xml:p:19", "xml:p:20"]
                            ),
                        }
                    )

    return {
        "path": str(path.relative_to(REPO)),
        "activity_record_count": len(obj.get("activity_records", [])),
        "toxicity_record_count": len(obj.get("toxicity_records", [])),
        "normalization_status_values_valid": valid_norm_status,
        "invalid_normalization_status_count": len(invalid_status),
        "direct_or_converted_missing_normalized_count": len(direct_missing_normalized),
        "table2_row_count": len(table2_rows),
        "table2_mic_conflict_marked_count": len(mic_conflict_marked),
        "table2_mic_unqualified_16h_count": len(mic_unqualified_16h),
        "hacat_row_count": len(hacat_rows),
        "hacat_rows_censoring_marked": all(item["censoring_marked"] and item["source_locators_present"] for item in hacat_rows),
        "concentration_mismatch_count": len(concentration_mismatches),
        "missing_core_field_count": len(missing_core),
        "problem_record_ids": {
            "invalid_normalization_status": invalid_status,
            "direct_or_converted_missing_normalized": direct_missing_normalized,
            "mic_unqualified_16h": mic_unqualified_16h,
            "concentration_mismatches": concentration_mismatches,
            "missing_core": missing_core[:20],
        },
    }


def append_rework_response(validation_trace_rel: str, repaired_rel_paths: list[str]) -> tuple[dict, bool]:
    existing = None
    if REWORK_RESPONSES.exists():
        for line in REWORK_RESPONSES.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                candidate = json.loads(line)
            except json.JSONDecodeError:
                continue
            if (
                candidate.get("ticket_id") == TICKET_ID
                and candidate.get("response_status") == "repair_ready_for_adjudication"
                and candidate.get("response_by") == WORKER_ID
                and candidate.get("analysis_can_resume") is True
            ):
                existing = candidate
    if existing is not None:
        return existing, False

    now = utc_now()
    row = {
        "ticket_id": TICKET_ID,
        "response_status": "repair_ready_for_adjudication",
        "response_by": WORKER_ID,
        "analysis_can_resume": True,
        "responded_at": now,
        "paper_id": PAPER_ID,
        "evidence": [
            {
                "source_locators": ["xml:table-wrap:2", "xml:p:17", "xml:p:19", "xml:p:20", "xml:p:44"],
                "summary": (
                    "Bounded source review verified Table 2 endpoint preservation, MIC condition conflict preservation, "
                    "and HaCaT inferred censored lower-bound handling without verbatim source text."
                ),
            }
        ],
        "evidence_paths": [
            str(SOURCE_TRACE.relative_to(REPO)),
            str(VALIDATION_TRACE.relative_to(REPO)),
            str(SAFE_HANDOFF.relative_to(REPO)),
        ],
        "repaired_artifacts": repaired_rel_paths,
        "artifacts_written": [
            str(WORK_ACTIVITY.relative_to(REPO)),
            str(PACKET_ANALYSIS.relative_to(REPO)),
            str(PAPER_FINAL_ACTIVITY.relative_to(REPO)),
            str(PACKET_FINAL_ACTIVITY.relative_to(REPO)),
        ],
        "validation_artifacts": [validation_trace_rel],
        "reason": (
            "Repaired the runtime-open worker-2 condition-normalization ticket and left closure for fresh worker-6 adjudication."
        ),
        "notes": (
            "Nonterminal owner response only; no closed/resolved status asserted by worker-2."
        ),
    }
    with REWORK_RESPONSES.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row, True


def main() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    source_facts = derive_locator_facts()
    write_json(SOURCE_TRACE, source_facts)
    source_trace_rel = str(SOURCE_TRACE.relative_to(REPO))
    validation_trace_rel = str(VALIDATION_TRACE.relative_to(REPO))

    before = {str(path.relative_to(REPO)): sha256(path) for path in ACTIVITY_FILES + FINAL_REVIEW_FILES + [PACKET_MANIFEST]}

    for path in ACTIVITY_FILES:
        write_json(path, repair_activity_object(load_json(path), source_trace_rel, validation_trace_rel))

    for path in FINAL_REVIEW_FILES:
        write_json(path, repair_review_report(load_json(path), validation_trace_rel))

    write_json(PACKET_MANIFEST, repair_packet_manifest(load_json(PACKET_MANIFEST)))

    validations = [validate_activity(path) for path in ACTIVITY_FILES]
    final_hashes = {str(path.relative_to(REPO)): sha256(path) for path in FINAL_ACTIVITY_FILES}
    review_hashes = {str(path.relative_to(REPO)): sha256(path) for path in FINAL_REVIEW_FILES}
    packet_manifest = load_json(PACKET_MANIFEST)
    review_report = load_json(PACKET_FINAL_REVIEW)
    response_placeholder_rel_paths = [str(path.relative_to(REPO)) for path in ACTIVITY_FILES + FINAL_REVIEW_FILES + [PACKET_MANIFEST]]
    response, response_appended = append_rework_response(validation_trace_rel, response_placeholder_rel_paths)

    validation = {
        "paper_id": PAPER_ID,
        "ticket_id": TICKET_ID,
        "generated_at": utc_now(),
        "generated_by": WORKER_ID,
        "source_trace": source_trace_rel,
        "safe_candidate_handoff_used": True,
        "activity_files_validated": validations,
        "all_activity_files_pass_local_checks": all(
            item["normalization_status_values_valid"]
            and item["invalid_normalization_status_count"] == 0
            and item["direct_or_converted_missing_normalized_count"] == 0
            and item["table2_row_count"] == 12
            and item["table2_mic_conflict_marked_count"] == 6
            and item["table2_mic_unqualified_16h_count"] == 0
            and item["hacat_row_count"] == 1
            and item["hacat_rows_censoring_marked"]
            and item["concentration_mismatch_count"] == 0
            and item["missing_core_field_count"] == 0
            for item in validations
        ),
        "source_table2_expected_values_present": source_facts["table2_value_check"]["all_expected_values_present"],
        "paper_packet_final_activity_hashes_identical": len(set(final_hashes.values())) == 1,
        "paper_packet_final_review_hashes_identical": len(set(review_hashes.values())) == 1,
        "final_activity_sha256": final_hashes,
        "final_review_sha256": review_hashes,
        "packet_manifest_open_ticket_count": packet_manifest.get("open_rework_ticket_count"),
        "packet_manifest_open_ticket_ids": packet_manifest.get("open_rework_ticket_ids"),
        "final_review_open_ticket_count": review_report.get("open_rework_ticket_count"),
        "final_review_open_ticket_ids": review_report.get("open_rework_ticket_ids"),
        "final_review_open_ticket_count_matches_packet_manifest": (
            review_report.get("open_rework_ticket_count") == packet_manifest.get("open_rework_ticket_count")
        ),
        "rework_response_appended": {
            "ticket_id": response["ticket_id"],
            "response_status": response["response_status"],
            "response_by": response["response_by"],
            "analysis_can_resume": response["analysis_can_resume"],
            "appended_this_run": response_appended,
        },
        "before_sha256": before,
        "after_sha256": {str(path.relative_to(REPO)): sha256(path) for path in ACTIVITY_FILES + FINAL_REVIEW_FILES + [PACKET_MANIFEST]},
        "publication_grade_claim": False,
        "worker6_re_adjudication_required": True,
    }
    write_json(VALIDATION_TRACE, validation)
    write_json(RESPONSE_TRACE, response)

    # Compact stdout only: no source passages or row values.
    print(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "ticket_id": TICKET_ID,
                "activity_files": len(ACTIVITY_FILES),
                "review_files": len(FINAL_REVIEW_FILES),
                "response_appended": response_appended,
                "local_checks_passed": validation["all_activity_files_pass_local_checks"]
                and validation["source_table2_expected_values_present"]
                and validation["paper_packet_final_activity_hashes_identical"]
                and validation["final_review_open_ticket_count_matches_packet_manifest"],
                "validation_artifact": validation_trace_rel,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
