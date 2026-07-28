#!/usr/bin/env python3
"""Build controlled manual-digitization and analysis-rework task packets.

This script does not extract or promote exact values. It classifies the current
manual-digitization backlog into: (1) controlled figure digitization tasks that
need calibrated human/vision QA, (2) analysis rework tasks that can use existing
packet tables/locators, and (3) missing-source blockers that should remain out
of owner-worker review until new material is acquired.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "reports" / "nar_resource_freeze_v1" / "needs_targeted_rework_work"
DEFAULT_CANDIDATES = WORK / "manual_digitization_candidates_latest.csv"
DEFAULT_OUT_PREFIX = WORK / "manual_digitization_processing_latest"
LEGACY_FEASIBILITY_PREFIX = WORK / "manual_digitization_feasibility_latest"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".gif", ".bmp", ".webp"}

HARD_MISSING_SOURCE_TOKENS = (
    "source_data_not_locally_landed",
    "unrecoverable_local_source_data_gap",
    "primary_one_letter_sequence_table_not_locally_recoverable",
    "primary_sequence_evidence_absent_after_bounded_local_recovery",
    "worker4_database_exact_toxicity_values_not_locally_recoverable",
    "database exact toxicity",
    "not recoverable from local xml/pdf text, parsed tables, or supplementary assets",
)
ANALYSIS_OWNER_TOKENS = (
    "activity_table_axis_inversion",
    "activity_table_orientation_incomplete",
    "raw_value_matches_not_promoted_without_entity_target_alignment",
    "supplementary_tables_indexed_database_alignment_incomplete",
    "mechanism_claims_placeholder_not_source_adjudicated",
    "mechanism_context_pending_review",
)
FIGURE_GAP_TOKENS = (
    "figure",
    "fig",
    "graph",
    "plot",
    "curve",
    "axis",
    "chart",
    "not_machine_readable",
    "exact_values_unrecoverable",
    "exact_value",
)
SPECIFIC_FIGURE_GAP_TOKENS = (
    "figure_only",
    "figure4",
    "figure8",
    "fig_s1",
    "fig s1",
    "time_kill",
    "time-kill",
    "hemolysis_curve",
    "cytotoxicity_values",
    "cytotoxicity_percent",
    "ec50_values",
    "not_machine_readable",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def flatten_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return ";".join(str(item) for item in value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: flatten_cell(row.get(name, "")) for name in fieldnames})


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except Exception:
        return str(path)


def list_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(p for p in path.rglob("*") if p.is_file())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
            if isinstance(value, dict):
                rows.append(value)
        except json.JSONDecodeError:
            rows.append({"raw": line[:500]})
    return rows


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def collect_failure_codes(*objects: dict[str, Any], csv_codes: str = "") -> list[str]:
    codes: set[str] = {code for code in csv_codes.split(";") if code}
    for data in objects:
        if not isinstance(data, dict):
            continue
        for key in ("qc_failure_reasons", "rework_targets", "unrecoverable_material_gaps", "caution_findings"):
            for item in as_list(data.get(key)):
                if not isinstance(item, dict):
                    continue
                for code_key in ("code", "failure_code", "gap_code", "omission_code", "caution_code"):
                    if item.get(code_key):
                        codes.add(str(item[code_key]))
                for list_key in ("codes", "owner_workers"):
                    if isinstance(item.get(list_key), list):
                        for value in item[list_key]:
                            if isinstance(value, str) and value.startswith(("worker", "rwk")):
                                continue
        bounded = data.get("bounded_rework_result")
        if isinstance(bounded, dict) and bounded.get("result_reason_code"):
            codes.add(str(bounded["result_reason_code"]))
    return sorted(codes)


def collect_rework_targets(review: dict[str, Any], quality_feedback: dict[str, Any]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_name, data in (("review_report", review), ("quality_feedback", quality_feedback)):
        for item in as_list(data.get("rework_targets")):
            if not isinstance(item, dict):
                continue
            target = dict(item)
            target.setdefault("source_artifact", source_name)
            key = json.dumps(target, ensure_ascii=False, sort_keys=True)
            if key not in seen:
                targets.append(target)
                seen.add(key)
    return targets


def collect_unrecoverable_gaps(review: dict[str, Any], quality_feedback: dict[str, Any]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_name, data in (("review_report", review), ("quality_feedback", quality_feedback)):
        for item in as_list(data.get("unrecoverable_material_gaps")):
            if not isinstance(item, dict):
                continue
            gap = dict(item)
            gap.setdefault("source_artifact", source_name)
            key = json.dumps(gap, ensure_ascii=False, sort_keys=True)
            if key not in seen:
                gaps.append(gap)
                seen.add(key)
    return gaps


def image_inventory(packet: Path, paper: Path) -> list[dict[str, Any]]:
    roots = [packet / "extracted", packet / "raw", paper / "source"]
    items: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for root in roots:
        for path in list_files(root):
            lower = path.name.lower()
            if path.suffix.lower() not in IMAGE_EXTS and not any(token in lower for token in ("fig", "figure", "page-", "sf")):
                continue
            if path in seen:
                continue
            seen.add(path)
            items.append(
                {
                    "path": rel(path),
                    "name": path.name,
                    "suffix": path.suffix.lower(),
                    "size_bytes": path.stat().st_size if path.exists() else None,
                }
            )
    return items


def pdf_embedded_image_count(packet: Path) -> int:
    pdf = packet / "raw" / "paper.pdf"
    if not pdf.exists():
        return 0
    try:
        proc = subprocess.run(["pdfimages", "-list", str(pdf)], text=True, capture_output=True, timeout=20)
    except Exception:
        return 0
    return sum(1 for line in proc.stdout.splitlines() if re.match(r"\s*\d+", line))


def table_summary(packet: Path) -> dict[str, Any]:
    result = {"supplementary_table_count": 0, "pdf_table_count": 0, "xml_table_locator_count": 0}
    supp = read_json(packet / "extracted" / "supplementary_tables.json", {}) or {}
    if isinstance(supp, dict):
        if isinstance(supp.get("tables"), list):
            result["supplementary_table_count"] = len(supp["tables"])
        elif isinstance(supp.get("table_count"), int):
            result["supplementary_table_count"] = supp["table_count"]
    elif isinstance(supp, list):
        result["supplementary_table_count"] = len(supp)
    pdf_tables = read_json(packet / "extracted" / "pdf_tables.json", {}) or {}
    if isinstance(pdf_tables, dict):
        if isinstance(pdf_tables.get("tables"), list):
            result["pdf_table_count"] = len(pdf_tables["tables"])
        elif isinstance(pdf_tables.get("table_count"), int):
            result["pdf_table_count"] = pdf_tables["table_count"]
    loc = read_json(packet / "locators" / "locator_index.json", {}) or {}
    text = json.dumps(loc, ensure_ascii=False).lower()
    result["xml_table_locator_count"] = text.count("xml:table=")
    return result


def collect_blob(*values: Any) -> str:
    return "\n".join(json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value for value in values).lower()


def infer_target_surfaces(codes: list[str], blob: str, images: list[dict[str, Any]], rework_targets: list[dict[str, Any]], gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    joined = ";".join(codes).lower() + "\n" + blob
    figure_patterns = [
        ("figure4", "Figure 4"),
        ("fig_s1", "Figure S1"),
        ("fig s1", "Figure S1"),
        ("figure8", "Figure 8"),
        ("time_kill", "Figure 2"),
        ("time-kill", "Figure 2"),
        ("hemolysis_curve", "Supplementary hemolysis curve"),
        ("cytotoxic", "cytotoxicity figure/panel"),
        ("ec50", "dose-response/EC50 figure"),
    ]
    labels = [label for token, label in figure_patterns if token in joined]
    if not labels and any(token in joined for token in ("figure", "fig", "graph", "curve", "plot")):
        labels = ["figure-only exact-value surface"]
    source_paths: list[str] = []
    for item in rework_targets + gaps:
        if not isinstance(item, dict):
            continue
        for key in ("source_paths_to_check", "source_evidence_to_check", "source_paths_checked"):
            for value in as_list(item.get(key)):
                if isinstance(value, str):
                    source_paths.append(value)
    image_paths = [item["path"] for item in images]
    for source in source_paths:
        if Path(source).suffix.lower() in IMAGE_EXTS and source not in image_paths:
            image_paths.append(source)
    for label in sorted(set(labels)):
        matching_images = [path for path in image_paths if image_matches_label(path, label)] or image_paths[:8]
        surfaces.append(
            {
                "label": label,
                "candidate_image_paths": matching_images[:12],
                "source_paths_from_rework": source_paths[:24],
                "calibration_required": True,
                "independent_qa_required": True,
            }
        )
    return surfaces


def image_matches_label(path: str, label: str) -> bool:
    lower = path.lower()
    label_lower = label.lower()
    if "figure 4" in label_lower:
        return any(token in lower for token in ("g004", "fig4", "figure4", "_0004", "gr4"))
    if "figure s1" in label_lower or "supplementary" in label_lower:
        return any(token in lower for token in ("sf001", "s001", "supp", "figs1"))
    if "figure 8" in label_lower:
        return any(token in lower for token in ("fig8", "figure8", "_fig8", "f008"))
    if "figure 2" in label_lower:
        return any(token in lower for token in ("g002", "fig2", "figure2", "_0002", "f002", "gr2"))
    return True


def classify_candidate(codes: list[str], blob: str, tables: dict[str, Any], images: list[dict[str, Any]], rework_targets: list[dict[str, Any]]) -> tuple[str, str, str, bool, bool, bool]:
    text = ";".join(codes).lower() + "\n" + blob
    has_hard_missing = any(token in text for token in HARD_MISSING_SOURCE_TOKENS)
    has_analysis = any(token in text for token in ANALYSIS_OWNER_TOKENS)
    has_figure = any(token in text for token in FIGURE_GAP_TOKENS)
    has_specific_figure_gap = any(token in text for token in SPECIFIC_FIGURE_GAP_TOKENS)
    has_analysis_target = any((target.get("target_queue") == "analysis" or target.get("worker") in {"worker-2", "worker-4", "worker-5"}) for target in rework_targets)
    has_tables = any(int(tables.get(key) or 0) > 0 for key in ("supplementary_table_count", "pdf_table_count", "xml_table_locator_count"))
    image_count = len(images)
    if has_hard_missing:
        return (
            "not_digitizable_missing_source_data",
            "still_unrecoverable_backlog",
            "Do not launch owner-worker from the current packet; acquire missing source data/sequence/exact table material first, otherwise keep conflict/unresolved.",
            False,
            False,
            has_hard_missing,
        )
    if has_analysis and has_specific_figure_gap and has_analysis_target:
        return (
            "mixed_analysis_rework_plus_controlled_digitization_gap",
            "analysis_rework_candidate_not_auto_queued",
            "Run owner-worker analysis repair for table/entity/mechanism gaps; keep figure-only exact curve values unresolved unless a controlled digitization pass with QA is later performed.",
            False,
            True,
            False,
        )
    if has_analysis and (has_analysis_target or has_tables):
        return (
            "analysis_rework_from_existing_material",
            "analysis_rework_candidate_not_auto_queued",
            "Existing packet tables/locators or analysis tickets support targeted owner-worker repair; this is not a blind figure-digitization task.",
            False,
            True,
            False,
        )
    if has_figure and image_count > 0:
        return (
            "controlled_digitization_possible_but_requires_human_calibration",
            "manual_digitization_controlled_task",
            "Image evidence exists, but exact values require calibrated digitization and independent QA before any owner-worker can promote them.",
            True,
            False,
            False,
        )
    return (
        "not_digitizable_no_controlled_target",
        "still_unrecoverable_backlog",
        "No controlled local target was found; keep non-publication-grade until new source evidence is staged.",
        False,
        False,
        False,
    )


def build_tasks(
    paper_id: str,
    classification: str,
    recommended_queue: str,
    action: str,
    surfaces: list[dict[str, Any]],
    rework_targets: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    if "controlled_digitization" in classification or classification.startswith("mixed_"):
        for idx, surface in enumerate(surfaces or [{"label": "unspecified figure-only exact-value surface", "candidate_image_paths": []}], start=1):
            tasks.append(
                {
                    "task_id": f"md-{paper_id}-{idx:02d}",
                    "task_type": "controlled_digitization_task",
                    "status": "not_performed_requires_calibrated_human_or_vision_qa",
                    "target_surface": surface,
                    "required_output_fields": [
                        "axis_calibration_points",
                        "digitized_raw_points_or_bars",
                        "uncertainty_or_reading_error",
                        "independent_qa_reviewer",
                        "decision_do_not_promote_if_uncertain",
                    ],
                    "acceptance_rule": "Do not write recovered exact values into final artifacts until owner-worker source review plus worker-6 adjudication and strict gates pass.",
                }
            )
    if "analysis_rework" in recommended_queue or "analysis_rework" in classification or classification.startswith("mixed_"):
        for idx, target in enumerate(rework_targets, start=1):
            if target.get("target_queue") not in {"analysis", "adjudication", None, ""} and target.get("worker") not in {"worker-2", "worker-4", "worker-5", "worker-6"}:
                continue
            tasks.append(
                {
                    "task_id": f"ar-{paper_id}-{idx:02d}",
                    "task_type": "analysis_owner_rework_task",
                    "status": "pending_owner_worker_review",
                    "worker": target.get("worker") or target.get("owner_worker") or target.get("owner_workers"),
                    "layer": target.get("layer"),
                    "failure_code": target.get("failure_code") or target.get("omission_code"),
                    "artifact_path": target.get("artifact_path"),
                    "required_action": target.get("required_action") or target.get("reason"),
                    "source_evidence_to_check": target.get("source_evidence_to_check") or target.get("source_paths_to_check"),
                    "acceptance_rule": "Owner worker must reopen packet sources and then return to worker-6; final acceptance still requires semantic and publication-quality gates.",
                }
            )
    if classification.startswith("not_digitizable"):
        tasks.append(
            {
                "task_id": f"gap-{paper_id}-01",
                "task_type": "missing_source_blocker",
                "status": "blocked_until_new_primary_material",
                "recommended_queue": recommended_queue,
                "required_action": action,
                "unrecoverable_material_gaps": gaps,
                "acceptance_rule": "Do not rerun owner-worker from the same packet; acquire named source material or preserve source_conflict/unresolved.",
            }
        )
    return tasks


def process_one(row: dict[str, str], generated_at: str) -> dict[str, Any]:
    paper_id = row["paper_id"]
    packet = ROOT / "paper_packets" / paper_id
    paper = ROOT / "papers" / paper_id
    review = read_json(paper / "final" / "review_report.json", {}) or {}
    quality_feedback = read_json(paper / "work" / "review" / "quality_feedback.json", {}) or {}
    activity = read_json(paper / "final" / "activity_toxicity_evidence.json", {}) or {}
    database = read_json(paper / "final" / "database_record_verification.json", {}) or {}
    mechanism = read_json(paper / "final" / "mechanism_ontology_record.json", {}) or {}
    analysis_status = read_json(packet / "analysis" / "analysis_status.json", {}) or {}
    rework_targets = collect_rework_targets(review, quality_feedback)
    gaps = collect_unrecoverable_gaps(review, quality_feedback)
    codes = collect_failure_codes(review, quality_feedback, csv_codes=row.get("failure_codes") or row.get("feedback_failure_codes") or "")
    images = image_inventory(packet, paper)
    pdf_images = pdf_embedded_image_count(packet)
    tables = table_summary(packet)
    blob = collect_blob(row, review, quality_feedback, analysis_status)
    classification, recommended_queue, action, digitization_candidate, analysis_candidate, hard_missing = classify_candidate(
        codes, blob, tables, images, rework_targets
    )
    surfaces = infer_target_surfaces(codes, blob, images, rework_targets, gaps)
    tasks = build_tasks(paper_id, classification, recommended_queue, action, surfaces, rework_targets, gaps)
    paper_out = packet / "manual_digitization"
    feasibility = {
        "generated_at": generated_at,
        "paper_id": paper_id,
        "classification": classification,
        "recommended_queue": recommended_queue,
        "recommended_action": action,
        "publication_grade": review.get("publication_grade"),
        "review_status": review.get("review_status"),
        "failure_codes": codes,
        "digitization_candidate": digitization_candidate,
        "analysis_rework_candidate": analysis_candidate,
        "hard_missing_source_gap": hard_missing,
        "image_inventory_count": len(images),
        "pdf_embedded_image_count": pdf_images,
        "tables": tables,
        "target_surfaces": surfaces,
        "rework_target_count": len(rework_targets),
        "unrecoverable_gap_count": len(gaps),
        "strict_boundary": "Feasibility/task packaging only; no exact values are promoted and no paper becomes publication-grade from this script.",
    }
    task_manifest = {
        "generated_at": generated_at,
        "paper_id": paper_id,
        "tasks": tasks,
        "dispatch_status": "not_dispatched_to_owner_worker_by_this_script",
        "next_gate": "Run true owner-worker review only for analysis candidates or for digitization candidates after controlled calibrated evidence is attached.",
    }
    evidence = {
        "generated_at": generated_at,
        "paper_id": paper_id,
        "status": "no_exact_values_promoted",
        "digitized_value_count": 0,
        "analysis_value_promotion_count": 0,
        "reason": action,
        "candidate_image_paths": [item["path"] for item in images[:24]],
        "source_rework_targets": rework_targets,
        "unrecoverable_material_gaps": gaps,
        "quality_rule": "Keep source_conflict/unresolved unless controlled evidence plus owner-worker and worker-6 gates later pass.",
    }
    write_json(paper_out / "feasibility.json", feasibility)
    write_json(paper_out / "manual_digitization_tasks.json", task_manifest)
    write_json(paper_out / "digitization_evidence.json", evidence)
    return {
        "paper_id": paper_id,
        "classification": classification,
        "recommended_queue": recommended_queue,
        "recommended_action": action,
        "digitization_candidate": digitization_candidate,
        "analysis_rework_candidate": analysis_candidate,
        "hard_missing_source_gap": hard_missing,
        "review_status": review.get("review_status", ""),
        "publication_grade": review.get("publication_grade", ""),
        "failure_codes": codes,
        "activity_records": len(activity.get("activity_records") or []),
        "database_record_count": len(database.get("record_audits") or database.get("database_record_audits") or []),
        "mechanism_claim_count": len(mechanism.get("mechanism_claims") or []),
        "local_image_inventory_count": len(images),
        "pdf_embedded_image_count": pdf_images,
        "supplementary_table_count": tables["supplementary_table_count"],
        "pdf_table_count": tables["pdf_table_count"],
        "xml_table_locator_count": tables["xml_table_locator_count"],
        "target_surface_count": len(surfaces),
        "task_count": len(tasks),
        "rework_target_count": len(rework_targets),
        "unrecoverable_gap_count": len(gaps),
        "target_surfaces": [surface.get("label") for surface in surfaces],
        "task_packet_dir": rel(paper_out),
        "feasibility_json": rel(paper_out / "feasibility.json"),
        "task_manifest_json": rel(paper_out / "manual_digitization_tasks.json"),
        "digitization_evidence_json": rel(paper_out / "digitization_evidence.json"),
        "sample_image_paths": [item["path"] for item in images[:12]],
    }


def render_md(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Manual Digitization Processing Report",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        f"Completion claim: `{summary['completion_claim']}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in summary["classification_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            f"- `analysis_rework_candidate_count`: {summary['analysis_rework_candidate_count']}",
            f"- `controlled_digitization_candidate_count`: {summary['controlled_digitization_candidate_count']}",
            f"- `missing_source_blocker_count`: {summary['missing_source_blocker_count']}",
            "",
            "## Per Paper",
            "",
            "| paper_id | classification | queue | images | tables | tasks | action |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        table_total = int(row.get("supplementary_table_count") or 0) + int(row.get("pdf_table_count") or 0)
        lines.append(
            f"| `{row['paper_id']}` | `{row['classification']}` | `{row['recommended_queue']}` | "
            f"{row['local_image_inventory_count']} | {table_total} | {row['task_count']} | {row['recommended_action']} |"
        )
    lines.extend(
        [
            "",
            "## Quality Boundary",
            "",
            "- These artifacts are task packets only; they do not promote exact figure values.",
            "- A digitized value can be used only after calibrated extraction, independent QA, owner-worker source review, worker-6 adjudication, semantic gate, and publication-quality gate.",
            "- Missing source/sequence/source-data cases remain non-publication-grade until new primary material is acquired.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--out-prefix", type=Path, default=DEFAULT_OUT_PREFIX)
    parser.add_argument("--filter-target-queue", default="", help="Process only rows whose target_queue equals this value.")
    parser.add_argument("--filter-audit-bucket", default="", help="Process only rows whose audit_bucket equals this value.")
    parser.add_argument("--write-legacy-feasibility", action="store_true", default=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generated_at = now_iso()
    candidates = read_csv(args.candidates)
    if args.filter_target_queue:
        candidates = [row for row in candidates if row.get("target_queue") == args.filter_target_queue]
    if args.filter_audit_bucket:
        candidates = [row for row in candidates if row.get("audit_bucket") == args.filter_audit_bucket]
    rows = [process_one(row, generated_at) for row in candidates]
    classification_counts = Counter(row["classification"] for row in rows)
    queue_counts = Counter(row["recommended_queue"] for row in rows)
    summary = {
        "generated_at": generated_at,
        "completion_claim": "manual_digitization_task_packaging_only_no_publication_grade_change",
        "input_candidates": rel(args.candidates),
        "filter_target_queue": args.filter_target_queue,
        "filter_audit_bucket": args.filter_audit_bucket,
        "paper_count": len(rows),
        "classification_counts": dict(classification_counts),
        "recommended_queue_counts": dict(queue_counts),
        "analysis_rework_candidate_count": sum(1 for row in rows if row["analysis_rework_candidate"]),
        "controlled_digitization_candidate_count": sum(1 for row in rows if row["digitization_candidate"] or row["classification"].startswith("mixed_")),
        "missing_source_blocker_count": sum(1 for row in rows if row["hard_missing_source_gap"]),
        "exact_values_promoted": 0,
        "owner_worker_launch_allowed_by_this_script": False,
        "outputs": {
            "json": rel(args.out_prefix.with_suffix(".json")),
            "csv": rel(args.out_prefix.with_suffix(".csv")),
            "md": rel(args.out_prefix.with_suffix(".md")),
            "analysis_rework_candidates_csv": rel(WORK / "manual_digitization_analysis_rework_candidates_latest.csv"),
            "controlled_tasks_csv": rel(WORK / "manual_digitization_controlled_tasks_latest.csv"),
            "not_digitizable_csv": rel(WORK / "manual_digitization_not_digitizable_latest.csv"),
            "task_manifest_json": rel(WORK / "manual_digitization_task_manifest_latest.json"),
        },
    }
    payload = {"summary": summary, "rows": rows}
    fieldnames = [
        "paper_id",
        "classification",
        "recommended_queue",
        "recommended_action",
        "digitization_candidate",
        "analysis_rework_candidate",
        "hard_missing_source_gap",
        "review_status",
        "publication_grade",
        "failure_codes",
        "activity_records",
        "database_record_count",
        "mechanism_claim_count",
        "local_image_inventory_count",
        "pdf_embedded_image_count",
        "supplementary_table_count",
        "pdf_table_count",
        "xml_table_locator_count",
        "target_surface_count",
        "target_surfaces",
        "task_count",
        "rework_target_count",
        "unrecoverable_gap_count",
        "task_packet_dir",
        "feasibility_json",
        "task_manifest_json",
        "digitization_evidence_json",
        "sample_image_paths",
    ]
    write_json(args.out_prefix.with_suffix(".json"), payload)
    write_csv(args.out_prefix.with_suffix(".csv"), rows, fieldnames)
    args.out_prefix.with_suffix(".md").write_text(render_md(summary, rows), encoding="utf-8")
    write_csv(WORK / "manual_digitization_analysis_rework_candidates_latest.csv", [row for row in rows if row["analysis_rework_candidate"]], fieldnames)
    write_csv(WORK / "manual_digitization_controlled_tasks_latest.csv", [row for row in rows if row["digitization_candidate"] or row["classification"].startswith("mixed_")], fieldnames)
    write_csv(WORK / "manual_digitization_not_digitizable_latest.csv", [row for row in rows if row["hard_missing_source_gap"]], fieldnames)
    write_json(
        WORK / "manual_digitization_task_manifest_latest.json",
        {
            "generated_at": generated_at,
            "paper_count": len(rows),
            "paper_ids": [row["paper_id"] for row in rows],
            "classification_counts": dict(classification_counts),
            "rows": [
                {
                    "paper_id": row["paper_id"],
                    "classification": row["classification"],
                    "recommended_queue": row["recommended_queue"],
                    "task_packet_dir": row["task_packet_dir"],
                    "task_manifest_json": row["task_manifest_json"],
                }
                for row in rows
            ],
        },
    )
    if args.write_legacy_feasibility:
        legacy_summary = {
            "generated_at": generated_at,
            "paper_count": len(rows),
            "bucket_counts": dict(classification_counts),
            "completion_claim": "manual_digitization_feasibility_audit_only_no_publication_grade_change",
            "superseded_by": rel(args.out_prefix.with_suffix(".json")),
        }
        write_json(LEGACY_FEASIBILITY_PREFIX.with_suffix(".json"), {"summary": legacy_summary, "rows": rows})
        write_csv(LEGACY_FEASIBILITY_PREFIX.with_suffix(".csv"), rows, fieldnames)
        LEGACY_FEASIBILITY_PREFIX.with_suffix(".md").write_text(render_md(legacy_summary | {"classification_counts": dict(classification_counts), "analysis_rework_candidate_count": summary["analysis_rework_candidate_count"], "controlled_digitization_candidate_count": summary["controlled_digitization_candidate_count"], "missing_source_blocker_count": summary["missing_source_blocker_count"]}, rows), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
