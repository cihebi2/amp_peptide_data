#!/usr/bin/env python3
"""Preflight source-staging blockers before rerunning paper review.

This script is intentionally evidence-path focused. It inspects local packet
inventories, extraction status, supplementary indexes, quality feedback, and
the follow-up queue reason codes, then classifies what must happen before a
paper should be sent back to owner workers.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_stamp() -> str:
    return now_utc().replace("-", "").replace(":", "")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:  # noqa: BLE001 - audit should preserve partial failures
        return {"_parse_error": str(exc), "_path": str(path)}
    return data if isinstance(data, dict) else {"_not_object": True, "_path": str(path)}


def read_jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            count += 1
    return count


def text_blob(*values: Any) -> str:
    return json.dumps(values, ensure_ascii=False, sort_keys=True).lower()


def count_files(path: Path, pattern: str = "*") -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob(pattern) if item.is_file())


def supplementary_asset_stats(supplementary_index: dict[str, Any]) -> dict[str, Any]:
    assets = supplementary_index.get("supplementary_assets") or []
    suffix_counts: Counter[str] = Counter()
    landing_like = 0
    real_data_like = 0
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        suffix = str(asset.get("suffix") or Path(str(asset.get("name") or "")).suffix or "<none>").lower()
        name = str(asset.get("name") or "").lower()
        path = str(asset.get("path") or "").lower()
        suffix_counts[suffix] += 1
        if "landing" in name or "landing" in path or suffix == ".bin":
            landing_like += 1
        if suffix in {".xlsx", ".xls", ".csv", ".tsv", ".ods", ".docx", ".pdf", ".zip", ".rar", ".7z"}:
            real_data_like += 1
    return {
        "asset_count": len(assets),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "landing_like_count": landing_like,
        "real_data_like_count": real_data_like,
    }


def classify_source_action(item: dict[str, Any], packet: Path, paper: Path) -> dict[str, Any]:
    paper_id = str(item.get("paper_id") or "")
    packet_manifest = read_json(packet / "packet_manifest.json")
    supplementary_index = read_json(packet / "extracted" / "supplementary_index.json")
    supplementary_tables = read_json(packet / "extracted" / "supplementary_tables.json")
    extraction_status = read_json(packet / "extraction" / "extraction_status.json")
    quality_feedback = read_json(paper / "work" / "review" / "quality_feedback.json")
    extraction_error_count = read_jsonl_count(packet / "extraction" / "extraction_errors.jsonl")
    pdf_text_file_count = count_files(packet / "extracted" / "pdf_text")
    figure_caption_exists = (packet / "extracted" / "figure_captions.json").exists()

    blob = text_blob(
        item.get("refined_status"),
        item.get("qc_codes"),
        item.get("gap_codes"),
        item.get("semantic_issue_codes"),
        packet_manifest.get("known_missing_or_blocked_materials"),
        quality_feedback.get("qc_failure_reasons"),
        quality_feedback.get("unrecoverable_material_gaps"),
    )
    supp_stats = supplementary_asset_stats(supplementary_index)
    table_count = int(supplementary_tables.get("table_count") or len(supplementary_tables.get("tables") or []))
    refined_status = str(item.get("refined_status") or "")

    if not packet.exists():
        action = "missing_packet_or_material_manifest"
    elif refined_status == "blocked_source_gap_missing_external_supplement":
        action = "needs_external_supplement_staging"
    elif refined_status == "blocked_source_gap_figure_chart_exact_value":
        action = "needs_figure_or_chart_digitization"
    elif (
        "supplement" in blob
        or "moesm" in blob
        or "source data" in blob
        or "external_source" in blob
        or (supp_stats["asset_count"] and supp_stats["real_data_like_count"] == 0 and table_count == 0)
    ):
        action = "needs_external_supplement_staging"
    elif "figure" in blob or "chart" in blob or "exact_value" in blob:
        action = "needs_figure_or_chart_digitization"
    elif table_count > 0 or pdf_text_file_count > 0:
        action = "local_material_reinspection_candidate"
    else:
        action = "source_gap_requires_manual_triage"

    return {
        "paper_id": paper_id,
        "source_queue_status": item.get("refined_status"),
        "recommended_preflight_action": action,
        "source_summary": item.get("source_summary"),
        "packet_path": str(packet),
        "paper_path": str(paper),
        "path_checks": {
            "packet_exists": packet.exists(),
            "packet_manifest": str(packet / "packet_manifest.json"),
            "supplementary_index": str(packet / "extracted" / "supplementary_index.json"),
            "supplementary_tables": str(packet / "extracted" / "supplementary_tables.json"),
            "extraction_status": str(packet / "extraction" / "extraction_status.json"),
            "quality_feedback": str(paper / "work" / "review" / "quality_feedback.json"),
        },
        "local_inventory": {
            "material_queue_status": packet_manifest.get("material_queue_status"),
            "analysis_queue_status": packet_manifest.get("analysis_queue_status"),
            "source_inventory": extraction_status.get("source_inventory") or {},
            "extraction_status": extraction_status.get("status"),
            "extraction_error_count": extraction_error_count,
            "supplementary_asset_stats": supp_stats,
            "supplementary_table_count": table_count,
            "pdf_text_file_count": pdf_text_file_count,
            "figure_caption_exists": figure_caption_exists,
        },
        "reason_codes": {
            "refined_reason_code": item.get("refined_reason_code"),
            "qc_codes": item.get("qc_codes") or [],
            "gap_codes": item.get("gap_codes") or [],
            "semantic_issue_codes": item.get("semantic_issue_codes") or [],
        },
        "next_action_contract": {
            "needs_external_supplement_staging": "stage true supplementary/source-data files, then rerun material extraction before analysis",
            "needs_figure_or_chart_digitization": "digitize chart/figure exact values or mark value unavailable with source paths checked",
            "local_material_reinspection_candidate": "rerun targeted extraction against existing local material before requesting external source",
            "source_gap_requires_manual_triage": "manual source triage required before any owner re-review",
            "missing_packet_or_material_manifest": "rebuild material packet before analysis",
        }[action],
    }


def load_items(manifest: Path) -> list[dict[str, Any]]:
    data = read_json(manifest)
    items = data.get("items") or []
    if not isinstance(items, list):
        raise SystemExit(f"Manifest items is not a list: {manifest}")
    return [item for item in items if isinstance(item, dict)]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default="reports/followup_queues/true_rework_queue_next500_obtainable_20260505_source_staging_needed.json",
        help="source_staging_needed follow-up queue manifest.",
    )
    parser.add_argument("--out-dir", default="reports/source_staging_preflight")
    parser.add_argument("--run-label", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path.cwd()
    manifest = Path(args.manifest)
    items = load_items(manifest)
    rows = []
    for item in items:
        paper_id = str(item.get("paper_id") or "")
        rows.append(
            classify_source_action(
                item,
                repo / "paper_packets" / paper_id,
                repo / "papers" / paper_id,
            )
        )

    action_counts = Counter(row["recommended_preflight_action"] for row in rows)
    report = {
        "generated_at": now_utc(),
        "run_label": args.run_label,
        "source_manifest": str(manifest),
        "completion_claim": "source_staging_preflight_not_material_recovery_completion",
        "paper_count": len(rows),
        "action_counts": dict(sorted(action_counts.items())),
        "papers": rows,
    }

    prefix = args.run_label or f"source_staging_preflight_{safe_stamp()}"
    out_dir = Path(args.out_dir)
    out = out_dir / f"{prefix}.json"
    latest = out_dir / "source_staging_preflight_latest.json"
    write_json(out, report)
    write_json(latest, report)
    print(json.dumps({"ok": True, "out": str(out), "latest": str(latest), "paper_count": len(rows), "action_counts": report["action_counts"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
