#!/usr/bin/env python3
"""Check validation420 source-review packet outputs at a pause/checkpoint."""

from __future__ import annotations

import argparse
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
    / "validation420"
    / "source_review_packets"
)
PACKET_INDEX = PACKET_ROOT / "packet_index_latest.csv"
OUTDIR = PACKET_ROOT / "summary"

ALLOWED_FINAL_DECISIONS = {
    "accepted_clean",
    "accepted_with_cautions",
    "needs_targeted_rework",
    "blocked_missing_primary_material",
    "unverifiable_best_effort",
    "deferred_not_safe_to_edit",
}
ALLOWED_ROW_DECISIONS = {
    "confirmed",
    "confirmed_with_caution",
    "needs_targeted_rework",
    "blocked_missing_primary_material",
    "unverifiable_best_effort",
    "not_applicable",
}
HARD_ROW_DECISIONS = {"needs_targeted_rework", "blocked_missing_primary_material"}
REQUIRED_RESULT_KEYS = {
    "paper_id",
    "review_sample_id",
    "reviewed_at",
    "review_model",
    "reasoning_effort",
    "final_decision",
    "sample_row_decisions",
    "material_review",
    "worker6_adjudication",
    "rework_targets",
    "caution_findings",
    "checked_inputs",
}
REQUIRED_ROW_KEYS = {
    "sample_id",
    "audit_record_id",
    "row_decision",
    "evidence_summary",
    "locators_checked",
    "cautions",
    "rework_target_ids",
}
REQUIRED_TICKET_KEYS = {
    "ticket_id",
    "paper_id",
    "target_queue",
    "owner_worker",
    "severity",
    "reason",
    "requested_outputs",
    "blocks",
    "created_at",
}
STANDARD_PACKET_INPUTS = {
    "validation_samples.json",
    "release_rows.json",
    "sample_final_records.json",
    "source_locator_hints.json",
    "material_inventory.json",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except (OSError, RuntimeError, ValueError):
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_dict(path: Path) -> dict[str, Any]:
    try:
        data = load_json(path)
    except Exception as exc:  # noqa: BLE001
        return {"_load_error": f"{type(exc).__name__}: {exc}"}
    return data if isinstance(data, dict) else {"_load_error": "not_a_json_object"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_validation_sample_ids(packet_dir: Path) -> set[str]:
    try:
        data = load_json(packet_dir / "validation_samples.json")
    except Exception:
        return set()
    if not isinstance(data, list):
        return set()
    return {str(item.get("sample_id", "")) for item in data if isinstance(item, dict) and item.get("sample_id")}


def read_tickets(ticket_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    tickets: list[dict[str, Any]] = []
    errors: list[str] = []
    if not ticket_path.exists():
        return tickets, errors
    for lineno, line in enumerate(ticket_path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"line {lineno}: unreadable_json:{type(exc).__name__}")
            continue
        if isinstance(data, dict):
            tickets.append(data)
        else:
            errors.append(f"line {lineno}: not_a_json_object")
    return tickets, errors


def has_standard_input_marker(checked_inputs: list[Any], marker: str) -> bool:
    return any(marker in str(item) for item in checked_inputs)


def validate_packet(index_row: dict[str, str]) -> dict[str, Any]:
    packet_dir = ROOT / index_row["packet_dir"]
    result_path = ROOT / index_row["result_path"]
    ticket_path = packet_dir / "rework_tickets.jsonl"
    status_path = packet_dir / "runner_status.json"
    runner_status = load_json_dict(status_path) if status_path.exists() else {}
    problems: list[str] = []
    warnings: list[str] = []
    info: dict[str, Any] = {
        "review_sample_id": index_row["review_sample_id"],
        "paper_id": index_row["paper_id"],
        "packet_dir": rel(packet_dir),
        "result_path": rel(result_path),
        "sample_count": int(index_row.get("sample_count") or 0),
        "result_exists": result_path.exists(),
        "runner_status_exists": status_path.exists(),
        "runner_state": runner_status.get("runner_state", ""),
        "runner_validation": runner_status.get("runner_validation", ""),
        "runner_returncode": runner_status.get("returncode", ""),
        "contract_pass": False,
        "blocking_problem_count": 0,
        "warning_count": 0,
    }
    if not result_path.exists():
        info.update(
            {
                "final_decision": "missing_result",
                "sample_row_decision_total": 0,
                "ticket_count": 0,
                "problems": problems,
                "warnings": warnings,
            }
        )
        return info

    result = load_json_dict(result_path)
    if "_load_error" in result:
        problems.append(f"result_load_error:{result['_load_error']}")
        info.update(
            {
                "final_decision": "invalid_result",
                "sample_row_decision_total": 0,
                "ticket_count": 0,
                "problems": problems,
                "warnings": warnings,
                "blocking_problem_count": len(problems),
            }
        )
        return info

    missing_keys = sorted(REQUIRED_RESULT_KEYS - set(result))
    if missing_keys:
        problems.append("missing_result_keys:" + ",".join(missing_keys))
    if result.get("paper_id") != index_row["paper_id"]:
        problems.append(f"paper_id_mismatch:{result.get('paper_id')}")
    if result.get("review_sample_id") != index_row["review_sample_id"]:
        problems.append(f"review_sample_id_mismatch:{result.get('review_sample_id')}")
    if result.get("review_model") != "gpt-5.5":
        problems.append(f"review_model_mismatch:{result.get('review_model')}")
    if result.get("reasoning_effort") != "xhigh":
        problems.append(f"reasoning_effort_mismatch:{result.get('reasoning_effort')}")

    final_decision = str(result.get("final_decision", ""))
    if final_decision not in ALLOWED_FINAL_DECISIONS:
        problems.append(f"unknown_final_decision:{final_decision}")

    sample_decisions = result.get("sample_row_decisions")
    if not isinstance(sample_decisions, list) or not sample_decisions:
        problems.append("missing_sample_row_decisions")
        sample_decisions = []

    expected_sample_ids = read_validation_sample_ids(packet_dir)
    seen_sample_ids: list[str] = []
    row_decision_counts: Counter[str] = Counter()
    row_rework_ids: set[str] = set()
    rows_with_locator_count = 0
    rows_with_evidence_summary_count = 0
    for pos, item in enumerate(sample_decisions, 1):
        if not isinstance(item, dict):
            problems.append(f"sample_row_{pos}:not_object")
            continue
        missing_row_keys = sorted(REQUIRED_ROW_KEYS - set(item))
        if missing_row_keys:
            problems.append(f"sample_row_{pos}:missing_keys:{','.join(missing_row_keys)}")
        sample_id = str(item.get("sample_id", ""))
        if sample_id:
            seen_sample_ids.append(sample_id)
        row_decision = str(item.get("row_decision", ""))
        row_decision_counts[row_decision] += 1
        if row_decision not in ALLOWED_ROW_DECISIONS:
            problems.append(f"sample_row_{sample_id or pos}:unknown_row_decision:{row_decision}")
        if isinstance(item.get("locators_checked"), list) and item["locators_checked"]:
            rows_with_locator_count += 1
        else:
            problems.append(f"sample_row_{sample_id or pos}:missing_locators_checked")
        if str(item.get("evidence_summary", "")).strip():
            rows_with_evidence_summary_count += 1
        else:
            problems.append(f"sample_row_{sample_id or pos}:missing_evidence_summary")
        for target_id in item.get("rework_target_ids") or []:
            row_rework_ids.add(str(target_id))

    if len(sample_decisions) != int(index_row.get("sample_count") or 0):
        problems.append(
            f"sample_row_count_mismatch:expected={index_row.get('sample_count')},actual={len(sample_decisions)}"
        )
    if expected_sample_ids and set(seen_sample_ids) != expected_sample_ids:
        missing = sorted(expected_sample_ids - set(seen_sample_ids))
        extra = sorted(set(seen_sample_ids) - expected_sample_ids)
        problems.append(f"sample_id_coverage_mismatch:missing={missing},extra={extra}")
    if len(seen_sample_ids) != len(set(seen_sample_ids)):
        problems.append("duplicate_sample_ids")

    checked_inputs = result.get("checked_inputs")
    if not isinstance(checked_inputs, list) or not checked_inputs:
        problems.append("missing_checked_inputs")
        checked_inputs = []
    missing_standard_inputs = sorted(
        marker for marker in STANDARD_PACKET_INPUTS if not has_standard_input_marker(checked_inputs, marker)
    )
    if missing_standard_inputs:
        warnings.append("checked_inputs_missing_standard_packet_files:" + ",".join(missing_standard_inputs))

    rework_targets = result.get("rework_targets")
    if not isinstance(rework_targets, list):
        problems.append("rework_targets_not_array")
        rework_targets = []
    rework_target_ids = {str(item.get("target_id") or item.get("ticket_id") or item.get("id") or "") for item in rework_targets if isinstance(item, dict)}
    rework_target_ids.discard("")
    if row_rework_ids and rework_target_ids and not row_rework_ids <= rework_target_ids:
        missing = sorted(row_rework_ids - rework_target_ids)
        warnings.append(f"row_rework_ids_not_all_in_rework_targets:{missing}")

    caution_findings = result.get("caution_findings")
    if not isinstance(caution_findings, list):
        problems.append("caution_findings_not_array")
        caution_findings = []

    tickets, ticket_errors = read_tickets(ticket_path)
    for error in ticket_errors:
        problems.append(f"ticket_parse_error:{error}")
    for ticket in tickets:
        missing_ticket_keys = sorted(REQUIRED_TICKET_KEYS - set(ticket))
        if missing_ticket_keys:
            problems.append(f"ticket_missing_keys:{ticket.get('ticket_id','?')}:{','.join(missing_ticket_keys)}")
        if ticket.get("paper_id") != index_row["paper_id"]:
            problems.append(f"ticket_paper_id_mismatch:{ticket.get('ticket_id','?')}")

    has_hard_rows = any(decision in HARD_ROW_DECISIONS for decision in row_decision_counts)
    has_hard_final = final_decision in {"needs_targeted_rework", "blocked_missing_primary_material"}
    if final_decision == "accepted_clean":
        if row_decision_counts - Counter({"confirmed": row_decision_counts.get("confirmed", 0)}):
            problems.append("accepted_clean_has_non_confirmed_rows")
        if rework_targets or tickets or caution_findings:
            problems.append("accepted_clean_has_rework_ticket_or_caution")
    if final_decision == "accepted_with_cautions":
        if has_hard_rows or rework_targets or tickets:
            problems.append("accepted_with_cautions_has_hard_rows_or_rework")
        if not caution_findings and not row_decision_counts.get("confirmed_with_caution"):
            warnings.append("accepted_with_cautions_without_cautions")
    if has_hard_rows and not has_hard_final:
        problems.append("hard_row_decision_without_hard_final_decision")
    if has_hard_final and not tickets:
        problems.append("hard_final_decision_missing_rework_tickets_jsonl")
    if has_hard_final and not rework_targets:
        problems.append("hard_final_decision_missing_rework_targets")

    info.update(
        {
            "final_decision": final_decision,
            "sample_row_decision_counts": dict(row_decision_counts),
            "sample_row_decision_total": len(sample_decisions),
            "checked_input_count": len(checked_inputs),
            "rows_with_locator_count": rows_with_locator_count,
            "rows_with_evidence_summary_count": rows_with_evidence_summary_count,
            "rework_target_count": len(rework_targets),
            "caution_count": len(caution_findings),
            "ticket_count": len(tickets),
            "problems": problems,
            "warnings": warnings,
            "blocking_problem_count": len(problems),
            "warning_count": len(warnings),
            "contract_pass": not problems,
        }
    )
    return info


def recover_missing_runner_status(row: dict[str, str], packet: dict[str, Any]) -> None:
    if not packet.get("result_exists") or not packet.get("contract_pass"):
        return
    packet_dir = ROOT / row["packet_dir"]
    status_path = packet_dir / "runner_status.json"
    if status_path.exists():
        return
    status = {
        **row,
        "runner_state": "paused_child_completed_valid_result",
        "runner_validation": "valid_result_json",
        "final_decision": packet.get("final_decision", ""),
        "reviewed_row_count": packet.get("sample_row_decision_total", 0),
        "started_at": "",
        "finished_at": "",
        "status_recovered_at": now_utc(),
        "elapsed_seconds": "",
        "returncode": "not_reaped_parent_sigstop",
        "stdout_log": rel(packet_dir / "codex_exec.stdout.log"),
        "stderr_log": rel(packet_dir / "codex_exec.stderr.log"),
        "last_message_path": rel(packet_dir / "CODEX_LAST_MESSAGE.md"),
        "status_recovery_note": "Runner parent was SIGSTOP-paused before it could reap this completed child; true_review_result.json passed checkpoint QA.",
    }
    write_json(status_path, status)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-index", type=Path, default=PACKET_INDEX)
    parser.add_argument("--outdir", type=Path, default=OUTDIR)
    parser.add_argument("--recover-missing-runner-status", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.packet_index)
    packets = [validate_packet(row) for row in rows]
    row_by_id = {row["review_sample_id"]: row for row in rows}
    if args.recover_missing_runner_status:
        for packet in packets:
            recover_missing_runner_status(row_by_id[packet["review_sample_id"]], packet)

    result_packets = [packet for packet in packets if packet["result_exists"]]
    missing_packets = [packet for packet in packets if not packet["result_exists"]]
    contract_failed = [packet for packet in result_packets if not packet["contract_pass"]]
    final_counts = Counter(packet["final_decision"] for packet in packets)
    runner_state_counts = Counter(packet.get("runner_state", "") for packet in packets if packet.get("runner_status_exists"))
    runner_validation_counts = Counter(packet.get("runner_validation", "") for packet in packets if packet.get("runner_status_exists"))
    invalid_runner_packets = [
        packet
        for packet in packets
        if packet.get("runner_status_exists") and packet.get("runner_validation") != "valid_result_json"
    ]
    row_decision_counts: Counter[str] = Counter()
    for packet in result_packets:
        row_decision_counts.update(packet.get("sample_row_decision_counts") or {})

    run_id = stamp()
    summary = {
        "generated_at": now_utc(),
        "claim": "validation420_pause_checkpoint_source_review_contract_qa_not_final_closure",
        "packet_index": rel(args.packet_index),
        "packet_count": len(packets),
        "result_count": len(result_packets),
        "missing_result_count": len(missing_packets),
        "reviewed_sample_rows": sum(int(packet.get("sample_row_decision_total") or 0) for packet in result_packets),
        "manifest_sample_rows": sum(int(row.get("sample_count") or 0) for row in rows),
        "contract_pass_count": sum(1 for packet in result_packets if packet["contract_pass"]),
        "contract_fail_count": len(contract_failed),
        "blocking_problem_count": sum(int(packet["blocking_problem_count"]) for packet in result_packets),
        "warning_count": sum(int(packet["warning_count"]) for packet in result_packets),
        "runner_status_count": sum(1 for packet in packets if packet.get("runner_status_exists")),
        "runner_valid_result_count": sum(
            1 for packet in packets if packet.get("runner_validation") == "valid_result_json"
        ),
        "runner_invalid_result_count": len(invalid_runner_packets),
        "runner_no_status_count": sum(1 for packet in packets if not packet.get("runner_status_exists")),
        "runner_state_counts": dict(runner_state_counts),
        "runner_validation_counts": dict(runner_validation_counts),
        "final_decision_counts": dict(final_counts),
        "sample_row_decision_counts": dict(row_decision_counts),
        "total_rework_targets": sum(int(packet.get("rework_target_count") or 0) for packet in result_packets),
        "total_tickets": sum(int(packet.get("ticket_count") or 0) for packet in result_packets),
        "total_cautions": sum(int(packet.get("caution_count") or 0) for packet in result_packets),
        "contract_failed_packets": contract_failed,
        "invalid_runner_status_packets": invalid_runner_packets,
        "missing_result_packets": missing_packets,
    }

    args.outdir.mkdir(parents=True, exist_ok=True)
    json_path = args.outdir / f"validation420_pause_checkpoint_qa_{run_id}.json"
    latest_json = args.outdir / "validation420_pause_checkpoint_qa_latest.json"
    md_path = args.outdir / f"validation420_pause_checkpoint_qa_{run_id}.md"
    latest_md = args.outdir / "validation420_pause_checkpoint_qa_latest.md"
    write_json(json_path, summary)
    write_json(latest_json, summary)

    examples_by_decision: dict[str, list[str]] = defaultdict(list)
    for packet in result_packets:
        if len(examples_by_decision[packet["final_decision"]]) < 5:
            examples_by_decision[packet["final_decision"]].append(packet["review_sample_id"])

    lines = [
        "# Validation420 Pause Checkpoint QA",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "This checks source-review output contracts for existing packet results only. It is not final closure and does not replace owner rework plus worker-6 final adjudication.",
        "",
        "## Counts",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| packets | {summary['packet_count']} |",
        f"| result files | {summary['result_count']} |",
        f"| missing results | {summary['missing_result_count']} |",
        f"| reviewed sample rows | {summary['reviewed_sample_rows']} |",
        f"| manifest sample rows | {summary['manifest_sample_rows']} |",
        f"| contract pass among result files | {summary['contract_pass_count']} |",
        f"| contract fail among result files | {summary['contract_fail_count']} |",
        f"| blocking output problems | {summary['blocking_problem_count']} |",
        f"| warnings | {summary['warning_count']} |",
        f"| runner status files | {summary['runner_status_count']} |",
        f"| runner valid results | {summary['runner_valid_result_count']} |",
        f"| runner invalid/interrupted | {summary['runner_invalid_result_count']} |",
        f"| runner no status | {summary['runner_no_status_count']} |",
        f"| rework targets | {summary['total_rework_targets']} |",
        f"| tickets | {summary['total_tickets']} |",
        f"| cautions | {summary['total_cautions']} |",
        "",
        "## Final Decisions",
        "",
        "| decision | count | example packets |",
        "| --- | ---: | --- |",
    ]
    for decision, count in sorted(summary["final_decision_counts"].items()):
        examples = ", ".join(examples_by_decision.get(decision, []))
        lines.append(f"| `{decision}` | {count} | {examples} |")
    lines.extend(["", "## Sample Row Decisions", "", "| row decision | count |", "| --- | ---: |"])
    for decision, count in sorted(summary["sample_row_decision_counts"].items()):
        lines.append(f"| `{decision}` | {count} |")
    lines.extend(["", "## Contract Failures", ""])
    if contract_failed:
        for packet in contract_failed[:50]:
            lines.append(
                f"- `{packet['review_sample_id']}` `{packet['paper_id']}`: "
                + "; ".join(packet.get("problems") or [])
            )
    else:
        lines.append("- None among existing result files.")
    lines.extend(["", "## Runner Invalid / Interrupted", ""])
    if invalid_runner_packets:
        for packet in invalid_runner_packets[:50]:
            lines.append(
                f"- `{packet['review_sample_id']}` `{packet['paper_id']}`: "
                f"`{packet.get('runner_state')}` / `{packet.get('runner_validation')}` / returncode `{packet.get('runner_returncode')}`"
            )
    else:
        lines.append("- None.")
    lines.extend(["", "## Missing Results", ""])
    lines.append(f"- {len(missing_packets)} packets have not produced `true_review_result.json` yet.")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(
        json.dumps(
            {
                k: v
                for k, v in summary.items()
                if k not in {"contract_failed_packets", "invalid_runner_status_packets", "missing_result_packets"}
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    print(f"json={rel(json_path)}")
    print(f"md={rel(md_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
