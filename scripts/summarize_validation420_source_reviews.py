#!/usr/bin/env python3
"""Summarize validation420 paper-level source-review results."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "validation420" / "source_review_packets"
PACKET_INDEX = PACKET_ROOT / "packet_index_latest.csv"
OUTDIR = PACKET_ROOT / "summary"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except (ValueError, RuntimeError, OSError):
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
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())


def concise(value: Any, limit: int = 220) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = " ".join(text.split())
    return text[: limit - 1] + "..." if len(text) > limit else text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-index", type=Path, default=PACKET_INDEX)
    args = parser.parse_args()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    run_id = stamp()
    rows: list[dict[str, Any]] = []
    ticket_rows: list[dict[str, Any]] = []
    for index_row in read_csv(args.packet_index):
        packet_dir = ROOT / index_row["packet_dir"]
        result_path = ROOT / index_row["result_path"]
        result = load_json(result_path)
        sample_decisions = result.get("sample_row_decisions") or []
        row_decision_counts = Counter()
        if isinstance(sample_decisions, list):
            for item in sample_decisions:
                if isinstance(item, dict):
                    row_decision_counts[str(item.get("row_decision", ""))] += 1
        ticket_path = packet_dir / "rework_tickets.jsonl"
        ticket_count = count_jsonl(ticket_path)
        if ticket_count:
            for line in ticket_path.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.strip():
                    try:
                        ticket = json.loads(line)
                    except Exception:
                        ticket = {"_unparsed": line}
                    ticket_rows.append({**ticket, "review_sample_id": index_row["review_sample_id"], "paper_id": index_row["paper_id"], "ticket_path": rel(ticket_path)})
        rows.append({
            **index_row,
            "result_exists": str(result_path.exists()).lower(),
            "result_path": rel(result_path),
            "reviewed_at": result.get("reviewed_at", ""),
            "review_model": result.get("review_model", ""),
            "reasoning_effort": result.get("reasoning_effort", ""),
            "final_decision": result.get("final_decision", "missing_result"),
            "sample_row_decision_counts": json.dumps(dict(row_decision_counts), ensure_ascii=False, sort_keys=True),
            "sample_row_decision_total": sum(row_decision_counts.values()),
            "rework_target_count": len(result.get("rework_targets") or []) if isinstance(result.get("rework_targets") or [], list) else 0,
            "caution_count": len(result.get("caution_findings") or []) if isinstance(result.get("caution_findings") or [], list) else 0,
            "checked_input_count": len(result.get("checked_inputs") or []) if isinstance(result.get("checked_inputs") or [], list) else 0,
            "ticket_count": ticket_count,
            "note": concise(result.get("worker6_adjudication") or result.get("qc_summary") or ""),
        })
    fields = [
        "review_sample_id",
        "paper_id",
        "sample_count",
        "result_exists",
        "final_decision",
        "sample_row_decision_counts",
        "sample_row_decision_total",
        "rework_target_count",
        "caution_count",
        "ticket_count",
        "checked_input_count",
        "reviewed_at",
        "review_model",
        "reasoning_effort",
        "packet_dir",
        "result_path",
        "note",
    ]
    csv_path = OUTDIR / f"validation420_source_review_results_{run_id}.csv"
    latest_csv = OUTDIR / "validation420_source_review_results_latest.csv"
    write_csv(csv_path, rows, fields)
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")
    tickets_path = OUTDIR / f"validation420_rework_tickets_{run_id}.jsonl"
    latest_tickets = OUTDIR / "validation420_rework_tickets_latest.jsonl"
    with tickets_path.open("w", encoding="utf-8") as fh:
        for ticket in ticket_rows:
            fh.write(json.dumps(ticket, ensure_ascii=False, sort_keys=True) + "\n")
    latest_tickets.write_text(tickets_path.read_text(encoding="utf-8"), encoding="utf-8")
    row_decision_counts: Counter[str] = Counter()
    for row in rows:
        try:
            row_decision_counts.update(json.loads(row["sample_row_decision_counts"]))
        except Exception:
            pass
    summary = {
        "generated_at": now_utc(),
        "completion_claim": "validation420_source_review_summary_not_final_closure",
        "packet_index": rel(args.packet_index),
        "packet_count": len(rows),
        "result_count": sum(1 for row in rows if row["result_exists"] == "true"),
        "manifest_sample_rows": sum(int(row.get("sample_count") or 0) for row in rows),
        "reviewed_sample_rows": sum(int(row.get("sample_row_decision_total") or 0) for row in rows),
        "final_decision_counts": dict(Counter(row["final_decision"] for row in rows)),
        "sample_row_decision_counts": dict(row_decision_counts),
        "total_rework_targets": sum(int(row.get("rework_target_count") or 0) for row in rows),
        "total_cautions": sum(int(row.get("caution_count") or 0) for row in rows),
        "ticket_count": len(ticket_rows),
        "outputs": {
            "results_csv": rel(csv_path),
            "latest_results_csv": rel(latest_csv),
            "tickets_jsonl": rel(tickets_path),
            "latest_tickets_jsonl": rel(latest_tickets),
            "summary_json": rel(OUTDIR / f"validation420_source_review_summary_{run_id}.json"),
            "latest_summary_json": rel(OUTDIR / "validation420_source_review_summary_latest.json"),
            "report_md": rel(OUTDIR / f"validation420_source_review_report_{run_id}.md"),
            "latest_report_md": rel(OUTDIR / "validation420_source_review_report_latest.md"),
        },
    }
    write_json(OUTDIR / f"validation420_source_review_summary_{run_id}.json", summary)
    write_json(OUTDIR / "validation420_source_review_summary_latest.json", summary)
    lines = [
        "# Validation420 Source-Review Summary",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "This summarizes paper-level source-review results for the 420-row manual validation manifest. It is not final closure until owner rework and worker-6 final adjudication are completed.",
        "",
        "## Counts",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| packets / unique papers | {summary['packet_count']} |",
        f"| result JSON files | {summary['result_count']} |",
        f"| manifest sample rows | {summary['manifest_sample_rows']} |",
        f"| reviewed sample rows | {summary['reviewed_sample_rows']} |",
        f"| rework targets | {summary['total_rework_targets']} |",
        f"| cautions | {summary['total_cautions']} |",
        f"| tickets | {summary['ticket_count']} |",
        "",
        "## Final Decisions",
        "",
        "| final decision | count |",
        "| --- | ---: |",
    ]
    for decision, count in sorted(summary["final_decision_counts"].items()):
        lines.append(f"| `{decision}` | {count} |")
    lines.extend(["", "## Sample Row Decisions", "", "| row decision | count |", "| --- | ---: |"])
    for decision, count in sorted(summary["sample_row_decision_counts"].items()):
        lines.append(f"| `{decision}` | {count} |")
    report = OUTDIR / f"validation420_source_review_report_{run_id}.md"
    latest_report = OUTDIR / "validation420_source_review_report_latest.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    latest_report.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
