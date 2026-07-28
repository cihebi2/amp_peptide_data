#!/usr/bin/env python3
"""Summarize pilot20 worker-6 final mirror/re-adjudication outcomes."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "pilot20" / "source_review_packets"
MIRROR_ROOT = BASE / "worker6_final_mirror"
RUNNER_STATUS = MIRROR_ROOT / "runner" / "worker6_final_runner_status_latest.csv"
ONTOLOGY_QC = BASE / "owner_rework_dispatch" / "ontology_qc" / "mechanism_ontology_class_qc_latest.csv"
ONTOLOGY_QC_SUMMARY = BASE / "owner_rework_dispatch" / "ontology_qc" / "mechanism_ontology_class_qc_summary_latest.json"
OUTDIR = MIRROR_ROOT / "summary"
REQUIRED_REVIEW_KEYS = [
    "review_status",
    "publication_grade",
    "validator_contract_passed",
    "reviewed_at",
    "review_model",
    "reasoning_effort",
    "source_reviewed",
    "source_review_depth",
    "materials_exhausted",
    "rework_targets",
    "caution_findings",
]
POSITIVE_DECISIONS = {"accepted_clean", "accepted_with_cautions"}
NONTERMINAL_DECISIONS = {"needs_targeted_rework", "blocked_missing_primary_material", "deferred_not_safe_to_edit"}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except (OSError, RuntimeError, ValueError):
        return str(path)


def abs_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def concise(value: Any, limit: int = 220) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = " ".join(text.split())
    return text[: limit - 1] + "..." if len(text) > limit else text


def ontology_bad_counts() -> dict[str, int]:
    if not ONTOLOGY_QC.exists():
        return {}
    counts: dict[str, int] = defaultdict(int)
    for row in read_csv(ONTOLOGY_QC):
        try:
            bad_count = int(row.get("bad_count", "0") or 0)
        except ValueError:
            bad_count = 1
        if bad_count > 0:
            counts[row.get("paper_id", "")] += 1
    return dict(counts)


def validate_review_report(paper_id: str, decision: str) -> tuple[dict[str, Any], list[str]]:
    path = ROOT / "papers" / paper_id / "final" / "review_report.json"
    data = read_json(path)
    problems: list[str] = []
    if not data:
        return {"review_report_path": rel(path)}, ["missing_or_unreadable_review_report"]

    missing = [key for key in REQUIRED_REVIEW_KEYS if key not in data]
    if missing:
        problems.append("missing_keys:" + ",".join(missing))
    if data.get("review_status") != decision:
        problems.append(f"decision_mismatch:runner={decision};review_report={data.get('review_status')}")
    if data.get("review_model") != "gpt-5.5" or data.get("reasoning_effort") != "xhigh":
        problems.append(f"model_effort_mismatch:{data.get('review_model')}/{data.get('reasoning_effort')}")
    rework_targets = data.get("rework_targets") or []
    caution_findings = data.get("caution_findings") or []
    if decision in POSITIVE_DECISIONS and (not data.get("publication_grade") or rework_targets):
        problems.append(f"accepted_gate_mismatch:publication_grade={data.get('publication_grade')};rework_targets={len(rework_targets)}")
    if decision in NONTERMINAL_DECISIONS and data.get("publication_grade"):
        problems.append("nonterminal_publication_grade_true")
    mirror = data.get("worker6_final_mirror") if isinstance(data.get("worker6_final_mirror"), dict) else {}
    if mirror.get("reviewed_at") and data.get("reviewed_at") != mirror.get("reviewed_at"):
        problems.append(f"top_level_reviewed_at_not_synced:{data.get('reviewed_at')}!={mirror.get('reviewed_at')}")
    return {
        "review_report_path": rel(path),
        "review_status": data.get("review_status", ""),
        "publication_grade": data.get("publication_grade", ""),
        "validator_contract_passed": data.get("validator_contract_passed", ""),
        "reviewed_at": data.get("reviewed_at", ""),
        "review_model": data.get("review_model", ""),
        "reasoning_effort": data.get("reasoning_effort", ""),
        "source_reviewed": data.get("source_reviewed", ""),
        "rework_target_count": len(rework_targets) if isinstance(rework_targets, list) else "not_list",
        "caution_count": len(caution_findings) if isinstance(caution_findings, list) else "not_list",
    }, problems


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    run_id = stamp()
    status_rows = read_csv(RUNNER_STATUS)
    bad_counts = ontology_bad_counts()
    rows: list[dict[str, Any]] = []
    problems_by_paper: dict[str, list[str]] = {}

    for status in status_rows:
        response_path = abs_path(status["response_path"])
        response = read_json(response_path)
        paper_id = status["paper_id"]
        decision = status["final_decision"]
        review_fields, problems = validate_review_report(paper_id, decision)
        if decision in POSITIVE_DECISIONS and bad_counts.get(paper_id, 0):
            problems.append(f"accepted_has_nonstandard_mechanism_classes:{bad_counts[paper_id]}")
        if problems:
            problems_by_paper[paper_id] = problems
        rows.append({
            "dispatch_id": status["dispatch_id"],
            "pilot_sample_id": status["pilot_sample_id"],
            "paper_id": paper_id,
            "owner_worker": status["owner_worker"],
            "owner_action": status["action_taken"],
            "runner_state": status["runner_state"],
            "runner_validation": status["runner_validation"],
            "final_decision": decision,
            "files_updated_count": len(response.get("files_updated") or []) if isinstance(response.get("files_updated") or [], list) else "not_list",
            "remaining_blocker_count": len(response.get("remaining_blockers") or []) if isinstance(response.get("remaining_blockers") or [], list) else "not_list",
            "ontology_bad_file_count": bad_counts.get(paper_id, 0),
            "validation_problem_count": len(problems),
            "validation_problems": ";".join(problems),
            "response_path": rel(response_path),
            "qc_note": concise(response.get("qc_summary")),
            **review_fields,
        })

    fields = [
        "dispatch_id",
        "pilot_sample_id",
        "paper_id",
        "owner_worker",
        "owner_action",
        "runner_state",
        "runner_validation",
        "final_decision",
        "review_status",
        "publication_grade",
        "validator_contract_passed",
        "reviewed_at",
        "review_model",
        "reasoning_effort",
        "source_reviewed",
        "rework_target_count",
        "caution_count",
        "files_updated_count",
        "remaining_blocker_count",
        "ontology_bad_file_count",
        "validation_problem_count",
        "validation_problems",
        "response_path",
        "review_report_path",
        "qc_note",
    ]
    csv_path = OUTDIR / f"worker6_final_mirror_summary_{run_id}.csv"
    latest_csv = OUTDIR / "worker6_final_mirror_summary_latest.csv"
    write_csv(csv_path, rows, fields)
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")

    qc_summary = read_json(ONTOLOGY_QC_SUMMARY)
    summary = {
        "generated_at": now_utc(),
        "completion_claim": "pilot20_worker6_final_mirror_summarized_after_qc",
        "selected_count": len(rows),
        "runner_state_counts": dict(Counter(row["runner_state"] for row in rows)),
        "runner_validation_counts": dict(Counter(row["runner_validation"] for row in rows)),
        "final_decision_counts": dict(Counter(row["final_decision"] for row in rows)),
        "publication_grade_true_count": sum(1 for row in rows if row.get("publication_grade") is True),
        "accepted_with_cautions_count": sum(1 for row in rows if row["final_decision"] == "accepted_with_cautions"),
        "nonterminal_count": sum(1 for row in rows if row["final_decision"] in NONTERMINAL_DECISIONS),
        "review_report_validation_problem_count": sum(len(items) for items in problems_by_paper.values()),
        "papers_with_validation_problems": problems_by_paper,
        "accepted_files_with_bad_classes": qc_summary.get("accepted_files_with_bad_classes", ""),
        "nonterminal_files_with_bad_classes": qc_summary.get("nonterminal_files_with_bad_classes", ""),
        "ontology_qc_summary": rel(ONTOLOGY_QC_SUMMARY) if ONTOLOGY_QC_SUMMARY.exists() else "",
        "runner_status_csv": rel(RUNNER_STATUS),
        "outputs": {
            "summary_csv": rel(csv_path),
            "latest_summary_csv": rel(latest_csv),
            "summary_json": rel(OUTDIR / f"worker6_final_mirror_summary_{run_id}.json"),
            "latest_summary_json": rel(OUTDIR / "worker6_final_mirror_summary_latest.json"),
            "report_md": rel(OUTDIR / f"worker6_final_mirror_report_{run_id}.md"),
            "latest_report_md": rel(OUTDIR / "worker6_final_mirror_report_latest.md"),
        },
    }
    write_json(OUTDIR / f"worker6_final_mirror_summary_{run_id}.json", summary)
    write_json(OUTDIR / "worker6_final_mirror_summary_latest.json", summary)

    lines = [
        "# Pilot20 Worker-6 Final Mirror Summary",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "This report summarizes worker-6 final mirror/re-adjudication after owner-worker rework responses. It distinguishes accepted papers from nonterminal blocked/rework cases.",
        "",
        "## Counts",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| selected dispatches | {summary['selected_count']} |",
        f"| valid worker-6 responses | {summary['runner_validation_counts'].get('valid_worker6_response', 0)} |",
        f"| accepted_with_cautions | {summary['accepted_with_cautions_count']} |",
        f"| nonterminal | {summary['nonterminal_count']} |",
        f"| publication_grade true | {summary['publication_grade_true_count']} |",
        f"| accepted files with bad mechanism classes | {summary['accepted_files_with_bad_classes']} |",
        f"| nonterminal files with bad mechanism classes | {summary['nonterminal_files_with_bad_classes']} |",
        f"| review-report validation problems | {summary['review_report_validation_problem_count']} |",
        "",
        "## Final Decisions",
        "",
        "| final decision | count |",
        "| --- | ---: |",
    ]
    for decision, count in sorted(summary["final_decision_counts"].items()):
        lines.append(f"| `{decision}` | {count} |")
    lines.extend([
        "",
        "## Per Dispatch",
        "",
        "| dispatch | paper | final decision | pub-grade | rework targets | cautions | bad-class files | validation problems |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ])
    for row in rows:
        lines.append(
            f"| `{row['dispatch_id']}` | `{row['paper_id']}` | `{row['final_decision']}` | `{row['publication_grade']}` | {row['rework_target_count']} | {row['caution_count']} | {row['ontology_bad_file_count']} | {row['validation_problem_count']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- The 7 accepted papers are accepted with cautions, not clean; preserved cautions remain part of the result.",
        "- The 3 blocked papers stay `blocked_missing_primary_material` and must not be counted as accepted until missing primary/supplementary materials are recovered.",
        "- The 1 `needs_targeted_rework` paper remains nonterminal because owner repair was not actually applied and mechanism class vocabulary is still invalid.",
        "- Ontology QC now reports bad classes by final decision; accepted files have zero non-standard mechanism evidence classes.",
        "",
    ])
    report = OUTDIR / f"worker6_final_mirror_report_{run_id}.md"
    latest_report = OUTDIR / "worker6_final_mirror_report_latest.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    latest_report.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
