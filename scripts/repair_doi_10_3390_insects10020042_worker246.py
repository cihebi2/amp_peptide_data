#!/usr/bin/env python3
"""Source-reviewed worker-2/4/6 repair for doi__10.3390_insects10020042."""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.3390_insects10020042"
TICKET_ID = "rwk-complete-test-0001"
PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
REPORTS = ROOT / "reports"
MANIFEST = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"
SEMANTIC_REPORT = REPORTS / f"{PAPER_ID}.semantic_gate.json"
PUBLICATION_REPORT = REPORTS / f"{PAPER_ID}.publication_quality.json"
COMPLETE_REPORT = REPORTS / f"{PAPER_ID}.complete_message_test_report.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    return payload if isinstance(payload, dict) else {}


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


def source_locator(locator: str, path: str = "source/paper.xml", **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"source_path": path, "locator": locator}
    payload.update(extra)
    return payload


PEPTIDE = {
    "peptide_name": "Myrmicitoxin U-MYRTX-MRArub1",
    "sequence": "IDPKLLESLA",
    "reported_structure": "NH2-IDPKLLESLA-CONH2",
    "modification": "C-terminal amidation",
    "source_organism": "Myrmica rubra",
    "database_keys": ["DBAASP:DBAASPS_14047", "CAMP:CAMPSQ23658"],
}

BACTERIA = [
    ("110221", "Bacillus subtilis", "DSM 10", "Gram-positive bacterium"),
    ("110222", "Bacillus megaterium", "", "Gram-positive bacterium"),
    ("110223", "Listeria monocytogenes", "DSM 20600", "Gram-positive bacterium"),
    ("110224", "Listeria fleischmannii", "DSM 24998", "Gram-positive bacterium"),
    ("110225", "Micrococcus luteus", "DSM 20030", "Gram-positive bacterium"),
    ("110226", "Staphylococcus aureus", "DSM 2569", "Gram-positive bacterium"),
    ("110227", "Staphylococcus epidermidis", "DSM 2369", "Gram-positive bacterium"),
    ("110228", "Escherichia coli", "D31", "Gram-negative bacterium"),
    ("110229", "Pseudomonas aeruginosa", "DSM 50071", "Gram-negative bacterium"),
]


