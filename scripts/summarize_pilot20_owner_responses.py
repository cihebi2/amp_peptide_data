#!/usr/bin/env python3
"""Summarize owner-worker responses for pilot20 rework dispatch."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DISPATCH_ROOT = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "pilot20" / "source_review_packets" / "owner_rework_dispatch"
DISPATCH_INDEX = DISPATCH_ROOT / "dispatch_index_latest.csv"
OUTDIR = DISPATCH_ROOT / "owner_response_summary"


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


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def abs_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def concise(value: Any, limit: int = 260) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = " ".join(text.split())
    return text[: limit - 1] + "..." if len(text) > limit else text


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    run_id = stamp()
    dispatch_rows = read_csv(DISPATCH_INDEX)
    rows: list[dict[str, Any]] = []
    for dispatch in dispatch_rows:
        response_path = abs_path(dispatch["expected_response_path"])
        if response_path.exists():
            response = load_json(response_path)
            action = response.get("action_taken", "")
            checked_count = len(response.get("source_inputs_checked") or [])
            gaps_count = len(response.get("remaining_gaps") or [])
            files_count = len(response.get("files_to_update_or_review") or [])
            followup = response.get("worker6_followup_required", "")
            note = concise(response.get("owner_summary") or response.get("rationale") or response.get("remaining_gaps") or "")
        else:
            response = {}
            action = "missing_owner_response"
            checked_count = gaps_count = files_count = 0
            followup = ""
            note = ""
        rows.append(
            {
                **dispatch,
                "owner_response_path": rel(response_path),
                "action_taken": action,
                "source_inputs_checked_count": checked_count,
                "remaining_gaps_count": gaps_count,
                "files_to_update_or_review_count": files_count,
                "worker6_followup_required": str(followup).lower(),
                "note": note,
            }
        )

    fields = [
        "dispatch_id",
        "pilot_sample_id",
        "paper_id",
        "audit_record_id",
        "owner_worker",
        "severity",
        "target_queue",
        "ticket_id",
        "action_taken",
        "source_inputs_checked_count",
        "remaining_gaps_count",
        "files_to_update_or_review_count",
        "worker6_followup_required",
        "owner_response_path",
        "note",
    ]
    csv_path = OUTDIR / f"owner_response_summary_{run_id}.csv"
    latest_csv = OUTDIR / "owner_response_summary_latest.csv"
    write_csv(csv_path, rows, fields)
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")

    summary = {
        "generated_at": now_utc(),
        "completion_claim": "pilot20_owner_responses_summarized_not_worker6_final_acceptance",
        "dispatch_index": rel(DISPATCH_INDEX),
        "dispatch_count": len(rows),
        "action_counts": dict(Counter(row["action_taken"] for row in rows)),
        "owner_counts": dict(Counter(row["owner_worker"] for row in rows)),
        "worker6_followup_required_count": sum(1 for row in rows if row["worker6_followup_required"] == "true"),
        "missing_response_count": sum(1 for row in rows if row["action_taken"] == "missing_owner_response"),
        "outputs": {
            "summary_csv": rel(csv_path),
            "latest_summary_csv": rel(latest_csv),
            "summary_json": rel(OUTDIR / f"owner_response_summary_{run_id}.json"),
            "latest_summary_json": rel(OUTDIR / "owner_response_summary_latest.json"),
            "report_md": rel(OUTDIR / f"owner_response_report_{run_id}.md"),
            "latest_report_md": rel(OUTDIR / "owner_response_report_latest.md"),
        },
    }
    write_json(OUTDIR / f"owner_response_summary_{run_id}.json", summary)
    write_json(OUTDIR / "owner_response_summary_latest.json", summary)

    lines = [
        "# Pilot20 Owner-Worker Response Summary",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "These are owner-worker responses to the 11 pilot20 dispatch packets. They do not constitute worker-6 final acceptance.",
        "",
        "## Counts",
        "",
        "| action | count |",
        "| --- | ---: |",
    ]
    for action, count in sorted(summary["action_counts"].items()):
        lines.append(f"| `{action}` | {count} |")
    lines.extend(["", "## Per-Dispatch", "", "| dispatch | owner | paper | action | checked | gaps | worker-6 followup |", "| --- | --- | --- | --- | ---: | ---: | --- |"])
    for row in rows:
        lines.append(
            f"| `{row['dispatch_id']}` | `{row['owner_worker']}` | `{row['paper_id']}` | `{row['action_taken']}` | {row['source_inputs_checked_count']} | {row['remaining_gaps_count']} | `{row['worker6_followup_required']}` |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- `repair_ready` means the owner identified a safe repair/update path; worker-6 still must re-adjudicate.",
        "- `blocked_missing_material` or `needs_upstream_material` stays nonterminal and should not be promoted.",
        "- This summary does not edit canonical `final/` artifacts.",
        "",
    ])
    report = OUTDIR / f"owner_response_report_{run_id}.md"
    latest_report = OUTDIR / "owner_response_report_latest.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    latest_report.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
