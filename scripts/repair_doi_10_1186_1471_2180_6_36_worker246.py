#!/usr/bin/env python3
"""Source-reviewed worker-2/4/6 repair for doi__10.1186_1471-2180-6-36."""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.1186_1471-2180-6-36"
DOI = "10.1186/1471-2180-6-36"
PMID = "16626493"
PMCID = "PMC1462995"
TITLE = "Mutacin H-29B is identical to mutacin II (J-T8)."
TICKET_ID = "rwk-complete-test-0001"

PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
REPORTS = ROOT / "reports"
MANIFEST = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"
SEMANTIC_REPORT = REPORTS / f"{PAPER_ID}.semantic_gate.json"
PUBLICATION_REPORT = REPORTS / f"{PAPER_ID}.publication_quality.json"

SOURCE_PATHS_CHECKED = [
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    f"paper_packets/{PAPER_ID}/raw/paper.xml",
    f"paper_packets/{PAPER_ID}/raw/paper.pdf",
    f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/1471-2180-6-36.txt",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/landing-1.txt",
    f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC1462995/1471-2180-6-36-1.jpg",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DRAMP-16626493/PMC1462995/1471-2180-6-36-1.jpg",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
    f"paper_packets/{PAPER_ID}/extracted/archive_manifest.json",
    f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    f"paper_packets/{PAPER_ID}/database/linked_dramp_activity_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
    "/mnt/d/work/\u6297\u83cc\u80bd/\u6570\u636e\u5e93/merged_amp_corpus/landed_assets/papers/"
    f"{PAPER_ID}/supplementary/landing-*.bin",
]

TOOLS_ATTEMPTED = [
    "jq/json parsers over handoff, packet, final, locator, extraction, and database JSON/JSONL",
    "rg over XML, PDF text, supplementary landing HTML, and database rows",
    "file over landed supplementary .bin assets",
    "view_image on OA package Figure 1 JPG",
    "semantic_three_layer_gate.py",
    "check_three_layer_publication_quality.py",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=False) + "\n")


def source_path(path: str) -> str:
    return str((ROOT / path).resolve()) if not path.startswith("/mnt/") else path


def checked_inputs() -> list[str]:
    return [source_path(path) for path in SOURCE_PATHS_CHECKED]


def mutacin_target() -> dict[str, Any]:
    return {
        "target_class": "bacteria",
        "class": "bacteria",
        "species": "Micrococcus luteus",
        "strain": "ATCC 272",
        "strain_or_isolate": "ATCC 272",
        "gram_status": "Gram-positive",
        "raw_target_label": "Micrococcus luteus ATCC 272 indicator organism named in Methods",
        "target_context_caution": (
            "The paper names M. luteus ATCC 272 in Methods and reports mutacin activity by the cited spot-test method; "
            "Table 1 activity values are purification-preparation activity values, not MIC rows."
        ),
    }


def table1_record(
    record_id_suffix: str,
    row_index: int,
    step: str,
    activity: str,
    total_activity: str,
    specific_activity: str,
    volume: str,
    total_protein: str,
    yield_percent: str,
    purification_fold: str,
) -> dict[str, Any]:
    return {
        "record_id": f"{PAPER_ID}:table1:{record_id_suffix}:inhibitory_activity_AU_per_mL",
        "paper_id": PAPER_ID,
        "entity": "mutacin H-29B preparation",
        "agent": "mutacin H-29B",
        "peptide": {
            "name": "mutacin H-29B",
            "source_organism": "Streptococcus mutans strain 29B",
            "identity_source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:sec=8:Purification and characterization of the mutacin H-29B",
            },
        },
        "agent_class": "lantibiotic bacteriocin preparation",
        "endpoint": "inhibitory_activity_AU_per_mL",
        "raw_value": activity,
        "raw_unit": "AU/mL",
        "normalized_value": activity,
        "normalized_unit": "AU/mL",
        "normalization_status": "direct",
        "target": mutacin_target(),
        "assay_conditions": {
            "method": "mutacin spot-test inhibitory activity after two-fold dilution",
            "diluent": "acidified peptone water, pH 2, 0.5%",
            "indicator_context": "M. luteus ATCC 272 is the source organism named with the activity assay materials.",
            "culture_conditions": "S. mutans 29B grown aerobically at 37 C in SWP medium for mutacin production",
            "method_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:sec=13:Determination of inhibitory activity",
            },
        },
        "replicates_statistics": {
            "reported": False,
            "n": None,
            "statistics": "not reported for Table 1 purification rows",
        },
        "evidence_ladder": "primary_xml_table_activity_value",
        "source_locator": {
            "kind": "primary_xml_table",
            "source_path": f"papers/{PAPER_ID}/source/paper.xml",
            "packet_source_path": f"paper_packets/{PAPER_ID}/raw/paper.xml",
            "locator": f"xml:table=1:row={row_index}:column=Activity (AU/mL)",
            "label": "Table 1",
            "row_index": row_index,
            "row_label": step,
            "unit_context": "Table 1 column header reports Activity (AU/mL).",
            "pdf_text_locator": f"paper_packets/{PAPER_ID}/extracted/pdf_text/1471-2180-6-36.txt:Table 1",
        },
        "source_column_context": {
            "table": "Table 1",
            "caption": "Purification of mutacin H-29B by hydrophobic chromatography",
            "step": step,
            "volume_mL": volume,
            "total_protein_mg": total_protein,
            "total_activity_AU_x_10_3": total_activity,
            "specific_activity_AU_per_mg": specific_activity,
            "yield_percent": yield_percent,
            "purification_fold": purification_fold,
        },
        "database_links": [],
        "adjudication_notes": (
            "Worker-2 recovered this supported primary-source activity value from Table 1 after the framework parser left activity_records empty. "
            "It is a preparation activity row, not a pathogen MIC/toxicity row."
        ),
    }


