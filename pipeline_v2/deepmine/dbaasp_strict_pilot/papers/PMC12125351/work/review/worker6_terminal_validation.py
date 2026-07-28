#!/usr/bin/env python3
"""Worker-6 terminal contract validation for PMC12125351.

The script intentionally emits only compact status JSON. It does not print
source passages, table text, assay prose, or biomedical excerpts.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[7]
PAPER_ID = "PMC12125351"
PILOT = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot"
PAPER = PILOT / "papers" / PAPER_ID
PACKET = PILOT / "packets" / PAPER_ID
PAPER_FINAL = PAPER / "final"
PACKET_FINAL = PACKET / "final"
WORK_REVIEW = PAPER / "work/review"

RUNTIME_TICKET_IDS = [
    "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W1-FINAL-TICKET-METADATA-STALE",
    "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W2-ACTIVITY-TOXICITY-UNDEREXTRACTED",
    "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W2-SD10-STRAIN-CONFLICT-METADATA",
    "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W3-SUPP-XLSX-PACKET-INCOMPLETE",
    "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W4-DATABASE-ENTITY-CONFLATION",
    "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W4-FALLBACK-ROW-SUBCHECK-STATUS-CONFLATION",
    "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W5-MECHANISM-PI-SOURCE-DATA-OMITTED",
    "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W1-FINAL-COUNT-STATE-MISMATCH",
    "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W1-LIVE-REWORK-STATE-NONTERMINAL",
    "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W2-ACTIVITY-HARD-FINDING-NOT-RECONCILED",
    "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W2-ACTIVITY-TOXICITY-SOURCE-FIELD-CONFLICTS",
    "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W4-DATABASE-ARTICLE-ID-LOCATORS-NOT-PACKET-RE",
    "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W5-MECHANISM-RECURSIVE-SOURCE-LOCATOR",
    "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W1-FINAL-MATERIALS-MANIFEST-STALE",
    "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W1-PACKET-FINAL-STATE-METADATA-INCONSISTENT",
    "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W2-ACTIVITY-SUMMARY-METADATA-PLACEHOLDER",
    "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W2-ACTIVITY-TOXICITY-FIELD-CONFLICTS",
    "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W4-DATABASE-RECURSIVE-AND-STALE-FIELDS",
    "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W5-MECHANISM-PHENOTYPE-LOCATOR-AND-TICKET-STA",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    out = []
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(failures: list[dict[str, Any]], ticket: str, code: str, detail: Any = None) -> None:
    item = {"ticket_id": ticket, "failure_code": code}
    if detail is not None:
        item["detail"] = detail
    failures.append(item)


def iter_values(obj: Any):
    if isinstance(obj, dict):
        for value in obj.values():
            yield from iter_values(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from iter_values(value)
    else:
        yield obj


def locator_values(obj: Any, key_hint: str = ""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_hint = key
            if "locator" in key:
                if isinstance(value, str):
                    yield key, value
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            yield key, item
            yield from locator_values(value, next_hint)
    elif isinstance(obj, list):
        for value in obj:
            yield from locator_values(value, key_hint)


def source_locator_values(obj: Any):
    allowed_keys = {
        "source_locator",
        "supporting_source_locators",
        "source_label_locator",
        "method_source_locator",
        "value_source_locator",
    }
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in allowed_keys:
                if isinstance(value, str):
                    yield key, value
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            yield key, item
            yield from source_locator_values(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from source_locator_values(value)


def locs_for_record(record: dict[str, Any]) -> set[str]:
    return {loc for _, loc in source_locator_values(record)}


def normalize_num(value: Any) -> str:
    if isinstance(value, (int, float)):
        return format(value, ".15g")
    return str(value)


def resolve_locator(locator: str, locator_set: set[str]) -> bool:
    if locator in locator_set:
        return True
    if locator.startswith("database:"):
        return True
    return False


def owner_prereq(reqs: list[dict[str, Any]], resps: list[dict[str, Any]], failures: list[dict[str, Any]]) -> None:
    req_by_id = {r["ticket_id"]: r for r in reqs}
    for tid in RUNTIME_TICKET_IDS:
        req = req_by_id.get(tid)
        if not req:
            fail(failures, tid, "ticket_request_missing")
            continue
        owner = req.get("owner_worker")
        if owner == "worker-6":
            continue
        owner_resps = [
            r
            for r in resps
            if (r.get("ticket_id") or r.get("rework_ticket_id")) == tid and r.get("response_by") == owner
        ]
        ok = False
        for r in owner_resps:
            status = r.get("status") or r.get("response_status")
            evidence = bool(
                r.get("evidence_paths")
                or r.get("verified_artifact_paths")
                or r.get("repair_artifact_paths")
                or r.get("validation_artifacts")
                or r.get("ticket_contract_evidence")
            )
            if (
                status not in {"closed_repaired", "closed", "closed_unrecoverable", "cancelled"}
                and r.get("analysis_can_resume") is True
                and evidence
            ):
                ok = True
                break
        if not ok:
            fail(failures, tid, "owner_nonterminal_analysis_can_resume_response_missing", owner)


def main() -> int:
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    activity = load_json(PAPER_FINAL / "activity_toxicity_evidence.json")
    database = load_json(PAPER_FINAL / "database_record_verification.json")
    mechanism = load_json(PAPER_FINAL / "mechanism_ontology_record.json")
    review = load_json(PAPER_FINAL / "review_report.json")
    materials = load_json(PAPER_FINAL / "materials_manifest.json")
    packet_manifest = load_json(PACKET / "packet_manifest.json")
    analysis_status = load_json(PACKET / "analysis/analysis_status.json")
    extraction_status = load_json(PACKET / "extraction/extraction_status.json")
    supplementary_index = load_json(PACKET / "extracted/supplementary_index.json")
    supplementary_tables = load_json(PACKET / "extracted/supplementary_tables.json")
    locator_index = load_json(PACKET / "locators/locator_index.json")
    reqs = load_jsonl(PACKET / "rework/rework_requests.jsonl")
    resps = load_jsonl(PACKET / "rework/rework_responses.jsonl")

    locator_set = {entry.get("locator") for entry in locator_index.get("locators", []) if entry.get("locator")}
    source_file = "42003_2025_8282_MOESM2_ESM.xlsx"

    # Ticket owner response prerequisite.
    owner_prereq(reqs, resps, failures)

    # Mirror checks for current authoritative finals.
    required_mirrors = [
        "activity_toxicity_evidence.json",
        "database_record_verification.json",
        "materials_manifest.json",
        "mechanism_ontology_record.json",
        "review_report.json",
    ]
    for name in required_mirrors:
        paper_path = PAPER_FINAL / name
        packet_path = PACKET_FINAL / name
        if not packet_path.exists() or sha256(paper_path) != sha256(packet_path):
            fail(failures, "mirror-policy", "paper_packet_final_hash_mismatch", name)
    if sha256(PAPER_FINAL / "mechanism_ontology_record.json") != sha256(PACKET_FINAL / "mechanism_evidence.json"):
        fail(failures, "mirror-policy", "mechanism_evidence_alias_hash_mismatch")

    # Workbook packet locator coverage.
    target_sheets = [
        "Supplementary Data 3",
        "Supplementary Data 4",
        "Supplementary Data 9",
        "Supplementary Data 10",
        "Supplementary Data 11",
        "Supplementary Data 12",
    ]
    workbook_counts: dict[str, dict[str, int]] = {}
    for sheet in target_sheets:
        prefix = f"supp:{source_file}:sheet={sheet}"
        workbook_counts[sheet] = {
            "sheet": sum(1 for loc in locator_set if loc == prefix),
            "row": sum(1 for loc in locator_set if loc.startswith(prefix + ":row=") and ":cell=" not in loc),
            "cell": sum(1 for loc in locator_set if loc.startswith(prefix + ":row=") and ":cell=" in loc),
        }
        if workbook_counts[sheet]["row"] == 0 or workbook_counts[sheet]["cell"] == 0:
            fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W3-SUPP-XLSX-PACKET-INCOMPLETE", "workbook_row_or_cell_locator_missing", sheet)
    if len(supplementary_tables.get("tables", [])) < 12:
        fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W3-SUPP-XLSX-PACKET-INCOMPLETE", "supplementary_tables_sheet_count_low")

    # Activity/toxicity row counts by sheet and role.
    activity_records = activity.get("activity_records", [])
    toxicity_records = activity.get("toxicity_records", [])
    counts = {
        "activity_records": len(activity_records),
        "toxicity_records": len(toxicity_records),
        "database_record_audits": len(database.get("database_record_audits", [])),
        "mechanism_claims": len(mechanism.get("mechanism_claims", [])),
        "review_rework_targets": len(review.get("rework_targets", [])),
    }
    expected_counts = {
        "activity_records": 130,
        "toxicity_records": 126,
        "database_record_audits": 4,
        "mechanism_claims": 4,
        "review_rework_targets": 0,
    }
    for key, expected in expected_counts.items():
        if counts[key] != expected:
            fail(failures, "final-counts", "final_count_mismatch", {key: counts[key], "expected": expected})

    by_sheet_role = Counter()
    for rec in activity_records:
        loc = rec.get("source_locator", "")
        if "Supplementary Data 3" in loc:
            by_sheet_role["sd3_mic"] += 1
        if "Supplementary Data 4" in loc:
            by_sheet_role["sd4_mic"] += 1
        if "Supplementary Data 10" in loc:
            by_sheet_role["sd10_mic"] += 1
    for rec in toxicity_records:
        loc = rec.get("source_locator", "")
        endpoint = str(rec.get("endpoint", "")).lower()
        if "Supplementary Data 10" in loc and ("cc50" in endpoint or "hc50" in endpoint):
            by_sheet_role["sd10_cc50_hc50"] += 1
        if "Supplementary Data 11" in loc:
            by_sheet_role["sd11_hemolysis"] += 1
        if "Supplementary Data 12" in loc:
            by_sheet_role["sd12_cell_viability"] += 1
    expected_sheet_counts = {
        "sd3_mic": 76,
        "sd4_mic": 36,
        "sd10_mic": 18,
        "sd10_cc50_hc50": 18,
        "sd11_hemolysis": 54,
        "sd12_cell_viability": 54,
    }
    for key, expected in expected_sheet_counts.items():
        if by_sheet_role[key] != expected:
            fail(failures, "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W2-ACTIVITY-SUMMARY-METADATA-PLACEHOLDER", "source_sheet_role_count_mismatch", {key: by_sheet_role[key], "expected": expected})

    # Activity-specific contract checks.
    sd3_k88_missing = [
        r.get("record_id")
        for r in activity_records
        if "Supplementary Data 3" in str(r.get("source_locator", ""))
        and str(r.get("target_species", "")).lower().startswith("escherichia coli")
        and str(r.get("target_strain_or_isolate", "")).strip().lower() in {"not reported", "", "none"}
    ]
    if sd3_k88_missing:
        fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W2-ACTIVITY-TOXICITY-SOURCE-FIELD-CONFLICTS", "sd3_ecoli_strain_missing", len(sd3_k88_missing))

    sd10_bad_units = [
        r.get("record_id")
        for r in toxicity_records
        if "Supplementary Data 10" in str(r.get("source_locator", ""))
        and str(r.get("raw_endpoint_label", "")).lower().startswith("log10")
        and str(r.get("raw_unit", "")).strip() in {"μM", "uM", "log2"}
    ]
    if sd10_bad_units:
        fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W2-ACTIVITY-TOXICITY-SOURCE-FIELD-CONFLICTS", "sd10_log10_bad_unit", len(sd10_bad_units))

    sd10_si_bad = [
        r.get("record_id")
        for r in toxicity_records
        if "Supplementary Data 10" in str(r.get("source_locator", ""))
        and str(r.get("endpoint", "")).strip().lower() == "selectivity index"
    ]
    if sd10_si_bad:
        fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W2-ACTIVITY-TOXICITY-SOURCE-FIELD-CONFLICTS", "sd10_unsupported_selectivity_index", len(sd10_si_bad))

    human_tox_bad = [
        r.get("record_id")
        for r in toxicity_records
        if any(f"Supplementary Data {n}" in str(r.get("source_locator", "")) for n in (10, 11, 12))
        and str(r.get("target_species", "")).strip().lower() == "homo sapiens"
    ]
    if human_tox_bad:
        fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W2-ACTIVITY-TOXICITY-SOURCE-FIELD-CONFLICTS", "unsupported_homo_sapiens_toxicity_target", len(human_tox_bad))

    hemolysis_time_bad = [
        r.get("record_id")
        for r in toxicity_records
        if str(r.get("endpoint", "")).lower() in {"hc50", "percent hemolysis"}
        and str(r.get("assay_conditions", {}).get("incubation_time", "")).strip() != "1 h"
    ]
    if hemolysis_time_bad:
        fail(failures, "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W2-ACTIVITY-TOXICITY-FIELD-CONFLICTS", "hemolysis_incubation_time_not_1h", len(hemolysis_time_bad))

    sd10_col_e = [
        r
        for r in activity_records
        if re.search(r"Supplementary Data 10:row=(?:3|4|5|6|7|8|9|10|11):cell=E", str(r.get("source_locator", "")))
    ]
    if len(sd10_col_e) != 9:
        fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W2-SD10-STRAIN-CONFLICT-METADATA", "sd10_column_e_row_count_mismatch", len(sd10_col_e))
    for rec in sd10_col_e:
        vals = [str(v) for v in iter_values(rec)]
        joined = " | ".join(vals)
        if "ATCC 25923" not in str(rec.get("raw_endpoint_label", "")):
            fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W2-SD10-STRAIN-CONFLICT-METADATA", "sd10_column_e_label_missing_source_strain", rec.get("record_id"))
        if str(rec.get("target_strain_or_isolate", "")) == "ATCC 29213" and not ("ATCC 25923" in joined and "ATCC 29213" in joined):
            fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W2-SD10-STRAIN-CONFLICT-METADATA", "sd10_column_e_conflict_metadata_incomplete", rec.get("record_id"))
        for _, loc in source_locator_values(rec):
            if ":column=E" in loc or not resolve_locator(loc, locator_set):
                fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W2-SD10-STRAIN-CONFLICT-METADATA", "sd10_column_e_unresolved_locator", {"record_id": rec.get("record_id"), "locator_field": loc.split(":column=")[0] + ":column=E" if ":column=E" in loc else loc})

    # p17/p20 P. aeruginosa conflict preservation.
    needed_ids = {"PMC12125351-SD4-R006-C05-MIC": ("35.15625", "9.96722061992234"), "PMC12125351-SD4-R007-C05-MIC": ("70.3125", "18.5789934940427")}
    by_id = {r.get("record_id"): r for r in activity_records}
    for rid, (ug, um) in needed_ids.items():
        rec = by_id.get(rid)
        if not rec:
            fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W2-ACTIVITY-HARD-FINDING-NOT-RECONCILED", "p17_p20_record_missing", rid)
            continue
        joined = " | ".join(str(v) for v in iter_values(rec))
        if normalize_num(rec.get("raw_value")) != ug or um not in joined or "preserved_source_conflict" not in rec:
            fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W2-ACTIVITY-HARD-FINDING-NOT-RECONCILED", "p17_p20_conflict_or_value_not_preserved", rid)

    # Reject unrelated non-assay table surfaces.
    disallowed = ["formulation", "composition", "ftir", "spectroscopy", "tga", "thermal", "wettability", "mechanical"]
    for rec in activity_records + toxicity_records:
        fields = " | ".join(str(v).lower() for v in iter_values(rec))
        if any(term in fields for term in disallowed):
            fail(failures, "activity-toxicity", "disallowed_non_assay_surface_in_final_record", rec.get("record_id"))

    # Locator integrity for activity and toxicity source fields.
    unresolved_locs = []
    for rec in activity_records + toxicity_records:
        for key, loc in source_locator_values(rec):
            if not resolve_locator(loc, locator_set):
                unresolved_locs.append({"record_id": rec.get("record_id"), "field": key})
    if unresolved_locs:
        fail(failures, "activity-toxicity", "unresolved_activity_toxicity_source_locator_count", len(unresolved_locs))

    # Summary metadata.
    summary_counts = activity.get("summary_counts", {})
    if summary_counts.get("source_tables_checked", 0) == 0 or summary_counts.get("activity_tables_accepted", 0) == 0:
        fail(failures, "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W2-ACTIVITY-SUMMARY-METADATA-PLACEHOLDER", "activity_summary_placeholder_counts")
    if not activity.get("qa_summary", {}).get("source_role_counts"):
        fail(failures, "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W2-ACTIVITY-SUMMARY-METADATA-PLACEHOLDER", "qa_source_role_counts_missing")

    # Database contract checks.
    if database.get("authoritative_dbaasp_ingest_ready") is not False or database.get("fallback_rows_promoted_to_source_verified") is not False:
        fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W4-DATABASE-ENTITY-CONFLATION", "database_authoritative_boundary_bad")
    linked_files = [
        "linked_article_records.jsonl",
        "linked_assay_records.jsonl",
        "linked_sequence_records.jsonl",
        "linked_literature_records.jsonl",
    ]
    linked_counts = {name: len(load_jsonl(PACKET / "database" / name)) for name in linked_files}
    if any(linked_counts.values()) and database.get("authoritative_dbaasp_ingest_ready") is not True:
        warnings.append({"code": "authoritative_linked_rows_present_but_not_ingest_ready", "counts": linked_counts})

    seq_expect = {"p15": 26, "p17": 29, "p20": 32}
    seq_lengths = {}
    for audit in database.get("database_record_audits", []):
        candidate = str(audit.get("candidate_peptide", "") or audit.get("candidate_alias", "")).lower()
        for key in seq_expect:
            if key in candidate:
                seq_lengths[key] = audit.get("candidate_sequence_length")
        if audit.get("status") != "unresolved_record":
            fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W4-FALLBACK-ROW-SUBCHECK-STATUS-CONFLATION", "fallback_top_level_not_unresolved", audit.get("record_audit_id"))
        for subkey in ["sequence_agreement_with_primary", "amidation_check", "name_synonym_agreement", "modification_check"]:
            sub = audit.get(subkey)
            if isinstance(sub, dict) and sub.get("status") == "source_verified":
                fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W4-FALLBACK-ROW-SUBCHECK-STATUS-CONFLATION", "fallback_subcheck_promoted_source_verified", {"record": audit.get("record_audit_id"), "subcheck": subkey})
    for key, expected in seq_expect.items():
        if seq_lengths.get(key) != expected:
            fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W4-DATABASE-ENTITY-CONFLATION", "source_local_sequence_length_mismatch", {key: seq_lengths.get(key), "expected": expected})
    for _, loc in source_locator_values(database):
        if any(loc.startswith(prefix) for prefix in ("pipeline_v2/", "packets/", "papers/", "work/", "analysis/")):
            fail(failures, "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W4-DATABASE-RECURSIVE-AND-STALE-FIELDS", "recursive_database_source_locator")
        if loc.startswith("xml:article-id:") and loc not in locator_set:
            fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W4-DATABASE-ARTICLE-ID-LOCATORS-NOT-PACKET-RE", "article_id_locator_unresolved")

    # Mechanism contract checks.
    claims = mechanism.get("mechanism_claims", [])
    class_counts = Counter(c.get("evidence_class") for c in claims)
    expected_class_counts = {"direct_mechanism": 1, "computational_only": 1, "inferred_mechanism": 1, "phenotype_supported": 1}
    if dict(class_counts) != expected_class_counts:
        fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W5-MECHANISM-RECURSIVE-SOURCE-LOCATOR", "mechanism_class_count_mismatch", dict(class_counts))
    for claim in claims:
        cls = claim.get("evidence_class")
        direct_types = claim.get("direct_assay_types") or []
        if cls == "direct_mechanism" and not direct_types:
            fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W5-MECHANISM-PI-SOURCE-DATA-OMITTED", "direct_mechanism_missing_direct_assay_types", claim.get("claim_id"))
        if cls != "direct_mechanism" and direct_types:
            fail(failures, "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W5-MECHANISM-PHENOTYPE-LOCATOR-AND-TICKET-STA", "nondirect_claim_has_direct_assay_types", claim.get("claim_id"))
        if claim.get("claim_id") == "PMC12125351-MECH-004" and claim.get("source_locator") == "xml:p:27":
            fail(failures, "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W5-MECHANISM-PHENOTYPE-LOCATOR-AND-TICKET-STA", "phenotype_claim_wrong_primary_locator")
        for key, loc in source_locator_values(claim):
            if any(token in loc for token in ["/analysis/", "/work/", "/final/", "papers/", "packets/"]) or loc.startswith("/"):
                fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W5-MECHANISM-RECURSIVE-SOURCE-LOCATOR", "recursive_mechanism_source_locator", {"claim_id": claim.get("claim_id"), "field": key})
            if not resolve_locator(loc, locator_set):
                fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W5-MECHANISM-RECURSIVE-SOURCE-LOCATOR", "unresolved_mechanism_source_locator", {"claim_id": claim.get("claim_id"), "field": key})
    direct_joined = " | ".join(str(v) for c in claims if c.get("evidence_class") == "direct_mechanism" for v in iter_values(c))
    if "Supplementary Data 9" not in direct_joined:
        fail(failures, "rwk-PMC12125351-campaign-r01-BF-PMC12125351-W5-MECHANISM-PI-SOURCE-DATA-OMITTED", "direct_pi_missing_supplementary_data_9_support")

    # Live/final ticket state consistency. Current runtime list is expected open
    # before terminal responses, so this only checks internal equality fields.
    final_live_counts = {
        "packet_manifest": packet_manifest.get("open_rework_ticket_count"),
        "analysis_status": analysis_status.get("open_rework_ticket_count"),
        "review_report": review.get("open_rework_ticket_count"),
        "materials_manifest": materials.get("open_rework_ticket_count"),
    }
    if len(set(final_live_counts.values())) != 1:
        warnings.append({"code": "preterminal_open_rework_count_fields_not_equal", "counts": final_live_counts})
    if review.get("final_counts", {}).get("review_rework_targets") != len(review.get("rework_targets", [])):
        fail(failures, "rwk-PMC12125351-campaign-r02-BF-PMC12125351-W1-FINAL-COUNT-STATE-MISMATCH", "review_rework_target_count_mismatch")

    # Material inventory consistency.
    supp_count = len(supplementary_index.get("files", []))
    material_supp_count = materials.get("supplementary_inventory_summary", {}).get("supplementary_file_count")
    extraction_supp_count = extraction_status.get("supplementary_file_count")
    if len({supp_count, material_supp_count, extraction_supp_count}) != 1 or supp_count != 4:
        fail(failures, "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W1-PACKET-FINAL-STATE-METADATA-INCONSISTENT", "supplementary_file_count_inconsistent", {"supplementary_index": supp_count, "materials": material_supp_count, "extraction_status": extraction_supp_count})
    if materials.get("locator_count") != packet_manifest.get("locator_count"):
        fail(failures, "rwk-PMC12125351-campaign-r03-BF-PMC12125351-W1-FINAL-MATERIALS-MANIFEST-STALE", "materials_locator_count_stale")

    out = {
        "paper_id": PAPER_ID,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "overall_contract_pass": not failures,
        "failure_count": len(failures),
        "warning_count": len(warnings),
        "failures": failures,
        "warnings": warnings,
        "runtime_ticket_count": len(RUNTIME_TICKET_IDS),
        "owner_prerequisite_checked": True,
        "counts": counts,
        "source_sheet_role_counts": dict(by_sheet_role),
        "workbook_locator_counts": workbook_counts,
        "linked_database_row_counts": linked_counts,
        "preterminal_open_rework_counts": final_live_counts,
        "paper_packet_final_hashes": {
            name: {
                "paper": sha256(PAPER_FINAL / name),
                "packet": sha256(PACKET_FINAL / name) if (PACKET_FINAL / name).exists() else None,
            }
            for name in required_mirrors
        },
        "mechanism_alias_hash": {
            "paper_mechanism_ontology_record": sha256(PAPER_FINAL / "mechanism_ontology_record.json"),
            "packet_mechanism_evidence": sha256(PACKET_FINAL / "mechanism_evidence.json"),
        },
    }
    WORK_REVIEW.mkdir(parents=True, exist_ok=True)
    output = WORK_REVIEW / "worker6_terminal_validation.json"
    output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall_contract_pass": out["overall_contract_pass"], "failure_count": len(failures), "warning_count": len(warnings), "artifact": str(output.relative_to(ROOT))}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
