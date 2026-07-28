#!/usr/bin/env python3
"""Reload the parallel strict-review scheduler without interrupting papers.

The old scheduler is stopped before it can launch replacement papers. Its
already-running campaign children continue to their natural process boundary.
The scheduler is resumed only long enough to reap those children and append
their normal ``paper_attempt_finished`` journal rows, then replaced.
"""

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
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot"
REPORT_DIR = PILOT / "reports/remaining_200_campaign/supervisor"
STATUS = REPORT_DIR / "supervisor_status_latest.json"
JOURNAL = REPORT_DIR / "supervisor_journal.jsonl"
SUPERVISOR = (
    ROOT / "pipeline_v2/deepmine/"
    "supervise_remaining_200_parallel_campaign.py"
)
CAMPAIGN_NAME = "run_remaining_200_strict_campaign.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def parse_proc_stat(text: str) -> tuple[str, int]:
    """Return Linux process state and raw wait status from ``/proc/PID/stat``."""
    close = text.rfind(")")
    if close < 0:
        raise ValueError("malformed /proc stat: missing command terminator")
    fields = text[close + 1 :].strip().split()
    if len(fields) < 50:
        raise ValueError("malformed /proc stat: missing exit_code field")
    return fields[0], int(fields[49])


def proc_state(pid: int) -> tuple[str, int] | None:
    try:
        return parse_proc_stat(
            Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        )
    except FileNotFoundError:
        return None


def process_exists(pid: int) -> bool:
    return proc_state(pid) is not None


def read_cmdline(pid: int) -> list[str]:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except FileNotFoundError:
        return []
    return [
        item.decode("utf-8", errors="replace")
        for item in raw.split(b"\0")
        if item
    ]


def is_campaign_command(command: list[str]) -> bool:
    return any(Path(value).name == CAMPAIGN_NAME for value in command)


def paper_id_from_command(command: list[str]) -> str | None:
    try:
        index = command.index("--paper-id")
    except ValueError:
        return None
    if index + 1 >= len(command):
        return None
    return command[index + 1]


def direct_children(pid: int) -> set[int]:
    children: set[int] = set()
    for child_file in Path(f"/proc/{pid}/task").glob("*/children"):
        try:
            values = child_file.read_text(encoding="utf-8").split()
        except FileNotFoundError:
            continue
        children.update(int(value) for value in values)
    return children


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(
        encoding="utf-8", errors="replace"
    ).splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def attempt_set_finished(
    expected: set[tuple[str, int]], rows: list[dict[str, Any]]
) -> bool:
    finished: set[tuple[str, int]] = set()
    for row in rows:
        if row.get("event") != "paper_attempt_finished":
            continue
        try:
            key = (str(row.get("paper_id") or ""), int(row.get("attempt")))
        except (TypeError, ValueError):
            continue
        finished.add(key)
    return expected.issubset(finished)


def has_attempt_start(
    rows: list[dict[str, Any]], *, checkpoint: int
) -> bool:
    return any(
        row.get("event") == "paper_attempt_started"
        for row in rows[checkpoint:]
    )


def complete_campaign_child_map(
    active_papers: set[str],
    mapped_children: dict[str, int],
    anonymous_zombies: list[int],
) -> dict[str, int]:
    """Assign only an exact set of drained anonymous children to boundaries."""
    missing = sorted(active_papers - set(mapped_children))
    if len(missing) != len(anonymous_zombies):
        raise RuntimeError(
            "anonymous zombie count does not match missing campaign "
            f"boundaries: missing={missing}, "
            f"zombies={sorted(anonymous_zombies)}"
        )
    completed = dict(mapped_children)
    for paper_id, child_pid in zip(
        missing, sorted(anonymous_zombies), strict=True
    ):
        completed[paper_id] = child_pid
    return completed


def capture_boundaries(
    old_pid: int,
) -> tuple[list[dict[str, Any]], set[tuple[str, int]]]:
    status = read_json(STATUS)
    if int(status.get("supervisor_pid") or 0) != old_pid:
        raise RuntimeError("status PID does not match requested supervisor")
    active = status.get("active_runs")
    if not isinstance(active, list) or not active:
        raise RuntimeError("supervisor has no active paper boundary to drain")
    active_by_paper = {
        str(row.get("paper_id")): row
        for row in active
        if isinstance(row, dict) and row.get("paper_id")
    }
    campaign_children: dict[str, int] = {}
    anonymous_zombies: list[int] = []
    for child_pid in direct_children(old_pid):
        command = read_cmdline(child_pid)
        if not is_campaign_command(command):
            state = proc_state(child_pid)
            if state is not None and state[0] == "Z" and not command:
                anonymous_zombies.append(child_pid)
            continue
        paper_id = paper_id_from_command(command)
        if not paper_id or paper_id in campaign_children:
            raise RuntimeError("campaign child paper mapping is not unique")
        campaign_children[paper_id] = child_pid
    campaign_children = complete_campaign_child_map(
        set(active_by_paper), campaign_children, anonymous_zombies
    )
    if set(campaign_children) != set(active_by_paper):
        raise RuntimeError(
            "live campaign children do not match active status: "
            f"children={sorted(campaign_children)}, "
            f"status={sorted(active_by_paper)}"
        )
    boundaries: list[dict[str, Any]] = []
    expected: set[tuple[str, int]] = set()
    for paper_id, row in active_by_paper.items():
        attempt = int(row.get("attempt") or 0)
        if attempt < 1:
            raise RuntimeError(f"invalid attempt for {paper_id}")
        boundaries.append(
            {
                "paper_id": paper_id,
                "attempt": attempt,
                "campaign_pid": campaign_children[paper_id],
                "started_at": row.get("started_at"),
            }
        )
        expected.add((paper_id, attempt))
    return sorted(boundaries, key=lambda row: row["paper_id"]), expected


