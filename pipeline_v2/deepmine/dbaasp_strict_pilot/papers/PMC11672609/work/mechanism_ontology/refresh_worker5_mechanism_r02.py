#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "PMC11672609"
WORKER_ID = "worker-5"
MODEL = "gpt-5.5"
EFFORT = "xhigh"
TICKET_ID = "rwk-PMC11672609-campaign-r02-BF-W5-MECHANISM-FINAL-SUPPLEMENT-CAUTION-STALE"
STALE_CAUTION_CODE = "packet_supplementary_text_empty"
DIRECT_CLAIM_ID = "mech-PMC11672609-001"

ROOT = Path(__file__).resolve().parents[4]
PAPER_ROOT = ROOT / "papers" / PAPER_ID
PACKET_ROOT = ROOT / "packets" / PAPER_ID
WORK_DIR = PAPER_ROOT / "work" / "mechanism_ontology"

WORK_MECH = WORK_DIR / "mechanism_evidence.json"
PACKET_ANALYSIS_MECH = PACKET_ROOT / "analysis" / "mechanism_evidence.worker5.json"
PAPER_FINAL_MECH = PAPER_ROOT / "final" / "mechanism_ontology_record.json"
PACKET_FINAL_MECH = PACKET_ROOT / "final" / "mechanism_ontology_record.json"
PACKET_FINAL_MECH_EVIDENCE = PACKET_ROOT / "final" / "mechanism_evidence.json"
REWORK_RESPONSES = PACKET_ROOT / "rework" / "rework_responses.jsonl"

SOURCE_SCAN = WORK_DIR / "mechanism_source_scan.worker5.r02.json"
VALIDATION = WORK_DIR / "mechanism_repair_validation.worker5.r02.json"

REQUIRED_SUPP_LOCATORS = [
    "supp:antibiotics-3288224-supplementary.pdf:page=3:fig=S2",
    "supp:antibiotics-3288224-supplementary.pdf:page=4:fig=S3",
    "supp:antibiotics-3288224-supplementary.pdf:page=7-8:table=S2",
]

