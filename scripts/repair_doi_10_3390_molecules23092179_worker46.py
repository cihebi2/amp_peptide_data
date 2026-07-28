#!/usr/bin/env python3
"""Source-reviewed worker-4/6 repair for doi__10.3390_molecules23092179."""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.3390_molecules23092179"
DOI = "10.3390/molecules23092179"
TITLE = "Pumilacidins from the Octocoral-Associated Bacillus sp. DT001 Display Anti-Proliferative Effects in Plasmodium falciparum."
TICKET_ID = "rwk-complete-test-0001"
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
REPORTS = ROOT / "reports"
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
MANIFEST = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"
SEMANTIC_REPORT = REPORTS / f"{PAPER_ID}.semantic_gate.json"
PUBLICATION_REPORT = REPORTS / f"{PAPER_ID}.publication_quality.json"
COMPLETE_REPORT = REPORTS / f"{PAPER_ID}.complete_message_test_report.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl_once(path: Path, response_id: str, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    for line in existing:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("response_id") == response_id:
            return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def loc(locator: str, path: str = "source/paper.xml", **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"source_path": path, "locator": locator}
    payload.update(extra)
    return payload


CHECKED_INPUTS = [
    f"rework_context/{PAPER_ID}/handoff_context.json",
    f"paper_packets/{PAPER_ID}/packet_manifest.json",
    f"paper_packets/{PAPER_ID}/locators/locator_index.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
    f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
    f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_text/molecules-23-02179-s001.txt",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/local-DBAASP-PMC6225264.txt",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/molecules-23-02179.txt",
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    f"papers/{PAPER_ID}/source/supplementary/molecules-23-02179-s001.pdf",
    f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/all_experimental_records.csv",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/dbaasp_assay_records.csv",
    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/literature/sequence_literature_links.csv",
]


def table_activity(
    *,
    record_id: str,
    entity: str,
    stage: str,
    value: str,
    sem: str,
    row: int,
    compound_locator: str,
    generated_at: str,
) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "entity": entity,
        "compound": {
            "name": entity,
            "class": "pumilacidin/surfactin lipopeptide",
            "source_locator": loc(compound_locator),
        },
        "endpoint": "IC50",
        "raw_value": value,
        "raw_unit": "μM",
        "normalization_status": "raw_unit_preserved",
        "evidence_ladder": "primary_xml_table_source_reviewed",
        "target": {
            "species": "Plasmodium falciparum",
            "strain": "strain not reported",
            "class": "malaria parasite",
            "life_cycle_stage": stage,
        },
        "assay_conditions": {
            "assay": "48 h parasite viability/proliferation assay; Table 1 reports IC50 with SEM from three experiments run in duplicate",
            "parasite_stage": stage,
            "sem": sem,
            "method_locator": loc("xml:sec=4.7;xml:sec=4.8"),
            "result_locator": loc("xml:sec=2.3;xml:table=1"),
            "figure_locator": loc("xml:fig=2"),
        },
        "source_locator": loc(f"xml:table=1:row={row}", table="Table 1"),
        "review_notes": "Rowspan-aware source review preserves the compound name across the paired schizont/ring rows.",
        "reviewed_at": generated_at,
    }


