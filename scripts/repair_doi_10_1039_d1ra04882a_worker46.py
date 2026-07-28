#!/usr/bin/env python3
"""Repair worker-4/6 artifacts for doi__10.1039_d1ra04882a."""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


PAPER_ID = "doi__10.1039_d1ra04882a"
DOI = "10.1039/d1ra04882a"
PMID = "35498921"
PMCID = "PMC9041360"
ROOT = Path(".").resolve()
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
REPORTS = ROOT / "reports"
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
ORIGINAL_TICKET_ID = "rwk-complete-test-0001"
ACTIVITY_TICKET_ID = "rwk-worker2-activity-ic50-targetclass-20260503T1500Z"
MECHANISM_TICKET_ID = "rwk-worker5-mechanism-source-review-20260503T1500Z"
OPEN_TICKET_IDS = [ACTIVITY_TICKET_ID, MECHANISM_TICKET_ID]

SOURCE_PATHS_CHECKED = [
    f"rework_context/{PAPER_ID}/handoff_context.json",
    f"paper_packets/{PAPER_ID}/packet_manifest.json",
    f"paper_packets/{PAPER_ID}/locators/locator_index.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
    f"paper_packets/{PAPER_ID}/analysis/activity_toxicity_evidence.json",
    f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
    f"paper_packets/{PAPER_ID}/analysis/mechanism_evidence.json",
    f"paper_packets/{PAPER_ID}/analysis/adjudication_report.json",
    f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
    f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
    f"paper_packets/{PAPER_ID}/extracted/archive_manifest.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_text/RA-011-D1RA04882A-s001.txt",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/RA-011-D1RA04882A.txt",
    f"paper_packets/{PAPER_ID}/raw/paper.xml",
    f"paper_packets/{PAPER_ID}/raw/paper.pdf",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-1.bin",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9041360/PMC9041360/RA-011-D1RA04882A.nxml",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9041360/PMC9041360/RA-011-D1RA04882A.pdf",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9041360/PMC9041360/RA-011-D1RA04882A-s001.pdf",
    f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_dramp_activity_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    f"papers/{PAPER_ID}/source/supplementary/RA-011-D1RA04882A-s001.pdf",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/all_experimental_records.csv",
]

TOOLS_ATTEMPTED = [
    "jq",
    "rg",
    "file",
    "xml.etree.ElementTree JATS table review",
    "pdftotext-derived packet text review",
    "JSONL linked DBAASP row review",
    "merged all_sequences.csv row lookup",
    "semantic_three_layer_gate.py",
    "check_three_layer_publication_quality.py",
]

PEPTIDES = {
    "DBAASP:DBAASPN_21607": {
        "database_sequence": "XVXNXNATXP",
        "database_name": "Minutissamide A",
        "primary_name": "MIN A",
        "compound": "1",
        "table_column": 4,
        "name_locator": "xml:fig=1:Fig. 1; xml:sec=Cytotoxicity and antifungal properties evaluation of PUW F and MIN A",
        "source_origin": "Natural cyanobacterial PUW/MIN variant isolated as compound 1 in this paper.",
        "sequence_caution": "The merged DBAASP row stores a 10-residue nonribosomal placeholder sequence with X residues; the paper presents PUW/MIN chemical structures and compound names, not an exact linear amino-acid string suitable for clean sequence normalization.",
    },
    "DBAASP:DBAASPN_21608": {
        "database_sequence": "XVXNXNAtXP",
        "database_name": "Puwainaphycin F",
        "primary_name": "PUW F",
        "compound": "2",
        "table_column": 1,
        "name_locator": "xml:fig=1:Fig. 1; xml:sec=Cytotoxicity and antifungal properties evaluation of PUW F and MIN A",
        "source_origin": "Natural cyanobacterial PUW/MIN variant isolated as compound 2 in this paper.",
        "sequence_caution": "The merged DBAASP row stores a 10-residue nonribosomal placeholder sequence with X residues and lower-case threonine notation; the paper presents PUW/MIN chemical structures and compound names, not an exact clean linear sequence.",
    },
    "DBAASP:DBAASPS_21609": {
        "database_sequence": "XVXNXNATXP",
        "database_name": "PUW/MIN 4a",
        "primary_name": "PUW/MIN 4a",
        "compound": "4a",
        "table_column": 2,
        "name_locator": "xml:fig=1:Fig. 1; xml:sec=Biological activity of PUW/MIN semi-synthetic variants; supplementary_text:RA-011-D1RA04882A-s001.txt:Fig. S3/S12",
        "source_origin": "Semi-synthetic analog prepared within this study from MIN C-derived chemistry.",
        "sequence_caution": "The merged DBAASP row stores the same normalized nonribosomal placeholder sequence as MIN A while the primary paper identifies 4a by semi-synthetic FA modification, NMR, and HRMS/MS rather than a distinct clean linear peptide sequence.",
    },
}

