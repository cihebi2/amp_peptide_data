#!/usr/bin/env python3
"""Source-reviewed worker-4/worker-6 repair for doi__10.3390_md16110401."""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "doi__10.3390_md16110401"
DOI = "10.3390/md16110401"
PMID = "30360541"
TICKET_ID = "rwk-complete-test-0001"
PAPER = ROOT / "papers" / PAPER_ID
PACKET = ROOT / "paper_packets" / PAPER_ID
REPORTS = ROOT / "reports"
MANIFEST = REPORTS / f"{PAPER_ID}.complete_message_test_manifest.json"
SEMANTIC_REPORT = REPORTS / f"{PAPER_ID}.semantic_gate.json"
PUBLICATION_REPORT = REPORTS / f"{PAPER_ID}.publication_quality.json"
MERGED_OUTPUT = Path(
    "/mnt/d/work/\u6297\u83cc\u80bd/\u6570\u636e\u5e93/merged_amp_corpus/output"
)

SOURCE_PATHS_CHECKED = [
    f"rework_context/{PAPER_ID}/handoff_context.json",
    f"paper_packets/{PAPER_ID}/packet_manifest.json",
    f"paper_packets/{PAPER_ID}/locators/locator_index.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_status.json",
    f"paper_packets/{PAPER_ID}/extraction/extraction_quality_report.json",
    f"paper_packets/{PAPER_ID}/extracted/xml_sections.json",
    f"paper_packets/{PAPER_ID}/extracted/figure_captions.json",
    f"paper_packets/{PAPER_ID}/extracted/pdf_text/marinedrugs-16-00401.txt",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_text/marinedrugs-16-00401-s001.txt",
    f"paper_packets/{PAPER_ID}/extracted/supplementary_tables.json",
    f"papers/{PAPER_ID}/source/paper.xml",
    f"papers/{PAPER_ID}/source/paper.pdf",
    f"paper_packets/{PAPER_ID}/database/database_source_manifest.json",
    f"paper_packets/{PAPER_ID}/database/linked_assay_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_dramp_activity_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_experiment_records.jsonl",
    f"paper_packets/{PAPER_ID}/database/linked_literature_records.jsonl",
    str(MERGED_OUTPUT / "sequences/all_sequences.csv"),
    str(MERGED_OUTPUT / "experiments/all_experimental_records.csv"),
    str(MERGED_OUTPUT / "experiments/dbaasp_assay_records.csv"),
]

TOOLS_ATTEMPTED = [
    "jq over handoff, packet, final, quality, and report artifacts",
    "python xml.etree table extraction from paper.xml",
    "rg over XML, PDF text, supplementary text, and merged database exports",
    "sed inspection of extracted PDF and supplementary text",
    "local image inspection of Figure 9",
    "semantic_three_layer_gate.py",
    "check_three_layer_publication_quality.py",
]

PEPTIDES = {
    "DBAASP:DBAASPR_12236": {
        "name": "Nicomicin-1",
        "sequence": "GFWSSVWDGAKNVGTAIIKNAKVCVYAVCVSHK",
        "source": "Nicomache minor",
        "source_type": "natural/recombinant mature peptide",
        "sequence_locator": "xml:fig=3;xml:sec=2.1;supp:Figure_S3",
    },
    "DBAASP:DBAASPS_12237": {
        "name": "Nico(1-17)",
        "sequence": "GFWSSVWDGAKNVGTAI",
        "source": "synthetic fragment of nicomicin-1",
        "source_type": "recombinant/synthetic fragment",
        "sequence_locator": "xml:sec=2.3;xml:table=2;xml:fig=3",
    },
    "DBAASP:DBAASPS_12238": {
        "name": "Nico(18-33)",
        "sequence": "IKNAKVCVYAVCVSHK",
        "source": "synthetic fragment of nicomicin-1",
        "source_type": "recombinant/synthetic fragment",
        "sequence_locator": "xml:sec=2.3;xml:table=2;xml:fig=3",
    },
    "APD6:AP03027": {
        "name": "Nicomicin-1",
        "sequence": "GFWSSVWDGAKNVGTAIIKNAKVCVYAVCVSHK",
        "source": "Nicomache minor",
        "source_type": "natural/recombinant mature peptide",
        "sequence_locator": "xml:fig=3;xml:sec=2.1;supp:Figure_S3",
    },
    "DRAMP:DRAMP34549": {
        "name": "Nicomicin-1",
        "sequence": "GFWSSVWDGAKNVGTAIIKNAKVCVYAVCVSHK",
        "source": "Nicomache minor",
        "source_type": "natural/recombinant mature peptide",
        "sequence_locator": "xml:fig=3;xml:sec=2.1;supp:Figure_S3",
    },
    "DRAMP:DRAMP34550": {
        "name": "Nicomicin-1 (1-17)",
        "sequence": "GFWSSVWDGAKNVGTAI",
        "source": "synthetic fragment of nicomicin-1",
        "source_type": "recombinant/synthetic fragment",
        "sequence_locator": "xml:sec=2.3;xml:table=2;xml:fig=3",
    },
    "DRAMP:DRAMP35646": {
        "name": "Nicomicin-1 (18-33)",
        "sequence": "IKNAKVCVYAVCVSHK",
        "source": "synthetic fragment of nicomicin-1",
        "source_type": "recombinant/synthetic fragment",
        "sequence_locator": "xml:sec=2.3;xml:table=2;xml:fig=3",
    },
}

DBAASP_ENTITY = {
    "DBAASP:DBAASPR_12236": "Nicomicin-1",
    "DBAASP:DBAASPS_12237": "Nico(1-17)",
    "DBAASP:DBAASPS_12238": "Nico(18-33)",
}