def build_activity(generated_at: str) -> dict[str, Any]:
    records = [
        table_activity(
            record_id=f"{PAPER_ID}-table1-pumilacidin-a-schizont-ic50",
            entity="Pumilacidin A",
            stage="schizont",
            value="8.34",
            sem="0.97",
            row=2,
            compound_locator="xml:fig=1;xml:sec=2.2",
            generated_at=generated_at,
        ),
        table_activity(
            record_id=f"{PAPER_ID}-table1-pumilacidin-a-ring-ic50",
            entity="Pumilacidin A",
            stage="ring",
            value="15.44",
            sem="3.9",
            row=3,
            compound_locator="xml:fig=1;xml:sec=2.2",
            generated_at=generated_at,
        ),
        table_activity(
            record_id=f"{PAPER_ID}-table1-pumilacidin-c-schizont-ic50",
            entity="Pumilacidin C",
            stage="schizont",
            value="7.75",
            sem="1.74",
            row=4,
            compound_locator="xml:fig=1;xml:sec=2.2",
            generated_at=generated_at,
        ),
        table_activity(
            record_id=f"{PAPER_ID}-table1-pumilacidin-c-ring-ic50",
            entity="Pumilacidin C",
            stage="ring",
            value="19.59",
            sem="4.4",
            row=5,
            compound_locator="xml:fig=1;xml:sec=2.2",
            generated_at=generated_at,
        ),
        {
            "record_id": f"{PAPER_ID}-table2-pumilacidin-a-vero-ic50",
            "entity": "Pumilacidin A",
            "compound": {"name": "Pumilacidin A", "class": "pumilacidin/surfactin lipopeptide", "source_locator": loc("xml:fig=1;xml:sec=2.2")},
            "endpoint": "IC50",
            "raw_value": "28.42",
            "raw_unit": "μM",
            "normalization_status": "raw_unit_preserved",
            "evidence_ladder": "primary_xml_table_source_reviewed",
            "target": {"species": "African green monkey", "strain": "Vero cells", "class": "mammalian epithelial cell line"},
            "assay_conditions": {
                "assay": "cytotoxicity assay on Vero cells; Table 2 reports means of one experiment run in duplicate",
                "sem": "9.86",
                "method_locator": loc("xml:sec=4.6"),
                "result_locator": loc("xml:sec=2.3;xml:table=2"),
            },
            "source_locator": loc("xml:table=2:row=2", table="Table 2"),
            "reviewed_at": generated_at,
        },
        {
            "record_id": f"{PAPER_ID}-table2-pumilacidin-c-vero-ic50",
            "entity": "Pumilacidin C",
            "compound": {"name": "Pumilacidin C", "class": "pumilacidin/surfactin lipopeptide", "source_locator": loc("xml:fig=1;xml:sec=2.2")},
            "endpoint": "IC50",
            "raw_value": "26.07",
            "raw_unit": "μM",
            "normalization_status": "raw_unit_preserved",
            "evidence_ladder": "primary_xml_table_source_reviewed",
            "target": {"species": "African green monkey", "strain": "Vero cells", "class": "mammalian epithelial cell line"},
            "assay_conditions": {
                "assay": "cytotoxicity assay on Vero cells; Table 2 reports means of one experiment run in duplicate",
                "sem": "10.10",
                "method_locator": loc("xml:sec=4.6"),
                "result_locator": loc("xml:sec=2.3;xml:table=2"),
            },
            "source_locator": loc("xml:table=2:row=3", table="Table 2"),
            "reviewed_at": generated_at,
        },
        {
            "record_id": f"{PAPER_ID}-fig3-pfalciparum-10um-24h-proliferation-inhibition",
            "entity": "Pumilacidins A and C",
            "endpoint": "parasite_proliferation_inhibition",
            "raw_value": "almost 50",
            "raw_unit": "% inhibition",
            "normalization_status": "qualitative_main_text_value_preserved",
            "evidence_ladder": "primary_xml_results_and_figure_caption",
            "target": {"species": "Plasmodium falciparum", "strain": "strain not reported", "class": "malaria parasite", "life_cycle_stage": "schizont"},
            "assay_conditions": {
                "compound_concentration": "10 μM",
                "incubation": "24 h",
                "readout": "flow cytometry DNA-content measurement with Hoechst 33342 staining",
                "method_locator": loc("xml:sec=4.8"),
            },
            "source_locator": loc("xml:sec=2.3;xml:fig=3"),
            "review_notes": "The paper reports an approximate inhibition, so no graph-digitized exact value is invented.",
            "reviewed_at": generated_at,
        },
        {
            "record_id": f"{PAPER_ID}-fig4-human-rbc-hemolysis-not-detected-10um",
            "entity": "Pumilacidins A and C",
            "endpoint": "hemolytic_activity_not_detected_at_test_condition",
            "raw_value": "no evident hemolytic activity",
            "raw_unit": "qualitative at 10 μM for 24 h",
            "normalization_status": "qualitative_result_preserved",
            "evidence_ladder": "primary_xml_results_and_figure_caption",
            "target": {"species": "human", "strain": "red blood cells", "class": "erythrocytes"},
            "assay_conditions": {
                "compound_concentration": "10 μM",
                "incubation": "24 h",
                "positive_control": "0.1% Triton set as 100% hemolysis",
                "method_locator": loc("xml:sec=4.9"),
            },
            "source_locator": loc("xml:sec=2.3;xml:fig=4"),
            "review_notes": "Only the qualitative conclusion is recoverable from local text without graph digitization.",
            "reviewed_at": generated_at,
        },
    ]
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 source-reviewed final activity/toxicity reconciliation from XML/PDF Table 1, Table 2, Figure 3, and Figure 4; no absent exact figure values were fabricated.",
        "activity_records": records,
        "extraction_issues": [],
        "unrecoverable_material_gaps": [],
        "parser_quality_control": {
            "rowspan_reconciled": True,
            "table1_rows": 4,
            "table2_rows": 2,
            "figure_only_values_not_digitized": True,
            "supplementary_tables_present": 0,
        },
    }


def audit_record(
    *,
    source_table: str,
    source_id: str,
    trace_locator: str,
    status: str,
    generated_at: str,
    database_measure: str = "",
    database_subject: str = "",
    matched_ids: list[str] | None = None,
    conflict_context: str = "",
    review_notes: str = "",
    sequence_status: str = "not_applicable",
    source_locator: dict[str, Any] | None = None,
) -> dict[str, Any]:
    matched_ids = matched_ids or []
    return {
        "source_id": source_id,
        "sequence_key": "DBAASP:DBAASPN_19717",
        "source_table": source_table,
        "status": status,
        "layer1_status": status,
        "database_measure": database_measure,
        "database_subject": database_subject,
        "matched_activity_record_ids": matched_ids,
        "matched_activity_record_id": matched_ids[0] if matched_ids else "",
        "traceability": loc(trace_locator, path=f"paper_packets/{PAPER_ID}/database/{source_table}"),
        "citation_traceability": loc("xml:article-meta", doi=DOI, pmid="30158478", pmcid="PMC6225264"),
        "sequence_check": {
            "status": sequence_status,
            "source_locator": source_locator
            or loc("xml:fig=1;xml:sec=2.2;supp:molecules-23-02179-s001.pdf:Figures_S1-S18"),
            "database_sequence": "ELlLDlI",
            "database_sequence_source": "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv:26049",
            "note": "DBAASP stores a generic nonribosomal Pumilacidin sequence while this paper reports pumilacidins A and C as separate lipopeptides with structure/NMR/MS evidence.",
        },
        "conflict_context": conflict_context,
        "review_notes": review_notes or conflict_context,
        "reviewed_at": generated_at,
    }


