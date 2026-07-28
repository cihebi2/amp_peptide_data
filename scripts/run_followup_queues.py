#!/usr/bin/env python3
"""Plan or execute follow-up queues produced by true-rework runs.

Default mode is non-destructive planning: it writes the exact commands/manifests
that should be used for each queue type. Use --execute only when intentionally
starting the next recovery wave.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SUPPORTED_EXECUTION_QUEUES = {
    "infra_recovery",
    "watchdog_retry",
    "owner_context_rework_needed",
    "source_staging_needed",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_stamp() -> str:
    return now_utc().replace("-", "").replace(":", "")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"JSON root must be an object: {path}")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def queue_manifest_from_items(source: dict[str, Any], out: Path) -> Path:
    paper_ids = [str(item.get("paper_id")) for item in source.get("items") or [] if item.get("paper_id")]
    manifest = {
        "generated_at": now_utc(),
        "source_followup_manifest": source.get("_path"),
        "queue_name": source.get("queue_name"),
        "paper_count": len(paper_ids),
        "paper_ids": paper_ids,
        "completion_claim": "followup_execution_manifest_not_publication_grade_acceptance",
    }
    write_json(out, manifest)
    return out


def build_queue_plan(manifest_path: Path, out_dir: Path, run_label: str) -> dict[str, Any]:
    data = read_json(manifest_path)
    data["_path"] = str(manifest_path)
    queue_name = str(data.get("queue_name") or manifest_path.stem)
    queue_run_label = f"{run_label}_{queue_name}"
    queue_out_dir = out_dir / queue_run_label
    queue_out_dir.mkdir(parents=True, exist_ok=True)
    paper_count = int(data.get("paper_count") or len(data.get("items") or []))
    command: list[str] = []
    execution_supported = queue_name in SUPPORTED_EXECUTION_QUEUES
    execution_kind = "plan_only"
    generated_manifest = ""

    if queue_name == "infra_recovery":
        generated = queue_manifest_from_items(data, queue_out_dir / f"{queue_run_label}_manifest.json")
        generated_manifest = str(generated)
        command = [
            sys.executable,
            "scripts/run_true_rework_queue.py",
            "--manifest",
            str(generated),
            "--run-label",
            queue_run_label,
            "--max-rework",
            "3",
            "--obtainable-only",
            "--worker-timeout-seconds",
            "1800",
            "--worker-infra-retries",
            "5",
            "--paper-runtime-retries",
            "5",
        ]
        execution_kind = "codex_rework_queue"
    elif queue_name == "watchdog_retry":
        generated = queue_manifest_from_items(data, queue_out_dir / f"{queue_run_label}_manifest.json")
        generated_manifest = str(generated)
        command = [
            sys.executable,
            "scripts/run_true_rework_queue.py",
            "--manifest",
            str(generated),
            "--run-label",
            queue_run_label,
            "--max-rework",
            "2",
            "--obtainable-only",
            "--worker-timeout-seconds",
            "3600",
            "--worker-infra-retries",
            "5",
            "--retry-worker-timeouts",
            "--paper-runtime-retries",
            "5",
        ]
        execution_kind = "codex_rework_queue_long_watchdog"
    elif queue_name == "owner_context_rework_needed":
        generated = queue_manifest_from_items(data, queue_out_dir / f"{queue_run_label}_manifest.json")
        generated_manifest = str(generated)
        command = [
            sys.executable,
            "scripts/run_true_rework_queue.py",
            "--manifest",
            str(generated),
            "--run-label",
            queue_run_label,
            "--max-rework",
            "2",
            "--obtainable-only",
            "--worker-timeout-seconds",
            "2400",
            "--worker-infra-retries",
            "5",
            "--paper-runtime-retries",
            "5",
        ]
        execution_kind = "codex_rework_queue_targeted_context"
    elif queue_name == "source_staging_needed":
        command = [
            sys.executable,
            "scripts/source_staging_preflight.py",
            "--manifest",
            str(manifest_path),
            "--run-label",
            queue_run_label,
        ]
        execution_kind = "source_staging_preflight"
    elif queue_name == "parser_manual_extraction_needed":
        generated = queue_out_dir / f"{queue_run_label}_manual_extraction_tasks.json"
        write_json(
            generated,
            {
                "generated_at": now_utc(),
                "queue_name": queue_name,
                "source_followup_manifest": str(manifest_path),
                "completion_claim": "manual_extraction_task_manifest_not_executed",
                "paper_count": paper_count,
                "items": data.get("items") or [],
                "required_worker": "worker-2",
                "required_action": "repair table parser or run manual/vision extraction before owner re-review",
            },
        )
        generated_manifest = str(generated)
        execution_supported = False
        execution_kind = "manual_extraction_task_manifest"
    elif queue_name == "accepted_sample_audit":
        command = [
            sys.executable,
            "scripts/accepted_sample_audit.py",
            "--manifest",
            str(manifest_path),
            "--run-label",
            queue_run_label,
        ]
        execution_supported = True
        execution_kind = "accepted_sample_audit"

    return {
        "queue_name": queue_name,
        "source_manifest": str(manifest_path),
        "paper_count": paper_count,
        "execution_supported": execution_supported,
        "execution_kind": execution_kind,
        "generated_manifest": generated_manifest,
        "command": command,
    }


def execute_plan(plan: dict[str, Any]) -> dict[str, Any]:
    if not plan.get("execution_supported"):
        return {"executed": False, "reason": "execution_not_supported_for_queue_type"}
    command = plan.get("command") or []
    if not command:
        return {"executed": False, "reason": "no_command"}
    proc = subprocess.run(command, text=True, capture_output=True, check=False)
    return {
        "executed": True,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        action="append",
        help="Follow-up queue manifest. May repeat. Defaults to all latest generated queue manifests.",
    )
    parser.add_argument(
        "--queue",
        action="append",
        help="Queue name to include when using default manifest discovery. May repeat.",
    )
    parser.add_argument("--out-dir", default="reports/followup_queue_runs")
    parser.add_argument("--run-label", default=None)
    parser.add_argument("--execute", action="store_true", help="Execute supported queue commands. Default only plans.")
    return parser.parse_args()


def default_manifests() -> list[Path]:
    roots = sorted(Path("reports/followup_queues").glob("true_rework_queue_next500_obtainable_20260505_*.json"))
    return [path for path in roots if not path.name.endswith("_latest.json")]


def main() -> int:
    args = parse_args()
    run_label = args.run_label or f"followup_{safe_stamp()}"
    manifests = [Path(path) for path in args.manifest] if args.manifest else default_manifests()
    if args.queue:
        wanted = set(args.queue)
        filtered = []
        for path in manifests:
            try:
                queue_name = str(read_json(path).get("queue_name") or "")
            except Exception:
                queue_name = ""
            if queue_name in wanted:
                filtered.append(path)
        manifests = filtered
    if not manifests:
        raise SystemExit("No follow-up manifests selected.")
    out_dir = Path(args.out_dir)
    plans = [build_queue_plan(path, out_dir, run_label) for path in manifests]
    for plan in plans:
        if args.execute:
            plan["execution_result"] = execute_plan(plan)
        else:
            plan["execution_result"] = {"executed": False, "reason": "dry_run_plan_only"}
    report = {
        "generated_at": now_utc(),
        "run_label": run_label,
        "execute": args.execute,
        "completion_claim": "followup_queue_runner_report_not_publication_grade_completion",
        "queue_count": len(plans),
        "paper_count_total": sum(int(plan.get("paper_count") or 0) for plan in plans),
        "plans": plans,
    }
    out = out_dir / f"{run_label}.json"
    latest = out_dir / "followup_queue_runner_latest.json"
    write_json(out, report)
    write_json(latest, report)
    print(json.dumps({"ok": True, "out": str(out), "latest": str(latest), "execute": args.execute, "queue_count": len(plans), "paper_count_total": report["paper_count_total"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