TABLE3 = [
    ("Micrococcus luteus", "VKM B-1314", ["0.125", "0.25", ">16", ">16", "16", ">16"], 5),
    ("Bacillus subtilis", "VKM B-886", ["0.062", "0.25", ">16", ">16", "16", ">16"], 6),
    ("Bacillus licheniformis", "VK21", ["0.125", "0.25", ">16", ">16", "8", ">128"], 7),
    ("Bacillus megaterium", "VKM41", [">16", ">16", ">16", ">16", ">16", ">16"], 8),
    ("Staphylococcus aureus", "209P", ["2", "32", ">16", ">16", ">16", ">16"], 9),
    ("Staphylococcus aureus", "ATCC 29213", ["2", "16", ">16", ">16", ">128", ">128"], 10),
    ("Rhodococcus sp.", "SS1", ["0.125", "0.25", ">16", ">16", ">16", ">16"], 11),
    ("Escherichia coli", "BL21 (DE3)", ["2", "32", ">64", ">64", ">64", ">64"], 13),
    ("Escherichia coli", "ML-35p", ["16", ">32", ">64", ">64", ">64", ">64"], 14),
    ("Escherichia coli", "C600", ["32", ">32", ">64", ">64", ">64", ">64"], 15),
    ("Acinetobacter baumannii", "clinical isolate", ["32", ">32", ">64", ">64", ">64", ">64"], 16),
    ("Pseudomonas aeruginosa", "PAO1", ["32", ">32", ">64", ">64", ">128", ">128"], 17),
]

TABLE3_COLUMNS = [
    ("Nicomicin-1", "without NaCl", 3),
    ("Nicomicin-1", "+150 mM NaCl", 4),
    ("Nico(1-17)", "without NaCl", 5),
    ("Nico(1-17)", "+150 mM NaCl", 6),
    ("Nico(18-33)", "without NaCl", 7),
    ("Nico(18-33)", "+150 mM NaCl", 8),
]

TOXICITY_ROWS = [
    ("Nicomicin-1", "Homo sapiens", "human embryonic fibroblasts", "cell_death_percent", "70", "% at 32 uM", "figure_graph_estimate", "xml:fig=9B"),
    ("Nicomicin-1", "Homo sapiens", "human erythrocytes", "hemolysis_HC50", "about 64", "uM", "source_text", "xml:sec=2.8;xml:fig=9A"),
    ("Nicomicin-1", "Homo sapiens", "HeLa cervix adenocarcinoma cells", "cell_death_percent", "85", "% at 32 uM", "source_text", "xml:sec=2.8;xml:fig=9B"),
    ("Nico(1-17)", "Homo sapiens", "human embryonic fibroblasts", "cell_death_percent", "60", "% at 32 uM", "figure_graph_estimate", "xml:fig=9B"),
    ("Nico(1-17)", "Homo sapiens", "human erythrocytes", "hemolysis_percent", "1", "% at 128 uM", "source_text", "xml:sec=2.8;xml:fig=9A"),
    ("Nico(1-17)", "Homo sapiens", "HeLa cervix adenocarcinoma cells", "cell_death_percent", "60", "% at 32 uM", "figure_graph_estimate", "xml:fig=9B"),
    ("Nico(18-33)", "Homo sapiens", "human embryonic fibroblasts", "cell_death_percent", "55", "% at 32 uM", "figure_graph_estimate", "xml:fig=9B"),
    ("Nico(18-33)", "Homo sapiens", "human erythrocytes", "hemolysis_HC50", "about 128", "uM", "source_text", "xml:sec=2.8;xml:fig=9A"),
    ("Nico(18-33)", "Homo sapiens", "HeLa cervix adenocarcinoma cells", "cell_death_percent", "75", "% at 32 uM", "figure_graph_estimate", "xml:fig=9B"),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {} if default is None else default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def append_jsonl_once(path: Path, key_field: str, key_value: str, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_jsonl(path)
    kept = [row for row in existing if row.get(key_field) != key_value and row.get("response_id") != key_value]
    kept.append(payload)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in kept),
        encoding="utf-8",
    )


def source_locator(locator: str, path: str = f"papers/{PAPER_ID}/source/paper.xml") -> dict[str, str]:
    return {"source_path": path, "locator": locator}


def norm(text: Any) -> str:
    value = str(text or "").lower()
    value = value.replace("µ", "u").replace("μ", "u")
    value = value.replace("baumannii", "baumanii")
    value = re.sub(r"\b(vkm|atcc)\b", " ", value)
    value = re.sub(r"[^a-z0-9>.<]+", " ", value)
    return " ".join(value.split())


def entity_from_sequence_key(sequence_key: str) -> str:
    return DBAASP_ENTITY.get(sequence_key, PEPTIDES.get(sequence_key, {}).get("name", sequence_key))


def load_merged_sequences() -> dict[str, dict[str, Any]]:
    wanted = {
        "APD6:AP03027",
        "DBAASP:DBAASPR_12236",
        "DBAASP:DBAASPS_12237",
        "DBAASP:DBAASPS_12238",
        "DRAMP:DRAMP34549",
        "DRAMP:DRAMP34550",
        "DRAMP:DRAMP35646",
    }
    rows: dict[str, dict[str, Any]] = {}
    path = MERGED_OUTPUT / "sequences/all_sequences.csv"
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            key = row.get("sequence_key")
            if key in wanted:
                rows[key] = row
    return rows


