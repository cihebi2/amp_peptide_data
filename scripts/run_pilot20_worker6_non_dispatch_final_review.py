#!/usr/bin/env python3
"""Run worker-6 final review for pilot20 papers that never entered owner dispatch."""

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
BASE = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "pilot20" / "source_review_packets"
READJUDICATION = BASE / "worker6_readjudication" / "pilot20_worker6_readjudication_latest.csv"
DISPATCH_INDEX = BASE / "owner_rework_dispatch" / "dispatch_index_latest.csv"
FINAL_MIRROR_STATUS = BASE / "worker6_final_mirror" / "runner" / "worker6_final_runner_status_latest.csv"
OUTDIR = BASE / "worker6_non_dispatch_final_review"
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
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    return data if isinstance(data, dict) else {}


def existing_final_mirror_papers() -> set[str]:
    papers: set[str] = set()
    for path in [DISPATCH_INDEX, FINAL_MIRROR_STATUS]:
        if not path.exists():
            continue
        for row in read_csv(path):
            paper_id = row.get("paper_id", "")
            if paper_id:
                papers.add(paper_id)
    return papers


def selected_rows(limit: int = 0) -> list[dict[str, str]]:
    already = existing_final_mirror_papers()
    rows = [row for row in read_csv(READJUDICATION) if row.get("paper_id") not in already]
    if limit:
        rows = rows[:limit]
    return rows


def codex_command(last_message_path: Path) -> list[str]:
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


def response_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": [
            "paper_id",
            "pilot_sample_id",
            "reviewed_at",
            "review_model",
            "reasoning_effort",
            "final_decision",
            "files_updated",
            "qc_summary",
            "remaining_blockers",
            "worker6_followup",
        ],
        "properties": {
            "final_decision": {
                "enum": [
                    "accepted_with_cautions",
                    "needs_targeted_rework",
                    "blocked_missing_primary_material",
                    "deferred_not_safe_to_edit",
                ]
            }
        },
        "additionalProperties": True,
    }


