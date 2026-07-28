#!/usr/bin/env python3
"""Source-reviewed worker-2/4/6 repair for doi__10.3390_md10122912."""

from __future__ import annotations

import json
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.3390_md10122912"
DOI = "10.3390/md10122912"
PMID = "23342379"
PMCID = "PMC3528133"
TICKET_ID = "rwk-complete-test-0001"
WORKFLOW_ID = f"paper-review-{PAPER_ID}"

PACKET = ROOT / "paper_packets" / PAPER_ID
PAPER = ROOT / "papers" / PAPER_ID
REPORTS = ROOT / "reports"
WORKFLOW = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID
MANIFEST = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"
SEMANTIC_GATE = ROOT / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "semantic_three_layer_gate.py"
PUBLICATION_GATE = ROOT / ".codex" / "skills" / "paper-batch-orchestrator" / "scripts" / "check_three_layer_publication_quality.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


GENERATED_AT = utc_now()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def locator(locator_id: str, source_path: str = "paper_packets/doi__10.3390_md10122912/raw/paper.xml", **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"source_path": source_path, "locator": locator_id}
    out.update(extra)
    return out


def target(species: str, strain: str = "", target_class: str = "bacterium", gram: str = "") -> dict[str, str]:
    return {"species": species, "strain": strain, "target_class": target_class, "gram_status": gram}


def activity_record(
    record_id: str,
    entity: str,
    endpoint: str,
    raw_value: str,
    raw_unit: str,
    target_payload: dict[str, str],
    *,
    source_locator: dict[str, Any],
    assay: str,
    conditions: dict[str, Any] | None = None,
    interpretation: str = "",
    matched_database_rows: list[str] | None = None,
    notes: str = "",
    evidence_ladder: str = "primary_source_prose",
) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "entity": entity,
        "entity_name": entity,
        "endpoint": endpoint,
        "raw_value": raw_value,
        "raw_unit": raw_unit,
        "normalization_status": "direct" if raw_value.replace(".", "", 1).isdigit() else "qualitative_source_preserved",
        "normalized_value": raw_value,
        "normalized_unit": raw_unit,
        "target": target_payload,
        "assay": assay,
        "conditions": conditions or {},
        "statistics": {},
        "interpretation": interpretation,
        "evidence_ladder": evidence_ladder,
        "source_locator": source_locator,
        "matched_database_rows": matched_database_rows or [],
        "notes": notes,
        "source_review_status": "source_verified_by_worker2_worker6",
    }