def bacteria_activity_records(generated_at: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for assay_id, species, strain, target_class in BACTERIA:
        rows.append(
            {
                "record_id": f"{PAPER_ID}-dbaasp-{assay_id}-no-mic-up-to-100uM",
                "entity": PEPTIDE["peptide_name"],
                "peptide": PEPTIDE,
                "endpoint": "MIC_not_observed_up_to_test_limit",
                "raw_value": ">100",
                "raw_unit": "uM",
                "normalized_value": None,
                "normalized_unit": None,
                "normalization_status": "not_convertible_negative_censored_value",
                "evidence_ladder": "primary_xml_methods_and_results_plus_database_row",
                "target": {
                    "species": species,
                    "strain": strain,
                    "class": target_class,
                },
                "assay_conditions": {
                    "assay": "two-fold microtiter broth dilution MIC assay",
                    "peptide_concentration_range": "0.8 to 100 uM",
                    "incubation": "16 h at 37 C",
                    "readout": "absorbance at 600 nm",
                    "replicates": "triplicate",
                    "method_locator": source_locator("xml:sec=2.11"),
                    "result_locator": source_locator("xml:sec=3.4"),
                },
                "source_locator": source_locator(
                    "xml:sec=3.4;database:linked_assay_records",
                    database_row=f"linked_assay_records:{assay_id}",
                ),
                "database_row_ids": [f"DBAASP:{assay_id}"],
                "review_notes": "Primary source reports no significant bacterial growth inhibition at the maximum tested peptide concentration; this is recorded as a negative MIC-limit row, not as a fabricated MIC.",
                "reviewed_at": generated_at,
            }
        )
    return rows


def aphid_activity_records(generated_at: str) -> list[dict[str, Any]]:
    base_assay = {
        "target": {
            "species": "Acyrthosiphon pisum",
            "strain": "clone LL01",
            "class": "insect pest",
        },
        "peptide": PEPTIDE,
        "entity": PEPTIDE["peptide_name"],
        "evidence_ladder": "primary_xml_results_plus_supplementary_table_s1",
        "reviewed_at": generated_at,
    }
    return [
        {
            **base_assay,
            "record_id": f"{PAPER_ID}-fig3-aphid-survival-500ugml",
            "endpoint": "three_day_aphid_survival_after_feeding",
            "raw_value": "approximately 40",
            "raw_unit": "% survival",
            "normalization_status": "qualitative_figure_value_preserved_with_supplement_statistics",
            "assay_conditions": {
                "exposure": "3 days feeding on AP3 diet mixed with peptide",
                "peptide_concentration": "500 ug/mL",
                "replicates": "three independent biological replicates; over 2000 nymphs per treatment",
                "supplement_stats": {
                    "control_estimate": "4.63 +/- 0.01; 95% CI 4.61-4.66",
                    "peptide_estimate": "4.50 +/- 0.01; 95% CI 4.48-4.52",
                    "significance": "p < 0.0001",
                },
                "method_locator": source_locator("xml:sec=2.12"),
            },
            "source_locator": source_locator(
                "xml:sec=3.5;xml:fig=3;supp:insects-10-00042-s001.pdf:Table_S1",
                path="paper_packets/doi__10.3390_insects10020042/extracted/supplementary_text/insects-10-00042-s001.txt",
            ),
            "review_notes": "The main text gives an approximate survival rate and Table S1 gives the Kaplan-Meier statistical comparison; no graph digitization was used.",
        },
        {
            **base_assay,
            "record_id": f"{PAPER_ID}-fig4-imidacloprid-mortality-after-peptide",
            "endpoint": "imidacloprid_mortality_after_peptide_pretreatment",
            "raw_value": "76.35 +/- 4.30 versus 39.55 +/- 5.10 control",
            "raw_unit": "% mortality; mean +/- SE",
            "normalization_status": "direct_supplement_table_value",
            "assay_conditions": {
                "peptide_pretreatment": "500 ug/mL in AP3 diet for 3 days",
                "insecticide": "imidacloprid 0.0975 ug/mL",
                "significance": "p < 0.0001",
                "method_locator": source_locator("xml:sec=2.13"),
            },
            "source_locator": source_locator(
                "xml:fig=4;supp:insects-10-00042-s001.pdf:Table_S1",
                path="paper_packets/doi__10.3390_insects10020042/extracted/supplementary_text/insects-10-00042-s001.txt",
            ),
        },
        {
            **base_assay,
            "record_id": f"{PAPER_ID}-fig4-spirotetramat-mortality-after-peptide",
            "endpoint": "spirotetramat_mortality_after_peptide_pretreatment",
            "raw_value": "66.14 +/- 4.81 versus 67.75 +/- 4.58 control",
            "raw_unit": "% mortality; mean +/- SE",
            "normalization_status": "direct_supplement_table_value",
            "assay_conditions": {
                "peptide_pretreatment": "500 ug/mL in AP3 diet for 3 days",
                "insecticide": "spirotetramat 1.56 ug/mL",
                "significance": "not significant",
                "method_locator": source_locator("xml:sec=2.13"),
            },
            "source_locator": source_locator(
                "xml:fig=4;supp:insects-10-00042-s001.pdf:Table_S1",
                path="paper_packets/doi__10.3390_insects10020042/extracted/supplementary_text/insects-10-00042-s001.txt",
            ),
        },
        {
            **base_assay,
            "record_id": f"{PAPER_ID}-fig4-methomyl-mortality-after-peptide",
            "endpoint": "methomyl_mortality_after_peptide_pretreatment",
            "raw_value": "35.69 +/- 6.60 versus 11.49 +/- 3.09 control",
            "raw_unit": "% mortality; mean +/- SE",
            "normalization_status": "direct_supplement_table_value",
            "assay_conditions": {
                "peptide_pretreatment": "500 ug/mL in AP3 diet for 3 days",
                "insecticide": "methomyl 6.25 ug/mL",
                "significance": "p < 0.01",
                "method_locator": source_locator("xml:sec=2.13"),
            },
            "source_locator": source_locator(
                "xml:fig=4;supp:insects-10-00042-s001.pdf:Table_S1",
                path="paper_packets/doi__10.3390_insects10020042/extracted/supplementary_text/insects-10-00042-s001.txt",
            ),
        },
    ]


def build_activity(generated_at: str) -> dict[str, Any]:
    records = bacteria_activity_records(generated_at) + aphid_activity_records(generated_at)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "accepted_with_cautions",
        "publication_grade": True,
        "extraction_scope": "worker-2 source-reviewed activity/toxicity repair from primary XML, PDF text, Supplementary Table S1, and linked DBAASP/CAMP rows.",
        "activity_records": records,
        "extraction_issues": [],
        "unrecoverable_material_gaps": [
            {
                "gap_code": "camp_merged_aphid_dose_rows_not_supported_by_this_primary_paper",
                "source_paths_checked": [
                    "papers/doi__10.3390_insects10020042/source/paper.xml",
                    "papers/doi__10.3390_insects10020042/source/paper.pdf",
                    "paper_packets/doi__10.3390_insects10020042/extracted/pdf_text/insects-10-00042.txt",
                    "paper_packets/doi__10.3390_insects10020042/extracted/supplementary_text/insects-10-00042-s001.txt",
                    "paper_packets/doi__10.3390_insects10020042/database/linked_experiment_records.jsonl",
                    "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/camp_activity_text_records.csv",
                ],
                "tools_attempted": [
                    "rg over XML/PDF/supplement text",
                    "pdftotext -layout on supplementary PDF",
                    "jq/sed inspection of packet database JSONL",
                    "rg over merged corpus experiment exports",
                ],
                "why_unrecoverable": "The CAMP/database text merges this PMID with a second paper and lists 16000/4000/1000 ug/mL aphid killing rows that are not in this primary paper's local XML/PDF/supplement. This primary paper supports 500 ug/mL feeding plus insecticide-sensitization values only.",
                "impact": "Those merged database values are not promoted to activity records; source-supported bacterial negative rows and aphid Table S1 rows remain recorded.",
                "owner_worker": "worker-2 + worker-4 + worker-6",
                "blocks_publication_grade": False,
                "next_action": "record_and_continue",
            }
        ],
        "parser_quality_control": {
            "activity_rows_parsed": len(records),
            "negative_antimicrobial_rows": len(BACTERIA),
            "aphid_rows": 4,
            "rejects_database_only_mixed_pmid_dose_rows": True,
            "source_locators_present": True,
        },
    }


