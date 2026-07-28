#!/usr/bin/env python3
"""Bridge DBAASP pending machine rows into a strict six-worker pilot.

This script does not promote DBAASP fallback rows into the release. It creates a
two-queue packet surface from the DBAASP worklist/source XML/PDF plus the Codex
fallback batch artifacts, then can launch independent Codex CLI worker-role
passes over that packet.
"""
from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
DEEPMINE = ROOT / "pipeline_v2" / "deepmine"
BASE = DEEPMINE / "dbaasp_strict_pilot"
DEFAULT_PAPER_IDS = ["PMC13036774", "PMC13036000"]

WORKLIST = DEEPMINE / "dbaasp_worklist.json"
MATERIAL_WORKLIST_OVERLAY = BASE / "manifests/material_recovery_worklist_overlay.json"
BATCH_ROWS = DEEPMINE / "dbaasp_codex_batch_20260708_1235_rows.tsv"
REVIEW_QUEUE = DEEPMINE / "dbaasp_codex_batch_20260708_1235_review_queue.tsv"
EMPTY_DONE = DEEPMINE / "dbaasp_empty_done.tsv"
DBAASP_EXTRACTED = DEEPMINE / "dbaasp_extracted.tsv"
SESSION_AUDIT = DEEPMINE / "dbaasp_codex_batch_20260708_1235_session_audit.tsv"
SESSION_AUDIT_JSON = DEEPMINE / "dbaasp_codex_batch_20260708_1235_session_audit.json"
BATCH_REPORT = DEEPMINE / "dbaasp_codex_batch_20260708_1235_report.json"

AUTHORITATIVE_DB_INPUTS = {
    "dbaasp_article_refs": Path("/mnt/d/work/抗菌肽/数据库/DBAASP/data/index/article_refs.csv"),
    "dbaasp_assay_refs": Path("/mnt/d/work/抗菌肽/数据库/DBAASP/data/index/assay_refs.csv"),
    "dbaasp_peptides_summary": Path("/mnt/d/work/抗菌肽/数据库/DBAASP/data/index/peptides_summary.csv"),
    "merged_dbaasp_assay_records": Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/experiments/dbaasp_assay_records.csv"),
    "merged_sequence_literature_links": Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/literature/sequence_literature_links.csv"),
    "merged_unique_literature_availability": Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/literature/unique_literature_availability.csv"),
    "merged_all_sequences": Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output/sequences/all_sequences.csv"),
}

CHECK_PACKET_SCRIPT = ROOT / ".codex/skills/paper-batch-orchestrator/scripts/check_two_queue_packets.py"
SEMANTIC_GATE = ROOT / ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py"
PUBLICATION_GATE = ROOT / ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py"

WORKER_SKILLS = {
    "worker-1": ROOT / ".codex/skills/paper-intake-worker/SKILL.md",
    "worker-2": ROOT / ".codex/skills/paper-body-table-worker/SKILL.md",
    "worker-3": ROOT / ".codex/skills/paper-supp-evidence-worker/SKILL.md",
    "worker-4": ROOT / ".codex/skills/paper-database-record-auditor/SKILL.md",
    "worker-5": ROOT / ".codex/skills/paper-mechanism-ontology-worker/SKILL.md",
    "worker-6": ROOT / ".codex/skills/paper-adjudicator-review-worker/SKILL.md",
}

REQUIRED_REFERENCES = [
    ROOT / ".codex/skills/amp-three-layer-curation/SKILL.md",
    ROOT / ".codex/skills/amp-three-layer-curation/references/publication-grade-source-review.md",
    ROOT / ".codex/skills/amp-three-layer-curation/references/publication-grade-quality-gate.md",
    ROOT / ".codex/skills/amp-three-layer-curation/references/team-rework-message-contract.md",
    ROOT / ".codex/skills/amp-three-layer-curation/references/two-queue-paper-packet-contract.md",
]