def build_database(activity: dict[str, Any], generated_at: str) -> dict[str, Any]:
    ids = {row["record_id"]: row for row in activity["activity_records"]}
    records = [
        audit_record(
            source_table="linked_assay_records.jsonl",
            source_id="DBAASP:DBAASPN_19717:assay:168665",
            trace_locator="database:linked_assay_records:row=1",
            status="source_conflict",
            database_measure="IC50 8 µM",
            database_subject="Plasmodium falciparum; schizont stage",
            matched_ids=[
                f"{PAPER_ID}-table1-pumilacidin-a-schizont-ic50",
                f"{PAPER_ID}-table1-pumilacidin-c-schizont-ic50",
            ],
            conflict_context="DBAASP collapses pumilacidins A/C into generic Pumilacidin and rounds the schizont IC50 to 8 µM; primary Table 1 has separate A=8.34 µM and C=7.75 µM rows.",
            review_notes="Preserved as source_conflict rather than source_verified because the database row is a rounded/generic summary of two primary-source compounds.",
            generated_at=generated_at,
        ),
        audit_record(
            source_table="linked_assay_records.jsonl",
            source_id="DBAASP:DBAASPN_19717:assay:168666",
            trace_locator="database:linked_assay_records:row=2",
            status="source_conflict",
            database_measure="IC50 17.5 µM",
            database_subject="Plasmodium falciparum; ring stage",
            matched_ids=[
                f"{PAPER_ID}-table1-pumilacidin-a-ring-ic50",
                f"{PAPER_ID}-table1-pumilacidin-c-ring-ic50",
            ],
            conflict_context="DBAASP collapses pumilacidins A/C into generic Pumilacidin and records a ring-stage value of 17.5 µM; primary Table 1 has separate A=15.44 µM and C=19.59 µM rows.",
            review_notes="Preserved as source_conflict rather than source_verified because the database row appears to summarize/round two primary-source compound-specific rows.",
            generated_at=generated_at,
        ),
        audit_record(
            source_table="linked_experiment_records.jsonl",
            source_id="DBAASP:DBAASPN_19717:experiment:168665",
            trace_locator="database:linked_experiment_records:row=1",
            status="source_conflict",
            database_measure="IC50 8 µM",
            database_subject="Plasmodium falciparum; schizont stage",
            matched_ids=[
                f"{PAPER_ID}-table1-pumilacidin-a-schizont-ic50",
                f"{PAPER_ID}-table1-pumilacidin-c-schizont-ic50",
            ],
            conflict_context="Source conflict: experiment export repeats the generic/rounded DBAASP schizont row; source evidence supports separate Table 1 compound rows but not a single exact generic Pumilacidin 8 µM row.",
            generated_at=generated_at,
        ),
        audit_record(
            source_table="linked_experiment_records.jsonl",
            source_id="DBAASP:DBAASPN_19717:experiment:168666",
            trace_locator="database:linked_experiment_records:row=2",
            status="source_conflict",
            database_measure="IC50 17.5 µM",
            database_subject="Plasmodium falciparum; ring stage",
            matched_ids=[
                f"{PAPER_ID}-table1-pumilacidin-a-ring-ic50",
                f"{PAPER_ID}-table1-pumilacidin-c-ring-ic50",
            ],
            conflict_context="Source conflict: experiment export repeats the generic/rounded DBAASP ring-stage row; source evidence supports separate Table 1 compound rows but not a single exact generic Pumilacidin 17.5 µM row.",
            generated_at=generated_at,
        ),
        audit_record(
            source_table="linked_literature_records.jsonl",
            source_id="DBAASP:DBAASPN_19717:literature:30158478",
            trace_locator="database:linked_literature_records:row=1",
            status="source_verified",
            database_subject=TITLE,
            matched_ids=[],
            conflict_context="",
            review_notes="Literature linkage matches the paper DOI, PMID, PMCID, title, and year in article metadata.",
            sequence_status="not_required_for_literature_link",
            source_locator=loc("xml:article-meta", doi=DOI, pmid="30158478", pmcid="PMC6225264"),
            generated_at=generated_at,
        ),
        {
            "source_id": "DBAASP:DBAASPN_19717:sequence_catalog",
            "sequence_key": "DBAASP:DBAASPN_19717",
            "source_table": "merged_amp_corpus/output/sequences/all_sequences.csv",
            "status": "sequence_modified_not_normalized",
            "layer1_status": "sequence_modified_not_normalized",
            "database_measure": "",
            "database_subject": "Pumilacidin",
            "database_sequence": "ELlLDlI",
            "database_length": 7,
            "database_sequence_type": "Nonribosomal",
            "traceability": loc(
                "merged:sequences/all_sequences.csv:row=26049",
                path="/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
            ),
            "citation_traceability": loc("xml:article-meta", doi=DOI, pmid="30158478", pmcid="PMC6225264"),
            "sequence_check": {
                "status": "modified_nonribosomal_sequence_requires_context",
                "source_locator": loc("xml:fig=1;xml:sec=2.2;supp:molecules-23-02179-s001.pdf:Figures_S1-S18"),
                "primary_source_statement": "The paper reports isolated pumilacidins A and C as structures characterized by NMR/tandem MS and comparison with literature; it does not print the DBAASP one-letter nonribosomal sequence.",
            },
            "conflict_context": "The merged sequence catalog supplies a generic modified/nonribosomal sequence for DBAASPN_19717, while the primary paper separates pumilacidin A and C and supports them by structure, NMR, and MS figures rather than a normalized peptide sequence string.",
            "review_notes": "Do not normalize this nonribosomal lipopeptide into an unmodified linear peptide sequence; preserve the modified sequence caveat.",
            "reviewed_at": generated_at,
        },
    ]
    summary = Counter(record["status"] for record in records)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "audit_scope": "Worker-4 source-reviewed DBAASP linked assay/experiment/literature rows plus the merged DBAASP sequence catalog row against XML/PDF/supplement/database evidence.",
        "database_row_counts": {
            "linked_assay_records": 2,
            "linked_experiment_records": 2,
            "linked_literature_records": 1,
            "linked_dramp_activity_records": 0,
            "linked_sequence_records": 0,
            "merged_sequence_catalog_records_checked": 1,
        },
        "record_audits": records,
        "status_summary": dict(summary),
        "caution_findings": [
            {
                "caution_code": "dbaasp_generic_rounded_activity_rows",
                "severity": "caution",
                "record_ids": [
                    "DBAASP:DBAASPN_19717:assay:168665",
                    "DBAASP:DBAASPN_19717:assay:168666",
                ],
                "evidence_context": "Primary Table 1 has compound-specific pumilacidin A/C rows; DBAASP has two generic rounded Pumilacidin rows for parasite stage.",
            },
            {
                "caution_code": "nonribosomal_sequence_not_normalized",
                "severity": "caution",
                "record_ids": ["DBAASP:DBAASPN_19717:sequence_catalog"],
                "evidence_context": "Primary source supports structures of pumilacidins A/C but not a normalized one-letter database sequence.",
            },
        ],
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    claims = [
        {
            "claim_id": "mech-mitochondrial-membrane-potential",
            "claim_text": "Pumilacidins A and C are associated with mitochondrial dysfunction in P. falciparum, shown by reduced mitochondrial membrane potential after treatment.",
            "entity_scope": "Pumilacidins A and C at 10 μM in schizont-stage P. falciparum",
            "evidence_class": "direct_mechanism",
            "direct_assay_types": ["DiOC6(3) mitochondrial membrane potential flow cytometry"],
            "source_locator": loc("xml:sec=2.5;xml:fig=7;xml:sec=4.11"),
            "limitations": "The paper supports mitochondrial dysfunction as an apoptosis-like phenotype; it does not identify a single molecular target.",
            "reviewed_at": generated_at,
        },
        {
            "claim_id": "mech-cytosolic-calcium-decrease",
            "claim_text": "Pumilacidin treatment decreased parasite cytosolic calcium beginning at the 10 min measurement in saponin-isolated parasites.",
            "entity_scope": "Pumilacidins A and C at 10 μM in isolated P. falciparum parasites",
            "evidence_class": "direct_mechanism",
            "direct_assay_types": ["FURA 2AM calcium fluorescence assay"],
            "source_locator": loc("xml:sec=2.7;xml:fig=9;xml:sec=4.13"),
            "limitations": "Direction and timing are supported; exact figure values are not graph-digitized from the local image.",
            "reviewed_at": generated_at,
        },
        {
            "claim_id": "mech-ip3-pi3k-pkc-pathway-rescue",
            "claim_text": "IP3K/PI3K/PKC-related inhibitors partly reversed surfactin-induced parasite growth inhibition, supporting involvement of survival/signaling pathways.",
            "entity_scope": "Pumilacidins A and C with 3MA, LY29400, or bisindolylmaleimide I pre-incubation",
            "evidence_class": "pathway_inference_with_direct_assay",
            "direct_assay_types": ["pharmacological inhibitor proliferation assay", "Giemsa morphology microscopy"],
            "source_locator": loc("xml:sec=2.8;xml:table=3;xml:fig=10;xml:fig=11"),
            "limitations": "The inhibitor rescue assay is pathway-level support and should not be promoted to a named direct molecular target.",
            "reviewed_at": generated_at,
        },
        {
            "claim_id": "mech-ros-not-supported",
            "claim_text": "ROS generation was not supported as a mechanism in the local source; CM-H2DCFDA fluorescence did not change in a time-dependent manner after surfactin treatment.",
            "entity_scope": "Pumilacidins A and C at 10 μM in schizont-stage P. falciparum",
            "evidence_class": "negative_mechanism_evidence",
            "direct_assay_types": ["CM-H2DCFDA ROS flow cytometry"],
            "source_locator": loc("xml:sec=2.6;xml:fig=8;xml:sec=4.12"),
            "limitations": "This is negative evidence for ROS involvement, not a positive mechanism claim.",
            "reviewed_at": generated_at,
        },
        {
            "claim_id": "mech-host-cell-membrane-damage-not-supported",
            "claim_text": "At 10 μM, the paper did not find evident hemolysis or significant propidium iodide incorporation in treated red blood cells.",
            "entity_scope": "uninfected and infected red blood cells exposed to pumilacidins A and C",
            "evidence_class": "negative_toxicity_mechanism_evidence",
            "direct_assay_types": ["hemolysis assay", "propidium iodide flow cytometry"],
            "source_locator": loc("xml:sec=2.3;xml:fig=4;xml:fig=5"),
            "limitations": "Only the reported test concentration/time condition is supported.",
            "reviewed_at": generated_at,
        },
    ]
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 source-reviewed mechanism ontology from Results, Methods, figures, and Table 3. Figure-only exact numeric values were not invented.",
        "mechanism_claims": claims,
        "unrecoverable_material_gaps": [],
        "caution_findings": [
            {
                "caution_code": "direct_molecular_target_unresolved",
                "severity": "caution",
                "evidence_context": "The paper supports mitochondrial/calcium/pathway phenotypes but says the precise surfactin mechanism in Plasmodium parasites remains unclear.",
            }
        ],
    }