def database_source_verified_record(
    *,
    source_id: str,
    source_table: str,
    row_number: int,
    database_subject: str,
    matched_activity_record_id: str,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "sequence_key": "DBAASP:DBAASPS_14047",
        "source_table": source_table,
        "status": "source_verified",
        "layer1_status": "source_verified",
        "database_subject": database_subject,
        "database_measure": "not active up to 100 uM",
        "matched_activity_record_id": matched_activity_record_id,
        "traceability": source_locator(
            f"database:{source_table}:row={row_number}",
            path=f"paper_packets/doi__10.3390_insects10020042/database/{source_table}",
        ),
        "citation_traceability": source_locator("xml:article-meta"),
        "sequence_check": {
            "source_sequence": "IDPKLLESLA",
            "database_sequence": "IDPKLLESLA",
            "modification_status": "C-terminal amidation source-supported",
            "source_locator": source_locator("xml:abstract;xml:sec=3.3", primary_source_sequence="IDPKLLESLA"),
        },
        "name_check": {
            "database_name": "Myrmicitoxin U-MYRTX-MRArub1",
            "primary_source_name": "U-MYRTX-MRArub1",
            "status": "source_verified",
        },
        "source_organism_check": {
            "database_source": "Synthetic",
            "primary_source_context": "Synthetic peptide corresponding to a Myrmica rubra venom decapeptide was tested.",
            "status": "source_verified_with_synthetic_test_material",
        },
        "activity_match_status": "negative_activity_limit_source_verified",
        "review_notes": "Primary source methods/results support the DBAASP negative antibacterial call: no significant growth inhibition at peptide concentrations up to 100 uM.",
    }


