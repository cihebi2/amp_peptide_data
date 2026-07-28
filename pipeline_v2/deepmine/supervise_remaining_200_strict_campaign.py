#!/usr/bin/env python3
"""Durably supervise the frozen 200-paper strict review campaign.

The supervisor invokes the fail-closed single-paper campaign executor one
paper at a time, rotates across every nonterminal paper in a sweep, persists
attempt/result evidence, and publishes an atomic machine/human status
heartbeat. It never promotes papers itself; the strict ledger remains the
only terminal-state authority.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot"
STATE = (
    PILOT
    / "manifests/remaining_200_strict_review_state_20260726.json"
)
CONTROLLER = ROOT / "pipeline_v2/deepmine/remaining_200_strict_controller.py"
CAMPAIGN = ROOT / "pipeline_v2/deepmine/run_remaining_200_strict_campaign.py"
REPORT_DIR = PILOT / "reports/remaining_200_campaign/supervisor"
STATUS_JSON = REPORT_DIR / "supervisor_status_latest.json"
STATUS_MD = REPORT_DIR / "REMAINING_200_CAMPAIGN_STATUS.md"
JOURNAL = REPORT_DIR / "supervisor_journal.jsonl"
LOCK = REPORT_DIR / ".supervisor.lock"

STATUS_PRIORITY = {
    "needs_targeted_semantic_rework": 0,
    "awaiting_worker6_repair_or_mechanical_acceptance": 1,
    "six_worker_review_in_progress": 2,
    "awaiting_leader_field_semantic_audit": 3,
    "awaiting_independent_verifier": 4,
    "ready_for_six_worker_review": 5,
}
TERMINAL_STATUS = "terminal_scientific_review_complete"
IMMEDIATE_RETRY_STATUSES = {
    "needs_targeted_semantic_rework",
    "awaiting_worker6_repair_or_mechanical_acceptance",
    "six_worker_review_in_progress",
    "awaiting_leader_field_semantic_audit",
    "awaiting_independent_verifier",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_text(
        path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    )


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_state() -> dict[str, Any]:
    with STATE.open(encoding="utf-8") as handle:
        return json.load(handle)


def refresh_ledger(log_path: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(CONTROLLER), "status"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=900,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        completed.stdout
        + ("\n--- STDERR ---\n" + completed.stderr if completed.stderr else ""),
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"strict ledger refresh failed rc={completed.returncode}: "
            f"{completed.stderr[-2000:]}"
        )
    return json.loads(completed.stdout)


def ordered_nonterminal_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in state.get("papers", [])
        if row.get("workflow_status") != TERMINAL_STATUS
    ]
    return sorted(
        rows,
        key=lambda row: (
            STATUS_PRIORITY.get(str(row.get("workflow_status")), 99),
            int(row.get("queue_index") or 10**9),
            str(row.get("paper_id") or ""),
        ),
    )


def should_immediately_retry(
    row: dict[str, Any],
    *,
    consecutive_attempt: int,
    total_attempts: int,
    max_consecutive_attempts: int,
    max_attempts_per_paper: int,
) -> bool:
    return (
        str(row.get("workflow_status")) in IMMEDIATE_RETRY_STATUSES
        and consecutive_attempt < max_consecutive_attempts
        and total_attempts < max_attempts_per_paper
    )


def attempt_counts() -> Counter[str]:
    counts: Counter[str] = Counter()
    if not JOURNAL.exists():
        return counts
    for line in JOURNAL.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("event") == "paper_attempt_finished" and row.get("paper_id"):
            counts[str(row["paper_id"])] += 1
    return counts


def status_payload(
    *,
    state: dict[str, Any],
    active_paper: str | None,
    active_attempt: int | None,
    sweep_number: int,
    attempts: Counter[str],
    latest_result: dict[str, Any] | None,
    supervisor_started_at: str,
) -> dict[str, Any]:
    rows = list(state.get("papers", []))
    status_counts = Counter(str(row.get("workflow_status")) for row in rows)
    terminal = status_counts.get(TERMINAL_STATUS, 0)
    return {
        "generated_at": utc_now(),
        "supervisor_pid": os.getpid(),
        "supervisor_started_at": supervisor_started_at,
        "frozen_denominator": len(rows),
        "terminal_scientific_review_complete": terminal,
        "remaining_nonterminal": len(rows) - terminal,
        "strict_material_ready": sum(
            1 for row in rows if (row.get("material") or {}).get("strict_material_ready")
        ),
        "open_ticket_count": sum(
            int((row.get("tickets") or {}).get("open_ticket_count") or 0)
            for row in rows
        ),
        "workflow_status_counts": dict(sorted(status_counts.items())),
        "active_paper": active_paper,
        "active_attempt": active_attempt,
        "sweep_number": sweep_number,
        "attempt_counts": dict(sorted(attempts.items())),
        "latest_result": latest_result,
        "terminal_contract": (
            "Per paper: six unique sequential exact codex exec gpt-5.5/xhigh "
            "workers, fresh worker-6, current mechanical acceptance, zero open "
            "tickets, structured leader PASS, independent verifier PASS, "
            "recursive authority=false, and fallback release exclusion."
        ),
        "state_path": str(STATE.relative_to(ROOT)),
        "journal_path": str(JOURNAL.relative_to(ROOT)),
    }


def render_status_markdown(payload: dict[str, Any]) -> str:
    latest = payload.get("latest_result") or {}
    latest_text = (
        f"`{latest.get('paper_id')}` / `{latest.get('after_status')}` / "
        f"campaign rc `{latest.get('campaign_returncode')}`"
        if latest
        else "none yet"
    )
    workflow = "\n".join(
        f"- `{key}`: {value}"
        for key, value in payload["workflow_status_counts"].items()
    )
    active_runs = payload.get("active_runs")
    if isinstance(active_runs, list) and active_runs:
        active_text = "\n".join(
            f"- `{row.get('paper_id')}` / attempt `{row.get('attempt')}` / "
            f"started `{row.get('started_at')}`"
            for row in active_runs
            if isinstance(row, dict)
        )
    else:
        active_text = (
            f"- `{payload['active_paper'] or 'none'}` / "
            f"attempt `{payload['active_attempt'] or 'none'}`"
        )
    return f"""# Remaining 200 Strict Review Campaign Status

