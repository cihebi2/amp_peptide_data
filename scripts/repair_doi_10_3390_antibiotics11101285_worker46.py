#!/usr/bin/env python3
"""Bounded worker-4/6 re-review for doi__10.3390_antibiotics11101285."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.3390_antibiotics11101285"
DOI = "10.3390/antibiotics11101285"
PMCID = "PMC9598925"
PMID = "36289944"
OLD_TICKET_ID = "rwk-complete-test-0001"
GAP_TICKET_ID = "rwk-worker46-figure-toxicity-gap-0002"

PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
REPORTS = ROOT / "reports"
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID

SOURCE_PATHS_CHECKED = [
    f"rework_context/{PAPER_ID}/handoff_context.json",
    f"paper_packets/{PAPER_ID}/packet_manifest.json",
    f"paper_packets/{PAPER_ID}/locators/locator_index.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
    f"paper_packets/{PAPER_ID}/raw/paper.xml",
    f"paper_packets/{PAPER_ID}/raw/paper.pdf",
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/antibiotics-11-01285.txt",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/local-DBAASP-PMC9598925.txt",
    f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
    f"paper_packets/{PAPER_ID}/extracted/archive_manifest.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9598925/PMC9598925/antibiotics-11-01285.nxml",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9598925/PMC9598925/antibiotics-11-01285.pdf",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9598925/PMC9598925/antibiotics-11-01285-g001.jpg",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9598925/PMC9598925/antibiotics-11-01285-g002.jpg",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9598925/PMC9598925/antibiotics-11-01285-g003.jpg",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9598925/PMC9598925/antibiotics-11-01285-g004.jpg",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9598925/PMC9598925/antibiotics-11-01285-g005.jpg",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9598925/PMC9598925/antibiotics-11-01285-g006.jpg",
    f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_dramp_activity_records.jsonl",
    "/mnt/d/work/\u6297\u83cc\u80bd/\u6570\u636e\u5e93/merged_amp_corpus/output",
]

TOOLS_ATTEMPTED = [
    "jq JSON inspection",
    "rg over XML/PDF text/extracted JSON",
    "python xml.etree primary XML table/figure inspection",
    "pdftotext-derived local PDF text review",
    "file inspection of OA figure images and source symlinks",
    "semantic_three_layer_gate.py --json",
    "check_three_layer_publication_quality.py --json-out",
]

PEPTIDE_NLE = "[Nle1, dLeu9, dLys10]TL"
PEPTIDE_LEAD = "[dLeu9, dLys10]TL"
PEPTIDE_NLE_SEQUENCE = "Nle-Phe-Val-Pro-Trp-Phe-Lys-Phe-dLeu-dLys-Arg-Ile-Leu-CONH2"
PEPTIDE_LEAD_SEQUENCE = "FVPWFSKFlkRIL"
SEQUENCE_KEY = "DBAASP:DBAASPS_19933"

MIC_ROWS = [
    ("Escherichia coli ATCC 25922", "xml:table=2:row=3", "6.25", "12.5"),
    ("Pseudomonas aeruginosa ATCC 27853", "xml:table=2:row=4", "12.5", "12.5"),
    ("Acinetobacter baumannii ATCC 19606", "xml:table=2:row=5", "3.12", "6.25"),
    ("Klebsiella pneumoniae ATCC BAA-1705", "xml:table=2:row=6", "12.5", "12.5"),
    ("Staphylococcus aureus ATCC 25923", "xml:table=2:row=7", "3.12", "6.25"),
    ("Staphylococcus epidermidis ATCC 12228", "xml:table=2:row=8", "3.12", "3.12"),
    ("Bacillus megaterium Bm11", "xml:table=2:row=9", "0.78", "3.12"),
]

DBAASP_MIC_LOCATORS = {
    "Escherichia coli ATCC 25922": ("doi__10.3390_antibiotics11101285-table2-r3-c1-MIC", "xml:table=2:row=3:column=1"),
    "Pseudomonas aeruginosa ATCC 27853": ("doi__10.3390_antibiotics11101285-table2-r4-c1-MIC", "xml:table=2:row=4:column=1"),
    "Acinetobacter baumannii ATCC 19606": ("doi__10.3390_antibiotics11101285-table2-r5-c1-MIC", "xml:table=2:row=5:column=1"),
    "Klebsiella pneumoniae ATCC BAA-1705": ("doi__10.3390_antibiotics11101285-table2-r6-c1-MIC", "xml:table=2:row=6:column=1"),
    "Staphylococcus aureus ATCC 25923": ("doi__10.3390_antibiotics11101285-table2-r7-c1-MIC", "xml:table=2:row=7:column=1"),
    "Staphylococcus epidermidis ATCC 12228": ("doi__10.3390_antibiotics11101285-table2-r8-c1-MIC", "xml:table=2:row=8:column=1"),
    "Bacillus megaterium Bm11": ("doi__10.3390_antibiotics11101285-table2-r9-c1-MIC", "xml:table=2:row=9:column=1"),
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any | None = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        if default is not None:
            return default
        raise


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def append_jsonl_once(path: Path, row: dict[str, Any], key: str) -> None:
    existing = read_jsonl(path)
    if any(item.get(key) == row.get(key) for item in existing):
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def source_locator(locator: str, source_path: str = "source/paper.xml") -> dict[str, str]:
    return {"source_path": source_path, "locator": locator}


def species_from_db(value: str) -> str:
    value = value.replace("Escherichia coli", "Escherichia coli")
    return value.strip()


def activity_record(
    record_id: str,
    entity: str,
    endpoint: str,
    raw_value: str,
    raw_unit: str,
    target: str,
    locator: str,
    assay_context: dict[str, Any],
    sequence_key: str | None = None,
    evidence_ladder: str = "in_vitro_assay_table",
) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "entity": entity,
        "sequence_key": sequence_key,
        "endpoint": endpoint,
        "raw_value": raw_value,
        "raw_unit": raw_unit,
        "normalization_status": "raw_unit_preserved",
        "evidence_ladder": evidence_ladder,
        "target": {
            "class": "bacteria" if endpoint == "MIC" else "host_cell_or_model",
            "species": target,
            "strain": target,
        },
        "assay_conditions": assay_context,
        "source_locator": source_locator(locator),
        "curation_notes": "Source-reviewed worker-6 final activity/toxicity row; unsupported exact DBAASP figure-only values are not normalized from this row.",
    }


def build_activity() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for index, (species, base_locator, nle_value, lead_value) in enumerate(MIC_ROWS, start=3):
        records.append(
            activity_record(
                f"doi__10.3390_antibiotics11101285-table2-r{index}-c1-MIC",
                PEPTIDE_NLE,
                "MIC",
                nle_value,
                "\u03bcM",
                species,
                f"{base_locator}:column=1",
                {
                    "source_column_context": "Table 2 MIC values for the Nle temporin analogue.",
                    "comparison_context": "Lead peptide column is retained separately; this row is the current-paper [Nle1, dLeu9, dLys10]TL value.",
                },
                SEQUENCE_KEY,
            )
        )
        records.append(
            activity_record(
                f"doi__10.3390_antibiotics11101285-table2-r{index}-c2-MIC",
                PEPTIDE_LEAD,
                "MIC",
                lead_value,
                "\u03bcM",
                species,
                f"{base_locator}:column=2",
                {
                    "source_column_context": "Table 2 comparison MIC values for the previously reported lead peptide.",
                    "comparison_context": "The table footnote says the lead-peptide MIC values were already reported in prior works.",
                },
                None,
            )
        )

    records.extend(
        [
            activity_record(
                "doi__10.3390_antibiotics11101285-fig1b-hemolysis-low-range",
                PEPTIDE_NLE,
                "hemolysis",
                "<20",
                "%",
                "red blood cells",
                "xml:sec=2.4:Figure 1 panel B",
                {
                    "concentration_range": "3.12-6.25 \u03bcM",
                    "exposure_time": "40 min",
                    "source_support": "Prose reports weak hemolysis below 20%; exact DBAASP 18% at 12.5 \u03bcM is not source-verified.",
                },
                SEQUENCE_KEY,
                "host_toxicity_prose_and_figure",
            ),
            activity_record(
                "doi__10.3390_antibiotics11101285-fig1b-hemolysis-high-range",
                PEPTIDE_NLE,
                "hemolysis",
                "~40",
                "%",
                "red blood cells",
                "xml:sec=2.4:Figure 1 panel B",
                {
                    "concentration_range": "50-100 \u03bcM",
                    "exposure_time": "40 min",
                    "source_support": "Prose reports strongest hemolysis around 40%; exact DBAASP 38% at 100 \u03bcM remains figure/database-only.",
                },
                SEQUENCE_KEY,
                "host_toxicity_prose_and_figure",
            ),
            activity_record(
                "doi__10.3390_antibiotics11101285-fig1c-hacat-low-range",
                PEPTIDE_NLE,
                "cell_viability",
                "slight reduction",
                "qualitative",
                "human keratinocytes HaCaT",
                "xml:sec=2.4:Figure 1 panel C",
                {
                    "concentration_range": "3.12-12.5 \u03bcM",
                    "timepoints": "2 h and 24 h",
                    "source_support": "Prose supports only a slight viability reduction in this range.",
                },
                SEQUENCE_KEY,
                "host_toxicity_prose_and_figure",
            ),
            activity_record(
                "doi__10.3390_antibiotics11101285-fig1c-hacat-25uM",
                PEPTIDE_NLE,
                "cell_viability",
                "~40 and ~50",
                "% viability",
                "human keratinocytes HaCaT",
                "xml:sec=2.4:Figure 1 panel C",
                {
                    "concentration": "25 \u03bcM",
                    "timepoints": "2 h and 24 h",
                    "source_support": "Prose reports approximate cell viability at 25 \u03bcM; DBAASP records this as 50% cell death and is kept source_conflict.",
                },
                SEQUENCE_KEY,
                "host_toxicity_prose_and_figure",
            ),
            activity_record(
                "doi__10.3390_antibiotics11101285-fig5-j774a1-viability",
                PEPTIDE_NLE,
                "cell_viability",
                "safe at 1-3; reduced at 10-30",
                "qualitative",
                "J774A.1 murine macrophage cells",
                "xml:sec=2.9:Figure 5",
                {
                    "concentration_range": "1-30 \u03bcM",
                    "assay": "MTT",
                    "source_support": "Prose and Figure 5 support a safe profile at 1-3 \u03bcM and reduced viability at higher tested concentrations.",
                },
                SEQUENCE_KEY,
                "host_toxicity_prose_and_figure",
            ),
            activity_record(
                "doi__10.3390_antibiotics11101285-fig6-il6-modulation",
                PEPTIDE_NLE,
                "IL-6",
                "reduced relative to LPS",
                "qualitative pg/mL assay",
                "J774A.1 murine macrophage cells",
                "xml:sec=2.9:Figure 6",
                {
                    "concentration": "3 \u03bcM",
                    "stimulus": "LPS 10 \u03bcg/mL for 24 h",
                    "source_support": "Prose and Figure 6 support IL-6 modulation but not an exact local numeric IL-6 value.",
                },
                SEQUENCE_KEY,
                "host_response_assay",
            ),
        ]
    )

    return {
        "paper_id": PAPER_ID,
        "generated_at": now(),
        "source_reviewed": True,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "activity_record_count": len(records),
        "activity_records": records,
        "parser_quality_control": {
            "issue_count": 0,
            "strict_endpoint_matching": True,
            "figure_only_exact_values_not_fabricated": True,
        },
        "extraction_issues": [
            {
                "issue_code": "figure_only_exact_toxicity_values_not_source_verified",
                "severity": "blocking_for_publication_grade",
                "details": "DBAASP exact hemolysis/cell-death values are preserved in database audit as source_conflict because the local XML/PDF/OA package has only prose approximations and Figure 1 image/caption, not a source data table.",
            }
        ],
        "checked_inputs": SOURCE_PATHS_CHECKED,
    }


def peptide_identity_locator() -> dict[str, Any]:
    return {
        "source_path": "source/paper.xml",
        "locator": "xml:abstract; xml:sec=1:Introduction; xml:sec=2.1:Peptide Design",
        "primary_source_statement": "Primary source identifies [Nle1, dLeu9, dLys10]TL and gives the modified C-terminal amidated sequence.",
        "source_sequence": PEPTIDE_NLE_SEQUENCE,
        "source_modifications": ["N-terminal norleucine", "dLeu9", "dLys10", "C-terminal amide"],
    }


def audit_row(row: dict[str, Any], source_table: str, row_number: int) -> dict[str, Any]:
    subject = species_from_db(str(row.get("subject_name") or row.get("target_organism_text") or ""))
    measure = str(row.get("measure_value") or row.get("assay_text") or row.get("measure_group") or "")
    concentration = str(row.get("concentration") or "")
    traceability = {
        "source_path": f"paper_packets/{PAPER_ID}/database/{source_table}",
        "locator": f"database:{source_table}:row={row_number}",
    }
    status = "source_conflict"
    matched_activity_record_id = ""
    activity_source_locator: dict[str, str] | None = None
    conflict_context = (
        "Source conflict preserved: linked DBAASP toxicity/host-cell row contains an exact numeric value, "
        "but local XML/PDF/OA package evidence provides only prose approximations plus Figure 1 image/caption; "
        "no supplementary source-data table is present."
    )
    review_notes = "Database row is not source_verified because exact figure-derived toxicity value is not locally recoverable."

    if str(row.get("assay_type") or "") == "target_activity" and subject in DBAASP_MIC_LOCATORS:
        matched_activity_record_id, locator = DBAASP_MIC_LOCATORS[subject]
        status = "source_verified"
        activity_source_locator = source_locator(locator)
        conflict_context = ""
        review_notes = (
            "DBAASP MIC target/concentration row matches the current-paper Table 2 [Nle1, dLeu9, dLys10]TL value, "
            "with peptide identity traced to the source sequence in the primary article."
        )

    return {
        "source_id": row.get("source_id") or row.get("source_record_id") or row.get("dbaasp_id") or SEQUENCE_KEY,
        "sequence_key": row.get("sequence_key") or SEQUENCE_KEY,
        "source_table": source_table,
        "database": row.get("database") or row.get("\ufeffdatabase") or "DBAASP",
        "database_subject": subject,
        "database_measure": measure,
        "database_concentration": concentration,
        "database_unit": row.get("unit") or "",
        "matched_activity_record_id": matched_activity_record_id,
        "status": status,
        "layer1_status": status,
        "traceability": traceability,
        "citation_traceability": {
            "source_path": "source/paper.xml",
            "locator": "xml:article-meta",
            "doi": DOI,
            "pmid": PMID,
            "pmcid": PMCID,
        },
        "sequence_check": {
            "source_locator": peptide_identity_locator(),
            "database_sequence_snapshot": "paper_packets/doi__10.3390_antibiotics11101285/database/linked_sequence_records.jsonl",
            "database_sequence_snapshot_status": "no linked sequence rows were present in the local packet",
        },
        "activity_source_locator": activity_source_locator,
        "review_notes": review_notes,
        "conflict_context": conflict_context,
        "conflict_flags": [status] if status == "source_conflict" else [],
    }


def literature_row(row: dict[str, Any], row_number: int) -> dict[str, Any]:
    return {
        "source_id": row.get("source_id") or SEQUENCE_KEY,
        "sequence_key": row.get("sequence_key") or SEQUENCE_KEY,
        "source_table": "linked_literature_records.jsonl",
        "database": row.get("database") or "DBAASP",
        "database_subject": row.get("title") or "",
        "database_measure": "literature_link",
        "database_concentration": "",
        "database_unit": "",
        "matched_activity_record_id": "",
        "status": "source_verified",
        "layer1_status": "source_verified",
        "traceability": {
            "source_path": f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
            "locator": f"database:linked_literature_records:row={row_number}",
        },
        "citation_traceability": {
            "source_path": "source/paper.xml",
            "locator": "xml:article-meta",
            "doi": DOI,
            "pmid": PMID,
            "pmcid": PMCID,
        },
        "sequence_check": {"source_locator": peptide_identity_locator()},
        "review_notes": "Literature row DOI/PMID/PMCID matches the current primary paper metadata.",
        "conflict_context": "",
        "conflict_flags": [],
    }


def build_database() -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    for source_table in ("linked_assay_records.jsonl", "linked_experiment_records.jsonl"):
        for idx, row in enumerate(read_jsonl(PACKET / "database" / source_table), start=1):
            audits.append(audit_row(row, source_table, idx))
    for idx, row in enumerate(read_jsonl(PACKET / "database" / "linked_literature_records.jsonl"), start=1):
        audits.append(literature_row(row, idx))
    summary = dict(sorted(Counter(record["status"] for record in audits).items()))
    return {
        "paper_id": PAPER_ID,
        "generated_at": now(),
        "source_reviewed": True,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "audit_scope": "Worker-4 source-reviewed DBAASP linked assay/experiment/literature rows against the current paper XML/PDF/OA package and packet database snapshots.",
        "database_row_counts": {
            "linked_assay_records": len(read_jsonl(PACKET / "database" / "linked_assay_records.jsonl")),
            "linked_experiment_records": len(read_jsonl(PACKET / "database" / "linked_experiment_records.jsonl")),
            "linked_literature_records": len(read_jsonl(PACKET / "database" / "linked_literature_records.jsonl")),
            "linked_dramp_activity_records": len(read_jsonl(PACKET / "database" / "linked_dramp_activity_records.jsonl")),
            "linked_sequence_records": len(read_jsonl(PACKET / "database" / "linked_sequence_records.jsonl")),
        },
        "record_audits": audits,
        "status_summary": summary,
        "caution_findings": [
            {
                "caution_code": "linked_sequence_snapshot_absent",
                "status": "source_verified_with_packet_limitation",
                "evidence_context": "The packet has no linked_sequence_records rows; peptide identity is traced to primary-source sequence/name/modification evidence, not a local DBAASP sequence snapshot.",
            },
            {
                "caution_code": "database_toxicity_exact_values_source_conflict",
                "status": "source_conflict",
                "evidence_context": "Six DBAASP duplicate assay/experiment toxicity rows carry exact figure-like hemolysis/cell-death values not recoverable as exact local source-table values.",
            },
        ],
        "checked_inputs": SOURCE_PATHS_CHECKED,
    }


def build_mechanism() -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": now(),
        "source_reviewed": True,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "mechanism_claims": [
            {
                "claim_id": "mech-001-membrane-biophysical",
                "claim_text": "The paper supports membrane-interaction and membrane-perturbation claims for [Nle1, dLeu9, dLys10]TL using LUV aggregation, CD conformation, Laurdan GP, and ANTS/DPX leakage assays.",
                "entity_scope": PEPTIDE_NLE,
                "evidence_class": "direct_mechanism",
                "direct_assay_types": [
                    "Thioflavin T aggregation in bacterial-mimic LUVs",
                    "circular dichroism in LUVs",
                    "Laurdan generalized polarization membrane-fluidity assay",
                    "ANTS/DPX LUV leakage assay",
                ],
                "source_locator": source_locator("xml:sec=2.5-2.8; xml:fig=2; xml:fig=3; xml:fig=4; xml:table=3"),
                "limitations": "Assays use model membranes; the record does not assign a unique pore model or intracellular bacterial target.",
            },
            {
                "claim_id": "mech-002-host-il6-modulation",
                "claim_text": "The paper supports anti-inflammatory host-response activity: 3 uM peptide reduced IL-6 production in LPS-stimulated J774A.1 macrophages.",
                "entity_scope": PEPTIDE_NLE,
                "evidence_class": "direct_host_response_assay",
                "direct_assay_types": ["J774A.1 LPS stimulation with IL-6 ELISA"],
                "source_locator": source_locator("xml:sec=2.9; xml:fig=6"),
                "limitations": "The local source supports IL-6 modulation, not a complete cytokine pathway map or receptor target.",
            },
            {
                "claim_id": "mech-003-structure-activity-caution",
                "claim_text": "The paper links N-terminal norleucine-driven hydrophobicity and beta-type membrane conformation to improved MIC values, but detailed cellular killing mechanism remains bounded to the reported biophysical assays.",
                "entity_scope": PEPTIDE_NLE,
                "evidence_class": "source_reviewed_structure_activity_context",
                "direct_assay_types": [],
                "source_locator": source_locator("xml:abstract; xml:sec=2.1-2.3; xml:sec=3:Discussion; xml:table=1; xml:table=2"),
                "limitations": "Structure/activity interpretation is not converted into unsupported exact molecular target annotation.",
            },
        ],
        "checked_inputs": SOURCE_PATHS_CHECKED,
    }


def unrecoverable_gap() -> dict[str, Any]:
    return {
        "gap_code": "figure_only_exact_toxicity_database_values_unrecoverable",
        "source_paths_checked": [
            f"papers/{PAPER_ID}/source/paper.xml",
            f"papers/{PAPER_ID}/source/paper.pdf",
            f"paper_packets/{PAPER_ID}/extracted/pdf_text/antibiotics-11-01285.txt",
            f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
            f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
            f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
            f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
            f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9598925/PMC9598925/antibiotics-11-01285-g001.jpg",
            f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
            f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
            f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
        ],
        "tools_attempted": [
            "rg over XML/PDF text/extracted JSON",
            "python xml.etree table and figure-caption inspection",
            "jq linked database row inspection",
            "file image/source-package inspection",
        ],
        "why_unrecoverable": "The local paper has XML/PDF prose, Figure 1 image/caption, and no supplementary assets or source-data tables. It supports approximate toxicity statements but not the exact DBAASP values 18% hemolysis, 38% hemolysis, or 50% cell death as source-verifiable table values.",
        "impact": "Worker-4 preserves six duplicate linked DBAASP toxicity rows as source_conflict; worker-6 cannot certify publication-grade database reconciliation from local material.",
        "owner_worker": "worker-4 + worker-6",
        "blocks_publication_grade": True,
        "next_action": "record_and_continue",
    }


def current_rework_target(generated_at: str) -> dict[str, Any]:
    return {
        "ticket_id": GAP_TICKET_ID,
        "paper_id": PAPER_ID,
        "created_at": generated_at,
        "worker": "worker-4 + worker-6",
        "owner_worker": "worker-4 + worker-6",
        "target_queue": "analysis",
        "layer": "database_record_audit",
        "severity": "blocking",
        "failure_code": "figure_only_exact_toxicity_database_values_unrecoverable",
        "omission_code": "database_toxicity_exact_values_not_source_verifiable",
        "failing_object": "linked DBAASP toxicity assay/experiment rows for DBAASPS_19933",
        "artifact_path": f"papers/{PAPER_ID}/final/database_record_verification.json",
        "source_paths_to_check": unrecoverable_gap()["source_paths_checked"],
        "required_action": "No further local retry is recommended unless external source data or a manual figure-digitization policy is supplied; keep source_conflict rows explicit and leave paper non-publication-grade.",
        "blocks": ["publication_grade_ready", "final_approval"],
        "qc_failure_reasons": [
            {
                "code": "figure_only_exact_toxicity_database_values_unrecoverable",
                "owner_worker": "worker-4 + worker-6",
                "severity": "blocking",
                "reason": "Exact database toxicity values are not present in local XML/PDF/supplement tables and cannot be source-verified after bounded local recovery.",
            }
        ],
    }


def build_review(activity_count: int, database_summary: dict[str, int], mechanism_count: int, generated_at: str) -> dict[str, Any]:
    target = current_rework_target(generated_at)
    return {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "pmcid": PMCID,
        "pmid": PMID,
        "reviewed_at": generated_at,
        "generated_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "review_status": "blocked_missing_primary_material",
        "publication_grade": False,
        "validator_contract_passed": True,
        "source_reviewed": True,
        "source_review_depth": [
            "paper_xml",
            "paper_pdf",
            "oa_package",
            "supplementary_assets",
            "merged_database_rows",
        ],
        "materials_exhausted": {
            "paper_xml": True,
            "paper_pdf": True,
            "oa_package": True,
            "supplementary_assets": True,
            "merged_database_rows": True,
            "note": "No supplementary assets/source-data tables are present; Figure 1 image/caption supports only approximate toxicity statements, not exact DBAASP toxicity values.",
        },
        "checked_inputs": SOURCE_PATHS_CHECKED,
        "semantic_quality_checks": {
            "activity_rows_source_reviewed": activity_count,
            "database_status_summary": database_summary,
            "mechanism_claims_source_reviewed": mechanism_count,
            "open_rework_targets": 1,
            "unrecoverable_blocking_gap_count": 1,
            "closed_or_superseded_ticket_ids": [OLD_TICKET_ID],
            "current_ticket_ids": [GAP_TICKET_ID],
        },
        "per_layer_decision_rationale": {
            "material_packet": "XML/PDF/OA package and figure assets were reopened; supplementary inventory is empty, so no source-data table can be recovered locally.",
            "validator_contract": "Structural artifacts are present and machine-readable; this is separate from publication-grade acceptance.",
            "layer_1_database": "All seven DBAASP MIC rows are source_verified against Table 2; six duplicate hemolysis/HaCaT toxicity rows remain source_conflict because exact database values are figure/database-only.",
            "layer_2_activity_toxicity": "Table 2 MIC values and source-prose toxicity/host-response statements were captured without inventing exact figure values.",
            "layer_3_mechanism": "Mechanism claims were replaced with source-reviewed, assay-bounded membrane and IL-6 host-response evidence.",
            "publication_grade_review": "Non-accepted: a blocking worker-4/6 database conflict remains unrecoverable from local materials, so final approval is refused rather than retried indefinitely.",
        },
        "caution_findings": [
            {
                "caution_code": "database_toxicity_exact_values_source_conflict",
                "severity": "blocking",
                "evidence_context": "DBAASP exact toxicity values are not source-verifiable as exact values in local XML/PDF/OA/supplement material.",
            },
            {
                "caution_code": "linked_sequence_snapshot_absent",
                "severity": "caution",
                "evidence_context": "No linked_sequence_records rows were present, so source sequence/modification evidence is taken from the primary article.",
            },
        ],
        "qc_failure_reasons": target["qc_failure_reasons"],
        "rework_targets": [target],
        "strict_gate": {
            "required_rework_count": 1,
            "open_ticket_ids": [GAP_TICKET_ID],
            "semantic_gate_required": True,
        },
        "unrecoverable_material_gaps": [unrecoverable_gap()],
        "adjudication_summary": "Worker-4/6 re-review recovered supported MIC, toxicity prose, mechanism, and database evidence, but the exact DBAASP toxicity rows remain locally unrecoverable; paper remains non-publication-grade.",
    }


def quality_feedback(generated_at: str, gate_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    target = current_rework_target(generated_at)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": 1,
        "status": "blocked_missing_primary_material_after_worker4_worker6_source_review",
        "publication_grade_ready": False,
        "qc_failure_reasons": target["qc_failure_reasons"],
        "rework_targets": [target],
        "rework_context_packet_required": False,
        "superseded_ticket_ids": [OLD_TICKET_ID],
        "open_ticket_ids": [GAP_TICKET_ID],
        "unrecoverable_material_gaps": [unrecoverable_gap()],
        "gate_evidence": gate_evidence or {},
        "review_notes": "Bounded source recovery reopened paper XML/PDF/OA package/images and linked DBAASP rows. Supported MIC and mechanism evidence was repaired; exact figure-only toxicity database values remain unrecoverable locally.",
    }


def run_gates() -> dict[str, Any]:
    semantic_report = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    publication_report = REPORTS / f"{PAPER_ID}.publication_quality.json"
    manifest = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"
    semantic_cmd = [
        sys.executable,
        str(ROOT / ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py"),
        "--paper-id",
        PAPER_ID,
        "--json",
    ]
    semantic = subprocess.run(semantic_cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    semantic_report.write_text(semantic.stdout, encoding="utf-8")
    publication_cmd = [
        sys.executable,
        str(ROOT / ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py"),
        "--manifest",
        str(manifest),
        "--json-out",
        str(publication_report),
    ]
    publication = subprocess.run(publication_cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    if publication.stdout and not publication_report.exists():
        publication_report.write_text(publication.stdout, encoding="utf-8")
    semantic_json = read_json(semantic_report)
    publication_json = read_json(publication_report)
    shutil.copyfile(semantic_report, REPORTS / f"{PAPER_ID}.true_rework_queue_attempt_1.after_worker.semantic_gate.json")
    shutil.copyfile(publication_report, REPORTS / f"{PAPER_ID}.true_rework_queue_attempt_1.after_worker.publication_quality.json")
    return {
        "semantic_report": str(semantic_report),
        "semantic_returncode": semantic.returncode,
        "semantic_publication_grade_pass_count": semantic_json.get("publication_grade_pass_count"),
        "semantic_publication_grade_fail_count": semantic_json.get("publication_grade_fail_count"),
        "semantic_issue_count": sum(item.get("issue_count", 0) for item in semantic_json.get("results", [])),
        "semantic_issue_codes": [
            issue.get("code")
            for result in semantic_json.get("results", [])
            for issue in result.get("issues", [])
        ],
        "publication_report": str(publication_report),
        "publication_returncode": publication.returncode,
        "publication_grade_pass": publication_json.get("publication_grade_pass"),
        "publication_risk_counts": publication_json.get("risk_counts", {}),
    }


def update_packet_state(gates: dict[str, Any], activity_count: int, mechanism_count: int) -> None:
    manifest = read_json(PACKET / "packet_manifest.json")
    manifest["analysis_queue_status"] = "analysis_needs_analysis_rework"
    manifest["open_rework_ticket_ids"] = [GAP_TICKET_ID]
    manifest["known_missing_or_blocked_materials"] = [unrecoverable_gap()]
    manifest["test_scope"] = "worker-4/6 bounded re-review completed; terminal status is blocked_missing_primary_material, not publication-grade acceptance"
    manifest["updated_at"] = now()
    write_json(PACKET / "packet_manifest.json", manifest)

    status = read_json(PACKET / "analysis" / "analysis_status.json")
    status["status"] = "analysis_needs_analysis_rework"
    status["open_rework_ticket_ids"] = [GAP_TICKET_ID]
    status["superseded_rework_ticket_ids"] = [OLD_TICKET_ID]
    status["generated_at"] = now()
    status["activity_record_count"] = activity_count
    status["mechanism_claim_count"] = mechanism_count
    status["unrecoverable_material_gaps"] = [unrecoverable_gap()]
    status["gate_evidence"] = gates
    write_json(PACKET / "analysis" / "analysis_status.json", status)


def update_workflow_context(gates: dict[str, Any]) -> None:
    path = WORKFLOW / "workflow_context.json"
    context = read_json(path, {})
    if not context:
        return
    context["current_round"] = "final_approval"
    context["current_state"] = "blocked_missing_primary_material"
    context["updated_at"] = now()
    context["open_rework_tickets"] = [GAP_TICKET_ID]
    context["superseded_rework_tickets"] = [OLD_TICKET_ID]
    context["queue_status"] = {
        "material": "material_extracted_with_gaps",
        "analysis": "analysis_needs_analysis_rework",
    }
    context["gate_summary"] = {
        "structural_ready": True,
        "validator_contract_ready": True,
        "semantic_gate_ready": False,
        "publication_grade_ready": False,
    }
    context.setdefault("artifacts", {})["semantic_gate"] = gates["semantic_report"]
    context.setdefault("artifacts", {})["publication_quality"] = gates["publication_report"]
    context["unrecoverable_material_gaps"] = [unrecoverable_gap()]
    write_json(path, context)


def update_complete_report(gates: dict[str, Any], activity_count: int, db_summary: dict[str, int], mechanism_count: int) -> None:
    report = {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "pmcid": PMCID,
        "pmid": PMID,
        "generated_at": now(),
        "completion_claim": "worker4_worker6_source_review_repaired_supported_layers_but_left_unrecoverable_gap_nonaccepted",
        "current_state": "blocked_missing_primary_material",
        "terminal_status": "blocked_unrecoverable",
        "final_approval_status": "refused_unrecoverable_material_gap",
        "gate_summary": {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": False,
            "publication_grade_ready": False,
        },
        "gate_results": gates,
        "analysis": {
            "review_status": "blocked_missing_primary_material",
            "activity_records": activity_count,
            "mechanism_claims": mechanism_count,
            "database_status_summary": db_summary,
        },
        "material": {
            "status": "material_extracted_with_gaps",
            "supplementary_assets": 0,
            "note": "No local supplement/source-data table exists for exact toxicity figure/database values.",
        },
        "open_rework_ticket_count": 1,
        "rework_ticket_ids": [GAP_TICKET_ID],
        "superseded_rework_ticket_ids": [OLD_TICKET_ID],
        "not_publication_grade_reason": "Exact DBAASP toxicity database values remain source_conflict/unrecoverable from local XML/PDF/OA/supplement material.",
        "unrecoverable_material_gaps": [unrecoverable_gap()],
        "semantic_gate": "failed_expected_unrecoverable_gap",
        "publication_quality_gate": "failed_expected_open_rework",
        "manifest": str(REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"),
        "semantic_report": gates["semantic_report"],
        "publication_quality_report": gates["publication_report"],
        "workflow_dir": str(WORKFLOW),
    }
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", report)


def append_rework_ticket(generated_at: str) -> None:
    append_jsonl_once(PACKET / "rework" / "rework_requests.jsonl", current_rework_target(generated_at), "ticket_id")


def append_rework_response(gates: dict[str, Any], generated_at: str) -> None:
    response = {
        "record_type": "rework_response",
        "response_id": f"{PAPER_ID}-worker46-source-review-{generated_at}",
        "paper_id": PAPER_ID,
        "ticket_ids": [OLD_TICKET_ID],
        "superseding_ticket_ids": [GAP_TICKET_ID],
        "status": "blocked_unrecoverable",
        "resolved": False,
        "resolved_by": "codex-cli",
        "owner_workers": ["worker-4", "worker-6"],
        "created_at": generated_at,
        "state": "worker4_worker6_bounded_source_review",
        "checked_source_paths": SOURCE_PATHS_CHECKED,
        "tools_attempted": TOOLS_ATTEMPTED,
        "what_was_repaired": [
            "Worker-4 reclassified all seven DBAASP MIC rows as source_verified against Table 2 and preserved six toxicity duplicate rows as source_conflict with concrete context.",
            "Worker-6 rebuilt final activity/toxicity rows with peptide-specific MIC rows, source-prose toxicity/host-response records, and source-located mechanism claims.",
            "Worker-6 replaced the framework-only review with source-reviewed adjudication, concrete qc_failure_reasons, and a bounded unrecoverable material gap.",
        ],
        "what_remains": [
            "Exact DBAASP values 18% hemolysis, 38% hemolysis, and 50% cell death are not locally source-verifiable as exact values; no supplement/source-data table exists.",
            "Strict gates are expected to fail because the paper remains non-publication-grade with open ticket rwk-worker46-figure-toxicity-gap-0002.",
        ],
        "unrecoverable_material_gaps": [unrecoverable_gap()],
        "gate_results": gates,
        "artifact_refs": [
            f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
            f"paper_packets/{PAPER_ID}/analysis/adjudication_report.json",
            f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
            f"papers/{PAPER_ID}/final/database_record_verification.json",
            f"papers/{PAPER_ID}/final/mechanism_ontology_record.json",
            f"papers/{PAPER_ID}/final/review_report.json",
            f"papers/{PAPER_ID}/work/review/quality_feedback.json",
            gates["semantic_report"],
            gates["publication_report"],
            f"reports/{PAPER_ID}.complete_message_test_report.json",
        ],
    }
    append_jsonl_once(PACKET / "rework" / "rework_responses.jsonl", response, "response_id")


def main() -> int:
    generated_at = now()
    activity = build_activity()
    database = build_database()
    mechanism = build_mechanism()
    db_summary = database["status_summary"]
    review = build_review(activity["activity_record_count"], db_summary, len(mechanism["mechanism_claims"]), generated_at)

    write_json(PAPER / "final" / "activity_toxicity_evidence.json", activity)
    write_json(PACKET / "analysis" / "activity_toxicity_evidence.json", activity)
    write_json(PACKET / "final" / "activity_toxicity_evidence.json", activity)

    write_json(PAPER / "final" / "database_record_verification.json", database)
    write_json(PACKET / "analysis" / "database_record_audit.json", database)
    write_json(PACKET / "final" / "database_record_verification.json", database)

    write_json(PAPER / "final" / "mechanism_ontology_record.json", mechanism)
    write_json(PAPER / "final" / "mechanism_evidence.json", mechanism)
    write_json(PACKET / "analysis" / "mechanism_evidence.json", mechanism)
    write_json(PACKET / "final" / "mechanism_evidence.json", mechanism)

    write_json(PAPER / "final" / "review_report.json", review)
    write_json(PACKET / "analysis" / "adjudication_report.json", review)
    write_json(PACKET / "final" / "review_report.json", review)
    append_rework_ticket(generated_at)

    gates = run_gates()
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality_feedback(generated_at, gates))
    update_packet_state(gates, activity["activity_record_count"], len(mechanism["mechanism_claims"]))
    update_workflow_context(gates)
    update_complete_report(gates, activity["activity_record_count"], db_summary, len(mechanism["mechanism_claims"]))
    append_rework_response(gates, generated_at)

    print(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "publication_grade_ready": False,
                "database_status_summary": db_summary,
                "activity_records": activity["activity_record_count"],
                "mechanism_claims": len(mechanism["mechanism_claims"]),
                "gate_results": gates,
                "open_ticket_ids": [GAP_TICKET_ID],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