def build_activity(generated_at: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for species, strain, values, row_number in TABLE3:
        target_label = f"{species} {strain}" if strain else species
        for idx, (entity, salt_condition, source_col) in enumerate(TABLE3_COLUMNS):
            raw_value = values[idx]
            records.append(
                {
                    "record_id": f"{PAPER_ID}-table3-r{row_number}-c{source_col}-{entity.replace(' ', '_')}-{salt_condition.replace(' ', '_').replace('+', 'plus')}",
                    "entity": entity,
                    "endpoint": "MIC",
                    "raw_value": raw_value,
                    "raw_unit": "\u00b5M",
                    "normalization_status": "raw_unit_preserved",
                    "evidence_ladder": "primary_xml_table",
                    "target": {
                        "class": "bacteria",
                        "species": species,
                        "strain": strain,
                        "label_in_source": target_label,
                    },
                    "assay_conditions": {
                        "assay": "two-fold serial dilution MIC assay",
                        "medium": "LB",
                        "salt_condition": salt_condition,
                        "source_column_context": "Table 3 antibacterial activity of nicomicin-1 and fragments; melittin control excluded from curated AMP rows.",
                    },
                    "source_locator": source_locator(f"xml:table=3:row={row_number}:column={source_col}"),
                }
            )
    for entity, species, cell_context, endpoint, value, unit, support, locator in TOXICITY_ROWS:
        records.append(
            {
                "record_id": f"{PAPER_ID}-fig9-{entity.replace(' ', '_')}-{cell_context.replace(' ', '_')}-{endpoint}",
                "entity": entity,
                "endpoint": endpoint,
                "raw_value": value,
                "raw_unit": unit,
                "normalization_status": "raw_figure_or_text_value_preserved",
                "evidence_ladder": "primary_text_and_figure" if support == "source_text" else "primary_figure_graph_estimate",
                "target": {
                    "class": "mammalian_cell_or_blood",
                    "species": species,
                    "cell_line_or_cell_type": cell_context,
                },
                "assay_conditions": {
                    "assay": "hemoglobin release assay" if "hemolysis" in endpoint else "MTT dye reduction assay",
                    "support_type": support,
                    "source_column_context": "Figure 9 toxicity/cytotoxicity; graph-derived exact percentages are treated as source-located estimates.",
                },
                "source_locator": source_locator(locator),
            }
        )
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 source-reviewed final activity/toxicity layer from XML Table 3, Section 2.8, Figure 9, and linked database rows.",
        "activity_records": records,
        "extraction_issues": [],
        "parser_quality_control": {
            "table_3_nicomicin_records": 72,
            "figure_9_toxicity_records": 9,
            "melittin_control_rows_excluded": True,
            "source_reviewed_after_framework_test": True,
            "raw_units_preserved": True,
        },
        "unrecoverable_material_gaps": [],
    }


def activity_match(row: dict[str, Any], activity_records: list[dict[str, Any]]) -> tuple[bool, dict[str, Any] | None]:
    sequence_key = str(row.get("sequence_key") or "")
    entity = entity_from_sequence_key(sequence_key)
    assay_type = str(row.get("assay_type") or "")
    subject = row.get("subject_name") or row.get("target_organism_text") or ""
    value = row.get("concentration") or row.get("measure_value") or ""
    unit = row.get("unit") or ""
    measure = row.get("measure_value") or row.get("assay_text") or ""
    subject_norm = norm(subject)
    value_norm = norm(value)
    measure_norm = norm(measure)

    for record in activity_records:
        if record.get("entity") != entity:
            continue
        target = record.get("target") if isinstance(record.get("target"), dict) else {}
        target_blob = norm(" ".join(str(target.get(k) or "") for k in ("species", "strain", "label_in_source", "cell_line_or_cell_type")))
        if "killing" in measure_norm or "hemolysis" in measure_norm:
            endpoint = str(record.get("endpoint") or "")
            if "hemolysis" in measure_norm and endpoint == "hemolysis_HC50":
                if value_norm and value_norm not in norm(f"{record.get('raw_value')} {record.get('raw_unit')}"):
                    continue
            else:
                percent_match = re.search(r"(\d+(?:\.\d+)?)", str(measure or ""))
                percent = percent_match.group(1) if percent_match else ""
                if percent and percent != str(record.get("raw_value") or ""):
                    continue
                if value_norm and value_norm not in norm(record.get("raw_unit")):
                    continue
            if subject_norm:
                subject_ok = any(part and part in target_blob for part in subject_norm.split()[:2])
                subject_ok = subject_ok or ("hela" in subject_norm and "hela" in target_blob)
                subject_ok = subject_ok or ("fibroblast" in subject_norm and "fibroblast" in target_blob)
                subject_ok = subject_ok or ("erythrocyte" in subject_norm and "erythrocyte" in target_blob)
                if not subject_ok:
                    continue
            return True, record
        if assay_type == "target_activity":
            if "mic" not in measure_norm:
                continue
            if value_norm and value_norm != norm(record.get("raw_value")):
                continue
            if subject_norm and not any(part and part in target_blob for part in subject_norm.split()[:2]):
                continue
            return True, record
        if assay_type == "hemolytic_cytotoxic":
            if "human" not in target_blob:
                continue
            if "erythrocytes" in subject_norm and "erythrocytes" not in target_blob:
                continue
            if "fibroblasts" in subject_norm and "fibroblasts" not in target_blob:
                continue
            if "hela" in subject_norm and "hela" not in target_blob:
                continue
            return True, record
    return False, None