def build_prompt(row: dict[str, str], task_dir: Path) -> str:
    paper_id = row["paper_id"]
    pilot_id = row["pilot_sample_id"]
    packet_dir = BASE / f"{pilot_id}__{paper_id}"
    result_path = task_dir / "worker6_non_dispatch_final_response.json"
    schema_path = task_dir / "worker6_non_dispatch_final_response.schema.json"
    write_json(schema_path, response_schema())
    return f"""# Worker-6 Final Review For Non-Dispatch Pilot20 Paper

You are worker-6 (`paper-adjudicator-review-worker`) for one pilot20 paper that never entered owner dispatch.

## Hard constraints

- Use `gpt-5.5` with `reasoning_effort=xhigh`; runner command provides this. Treat runner command/header as model/effort provenance unless contradicted.
- Preserve conflicts, cautions, database-only, unresolved, and material gaps.
- Do not mark `accepted_clean` in this pilot.
- Do not mark publication-grade true if hard rework, non-standard mechanism evidence classes in accepted artifacts, missing material, or open rework remains.
- Do not invent missing supplement/PDF/XML evidence.
- If the only prior blocker was model self-proof and source/material/ontology gates now pass, you may write `accepted_with_cautions` with preserved cautions.
- If mechanism evidence classes use labels outside the five-class ontology, repair only if the local source evidence and claim text make the mapping safe; otherwise write `needs_targeted_rework` with concrete owner target.

Allowed mechanism evidence classes: `direct_mechanism`, `phenotype_supported`, `inferred_mechanism`, `computational_only`, `unknown_or_not_tested`.

## Input

- pilot_sample_id: `{pilot_id}`
- paper_id: `{paper_id}`
- readjudicated_decision: `{row.get('readjudicated_decision', '')}`
- readjudication_reason_code: `{row.get('reason_code', '')}`
- original_decision: `{row.get('original_decision', '')}`
- audit_record_id: `{row.get('audit_record_id', '')}`
- true review result: `{rel(Path(row.get('result_path', '')) if Path(row.get('result_path', '')).is_absolute() else ROOT / row.get('result_path', ''))}`
- review packet: `{rel(packet_dir)}`
- current paper final dir: `papers/{paper_id}/final/`
- packet final dir: `paper_packets/{paper_id}/final/`
- write response JSON: `{rel(result_path)}`
- response schema: `{rel(schema_path)}`

Read these instructions before editing:

1. `.codex/skills/amp-three-layer-curation/SKILL.md`
2. `.codex/skills/paper-adjudicator-review-worker/SKILL.md`
3. `.codex/skills/amp-three-layer-curation/references/publication-grade-source-review.md`
4. `.codex/skills/amp-three-layer-curation/references/publication-grade-quality-gate.md`
5. `.codex/skills/amp-three-layer-curation/references/team-rework-message-contract.md`
6. `.codex/skills/amp-three-layer-curation/references/two-queue-paper-packet-contract.md`

## Task

1. Re-open the true review result, source review packet, packet materials, current final artifacts, and relevant source locators/database rows.
2. Decide whether the previous non-dispatch state can be finalized or must remain nonterminal.
3. For safe acceptance:
   - Mirror/repair mechanism artifacts so accepted files use only the five allowed evidence classes.
   - Update `papers/{paper_id}/final/review_report.json` and `paper_packets/{paper_id}/final/review_report.json` with worker-6 provenance, checked inputs, semantic QA summary, preserved cautions, and zero hard rework targets.
   - Highest positive decision allowed is `accepted_with_cautions`.
4. For nonterminal outcomes:
   - Write/update review reports as `needs_targeted_rework` or `blocked_missing_primary_material`, `publication_grade: false`, and concrete `rework_targets` / `unrecoverable_material_gaps`.
   - Include owner worker, artifact path, failing claim/row/record, failure code, source evidence to check, required action, and acceptance check.
5. Write `{rel(result_path)}` matching schema with `final_decision`, `files_updated`, `qc_summary`, `remaining_blockers`, and `worker6_followup`.

Use Python/JSON tools if helpful. Keep final response short and point to the response JSON.
"""


def validate_response(path: Path) -> tuple[bool, str, str]:
    if not path.exists():
        return False, "missing_worker6_response", ""
    try:
        data = load_json(path)
    except Exception as exc:  # noqa: BLE001
        return False, f"unreadable_worker6_response:{type(exc).__name__}", ""
    required = ["paper_id", "pilot_sample_id", "review_model", "reasoning_effort", "final_decision", "files_updated", "qc_summary", "remaining_blockers"]
    missing = [key for key in required if key not in data]
    if missing:
        return False, "missing_required_keys:" + ",".join(missing), str(data.get("final_decision", ""))
    if data.get("review_model") != "gpt-5.5" or data.get("reasoning_effort") != "xhigh":
        return False, "model_or_reasoning_mismatch", str(data.get("final_decision", ""))
    allowed = {"accepted_with_cautions", "needs_targeted_rework", "blocked_missing_primary_material", "deferred_not_safe_to_edit"}
    decision = str(data.get("final_decision", ""))
    if decision not in allowed:
        return False, f"unknown_final_decision:{decision}", decision
    return True, "valid_worker6_response", decision