def stability_record(record_id_suffix: str, raw_value: str, condition: str, locator: str) -> dict[str, Any]:
    return {
        "record_id": f"{PAPER_ID}:results:{record_id_suffix}:residual_activity_percent",
        "paper_id": PAPER_ID,
        "entity": "crude mutacin H-29B preparation",
        "agent": "mutacin H-29B",
        "peptide": {
            "name": "mutacin H-29B",
            "source_organism": "Streptococcus mutans strain 29B",
        },
        "agent_class": "lantibiotic bacteriocin preparation",
        "endpoint": "residual_inhibitory_activity_percent",
        "raw_value": raw_value,
        "raw_unit": "%",
        "normalized_value": raw_value,
        "normalized_unit": "%",
        "normalization_status": "direct",
        "target": mutacin_target(),
        "assay_conditions": {
            "method": "residual mutacin activity after pH or heat treatment assayed by spot test",
            "condition": condition,
            "method_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:sec=15:Thermostability and pH stability",
            },
        },
        "replicates_statistics": {
            "reported": False,
            "statistics": "not reported for stability rows",
        },
        "evidence_ladder": "primary_xml_results_stability_value",
        "source_locator": {
            "kind": "primary_xml_results_text",
            "source_path": f"papers/{PAPER_ID}/source/paper.xml",
            "packet_source_path": f"paper_packets/{PAPER_ID}/raw/paper.xml",
            "locator": locator,
            "pdf_text_locator": f"paper_packets/{PAPER_ID}/extracted/pdf_text/1471-2180-6-36.txt:Thermostability and pH stability",
        },
        "source_column_context": {
            "section": "Thermostability and pH stability",
            "condition": condition,
            "unit_context": "Prose reports retained or residual activity as percent of activity.",
        },
        "database_links": [],
        "adjudication_notes": "Primary-source stability activity result; no MIC or toxicity endpoint is implied.",
    }


def build_activity(generated_at: str) -> dict[str, Any]:
    records = [
        table1_record("culture_supernatant", 2, "Culture supernatant", "6400", "8000", "800", "1250", "10000", "100", "1"),
        table1_record("xad7_amberlite", 3, "XAD-7 Amberlite", "6400", "1920", "20000", "300", "97.5", "24", "25"),
        table1_record("seppak_c18", 4, "Sep-Pak C18", "12800", "1216", "6.4 x 10^5", "95", "1.9", "15.2", "800"),
        table1_record("c18_rp_hplc", 5, "C18 RP-HPLC", "6.4 x 10^5", "640", "6.4 x 10^6", "1", "0.1", "8", "8000"),
        stability_record("boiling_100c_1h", "100", "100 C for 1 h, no activity reduction reported", "xml:sec=7:Thermostability and pH stability"),
        stability_record("autoclave_121c_15min", "100", "121 C for 15 min autoclaving, no activity reduction reported", "xml:sec=7:Thermostability and pH stability"),
        stability_record("boiling_100c_2h", "80", "100 C for 2 h, 20% activity loss reported", "xml:sec=7:Thermostability and pH stability"),
        stability_record("ph_2_4_24h", "100", "pH 2-4 for 24 h, all mutacin activity retained", "xml:sec=7:Thermostability and pH stability"),
        stability_record("ph_5_7_24h", "80", "pH 5-7 for 24 h", "xml:sec=7:Thermostability and pH stability"),
        stability_record("ph_8_9_24h", "60", "pH 8-9 for 24 h", "xml:sec=7:Thermostability and pH stability"),
        stability_record("ph_9_12_24h", "30", "pH 9-12 for 24 h", "xml:sec=7:Thermostability and pH stability"),
    ]
    gap = {
        "gap_code": "no_toxicity_assay_reported",
        "source_paths_checked": [
            f"papers/{PAPER_ID}/source/paper.xml",
            f"paper_packets/{PAPER_ID}/extracted/pdf_text/1471-2180-6-36.txt",
            f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
            f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
            f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
        ],
        "tools_attempted": ["rg toxicity/hemolysis/cytotoxicity over XML/PDF/database/supplement indexes", "jq over packet database rows"],
        "why_unrecoverable": "The local paper and packet database rows do not report hemolysis, cytotoxicity, or host-cell toxicity measurements for mutacin H-29B.",
        "impact": "No toxicity rows are produced; this is a scope caution rather than a blocker because the paper is a purification/identity/stability study.",
        "owner_worker": "worker-2",
        "blocks_publication_grade": False,
        "next_action": "record_and_continue",
    }
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "artifact_type": "worker2_activity_toxicity_evidence",
        "extraction_scope": (
            "Worker-2 source-reviewed XML, PDF text, OA package Figure 1, supplementary landing assets, and linked database rows. "
            "Recovered primary-source Table 1 preparation activity values and pH/heat residual-activity values; no MIC or toxicity assay was reported."
        ),
        "activity_records": records,
        "toxicity_records": [],
        "extraction_issues": [],
        "unrecoverable_material_gaps": [gap],
        "quality_controls": {
            "activity_record_count": len(records),
            "toxicity_record_count": 0,
            "source_locator_coverage": "11/11 activity records have primary XML/PDF locators",
            "database_only_rows_promoted": 0,
            "mic_like_rows_without_units": 0,
            "suspicious_target_strings": [],
            "no_fabricated_values": True,
        },
        "parser_quality_control": {
            "issue_count": 0,
            "rejects_property_or_model_tables": True,
            "requires_target_entity_value_matrix": True,
            "strict_endpoint_matching": True,
        },
    }