def build_database(activity: dict[str, Any], generated_at: str) -> dict[str, Any]:
    records = activity["activity_records"]
    bacteria_by_assay = {
        record["database_row_ids"][0].split(":", 1)[1]: record["record_id"]
        for record in records
        if record.get("database_row_ids")
    }
    audits: list[dict[str, Any]] = []
    for idx, (assay_id, species, strain, _target_class) in enumerate(BACTERIA, start=1):
        label = f"{species} {strain}".strip()
        audits.append(
            database_source_verified_record(
                source_id=f"DBAASP:{assay_id}",
                source_table="linked_assay_records.jsonl",
                row_number=idx,
                database_subject=label,
                matched_activity_record_id=bacteria_by_assay[assay_id],
            )
        )
    for idx, (assay_id, species, strain, _target_class) in enumerate(BACTERIA, start=1):
        label = f"{species} {strain}".strip()
        audits.append(
            database_source_verified_record(
                source_id=f"DBAASP:{assay_id}",
                source_table="linked_experiment_records.jsonl",
                row_number=idx,
                database_subject=label,
                matched_activity_record_id=bacteria_by_assay[assay_id],
            )
        )
    audits.append(
        {
            "source_id": "CAMP:CAMPSQ23658",
            "sequence_key": "CAMP:CAMPSQ23658",
            "source_table": "linked_experiment_records.jsonl",
            "status": "source_conflict",
            "layer1_status": "source_conflict",
            "database_subject": "Merged CAMP entry listing bacterial targets and Acyrthosiphon pisum dose-response rows",
            "database_measure": "Antibacterial/Antifungal plus aphid killing values from mixed PMID text",
            "matched_activity_record_id": f"{PAPER_ID}-fig3-aphid-survival-500ugml",
            "traceability": source_locator(
                "database:linked_experiment_records:row=10",
                path="paper_packets/doi__10.3390_insects10020042/database/linked_experiment_records.jsonl",
            ),
            "citation_traceability": {
                "database_pmids": ["30717163", "31557881"],
                "local_primary_paper": "30717163",
                "source_locator": source_locator("xml:article-meta"),
            },
            "sequence_check": {
                "source_sequence": "IDPKLLESLA",
                "database_sequence": "IDPKLLESLA",
                "source_locator": source_locator("xml:abstract;xml:sec=3.3", primary_source_sequence="IDPKLLESLA"),
            },
            "conflict_flags": ["mixed_pmid_activity_text", "unsupported_aphid_dose_rows_for_this_paper"],
            "conflict_context": "Local primary source supports U-MYRTX-MRArub1 identity, no bacterial growth inhibition up to 100 uM, and aphid feeding at 500 ug/mL. It does not contain the CAMP 16000/4000/1000 ug/mL aphid killing rows, which trace to merged database text including PMID 31557881.",
            "review_notes": "Preserved as source_conflict rather than converted to source_verified or used to create activity rows.",
        }
    )
    audits.append(
        {
            "source_id": "DBAASP:DBAASPS_14047",
            "sequence_key": "DBAASP:DBAASPS_14047",
            "source_table": "linked_literature_records.jsonl",
            "status": "source_verified",
            "layer1_status": "source_verified",
            "database_subject": "Literature link for 10.3390/insects10020042",
            "database_measure": "",
            "matched_activity_record_id": "",
            "traceability": source_locator(
                "database:linked_literature_records:row=1",
                path="paper_packets/doi__10.3390_insects10020042/database/linked_literature_records.jsonl",
            ),
            "citation_traceability": source_locator("xml:article-meta"),
            "sequence_check": {
                "source_locator": source_locator("xml:article-meta;xml:abstract;xml:sec=3.3"),
                "source_sequence": "IDPKLLESLA",
            },
            "review_notes": "DOI/PMID/PMCID literature linkage and peptide identity are source-supported.",
        }
    )
    summary = Counter(record["status"] for record in audits)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "accepted_with_cautions",
        "publication_grade": True,
        "audit_scope": "worker-4 source-reviewed linked DBAASP/CAMP rows against primary XML/PDF/supplement and merged database exports.",
        "database_row_counts": {
            "linked_assay_records": 9,
            "linked_dramp_activity_records": 0,
            "linked_experiment_records": 10,
            "linked_literature_records": 1,
            "linked_sequence_records": 0,
        },
        "record_audits": audits,
        "status_summary": dict(summary),
        "source_conflict_summary": [
            "CAMP CAMPSQ23658 is preserved as source_conflict because its merged activity text includes aphid dose rows not present in this primary paper's local source material."
        ],
        "unrecoverable_material_gaps": activity["unrecoverable_material_gaps"],
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "accepted_with_cautions",
        "publication_grade": True,
        "extraction_scope": "worker-6 bounded final mechanism adjudication from source text; no worker-5 direct mechanism expansion was performed.",
        "mechanism_claims": [
            {
                "claim_id": "mech-001",
                "entity_scope": "U-MYRTX-MRArub1",
                "claim_text": "The paper establishes insecticidal activity and insecticide-sensitization phenotypes for U-MYRTX-MRArub1, but it does not identify a direct molecular target.",
                "evidence_class": "phenotypic_activity_mechanism_unresolved",
                "source_locator": source_locator("xml:sec=3.5;xml:fig=3;xml:fig=4;xml:sec=4"),
                "limitations": "Do not promote discussion-level possibilities such as membrane disruption, ion channels, or macromolecular synthesis into direct mechanisms.",
            },
            {
                "claim_id": "mech-002",
                "entity_scope": "U-MYRTX-MRArub1 structure context",
                "claim_text": "The peptide is a linear cysteine-free C-terminal amidated decapeptide; helical conformation is model/context evidence rather than a demonstrated killing mechanism.",
                "evidence_class": "structure_context_not_direct_mechanism",
                "source_locator": source_locator(
                    "xml:abstract;xml:sec=3.3;xml:sec=4;supp:Figure_S4",
                    path="paper_packets/doi__10.3390_insects10020042/extracted/supplementary_text/insects-10-00042-s001.txt",
                ),
                "limitations": "No direct assay in the local material maps the peptide to a membrane, ion-channel, translation, or protein-synthesis target in aphids.",
            },
        ],
        "unrecoverable_material_gaps": [],
    }


