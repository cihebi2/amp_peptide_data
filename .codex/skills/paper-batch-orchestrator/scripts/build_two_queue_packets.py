#!/usr/bin/env python3
"""Build two-queue paper packets for an AMP curation handoff.

The script is intentionally conservative: it creates packet directories from
already landed/staged paper assets and existing worker outputs. It does not make
new scientific conclusions. Its job is to test whether the material queue can
produce a self-contained packet that the analysis queue can consume. Existing
analysis/final files copied into the packet are prior artifacts only; this
script must not mark them as source-reviewed analysis acceptance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

TEXT_SUFFIXES = {".txt", ".csv", ".tsv", ".md"}
PDF_SUFFIXES = {".pdf"}
DOC_SUFFIXES = {".doc"}
XLS_SUFFIXES = {".xls"}
XLSX_SUFFIXES = {".xlsx"}
ARCHIVE_SUFFIXES = {".zip", ".rar", ".7z", ".gz", ".tgz", ".tar"}

CORPUS_OUTPUT = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output")
LOCAL_TOOLS = {
    "pdftotext": shutil.which("pdftotext"),
    "antiword": shutil.which("antiword"),
    "catdoc": shutil.which("catdoc"),
    "xls2csv": shutil.which("xls2csv"),
    "seven_zip": "/root/software/rar-tools/7zz",
    "extract_rar": "/root/software/rar-tools/extract-rar",
    "paddleocr_python": "/root/software/PaddleOCR/.venv/bin/python",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def stable_ticket_id(paper_id: str, index: int, error: dict[str, Any]) -> str:
    payload = json.dumps(error, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256(f"{paper_id}\n{index}\n{payload}".encode("utf-8")).hexdigest()[:12]
    return f"material-rework-{index:03d}-{digest}"


def material_error_severity(error: dict[str, Any]) -> str:
    error_type = str(error.get("type") or "")
    source = str(error.get("source") or "")
    if error_type in {"missing_xml", "missing_pdf", "xml_parse_error", "pdf_text_failed", "missing_database_linkage"}:
        return "blocking"
    if error_type == "missing_raw_source" and source.endswith(("paper.xml", "paper.pdf")):
        return "blocking"
    if source.endswith("source_record_links.json"):
        return "blocking"
    return "caution"


def material_error_required_action(error: dict[str, Any]) -> str:
    error_type = str(error.get("type") or "material_gap")
    source = str(error.get("source") or "unknown source")
    if error_type == "missing_database_linkage":
        return (
            "Regenerate or restore work/database_linkage/source_record_links.json, "
            "then rebuild the packet database snapshot without inventing source_verified links."
        )
    if error_type in {"missing_xml", "xml_parse_error"} or source.endswith("paper.xml"):
        return "Restore or regenerate a parseable primary paper.xml/nxml source, then rebuild XML locators."
    if error_type in {"missing_pdf", "pdf_text_failed"} or source.endswith("paper.pdf"):
        return "Restore or regenerate the primary paper PDF/text surface, then rebuild PDF locators."
    if "supp" in source.lower() or "package" in source.lower() or error_type.endswith("_extract_failed"):
        return "Recover or explicitly exhaust the referenced supplementary/package material, then rebuild packet extracts."
    return "Resolve or explicitly justify the packet material gap, then rebuild the packet and rerun packet checks."


def material_error_acceptance_check(error: dict[str, Any]) -> str:
    error_type = str(error.get("type") or "material_gap")
    source = str(error.get("source") or "")
    if error_type == "missing_database_linkage" or source.endswith("source_record_links.json"):
        return "database/database_source_manifest.json reports source_record_links_present=true and no missing_database_linkage remains."
    if error_type in {"missing_xml", "xml_parse_error"} or source.endswith("paper.xml"):
        return "extracted/xml_sections.json has source text or a source-backed blocked reason, and this ticket is closed."
    if error_type in {"missing_pdf", "pdf_text_failed"} or source.endswith("paper.pdf"):
        return "extracted/pdf_text.jsonl has PDF text locators or a source-backed blocked reason, and this ticket is closed."
    return "extraction/extraction_errors.jsonl no longer contains this error, or the packet manifest preserves a justified blocked/caution state."


def material_rework_tickets(paper_id: str, errors: list[dict[str, Any]], generated_at: str) -> list[dict[str, Any]]:
    tickets: list[dict[str, Any]] = []
    for index, error in enumerate(errors, start=1):
        if not isinstance(error, dict):
            continue
        error_type = str(error.get("type") or "material_gap")
        tickets.append(
            {
                "ticket_id": stable_ticket_id(paper_id, index, error),
                "created_at": generated_at,
                "paper_id": paper_id,
                "target_queue": "material",
                "severity": material_error_severity(error),
                "blocker_type": error_type,
                "source": error.get("source"),
                "owner_stage": "packet_preflight_or_material_extraction",
                "required_action": material_error_required_action(error),
                "acceptance_check": material_error_acceptance_check(error),
                "source_error": error,
            }
        )
    return tickets


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(elem: ET.Element) -> str:
    return " ".join(" ".join(elem.itertext()).split())


def safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def materialize(src: Path, dest: Path, mode: str, errors: list[dict[str, Any]]) -> None:
    if not src.exists():
        errors.append({"type": "missing_raw_source", "source": str(src), "dest": str(dest)})
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.unlink()
    if mode == "manifest-only":
        return
    if mode == "symlink":
        os.symlink(src, dest, target_is_directory=src.is_dir())
        return
    if src.is_dir():
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)


def run_cmd(cmd: list[str], timeout: int = 120) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or f"timeout after {timeout}s"
    return proc.returncode, proc.stdout, proc.stderr


def extract_xml_sections(xml_path: Path, out_path: Path) -> tuple[int, list[dict[str, Any]], list[dict[str, Any]]]:
    sections: list[dict[str, Any]] = []
    captions: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if not xml_path.exists():
        errors.append({"type": "missing_xml", "source": str(xml_path)})
        write_json(out_path, {"source": str(xml_path), "sections": sections, "errors": errors})
        return 0, captions, errors
    try:
        root = ET.parse(xml_path).getroot()
    except Exception as exc:  # noqa: BLE001 - diagnostic packet output
        errors.append({"type": "xml_parse_error", "source": str(xml_path), "error": str(exc)})
        write_json(out_path, {"source": str(xml_path), "sections": sections, "errors": errors})
        return 0, captions, errors

    counters: Counter[str] = Counter()
    for elem in root.iter():
        tag = local_name(elem.tag)
        if tag not in {"article-title", "abstract", "sec", "p", "table-wrap", "fig", "caption"}:
            continue
        text = text_of(elem)
        if not text:
            continue
        counters[tag] += 1
        locator = f"xml:{tag}:{counters[tag]}"
        item = {"locator": locator, "tag": tag, "text": text[:5000]}
        sections.append(item)
        if tag in {"fig", "caption", "table-wrap"}:
            captions.append(item)
    write_json(out_path, {"source": str(xml_path), "section_count": len(sections), "sections": sections, "errors": errors})
    return len(sections), captions, errors


def extract_pdf_text(pdf_path: Path, out_path: Path, errors: list[dict[str, Any]], label: str) -> int:
    if not pdf_path.exists():
        errors.append({"type": "missing_pdf", "source": str(pdf_path)})
        append_jsonl(out_path, [])
        return 0
    if not LOCAL_TOOLS["pdftotext"]:
        errors.append({"type": "missing_tool", "tool": "pdftotext", "source": str(pdf_path)})
        append_jsonl(out_path, [])
        return 0
    code, stdout, stderr = run_cmd([LOCAL_TOOLS["pdftotext"] or "pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), "-"], timeout=180)
    if code != 0:
        errors.append({"type": "pdf_text_failed", "source": str(pdf_path), "exit_code": code, "stderr": stderr[-2000:]})
        append_jsonl(out_path, [])
        return 0
    pages = stdout.split("\f")
    rows = []
    for index, page in enumerate(pages, start=1):
        text = page.strip()
        if text:
            rows.append({"locator": f"{label}:page={index}", "source": str(pdf_path), "page": index, "text": text})
    append_jsonl(out_path, rows)
    return len(rows)


def extract_doc_text(src: Path) -> tuple[str, list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    tool = LOCAL_TOOLS.get("antiword") or LOCAL_TOOLS.get("catdoc")
    if not tool:
        return "", [{"type": "missing_tool", "tool": "antiword_or_catdoc", "source": str(src)}]
    code, stdout, stderr = run_cmd([tool, str(src)], timeout=120)
    if code != 0:
        errors.append({"type": "doc_extract_failed", "source": str(src), "tool": tool, "exit_code": code, "stderr": stderr[-2000:]})
        return "", errors
    return stdout, errors


def extract_xls_text(src: Path) -> tuple[str, list[dict[str, Any]]]:
    tool = LOCAL_TOOLS.get("xls2csv")
    if not tool:
        return "", [{"type": "missing_tool", "tool": "xls2csv", "source": str(src)}]
    code, stdout, stderr = run_cmd([tool, str(src)], timeout=120)
    if code != 0:
        return "", [{"type": "xls_extract_failed", "source": str(src), "exit_code": code, "stderr": stderr[-2000:]}]
    return stdout, []


def read_xlsx_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    strings: list[str] = []
    for si in root.iter():
        if local_name(si.tag) != "si":
            continue
        strings.append(" ".join(" ".join(si.itertext()).split()))
    return strings


def extract_xlsx_tables(src: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tables: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(src) as zf:
            shared = read_xlsx_shared_strings(zf)
            sheet_names = [name for name in zf.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")]
            for sheet_index, name in enumerate(sheet_names, start=1):
                root = ET.fromstring(zf.read(name))
                rows: list[list[str]] = []
                for row in root.iter():
                    if local_name(row.tag) != "row":
                        continue
                    values: list[str] = []
                    for cell in row:
                        if local_name(cell.tag) != "c":
                            continue
                        cell_type = cell.attrib.get("t")
                        value = ""
                        for child in cell:
                            if local_name(child.tag) == "v":
                                value = child.text or ""
                                break
                        if cell_type == "s" and value.isdigit() and int(value) < len(shared):
                            value = shared[int(value)]
                        values.append(value)
                    if any(values):
                        rows.append(values)
                tables.append({"source": str(src), "sheet_index": sheet_index, "sheet_xml": name, "row_count": len(rows), "rows": rows})
    except Exception as exc:  # noqa: BLE001
        errors.append({"type": "xlsx_extract_failed", "source": str(src), "error": str(exc)})
    return tables, errors


def extract_supplementary(supp_dir: Path, packet: Path, errors: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    index: list[dict[str, Any]] = []
    text_rows: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    text_count = 0
    if not supp_dir.exists():
        write_json(packet / "extracted/supplementary_index.json", {"files": [], "note": "no supplementary directory staged"})
        append_jsonl(packet / "extracted/supplementary_text.jsonl", [])
        write_json(packet / "extracted/supplementary_tables.json", {"tables": []})
        return index, tables, text_count

    for src in sorted(path for path in supp_dir.rglob("*") if path.is_file()):
        rel = safe_rel(src, supp_dir)
        suffix = src.suffix.lower()
        record = {"path": str(src), "relative_path": rel, "size_bytes": src.stat().st_size, "suffix": suffix}
        index.append(record)
        text = ""
        local_errors: list[dict[str, Any]] = []
        if suffix in TEXT_SUFFIXES:
            text = src.read_text(encoding="utf-8", errors="replace")
        elif suffix in PDF_SUFFIXES:
            out = packet / "extracted" / "ocr" / f"{src.stem}.pdf_text.jsonl"
            count = extract_pdf_text(src, out, errors, f"supp:{rel}")
            record["pdf_text_pages"] = count
            continue
        elif suffix in DOC_SUFFIXES:
            text, local_errors = extract_doc_text(src)
        elif suffix in XLS_SUFFIXES:
            text, local_errors = extract_xls_text(src)
        elif suffix in XLSX_SUFFIXES:
            xlsx_tables, local_errors = extract_xlsx_tables(src)
            tables.extend(xlsx_tables)
        else:
            record["extraction_status"] = "inventory_only"
        errors.extend(local_errors)
        if text.strip():
            text_count += 1
            text_rows.append({"locator": f"supp:{rel}", "source": str(src), "text": text})
            record["extraction_status"] = "text_extracted"
        elif local_errors:
            record["extraction_status"] = "extract_failed"
    write_json(packet / "extracted/supplementary_index.json", {"files": index})
    append_jsonl(packet / "extracted/supplementary_text.jsonl", text_rows)
    write_json(packet / "extracted/supplementary_tables.json", {"tables": tables})
    return index, tables, text_count


def archive_entries(src: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entries: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    suffixes = "".join(src.suffixes).lower()
    if src.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(src) as zf:
                for info in zf.infolist():
                    entries.append({"name": info.filename, "size": info.file_size, "compressed_size": info.compress_size})
            return entries, errors
        except Exception as exc:  # noqa: BLE001
            errors.append({"type": "zip_list_failed", "source": str(src), "error": str(exc)})
    if suffixes.endswith(".tar.gz") or src.suffix.lower() in {".tar", ".tgz"}:
        try:
            with tarfile.open(src) as tf:
                for member in tf.getmembers():
                    entries.append({"name": member.name, "size": member.size, "type": member.type.decode(errors="ignore") if isinstance(member.type, bytes) else str(member.type)})
            return entries, errors
        except Exception as exc:  # noqa: BLE001
            errors.append({"type": "tar_list_failed", "source": str(src), "error": str(exc)})
    seven_zip = LOCAL_TOOLS.get("seven_zip")
    if seven_zip and Path(seven_zip).exists():
        code, stdout, stderr = run_cmd([seven_zip, "l", "-slt", str(src)], timeout=120)
        if code == 0:
            for block in stdout.split("\n\n"):
                item: dict[str, Any] = {}
                for line in block.splitlines():
                    if " = " in line:
                        key, value = line.split(" = ", 1)
                        item[key.strip().lower().replace(" ", "_")] = value.strip()
                if item.get("path"):
                    entries.append(item)
        else:
            errors.append({"type": "seven_zip_list_failed", "source": str(src), "exit_code": code, "stderr": stderr[-2000:]})
    return entries, errors


def build_archive_manifest(source_dir: Path, packet: Path, errors: list[dict[str, Any]]) -> int:
    manifests: list[dict[str, Any]] = []
    for src in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        suffixes = "".join(src.suffixes).lower()
        if src.suffix.lower() not in ARCHIVE_SUFFIXES and not suffixes.endswith(".tar.gz"):
            continue
        entries, local_errors = archive_entries(src)
        errors.extend(local_errors)
        manifests.append({"source": str(src), "entry_count": len(entries), "entries": entries[:500]})
    write_json(packet / "extracted/archive_manifest.json", {"archives": manifests})
    return len(manifests)


def choose_landed_file(landed_root: Path, subdir: str, suffixes: tuple[str, ...]) -> Path | None:
    base = landed_root / subdir
    if not base.exists():
        return None
    candidates = [path for path in base.rglob("*") if path.is_file() and path.suffix.lower() in suffixes]
    if not candidates:
        return None
    def score(path: Path) -> tuple[int, int, str]:
        name = path.name.lower()
        preferred = 0
        if name.startswith("local-dbaasp"):
            preferred = 4
        elif name.startswith("local-apd6"):
            preferred = 3
        elif name.startswith("local-"):
            preferred = 2
        elif name.startswith("remote-"):
            preferred = 1
        return (preferred, path.stat().st_size, name)
    return sorted(candidates, key=score, reverse=True)[0]


def extract_package_supplements(landed_root: Path | None, dest: Path, errors: list[dict[str, Any]]) -> int:
    """Extract supplementary-like members from landed OA packages into packet raw."""
    if not landed_root or not (landed_root / "package").exists():
        return 0
    dest.mkdir(parents=True, exist_ok=True)
    extracted = 0
    seen_names: set[str] = set()
    for package in sorted((landed_root / "package").glob("*")):
        suffixes = "".join(package.suffixes).lower()
        if not (suffixes.endswith(".tar.gz") or package.suffix.lower() in {".tar", ".tgz"}):
            continue
        try:
            with tarfile.open(package) as tf:
                for member in tf.getmembers():
                    if not member.isfile():
                        continue
                    name = Path(member.name).name
                    lower = name.lower()
                    is_supp = (
                        "-s" in lower
                        or "supp" in lower
                        or lower.endswith((".doc", ".xls", ".xlsx"))
                    )
                    if not is_supp or lower.endswith((".nxml", ".xml")):
                        continue
                    target = dest / name
                    if name in seen_names and target.exists():
                        continue
                    src_fh = tf.extractfile(member)
                    if src_fh is None:
                        continue
                    with target.open("wb") as out:
                        shutil.copyfileobj(src_fh, out)
                    seen_names.add(name)
                    extracted += 1
        except Exception as exc:  # noqa: BLE001 - record package extraction gap
            errors.append({"type": "package_supplement_extract_failed", "source": str(package), "error": str(exc)})
    return extracted


def identifiers_from_sources(paper_root: Path, landed_root: Path | None = None) -> dict[str, str]:
    out: dict[str, str] = {}
    paths = [
        paper_root / "source/paper_meta.json",
        paper_root / "work/database_linkage/source_record_links.json",
    ]
    if landed_root:
        paths.append(landed_root / "metadata.json")
    for path in paths:
        if not path.exists():
            continue
        try:
            data = read_json(path)
        except Exception:
            continue
        candidates = [data]
        if isinstance(data, dict) and isinstance(data.get("paper_identifiers"), dict):
            candidates.append(data["paper_identifiers"])
        for obj in candidates:
            if not isinstance(obj, dict):
                continue
            for key in ("doi", "pmid", "pmcid", "title"):
                value = obj.get(key) or obj.get(f"canonical_{key}")
                if value and key not in out:
                    out[key] = str(value).strip()
    return out


def norm(value: str) -> str:
    return " ".join(str(value or "").lower().replace("https://doi.org/", "").split())


def row_matches(row: dict[str, str], identifiers: dict[str, str]) -> bool:
    doi = norm(identifiers.get("doi", ""))
    pmid = norm(identifiers.get("pmid", ""))
    pmcid = norm(identifiers.get("pmcid", ""))
    title = norm(identifiers.get("title", ""))
    for key, value in row.items():
        key_l = key.lower()
        value_n = norm(value)
        if not value_n:
            continue
        if doi and ("doi" in key_l or "reference" in key_l) and doi in value_n:
            return True
        if pmid and ("pmid" in key_l or "pubmed" in key_l or "reference" in key_l) and pmid in value_n:
            return True
        if pmcid and ("pmcid" in key_l or "article_id" in key_l or "reference" in key_l) and pmcid in value_n:
            return True
        if title and ("title" in key_l or "reference" in key_l) and (title == value_n or title[:80] in value_n):
            return True
    return False


def snapshot_csv_rows(csv_path: Path, out_path: Path, identifiers: dict[str, str], sequence_keys: set[str] | None = None) -> tuple[int, set[str]]:
    rows: list[dict[str, Any]] = []
    found_keys: set[str] = set()
    if not csv_path.exists():
        append_jsonl(out_path, [])
        return 0, found_keys
    with csv_path.open(newline="", encoding="utf-8", errors="replace") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = row.get("sequence_key") or ""
            matched = row_matches(row, identifiers) or (bool(sequence_keys) and key in (sequence_keys or set()))
            if not matched:
                continue
            rows.append(dict(row))
            if key:
                found_keys.add(key)
    append_jsonl(out_path, rows)
    return len(rows), found_keys


def build_database_snapshot(packet: Path, paper_root: Path, identifiers: dict[str, str], errors: list[dict[str, Any]]) -> dict[str, Any]:
    db_dir = packet / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    sequence_keys: set[str] = set()

    linkage = paper_root / "work/database_linkage/source_record_links.json"
    if linkage.exists():
        shutil.copy2(linkage, db_dir / "source_record_links.json")
    else:
        errors.append({"type": "missing_database_linkage", "source": str(linkage)})

    lit_path = CORPUS_OUTPUT / "literature/sequence_literature_links.csv"
    counts["linked_literature_records"], sequence_keys = snapshot_csv_rows(lit_path, db_dir / "linked_literature_records.jsonl", identifiers)
    counts["linked_sequence_records"], _ = snapshot_csv_rows(CORPUS_OUTPUT / "sequences/all_sequences.csv", db_dir / "linked_sequence_records.jsonl", identifiers, sequence_keys)

    experiment_files = {
        "linked_experiment_records": CORPUS_OUTPUT / "experiments/all_experimental_records.csv",
        "linked_dbaasp_assay_records": CORPUS_OUTPUT / "experiments/dbaasp_assay_records.csv",
        "linked_apd6_activity_records": CORPUS_OUTPUT / "experiments/apd6_activity_text_records.csv",
        "linked_dramp_activity_records": CORPUS_OUTPUT / "experiments/dramp_activity_text_records.csv",
    }
    for name, path in experiment_files.items():
        counts[name], extra_keys = snapshot_csv_rows(path, db_dir / f"{name}.jsonl", identifiers, sequence_keys)
        sequence_keys |= extra_keys

    manifest = {
        "generated_at": utc_now(),
        "identifiers": identifiers,
        "corpus_output_root": str(CORPUS_OUTPUT),
        "row_counts": counts,
        "sequence_key_count": len(sequence_keys),
        "source_record_links_present": linkage.exists(),
    }
    write_json(db_dir / "database_source_manifest.json", manifest)
    return manifest


def copy_if_exists(src: Path, dest: Path) -> bool:
    if not src.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def copy_analysis_and_final(packet: Path, paper_root: Path) -> dict[str, Any]:
    mapping = {
        "analysis/database_record_audit.json": paper_root / "work/database_record_audit/record_identity_audit.json",
        "analysis/activity_toxicity_evidence.json": paper_root / "work/activity_evidence/activity_records.json",
        "analysis/mechanism_evidence.json": paper_root / "work/mechanism_ontology/mechanism_evidence.json",
        "analysis/adjudication_report.json": paper_root / "work/review/adjudication_report.json",
        "final/database_record_verification.json": paper_root / "final/database_record_verification.json",
        "final/activity_toxicity_evidence.json": paper_root / "final/activity_toxicity_evidence.json",
        "final/mechanism_evidence.json": paper_root / "final/mechanism_ontology_record.json",
        "final/final_conclusion.json": paper_root / "final/review_report.json",
        "final/review_report.json": paper_root / "final/review_report.json",
    }
    present: dict[str, bool] = {}
    for rel, src in mapping.items():
        present[rel] = copy_if_exists(src, packet / rel)
    status = "analysis_artifacts_present" if all(present[f"final/{name}"] for name in ["database_record_verification.json", "activity_toxicity_evidence.json", "mechanism_evidence.json", "review_report.json"]) else "analysis_blocked"
    write_json(packet / "analysis/analysis_status.json", {"status": status, "generated_at": utc_now(), "copied_outputs": present})
    return {"analysis_status": status, "copied_outputs": present}


def build_packet(repo_root: Path, paper_id: str, packet_root: Path, source_pool_root: Path | None, raw_mode: str) -> dict[str, Any]:
    paper_root = repo_root / "papers" / paper_id
    packet = packet_root / paper_id
    if packet.exists():
        shutil.rmtree(packet)
    for rel in ["raw", "extracted/ocr", "database", "locators", "extraction", "analysis", "final", "rework"]:
        (packet / rel).mkdir(parents=True, exist_ok=True)

    errors: list[dict[str, Any]] = []
    landed = source_pool_root / paper_id if source_pool_root else None
    source = paper_root / "source"
    raw_source_root = landed if landed and landed.exists() else source
    landed_xml = choose_landed_file(landed, "xml", (".xml", ".nxml")) if landed and landed.exists() else None
    landed_pdf = choose_landed_file(landed, "pdf", (".pdf",)) if landed and landed.exists() else None
    landed_metadata = landed / "metadata.json" if landed and landed.exists() else None
    landed_manifest = landed / "asset_manifest.csv" if landed and landed.exists() else None
    landed_package = choose_landed_file(landed, "package", (".gz", ".tgz", ".tar", ".zip")) if landed and landed.exists() else None
    raw_sources = {
        "paper.xml": landed_xml or (source / "paper.xml"),
        "paper.pdf": landed_pdf or (source / "paper.pdf"),
        "paper_meta.json": landed_metadata or (source / "paper_meta.json"),
        "asset_manifest.csv": landed_manifest or (source / "asset_manifest.csv"),
        "pmc_oa_package.tar.gz": landed_package or (source / "pmc_oa_package.tar.gz"),
    }
    for name, src in raw_sources.items():
        materialize(src, packet / "raw" / name, raw_mode, errors)
    extracted_from_package = extract_package_supplements(landed if landed and landed.exists() else None, packet / "raw/supplementary_original", errors)
    if not extracted_from_package and (source / "supplementary").exists():
        materialize(source / "supplementary", packet / "raw/supplementary_original", raw_mode, errors)
    if landed and (landed / "package").exists():
        materialize(landed / "package", packet / "raw/oa_package", raw_mode, errors)

    packet_xml = raw_sources["paper.xml"]
    packet_pdf = raw_sources["paper.pdf"]
    xml_count, captions, xml_errors = extract_xml_sections(packet_xml, packet / "extracted/xml_sections.json")
    errors.extend(xml_errors)
    write_json(packet / "extracted/figure_captions.json", {"captions": captions})
    pdf_pages = extract_pdf_text(packet_pdf, packet / "extracted/pdf_text.jsonl", errors, "pdf")
    packet_supp = packet / "raw/supplementary_original"
    supp_index, supp_tables, supp_text_count = extract_supplementary(packet_supp, packet, errors)
    archive_count = build_archive_manifest(raw_source_root, packet, errors)

    table_evidence = paper_root / "work/table_evidence/evidence.json"
    if table_evidence.exists():
        copy_if_exists(table_evidence, packet / "extracted/pdf_tables.json")
    elif not (packet / "extracted/pdf_tables.json").exists():
        write_json(packet / "extracted/pdf_tables.json", {"tables": [], "note": "no existing table evidence artifact"})

    identifiers = identifiers_from_sources(paper_root, landed if landed and landed.exists() else None)
    database_manifest = build_database_snapshot(packet, paper_root, identifiers, errors)
    analysis = copy_analysis_and_final(packet, paper_root)

    locator_rows: list[dict[str, Any]] = []
    locator_rows.extend({"locator": item["locator"], "source": "xml_sections"} for item in read_json(packet / "extracted/xml_sections.json").get("sections", []))
    locator_rows.extend({"locator": f"pdf:page={idx}", "source": "pdf_text"} for idx in range(1, pdf_pages + 1))
    for item in supp_index:
        if item.get("extraction_status") == "text_extracted":
            locator_rows.append({"locator": f"supp:{item['relative_path']}", "source": "supplementary_text"})
    write_json(packet / "locators/locator_index.json", {"locator_count": len(locator_rows), "locators": locator_rows})
    write_json(packet / "locators/citation_map.json", {"note": "pilot packet locator map; final scientific citation mapping remains analysis/adjudication owned"})

    blocking_errors = [err for err in errors if err.get("type") in {"missing_xml", "missing_pdf", "missing_raw_source"} and str(err.get("source", "")).endswith(("paper.xml", "paper.pdf"))]
    material_status = "material_blocked_missing_source" if blocking_errors else ("material_extracted_with_gaps" if errors else "material_extracted_complete")
    extraction_status = {
        "paper_id": paper_id,
        "status": material_status,
        "generated_at": utc_now(),
        "xml_section_count": xml_count,
        "pdf_text_page_count": pdf_pages,
        "supplementary_file_count": len(supp_index),
        "supplementary_text_item_count": supp_text_count,
        "supplementary_table_count": len(supp_tables),
        "archive_count": archive_count,
        "error_count": len(errors),
    }
    write_json(packet / "extraction/extraction_status.json", extraction_status)
    write_json(packet / "extraction/extraction_quality_report.json", {"status": material_status, "errors": errors[:100], "tool_registry": LOCAL_TOOLS})
    append_jsonl(packet / "extraction/extraction_errors.jsonl", errors)
    generated_at = utc_now()
    rework_tickets = material_rework_tickets(paper_id, errors, generated_at)
    append_jsonl(packet / "rework/rework_requests.jsonl", rework_tickets)
    append_jsonl(packet / "rework/rework_responses.jsonl", [])

    manifest = {
        "paper_id": paper_id,
        "packet_version": 1,
        "generated_at": generated_at,
        "packet_root": str(packet),
        "repo_paper_root": str(paper_root),
        "source_pool_root": str(landed) if landed else None,
        "raw_source_root": str(raw_source_root),
        "raw_source_policy": "prefer_landed_assets_over_staged_papers",
        "raw_mode": raw_mode,
        "identifiers": identifiers,
        "material_queue_status": material_status,
        "analysis_queue_status": analysis["analysis_status"],
        "database_snapshot": database_manifest,
        "locator_index_path": "locators/locator_index.json",
        "open_rework_ticket_ids": [ticket["ticket_id"] for ticket in rework_tickets],
        "known_missing_or_blocked_materials": errors,
        "legacy_path_mapping": {
            "source": str(paper_root / "source"),
            "work": str(paper_root / "work"),
            "final": str(paper_root / "final"),
        },
    }
    write_json(packet / "packet_manifest.json", manifest)
    return {
        "paper_id": paper_id,
        "packet_root": str(packet),
        "material_status": material_status,
        "analysis_status": analysis["analysis_status"],
        "error_count": len(errors),
        "locator_count": len(locator_rows),
        "database_row_counts": database_manifest["row_counts"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build two-queue packet directories for a manifest pilot.")
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--packet-root", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--raw-mode", choices=["symlink", "copy", "manifest-only"], default="symlink")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest if args.manifest.is_absolute() else (Path.cwd() / args.manifest).resolve()
    manifest = read_json(manifest_path)
    paper_ids = [str(item) for item in manifest.get("paper_ids", [])]
    if args.limit:
        paper_ids = paper_ids[: args.limit]
    packet_root = args.packet_root if args.packet_root.is_absolute() else (Path.cwd() / args.packet_root).resolve()
    packet_root.mkdir(parents=True, exist_ok=True)
    source_pool_root = Path(manifest["source_pool_root"]) if manifest.get("source_pool_root") else None

    results = [build_packet(repo_root, pid, packet_root, source_pool_root, args.raw_mode) for pid in paper_ids]
    summary = {
        "generated_at": utc_now(),
        "manifest": str(manifest_path),
        "packet_root": str(packet_root),
        "paper_count": len(results),
        "raw_mode": args.raw_mode,
        "material_status_counts": dict(Counter(item["material_status"] for item in results)),
        "analysis_status_counts": dict(Counter(item["analysis_status"] for item in results)),
        "results": results,
    }
    write_json(packet_root / "two_queue_packet_build_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