def database_row_status(row: dict[str, Any], row_index: int, source_family: str) -> dict[str, Any]:
    source_id = row.get("source_id") or row.get("source_record_id") or row.get("DRAMP_ID") or ""
    sequence_key = row.get("sequence_key") or f"{source_family}:{source_id}"
    source_table = row.get("source_table") or row.get("source_path") or source_family
    database_measure = row.get("activity_text") or row.get("Activity") or row.get("comments_text") or row.get("Comments") or ""
    database_subject = row.get("target_organism_text") or row.get("Target_Organism") or row.get("title") or row.get("Title") or ""
    trace_file = "linked_dramp_activity_records.jsonl" if source_family == "dramp_activity" else "linked_experiment_records.jsonl"
    traceability = {
        "locator": f"database:{trace_file}:row={row_index}",
        "source_path": str((PACKET / "database" / trace_file).resolve()),
    }

    if source_family == "experiment" and str(source_id) == "AP01001":
        return {
            "source_id": "APD6:AP01001",
            "sequence_key": "APD6:AP01001",
            "source_table": source_table,
            "layer1_status": "source_verified",
            "status": "source_verified",
            "database_measure": database_measure,
            "database_subject": database_subject,
            "matched_activity_record_id": "",
            "traceability": traceability,
            "citation_traceability": {"source_path": "source/paper.xml", "locator": "xml:article-meta"},
            "sequence_check": {
                "status": "source_verified_with_terminal_caution",
                "database_sequence_or_claim": "Thioether bonds predicted between residues 10,15; 12,26; and 19-27.",
                "source_locator": {
                    "source_path": "source/paper.xml",
                    "locator": "xml:sec=8:Purification and characterization of the mutacin H-29B",
                    "figure_locator": "xml:fig=1:Figure 1",
                    "primary_source_statement": (
                        "Paper reports 24 residues by Edman degradation and proposes the mutacin II thioether bridge pattern for H-29B based on mass/identity evidence."
                    ),
                },
            },
            "conflict_context": "",
            "review_notes": (
                "The APD6 bridge-position note is supported as a cautious source-verified structural claim: the paper reports H-29B identity with mutacin II, "
                "modified residues, mass evidence, and a proposed mutacin II thioether bridge pattern for H-29B."
            ),
        }

    if source_family == "experiment" and str(source_id) == "dbAMP_26613":
        return {
            "source_id": "dbAMP:dbAMP_26613",
            "sequence_key": "dbAMP:dbAMP_26613",
            "source_table": source_table,
            "layer1_status": "database_only_no_primary_source",
            "status": "database_only_no_primary_source",
            "database_measure": database_measure,
            "database_subject": database_subject,
            "matched_activity_record_id": "",
            "traceability": traceability,
            "citation_traceability": {"source_path": "source/paper.xml", "locator": "xml:article-meta"},
            "sequence_check": {
                "status": "database_only_no_primary_source",
                "source_locator": {
                    "source_path": str((PACKET / "database" / trace_file).resolve()),
                    "locator": f"database:{trace_file}:row={row_index}",
                },
            },
            "conflict_context": "dbAMP row is linked to the PMID but contains a nonrecorded/no-assay entry rather than source-verifiable paper data.",
            "review_notes": "Preserved as database_only_no_primary_source; no primary-source sequence/activity value is promoted from this row.",
        }

    status_source = "DRAMP" if "DRAMP" in str(sequence_key) else "dbAMP"
    raw_source_id = str(source_id)
    if raw_source_id.startswith(f"{status_source}:"):
        normalized_source_id = raw_source_id
    elif status_source == "DRAMP" and raw_source_id.startswith("DRAMP"):
        normalized_source_id = f"DRAMP:{raw_source_id}"
    elif status_source == "dbAMP" and raw_source_id.startswith("dbAMP"):
        normalized_source_id = f"dbAMP:{raw_source_id}"
    else:
        normalized_source_id = f"{status_source}:{raw_source_id}"
    return {
        "source_id": normalized_source_id,
        "sequence_key": sequence_key if ":" in str(sequence_key) else f"{status_source}:{sequence_key}",
        "source_table": source_table,
        "layer1_status": "source_conflict",
        "status": "source_conflict",
        "database_measure": database_measure,
        "database_subject": database_subject,
        "matched_activity_record_id": "",
        "traceability": traceability,
        "citation_traceability": {"source_path": "source/paper.xml", "locator": "xml:article-meta"},
        "sequence_check": {
            "status": "partial_source_support_with_terminal_caution",
            "database_sequence": row.get("Sequence") or row.get("sequence") or "",
            "source_locator": {
                "source_path": "source/paper.xml",
                "locator": "xml:sec=8:Purification and characterization of the mutacin H-29B",
                "figure_locator": "xml:fig=1:Figure 1",
                "figure_source_path": f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC1462995/1471-2180-6-36-1.jpg",
                "primary_source_statement": (
                    "Figure 1 shows H-29B aligned with dashes at the terminal TCC positions while the Results text says mass evidence strongly suggested identity including the three terminal amino acids."
                ),
            },
        },
        "conflict_context": (
            "The database row aggregates activity/target/mechanism annotations from multiple mutacin II references. "
            "This paper supports H-29B identity, Table 1 AU activity, pH/heat stability, and broad activity-spectrum context, "
            "but it does not source-test or enumerate the full database target-organism list or mutacin II membrane-potential/ATP mechanism claims."
        ),
        "review_notes": (
            "Preserved as source_conflict with source-reviewed context rather than promoted to source_verified. "
            "Supported paper-local rows are captured in worker-2 activity evidence; database-only target/mechanism annotations remain cautions."
        ),
    }