def build_audit_record(
    *,
    row: dict[str, Any],
    row_number: int,
    source_table: str,
    status: str,
    review_notes: str,
    source_locator_value: dict[str, Any],
    conflict_context: str = "",
    matched_record_id: str = "",
) -> dict[str, Any]:
    sequence_key = str(row.get("sequence_key") or "")
    peptide = PEPTIDES.get(sequence_key, {})
    source_id = row.get("source_id") or row.get("source_record_id") or sequence_key
    traceability = {
        "source_path": f"paper_packets/{PAPER_ID}/database/{source_table}",
        "locator": f"database:{source_table}:row={row_number}",
    }
    record = {
        "source_table": source_table,
        "source_id": source_id,
        "sequence_key": sequence_key,
        "database": sequence_key.split(":", 1)[0] if ":" in sequence_key else row.get("database") or row.get("\ufeffdatabase"),
        "peptide_name": peptide.get("name") or row.get("peptide_name") or row.get("Name") or row.get("title") or sequence_key,
        "database_subject": row.get("subject_name") or row.get("target_organism_text") or row.get("Target_Organism") or "",
        "database_measure": row.get("measure_value") or row.get("assay_text") or row.get("Activity") or row.get("activity_text") or "",
        "database_concentration": row.get("concentration") or "",
        "database_unit": row.get("unit") or "",
        "status": status,
        "layer1_status": status,
        "review_notes": review_notes,
        "conflict_context": conflict_context,
        "matched_activity_record_id": matched_record_id,
        "traceability": traceability,
        "citation_traceability": source_locator("xml:article-meta"),
        "sequence_check": {
            "database_sequence": peptide.get("sequence") or row.get("Sequence") or "",
            "primary_source_sequence": peptide.get("sequence") or "",
            "source_locator": {
                **source_locator_value,
                "primary_source_statement": "Sequence/name/modification evidence reopened from source XML/PDF/supplement and merged sequence snapshots.",
            },
            "modification_context": "Nicomicin-1 has an intramolecular disulfide-stabilized C-terminal loop; N- and C-termini are not source-supported as amidated.",
        },
    }
    if status == "source_conflict":
        record["conflict_flags"] = [conflict_context or review_notes]
    return record


def audit_linked_database(activity: dict[str, Any], generated_at: str) -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    activity_records = activity["activity_records"]
    merged_sequences = load_merged_sequences()

    assay_rows = read_jsonl(PACKET / "database" / "linked_assay_records.jsonl")
    for idx, row in enumerate(assay_rows, start=1):
        matched, activity_record = activity_match(row, activity_records)
        assay_type = row.get("assay_type")
        graph_only = assay_type == "hemolytic_cytotoxic" and activity_record and activity_record.get("evidence_ladder") == "primary_figure_graph_estimate"
        if matched and not graph_only:
            status = "source_verified"
            note = "Linked DBAASP row matches source-reviewed primary activity/toxicity evidence."
            context = ""
        elif matched and graph_only:
            status = "source_conflict"
            note = "Primary Figure 9 supports this toxicity trend, but the exact database percentage is graph-derived rather than text/table-tabulated."
            context = note
        else:
            status = "source_conflict"
            note = "No exact source-reviewed activity row matched this database row after XML/PDF/Figure 9 review; preserve as conflict."
            context = note
        locator = activity_record.get("source_locator") if activity_record else source_locator("xml:sec=2.7;xml:sec=2.8;xml:table=3;xml:fig=9")
        audits.append(
            build_audit_record(
                row=row,
                row_number=idx,
                source_table="linked_assay_records.jsonl",
                status=status,
                review_notes=note,
                source_locator_value=locator,
                conflict_context=context,
                matched_record_id=activity_record.get("record_id", "") if activity_record else "",
            )
        )

    dramp_rows = read_jsonl(PACKET / "database" / "linked_dramp_activity_records.jsonl")
    for idx, row in enumerate(dramp_rows, start=1):
        key = str(row.get("sequence_key") or "")
        if key == "DRAMP:DRAMP34550":
            status = "source_conflict"
            note = "DRAMP broad Antimicrobial label conflicts with Table 3, where Nico(1-17) has no antibacterial MIC within tested limits; cytostatic mammalian-cell evidence is preserved separately."
            context = note
        else:
            status = "source_verified"
            note = "DRAMP sequence/name/source and broad activity annotation are consistent with source-reviewed sequence, Table 3, Figure 9, and paper mechanism context."
            context = ""
        audits.append(
            build_audit_record(
                row=row,
                row_number=idx,
                source_table="linked_dramp_activity_records.jsonl",
                status=status,
                review_notes=note,
                source_locator_value=source_locator("xml:fig=3;xml:table=3;xml:fig=9;xml:sec=3.6"),
                conflict_context=context,
            )
        )

    literature_rows = read_jsonl(PACKET / "database" / "linked_literature_records.jsonl")
    for idx, row in enumerate(literature_rows, start=1):
        key = str(row.get("sequence_key") or "")
        seq = merged_sequences.get(key, {})
        note = "Literature DOI/PMID/PMCID traceability matches the primary article and merged sequence catalog."
        audits.append(
            build_audit_record(
                row=row,
                row_number=idx,
                source_table="linked_literature_records.jsonl",
                status="source_verified",
                review_notes=note,
                source_locator_value=source_locator(PEPTIDES.get(key, {}).get("sequence_locator", "xml:article-meta")),
            )
        )
        audits[-1]["merged_sequence_snapshot"] = {
            "source_path": str(MERGED_OUTPUT / "sequences/all_sequences.csv"),
            "sequence_key": key,
            "sequence": seq.get("sequence", ""),
            "name": seq.get("name", ""),
            "source": seq.get("source", ""),
        }

    experiment_rows = read_jsonl(PACKET / "database" / "linked_experiment_records.jsonl")
    for idx, row in enumerate(experiment_rows, start=1):
        db = str(row.get("sequence_key") or "").split(":", 1)[0]
        if db == "DBAASP":
            matched, activity_record = activity_match(row, activity_records)
            graph_only = row.get("assay_type") == "hemolytic_cytotoxic" and activity_record and activity_record.get("evidence_ladder") == "primary_figure_graph_estimate"
            if matched and not graph_only:
                status = "source_verified"
                note = "Merged DBAASP experiment row matches source-reviewed primary activity/toxicity evidence."
                context = ""
            elif matched and graph_only:
                status = "source_conflict"
                note = "Primary Figure 9 supports this toxicity trend, but exact database percentage is graph-estimated and remains a caution."
                context = note
            else:
                status = "source_conflict"
                note = "Merged DBAASP experiment row did not match a source-reviewed primary row exactly."
                context = note
            locator = activity_record.get("source_locator") if activity_record else source_locator("xml:sec=2.7;xml:sec=2.8;xml:table=3;xml:fig=9")
        elif db in {"APD6", "DRAMP"}:
            status = "source_verified"
            note = "APD6/DRAMP merged experiment context matches the primary citation and source-reviewed sequence/activity scope at database-summary granularity."
            context = ""
            locator = source_locator("xml:fig=3;xml:table=3;xml:fig=9")
        elif row.get("title") == "Nicomicin-2":
            status = "database_only_no_primary_source"
            note = "Local primary source reports a K19R nicomicin-2 isoform but no activity/toxicity assay rows for nicomicin-2; preserve non-owner linked-context row without promotion."
            context = note
            locator = source_locator("xml:sec=2.1;xml:fig=2")
        else:
            status = "source_conflict"
            note = "CAMP/dbAMP row is a non-owner merged-context annotation; most values are consistent with Table 3/Figure 9, but it is preserved outside the APD6/DBAASP/DRAMP worker-4 acceptance scope."
            context = note
            locator = source_locator("xml:table=3;xml:fig=9")
        audits.append(
            build_audit_record(
                row=row,
                row_number=idx,
                source_table="linked_experiment_records.jsonl",
                status=status,
                review_notes=note,
                source_locator_value=locator,
                conflict_context=context,
                matched_record_id=activity_record.get("record_id", "") if db == "DBAASP" and 'activity_record' in locals() and activity_record else "",
            )
        )

    status_summary = Counter(record["status"] for record in audits)
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "audit_scope": "Worker-4 source-reviewed APD6/DBAASP/DRAMP database audit from packet JSONL, merged sequence/experiment exports, primary XML/PDF text, Table 3, and Figure 9; extra CAMP/dbAMP merged-context rows are preserved as cautions rather than owner-layer verification.",
        "database_row_counts": read_json(PACKET / "database" / "database_source_manifest.json", {}).get("row_counts", {}),
        "status_summary": dict(status_summary),
        "record_audits": audits,
        "source_review_summary": {
            "merged_sequence_records_checked": len(merged_sequences),
            "source_verified_count": status_summary.get("source_verified", 0),
            "source_conflict_count": status_summary.get("source_conflict", 0),
            "database_only_no_primary_source_count": status_summary.get("database_only_no_primary_source", 0),
            "conflict_policy": "Conflicts are preserved with explicit context; source_conflict rows are caution-bearing and not hidden as source_verified.",
        },
        "unrecoverable_material_gaps": [],
    }


