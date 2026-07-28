#!/usr/bin/env python3
"""Worker-4/6 bounded re-review for doi__10.1038_s41522-024-00637-y.

This repair keeps the paper non-accepted because local materials do not expose
the exact DJK-5 sequence or the supplementary table/figure files referenced by
the article.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "doi__10.1038_s41522-024-00637-y"
DOI = "10.1038/s41522-024-00637-y"
ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
REPORTS = ROOT / "reports"
LANDED = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers") / PAPER_ID

REVIEW_TICKET_ID = "rwk-complete-test-0001"
SUPP_TICKET_ID = "rwk-worker46-20260503-local-supplement-gap"
DB_TICKET_ID = "rwk-worker46-20260503-database-sequence-gap"
OPEN_TICKET_IDS = [REVIEW_TICKET_ID, SUPP_TICKET_ID, DB_TICKET_ID]

SOURCE_INPUTS_CHECKED = [
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
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    str(LANDED / "asset_manifest.csv"),
    str(LANDED / "metadata.json"),
    str(LANDED / "xml" / "local-DBAASP-PMC11711674.xml"),
    str(LANDED / "pdf" / "local-DBAASP-PMC11711674.pdf"),
    str(LANDED / "supplementary"),
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
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=False) + "\n")


def locator(source_path: str, loc: str, note: str | None = None) -> dict[str, str]:
    item = {"source_path": source_path, "locator": loc}
    if note:
        item["note"] = note
    return item


def build_activity(generated_at: str) -> dict[str, Any]:
    table_note = (
        "Table 1 reports planktonic MIC values in MHB and DFG and unitless FICI "
        "for colistin/DJK-5; supplementary daptomycin/DJK-5 table values are not "
        "locally recoverable."
    )
    rows = [
        ("pa-colistin-mhb", "Colistin", "MIC", "3.13", "μg/mL", "P. aeruginosa LESB58", "Pseudomonas aeruginosa LESB58", "MHB", "xml:table=1:row=4:column=1"),
        ("pa-colistin-dfg", "Colistin", "MIC", "12.5", "μg/mL", "P. aeruginosa LESB58", "Pseudomonas aeruginosa LESB58", "DFG", "xml:table=1:row=4:column=2"),
        ("pa-djk5-mhb", "DJK-5", "MIC", "50", "μg/mL", "P. aeruginosa LESB58", "Pseudomonas aeruginosa LESB58", "MHB", "xml:table=1:row=4:column=3"),
        ("pa-djk5-dfg", "DJK-5", "MIC", "100", "μg/mL", "P. aeruginosa LESB58", "Pseudomonas aeruginosa LESB58", "DFG", "xml:table=1:row=4:column=4"),
        ("pa-colistin-djk5-mhb-fici", "Colistin/DJK-5", "FICI", "0.5", "unitless", "P. aeruginosa LESB58", "Pseudomonas aeruginosa LESB58", "MHB", "xml:table=1:row=4:column=5"),
        ("pa-colistin-djk5-dfg-fici", "Colistin/DJK-5", "FICI", "1", "unitless", "P. aeruginosa LESB58", "Pseudomonas aeruginosa LESB58", "DFG", "xml:table=1:row=4:column=6"),
        ("sa-colistin-mhb", "Colistin", "MIC", ">100", "μg/mL", "S. aureus USA300 LAC", "Staphylococcus aureus USA300 LAC", "MHB", "xml:table=1:row=5:column=1"),
        ("sa-colistin-dfg", "Colistin", "MIC", "250", "μg/mL", "S. aureus USA300 LAC", "Staphylococcus aureus USA300 LAC", "DFG", "xml:table=1:row=5:column=2"),
        ("sa-djk5-mhb", "DJK-5", "MIC", "25", "μg/mL", "S. aureus USA300 LAC", "Staphylococcus aureus USA300 LAC", "MHB", "xml:table=1:row=5:column=3"),
        ("sa-djk5-dfg", "DJK-5", "MIC", "6.25", "μg/mL", "S. aureus USA300 LAC", "Staphylococcus aureus USA300 LAC", "DFG", "xml:table=1:row=5:column=4"),
        ("sa-colistin-djk5-mhb-fici", "Colistin/DJK-5", "FICI", "1.56", "unitless", "S. aureus USA300 LAC", "Staphylococcus aureus USA300 LAC", "MHB", "xml:table=1:row=5:column=5"),
        ("sa-colistin-djk5-dfg-fici", "Colistin/DJK-5", "FICI", "0.75", "unitless", "S. aureus USA300 LAC", "Staphylococcus aureus USA300 LAC", "DFG", "xml:table=1:row=5:column=6"),
    ]
    activity_records: list[dict[str, Any]] = []
    for suffix, entity, endpoint, value, unit, source_species, species, medium, loc in rows:
        activity_records.append(
            {
                "record_id": f"{PAPER_ID}-table1-{suffix}",
                "entity": entity,
                "endpoint": endpoint,
                "raw_value": value,
                "raw_unit": unit,
                "normalization_status": "raw_source_value_preserved",
                "evidence_ladder": "in_vitro_assay_table",
                "target": {
                    "class": "bacteria",
                    "species": species,
                    "strain": species,
                    "source_label": source_species,
                },
                "assay_conditions": {
                    "source_table": "Table 1",
                    "medium": medium,
                    "source_column_context": table_note,
                },
                "source_locator": locator("source/paper.xml", loc, "Primary XML Table 1; PDF text was also checked."),
            }
        )
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 source-reviewed final activity rows limited to values recoverable from local Table 1.",
        "activity_records": activity_records,
        "toxicity_records": [],
        "unsupported_activity_sources": [
            {
                "source": "Supplementary Table 1 and Supplementary Figs. 1-13",
                "status": "not_locally_recoverable",
                "reason": "The article references supplementary activity/figure evidence, but local supplementary assets are HTML article landing pages and no source table/figure file is available in the packet or landed paper directory.",
                "source_paths_checked": [
                    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
                    f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
                    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
                    str(LANDED / "supplementary"),
                ],
            }
        ],
    }


TABLE1_SUPPORTED_SOURCE_RECORD_IDS = {
    "184644",
    "184645",
    "184646",
    "184647",
    "184648",
    "184649",
    "184650",
    "184651",
    "5271",
    "5272",
    "5273",
    "5274",
}


TABLE1_LOCATORS = {
    "184648": "xml:table=1:row=4:column=1",
    "184649": "xml:table=1:row=4:column=2",
    "184644": "xml:table=1:row=4:column=3",
    "184645": "xml:table=1:row=4:column=4",
    "5271": "xml:table=1:row=4:column=5",
    "5272": "xml:table=1:row=4:column=6",
    "184650": "xml:table=1:row=5:column=1",
    "184651": "xml:table=1:row=5:column=2",
    "184646": "xml:table=1:row=5:column=3",
    "184647": "xml:table=1:row=5:column=4",
    "5273": "xml:table=1:row=5:column=5",
    "5274": "xml:table=1:row=5:column=6",
}


def source_record_id(row: dict[str, Any]) -> str:
    return str(row.get("source_record_id") or row.get("assay_id") or row.get("article_id") or "")


def classify_database_row(row: dict[str, Any], table: str) -> tuple[str, str, str, dict[str, str] | None]:
    record_id = source_record_id(row)
    sequence_key = str(row.get("sequence_key") or "")
    source_id = str(row.get("source_id") or row.get("dbaasp_id") or "")
    if table == "linked_literature_records.jsonl":
        return (
            "database_only_no_primary_source",
            "article_link_verified_sequence_not_primary_sourced",
            "Literature DOI/PMID/PMCID match this paper, but the linked sequence identity is not source-verified because local primary material lacks exact sequence/modification evidence.",
            locator("source/paper.xml", "xml:article-meta"),
        )
    if record_id in TABLE1_SUPPORTED_SOURCE_RECORD_IDS:
        return (
            "database_only_no_primary_source",
            "source_value_verified_sequence_not_primary_sourced",
            "The database row value maps to primary Table 1, but exact peptide/compound sequence evidence is absent from local primary material and linked_sequence_records.jsonl is empty.",
            locator("source/paper.xml", TABLE1_LOCATORS[record_id]),
        )
    if sequence_key == "DBAASP:DBAASPS_11338" and record_id.startswith("526"):
        return (
            "unresolved_record",
            "synergy_partner_ambiguous_or_supplement_unavailable",
            "DBAASP DJK-5 synergy rows do not identify the partner drug in the local snapshot. Some FICI values overlap Table 1, while additional values appear to require the missing supplementary table.",
            locator("source/paper.xml", "xml:table=1", "Main Table 1 checked; supplementary table unavailable locally."),
        )
    if source_id == "DBAASPN_20908" or sequence_key == "DBAASP:DBAASPN_20908":
        return (
            "unresolved_record",
            "daptomycin_exact_values_require_missing_supplement",
            "The primary text discusses daptomycin/DJK-5 and figures, but exact planktonic MIC/FICI values are referenced to Supplementary Table 1, which is not locally recoverable.",
            locator("source/paper.xml", "xml:sec=9; xml:sec=16", "Daptomycin/DJK-5 text and methods checked; Supplementary Table 1 file absent locally."),
        )
    return (
        "unresolved_record",
        "not_row_level_source_verified",
        "The local source review could not map this database row to a unique source table value.",
        locator("source/paper.xml", "xml:table=1"),
    )


def build_database(generated_at: str) -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    for table in ("linked_assay_records.jsonl", "linked_experiment_records.jsonl", "linked_literature_records.jsonl"):
        rows = read_jsonl(PACKET / "database" / table)
        for idx, row in enumerate(rows, start=1):
            status, support_status, note, source_value_locator = classify_database_row(row, table)
            sequence_key = str(row.get("sequence_key") or "")
            source_id = str(row.get("source_id") or row.get("dbaasp_id") or "")
            subject = str(row.get("subject_name") or row.get("target_organism_text") or row.get("title") or row.get("article_title") or "")
            measure = str(row.get("measure_group") or row.get("assay_text") or "")
            if row.get("concentration"):
                measure = f"{measure}; concentration={row.get('concentration')}"
            if row.get("fici"):
                measure = f"{measure}; fici={row.get('fici')}"
            audit = {
                "source_table": table,
                "source_id": f"DBAASP:{source_id}" if source_id and not source_id.startswith("DBAASP:") else source_id,
                "sequence_key": sequence_key,
                "database_subject": subject,
                "database_measure": measure.strip("; "),
                "status": status,
                "layer1_status": status,
                "source_value_support_status": support_status,
                "traceability": locator(
                    str(PACKET / "database" / table),
                    f"database:{table.replace('.jsonl', '')}:row={idx}",
                ),
                "citation_traceability": locator("source/paper.xml", "xml:article-meta"),
                "sequence_check": {
                    "status": "not_primary_source_verified",
                    "source_locator": locator(
                        "source/paper.xml",
                        "xml:sec=3:Introduction; xml:sec=16:Antimicrobial activity of colistin and DJK-5",
                        "Primary source names DJK-5 and reports D-enantiomeric peptide context but does not embed exact sequence/modification.",
                    ),
                    "linked_sequence_records": "absent",
                    "primary_source_statement": "Exact DJK-5 sequence/modification evidence is not embedded in extracted local XML/PDF, and linked_sequence_records.jsonl is empty.",
                },
                "source_value_locator": source_value_locator,
                "review_notes": note,
                "conflict_context": note,
            }
            audits.append(audit)
    counts = Counter(audit["status"] for audit in audits)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "audit_scope": "Worker-4 source-reviewed linked DBAASP assay/experiment/literature rows against local XML/PDF Table 1, article text, local supplementary inventory, and linked database snapshots.",
        "database_row_counts": read_json(PACKET / "database" / "database_source_manifest.json")["row_counts"],
        "record_audits": audits,
        "status_summary": dict(sorted(counts.items())),
        "source_inputs_checked": SOURCE_INPUTS_CHECKED,
        "unrecoverable_material_gaps": [
            "database_sequence_records_absent_primary_sequence_not_embedded",
            "supplementary_table_1_not_locally_recoverable_for_daptomycin_rows",
        ],
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 source-reviewed mechanism claims from local XML/PDF result sections, figure captions, and methods; missing supplementary figure files are not used to fabricate exact values.",
        "mechanism_claims": [
            {
                "claim_id": "mech-001",
                "entity_scope": "DJK-5 background mechanism context",
                "claim_text": "The article frames DJK-5 as a D-enantiomeric anti-biofilm peptide with prior evidence for membrane permeabilization/enhanced uptake and ppGpp/stringent-response effects.",
                "evidence_class": "background_mechanism_context",
                "source_locator": locator("source/paper.xml", "xml:sec=3:Introduction"),
                "limitations": "Recorded as background from cited prior work, not as a new direct mechanism proven solely by this paper.",
            },
            {
                "claim_id": "mech-002",
                "entity_scope": "colistin/DJK-5 co-biofilm treatment",
                "claim_text": "Inducing stringent stress response with serine hydroxamate attenuated the colistin/DJK-5 combinatory effect, supporting an indirect stringent-stress-response context.",
                "evidence_class": "indirect_mechanism_context",
                "source_locator": locator("source/paper.xml", "xml:sec=7:Inducing stringent stress response attenuated th; xml:fig=3:Fig. 3"),
                "limitations": "Perturbation evidence supports context for the combination effect but does not establish a sole molecular target.",
            },
            {
                "claim_id": "mech-003",
                "entity_scope": "P. aeruginosa and S. aureus co-biofilms",
                "claim_text": "SEM evidence supports treatment-associated cell deformation, damaged membrane morphology, and debris after colistin/DJK-5 exposure in co-biofilm settings.",
                "evidence_class": "direct_mechanism",
                "direct_assay_types": ["scanning electron microscopy"],
                "source_locator": locator("source/paper.xml", "xml:sec=10:Colistin combined with DJK-5 caused cell deforma; xml:fig=6:Fig. 6"),
                "limitations": "Morphology supports membrane/cell-envelope damage context but does not quantify a pore model.",
            },
            {
                "claim_id": "mech-004",
                "entity_scope": "S. aureus in co-biofilms",
                "claim_text": "A LacZ leakage assay in co-biofilm supernatant supports increased membrane leakage after DJK-5 and colistin/DJK-5 treatment.",
                "evidence_class": "direct_mechanism",
                "direct_assay_types": ["LacZ membrane leakage assay"],
                "source_locator": locator("source/paper.xml", "xml:sec=11:Membrane leakage in co-biofilms indicated the sy; xml:sec=20:Membrane leakage assay"),
                "limitations": "Main text reports fold-change direction; missing local supplementary figure prevents replotting exact underlying points.",
            },
            {
                "claim_id": "mech-005",
                "entity_scope": "colistin/DJK-5 and daptomycin/DJK-5 combinations",
                "claim_text": "The study reports biofilm and in vivo synergy contexts for DJK-5 combinations with colistin or daptomycin against mixed P. aeruginosa/S. aureus infections.",
                "evidence_class": "phenotypic_synergy_context",
                "source_locator": locator("source/paper.xml", "xml:sec=6:Colistin combined with DJK-5 exhibited synergist; xml:sec=9:The Gram-positive bacteria targeting antibiotic; xml:sec=12:Colistin combined with DJK-5 demonstrated synerg"),
                "limitations": "Kept as phenotypic activity/mechanism context; exact daptomycin planktonic Supplementary Table 1 values are not locally recoverable.",
            },
        ],
    }


def unrecoverable_gaps() -> list[dict[str, Any]]:
    return [
        {
            "gap_code": "supplementary_table_and_figures_not_locally_recoverable",
            "source_paths_checked": [
                f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
                str(LANDED / "asset_manifest.csv"),
                str(LANDED / "metadata.json"),
                str(LANDED / "supplementary" / "landing-1.bin"),
                str(LANDED / "supplementary" / "landing-10.bin"),
                str(LANDED / "supplementary"),
                f"papers/{PAPER_ID}/source/paper.xml",
                f"papers/{PAPER_ID}/source/paper.pdf",
            ],
            "tools_attempted": ["jq", "rg", "file", "sha256/hash comparison", "existing pdftotext extraction review"],
            "why_unrecoverable": "All ten local supplementary .bin assets are article HTML landing pages, supplementary_text.jsonl is indexed_only for those assets, supplementary_tables.json has no structured table, and metadata records the PMC OA package fetch failure. The local packet therefore cannot support Supplementary Table 1 or Supplementary Figs. 1-13 exact values.",
            "impact": "Daptomycin/DJK-5 Supplementary Table 1 MIC/FICI rows and supplementary figure exact values cannot be source-reviewed from local material.",
            "owner_worker": "worker-3",
            "blocks_publication_grade": True,
            "next_action": "record_and_continue",
        },
        {
            "gap_code": "database_sequence_records_absent_primary_sequence_not_embedded",
            "source_paths_checked": [
                f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
                f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
                f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
                f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
                f"papers/{PAPER_ID}/source/paper.xml",
                f"papers/{PAPER_ID}/source/paper.pdf",
                f"paper_packets/{PAPER_ID}/extracted/pdf_text/landing-1.txt",
                f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
            ],
            "tools_attempted": ["jq", "rg", "database JSONL row review", "XML/PDF text search"],
            "why_unrecoverable": "The source article names DJK-5 and reports D-enantiomeric peptide context, but no exact DJK-5 sequence/modification is embedded in the local primary XML/PDF and linked_sequence_records.jsonl has zero rows.",
            "impact": "Linked DBAASP sequence identifiers cannot be marked source_verified; database rows remain database_only_no_primary_source or unresolved_record.",
            "owner_worker": "worker-4",
            "blocks_publication_grade": True,
            "next_action": "record_and_continue",
        },
    ]


def rework_targets(generated_at: str) -> list[dict[str, Any]]:
    return [
        {
            "ticket_id": SUPP_TICKET_ID,
            "paper_id": PAPER_ID,
            "created_at": generated_at,
            "worker": "worker-3",
            "owner_worker": "worker-3",
            "target_queue": "material_extraction",
            "layer": "material_packet",
            "severity": "blocking",
            "failure_code": "supplementary_table_and_figures_not_locally_recoverable",
            "omission_code": "missing_supplementary_table_1_and_figures_1_13",
            "artifact_path": f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
            "source_paths_to_check": [
                f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
                str(LANDED / "supplementary"),
                str(LANDED / "metadata.json"),
            ],
            "required_action": "No further local retry unless an external/recovered supplement or OA package is supplied; current local material supports only an unrecoverable gap.",
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
            "failure_code": "database_sequence_records_absent_primary_sequence_not_embedded",
            "omission_code": "missing_primary_sequence_locator_for_dbaasp_sequence_ids",
            "artifact_path": f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
            "source_paths_to_check": [
                f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
                f"papers/{PAPER_ID}/source/paper.xml",
                f"papers/{PAPER_ID}/source/paper.pdf",
            ],
            "required_action": "Keep DBAASP sequence-linked rows non-source_verified unless exact sequence/modification evidence is supplied from primary or linked database sequence material.",
            "blocks": ["publication_grade_ready", "final_approval"],
        },
    ]


def build_review(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> dict[str, Any]:
    gaps = unrecoverable_gaps()
    targets = rework_targets(generated_at)
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "blocked_missing_primary_material",
        "publication_grade": False,
        "validator_contract_passed": True,
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
            "note": "Local XML/PDF, extracted text/tables, figure captions, landing supplementary assets, and linked DBAASP rows were checked. Supported Table 1 and main-text claims are preserved; missing supplementary table/figure files and absent sequence records block publication-grade acceptance.",
        },
        "checked_inputs": SOURCE_INPUTS_CHECKED,
        "semantic_quality_checks": {
            "activity_rows_source_reviewed": len(activity["activity_records"]),
            "database_record_status_summary": database["status_summary"],
            "mechanism_claims_source_reviewed": len(mechanism["mechanism_claims"]),
            "open_rework_targets": len(targets),
            "unrecoverable_material_gap_count": len(gaps),
        },
        "per_layer_decision_rationale": {
            "layer_1_database": "Worker-4 rechecked linked DBAASP rows against local Table 1, article metadata, and database snapshots. Source-supported values are preserved, but exact sequence/modification support is absent, so rows are not promoted to source_verified.",
            "layer_2_activity_toxicity": "Worker-6 preserves local Table 1 MIC/FICI values with units and locators. Supplementary Table 1 and supplementary figure values cannot be recovered locally and are not fabricated.",
            "layer_3_mechanism": "Worker-6 replaced automated placeholder mechanism notes with source-reviewed main-text mechanism context and direct SEM/LacZ assay locators, while preserving missing supplementary figure limitations.",
            "publication_decision": "The owner-layer repair is bounded and source-reviewed, but two unrecoverable material gaps block publication-grade acceptance under obtainable-only mode.",
        },
        "caution_findings": [
            {
                "caution_code": "database_sequence_not_primary_sourced",
                "evidence_context": "DJK-5 name and D-enantiomeric context are present in the source article, but exact sequence/modification evidence is absent from local primary and linked sequence artifacts.",
            },
            {
                "caution_code": "supplementary_assets_are_article_landing_html",
                "evidence_context": "The ten local supplementary .bin files were opened/classified and are article landing HTML; they do not contain Supplementary Table 1 or figure data.",
            },
            {
                "caution_code": "database_daptomycin_rows_require_missing_supplement",
                "evidence_context": "Daptomycin/DJK-5 exact planktonic MIC/FICI values appear to depend on Supplementary Table 1 and remain unresolved.",
            },
        ],
        "qc_failure_reasons": [
            {
                "code": "supplementary_table_and_figures_not_locally_recoverable",
                "owner_worker": "worker-3",
                "reason": "Local supplementary assets are HTML landing pages and no recoverable Supplementary Table 1/Figs. 1-13 source file exists in the packet or landed paper directory.",
                "severity": "blocking",
            },
            {
                "code": "database_sequence_records_absent_primary_sequence_not_embedded",
                "owner_worker": "worker-4",
                "reason": "Exact DJK-5 sequence/modification cannot be verified from local primary XML/PDF or linked sequence records.",
                "severity": "major",
            },
        ],
        "rework_targets": targets,
        "unrecoverable_material_gaps": gaps,
        "adjudication_summary": "Worker-4/6 source re-review repaired the overclaimed database/final layers and preserved supported local Table 1 and mechanism evidence. The paper remains non-publication-grade because local material cannot support the missing supplementary table/figure data or exact sequence verification.",
    }


def build_quality_feedback(generated_at: str) -> dict[str, Any]:
    targets = rework_targets(generated_at)
    reasons = [
        {
            "code": "supplementary_table_and_figures_not_locally_recoverable",
            "owner_worker": "worker-3",
            "reason": "Local supplementary assets are HTML landing pages; no local Supplementary Table 1 or supplementary figure source data can be extracted.",
            "severity": "blocking",
        },
        {
            "code": "database_sequence_records_absent_primary_sequence_not_embedded",
            "owner_worker": "worker-4",
            "reason": "DJK-5 exact sequence/modification is absent from local primary XML/PDF and linked_sequence_records.jsonl is empty.",
            "severity": "major",
        },
    ]
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": len(reasons),
        "qc_failure_reasons": reasons,
        "rework_context_packet_required": False,
        "rework_targets": targets,
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "status": "blocked_after_bounded_worker4_worker6_source_review",
        "notes": "Previous broad framework-test blocker was converted into concrete owner-layer evidence and unrecoverable material gaps. The paper must remain non-accepted under obtainable-only mode.",
    }


def build_rework_response(generated_at: str) -> dict[str, Any]:
    return {
        "record_type": "rework_response",
        "response_id": f"{PAPER_ID}-worker46-bounded-source-review-{generated_at}",
        "paper_id": PAPER_ID,
        "ticket_ids": [REVIEW_TICKET_ID],
        "created_ticket_ids": [SUPP_TICKET_ID, DB_TICKET_ID],
        "status": "bounded_repair_completed_nonaccepted_unrecoverable_gaps",
        "owner_workers": ["worker-4", "worker-6"],
        "resolved_by": "codex-cli",
        "state": "worker4_worker6_source_review_bounded_nonacceptance",
        "checked_source_paths": SOURCE_INPUTS_CHECKED,
        "tools_attempted": ["jq", "rg", "file", "sha256/hash comparison", "database JSONL review", "existing pdftotext extraction review"],
        "what_was_repaired": [
            "Rebuilt final/packet activity evidence to preserve local Table 1 MIC/FICI values without duplicate or generic column labels.",
            "Rebuilt worker-4 database audit so linked DBAASP rows are no longer overclaimed as source_verified when exact sequence or supplementary values are absent.",
            "Replaced automated mechanism placeholders with source-reviewed worker-6 mechanism claims and limitations.",
            "Rewrote final adjudication and quality feedback to blocked_missing_primary_material with concrete unrecoverable gaps.",
        ],
        "what_remains": [
            "Supplementary Table 1 and Supplementary Figs. 1-13 are not locally recoverable from packet/landed assets.",
            "Exact DJK-5 sequence/modification evidence is not locally recoverable from primary XML/PDF or linked_sequence_records.jsonl.",
            "Paper remains non-publication-grade and should not be accepted unless new local source material is supplied.",
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


def append_rework_requests(generated_at: str) -> None:
    existing = read_jsonl(PACKET / "rework" / "rework_requests.jsonl")
    existing_ids = {str(row.get("ticket_id")) for row in existing}
    for target in rework_targets(generated_at):
        if target["ticket_id"] not in existing_ids:
            append_jsonl(PACKET / "rework" / "rework_requests.jsonl", target)


def update_status_files(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> None:
    analysis_status_path = PACKET / "analysis" / "analysis_status.json"
    analysis_status = read_json(analysis_status_path)
    analysis_status.update(
        {
            "generated_at": generated_at,
            "status": "analysis_blocked_unrecoverable_material_gaps",
            "activity_record_count": len(activity["activity_records"]),
            "mechanism_claim_count": len(mechanism["mechanism_claims"]),
            "database_status_summary": database["status_summary"],
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
        ctx["queue_status"] = {
            "analysis": "analysis_blocked_unrecoverable_material_gaps",
            "material": "material_extracted_with_gaps",
        }
        ctx["gate_summary"] = {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": False,
            "publication_grade_ready": False,
        }
        write_json(WORKFLOW / "workflow_context.json", ctx)


def repair() -> None:
    generated_at = now_iso()
    activity = build_activity(generated_at)
    database = build_database(generated_at)
    mechanism = build_mechanism(generated_at)
    review = build_review(generated_at, activity, database, mechanism)
    feedback = build_quality_feedback(generated_at)

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
    write_json(PAPER / "work" / "review" / "quality_feedback.json", feedback)

    append_jsonl(PACKET / "rework" / "rework_responses.jsonl", build_rework_response(generated_at))
    append_rework_requests(generated_at)
    update_status_files(generated_at, activity, database, mechanism)
    print(json.dumps({"ok": True, "generated_at": generated_at, "status": "nonaccepted_unrecoverable_gaps_recorded"}, ensure_ascii=False, indent=2))


def finalize_gates() -> None:
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

    review_path = PAPER / "final" / "review_report.json"
    review = read_json(review_path)
    review["gate_validation"] = {
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
    write_json(review_path, review)
    write_json(PACKET / "analysis" / "adjudication_report.json", review)
    write_json(PACKET / "final" / "review_report.json", review)

    feedback_path = PAPER / "work" / "review" / "quality_feedback.json"
    feedback = read_json(feedback_path)
    feedback["gate_validation"] = review["gate_validation"]
    feedback["post_gate_status"] = "strict_gates_failed_expected_nonaccepted_unrecoverable_gaps"
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

    final_activity = read_json(PAPER / "final" / "activity_toxicity_evidence.json")
    final_database = read_json(PAPER / "final" / "database_record_verification.json")
    final_mechanism = read_json(PAPER / "final" / "mechanism_ontology_record.json")
    report = {
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
            "activity_records": len(final_activity.get("activity_records") or []),
            "mechanism_claims": len(final_mechanism.get("mechanism_claims") or []),
            "database_status_summary": final_database.get("status_summary"),
            "unrecoverable_material_gap_count": len(unrecoverable_gaps()),
        },
        "open_rework_ticket_count": len(OPEN_TICKET_IDS),
        "rework_ticket_ids": OPEN_TICKET_IDS,
        "not_publication_grade_reason": "Local source cannot support Supplementary Table/Figure files or exact DJK-5 sequence evidence after bounded worker-4/6 source review.",
        "semantic_gate": "passed" if gates_ready else "failed_expected_nonaccepted_unrecoverable_gaps",
        "publication_quality_gate": "passed" if gates_ready else "failed_expected_open_rework_and_nonpublication_grade",
        "manifest": str(REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"),
        "semantic_report": str(semantic_path),
        "publication_quality_report": str(publication_path),
        "workflow_dir": str(WORKFLOW),
    }
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", report)
    print(json.dumps({"ok": True, "gates_ready": gates_ready, "updated_report": str(REPORTS / f"{PAPER_ID}.complete_message_test_report.json")}, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["repair", "finalize-gates"])
    args = parser.parse_args()
    if args.mode == "repair":
        repair()
    else:
        finalize_gates()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
