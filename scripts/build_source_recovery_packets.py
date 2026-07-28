#!/usr/bin/env python3
"""Build material-only recovery packets from landed source assets.

The packets produced here are for source recovery only. They deliberately set
analysis_status to blocked until a later review queue consumes a strict-ready
packet. This prevents weak-source and metadata-only papers from being promoted
to scientific review by accident.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tarfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


TEXT_SUFFIXES = {".txt", ".csv", ".tsv", ".md", ".html", ".htm"}
XML_SUFFIXES = {".xml", ".nxml"}
PDF_SUFFIXES = {".pdf"}
ARCHIVE_SUFFIXES = {".zip", ".tar", ".gz", ".tgz"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(elem: ET.Element) -> str:
    return " ".join(" ".join(elem.itertext()).split())


def link_or_copy(src: Path, dest: Path, mode: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        return
    if mode == "symlink":
        os.symlink(src, dest, target_is_directory=src.is_dir())
    elif mode == "hardlink" and src.is_file():
        try:
            os.link(src, dest)
        except OSError:
            shutil.copy2(src, dest)
    else:
        shutil.copy2(src, dest)


def stage_tree(source_dir: Path, dest_dir: Path, mode: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not source_dir.exists():
        return rows
    for src in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        rel = src.relative_to(source_dir)
        dest = dest_dir / rel
        link_or_copy(src, dest, mode)
        rows.append({"source": str(src), "target": str(dest), "relative_path": str(rel), "size_bytes": src.stat().st_size})
    return rows


def extract_xml(xml_paths: list[Path], out_path: Path) -> tuple[int, list[dict[str, Any]], list[dict[str, Any]]]:
    sections: list[dict[str, Any]] = []
    captions: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for xml_path in xml_paths:
        try:
            root = ET.parse(xml_path).getroot()
        except Exception as exc:  # noqa: BLE001 - packet should preserve parse failure
            errors.append({"type": "xml_parse_error", "source": str(xml_path), "error": str(exc)})
            continue
        counters: Counter[str] = Counter()
        for elem in root.iter():
            tag = local_name(elem.tag)
            if tag not in {"article-title", "abstract", "sec", "p", "table-wrap", "fig", "caption"}:
                continue
            text = text_of(elem)
            if not text:
                continue
            counters[tag] += 1
            locator = f"xml:{xml_path.name}:{tag}:{counters[tag]}"
            item = {"locator": locator, "source": str(xml_path), "tag": tag, "text": text[:5000]}
            sections.append(item)
            if tag in {"fig", "caption", "table-wrap"}:
                captions.append(item)
    write_json(out_path, {"source_count": len(xml_paths), "section_count": len(sections), "sections": sections, "errors": errors})
    return len(sections), captions, errors


def run_cmd(cmd: list[str], timeout: int = 180) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or f"timeout after {timeout}s"
    return proc.returncode, proc.stdout, proc.stderr


def extract_pdf_text(pdf_paths: list[Path], out_path: Path) -> tuple[int, list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    tool = shutil.which("pdftotext")
    if not tool and pdf_paths:
        errors.append({"type": "missing_tool", "tool": "pdftotext"})
        append_jsonl(out_path, rows)
        return 0, rows, errors
    for pdf_path in pdf_paths:
        code, stdout, stderr = run_cmd([tool or "pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), "-"])
        if code != 0:
            errors.append({"type": "pdf_text_failed", "source": str(pdf_path), "exit_code": code, "stderr": stderr[-2000:]})
            continue
        for page, text in enumerate(stdout.split("\f"), start=1):
            text = text.strip()
            if text:
                rows.append({"locator": f"pdf:{pdf_path.name}:page={page}", "source": str(pdf_path), "page": page, "text": text})
    append_jsonl(out_path, rows)
    return len(rows), rows, errors


def archive_manifest(files: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    archives: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for src in files:
        suffixes = "".join(src.suffixes).lower()
        if src.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(src) as zf:
                    archives.append({"source": str(src), "entry_count": len(zf.infolist()), "entries": [info.filename for info in zf.infolist()[:200]]})
            except Exception as exc:  # noqa: BLE001
                errors.append({"type": "zip_list_failed", "source": str(src), "error": str(exc)})
        elif src.suffix.lower() in {".tar", ".tgz"} or suffixes.endswith(".tar.gz"):
            try:
                with tarfile.open(src) as tf:
                    members = tf.getmembers()
                    archives.append({"source": str(src), "entry_count": len(members), "entries": [m.name for m in members[:200]]})
            except Exception as exc:  # noqa: BLE001
                errors.append({"type": "tar_list_failed", "source": str(src), "error": str(exc)})
    return archives, errors


def ticket(paper_id: str, code: str, severity: str, required_action: str, source: str | None = None) -> dict[str, Any]:
    return {
        "ticket_id": f"material-recovery-{paper_id}-{code}",
        "created_at": utc_now(),
        "paper_id": paper_id,
        "target_queue": "material",
        "severity": severity,
        "blocker_type": code,
        "source": source,
        "required_action": required_action,
        "acceptance_check": "Rebuild packet after source recovery and verify primary XML/PDF or an explicit exhausted-material blocker.",
    }


def build_packet(item: dict[str, Any], packet_root: Path, mode: str) -> dict[str, Any]:
    paper_id = str(item["paper_id"])
    source_path = Path(str(item["source_path"]))
    packet = packet_root / paper_id
    if packet.exists():
        shutil.rmtree(packet)
    for rel in ["raw/xml", "raw/pdf", "raw/package", "raw/supplementary", "extracted", "extraction", "database", "locators", "analysis", "final", "rework"]:
        (packet / rel).mkdir(parents=True, exist_ok=True)

    staged = {
        "metadata": stage_tree(source_path, packet / "raw/source_root_manifest", mode) if False else [],
        "xml": stage_tree(source_path / "xml", packet / "raw/xml", mode),
        "pdf": stage_tree(source_path / "pdf", packet / "raw/pdf", mode),
        "package": stage_tree(source_path / "package", packet / "raw/package", mode),
        "supplementary": stage_tree(source_path / "supplementary", packet / "raw/supplementary", mode),
    }
    for name in ["metadata.json", "asset_manifest.csv"]:
        src = source_path / name
        if src.exists():
            link_or_copy(src, packet / "raw" / name, mode)

    xml_paths = sorted(path for path in (packet / "raw/xml").rglob("*") if path.is_file() and path.suffix.lower() in XML_SUFFIXES)
    pdf_paths = sorted(path for path in (packet / "raw/pdf").rglob("*") if path.is_file() and path.suffix.lower() in PDF_SUFFIXES)
    supp_files = sorted(path for path in (packet / "raw/supplementary").rglob("*") if path.is_file())
    package_files = sorted(path for path in (packet / "raw/package").rglob("*") if path.is_file())

    xml_count, captions, xml_errors = extract_xml(xml_paths, packet / "extracted/xml_sections.json")
    pdf_text_count, pdf_rows, pdf_errors = extract_pdf_text(pdf_paths, packet / "extracted/pdf_text.jsonl")
    archive_rows, archive_errors = archive_manifest(package_files + [item for item in supp_files if item.suffix.lower() in ARCHIVE_SUFFIXES or "".join(item.suffixes).lower().endswith(".tar.gz")])
    write_json(packet / "extracted/figure_captions.json", {"caption_count": len(captions), "captions": captions})
    write_json(
        packet / "extracted/supplementary_index.json",
        {
            "file_count": len(supp_files),
            "files": [
                {"path": str(path), "relative_path": str(path.relative_to(packet / "raw/supplementary")), "suffix": path.suffix.lower(), "size_bytes": path.stat().st_size}
                for path in supp_files
            ],
        },
    )
    write_json(packet / "extracted/supplementary_tables.json", {"tables": [], "note": "source-recovery packet inventory only"})
    write_json(packet / "extracted/archive_manifest.json", {"archive_count": len(archive_rows), "archives": archive_rows})

    errors = xml_errors + pdf_errors + archive_errors
    tickets: list[dict[str, Any]] = []
    if not xml_paths:
        tickets.append(ticket(paper_id, "missing_primary_xml_or_nxml", "blocking", "Recover primary XML/NXML or document why XML is unavailable.", str(source_path / "xml")))
    elif not any(path.suffix.lower() == ".xml" for path in xml_paths):
        tickets.append(ticket(paper_id, "nxml_present_but_strict_xml_missing", "caution", "Either convert/accept NXML as primary XML equivalent or stage strict xml/*.xml before review.", str(source_path / "xml")))
    if not pdf_paths:
        tickets.append(ticket(paper_id, "missing_primary_pdf", "blocking", "Recover primary PDF or document why PDF is unavailable.", str(source_path / "pdf")))
    if not xml_paths and not pdf_paths:
        material_status = "material_blocked_missing_source"
    elif tickets:
        material_status = "material_extracted_with_gaps"
    else:
        material_status = "material_extracted_complete"

    locator_rows = []
    locator_rows.extend({"locator": section["locator"], "source": "xml_sections"} for section in read_json(packet / "extracted/xml_sections.json").get("sections", []))
    locator_rows.extend({"locator": row["locator"], "source": "pdf_text"} for row in pdf_rows)
    write_json(packet / "locators/locator_index.json", {"locator_count": len(locator_rows), "locators": locator_rows[:10000]})
    write_json(packet / "locators/citation_map.json", {"note": "material-recovery locator map; scientific citation mapping is analysis-owned"})
    write_json(packet / "database/database_source_manifest.json", {"row_counts": {}, "note": "database snapshot not built in material-only source recovery packet"})
    write_json(packet / "analysis/analysis_status.json", {"status": "analysis_blocked_until_material_handoff", "generated_at": utc_now()})

    extraction_status = {
        "paper_id": paper_id,
        "status": material_status,
        "generated_at": utc_now(),
        "xml_file_count": len(xml_paths),
        "pdf_file_count": len(pdf_paths),
        "xml_section_count": xml_count,
        "pdf_text_item_count": pdf_text_count,
        "supplementary_file_count": len(supp_files),
        "package_file_count": len(package_files),
        "error_count": len(errors),
    }
    write_json(packet / "extraction/extraction_status.json", extraction_status)
    write_json(packet / "extraction/extraction_quality_report.json", {"status": material_status, "errors": errors, "tickets": tickets})
    append_jsonl(packet / "extraction/extraction_errors.jsonl", errors)
    append_jsonl(packet / "rework/rework_requests.jsonl", tickets)
    append_jsonl(packet / "rework/rework_responses.jsonl", [])

    packet_manifest = {
        "paper_id": paper_id,
        "packet_version": "source_recovery_v1",
        "generated_at": utc_now(),
        "packet_root": str(packet),
        "source_path": str(source_path),
        "source_category": item.get("category"),
        "raw_mode": mode,
        "material_queue_status": material_status,
        "analysis_queue_status": "analysis_blocked_until_material_handoff",
        "open_rework_ticket_ids": [row["ticket_id"] for row in tickets],
        "known_missing_or_blocked_materials": tickets,
        "staged_file_counts": {key: len(value) for key, value in staged.items()},
    }
    write_json(packet / "packet_manifest.json", packet_manifest)
    return {
        "paper_id": paper_id,
        "packet_root": str(packet),
        "material_status": material_status,
        "analysis_status": "analysis_blocked_until_material_handoff",
        "xml_file_count": len(xml_paths),
        "pdf_file_count": len(pdf_paths),
        "locator_count": len(locator_rows),
        "open_rework_ticket_count": len(tickets),
        "error_count": len(errors),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("reports/source_recovery/weak_source_manifest_latest.json"))
    parser.add_argument("--packet-root", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--raw-mode", choices=["symlink", "hardlink", "copy"], default="symlink")
    parser.add_argument("--run-label", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = read_json(args.manifest)
    items = [item for item in manifest.get("items", []) if isinstance(item, dict)]
    if args.limit:
        items = items[: args.limit]
    run_label = args.run_label or f"source_recovery_packets_{safe_stamp()}"
    packet_root = args.packet_root or Path("source_recovery_packets") / run_label
    packet_root.mkdir(parents=True, exist_ok=True)
    results = [build_packet(item, packet_root, args.raw_mode) for item in items]
    summary = {
        "generated_at": utc_now(),
        "manifest": str(args.manifest),
        "packet_root": str(packet_root),
        "paper_count": len(results),
        "raw_mode": args.raw_mode,
        "completion_claim": "material_recovery_packets_only_not_review_completion",
        "material_status_counts": dict(Counter(row["material_status"] for row in results)),
        "analysis_status_counts": dict(Counter(row["analysis_status"] for row in results)),
        "open_rework_ticket_count": sum(row["open_rework_ticket_count"] for row in results),
        "total_locator_count": sum(row["locator_count"] for row in results),
        "results": results,
    }
    write_json(packet_root / "source_recovery_packet_build_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