ACTIVITY_TABLE_PATTERNS = {
    "antibacterial": re.compile(r"\b(?:antibacterial|antimicrobial)\b", re.I),
    "inhibition_zone": re.compile(r"\binhibition\s+zone\b", re.I),
    "mic": re.compile(r"\bMIC\b|minimum\s+inhibitory\s+concentration", re.I),
    "mbc": re.compile(r"\bMBC\b|minimum\s+bactericidal\s+concentration", re.I),
    "mfc": re.compile(r"\bMFC\b|minimum\s+fungicidal\s+concentration", re.I),
    "cfu": re.compile(r"\bCFU(?:/mL)?\b|colony[- ]forming\s+units?", re.I),
    "toxicity": re.compile(r"\b(?:hemolysis|haemolysis|cytotoxicity|cell\s+viability|HC50|CC50|MHC)\b", re.I),
}
TOXICITY_SEARCH_TERMS = [
    "hemolysis",
    "haemolysis",
    "human red blood cells",
    "red blood cells",
    "hrbc",
    "cytotoxicity",
    "cell viability",
    "hc50",
    "cc50",
    "mhc",
]
FIGURE_REFERENCE_RE = re.compile(r"\bfig(?:ure)?\.?\s*\d+[a-z]?\b", re.I)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def cst_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def write_json(path: Path, data: Any) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    atomic_write_text(path, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


@contextmanager
def pilot_manifest_lock():
    """Serialize updates to the rolling manifest shared by distinct papers."""
    lock_path = BASE / "manifests/.dbaasp_strict_pilot_manifest.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        return [dict(row) for row in csv.DictReader(fh, delimiter="\t")]


def normalize_identifier(value: Any) -> str:
    return str(value or "").strip()


def activity_table_locator_candidates(table_text_by_locator: dict[str, str]) -> list[dict[str, Any]]:
    """Return only tables whose own text contains an activity/toxicity signal."""
    candidates: list[dict[str, Any]] = []
    for locator, text in table_text_by_locator.items():
        matched = [name for name, pattern in ACTIVITY_TABLE_PATTERNS.items() if pattern.search(text)]
        if matched:
            candidates.append(
                {
                    "locator": locator,
                    "source": "extracted/pdf_tables.json",
                    "tag": "table-wrap",
                    "matched_terms": matched,
                }
            )
    return candidates


def toxicity_locator_terms(endpoint: Any, evidence: Any) -> list[str]:
    """Build toxicity search terms without treating a generic figure number as toxicity."""
    endpoint_text = normalize_identifier(endpoint)
    evidence_text = normalize_identifier(evidence)
    combined = f"{endpoint_text} {evidence_text}".lower()
    if not any(term in combined for term in TOXICITY_SEARCH_TERMS):
        return []
    terms = list(TOXICITY_SEARCH_TERMS)
    for match in FIGURE_REFERENCE_RE.findall(evidence_text):
        normalized = " ".join(match.lower().replace("figure", "fig").replace(".", "").split())
        if normalized and normalized not in terms:
            terms.append(normalized)
    return terms


def normalize_doi(value: Any) -> str:
    text = normalize_identifier(value).lower()
    text = re.sub(r"^doi:\s*", "", text)
    text = re.sub(r"https?://(?:dx\.)?doi\.org/", "", text)
    return text.rstrip(").,;")


def normalize_pmcid(value: Any) -> str:
    text = normalize_identifier(value).upper()
    if text and text.isdigit():
        text = f"PMC{text}"
    return text


def normalize_title(value: Any) -> str:
    text = normalize_identifier(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def metadata_match_terms(metadata: dict[str, Any], paper_id: str) -> dict[str, str]:
    return {
        "doi": normalize_doi(metadata.get("doi") or metadata.get("canonical_doi")),
        "pmid": normalize_identifier(metadata.get("pmid") or metadata.get("pubmed_id")),
        "pmcid": normalize_pmcid(metadata.get("pmcid") or paper_id),
        "title": normalize_title(metadata.get("title")),
    }


def title_matches(row_title: str, target_title: str) -> bool:
    if not row_title or not target_title:
        return False
    if row_title == target_title:
        return True
    short, long = sorted([row_title, target_title], key=len)
    return len(short) >= 60 and short in long


def row_metadata_match(row: dict[str, str], terms: dict[str, str]) -> list[str]:
    reasons: list[str] = []
    doi_fields = ("canonical_doi", "enriched_doi", "ncbi_enriched_doi", "crossref_doi", "doi")
    pmid_fields = ("pubmed_id", "article_pubmed_id", "canonical_pmid", "enriched_pmid")
    pmcid_fields = ("canonical_pmcid", "enriched_pmcid", "ncbi_enriched_pmcid", "pmcid")
    title_fields = ("title", "article_title", "crossref_title", "openalex_title")
    if terms["doi"]:
        for field in doi_fields:
            if normalize_doi(row.get(field)) == terms["doi"]:
                reasons.append(f"{field}=doi")
        dedupe = normalize_identifier(row.get("dedupe_key")).lower()
        if dedupe == f"doi:{terms['doi']}":
            reasons.append("dedupe_key=doi")
    if terms["pmid"]:
        for field in pmid_fields:
            if normalize_identifier(row.get(field)) == terms["pmid"]:
                reasons.append(f"{field}=pmid")
    if terms["pmcid"]:
        for field in pmcid_fields:
            if normalize_pmcid(row.get(field)) == terms["pmcid"]:
                reasons.append(f"{field}=pmcid")
    if terms["title"]:
        for field in title_fields:
            if title_matches(normalize_title(row.get(field)), terms["title"]):
                reasons.append(f"{field}=title")
    return reasons


def read_csv_matches(path: Path, terms: dict[str, str]) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    matches: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            reasons = row_metadata_match(dict(row), terms)
            if reasons:
                enriched: dict[str, Any] = dict(row)
                enriched["_source_csv"] = str(path)
                enriched["_match_reasons"] = reasons
                matches.append(enriched)
    return matches


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(elem: ET.Element) -> str:
    return " ".join(" ".join(elem.itertext()).split())


def safe_clear_dir(path: Path) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def materialize(src: Path, dest: Path, mode: str) -> dict[str, Any]:
    record = {
        "source": str(src),
        "dest": str(dest),
        "mode": mode,
        "exists": src.exists(),
        "is_dir": src.is_dir() if src.exists() else False,
    }
    if not src.exists():
        return record
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.unlink()
    if mode == "manifest-only":
        return record
    if mode == "symlink":
        os.symlink(src, dest, target_is_directory=src.is_dir())
        return record
    if src.is_dir():
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)
    return record


def worklist_map() -> dict[str, tuple[Path, str]]:
    rows = read_json(WORKLIST)
    work = {str(row[0]): (Path(row[1]), str(row[2])) for row in rows}
    if MATERIAL_WORKLIST_OVERLAY.exists():
        overlay = read_json(MATERIAL_WORKLIST_OVERLAY)
        overlay_rows = overlay.get("rows") if isinstance(overlay, dict) else []
        for row in overlay_rows if isinstance(overlay_rows, list) else []:
            if not isinstance(row, list) or len(row) < 3:
                continue
            path = Path(str(row[1]))
            if path.exists():
                work[str(row[0])] = (path, str(row[2]))
    return work


def parse_xml_metadata(xml_path: Path) -> dict[str, Any]:
    meta: dict[str, Any] = {"source": str(xml_path)}
    if not xml_path.exists():
        meta["error"] = "missing_xml"
        return meta
    try:
        root = ET.parse(xml_path).getroot()
    except Exception as exc:  # noqa: BLE001 - packet diagnostic
        meta["error"] = f"xml_parse_error: {exc}"
        return meta
    if local_name(root.tag) == "collection":
        passages = [
            element for element in root.iter() if local_name(element.tag) == "passage"
        ]
        if passages:
            infons = {
                str(element.attrib.get("key") or ""): str(element.text or "").strip()
                for element in passages[0]
                if local_name(element.tag) == "infon"
            }
            document_id = next(
                (
                    str(element.text or "").strip()
                    for element in root.iter()
                    if local_name(element.tag) == "id"
                ),
                "",
            )
            for source_key, target_key in (
                ("article-id_doi", "doi"),
                ("article-id_pmid", "pmid"),
                ("year", "year"),
            ):
                if infons.get(source_key):
                    meta[target_key] = infons[source_key]
            if document_id:
                meta["pmcid"] = f"PMC{document_id.upper().removeprefix('PMC')}"
            title = next(
                (
                    str(child.text or "").strip()
                    for passage in passages
                    if any(
                        local_name(item.tag) == "infon"
                        and item.attrib.get("key") == "section_type"
                        and str(item.text or "").upper() == "TITLE"
                        for item in passage
                    )
                    for child in passage
                    if local_name(child.tag) == "text"
                    and str(child.text or "").strip()
                ),
                "",
            )
            if title:
                meta["title"] = title
            meta["structured_fulltext_format"] = "bioc_xml"
            return meta
    for elem in root.iter():
        tag = local_name(elem.tag)
        if tag == "article-id":
            typ = elem.attrib.get("pub-id-type") or elem.attrib.get("article-id-type")
            value = text_of(elem)
            if typ and value:
                meta[typ] = value
        elif tag == "article-title" and "title" not in meta:
            meta["title"] = text_of(elem)
        elif tag == "journal-title" and "journal" not in meta:
            meta["journal"] = text_of(elem)
        elif tag == "year" and "year" not in meta:
            meta["year"] = text_of(elem)
    if "pmcid" not in meta and "pmcid-ver" in meta:
        meta["pmcid"] = str(meta["pmcid-ver"]).split(".")[0]
    return meta


def extract_xml_surfaces(xml_path: Path, packet: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    sections: list[dict[str, Any]] = []
    figures: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    supp_refs: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if not xml_path.exists():
        errors.append({"type": "missing_xml", "source": str(xml_path)})
        write_json(packet / "extracted/xml_sections.json", {"sections": sections, "errors": errors})
        return sections, tables, supp_refs, errors
    try:
        root = ET.parse(xml_path).getroot()
    except Exception as exc:  # noqa: BLE001
        errors.append({"type": "xml_parse_error", "source": str(xml_path), "error": str(exc)})
        write_json(packet / "extracted/xml_sections.json", {"sections": sections, "errors": errors})
        return sections, tables, supp_refs, errors

    if local_name(root.tag) == "collection":
        passage_number = 0
        for passage in root.iter():
            if local_name(passage.tag) != "passage":
                continue
            passage_number += 1
            infons = {
                str(child.attrib.get("key") or ""): str(child.text or "")
                for child in passage
                if local_name(child.tag) == "infon"
            }
            text = next(
                (
                    str(child.text or "").strip()
                    for child in passage
                    if local_name(child.tag) == "text"
                ),
                "",
            )
            if not text:
                continue
            section_type = str(infons.get("section_type") or "UNKNOWN")
            passage_type = str(infons.get("type") or "passage")
            item = {
                "locator": f"bioc:passage={passage_number}",
                "tag": passage_type,
                "section_type": section_type,
                "structured_fulltext_format": "bioc_xml",
                "text": text[:8000],
            }
            sections.append(item)
            if section_type.upper() == "TABLE" and passage_type.lower() == "table":
                tables.append(item)
            if section_type.upper() in {"FIG", "FIGURE"}:
                figures.append(item)
        write_json(
            packet / "extracted/xml_sections.json",
            {
                "source": str(xml_path),
                "structured_fulltext_format": "bioc_xml",
                "section_count": len(sections),
                "sections": sections,
                "errors": errors,
            },
        )
        write_json(
            packet / "extracted/pdf_tables.json",
            {
                "note": "BioC structured table passages; verify layout against the primary PDF",
                "tables": tables,
            },
        )
        write_json(packet / "extracted/figure_captions.json", {"figures": figures})
        return sections, tables, supp_refs, errors

    counters: Counter[str] = Counter()
    for elem in root.iter():
        tag = local_name(elem.tag)
        if tag in {"article-title", "abstract", "sec", "p", "table-wrap", "fig", "caption"}:
            text = text_of(elem)
            if text:
                counters[tag] += 1
                locator = f"xml:{tag}:{counters[tag]}"
                item = {"locator": locator, "tag": tag, "text": text[:8000]}
                sections.append(item)
                if tag == "table-wrap":
                    tables.append(item)
                if tag in {"fig", "caption"}:
                    figures.append(item)
        if tag in {"supplementary-material", "ext-link", "media"}:
            text = text_of(elem)
            href = ""
            for key, value in elem.attrib.items():
                if key.endswith("href") or "href" in key:
                    href = value
                    break
            if text or href:
                supp_refs.append({"tag": tag, "text": text[:500], "href": href})

    write_json(packet / "extracted/xml_sections.json", {"source": str(xml_path), "section_count": len(sections), "sections": sections, "errors": errors})
    write_json(packet / "extracted/pdf_tables.json", {"note": "table structure from XML only in DBAASP strict pilot", "tables": tables})
    write_json(packet / "extracted/figure_captions.json", {"figures": figures})
    return sections, tables, supp_refs, errors


def extract_pdf_text(pdf_path: Path, out_path: Path) -> tuple[int, list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    if not pdf_path.exists():
        errors.append({"type": "missing_pdf", "source": str(pdf_path)})
        write_jsonl(out_path, [])
        return 0, errors
    tool = shutil.which("pdftotext")
    if not tool:
        errors.append({"type": "missing_tool", "tool": "pdftotext", "source": str(pdf_path)})
        write_jsonl(out_path, [])
        return 0, errors
    proc = subprocess.run([tool, "-layout", "-enc", "UTF-8", str(pdf_path), "-"], capture_output=True, text=True, timeout=180, check=False)
    if proc.returncode != 0:
        errors.append({"type": "pdf_text_failed", "source": str(pdf_path), "stderr": proc.stderr[-2000:]})
        write_jsonl(out_path, [])
        return 0, errors
    rows = []
    for index, page in enumerate(proc.stdout.split("\f"), start=1):
        text = page.strip()
        if text:
            rows.append({"locator": f"pdf:page={index}", "source": str(pdf_path), "page": index, "text": text})
    write_jsonl(out_path, rows)
    return len(rows), errors


def extract_docx_text(path: Path) -> tuple[str, list[dict[str, Any]]]:
    try:
        with zipfile.ZipFile(path) as zf:
            chunks: list[str] = []
            for name in sorted(zf.namelist()):
                if name.startswith("word/") and name.endswith(".xml"):
                    raw = zf.read(name)
                    try:
                        root = ET.fromstring(raw)
                    except Exception:
                        continue
                    text = " ".join(" ".join(root.itertext()).split())
                    if text:
                        chunks.append(f"[{name}] {text}")
            return "\n\n".join(chunks), []
    except Exception as exc:  # noqa: BLE001
        return "", [{"type": "docx_extract_failed", "source": str(path), "error": str(exc)}]


def extract_docx_tables(path: Path, rel: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        with zipfile.ZipFile(path) as zf:
            raw = zf.read("word/document.xml")
    except Exception as exc:  # noqa: BLE001
        return [], [{"type": "docx_table_extract_failed", "source": str(path), "error": str(exc)}]
    try:
        root = ET.fromstring(raw)
    except Exception as exc:  # noqa: BLE001
        return [], [{"type": "docx_table_xml_parse_failed", "source": str(path), "error": str(exc)}]

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    tables: list[dict[str, Any]] = []
    for table_index, tbl in enumerate(root.findall(".//w:tbl", ns), start=1):
        rows: list[dict[str, Any]] = []
        for row_index, tr in enumerate(tbl.findall("./w:tr", ns), start=1):
            cells: list[dict[str, Any]] = []
            for cell_index, tc in enumerate(tr.findall("./w:tc", ns), start=1):
                text = " ".join(" ".join(tc.itertext()).split())
                cells.append(
                    {
                        "column_index": cell_index,
                        "text": text,
                        "locator": f"supp:{rel}:word/document.xml:tbl={table_index}:row={row_index}:cell={cell_index}",
                    }
                )
            rows.append(
                {
                    "row_index": row_index,
                    "cells": cells,
                    "locator": f"supp:{rel}:word/document.xml:tbl={table_index}:row={row_index}",
                }
            )
        tables.append(
            {
                "locator": f"supp:{rel}:word/document.xml:tbl={table_index}",
                "source": str(path),
                "relative_path": rel,
                "format": "docx",
                "table_index": table_index,
                "row_count": len(rows),
                "max_cell_count": max((len(row["cells"]) for row in rows), default=0),
                "rows": rows,
            }
        )
    return tables, []


def extract_supplementary(supp_dir: Path, packet: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    files: list[dict[str, Any]] = []
    text_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    archives: list[dict[str, Any]] = []
    if not supp_dir.exists():
        write_json(packet / "extracted/supplementary_index.json", {"files": [], "note": "no staged supplementary directory"})
        write_jsonl(packet / "extracted/supplementary_text.jsonl", [])
        write_json(packet / "extracted/supplementary_tables.json", {"tables": tables})
        write_json(packet / "extracted/archive_manifest.json", {"archives": archives})
        return files, text_rows, errors

    for src in sorted(path for path in supp_dir.rglob("*") if path.is_file()):
        rel = str(src.relative_to(supp_dir))
        suffix = src.suffix.lower()
        item = {"relative_path": rel, "source": str(src), "suffix": suffix, "size_bytes": src.stat().st_size}
        text = ""
        local_errors: list[dict[str, Any]] = []
        if suffix in {".txt", ".csv", ".tsv", ".md"}:
            text = src.read_text(encoding="utf-8", errors="replace")
        elif suffix == ".docx":
            text, local_errors = extract_docx_text(src)
            docx_tables, table_errors = extract_docx_tables(src, rel)
            tables.extend(docx_tables)
            local_errors.extend(table_errors)
            if docx_tables:
                item["docx_table_count"] = len(docx_tables)
                item["docx_table_dimensions"] = [
                    {"rows": table["row_count"], "max_cells": table["max_cell_count"]}
                    for table in docx_tables
                ]
        elif suffix == ".pdf":
            ocr_path = packet / "extracted/ocr" / f"{src.stem}.pdf_text.jsonl"
            pages, local_errors = extract_pdf_text(src, ocr_path)
            item["pdf_text_pages"] = pages
            if pages:
                item["extraction_status"] = "pdf_text_extracted"
            for row in read_jsonl(ocr_path):
                page = row.get("page")
                if row.get("text") and page:
                    text_rows.append(
                        {
                            "locator": f"supp:{rel}:page={page}",
                            "source": str(src),
                            "page": page,
                            "text": row["text"],
                        }
                    )
        elif suffix == ".xlsx":
            item["extraction_status"] = "inventory_only_xlsx"
        elif suffix == ".doc":
            item["extraction_status"] = "inventory_only_doc"
        elif suffix == ".zip":
            try:
                with zipfile.ZipFile(src) as zf:
                    members = [
                        {
                            "name": info.filename,
                            "file_size": info.file_size,
                            "compress_size": info.compress_size,
                            "crc": f"{info.CRC:08x}",
                            "is_dir": info.is_dir(),
                        }
                        for info in zf.infolist()
                    ]
                item["extraction_status"] = "archive_inventory_extracted"
                item["zip_member_count"] = len(members)
                archives.append({"relative_path": rel, "source": str(src), "member_count": len(members), "members": members})
            except Exception as exc:  # noqa: BLE001 - archive inventory diagnostic
                item["extraction_status"] = "archive_inventory_failed"
                local_errors.append({"type": "zip_inventory_failed", "source": str(src), "error": str(exc)})
        else:
            item["extraction_status"] = "inventory_only"
        errors.extend(local_errors)
        if text.strip():
            item["extraction_status"] = "text_extracted"
            text_rows.append({"locator": f"supp:{rel}", "source": str(src), "text": text})
        elif local_errors:
            item["extraction_status"] = "extract_failed"
        files.append(item)

    write_json(packet / "extracted/supplementary_index.json", {"files": files})
    write_jsonl(packet / "extracted/supplementary_text.jsonl", text_rows)
    write_json(packet / "extracted/supplementary_tables.json", {"tables": tables, "note": "DOCX supplementary tables are extracted with row/cell locators; spreadsheet table normalization remains a rework item if needed."})
    write_json(packet / "extracted/archive_manifest.json", {"archives": archives})
    return files, text_rows, errors


def looks_like_supplement_reference(ref: dict[str, Any]) -> bool:
    href = str(ref.get("href") or "")
    tag = str(ref.get("tag") or "")
    text = str(ref.get("text") or "")
    blob = f"{href} {text}".lower()
    suffix = Path(href).suffix.lower()
    if tag in {"supplementary-material", "media"} and suffix in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".tsv", ".zip"}:
        return True
    if "suppl_file" in blob:
        return True
    if suffix in {".doc", ".docx", ".xls", ".xlsx", ".zip"} and re.search(r"(supp|moesm|esm|si_|s\d{2,}|table\s*s|fig(?:ure)?\s*s)", blob):
        return True
    if suffix == ".pdf" and re.search(r"(supp|moesm|esm|si_|s\d{2,}|supporting information|table\s*s|fig(?:ure)?\s*s)", blob):
        return True
    return False


def jsonl_rows_from_tsv(path: Path, paper_id: str) -> list[dict[str, str]]:
    return [row for row in read_tsv(path) if row.get("paper_id") == paper_id]


def collect_database_ids(rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    ids: dict[str, set[str]] = {
        "article_id": set(),
        "article_index": set(),
        "peptide_id": set(),
        "dbaasp_id": set(),
        "sequence_key": set(),
        "source_id": set(),
    }
    for row in rows:
        for key in ids:
            value = normalize_identifier(row.get(key))
            if value:
                ids[key].add(value)
        source_id = normalize_identifier(row.get("source_id"))
        if source_id:
            ids["dbaasp_id"].add(source_id)
        sequence_key = normalize_identifier(row.get("sequence_key"))
        if sequence_key:
            ids["sequence_key"].add(sequence_key)
    return ids


def row_matches_database_ids(row: dict[str, str], ids: dict[str, set[str]]) -> list[str]:
    reasons: list[str] = []
    for key, values in ids.items():
        value = normalize_identifier(row.get(key))
        if value and value in values:
            reasons.append(f"{key}=linked")
    if normalize_identifier(row.get("source_id")) in ids["dbaasp_id"]:
        reasons.append("source_id=dbaasp_id")
    return reasons


def read_csv_by_database_ids(path: Path, ids: dict[str, set[str]]) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    matches: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            reasons = row_matches_database_ids(dict(row), ids)
            if reasons:
                enriched: dict[str, Any] = dict(row)
                enriched["_source_csv"] = str(path)
                enriched["_match_reasons"] = sorted(set(reasons))
                matches.append(enriched)
    return matches


def dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        key = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def build_authoritative_database_snapshot(packet: Path, paper_id: str, metadata: dict[str, Any]) -> dict[str, Any]:
    """Snapshot locally indexed DBAASP/merged rows linked by DOI, PMID, PMCID, or title."""
    terms = metadata_match_terms(metadata, paper_id)
    article_rows = read_csv_matches(AUTHORITATIVE_DB_INPUTS["dbaasp_article_refs"], terms)
    assay_rows = read_csv_matches(AUTHORITATIVE_DB_INPUTS["dbaasp_assay_refs"], terms)
    merged_assay_rows = read_csv_matches(AUTHORITATIVE_DB_INPUTS["merged_dbaasp_assay_records"], terms)
    literature_rows = read_csv_matches(AUTHORITATIVE_DB_INPUTS["merged_sequence_literature_links"], terms)
    unique_literature_rows = read_csv_matches(AUTHORITATIVE_DB_INPUTS["merged_unique_literature_availability"], terms)

    linked_ids = collect_database_ids(article_rows + assay_rows + merged_assay_rows + literature_rows)
    linked_assay_rows = read_csv_by_database_ids(AUTHORITATIVE_DB_INPUTS["dbaasp_assay_refs"], linked_ids)
    linked_merged_assay_rows = read_csv_by_database_ids(AUTHORITATIVE_DB_INPUTS["merged_dbaasp_assay_records"], linked_ids)
    peptide_rows = read_csv_by_database_ids(AUTHORITATIVE_DB_INPUTS["dbaasp_peptides_summary"], linked_ids)
    sequence_rows = read_csv_by_database_ids(AUTHORITATIVE_DB_INPUTS["merged_all_sequences"], linked_ids)

    article_rows = dedupe_rows(article_rows)
    assay_rows = dedupe_rows(assay_rows + linked_assay_rows + merged_assay_rows + linked_merged_assay_rows)
    sequence_rows = dedupe_rows(peptide_rows + sequence_rows)
    literature_rows = dedupe_rows(literature_rows + unique_literature_rows)

    write_jsonl(packet / "database/linked_article_records.jsonl", article_rows)
    write_jsonl(packet / "database/linked_assay_records.jsonl", assay_rows)
    write_jsonl(packet / "database/linked_sequence_records.jsonl", sequence_rows)
    write_jsonl(packet / "database/linked_literature_records.jsonl", literature_rows)

    report = {
        "generated_at": utc_now(),
        "paper_id": paper_id,
        "match_terms": terms,
        "input_paths": {name: str(path) for name, path in AUTHORITATIVE_DB_INPUTS.items()},
        "input_path_exists": {name: path.exists() for name, path in AUTHORITATIVE_DB_INPUTS.items()},
        "row_counts": {
            "linked_article_records": len(article_rows),
            "linked_assay_records": len(assay_rows),
            "linked_sequence_records": len(sequence_rows),
            "linked_literature_records": len(literature_rows),
        },
        "source_record_links_present": any([article_rows, assay_rows, sequence_rows, literature_rows]),
        "strict_interpretation": "zero linked rows means the local authoritative indexes were checked and did not contain a stable DBAASP/merged link for this paper; Codex fallback rows remain machine candidates only.",
    }
    write_json(packet / "database/authoritative_match_report.json", report)
    return report


def build_database_snapshot(packet: Path, paper_id: str, work_entry: tuple[Path, str], metadata: dict[str, Any]) -> dict[str, Any]:
    rows = jsonl_rows_from_tsv(DBAASP_EXTRACTED, paper_id)
    review_rows = jsonl_rows_from_tsv(REVIEW_QUEUE, paper_id)
    empty_rows = jsonl_rows_from_tsv(EMPTY_DONE, paper_id)
    session_rows = jsonl_rows_from_tsv(SESSION_AUDIT, paper_id)
    authoritative = build_authoritative_database_snapshot(packet, paper_id, metadata)
    write_jsonl(packet / "database/dbaasp_machine_extracted_rows.jsonl", rows)
    write_jsonl(packet / "database/dbaasp_review_queue_rows.jsonl", review_rows)
    write_jsonl(packet / "database/dbaasp_empty_done.jsonl", empty_rows)
    write_jsonl(packet / "database/codex_session_audit.jsonl", session_rows)
    write_json(packet / "database/dbaasp_worklist_entry.json", {"paper_id": paper_id, "path": str(work_entry[0]), "kind": work_entry[1]})
    manifest = {
        "generated_at": utc_now(),
        "paper_id": paper_id,
        "identifiers": metadata,
        "source": "DBAASP pending Codex fallback artifacts",
        "row_counts": {
            "dbaasp_machine_extracted_rows": len(rows),
            "dbaasp_review_queue_rows": len(review_rows),
            "dbaasp_empty_done_rows": len(empty_rows),
            "codex_exec_sessions": len(session_rows),
            **authoritative["row_counts"],
        },
        "source_record_links_present": authoritative["source_record_links_present"],
        "authoritative_match_report": str(packet / "database/authoritative_match_report.json"),
        "strict_interpretation": "machine rows are candidate evidence only; worker-4/6 must source-review before any source_verified or release/portal ingest claim",
        "input_artifacts": {
            "machine_rows": str(DBAASP_EXTRACTED),
            "codex_batch_rows": str(BATCH_ROWS),
            "review_queue": str(REVIEW_QUEUE),
            "empty_done": str(EMPTY_DONE),
            "session_audit": str(SESSION_AUDIT),
            "session_audit_json": str(SESSION_AUDIT_JSON),
            "batch_report": str(BATCH_REPORT),
            "authoritative_inputs": {name: str(path) for name, path in AUTHORITATIVE_DB_INPUTS.items()},
        },
    }
    write_json(packet / "database/database_source_manifest.json", manifest)
    return manifest


def build_locator_index(packet: Path, sections: list[dict[str, Any]], supp_text: list[dict[str, Any]]) -> dict[str, Any]:
    locators: list[dict[str, Any]] = []
    for item in sections:
        locators.append({"locator": item["locator"], "source": "extracted/xml_sections.json", "tag": item.get("tag"), "preview": item.get("text", "")[:240]})
    pdf_text = packet / "extracted/pdf_text.jsonl"
    if pdf_text.exists():
        for line in pdf_text.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            locators.append({"locator": row["locator"], "source": "extracted/pdf_text.jsonl", "preview": row.get("text", "")[:240]})
    for row in supp_text:
        locators.append({"locator": row["locator"], "source": "extracted/supplementary_text.jsonl", "preview": row.get("text", "")[:240]})
    supp_tables_path = packet / "extracted/supplementary_tables.json"
    if supp_tables_path.exists():
        supp_tables = read_json(supp_tables_path).get("tables", [])
        for table in supp_tables if isinstance(supp_tables, list) else []:
            if not isinstance(table, dict):
                continue
            table_preview = []
            rows = table.get("rows") if isinstance(table.get("rows"), list) else []
            for row in rows[:3]:
                cells = row.get("cells") if isinstance(row, dict) and isinstance(row.get("cells"), list) else []
                table_preview.append(" | ".join(str(cell.get("text") or "") for cell in cells[:8] if isinstance(cell, dict)))
            locators.append(
                {
                    "locator": table.get("locator"),
                    "source": "extracted/supplementary_tables.json",
                    "preview": " / ".join(part for part in table_preview if part)[:240],
                }
            )
            for row in rows:
                if not isinstance(row, dict):
                    continue
                cells = row.get("cells") if isinstance(row.get("cells"), list) else []
                preview = " | ".join(str(cell.get("text") or "") for cell in cells if isinstance(cell, dict))
                locators.append(
                    {
                        "locator": row.get("locator"),
                        "source": "extracted/supplementary_tables.json",
                        "preview": preview[:240],
                    }
                )
    data = {"generated_at": utc_now(), "locator_count": len(locators), "locators": locators}
    write_json(packet / "locators/locator_index.json", data)
    write_json(packet / "locators/citation_map.json", {"generated_at": utc_now(), "note": "citation map not normalized in DBAASP strict pilot"})
    return data


def build_packet(paper_id: str, raw_mode: str) -> dict[str, Any]:
    work = worklist_map()
    if paper_id not in work:
        raise SystemExit(f"{paper_id} not found in {WORKLIST}")
    source_path, kind = work[paper_id]
    source_dir = source_path.parent
    if kind == "pdf":
        source_pdf = source_path
        source_xml = source_path.with_suffix(".xml")
    else:
        source_xml = source_path
        source_pdf = source_dir / "paper.pdf"
    paper_root = BASE / "papers" / paper_id
    packet = BASE / "packets" / paper_id
    safe_clear_dir(paper_root)
    safe_clear_dir(packet)
    for rel in ["source", "work/intake", "work/activity_evidence", "work/supplementary_methods", "work/database_record_audit", "work/mechanism_ontology", "work/review", "final"]:
        (paper_root / rel).mkdir(parents=True, exist_ok=True)
    for rel in ["raw/supplementary_original", "extracted/ocr", "database", "locators", "extraction", "analysis", "final", "rework"]:
        (packet / rel).mkdir(parents=True, exist_ok=True)

    staged: list[dict[str, Any]] = []
    staged.append(materialize(source_xml, paper_root / "source/paper.xml", raw_mode))
    staged.append(materialize(source_pdf, paper_root / "source/paper.pdf", raw_mode))
    staged.append(materialize(source_dir / "paper_meta.json", paper_root / "source/paper_meta.json", raw_mode))
    staged.append(materialize(source_dir / "supplementary", paper_root / "source/supplementary", raw_mode))
    staged.append(materialize(source_xml, packet / "raw/paper.xml", raw_mode))
    staged.append(materialize(source_pdf, packet / "raw/paper.pdf", raw_mode))
    staged.append(materialize(source_dir / "paper_meta.json", packet / "raw/paper_meta.json", raw_mode))
    staged.append(materialize(source_dir / "supplementary", packet / "raw/supplementary_original", raw_mode))

    metadata = parse_xml_metadata(source_xml)
    if kind == "pdf" and paper_id.lower().startswith("10."):
        metadata.setdefault("doi", paper_id)
    source_meta_path = source_dir / "paper_meta.json"
    if source_meta_path.exists():
        metadata["staging_metadata"] = read_json(source_meta_path)

    sections, tables, supp_refs, xml_errors = extract_xml_surfaces(paper_root / "source/paper.xml", packet)
    if kind == "pdf" and not source_xml.exists():
        for error in xml_errors:
            if error.get("type") == "missing_xml":
                error.update(
                    {
                        "severity": "major",
                        "source_review_requirement": (
                            "Inspect the complete primary PDF and preserve the "
                            "structured-fulltext unavailability as a caution."
                        ),
                        "impact": (
                            "XML locators/tables are unavailable; PDF page "
                            "locators are the primary evidence surface."
                        ),
                    }
                )
    pdf_pages, pdf_errors = extract_pdf_text(paper_root / "source/paper.pdf", packet / "extracted/pdf_text.jsonl")
    supp_files, supp_text, supp_errors = extract_supplementary(paper_root / "source/supplementary", packet)
    supp_table_count = len(read_json(packet / "extracted/supplementary_tables.json").get("tables", []))
    locators = build_locator_index(packet, sections, supp_text)
    db_manifest = build_database_snapshot(packet, paper_id, (source_path, kind), metadata)

    staged_supp_names = {Path(str(item.get("relative_path") or "")).name for item in supp_files}
    staged_supp_names.update(str(item.get("relative_path") or "") for item in supp_files)
    missing_local_supp = []
    for ref in supp_refs:
        href = str(ref.get("href") or "")
        if not href or not looks_like_supplement_reference(ref):
            continue
        href_name = Path(href).name
        if href_name and href_name not in staged_supp_names and href not in staged_supp_names:
            missing_local_supp.append(ref)
    errors = xml_errors + pdf_errors + supp_errors
    for ref in missing_local_supp:
        errors.append(
            {
                "type": "external_supplementary_reference_not_staged",
                "severity": "major",
                "source": str(source_xml),
                "reference": ref,
                "impact": "worker-3/worker-6 must decide whether XML/PDF text is sufficient or a material rework ticket is required",
            }
        )

    material_status = "material_extracted_complete"
    if errors:
        material_status = "material_extracted_with_gaps"
    if not (paper_root / "source/paper.xml").exists() and not (paper_root / "source/paper.pdf").exists():
        material_status = "material_blocked_missing_source"

    extraction_status = {
        "status": material_status,
        "generated_at": utc_now(),
        "paper_id": paper_id,
        "xml_section_count": len(sections),
        "xml_table_count": len(tables),
        "pdf_page_count": pdf_pages,
        "supplementary_file_count": len(supp_files),
        "supplementary_text_count": len(supp_text),
        "supplementary_table_count": supp_table_count,
        "error_count": len(errors),
    }
    write_json(packet / "extraction/extraction_status.json", extraction_status)
    write_json(packet / "extraction/extraction_quality_report.json", {"generated_at": utc_now(), "paper_id": paper_id, "errors": errors})
    write_jsonl(packet / "extraction/extraction_errors.jsonl", errors)
    write_json(packet / "analysis/analysis_status.json", {"status": "analysis_queued", "generated_at": utc_now(), "note": "awaiting worker-4/5/6 source-reviewed analysis"})
    write_jsonl(packet / "rework/rework_requests.jsonl", [])
    write_jsonl(packet / "rework/rework_responses.jsonl", [])
    write_jsonl(packet / "rework/closure_receipts.jsonl", [])

    manifest = {
        "paper_id": paper_id,
        "packet_version": "dbaasp_strict_pilot_v1",
        "generated_at": utc_now(),
        "metadata": metadata,
        "source_root": str(source_dir),
        "paper_root": str(paper_root),
        "packet_root": str(packet),
        "staged_files": staged,
        "material_queue_status": material_status,
        "analysis_queue_status": "analysis_queued",
        "database_snapshot_inputs": db_manifest,
        "locator_index_path": str(packet / "locators/locator_index.json"),
        "locator_count": locators["locator_count"],
        "known_missing_or_blocked_materials": errors,
        "strict_boundary": "packet handoff only; not source-reviewed until workers 4-6 and strict gates pass",
    }
    write_json(packet / "packet_manifest.json", manifest)
    write_json(paper_root / "final/materials_manifest.json", manifest)

    packet_link = paper_root / "packet"
    if packet_link.exists() or packet_link.is_symlink():
        if packet_link.is_dir() and not packet_link.is_symlink():
            shutil.rmtree(packet_link)
        else:
            packet_link.unlink()
    os.symlink(packet, packet_link, target_is_directory=True)

    return {
        "paper_id": paper_id,
        "paper_root": str(paper_root),
        "packet_root": str(packet),
        "material_status": material_status,
        "locator_count": locators["locator_count"],
        "database_row_counts": db_manifest["row_counts"],
        "error_count": len(errors),
    }


def existing_built_summary(paper_id: str) -> dict[str, Any]:
    packet = BASE / "packets" / paper_id
    paper_root = BASE / "papers" / paper_id
    manifest = read_json(packet / "packet_manifest.json") if (packet / "packet_manifest.json").exists() else {}
    db = read_json(packet / "database/database_source_manifest.json") if (packet / "database/database_source_manifest.json").exists() else {}
    return {
        "paper_id": paper_id,
        "paper_root": str(paper_root),
        "packet_root": str(packet),
        "material_status": manifest.get("material_queue_status", "unknown"),
        "locator_count": live_locator_count(packet),
        "database_row_counts": db.get("row_counts", {}),
        "error_count": len(live_extraction_errors(packet)),
    }


def write_pilot_manifest(paper_ids: list[str], built: list[dict[str, Any]], *, append: bool = False) -> Path:
    with pilot_manifest_lock():
        if append:
            previous_path = BASE / "manifests/dbaasp_strict_pilot_manifest.json"
            previous_ids: list[str] = []
            if previous_path.exists():
                previous = read_json(previous_path)
                previous_ids = [str(item) for item in previous.get("paper_ids", [])]
            merged_ids = list(dict.fromkeys(previous_ids + paper_ids))
            built_by_id = {item["paper_id"]: item for item in built}
            built = [
                built_by_id.get(pid) or existing_built_summary(pid)
                for pid in merged_ids
            ]
            paper_ids = merged_ids
        manifest = {
            "created_at": utc_now(),
            "scope": "DBAASP pending strict pilot; generated from Codex fallback machine extraction artifacts",
            "paper_ids": paper_ids,
            "papers": built,
            "packet_root": str(BASE / "packets"),
            "root_for_gates": str(BASE),
            "model_requirement": {"model": "gpt-5.5", "reasoning_effort": "xhigh"},
            "strict_boundary": "not publication-grade until semantic and publication gates pass after worker-6 adjudication",
        }
        path = BASE / "manifests/dbaasp_strict_pilot_manifest.json"
        write_json(path, manifest)
        issues_path = BASE / "issues/dbaasp_strict_pilot_issues.jsonl"
        if not append or not issues_path.exists():
            write_jsonl(issues_path, [])
    return path


def locator_refs_for_terms(packet: Path, terms: list[str], *, max_count: int = 8) -> list[dict[str, Any]]:
    index_path = packet / "locators/locator_index.json"
    if not index_path.exists():
        return []
    index = read_json(index_path)
    refs: list[dict[str, Any]] = []
    seen: set[str] = set()
    lowered_terms = [term.lower() for term in terms]
    for item in index.get("locators", []):
        if not isinstance(item, dict):
            continue
        preview = str(item.get("preview") or "").lower()
        if not any(term in preview for term in lowered_terms):
            continue
        locator = str(item.get("locator") or "")
        if not locator or locator in seen:
            continue
        seen.add(locator)
        refs.append(
            {
                "locator": locator,
                "source": item.get("source"),
                "tag": item.get("tag"),
                "note": "locator matched by controlled keyword search; preview intentionally omitted from handoff",
            }
        )
        if len(refs) >= max_count:
            break
    return refs


def normalize_candidate_name(value: Any) -> str:
    text = normalize_identifier(value)
    text = re.sub(r"\s*\(BSFL fraction\)\s*$", "", text, flags=re.I)
    return " ".join(text.split())


def safe_activity_row(
    *,
    paper_id: str,
    source_table: str,
    source_locator: str,
    entity: str,
    sequence: str | None,
    endpoint: str,
    value: str,
    unit: str,
    target: str,
    assay_medium: str | None = None,
    inoculum: str | None = None,
    evidence_ladder: str = "in_vitro_multi_pathogen",
    notes: list[str] | None = None,
) -> dict[str, Any]:
    entity_name = normalize_candidate_name(entity)
    return {
        "paper_id": paper_id,
        "source_table": source_table,
        "source_locator": source_locator,
        "entity": entity_name,
        "entity_type": "fraction" if re.fullmatch(r"F\d+", entity_name) else "peptide",
        "sequence": None if sequence in {None, "", "None"} else sequence,
        "endpoint": endpoint,
        "raw_value": value,
        "raw_unit": unit,
        "target": target,
        "assay_medium": assay_medium,
        "inoculum": inoculum,
        "evidence_ladder": evidence_ladder,
        "normalization_status": "direct",
        "source_review_status": "candidate_from_safe_handoff_requires_worker2_confirmation",
        "notes": notes or [],
    }


def table1_safe_rows(paper_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    targets = [
        ("Listeria monocytogenes DMST 17303", ["8", "1", "1", "1", "4"], "MHB + 0.6% yeast extract"),
        ("Salmonella enterica serovar Enteritidis DMST 15679", ["8", "8", "4", "4", ">8"], "MHB"),
        ("Escherichia coli O157:H7 DMST 12743", [">8", "8", "4", "4", ">8"], "MHB"),
    ]
    for target, values, medium in targets:
        for fraction, value in zip(["F1", "F2", "F3", "F4", "F5"], values, strict=True):
            rows.append(
                safe_activity_row(
                    paper_id=paper_id,
                    source_table="Table 1",
                    source_locator="xml:table-wrap:1",
                    entity=fraction,
                    sequence=None,
                    endpoint="MIC",
                    value=value,
                    unit="mM",
                    target=target,
                    assay_medium=medium,
                    inoculum="~1e6 CFU/mL",
                    notes=["fraction-level MIC row from controlled table digest"],
                )
            )
    return rows


def table2_safe_rows(paper_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    targets = [
        ("Listeria monocytogenes DMST 17303", "LM"),
        ("Salmonella enterica serovar Enteritidis DMST 15679", "SE"),
        ("Escherichia coli O157:H7 DMST 12743", "EC"),
    ]
    active = {
        "CGPPRQGPFPR": {"LM": "4", "SE": ">4", "EC": ">4", "fraction": "F2"},
        "HLEEELK": {"LM": "4", "SE": "4", "EC": "4", "fraction": "F3"},
        "LEEAEERAD": {"LM": "4", "SE": "4", "EC": "4", "fraction": "F3"},
        "TEELEEAKKK": {"LM": "4", "SE": "4", "EC": "4", "fraction": "F3"},
        "KGNSELEEAKKK": {"LM": "4", "SE": "4", "EC": "4", "fraction": "F3"},
    }
    inactive = [
        ("RSHERGALTNEFLVGS", "F2"),
        ("TPKCPK", "F2"),
        ("AERELVR", "F3"),
        ("ESKERLE", "F3"),
        ("EVKLR", "F3"),
        ("EYEEQEASLN", "F3"),
        ("KFTMEEKAKK", "F3"),
        ("KLPEWRW", "F3"),
    ]
    for seq, values in active.items():
        for target, code in targets:
            rows.append(
                safe_activity_row(
                    paper_id=paper_id,
                    source_table="Table 2",
                    source_locator="xml:table-wrap:2",
                    entity=seq,
                    sequence=seq,
                    endpoint="MIC",
                    value=values[code],
                    unit="mM",
                    target=target,
                    assay_medium="not row-specific in table; worker-2 should preserve source-located method notes if used",
                    inoculum=None,
                    notes=[f"peptide-level MIC row from controlled table digest; fraction={values['fraction']}"],
                )
            )
    for seq, fraction in inactive:
        excluded.append(
            {
                "paper_id": paper_id,
                "source_table": "Table 2",
                "source_locator": "xml:table-wrap:2",
                "sequence": seq,
                "fraction": fraction,
                "activity_field": "ND",
                "required_worker2_action": "do not create activity_records for ND table entries",
            }
        )
    return rows, excluded


def build_activity_safe_handoff(paper_id: str) -> dict[str, Any]:
    packet = BASE / "packets" / paper_id
    tables_path = packet / "extracted/pdf_tables.json"
    table_text_by_locator: dict[str, str] = {}
    if tables_path.exists():
        tables_data = read_json(tables_path)
        for item in tables_data.get("tables", []):
            if isinstance(item, dict) and item.get("locator"):
                table_text_by_locator[str(item["locator"])] = str(item.get("text") or "")
    machine_path = packet / "database/dbaasp_machine_extracted_rows.jsonl"
    machine_rows = read_jsonl(machine_path) if machine_path.exists() else []
    machine_candidates: list[dict[str, Any]] = []
    duplicate_counter: Counter[str] = Counter()
    for row in machine_rows:
        if not isinstance(row, dict):
            continue
        entity = normalize_candidate_name(row.get("peptide"))
        key = "|".join(
            [
                entity,
                normalize_identifier(row.get("sequence")),
                normalize_identifier(row.get("endpoint")),
                normalize_identifier(row.get("value")),
                normalize_identifier(row.get("unit")),
                normalize_identifier(row.get("target")),
                normalize_identifier(row.get("evidence")),
            ]
        )
        duplicate_counter[key] += 1
    for index, row in enumerate(machine_rows, start=1):
        if not isinstance(row, dict):
            continue
        evidence = normalize_identifier(row.get("evidence"))
        locators: list[dict[str, Any]] = []
        if "Table 1" in evidence:
            locators = [{"locator": "xml:table-wrap:1", "source": "extracted/pdf_tables.json", "tag": "table-wrap"}]
        elif "Table 2" in evidence:
            locators = [{"locator": "xml:table-wrap:2", "source": "extracted/pdf_tables.json", "tag": "table-wrap"}]
        else:
            toxicity_terms = toxicity_locator_terms(row.get("endpoint"), evidence)
            if toxicity_terms:
                locators = locator_refs_for_terms(packet, toxicity_terms, max_count=8)
        entity = normalize_candidate_name(row.get("peptide"))
        key = "|".join(
            [
                entity,
                normalize_identifier(row.get("sequence")),
                normalize_identifier(row.get("endpoint")),
                normalize_identifier(row.get("value")),
                normalize_identifier(row.get("unit")),
                normalize_identifier(row.get("target")),
                evidence,
            ]
        )
        machine_candidates.append(
            {
                "machine_row_index": index,
                "candidate_key": hashlib.sha1(key.encode("utf-8")).hexdigest()[:12],
                "duplicate_group_size": duplicate_counter[key],
                "entity": entity,
                "sequence": None if row.get("sequence") in {None, "", "None"} else row.get("sequence"),
                "endpoint": row.get("endpoint"),
                "raw_value": row.get("value"),
                "raw_unit": row.get("unit"),
                "target": row.get("target"),
                "assay_medium": row.get("assay_medium"),
                "inoculum": row.get("inoculum"),
                "modification": row.get("modification"),
                "machine_verdict": row.get("verdict"),
                "machine_evidence": evidence,
                "source_locator_candidates": locators,
                "status": "machine_candidate_only_requires_source_review",
            }
        )

    table1_rows: list[dict[str, Any]] = []
    table2_rows: list[dict[str, Any]] = []
    excluded_table2: list[dict[str, Any]] = []
    table1_text = table_text_by_locator.get("xml:table-wrap:1", "")
    table2_text = table_text_by_locator.get("xml:table-wrap:2", "")
    if all(term in table1_text for term in ["black soldier fly", "F 1", "F 2", "L. monocytogenes"]):
        table1_rows = table1_safe_rows(paper_id)
    if all(term in table2_text for term in ["CGPPRQGPFPR", "HLEEELK", "KGNSELEEAKKK"]):
        table2_rows, excluded_table2 = table2_safe_rows(paper_id)
    deterministic_rows = table1_rows + table2_rows
    generic_activity_tables = activity_table_locator_candidates(table_text_by_locator)
    toxicity_locators = locator_refs_for_terms(packet, TOXICITY_SEARCH_TERMS, max_count=10)
    handoff = {
        "paper_id": paper_id,
        "generated_at": utc_now(),
        "artifact_role": "safe_worker2_activity_candidate_handoff",
        "safety_boundary": {
            "do_not_read_full_source_text_into_model_context": True,
            "omitted_fields": ["xml_full_text", "pdf_full_text", "table_full_text", "source_passages"],
            "allowed_review_surface": "short controlled row values, source locator IDs, and packet paths",
        },
        "source_files": {
            "pdf_tables": str(packet / "extracted/pdf_tables.json"),
            "locator_index": str(packet / "locators/locator_index.json"),
            "machine_candidates": str(machine_path),
        },
        "source_locator_groups": {
            "activity_table_locator_candidates": generic_activity_tables,
            "table_1_mic_fraction_rows": (
                [{"locator": "xml:table-wrap:1", "source": "extracted/pdf_tables.json"}] if table1_rows else []
            ),
            "table_2_mic_peptide_rows": (
                [{"locator": "xml:table-wrap:2", "source": "extracted/pdf_tables.json"}]
                if table2_rows or excluded_table2
                else []
            ),
            "mic_method_locator_candidates": locator_refs_for_terms(
                packet, ["minimum inhibitory concentration", "inoculum", "muller", "mhb"], max_count=10
            ),
            "toxicity_locator_candidates": toxicity_locators,
            "hemolysis_locator_candidates": toxicity_locators,
        },
        "deterministic_table_candidate_rows": deterministic_rows,
        "excluded_non_activity_table_entries": excluded_table2,
        "machine_candidate_rows": machine_candidates,
        "worker2_instructions": [
            "Use deterministic_table_candidate_rows as the first source-located scaffold.",
            "Use activity_table_locator_candidates only as locators to inspect; derive each endpoint from that table's own header/caption.",
            "An empty legacy table_1/table_2 group means those table numbers are not assay tables for this paper.",
            "Compare machine_candidate_rows only as candidate/database provenance; do not promote duplicates without source-locator review.",
            "Do not create activity rows for excluded_non_activity_table_entries with activity_field=ND.",
            "Never label preparation, composition, FTIR, thermal, wettability, or mechanical-property cells as MIC/activity rows.",
            "Never invent or coerce raw_unit; preserve the exact endpoint-specific unit supported by the source header/caption.",
            "If hemolysis rows are kept, mark them source-reviewed only if the cited locator supports the raw value; otherwise keep as unresolved/excluded candidate.",
            "Write row-level JSON artifacts; final terminal output should list only paths, counts, status, and blockers.",
        ],
        "counts": {
            "deterministic_table_candidate_rows": len(deterministic_rows),
            "excluded_non_activity_table_entries": len(excluded_table2),
            "activity_table_locator_candidates": len(generic_activity_tables),
            "toxicity_locator_candidates": len(toxicity_locators),
            "machine_candidate_rows": len(machine_candidates),
            "machine_duplicate_candidate_rows": sum(max(count - 1, 0) for count in duplicate_counter.values()),
        },
    }
    out_path = packet / "analysis/activity_safe_candidate_handoff.json"
    write_json(out_path, handoff)
    return handoff


def worker_prompt(paper_id: str, worker: str) -> str:
    paper_root = BASE / "papers" / paper_id
    packet = BASE / "packets" / paper_id
    activity_handoff = packet / "analysis/activity_safe_candidate_handoff.json"
    leader_preflight_root = paper_root / "work/leader_preflight"
    leader_preflight_contracts = sorted(
        path
        for path in leader_preflight_root.glob("*.json")
        if path.is_file() and "contract" in path.name.lower()
    )
    leader_preflight_evidence = sorted(
        path
        for path in leader_preflight_root.glob("*.json")
        if path.is_file() and path not in set(leader_preflight_contracts)
    )
    common_refs = "\n".join(f"- {path}" for path in REQUIRED_REFERENCES)
    skill = WORKER_SKILLS[worker]
    requests = read_jsonl(packet / "rework/rework_requests.jsonl")
    runtime_open_ids = {
        str(row.get("ticket_id") or "") for row in open_rework_tickets(packet)
    }
    if worker == "worker-6":
        assigned_open_ticket_ids = sorted(runtime_open_ids)
    else:
        assigned_open_ticket_ids = sorted(
            str(row.get("ticket_id") or "")
            for row in requests
            if str(row.get("ticket_id") or "") in runtime_open_ids
            and worker in set(re.findall(r"worker-[1-6]", str(row.get("owner_worker") or "").lower()))
        )
    assigned_open_ticket_contracts = [
        row
        for row in requests
        if str(row.get("ticket_id") or "") in set(assigned_open_ticket_ids)
    ]
    if worker == "worker-6":
        rework_instruction = """For every currently open rework ticket, independently verify the repaired owner-lane artifact against the ticket contract, rebuild the final and packet-final mirrors, and run the packet, semantic, and publication gates without allow flags. The Runtime-open ticket IDs assigned to worker-6 list is authoritative: if a ticket is listed there, any earlier closed/repaired response is an invalid or superseded candidate under the current runtime contract and you must append a new complete terminal response after verification; never skip a listed ticket merely because rework_responses.jsonl already contains a closed-looking string. An owner-lane ticket must already have a nonterminal, evidence-bearing, analysis_can_resume response from every named owner worker; adjudication-owned tickets are exempt from that owner-response prerequisite. Only when the ticket contract is fully satisfied, all three strict gates pass, review_status is accepted_clean or accepted_with_cautions, publication_grade is true, and no hard rework target remains, append exactly one new valid terminal adjudication response to rework_responses.jsonl. The runtime closure schema is mandatory: status and response_status must both be exactly closed_repaired; response_by must be worker-6; analysis_can_resume and publication_grade must be true; review_status must be accepted_clean or accepted_with_cautions; created_at and final_counts must be present; final_counts must exactly include activity_records, toxicity_records, database_record_audits, mechanism_claims, and review_rework_targets; ticket_contract_evidence.overall_contract_pass must be true; gate_return_codes must contain packet, semantic, and publication values all equal to 0; gate_artifact_paths must identify fresh post-response reports with the formal pass schema for those three strict gates and the correct single-paper manifest; and verified_artifact_paths must contain both paper and packet final paths for activity_toxicity_evidence, database_record_verification, review_report, and the aligned mechanism final. The paper/packet final mirror pairs must be byte-identical. The packet gate may initially report only the exact ticket IDs being closed; after appending all terminal responses, rerun all three gates so the same artifact paths are newer than the response and the packet report has zero unrelated open tickets. This adjudication response may close a repaired owner-lane ticket; it does not replace the owner's nonterminal repair response. If any owner response, contract item, source proof, final rebuild, mirror, manifest binding, count, or strict gate is incomplete, leave the ticket open and write a concrete rework target instead. Never append another terminal response only when the runtime-open list confirms that ticket is already closed."""
    else:
        rework_instruction = """The Runtime-open ticket IDs assigned to your worker list is authoritative. For every listed ticket, append one fresh owner-repair response row to rework_responses.jsonl after verifying or repairing the current artifact, even when the artifact itself needs no further change and even when an older response exists. Every owner response is nonterminal and must contain these top-level fields exactly: ticket_id set to the listed ticket; response_status repair_ready_for_adjudication; response_by set to your worker ID; analysis_can_resume true; and at least one non-empty evidence, evidence_paths, repaired_artifacts, artifacts_written, added_files, validation_artifacts, reason, or notes field. Do not put analysis_can_resume only inside a nested summary. Never use closed*, resolved*, repaired_*_complete, needs_followup, or blocked_* as the response status for a repair-ready ticket. Only worker-6 may append terminal closed_repaired after final rebuild and strict adjudication. Do not respond to a ticket not assigned to your worker."""
    worker_outputs = {
        "worker-1": """
Write or update:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/work/intake/source_inventory.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/work/intake/intake_report.md
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/{paper_id}/analysis/analysis_status.json only if intake status changes
Do not make source_verified claims.
""",
        "worker-2": """
Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/work/activity_evidence/activity_records.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/{paper_id}/analysis/activity_toxicity_evidence.worker2.json
Rows must be source-located with endpoint, raw_value, raw_unit or no-unit rationale, target species/strain, assay conditions, evidence_ladder, and source_locator.
Every row must use normalization_status exactly as direct, converted, not_convertible, or ambiguous. Direct/converted rows require normalized_value and normalized_unit. Direct means no value or unit conversion: do not copy a stale normalized value, change the unit, or hide a conversion under direct; put any non-conversion or ambiguity reason in a dedicated normalization note/rationale.
Use the safe candidate handoff first:
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/{paper_id}/analysis/activity_safe_candidate_handoff.json
Treat activity_table_locator_candidates as inspection hints only. Derive the endpoint, target, and unit from the cited table's own caption/header; table number or a machine label is never enough.
Do not emit activity rows from formulation/composition, FTIR/spectroscopy, TGA/thermal, contact-angle, tensile/mechanical, or reference columns.
Do not relabel a source unit to make a validator pass. If the source does not support an endpoint-specific unit, exclude or keep the candidate unresolved rather than inventing one.
Quantitative activity or toxicity evidence may be supported by an exact XML paragraph, figure/caption, or PDF-page locator. Lack of a source table is not a reason to discard it when treatment, endpoint, target, value, unit, and assay context are source-supported; emit the row or open a concrete ambiguity ticket instead of claiming no evidence.
Keep redundant record fields semantically identical: top-level concentration/concentration_unit must agree with any assay_conditions peptide/sample concentration copy. A stale nested scaffold value is a hard data conflict, not harmless metadata.
If a rework ticket asks about toxicity and all matched percentage surfaces are non-biological material measurements, write durable no-source-located-toxicity evidence in a nonterminal owner-repair response for your worker-2 ticket.
If a rework ticket declares expected_shape, expected_observation_counts, require_cell_locators, or expected_cell_observations, prove the full contract before marking your owner repair ready for worker-6 adjudication. Every expected_cell_observations locator must bind to that cell's named endpoint, value, unit, treatment, concentration/timepoint, and target fields; unique coordinates attached to the wrong existing rows are a hard failure. Do not satisfy a table ticket by attaching its base locator to unrelated existing rows, and do not mirror the same observation in both activity_records and toxicity_records.
Do not open raw paper XML/PDF, full xml_sections.json, full pdf_text.jsonl, or full table text in model context. If exact locator checking is needed, run a bounded local Python command that extracts only the requested locator IDs into a small JSON artifact under work/activity_evidence/, then read that small artifact. Terminal output must not contain source passages.
""",
        "worker-3": """
Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/work/supplementary_methods/supplementary_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/{paper_id}/analysis/supplementary_evidence.worker3.json
Inventory every staged or referenced supplement; record exact missing/unparsed material and impact.
When a blocking ticket requires quantitative figure observations, inspect the staged figure asset and recover every requested visible bar/point with axis calibration, approximate raw value, raw unit, uncertainty, image coordinates or equivalent calibration evidence, exact-vs-approximate status, and treatment/control role. A null raw_value or raw_unit is not a completed digitization when the plotted mark and axis can be calibrated. If the asset or scale is genuinely insufficient, leave the ticket open and record the exact material gap instead of emitting null placeholders as a repaired result.
""",
        "worker-4": """
Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/work/database_record_audit/record_identity_audit.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/{paper_id}/analysis/database_record_audit.worker4.json
Use only statuses: source_verified, source_conflict, database_only_no_primary_source, sequence_modified_not_normalized, unresolved_record. Preserve DBAASP machine rows as candidate/database provenance until source-reviewed.
""",
        "worker-5": """
Write:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/work/mechanism_ontology/mechanism_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/{paper_id}/analysis/mechanism_evidence.worker5.json
Every mechanism_claim must have claim_id, claim_text, entity_scope, evidence_class, source_locator, and direct_assay_types when direct.
Set review_model exactly to gpt-5.5 and reasoning_effort exactly to xhigh in both required artifacts; the independent run report is the runtime proof.
""",
        "worker-6": """
Write final adjudication outputs:
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/work/review/adjudication_report.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/work/review/quality_feedback.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/final/database_record_verification.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/final/activity_toxicity_evidence.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/final/mechanism_ontology_record.json
- pipeline_v2/deepmine/dbaasp_strict_pilot/papers/{paper_id}/final/review_report.json
Also copy/align final mechanism to:
- pipeline_v2/deepmine/dbaasp_strict_pilot/packets/{paper_id}/final/mechanism_evidence.json
and mirror all final files under the packet final/ directory.
When a newer worker-2 artifact repairs an open activity/toxicity ticket, first rebuild the adjudication candidate and both final mirrors from that current worker artifact, then run strict gates on the rebuilt final. Do not gate the stale pre-repair final and reopen an already repaired ticket merely because the old final still fails.
If hard gates fail, use review_status=needs_targeted_rework or blocked_missing_primary_material, publication_grade=false, and concrete rework_targets plus packet rework tickets.
Before accepting, reject any activity row whose cited table is formulation/composition, FTIR/spectroscopy, TGA/thermal, wettability, or mechanical data, and reject endpoint/unit values not supported by that table's own caption/header. Never repair such rows by guessing or changing units.
For every rework ticket with expected_shape, expected_observation_counts, require_cell_locators, or expected_cell_observations, independently compare the final unique row count, exact row/cell locators, and cell-bound fields against that contract. A base-table citation, a closed response, unique-but-misassigned coordinates, or validator success does not prove cell-level completeness. Reject duplicated observations mirrored across activity_records and toxicity_records, and reject unrelated rows that merely gained the requested table locator.
For a blocking quantitative-figure ticket, reject closure when a requested visible bar/point remains absent from the final arrays or has null raw_value/raw_unit despite a calibratable staged image. Require approximate/exact status, calibration evidence, uncertainty, and treatment/control role for digitized values; preserve approximation rather than promoting it to an exact table value.
Reject a row/cell-level table locator when that table's own caption/header does not support the row endpoint, even if another PDF/figure locator supports the measurement. Remove the false table-cell locator rather than deleting a valid source-supported endpoint. Independently verify normalization_status and normalized value/unit consistency under the same canonical contract required of worker-2.
Quantitative activity or toxicity evidence may be supported by an exact XML paragraph, figure/caption, or PDF-page locator. Lack of a source table is not a reason to discard it when treatment, endpoint, target, value, unit, and assay context are source-supported; reject a no-evidence claim that merely excludes such figure/text records.
Reject final records whose top-level concentration/concentration_unit contradict any redundant assay_conditions peptide/sample concentration copy; stale nested scaffold metadata must be repaired before acceptance.
If the only remaining blocker is missing authoritative DBAASP linked rows, and
the packet contains durable no-match evidence plus a nonterminal owner-repair
response with analysis_can_resume=true, do not keep an infinite hard rework
target solely for zero linked rows. Preserve this as accepted_with_cautions only
when fallback rows remain unresolved/database-only and are not promoted to
source_verified or authoritative DBAASP ingest-ready. Authoritative ingest must
remain false until real linked article/assay/sequence/literature rows exist. The
ticket still requires the same strict worker-6 closed_repaired terminal schema.
""",
    }[worker].format(paper_id=paper_id)

    return f"""You are {worker} for an AMP three-layer DBAASP strict pilot.

Hard constraints:
- Use this checkout only; do not browse the internet.
- Work only on paper_id {paper_id}.
- Read and obey your worker skill: {skill}
- Read and obey these strict references:
{common_refs}
- Use source-reviewed, paper-local evidence from this packet. Treat DBAASP Codex fallback rows as candidate machine evidence only.
- Keep human/source-reviewed claims separate from machine extraction.
- Read and obey every listed leader preflight contract before reviewing the
  source. Contracts define required coverage/conflict preservation but do not
  replace source evidence.
- Use and independently verify leader evidence scaffolds; preserve approximate,
  unresolved, and candidate status rather than promoting scaffold values to
  exact source facts.
- Do not claim publication-grade unless the required strict gates can pass.
- Write the requested files directly; keep JSON valid and paper-specific.
- Keep terminal output compact. Do not print XML/PDF/supplement excerpts,
  table text, assay-method prose, source sentences, or biomedical passages to
  stdout/stderr/final messages. Do not run shell commands that print source text
  to the terminal; write derived JSON/TSV/MD artifacts to your work directory and
  report only file paths, counts, statuses, short locator IDs, and field names.
- This is literature/database curation only. Do not provide wet-lab protocols,
  optimization advice, or actionable biological experimentation guidance.

Current inputs:
- Paper root: {paper_root}
- Packet root: {packet}
- Packet manifest: {packet / 'packet_manifest.json'}
- XML sections: {packet / 'extracted/xml_sections.json'}
- PDF text: {packet / 'extracted/pdf_text.jsonl'}
- Supplement index/text: {packet / 'extracted/supplementary_index.json'} and {packet / 'extracted/supplementary_text.jsonl'}
- Database snapshot: {packet / 'database/database_source_manifest.json'}
- DBAASP candidate rows: {packet / 'database/dbaasp_machine_extracted_rows.jsonl'}
- Safe worker-2 activity handoff: {activity_handoff}
- Leader preflight contracts: {json.dumps([str(path) for path in leader_preflight_contracts], ensure_ascii=False)}
- Leader preflight evidence scaffolds: {json.dumps([str(path) for path in leader_preflight_evidence], ensure_ascii=False)}
- Authoritative DBAASP/merged match report: {packet / 'database/authoritative_match_report.json'}
- Linked authoritative rows, if any: {packet / 'database/linked_article_records.jsonl'}, {packet / 'database/linked_assay_records.jsonl'}, {packet / 'database/linked_sequence_records.jsonl'}, {packet / 'database/linked_literature_records.jsonl'}
- Codex session audit: {packet / 'database/codex_session_audit.jsonl'}
- Packet gate script: {CHECK_PACKET_SCRIPT}
- Semantic gate script: {SEMANTIC_GATE}
- Publication gate script: {PUBLICATION_GATE}
- Rework requests/responses: {packet / 'rework/rework_requests.jsonl'} and {packet / 'rework/rework_responses.jsonl'}
- Runtime-open ticket IDs assigned to {worker}: {json.dumps(assigned_open_ticket_ids, ensure_ascii=False)}
- Runtime-open ticket contracts assigned to {worker}: {json.dumps(assigned_open_ticket_contracts, ensure_ascii=False, indent=2)}

{rework_instruction}

Required outputs for this worker:
{worker_outputs}

Return a concise final message listing files written, unresolved blockers, and whether your lane is source-reviewed complete or needs targeted rework.
"""


def write_prompts(paper_ids: list[str]) -> list[Path]:
    paths: list[Path] = []
    for paper_id in paper_ids:
        for worker in WORKER_SKILLS:
            if worker == "worker-2":
                build_activity_safe_handoff(paper_id)
            path = BASE / "prompts" / paper_id / f"{worker}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(worker_prompt(paper_id, worker), encoding="utf-8")
            paths.append(path)
    return paths


def run_cmd(cmd: list[str], *, input_text: str | None = None, timeout: int = 120) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, input=input_text, capture_output=True, text=True, timeout=timeout, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def parse_codex_stderr_metadata(stderr: str) -> dict[str, str | None]:
    """Capture the Codex run identity so future audits do not need log parsing."""
    patterns = {
        "codex_session_id": r"session id:\s*([0-9a-f-]+)",
        "codex_model": r"model:\s*(\S+)",
        "codex_reasoning_effort": r"reasoning effort:\s*(\S+)",
    }
    metadata: dict[str, str | None] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, stderr)
        metadata[key] = match.group(1) if match else None
    return metadata


def classify_worker_failure(returncode: int, stderr: str) -> dict[str, str] | dict[str, None]:
    if returncode == 0:
        return {"failure_code": None, "failure_summary": None}
    if "Invalid prompt" in stderr and "limited access to this content" in stderr:
        return {
            "failure_code": "model_safety_content_filter",
            "failure_summary": "Codex rejected the worker continuation after biological source-text content entered the model context.",
        }
    if "TimeoutExpired" in stderr or "timed out" in stderr.lower():
        return {"failure_code": "worker_timeout", "failure_summary": "Worker command timed out before completion."}
    return {"failure_code": "worker_nonzero_exit", "failure_summary": "Worker command returned a nonzero exit code."}


def codex_worker_command(output_path: Path) -> list[str]:
    return [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        "-m",
        "gpt-5.5",
        "-c",
        'model_reasoning_effort="xhigh"',
        "-C",
        str(ROOT),
        "-o",
        str(output_path),
        "-",
    ]


def run_worker(paper_id: str, worker: str, timeout: int, run_id: str | None = None) -> dict[str, Any]:
    prompt_path = BASE / "prompts" / paper_id / f"{worker}.md"
    if worker == "worker-2":
        build_activity_safe_handoff(paper_id)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(worker_prompt(paper_id, worker), encoding="utf-8")
    out_dir = BASE / "worker_logs" / paper_id
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = run_id or re.sub(r"[^0-9A-Za-z]+", "", utc_now())
    final_message = out_dir / f"{run_id}.{worker}.last_message.md"
    stdout_path = out_dir / f"{run_id}.{worker}.stdout.log"
    stderr_path = out_dir / f"{run_id}.{worker}.stderr.log"
    started = utc_now()
    cmd = codex_worker_command(final_message)
    code, stdout, stderr = run_cmd(cmd, input_text=prompt_path.read_text(encoding="utf-8"), timeout=timeout)
    stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
    report = {
        "paper_id": paper_id,
        "worker": worker,
        "command": cmd,
        "started_at": started,
        "finished_at": utc_now(),
        "returncode": code,
        "prompt_path": str(prompt_path),
        "final_message_path": str(final_message),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        **parse_codex_stderr_metadata(stderr),
        **classify_worker_failure(code, stderr),
    }
    write_json(out_dir / f"{run_id}.{worker}.run_report.json", report)
    write_json(out_dir / f"{worker}.run_report.json", report)
    latest_message = final_message.read_text(encoding="utf-8", errors="replace") if final_message.exists() else ""
    (out_dir / f"{worker}.last_message.md").write_text(latest_message, encoding="utf-8")
    (out_dir / f"{worker}.stdout.log").write_text(stdout, encoding="utf-8", errors="replace")
    (out_dir / f"{worker}.stderr.log").write_text(stderr, encoding="utf-8", errors="replace")
    return report


def write_run_sequence(paper_id: str, workers: list[str], reports: list[dict[str, Any]], *, merge_existing: bool = False) -> dict[str, Any]:
    path = BASE / "worker_logs" / paper_id / "run_sequence_latest.json"
    if merge_existing:
        existing = safe_read_json(path)
        merged_by_worker: dict[str, dict[str, Any]] = {}
        existing_reports = existing.get("reports") if isinstance(existing.get("reports"), list) else []
        for item in existing_reports:
            if isinstance(item, dict) and item.get("worker"):
                merged_by_worker[str(item["worker"])] = item
        for item in reports:
            if isinstance(item, dict) and item.get("worker"):
                merged_by_worker[str(item["worker"])] = item
        merged_workers = [worker for worker in WORKER_SKILLS if worker in merged_by_worker]
        data = {"paper_id": paper_id, "workers": merged_workers, "reports": [merged_by_worker[worker] for worker in merged_workers]}
    else:
        data = {"paper_id": paper_id, "workers": workers, "reports": reports}
    write_json(path, data)
    return data


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            rows.append({"_parse_error": line[:500]})
            continue
        rows.append(row if isinstance(row, dict) else {"_not_object": row})
    return rows


def live_locator_count(packet: Path) -> int:
    index = safe_read_json(packet / "locators/locator_index.json")
    locators = index.get("locators")
    if isinstance(locators, list):
        return len(locators)
    try:
        return int(index.get("locator_count") or 0)
    except (TypeError, ValueError):
        return 0


def live_extraction_errors(packet: Path) -> list[dict[str, Any]]:
    return read_jsonl(packet / "extraction/extraction_errors.jsonl")


def recursive_authority_true_locations(value: Any, pointer: str = "$") -> list[str]:
    locations: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = f"{pointer}/{str(key).replace('~', '~0').replace('/', '~1')}"
            if key == "authoritative_dbaasp_ingest_ready" and child is True:
                locations.append(child_pointer)
            locations.extend(recursive_authority_true_locations(child, child_pointer))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            locations.extend(recursive_authority_true_locations(child, f"{pointer}/{index}"))
    return locations


def recursive_sequence_length_mismatches(
    value: Any, pointer: str = "$"
) -> list[dict[str, Any]]:
    """Find self-contradictory standard-residue sequence lengths.

    Modified, ambiguous, or nonstandard residue strings are left to scientific
    review. A plain standard one-letter sequence, however, has an unambiguous
    residue count and must agree with a sibling ``sequence_length`` field.
    """
    findings: list[dict[str, Any]] = []
    if isinstance(value, dict):
        sequence = value.get("sequence")
        declared = value.get("sequence_length")
        if (
            isinstance(sequence, str)
            and sequence == sequence.strip().upper()
            and re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWY]+", sequence)
            and isinstance(declared, int)
            and not isinstance(declared, bool)
            and declared != len(sequence.strip())
        ):
            findings.append(
                {
                    "json_pointer": pointer,
                    "sequence": sequence,
                    "declared_sequence_length": declared,
                    "actual_sequence_length": len(sequence.strip()),
                }
            )
        for key, child in value.items():
            child_pointer = f"{pointer}/{str(key).replace('~', '~0').replace('/', '~1')}"
            findings.extend(
                recursive_sequence_length_mismatches(child, child_pointer)
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                recursive_sequence_length_mismatches(child, f"{pointer}/{index}")
            )
    return findings


def recursive_non_source_locator_references(
    value: Any, pointer: str = "$"
) -> list[dict[str, str]]:
    """Reject project artifacts recursively presented as primary-source locators."""
    locator_keys = {
        "source_locator",
        "source_locators",
        "supporting_source_locators",
    }
    project_prefixes = (
        "papers/",
        "packets/",
        "pipeline_v2/",
        "worker_logs/",
        "reports/",
    )
    project_segments = ("/analysis/", "/work/", "/final/")
    findings: list[dict[str, str]] = []

    def strings(child: Any) -> list[str]:
        if isinstance(child, str):
            return [child]
        if isinstance(child, list):
            return [item for nested in child for item in strings(nested)]
        return []

    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = f"{pointer}/{str(key).replace('~', '~0').replace('/', '~1')}"
            if key in locator_keys:
                for locator in strings(child):
                    lowered = locator.lower()
                    if (
                        locator.startswith("/")
                        or lowered.startswith(project_prefixes)
                        or any(segment in lowered for segment in project_segments)
                    ):
                        findings.append(
                            {
                                "json_pointer": child_pointer,
                                "non_source_locator": locator,
                            }
                        )
            findings.extend(
                recursive_non_source_locator_references(child, child_pointer)
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                recursive_non_source_locator_references(
                    child, f"{pointer}/{index}"
                )
            )
    return findings


def current_artifact_json_paths(paper_id: str) -> list[Path]:
    roots = [
        BASE / "papers" / paper_id / "work",
        BASE / "papers" / paper_id / "final",
        BASE / "packets" / paper_id / "analysis",
        BASE / "packets" / paper_id / "final",
    ]
    paths: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        paths.extend(path for path in root.rglob("*.json") if path.is_file())
        paths.extend(path for path in root.rglob("*.jsonl") if path.is_file())
    return sorted(set(paths))


def strict_artifact_consistency_findings(paper_id: str) -> list[dict[str, Any]]:
    """Find authority-boundary and material-count contradictions before sync repairs."""
    findings: list[dict[str, Any]] = []
    packet = BASE / "packets" / paper_id

    for path in current_artifact_json_paths(paper_id):
        payloads: list[tuple[str, Any]] = []
        if path.suffix == ".jsonl":
            payloads = [(f"line:{index}", row) for index, row in enumerate(read_jsonl(path), start=1)]
        else:
            try:
                payloads = [("document", read_json(path))]
            except Exception:  # noqa: BLE001 - parse quality is covered by packet/publication gates
                continue
        for record_label, payload in payloads:
            for pointer in recursive_authority_true_locations(payload):
                findings.append(
                    {
                        "paper_id": paper_id,
                        "severity": "hard",
                        "code": "recursive_authority_boundary_true",
                        "path": str(path),
                        "record": record_label,
                        "json_pointer": pointer,
                        "required_value": False,
                    }
                )
            for mismatch in recursive_sequence_length_mismatches(payload):
                findings.append(
                    {
                        "paper_id": paper_id,
                        "severity": "hard",
                        "code": "sequence_length_mismatch",
                        "path": str(path),
                        "record": record_label,
                        **mismatch,
                    }
                )
            for reference in recursive_non_source_locator_references(payload):
                findings.append(
                    {
                        "paper_id": paper_id,
                        "severity": "hard",
                        "code": "recursive_non_source_locator_reference",
                        "path": str(path),
                        "record": record_label,
                        **reference,
                    }
                )

    review_path = BASE / "papers" / paper_id / "final/review_report.json"
    if review_path.exists():
        review = safe_read_json(review_path)
        semantic_checks = review.get("semantic_quality_checks")
        semantic_checks = semantic_checks if isinstance(semantic_checks, dict) else {}
        declared_open_count = semantic_checks.get("open_rework_ticket_count")
        if isinstance(declared_open_count, int) and not isinstance(
            declared_open_count, bool
        ):
            actual_open_count = len(open_rework_tickets(packet))
            if declared_open_count != actual_open_count:
                findings.append(
                    {
                        "paper_id": paper_id,
                        "severity": "hard",
                        "code": "review_report_open_ticket_count_mismatch",
                        "path": str(review_path),
                        "json_pointer": (
                            "$/semantic_quality_checks/open_rework_ticket_count"
                        ),
                        "declared_open_rework_ticket_count": declared_open_count,
                        "actual_open_rework_ticket_count": actual_open_count,
                        "ticket_paths": [
                            str(packet / "rework/rework_requests.jsonl"),
                            str(packet / "rework/rework_responses.jsonl"),
                        ],
                    }
                )

    packet_manifest = safe_read_json(packet / "packet_manifest.json")
    locator_index = safe_read_json(packet / "locators/locator_index.json")
    if packet_manifest and locator_index and "_parse_error" not in locator_index:
        locator_rows = locator_index.get("locators")
        actual_count = len(locator_rows) if isinstance(locator_rows, list) else None
        declared_count = locator_index.get("locator_count")
        manifest_count = packet_manifest.get("locator_count")
        compared = [manifest_count, declared_count, actual_count]
        if actual_count is not None and any(value != actual_count for value in compared):
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "locator_count_mismatch",
                    "packet_manifest_locator_count": manifest_count,
                    "locator_index_declared_count": declared_count,
                    "locator_index_actual_count": actual_count,
                    "paths": [
                        str(packet / "packet_manifest.json"),
                        str(packet / "locators/locator_index.json"),
                    ],
                }
            )

    extraction_status = safe_read_json(packet / "extraction/extraction_status.json")
    errors_path = packet / "extraction/extraction_errors.jsonl"
    if extraction_status and errors_path.exists():
        status_count = extraction_status.get("error_count")
        actual_count = len(live_extraction_errors(packet))
        if status_count != actual_count:
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "extraction_error_count_mismatch",
                    "extraction_status_error_count": status_count,
                    "extraction_errors_actual_count": actual_count,
                    "paths": [
                        str(packet / "extraction/extraction_status.json"),
                        str(errors_path),
                    ],
                }
            )

    rolling_manifest = safe_read_json(BASE / "manifests/dbaasp_strict_pilot_manifest.json")
    rolling_rows = rolling_manifest.get("papers") if isinstance(rolling_manifest.get("papers"), list) else []
    rolling_row = next(
        (
            item
            for item in rolling_rows
            if isinstance(item, dict) and str(item.get("paper_id") or "") == paper_id
        ),
        None,
    )
    if rolling_row is not None:
        live_locator = live_locator_count(packet)
        live_errors = len(live_extraction_errors(packet))
        if rolling_row.get("locator_count") != live_locator or rolling_row.get("error_count") != live_errors:
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "rolling_manifest_material_count_mismatch",
                    "manifest_locator_count": rolling_row.get("locator_count"),
                    "live_locator_count": live_locator,
                    "manifest_error_count": rolling_row.get("error_count"),
                    "live_error_count": live_errors,
                    "path": str(BASE / "manifests/dbaasp_strict_pilot_manifest.json"),
                }
            )
    return findings