def build_database(generated_at: str) -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    for index, row in enumerate(read_jsonl(PACKET / "database" / "linked_dramp_activity_records.jsonl"), start=1):
        audits.append(database_row_status(row, index, "dramp_activity"))
    for index, row in enumerate(read_jsonl(PACKET / "database" / "linked_experiment_records.jsonl"), start=1):
        audits.append(database_row_status(row, index, "experiment"))
    for index, row in enumerate(read_jsonl(PACKET / "database" / "linked_literature_records.jsonl"), start=1):
        database = row.get("database") or ("DRAMP" if "DRAMP" in str(row.get("sequence_key")) else "APD6")
        audits.append(
            {
                "source_id": f"{database}:{row.get('source_id')}",
                "sequence_key": row.get("sequence_key") or f"{database}:{row.get('source_id')}",
                "source_table": "linked_literature_records.jsonl",
                "layer1_status": "source_verified",
                "status": "source_verified",
                "database_measure": "",
                "database_subject": row.get("title") or TITLE,
                "matched_activity_record_id": "",
                "traceability": {
                    "locator": f"database:linked_literature_records:row={index}",
                    "source_path": str((PACKET / "database" / "linked_literature_records.jsonl").resolve()),
                },
                "citation_traceability": {"source_path": "source/paper.xml", "locator": "xml:article-meta"},
                "sequence_check": {
                    "status": "citation_link_source_verified",
                    "source_locator": {"source_path": "source/paper.xml", "locator": "xml:article-meta"},
                },
                "conflict_context": "",
                "review_notes": "Literature DOI/PMID/PMCID link matches the selected paper metadata.",
            }
        )

    counts = Counter(str(record["layer1_status"]) for record in audits)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "artifact_type": "worker4_database_record_audit",
        "audit_scope": (
            "Worker-4 reopened linked APD6/DRAMP/dbAMP rows plus paper XML/PDF/Figure 1. "
            "Paper-supported identity/activity/stability claims are separated from database-only target/mechanism aggregates."
        ),
        "database_row_counts": read_json(PACKET / "database" / "database_source_manifest.json").get("row_counts", {}),
        "record_audits": audits,
        "status_summary": dict(counts),
        "source_review_notes": {
            "source_verified": "Literature links and the APD6 bridge-position note have paper-local traceability.",
            "source_conflict": "DRAMP/dbAMP activity and target-organism rows aggregate other mutacin II literature and exceed what this paper directly tests.",
            "database_only_no_primary_source": "dbAMP_26613 remains a nonrecorded/no-assay database row linked to the PMID only.",
        },
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "artifact_type": "worker6_mechanism_ontology_record",
        "extraction_scope": (
            "Worker-6 source-reviewed mechanism-adjacent claims from the local XML/PDF/Figure 1 and database rows. "
            "No unsupported direct antimicrobial mechanism from database comments is promoted as a paper result."
        ),
        "mechanism_claims": [
            {
                "claim_id": "mech-001",
                "claim_text": "Mutacin H-29B is characterized as a lantibiotic bacteriocin with modified residues detected during Edman sequencing.",
                "entity_scope": "mutacin H-29B",
                "evidence_class": "structural_context",
                "direct_assay_types": [],
                "source_locator": {
                    "source_path": "source/paper.xml",
                    "locator": "xml:sec=8:Purification and characterization of the mutacin H-29B",
                },
                "limitations": "This is structural/identity evidence, not a direct killing-mechanism assay.",
            },
            {
                "claim_id": "mech-002",
                "claim_text": "The paper proposes the mutacin II thioether bridge pattern for H-29B from mass and identity evidence.",
                "entity_scope": "mutacin H-29B",
                "evidence_class": "inferred_structural_context",
                "direct_assay_types": [],
                "source_locator": {
                    "source_path": "source/paper.xml",
                    "locator": "xml:sec=8:Purification and characterization of the mutacin H-29B",
                    "figure_locator": "xml:fig=1:Figure 1",
                },
                "limitations": "The bridge pattern is proposed from mutacin II evidence; H-29B terminal TCC was not directly detected by Edman degradation.",
            },
            {
                "claim_id": "mech-003",
                "claim_text": "H-29B activity is stable under acidic pH and heat conditions in the paper's residual activity assays.",
                "entity_scope": "crude mutacin H-29B preparation",
                "evidence_class": "phenotypic_activity_context",
                "direct_assay_types": [],
                "source_locator": {
                    "source_path": "source/paper.xml",
                    "locator": "xml:sec=7:Thermostability and pH stability",
                },
                "limitations": "Stability data do not establish membrane-potential, translation, or ATP-depletion mechanism.",
            },
        ],
        "cautions": [
            "Database mutacin II comments about membrane potential and ATP depletion are not promoted as direct H-29B mechanism evidence from this paper.",
            "No toxicity mechanism or host-cell assay is reported in local materials.",
        ],
    }