def run_one(row: dict[str, str], timeout_seconds: int, force: bool) -> dict[str, Any]:
    task_dir = OUTDIR / f"{row['pilot_sample_id']}__{row['paper_id']}"
    task_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = task_dir / "WORKER6_NON_DISPATCH_FINAL_PROMPT.md"
    response_path = task_dir / "worker6_non_dispatch_final_response.json"
    if force or not prompt_path.exists():
        prompt_path.write_text(build_prompt(row, task_dir), encoding="utf-8")

    stdout_path = task_dir / "codex_worker6.stdout.log"
    stderr_path = task_dir / "codex_worker6.stderr.log"
    last_message_path = task_dir / "CODEX_WORKER6_LAST_MESSAGE.md"
    status_path = task_dir / "worker6_non_dispatch_runner_status.json"

    started_at = now_utc()
    if response_path.exists() and not force:
        ok, validation, decision = validate_response(response_path)
        status = {
            **row,
            "runner_state": "skipped_existing_response" if ok else "existing_response_invalid",
            "runner_validation": validation,
            "final_decision": decision,
            "started_at": started_at,
            "finished_at": now_utc(),
            "elapsed_seconds": 0,
            "returncode": "",
            "response_path": rel(response_path),
        }
        write_json(status_path, status)
        return status

    start = time.monotonic()
    try:
        with stdout_path.open("w", encoding="utf-8") as stdout_fh, stderr_path.open("w", encoding="utf-8") as stderr_fh:
            proc = subprocess.run(
                codex_command(last_message_path),
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

    ok, validation, decision = validate_response(response_path)
    if runner_state == "codex_finished" and ok:
        runner_state = "completed_valid_response"
    elif runner_state == "codex_finished":
        runner_state = "codex_finished_no_valid_response"

    status = {
        **row,
        "runner_state": runner_state,
        "runner_validation": validation,
        "final_decision": decision,
        "started_at": started_at,
        "finished_at": now_utc(),
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "returncode": returncode,
        "response_path": rel(response_path),
        "stdout_log": rel(stdout_path),
        "stderr_log": rel(stderr_path),
        "last_message_path": rel(last_message_path),
    }
    write_json(status_path, status)
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parallel", type=int, default=3)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    rows = selected_rows(args.limit)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    run_id = stamp()
    statuses: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {pool.submit(run_one, row, args.timeout_seconds, args.force): row for row in rows}
        for future in as_completed(futures):
            status = future.result()
            statuses.append(status)
            print(json.dumps({
                "pilot_sample_id": status.get("pilot_sample_id"),
                "paper_id": status.get("paper_id"),
                "runner_state": status.get("runner_state"),
                "final_decision": status.get("final_decision"),
                "validation": status.get("runner_validation"),
            }, ensure_ascii=False, sort_keys=True), flush=True)
    statuses.sort(key=lambda item: item.get("pilot_sample_id", ""))
    fields = [
        "pilot_sample_id",
        "paper_id",
        "database",
        "source_id",
        "audit_record_id",
        "status",
        "original_decision",
        "readjudicated_decision",
        "reason_code",
        "runner_state",
        "runner_validation",
        "final_decision",
        "started_at",
        "finished_at",
        "elapsed_seconds",
        "returncode",
        "response_path",
        "stdout_log",
        "stderr_log",
        "last_message_path",
    ]
    outdir = OUTDIR / "runner"
    csv_path = outdir / f"worker6_non_dispatch_status_{run_id}.csv"
    latest_csv = outdir / "worker6_non_dispatch_status_latest.csv"
    write_csv(csv_path, statuses, fields)
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")
    summary = {
        "generated_at": now_utc(),
        "completion_claim": "pilot20_worker6_non_dispatch_final_review_completed_pending_qc",
        "selected_count": len(rows),
        "parallel": args.parallel,
        "timeout_seconds": args.timeout_seconds,
        "runner_state_counts": dict(Counter(row["runner_state"] for row in statuses)),
        "validation_counts": dict(Counter(row["runner_validation"] for row in statuses)),
        "final_decision_counts": dict(Counter(row["final_decision"] for row in statuses)),
        "outputs": {
            "status_csv": rel(csv_path),
            "latest_status_csv": rel(latest_csv),
            "summary_json": rel(outdir / f"worker6_non_dispatch_summary_{run_id}.json"),
            "latest_summary_json": rel(outdir / "worker6_non_dispatch_summary_latest.json"),
        },
    }
    write_json(outdir / f"worker6_non_dispatch_summary_{run_id}.json", summary)
    write_json(outdir / "worker6_non_dispatch_summary_latest.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
