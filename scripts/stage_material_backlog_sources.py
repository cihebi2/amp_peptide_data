#!/usr/bin/env python3
"""Stage recoverable backlog supplementary sources into paper packets.

This helper consumes the material backlog audit output. It copies already local
alternate-identifier assets, downloads direct supplementary URLs explicitly
listed in source XML or rework tickets, and refreshes packet supplementary
indexes/text/tables. It does not update final review status or mark papers
publication-grade.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "reports" / "nar_resource_freeze_v1" / "needs_targeted_rework_work"
DEFAULT_AUDIT = WORK / "material_backlog_audit_latest.json"
DEFAULT_OUT = WORK / "material_source_staging_latest.json"

SPRINGER_DOI_PREFIX = "10.1038/"
XLS_NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
DOCX_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
STAGEABLE_EXTS = {".docx", ".xlsx", ".pdf", ".zip", ".mp4", ".tar", ".tgz", ".gz", ".tif", ".tiff", ".jpg", ".png", ".gif"}
PRIMARY_PAPER_NAMES = {"paper.pdf", "paper.xml"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except Exception:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_copy(src: Path, dst: Path) -> dict[str, Any]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    action = "copied"
    if dst.exists() and src.exists() and sha256(dst) == sha256(src):
        action = "already_present"
    else:
        shutil.copy2(src, dst)
    return {
        "action": action,
        "source": str(src),
        "target": str(dst),
        "size": dst.stat().st_size if dst.exists() else None,
        "sha256": sha256(dst) if dst.exists() else "",
    }


def download_url(url: str, dst: Path, timeout: int = 60) -> dict[str, Any]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size > 0:
        return {
            "action": "already_present",
            "url": url,
            "target": str(dst),
            "size": dst.stat().st_size,
            "sha256": sha256(dst),
        }
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = resp.read()
        dst.write_bytes(data)
        return {
            "action": "downloaded",
            "url": url,
            "target": str(dst),
            "size": dst.stat().st_size,
            "sha256": sha256(dst),
        }
    except Exception as exc:
        return {"action": "download_failed", "url": url, "target": str(dst), "error": repr(exc)}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def xml_text(element: ET.Element) -> str:
    return " ".join(part.strip() for part in element.itertext() if part and part.strip())


def parse_docx(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    text_records: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(path) as archive:
            doc = ET.fromstring(archive.read("word/document.xml"))
    except Exception as exc:
        return ([{"asset_type": "docx", "source_path": str(path), "status": "parse_failed", "error": repr(exc)}], tables)

    paragraphs: list[str] = []
    for para in doc.findall(".//w:p", DOCX_NS):
        text = xml_text(para)
        if text:
            paragraphs.append(text)
    if paragraphs:
        text_records.append(
            {
                "asset_type": "docx",
                "source_path": str(path),
                "status": "parsed_text",
                "paragraph_count": len(paragraphs),
                "text": "\n".join(paragraphs),
            }
        )

    for table_index, table in enumerate(doc.findall(".//w:tbl", DOCX_NS), start=1):
        rows: list[list[str]] = []
        for tr in table.findall(".//w:tr", DOCX_NS):
            cells = [xml_text(tc) for tc in tr.findall("./w:tc", DOCX_NS)]
            if any(cells):
                rows.append(cells)
        if rows:
            tables.append(
                {
                    "asset_type": "docx",
                    "source_path": str(path),
                    "table_id": f"{path.name}::table_{table_index}",
                    "row_count": len(rows),
                    "rows": rows,
                }
            )
    return text_records, tables


def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except Exception:
        return []
    strings: list[str] = []
    for si in root.findall(".//main:si", XLS_NS):
        strings.append(xml_text(si))
    return strings


def cell_value(cell: ET.Element, strings: list[str]) -> str:
    value = cell.find("main:v", XLS_NS)
    if value is None or value.text is None:
        inline = cell.find(".//main:t", XLS_NS)
        return inline.text.strip() if inline is not None and inline.text else ""
    raw = value.text.strip()
    if cell.attrib.get("t") == "s":
        try:
            return strings[int(raw)]
        except Exception:
            return raw
    return raw


def parse_xlsx(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tables: list[dict[str, Any]] = []
    text_records: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(path) as archive:
            strings = shared_strings(archive)
            sheet_names = [n for n in archive.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
            for sheet_index, name in enumerate(sorted(sheet_names), start=1):
                root = ET.fromstring(archive.read(name))
                rows: list[list[str]] = []
                for row in root.findall(".//main:sheetData/main:row", XLS_NS):
                    cells = [cell_value(cell, strings) for cell in row.findall("main:c", XLS_NS)]
                    if any(cells):
                        rows.append(cells)
                if rows:
                    tables.append(
                        {
                            "asset_type": "xlsx",
                            "source_path": str(path),
                            "table_id": f"{path.name}::sheet_{sheet_index}",
                            "row_count": len(rows),
                            "rows": rows,
                        }
                    )
            text_records.append(
                {
                    "asset_type": "xlsx",
                    "source_path": str(path),
                    "status": "parsed_tables",
                    "sheet_count": len(sheet_names),
                    "table_count": len(tables),
                }
            )
    except Exception as exc:
        text_records.append({"asset_type": "xlsx", "source_path": str(path), "status": "parse_failed", "error": repr(exc)})
    return text_records, tables


def parse_pdf(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        proc = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return (
                [
                    {
                        "asset_type": "pdf",
                        "source_path": str(path),
                        "status": "pdftotext",
                        "text": proc.stdout,
                    }
                ],
                [],
            )
        return (
            [
                {
                    "asset_type": "pdf",
                    "source_path": str(path),
                    "status": "pdftotext_failed",
                    "stderr": proc.stderr[-1000:],
                }
            ],
            [],
        )
    except Exception as exc:
        return ([{"asset_type": "pdf", "source_path": str(path), "status": "parse_failed", "error": repr(exc)}], [])


def index_binary(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [
            {
                "asset_type": path.suffix.lower().lstrip(".") or "binary",
                "source_path": str(path),
                "status": "indexed_only",
                "size": path.stat().st_size if path.exists() else None,
                "sha256": sha256(path) if path.exists() else "",
            }
        ],
        [],
    )


def parse_asset(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return parse_docx(path)
    if suffix == ".xlsx":
        return parse_xlsx(path)
    if suffix == ".pdf":
        return parse_pdf(path)
    return index_binary(path)


def update_supplementary_index(packet: Path, staged_assets: list[Path]) -> None:
    path = packet / "extracted" / "supplementary_index.json"
    data = load_json(path)
    if not isinstance(data, dict):
        data = {"paper_id": packet.name, "supplementary_assets": []}
    assets = data.setdefault("supplementary_assets", [])
    seen = {str(item.get("path")) for item in assets if isinstance(item, dict)}
    for asset in staged_assets:
        if str(asset) in seen:
            continue
        assets.append(
            {
                "name": asset.name,
                "path": str(asset),
                "suffix": asset.suffix.lower(),
                "size": asset.stat().st_size if asset.exists() else None,
                "sha256": sha256(asset) if asset.exists() else "",
                "staged_by": "stage_material_backlog_sources.py",
            }
        )
    data["updated_at"] = utc_now()
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, data)


def update_supplementary_text_and_tables(packet: Path, text_records: list[dict[str, Any]], tables: list[dict[str, Any]]) -> None:
    text_path = packet / "extracted" / "supplementary_text.jsonl"
    existing_text = read_jsonl(text_path)
    existing_keys = {(row.get("source_path"), row.get("status")) for row in existing_text}
    for record in text_records:
        record.setdefault("paper_id", packet.name)
        record.setdefault("staged_by", "stage_material_backlog_sources.py")
        key = (record.get("source_path"), record.get("status"))
        if key not in existing_keys:
            existing_text.append(record)
            existing_keys.add(key)
    write_jsonl(text_path, existing_text)

    tables_path = packet / "extracted" / "supplementary_tables.json"
    table_data = load_json(tables_path)
    if not isinstance(table_data, dict):
        table_data = {"paper_id": packet.name, "tables": []}
    existing_tables = table_data.setdefault("tables", [])
    seen_tables = {item.get("table_id") for item in existing_tables if isinstance(item, dict)}
    for table in tables:
        table.setdefault("paper_id", packet.name)
        table.setdefault("staged_by", "stage_material_backlog_sources.py")
        if table.get("table_id") not in seen_tables:
            existing_tables.append(table)
            seen_tables.add(table.get("table_id"))
    table_data["table_count"] = len(existing_tables)
    table_data["updated_at"] = utc_now()
    write_json(tables_path, table_data)


def extract_tar_package(package: Path, out_dir: Path) -> list[dict[str, Any]]:
    members: list[dict[str, Any]] = []
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(package) as tar:
            tar.extractall(out_dir)
            for member in tar.getmembers():
                members.append({"package": str(package), "member": member.name, "size": member.size, "type": "directory" if member.isdir() else "file"})
    except Exception as exc:
        members.append({"package": str(package), "error": repr(exc)})
    return members


def update_archive_manifest(packet: Path, new_members: list[dict[str, Any]]) -> None:
    if not new_members:
        return
    path = packet / "extracted" / "archive_manifest.json"
    data = load_json(path)
    if not isinstance(data, dict):
        data = {"paper_id": packet.name, "archives": []}
    archives = data.setdefault("archives", [])
    seen = {(item.get("package"), item.get("member")) for item in archives if isinstance(item, dict)}
    for member in new_members:
        key = (member.get("package"), member.get("member"))
        if key not in seen:
            archives.append(member)
            seen.add(key)
    data["updated_at"] = utc_now()
    write_json(path, data)


def write_staging_status(packet: Path, status: dict[str, Any]) -> None:
    path = packet / "extraction" / "material_staging_status.json"
    write_json(path, status)


def prior_material_change_at(packet: Path) -> str:
    prior = load_json(packet / "extraction" / "material_staging_status.json")
    if not isinstance(prior, dict):
        return ""
    return str(prior.get("material_change_at") or prior.get("generated_at") or "")


def collect_existing_local_assets(row: dict[str, Any]) -> list[Path]:
    assets: list[Path] = []
    roots = [Path(p) for p in row.get("alternate_identifier_roots") or []]
    stageable_names = set(row.get("stageable_asset_names") or [])
    for root in roots:
        if not root.exists():
            continue
        for child in (root / "supplementary").glob("*"):
            if child.is_file() and (not stageable_names or child.name in stageable_names):
                assets.append(child)
        for child in (root / "package").glob("*"):
            if child.is_file() and (not stageable_names or child.name in stageable_names):
                assets.append(child)
    return sorted(set(assets))


def extract_literal_urls(*values: Any) -> list[str]:
    urls: list[str] = []
    url_re = re.compile(r"https?://[^\s;,\]\)\"']+")

    def visit(value: Any) -> None:
        if isinstance(value, str):
            urls.extend(url_re.findall(value))
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            for item in value.values():
                visit(item)

    for value in values:
        visit(value)
    clean: list[str] = []
    seen: set[str] = set()
    for url in urls:
        url = url.rstrip(".")
        if url not in seen:
            clean.append(url)
            seen.add(url)
    return clean


def extract_existing_paths(*values: Any) -> list[Path]:
    candidates: list[Path] = []

    def maybe_add(text: str) -> None:
        for token in re.split(r"[\s,;\]\[\"']+", text):
            token = token.strip().rstrip(":.")
            if not token:
                continue
            if token.startswith("/"):
                path = Path(token)
            elif token.startswith(("paper_packets/", "papers/", "reports/", "rework_context/")):
                path = ROOT / token
            else:
                continue
            if path.name.lower() in PRIMARY_PAPER_NAMES:
                continue
            if "/raw/paper." in str(path) or "/source/paper." in str(path):
                continue
            if path.exists() and path.is_file() and path.suffix.lower() in STAGEABLE_EXTS:
                candidates.append(path)

    def visit(value: Any) -> None:
        if isinstance(value, str):
            maybe_add(value)
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            for item in value.values():
                visit(item)

    for value in values:
        visit(value)

    seen: set[str] = set()
    out: list[Path] = []
    for path in candidates:
        key = str(path)
        if key not in seen:
            out.append(path)
            seen.add(key)
    return out


def springer_urls_from_xml(paper_id: str, doi: str) -> list[str]:
    if not doi.startswith(SPRINGER_DOI_PREFIX):
        return []
    xml_paths = [ROOT / "papers" / paper_id / "source" / "paper.xml", ROOT / "paper_packets" / paper_id / "raw" / "paper.xml"]
    hrefs: set[str] = set()
    for path in xml_paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        hrefs.update(re.findall(r'xlink:href="([^"]+MOESM[^"]+)"', text))
    encoded_doi = doi.replace("/", "%2F")
    return [
        f"https://static-content.springer.com/esm/art%3A{encoded_doi}/MediaObjects/{href}"
        for href in sorted(hrefs)
        if href.lower().endswith((".pdf", ".xlsx", ".docx", ".mp4", ".zip"))
    ]


def paper_doi(row: dict[str, Any]) -> str:
    packet = ROOT / "paper_packets" / row["paper_id"] / "packet_manifest.json"
    manifest = load_json(packet)
    if isinstance(manifest, dict) and manifest.get("doi"):
        return str(manifest["doi"])
    pid = row["paper_id"]
    if pid.startswith("doi__"):
        return pid.removeprefix("doi__").replace("_", "/")
    return ""


def destination_for(packet: Path, asset_name: str, source: str = "") -> Path:
    lower = asset_name.lower()
    if lower.endswith((".tar.gz", ".tgz", ".tar")):
        return packet / "raw" / "oa_package" / asset_name
    if lower.endswith((".pdf", ".docx", ".xlsx", ".zip", ".mp4", ".csv", ".txt", ".tif", ".tiff", ".jpg", ".png", ".gif")):
        return packet / "raw" / "supplementary_original" / asset_name
    if "package" in source:
        return packet / "raw" / "oa_package" / asset_name
    return packet / "raw" / "supplementary_original" / asset_name


def stage_one(row: dict[str, Any], download: bool) -> dict[str, Any]:
    paper_id = row["paper_id"]
    packet = ROOT / "paper_packets" / paper_id
    packet.mkdir(parents=True, exist_ok=True)
    review = load_json(ROOT / "papers" / paper_id / "final" / "review_report.json") or {}
    feedback = load_json(ROOT / "papers" / paper_id / "work" / "review" / "quality_feedback.json") or {}

    doi = paper_doi(row)
    local_assets = collect_existing_local_assets(row)
    local_assets.extend(extract_existing_paths(review.get("rework_targets"), feedback.get("rework_targets")))
    local_assets = sorted({path for path in local_assets if path.name.lower() not in PRIMARY_PAPER_NAMES})
    urls = extract_literal_urls(review.get("rework_targets"), feedback.get("rework_targets"))
    urls.extend(url for url in springer_urls_from_xml(paper_id, doi) if url not in urls)

    actions: list[dict[str, Any]] = []
    staged_assets: list[Path] = []
    archive_members: list[dict[str, Any]] = []
    text_records: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []

    for src in local_assets:
        dst = destination_for(packet, src.name, str(src.parent))
        action = safe_copy(src, dst)
        actions.append(action)
        if dst.exists():
            staged_assets.append(dst)

    if download:
        for url in urls:
            name = urllib.request.urlparse(url).path.rsplit("/", 1)[-1]
            if not name:
                continue
            dst = destination_for(packet, name, url)
            action = download_url(url, dst)
            actions.append(action)
            if action.get("action") in {"downloaded", "already_present"} and dst.exists():
                staged_assets.append(dst)
    else:
        for url in urls:
            actions.append({"action": "download_skipped", "url": url})

    for asset in sorted(set(staged_assets)):
        if asset.name.lower().endswith((".tar.gz", ".tgz", ".tar")):
            out_dir = packet / "extracted" / "oa_package" / asset.name.replace(".tar.gz", "").replace(".tgz", "").replace(".tar", "")
            archive_members.extend(extract_tar_package(asset, out_dir))
            for nested in out_dir.rglob("*"):
                if nested.is_file() and nested.suffix.lower() in {".docx", ".xlsx", ".pdf"}:
                    records, parsed_tables = parse_asset(nested)
                    text_records.extend(records)
                    tables.extend(parsed_tables)
        else:
            records, parsed_tables = parse_asset(asset)
            text_records.extend(records)
            tables.extend(parsed_tables)

    update_supplementary_index(packet, sorted(set(staged_assets)))
    update_supplementary_text_and_tables(packet, text_records, tables)
    update_archive_manifest(packet, archive_members)

    success_actions = [a for a in actions if a.get("action") in {"copied", "downloaded", "already_present"}]
    change_actions = [a for a in actions if a.get("action") in {"copied", "downloaded"}]
    generated_at = utc_now()
    material_change_at = generated_at if change_actions else prior_material_change_at(packet)
    status = {
        "paper_id": paper_id,
        "generated_at": generated_at,
        "material_change_at": material_change_at,
        "material_changed": bool(change_actions),
        "status": "material_staged" if change_actions else ("material_already_staged" if success_actions else "no_new_material_staged"),
        "publication_grade_changed": False,
        "owner_worker_launch_allowed": False,
        "actions": actions,
        "new_material_action_count": len(change_actions),
        "already_present_action_count": sum(1 for a in actions if a.get("action") == "already_present"),
        "staged_asset_count": len(set(staged_assets)),
        "text_record_count_added_or_indexed": len(text_records),
        "table_count_added_or_indexed": len(tables),
        "archive_member_count_added_or_indexed": len(archive_members),
        "next_gate": "rerun material backlog audit and triage; only then consider policy-safe owner-worker analysis for newly ready packets",
    }
    write_staging_status(packet, status)
    return status


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "paper_id",
        "status",
        "staged_asset_count",
        "text_record_count_added_or_indexed",
        "table_count_added_or_indexed",
        "archive_member_count_added_or_indexed",
        "owner_worker_launch_allowed",
        "publication_grade_changed",
        "next_gate",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def render_md(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Material Source Staging Report",
        "",
        f"- generated_at: `{summary['generated_at']}`",
        f"- completion_claim: `{summary['completion_claim']}`",
        f"- processed_papers: `{summary['processed_papers']}`",
        f"- status_counts: `{json.dumps(summary['status_counts'], ensure_ascii=False, sort_keys=True)}`",
        "",
        "This report records material staging only. Final review status and publication-grade decisions remain unchanged.",
        "",
    ]
    for row in rows:
        lines.append(
            "- `{paper_id}` | `{status}` | assets={assets} tables={tables} text_records={texts}".format(
                paper_id=row["paper_id"],
                status=row["status"],
                assets=row["staged_asset_count"],
                tables=row["table_count_added_or_indexed"],
                texts=row["text_record_count_added_or_indexed"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--download", action="store_true", help="Download direct supplementary URLs found in XML/tickets.")
    parser.add_argument(
        "--include-buckets",
        default="source_staging_candidate",
        help="Comma-separated audit buckets to stage.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = load_json(args.audit) or {}
    buckets = {item.strip() for item in args.include_buckets.split(",") if item.strip()}
    candidate_rows = [row for row in audit.get("rows", []) if row.get("audit_bucket") in buckets]
    results = [stage_one(row, args.download) for row in candidate_rows]
    summary = {
        "generated_at": utc_now(),
        "completion_claim": "material_staging_only_not_publication_grade_acceptance",
        "input_audit": str(args.audit),
        "processed_papers": len(results),
        "download_enabled": bool(args.download),
        "status_counts": dict(Counter(row["status"] for row in results)),
        "owner_worker_launch_allowed": False,
        "publication_grade_changed": False,
        "outputs": {
            "json": str(args.out),
            "csv": str(args.out.with_suffix(".csv")),
            "md": str(args.out.with_suffix(".md")),
        },
    }
    write_json(args.out, {"summary": summary, "rows": results})
    write_csv(args.out.with_suffix(".csv"), results)
    args.out.with_suffix(".md").write_text(render_md(summary, results), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
