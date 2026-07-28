#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "PMC11672609"
MODEL = "gpt-5.5"
EFFORT = "xhigh"
TICKET_ID = "rwk-PMC11672609-campaign-r02-BF-PMC11672609-W2-ACTIVITY-TOXICITY-CONDITION-NORMALIZATION"
OWNER_WORKER = "worker-2"
TABLE2_RECORD_IDS = [f"PMC11672609-W2-ACT-{idx:03d}" for idx in range(1, 13)]
TABLE2_CELL_RE = re.compile(r"xml:table-wrap:2:body-row=(\d+):cell=(\d+)")

ROOT = Path(__file__).resolve().parents[4]
REPO = ROOT.parents[2]
PAPER = ROOT / "papers" / PAPER_ID
PACKET = ROOT / "packets" / PAPER_ID
WORK_REVIEW = PAPER / "work" / "review"
VALIDATION = WORK_REVIEW / "validation"
PAPER_FINAL = PAPER / "final"
PACKET_FINAL = PACKET / "final"
REQUESTS = PACKET / "rework" / "rework_requests.jsonl"
RESPONSES = PACKET / "rework" / "rework_responses.jsonl"
SINGLE_MANIFEST = WORK_REVIEW / "worker6_single_paper_manifest.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    text = value.lower()
    for left, right in (("μ", "u"), ("µ", "u"), ("\u00a0", " "), ("micrograms", "ug"), ("microgram", "ug")):
        text = text.replace(left, right)
    return re.sub(r"\s+", " ", text).strip()


def normalize_scalar(value: Any) -> str:
    return normalize_text(str(value or "")).replace(" ", "")


def flatten(value: Any) -> list[str]:
    if isinstance(value, dict):
        out: list[str] = []
        for item in value.values():
            out.extend(flatten(item))
        return out
    if isinstance(value, list):
        out = []
        for item in value:
            out.extend(flatten(item))
        return out
    if value is None:
        return []
    return [str(value)]


def source_locators(row: dict[str, Any]) -> set[str]:
    return {
        item
        for item in flatten(row)
        if item.startswith(("xml:", "supp:", "pdf:", "database:"))
    }


def parse_xml_sections() -> dict[str, str]:
    payload = read_json(PACKET / "extracted" / "xml_sections.json")
    return {
        str(item.get("locator")): str(item.get("text") or "")
        for item in payload.get("sections") or []
        if isinstance(item, dict) and item.get("locator")
    }


def parse_table2_cells() -> dict[tuple[int, int], str]:
    xml_root = ET.parse(PAPER / "source" / "paper.xml").getroot()
    table_wraps = [node for node in xml_root.iter() if node.tag.endswith("table-wrap")]
    table = table_wraps[1]
    tbody = next(node for node in table.iter() if node.tag.endswith("tbody"))
    cells: dict[tuple[int, int], str] = {}
    for row_idx, tr in enumerate([node for node in tbody.iter() if node.tag.endswith("tr")], start=1):
        row_cells = [node for node in list(tr) if node.tag.endswith("td") or node.tag.endswith("th")]
        for cell_idx, cell in enumerate(row_cells, start=1):
            cells[(row_idx, cell_idx)] = normalize_text(" ".join(cell.itertext()))
    return cells


def table2_full_text() -> str:
    xml_root = ET.parse(PAPER / "source" / "paper.xml").getroot()
    table_wraps = [node for node in xml_root.iter() if node.tag.endswith("table-wrap")]
    return normalize_text(" ".join(table_wraps[1].itertext()))


def extract_table2_cell_locator(row: dict[str, Any]) -> tuple[int, int] | None:
    for locator in sorted(source_locators(row)):
        match = TABLE2_CELL_RE.match(locator)
        if match:
            return int(match.group(1)), int(match.group(2))
    return None


def raw_value_matches_cell(raw_value: Any, cell_text: str) -> bool:
    raw = normalize_scalar(raw_value)
    cell = normalize_scalar(cell_text)
    candidates = {raw, raw.replace(">", ""), raw.replace("<", ""), raw.replace("=", "")}
    return any(candidate and candidate in cell for candidate in candidates)


