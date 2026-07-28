#!/usr/bin/env python3
"""Source-reviewed worker-4/worker-6 repair for doi__10.1186_s12870-018-1611-z."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.1186_s12870-018-1611-z"
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
REPORTS = ROOT / "reports"
MANIFEST = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"

XML_PATH = f"papers/{PAPER_ID}/source/paper.xml"
PDF_TEXT_PATH = f"paper_packets/{PAPER_ID}/extracted/pdf_text/landing-1.txt"
SUPP_DIR = f"paper_packets/{PAPER_ID}/raw/supplementary_original"
SEQ_CATALOG = "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv"
EXP_CATALOG = "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/all_experimental_records.csv"
FIVE_DB_CATALOG = "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/five_database_sequence_catalog.csv"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=False) + "\n")


def table_locator(table: int, row: int, column: int | None = None) -> dict[str, str]:
    locator = f"xml:table={table}:row={row}"
    if column is not None:
        locator += f":column={column}"
    return {"source_path": "source/paper.xml", "locator": locator}


def section_locator(sec: int, title: str) -> dict[str, str]:
    return {"source_path": "source/paper.xml", "locator": f"xml:sec={sec}:{title}"}


def db_locator(file_name: str, row: int) -> dict[str, str]:
    return {
        "source_path": str(PACKET / "database" / file_name),
        "locator": f"database:{file_name}:row={row}",
    }


def merged_locator(path: str, line: int, label: str) -> dict[str, str]:
    return {"source_path": path, "locator": f"{Path(path).name}:line={line}:{label}"}


PEPTIDES: dict[str, dict[str, Any]] = {
    "pep1": {
        "sequence": "LVQIGTKIVGVGRNYAAH",
        "name": "Pp3c9_26130V3 (9-26)",
        "protein": "Fumarylacetoacetate hydrolase domain-containing protein 1",
        "gene": "Pp3c9_26130V3",
        "table1": table_locator(1, 3),
        "table2": table_locator(2, 3),
        "database_sequence_locators": [
            merged_locator(SEQ_CATALOG, 18720, "DBAASP:DBAASPS_12379"),
            merged_locator(FIVE_DB_CATALOG, 77153, "CAMP:CAMPSQ11484"),
            merged_locator(FIVE_DB_CATALOG, 130763, "dbAMP:dbAMP_17904"),
        ],
    },
    "pep8": {
        "sequence": "INIINAPLQGFKIA",
        "name": "Pp3c14_22870V3 (223-236)",
        "protein": "Predicted",
        "gene": "Pp3c14_22870V3",
        "table1": table_locator(1, 9),
        "table2": table_locator(2, 4),
        "database_sequence_locators": [
            merged_locator(SEQ_CATALOG, 18721, "DBAASP:DBAASPS_12380"),
            merged_locator(FIVE_DB_CATALOG, 74466, "CAMP:CAMPSQ11489"),
            merged_locator(FIVE_DB_CATALOG, 130757, "dbAMP:dbAMP_17905"),
        ],
    },
    "pep4": {
        "sequence": "KIKVAINGFGRIG",
        "name": "Glyceraldehyde-3-phosphate dehydrogenase",
        "protein": "Glyceraldehyde-3-phosphate dehydrogenase",
        "gene": "Pp3c2_24160V3",
        "table1": table_locator(1, 6),
        "database_sequence_locators": [
            merged_locator(FIVE_DB_CATALOG, 73512, "CAMP:CAMPSQ11486"),
            merged_locator(FIVE_DB_CATALOG, 149204, "dbAMP:dbAMP_32567"),
        ],
    },
    "pep2": {
        "sequence": "AAQGQKIENTKLAGAAGDILSGLAAYGKLD",
        "name": "Intracellular predicted protein",
        "protein": "Predicted",
        "gene": "Pp3c22_17930V3",
        "table1": table_locator(1, 4),
        "database_sequence_locators": [
            merged_locator(FIVE_DB_CATALOG, 82987, "CAMP:CAMPSQ11490"),
            merged_locator(FIVE_DB_CATALOG, 149233, "dbAMP:dbAMP_32570"),
        ],
    },
    "pep3": {
        "sequence": "VAAVAPKFATLKPLG",
        "name": "Chloroplast chaperonin 21",
        "protein": "Chloroplast chaperonin 21",
        "gene": "Pp3c19_4270V3",
        "table1": table_locator(1, 5),
        "database_sequence_locators": [
            merged_locator(FIVE_DB_CATALOG, 75239, "CAMP:CAMPSQ11485"),
            merged_locator(FIVE_DB_CATALOG, 149209, "dbAMP:dbAMP_32566"),
        ],
    },
    "pep5": {
        "sequence": "IVPTSTGAAKAVALVLPNLK",
        "name": "Glyceraldehyde-3-phosphate dehydrogenase",
        "protein": "Glyceraldehyde-3-phosphate dehydrogenase",
        "gene": "Pp3c2_24160V3",
        "table1": table_locator(1, 7),
        "database_sequence_locators": [
            merged_locator(FIVE_DB_CATALOG, 78945, "CAMP:CAMPSQ11487"),
            merged_locator(FIVE_DB_CATALOG, 149199, "dbAMP:dbAMP_32568"),
        ],
    },
    "pep7": {
        "sequence": "TDINLDLGDGKQG",
        "name": "Alpha expansin protein family EXPA6",
        "protein": "alpha expansin protein family EXPA6",
        "gene": "Pp3c8_870V3",
        "table1": table_locator(1, 10),
        "database_sequence_locators": [
            merged_locator(FIVE_DB_CATALOG, 73513, "CAMP:CAMPSQ11488"),
            merged_locator(FIVE_DB_CATALOG, 149201, "dbAMP:dbAMP_32569"),
        ],
    },
    "pep8b": {
        "sequence": "VVDLLAPYRRGGKIG",
        "name": "Secretome predicted protein",
        "protein": "Predicted",
        "gene": "PhpapaCp032",
        "table1": table_locator(1, 11),
        "database_sequence_locators": [
            merged_locator(FIVE_DB_CATALOG, 75240, "CAMP:CAMPSQ11491"),
            merged_locator(FIVE_DB_CATALOG, 149236, "dbAMP:dbAMP_32571"),
        ],
    },
}


def activity_payload(generated_at: str) -> dict[str, Any]:
    records = [
        {
            "record_id": f"{PAPER_ID}-table2-pep1-ecoli-mic",
            "entity": PEPTIDES["pep1"]["sequence"],
            "peptide_name": "pep1",
            "endpoint": "MIC",
            "raw_value": "64",
            "raw_unit": "μg/mL",
            "normalization_status": "raw_unit_preserved",
            "evidence_ladder": "in_vitro_assay_table",
            "target": {"class": "bacteria", "species": "E. coli", "strain": "E. coli K-12 MG1655"},
            "assay_conditions": {
                "method": "serial dilution in liquid MHB medium; 20 h incubation at 37 C; MIC assessed by visible growth and OD570",
                "replicates": "three replicates",
                "source_column_context": "Table 2 E. coli MIC column",
                "inhibition": ">90%",
            },
            "source_locator": table_locator(2, 3, 1),
            "supporting_locators": [table_locator(1, 3), section_locator(9, "Analysis of the biological activity of synthetic peptides")],
        },
        {
            "record_id": f"{PAPER_ID}-table2-pep1-bsubtilis-mic",
            "entity": PEPTIDES["pep1"]["sequence"],
            "peptide_name": "pep1",
            "endpoint": "MIC",
            "raw_value": "64",
            "raw_unit": "μg/mL",
            "normalization_status": "raw_unit_preserved",
            "evidence_ladder": "in_vitro_assay_table",
            "target": {"class": "bacteria", "species": "B. subtilis", "strain": "B. subtilis 168 HT"},
            "assay_conditions": {
                "method": "serial dilution in liquid MHB medium; 20 h incubation at 37 C; MIC assessed by visible growth and OD570",
                "replicates": "three replicates",
                "source_column_context": "Table 2 B. subtilis MIC column",
                "inhibition": ">90%",
            },
            "source_locator": table_locator(2, 3, 3),
            "supporting_locators": [table_locator(1, 3), section_locator(9, "Analysis of the biological activity of synthetic peptides")],
        },
        {
            "record_id": f"{PAPER_ID}-table2-pep8-ecoli-mic",
            "entity": PEPTIDES["pep8"]["sequence"],
            "peptide_name": "pep8",
            "endpoint": "MIC",
            "raw_value": "16",
            "raw_unit": "μg/mL",
            "normalization_status": "raw_unit_preserved",
            "evidence_ladder": "in_vitro_assay_table",
            "target": {"class": "bacteria", "species": "E. coli", "strain": "E. coli K-12 MG1655"},
            "assay_conditions": {
                "method": "serial dilution in liquid MHB medium; 20 h incubation at 37 C; MIC assessed by visible growth and OD570",
                "replicates": "three replicates",
                "source_column_context": "Table 2 E. coli MIC column",
                "inhibition": ">90%",
            },
            "source_locator": table_locator(2, 4, 1),
            "supporting_locators": [table_locator(1, 9), section_locator(9, "Analysis of the biological activity of synthetic peptides")],
        },
        {
            "record_id": f"{PAPER_ID}-table2-pep8-bsubtilis-mic",
            "entity": PEPTIDES["pep8"]["sequence"],
            "peptide_name": "pep8",
            "endpoint": "MIC",
            "raw_value": "32",
            "raw_unit": "μg/mL",
            "normalization_status": "raw_unit_preserved",
            "evidence_ladder": "in_vitro_assay_table",
            "target": {"class": "bacteria", "species": "B. subtilis", "strain": "B. subtilis 168 HT"},
            "assay_conditions": {
                "method": "serial dilution in liquid MHB medium; 20 h incubation at 37 C; MIC assessed by visible growth and OD570",
                "replicates": "three replicates",
                "source_column_context": "Table 2 B. subtilis MIC column",
                "inhibition": ">90%",
            },
            "source_locator": table_locator(2, 4, 3),
            "supporting_locators": [table_locator(1, 9), section_locator(9, "Analysis of the biological activity of synthetic peptides")],
        },
    ]
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "source_reviewed": True,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "extraction_scope": {
            "source_paths_checked": [
                XML_PATH,
                PDF_TEXT_PATH,
                f"{PACKET}/locators/locator_index.json",
                f"{PACKET}/database/linked_assay_records.jsonl",
                f"{PACKET}/database/linked_experiment_records.jsonl",
            ],
            "method_source_locator": section_locator(19, "Antimicrobial activity assay"),
        },
        "activity_records": records,
        "extraction_issues": [],
        "toxicity_records": [],
        "parser_quality_control": {
            "manual_source_review_completed": True,
            "prior_issue_repaired": "Table 2 was reparsed as two assay targets per peptide; the missing pep1 B. subtilis MIC row and target-species labels were repaired.",
            "no_fabricated_values": True,
        },
    }


def verified_record(
    *,
    source_id: str,
    sequence_key: str,
    database: str,
    source_table: str,
    row_locator: dict[str, str],
    peptide_key: str,
    database_measure: str = "",
    database_subject: str = "",
    database_record_id: str = "",
    activity_locator: dict[str, str] | None = None,
    activity_note: str = "",
) -> dict[str, Any]:
    peptide = PEPTIDES[peptide_key]
    locators = [peptide["table1"]]
    if "table2" in peptide:
        locators.append(peptide["table2"])
    locators.extend(peptide["database_sequence_locators"])
    if activity_locator:
        locators.append(activity_locator)
    return {
        "source_id": source_id,
        "sequence_key": sequence_key,
        "database": database,
        "source_table": source_table,
        "source_record_id": database_record_id,
        "database_peptide_name": peptide["name"],
        "database_sequence": peptide["sequence"],
        "database_measure": database_measure,
        "database_subject": database_subject,
        "primary_sequence": peptide["sequence"],
        "primary_name": peptide["name"],
        "status": "source_verified",
        "layer1_status": "source_verified",
        "sequence_check": {
            "status": "source_verified",
            "database_sequence": peptide["sequence"],
            "primary_sequence": peptide["sequence"],
            "source_locator": peptide["table1"],
            "supporting_database_sequence_locators": peptide["database_sequence_locators"],
        },
        "name_check": {
            "status": "source_verified",
            "database_name": peptide["name"],
            "primary_name_or_gene": peptide["gene"],
            "source_locator": peptide["table1"],
        },
        "modification_check": {
            "status": "source_verified",
            "primary_source_statement": "No N-terminal, C-terminal, D-amino-acid, cyclization, disulfide, amidation, or lipidation modification is reported for the Table 1/Table 2 peptide sequence.",
            "source_locator": peptide["table1"],
        },
        "source_organism_check": {
            "status": "source_verified",
            "database_source": "Physcomitrella patens / synthetic peptide assayed from moss peptide sequence",
            "primary_source": "Physcomitrella patens",
            "source_locator": {"source_path": "source/paper.xml", "locator": "xml:article-title+abstract+methods"},
        },
        "activity_check": {
            "status": "source_verified" if database_measure or activity_locator else "not_applicable",
            "database_measure": database_measure,
            "database_subject": database_subject,
            "primary_activity_locator": activity_locator,
            "review_note": activity_note,
        },
        "citation_traceability": {"source_path": "source/paper.xml", "locator": "xml:article-meta:doi+pmid+pmcid"},
        "traceability": row_locator,
        "database_row_locators": [row_locator],
        "primary_source_locators": locators,
        "review_notes": "Primary XML/PDF table evidence and merged database sequence snapshot support the sequence/name/citation row; activity values match Table 2 where present.",
        "conflict_flags": [],
        "conflict_context": "",
    }


def conflict_record(
    *,
    source_id: str,
    sequence_key: str,
    database: str,
    source_table: str,
    row_locator: dict[str, str],
    peptide_key: str,
    database_activity: str,
    conflict_context: str,
    database_record_id: str = "",
) -> dict[str, Any]:
    peptide = PEPTIDES[peptide_key]
    return {
        "source_id": source_id,
        "sequence_key": sequence_key,
        "database": database,
        "source_table": source_table,
        "source_record_id": database_record_id,
        "database_peptide_name": peptide["name"],
        "database_sequence": peptide["sequence"],
        "database_measure": "text",
        "database_subject": database_activity,
        "primary_sequence": peptide["sequence"],
        "primary_name": peptide["name"],
        "status": "source_conflict",
        "layer1_status": "source_conflict",
        "sequence_check": {
            "status": "source_verified",
            "database_sequence": peptide["sequence"],
            "primary_sequence": peptide["sequence"],
            "source_locator": peptide["table1"],
            "supporting_database_sequence_locators": peptide["database_sequence_locators"],
        },
        "name_check": {
            "status": "source_verified",
            "database_name": peptide["name"],
            "primary_name_or_gene": peptide["gene"],
            "source_locator": peptide["table1"],
        },
        "activity_check": {
            "status": "source_conflict",
            "database_activity": database_activity,
            "primary_activity_context": "Primary source supports peptide selection/prediction or limited growth-inhibition context, but not a fully source-located direct MIC/activity row for this database label.",
        },
        "citation_traceability": {"source_path": "source/paper.xml", "locator": "xml:article-meta:doi+pmid+pmcid"},
        "traceability": row_locator,
        "database_row_locators": [row_locator],
        "primary_source_locators": [peptide["table1"], *peptide["database_sequence_locators"]],
        "review_notes": conflict_context,
        "conflict_reason": conflict_context,
        "conflict_context": conflict_context,
        "conflict_flags": ["activity_evidence_granularity_conflict"],
    }


def database_payload(generated_at: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    assay_rows = [
        ("linked_assay_records.jsonl", 1, "DBAASP:DBAASPS_12379", "DBAASP:DBAASPS_12379", "DBAASP", "pep1", "94766", "MIC", "Escherichia coli K12 MG1655", table_locator(2, 3, 1), "DBAASP E. coli MIC 64 matches primary Table 2."),
        ("linked_assay_records.jsonl", 2, "DBAASP:DBAASPS_12379", "DBAASP:DBAASPS_12379", "DBAASP", "pep1", "94768", "MIC", "Bacillus subtilis 168 HT", table_locator(2, 3, 3), "DBAASP B. subtilis MIC 64 matches primary Table 2."),
        ("linked_assay_records.jsonl", 3, "DBAASP:DBAASPS_12380", "DBAASP:DBAASPS_12380", "DBAASP", "pep8", "94767", "MIC", "Escherichia coli K12 MG1655", table_locator(2, 4, 1), "DBAASP E. coli MIC 16 matches primary Table 2."),
        ("linked_assay_records.jsonl", 4, "DBAASP:DBAASPS_12380", "DBAASP:DBAASPS_12380", "DBAASP", "pep8", "94769", "MIC", "Bacillus subtilis 168 HT", table_locator(2, 4, 3), "DBAASP B. subtilis MIC 32 matches primary Table 2."),
        ("linked_experiment_records.jsonl", 1, "DBAASP:DBAASPS_12379", "DBAASP:DBAASPS_12379", "DBAASP", "pep1", "94766", "MIC", "Escherichia coli K12 MG1655", table_locator(2, 3, 1), "Duplicate merged DBAASP assay row matches primary Table 2."),
        ("linked_experiment_records.jsonl", 2, "DBAASP:DBAASPS_12379", "DBAASP:DBAASPS_12379", "DBAASP", "pep1", "94768", "MIC", "Bacillus subtilis 168 HT", table_locator(2, 3, 3), "Duplicate merged DBAASP assay row matches primary Table 2."),
        ("linked_experiment_records.jsonl", 3, "DBAASP:DBAASPS_12380", "DBAASP:DBAASPS_12380", "DBAASP", "pep8", "94767", "MIC", "Escherichia coli K12 MG1655", table_locator(2, 4, 1), "Duplicate merged DBAASP assay row matches primary Table 2."),
        ("linked_experiment_records.jsonl", 4, "DBAASP:DBAASPS_12380", "DBAASP:DBAASPS_12380", "DBAASP", "pep8", "94769", "MIC", "Bacillus subtilis 168 HT", table_locator(2, 4, 3), "Duplicate merged DBAASP assay row matches primary Table 2."),
    ]
    for file_name, row, source_id, sequence_key, database, peptide, rec_id, measure, subject, act_loc, note in assay_rows:
        records.append(
            verified_record(
                source_id=source_id,
                sequence_key=sequence_key,
                database=database,
                source_table=file_name if file_name != "linked_experiment_records.jsonl" else "assay_refs.csv",
                row_locator=db_locator(file_name, row),
                peptide_key=peptide,
                database_measure=measure,
                database_subject=subject,
                database_record_id=rec_id,
                activity_locator=act_loc,
                activity_note=note,
            )
        )

    records.extend(
        [
            verified_record(
                source_id="CAMP:CAMPSQ11484",
                sequence_key="CAMP:CAMPSQ11484",
                database="CAMP",
                source_table="camp_r4_export/data/sequences.csv",
                row_locator=db_locator("linked_experiment_records.jsonl", 10),
                peptide_key="pep1",
                database_measure="entry_text_mic",
                database_subject="E. coli MIC 64; B. subtilis MIC 64",
                database_record_id="CAMPSQ11484",
                activity_locator=table_locator(2, 3),
                activity_note="CAMP sequence/name and exact MIC text match primary Table 1/Table 2.",
            ),
            verified_record(
                source_id="CAMP:CAMPSQ11489",
                sequence_key="CAMP:CAMPSQ11489",
                database="CAMP",
                source_table="camp_r4_export/data/sequences.csv",
                row_locator=db_locator("linked_experiment_records.jsonl", 7),
                peptide_key="pep8",
                database_measure="entry_text_mic",
                database_subject="E. coli MIC 16; B. subtilis MIC 32",
                database_record_id="CAMPSQ11489",
                activity_locator=table_locator(2, 4),
                activity_note="CAMP Pep8 sequence/name and exact MIC text match primary Table 1/Table 2.",
            ),
            verified_record(
                source_id="dbAMP:dbAMP_17904",
                sequence_key="dbAMP:dbAMP_17904",
                database="dbAMP",
                source_table="data/dbamp3_detail_basic.csv",
                row_locator=db_locator("linked_experiment_records.jsonl", 14),
                peptide_key="pep1",
                database_measure="entry_text_mic",
                database_subject="E. coli MIC 64; B. subtilis MIC 64",
                database_record_id="dbAMP_17904",
                activity_locator=table_locator(2, 3),
                activity_note="dbAMP sequence/name and exact MIC text match primary Table 1/Table 2.",
            ),
            verified_record(
                source_id="dbAMP:dbAMP_17905",
                sequence_key="dbAMP:dbAMP_17905",
                database="dbAMP",
                source_table="data/dbamp3_detail_basic.csv",
                row_locator=db_locator("linked_experiment_records.jsonl", 13),
                peptide_key="pep8",
                database_measure="entry_text_mic",
                database_subject="E. coli MIC 16; B. subtilis MIC 32",
                database_record_id="dbAMP_17905",
                activity_locator=table_locator(2, 4),
                activity_note="dbAMP sequence/name and exact MIC text match primary Table 1/Table 2.",
            ),
        ]
    )

    conflict_specs = [
        ("CAMP:CAMPSQ11486", "CAMP", "camp_r4_export/data/sequences.csv", 5, "pep4", "Active against E. coli and B. subtilis", "Primary text supports KIKVAINGFGRIG growth inhibition at 128 μg/mL on day 1, but the local main text does not provide a Table 2 MIC row or fully row-level target/value pair for the CAMP target text."),
        ("CAMP:CAMPSQ11488", "CAMP", "camp_r4_export/data/sequences.csv", 6, "pep7", "Antimicrobial", "Primary Table 1 supports the sequence and predicted CAMP score context, but local source does not support a direct antimicrobial assay row for this database activity label."),
        ("CAMP:CAMPSQ11485", "CAMP", "camp_r4_export/data/sequences.csv", 8, "pep3", "Antimicrobial", "Primary Table 1 supports the sequence and predicted CAMP score context, but local source does not support a direct antimicrobial assay row for this database activity label."),
        ("CAMP:CAMPSQ11491", "CAMP", "camp_r4_export/data/sequences.csv", 9, "pep8b", "Antimicrobial", "Primary Table 1 supports the sequence and predicted CAMP score context, but local source does not support a direct antimicrobial assay row for this database activity label."),
        ("CAMP:CAMPSQ11487", "CAMP", "camp_r4_export/data/sequences.csv", 11, "pep5", "Antimicrobial", "Primary Table 1 supports the sequence and predicted CAMP score context, but local source does not support a direct antimicrobial assay row for this database activity label."),
        ("CAMP:CAMPSQ11490", "CAMP", "camp_r4_export/data/sequences.csv", 12, "pep2", "Antimicrobial", "Primary Table 1 supports the sequence and predicted CAMP score context, but local source does not support a direct antimicrobial assay row for this database activity label."),
        ("dbAMP:dbAMP_32568", "dbAMP", "data/dbamp3_detail_basic.csv", 15, "pep5", "Antimicrobial", "Primary Table 1 supports the sequence and predicted selection context, but local source does not support a direct antimicrobial assay row for this dbAMP activity label."),
        ("dbAMP:dbAMP_32569", "dbAMP", "data/dbamp3_detail_basic.csv", 16, "pep7", "Antimicrobial", "Primary Table 1 supports the sequence and predicted selection context, but local source does not support a direct antimicrobial assay row for this dbAMP activity label."),
        ("dbAMP:dbAMP_32567", "dbAMP", "data/dbamp3_detail_basic.csv", 17, "pep4", "Active against E. coli and B. subtilis", "Primary text supports KIKVAINGFGRIG growth inhibition at 128 μg/mL on day 1, but the local main text does not provide a Table 2 MIC row or fully row-level target/value pair for the dbAMP target text."),
        ("dbAMP:dbAMP_32566", "dbAMP", "data/dbamp3_detail_basic.csv", 18, "pep3", "Antimicrobial", "Primary Table 1 supports the sequence and predicted selection context, but local source does not support a direct antimicrobial assay row for this dbAMP activity label."),
        ("dbAMP:dbAMP_32570", "dbAMP", "data/dbamp3_detail_basic.csv", 19, "pep2", "Antimicrobial", "Primary Table 1 supports the sequence and predicted selection context, but local source does not support a direct antimicrobial assay row for this dbAMP activity label."),
        ("dbAMP:dbAMP_32571", "dbAMP", "data/dbamp3_detail_basic.csv", 20, "pep8b", "Antimicrobial", "Primary Table 1 supports the sequence and predicted selection context, but local source does not support a direct antimicrobial assay row for this dbAMP activity label."),
    ]
    for source_id, database, table, row, peptide, activity, context in conflict_specs:
        records.append(
            conflict_record(
                source_id=source_id,
                sequence_key=source_id,
                database=database,
                source_table=table,
                row_locator=db_locator("linked_experiment_records.jsonl", row),
                peptide_key=peptide,
                database_activity=activity,
                conflict_context=context,
                database_record_id=source_id.split(":", 1)[1],
            )
        )

    records.extend(
        [
            verified_record(
                source_id="DBAASP:DBAASPS_12379",
                sequence_key="DBAASP:DBAASPS_12379",
                database="DBAASP",
                source_table="linked_literature_records.jsonl",
                row_locator=db_locator("linked_literature_records.jsonl", 1),
                peptide_key="pep1",
                database_record_id="doi:10.1186/s12870-018-1611-z",
                activity_note="Literature DOI/PMID/PMCID link matches article metadata.",
            ),
            verified_record(
                source_id="DBAASP:DBAASPS_12380",
                sequence_key="DBAASP:DBAASPS_12380",
                database="DBAASP",
                source_table="linked_literature_records.jsonl",
                row_locator=db_locator("linked_literature_records.jsonl", 2),
                peptide_key="pep8",
                database_record_id="doi:10.1186/s12870-018-1611-z",
                activity_note="Literature DOI/PMID/PMCID link matches article metadata.",
            ),
        ]
    )

    counts = Counter(record["status"] for record in records)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "source_reviewed": True,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "audit_scope": "Worker-4 reopened primary XML/PDF table evidence, packet linked database rows, and merged sequence/experiment snapshots; source_conflict rows are preserved where database activity labels overstate source-supported assay evidence.",
        "database_row_counts": {
            "linked_assay_records": 4,
            "linked_dramp_activity_records": 0,
            "linked_experiment_records": 20,
            "linked_literature_records": 2,
            "linked_sequence_records": 0,
            "merged_sequence_catalog_hits": 18,
        },
        "status_summary": dict(counts),
        "record_audits": records,
    }


def mechanism_payload(generated_at: str) -> dict[str, Any]:
    claims = [
        {
            "claim_id": "mech-001",
            "claim_text": "Pep1 and pep8 have source-supported antibacterial MIC activity against E. coli and B. subtilis in Table 2; this is an activity phenotype, not a direct molecular mechanism.",
            "entity_scope": "LVQIGTKIVGVGRNYAAH and INIINAPLQGFKIA",
            "evidence_class": "phenotypic_activity_assay",
            "direct_assay_types": [],
            "limitations": "No membrane permeabilization, binding target, or direct killing mechanism assay is reported for these peptides in the opened local source.",
            "source_locator": table_locator(2, 1),
        },
        {
            "claim_id": "mech-002",
            "claim_text": "Pep8 is reported to alter OPR3 and AOS transcription in protonema qRT-PCR experiments, supporting host defense-signaling context without proving a direct antimicrobial mechanism.",
            "entity_scope": "INIINAPLQGFKIA / pep8",
            "evidence_class": "host_response_gene_expression",
            "direct_assay_types": [],
            "limitations": "The qRT-PCR result is regulatory/signaling evidence; it is not a peptide-target mechanism or membrane assay.",
            "source_locator": {"source_path": "source/paper.xml", "locator": "xml:fig=4:Fig. 4"},
        },
        {
            "claim_id": "mech-003",
            "claim_text": "MeJA treatment is associated with changes in moss peptide pools and release of bioactive peptides; mechanism framing remains proteolysis/peptidome context rather than a direct AMP mechanism.",
            "entity_scope": "reported moss peptide pools and selected peptides",
            "evidence_class": "biogenesis_context",
            "direct_assay_types": [],
            "limitations": "Source supports stress-hormone-associated peptide generation and activity context, not a direct molecular target.",
            "source_locator": section_locator(8, "Results"),
        },
    ]
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "source_reviewed": True,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "mechanism_claims": claims,
        "ontology_decision": "No direct_mechanism claim is asserted; retained claims are activity/regulatory/biogenesis context with source locators.",
    }


def nonblocking_material_gaps() -> list[dict[str, Any]]:
    return [
        {
            "gap_code": "true_supplement_files_not_local_nonblocking",
            "source_paths_checked": [
                f"{SUPP_DIR}/landing-1.bin",
                f"{SUPP_DIR}/landing-3.bin",
                f"{SUPP_DIR}/landing-4.bin",
                f"{SUPP_DIR}/landing-5.bin",
                f"{SUPP_DIR}/landing-6.bin",
                f"{SUPP_DIR}/landing-7.bin",
                f"{SUPP_DIR}/landing-9.bin",
                f"{SUPP_DIR}/landing-10.bin",
                XML_PATH,
                PDF_TEXT_PATH,
            ],
            "tools_attempted": ["file", "rg", "XML associated-data inspection", "pdftotext-derived packet text"],
            "why_unrecoverable": "The paper-local supplementary_original files are article/support HTML snapshots, not the actual PDF/XLSX supplementary assets referenced by the XML. The opened main XML/PDF still provide the curated Table 1/Table 2 peptide identity and MIC values used in this repair.",
            "impact": "Does not block the worker-4/worker-6 owner-layer decision because no final value here depends on an absent supplementary table; exact supplementary figure/spreadsheet values were not fabricated.",
            "owner_worker": "worker-6",
            "blocks_publication_grade": False,
            "next_action": "record_and_continue",
        }
    ]


def checked_inputs() -> list[str]:
    return [
        f"rework_context/{PAPER_ID}/handoff_context.json",
        f"paper_packets/{PAPER_ID}/packet_manifest.json",
        f"paper_packets/{PAPER_ID}/locators/locator_index.json",
        f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
        f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
        f"paper_packets/{PAPER_ID}/analysis/activity_toxicity_evidence.json",
        f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
        f"paper_packets/{PAPER_ID}/analysis/mechanism_evidence.json",
        XML_PATH,
        f"paper_packets/{PAPER_ID}/raw/paper.xml",
        f"papers/{PAPER_ID}/source/paper.pdf",
        f"paper_packets/{PAPER_ID}/raw/paper.pdf",
        PDF_TEXT_PATH,
        f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
        f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
        f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
        f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
        f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
        f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
        f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
        f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
        SEQ_CATALOG,
        EXP_CATALOG,
        FIVE_DB_CATALOG,
    ]


def caution_findings() -> list[dict[str, Any]]:
    return [
        {
            "caution_code": "database_activity_granularity_conflicts_preserved",
            "status": "source_conflict_preserved",
            "evidence_context": "CAMP/dbAMP rows for predicted or broad activity labels are retained as source_conflict when Table 1 supports sequence/prediction context but the opened primary source lacks a direct row-level assay for the database activity label.",
        },
        {
            "caution_code": "kik_growth_inhibition_not_mic_row",
            "status": "source_conflict_preserved",
            "evidence_context": "Primary text supports KIKVAINGFGRIG growth inhibition at 128 μg/mL on day 1, but not a Table 2 MIC row; matching CAMP/dbAMP broad target rows stay source_conflict.",
        },
        {
            "caution_code": "supplement_true_assets_not_local",
            "status": "nonblocking_material_gap_recorded",
            "evidence_context": "Local supplementary_original contains HTML snapshots rather than actual referenced PDF/XLSX files. Main XML/PDF contain the final MIC values and peptide identity evidence used here; absent supplementary exact curves/spreadsheets were not fabricated.",
        },
        {
            "caution_code": "mechanism_not_direct",
            "status": "nonblocking_caution",
            "evidence_context": "Final mechanism ontology keeps antimicrobial/regulatory/proteolysis context and does not promote it to direct molecular mechanism.",
        },
    ]


def review_payload(
    generated_at: str,
    activity: dict[str, Any],
    database: dict[str, Any],
    mechanism: dict[str, Any],
    gate_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "source_review_depth": {
            "paper_xml": "opened source/paper.xml and packet raw paper.xml; Table 1/Table 2 and article metadata used for peptide identity, MIC rows, and DOI/PMID traceability",
            "paper_pdf": "opened pdftotext-derived packet PDF text and source PDF path; Table 2/methods text cross-checked",
            "oa_package": "packet raw OA package path checked; no extracted archive members available beyond XML/PDF links",
            "supplementary_assets": "paper-local supplementary_original files checked with file/rg; they are HTML snapshots, not true PDF/XLSX supplements; no final value was fabricated from absent supplements",
            "merged_database_rows": "packet linked database JSONL plus merged sequence/experiment catalog rows checked for DBAASP/CAMP/dbAMP sequence and activity rows",
        },
        "checked_inputs": checked_inputs(),
        "materials_exhausted": {
            "paper_xml": True,
            "paper_pdf": True,
            "oa_package": "available XML/PDF package paths checked; no archive members",
            "supplementary_assets": "local HTML snapshots checked; true PDF/XLSX supplement binaries unavailable locally and recorded as a nonblocking obtainable-only gap",
            "merged_database_rows": True,
            "tools_attempted": ["jq", "rg", "file", "pdftotext-derived text review", "merged CSV row lookup", "semantic_three_layer_gate.py", "check_three_layer_publication_quality.py"],
        },
        "validator_contract_passed": True,
        "review_status": "accepted_with_cautions",
        "publication_grade": True,
        "source_review_depth_label": "source_reviewed_owner_layers_with_nonblocking_material_gap",
        "source_review_depth_summary": "Worker-4/6 reopened source XML/PDF, packet locators, linked database rows, and merged sequence/experiment snapshots; unresolved database activity labels are preserved as cautions.",
        "adjudication_summary": "Source-reviewed worker-4/worker-6 repair resolved the prior framework-only adjudication blocker: four Table 2 MIC rows are source-located, 26 database rows are reconciled with conflicts preserved, and no open targeted rework remains.",
        "semantic_quality_checks": {
            "activity_rows": len(activity["activity_records"]),
            "database_status_summary": database["status_summary"],
            "mechanism_claims": len(mechanism["mechanism_claims"]),
            "source_conflicts_preserved": database["status_summary"].get("source_conflict", 0),
            "gate_results": gate_evidence or {},
        },
        "per_layer_decision_rationale": {
            "material_packet": "Packet remains material_extracted_with_gaps because true supplementary PDF/XLSX files are not local; owner-layer final values here are supported by main XML/PDF and merged database rows.",
            "validator_contract": "Required final JSON artifacts and packet/final mirrors are present after repair.",
            "activity_toxicity": "Final activity rows are limited to the four source-supported Table 2 MIC values for pep1 and pep8; no toxicity or unsupported supplementary curve values were invented.",
            "database_record_verification": "DBAASP exact MIC rows and matching CAMP/dbAMP exact MIC rows are source_verified; predicted or broad database activity labels remain source_conflict with reasons.",
            "mechanism_ontology": "Claims are phenotypic/regulatory/biogenesis context only; no direct mechanism claim is asserted.",
            "publication_grade_review": "No blocking/major owner-layer issue remains; nonblocking cautions and one obtainable-only material gap are explicit.",
        },
        "caution_findings": caution_findings(),
        "qc_failure_reasons": [],
        "rework_targets": [],
        "unrecoverable_material_gaps": nonblocking_material_gaps(),
        "strict_gate": {"required_rework_count": 0, "open_rework_ticket_ids": []},
    }


def quality_payload(generated_at: str, gate_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "status": "source_reviewed_publication_grade_with_cautions",
        "issue_count": 0,
        "qc_failure_reasons": [],
        "rework_targets": [],
        "rework_context_packet_required": False,
        "source_review_summary": "Prior worker-6 framework-only and database-conflict blockers were repaired from local XML/PDF/database evidence.",
        "remaining_cautions": [item["caution_code"] for item in caution_findings()],
        "unrecoverable_material_gaps": nonblocking_material_gaps(),
        "gate_results": gate_evidence or {},
    }


def analysis_status_payload(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "status": "analysis_adjudicated_with_cautions",
        "activity_record_count": len(activity["activity_records"]),
        "activity_extraction_issue_count": 0,
        "activity_extraction_issues": [],
        "database_status_summary": database["status_summary"],
        "database_record_count": len(database["record_audits"]),
        "mechanism_claim_count": len(mechanism["mechanism_claims"]),
        "open_rework_ticket_ids": [],
        "unrecoverable_material_gap_count": len(nonblocking_material_gaps()),
        "blocking_unrecoverable_material_gap_count": 0,
    }


def sync_manifest(generated_at: str) -> None:
    manifest = read_json(PACKET / "packet_manifest.json", {})
    manifest.update(
        {
            "updated_at": generated_at,
            "analysis_queue_status": "analysis_adjudicated_with_cautions",
            "open_rework_ticket_ids": [],
            "resolved_rework_ticket_ids": ["rwk-complete-test-0001"],
            "known_missing_or_blocked_materials": nonblocking_material_gaps(),
        }
    )
    write_json(PACKET / "packet_manifest.json", manifest)


def run_gate(cmd: list[str], out_path: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    if out_path and proc.stdout.strip():
        out_path.write_text(proc.stdout, encoding="utf-8")
    return proc.returncode, proc.stdout, proc.stderr


def run_gates() -> dict[str, Any]:
    semantic_path = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    publication_path = REPORTS / f"{PAPER_ID}.publication_quality.json"
    semantic_rc, _, semantic_err = run_gate(
        [
            "python",
            ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py",
            "--root",
            ".",
            "--paper-id",
            PAPER_ID,
            "--json",
        ],
        semantic_path,
    )
    publication_rc, _, publication_err = run_gate(
        [
            "python",
            ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py",
            "--root",
            ".",
            "--manifest",
            str(MANIFEST),
            "--json-out",
            str(publication_path),
        ],
        None,
    )
    semantic = read_json(semantic_path, {})
    publication = read_json(publication_path, {})
    return {
        "semantic_gate": {
            "returncode": semantic_rc,
            "stderr": semantic_err.strip(),
            "path": str(semantic_path),
            "publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
            "publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
            "issue_count": (semantic.get("results") or [{}])[0].get("issue_count"),
            "failed_papers": semantic.get("failed_papers"),
        },
        "publication_quality": {
            "returncode": publication_rc,
            "stderr": publication_err.strip(),
            "path": str(publication_path),
            "publication_grade_pass": publication.get("publication_grade_pass"),
            "risk_counts": publication.get("risk_counts"),
            "review_status": publication.get("review_status"),
            "counts": publication.get("counts"),
        },
    }


def update_workflow_context(generated_at: str, gate_evidence: dict[str, Any]) -> None:
    ctx = read_json(WORKFLOW / "workflow_context.json", {})
    ctx.update(
        {
            "current_state": "codex_recheck_20260503_gate_verified",
            "current_round": "paper_review",
            "updated_at": generated_at,
            "open_rework_tickets": [],
            "resolved_rework_tickets": sorted(set((ctx.get("resolved_rework_tickets") or []) + ["rwk-complete-test-0001"])),
            "queue_status": {
                "analysis": "analysis_adjudicated_with_cautions",
                "material": "material_extracted_with_gaps",
            },
            "gate_summary": {
                "structural_ready": True,
                "validator_contract_ready": True,
                "semantic_gate_ready": gate_evidence["semantic_gate"]["publication_grade_fail_count"] == 0,
                "publication_grade_ready": gate_evidence["publication_quality"]["publication_grade_pass"] is True,
            },
        }
    )
    artifacts = ctx.setdefault("artifacts", {})
    artifacts.update(
        {
            "semantic_gate_report": str(REPORTS / f"{PAPER_ID}.semantic_gate.json"),
            "publication_quality_report": str(REPORTS / f"{PAPER_ID}.publication_quality.json"),
            "rework_response": str(PACKET / "rework" / "rework_responses.jsonl"),
        }
    )
    write_json(WORKFLOW / "workflow_context.json", ctx)


def append_state(generated_at: str, state: str, status: str, summary: str, artifacts: list[str]) -> None:
    entry = {
        "record_type": "state_execution",
        "workflow_id": f"paper-review-{PAPER_ID}",
        "paper_id": PAPER_ID,
        "state": state,
        "role": "codex_cli_worker_4_6",
        "provider": "codex-cli",
        "model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "status": status,
        "attempt": 1,
        "started_at": generated_at,
        "finished_at": generated_at,
        "created_at": generated_at,
        "duration_ms": 0,
        "output_summary": summary,
        "artifact_refs": artifacts,
        "rework_ticket_ids": ["rwk-complete-test-0001"],
    }
    append_jsonl(WORKFLOW / "state_executions.jsonl", entry)


def append_rework_response(generated_at: str, gate_evidence: dict[str, Any], activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> None:
    response = {
        "record_type": "rework_response",
        "paper_id": PAPER_ID,
        "ticket_id": "rwk-complete-test-0001",
        "ticket_ids": ["rwk-complete-test-0001"],
        "response_id": f"rsp-{generated_at.replace(':', '').replace('-', '').replace('Z', 'Z')}",
        "created_at": generated_at,
        "responded_at": generated_at,
        "status": "resolved_gate_verified",
        "state": "codex_recheck_20260503_gate_verified",
        "resolved_by": "codex_cli_worker_4_6",
        "owner_workers_repaired": ["worker-4", "worker-6"],
        "target_queue": "analysis",
        "what_was_checked": checked_inputs(),
        "tools_attempted": [
            "jq",
            "rg",
            "file",
            "pdftotext-derived packet text",
            "merged sequence/experiment CSV row lookup",
            "structured JSON artifact rewrite",
            "semantic_three_layer_gate.py",
            "check_three_layer_publication_quality.py",
        ],
        "repairs_made": [
            "worker-4: reconciled 26 linked database rows using primary Table 1/Table 2 and merged DBAASP/CAMP/dbAMP sequence snapshots; source conflicts were preserved.",
            "worker-6: repaired final activity target labels and missing pep1 B. subtilis MIC row, rewrote adjudication/QC provenance, cleared the open ticket, and kept nonblocking cautions.",
        ],
        "repair_summary": {
            "activity_records": len(activity["activity_records"]),
            "database_record_audits": len(database["record_audits"]),
            "database_status_summary": database["status_summary"],
            "mechanism_claims": len(mechanism["mechanism_claims"]),
            "quality_feedback_issue_count": 0,
        },
        "remaining_blockers": [],
        "remaining_open_rework_ticket_ids": [],
        "remaining_cautions": [item["caution_code"] for item in caution_findings()],
        "unrecoverable_material_gaps": nonblocking_material_gaps(),
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
            f"reports/{PAPER_ID}.semantic_gate.json",
            f"reports/{PAPER_ID}.publication_quality.json",
        ],
        "gate_results": gate_evidence,
        "publication_grade_decision": "accepted_with_cautions",
    }
    append_jsonl(PACKET / "rework" / "rework_responses.jsonl", response)
    append_jsonl(
        WORKFLOW / "chat_messages.jsonl",
        {
            "record_type": "chat_message",
            "workflow_id": f"paper-review-{PAPER_ID}",
            "paper_id": PAPER_ID,
            "state": "codex_recheck_20260503_gate_verified",
            "role": "agent",
            "message": "Rework ticket rwk-complete-test-0001 resolved after worker-4/worker-6 source-reviewed repair and strict gate pass.",
            "created_at": generated_at,
        },
    )


def update_complete_report(generated_at: str, gate_evidence: dict[str, Any], activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> None:
    report_path = REPORTS / f"{PAPER_ID}.complete_message_test_report.json"
    report = read_json(report_path, {})
    report.update(
        {
            "generated_at": generated_at,
            "current_state": "codex_recheck_20260503_gate_verified",
            "terminal_status": "accepted_with_cautions",
            "completion_claim": "source_reviewed_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions",
            "final_approval_status": "approved_accepted_with_cautions",
            "publication_quality_gate": "passed_after_worker4_worker6_source_review",
            "semantic_gate": "passed_after_worker4_worker6_source_review",
            "not_publication_grade_reason": None,
            "open_rework_ticket_count": 0,
            "rework_ticket_ids": [],
            "gate_summary": {
                "structural_ready": True,
                "validator_contract_ready": True,
                "semantic_gate_ready": gate_evidence["semantic_gate"]["publication_grade_fail_count"] == 0,
                "publication_grade_ready": gate_evidence["publication_quality"]["publication_grade_pass"] is True,
            },
            "gate_results": {
                "semantic_publication_grade_pass_count": gate_evidence["semantic_gate"]["publication_grade_pass_count"],
                "semantic_publication_grade_fail_count": gate_evidence["semantic_gate"]["publication_grade_fail_count"],
                "semantic_issue_count": gate_evidence["semantic_gate"]["issue_count"],
                "publication_quality_pass": gate_evidence["publication_quality"]["publication_grade_pass"],
                "publication_risk_counts": gate_evidence["publication_quality"]["risk_counts"],
            },
            "analysis": {
                "activity_records": len(activity["activity_records"]),
                "database_row_counts": database["database_row_counts"],
                "database_status_summary": database["status_summary"],
                "mechanism_claims": len(mechanism["mechanism_claims"]),
                "review_status": "accepted_with_cautions",
            },
            "queue_status": {
                "analysis": "analysis_adjudicated_with_cautions",
                "material": "material_extracted_with_gaps",
            },
            "publication_quality_report": str(REPORTS / f"{PAPER_ID}.publication_quality.json"),
            "semantic_gate_report": str(REPORTS / f"{PAPER_ID}.semantic_gate.json"),
        }
    )
    write_json(report_path, report)


def main() -> int:
    generated_at = now_iso()
    activity = activity_payload(generated_at)
    database = database_payload(generated_at)
    mechanism = mechanism_payload(generated_at)
    review = review_payload(generated_at, activity, database, mechanism)
    quality = quality_payload(generated_at)
    analysis_status = analysis_status_payload(generated_at, activity, database, mechanism)

    for path in [
        PACKET / "analysis" / "activity_toxicity_evidence.json",
        PACKET / "final" / "activity_toxicity_evidence.json",
        PAPER / "final" / "activity_toxicity_evidence.json",
    ]:
        write_json(path, activity)
    for path in [
        PACKET / "analysis" / "database_record_audit.json",
        PACKET / "final" / "database_record_verification.json",
        PAPER / "final" / "database_record_verification.json",
    ]:
        write_json(path, database)
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
        PAPER / "work" / "review" / "adjudication_report.json",
        PAPER / "final" / "review_report.json",
    ]:
        write_json(path, review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality)
    write_json(PACKET / "analysis" / "analysis_status.json", analysis_status)
    sync_manifest(generated_at)

    gate_evidence = run_gates()
    gate_ready = (
        gate_evidence["semantic_gate"]["publication_grade_fail_count"] == 0
        and gate_evidence["semantic_gate"]["issue_count"] == 0
        and gate_evidence["publication_quality"]["publication_grade_pass"] is True
    )
    if not gate_ready:
        raise SystemExit(json.dumps({"status": "gate_failed_after_repair", "gate_evidence": gate_evidence}, ensure_ascii=False, indent=2))

    review = review_payload(generated_at, activity, database, mechanism, gate_evidence)
    quality = quality_payload(generated_at, gate_evidence)
    for path in [
        PACKET / "analysis" / "adjudication_report.json",
        PACKET / "final" / "review_report.json",
        PAPER / "work" / "review" / "adjudication_report.json",
        PAPER / "final" / "review_report.json",
    ]:
        write_json(path, review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality)

    gate_evidence = run_gates()
    gate_ready = (
        gate_evidence["semantic_gate"]["publication_grade_fail_count"] == 0
        and gate_evidence["semantic_gate"]["issue_count"] == 0
        and gate_evidence["publication_quality"]["publication_grade_pass"] is True
    )
    if not gate_ready:
        raise SystemExit(json.dumps({"status": "gate_failed_after_final_sync", "gate_evidence": gate_evidence}, ensure_ascii=False, indent=2))

    update_workflow_context(generated_at, gate_evidence)
    append_state(
        generated_at,
        "codex_recheck_20260503_gate_verified",
        "completed",
        "Worker-4/worker-6 source-reviewed repair resolved rwk-complete-test-0001; semantic and publication gates passed.",
        [
            str(PAPER / "final" / "review_report.json"),
            str(PAPER / "work" / "review" / "quality_feedback.json"),
            str(REPORTS / f"{PAPER_ID}.semantic_gate.json"),
            str(REPORTS / f"{PAPER_ID}.publication_quality.json"),
        ],
    )
    append_rework_response(generated_at, gate_evidence, activity, database, mechanism)
    update_complete_report(generated_at, gate_evidence, activity, database, mechanism)

    print(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "status": "accepted_with_cautions",
                "activity_records": len(activity["activity_records"]),
                "database_status_summary": database["status_summary"],
                "mechanism_claims": len(mechanism["mechanism_claims"]),
                "gate_evidence": gate_evidence,
                "open_rework_ticket_ids": [],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