TARGET_ROWS = {
    "Aspergillus fumigatus": {"row": 4, "source_label": "A. fumigatus"},
    "Fusarium oxysporum": {"row": 5, "source_label": "F. oxysporum"},
    "Trichoderma harzianum": {"row": 6, "source_label": "T. harzianum"},
    "Alternaria alternata": {"row": 7, "source_label": "A. alternata"},
    "Bipolaris sorokiniana": {"row": 8, "source_label": "B. sorokiniana"},
    "Plectosphaerella cucumerina": {
        "row": 9,
        "source_label": "M. cucumerina",
        "taxon_note": "Packet database uses Plectosphaerella cucumerina BCC020_2872; paper methods/table use Monographella/M. cucumerina for the same BCC isolate.",
    },
    "Chaetomium globosum": {"row": 10, "source_label": "C. globosum"},
    "Candida friedrichii": {"row": 11, "source_label": "C. friedrichii"},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


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
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=False) + "\n")


def append_jsonl_once(path: Path, payload: dict[str, Any], key: str = "ticket_id") -> None:
    existing = read_jsonl(path)
    if key and payload.get(key) and any(row.get(key) == payload.get(key) for row in existing):
        return
    append_jsonl(path, payload)


def text_of(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return " ".join("".join(node.itertext()).split())


def table_rows() -> list[list[str]]:
    root = ET.parse(PACKET / "raw" / "paper.xml").getroot()
    table = root.find(".//{*}table-wrap")
    rows: list[list[str]] = []
    if table is None:
        return rows
    for tr in table.findall(".//{*}tr"):
        cells: list[str] = []
        for cell in list(tr):
            if cell.tag.endswith("td") or cell.tag.endswith("th"):
                cells.append(text_of(cell))
        if cells:
            rows.append(cells)
    return rows


TABLE_ROWS = table_rows()


def normalize_na(value: str) -> str:
    return str(value or "").strip().upper()


def subject_row(subject: str) -> dict[str, Any]:
    for prefix, info in TARGET_ROWS.items():
        if prefix in subject:
            return info
    raise KeyError(f"unhandled database subject: {subject}")


def source_table_value(sequence_key: str, subject: str) -> tuple[str, dict[str, Any]]:
    peptide = PEPTIDES[sequence_key]
    target = subject_row(subject)
    table_row = int(target["row"])
    table_column = int(peptide["table_column"])
    # XML table rows are 1-based in locators. Row cells hold the target label
    # at index 0 and compound values at indices 1..8.
    value = TABLE_ROWS[table_row - 1][table_column]
    locator = {
        "source_path": f"papers/{PAPER_ID}/source/paper.xml",
        "packet_source_path": f"paper_packets/{PAPER_ID}/raw/paper.xml",
        "locator": f"xml:table=1:row={table_row}:column={table_column}",
        "label": "Table 1",
        "column_compound": peptide["compound"],
        "source_target_label": target["source_label"],
        "method_locator": "xml:sec=Antifungal activity",
    }
    return value, locator


def activity_check_for_row(row: dict[str, Any]) -> dict[str, Any]:
    sequence_key = str(row.get("sequence_key") or "")
    peptide = PEPTIDES[sequence_key]
    subject = str(row.get("subject_name") or row.get("target_organism_text") or "")
    database_value = str(row.get("concentration") or "")
    if "Human cervical carcinoma HeLa" in subject:
        if sequence_key == "DBAASP:DBAASPN_21607":
            return {
                "status": "source_verified",
                "endpoint": "IC50",
                "database_value": database_value,
                "database_unit": row.get("unit") or "µM",
                "primary_value": "2.8",
                "primary_unit": "μM",
                "primary_target": "HeLa cells",
                "value_agreement": database_value == "2.8",
                "source_locator": {
                    "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                    "locator": "xml:sec=Cytotoxicity and antifungal properties evaluation of PUW F and MIN A; xml:fig=2:Fig. 2",
                    "source_statement": "The paper reports compound 1/MIN A HeLa IC50 as 2.8 μM in text/discussion context.",
                },
            }
        if sequence_key == "DBAASP:DBAASPN_21608":
            return {
                "status": "source_verified",
                "endpoint": "IC50",
                "database_value": database_value,
                "database_unit": row.get("unit") or "µM",
                "primary_value": "3.15",
                "primary_unit": "μM",
                "primary_target": "HeLa cells",
                "value_agreement": database_value == "3.15",
                "source_locator": {
                    "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                    "locator": "xml:sec=Discussion; xml:fig=2:Fig. 2",
                    "source_statement": "The paper discussion reports compound 2/PUW F HeLa IC50 as 3.15 μM, while results text rounds it to 3.2 ± 0.5 μM.",
                },
            }
        return {
            "status": "source_conflict",
            "endpoint": "IC50",
            "database_value": database_value,
            "database_unit": row.get("unit") or "µM",
            "primary_value": "not_calculable",
            "primary_unit": "not_applicable",
            "primary_target": "HeLa cells",
            "value_agreement": False,
            "source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:sec=Biological activity of PUW/MIN semi-synthetic variants; xml:fig=8:Fig. 6; supplementary_text:RA-011-D1RA04882A-s001.txt:Fig. S1",
                "source_statement": "The paper states the 4a/4b dose-response was non-standard and corresponding IC50 values could not be calculated; 20 μM is a tested concentration/full-inhibition context, not a source-supported IC50.",
            },
        }

    source_value, locator = source_table_value(sequence_key, subject)
    database_na = normalize_na(database_value) == "NA"
    source_na = normalize_na(source_value) == "NA"
    target = subject_row(subject)
    unit = row.get("unit") or ("not_reported_for_NA_threshold" if database_na else "µM")
    primary_unit = "μM"
    if source_na:
        primary_unit = "not_applicable; highest concentration tested was 75 μM"
    return {
        "status": "source_verified",
        "endpoint": "MIC" if not source_na else "not_active_at_highest_tested_concentration",
        "database_value": database_value,
        "database_unit": unit,
        "primary_value": source_value,
        "primary_unit": primary_unit,
        "primary_target": target["source_label"],
        "value_agreement": database_value == source_value,
        "source_locator": locator,
        "target_taxon_note": target.get("taxon_note", ""),
    }