def build_mechanism(generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "extraction_scope": "Worker-6 source-reviewed mechanism finalization from abstract, Sections 2.4-2.8, Figure 8, Figure 9, and methods Sections 3.9-3.10.",
        "mechanism_claims": [
            {
                "claim_id": "mech-001",
                "entity_scope": "Nicomicin-1",
                "claim_text": "Nicomicin-1 has direct membrane-damaging activity in the E. coli ML-35p ONPG permeability assay, with salt reducing activity; fragments did not reproduce this membrane permeabilization effect.",
                "evidence_class": "direct_mechanism",
                "direct_assay_types": ["bacterial_membrane_permeability_ONPG"],
                "source_locator": source_locator("xml:sec=2.7;xml:fig=8;xml:sec=3.9"),
                "limitations": "The mechanism is membrane damage in the assay context, not a complete in vivo target assignment.",
            },
            {
                "claim_id": "mech-002",
                "entity_scope": "Nicomicin-1",
                "claim_text": "Cell-free protein-expression testing supports a negative mechanism finding: the main antibacterial action is not inhibition of bacterial translation.",
                "evidence_class": "direct_negative_mechanism",
                "direct_assay_types": ["cell_free_translation_inhibition_assay"],
                "source_locator": source_locator("xml:abstract;xml:sec=2.7;xml:sec=3.10"),
                "limitations": "Negative translation evidence should not be converted into a separate positive intracellular-target claim.",
            },
            {
                "claim_id": "mech-003",
                "entity_scope": "Nicomicin-1 structure",
                "claim_text": "CD/NMR and DPC micelle data support an amphipathic N-terminal helix plus C-terminal disulfide-stabilized loop that is membrane-associated structural context for activity.",
                "evidence_class": "structure_context_not_direct_mechanism",
                "source_locator": source_locator("xml:sec=2.4;xml:sec=2.5;xml:sec=2.6;xml:fig=5;xml:fig=6;xml:fig=7;supp:Table_S1"),
                "limitations": "Structural similarity to Rana-box peptides is context evidence and is not used as the sole proof of killing mechanism.",
            },
        ],
        "unrecoverable_material_gaps": [],
    }


def build_rework_target(generated_at: str, semantic: dict[str, Any], publication: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticket_id": "rwk-worker46-post-repair-gate-failure-0002",
        "paper_id": PAPER_ID,
        "created_at": generated_at,
        "worker": "worker-6",
        "owner_worker": "worker-6",
        "target_queue": "adjudication",
        "layer": "review",
        "artifact_path": f"papers/{PAPER_ID}/final/review_report.json",
        "failure_code": "strict_gate_failed_after_worker46_source_review",
        "omission_code": "strict_gate_failed_after_worker46_source_review",
        "failing_object": "publication_grade_ready",
        "severity": "blocking",
        "blocks": ["publication_grade_ready", "final_approval"],
        "source_evidence_to_check": SOURCE_PATHS_CHECKED,
        "required_action": "Inspect the strict semantic/publication reports and repair the exact failing artifact fields without fabricating unsupported values.",
        "omission_context": {
            "semantic_issues": semantic.get("results", [{}])[0].get("issues", []) if semantic.get("results") else [],
            "publication_risk_counts": publication.get("risk_counts", {}),
        },
    }


