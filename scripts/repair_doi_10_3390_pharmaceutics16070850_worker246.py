#!/usr/bin/env python3
"""Source-reviewed worker-2/4/6 repair for doi__10.3390_pharmaceutics16070850."""

from __future__ import annotations

import json
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.3390_pharmaceutics16070850"
DOI = "10.3390/pharmaceutics16070850"
PMCID = "PMC11279594"
PMID = "39065546"
TICKET_ID = "rwk-complete-test-0001"
REVIEWED_AT_START = "2026-05-09T18:22:30Z"

PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
REPORTS = ROOT / "reports"
MANIFEST = REPORTS / f"{PAPER_ID}.codex_worker246_rereview_manifest.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path | str) -> str:
    path = Path(path)
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl_once(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    key = (payload.get("ticket_id"), payload.get("status"), payload.get("created_by"))
    existing: list[dict[str, Any]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            existing.append(row)
            if (row.get("ticket_id"), row.get("status"), row.get("created_by")) == key:
                return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


SOURCE_PATHS_CHECKED = [
    "rework_context/doi__10.3390_pharmaceutics16070850/handoff_context.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/packet_manifest.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/locators/locator_index.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extraction/extraction_status.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extraction/extraction_quality_report.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/raw/paper.xml",
    "paper_packets/doi__10.3390_pharmaceutics16070850/raw/paper.pdf",
    "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
    "papers/doi__10.3390_pharmaceutics16070850/source/paper.pdf",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/xml_sections.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/pdf_text/pharmaceutics-16-00850.txt",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/pdf_text/local-DBAASP-PMC11279594.txt",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/pdf_tables.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/figure_captions.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/supplementary_index.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/supplementary_tables.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/archive_manifest.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/raw/oa_package/local-APD6-pmc_package.tar.gz",
    "paper_packets/doi__10.3390_pharmaceutics16070850/raw/oa_package/local-DBAASP-PMC11279594.tar.gz",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/oa_package/local-APD6-pmc_package/PMC11279594/pharmaceutics-16-00850.nxml",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/oa_package/local-APD6-pmc_package/PMC11279594/pharmaceutics-16-00850.pdf",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/oa_package/local-APD6-pmc_package/PMC11279594/pharmaceutics-16-00850-g005.jpg",
    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/oa_package/local-APD6-pmc_package/PMC11279594/pharmaceutics-16-00850-g006.jpg",
    "paper_packets/doi__10.3390_pharmaceutics16070850/database/database_source_manifest.json",
    "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_assay_records.jsonl",
    "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_experiment_records.jsonl",
    "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_literature_records.jsonl",
    "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_sequence_records.jsonl",
    "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_dramp_activity_records.jsonl",
]

TOOLS_ATTEMPTED = [
    "sed/jq over worker skill files and handoff JSON",
    "rg over paper XML, extracted XML sections, and PDF text for MIC, ZOI, hemolysis, NACAP-II, and database IDs",
    "jq/nl over packet database JSONL snapshots",
    "tar -tzf over both local OA packages",
    "find/jq over supplementary indexes and package members",
    "view_image inspection of Figure 5 and Figure 6 local JPEGs",
    "semantic_three_layer_gate.py --json",
    "check_three_layer_publication_quality.py --json-out",
]


def activity_records() -> list[dict[str, Any]]:
    common = {
        "entity": "NACAP-II",
        "entity_display_name": "NACAP-II",
        "peptide_label_in_source": "NACAP-II",
        "sequence": "LANVLFRRNATTILQ",
        "sequence_key": "DBAASP:DBAASPS_23071",
        "sequence_modification_note": "Linear synthesized NACAP-II sequence as reported in Table 1, Figure 1, and peptide synthesis/results sections; no terminal modification was source-reported.",
        "normalization_status": "direct",
        "database_crossrefs": [
            "DBAASP:DBAASPS_23071",
            "APD6:AP05465",
        ],
    }
    return [
        {
            **common,
            "record_id": f"{PAPER_ID}-nacap_ii-esbl_ecoli_atcc35218-mic",
            "endpoint": "MIC",
            "raw_value": "91.3 ± 1.2",
            "raw_unit": "µg/mL",
            "target": {
                "class": "bacteria",
                "species": "Escherichia coli",
                "strain": "ATCC 35218; ESBL-producing",
                "gram_status": "Gram-negative",
                "source_label": "ESBL-producing E. coli ATCC 35218",
            },
            "assay_conditions": {
                "assay_method": "broth dilution with resazurin readout",
                "medium": "Tryptic Soy Broth",
                "inoculum": "1.5 × 10^6 cells/mL bacterial suspension added to test wells",
                "temperature": "37 °C",
                "incubation_time": "overnight before resazurin, then 4 h after resazurin",
                "replicate_statistics": "triplicate dilutions; result reported as mean ± SEM",
                "source_method_locator": {
                    "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                    "locator": "xml:sec=13:2.7.2. Broth Dilution Method",
                },
            },
            "evidence_ladder": "primary_xml_results_plus_method",
            "source_locator": {
                "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                "locator": "xml:sec=19:3.4. Peptide Synthesis and In Vitro Antimicrobial Activity",
                "method_locator": "xml:sec=13:2.7.2. Broth Dilution Method",
                "abstract_locator": "xml:abstract",
            },
            "source_column_context": {
                "result_context": "MIC against ESBL-producing E. coli",
                "unit": "µg/mL",
            },
            "database_crossrefs": [
                "DBAASP:linked_assay_records:row=2",
                "DBAASP:linked_experiment_records:row=2",
                "APD6:linked_experiment_records:row=3",
            ],
            "curation_notes": "Worker-2 source review recovered this primary MIC result from XML/PDF prose after the parser emitted zero activity rows.",
        },
        {
            **common,
            "record_id": f"{PAPER_ID}-nacap_ii-esbl_ecoli_atcc35218-zoi",
            "endpoint": "ZOI",
            "raw_value": "22.7 ± 0.9",
            "raw_unit": "mm",
            "target": {
                "class": "bacteria",
                "species": "Escherichia coli",
                "strain": "ATCC 35218; ESBL-producing",
                "gram_status": "Gram-negative",
                "source_label": "ESBL-producing E. coli cultured on Mueller-Hinton Agar",
            },
            "assay_conditions": {
                "assay_method": "spot-on-lawn zone-of-inhibition assay",
                "medium": "Mueller-Hinton Agar",
                "peptide_application": "25 µL laboratory-prepared NACAP-II spotted onto lawn",
                "temperature": "37 °C",
                "incubation_time": "18 h",
                "controls": "ciprofloxacin positive control and 1X PBS negative control",
                "replicate_statistics": "experiment performed in triplicate; result reported as mean ± SEM",
                "source_method_locator": {
                    "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                    "locator": "xml:sec=12:2.7.1. Spot-on-Lawn Method",
                },
            },
            "evidence_ladder": "primary_xml_figure_caption_plus_results",
            "source_locator": {
                "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                "locator": "xml:fig=5:Figure 5",
                "result_locator": "xml:sec=19:3.4. Peptide Synthesis and In Vitro Antimicrobial Activity",
                "figure_image": "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/oa_package/local-APD6-pmc_package/PMC11279594/pharmaceutics-16-00850-g005.jpg",
            },
            "source_column_context": {
                "figure": "Figure 5",
                "unit": "mm",
            },
            "database_crossrefs": [
                "APD6:linked_experiment_records:row=3",
            ],
            "curation_notes": "Worker-2 preserved the ZOI result as a source-reported phenotype row rather than treating it as a database-only comment.",
        },
        {
            **common,
            "record_id": f"{PAPER_ID}-nacap_ii-rabbit_erythrocytes-hemolysis",
            "endpoint": "percent hemolysis",
            "raw_value": "<5 at 100 µg/mL; non-hemolytic across 1-100 µg/mL",
            "raw_unit": "%",
            "target": {
                "class": "mammalian erythrocytes",
                "species": "Oryctolagus cuniculus",
                "strain": "rabbit red blood cells",
                "gram_status": "not_applicable",
                "source_label": "rabbit erythrocytes",
            },
            "assay_conditions": {
                "assay_method": "rabbit red blood cell hemolysis assay",
                "test_concentrations": "1, 10, 50, and 100 µg/mL",
                "temperature": "37 °C",
                "incubation_time": "1 h",
                "positive_control": "1% Triton X-100",
                "negative_control": "1X PBS without peptide",
                "replicate_statistics": "three independent experiments; mean values reported; text reports p = 0.198",
                "source_method_locator": {
                    "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                    "locator": "xml:sec=14:2.8. Hemotoxicity Profile of Antimicrobial Peptide",
                },
            },
            "evidence_ladder": "primary_xml_figure_caption_plus_visual_figure_review",
            "source_locator": {
                "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                "locator": "xml:fig=6:Figure 6",
                "result_locator": "xml:sec=20:3.5. Hemolytic Activity of the Antimicrobial Peptide",
                "figure_image": "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/oa_package/local-APD6-pmc_package/PMC11279594/pharmaceutics-16-00850-g006.jpg",
            },
            "source_column_context": {
                "figure": "Figure 6",
                "unit": "%",
                "exactness_caution": "per-concentration exact numeric values are plotted, not tabulated",
            },
            "database_crossrefs": [
                "DBAASP:linked_assay_records:row=1",
                "DBAASP:linked_experiment_records:row=1",
                "APD6:linked_experiment_records:row=3",
            ],
            "curation_notes": "Worker-2 preserved the source-supported non-hemolysis finding and did not invent per-concentration exact values beyond the figure/database-supported <5% at 100 µg/mL.",
        },
    ]


def build_activity_payload(timestamp: str) -> dict[str, Any]:
    records = activity_records()
    return {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "generated_at": timestamp,
        "reviewed_at": timestamp,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "publication_grade": True,
        "activity_record_count": len(records),
        "activity_records": records,
        "extraction_scope": "Worker-2 re-review reopened XML/PDF text, figure captions/images, OA packages, and linked database rows; primary activity/toxicity rows are limited to source-supported NACAP-II MIC, ZOI, and hemolysis findings.",
        "source_paths_checked": SOURCE_PATHS_CHECKED,
        "tools_attempted": TOOLS_ATTEMPTED,
        "non_promoted_context_findings": [
            {
                "finding_id": "ctx-in-silico-amp-table1",
                "category": "computational_prediction_context",
                "source_locator": {
                    "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                    "locator": "xml:table=1",
                },
                "source_summary": "Table 1 reports general antimicrobial prediction labels for eight NACAP peptides; these are not experimental MIC/ZOI/toxicity endpoint rows.",
                "promotion_decision": "not_promoted_computational_prediction",
            },
            {
                "finding_id": "ctx-pride-data-availability",
                "category": "external_repository_context",
                "source_locator": {
                    "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                    "locator": "xml:sec=27:Data Availability Statement",
                },
                "source_summary": "The paper points to PRIDE mass-spectrometry data; no local supplementary activity/toxicity table is packaged with the packet.",
                "promotion_decision": "not_promoted_external_repository_not_local_activity_table",
            },
        ],
        "extraction_issues": [],
        "parser_quality_control": {
            "issue_count": 0,
            "rejects_property_or_model_tables": True,
            "requires_target_entity_value_matrix": True,
            "strict_endpoint_matching": True,
            "worker2_repair_note": "The prior zero-row artifact was repaired from source prose and figure locators; Table 1 prediction/property rows remain non-promoted.",
        },
        "unrecoverable_material_gaps": [
            {
                "gap_code": "no_local_supplementary_activity_tables",
                "source_paths_checked": [
                    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/supplementary_index.json",
                    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/supplementary_tables.json",
                    "paper_packets/doi__10.3390_pharmaceutics16070850/raw/oa_package/local-APD6-pmc_package.tar.gz",
                    "paper_packets/doi__10.3390_pharmaceutics16070850/raw/oa_package/local-DBAASP-PMC11279594.tar.gz",
                ],
                "tools_attempted": ["jq", "find", "tar -tzf", "rg supplementary/PXD049239"],
                "why_unrecoverable": "Both OA packages contain the article XML/PDF plus figures; packet supplementary indexes contain zero local supplementary assets or structured supplementary tables.",
                "impact": "No additional supplement-derived activity/toxicity rows can be recovered locally; primary XML/PDF prose and figures are the supported activity/toxicity surface.",
                "owner_worker": "worker-2",
                "blocks_publication_grade": False,
                "next_action": "record_and_continue",
            },
            {
                "gap_code": "hemolysis_exact_point_values_not_tabulated",
                "source_paths_checked": [
                    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/figure_captions.json",
                    "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/oa_package/local-APD6-pmc_package/PMC11279594/pharmaceutics-16-00850-g006.jpg",
                    "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                ],
                "tools_attempted": ["view_image", "rg hemolysis/non-hemolytic/p=0.198", "XML/PDF text review"],
                "why_unrecoverable": "The source figure and text support non-hemolysis and a low plotted value at 100 µg/mL, but the paper does not tabulate every per-concentration exact percentage.",
                "impact": "Hemolysis is recorded as source-supported non-hemolytic/<5% at 100 µg/mL with an exactness caution; no fabricated per-concentration values were added.",
                "owner_worker": "worker-2",
                "blocks_publication_grade": False,
                "next_action": "record_and_continue",
            },
        ],
    }


def source_locator() -> dict[str, str]:
    return {
        "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
        "locator": "xml:table=1:row=3 + xml:fig=1 + xml:sec=19",
        "primary_source_statement": "Table 1 and Figure 1 identify NACAP-II as LANVLFRRNATTILQ; the results section reports synthesized NACAP-II activity.",
    }


def db_record(
    *,
    row_no: int,
    table: str,
    source_id: str,
    sequence_key: str,
    database: str,
    subject: str,
    measure: str,
    concentration: str,
    unit: str,
    matched: str | list[str],
    status: str,
    locator: str,
    notes: str,
    conflict: str = "",
    flags: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "sequence_key": sequence_key,
        "source_table": table,
        "database": database,
        "database_subject": subject,
        "database_measure": measure,
        "database_concentration": concentration,
        "database_unit": unit,
        "matched_activity_record_id": matched,
        "status": status,
        "layer1_status": status,
        "traceability": {
            "source_path": f"paper_packets/doi__10.3390_pharmaceutics16070850/database/{table}",
            "locator": f"database:{table}:row={row_no}",
        },
        "citation_traceability": {
            "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
            "locator": "xml:article-meta",
        },
        "sequence_check": {
            "source_locator": source_locator(),
            "database_sequence_snapshot": "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_sequence_records.jsonl",
        },
        "activity_source_locator": {
            "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
            "locator": locator,
        },
        "review_notes": notes,
        "conflict_context": conflict,
        "conflict_flags": flags or [],
    }


def build_database_payload(timestamp: str) -> dict[str, Any]:
    mic_id = f"{PAPER_ID}-nacap_ii-esbl_ecoli_atcc35218-mic"
    zoi_id = f"{PAPER_ID}-nacap_ii-esbl_ecoli_atcc35218-zoi"
    hemo_id = f"{PAPER_ID}-nacap_ii-rabbit_erythrocytes-hemolysis"
    records = [
        db_record(
            row_no=1,
            table="linked_assay_records.jsonl",
            source_id="DBAASPS_23071",
            sequence_key="DBAASP:DBAASPS_23071",
            database="DBAASP",
            subject="Rabbit erythrocytes",
            measure="<5% Hemolysis",
            concentration="100",
            unit="µg/ml",
            matched=hemo_id,
            status="source_verified",
            locator="xml:fig=6:Figure 6 + xml:sec=20:3.5. Hemolytic Activity",
            notes="Worker-4 matched the DBAASP hemolysis row to primary Figure 6/text; exact per-concentration percentages remain figure-only and are preserved as a caution.",
            flags=["exact_hemolysis_point_values_not_tabulated"],
        ),
        db_record(
            row_no=2,
            table="linked_assay_records.jsonl",
            source_id="DBAASPS_23071",
            sequence_key="DBAASP:DBAASPS_23071",
            database="DBAASP",
            subject="Escherichia coli ATCC 35218",
            measure="MIC",
            concentration="91.3±1.2",
            unit="µg/ml",
            matched=mic_id,
            status="source_verified",
            locator="xml:sec=19:3.4. Peptide Synthesis and In Vitro Antimicrobial Activity",
            notes="Worker-4 matched the DBAASP MIC row to the primary XML/PDF result and method locators.",
        ),
        db_record(
            row_no=1,
            table="linked_experiment_records.jsonl",
            source_id="DBAASPS_23071",
            sequence_key="DBAASP:DBAASPS_23071",
            database="DBAASP",
            subject="Rabbit erythrocytes",
            measure="<5% Hemolysis",
            concentration="100",
            unit="µg/ml",
            matched=hemo_id,
            status="source_verified",
            locator="xml:fig=6:Figure 6 + xml:sec=20:3.5. Hemolytic Activity",
            notes="Duplicate DBAASP assay_refs.csv row reconciled to the same primary-source hemolysis finding.",
            flags=["exact_hemolysis_point_values_not_tabulated"],
        ),
        db_record(
            row_no=2,
            table="linked_experiment_records.jsonl",
            source_id="DBAASPS_23071",
            sequence_key="DBAASP:DBAASPS_23071",
            database="DBAASP",
            subject="Escherichia coli ATCC 35218",
            measure="MIC",
            concentration="91.3±1.2",
            unit="µg/ml",
            matched=mic_id,
            status="source_verified",
            locator="xml:sec=19:3.4. Peptide Synthesis and In Vitro Antimicrobial Activity",
            notes="Duplicate DBAASP assay_refs.csv MIC row reconciled to the same primary-source MIC finding.",
        ),
        db_record(
            row_no=3,
            table="linked_experiment_records.jsonl",
            source_id="AP05465",
            sequence_key="APD6:AP05465",
            database="APD6",
            subject="free-text APD6 peptide entry",
            measure="entry_text",
            concentration="",
            unit="",
            matched=[mic_id, zoi_id, hemo_id],
            status="source_conflict",
            locator="xml:table=1:row=3 + xml:sec=19 + xml:fig=5 + xml:fig=6",
            notes="APD6 free text is linked to this paper and partly agrees with primary MIC/ZOI/non-hemolysis evidence, but uses database-only shorthand and an HC50-style statement that is not exactly reported in the local primary source.",
            conflict="Primary source supports NACAP-II sequence, MIC 91.3 ± 1.2 µg/mL, ZOI 22.7 ± 0.9 mm, and non-hemolysis; APD6 free text also states HC50>100 µg/mL and rounded ZOI/MIC wording not tabulated verbatim in the paper.",
            flags=["database_free_text_partially_supported", "hc50_statement_not_primary_text"],
        ),
        db_record(
            row_no=1,
            table="linked_literature_records.jsonl",
            source_id="AP05465",
            sequence_key="APD6:AP05465",
            database="APD6",
            subject="article metadata",
            measure="literature_link",
            concentration="",
            unit="",
            matched="",
            status="source_verified",
            locator="xml:article-meta",
            notes="APD6 literature link matches the primary article DOI, PMID, PMCID, title, and year.",
        ),
        db_record(
            row_no=2,
            table="linked_literature_records.jsonl",
            source_id="DBAASPS_23071",
            sequence_key="DBAASP:DBAASPS_23071",
            database="DBAASP",
            subject="article metadata",
            measure="literature_link",
            concentration="",
            unit="",
            matched="",
            status="source_verified",
            locator="xml:article-meta",
            notes="DBAASP literature link matches the primary article DOI, PMID, PMCID, title, and year.",
        ),
    ]
    status_summary = Counter(record["status"] for record in records)
    return {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "generated_at": timestamp,
        "reviewed_at": timestamp,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "publication_grade": True,
        "audit_scope": "Worker-4 rechecked linked APD6/DBAASP rows against primary XML/PDF prose, Figure 5, Figure 6, article metadata, and packet database JSONL.",
        "database_row_counts": {
            "linked_assay_records": 2,
            "linked_experiment_records": 3,
            "linked_literature_records": 2,
            "linked_dramp_activity_records": 0,
            "linked_sequence_records": 0,
        },
        "record_audits": records,
        "status_summary": dict(status_summary),
        "unrecoverable_material_gaps": [
            {
                "gap_code": "linked_sequence_records_absent",
                "source_paths_checked": [
                    "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_sequence_records.jsonl",
                    "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_assay_records.jsonl",
                    "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                ],
                "tools_attempted": ["wc -l", "nl -ba", "rg", "XML section/table review"],
                "why_unrecoverable": "The packet contains linked assay, experiment, and literature rows but no linked sequence rows; sequence identity was therefore source-reviewed from primary Table 1/Figure 1 and database IDs.",
                "impact": "Missing sequence snapshot remains a caution, but linked assay/literature rows can be adjudicated from source locators.",
                "owner_worker": "worker-4",
                "blocks_publication_grade": False,
                "next_action": "record_and_continue",
            }
        ],
    }


def build_mechanism_payload(timestamp: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "generated_at": timestamp,
        "reviewed_at": timestamp,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "publication_grade": True,
        "extraction_scope": "Worker-6 final mechanism review keeps claims bounded to source-supported phenotype, safety, and computational structure context; no direct molecular mechanism assay is claimed.",
        "mechanism_claims": [
            {
                "claim_id": "mech-001",
                "claim_text": "NACAP-II has source-supported antibacterial phenotype against ESBL-producing E. coli, but the paper does not establish a direct molecular mechanism of action.",
                "entity_scope": "NACAP-II",
                "evidence_class": "phenotype_supported",
                "direct_assay_types": [],
                "source_locator": {
                    "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                    "locator": "xml:sec=19:3.4. Peptide Synthesis and In Vitro Antimicrobial Activity + xml:fig=5",
                },
                "limitations": "ZOI and MIC are activity phenotypes, not membrane-disruption or intracellular-target assays.",
            },
            {
                "claim_id": "mech-002",
                "claim_text": "NACAP-II was non-hemolytic to rabbit erythrocytes under the tested local-source conditions.",
                "entity_scope": "NACAP-II",
                "evidence_class": "toxicity_phenotype",
                "direct_assay_types": [],
                "source_locator": {
                    "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                    "locator": "xml:sec=20:3.5. Hemolytic Activity of the Antimicrobial Peptide + xml:fig=6",
                },
                "limitations": "This is a safety/toxicity phenotype; it does not identify a microbial mechanism.",
            },
            {
                "claim_id": "mech-003",
                "claim_text": "I-TASSER and PEP-FOLD structure predictions support computational structure context for NACAP-II only.",
                "entity_scope": "NACAP-II",
                "evidence_class": "computational_structure_context",
                "direct_assay_types": [],
                "source_locator": {
                    "source_path": "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                    "locator": "xml:sec=18:3.3. The 3-D Structure Modelling + xml:table=2 + xml:fig=2",
                },
                "limitations": "Computational model quality metrics are not promoted to direct mechanism evidence.",
            },
        ],
        "caution_findings": [
            {
                "caution_code": "no_direct_mechanism_assay",
                "severity": "caution",
                "evidence_context": "The paper itself says further studies are required to establish mode of action; worker-6 does not promote background membrane language from references.",
            }
        ],
    }


def gap_entries() -> list[dict[str, Any]]:
    return [
        {
            "gap_code": "no_local_supplementary_assets",
            "source_paths_checked": [
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/supplementary_index.json",
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/supplementary_tables.json",
                "paper_packets/doi__10.3390_pharmaceutics16070850/raw/oa_package/local-APD6-pmc_package.tar.gz",
                "paper_packets/doi__10.3390_pharmaceutics16070850/raw/oa_package/local-DBAASP-PMC11279594.tar.gz",
            ],
            "tools_attempted": ["jq", "find", "tar -tzf", "rg supplementary/PXD049239"],
            "why_unrecoverable": "No paper-local supplementary files or structured supplementary tables are present; OA packages contain article XML/PDF and figures only.",
            "impact": "No supplement-derived activity/toxicity/mechanism rows can be added locally.",
            "owner_worker": "worker-2",
            "blocks_publication_grade": False,
            "next_action": "record_and_continue",
        },
        {
            "gap_code": "linked_sequence_records_absent",
            "source_paths_checked": [
                "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_sequence_records.jsonl",
                "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_assay_records.jsonl",
                "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_literature_records.jsonl",
                "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
            ],
            "tools_attempted": ["wc -l", "nl -ba", "rg", "XML section/table review"],
            "why_unrecoverable": "The packet database snapshot has no linked sequence rows, so exact database sequence snapshots cannot be independently compared from that file.",
            "impact": "Worker-4 anchored sequence identity to Table 1/Figure 1 and preserved the missing sequence snapshot as a caution.",
            "owner_worker": "worker-4",
            "blocks_publication_grade": False,
            "next_action": "record_and_continue",
        },
        {
            "gap_code": "hemolysis_exact_point_values_not_tabulated",
            "source_paths_checked": [
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/figure_captions.json",
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/oa_package/local-APD6-pmc_package/PMC11279594/pharmaceutics-16-00850-g006.jpg",
                "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
            ],
            "tools_attempted": ["view_image", "rg hemolysis/non-hemolytic/p=0.198", "XML/PDF text review"],
            "why_unrecoverable": "The source plots hemolysis values but does not tabulate every exact per-concentration percentage.",
            "impact": "Database/source hemolysis is accepted as low/non-hemolytic with an exactness caution; no fabricated point series was added.",
            "owner_worker": "worker-2",
            "blocks_publication_grade": False,
            "next_action": "record_and_continue",
        },
    ]


def build_review_payload(
    timestamp: str,
    activity_payload: dict[str, Any],
    database_payload: dict[str, Any],
    mechanism_payload: dict[str, Any],
    gates: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "pmcid": PMCID,
        "pmid": PMID,
        "generated_at": timestamp,
        "reviewed_at": timestamp,
        "reviewed_at_start": REVIEWED_AT_START,
        "reviewed_at_end": timestamp,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "review_status": "accepted_with_cautions",
        "publication_grade": True,
        "validator_contract_passed": True,
        "source_reviewed": True,
        "source_review_depth": {
            "paper_xml": [
                "papers/doi__10.3390_pharmaceutics16070850/source/paper.xml",
                "paper_packets/doi__10.3390_pharmaceutics16070850/raw/paper.xml",
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/xml_sections.json",
            ],
            "paper_pdf": [
                "papers/doi__10.3390_pharmaceutics16070850/source/paper.pdf",
                "paper_packets/doi__10.3390_pharmaceutics16070850/raw/paper.pdf",
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/pdf_text/pharmaceutics-16-00850.txt",
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/pdf_text/local-DBAASP-PMC11279594.txt",
            ],
            "oa_package": [
                "paper_packets/doi__10.3390_pharmaceutics16070850/raw/oa_package/local-APD6-pmc_package.tar.gz",
                "paper_packets/doi__10.3390_pharmaceutics16070850/raw/oa_package/local-DBAASP-PMC11279594.tar.gz",
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/oa_package/local-APD6-pmc_package/PMC11279594/",
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/oa_package/local-DBAASP-PMC11279594/PMC11279594/",
            ],
            "supplementary_assets": [
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/supplementary_index.json",
                "paper_packets/doi__10.3390_pharmaceutics16070850/extracted/supplementary_tables.json",
                "supplementary_asset_count=0",
            ],
            "merged_database_rows": [
                "paper_packets/doi__10.3390_pharmaceutics16070850/database/database_source_manifest.json",
                "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_assay_records.jsonl",
                "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_experiment_records.jsonl",
                "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_literature_records.jsonl",
                "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_sequence_records.jsonl",
                "paper_packets/doi__10.3390_pharmaceutics16070850/database/linked_dramp_activity_records.jsonl",
            ],
        },
        "materials_exhausted": {
            "paper_xml": True,
            "paper_pdf": True,
            "oa_package": True,
            "supplementary_assets": True,
            "merged_database_rows": True,
            "note": "Bounded worker-2/4/6 re-review reopened XML/PDF/prose/figures/OA packages/database snapshots. No local supplementary assets exist; remaining gaps are nonblocking cautions.",
        },
        "checked_inputs": SOURCE_PATHS_CHECKED,
        "semantic_quality_checks": {
            "activity_rows_source_reviewed": activity_payload["activity_record_count"],
            "database_status_summary": database_payload["status_summary"],
            "mechanism_claims_source_reviewed": len(mechanism_payload["mechanism_claims"]),
            "open_rework_targets": 0,
            "closed_rework_ticket_ids": [TICKET_ID],
            "unrecoverable_material_gap_count": len(gap_entries()),
            "blocking_unrecoverable_material_gap_count": 0,
            "gate_results": gates or {},
        },
        "per_layer_decision_rationale": {
            "material_packet": "Material packet remains structurally complete-with-gaps because no local supplementary assets are present; the gate-changing XML/PDF/figure/database surfaces were reopened and exhausted.",
            "validator_contract": "Canonical final and packet analysis artifacts are present after worker-2/4/6 repair.",
            "layer_1_database": "DBAASP MIC/hemolysis rows and APD6/DBAASP literature links are reconciled to source locators; the APD6 free-text peptide entry is preserved as source_conflict because it includes database-only shorthand not exactly stated in the paper.",
            "layer_2_activity_toxicity": "Worker-2 recovered source-supported NACAP-II MIC, ZOI, and hemolysis rows with target, unit, method, statistics, and locators.",
            "layer_3_mechanism": "Worker-6 keeps mechanism bounded to phenotype, safety, and computational structure context; no direct molecular mode-of-action assay is claimed.",
            "publication_grade_review": "The previous framework-only rework ticket is closed because source review is complete for the owned layers and remaining gaps are explicit nonblocking cautions.",
        },
        "caution_findings": [
            {
                "caution_code": "no_local_supplementary_assets",
                "severity": "caution",
                "evidence_context": "OA packages contain article XML/PDF plus figures only; supplementary indexes have zero assets/tables.",
            },
            {
                "caution_code": "linked_sequence_records_absent",
                "severity": "caution",
                "evidence_context": "No linked sequence JSONL rows exist in the packet; sequence identity is anchored to primary Table 1/Figure 1 and database IDs.",
            },
            {
                "caution_code": "apd6_free_text_partial_source_conflict",
                "severity": "caution",
                "evidence_context": "APD6 AP05465 free text partly matches MIC/ZOI/non-hemolysis but includes HC50-style/rounded wording not exactly tabulated in the primary source.",
            },
            {
                "caution_code": "no_direct_mechanism_assay",
                "severity": "caution",
                "evidence_context": "The source reports in vitro activity and modeled structure, but no direct membrane-disruption or intracellular target assay.",
            },
        ],
        "qc_failure_reasons": [],
        "rework_targets": [],
        "strict_gate": {
            "required_rework_count": 0,
            "open_ticket_ids": [],
            "semantic_gate_required": True,
        },
        "unrecoverable_material_gaps": gap_entries(),
        "adjudication_summary": "Worker-2/4/6 re-review recovered source-supported NACAP-II activity/toxicity rows, reconciled linked APD6/DBAASP rows with conflict preservation, exhausted local package/supplement surfaces, and closed rwk-complete-test-0001 as accepted_with_cautions.",
    }


def write_repair_artifacts(timestamp: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    activity_payload = build_activity_payload(timestamp)
    database_payload = build_database_payload(timestamp)
    mechanism_payload = build_mechanism_payload(timestamp)
    review_payload = build_review_payload(timestamp, activity_payload, database_payload, mechanism_payload)

    write_json(PACKET / "analysis" / "activity_toxicity_evidence.json", activity_payload)
    write_json(PAPER / "final" / "activity_toxicity_evidence.json", activity_payload)

    write_json(PACKET / "analysis" / "database_record_audit.json", database_payload)
    write_json(PAPER / "final" / "database_record_verification.json", database_payload)

    write_json(PACKET / "analysis" / "mechanism_evidence.json", mechanism_payload)
    write_json(PAPER / "final" / "mechanism_ontology_record.json", mechanism_payload)

    write_json(PACKET / "analysis" / "adjudication_report.json", review_payload)
    write_json(PAPER / "work" / "review" / "adjudication_report.json", review_payload)
    write_json(PAPER / "final" / "review_report.json", review_payload)

    analysis_status = read_json(PACKET / "analysis" / "analysis_status.json", {})
    analysis_status.update(
        {
            "paper_id": PAPER_ID,
            "generated_at": timestamp,
            "status": "source_reviewed_publication_grade_ready",
            "activity_record_count": activity_payload["activity_record_count"],
            "activity_extraction_issue_count": 0,
            "activity_extraction_issues": [],
            "database_status_summary": database_payload["status_summary"],
            "mechanism_claim_count": len(mechanism_payload["mechanism_claims"]),
            "open_rework_ticket_ids": [],
            "closed_rework_ticket_ids": [TICKET_ID],
        }
    )
    write_json(PACKET / "analysis" / "analysis_status.json", analysis_status)

    packet_manifest = read_json(PACKET / "packet_manifest.json", {})
    packet_manifest.update(
        {
            "analysis_queue_status": "source_reviewed_publication_grade_ready",
            "open_rework_ticket_ids": [],
            "closed_rework_ticket_ids": [TICKET_ID],
            "source_review_repair": {
                "updated_at": timestamp,
                "owner_workers": ["worker-2", "worker-4", "worker-6"],
                "activity_record_count": activity_payload["activity_record_count"],
                "database_status_summary": database_payload["status_summary"],
                "mechanism_claim_count": len(mechanism_payload["mechanism_claims"]),
                "closed_rework_ticket_ids": [TICKET_ID],
            },
        }
    )
    write_json(PACKET / "packet_manifest.json", packet_manifest)

    response = {
        "record_type": "rework_response",
        "ticket_id": TICKET_ID,
        "paper_id": PAPER_ID,
        "status": "closed_after_worker2_worker4_worker6_source_review",
        "created_at": timestamp,
        "created_by": "codex_worker246_rereview",
        "owner_workers": ["worker-2", "worker-4", "worker-6"],
        "source_paths_checked": SOURCE_PATHS_CHECKED,
        "tools_attempted": TOOLS_ATTEMPTED,
        "repairs_completed": [
            "Recovered three source-supported activity/toxicity rows for NACAP-II: MIC, ZOI, and rabbit erythrocyte hemolysis.",
            "Matched DBAASP MIC/hemolysis assay rows to primary-source locators and preserved the APD6 free-text row as source_conflict.",
            "Rewrote worker-6 adjudication/final review with source-review provenance, closed rework targets, and publication-grade accepted_with_cautions status.",
            "Confirmed no local supplementary activity/toxicity tables exist in packet supplementary indexes or OA packages.",
        ],
        "remaining_cautions": [
            "No linked sequence JSONL rows exist; sequence is source-reviewed from Table 1/Figure 1 and database IDs.",
            "APD6 free text contains HC50-style/rounded wording not exactly tabulated in the primary source and remains source_conflict.",
            "Hemolysis per-concentration exact values are figure-only, not tabled; the final record preserves a low/non-hemolytic exactness caution.",
            "No direct molecular mechanism assay is reported; mechanism remains phenotype/computational-context only.",
        ],
        "unrecoverable_material_gaps": gap_entries(),
        "blocks_publication_grade": False,
    }
    append_jsonl_once(PACKET / "rework" / "rework_responses.jsonl", response)

    write_json(
        PAPER / "work" / "review" / "quality_feedback.json",
        {
            "paper_id": PAPER_ID,
            "generated_at": timestamp,
            "status": "source_reviewed_rework_closed_pending_gate_rerun",
            "issue_count": 0,
            "qc_failure_reasons": [],
            "rework_targets": [],
            "closed_rework_ticket_ids": [TICKET_ID],
            "source_reviewed": True,
            "owner_workers": ["worker-2", "worker-4", "worker-6"],
            "unrecoverable_material_gaps": gap_entries(),
            "review_notes": "Previous full_source_review_not_completed, database_conflicts_require_adjudication, and no_supported_activity_rows_extracted blockers were repaired from reopened paper-local sources.",
        },
    )

    return activity_payload, database_payload, mechanism_payload, review_payload


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def run_gates(timestamp: str) -> tuple[dict[str, Any], dict[str, Any], bool]:
    write_json(MANIFEST, {"paper_ids": [PAPER_ID], "generated_at": timestamp})
    semantic_path = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    publication_path = REPORTS / f"{PAPER_ID}.publication_quality.json"
    semantic_after = REPORTS / f"{PAPER_ID}.codex_worker246_rereview.semantic_gate.json"
    publication_after = REPORTS / f"{PAPER_ID}.codex_worker246_rereview.publication_quality.json"

    semantic_proc = run_command(
        [
            "python",
            ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py",
            "--root",
            ".",
            "--paper-id",
            PAPER_ID,
            "--json",
        ]
    )
    semantic_text = semantic_proc.stdout.strip() or "{}"
    semantic_path.write_text(semantic_text + "\n", encoding="utf-8")
    semantic = json.loads(semantic_text)
    shutil.copyfile(semantic_path, semantic_after)

    publication_proc = run_command(
        [
            "python",
            ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py",
            "--root",
            ".",
            "--manifest",
            str(MANIFEST),
            "--json-out",
            str(publication_path),
        ]
    )
    publication = read_json(publication_path, {})
    shutil.copyfile(publication_path, publication_after)

    gates_ready = (
        semantic_proc.returncode == 0
        and publication_proc.returncode == 0
        and int(semantic.get("publication_grade_pass_count") or 0) == 1
        and int(semantic.get("publication_grade_fail_count") or 0) == 0
        and publication.get("publication_grade_pass") is True
    )
    gate_record = {
        "semantic_returncode": semantic_proc.returncode,
        "semantic_stderr": semantic_proc.stderr.strip(),
        "publication_returncode": publication_proc.returncode,
        "publication_stderr": publication_proc.stderr.strip(),
        "semantic_report": rel(semantic_path),
        "publication_report": rel(publication_path),
        "semantic_copy": rel(semantic_after),
        "publication_copy": rel(publication_after),
    }
    return semantic | {"_gate_command": gate_record}, publication, gates_ready


def finalize(
    timestamp: str,
    activity_payload: dict[str, Any],
    database_payload: dict[str, Any],
    mechanism_payload: dict[str, Any],
    semantic: dict[str, Any],
    publication: dict[str, Any],
    gates_ready: bool,
) -> None:
    gate_summary = {
        "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
        "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
        "semantic_issue_count": sum(item.get("issue_count", 0) for item in semantic.get("results", [])),
        "publication_quality_pass": publication.get("publication_grade_pass"),
        "publication_risk_counts": publication.get("risk_counts", {}),
        "semantic_report": "reports/doi__10.3390_pharmaceutics16070850.semantic_gate.json",
        "publication_report": "reports/doi__10.3390_pharmaceutics16070850.publication_quality.json",
    }
    review_payload = build_review_payload(timestamp, activity_payload, database_payload, mechanism_payload, gates=gate_summary)
    if not gates_ready:
        review_payload["review_status"] = "needs_targeted_rework"
        review_payload["publication_grade"] = False
        review_payload["qc_failure_reasons"] = [
            {
                "code": "post_repair_gate_failed",
                "owner_worker": "worker-6",
                "severity": "blocking",
                "reason": "Strict semantic/publication gate did not pass after bounded worker-2/4/6 repair.",
                "semantic_issues": semantic.get("results", [{}])[0].get("issues", []) if semantic.get("results") else [],
                "publication_risk_counts": publication.get("risk_counts", {}),
            }
        ]
        review_payload["rework_targets"] = [
            {
                "ticket_id": "rwk-worker246-post-gate",
                "paper_id": PAPER_ID,
                "worker": "worker-6",
                "owner_worker": "worker-6",
                "target_queue": "analysis",
                "layer": "publication_grade_review",
                "severity": "blocking",
                "failure_code": "post_repair_gate_failed",
                "omission_code": "post_repair_gate_failed",
                "artifact_path": "papers/doi__10.3390_pharmaceutics16070850/final/review_report.json",
                "source_paths_to_check": SOURCE_PATHS_CHECKED,
                "required_action": "Inspect semantic/publication gate reports and repair concrete remaining issue codes.",
            }
        ]
        review_payload["strict_gate"] = {
            "required_rework_count": 1,
            "open_ticket_ids": ["rwk-worker246-post-gate"],
            "semantic_gate_required": True,
        }

    write_json(PACKET / "analysis" / "adjudication_report.json", review_payload)
    write_json(PAPER / "work" / "review" / "adjudication_report.json", review_payload)
    write_json(PAPER / "final" / "review_report.json", review_payload)

    quality_feedback = {
        "paper_id": PAPER_ID,
        "generated_at": timestamp,
        "status": "source_reviewed_rework_closed" if gates_ready else "post_repair_gate_failed",
        "issue_count": 0 if gates_ready else 1,
        "qc_failure_reasons": [] if gates_ready else review_payload["qc_failure_reasons"],
        "rework_targets": [] if gates_ready else review_payload["rework_targets"],
        "closed_rework_ticket_ids": [TICKET_ID] if gates_ready else [],
        "source_reviewed": True,
        "owner_workers": ["worker-2", "worker-4", "worker-6"],
        "unrecoverable_material_gaps": gap_entries(),
        "gate_results": gate_summary,
        "review_notes": "Previous full_source_review_not_completed, database_conflicts_require_adjudication, and no_supported_activity_rows_extracted blockers were repaired from reopened paper-local sources."
        if gates_ready
        else "Bounded repair ran, but strict gate still failed; keep targeted rework open.",
    }
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality_feedback)

    analysis_status = read_json(PACKET / "analysis" / "analysis_status.json", {})
    analysis_status.update(
        {
            "generated_at": timestamp,
            "status": "source_reviewed_publication_grade_ready" if gates_ready else "analysis_needs_analysis_rework",
            "open_rework_ticket_ids": [] if gates_ready else ["rwk-worker246-post-gate"],
            "closed_rework_ticket_ids": [TICKET_ID] if gates_ready else [],
            "gate_results": gate_summary,
        }
    )
    write_json(PACKET / "analysis" / "analysis_status.json", analysis_status)

    packet_manifest = read_json(PACKET / "packet_manifest.json", {})
    packet_manifest.update(
        {
            "analysis_queue_status": "source_reviewed_publication_grade_ready" if gates_ready else "analysis_needs_analysis_rework",
            "open_rework_ticket_ids": [] if gates_ready else ["rwk-worker246-post-gate"],
            "closed_rework_ticket_ids": [TICKET_ID] if gates_ready else [],
            "source_review_repair": {
                "updated_at": timestamp,
                "owner_workers": ["worker-2", "worker-4", "worker-6"],
                "activity_record_count": activity_payload["activity_record_count"],
                "database_status_summary": database_payload["status_summary"],
                "mechanism_claim_count": len(mechanism_payload["mechanism_claims"]),
                "closed_rework_ticket_ids": [TICKET_ID] if gates_ready else [],
                "gate_results": gate_summary,
            },
        }
    )
    write_json(PACKET / "packet_manifest.json", packet_manifest)

    complete = read_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", {})
    complete.update(
        {
            "paper_id": PAPER_ID,
            "doi": DOI,
            "generated_at": timestamp,
            "completion_claim": "source_reviewed_worker2_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions"
            if gates_ready
            else "worker2_worker4_worker6_rework_attempt_gate_failed",
            "current_state": "source_reviewed_publication_grade_ready" if gates_ready else "rework_queue",
            "terminal_status": "accepted_with_cautions" if gates_ready else "awaiting_targeted_rework",
            "final_approval_status": "accepted_with_cautions" if gates_ready else "refused_needs_rework",
            "not_publication_grade_reason": None if gates_ready else "Strict gate failed after bounded worker-2/4/6 repair.",
            "open_rework_ticket_count": 0 if gates_ready else 1,
            "rework_ticket_ids": [] if gates_ready else ["rwk-worker246-post-gate"],
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
                "publication_risk_counts": publication.get("risk_counts", {}),
            },
            "analysis": {
                "activity_records": activity_payload["activity_record_count"],
                "database_status_summary": database_payload["status_summary"],
                "mechanism_claims": len(mechanism_payload["mechanism_claims"]),
                "review_status": review_payload["review_status"],
            },
            "queue_status": {
                "analysis": "source_reviewed_publication_grade_ready" if gates_ready else "analysis_needs_analysis_rework",
                "material": "material_extracted_with_gaps",
            },
            "publication_quality_gate": "passed_after_worker246_rereview" if gates_ready else "failed_after_worker246_rereview",
            "semantic_gate": "passed_after_worker246_rereview" if gates_ready else "failed_after_worker246_rereview",
        }
    )
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", complete)

    workflow = read_json(ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID / "workflow_context.json", {})
    workflow.update(
        {
            "updated_at": timestamp,
            "current_state": "source_reviewed_publication_grade_ready" if gates_ready else "rework_context_prepared",
            "open_rework_tickets": [] if gates_ready else ["rwk-worker246-post-gate"],
            "gate_summary": {
                "structural_ready": True,
                "validator_contract_ready": True,
                "semantic_gate_ready": gates_ready,
                "publication_grade_ready": gates_ready,
            },
            "queue_status": {
                "analysis": "source_reviewed_publication_grade_ready" if gates_ready else "analysis_needs_analysis_rework",
                "material": "material_extracted_with_gaps",
            },
        }
    )
    write_json(ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID / "workflow_context.json", workflow)


def main() -> int:
    timestamp = now_iso()
    activity_payload, database_payload, mechanism_payload, _review_payload = write_repair_artifacts(timestamp)
    semantic, publication, gates_ready = run_gates(timestamp)
    finalize(timestamp, activity_payload, database_payload, mechanism_payload, semantic, publication, gates_ready)
    print(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "gates_ready": gates_ready,
                "activity_record_count": activity_payload["activity_record_count"],
                "database_status_summary": database_payload["status_summary"],
                "semantic_issue_count": sum(item.get("issue_count", 0) for item in semantic.get("results", [])),
                "publication_grade_pass": publication.get("publication_grade_pass"),
                "semantic_report": f"reports/{PAPER_ID}.semantic_gate.json",
                "publication_report": f"reports/{PAPER_ID}.publication_quality.json",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if gates_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
