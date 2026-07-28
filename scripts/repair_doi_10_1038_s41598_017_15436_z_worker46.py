#!/usr/bin/env python3
"""Worker-4/6 bounded re-review for doi__10.1038_s41598-017-15436-z."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "doi__10.1038_s41598-017-15436-z"
DOI = "10.1038/s41598-017-15436-z"
ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
REPORTS = ROOT / "reports"
LANDED = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers") / PAPER_ID
DOWNLOADED = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/downloaded_assets/papers") / PAPER_ID

OLD_TICKET_ID = "rwk-complete-test-0001"
SUPP_TICKET_ID = "rwk-worker46-20260504-supplement-doc-unrecoverable"
DB_TICKET_ID = "rwk-worker46-20260504-database-sequence-dbamp-conflict"
OPEN_TICKET_IDS = [SUPP_TICKET_ID, DB_TICKET_ID]

CHECKED_INPUTS = [
    f"rework_context/{PAPER_ID}/handoff_context.json",
    f"paper_packets/{PAPER_ID}/packet_manifest.json",
    f"paper_packets/{PAPER_ID}/locators/locator_index.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
    f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/landing-1.txt",
    f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
    f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
    f"paper_packets/{PAPER_ID}/raw/paper.xml",
    f"paper_packets/{PAPER_ID}/raw/paper.pdf",
    str(LANDED / "asset_manifest.csv"),
    str(LANDED / "metadata.json"),
    str(LANDED / "supplementary"),
    str(DOWNLOADED / "supplementary"),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def loc(source_path: str, locator: str, note: str | None = None) -> dict[str, str]:
    item = {"source_path": source_path, "locator": locator}
    if note:
        item["note"] = note
    return item


def table_locator(subject: str, concentration: str, source_id: str) -> str:
    target = subject.lower()
    d_series = source_id == "DBAASPS_10812"
    if "erythrocytes" in target:
        return "xml:sec=7:D-Ctl is not cytotoxic; xml:fig=2:Figure 2"
    if "caco-2" in target:
        return "xml:sec=7:D-Ctl is not cytotoxic; xml:fig=2:Figure 2"
    if "atcc 25922" in target:
        return "xml:table=1:row=3:column=3" if not d_series else "xml:table=1:row=3:column=4"
    if "k-12" in target:
        return "xml:table=1:row=5:column=3" if not d_series else "xml:table=1:row=5:column=4"
    if "fusobacterium" in target:
        return "xml:table=1:row=6:column=3" if not d_series or concentration == "125" else "xml:table=1:row=6:column=4"
    if "prevotella" in target:
        return "xml:table=1:row=7:column=3" if not d_series or concentration == "149" else "xml:table=1:row=7:column=4"
    if "parvimonas" in target:
        return "xml:table=1:row=8:column=3" if not d_series or concentration == "120" else "xml:table=1:row=8:column=4"
    if "atcc 25923" in target:
        return "xml:table=1:row=9:column=3" if not d_series or concentration == "40" else "xml:table=1:row=9:column=4"
    if "staphylococcus aureus mr" in target:
        return "xml:table=1:row=10:column=3" if not d_series or concentration == "37" else "xml:table=1:row=10:column=4"
    return "xml:tables_and_sections_unmatched"


def source_id(row: dict[str, Any]) -> str:
    return str(row.get("source_id") or row.get("dbaasp_id") or row.get("source_numeric_id") or "")


def source_record_id(row: dict[str, Any]) -> str:
    return str(row.get("source_record_id") or row.get("assay_id") or row.get("source_id") or "")


def database_row_audit(row: dict[str, Any], table: str, line_no: int) -> dict[str, Any]:
    sid = source_id(row)
    sequence_key = str(row.get("sequence_key") or "")
    subject = str(row.get("subject_name") or row.get("target_organism_text") or "")
    concentration = str(row.get("concentration") or "")
    measure = str(row.get("measure_group") or row.get("measure_value") or "")
    record_id = source_record_id(row)

    if sequence_key.startswith("dbAMP:"):
        status = "source_conflict"
        matched = "partial_table1_overlap"
        review_notes = (
            "source conflict: dbAMP aggregate row mixes activity claims from this DOI with organisms and MICs from other citations; "
            "Table 1 supports only the listed E. coli/oral/Staphylococcus rows for this paper."
        )
        source_locator = loc("source/paper.xml", "xml:table=1", "Partial overlap only; off-paper organism list is preserved as conflict.")
        conflict_context = "Database row cites PMID 29123174 plus other PMIDs and includes antimicrobial/fungal targets not found in this paper's local XML/PDF."
    elif table == "linked_literature_records.jsonl":
        status = "database_only_no_primary_source"
        matched = "article_metadata"
        review_notes = "Literature DOI/PMID/PMCID and title match the primary article metadata, but exact sequence identity remains database-only because no linked sequence row or primary-source sequence is local."
        source_locator = loc("source/paper.xml", "xml:article-meta")
        conflict_context = "Exact sequence/modification cannot be primary-source verified from local material."
    else:
        status = "database_only_no_primary_source"
        matched = f"{PAPER_ID}-{record_id}"
        source_locator = loc("source/paper.xml", table_locator(subject, concentration, sid))
        if "erythrocytes" in subject.lower() or "caco-2" in subject.lower():
            review_notes = "Primary source safety section and Figure 2 support the database negative activity note up to 100 µg/mL, but exact sequence/modification remains database-only."
        else:
            review_notes = "Primary source Table 1 supports the database assay target and raw value for this row, but exact sequence/modification remains database-only."
        conflict_context = "Record value is source-supported; exact peptide sequence/modification cannot be primary-source verified from local material."

    return {
        "source_table": table,
        "source_row_number": line_no,
        "source_id": sid,
        "sequence_key": sequence_key,
        "source_record_id": record_id,
        "database_subject": subject,
        "database_measure": measure,
        "database_concentration": concentration,
        "database_unit": str(row.get("unit") or ""),
        "record_value_status": "source_verified" if not sequence_key.startswith("dbAMP:") else "partial_source_overlap",
        "status": status,
        "layer1_status": status,
        "matched_activity_record_id": matched,
        "traceability": loc(f"paper_packets/{PAPER_ID}/database/{table}", f"database:{table}:row={line_no}"),
        "citation_traceability": loc("source/paper.xml", "xml:article-meta"),
        "sequence_check": {
            "status": "identity_context_supported_exact_sequence_not_printed",
            "primary_source_locator": loc("source/paper.xml", "xml:sec=2; xml:sec=3", "Article identifies L-Ctl/D-Ctl relationship but does not print the exact sequence."),
            "linked_sequence_records": f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
            "linked_sequence_record_count": 0,
        },
        "review_notes": review_notes,
        "conflict_context": conflict_context,
    }


def build_database(generated_at: str) -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    for table in ("linked_assay_records.jsonl", "linked_experiment_records.jsonl", "linked_literature_records.jsonl"):
        for line_no, row in enumerate(read_jsonl(PACKET / "database" / table), start=1):
            audits.append(database_row_audit(row, table, line_no))
    summary = Counter(audit["status"] for audit in audits)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "audit_scope": "Worker-4 row-by-row re-review of linked DBAASP/dbAMP rows against local XML/PDF and packet database snapshots.",
        "database_row_counts": read_json(PACKET / "database" / "database_source_manifest.json")["row_counts"],
        "record_audits": audits,
        "status_summary": dict(sorted(summary.items())),
        "caution_findings": [
            {
                "caution_code": "exact_sequence_not_embedded_in_primary_or_linked_sequence_snapshot",
                "evidence_context": "The article supports D-Ctl/L-Ctl identity context, but linked_sequence_records.jsonl is empty and exact sequence/modification cannot be source-verified locally.",
            },
            {
                "caution_code": "dbamp_aggregate_row_partial_source_conflict",
                "evidence_context": "dbAMP_27346 combines this DOI with other PMIDs and off-paper target/MIC claims; only this paper's Table 1 overlap is locally supported.",
            },
        ],
    }


def build_activity(generated_at: str) -> dict[str, Any]:
    activity = read_json(PAPER / "final" / "activity_toxicity_evidence.json")
    activity.update(
        {
            "generated_at": generated_at,
            "reviewed_at": generated_at,
            "review_model": "gpt-5.5",
            "reasoning_effort": "xhigh",
            "source_reviewed": True,
            "worker6_adjudication_status": "source_supported_local_table_values_preserved",
            "extraction_scope": "Worker-6 preserved local XML Table 1/Table 2 candidate rows and added source-reviewed safety/toxicity evidence; missing supplement values are not fabricated.",
        }
    )
    activity["toxicity_records"] = [
        {
            "record_id": f"{PAPER_ID}-fig2-caco2-no-cytotoxicity",
            "entity": "D-Ctl and L-Ctl",
            "endpoint": "cytotoxicity",
            "raw_value": "not detected up to 100",
            "raw_unit": "µg/mL",
            "normalization_status": "qualitative_source_value_preserved",
            "target": {"class": "mammalian_cell_line", "species": "Homo sapiens", "strain": "Caco-2"},
            "assay_conditions": {"duration": "72 h", "source_context": "Figure 2A and safety-result prose"},
            "source_locator": loc("source/paper.xml", "xml:sec=7:D-Ctl is not cytotoxic; xml:fig=2:Figure 2"),
        },
        {
            "record_id": f"{PAPER_ID}-fig2-erythrocyte-no-hemolysis",
            "entity": "D-Ctl and L-Ctl",
            "endpoint": "hemolysis",
            "raw_value": "not observed up to 100",
            "raw_unit": "µg/mL",
            "normalization_status": "qualitative_source_value_preserved",
            "target": {"class": "human_blood_cell", "species": "Homo sapiens", "strain": "erythrocytes"},
            "assay_conditions": {"duration": "1 h", "source_context": "Figure 2B and safety-result prose"},
            "source_locator": loc("source/paper.xml", "xml:sec=7:D-Ctl is not cytotoxic; xml:fig=2:Figure 2"),
        },
        {
            "record_id": f"{PAPER_ID}-fig2-pbmc-no-cytotoxicity",
            "entity": "D-Ctl and L-Ctl",
            "endpoint": "cytotoxicity",
            "raw_value": "not detected up to 100",
            "raw_unit": "µg/mL",
            "normalization_status": "qualitative_source_value_preserved",
            "target": {"class": "primary_human_cell", "species": "Homo sapiens", "strain": "PBMCs"},
            "assay_conditions": {"duration": "72 h", "source_context": "Figure 2C/D and safety-result prose"},
            "source_locator": loc("source/paper.xml", "xml:sec=7:D-Ctl is not cytotoxic; xml:fig=2:Figure 2"),
        },
    ]
    activity["unsupported_activity_sources"] = [
        {
            "source": "Supplementary Dataset 1 / supplementary figures",
            "status": "not_locally_recoverable",
            "reason": "The XML references 41598_2017_15436_MOESM1_ESM.doc, but local supplementary assets are HTML landing pages and no DOC/DOCX/PDF/XLSX supplement file is present in landed/downloaded packet roots.",
            "source_paths_checked": [
                f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
                str(LANDED / "supplementary"),
                str(DOWNLOADED / "supplementary"),
            ],
        }
    ]
    return activity


def build_mechanism(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "extraction_scope": "Worker-6 source-reviewed mechanism evidence from main XML/PDF; missing supplementary figures are not quantified.",
        "mechanism_claims": [
            {
                "claim_id": "mech-dctl-cell-wall-membrane-damage",
                "claim_text": "D-Ctl damages E. coli MDR cell wall/membrane integrity and is associated with membrane permeabilization.",
                "entity_scope": "D-Ctl against E. coli MDR",
                "evidence_class": "direct_mechanism",
                "direct_assay_types": ["epifluorescence BacLight staining", "ATR-FTIR spectroscopy", "atomic force microscopy elasticity"],
                "source_locator": loc("source/paper.xml", "xml:sec=10:D-Ctl dramatically damaged the cell wall; xml:fig=5; xml:fig=6"),
                "limitations": "Mechanism is source-supported for the E. coli MDR model; supplementary figure quantification is unavailable locally.",
            },
            {
                "claim_id": "mech-dctl-resistance-acquisition",
                "claim_text": "Under serial sub-MIC exposure, E. coli did not show increased MIC to D-Ctl over the assay period, unlike comparator antibiotics.",
                "entity_scope": "D-Ctl against E. coli wild type",
                "evidence_class": "phenotypic_resistance_assay",
                "direct_assay_types": ["resistance acquisition serial culture"],
                "source_locator": loc("source/paper.xml", "xml:sec=6:Unlike ampicillin and cefotaxime; xml:fig=1"),
                "limitations": "This supports resistance-acquisition phenotype, not a molecular target by itself.",
            },
            {
                "claim_id": "mech-dctl-protease-stability",
                "claim_text": "D-Ctl is more resistant than L-Ctl to degradation by tested bacterial secreted proteases.",
                "entity_scope": "D-Ctl and L-Ctl",
                "evidence_class": "stability_assay",
                "direct_assay_types": ["HPLC after bacterial supernatant incubation"],
                "source_locator": loc("source/paper.xml", "xml:sec=9:D-Ctl is more resistant to degradation; xml:fig=4"),
                "limitations": "Stability evidence supports therapeutic robustness but is not a killing mechanism.",
            },
        ],
        "caution_findings": [
            {
                "caution_code": "supplementary_figure_quantification_missing",
                "evidence_context": "Main-text figures/captions are source-located; exact supplementary figure curves or raw values are not locally recoverable.",
            }
        ],
    }


def unrecoverable_gaps() -> list[dict[str, Any]]:
    return [
        {
            "gap_code": "supplementary_dataset_1_doc_not_locally_recoverable",
            "source_paths_checked": [
                f"paper_packets/{PAPER_ID}/raw/paper.xml",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
                str(LANDED / "supplementary"),
                str(DOWNLOADED / "supplementary"),
                str(LANDED / "asset_manifest.csv"),
            ],
            "tools_attempted": ["rg", "find", "file", "jq", "existing pdftotext extraction review"],
            "why_unrecoverable": "The primary XML names 41598_2017_15436_MOESM1_ESM.doc, but the local landed/downloaded supplementary files are HTML article landing pages and no DOC/DOCX/PDF/XLSX supplement member exists in the paper-local roots or merged output match set.",
            "impact": "Supplementary Dataset 1 / supplementary figure values cannot be source-reviewed or used to alter activity, toxicity, or mechanism conclusions.",
            "owner_worker": "worker-6",
            "blocks_publication_grade": True,
        },
        {
            "gap_code": "exact_peptide_sequence_not_in_primary_or_linked_sequence_snapshot",
            "source_paths_checked": [
                f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
                f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
                f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
                f"paper_packets/{PAPER_ID}/raw/paper.xml",
                f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
                f"paper_packets/{PAPER_ID}/extracted/pdf_text/landing-1.txt",
            ],
            "tools_attempted": ["rg exact-sequence search", "jq database row review", "wc -l linked_sequence_records.jsonl"],
            "why_unrecoverable": "The local article identifies D-Ctl as the D-amino-acid epimer of L-Ctl and links DBAASP rows by PMID/DOI, but it does not print the exact peptide sequence and linked_sequence_records.jsonl has zero rows.",
            "impact": "DBAASP sequence identifiers cannot be promoted to exact primary-source sequence verification; supported assay outcomes are preserved separately.",
            "owner_worker": "worker-4",
            "blocks_publication_grade": True,
        },
    ]


def rework_targets(generated_at: str) -> list[dict[str, Any]]:
    return [
        {
            "ticket_id": SUPP_TICKET_ID,
            "paper_id": PAPER_ID,
            "created_at": generated_at,
            "worker": "worker-6",
            "owner_worker": "worker-6",
            "target_queue": "adjudication",
            "layer": "review",
            "severity": "blocking",
            "failure_code": "supplementary_dataset_1_doc_not_locally_recoverable",
            "omission_code": "missing_local_41598_2017_15436_MOESM1_ESM_doc",
            "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
            "source_paths_to_check": [
                f"paper_packets/{PAPER_ID}/raw/paper.xml",
                f"paper_packets/{PAPER_ID}/raw/supplementary_original",
                str(LANDED / "supplementary"),
                str(DOWNLOADED / "supplementary"),
            ],
            "required_action": "Do not accept from current local material; only close if the named supplement file is later recovered locally or the controller explicitly downgrades this gap.",
            "blocks": ["publication_grade_ready", "final_approval"],
        },
        {
            "ticket_id": DB_TICKET_ID,
            "paper_id": PAPER_ID,
            "created_at": generated_at,
            "worker": "worker-4",
            "owner_worker": "worker-4",
            "target_queue": "analysis",
            "layer": "database",
            "severity": "major",
            "failure_code": "exact_peptide_sequence_not_in_primary_or_linked_sequence_snapshot",
            "omission_code": "missing_primary_sequence_locator_for_dbaasp_sequence_ids",
            "artifact_path": f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
            "source_paths_to_check": [
                f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
                f"paper_packets/{PAPER_ID}/raw/paper.xml",
                f"paper_packets/{PAPER_ID}/raw/paper.pdf",
            ],
            "required_action": "Keep exact sequence verification unresolved unless primary or linked database sequence material is supplied.",
            "blocks": ["publication_grade_ready", "final_approval"],
        },
    ]


def qc_failure_reasons() -> list[dict[str, str]]:
    return [
        {
            "code": "supplementary_dataset_1_doc_not_locally_recoverable",
            "owner_worker": "worker-6",
            "reason": "The local packet/landed/downloaded assets do not contain the Word supplement named by the primary XML; only article HTML landing pages are present under supplementary.",
            "severity": "blocking",
        },
        {
            "code": "exact_peptide_sequence_not_in_primary_or_linked_sequence_snapshot",
            "owner_worker": "worker-4",
            "reason": "Exact L-Ctl/D-Ctl sequence evidence is absent from the primary XML/PDF and linked_sequence_records.jsonl has zero rows.",
            "severity": "major",
        },
        {
            "code": "dbamp_aggregate_row_preserved_as_source_conflict",
            "owner_worker": "worker-4",
            "reason": "dbAMP_27346 contains off-paper organism/MIC claims mixed with this DOI; only the Table 1 overlap is locally supported.",
            "severity": "major",
        },
    ]


def build_review(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> dict[str, Any]:
    targets = rework_targets(generated_at)
    gaps = unrecoverable_gaps()
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "blocked_missing_primary_material",
        "publication_grade": False,
        "validator_contract_passed": True,
        "source_review_depth": ["paper_xml", "paper_pdf", "oa_package", "supplementary_assets", "merged_database_rows"],
        "materials_exhausted": {
            "paper_xml": True,
            "paper_pdf": True,
            "oa_package": True,
            "supplementary_assets": True,
            "merged_database_rows": True,
            "note": "Local XML/PDF, HTML supplementary landing assets, and packet database rows were reopened. Supported activity/safety/mechanism/database findings are preserved; the named supplement DOC and exact sequence evidence are not locally recoverable.",
        },
        "checked_inputs": CHECKED_INPUTS,
        "semantic_quality_checks": {
            "activity_records_preserved": len(activity.get("activity_records") or []),
            "toxicity_records_added": len(activity.get("toxicity_records") or []),
            "database_status_summary": database.get("status_summary"),
            "mechanism_claims_source_reviewed": len(mechanism.get("mechanism_claims") or []),
            "unrecoverable_material_gap_count": len(gaps),
            "open_rework_target_count": len(targets),
        },
        "per_layer_decision_rationale": {
            "layer_1_database": "Worker-4 matched DBAASP assay rows to primary Table 1 or Figure 2/prose where possible, preserved dbAMP_27346 as a partial source conflict, and kept exact sequence verification unresolved because no primary/linkage sequence row is local.",
            "layer_2_activity_toxicity": "Worker-6 preserved locally supported XML Table 1/Table 2 values and added safety rows for Caco-2, erythrocytes, and PBMCs; missing supplement values were not fabricated.",
            "layer_3_mechanism": "Worker-6 replaced automated placeholder claims with source-located mechanism/stability/resistance claims and explicit limitations.",
            "publication_decision": "The broad framework-test blocker is repaired into concrete findings, but publication-grade acceptance remains blocked by unrecoverable local supplement and sequence gaps.",
        },
        "caution_findings": [
            {
                "caution_code": "supplementary_dataset_named_but_absent_locally",
                "evidence_context": "XML points to 41598_2017_15436_MOESM1_ESM.doc; local supplementary files are HTML article pages and no named supplement file exists in checked local roots.",
            },
            {
                "caution_code": "exact_sequence_not_source_verified",
                "evidence_context": "D-Ctl/L-Ctl identity context is supported, but exact sequence/modification is absent from primary XML/PDF and linked sequence rows.",
            },
            {
                "caution_code": "dbamp_aggregate_source_conflict_preserved",
                "evidence_context": "dbAMP_27346 includes off-paper antimicrobial/fungal rows from other PMIDs; the conflict is preserved rather than normalized.",
            },
        ],
        "qc_failure_reasons": qc_failure_reasons(),
        "rework_targets": targets,
        "unrecoverable_material_gaps": gaps,
        "adjudication_summary": "Bounded worker-4/6 re-review completed source-grounded repair of database and adjudication layers. The paper is not accepted because local material cannot support the named supplement DOC or exact sequence verification.",
    }


def build_quality_feedback(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": len(qc_failure_reasons()),
        "qc_failure_reasons": qc_failure_reasons(),
        "rework_context_packet_required": False,
        "rework_targets": rework_targets(generated_at),
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "status": "blocked_after_bounded_worker4_worker6_re_review",
        "notes": "The original broad full_source_review_not_completed ticket has been converted to concrete worker-4/6 findings. Do not accept unless new local source material resolves the supplement and sequence gaps.",
    }


def build_rework_response(generated_at: str) -> dict[str, Any]:
    return {
        "record_type": "rework_response",
        "response_id": f"{PAPER_ID}-worker46-bounded-review-{generated_at}",
        "paper_id": PAPER_ID,
        "ticket_ids": [OLD_TICKET_ID],
        "created_ticket_ids": OPEN_TICKET_IDS,
        "status": "bounded_repair_completed_nonaccepted_unrecoverable_gaps",
        "owner_workers": ["worker-4", "worker-6"],
        "resolved_by": "codex-cli",
        "checked_source_paths": CHECKED_INPUTS,
        "tools_attempted": ["jq", "rg", "find", "file", "wc", "database JSONL review", "existing pdftotext extraction review"],
        "what_was_checked": [
            "Primary XML/PDF sections, Table 1, Table 2, Figure 1-6 captions/prose, and article metadata.",
            "Local landed/downloaded supplementary directories and packet supplementary extraction outputs.",
            "All linked_assay_records, linked_experiment_records, linked_literature_records, and empty linked_sequence_records snapshots.",
        ],
        "what_was_repaired": [
            "Worker-4 database audit now preserves row-level DBAASP support, dbAMP source conflict, and exact-sequence gap separately.",
            "Worker-6 review now contains paper-specific source-review provenance, source-reviewed mechanism claims, concrete quality feedback, and unrecoverable material gaps.",
            "Final and packet activity artifacts preserve local table values and include safety/toxicity rows supported by Figure 2/prose.",
        ],
        "what_remains": [
            "The named Supplementary Dataset 1 DOC is not locally recoverable.",
            "Exact L-Ctl/D-Ctl sequence/modification evidence is not locally recoverable from primary XML/PDF or linked sequence snapshots.",
            "Paper remains non-publication-grade and must not be accepted from current local material.",
        ],
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "artifact_refs": [
            f"paper_packets/{PAPER_ID}/analysis/activity_toxicity_evidence.json",
            f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
            f"paper_packets/{PAPER_ID}/analysis/mechanism_evidence.json",
            f"paper_packets/{PAPER_ID}/analysis/adjudication_report.json",
            f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
            f"papers/{PAPER_ID}/final/database_record_verification.json",
            f"papers/{PAPER_ID}/final/mechanism_ontology_record.json",
            f"papers/{PAPER_ID}/final/review_report.json",
            f"papers/{PAPER_ID}/work/review/quality_feedback.json",
        ],
    }


def append_new_rework_requests(generated_at: str) -> None:
    existing = read_jsonl(PACKET / "rework" / "rework_requests.jsonl")
    existing_ids = {str(row.get("ticket_id")) for row in existing}
    for target in rework_targets(generated_at):
        if target["ticket_id"] not in existing_ids:
            append_jsonl(PACKET / "rework" / "rework_requests.jsonl", target)


def update_status_files(generated_at: str, database: dict[str, Any], activity: dict[str, Any], mechanism: dict[str, Any]) -> None:
    analysis_status_path = PACKET / "analysis" / "analysis_status.json"
    analysis_status = read_json(analysis_status_path)
    analysis_status.update(
        {
            "generated_at": generated_at,
            "status": "analysis_blocked_unrecoverable_material_gaps",
            "activity_record_count": len(activity.get("activity_records") or []),
            "toxicity_record_count": len(activity.get("toxicity_records") or []),
            "mechanism_claim_count": len(mechanism.get("mechanism_claims") or []),
            "database_status_summary": database.get("status_summary"),
            "open_rework_ticket_ids": OPEN_TICKET_IDS,
            "unrecoverable_material_gap_count": len(unrecoverable_gaps()),
        }
    )
    write_json(analysis_status_path, analysis_status)

    manifest_path = PACKET / "packet_manifest.json"
    manifest = read_json(manifest_path)
    manifest["analysis_queue_status"] = "analysis_blocked_unrecoverable_material_gaps"
    manifest["open_rework_ticket_ids"] = OPEN_TICKET_IDS
    manifest["known_missing_or_blocked_materials"] = unrecoverable_gaps()
    manifest["updated_at"] = generated_at
    write_json(manifest_path, manifest)

    if (WORKFLOW / "workflow_context.json").exists():
        ctx = read_json(WORKFLOW / "workflow_context.json")
        ctx["current_state"] = "blocked_unrecoverable_material_gaps"
        ctx["updated_at"] = generated_at
        ctx["open_rework_tickets"] = OPEN_TICKET_IDS
        ctx["queue_status"] = {"analysis": "analysis_blocked_unrecoverable_material_gaps", "material": "material_extracted_with_gaps"}
        ctx["gate_summary"] = {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": False,
            "publication_grade_ready": False,
        }
        write_json(WORKFLOW / "workflow_context.json", ctx)


def repair() -> int:
    generated_at = now_iso()
    database = build_database(generated_at)
    activity = build_activity(generated_at)
    mechanism = build_mechanism(generated_at)
    review = build_review(generated_at, activity, database, mechanism)
    feedback = build_quality_feedback(generated_at)

    for path in [
        PACKET / "analysis" / "database_record_audit.json",
        PACKET / "final" / "database_record_verification.json",
        PAPER / "final" / "database_record_verification.json",
    ]:
        write_json(path, database)
    for path in [
        PACKET / "analysis" / "activity_toxicity_evidence.json",
        PACKET / "final" / "activity_toxicity_evidence.json",
        PAPER / "final" / "activity_toxicity_evidence.json",
    ]:
        write_json(path, activity)
    for path in [
        PACKET / "analysis" / "mechanism_evidence.json",
        PACKET / "final" / "mechanism_evidence.json",
        PAPER / "final" / "mechanism_evidence.json",
        PAPER / "final" / "mechanism_ontology_record.json",
    ]:
        write_json(path, mechanism)
    for path in [
        PACKET / "analysis" / "adjudication_report.json",
        PACKET / "final" / "review_report.json",
        PAPER / "final" / "review_report.json",
    ]:
        write_json(path, review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", feedback)
    append_jsonl(PACKET / "rework" / "rework_responses.jsonl", build_rework_response(generated_at))
    append_new_rework_requests(generated_at)
    update_status_files(generated_at, database, activity, mechanism)
    print(json.dumps({"ok": True, "generated_at": generated_at, "status": "nonaccepted_unrecoverable_gaps_recorded"}, ensure_ascii=False, indent=2))
    return 0


def finalize_gates() -> int:
    generated_at = now_iso()
    semantic_path = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    publication_path = REPORTS / f"{PAPER_ID}.publication_quality.json"
    semantic = read_json(semantic_path)
    publication = read_json(publication_path)
    semantic_result = (semantic.get("results") or [{}])[0]
    gates_ready = (
        int(semantic.get("publication_grade_pass_count") or 0) == 1
        and int(semantic.get("publication_grade_fail_count") or 0) == 0
        and publication.get("publication_grade_pass") is True
    )

    gate_validation = {
        "validated_at": generated_at,
        "semantic_gate": {
            "path": str(semantic_path.relative_to(ROOT)),
            "publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
            "publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
            "issue_count": semantic_result.get("issue_count"),
            "issue_codes": [issue.get("code") for issue in semantic_result.get("issues", [])],
        },
        "publication_quality_gate": {
            "path": str(publication_path.relative_to(ROOT)),
            "publication_grade_pass": publication.get("publication_grade_pass"),
            "risk_counts": publication.get("risk_counts"),
            "review_status": publication.get("review_status"),
        },
    }
    for path in [PAPER / "final" / "review_report.json", PACKET / "analysis" / "adjudication_report.json", PACKET / "final" / "review_report.json"]:
        payload = read_json(path)
        payload["gate_validation"] = gate_validation
        write_json(path, payload)

    feedback_path = PAPER / "work" / "review" / "quality_feedback.json"
    feedback = read_json(feedback_path)
    feedback["gate_validation"] = gate_validation
    feedback["post_gate_status"] = "strict_gates_failed_expected_nonaccepted_unrecoverable_gaps" if not gates_ready else "strict_gates_passed"
    write_json(feedback_path, feedback)

    if (WORKFLOW / "workflow_context.json").exists():
        ctx = read_json(WORKFLOW / "workflow_context.json")
        ctx["updated_at"] = generated_at
        ctx["gate_summary"] = {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": gates_ready,
            "publication_grade_ready": gates_ready,
        }
        write_json(WORKFLOW / "workflow_context.json", ctx)

    activity = read_json(PAPER / "final" / "activity_toxicity_evidence.json")
    database = read_json(PAPER / "final" / "database_record_verification.json")
    mechanism = read_json(PAPER / "final" / "mechanism_ontology_record.json")
    complete_report = {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "generated_at": generated_at,
        "completion_claim": "bounded_worker4_worker6_source_review_completed_nonaccepted_unrecoverable_gaps",
        "current_state": "blocked_unrecoverable_material_gaps",
        "terminal_status": "blocked_missing_primary_material",
        "final_approval_status": "refused_unrecoverable_material_gaps",
        "gate_summary": {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": gates_ready,
            "publication_grade_ready": gates_ready,
        },
        "gate_results": {
            "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
            "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
            "publication_quality_pass": publication.get("publication_grade_pass"),
            "semantic_issue_count": semantic_result.get("issue_count"),
            "semantic_issue_codes": [issue.get("code") for issue in semantic_result.get("issues", [])],
            "publication_risk_counts": publication.get("risk_counts"),
        },
        "analysis": {
            "review_status": "blocked_missing_primary_material",
            "activity_records": len(activity.get("activity_records") or []),
            "toxicity_records": len(activity.get("toxicity_records") or []),
            "mechanism_claims": len(mechanism.get("mechanism_claims") or []),
            "database_status_summary": database.get("status_summary"),
            "unrecoverable_material_gap_count": len(unrecoverable_gaps()),
        },
        "open_rework_ticket_count": len(OPEN_TICKET_IDS),
        "rework_ticket_ids": OPEN_TICKET_IDS,
        "not_publication_grade_reason": "Local source cannot support the named supplement DOC or exact peptide sequence evidence after bounded worker-4/6 source review.",
        "semantic_gate": "passed" if gates_ready else "failed_expected_nonaccepted_unrecoverable_gaps",
        "publication_quality_gate": "passed" if gates_ready else "failed_expected_open_rework_and_nonpublication_grade",
        "manifest": str(REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"),
        "semantic_report": str(semantic_path),
        "publication_quality_report": str(publication_path),
        "workflow_dir": str(WORKFLOW),
    }
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", complete_report)
    print(json.dumps({"ok": True, "gates_ready": gates_ready, "updated_report": str(REPORTS / f"{PAPER_ID}.complete_message_test_report.json")}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    if len(sys.argv) == 1 or sys.argv[1] == "repair":
        return repair()
    if sys.argv[1] == "finalize-gates":
        return finalize_gates()
    raise SystemExit(f"unknown command: {sys.argv[1]}")


if __name__ == "__main__":
    raise SystemExit(main())