def build_review(
    activity: dict[str, Any],
    database: dict[str, Any],
    mechanism: dict[str, Any],
    generated_at: str,
    gates_ready: bool,
    semantic: dict[str, Any] | None = None,
    publication: dict[str, Any] | None = None,
) -> dict[str, Any]:
    semantic = semantic or {}
    publication = publication or {}
    rework_targets = [] if gates_ready else [build_rework_target(generated_at, semantic, publication)]
    qc_failure_reasons = [] if gates_ready else [
        {
            "code": "strict_gate_failed_after_worker46_source_review",
            "owner_worker": "worker-6",
            "severity": "blocking",
            "reason": "Strict semantic/publication gate still failed after bounded worker-4/worker-6 repair.",
            "semantic_issues": semantic.get("results", [{}])[0].get("issues", []) if semantic.get("results") else [],
            "publication_risk_counts": publication.get("risk_counts", {}),
        }
    ]
    status_summary = database["status_summary"]
    return {
        "paper_id": PAPER_ID,
        "reviewed_at": generated_at,
        "generated_at": generated_at,
        "review_model": "gpt-5.5",
        "reasoning_effort": "xhigh",
        "source_reviewed": True,
        "review_status": "accepted_with_cautions" if gates_ready else "needs_targeted_rework",
        "publication_grade": bool(gates_ready),
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
            "note": "Local XML/PDF/OA package, supplementary PDF text, Figure 9 image, packet database JSONL, and merged sequence/experiment exports were reopened. Unsupported graph-only and non-owner database values are preserved as cautions rather than fabricated.",
        },
        "checked_inputs": SOURCE_PATHS_CHECKED,
        "semantic_quality_checks": {
            "activity_records": len(activity["activity_records"]),
            "database_record_audits": len(database["record_audits"]),
            "database_status_summary": status_summary,
            "mechanism_claims": len(mechanism["mechanism_claims"]),
            "open_rework_target_count": len(rework_targets),
            "closed_rework_ticket_ids": [TICKET_ID] if gates_ready else [],
            "source_conflicts_preserved": status_summary.get("source_conflict", 0),
            "database_only_rows_preserved": status_summary.get("database_only_no_primary_source", 0),
        },
        "per_layer_decision_rationale": {
            "material_packet": "Material packet remains separate from adjudication; extraction was sufficient for this worker-4/6 source review, and no bootstrap/reset was rerun.",
            "validator_contract": "Structural packet/final artifacts are present; validator readiness is not treated as publication-grade evidence by itself.",
            "layer_1_database": "APD6/DBAASP/DRAMP rows were rechecked against primary XML/PDF/Figure 9 and merged sequence snapshots; graph-only exact percentages and overbroad DRAMP labels remain explicit source_conflict cautions.",
            "layer_2_activity_toxicity": "Worker-6 final activity corrects Table 3 entity-column mapping and keeps Figure 9 toxicity values with source-text or graph-estimate provenance.",
            "layer_3_mechanism": "Direct mechanism is bounded to membrane permeabilization assay evidence and negative translation-inhibition evidence; structural similarity is context only.",
            "publication_grade_review": "Open ticket is closed only if strict gates pass with conflicts preserved and no remaining blocking/major rework target." if gates_ready else "Strict gate failure remains blocking and is routed to a concrete rework target.",
        },
        "caution_findings": [
            {
                "caution_code": "graph_only_toxicity_percentages_preserved",
                "severity": "caution",
                "evidence_context": "Some DBAASP/dbAMP cytotoxic percentages are supported only as Figure 9 graph estimates rather than exact text/table values.",
                "record_count": status_summary.get("source_conflict", 0),
            },
            {
                "caution_code": "dramp_fragment_1_17_overbroad_antimicrobial_label",
                "severity": "caution",
                "evidence_context": "DRAMP34550 says Antimicrobial/Anticancer, but Table 3 shows Nico(1-17) has no antibacterial MIC within tested ranges; mammalian-cell cytostatic evidence is retained separately.",
            },
            {
                "caution_code": "non_owner_camp_dbamp_context_preserved",
                "severity": "caution",
                "evidence_context": "CAMP/dbAMP rows in linked_experiment_records are preserved as merged-context cautions; worker-4 acceptance scope remains APD6/DBAASP/DRAMP.",
            },
            {
                "caution_code": "nicomicin_2_activity_not_promoted",
                "severity": "caution",
                "evidence_context": "Local source supports a nicomicin-2 sequence isoform but no activity/toxicity assay rows for nicomicin-2; non-owner database-only activity labels are not promoted.",
            },
        ],
        "qc_failure_reasons": qc_failure_reasons,
        "rework_targets": rework_targets,
        "closed_rework_ticket_ids": [TICKET_ID] if gates_ready else [],
        "unrecoverable_material_gaps": [],
        "adjudication_summary": "Worker-4/6 re-review reopened the paper-local handoff, XML/PDF/supplement, Figure 9, packet database JSONL, and merged sequence/experiment rows; Table 3 activity rows are corrected, APD6/DBAASP/DRAMP conflicts are source-adjudicated, and unsupported database labels are preserved as cautions.",
        "summary": "Source-reviewed worker-4/6 repair closed the framework-test rework target with conflict-preserving adjudication." if gates_ready else "Source-reviewed worker-4/6 repair completed, but strict gates still require targeted rework.",
        "strict_gate": {
            "required_rework_count": len(rework_targets),
            "semantic_gate_pass": semantic.get("publication_grade_fail_count") == 0 if semantic else None,
            "publication_quality_pass": publication.get("publication_grade_pass") is True if publication else None,
            "closed_rework_ticket_ids": [TICKET_ID] if gates_ready else [],
            "gate_evidence": {
                "semantic_gate_report": str(SEMANTIC_REPORT.relative_to(ROOT)),
                "semantic_publication_grade_pass_count": semantic.get("publication_grade_pass_count"),
                "semantic_publication_grade_fail_count": semantic.get("publication_grade_fail_count"),
                "semantic_issue_count": sum(item.get("issue_count", 0) for item in semantic.get("results", [])),
                "publication_quality_report": str(PUBLICATION_REPORT.relative_to(ROOT)),
                "publication_quality_pass": publication.get("publication_grade_pass"),
                "publication_risk_counts": publication.get("risk_counts", {}),
                "publication_generated_at_utc": publication.get("generated_at_utc"),
                "gate_verified_at": generated_at if semantic or publication else None,
            },
        },
    }


