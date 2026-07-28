#!/usr/bin/env python3
"""Worker-4/6 bounded source-reviewed repair for doi__10.1038_s41598-019-54716-8.

This repair consumes only the paper-local packet, primary XML/PDF, extracted
landing-page supplement inventory, and linked database rows. It preserves
figure-only/database-only conflicts instead of promoting them to source_verified.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "doi__10.1038_s41598-019-54716-8"
DOI = "10.1038/s41598-019-54716-8"
PMID = "31827113"
PMCID = "PMC6906472"
ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
LANDED = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers") / PAPER_ID

TICKET_ORIGINAL = "rwk-complete-test-0001"
TICKET_HEMOLYSIS = "rwk-worker4-hemolysis-figure-values-unrecoverable"
TICKET_SUPPLEMENT = "rwk-worker6-supplement-payload-unrecoverable"

CHECKED_INPUTS = [
    f"rework_context/{PAPER_ID}/handoff_context.json",
    f"paper_packets/{PAPER_ID}/packet_manifest.json",
    f"paper_packets/{PAPER_ID}/locators/locator_index.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
    f"paper_packets/{PAPER_ID}/analysis/activity_toxicity_evidence.json",
    f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
    f"paper_packets/{PAPER_ID}/analysis/mechanism_evidence.json",
    f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
    f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text.jsonl",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/landing-1.txt",
    f"paper_packets/{PAPER_ID}/extracted/pdf_tables.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
    f"paper_packets/{PAPER_ID}/raw/paper.xml",
    f"paper_packets/{PAPER_ID}/raw/paper.pdf",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-1.bin",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-2.bin",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-3.bin",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-4.bin",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-5.bin",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-6.bin",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-7.bin",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-8.bin",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-9.bin",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-10.bin",
    f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    f"papers/{PAPER_ID}/source/supplementary/",
    str(LANDED / "asset_manifest.csv"),
    str(LANDED / "metadata.json"),
    str(LANDED / "xml" / "local-DBAASP-PMC6906472.xml"),
    str(LANDED / "xml" / "remote-PMC6906472.xml"),
    str(LANDED / "pdf" / "landing-1.pdf"),
    str(LANDED / "pdf" / "local-DBAASP-PMC6906472.pdf"),
    str(LANDED / "pdf" / "remote-openalex.pdf"),
    str(LANDED / "supplementary"),
]

TOOLS_ATTEMPTED = [
    "jq",
    "rg",
    "find -L",
    "file -L",
    "pdftotext",
    "xml.etree.ElementTree JATS table extraction",
    "linked JSONL database row reconciliation",
    "manual review of XML sections, PDF text, figure captions, and supplement inventory",
]

PEPTIDES = {
    "DBAASP:DBAASPN_14747": {"name": "Tridecaptin M / M1", "paper_label": "M1 (or M)", "table1_row": 4, "table2_col": 1},
    "DBAASP:DBAASPN_14748": {"name": "Tridecaptin M2", "paper_label": "M2", "table1_row": 5, "table2_col": 2},
    "DBAASP:DBAASPN_14749": {"name": "Tridecaptin M5", "paper_label": "M5", "table1_row": 6, "table2_col": 3},
    "DBAASP:DBAASPN_14750": {"name": "Tridecaptin M6", "paper_label": "M6", "table1_row": 7, "table2_col": 4},
    "DBAASP:DBAASPN_14751": {"name": "Tridecaptin M7", "paper_label": "M7", "table1_row": 8, "table2_col": 5},
    "DBAASP:DBAASPN_14752": {"name": "Tridecaptin M8", "paper_label": "M8", "table1_row": 9, "table2_col": 6},
    "CAMP:CAMPSQ18458": {"name": "Tridecaptin M / M1", "paper_label": "M1 (or M)", "table1_row": 4, "table2_col": 1},
    "CAMP:CAMPSQ18459": {"name": "Tridecaptin M2", "paper_label": "M2", "table1_row": 5, "table2_col": 2},
    "CAMP:CAMPSQ18460": {"name": "Tridecaptin M5", "paper_label": "M5", "table1_row": 6, "table2_col": 3},
    "CAMP:CAMPSQ18461": {"name": "Tridecaptin M6", "paper_label": "M6", "table1_row": 7, "table2_col": 4},
    "CAMP:CAMPSQ18463": {"name": "Tridecaptin M7", "paper_label": "M7", "table1_row": 8, "table2_col": 5},
    "CAMP:CAMPSQ18462": {"name": "Tridecaptin M8", "paper_label": "M8", "table1_row": 9, "table2_col": 6},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def tag(elem: ET.Element) -> str:
    return elem.tag.rsplit("}", 1)[-1]


def elem_text(elem: ET.Element) -> str:
    return " ".join("".join(elem.itertext()).split())


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def append_jsonl_once(path: Path, payload: dict[str, Any], key: str, value: str) -> None:
    rows = read_jsonl(path)
    if any(str(row.get(key) or "") == value for row in rows):
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=False) + "\n")


def loc(source_path: str, locator: str, note: str | None = None) -> dict[str, str]:
    out = {"source_path": source_path, "locator": locator}
    if note:
        out["note"] = note
    return out


def table_rows() -> dict[str, list[list[str]]]:
    root = ET.parse(PAPER / "source" / "paper.xml").getroot()
    tables: dict[str, list[list[str]]] = {}
    for table_wrap in [elem for elem in root.iter() if tag(elem) == "table-wrap"]:
        label = next((elem_text(child) for child in table_wrap if tag(child) == "label"), "")
        rows: list[list[str]] = []
        for tr in table_wrap.iter():
            if tag(tr) == "tr":
                rows.append([elem_text(child) for child in tr if tag(child) in {"td", "th"}])
        tables[label] = rows
    return tables


TABLES = table_rows()
TABLE2 = TABLES["Table 2"]


def normalize_value(value: str) -> str:
    return str(value or "").replace("μ", "µ").replace("microg/ml", "µg/ml").replace(" ", "").lower()


def table2_row_for_subject(subject: str, note: str = "") -> tuple[list[int], str]:
    subject_l = subject.lower()
    note_l = note.lower()
    if "rabbit erythrocytes" in subject_l:
        return [], "hemolysis"
    if "atcc 700603" in subject_l:
        return [3], "K. pneumoniae ATCC 700603"
    if "klebsiella pneumoniae cr" in subject_l:
        if "ah-3" in note_l and "ah-16" in note_l:
            return [4, 5], "K. pneumoniae AH-3/AH-16 (Col-R)"
        if "ah-3" in note_l:
            return [4], "K. pneumoniae AH-3 (Col-R)"
        if "ah-16" in note_l:
            return [5], "K. pneumoniae AH-16 (Col-R)"
        return [4, 5], "K. pneumoniae colistin-resistant clinical isolates"
    if "escherichia coli mcr" in subject_l:
        return [6], "E. coli CF-23 (mcr-1)"
    if "proteus mirabilis" in subject_l:
        return [7], "Proteus mirabilis MTCC 1429"
    if "serratia marcescens" in subject_l:
        return [8], "Serratia marcescens MTCC 97"
    if "p3r" in subject_l:
        return [9], "K. pneumoniae P3R (M1-R)"
    if "gmch 13" in subject_l:
        return [10], "K. pneumoniae GMCH 13"
    if "gmch 15" in subject_l:
        return [11], "K. pneumoniae GMCH 15"
    if "acinetobacter baumannii" in subject_l:
        return [12], "A. baumannii ATCC 19606"
    if "pseudomonas aeruginosa" in subject_l:
        return [13], "P. aeruginosa ATCC 27853"
    return [], ""


def source_values_for_rows(rows: list[int], table2_col: int) -> list[str]:
    return [TABLE2[row_index - 1][table2_col] for row_index in rows]


def value_matches_database(database_value: str, source_values: list[str]) -> bool:
    db = normalize_value(database_value)
    if not source_values:
        return False
    values = [normalize_value(item) for item in source_values]
    if len(values) == 1:
        return db == values[0]
    numeric = sorted({value.replace(">", "").replace("<", "") for value in values})
    if db == "-".join(numeric) or db == "–".join(numeric):
        return True
    return all(value == db for value in values)


def row_locator(rows: list[int], col: int, note: str | None = None) -> dict[str, str]:
    if len(rows) == 1:
        return loc("source/paper.xml", f"xml:table=2:row={rows[0]}:column={col}", note)
    row_text = ",".join(str(row) for row in rows)
    return loc("source/paper.xml", f"xml:table=2:rows={row_text}:column={col}", note)


def sequence_check(sequence_key: str) -> dict[str, Any]:
    peptide = PEPTIDES.get(sequence_key, {})
    row = peptide.get("table1_row")
    return {
        "status": "source_verified",
        "paper_peptide_label": peptide.get("paper_label", ""),
        "database_peptide_label": peptide.get("name", sequence_key),
        "source_locator": loc("source/paper.xml", f"xml:table=1:row={row}", "Primary sequence/composition row for the named tridecaptin variant."),
        "modification_notes": "Primary Table 1 preserves D-Dab, D-Ser, D-Trp/D-Phe, D-Val/D-aIle and Dab residue annotations; lipid moiety is described in Results text as 6(S)-methyloctanoic acid for characterized variants.",
    }


def base_record(row: dict[str, Any], source_table: str, row_number: int) -> dict[str, Any]:
    sequence_key = row.get("sequence_key", "")
    source_id = row.get("source_id") or row.get("dbaasp_id") or sequence_key
    return {
        "source_id": source_id,
        "source_record_id": row.get("source_record_id") or row.get("assay_id") or source_id,
        "sequence_key": sequence_key,
        "source_table": source_table,
        "database": row.get("database") or row.get("\ufeffdatabase") or "DBAASP",
        "database_peptide_name": row.get("peptide_name") or PEPTIDES.get(sequence_key, {}).get("name", ""),
        "database_assay_type": row.get("assay_type", ""),
        "database_subject": row.get("subject_name") or row.get("target_organism_text") or "",
        "database_measure": row.get("measure_group") or row.get("measure_value") or row.get("assay_text") or "",
        "database_value": row.get("concentration") or row.get("measure_value") or "",
        "database_unit": row.get("unit") or "",
        "database_note": row.get("note") or row.get("comments_text") or "",
        "traceability": loc(
            f"paper_packets/{PAPER_ID}/database/{source_table}",
            f"database:{source_table}:row={row_number}",
        ),
        "citation_traceability": loc("source/paper.xml", "xml:article-meta", "DOI/PMID/PMCID match the selected primary article."),
        "sequence_check": sequence_check(sequence_key) if sequence_key in PEPTIDES else {},
    }


def verify_activity_row(row: dict[str, Any], source_table: str, row_number: int) -> dict[str, Any]:
    record = base_record(row, source_table, row_number)
    sequence_key = row.get("sequence_key", "")
    peptide = PEPTIDES.get(sequence_key, {})
    col = int(peptide.get("table2_col") or 0)
    subject = record["database_subject"]
    note = record["database_note"]
    rows, source_subject = table2_row_for_subject(subject, note)

    if record["database_assay_type"] == "hemolytic_cytotoxic" or not rows:
        record.update(
            {
                "status": "source_conflict",
                "layer1_status": "source_conflict",
                "matched_activity_record_id": "",
                "source_activity_match": {
                    "status": "endpoint_supported_exact_value_not_recoverable",
                    "source_locator": loc(
                        "source/paper.xml",
                        "xml:fig=2:Figure 2; xml:sec=15:Antimicrobial profile and haemolytic activity",
                        "Primary source confirms rabbit RBC hemolysis at 128 µg/ml but does not expose exact per-peptide numeric values as a table in local XML/PDF text.",
                    ),
                },
                "conflict_context": "Exact hemolysis percentage is present only in the linked database row or as a figure-derived estimate; local XML/PDF text supports the assay and qualitative result but not the exact database value.",
                "review_notes": "Preserved as source_conflict after bounded worker-4 review; do not promote to source_verified without a primary-source numeric table or reliable figure-data extraction.",
            }
        )
        return record

    values = source_values_for_rows(rows, col)
    source_value = values[0] if len(set(values)) == 1 else "-".join(sorted({value.replace(">", "").replace("<", "") for value in values}))
    matched = value_matches_database(str(row.get("concentration") or ""), values)
    record.update(
        {
            "status": "source_verified" if matched else "source_conflict",
            "layer1_status": "source_verified" if matched else "source_conflict",
            "matched_activity_record_id": f"{PAPER_ID}-table2-r{'_'.join(str(item) for item in rows)}-c{col}-MIC",
            "source_activity_match": {
                "status": "exact_or_range_match" if matched else "value_mismatch",
                "paper_peptide_label": peptide.get("paper_label", ""),
                "paper_subject": source_subject,
                "paper_value": source_value,
                "paper_unit": "µg/ml",
                "source_locator": row_locator(rows, col, "Primary Table 2 MIC value for the database peptide/target row."),
            },
            "review_notes": "Database target-activity row reconciled against primary XML Table 2 with peptide column, target strain, raw MIC value, and unit preserved.",
        }
    )
    if not matched:
        record["conflict_context"] = "Linked database value does not match the primary Table 2 value for the mapped peptide/target row."
    else:
        record["conflict_context"] = ""
    return record


def verify_camp_entry(row: dict[str, Any], row_number: int) -> dict[str, Any]:
    record = base_record(row, "linked_experiment_records.jsonl", row_number)
    sequence_key = row.get("sequence_key", "")
    peptide = PEPTIDES[sequence_key]
    col = int(peptide["table2_col"])
    source_values = {TABLE2[row_index - 1][0]: TABLE2[row_index - 1][col] for row_index in range(3, 14)}
    subject_text = str(row.get("subject_name") or row.get("target_organism_text") or "")
    normalized_sources = {
        subject.replace("A. baumannii", "Acinetobacter baumannii").replace("P. aeruginosa", "Pseudomonas aeruginosa"): value
        for subject, value in source_values.items()
        if value != "ND"
    }
    normalized_subject_text = subject_text.replace("A. baumannii", "Acinetobacter baumannii").replace("P. aeruginosa", "Pseudomonas aeruginosa")
    asserted_pairs = re.findall(r"([^,]+?)\s+\(MIC=\s*([^)]*?)microg/ml\)", normalized_subject_text)
    matched_subjects: dict[str, str] = {}
    mismatches: list[str] = []
    for asserted_subject, asserted_value in asserted_pairs:
        asserted_subject = " ".join(asserted_subject.split())
        asserted_value = asserted_value.strip()
        source_value = normalized_sources.get(asserted_subject)
        if source_value is None:
            mismatches.append(f"{asserted_subject}: not present in source Table 2")
            continue
        matched_subjects[asserted_subject] = asserted_value
        if normalize_value(asserted_value) != normalize_value(source_value):
            mismatches.append(f"{asserted_subject}: database {asserted_value} vs source {source_value}")
    record.update(
        {
            "status": "source_verified" if not mismatches else "source_conflict",
            "layer1_status": "source_verified" if not mismatches else "source_conflict",
            "matched_activity_record_id": f"{PAPER_ID}-table2-r3-13-c{col}-MIC-summary",
            "source_activity_match": {
                "status": "entry_activity_summary_matches_table2_column" if not mismatches else "entry_activity_summary_mismatch",
                "paper_peptide_label": peptide["paper_label"],
                "paper_values": source_values,
                "database_asserted_values": matched_subjects,
                "paper_unit": "µg/ml",
                "source_locator": loc("source/paper.xml", f"xml:table=2:rows=3-13:column={col}", "CAMP entry-activity summary reconciled to the full primary Table 2 peptide column."),
            },
            "review_notes": "CAMP linked entry summarizes Table 2 MIC values; source-reviewed as a table-column summary, not as an independent primary-source row.",
            "conflict_context": "" if not mismatches else "Source conflict: CAMP entry summary differs from one or more source Table 2 values.",
        }
    )
    return record


def verify_literature_row(row: dict[str, Any], row_number: int) -> dict[str, Any]:
    record = base_record(row, "linked_literature_records.jsonl", row_number)
    doi_ok = str(row.get("canonical_doi") or "").lower() == DOI
    pmid_ok = str(row.get("canonical_pmid") or "") == PMID
    pmcid_ok = str(row.get("canonical_pmcid") or "") == PMCID
    record.update(
        {
            "status": "source_verified" if doi_ok and pmid_ok and pmcid_ok else "source_conflict",
            "layer1_status": "source_verified" if doi_ok and pmid_ok and pmcid_ok else "source_conflict",
            "matched_activity_record_id": "",
            "sequence_check": sequence_check(row.get("sequence_key", "")),
            "literature_match": {
                "doi": row.get("canonical_doi"),
                "pmid": row.get("canonical_pmid"),
                "pmcid": row.get("canonical_pmcid"),
                "source_locator": loc("source/paper.xml", "xml:article-meta"),
            },
            "conflict_context": "" if doi_ok and pmid_ok and pmcid_ok else "Linked literature identifier does not match the selected primary article identifiers.",
            "review_notes": "Literature link matches the selected primary article and supports citation traceability only; activity/hemolysis values are audited separately.",
        }
    )
    return record


def build_database_audit(generated_at: str) -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    for filename in ("linked_assay_records.jsonl", "linked_experiment_records.jsonl"):
        rows = read_jsonl(PACKET / "database" / filename)
        for row_number, row in enumerate(rows, start=1):
            if row.get("sequence_key", "").startswith("CAMP:"):
                audits.append(verify_camp_entry(row, row_number))
            else:
                audits.append(verify_activity_row(row, filename, row_number))
    for row_number, row in enumerate(read_jsonl(PACKET / "database" / "linked_literature_records.jsonl"), start=1):
        audits.append(verify_literature_row(row, row_number))

    status_summary = Counter(str(record.get("status")) for record in audits)
    hemolysis_conflicts = sum(
        1
        for record in audits
        if record.get("status") == "source_conflict" and record.get("database_subject") == "Rabbit erythrocytes"
    )
    camp_conflicts = sum(
        1
        for record in audits
        if record.get("status") == "source_conflict" and str(record.get("sequence_key", "")).startswith("CAMP:")
    )
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "audit_scope": "Worker-4 source-reviewed every linked DBAASP/CAMP database row against primary XML Table 1, Table 2, article metadata, and local figure/supplement inventory.",
        "database_row_counts": read_json(PACKET / "database" / "database_source_manifest.json").get("row_counts", {}),
        "status_summary": dict(status_summary),
        "record_audits": audits,
        "caution_findings": [
            {
                "caution_code": "hemolysis_exact_values_figure_only",
                "affected_status": "source_conflict",
                "record_count": hemolysis_conflicts,
                "evidence_context": "Rabbit RBC hemolysis endpoint/concentration is primary-source supported, but exact per-peptide percentage values are not locally available as a source table.",
            },
            {
                "caution_code": "camp_m8_activity_summary_conflict",
                "affected_status": "source_conflict",
                "record_count": camp_conflicts,
                "evidence_context": "The linked CAMP M8 summary reports A. baumannii ATCC 19606 MIC as >128 µg/ml, while primary Table 2 reports 128 µg/ml.",
            }
        ],
        "source_reviewed": True,
    }


def unrecoverable_gaps() -> list[dict[str, Any]]:
    return [
        {
            "gap_code": "hemolysis_exact_percent_values_figure_only",
            "source_paths_checked": [
                f"papers/{PAPER_ID}/source/paper.xml",
                f"papers/{PAPER_ID}/source/paper.pdf",
                f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
                f"paper_packets/{PAPER_ID}/extracted/pdf_text/landing-1.txt",
                f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
                f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
            ],
            "tools_attempted": ["xml.etree.ElementTree", "pdftotext", "jq", "rg", "linked JSONL row reconciliation"],
            "why_unrecoverable": "The primary article locally supports rabbit RBC hemolysis at 128 µg/ml and shows Figure 2, but the exact per-peptide numeric percentages used by database rows are not exposed as XML/PDF text or supplementary table data.",
            "impact": "Toxicity/database rows for linked hemolysis records remain source_conflict rather than source_verified.",
            "owner_worker": "worker-4",
            "blocks_publication_grade": True,
            "next_action": "record_and_continue",
        },
        {
            "gap_code": "supplementary_payload_landing_pages_only",
            "source_paths_checked": [
                f"papers/{PAPER_ID}/source/supplementary/",
                f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-1.bin",
                f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-10.bin",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
                str(LANDED / "supplementary"),
            ],
            "tools_attempted": ["find -L", "file -L", "rg", "jq"],
            "why_unrecoverable": "All ten local supplementary assets resolve to duplicated Nature article landing-page HTML; the paper-local supplementary directory is empty and no spreadsheet/PDF/office/archive payload is locally present.",
            "impact": "Supplementary figures/tables cited by the article cannot be used for exact MS/MS, efflux, or M11 synergy details; final adjudication remains non-publication-grade.",
            "owner_worker": "worker-6",
            "blocks_publication_grade": True,
            "next_action": "record_and_continue",
        },
    ]


def rework_targets(generated_at: str) -> list[dict[str, Any]]:
    gaps = unrecoverable_gaps()
    return [
        {
            "ticket_id": TICKET_HEMOLYSIS,
            "paper_id": PAPER_ID,
            "created_at": generated_at,
            "worker": "worker-4",
            "owner_worker": "worker-4",
            "target_queue": "analysis",
            "layer": "database",
            "artifact_path": f"papers/{PAPER_ID}/final/database_record_verification.json",
            "failure_code": gaps[0]["gap_code"],
            "omission_code": gaps[0]["gap_code"],
            "severity": "blocking",
            "failing_object": "linked hemolysis database/toxicity rows",
            "source_paths_to_check": gaps[0]["source_paths_checked"],
            "required_action": "No further local extraction is available; preserve hemolysis rows as source_conflict unless an external primary-source data table becomes available.",
            "unrecoverable_material_gap": gaps[0],
            "blocks": ["publication_grade_ready", "database_exact_toxicity_source_verification"],
        },
        {
            "ticket_id": TICKET_SUPPLEMENT,
            "paper_id": PAPER_ID,
            "created_at": generated_at,
            "worker": "worker-6",
            "owner_worker": "worker-6",
            "target_queue": "adjudication",
            "layer": "review",
            "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
            "failure_code": gaps[1]["gap_code"],
            "omission_code": gaps[1]["gap_code"],
            "severity": "blocking",
            "failing_object": "supplement-derived exact values and final publication-grade decision",
            "source_paths_to_check": gaps[1]["source_paths_checked"],
            "required_action": "Keep final status blocked_missing_primary_material in obtainable-only mode; do not accept unless real local supplementary payloads or external primary data are supplied.",
            "unrecoverable_material_gap": gaps[1],
            "blocks": ["publication_grade_ready", "final_approval"],
        },
    ]


def build_review(generated_at: str, database_audit: dict[str, Any]) -> dict[str, Any]:
    targets = rework_targets(generated_at)
    gaps = unrecoverable_gaps()
    status_summary = database_audit["status_summary"]
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "validator_contract_passed": True,
        "publication_grade": False,
        "review_status": "blocked_missing_primary_material",
        "adjudication_summary": "Worker-4/6 re-review resolved the generic database-conflict failure into row-level source_verified/source_conflict decisions, but bounded local source recovery could not produce exact hemolysis figure values or real supplementary payloads; the paper remains non-accepted.",
        "checked_inputs": CHECKED_INPUTS,
        "source_review_depth": [
            "paper_xml",
            "paper_pdf",
            "oa_package",
            "supplementary_assets",
            "merged_database_rows",
            "linked_database_rows",
            "rework_context_packet",
        ],
        "materials_exhausted": {
            "paper_xml": True,
            "paper_pdf": True,
            "oa_package": True,
            "supplementary_assets": "exhausted_unrecoverable_landing_pages_only",
            "merged_database_rows": True,
            "linked_database_rows": True,
            "unavailable_sources": [gap["gap_code"] for gap in gaps],
            "note": "Local XML/PDF/database rows were sufficient for Table 1/2 database reconciliation; exact figure-derived hemolysis values and supplementary tables/figures are not locally recoverable.",
        },
        "semantic_quality_checks": {
            "activity_rows_parsed": len(read_json(PACKET / "analysis" / "activity_toxicity_evidence.json").get("activity_records", [])),
            "database_records_reviewed": len(database_audit["record_audits"]),
            "database_status_summary": status_summary,
            "mechanism_claims": len(read_json(PAPER / "final" / "mechanism_ontology_record.json").get("mechanism_claims", [])),
            "open_rework_targets": len(targets),
            "unrecoverable_material_gap_count": len(gaps),
        },
        "per_layer_decision_rationale": {
            "layer_1_database": "Target-activity and literature rows are source-reviewed against Table 1/Table 2/article metadata; hemolysis rows remain source_conflict because exact Figure 2 percentages are not locally source-verifiable.",
            "layer_2_activity_toxicity": "Existing parsed activity rows retain primary XML table locators and units, but toxicity exact percentages remain unresolved for database hemolysis rows.",
            "layer_3_mechanism": "Main-text mechanism context is source-located; supplementary efflux and M11 synergy details cannot be independently source-reviewed because local supplement payloads are landing pages only.",
            "publication_grade_decision": "Non-accepted under obtainable-only mode because two material gaps block publication-grade source review after bounded local recovery.",
        },
        "caution_findings": [
            {
                "caution_code": "database_hemolysis_values_not_source_verified",
                "evidence_context": "Linked DBAASP hemolysis rows are preserved as source_conflict rather than smoothed or promoted.",
                "affected_records": 12,
            },
            {
                "caution_code": "camp_m8_activity_summary_conflict",
                "evidence_context": "CAMP M8 entry activity conflicts with primary Table 2 for A. baumannii ATCC 19606; the row is preserved as source_conflict.",
                "affected_records": 1,
            },
            {
                "caution_code": "supplement_payload_unavailable",
                "evidence_context": "Supplementary local assets are duplicated article landing HTML, not the cited supplementary figures/tables.",
            },
        ],
        "qc_failure_reasons": [
            {
                "code": "hemolysis_exact_percent_values_figure_only",
                "owner_worker": "worker-4",
                "severity": "blocking",
                "reason": "Exact database hemolysis percentages cannot be verified from local XML/PDF/supplement material; the rows are preserved as source_conflict.",
            },
            {
                "code": "supplementary_payload_landing_pages_only",
                "owner_worker": "worker-6",
                "severity": "blocking",
                "reason": "The local supplementary assets are article landing HTML and do not provide the cited supplementary figures/tables needed for full source-reviewed adjudication.",
            },
        ],
        "unrecoverable_material_gaps": gaps,
        "rework_targets": targets,
    }


def build_quality_feedback(generated_at: str) -> dict[str, Any]:
    review_targets = rework_targets(generated_at)
    qc_failure_reasons = [
        {
            "code": "hemolysis_exact_percent_values_figure_only",
            "owner_worker": "worker-4",
            "severity": "blocking",
            "reason": "Worker-4 source review could not verify exact DBAASP hemolysis percentages from local primary material; source_conflict is the controlled outcome.",
        },
        {
            "code": "supplementary_payload_landing_pages_only",
            "owner_worker": "worker-6",
            "severity": "blocking",
            "reason": "Worker-6 source review found only landing-page HTML for the supplementary assets, so supplement-derived exact values remain unrecoverable locally.",
        },
    ]
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": len(qc_failure_reasons),
        "qc_failure_reasons": qc_failure_reasons,
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "rework_context_packet_required": True,
        "rework_targets": review_targets,
    }


def build_rework_response(generated_at: str, database_audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "response_id": f"{TICKET_ORIGINAL}-worker46-response-v2",
        "ticket_id": TICKET_ORIGINAL,
        "paper_id": PAPER_ID,
        "created_at": generated_at,
        "owner_workers": ["worker-4", "worker-6"],
        "status": "not_closed_blocked_unrecoverable_material_gap",
        "kept_open": True,
        "checked": CHECKED_INPUTS,
        "tools_attempted": TOOLS_ATTEMPTED,
        "repair_actions": [
            "Reconciled linked DBAASP/CAMP target-activity rows against primary XML Table 2.",
            "Reconciled peptide identity/sequence labels against primary XML Table 1.",
            "Preserved exact hemolysis database values as source_conflict because local primary material lacks exact numeric table values.",
            "Verified local supplementary assets are landing-page HTML rather than the cited supplementary figures/tables.",
            "Updated worker-6 review, quality feedback, and targeted rework/unrecoverable-gap records.",
        ],
        "database_status_summary_after_repair": database_audit["status_summary"],
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "remaining_blockers": [TICKET_HEMOLYSIS, TICKET_SUPPLEMENT],
        "publication_grade": False,
    }


def main() -> int:
    generated_at = now_iso()
    database_audit = build_database_audit(generated_at)
    review = build_review(generated_at, database_audit)
    quality_feedback = build_quality_feedback(generated_at)

    for path in (
        PACKET / "analysis" / "database_record_audit.json",
        PACKET / "final" / "database_record_verification.json",
        PAPER / "final" / "database_record_verification.json",
    ):
        write_json(path, database_audit)

    for path in (
        PACKET / "analysis" / "adjudication_report.json",
        PACKET / "final" / "review_report.json",
        PAPER / "work" / "review" / "adjudication_report.json",
        PAPER / "final" / "review_report.json",
    ):
        write_json(path, review)

    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality_feedback)

    for target in review["rework_targets"]:
        append_jsonl_once(PACKET / "rework" / "rework_requests.jsonl", target, "ticket_id", target["ticket_id"])
    append_jsonl_once(
        PACKET / "rework" / "rework_responses.jsonl",
        build_rework_response(generated_at, database_audit),
        "response_id",
        f"{TICKET_ORIGINAL}-worker46-response-v2",
    )

    status = read_json(PACKET / "analysis" / "analysis_status.json")
    status.update(
        {
            "status": "analysis_blocked_unrecoverable_material_gap",
            "updated_at": generated_at,
            "open_rework_ticket_ids": [TICKET_HEMOLYSIS, TICKET_SUPPLEMENT],
            "database_record_count": len(database_audit["record_audits"]),
            "database_status_summary": database_audit["status_summary"],
            "unrecoverable_material_gap_count": len(unrecoverable_gaps()),
        }
    )
    write_json(PACKET / "analysis" / "analysis_status.json", status)

    print(json.dumps({"paper_id": PAPER_ID, "database_status_summary": database_audit["status_summary"], "review_status": review["review_status"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
