#!/usr/bin/env python3
"""Refresh owner-worker rework contexts and lane manifests for current queue."""
from __future__ import annotations

import csv
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "reports" / "nar_resource_freeze_v1" / "needs_targeted_rework_work"
OWNER_QUEUE = WORK / "owner_worker_rework_queue_latest.csv"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_owner_rows() -> list[dict[str, str]]:
    if not OWNER_QUEUE.exists():
        raise SystemExit(f"missing owner queue: {OWNER_QUEUE}")
    with OWNER_QUEUE.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def build_context(row: dict[str, str], max_rework: int, prompt_mode: str) -> dict[str, Any]:
    paper_id = row["paper_id"]
    cmd = [
        sys.executable,
        "scripts/build_rework_context_packet.py",
        "--paper-id",
        paper_id,
        "--obtainable-only",
        "--max-rework",
        str(max_rework),
    ]
    if prompt_mode != "standard":
        cmd.extend(["--prompt-mode", prompt_mode])
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    payload: dict[str, Any] = {}
    if proc.stdout.strip().startswith("{"):
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = {}
    return {
        "paper_id": paper_id,
        "returncode": proc.returncode,
        "context": payload.get("context"),
        "prompt": payload.get("prompt"),
        "owner_workers": payload.get("owner_workers") or [],
        "failure_reason_count": payload.get("failure_reason_count"),
        "prompt_mode": prompt_mode,
        "stdout_tail": proc.stdout[-1000:],
        "stderr_tail": proc.stderr[-1000:],
    }


def split_lanes(rows: list[dict[str, str]], lane_count: int) -> list[list[dict[str, str]]]:
    lanes: list[list[dict[str, str]]] = [[] for _ in range(lane_count)]
    for idx, row in enumerate(rows):
        lanes[idx % lane_count].append(row)
    return lanes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane-count", type=int, default=5)
    parser.add_argument("--max-rework", type=int, default=5)
    parser.add_argument("--prompt-mode", default="standard", choices=["standard", "policy_safe_minimal"])
    args = parser.parse_args()

    lane_count = args.lane_count
    max_rework = args.max_rework
    rows = read_owner_rows()
    generated_at = now_iso()
    context_results = [build_context(row, max_rework=max_rework, prompt_mode=args.prompt_mode) for row in rows]
    failed = [row for row in context_results if row["returncode"] != 0 or not row.get("prompt")]

    lane_entries = []
    for lane_no, lane_rows in enumerate(split_lanes(rows, lane_count), start=1):
        items = []
        for row in lane_rows:
            paper_id = row["paper_id"]
            item = dict(row)
            prompt_name = "CODEX_REVIEW_PROMPT_POLICY_SAFE.md" if args.prompt_mode == "policy_safe_minimal" else "CODEX_REVIEW_PROMPT.md"
            item["codex_review_prompt"] = f"rework_context/{paper_id}/{prompt_name}"
            items.append(item)
        lane_payload = {
            "generated_at": generated_at,
            "lane": lane_no,
            "paper_count": len(items),
            "paper_ids": [item["paper_id"] for item in items],
            "items": items,
        }
        lane_path = WORK / f"owner_worker_rework_lane{lane_no:02d}.json"
        write_json(lane_path, lane_payload)
        lane_entries.append(
            {
                "lane": lane_no,
                "paper_count": len(items),
                "paper_ids": lane_payload["paper_ids"],
                "manifest": str(lane_path.relative_to(ROOT)),
            }
        )

    manifest = {
        "generated_at": generated_at,
        "queue": "owner_worker_rework_queue",
        "paper_count": len(rows),
        "lane_count": lane_count,
        "prompt_mode": args.prompt_mode,
        "lanes": lane_entries,
    }
    write_json(WORK / "owner_worker_rework_manifest_latest.json", manifest)
    context_payload = {
        "generated_at": generated_at,
        "count": len(context_results),
        "failed": failed,
        "results": context_results,
    }
    write_json(WORK / "context_build_latest.json", context_payload)
    print(
        json.dumps(
            {
                "ok": not failed,
                "owner_queue_count": len(rows),
                "lane_counts": [lane["paper_count"] for lane in lane_entries],
                "context_failures": len(failed),
                "prompt_mode": args.prompt_mode,
                "manifest": str((WORK / "owner_worker_rework_manifest_latest.json").relative_to(ROOT)),
                "context_build": str((WORK / "context_build_latest.json").relative_to(ROOT)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