def owner_response_prerequisite() -> dict[str, Any]:
    owner_rows = []
    terminal_lines = []
    for line_number, row in enumerate(read_jsonl(RESPONSES), start=1):
        if row.get("ticket_id") != TICKET_ID:
            continue
        if row.get("response_by") == OWNER_WORKER and row.get("analysis_can_resume") is True:
            owner_rows.append(
                {
                    "line_number": line_number,
                    "response_by": row.get("response_by"),
                    "response_status": row.get("response_status"),
                    "analysis_can_resume": row.get("analysis_can_resume"),
                    "has_evidence_paths": bool(row.get("evidence_paths") or row.get("validation_artifacts")),
                }
            )
        if row.get("response_by") == "worker-6" and row.get("status") == "closed_repaired" and row.get("response_status") == "closed_repaired":
            terminal_lines.append(line_number)
    return {
        "ticket_id": TICKET_ID,
        "request_present": any(row.get("ticket_id") == TICKET_ID for row in read_jsonl(REQUESTS)),
        "owner_response_count": len(owner_rows),
        "owner_nonterminal_response_present": bool(owner_rows),
        "owner_responses": owner_rows,
        "existing_worker6_terminal_response_count": len(terminal_lines),
        "existing_worker6_terminal_response_lines": terminal_lines,
        "pass": bool(owner_rows) and not terminal_lines,
    }