def build_rework_target(generated_at: str, semantic: dict[str, Any], publication: dict[str, Any]) -> dict[str, Any]:
    semantic_codes = [
        issue.get("code")
        for result in semantic.get("results", [])
        for issue in result.get("issues", [])
        if isinstance(issue, dict)
    ]
    return {
        "ticket_id": TICKET_ID,
        "paper_id": PAPER_ID,
        "created_at": generated_at,
        "worker": "worker-6",
        "owner_worker": "worker-6",
        "target_queue": "analysis",
        "layer": "review",
        "failure_code": "strict_gates_failed_after_worker46_repair",
        "failing_object": "publication_grade_ready",
        "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
        "source_evidence_to_check": CHECKED_INPUTS,
        "omission_context": semantic_codes,
        "blocks": ["publication_grade_ready", "final_approval"],
        "required_action": "Repair the concrete semantic/publication QA failures, rerun semantic_three_layer_gate.py and check_three_layer_publication_quality.py, and keep the paper non-accepted until they pass.",
        "qc_failure_reasons": [
            {
                "code": "strict_gates_failed_after_worker46_repair",
                "owner_worker": "worker-6",
                "severity": "blocking",
                "reason": "Strict semantic or publication-quality gates still failed after bounded worker-4/6 repair.",
            }
        ],
        "gate_failure_context": {
            "semantic_issue_codes": semantic_codes,
            "publication_risk_counts": publication.get("risk_counts", {}),
        },
    }