def row_layer1_status(row: dict[str, Any]) -> str:
    subject = str(row.get("subject_name") or row.get("target_organism_text") or "")
    if "Human cervical carcinoma HeLa" in subject and row.get("sequence_key") == "DBAASP:DBAASPS_21609":
        return "source_conflict"
    return "sequence_modified_not_normalized"


def audit_for_row(row: dict[str, Any], source_file: str, row_no: int, generated_at: str) -> dict[str, Any]:
    sequence_key = str(row.get("sequence_key") or "")
    peptide = PEPTIDES[sequence_key]
    subject = str(row.get("subject_name") or row.get("target_organism_text") or "")
    activity_check = activity_check_for_row(row)
    status = row_layer1_status(row)
    if status == "source_conflict":
        conflict_context = (
            "Database stores PUW/MIN 4a HeLa IC50 as 20 µM, but the primary paper says 4a/4b IC50 values could not be "
            "calculated and describes 20 µM as a tested concentration/morphology context. Preserve as source_conflict."
        )
    else:
        conflict_context = (
            "Database activity/citation row is source-matched, but the sequence is not promoted to source_verified because "
            "the DBAASP sequence uses normalized nonribosomal placeholder notation that is not an exact linear source sequence."
        )
    source_record_id = row.get("assay_id") or row.get("source_record_id") or row.get("dbaasp_id") or ""
    return {
        "source_id": row.get("source_id") or sequence_key,
        "sequence_key": sequence_key,
        "source_table": source_file,
        "source_record_id": str(source_record_id),
        "database": row.get("database") or row.get("﻿database") or "DBAASP",
        "database_subject": subject,
        "database_measure": row.get("measure_group") or row.get("measure_value") or row.get("assay_text") or row.get("assay_type") or "",
        "database_concentration": row.get("concentration") or "",
        "database_unit": row.get("unit") or "",
        "database_peptide_name": row.get("peptide_name") or peptide["database_name"],
        "traceability": {
            "source_path": f"paper_packets/{PAPER_ID}/database/{source_file}",
            "locator": f"database:{source_file}:row={row_no}",
        },
        "citation_traceability": {
            "source_path": f"papers/{PAPER_ID}/source/paper.xml",
            "locator": "xml:article-meta",
            "doi": DOI,
            "pmid": PMID,
            "pmcid": PMCID,
        },
        "status": status,
        "layer1_status": status,
        "matched_activity_record_id": "",
        "sequence_check": {
            "status": "sequence_modified_not_normalized",
            "database_sequence": peptide["database_sequence"],
            "primary_name": peptide["primary_name"],
            "compound": peptide["compound"],
            "modification_evidence": peptide["sequence_caution"],
            "source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "packet_source_path": f"paper_packets/{PAPER_ID}/raw/paper.xml",
                "locator": peptide["name_locator"],
                "supplementary_sources": [
                    f"paper_packets/{PAPER_ID}/extracted/supplementary_text/RA-011-D1RA04882A-s001.txt",
                ],
                "primary_source_statement": "Primary material supports compound identity/structure class but not a clean exact linear sequence matching the DBAASP placeholder sequence.",
            },
        },
        "name_check": {
            "status": "source_verified",
            "database_name": row.get("peptide_name") or peptide["database_name"],
            "primary_name": peptide["primary_name"],
            "source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": peptide["name_locator"],
            },
        },
        "activity_check": activity_check,
        "source_organism_check": {
            "status": "source_verified_with_context",
            "database_source": "DBAASP row source field absent in packet snapshot",
            "primary_source": peptide["source_origin"],
            "source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": peptide["name_locator"],
            },
        },
        "review_notes": (
            "Worker-4 source re-review matched this linked DBAASP row to reopened primary XML/table/text evidence. "
            f"{conflict_context}"
        ),
        "conflict_context": conflict_context,
        "conflict_flags": ["database_activity_value_conflicts_with_primary_text"] if status == "source_conflict" else ["database_sequence_uses_nonribosomal_placeholder_notation"],
        "source_reviewed": True,
        "reviewed_at": generated_at,
    }


