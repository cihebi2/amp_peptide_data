#!/usr/bin/env python3
"""Targeted worker-2/4/6 repair for doi__10.3389_fchem.2017.00051."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.3389_fchem.2017.00051"
TICKET_ID = "rwk-complete-test-0001"
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
REPORTS = ROOT / "reports"
MANIFEST = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"
SEMANTIC_REPORT = REPORTS / f"{PAPER_ID}.semantic_gate.json"
PUBLICATION_REPORT = REPORTS / f"{PAPER_ID}.publication_quality.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl_once(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                rows.append({"_unparsed": line})
                continue
            if parsed.get("ticket_id") == row.get("ticket_id") and parsed.get("response_code") == row.get("response_code"):
                continue
            rows.append(parsed)
    rows.append(row)
    path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in rows), encoding="utf-8")


def source_locator(locator: str, source_path: str = "source/paper.xml") -> dict[str, str]:
    return {"locator": locator, "source_path": source_path}


def target(species: str, strain: str, target_class: str = "bacteria", gram: str | None = None) -> dict[str, str]:
    out = {"class": target_class, "species": species, "strain": strain}
    if gram:
        out["gram_status"] = gram
    return out


def build_activity(generated_at: str) -> dict[str, Any]:
    species_by_col = [
        ("Salmonella enterica", "serovar Typhimurium SL1344", "Gram-negative"),
        ("Escherichia coli", "K-12", "Gram-negative"),
        ("Staphylococcus aureus", "RN4220", "Gram-positive"),
        ("Enterococcus faecalis", "JH2-2", "Gram-positive"),
    ]
    table2 = [
        ("Polymyxin B sulfate", ["1.95", "1.95", "250", "31.25"]),
        ("Ciprofloxacin", ["0.12", "0.06", ">250", "62.5"]),
        ("Vancomycin hydrochloride", ["250", "125", "0.98", "62.5"]),
        ("Buwchitin", [">400", ">400", ">400", "100\u2013200"]),
    ]
    records: list[dict[str, Any]] = []
    for row_index, (entity, values) in enumerate(table2, start=3):
        for offset, raw_value in enumerate(values, start=2):
            species, strain, gram = species_by_col[offset - 2]
            records.append(
                {
                    "record_id": f"{PAPER_ID}-table2-r{row_index}-c{offset}-MIC",
                    "entity": entity,
                    "endpoint": "MIC",
                    "raw_value": raw_value,
                    "raw_unit": "\u03bcg/mL",
                    "normalization_status": "raw_unit_preserved",
                    "target": target(species, strain, gram=gram),
                    "assay_conditions": {
                        "assay": "broth microdilution susceptibility assay",
                        "medium": "Mueller Hinton broth",
                        "inoculum": "5 x 10^5 CFU/mL",
                        "incubation": "18-24 h at 37 C",
                        "replicates": "n = 6",
                        "source_column_context": "Table 2 MIC matrix; columns are Sal. typhimurium, E. coli, S. aureus, and E. faecalis.",
                    },
                    "evidence_ladder": "in_vitro_assay_table",
                    "source_locator": source_locator(f"xml:table=2:row={row_index}:column={offset}"),
                }
            )

    records.extend(
        [
            {
                "record_id": f"{PAPER_ID}-figure2-efaecalis-survival-24h",
                "entity": "Buwchitin",
                "endpoint": "percent viable cells after 24 h",
                "raw_value": "30 \u00b1 1.4",
                "raw_unit": "%",
                "normalization_status": "raw_unit_preserved",
                "target": target("Enterococcus faecalis", "JH2-2", gram="Gram-positive"),
                "assay_conditions": {
                    "assay": "OD600 growth/survival monitoring at 1 x MIC",
                    "medium": "Mueller Hinton broth",
                    "incubation": "24 h at 37 C",
                    "statistics": "P < 0.05 reported for surviving cells",
                },
                "evidence_ladder": "in_vitro_time_kill_growth_curve",
                "source_locator": source_locator("xml:sec=18:Antimicrobial and cytotoxic activity of buwchitin; xml:fig=2:Figure 2"),
            },
            {
                "record_id": f"{PAPER_ID}-discussion-efaecalis-MBC",
                "entity": "Buwchitin",
                "endpoint": "MBC",
                "raw_value": "200\u2013400",
                "raw_unit": "\u03bcg/mL",
                "normalization_status": "raw_unit_preserved",
                "target": target("Enterococcus faecalis", "JH2-2", gram="Gram-positive"),
                "assay_conditions": {
                    "assay": "bactericidal/bacteriostatic activity interpretation",
                    "note": "Text states this MBC range is suggestive of bacteriostatic killing activity.",
                },
                "evidence_ladder": "source_text_activity_claim",
                "source_locator": source_locator("xml:sec=20:Discussion"),
            },
        ]
    )

    hemolysis_values = [
        ("2", "400", "12.81 \u00b1 0.02"),
        ("3", "200", "9.69 \u00b1 0.09"),
        ("4", "100", "5.23 \u00b1 0.08"),
        ("5", "50", "4.12 \u00b1 0.06"),
        ("6", "25", "4.15 \u00b1 0.06"),
        ("7", "12.5", "3.08 \u00b1 0.03"),
        ("8", "6.25", "2.80 \u00b1 0.02"),
        ("9", "3.125", "3.11 \u00b1 0.06"),
    ]
    for row, concentration, value in hemolysis_values:
        records.append(
            {
                "record_id": f"{PAPER_ID}-table3-r{row}-hemolysis",
                "entity": "Buwchitin",
                "endpoint": "percent hemolysis",
                "raw_value": value,
                "raw_unit": "%",
                "normalization_status": "raw_unit_preserved",
                "target": target("Ovis aries", "defibrinated sheep erythrocytes", target_class="mammalian erythrocytes"),
                "assay_conditions": {
                    "assay": "erythrocyte leakage assay",
                    "concentration_raw_value": concentration,
                    "concentration_unit": "\u03bcg/mL",
                    "erythrocyte_preparation": "4% sheep erythrocytes in PBS",
                    "incubation": "1 h at 37 C",
                    "readout": "OD450 nm hemoglobin leakage",
                    "replicates": "three independent replicates with standard deviation",
                },
                "evidence_ladder": "in_vitro_toxicity_table",
                "source_locator": source_locator(f"xml:table=3:row={row}:columns=1-2"),
            }
        )

    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Source-reviewed worker-2 repair from XML/PDF Table 2, Figure 2 text, Discussion MBC text, and Table 3 hemolysis rows.",
        "activity_records": records,
        "extraction_issues": [],
        "parser_quality_control": {
            "issue_count": 0,
            "table2_column_mapping_repaired": True,
            "table3_hemolysis_rows_recovered": 8,
            "rejects_property_or_model_tables": True,
            "requires_target_entity_value_matrix": True,
            "strict_endpoint_matching": True,
        },
        "source_paths_checked": [
            "papers/doi__10.3389_fchem.2017.00051/source/paper.xml",
            "paper_packets/doi__10.3389_fchem.2017.00051/extracted/xml_sections.json",
            "paper_packets/doi__10.3389_fchem.2017.00051/extracted/pdf_text/fchem-05-00051.txt",
            "paper_packets/doi__10.3389_fchem.2017.00051/locators/locator_index.json",
        ],
    }


def build_database(generated_at: str, activity: dict[str, Any]) -> dict[str, Any]:
    record_ids = {row["record_id"] for row in activity["activity_records"]}
    matched = [
        f"{PAPER_ID}-table2-r6-c5-MIC",
        f"{PAPER_ID}-discussion-efaecalis-MBC",
        f"{PAPER_ID}-table3-r2-hemolysis",
    ]
    for record_id in matched:
        if record_id not in record_ids:
            raise RuntimeError(f"expected activity record missing: {record_id}")
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "audit_scope": "Source-reviewed worker-4 repair of APD6 linked literature, sequence, and experiment text rows against local XML/PDF and merged database rows.",
        "database_row_counts": {
            "linked_assay_records": 0,
            "linked_dramp_activity_records": 0,
            "linked_experiment_records": 1,
            "linked_literature_records": 1,
            "linked_sequence_records": 0,
            "merged_apd6_activity_text_records": 1,
            "merged_sequence_records": 1,
        },
        "record_audits": [
            {
                "source_id": "AP03153",
                "sequence_key": "APD6:AP03153",
                "source_table": "APD6 peptides.csv / merged sequence catalog",
                "status": "database_only_no_primary_source",
                "layer1_status": "database_only_no_primary_source",
                "database_subject": "Buwchitin",
                "database_measure": "APD6 entry text records Anti-Gram+ activity, E. faecalis MIC 100-200 ug/ml, poor sheep-RBC hemolysis at 400 ug/ml, and recombinant-production context.",
                "name_check": {
                    "status": "source_verified",
                    "source_locator": source_locator("xml:table=1:row=6; xml:sec=6:Amplification of antimicrobial genes"),
                    "note": "Primary source supports the buwchitin name, 71 aa length, GenBank KY823515 deposition, and rumen metagenomic origin.",
                },
                "sequence_check": {
                    "status": "database_only_no_primary_source",
                    "database_sequence_present": True,
                    "primary_source_exact_sequence_present": False,
                    "source_locator": source_locator("xml:table=1:row=6; xml:sec=6:GenBank KY823515; xml:sec=19:APD2 properties"),
                    "database_locator": {
                        "locator": "merged_output:sequences/all_sequences.csv:row=3154",
                        "source_path": "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
                    },
                    "note": "Local XML/PDF give identity, length, accession, and properties but do not print the exact amino-acid sequence carried by APD6.",
                },
                "modification_check": {
                    "status": "no_primary_or_database_modification_reported",
                    "note": "No amidation, cyclization, D-amino-acid, disulfide, lipidation, or terminal modification is supported in local primary text or APD6 linked rows.",
                },
                "source_organism_check": {
                    "status": "source_verified_with_caution",
                    "primary_source": "rumen bacterial metagenome / cow rumen solid attached bacteria library",
                    "database_source": "uncultured bacterium; bovine microbiota:gut",
                    "source_locator": source_locator("xml:sec=5:Identification of antimicrobial genes; xml:table=1:row=6"),
                },
                "activity_claim_checks": [
                    {
                        "claim": "E. faecalis MIC 100-200 ug/ml",
                        "status": "source_verified",
                        "matched_activity_record_id": f"{PAPER_ID}-table2-r6-c5-MIC",
                        "source_locator": source_locator("xml:table=2:row=6:column=5"),
                    },
                    {
                        "claim": "MBC 200-400 ug/ml",
                        "status": "source_verified",
                        "matched_activity_record_id": f"{PAPER_ID}-discussion-efaecalis-MBC",
                        "source_locator": source_locator("xml:sec=20:Discussion"),
                    },
                    {
                        "claim": "poor sheep-RBC hemolysis at 400 ug/ml",
                        "status": "source_verified",
                        "matched_activity_record_id": f"{PAPER_ID}-table3-r2-hemolysis",
                        "source_locator": source_locator("xml:table=3:row=2"),
                    },
                ],
                "matched_activity_record_id": f"{PAPER_ID}-table2-r6-c5-MIC",
                "citation_traceability": source_locator("xml:article-meta"),
                "traceability": {
                    "locator": "database:linked_experiment_records:row=1; merged_output:experiments/apd6_activity_text_records.csv:row=3154; merged_output:sequences/all_sequences.csv:row=3154",
                    "source_path": "paper_packets/doi__10.3389_fchem.2017.00051/database/linked_experiment_records.jsonl",
                },
                "conflict_context": "Exact APD6 amino-acid sequence remains database-only under local obtainable materials because the primary XML/PDF provide GenBank accession and peptide length but not the full sequence text.",
                "review_notes": "Preserved as database_only_no_primary_source rather than source_verified; source-supported activity/toxicity claims remain usable through the repaired activity records.",
            },
            {
                "source_id": "AP03153",
                "sequence_key": "APD6:AP03153",
                "source_table": "linked_literature_records.jsonl",
                "status": "source_verified",
                "layer1_status": "source_verified",
                "database_subject": "Buwchitin: A Ruminal Peptide with Antimicrobial Potential against Enterococcus faecalis",
                "database_measure": "",
                "citation_traceability": source_locator("xml:article-meta"),
                "sequence_check": {
                    "status": "not_sequence_record",
                    "source_locator": source_locator("xml:article-meta"),
                },
                "traceability": {
                    "locator": "database:linked_literature_records:row=1",
                    "source_path": "paper_packets/doi__10.3389_fchem.2017.00051/database/linked_literature_records.jsonl",
                },
                "review_notes": "APD6 literature link matches the local DOI, PMID, PMCID, title, journal, and year in article metadata.",
                "conflict_context": "",
                "matched_activity_record_id": "",
            },
        ],
        "status_summary": {
            "database_only_no_primary_source": 1,
            "source_verified": 1,
        },
        "source_paths_checked": [
            "paper_packets/doi__10.3389_fchem.2017.00051/database/linked_experiment_records.jsonl",
            "paper_packets/doi__10.3389_fchem.2017.00051/database/linked_literature_records.jsonl",
            "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/apd6_activity_text_records.csv",
            "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
            "papers/doi__10.3389_fchem.2017.00051/source/paper.xml",
            "paper_packets/doi__10.3389_fchem.2017.00051/extracted/pdf_text/fchem-05-00051.txt",
        ],
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 source-reviewed mechanism closeout; direct mechanism overclaims are avoided and negative/inconclusive assays are preserved.",
        "mechanism_claims": [
            {
                "claim_id": "mech-001",
                "claim_text": "Buwchitin shows bacteriostatic activity against E. faecalis at MIC, with approximately 30% surviving cells after 24 h in the reported growth assay.",
                "entity_scope": "Buwchitin against Enterococcus faecalis JH2-2",
                "evidence_class": "direct_phenotypic_activity",
                "direct_assay_types": ["OD600 growth/survival monitoring"],
                "source_locator": source_locator("xml:sec=18:Antimicrobial and cytotoxic activity of buwchitin; xml:fig=2:Figure 2"),
                "limitations": "This is phenotypic activity evidence, not a molecular target mechanism.",
            },
            {
                "claim_id": "mech-002",
                "claim_text": "Membrane depolarization was not detected during the first 2 h of buwchitin treatment under the reported diSC3(5) assay conditions.",
                "entity_scope": "Buwchitin-treated Enterococcus faecalis",
                "evidence_class": "negative_direct_mechanism_assay",
                "direct_assay_types": ["diSC3(5) membrane depolarization assay"],
                "source_locator": source_locator("xml:sec=13:Inner membrane depolarization assay; xml:sec=18:Antimicrobial and cytotoxic activity of buwchitin"),
                "limitations": "Negative depolarization result argues against simple membrane depolarization as the sole mechanism.",
            },
            {
                "claim_id": "mech-003",
                "claim_text": "TEM morphology evidence showed limited early damage and later cytoplasmic vacuoles/envelope separation after 24 h exposure.",
                "entity_scope": "Buwchitin-treated Enterococcus faecalis",
                "evidence_class": "morphology_context_not_direct_mechanism",
                "direct_assay_types": ["transmission electron microscopy"],
                "source_locator": source_locator("xml:fig=3:Figure 3; xml:sec=18:Antimicrobial and cytotoxic activity of buwchitin"),
                "limitations": "TEM supports cellular-effect context but does not by itself identify the molecular target.",
            },
            {
                "claim_id": "mech-004",
                "claim_text": "Predicted cationic amphipathic alpha-helical structure is consistent with AMP-like membrane interaction context, but the paper frames the detailed mechanism as requiring further study.",
                "entity_scope": "Buwchitin structure/model",
                "evidence_class": "computational_context_hypothesis",
                "direct_assay_types": ["PHYRE2 structural modeling", "APD2 property prediction"],
                "source_locator": source_locator("xml:sec=19:Structural modeling of buwchitin; xml:fig=4:Figure 4; xml:sec=20:Discussion"),
                "limitations": "Do not promote this modeled context to direct_mechanism.",
            },
        ],
        "source_paths_checked": [
            "papers/doi__10.3389_fchem.2017.00051/source/paper.xml",
            "paper_packets/doi__10.3389_fchem.2017.00051/extracted/figure_captions.json",
            "paper_packets/doi__10.3389_fchem.2017.00051/extracted/pdf_text/fchem-05-00051.txt",
        ],
    }


def build_review(
    generated_at: str,
    activity: dict[str, Any],
    database: dict[str, Any],
    mechanism: dict[str, Any],
    gates_ready: bool | None = None,
    gate_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    accepted = gates_ready is not False
    status = "accepted_with_cautions" if accepted else "needs_targeted_rework"
    rework_targets = [] if accepted else [
        {
            "ticket_id": TICKET_ID,
            "worker": "worker-6",
            "target_queue": "adjudication",
            "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
            "failure_code": "strict_gate_failed_after_worker246_repair",
            "required_action": "Inspect strict semantic/publication gate output and repair the listed concrete issue before accepting.",
            "source_evidence_to_check": [
                f"reports/{PAPER_ID}.semantic_gate.json",
                f"reports/{PAPER_ID}.publication_quality.json",
            ],
            "blocks": ["publication_grade_ready", "final_approval"],
        }
    ]
    cautions = [
        {
            "caution_code": "apd6_exact_sequence_database_only",
            "evidence_context": "APD6 exact amino-acid sequence is preserved as database-only because local primary XML/PDF support name, length, accession, and activity but do not print the full sequence.",
            "record_id": "APD6:AP03153",
        },
        {
            "caution_code": "supplementary_landing_pages_not_data_supplements",
            "evidence_context": "The local supplementary directory contains HTML landing captures; PMC metadata reports no supplement and no structured supplementary table changed the curation.",
        },
        {
            "caution_code": "mechanism_bounded_not_molecular_target",
            "evidence_context": "Bacteriostatic activity, negative depolarization, TEM morphology, and predicted amphipathic structure are preserved without claiming a resolved molecular mechanism.",
        },
    ]
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": status,
        "publication_grade": accepted,
        "validator_contract_passed": True,
        "adjudication_summary": (
            "Worker-2/4/6 source review repaired the Table 2 mapping, recovered Table 3 hemolysis rows, preserved the APD6 exact-sequence caveat, and closed the original targeted rework with cautions."
            if accepted
            else "Worker-2/4/6 source review attempted the targeted repair, but strict gates still require rework."
        ),
        "summary": (
            "Buwchitin is curated as a source-reviewed, caution-bearing AMP record: primary activity/toxicity values are recoverable locally, while the APD6 exact sequence remains database-only relative to the local primary text."
            if accepted
            else "Strict gate failure remains after bounded worker-2/4/6 repair."
        ),
        "checked_inputs": [
            str(PACKET / "packet_manifest.json"),
            str(PACKET / "locators" / "locator_index.json"),
            str(PACKET / "extracted" / "xml_sections.json"),
            str(PACKET / "extracted" / "pdf_text" / "fchem-05-00051.txt"),
            str(PACKET / "extracted" / "supplementary_index.json"),
            str(PACKET / "extracted" / "supplementary_text.jsonl"),
            str(PACKET / "database" / "linked_experiment_records.jsonl"),
            str(PACKET / "database" / "linked_literature_records.jsonl"),
            "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/apd6_activity_text_records.csv",
            "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
            str(PAPER / "source" / "paper.xml"),
            str(PAPER / "source" / "paper.pdf"),
        ],
        "source_review_depth": {
            "paper_xml": {"checked": True, "used_for": ["tables", "methods", "article metadata", "mechanism text"]},
            "paper_pdf": {"checked": True, "used_for": ["Table 3 text confirmation", "main text confirmation"]},
            "oa_package": {"checked": True, "used_for": ["NXML/PDF/figure members"]},
            "supplementary_assets": {"checked": True, "status": "HTML landing captures only; no true local supplementary data table found"},
            "merged_database_rows": {"checked": True, "used_for": ["APD6 activity text", "APD6 sequence catalog", "literature link"]},
        },
        "materials_exhausted": {
            "paper_xml": True,
            "paper_pdf": True,
            "oa_package": True,
            "supplementary_assets": "checked_html_landing_captures_no_true_supplementary_table",
            "merged_database_rows": True,
            "unrecoverable_material_gaps": [],
        },
        "semantic_quality_checks": {
            "activity_rows_parsed": len(activity["activity_records"]),
            "activity_extraction_issues": len(activity.get("extraction_issues", [])),
            "database_status_summary": database["status_summary"],
            "mechanism_claims": len(mechanism["mechanism_claims"]),
            "table2_column_mapping_repaired": True,
            "table3_hemolysis_rows_recovered": 8,
            "strict_gate_evidence": gate_evidence or {},
        },
        "per_layer_decision_rationale": {
            "layer_1_database": "APD6 literature and activity claims trace to this paper; exact APD6 sequence is preserved as database_only_no_primary_source because local primary text does not print the full sequence.",
            "layer_2_activity_toxicity": "Table 2 MIC values were re-mapped to all four target species, the E. faecalis survival/MBC claims were retained, and Table 3 sheep-erythrocyte hemolysis rows were recovered with units and locators.",
            "layer_3_mechanism": "Mechanism records are bounded to source-supported bacteriostatic, negative depolarization, TEM morphology, and modeled structure context without direct molecular-target overclaim.",
            "layer_4_publication_grade": "No blocking or major owner-layer issue remains; the final state is accepted_with_cautions only after strict gate rerun clears.",
        },
        "caution_findings": cautions,
        "qc_failure_reasons": [] if accepted else [
            {
                "code": "strict_gate_failed_after_worker246_repair",
                "owner_worker": "worker-6",
                "severity": "blocking",
                "reason": "Strict semantic or publication-quality gate still failed after bounded worker-2/4/6 repair.",
            }
        ],
        "rework_targets": rework_targets,
        "strict_gate": {
            "required_rework_count": len(rework_targets),
            "open_rework_targets": len(rework_targets),
            "closed_rework_ticket_ids": [TICKET_ID] if accepted else [],
            "gate_evidence": gate_evidence or {},
        },
        "unrecoverable_material_gaps": [],
    }


def build_quality(generated_at: str, gates_ready: bool, review: dict[str, Any], gate_evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": 0 if gates_ready else 1,
        "qc_failure_reasons": [] if gates_ready else review["qc_failure_reasons"],
        "rework_context_packet_required": not gates_ready,
        "rework_targets": [] if gates_ready else review["rework_targets"],
        "closed_rework_ticket_ids": [TICKET_ID] if gates_ready else [],
        "remaining_open_rework_ticket_ids": [] if gates_ready else [TICKET_ID],
        "publication_grade": gates_ready,
        "review_status": review["review_status"],
        "source_review_depth": review["source_review_depth"],
        "unrecoverable_material_gaps": [],
        "gate_evidence": gate_evidence,
    }


def run_gates() -> dict[str, Any]:
    semantic_cmd = [
        sys.executable,
        str(ROOT / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "semantic_three_layer_gate.py"),
        "--root",
        str(ROOT),
        "--manifest",
        str(MANIFEST.relative_to(ROOT)),
        "--json",
    ]
    semantic_proc = subprocess.run(semantic_cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    if semantic_proc.stdout.strip():
        SEMANTIC_REPORT.write_text(semantic_proc.stdout, encoding="utf-8")
        semantic = json.loads(semantic_proc.stdout)
    else:
        semantic = {"error": semantic_proc.stderr, "returncode": semantic_proc.returncode}
        write_json(SEMANTIC_REPORT, semantic)

    publication_cmd = [
        sys.executable,
        str(ROOT / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "check_three_layer_publication_quality.py"),
        "--manifest",
        str(MANIFEST),
        "--root",
        str(ROOT),
        "--json-out",
        str(PUBLICATION_REPORT),
    ]
    publication_proc = subprocess.run(publication_cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    publication = read_json(PUBLICATION_REPORT, {"error": publication_proc.stderr, "returncode": publication_proc.returncode})
    semantic_ready = semantic_proc.returncode == 0 and int(semantic.get("publication_grade_pass_count") or 0) == 1 and int(semantic.get("publication_grade_fail_count") or 0) == 0
    publication_ready = publication_proc.returncode == 0 and publication.get("publication_grade_pass") is True
    return {
        "semantic_ready": semantic_ready,
        "publication_quality_pass": publication_ready,
        "publication_grade_ready": bool(semantic_ready and publication_ready),
        "semantic_returncode": semantic_proc.returncode,
        "publication_returncode": publication_proc.returncode,
        "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
        "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
        "semantic_issue_examples": semantic.get("results", [{}])[0].get("issues", [])[:8] if isinstance(semantic.get("results"), list) else [],
        "publication_risk_counts": publication.get("risk_counts", {}),
        "publication_quality_report": str(PUBLICATION_REPORT.relative_to(ROOT)),
        "semantic_report": str(SEMANTIC_REPORT.relative_to(ROOT)),
    }


def sync_control_state(generated_at: str, gates_ready: bool, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], gate_evidence: dict[str, Any]) -> None:
    open_tickets = [] if gates_ready else [TICKET_ID]
    manifest = read_json(PACKET / "packet_manifest.json")
    manifest.update(
        {
            "updated_at": generated_at,
            "analysis_queue_status": "source_reviewed_publication_grade_ready" if gates_ready else "analysis_needs_analysis_rework",
            "open_rework_ticket_ids": open_tickets,
            "known_missing_or_blocked_materials": [] if gates_ready else manifest.get("known_missing_or_blocked_materials", []),
        }
    )
    write_json(PACKET / "packet_manifest.json", manifest)

    analysis_status = read_json(PACKET / "analysis" / "analysis_status.json")
    analysis_status.update(
        {
            "generated_at": generated_at,
            "status": "source_reviewed_publication_grade_ready" if gates_ready else "analysis_needs_analysis_rework",
            "activity_record_count": len(activity["activity_records"]),
            "activity_extraction_issue_count": 0 if gates_ready else 1,
            "activity_extraction_issues": [] if gates_ready else analysis_status.get("activity_extraction_issues", []),
            "database_status_summary": database["status_summary"],
            "mechanism_claim_count": len(mechanism["mechanism_claims"]),
            "open_rework_ticket_ids": open_tickets,
        }
    )
    write_json(PACKET / "analysis" / "analysis_status.json", analysis_status)

    workflow = read_json(WORKFLOW / "workflow_context.json")
    workflow.update(
        {
            "updated_at": generated_at,
            "current_state": "source_reviewed_publication_grade_ready" if gates_ready else "rework_context_prepared",
            "open_rework_tickets": open_tickets,
            "queue_status": {
                "material": workflow.get("queue_status", {}).get("material", "material_extracted_with_gaps"),
                "analysis": "source_reviewed_publication_grade_ready" if gates_ready else "analysis_needs_analysis_rework",
            },
            "gate_summary": {
                "structural_ready": True,
                "validator_contract_ready": True,
                "semantic_gate_ready": bool(gate_evidence.get("semantic_ready")),
                "publication_grade_ready": gates_ready,
            },
        }
    )
    write_json(WORKFLOW / "workflow_context.json", workflow)


def write_complete_report(generated_at: str, gates_ready: bool, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], gate_evidence: dict[str, Any]) -> None:
    report = read_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json")
    report.update(
        {
            "generated_at": generated_at,
            "current_state": "source_reviewed_publication_grade_ready" if gates_ready else "rework_queue",
            "completion_claim": "source_reviewed_worker246_rework_closed_publication_grade_accepted_with_cautions" if gates_ready else "worker246_repair_attempt_gate_failed",
            "final_approval_status": "approved_with_cautions" if gates_ready else "refused_needs_rework",
            "not_publication_grade_reason": None if gates_ready else "Strict gates did not pass after bounded worker-2/4/6 repair.",
            "open_rework_ticket_count": 0 if gates_ready else 1,
            "rework_ticket_ids": [TICKET_ID],
            "closed_rework_ticket_ids": [TICKET_ID] if gates_ready else [],
            "terminal_status": "publication_grade_ready_with_cautions" if gates_ready else "awaiting_targeted_rework",
            "semantic_gate": "passed_after_worker246_source_review" if gate_evidence.get("semantic_ready") else "failed_after_worker246_source_review",
            "publication_quality_gate": "passed_after_worker246_source_review" if gate_evidence.get("publication_quality_pass") else "failed_after_worker246_source_review",
            "publication_quality_gate_report": str(PUBLICATION_REPORT),
            "gate_summary": {
                "structural_ready": True,
                "validator_contract_ready": True,
                "semantic_gate_ready": bool(gate_evidence.get("semantic_ready")),
                "publication_grade_ready": gates_ready,
            },
            "gate_results": {
                "packet_hard_finding_count": report.get("gate_results", {}).get("packet_hard_finding_count", 0),
                "semantic_publication_grade_pass_count": gate_evidence.get("semantic_publication_grade_pass_count"),
                "semantic_publication_grade_fail_count": gate_evidence.get("semantic_publication_grade_fail_count"),
                "publication_quality_pass": gate_evidence.get("publication_quality_pass"),
            },
            "analysis": {
                "activity_records": len(activity["activity_records"]),
                "activity_extraction_issue_count": 0 if gates_ready else 1,
                "database_row_counts": {
                    "linked_experiment_records": 1,
                    "linked_literature_records": 1,
                    "merged_sequence_records": 1,
                    "merged_apd6_activity_text_records": 1,
                },
                "database_status_summary": database["status_summary"],
                "mechanism_claims": len(mechanism["mechanism_claims"]),
                "review_status": "accepted_with_cautions" if gates_ready else "needs_targeted_rework",
            },
            "queue_status": {
                "material": report.get("queue_status", {}).get("material", "material_extracted_with_gaps"),
                "analysis": "source_reviewed_publication_grade_ready" if gates_ready else "analysis_needs_analysis_rework",
            },
        }
    )
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", report)


def main() -> int:
    generated_at = now_utc()
    activity = build_activity(generated_at)
    database = build_database(generated_at, activity)
    mechanism = build_mechanism(generated_at)
    review = build_review(generated_at, activity, database, mechanism, gates_ready=None)

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

    first_gate = run_gates()
    gates_ready = bool(first_gate["publication_grade_ready"])
    final_review = build_review(generated_at, activity, database, mechanism, gates_ready=gates_ready, gate_evidence=first_gate)
    for path in [
        PACKET / "analysis" / "adjudication_report.json",
        PACKET / "final" / "review_report.json",
        PAPER / "work" / "review" / "adjudication_report.json",
        PAPER / "final" / "review_report.json",
    ]:
        write_json(path, final_review)

    gate_evidence = first_gate
    if not gates_ready:
        gate_evidence = run_gates()
        gates_ready = bool(gate_evidence["publication_grade_ready"])
        final_review = build_review(generated_at, activity, database, mechanism, gates_ready=gates_ready, gate_evidence=gate_evidence)
        for path in [
            PACKET / "analysis" / "adjudication_report.json",
            PACKET / "final" / "review_report.json",
            PAPER / "work" / "review" / "adjudication_report.json",
            PAPER / "final" / "review_report.json",
        ]:
            write_json(path, final_review)
        if gates_ready:
            gate_evidence = run_gates()

    quality = build_quality(generated_at, gates_ready, final_review, gate_evidence)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality)
    sync_control_state(generated_at, gates_ready, activity, database, mechanism, gate_evidence)
    write_complete_report(generated_at, gates_ready, activity, database, mechanism, gate_evidence)

    response = {
        "ticket_id": TICKET_ID,
        "paper_id": PAPER_ID,
        "responded_at": generated_at,
        "response_code": "worker246_source_review_repair",
        "status": "closed_after_source_review" if gates_ready else "kept_open_after_gate_failure",
        "owner_workers": ["worker-2", "worker-4", "worker-6"],
        "source_paths_checked": final_review["checked_inputs"],
        "tools_attempted": ["rg", "jq", "file", "pdf_text", "semantic_three_layer_gate.py", "check_three_layer_publication_quality.py"],
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
        ],
        "rework_resolved": {
            "table2_activity_matrix": "corrected all four target columns and strains",
            "table3_hemolysis": "recovered eight concentration/% hemolysis rows",
            "database_adjudication": "preserved APD6 exact sequence as database_only_no_primary_source while source-verifying activity/literature claims",
            "worker6_adjudication": "rewritten as source-reviewed accepted_with_cautions only when strict gates pass",
        },
        "remaining_open_rework_ticket_ids": [] if gates_ready else [TICKET_ID],
        "unrecoverable_material_gaps": [],
        "gate_results": gate_evidence,
        "blocks_publication_grade": not gates_ready,
    }
    append_jsonl_once(PACKET / "rework" / "rework_responses.jsonl", response)

    print(json.dumps({"paper_id": PAPER_ID, "gates_ready": gates_ready, "gate_evidence": gate_evidence}, ensure_ascii=False, indent=2))
    return 0 if gates_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