def wait_for_campaign_drain(
    boundaries: list[dict[str, Any]],
    *,
    timeout: float,
    poll_seconds: float,
    report: dict[str, Any],
    report_path: Path,
) -> None:
    started = time.monotonic()
    while True:
        states: dict[str, str] = {}
        drained = True
        for row in boundaries:
            state = proc_state(int(row["campaign_pid"]))
            label = "gone" if state is None else state[0]
            states[str(row["paper_id"])] = label
            if label not in {"Z", "gone"}:
                drained = False
        report["campaign_process_states"] = states
        report["updated_at"] = utc_now()
        atomic_write_json(report_path, report)
        if drained:
            return
        if time.monotonic() - started > timeout:
            raise TimeoutError("timed out waiting for active campaigns to drain")
        time.sleep(poll_seconds)


def wait_for_normal_journal(
    old_pid: int,
    expected: set[tuple[str, int]],
    *,
    timeout: float,
    poll_seconds: float,
) -> None:
    started = time.monotonic()
    while not attempt_set_finished(expected, read_jsonl(JOURNAL)):
        if not process_exists(old_pid):
            raise RuntimeError(
                "old supervisor exited before journaling drained attempts"
            )
        if time.monotonic() - started > timeout:
            raise TimeoutError(
                "timed out waiting for normal attempt-finished journal rows"
            )
        time.sleep(poll_seconds)


def wait_for_children_to_finish(
    old_pid: int, *, timeout: float, poll_seconds: float
) -> None:
    """Wait for any post-journal ledger child to finish before replacement."""
    started = time.monotonic()
    while True:
        live = []
        for child_pid in direct_children(old_pid):
            state = proc_state(child_pid)
            if state is not None and state[0] != "Z":
                live.append((child_pid, read_cmdline(child_pid)))
        if not live:
            return
        if any(is_campaign_command(command) for _, command in live):
            raise RuntimeError(
                "old supervisor launched a new campaign during handoff"
            )
        if time.monotonic() - started > timeout:
            raise TimeoutError(
                "timed out waiting for post-journal helper process"
            )
        time.sleep(poll_seconds)


def stop_process(pid: int, timeout: float = 30) -> None:
    if not process_exists(pid):
        return
    os.kill(pid, signal.SIGKILL)
    started = time.monotonic()
    while True:
        state = proc_state(pid)
        if state is None or state[0] == "Z":
            return
        if time.monotonic() - started > timeout:
            raise TimeoutError(f"process did not stop: {pid}")
        time.sleep(0.1)