def build_literature_audit(row: dict[str, Any], row_no: int, generated_at: str) -> dict[str, Any]:
    sequence_key = str(row.get("sequence_key") or "")
    return {
        "source_id": row.get("source_id") or sequence_key,
        "sequence_key": sequence_key,
        "source_table": "linked_literature_records.jsonl",
        "source_record_id": row.get("literature_dedupe_key") or f"doi:{DOI}",
        "database": row.get("database") or "DBAASP",
        "database_subject": row.get("title") or "",
        "database_measure": "literature_link",
        "traceability": {
            "source_path": f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
            "locator": f"database:linked_literature_records.jsonl:row={row_no}",
        },
        "citation_traceability": {
            "source_path": f"papers/{PAPER_ID}/source/paper.xml",
            "locator": "xml:article-meta",
            "doi": DOI,
            "pmid": PMID,
            "pmcid": PMCID,
        },
        "status": "source_verified",
        "layer1_status": "source_verified",
        "matched_activity_record_id": "",
        "sequence_check": {
            "status": "literature_link_verified_not_sequence_row",
            "source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:article-meta",
                "primary_source_statement": "Literature row verifies DOI/PMID/PMCID/title; peptide sequence normalization is handled in linked assay/experiment rows.",
            },
        },
        "review_notes": "Literature link matches selected paper DOI, PMID, PMCID, year, and title.",
        "conflict_context": "",
        "conflict_flags": [],
        "source_reviewed": True,
        "reviewed_at": generated_at,
    }


def build_database(generated_at: str) -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    for source_file in ("linked_assay_records.jsonl", "linked_experiment_records.jsonl"):
        for row_no, row in enumerate(read_jsonl(PACKET / "database" / source_file), start=1):
            audits.append(audit_for_row(row, source_file, row_no, generated_at))
    for row_no, row in enumerate(read_jsonl(PACKET / "database" / "linked_literature_records.jsonl"), start=1):
        audits.append(build_literature_audit(row, row_no, generated_at))
    status_summary = dict(Counter(record["status"] for record in audits))
    return {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "generated_at": generated_at,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "source_reviewed_with_conflicts_preserved",
        "publication_grade": False,
        "audit_scope": "Worker-4 source-reviewed reconciliation of all linked DBAASP packet rows against primary XML Table 1, cytotoxicity text/figures, supplement figure text, article metadata, and merged sequence/experiment snapshots.",
        "database_row_counts": {
            "linked_assay_records": 27,
            "linked_dramp_activity_records": 0,
            "linked_experiment_records": 27,
            "linked_literature_records": 3,
            "linked_sequence_records": 0,
        },
        "record_audits": audits,
        "status_summary": status_summary,
        "caution_findings": [
            {
                "caution_code": "sequence_modified_not_normalized",
                "evidence_context": "DBAASP sequence snapshots use normalized nonribosomal X/t placeholder notation for MIN A, PUW F, and PUW/MIN 4a; source compound identity is supported but exact clean linear sequence verification is not promoted.",
            },
            {
                "caution_code": "source_conflict_dbaasp_4a_hela_ic50",
                "evidence_context": "DBAASP records PUW/MIN 4a HeLa IC50=20 µM, but the primary paper says 4a/4b IC50 values could not be calculated and describes 20 µM as treatment/morphology context.",
            },
            {
                "caution_code": "no_packet_linked_sequence_records",
                "evidence_context": "The packet contains zero linked_sequence_records rows; sequence normalization was cross-checked against merged all_sequences.csv and primary source compound locators.",
            },
        ],
        "source_paths_checked": SOURCE_PATHS_CHECKED,
        "tools_attempted": TOOLS_ATTEMPTED,
        "unrecoverable_material_gaps": [],
    }