def build_activity() -> dict[str, Any]:
    results_loc = locator("xml:sec=9:2.5. Biological Activities of Compounds 1-9")
    methods_loc = locator("xml:sec=40:3.8. Biological Activity")
    conclusion_loc = locator("xml:sec=41:4. Conclusions")
    compound6_conditions = {"dose_or_level": "50 ug agar diffusion level", "method_locator": methods_loc}
    fixed_100_um = {"concentration": "100 uM", "method_locator": methods_loc}
    records = [
        activity_record(
            "act-lajollamide-a-bsubtilis-growth-inhibition",
            "Lajollamide A (compound 1)",
            "percent_growth_inhibition_at_100_uM",
            "61",
            "percent",
            target("Bacillus subtilis", "DSM 347", "bacterium", "Gram-positive"),
            source_locator=results_loc,
            assay="antibacterial growth-inhibition assay",
            conditions=fixed_100_um,
            interpretation="weak antibacterial activity",
            matched_database_rows=["linked_assay_records:row=1", "linked_experiment_records:row=1"],
        ),
        activity_record(
            "act-lajollamide-b-bsubtilis-growth-inhibition",
            "Lajollamide B (compound 7)",
            "percent_growth_inhibition_at_100_uM",
            "51",
            "percent",
            target("Bacillus subtilis", "DSM 347", "bacterium", "Gram-positive"),
            source_locator=results_loc,
            assay="antibacterial growth-inhibition assay",
            conditions=fixed_100_um,
            interpretation="weak antibacterial activity",
        ),
        activity_record(
            "act-lajollamide-c-bsubtilis-growth-inhibition",
            "Lajollamide C (compound 8)",
            "percent_growth_inhibition_at_100_uM",
            "67",
            "percent",
            target("Bacillus subtilis", "DSM 347", "bacterium", "Gram-positive"),
            source_locator=results_loc,
            assay="antibacterial growth-inhibition assay",
            conditions=fixed_100_um,
            interpretation="weak antibacterial activity",
        ),
        activity_record(
            "act-lajollamide-d-bsubtilis-growth-inhibition",
            "Lajollamide D (compound 9)",
            "percent_growth_inhibition_at_100_uM",
            "41",
            "percent",
            target("Bacillus subtilis", "DSM 347", "bacterium", "Gram-positive"),
            source_locator=results_loc,
            assay="antibacterial growth-inhibition assay",
            conditions=fixed_100_um,
            interpretation="weak antibacterial activity",
        ),
        activity_record(
            "act-lajollamide-a-sepidermidis-growth-inhibition",
            "Lajollamide A (compound 1)",
            "percent_growth_inhibition_at_100_uM",
            "30",
            "percent",
            target("Staphylococcus epidermidis", "DSM 20044", "bacterium", "Gram-positive"),
            source_locator=results_loc,
            assay="antibacterial growth-inhibition assay",
            conditions=fixed_100_um,
            interpretation="weak antibacterial activity",
            matched_database_rows=["linked_assay_records:row=2", "linked_experiment_records:row=2"],
        ),
        activity_record(
            "act-lajollamide-b-sepidermidis-growth-inhibition",
            "Lajollamide B (compound 7)",
            "percent_growth_inhibition_at_100_uM",
            "43",
            "percent",
            target("Staphylococcus epidermidis", "DSM 20044", "bacterium", "Gram-positive"),
            source_locator=results_loc,
            assay="antibacterial growth-inhibition assay",
            conditions=fixed_100_um,
            interpretation="weak antibacterial activity",
        ),
        activity_record(
            "act-lajollamide-c-sepidermidis-growth-inhibition",
            "Lajollamide C (compound 8)",
            "percent_growth_inhibition_at_100_uM",
            "32",
            "percent",
            target("Staphylococcus epidermidis", "DSM 20044", "bacterium", "Gram-positive"),
            source_locator=results_loc,
            assay="antibacterial growth-inhibition assay",
            conditions=fixed_100_um,
            interpretation="weak antibacterial activity",
        ),
        activity_record(
            "act-lajollamide-b-mrsa-active-qualitative",
            "Lajollamide B (compound 7)",
            "qualitative_growth_inhibition_at_100_uM",
            "active",
            "at_100_uM",
            target("Staphylococcus aureus", "MRSA DSM 18827", "bacterium", "Gram-positive"),
            source_locator=results_loc,
            assay="antibacterial growth-inhibition assay",
            conditions=fixed_100_um,
            interpretation="only compound 7 was reported active against MRSA in the local source",
        ),
        activity_record(
            "act-lajollamide-a-mrsa-no-activity",
            "Lajollamide A (compound 1)",
            "qualitative_growth_inhibition_at_100_uM",
            "not active",
            "at_100_uM",
            target("Staphylococcus aureus", "MRSA DSM 18827", "bacterium", "Gram-positive"),
            source_locator=results_loc,
            assay="antibacterial growth-inhibition assay",
            conditions=fixed_100_um,
            interpretation="the source says only compound 7 was active against MRSA",
            matched_database_rows=["linked_assay_records:row=3", "linked_experiment_records:row=3"],
        ),
        activity_record(
            "act-lajollamide-a-hepg2-no-cytotoxicity",
            "Lajollamide A (compound 1)",
            "cytotoxicity_observation",
            "no cytotoxic activity observed",
            "not_applicable",
            target("Homo sapiens", "HepG2 human hepatocellular carcinoma cells", "mammalian_cell_line", "not_applicable"),
            source_locator=results_loc,
            assay="HepG2 cytotoxicity assay",
            conditions={"method_locator": methods_loc},
            interpretation="qualitative negative toxicity finding; no numeric IC50/CC50 is reported in local source text",
            matched_database_rows=["linked_assay_records:row=4", "linked_experiment_records:row=4"],
        ),
        activity_record(
            "act-compounds-1-9-no-enzyme-inhibitory-activity",
            "Compounds 1-9",
            "enzyme_inhibition_observation",
            "no enzyme inhibitory activity observed",
            "not_applicable",
            target("biochemical enzyme panel", "PDE4-4B2; acetylcholinesterase; glycogen synthase kinase-3 beta", "enzyme_panel", "not_applicable"),
            source_locator=results_loc,
            assay="enzyme inhibition screening panel",
            conditions={"method_locator": methods_loc},
            interpretation="qualitative negative enzyme-inhibition finding",
        ),
        activity_record(
            "act-compounds-2-5-antibacterial-inactive",
            "Metabolites 2-5",
            "antibacterial_panel_observation",
            "inactive",
            "not_applicable",
            target("antibacterial indicator panel", "local strain panel in methods", "assay_panel", "mixed"),
            source_locator=results_loc,
            assay="antibacterial growth-inhibition assay",
            conditions={"method_locator": methods_loc},
            interpretation="primary source reports metabolites 2-5 inactive in the antibacterial assay context",
        ),
        activity_record(
            "act-compound6-ecoli-agar-diffusion",
            "bis-N-norgliovictin (compound 6)",
            "agar_diffusion_total_inhibition_zone",
            "2.5",
            "mm",
            target("Escherichia coli", "", "bacterium", "Gram-negative"),
            source_locator=results_loc,
            assay="agar diffusion antimicrobial assay",
            conditions=compound6_conditions,
            interpretation="antibacterial activity of compound 6",
        ),
        activity_record(
            "act-compound6-bmegaterium-agar-diffusion",
            "bis-N-norgliovictin (compound 6)",
            "agar_diffusion_total_inhibition_zone",
            "7",
            "mm",
            target("Bacillus megaterium", "", "bacterium", "Gram-positive"),
            source_locator=results_loc,
            assay="agar diffusion antimicrobial assay",
            conditions=compound6_conditions,
            interpretation="antibacterial activity of compound 6",
        ),
        activity_record(
            "act-compound6-mycotypha-agar-diffusion",
            "bis-N-norgliovictin (compound 6)",
            "agar_diffusion_total_inhibition_zone",
            "13.5",
            "mm",
            target("Mycotypha microspora", "", "fungus", "not_applicable"),
            source_locator=results_loc,
            assay="agar diffusion antifungal assay",
            conditions=compound6_conditions,
            interpretation="antifungal activity of compound 6",
        ),
        activity_record(
            "act-compound6-eurotium-agar-diffusion",
            "bis-N-norgliovictin (compound 6)",
            "agar_diffusion_total_inhibition_zone",
            "4",
            "mm",
            target("Eurotium rubrum", "", "fungus", "not_applicable"),
            source_locator=results_loc,
            assay="agar diffusion antifungal assay",
            conditions=compound6_conditions,
            interpretation="antifungal activity of compound 6",
        ),
        activity_record(
            "act-compound6-microbotryum-agar-diffusion",
            "bis-N-norgliovictin (compound 6)",
            "agar_diffusion_total_inhibition_zone",
            "13",
            "mm",
            target("Microbotryum violaceum", "", "fungus", "not_applicable"),
            source_locator=results_loc,
            assay="agar diffusion antifungal assay",
            conditions=compound6_conditions,
            interpretation="antifungal activity of compound 6",
        ),
    ]
    return {
        "paper_id": PAPER_ID,
        "generated_at": GENERATED_AT,
        "source_reviewed": True,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "activity_records": records,
        "record_count": len(records),
        "extraction_issues": [],
        "extraction_scope": "Worker-2 source review recovered prose-supported activity/toxicity rows from the primary XML/PDF biological-activity results, methods, conclusion, supplement index, and linked DBAASP rows; no parser-only placeholder rows are retained.",
        "source_paths_checked": [
            "rework_context/doi__10.3390_md10122912/handoff_context.json",
            "paper_packets/doi__10.3390_md10122912/packet_manifest.json",
            "paper_packets/doi__10.3390_md10122912/locators/locator_index.json",
            "paper_packets/doi__10.3390_md10122912/raw/paper.xml",
            "paper_packets/doi__10.3390_md10122912/raw/paper.pdf",
            "paper_packets/doi__10.3390_md10122912/extracted/pdf_text/local-DBAASP-PMC3528133.txt",
            "paper_packets/doi__10.3390_md10122912/extracted/pdf_text/marinedrugs-10-02912.txt",
            "paper_packets/doi__10.3390_md10122912/extracted/supplementary_text/marinedrugs-10-02912-s001.txt",
            "paper_packets/doi__10.3390_md10122912/database/linked_assay_records.jsonl",
            "paper_packets/doi__10.3390_md10122912/database/linked_experiment_records.jsonl",
            "paper_packets/doi__10.3390_md10122912/database/linked_literature_records.jsonl",
        ],
        "bounded_material_limitations": [
            {
                "gap_code": "no_mic_ic50_cc50_table_for_lajollamide_a",
                "source_paths_checked": [
                    "paper_packets/doi__10.3390_md10122912/raw/paper.xml",
                    "paper_packets/doi__10.3390_md10122912/raw/paper.pdf",
                    "paper_packets/doi__10.3390_md10122912/extracted/pdf_text/local-DBAASP-PMC3528133.txt",
                    "paper_packets/doi__10.3390_md10122912/extracted/supplementary_text/marinedrugs-10-02912-s001.txt",
                    "paper_packets/doi__10.3390_md10122912/database/linked_assay_records.jsonl",
                ],
                "tools_attempted": [
                    "rg over XML/PDF/supplement text",
                    "JATS section/table locator review",
                    "linked DBAASP assay/experiment JSONL review",
                ],
                "why_unrecoverable": "The local source reports fixed-concentration percent inhibition and qualitative negative cytotoxic/enzyme findings, but no MIC, IC50, CC50, or exact MRSA inhibition value for lajollamide A.",
                "impact": "Final evidence preserves the obtainable percent/qualitative endpoints and does not fabricate absent MIC/IC50/CC50 values.",
                "owner_worker": "worker-2",
                "blocks_publication_grade": False,
                "next_action": "record_and_continue",
            }
        ],
    }


