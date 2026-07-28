#!/usr/bin/env python3
"""Run distinct strict-paper reviews concurrently without weakening per-paper QA.

Every paper still uses the fail-closed campaign executor and its six sequential
canonical workers. Parallelism exists only across different paper IDs.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import time
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any

try:
    from pipeline_v2.deepmine import (
        supervise_remaining_200_strict_campaign as base,
    )
except ModuleNotFoundError:
    import supervise_remaining_200_strict_campaign as base


REPAIR_STATUSES = {
    "needs_targeted_semantic_rework",
    "awaiting_worker6_repair_or_mechanical_acceptance",
    "six_worker_review_in_progress",
    "awaiting_leader_field_semantic_audit",
    "awaiting_independent_verifier",
}


def eligible_launch_rows(
    state: dict[str, Any],
    *,
    active_papers: set[str],
    attempts: Counter[str],
    max_attempts_per_paper: int,
    available_slots: int,
    max_parallel_papers: int,
    max_rework_parallel: int,
    active_rework_count: int,
) -> list[dict[str, Any]]:
    """Choose fair, distinct papers while reserving capacity for fresh reviews."""
    rows: list[dict[str, Any]] = []
    seen_papers: set[str] = set()
    for row in base.ordered_nonterminal_rows(state):
        paper_id = str(row.get("paper_id") or "")
        if (
            not paper_id
            or paper_id in seen_papers
            or paper_id in active_papers
            or attempts[paper_id] >= max_attempts_per_paper
        ):
            continue
        seen_papers.add(paper_id)
        rows.append(row)
    if not rows or available_slots < 1:
        return []

    ready = [
        row for row in rows
        if row.get("workflow_status") == "ready_for_six_worker_review"
    ]
    repair = [
        row for row in rows
        if row.get("workflow_status") in REPAIR_STATUSES
    ]
    repair.sort(
        key=lambda row: (
            attempts[str(row.get("paper_id"))],
            int(row.get("queue_index") or 10**9),
            str(row.get("paper_id") or ""),
        )
    )

    # While untouched papers remain, cap repair concurrency so one difficult
    # cluster cannot occupy every lane. Once breadth-first review is exhausted,
    # all lanes may converge outstanding repairs.
    total_rework_backlog = len(repair) + active_rework_count
    effective_rework_parallel = max_rework_parallel
    if ready:
        maximum_with_fresh_lane = max(0, max_parallel_papers - 1)
        effective_rework_parallel = min(
            effective_rework_parallel, maximum_with_fresh_lane
        )
        if total_rework_backlog >= max_parallel_papers:
            effective_rework_parallel = maximum_with_fresh_lane
    repair_capacity = (
        max(0, effective_rework_parallel - active_rework_count)
        if ready
        else available_slots
    )
    selected = repair[: min(repair_capacity, available_slots)]
    selected_ids = {str(row.get("paper_id")) for row in selected}
    for row in ready:
        if len(selected) >= available_slots:
            break
        if str(row.get("paper_id")) not in selected_ids:
            selected.append(row)
            selected_ids.add(str(row.get("paper_id")))
    if not ready:
        for row in rows:
            if len(selected) >= available_slots:
                break
            if str(row.get("paper_id")) not in selected_ids:
                selected.append(row)
                selected_ids.add(str(row.get("paper_id")))
    return selected


def publish_parallel_status(
    *,
    state: dict[str, Any],
    active: dict[Future[tuple[int, Path, Path]], dict[str, Any]],
    cycle_number: int,
    attempts: Counter[str],
    latest_result: dict[str, Any] | None,
    supervisor_started_at: str,
    max_parallel_papers: int,
) -> None:
    active_runs = sorted(
        (
            {
                "paper_id": meta["paper_id"],
                "attempt": meta["attempt"],
                "started_at": meta["started_at"],
                "workflow_status": meta["before_status"],
            }
            for meta in active.values()
        ),
        key=lambda row: (row["paper_id"], row["attempt"]),
    )
    first = active_runs[0] if active_runs else {}
    payload = base.status_payload(
        state=state,
        active_paper=first.get("paper_id"),
        active_attempt=first.get("attempt"),
        sweep_number=cycle_number,
        attempts=attempts,
        latest_result=latest_result,
        supervisor_started_at=supervisor_started_at,
    )
    payload.update(
        {
            "mode": "parallel_distinct_papers",
            "max_parallel_papers": max_parallel_papers,
            "active_runs": active_runs,
        }
    )
    base.publish_status(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-parallel-papers", type=int, default=4)
    parser.add_argument("--max-rework-parallel", type=int, default=1)
    parser.add_argument("--max-attempts-per-paper", type=int, default=12)
    parser.add_argument("--max-rework-rounds", type=int, default=3)
    parser.add_argument("--worker-timeout", type=int, default=5400)
    parser.add_argument("--audit-timeout", type=int, default=5400)
    parser.add_argument("--sleep-seconds", type=int, default=15)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    for name in (
        "max_parallel_papers",
        "max_rework_parallel",
        "max_attempts_per_paper",
        "max_rework_rounds",
        "worker_timeout",
        "audit_timeout",
        "sleep_seconds",
    ):
        if getattr(args, name) < 1:
            raise SystemExit(f"--{name.replace('_', '-')} must be positive")
    if args.max_rework_parallel > args.max_parallel_papers:
        raise SystemExit("--max-rework-parallel cannot exceed parallel capacity")

    base.REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lock_handle = base.LOCK.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        raise SystemExit("another strict campaign supervisor owns the lock") from error

    supervisor_started_at = base.utc_now()
    lock_handle.seek(0)
    lock_handle.truncate()
    lock_handle.write(
        json.dumps(
            {
                "pid": os.getpid(),
                "mode": "parallel_distinct_papers",
                "acquired_at": supervisor_started_at,
            }
        )
        + "\n"
    )
    lock_handle.flush()

    attempts = base.attempt_counts()
    latest_result: dict[str, Any] | None = None
    cycle_number = 0
    base.append_jsonl(
        base.JOURNAL,
        {
            "event": "parallel_supervisor_started",
            "created_at": supervisor_started_at,
            "pid": os.getpid(),
            "arguments": vars(args),
        },
    )

    campaign_args = argparse.Namespace(
        max_rework_rounds=args.max_rework_rounds,
        worker_timeout=args.worker_timeout,
        audit_timeout=args.audit_timeout,
    )
    active: dict[Future[tuple[int, Path, Path]], dict[str, Any]] = {}
    executor = ThreadPoolExecutor(
        max_workers=args.max_parallel_papers,
        thread_name_prefix="strict-paper",
    )
    try:
        while True:
            cycle_number += 1
            base.refresh_ledger(
                base.REPORT_DIR
                / f"{base.run_stamp()}.parallel-cycle-{cycle_number:06d}-ledger.log"
            )
            state = base.read_state()
            terminal = int(
                (state.get("counts") or {}).get(
                    "terminal_scientific_review_complete", 0
                )
            )
            if terminal == int(
                (state.get("counts") or {}).get("frozen_denominator", 200)
            ):
                publish_parallel_status(
                    state=state,
                    active=active,
                    cycle_number=cycle_number,
                    attempts=attempts,
                    latest_result=latest_result,
                    supervisor_started_at=supervisor_started_at,
                    max_parallel_papers=args.max_parallel_papers,
                )
                base.append_jsonl(
                    base.JOURNAL,
                    {
                        "event": "parallel_supervisor_terminal_complete",
                        "created_at": base.utc_now(),
                        "terminal_count": terminal,
                    },
                )
                return 0

            active_papers = {
                str(meta["paper_id"]) for meta in active.values()
            }
            active_rework_count = sum(
                meta["before_status"] in REPAIR_STATUSES
                for meta in active.values()
            )
            selected = eligible_launch_rows(
                state,
                active_papers=active_papers,
                attempts=attempts,
                max_attempts_per_paper=args.max_attempts_per_paper,
                available_slots=args.max_parallel_papers - len(active),
                max_parallel_papers=args.max_parallel_papers,
                max_rework_parallel=args.max_rework_parallel,
                active_rework_count=active_rework_count,
            )
            if args.dry_run:
                print(
                    json.dumps(
                        {
                            "selected": [row["paper_id"] for row in selected],
                            "max_parallel_papers": args.max_parallel_papers,
                            "max_rework_parallel": args.max_rework_parallel,
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
                return 0

            for row in selected:
                paper_id = str(row["paper_id"])
                attempt = attempts[paper_id] + 1
                before_status = str(row.get("workflow_status"))
                started_at = base.utc_now()
                meta = {
                    "paper_id": paper_id,
                    "attempt": attempt,
                    "sweep_number": cycle_number,
                    "before_status": before_status,
                    "started_at": started_at,
                }
                base.append_jsonl(
                    base.JOURNAL,
                    {
                        "event": "paper_attempt_started",
                        "created_at": started_at,
                        **{key: value for key, value in meta.items() if key != "started_at"},
                        "scheduler_mode": "parallel_distinct_papers",
                    },
                )
                future = executor.submit(
                    base.run_campaign,
                    paper_id=paper_id,
                    attempt=attempt,
                    sweep_number=cycle_number,
                    args=campaign_args,
                )
                active[future] = meta

            publish_parallel_status(
                state=state,
                active=active,
                cycle_number=cycle_number,
                attempts=attempts,
                latest_result=latest_result,
                supervisor_started_at=supervisor_started_at,
                max_parallel_papers=args.max_parallel_papers,
            )
            if not active:
                base.append_jsonl(
                    base.JOURNAL,
                    {
                        "event": "parallel_supervisor_attempt_budget_exhausted",
                        "created_at": base.utc_now(),
                        "remaining_nonterminal": (
                            state.get("counts") or {}
                        ).get("remaining_nonterminal"),
                    },
                )
                return 2

            done, _ = wait(
                active,
                timeout=args.sleep_seconds,
                return_when=FIRST_COMPLETED,
            )
            if not done:
                continue
            for future in done:
                meta = active.pop(future)
                paper_id = str(meta["paper_id"])
                try:
                    returncode, stdout_path, stderr_path = future.result()
                except Exception as error:  # noqa: BLE001 - fail closed in ledger
                    returncode = 1
                    stdout_path = base.REPORT_DIR / "missing.stdout.log"
                    stderr_path = base.REPORT_DIR / "missing.stderr.log"
                    stderr_path.write_text(
                        f"{type(error).__name__}: {error}\n", encoding="utf-8"
                    )
                attempts[paper_id] += 1
                base.refresh_ledger(
                    base.REPORT_DIR
                    / f"{base.run_stamp()}.{paper_id}.parallel-post-attempt-ledger.log"
                )
                after_state = base.read_state()
                after_row = next(
                    row
                    for row in after_state.get("papers", [])
                    if row.get("paper_id") == paper_id
                )
                latest_result = {
                    **meta,
                    "finished_at": base.utc_now(),
                    "after_status": str(after_row.get("workflow_status")),
                    "campaign_returncode": returncode,
                    "stdout_path": str(stdout_path.relative_to(base.ROOT)),
                    "stderr_path": str(stderr_path.relative_to(base.ROOT)),
                    "scheduler_mode": "parallel_distinct_papers",
                }
                base.append_jsonl(
                    base.JOURNAL,
                    {"event": "paper_attempt_finished", **latest_result},
                )
    finally:
        executor.shutdown(wait=True, cancel_futures=False)


if __name__ == "__main__":
    raise SystemExit(main())