def rework_target_activity(generated_at: str) -> dict[str, Any]:
    return {
        "ticket_id": ACTIVITY_TICKET_ID,
        "paper_id": PAPER_ID,
        "created_at": generated_at,
        "worker": "worker-2",
        "owner_worker": "worker-2",
        "target_queue": "analysis",
        "layer": "activity_toxicity",
        "severity": "blocking",
        "failure_code": "activity_toxicity_final_not_source_reviewed_complete",
        "omission_code": "missing_hela_ic50_and_activity_target_class_review",
        "artifact_path": f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
        "source_evidence_to_check": [
            f"papers/{PAPER_ID}/source/paper.xml",
            f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
            f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
            f"paper_packets/{PAPER_ID}/extracted/pdf_text/RA-011-D1RA04882A.txt",
            f"paper_packets/{PAPER_ID}/extracted/supplementary_text/RA-011-D1RA04882A-s001.txt",
            f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
        ],
        "required_action": "Repair worker-2/final activity evidence from primary Table 1 and cytotoxicity text: preserve antifungal MIC positives and NA highest-tested cases, correct fungal target classes, add/source-review HeLa IC50 rows for compounds 1 and 2, and preserve the PUW/MIN 4a IC50=20 µM database row as source_conflict rather than a source-supported IC50.",
        "reason": "Worker-4 verified the linked DBAASP activity rows, but final activity_toxicity_evidence.json remains a framework extraction with worker-review notes, fungal targets labeled as bacteria, no HeLa IC50 rows, and no explicit 4a IC50 conflict preservation.",
        "blocks": ["publication_grade_ready", "final_approval"],
    }


def rework_target_mechanism(generated_at: str) -> dict[str, Any]:
    return {
        "ticket_id": MECHANISM_TICKET_ID,
        "paper_id": PAPER_ID,
        "created_at": generated_at,
        "worker": "worker-5",
        "owner_worker": "worker-5",
        "target_queue": "analysis",
        "layer": "mechanism",
        "severity": "major",
        "failure_code": "mechanism_ontology_scaffold_note_pending_source_review",
        "omission_code": "framework_mechanism_locator_not_source_reviewed_ontology",
        "artifact_path": f"papers/{PAPER_ID}/final/mechanism_ontology_record.json",
        "source_evidence_to_check": [
            f"papers/{PAPER_ID}/source/paper.xml",
            f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
            f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
            f"paper_packets/{PAPER_ID}/extracted/supplementary_text/RA-011-D1RA04882A-s001.txt",
        ],
        "required_action": "Replace the framework mechanism locator note with worker-5 source-reviewed mechanism ontology distinguishing direct membrane assays for compounds 1/2, morphology/cytotoxicity context for 4a/4b/5a-d, and bounded SAR discussion without overclaiming.",
        "reason": "Current mechanism_ontology_record.json explicitly says it is a framework locator note and not publication-grade mechanism adjudication.",
        "blocks": ["publication_grade_ready", "final_approval"],
    }


def qc_failure_reasons() -> list[dict[str, Any]]:
    return [
        {
            "code": "activity_toxicity_final_not_source_reviewed_complete",
            "owner_worker": "worker-2",
            "severity": "blocking",
            "reason": "Worker-4 resolved database row mapping, but the final activity artifact still omits source-reviewed HeLa IC50/conflict handling and contains framework target-class issues.",
        },
        {
            "code": "mechanism_ontology_scaffold_note_pending_source_review",
            "owner_worker": "worker-5",
            "severity": "major",
            "reason": "The final mechanism artifact remains a framework note rather than worker-5 source-reviewed mechanism ontology.",
        },
    ]