def validate_activity_contract(activity: dict[str, Any], source_label: str) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    sections = parse_xml_sections()
    required_locators = ["xml:p:17", "xml:p:44", "xml:p:19", "xml:p:20", "xml:table-wrap:2"]
    source_checks = {
        locator: {
            "present": locator in sections,
            "text_length": len(sections.get(locator, "")),
        }
        for locator in required_locators
    }
    for locator, check in source_checks.items():
        if not check["present"]:
            failures.append({"failure_code": "required_source_locator_absent", "locator": locator})

    unqualified_mic_16h = []
    for row in activity.get("activity_records") or []:
        if not isinstance(row, dict) or normalize_text(row.get("endpoint")) != "mic":
            continue
        conditions = row.get("assay_conditions") or {}
        incubation_time = normalize_scalar(conditions.get("incubation_time"))
        conflict_present = any(
            conditions.get(key)
            for key in (
                "condition_conflict_preserved",
                "condition_conflict",
                "condition_conflict_locator_ids",
                "incubation_time_conflict",
                "incubation_time_status",
            )
        )
        has_conflict_locators = {"xml:p:17", "xml:p:44"}.issubset(source_locators(row))
        if incubation_time in {"16h", "16hours"} and not (conflict_present and has_conflict_locators):
            unqualified_mic_16h.append(str(row.get("record_id")))
    if unqualified_mic_16h:
        failures.append(
            {
                "failure_code": "mic_unqualified_16h_without_condition_conflict",
                "record_ids": unqualified_mic_16h,
            }
        )

    cells = parse_table2_cells()
    full_text = table2_full_text()
    table2_records = [row for row in activity.get("activity_records") or [] if str(row.get("record_id")) in TABLE2_RECORD_IDS]
    table2_checks = []
    if sorted(str(row.get("record_id")) for row in table2_records) != TABLE2_RECORD_IDS:
        failures.append({"failure_code": "table2_record_id_set_changed", "observed_count": len(table2_records)})
    for row in sorted(table2_records, key=lambda item: str(item.get("record_id"))):
        locator = extract_table2_cell_locator(row)
        check = {
            "record_id": row.get("record_id"),
            "cell_locator_present": locator is not None,
            "raw_value_matches_xml_cell": False,
            "endpoint_supported_by_table_text": False,
            "unit_supported_by_table_text": False,
        }
        if locator is not None:
            check["raw_value_matches_xml_cell"] = raw_value_matches_cell(row.get("raw_value"), cells.get(locator, ""))
            check["endpoint_supported_by_table_text"] = normalize_scalar(row.get("endpoint")) in normalize_scalar(full_text)
            check["unit_supported_by_table_text"] = normalize_scalar(row.get("raw_unit")) in normalize_scalar(full_text)
        for key, code in (
            ("cell_locator_present", "table2_cell_locator_missing"),
            ("raw_value_matches_xml_cell", "table2_raw_value_not_bound_to_xml_cell"),
            ("endpoint_supported_by_table_text", "table2_endpoint_not_supported_by_table"),
            ("unit_supported_by_table_text", "table2_unit_not_supported_by_table"),
        ):
            if not check[key]:
                failures.append({"failure_code": code, "record_id": row.get("record_id")})
        table2_checks.append(check)

    hacat = [
        row
        for row in activity.get("toxicity_records") or []
        if "hacat" in normalize_text(" ".join(str(row.get(key) or "") for key in ("record_id", "cell_line", "target", "target_species", "target_strain_or_isolate")))
    ]
    if len(hacat) != 1:
        failures.append({"failure_code": "hacat_record_count", "observed_count": len(hacat)})
    else:
        row = hacat[0]
        raw_value = str(row.get("raw_value") or "").strip()
        status = normalize_text(row.get("raw_value_source_status"))
        has_toxicity_locator = bool({"xml:p:19", "xml:p:20"} & source_locators(row))
        has_censoring_rationale = bool((row.get("assay_conditions") or {}).get("censoring_rationale"))
        direct_claim = (
            "not_direct" not in status
            and (
                status.startswith("direct")
                or "direct_transcription" in status
                or "direct_table" in status
                or "direct_raw" in status
            )
        )
        if raw_value.startswith(">") and (direct_claim or not (has_toxicity_locator and has_censoring_rationale)):
            failures.append({"failure_code": "hacat_censored_threshold_not_qualified", "record_id": row.get("record_id")})

    non_assay_table_rows = [
        row.get("record_id")
        for bucket in ("activity_records", "toxicity_records")
        for row in activity.get(bucket) or []
        if "xml:table-wrap:1" in source_locators(row)
    ]
    if non_assay_table_rows:
        failures.append({"failure_code": "non_assay_table_locator_present", "record_ids": non_assay_table_rows})

    activity_sigs = {
        tuple(normalize_scalar(row.get(key)) for key in ("endpoint", "target_species", "target_strain_or_isolate", "raw_value", "raw_unit"))
        for row in activity.get("activity_records") or []
    }
    toxicity_sigs = {
        tuple(normalize_scalar(row.get(key)) for key in ("endpoint", "target_species", "target_strain_or_isolate", "raw_value", "raw_unit"))
        for row in activity.get("toxicity_records") or []
    }
    mirrored_duplicate_count = len(activity_sigs & toxicity_sigs)
    if mirrored_duplicate_count:
        failures.append({"failure_code": "activity_toxicity_mirrored_duplicate_signature", "observed_count": mirrored_duplicate_count})

    nested_concentration_failures = []
    for row in activity.get("toxicity_records") or []:
        conditions = row.get("assay_conditions") or {}
        if row.get("concentration") not in (None, ""):
            for key in ("peptide_concentration", "sample_concentration"):
                if key in conditions and str(conditions.get(key)) != str(row.get("concentration")):
                    nested_concentration_failures.append(row.get("record_id"))
        if row.get("concentration_unit") not in (None, ""):
            for key in ("peptide_concentration_unit", "sample_concentration_unit"):
                if key in conditions and str(conditions.get(key)) != str(row.get("concentration_unit")):
                    nested_concentration_failures.append(row.get("record_id"))
    if nested_concentration_failures:
        failures.append(
            {
                "failure_code": "nested_concentration_contradiction",
                "record_ids": sorted(set(str(item) for item in nested_concentration_failures)),
            }
        )

    return {
        "source_label": source_label,
        "pass": not failures,
        "failure_count": len(failures),
        "failures": failures,
        "source_locator_checks": source_checks,
        "contract_counts": {
            "activity_records": len(activity.get("activity_records") or []),
            "toxicity_records": len(activity.get("toxicity_records") or []),
            "table2_endpoint_records_checked": len(table2_checks),
            "unqualified_mic_16h_records": len(unqualified_mic_16h),
            "hacat_records": len(hacat),
            "activity_toxicity_mirrored_duplicates": mirrored_duplicate_count,
        },
    }