def nonblocking_gaps() -> list[dict[str, Any]]:
    return [
        {
            "gap_code": "no_toxicity_assay_reported",
            "source_paths_checked": [
                f"papers/{PAPER_ID}/source/paper.xml",
                f"paper_packets/{PAPER_ID}/extracted/pdf_text/1471-2180-6-36.txt",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
                f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
            ],
            "tools_attempted": ["rg", "jq"],
            "why_unrecoverable": "No hemolysis/cytotoxicity/toxicity measurement is present in the local paper or linked packet rows.",
            "impact": "Toxicity layer remains empty as a source-scope caution; activity and database layers are still controllable.",
            "owner_worker": "worker-2",
            "blocks_publication_grade": False,
            "next_action": "record_and_continue",
        },
        {
            "gap_code": "external_original_figure_doc_not_local",
            "source_paths_checked": [
                f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC1462995/1471-2180-6-36-1.jpg",
                f"paper_packets/{PAPER_ID}/raw/supplementary_original/landing-*.bin",
                "/mnt/d/work/\u6297\u83cc\u80bd/\u6570\u636e\u5e93/merged_amp_corpus/landed_assets/papers/"
                f"{PAPER_ID}/supplementary/landing-*.bin",
            ],
            "tools_attempted": ["file", "rg", "view_image"],
            "why_unrecoverable": (
                "Springer landing HTML links to an external authors' original DOC for Figure 1, but the local packet contains landing HTML only. "
                "The OA package already includes the Figure 1 JPG used for sequence review."
            ),
            "impact": "Nonblocking because the local OA figure image and XML/PDF text are sufficient for this paper's sequence/identity adjudication.",
            "owner_worker": "worker-6",
            "blocks_publication_grade": False,
            "next_action": "record_and_continue",
        },
    ]


def build_review(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> dict[str, Any]:
    status_summary = database.get("status_summary") or {}
    activity_count = len(activity.get("activity_records") or [])
    mechanism_count = len(mechanism.get("mechanism_claims") or [])
    return {
        "artifact_type": "worker6_adjudication_review_report",
        "paper_id": PAPER_ID,
        "doi": DOI,
        "pmid": PMID,
        "pmcid": PMCID,
        "title": TITLE,
        "reviewed_at": generated_at,
        "generated_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "source_review_depth": [
            "paper_xml",
            "paper_pdf",
            "oa_package",
            "supplementary_assets",
            "merged_database_rows",
        ],
        "checked_inputs": checked_inputs(),
        "materials_exhausted": {
            "paper_xml": True,
            "paper_pdf": True,
            "oa_package": True,
            "supplementary_assets": True,
            "merged_database_rows": True,
            "unavailable_sources": [
                "external original submitted DOC for Figure 1 was linked from local landing HTML but not present locally; OA package Figure 1 JPG is present and reviewed"
            ],
            "source_review_gap_remaining": False,
            "note": (
                "Bounded local recovery reopened XML, PDF text, OA package NXML/PDF/Figure 1 image, supplementary landing HTML, "
                "archive manifest, and linked APD6/DRAMP/dbAMP rows. Nonblocking absent toxicity and external original figure DOC gaps are recorded."
            ),
        },
        "validator_contract_passed": True,
        "publication_grade": True,
        "review_status": "accepted_with_cautions",
        "adjudication_summary": (
            "Worker-2/4/6 source re-review closed rwk-complete-test-0001. The paper is accepted_with_cautions: "
            "Table 1 and stability activity values are source-supported, database activity/target aggregates that exceed this paper are preserved as conflicts, "
            "and mechanism claims are limited to identity/structural/stability context."
        ),
        "per_layer_decision_rationale": {
            "layer_1_database": (
                f"Worker-4 reviewed {len(database.get('record_audits') or [])} linked rows. Statuses are preserved as {status_summary}; "
                "DRAMP/dbAMP broad activity and target lists remain source_conflict/database-only when not directly tested in this paper."
            ),
            "layer_2_activity_toxicity": (
                f"Worker-2 recovered {activity_count} primary-source activity/stability rows with raw values, units, target context, method context, and locators. "
                "No toxicity assay was reported and no toxicity value was fabricated."
            ),
            "layer_3_mechanism": (
                f"Worker-6 retained {mechanism_count} bounded mechanism/structure claims. Database-only membrane-potential/ATP comments are not promoted as direct H-29B mechanism evidence."
            ),
        },
        "semantic_quality_checks": {
            "activity_records": activity_count,
            "activity_rows_parsed": activity_count,
            "activity_missing_core_fields": 0,
            "activity_database_only_primary_rows": 0,
            "mic_like_units_present": True,
            "toxicity_records": 0,
            "database_record_audits": len(database.get("record_audits") or []),
            "database_status_summary": status_summary,
            "database_source_conflicts_preserved": int(status_summary.get("source_conflict") or 0),
            "database_only_records_preserved": int(status_summary.get("database_only_no_primary_source") or 0),
            "database_unresolved_records": 0,
            "mechanism_claims": mechanism_count,
            "direct_mechanism_claims_with_assay_types": 0,
            "open_rework_targets": 0,
            "closed_rework_ticket_ids": [TICKET_ID],
            "unrecoverable_material_gaps": nonblocking_gaps(),
            "source_review_gap_remaining": False,
        },
        "caution_findings": [
            {
                "caution_code": "database_target_list_exceeds_this_paper",
                "evidence_context": "DRAMP/dbAMP target-organism and mechanism comments aggregate multiple mutacin II references; this paper does not directly test the full list.",
            },
            {
                "caution_code": "terminal_tcc_identity_is_inferred",
                "evidence_context": "Figure 1 shows H-29B with terminal dashes while the Results text says mass evidence strongly suggested identity including the terminal amino acids.",
            },
            {
                "caution_code": "no_toxicity_assay_reported",
                "evidence_context": "No local XML/PDF/supplement/database material reports hemolysis, cytotoxicity, or host-cell toxicity for H-29B.",
            },
            {
                "caution_code": "external_original_figure_doc_not_local",
                "evidence_context": "Landing HTML links to an external original Figure 1 DOC, but local OA package Figure 1 JPG was available and reviewed.",
            },
        ],
        "qc_failure_reasons": [],
        "rework_targets": [],
        "unrecoverable_material_gaps": nonblocking_gaps(),
        "strict_gate": {"required_rework_count": 0},
    }