def rework_response_is_closed(row: dict[str, Any]) -> bool:
    codes = row.get("gate_return_codes")
    contract = row.get("ticket_contract_evidence")
    verified = row.get("verified_artifact_paths")
    gate_artifacts = row.get("gate_artifact_paths")
    return bool(
        str(row.get("status") or "").strip().lower() == "closed_repaired"
        and str(row.get("response_status") or "").strip().lower() == "closed_repaired"
        and str(row.get("response_by") or "").strip().lower() == "worker-6"
        and row.get("analysis_can_resume") is True
        and row.get("publication_grade") is True
        and str(row.get("review_status") or "").strip().lower()
        in {"accepted_clean", "accepted_with_cautions"}
        and bool(str(row.get("created_at") or "").strip())
        and isinstance(row.get("final_counts"), dict)
        and isinstance(contract, dict)
        and contract.get("overall_contract_pass") is True
        and isinstance(codes, dict)
        and all(codes.get(name, codes.get(f"{name}_gate")) == 0 for name in ("packet", "semantic", "publication"))
        and isinstance(verified, dict)
        and bool(verified)
        and isinstance(gate_artifacts, dict)
        and bool(gate_artifacts)
    )


def _resolve_rework_artifact_path(value: Any, packet: Path) -> Path | None:
    text = str(value or "").strip()
    if not text:
        return None
    path = Path(text)
    if path.is_absolute():
        return path
    candidates = [ROOT / path, packet.parent.parent / path, packet / path]
    return next((candidate for candidate in candidates if candidate.exists()), candidates[0])