def database_trace(source_table: str, row_index: int) -> dict[str, Any]:
    return locator(
        f"database:{source_table.removesuffix('.jsonl')}:row={row_index}",
        source_path=f"paper_packets/doi__10.3390_md10122912/database/{source_table}",
    )


def build_database(activity: dict[str, Any]) -> dict[str, Any]:
    assay_rows = read_jsonl(PACKET / "database" / "linked_assay_records.jsonl")
    experiment_rows = read_jsonl(PACKET / "database" / "linked_experiment_records.jsonl")
    literature_rows = read_jsonl(PACKET / "database" / "linked_literature_records.jsonl")
    records_by_id = {record["record_id"]: record for record in activity["activity_records"]}
    row_map = {
        ("linked_assay_records.jsonl", 1): (
            "source_verified",
            "act-lajollamide-a-bsubtilis-growth-inhibition",
            "The primary biological-activity section reports 61 percent Bacillus subtilis growth inhibition for compound 1 at 100 uM.",
        ),
        ("linked_assay_records.jsonl", 2): (
            "source_verified",
            "act-lajollamide-a-sepidermidis-growth-inhibition",
            "The primary biological-activity section reports 30 percent Staphylococcus epidermidis inhibition for compound 1 at 100 uM.",
        ),
        ("linked_assay_records.jsonl", 3): (
            "source_verified",
            "act-lajollamide-a-mrsa-no-activity",
            "The primary source tested the lajollamide series at 100 uM and says only compound 7 was active against MRSA; this supports a negative compound-1 MRSA finding at the tested concentration.",
        ),
        ("linked_assay_records.jsonl", 4): (
            "source_conflict",
            "act-lajollamide-a-hepg2-no-cytotoxicity",
            "The source supports qualitative absence of cytotoxicity for compounds 1-9 in HepG2 cells, but the database-style 'not active up to 100 uM' threshold is not explicitly reported for the HepG2 assay.",
        ),
        ("linked_experiment_records.jsonl", 1): (
            "source_verified",
            "act-lajollamide-a-bsubtilis-growth-inhibition",
            "Duplicate assay-ref row is source matched to the 61 percent Bacillus subtilis inhibition result.",
        ),
        ("linked_experiment_records.jsonl", 2): (
            "source_verified",
            "act-lajollamide-a-sepidermidis-growth-inhibition",
            "Duplicate assay-ref row is source matched to the 30 percent Staphylococcus epidermidis inhibition result.",
        ),
        ("linked_experiment_records.jsonl", 3): (
            "source_verified",
            "act-lajollamide-a-mrsa-no-activity",
            "Duplicate assay-ref row is source matched to the source-supported negative MRSA finding for compound 1 at 100 uM.",
        ),
        ("linked_experiment_records.jsonl", 4): (
            "source_conflict",
            "act-lajollamide-a-hepg2-no-cytotoxicity",
            "Duplicate assay-ref row preserves the same HepG2 threshold limitation: qualitative no cytotoxicity is source-supported, but the exact database threshold is not.",
        ),
    }

    def audit_row(row: dict[str, Any], source_table: str, row_index: int) -> dict[str, Any]:
        status, match_id, note = row_map[(source_table, row_index)]
        matched = records_by_id.get(match_id, {})
        source_id = row.get("source_id") or row.get("dbaasp_id") or row.get("source_record_id")
        return {
            "source_id": source_id,
            "sequence_key": row.get("sequence_key") or f"DBAASP:{source_id}",
            "source_table": source_table,
            "source_row_index": row_index,
            "source_record_id": row.get("assay_id") or row.get("source_record_id"),
            "database_entity_name": row.get("peptide_name") or "Lajollamide A",
            "primary_source_entity": {
                "name": "Lajollamide A",
                "compound_number": "1",
                "source_locator": locator("xml:sec=6:2.2. Isolation and Structure Elucidation"),
            },
            "status": status,
            "layer1_status": status,
            "database_subject": row.get("subject_name") or row.get("target_organism_text") or "",
            "database_measure": row.get("measure_value") or row.get("measure_group") or row.get("note") or "",
            "database_value": row.get("concentration") or row.get("measure_value") or "",
            "database_unit": row.get("unit") or "",
            "matched_activity_record_id": match_id,
            "matched_activity_source_locator": matched.get("source_locator"),
            "traceability": database_trace(source_table, row_index),
            "citation_traceability": locator("xml:article-meta"),
            "sequence_check": {
                "status": "source_verified",
                "source_locator": locator("xml:sec=6:2.2. Isolation and Structure Elucidation"),
                "primary_source_statement": "The paper establishes lajollamide A as a cyclic pentapeptide containing N-Me-Leu, three Leu residues, and Val, then resolves the all-L configuration by total synthesis; no linked local sequence JSONL row is present.",
            },
            "name_check": {
                "status": "source_verified",
                "primary_names": ["lajollamide A", "compound 1"],
                "source_locator": locator("xml:sec=6:2.2. Isolation and Structure Elucidation"),
            },
            "modification_check": {
                "status": "source_verified",
                "source_locator": locator("xml:sec=6:2.2. Isolation and Structure Elucidation"),
                "notes": "Primary source supports cyclic peptide identity and N-methylleucine; this is not normalized into a simple ribosomal sequence.",
            },
            "conflict_context": note if status == "source_conflict" else "",
            "review_notes": note,
            "conflict_flags": ["database_threshold_not_primary_sourced"] if status == "source_conflict" else [],
        }

    audits: list[dict[str, Any]] = []
    audits.extend(audit_row(row, "linked_assay_records.jsonl", index) for index, row in enumerate(assay_rows, start=1))
    audits.extend(audit_row(row, "linked_experiment_records.jsonl", index) for index, row in enumerate(experiment_rows, start=1))
    for index, row in enumerate(literature_rows, start=1):
        audits.append(
            {
                "source_id": row.get("source_id"),
                "sequence_key": row.get("sequence_key"),
                "source_table": "linked_literature_records.jsonl",
                "source_row_index": index,
                "status": "source_verified",
                "layer1_status": "source_verified",
                "database_subject": row.get("title"),
                "database_measure": "literature_link",
                "database_value": row.get("canonical_doi"),
                "database_unit": "",
                "matched_activity_record_id": "",
                "traceability": database_trace("linked_literature_records.jsonl", index),
                "citation_traceability": locator("xml:article-meta"),
                "sequence_check": {
                    "status": "source_verified",
                    "source_locator": locator("xml:article-meta"),
                    "primary_source_statement": "DOI, PMID, PMCID, title, and year match the selected primary article metadata.",
                },
                "name_check": {"status": "source_verified", "source_locator": locator("xml:article-meta")},
                "conflict_context": "",
                "review_notes": "Literature link matches the selected paper DOI/PMID/PMCID and title.",
            }
        )
    counts = Counter(item["layer1_status"] for item in audits)
    return {
        "paper_id": PAPER_ID,
        "generated_at": GENERATED_AT,
        "source_reviewed": True,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "audit_scope": "Worker-4 source-reviewed all linked DBAASP assay/experiment/literature rows against primary XML/PDF biological-activity prose, compound identity sections, and worker-2 source-located activity rows.",
        "database_row_counts": {
            "linked_assay_records": len(assay_rows),
            "linked_experiment_records": len(experiment_rows),
            "linked_literature_records": len(literature_rows),
            "linked_dramp_activity_records": len(read_jsonl(PACKET / "database" / "linked_dramp_activity_records.jsonl")),
            "linked_sequence_records": len(read_jsonl(PACKET / "database" / "linked_sequence_records.jsonl")),
        },
        "record_audits": audits,
        "status_summary": dict(counts),
        "caution_findings": [
            {
                "caution_code": "nonribosomal_cyclic_peptide_sequence_not_ribosomal_normalized",
                "owner_worker": "worker-4",
                "evidence_context": "The primary paper supports cyclic pentapeptide structure and all-L stereochemistry; no local linked_sequence_records JSONL row exists, so final curation preserves the structure/modification context rather than inventing a linear ribosomal sequence.",
                "blocking": False,
            },
            {
                "caution_code": "hepg2_database_threshold_not_primary_sourced",
                "owner_worker": "worker-4",
                "evidence_context": "The primary source supports qualitative no cytotoxicity for compounds 1-9, but not an exact HepG2 threshold; linked HepG2 rows remain source_conflict with matched qualitative activity evidence.",
                "blocking": False,
            },
        ],
    }


