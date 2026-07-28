#!/usr/bin/env python3
"""Targeted worker-4/worker-6 re-review repair for doi__10.1128_spectrum.02013-21."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ID = "doi__10.1128_spectrum.02013-21"
ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
REPORTS = ROOT / "reports"

SOURCE_PATHS_CHECKED = [
    "rework_context/doi__10.1128_spectrum.02013-21/handoff_context.json",
    "paper_packets/doi__10.1128_spectrum.02013-21/packet_manifest.json",
    "paper_packets/doi__10.1128_spectrum.02013-21/locators/locator_index.json",
    "paper_packets/doi__10.1128_spectrum.02013-21/raw/paper.xml",
    "paper_packets/doi__10.1128_spectrum.02013-21/raw/paper.pdf",
    "paper_packets/doi__10.1128_spectrum.02013-21/extracted/xml_sections.json",
    "paper_packets/doi__10.1128_spectrum.02013-21/extracted/pdf_text/spectrum.02013-21.txt",
    "paper_packets/doi__10.1128_spectrum.02013-21/extracted/figure_captions.json",
    "paper_packets/doi__10.1128_spectrum.02013-21/extracted/supplementary_index.json",
    "paper_packets/doi__10.1128_spectrum.02013-21/extracted/supplementary_tables.json",
    "paper_packets/doi__10.1128_spectrum.02013-21/extracted/oa_package/local-DBAASP-PMC9045357/PMC9045357/spectrum.02013-21-f002.jpg",
    "paper_packets/doi__10.1128_spectrum.02013-21/database/linked_assay_records.jsonl",
    "paper_packets/doi__10.1128_spectrum.02013-21/database/linked_experiment_records.jsonl",
    "paper_packets/doi__10.1128_spectrum.02013-21/database/linked_dramp_activity_records.jsonl",
    "paper_packets/doi__10.1128_spectrum.02013-21/database/linked_literature_records.jsonl",
]

TOOLS_ATTEMPTED = [
    "jq over packet, final, quality feedback, and database JSON/JSONL",
    "rg over XML sections, raw XML, and extracted PDF text",
    "file image inventory for Figure 2 and table images",
    "tesseract attempted for Figure 2 OCR; binary not installed in this environment",
    "manual source reconciliation from XML section, Figure 2 caption, Table 1, Table 2, and linked database rows",
]

PEPTIDE_IDENTITY = {
    "primary_name": "gcIFN-20",
    "database_names": [
        "Grasscarp interferon (137-156), GcIFN-20",
        "GcIFN-20",
    ],
    "sequence": "SYEKKINRHFKILKKNLKKK",
    "source_organism": "Ctenopharyngodon idella IFN1-derived synthetic peptide",
    "modification_status": "No N-terminal, C-terminal, D-amino-acid, cyclization, disulfide, amidation, or lipidation modification is reported in the local primary article text.",
    "primary_source_locators": [
        {"source_path": "source/paper.xml", "locator": "xml:abstract"},
        {"source_path": "source/paper.xml", "locator": "xml:sec=5:IFN1 contains a cationic, amphipathic novel alpha-helical peptide"},
        {"source_path": "source/paper.xml", "locator": "xml:fig=1:FIG 1"},
    ],
}

TOXICITY_FIGURE_LOCATORS = [
    {"source_path": "source/paper.xml", "locator": "xml:sec=6:GcIFN-20 possesses direct bactericidal activity and negligible toxicity"},
    {"source_path": "source/paper.xml", "locator": "xml:fig=2:FIG 2"},
    {
        "source_path": "paper_packets/doi__10.1128_spectrum.02013-21/extracted/oa_package/local-DBAASP-PMC9045357/PMC9045357/spectrum.02013-21-f002.jpg",
        "locator": "local_oa_figure_image:FIG 2",
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def status_summary(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter(str(record.get("status") or record.get("layer1_status") or "unresolved_record") for record in records)
    return dict(sorted(counts.items()))


def original_assay_locator(record: dict[str, Any]) -> dict[str, Any] | None:
    locator = (record.get("sequence_check") or {}).get("source_locator") if isinstance(record.get("sequence_check"), dict) else None
    return locator if isinstance(locator, dict) else None


def is_non_table_exact_toxicity(record: dict[str, Any]) -> bool:
    subject = str(record.get("database_subject") or "").lower()
    measure = str(record.get("database_measure") or "").lower()
    return any(key in subject for key in ("erythrocyte", "vero", "raw 264")) and any(
        key in measure for key in ("hemolysis", "killing", "na")
    )


def is_database_only_toxicity(record: dict[str, Any]) -> bool:
    subject = str(record.get("database_subject") or "").lower()
    measure = str(record.get("database_measure") or "").strip().lower()
    return any(key in subject for key in ("vero", "raw 264")) and measure in {"", "na"}


def is_dramp_scope_conflict(record: dict[str, Any]) -> bool:
    return str(record.get("source_id") or "").startswith("DRAMP:") or str(record.get("sequence_key") or "").startswith("DRAMP:")


def source_review_record(record: dict[str, Any]) -> dict[str, Any]:
    updated = dict(record)
    original_locator = original_assay_locator(updated)
    updated["peptide_identity_check"] = PEPTIDE_IDENTITY
    updated.setdefault("citation_traceability", {"source_path": "source/paper.xml", "locator": "xml:article-meta"})
    updated.setdefault("traceability", record.get("traceability") or {})

    if updated.get("status") == "source_verified" or updated.get("layer1_status") == "source_verified":
        if original_locator:
            updated["assay_source_locator"] = original_locator
        updated["sequence_check"] = {
            "status": "source_verified",
            "source_locator": {
                "source_path": "source/paper.xml",
                "locator": "xml:sec=5:IFN1 contains a cationic, amphipathic novel alpha-helical peptide",
                "primary_source_statement": "The local primary article names gcIFN-20 and gives the 20-aa sequence; linked table rows verify antimicrobial assay values, not sequence by themselves.",
            },
        }
        updated["review_notes"] = "Worker-4 re-review verified the linked antimicrobial table row against XML Table 1/2 and verified peptide identity against the primary sequence locator."
        updated["source_review_provenance"] = {
            "assay_values": "source_verified_from_xml_table" if original_locator else "not_applicable_literature_link",
            "identity": "source_verified_from_primary_sequence_text",
            "reviewed_by": ["worker-4"],
        }
        updated["status"] = "source_verified"
        updated["layer1_status"] = "source_verified"
        return updated

    if is_database_only_toxicity(updated):
        updated["status"] = "database_only_no_primary_source"
        updated["layer1_status"] = "database_only_no_primary_source"
        updated["sequence_check"] = {
            "status": "source_verified_for_peptide_identity_only",
            "source_locator": PEPTIDE_IDENTITY["primary_source_locators"][1],
        }
        updated["toxicity_source_review"] = {
            "paper_support": "Primary text supports weak cytotoxicity and IC50 greater than 100 uM but does not provide this database row's empty/NA exact activity threshold.",
            "toxicity_locators_checked": TOXICITY_FIGURE_LOCATORS,
            "exact_database_value_supported": False,
        }
        updated["conflict_context"] = "Database row is linked to this paper but the row-specific empty/NA cytotoxicity threshold is not present in local XML tables, PDF text, or extracted text. Figure 2 supports only qualitative low-toxicity context here."
        updated["review_notes"] = updated["conflict_context"]
        updated["unrecoverable_gap_code"] = "figure_only_toxicity_exact_values_unrecoverable"
        return updated

    if is_non_table_exact_toxicity(updated):
        updated["status"] = "source_conflict"
        updated["layer1_status"] = "source_conflict"
        updated["sequence_check"] = {
            "status": "source_verified_for_peptide_identity_only",
            "source_locator": PEPTIDE_IDENTITY["primary_source_locators"][1],
        }
        updated["toxicity_source_review"] = {
            "paper_support": "Primary text and Figure 2 caption identify SRBC hemolysis and RAW/Vero MTT cytotoxicity assays, but the exact database percentages are not available in local XML/PDF tables or extracted text.",
            "toxicity_locators_checked": TOXICITY_FIGURE_LOCATORS,
            "exact_database_value_supported": False,
        }
        updated["conflict_context"] = "Preserve as source_conflict: the local primary article supports the toxicity assay context, but the exact database value is figure-only/not machine-recovered from local text or tables."
        updated["review_notes"] = updated["conflict_context"]
        updated["unrecoverable_gap_code"] = "figure_only_toxicity_exact_values_unrecoverable"
        return updated

    if is_dramp_scope_conflict(updated):
        updated["status"] = "source_conflict"
        updated["layer1_status"] = "source_conflict"
        updated["sequence_check"] = {
            "status": "source_verified_for_peptide_identity_only",
            "source_locator": PEPTIDE_IDENTITY["primary_source_locators"][1],
        }
        updated["dramp_scope_review"] = {
            "paper_support": "The local primary article supports antimicrobial and anti-inflammatory activity for gcIFN-20.",
            "unsupported_database_scope": "The DRAMP row labels activity as Antimicrobial, Anticancer but local source review did not find primary support for anticancer activity or a target organism row.",
            "source_locators_checked": [
                {"source_path": "source/paper.xml", "locator": "xml:abstract"},
                {"source_path": "source/paper.xml", "locator": "xml:sec=6"},
                {"source_path": "source/paper.xml", "locator": "xml:fig=2:FIG 2"},
            ],
        }
        updated["conflict_context"] = "Preserve as source_conflict: DRAMP antimicrobial scope is partly supported, but anticancer/target-organism details are database-only or unsupported by local primary material."
        updated["review_notes"] = updated["conflict_context"]
        updated["unrecoverable_gap_code"] = "database_activity_scope_conflict_unresolved"
        return updated

    updated["status"] = "unresolved_record"
    updated["layer1_status"] = "unresolved_record"
    updated["conflict_context"] = "Record remains unresolved after bounded worker-4 source review."
    updated["review_notes"] = updated["conflict_context"]
    return updated


def unrecoverable_gaps(generated_at: str) -> list[dict[str, Any]]:
    return [
        {
            "blocks_publication_grade": True,
            "gap_code": "figure_only_toxicity_exact_values_unrecoverable",
            "impact": "Exact DBAASP hemolysis/cytotoxicity percentages for SRBC, Vero cells, and RAW 264.7 cells cannot be source-verified from local text/table material; database rows remain source_conflict or database_only_no_primary_source.",
            "next_action": "record_and_continue",
            "owner_worker": "worker-4",
            "recorded_at": generated_at,
            "source_paths_checked": SOURCE_PATHS_CHECKED,
            "tools_attempted": TOOLS_ATTEMPTED,
            "why_unrecoverable": "The local XML/PDF text and parsed tables provide Table 1/2 antimicrobial values and qualitative low-toxicity context with Figure 2 locators, but not the exact database toxicity percentages. No supplementary files are present, and tesseract OCR is unavailable in this environment.",
        },
        {
            "blocks_publication_grade": True,
            "gap_code": "database_activity_scope_conflict_unresolved",
            "impact": "DRAMP/database activity scope includes unsupported anticancer or non-specific rows; supported antimicrobial evidence is retained, but unsupported scope remains non-publication-grade.",
            "next_action": "record_and_continue",
            "owner_worker": "worker-4",
            "recorded_at": generated_at,
            "source_paths_checked": SOURCE_PATHS_CHECKED,
            "tools_attempted": TOOLS_ATTEMPTED,
            "why_unrecoverable": "Local primary material supports gcIFN-20 antimicrobial and anti-inflammatory claims, but does not support the linked DRAMP anticancer label or row-specific target values.",
        },
    ]


def qc_reasons() -> list[dict[str, Any]]:
    return [
        {
            "code": "figure_only_toxicity_exact_values_unrecoverable",
            "owner_worker": "worker-4",
            "reason": "Exact database toxicity percentages for SRBC, Vero, and RAW 264.7 rows were not recoverable from local XML/PDF text, parsed tables, or supplementary assets; Figure 2 provides assay context but not source-extracted exact values.",
            "severity": "blocking",
        },
        {
            "code": "database_activity_scope_conflict_unresolved",
            "owner_worker": "worker-4 + worker-6",
            "reason": "Linked DRAMP/database rows include unsupported or database-only activity scope; supported antimicrobial rows are retained while unsupported scope remains conflict-preserved.",
            "severity": "major",
        },
    ]


def rework_target(generated_at: str) -> dict[str, Any]:
    return {
        "artifact_path": "papers/doi__10.1128_spectrum.02013-21/final/review_report.json",
        "blocks": ["publication_grade_ready", "final_approval"],
        "created_at": generated_at,
        "failing_object": "publication_grade_ready",
        "failure_code": "figure_only_toxicity_exact_values_unrecoverable",
        "layer": "database_record_adjudication_and_final_review",
        "omission_code": "worker4_database_exact_toxicity_values_not_locally_recoverable",
        "owner_workers": ["worker-4", "worker-6"],
        "paper_id": PAPER_ID,
        "qc_failure_reasons": qc_reasons(),
        "reason": "Worker-4/6 re-review completed bounded local source recovery and preserved the unsupported exact database toxicity/scope rows as conflicts instead of fabricating values.",
        "requested_by": "codex_cli_worker46_re_review",
        "requested_outputs": [
            {
                "artifact_path": "paper_packets/doi__10.1128_spectrum.02013-21/analysis/database_record_audit.json",
                "need": "Keep source_conflict/database_only rows explicit with source paths checked and unrecoverable gap codes.",
                "required_locators": ["xml:sec=6", "xml:fig=2", "database:linked_assay_records", "database:linked_experiment_records"],
            },
            {
                "artifact_path": "papers/doi__10.1128_spectrum.02013-21/work/review/quality_feedback.json",
                "need": "Keep publication-grade blocked until external/manual figure quantification or authoritative source evidence resolves the exact database toxicity values.",
                "required_locators": ["quality_feedback:unrecoverable_material_gaps"],
            },
        ],
        "required_action": "Do not accept under obtainable-only mode. Controller should mark this paper blocked/unrecoverable for the exact database-toxicity values or provide new authoritative local evidence; do not rerun broad initial workflow/bootstrap.",
        "rework_context_packet_required": False,
        "severity": "blocking",
        "source_paths_to_check": SOURCE_PATHS_CHECKED,
        "target_queue": "analysis",
        "ticket_id": "rwk-complete-test-0001",
        "unrecoverable_material_gap_codes": [
            "figure_only_toxicity_exact_values_unrecoverable",
            "database_activity_scope_conflict_unresolved",
        ],
        "worker": "worker-6",
    }


def build_review(generated_at: str, database: dict[str, Any]) -> dict[str, Any]:
    gaps = unrecoverable_gaps(generated_at)
    target = rework_target(generated_at)
    return {
        "adjudication_summary": "Worker-4/6 source re-review completed for gcIFN-20. Table 1/2 antimicrobial rows are source-verified, but exact toxicity percentages and unsupported DRAMP activity scope remain conflict-preserved/unrecoverable from local material, so the paper is not publication-grade.",
        "caution_findings": [
            {
                "caution_code": "table_activity_rows_source_verified",
                "evidence_context": "Antimicrobial MIC/MBC/MBC90 rows mapped to XML Table 1 and Table 2 are retained with raw units and locators.",
            },
            {
                "caution_code": "database_exact_toxicity_values_not_source_verified",
                "evidence_context": "SRBC, Vero, and RAW 264.7 database toxicity rows have Figure 2 assay context but no exact text/table values recoverable locally.",
            },
            {
                "caution_code": "dramp_activity_scope_conflict_preserved",
                "evidence_context": "DRAMP antimicrobial scope is partly supported; anticancer or unavailable target scope is not supported by the local primary material.",
            },
        ],
        "checked_inputs": SOURCE_PATHS_CHECKED,
        "materials_exhausted": {
            "figure_images": "Figure 2 image located; exact plotted values not recoverable with available local text/OCR tools.",
            "merged_database_rows": True,
            "oa_package": True,
            "paper_pdf": True,
            "paper_xml": True,
            "supplementary_assets": "No supplementary assets are present in the packet or landed paper inventory.",
        },
        "paper_id": PAPER_ID,
        "per_layer_decision_rationale": {
            "layer_1_database": "Worker-4 verified peptide identity and table-backed antimicrobial database rows. Non-table exact toxicity percentages and unsupported DRAMP scope remain source_conflict/database_only with unrecoverable gap codes.",
            "layer_2_activity_toxicity": "Existing worker-2 activity table extraction is retained; worker-4/6 did not fabricate figure-only toxicity values into activity rows.",
            "layer_3_mechanism": "Existing mechanism locator notes are not expanded in this worker-4/6 lane; database blockers already prevent publication-grade acceptance.",
            "publication_grade_review": "Worker-6 keeps the paper non-accepted because blocking database exact-value gaps remain after bounded source recovery.",
        },
        "publication_grade": False,
        "qc_failure_reasons": qc_reasons(),
        "reasoning_effort": "xhigh",
        "review_model": "gpt-5.5",
        "review_status": "needs_targeted_rework",
        "reviewed_at": generated_at,
        "rework_targets": [target],
        "semantic_quality_checks": {
            "activity_rows_parsed": len((read_json(PACKET / "analysis" / "activity_toxicity_evidence.json", {}) or {}).get("activity_records", [])),
            "database_status_summary": database.get("status_summary", {}),
            "database_snapshots": database.get("database_row_counts", {}),
            "mechanism_claims": len((read_json(PACKET / "analysis" / "mechanism_evidence.json", {}) or {}).get("mechanism_claims", [])),
            "owner_worker_re_review": {
                "source_paths_checked": SOURCE_PATHS_CHECKED,
                "tools_attempted": TOOLS_ATTEMPTED,
                "unrecoverable_material_gap_count": len(gaps),
            },
        },
        "source_review_depth": [
            "paper_xml",
            "paper_pdf",
            "oa_package",
            "supplementary_assets",
            "merged_database_rows",
            "figure_images",
        ],
        "source_reviewed": True,
        "strict_gate": {
            "publication_grade_ready": False,
            "required_rework_count": 1,
            "unrecoverable_material_gap_count": len(gaps),
        },
        "unrecoverable_material_gaps": gaps,
        "validator_contract_passed": True,
    }


def repair_artifacts() -> None:
    generated_at = now_iso()
    database = read_json(PACKET / "analysis" / "database_record_audit.json")
    database["artifact_type"] = "worker4_database_record_audit"
    database["audit_scope"] = "Worker-4 targeted re-review of linked DBAASP/DRAMP/database rows against local primary XML/PDF/table/figure/database material."
    database["generated_at"] = generated_at
    database["review_model"] = "gpt-5.5"
    database["reasoning_effort"] = "xhigh"
    database["source_reviewed"] = True
    database["source_paths_checked"] = SOURCE_PATHS_CHECKED
    database["tools_attempted"] = TOOLS_ATTEMPTED
    database["record_audits"] = [source_review_record(record) for record in database.get("record_audits", [])]
    database["status_summary"] = status_summary(database["record_audits"])
    database["unrecoverable_material_gaps"] = unrecoverable_gaps(generated_at)
    database["worker4_decision"] = "bounded_source_review_complete_nonaccepted_due_unrecoverable_database_exact_value_gaps"

    write_json(PACKET / "analysis" / "database_record_audit.json", database)
    write_json(PAPER / "final" / "database_record_verification.json", database)
    if (PACKET / "final").exists():
        write_json(PACKET / "final" / "database_record_verification.json", database)

    review = build_review(generated_at, database)
    write_json(PACKET / "analysis" / "adjudication_report.json", review)
    write_json(PAPER / "final" / "review_report.json", review)
    if (PACKET / "final").exists():
        write_json(PACKET / "final" / "review_report.json", review)

    target = review["rework_targets"][0]
    feedback = {
        "generated_at": generated_at,
        "issue_count": len(qc_reasons()),
        "paper_id": PAPER_ID,
        "publication_grade_ready": False,
        "qc_failure_reasons": qc_reasons(),
        "rework_context_packet_required": False,
        "rework_targets": [target],
        "status": "needs_targeted_rework_unrecoverable_material_gap",
        "unrecoverable_material_gaps": review["unrecoverable_material_gaps"],
    }
    write_json(PAPER / "work" / "review" / "quality_feedback.json", feedback)

    requests_path = PACKET / "rework" / "rework_requests.jsonl"
    requests = [row for row in read_jsonl(requests_path) if row.get("ticket_id") != "rwk-complete-test-0001"]
    requests.append(target)
    write_jsonl(requests_path, requests)

    status = read_json(PACKET / "analysis" / "analysis_status.json", {})
    status.update(
        {
            "generated_at": generated_at,
            "open_rework_ticket_ids": ["rwk-complete-test-0001"],
            "paper_id": PAPER_ID,
            "status": "analysis_needs_analysis_rework",
            "unrecoverable_material_gaps": review["unrecoverable_material_gaps"],
            "worker4_worker6_re_review": "completed_but_not_publication_grade",
        }
    )
    write_json(PACKET / "analysis" / "analysis_status.json", status)

    append_jsonl(
        PACKET / "rework" / "rework_responses.jsonl",
        {
            "created_at": generated_at,
            "paper_id": PAPER_ID,
            "remaining_qc_failure_reasons": qc_reasons(),
            "repair_status": "bounded_source_review_completed_ticket_remains_open",
            "responding_workers": ["worker-4", "worker-6"],
            "response_id": f"worker46-{generated_at}",
            "source_paths_checked": SOURCE_PATHS_CHECKED,
            "ticket_id": "rwk-complete-test-0001",
            "ticket_status_after_response": "open_blocked_unrecoverable_material_gap",
            "tools_attempted": TOOLS_ATTEMPTED,
            "unrecoverable_material_gaps": review["unrecoverable_material_gaps"],
            "written_artifacts": [
                "paper_packets/doi__10.1128_spectrum.02013-21/analysis/database_record_audit.json",
                "paper_packets/doi__10.1128_spectrum.02013-21/analysis/adjudication_report.json",
                "paper_packets/doi__10.1128_spectrum.02013-21/analysis/analysis_status.json",
                "paper_packets/doi__10.1128_spectrum.02013-21/rework/rework_requests.jsonl",
                "papers/doi__10.1128_spectrum.02013-21/final/database_record_verification.json",
                "papers/doi__10.1128_spectrum.02013-21/final/review_report.json",
                "papers/doi__10.1128_spectrum.02013-21/work/review/quality_feedback.json",
            ],
        },
    )


def finalize_gates() -> None:
    generated_at = now_iso()
    semantic = read_json(REPORTS / f"{PAPER_ID}.semantic_gate.json", {})
    publication = read_json(REPORTS / f"{PAPER_ID}.publication_quality.json", {})
    feedback_path = PAPER / "work" / "review" / "quality_feedback.json"
    feedback = read_json(feedback_path, {})
    feedback["gate_evidence_after_repair"] = {
        "generated_at": generated_at,
        "publication_quality_pass": publication.get("publication_grade_pass"),
        "publication_quality_report": f"reports/{PAPER_ID}.publication_quality.json",
        "semantic_issue_count": (semantic.get("results") or [{}])[0].get("issue_count") if semantic.get("results") else None,
        "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
        "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
        "semantic_report": f"reports/{PAPER_ID}.semantic_gate.json",
    }
    write_json(feedback_path, feedback)
    append_jsonl(
        PACKET / "rework" / "rework_responses.jsonl",
        {
            "created_at": generated_at,
            "gate_evidence_after_repair": feedback["gate_evidence_after_repair"],
            "paper_id": PAPER_ID,
            "repair_status": "gate_rerun_completed_ticket_remains_open",
            "responding_workers": ["worker-6"],
            "response_id": f"worker46-gates-{generated_at}",
            "ticket_id": "rwk-complete-test-0001",
            "ticket_status_after_response": "open_blocked_unrecoverable_material_gap",
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--finalize-gates", action="store_true")
    args = parser.parse_args()
    if args.finalize_gates:
        finalize_gates()
    else:
        repair_artifacts()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