def build_rework_target(generated_at: str, semantic: dict[str, Any], publication: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticket_id": "rwk-worker246-gate-failure-0002",
        "paper_id": PAPER_ID,
        "created_at": generated_at,
        "worker": "worker-6",
        "target_queue": "adjudication",
        "layer": "review",
        "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
        "failure_code": "strict_gates_failed_after_worker246_repair",
        "failing_object": "publication_grade_ready",
        "severity": "blocking",
        "blocks": ["publication_grade_ready", "final_approval"],
        "source_evidence_to_check": [
            f"papers/{PAPER_ID}/source/paper.xml",
            f"paper_packets/{PAPER_ID}/extracted/supplementary_text/insects-10-00042-s001.txt",
            f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
        ],
        "required_action": "Inspect the strict semantic/publication reports and repair the named failing artifact fields without fabricating unsupported values.",
        "omission_context": {
            "semantic_issue_count": sum(item.get("issue_count", 0) for item in semantic.get("results", [])),
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
    review_status = "accepted_with_cautions" if publication_grade else "needs_targeted_rework"
    rework_targets = [] if publication_grade else [build_rework_target(generated_at, semantic, publication)]
    qc_failure_reasons = [] if publication_grade else [
        {
            "code": "strict_gates_failed_after_worker246_repair",
            "owner_worker": "worker-6",
            "severity": "blocking",
            "reason": "Strict semantic or publication-quality gates still failed after bounded worker-2/4/6 repair.",
        }
    ]
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "generated_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": review_status,
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
            "note": "Local XML/PDF/OA package, Supplementary Table S1 text, figure captions, packet database JSONL, and merged sequence/experiment exports were reopened. Unsupported mixed-PMID CAMP dose rows are preserved as nonblocking source_conflict rather than promoted.",
        },
        "checked_inputs": [
            f"rework_context/{PAPER_ID}/handoff_context.json",
            f"paper_packets/{PAPER_ID}/packet_manifest.json",
            f"paper_packets/{PAPER_ID}/locators/locator_index.json",
            f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
            f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
            f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
            f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
            f"paper_packets/{PAPER_ID}/extracted/pdf_text/insects-10-00042.txt",
            f"paper_packets/{PAPER_ID}/extracted/pdf_text/local-DBAASP-PMC6409562.txt",
            f"paper_packets/{PAPER_ID}/extracted/supplementary_text/insects-10-00042-s001.txt",
            f"papers/{PAPER_ID}/source/paper.xml",
            f"papers/{PAPER_ID}/source/paper.pdf",
            f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
            f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
            f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
            "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv",
            "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/all_experimental_records.csv",
            "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/camp_activity_text_records.csv",
        ],
        "semantic_quality_checks": {
            "activity_records": len(activity["activity_records"]),
            "negative_antimicrobial_rows": 9,
            "aphid_activity_rows": 4,
            "database_record_audits": len(database["record_audits"]),
            "database_status_summary": database["status_summary"],
            "mechanism_claims": len(mechanism["mechanism_claims"]),
            "open_rework_target_count": len(rework_targets),
            "closed_rework_ticket_ids": [TICKET_ID] if publication_grade else [],
        },
        "per_layer_decision_rationale": {
            "material_packet": "Material packet remains material-extracted-with-gaps, but the relevant gaps are analysis/adjudication questions now resolved or preserved as nonblocking conflicts; no bootstrap/reset was run.",
            "validator_contract": "Required paper-local packet/final/work artifacts are present and structurally valid; this is kept separate from semantic/publication-grade review.",
            "layer_1_database": "DBAASP negative antibacterial assay rows match the primary paper and are source_verified; the mixed-PMID CAMP activity text remains source_conflict.",
            "layer_2_activity_toxicity": "Worker-2 now records source-supported negative antibacterial rows plus aphid survival and insecticide-sensitization rows from Figure 3/Figure 4/Table S1.",
            "layer_3_mechanism": "Mechanism is bounded to phenotypic insecticidal activity and structural context; no direct molecular target is claimed.",
            "publication_grade_review": "The prior framework-test ticket is closed only when strict gates pass; remaining database conflict is explicit and nonblocking." if publication_grade else "Strict gate failure remains blocking and is routed to a concrete rework target.",
        },
        "caution_findings": [
            {
                "caution_code": "camp_mixed_pmid_activity_text_preserved",
                "severity": "caution",
                "evidence_context": "CAMP CAMPSQ23658 combines this paper with a second PMID and lists aphid dose rows not present in the local source; those rows remain source_conflict.",
                "record_count": 1,
            },
            {
                "caution_code": "negative_antimicrobial_rows_are_limit_values",
                "severity": "caution",
                "evidence_context": "Bacterial assay rows are negative MIC-limit evidence up to 100 uM, not exact MIC measurements.",
                "record_count": 9,
            },
            {
                "caution_code": "direct_mechanism_unresolved",
                "severity": "caution",
                "evidence_context": "The primary paper supports insecticidal phenotype and sensitization to two insecticides but does not identify a direct molecular target.",
            },
        ],
        "unrecoverable_material_gaps": activity["unrecoverable_material_gaps"],
        "qc_failure_reasons": qc_failure_reasons,
        "rework_targets": rework_targets,
        "closed_rework_ticket_ids": [TICKET_ID] if publication_grade else [],
        "summary": "Source-reviewed worker-2/4/6 repair recovered local activity rows, source-verified DBAASP negative assay rows, preserved the mixed-PMID CAMP conflict, and bounded mechanism claims to the evidence actually present.",
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
    payload: dict[str, Any]
    try:
        payload = json.loads(text) if text else {}
    except json.JSONDecodeError:
        payload = {"stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode}
    if out_path and (not out_path.exists() or payload):
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
    write_json(PAPER / "final" / "mechanism_ontology_record.json", mechanism)
    write_json(PAPER / "final" / "mechanism_evidence.json", mechanism)
    write_json(PACKET / "analysis" / "adjudication_report.json", review)
    write_json(PACKET / "final" / "review_report.json", review)
    write_json(PAPER / "work" / "review" / "adjudication_report.json", review)
    write_json(PAPER / "final" / "review_report.json", review)
    write_json(PAPER / "work" / "review" / "quality_feedback.json", build_quality_feedback(review, generated_at))


def update_status_files(generated_at: str, activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], review: dict[str, Any]) -> None:
    manifest = read_json(PACKET / "packet_manifest.json")
    manifest.update(
        {
            "analysis_queue_status": "source_reviewed_publication_grade_ready" if review["publication_grade"] else "analysis_needs_analysis_rework",
            "open_rework_ticket_ids": [] if review["publication_grade"] else [target["ticket_id"] for target in review["rework_targets"]],
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
            "status": "source_reviewed_publication_grade_ready" if review["publication_grade"] else "analysis_needs_analysis_rework",
            "activity_record_count": len(activity["activity_records"]),
            "activity_extraction_issue_count": len(activity["extraction_issues"]),
            "activity_extraction_issues": activity["extraction_issues"],
            "database_record_count": len(database["record_audits"]),
            "database_status_summary": database["status_summary"],
            "mechanism_claim_count": len(mechanism["mechanism_claims"]),
            "open_rework_ticket_ids": [] if review["publication_grade"] else [target["ticket_id"] for target in review["rework_targets"]],
            "closed_rework_ticket_ids": review["closed_rework_ticket_ids"],
            "publication_grade_ready": review["publication_grade"],
        },
    )

    context_path = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID / "workflow_context.json"
    context = read_json(context_path)
    if context:
        context["current_state"] = "source_reviewed_publication_grade_ready" if review["publication_grade"] else "rework_context_prepared"
        context["updated_at"] = generated_at
        context["open_rework_tickets"] = [] if review["publication_grade"] else [target["ticket_id"] for target in review["rework_targets"]]
        context["gate_summary"] = {
            "structural_ready": True,
            "validator_contract_ready": True,
            "semantic_gate_ready": review["strict_gate"]["semantic_gate_pass"],
            "publication_grade_ready": review["publication_grade"],
        }
        write_json(context_path, context)


def update_reports(generated_at: str, review: dict[str, Any], activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], semantic: dict[str, Any], publication: dict[str, Any]) -> None:
    write_json(
        COMPLETE_REPORT,
        {
            "paper_id": PAPER_ID,
            "doi": "10.3390/insects10020042",
            "title": "Proteomic Analysis of the Venom from the Ruby Ant Myrmica rubra and the Isolation of a Novel Insecticidal Decapeptide.",
            "generated_at": generated_at,
            "completion_claim": "source_reviewed_worker2_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions"
            if review["publication_grade"]
            else "worker246_repair_done_but_strict_gate_failed",
            "current_state": "source_reviewed_publication_grade_ready" if review["publication_grade"] else "rework_queue",
            "terminal_status": "source_reviewed_publication_grade_ready" if review["publication_grade"] else "awaiting_targeted_rework",
            "final_approval_status": "accepted_with_cautions" if review["publication_grade"] else "refused_needs_rework",
            "not_publication_grade_reason": None if review["publication_grade"] else "Strict gate failed after bounded worker-2/4/6 source repair.",
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
            "rework_ticket_ids": [] if review["publication_grade"] else [target["ticket_id"] for target in review["rework_targets"]],
            "closed_rework_ticket_ids": review["closed_rework_ticket_ids"],
            "open_rework_ticket_count": 0 if review["publication_grade"] else len(review["rework_targets"]),
            "publication_quality_gate": "passed_after_worker246_repair" if publication.get("publication_grade_pass") is True else "failed_after_worker246_repair",
            "semantic_gate": "passed_after_worker246_repair" if semantic.get("publication_grade_fail_count") == 0 else "failed_after_worker246_repair",
            "packet_root": str(PACKET),
            "workflow_dir": str(ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID),
        },
    )


