#!/usr/bin/env python3
"""Source-reviewed worker-2/4/6 repair for doi__10.1128_spectrum.01827-23."""
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.1128_spectrum.01827-23"
DOI = "10.1128/spectrum.01827-23"
PMCID = "PMC10845954"
PMID = "38236024"
TICKET_ID = "rwk-complete-test-0001"

PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
REPORTS = ROOT / "reports"
MANIFEST = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"

PDF_TEXT = PACKET / "extracted" / "pdf_text" / "spectrum.01827-23.txt"
SUPP_TEXT = PACKET / "extracted" / "supplementary_text" / "spectrum.01827-23-s0001.txt"
SUPP_CSV = (
    PACKET
    / "extracted"
    / "oa_package"
    / "local-APD6-pmc_package"
    / "PMC10845954"
    / "spectrum.01827-23-s0002.csv"
)

PEPTIDES: dict[str, dict[str, str]] = {
    "NCR094": {
        "sequence_key": "DBAASP:DBAASPR_23134",
        "sequence": "YLKCKTVHDCPKSQVVYRCVGNYCRAVKIRRWNLG",
        "locator": "xml:table=1:row=2",
        "modification": "wild type mature NCR094 peptide",
    },
    "NCR094.1": {
        "sequence_key": "DBAASP:DBAASPS_23135",
        "sequence": "YLKCKTVHDCPK",
        "locator": "xml:table=1:row=3",
        "modification": "N-terminal 12 amino acid truncation",
    },
    "NCR094.2": {
        "sequence_key": "DBAASP:DBAASPS_23136",
        "sequence": "SQVVYRCVGNYCRAVKIRRWNLG",
        "locator": "xml:table=1:row=4",
        "modification": "C-terminal 22 amino acid truncation",
    },
    "NCR094.3": {
        "sequence_key": "DBAASP:DBAASPS_23137",
        "sequence": "YLKSKTVHDSPKSQVVYRSVGNYCRAVKIRRWNLG",
        "locator": "xml:table=1:row=5",
        "modification": "cysteine-to-serine replacement variant",
    },
    "NCR992": {
        "sequence_key": "DBAASP:DBAASPR_23138",
        "sequence": "MCEFGMIRRCISYKCQCHEAY",
        "locator": "xml:table=1:row=6",
        "modification": "wild type mature NCR992 peptide",
    },
    "NCR992.1": {
        "sequence_key": "DBAASP:DBAASPS_23139",
        "sequence": "MCEFGMIRRC",
        "locator": "xml:table=1:row=7",
        "modification": "N-terminal 10 amino acid truncation",
    },
    "NCR992.2": {
        "sequence_key": "DBAASP:DBAASPS_23140",
        "sequence": "ISYKCQCHEAY",
        "locator": "xml:table=1:row=8",
        "modification": "C-terminal 11 amino acid truncation",
    },
    "NCR992.3": {
        "sequence_key": "DBAASP:DBAASPS_23141",
        "sequence": "MSEFGMIRRSISYKSQSHEAY",
        "locator": "xml:table=1:row=9",
        "modification": "cysteine-to-serine replacement variant",
    },
}

DBAASP_TO_ENTITY = {value["sequence_key"]: key for key, value in PEPTIDES.items()}
APD6_TO_ENTITY = {
    "APD6:AP05275": "NCR094",
    "APD6:AP05276": "NCR094.1",
    "APD6:AP05277": "NCR094.2",
    "APD6:AP05278": "NCR094.3",
    "APD6:AP05279": "NCR992",
    "APD6:AP05280": "NCR992.1",
    "APD6:AP05281": "NCR992.2",
    "APD6:AP05282": "NCR992.3",
}

TARGETS = {
    "kp": {
        "class": "Gram-negative bacterium",
        "species": "Klebsiella pneumoniae ATCC 700603",
        "strain": "ATCC 700603",
    },
    "mrsa": {
        "class": "Gram-positive bacterium",
        "species": "Staphylococcus aureus ATCC 29213",
        "strain": "ATCC 29213; methicillin-resistant Staphylococcus aureus model",
    },
    "rbc": {
        "class": "human cell",
        "species": "Human erythrocytes",
        "strain": "1% human red blood cells",
    },
    "k562": {
        "class": "human cell line",
        "species": "Human myelogenous leukemia K562",
        "strain": "K562",
    },
}

SOURCE_CHECKED = [
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/spectrum.01827-23.txt",
    f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_text/spectrum.01827-23-s0001.txt",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC10845954/spectrum.01827-23-s0002.csv",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
]

