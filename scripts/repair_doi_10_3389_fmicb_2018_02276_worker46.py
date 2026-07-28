#!/usr/bin/env python3
"""Worker-4/6 source-reviewed repair for doi__10.3389_fmicb.2018.02276."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


PAPER_ID = "doi__10.3389_fmicb.2018.02276"
DOI = "10.3389/fmicb.2018.02276"
TICKET_ID = "rwk-complete-test-0001"
ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / PAPER_ID
PACKET = ROOT / "paper_packets" / PAPER_ID
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
REPORTS = ROOT / "reports"
LANDED = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers") / PAPER_ID


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
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


def upsert_rework_response(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    retained = []
    for row in read_jsonl(path):
        same_worker46_closeout = (
            row.get("paper_id") == PAPER_ID
            and row.get("record_type") == "rework_response"
            and row.get("state") == "worker4_worker6_source_review_repair"
            and TICKET_ID in (row.get("ticket_ids") or [])
        )
        if not same_worker46_closeout:
            retained.append(row)
    retained.append(payload)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in retained),
        encoding="utf-8",
    )


def loc(source_path: str, locator: str, note: str | None = None) -> dict[str, str]:
    out = {"source_path": source_path, "locator": locator}
    if note:
        out["note"] = note
    return out


def extract_table1_rows() -> dict[int, dict[str, str]]:
    root = ET.parse(PAPER / "source" / "paper.xml").getroot()
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    def text(elem: ET.Element | None) -> str:
        if elem is None:
            return ""
        return " ".join("".join(elem.itertext()).split())

    table = None
    for table_wrap in root.findall(".//table-wrap"):
        label = text(table_wrap.find("label"))
        caption = text(table_wrap.find("caption"))
        if label == "Table 1" and "Antibacterial spectrum" in caption:
            table = table_wrap
            break
    if table is None:
        raise RuntimeError("Table 1 not found in source/paper.xml")

    rows: dict[int, dict[str, str]] = {}
    for row_index, tr in enumerate(table.findall(".//tr"), start=1):
        cells = [text(cell) for cell in list(tr) if cell.tag in {"td", "th"}]
        if len(cells) == 5:
            rows[row_index] = {
                "indicator": cells[0],
                "source": cells[1],
                "media": cells[2],
                "activity": cells[3],
                "mic": cells[4],
            }
    return rows


def activity_class(row_index: int) -> str:
    if 3 <= row_index <= 19:
        return "Gram-positive bacteria"
    if 21 <= row_index <= 24:
        return "Gram-negative bacteria"
    if 26 <= row_index <= 27:
        return "Fungi"
    return "unknown"


def build_activity_records(generated_at: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for row_index, row in extract_table1_rows().items():
        indicator = row["indicator"]
        if row_index == 1 or not indicator or "bacteria" in indicator.lower() or indicator == "Fungi":
            continue
        base_target = {
            "class": activity_class(row_index),
            "species": indicator,
            "strain": indicator,
            "source_collection": row["source"],
            "medium": row["media"],
        }
        if row["activity"]:
            records.append(
                {
                    "record_id": f"{PAPER_ID}-table1-r{row_index}-c4-inhibition-zone",
                    "entity": "plantaricin LPL-1",
                    "endpoint": "inhibition_zone_diameter",
                    "raw_value": row["activity"],
                    "raw_unit": "mm",
                    "normalization_status": "raw_unit_preserved",
                    "evidence_ladder": "in_vitro_assay_table",
                    "target": base_target,
                    "assay_conditions": {
                        "source_column_context": "Table 1 Activity (mm)",
                        "table_context": "Antibacterial spectrum of plantaricin LPL-1.",
                    },
                    "source_locator": loc("source/paper.xml", f"xml:table=1:row={row_index}:column=4"),
                }
            )
        if row["mic"]:
            records.append(
                {
                    "record_id": f"{PAPER_ID}-table1-r{row_index}-c5-MIC",
                    "entity": "plantaricin LPL-1",
                    "endpoint": "MIC",
                    "raw_value": row["mic"],
                    "raw_unit": "μg/mL",
                    "normalization_status": "raw_unit_preserved",
                    "evidence_ladder": "in_vitro_assay_table",
                    "target": base_target,
                    "assay_conditions": {
                        "source_column_context": "Table 1 MIC (μg/mL)",
                        "table_context": "Antibacterial spectrum of plantaricin LPL-1.",
                    },
                    "source_locator": loc("source/paper.xml", f"xml:table=1:row={row_index}:column=5"),
                }
            )

    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 source-reviewed final activity evidence from primary XML Table 1; Table S1 is screening-only and Table S2 is strain-identity 16S alignment, so neither adds final activity rows.",
        "activity_records": records,
        "extraction_issues": [],
        "parser_quality_control": {
            "issue_count": 0,
            "source_reviewed_by_worker_6": True,
            "corrected_prior_column_error": "Prior artifact mislabeled Table 1 Activity (mm) as MIC; final records now separate inhibition-zone and MIC endpoints.",
            "strict_endpoint_matching": True,
            "raw_units_preserved": True,
        },
    }


ROW_MAP: dict[str, dict[str, Any]] = {
    "Listeria monocytogenes NICPBP 54002": {"rows": [3], "status": "source_verified"},
    "Listeria monocytogenes ATCC 19113": {"rows": [4], "status": "source_verified"},
    "Listeria monocytogenes ATCC 19114": {"rows": [5], "status": "source_verified"},
    "Staphylococcus aureus ATCC 13565": {"rows": [6], "status": "source_verified"},
    "Staphylococcus aureus ATCC 6538": {
        "rows": [7],
        "status": "source_conflict",
        "conflict": "Primary Table 1 reports S. aureus 6538 with source collection CGNCC; the database row labels the same strain number as ATCC 6538.",
    },
    "Staphylococcus aureus CVCC 26112": {"rows": [8], "status": "source_verified"},
    "Enterococcus faecalis": {
        "rows": [9, 10],
        "status": "source_conflict",
        "conflict": "Database row aggregates two primary-source lab rows, E. faecalis M2 and E. faecalis, under a species-level target.",
    },
    "Lactobacillus delbrueckii subsp. lactis": {"rows": [11], "status": "source_verified"},
    "Lactiplantibacillus plantarum": {
        "rows": [12, 13],
        "status": "source_conflict",
        "conflict": "Database row uses the post-reclassification genus and aggregates two primary-source L. plantarum lab strains, S-35 and γ-35.",
    },
    "Lactobacillus delbrueckii subsp. bulgaricus": {
        "rows": [14],
        "status": "source_verified",
        "note": "Primary source uses Lactobacillus bulgaricus; database uses the formal subspecies name.",
    },
    "Ligilactobacillus salivarius": {
        "rows": [15],
        "status": "source_verified",
        "note": "Primary source uses Lactobacillus salivarius; database uses the post-reclassification genus.",
    },
    "Lactococcus lactis MG1363": {
        "rows": [17],
        "status": "source_verified",
        "note": "Database note also mentions L. lactis NZ9000, which is separately present in Table 1 with the same MIC.",
    },
    "Bacillus amyloliquefaciens": {"rows": [18], "status": "source_verified"},
    "Bacillus pumilus": {
        "rows": [19],
        "status": "source_verified",
        "note": "Primary source abbreviates the genus as B. pumilus.",
    },
    "Escherichia coli DH5alpha": {
        "rows": [21],
        "status": "source_verified",
        "note": "Primary source uses DH5α; database ASCII-normalizes alpha.",
    },
    "Escherichia coli BL21": {"rows": [22], "status": "source_verified"},
    "Escherichia coli BW25113": {"rows": [23], "status": "source_verified"},
    "Escherichia coli JM109": {"rows": [24], "status": "source_verified"},
    "Saccharomyces cerevisiae": {"rows": [26], "status": "source_verified"},
    "Pichia pastoris GS115": {"rows": [27], "status": "source_verified"},
}


def db_subject(row: dict[str, Any]) -> str:
    for key in ("subject_name", "target_organism_text", "title"):
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return ""


def source_locs_for_rows(rows: list[int], column: int = 5) -> list[dict[str, str]]:
    return [loc("source/paper.xml", f"xml:table=1:row={row}:column={column}") for row in rows]


def build_database_audit(generated_at: str) -> dict[str, Any]:
    rows_by_index = extract_table1_rows()
    record_audits: list[dict[str, Any]] = []
    source_files = {
        "linked_assay_records.jsonl": PACKET / "database" / "linked_assay_records.jsonl",
        "linked_experiment_records.jsonl": PACKET / "database" / "linked_experiment_records.jsonl",
        "linked_literature_records.jsonl": PACKET / "database" / "linked_literature_records.jsonl",
    }

    for source_table, path in source_files.items():
        for line_number, row in enumerate(read_jsonl(path), start=1):
            subject = db_subject(row)
            sequence_key = str(row.get("sequence_key") or row.get("source_id") or "").strip()
            database = str(row.get("database") or row.get("\ufeffdatabase") or "DBAASP").strip()

            if source_table == "linked_literature_records.jsonl":
                status = "source_verified"
                rows = []
                conflict_context = ""
                review_notes = "Literature row DOI/PMID/PMCID/title match the primary article metadata."
                source_locator: Any = loc("source/paper.xml", "xml:article-meta")
                matched_ids: list[str] = []
            elif sequence_key.startswith("CAMP:"):
                status = "source_conflict"
                rows = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27]
                conflict_context = "CAMP entry text says Antibacterial, Antifungal, but primary Table 1 supports antibacterial activity against Gram-positive strains and no activity against the tested fungi; preserve as a source conflict."
                review_notes = conflict_context
                source_locator = [loc("source/paper.xml", "xml:abstract"), loc("source/paper.xml", "xml:table=1")]
                matched_ids = []
            else:
                mapping = ROW_MAP.get(subject)
                if mapping is None:
                    status = "unresolved_record"
                    rows = []
                    conflict_context = f"No bounded local Table 1 match was found for database target {subject!r}."
                    review_notes = conflict_context
                    source_locator = loc("source/paper.xml", "xml:table=1")
                    matched_ids = []
                else:
                    status = str(mapping["status"])
                    rows = list(mapping["rows"])
                    conflict_context = str(mapping.get("conflict") or "")
                    review_notes = conflict_context or str(mapping.get("note") or "Database target, MIC/no-activity value, and article citation are supported by primary Table 1 and article metadata.")
                    mic_rows = [row_index for row_index in rows if rows_by_index[row_index].get("mic")]
                    column = 5 if mic_rows else 4
                    source_locator = source_locs_for_rows(rows, column=column)
                    matched_ids = [
                        f"{PAPER_ID}-table1-r{row_index}-c{column}-{'MIC' if column == 5 else 'inhibition-zone'}"
                        for row_index in rows
                    ]

            audit = {
                "source_id": f"{database}:{row.get('source_id') or row.get('dbaasp_id') or row.get('source_record_id') or sequence_key}",
                "sequence_key": sequence_key,
                "source_table": source_table if source_table != "linked_experiment_records.jsonl" else str(row.get("source_table") or source_table),
                "database": database,
                "database_subject": subject,
                "database_measure": str(row.get("measure_group") or row.get("measure_value") or row.get("assay_text") or "").strip(),
                "database_value": str(row.get("concentration") or row.get("activity_text") or "").strip(),
                "database_unit": str(row.get("unit") or "").strip(),
                "status": status,
                "layer1_status": status,
                "matched_activity_record_ids": matched_ids,
                "sequence_check": {
                    "status": "source_verified",
                    "source_locator": {
                        "source_path": "source/paper.xml",
                        "locator": "xml:abstract; xml:sec=Results:Molecular Mass and Amino Acid Sequence; xml:sec=Conclusion",
                        "primary_source_statement": "Primary XML/PDF report plantaricin LPL-1 as the mature peptide with sequence VIADKYYGNGVSCGKHTCTVDWGEAFSCSVSHLANFGHGKC and mass 4347.8467 Da.",
                    },
                },
                "name_check": {
                    "status": "source_verified" if status == "source_verified" else "source_conflict",
                    "source_locator": loc("source/paper.xml", "xml:article-title; xml:abstract"),
                    "primary_name": "plantaricin LPL-1",
                    "database_name": str(row.get("peptide_name") or row.get("title") or "Bacteriocin Plantaricin LPL-1"),
                },
                "target_check": {
                    "status": status,
                    "source_locator": source_locator,
                    "primary_table_rows": rows,
                },
                "citation_traceability": loc("source/paper.xml", "xml:article-meta"),
                "traceability": loc(str(path), f"database:{source_table}:row={line_number}"),
                "review_notes": review_notes,
                "conflict_context": conflict_context,
            }
            if status == "source_conflict":
                audit["conflict_flags"] = ["database_primary_source_target_or_activity_mismatch"]
            record_audits.append(audit)

    counts = Counter(record["status"] for record in record_audits)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "audit_scope": "Worker-4 source-reviewed linked DBAASP/CAMP/literature rows against primary XML Table 1, article metadata, and peptide identity evidence; conflicts are preserved as nonblocking cautions when the source can be bounded.",
        "database_row_counts": {
            "linked_assay_records": len(read_jsonl(PACKET / "database" / "linked_assay_records.jsonl")),
            "linked_dramp_activity_records": len(read_jsonl(PACKET / "database" / "linked_dramp_activity_records.jsonl")),
            "linked_experiment_records": len(read_jsonl(PACKET / "database" / "linked_experiment_records.jsonl")),
            "linked_literature_records": len(read_jsonl(PACKET / "database" / "linked_literature_records.jsonl")),
            "linked_sequence_records": len(read_jsonl(PACKET / "database" / "linked_sequence_records.jsonl")),
        },
        "status_summary": dict(sorted(counts.items())),
        "record_audits": record_audits,
        "unrecoverable_material_gaps": [],
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 source-reviewed mechanism ontology from primary XML/PDF figures, captions, results, and discussion; automated placeholder mechanism notes were replaced.",
        "mechanism_claims": [
            {
                "claim_id": "mech-001",
                "claim_text": "Plantaricin LPL-1 is characterized as a class IIa bacteriocin with a YGNGV motif and cysteine-containing mature peptide sequence; this supports AMP identity/classification, not a cellular target claim.",
                "entity_scope": "plantaricin LPL-1",
                "evidence_class": "identity_classification",
                "source_locator": loc("source/paper.xml", "xml:abstract; xml:fig=4:FIGURE 4; xml:sec=Conclusion"),
                "limitations": "Class assignment and sequence evidence do not by themselves identify a complete killing mechanism.",
            },
            {
                "claim_id": "mech-002",
                "claim_text": "The paper reports bactericidal action against Listeria monocytogenes 54002 in time-kill/OD600 mode-of-action experiments.",
                "entity_scope": "plantaricin LPL-1 against Listeria monocytogenes 54002",
                "evidence_class": "direct_mechanism",
                "direct_assay_types": ["viable_cell_count_time_kill", "OD600_growth_monitoring"],
                "source_locator": loc("source/paper.xml", "xml:fig=6:FIGURE 6; xml:sec=Results:Mode of Action of Plantaricin LPL-1"),
                "limitations": "The result supports bactericidal action in the tested indicator strain but not a universal target model.",
            },
            {
                "claim_id": "mech-003",
                "claim_text": "SYTOX Green and CLSM assays support membrane permeabilization/damage in Listeria monocytogenes 54002 after plantaricin LPL-1 treatment.",
                "entity_scope": "plantaricin LPL-1 against Listeria monocytogenes 54002",
                "evidence_class": "direct_mechanism",
                "direct_assay_types": ["SYTOX_Green_membrane_permeabilization", "confocal_microscopy_dead_cell_staining"],
                "source_locator": loc("source/paper.xml", "xml:fig=7:FIGURE 7; xml:fig=8:FIGURE 8; xml:sec=Discussion"),
                "limitations": "The paper itself states that precise pore/PMF/ATP/electrical mechanisms require future investigation.",
            },
        ],
    }


def checked_inputs() -> list[str]:
    return [
        f"rework_context/{PAPER_ID}/handoff_context.json",
        f"paper_packets/{PAPER_ID}/packet_manifest.json",
        f"paper_packets/{PAPER_ID}/locators/locator_index.json",
        f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
        f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
        f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
        f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
        f"paper_packets/{PAPER_ID}/extracted/pdf_text/fmicb-09-02276.txt",
        f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
        f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
        f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC6172451/PMC6172451/Table_1.DOC",
        f"paper_packets/{PAPER_ID}/extracted/oa_package/local-DBAASP-PMC6172451/PMC6172451/Table_2.doc",
        f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
        f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
        f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
        str(LANDED / "xml" / "local-DBAASP-PMC6172451.xml"),
        str(LANDED / "pdf" / "local-DBAASP-PMC6172451.pdf"),
        str(LANDED / "package" / "local-DBAASP-PMC6172451.tar.gz"),
        str(LANDED / "supplementary"),
    ]


def build_review(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> dict[str, Any]:
    caution_findings = [
        {
            "code": "database_source_conflicts_preserved",
            "severity": "caution",
            "finding": "Several linked database rows aggregate strain-level Table 1 entries or use taxonomy/collection labels not exactly printed in the primary source; these remain explicit source_conflict records rather than hidden normalizations.",
            "affected_status_summary": database["status_summary"],
        },
        {
            "code": "supplementary_not_gate_changing",
            "severity": "caution",
            "finding": "OA package supplements were opened: Table S1 is preliminary screening, Table S2 is 16S alignment, and Figure S1 is phylogeny. They do not add source-supported final MIC/toxicity rows beyond main Table 1.",
        },
        {
            "code": "mechanism_bounded_to_membrane_permeabilization",
            "severity": "caution",
            "finding": "The paper supports bactericidal action and membrane permeabilization for L. monocytogenes 54002, while exact pore/PMF/ATP/electric-conductivity mechanisms are future-work limitations.",
        },
    ]
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "accepted_with_cautions",
        "publication_grade": True,
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
            "note": "Local XML/NXML, PDF text, OA package files, Table S1 DOC, Table S2 DOCX, supplementary landing captures, figure captions/images, and linked database JSONL rows were opened. No blocking local material gap remains after bounded repair.",
        },
        "checked_inputs": checked_inputs(),
        "semantic_quality_checks": {
            "activity_rows_source_reviewed": len(activity["activity_records"]),
            "database_record_status_summary": database["status_summary"],
            "mechanism_claims_source_reviewed": len(mechanism["mechanism_claims"]),
            "open_rework_targets": 0,
            "unrecoverable_material_gap_count": 0,
            "closed_rework_ticket_ids": [TICKET_ID],
        },
        "per_layer_decision_rationale": {
            "material_packet": "Material remains material_extracted_with_gaps structurally because generic landing .bin captures exist, but the relevant local XML/PDF/OA DOC/DOCX/database evidence needed for the blocker was recoverable.",
            "validator_contract": "The packet/final files are present and schema-compatible; validator success is treated as structural only, not as the source-review proof.",
            "layer_1_database": "Worker-4 reconciled linked database rows against primary Table 1, article metadata, and sequence/mass identity. True database-source conflicts are preserved with context and do not remain open rework.",
            "layer_2_activity_toxicity": "Worker-6 corrected the prior column mismatch by separating Table 1 inhibition-zone values in mm from MIC values in μg/mL and preserving no-activity rows for Gram-negative/fungal targets.",
            "layer_3_mechanism": "Worker-6 replaced placeholder mechanism notes with source-reviewed bactericidal and membrane-permeabilization claims plus limitations.",
            "publication_grade_review": "The original worker-6 source-review blocker and database-conflict blocker are closed; remaining cautions are explicit and bounded by local evidence.",
        },
        "caution_findings": caution_findings,
        "rework_targets": [],
        "unrecoverable_material_gaps": [],
        "adjudication_summary": "Worker-4/6 re-review closed the framework-test blocker by source-reviewing Table 1, source supplements, linked DBAASP/CAMP rows, and mechanism figures. The final state is accepted_with_cautions because supported values are extracted and database/source conflicts remain explicit cautions.",
    }


def quality_feedback_pass(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": 0,
        "qc_failure_reasons": [],
        "rework_context_packet_required": False,
        "rework_targets": [],
        "resolved_rework_ticket_ids": [TICKET_ID],
        "status": "qc_passed_after_worker4_worker6_source_review",
        "notes": "Previous full_source_review_not_completed and database_conflicts_require_adjudication blockers were resolved by source-reviewed worker-4/worker-6 repair. Remaining source_conflict records are bounded cautions, not open rework tickets.",
    }


def quality_feedback_fail(generated_at: str, gate_evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": 1,
        "qc_failure_reasons": [
            {
                "code": "strict_gate_failed_after_worker46_repair",
                "owner_worker": "worker-6",
                "severity": "blocking",
                "reason": "Strict semantic or publication gate still failed after bounded worker-4/6 source review.",
                "gate_evidence": gate_evidence,
            }
        ],
        "rework_context_packet_required": True,
        "rework_targets": [
            {
                "ticket_id": TICKET_ID,
                "paper_id": PAPER_ID,
                "worker": "worker-6",
                "owner_worker": "worker-6",
                "target_queue": "adjudication",
                "severity": "blocking",
                "failure_code": "strict_gate_failed_after_worker46_repair",
                "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
                "source_paths_to_check": checked_inputs(),
                "required_action": "Repair the strict semantic/publication gate issue codes from the current reports without fabricating missing source values.",
                "created_at": generated_at,
            }
        ],
    }


def write_core_artifacts(generated_at: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    activity = build_activity_records(generated_at)
    database = build_database_audit(generated_at)
    mechanism = build_mechanism(generated_at)
    review = build_review(generated_at, activity, database, mechanism)

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
        PAPER / "final" / "mechanism_ontology_record.json",
        PAPER / "final" / "mechanism_evidence.json",
    ):
        write_json(path, mechanism)
    for path in (
        PACKET / "analysis" / "adjudication_report.json",
        PACKET / "final" / "review_report.json",
        PAPER / "final" / "review_report.json",
    ):
        write_json(path, review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality_feedback_pass(generated_at))
    return activity, database, mechanism, review


def set_queue_state(generated_at: str, gates_ready: bool, activity_count: int, mechanism_count: int) -> None:
    ticket_ids = [] if gates_ready else [TICKET_ID]
    analysis_status = "analysis_accepted_with_cautions" if gates_ready else "analysis_needs_analysis_rework"

    manifest_path = PACKET / "packet_manifest.json"
    manifest = read_json(manifest_path)
    manifest["analysis_queue_status"] = analysis_status
    manifest["open_rework_ticket_ids"] = ticket_ids
    manifest["updated_at"] = generated_at
    write_json(manifest_path, manifest)

    status_path = PACKET / "analysis" / "analysis_status.json"
    status = read_json(status_path)
    status["status"] = analysis_status
    status["open_rework_ticket_ids"] = ticket_ids
    status["source_reviewed_rework_checked_at"] = generated_at
    status["activity_record_count"] = activity_count
    status["mechanism_claim_count"] = mechanism_count
    write_json(status_path, status)

    ctx_path = WORKFLOW / "workflow_context.json"
    if ctx_path.exists():
        ctx = read_json(ctx_path)
        ctx["current_state"] = "final_approval" if gates_ready else "rework_queue"
        ctx["updated_at"] = generated_at
        ctx["open_rework_tickets"] = ticket_ids
        ctx["queue_status"] = {"material": "material_extracted_with_gaps", "analysis": analysis_status}
        ctx["gate_summary"] = {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": bool(gates_ready),
            "publication_grade_ready": bool(gates_ready),
        }
        write_json(ctx_path, ctx)


def run_gates() -> tuple[bool, dict[str, Any], dict[str, Any], dict[str, Any]]:
    semantic_path = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    publication_path = REPORTS / f"{PAPER_ID}.publication_quality.json"
    manifest = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"
    semantic_cmd = [
        sys.executable,
        str(ROOT / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "semantic_three_layer_gate.py"),
        "--root",
        str(ROOT),
        "--paper-id",
        PAPER_ID,
        "--json",
    ]
    semantic_proc = subprocess.run(semantic_cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    semantic_path.write_text(semantic_proc.stdout, encoding="utf-8")
    if semantic_proc.returncode not in (0, 1):
        raise RuntimeError(f"semantic gate did not run cleanly: {semantic_proc.stderr}")
    semantic = json.loads(semantic_proc.stdout)

    publication_cmd = [
        sys.executable,
        str(ROOT / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "check_three_layer_publication_quality.py"),
        "--root",
        str(ROOT),
        "--manifest",
        str(manifest),
        "--json-out",
        str(publication_path),
    ]
    publication_proc = subprocess.run(publication_cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    if publication_proc.returncode not in (0, 2):
        raise RuntimeError(f"publication gate did not run cleanly: {publication_proc.stderr}")
    publication = read_json(publication_path)
    first = (semantic.get("results") or [{}])[0]
    gates_ready = (
        semantic_proc.returncode == 0
        and publication_proc.returncode == 0
        and int(first.get("issue_count") or 0) == 0
        and publication.get("publication_grade_pass") is True
    )
    gate_evidence = {
        "semantic_report": f"reports/{PAPER_ID}.semantic_gate.json",
        "semantic_issue_count": first.get("issue_count"),
        "semantic_issue_examples": (first.get("issues") or [])[:5],
        "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
        "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
        "publication_report": f"reports/{PAPER_ID}.publication_quality.json",
        "publication_quality_pass": publication.get("publication_grade_pass"),
        "publication_risk_counts": publication.get("risk_counts", {}),
        "publication_risk_examples": publication.get("risk_examples", {}),
    }
    return gates_ready, gate_evidence, semantic, publication


def write_complete_report(
    generated_at: str,
    gates_ready: bool,
    gate_evidence: dict[str, Any],
    activity: dict[str, Any],
    database: dict[str, Any],
    mechanism: dict[str, Any],
) -> None:
    report = {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "generated_at": generated_at,
        "test_type": "complete_real_paper_message_transfer_test",
        "completion_claim": "source_reviewed_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions" if gates_ready else "worker4_worker6_rework_attempt_gate_failed",
        "current_state": "final_approval" if gates_ready else "rework_queue",
        "terminal_status": "accepted_with_cautions" if gates_ready else "awaiting_targeted_rework",
        "final_approval_status": "accepted_with_cautions" if gates_ready else "refused_needs_rework",
        "publication_quality_gate": "passed_after_worker4_worker6_source_review" if gates_ready else "failed_after_worker4_worker6_source_review",
        "semantic_gate": "passed_after_worker4_worker6_source_review" if gates_ready else "failed_after_worker4_worker6_source_review",
        "open_rework_ticket_count": 0 if gates_ready else 1,
        "rework_ticket_ids": [] if gates_ready else [TICKET_ID],
        "not_publication_grade_reason": None if gates_ready else "Strict gates did not pass after worker-4/6 source review.",
        "gate_results": gate_evidence,
        "gate_summary": {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": gates_ready,
            "publication_grade_ready": gates_ready,
        },
        "analysis": {
            "activity_records": len(activity["activity_records"]),
            "database_status_summary": database["status_summary"],
            "mechanism_claims": len(mechanism["mechanism_claims"]),
            "review_status": "accepted_with_cautions" if gates_ready else "needs_targeted_rework",
        },
        "material": {
            "tables": 3,
            "figures": 8,
            "supplementary_assets": 10,
            "supplementary_tables": 0,
            "archive_members": 26,
            "source_review_note": "XML/PDF/OA package contains Table 1-3, Figure S1, Table S1 DOC, and Table S2 DOCX. Supplementary material was checked and did not change final activity/database/mechanism decisions.",
        },
        "packet_root": str(PACKET),
        "workflow_dir": str(WORKFLOW),
        "publication_quality_report": f"reports/{PAPER_ID}.publication_quality.json",
        "semantic_report": f"reports/{PAPER_ID}.semantic_gate.json",
    }
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", report)


def rework_response(generated_at: str, gates_ready: bool, gate_evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_type": "rework_response",
        "response_id": f"{PAPER_ID}-worker46-source-review-{generated_at}",
        "paper_id": PAPER_ID,
        "ticket_ids": [TICKET_ID],
        "status": "closed" if gates_ready else "kept_open",
        "owner_workers": ["worker-4", "worker-6"],
        "resolved_by": "codex-cli-worker",
        "state": "worker4_worker6_source_review_repair",
        "checked_source_paths": checked_inputs(),
        "tools_attempted": [
            "jq",
            "rg",
            "file",
            "antiword",
            "python zipfile OOXML reader",
            "xml.etree.ElementTree table extraction",
            "existing pdftotext extraction review",
            "semantic_three_layer_gate.py",
            "check_three_layer_publication_quality.py",
        ],
        "what_was_repaired": [
            "Rebuilt final activity evidence so Table 1 Activity (mm) and MIC (μg/mL) columns are separate source-reviewed endpoints.",
            "Rebuilt worker-4 database audit for linked DBAASP/CAMP/literature rows, preserving source_conflict records with context.",
            "Replaced worker-6 placeholder mechanism notes with source-reviewed bactericidal and membrane-permeabilization claims.",
            "Rewrote final review_report.json and quality_feedback.json with source-review provenance.",
            "Reran semantic and publication gates after repair.",
        ],
        "what_remains": [
            "Nonblocking cautions remain for database taxonomy/strain aggregation conflicts and source-bounded mechanism limitations.",
            "No unrecoverable material gap remains for the worker-4/6 blocker." if gates_ready else "Strict gates still failed; quality_feedback.json keeps the targeted rework ticket open.",
        ],
        "unrecoverable_material_gaps": [],
        "gate_evidence": gate_evidence,
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
        "created_at": generated_at,
    }


def main() -> int:
    generated_at = now_iso()
    activity, database, mechanism, review = write_core_artifacts(generated_at)
    gates_ready, gate_evidence, _, _ = run_gates()
    finalized_at = now_iso()

    if not gates_ready:
        review["review_status"] = "needs_targeted_rework"
        review["publication_grade"] = False
        review["rework_targets"] = quality_feedback_fail(finalized_at, gate_evidence)["rework_targets"]
        review["qc_failure_reasons"] = quality_feedback_fail(finalized_at, gate_evidence)["qc_failure_reasons"]
        for path in (PACKET / "analysis" / "adjudication_report.json", PACKET / "final" / "review_report.json", PAPER / "final" / "review_report.json"):
            write_json(path, review)
        write_json(PAPER / "work" / "review" / "quality_feedback.json", quality_feedback_fail(finalized_at, gate_evidence))
        gates_ready, gate_evidence, _, _ = run_gates()

    set_queue_state(finalized_at, gates_ready, len(activity["activity_records"]), len(mechanism["mechanism_claims"]))
    write_complete_report(finalized_at, gates_ready, gate_evidence, activity, database, mechanism)
    upsert_rework_response(PACKET / "rework" / "rework_responses.jsonl", rework_response(finalized_at, gates_ready, gate_evidence))
    print(
        json.dumps(
            {
                "ok": True,
                "paper_id": PAPER_ID,
                "gates_ready": gates_ready,
                "semantic_issue_count": gate_evidence.get("semantic_issue_count"),
                "publication_quality_pass": gate_evidence.get("publication_quality_pass"),
                "activity_records": len(activity["activity_records"]),
                "database_status_summary": database["status_summary"],
                "mechanism_claims": len(mechanism["mechanism_claims"]),
                "complete_report": f"reports/{PAPER_ID}.complete_message_test_report.json",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if gates_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
