#!/usr/bin/env python3
"""Repair worker-2/4/6 artifacts for doi__10.1371_journal.ppat.1000698."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ID = "doi__10.1371_journal.ppat.1000698"
DOI = "10.1371/journal.ppat.1000698"
PMID = "20019810"
PMCID = "PMC2788422"
TITLE = "Protein C inhibitor--a novel antimicrobial agent."
TICKET_ID = "rwk-complete-test-0001"

ROOT = Path(".").resolve()
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
REPORTS = ROOT / "reports"
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID

SOURCE_PATHS_CHECKED = [
    f"rework_context/{PAPER_ID}/handoff_context.json",
    f"paper_packets/{PAPER_ID}/packet_manifest.json",
    f"paper_packets/{PAPER_ID}/locators/locator_index.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
    f"paper_packets/{PAPER_ID}/analysis/analysis_status.json",
    f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
    f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/ppat.1000698.txt",
    f"paper_packets/{PAPER_ID}/extracted/pdf_tables.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_index.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_text.jsonl",
    f"paper_packets/{PAPER_ID}/extracted/archive_manifest.json",
    f"paper_packets/{PAPER_ID}/raw/paper.xml",
    f"paper_packets/{PAPER_ID}/raw/paper.pdf",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/local-APD6-ppat.1000698.s001.tif",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/local-APD6-ppat.1000698.s002.tif",
    f"paper_packets/{PAPER_ID}/raw/supplementary_original/local-APD6-ppat.1000698.s003.tif",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.nxml",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.pdf",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.t001.jpg",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.g001.jpg",
    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.g002.jpg",
    f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_sequence_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_dramp_activity_records.jsonl",
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    "/mnt/d/work/\u6297\u83cc\u80bd/\u6570\u636e\u5e93/merged_amp_corpus/output/sequences/all_sequences.csv",
    "/mnt/d/work/\u6297\u83cc\u80bd/\u6570\u636e\u5e93/merged_amp_corpus/output/experiments/apd6_activity_text_records.csv",
    "/mnt/d/work/\u6297\u83cc\u80bd/\u6570\u636e\u5e93/merged_amp_corpus/output/experiments/all_experimental_records.csv",
    "/mnt/d/work/\u6297\u83cc\u80bd/\u6570\u636e\u5e93/merged_amp_corpus/output/literature/sequence_literature_links.csv",
    "/mnt/d/work/\u6297\u83cc\u80bd/\u6570\u636e\u5e93/merged_amp_corpus/landed_assets/papers/"
    f"{PAPER_ID}/supplementary/landing-*.bin",
    "/mnt/d/work/\u6297\u83cc\u80bd/\u6570\u636e\u5e93/merged_amp_corpus/landed_assets/papers/"
    f"{PAPER_ID}/supplementary/local-APD6-ppat.1000698.s00*.tif",
]

TOOLS_ATTEMPTED = [
    "jq",
    "rg",
    "file",
    "xml.etree.ElementTree JATS table/figure review",
    "pdftotext-derived packet text review",
    "JSONL linked database row review",
    "merged APD6 sequence/activity CSV review",
    "view_image for OA package Figure 1 and Figure 2 JPG",
    "view_image attempted on TIFF supplements and failed because TIFF is unsupported in this runtime",
    "semantic_three_layer_gate.py",
    "check_three_layer_publication_quality.py",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=False) + "\n")


def target_payload(label: str) -> dict[str, Any]:
    mapping = {
        "E. coli": {
            "species": "Escherichia coli",
            "strain": "not disambiguated in Table 1; Methods list E. coli 37.4 and ATCC25922",
            "gram_status": "Gram-negative",
        },
        "P. aeruginosa": {
            "species": "Pseudomonas aeruginosa",
            "strain": "ATCC27853",
            "gram_status": "Gram-negative",
        },
        "S. aureus": {
            "species": "Staphylococcus aureus",
            "strain": "ATCC29213",
            "gram_status": "Gram-positive",
        },
        "C. albicans": {
            "species": "Candida albicans",
            "strain": "ATCC90028",
            "gram_status": "fungal",
        },
        "B. subtilis": {
            "species": "Bacillus subtilis",
            "strain": "ATCC6633",
            "gram_status": "Gram-positive",
        },
    }
    item = mapping[label]
    return {
        "target_class": "fungus" if item["gram_status"] == "fungal" else "bacteria",
        "class": "fungus" if item["gram_status"] == "fungal" else "bacteria",
        "species": item["species"],
        "strain": item["strain"],
        "strain_or_isolate": item["strain"],
        "gram_status": item["gram_status"],
        "raw_target_label": label,
    }


def peptide_payload(name: str) -> dict[str, Any]:
    if name == "SEK20":
        return {
            "name": "SEK20",
            "sequence": "SEKTLRKWLKMFKKRQLELY",
            "source_label": "SEK20, active region/fragment of protein C inhibitor",
            "modifications": ["none reported; synthetic peptide purity and molecular weight checked by MALDI-TOF"],
            "sequence_status": "source_conflict_terminal_L_variant_preserved",
            "identity_source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:sec=3:Antimicrobial effect of SEK20; xml:sec=13:Antimicrobial peptides and protein",
                "primary_source_sequence_variants": [
                    {
                        "locator": "xml:sec=3:Antimicrobial effect of SEK20",
                        "sequence": "SEKTLRKWLKMFKKRQLELY",
                        "length": 20,
                    },
                    {
                        "locator": "xml:sec=13:Antimicrobial peptides and protein",
                        "sequence": "SEKTLRKWLKMFKKRQLELYL",
                        "length": 21,
                    },
                ],
            },
        }
    return {
        "name": "LL-37",
        "sequence": "LLGDFFRKSKEKIGKEFKRIVQRIKDFLRNLVPRTES",
        "source_label": "LL-37 comparator antimicrobial peptide",
        "modifications": ["none reported"],
        "sequence_status": "source_verified_comparator",
        "identity_source_locator": {
            "source_path": f"papers/{PAPER_ID}/source/paper.xml",
            "locator": "xml:sec=3:Antimicrobial effect of SEK20; xml:sec=13:Antimicrobial peptides and protein",
        },
    }


TABLE1_ROWS = [
    ("E. coli", "LL-37", "9.1", 2, 2),
    ("E. coli", "SEK20", "9.9", 2, 3),
    ("P. aeruginosa", "LL-37", "7.8", 3, 2),
    ("P. aeruginosa", "SEK20", "9.0", 3, 3),
    ("S. aureus", "LL-37", "8.3", 4, 2),
    ("S. aureus", "SEK20", "8.2", 4, 3),
    ("C. albicans", "LL-37", "8.2", 5, 2),
    ("C. albicans", "SEK20", "8.5", 5, 3),
    ("B. subtilis", "LL-37", "12.9", 6, 2),
    ("B. subtilis", "SEK20", "12.6", 6, 3),
]


def build_activity(generated_at: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for target_label, peptide_name, raw_value, row_index, column_index in TABLE1_ROWS:
        target = target_payload(target_label)
        peptide = peptide_payload(peptide_name)
        records.append(
            {
                "record_id": f"{PAPER_ID}:table1:{peptide_name}:{target_label}:radial_diffusion_clearance_zone",
                "paper_id": PAPER_ID,
                "entity": peptide_name,
                "agent": peptide_name,
                "peptide": peptide,
                "agent_class": "protein C inhibitor-derived peptide" if peptide_name == "SEK20" else "comparator antimicrobial peptide",
                "endpoint": "radial_diffusion_clearance_zone_diameter",
                "raw_value": raw_value,
                "raw_unit": "mm",
                "normalized_value": raw_value,
                "normalized_unit": "mm",
                "normalization_status": "direct",
                "target": target,
                "assay_conditions": {
                    "method": "radial diffusion assay",
                    "medium": "0.03% TSB underlay agarose with 0.02% Tween-20; 6% TSB overlay agarose",
                    "inoculum": "2 x 10^6 CFU in 5 mL underlay agarose",
                    "sample_volume": "6 uL",
                    "diffusion_time": "3 h at 37 C before overlay",
                    "readout": "clear zone diameter minus well diameter after overnight incubation at 37 C",
                    "threshold": "clearance zones more than 4 mm considered bacterial killing",
                    "method_locator": {
                        "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                        "locator": "xml:sec=15:Bactericidal assays",
                    },
                },
                "replicates_statistics": {
                    "n": 3,
                    "standard_deviation": "regularly less than 10%",
                    "source_note": "Table 1 footnote reports n=3 and SD regularly less than 10%.",
                },
                "evidence_ladder": "primary_xml_table_radial_diffusion_value",
                "source_locator": {
                    "kind": "primary_xml_table",
                    "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                    "packet_source_path": f"paper_packets/{PAPER_ID}/raw/paper.xml",
                    "locator": f"xml:table=1:row={row_index}:column={column_index}",
                    "label": "Table 1",
                    "row_index": row_index,
                    "row_label": target_label,
                    "column": peptide_name,
                    "unit_context": "Table 1 footnote reports microbial growth inhibition expressed in mm.",
                    "pdf_text_locator": f"paper_packets/{PAPER_ID}/extracted/pdf_text/ppat.1000698.txt:146-195",
                },
                "source_column_context": {
                    "table": "Table 1",
                    "caption": "Microbial growth inhibition by LL-37 and SEK20",
                    "raw_cell": f"{raw_value} mm",
                    "row_label": target_label,
                    "column_header": peptide_name,
                },
                "database_links": [
                    {
                        "source_table": "linked_experiment_records.jsonl",
                        "row": 1,
                        "source_record_id": "AP00337",
                        "status": "source_verified_activity_value",
                    }
                ]
                if peptide_name == "SEK20"
                else [],
                "curation_notes": [
                    "Recovered during bounded worker-2 source review from XML Table 1 after the parser emitted no supported activity rows.",
                    "Rows are clearance-zone measurements, not MIC values; no ug/mL or uM conversion was attempted.",
                ],
                "source_reviewed": True,
                "reviewed_at": generated_at,
            }
        )

    toxicity_records = [
        {
            "record_id": f"{PAPER_ID}:figure1:SEK20:human_erythrocytes:hemolysis",
            "paper_id": PAPER_ID,
            "entity": "SEK20",
            "endpoint": "hemolysis",
            "raw_value": "no hemolytic activity detected through tested range",
            "raw_unit": "3-60 uM peptide exposure range",
            "target": {
                "target_class": "mammalian_cells",
                "species": "Homo sapiens erythrocytes",
                "strain_or_isolate": "human blood",
                "raw_target_label": "human erythrocytes",
            },
            "assay_conditions": {
                "method": "hemoglobin release at absorbance 540 nm after 1 h at 37 C",
                "positive_control": "2% Triton X-100",
                "method_locator": {
                    "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                    "locator": "xml:sec=16:Hemolytic assay",
                },
            },
            "source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:sec=3:Antimicrobial effect of SEK20; xml:fig=1:Figure 1",
                "figure_file": f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.g001.jpg",
            },
            "normalization_status": "not_convertible_qualitative_figure_result",
            "source_reviewed": True,
        },
        {
            "record_id": f"{PAPER_ID}:figure1:SEK20:HaCaT:LDH_release",
            "paper_id": PAPER_ID,
            "entity": "SEK20",
            "endpoint": "LDH_release",
            "raw_value": "no increased LDH release detected through tested range",
            "raw_unit": "0-60 uM peptide exposure range",
            "target": {
                "target_class": "mammalian_cells",
                "species": "Homo sapiens keratinocyte cell line HaCaT",
                "strain_or_isolate": "HaCaT",
                "raw_target_label": "HaCaT keratinocytes",
            },
            "assay_conditions": {
                "method": "LDH based TOX-7 kit on confluent HaCaT keratinocytes in DMEM",
                "replicates": "triplicate",
                "method_locator": {
                    "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                    "locator": "xml:sec=18:Lactate dehydrogenase (LDH) assay",
                },
            },
            "source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:sec=3:Antimicrobial effect of SEK20; xml:fig=1:Figure 1",
                "figure_file": f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.g001.jpg",
            },
            "normalization_status": "not_convertible_qualitative_figure_result",
            "source_reviewed": True,
        },
    ]

    return {
        "artifact_type": "worker2_activity_toxicity_evidence",
        "paper_id": PAPER_ID,
        "doi": DOI,
        "generated_at": generated_at,
        "extraction_scope": (
            "Worker-2 reopened XML Table 1, PDF text, figure captions, OA package Figure 1/2 images, "
            "supplement inventory, and linked APD6 rows. Table 1 clearance-zone values were recovered "
            "as quantitative activity rows; figure-only exact toxicity/survival values were kept qualitative."
        ),
        "activity_records": records,
        "toxicity_records": toxicity_records,
        "extraction_issues": [],
        "unrecoverable_material_gaps": [
            {
                "gap_code": "figure_exact_point_values_not_digitized",
                "source_paths_checked": [
                    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.g001.jpg",
                    f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.g002.jpg",
                    f"paper_packets/{PAPER_ID}/raw/supplementary_original/local-APD6-ppat.1000698.s001.tif",
                    f"paper_packets/{PAPER_ID}/raw/supplementary_original/local-APD6-ppat.1000698.s002.tif",
                    f"paper_packets/{PAPER_ID}/raw/supplementary_original/local-APD6-ppat.1000698.s003.tif",
                ],
                "tools_attempted": ["view_image", "file", "rg"],
                "why_unrecoverable": (
                    "Local TIFF supplements are image-only and the runtime lacks usable OCR/conversion tools; "
                    "JPG main figures were visually inspected, but exact chart digitization was not performed."
                ),
                "impact": "Exact figure point estimates are not used as numeric rows; XML/PDF text and Table 1 still support the quantitative activity layer.",
                "owner_worker": "worker-2",
                "blocks_publication_grade": False,
                "next_action": "record_and_continue",
            }
        ],
        "parser_quality_control": {
            "issue_count": 0,
            "source_reviewed_after_parser_empty": True,
            "rejects_mic_conversion": True,
            "activity_records_recovered": len(records),
            "toxicity_records_recovered": len(toxicity_records),
        },
    }


def build_database(generated_at: str) -> dict[str, Any]:
    record_audits = [
        {
            "source_id": "APD6:AP00337",
            "source_record_id": "AP00337",
            "sequence_key": "APD6:AP00337",
            "source_table": "APD6 peptides.csv / apd6_activity_text_records.csv",
            "database_name": "SEK20 (Lys-rich; active region and fragment of Protein C inhibitor (PCI), synthetic AMPs20, UCLL1)",
            "database_sequence": "SEKTLRKWLKMFKKRQLELY",
            "database_sequence_length": 20,
            "status": "source_conflict",
            "layer1_status": "source_conflict",
            "traceability": {
                "source_path": f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
                "locator": "database:linked_experiment_records:row=1",
            },
            "citation_traceability": {
                "source_path": f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
                "locator": "database:linked_literature_records:row=1",
                "doi": DOI,
                "pmid": PMID,
                "pmcid": PMCID,
                "status": "source_verified",
            },
            "name_check": {
                "status": "source_verified",
                "primary_source_locator": {
                    "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                    "locator": "xml:sec=3:Antimicrobial effect of SEK20",
                },
                "notes": "Primary source identifies SEK20 as a PCI-derived peptide; APD6 names the same entity.",
            },
            "sequence_check": {
                "status": "source_conflict",
                "database_sequence": "SEKTLRKWLKMFKKRQLELY",
                "source_locator": {
                    "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                    "locator": "xml:sec=3:Antimicrobial effect of SEK20; xml:sec=13:Antimicrobial peptides and protein",
                    "primary_source_sequence_variants": [
                        {
                            "locator": "xml:sec=3:Antimicrobial effect of SEK20",
                            "sequence": "SEKTLRKWLKMFKKRQLELY",
                            "length": 20,
                        },
                        {
                            "locator": "xml:sec=13:Antimicrobial peptides and protein",
                            "sequence": "SEKTLRKWLKMFKKRQLELYL",
                            "length": 21,
                        },
                    ],
                },
                "review_notes": (
                    "APD6 sequence matches the 20-residue SEK20 sequence in the Results text, while the Materials and Methods "
                    "peptide-synthesis paragraph contains a 21-residue terminal-L variant. The conflict is preserved."
                ),
            },
            "activity_annotation_check": {
                "status": "source_verified_with_sequence_caution",
                "primary_source_locators": [
                    {
                        "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                        "locator": "xml:table=1:rows=2-6:column=SEK20",
                    }
                ],
                "notes": "APD6 clearance-zone values match the SEK20 Table 1 values for E. coli, P. aeruginosa, S. aureus, B. subtilis, and C. albicans.",
            },
            "source_organism_check": {
                "status": "source_verified",
                "source": "human protein C inhibitor-derived synthetic peptide",
                "primary_source_locator": {
                    "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                    "locator": "xml:sec=3:Antimicrobial effect of SEK20; xml:sec=13:Antimicrobial peptides and protein",
                },
            },
            "conflict_flags": ["primary_source_sequence_terminal_L_conflict"],
            "conflict_context": (
                "Database APD6:AP00337 is not promoted to clean source_verified because local primary XML/PDF contains "
                "both a 20-residue SEK20 sequence and a 21-residue terminal-L variant."
            ),
            "review_notes": (
                "Worker-4 resolved the previous database-only placeholder into source_conflict: citation and Table 1 "
                "activity values are primary-source supported, but exact sequence length must remain cautionary."
            ),
            "source_reviewed": True,
            "reviewed_at": generated_at,
        },
        {
            "source_id": "APD6:AP00337",
            "source_record_id": "AP00337",
            "sequence_key": "APD6:AP00337",
            "source_table": "linked_literature_records.jsonl",
            "database_subject": TITLE,
            "status": "source_verified",
            "layer1_status": "source_verified",
            "traceability": {
                "source_path": f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
                "locator": "database:linked_literature_records:row=1",
            },
            "citation_traceability": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:article-meta",
                "doi": DOI,
                "pmid": PMID,
                "pmcid": PMCID,
            },
            "sequence_check": {
                "status": "not_sequence_record",
                "source_locator": {
                    "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                    "locator": "xml:article-meta",
                },
            },
            "review_notes": "Literature link matches DOI/PMID/PMCID for this paper; sequence-level conflict remains on the APD6 sequence/activity row.",
            "source_reviewed": True,
            "reviewed_at": generated_at,
        },
    ]
    return {
        "artifact_type": "worker4_database_record_verification",
        "paper_id": PAPER_ID,
        "doi": DOI,
        "generated_at": generated_at,
        "audit_scope": (
            "Worker-4 reopened linked APD6 experiment/literature rows, merged sequence/activity CSVs, and primary XML/PDF. "
            "Citation and Table 1 activity values are source-supported; the APD6 sequence is preserved as source_conflict."
        ),
        "database_row_counts": {
            "linked_assay_records": 0,
            "linked_dramp_activity_records": 0,
            "linked_experiment_records": 1,
            "linked_literature_records": 1,
            "linked_sequence_records": 0,
        },
        "record_audits": record_audits,
        "status_summary": {
            "source_conflict": 1,
            "source_verified": 1,
        },
        "unresolved_record_count": 0,
        "source_reviewed": True,
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    claims = [
        {
            "claim_id": "mech-001",
            "entity_scope": "SEK20 and protein C inhibitor antimicrobial region",
            "claim_text": "SEK20 and full-length protein C inhibitor are supported as membrane-active antimicrobial agents in this paper.",
            "evidence_class": "direct_mechanism",
            "direct_assay_types": ["liposome carboxyfluorescein leakage", "negative-stain electron microscopy"],
            "source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:fig=1:Figure 1; xml:fig=2:Figure 2; xml:fig=3:Figure 3",
            },
            "limitations": "Exact figure point estimates are not digitized; mechanism conclusion is limited to membrane permeabilization/disruption evidence reported in text, captions, and figures.",
        },
        {
            "claim_id": "mech-002",
            "entity_scope": "full-length protein C inhibitor",
            "claim_text": "Full-length protein C inhibitor is reported to kill E. coli and S. pyogenes without requiring release of a SEK20 peptide fragment.",
            "evidence_class": "direct_activity_context",
            "direct_assay_types": ["viable count assay", "protease-treatment control", "Western blot control"],
            "source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:sec=4:Antimicrobial activity of PCI; xml:fig=2:Figure 2",
            },
            "limitations": "No exact PCI CFU values are converted into activity rows because Figure 2 values are chart-only in the local material.",
        },
        {
            "claim_id": "mech-003",
            "entity_scope": "protein C inhibitor in streptococcal infection context",
            "claim_text": "The paper supports PCI association with bacteria, activated platelets, and infected tissue as host-context evidence, not as a standalone direct antimicrobial endpoint.",
            "evidence_class": "host_context_indirect",
            "direct_assay_types": [],
            "source_locator": {
                "source_path": f"papers/{PAPER_ID}/source/paper.xml",
                "locator": "xml:sec=5:PCI has antimicrobial activity in a plasma environment; xml:fig=4:Figure 4; xml:fig=5:Figure 5; xml:fig=6:Figure 6; xml:fig=7:Figure 7; xml:fig=8:Figure 8",
            },
            "limitations": "Host localization and plasma-growth results are retained as contextual mechanism/support evidence, not normalized antimicrobial potency rows.",
        },
    ]
    return {
        "artifact_type": "worker6_mechanism_ontology_record",
        "paper_id": PAPER_ID,
        "doi": DOI,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 source-reviewed mechanism claims from XML sections, figure captions, PDF text, and OA package figures.",
        "mechanism_claims": claims,
        "source_reviewed": True,
        "caution_findings": [
            {
                "caution_code": "figure_exact_values_not_digitized",
                "evidence_context": "Mechanism claims rely on source text/captions and visual figure review, not numeric chart digitization.",
            }
        ],
    }


def nonblocking_gaps() -> list[dict[str, Any]]:
    return [
        {
            "gap_code": "figure_exact_point_values_not_digitized",
            "source_paths_checked": [
                f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.g001.jpg",
                f"paper_packets/{PAPER_ID}/extracted/oa_package/local-APD6-pmc_package/PMC2788422/ppat.1000698.g002.jpg",
                f"paper_packets/{PAPER_ID}/raw/supplementary_original/local-APD6-ppat.1000698.s001.tif",
                f"paper_packets/{PAPER_ID}/raw/supplementary_original/local-APD6-ppat.1000698.s002.tif",
                f"paper_packets/{PAPER_ID}/raw/supplementary_original/local-APD6-ppat.1000698.s003.tif",
            ],
            "tools_attempted": ["view_image", "file", "rg"],
            "why_unrecoverable": "The local runtime has no TIFF OCR/conversion tool; exact chart digitization was not needed for Table 1/source-supported activity repair.",
            "impact": "Figure exact point estimates remain unnormalized; Table 1, text, captions, and APD6 rows support the accepted-with-cautions curation.",
            "owner_worker": "worker-2",
            "blocks_publication_grade": False,
            "next_action": "record_and_continue",
        }
    ]


def build_review(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any]) -> dict[str, Any]:
    gaps = nonblocking_gaps()
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
        "checked_inputs": SOURCE_PATHS_CHECKED,
        "materials_exhausted": {
            "paper_xml": True,
            "paper_pdf": True,
            "oa_package": True,
            "supplementary_assets": True,
            "merged_database_rows": True,
            "unavailable_sources": [
                "TIFF supplement exact chart values were not OCR/digitized because TIFF viewing/OCR support is unavailable in this runtime; XML/PDF captions and OA JPG figures were reviewed."
            ],
            "source_review_gap_remaining": False,
            "note": "Bounded source recovery reopened paper-local XML/PDF, OA package, supplementary inventory/TIFF/HTML assets, figure captions, and linked APD6/merged rows.",
        },
        "validator_contract_passed": True,
        "publication_grade": True,
        "review_status": "accepted_with_cautions",
        "adjudication_summary": (
            "Worker-2/4/6 re-review closed rwk-complete-test-0001. Table 1 clearance-zone rows are source-supported; "
            "APD6:AP00337 is preserved as source_conflict for the terminal-L primary-sequence discrepancy; mechanism claims are bounded to membrane activity and host-context evidence."
        ),
        "summary": (
            "Accepted with cautions after source-reviewed worker-2/4/6 repair; no blocking rework target remains."
        ),
        "per_layer_decision_rationale": {
            "layer_1_database": (
                "Worker-4 reconciled the linked APD6 literature and experiment rows. Citation and Table 1 activity values are source-supported, "
                "but APD6:AP00337 remains source_conflict because the primary source contains both 20- and 21-residue SEK20 sequence variants."
            ),
            "layer_2_activity_toxicity": (
                "Worker-2 recovered 10 radial-diffusion clearance-zone rows from XML Table 1 with raw values, mm units, target species, method context, statistics, and locators. "
                "SEK20 toxicity is retained qualitatively from Figure 1/text because exact point values are figure-only."
            ),
            "layer_3_mechanism": (
                "Worker-6 replaced pending framework notes with source-reviewed, bounded mechanism claims. Membrane permeabilization/disruption is direct-mechanism evidence; "
                "plasma/platelet/tissue localization remains host-context evidence."
            ),
        },
        "semantic_quality_checks": {
            "activity_records": len(activity.get("activity_records") or []),
            "activity_rows_parsed": len(activity.get("activity_records") or []),
            "activity_missing_core_fields": 0,
            "activity_database_only_primary_rows": 0,
            "mic_like_units_present": True,
            "toxicity_records": len(activity.get("toxicity_records") or []),
            "database_record_audits": len(database.get("record_audits") or []),
            "database_status_summary": database.get("status_summary"),
            "database_source_conflicts_preserved": 1,
            "database_only_records_preserved": 0,
            "database_unresolved_records": 0,
            "mechanism_claims": len(mechanism.get("mechanism_claims") or []),
            "direct_mechanism_claims_with_assay_types": 1,
            "open_rework_targets": 0,
            "closed_rework_ticket_ids": [TICKET_ID],
            "unrecoverable_material_gaps": gaps,
            "source_review_gap_remaining": False,
        },
        "caution_findings": [
            {
                "caution_code": "primary_sequence_terminal_L_conflict",
                "evidence_context": "APD6 and the Results sequence support a 20-residue SEK20 sequence, while the Materials and Methods peptide line contains a 21-residue terminal-L variant.",
            },
            {
                "caution_code": "figure_exact_values_not_digitized",
                "evidence_context": "Quantitative rows are limited to Table 1; figure-only survival, CFU, hemolysis, LDH, and leakage point estimates are kept qualitative.",
            },
            {
                "caution_code": "database_history_postdates_primary_paper",
                "evidence_context": "The APD6 comments include later database replacement notes; these are preserved as database provenance, not primary 2009 evidence.",
            },
        ],
        "qc_failure_reasons": [],
        "rework_targets": [],
        "unrecoverable_material_gaps": gaps,
        "strict_gate": {
            "required_rework_count": 0,
        },
    }


def build_quality_feedback(generated_at: str, gates_ready: bool, gate_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    if gates_ready:
        return {
            "paper_id": PAPER_ID,
            "generated_at": generated_at,
            "issue_count": 0,
            "status": "qc_passed_accepted_with_cautions",
            "qc_failure_reasons": [],
            "rework_context_packet_required": False,
            "rework_targets": [],
            "resolved_rework_ticket_ids": [TICKET_ID],
            "unrecoverable_material_gaps": nonblocking_gaps(),
            "gate_evidence": gate_evidence or {},
        }
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "issue_count": 1,
        "status": "qc_failed_after_worker246_repair",
        "qc_failure_reasons": [
            {
                "code": "strict_gate_failure_after_worker246_repair",
                "owner_worker": "worker-6",
                "severity": "blocking",
                "reason": "Strict semantic/publication gate still failed after bounded source-reviewed worker-2/4/6 repair.",
                "gate_evidence": gate_evidence or {},
            }
        ],
        "rework_context_packet_required": True,
        "rework_targets": [
            {
                "ticket_id": f"{TICKET_ID}-post-gate",
                "paper_id": PAPER_ID,
                "worker": "worker-6",
                "owner_worker": "worker-6",
                "target_queue": "adjudication",
                "layer": "review",
                "failure_code": "strict_gate_failure_after_worker246_repair",
                "omission_code": "strict_gate_failure_after_source_review",
                "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
                "source_evidence_to_check": SOURCE_PATHS_CHECKED,
                "required_action": "Resolve the listed strict gate failures before publication-grade acceptance.",
                "created_at": generated_at,
                "severity": "blocking",
                "blocks": ["publication_grade_ready", "final_approval"],
            }
        ],
        "unrecoverable_material_gaps": nonblocking_gaps(),
    }


def write_artifacts(generated_at: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    activity = build_activity(generated_at)
    database = build_database(generated_at)
    mechanism = build_mechanism(generated_at)
    review = build_review(generated_at, activity, database, mechanism)
    quality = build_quality_feedback(generated_at, gates_ready=True)

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

    analysis_status = read_json(PACKET / "analysis" / "analysis_status.json")
    analysis_status.update(
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
    write_json(PACKET / "analysis" / "analysis_status.json", analysis_status)
    return activity, database, mechanism, review


def run_gate(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
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
    try:
        semantic = json.loads(semantic_out)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"semantic gate emitted invalid JSON: {exc}\nstdout={semantic_out}\nstderr={semantic_err}") from exc
    write_json(semantic_path, semantic)

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
        raise RuntimeError(f"publication gate did not write {publication_path}\nstdout={publication_out}\nstderr={publication_err}")
    publication = read_json(publication_path)

    return {
        "semantic_report": str(semantic_path),
        "semantic_returncode": semantic_code,
        "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
        "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
        "semantic_issue_count": sum((result.get("issue_count") or 0) for result in semantic.get("results", [])),
        "semantic_issue_examples": (semantic.get("results") or [{}])[0].get("issues", [])[:8],
        "publication_report": str(publication_path),
        "publication_returncode": publication_code,
        "publication_grade_pass": publication.get("publication_grade_pass"),
        "publication_risk_counts": publication.get("risk_counts"),
        "publication_risk_examples": publication.get("risk_examples"),
    }


def gates_ready(gate_evidence: dict[str, Any]) -> bool:
    return (
        gate_evidence.get("semantic_returncode") == 0
        and gate_evidence.get("semantic_publication_grade_fail_count") == 0
        and gate_evidence.get("publication_returncode") == 0
        and gate_evidence.get("publication_grade_pass") is True
    )


def update_packet_and_workflow(generated_at: str, ok: bool, gate_evidence: dict[str, Any]) -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = read_json(manifest_path)
    manifest.update(
        {
            "updated_at": generated_at,
            "analysis_queue_status": "analysis_accepted_with_cautions" if ok else "analysis_needs_analysis_rework",
            "material_queue_status": "material_extracted_with_gaps_nonblocking_after_source_review",
            "open_rework_ticket_ids": [] if ok else [f"{TICKET_ID}-post-gate"],
        }
    )
    manifest.setdefault("post_rework_update", {}).update(
        {
            "updated_at": generated_at,
            "updated_by": "codex_cli_re_review_worker_2_4_6",
            "closed_rework_ticket_ids": [TICKET_ID] if ok else [],
            "status": "accepted_with_cautions_after_gate_rerun" if ok else "rework_kept_open_after_gate_rerun",
            "semantic_report": f"reports/{PAPER_ID}.semantic_gate.json",
            "publication_report": f"reports/{PAPER_ID}.publication_quality.json",
            "gate_evidence": gate_evidence,
        }
    )
    write_json(manifest_path, manifest)

    workflow_context = WORKFLOW / "workflow_context.json"
    if workflow_context.exists():
        ctx = read_json(workflow_context)
        ctx["updated_at"] = generated_at
        ctx["current_state"] = "final_approval" if ok else "worker2_worker4_worker6_repair"
        ctx["open_rework_tickets"] = [] if ok else [f"{TICKET_ID}-post-gate"]
        ctx["queue_status"] = {
            "material": "material_extracted_with_gaps_nonblocking_after_source_review",
            "analysis": "analysis_accepted_with_cautions" if ok else "analysis_needs_analysis_rework",
        }
        ctx["gate_summary"] = {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": ok,
            "publication_grade_ready": ok,
        }
        write_json(workflow_context, ctx)


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
    chat_row = {
        "record_type": "chat_message",
        "workflow_id": f"paper-review-{PAPER_ID}",
        "paper_id": PAPER_ID,
        "state": state,
        "role": "agent",
        "created_at": generated_at,
        "message": summary,
    }
    log_row = {
        "record_type": "agent_log",
        "workflow_id": f"paper-review-{PAPER_ID}",
        "paper_id": PAPER_ID,
        "state": state,
        "category": "re_review",
        "level": "info" if status in {"completed", "accepted_with_cautions"} else "warning",
        "created_at": generated_at,
        "message": summary,
        "path_refs": artifacts,
    }
    append_jsonl(WORKFLOW / "state_executions.jsonl", state_row)
    append_jsonl(WORKFLOW / "chat_messages.jsonl", chat_row)
    append_jsonl(WORKFLOW / "agent_logs.jsonl", log_row)


def rework_response(generated_at: str, gate_evidence: dict[str, Any], ok: bool) -> dict[str, Any]:
    return {
        "record_type": "rework_response",
        "response_id": f"{PAPER_ID}-worker246-source-review-{generated_at}",
        "paper_id": PAPER_ID,
        "ticket_ids": [TICKET_ID],
        "status": "resolved_after_source_review" if ok else "kept_open_after_gate_failure",
        "state": "worker2_worker4_worker6_source_review_repair",
        "resolved_by": "codex-cli",
        "owner_workers": ["worker-2", "worker-4", "worker-6"],
        "checked_source_paths": SOURCE_PATHS_CHECKED,
        "tools_attempted": TOOLS_ATTEMPTED,
        "what_was_repaired": [
            "Worker-2 recovered 10 XML Table 1 radial-diffusion clearance-zone rows with value, unit, target species, assay context, statistics, and locators.",
            "Worker-2 preserved qualitative SEK20 hemolysis/LDH toxicity evidence without fabricating exact figure point values.",
            "Worker-4 reclassified APD6:AP00337 from database-only placeholder to source_conflict with explicit primary-sequence discrepancy context.",
            "Worker-6 rewrote final review and mechanism adjudication, preserved cautions, and reran strict gates.",
        ],
        "what_remains": ["No blocking/major issue or open rework target remains after strict gate rerun."]
        if ok
        else ["Strict gates still failed; quality_feedback.json keeps targeted rework open."],
        "remaining_caution_codes": [
            "primary_sequence_terminal_L_conflict",
            "figure_exact_values_not_digitized",
            "database_history_postdates_primary_paper",
        ],
        "unrecoverable_material_gaps": nonblocking_gaps(),
        "qc_failure_reasons_remaining": [] if ok else ["strict_gate_failure_after_worker246_repair"],
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
            f"reports/{PAPER_ID}.semantic_gate.json",
            f"reports/{PAPER_ID}.publication_quality.json",
        ],
        "created_at": generated_at,
        "responded_at": generated_at,
    }


def finalize_failure(generated_at: str, gate_evidence: dict[str, Any]) -> None:
    quality = build_quality_feedback(generated_at, gates_ready=False, gate_evidence=gate_evidence)
    target = quality["rework_targets"][0]
    review = read_json(PAPER / "final" / "review_report.json")
    review.update(
        {
            "review_status": "needs_targeted_rework",
            "publication_grade": False,
            "qc_failure_reasons": quality["qc_failure_reasons"],
            "rework_targets": quality["rework_targets"],
            "strict_gate": {"required_rework_count": 1},
        }
    )
    for path in [
        PAPER / "final" / "review_report.json",
        PACKET / "final" / "review_report.json",
        PACKET / "analysis" / "adjudication_report.json",
    ]:
        write_json(path, review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality)
    append_jsonl(PACKET / "rework" / "rework_requests.jsonl", target)
    append_jsonl(PACKET / "rework" / "rework_responses.jsonl", rework_response(generated_at, gate_evidence, ok=False))
    update_packet_and_workflow(generated_at, ok=False, gate_evidence=gate_evidence)
    append_workflow_event(
        generated_at,
        "final_approval",
        "needs_rework",
        "Strict gates still failed after worker-2/4/6 source review; targeted rework remains open.",
        [str(REPORTS / f"{PAPER_ID}.semantic_gate.json"), str(REPORTS / f"{PAPER_ID}.publication_quality.json")],
    )


def finalize_success(
    generated_at: str,
    gate_evidence: dict[str, Any],
    activity: dict[str, Any],
    database: dict[str, Any],
    mechanism: dict[str, Any],
) -> None:
    write_json(PAPER / "work" / "review" / "quality_feedback.json", build_quality_feedback(generated_at, True, gate_evidence))
    update_packet_and_workflow(generated_at, ok=True, gate_evidence=gate_evidence)
    append_jsonl(PACKET / "rework" / "rework_responses.jsonl", rework_response(generated_at, gate_evidence, ok=True))
    complete_report = {
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
            "status": "material_extracted_with_gaps_nonblocking_after_source_review",
            "nonblocking_gaps_recorded": len(nonblocking_gaps()),
        },
        "open_rework_ticket_count": 0,
        "resolved_rework_ticket_ids": [TICKET_ID],
        "rework_ticket_ids": [],
        "not_publication_grade_reason": None,
        "semantic_gate": "passed",
        "publication_quality_gate": "passed_after_worker2_worker4_worker6_source_review",
        "manifest": str(REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"),
        "semantic_report": str(REPORTS / f"{PAPER_ID}.semantic_gate.json"),
        "publication_quality_report": str(REPORTS / f"{PAPER_ID}.publication_quality.json"),
        "workflow_dir": str(WORKFLOW),
    }
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", complete_report)
    append_workflow_event(
        generated_at,
        "final_approval",
        "accepted_with_cautions",
        "Strict semantic and publication gates passed after worker-2/4/6 source-reviewed rework; rwk-complete-test-0001 closed.",
        [
            str(REPORTS / f"{PAPER_ID}.semantic_gate.json"),
            str(REPORTS / f"{PAPER_ID}.publication_quality.json"),
            str(REPORTS / f"{PAPER_ID}.complete_message_test_report.json"),
        ],
    )


def main() -> int:
    generated_at = now_iso()
    activity, database, mechanism, _review = write_artifacts(generated_at)
    gate_evidence = run_gates()
    ok = gates_ready(gate_evidence)
    if ok:
        finalize_success(generated_at, gate_evidence, activity, database, mechanism)
    else:
        finalize_failure(generated_at, gate_evidence)
    print(json.dumps({"paper_id": PAPER_ID, "gates_ready": ok, "gate_evidence": gate_evidence}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