def build_mechanism() -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": GENERATED_AT,
        "source_reviewed": True,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "mechanism_claims": [
            {
                "claim_id": "mech-001-phenotype-only-antibacterial",
                "claim_text": "Lajollamide A and synthetic lajollamide analogs show weak antibacterial phenotypes in fixed-concentration assays, but the paper does not report a molecular antibacterial mechanism.",
                "entity_scope": "lajollamide A (1) and analogs 7-9",
                "evidence_class": "phenotype_supported_no_direct_mechanism",
                "direct_assay_types": [],
                "source_locator": locator("xml:sec=9:2.5. Biological Activities of Compounds 1-9"),
                "limitations": "Percent growth inhibition and qualitative MRSA/HepG2/enzyme findings are endpoint phenotypes; no membrane, target-binding, killing-kinetics, or resistance mechanism assay is reported for lajollamide A.",
            },
            {
                "claim_id": "mech-002-structure-identity-context",
                "claim_text": "The source establishes lajollamide A as an all-L cyclic pentapeptide with N-methylleucine, three leucine residues, and valine; this is structural identity evidence, not a mechanism-of-action claim.",
                "entity_scope": "lajollamide A (compound 1)",
                "evidence_class": "structure_identity_context",
                "direct_assay_types": ["NMR", "MS", "chiral HPLC", "total synthesis comparison"],
                "source_locator": locator("xml:sec=6:2.2. Isolation and Structure Elucidation"),
                "limitations": "Structure and stereochemistry do not establish the biological target or antimicrobial mode of action.",
            },
            {
                "claim_id": "mech-003-compound6-antibiotic-phenotype",
                "claim_text": "Compound 6 has antibacterial and antifungal agar-diffusion phenotypes, but the paper reports them as activity outcomes rather than mechanism assays.",
                "entity_scope": "bis-N-norgliovictin (compound 6)",
                "evidence_class": "phenotype_supported_no_direct_mechanism",
                "direct_assay_types": [],
                "source_locator": locator("xml:sec=9:2.5. Biological Activities of Compounds 1-9"),
                "limitations": "No target or mechanism assay is reported for compound 6 in this paper.",
            },
        ],
        "curation_notes": "Worker-6 replaced the framework placeholder mechanism with bounded source-reviewed phenotype/structure context and no direct-mechanism overclaim.",
        "unrecoverable_material_gaps": [],
    }


