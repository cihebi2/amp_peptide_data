#!/usr/bin/env python3
"""Summarize the live material-source recovery lane.

This is a status/reporting helper. It does not classify papers as reviewed and
does not launch review workers.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_text(command: str) -> str:
    proc = subprocess.run(["bash", "-lc", command], capture_output=True, text=True, check=False)
    return proc.stdout.strip()


def metadata_source_counts(manifest_path: Path) -> dict[str, int]:
    manifest = read_json(manifest_path) or {"items": []}
    counts = {"strict_xml_pdf": 0, "xml_or_nxml_plus_pdf": 0, "partial_xml_or_pdf": 0, "none": 0}
    for item in manifest.get("items", []):
        if not isinstance(item, dict) or not item.get("source_path"):
            continue
        source = Path(str(item["source_path"]))
        strict_xml = sum(1 for path in (source / "xml").glob("*.xml") if path.is_file())
        any_xml = sum(1 for path in (source / "xml").glob("*") if path.is_file() and path.suffix.lower() in {".xml", ".nxml"})
        pdf = sum(1 for path in (source / "pdf").glob("*.pdf") if path.is_file())
        if strict_xml and pdf:
            counts["strict_xml_pdf"] += 1
        elif any_xml and pdf:
            counts["xml_or_nxml_plus_pdf"] += 1
        elif any_xml or pdf:
            counts["partial_xml_or_pdf"] += 1
        else:
            counts["none"] += 1
    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("reports/source_recovery/material_source_recovery_status_latest.json"))
    parser.add_argument("--remaining-manifest", type=Path, default=Path("reports/source_recovery/remaining_unreviewed_sources_latest.json"))
    parser.add_argument("--weak-summary", type=Path, default=Path("source_recovery_packets/weak_source_full_20260511T150913Z/source_recovery_packet_build_summary.json"))
    parser.add_argument("--weak-check", type=Path, default=Path("reports/source_recovery/weak_source_full_packet_check_20260511T150913Z.json"))
    parser.add_argument("--metadata-manifest", type=Path, default=Path("reports/source_recovery/metadata_only_manifest_latest.json"))
    parser.add_argument("--metadata-final", type=Path, default=Path("reports/source_recovery/metadata_acquisition/metadata_full_20260511T150913Z.json"))
    parser.add_argument("--metadata-recovered-manifest", type=Path, default=Path("reports/source_recovery/metadata_recovered_partial_manifest_latest.json"))
    parser.add_argument(
        "--metadata-recovered-summary",
        type=Path,
        default=Path("source_recovery_packets/metadata_recovered_partial_20260511T165924Z/source_recovery_packet_build_summary.json"),
    )
    parser.add_argument(
        "--metadata-recovered-check",
        type=Path,
        default=Path("reports/source_recovery/metadata_recovered_partial_packet_check_20260511T165924Z.json"),
    )
    parser.add_argument("--metadata-process-pattern", default="recover_metadata_primary_sources.py")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    remaining = read_json(args.remaining_manifest) or {}
    weak = read_json(args.weak_summary) or {}
    weak_check = read_json(args.weak_check) or {}
    metadata_final = read_json(args.metadata_final)
    metadata_recovered_manifest = read_json(args.metadata_recovered_manifest) or {}
    metadata_recovered_summary = read_json(args.metadata_recovered_summary) or {}
    metadata_recovered_check = read_json(args.metadata_recovered_check) or {}
    process = run_text(f"ps -eo pid,etime,pcpu,pmem,cmd | rg '{args.metadata_process_pattern}' | rg -v rg || true")
    tmux = run_text("tmux list-sessions 2>/dev/null | rg 'src(weak|meta)_20260511' || true")
    status = {
        "generated_at": utc_now(),
        "completion_claim": "material_recovery_status_not_review_completion",
        "remaining_counts": (remaining.get("summary") or {}).get("remaining_category_counts"),
        "weak_packet_build": {
            "paper_count": weak.get("paper_count"),
            "material_status_counts": weak.get("material_status_counts"),
            "analysis_status_counts": weak.get("analysis_status_counts"),
            "open_rework_ticket_count": weak.get("open_rework_ticket_count"),
            "total_locator_count": weak.get("total_locator_count"),
            "check_total_extraction_error_count": weak_check.get("total_extraction_error_count"),
            "check_hard_finding_count": weak_check.get("hard_finding_count"),
            "hard_findings_are_expected_analysis_not_run": True,
        },
        "metadata_acquisition": {
            "is_running": bool(process),
            "process": process,
            "tmux_sessions": tmux.splitlines() if tmux else [],
            "final_summary": str(args.metadata_final),
            "final_summary_exists": metadata_final is not None,
            "final_status_counts": (metadata_final or {}).get("status_counts"),
            "current_source_counts": metadata_source_counts(args.metadata_manifest),
        },
        "metadata_recovered_partial_packets": {
            "manifest": str(args.metadata_recovered_manifest),
            "manifest_exists": bool(metadata_recovered_manifest),
            "paper_count": metadata_recovered_summary.get("paper_count") or metadata_recovered_manifest.get("paper_count"),
            "material_status_counts": metadata_recovered_summary.get("material_status_counts"),
            "analysis_status_counts": metadata_recovered_summary.get("analysis_status_counts"),
            "open_rework_ticket_count": metadata_recovered_summary.get("open_rework_ticket_count"),
            "total_locator_count": metadata_recovered_summary.get("total_locator_count"),
            "check_total_extraction_error_count": metadata_recovered_check.get("total_extraction_error_count"),
            "check_hard_finding_count": metadata_recovered_check.get("hard_finding_count"),
            "hard_findings_are_expected_analysis_not_run": True,
        },
        "review_worker_launch_allowed": False,
        "next_gate": "metadata acquisition completion -> regenerate manifests -> packetize recovered source-ready items only",
    }
    write_json(args.out, status)
    print(json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
