#!/usr/bin/env python3
"""Audit the material/digitization backlog without promoting papers to review.

The script inspects the current needs-targeted material backlog, local paper
packets, landed/downloaded assets, and review feedback. It writes evidence
manifests that decide which papers need material staging, manual digitization,
or should remain a documented non-publication-grade backlog.
"""

from __future__ import annotations

import argparse
import csv
import json
import mimetypes
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "reports" / "nar_resource_freeze_v1"
WORK = FREEZE / "needs_targeted_rework_work"
DEFAULT_BACKLOG = WORK / "material_or_digitization_backlog_latest.csv"
DEFAULT_OUT_PREFIX = WORK / "material_backlog_audit_latest"
DEFAULT_LANDED = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers")
DEFAULT_DOWNLOADED = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/downloaded_assets/papers")

TEXT_EXTS = {".txt", ".csv", ".tsv", ".json", ".jsonl", ".xml", ".nxml", ".html", ".htm", ".xhtml"}
STRUCTURED_SUPP_EXTS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".tsv",
    ".txt",
    ".zip",
    ".rar",
    ".7z",
    ".gz",
    ".tar",
    ".xml",
    ".nxml",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".tif",
    ".tiff",
    ".ppt",
    ".pptx",
    ".pdb",
}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp", ".webp"}
ARCHIVE_EXTS = {".zip", ".rar", ".7z", ".gz", ".tar", ".tgz"}
OFFICE_EXTS = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}
FIGURE_KEYWORDS = ("figure", "fig_", "fig-", "g00", "_g0", "-g0", ".jpg", ".png", ".gif", ".tif")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def timestamp_after(later: Any, earlier: Any) -> bool:
    later_dt = parse_timestamp(later)
    earlier_dt = parse_timestamp(earlier)
    return later_dt is not None and earlier_dt is not None and later_dt > earlier_dt


def latest_repair_timestamp(staging: dict[str, Any]) -> str:
    values = [str(staging.get("material_change_at") or staging.get("generated_at") or "")]
    try:
        locator_count = int(staging.get("locator_index_repair_count") or 0)
    except (TypeError, ValueError):
        locator_count = 0
    if locator_count > 0:
        values.append(str(staging.get("locator_index_repair_at") or ""))
    parsed = [(parse_timestamp(value), value) for value in values if value]
    parsed = [(dt, value) for dt, value in parsed if dt is not None]
    if not parsed:
        return ""
    return max(parsed, key=lambda item: item[0])[1]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: flatten_cell(row.get(name, "")) for name in fieldnames})


