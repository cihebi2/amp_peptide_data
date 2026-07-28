#!/usr/bin/env python3
"""Repair worker-2/4/6 artifacts for doi__10.1371_journal.pone.0110809.

This paper's local DOI packet resolves to a PLOS ONE bioconversion article,
while the linked AMP database rows describe Muscin from Acta Entomologica
Sinica. The repair preserves database-only Muscin values and leaves the paper
non-accepted because no local primary Muscin source is available.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.1371_journal.pone.0110809"
STAMP = "2026-05-05T17:01:17Z"
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
REPORTS = ROOT / "reports"
MANIFEST = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"

APD6_ACTIVITY = "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/apd6_activity_text_records.csv"
DBAASP_ASSAY = "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/dbaasp_assay_records.csv"
DRAMP_ACTIVITY = "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/dramp_activity_text_records.csv"
SEQUENCES = "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv"
LITERATURE = "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/literature/all_literature_records.csv"


def source_paths_checked() -> list[str]:
    return [
        "rework_context/doi__10.1371_journal.pone.0110809/handoff_context.json",
        "paper_packets/doi__10.1371_journal.pone.0110809/packet_manifest.json",
        "paper_packets/doi__10.1371_journal.pone.0110809/locators/locator_index.json",
        "paper_packets/doi__10.1371_journal.pone.0110809/raw/paper.xml",
        "paper_packets/doi__10.1371_journal.pone.0110809/raw/paper.pdf",
        "paper_packets/doi__10.1371_journal.pone.0110809/raw/oa_package/local-APD6-pmc_package.tar.gz",
        "paper_packets/doi__10.1371_journal.pone.0110809/extracted/xml_sections.json",
        "paper_packets/doi__10.1371_journal.pone.0110809/extracted/pdf_text/pone.0110809.txt",
        "paper_packets/doi__10.1371_journal.pone.0110809/extracted/figure_captions.json",
        "paper_packets/doi__10.1371_journal.pone.0110809/extracted/supplementary_text.jsonl",
        "paper_packets/doi__10.1371_journal.pone.0110809/extracted/supplementary_tables.json",
        "paper_packets/doi__10.1371_journal.pone.0110809/database/linked_literature_records.jsonl",
        APD6_ACTIVITY,
        DBAASP_ASSAY,
        DRAMP_ACTIVITY,
        SEQUENCES,
        LITERATURE,
        "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1371_journal.pone.0110809/metadata.json",
        "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1371_journal.pone.0110809/asset_manifest.csv",
        "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1371_journal.pone.0110809/pdf/local-APD6-paper.pdf",
        "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1371_journal.pone.0110809/xml/local-APD6-pone.0110809.nxml",
        "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1371_journal.pone.0110809/supplementary/",
    ]


def tools_attempted() -> list[str]:
    return [
        "jq artifact review",
        "rg over XML/PDF text/HTML/database rows for Muscin, MIC, AP02594, and sequence evidence",
        "file on landed supplementary assets",
        "pdfinfo on staged PDFs",
        "md5sum comparison of landed PDFs",
        "tar -tzf OA package inventory",
        "semantic_three_layer_gate.py",
        "check_three_layer_publication_quality.py",
    ]


def unrecoverable_gap() -> dict[str, Any]:
    return {
        "gap_code": "primary_muscin_source_not_locally_recovered",
        "source_paths_checked": source_paths_checked(),
        "tools_attempted": tools_attempted(),
        "why_unrecoverable": (
            "All local DOI/PDF/XML/OA/package/supplementary surfaces resolve to the PLOS ONE "
            "gibberellin-fermentation-residue bioconversion article, not the Muscin antimicrobial "
            "peptide article named by the APD6/DBAASP/DRAMP database rows. No local primary source "
            "contains the Muscin sequence, MIC table, hemolysis assay, or mechanism evidence."
        ),
        "impact": (
            "Worker-2 cannot promote database-only MIC/hemolysis annotations to primary-source "
            "activity rows; worker-4 must preserve source_conflict/database_only statuses; worker-6 "
            "must leave publication_grade false."
        ),
        "owner_worker": "worker-2|worker-4|worker-6",
        "blocks_publication_grade": True,
        "next_action": "record_and_continue",
    }


def qc_failure_reasons() -> list[dict[str, str]]:
    return [
        {
            "code": "primary_source_linkage_conflict",
            "owner_worker": "worker-4 + worker-6",
            "severity": "blocking",
            "reason": (
                "The linked APD6 Muscin literature row is keyed to DOI/PMID/PMCID values whose "
                "local primary assets are a different PLOS ONE bioconversion paper."
            ),
        },
        {
            "code": "no_primary_supported_amp_activity_rows",
            "owner_worker": "worker-2",
            "severity": "blocking",
            "reason": (
                "Local XML/PDF/OA/package/supplementary assets contain no primary Muscin MIC, "
                "hemolysis, cytotoxicity, or antimicrobial assay table; database-only activity "
                "annotations are preserved separately and not counted as primary rows."
            ),
        },
        {
            "code": "database_records_conflicted_or_database_only",
            "owner_worker": "worker-4",
            "severity": "major",
            "reason": (
                "APD6, DBAASP, and DRAMP rows support Muscin database annotations but disagree on "
                "source linkage, organism spelling, and one sequence residue; none is primary-source "
                "verified from the staged paper packet."
            ),
        },
        {
            "code": "publication_grade_blocked_unrecoverable_material_gap",
            "owner_worker": "worker-6",
            "severity": "blocking",
            "reason": (
                "Bounded local recovery exhausted the available paper packet and merged-row evidence "
                "without recovering the primary Muscin paper."
            ),
        },
    ]


def source_locator(path: str, locator: str) -> dict[str, str]:
    return {"source_path": path, "locator": locator}


def database_activity_annotations() -> list[dict[str, Any]]:
    dbaasp_values = [
        ("6854", "hemolysis", "Rabbit erythrocytes", "10% Hemolysis", "0.327", "uM"),
        ("6855", "hemolysis", "Rabbit erythrocytes", "18% Hemolysis", "54", "uM"),
        ("6856", "hemolysis", "Rabbit erythrocytes", "19% Hemolysis", "65.4", "uM"),
        ("60072", "MIC", "Microbacterium oxydans", "MIC", "0.164", "uM"),
        ("60073", "MIC", "Bacillus cereus", "MIC", "0.327", "uM"),
        ("60074", "MIC", "Bacillus megaterium", "MIC", "3.27", "uM"),
        ("60075", "MIC", "Micrococcus luteus", "MIC", "16.4", "uM"),
        ("60076", "MIC", "Sporosarcina ureae", "MIC", "164", "uM"),
        ("60077", "MIC", "Staphylococcus aureus", "MIC", "164", "uM"),
        ("60078", "MIC", "Aeromonas hydrophila", "MIC", "1.64", "uM"),
        ("60079", "MIC", "Salmonella enterica subsp. enterica serovar Gallinarum", "MIC", "1.64", "uM"),
        ("60080", "MIC", "Lelliottia amnigena", "MIC", "16.4", "uM"),
        ("60081", "MIC", "Escherichia coli", "MIC", "16.4", "uM"),
        ("60082", "MIC", "Salmonella enterica subsp. enterica serovar Typhi", "MIC", "16.4", "uM"),
        ("60083", "MIC", "Pseudomonas fluorescens", "MIC", "32.7", "uM"),
        ("60084", "MIC", "Proteus sp.", "MIC", "164", "uM"),
        ("60085", "MIC", "Burkholderia stabilis", "MIC", ">164", "uM"),
        ("60086", "MIC", "Kluyvera cryocrescens", "MIC", ">164", "uM"),
        ("60087", "MIC", "Shigella sp.", "MIC", "16.4", "uM"),
    ]
    return [
        {
            "annotation_id": "dbann-apd6-ap02594-summary",
            "provenance": "database_only_not_primary_source",
            "source_database": "APD6",
            "source_id": "AP02594",
            "sequence_key": "APD6:AP02594",
            "entity_name": "Muscin",
            "reported_sequence": "EWKLPDLIINHITLTRRNCNKYRCG",
            "reported_source_organism": "Musca demestica",
            "activity_summary": (
                "APD6 text reports MIC values against Gram-positive and Gram-negative bacteria "
                "and rabbit erythrocyte hemolysis, but this is database text rather than a local "
                "primary-source assay table."
            ),
            "source_locator": source_locator(APD6_ACTIVITY, "csv:line=2595"),
            "primary_source_status": "not_primary_source_verified",
            "cautions": [
                "organism spelling Musca demestica conflicts with Musca domestica in the article title and DRAMP",
                "database row's DOI/PMID/PMCID linkage resolves locally to a non-Muscin PLOS ONE paper",
            ],
        },
        {
            "annotation_id": "dbann-dbaasp-dbaaspr_8351-assays",
            "provenance": "database_only_not_primary_source",
            "source_database": "DBAASP",
            "source_id": "DBAASPR_8351",
            "sequence_key": "DBAASP:DBAASPR_8351",
            "entity_name": "Muscin",
            "reported_sequence": "EWKLPDLIINHITLTRRNCFKYRCG",
            "activity_values": [
                {
                    "database_assay_id": assay_id,
                    "endpoint": endpoint,
                    "target": target,
                    "measure_value": measure,
                    "raw_value": raw_value,
                    "raw_unit": unit,
                    "source_locator": source_locator(DBAASP_ASSAY, f"csv:line={74264 + i}"),
                }
                for i, (assay_id, endpoint, target, measure, raw_value, unit) in enumerate(dbaasp_values)
            ],
            "primary_source_status": "not_primary_source_verified",
            "cautions": [
                "DBAASP sequence has Cys-Phe-Lys where APD6/DRAMP report Cys-Asn-Lys",
                "DBAASP literature row has no locally staged primary paper for source verification",
            ],
        },
        {
            "annotation_id": "dbann-dramp-dramp37362-summary",
            "provenance": "database_only_not_primary_source",
            "source_database": "DRAMP",
            "source_id": "DRAMP37362",
            "sequence_key": "DRAMP:DRAMP37362",
            "entity_name": "c-Muscin",
            "reported_sequence": "EWKLPDLIINHITLTRRNCNKYRCG",
            "reported_source_organism": "Musca domestica",
            "activity_summary": (
                "DRAMP text reports MIC annotations for Gram-positive and Gram-negative bacteria "
                "and cites DOI 10.16380/j.kcxb.2015.06.005; no matching primary article is staged "
                "under this DOI packet."
            ),
            "source_locator": source_locator(DRAMP_ACTIVITY, "csv:lines=30975-30976"),
            "primary_source_status": "not_primary_source_verified",
            "cautions": [
                "DRAMP citation points to a different DOI than the packet DOI",
                "DRAMP Micrococcus luteus MIC text conflicts with APD6/DBAASP values",
            ],
        },
    ]


def activity_payload() -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": STAMP,
        "owner_worker": "worker-2",
        "review_status": "blocked_missing_primary_material",
        "source_reviewed": True,
        "activity_records": [],
        "activity_record_decision": (
            "No primary-source AMP activity/toxicity rows were extracted because the local paper "
            "packet is not the Muscin primary paper. Database-only activity annotations are retained "
            "below as provenance and must not be treated as primary assay rows."
        ),
        "database_activity_annotations": database_activity_annotations(),
        "supported_local_non_amp_measurements": [
            {
                "record_id": "local-non-amp-ga3-hfl-001",
                "measurement": "GA3 content in HFL/HFL meal/GFR/digested GFR",
                "source_locator": source_locator(
                    "paper_packets/doi__10.1371_journal.pone.0110809/locators/locator_index.json",
                    "xml:table=3:rows=1-5",
                ),
                "curation_note": "Local source measurement is not an AMP activity/toxicity endpoint for Muscin.",
            }
        ],
        "unrecoverable_material_gaps": [unrecoverable_gap()],
        "source_paths_checked": source_paths_checked(),
        "tools_attempted": tools_attempted(),
    }


def database_payload() -> dict[str, Any]:
    audits = [
        {
            "source_id": "AP02594",
            "sequence_key": "APD6:AP02594",
            "source_table": "linked_literature_records.jsonl + merged APD6 rows",
            "database_subject": "Muscin",
            "database_measure": "APD6 sequence/activity text",
            "status": "source_conflict",
            "layer1_status": "source_conflict",
            "reported_sequence": "EWKLPDLIINHITLTRRNCNKYRCG",
            "reported_source_organism": "Musca demestica",
            "traceability": source_locator(
                "paper_packets/doi__10.1371_journal.pone.0110809/database/linked_literature_records.jsonl",
                "jsonl:line=1",
            ),
            "sequence_check": {
                "source_locator": source_locator(APD6_ACTIVITY, "csv:line=2595"),
                "primary_source_status": "not_verified_from_local_primary_source",
            },
            "citation_traceability": source_locator(LITERATURE, "csv:line=180"),
            "conflict_context": (
                "APD6 metadata names a Muscin Acta Entomologica Sinica paper, but the DOI/PMID/PMCID "
                "linkage in the local packet resolves to a PLOS ONE GFR bioconversion article with no "
                "Muscin sequence or antimicrobial assay."
            ),
            "conflict_flags": [
                "wrong_primary_source_linkage",
                "organism_spelling_conflict_Musca_demestica_vs_Musca_domestica",
            ],
            "review_notes": "Do not mark source_verified until the actual Muscin primary article is staged and checked.",
        },
        {
            "source_id": "DBAASPR_8351",
            "sequence_key": "DBAASP:DBAASPR_8351",
            "source_table": "merged DBAASP sequence and assay rows",
            "database_subject": "Muscin",
            "database_measure": "DBAASP MIC and hemolysis rows",
            "status": "source_conflict",
            "layer1_status": "source_conflict",
            "reported_sequence": "EWKLPDLIINHITLTRRNCFKYRCG",
            "traceability": source_locator(SEQUENCES, "csv:line=14713"),
            "sequence_check": {
                "source_locator": source_locator(SEQUENCES, "csv:line=14713"),
                "primary_source_status": "not_verified_from_local_primary_source",
            },
            "citation_traceability": source_locator(LITERATURE, "csv:line=4449"),
            "conflict_context": (
                "DBAASP provides database-only Muscin assay rows and a sequence that differs from "
                "APD6/DRAMP at one residue; no local primary Muscin paper is staged for adjudication."
            ),
            "conflict_flags": [
                "sequence_conflict_DBAASP_vs_APD6_DRAMP",
                "database_only_assay_rows",
            ],
            "review_notes": "Preserve values as database annotations only; not primary-source verified.",
        },
        {
            "source_id": "DRAMP37362",
            "sequence_key": "DRAMP:DRAMP37362",
            "source_table": "merged DRAMP sequence/activity rows",
            "database_subject": "c-Muscin",
            "database_measure": "DRAMP antimicrobial text",
            "status": "database_only_no_primary_source",
            "layer1_status": "database_only_no_primary_source",
            "reported_sequence": "EWKLPDLIINHITLTRRNCNKYRCG",
            "reported_source_organism": "Musca domestica",
            "traceability": source_locator(SEQUENCES, "csv:line=67691"),
            "sequence_check": {
                "source_locator": source_locator(DRAMP_ACTIVITY, "csv:lines=30975-30976"),
                "primary_source_status": "not_verified_from_local_primary_source",
            },
            "citation_traceability": source_locator(LITERATURE, "csv:line=8581"),
            "conflict_context": (
                "DRAMP points to DOI 10.16380/j.kcxb.2015.06.005, while this packet is keyed to "
                "10.1371/journal.pone.0110809. The DRAMP paper is not locally staged."
            ),
            "conflict_flags": [
                "different_true_doi_than_packet",
                "database_only_no_primary_source",
            ],
            "review_notes": "Retain as database-only evidence pending correct primary-source acquisition.",
        },
    ]
    return {
        "paper_id": PAPER_ID,
        "generated_at": STAMP,
        "owner_worker": "worker-4",
        "audit_scope": (
            "Source-reviewed database audit after bounded local recovery. Statuses preserve the "
            "Muscin source/linkage conflict rather than converting database rows to source_verified."
        ),
        "database_row_counts": {
            "packet_linked_literature_records": 1,
            "merged_sequence_records_reviewed": 3,
            "merged_database_activity_annotation_groups": 3,
            "primary_source_verified_records": 0,
        },
        "record_audits": audits,
        "status_summary": {
            "source_conflict": 2,
            "database_only_no_primary_source": 1,
            "source_verified": 0,
        },
        "cross_database_conflicts": [
            "APD6/DRAMP sequence EWKLPDLIINHITLTRRNCNKYRCG vs DBAASP sequence EWKLPDLIINHITLTRRNCFKYRCG",
            "APD6 organism spelling Musca demestica vs DRAMP/article-title Musca domestica",
            "APD6 DOI linkage 10.1371/journal.pone.0110809 vs DRAMP DOI 10.16380/j.kcxb.2015.06.005",
            "DRAMP Micrococcus luteus MIC text conflicts with APD6/DBAASP values",
        ],
        "unrecoverable_material_gaps": [unrecoverable_gap()],
        "source_paths_checked": source_paths_checked(),
        "tools_attempted": tools_attempted(),
    }


def mechanism_payload() -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": STAMP,
        "owner_worker": "worker-6",
        "source_reviewed": True,
        "mechanism_claims": [
            {
                "claim_id": "mech-local-001",
                "claim_text": (
                    "Local primary material does not support a Muscin AMP mechanism claim; the staged "
                    "figures and tables concern GA3 degradation, housefly-larvae bioconversion, and "
                    "nutritional/residue measurements."
                ),
                "entity_scope": "Muscin database rows vs local DOI packet",
                "evidence_class": "no_primary_amp_mechanism_supported",
                "source_locator": source_locator(
                    "paper_packets/doi__10.1371_journal.pone.0110809/extracted/figure_captions.json",
                    "xml:fig=1-4",
                ),
                "limitations": "DRAMP database text lists a cell-membrane binding target, but no local primary source supports promotion to direct_mechanism.",
            }
        ],
        "database_mechanism_annotations": [
            {
                "source_database": "DRAMP",
                "source_id": "DRAMP37362",
                "annotation": "Binding target: Cell membrane",
                "provenance": "database_only_not_primary_source",
                "source_locator": source_locator(DRAMP_ACTIVITY, "csv:lines=30975-30976"),
            }
        ],
        "unrecoverable_material_gaps": [unrecoverable_gap()],
    }


def rework_target() -> dict[str, Any]:
    return {
        "ticket_id": "rwk-20260505-170117-source-linkage-conflict",
        "paper_id": PAPER_ID,
        "created_at": STAMP,
        "requested_by": "worker-6_source_reviewed_repair",
        "target_queue": "material_extraction",
        "worker": "worker-1",
        "owner_worker": "worker-1",
        "layer": "material_source_linkage",
        "severity": "blocking",
        "failing_object": "publication_grade_ready",
        "failure_code": "primary_muscin_source_not_locally_recovered",
        "artifact_path": "paper_packets/doi__10.1371_journal.pone.0110809/packet_manifest.json",
        "source_evidence_to_check": [
            "paper_packets/doi__10.1371_journal.pone.0110809/raw/paper.xml",
            "paper_packets/doi__10.1371_journal.pone.0110809/raw/paper.pdf",
            "paper_packets/doi__10.1371_journal.pone.0110809/raw/oa_package/local-APD6-pmc_package.tar.gz",
            APD6_ACTIVITY,
            DBAASP_ASSAY,
            DRAMP_ACTIVITY,
            LITERATURE,
        ],
        "required_action": (
            "Correct the source linkage/staging for the Muscin Acta Entomologica Sinica paper or "
            "mark the primary source unavailable; do not accept this DOI packet as publication-grade."
        ),
        "blocks": ["publication_grade_ready", "final_approval"],
        "qc_failure_reasons": qc_failure_reasons(),
    }


def review_payload() -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": STAMP,
        "generated_at": STAMP,
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
            "primary_muscin_source": False,
            "unavailable_sources": ["primary Muscin Acta Entomologica Sinica article not staged in local packet"],
        },
        "checked_inputs": source_paths_checked(),
        "semantic_quality_checks": {
            "activity_rows_parsed": 0,
            "database_activity_annotation_groups": 3,
            "database_record_status_summary": database_payload()["status_summary"],
            "mechanism_claims": 1,
            "unrecoverable_material_gap_count": 1,
            "open_rework_ticket_ids": ["rwk-20260505-170117-source-linkage-conflict"],
        },
        "per_layer_decision_rationale": {
            "layer_1_database": (
                "APD6, DBAASP, and DRAMP Muscin records are preserved as source_conflict or "
                "database_only_no_primary_source; no database row is source_verified from the local packet."
            ),
            "layer_2_activity_toxicity": (
                "Database MIC/hemolysis annotations are retained as database-only provenance, but "
                "activity_records remains empty because local primary material has no Muscin assay rows."
            ),
            "layer_3_mechanism": (
                "Local figures/tables do not support a Muscin AMP mechanism. DRAMP cell-membrane "
                "annotation remains database-only and is not promoted to direct_mechanism."
            ),
        },
        "adjudication_summary": (
            "Bounded worker-2/4/6 re-review exhausted the local paper packet and merged database rows. "
            "The staged DOI assets are a non-Muscin PLOS ONE bioconversion article, so Muscin sequence, "
            "activity, toxicity, and mechanism evidence remains database-only/source-conflicted. The paper "
            "must stay non-accepted with a source-linkage/material blocker."
        ),
        "caution_findings": [
            {
                "caution_code": "wrong_primary_source_linkage",
                "evidence_context": "Packet DOI/PMID/PMCID assets resolve to a different PLOS ONE article than the Muscin database title.",
            },
            {
                "caution_code": "database_only_activity_not_primary_evidence",
                "evidence_context": "APD6/DBAASP/DRAMP values are preserved as database annotations only.",
            },
            {
                "caution_code": "cross_database_muscin_conflicts",
                "evidence_context": "Sequence, organism spelling, DOI linkage, and one MIC text value conflict across database surfaces.",
            },
        ],
        "qc_failure_reasons": qc_failure_reasons(),
        "rework_targets": [rework_target()],
        "unrecoverable_material_gaps": [unrecoverable_gap()],
        "validator_contract_ready": True,
        "semantic_gate_ready": False,
        "publication_grade_ready": False,
    }


def quality_feedback_payload() -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": STAMP,
        "issue_count": len(qc_failure_reasons()),
        "qc_failure_reasons": qc_failure_reasons(),
        "rework_context_packet_required": True,
        "rework_targets": [rework_target()],
        "unrecoverable_material_gaps": [unrecoverable_gap()],
        "source_review_response": {
            "responding_workers": ["worker-2", "worker-4", "worker-6"],
            "bounded_attempt_status": "completed_unrecoverable_material_gap",
            "publication_grade": False,
            "source_paths_checked": source_paths_checked(),
            "tools_attempted": tools_attempted(),
        },
    }


def analysis_status_payload() -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": STAMP,
        "status": "analysis_blocked_missing_primary_material",
        "activity_record_count": 0,
        "activity_extraction_issue_count": 1,
        "activity_extraction_issues": [
            "primary_muscin_source_not_locally_recovered",
        ],
        "mechanism_claim_count": 1,
        "database_record_status_summary": database_payload()["status_summary"],
        "open_rework_ticket_ids": ["rwk-20260505-170117-source-linkage-conflict"],
        "unrecoverable_material_gap_count": 1,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl_once(path: Path, row: dict[str, Any], key: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, Any]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                existing.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if any(item.get(key) == row.get(key) for item in existing):
        return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def run_gate(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def rerun_gates() -> dict[str, Any]:
    semantic_report = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    publication_report = REPORTS / f"{PAPER_ID}.publication_quality.json"
    semantic_code, semantic_stdout, semantic_stderr = run_gate(
        [
            sys.executable,
            ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py",
            "--root",
            ".",
            "--paper-id",
            PAPER_ID,
            "--json",
        ]
    )
    semantic_report.write_text(semantic_stdout, encoding="utf-8")
    publication_code, publication_stdout, publication_stderr = run_gate(
        [
            sys.executable,
            ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py",
            "--root",
            ".",
            "--manifest",
            str(MANIFEST),
            "--json-out",
            str(publication_report),
        ]
    )
    try:
        semantic = json.loads(semantic_stdout)
    except json.JSONDecodeError:
        semantic = {"parse_error": semantic_stderr, "stdout": semantic_stdout}
    try:
        publication = json.loads(publication_report.read_text(encoding="utf-8"))
    except Exception as exc:
        publication = {"parse_error": str(exc), "stdout": publication_stdout, "stderr": publication_stderr}
    return {
        "semantic_exit_code": semantic_code,
        "publication_exit_code": publication_code,
        "semantic_report": str(semantic_report.relative_to(ROOT)),
        "publication_report": str(publication_report.relative_to(ROOT)),
        "semantic_issue_codes": [
            issue.get("code")
            for result in semantic.get("results", [])
            for issue in result.get("issues", [])
            if isinstance(issue, dict)
        ],
        "publication_risk_counts": publication.get("risk_counts", {}),
        "publication_grade_pass": semantic.get("publication_grade_fail_count") == 0
        and publication.get("publication_grade_pass") is True,
    }


def rework_response(gates: dict[str, Any]) -> dict[str, Any]:
    return {
        "response_id": "rwk-response-20260505-170117-worker246",
        "ticket_id": "rwk-complete-test-0001",
        "paper_id": PAPER_ID,
        "created_at": STAMP,
        "responding_workers": ["worker-2", "worker-4", "worker-6"],
        "status": "bounded_attempt_completed_unrecoverable_gap_kept_open",
        "checked_source_paths": source_paths_checked(),
        "tools_attempted": tools_attempted(),
        "repairs_written": [
            "paper_packets/doi__10.1371_journal.pone.0110809/analysis/activity_toxicity_evidence.json",
            "paper_packets/doi__10.1371_journal.pone.0110809/analysis/database_record_audit.json",
            "paper_packets/doi__10.1371_journal.pone.0110809/analysis/adjudication_report.json",
            "papers/doi__10.1371_journal.pone.0110809/final/activity_toxicity_evidence.json",
            "papers/doi__10.1371_journal.pone.0110809/final/database_record_verification.json",
            "papers/doi__10.1371_journal.pone.0110809/final/mechanism_ontology_record.json",
            "papers/doi__10.1371_journal.pone.0110809/final/review_report.json",
            "papers/doi__10.1371_journal.pone.0110809/work/review/quality_feedback.json",
        ],
        "findings": [
            "Local primary assets for this DOI are the PLOS ONE GFR bioconversion article, not the Muscin AMP article.",
            "APD6/DBAASP/DRAMP Muscin rows are preserved as database-only/source-conflict evidence.",
            "No primary-source AMP activity/toxicity rows were recoverable from local material.",
            "Publication-grade acceptance remains blocked.",
        ],
        "unrecoverable_material_gaps": [unrecoverable_gap()],
        "remaining_rework_ticket_ids": ["rwk-20260505-170117-source-linkage-conflict"],
        "gate_results": gates,
    }


def main() -> int:
    activity = activity_payload()
    database = database_payload()
    mechanism = mechanism_payload()
    review = review_payload()
    quality = quality_feedback_payload()
    analysis_status = analysis_status_payload()

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

    append_jsonl_once(PACKET / "rework" / "rework_requests.jsonl", rework_target(), "ticket_id")
    gates = rerun_gates()
    append_jsonl_once(PACKET / "rework" / "rework_responses.jsonl", rework_response(gates), "response_id")
    print(json.dumps({"paper_id": PAPER_ID, "gates": gates}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