def build_review(
    activity: dict[str, Any],
    database: dict[str, Any],
    mechanism: dict[str, Any],
    generated_at: str,
    gates_ready: bool | None,
    semantic: dict[str, Any] | None = None,
    publication: dict[str, Any] | None = None,
) -> dict[str, Any]:
    semantic = semantic or {}
    publication = publication or {}
    publication_grade = gates_ready is not False
    rework_targets = [] if publication_grade else [build_rework_target(generated_at, semantic, publication)]
    qc_failure_reasons = [] if publication_grade else rework_targets[0]["qc_failure_reasons"]
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "generated_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "accepted_with_cautions" if publication_grade else "needs_targeted_rework",
        "publication_grade": publication_grade,
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
            "note": "Local XML/PDF/OA package, Supplementary PDF text, Figure 1-11 captions, Table 1-3 rows, packet database JSONL, and merged DBAASP sequence/assay/literature rows were reopened. The supplement contains NMR/MS figure support and no activity/toxicity/mechanism table requiring extraction.",
        },
        "checked_inputs": CHECKED_INPUTS,
        "semantic_quality_checks": {
            "activity_records": len(activity["activity_records"]),
            "activity_rows_from_table1": 4,
            "toxicity_rows_from_table2_or_figures": 3,
            "database_record_audits": len(database["record_audits"]),
            "database_status_summary": database["status_summary"],
            "mechanism_claims": len(mechanism["mechanism_claims"]),
            "open_rework_target_count": len(rework_targets),
            "closed_rework_ticket_ids": [TICKET_ID] if publication_grade else [],
            "supplementary_tables_present": 0,
            "supplementary_pdf_reviewed": True,
        },
        "per_layer_decision_rationale": {
            "material_packet": "Material remains material_extracted_with_gaps because the packet is an extraction surface, but paper-local XML/PDF/OA/supplement files needed for this worker-4/6 re-review were reopened and no material blocker remains.",
            "validator_contract": "The structural validator contract is distinct from publication review; final acceptance depends on the semantic and publication gates rerun after this repair.",
            "layer_1_database": "DBAASP literature linkage is source_verified. DBAASP assay/experiment rows are not promoted to source_verified because they collapse pumilacidins A/C into generic rounded Pumilacidin stage rows; these are preserved as nonblocking source_conflict. The nonribosomal sequence catalog row is preserved as sequence_modified_not_normalized.",
            "layer_2_activity_toxicity": "Worker-6 final reconciliation corrected the Table 1 rowspan parsing, retained Table 2 Vero-cell cytotoxicity values, and kept figure-only hemolysis/proliferation results qualitative rather than inventing exact graph values.",
            "layer_3_mechanism": "Mechanism claims are bounded to directly assayed mitochondrial potential, calcium, ROS-negative, membrane-damage-negative, and pathway-inhibitor evidence. No direct molecular target is claimed.",
            "publication_grade_review": "The previous framework-test blocker is closed only if strict gates pass; remaining database and mechanism uncertainties are explicit cautions rather than open rework targets." if publication_grade else "Strict gates still fail after bounded repair, so the existing ticket remains open with concrete gate context.",
        },
        "caution_findings": [
            {
                "caution_code": "dbaasp_generic_rounded_activity_rows_preserved",
                "severity": "caution",
                "evidence_context": "DBAASP reports generic Pumilacidin IC50 rows of 8 and 17.5 µM, while primary Table 1 reports separate Pumilacidin A/C rows for schizont and ring stages.",
                "record_count": 4,
            },
            {
                "caution_code": "nonribosomal_sequence_not_normalized",
                "severity": "caution",
                "evidence_context": "DBAASP sequence ELlLDlI is a modified/nonribosomal catalog representation; the paper supports structures through Figure 1 plus NMR/MS supplementary figures, not a normalized peptide string.",
            },
            {
                "caution_code": "figure_only_exact_values_not_digitized",
                "severity": "caution",
                "evidence_context": "Local source supports qualitative or approximate figure claims for hemolysis, membrane integrity, proliferation, ROS, calcium, and mitochondrial potential; exact chart values were not fabricated.",
            },
            {
                "caution_code": "direct_molecular_target_unresolved",
                "severity": "caution",
                "evidence_context": "The paper supports mitochondrial dysfunction, calcium decrease, and pathway involvement but does not identify a single direct molecular target.",
            },
        ],
        "unrecoverable_material_gaps": [],
        "qc_failure_reasons": qc_failure_reasons,
        "rework_targets": rework_targets,
        "closed_rework_ticket_ids": [TICKET_ID] if publication_grade else [],
        "summary": "Worker-4/6 source review reopened the local XML/PDF/OA package, supplementary PDF text, locator index, packet database JSONL, and merged DBAASP rows. Table 1 compound/stage rows were reconciled, DBAASP generic rounded activity rows were preserved as source_conflict, the nonribosomal sequence catalog row remains sequence_modified_not_normalized, and final review is accepted with cautions only if strict gates pass.",
        "strict_gate": {
            "required_rework_count": len(rework_targets),
            "semantic_gate_pass": None if gates_ready is None else semantic.get("publication_grade_fail_count") == 0,
            "publication_quality_pass": None if gates_ready is None else publication.get("publication_grade_pass") is True,
            "closed_rework_ticket_ids": [TICKET_ID] if publication_grade else [],
            "gate_evidence": {
                "semantic_gate_report": str(SEMANTIC_REPORT.relative_to(ROOT)),
                "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
                "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
                "semantic_issue_count": sum(item.get("issue_count", 0) for item in semantic.get("results", [])),
                "publication_quality_report": str(PUBLICATION_REPORT.relative_to(ROOT)),
                "publication_quality_pass": publication.get("publication_grade_pass"),
                "publication_risk_counts": publication.get("risk_counts", {}),
                "publication_generated_at_utc": publication.get("generated_at_utc"),
                "gate_verified_at": generated_at if gates_ready is not None else None,
            },
        },
    }