def flatten_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return ";".join(str(x) for x in value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def list_files(path: Path) -> list[Path]:
    if not path.exists() or not path.is_dir():
        return []
    return sorted([p for p in path.rglob("*") if p.is_file()])


def file_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    try:
        head = path.read_bytes()[:4096]
    except Exception:
        head = b""
    lower = head.lower()
    if head.startswith(b"%PDF"):
        return "pdf"
    if head.startswith(b"PK\x03\x04"):
        if suffix in {".docx", ".xlsx", ".pptx"}:
            return suffix[1:]
        return "zip_like"
    if lower.lstrip().startswith((b"<!doctype html", b"<html")) or b"<html" in lower[:512]:
        return "html"
    if suffix in IMAGE_EXTS:
        return "image"
    if suffix in ARCHIVE_EXTS:
        return "archive"
    if suffix in OFFICE_EXTS:
        return suffix[1:]
    if suffix in {".xml", ".nxml"}:
        return "xml"
    if suffix in TEXT_EXTS or (mimetypes.guess_type(path.name)[0] or "").startswith("text/"):
        return "text"
    if not head:
        return "empty_or_unreadable"
    return "binary_or_unknown"


def parse_asset_counts(root: Path) -> dict[str, int]:
    counts = {
        "pdf": len(list_files(root / "pdf")),
        "xml": len([p for p in list_files(root / "xml") if p.suffix.lower() in {".xml", ".nxml"}]),
        "package": len(list_files(root / "package")),
        "supplementary": len(list_files(root / "supplementary")),
    }
    return counts


def collect_asset_details(root: Path) -> dict[str, Any]:
    folders = {
        "pdf": root / "pdf",
        "xml": root / "xml",
        "package": root / "package",
        "supplementary": root / "supplementary",
    }
    details: dict[str, Any] = {"root": str(root), "exists": root.exists(), "counts": {}, "files": {}}
    for label, folder in folders.items():
        files = list_files(folder)
        details["counts"][label] = len(files)
        details["files"][label] = [
            {
                "path": str(path),
                "name": path.name,
                "suffix": path.suffix.lower(),
                "size": path.stat().st_size if path.exists() else None,
                "kind": file_kind(path),
            }
            for path in files
        ]
    return details


def count_true_supplementary(files: list[dict[str, Any]]) -> tuple[int, int, int]:
    true_count = 0
    html_or_landing_count = 0
    unknown_count = 0
    for item in files:
        suffix = str(item.get("suffix") or "").lower()
        kind = str(item.get("kind") or "")
        name = str(item.get("name") or "").lower()
        if kind == "html" or suffix in {".html", ".htm", ".xhtml"}:
            html_or_landing_count += 1
        elif kind in {"pdf", "zip_like", "docx", "xlsx", "pptx", "archive", "image", "xml", "text"}:
            true_count += 1
        elif suffix in STRUCTURED_SUPP_EXTS:
            true_count += 1
        elif suffix == ".bin" and ("landing" in name or kind == "binary_or_unknown"):
            unknown_count += 1
        else:
            unknown_count += 1
    return true_count, html_or_landing_count, unknown_count


def packet_staging_status(packet: Path) -> dict[str, Any]:
    data = load_json(packet / "extraction" / "material_staging_status.json")
    return data if isinstance(data, dict) else {}


def first_metadata(roots: list[Path]) -> dict[str, Any]:
    for root in roots:
        data = load_json(root / "metadata.json")
        if isinstance(data, dict):
            return data
    return {}


def direct_and_identifier_roots(paper_id: str, landed: Path, downloaded: Path) -> list[Path]:
    initial = [landed / paper_id, downloaded / paper_id]
    meta = first_metadata([p for p in initial if p.exists()])
    names = [paper_id]
    pmid = str(meta.get("canonical_pmid") or "").strip()
    pmcid = str(meta.get("canonical_pmcid") or "").strip()
    if pmid:
        names.append(f"pmid__{pmid}")
    if pmcid:
        names.append(f"pmcid__{pmcid}")
        names.append(f"pmcid__{pmcid.upper()}")
    roots: list[Path] = []
    seen: set[str] = set()
    for name in names:
        for base in (landed, downloaded):
            path = base / name
            key = str(path)
            if key not in seen:
                roots.append(path)
                seen.add(key)
    return roots


def count_json_table_rows(path: Path) -> int:
    data = load_json(path)
    if isinstance(data, dict):
        if isinstance(data.get("tables"), list):
            return len(data["tables"])
        if isinstance(data.get("table_count"), int):
            return int(data["table_count"])
    if isinstance(data, list):
        return len(data)
    return 0


def locator_counts(path: Path) -> dict[str, int]:
    data = load_json(path)
    counts: Counter[str] = Counter()
    if isinstance(data, dict):
        for loc in data.get("locators") or []:
            if isinstance(loc, dict):
                kind = str(loc.get("kind") or "unknown")
                label = str(loc.get("label") or "").lower()
                locator = str(loc.get("locator") or "").lower()
                counts[kind] += 1
                if "table" in kind or "table" in label or "table" in locator:
                    counts["table_like"] += 1
                if "fig" in kind or "fig" in label or "fig" in locator:
                    counts["figure_like"] += 1
    return dict(counts)


def database_row_counts(packet: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    db = packet / "database"
    for path in sorted(db.glob("*.jsonl")):
        try:
            count = sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
        except Exception:
            count = 0
        counts[path.stem] = count
    manifest = load_json(db / "database_source_manifest.json")
    if isinstance(manifest, dict):
        row_counts = manifest.get("row_counts")
        if isinstance(row_counts, dict):
            for key, value in row_counts.items():
                if isinstance(value, int):
                    counts.setdefault(key, value)
    return counts


def extract_quality_feedback(paper_id: str) -> dict[str, Any]:
    paths = [
        ROOT / "papers" / paper_id / "work" / "review" / "quality_feedback.json",
        ROOT / "paper_packets" / paper_id / "analysis" / "quality_feedback.json",
    ]
    for path in paths:
        data = load_json(path)
        if isinstance(data, dict):
            return data
    return {}


def extract_review_report(paper_id: str) -> dict[str, Any]:
    paths = [
        ROOT / "papers" / paper_id / "final" / "review_report.json",
        ROOT / "paper_packets" / paper_id / "final" / "review_report.json",
        ROOT / "paper_packets" / paper_id / "analysis" / "adjudication_report.json",
    ]
    for path in paths:
        data = load_json(path)
        if isinstance(data, dict):
            return data
    return {}


def owned_failure_codes(feedback: dict[str, Any], review: dict[str, Any]) -> tuple[list[str], list[str]]:
    codes: list[str] = []
    owners: list[str] = []
    for source in [feedback.get("qc_failure_reasons"), feedback.get("rework_targets"), review.get("rework_targets")]:
        if not isinstance(source, list):
            continue
        for item in source:
            if not isinstance(item, dict):
                continue
            owner = item.get("owner_worker") or item.get("worker")
            for code_key in ("code", "failure_code", "omission_code", "gap_code"):
                if item.get(code_key):
                    codes.append(str(item[code_key]))
            if owner:
                owners.append(str(owner))
    return sorted(set(codes)), sorted(set(owners))


def rework_target_queue_counts(feedback: dict[str, Any], review: dict[str, Any], requests: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for source in [feedback.get("rework_targets"), review.get("rework_targets"), requests]:
        if not isinstance(source, list):
            continue
        for item in source:
            if not isinstance(item, dict):
                continue
            queue = str(item.get("target_queue") or "").strip()
            if queue:
                counts[queue] += 1
    return dict(counts)


def material_exhausted_flag(review: dict[str, Any]) -> str:
    materials = review.get("materials_exhausted")
    if isinstance(materials, dict):
        bool_values = [value for value in materials.values() if isinstance(value, bool)]
        if bool_values and all(bool_values):
            return "all_true"
        if bool_values and any(bool_values):
            return "partial_true"
        note = str(materials.get("note") or "")
        if note:
            return "noted"
    if materials is True:
        return "all_true"
    return "unknown"


def classify_row(row: dict[str, str], evidence: dict[str, Any]) -> dict[str, Any]:
    triage_class = row.get("triage_class", "")
    target_queue = row.get("target_queue", "")
    failure_codes = row.get("failure_codes", "")
    feedback_codes = ";".join(evidence.get("feedback_failure_codes") or [])
    combined = ";".join([triage_class, target_queue, failure_codes, feedback_codes]).lower()
    true_supp = int(evidence["total_true_supplementary_candidates"])
    package_members = int(evidence["package_member_count"])
    figure_assets = int(evidence["figure_asset_count"])
    xml_table_rows = int(evidence["xml_table_locator_count"])
    supp_tables = int(evidence["supplementary_table_count"])
    material_exhausted = evidence.get("material_exhausted")
    alt_material = bool(evidence.get("alternate_identifier_material_present"))

    source_gap_tokens = (
        "missing_supplement",
        "unparsed_table",
        "not_staged",
        "not_locally_landed",
        "source_data_not",
        "docx",
        "xlsx",
        "supplement_docx",
        "supplementary_docx",
    )
    figure_tokens = (
        "figure",
        "digitization",
        "plot",
        "axis",
        "curve",
        "orientation",
        "not_machine_readable",
    )
    runtime_tokens = ("codex_worker_nonzero", "codex_api_or_network_error", "codex_worker_timeout")
    exact_unrecoverable_tokens = ("unrecoverable", "exact_value", "exact_values", "figure_only", "not_machine_readable")
    hard_missing_source_tokens = (
        "source_data_not_locally_landed",
        "unrecoverable_local_source_data_gap",
        "primary_one_letter_sequence_table_not_locally_recoverable",
        "primary_sequence_evidence_absent_after_bounded_local_recovery",
        "worker4_database_exact_toxicity_values_not_locally_recoverable",
    )
    analysis_owner_tokens = (
        "activity_table_axis_inversion",
        "activity_table_orientation_incomplete",
        "raw_value_matches_not_promoted_without_entity_target_alignment",
        "supplementary_tables_indexed_database_alignment_incomplete",
        "mechanism_claims_placeholder_not_source_adjudicated",
        "mechanism_context_pending_review",
    )

    has_source_gap = any(token in combined for token in source_gap_tokens)
    has_figure_gap = any(token in combined for token in figure_tokens)
    has_runtime_gap = any(token in combined for token in runtime_tokens)
    has_exact_unrecoverable = any(token in combined for token in exact_unrecoverable_tokens)
    has_hard_missing_source_gap = any(token in combined for token in hard_missing_source_tokens)
    has_analysis_owner_gap = any(token in combined for token in analysis_owner_tokens)
    has_local_tables = xml_table_rows > 0 or supp_tables > 0
    has_stageable_material = true_supp > 0 or package_members > 0 or alt_material
    material_ticket_count = int((evidence.get("rework_target_queue_counts") or {}).get("material_extraction", 0))
    analysis_ticket_count = int((evidence.get("rework_target_queue_counts") or {}).get("analysis", 0))
    packet_staged = evidence.get("packet_material_staging_status") in {"material_staged", "material_already_staged"}
    packet_staged_tables = int(evidence.get("packet_material_staged_table_count") or 0)
    packet_staged_assets = int(evidence.get("packet_material_staged_asset_count") or 0)
    packet_staged_text = int(evidence.get("packet_material_staged_text_record_count") or 0)
    staged_after_blocked = bool(evidence.get("material_staging_newer_than_bounded_rework"))
    bounded_status = str(evidence.get("bounded_result_status") or "")
    unsupported_activity_tokens = (
        "no_source_supported_amp_activity_rows",
        "missing_activity_records",
        "database_only_activity_not_primary_source_verified",
        "publication_grade_blocked_by_activity_primary_source_gap",
    )
    has_unsupported_activity_gap = any(token in combined for token in unsupported_activity_tokens)
    material_repair_surface = "none"
    if packet_staged_tables > 0:
        material_repair_surface = "supplementary_tables"
    elif packet_staged_text > 0 or packet_staged_assets > 0:
        material_repair_surface = "text_only_supplementary_assets"

    if bounded_status == "blocked_after_best_effort" and staged_after_blocked and packet_staged:
        bucket = "material_repaired_ready_for_retriage"
        if packet_staged_tables > 0:
            action = "Newer material staging added parseable supplementary/table evidence after the previous blocked result; rerun triage and launch policy-safe owner-worker source review."
        elif packet_staged_text > 0 or packet_staged_assets > 0:
            action = "Newer material staging added text-only supplementary assets after the previous blocked result; rerun triage and launch owner-worker review to recover obtainable facts, but keep exact table values unresolved if unsupported."
        else:
            action = "Newer material staging marker exists but no indexed asset/table count was recorded; inspect staging report before owner-worker launch."
    elif bounded_status == "blocked_after_best_effort":
        if has_hard_missing_source_gap:
            bucket = "still_unrecoverable_backlog"
            action = "Keep non-publication-grade; the remaining blocker is missing primary/source-data/sequence evidence rather than a locally controllable figure-digitization task."
        elif has_analysis_owner_gap and (analysis_ticket_count > 0 or has_local_tables or packet_staged_tables > 0):
            bucket = "analysis_rework_candidate_not_auto_queued"
            action = "Current packet has analysis-owned repair targets or table/locator evidence; run explicit owner-worker analysis rework, not blind figure digitization."
        elif has_figure_gap:
            bucket = "manual_digitization_candidate"
            action = "Owner-worker already exhausted the current packet; use controlled digitization for figure/chart exact values or keep source_conflict."
        elif has_source_gap:
            bucket = "source_staging_candidate"
            action = "Owner-worker already exhausted current material; only new/parseable supplement or source-data staging can justify another review."
        else:
            bucket = "still_unrecoverable_backlog"
            action = "Owner-worker already ran after available material repair and strict gates remained blocked; keep non-publication-grade until new evidence or policy change."
    elif packet_staged and packet_staged_tables > 0:
        bucket = "material_repaired_ready_for_retriage"
        action = "Material staging added parseable supplementary/table evidence; rerun needs-targeted triage before any policy-safe owner-worker analysis."
    elif packet_staged and packet_staged_assets > 0 and has_figure_gap:
        bucket = "manual_digitization_candidate"
        action = "Material staging found only figure/binary assets for the remaining exact-value gap; use controlled digitization or keep source_conflict."
    elif "missing_supplement_or_unparsed_table" in triage_class:
        if material_ticket_count > 0 or has_stageable_material:
            bucket = "source_staging_candidate"
            action = "Run material queue to rebuild/stage packet supplements or tables, then rerun triage; do not launch owner-worker until packet repair is recorded."
        elif analysis_ticket_count > 0 and has_local_tables and not has_unsupported_activity_gap:
            bucket = "analysis_rework_candidate_not_auto_queued"
            action = "Packet has source locators and analysis-owned rework tickets; keep out of owner-worker until explicitly re-triaged from backlog to analysis queue."
        else:
            bucket = "still_unrecoverable_backlog"
            action = "Keep non-publication-grade; no local stageable supplement/table candidate was found, or current sources support no primary AMP activity row."
    elif "figure_exact_value_or_digitization_needed" in triage_class:
        bucket = "manual_digitization_candidate"
        if has_hard_missing_source_gap:
            bucket = "still_unrecoverable_backlog"
            action = "Do not digitize: the unresolved field requires missing source data, a primary sequence table, or database-exact material not present locally."
        elif has_analysis_owner_gap and (analysis_ticket_count > 0 or has_local_tables):
            bucket = "analysis_rework_candidate_not_auto_queued"
            action = "Figure/digitization triage hides an analysis-owned table/entity/ontology repair; explicitly re-triage to owner-worker analysis before any acceptance claim."
        elif figure_assets:
            action = "Manual figure/table digitization may recover exact values; otherwise preserve source_conflict and keep non-publication-grade."
        else:
            action = "No local figure asset found for digitization; keep documented backlog unless external source data is acquired."
    elif material_ticket_count > 0 or (has_source_gap and (has_stageable_material or alt_material)):
        bucket = "source_staging_candidate"
        action = "Stage newly located or alternate-identifier materials into the packet and rerun material extraction before analysis."
    elif has_figure_gap and (figure_assets or has_exact_unrecoverable):
        bucket = "manual_digitization_candidate"
        action = "Digitize figure-only exact values only if a controlled digitization pass is authorized; do not fabricate values from plots."
    elif (analysis_ticket_count > 0 or has_runtime_gap) and has_local_tables and material_exhausted != "all_true":
        bucket = "analysis_rework_candidate_not_auto_queued"
        action = "Local XML/table evidence exists but current freeze class keeps it out of owner queue; requires explicit re-triage before owner-worker launch."
    else:
        bucket = "still_unrecoverable_backlog"
        if material_exhausted == "all_true" or "obtainable_only_source_gap_documented" in combined:
            action = "Keep non-publication-grade; obtainable local materials were already exhausted and remaining values/conflicts are unsupported."
        else:
            action = "Keep backlog pending external primary/source-data acquisition or manual curator override."

    ready = bucket in {"analysis_rework_candidate_not_auto_queued", "material_repaired_ready_for_retriage"}
    return {
        "audit_bucket": bucket,
        "ready_for_owner_worker_after_material_repair": ready,
        "material_repair_surface": material_repair_surface,
        "recommended_next_action_from_audit": action,
        "has_source_gap_signal": has_source_gap,
        "has_figure_gap_signal": has_figure_gap,
        "has_runtime_gap_signal": has_runtime_gap,
        "has_exact_unrecoverable_signal": has_exact_unrecoverable,
        "has_hard_missing_source_gap_signal": has_hard_missing_source_gap,
        "has_analysis_owner_gap_signal": has_analysis_owner_gap,
    }


def audit_one(row: dict[str, str], landed: Path, downloaded: Path) -> dict[str, Any]:
    paper_id = row["paper_id"]
    roots = direct_and_identifier_roots(paper_id, landed, downloaded)
    existing_roots = [root for root in roots if root.exists()]
    asset_details = [collect_asset_details(root) for root in existing_roots]
    direct_root_strings = {str(landed / paper_id), str(downloaded / paper_id)}
    alternate_roots = [root for root in existing_roots if str(root) not in direct_root_strings]

    total_counts = Counter()
    total_true_supp = 0
    total_html_supp = 0
    total_unknown_supp = 0
    figure_asset_count = 0
    stageable_names: set[str] = set()
    for details in asset_details:
        for key, count in (details.get("counts") or {}).items():
            total_counts[key] += int(count or 0)
        supp_files = details.get("files", {}).get("supplementary", [])
        true_count, html_count, unknown_count = count_true_supplementary(supp_files)
        total_true_supp += true_count
        total_html_supp += html_count
        total_unknown_supp += unknown_count
        for label in ["supplementary", "package"]:
            for item in details.get("files", {}).get(label, []):
                name = str(item.get("name") or "")
                suffix = str(item.get("suffix") or "").lower()
                kind = str(item.get("kind") or "")
                if kind in {"pdf", "zip_like", "docx", "xlsx", "pptx", "archive", "image", "xml", "text"} or suffix in STRUCTURED_SUPP_EXTS:
                    stageable_names.add(name)
                lower_name = name.lower()
                if suffix in IMAGE_EXTS or any(token in lower_name for token in FIGURE_KEYWORDS):
                    figure_asset_count += 1

    packet = ROOT / "paper_packets" / paper_id
    staging = packet_staging_status(packet)
    manifest = load_json(packet / "packet_manifest.json") or {}
    extraction_status = load_json(packet / "extraction" / "extraction_status.json") or {}
    extraction_quality = load_json(packet / "extraction" / "extraction_quality_report.json") or {}
    loc_counts = locator_counts(packet / "locators" / "locator_index.json")
    db_counts = database_row_counts(packet)
    review = extract_review_report(paper_id)
    feedback = extract_quality_feedback(paper_id)
    feedback_codes, owners = owned_failure_codes(feedback, review)
    bounded = feedback.get("bounded_rework_result") if isinstance(feedback.get("bounded_rework_result"), dict) else {}
    rework_requests = read_jsonl(packet / "rework" / "rework_requests.jsonl")
    rework_responses = read_jsonl(packet / "rework" / "rework_responses.jsonl")
    target_queue_counts = rework_target_queue_counts(feedback, review, rework_requests)

    archive_manifest = load_json(packet / "extracted" / "archive_manifest.json") or {}
    archive_members = archive_manifest.get("archives") if isinstance(archive_manifest, dict) else []
    if not isinstance(archive_members, list):
        archive_members = []
    package_member_count = len(archive_members)
    package_image_count = 0
    for item in archive_members:
        if isinstance(item, dict):
            suffix = Path(str(item.get("member") or "")).suffix.lower()
            if suffix in IMAGE_EXTS:
                package_image_count += 1

    alternate_material_present = False
    for root in alternate_roots:
        counts = parse_asset_counts(root)
        if counts["supplementary"] or counts["package"] or counts["pdf"] or counts["xml"]:
            alternate_material_present = True
            break

    evidence: dict[str, Any] = {
        **row,
        "found_asset_roots": [str(root) for root in existing_roots],
        "alternate_identifier_roots": [str(root) for root in alternate_roots],
        "alternate_identifier_material_present": alternate_material_present,
        "paper_packet_exists": packet.exists(),
        "material_queue_status": manifest.get("material_queue_status") or extraction_status.get("status") or "",
        "analysis_queue_status": manifest.get("analysis_queue_status") or "",
        "packet_version": manifest.get("packet_version") or "",
        "packet_known_missing_count": len(manifest.get("known_missing_or_blocked_materials") or []) if isinstance(manifest, dict) else 0,
        "open_rework_ticket_count": len(manifest.get("open_rework_ticket_ids") or []) if isinstance(manifest, dict) else 0,
        "rework_request_count": len(rework_requests),
        "rework_response_count": len(rework_responses),
        "rework_target_queue_counts": target_queue_counts,
        "material_rework_ticket_count": target_queue_counts.get("material_extraction", 0),
        "analysis_rework_ticket_count": target_queue_counts.get("analysis", 0),
        "adjudication_rework_ticket_count": target_queue_counts.get("adjudication", 0),
        "packet_material_staging_status": staging.get("status", ""),
        "packet_material_staging_generated_at": staging.get("generated_at", ""),
        "packet_material_change_at": staging.get("material_change_at", ""),
        "packet_material_changed": bool(staging.get("material_changed")),
        "packet_locator_index_repair_at": staging.get("locator_index_repair_at", ""),
        "packet_locator_index_repair_count": staging.get("locator_index_repair_count", 0),
        "packet_material_staged_asset_count": staging.get("staged_asset_count", 0),
        "packet_material_staged_text_record_count": staging.get("text_record_count_added_or_indexed", 0),
        "packet_material_staged_table_count": staging.get("table_count_added_or_indexed", 0),
        "bounded_rework_result_updated_at": bounded.get("updated_at", ""),
        "material_staging_newer_than_bounded_rework": timestamp_after(latest_repair_timestamp(staging), bounded.get("updated_at")),
        "packet_material_staging_report": safe_rel(packet / "extraction" / "material_staging_status.json") if staging else "",
        "total_pdf_files": total_counts["pdf"],
        "total_xml_files": total_counts["xml"],
        "total_package_files": total_counts["package"],
        "total_supplementary_files": total_counts["supplementary"],
        "total_true_supplementary_candidates": total_true_supp,
        "total_html_or_landing_supplementary": total_html_supp,
        "total_unknown_supplementary": total_unknown_supp,
        "stageable_asset_names": sorted(stageable_names)[:40],
        "stageable_asset_name_count": len(stageable_names),
        "package_member_count": package_member_count,
        "package_image_member_count": package_image_count,
        "figure_asset_count": figure_asset_count + package_image_count,
        "xml_section_count": extraction_quality.get("xml_section_count", ""),
        "xml_table_count": extraction_quality.get("xml_table_count", ""),
        "supplementary_asset_count": extraction_quality.get("supplementary_asset_count", ""),
        "supplementary_table_count": count_json_table_rows(packet / "extracted" / "supplementary_tables.json"),
        "pdf_table_count": count_json_table_rows(packet / "extracted" / "pdf_tables.json"),
        "locator_count": loc_counts.get("unknown", 0) + sum(v for k, v in loc_counts.items() if k != "table_like" and k != "figure_like"),
        "xml_table_locator_count": loc_counts.get("table_like", 0),
        "figure_locator_count": loc_counts.get("figure_like", 0),
        "database_row_total": sum(db_counts.values()),
        "database_row_counts": db_counts,
        "review_status": review.get("review_status") or review.get("blocker_status") or "",
        "publication_grade": review.get("publication_grade", ""),
        "validator_contract_passed": review.get("validator_contract_passed", ""),
        "material_exhausted": material_exhausted_flag(review),
        "feedback_failure_codes": feedback_codes,
        "feedback_owner_workers": owners,
        "bounded_result_status": bounded.get("status", ""),
        "bounded_result_reason_code": bounded.get("result_reason_code", ""),
        "quality_feedback_issue_count": feedback.get("issue_count", ""),
        "sample_paths_checked": [
            safe_rel(packet / "packet_manifest.json"),
            safe_rel(packet / "extraction" / "extraction_status.json"),
            safe_rel(packet / "locators" / "locator_index.json"),
            safe_rel(ROOT / "papers" / paper_id / "work" / "review" / "quality_feedback.json"),
        ],
    }
    evidence.update(classify_row(row, evidence))
    return evidence


def render_md(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Material/Digitization Backlog Audit",
        "",
        f"- generated_at: `{summary['generated_at']}`",
        f"- completion_claim: `{summary['completion_claim']}`",
        f"- backlog_rows: `{summary['backlog_rows']}`",
        f"- owner_worker_launch_allowed: `{summary['owner_worker_launch_allowed']}`",
        f"- bucket_counts: `{json.dumps(summary['audit_bucket_counts'], ensure_ascii=False, sort_keys=True)}`",
        f"- material_repair_surface_counts: `{json.dumps(summary.get('material_repair_surface_counts', {}), ensure_ascii=False, sort_keys=True)}`",
        "",
        "This report audits local material availability only. It does not make any paper publication-grade, close rework tickets, or move papers into owner-worker review.",
        "",
        "## Buckets",
    ]
    for bucket, count in summary["audit_bucket_counts"].items():
        lines.append(f"- `{bucket}`: {count}")
    lines.extend(["", "## Paper Actions", ""])
    for row in rows:
        lines.append(
            "- `{paper_id}` | `{bucket}` | triage=`{triage}` | action={action}".format(
                paper_id=row["paper_id"],
                bucket=row["audit_bucket"],
                triage=row.get("triage_class", ""),
                action=row.get("recommended_next_action_from_audit", ""),
            )
        )
        lines.append(
            "  - evidence: roots={roots}; xml_tables={xml_tables}; supp_tables={supp_tables}; staged_assets={staged_assets}; staged_tables={staged_tables}; repair_surface={surface}; staging_after_blocked={staging_after_blocked}; true_supp={supp}; package_members={packages}; figures={figures}; material_exhausted={exhausted}".format(
                roots=len(row.get("found_asset_roots") or []),
                xml_tables=row.get("xml_table_locator_count", 0),
                supp_tables=row.get("supplementary_table_count", 0),
                staged_assets=row.get("packet_material_staged_asset_count", 0),
                staged_tables=row.get("packet_material_staged_table_count", 0),
                surface=row.get("material_repair_surface", ""),
                staging_after_blocked=row.get("material_staging_newer_than_bounded_rework", ""),
                supp=row.get("total_true_supplementary_candidates", 0),
                packages=row.get("package_member_count", 0),
                figures=row.get("figure_asset_count", 0),
                exhausted=row.get("material_exhausted", ""),
            )
        )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backlog", type=Path, default=DEFAULT_BACKLOG)
    parser.add_argument("--out-prefix", type=Path, default=DEFAULT_OUT_PREFIX)
    parser.add_argument("--landed-root", type=Path, default=DEFAULT_LANDED)
    parser.add_argument("--downloaded-root", type=Path, default=DEFAULT_DOWNLOADED)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_csv(args.backlog)
    audited = [audit_one(row, args.landed_root, args.downloaded_root) for row in rows]
    bucket_counts = Counter(row["audit_bucket"] for row in audited)
    triage_counts = Counter(row.get("triage_class", "") for row in audited)
    target_counts = Counter(row.get("target_queue", "") for row in audited)
    surface_counts = Counter(row.get("material_repair_surface", "none") for row in audited)
    ready_count = sum(1 for row in audited if row.get("ready_for_owner_worker_after_material_repair"))

    summary = {
        "generated_at": utc_now(),
        "completion_claim": "material_backlog_audit_only_not_publication_grade_acceptance",
        "input_backlog": str(args.backlog),
        "backlog_rows": len(audited),
        "audit_bucket_counts": dict(bucket_counts),
        "material_repair_surface_counts": dict(surface_counts),
        "triage_class_counts": dict(triage_counts),
        "target_queue_counts": dict(target_counts),
        "ready_for_owner_worker_after_material_repair_count": ready_count,
        "owner_worker_launch_allowed": False,
        "strict_boundary": "Only papers with a later material-repair record, strict source-reviewed owner-worker pass, and worker-6 adjudication may leave this backlog.",
        "outputs": {
            "json": str(args.out_prefix.with_suffix(".json")),
            "csv": str(args.out_prefix.with_suffix(".csv")),
            "md": str(args.out_prefix.with_suffix(".md")),
            "source_staging_candidates": str(WORK / "source_staging_candidates_latest.csv"),
            "manual_digitization_candidates": str(WORK / "manual_digitization_candidates_latest.csv"),
            "analysis_rework_candidates": str(WORK / "analysis_rework_candidates_not_auto_queued_latest.csv"),
            "material_repaired_ready_for_retriage": str(WORK / "material_repaired_ready_for_retriage_latest.csv"),
            "still_unrecoverable_backlog": str(WORK / "still_unrecoverable_backlog_latest.csv"),
            "ready_for_owner_worker_after_material_repair": str(WORK / "ready_for_owner_worker_after_material_repair_latest.csv"),
        },
    }

    fieldnames = [
        "paper_id",
        "triage_class",
        "target_queue",
        "audit_bucket",
        "ready_for_owner_worker_after_material_repair",
        "recommended_next_action_from_audit",
        "material_queue_status",
        "analysis_queue_status",
        "review_status",
        "publication_grade",
        "material_exhausted",
        "total_pdf_files",
        "total_xml_files",
        "total_package_files",
        "total_supplementary_files",
        "total_true_supplementary_candidates",
        "total_html_or_landing_supplementary",
        "total_unknown_supplementary",
        "stageable_asset_name_count",
        "package_member_count",
        "package_image_member_count",
        "figure_asset_count",
        "xml_table_locator_count",
        "supplementary_table_count",
        "pdf_table_count",
        "database_row_total",
        "open_rework_ticket_count",
        "rework_request_count",
        "rework_response_count",
        "material_rework_ticket_count",
        "analysis_rework_ticket_count",
        "adjudication_rework_ticket_count",
        "rework_target_queue_counts",
        "packet_material_staging_status",
        "packet_material_staging_generated_at",
        "packet_material_change_at",
        "packet_material_changed",
        "packet_locator_index_repair_at",
        "packet_locator_index_repair_count",
        "packet_material_staged_asset_count",
        "packet_material_staged_text_record_count",
        "packet_material_staged_table_count",
        "bounded_rework_result_updated_at",
        "material_staging_newer_than_bounded_rework",
        "material_repair_surface",
        "packet_material_staging_report",
        "feedback_failure_codes",
        "feedback_owner_workers",
        "bounded_result_status",
        "bounded_result_reason_code",
        "failure_codes",
        "has_hard_missing_source_gap_signal",
        "has_analysis_owner_gap_signal",
        "found_asset_roots",
        "alternate_identifier_roots",
        "alternate_identifier_material_present",
        "stageable_asset_names",
        "sample_paths_checked",
    ]

    write_json(args.out_prefix.with_suffix(".json"), {"summary": summary, "rows": audited})
    write_csv(args.out_prefix.with_suffix(".csv"), audited, fieldnames)
    args.out_prefix.with_suffix(".md").write_text(render_md(summary, audited), encoding="utf-8")

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in audited:
        groups[row["audit_bucket"]].append(row)
    write_csv(WORK / "source_staging_candidates_latest.csv", groups["source_staging_candidate"], fieldnames)
    write_csv(WORK / "manual_digitization_candidates_latest.csv", groups["manual_digitization_candidate"], fieldnames)
    write_csv(WORK / "analysis_rework_candidates_not_auto_queued_latest.csv", groups["analysis_rework_candidate_not_auto_queued"], fieldnames)
    write_csv(WORK / "material_repaired_ready_for_retriage_latest.csv", groups["material_repaired_ready_for_retriage"], fieldnames)
    write_csv(WORK / "still_unrecoverable_backlog_latest.csv", groups["still_unrecoverable_backlog"], fieldnames)
    write_csv(
        WORK / "ready_for_owner_worker_after_material_repair_latest.csv",
        [row for row in audited if row.get("ready_for_owner_worker_after_material_repair")],
        fieldnames,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
