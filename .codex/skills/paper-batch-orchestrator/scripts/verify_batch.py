#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_controller(repo_root: Path):
    path = repo_root / "workspace-guide/team-paper-sample/paper_batch_controller.py"
    spec = importlib.util.spec_from_file_location("pbc", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load controller from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def list_active_team_sessions() -> list[str]:
    proc = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip().startswith("omx-team-")]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a paper batch against the current manifest.")
    parser.add_argument("--repo-root", default=".", help="Repository root; defaults to current directory")
    parser.add_argument("--manifest", required=True, help="Path to batch manifest JSON")
    parser.add_argument("--include-problems", action="store_true", help="Include full per-paper problem objects")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (repo_root / manifest_path).resolve()

    controller = load_controller(repo_root)
    manifest = read_json(manifest_path)
    paper_ids = manifest["paper_ids"]
    protocol = str(manifest.get("protocol") or "")
    three_layer = protocol == "amp_three_layer_v2"

    ready_count = 0
    structural_ready_count = 0
    problems: list[dict[str, Any]] = []
    for pid in paper_ids:
        if three_layer:
            structural = controller.three_layer_final_artifacts_structurally_ready(repo_root, pid)
            issues = controller.three_layer_final_artifacts_quality_issues(repo_root, pid) if structural else ["not_structurally_ready"]
            ready = structural and not issues
        else:
            structural = controller.final_artifacts_structurally_ready(repo_root, pid)
            ready = controller.final_artifacts_ready(repo_root, pid)
            issues = controller.final_artifacts_quality_issues(repo_root, pid) if structural else ["not_structurally_ready"]
        if structural:
            structural_ready_count += 1
        if ready:
            ready_count += 1
        if (not structural) or (not ready) or issues:
            problems.append(
                {
                    "paper_id": pid,
                    "structural_ready": structural,
                    "final_ready": ready,
                    "quality_issues": issues,
                }
            )

    result: dict[str, Any] = {
        "manifest": str(manifest_path),
        "protocol": protocol or "paper_audit_v1",
        "total": len(paper_ids),
        "structural_ready_count": structural_ready_count,
        "final_ready_count": ready_count,
        "problem_count": len(problems),
        "all_final_ready": ready_count == len(paper_ids) and len(problems) == 0,
        "active_tmux_team_sessions": list_active_team_sessions(),
    }
    if args.include_problems:
        result["problems"] = problems
    else:
        result["problem_papers"] = [item["paper_id"] for item in problems]

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
