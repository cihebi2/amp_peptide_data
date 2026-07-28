#!/usr/bin/env python3
"""Safely replace the serial supervisor after its current campaign boundary."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot"
REPORT_DIR = PILOT / "reports/remaining_200_campaign/supervisor"
JOURNAL = REPORT_DIR / "supervisor_journal.jsonl"
PARALLEL = ROOT / "pipeline_v2/deepmine/supervise_remaining_200_parallel_campaign.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def attempt_finished(paper_id: str, attempt: int) -> bool:
    if not JOURNAL.exists():
        return False
    for line in reversed(
        JOURNAL.read_text(encoding="utf-8", errors="replace").splitlines()
    ):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            row.get("event") == "paper_attempt_finished"
            and row.get("paper_id") == paper_id
            and int(row.get("attempt") or 0) == attempt
        ):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial-supervisor-pid", type=int, required=True)
    parser.add_argument("--active-campaign-pid", type=int, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--poll-seconds", type=int, default=2)
    parser.add_argument("--boundary-timeout", type=int, default=21600)
    parser.add_argument("--journal-grace-seconds", type=int, default=90)
    parser.add_argument("--max-parallel-papers", type=int, default=4)
    parser.add_argument("--max-rework-parallel", type=int, default=1)
    args = parser.parse_args()

    started = time.monotonic()
    while process_exists(args.active_campaign_pid):
        if time.monotonic() - started > args.boundary_timeout:
            raise SystemExit("timed out waiting for active campaign boundary")
        time.sleep(args.poll_seconds)

    grace_started = time.monotonic()
    while not attempt_finished(args.paper_id, args.attempt):
        if time.monotonic() - grace_started > args.journal_grace_seconds:
            raise SystemExit("campaign ended but serial supervisor did not journal finish")
        time.sleep(1)

    if process_exists(args.serial_supervisor_pid):
        os.kill(args.serial_supervisor_pid, signal.SIGTERM)
        stop_started = time.monotonic()
        while process_exists(args.serial_supervisor_pid):
            if time.monotonic() - stop_started > 30:
                os.kill(args.serial_supervisor_pid, signal.SIGKILL)
                break
            time.sleep(0.5)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stdout_path = REPORT_DIR / "parallel_supervisor.stdout.log"
    stderr_path = REPORT_DIR / "parallel_supervisor.stderr.log"
    command = [
        sys.executable,
        str(PARALLEL),
        "--max-parallel-papers",
        str(args.max_parallel_papers),
        "--max-rework-parallel",
        str(args.max_rework_parallel),
        "--max-attempts-per-paper",
        "12",
        "--max-rework-rounds",
        "3",
        "--worker-timeout",
        "5400",
        "--audit-timeout",
        "5400",
        "--sleep-seconds",
        "15",
    ]
    with stdout_path.open("a", encoding="utf-8") as stdout, stderr_path.open(
        "a", encoding="utf-8"
    ) as stderr:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
    result = {
        "switched_at": utc_now(),
        "old_serial_supervisor_pid": args.serial_supervisor_pid,
        "completed_boundary": {
            "paper_id": args.paper_id,
            "attempt": args.attempt,
        },
        "parallel_supervisor_pid": process.pid,
        "max_parallel_papers": args.max_parallel_papers,
        "max_rework_parallel": args.max_rework_parallel,
        "stdout_path": str(stdout_path.relative_to(ROOT)),
        "stderr_path": str(stderr_path.relative_to(ROOT)),
    }
    result_path = REPORT_DIR / "parallel_switch_result.json"
    result_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (REPORT_DIR / "parallel_supervisor.pid").write_text(
        f"{process.pid}\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