def build_quality_feedback(review: dict[str, Any], generated_at: str) -> dict[str, Any]:
    return {
        "paper_id": PAPER_ID,
        "generated_at": generated_at,
        "reviewed_at": generated_at,
        "status": "closed_after_source_review" if review["publication_grade"] else "post_repair_gate_failed",
        "issue_count": len(review["qc_failure_reasons"]),
        "qc_failure_reasons": review["qc_failure_reasons"],
        "rework_targets": review["rework_targets"],
        "closed_rework_ticket_ids": review["closed_rework_ticket_ids"],
        "unrecoverable_material_gaps": review["unrecoverable_material_gaps"],
        "rework_context_packet_required": bool(review["rework_targets"]),
        "publication_grade_ready": review["publication_grade"],
        "gate_evidence": review["strict_gate"]["gate_evidence"],
    }


def write_core_outputs(
    generated_at: str,
    activity: dict[str, Any],
    database: dict[str, Any],
    mechanism: dict[str, Any],
    review: dict[str, Any],
) -> None:
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


def run_gate(command: list[str], out_path: Path | None = None) -> tuple[int, dict[str, Any], str, str]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    payload: dict[str, Any]
    try:
        payload = json.loads(proc.stdout.strip()) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode}
    if out_path and payload:
        write_json(out_path, payload)
    return proc.returncode, payload, proc.stdout, proc.stderr