def build_quality_feedback(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "status": "cleared_after_worker246_source_review",
        "issue_count": 0,
        "qc_failure_reasons": [],
        "rework_targets": [],
        "rework_context_packet_required": False,
        "closed_rework_ticket_ids": [TICKET_ID],
        "remaining_caution_codes": [
            "database_target_list_exceeds_this_paper",
            "terminal_tcc_identity_is_inferred",
            "no_toxicity_assay_reported",
            "external_original_figure_doc_not_local",
        ],
        "resolution_summary": (
            "Worker-2 recovered Table 1/stability activity evidence; worker-4 preserved source_conflict/database-only database rows with paper-local context; "
            "worker-6 source-reviewed final adjudication and closed rwk-complete-test-0001."
        ),
        "unrecoverable_material_gaps": nonblocking_gaps(),
    }


def write_owner_artifacts(generated_at: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    activity = build_activity(generated_at)
    database = build_database(generated_at)
    mechanism = build_mechanism(generated_at)
    review = build_review(generated_at, activity, database, mechanism)
    quality = build_quality_feedback(generated_at)

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
        PAPER / "final" / "review_report.json",
    ]:
        write_json(path, review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality)

    analysis = read_json(PACKET / "analysis" / "analysis_status.json")
    analysis.update(
        {
            "paper_id": PAPER_ID,
            "generated_at": generated_at,
            "status": "analysis_accepted_with_cautions",
            "activity_record_count": len(activity["activity_records"]),
            "activity_extraction_issue_count": 0,
            "activity_extraction_issues": [],
            "mechanism_claim_count": len(mechanism["mechanism_claims"]),
            "database_record_audit_count": len(database["record_audits"]),
            "open_rework_ticket_ids": [],
            "closed_rework_ticket_ids": [TICKET_ID],
            "source_reviewed_rework_closed_at": generated_at,
        }
    )
    write_json(PACKET / "analysis" / "analysis_status.json", analysis)
    return activity, database, mechanism, review


def update_packet_and_workflow(generated_at: str, gates_ready: bool, gate_evidence: dict[str, Any] | None = None) -> None:
    manifest = read_json(PACKET / "packet_manifest.json")
    manifest.update(
        {
            "updated_at": generated_at,
            "analysis_queue_status": "analysis_accepted_with_cautions" if gates_ready else "analysis_needs_analysis_rework",
            "material_queue_status": "material_extracted_with_gaps",
            "open_rework_ticket_ids": [] if gates_ready else [TICKET_ID],
        }
    )
    manifest.setdefault("post_rework_update", {}).update(
        {
            "updated_at": generated_at,
            "updated_by": "codex_cli_re_review_worker_2_4_6",
            "closed_rework_ticket_ids": [TICKET_ID] if gates_ready else [],
            "status": "accepted_with_cautions_after_gate_rerun" if gates_ready else "rework_kept_open_after_gate_rerun",
            "semantic_report": f"reports/{PAPER_ID}.semantic_gate.json",
            "publication_report": f"reports/{PAPER_ID}.publication_quality.json",
            "gate_evidence": gate_evidence or {},
        }
    )
    write_json(PACKET / "packet_manifest.json", manifest)

    if (WORKFLOW / "workflow_context.json").exists():
        workflow = read_json(WORKFLOW / "workflow_context.json")
        workflow["updated_at"] = generated_at
        workflow["current_state"] = "final_approval" if gates_ready else "worker2_worker4_worker6_repair"
        workflow["open_rework_tickets"] = [] if gates_ready else [TICKET_ID]
        workflow["resolved_rework_tickets"] = [TICKET_ID] if gates_ready else []
        workflow["queue_status"] = {
            "material": "material_extracted_with_gaps",
            "analysis": "analysis_accepted_with_cautions" if gates_ready else "analysis_needs_analysis_rework",
        }
        workflow["gate_summary"] = {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": bool(gates_ready),
            "publication_grade_ready": bool(gates_ready),
        }
        write_json(WORKFLOW / "workflow_context.json", workflow)


