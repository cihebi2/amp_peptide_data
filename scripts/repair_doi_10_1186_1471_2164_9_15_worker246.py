#!/usr/bin/env python3
"""Worker-2/4/6 bounded re-review for doi__10.1186_1471-2164-9-15.

This repair intentionally keeps the paper non-accepted.  The local source
supports LuloDEF identity context, but not primary activity/toxicity assay
values.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "doi__10.1186_1471-2164-9-15"
OLD_TICKET_ID = "rwk-complete-test-0001"
NEW_TICKET_ID = "rwk-20260503-worker246-unrecoverable-primary-activity"

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
REWORK = PACKET / "rework"
REPORTS = ROOT / "reports"
MANIFEST = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"

SEMANTIC_REPORT = REPORTS / f"{PAPER_ID}.codex_worker246_rereview_20260503.semantic_gate.json"
PUBLICATION_REPORT = REPORTS / f"{PAPER_ID}.codex_worker246_rereview_20260503.publication_quality.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path, default: Any | None = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl_once(path: Path, payload: dict[str, Any], key: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wanted = payload.get(key)
    for row in read_jsonl(path):
        if row.get(key) == wanted:
            return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def database_counts() -> dict[str, int]:
    names = [
        "linked_assay_records",
        "linked_dramp_activity_records",
        "linked_experiment_records",
        "linked_literature_records",
        "linked_sequence_records",
    ]
    return {name: len(read_jsonl(PACKET / "database" / f"{name}.jsonl")) for name in names}


def checked_source_paths() -> list[str]:
    paths = [
        ROOT / "rework_context" / PAPER_ID / "handoff_context.json",
        PACKET / "packet_manifest.json",
        PACKET / "locators" / "locator_index.json",
        PACKET / "extraction" / "extraction_status.json",
        PACKET / "extraction" / "extraction_quality_report.json",
        PACKET / "analysis" / "analysis_status.json",
        PACKET / "analysis" / "activity_toxicity_evidence.json",
        PACKET / "analysis" / "database_record_audit.json",
        PACKET / "analysis" / "mechanism_evidence.json",
        PACKET / "analysis" / "adjudication_report.json",
        REWORK / "rework_requests.jsonl",
        REWORK / "rework_responses.jsonl",
        PAPER / "source" / "paper.xml",
        PAPER / "source" / "paper.pdf",
        PACKET / "raw" / "paper.xml",
        PACKET / "raw" / "paper.pdf",
        PACKET / "extracted" / "xml_sections.json",
        PACKET / "extracted" / "pdf_text" / "1471-2164-9-15.txt",
        PACKET / "extracted" / "figure_captions.json",
        PACKET / "extracted" / "supplementary_index.json",
        PACKET / "extracted" / "supplementary_tables.json",
        PACKET / "extracted" / "archive_manifest.json",
        PACKET / "database" / "database_source_manifest.json",
        PAPER / "final" / "review_report.json",
        PAPER / "final" / "activity_toxicity_evidence.json",
        PAPER / "final" / "database_record_verification.json",
        PAPER / "final" / "mechanism_ontology_record.json",
        PAPER / "work" / "review" / "quality_feedback.json",
        REPORTS / f"{PAPER_ID}.complete_message_test_report.json",
    ]
    paths.extend(sorted((PACKET / "database").glob("*.jsonl")))
    paths.extend(sorted((PACKET / "extracted" / "supplementary_text").glob("*.txt")))
    paths.extend(sorted((PACKET / "raw" / "supplementary_original").glob("*")))
    return [rel(path) for path in paths if path.exists()]


def source_locator(locator: str, source_path: str, **extra: Any) -> dict[str, Any]:
    data = {"locator": locator, "source_path": source_path}
    data.update(extra)
    return data


SOURCE_LOCATORS = {
    "article_meta": source_locator("xml:article-meta", f"papers/{PAPER_ID}/source/paper.xml"),
    "antibacterial_section": source_locator(
        "xml:sec=16:Anti-bacterial molecules",
        f"papers/{PAPER_ID}/source/paper.xml",
    ),
    "table14_defensin": source_locator("xml:table=14:row=16", f"papers/{PAPER_ID}/source/paper.xml"),
    "table15_defensin": source_locator("xml:table=15:row=17", f"papers/{PAPER_ID}/source/paper.xml"),
    "table16_defensin": source_locator("xml:table=16:row=16", f"papers/{PAPER_ID}/source/paper.xml"),
    "figure10_caption": source_locator("xml:fig=10:Figure 10", f"papers/{PAPER_ID}/source/paper.xml"),
    "supplement_figure10_sequence": source_locator(
        "supp:local-DRAMP-12864_2007_1209_MOESM10_ESM.txt:line=30",
        f"paper_packets/{PAPER_ID}/extracted/supplementary_text/local-DRAMP-12864_2007_1209_MOESM10_ESM.txt",
    ),
    "database_manifest": source_locator(
        "database:database_source_manifest",
        f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    ),
}


def tool_attempts() -> list[str]:
    return [
        "jq JSON artifact review",
        "rg source/database keyword search",
        "Python ElementTree extraction of XML table rows 14-16",
        "existing pdftotext outputs reviewed for paper PDF and OA package PDF",
        "supplementary PDF text outputs reviewed, especially MOESM10 Figure 10 alignment",
        "file type inspection of supplementary .bin and .pdf assets",
        "database JSONL row review for linked DRAMP/dbAMP/literature records",
        "semantic_three_layer_gate.py rerun",
        "check_three_layer_publication_quality.py rerun",
    ]


def unrecoverable_gap(paths: list[str]) -> dict[str, Any]:
    return {
        "gap_code": "no_primary_activity_or_toxicity_assay_in_local_material",
        "source_paths_checked": paths,
        "tools_attempted": tool_attempts(),
        "why_unrecoverable": (
            "The local XML/PDF/OA package/supplementary text and linked database rows support a putative "
            "LuloDEF defensin identity and immune-context discussion, but do not contain primary MIC, MBC, "
            "target-organism, hemolysis, cytotoxicity, or other row-level activity/toxicity assay values."
        ),
        "impact": (
            "Worker-2 cannot produce source-supported activity_records without fabricating values; "
            "the strict semantic gate should continue to flag missing_activity_records."
        ),
        "owner_worker": "worker-2",
        "blocks_publication_grade": True,
        "next_action": "record_and_continue",
    }


def linked_row_locator(table: str, index: int) -> dict[str, Any]:
    return source_locator(
        f"database:{table}:row={index}",
        f"paper_packets/{PAPER_ID}/database/{table}.jsonl",
    )


def dramp_audit(row: dict[str, Any], index: int, table: str) -> dict[str, Any]:
    return {
        "source_id": f"DRAMP:{row.get('DRAMP_ID') or row.get('source_id') or 'DRAMP04475'}",
        "sequence_key": row.get("sequence_key") or "DRAMP:DRAMP04475",
        "source_table": table,
        "database": "DRAMP",
        "status": "source_conflict",
        "layer1_status": "source_conflict",
        "name_check": {
            "status": "source_supported_identity_context",
            "database_name": row.get("Name") or row.get("subject_name") or "Putative defensin",
            "primary_source_name": "LuloDEF",
            "primary_source_locators": [
                SOURCE_LOCATORS["antibacterial_section"],
                SOURCE_LOCATORS["table14_defensin"],
                SOURCE_LOCATORS["table15_defensin"],
                SOURCE_LOCATORS["table16_defensin"],
            ],
        },
        "sequence_check": {
            "status": "source_conflict",
            "database_sequence": row.get("Sequence") or "",
            "source_relation": (
                "The DRAMP peptide sequence is present as a fragment of the LuloDEF Figure 10 alignment, "
                "but the paper does not explicitly define the DRAMP mature-peptide boundary as the complete "
                "primary-source sequence."
            ),
            "source_locator": {
                **SOURCE_LOCATORS["supplement_figure10_sequence"],
                "supplementary_sources": [SOURCE_LOCATORS["supplement_figure10_sequence"]["source_path"]],
            },
        },
        "activity_check": {
            "status": "database_only_no_primary_assay",
            "database_activity": row.get("Activity") or row.get("activity_text") or "",
            "database_target_organism": row.get("Target_Organism") or row.get("target_organism_text") or "",
            "assay_fields_present": False,
            "primary_activity_record_id": None,
        },
        "citation_traceability": SOURCE_LOCATORS["article_meta"],
        "traceability": linked_row_locator(table, index),
        "matched_activity_record_id": "",
        "conflict_flags": [
            "database_activity_without_primary_assay",
            "database_mature_sequence_boundary_not_explicit_in_primary_source",
        ],
        "conflict_context": (
            "Conflict preserved: the primary paper supports a putative LuloDEF defensin transcript and "
            "sequence context, but local primary material does not report antimicrobial assay values, "
            "targets, toxicity, or an explicitly normalized mature peptide matching the database row."
        ),
        "review_notes": (
            "Do not promote this DRAMP row to source_verified activity evidence; keep it as a database "
            "activity annotation with source-supported identity context only."
        ),
    }


def experiment_audit(row: dict[str, Any], index: int) -> dict[str, Any]:
    if str(row.get("sequence_key") or "").startswith("dbAMP:"):
        return {
            "source_id": row.get("sequence_key") or "dbAMP:dbAMP_15622",
            "sequence_key": row.get("sequence_key") or "dbAMP:dbAMP_15622",
            "source_table": row.get("source_table") or "data/dbamp3_detail_basic.csv",
            "database": "dbAMP",
            "status": "database_only_no_primary_source",
            "layer1_status": "database_only_no_primary_source",
            "name_check": {
                "status": "source_supported_identity_context_only",
                "database_subject": row.get("title") or "",
                "primary_source_name": "LuloDEF",
                "primary_source_locators": [
                    SOURCE_LOCATORS["antibacterial_section"],
                    SOURCE_LOCATORS["table14_defensin"],
                    SOURCE_LOCATORS["table16_defensin"],
                ],
            },
            "activity_check": {
                "status": "no_primary_assay_fields",
                "database_activity": row.get("activity_text") or "",
                "database_assay_text": row.get("assay_text") or "",
                "primary_activity_record_id": None,
            },
            "sequence_check": {
                "status": "database_only_no_primary_source",
                "source_locator": linked_row_locator("linked_experiment_records", index),
            },
            "citation_traceability": SOURCE_LOCATORS["article_meta"],
            "traceability": linked_row_locator("linked_experiment_records", index),
            "matched_activity_record_id": "",
            "conflict_context": (
                "Database-only row retained: local primary material supports LuloDEF identity context but "
                "does not provide the dbAMP activity/assay endpoint as primary-source evidence."
            ),
            "review_notes": "No source-supported activity/toxicity row can be recovered from this dbAMP-linked entry.",
        }

    return {
        "source_id": row.get("sequence_key") or "DRAMP:DRAMP04475",
        "sequence_key": row.get("sequence_key") or "DRAMP:DRAMP04475",
        "source_table": row.get("source_table") or "linked_experiment_records.jsonl",
        "database": "DRAMP",
        "status": "source_conflict",
        "layer1_status": "source_conflict",
        "activity_check": {
            "status": "database_only_no_primary_assay",
            "database_activity": row.get("activity_text") or "",
            "database_target_organism": row.get("target_organism_text") or "",
            "assay_fields_present": False,
            "primary_activity_record_id": None,
        },
        "sequence_check": {
            "status": "source_conflict",
            "source_locator": {
                **SOURCE_LOCATORS["supplement_figure10_sequence"],
                "supplementary_sources": [SOURCE_LOCATORS["supplement_figure10_sequence"]["source_path"]],
            },
        },
        "citation_traceability": SOURCE_LOCATORS["article_meta"],
        "traceability": linked_row_locator("linked_experiment_records", index),
        "matched_activity_record_id": "",
        "conflict_flags": ["database_experiment_row_without_primary_assay"],
        "conflict_context": (
            "Conflict preserved: linked DRAMP experiment row contains no recoverable primary assay endpoint, "
            "value, unit, or target in the local paper materials."
        ),
        "review_notes": "Retained as database conflict, not as primary activity evidence.",
    }


def literature_audit(row: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "source_id": row.get("sequence_key") or "DRAMP:DRAMP04475",
        "sequence_key": row.get("sequence_key") or "DRAMP:DRAMP04475",
        "source_table": "linked_literature_records.jsonl",
        "database": row.get("database") or "DRAMP",
        "status": "source_verified",
        "layer1_status": "source_verified",
        "citation_traceability": SOURCE_LOCATORS["article_meta"],
        "traceability": linked_row_locator("linked_literature_records", index),
        "sequence_check": {
            "status": "citation_link_verified_only",
            "source_locator": SOURCE_LOCATORS["article_meta"],
        },
        "matched_activity_record_id": "",
        "review_notes": (
            "Literature DOI/PMID link is source-verified for citation traceability only; it does not verify "
            "the DRAMP antimicrobial activity annotation."
        ),
    }


def build_database_audit(generated_at: str) -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    for index, row in enumerate(read_jsonl(PACKET / "database" / "linked_dramp_activity_records.jsonl"), start=1):
        audits.append(dramp_audit(row, index, "linked_dramp_activity_records"))
    for index, row in enumerate(read_jsonl(PACKET / "database" / "linked_experiment_records.jsonl"), start=1):
        audits.append(experiment_audit(row, index))
    for index, row in enumerate(read_jsonl(PACKET / "database" / "linked_literature_records.jsonl"), start=1):
        audits.append(literature_audit(row, index))

    summary = Counter(str(item["layer1_status"]) for item in audits)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "audit_scope": (
            "Worker-4 re-reviewed linked DRAMP/dbAMP/literature rows against XML/PDF/supplement/database "
            "locators. Identity context is retained, but activity rows without primary assays remain conflict "
            "or database-only records."
        ),
        "database_row_counts": database_counts(),
        "record_audits": audits,
        "status_summary": dict(sorted(summary.items())),
        "unrecoverable_material_gaps": [],
    }


def build_activity(generated_at: str, paths: list[str], gap: dict[str, Any]) -> dict[str, Any]:
    dramp_rows = read_jsonl(PACKET / "database" / "linked_dramp_activity_records.jsonl")
    experiment_rows = read_jsonl(PACKET / "database" / "linked_experiment_records.jsonl")
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "worker_owner": "worker-2",
        "activity_records": [],
        "toxicity_records": [],
        "candidate_entity_records": [
            {
                "entity_id": "entity-lulodef-eu124626",
                "entity_type": "putative_defensin_transcript",
                "name": "LuloDEF",
                "cluster": "1960",
                "organism": "Lutzomyia longipalpis",
                "source_supported_fields": {
                    "putative_function": "Defensin",
                    "gene_name": "LuloDEF",
                    "localization": "Secreted",
                    "genbank": "EU124626",
                    "sequence_relation_to_dramp": (
                        "DRAMP04475 sequence appears as a fragment of the LuloDEF Figure 10 alignment; "
                        "primary paper does not report MIC or toxicity assays."
                    ),
                },
                "not_promoted_to_activity_record": True,
                "source_locators": [
                    SOURCE_LOCATORS["antibacterial_section"],
                    SOURCE_LOCATORS["table14_defensin"],
                    SOURCE_LOCATORS["table15_defensin"],
                    SOURCE_LOCATORS["table16_defensin"],
                    SOURCE_LOCATORS["figure10_caption"],
                    SOURCE_LOCATORS["supplement_figure10_sequence"],
                ],
            }
        ],
        "database_activity_annotations_not_primary_assays": [
            {
                "source_id": row.get("DRAMP_ID") or row.get("source_id"),
                "sequence_key": row.get("sequence_key"),
                "database": "DRAMP",
                "activity_text": row.get("Activity") or "",
                "target_organism_text": row.get("Target_Organism") or "",
                "assay_text": row.get("Assay") or "",
                "assessment": "database_annotation_only_no_primary_assay",
            }
            for row in dramp_rows
        ]
        + [
            {
                "source_id": row.get("source_id"),
                "sequence_key": row.get("sequence_key"),
                "database": "dbAMP" if str(row.get("sequence_key") or "").startswith("dbAMP:") else "DRAMP",
                "activity_text": row.get("activity_text") or "",
                "target_organism_text": row.get("target_organism_text") or "",
                "assay_text": row.get("assay_text") or "",
                "assessment": "database_annotation_only_no_primary_assay",
            }
            for row in experiment_rows
        ],
        "extraction_issues": [
            {
                "code": gap["gap_code"],
                "severity": "blocking",
                "owner_worker": "worker-2",
                "reason": gap["why_unrecoverable"],
                "source_paths_checked": paths,
            }
        ],
        "unrecoverable_material_gaps": [gap],
        "source_reviewed_surfaces": paths,
        "parser_quality_control": {
            "database_only_rows_not_promoted": True,
            "no_fabricated_activity_values": True,
            "activity_record_count": 0,
        },
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "mechanism_claims": [
            {
                "claim_id": "context-lulodef-immune-001",
                "claim_text": (
                    "LuloDEF is source-supported as a putative secreted defensin transcript with conserved "
                    "cysteine/defensin homology; this is immune-context evidence only."
                ),
                "entity_scope": "LuloDEF / cluster 1960",
                "evidence_class": "indirect_mechanism_context",
                "direct_assay_types": [],
                "limitations": "No direct antimicrobial, Leishmania-killing, hemolysis, or toxicity assay is reported locally.",
                "source_locator": [
                    SOURCE_LOCATORS["antibacterial_section"],
                    SOURCE_LOCATORS["table14_defensin"],
                    SOURCE_LOCATORS["table16_defensin"],
                    SOURCE_LOCATORS["figure10_caption"],
                    SOURCE_LOCATORS["supplement_figure10_sequence"],
                ],
            },
            {
                "claim_id": "context-lulopgrp-immune-002",
                "claim_text": (
                    "LuloPGRP is discussed as a putative peptidoglycan-recognition protein that may contribute "
                    "to sand fly immune defense against bacteria."
                ),
                "entity_scope": "LuloPGRP / cluster 235",
                "evidence_class": "indirect_mechanism_context",
                "direct_assay_types": [],
                "limitations": "The paper provides transcriptomic and homology context, not direct antimicrobial assay output.",
                "source_locator": [
                    SOURCE_LOCATORS["antibacterial_section"],
                    source_locator("xml:table=14:row=15", f"papers/{PAPER_ID}/source/paper.xml"),
                    source_locator("xml:table=15:row=16", f"papers/{PAPER_ID}/source/paper.xml"),
                    source_locator("xml:table=16:row=15", f"papers/{PAPER_ID}/source/paper.xml"),
                    source_locator(
                        "supp:local-DRAMP-12864_2007_1209_MOESM9_ESM.txt:lines=10-11",
                        f"paper_packets/{PAPER_ID}/extracted/supplementary_text/local-DRAMP-12864_2007_1209_MOESM9_ESM.txt",
                    ),
                ],
            },
            {
                "claim_id": "context-leishmania-transcriptome-003",
                "claim_text": (
                    "The source paper supports transcriptomic modulation of sand fly midgut genes during "
                    "Leishmania infection and blood meal digestion."
                ),
                "entity_scope": "Lutzomyia longipalpis midgut transcriptome",
                "evidence_class": "transcriptomic_association_context",
                "direct_assay_types": [],
                "limitations": "This does not establish direct AMP mechanism or antimicrobial potency for DRAMP04475.",
                "source_locator": [
                    source_locator("xml:sec=18:Transcripts differentially expressed by the presence of Leishmania infantum chagasi", f"papers/{PAPER_ID}/source/paper.xml"),
                    source_locator("xml:sec=19:Conclusion", f"papers/{PAPER_ID}/source/paper.xml"),
                    source_locator("xml:table=19", f"papers/{PAPER_ID}/source/paper.xml"),
                    source_locator("xml:table=20", f"papers/{PAPER_ID}/source/paper.xml"),
                ],
            },
        ],
        "unrecoverable_material_gaps": [],
    }


def qc_reasons() -> list[dict[str, Any]]:
    return [
        {
            "code": "no_primary_activity_toxicity_assay_in_local_material",
            "owner_worker": "worker-2",
            "severity": "blocking",
            "reason": (
                "XML/PDF/OA/supplement/database review found no primary MIC, MBC, target-organism, "
                "hemolysis, cytotoxicity, or equivalent activity/toxicity endpoint rows."
            ),
        },
        {
            "code": "database_activity_annotation_not_primary_source_supported",
            "owner_worker": "worker-4",
            "severity": "major",
            "reason": (
                "DRAMP/dbAMP rows link LuloDEF to antimicrobial/database activity context, but the primary "
                "paper supports only putative defensin identity and immune-context discussion."
            ),
        },
        {
            "code": "publication_grade_blocked_by_unrecoverable_activity_gap",
            "owner_worker": "worker-6",
            "severity": "blocking",
            "reason": "Publication-grade acceptance remains blocked because the source-supported activity layer is empty by evidence, not by parser omission.",
        },
    ]


def rework_target(gap: dict[str, Any], paths: list[str]) -> dict[str, Any]:
    return {
        "ticket_id": NEW_TICKET_ID,
        "supersedes_ticket_id": OLD_TICKET_ID,
        "paper_id": PAPER_ID,
        "created_at": gap.get("created_at"),
        "worker": "worker-6",
        "owner_workers": ["worker-2", "worker-4", "worker-6"],
        "target_queue": "analysis",
        "layer": "activity_toxicity/database_adjudication/final_review",
        "artifact_path": f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
        "related_artifact_paths": [
            f"paper_packets/{PAPER_ID}/analysis/activity_toxicity_evidence.json",
            f"papers/{PAPER_ID}/final/database_record_verification.json",
            f"papers/{PAPER_ID}/final/review_report.json",
            f"papers/{PAPER_ID}/work/review/quality_feedback.json",
        ],
        "failure_code": gap["gap_code"],
        "omission_code": "primary_activity_endpoint_absent_after_source_exhaustion",
        "severity": "blocking",
        "status": "open_blocked_unrecoverable_local_material",
        "blocks": ["publication_grade_ready", "final_approval"],
        "required_action": (
            "Keep paper non-accepted unless new local primary material or an external/manual acquisition "
            "step provides source-supported activity/toxicity endpoints; do not fabricate assay rows from "
            "database-only DRAMP/dbAMP annotations."
        ),
        "source_paths_to_check": [
            f"papers/{PAPER_ID}/source/paper.xml",
            f"papers/{PAPER_ID}/source/paper.pdf",
            f"paper_packets/{PAPER_ID}/extracted/supplementary_text/",
            f"paper_packets/{PAPER_ID}/database/*.jsonl",
        ],
        "source_paths_checked": paths,
        "unrecoverable_material_gaps": [gap],
    }


def build_review(generated_at: str, paths: list[str], gap: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    counts = database_counts()
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "updated_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "blocked_missing_primary_material",
        "publication_grade": False,
        "validator_contract_passed": True,
        "summary": (
            "Source re-review recovered LuloDEF defensin identity context but found no local primary "
            "activity/toxicity assay rows; the paper remains non-accepted with an unrecoverable local "
            "activity gap."
        ),
        "adjudication_summary": (
            "Worker-2/4/6 bounded re-review resolved the prior parser-vs-source ambiguity: missing "
            "activity rows are a true local source limitation, not an extraction value to invent."
        ),
        "checked_inputs": paths,
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
        },
        "semantic_quality_checks": {
            "activity_records": 0,
            "activity_rows_parsed": 0,
            "database_snapshots": counts,
            "mechanism_claims": 3,
            "unrecoverable_material_gap_count": 1,
            "open_rework_ticket_ids": [OLD_TICKET_ID, NEW_TICKET_ID],
        },
        "per_layer_decision_rationale": {
            "layer_1_database": (
                "DRAMP/dbAMP links are preserved as source_conflict or database_only_no_primary_source "
                "for activity; the literature citation link is source_verified only for DOI/PMID traceability."
            ),
            "layer_2_activity_toxicity": (
                "No source-supported activity/toxicity endpoint rows are present in the local XML, PDF, "
                "supplement text, OA package, or linked database records."
            ),
            "layer_3_mechanism": (
                "LuloDEF/LuloPGRP are retained as indirect immune/transcriptomic context only; no direct "
                "mechanism or potency assay is claimed."
            ),
            "worker_6_decision": "Publication-grade approval refused; keep targeted unrecoverable-gap ticket open.",
        },
        "caution_findings": [
            {
                "caution_code": "database_activity_annotation_without_primary_assay",
                "evidence_context": "DRAMP04475/dbAMP_15622 are useful identity/context links but cannot supply primary activity rows.",
            },
            {
                "caution_code": "sequence_fragment_boundary_unresolved",
                "evidence_context": "DRAMP04475 peptide is found as a fragment in the LuloDEF alignment; mature boundary is not explicitly normalized in the paper.",
            },
        ],
        "qc_failure_reasons": qc_reasons(),
        "unrecoverable_material_gaps": [gap],
        "rework_targets": [target],
        "strict_gate": {
            "required_rework_count": 1,
            "open_ticket_ids": [OLD_TICKET_ID, NEW_TICKET_ID],
            "publication_grade_ready": False,
        },
    }


def build_quality_feedback(generated_at: str, paths: list[str], gap: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "updated_at": generated_at,
        "issue_count": 3,
        "qc_failure_reasons": qc_reasons(),
        "rework_context_packet_required": False,
        "rework_targets": [target],
        "unrecoverable_material_gaps": [gap],
        "source_paths_checked": paths,
        "tools_attempted": tool_attempts(),
        "publication_grade_ready": False,
        "final_decision": "blocked_missing_primary_material",
    }


def run_gate_commands() -> dict[str, Any]:
    semantic_cmd = [
        sys.executable,
        str(ROOT / ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py"),
        "--root",
        str(ROOT),
        "--paper-id",
        PAPER_ID,
        "--json",
    ]
    semantic = subprocess.run(semantic_cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    SEMANTIC_REPORT.write_text(semantic.stdout, encoding="utf-8")
    semantic_payload = json.loads(semantic.stdout) if semantic.stdout.strip() else {}

    publication_cmd = [
        sys.executable,
        str(ROOT / ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py"),
        "--root",
        str(ROOT),
        "--manifest",
        str(MANIFEST),
        "--json-out",
        str(PUBLICATION_REPORT),
    ]
    publication = subprocess.run(publication_cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    publication_payload = read_json(PUBLICATION_REPORT, {})

    return {
        "semantic": {
            "command": " ".join(semantic_cmd),
            "returncode": semantic.returncode,
            "report_path": rel(SEMANTIC_REPORT),
            "publication_grade_pass_count": semantic_payload.get("publication_grade_pass_count"),
            "publication_grade_fail_count": semantic_payload.get("publication_grade_fail_count"),
            "issue_count": (semantic_payload.get("results") or [{}])[0].get("issue_count") if semantic_payload.get("results") else None,
            "issue_codes": [
                issue.get("code")
                for issue in ((semantic_payload.get("results") or [{}])[0].get("issues") or [])
            ],
        },
        "publication_quality": {
            "command": " ".join(publication_cmd),
            "returncode": publication.returncode,
            "report_path": rel(PUBLICATION_REPORT),
            "publication_grade_pass": publication_payload.get("publication_grade_pass"),
            "risk_counts": publication_payload.get("risk_counts"),
        },
    }


def update_manifest(generated_at: str) -> None:
    path = PACKET / "packet_manifest.json"
    manifest = read_json(path, {})
    if not isinstance(manifest, dict):
        manifest = {}
    manifest.update(
        {
            "paper_id": PAPER_ID,
            "updated_at": generated_at,
            "analysis_queue_status": "analysis_blocked_unrecoverable_material_gap",
            "material_queue_status": manifest.get("material_queue_status") or "material_extracted_with_gaps",
            "open_rework_ticket_ids": [OLD_TICKET_ID, NEW_TICKET_ID],
            "known_missing_or_blocked_materials": [
                "no_primary_activity_or_toxicity_assay_in_local_material"
            ],
        }
    )
    write_json(path, manifest)


def main() -> int:
    generated_at = now_utc()
    paths = checked_source_paths()
    gap = unrecoverable_gap(paths)
    gap["created_at"] = generated_at
    target = rework_target(gap, paths)
    target["created_at"] = generated_at

    activity = build_activity(generated_at, paths, gap)
    database = build_database_audit(generated_at)
    mechanism = build_mechanism(generated_at)
    review = build_review(generated_at, paths, gap, target)
    quality = build_quality_feedback(generated_at, paths, gap, target)

    write_json(PACKET / "analysis" / "activity_toxicity_evidence.json", activity)
    write_json(PAPER / "final" / "activity_toxicity_evidence.json", activity)
    write_json(PACKET / "analysis" / "database_record_audit.json", database)
    write_json(PAPER / "final" / "database_record_verification.json", database)
    write_json(PACKET / "analysis" / "mechanism_evidence.json", mechanism)
    write_json(PAPER / "final" / "mechanism_evidence.json", mechanism)
    write_json(PAPER / "final" / "mechanism_ontology_record.json", mechanism)
    write_json(PACKET / "analysis" / "adjudication_report.json", review)
    write_json(PAPER / "final" / "review_report.json", review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality)
    write_json(
        PACKET / "analysis" / "analysis_status.json",
        {
            "paper_id": PAPER_ID,
            "generated_at": generated_at,
            "status": "analysis_blocked_unrecoverable_material_gap",
            "activity_record_count": 0,
            "activity_extraction_issue_count": 1,
            "activity_extraction_issues": [gap["gap_code"]],
            "database_status_summary": database["status_summary"],
            "mechanism_claim_count": len(mechanism["mechanism_claims"]),
            "open_rework_ticket_ids": [OLD_TICKET_ID, NEW_TICKET_ID],
            "publication_grade_ready": False,
        },
    )
    update_manifest(generated_at)

    append_jsonl_once(REWORK / "rework_requests.jsonl", target, "ticket_id")

    gate_results = run_gate_commands()
    response = {
        "response_id": "rr-20260503-worker246-source-exhaustion",
        "ticket_id": OLD_TICKET_ID,
        "responds_to_ticket_ids": [OLD_TICKET_ID, NEW_TICKET_ID],
        "paper_id": PAPER_ID,
        "created_at": generated_at,
        "owner_workers": ["worker-2", "worker-4", "worker-6"],
        "status": "not_closed_unrecoverable_local_gap_open",
        "checked_source_paths": paths,
        "tools_attempted": tool_attempts(),
        "repair_summary": {
            "activity_records": 0,
            "database_status_summary": database["status_summary"],
            "mechanism_claims": len(mechanism["mechanism_claims"]),
            "publication_grade_ready": False,
        },
        "what_was_checked": [
            "Primary XML/PDF table and section evidence for LuloDEF/LuloPGRP",
            "Supplementary PDF text for Figure 10 defensin alignment",
            "OA package manifest and extracted NXML/PDF text",
            "Linked DRAMP/dbAMP/literature JSONL rows",
            "Prior packet/final/rework artifacts from the message-transfer test",
        ],
        "what_remains": [
            "No source-supported activity/toxicity endpoint rows are locally recoverable.",
            "DRAMP/dbAMP antimicrobial activity annotations remain database-only/source-conflict evidence.",
            "Paper remains non-accepted with targeted unrecoverable-gap ticket open.",
        ],
        "unrecoverable_material_gaps": [gap],
        "artifacts_updated": [
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
        "gate_results": gate_results,
    }
    append_jsonl_once(REWORK / "rework_responses.jsonl", response, "response_id")

    print(
        json.dumps(
            {
                "ok": True,
                "paper_id": PAPER_ID,
                "generated_at": generated_at,
                "activity_records": 0,
                "database_status_summary": database["status_summary"],
                "semantic_gate": gate_results["semantic"],
                "publication_quality": gate_results["publication_quality"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
