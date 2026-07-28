#!/usr/bin/env python3
"""Assess how much of the current AMP evidence corpus can support DesignToxBench.

The report deliberately separates:

1. high-confidence paper-level design candidates identified from explicit titles;
2. analogue/optimization candidates that still need origin adjudication;
3. sequence-ready safety candidates;
4. publication-ready benchmark gold, which requires fields not present today.

Only Python's standard library is used so the assessment is reproducible in the
current project environment.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo


CANONICAL_AA = re.compile(r"^[ACDEFGHIKLMNPQRSTVWY]+$", re.IGNORECASE)
CANCER_MARKER = re.compile(
    r"cancer|tumou?r|carcinoma|leukemi|lymphoma|melanoma|sarcoma|glioma|"
    r"adenocarcinoma|\bhela\b|\ba549\b|\bmcf[- ]?7\b|\bpc[- ]?3\b",
    re.IGNORECASE,
)
NORMAL_CELL_MARKER = re.compile(
    r"normal|non[- ]?cancer|healthy|fibroblast|keratinocyte|hepatocyte|"
    r"splenocyte|hek[- ]?293|hacat|huvec",
    re.IGNORECASE,
)
HOST_CELL_MARKER = re.compile(
    r"\bhuman\b|homo sapiens|\bmurine\b|\bmouse\b|\brat\b|mammal|cell line|fibroblast|"
    r"keratinocyte|hepatocyte|splenocyte|epithelial|endothelial|macrophage|"
    r"hek[- ]?293|hacat|huvec|hmec|l929|raw 264",
    re.IGNORECASE,
)
MICROBIAL_MARKER = re.compile(
    r"biofilm|bacter|staphyl|pseudomon|escherichia|candida|fung|yeast|microb",
    re.IGNORECASE,
)


def increase_csv_field_limit() -> None:
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit //= 10


def normalize_text(value: Any) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(value or "")
        .replace("‐", "-")
        .replace("‑", "-")
        .replace("–", "-"),
    ).strip()


def normalize_sequence(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "")).upper()


def is_short_canonical_sequence(sequence: str, max_length: int) -> bool:
    return bool(CANONICAL_AA.fullmatch(sequence) and len(sequence) <= max_length)


def read_tsv(path: Path) -> Iterable[dict[str, str]]:
    with path.open(
        newline="", encoding="utf-8-sig", errors="replace"
    ) as handle:
        yield from csv.DictReader(handle, delimiter="\t")


def paper_xml_metadata(project_root: Path, paper_id: str) -> dict[str, str]:
    path = project_root / "papers" / paper_id / "source" / "paper.xml"
    result = {"title": "", "publication_year": "", "xml_doi": ""}
    if not path.exists():
        return result

    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return result

    title_node = root.find(".//article-title")
    if title_node is not None:
        result["title"] = normalize_text("".join(title_node.itertext()))

    years = [
        normalize_text("".join(node.itertext()))
        for node in root.findall(".//pub-date/year")
        if normalize_text("".join(node.itertext()))
    ]
    if not years:
        years = [
            normalize_text("".join(node.itertext()))
            for node in root.findall(".//year")
            if normalize_text("".join(node.itertext()))
        ]
    result["publication_year"] = years[0] if years else ""

    for node in root.findall(".//article-id"):
        if node.attrib.get("pub-id-type") == "doi":
            result["xml_doi"] = normalize_text("".join(node.itertext()))
            break
    return result


def classify_design_title(title: str) -> str:
    """Return a deliberately conservative paper-level design category.

    This is a candidate-mining rule, not an entity-level gold label.
    """

    text = normalize_text(title).lower()
    if not re.search(r"peptid|peptoid|miniprotein", text):
        return ""

    model_marker = re.search(
        r"prompt diffusion|latent diffusion|diffusion[- ]driven|"
        r"generative adversarial|variational autoencoder|generative model|"
        r"broadamp-gpt|dlfea4ampgen|"
        r"recurrent neural network|machine learning|deep learning|"
        r"artificial intelligence",
        text,
    )
    design_action = re.search(
        r"design|generat|directed evolution|optim(?:iz|is)|"
        r"de novo-development",
        text,
    )
    if model_marker and design_action:
        return "generative_or_ml_design"

    if re.search(
        r"\b(?:de[ -]?novo design|de[ -]?novo designed|"
        r"de[ -]?novo synthetic .*? design|rational(?:ly)? design|"
        r"rational designed|computer-aided design|computational design|"
        r"in silico design|in silico[- ]based discovery|ab initio designed|"
        r"artificial(?:ly)? designed|"
        r"designed antimicrobial peptide|redesigning .*?peptide|"
        r"design(?:,| and| of).*?peptid|engineering of .*?peptid|"
        r"engineered .*?peptid)",
        text,
    ):
        return "explicit_rational_or_de_novo_design"

    if re.search(
        r"analog(?:ue)?s?|derivatives?|substitut|mutant|truncat|"
        r"hybrid peptid|chimeric peptid|stapled peptid|lipidation|"
        r"directed evolution|optim(?:iz|is).*?peptid",
        text,
    ):
        return "analogue_or_optimization_candidate"
    return ""


def classify_safety_endpoint(row: dict[str, str]) -> str:
    """Classify only from endpoint semantics plus target orientation.

    Generic IC50/EC50 values are intentionally excluded. Cancer-cell viability
    is treated as efficacy unless a normal-cell marker is also present.
    """

    endpoint = normalize_text(row.get("endpoint")).lower().replace("_", " ")
    target = normalize_text(row.get("target")).lower()
    assay = normalize_text(row.get("assay_conditions")).lower()

    if re.search(
        r"ha?emol|\bhc\s*\d+\b|\bmhc\b|erythrocy|red blood|\brbc\b",
        endpoint,
    ):
        return "hemolysis"

    is_cell_endpoint = bool(
        re.search(
            r"cytotox|\bcc\s*\d+\b|cell viability|cell survival|"
            r"cck[- ]?8|\bmtt\b|\bldh\b",
            endpoint,
        )
    )
    target_context = f"{target} | {assay}"
    microbial_only = bool(
        MICROBIAL_MARKER.search(f"{endpoint} | {target_context}")
    ) and not bool(HOST_CELL_MARKER.search(target_context))
    if is_cell_endpoint and microbial_only:
        return ""
    cancer_only = bool(CANCER_MARKER.search(target_context)) and not bool(
        NORMAL_CELL_MARKER.search(target_context)
    )
    if is_cell_endpoint and not cancer_only:
        return "cytotoxicity_or_cell_viability"

    if re.search(
        r"acute toxicity|organ toxicity|histopath|body weight|"
        r"embryo toxicity|zebrafish toxicity|mortality|tolerability|"
        r"adverse effect",
        endpoint,
    ):
        return "other_explicit_safety"
    return ""


def classify_activity_endpoint(row: dict[str, str]) -> str:
    endpoint = normalize_text(row.get("endpoint")).lower().replace("_", " ")
    target = normalize_text(row.get("target")).lower()

    if re.search(
        r"\bmic(?:50|90)?\b|\bmbc\b|\bmfc\b|\bmbec\b|\bmbic\b|"
        r"\bfic(?:i)?\b|inhibition zone|killing percent|cfu reduction|"
        r"antibacterial|antimicrobial|antifungal|antiviral|antibiofilm",
        endpoint,
    ):
        return "activity"

    cancer_activity = re.search(
        r"anticancer|antitumou?r|anti-prolifer", endpoint
    ) or (
        re.search(r"\b(?:ic50|ec50|cell viability|cytotox)", endpoint)
        and CANCER_MARKER.search(target)
    )
    return "activity" if cancer_activity else ""


def has_explicit_row_design_marker(row: dict[str, str]) -> bool:
    text = " | ".join(
        normalize_text(row.get(field))
        for field in ("entity_type", "entity", "peptide", "curation_notes")
    )
    return bool(
        re.search(
            r"\b(?:de[ -]?novo|designed|engineered|generated|generative|"
            r"artificial|computer[- ]designed|machine[- ]learning[- ]designed|"
            r"ai[- ](?:aided|designed)|rationally designed|ab initio)\b",
            text,
            re.IGNORECASE,
        )
    )


def has_censor_or_inequality(row: dict[str, str]) -> bool:
    text = " | ".join(
        normalize_text(row.get(field))
        for field in ("raw_value", "normalization_status")
    )
    return bool(
        re.search(
            r"(^|[\s;|])(?:[<>]=?|≤|≥)|not "
            r"(?:reached|detected|determined|observed)|no activity|inactive|"
            r"below detection|above (?:the )?limit|\b(?:nd|n\.d\.)\b|"
            r"upper bound|lower bound|inequal|censor",
            text,
            re.IGNORECASE,
        )
    )


def entity_key(row: dict[str, Any]) -> tuple[str, str]:
    identity = (
        row["_sequence"]
        or normalize_text(row.get("peptide"))
        or normalize_text(row.get("entity"))
    )
    return row["paper_id"], identity


def aggregate(
    paper_ids: set[str],
    rows_by_paper: dict[str, list[dict[str, Any]]],
    max_length: int,
) -> dict[str, Any]:
    rows = [
        row
        for paper_id in paper_ids
        for row in rows_by_paper.get(paper_id, [])
    ]
    safety_rows = [row for row in rows if row["_safety_family"]]
    activity_rows = [row for row in rows if row["_activity_family"]]

    def short_sequences(
        selected_rows: Iterable[dict[str, Any]],
    ) -> set[str]:
        return {
            row["_sequence"]
            for row in selected_rows
            if is_short_canonical_sequence(row["_sequence"], max_length)
        }

    safety_sequences = short_sequences(safety_rows)
    activity_sequences = short_sequences(activity_rows)
    safety_paper_sequence_keys = {
        (row["paper_id"], row["_sequence"])
        for row in safety_rows
        if is_short_canonical_sequence(row["_sequence"], max_length)
    }
    activity_paper_sequence_keys = {
        (row["paper_id"], row["_sequence"])
        for row in activity_rows
        if is_short_canonical_sequence(row["_sequence"], max_length)
    }
    paired_paper_sequence_keys = (
        safety_paper_sequence_keys & activity_paper_sequence_keys
    )
    paired_entity_keys = {
        entity_key(row) for row in safety_rows
    } & {entity_key(row) for row in activity_rows}

    return {
        "papers": len(paper_ids),
        "release_observation_rows": len(rows),
        "short_canonical_sequences": len(short_sequences(rows)),
        "safety_rows": len(safety_rows),
        "safety_papers": len({row["paper_id"] for row in safety_rows}),
        "sequence_ready_safety_papers": len(
            {
                row["paper_id"]
                for row in safety_rows
                if is_short_canonical_sequence(row["_sequence"], max_length)
            }
        ),
        "safety_short_canonical_sequences": len(safety_sequences),
        "activity_rows": len(activity_rows),
        "activity_papers": len({row["paper_id"] for row in activity_rows}),
        "activity_short_canonical_sequences": len(activity_sequences),
        "paired_activity_safety_paper_sequence_keys": len(
            paired_paper_sequence_keys
        ),
        "paired_activity_safety_unique_sequences": len(
            {sequence for _, sequence in paired_paper_sequence_keys}
        ),
        "paired_activity_safety_paper_entity_keys": len(paired_entity_keys),
        "explicit_row_design_safety_rows": sum(
            bool(row["_explicit_row_design"]) for row in safety_rows
        ),
        "explicit_row_design_safety_short_sequences": len(
            {
                row["_sequence"]
                for row in safety_rows
                if row["_explicit_row_design"]
                and is_short_canonical_sequence(row["_sequence"], max_length)
            }
        ),
        "censored_or_inequality_safety_rows": sum(
            bool(row["_censored"]) for row in safety_rows
        ),
        "safety_rows_with_raw_value": sum(
            bool(normalize_text(row.get("raw_value"))) for row in safety_rows
        ),
        "safety_rows_with_normalized_value": sum(
            bool(normalize_text(row.get("normalized_value")))
            for row in safety_rows
        ),
        "safety_rows_with_source_locator": sum(
            bool(normalize_text(row.get("source_locator")))
            for row in safety_rows
        ),
        "safety_endpoint_families": dict(
            Counter(row["_safety_family"] for row in safety_rows)
        ),
        "_safety_sequences": sorted(safety_sequences),
    }


def public_release_summary(
    paper_rows: list[dict[str, str]],
    activity_rows: list[dict[str, Any]],
    max_length: int,
) -> dict[str, int]:
    public_rows = [
        row
        for row in activity_rows
        if row["public_v1_included"].lower() == "true"
    ]
    all_sequences = {
        row["_sequence"] for row in activity_rows if row["_sequence"]
    }
    public_sequences = {
        row["_sequence"] for row in public_rows if row["_sequence"]
    }
    return {
        "paper_rows": len(paper_rows),
        "public_papers": sum(
            row["public_v1_included"].lower() == "true"
            for row in paper_rows
        ),
        "activity_rows": len(activity_rows),
        "public_activity_rows": len(public_rows),
        "activity_papers": len({row["paper_id"] for row in activity_rows}),
        "public_activity_papers": len(
            {row["paper_id"] for row in public_rows}
        ),
            "unique_normalized_nonempty_sequences": len(all_sequences),
            "public_unique_normalized_nonempty_sequences": len(
                public_sequences
            ),
        "public_short_canonical_sequences": len(
            {
                sequence
                for sequence in public_sequences
                if is_short_canonical_sequence(sequence, max_length)
            }
        ),
    }


def temporal_summary(
    paper_ids: set[str],
    papers: dict[str, dict[str, str]],
    rows_by_paper: dict[str, list[dict[str, Any]]],
    max_length: int,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for cutoff in (2023, 2024, 2025):
        selected = {
            paper_id
            for paper_id in paper_ids
            if papers[paper_id]["publication_year"].isdigit()
            and int(papers[paper_id]["publication_year"]) >= cutoff
            and any(
                row["_safety_family"]
                for row in rows_by_paper.get(paper_id, [])
            )
        }
        result = aggregate(selected, rows_by_paper, max_length)
        result.pop("_safety_sequences")
        output[f"publication_year_gte_{cutoff}"] = result
    return output


def external_merged_summary(
    merged_root: Path, design_safety_sequences: set[str]
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "available": False,
        "path": str(merged_root),
    }
    sequence_path = merged_root / "sequences" / "all_sequences.csv"
    five_database_path = (
        merged_root / "experiments" / "five_database_analysis_summary.json"
    )
    literature_path = merged_root / "summary.json"
    if not sequence_path.exists():
        return result

    merged_sequences: set[str] = set()
    sequence_rows = 0
    synthesis_type = Counter()
    with sequence_path.open(
        newline="", encoding="utf-8-sig", errors="replace"
    ) as handle:
        for row in csv.DictReader(handle):
            sequence_rows += 1
            sequence = normalize_sequence(row.get("sequence"))
            if sequence:
                merged_sequences.add(sequence)
            synthesis_type[normalize_text(row.get("synthesis_type"))] += 1

    overlap = design_safety_sequences & merged_sequences
    result.update(
        {
            "available": True,
            "three_database_sequence_rows": sequence_rows,
            "three_database_unique_normalized_sequence_strings": len(
                merged_sequences
            ),
            "synthesis_type_counts": dict(synthesis_type),
            "design_safety_sequence_exact_overlap": len(overlap),
            "design_safety_sequence_exact_nonoverlap": len(
                design_safety_sequences - overlap
            ),
            "overlap_denominator": len(design_safety_sequences),
            "warning": (
                "This is exact sequence overlap with the current merged "
                "database universe, not a homology or natural-origin test."
            ),
        }
    )
    if five_database_path.exists():
        result["five_database_analysis"] = json.loads(
            five_database_path.read_text(encoding="utf-8")
        )
    if literature_path.exists():
        result["three_database_corpus_summary"] = json.loads(
            literature_path.read_text(encoding="utf-8")
        )
    return result


def strict_incremental_summary(
    project_root: Path,
    rc2_dois: set[str],
    max_length: int,
) -> dict[str, Any]:
    state_path = (
        project_root
        / "pipeline_v2"
        / "deepmine"
        / "dbaasp_strict_pilot"
        / "manifests"
        / "remaining_200_strict_review_state_20260726.json"
    )
    result: dict[str, Any] = {
        "available": False,
        "state_path": str(state_path.relative_to(project_root)),
    }
    if not state_path.exists():
        return result

    state = json.loads(state_path.read_text(encoding="utf-8"))
    design_candidates = [
        paper
        for paper in state.get("papers", [])
        if classify_design_title(paper.get("title", ""))
        in {
            "generative_or_ml_design",
            "explicit_rational_or_de_novo_design",
        }
    ]
    terminal = [
        paper
        for paper in design_candidates
        if paper.get("workflow_status")
        == "terminal_scientific_review_complete"
    ]

    terminal_details: list[dict[str, Any]] = []
    total_activity = 0
    total_toxicity = 0
    terminal_sequences: set[str] = set()
    for paper in terminal:
        paper_id = paper["paper_id"]
        evidence_path = (
            project_root
            / "pipeline_v2"
            / "deepmine"
            / "dbaasp_strict_pilot"
            / "papers"
            / paper_id
            / "final"
            / "activity_toxicity_evidence.json"
        )
        activity_records: list[dict[str, Any]] = []
        toxicity_records: list[dict[str, Any]] = []
        if evidence_path.exists():
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            activity_records = evidence.get("activity_records", [])
            toxicity_records = evidence.get("toxicity_records", [])

        paper_sequences: set[str] = set()
        for record in activity_records + toxicity_records:
            sequence = normalize_sequence(
                record.get("sequence")
                or record.get("peptide_sequence")
                or record.get("amino_acid_sequence")
            )
            if is_short_canonical_sequence(sequence, max_length):
                paper_sequences.add(sequence)
                terminal_sequences.add(sequence)

        doi = normalize_text(paper.get("doi")).lower()
        total_activity += len(activity_records)
        total_toxicity += len(toxicity_records)
        terminal_details.append(
            {
                "paper_id": paper_id,
                "doi": paper.get("doi", ""),
                "title": paper.get("title", ""),
                "design_category": classify_design_title(
                    paper.get("title", "")
                ),
                "activity_records": len(activity_records),
                "toxicity_records": len(toxicity_records),
                "short_canonical_sequences": len(paper_sequences),
                "already_in_rc2_by_doi": bool(doi and doi in rc2_dois),
                "evidence_path": str(evidence_path.relative_to(project_root)),
            }
        )

    result.update(
        {
            "available": True,
            "state_updated_at": state.get("updated_at"),
            "frozen_denominator": state.get("frozen_denominator"),
            "terminal_papers_all_topics": state.get("counts", {}).get(
                "terminal_scientific_review_complete"
            ),
            "high_confidence_design_candidate_papers": len(
                design_candidates
            ),
            "terminal_high_confidence_design_papers": len(terminal),
            "nonterminal_high_confidence_design_candidates": len(
                design_candidates
            )
            - len(terminal),
            "terminal_design_activity_records": total_activity,
            "terminal_design_toxicity_records": total_toxicity,
            "terminal_design_short_canonical_sequences": len(
                terminal_sequences
            ),
            "terminal_papers": terminal_details,
            "release_boundary": (
                "Strict incremental artifacts are not part of RC2 and must "
                "not be silently merged into the public release."
            ),
        }
    )
    return result


def write_candidate_tsv(
    path: Path,
    paper_ids: set[str],
    papers: dict[str, dict[str, str]],
    rows_by_paper: dict[str, list[dict[str, Any]]],
    max_length: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "paper_id",
        "design_category",
        "publication_year",
        "xml_doi",
        "title",
        "release_observation_rows",
        "safety_rows",
        "safety_short_canonical_sequences",
        "activity_rows",
        "paired_activity_safety_paper_sequence_keys",
        "censored_or_inequality_safety_rows",
        "open_rework_ticket_count",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields)
        writer.writeheader()
        for paper_id in sorted(paper_ids):
            result = aggregate({paper_id}, rows_by_paper, max_length)
            paper = papers[paper_id]
            writer.writerow(
                {
                    "paper_id": paper_id,
                    "design_category": paper["design_category"],
                    "publication_year": paper["publication_year"],
                    "xml_doi": paper["xml_doi"],
                    "title": paper["title"],
                    "release_observation_rows": result[
                        "release_observation_rows"
                    ],
                    "safety_rows": result["safety_rows"],
                    "safety_short_canonical_sequences": result[
                        "safety_short_canonical_sequences"
                    ],
                    "activity_rows": result["activity_rows"],
                    "paired_activity_safety_paper_sequence_keys": result[
                        "paired_activity_safety_paper_sequence_keys"
                    ],
                    "censored_or_inequality_safety_rows": result[
                        "censored_or_inequality_safety_rows"
                    ],
                    "open_rework_ticket_count": paper.get(
                        "open_rework_ticket_count", ""
                    ),
                }
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--max-length", type=int, default=50)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-candidates-tsv", type=Path)
    parser.add_argument(
        "--merged-root",
        type=Path,
        default=Path(
            "/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output"
        ),
    )
    return parser.parse_args()


def main() -> int:
    increase_csv_field_limit()
    args = parse_args()
    project_root = args.project_root.resolve()
    release_root = project_root / "releases" / "amp_evidence_atlas_v1_rc2"
    papers_path = release_root / "papers.tsv"
    activity_path = release_root / "activity_observations.tsv"
    if not papers_path.exists() or not activity_path.exists():
        raise SystemExit("RC2 papers/activity files were not found")

    paper_rows = list(read_tsv(papers_path))
    papers: dict[str, dict[str, str]] = {}
    for row in paper_rows:
        metadata = paper_xml_metadata(project_root, row["paper_id"])
        papers[row["paper_id"]] = {
            **row,
            **metadata,
            "design_category": classify_design_title(metadata["title"]),
        }

    activity_rows: list[dict[str, Any]] = []
    rows_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for source_row in read_tsv(activity_path):
        row: dict[str, Any] = dict(source_row)
        row["_sequence"] = normalize_sequence(row.get("sequence"))
        row["_safety_family"] = classify_safety_endpoint(source_row)
        row["_activity_family"] = classify_activity_endpoint(source_row)
        row["_explicit_row_design"] = has_explicit_row_design_marker(
            source_row
        )
        row["_censored"] = has_censor_or_inequality(source_row)
        activity_rows.append(row)
        if row["public_v1_included"].lower() == "true":
            rows_by_paper[row["paper_id"]].append(row)

    category_paper_ids: dict[str, set[str]] = defaultdict(set)
    for paper_id, paper in papers.items():
        category = paper["design_category"]
        if category and paper["public_v1_included"].lower() == "true":
            category_paper_ids[category].add(paper_id)

    high_confidence_paper_ids = (
        category_paper_ids["generative_or_ml_design"]
        | category_paper_ids["explicit_rational_or_de_novo_design"]
    )
    analogue_paper_ids = category_paper_ids[
        "analogue_or_optimization_candidate"
    ]
    broad_paper_ids = high_confidence_paper_ids | analogue_paper_ids

    high_confidence = aggregate(
        high_confidence_paper_ids, rows_by_paper, args.max_length
    )
    high_confidence_safety_sequences = set(
        high_confidence.pop("_safety_sequences")
    )
    analogue = aggregate(
        analogue_paper_ids, rows_by_paper, args.max_length
    )
    analogue.pop("_safety_sequences")
    broad = aggregate(broad_paper_ids, rows_by_paper, args.max_length)
    broad.pop("_safety_sequences")

    by_category: dict[str, Any] = {}
    for category, paper_ids in sorted(category_paper_ids.items()):
        result = aggregate(paper_ids, rows_by_paper, args.max_length)
        result.pop("_safety_sequences")
        by_category[category] = result

    report = {
        "report_name": "DesignToxBench current-data support audit",
        "generated_at": datetime.now(
            ZoneInfo("Asia/Shanghai")
        ).isoformat(timespec="seconds"),
        "authority": {
            "release": "amp_evidence_atlas_v1_rc2",
            "papers_path": str(papers_path.relative_to(project_root)),
            "activity_path": str(activity_path.relative_to(project_root)),
            "rules": {
                "design_identity": (
                    "Explicit paper-title candidate rules. Paper-level "
                    "classification is not entity-level adjudication."
                ),
                "safety": (
                    "Endpoint-derived hemolysis, non-cancer-only "
                    "cytotoxicity/cell viability, and explicit other safety. "
                    "Generic IC50/EC50 is excluded."
                ),
                "sequence_ready": (
                    f"Canonical 20-amino-acid sequence length <= "
                    f"{args.max_length}."
                ),
                "pairing": (
                    "Activity and safety must share paper_id and sequence; "
                    "paper/entity pairing is also reported."
                ),
            },
        },
        "release_summary": public_release_summary(
            paper_rows, activity_rows, args.max_length
        ),
        "support_tiers": {
            "publication_ready_designtoxbench_gold": {
                "records": 0,
                "reason": (
                    "No entity-level design-origin adjudication, endpoint "
                    "threshold policy, canonical molecular identity, homology "
                    "split, temporal split manifest, or benchmark release "
                    "contract exists yet."
                ),
            },
            "high_confidence_design_paper_envelope": high_confidence,
            "analogue_or_optimization_enrichment_envelope": analogue,
            "broad_candidate_upper_envelope": broad,
        },
        "by_design_category": by_category,
        "temporal_candidate_envelopes": temporal_summary(
            high_confidence_paper_ids,
            papers,
            rows_by_paper,
            args.max_length,
        ),
        "external_merged_corpus": external_merged_summary(
            args.merged_root, high_confidence_safety_sequences
        ),
        "strict_incremental_not_in_rc2": strict_incremental_summary(
            project_root,
            {
                normalize_text(paper.get("xml_doi")).lower()
                for paper in papers.values()
                if normalize_text(paper.get("xml_doi"))
            },
            args.max_length,
        ),
        "benchmark_requirement_status": {
            "leave_paper_out": {
                "status": "directly_supported",
                "field": "paper_id",
            },
            "exact_sequence_deduplication": {
                "status": "partly_supported",
                "field": "sequence",
                "limitation": "Sequence is missing for many observations.",
            },
            "natural_train_designed_test": {
                "status": "requires_adjudication",
                "missing_fields": [
                    "natural_or_designed",
                    "entity_design_origin",
                    "parent_sequence",
                ],
            },
            "low_homology_test": {
                "status": "requires_derivation",
                "missing_fields": [
                    "canonical_molecular_identity",
                    "homology_cluster_id",
                    "max_train_test_identity",
                ],
            },
            "publication_time_split": {
                "status": "metadata_recoverable_not_in_release_table",
                "source": "papers/*/source/paper.xml",
            },
            "post_model_training_cutoff": {
                "status": "requires_model_provenance",
                "missing_fields": [
                    "model_training_cutoff",
                    "training_dataset_version",
                ],
            },
            "design_method_strata": {
                "status": "requires_adjudication",
                "missing_fields": [
                    "design_method",
                    "design_model",
                    "library_or_optimization_source",
                ],
            },
            "four_activity_safety_quadrants": {
                "status": "quantitative_pairing_available_labels_undefined",
                "missing_fields": [
                    "activity_label_policy",
                    "safety_label_policy",
                    "censor_operator",
                ],
            },
            "calibration_risk_coverage_high_confidence_errors": {
                "status": "model_evaluation_layer_not_source_data",
                "missing_fields": [
                    "prediction_probability",
                    "prediction_confidence",
                    "abstention_score",
                    "adjudicated_error_label",
                ],
            },
        },
        "critical_conflicts": [
            (
                "Synthetic assay or synthesis_type=Synthetic does not prove "
                "artificial sequence design."
            ),
            (
                "Paper-level design titles can contain a natural parent and "
                "designed variants; entity-level origin is still required."
            ),
            (
                "Endpoint spellings and assay semantics are heterogeneous; "
                "hemolysis, HC50, MHC, cell viability, and CC50 must not be "
                "collapsed without conditions."
            ),
            (
                "Cancer-cell cytotoxicity can be efficacy rather than safety."
            ),
            (
                "Inequalities and detection-limit records are preserved in "
                "raw text but have no common comparator/bounds schema."
            ),
            (
                "Random observation-level splits would leak the same peptide "
                "and paper across train and test."
            ),
            (
                "Most current high-confidence design safety sequences already "
                "exactly overlap the merged database universe; training-data "
                "version and time filtering are mandatory."
            ),
        ],
        "recommended_new_fields": [
            "benchmark_record_id",
            "canonical_peptide_id",
            "raw_sequence",
            "standardized_sequence",
            "modification",
            "stereochemistry",
            "cyclicity",
            "lipidation_or_conjugation",
            "paper_id",
            "doi",
            "pmid",
            "publication_date",
            "data_publication_date",
            "natural_or_designed",
            "entity_design_origin",
            "design_method",
            "design_model",
            "parent_sequence",
            "scaffold_or_library_id",
            "safety_endpoint_family",
            "activity_endpoint_family",
            "target_or_cell_type",
            "raw_value",
            "raw_unit",
            "value_operator",
            "lower_bound",
            "upper_bound",
            "is_censored",
            "label_definition",
            "homology_cluster_id",
            "max_train_test_identity",
            "split_group",
            "training_dataset_version",
            "model_training_cutoff",
        ],
    }

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.output_candidates_tsv:
        write_candidate_tsv(
            args.output_candidates_tsv,
            broad_paper_ids,
            papers,
            rows_by_paper,
            args.max_length,
        )

    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
