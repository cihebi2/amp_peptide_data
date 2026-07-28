#!/usr/bin/env python3
"""Leader-owned semantic assertions for PMC12019989 candidate 17."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[7]
BASE = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot"
PAPER_ID = "PMC12019989"
PAPER = BASE / "papers" / PAPER_ID
PACKET = BASE / "packets" / PAPER_ID
LOGS = BASE / "worker_logs" / PAPER_ID
EXPECTED_CONFLICTS = {
    "fig2-dose-fold-caption-vs-methods-legend",
    "fig2-timepoints-caption-vs-methods-axis",
    "fig2-y-unit-axis-vs-methods-caption",
    "fig2-global-legend-absolute-concentrations-vs-strain-specific-mic",
    "fig3-biofilm-reduction-vs-residual-mass-endpoint",
    "fig3-biofilm-fold-vs-absolute-concentration-and-strain",
    "fig4-figure-axis-vs-prose-unit",
    "fig4-caption-organ-matrix-omission",
    "fig4-prose-exact-value-dose-attribution",
    "fig6-survival-71.4-vs-75",
}
EXPECTED_MIC = {
    "Escherichia coli ATCC 8739": 3.13,
    "Escherichia coli Clinical Isolate 1": 3.13,
    "Escherichia coli Clinical Isolate 2": 6.25,
    "Klebsiella pneumoniae ATCC 700603": 12.5,
    "Pseudomonas aeruginosa ATCC 9027": 6.25,
    "Staphylococcus aureus ATCC 6538": 3.13,
    "Staphylococcus aureus Clinical Isolate 1": 6.25,
    "Staphylococcus aureus Clinical Isolate 2": 6.25,
    "Staphylococcus aureus Clinical Isolate 3": 12.5,
    "methicillin-resistant Staphylococcus aureus ATCC 43300": 12.5,
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_values(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if item_key == key:
                found.append(item_value)
            found.extend(find_values(item_value, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(find_values(item, key))
    return found


def contains_text(value: Any, needle: str) -> bool:
    return needle.lower() in json.dumps(value, ensure_ascii=False).lower()


def add_issue(issues: list[dict[str, Any]], code: str, path: Path | str, detail: Any) -> None:
    issues.append({"code": code, "path": str(path), "detail": detail})


def fig2_key_from_worker3(row: dict[str, Any]) -> tuple[Any, ...]:
    return (row.get("panel"), float(row.get("dose_fold_mic")), int(row.get("time_h")))


def fig2_key_from_final(row: dict[str, Any]) -> tuple[Any, ...]:
    assay = row.get("assay_conditions") or {}
    return (assay.get("panel"), float(assay.get("dose_fold_mic")), int(assay.get("time_h")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    issues: list[dict[str, Any]] = []

    paths = {
        "worker2": PAPER / "work/activity_evidence/activity_records.json",
        "worker3": PAPER / "work/supplementary_methods/supplementary_evidence.json",
        "worker4": PAPER / "work/database_record_audit/record_identity_audit.json",
        "activity": PAPER / "final/activity_toxicity_evidence.json",
        "database": PAPER / "final/database_record_verification.json",
        "mechanism": PAPER / "final/mechanism_ontology_record.json",
        "review": PAPER / "final/review_report.json",
        "leader_figure2": PAPER / "work/leader_preflight/leader_color_digitized_figure2.json",
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        add_issue(issues, "missing_required_artifact", PAPER, missing)
        payload = {"paper_id": PAPER_ID, "passed": False, "issue_count": len(issues), "issues": issues}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return 1

    data = {name: read_json(path) for name, path in paths.items()}

    for worker in ("worker-2", "worker-3", "worker-4", "worker-6"):
        report = read_json(LOGS / f"{worker}.run_report.json")
        if report.get("returncode") != 0 or report.get("codex_model") != "gpt-5.5" or report.get("codex_reasoning_effort") != "xhigh":
            add_issue(issues, "canonical_worker_runtime_mismatch", LOGS / f"{worker}.run_report.json", {
                "returncode": report.get("returncode"),
                "codex_model": report.get("codex_model"),
                "codex_reasoning_effort": report.get("codex_reasoning_effort"),
            })

    for name in ("worker2", "worker4"):
        artifact = data[name]
        if artifact.get("review_model") != "gpt-5.5" or artifact.get("reasoning_effort") != "xhigh":
            add_issue(issues, "owner_artifact_runtime_metadata_mismatch", paths[name], {
                "review_model": artifact.get("review_model"),
                "reasoning_effort": artifact.get("reasoning_effort"),
            })

    observations = (data["worker3"].get("quantitative_figure_repair") or {}).get("observations") or []
    fig2_worker3 = [row for row in observations if row.get("figure") == "Figure 2"]
    if len(fig2_worker3) != 240:
        add_issue(issues, "worker3_figure2_count", paths["worker3"], len(fig2_worker3))
    numeric_worker3 = [row for row in fig2_worker3 if isinstance(row.get("raw_value"), (int, float)) and not isinstance(row.get("raw_value"), bool)]
    if len(numeric_worker3) != 240:
        add_issue(issues, "worker3_figure2_non_numeric_values", paths["worker3"], 240 - len(numeric_worker3))
    unique_values = {round(float(row["raw_value"]), 4) for row in numeric_worker3}
    if len(unique_values) < 30:
        add_issue(issues, "worker3_figure2_degenerate_values", paths["worker3"], {"unique_value_count": len(unique_values), "values": sorted(unique_values)[:40]})

    curves: dict[tuple[Any, Any], list[dict[str, Any]]] = defaultdict(list)
    for row in fig2_worker3:
        curves[(row.get("panel"), row.get("dose_fold_mic"))].append(row)
    if len(curves) != 30:
        add_issue(issues, "worker3_figure2_curve_count", paths["worker3"], len(curves))
    for curve_key, rows in sorted(curves.items(), key=str):
        times = {row.get("time_h") for row in rows}
        values = {row.get("raw_value") for row in rows}
        y_coords = {
            (row.get("image_coordinate_px") or {}).get("y")
            for row in rows
        }
        if times != {0, 1, 2, 3, 4, 5, 12, 24}:
            add_issue(issues, "worker3_curve_time_grid", paths["worker3"], {"curve": curve_key, "times": sorted(times, key=str)})
        if len(values) < 3 or len(y_coords) < 3:
            add_issue(issues, "worker3_curve_is_constant_or_placeholder", paths["worker3"], {
                "curve": curve_key,
                "unique_values": len(values),
                "unique_y_coordinates": len(y_coords),
            })

    worker3_by_key = {fig2_key_from_worker3(row): row for row in fig2_worker3}
    leader_figure2 = data["leader_figure2"].get("observations") or []
    leader_by_key = {fig2_key_from_worker3(row): row for row in leader_figure2}
    if len(leader_by_key) != 240:
        add_issue(issues, "leader_figure2_scaffold_key_count", paths["leader_figure2"], len(leader_by_key))
    for key, leader_row in leader_by_key.items():
        worker_row = worker3_by_key.get(key)
        if worker_row is None:
            continue
        worker_value = worker_row.get("raw_value")
        leader_value = leader_row.get("raw_value")
        if not isinstance(worker_value, (int, float)) or abs(float(worker_value) - float(leader_value)) > 0.75:
            add_issue(issues, "worker3_value_outside_leader_color_digitization_tolerance", paths["worker3"], {
                "key": key,
                "worker3": worker_value,
                "leader_color_digitization": leader_value,
                "absolute_tolerance": 0.75,
            })
        worker_coordinate = worker_row.get("image_coordinate_px") or {}
        leader_coordinate = leader_row.get("image_coordinate_px") or {}
        if not isinstance(worker_coordinate.get("x"), (int, float)) or not isinstance(worker_coordinate.get("y"), (int, float)):
            add_issue(issues, "worker3_coordinate_not_numeric", paths["worker3"], {"key": key, "coordinate": worker_coordinate})
        elif abs(float(worker_coordinate["x"]) - float(leader_coordinate["x"])) > 10 or abs(float(worker_coordinate["y"]) - float(leader_coordinate["y"])) > 12:
            add_issue(issues, "worker3_coordinate_outside_leader_color_digitization_tolerance", paths["worker3"], {
                "key": key,
                "worker3": worker_coordinate,
                "leader_color_digitization": leader_coordinate,
                "x_tolerance_px": 10,
                "y_tolerance_px": 12,
            })
    spot_ranges = {
        ("A", 0.5, 0): (5.3, 6.8),
        ("A", 1.0, 0): (5.3, 6.8),
        ("A", 5.0, 0): (5.3, 6.8),
        ("A", 0.5, 24): (1.5, 3.0),
        ("A", 1.0, 24): (0.0, 0.5),
        ("A", 5.0, 24): (0.0, 0.5),
        ("F", 5.0, 1): (0.0, 0.8),
        ("I", 0.5, 24): (4.0, 6.0),
        ("I", 5.0, 24): (0.0, 0.5),
        ("J", 0.5, 24): (1.5, 2.8),
        ("J", 1.0, 24): (0.0, 0.8),
        ("J", 5.0, 24): (0.0, 0.4),
    }
    for key, (minimum, maximum) in spot_ranges.items():
        row = worker3_by_key.get(key)
        value = row.get("raw_value") if row else None
        if not isinstance(value, (int, float)) or not minimum <= float(value) <= maximum:
            add_issue(issues, "worker3_visual_spot_check_failed", paths["worker3"], {
                "key": key,
                "raw_value": value,
                "allowed_range": [minimum, maximum],
            })

    activity = data["activity"]
    records = activity.get("activity_records") or []
    toxicity = activity.get("toxicity_records") or []
    if len(records) != 279 or len(toxicity) != 0:
        add_issue(issues, "final_layer2_count_mismatch", paths["activity"], {"activity": len(records), "toxicity": len(toxicity)})
    final_fig2 = [row for row in records if str(row.get("record_id") or "").startswith("fig2-")]
    if len(final_fig2) != 240:
        add_issue(issues, "final_figure2_count", paths["activity"], len(final_fig2))
    final_by_key = {fig2_key_from_final(row): row for row in final_fig2}
    if len(final_by_key) != 240:
        add_issue(issues, "final_figure2_unique_key_count", paths["activity"], len(final_by_key))
    for key, source_row in worker3_by_key.items():
        final_row = final_by_key.get(key)
        if final_row is None:
            add_issue(issues, "final_missing_worker3_observation", paths["activity"], key)
            continue
        final_value = final_row.get("raw_value")
        source_value = source_row.get("raw_value")
        if not isinstance(final_value, (int, float)) or isinstance(final_value, bool):
            add_issue(issues, "final_figure2_raw_value_not_numeric", paths["activity"], {"key": key, "raw_value": final_value})
        elif isinstance(source_value, (int, float)) and abs(float(final_value) - float(source_value)) > 1e-9:
            add_issue(issues, "final_worker3_value_not_integrated", paths["activity"], {"key": key, "final": final_value, "worker3": source_value})
        if not final_row.get("figure_quantitation") or not final_row.get("calibration_evidence"):
            add_issue(issues, "final_figure2_provenance_missing", paths["activity"], key)
    if contains_text(activity, "pending_worker3_digitization"):
        add_issue(issues, "pending_worker3_placeholder_survives", paths["activity"], "pending_worker3_digitization")
    if contains_text(activity, "does not contain worker-3 digitized"):
        add_issue(issues, "stale_pre_digitization_note_survives", paths["activity"], "does not contain worker-3 digitized")

    mic_rows = [row for row in records if row.get("endpoint") == "MIC"]
    observed_mic = {}
    for row in mic_rows:
        target = row.get("target")
        target_label = target.get("source_label") if isinstance(target, dict) else str(target)
        observed_mic[target_label] = float(row.get("raw_value"))
    if observed_mic != EXPECTED_MIC:
        add_issue(issues, "figure1_mic_contract_mismatch", paths["activity"], observed_mic)
    conflict_ids = {row.get("conflict_id") for row in activity.get("source_conflicts_preserved") or []}
    if conflict_ids != EXPECTED_CONFLICTS:
        add_issue(issues, "source_conflict_set_mismatch", paths["activity"], {
            "missing": sorted(EXPECTED_CONFLICTS - conflict_ids),
            "extra": sorted(conflict_ids - EXPECTED_CONFLICTS),
        })

    shared_reviewed_at = set()
    for name in ("activity", "database", "mechanism"):
        artifact = data[name]
        required = {
            "review_status": "accepted_with_cautions",
            "publication_grade": True,
            "review_model": "gpt-5.5",
            "reasoning_effort": "xhigh",
            "source_reviewed": True,
        }
        for key, expected in required.items():
            if artifact.get(key) != expected:
                add_issue(issues, "final_layer_adjudication_metadata", paths[name], {"field": key, "expected": expected, "actual": artifact.get(key)})
        if not artifact.get("reviewed_at"):
            add_issue(issues, "final_layer_reviewed_at_missing", paths[name], None)
        else:
            shared_reviewed_at.add(artifact.get("reviewed_at"))
        adjudication = artifact.get("worker6_adjudication") or {}
        if adjudication.get("worker") != "worker-6" or adjudication.get("decision") != "accepted_with_cautions" or adjudication.get("source_reviewed") is not True:
            add_issue(issues, "final_layer_worker6_adjudication", paths[name], adjudication)
    if len(shared_reviewed_at) != 1:
        add_issue(issues, "final_layer_reviewed_at_not_shared", PAPER / "final", sorted(shared_reviewed_at))

    database = data["database"]
    paper_identity = database.get("paper_local_identity") or {}
    if paper_identity.get("entity") != "SK1260" or paper_identity.get("sequence") != "KAFAVKFAWKFHAWKAWKKAW" or paper_identity.get("sequence_length") != 21 or paper_identity.get("status") != "source_verified":
        add_issue(issues, "paper_local_identity_contract", paths["database"], paper_identity)
    if paper_identity.get("terminal_modifications") != "not explicitly reported":
        add_issue(issues, "terminal_modification_boundary", paths["database"], paper_identity.get("terminal_modifications"))
    audits = database.get("record_audits") or []
    if len(audits) != 13 or {row.get("status") for row in audits} != {"unresolved_record"}:
        add_issue(issues, "fallback_record_status_category", paths["database"], {
            "count": len(audits),
            "statuses": sorted({str(row.get("status")) for row in audits}),
        })
    recursive_authoritative_true = sum(value is True for value in find_values(database, "authoritative_dbaasp_ingest_ready"))
    if recursive_authoritative_true:
        add_issue(issues, "recursive_authoritative_true", paths["database"], recursive_authoritative_true)

    review = data["review"]
    caution_text = json.dumps(review.get("caution_findings") or [], ensure_ascii=False).lower()
    if "toxicity" not in caution_text or "zero" not in caution_text and "no source" not in caution_text:
        add_issue(issues, "review_missing_no_toxicity_caution", paths["review"], review.get("caution_findings"))

    mirror_pairs = [
        (PAPER / "final/activity_toxicity_evidence.json", PACKET / "final/activity_toxicity_evidence.json"),
        (PAPER / "final/database_record_verification.json", PACKET / "final/database_record_verification.json"),
        (PAPER / "final/mechanism_ontology_record.json", PACKET / "final/mechanism_evidence.json"),
        (PAPER / "final/review_report.json", PACKET / "final/review_report.json"),
    ]
    mirror_results = []
    for paper_path, packet_path in mirror_pairs:
        match = paper_path.exists() and packet_path.exists() and sha256(paper_path) == sha256(packet_path)
        mirror_results.append({"paper": str(paper_path), "packet": str(packet_path), "byte_identical": match})
        if not match:
            add_issue(issues, "paper_packet_mirror_mismatch", paper_path, str(packet_path))

    payload = {
        "paper_id": PAPER_ID,
        "passed": not issues,
        "issue_count": len(issues),
        "issues": issues,
        "metrics": {
            "worker3_figure2_observations": len(fig2_worker3),
            "worker3_figure2_unique_values": len(unique_values),
            "worker3_figure2_curve_count": len(curves),
            "leader_figure2_scaffold_rows": len(leader_by_key),
            "final_activity_records": len(records),
            "final_toxicity_records": len(toxicity),
            "final_figure2_records": len(final_fig2),
            "final_figure1_mic_records": len(mic_rows),
            "source_conflict_count": len(conflict_ids),
            "recursive_authoritative_true": recursive_authoritative_true,
            "shared_final_reviewed_at_count": len(shared_reviewed_at),
            "mirror_results": mirror_results,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": payload["passed"], "issue_count": payload["issue_count"], "output": str(output)}, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