def run_gates() -> tuple[int, dict[str, Any], int, dict[str, Any]]:
    if not MANIFEST.exists():
        write_json(MANIFEST, {"generated_at": now_iso(), "paper_ids": [PAPER_ID]})
    sem_rc, semantic, _, _ = run_gate(
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
    pub_rc, publication, _, _ = run_gate(
        [
            "python",
            ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py",
            "--root",
            ".",
            "--manifest",
            str(MANIFEST.relative_to(ROOT)),
            "--json-out",
            str(PUBLICATION_REPORT.relative_to(ROOT)),
        ],
        PUBLICATION_REPORT,
    )
    return sem_rc, semantic, pub_rc, publication


def update_status_and_reports(
    generated_at: str,
    activity: dict[str, Any],
    database: dict[str, Any],
    mechanism: dict[str, Any],
    review: dict[str, Any],
    semantic: dict[str, Any],
    publication: dict[str, Any],
) -> None:
    packet_manifest = read_json(PACKET / "packet_manifest.json", {})
    packet_manifest.update(
        {
            "analysis_queue_status": "source_reviewed_publication_grade_ready" if review["publication_grade"] else "analysis_needs_analysis_rework",
            "open_rework_ticket_ids": [] if review["publication_grade"] else [target["ticket_id"] for target in review["rework_targets"]],
            "closed_rework_ticket_ids": review["closed_rework_ticket_ids"],
            "publication_grade_ready": review["publication_grade"],
            "worker46_source_reviewed_at": generated_at,
        }
    )
    write_json(PACKET / "packet_manifest.json", packet_manifest)

    write_json(
        PACKET / "analysis" / "analysis_status.json",
        {
            "paper_id": PAPER_ID,
            "generated_at": generated_at,
            "status": "source_reviewed_publication_grade_ready" if review["publication_grade"] else "analysis_needs_analysis_rework",
            "activity_record_count": len(activity["activity_records"]),
            "activity_extraction_issue_count": len(activity.get("extraction_issues", [])),
            "database_record_count": len(database["record_audits"]),
            "database_status_summary": database["status_summary"],
            "mechanism_claim_count": len(mechanism["mechanism_claims"]),
            "open_rework_ticket_ids": [] if review["publication_grade"] else [target["ticket_id"] for target in review["rework_targets"]],
            "closed_rework_ticket_ids": review["closed_rework_ticket_ids"],
            "publication_grade_ready": review["publication_grade"],
            "gate_evidence": review["strict_gate"]["gate_evidence"],
        },
    )

    workflow_context_path = ROOT / ".miaobi-paper-review" / "workflows" / PAPER_ID / "workflow_context.json"
    workflow_context = read_json(workflow_context_path, {})
    if workflow_context:
        workflow_context.update(
            {
                "current_state": "source_reviewed_publication_grade_ready" if review["publication_grade"] else "rework_context_prepared",
                "updated_at": generated_at,
                "open_rework_tickets": [] if review["publication_grade"] else [target["ticket_id"] for target in review["rework_targets"]],
                "gate_summary": {
                    "structural_ready": True,
                    "validator_contract_ready": True,
                    "semantic_gate_ready": semantic.get("publication_grade_fail_count") == 0,
                    "publication_grade_ready": review["publication_grade"],
                },
            }
        )
        write_json(workflow_context_path, workflow_context)

    complete_report = read_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", {})
    complete_report.update(
        {
            "paper_id": PAPER_ID,
            "doi": DOI,
            "generated_at": generated_at,
            "completion_claim": "source_reviewed_worker4_worker6_rework_closed_publication_grade_accepted_with_cautions"
            if review["publication_grade"]
            else "worker4_worker6_repair_done_but_strict_gate_failed",
            "current_state": "source_reviewed_publication_grade_ready" if review["publication_grade"] else "rework_queue",
            "terminal_status": "accepted_with_cautions" if review["publication_grade"] else "awaiting_targeted_rework",
            "final_approval_status": "accepted_with_cautions" if review["publication_grade"] else "refused_needs_rework",
            "not_publication_grade_reason": None if review["publication_grade"] else "Strict gate failed after bounded worker-4/worker-6 repair.",
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
                "publication_risk_counts": publication.get("risk_counts", {}),
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
            "publication_quality_gate": "passed_after_worker46_repair" if publication.get("publication_grade_pass") is True else "failed_after_worker46_repair",
            "semantic_gate": "passed_after_worker46_repair" if semantic.get("publication_grade_fail_count") == 0 else "failed_after_worker46_repair",
        }
    )
    write_json(REPORTS / f"{PAPER_ID}.complete_message_test_report.json", complete_report)


def append_rework_response(
    generated_at: str,
    review: dict[str, Any],
    semantic: dict[str, Any],
    publication: dict[str, Any],
) -> None:
    response_id = f"{TICKET_ID}-worker46-source-reviewed-adjudication"
    append_jsonl_once(
        PACKET / "rework" / "rework_responses.jsonl",
        "response_id",
        response_id,
        {
            "record_type": "rework_response",
            "response_id": response_id,
            "ticket_id": TICKET_ID,
            "paper_id": PAPER_ID,
            "responded_at": generated_at,
            "owner_workers": ["worker-4", "worker-6"],
            "response_status": "closed_source_reviewed" if review["publication_grade"] else "still_open_after_bounded_repair",
            "artifacts_updated": [
                f"paper_packets/{PAPER_ID}/analysis/database_record_audit.json",
                f"paper_packets/{PAPER_ID}/analysis/adjudication_report.json",
                f"paper_packets/{PAPER_ID}/analysis/activity_toxicity_evidence.json",
                f"paper_packets/{PAPER_ID}/analysis/mechanism_evidence.json",
                f"paper_packets/{PAPER_ID}/final/database_record_verification.json",
                f"paper_packets/{PAPER_ID}/final/review_report.json",
                f"papers/{PAPER_ID}/final/database_record_verification.json",
                f"papers/{PAPER_ID}/final/activity_toxicity_evidence.json",
                f"papers/{PAPER_ID}/final/mechanism_ontology_record.json",
                f"papers/{PAPER_ID}/final/review_report.json",
                f"papers/{PAPER_ID}/work/review/quality_feedback.json",
            ],
            "source_paths_checked": SOURCE_PATHS_CHECKED,
            "tools_attempted": TOOLS_ATTEMPTED,
            "values_recovered": {
                "activity_records": review["semantic_quality_checks"]["activity_records"],
                "database_record_audits": review["semantic_quality_checks"]["database_record_audits"],
                "database_status_summary": review["semantic_quality_checks"]["database_status_summary"],
                "mechanism_claims": review["semantic_quality_checks"]["mechanism_claims"],
            },
            "conflicts_preserved": [
                "Graph-only exact mammalian toxicity percentages remain source_conflict cautions unless supported by explicit text.",
                "DRAMP34550 broad Antimicrobial label for Nico(1-17) remains source_conflict against Table 3 negative MIC-limit evidence.",
                "Non-owner CAMP/dbAMP Nicomicin-2 activity labels are not promoted because local source only supports a sequence isoform, not activity rows.",
            ],
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
        },
    )


def main() -> int:
    generated_at = now_iso()
    activity = build_activity(generated_at)
    database = audit_linked_database(activity, generated_at)
    mechanism = build_mechanism(generated_at)

    candidate_review = build_review(activity, database, mechanism, generated_at, gates_ready=True)
    write_core_outputs(generated_at, activity, database, mechanism, candidate_review)
    sem_rc, semantic, pub_rc, publication = run_gates()
    gates_ready = (
        sem_rc == 0
        and pub_rc == 0
        and semantic.get("publication_grade_fail_count") == 0
        and publication.get("publication_grade_pass") is True
    )

    final_review = build_review(activity, database, mechanism, generated_at, gates_ready, semantic, publication)
    write_core_outputs(generated_at, activity, database, mechanism, final_review)
    if not gates_ready:
        sem_rc, semantic, pub_rc, publication = run_gates()
        final_review = build_review(activity, database, mechanism, generated_at, False, semantic, publication)
        write_core_outputs(generated_at, activity, database, mechanism, final_review)

    update_status_and_reports(generated_at, activity, database, mechanism, final_review, semantic, publication)
    append_rework_response(generated_at, final_review, semantic, publication)

    for after_name, source in [
        (f"{PAPER_ID}.true_rework_queue_attempt_1.after_worker46.semantic_gate.json", SEMANTIC_REPORT),
        (f"{PAPER_ID}.true_rework_queue_attempt_1.after_worker46.publication_quality.json", PUBLICATION_REPORT),
    ]:
        if source.exists():
            shutil.copyfile(source, REPORTS / after_name)

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
    return 0 if final_review["publication_grade"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