Generated: {payload['generated_at']}  
Supervisor PID: `{payload['supervisor_pid']}`  
Supervisor started: {payload['supervisor_started_at']}

## Current denominator

- Frozen queue: **{payload['frozen_denominator']}**
- Terminal scientific review complete: **{payload['terminal_scientific_review_complete']}**
- Remaining nonterminal: **{payload['remaining_nonterminal']}**
- Strict materials ready: **{payload['strict_material_ready']}**
- Live open tickets: **{payload['open_ticket_count']}**

## Active work

- Sweep: **{payload['sweep_number']}**
- Parallel capacity: **{payload.get('max_parallel_papers', 1)}**
{active_text}
- Latest result: {latest_text}

## Workflow states

{workflow}

## Quality boundary

{payload['terminal_contract']}

This file is a generated heartbeat. Terminal promotion is controlled only by
the frozen strict ledger at `{payload['state_path']}`. Campaign attempts are
append-only in `{payload['journal_path']}`.
"""


def publish_status(payload: dict[str, Any]) -> None:
    atomic_write_json(STATUS_JSON, payload)
    atomic_write_text(STATUS_MD, render_status_markdown(payload))


def run_campaign(
    *,
    paper_id: str,
    attempt: int,
    sweep_number: int,
    args: argparse.Namespace,
) -> tuple[int, Path, Path]:
    stamp = run_stamp()
    stdout_path = REPORT_DIR / (
        f"{stamp}.sweep-{sweep_number:04d}.{paper_id}."
        f"attempt-{attempt:03d}.stdout.log"
    )
    stderr_path = stdout_path.with_name(
        stdout_path.name.replace(".stdout.log", ".stderr.log")
    )
    command = [
        sys.executable,
        str(CAMPAIGN),
        "--paper-id",
        paper_id,
        "--max-papers",
        "1",
        "--max-rework-rounds",
        str(args.max_rework_rounds),
        "--worker-timeout",
        str(args.worker_timeout),
        "--audit-timeout",
        str(args.audit_timeout),
    ]
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=stdout,
            stderr=stderr,
            check=False,
        )
    return completed.returncode, stdout_path, stderr_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-sweeps", type=int, default=100)
    parser.add_argument("--max-attempts-per-paper", type=int, default=12)
    parser.add_argument("--max-consecutive-attempts", type=int, default=3)
    parser.add_argument("--max-rework-rounds", type=int, default=3)
    parser.add_argument("--worker-timeout", type=int, default=5400)
    parser.add_argument("--audit-timeout", type=int, default=5400)
    parser.add_argument("--sleep-seconds", type=int, default=15)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    for name in (
        "max_sweeps",
        "max_attempts_per_paper",
        "max_consecutive_attempts",
        "max_rework_rounds",
        "worker_timeout",
        "audit_timeout",
    ):
        if getattr(args, name) < 1:
            raise SystemExit(f"--{name.replace('_', '-')} must be positive")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lock_handle = LOCK.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        raise SystemExit("another strict campaign supervisor owns the lock") from error
    supervisor_started_at = utc_now()
    lock_handle.seek(0)
    lock_handle.truncate()
    lock_handle.write(
        json.dumps(
            {"pid": os.getpid(), "acquired_at": supervisor_started_at},
            ensure_ascii=False,
        )
        + "\n"
    )
    lock_handle.flush()

    attempts = attempt_counts()
    latest_result: dict[str, Any] | None = None
    if args.dry_run:
        refresh_ledger(REPORT_DIR / f"{run_stamp()}.dry-run-ledger.log")
        state = read_state()
        rows = ordered_nonterminal_rows(state)
        payload = status_payload(
            state=state,
            active_paper=None,
            active_attempt=None,
            sweep_number=0,
            attempts=attempts,
            latest_result=None,
            supervisor_started_at=supervisor_started_at,
        )
        publish_status(payload)
        print(
            json.dumps(
                {
                    "selected_count": len(rows),
                    "first_paper": rows[0]["paper_id"] if rows else None,
                    "status": payload,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    append_jsonl(
        JOURNAL,
        {
            "event": "supervisor_started",
            "created_at": supervisor_started_at,
            "pid": os.getpid(),
            "arguments": vars(args),
        },
    )

    for sweep_number in range(1, args.max_sweeps + 1):
        refresh_ledger(REPORT_DIR / f"{run_stamp()}.sweep-{sweep_number:04d}-ledger.log")
        state = read_state()
        rows = ordered_nonterminal_rows(state)
        if not rows:
            payload = status_payload(
                state=state,
                active_paper=None,
                active_attempt=None,
                sweep_number=sweep_number,
                attempts=attempts,
                latest_result=latest_result,
                supervisor_started_at=supervisor_started_at,
            )
            publish_status(payload)
            append_jsonl(
                JOURNAL,
                {
                    "event": "supervisor_terminal_complete",
                    "created_at": utc_now(),
                    "sweep_number": sweep_number,
                    "terminal_count": payload[
                        "terminal_scientific_review_complete"
                    ],
                },
            )
            return 0

        attempted_this_sweep = 0
        pending: list[tuple[dict[str, Any], int]] = [
            (row, 1) for row in rows
        ]
        while pending:
            initial_row, consecutive_attempt = pending.pop(0)
            paper_id = str(initial_row["paper_id"])
            if attempts[paper_id] >= args.max_attempts_per_paper:
                continue
            refresh_ledger(
                REPORT_DIR
                / f"{run_stamp()}.{paper_id}.pre-attempt-ledger.log"
            )
            current = next(
                (
                    row
                    for row in read_state().get("papers", [])
                    if row.get("paper_id") == paper_id
                ),
                None,
            )
            if current is None or current.get("workflow_status") == TERMINAL_STATUS:
                continue

            attempted_this_sweep += 1
            attempt = attempts[paper_id] + 1
            before_status = str(current.get("workflow_status"))
            payload = status_payload(
                state=read_state(),
                active_paper=paper_id,
                active_attempt=attempt,
                sweep_number=sweep_number,
                attempts=attempts,
                latest_result=latest_result,
                supervisor_started_at=supervisor_started_at,
            )
            publish_status(payload)
            append_jsonl(
                JOURNAL,
                {
                    "event": "paper_attempt_started",
                    "created_at": utc_now(),
                    "paper_id": paper_id,
                    "attempt": attempt,
                    "sweep_number": sweep_number,
                    "before_status": before_status,
                },
            )

            started_at = utc_now()
            returncode, stdout_path, stderr_path = run_campaign(
                paper_id=paper_id,
                attempt=attempt,
                sweep_number=sweep_number,
                args=args,
            )
            finished_at = utc_now()
            attempts[paper_id] += 1
            refresh_ledger(
                REPORT_DIR
                / f"{run_stamp()}.{paper_id}.post-attempt-ledger.log"
            )
            after_state = read_state()
            after_row = next(
                row
                for row in after_state.get("papers", [])
                if row.get("paper_id") == paper_id
            )
            latest_result = {
                "paper_id": paper_id,
                "attempt": attempt,
                "sweep_number": sweep_number,
                "started_at": started_at,
                "finished_at": finished_at,
                "before_status": before_status,
                "after_status": str(after_row.get("workflow_status")),
                "campaign_returncode": returncode,
                "stdout_path": str(stdout_path.relative_to(ROOT)),
                "stderr_path": str(stderr_path.relative_to(ROOT)),
            }
            append_jsonl(
                JOURNAL,
                {"event": "paper_attempt_finished", **latest_result},
            )
            publish_status(
                status_payload(
                    state=after_state,
                    active_paper=None,
                    active_attempt=None,
                    sweep_number=sweep_number,
                    attempts=attempts,
                    latest_result=latest_result,
                    supervisor_started_at=supervisor_started_at,
                )
            )
            if should_immediately_retry(
                after_row,
                consecutive_attempt=consecutive_attempt,
                total_attempts=attempts[paper_id],
                max_consecutive_attempts=args.max_consecutive_attempts,
                max_attempts_per_paper=args.max_attempts_per_paper,
            ):
                pending.insert(0, (after_row, consecutive_attempt + 1))
                append_jsonl(
                    JOURNAL,
                    {
                        "event": "paper_immediate_retry_queued",
                        "created_at": utc_now(),
                        "paper_id": paper_id,
                        "next_consecutive_attempt": consecutive_attempt + 1,
                        "total_attempts": attempts[paper_id],
                        "workflow_status": after_row.get("workflow_status"),
                    },
                )
            if args.sleep_seconds:
                time.sleep(args.sleep_seconds)

        if attempted_this_sweep == 0:
            state = read_state()
            payload = status_payload(
                state=state,
                active_paper=None,
                active_attempt=None,
                sweep_number=sweep_number,
                attempts=attempts,
                latest_result=latest_result,
                supervisor_started_at=supervisor_started_at,
            )
            publish_status(payload)
            append_jsonl(
                JOURNAL,
                {
                    "event": "supervisor_attempt_budget_exhausted",
                    "created_at": utc_now(),
                    "sweep_number": sweep_number,
                    "remaining_nonterminal": payload["remaining_nonterminal"],
                },
            )
            return 2

    append_jsonl(
        JOURNAL,
        {
            "event": "supervisor_max_sweeps_exhausted",
            "created_at": utc_now(),
            "max_sweeps": args.max_sweeps,
        },
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