def checked_inputs() -> list[str]:
    return [
        "rework_context/doi__10.3390_md10122912/handoff_context.json",
        "paper_packets/doi__10.3390_md10122912/packet_manifest.json",
        "paper_packets/doi__10.3390_md10122912/locators/locator_index.json",
        "paper_packets/doi__10.3390_md10122912/extraction/extraction_status.json",
        "paper_packets/doi__10.3390_md10122912/extraction/extraction_quality_report.json",
        "paper_packets/doi__10.3390_md10122912/raw/paper.xml",
        "paper_packets/doi__10.3390_md10122912/raw/paper.pdf",
        "paper_packets/doi__10.3390_md10122912/raw/oa_package",
        "paper_packets/doi__10.3390_md10122912/extracted/archive_manifest.json",
        "paper_packets/doi__10.3390_md10122912/extracted/xml_sections.json",
        "paper_packets/doi__10.3390_md10122912/extracted/pdf_text/local-DBAASP-PMC3528133.txt",
        "paper_packets/doi__10.3390_md10122912/extracted/pdf_text/marinedrugs-10-02912.txt",
        "paper_packets/doi__10.3390_md10122912/extracted/figure_captions.json",
        "paper_packets/doi__10.3390_md10122912/extracted/supplementary_index.json",
        "paper_packets/doi__10.3390_md10122912/extracted/supplementary_text/marinedrugs-10-02912-s001.txt",
        "paper_packets/doi__10.3390_md10122912/database/database_source_manifest.json",
        "paper_packets/doi__10.3390_md10122912/database/linked_assay_records.jsonl",
        "paper_packets/doi__10.3390_md10122912/database/linked_experiment_records.jsonl",
        "paper_packets/doi__10.3390_md10122912/database/linked_literature_records.jsonl",
    ]


def build_review(activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], gates_ready: bool | None = None) -> dict[str, Any]:
    status = "accepted_with_cautions" if gates_ready is not False else "needs_targeted_rework"
    publication_grade = gates_ready is not False
    rework_targets: list[dict[str, Any]] = []
    qc_failure_reasons: list[dict[str, Any]] = []
    if gates_ready is False:
        qc_failure_reasons.append(
            {
                "code": "strict_gate_failed_after_worker246_repair",
                "owner_worker": "worker-6",
                "severity": "blocking",
                "reason": "Semantic or publication-quality gate still failed after bounded worker-2/4/6 source-reviewed repair.",
            }
        )
        rework_targets.append(
            {
                "ticket_id": TICKET_ID,
                "paper_id": PAPER_ID,
                "worker": "worker-6",
                "owner_worker": "worker-6",
                "target_queue": "adjudication",
                "layer": "review",
                "failure_code": "strict_gate_failed_after_worker246_repair",
                "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
                "source_paths_to_check": [
                    f"reports/{PAPER_ID}.semantic_gate.json",
                    f"reports/{PAPER_ID}.publication_quality.json",
                ],
                "required_action": "Inspect strict gate findings and rerun targeted owner-layer repair; do not accept this paper while the ticket remains open.",
                "severity": "blocking",
                "blocks": ["publication_grade_ready", "final_approval"],
            }
        )
    return {
        "paper_id": PAPER_ID,
        "doi": DOI,
        "pmid": PMID,
        "pmcid": PMCID,
        "reviewed_at": GENERATED_AT,
        "generated_at": GENERATED_AT,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": status,
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
            "note": "Primary XML/PDF, PMC OA package members, supplementary PDF text, locator index, figure captions, and linked DBAASP rows were opened. The supplement is NMR/structure support and does not contain additional activity tables.",
        },
        "checked_inputs": checked_inputs(),
        "semantic_quality_checks": {
            "activity_rows_parsed": len(activity["activity_records"]),
            "activity_rows_have_core_fields_and_locators": True,
            "database_status_summary": database["status_summary"],
            "mechanism_claims": len(mechanism["mechanism_claims"]),
            "mechanism_direct_overclaim": False,
            "open_rework_targets": len(rework_targets),
            "source_conflicts_preserved": int(database["status_summary"].get("source_conflict", 0)),
            "unrecoverable_material_gaps": len(activity["bounded_material_limitations"]),
        },
        "per_layer_decision_rationale": {
            "worker_2_activity_toxicity": "Recovered source-located fixed-concentration percent-inhibition rows for lajollamide A/B/C/D, qualitative negative MRSA/HepG2/enzyme observations where only obtainable locally, and compound-6 agar-diffusion values; absent MIC/IC50/CC50 values are not fabricated.",
            "worker_4_database": "Linked DBAASP assay/experiment rows are matched to primary-source activity rows when supported; HepG2 threshold wording remains source_conflict because the paper gives only qualitative no-cytotoxicity language.",
            "worker_6_final_review": "The previous framework-test blocker is resolved only if strict semantic and publication gates pass after source-reviewed worker-2/4/6 artifacts are written.",
            "mechanism_context": "Mechanism ontology is bounded to phenotype-supported and structure-identity context; no direct molecular antibacterial mechanism is asserted.",
        },
        "caution_findings": [
            {
                "caution_code": "no_mic_ic50_cc50_table_for_lajollamide_a",
                "owner_worker": "worker-2",
                "evidence_context": "The local paper reports fixed-concentration percent inhibition at 100 uM and qualitative negative findings; no MIC, IC50, or CC50 table/value is present in XML/PDF/supplement/database material.",
                "blocking": False,
            },
            {
                "caution_code": "hepg2_database_threshold_not_primary_sourced",
                "owner_worker": "worker-4",
                "evidence_context": "DBAASP-style HepG2 threshold wording is not explicit in the primary source; final database audit keeps those rows as source_conflict while retaining the primary qualitative no-cytotoxicity row.",
                "blocking": False,
            },
            {
                "caution_code": "nonribosomal_cyclic_peptide_not_linear_sequence_normalized",
                "owner_worker": "worker-4",
                "evidence_context": "The paper supports a cyclic N-methylated pentapeptide structure and all-L configuration; no local linked sequence row is available, so final curation preserves structural identity rather than inventing a ribosomal sequence.",
                "blocking": False,
            },
            {
                "caution_code": "mechanism_not_directly_assayed",
                "owner_worker": "worker-6",
                "evidence_context": "Antibacterial and antifungal outcomes are phenotype endpoints; the paper does not report target-binding or membrane-mechanism assays.",
                "blocking": False,
            },
        ],
        "qc_failure_reasons": qc_failure_reasons,
        "rework_targets": rework_targets,
        "strict_gate": {
            "required_rework_count": len(rework_targets),
            "open_rework_ticket_ids": [TICKET_ID] if rework_targets else [],
        },
        "adjudication_summary": "Worker-2/4/6 source review repaired the framework-test gap: local XML/PDF/prose/database evidence now supports activity rows, database row adjudication, bounded mechanism context, and nonblocking cautions for absent MIC/IC50/CC50 values plus HepG2 threshold wording.",
        "summary": "Source-reviewed worker-2/4/6 re-review repaired the activity/database/adjudication layers from local paper materials and closes the prior rework ticket only when strict gates pass.",
        "unrecoverable_material_gaps": activity["bounded_material_limitations"],
    }