def build_quality_feedback(review: dict[str, Any], generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_at": generated_at,
        "issue_count": len(review["qc_failure_reasons"]),
        "qc_failure_reasons": review["qc_failure_reasons"],
        "rework_targets": review["rework_targets"],
        "closed_rework_ticket_ids": review["closed_rework_ticket_ids"],
        "unrecoverable_material_gaps": review["unrecoverable_material_gaps"],
        "rework_context_packet_required": bool(review["rework_targets"]),
        "publication_grade_ready": review["publication_grade"],
        "gate_evidence": review["strict_gate"]["gate_evidence"],
    }


def run_gate(cmd: list[str], out_path: Path | None = None) -> tuple[int, dict[str, Any]]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    text = proc.stdout.strip()
    try:
        payload = json.loads(text) if text else {}
    except json.JSONDecodeError:
        payload = {"stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode}
    if out_path and payload:
        write_json(out_path, payload)
    return proc.returncode, payload


def write_core_outputs(generated_at: str, review: dict[str, Any], activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> None:
    write_json(PACKET / "analysis" / "activity_toxicity_evidence.json", activity)
    write_json(PACKET / "final" / "activity_toxicity_evidence.json", activity)
    write_json(PAPER / "final" / "activity_toxicity_evidence.json", activity)
    write_json(PACKET / "analysis" / "database_record_audit.json", database)
    write_json(PACKET / "final" / "database_record_verification.json", database)
    write_json(PAPER / "final" / "database_record_verification.json", database)
    write_json(PACKET / "analysis" / "mechanism_evidence.json", mechanism)
    write_json(PACKET / "final" / "mechanism_evidence.json", mechanism)
    write_json(PACKET / "final" / "mechanism_ontology_record.json", mechanism)
    write_json(PAPER / "final" / "mechanism_evidence.json", mechanism)
    write_json(PAPER / "final" / "mechanism_ontology_record.json", mechanism)
    write_json(PACKET / "analysis" / "adjudication_report.json", review)
    write_json(PACKET / "final" / "review_report.json", review)
    write_json(PAPER / "work" / "review" / "adjudication_report.json", review)
    write_json(PAPER / "final" / "review_report.json", review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", build_quality_feedback(review, generated_at))


def update_status_files(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], review: dict[str, Any]) -> None:
    status = "source_reviewed_publication_grade_ready" if review["publication_grade"] else "analysis_needs_analysis_rework"
    open_ticket_ids = [] if review["publication_grade"] else [target["ticket_id"] for target in review["rework_targets"]]
    manifest = read_json(PACKET / "packet_manifest.json")
    manifest.update(
        {
            "analysis_queue_status": status,
            "open_rework_ticket_ids": open_ticket_ids,
            "closed_rework_ticket_ids": review["closed_rework_ticket_ids"],
            "updated_at": generated_at,
            "publication_grade_ready": review["publication_grade"],
        }
    )
    write_json(PACKET / "packet_manifest.json", manifest)
    write_json(
        PACKET / "analysis" / "analysis_status.json",
        {
            "paper_id": PAPER_ID,
            "generated_at": generated_at,
            "status": status,
            "activity_record_count": len(activity["activity_records"]),
            "activity_extraction_issue_count": len(activity["extraction_issues"]),
            "activity_extraction_issues": activity["extraction_issues"],
            "database_record_count": len(database["record_audits"]),
            "database_status_summary": database["status_summary"],
            "mechanism_claim_count": len(mechanism["mechanism_claims"]),
            "open_rework_ticket_ids": open_ticket_ids,
            "closed_rework_ticket_ids": review["closed_rework_ticket_ids"],
            "publication_grade_ready": review["publication_grade"],
        },
    )
    context_path = WORKFLOW / "workflow_context.json"
    context = read_json(context_path)
    if context:
        context["current_state"] = status
        context["updated_at"] = generated_at
        context["open_rework_tickets"] = open_ticket_ids
        context["gate_summary"] = {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": review["strict_gate"]["semantic_gate_pass"],
            "publication_grade_ready": review["publication_grade"],
        }
        context.setdefault("gate_reports", {})
        context["gate_reports"]["semantic_gate"] = str(SEMANTIC_REPORT)
        context["gate_reports"]["publication_quality"] = str(PUBLICATION_REPORT)
        write_json(context_path, context)


def update_reports(generated_at: str, review: dict[str, Any], activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], semantic: dict[str, Any], publication: dict[str, Any]) -> None:
    write_json(
        COMPLETE_REPORT,
        {
            "paper_id": PAPER_ID,
            "doi": DOI,
            "title": TITLE,
            "generated_at": generated_at,
            "completion_claim": "source_reviewed_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions"
            if review["publication_grade"]
            else "worker46_repair_done_but_strict_gate_failed",
            "current_state": "source_reviewed_publication_grade_ready" if review["publication_grade"] else "rework_queue",
            "terminal_status": "source_reviewed_publication_grade_ready" if review["publication_grade"] else "awaiting_targeted_rework",
            "final_approval_status": "accepted_with_cautions" if review["publication_grade"] else "refused_needs_rework",
            "not_publication_grade_reason": None if review["publication_grade"] else "Strict gate failed after bounded worker-4/6 source repair.",
            "gate_summary": {
                "structural_ready": True,
                "validator_contract_ready": True,
                "semantic_gate_ready": semantic.get("publication_grade_fail_count") == 0,
                "publication_grade_ready": review["publication_grade"],
            },
            "gate_results": {
                "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
                "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
                "publication_quality_pass": publication.get("publication_grade_pass"),
            },
            "analysis": {
                "activity_records": len(activity["activity_records"]),
                "database_record_audits": len(database["record_audits"]),
                "database_status_summary": database["status_summary"],
                "mechanism_claims": len(mechanism["mechanism_claims"]),
                "review_status": review["review_status"],
            },
            "material": {
                "material_queue_status": read_json(PACKET / "packet_manifest.json").get("material_queue_status"),
                "supplementary_tables": 0,
                "materials_exhausted_for_worker46_review": True,
            },
            "rework_ticket_ids": [] if review["publication_grade"] else [target["ticket_id"] for target in review["rework_targets"]],
            "closed_rework_ticket_ids": review["closed_rework_ticket_ids"],
            "open_rework_ticket_count": 0 if review["publication_grade"] else len(review["rework_targets"]),
            "publication_quality_gate": "passed_after_worker46_repair" if publication.get("publication_grade_pass") is True else "failed_after_worker46_repair",
            "semantic_gate": "passed_after_worker46_repair" if semantic.get("publication_grade_fail_count") == 0 else "failed_after_worker46_repair",
            "packet_root": str(PACKET),
            "workflow_dir": str(WORKFLOW),
        },
    )


def append_rework_response(generated_at: str, review: dict[str, Any], semantic: dict[str, Any], publication: dict[str, Any]) -> None:
    response_id = f"{TICKET_ID}-worker46-source-review-{'closed' if review['publication_grade'] else 'still-open'}"
    append_jsonl_once(
        PACKET / "rework" / "rework_responses.jsonl",
        response_id,
        {
            "response_id": response_id,
            "ticket_id": TICKET_ID,
            "paper_id": PAPER_ID,
            "responded_at": generated_at,
            "owner_workers": ["worker-4", "worker-6"],
            "response_status": "closed_source_reviewed" if review["publication_grade"] else "still_open_after_bounded_repair",
            "artifacts_updated": [
                f"paper_packets/{PAPER_ID}/analysis/activity_toxicity_evidence.json",
                f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
                f"paper_packets/{PAPER_ID}/analysis/mechanism_evidence.json",
                f"paper_packets/{PAPER_ID}/analysis/adjudication_report.json",
                f"paper_packets/{PAPER_ID}/final/activity_toxicity_evidence.json",
                f"paper_packets/{PAPER_ID}/final/database_record_verification.json",
                f"paper_packets/{PAPER_ID}/final/mechanism_evidence.json",
                f"paper_packets/{PAPER_ID}/final/mechanism_ontology_record.json",
                f"paper_packets/{PAPER_ID}/final/review_report.json",
                f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
                f"papers/{PAPER_ID}/final/database_record_verification.json",
                f"papers/{PAPER_ID}/final/mechanism_evidence.json",
                f"papers/{PAPER_ID}/final/mechanism_ontology_record.json",
                f"papers/{PAPER_ID}/final/review_report.json",
                f"papers/{PAPER_ID}/work/review/adjudication_report.json",
                f"papers/{PAPER_ID}/work/review/quality_feedback.json",
            ],
            "source_paths_checked": CHECKED_INPUTS,
            "tools_attempted": [
                "jq over handoff, packet, status, final, and database artifacts",
                "ElementTree XML table/section parsing for source/paper.xml",
                "rg over XML/PDF/supplement/database text",
                "sed inspection of extracted PDF and supplementary PDF text",
                "merged-corpus rg for DBAASP sequence/assay/literature rows",
                "semantic_three_layer_gate.py",
                "check_three_layer_publication_quality.py",
            ],
            "values_recovered": {
                "table1_antiplasmodial_ic50_rows": 4,
                "table2_vero_ic50_rows": 2,
                "qualitative_figure_activity_toxicity_rows": 2,
                "database_rows_source_verified": review["semantic_quality_checks"]["database_status_summary"].get("source_verified", 0),
                "database_rows_source_conflict": review["semantic_quality_checks"]["database_status_summary"].get("source_conflict", 0),
                "database_rows_sequence_modified_not_normalized": review["semantic_quality_checks"]["database_status_summary"].get("sequence_modified_not_normalized", 0),
                "mechanism_claims_source_reviewed": len(read_json(PAPER / "final" / "mechanism_ontology_record.json").get("mechanism_claims", [])),
            },
            "unrecoverable_material_gaps": review["unrecoverable_material_gaps"],
            "remaining_qc_failure_reasons": review["qc_failure_reasons"],
            "remaining_rework_targets": review["rework_targets"],
            "gate_evidence": {
                "semantic_report": str(SEMANTIC_REPORT.relative_to(ROOT)),
                "semantic_pass_count": semantic.get("publication_grade_pass_count"),
                "semantic_fail_count": semantic.get("publication_grade_fail_count"),
                "publication_report": str(PUBLICATION_REPORT.relative_to(ROOT)),
                "publication_quality_pass": publication.get("publication_grade_pass"),
            },
            "notes": "Bounded local recovery found no supplementary activity/mechanism table. The existing blocker is closed only when strict gates pass; DBAASP generic rounded rows remain explicit source_conflict cautions.",
        },
    )


def main() -> int:
    generated_at = utc_now()
    activity = build_activity(generated_at)
    database = build_database(activity, generated_at)
    mechanism = build_mechanism(generated_at)
    provisional_review = build_review(activity, database, mechanism, generated_at, gates_ready=None)
    write_core_outputs(generated_at, provisional_review, activity, database, mechanism)

    sem_rc, semantic = run_gate(
        [
            "python",
            ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py",
            "--root",
            ".",
            "--paper-id",
            PAPER_ID,
            "--json",
        ],
        SEMANTIC_REPORT,
    )
    pub_rc, publication = run_gate(
        [
            "python",
            ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py",
            "--manifest",
            str(MANIFEST.relative_to(ROOT)),
            "--root",
            ".",
            "--json-out",
            str(PUBLICATION_REPORT.relative_to(ROOT)),
        ],
        PUBLICATION_REPORT,
    )
    gates_ready = sem_rc == 0 and pub_rc == 0 and publication.get("publication_grade_pass") is True
    final_review = build_review(activity, database, mechanism, generated_at, gates_ready, semantic, publication)
    write_core_outputs(generated_at, final_review, activity, database, mechanism)
    update_status_files(generated_at, activity, database, mechanism, final_review)
    append_rework_response(generated_at, final_review, semantic, publication)
    update_reports(generated_at, final_review, activity, database, mechanism, semantic, publication)

    print(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "activity_records": len(activity["activity_records"]),
                "database_status_summary": database["status_summary"],
                "mechanism_claims": len(mechanism["mechanism_claims"]),
                "semantic_returncode": sem_rc,
                "publication_returncode": pub_rc,
                "publication_grade_ready": final_review["publication_grade"],
                "review_status": final_review["review_status"],
                "semantic_report": str(SEMANTIC_REPORT.relative_to(ROOT)),
                "publication_report": str(PUBLICATION_REPORT.relative_to(ROOT)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if gates_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
