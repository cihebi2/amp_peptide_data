#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_controller(repo_root: Path):
    path = repo_root / "workspace-guide/team-paper-sample/paper_batch_controller.py"
    spec = importlib.util.spec_from_file_location("pbc", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load controller from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure locator coverage across a batch manifest.")
    parser.add_argument("--repo-root", default=".", help="Repository root; defaults to current directory")
    parser.add_argument("--manifest", required=True, help="Path to batch manifest JSON")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (repo_root / manifest_path).resolve()

    manifest = read_json(manifest_path)
    papers_root = repo_root / "papers"
    controller = load_controller(repo_root)

    body_total = 0
    body_with_locator = 0
    papers_all_body_locators = 0
    body_gap_papers: list[str] = []
    final_gap_papers: list[str] = []

    for pid in manifest["paper_ids"]:
        paper_root = papers_root / pid
        body = read_json(paper_root / "work/body_evidence/evidence.json")
        claims = [item for item in body.get("claims", []) if isinstance(item, dict)]
        with_locator = sum(1 for item in claims if item.get("source_locator"))
        body_total += len(claims)
        body_with_locator += with_locator
        if with_locator == len(claims):
            papers_all_body_locators += 1
        else:
            body_gap_papers.append(pid)

        if (not controller.mechanism_record_locator_contract_compatible(repo_root, pid)) or (
            not controller.vc_projection_locator_contract_compatible(repo_root, pid)
        ):
            final_gap_papers.append(pid)

    result = {
        "manifest": str(manifest_path),
        "papers": len(manifest["paper_ids"]),
        "body_claims_total": body_total,
        "body_claims_with_source_locator": body_with_locator,
        "body_claim_locator_ratio": f"{body_with_locator}/{body_total}" if body_total else "0/0",
        "papers_with_all_body_claim_locators": papers_all_body_locators,
        "body_claim_locator_gap_papers": body_gap_papers,
        "final_locator_gap_papers": final_gap_papers,
    }

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
