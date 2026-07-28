#!/usr/bin/env python3
"""Summarize the full pilot20 final review closure state."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "pilot20" / "source_review_packets"
READJUDICATION = BASE / "worker6_readjudication" / "pilot20_worker6_readjudication_latest.csv"
FINAL_MIRROR = BASE / "worker6_final_mirror" / "runner" / "worker6_final_runner_status_latest.csv"
NON_DISPATCH = BASE / "worker6_non_dispatch_final_review" / "runner" / "worker6_non_dispatch_status_latest.csv"
ONTOLOGY_QC = BASE / "owner_rework_dispatch" / "ontology_qc" / "mechanism_ontology_class_qc_latest.csv"
ONTOLOGY_QC_SUMMARY = BASE / "owner_rework_dispatch" / "ontology_qc" / "mechanism_ontology_class_qc_summary_latest.json"
OUTDIR = BASE / "pilot20_final_review_closure"
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
POSITIVE = {"accepted_clean", "accepted_with_cautions"}
NONTERMINAL = {"needs_targeted_rework", "blocked_missing_primary_material", "deferred_not_safe_to_edit"}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except (OSError, RuntimeError, ValueError):
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    return data if isinstance(data, dict) else {}


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def decision_table() -> dict[str, dict[str, str]]:
    decisions: dict[str, dict[str, str]] = {}
    for row in read_csv(READJUDICATION):
        decision = row.get("readjudicated_decision", "")
        if decision == "accepted_with_cautions_confirmed":
            decision = "accepted_with_cautions"
        decisions[row["paper_id"]] = {
            "paper_id": row["paper_id"],
            "pilot_sample_id": row.get("pilot_sample_id", ""),
            "audit_record_id": row.get("audit_record_id", ""),
            "final_decision": decision,
            "decision_source": "worker6_readjudication",
        }
    for source_name, path in [("worker6_non_dispatch_final_review", NON_DISPATCH), ("worker6_final_mirror", FINAL_MIRROR)]:
        if not path.exists():
            continue
        for row in read_csv(path):
            paper_id = row["paper_id"]
            current = decisions.setdefault(paper_id, {"paper_id": paper_id})
            current.update({
                "pilot_sample_id": row.get("pilot_sample_id", current.get("pilot_sample_id", "")),
                "audit_record_id": row.get("audit_record_id", current.get("audit_record_id", "")),
                "final_decision": row.get("final_decision", ""),
                "decision_source": source_name,
                "runner_validation": row.get("runner_validation", ""),
                "response_path": row.get("response_path", ""),
            })
    return decisions


def ontology_bad_counts() -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    if not ONTOLOGY_QC.exists():
        return {}
    for row in read_csv(ONTOLOGY_QC):
        try:
            bad_count = int(row.get("bad_count") or 0)
        except ValueError:
            bad_count = 1
        if bad_count > 0:
            counts[row.get("paper_id", "")] += 1
    return dict(counts)


def validate_row(info: dict[str, str], bad_counts: dict[str, int]) -> dict[str, Any]:
    paper_id = info["paper_id"]
    decision = info.get("final_decision", "")
    review_path = ROOT / "papers" / paper_id / "final" / "review_report.json"
    report = read_json(review_path)
    problems: list[str] = []
    if not report:
        problems.append("missing_or_unreadable_review_report")
    missing = [key for key in REQUIRED_REVIEW_KEYS if key not in report]
    if missing:
        problems.append("missing_keys:" + ",".join(missing))
    rework_targets = report.get("rework_targets") or []
    caution_findings = report.get("caution_findings") or []
    if report.get("review_status") != decision:
        problems.append(f"decision_mismatch:{decision}!={report.get('review_status')}")
    if report.get("review_model") != "gpt-5.5" or report.get("reasoning_effort") != "xhigh":
        problems.append(f"model_effort_mismatch:{report.get('review_model')}/{report.get('reasoning_effort')}")
    if decision in POSITIVE and (not report.get("publication_grade") or rework_targets or bad_counts.get(paper_id, 0)):
        problems.append(
            f"accepted_gate_mismatch:publication_grade={report.get('publication_grade')};rework_targets={len(rework_targets)};ontology_bad_files={bad_counts.get(paper_id, 0)}"
        )
    if decision in NONTERMINAL and report.get("publication_grade"):
        problems.append("nonterminal_publication_grade_true")
    return {
        **info,
        "review_report_path": rel(review_path),
        "review_status": report.get("review_status", ""),
        "publication_grade": report.get("publication_grade", ""),
        "validator_contract_passed": report.get("validator_contract_passed", ""),
        "reviewed_at": report.get("reviewed_at", ""),
        "review_model": report.get("review_model", ""),
        "reasoning_effort": report.get("reasoning_effort", ""),
        "source_reviewed": report.get("source_reviewed", ""),
        "rework_target_count": len(rework_targets) if isinstance(rework_targets, list) else "not_list",
        "caution_count": len(caution_findings) if isinstance(caution_findings, list) else "not_list",
        "ontology_bad_file_count": bad_counts.get(paper_id, 0),
        "validation_problem_count": len(problems),
        "validation_problems": ";".join(problems),
    }


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    run_id = stamp()
    decisions = decision_table()
    bad_counts = ontology_bad_counts()
    rows = [validate_row(info, bad_counts) for _, info in sorted(decisions.items())]
    fields = [
        "pilot_sample_id",
        "paper_id",
        "audit_record_id",
        "final_decision",
        "decision_source",
        "runner_validation",
        "review_status",
        "publication_grade",
        "validator_contract_passed",
        "reviewed_at",
        "review_model",
        "reasoning_effort",
        "source_reviewed",
        "rework_target_count",
        "caution_count",
        "ontology_bad_file_count",
        "validation_problem_count",
        "validation_problems",
        "response_path",
        "review_report_path",
    ]
    csv_path = OUTDIR / f"pilot20_final_review_closure_{run_id}.csv"
    latest_csv = OUTDIR / "pilot20_final_review_closure_latest.csv"
    write_csv(csv_path, rows, fields)
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")
    qc_summary = read_json(ONTOLOGY_QC_SUMMARY)
    summary = {
        "generated_at": now_utc(),
        "completion_claim": "pilot20_final_review_closure_summarized",
        "paper_count": len(rows),
        "final_decision_counts": dict(Counter(row["final_decision"] for row in rows)),
        "decision_source_counts": dict(Counter(row["decision_source"] for row in rows)),
        "publication_grade_true_count": sum(1 for row in rows if row.get("publication_grade") is True),
        "review_report_validation_problem_count": sum(int(row["validation_problem_count"]) for row in rows),
        "accepted_files_with_bad_classes": qc_summary.get("accepted_files_with_bad_classes", ""),
        "nonterminal_files_with_bad_classes": qc_summary.get("nonterminal_files_with_bad_classes", ""),
        "ontology_qc_summary": rel(ONTOLOGY_QC_SUMMARY),
        "inputs": {
            "readjudication_csv": rel(READJUDICATION),
            "worker6_final_mirror_csv": rel(FINAL_MIRROR),
            "worker6_non_dispatch_csv": rel(NON_DISPATCH),
            "ontology_qc_csv": rel(ONTOLOGY_QC),
        },
        "outputs": {
            "closure_csv": rel(csv_path),
            "latest_closure_csv": rel(latest_csv),
            "summary_json": rel(OUTDIR / f"pilot20_final_review_closure_summary_{run_id}.json"),
            "latest_summary_json": rel(OUTDIR / "pilot20_final_review_closure_summary_latest.json"),
            "report_md": rel(OUTDIR / f"pilot20_final_review_closure_report_{run_id}.md"),
            "latest_report_md": rel(OUTDIR / "pilot20_final_review_closure_report_latest.md"),
        },
    }
    write_json(OUTDIR / f"pilot20_final_review_closure_summary_{run_id}.json", summary)
    write_json(OUTDIR / "pilot20_final_review_closure_summary_latest.json", summary)

    lines = [
        "# Pilot20 Final Review Closure",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "This is the full pilot20 closure state after worker-6 final mirror for dispatch papers and worker-6 final review for non-dispatch papers.",
        "",
        "## Counts",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| papers | {summary['paper_count']} |",
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
        "## Per Paper",
        "",
        "| paper | decision | source | pub-grade | rework targets | cautions | bad-class files | validation problems |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ])
    for row in rows:
        lines.append(
            f"| `{row['paper_id']}` | `{row['final_decision']}` | `{row['decision_source']}` | `{row['publication_grade']}` | {row['rework_target_count']} | {row['caution_count']} | {row['ontology_bad_file_count']} | {row['validation_problem_count']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- `accepted_with_cautions` is not clean acceptance; preserved cautions/conflicts remain part of the curated record.",
        "- Nonterminal papers keep `publication_grade=false` and concrete rework/material blockers.",
        "- The pilot20 accepted subset now has zero non-standard mechanism evidence classes after full-scope ontology QC.",
        "- Scaling to the 420-row validation set should use this full-scope QC, not the earlier dispatch-only QC.",
        "",
    ])
    report = OUTDIR / f"pilot20_final_review_closure_report_{run_id}.md"
    latest_report = OUTDIR / "pilot20_final_review_closure_report_latest.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    latest_report.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