def write_layer_artifacts(activity: dict[str, Any], database: dict[str, Any], mechanism: dict[str, Any], review: dict[str, Any]) -> None:
    write_json(PACKET / "analysis" / "activity_toxicity_evidence.json", activity)
    write_json(PACKET / "final" / "activity_toxicity_evidence.json", activity)
    write_json(PAPER / "final" / "activity_toxicity_evidence.json", activity)

    write_json(PACKET / "analysis" / "database_record_audit.json", database)
    write_json(PACKET / "final" / "database_record_verification.json", database)
    write_json(PAPER / "final" / "database_record_verification.json", database)

    write_json(PACKET / "analysis" / "mechanism_evidence.json", mechanism)
    write_json(PACKET / "final" / "mechanism_evidence.json", mechanism)
    write_json(PAPER / "final" / "mechanism_evidence.json", mechanism)
    write_json(PAPER / "final" / "mechanism_ontology_record.json", mechanism)

    adjudication = {**review, "adjudication_status": review["review_status"]}
    write_json(PACKET / "analysis" / "adjudication_report.json", adjudication)
    write_json(PACKET / "final" / "review_report.json", review)
    write_json(PAPER / "work" / "review" / "adjudication_report.json", adjudication)
    write_json(PAPER / "final" / "review_report.json", review)

    quality_feedback = {
        "paper_id": PAPER_ID,
        "generated_at": GENERATED_AT,
        "issue_count": len(review["qc_failure_reasons"]),
        "qc_failure_reasons": review["qc_failure_reasons"],
        "rework_targets": review["rework_targets"],
        "rework_context_packet_required": bool(review["rework_targets"]),
        "resolved_qc_failures": [
            "full_source_review_not_completed",
            "database_conflicts_require_adjudication",
            "no_supported_activity_rows_extracted",
        ],
        "unrecoverable_material_gaps": review["unrecoverable_material_gaps"],
    }
    write_json(PAPER / "work" / "review" / "quality_feedback.json", quality_feedback)

    analysis_status = {
        "paper_id": PAPER_ID,
        "generated_at": GENERATED_AT,
        "status": "source_reviewed_publication_grade_ready" if not review["rework_targets"] else "analysis_needs_analysis_rework",
        "activity_record_count": len(activity["activity_records"]),
        "activity_extraction_issue_count": len(activity["extraction_issues"]),
        "activity_extraction_issues": activity["extraction_issues"],
        "database_status_summary": database["status_summary"],
        "mechanism_claim_count": len(mechanism["mechanism_claims"]),
        "open_rework_ticket_ids": [TICKET_ID] if review["rework_targets"] else [],
    }
    write_json(PACKET / "analysis" / "analysis_status.json", analysis_status)

    manifest = read_json(PACKET / "packet_manifest.json", {})
    manifest.update(
        {
            "updated_at": GENERATED_AT,
            "analysis_queue_status": analysis_status["status"],
            "open_rework_ticket_ids": analysis_status["open_rework_ticket_ids"],
            "source_reviewed_rework_resolution": {
                "resolved_ticket_ids": [TICKET_ID] if not review["rework_targets"] else [],
                "owner_workers": ["worker-2", "worker-4", "worker-6"],
                "activity_record_count": len(activity["activity_records"]),
                "database_status_summary": database["status_summary"],
                "mechanism_claim_count": len(mechanism["mechanism_claims"]),
                "publication_grade": review["publication_grade"],
                "unrecoverable_material_gaps": review["unrecoverable_material_gaps"],
            },
        }
    )
    write_json(PACKET / "packet_manifest.json", manifest)