def launch_supervisor(args: argparse.Namespace) -> tuple[int, Path, Path]:
    stdout_path = REPORT_DIR / "parallel_supervisor.stdout.log"
    stderr_path = REPORT_DIR / "parallel_supervisor.stderr.log"
    command = [
        sys.executable,
        str(SUPERVISOR),
        "--max-parallel-papers",
        str(args.max_parallel_papers),
        "--max-rework-parallel",
        str(args.max_rework_parallel),
        "--max-attempts-per-paper",
        str(args.max_attempts_per_paper),
        "--max-rework-rounds",
        str(args.max_rework_rounds),
        "--worker-timeout",
        str(args.worker_timeout),
        "--audit-timeout",
        str(args.audit_timeout),
        "--sleep-seconds",
        str(args.sleep_seconds),
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
    return process.pid, stdout_path, stderr_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-supervisor-pid", type=int, required=True)
    parser.add_argument(
        "--pause-only",
        action="store_true",
        help=(
            "Drain and journal the active paper boundary, then stop without "
            "launching a replacement supervisor."
        ),
    )
    parser.add_argument("--drain-timeout", type=int, default=21600)
    parser.add_argument("--journal-timeout", type=int, default=1800)
    parser.add_argument("--poll-seconds", type=float, default=0.2)
    parser.add_argument("--max-parallel-papers", type=int, default=4)
    parser.add_argument("--max-rework-parallel", type=int, default=1)
    parser.add_argument("--max-attempts-per-paper", type=int, default=12)
    parser.add_argument("--max-rework-rounds", type=int, default=3)
    parser.add_argument("--worker-timeout", type=int, default=5400)
    parser.add_argument("--audit-timeout", type=int, default=5400)
    parser.add_argument("--sleep-seconds", type=int, default=15)
    args = parser.parse_args()
    if args.poll_seconds <= 0:
        raise SystemExit("--poll-seconds must be positive")

    command = read_cmdline(args.old_supervisor_pid)
    if not any(
        Path(value).name
        == "supervise_remaining_200_parallel_campaign.py"
        for value in command
    ):
        raise SystemExit("old PID is not the strict parallel supervisor")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = REPORT_DIR / f"drain_restart_{stamp}.json"
    report: dict[str, Any] = {
        "schema_version": "remaining_200_parallel_drain_restart_v1",
        "started_at": utc_now(),
        "updated_at": utc_now(),
        "finished_at": None,
        "status": "validating",
        "old_supervisor_pid": args.old_supervisor_pid,
    }
    atomic_write_json(report_path, report)
    old_stopped = False
    old_replaced = False
    try:
        boundaries, expected = capture_boundaries(
            args.old_supervisor_pid
        )
        report.update(status="draining", boundaries=boundaries)
        atomic_write_json(report_path, report)

        os.kill(args.old_supervisor_pid, signal.SIGSTOP)
        old_stopped = True
        wait_for_campaign_drain(
            boundaries,
            timeout=args.drain_timeout,
            poll_seconds=args.poll_seconds,
            report=report,
            report_path=report_path,
        )

        report.update(status="journaling", resumed_at=utc_now())
        atomic_write_json(report_path, report)
        journal_checkpoint = len(read_jsonl(JOURNAL))
        os.kill(args.old_supervisor_pid, signal.SIGCONT)
        old_stopped = False
        wait_for_normal_journal(
            args.old_supervisor_pid,
            expected,
            timeout=args.journal_timeout,
            poll_seconds=min(args.poll_seconds, 0.05),
        )
        os.kill(args.old_supervisor_pid, signal.SIGSTOP)
        old_stopped = True
        if has_attempt_start(
            read_jsonl(JOURNAL), checkpoint=journal_checkpoint
        ):
            raise RuntimeError(
                "old supervisor staged a replacement attempt during handoff"
            )
        wait_for_children_to_finish(
            args.old_supervisor_pid,
            timeout=args.journal_timeout,
            poll_seconds=args.poll_seconds,
        )

        report.update(status="replacing", journaled_at=utc_now())
        atomic_write_json(report_path, report)
        stop_process(args.old_supervisor_pid)
        old_stopped = False
        old_replaced = True
        append_jsonl(
            JOURNAL,
            {
                "event": (
                    "parallel_supervisor_natural_pause"
                    if args.pause_only
                    else "parallel_supervisor_drain_restart"
                ),
                "created_at": utc_now(),
                "old_pid": args.old_supervisor_pid,
                "boundaries": [
                    {
                        "paper_id": row["paper_id"],
                        "attempt": row["attempt"],
                    }
                    for row in boundaries
                ],
                "reason": (
                    "user-requested natural pause after active papers finish"
                    if args.pause_only
                    else (
                        "activate tested resume, ticket-dedup, "
                        "closure-receipt, and adaptive rework scheduling fixes"
                    )
                ),
            },
        )
        if args.pause_only:
            report.update(
                status="complete",
                finished_at=utc_now(),
                action="natural_pause",
                new_supervisor_pid=None,
            )
            atomic_write_json(report_path, report)
            atomic_write_json(
                REPORT_DIR / "drain_pause_latest.json", report
            )
            pid_path = REPORT_DIR / "parallel_supervisor.pid"
            if pid_path.exists():
                try:
                    recorded_pid = int(
                        pid_path.read_text(encoding="utf-8").strip()
                    )
                except ValueError:
                    recorded_pid = None
                if recorded_pid == args.old_supervisor_pid:
                    pid_path.unlink()
            (REPORT_DIR / "parallel_supervisor.paused").write_text(
                json.dumps(
                    {
                        "paused_at": report["finished_at"],
                        "old_supervisor_pid": args.old_supervisor_pid,
                        "report_path": str(report_path.relative_to(ROOT)),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
        new_pid, stdout_path, stderr_path = launch_supervisor(args)
        report.update(
            status="complete",
            finished_at=utc_now(),
            new_supervisor_pid=new_pid,
            stdout_path=str(stdout_path.relative_to(ROOT)),
            stderr_path=str(stderr_path.relative_to(ROOT)),
        )
        atomic_write_json(report_path, report)
        atomic_write_json(
            REPORT_DIR / "drain_restart_latest.json", report
        )
        (REPORT_DIR / "parallel_supervisor.pid").write_text(
            f"{new_pid}\n", encoding="utf-8"
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        report.update(
            status="failed",
            finished_at=utc_now(),
            error=f"{type(error).__name__}: {error}"[:4000],
        )
        atomic_write_json(report_path, report)
        atomic_write_json(
            REPORT_DIR / "drain_restart_latest.json", report
        )
        if old_stopped and not old_replaced and process_exists(
            args.old_supervisor_pid
        ):
            os.kill(args.old_supervisor_pid, signal.SIGCONT)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