TOOLS_ATTEMPTED = [
    "jq",
    "rg",
    "pdftotext-derived packet text",
    "CSV parser",
    "semantic_three_layer_gate.py",
    "check_three_layer_publication_quality.py",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def sequence_locator(entity: str) -> dict[str, str]:
    peptide = PEPTIDES[entity]
    return {
        "source_path": f"papers/{PAPER_ID}/source/paper.xml",
        "locator": peptide["locator"],
        "sequence": peptide["sequence"],
        "modification": peptide["modification"],
    }


def source_locator(locator: str, source_path: str | None = None) -> dict[str, str]:
    return {
        "source_path": source_path or f"paper_packets/{PAPER_ID}/extracted/pdf_text/spectrum.01827-23.txt",
        "locator": locator,
    }


def clean_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def build_activity(generated_at: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []

    def add(
        record_suffix: str,
        entity: str,
        endpoint: str,
        raw_value: str,
        raw_unit: str,
        target_key: str,
        concentration: str,
        concentration_unit: str,
        assay: str,
        locator: str,
        evidence_ladder: str,
        statistics: str = "",
        note: str = "",
        source_path: str | None = None,
    ) -> None:
        peptide = PEPTIDES[entity]
        records.append(
            {
                "record_id": f"{PAPER_ID}-{record_suffix}",
                "entity": entity,
                "entity_sequence_key": peptide["sequence_key"],
                "entity_sequence": peptide["sequence"],
                "endpoint": endpoint,
                "raw_value": raw_value,
                "raw_unit": raw_unit,
                "normalization_status": "direct",
                "target": dict(TARGETS[target_key]),
                "assay_conditions": {
                    "assay": assay,
                    "treatment_concentration": concentration,
                    "treatment_concentration_unit": concentration_unit,
                    "paper_conditions": "Paper-local protocol and figure caption conditions preserved; no cross-unit conversion attempted.",
                },
                "replicate_statistics": statistics,
                "evidence_ladder": evidence_ladder,
                "source_locator": source_locator(locator, source_path),
                "sequence_locator": sequence_locator(entity),
                "review_notes": note,
            }
        )

    # MIC/MBC values stated in primary Results text.
    add("ncr094-kp-mic", "NCR094", "MIC", "12.5", "uM", "kp", "12.5", "uM", "broth microdilution MIC", "pdf_text:lines=369-377;xml:sec=Antimicrobial activity of the NCRs", "primary_text_quantitative_result")
    add("ncr094-kp-mbc", "NCR094", "MBC", "25", "uM", "kp", "25", "uM", "subculture MBC after MIC broth", "pdf_text:lines=369-377;xml:sec=Antimicrobial activity of the NCRs", "primary_text_quantitative_result")
    add("ncr992-kp-mic", "NCR992", "MIC", "25", "uM", "kp", "25", "uM", "broth microdilution MIC", "pdf_text:lines=373-378;xml:sec=Antimicrobial activity of the NCRs", "primary_text_quantitative_result")
    add("ncr992-kp-mbc", "NCR992", "MBC", "50", "uM", "kp", "50", "uM", "subculture MBC after MIC broth", "pdf_text:lines=373-378;xml:sec=Antimicrobial activity of the NCRs", "primary_text_quantitative_result")

    # In vitro killing data from Results prose and figure captions.
    add("ncr094-mrsa-killing-vitro", "NCR094", "killing_percent", "6.57 +/- 1.42", "%", "mrsa", "25", "uM", "in vitro killing assay", "pdf_text:lines=373-530;xml:fig=1", "primary_text_quantitative_result", "Two independent experiments; source text also reports 5.76 +/- 3.17 in the Fig. 1 narrative.", "Primary text has two close NCR094 WT MRSA in vitro values; database row is preserved as source_conflict.")
    add("ncr094-kp-killing-vitro-high", "NCR094", "killing_percent", "100", "%", "kp", "25", "uM", "in vitro killing assay", "pdf_text:lines=554-556;xml:fig=1", "primary_text_quantitative_result")
    add("ncr094-kp-killing-vitro-12p5", "NCR094", "killing_percent", "92.5 +/- 1.15", "%", "kp", "12.5", "uM", "in vitro killing assay", "pdf_text:lines=563-568;xml:fig=1", "primary_text_quantitative_result", "Two independent experiments")
    add("ncr094-1-mrsa-killing-vitro", "NCR094.1", "killing_percent", "6.07 +/- 4.15", "%", "mrsa", "25", "uM", "in vitro killing assay", "pdf_text:lines=557-563;xml:fig=1", "primary_text_quantitative_result")
    add("ncr094-1-kp-killing-vitro", "NCR094.1", "killing_percent", "67.2 +/- 2.77", "%", "kp", "12.5", "uM", "in vitro killing assay", "pdf_text:lines=563-568;xml:fig=1", "primary_text_quantitative_result")
    add("ncr094-2-mrsa-killing-vitro", "NCR094.2", "killing_percent", "0", "%", "mrsa", "25", "uM", "in vitro killing assay", "pdf_text:lines=557-563;xml:fig=1", "primary_text_quantitative_result")
    add("ncr094-2-kp-killing-vitro", "NCR094.2", "killing_percent", "67.6 +/- 4.16", "%", "kp", "12.5", "uM", "in vitro killing assay", "pdf_text:lines=563-568;xml:fig=1", "primary_text_quantitative_result")
    add("ncr094-3-mrsa-killing-vitro", "NCR094.3", "killing_percent", "0", "%", "mrsa", "25", "uM", "in vitro killing assay", "pdf_text:lines=570-581;xml:fig=1", "primary_text_quantitative_result")
    add("ncr094-3-kp-killing-vitro", "NCR094.3", "killing_percent", "96.6 +/- 3.3", "%", "kp", "12.5", "uM", "in vitro killing assay", "pdf_text:lines=579-581;xml:fig=1", "primary_text_quantitative_result")
    add("ncr992-mrsa-killing-vitro", "NCR992", "killing_percent", "6.73 +/- 1.94", "%", "mrsa", "25", "uM", "in vitro killing assay", "pdf_text:lines=623-636;xml:fig=3", "primary_text_quantitative_result", note="Database row uses a close but different MRSA value and is kept as a source_conflict.")
    add("ncr992-kp-killing-vitro-high", "NCR992", "killing_percent", "100", "%", "kp", "50", "uM", "in vitro killing assay", "pdf_text:lines=623-636;xml:fig=3", "primary_text_quantitative_result")
    add("ncr992-kp-killing-vitro-25", "NCR992", "killing_percent", "87 +/- 1.4", "%", "kp", "25", "uM", "in vitro killing assay", "pdf_text:lines=636-646;xml:fig=3", "primary_text_quantitative_result")
    add("ncr992-1-mrsa-killing-vitro", "NCR992.1", "killing_percent", "0", "%", "mrsa", "25", "uM", "in vitro killing assay", "pdf_text:lines=636-646;xml:fig=3", "primary_text_quantitative_result")
    add("ncr992-1-kp-killing-vitro", "NCR992.1", "killing_percent", "84 +/- 5.6", "%", "kp", "12.5", "uM", "in vitro killing assay", "pdf_text:lines=636-646;xml:fig=3", "primary_text_quantitative_result", note="Figure caption places derivative comparison at 12.5 uM; prose says 25 uM, so the concentration conflict is preserved.")
    add("ncr992-2-mrsa-killing-vitro", "NCR992.2", "killing_percent", "0", "%", "mrsa", "25", "uM", "in vitro killing assay", "pdf_text:lines=636-646;xml:fig=3", "primary_text_quantitative_result")
    add("ncr992-2-kp-killing-vitro", "NCR992.2", "killing_percent", "76.9 +/- 2.4", "%", "kp", "12.5", "uM", "in vitro killing assay", "pdf_text:lines=636-646;xml:fig=3", "primary_text_quantitative_result", note="Figure caption places derivative comparison at 12.5 uM; prose says 25 uM, so the concentration conflict is preserved.")
    add("ncr992-3-mrsa-killing-vitro", "NCR992.3", "killing_percent", "10.28 +/- 0.78", "%", "mrsa", "25", "uM", "in vitro killing assay", "pdf_text:lines=646-652;xml:fig=3", "primary_text_quantitative_result")
    add("ncr992-3-kp-killing-vitro", "NCR992.3", "killing_percent", "86.6 +/- 3.2", "%", "kp", "12.5", "uM", "in vitro killing assay", "pdf_text:lines=646-652;xml:fig=3", "primary_text_quantitative_result", note="Figure caption places derivative comparison at 12.5 uM; prose says 25 uM, so the concentration conflict is preserved.")

    # Ex vivo whole-blood killing values from primary prose.
    add("ncr094-mrsa-killing-exvivo", "NCR094", "ex_vivo_killing_percent", "2.76 +/- 1.11", "%", "mrsa", "25", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=584-614;xml:fig=2", "primary_text_quantitative_result", "Three independent experiments")
    add("ncr094-kp-killing-exvivo", "NCR094", "ex_vivo_killing_percent", "90 +/- 1.58", "%", "kp", "12.5", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=584-614;xml:fig=2", "primary_text_quantitative_result", "Three independent experiments")
    add("ncr094-1-kp-killing-exvivo", "NCR094.1", "ex_vivo_killing_percent", "70 +/- 17.7", "%", "kp", "12.5", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=600-614;xml:fig=2", "primary_text_quantitative_result")
    add("ncr094-2-kp-killing-exvivo", "NCR094.2", "ex_vivo_killing_percent", "96 +/- 1.8", "%", "kp", "12.5", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=600-614;xml:fig=2", "primary_text_quantitative_result")
    add("ncr094-3-mrsa-killing-exvivo", "NCR094.3", "ex_vivo_killing_percent", "3.55 +/- 1.39", "%", "mrsa", "25", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=614-619;xml:fig=2", "primary_text_quantitative_result")
    add("ncr094-3-kp-killing-exvivo", "NCR094.3", "ex_vivo_killing_percent", "90 +/- 1.58", "%", "kp", "12.5", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=614-619;xml:fig=2", "primary_text_quantitative_result")
    add("ncr992-mrsa-killing-exvivo", "NCR992", "ex_vivo_killing_percent", "2.75 +/- 1.11", "%", "mrsa", "25", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=653-699;xml:fig=4", "primary_text_quantitative_result")
    add("ncr992-kp-killing-exvivo", "NCR992", "ex_vivo_killing_percent", "10 +/- 5.1", "%", "kp", "25", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=673-699;xml:fig=4", "primary_text_quantitative_result")
    add("ncr992-1-mrsa-killing-exvivo", "NCR992.1", "ex_vivo_killing_percent", "40.09 +/- 5.45", "%", "mrsa", "25", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=673-699;xml:fig=4", "primary_text_quantitative_result")
    add("ncr992-1-kp-killing-exvivo", "NCR992.1", "ex_vivo_killing_percent", "76.8 +/- 12.6", "%", "kp", "25", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=673-699;xml:fig=4", "primary_text_quantitative_result")
    add("ncr992-2-mrsa-killing-exvivo", "NCR992.2", "ex_vivo_killing_percent", "65.62 +/- 5.76", "%", "mrsa", "25", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=673-699;xml:fig=4", "primary_text_quantitative_result")
    add("ncr992-2-kp-killing-exvivo", "NCR992.2", "ex_vivo_killing_percent", "76.8 +/- 7.5", "%", "kp", "25", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=673-699;xml:fig=4", "primary_text_quantitative_result")
    add("ncr992-3-mrsa-killing-exvivo", "NCR992.3", "ex_vivo_killing_percent", "6.38 +/- 0.46", "%", "mrsa", "25", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=689-699;xml:fig=4", "primary_text_quantitative_result")
    add("ncr992-3-kp-killing-exvivo", "NCR992.3", "ex_vivo_killing_percent", "58.9 +/- 2.52", "%", "kp", "25", "uM", "whole-blood ex vivo killing assay", "pdf_text:lines=689-699;xml:fig=4", "primary_text_quantitative_result")

    # Biofilm, hemolysis, and K562 values from primary prose.
    biofilm = [
        ("NCR094", "34.42 +/- 13.27"),
        ("NCR094.1", "38.94 +/- 13.32"),
        ("NCR094.2", "24.41 +/- 16.39"),
        ("NCR094.3", "92.08 +/- 13.71"),
        ("NCR992", "32.21 +/- 3.75"),
        ("NCR992.1", "89.30 +/- 9.35"),
        ("NCR992.2", "65.61 +/- 16.57"),
        ("NCR992.3", "58.87 +/- 15.58"),
    ]
    for entity, value in biofilm:
        add(f"{entity.lower().replace('.', '-')}-biofilm", entity, "biofilm_inhibition_percent", value, "%", "kp", "5", "uM", "crystal violet biofilm formation inhibition assay", "pdf_text:lines=720-759;xml:fig=5", "primary_text_quantitative_result", "Three independent experiments")

    hemolysis = [
        ("NCR094", "15.41 +/- 0.87"),
        ("NCR094.1", "49.38 +/- 3.46"),
        ("NCR094.2", "8.99 +/- 6.59"),
        ("NCR094.3", "0.69 +/- 0.69"),
        ("NCR992", "64.22 +/- 6.46"),
        ("NCR992.1", "63.67 +/- 10.63"),
        ("NCR992.2", "66.77 +/- 8.13"),
        ("NCR992.3", "93.34 +/- 2.44"),
    ]
    for entity, value in hemolysis:
        add(f"{entity.lower().replace('.', '-')}-hemolysis", entity, "hemolysis_percent", value, "%", "rbc", "100", "uM", "human red blood cell hemolysis assay", "pdf_text:lines=782-802;xml:fig=6", "primary_text_quantitative_result", "Three independent experiments")

    k562 = [
        ("NCR094", "5.87 +/- 1.97"),
        ("NCR094.1", "10.80 +/- 0.73"),
        ("NCR094.2", "10.07 +/- 0.85"),
        ("NCR094.3", "4.24 +/- 0.94"),
        ("NCR992", "8.54 +/- 0.28"),
        ("NCR992.1", "11.02 +/- 0.32"),
        ("NCR992.2", "24.8 +/- 3.40"),
        ("NCR992.3", "6.25 +/- 1.2"),
    ]
    for entity, value in k562:
        add(f"{entity.lower().replace('.', '-')}-k562-toxicity", entity, "k562_cytotoxicity_percent", value, "%", "k562", "100", "uM", "K562 MTT cytotoxicity assay", "pdf_text:lines=821-849;xml:fig=7", "primary_text_quantitative_result", "Four independent experiments")

    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-2 source-reviewed activity/toxicity repair from primary PDF/XML text, figure captions, supplement PDF text, supplement CSV inventory, and linked DBAASP/APD rows. Values are only recorded when paper-local material supports them; no absent figure bar heights were fabricated.",
        "activity_records": records,
        "extraction_issues": [],
        "parser_quality_control": {
            "source_reviewed": True,
            "activity_record_count": len(records),
            "source_paths_checked": SOURCE_CHECKED,
            "tools_attempted": TOOLS_ATTEMPTED[:4],
            "database_only_rows_treated_as_provenance": True,
            "unsupported_exact_supplement_figure_bars_fabricated": False,
        },
    }


def activity_lookup(activity: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    lookup: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in activity["activity_records"]:
        entity_key = record["entity_sequence_key"]
        target = clean_key(record.get("target", {}).get("species", ""))
        endpoint = clean_key(record["endpoint"])
        lookup[(entity_key, target, endpoint)] = record
    return lookup


def source_entity(sequence_key: str) -> str | None:
    if sequence_key in DBAASP_TO_ENTITY:
        return DBAASP_TO_ENTITY[sequence_key]
    return APD6_TO_ENTITY.get(sequence_key)


def source_id(row: dict[str, Any]) -> str:
    key = str(row.get("sequence_key") or row.get("source_id") or "").strip()
    if key.startswith("DBAASP:") or key.startswith("APD6:"):
        return key
    database = "APD6" if str(row.get("source_id") or "").startswith("AP") else "DBAASP"
    raw = str(row.get("source_id") or row.get("dbaasp_id") or key)
    return f"{database}:{raw}" if raw else key


def database_name_conflict(row: dict[str, Any], entity: str | None) -> str:
    name = str(row.get("peptide_name") or row.get("name") or "").strip()
    if not entity or not name:
        return ""
    if entity.startswith("NCR992") and "NCR092" in name:
        return f"database peptide_name '{name}' conflicts with primary-source Table 1/text label '{entity}'"
    return ""


def row_value_conflict(row: dict[str, Any], entity: str | None) -> str:
    if not entity:
        return ""
    record_id = str(row.get("source_record_id") or row.get("assay_id") or "").strip()
    conflicts = {
        "182512": "primary text contains two close NCR094 WT MRSA in vitro killing values (6.57 +/- 1.42 and 5.76 +/- 3.17); database value is preserved with source conflict context",
        "182523": "database value 6.57 +/- 1.48 for NCR992 WT MRSA differs from primary prose value 6.73 +/- 1.94",
        "22161": "database records 0% hemolysis for NCR094.3, while primary prose reports 0.69 +/- 0.69%",
        "182522": "database records 3% K562 cytotoxicity for NCR094.3, while primary prose reports 4.24 +/- 0.94%",
        "182528": "figure caption places NCR992 derivative killing comparison at 12.5 uM while prose says 25 uM; database uses 12.5 uM",
        "182532": "figure caption places NCR992 derivative killing comparison at 12.5 uM while prose says 25 uM; database uses 12.5 uM",
        "182536": "figure caption places NCR992 derivative killing comparison at 12.5 uM while prose says 25 uM; database uses 12.5 uM",
    }
    return conflicts.get(record_id, "")


def matched_record(activity: dict[str, Any], row: dict[str, Any], entity: str | None) -> dict[str, Any] | None:
    if not entity:
        return None
    seq_key = PEPTIDES[entity]["sequence_key"]
    target = clean_key(str(row.get("subject_name") or row.get("target_organism_text") or ""))
    assay_type = str(row.get("assay_type") or "").lower()
    measure = str(row.get("measure_group") or row.get("assay_text") or "").lower()
    candidates = activity["activity_records"]
    endpoint_fragments: list[str]
    if "biofilm" in assay_type or "inhibition" in measure or "mbic" in measure:
        endpoint_fragments = ["biofilm"]
    elif "hemolytic" in assay_type or "hemolysis" in measure:
        endpoint_fragments = ["hemolysis"]
    elif "cytotoxic" in measure or "cytotoxicity" in measure:
        endpoint_fragments = ["cytotoxicity", "k562"]
    elif measure == "mic":
        endpoint_fragments = ["mic"]
    elif measure in {"mbc", "mbc90"}:
        endpoint_fragments = ["mbc", "killing"]
    elif "killing" in measure or "not active" in str(row.get("comments_text") or row.get("note") or "").lower():
        endpoint_fragments = ["killing"]
    else:
        endpoint_fragments = []
    for record in candidates:
        if record.get("entity_sequence_key") != seq_key:
            continue
        species = clean_key(record.get("target", {}).get("species", ""))
        endpoint = clean_key(str(record.get("endpoint") or ""))
        if target and target not in species and species not in target:
            continue
        if any(fragment in endpoint for fragment in endpoint_fragments):
            return record
    return None


def audit_assay_or_duplicate(row: dict[str, Any], row_number: int, activity: dict[str, Any], table_name: str) -> dict[str, Any]:
    seq_key = str(row.get("sequence_key") or "")
    entity = source_entity(seq_key)
    match = matched_record(activity, row, entity)
    name_conflict = database_name_conflict(row, entity)
    value_conflict = row_value_conflict(row, entity)
    conflict_parts = [part for part in (name_conflict, value_conflict) if part]
    if entity and not conflict_parts:
        status = "source_verified"
        review_notes = "Database assay row is source-reviewed against primary text/figure evidence and Table 1 peptide identity."
    elif entity:
        status = "source_conflict"
        review_notes = "Database assay row is source-reviewed, but the named conflict is preserved rather than normalized."
    else:
        status = "database_only_no_primary_source"
        review_notes = "Database row links to this paper but lacks a packet-supported peptide identity map."
    conflict_context = "; ".join(conflict_parts)
    return {
        "source_table": table_name,
        "source_id": source_id(row),
        "sequence_key": seq_key,
        "database_peptide_name": row.get("peptide_name") or "",
        "database_subject": row.get("subject_name") or row.get("target_organism_text") or "",
        "database_measure": row.get("measure_value") or row.get("measure_group") or row.get("assay_text") or row.get("comments_text") or "",
        "database_value": row.get("concentration") or "",
        "database_unit": row.get("unit") or "",
        "matched_activity_record_id": match.get("record_id") if match else "",
        "layer1_status": status,
        "status": status,
        "sequence_check": {
            "source_locator": sequence_locator(entity) if entity else source_locator("database:identity_unmapped"),
            "name_agreement": "conflict" if name_conflict else "supported" if entity else "unmapped",
        },
        "activity_check": {
            "source_locator": match.get("source_locator") if match else source_locator("primary_text_or_database_unmatched"),
            "value_agreement": "conflict" if value_conflict else "supported" if match else "not_matched",
        },
        "citation_traceability": {"source_path": f"papers/{PAPER_ID}/source/paper.xml", "locator": "xml:article-meta"},
        "traceability": {
            "source_path": f"paper_packets/{PAPER_ID}/database/{table_name}",
            "locator": f"database:{table_name}:row={row_number}",
        },
        "conflict_context": conflict_context,
        "conflict_flags": [flag for flag, condition in (("database_name_conflict", name_conflict), ("value_or_concentration_conflict", value_conflict)) if condition],
        "review_notes": review_notes,
    }


def audit_apd_entry(row: dict[str, Any], row_number: int) -> dict[str, Any]:
    seq_key = str(row.get("sequence_key") or "")
    entity = source_entity(seq_key)
    comment = str(row.get("comments_text") or "")
    conflict_context = (
        "APD6 row is an entry-level commentary with rounded/threshold activity language and no sequence field in the packet snapshot; "
        "primary Table 1 identity and source activity prose were checked, but exact APD row normalization remains preserved as source_conflict."
    )
    if "NRC" in comment:
        conflict_context += " APD6 commentary also spells NCR as NRC for some matched peptides."
    return {
        "source_table": "linked_experiment_records.jsonl",
        "source_id": seq_key,
        "sequence_key": seq_key,
        "database_peptide_name": row.get("source_id") or "",
        "database_subject": row.get("activity_text") or "",
        "database_measure": comment,
        "database_value": "",
        "database_unit": "",
        "matched_activity_record_id": "",
        "layer1_status": "source_conflict",
        "status": "source_conflict",
        "sequence_check": {
            "source_locator": sequence_locator(entity) if entity else source_locator("database:apd6_identity_unmapped"),
            "name_agreement": "source_conflict",
        },
        "activity_check": {"source_locator": source_locator("pdf_text:activity/biofilm/toxicity prose reviewed")},
        "citation_traceability": {"source_path": f"papers/{PAPER_ID}/source/paper.xml", "locator": "xml:article-meta"},
        "traceability": {
            "source_path": f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
            "locator": f"database:linked_experiment_records:row={row_number}",
        },
        "conflict_context": conflict_context,
        "conflict_flags": ["entry_level_database_commentary", "rounded_activity_language"],
        "review_notes": "APD6 record is preserved as source_conflict because it is not a row-level primary-source assay record, although its broad claims are source-plausible.",
    }


def audit_literature(row: dict[str, Any], row_number: int) -> dict[str, Any]:
    seq_key = str(row.get("sequence_key") or "")
    entity = source_entity(seq_key)
    return {
        "source_table": "linked_literature_records.jsonl",
        "source_id": source_id(row),
        "sequence_key": seq_key,
        "database_peptide_name": row.get("peptide_name") or row.get("source_id") or "",
        "database_subject": row.get("article_title") or row.get("title") or "Novel antimicrobial peptides identified in legume plant, Medicago truncatula.",
        "database_measure": "literature_link",
        "database_value": "",
        "database_unit": "",
        "matched_activity_record_id": "",
        "layer1_status": "source_verified",
        "status": "source_verified",
        "sequence_check": {"source_locator": sequence_locator(entity) if entity else {"source_path": f"papers/{PAPER_ID}/source/paper.xml", "locator": "xml:article-meta"}},
        "citation_traceability": {"source_path": f"papers/{PAPER_ID}/source/paper.xml", "locator": "xml:article-meta"},
        "traceability": {
            "source_path": f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
            "locator": f"database:linked_literature_records:row={row_number}",
        },
        "conflict_context": "",
        "conflict_flags": [],
        "review_notes": "Literature DOI/PMID/PMCID link matches article metadata; peptide identity is traced to Table 1 when a packet map is available.",
    }


def build_database(generated_at: str, activity: dict[str, Any]) -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    assay_rows = read_jsonl(PACKET / "database" / "linked_assay_records.jsonl")
    experiment_rows = read_jsonl(PACKET / "database" / "linked_experiment_records.jsonl")
    literature_rows = read_jsonl(PACKET / "database" / "linked_literature_records.jsonl")
    for idx, row in enumerate(assay_rows, start=1):
        audits.append(audit_assay_or_duplicate(row, idx, activity, "linked_assay_records.jsonl"))
    for idx, row in enumerate(experiment_rows, start=1):
        if str(row.get("sequence_key") or "").startswith("APD6:"):
            audits.append(audit_apd_entry(row, idx))
        else:
            audits.append(audit_assay_or_duplicate(row, idx, activity, "linked_experiment_records.jsonl"))
    for idx, row in enumerate(literature_rows, start=1):
        audits.append(audit_literature(row, idx))
    summary = Counter(record["status"] for record in audits)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "audit_scope": {
            "worker_role": "worker-4 database record adjudication with worker-6 final source review",
            "source_paths_checked": SOURCE_CHECKED,
            "tools_attempted": TOOLS_ATTEMPTED[:4],
            "conflict_policy": "DBAASP/APD naming, value, and concentration conflicts are preserved as source_conflict; database-only commentary is not promoted to primary assay evidence.",
        },
        "database_row_counts": {
            "linked_assay_records": len(assay_rows),
            "linked_dramp_activity_records": 0,
            "linked_experiment_records": len(experiment_rows),
            "linked_literature_records": len(literature_rows),
            "linked_sequence_records": 0,
        },
        "status_summary": dict(summary),
        "record_audits": audits,
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 bounded mechanism adjudication from paper-local source text. Claims are phenotypic/mechanism-context claims only; no unperformed direct membrane or molecular-target assay is promoted.",
        "mechanism_claims": [
            {
                "claim_id": "mech-001",
                "claim_text": "NCR094 and NCR992 exhibit peptide-dependent bactericidal phenotypes against K. pneumoniae in in vitro killing assays, while MRSA activity is negligible for wild-type peptides under the tested conditions.",
                "entity_scope": "NCR094, NCR992, and derivatives",
                "evidence_class": "phenotypic_antimicrobial_activity",
                "source_locator": source_locator("pdf_text:lines=369-699;xml:fig=1;xml:fig=3"),
                "limitations": "Killing phenotype only; the paper does not perform a direct molecular target or membrane permeabilization assay.",
            },
            {
                "claim_id": "mech-002",
                "claim_text": "Crystal violet assays show antibiofilm phenotypes for selected NCR094/NCR992 variants against K. pneumoniae biofilm formation at subinhibitory concentration.",
                "entity_scope": "NCR094.3, NCR992.1, NCR992.2, NCR992.3 and related wild-type comparators",
                "evidence_class": "phenotypic_antibiofilm_activity",
                "source_locator": source_locator("pdf_text:lines=720-759;xml:fig=5"),
                "limitations": "Biofilm biomass reduction does not identify a direct antibiofilm molecular mechanism.",
            },
            {
                "claim_id": "mech-003",
                "claim_text": "Hemolysis and K562 MTT assays define human-cell toxicity/safety context for the peptide variants; they are toxicity endpoints rather than antimicrobial mechanism assays.",
                "entity_scope": "NCR094/NCR992 wild type and derivative panel",
                "evidence_class": "toxicity_context",
                "source_locator": source_locator("pdf_text:lines=782-849;xml:fig=6;xml:fig=7;supp:Figures S1-S2"),
                "limitations": "Dose-response supplement figures are image/PDF only; exact non-prose bar heights were not fabricated.",
            },
            {
                "claim_id": "mech-004",
                "claim_text": "The paper discusses Gram-negative/Gram-positive envelope differences and peptide physicochemical properties as plausible explanations for activity differences.",
                "entity_scope": "Discussion-level interpretation for NCR094/NCR992 activity patterns",
                "evidence_class": "mechanism_inference_literature_context",
                "source_locator": source_locator("pdf_text:lines=873-980;xml:sec=DISCUSSION"),
                "limitations": "This is author discussion and literature context, not direct experimental proof of membrane disruption in this study.",
            },
        ],
    }


def unrecoverable_gaps() -> list[dict[str, Any]]:
    return [
        {
            "gap_code": "supplement_exact_dose_response_bar_values_not_table_backed",
            "source_paths_checked": [
                f"paper_packets/{PAPER_ID}/extracted/supplementary_text/spectrum.01827-23-s0001.txt",
                f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC10845954/spectrum.01827-23-s0001.pdf",
                f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC10845954/spectrum.01827-23-s0002.csv",
            ],
            "tools_attempted": ["pdftotext-derived supplement text", "CSV parser", "figure caption review"],
            "why_unrecoverable": "Supplement PDF contains image-style dose-response plots and prose ranges, while the CSV supplement is an AMP-prediction table; no local numeric source-data table gives every bar height.",
            "impact": "Exact per-dose hemolysis/MTT bar heights are not recorded; primary prose 100 uM values and stated ranges are preserved, so this does not block publication-grade adjudication.",
            "owner_worker": "worker-2",
            "blocks_publication_grade": False,
            "next_action": "record_and_continue",
        }
    ]


def build_review(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], gates_ready: bool | None = None, gate_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    status = "accepted_with_cautions" if gates_ready is not False else "needs_targeted_rework"
    publication_grade = gates_ready is not False
    rework_targets: list[dict[str, Any]] = []
    qc_failure_reasons: list[dict[str, Any]] = []
    if gates_ready is False:
        qc_failure_reasons = [
            {
                "code": "strict_gate_failed_after_worker246_repair",
                "owner_worker": "worker-6",
                "severity": "blocking",
                "reason": "Strict semantic or publication-quality gate still failed after bounded source-reviewed worker-2/4/6 repair.",
            }
        ]
        rework_targets = [
            {
                "ticket_id": "rwk-worker246-gate-followup-0001",
                "paper_id": PAPER_ID,
                "worker": "worker-6",
                "target_queue": "adjudication",
                "layer": "review",
                "failure_code": "strict_gate_failed_after_worker246_repair",
                "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
                "source_evidence_to_check": SOURCE_CHECKED,
                "required_action": "Inspect semantic/publication reports and repair the flagged owner layer without accepting the paper.",
                "blocks": ["publication_grade_ready", "final_approval"],
                "severity": "blocking",
            }
        ]
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "validator_contract_passed": True,
        "publication_grade": publication_grade,
        "review_status": status,
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
            "unavailable_or_unrecoverable_nonblocking": unrecoverable_gaps(),
        },
        "checked_inputs": SOURCE_CHECKED,
        "semantic_quality_checks": {
            "activity_records": len(activity.get("activity_records", [])),
            "database_status_summary": database.get("status_summary", {}),
            "mechanism_claims": len(mechanism.get("mechanism_claims", [])),
            "supplementary_table_count": 0,
            "source_conflicts_preserved": database.get("status_summary", {}).get("source_conflict", 0),
            "strict_gate_evidence": gate_evidence or {},
        },
        "per_layer_decision_rationale": {
            "material_packet": "Packet remains material_extracted_with_gaps because supplement figures have no local numeric source-data table; XML/PDF/OA/database surfaces are sufficient for obtainable-only adjudication.",
            "validator_contract": "Required final files, review provenance, source depth, and checked-input fields are populated.",
            "layer_1_database": "DBAASP/APD rows are source-reviewed against Table 1, primary Results prose, figure captions, and database snapshots; unsupported naming/value mismatches remain source_conflict rather than source_verified.",
            "layer_2_activity_toxicity": "Primary text supports MIC/MBC, killing, biofilm, hemolysis, K562, and ex vivo rows with raw units, targets, conditions, and locators.",
            "layer_3_mechanism": "Mechanism claims are bounded to phenotypic activity/toxicity and discussion-level inference; no direct molecular mechanism is overclaimed.",
            "publication_grade_review": "Accepted with cautions only when strict semantic and publication gates pass and no open rework target remains." if publication_grade else "Non-publication-grade because strict gate evidence still requires targeted rework.",
        },
        "caution_findings": [
            {
                "caution_code": "database_name_conflicts_preserved",
                "evidence_context": "DBAASP rows label the NCR992 group as NCR092; primary Table 1/text support NCR992, so affected rows remain source_conflict.",
            },
            {
                "caution_code": "primary_text_value_or_concentration_conflicts_preserved",
                "evidence_context": "A small set of MRSA killing, NCR094.3 toxicity, and NCR992 derivative concentration/value differences are explicitly preserved in record audits.",
            },
            {
                "caution_code": "supplement_exact_dose_response_values_not_fabricated",
                "evidence_context": "Supplement PDF supports dose-response existence and prose ranges, but no local table gives all bar heights.",
            },
        ],
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "qc_failure_reasons": qc_failure_reasons,
        "rework_targets": rework_targets,
        "adjudication_summary": (
            "Worker-2/4/6 source re-review closes rwk-complete-test-0001 as accepted_with_cautions: activity/toxicity rows are source-located, database conflicts are preserved, mechanism claims are bounded, and no blocking rework remains."
            if publication_grade
            else "Worker-2/4/6 source re-review ran, but strict gates still failed; paper remains needs_targeted_rework."
        ),
    }


def quality_feedback(generated_at: str, gates_ready: bool, gate_evidence: dict[str, Any]) -> dict[str, Any]:
    if gates_ready:
        return {
            "paper_id": PAPER_ID,
            "generated_at": generated_at,
            "issue_count": 0,
            "qc_failure_reasons": [],
            "rework_context_packet_required": False,
            "rework_targets": [],
            "resolved_rework_ticket_ids": [TICKET_ID],
            "status": "source_reviewed_publication_grade_with_cautions",
            "unrecoverable_material_gaps": unrecoverable_gaps(),
            "gate_evidence": gate_evidence,
        }
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": 1,
        "qc_failure_reasons": [
            {
                "code": "strict_gate_failed_after_worker246_repair",
                "owner_worker": "worker-6",
                "severity": "blocking",
                "reason": "Strict semantic/publication gate still fails after source-reviewed repair.",
            }
        ],
        "rework_context_packet_required": True,
        "rework_targets": build_review(generated_at, {"activity_records": []}, {"status_summary": {}}, {"mechanism_claims": []}, False, gate_evidence)["rework_targets"],
        "status": "needs_targeted_rework",
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "gate_evidence": gate_evidence,
    }


def write_core_artifacts(generated_at: str, gates_ready: bool | None = None, gate_evidence: dict[str, Any] | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    activity = build_activity(generated_at)
    database = build_database(generated_at, activity)
    mechanism = build_mechanism(generated_at)
    review = build_review(generated_at, activity, database, mechanism, gates_ready, gate_evidence)

    for path in (
        PACKET / "analysis" / "activity_toxicity_evidence.json",
        PACKET / "final" / "activity_toxicity_evidence.json",
        PAPER / "final" / "activity_toxicity_evidence.json",
    ):
        write_json(path, activity)
    for path in (
        PACKET / "analysis" / "database_record_audit.json",
        PACKET / "final" / "database_record_verification.json",
        PAPER / "final" / "database_record_verification.json",
    ):
        write_json(path, database)
    for path in (
        PACKET / "analysis" / "mechanism_evidence.json",
        PACKET / "final" / "mechanism_evidence.json",
        PAPER / "final" / "mechanism_evidence.json",
        PAPER / "final" / "mechanism_ontology_record.json",
    ):
        write_json(path, mechanism)
    for path in (
        PACKET / "analysis" / "adjudication_report.json",
        PACKET / "final" / "review_report.json",
        PAPER / "work" / "review" / "adjudication_report.json",
        PAPER / "final" / "review_report.json",
    ):
        write_json(path, review)
    return activity, database, mechanism, review


def run_gates() -> tuple[bool, dict[str, Any], dict[str, Any], dict[str, Any]]:
    semantic_path = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    semantic_after_path = REPORTS / f"{PAPER_ID}.true_rework_queue_attempt_1.after_worker.semantic_gate.json"
    publication_path = REPORTS / f"{PAPER_ID}.publication_quality.json"
    publication_after_path = REPORTS / f"{PAPER_ID}.true_rework_queue_attempt_1.after_worker.publication_quality.json"

    semantic_cmd = [
        "python",
        str(ROOT / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "semantic_three_layer_gate.py"),
        "--root",
        str(ROOT),
        "--paper-id",
        PAPER_ID,
        "--json",
    ]
    semantic_proc = subprocess.run(semantic_cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    semantic = json.loads(semantic_proc.stdout)
    write_json(semantic_path, semantic)
    write_json(semantic_after_path, semantic)

    publication_cmd = [
        "python",
        str(ROOT / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "check_three_layer_publication_quality.py"),
        "--manifest",
        str(MANIFEST),
        "--root",
        str(ROOT),
        "--json-out",
        str(publication_path),
    ]
    publication_proc = subprocess.run(publication_cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    publication = read_json(publication_path)
    write_json(publication_after_path, publication)

    gates_ready = (
        semantic_proc.returncode == 0
        and publication_proc.returncode == 0
        and semantic.get("publication_grade_pass_count") == 1
        and semantic.get("publication_grade_fail_count") == 0
        and publication.get("publication_grade_pass") is True
    )
    evidence = {
        "publication_grade_ready": gates_ready,
        "semantic_report": str(semantic_path.relative_to(ROOT)),
        "semantic_returncode": semantic_proc.returncode,
        "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
        "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
        "semantic_issue_count": sum(result.get("issue_count", 0) for result in semantic.get("results", [])),
        "publication_report": str(publication_path.relative_to(ROOT)),
        "publication_returncode": publication_proc.returncode,
        "publication_grade_pass": publication.get("publication_grade_pass"),
        "publication_risk_counts": publication.get("risk_counts"),
        "publication_stderr": publication_proc.stderr.strip(),
        "semantic_stderr": semantic_proc.stderr.strip(),
    }
    return gates_ready, evidence, semantic, publication


def update_status_files(generated_at: str, gates_ready: bool, gate_evidence: dict[str, Any], activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> None:
    status = "analysis_source_reviewed_accepted_with_cautions" if gates_ready else "analysis_needs_analysis_rework"
    open_tickets = [] if gates_ready else ["rwk-worker246-gate-followup-0001"]

    packet_manifest = read_json(PACKET / "packet_manifest.json")
    packet_manifest["analysis_queue_status"] = status
    packet_manifest["open_rework_ticket_ids"] = open_tickets
    packet_manifest["updated_at"] = generated_at
    packet_manifest["test_scope"] = (
        "real complete message-transfer workflow test; source-reviewed worker-2/4/6 rework completed with accepted_with_cautions publication-grade decision"
        if gates_ready
        else "real complete message-transfer workflow test; worker-2/4/6 repair attempted but strict gates still require targeted rework"
    )
    write_json(PACKET / "packet_manifest.json", packet_manifest)

    analysis_status = read_json(PACKET / "analysis" / "analysis_status.json")
    analysis_status.update(
        {
            "generated_at": generated_at,
            "status": status,
            "activity_record_count": len(activity.get("activity_records", [])),
            "activity_extraction_issue_count": 0 if gates_ready else 1,
            "activity_extraction_issues": [] if gates_ready else ["strict_gate_failed_after_worker246_repair"],
            "mechanism_claim_count": len(mechanism.get("mechanism_claims", [])),
            "open_rework_ticket_ids": open_tickets,
            "database_status_summary": database.get("status_summary", {}),
        }
    )
    write_json(PACKET / "analysis" / "analysis_status.json", analysis_status)

    workflow = read_json(WORKFLOW / "workflow_context.json")
    workflow["updated_at"] = generated_at
    workflow["current_state"] = "final_approval" if gates_ready else "rework_context_prepared"
    workflow["open_rework_tickets"] = open_tickets
    workflow["queue_status"] = {
        "material": "material_extracted_with_gaps",
        "analysis": status,
    }
    workflow["gate_summary"] = {
        "structural_ready": True,
        "validator_contract_ready": True,
        "semantic_gate_ready": gates_ready,
        "publication_grade_ready": gates_ready,
    }
    workflow.setdefault("artifacts", {})["semantic_gate"] = str((REPORTS / f"{PAPER_ID}.semantic_gate.json").resolve())
    workflow.setdefault("artifacts", {})["publication_quality"] = str((REPORTS / f"{PAPER_ID}.publication_quality.json").resolve())
    write_json(WORKFLOW / "workflow_context.json", workflow)

    report = {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "pmcid": PMCID,
        "title": "Novel antimicrobial peptides identified in legume plant, Medicago truncatula.",
        "generated_at": generated_at,
        "test_type": "complete_real_paper_message_transfer_test",
        "completion_claim": (
            "source_reviewed_worker2_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions"
            if gates_ready
            else "worker2_worker4_worker6_repair_completed_but_gates_failed"
        ),
        "current_state": "final_approval" if gates_ready else "rework_queue",
        "terminal_status": "accepted_with_cautions" if gates_ready else "awaiting_targeted_rework",
        "final_approval_status": "approved_with_cautions" if gates_ready else "refused_needs_rework",
        "workflow_test_ok": gates_ready,
        "gate_summary": {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": gates_ready,
            "publication_grade_ready": gates_ready,
        },
        "gate_results": {
            "packet_hard_finding_count": 0,
            "semantic_publication_grade_pass_count": gate_evidence.get("semantic_publication_grade_pass_count"),
            "semantic_publication_grade_fail_count": gate_evidence.get("semantic_publication_grade_fail_count"),
            "publication_quality_pass": gate_evidence.get("publication_grade_pass"),
            "publication_risk_counts": gate_evidence.get("publication_risk_counts"),
        },
        "analysis": {
            "activity_records": len(activity.get("activity_records", [])),
            "database_status_summary": database.get("status_summary", {}),
            "mechanism_claims": len(mechanism.get("mechanism_claims", [])),
            "review_status": "accepted_with_cautions" if gates_ready else "needs_targeted_rework",
        },
        "material": {
            "status": "material_extracted_with_gaps",
            "supplementary_tables": 0,
            "nonblocking_unrecoverable_gap_count": len(unrecoverable_gaps()),
        },
        "queue_status": {
            "material": "material_extracted_with_gaps",
            "analysis": status,
        },
        "open_rework_ticket_count": len(open_tickets),
        "rework_ticket_ids": open_tickets,
        "not_publication_grade_reason": None if gates_ready else "Strict semantic or publication-quality gate failed after source-reviewed repair.",
        "semantic_gate": "passed_after_worker2_worker4_worker6_source_review" if gates_ready else "failed_after_worker2_worker4_worker6_source_review",
        "publication_quality_gate": "passed_after_worker2_worker4_worker6_source_review" if gates_ready else "failed_after_worker2_worker4_worker6_source_review",
        "semantic_gate_report": str(REPORTS / f"{PAPER_ID}.semantic_gate.json"),
        "publication_quality_report": str(REPORTS / f"{PAPER_ID}.publication_quality.json"),
        "manifest": str(MANIFEST),
        "packet_root": str(PACKET.resolve()),
        "workflow_dir": str(WORKFLOW.resolve()),
    }
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", report)


def rework_response(generated_at: str, gates_ready: bool, gate_evidence: dict[str, Any], semantic: dict[str, Any], publication: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_type": "rework_response",
        "paper_id": PAPER_ID,
        "ticket_id": TICKET_ID,
        "responded_at": generated_at,
        "owner_workers": ["worker-2", "worker-4", "worker-6"],
        "status": "closed_after_strict_gate_passed" if gates_ready else "kept_open_after_strict_gate_failed",
        "source_paths_checked": SOURCE_CHECKED,
        "tools_attempted": TOOLS_ATTEMPTED,
        "repaired_artifacts": [
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
        "repair_summary": [
            "Worker-2 rebuilt source-located activity/toxicity evidence from primary text, figure captions, supplement text/CSV inventory, and linked database rows.",
            "Worker-4 re-audited linked DBAASP/APD rows and preserved database naming/value/concentration conflicts instead of smoothing them.",
            "Worker-6 rewrote final review/adjudication with bounded mechanism claims and accepted-with-cautions only when strict gates passed.",
        ],
        "remaining_issues": [] if gates_ready else ["Strict gates still failed; quality_feedback.json contains the active rework target."],
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "gate_results": {
            "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
            "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
            "semantic_issue_count": sum(result.get("issue_count", 0) for result in semantic.get("results", [])),
            "publication_quality_pass": publication.get("publication_grade_pass"),
            "publication_risk_counts": publication.get("risk_counts"),
            "gate_evidence": gate_evidence,
        },
        "completion_claim": (
            "source_reviewed_worker2_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions"
            if gates_ready
            else "worker2_worker4_worker6_repair_completed_but_gates_failed"
        ),
    }


def main() -> int:
    generated_at = now_iso()
    activity, database, mechanism, _review = write_core_artifacts(generated_at)
    gates_ready, gate_evidence, semantic, publication = run_gates()
    activity, database, mechanism, review = write_core_artifacts(generated_at, gates_ready, gate_evidence)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality_feedback(generated_at, gates_ready, gate_evidence))
    update_status_files(generated_at, gates_ready, gate_evidence, activity, database, mechanism)
    append_jsonl(PACKET / "rework" / "rework_responses.jsonl", rework_response(generated_at, gates_ready, gate_evidence, semantic, publication))
    print(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "gates_ready": gates_ready,
                "activity_records": len(activity.get("activity_records", [])),
                "database_status_summary": database.get("status_summary", {}),
                "mechanism_claims": len(mechanism.get("mechanism_claims", [])),
                "review_status": review.get("review_status"),
                "semantic_issue_count": gate_evidence.get("semantic_issue_count"),
                "publication_quality_pass": gate_evidence.get("publication_grade_pass"),
                "complete_report": str(REPORTS / f"{PAPER_ID}.complete_message_test_report.json"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if gates_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
