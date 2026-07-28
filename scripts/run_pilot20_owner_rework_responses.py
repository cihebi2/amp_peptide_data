#!/usr/bin/env python3
"""Run Codex owner-worker responses for pilot20 rework dispatch packets."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DISPATCH_ROOT = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "pilot20" / "source_review_packets" / "owner_rework_dispatch"
DEFAULT_INDEX = DISPATCH_ROOT / "dispatch_index_latest.csv"
MERGED_CORPUS_ROOT = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus")


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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


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


def validate_owner_response(path: Path) -> tuple[bool, str, str]:
    if not path.exists():
        return False, "missing_owner_response", ""
    try:
        data = load_json(path)
    except Exception as exc:  # noqa: BLE001
        return False, f"unreadable_owner_response:{type(exc).__name__}", ""
    required = ["ticket_id", "paper_id", "owner_worker", "action_taken", "source_inputs_checked", "worker6_followup_required"]
    missing = [key for key in required if key not in data]
    if missing:
        return False, "missing_required_keys:" + ",".join(missing), str(data.get("action_taken", ""))
    allowed = {"repair_ready", "blocked_missing_material", "needs_upstream_material", "defer_to_worker6"}
    action = str(data.get("action_taken", ""))
    if action not in allowed:
        return False, f"unknown_action:{action}", action
    return True, "valid_owner_response", action


def run_one(row: dict[str, str], timeout_seconds: int, force: bool) -> dict[str, Any]:
    dispatch_packet = abs_path(row["dispatch_packet"])
    prompt_path = abs_path(row["prompt_path"])
    response_path = abs_path(row["expected_response_path"])
    dispatch_dir = dispatch_packet.parent
    stdout_path = dispatch_dir / "codex_owner.stdout.log"
    stderr_path = dispatch_dir / "codex_owner.stderr.log"
    last_message_path = dispatch_dir / "CODEX_OWNER_LAST_MESSAGE.md"
    status_path = dispatch_dir / "owner_runner_status.json"

    started_at = now_utc()
    if response_path.exists() and not force:
        ok, validation, action = validate_owner_response(response_path)
        status = {
            **row,
            "runner_state": "skipped_existing_response" if ok else "existing_response_invalid",
            "runner_validation": validation,
            "action_taken": action,
            "started_at": started_at,
            "finished_at": now_utc(),
            "elapsed_seconds": 0,
            "returncode": "",
            "stdout_log": rel(stdout_path),
            "stderr_log": rel(stderr_path),
            "last_message_path": rel(last_message_path),
        }
        write_json(status_path, status)
        return status

    start = time.monotonic()
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
    except Exception as exc:  # noqa: BLE001
        returncode = type(exc).__name__
        runner_state = "runner_exception"
        stderr_path.write_text(str(exc) + "\n", encoding="utf-8")

    ok, validation, action = validate_owner_response(response_path)
    if runner_state == "codex_finished" and ok:
        runner_state = "completed_valid_response"
    elif runner_state == "codex_finished":
        runner_state = "codex_finished_no_valid_response"

    status = {
        **row,
        "runner_state": runner_state,
        "runner_validation": validation,
        "action_taken": action,
        "started_at": started_at,
        "finished_at": now_utc(),
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "returncode": returncode,
        "stdout_log": rel(stdout_path),
        "stderr_log": rel(stderr_path),
        "last_message_path": rel(last_message_path),
    }
    write_json(status_path, status)
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dispatch-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--parallel", type=int, default=3)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.dispatch_index)
    if args.limit:
        rows = rows[: args.limit]
    if args.parallel < 1:
        raise RuntimeError("--parallel must be >= 1")
    if not rows:
        raise RuntimeError("no dispatch rows")

    run_id = stamp()
    outdir = args.dispatch_index.parent / "owner_runner"
    outdir.mkdir(parents=True, exist_ok=True)
    statuses: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {pool.submit(run_one, row, args.timeout_seconds, args.force): row for row in rows}
        for future in as_completed(futures):
            status = future.result()
            statuses.append(status)
            print(json.dumps({
                "dispatch_id": status.get("dispatch_id"),
                "owner_worker": status.get("owner_worker"),
                "runner_state": status.get("runner_state"),
                "action_taken": status.get("action_taken"),
                "validation": status.get("runner_validation"),
            }, ensure_ascii=False, sort_keys=True), flush=True)

    statuses.sort(key=lambda row: row.get("dispatch_id", ""))
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
        "runner_state",
        "runner_validation",
        "started_at",
        "finished_at",
        "elapsed_seconds",
        "returncode",
        "stdout_log",
        "stderr_log",
        "last_message_path",
        "expected_response_path",
    ]
    csv_path = outdir / f"owner_runner_status_{run_id}.csv"
    latest_csv = outdir / "owner_runner_status_latest.csv"
    write_csv(csv_path, statuses, fields)
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")

    summary = {
        "generated_at": now_utc(),
        "completion_claim": "pilot20_owner_worker_responses_completed_not_final_artifact_repair",
        "dispatch_index": rel(args.dispatch_index),
        "selected_count": len(rows),
        "parallel": args.parallel,
        "timeout_seconds": args.timeout_seconds,
        "runner_state_counts": dict(Counter(row["runner_state"] for row in statuses)),
        "validation_counts": dict(Counter(row["runner_validation"] for row in statuses)),
        "action_counts": dict(Counter(row["action_taken"] for row in statuses)),
        "owner_counts": dict(Counter(row["owner_worker"] for row in statuses)),
        "outputs": {
            "status_csv": rel(csv_path),
            "latest_status_csv": rel(latest_csv),
            "summary_json": rel(outdir / f"owner_runner_summary_{run_id}.json"),
            "latest_summary_json": rel(outdir / "owner_runner_summary_latest.json"),
        },
    }
    write_json(outdir / f"owner_runner_summary_{run_id}.json", summary)
    write_json(outdir / "owner_runner_summary_latest.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