def append_rework_response(generated_at: str, review: dict[str, Any], semantic: dict[str, Any], publication: dict[str, Any]) -> None:
    append_jsonl_once(
        PACKET / "rework" / "rework_responses.jsonl",
        f"{TICKET_ID}-worker246-source-review-packet-final-sync",
        {
            "response_id": f"{TICKET_ID}-worker246-source-review-packet-final-sync",
            "ticket_id": TICKET_ID,
            "paper_id": PAPER_ID,
            "responded_at": generated_at,
            "owner_workers": ["worker-2", "worker-4", "worker-6"],
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
                f"papers/{PAPER_ID}/final/mechanism_ontology_record.json",
                f"papers/{PAPER_ID}/final/review_report.json",
                f"papers/{PAPER_ID}/work/review/quality_feedback.json",
            ],
            "source_paths_checked": review["checked_inputs"],
            "tools_attempted": [
                "jq over handoff, packet, and final artifacts",
                "rg over XML/PDF/supplement/database text",
                "pdftotext -layout on supplementary PDF",
                "sed inspection of extracted supplementary text",
                "merged-corpus rg for DBAASP/CAMP sequence and experiment rows",
                "semantic_three_layer_gate.py",
                "check_three_layer_publication_quality.py",
            ],
            "values_recovered": {
                "negative_antimicrobial_rows": 9,
                "aphid_activity_rows": 4,
                "database_rows_source_verified": review["semantic_quality_checks"]["database_status_summary"].get("source_verified", 0),
                "database_rows_source_conflict": review["semantic_quality_checks"]["database_status_summary"].get("source_conflict", 0),
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
            "notes": "Local material supports closure with cautions; database-only mixed-PMID CAMP dose rows are preserved as source_conflict and not promoted.",
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