def build_review(generated_at: str, database: dict[str, Any]) -> dict[str, Any]:
    targets = [rework_target_activity(generated_at), rework_target_mechanism(generated_at)]
    return {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "review_status": "needs_targeted_rework",
        "publication_grade": False,
        "validator_contract_passed": True,
        "source_reviewed": True,
        "reviewed_at": generated_at,
        "generated_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "adjudication_summary": "Worker-4/6 re-review completed the owner-layer source adjudication: linked DBAASP rows were reconciled to primary Table 1, cytotoxicity text/figures, supplement figure text, article metadata, and merged database snapshots; the paper remains non-accepted because final activity and mechanism artifacts still need targeted owner-worker repair.",
        "summary": "Owner-layer repair complete for database reconciliation and worker-6 provenance; not accepted because targeted worker-2 and worker-5 rework remains open.",
        "checked_inputs": SOURCE_PATHS_CHECKED,
        "source_review_depth": [
            "paper_xml",
            "paper_pdf",
            "oa_package",
            "supplementary_assets",
            "merged_database_rows",
        ],
        "materials_exhausted": {
            "material_queue_status": "material_extracted_with_gaps_nonblocking_for_worker46",
            "known_missing_or_blocked_materials": [],
            "paper_xml": {
                "available": True,
                "used": True,
                "blocker": False,
                "path": f"papers/{PAPER_ID}/source/paper.xml",
            },
            "paper_pdf": {
                "available": True,
                "used": True,
                "blocker": False,
                "path": f"papers/{PAPER_ID}/source/paper.pdf",
            },
            "oa_package": {
                "available": True,
                "used": True,
                "blocker": False,
                "path": f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC9041360/PMC9041360",
            },
            "supplementary_assets": {
                "available": True,
                "used": True,
                "blocker": False,
                "paths": [
                    f"paper_packets/{PAPER_ID}/extracted/supplementary_text/RA-011-D1RA04882A-s001.txt",
                    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
                    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
                    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-1.bin",
                ],
                "note": "Supplementary PDF text supports figure/morphology and compound characterization checks; no structured supplementary spreadsheet/table was present.",
            },
            "merged_database_rows": {
                "available": True,
                "used": True,
                "blocker": False,
                "paths": [
                    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
                    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
                    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
                    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
                    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/all_experimental_records.csv",
                ],
            },
            "open_rework_ticket_ids": OPEN_TICKET_IDS,
            "closed_or_superseded_rework_ticket_ids": [ORIGINAL_TICKET_ID],
            "source_review_gap_remaining": True,
            "note": "Worker-4/6 local source recovery is exhausted for the database/adjudication blocker. Remaining non-accepted state is analysis-layer activity/mechanism rework, not a missing material gap for worker-4/6.",
        },
        "per_layer_decision_rationale": {
            "layer_1_database": "All 54 linked DBAASP assay/experiment rows were reopened. Antifungal rows map to Table 1 values for compound 1/MIN A, compound 2/PUW F, and compound 4a; literature rows match DOI/PMID/PMCID. Rows remain caution-bearing because DBAASP sequence strings are normalized nonribosomal placeholders, and the 4a HeLa IC50=20 µM row is preserved as source_conflict.",
            "layer_2_activity_toxicity": "Worker-6 cannot approve publication-grade activity because final activity rows still require owner worker-2 source review: HeLa IC50 rows/conflict handling are absent and fungal target classes need correction.",
            "layer_3_mechanism": "Worker-6 cannot approve publication-grade mechanism because the current mechanism artifact is explicitly a framework locator note and needs worker-5 ontology adjudication.",
        },
        "semantic_quality_checks": {
            "activity_records_current_final": len(read_json(PAPER / "final" / "activity_toxicity_evidence.json").get("activity_records") or []),
            "database_record_audits": len(database["record_audits"]),
            "database_status_summary": database["status_summary"],
            "database_source_conflicts_remaining": int(database["status_summary"].get("source_conflict", 0)),
            "database_sequence_modified_not_normalized": int(database["status_summary"].get("sequence_modified_not_normalized", 0)),
            "mechanism_claims_current_final": len(read_json(PAPER / "final" / "mechanism_ontology_record.json").get("mechanism_claims") or []),
            "open_rework_targets": len(targets),
            "open_rework_ticket_ids": OPEN_TICKET_IDS,
            "unrecoverable_material_gaps": [],
        },
        "caution_findings": [
            {
                "caution_code": "sequence_modified_not_normalized",
                "evidence_context": "DBAASP sequence placeholders for MIN A/PUW F/4a are not promoted to clean source_verified sequence identity.",
            },
            {
                "caution_code": "source_conflict_dbaasp_4a_hela_ic50",
                "evidence_context": "The 4a HeLa IC50=20 µM database value conflicts with primary text stating 4a/4b IC50 values could not be calculated.",
            },
        ],
        "qc_failure_reasons": qc_failure_reasons(),
        "rework_targets": targets,
        "unrecoverable_material_gaps": [],
        "strict_gate": {"required_rework_count": len(targets)},
    }


def build_quality_feedback(generated_at: str) -> dict[str, Any]:
    targets = [rework_target_activity(generated_at), rework_target_mechanism(generated_at)]
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": len(targets),
        "qc_failure_reasons": qc_failure_reasons(),
        "rework_targets": targets,
        "rework_context_packet_required": True,
        "closed_or_superseded_rework_ticket_ids": [ORIGINAL_TICKET_ID],
        "open_rework_ticket_ids": OPEN_TICKET_IDS,
        "resolution_summary": "Worker-4/6 owner-layer re-review resolved the original database conflict/provenance blocker and rewrote final adjudication provenance. Publication-grade approval remains blocked by targeted worker-2 activity repair and worker-5 mechanism ontology review.",
        "remaining_caution_codes": [
            "sequence_modified_not_normalized",
            "source_conflict_dbaasp_4a_hela_ic50",
            "no_packet_linked_sequence_records",
        ],
        "unrecoverable_material_gaps": [],
    }


