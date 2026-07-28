#!/usr/bin/env python3
"""Recover declared supplements for the frozen strict 200-paper queue.

This controller only stages and validates source material.  It never marks a
paper reviewed, accepted, publication-grade, or authority-ready.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot"
PILOT_CLI = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot.py"
STATE = (
    PILOT_DIR
    / "manifests/remaining_200_strict_review_state_20260726.json"
)
REPORT_DIR = PILOT_DIR / "reports/material_recovery_200/supplement_batches"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def recover_one(paper_id: str, timeout: int, run_dir: Path) -> dict[str, Any]:
    started_at = utc_now()
    command = [
        "python3",
        str(PILOT_CLI),
        "recover-materials",
        "--paper-id",
        paper_id,
        "--apply",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        timed_out = True

    stdout_path = run_dir / f"{paper_id.replace('/', '_')}.stdout.json"
    stderr_path = run_dir / f"{paper_id.replace('/', '_')}.stderr.txt"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    payload: dict[str, Any] = {}
    try:
        parsed = json.loads(stdout)
        if isinstance(parsed, dict):
            payload = parsed
    except json.JSONDecodeError:
        pass
    still_missing = payload.get("still_missing_count")
    success = (
        returncode == 0
        and payload.get("paper_id") == paper_id
        and still_missing == 0
    )
    return {
        "paper_id": paper_id,
        "started_at": started_at,
        "finished_at": utc_now(),
        "returncode": returncode,
        "timed_out": timed_out,
        "success": success,
        "declared_supplement_count": payload.get("declared_supplement_count"),
        "recovered_count": payload.get("recovered_count"),
        "still_missing_count": still_missing,
        "still_missing": payload.get("still_missing") or [],
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "command": command,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--run-id",
        default=datetime.now(timezone.utc).strftime("supplement_recovery_%Y%m%dT%H%M%SZ"),
    )
    args = parser.parse_args()
    if args.concurrency < 1 or args.concurrency > 16:
        raise SystemExit("--concurrency must be between 1 and 16")

    state = read_json(args.state)
    papers = state.get("papers")
    papers = papers if isinstance(papers, list) else []
    targets = [
        str(row["paper_id"])
        for row in papers
        if isinstance(row, dict)
        and row.get("workflow_status") == "needs_declared_supplement_recovery"
    ]
    if args.limit is not None:
        targets = targets[: args.limit]

    run_dir = REPORT_DIR / args.run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    report_path = REPORT_DIR / f"{args.run_id}.json"
    report: dict[str, Any] = {
        "schema_version": "remaining_200_supplement_recovery_batch_v1",
        "run_id": args.run_id,
        "started_at": utc_now(),
        "finished_at": None,
        "state_path": str(args.state),
        "target_count": len(targets),
        "concurrency": args.concurrency,
        "timeout_seconds_per_paper": args.timeout,
        "material_only_boundary": (
            "Recovery success stages source material only and does not imply "
            "paper review, publication-grade acceptance, or authority readiness."
        ),
        "results": [],
        "counts": {},
    }
    atomic_write_json(report_path, report)

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {
            executor.submit(recover_one, paper_id, args.timeout, run_dir): paper_id
            for paper_id in targets
        }
        for future in as_completed(futures):
            result = future.result()
            report["results"].append(result)
            report["results"].sort(key=lambda row: targets.index(row["paper_id"]))
            report["counts"] = {
                "target": len(targets),
                "completed": len(report["results"]),
                "success": sum(row["success"] for row in report["results"]),
                "still_missing_or_failed": sum(
                    not row["success"] for row in report["results"]
                ),
            }
            atomic_write_json(report_path, report)

    report["finished_at"] = utc_now()
    report["counts"] = {
        "target": len(targets),
        "completed": len(report["results"]),
        "success": sum(row["success"] for row in report["results"]),
        "still_missing_or_failed": sum(not row["success"] for row in report["results"]),
    }
    atomic_write_json(report_path, report)
    atomic_write_json(REPORT_DIR / "latest.json", report)
    print(json.dumps({"report_path": str(report_path), **report["counts"]}, indent=2))
    return 0 if report["counts"]["still_missing_or_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