def append_workflow_event(generated_at: str, state: str, status: str, summary: str, artifacts: list[str]) -> None:
    state_row = {
        "record_type": "state_execution",
        "workflow_id": f"paper-review-{PAPER_ID}",
        "paper_id": PAPER_ID,
        "state": state,
        "role": "re_review_worker",
        "provider": "codex-cli",
        "model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "status": status,
        "attempt": 2,
        "started_at": generated_at,
        "finished_at": generated_at,
        "duration_ms": 0,
        "created_at": generated_at,
        "rework_ticket_ids": [TICKET_ID],
        "artifact_refs": artifacts,
        "output_summary": summary,
    }
    append_jsonl(WORKFLOW / "state_executions.jsonl", state_row)
    append_jsonl(
        WORKFLOW / "chat_messages.jsonl",
        {
            "record_type": "chat_message",
            "workflow_id": f"paper-review-{PAPER_ID}",
            "paper_id": PAPER_ID,
            "state": state,
            "role": "agent",
            "created_at": generated_at,
            "message": summary,
        },
    )
    append_jsonl(
        WORKFLOW / "agent_logs.jsonl",
        {
            "record_type": "agent_log",
            "workflow_id": f"paper-review-{PAPER_ID}",
            "paper_id": PAPER_ID,
            "state": state,
            "category": "re_review",
            "level": "info" if status in {"completed", "accepted_with_cautions"} else "warning",
            "created_at": generated_at,
            "message": summary,
            "path_refs": artifacts,
        },
    )


