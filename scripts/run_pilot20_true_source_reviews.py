#!/usr/bin/env python3
"""Run pilot-20 true source-review Codex jobs with bounded parallelism."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET_INDEX = (
    ROOT
    / "reports"
    / "nar_resource_freeze_v1"
    / "manual_validation"
    / "pilot20"
    / "source_review_packets"
    / "packet_index_latest.csv"
)
MERGED_CORPUS_ROOT = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus")


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def abs_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except (ValueError, RuntimeError, OSError):
        return str(path)


def validate_result(path: Path) -> tuple[bool, str, str]:
    if not path.exists():
        return False, "missing_result_json", ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - status summary should capture exact failure.
        return False, f"unreadable_result_json:{type(exc).__name__}", ""
    required = [
        "paper_id",
        "pilot_sample_id",
        "audit_record_id",
        "review_model",
        "reasoning_effort",
        "decision",
        "checked_inputs",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        return False, "missing_required_keys:" + ",".join(missing), str(data.get("decision", ""))
    if data.get("review_model") != "gpt-5.5" or data.get("reasoning_effort") != "xhigh":
        return False, "model_or_reasoning_mismatch", str(data.get("decision", ""))
    decision = str(data.get("decision", ""))
    allowed = {
        "pass_source_review",
        "accepted_with_cautions_confirmed",
        "needs_targeted_rework",
        "blocked_missing_primary_material",
        "unverifiable_best_effort",
    }
    if decision not in allowed:
        return False, f"unknown_decision:{decision}", decision
    return True, "valid_result_json", decision


def codex_command(prompt_path: Path, last_message_path: Path) -> list[str]:
    return [
        "codex",
        "exec",
        "-C",
        str(ROOT),
        "--skip-git-repo-check",
        "--add-dir",
        str(ROOT),
        "--add-dir",
        str(MERGED_CORPUS_ROOT),
        "-m",
        "gpt-5.5",
        "-c",
        'model_reasoning_effort="xhigh"',
        "-c",
        'approval_policy="never"',
        "-o",
        str(last_message_path),
        "-",
    ]


def run_one(row: dict[str, str], timeout_seconds: int, force: bool) -> dict[str, Any]:
    packet_dir = abs_path(row["packet_dir"])
    prompt_path = abs_path(row["prompt_path"])
    result_path = abs_path(row["result_path"])
    last_message_path = packet_dir / "CODEX_LAST_MESSAGE.md"
    stdout_path = packet_dir / "codex_exec.stdout.log"
    stderr_path = packet_dir / "codex_exec.stderr.log"
    status_path = packet_dir / "runner_status.json"

    started_at = now_utc()
    start = time.monotonic()
    if result_path.exists() and not force:
        ok, validation, decision = validate_result(result_path)
        status = {
            **row,
            "runner_state": "skipped_existing_result" if ok else "existing_result_invalid",
            "runner_validation": validation,
            "decision": decision,
            "started_at": started_at,
            "finished_at": now_utc(),
            "elapsed_seconds": 0,
            "returncode": "",
            "stdout_log": rel_path(stdout_path),
            "stderr_log": rel_path(stderr_path),
        }
        write_json(status_path, status)
        return status

    cmd = codex_command(prompt_path, last_message_path)
    try:
        with stdout_path.open("w", encoding="utf-8") as stdout_fh, stderr_path.open("w", encoding="utf-8") as stderr_fh:
            proc = subprocess.run(
                cmd,
                cwd=ROOT,
                input=prompt_path.read_text(encoding="utf-8"),
                text=True,
                stdout=stdout_fh,
                stderr=stderr_fh,
                timeout=timeout_seconds,
                check=False,
            )
        returncode: int | str = proc.returncode
        runner_state = "codex_finished"
    except subprocess.TimeoutExpired:
        returncode = "timeout"
        runner_state = "timeout"
    except Exception as exc:  # noqa: BLE001 - record the runner failure.
        returncode = type(exc).__name__
        runner_state = "runner_exception"
        stderr_path.write_text(str(exc) + "\n", encoding="utf-8")

    ok, validation, decision = validate_result(result_path)
    elapsed = round(time.monotonic() - start, 3)
    if runner_state == "codex_finished" and not ok:
        runner_state = "codex_finished_no_valid_result"
    elif runner_state == "codex_finished" and ok:
        runner_state = "completed_valid_result"

    status = {
        **row,
        "runner_state": runner_state,
        "runner_validation": validation,
        "decision": decision,
        "started_at": started_at,
        "finished_at": now_utc(),
        "elapsed_seconds": elapsed,
        "returncode": returncode,
        "stdout_log": rel_path(stdout_path),
        "stderr_log": rel_path(stderr_path),
        "last_message_path": rel_path(last_message_path),
    }
    write_json(status_path, status)
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-index", type=Path, default=DEFAULT_PACKET_INDEX)
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.packet_index)
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        raise RuntimeError("no packet rows to run")
    if args.parallel < 1:
        raise RuntimeError("--parallel must be >= 1")

    outdir = args.packet_index.parent / "runner"
    outdir.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    status_rows: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {pool.submit(run_one, row, args.timeout_seconds, args.force): row for row in rows}
        for future in as_completed(futures):
            status = future.result()
            status_rows.append(status)
            print(json.dumps({
                "pilot_sample_id": status.get("pilot_sample_id"),
                "paper_id": status.get("paper_id"),
                "runner_state": status.get("runner_state"),
                "decision": status.get("decision"),
                "validation": status.get("runner_validation"),
            }, ensure_ascii=False, sort_keys=True), flush=True)

    fields = [
        "pilot_sample_id",
        "paper_id",
        "database",
        "source_id",
        "audit_record_id",
        "status",
        "packet_dir",
        "result_path",
        "runner_state",
        "runner_validation",
        "decision",
        "started_at",
        "finished_at",
        "elapsed_seconds",
        "returncode",
        "stdout_log",
        "stderr_log",
        "last_message_path",
    ]
    status_rows.sort(key=lambda row: row.get("pilot_sample_id", ""))
    csv_path = outdir / f"true_source_review_status_{run_id}.csv"
    json_path = outdir / f"true_source_review_summary_{run_id}.json"
    write_csv(csv_path, status_rows, fields)
    latest_csv = outdir / "true_source_review_status_latest.csv"
    latest_json = outdir / "true_source_review_summary_latest.json"
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")

    summary = {
        "generated_at": now_utc(),
        "packet_index": rel_path(args.packet_index),
        "parallel": args.parallel,
        "timeout_seconds": args.timeout_seconds,
        "selected_count": len(rows),
        "runner_state_counts": {},
        "decision_counts": {},
        "validation_counts": {},
        "outputs": {
            "status_csv": rel_path(csv_path),
            "latest_status_csv": rel_path(latest_csv),
            "summary_json": rel_path(json_path),
            "latest_summary_json": rel_path(latest_json),
        },
    }
    for key, target in [
        ("runner_state", "runner_state_counts"),
        ("decision", "decision_counts"),
        ("runner_validation", "validation_counts"),
    ]:
        counts: dict[str, int] = {}
        for row in status_rows:
            value = str(row.get(key, ""))
            counts[value] = counts.get(value, 0) + 1
        summary[target] = counts
    write_json(json_path, summary)
    write_json(latest_json, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