def _artifact_path_values(value: Any) -> list[Any]:
    if isinstance(value, dict):
        return [item for nested in value.values() for item in _artifact_path_values(nested)]
    if isinstance(value, list):
        return [item for nested in value for item in _artifact_path_values(nested)]
    return [value]


def _response_epoch(row: dict[str, Any]) -> float | None:
    text = str(row.get("created_at") or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _gate_payloads_valid(
    row: dict[str, Any], packet: Path, closing_ticket_ids: set[str]
) -> tuple[bool, list[Path]]:
    gate_artifacts = row.get("gate_artifact_paths") or {}
    payloads: dict[str, dict[str, Any]] = {}
    paths: list[Path] = []
    for name in ("packet", "semantic", "publication"):
        value = gate_artifacts.get(name, gate_artifacts.get(f"{name}_gate"))
        path = _resolve_rework_artifact_path(value, packet)
        if path is None or not path.exists():
            return False, []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False, []
        if not isinstance(payload, dict):
            return False, []
        payloads[name] = payload
        paths.append(path)

    paper_id = packet.name
    packet_gate = payloads["packet"]
    packet_results = packet_gate.get("results")
    if not (
        packet_gate.get("paper_count") == 1
        and packet_gate.get("hard_finding_count") == 0
        and packet_gate.get("hard_finding_papers") in ([], None)
        and isinstance(packet_results, list)
        and len(packet_results) == 1
        and packet_results[0].get("paper_id") == paper_id
        and packet_results[0].get("hard_findings") in ([], None)
        and packet_results[0].get("missing_packet_files") in ([], None)
        and packet_results[0].get("missing_final_files") in ([], None)
    ):
        return False, []
    packet_open_ids = {
        str(item)
        for item in (packet_results[0].get("open_rework_ticket_ids") or [])
        if str(item)
    }
    if not packet_open_ids.issubset(closing_ticket_ids):
        return False, []
    if packet_gate.get("open_rework_ticket_count") != len(packet_open_ids):
        return False, []

    semantic = payloads["semantic"]
    semantic_results = semantic.get("results")
    if not (
        semantic.get("paper_count") == 1
        and semantic.get("publication_grade_pass_count") == 1
        and semantic.get("publication_grade_fail_count") == 0
        and semantic.get("failed_papers") in ([], None)
        and isinstance(semantic_results, list)
        and len(semantic_results) == 1
        and semantic_results[0].get("paper_id") == paper_id
        and semantic_results[0].get("publication_grade_pass") is True
        and semantic_results[0].get("issue_count") == 0
        and semantic_results[0].get("issues") in ([], None)
    ):
        return False, []

    publication = payloads["publication"]
    risk_counts = publication.get("risk_counts")
    manifest_path = _resolve_rework_artifact_path(publication.get("manifest"), packet)
    if not (
        publication.get("paper_count") == 1
        and publication.get("publication_grade_pass") is True
        and isinstance(risk_counts, dict)
        and not any(int(value or 0) for value in risk_counts.values())
        and manifest_path is not None
        and manifest_path.exists()
    ):
        return False, []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False, []
    if not isinstance(manifest, dict) or manifest.get("paper_ids") != [paper_id]:
        return False, []
    return True, paths


def _terminal_final_state(
    row: dict[str, Any], packet: Path
) -> tuple[list[tuple[Path, Path]], dict[str, int]] | None:
    if not rework_response_is_closed(row):
        return None
    pilot_base = packet.parent.parent if packet.parent.name == "packets" else packet.parent
    paper_root = pilot_base / "papers" / packet.name
    expected_pairs = [
        (
            paper_root / "final/activity_toxicity_evidence.json",
            packet / "final/activity_toxicity_evidence.json",
        ),
        (
            paper_root / "final/database_record_verification.json",
            packet / "final/database_record_verification.json",
        ),
        (paper_root / "final/review_report.json", packet / "final/review_report.json"),
        (
            paper_root / "final/mechanism_ontology_record.json",
            packet / "final/mechanism_evidence.json",
        ),
    ]
    verified = row.get("verified_artifact_paths") or {}
    verified_paths = {
        path.resolve()
        for value in _artifact_path_values(verified)
        if (path := _resolve_rework_artifact_path(value, packet)) is not None
    }
    required_paths = {path.resolve() for pair in expected_pairs for path in pair}
    if not required_paths.issubset(verified_paths):
        return None
    if any(not left.exists() or not right.exists() or left.read_bytes() != right.read_bytes() for left, right in expected_pairs):
        return None

    activity = safe_read_json(expected_pairs[0][0])
    database = safe_read_json(expected_pairs[1][0])
    review = safe_read_json(expected_pairs[2][0])
    mechanism = safe_read_json(expected_pairs[3][0])
    counts = row.get("final_counts") or {}
    actual_counts = {
        "activity_records": len(activity.get("activity_records") if isinstance(activity.get("activity_records"), list) else []),
        "toxicity_records": len(activity.get("toxicity_records") if isinstance(activity.get("toxicity_records"), list) else []),
        "database_record_audits": len(first_list_field(database, ["record_audits", "records", "database_record_audits", "audit_records"])),
        "mechanism_claims": len(mechanism.get("mechanism_claims") if isinstance(mechanism.get("mechanism_claims"), list) else []),
        "review_rework_targets": len(review.get("rework_targets") if isinstance(review.get("rework_targets"), list) else []),
    }
    if any(counts.get(name) != value for name, value in actual_counts.items()):
        return None
    return expected_pairs, actual_counts


def terminal_rework_response_preconditions_valid(row: dict[str, Any], packet: Path) -> bool:
    return _terminal_final_state(row, packet) is not None


def terminal_rework_response_artifacts_valid(
    row: dict[str, Any], packet: Path, closing_ticket_ids: set[str] | None = None
) -> bool:
    final_state = _terminal_final_state(row, packet)
    if final_state is None:
        return False
    expected_pairs, actual_counts = final_state
    if closing_ticket_ids is None:
        closing_ticket_ids = {str(row.get("ticket_id") or "")}
    gate_valid, gate_paths = _gate_payloads_valid(row, packet, closing_ticket_ids)
    if not gate_valid:
        return False
    response_epoch = _response_epoch(row)
    if response_epoch is None or any(path.stat().st_mtime < response_epoch - 1 for path in gate_paths):
        return False
    latest_final_mtime = max(path.stat().st_mtime for pair in expected_pairs for path in pair)
    if any(path.stat().st_mtime + 1 < latest_final_mtime for path in gate_paths):
        return False
    publication = json.loads(gate_paths[2].read_text(encoding="utf-8"))
    publication_counts = publication.get("counts") or {}
    if publication_counts.get("activity_records") != actual_counts["activity_records"]:
        return False
    if publication_counts.get("mechanism_claims") != actual_counts["mechanism_claims"]:
        return False
    return True


def _response_has_repair_evidence(row: dict[str, Any]) -> bool:
    return any(
        row.get(key)
        for key in (
            "evidence",
            "evidence_paths",
            "repaired_artifacts",
            "artifacts_written",
            "added_files",
            "validation_artifacts",
            "closure_basis",
            "reason",
            "notes",
        )
    )


def owner_repair_response_present(
    request: dict[str, Any], prior_responses: list[dict[str, Any]]
) -> bool:
    ticket_id = str(request.get("ticket_id") or "")
    declared_workers = set(re.findall(r"worker-[1-6]", str(request.get("owner_worker") or "").lower()))
    owner_workers = declared_workers - {"worker-6"}
    target_queue = str(request.get("target_queue") or "").lower()
    if declared_workers == {"worker-6"}:
        return True
    if not declared_workers and target_queue == "adjudication":
        return True
    if not owner_workers:
        return False
    eligible = [
        row
        for row in prior_responses
        if str(row.get("ticket_id") or "") == ticket_id
        and str(row.get("response_status") or "").strip().lower()
        == "repair_ready_for_adjudication"
        and re.fullmatch(r"worker-[1-5]", str(row.get("response_by") or "").strip().lower())
        and row.get("analysis_can_resume") is True
        and not rework_response_is_closed(row)
        and _response_has_repair_evidence(row)
    ]
    if owner_workers:
        found = {str(row.get("response_by")).strip().lower() for row in eligible}
        return owner_workers.issubset(found)
    return bool(eligible)


def terminal_response_sha256(row: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def sealed_closure_ticket_ids(
    packet: Path,
    requests: list[dict[str, Any]],
    responses: list[dict[str, Any]],
) -> set[str]:
    requests_by_id = {
        str(request.get("ticket_id") or ""): request
        for request in requests
        if request.get("ticket_id")
    }
    terminal_indices_by_ticket: dict[str, list[int]] = {}
    for index, response in enumerate(responses):
        ticket_id = str(response.get("ticket_id") or "")
        if ticket_id and rework_response_is_closed(response):
            terminal_indices_by_ticket.setdefault(ticket_id, []).append(index)
    valid_by_ticket: dict[str, list[dict[str, Any]]] = {}
    for receipt in read_jsonl(
        packet / "rework/closure_receipts.jsonl"
    ):
        if (
            receipt.get("schema_version")
            != "strict_ticket_closure_receipt_v1"
            or receipt.get("overall_contract_pass") is not True
        ):
            continue
        ticket_id = str(receipt.get("ticket_id") or "")
        request = requests_by_id.get(ticket_id)
        try:
            response_index = int(receipt.get("terminal_response_index"))
        except (TypeError, ValueError):
            continue
        if (
            request is None
            or response_index < 0
            or response_index >= len(responses)
            or terminal_indices_by_ticket.get(ticket_id) != [response_index]
        ):
            continue
        response = responses[response_index]
        if (
            str(response.get("ticket_id") or "") != ticket_id
            or not rework_response_is_closed(response)
            or terminal_response_sha256(response)
            != receipt.get("terminal_response_sha256")
            or not owner_repair_response_present(
                request, responses[:response_index]
            )
        ):
            continue
        valid_by_ticket.setdefault(ticket_id, []).append(receipt)
    return {
        ticket_id
        for ticket_id, receipts in valid_by_ticket.items()
        if len(receipts) == 1
    }


@contextmanager
def closure_receipt_lock(packet: Path):
    lock_path = packet / "rework/.closure_receipts.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield


def seal_ticket_closures(
    packet: Path,
    valid_terminal_by_ticket: dict[
        str, tuple[int, dict[str, Any]]
    ],
    requests: list[dict[str, Any]],
    responses: list[dict[str, Any]],
) -> set[str]:
    if not valid_terminal_by_ticket:
        return sealed_closure_ticket_ids(
            packet, requests, responses
        )
    receipt_path = packet / "rework/closure_receipts.jsonl"
    with closure_receipt_lock(packet):
        receipts = read_jsonl(receipt_path)
        already_valid = sealed_closure_ticket_ids(
            packet, requests, responses
        )
        for ticket_id, (
            response_index,
            response,
        ) in valid_terminal_by_ticket.items():
            if ticket_id in already_valid:
                continue
            artifact_hashes: dict[str, str] = {}
            for key in (
                "verified_artifact_paths",
                "gate_artifact_paths",
            ):
                for value in _artifact_path_values(
                    response.get(key) or {}
                ):
                    path = _resolve_rework_artifact_path(value, packet)
                    if path is not None and path.is_file():
                        artifact_hashes[str(path)] = hashlib.sha256(
                            path.read_bytes()
                        ).hexdigest()
            receipts.append(
                {
                    "schema_version": (
                        "strict_ticket_closure_receipt_v1"
                    ),
                    "ticket_id": ticket_id,
                    "sealed_at": utc_now(),
                    "terminal_response_index": response_index,
                    "terminal_response_sha256": (
                        terminal_response_sha256(response)
                    ),
                    "artifact_sha256_at_seal": artifact_hashes,
                    "owner_response_present_at_seal": True,
                    "overall_contract_pass": True,
                    "current_state_revalidation_required": True,
                }
            )
        write_jsonl(receipt_path, receipts)
    return sealed_closure_ticket_ids(packet, requests, responses)


def open_rework_tickets(packet: Path) -> list[dict[str, Any]]:
    requests = read_jsonl(packet / "rework/rework_requests.jsonl")
    responses = read_jsonl(packet / "rework/rework_responses.jsonl")
    terminal_by_ticket: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, row in enumerate(responses):
        ticket_id = str(row.get("ticket_id") or "")
        if ticket_id and rework_response_is_closed(row):
            terminal_by_ticket.setdefault(ticket_id, []).append((index, row))
    requests_by_id = {str(row.get("ticket_id") or ""): row for row in requests}
    prevalidated_terminal_by_ticket: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for ticket_id, rows in terminal_by_ticket.items():
        request = requests_by_id.get(ticket_id)
        if request is None:
            continue
        for index, row in rows:
            if owner_repair_response_present(request, responses[:index]) and terminal_rework_response_preconditions_valid(
                row, packet
            ):
                prevalidated_terminal_by_ticket.setdefault(ticket_id, []).append((index, row))
    closing_ticket_ids = set(prevalidated_terminal_by_ticket)
    valid_terminal_by_ticket: dict[
        str, list[tuple[int, dict[str, Any]]]
    ] = {}
    while True:
        valid_terminal_by_ticket = {}
        for ticket_id, rows in prevalidated_terminal_by_ticket.items():
            for index, row in rows:
                if terminal_rework_response_artifacts_valid(row, packet, closing_ticket_ids):
                    valid_terminal_by_ticket.setdefault(
                        ticket_id, []
                    ).append((index, row))
        next_closing_ticket_ids = {
            ticket_id
            for ticket_id, rows in valid_terminal_by_ticket.items()
            if len(rows) == 1
        } & closing_ticket_ids
        if next_closing_ticket_ids == closing_ticket_ids:
            break
        closing_ticket_ids = next_closing_ticket_ids
    current_valid = {
        ticket_id: valid_terminal_by_ticket[ticket_id][0]
        for ticket_id in closing_ticket_ids
    }
    sealed = seal_ticket_closures(
        packet, current_valid, requests, responses
    )
    closed = closing_ticket_ids | sealed
    return [row for row in requests if str(row.get("ticket_id") or "") not in closed]


def sync_packet_statuses(paper_ids: list[str] | None = None) -> None:
    """Reflect current final, locator, and extraction state into mutable manifests."""
    packet_root = BASE / "packets"
    if not packet_root.exists():
        return
    selected = {str(item) for item in paper_ids} if paper_ids else None
    live_material_counts: dict[str, tuple[int, int]] = {}
    for packet in sorted(path for path in packet_root.iterdir() if path.is_dir()):
        paper_id = packet.name
        if selected is not None and paper_id not in selected:
            continue
        manifest_path = packet / "packet_manifest.json"
        analysis_path = packet / "analysis/analysis_status.json"
        extraction_path = packet / "extraction/extraction_status.json"
        review_path = BASE / "papers" / paper_id / "final/review_report.json"
        if not manifest_path.exists():
            continue
        manifest = read_json(manifest_path)
        locator_count = live_locator_count(packet)
        extraction_errors = live_extraction_errors(packet)
        extraction_error_count = len(extraction_errors)
        live_material_counts[paper_id] = (locator_count, extraction_error_count)
        tickets = open_rework_tickets(packet)
        ticket_queues = {
            str(item.get("target_queue") or "")
            for item in tickets
            if isinstance(item, dict)
        }
        analysis_status = "analysis_queued"
        if review_path.exists():
            review = read_json(review_path)
            status = str(review.get("review_status") or "")
            targets = review.get("rework_targets") if isinstance(review.get("rework_targets"), list) else []
            queues = {str(item.get("target_queue") or "") for item in targets if isinstance(item, dict)}
            if status in {"accepted_clean", "accepted_with_cautions"} and review.get("publication_grade") is True:
                analysis_status = "analysis_source_reviewed_accepted"
            elif "material_extraction" in queues:
                analysis_status = "analysis_needs_material_rework"
            elif "analysis" in queues:
                analysis_status = "analysis_needs_analysis_rework"
            elif status == "needs_targeted_rework":
                analysis_status = "analysis_needs_analysis_rework"
            elif status == "blocked_missing_primary_material":
                analysis_status = "analysis_blocked"
            else:
                analysis_status = "analysis_artifacts_present"
        elif any((packet / "final" / rel).exists() for rel in ["review_report.json", "activity_toxicity_evidence.json", "database_record_verification.json"]):
            analysis_status = "analysis_artifacts_present"

        # A newly opened durable ticket invalidates an older accepted queue state
        # until the owner worker repairs and closes that ticket.
        if "material_extraction" in ticket_queues:
            analysis_status = "analysis_needs_material_rework"
        elif tickets:
            analysis_status = "analysis_needs_analysis_rework"

        open_ticket_ids = [row.get("ticket_id") for row in tickets if isinstance(row, dict) and row.get("ticket_id")]
        manifest["analysis_queue_status"] = analysis_status
        manifest["open_rework_ticket_ids"] = open_ticket_ids
        manifest["locator_count"] = locator_count
        manifest["known_missing_or_blocked_materials"] = extraction_errors
        manifest["extraction_error_count"] = extraction_error_count
        manifest["updated_at"] = utc_now()
        write_json(manifest_path, manifest)
        if extraction_path.exists():
            extraction = read_json(extraction_path)
            extraction["error_count"] = extraction_error_count
            extraction["updated_at"] = utc_now()
            write_json(extraction_path, extraction)
        write_json(
            analysis_path,
            {
                "status": analysis_status,
                "generated_at": utc_now(),
                "open_rework_ticket_count": len(open_ticket_ids),
                "open_rework_ticket_ids": open_ticket_ids,
                "source": "dbaasp_strict_pilot sync_packet_statuses",
            },
        )

    rolling_path = BASE / "manifests/dbaasp_strict_pilot_manifest.json"
    if rolling_path.exists():
        with pilot_manifest_lock():
            rolling = read_json(rolling_path)
            rows = (
                rolling.get("papers")
                if isinstance(rolling.get("papers"), list)
                else []
            )
            changed = False
            for row in rows:
                if not isinstance(row, dict):
                    continue
                paper_id = str(row.get("paper_id") or "")
                counts = live_material_counts.get(paper_id)
                if counts is None:
                    continue
                locator_count, extraction_error_count = counts
                if row.get("locator_count") != locator_count:
                    row["locator_count"] = locator_count
                    changed = True
                if row.get("error_count") != extraction_error_count:
                    row["error_count"] = extraction_error_count
                    changed = True
            if changed:
                rolling["updated_at"] = utc_now()
                rolling["count_refresh_source"] = (
                    "dbaasp_strict_pilot sync_packet_statuses"
                )
                write_json(rolling_path, rolling)


def build_scoped_gate_manifest(paper_ids: list[str] | None = None) -> Path:
    manifest = BASE / "manifests/dbaasp_strict_pilot_manifest.json"
    if not paper_ids:
        return manifest
    source = safe_read_json(manifest)
    selected = {str(item) for item in paper_ids}
    papers = [
        item
        for item in source.get("papers", [])
        if isinstance(item, dict) and str(item.get("paper_id")) in selected
    ]
    by_id = {str(item.get("paper_id")): item for item in papers}
    ordered = [by_id[paper_id] for paper_id in paper_ids if paper_id in by_id]
    digest = hashlib.sha256("\n".join(paper_ids).encode("utf-8")).hexdigest()[:12]
    scoped = {
        **source,
        "created_at": utc_now(),
        "scope": "strict scoped gate manifest",
        "paper_ids": list(paper_ids),
        "papers": ordered,
        "source_manifest": str(manifest),
    }
    path = BASE / "manifests" / f"dbaasp_strict_pilot_scoped_{digest}.json"
    write_json(path, scoped)
    return path


def verify(paper_ids: list[str] | None = None) -> dict[str, Any]:
    sync_packet_statuses()
    ids = list(paper_ids) if paper_ids else None
    manifest = build_scoped_gate_manifest(ids)
    suffix = ""
    if ids:
        digest = hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()[:12]
        suffix = f"_scoped_{digest}"
    packet_json = BASE / "reports" / f"check_two_queue_packets{suffix}_latest.json"
    semantic_json = BASE / "reports" / f"semantic_gate{suffix}_latest.json"
    publication_json = BASE / "reports" / f"publication_quality{suffix}_latest.json"
    manifest_sha256_at_start = hashlib.sha256(manifest.read_bytes()).hexdigest()
    reports: dict[str, Any] = {
        "generated_at": utc_now(),
        "paper_ids": ids or manifest_paper_ids(),
        "manifest": str(manifest),
        "manifest_sha256_at_start": manifest_sha256_at_start,
    }

    cmds = {
        "packet_check": [
            sys.executable,
            str(CHECK_PACKET_SCRIPT),
            "--packet-root",
            str(BASE / "packets"),
            "--manifest",
            str(manifest),
            "--json-out",
            str(packet_json),
        ],
        "semantic_gate": [
            sys.executable,
            str(SEMANTIC_GATE),
            "--root",
            str(BASE),
            "--manifest",
            str(manifest),
            "--json",
        ],
        "publication_gate": [
            sys.executable,
            str(PUBLICATION_GATE),
            "--root",
            str(BASE),
            "--manifest",
            str(manifest),
            "--issues",
            str(BASE / "issues/dbaasp_strict_pilot_issues.jsonl"),
            "--json-out",
            str(publication_json),
        ],
    }
    for name, cmd in cmds.items():
        code, stdout, stderr = run_cmd(cmd, timeout=240)
        reports[name] = {"returncode": code, "stdout": stdout[-4000:], "stderr": stderr[-4000:]}
        if name == "semantic_gate":
            semantic_json.parent.mkdir(parents=True, exist_ok=True)
            semantic_json.write_text(stdout, encoding="utf-8")
    worker_gate = strict_worker_run_gate(ids)
    reports["strict_worker_run_gate"] = {
        "returncode": 0 if worker_gate["hard_finding_count"] == 0 else 1,
        "json_path": str(strict_worker_run_gate_path(ids)),
        "hard_finding_count": worker_gate["hard_finding_count"],
        "hard_finding_papers": worker_gate["hard_finding_papers"],
    }
    manifest_sha256_at_finish = hashlib.sha256(manifest.read_bytes()).hexdigest()
    reports["manifest_sha256_at_finish"] = manifest_sha256_at_finish
    reports["manifest_unchanged_during_verify"] = (
        manifest_sha256_at_start == manifest_sha256_at_finish
    )
    verify_path = BASE / "reports" / f"verify{suffix}_latest.json"
    write_json(verify_path, reports)
    reports["json_path"] = str(verify_path)
    return reports


def missing_final_files(packet: Path) -> list[str]:
    required = [
        "final/database_record_verification.json",
        "final/activity_toxicity_evidence.json",
        "final/mechanism_evidence.json",
        "final/review_report.json",
    ]
    return [rel for rel in required if not (packet / rel).exists()]


def safe_read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = read_json(path)
    except Exception as exc:  # noqa: BLE001 - status diagnostic
        return {"_parse_error": str(exc)}
    return data if isinstance(data, dict) else {"_not_object": data}


def first_list_field(data: dict[str, Any], keys: list[str]) -> list[Any]:
    for key in keys:
        value = data.get(key)
        if isinstance(value, list):
            return value
    return []


def first_dict_field(data: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    for key in keys:
        value = data.get(key)
        if isinstance(value, dict):
            return value
    return {}


def enrich_worker_report(report: dict[str, Any], *, sequence_mtime: float | None = None) -> dict[str, Any]:
    """Backfill old run reports whose Codex metadata only exists in stderr."""
    enriched = dict(report)
    stderr_path = enriched.get("stderr_path")
    stderr = ""
    if isinstance(stderr_path, str) and Path(stderr_path).exists():
        stderr_file = Path(stderr_path)
        stderr_mtime = stderr_file.stat().st_mtime
        if sequence_mtime is not None and stderr_mtime > sequence_mtime + 1:
            # A rerun overwrites worker-*.stderr.log before run_sequence_latest.json
            # is rewritten. Do not mix fresh stderr metadata into a stale sequence.
            enriched["metadata_backfill_skipped"] = "stderr_newer_than_run_sequence"
            enriched["stderr_mtime_newer_than_sequence"] = True
            return enriched
        stderr = stderr_file.read_text(encoding="utf-8", errors="replace")
        if not (
            enriched.get("codex_session_id")
            and enriched.get("codex_model")
            and enriched.get("codex_reasoning_effort")
        ):
            for key, value in parse_codex_stderr_metadata(stderr).items():
                if value and not enriched.get(key):
                    enriched[key] = value
        if enriched.get("returncode") not in {None, 0} and not enriched.get("failure_code"):
            for key, value in classify_worker_failure(int(enriched.get("returncode") or 1), stderr).items():
                enriched[key] = value
    return enriched


def worker_reports_for_paper(paper_id: str, sequence_path: Path) -> list[dict[str, Any]]:
    data = safe_read_json(sequence_path)
    reports = data.get("reports") if isinstance(data.get("reports"), list) else []
    sequence_mtime = sequence_path.stat().st_mtime if sequence_path.exists() else None
    report_dir = BASE / "worker_logs" / paper_id
    if not reports:
        reports = []
        for report_path in sorted(report_dir.glob("worker-*.run_report.json")):
            report = safe_read_json(report_path)
            if report:
                reports.append(report)
        sequence_mtime = None
    else:
        sequence_reports = [dict(item) for item in reports if isinstance(item, dict)]
        by_worker = {
            str(item.get("worker")): item
            for item in sequence_reports
            if item.get("worker")
        }
        for alias_path in sorted(report_dir.glob("worker-*.run_report.json")):
            alias = safe_read_json(alias_path)
            worker = str(alias.get("worker") or "")
            sequence_report = by_worker.get(worker)
            if not worker or not sequence_report:
                continue
            alias_finished = parse_run_timestamp(alias.get("finished_at"))
            sequence_finished = parse_run_timestamp(sequence_report.get("finished_at"))
            alias_started = parse_run_timestamp(alias.get("started_at"))
            sequence_started = parse_run_timestamp(sequence_report.get("started_at"))
            alias_is_newer = bool(
                (alias_finished and (not sequence_finished or alias_finished > sequence_finished))
                or (
                    alias_finished == sequence_finished
                    and alias_started
                    and (not sequence_started or alias_started > sequence_started)
                )
            )
            if alias_is_newer:
                sequence_report["worker_report_alias_newer_than_run_sequence"] = True
                sequence_report["newer_alias_path"] = str(alias_path)
                sequence_report["newer_alias_started_at"] = alias.get("started_at")
                sequence_report["newer_alias_finished_at"] = alias.get("finished_at")
                sequence_report["newer_alias_codex_session_id"] = alias.get("codex_session_id")
        reports = sequence_reports
    return [enrich_worker_report(item, sequence_mtime=sequence_mtime) for item in reports if isinstance(item, dict)]


def parse_run_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def adjudication_freshness(reports: list[dict[str, Any]]) -> dict[str, Any]:
    by_worker = {
        str(item.get("worker")): item
        for item in reports
        if isinstance(item, dict) and item.get("worker")
    }
    worker_6 = by_worker.get("worker-6")
    worker_6_started_at = worker_6.get("started_at") if worker_6 else None
    worker_6_started = parse_run_timestamp(worker_6_started_at)
    upstream_finishes: list[tuple[str, str, datetime]] = []
    timestamp_parse_error_workers: list[str] = []
    for worker in WORKER_SKILLS:
        if worker == "worker-6" or worker not in by_worker:
            continue
        raw_finished = by_worker[worker].get("finished_at")
        finished = parse_run_timestamp(raw_finished)
        if finished is None:
            timestamp_parse_error_workers.append(worker)
            continue
        upstream_finishes.append((worker, str(raw_finished), finished))
    if worker_6 is not None and worker_6_started is None:
        timestamp_parse_error_workers.append("worker-6")
    stale_workers = [
        worker
        for worker, _raw, finished in upstream_finishes
        if worker_6_started is not None and finished > worker_6_started
    ]
    latest_upstream = max(upstream_finishes, key=lambda item: item[2]) if upstream_finishes else None
    return {
        "worker_6_after_upstream": bool(
            worker_6_started is not None
            and len(upstream_finishes) == len(WORKER_SKILLS) - 1
            and not timestamp_parse_error_workers
            and not stale_workers
        ),
        "worker_6_started_at": worker_6_started_at,
        "latest_upstream_finished_at": latest_upstream[1] if latest_upstream else None,
        "latest_upstream_worker": latest_upstream[0] if latest_upstream else None,
        "stale_adjudication_workers": stale_workers,
        "timestamp_parse_error_workers": timestamp_parse_error_workers,
    }


def worker_report_is_exact_codex_exec(report: dict[str, Any]) -> bool:
    command = report.get("command")
    return bool(
        isinstance(command, list)
        and len(command) >= 2
        and Path(str(command[0])).name == "codex"
        and command[1] == "exec"
    )


def run_sequence_summary(paper_id: str) -> dict[str, Any]:
    path = BASE / "worker_logs" / paper_id / "run_sequence_latest.json"
    reports = worker_reports_for_paper(paper_id, path)
    session_ids = [item.get("codex_session_id") for item in reports if isinstance(item, dict) and item.get("codex_session_id")]
    failed_workers = [
        {
            "worker": item.get("worker"),
            "returncode": item.get("returncode"),
            "failure_code": item.get("failure_code"),
            "failure_summary": item.get("failure_summary"),
            "stderr_path": item.get("stderr_path"),
        }
        for item in reports
        if isinstance(item, dict) and item.get("returncode") not in {0, None}
    ]
    stale_log_count = sum(1 for item in reports if isinstance(item, dict) and item.get("stderr_mtime_newer_than_sequence"))
    newer_alias_workers = sorted(
        str(item.get("worker"))
        for item in reports
        if isinstance(item, dict) and item.get("worker_report_alias_newer_than_run_sequence")
    )
    workers = [
        item.get("worker")
        for item in reports
        if isinstance(item, dict)
    ]
    return {
        "path": str(path),
        "exists": path.exists(),
        "worker_count": len(reports),
        "workers": workers,
        "canonical_worker_order": workers == list(WORKER_SKILLS),
        "all_exact_codex_exec": bool(reports)
        and all(
            worker_report_is_exact_codex_exec(item)
            for item in reports
            if isinstance(item, dict)
        ),
        "all_returncode_zero": bool(reports) and all(item.get("returncode") == 0 for item in reports if isinstance(item, dict)),
        "all_gpt55_xhigh": bool(reports)
        and all(item.get("codex_model") == "gpt-5.5" and item.get("codex_reasoning_effort") == "xhigh" for item in reports if isinstance(item, dict)),
        "unique_session_count": len(set(session_ids)),
        "session_ids": session_ids,
        "failed_worker_count": len(failed_workers),
        "failed_workers": failed_workers,
        "stale_or_mutated_log_reference_count": stale_log_count + len(newer_alias_workers),
        "worker_report_alias_newer_than_run_sequence_count": len(newer_alias_workers),
        "worker_report_alias_newer_than_run_sequence_workers": newer_alias_workers,
        **adjudication_freshness(reports),
    }


def paper_level_completion_ready(
    *,
    worker_run_clean: bool,
    publication_grade: bool,
    review_status: str,
    rework_targets: list[Any],
    open_rework_tickets: list[dict[str, Any]],
) -> bool:
    return bool(
        worker_run_clean
        and publication_grade
        and review_status in {"accepted_clean", "accepted_with_cautions"}
        and not rework_targets
        and not open_rework_tickets
    )


def paper_status_summary(paper_id: str) -> dict[str, Any]:
    packet = BASE / "packets" / paper_id
    paper_root = BASE / "papers" / paper_id
    manifest = safe_read_json(packet / "packet_manifest.json")
    extraction = safe_read_json(packet / "extraction/extraction_status.json")
    db_manifest = safe_read_json(packet / "database/database_source_manifest.json")
    auth_report = safe_read_json(packet / "database/authoritative_match_report.json")
    review = safe_read_json(paper_root / "final/review_report.json")
    db_final = safe_read_json(paper_root / "final/database_record_verification.json")
    activity = safe_read_json(paper_root / "final/activity_toxicity_evidence.json")
    mechanism = safe_read_json(paper_root / "final/mechanism_ontology_record.json")
    run = run_sequence_summary(paper_id)
    rework_tickets = open_rework_tickets(packet)
    activity_records = activity.get("activity_records") if isinstance(activity.get("activity_records"), list) else []
    mechanism_claims = mechanism.get("mechanism_claims") if isinstance(mechanism.get("mechanism_claims"), list) else []
    record_audits = first_list_field(db_final, ["record_audits", "records", "database_record_audits", "audit_records"])
    database_status_summary = first_dict_field(db_final, ["status_summary", "status_counts", "database_status_summary"])
    linked_counts = {
        key: int((db_manifest.get("row_counts") or {}).get(key) or 0)
        for key in ["linked_article_records", "linked_assay_records", "linked_sequence_records", "linked_literature_records"]
    }
    authoritative_rows_present = any(linked_counts.values()) or bool(db_manifest.get("source_record_links_present"))
    publication_grade = review.get("publication_grade") is True
    review_status = str(review.get("review_status") or "missing_review")
    rework_targets = review.get("rework_targets") if isinstance(review.get("rework_targets"), list) else []
    worker_run_clean = bool(
        run.get("worker_count") == 6
        and run.get("all_returncode_zero")
        and run.get("all_gpt55_xhigh")
        and run.get("canonical_worker_order") is True
        and run.get("all_exact_codex_exec") is True
        and run.get("unique_session_count") == 6
        and int(run.get("failed_worker_count") or 0) == 0
        and int(run.get("stale_or_mutated_log_reference_count") or 0) == 0
        and run.get("worker_6_after_upstream") is True
    )
    paper_level_source_reviewed_complete = paper_level_completion_ready(
        worker_run_clean=worker_run_clean,
        publication_grade=publication_grade,
        review_status=review_status,
        rework_targets=rework_targets,
        open_rework_tickets=rework_tickets,
    )
    authoritative_ingest_ready = bool(
        paper_level_source_reviewed_complete
        and review_status in {"accepted_clean", "accepted_with_cautions"}
        and authoritative_rows_present
        and not rework_targets
    )
    return {
        "paper_id": paper_id,
        "packet_exists": packet.exists(),
        "paper_root": str(paper_root),
        "packet_root": str(packet),
        "material_status": manifest.get("material_queue_status") or extraction.get("status") or "unknown",
        "analysis_status": manifest.get("analysis_queue_status") or "unknown",
        "review_status": review_status,
        "publication_grade": publication_grade,
        "validator_contract_passed": review.get("validator_contract_passed") is True,
        "missing_final_files": missing_final_files(packet),
        "open_rework_ticket_count": len(rework_tickets),
        "rework_target_count": len(rework_targets),
        "caution_count": len(review.get("caution_findings") if isinstance(review.get("caution_findings"), list) else []),
        "locator_count": live_locator_count(packet),
        "extraction_error_count": len(live_extraction_errors(packet)),
        "database_row_counts": db_manifest.get("row_counts") or {},
        "linked_authoritative_row_counts": linked_counts,
        "authoritative_match_checked": bool(auth_report),
        "authoritative_rows_present": authoritative_rows_present,
        "authoritative_dbaasp_ingest_ready": authoritative_ingest_ready,
        "paper_level_source_reviewed_complete": paper_level_source_reviewed_complete,
        "worker_run_clean": worker_run_clean,
        "activity_record_count": len(activity_records),
        "database_record_audit_count": len(record_audits),
        "database_status_summary": database_status_summary,
        "mechanism_claim_count": len(mechanism_claims),
        "worker_run": run,
        "recommended_next_action": recommended_next_action(review_status, publication_grade, authoritative_ingest_ready, rework_targets, packet, run),
    }


def recommended_next_action(
    review_status: str,
    publication_grade: bool,
    authoritative_ingest_ready: bool,
    rework_targets: list[Any],
    packet: Path,
    run: dict[str, Any] | None = None,
) -> str:
    if run and int(run.get("failed_worker_count") or 0):
        return "repair_failed_worker_runs_then_rerun_worker_6_and_acceptance_gates"
    if open_rework_tickets(packet):
        return "repair_runtime_open_rework_tickets_then_rerun_worker_6_and_acceptance_gates"
    if authoritative_ingest_ready:
        return "candidate_authoritative_ingest_after_release_policy_review"
    if publication_grade and review_status in {"accepted_clean", "accepted_with_cautions"}:
        return "preserve_as_source_reviewed_pilot_evidence; do_not_promote_fallback_rows_without_authoritative_links"
    if review_status == "needs_targeted_rework":
        queues = {str(item.get("target_queue") or "") for item in rework_targets if isinstance(item, dict)}
        if "material_extraction" in queues:
            return "repair_material_packet_then_rerun_worker_6"
        return "repair_analysis_outputs_then_rerun_worker_6"
    if review_status == "blocked_missing_primary_material":
        return "mark_blocked_or_recover_primary_material"
    if missing_final_files(packet):
        return "run_worker_1_to_6_or_remove_from_acceptance_manifest"
    return "inspect_packet_state"


def manifest_paper_ids() -> list[str]:
    manifest = BASE / "manifests/dbaasp_strict_pilot_manifest.json"
    if manifest.exists():
        data = safe_read_json(manifest)
        ids = data.get("paper_ids")
        if isinstance(ids, list):
            return [str(item) for item in ids]
    packet_root = BASE / "packets"
    if packet_root.exists():
        return sorted(path.name for path in packet_root.iterdir() if path.is_dir())
    return []


def status_report_path(paper_ids: list[str] | None) -> Path:
    if not paper_ids:
        return BASE / "reports/status_latest.json"
    if len(paper_ids) == 1:
        safe_id = re.sub(r"[^0-9A-Za-z_.-]+", "_", str(paper_ids[0]))
        return BASE / "reports" / f"{safe_id}_status_latest.json"
    return BASE / "reports/status_selected_latest.json"


def build_status_report(paper_ids: list[str] | None = None) -> dict[str, Any]:
    sync_packet_statuses(paper_ids)
    ids = paper_ids or manifest_paper_ids()
    papers = [paper_status_summary(pid) for pid in ids]
    counts = {
        "material_status": dict(Counter(item["material_status"] for item in papers)),
        "analysis_status": dict(Counter(item["analysis_status"] for item in papers)),
        "review_status": dict(Counter(item["review_status"] for item in papers)),
    }
    summary = {
        "generated_at": utc_now(),
        "paper_count": len(papers),
        "counts": counts,
        "source_reviewed_publication_grade_count": sum(1 for item in papers if item["paper_level_source_reviewed_complete"]),
        "authoritative_dbaasp_ingest_ready_count": sum(1 for item in papers if item["authoritative_dbaasp_ingest_ready"]),
        "open_rework_ticket_count": sum(item["open_rework_ticket_count"] for item in papers),
        "missing_final_paper_count": sum(1 for item in papers if item["missing_final_files"]),
        "papers": papers,
    }
    write_json(status_report_path(paper_ids), summary)
    return summary


def strict_worker_run_gate_path(paper_ids: list[str] | None = None) -> Path:
    if not paper_ids:
        return BASE / "reports/strict_worker_run_gate_latest.json"
    digest = hashlib.sha256("\n".join(paper_ids).encode("utf-8")).hexdigest()[:12]
    return BASE / "reports" / f"strict_worker_run_gate_scoped_{digest}_latest.json"


def strict_worker_run_gate(paper_ids: list[str] | None = None) -> dict[str, Any]:
    ids = list(paper_ids) if paper_ids else manifest_paper_ids()
    # Capture contradictions before build_status_report performs mutable count
    # synchronization. The current gate fails once rather than silently
    # normalizing stale state into a false green result.
    findings = [
        finding
        for paper_id in ids
        for finding in strict_artifact_consistency_findings(paper_id)
    ]
    status = build_status_report(paper_ids if paper_ids else None)
    for paper in status["papers"]:
        run = paper.get("worker_run") or {}
        failed_workers = run.get("failed_workers") if isinstance(run.get("failed_workers"), list) else []
        if failed_workers:
            findings.append(
                {
                    "paper_id": paper["paper_id"],
                    "severity": "hard",
                    "code": "worker_run_failed",
                    "review_status": paper["review_status"],
                    "publication_grade": paper["publication_grade"],
                    "failed_workers": failed_workers,
                }
            )
        if paper["review_status"] in {"accepted_clean", "accepted_with_cautions"} and not paper.get("worker_run_clean"):
            findings.append(
                {
                    "paper_id": paper["paper_id"],
                    "severity": "hard",
                    "code": "accepted_review_without_clean_worker_run",
                    "review_status": paper["review_status"],
                    "publication_grade": paper["publication_grade"],
                    "worker_run": run,
                }
            )
    report = {
        "generated_at": utc_now(),
        "paper_count": status["paper_count"],
        "paper_level_source_reviewed_complete_count": status["source_reviewed_publication_grade_count"],
        "authoritative_dbaasp_ingest_ready_count": status["authoritative_dbaasp_ingest_ready_count"],
        "hard_finding_count": len(findings),
        "hard_finding_papers": sorted({item["paper_id"] for item in findings}),
        "findings": findings,
    }
    write_json(strict_worker_run_gate_path(paper_ids), report)
    return report


def worker_role_label(worker: str) -> str:
    labels = {
        "worker-1": "intake_linkage",
        "worker-2": "body_table_activity_toxicity",
        "worker-3": "supplementary_evidence",
        "worker-4": "database_record_audit",
        "worker-5": "mechanism_ontology",
        "worker-6": "adjudicator_review",
    }
    return labels.get(worker, "unknown_worker")


def worker_report_rows_for_paper(paper_id: str) -> list[dict[str, Any]]:
    report_dir = BASE / "worker_logs" / paper_id
    sequence_path = report_dir / "run_sequence_latest.json"
    rows: list[dict[str, Any]] = []
    for report in worker_reports_for_paper(paper_id, sequence_path):
        if not isinstance(report, dict):
            continue
        rows.append(
            {
                "paper_id": paper_id,
                "worker": report.get("worker"),
                "role": worker_role_label(str(report.get("worker") or "")),
                "returncode": report.get("returncode"),
                "codex_model": report.get("codex_model"),
                "codex_reasoning_effort": report.get("codex_reasoning_effort"),
                "codex_session_id": report.get("codex_session_id"),
                "codex_exec_command": worker_report_is_exact_codex_exec(
                    report
                ),
                "started_at": report.get("started_at"),
                "finished_at": report.get("finished_at"),
                "prompt_path": report.get("prompt_path"),
                "final_message_path": report.get("final_message_path"),
                "stdout_path": report.get("stdout_path"),
                "stderr_path": report.get("stderr_path"),
                "metadata_backfill_skipped": report.get("metadata_backfill_skipped"),
                "stderr_mtime_newer_than_sequence": report.get("stderr_mtime_newer_than_sequence"),
                "worker_report_alias_newer_than_run_sequence": report.get(
                    "worker_report_alias_newer_than_run_sequence"
                ),
                "newer_alias_path": report.get("newer_alias_path"),
                "newer_alias_started_at": report.get("newer_alias_started_at"),
                "newer_alias_finished_at": report.get("newer_alias_finished_at"),
                "newer_alias_codex_session_id": report.get("newer_alias_codex_session_id"),
                "failure_code": report.get("failure_code"),
                "failure_summary": report.get("failure_summary"),
            }
        )
    return rows


def verify_gate_findings(verify_report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(verify_report, dict):
        return []
    findings: list[dict[str, Any]] = []
    for gate in ("packet_check", "semantic_gate", "publication_gate", "strict_worker_run_gate"):
        result = verify_report.get(gate)
        if not isinstance(result, dict) or result.get("returncode") != 0:
            findings.append(
                {
                    "severity": "hard",
                    "code": f"{gate}_failed",
                    "returncode": result.get("returncode") if isinstance(result, dict) else None,
                }
            )
    if verify_report.get("manifest_unchanged_during_verify") is False:
        findings.append(
            {
                "severity": "hard",
                "code": "manifest_changed_during_verify",
                "manifest_sha256_at_start": verify_report.get("manifest_sha256_at_start"),
                "manifest_sha256_at_finish": verify_report.get("manifest_sha256_at_finish"),
            }
        )
    return findings


def build_worker_independence_audit(
    paper_ids: list[str] | None = None, *, run_gates: bool = True, allow_incomplete: bool = False
) -> dict[str, Any]:
    ids = paper_ids or manifest_paper_ids()
    status = build_status_report(ids)
    verify_report = verify(ids if paper_ids is not None else None) if run_gates else None
    strict_gate = (
        (verify_report or {}).get("strict_worker_run_gate")
        if isinstance(verify_report, dict)
        else strict_worker_run_gate(ids)
    )
    status_by_id = {str(item.get("paper_id")): item for item in status.get("papers", []) if isinstance(item, dict)}
    per_paper: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = verify_gate_findings(verify_report)

    for paper_id in ids:
        rows = worker_report_rows_for_paper(paper_id)
        all_rows.extend(rows)
        workers = [str(row.get("worker") or "") for row in rows]
        sessions = [str(row.get("codex_session_id")) for row in rows if row.get("codex_session_id")]
        missing_workers = [worker for worker in WORKER_SKILLS if worker not in workers]
        duplicate_sessions = sorted(sid for sid, count in Counter(sessions).items() if count > 1)
        freshness = adjudication_freshness(rows)
        status_item = status_by_id.get(paper_id, {})
        paper = {
            "paper_id": paper_id,
            "worker_report_count": len(rows),
            "expected_worker_count": len(WORKER_SKILLS),
            "workers": rows,
            "missing_workers": missing_workers,
            "unique_session_count": len(set(sessions)),
            "duplicate_session_ids": duplicate_sessions,
            "all_returncode_zero": bool(rows) and all(row.get("returncode") == 0 for row in rows),
            "all_gpt55_xhigh": bool(rows)
            and all(row.get("codex_model") == "gpt-5.5" and row.get("codex_reasoning_effort") == "xhigh" for row in rows),
            "all_codex_exec": bool(rows) and all(row.get("codex_exec_command") for row in rows),
            **freshness,
            "review_status": status_item.get("review_status"),
            "publication_grade": status_item.get("publication_grade"),
            "validator_contract_passed": status_item.get("validator_contract_passed"),
            "worker_run_clean": status_item.get("worker_run_clean"),
            "paper_level_source_reviewed_complete": status_item.get("paper_level_source_reviewed_complete"),
            "authoritative_dbaasp_ingest_ready": status_item.get("authoritative_dbaasp_ingest_ready"),
            "open_rework_ticket_count": status_item.get("open_rework_ticket_count"),
            "rework_target_count": status_item.get("rework_target_count"),
            "caution_count": status_item.get("caution_count"),
            "activity_record_count": status_item.get("activity_record_count"),
            "database_record_audit_count": status_item.get("database_record_audit_count"),
            "mechanism_claim_count": status_item.get("mechanism_claim_count"),
            "recommended_next_action": status_item.get("recommended_next_action"),
        }
        per_paper.append(paper)

        if len(rows) != len(WORKER_SKILLS):
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "worker_report_count_not_six",
                    "worker_report_count": len(rows),
                    "missing_workers": missing_workers,
                }
            )
        if duplicate_sessions:
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "duplicate_codex_session_within_paper",
                    "duplicate_session_ids": duplicate_sessions,
                }
            )
        if rows and not paper["all_returncode_zero"]:
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "nonzero_worker_returncode",
                    "workers": [
                        {"worker": row.get("worker"), "returncode": row.get("returncode"), "failure_code": row.get("failure_code")}
                        for row in rows
                        if row.get("returncode") != 0
                    ],
                }
            )
        if rows and not paper["all_gpt55_xhigh"]:
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "model_or_reasoning_effort_mismatch",
                    "workers": [
                        {
                            "worker": row.get("worker"),
                            "codex_model": row.get("codex_model"),
                            "codex_reasoning_effort": row.get("codex_reasoning_effort"),
                        }
                        for row in rows
                        if row.get("codex_model") != "gpt-5.5" or row.get("codex_reasoning_effort") != "xhigh"
                    ],
                }
            )
        if rows and not paper["all_codex_exec"]:
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "worker_not_launched_by_codex_exec",
                    "workers": [row.get("worker") for row in rows if not row.get("codex_exec_command")],
                }
            )
        if rows and not freshness["worker_6_after_upstream"]:
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "worker_6_stale_relative_to_upstream",
                    "worker_6_started_at": freshness["worker_6_started_at"],
                    "latest_upstream_worker": freshness["latest_upstream_worker"],
                    "latest_upstream_finished_at": freshness["latest_upstream_finished_at"],
                    "stale_adjudication_workers": freshness["stale_adjudication_workers"],
                    "timestamp_parse_error_workers": freshness["timestamp_parse_error_workers"],
                }
            )
        newer_alias_rows = [
            row for row in rows if row.get("worker_report_alias_newer_than_run_sequence")
        ]
        if newer_alias_rows:
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "worker_report_alias_newer_than_run_sequence",
                    "workers": [
                        {
                            "worker": row.get("worker"),
                            "sequence_started_at": row.get("started_at"),
                            "sequence_finished_at": row.get("finished_at"),
                            "newer_alias_path": row.get("newer_alias_path"),
                            "newer_alias_started_at": row.get("newer_alias_started_at"),
                            "newer_alias_finished_at": row.get("newer_alias_finished_at"),
                            "newer_alias_codex_session_id": row.get("newer_alias_codex_session_id"),
                        }
                        for row in newer_alias_rows
                    ],
                }
            )
        if not allow_incomplete and not paper["paper_level_source_reviewed_complete"]:
            findings.append(
                {
                    "paper_id": paper_id,
                    "severity": "hard",
                    "code": "paper_not_source_reviewed_complete",
                    "review_status": paper["review_status"],
                    "worker_run_clean": paper["worker_run_clean"],
                }
            )

    all_sessions = [str(row.get("codex_session_id")) for row in all_rows if row.get("codex_session_id")]
    duplicate_global_sessions = sorted(sid for sid, count in Counter(all_sessions).items() if count > 1)
    if duplicate_global_sessions:
        findings.append(
            {
                "severity": "hard",
                "code": "duplicate_codex_session_across_papers",
                "duplicate_session_ids": duplicate_global_sessions,
            }
        )

    cst = cst_now()
    audit = {
        "generated_at": utc_now(),
        "generated_at_cst": cst.isoformat(),
        "scope": "strict Codex CLI worker independence and paper-level source-review audit",
        "paper_ids": ids,
        "manifest_paper_count": len(ids),
        "strict_completed_count": sum(1 for item in per_paper if item.get("paper_level_source_reviewed_complete")),
        "authoritative_dbaasp_ingest_ready_count": status.get("authoritative_dbaasp_ingest_ready_count"),
        "open_rework_ticket_count": status.get("open_rework_ticket_count"),
        "missing_final_paper_count": status.get("missing_final_paper_count"),
        "total_worker_reports_found": len(all_rows),
        "unique_codex_sessions_found": len(set(all_sessions)),
        "duplicate_session_ids": duplicate_global_sessions,
        "nonzero_worker_report_count": sum(1 for row in all_rows if row.get("returncode") != 0),
        "bad_model_effort_report_count": sum(
            1 for row in all_rows if row.get("codex_model") != "gpt-5.5" or row.get("codex_reasoning_effort") != "xhigh"
        ),
        "non_codex_exec_report_count": sum(1 for row in all_rows if not row.get("codex_exec_command")),
        "worker_independence_pass": not findings,
        "hard_finding_count": len(findings),
        "findings": findings,
        "status_report": status,
        "verify_report": verify_report,
        "strict_worker_run_gate": strict_gate,
        "per_paper": per_paper,
        "runtime_boundary": "sequential independent codex exec bridge; not full durable OMX team mailbox production state",
        "strict_boundary": "paper-level source-reviewed complete does not imply authoritative DBAASP release ingest",
    }
    stamp = cst.strftime("%Y%m%d_%H%M%S")
    json_path = BASE / "reports" / f"strict_codex_cli_independence_recheck_{stamp}.json"
    md_path = BASE / "reports" / f"strict_codex_cli_independence_recheck_{stamp}.md"
    audit["json_path"] = str(json_path)
    audit["markdown_path"] = str(md_path)
    write_json(json_path, audit)
    write_json(BASE / "reports/strict_codex_cli_independence_recheck_latest.json", audit)
    markdown = render_worker_independence_audit_markdown(audit)
    md_path.write_text(markdown, encoding="utf-8")
    (BASE / "reports/strict_codex_cli_independence_recheck_latest.md").write_text(markdown, encoding="utf-8")
    return audit