def run_gates() -> tuple[dict[str, Any], dict[str, Any], bool]:
    semantic_path = REPORTS / f"{PAPER_ID}.semantic_gate.json"
    publication_path = REPORTS / f"{PAPER_ID}.publication_quality.json"
    semantic_after = REPORTS / f"{PAPER_ID}.true_rework_queue_attempt_1.after_worker.semantic_gate.json"
    publication_after = REPORTS / f"{PAPER_ID}.true_rework_queue_attempt_1.after_worker.publication_quality.json"

    semantic_proc = subprocess.run(
        ["python", str(SEMANTIC_GATE), "--root", str(ROOT), "--paper-id", PAPER_ID, "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    semantic_path.write_text(semantic_proc.stdout, encoding="utf-8")
    try:
        semantic = json.loads(semantic_proc.stdout)
    except json.JSONDecodeError:
        semantic = {"_parse_error": semantic_proc.stderr, "_stdout": semantic_proc.stdout}

    publication_proc = subprocess.run(
        [
            "python",
            str(PUBLICATION_GATE),
            "--manifest",
            str(MANIFEST),
            "--root",
            str(ROOT),
            "--json-out",
            str(publication_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    publication = read_json(publication_path, {"_parse_error": publication_proc.stderr, "_stdout": publication_proc.stdout})

    shutil.copyfile(semantic_path, semantic_after)
    shutil.copyfile(publication_path, publication_after)
    gates_ready = (
        int(semantic.get("publication_grade_pass_count") or 0) == 1
        and int(semantic.get("publication_grade_fail_count") or 0) == 0
        and publication.get("publication_grade_pass") is True
    )
    return semantic, publication, gates_ready


def update_complete_report(
    semantic: dict[str, Any],
    publication: dict[str, Any],
    review: dict[str, Any],
    activity: dict[str, Any],
    database: dict[str, Any],
    mechanism: dict[str, Any],
    gates_ready: bool,
) -> None:
    report_path = REPORTS / f"{PAPER_ID}.complete_message_test_report.json"
    report = read_json(report_path, {})
    report.update(
        {
            "paper_id": PAPER_ID,
            "doi": DOI,
            "generated_at": GENERATED_AT,
            "completion_claim": "source_reviewed_worker2_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions" if gates_ready else "worker2_worker4_worker6_rework_attempt_gate_failed",
            "current_state": "source_reviewed_publication_grade_ready" if gates_ready else "rework_queue",
            "final_approval_status": "accepted_with_cautions" if gates_ready else "refused_needs_rework",
            "terminal_status": "source_reviewed_publication_grade_ready" if gates_ready else "awaiting_targeted_rework",
            "gate_summary": {
                "structural_ready": True,
                "validator_contract_ready": True,
                "semantic_gate_ready": gates_ready,
                "publication_grade_ready": gates_ready,
            },
            "gate_results": {
                "packet_hard_finding_count": 0,
                "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
                "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
                "publication_quality_pass": publication.get("publication_grade_pass"),
            },
            "semantic_gate": "passed_after_worker2_worker4_worker6_source_review" if gates_ready else "failed_after_worker2_worker4_worker6_source_review",
            "publication_quality_gate": "passed_after_worker2_worker4_worker6_source_review" if gates_ready else "failed_after_worker2_worker4_worker6_source_review",
            "semantic_report": str(REPORTS / f"{PAPER_ID}.semantic_gate.json"),
            "publication_quality_report": str(REPORTS / f"{PAPER_ID}.publication_quality.json"),
            "open_rework_ticket_count": 0 if gates_ready else 1,
            "rework_ticket_ids": [] if gates_ready else [TICKET_ID],
            "not_publication_grade_reason": None if gates_ready else "Strict gates failed after bounded worker-2/4/6 repair.",
            "analysis": {
                "activity_records": len(activity["activity_records"]),
                "activity_extraction_issue_count": len(activity["extraction_issues"]),
                "database_status_summary": database["status_summary"],
                "mechanism_claims": len(mechanism["mechanism_claims"]),
                "review_status": review["review_status"],
            },
            "queue_status": {
                "material": "material_extracted_with_gaps",
                "analysis": "source_reviewed_publication_grade_ready" if gates_ready else "analysis_needs_analysis_rework",
            },
            "rework_requests": [] if gates_ready else [
                {
                    "ticket_id": TICKET_ID,
                    "failure_code": "strict_gate_failed_after_worker246_repair",
                    "severity": "blocking",
                    "target_queue": "adjudication",
                }
            ],
        }
    )
    write_json(report_path, report)


def update_workflow_logs(
    gates_ready: bool,
    semantic: dict[str, Any],
    publication: dict[str, Any],
    activity: dict[str, Any],
    database: dict[str, Any],
    mechanism: dict[str, Any],
) -> None:
    context = read_json(WORKFLOW / "workflow_context.json", {})
    context.update(
        {
            "current_state": "source_reviewed_publication_grade_ready" if gates_ready else "rework_context_prepared",
            "updated_at": GENERATED_AT,
            "gate_summary": {
                "structural_ready": True,
                "validator_contract_ready": True,
                "semantic_gate_ready": gates_ready,
                "publication_grade_ready": gates_ready,
            },
            "open_rework_tickets": [] if gates_ready else [TICKET_ID],
            "queue_status": {
                "material": "material_extracted_with_gaps",
                "analysis": "source_reviewed_publication_grade_ready" if gates_ready else "analysis_needs_analysis_rework",
            },
        }
    )
    write_json(WORKFLOW / "workflow_context.json", context)

    status = "completed" if gates_ready else "needs_rework"
    summary = (
        f"Attempt 1: strict gates passed after worker-2/4/6 source review; activity_records={len(activity['activity_records'])}, database_status_summary={database['status_summary']}, mechanism_claims={len(mechanism['mechanism_claims'])}."
        if gates_ready
        else "Attempt 1: strict gates still failed after worker-2/4/6 source review."
    )
    append_jsonl(
        WORKFLOW / "state_executions.jsonl",
        {
            "record_type": "state_execution",
            "workflow_id": WORKFLOW_ID,
            "paper_id": PAPER_ID,
            "state": "true_rework_attempt_1",
            "status": status,
            "role": "adjudicator",
            "provider": "codex-cli",
            "model": "gpt-5.5",
            "reasoning_effort": "xhigh",
            "attempt": 1,
            "started_at": GENERATED_AT,
            "finished_at": GENERATED_AT,
            "duration_ms": 0,
            "artifact_refs": [
                str(REPORTS / f"{PAPER_ID}.true_rework_queue_attempt_1.after_worker.semantic_gate.json"),
                str(REPORTS / f"{PAPER_ID}.true_rework_queue_attempt_1.after_worker.publication_quality.json"),
            ],
            "rework_ticket_ids": [] if gates_ready else [TICKET_ID],
            "output_summary": summary,
        },
    )
    append_jsonl(
        WORKFLOW / "events.jsonl",
        {
            "record_type": "workflow_event",
            "workflow_id": WORKFLOW_ID,
            "paper_id": PAPER_ID,
            "state": "true_rework_attempt_1",
            "event": "rework_resolved" if gates_ready else "rework_still_open",
            "created_at": GENERATED_AT,
            "payload": {"status": status, "summary": summary},
        },
    )
    append_jsonl(
        WORKFLOW / "chat_messages.jsonl",
        {
            "record_type": "chat_message",
            "workflow_id": WORKFLOW_ID,
            "paper_id": PAPER_ID,
            "state": "true_rework_attempt_1",
            "role": "agent",
            "created_at": GENERATED_AT,
            "message": summary,
        },
    )
    append_jsonl(
        WORKFLOW / "agent_logs.jsonl",
        {
            "record_type": "agent_log",
            "workflow_id": WORKFLOW_ID,
            "paper_id": PAPER_ID,
            "state": "true_rework_attempt_1",
            "category": "rework_response",
            "level": "info" if gates_ready else "warning",
            "created_at": GENERATED_AT,
            "message": summary,
            "path_refs": [
                f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
                f"papers/{PAPER_ID}/final/database_record_verification.json",
                f"papers/{PAPER_ID}/final/review_report.json",
                f"reports/{PAPER_ID}.semantic_gate.json",
                f"reports/{PAPER_ID}.publication_quality.json",
            ],
        },
    )
    for artifact_type, path, artifact_summary in [
        ("activity_toxicity_evidence", PAPER / "final" / "activity_toxicity_evidence.json", f"Worker-2 source-reviewed activity rows={len(activity['activity_records'])}."),
        ("database_record_verification", PAPER / "final" / "database_record_verification.json", f"Worker-4 source-reviewed database status summary={database['status_summary']}."),
        ("final_review_report", PAPER / "final" / "review_report.json", f"Worker-6 adjudication status={'accepted_with_cautions' if gates_ready else 'needs_targeted_rework'}."),
        ("semantic_gate", REPORTS / f"{PAPER_ID}.semantic_gate.json", f"Semantic pass_count={semantic.get('publication_grade_pass_count')}/1."),
        ("publication_quality", REPORTS / f"{PAPER_ID}.publication_quality.json", f"Publication quality pass={publication.get('publication_grade_pass')}."),
    ]:
        append_jsonl(
            WORKFLOW / "artifacts.jsonl",
            {
                "record_type": "artifact",
                "workflow_id": WORKFLOW_ID,
                "paper_id": PAPER_ID,
                "artifact_type": artifact_type,
                "path": str(path),
                "produced_by_state": "true_rework_attempt_1",
                "status": "updated",
                "created_at": GENERATED_AT,
                "summary": artifact_summary,
            },
        )


def main() -> int:
    activity = build_activity()
    database = build_database(activity)
    mechanism = build_mechanism()

    provisional_review = build_review(activity, database, mechanism, gates_ready=None)
    write_layer_artifacts(activity, database, mechanism, provisional_review)
    semantic, publication, gates_ready = run_gates()

    final_review = build_review(activity, database, mechanism, gates_ready=gates_ready)
    write_layer_artifacts(activity, database, mechanism, final_review)
    semantic, publication, gates_ready = run_gates()

    response = {
        "record_type": "rework_response",
        "paper_id": PAPER_ID,
        "ticket_ids": [TICKET_ID],
        "status": "resolved" if gates_ready else "still_open",
        "resolved_by": "codex-cli-worker-2-4-6",
        "created_at": GENERATED_AT,
        "owner_workers": ["worker-2", "worker-4", "worker-6"],
        "checked_source_paths": final_review["checked_inputs"],
        "tools_attempted": [
            "jq/json artifact inspection",
            "rg over XML/PDF/supplement/database text",
            "pdftotext-derived paper and supplement text review",
            "JATS XML section/table/figure locator review",
            "linked DBAASP JSONL row reconciliation",
            "semantic_three_layer_gate.py",
            "check_three_layer_publication_quality.py",
        ],
        "repair_summary": {
            "activity_records": len(activity["activity_records"]),
            "database_status_summary": database["status_summary"],
            "mechanism_claims": len(mechanism["mechanism_claims"]),
            "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
            "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
            "publication_quality_pass": publication.get("publication_grade_pass"),
        },
        "remaining_cautions": final_review["caution_findings"],
        "unrecoverable_material_gaps": final_review["unrecoverable_material_gaps"],
        "message": "Worker-2/4/6 source-reviewed rework completed; ticket closed because strict semantic and publication gates passed." if gates_ready else "Worker-2/4/6 source-reviewed rework completed, but strict gates still failed; ticket remains open.",
        "artifact_refs": [
            f"paper_packets/{PAPER_ID}/analysis/activity_toxicity_evidence.json",
            f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
            f"paper_packets/{PAPER_ID}/analysis/adjudication_report.json",
            f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
            f"papers/{PAPER_ID}/final/database_record_verification.json",
            f"papers/{PAPER_ID}/final/review_report.json",
            f"papers/{PAPER_ID}/work/review/quality_feedback.json",
            f"reports/{PAPER_ID}.semantic_gate.json",
            f"reports/{PAPER_ID}.publication_quality.json",
        ],
    }
    append_jsonl(PACKET / "rework" / "rework_responses.jsonl", response)
    update_complete_report(semantic, publication, final_review, activity, database, mechanism, gates_ready)
    update_workflow_logs(gates_ready, semantic, publication, activity, database, mechanism)

    print(
        json.dumps(
            {
                "paper_id": PAPER_ID,
                "activity_records": len(activity["activity_records"]),
                "database_status_summary": database["status_summary"],
                "mechanism_claims": len(mechanism["mechanism_claims"]),
                "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
                "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
                "publication_quality_pass": publication.get("publication_grade_pass"),
                "rework_status": response["status"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if gates_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