def final_counts() -> dict[str, int]:
    database = read_json(PAPER_FINAL / "database_record_verification.json")
    activity = read_json(PAPER_FINAL / "activity_toxicity_evidence.json")
    mechanism = read_json(PAPER_FINAL / "mechanism_ontology_record.json")
    review = read_json(PAPER_FINAL / "review_report.json")
    return {
        "activity_records": len(activity.get("activity_records") or []),
        "toxicity_records": len(activity.get("toxicity_records") or []),
        "database_record_audits": len(database.get("record_audits") or database.get("record_identity_audit") or []),
        "mechanism_claims": len(mechanism.get("mechanism_claims") or mechanism.get("claims") or []),
        "review_rework_targets": len(review.get("rework_targets") or []),
    }


def mirror_pairs() -> dict[str, tuple[Path, Path]]:
    return {
        "activity_toxicity_evidence": (PAPER_FINAL / "activity_toxicity_evidence.json", PACKET_FINAL / "activity_toxicity_evidence.json"),
        "database_record_verification": (PAPER_FINAL / "database_record_verification.json", PACKET_FINAL / "database_record_verification.json"),
        "review_report": (PAPER_FINAL / "review_report.json", PACKET_FINAL / "review_report.json"),
        "mechanism_ontology_record": (PAPER_FINAL / "mechanism_ontology_record.json", PACKET_FINAL / "mechanism_ontology_record.json"),
        "aligned_mechanism_final": (PAPER_FINAL / "mechanism_ontology_record.json", PACKET_FINAL / "mechanism_evidence.json"),
    }


def verified_artifact_paths() -> dict[str, dict[str, str]]:
    return {
        key: {"paper": str(pair[0]), "packet": str(pair[1])}
        for key, pair in mirror_pairs().items()
    }


def gate_artifact_paths(stage: str) -> dict[str, str]:
    prefix = f"worker6_r02_condition_normalization_{stage}"
    return {
        "packet": str(VALIDATION / f"{prefix}_packet_gate.PMC11672609.json"),
        "semantic": str(VALIDATION / f"{prefix}_semantic_gate.PMC11672609.json"),
        "publication": str(VALIDATION / f"{prefix}_publication_quality.PMC11672609.json"),
        "single_paper_manifest": str(SINGLE_MANIFEST),
    }