def render_worker_independence_audit_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Strict Codex CLI Independence Recheck",
        "",
        f"Timestamp: {audit.get('generated_at_cst')} CST.",
        "",
        "## Short Answer",
        "",
    ]
    if audit.get("worker_independence_pass"):
        lines.extend(
            [
                f"- Yes for all {audit.get('manifest_paper_count')} audited paper(s): every paper has six independent Codex CLI worker reports.",
                "- All worker reports use `gpt-5.5/xhigh`, return code 0, and `codex exec` command provenance.",
            ]
        )
    else:
        lines.extend(
            [
                "- No: at least one audited paper does not currently satisfy the strict worker-independence/source-review gate.",
                f"- Hard findings: {audit.get('hard_finding_count')}.",
            ]
        )
    lines.extend(
        [
            f"- Paper-level source-reviewed complete: {audit.get('strict_completed_count')}/{audit.get('manifest_paper_count')}.",
            f"- Authoritative DBAASP ingest-ready: {audit.get('authoritative_dbaasp_ingest_ready_count')}.",
            "- Runtime boundary: sequential independent `codex exec` bridge, not full durable `omx team` mailbox production state.",
            "",
            "## Current Counts",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Manifest papers | {audit.get('manifest_paper_count')} |",
            f"| Paper-level source-reviewed complete | {audit.get('strict_completed_count')} |",
            f"| Authoritative DBAASP ingest-ready | {audit.get('authoritative_dbaasp_ingest_ready_count')} |",
            f"| Open rework tickets | {audit.get('open_rework_ticket_count')} |",
            f"| Missing-final paper count | {audit.get('missing_final_paper_count')} |",
            f"| Worker reports found | {audit.get('total_worker_reports_found')} |",
            f"| Unique Codex session IDs found | {audit.get('unique_codex_sessions_found')} |",
            f"| Duplicate Codex session IDs | {len(audit.get('duplicate_session_ids') or [])} |",
            f"| Nonzero worker reports | {audit.get('nonzero_worker_report_count')} |",
            f"| Wrong model/effort reports | {audit.get('bad_model_effort_report_count')} |",
            f"| Non-`codex exec` reports | {audit.get('non_codex_exec_report_count')} |",
            f"| Hard findings | {audit.get('hard_finding_count')} |",
            "",
            "## Per-Paper Proof",
            "",
            "| Paper | Workers | Unique sessions | Model/effort | Return codes | Review | Activity | DB audits | Mechanism | Cautions | Auth ingest |",
            "| --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for paper in audit.get("per_paper") or []:
        model = "all gpt-5.5/xhigh" if paper.get("all_gpt55_xhigh") else "problem"
        returns = "all 0" if paper.get("all_returncode_zero") else "problem"
        lines.append(
            "| `{paper_id}` | {workers} | {sessions} | {model} | {returns} | `{review}` | {activity} | {db} | {mechanism} | {cautions} | {auth} |".format(
                paper_id=paper.get("paper_id"),
                workers=paper.get("worker_report_count"),
                sessions=paper.get("unique_session_count"),
                model=model,
                returns=returns,
                review=paper.get("review_status"),
                activity=paper.get("activity_record_count"),
                db=paper.get("database_record_audit_count"),
                mechanism=paper.get("mechanism_claim_count"),
                cautions=paper.get("caution_count"),
                auth=paper.get("authoritative_dbaasp_ingest_ready"),
            )
        )
    if audit.get("findings"):
        lines.extend(["", "## Findings", ""])
        for finding in audit["findings"]:
            lines.append(f"- `{finding.get('code')}`: {json.dumps(finding, ensure_ascii=False)}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This proves worker-session independence and paper-level source-reviewed completion only when the pass flag is true.",
            "- It does not make candidate DBAASP machine rows authoritative release/portal ingest rows.",
            "- Full production queue semantics still require durable OMX team/mailbox orchestration.",
        ]
    )
    return "\n".join(lines) + "\n"


def declared_supplement_names(xml_path: Path) -> list[str]:
    return [str(ref["name"]) for ref in declared_supplement_refs(xml_path)]


def suppdata_metadata_by_name(xml_path: Path) -> dict[str, dict[str, Any]]:
    """Recover PMC processing-instruction metadata that ElementTree discards."""
    if not xml_path.exists():
        return {}
    text = xml_path.read_text(encoding="utf-8", errors="replace")
    by_name: dict[str, dict[str, Any]] = {}
    for match in re.finditer(r"<media\b(?P<attrs>[^>]*)>(?P<body>.*?)</media>", text, flags=re.I | re.S):
        attrs = match.group("attrs")
        body = match.group("body")
        href_match = re.search(r"(?:xlink:)?href=[\"']([^\"']+)[\"']", attrs, flags=re.I)
        pi_pairs = {
            key.lower().replace("-", "_"): value.strip()
            for key, value in re.findall(r"<\?suppdata-([A-Za-z0-9_-]+)\s+([^?]+?)\?>", body)
        }
        name = pi_pairs.get("name") or (Path(href_match.group(1)).name if href_match else "")
        if not name:
            continue
        record = by_name.setdefault(name, {"name": name})
        if href_match:
            record.setdefault("href", href_match.group(1))
        for key, value in pi_pairs.items():
            record[f"suppdata_{key}"] = value
    return by_name


def merge_supplement_ref(refs_by_name: dict[str, dict[str, Any]], ref: dict[str, Any]) -> None:
    name = str(ref.get("name") or "")
    if not name:
        return
    key = name.lower()
    existing = refs_by_name.setdefault(
        key,
        {"name": name, "href": "", "text": "", "tag": "", "hrefs": [], "texts": [], "tags": []},
    )
    href = str(ref.get("href") or "")
    text = str(ref.get("text") or "")
    tag = str(ref.get("tag") or "")
    if href and href not in existing["hrefs"]:
        existing["hrefs"].append(href)
    if text and text not in existing["texts"]:
        existing["texts"].append(text)
    if tag and tag not in existing["tags"]:
        existing["tags"].append(tag)
    if href and (not existing.get("href") or href.startswith(("http://", "https://"))):
        existing["href"] = href
    if text and not existing.get("text"):
        existing["text"] = text
    if tag and not existing.get("tag"):
        existing["tag"] = tag
    for meta_key, value in ref.items():
        if meta_key.startswith("suppdata_") and value:
            existing[meta_key] = value


def declared_supplement_refs(xml_path: Path) -> list[dict[str, Any]]:
    if not xml_path.exists():
        return []
    try:
        root = ET.parse(xml_path).getroot()
    except Exception:
        return []
    refs_by_name: dict[str, dict[str, Any]] = {}
    for elem in root.iter():
        tag = local_name(elem.tag)
        if tag not in {"supplementary-material", "media", "ext-link"}:
            continue
        href = ""
        for key, value in elem.attrib.items():
            if key.endswith("href") or "href" in key:
                href = value
                break
        text = text_of(elem)[:500]
        ref = {"tag": tag, "href": href, "text": text}
        if not looks_like_supplement_reference(ref):
            continue
        name = Path(href).name if href else ""
        if not name:
            match = re.search(r"([A-Za-z0-9_.-]+\.(?:pdf|docx?|xlsx?|zip|csv|tsv))", text, re.I)
            name = match.group(1) if match else ""
        if not name:
            continue
        merge_supplement_ref(refs_by_name, {"name": name, "href": href, "text": text, "tag": tag})
    for name, meta in suppdata_metadata_by_name(xml_path).items():
        merge_supplement_ref(refs_by_name, meta)
    return list(refs_by_name.values())


def validate_material_file(path: Path, expected_name: str) -> tuple[bool, str]:
    if not path.exists() or path.stat().st_size == 0:
        return False, "missing_or_empty"
    head = path.read_bytes()[:16]
    suffix = Path(expected_name).suffix.lower()
    if suffix == ".pdf":
        return (head.startswith(b"%PDF"), "pdf_magic_ok" if head.startswith(b"%PDF") else "not_pdf_magic")
    if suffix in {".zip", ".docx", ".xlsx"}:
        return (head.startswith(b"PK"), "zip_magic_ok" if head.startswith(b"PK") else "not_zip_magic")
    return True, "non_magic_checked"


def supplement_url_candidates(paper_id: str, metadata: dict[str, Any], ref: dict[str, Any], ref_index: int) -> list[str]:
    name = str(ref.get("name") or "")
    href = str(ref.get("href") or "")
    text = str(ref.get("text") or "")
    doi = normalize_doi(metadata.get("doi"))
    pmcaid = normalize_identifier(metadata.get("pmcaid") or metadata.get("pmcaiid") or "").removeprefix("PMC")
    pmcid = normalize_pmcid(metadata.get("pmcid") or paper_id)
    urls: list[str] = []
    if href.startswith("http://") or href.startswith("https://"):
        urls.append(href)
    if doi.startswith("10.2478/"):
        urls.append(f"https://reference-global.com/download/supplement/article/{doi}/{ref_index}")
    peerj_match = re.search(r"10\.7717/peerj\.(\d+)/supp-(\d+)", f"{href} {text}", re.I)
    if peerj_match:
        article, supp = peerj_match.groups()
        urls.extend(
            [
                f"https://peerj.com/articles/{article}/supp-{supp}/",
                f"https://peerj.com/articles/{article}/supp-{supp}.pdf",
                f"https://peerj.com/articles/{article}/supp-{supp}.xlsx",
            ]
        )
    if pmcaid and name:
        urls.append(f"https://pmc.ncbi.nlm.nih.gov/articles/instance/{pmcaid}/bin/{name}")
    if pmcid and name:
        urls.append(f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/bin/{name}")
    out: list[str] = []
    for url in urls:
        clean = url.strip().rstrip("\\")
        if clean and clean not in out:
            out.append(clean)
    return out


def solve_cloudpmc_pow_cookie(html_path: Path) -> str | None:
    if not html_path.exists():
        return None
    html = html_path.read_text(encoding="utf-8", errors="replace")
    if "cloudpmc-viewer-pow" not in html or "POW_CHALLENGE" not in html:
        return None
    challenge = re.search(r'POW_CHALLENGE\s*=\s*"([^"]+)"', html)
    difficulty = re.search(r'POW_DIFFICULTY\s*=\s*"([^"]+)"', html)
    cookie_name = re.search(r'POW_COOKIE_NAME\s*=\s*"([^"]+)"', html)
    if not (challenge and difficulty and cookie_name):
        return None
    zeros = "0" * int(difficulty.group(1))
    nonce = 0
    while True:
        digest = hashlib.sha256((challenge.group(1) + str(nonce)).encode("utf-8")).hexdigest()
        if digest.startswith(zeros):
            return f"{cookie_name.group(1)}={challenge.group(1)},{nonce}"
        nonce += 1


def curl_download(url: str, out_path: Path, timeout: int = 80, cookie: str | None = None) -> dict[str, Any]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".part")
    if tmp.exists():
        tmp.unlink()
    cmd = [
        "curl",
        "-L",
        "--max-time",
        str(timeout),
        "--retry",
        "1",
        "--user-agent",
        "Mozilla/5.0",
        "-o",
        str(tmp),
        "-w",
        "http_code=%{http_code}\\ncontent_type=%{content_type}\\nsize_download=%{size_download}\\nurl_effective=%{url_effective}\\n",
        url,
    ]
    if cookie:
        cmd[-1:-1] = ["-b", cookie]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 20, check=False)
    metadata = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            metadata[key] = value
    return {
        "url": url,
        "returncode": proc.returncode,
        "stdout_metadata": metadata,
        "stderr_tail": proc.stderr[-1000:],
        "tmp_path": str(tmp),
        "output_path": str(out_path),
        "downloaded_bytes": tmp.stat().st_size if tmp.exists() else 0,
        "used_cookie": bool(cookie),
    }


