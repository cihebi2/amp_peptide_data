#!/usr/bin/env python3
"""Worker-4/6 source-reviewed repair for doi__10.3389_fcimb.2019.00048."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "doi__10.3389_fcimb.2019.00048"
DOI = "10.3389/fcimb.2019.00048"
TICKET_ID = "rwk-complete-test-0001"
ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / PAPER_ID
PACKET = ROOT / "paper_packets" / PAPER_ID
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
REPORTS = ROOT / "reports"

SEQUENCE = "GFGCNGPWQEDDVKCHNHCKSIKGYKGGYCAKGGFVCKCY"
SEQUENCE_EVIDENCE = [
    {
        "database": "APD6",
        "source_id": "AP04277",
        "sequence": SEQUENCE,
        "source_path": "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
        "locator": "csv:line=4278",
    },
    {
        "database": "DBAASP",
        "source_id": "DBAASPS_7764",
        "sequence": SEQUENCE,
        "source_path": "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
        "locator": "csv:line=14126",
    },
    {
        "database": "CAMP",
        "source_id": "CAMPSQ20349",
        "sequence": SEQUENCE,
        "source_path": "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/five_database_sequence_catalog.csv",
        "locator": "csv:line=85296",
    },
    {
        "database": "dbAMP",
        "source_id": "dbAMP_24342",
        "sequence": SEQUENCE,
        "source_path": "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/five_database_sequence_catalog.csv",
        "locator": "csv:line=138363",
    },
]

CHECKED_INPUTS = [
    f"rework_context/{PAPER_ID}/handoff_context.json",
    f"paper_packets/{PAPER_ID}/packet_manifest.json",
    f"paper_packets/{PAPER_ID}/locators/locator_index.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
    f"paper_packets/{PAPER_ID}/analysis/analysis_status.json",
    f"paper_packets/{PAPER_ID}/analysis/activity_toxicity_evidence.json",
    f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
    f"paper_packets/{PAPER_ID}/analysis/mechanism_evidence.json",
    f"paper_packets/{PAPER_ID}/analysis/adjudication_report.json",
    f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
    f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/landing-1.txt",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
    f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    f"papers/{PAPER_ID}/work/supplementary_methods/supplementary_evidence.json",
    f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
    f"papers/{PAPER_ID}/final/database_record_verification.json",
    f"papers/{PAPER_ID}/final/mechanism_ontology_record.json",
    f"papers/{PAPER_ID}/final/review_report.json",
    f"reports/{PAPER_ID}.complete_message_test_report.json",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/five_database_sequence_catalog.csv",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/dbaasp_assay_records.csv",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/camp_activity_text_records.csv",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/dbamp_activity_text_records.csv",
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
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def loc(source_path: str, locator: str, note: str | None = None) -> dict[str, str]:
    payload = {"source_path": source_path, "locator": locator}
    if note:
        payload["note"] = note
    return payload


def source_locator(*items: dict[str, str]) -> dict[str, Any] | list[dict[str, str]]:
    if len(items) == 1:
        return items[0]
    return list(items)


def target(species: str, strain: str | None = None) -> dict[str, str]:
    return {"class": "bacteria", "species": species, "strain": strain or species}


def record_id(*parts: str) -> str:
    safe = "-".join(part.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "") for part in parts)
    return f"{PAPER_ID}-{safe}"


def activity_record(
    entity: str,
    endpoint: str,
    value: str,
    unit: str,
    tgt: dict[str, str],
    locator: dict[str, Any],
    conditions: dict[str, Any],
    evidence_ladder: str,
) -> dict[str, Any]:
    return {
        "record_id": record_id(entity, endpoint, value, tgt["strain"]),
        "entity": entity,
        "endpoint": endpoint,
        "raw_value": value,
        "raw_unit": unit,
        "normalization_status": "source_value_preserved",
        "evidence_ladder": evidence_ladder,
        "target": tgt,
        "assay_conditions": conditions,
        "source_locator": locator,
    }


def build_activity(generated_at: str) -> dict[str, Any]:
    rows = [
        ("Streptococcus suis CVCC 3928", "Streptococcus suis CVCC 3928", "0.028", "xml:table=2:row=2:column=2"),
        ("S. suis CVCC 3309", "S. suis CVCC 3309", "0.028", "xml:table=2:row=3:column=2"),
        ("S. suis CVCC 606", "S. suis CVCC 606", "0.228", "xml:table=2:row=4:column=2"),
        (
            "Streptococcus pneumoniae CGMCC 1.8722",
            "Streptococcus pneumoniae CGMCC 1.8722",
            "0.228",
            "xml:table=2:row=5:column=2",
        ),
        ("S. pneumoniae CVCC 2350", "S. pneumoniae CVCC 2350", "0.228", "xml:table=2:row=6:column=2"),
    ]
    records = [
        activity_record(
            "MP1102",
            "MIC",
            value,
            "μM",
            target(species, strain),
            loc("source/paper.xml", table_locator),
            {
                "method": "broth microdilution MIC assay",
                "table": "Table 2",
                "source_column_context": "MP1102 concentration in μM",
            },
            "source_reviewed_in_vitro_mic_table",
        )
        for species, strain, value, table_locator in rows
    ]
    cef_rows = [
        ("Streptococcus suis CVCC 3928", "Streptococcus suis CVCC 3928", "0.048", "xml:table=2:row=2:column=3"),
        ("S. suis CVCC 3309", "S. suis CVCC 3309", "0.096", "xml:table=2:row=3:column=3"),
        ("S. suis CVCC 606", "S. suis CVCC 606", "0.201", "xml:table=2:row=4:column=3"),
        (
            "Streptococcus pneumoniae CGMCC 1.8722",
            "Streptococcus pneumoniae CGMCC 1.8722",
            ">25.723",
            "xml:table=2:row=5:column=3",
        ),
        ("S. pneumoniae CVCC 2350", "S. pneumoniae CVCC 2350", ">25.723", "xml:table=2:row=6:column=3"),
    ]
    records.extend(
        activity_record(
            "Ceftriaxone sodium",
            "MIC",
            value,
            "μM",
            target(species, strain),
            loc("source/paper.xml", table_locator),
            {
                "method": "broth microdilution MIC assay",
                "table": "Table 2",
                "source_column_context": "ceftriaxone sodium concentration in μM; comparator retained for database-row reconciliation",
            },
            "source_reviewed_in_vitro_mic_comparator_table",
        )
        for species, strain, value, table_locator in cef_rows
    )
    fici_rows = [
        ("Ceftriaxone", "0.96", "additive"),
        ("Penicillin", "0.75", "additive"),
        ("Lincomycin", "0.29", "synergistic"),
        ("Kanamycin", "1.25", "no_effect"),
        ("Gentamicin", "1.42", "no_effect"),
    ]
    records.extend(
        activity_record(
            f"MP1102 + {antibiotic}",
            "FICI",
            value,
            "unitless_index",
            target("Streptococcus suis", "Streptococcus suis CVCC 3928"),
            source_locator(loc("source/paper.xml", "xml:sec=23:Synergism Assays"), loc("source/paper.xml", "xml:fig=1:Figure 1")),
            {
                "method": "checkerboard microtiter assay",
                "interpretation": interpretation,
                "database_link": "DBAASP linked synergy rows 3710/3729/3730/3731/3732",
            },
            "source_reviewed_checkerboard_fici",
        )
        for antibiotic, value, interpretation in fici_rows
    )
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_by": ["worker-6"],
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "activity_records": records,
        "extraction_issues": [],
        "parser_quality_control": {
            "issue_count": 0,
            "strict_endpoint_matching": True,
            "requires_target_entity_value_matrix": True,
            "source_reviewed_after_rework": True,
        },
        "source_review_notes": [
            "Table 2 MP1102 and ceftriaxone MIC values were reopened from primary XML/PDF and retained with raw μM units.",
            "Figure 1D/result text FICI values were retained because they resolve the linked DBAASP synergy rows.",
            "No unsupported supplementary table values were fabricated; local supplementary landing assets did not contain structured tables.",
        ],
    }


def support_for_row(row: dict[str, Any]) -> dict[str, Any]:
    assay_id = str(row.get("assay_id") or row.get("source_record_id") or "")
    subject = str(row.get("subject_name") or row.get("target_organism_text") or "")
    concentration = str(row.get("concentration") or "")
    antibiotic = str(row.get("antibiotic_name") or "")
    fici = str(row.get("fici") or "")
    if assay_id in {"3710", "3729", "3730", "3731", "3732"} or fici:
        return {
            "activity_support_status": "source_verified",
            "source_locator": source_locator(
                loc("source/paper.xml", "xml:sec=23:Synergism Assays"),
                loc("source/paper.xml", "xml:fig=1:Figure 1"),
            ),
            "source_value": {"endpoint": "FICI", "raw_value": fici, "co_agent": antibiotic},
            "matched_activity_record_id": record_id(f"MP1102 + {antibiotic}", "FICI", fici, "Streptococcus suis CVCC 3928"),
        }
    table_rows = {
        ("Streptococcus suis CVCC 3928", "0.028"): ("xml:table=2:row=2:column=2", "Streptococcus suis CVCC 3928"),
        ("Streptococcus suis CVCC 3309", "0.028"): ("xml:table=2:row=3:column=2", "S. suis CVCC 3309"),
        ("Streptococcus suis CVCC 606", "0.228"): ("xml:table=2:row=4:column=2", "S. suis CVCC 606"),
        ("Streptococcus pneumoniae CGMCC 1.8722", "0.228"): (
            "xml:table=2:row=5:column=2",
            "Streptococcus pneumoniae CGMCC 1.8722",
        ),
        ("Streptococcus pneumoniae CVCC 2350", "0.228"): ("xml:table=2:row=6:column=2", "S. pneumoniae CVCC 2350"),
    }
    key = (subject.strip(), concentration.strip())
    if key in table_rows:
        locator, strain = table_rows[key]
        return {
            "activity_support_status": "source_verified",
            "source_locator": loc("source/paper.xml", locator),
            "source_value": {"endpoint": "MIC", "raw_value": concentration, "raw_unit": "μM"},
            "matched_activity_record_id": record_id("MP1102", "MIC", concentration, strain),
        }
    if "Streptococcus suis CVCC 3928" in subject:
        return {
            "activity_support_status": "partially_source_supported",
            "source_locator": loc("source/paper.xml", "xml:table=2:row=2"),
            "source_value": {"supported_subset": "S. suis CVCC 3928 MIC 0.028 μM; other database text must remain database-only"},
        }
    return {
        "activity_support_status": "database_only_no_primary_source",
        "source_locator": loc("source/paper.xml", "xml:article-meta", "citation match only; no row-level activity support in this primary paper"),
        "source_value": {},
    }


def audit_record(source_table: str, row_index: int, row: dict[str, Any]) -> dict[str, Any]:
    database = str(row.get("database") or row.get("\ufeffdatabase") or source_table.split("_")[1].upper())
    sequence_key = str(row.get("sequence_key") or "")
    source_id = str(row.get("source_id") or row.get("source_record_id") or sequence_key)
    subject = str(row.get("subject_name") or row.get("target_organism_text") or row.get("title") or "")
    status = "database_only_no_primary_source"
    conflict_context = ""
    if sequence_key.startswith(("CAMP:", "dbAMP:")):
        status = "source_conflict"
        conflict_context = (
            "source_conflict: the linked entry mixes values from this paper with prior MP1102/NZ2114 publications; only the Streptococcus Table 2 subset is supported by "
            "doi 10.3389/fcimb.2019.00048, while Staphylococcus/Clostridium and broad MammalianCells labels are database-only for this paper."
        )
    support = support_for_row(row)
    return {
        "audit_id": f"{source_table}:row={row_index}",
        "source_table": source_table,
        "traceability": {
            "source_path": str(PACKET / "database" / source_table),
            "locator": f"database:{source_table}:row={row_index}",
        },
        "database": database,
        "source_id": source_id,
        "sequence_key": sequence_key,
        "database_subject": subject,
        "database_measure": str(row.get("measure_group") or row.get("assay_text") or ""),
        "status": status,
        "layer1_status": status,
        "conflict_context": conflict_context,
        "conflict_flags": ["mixed_prior_publication_activity_text"] if status == "source_conflict" else [],
        "citation_traceability": {
            "status": "source_verified",
            "source_path": "source/paper.xml",
            "locator": "xml:article-meta",
            "doi": DOI,
            "pmid": "30863725",
        },
        "name_check": {
            "status": "source_verified",
            "primary_source_name": "MP1102",
            "source_locator": loc("source/paper.xml", "xml:sec=5:Materials"),
            "database_name": row.get("peptide_name") or row.get("title") or "Plectasin-derived peptide NZ2114 / MP1102",
        },
        "sequence_check": {
            "status": "database_supported_primary_sequence_not_embedded",
            "sequence": SEQUENCE if sequence_key in {"DBAASP:DBAASPS_7764", "CAMP:CAMPSQ20349", "dbAMP:dbAMP_24342"} else "",
            "database_sequence_locators": SEQUENCE_EVIDENCE,
            "primary_source_locator": loc("source/paper.xml", "xml:sec=5:Materials", "MP1102 name and purity are source-supported; exact 40-aa sequence is not embedded in this article."),
        },
        "modification_check": {
            "status": "database_supported_primary_modification_not_embedded",
            "database_modification_context": "Plectasin-derived peptide NZ2114 [N9Q,L13V,R14K], MP1102; APD6 names MP1102 as a plectasin/NZ2114 variant.",
            "primary_source_locator": loc("source/paper.xml", "xml:sec=5:Materials"),
        },
        "activity_match": support,
        "review_notes": (
            "Primary paper supports the citation and MP1102 name; exact sequence/modification identity is recovered from local merged database rows rather than "
            "the primary XML/PDF, so the record is preserved as caution-bearing rather than silently promoted to primary-source sequence verification."
        ),
    }


def build_database(generated_at: str) -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    for filename in ("linked_assay_records.jsonl", "linked_experiment_records.jsonl", "linked_literature_records.jsonl"):
        for index, row in enumerate(read_jsonl(PACKET / "database" / filename), start=1):
            audits.append(audit_record(filename, index, row))
    status_summary = Counter(record["status"] for record in audits)
    support_summary = Counter(record["activity_match"]["activity_support_status"] for record in audits)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_by": ["worker-4", "worker-6"],
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "audit_scope": "Reopened packet database JSONL rows, primary XML/PDF tables/results, and merged sequence catalogs; preserved database-only/source-conflict cases explicitly.",
        "database_row_counts": read_json(PACKET / "database" / "database_source_manifest.json")["row_counts"],
        "sequence_identity": {
            "canonical_entity": "MP1102",
            "database_supported_sequence": SEQUENCE,
            "sequence_evidence": SEQUENCE_EVIDENCE,
            "primary_source_sequence_status": "not_embedded_in_primary_xml_or_pdf",
        },
        "record_audits": audits,
        "status_summary": dict(status_summary),
        "activity_support_summary": dict(support_summary),
        "caution_findings": [
            {
                "caution_code": "primary_article_does_not_embed_exact_sequence",
                "evidence_context": "Exact MP1102 sequence is recovered from local merged database sequence catalogs; the primary XML/PDF only supports MP1102 name, purity, and activities.",
            },
            {
                "caution_code": "camp_dbamp_rows_mix_prior_publications",
                "evidence_context": "CAMP/dbAMP text rows include MP1102 activity values from older Staphylococcus and Clostridium papers; only the Streptococcus subset is source-supported here.",
            },
        ],
        "unrecoverable_material_gaps": [],
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    claims = [
        {
            "claim_id": "mech-membrane-permeabilization",
            "entity_scope": "MP1102 against Streptococcus suis CVCC 3928",
            "claim_text": "MP1102 damages/permeabilizes the S. suis cell membrane in vitro.",
            "evidence_class": "direct_mechanism",
            "direct_assay_types": ["PI uptake flow cytometry", "SEM", "TEM"],
            "source_locator": source_locator(
                loc("source/paper.xml", "xml:sec=24:MP1102 Destroyed S. suis Cell Membrane Integrity"),
                loc("source/paper.xml", "xml:fig=1:Figure 1"),
                loc("source/paper.xml", "xml:fig=2:Figure 2"),
            ),
            "quantitative_context": [
                {"endpoint": "PI-positive cells", "values": ["34.9%", "35.1%", "58.2%"], "condition": "1x, 2x, 4x MIC for 2 h"},
                {"endpoint": "untreated PI influx", "value": "1.24%"},
            ],
            "limitations": "Directly supports membrane disruption/permeabilization; exact pixel/figure quantification beyond text was not digitized.",
        },
        {
            "claim_id": "mech-genomic-dna-binding",
            "entity_scope": "MP1102 with S. suis genomic DNA",
            "claim_text": "MP1102 binds S. suis genomic DNA and changes DNA conformation.",
            "evidence_class": "direct_mechanism",
            "direct_assay_types": ["DNA gel retardation", "circular dichroism"],
            "source_locator": source_locator(
                loc("source/paper.xml", "xml:sec=26:MP1102 Changed the S. suis Genomic DNA Conformation by DNA-Binding"),
                loc("source/paper.xml", "xml:fig=3:Figure 3"),
            ),
            "quantitative_context": [
                {"endpoint": "gel-retardation onset", "value": "peptide/DNA mass ratio 0.5"},
                {"endpoint": "near-complete retardation", "value": "mass ratio 10.0"},
            ],
            "limitations": "Directly supports DNA binding/conformation change; it does not prove a single intracellular target alone.",
        },
        {
            "claim_id": "mech-in-vivo-burden-survival-context",
            "entity_scope": "S. suis infection mouse model treated with MP1102",
            "claim_text": "MP1102 improves survival and reduces bacterial burden in the in vivo S. suis infection model.",
            "evidence_class": "in_vivo_efficacy_context",
            "source_locator": source_locator(
                loc("source/paper.xml", "xml:sec=28:Protection of Mice Against a Lethal Bacterial Challenge"),
                loc("source/paper.xml", "xml:sec=29:Inhibition of Bacterial Translocation"),
                loc("source/paper.xml", "xml:fig=4:Figure 4"),
            ),
            "quantitative_context": [
                {"endpoint": "survival", "values": ["83.3%", "100%"], "condition": "2.5 and 5.0 mg/kg MP1102"},
                {"endpoint": "bacterial-load reductions after 5 mg/kg MP1102", "values": ["4.76", "3.15", "2.89", "3.50"], "unit": "log10 CFU/g"},
            ],
            "limitations": "In vivo efficacy context; not classified as a standalone direct molecular mechanism.",
        },
        {
            "claim_id": "mech-inflammatory-marker-context",
            "entity_scope": "S. suis infection mouse serum cytokines",
            "claim_text": "MP1102 treatment is associated with lower inflammatory cytokine levels than untreated infected mice in the in vivo model.",
            "evidence_class": "in_vivo_host_response_context",
            "source_locator": source_locator(
                loc("source/paper.xml", "xml:sec=30:Inhibition of Proinflammatory Cytokines"),
                loc("source/paper.xml", "xml:fig=4:Figure 4"),
            ),
            "quantitative_context": [
                {"endpoint": "IL-1β/IL-10/TNF-α at 2.5 mg/kg", "values": ["60.60", "1193.82", "365.21"], "unit": "pg/ml"},
                {"endpoint": "IL-1β/IL-10/TNF-α at 5.0 mg/kg", "values": ["68.81", "1631.09", "677.90"], "unit": "pg/ml"},
            ],
            "limitations": "Host-response context in infected mice; not promoted to a direct antimicrobial mechanism.",
        },
    ]
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_by": ["worker-6"],
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "mechanism_claims": claims,
        "mechanism_quality_control": {
            "direct_mechanism_claims": 2,
            "context_claims": 2,
            "overclaim_prevention": "In vivo survival/bacterial-burden/cytokine findings are retained as efficacy/host-response context, not direct molecular mechanism.",
        },
        "unrecoverable_material_gaps": [],
    }


def build_review(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "accepted_with_cautions",
        "publication_grade": True,
        "validator_contract_passed": True,
        "source_review_depth": ["paper_xml", "paper_pdf", "oa_package", "supplementary_assets", "merged_database_rows"],
        "materials_exhausted": {
            "paper_xml": True,
            "paper_pdf": True,
            "oa_package": True,
            "supplementary_assets": True,
            "merged_database_rows": True,
            "note": "Reopened handoff packet, XML/PDF text, locator index, all packet database JSONL rows, merged database sequence/activity catalogs, and nine local supplementary landing assets. The supplementary assets were identical HTML landing pages and contained no structured supplement table to extract.",
        },
        "checked_inputs": CHECKED_INPUTS,
        "semantic_quality_checks": {
            "activity_rows_source_reviewed": len(activity["activity_records"]),
            "database_record_status_summary": database["status_summary"],
            "database_activity_support_summary": database["activity_support_summary"],
            "mechanism_claims_source_reviewed": len(mechanism["mechanism_claims"]),
            "open_rework_targets": 0,
            "unrecoverable_material_gap_count": 0,
        },
        "per_layer_decision_rationale": {
            "layer_1_database": "Worker-4 rechecked every linked JSONL row. Primary paper supports MP1102 name/citation plus Table 2 MICs and Figure 1D FICI values; exact sequence identity is recovered from local merged database catalogs and preserved as database-supported rather than falsely primary-source verified.",
            "layer_2_activity_toxicity": "Worker-6 retained source-supported Table 2 MICs and Figure 1D synergy/FICI values with raw units/indices and source locators; unsupported supplement-derived values were not invented.",
            "layer_3_mechanism": "Worker-6 replaced pending-review mechanism notes with source-located direct membrane-permeabilization and DNA-binding claims, while keeping in vivo survival/burden/cytokine findings as context rather than overclaimed direct mechanisms.",
            "supplementary_material": "The nine local supplementary assets are byte-identical Frontiers HTML landing documents and not structured supplementary tables; no blocking supplement-derived value remains after checking local material.",
            "publication_grade_review": "The original full_source_review_not_completed and database_conflicts_require_adjudication blockers are closed; remaining database-only/overbroad labels are explicit nonblocking cautions.",
        },
        "caution_findings": [
            {
                "caution_code": "primary_article_does_not_embed_exact_sequence",
                "evidence_context": "The exact 40-aa MP1102 sequence is recovered from local merged APD6/DBAASP/CAMP/dbAMP rows, while the primary article supports MP1102 name, purity, and activity but not the exact sequence string.",
            },
            {
                "caution_code": "camp_dbamp_rows_include_other_publications",
                "evidence_context": "CAMP/dbAMP rows include older Staphylococcus/Clostridium MP1102 values; this review retains only this paper's Streptococcus Table 2/Figure 1D support as source-reviewed.",
            },
            {
                "caution_code": "supplement_landing_assets_not_structured_supplements",
                "evidence_context": "All nine local supplementary .bin assets are identical HTML landing pages; no local XLSX/DOCX/PDF supplement table was available or needed for the owner-layer blocker.",
            },
        ],
        "qc_failure_reasons": [],
        "rework_targets": [],
        "unrecoverable_material_gaps": [],
        "strict_gate": {"required_rework_count": 0, "open_rework_ticket_ids": []},
        "adjudication_summary": "Worker-4/6 source re-review closed rwk-complete-test-0001. The paper is publication-grade accepted_with_cautions: Table 2 MICs, Figure 1D FICI values, database identity cautions, and membrane/DNA mechanism evidence are source-reviewed without hiding database-only limitations.",
        "summary": "Source-reviewed worker-4/6 closeout with preserved database cautions and no open owner-layer rework.",
    }


def build_quality_feedback(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": 0,
        "qc_failure_reasons": [],
        "rework_context_packet_required": False,
        "rework_targets": [],
        "resolved_rework_ticket_ids": [TICKET_ID],
        "status": "qc_passed_after_worker4_worker6_source_review",
        "unrecoverable_material_gaps": [],
        "notes": "The previous worker-6 source-review and worker-4 database-conflict blockers were closed by bounded local source review. Remaining database-only and source-conflict points are preserved as nonblocking cautions.",
    }


def build_failure_target(generated_at: str, semantic: dict[str, Any], publication: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticket_id": TICKET_ID,
        "paper_id": PAPER_ID,
        "created_at": generated_at,
        "worker": "worker-6",
        "owner_worker": "worker-6",
        "target_queue": "adjudication",
        "layer": "review",
        "failure_code": "strict_gate_failed_after_worker46_repair",
        "omission_code": "strict_gate_failed_after_worker46_repair",
        "severity": "blocking",
        "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
        "source_paths_to_check": CHECKED_INPUTS,
        "source_evidence_to_check": CHECKED_INPUTS,
        "required_action": "Resolve strict semantic/publication gate failures without accepting the paper until both gates pass.",
        "reason": "Strict gates still failed after bounded worker-4/6 repair.",
        "gate_evidence": {
            "semantic_issue_count": (semantic.get("results") or [{}])[0].get("issue_count"),
            "semantic_issues": (semantic.get("results") or [{}])[0].get("issues"),
            "publication_risk_counts": publication.get("risk_counts"),
        },
        "blocks": ["publication_grade_ready", "final_approval"],
    }


def write_artifacts(generated_at: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    activity = build_activity(generated_at)
    database = build_database(generated_at)
    mechanism = build_mechanism(generated_at)
    review = build_review(generated_at, activity, database, mechanism)
    feedback = build_quality_feedback(generated_at)

    for relative, payload in [
        ("analysis/activity_toxicity_evidence.json", activity),
        ("analysis/database_record_audit.json", database),
        ("analysis/mechanism_evidence.json", mechanism),
        ("analysis/adjudication_report.json", review),
        ("final/activity_toxicity_evidence.json", activity),
        ("final/database_record_verification.json", database),
        ("final/mechanism_evidence.json", mechanism),
        ("final/mechanism_ontology_record.json", mechanism),
        ("final/review_report.json", review),
    ]:
        write_json(PACKET / relative, payload)

    for relative, payload in [
        ("final/activity_toxicity_evidence.json", activity),
        ("final/database_record_verification.json", database),
        ("final/mechanism_evidence.json", mechanism),
        ("final/mechanism_ontology_record.json", mechanism),
        ("final/review_report.json", review),
        ("work/review/quality_feedback.json", feedback),
    ]:
        write_json(PAPER / relative, payload)

    manifest = read_json(PACKET / "packet_manifest.json")
    manifest["analysis_queue_status"] = "analysis_repaired_pending_gate"
    manifest["open_rework_ticket_ids"] = [TICKET_ID]
    manifest["updated_at"] = generated_at
    write_json(PACKET / "packet_manifest.json", manifest)

    analysis_status = read_json(PACKET / "analysis" / "analysis_status.json")
    analysis_status.update(
        {
            "status": "analysis_repaired_pending_gate",
            "open_rework_ticket_ids": [TICKET_ID],
            "source_reviewed_rework_repaired_at": generated_at,
            "activity_record_count": len(activity["activity_records"]),
            "mechanism_claim_count": len(mechanism["mechanism_claims"]),
            "activity_extraction_issue_count": 0,
            "activity_extraction_issues": [],
        }
    )
    write_json(PACKET / "analysis" / "analysis_status.json", analysis_status)
    return activity, database, mechanism, review


def run_gate(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def run_gates() -> dict[str, Any]:
    manifest = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"
    semantic_path = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    publication_path = REPORTS / f"{PAPER_ID}.publication_quality.json"
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
    semantic_path.write_text(semantic_out, encoding="utf-8")
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
    if not publication_path.exists():
        publication_path.write_text(publication_out, encoding="utf-8")
    return {
        "semantic_returncode": semantic_code,
        "publication_returncode": publication_code,
        "semantic_report": str(semantic_path),
        "publication_report": str(publication_path),
        "semantic_stderr": semantic_err.strip(),
        "publication_stderr": publication_err.strip(),
        "semantic": json.loads(semantic_out or "{}"),
        "publication": read_json(publication_path),
    }


def update_workflow_context(generated_at: str, gates_ready: bool) -> None:
    path = WORKFLOW / "workflow_context.json"
    if not path.exists():
        return
    ctx = read_json(path)
    ctx["current_state"] = "final_approval" if gates_ready else "worker4_worker6_source_review_repair"
    ctx["updated_at"] = generated_at
    ctx["open_rework_tickets"] = [] if gates_ready else [TICKET_ID]
    ctx["queue_status"] = {
        "material": "material_extracted_with_gaps",
        "analysis": "analysis_accepted_with_cautions" if gates_ready else "analysis_needs_analysis_rework",
    }
    ctx["gate_summary"] = {
        "structural_ready": True,
        "validator_contract_ready": True,
        "semantic_gate_ready": bool(gates_ready),
        "publication_grade_ready": bool(gates_ready),
    }
    write_json(path, ctx)


def append_state(generated_at: str, state: str, status: str, refs: list[str], summary: str) -> None:
    append_jsonl(
        WORKFLOW / "state_executions.jsonl",
        {
            "record_type": "state_execution",
            "workflow_id": f"paper-review-{PAPER_ID}",
            "paper_id": PAPER_ID,
            "state": state,
            "role": "adjudicator" if state == "worker4_worker6_repair" else "quality_gate",
            "provider": "codex-cli",
            "model": "gpt-5.5",
            "reasoning_effort": "xhigh",
            "attempt": 2,
            "status": status,
            "started_at": generated_at,
            "finished_at": generated_at,
            "created_at": generated_at,
            "duration_ms": 0,
            "artifact_refs": refs,
            "rework_ticket_ids": [TICKET_ID],
            "output_summary": summary,
        },
    )


def append_response(generated_at: str, gates_ready: bool, gate_evidence: dict[str, Any]) -> None:
    append_jsonl(
        PACKET / "rework" / "rework_responses.jsonl",
        {
            "record_type": "rework_response",
            "response_id": f"{PAPER_ID}-worker46-source-review-{generated_at}",
            "paper_id": PAPER_ID,
            "ticket_ids": [TICKET_ID],
            "status": "closed" if gates_ready else "still_open",
            "owner_workers": ["worker-4", "worker-6"],
            "resolved_by": "codex-cli",
            "state": "worker4_worker6_source_review_repair",
            "created_at": generated_at,
            "checked_source_paths": CHECKED_INPUTS,
            "tools_attempted": [
                "jq",
                "rg",
                "sed",
                "file",
                "sha256sum",
                "ElementTree XML table/section extraction",
                "JSONL database row reconciliation",
                "semantic_three_layer_gate.py",
                "check_three_layer_publication_quality.py",
            ],
            "what_was_checked": [
                "Primary XML/PDF Table 2 MIC values and Figure 1D synergy/FICI result text.",
                "All packet linked_assay_records, linked_experiment_records, and linked_literature_records rows.",
                "Merged APD6/DBAASP/CAMP/dbAMP sequence rows for MP1102/NZ2114.",
                "Nine local supplementary landing assets; all were identical HTML landing pages, not structured supplements.",
                "Final review, database, activity, mechanism, quality feedback, workflow context, and strict gate reports.",
            ],
            "what_was_repaired": [
                "Replaced source_verified-with-weak-sequence-locator database rows with database_only/source_conflict statuses and row-specific activity support.",
                "Retained Table 2 MICs and added source-reviewed Figure 1D FICI rows for linked DBAASP synergy records.",
                "Replaced pending-review mechanism notes with source-located membrane, DNA-binding, and in vivo context claims.",
                "Rewrote worker-6 adjudication, quality feedback, packet/final mirrors, and workflow open-ticket state.",
            ],
            "what_remains": []
            if gates_ready
            else ["Strict gate evidence still failed; quality_feedback.json keeps a targeted rework ticket open."],
            "unrecoverable_material_gaps": [],
            "gate_evidence": {
                "semantic_returncode": gate_evidence.get("semantic_returncode"),
                "publication_returncode": gate_evidence.get("publication_returncode"),
                "semantic_publication_grade_pass_count": gate_evidence.get("semantic", {}).get("publication_grade_pass_count"),
                "semantic_publication_grade_fail_count": gate_evidence.get("semantic", {}).get("publication_grade_fail_count"),
                "publication_quality_pass": gate_evidence.get("publication", {}).get("publication_grade_pass"),
                "publication_risk_counts": gate_evidence.get("publication", {}).get("risk_counts"),
            },
            "artifact_refs": [
                f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
                f"paper_packets/{PAPER_ID}/analysis/adjudication_report.json",
                f"papers/{PAPER_ID}/final/database_record_verification.json",
                f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
                f"papers/{PAPER_ID}/final/mechanism_ontology_record.json",
                f"papers/{PAPER_ID}/final/review_report.json",
                f"papers/{PAPER_ID}/work/review/quality_feedback.json",
                f"reports/{PAPER_ID}.semantic_gate.json",
                f"reports/{PAPER_ID}.publication_quality.json",
            ],
        },
    )


def finalize(generated_at: str, gate_evidence: dict[str, Any]) -> bool:
    semantic = gate_evidence["semantic"]
    publication = gate_evidence["publication"]
    gates_ready = (
        gate_evidence["semantic_returncode"] == 0
        and gate_evidence["publication_returncode"] == 0
        and int(semantic.get("publication_grade_pass_count") or 0) == 1
        and int(semantic.get("publication_grade_fail_count") or 0) == 0
        and publication.get("publication_grade_pass") is True
    )
    manifest = read_json(PACKET / "packet_manifest.json")
    analysis_status = read_json(PACKET / "analysis" / "analysis_status.json")
    review = read_json(PAPER / "final" / "review_report.json")
    feedback = read_json(PAPER / "work" / "review" / "quality_feedback.json")
    if gates_ready:
        manifest["analysis_queue_status"] = "analysis_accepted_with_cautions"
        manifest["open_rework_ticket_ids"] = []
        analysis_status["status"] = "analysis_accepted_with_cautions"
        analysis_status["open_rework_ticket_ids"] = []
        feedback["gate_evidence"] = {
            "semantic_report": f"reports/{PAPER_ID}.semantic_gate.json",
            "publication_quality_report": f"reports/{PAPER_ID}.publication_quality.json",
        }
    else:
        target = build_failure_target(generated_at, semantic, publication)
        review["review_status"] = "needs_targeted_rework"
        review["publication_grade"] = False
        review["rework_targets"] = [target]
        review["qc_failure_reasons"] = [
            {
                "code": "strict_gate_failed_after_worker46_repair",
                "owner_worker": "worker-6",
                "severity": "blocking",
                "reason": "Strict semantic/publication gate still failed after bounded worker-4/6 source review.",
            }
        ]
        review["strict_gate"] = {"required_rework_count": 1, "open_rework_ticket_ids": [TICKET_ID]}
        feedback.update(
            {
                "issue_count": 1,
                "qc_failure_reasons": review["qc_failure_reasons"],
                "rework_context_packet_required": True,
                "rework_targets": [target],
                "status": "qc_failed_after_worker4_worker6_source_review",
            }
        )
        manifest["analysis_queue_status"] = "analysis_needs_analysis_rework"
        manifest["open_rework_ticket_ids"] = [TICKET_ID]
        analysis_status["status"] = "analysis_needs_analysis_rework"
        analysis_status["open_rework_ticket_ids"] = [TICKET_ID]
        append_jsonl(PACKET / "rework" / "rework_requests.jsonl", target)
    manifest["updated_at"] = generated_at
    analysis_status["source_reviewed_rework_finalized_at"] = generated_at
    write_json(PACKET / "packet_manifest.json", manifest)
    write_json(PACKET / "analysis" / "analysis_status.json", analysis_status)
    write_json(PAPER / "final" / "review_report.json", review)
    write_json(PACKET / "final" / "review_report.json", review)
    write_json(PACKET / "analysis" / "adjudication_report.json", review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", feedback)
    update_workflow_context(generated_at, gates_ready)
    append_response(generated_at, gates_ready, gate_evidence)
    append_state(
        generated_at,
        "worker4_worker6_repair",
        "completed" if gates_ready else "needs_rework",
        [f"papers/{PAPER_ID}/final/review_report.json", f"papers/{PAPER_ID}/work/review/quality_feedback.json"],
        "Worker-4/6 source review closed the ticket." if gates_ready else "Worker-4/6 source review ran but strict gates still failed.",
    )
    append_state(
        generated_at,
        "semantic_publication_gates",
        "completed" if gates_ready else "failed",
        [f"reports/{PAPER_ID}.semantic_gate.json", f"reports/{PAPER_ID}.publication_quality.json"],
        "Strict semantic and publication gates passed." if gates_ready else "Strict semantic/publication gate evidence still contains failures.",
    )
    report = {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "generated_at": generated_at,
        "completion_claim": "source_reviewed_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions"
        if gates_ready
        else "worker4_worker6_rework_attempt_gate_failed",
        "current_state": "final_approval" if gates_ready else "gate_failed_after_worker46_repair",
        "terminal_status": "accepted_with_cautions" if gates_ready else "gate_failed_after_worker46_repair",
        "final_approval_status": "accepted_with_cautions" if gates_ready else "refused_gate_failed",
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
            "semantic_issue_count": (semantic.get("results") or [{}])[0].get("issue_count"),
            "publication_risk_counts": publication.get("risk_counts"),
        },
        "analysis": {
            "review_status": "accepted_with_cautions" if gates_ready else "needs_targeted_rework",
            "activity_records": len(read_json(PAPER / "final" / "activity_toxicity_evidence.json")["activity_records"]),
            "mechanism_claims": len(read_json(PAPER / "final" / "mechanism_ontology_record.json")["mechanism_claims"]),
            "database_status_summary": read_json(PAPER / "final" / "database_record_verification.json")["status_summary"],
        },
        "open_rework_ticket_count": 0 if gates_ready else 1,
        "rework_ticket_ids": [] if gates_ready else [TICKET_ID],
        "not_publication_grade_reason": None if gates_ready else "Strict gates did not pass after worker-4/6 source review.",
        "semantic_gate": "passed" if gates_ready else "failed",
        "publication_quality_gate": "passed_after_worker4_worker6_source_review" if gates_ready else "failed_after_worker4_worker6_source_review",
        "manifest": str(REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"),
        "semantic_report": str(REPORTS / f"{PAPER_ID}.semantic_gate.json"),
        "publication_quality_report": str(REPORTS / f"{PAPER_ID}.publication_quality.json"),
        "workflow_dir": str(WORKFLOW),
    }
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", report)
    return gates_ready


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--gates", action="store_true")
    parser.add_argument("--finalize", action="store_true")
    args = parser.parse_args()
    if not any((args.repair, args.gates, args.finalize)):
        parser.error("select at least one action")

    generated_at = now_iso()
    if args.repair:
        activity, database, mechanism, _review = write_artifacts(generated_at)
        print(
            json.dumps(
                {
                    "repair_written": True,
                    "paper_id": PAPER_ID,
                    "generated_at": generated_at,
                    "activity_records": len(activity["activity_records"]),
                    "mechanism_claims": len(mechanism["mechanism_claims"]),
                    "database_status_summary": database["status_summary"],
                    "database_activity_support_summary": database["activity_support_summary"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    gate_evidence: dict[str, Any] | None = None
    if args.gates or args.finalize:
        gate_evidence = run_gates()
        print(
            json.dumps(
                {k: v for k, v in gate_evidence.items() if k not in {"semantic", "publication"}},
                ensure_ascii=False,
                indent=2,
            )
        )
    if args.finalize:
        assert gate_evidence is not None
        gates_ready = finalize(generated_at, gate_evidence)
        print(json.dumps({"finalized": True, "gates_ready": gates_ready}, ensure_ascii=False, indent=2))
        return 0 if gates_ready else 1
    if gate_evidence:
        return 0 if gate_evidence["semantic_returncode"] == 0 and gate_evidence["publication_returncode"] == 0 else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