PATTERNS = {
    "direct_membrane_potential": [
        r"disc3",
        r"membrane\s+potential",
        r"depolar",
    ],
    "biofilm_phenotype": [
        r"biofilm",
        r"mbec",
        r"crystal\s+violet",
    ],
    "rt_qpcr_transcription": [
        r"rt[- ]?qpcr",
        r"\bqpcr\b",
        r"primer",
        r"transcription",
        r"gene\s+expression",
    ],
    "computational": [
        r"docking",
        r"molecular\s+dynamics",
        r"simulation",
        r"alphafold",
        r"pdbsum",
        r"binding\s+energy",
    ],
    "morphology_or_microscopy": [
        r"\btem\b",
        r"\bsem\b",
        r"microscop",
        r"morpholog",
    ],
    "inferred_structure": [
        r"secondary\s+structure",
        r"hydrophobic",
        r"amphipath",
        r"charge",
        r"helix",
    ],
    "ros_phenotype": [
        r"\bros\b",
        r"reactive\s+oxygen",
    ],
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def flatten_strings(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for child in value.values():
            out.extend(flatten_strings(child))
    elif isinstance(value, list):
        for child in value:
            out.extend(flatten_strings(child))
    elif value is not None:
        out.append(str(value))
    return out


def locator_values(value: Any) -> list[str]:
    values: list[str] = []
    if isinstance(value, str):
        values.append(value)
    elif isinstance(value, list):
        for item in value:
            values.extend(locator_values(item))
    elif isinstance(value, dict):
        for key in ("source_locator", "source_locators", "locator", "locators", "id", "aliases", "locator_aliases"):
            if key in value:
                values.extend(locator_values(value[key]))
    return [v.strip() for v in values if isinstance(v, str) and v.strip()]


def collect_source_surfaces() -> tuple[dict[str, str], set[str], dict[str, Any]]:
    text_by_locator: dict[str, str] = {}
    locator_ids: set[str] = set()

    xml = read_json(PACKET_ROOT / "extracted" / "xml_sections.json")
    for row in xml.get("sections", []):
        loc = row.get("locator")
        if loc:
            locator_ids.add(loc)
            text_by_locator[loc] = str(row.get("text") or "")

    for row in read_jsonl(PACKET_ROOT / "extracted" / "pdf_text.jsonl"):
        loc = row.get("locator")
        if loc:
            locator_ids.add(loc)
            text_by_locator[loc] = str(row.get("text") or "")

    figure_captions = read_json(PACKET_ROOT / "extracted" / "figure_captions.json")
    figure_records = figure_captions.get("figures", [])
    for row in figure_records:
        loc = row.get("locator")
        if loc:
            locator_ids.add(loc)
            text_by_locator[loc] = str(row.get("text") or "")

    supp_text_rows = read_jsonl(PACKET_ROOT / "extracted" / "supplementary_text.jsonl")
    for row in supp_text_rows:
        locs = [row.get("locator"), *(row.get("locator_aliases") or [])]
        for loc in locs:
            if loc:
                locator_ids.add(loc)
                text_by_locator[loc] = str(row.get("text") or "")

    supp_tables = read_json(PACKET_ROOT / "extracted" / "supplementary_tables.json")
    table_records = supp_tables.get("tables", [])
    table_ids: list[str] = []
    table_row_counts: dict[str, int] = {}
    for table in table_records:
        table_id = str(table.get("table_id") or "")
        if table_id:
            table_ids.append(table_id)
            table_row_counts[table_id] = int(table.get("row_count") or 0)
        table_text = " ".join(flatten_strings(table.get("rows") or []))
        for loc in [table.get("locator"), table.get("page_locator"), *(table.get("locator_aliases") or [])]:
            if loc:
                locator_ids.add(loc)
                text_by_locator[loc] = table_text
        for row in table.get("rows") or []:
            for loc in locator_values(row):
                locator_ids.add(loc)
                text_by_locator.setdefault(loc, " ".join(flatten_strings(row)))

    locator_index = read_json(PACKET_ROOT / "locators" / "locator_index.json")
    for entry in locator_index.get("locators", []):
        for loc in locator_values(entry):
            locator_ids.add(loc)

    source_counts = {
        "xml_section_records": len(xml.get("sections", [])),
        "pdf_text_records": len(read_jsonl(PACKET_ROOT / "extracted" / "pdf_text.jsonl")),
        "figure_caption_records": len(figure_records),
        "supplementary_text_records": len(supp_text_rows),
        "supplementary_table_count": len(table_records),
        "supplementary_table_ids": sorted(table_ids),
        "supplementary_table_row_counts": table_row_counts,
        "locator_index_count": int(locator_index.get("locator_count") or len(locator_index.get("locators", []))),
        "linked_authoritative_rows": sum(
            len(read_jsonl(PACKET_ROOT / "database" / name))
            for name in (
                "linked_article_records.jsonl",
                "linked_assay_records.jsonl",
                "linked_sequence_records.jsonl",
                "linked_literature_records.jsonl",
            )
        ),
        "machine_candidate_rows": len(read_jsonl(PACKET_ROOT / "database" / "dbaasp_machine_extracted_rows.jsonl")),
    }
    return text_by_locator, locator_ids, source_counts


def pattern_groups_for_text(text: str) -> list[str]:
    hits: list[str] = []
    lowered = text.lower()
    for group, patterns in PATTERNS.items():
        if any(re.search(pattern, lowered, re.IGNORECASE) for pattern in patterns):
            hits.append(group)
    return hits


def build_source_scan(mechanism: dict[str, Any]) -> dict[str, Any]:
    text_by_locator, locator_ids, source_counts = collect_source_surfaces()
    global_counts: dict[str, int] = {key: 0 for key in PATTERNS}
    global_locator_hits: dict[str, list[str]] = {key: [] for key in PATTERNS}
    for loc, text in text_by_locator.items():
        for group in pattern_groups_for_text(text):
            global_counts[group] += 1
            global_locator_hits[group].append(loc)

    claim_summaries: list[dict[str, Any]] = []
    unresolved_all: list[str] = []
    unresolved_supp: list[str] = []
    for claim in mechanism.get("mechanism_claims") or []:
        locs = locator_values(claim.get("source_locator"))
        groups: set[str] = set()
        unresolved: list[str] = []
        for loc in locs:
            if loc not in locator_ids and loc not in text_by_locator:
                unresolved.append(loc)
                if loc.startswith("supp:"):
                    unresolved_supp.append(loc)
                continue
            if loc in text_by_locator:
                groups.update(pattern_groups_for_text(text_by_locator[loc]))
        unresolved_all.extend(unresolved)
        claim_summaries.append(
            {
                "claim_id": claim.get("claim_id"),
                "evidence_class": claim.get("evidence_class"),
                "direct_assay_types_present": bool(claim.get("direct_assay_types")),
                "source_locator_count": len(locs),
                "unresolved_source_locator_count": len(unresolved),
                "unresolved_supplementary_locator_count": sum(1 for loc in unresolved if loc.startswith("supp:")),
                "support_pattern_groups": sorted(groups),
            }
        )

    required_supp_resolution = {loc: loc in locator_ids for loc in REQUIRED_SUPP_LOCATORS}
    direct_claim_ids = [
        claim.get("claim_id")
        for claim in mechanism.get("mechanism_claims") or []
        if claim.get("evidence_class") == "direct_mechanism"
    ]
    non_direct_bad_groups = []
    for summary in claim_summaries:
        groups = set(summary["support_pattern_groups"])
        if summary["evidence_class"] == "direct_mechanism":
            continue
        if groups.intersection({"biofilm_phenotype", "rt_qpcr_transcription", "computational"}):
            non_direct_bad_groups.append(
                {
                    "claim_id": summary["claim_id"],
                    "evidence_class": summary["evidence_class"],
                    "support_pattern_groups": sorted(groups.intersection({"biofilm_phenotype", "rt_qpcr_transcription", "computational"})),
                    "promoted_to_direct": False,
                }
            )

    return {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "review_model": MODEL,
        "reasoning_effort": EFFORT,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_text_printed_to_terminal": False,
        "source_text_or_table_excerpt_in_artifact": False,
        "inputs_reopened": {
            "xml_sections": str(PACKET_ROOT / "extracted" / "xml_sections.json"),
            "pdf_text": str(PACKET_ROOT / "extracted" / "pdf_text.jsonl"),
            "supplementary_text": str(PACKET_ROOT / "extracted" / "supplementary_text.jsonl"),
            "supplementary_tables": str(PACKET_ROOT / "extracted" / "supplementary_tables.json"),
            "locator_index": str(PACKET_ROOT / "locators" / "locator_index.json"),
            "database_manifest": str(PACKET_ROOT / "database" / "database_source_manifest.json"),
        },
        "source_counts": source_counts,
        "pattern_group_locator_hit_counts": global_counts,
        "pattern_group_locator_samples": {key: values[:20] for key, values in global_locator_hits.items()},
        "claim_source_support": claim_summaries,
        "required_supplementary_locator_resolution": required_supp_resolution,
        "direct_claim_ids": direct_claim_ids,
        "non_direct_claims_with_non_direct_pattern_support": non_direct_bad_groups,
        "unresolved_source_locator_count": len(unresolved_all),
        "unresolved_supplementary_locator_count": len(unresolved_supp),
    }


def remove_stale_caution(payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    repaired = deepcopy(payload)
    old = repaired.get("material_gaps_or_cautions") or []
    new: list[Any] = []
    removed = 0
    for item in old:
        code = item.get("code") if isinstance(item, dict) else str(item)
        if code == STALE_CAUTION_CODE:
            removed += 1
            continue
        new.append(item)
    repaired["material_gaps_or_cautions"] = new
    return repaired, removed


def update_payload(payload: dict[str, Any], source_scan: dict[str, Any], validation_path: str, source_scan_path: str) -> dict[str, Any]:
    repaired, _ = remove_stale_caution(payload)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    source_counts = source_scan["source_counts"]

    repaired["review_model"] = MODEL
    repaired["reasoning_effort"] = EFFORT
    repaired["reviewed_at"] = now
    repaired["worker_id"] = WORKER_ID
    repaired.setdefault("source_review_depth", {})
    supp_depth = repaired["source_review_depth"].setdefault("supplementary_assets", {})
    supp_depth.update(
        {
            "inspected": True,
            "packet_supplementary_text_records": source_counts["supplementary_text_records"],
            "packet_supplementary_table_count": source_counts["supplementary_table_count"],
            "packet_supplementary_table_ids": source_counts["supplementary_table_ids"],
            "packet_supplementary_table_row_counts": source_counts["supplementary_table_row_counts"],
            "locator_index_required_supplementary_aliases_verified": all(
                source_scan["required_supplementary_locator_resolution"].values()
            ),
            "stale_empty_text_caution_removed": True,
        }
    )

    repaired.setdefault("quality_checks", {})
    repaired["quality_checks"].update(
        {
            "review_model_is_gpt55": repaired.get("review_model") == MODEL,
            "reasoning_effort_is_xhigh": repaired.get("reasoning_effort") == EFFORT,
            "packet_supplementary_text_nonempty": source_counts["supplementary_text_records"] > 0,
            "packet_supplementary_text_empty_caution_absent": not any(
                isinstance(item, dict) and item.get("code") == STALE_CAUTION_CODE
                for item in repaired.get("material_gaps_or_cautions", [])
            ),
            "all_supplementary_mechanism_locators_resolve": source_scan["unresolved_supplementary_locator_count"] == 0,
            "direct_mechanism_restricted_to_disc35_claim": source_scan["direct_claim_ids"] == [DIRECT_CLAIM_ID],
            "rt_qpcr_biofilm_and_computational_not_promoted_to_direct": True,
            "source_text_printed_to_terminal": False,
        }
    )

    repaired.setdefault("rework", {})
    repaired["rework"].update(
        {
            "runtime_open_ticket_ids_assigned_to_worker5": [TICKET_ID],
            "owner_repair_responses_appended": 1,
            "new_rework_requests_written": 0,
            "new_rework_request_paths": [],
        }
    )
    repaired.setdefault("scope_control", {})
    repaired["scope_control"].update(
        {
            "checkout_only": True,
            "internet_browsing_used": False,
            "paper_scope": PAPER_ID,
            "leader_preflight_contracts_supplied": 0,
            "leader_preflight_evidence_scaffolds_supplied": 0,
            "assigned_runtime_open_ticket_ids": [TICKET_ID],
            "ticket_response_appended": True,
        }
    )
    repaired.setdefault("lane_status", {})
    repaired["lane_status"].update(
        {
            "source_reviewed_complete": True,
            "needs_targeted_rework": False,
            "publication_grade_claim": False,
            "reason_publication_grade_not_claimed": "Worker-5 repaired the mechanism lane artifact for worker-6 adjudication; terminal publication-grade status remains worker-6 gated.",
        }
    )
    repaired["worker5_repair_provenance"] = {
        "ticket_id": TICKET_ID,
        "repair_status": "repair_ready_for_adjudication",
        "repaired_at_utc": now,
        "stale_caution_removed": STALE_CAUTION_CODE,
        "worker6_terminal_closure_required": True,
    }
    checked_inputs = list(repaired.get("checked_inputs") or [])
    for path in [
        str(PACKET_ROOT / "extracted" / "supplementary_text.jsonl"),
        str(PACKET_ROOT / "extracted" / "supplementary_tables.json"),
        str(PACKET_ROOT / "locators" / "locator_index.json"),
        source_scan_path,
        validation_path,
    ]:
        if path not in checked_inputs:
            checked_inputs.append(path)
    repaired["checked_inputs"] = checked_inputs
    validation_artifacts = list(repaired.get("validation_artifacts") or [])
    for path in [source_scan_path, validation_path]:
        if path not in validation_artifacts:
            validation_artifacts.append(path)
    repaired["validation_artifacts"] = validation_artifacts
    return repaired


def validate_payload(payload: dict[str, Any], source_scan: dict[str, Any], stale_removed: int) -> dict[str, Any]:
    claims = payload.get("mechanism_claims") or []
    required_fields = ["claim_id", "claim_text", "entity_scope", "evidence_class", "source_locator"]
    missing_required = []
    direct_without_assays = []
    non_direct_with_direct_assays = []
    valid_classes = {"direct_mechanism", "phenotype_supported", "inferred_mechanism", "computational_only", "unknown_or_not_tested"}
    invalid_classes = []
    for claim in claims:
        cid = claim.get("claim_id")
        missing = [field for field in required_fields if not claim.get(field)]
        if missing:
            missing_required.append({"claim_id": cid, "missing_fields": missing})
        if claim.get("evidence_class") not in valid_classes:
            invalid_classes.append({"claim_id": cid, "evidence_class": claim.get("evidence_class")})
        if claim.get("evidence_class") == "direct_mechanism" and not claim.get("direct_assay_types"):
            direct_without_assays.append(cid)
        if claim.get("evidence_class") != "direct_mechanism" and claim.get("direct_assay_types"):
            non_direct_with_direct_assays.append(cid)

    caution_codes = [
        item.get("code")
        for item in payload.get("material_gaps_or_cautions", [])
        if isinstance(item, dict)
    ]
    checks = {
        "review_model_exact": payload.get("review_model") == MODEL,
        "reasoning_effort_exact": payload.get("reasoning_effort") == EFFORT,
        "claim_count": len(claims),
        "all_claims_have_required_fields": not missing_required,
        "valid_evidence_classes": not invalid_classes,
        "direct_claim_ids_exact": source_scan["direct_claim_ids"] == [DIRECT_CLAIM_ID],
        "direct_claims_have_direct_assay_types": not direct_without_assays,
        "non_direct_claims_have_no_direct_assay_types": not non_direct_with_direct_assays,
        "rt_qpcr_biofilm_computational_not_promoted_to_direct": not any(
            summary["evidence_class"] == "direct_mechanism"
            and set(summary["support_pattern_groups"]).intersection({"rt_qpcr_transcription", "biofilm_phenotype", "computational"})
            for summary in source_scan["claim_source_support"]
            if summary["claim_id"] != DIRECT_CLAIM_ID
        ),
        "supplementary_text_records_nonzero": source_scan["source_counts"]["supplementary_text_records"] > 0,
        "supplementary_tables_present": source_scan["source_counts"]["supplementary_table_count"] >= 3,
        "required_supplementary_locators_resolve": all(source_scan["required_supplementary_locator_resolution"].values()),
        "all_mechanism_source_locators_resolve": source_scan["unresolved_source_locator_count"] == 0,
        "all_mechanism_supplementary_locators_resolve": source_scan["unresolved_supplementary_locator_count"] == 0,
        "stale_packet_supplementary_text_empty_caution_removed": STALE_CAUTION_CODE not in caution_codes and stale_removed >= 1,
        "source_text_printed_to_terminal": False,
        "source_text_or_table_excerpt_in_validation_artifact": False,
    }
    return {
        "paper_id": PAPER_ID,
        "worker_id": WORKER_ID,
        "review_model": MODEL,
        "reasoning_effort": EFFORT,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "ticket_id": TICKET_ID,
        "checks": checks,
        "missing_required_claim_fields": missing_required,
        "invalid_evidence_classes": invalid_classes,
        "direct_without_assays": direct_without_assays,
        "non_direct_with_direct_assays": non_direct_with_direct_assays,
        "remaining_caution_codes": caution_codes,
        "unresolved_source_locator_count": source_scan["unresolved_source_locator_count"],
        "unresolved_supplementary_locator_count": source_scan["unresolved_supplementary_locator_count"],
        "direct_claim_ids": source_scan["direct_claim_ids"],
        "source_counts": source_scan["source_counts"],
    }


def append_rework_response(validation: dict[str, Any], written_paths: list[str]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    response = {
        "ticket_id": TICKET_ID,
        "paper_id": PAPER_ID,
        "response_status": "repair_ready_for_adjudication",
        "response_by": WORKER_ID,
        "analysis_can_resume": True,
        "responded_at_utc": now,
        "reason": "Worker-5 re-opened current packet supplementary text, supplementary tables, locator index, and mechanism artifacts; removed the stale supplementary-empty caution and kept mechanism classes separated for worker-6 adjudication.",
        "evidence": {
            "source_reviewed_claim_count": validation["checks"]["claim_count"],
            "direct_claim_ids": validation["direct_claim_ids"],
            "supplementary_text_records": validation["source_counts"]["supplementary_text_records"],
            "supplementary_table_count": validation["source_counts"]["supplementary_table_count"],
            "stale_caution_removed": validation["checks"]["stale_packet_supplementary_text_empty_caution_removed"],
            "all_mechanism_supplementary_locators_resolve": validation["checks"]["all_mechanism_supplementary_locators_resolve"],
            "worker6_terminal_closure_required": True,
        },
        "evidence_paths": [
            str(PACKET_ROOT / "extracted" / "supplementary_text.jsonl"),
            str(PACKET_ROOT / "extracted" / "supplementary_tables.json"),
            str(PACKET_ROOT / "locators" / "locator_index.json"),
            str(SOURCE_SCAN),
            str(VALIDATION),
        ],
        "repaired_artifacts": written_paths,
        "artifacts_written": written_paths,
        "added_files": [str(SOURCE_SCAN), str(VALIDATION)],
        "validation_artifacts": [str(SOURCE_SCAN), str(VALIDATION)],
        "notes": "Nonterminal owner repair response only; worker-6 must re-adjudicate and may append terminal closure.",
    }
    REWORK_RESPONSES.parent.mkdir(parents=True, exist_ok=True)
    with REWORK_RESPONSES.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(response, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    base = read_json(WORK_MECH)
    source_scan = build_source_scan(base)
    repaired_base, stale_removed = remove_stale_caution(base)
    validation = validate_payload(repaired_base, source_scan, stale_removed)
    hard_checks = [
        "review_model_exact",
        "reasoning_effort_exact",
        "all_claims_have_required_fields",
        "valid_evidence_classes",
        "direct_claim_ids_exact",
        "direct_claims_have_direct_assay_types",
        "non_direct_claims_have_no_direct_assay_types",
        "rt_qpcr_biofilm_computational_not_promoted_to_direct",
        "supplementary_text_records_nonzero",
        "supplementary_tables_present",
        "required_supplementary_locators_resolve",
        "all_mechanism_source_locators_resolve",
        "all_mechanism_supplementary_locators_resolve",
        "stale_packet_supplementary_text_empty_caution_removed",
    ]
    failed = [name for name in hard_checks if not validation["checks"].get(name)]
    if failed:
        write_json(SOURCE_SCAN, source_scan)
        write_json(VALIDATION, validation)
        print(json.dumps({"status": "blocked", "failed_checks": failed, "validation_artifact": str(VALIDATION)}, ensure_ascii=False))
        return 1

    source_scan_path = str(SOURCE_SCAN)
    validation_path = str(VALIDATION)
    work_payload = update_payload(base, source_scan, validation_path, source_scan_path)
    final_payload = update_payload(read_json(PAPER_FINAL_MECH), source_scan, validation_path, source_scan_path)

    write_json(SOURCE_SCAN, source_scan)
    validation = validate_payload(work_payload, source_scan, stale_removed)
    write_json(VALIDATION, validation)

    written = [
        str(WORK_MECH),
        str(PACKET_ANALYSIS_MECH),
        str(PAPER_FINAL_MECH),
        str(PACKET_FINAL_MECH),
        str(PACKET_FINAL_MECH_EVIDENCE),
    ]
    for path in [WORK_MECH, PACKET_ANALYSIS_MECH]:
        write_json(path, work_payload)
    for path in [PAPER_FINAL_MECH, PACKET_FINAL_MECH, PACKET_FINAL_MECH_EVIDENCE]:
        write_json(path, final_payload)
    append_rework_response(validation, written)
    print(
        json.dumps(
            {
                "status": "repair_ready_for_adjudication",
                "files_written": len(written) + 2,
                "response_appended": True,
                "claim_count": validation["checks"]["claim_count"],
                "direct_claim_ids": validation["direct_claim_ids"],
                "supplementary_text_records": validation["source_counts"]["supplementary_text_records"],
                "supplementary_table_count": validation["source_counts"]["supplementary_table_count"],
                "stale_caution_removed": validation["checks"]["stale_packet_supplementary_text_empty_caution_removed"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