def recover_from_pmc_oa_package(
    pmcid: str, names: list[str], scratch: Path
) -> tuple[dict[str, Path], list[dict[str, Any]]]:
    recovered: dict[str, Path] = {}
    attempts: list[dict[str, Any]] = []
    if not pmcid or not names:
        return recovered, attempts
    oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}"
    metadata_target = scratch / "pmc_oa_package.xml"
    result = curl_download(oa_url, metadata_target, timeout=80)
    metadata_path = Path(str(result.get("tmp_path") or metadata_target))
    attempts.append({"attempt_type": "pmc_oa_metadata", **result})
    try:
        root = ET.parse(metadata_path).getroot()
        tgz_url = next(
            (
                str(element.attrib.get("href") or "")
                for element in root.iter()
                if local_name(element.tag) == "link"
                and str(element.attrib.get("format") or "").lower() == "tgz"
            ),
            "",
        )
    except Exception as error:  # noqa: BLE001 - recovery evidence
        attempts[-1]["parse_error"] = f"{type(error).__name__}: {error}"[:1000]
        return recovered, attempts
    if tgz_url.startswith("ftp://"):
        tgz_url = "https://" + tgz_url.removeprefix("ftp://")
    if not tgz_url:
        attempts[-1]["oa_package_available"] = False
        return recovered, attempts
    attempts[-1]["oa_package_available"] = True
    attempts[-1]["oa_package_url"] = tgz_url

    archive_target = scratch / "pmc_oa_package.tar.gz"
    archive_result = curl_download(tgz_url, archive_target, timeout=240)
    archive_path = Path(str(archive_result.get("tmp_path") or archive_target))
    archive_attempt = {
        "attempt_type": "pmc_oa_package",
        **archive_result,
        "requested_names": names,
    }
    attempts.append(archive_attempt)
    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            members_by_name: dict[str, list[tarfile.TarInfo]] = {}
            for member in archive.getmembers():
                if member.isfile():
                    members_by_name.setdefault(Path(member.name).name.lower(), []).append(
                        member
                    )
            for name in names:
                members = members_by_name.get(name.lower()) or []
                if len(members) != 1:
                    continue
                source = archive.extractfile(members[0])
                if source is None:
                    continue
                destination = scratch / "oa_package_files" / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read())
                ok, reason = validate_material_file(destination, name)
                attempts.append(
                    {
                        "name": name,
                        "attempt_type": "pmc_oa_package_member",
                        "archive_member": members[0].name,
                        "validation_ok": ok,
                        "validation_reason": reason,
                        "downloaded_bytes": destination.stat().st_size,
                    }
                )
                if ok:
                    recovered[name] = destination
    except Exception as error:  # noqa: BLE001 - recovery evidence
        archive_attempt["archive_error"] = f"{type(error).__name__}: {error}"[:1000]
    return recovered, attempts