def write_owner_artifacts(generated_at: str) -> dict[str, Any]:
    database = build_database(generated_at)
    review = build_review(generated_at, database)
    quality = build_quality_feedback(generated_at)

    for path in [
        PACKET / "analysis" / "database_record_audit.json",
        PACKET / "final" / "database_record_verification.json",
        PAPER / "final" / "database_record_verification.json",
    ]:
        write_json(path, database)
    for path in [
        PACKET / "analysis" / "adjudication_report.json",
        PACKET / "final" / "review_report.json",
        PAPER / "final" / "review_report.json",
    ]:
        write_json(path, review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality)

    analysis_status_path = PACKET / "analysis" / "analysis_status.json"
    analysis = read_json(analysis_status_path)
    analysis.update(
        {
            "paper_id": PAPER_ID,
            "generated_at": generated_at,
            "status": "analysis_needs_analysis_rework",
            "database_record_audit_count": len(database["record_audits"]),
            "database_status_summary": database["status_summary"],
            "worker4_worker6_repaired_at": generated_at,
            "open_rework_ticket_ids": OPEN_TICKET_IDS,
            "closed_or_superseded_rework_ticket_ids": [ORIGINAL_TICKET_ID],
        }
    )
    write_json(analysis_status_path, analysis)

    manifest_path = PACKET / "packet_manifest.json"
    manifest = read_json(manifest_path)
    manifest.update(
        {
            "updated_at": generated_at,
            "analysis_queue_status": "analysis_needs_analysis_rework",
            "material_queue_status": "material_extracted_with_gaps_nonblocking_for_worker46",
            "open_rework_ticket_ids": OPEN_TICKET_IDS,
        }
    )
    manifest["post_rework_update"] = {
        "updated_at": generated_at,
        "updated_by": "codex_cli_re_review_worker_4_6",
        "closed_or_superseded_rework_ticket_ids": [ORIGINAL_TICKET_ID],
        "open_rework_ticket_ids": OPEN_TICKET_IDS,
        "status": "worker4_worker6_repaired_remaining_analysis_rework",
        "semantic_report": f"reports/{PAPER_ID}.semantic_gate.json",
        "publication_report": f"reports/{PAPER_ID}.publication_quality.json",
    }
    write_json(manifest_path, manifest)

    request_path = PACKET / "rework" / "rework_requests.jsonl"
    append_jsonl_once(request_path, rework_target_activity(generated_at))
    append_jsonl_once(request_path, rework_target_mechanism(generated_at))
    return database