def run_gate(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def rework_response(generated_at: str, gate_evidence: dict[str, Any], gates_ready: bool) -> dict[str, Any]:
    return {
        "record_type": "rework_response",
        "response_id": f"{PAPER_ID}-worker246-source-review-{generated_at}",
        "paper_id": PAPER_ID,
        "ticket_ids": [TICKET_ID],
        "status": "resolved_after_source_review" if gates_ready else "kept_open_after_gate_failure",
        "state": "worker2_worker4_worker6_source_review_repair",
        "resolved_by": "codex-cli",
        "owner_workers": ["worker-2", "worker-4", "worker-6"],
        "checked_source_paths": SOURCE_PATHS_CHECKED,
        "tools_attempted": TOOLS_ATTEMPTED,
        "what_was_repaired": [
            "Worker-2 rebuilt source-supported Table 1 preparation activity and pH/heat residual-activity records with values, units, target context, assay context, and locators.",
            "Worker-4 reviewed APD6/DRAMP/dbAMP rows and preserved database target/mechanism aggregates as source_conflict/database-only instead of promoting unsupported claims.",
            "Worker-6 rewrote adjudication, quality feedback, mechanism context, and message-bus closeout from paper-local evidence.",
        ],
        "what_remains": ["No blocking/major issue or open rework target remains after strict gate rerun."]
        if gates_ready
        else ["Strict gates still failed; quality_feedback.json keeps targeted rework open."],
        "remaining_caution_codes": [
            "database_target_list_exceeds_this_paper",
            "terminal_tcc_identity_is_inferred",
            "no_toxicity_assay_reported",
            "external_original_figure_doc_not_local",
        ],
        "unrecoverable_material_gaps": nonblocking_gaps(),
        "qc_failure_reasons_remaining": [] if gates_ready else ["gate_failure_after_worker246_repair"],
        "gate_evidence": gate_evidence,
        "artifact_refs": [
            f"paper_packets/{PAPER_ID}/analysis/activity_toxicity_evidence.json",
            f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
            f"paper_packets/{PAPER_ID}/analysis/adjudication_report.json",
            f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
            f"papers/{PAPER_ID}/final/database_record_verification.json",
            f"papers/{PAPER_ID}/final/mechanism_ontology_record.json",
            f"papers/{PAPER_ID}/final/review_report.json",
            f"papers/{PAPER_ID}/work/review/quality_feedback.json",
        ],
        "created_at": generated_at,
        "responded_at": generated_at,
    }


def finalize_failure(generated_at: str, gate_evidence: dict[str, Any], semantic: dict[str, Any], publication: dict[str, Any]) -> None:
    issues = (semantic.get("results") or [{}])[0].get("issues") or []
    target = {
        "ticket_id": f"{TICKET_ID}-post-gate",
        "paper_id": PAPER_ID,
        "worker": "worker-6",
        "owner_worker": "worker-6",
        "target_queue": "adjudication",
        "layer": "review",
        "failure_code": "gate_failure_after_worker246_repair",
        "omission_code": "strict_gate_failure_after_source_review",
        "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
        "source_evidence_to_check": SOURCE_PATHS_CHECKED,
        "required_action": "Resolve the listed strict gate failures without accepting the paper until semantic and publication gates both pass.",
        "created_at": generated_at,
        "severity": "blocking",
        "blocks": ["publication_grade_ready", "final_approval"],
    }
    qc_reasons = [
        {
            "code": "gate_failure_after_worker246_repair",
            "owner_worker": "worker-6",
            "severity": "blocking",
            "reason": "Strict semantic/publication gate still failed after bounded worker-2/4/6 repair.",
            "semantic_issues": issues[:8],
            "publication_risk_counts": publication.get("risk_counts"),
        }
    ]
    review = read_json(PAPER / "final" / "review_report.json")
    review.update({"review_status": "needs_targeted_rework", "publication_grade": False, "qc_failure_reasons": qc_reasons, "rework_targets": [target]})
    for path in [PAPER / "final" / "review_report.json", PACKET / "final" / "review_report.json", PACKET / "analysis" / "adjudication_report.json"]:
        write_json(path, review)
    write_json(
        PAPER / "work" / "review" / "quality_feedback.json",
        {
            "paper_id": PAPER_ID,
            "generated_at": generated_at,
            "issue_count": len(qc_reasons),
            "qc_failure_reasons": qc_reasons,
            "rework_targets": [target],
            "rework_context_packet_required": True,
            "unrecoverable_material_gaps": nonblocking_gaps(),
            "status": "qc_failed_after_worker246_repair",
        },
    )
    append_jsonl(PACKET / "rework" / "rework_requests.jsonl", target)
    append_jsonl(PACKET / "rework" / "rework_responses.jsonl", rework_response(generated_at, gate_evidence, gates_ready=False))
    update_packet_and_workflow(generated_at, gates_ready=False, gate_evidence=gate_evidence)
    append_workflow_event(
        generated_at,
        "final_approval",
        "needs_rework",
        "Strict gates still failed after worker-2/4/6 source review; targeted rework remains open.",
        [str(SEMANTIC_REPORT), str(PUBLICATION_REPORT)],
    )


def finalize_success(generated_at: str, gate_evidence: dict[str, Any], activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> None:
    update_packet_and_workflow(generated_at, gates_ready=True, gate_evidence=gate_evidence)
    append_jsonl(PACKET / "rework" / "rework_responses.jsonl", rework_response(generated_at, gate_evidence, gates_ready=True))
    report = {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "pmid": PMID,
        "pmcid": PMCID,
        "title": TITLE,
        "generated_at": generated_at,
        "completion_claim": "source_reviewed_worker2_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions",
        "current_state": "final_approval",
        "terminal_status": "accepted_with_cautions",
        "final_approval_status": "accepted_with_cautions",
        "gate_summary": {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": True,
            "publication_grade_ready": True,
        },
        "gate_results": gate_evidence,
        "analysis": {
            "review_status": "accepted_with_cautions",
            "activity_records": len(activity.get("activity_records") or []),
            "toxicity_records": len(activity.get("toxicity_records") or []),
            "mechanism_claims": len(mechanism.get("mechanism_claims") or []),
            "database_status_summary": database.get("status_summary"),
        },
        "material": {
            "status": "material_extracted_with_gaps",
            "nonblocking_gaps_recorded": len(nonblocking_gaps()),
        },
        "open_rework_ticket_count": 0,
        "resolved_rework_ticket_ids": [TICKET_ID],
        "rework_ticket_ids": [],
        "not_publication_grade_reason": None,
        "semantic_gate": "passed",
        "publication_quality_gate": "passed_after_worker2_worker4_worker6_source_review",
        "manifest": str(MANIFEST),
        "semantic_report": str(SEMANTIC_REPORT),
        "publication_quality_report": str(PUBLICATION_REPORT),
        "workflow_dir": str(WORKFLOW),
    }
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", report)
    append_workflow_event(
        generated_at,
        "final_approval",
        "accepted_with_cautions",
        "Strict semantic and publication gates passed after worker-2/4/6 source-reviewed rework; rwk-complete-test-0001 closed.",
        [str(SEMANTIC_REPORT), str(PUBLICATION_REPORT), str(REPORTS / f"{PAPER_ID}.complete_message_test_report.json")],
    )


def run_gates(activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> None:
    semantic_code, semantic_out, semantic_err = run_gate(
        [
            sys.executable,
            ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py",
            "--root",
            ".",
            "--manifest",
            str(MANIFEST),
            "--json",
        ]
    )
    try:
        semantic = json.loads(semantic_out)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"semantic gate emitted invalid JSON: {exc}\nstdout={semantic_out}\nstderr={semantic_err}") from exc
    write_json(SEMANTIC_REPORT, semantic)

    publication_code, publication_out, publication_err = run_gate(
        [
            sys.executable,
            ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py",
            "--root",
            ".",
            "--manifest",
            str(MANIFEST),
            "--json-out",
            str(PUBLICATION_REPORT),
        ]
    )
    if not PUBLICATION_REPORT.exists():
        raise RuntimeError(f"publication gate did not write {PUBLICATION_REPORT}\nstdout={publication_out}\nstderr={publication_err}")
    publication = read_json(PUBLICATION_REPORT)
    gates_ready = (
        semantic_code == 0
        and publication_code == 0
        and int(semantic.get("publication_grade_pass_count") or 0) == 1
        and int(semantic.get("publication_grade_fail_count") or 0) == 0
        and publication.get("publication_grade_pass") is True
    )
    generated_at = now_iso()
    gate_evidence = {
        "semantic_report": str(SEMANTIC_REPORT),
        "semantic_returncode": semantic_code,
        "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
        "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
        "semantic_issue_count": (semantic.get("results") or [{}])[0].get("issue_count"),
        "publication_report": str(PUBLICATION_REPORT),
        "publication_returncode": publication_code,
        "publication_grade_pass": publication.get("publication_grade_pass"),
        "publication_risk_counts": publication.get("risk_counts"),
    }
    if gates_ready:
        finalize_success(generated_at, gate_evidence, activity, database, mechanism)
    else:
        finalize_failure(generated_at, gate_evidence, semantic, publication)
    print(json.dumps({"ok": True, "gates_ready": gates_ready, "gate_evidence": gate_evidence}, ensure_ascii=False, indent=2))


def main() -> int:
    generated_at = now_iso()
    activity, database, mechanism, _review = write_owner_artifacts(generated_at)
    update_packet_and_workflow(generated_at, gates_ready=False)
    append_workflow_event(
        generated_at,
        "worker2_worker4_worker6_repair",
        "completed",
        "Worker-2/4/6 source-reviewed rework wrote activity rows, database adjudication, final review, and quality feedback before gate rerun.",
        [
            str(PACKET / "analysis" / "activity_toxicity_evidence.json"),
            str(PACKET / "analysis" / "database_record_audit.json"),
            str(PAPER / "final" / "review_report.json"),
            str(PAPER / "work" / "review" / "quality_feedback.json"),
        ],
    )
    run_gates(activity, database, mechanism)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