def recover_materials_for_paper(paper_id: str, apply: bool = False) -> dict[str, Any]:
    work = worklist_map()
    if paper_id not in work:
        raise SystemExit(f"{paper_id} not found in {WORKLIST}")
    source_xml, _kind = work[paper_id]
    source_dir = source_xml.parent
    supp_dir = source_dir / "supplementary"
    metadata = parse_xml_metadata(source_xml)
    refs = declared_supplement_refs(source_xml)
    existing = {path.name: path for path in supp_dir.rglob("*") if path.is_file()} if supp_dir.exists() else {}
    attempts: list[dict[str, Any]] = []
    recovered: list[dict[str, Any]] = []
    still_missing: list[str] = []
    scratch = BASE / "material_recovery" / paper_id
    scratch.mkdir(parents=True, exist_ok=True)
    for index, ref in enumerate(refs):
        name = str(ref["name"])
        if name in existing:
            recovered.append({"name": name, "status": "already_present", "path": str(existing[name])})
            continue
        success = None
        for url in supplement_url_candidates(paper_id, metadata, ref, index):
            candidate = scratch / name
            result = curl_download(url, candidate)
            downloaded_path = Path(str(result.get("tmp_path") or candidate))
            ok, reason = validate_material_file(downloaded_path, name)
            result["validation_ok"] = ok
            result["validation_reason"] = reason
            attempts.append({"name": name, "attempt_type": "direct", **result})
            if not ok:
                pow_cookie = solve_cloudpmc_pow_cookie(downloaded_path)
                if pow_cookie:
                    retry = curl_download(url, candidate, cookie=pow_cookie)
                    retry_path = Path(str(retry.get("tmp_path") or candidate))
                    ok, reason = validate_material_file(retry_path, name)
                    retry["validation_ok"] = ok
                    retry["validation_reason"] = reason
                    retry["pow_cookie_solved"] = True
                    attempts.append({"name": name, "attempt_type": "cloudpmc_pow_retry", **retry})
                    downloaded_path = retry_path
            if ok:
                if candidate.exists():
                    candidate.unlink()
                downloaded_path.replace(candidate)
                if apply:
                    dest = supp_dir / name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(candidate, dest)
                    success = {"name": name, "status": "recovered", "path": str(dest), "url": url, "bytes": dest.stat().st_size}
                else:
                    success = {"name": name, "status": "downloadable", "path": str(candidate), "url": url, "bytes": candidate.stat().st_size}
                break
        if success:
            recovered.append(success)
        else:
            still_missing.append(name)
    pmcid = normalize_pmcid(metadata.get("pmcid") or paper_id)
    package_recovered, package_attempts = recover_from_pmc_oa_package(
        pmcid, still_missing, scratch
    )
    attempts.extend(package_attempts)
    if package_recovered:
        unresolved: list[str] = []
        for name in still_missing:
            source = package_recovered.get(name)
            if source is None:
                unresolved.append(name)
                continue
            if apply:
                dest = supp_dir / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                recovered.append(
                    {
                        "name": name,
                        "status": "recovered",
                        "path": str(dest),
                        "url": "PMC OA package",
                        "bytes": dest.stat().st_size,
                    }
                )
            else:
                recovered.append(
                    {
                        "name": name,
                        "status": "downloadable",
                        "path": str(source),
                        "url": "PMC OA package",
                        "bytes": source.stat().st_size,
                    }
                )
        still_missing = unresolved
    report = {
        "generated_at": utc_now(),
        "paper_id": paper_id,
        "apply": apply,
        "source_dir": str(source_dir),
        "supplementary_dir": str(supp_dir),
        "declared_supplement_count": len(refs),
        "recovered_count": sum(1 for item in recovered if item["status"] in {"recovered", "downloadable", "already_present"}),
        "still_missing_count": len(still_missing),
        "recovered": recovered,
        "still_missing": still_missing,
        "attempts": attempts,
    }
    write_json(BASE / "reports" / f"{paper_id}_material_recovery_latest.json", report)
    return report


def candidate_material_probe(
    paper_id: str,
    work: dict[str, tuple[Path, str]],
    row_counts: Counter[str],
    x2_counts: Counter[str],
    verdict_counts: dict[str, Counter[str]],
) -> dict[str, Any]:
    source_path, kind = work[paper_id]
    source_dir = source_path.parent
    if kind == "xml":
        source_xml = source_path
        source_pdf = source_dir / "paper.pdf"
    elif kind == "pdf":
        source_pdf = source_path
        source_xml = source_path.with_suffix(".xml")
    else:
        source_xml = source_dir / "paper.xml"
        source_pdf = source_dir / "paper.pdf"
    metadata = parse_xml_metadata(source_xml)
    if kind == "pdf" and paper_id.lower().startswith("10."):
        metadata.setdefault("doi", paper_id)
    supp_dir = source_dir / "supplementary"
    staged_supp = sorted(path.name for path in supp_dir.rglob("*") if path.is_file()) if supp_dir.exists() else []
    declared_supp = declared_supplement_names(source_xml)
    missing_supp = [name for name in declared_supp if name not in staged_supp]
    xml_exists = source_xml.exists()
    pdf_exists = source_pdf.exists()
    machine_rows = int(row_counts[paper_id])
    x2_rows = int(x2_counts[paper_id])
    already_has_review = (BASE / "papers" / paper_id / "final/review_report.json").exists()
    score = 0
    score += 30 if xml_exists else -50
    score += 30 if pdf_exists else -50
    score += 20 if not missing_supp else -10 * len(missing_supp)
    score += min(machine_rows, 20)
    score += min(x2_rows * 2, 20)
    if machine_rows == 0:
        score -= 10
    if already_has_review:
        score -= 20
    recommended = bool(xml_exists and pdf_exists and not missing_supp and machine_rows > 0 and not already_has_review)
    return {
        "paper_id": paper_id,
        "score": score,
        "doi": metadata.get("doi"),
        "pmid": metadata.get("pmid"),
        "title": metadata.get("title"),
        "source_dir": str(source_dir),
        "source_file": str(source_path),
        "source_kind": kind,
        "xml_exists": xml_exists,
        "pdf_exists": pdf_exists,
        "declared_supplement_count": len(declared_supp),
        "staged_supplement_count": len(staged_supp),
        "missing_declared_supplements": missing_supp,
        "machine_row_count": machine_rows,
        "x2_row_count": x2_rows,
        "verdict_counts": dict(verdict_counts.get(paper_id) or {}),
        "already_has_review": already_has_review,
        "recommended": recommended,
        "needs_structured_fulltext_recovery": bool(
            pdf_exists and not xml_exists and not already_has_review
        ),
        "needs_material_recovery_before_strict_run": bool(
            (missing_supp or not xml_exists or not pdf_exists)
            and machine_rows > 0
            and not already_has_review
        ),
        "next_command": f"python3 {Path(__file__).relative_to(ROOT)} build --paper-id {paper_id} --raw-mode copy --append-manifest && python3 {Path(__file__).relative_to(ROOT)} run --paper-id {paper_id} --workers worker-1,worker-2,worker-3,worker-4,worker-5,worker-6 --timeout 1800 --keep-going",
    }


def build_candidate_report(limit: int, source: str = "all") -> dict[str, Any]:
    source_rows = BATCH_ROWS if source == "codex-batch" else DBAASP_EXTRACTED
    rows = read_tsv(source_rows)
    row_counts = Counter(row.get("paper_id") for row in rows if row.get("paper_id"))
    x2_counts = Counter(
        row.get("paper_id")
        for row in rows
        if row.get("paper_id") and str(row.get("verdict") or "").endswith("_x2")
    )
    verdict_counts: dict[str, Counter[str]] = {}
    for row in rows:
        paper_id = row.get("paper_id")
        if not paper_id:
            continue
        verdict_counts.setdefault(paper_id, Counter())[row.get("verdict") or ""] += 1
    if source == "codex-batch":
        session_counts = Counter(row.get("paper_id") for row in read_tsv(SESSION_AUDIT) if row.get("paper_id"))
        ids = sorted(set(row_counts) | set(session_counts))
    else:
        ids = sorted(row_counts)
    work = worklist_map()
    candidates = [candidate_material_probe(pid, work, row_counts, x2_counts, verdict_counts) for pid in ids if pid in work]
    candidates.sort(key=lambda item: (item["recommended"], item["score"], item["machine_row_count"]), reverse=True)
    report = {
        "generated_at": utc_now(),
        "candidate_source": source,
        "source_rows": str(source_rows),
        "source_session_audit": str(SESSION_AUDIT) if source == "codex-batch" else None,
        "candidate_count": len(candidates),
        "recommended_count": sum(1 for item in candidates if item["recommended"]),
        "already_reviewed_count": sum(1 for item in candidates if item["already_has_review"]),
        "needs_material_recovery_count": sum(1 for item in candidates if item["needs_material_recovery_before_strict_run"]),
        "verdict_counts": dict(Counter(row.get("verdict") or "" for row in rows)),
        "candidates": candidates[:limit],
    }
    write_json(BASE / "reports/candidates_latest.json", report)
    return report


def controller_select_papers(paper_ids: list[str] | None, limit: int, source: str, candidate_scan_limit: int) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    if paper_ids:
        selected = []
        for paper_id in paper_ids[:limit]:
            selected.append({"paper_id": paper_id, "selection_reason": "explicit_paper_id"})
        return selected, None
    candidate_report = build_candidate_report(max(limit, candidate_scan_limit), source)
    selected = []
    for candidate in candidate_report.get("candidates", []):
        if not isinstance(candidate, dict) or not candidate.get("recommended"):
            continue
        selected.append({"paper_id": candidate["paper_id"], "selection_reason": "candidate_report_recommended", "candidate": candidate})
        if len(selected) >= limit:
            break
    return selected, candidate_report


def worker_report_is_clean(report: dict[str, Any] | None) -> bool:
    if not report:
        return False
    cmd = " ".join(str(item) for item in (report.get("command") or []))
    return bool(
        report.get("returncode") == 0
        and report.get("codex_model") == "gpt-5.5"
        and report.get("codex_reasoning_effort") == "xhigh"
        and report.get("codex_session_id")
        and "codex exec" in cmd
    )


def controller_workers_to_run(paper_id: str, requested_workers: list[str], *, force_workers: bool = False) -> tuple[list[str], dict[str, Any]]:
    packet = BASE / "packets" / paper_id
    if force_workers or not packet.exists():
        return requested_workers, {"reason": "force_workers_or_missing_packet"}

    status = paper_status_summary(paper_id)
    if status.get("worker_run_clean") and status.get("paper_level_source_reviewed_complete"):
        return [], {"reason": "already_source_reviewed_complete", "status": status}

    sequence_path = BASE / "worker_logs" / paper_id / "run_sequence_latest.json"
    reports = {str(item.get("worker")): item for item in worker_reports_for_paper(paper_id, sequence_path) if isinstance(item, dict) and item.get("worker")}
    to_run: list[str] = []
    upstream_changed = False
    for worker in requested_workers:
        if worker == "worker-6":
            continue
        if not worker_report_is_clean(reports.get(worker)):
            to_run.append(worker)
            upstream_changed = True

    if "worker-6" in requested_workers:
        worker_6_needs_run = (
            upstream_changed
            or not worker_report_is_clean(reports.get("worker-6"))
            or not status.get("paper_level_source_reviewed_complete")
            or status.get("review_status") == "needs_targeted_rework"
        )
        if worker_6_needs_run:
            to_run.append("worker-6")

    return to_run, {
        "reason": "missing_or_dirty_worker_reports" if to_run else "no_worker_rerun_needed",
        "status": status,
        "existing_workers": sorted(reports),
        "upstream_changed": upstream_changed,
    }


def controller_report_paths(prefix: str = "controller_once") -> tuple[Path, Path]:
    stamp = cst_now().strftime("%Y%m%d_%H%M%S")
    return BASE / "reports" / f"{prefix}_{stamp}.json", BASE / "reports" / f"{prefix}_{stamp}.md"


def render_controller_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# DBAASP Strict Pilot Controller Report",
        "",
        f"- Generated at: `{report.get('generated_at_cst')}`",
        f"- Mode: `{report.get('mode')}`",
        f"- Dry run: `{report.get('dry_run')}`",
        f"- Controller status: `{report.get('controller_status')}`",
        f"- Stop condition: `{report.get('stop_condition')}`",
        f"- Selected papers: {len(report.get('papers') or [])}",
        "",
        "| Paper | Build | Workers | Acceptance | Final status | Auth ingest |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for paper in report.get("papers", []):
        build = paper.get("build", {}).get("action")
        workers = paper.get("workers", {}).get("action")
        acceptance = paper.get("acceptance", {}).get("action")
        final_status = (paper.get("final_status") or {}).get("review_status")
        auth = (paper.get("final_status") or {}).get("authoritative_dbaasp_ingest_ready")
        lines.append(f"| `{paper.get('paper_id')}` | `{build}` | `{workers}` | `{acceptance}` | `{final_status}` | `{auth}` |")
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- Controller success means paper-level source-reviewed acceptance, not clean acceptance.",
            "- `accepted_with_cautions` remains cautioned and must not be promoted to clean.",
            "- `authoritative_dbaasp_ingest_ready=false` remains a separate release/authority boundary.",
            "- This controller is still a sequential independent `codex exec` bridge, not full durable `omx team` mailbox orchestration.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_controller_report(report: dict[str, Any], *, prefix: str = "controller_once") -> dict[str, Any]:
    json_path, md_path = controller_report_paths(prefix)
    report["json_path"] = str(json_path)
    report["markdown_path"] = str(md_path)
    write_json(json_path, report)
    write_json(BASE / "reports/controller_latest.json", report)
    markdown = render_controller_report_markdown(report)
    md_path.write_text(markdown, encoding="utf-8")
    (BASE / "reports/controller_latest.md").write_text(markdown, encoding="utf-8")
    return report