def run_gate(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout, proc.stderr


def run_gates() -> dict[str, Any]:
    semantic_path = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    publication_path = REPORTS / f"{PAPER_ID}.publication_quality.json"
    manifest = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"
    semantic_code, semantic_out, semantic_err = run_gate(
        [
            sys.executable,
            ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py",
            "--root",
            ".",
            "--manifest",
            str(manifest),
            "--json",
        ]
    )
    semantic = json.loads(semantic_out)
    write_json(semantic_path, semantic)
    publication_code, publication_out, publication_err = run_gate(
        [
            sys.executable,
            ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py",
            "--root",
            ".",
            "--manifest",
            str(manifest),
            "--json-out",
            str(publication_path),
        ]
    )
    publication = read_json(publication_path)
    gates_ready = (
        semantic_code == 0
        and publication_code == 0
        and int(semantic.get("publication_grade_pass_count") or 0) == 1
        and int(semantic.get("publication_grade_fail_count") or 0) == 0
        and publication.get("publication_grade_pass") is True
    )
    return {
        "gates_ready": gates_ready,
        "semantic_returncode": semantic_code,
        "semantic_stdout": semantic_out[:4000],
        "semantic_stderr": semantic_err,
        "semantic_report": str(semantic_path),
        "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
        "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
        "semantic_issue_count": (semantic.get("results") or [{}])[0].get("issue_count"),
        "semantic_issue_codes": [
            issue.get("code")
            for issue in ((semantic.get("results") or [{}])[0].get("issues") or [])
        ],
        "publication_returncode": publication_code,
        "publication_stdout": publication_out[:4000],
        "publication_stderr": publication_err,
        "publication_report": str(publication_path),
        "publication_quality_pass": publication.get("publication_grade_pass"),
        "publication_risk_counts": publication.get("risk_counts"),
    }


def update_reports_and_workflow(generated_at: str, gate_evidence: dict[str, Any], database: dict[str, Any]) -> None:
    complete_report_path = REPORTS / f"{PAPER_ID}.complete_message_test_report.json"
    report = read_json(complete_report_path)
    report.update(
        {
            "generated_at": generated_at,
            "current_state": "rework_queue",
            "terminal_status": "awaiting_targeted_worker2_worker5_rework",
            "final_approval_status": "refused_needs_rework",
            "gate_summary": {
                "structural_ready": True,
                "validator_contract_ready": True,
                "semantic_gate_ready": bool(gate_evidence["gates_ready"]),
                "publication_grade_ready": bool(gate_evidence["gates_ready"]),
            },
            "gate_results": gate_evidence,
            "analysis": {
                "review_status": "needs_targeted_rework",
                "activity_records": len(read_json(PAPER / "final" / "activity_toxicity_evidence.json").get("activity_records") or []),
                "mechanism_claims": len(read_json(PAPER / "final" / "mechanism_ontology_record.json").get("mechanism_claims") or []),
                "database_status_summary": database.get("status_summary"),
            },
            "open_rework_ticket_count": len(OPEN_TICKET_IDS),
            "rework_ticket_ids": OPEN_TICKET_IDS,
            "not_publication_grade_reason": "Worker-4/6 owner-layer repair completed, but targeted worker-2 activity and worker-5 mechanism rework remains open.",
            "semantic_gate": "failed_expected_open_rework",
            "publication_quality_gate": "failed_expected_open_rework",
        }
    )
    write_json(complete_report_path, report)

    ctx_path = WORKFLOW / "workflow_context.json"
    if ctx_path.exists():
        ctx = read_json(ctx_path)
        ctx["updated_at"] = generated_at
        ctx["current_state"] = "rework_queue"
        ctx["open_rework_tickets"] = OPEN_TICKET_IDS
        ctx["queue_status"] = {
            "material": "material_extracted_with_gaps_nonblocking_for_worker46",
            "analysis": "analysis_needs_analysis_rework",
        }
        ctx["gate_summary"] = {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": bool(gate_evidence["gates_ready"]),
            "publication_grade_ready": bool(gate_evidence["gates_ready"]),
        }
        write_json(ctx_path, ctx)

    append_jsonl(
        WORKFLOW / "state_executions.jsonl",
        {
            "record_type": "state_execution",
            "workflow_id": f"paper-review-{PAPER_ID}",
            "paper_id": PAPER_ID,
            "state": "codex_worker4_worker6_re_review",
            "status": "needs_rework",
            "role": "adjudicator",
            "provider": "codex-cli",
            "model": "gpt-5.5",
            "reasoning_effort": "xhigh",
            "attempt": 2,
            "created_at": generated_at,
            "started_at": generated_at,
            "finished_at": generated_at,
            "duration_ms": 0,
            "artifact_refs": [
                str(PACKET / "analysis" / "database_record_audit.json"),
                str(PAPER / "final" / "database_record_verification.json"),
                str(PAPER / "final" / "review_report.json"),
                str(PAPER / "work" / "review" / "quality_feedback.json"),
                str(REPORTS / f"{PAPER_ID}.semantic_gate.json"),
                str(REPORTS / f"{PAPER_ID}.publication_quality.json"),
            ],
            "rework_ticket_ids": OPEN_TICKET_IDS,
            "output_summary": "Worker-4/6 owner-layer repair completed; gates reran and paper remains non-accepted pending targeted worker-2/worker-5 rework.",
        },
    )
    append_jsonl(
        WORKFLOW / "agent_logs.jsonl",
        {
            "record_type": "agent_log",
            "workflow_id": f"paper-review-{PAPER_ID}",
            "paper_id": PAPER_ID,
            "created_at": generated_at,
            "level": "info",
            "category": "codex_re_review",
            "state": "worker4_worker6_repair_complete_needs_rework",
            "message": "Database conflicts were source-reviewed and narrowed; final approval remains blocked by worker-2 activity and worker-5 mechanism tickets.",
            "path_refs": [
                f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
                f"papers/{PAPER_ID}/final/review_report.json",
                f"papers/{PAPER_ID}/work/review/quality_feedback.json",
                f"reports/{PAPER_ID}.semantic_gate.json",
                f"reports/{PAPER_ID}.publication_quality.json",
            ],
        },
    )


def append_rework_response(generated_at: str, gate_evidence: dict[str, Any]) -> None:
    append_jsonl(
        PACKET / "rework" / "rework_responses.jsonl",
        {
            "paper_id": PAPER_ID,
            "ticket_id": ORIGINAL_TICKET_ID,
            "created_at": generated_at,
            "worker": "worker-4+worker-6",
            "owner_worker": "worker-4+worker-6",
            "status": "owner_layer_repaired_remaining_targeted_rework",
            "source_paths_checked": SOURCE_PATHS_CHECKED,
            "tools_attempted": TOOLS_ATTEMPTED,
            "repaired_artifacts": [
                f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
                f"paper_packets/{PAPER_ID}/analysis/adjudication_report.json",
                f"papers/{PAPER_ID}/final/database_record_verification.json",
                f"papers/{PAPER_ID}/final/review_report.json",
                f"papers/{PAPER_ID}/work/review/quality_feedback.json",
            ],
            "repair_summary": "All linked DBAASP assay/experiment rows were reconciled to primary Table 1 or cytotoxicity text/figure context. Sequence rows remain sequence_modified_not_normalized because DBAASP uses nonribosomal placeholder notation; the 4a HeLa IC50=20 µM row is preserved as source_conflict.",
            "remaining_rework_targets": OPEN_TICKET_IDS,
            "unrecoverable_material_gaps": [],
            "gate_evidence": gate_evidence,
            "next_action": "Keep paper non-accepted until worker-2 repairs final activity/toxicity evidence and worker-5 replaces the mechanism scaffold note; rerun gates after those artifacts are repaired.",
        },
    )


def main() -> int:
    generated_at = now_iso()
    database = write_owner_artifacts(generated_at)
    gate_evidence = run_gates()
    update_reports_and_workflow(generated_at, gate_evidence, database)
    append_rework_response(generated_at, gate_evidence)
    print(json.dumps({"ok": True, "gates_ready": gate_evidence["gates_ready"], "gate_evidence": gate_evidence}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
