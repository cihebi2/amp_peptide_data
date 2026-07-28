#!/usr/bin/env python3
"""Summarize pilot-20 true source-review results and tickets."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = (
    ROOT
    / "reports"
    / "nar_resource_freeze_v1"
    / "manual_validation"
    / "pilot20"
    / "source_review_packets"
)
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
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def concise(value: Any, limit: int = 260) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = " ".join(text.split())
    if len(text) > limit:
        return text[: limit - 1] + "..."
    return text


def caution_scopes(result: dict[str, Any]) -> list[str]:
    scopes: list[str] = []
    for item in result.get("caution_findings") or []:
        if isinstance(item, dict):
            scopes.append(str(item.get("scope") or item.get("caution_code") or item.get("failure_code") or "unknown"))
    return scopes


def rework_codes(result: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for item in result.get("rework_targets") or []:
        if isinstance(item, dict):
            codes.append(str(item.get("failure_code") or item.get("failure_type") or item.get("layer") or "unknown"))
    return codes


def best_effort_codes(result: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for item in result.get("best_effort_limits") or []:
        if isinstance(item, dict):
            codes.append(str(item.get("limit_code") or item.get("scope") or item.get("reason") or "unknown"))
        else:
            codes.append(str(item))
    return codes


def substantive_flag(result: dict[str, Any]) -> str:
    decision = str(result.get("decision", ""))
    if decision in {"needs_targeted_rework", "blocked_missing_primary_material"}:
        return decision
    if result.get("rework_targets"):
        return "has_rework_targets_despite_best_effort"
    text = json.dumps(result.get("worker6_adjudication") or {}, ensure_ascii=False).lower()
    if "needs_targeted_rework" in text:
        return "worker6_mentions_needs_targeted_rework"
    if "accepted_with_cautions" in text:
        return "accepted_with_cautions_substantive"
    if decision == "unverifiable_best_effort":
        return "best_effort_unverifiable_no_hard_rework"
    return decision or "unknown"


def has_model_provenance_downgrade(result: dict[str, Any]) -> bool:
    if result.get("decision") != "unverifiable_best_effort":
        return False
    text = json.dumps(result, ensure_ascii=False).lower()
    return "model_provenance" in text or "model/effort" in text or "cannot prove" in text or "runtime" in text


def ticket_payload(packet_dir: Path, result: dict[str, Any], row: dict[str, str]) -> list[dict[str, Any]]:
    ticket_path = packet_dir / "rework_ticket.json"
    if ticket_path.exists():
        ticket = load_json(ticket_path)
        if ticket:
            return [{**ticket, "_source_ticket_path": rel(ticket_path)}]
    tickets = []
    for idx, target in enumerate(result.get("rework_targets") or [], 1):
        tickets.append(
            {
                "ticket_id": f"pilot20-aggregate-{row['pilot_sample_id']}-{idx:02d}",
                "paper_id": row["paper_id"],
                "audit_record_id": row["audit_record_id"],
                "target_queue": "analysis",
                "severity": "major" if result.get("decision") != "blocked_missing_primary_material" else "blocking",
                "requested_by": "pilot20_true_source_review_aggregate",
                "reason": concise(target, 700),
                "requested_outputs": [target],
                "blocks": ["true_source_review_acceptance"],
                "created_at": now_utc(),
                "_source_ticket_path": "",
            }
        )
    return tickets


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    run_id = stamp()
    index_rows = read_csv(PACKET_INDEX)
    rows: list[dict[str, Any]] = []
    tickets: list[dict[str, Any]] = []

    for index_row in index_rows:
        packet_dir = ROOT / index_row["packet_dir"]
        result_path = packet_dir / "true_review_result.json"
        result = load_json(result_path)
        row = {
            **index_row,
            "result_path": rel(result_path),
            "decision": result.get("decision", ""),
            "confidence": result.get("confidence", ""),
            "reviewed_at": result.get("reviewed_at", ""),
            "review_model": result.get("review_model", ""),
            "reasoning_effort": result.get("reasoning_effort", ""),
            "checked_input_count": len(result.get("checked_inputs") or []),
            "rework_target_count": len(result.get("rework_targets") or []),
            "caution_count": len(result.get("caution_findings") or []),
            "best_effort_limit_count": len(result.get("best_effort_limits") or []),
            "caution_scopes": ";".join(caution_scopes(result)),
            "rework_codes": ";".join(rework_codes(result)),
            "best_effort_codes": ";".join(best_effort_codes(result)),
            "substantive_flag": substantive_flag(result),
            "model_provenance_downgrade": str(has_model_provenance_downgrade(result)).lower(),
        }
        rows.append(row)
        tickets.extend(ticket_payload(packet_dir, result, row))

    decision_counts = Counter(row["decision"] for row in rows)
    substantive_counts = Counter(row["substantive_flag"] for row in rows)
    status_decision_counts: dict[str, dict[str, int]] = defaultdict(dict)
    for row in rows:
        status = row.get("status", "")
        decision = row.get("decision", "")
        status_decision_counts[status][decision] = status_decision_counts[status].get(decision, 0) + 1

    fields = [
        "pilot_sample_id",
        "paper_id",
        "database",
        "source_id",
        "audit_record_id",
        "status",
        "decision",
        "substantive_flag",
        "confidence",
        "reviewed_at",
        "review_model",
        "reasoning_effort",
        "checked_input_count",
        "rework_target_count",
        "caution_count",
        "best_effort_limit_count",
        "model_provenance_downgrade",
        "rework_codes",
        "caution_scopes",
        "best_effort_codes",
        "result_path",
        "packet_dir",
    ]
    csv_path = OUTDIR / f"pilot20_true_source_review_results_{run_id}.csv"
    latest_csv = OUTDIR / "pilot20_true_source_review_results_latest.csv"
    write_csv(csv_path, rows, fields)
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")

    tickets_path = OUTDIR / f"pilot20_true_source_review_rework_tickets_{run_id}.jsonl"
    latest_tickets = OUTDIR / "pilot20_true_source_review_rework_tickets_latest.jsonl"
    with tickets_path.open("w", encoding="utf-8") as fh:
        for ticket in tickets:
            fh.write(json.dumps(ticket, ensure_ascii=False, sort_keys=True) + "\n")
    latest_tickets.write_text(tickets_path.read_text(encoding="utf-8"), encoding="utf-8")

    summary = {
        "generated_at": now_utc(),
        "completion_claim": "pilot20_true_source_review_completed_not_publication_grade_batch_acceptance",
        "packet_index": rel(PACKET_INDEX),
        "result_count": len(rows),
        "decision_counts": dict(decision_counts),
        "substantive_flag_counts": dict(substantive_counts),
        "status_decision_counts": status_decision_counts,
        "model_provenance_downgrade_count": sum(1 for row in rows if row["model_provenance_downgrade"] == "true"),
        "total_rework_targets": sum(int(row["rework_target_count"]) for row in rows),
        "total_cautions": sum(int(row["caution_count"]) for row in rows),
        "total_best_effort_limits": sum(int(row["best_effort_limit_count"]) for row in rows),
        "consolidated_ticket_count": len(tickets),
        "outputs": {
            "results_csv": rel(csv_path),
            "latest_results_csv": rel(latest_csv),
            "tickets_jsonl": rel(tickets_path),
            "latest_tickets_jsonl": rel(latest_tickets),
            "summary_json": rel(OUTDIR / f"pilot20_true_source_review_summary_{run_id}.json"),
            "latest_summary_json": rel(OUTDIR / "pilot20_true_source_review_summary_latest.json"),
            "report_md": rel(OUTDIR / f"pilot20_true_source_review_report_{run_id}.md"),
            "latest_report_md": rel(OUTDIR / "pilot20_true_source_review_report_latest.md"),
        },
    }
    summary_path = OUTDIR / f"pilot20_true_source_review_summary_{run_id}.json"
    latest_summary = OUTDIR / "pilot20_true_source_review_summary_latest.json"
    write_json(summary_path, summary)
    write_json(latest_summary, summary)

    report_path = OUTDIR / f"pilot20_true_source_review_report_{run_id}.md"
    latest_report = OUTDIR / "pilot20_true_source_review_report_latest.md"
    lines = [
        "# Pilot20 True Source-Review Summary",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "This summarizes fresh Codex CLI source-review results for the 20-paper pilot. It supersedes the earlier structural/status-evidence `pass=20` interpretation for these 20 papers.",
        "",
        "## Headline",
        "",
        f"- Result JSON files: `{summary['result_count']}` / 20.",
        f"- Runner validation: see `reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/runner/true_source_review_summary_latest.json`.",
        f"- Clean `pass_source_review`: `{decision_counts.get('pass_source_review', 0)}`.",
        f"- Accepted with cautions confirmed: `{decision_counts.get('accepted_with_cautions_confirmed', 0)}`.",
        f"- Needs targeted rework: `{decision_counts.get('needs_targeted_rework', 0)}`.",
        f"- Unverifiable after best effort: `{decision_counts.get('unverifiable_best_effort', 0)}`.",
        f"- Consolidated rework/material tickets: `{len(tickets)}`.",
        "",
        "## Decision Counts",
        "",
        "| decision | count |",
        "| --- | ---: |",
    ]
    for decision, count in sorted(decision_counts.items()):
        lines.append(f"| `{decision}` | {count} |")
    lines.extend(["", "## Substantive Flags", "", "| flag | count |", "| --- | ---: |"])
    for flag, count in sorted(substantive_counts.items()):
        lines.append(f"| `{flag}` | {count} |")
    lines.extend(["", "## Per-Paper Results", "", "| pilot | status | database | paper | decision | substantive flag | rework | cautions | limits |", "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |"])
    for row in rows:
        lines.append(
            f"| `{row['pilot_sample_id']}` | `{row['status']}` | `{row['database']}` | `{row['paper_id']}` | `{row['decision']}` | `{row['substantive_flag']}` | {row['rework_target_count']} | {row['caution_count']} | {row['best_effort_limit_count']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- The earlier `pilot20` structural checker proved evidence pointers were usable; it did not prove scientific acceptance.",
        "- Fresh source review found no clean `pass_source_review` cases in this pilot.",
        "- Most nonterminal results are not proof that the database row is wrong; they mean the reviewer found preserved cautions, material limits, ontology repair needs, or insufficient proof to promote the row to clean acceptance.",
        "- Several `unverifiable_best_effort` decisions are affected by model-provenance self-verification caution even though the runner command and stderr header record `gpt-5.5` and `xhigh`; the prompt should be revised before scaling to 420 rows so the reviewer can treat runner provenance as sufficient runtime evidence.",
        "- Rows with `needs_targeted_rework` or non-empty rework targets must be sent back to the owner lane and then re-adjudicated by worker-6 before publication-grade acceptance.",
        "",
        "## Outputs",
        "",
        f"- Results CSV: `{rel(latest_csv)}`",
        f"- Consolidated tickets JSONL: `{rel(latest_tickets)}`",
        f"- Summary JSON: `{rel(latest_summary)}`",
        "",
    ])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    latest_report.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