def run_controller_once(args: argparse.Namespace, *, loop_iteration: int | None = None) -> dict[str, Any]:
    workers = [worker.strip() for worker in args.workers.split(",") if worker.strip()]
    unknown = [worker for worker in workers if worker not in WORKER_SKILLS]
    if unknown:
        raise SystemExit(f"unknown workers: {unknown}")

    selected, candidate_report = controller_select_papers(args.paper_id, args.limit, args.source, args.candidate_scan_limit)
    report: dict[str, Any] = {
        "generated_at": utc_now(),
        "generated_at_cst": cst_now().isoformat(),
        "mode": "controller_once",
        "loop_iteration": loop_iteration,
        "dry_run": args.dry_run,
        "selection": {
            "source": args.source,
            "limit": args.limit,
            "candidate_scan_limit": args.candidate_scan_limit,
            "explicit_paper_ids": args.paper_id or [],
            "candidate_report_summary": None
            if candidate_report is None
            else {
                "candidate_count": candidate_report.get("candidate_count"),
                "recommended_count": candidate_report.get("recommended_count"),
                "already_reviewed_count": candidate_report.get("already_reviewed_count"),
                "needs_material_recovery_count": candidate_report.get("needs_material_recovery_count"),
                "report_path": str(BASE / "reports/candidates_latest.json"),
            },
        },
        "runtime_boundary": "sequential independent codex exec bridge; not full durable OMX team mailbox production state",
        "strict_boundary": "paper-level source-reviewed acceptance does not imply clean acceptance or authoritative DBAASP ingest",
        "papers": [],
    }
    if not selected:
        report["controller_status"] = "no_candidate_available"
        report["stop_condition"] = "no recommended unreviewed candidate from current source"
        return write_controller_report(report)

    any_failure = False
    any_acceptance_not_ready = False
    processed_ids: list[str] = []
    for selected_item in selected:
        paper_id = str(selected_item["paper_id"])
        processed_ids.append(paper_id)
        packet = BASE / "packets" / paper_id
        paper_report: dict[str, Any] = {"paper_id": paper_id, "selection": selected_item}

        should_build = args.force_rebuild or not (packet / "packet_manifest.json").exists()
        if args.dry_run:
            paper_report["build"] = {
                "action": "would_build_packet" if should_build else "skip_existing_packet",
                "force_rebuild": args.force_rebuild,
                "packet_manifest": str(packet / "packet_manifest.json"),
            }
        elif should_build:
            built = build_packet(paper_id, args.raw_mode)
            manifest = write_pilot_manifest([paper_id], [built], append=True)
            prompts = write_prompts([paper_id])
            paper_report["build"] = {
                "action": "built_packet",
                "built": built,
                "manifest": str(manifest),
                "prompt_count": len(prompts),
            }
        else:
            manifest = write_pilot_manifest([paper_id], [existing_built_summary(paper_id)], append=True)
            prompts = write_prompts([paper_id])
            paper_report["build"] = {
                "action": "skip_existing_packet",
                "manifest": str(manifest),
                "prompt_count": len(prompts),
            }

        workers_to_run, worker_reason = controller_workers_to_run(paper_id, workers, force_workers=args.force_workers)
        if args.dry_run:
            paper_report["workers"] = {
                "action": "would_run_workers" if workers_to_run else "skip_clean_workers",
                "workers": workers_to_run,
                "reason": worker_reason,
            }
        elif workers_to_run:
            run_id = re.sub(r"[^0-9A-Za-z]+", "", utc_now())
            worker_reports = []
            for worker in workers_to_run:
                worker_report = run_worker(paper_id, worker, args.timeout, run_id)
                worker_reports.append(worker_report)
                if worker_report["returncode"] != 0 and not args.keep_going:
                    break
            sequence = write_run_sequence(paper_id, workers_to_run, worker_reports, merge_existing=True)
            failed = [item for item in worker_reports if item.get("returncode") != 0]
            paper_report["workers"] = {
                "action": "ran_workers",
                "workers": workers_to_run,
                "run_id": run_id,
                "failed_worker_count": len(failed),
                "reports": worker_reports,
                "run_sequence_latest": str(BASE / "worker_logs" / paper_id / "run_sequence_latest.json"),
                "merged_worker_count": len(sequence.get("reports") or []),
            }
            if failed:
                any_failure = True
                paper_report["acceptance"] = {"action": "skip_after_worker_failure", "failed_worker_count": len(failed)}
        else:
            paper_report["workers"] = {"action": "skip_clean_workers", "workers": [], "reason": worker_reason}

        if "acceptance" not in paper_report:
            if args.dry_run:
                paper_report["acceptance"] = {"action": "would_run_acceptance_gates"}
            else:
                acceptance_manifest = build_acceptance_manifest(paper_id)
                gate_run = run_acceptance_gates(paper_id, acceptance_manifest)
                acceptance = build_acceptance_audit(paper_id, acceptance_manifest, gate_run)
                paper_report["acceptance"] = {
                    "action": "ran_acceptance_gates",
                    "acceptance_ready_for_paper_level_source_review": acceptance.get("acceptance_ready_for_paper_level_source_review"),
                    "authoritative_dbaasp_ingest_ready": acceptance.get("authoritative_dbaasp_ingest_ready"),
                    "audit_path": str(BASE / "reports" / f"{paper_id}_strict_acceptance_audit_latest.json"),
                    "gate_summary": acceptance.get("gate_summary"),
                }
                if not acceptance.get("acceptance_ready_for_paper_level_source_review"):
                    any_acceptance_not_ready = True

        if (BASE / "papers" / paper_id / "final/review_report.json").exists():
            final_status = paper_status_summary(paper_id)
            paper_report["final_status"] = {
                "review_status": final_status.get("review_status"),
                "publication_grade": final_status.get("publication_grade"),
                "worker_run_clean": final_status.get("worker_run_clean"),
                "paper_level_source_reviewed_complete": final_status.get("paper_level_source_reviewed_complete"),
                "authoritative_dbaasp_ingest_ready": final_status.get("authoritative_dbaasp_ingest_ready"),
                "open_rework_ticket_count": final_status.get("open_rework_ticket_count"),
                "rework_target_count": final_status.get("rework_target_count"),
            }
        report["papers"].append(paper_report)

        if any_failure and not args.keep_going:
            break

    if args.dry_run:
        report["controller_status"] = "dry_run_plan_ready"
        report["stop_condition"] = "dry_run_no_state_mutation"
    elif any_failure:
        report["controller_status"] = "blocked_by_worker_failure"
        report["stop_condition"] = "repair failed worker and rerun worker-6 plus acceptance"
    elif any_acceptance_not_ready:
        report["controller_status"] = "blocked_by_acceptance_gate"
        report["stop_condition"] = "paper produced nonterminal acceptance audit"
    else:
        status = build_status_report()
        verify_report = verify()
        audit = build_worker_independence_audit(run_gates=True)
        report["global_status_summary"] = {
            "paper_count": status.get("paper_count"),
            "source_reviewed_publication_grade_count": status.get("source_reviewed_publication_grade_count"),
            "authoritative_dbaasp_ingest_ready_count": status.get("authoritative_dbaasp_ingest_ready_count"),
            "open_rework_ticket_count": status.get("open_rework_ticket_count"),
            "missing_final_paper_count": status.get("missing_final_paper_count"),
        }
        report["global_verify_summary"] = {
            "strict_worker_run_gate": (verify_report.get("strict_worker_run_gate") or {}),
            "semantic_gate_returncode": (verify_report.get("semantic_gate") or {}).get("returncode"),
            "publication_gate_returncode": (verify_report.get("publication_gate") or {}).get("returncode"),
        }
        report["global_worker_audit_summary"] = {
            "manifest_paper_count": audit.get("manifest_paper_count"),
            "strict_completed_count": audit.get("strict_completed_count"),
            "total_worker_reports_found": audit.get("total_worker_reports_found"),
            "unique_codex_sessions_found": audit.get("unique_codex_sessions_found"),
            "worker_independence_pass": audit.get("worker_independence_pass"),
            "hard_finding_count": audit.get("hard_finding_count"),
            "json_path": audit.get("json_path"),
            "markdown_path": audit.get("markdown_path"),
        }
        global_ok = bool(
            audit.get("worker_independence_pass")
            and int(audit.get("hard_finding_count") or 0) == 0
            and int((verify_report.get("strict_worker_run_gate") or {}).get("hard_finding_count") or 0) == 0
            and (verify_report.get("semantic_gate") or {}).get("returncode") == 0
            and (verify_report.get("publication_gate") or {}).get("returncode") == 0
        )
        if global_ok:
            report["controller_status"] = "completed"
            report["stop_condition"] = f"processed {len(processed_ids)} paper(s) through strict controller and global audit"
        else:
            report["controller_status"] = "blocked_by_global_gate"
            report["stop_condition"] = "global semantic/publication/worker audit gate did not pass"

    return write_controller_report(report)


def cmd_controller_once(args: argparse.Namespace) -> int:
    report = run_controller_once(args)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["controller_status"] in {"dry_run_plan_ready", "completed", "no_candidate_available"}:
        return 0
    return 1


def cmd_controller_loop(args: argparse.Namespace) -> int:
    iterations: list[dict[str, Any]] = []
    failed = False
    for index in range(1, args.max_iterations + 1):
        report = run_controller_once(args, loop_iteration=index)
        iterations.append(
            {
                "iteration": index,
                "controller_status": report.get("controller_status"),
                "stop_condition": report.get("stop_condition"),
                "json_path": report.get("json_path"),
                "papers": [item.get("paper_id") for item in report.get("papers", [])],
            }
        )
        status = str(report.get("controller_status"))
        if status in {"dry_run_plan_ready", "no_candidate_available"}:
            break
        if status != "completed":
            failed = True
            break
        if index < args.max_iterations and args.sleep_seconds:
            time.sleep(args.sleep_seconds)

    loop_report = {
        "generated_at": utc_now(),
        "generated_at_cst": cst_now().isoformat(),
        "mode": "controller_loop",
        "dry_run": args.dry_run,
        "max_iterations": args.max_iterations,
        "iterations": iterations,
        "controller_status": "failed" if failed else "complete_or_no_more_candidates",
        "runtime_boundary": "sequential independent codex exec bridge; not full durable OMX team mailbox production state",
    }
    loop_report = write_controller_report(loop_report, prefix="controller_loop")
    print(json.dumps(loop_report, ensure_ascii=False, indent=2))
    return 1 if failed else 0


def build_acceptance_manifest(paper_id: str) -> Path:
    # Acceptance must gate the current queue state, not a stale
    # analysis_status.json left behind before terminal ticket closure.
    sync_packet_statuses([paper_id])
    packet = BASE / "packets" / paper_id
    paper_root = BASE / "papers" / paper_id
    if not packet.exists():
        raise SystemExit(f"missing packet for {paper_id}: {packet}")
    manifest = safe_read_json(packet / "packet_manifest.json")
    extraction = safe_read_json(packet / "extraction/extraction_status.json")
    db_manifest = safe_read_json(packet / "database/database_source_manifest.json")
    data = {
        "created_at": utc_now(),
        "scope": "Single-paper strict acceptance proof manifest for DBAASP pilot",
        "paper_ids": [paper_id],
        "papers": [
            {
                "paper_id": paper_id,
                "paper_root": str(paper_root),
                "packet_root": str(packet),
                "material_status": manifest.get("material_queue_status") or extraction.get("status") or "unknown",
                "locator_count": live_locator_count(packet),
                "database_row_counts": db_manifest.get("row_counts") or {},
                "error_count": len(live_extraction_errors(packet)),
            }
        ],
        "packet_root": str(BASE / "packets"),
        "root_for_gates": str(BASE),
        "model_requirement": {"model": "gpt-5.5", "reasoning_effort": "xhigh"},
        "strict_boundary": "single paper acceptance proof; global pilot manifest still preserves other blocked/queued papers",
    }
    path = BASE / "manifests" / f"dbaasp_strict_pilot_{paper_id}_acceptance_manifest.json"
    write_json(path, data)
    return path


def run_acceptance_gates(paper_id: str, manifest: Path) -> dict[str, Any]:
    packet_json = BASE / "reports" / f"{paper_id}_check_two_queue_packets_acceptance.json"
    semantic_json = BASE / "reports" / f"{paper_id}_semantic_gate_acceptance.json"
    publication_json = BASE / "reports" / f"{paper_id}_publication_quality_acceptance.json"
    commands = {
        "packet_gate": [
            "python3",
            str(CHECK_PACKET_SCRIPT),
            "--packet-root",
            str(BASE / "packets"),
            "--manifest",
            str(manifest),
            "--json-out",
            str(packet_json),
        ],
        "semantic_gate": [
            "python3",
            str(SEMANTIC_GATE),
            "--root",
            str(BASE),
            "--manifest",
            str(manifest),
            "--json",
        ],
        "publication_gate": [
            "python3",
            str(PUBLICATION_GATE),
            "--root",
            str(BASE),
            "--manifest",
            str(manifest),
            "--issues",
            str(BASE / "issues/dbaasp_strict_pilot_issues.jsonl"),
            "--json-out",
            str(publication_json),
        ],
    }
    report_paths = {
        "packet_gate": packet_json,
        "semantic_gate": semantic_json,
        "publication_gate": publication_json,
    }
    results: dict[str, Any] = {}
    for name, cmd in commands.items():
        report_path = report_paths[name]
        report_path.unlink(missing_ok=True)
        started_epoch = time.time()
        code, stdout, stderr = run_cmd(cmd, timeout=240)
        if name == "semantic_gate":
            semantic_json.parent.mkdir(parents=True, exist_ok=True)
            semantic_json.write_text(stdout, encoding="utf-8")
        report_exists = report_path.exists()
        report_mtime = report_path.stat().st_mtime if report_exists else None
        results[name] = {
            "returncode": code,
            "stdout_tail": stdout[-4000:],
            "stderr_tail": stderr[-4000:],
            "started_epoch": started_epoch,
            "report_exists": report_exists,
            "report_mtime": report_mtime,
            "report_fresh": bool(report_mtime is not None and report_mtime >= started_epoch - 1),
        }
    return {
        "manifest": str(manifest),
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "commands": commands,
        "results": results,
        "reports": {
            "packet_gate": str(packet_json),
            "semantic_gate": str(semantic_json),
            "publication_gate": str(publication_json),
        },
    }


def build_acceptance_audit(paper_id: str, manifest: Path, gate_run: dict[str, Any]) -> dict[str, Any]:
    strict_worker_gate = strict_worker_run_gate([paper_id])
    status = paper_status_summary(paper_id)
    review = safe_read_json(BASE / "papers" / paper_id / "final/review_report.json")
    packet_gate = safe_read_json(Path(gate_run["reports"]["packet_gate"]))
    semantic_gate = safe_read_json(Path(gate_run["reports"]["semantic_gate"]))
    publication_gate = safe_read_json(Path(gate_run["reports"]["publication_gate"]))
    gate_results = gate_run.get("results") if isinstance(gate_run.get("results"), dict) else {}
    gate_returncodes = {
        name: (gate_results.get(name) or {}).get("returncode")
        for name in ("packet_gate", "semantic_gate", "publication_gate")
    }
    gate_runs_passed = all(code == 0 for code in gate_returncodes.values())
    gate_payloads = (packet_gate, semantic_gate, publication_gate)
    gate_payloads_valid = all(
        bool(payload) and not any(key in payload for key in ("_parse_error", "_not_object"))
        for payload in gate_payloads
    )
    expected_manifest_sha256 = (
        hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest.exists() else None
    )
    gate_manifest_matches = bool(
        gate_run.get("manifest") == str(manifest)
        and expected_manifest_sha256
        and gate_run.get("manifest_sha256") == expected_manifest_sha256
    )

    def report_is_current(name: str) -> bool:
        result = gate_results.get(name)
        report_text = (gate_run.get("reports") or {}).get(name)
        if not isinstance(result, dict) or not isinstance(report_text, str):
            return False
        if result.get("report_fresh") is not True or result.get("report_exists") is not True:
            return False
        started_epoch = result.get("started_epoch")
        report_mtime = result.get("report_mtime")
        if not isinstance(started_epoch, (int, float)) or not isinstance(report_mtime, (int, float)):
            return False
        report_path = Path(report_text)
        if not report_path.exists():
            return False
        actual_mtime = report_path.stat().st_mtime
        return bool(
            report_mtime >= started_epoch - 1
            and actual_mtime >= started_epoch - 1
            and abs(actual_mtime - report_mtime) <= 1e-6
        )

    gate_reports_fresh = all(
        report_is_current(name)
        for name in ("packet_gate", "semantic_gate", "publication_gate")
    )
    acceptance_ready = bool(
        gate_runs_passed
        and gate_payloads_valid
        and gate_reports_fresh
        and gate_manifest_matches
        and status["paper_level_source_reviewed_complete"]
        and not status["authoritative_dbaasp_ingest_ready"]
        and status["worker_run"]["worker_count"] == 6
        and status["worker_run"]["all_returncode_zero"]
        and status["worker_run"]["all_gpt55_xhigh"]
        and status["worker_run"]["unique_session_count"] == 6
        and strict_worker_gate.get("hard_finding_count") == 0
        and packet_gate.get("hard_finding_count") == 0
        and packet_gate.get("open_rework_ticket_count") == 0
        and semantic_gate.get("publication_grade_pass_count") == 1
        and publication_gate.get("publication_grade_pass") is True
    )
    audit = {
        "generated_at": utc_now(),
        "paper_id": paper_id,
        "manifest": str(manifest),
        "acceptance_ready_for_paper_level_source_review": acceptance_ready,
        "authoritative_dbaasp_ingest_ready": status["authoritative_dbaasp_ingest_ready"],
        "review": {
            "review_status": review.get("review_status"),
            "publication_grade": review.get("publication_grade"),
            "validator_contract_passed": review.get("validator_contract_passed"),
            "reviewed_at": review.get("reviewed_at"),
            "review_model": review.get("review_model"),
            "reasoning_effort": review.get("reasoning_effort"),
            "rework_target_count": len(review.get("rework_targets") if isinstance(review.get("rework_targets"), list) else []),
            "caution_count": len(review.get("caution_findings") if isinstance(review.get("caution_findings"), list) else []),
        },
        "status": status,
        "gate_summary": {
            "gate_returncodes": gate_returncodes,
            "gate_runs_passed": gate_runs_passed,
            "gate_payloads_valid": gate_payloads_valid,
            "gate_reports_fresh": gate_reports_fresh,
            "gate_manifest_matches": gate_manifest_matches,
            "packet_hard_finding_count": packet_gate.get("hard_finding_count"),
            "packet_open_rework_ticket_count": packet_gate.get("open_rework_ticket_count"),
            "semantic_publication_grade_pass_count": semantic_gate.get("publication_grade_pass_count"),
            "semantic_failed_papers": semantic_gate.get("failed_papers"),
            "publication_grade_pass": publication_gate.get("publication_grade_pass"),
            "publication_risk_counts": publication_gate.get("risk_counts"),
            "strict_worker_run_hard_finding_count": strict_worker_gate.get("hard_finding_count"),
            "strict_worker_run_hard_finding_papers": strict_worker_gate.get("hard_finding_papers"),
        },
        "strict_worker_run_gate": strict_worker_gate,
        "gate_run": gate_run,
        "strict_boundary": "paper-level acceptance proof only; authoritative DBAASP ingest still requires linked authority rows and release policy approval",
    }
    path = BASE / "reports" / f"{paper_id}_strict_acceptance_audit_latest.json"
    write_json(path, audit)
    return audit


def cmd_build(args: argparse.Namespace) -> int:
    paper_ids = args.paper_id or DEFAULT_PAPER_IDS
    built = [build_packet(pid, args.raw_mode) for pid in paper_ids]
    manifest = write_pilot_manifest(paper_ids, built, append=args.append_manifest)
    manifest_data = read_json(manifest)
    prompts = write_prompts(paper_ids)
    summary = {
        "created_at": utc_now(),
        "paper_ids": paper_ids,
        "manifest_paper_ids": manifest_data.get("paper_ids", paper_ids),
        "manifest": str(manifest),
        "prompt_count": len(prompts),
        "built": built,
        "next_command": f"python3 {Path(__file__).relative_to(ROOT)} run --paper-id {paper_ids[0]} --workers worker-1,worker-2,worker-3,worker-4,worker-5,worker-6",
    }
    write_json(BASE / "reports/build_latest.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    paper_id = args.paper_id
    workers = [w.strip() for w in args.workers.split(",") if w.strip()]
    unknown = [w for w in workers if w not in WORKER_SKILLS]
    if unknown:
        raise SystemExit(f"unknown workers: {unknown}")
    run_id = re.sub(r"[^0-9A-Za-z]+", "", utc_now())
    reports = []
    sequence: dict[str, Any] = {}
    for worker in workers:
        report = run_worker(paper_id, worker, args.timeout, run_id)
        reports.append(report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        # Persist after every worker so a multi-hour six-worker paper can be
        # resumed without losing already completed canonical session proof.
        sequence = write_run_sequence(
            paper_id, workers, reports, merge_existing=args.merge_existing
        )
        if report["returncode"] != 0 and not args.keep_going:
            break
    return 0 if all(r["returncode"] == 0 for r in sequence.get("reports", [])) else 1


def cmd_verify(args: argparse.Namespace) -> int:
    report = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if getattr(args, "diagnostic", False):
        return 0
    return 1 if verify_gate_findings(report) else 0


def cmd_status(args: argparse.Namespace) -> int:
    report = build_status_report(args.paper_id)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def cmd_candidates(args: argparse.Namespace) -> int:
    report = build_candidate_report(args.limit, args.source)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def cmd_recover_materials(args: argparse.Namespace) -> int:
    report = recover_materials_for_paper(args.paper_id, apply=args.apply)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def cmd_acceptance(args: argparse.Namespace) -> int:
    manifest = build_acceptance_manifest(args.paper_id)
    gate_run = run_acceptance_gates(args.paper_id, manifest)
    audit = build_acceptance_audit(args.paper_id, manifest, gate_run)
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0 if audit["acceptance_ready_for_paper_level_source_review"] else 1


def cmd_audit_workers(args: argparse.Namespace) -> int:
    audit = build_worker_independence_audit(
        args.paper_id,
        run_gates=not args.skip_gates,
        allow_incomplete=args.allow_incomplete,
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0 if audit["worker_independence_pass"] else 1


def add_controller_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--paper-id", action="append", help="Explicit paper ID to process; otherwise choose recommended candidates")
    parser.add_argument("--limit", type=int, default=1, help="Number of papers to process in one controller pass")
    parser.add_argument("--source", choices=["all", "codex-batch"], default="all", help="Candidate source for automatic selection")
    parser.add_argument("--candidate-scan-limit", type=int, default=50, help="How many ranked candidates to scan for automatic selection")
    parser.add_argument("--raw-mode", choices=["copy", "symlink", "manifest-only"], default="copy")
    parser.add_argument("--workers", default="worker-1,worker-2,worker-3,worker-4,worker-5,worker-6")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--dry-run", action="store_true", help="Plan and write controller report without building, running workers, or gates")
    parser.add_argument("--force-rebuild", action="store_true", help="Rebuild packet even when a packet manifest exists")
    parser.add_argument("--force-workers", action="store_true", help="Rerun requested workers even when latest reports are clean")
    parser.add_argument("--keep-going", action="store_true", help="Continue within a paper after a worker failure and continue batch processing")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    build = sub.add_parser("build", help="Build DBAASP strict pilot packets/prompts")
    build.add_argument("--paper-id", action="append", help="Paper ID to include; repeatable")
    build.add_argument("--raw-mode", choices=["copy", "symlink", "manifest-only"], default="copy")
    build.add_argument("--append-manifest", action="store_true", help="Keep already built pilot papers in the manifest")
    build.set_defaults(func=cmd_build)

    run = sub.add_parser("run", help="Run independent Codex CLI worker roles for one pilot paper")
    run.add_argument("--paper-id", required=True)
    run.add_argument("--workers", default="worker-1,worker-2,worker-3,worker-4,worker-5,worker-6")
    run.add_argument("--timeout", type=int, default=1200)
    run.add_argument("--keep-going", action="store_true")
    run.add_argument("--merge-existing", action="store_true", help="Merge new worker reports into the existing run_sequence_latest.json")
    run.set_defaults(func=cmd_run)

    verify_parser = sub.add_parser("verify", help="Run packet/semantic/publication strict gates")
    verify_parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="Always return 0 after writing the gate report; strict mode is the default",
    )
    verify_parser.set_defaults(func=cmd_verify)

    status_parser = sub.add_parser("status", help="Summarize strict pilot paper states and ingest boundaries")
    status_parser.add_argument("--paper-id", action="append", help="Restrict status to one or more paper IDs")
    status_parser.set_defaults(func=cmd_status)

    candidates_parser = sub.add_parser("candidates", help="Rank DBAASP pending papers for the next strict pilot run")
    candidates_parser.add_argument("--limit", type=int, default=20)
    candidates_parser.add_argument(
        "--source",
        choices=["all", "codex-batch"],
        default="all",
        help="Use all canonical dbaasp_extracted.tsv rows or the original 10-paper Codex fallback batch",
    )
    candidates_parser.set_defaults(func=cmd_candidates)

    recover_parser = sub.add_parser("recover-materials", help="Recover declared supplementary files for one paper")
    recover_parser.add_argument("--paper-id", required=True)
    recover_parser.add_argument("--apply", action="store_true", help="Copy successfully downloaded files into the paper source supplementary directory")
    recover_parser.set_defaults(func=cmd_recover_materials)

    acceptance_parser = sub.add_parser("acceptance", help="Generate single-paper strict acceptance manifest, gates, and audit")
    acceptance_parser.add_argument("--paper-id", required=True)
    acceptance_parser.set_defaults(func=cmd_acceptance)

    audit_parser = sub.add_parser(
        "audit-workers",
        help="Audit six-worker Codex CLI session independence and paper-level strict completion",
    )
    audit_parser.add_argument("--paper-id", action="append", help="Restrict audit to one or more paper IDs")
    audit_parser.add_argument("--skip-gates", action="store_true", help="Skip full manifest verify() gate execution")
    audit_parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Report incomplete papers without failing the command; useful for in-progress snapshots",
    )
    audit_parser.set_defaults(func=cmd_audit_workers)

    controller = sub.add_parser("controller", help="Run or plan the resumable strict-pilot controller")
    controller_sub = controller.add_subparsers(dest="controller_cmd", required=True)
    controller_once = controller_sub.add_parser("once", help="Process the next strict-pilot candidate once")
    add_controller_common_args(controller_once)
    controller_once.set_defaults(func=cmd_controller_once)

    controller_loop = controller_sub.add_parser("loop", help="Repeat controller once until max iterations, failure, or no candidates")
    add_controller_common_args(controller_loop)
    controller_loop.add_argument("--max-iterations", type=int, default=1)
    controller_loop.add_argument("--sleep-seconds", type=int, default=0)
    controller_loop.set_defaults(func=cmd_controller_loop)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