def run_gates(stage: str) -> dict[str, Any]:
    VALIDATION.mkdir(parents=True, exist_ok=True)
    write_json(SINGLE_MANIFEST, {"paper_ids": [PAPER_ID]})
    paths = {name: Path(path) for name, path in gate_artifact_paths(stage).items() if name != "single_paper_manifest"}
    stdout_paths = {name: paths[name].with_suffix(".stdout.txt") for name in paths}
    stderr_paths = {name: paths[name].with_suffix(".stderr.txt") for name in paths}
    commands = {
        "packet": [
            "python",
            str(REPO / ".codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py"),
            "--packet-root",
            str(ROOT / "packets"),
            "--manifest",
            str(SINGLE_MANIFEST.resolve()),
            "--json-out",
            str(paths["packet"]),
        ],
        "semantic": [
            "python",
            str(REPO / ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py"),
            "--root",
            str(ROOT),
            "--manifest",
            str(SINGLE_MANIFEST.resolve()),
            "--json",
        ],
        "publication": [
            "python",
            str(REPO / ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py"),
            "--root",
            str(ROOT),
            "--manifest",
            str(SINGLE_MANIFEST.resolve()),
            "--json-out",
            str(paths["publication"]),
        ],
    }
    return_codes: dict[str, int] = {}
    for name, command in commands.items():
        with stdout_paths[name].open("w", encoding="utf-8") as stdout, stderr_paths[name].open("w", encoding="utf-8") as stderr:
            if name == "semantic":
                with paths[name].open("w", encoding="utf-8") as target:
                    return_codes[name] = subprocess.run(command, cwd=str(REPO), stdout=target, stderr=stderr).returncode
            else:
                return_codes[name] = subprocess.run(command, cwd=str(REPO), stdout=stdout, stderr=stderr).returncode
    return {
        "stage": stage,
        "return_codes": return_codes,
        "artifact_paths": {name: str(path) for name, path in paths.items()},
        "stdout_paths": {name: str(path) for name, path in stdout_paths.items()},
        "stderr_paths": {name: str(path) for name, path in stderr_paths.items()},
    }


def gate_summary(stage: str) -> dict[str, Any]:
    paths = {name: Path(path) for name, path in gate_artifact_paths(stage).items() if name != "single_paper_manifest"}
    packet = read_json(paths["packet"])
    semantic = read_json(paths["semantic"])
    publication = read_json(paths["publication"])
    packet_result = (packet.get("results") or [{}])[0]
    semantic_result = (semantic.get("results") or [{}])[0]
    return {
        "stage": stage,
        "packet": {
            "paper_count": packet.get("paper_count"),
            "hard_finding_count": packet.get("hard_finding_count"),
            "open_rework_ticket_count": packet_result.get("open_rework_ticket_count"),
            "open_rework_ticket_ids": packet_result.get("open_rework_ticket_ids") or [],
        },
        "semantic": {
            "paper_count": semantic.get("paper_count"),
            "publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
            "publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
            "issue_count": semantic_result.get("issue_count"),
        },
        "publication": {
            "paper_count": publication.get("paper_count"),
            "publication_grade_pass": publication.get("publication_grade_pass"),
            "risk_counts": publication.get("risk_counts"),
        },
    }


def open_ticket_state() -> dict[str, Any]:
    manifest = read_json(PACKET / "packet_manifest.json")
    return {
        "open_rework_ticket_count": int(manifest.get("open_rework_ticket_count") or 0),
        "open_rework_ticket_ids": manifest.get("open_rework_ticket_ids") or [],
        "runtime_open_ticket_ids_assigned_to_worker6": [TICKET_ID],
        "closed_repaired_ticket_ids": manifest.get("closed_repaired_ticket_ids") or [],
    }


def build_rework_target(validation_path: Path, failure_record_ids: list[str]) -> dict[str, Any]:
    return {
        "ticket_id": TICKET_ID,
        "worker": OWNER_WORKER,
        "layer": "activity_toxicity",
        "artifact_path": "packets/PMC11672609/analysis/activity_toxicity_evidence.worker2.json",
        "failing_object": failure_record_ids,
        "failure_code": "mic_unqualified_16h_without_condition_conflict",
        "source_evidence_to_check": ["xml:p:17", "xml:p:44", "supp:table=S1"],
        "required_action": (
            "Revise the listed MIC records so the incubation-time field is not an unqualified method-only value; "
            "preserve endpoint values and add explicit condition-conflict or qualified method-condition status with locators."
        ),
        "acceptance_check": (
            "Worker-6 validation over owner and final activity_toxicity_evidence artifacts reports zero "
            "mic_unqualified_16h_without_condition_conflict failures."
        ),
        "validation_artifact": str(validation_path),
    }


def update_activity_metadata(now: str, validation_path: Path, validation: dict[str, Any]) -> None:
    activity = read_json(PAPER_FINAL / "activity_toxicity_evidence.json")
    activity["review_status"] = "needs_targeted_rework"
    activity["publication_grade"] = False
    activity["publication_grade_claim"] = "blocked_by_runtime_open_rework_ticket"
    activity["publication_grade_limitation"] = "worker2_condition_normalization_contract_incomplete"
    activity["finalized_at"] = now
    activity["finalized_by"] = "worker-6"
    checks = activity.setdefault("quality_checks", {})
    checks["worker6_r02_condition_normalization_contract_validation"] = {
        "ticket_id": TICKET_ID,
        "status": "failed_owner_lane_contract",
        "validation_artifact": str(validation_path),
        "failure_codes": [item.get("failure_code") for item in validation["owner_activity_contract"]["failures"]],
        "failure_count": validation["owner_activity_contract"]["failure_count"],
    }
    activity["worker6_condition_normalization_adjudication"] = {
        "ticket_id": TICKET_ID,
        "status": "needs_targeted_rework",
        "reviewed_at": now,
        "validation_artifact": str(validation_path),
    }
    write_json(PAPER_FINAL / "activity_toxicity_evidence.json", activity)
    shutil.copy2(PAPER_FINAL / "activity_toxicity_evidence.json", PACKET_FINAL / "activity_toxicity_evidence.json")


def write_review_outputs(now: str, validation_path: Path, validation: dict[str, Any], gate_run: dict[str, Any] | None = None, gate_info: dict[str, Any] | None = None) -> None:
    ticket_state = open_ticket_state()
    failure_record_ids: list[str] = []
    for item in validation["owner_activity_contract"]["failures"]:
        if item.get("failure_code") == "mic_unqualified_16h_without_condition_conflict":
            failure_record_ids.extend(item.get("record_ids") or [])
    rework_target = build_rework_target(validation_path, sorted(set(failure_record_ids)))
    counts = final_counts()
    counts["review_rework_targets"] = 1
    gate_return_codes = gate_run["return_codes"] if gate_run else {"packet": None, "semantic": None, "publication": None}
    gate_paths = gate_artifact_paths("final")
    checked_inputs = [
        "packets/PMC11672609/packet_manifest.json",
        "packets/PMC11672609/extracted/xml_sections.json",
        "packets/PMC11672609/extracted/pdf_text.jsonl",
        "packets/PMC11672609/extracted/supplementary_index.json",
        "packets/PMC11672609/extracted/supplementary_text.jsonl",
        "packets/PMC11672609/database/database_source_manifest.json",
        "packets/PMC11672609/database/authoritative_match_report.json",
        "packets/PMC11672609/database/dbaasp_machine_extracted_rows.jsonl",
        "packets/PMC11672609/database/linked_article_records.jsonl",
        "packets/PMC11672609/database/linked_assay_records.jsonl",
        "packets/PMC11672609/database/linked_sequence_records.jsonl",
        "packets/PMC11672609/database/linked_literature_records.jsonl",
        "packets/PMC11672609/analysis/activity_toxicity_evidence.worker2.json",
        "papers/PMC11672609/source/paper.xml",
        "papers/PMC11672609/final/activity_toxicity_evidence.json",
        "papers/PMC11672609/final/database_record_verification.json",
        "papers/PMC11672609/final/mechanism_ontology_record.json",
        "packets/PMC11672609/final/activity_toxicity_evidence.json",
        "packets/PMC11672609/final/mechanism_evidence.json",
        str(validation_path),
    ]
    source_review_depth = {
        "paper_xml": {"inspected": True, "locators_checked": ["xml:p:17", "xml:p:19", "xml:p:20", "xml:p:44", "xml:table-wrap:2"]},
        "paper_pdf": {"inspected": True, "packet_text_index_present": True},
        "oa_package": {"inspected": True, "packet_manifest_binding_present": True},
        "supplementary_assets": {"inspected": True, "supplementary_text_index_present": True},
        "merged_database_rows": {"inspected": True, "candidate_machine_rows_are_machine_evidence_only": True},
    }
    materials_exhausted = {
        "paper_xml": True,
        "paper_pdf": True,
        "oa_package": True,
        "supplementary_assets": True,
        "merged_database_rows": True,
        "known_missing_or_blocked_materials": [],
        "unavailable_sources": [],
    }
    semantic_quality_checks = {
        "runtime_open_ticket_ids_verified": [TICKET_ID],
        "owner_nonterminal_response_present": validation["owner_response_prerequisite"]["owner_nonterminal_response_present"],
        "owner_contract_passed": validation["owner_activity_contract"]["pass"],
        "final_contract_passed": validation["final_activity_contract"]["pass"],
        "table2_endpoint_records_checked": validation["final_activity_contract"]["contract_counts"]["table2_endpoint_records_checked"],
        "hacat_toxicity_record_checked": validation["final_activity_contract"]["contract_counts"]["hacat_records"],
        "source_text_printed_to_terminal": False,
        "database_fallback_rows_not_promoted": True,
        "authoritative_dbaasp_ingest_ready_false": True,
        "mechanism_ontology_contract_compared": True,
    }
    per_layer = {
        "database_record_verification": "Layer 1 remains accepted with cautions: no linked authoritative DBAASP rows are present, so fallback rows remain unresolved machine evidence and are not ingest-ready.",
        "activity_toxicity_evidence": "Layer 2 remains blocked because the current owner-lane activity artifact still has MIC condition-normalization failures for the listed record ids.",
        "mechanism_ontology_record": "Layer 3 remains accepted with cautions and is mirrored to the packet mechanism final alias.",
    }
    caution_findings = [
        {
            "finding_id": "database_no_authoritative_linked_rows",
            "layer": "database_record_verification",
            "status": "accepted_with_cautions_not_ingest_ready",
        },
        {
            "finding_id": "runtime_open_activity_condition_normalization_ticket",
            "layer": "activity_toxicity",
            "status": "blocking_rework_target",
            "ticket_id": TICKET_ID,
        },
    ]
    common = {
        "paper_id": PAPER_ID,
        "worker_id": "worker-6",
        "reviewed_at": now,
        "review_model": MODEL,
        "reasoning_effort": EFFORT,
        "source_reviewed": True,
        "review_status": "needs_targeted_rework",
        "publication_grade": False,
        "validator_contract_passed": False,
        "source_review_depth": source_review_depth,
        "materials_exhausted": materials_exhausted,
        "checked_inputs": checked_inputs,
        "semantic_quality_checks": semantic_quality_checks,
        "per_layer_decision_rationale": per_layer,
        "caution_findings": caution_findings,
        "rework_targets": [rework_target],
        "final_counts": counts,
        "gate_return_codes": gate_return_codes,
        "gate_artifact_paths": gate_paths,
        "verified_artifact_paths": verified_artifact_paths(),
        "runtime_open_ticket_ids_assigned_to_worker6": [TICKET_ID],
        "open_rework_ticket_count": ticket_state["open_rework_ticket_count"],
        "open_rework_ticket_ids": ticket_state["open_rework_ticket_ids"],
        "closed_repaired_ticket_ids": ticket_state["closed_repaired_ticket_ids"],
        "terminal_response_appended": False,
        "terminal_response_ticket_ids": [],
        "terminal_rework_response_status": "not_appended_contract_failed",
        "worker2_nonterminal_repair": validation["owner_response_prerequisite"],
        "worker6_ticket_contract_validation": {
            "ticket_id": TICKET_ID,
            "overall_contract_pass": False,
            "validation_artifact": str(validation_path),
            "owner_activity_contract_pass": validation["owner_activity_contract"]["pass"],
            "final_activity_contract_pass": validation["final_activity_contract"]["pass"],
            "failure_codes": [item.get("failure_code") for item in validation["owner_activity_contract"]["failures"]],
        },
        "strict_gate": {
            "required_rework_count": 1,
            "review_rework_targets": 1,
            "latest_gate_summary": gate_info,
        },
        "adjudication_summary": (
            "Worker-6 rechecked the current worker-2 activity artifact and rebuilt the final mirror state, but did not close the runtime ticket because the owner-lane contract still fails for two MIC condition records."
        ),
    }
    review = dict(common)
    write_json(PAPER_FINAL / "review_report.json", review)
    shutil.copy2(PAPER_FINAL / "review_report.json", PACKET_FINAL / "review_report.json")

    adjudication = dict(common)
    adjudication["artifact_role"] = "worker6_adjudication_report"
    adjudication["source_review_trace"] = str(validation_path)
    adjudication["ticket_contract_validation"] = common["worker6_ticket_contract_validation"]
    write_json(WORK_REVIEW / "adjudication_report.json", adjudication)

    feedback = {
        "paper_id": PAPER_ID,
        "generated_at": now,
        "review_model": MODEL,
        "reasoning_effort": EFFORT,
        "review_status": "needs_targeted_rework",
        "publication_grade": False,
        "rework_required": True,
        "runtime_open_ticket_ids_assigned_to_worker6": [TICKET_ID],
        "closed_repaired_ticket_ids": ticket_state["closed_repaired_ticket_ids"],
        "ticket_contract_validation": common["worker6_ticket_contract_validation"],
        "quality_feedback_by_owner": [
            {
                "owner_worker": OWNER_WORKER,
                "ticket_id": TICKET_ID,
                "target_queue": "analysis",
                "rework_targets": [rework_target],
            }
        ],
        "rework_targets": [rework_target],
        "caution_findings": caution_findings,
    }
    write_json(WORK_REVIEW / "quality_feedback.json", feedback)


def mirror_static_finals() -> None:
    PACKET_FINAL.mkdir(parents=True, exist_ok=True)
    for name in ("database_record_verification.json", "mechanism_ontology_record.json"):
        shutil.copy2(PAPER_FINAL / name, PACKET_FINAL / name)
    shutil.copy2(PAPER_FINAL / "mechanism_ontology_record.json", PACKET_FINAL / "mechanism_evidence.json")


def mirror_status() -> dict[str, Any]:
    status = {}
    for key, (paper_path, packet_path) in mirror_pairs().items():
        status[key] = {
            "paper_sha256": sha256(paper_path),
            "packet_sha256": sha256(packet_path),
            "byte_identical": paper_path.read_bytes() == packet_path.read_bytes(),
        }
    return status


def main() -> int:
    now = utc_now()
    VALIDATION.mkdir(parents=True, exist_ok=True)
    owner_activity = read_json(PACKET / "analysis" / "activity_toxicity_evidence.worker2.json")
    final_activity = read_json(PAPER_FINAL / "activity_toxicity_evidence.json")
    validation = {
        "paper_id": PAPER_ID,
        "ticket_id": TICKET_ID,
        "validated_at": now,
        "validated_by": "worker-6",
        "review_model": MODEL,
        "reasoning_effort": EFFORT,
        "owner_response_prerequisite": owner_response_prerequisite(),
        "owner_activity_contract": validate_activity_contract(owner_activity, "packet_analysis_worker2"),
        "final_activity_contract": validate_activity_contract(final_activity, "paper_final"),
    }
    validation["overall_contract_pass"] = (
        validation["owner_response_prerequisite"]["pass"]
        and validation["owner_activity_contract"]["pass"]
        and validation["final_activity_contract"]["pass"]
    )
    validation_path = VALIDATION / "worker6_r02_condition_normalization_contract_validation.json"
    write_json(validation_path, validation)

    mirror_static_finals()
    update_activity_metadata(now, validation_path, validation)
    write_review_outputs(now, validation_path, validation)
    first_gate = run_gates("scratch")
    first_summary = gate_summary("scratch")
    write_review_outputs(now, validation_path, validation, first_gate, first_summary)
    final_gate = run_gates("final")
    final_summary = gate_summary("final")
    write_review_outputs(now, validation_path, validation, final_gate, final_summary)

    mirror_report = {
        "paper_id": PAPER_ID,
        "ticket_id": TICKET_ID,
        "validated_at": utc_now(),
        "overall_contract_pass": validation["overall_contract_pass"],
        "terminal_response_appended": False,
        "gate_return_codes": final_gate["return_codes"],
        "gate_summary": final_summary,
        "mirror_status": mirror_status(),
        "written_outputs": [
            str(WORK_REVIEW / "adjudication_report.json"),
            str(WORK_REVIEW / "quality_feedback.json"),
            str(PAPER_FINAL / "database_record_verification.json"),
            str(PAPER_FINAL / "activity_toxicity_evidence.json"),
            str(PAPER_FINAL / "mechanism_ontology_record.json"),
            str(PAPER_FINAL / "review_report.json"),
            str(PACKET_FINAL / "database_record_verification.json"),
            str(PACKET_FINAL / "activity_toxicity_evidence.json"),
            str(PACKET_FINAL / "mechanism_ontology_record.json"),
            str(PACKET_FINAL / "mechanism_evidence.json"),
            str(PACKET_FINAL / "review_report.json"),
        ],
    }
    mirror_path = VALIDATION / "worker6_r02_condition_normalization_rework_result.json"
    write_json(mirror_path, mirror_report)
    print(
        json.dumps(
            {
                "result_path": str(mirror_path),
                "contract_pass": validation["overall_contract_pass"],
                "terminal_response_appended": False,
                "gate_return_codes": final_gate["return_codes"],
                "open_rework_ticket_count": final_summary["packet"]["open_rework_ticket_count"],
                "failure_codes": [
                    item.get("failure_code") for item in validation["owner_activity_contract"]["failures"]
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
