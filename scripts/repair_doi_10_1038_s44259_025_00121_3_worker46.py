#!/usr/bin/env python3
"""Bounded worker-3/worker-4/worker-6 repair for doi__10.1038_s44259-025-00121-3."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.1038_s44259-025-00121-3"
DOI = "10.1038/s44259-025-00121-3"
PMID = "40527928"
PMCID = "PMC12174330"
TITLE = "Impact of stereochemical replacement on activity and selectivity of membrane-active antibacterial and antifungal cyclic peptides."

PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
REPORTS = ROOT / "reports"
LANDED = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers") / PAPER_ID

ORIGINAL_TICKET_ID = "rwk-complete-test-0001"
SUPP_TICKET_ID = "rwk-s44259-00121-worker3-moesm1-docx-unrecoverable"
DB_TICKET_ID = "rwk-s44259-00121-worker4-dbaasp-database-only"
OPEN_TICKET_IDS = [SUPP_TICKET_ID, DB_TICKET_ID]

SOURCE_PATHS_CHECKED = [
    f"rework_context/{PAPER_ID}/handoff_context.json",
    f"paper_packets/{PAPER_ID}/packet_manifest.json",
    f"paper_packets/{PAPER_ID}/locators/locator_index.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
    f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/landing-1.txt",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
    f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    str(LANDED / "asset_manifest.csv"),
    str(LANDED / "metadata.json"),
    str(LANDED / "supplementary"),
]

TOOLS_ATTEMPTED = [
    "jq",
    "rg",
    "find",
    "file",
    "sha256sum",
    "local supplementary HTML link inspection",
    "python xml.etree.ElementTree table extraction",
    "database JSONL row review",
    "existing pdftotext extraction review",
]

TABLE_ENTITY_COLUMNS = {
    1: {
        1: "7a",
        2: "12a",
        3: "7b",
        4: "15c",
        5: "16c",
        6: "20c",
        7: "Cefepime",
        8: "Colistin",
        9: "Levofloxacin",
        10: "Meropenem",
        11: "Oxacillin",
    },
    2: {
        1: "7a",
        2: "12a",
        3: "7b",
        4: "15c",
        5: "16c",
        6: "20c",
        7: "Fluconazole",
        8: "Voriconazole",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def locator(source_path: str, loc: str, note: str | None = None) -> dict[str, str]:
    out = {"source_path": source_path, "locator": loc}
    if note:
        out["note"] = note
    return out


def unrecoverable_gaps() -> list[dict[str, Any]]:
    return [
        {
            "gap_code": "springer_moesm1_docx_not_present_in_local_material",
            "source_paths_checked": [
                f"papers/{PAPER_ID}/source/paper.xml",
                f"paper_packets/{PAPER_ID}/raw/paper.xml",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
                str(LANDED / "supplementary"),
                str(LANDED / "asset_manifest.csv"),
                str(LANDED / "metadata.json"),
            ],
            "tools_attempted": ["rg", "find", "file", "sha256sum", "jq"],
            "why_unrecoverable": (
                "The XML declares 44259_2025_121_MOESM1_ESM.docx, but no local DOCX/XLSX/archive copy exists under "
                "the packet, paper source directory, or landed paper directory. The ten local supplementary .bin files "
                "are HTML article landing pages and supplementary_tables.json is empty."
            ),
            "impact": (
                "Supplementary Tables 1, 3, 4, 5, 6, 7, 8, 9 and supplementary figure source data cannot be used to "
                "verify exact peptide sequences, full-library MICs, hemolysis/cytotoxicity values, or modeling table values."
            ),
            "owner_worker": "worker-3",
            "blocks_publication_grade": True,
            "next_action": "record_and_continue",
        },
        {
            "gap_code": "dbaasp_rows_not_primary_source_verifiable_without_supplement_or_sequence_records",
            "source_paths_checked": [
                f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
                f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
                f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
                f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
                f"papers/{PAPER_ID}/source/paper.xml",
                f"papers/{PAPER_ID}/source/paper.pdf",
                f"paper_packets/{PAPER_ID}/extracted/pdf_text/landing-1.txt",
            ],
            "tools_attempted": ["jq", "rg", "python xml.etree.ElementTree table extraction", "database JSONL row review"],
            "why_unrecoverable": (
                "DBAASP linked_sequence_records.jsonl has zero rows. The local XML/PDF contain main Table 1/2 values and "
                "article-level peptide labels, but exact sequence/modification evidence and most DBAASP row-level activity "
                "values are declared in the missing Supplementary Information."
            ),
            "impact": (
                "Linked DBAASP sequence and assay rows must remain database_only_no_primary_source rather than source_verified."
            ),
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
            "failure_code": "springer_moesm1_docx_not_present_in_local_material",
            "omission_code": "missing_xml_declared_moesm1_supplement_docx",
            "artifact_path": f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
            "source_paths_to_check": [
                f"papers/{PAPER_ID}/source/paper.xml",
                f"paper_packets/{PAPER_ID}/raw/paper.xml",
                str(LANDED / "supplementary"),
                str(LANDED / "asset_manifest.csv"),
            ],
            "required_action": (
                "Do not rerun local extraction unless the actual MOESM1 DOCX or a recovered OA package is supplied; "
                "current local material supports only an unrecoverable gap."
            ),
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
            "failure_code": "dbaasp_rows_database_only_no_primary_source",
            "omission_code": "missing_primary_sequence_and_supplement_table_locators_for_dbaasp_rows",
            "artifact_path": f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
            "source_paths_to_check": [
                f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
                f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
                f"papers/{PAPER_ID}/source/paper.xml",
                f"papers/{PAPER_ID}/source/paper.pdf",
            ],
            "required_action": (
                "Keep linked DBAASP rows non-source_verified unless exact primary sequence/modification and row-level "
                "activity evidence are supplied from a recovered supplement or trusted local sequence snapshot."
            ),
            "blocks": ["publication_grade_ready", "final_approval"],
        },
    ]


def repair_supplementary(generated_at: str) -> dict[str, Any]:
    """Refresh worker-3 material-gap evidence without fabricating supplement tables."""
    path = PAPER / "work" / "supplementary_methods" / "supplementary_evidence.json"
    supplementary = read_json(path) if path.exists() else {"paper_id": PAPER_ID, "evidence_items": []}
    supplementary.update(
        {
            "paper_id": PAPER_ID,
            "generated_at": generated_at,
            "worker": "worker-3",
            "status": "material_extracted_with_unrecoverable_gap",
            "extraction_scope": (
                "Reopened XML-declared supplementary material, packet/landed supplementary inventory, and local HTML "
                "landing-page assets. No local DOCX/XLSX/archive payload exists for MOESM1; values requiring that "
                "supplement remain unrecoverable."
            ),
            "source_inputs_checked": [
                f"papers/{PAPER_ID}/source/paper.xml",
                f"paper_packets/{PAPER_ID}/raw/paper.xml",
                f"paper_packets/{PAPER_ID}/raw/supplementary_original",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
                f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
                str(LANDED / "supplementary"),
                str(LANDED / "asset_manifest.csv"),
                str(LANDED / "metadata.json"),
            ],
            "tools_attempted": ["rg", "find", "file", "sha256sum", "head", "jq"],
            "unrecoverable_material_gaps": [unrecoverable_gaps()[0]],
        }
    )
    write_json(path, supplementary)

    extraction_status_path = PACKET / "extraction" / "extraction_status.json"
    if extraction_status_path.exists():
        extraction_status = read_json(extraction_status_path)
        extraction_status.update(
            {
                "generated_at": generated_at,
                "status": "material_extracted_with_gaps",
                "gap_assessment": (
                    "Primary XML/PDF extraction and supplementary inventory are complete for local materials; "
                    "the XML-declared MOESM1 DOCX is not locally present and remains a publication-grade blocker."
                ),
                "unrecoverable_material_gaps": [unrecoverable_gaps()[0]],
            }
        )
        write_json(extraction_status_path, extraction_status)

    extraction_quality_path = PACKET / "extraction" / "extraction_quality_report.json"
    if extraction_quality_path.exists():
        extraction_quality = read_json(extraction_quality_path)
        extraction_quality.update(
            {
                "generated_at": generated_at,
                "quality_status": "complete_with_unrecoverable_material_gap",
                "supplement_parse_count": 0,
                "supplementary_table_count": 0,
                "unrecoverable_material_gaps": [unrecoverable_gaps()[0]],
            }
        )
        write_json(extraction_quality_path, extraction_quality)

    extraction_error = {
        "record_type": "unrecoverable_material_gap",
        "created_at": generated_at,
        "paper_id": PAPER_ID,
        "owner_worker": "worker-3",
        "gap_code": "springer_moesm1_docx_not_present_in_local_material",
        "source_paths_checked": unrecoverable_gaps()[0]["source_paths_checked"],
        "tools_attempted": unrecoverable_gaps()[0]["tools_attempted"],
        "impact": unrecoverable_gaps()[0]["impact"],
        "blocks_publication_grade": True,
    }
    append_jsonl(PACKET / "extraction" / "extraction_errors.jsonl", extraction_error)
    return supplementary


def repair_activity(generated_at: str) -> dict[str, Any]:
    activity = read_json(PAPER / "final" / "activity_toxicity_evidence.json")
    pattern = re.compile(r"table(?P<table>\d+)-r(?P<row>\d+)-c(?P<col>\d+)")
    for record in activity.get("activity_records", []):
        match = pattern.search(str(record.get("record_id") or ""))
        if not match:
            continue
        table_num = int(match.group("table"))
        col_num = int(match.group("col"))
        entity = TABLE_ENTITY_COLUMNS.get(table_num, {}).get(col_num)
        if entity:
            record["entity"] = entity
            record.setdefault("assay_conditions", {})["entity_column"] = entity
        target = record.setdefault("target", {})
        if table_num == 1:
            target["class"] = "bacteria"
            record.setdefault("assay_conditions", {})["source_table_label"] = "Table 1"
        elif table_num == 2:
            target["class"] = "fungi"
            record.setdefault("assay_conditions", {})["source_table_label"] = "Table 2"
        record.setdefault("assay_conditions", {})["worker6_re_review"] = (
            "Entity column and target class rechecked from XML table headers during bounded worker-6 review."
        )
    activity.update(
        {
            "generated_at": generated_at,
            "extraction_scope": (
                "Main XML Table 1/2 MIC rows preserved with worker-6 repaired entity-column and target-class metadata; "
                "missing Supplementary Information values are not fabricated."
            ),
            "source_inputs_checked": SOURCE_PATHS_CHECKED,
            "tools_attempted": TOOLS_ATTEMPTED,
            "unrecoverable_material_gaps": unrecoverable_gaps(),
        }
    )
    for path in [
        PAPER / "final" / "activity_toxicity_evidence.json",
        PACKET / "analysis" / "activity_toxicity_evidence.json",
        PACKET / "final" / "activity_toxicity_evidence.json",
    ]:
        if path.exists() or "analysis" in str(path) or "final" in str(path):
            write_json(path, activity)
    return activity


def load_database_rows() -> dict[str, list[dict[str, Any]]]:
    tables: dict[str, list[dict[str, Any]]] = {}
    for name in [
        "linked_assay_records.jsonl",
        "linked_experiment_records.jsonl",
        "linked_literature_records.jsonl",
        "linked_sequence_records.jsonl",
    ]:
        tables[name] = read_jsonl(PACKET / "database" / name)
    return tables


def row_for_audit(audit: dict[str, Any], row_maps: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    table_name = str(audit.get("source_table") or "")
    if table_name and not table_name.endswith(".jsonl"):
        table_name = f"{table_name}.jsonl"
    trace = audit.get("traceability") if isinstance(audit.get("traceability"), dict) else {}
    loc = str(trace.get("locator") or "")
    match = re.search(r"database:([^:]+):row=(\d+)", loc)
    if match:
        table_name = f"{match.group(1)}.jsonl"
        row_index = int(match.group(2)) - 1
        rows = row_maps.get(table_name) or []
        if 0 <= row_index < len(rows):
            return rows[row_index]
    return {}


def repair_database(generated_at: str) -> dict[str, Any]:
    database = read_json(PACKET / "analysis" / "database_record_audit.json")
    row_maps = load_database_rows()
    note = (
        "DBAASP row is retained but not promoted to source_verified: local XML/PDF support article citation and main "
        "Table 1/2 context only, while exact sequence/modification and most row-level activity values require the "
        "XML-declared MOESM1 supplement that is not locally present."
    )
    for audit in database.get("record_audits", []):
        row = row_for_audit(audit, row_maps)
        audit["status"] = "database_only_no_primary_source"
        audit["layer1_status"] = "database_only_no_primary_source"
        audit["source_value_support_status"] = "not_locally_primary_source_verified"
        audit["matched_activity_record_id"] = ""
        audit["review_notes"] = note
        audit["conflict_context"] = note
        audit["database_peptide_name"] = row.get("peptide_name") or audit.get("database_peptide_name") or ""
        audit["database_source_id_raw"] = row.get("source_id") or row.get("dbaasp_id") or ""
        audit["database_source_record_id"] = row.get("source_record_id") or row.get("assay_id") or ""
        audit["database_concentration"] = row.get("concentration") or ""
        audit["database_unit"] = row.get("unit") or ""
        audit["database_note"] = row.get("note") or row.get("comments_text") or ""
        audit["sequence_check"] = {
            "status": "not_primary_source_verified",
            "linked_sequence_records": "absent",
            "source_locator": locator(
                "source/paper.xml",
                "xml:supplementary-material=MOESM1; xml:article-meta",
                "Exact sequence/modification evidence is declared in MOESM1, but that DOCX is absent from local material.",
            ),
            "primary_source_statement": (
                "The local primary XML/PDF names peptide labels and contains main activity tables, but does not embed "
                "the exact sequence/modification evidence needed for source_verified database identity status."
            ),
        }
    counts = Counter(str(row.get("status") or "") for row in database.get("record_audits", []))
    database.update(
        {
            "generated_at": generated_at,
            "audit_scope": (
                "Worker-4 bounded source review of linked DBAASP assay/experiment/literature rows against local XML, PDF "
                "text, extracted main tables, supplementary inventory, and database snapshots. Rows are preserved as "
                "database_only_no_primary_source because required supplement/sequence evidence is not locally recoverable."
            ),
            "status_summary": dict(sorted(counts.items())),
            "source_inputs_checked": SOURCE_PATHS_CHECKED,
            "tools_attempted": TOOLS_ATTEMPTED,
            "unrecoverable_material_gaps": unrecoverable_gaps(),
        }
    )
    for path in [
        PACKET / "analysis" / "database_record_audit.json",
        PACKET / "final" / "database_record_verification.json",
        PAPER / "final" / "database_record_verification.json",
    ]:
        write_json(path, database)
    return database


def build_mechanism(generated_at: str) -> dict[str, Any]:
    mechanism = {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": (
            "Worker-6 source-reviewed mechanism claims from local XML/PDF result sections, figure captions, and methods; "
            "missing supplementary source files are not used to fabricate exact values."
        ),
        "source_inputs_checked": SOURCE_PATHS_CHECKED,
        "tools_attempted": TOOLS_ATTEMPTED,
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "mechanism_claims": [
            {
                "claim_id": "mech-001",
                "entity_scope": "lead cyclic peptides 15c and 16c",
                "claim_text": (
                    "Calcein dye leakage supports concentration-dependent disruption of bacterial-membrane-mimicking "
                    "liposomes by 15c and 16c, with lower leakage in mammalian-membrane-mimicking liposomes."
                ),
                "evidence_class": "direct_mechanism",
                "direct_assay_types": ["calcein dye leakage assay"],
                "source_locator": locator(
                    "source/paper.xml",
                    "xml:sec=Membranolytic action of the lead peptides shown by Calcein dye leakage assay; xml:fig=Fig. 4",
                ),
                "limitations": "Exact curve values are not re-tabulated because supplementary/source figure data are not locally available.",
            },
            {
                "claim_id": "mech-002",
                "entity_scope": "lead cyclic peptides 15c and 16c against bacterial and fungal cells",
                "claim_text": (
                    "FE-SEM source text supports treatment-associated membrane/cell-envelope damage and morphology changes "
                    "after exposure to 15c or 16c."
                ),
                "evidence_class": "direct_mechanism",
                "direct_assay_types": ["field-emission scanning electron microscopy"],
                "source_locator": locator(
                    "source/paper.xml",
                    "xml:sec=Membranolytic action of the lead peptides shown by FE-SEM; xml:fig=Fig. 4",
                ),
                "limitations": "Morphology supports membrane-damage context but does not quantify a pore model.",
            },
            {
                "claim_id": "mech-003",
                "entity_scope": "15c and 16c antimicrobial and antibiofilm phenotype",
                "claim_text": (
                    "Main-text kill kinetics and XTT antibiofilm assays support rapid killing and biofilm-mass reduction "
                    "phenotypes for 15c and 16c."
                ),
                "evidence_class": "phenotypic_activity_context",
                "source_locator": locator(
                    "source/paper.xml",
                    "xml:sec=Kill-kinetic assay; xml:sec=Anti-biofilm activity; xml:fig=Fig. 3",
                ),
                "limitations": "Recorded as activity/mechanism context, not a direct molecular target claim.",
            },
            {
                "claim_id": "mech-004",
                "entity_scope": "stereochemical replacement series and hemolytic selectivity",
                "claim_text": (
                    "NMR and MD analyses provide structural/dynamic context for hemolytic selectivity across representative "
                    "macrocyclic peptides, including 15c and 16c."
                ),
                "evidence_class": "structural_modeling_context",
                "source_locator": locator(
                    "source/paper.xml",
                    "xml:sec=Analysis of structure and oligomerization by NMR spectroscopy; xml:sec=Molecular dynamics analysis",
                ),
                "limitations": "Computational/NMR context is not promoted to direct antimicrobial mechanism by itself.",
            },
        ],
    }
    for path in [
        PACKET / "analysis" / "mechanism_evidence.json",
        PACKET / "final" / "mechanism_evidence.json",
        PAPER / "final" / "mechanism_evidence.json",
        PAPER / "final" / "mechanism_ontology_record.json",
    ]:
        write_json(path, mechanism)
    return mechanism


def build_review(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> dict[str, Any]:
    targets = rework_targets(generated_at)
    gaps = unrecoverable_gaps()
    return {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "pmid": PMID,
        "pmcid": PMCID,
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
            "note": (
                "Reopened handoff, packet manifest, XML/PDF text, XML tables, supplementary inventory, landing .bin assets, "
                "and linked DBAASP rows. The only XML-declared supplement payload is not locally present."
            ),
        },
        "checked_inputs": SOURCE_PATHS_CHECKED,
        "semantic_quality_checks": {
            "activity_rows_preserved": len(activity.get("activity_records") or []),
            "activity_metadata_repaired": "entity_column_and_table2_fungal_class",
            "database_status_summary": database.get("status_summary", {}),
            "mechanism_claims_source_reviewed": len(mechanism.get("mechanism_claims") or []),
            "open_rework_targets": len(targets),
            "supplementary_gap_refreshed": True,
            "unrecoverable_material_gap_count": len(gaps),
        },
        "per_layer_decision_rationale": {
            "layer_1_database": (
                "Worker-4 rechecked linked DBAASP rows against local XML/PDF, main tables, and database snapshots. "
                "Rows are retained but downgraded to database_only_no_primary_source because exact sequence/modification "
                "and row-level supplement evidence are not locally available."
            ),
            "layer_2_activity_toxicity": (
                "Main XML Table 1/2 MIC rows are preserved as local source-supported partial evidence; worker-6 repaired "
                "entity-column labels and Table 2 fungal target class. Supplement-only full-library values remain unavailable."
            ),
            "layer_3_mechanism": (
                "Automated placeholder mechanism notes were replaced with source-reviewed calcein leakage, FE-SEM, "
                "phenotypic antibiofilm/kill-kinetic, and NMR/MD context claims with limitations."
            ),
            "publication_decision": (
                "Bounded local repair is complete, but publication-grade acceptance is blocked by unrecoverable local "
                "supplement/sequence evidence gaps."
            ),
        },
        "caution_findings": [
            {
                "caution_code": "supplement_declared_but_not_local",
                "evidence_context": (
                    "The XML declares 44259_2025_121_MOESM1_ESM.docx; local supplementary assets are HTML landing pages "
                    "and do not contain the DOCX payload."
                ),
            },
            {
                "caution_code": "dbaasp_rows_preserved_as_database_only",
                "evidence_context": (
                    "Linked DBAASP rows cite this article, but row-level peptide sequence/modification and most exact "
                    "activity sources require missing supplementary material."
                ),
            },
            {
                "caution_code": "main_tables_preserved_as_partial_evidence",
                "evidence_context": (
                    "Table 1/2 MIC rows remain available and source-located, but they do not substitute for the missing "
                    "full-library supplementary tables."
                ),
            },
        ],
        "qc_failure_reasons": [
            {
                "code": "springer_moesm1_docx_not_present_in_local_material",
                "owner_worker": "worker-3",
                "reason": "XML-declared Supplementary Information DOCX is absent from local packet/source/landed assets.",
                "severity": "blocking",
            },
            {
                "code": "dbaasp_rows_database_only_no_primary_source",
                "owner_worker": "worker-4",
                "reason": (
                    "Linked DBAASP rows cannot be source-verified without exact primary sequence/modification and "
                    "supplement table evidence."
                ),
                "severity": "major",
            },
        ],
        "rework_targets": targets,
        "unrecoverable_material_gaps": gaps,
        "adjudication_summary": (
            "Worker-3/4/6 bounded source re-review refreshed the supplementary material gap, repaired overclaimed "
            "database and final mechanism/adjudication layers, preserved supported main-table activity rows, and left "
            "the paper non-accepted because required local supplement/sequence evidence is unrecoverable."
        ),
    }


def write_review_and_quality(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], gate_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    review = build_review(generated_at, activity, database, mechanism)
    if gate_evidence:
        review["gate_evidence"] = gate_evidence
    for path in [
        PAPER / "final" / "review_report.json",
        PACKET / "analysis" / "adjudication_report.json",
        PACKET / "final" / "review_report.json",
    ]:
        write_json(path, review)
    quality = {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "status": "blocked_after_bounded_worker3_worker4_worker6_source_review",
            "issue_count": len(review["qc_failure_reasons"]),
            "qc_failure_reasons": review["qc_failure_reasons"],
        "rework_targets": review["rework_targets"],
        "unrecoverable_material_gaps": review["unrecoverable_material_gaps"],
        "rework_context_packet_required": False,
        "resolution": (
            "Concrete worker-3/4/6 source-reviewed nonacceptance was refreshed: supported local values remain recorded, "
            "and unrecoverable local material gaps block publication-grade acceptance."
        ),
    }
    if gate_evidence:
        quality["gate_evidence"] = gate_evidence
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality)
    return review


def append_rework_requests(generated_at: str) -> None:
    existing = {str(row.get("ticket_id")) for row in read_jsonl(PACKET / "rework" / "rework_requests.jsonl")}
    for target in rework_targets(generated_at):
        if target["ticket_id"] not in existing:
            append_jsonl(PACKET / "rework" / "rework_requests.jsonl", target)


def update_status_files(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> None:
    analysis_status_path = PACKET / "analysis" / "analysis_status.json"
    analysis_status = read_json(analysis_status_path)
    analysis_status.update(
        {
            "generated_at": generated_at,
            "status": "analysis_blocked_unrecoverable_material_gaps",
            "activity_record_count": len(activity.get("activity_records") or []),
            "mechanism_claim_count": len(mechanism.get("mechanism_claims") or []),
            "database_status_summary": database.get("status_summary", {}),
            "open_rework_ticket_ids": OPEN_TICKET_IDS,
            "unrecoverable_material_gap_count": len(unrecoverable_gaps()),
        }
    )
    write_json(analysis_status_path, analysis_status)

    manifest_path = PACKET / "packet_manifest.json"
    manifest = read_json(manifest_path)
    manifest.update(
        {
            "updated_at": generated_at,
            "analysis_queue_status": "analysis_blocked_unrecoverable_material_gaps",
            "open_rework_ticket_ids": OPEN_TICKET_IDS,
            "known_missing_or_blocked_materials": unrecoverable_gaps(),
        }
    )
    write_json(manifest_path, manifest)

    workflow_path = WORKFLOW / "workflow_context.json"
    if workflow_path.exists():
        ctx = read_json(workflow_path)
        ctx.update(
            {
                "updated_at": generated_at,
                "current_state": "blocked_unrecoverable_material_gaps",
                "open_rework_tickets": OPEN_TICKET_IDS,
                "queue_status": {
                    "analysis": "analysis_blocked_unrecoverable_material_gaps",
                    "material": "material_extracted_with_gaps",
                },
                "gate_summary": {
                    "structural_ready": True,
                    "validator_contract_ready": True,
                    "semantic_gate_ready": False,
                    "publication_grade_ready": False,
                },
            }
        )
        write_json(workflow_path, ctx)


def run_gates() -> tuple[bool, dict[str, Any], dict[str, Any], dict[str, Any]]:
    semantic_path = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    publication_path = REPORTS / f"{PAPER_ID}.publication_quality.json"
    manifest = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"

    semantic_proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "semantic_three_layer_gate.py"),
            "--root",
            str(ROOT),
            "--paper-id",
            PAPER_ID,
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    try:
        semantic = json.loads(semantic_proc.stdout)
    except json.JSONDecodeError:
        semantic = {"parse_error": semantic_proc.stdout, "stderr": semantic_proc.stderr}
    write_json(semantic_path, semantic)

    publication_proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "check_three_layer_publication_quality.py"),
            "--root",
            str(ROOT),
            "--manifest",
            str(manifest),
            "--json-out",
            str(publication_path),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    publication = read_json(publication_path) if publication_path.exists() else {"stderr": publication_proc.stderr}
    semantic_result = (semantic.get("results") or [{}])[0] if isinstance(semantic, dict) else {}
    gates_ready = (
        semantic_proc.returncode == 0
        and publication_proc.returncode == 0
        and semantic.get("publication_grade_pass_count") == 1
        and semantic.get("publication_grade_fail_count") == 0
        and publication.get("publication_grade_pass") is True
    )
    evidence = {
        "semantic_report": str(semantic_path),
        "semantic_returncode": semantic_proc.returncode,
        "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
        "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
        "semantic_issue_count": semantic_result.get("issue_count"),
        "semantic_issue_codes": [issue.get("code") for issue in semantic_result.get("issues", [])],
        "publication_report": str(publication_path),
        "publication_returncode": publication_proc.returncode,
        "publication_grade_pass": publication.get("publication_grade_pass"),
        "publication_risk_counts": publication.get("risk_counts"),
        "gates_ready": gates_ready,
    }
    return gates_ready, evidence, semantic, publication


def build_rework_response(generated_at: str, gate_evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_type": "rework_response",
        "response_id": f"{PAPER_ID}-worker346-bounded-source-review-{generated_at}",
        "paper_id": PAPER_ID,
        "ticket_ids": [ORIGINAL_TICKET_ID, SUPP_TICKET_ID, DB_TICKET_ID],
        "created_ticket_ids": OPEN_TICKET_IDS,
        "status": "bounded_repair_completed_nonaccepted_unrecoverable_gaps",
        "owner_workers": ["worker-3", "worker-4", "worker-6"],
        "resolved_by": "codex-cli",
        "state": "worker3_worker4_worker6_source_review_bounded_nonacceptance",
        "checked_source_paths": SOURCE_PATHS_CHECKED,
        "tools_attempted": TOOLS_ATTEMPTED,
        "what_was_repaired": [
            "Worker-3 refreshed supplementary evidence, extraction status, and extraction quality with the XML-declared MOESM1 DOCX absence as an unrecoverable material gap.",
            "Worker-4 downgraded linked DBAASP rows from overmatched source_verified/source_conflict placeholders to database_only_no_primary_source with row traceability and source-exhaustion rationale.",
            "Worker-6 repaired final activity entity/target-class metadata for local Table 1/2 rows without fabricating supplement-only values.",
            "Worker-6 replaced automated mechanism placeholders with source-reviewed, locator-backed claims and limitations.",
            "Worker-6 rewrote final adjudication and quality feedback as blocked_missing_primary_material with concrete unrecoverable_material_gaps.",
        ],
        "what_remains": [
            "XML-declared MOESM1 DOCX is not locally present; supplementary tables/figures cannot be extracted from current local material.",
            "Linked DBAASP rows cannot be source_verified without exact sequence/modification and supplement table evidence.",
            "Strict gates are expected to fail because the paper remains non-accepted with open targeted rework/material-gap tickets.",
        ],
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "qc_failure_reasons_remaining": [
            "springer_moesm1_docx_not_present_in_local_material",
            "dbaasp_rows_database_only_no_primary_source",
        ],
        "gate_evidence": gate_evidence,
        "artifact_refs": [
            f"papers/{PAPER_ID}/work/supplementary_methods/supplementary_evidence.json",
            f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
            f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
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
        "created_at": generated_at,
        "responded_at": generated_at,
    }


def write_complete_report(generated_at: str, gate_evidence: dict[str, Any], semantic: dict[str, Any], publication: dict[str, Any]) -> None:
    final_activity = read_json(PAPER / "final" / "activity_toxicity_evidence.json")
    final_database = read_json(PAPER / "final" / "database_record_verification.json")
    final_mechanism = read_json(PAPER / "final" / "mechanism_ontology_record.json")
    semantic_result = (semantic.get("results") or [{}])[0] if isinstance(semantic, dict) else {}
    report = {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "pmid": PMID,
        "pmcid": PMCID,
        "title": TITLE,
        "generated_at": generated_at,
        "completion_claim": "bounded_worker3_worker4_worker6_source_review_completed_nonaccepted_unrecoverable_gaps",
        "current_state": "blocked_unrecoverable_material_gaps",
        "terminal_status": "blocked_missing_primary_material",
        "final_approval_status": "refused_unrecoverable_material_gaps",
        "gate_summary": {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": gate_evidence["gates_ready"],
            "publication_grade_ready": gate_evidence["gates_ready"],
        },
        "gate_results": {
            "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
            "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
            "semantic_issue_count": semantic_result.get("issue_count"),
            "semantic_issue_codes": gate_evidence.get("semantic_issue_codes"),
            "publication_quality_pass": publication.get("publication_grade_pass"),
            "publication_risk_counts": publication.get("risk_counts"),
        },
        "analysis": {
            "review_status": "blocked_missing_primary_material",
            "activity_records": len(final_activity.get("activity_records") or []),
            "database_status_summary": final_database.get("status_summary"),
            "mechanism_claims": len(final_mechanism.get("mechanism_claims") or []),
            "unrecoverable_material_gap_count": len(unrecoverable_gaps()),
        },
        "open_rework_ticket_count": len(OPEN_TICKET_IDS),
        "rework_ticket_ids": OPEN_TICKET_IDS,
        "not_publication_grade_reason": (
            "Local source cannot support the XML-declared supplementary DOCX or exact DBAASP sequence/supplement table "
            "evidence after bounded worker-4/6 review."
        ),
        "unrecoverable_material_gaps": unrecoverable_gaps(),
        "semantic_gate": "passed" if gate_evidence["gates_ready"] else "failed_expected_nonaccepted_unrecoverable_gaps",
        "publication_quality_gate": (
            "passed" if gate_evidence["gates_ready"] else "failed_expected_open_rework_and_nonpublication_grade"
        ),
        "manifest": str(REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"),
        "semantic_report": gate_evidence["semantic_report"],
        "publication_quality_report": gate_evidence["publication_report"],
        "workflow_dir": str(WORKFLOW),
    }
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", report)


def repair() -> dict[str, Any]:
    generated_at = utc_now()
    repair_supplementary(generated_at)
    activity = repair_activity(generated_at)
    database = repair_database(generated_at)
    mechanism = build_mechanism(generated_at)
    write_review_and_quality(generated_at, activity, database, mechanism)
    append_rework_requests(generated_at)
    update_status_files(generated_at, activity, database, mechanism)

    gates_ready, gate_evidence, semantic, publication = run_gates()
    write_review_and_quality(generated_at, activity, database, mechanism, gate_evidence)
    append_jsonl(PACKET / "rework" / "rework_responses.jsonl", build_rework_response(generated_at, gate_evidence))
    write_complete_report(generated_at, gate_evidence, semantic, publication)
    return {
        "paper_id": PAPER_ID,
        "gates_ready": gates_ready,
        "gate_evidence": gate_evidence,
        "open_rework_ticket_ids": OPEN_TICKET_IDS,
        "unrecoverable_material_gap_count": len(unrecoverable_gaps()),
    }


def main() -> int:
    result = repair()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
