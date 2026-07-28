#!/usr/bin/env python3
"""Execute QA over the accepted-sample audit queue.

This is a verification pass only: it reruns strict gates and checks review
provenance fields. It does not edit paper artifacts and does not promote a
paper to clean/publication-grade by itself.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_true_rework_queue import ensure_manifest, open_ticket_ids, read_json, run_gates


REQUIRED_REVIEW_FIELDS = [
    "reviewed_at",
    "review_model",
    "reasoning_effort",
    "checked_inputs",
    "materials_exhausted",
    "semantic_quality_checks",
    "per_layer_decision_rationale",
    "rework_targets",
    "caution_findings",
    "publication_grade",
    "validator_contract_passed",
    "source_review_depth",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_stamp() -> str:
    return now_utc().replace("-", "").replace(":", "")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_items(path: Path) -> list[dict[str, Any]]:
    data = read_json(path)
    items = data.get("items") or []
    if not isinstance(items, list):
        raise SystemExit(f"items must be a list: {path}")
    return [item for item in items if isinstance(item, dict)]


def review_field_issues(review: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for field in REQUIRED_REVIEW_FIELDS:
        if field not in review:
            issues.append(f"missing_review_field:{field}")
    if review.get("source_reviewed") is not True and review.get("source_review_depth") not in {"source_reviewed", "publication_grade"}:
        issues.append("source_review_not_explicit")
    if review.get("review_model") and str(review.get("review_model")) != "gpt-5.5":
        issues.append("review_model_not_gpt_5_5")
    if review.get("reasoning_effort") and str(review.get("reasoning_effort")).lower() not in {"high", "xhigh"}:
        issues.append("reasoning_effort_not_high_or_xhigh")
    rework_targets = review.get("rework_targets")
    if isinstance(rework_targets, list) and rework_targets:
        issues.append("review_report_has_open_rework_targets")
    return issues


def audit_one(repo: Path, item: dict[str, Any], index: int) -> dict[str, Any]:
    paper_id = str(item.get("paper_id") or "")
    result: dict[str, Any] = {
        "paper_id": paper_id,
        "audit_reason": item.get("audit_reason"),
        "source_refined_status": item.get("refined_status"),
        "sample_key": item.get("sample_key"),
        "passed": False,
        "issue_codes": [],
    }
    try:
        manifest = ensure_manifest(repo, paper_id)
        gate = run_gates(repo, paper_id, manifest, index, "accepted_sample_audit")
        paper_review_path = repo / "papers" / paper_id / "final" / "review_report.json"
        packet_review_path = repo / "paper_packets" / paper_id / "final" / "review_report.json"
        review = read_json(paper_review_path)
        packet_review = read_json(packet_review_path)
        field_issues = review_field_issues(review)
        ticket_ids = open_ticket_ids(repo, paper_id)
        issue_codes = list(field_issues)
        if not gate.get("passed"):
            issue_codes.append("strict_gate_failed_on_sample_audit")
        if ticket_ids:
            issue_codes.append("open_rework_tickets_present")
        if not packet_review:
            issue_codes.append("packet_review_report_missing_or_unreadable")
        result.update(
            {
                "passed": not issue_codes,
                "issue_codes": sorted(set(issue_codes)),
                "manifest": str(manifest),
                "gate": gate,
                "review_report": str(paper_review_path),
                "packet_review_report": str(packet_review_path),
                "open_rework_ticket_ids": ticket_ids,
                "checked_review_fields": REQUIRED_REVIEW_FIELDS,
            }
        )
    except Exception as exc:  # noqa: BLE001 - audit must continue across papers
        result.update(
            {
                "passed": False,
                "issue_codes": ["sample_audit_exception"],
                "exception_type": type(exc).__name__,
                "exception": str(exc),
            }
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default="reports/followup_queues/true_rework_queue_next500_obtainable_20260505_accepted_sample_audit.json",
        help="Accepted sample audit manifest.",
    )
    parser.add_argument("--out-dir", default="reports/accepted_sample_audit")
    parser.add_argument("--run-label", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path.cwd()
    manifest_path = Path(args.manifest)
    items = load_items(manifest_path)
    results = []
    for index, item in enumerate(items, start=1):
        print(f"[{index}/{len(items)}] accepted sample audit {item.get('paper_id')}", flush=True)
        results.append(audit_one(repo, item, index))
    issue_counts = Counter(code for result in results for code in result.get("issue_codes") or [])
    passed_count = sum(1 for result in results if result.get("passed"))
    report = {
        "generated_at": now_utc(),
        "run_label": args.run_label,
        "source_manifest": str(manifest_path),
        "completion_claim": "accepted_sample_audit_verification_not_publication_grade_completion",
        "paper_count": len(results),
        "passed_count": passed_count,
        "failed_count": len(results) - passed_count,
        "issue_counts": dict(sorted(issue_counts.items())),
        "results": results,
    }
    prefix = args.run_label or f"accepted_sample_audit_{safe_stamp()}"
    out_dir = Path(args.out_dir)
    out = out_dir / f"{prefix}.json"
    latest = out_dir / "accepted_sample_audit_latest.json"
    write_json(out, report)
    write_json(latest, report)
    print(json.dumps({"ok": True, "out": str(out), "latest": str(latest), "paper_count": len(results), "passed_count": passed_count, "failed_count": len(results) - passed_count, "issue_counts": report["issue_counts"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
