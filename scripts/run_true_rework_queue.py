#!/usr/bin/env python3
"""Run a start-once, bounded true Codex re-review queue.

This controller is intentionally conservative:
- it starts the per-paper message workflow at most once;
- every retry uses rework_context/<paper_id>/CODEX_REVIEW_PROMPT.md;
- owner repairs are launched in fresh Codex CLI sessions only when requested;
- strict gates decide acceptance;
- after the attempt cap, the paper is marked blocked/unrecoverable and the
  queue advances instead of looping forever.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from refine_true_rework_queue_status import (
    attach_refined_statuses_to_summary,
    write_accepted_sample_audit_manifest,
    write_followup_queue_manifests,
)
from run_ten_paper_message_tests import candidate_papers


MESSAGE_ROOT = Path(".miaobi-paper-review")


def safe_dir_name(paper_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._=-]+", "_", paper_id.strip())
    return cleaned.strip("._") or "paper"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def safe_stamp() -> str:
    return now_iso().replace(":", "").replace("-", "")


def day_stamp() -> str:
    return now_iso()[:10].replace("-", "")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - queue must preserve partial failures
        return {"_parse_error": str(exc), "_path": str(path)}
    return data if isinstance(data, dict) else {"_not_object": True, "_path": str(path)}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
            if isinstance(value, dict):
                rows.append(value)
        except json.JSONDecodeError:
            rows.append({"raw": line[:500]})
    return rows


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def run(
    cmd: list[str],
    cwd: Path,
    *,
    allow_fail: bool = False,
    input_text: str | None = None,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if proc.returncode and not allow_fail:
        raise SystemExit(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc


def bridge(repo: Path, *args: str, allow_fail: bool = True) -> subprocess.CompletedProcess[str]:
    return run([sys.executable, str(repo / "scripts" / "miaobi_message_bridge.py"), "--root", str(MESSAGE_ROOT), *args], repo, allow_fail=allow_fail)


def workflow_context_path(repo: Path, paper_id: str) -> Path:
    return repo / MESSAGE_ROOT / "workflows" / safe_dir_name(paper_id) / "workflow_context.json"


def load_context(repo: Path, paper_id: str) -> dict[str, Any]:
    return read_json(workflow_context_path(repo, paper_id))


def load_manifest_paper_ids(path: Path) -> list[str]:
    data = read_json(path)
    if isinstance(data.get("paper_ids"), list):
        return [str(item) for item in data["paper_ids"]]
    if isinstance(data.get("results"), list):
        return [str(item.get("paper_id")) for item in data["results"] if isinstance(item, dict) and item.get("paper_id")]
    if isinstance(data.get("papers"), list):
        ids: list[str] = []
        for item in data["papers"]:
            if isinstance(item, str):
                ids.append(item)
            elif isinstance(item, dict) and item.get("paper_id"):
                ids.append(str(item["paper_id"]))
        return ids
    raise SystemExit(f"manifest has no paper_ids/results/papers: {path}")


def selected_papers(args: argparse.Namespace) -> list[str]:
    ids: list[str] = []
    for paper_id in args.paper_id or []:
        ids.append(paper_id)
    if args.manifest:
        ids.extend(load_manifest_paper_ids(Path(args.manifest)))
    if not ids:
        ids.extend(candidate_papers(args.limit or 10))
    seen: set[str] = set()
    unique: list[str] = []
    for paper_id in ids:
        if paper_id not in seen:
            unique.append(paper_id)
            seen.add(paper_id)
    return unique[: args.limit] if args.limit else unique


def ensure_manifest(repo: Path, paper_id: str) -> Path:
    report = read_json(repo / "reports" / f"{paper_id}.complete_message_test_report.json")
    manifest = report.get("manifest")
    if manifest and Path(str(manifest)).exists():
        return Path(str(manifest))
    path = repo / "reports" / f"{paper_id}.true_rework_queue_manifest.json"
    write_json(path, {"generated_at": now_iso(), "paper_ids": [paper_id], "test_type": "true_rework_queue_single_paper"})
    return path


def start_initial_queue_once(repo: Path, paper_id: str, *, reset: bool, no_start_initial: bool) -> dict[str, Any]:
    report = repo / "reports" / f"{paper_id}.complete_message_test_report.json"
    context = workflow_context_path(repo, paper_id)
    if report.exists() and context.exists() and not reset:
        return {"started": False, "reason": "existing_workflow_reused", "report": str(report), "context": str(context)}
    if no_start_initial:
        return {"started": False, "skipped": True, "reason": "no_start_initial", "report_exists": report.exists(), "context_exists": context.exists()}
    cmd = [sys.executable, "scripts/run_one_paper_complete_message_test.py", "--paper-id", paper_id]
    if reset:
        cmd.append("--reset")
    started_at = now_iso()
    proc = run(cmd, repo, allow_fail=True)
    return {
        "started": proc.returncode == 0,
        "reason": "initial_queue_bootstrap_invoked_once",
        "returncode": proc.returncode,
        "started_at": started_at,
        "finished_at": now_iso(),
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
        "report": str(report),
        "context": str(context),
    }


def run_gates(repo: Path, paper_id: str, manifest: Path, attempt: int, phase: str) -> dict[str, Any]:
    reports = repo / "reports"
    semantic_report = reports / f"{paper_id}.true_rework_queue_attempt_{attempt}.{phase}.semantic_gate.json"
    publication_report = reports / f"{paper_id}.true_rework_queue_attempt_{attempt}.{phase}.publication_quality.json"
    semantic_proc = run(
        [
            sys.executable,
            ".codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py",
            "--root",
            ".",
            "--manifest",
            str(manifest),
            "--json",
        ],
        repo,
        allow_fail=True,
    )
    semantic_report.write_text(semantic_proc.stdout, encoding="utf-8")
    publication_proc = run(
        [
            sys.executable,
            ".codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py",
            "--root",
            ".",
            "--manifest",
            str(manifest),
            "--json-out",
            str(publication_report),
        ],
        repo,
        allow_fail=True,
    )
    semantic = read_json(semantic_report)
    publication = read_json(publication_report)
    semantic_issue_codes = sorted(
        {
            str(issue.get("code"))
            for result in semantic.get("results") or []
            if isinstance(result, dict)
            for issue in result.get("issues") or []
            if isinstance(issue, dict) and issue.get("code")
        }
    )
    passed = (
        int(semantic.get("paper_count") or 0) == 1
        and int(semantic.get("publication_grade_pass_count") or 0) == 1
        and publication.get("publication_grade_pass") is True
    )
    return {
        "attempt": attempt,
        "phase": phase,
        "semantic_report": str(semantic_report),
        "publication_report": str(publication_report),
        "semantic_returncode": semantic_proc.returncode,
        "publication_returncode": publication_proc.returncode,
        "semantic_pass_count": int(semantic.get("publication_grade_pass_count") or 0),
        "semantic_fail_count": int(semantic.get("publication_grade_fail_count") or 0),
        "semantic_issue_codes": semantic_issue_codes,
        "publication_quality_pass": publication.get("publication_grade_pass"),
        "publication_risk_counts": publication.get("risk_counts") or {},
        "passed": passed,
    }


def build_rework_context(
    repo: Path,
    paper_id: str,
    max_rework: int,
    *,
    obtainable_only: bool = False,
    prompt_mode: str = "standard",
) -> dict[str, Any]:
    cmd = [sys.executable, "scripts/build_rework_context_packet.py", "--paper-id", paper_id, "--max-rework", str(max_rework)]
    if obtainable_only:
        cmd.append("--obtainable-only")
    if prompt_mode != "standard":
        cmd.extend(["--prompt-mode", prompt_mode])
    proc = run(
        cmd,
        repo,
        allow_fail=True,
    )
    payload = read_json_from_text(proc.stdout)
    return {
        "returncode": proc.returncode,
        "context": payload.get("context"),
        "prompt": payload.get("prompt"),
        "owner_workers": payload.get("owner_workers") or [],
        "failure_reason_count": payload.get("failure_reason_count"),
        "stdout_tail": proc.stdout[-1000:],
        "stderr_tail": proc.stderr[-1000:],
    }


def source_gap_summary(repo: Path, paper_id: str) -> dict[str, Any]:
    """Return documented material gaps that should stop obtainable-only loops."""
    paths = [
        repo / "papers" / paper_id / "work" / "review" / "quality_feedback.json",
        repo / "papers" / paper_id / "final" / "review_report.json",
        repo / "paper_packets" / paper_id / "analysis" / "adjudication_report.json",
    ]
    gaps: list[dict[str, Any]] = []
    reasons: list[dict[str, Any]] = []
    source_gap_tokens = (
        "unrecoverable",
        "missing_primary",
        "missing_external",
        "external_source_needed",
        "source_exhaust",
        "figure",
        "chart",
        "ocr_unreadable",
        "supplement",
        "moesm",
        "not locally recoverable",
        "cannot be recovered",
    )
    for path in paths:
        data = read_json(path)
        for gap in data.get("unrecoverable_material_gaps") or []:
            if isinstance(gap, dict):
                item = dict(gap)
                item.setdefault("artifact_path", str(path))
                gaps.append(item)
        for reason in data.get("qc_failure_reasons") or []:
            if not isinstance(reason, dict):
                continue
            blob = json.dumps(reason, ensure_ascii=False).lower()
            if any(token in blob for token in source_gap_tokens):
                item = dict(reason)
                item.setdefault("artifact_path", str(path))
                reasons.append(item)
    return {
        "has_source_gap": bool(gaps or reasons),
        "unrecoverable_material_gaps": gaps,
        "source_gap_reasons": reasons,
    }


def read_json_from_text(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def codex_worker_command(repo: Path, prompt_path: Path, output_path: Path, args: argparse.Namespace) -> list[str]:
    cmd = ["codex", "exec", "--skip-git-repo-check", "-C", str(repo), "-m", args.model, "-o", str(output_path)]
    cmd.extend(["-c", f'model_reasoning_effort="{args.reasoning_effort}"'])
    if args.codex_bypass_approvals_and_sandbox:
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    else:
        cmd.extend(["-s", args.sandbox, "-c", 'approval_policy="never"'])
    cmd.append("-")
    return cmd


def classify_worker_infra_failure(result: dict[str, Any], *, retry_timeouts: bool) -> dict[str, Any]:
    """Classify Codex CLI/API process failures separately from paper quality gaps."""
    if result.get("dry_run"):
        return {"infra_failed": False, "infra_retryable": False}

    if not result.get("launched") and result.get("reason") == "prompt_missing":
        return {
            "infra_failed": True,
            "infra_retryable": False,
            "infra_reason_code": "codex_worker_prompt_missing",
            "infra_reason_summary": "Codex owner-worker prompt was missing; this needs script/context repair before retry.",
        }

    if result.get("timed_out"):
        return {
            "infra_failed": True,
            "infra_retryable": bool(retry_timeouts),
            "infra_reason_code": "codex_worker_timeout",
            "infra_reason_summary": "Codex owner-worker hit the configured watchdog.",
        }

    returncode = result.get("returncode")
    if returncode in {None, 0}:
        return {"infra_failed": False, "infra_retryable": False}

    blob = f"{result.get('stdout_tail') or ''}\n{result.get('stderr_tail') or ''}".lower()
    api_tokens = (
        "api",
        "429",
        "500",
        "502",
        "503",
        "504",
        "rate limit",
        "overloaded",
        "server error",
        "service unavailable",
        "gateway",
        "network",
        "connection",
        "connection reset",
        "stream",
        "request timed out",
        "temporarily unavailable",
    )
    interrupt_tokens = (
        "interrupted",
        "interrupt",
        "sigterm",
        "sigint",
        "signal",
        "keyboardinterrupt",
        "econnreset",
        "broken pipe",
    )
    if "invalid prompt" in blob and "limited access to this content for safety reasons" in blob:
        code = "codex_prompt_safety_restriction"
        summary = "Codex CLI refused the owner-worker prompt/content for safety reasons."
    elif any(token in blob for token in api_tokens):
        code = "codex_api_or_network_error"
        summary = "Codex CLI exited non-zero with API/network-like error text."
    elif any(token in blob for token in interrupt_tokens) or (isinstance(returncode, int) and returncode < 0):
        code = "codex_worker_interrupted"
        summary = "Codex CLI owner-worker appears to have been interrupted."
    else:
        code = "codex_worker_nonzero_exit"
        summary = "Codex CLI owner-worker exited non-zero before a successful review result."
    return {
        "infra_failed": True,
        # A generic non-zero exit often means the nested Codex worker wrote
        # artifacts but failed to emit a final assistant message. Return to the
        # controller immediately so strict gates can judge the artifacts instead
        # of burning all infra retries on the same already-reviewed paper.
        "infra_retryable": code not in {"codex_worker_nonzero_exit", "codex_prompt_safety_restriction"},
        "infra_reason_code": code,
        "infra_reason_summary": summary,
    }


def record_worker_infra_retry(repo: Path, paper_id: str, attempt: int, run_result: dict[str, Any], retry_no: int, max_retries: int) -> None:
    row = {
        "created_at": now_iso(),
        "paper_id": paper_id,
        "attempt": attempt,
        "retry_no": retry_no,
        "max_retries": max_retries,
        "returncode": run_result.get("returncode"),
        "timed_out": run_result.get("timed_out"),
        "infra_reason_code": run_result.get("infra_reason_code"),
        "infra_reason_summary": run_result.get("infra_reason_summary"),
        "output": run_result.get("output"),
    }
    append_jsonl(repo / "reports" / f"worker_infra_retries_{day_stamp()}.jsonl", row)
    bridge(
        repo,
        "record-state",
        "--paper-id",
        paper_id,
        "--state",
        "codex_worker_infra_retry",
        "--role",
        "queue_controller",
        "--status",
        "needs_rework",
        "--output-summary",
        f"Codex owner-worker infra failure {retry_no}/{max_retries}: {run_result.get('infra_reason_code')}",
        "--chat",
        "Codex worker/API/interruption failure recorded; retrying same owner prompt without changing scientific status.",
    )


def run_codex_worker_once(repo: Path, paper_id: str, prompt_path: Path, output_path: Path, attempt: int, infra_run: int, args: argparse.Namespace) -> dict[str, Any]:
    cmd = codex_worker_command(repo, prompt_path, output_path, args)
    started_at = now_iso()
    try:
        proc = run(cmd, repo, allow_fail=True, input_text=prompt_path.read_text(encoding="utf-8"), timeout=args.worker_timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
        return {
            "launched": True,
            "timed_out": True,
            "command": cmd,
            "returncode": 124,
            "started_at": started_at,
            "finished_at": now_iso(),
            "timeout_seconds": args.worker_timeout_seconds,
            "prompt": str(prompt_path.relative_to(repo)) if prompt_path.is_relative_to(repo) else str(prompt_path),
            "output": str(output_path),
            "infra_run": infra_run,
            "stdout_tail": stdout[-4000:],
            "stderr_tail": stderr[-4000:],
        }
    return {
        "launched": True,
        "timed_out": False,
        "command": cmd,
        "returncode": proc.returncode,
        "started_at": started_at,
        "finished_at": now_iso(),
        "prompt": str(prompt_path.relative_to(repo)) if prompt_path.is_relative_to(repo) else str(prompt_path),
        "output": str(output_path),
        "infra_run": infra_run,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }


def launch_codex_worker(repo: Path, paper_id: str, prompt: str, attempt: int, args: argparse.Namespace) -> dict[str, Any]:
    prompt_path = repo / prompt
    if not prompt_path.exists():
        result = {"launched": False, "returncode": 127, "reason": "prompt_missing", "prompt": prompt}
        result.update(classify_worker_infra_failure(result, retry_timeouts=args.retry_worker_timeouts))
        return result
    if args.dry_run:
        output_path = repo / "reports" / f"{paper_id}.true_rework_queue_attempt_{attempt}.codex_last_message.md"
        return {"launched": False, "dry_run": True, "command": codex_worker_command(repo, prompt_path, output_path, args), "prompt": prompt, "output": str(output_path)}

    max_retries = max(0, args.worker_infra_retries)
    max_runs = max_retries + 1
    runs: list[dict[str, Any]] = []
    last_result: dict[str, Any] = {}
    for infra_run in range(1, max_runs + 1):
        suffix = "" if infra_run == 1 else f".infra_retry_{infra_run}"
        output_path = repo / "reports" / f"{paper_id}.true_rework_queue_attempt_{attempt}{suffix}.codex_last_message.md"
        last_result = run_codex_worker_once(repo, paper_id, prompt_path, output_path, attempt, infra_run, args)
        last_result.update(classify_worker_infra_failure(last_result, retry_timeouts=args.retry_worker_timeouts))
        runs.append(dict(last_result))
        if not last_result.get("infra_failed"):
            last_result["infra_retry_count"] = infra_run - 1
            last_result["infra_runs"] = runs
            return last_result
        if not last_result.get("infra_retryable") or infra_run >= max_runs:
            break
        record_worker_infra_retry(repo, paper_id, attempt, last_result, infra_run, max_retries)

    last_result["infra_retry_count"] = max(0, len(runs) - 1)
    last_result["infra_retry_exhausted"] = bool(last_result.get("infra_failed") and last_result.get("infra_retryable") and len(runs) >= max_runs)
    last_result["infra_runs"] = runs
    return last_result


def _ticket_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [value]
    return []


def _unique_ticket_ids(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value and value not in seen:
            unique.append(value)
            seen.add(value)
    return unique


def _ticket_ids_from_keys(data: dict[str, Any], keys: tuple[str, ...]) -> set[str]:
    ids: set[str] = set()
    for key in keys:
        ids.update(_ticket_list(data.get(key)))
    return ids


def _closed_ticket_ids_from_response_rows(rows: list[dict[str, Any]]) -> tuple[set[str], set[str], bool]:
    closed: set[str] = set()
    remaining: set[str] = set()
    saw_remaining = False
    closed_keys = (
        "ticket_id",
        "ticket_ids",
        "closed_rework_ticket_ids",
        "resolved_rework_ticket_ids",
        "resolved_rework_tickets",
        "resolved_ticket_ids",
    )
    for row in rows:
        status = str(row.get("status") or "").lower()
        ticket_values = _ticket_ids_from_keys(row, closed_keys)
        is_closed_status = (
            status in {"resolved", "closed", "accepted", "accepted_with_cautions"}
            or status.startswith("resolved")
            or "closed" in status
        )
        if is_closed_status:
            closed.update(ticket_values)
        else:
            closed.update(_ticket_ids_from_keys(row, closed_keys[2:]))
        if "remaining_rework_ticket_ids" in row:
            saw_remaining = True
            remaining.update(_ticket_list(row.get("remaining_rework_ticket_ids")))
    return closed, remaining, saw_remaining


def open_ticket_ids(repo: Path, paper_id: str) -> list[str]:
    response_rows = read_jsonl(repo / "paper_packets" / paper_id / "rework" / "rework_responses.jsonl")
    response_closed, response_remaining, saw_remaining = _closed_ticket_ids_from_response_rows(response_rows)

    # workflow_context is the current-state source; request/report ledgers are historical unless explicitly open.
    ctx = load_context(repo, paper_id)
    if "open_rework_tickets" in ctx:
        ctx_open = _ticket_list(ctx.get("open_rework_tickets"))
        ctx_closed = _ticket_ids_from_keys(
            ctx,
            ("closed_rework_tickets", "closed_rework_ticket_ids", "resolved_rework_tickets", "resolved_rework_ticket_ids"),
        )
        return _unique_ticket_ids(
            [ticket_id for ticket_id in ctx_open if ticket_id not in ctx_closed and ticket_id not in response_closed]
        )

    report = read_json(repo / "reports" / f"{paper_id}.complete_message_test_report.json")
    report_closed = _ticket_ids_from_keys(
        report,
        ("closed_rework_ticket_ids", "resolved_rework_ticket_ids", "resolved_rework_tickets", "resolved_ticket_ids"),
    ) | response_closed
    report_open = _ticket_ids_from_keys(report, ("open_rework_ticket_ids", "open_rework_tickets"))
    if report_open:
        return _unique_ticket_ids([ticket_id for ticket_id in report_open if ticket_id not in report_closed])
    if report.get("open_rework_ticket_count") == 0:
        return []
    if isinstance(report.get("open_rework_ticket_count"), int) and report.get("open_rework_ticket_count", 0) > 0:
        return _unique_ticket_ids([ticket_id for ticket_id in _ticket_list(report.get("rework_ticket_ids")) if ticket_id not in report_closed])

    packet_manifest = read_json(repo / "paper_packets" / paper_id / "packet_manifest.json")
    packet_closed = _ticket_ids_from_keys(
        packet_manifest,
        ("closed_rework_ticket_ids", "resolved_rework_ticket_ids", "resolved_rework_tickets", "resolved_ticket_ids"),
    ) | response_closed
    packet_open = _ticket_ids_from_keys(packet_manifest, ("open_rework_ticket_ids", "open_rework_tickets"))
    if packet_open:
        return _unique_ticket_ids([ticket_id for ticket_id in packet_open if ticket_id not in packet_closed])
    if packet_manifest.get("open_rework_ticket_count") == 0:
        return []
    if isinstance(packet_manifest.get("open_rework_ticket_count"), int) and packet_manifest.get("open_rework_ticket_count", 0) > 0:
        return _unique_ticket_ids([ticket_id for ticket_id in _ticket_list(packet_manifest.get("rework_ticket_ids")) if ticket_id not in packet_closed])

    if saw_remaining:
        return _unique_ticket_ids([ticket_id for ticket_id in response_remaining if ticket_id not in response_closed])

    rows = read_jsonl(repo / "paper_packets" / paper_id / "rework" / "rework_requests.jsonl")
    requested = [str(row.get("ticket_id")) for row in rows if row.get("ticket_id")]
    return _unique_ticket_ids([ticket_id for ticket_id in requested if ticket_id not in response_closed])


def resolve_tickets(repo: Path, paper_id: str, ticket_ids: list[str], gate: dict[str, Any], attempt: int) -> None:
    if not ticket_ids:
        return
    cmd = [
        "resolve-rework",
        "--paper-id",
        paper_id,
        "--status",
        "resolved",
        "--state",
        f"true_rework_attempt_{attempt}",
        "--resolved-by",
        "agent",
        "--message",
        f"Bounded true rework attempt {attempt}: strict gates passed; closing tickets.",
        "--artifact-ref",
        gate["semantic_report"],
        "--artifact-ref",
        gate["publication_report"],
    ]
    for ticket_id in ticket_ids:
        cmd += ["--ticket-id", ticket_id]
    bridge(repo, *cmd)


def record_gate_state(repo: Path, paper_id: str, status: str, attempt: int, summary: str, gate: dict[str, Any], context_packet: dict[str, Any] | None = None) -> None:
    cmd = [
        "record-state",
        "--paper-id",
        paper_id,
        "--state",
        f"true_rework_attempt_{attempt}",
        "--role",
        "quality_gate",
        "--status",
        status,
        "--attempt",
        str(attempt),
        "--set-gate",
        f"semantic_gate_ready={str(gate.get('passed') is True).lower()}",
        "--set-gate",
        f"publication_grade_ready={str(gate.get('passed') is True).lower()}",
        "--artifact",
        f"semantic_gate={gate['semantic_report']}",
        "--artifact",
        f"publication_quality={gate['publication_report']}",
        "--output-summary",
        summary,
        "--chat",
        summary,
    ]
    if status == "blocked":
        cmd += ["--set-status", "analysis=analysis_blocked"]
    elif status == "needs_rework":
        cmd += ["--set-status", "analysis=analysis_needs_analysis_rework"]
    else:
        cmd += ["--set-status", "analysis=analysis_source_reviewed_accepted"]
    if context_packet:
        if context_packet.get("context"):
            cmd += ["--artifact", f"rework_context_packet={context_packet['context']}"]
        if context_packet.get("prompt"):
            cmd += ["--artifact", f"codex_re_review_prompt={context_packet['prompt']}"]
        for ticket_id in open_ticket_ids(repo, paper_id):
            cmd += ["--rework-ticket", ticket_id]
    bridge(repo, *cmd)


def quality_feedback_path(repo: Path, paper_id: str) -> Path:
    return repo / "papers" / paper_id / "work" / "review" / "quality_feedback.json"


def mark_blocked_after_best_effort(
    repo: Path,
    paper_id: str,
    max_rework: int,
    attempts: list[dict[str, Any]],
    context_packet: dict[str, Any] | None,
    *,
    reason: str | None = None,
    code: str = "bounded_rework_limit_reached",
) -> dict[str, Any]:
    path = quality_feedback_path(repo, paper_id)
    feedback = read_json(path)
    gap = {
        "gap_code": code,
        "owner_worker": "worker-6",
        "source_paths_checked": [],
        "tools_attempted": [
            "codex_cli_owner_worker_attempts",
            "semantic_three_layer_gate.py",
            "check_three_layer_publication_quality.py",
            "miaobi_message_bridge.py validate",
        ],
        "why_unrecoverable": reason
        or f"Strict gates still failed or tickets stayed open after {max_rework} bounded owner-worker attempts; no unsupported value was fabricated.",
        "impact": "paper remains non-publication-grade and must stay blocked or await external/manual source recovery",
        "blocks_publication_grade": True,
        "next_action": "record_and_continue",
    }
    if context_packet and context_packet.get("context"):
        context_path = repo / str(context_packet["context"])
        context = read_json(context_path)
        inventory = context.get("source_inventory") or {}
        for summary in inventory.values():
            if isinstance(summary, dict) and summary.get("exists") and summary.get("path"):
                gap["source_paths_checked"].append(str(summary["path"]))
        gap["source_paths_checked"] = gap["source_paths_checked"][:20]
    if not isinstance(feedback.get("qc_failure_reasons"), list):
        feedback["qc_failure_reasons"] = []
    if not isinstance(feedback.get("unrecoverable_material_gaps"), list):
        feedback["unrecoverable_material_gaps"] = []
    feedback["qc_failure_reasons"].append(
        {
            "code": code,
            "severity": "blocking",
            "owner_worker": "worker-6",
            "reason": gap["why_unrecoverable"],
            "artifact_path": str(path),
        }
    )
    feedback["unrecoverable_material_gaps"].append(gap)
    feedback["bounded_rework_result"] = {
        "status": "blocked_after_best_effort",
        "result_status": "blocked_watchdog_timeout_retryable" if code == "codex_worker_timeout" else "blocked_rework_cap_unresolved",
        "result_reason_code": code,
        "max_rework_attempts": max_rework,
        "attempt_count": len(attempts),
        "updated_at": now_iso(),
        "note": "Controller stopped this paper and advanced the queue instead of retrying indefinitely.",
    }
    write_json(path, feedback)
    append_jsonl(
        repo / "paper_packets" / paper_id / "rework" / "rework_responses.jsonl",
        {
            "record_type": "rework_response",
            "paper_id": paper_id,
            "ticket_ids": open_ticket_ids(repo, paper_id),
            "status": "blocked_after_best_effort",
            "resolved_by": "agent",
            "state": "bounded_rework_limit",
            "message": gap["why_unrecoverable"],
            "artifact_refs": [str(path)] + ([str(context_packet.get("context"))] if context_packet and context_packet.get("context") else []),
            "created_at": now_iso(),
        },
    )
    bridge(
        repo,
        "record-state",
        "--paper-id",
        paper_id,
        "--state",
        "bounded_rework_limit",
        "--role",
        "quality_gate",
        "--status",
        "blocked",
        "--set-status",
        "analysis=analysis_blocked",
        "--set-gate",
        "semantic_gate_ready=false",
        "--set-gate",
        "publication_grade_ready=false",
        "--artifact",
        f"quality_feedback={path}",
        "--output-summary",
        gap["why_unrecoverable"],
        "--chat",
        "达到打回上限：已标注不可控/不可恢复 gap，停止本篇并处理下一篇。",
    )
    return {"quality_feedback": str(path), "gap": gap}


def validate_message_bus(repo: Path, paper_id: str) -> dict[str, Any]:
    proc = bridge(repo, "validate", "--paper-id", paper_id, allow_fail=True)
    return {"returncode": proc.returncode, "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-1000:]}


def qc_context(repo: Path, paper_id: str, attempts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Collect gate/feedback signals for rich queue statuses."""
    paths = {
        "quality_feedback": repo / "papers" / paper_id / "work" / "review" / "quality_feedback.json",
        "review_report": repo / "papers" / paper_id / "final" / "review_report.json",
        "adjudication_report": repo / "paper_packets" / paper_id / "analysis" / "adjudication_report.json",
    }
    qc_reasons: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for name, path in paths.items():
        data = read_json(path)
        for item in data.get("qc_failure_reasons") or []:
            if isinstance(item, dict):
                row = dict(item)
                row.setdefault("artifact_path", str(path))
                row["_source"] = name
                qc_reasons.append(row)
        for item in data.get("unrecoverable_material_gaps") or []:
            if isinstance(item, dict):
                row = dict(item)
                row.setdefault("artifact_path", str(path))
                row["_source"] = name
                gaps.append(row)

    worker_results = [
        attempt.get("worker_result") or {}
        for attempt in attempts or []
        if isinstance(attempt, dict)
    ]
    semantic_issue_codes: list[str] = []
    for attempt in attempts or []:
        if not isinstance(attempt, dict):
            continue
        for phase in ("gate_before", "gate_after"):
            semantic_issue_codes.extend((attempt.get(phase) or {}).get("semantic_issue_codes") or [])

    return {
        "qc_codes": sorted({str(item.get("code")) for item in qc_reasons if item.get("code")}),
        "gap_codes": sorted({str(item.get("gap_code")) for item in gaps if item.get("gap_code")}),
        "owner_workers": sorted({str(item.get("owner_worker")) for item in qc_reasons if item.get("owner_worker")}),
        "semantic_issue_codes": sorted({str(code) for code in semantic_issue_codes if code}),
        "worker_timed_out": any(result.get("timed_out") for result in worker_results),
        "worker_returncodes": [result.get("returncode") for result in worker_results if "returncode" in result],
        "worker_infra_failed": any(result.get("infra_failed") for result in worker_results),
        "worker_infra_retry_exhausted": any(result.get("infra_retry_exhausted") for result in worker_results),
        "worker_infra_reason_codes": sorted({str(result.get("infra_reason_code")) for result in worker_results if result.get("infra_reason_code")}),
        "worker_infra_retry_count": max([int(result.get("infra_retry_count") or 0) for result in worker_results] or [0]),
        "qc_failure_reasons": qc_reasons,
        "unrecoverable_material_gaps": gaps,
    }


def classify_result_status(
    repo: Path,
    paper_id: str,
    terminal_status: str,
    attempts: list[dict[str, Any]] | None,
    *,
    worker_timeout_seconds: int | None = None,
) -> dict[str, Any]:
    """Keep the legacy terminal status, but add a richer machine status."""
    ctx = qc_context(repo, paper_id, attempts)
    code_blob = " ".join(ctx["qc_codes"] + ctx["gap_codes"] + ctx["semantic_issue_codes"]).lower()
    reason_blob = json.dumps(
        {
            "qc": ctx["qc_failure_reasons"],
            "gaps": ctx["unrecoverable_material_gaps"],
        },
        ensure_ascii=False,
    ).lower()

    result = {
        "result_status": terminal_status,
        "result_category": "unknown",
        "result_reason_code": terminal_status,
        "result_reason_summary": "No richer status classification was available.",
        "retryability": "unknown",
        "watchdog_seconds": worker_timeout_seconds,
        "qc_codes": ctx["qc_codes"],
        "gap_codes": ctx["gap_codes"],
        "semantic_issue_codes": ctx["semantic_issue_codes"],
        "owner_workers": ctx["owner_workers"],
        "worker_timed_out": ctx["worker_timed_out"],
        "worker_returncodes": ctx["worker_returncodes"],
        "worker_infra_failed": ctx["worker_infra_failed"],
        "worker_infra_retry_exhausted": ctx["worker_infra_retry_exhausted"],
        "worker_infra_reason_codes": ctx["worker_infra_reason_codes"],
        "worker_infra_retry_count": ctx["worker_infra_retry_count"],
    }

    if terminal_status.startswith("accepted"):
        result.update(
            {
                "result_category": "accepted",
                "result_reason_code": "strict_gates_passed",
                "result_reason_summary": "Semantic gate, publication-quality gate, and ticket closure reached an accepted queue outcome.",
                "retryability": "not_needed",
            }
        )
    elif terminal_status == "initial_queue_failed":
        result.update(
            {
                "result_status": "infrastructure_initial_queue_failed",
                "result_category": "infrastructure_failed",
                "result_reason_code": "initial_queue_bootstrap_failed",
                "result_reason_summary": "Initial workflow/bootstrap failed before an owner-worker review could run.",
                "retryability": "retry_after_script_or_source_fix",
            }
        )
    elif terminal_status == "missing_initial_queue":
        result.update(
            {
                "result_status": "infrastructure_missing_initial_queue",
                "result_category": "infrastructure_failed",
                "result_reason_code": "initial_workflow_context_missing",
                "result_reason_summary": "The start-once workflow context was missing and bootstrap was disabled.",
                "retryability": "retry_after_initialization",
            }
        )
    elif ctx["worker_timed_out"]:
        result.update(
            {
                "result_status": "blocked_watchdog_timeout_retryable",
                "result_category": "blocked_process_timeout",
                "result_reason_code": "codex_worker_timeout",
                "result_reason_summary": (
                    f"Owner Codex worker hit the {worker_timeout_seconds or 'configured'}s watchdog; "
                    "this is a retryable process/scope timeout, not proof that source material is absent."
                ),
                "retryability": "retry_with_longer_watchdog_or_narrower_owner_prompt",
            }
        )
    elif ctx["worker_infra_failed"]:
        codes = ctx["worker_infra_reason_codes"] or ["codex_worker_infra_failure"]
        exhausted = ctx["worker_infra_retry_exhausted"]
        result.update(
            {
                "result_status": "infrastructure_codex_worker_retry_exhausted" if exhausted else "infrastructure_codex_worker_failed",
                "result_category": "infrastructure_retry_exhausted" if exhausted else "infrastructure_failed",
                "result_reason_code": codes[0],
                "result_reason_summary": (
                    f"Codex owner-worker had infrastructure/API/interruption failures; "
                    f"retry_count={ctx['worker_infra_retry_count']}."
                ),
                "retryability": "defer_to_infrastructure_recovery_queue",
            }
        )
    elif (
        "figure4_exact" in code_blob
        or "figure_chart" in code_blob
        or (
            "figure" in reason_blob
            and ("exact" in reason_blob or "chart" in reason_blob or "percentage" in reason_blob)
            and not any(token in code_blob for token in ("supplement_table", "supplementary_moesm", "missing_external_supplement", "moesm"))
        )
    ):
        result.update(
            {
                "result_status": "blocked_figure_chart_value_gap",
                "result_category": "blocked_source_gap",
                "result_reason_code": "figure_or_chart_exact_value_unrecoverable",
                "result_reason_summary": "Remaining exact values are figure/chart-only or not source-promotable from local structured material.",
                "retryability": "retry_only_with_digitization_or_external_source",
            }
        )
    elif (
        any(token in code_blob for token in ("supplement_table", "supplementary_moesm", "missing_external_supplement", "moesm"))
        or any(token in reason_blob for token in ("true supplementary table", "html placeholder", "landing-", "moesm", "absent from packet"))
        or "external_source_needed" in code_blob
        or "external_source_needed" in reason_blob
    ):
        result.update(
            {
                "result_status": "blocked_missing_external_supplement",
                "result_category": "blocked_source_gap",
                "result_reason_code": "missing_external_supplement",
                "result_reason_summary": "A specific supplementary source/table is absent or only represented by non-data landing/placeholder material.",
                "retryability": "retry_only_after_source_staging",
            }
        )
    elif any(token in code_blob for token in ("review_article_no_primary_activity_matrix", "dramp_literature_links_without_primary")):
        result.update(
            {
                "result_status": "blocked_no_primary_assay_source",
                "result_category": "blocked_source_gap",
                "result_reason_code": "no_primary_assay_or_sequence_snapshot",
                "result_reason_summary": "Local paper/database evidence lacks primary assay or sequence rows sufficient for source-verified acceptance.",
                "retryability": "retry_only_with_primary_source_or_database_snapshot",
            }
        )
    elif (
        "no_supported_activity_rows_extracted" in code_blob
        or "activity_extraction_requires_worker2_rework" in code_blob
        or "missing_activity_records" in code_blob
    ):
        result.update(
            {
                "result_status": "blocked_activity_table_extraction_gap",
                "result_category": "blocked_parser_or_manual_extraction_gap",
                "result_reason_code": "activity_table_rows_not_safely_extracted",
                "result_reason_summary": "Activity/toxicity rows are missing or unsafe under current parser/table-shape handling.",
                "retryability": "retry_with_worker2_table_shape_or_manual_vision_fallback",
            }
        )
    elif "database_conflicts_require_adjudication" in code_blob:
        result.update(
            {
                "result_status": "blocked_database_adjudication_gap",
                "result_category": "blocked_database_conflict",
                "result_reason_code": "database_conflicts_require_adjudication",
                "result_reason_summary": "Linked database source_conflict/database-only rows still require row-level adjudication.",
                "retryability": "retry_with_worker4_database_adjudication",
            }
        )
    elif terminal_status == "blocked_after_best_effort":
        result.update(
            {
                "result_status": "blocked_rework_cap_unresolved",
                "result_category": "blocked_quality_gate_unresolved",
                "result_reason_code": "bounded_rework_limit_reached",
                "result_reason_summary": "Strict gates remained blocked after bounded obtainable-only repair.",
                "retryability": "retry_only_with_more_specific_owner_context",
            }
        )
    return result


def failed_result(paper_id: str, terminal_status: str, bootstrap: dict[str, Any], reason_code: str, reason_summary: str) -> dict[str, Any]:
    return {
        "paper_id": paper_id,
        "terminal_status": terminal_status,
        "result_status": f"infrastructure_{terminal_status}",
        "result_category": "infrastructure_failed",
        "result_reason_code": reason_code,
        "result_reason_summary": reason_summary,
        "retryability": "retry_after_script_or_source_fix",
        "accepted": False,
        "blocked": False,
        "bootstrap": bootstrap,
    }


def paper_runtime_retry_failed_result(paper_id: str, failures: list[dict[str, Any]], max_retries: int) -> dict[str, Any]:
    result = failed_result(
        paper_id,
        "paper_runtime_retry_exhausted",
        {"runtime_failures": failures, "max_retries": max_retries},
        "paper_runtime_exception_retry_exhausted",
        "Paper processing raised controller/runtime exceptions after bounded retries; tagged for later recovery.",
    )
    result.update(
        {
            "result_status": "infrastructure_paper_runtime_retry_exhausted",
            "result_category": "infrastructure_retry_exhausted",
            "retryability": "defer_to_infrastructure_recovery_queue",
            "runtime_retry_count": len(failures),
        }
    )
    return result


def run_one(repo: Path, paper_id: str, args: argparse.Namespace) -> dict[str, Any]:
    bootstrap = start_initial_queue_once(repo, paper_id, reset=args.reset_initial, no_start_initial=args.no_start_initial)
    if bootstrap.get("returncode") not in {None, 0}:
        return failed_result(
            paper_id,
            "initial_queue_failed",
            bootstrap,
            "initial_queue_bootstrap_failed",
            "Initial workflow/bootstrap failed before owner-worker review.",
        )
    if bootstrap.get("skipped") and not workflow_context_path(repo, paper_id).exists():
        return failed_result(
            paper_id,
            "missing_initial_queue",
            bootstrap,
            "initial_workflow_context_missing",
            "Initial workflow context is missing and bootstrap was disabled.",
        )

    manifest = ensure_manifest(repo, paper_id)
    attempts: list[dict[str, Any]] = []
    latest_context: dict[str, Any] | None = None
    terminal = "awaiting_targeted_rework"

    for attempt in range(1, args.max_rework + 1):
        gate_before = run_gates(repo, paper_id, manifest, attempt, "before_worker")
        tickets_before = open_ticket_ids(repo, paper_id)
        if gate_before["passed"] and not tickets_before:
            record_gate_state(repo, paper_id, "completed", attempt, f"Strict gates already pass before attempt {attempt}; no rework needed.", gate_before)
            terminal = "accepted_before_worker_rework"
            attempts.append({"attempt": attempt, "gate_before": gate_before, "tickets_before": tickets_before})
            break

        latest_context = build_rework_context(
            repo,
            paper_id,
            args.max_rework,
            obtainable_only=args.obtainable_only,
            prompt_mode=args.prompt_mode,
        )
        worker_result = launch_codex_worker(repo, paper_id, str(latest_context.get("prompt") or ""), attempt, args)
        attempt_row: dict[str, Any] = {
            "attempt": attempt,
            "gate_before": gate_before,
            "tickets_before": tickets_before,
            "rework_context_packet": latest_context,
            "worker_result": worker_result,
        }
        if args.dry_run:
            record_gate_state(
                repo,
                paper_id,
                "needs_rework",
                attempt,
                f"Dry run prepared Codex re-review prompt for attempt {attempt}; queue bootstrap was not repeated.",
                gate_before,
                latest_context,
            )
            terminal = "dry_run_rework_prompt_prepared"
            attempts.append(attempt_row)
            break

        gate_after = run_gates(repo, paper_id, manifest, attempt, "after_worker")
        tickets_after = open_ticket_ids(repo, paper_id)
        attempt_row.update({"gate_after": gate_after, "tickets_after": tickets_after})
        attempts.append(attempt_row)

        if gate_after["passed"]:
            resolve_tickets(repo, paper_id, tickets_after, gate_after, attempt)
            record_gate_state(repo, paper_id, "completed", attempt, f"Attempt {attempt}: strict gates passed after owner Codex re-review.", gate_after)
            terminal = "accepted_after_rework"
            break

        if worker_result.get("infra_failed") and not worker_result.get("timed_out"):
            reason = (
                "Codex owner-worker exited non-zero after bounded review, and strict gates still did not pass; "
                f"controller retried {worker_result.get('infra_retry_count', 0)} time(s), tagged the paper for later infrastructure recovery, and advanced. "
                "If the worker wrote partial artifacts, the after_worker gate reports above remain the scientific source of truth."
            )
            blocked = mark_blocked_after_best_effort(
                repo,
                paper_id,
                args.max_rework,
                attempts,
                latest_context,
                reason=reason,
                code=worker_result.get("infra_reason_code") or "codex_worker_infra_failure",
            )
            record_gate_state(
                repo,
                paper_id,
                "blocked",
                attempt,
                reason,
                gate_after,
                latest_context,
            )
            attempt_row["blocked_after_best_effort"] = blocked
            terminal = "blocked_after_best_effort"
            break

        source_gap = source_gap_summary(repo, paper_id)
        if args.obtainable_only and source_gap["has_source_gap"]:
            reason = (
                "Obtainable-only mode: local source-supported evidence was preserved, but the remaining blocker is documented as "
                "not recoverable from local materials; controller marked the paper blocked_after_best_effort and advanced."
            )
            blocked = mark_blocked_after_best_effort(
                repo,
                paper_id,
                args.max_rework,
                attempts,
                latest_context,
                reason=reason,
                code="obtainable_only_source_gap_documented",
            )
            blocked["source_gap_summary"] = source_gap
            record_gate_state(
                repo,
                paper_id,
                "blocked",
                attempt,
                reason,
                gate_after,
                latest_context,
            )
            attempt_row["blocked_after_best_effort"] = blocked
            terminal = "blocked_after_best_effort"
            break

        if worker_result.get("timed_out"):
            reason = (
                f"Owner Codex worker timed out after {args.worker_timeout_seconds} seconds during bounded source recovery; "
                "controller marked the paper blocked and advanced to avoid stalling the queue."
            )
            blocked = mark_blocked_after_best_effort(
                repo,
                paper_id,
                args.max_rework,
                attempts,
                latest_context,
                reason=reason,
                code="codex_worker_timeout",
            )
            record_gate_state(
                repo,
                paper_id,
                "blocked",
                attempt,
                reason,
                gate_after,
                latest_context,
            )
            attempt_row["blocked_after_best_effort"] = blocked
            terminal = "blocked_after_best_effort"
            break

        if attempt < args.max_rework:
            record_gate_state(
                repo,
                paper_id,
                "needs_rework",
                attempt,
                f"Attempt {attempt}/{args.max_rework}: gates still fail; refreshed context packet and returning to owner worker.",
                gate_after,
                latest_context,
            )
            terminal = "awaiting_targeted_rework"
        else:
            blocked = mark_blocked_after_best_effort(repo, paper_id, args.max_rework, attempts, latest_context)
            record_gate_state(
                repo,
                paper_id,
                "blocked",
                attempt,
                f"Attempt cap {args.max_rework} reached; paper marked blocked/unrecoverable and queue advances.",
                gate_after,
                latest_context,
            )
            attempt_row["blocked_after_best_effort"] = blocked
            terminal = "blocked_after_best_effort"

    validation = validate_message_bus(repo, paper_id)
    rich_status = classify_result_status(
        repo,
        paper_id,
        terminal,
        attempts,
        worker_timeout_seconds=args.worker_timeout_seconds,
    )
    return {
        "paper_id": paper_id,
        "terminal_status": terminal,
        **rich_status,
        "accepted": terminal.startswith("accepted"),
        "blocked": terminal == "blocked_after_best_effort",
        "bootstrap": bootstrap,
        "manifest": str(manifest),
        "attempt_count": len(attempts),
        "max_rework_attempts": args.max_rework,
        "attempts": attempts,
        "message_bus_validation": validation,
        "queue_policy": {
            "initial_queue_started_once": bootstrap.get("started") is True,
            "initial_queue_reused": bootstrap.get("reason") == "existing_workflow_reused",
            "retry_bootstrap_invocations": 0,
            "advance_on_unrecoverable_gap": True,
            "obtainable_only_mode": args.obtainable_only,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", help="Manifest with paper_ids/results/papers")
    parser.add_argument("--paper-id", action="append", help="Paper id to process; may repeat")
    parser.add_argument("--limit", type=int, default=None, help="Cap selected papers; default is all manifest papers or 10 auto-candidates")
    parser.add_argument("--max-rework", type=int, default=5)
    parser.add_argument("--reset-initial", action="store_true", help="Reset the initial per-paper workflow once before retries")
    parser.add_argument("--no-start-initial", action="store_true", help="Do not create missing initial workflow; useful for dry-run checks")
    parser.add_argument("--dry-run", action="store_true", help="Prepare prompts/context and record queue state but do not launch Codex workers")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--reasoning-effort", default="xhigh", choices=["low", "medium", "high", "xhigh"])
    parser.add_argument("--sandbox", default="danger-full-access", choices=["read-only", "workspace-write", "danger-full-access"])
    parser.add_argument("--codex-bypass-approvals-and-sandbox", action="store_true")
    parser.add_argument("--worker-timeout-seconds", type=int, default=1800)
    parser.add_argument("--worker-infra-retries", type=int, default=0, help="Retry Codex CLI API/non-zero/interruption failures before tagging for later recovery.")
    parser.add_argument("--retry-worker-timeouts", action="store_true", help="Also retry watchdog timeouts as worker infrastructure failures.")
    parser.add_argument("--paper-runtime-retries", type=int, default=0, help="Retry per-paper controller/runtime exceptions before tagging for later recovery.")
    parser.add_argument("--run-label", help="Optional label for lane-specific summary files, e.g. queue50_lane1")
    parser.add_argument("--obtainable-only", action="store_true", help="Extract only locally supportable material; documented source gaps stop the paper and advance the queue.")
    parser.add_argument(
        "--prompt-mode",
        default="standard",
        choices=["standard", "policy_safe_minimal"],
        help="Prompt/context style for owner Codex workers.",
    )
    args = parser.parse_args()

    if args.max_rework < 1:
        raise SystemExit("--max-rework must be >= 1")
    if args.worker_infra_retries < 0:
        raise SystemExit("--worker-infra-retries must be >= 0")
    if args.paper_runtime_retries < 0:
        raise SystemExit("--paper-runtime-retries must be >= 0")

    repo = Path.cwd()
    paper_ids = selected_papers(args)
    if not paper_ids:
        raise SystemExit("no papers selected")

    results = []
    for index, paper_id in enumerate(paper_ids, start=1):
        print(f"[{index}/{len(paper_ids)}] true rework queue {paper_id}", flush=True)
        runtime_failures: list[dict[str, Any]] = []
        for runtime_try in range(1, args.paper_runtime_retries + 2):
            try:
                result = run_one(repo, paper_id, args)
                if runtime_failures:
                    result["paper_runtime_retries"] = runtime_failures
                    result["paper_runtime_retry_count"] = len(runtime_failures)
                results.append(result)
                break
            except BaseException as exc:  # noqa: BLE001 - queue must tag and advance after bounded retries
                if isinstance(exc, KeyboardInterrupt):
                    raise
                failure = {
                    "created_at": now_iso(),
                    "paper_id": paper_id,
                    "runtime_try": runtime_try,
                    "max_retries": args.paper_runtime_retries,
                    "exception_type": type(exc).__name__,
                    "exception": str(exc),
                    "traceback_tail": traceback.format_exc()[-4000:],
                }
                runtime_failures.append(failure)
                append_jsonl(repo / "reports" / f"paper_runtime_retries_{day_stamp()}.jsonl", failure)
                if runtime_try <= args.paper_runtime_retries:
                    print(f"[{index}/{len(paper_ids)}] retrying {paper_id} after runtime failure {runtime_try}/{args.paper_runtime_retries}: {type(exc).__name__}", flush=True)
                    continue
                results.append(paper_runtime_retry_failed_result(paper_id, runtime_failures, args.paper_runtime_retries))
                break

    summary = {
        "ok": all(not item.get("terminal_status", "").endswith("failed") for item in results),
        "generated_at": now_iso(),
        "test_type": "true_rework_queue_start_once_bounded_best_effort",
        "completion_claim": "queue_control_and_rework_execution_report_not_blanket_publication_grade_acceptance",
        "paper_ids": paper_ids,
        "max_rework_attempts": args.max_rework,
        "dry_run": args.dry_run,
        "quality_control": {
            "queue_start_policy": "start once; retries consume rework_context only",
            "acceptance_requires": ["open_rework_tickets=0", "semantic gate pass", "publication-quality gate pass", "worker-6 source-reviewed acceptance"],
            "unrecoverable_policy": "record unrecoverable_material_gaps/blocked_after_best_effort and advance to next paper after cap",
            "obtainable_only_mode": args.obtainable_only,
            "rich_result_status": "terminal_status remains backward-compatible; result_status/result_category/result_reason_code describe why the queue stopped",
            "worker_infra_retries": args.worker_infra_retries,
            "paper_runtime_retries": args.paper_runtime_retries,
            "prompt_mode": args.prompt_mode,
            "no_infinite_loop": True,
        },
        "terminal_status_counts": {},
        "result_status_counts": {},
        "result_category_counts": {},
        "results": results,
    }
    for item in results:
        status = str(item.get("terminal_status") or "unknown")
        summary["terminal_status_counts"][status] = summary["terminal_status_counts"].get(status, 0) + 1
        result_status = str(item.get("result_status") or "unknown")
        summary["result_status_counts"][result_status] = summary["result_status_counts"].get(result_status, 0) + 1
        result_category = str(item.get("result_category") or "unknown")
        summary["result_category_counts"][result_category] = summary["result_category_counts"].get(result_category, 0) + 1

    summary_prefix = f"true_rework_queue_{args.run_label}" if args.run_label else "true_rework_queue"
    stamp = safe_stamp()
    out = repo / "reports" / f"{summary_prefix}_{stamp}.json"
    latest = repo / "reports" / f"{summary_prefix}_latest.json"
    attach_refined_statuses_to_summary(summary)
    followup_paths = write_followup_queue_manifests(
        summary,
        out_dir=repo / "reports" / "followup_queues",
        prefix=f"{summary_prefix}_{stamp}",
        source_summary_path=str(out),
        run_label=args.run_label,
    )
    accepted_sample_path = write_accepted_sample_audit_manifest(
        summary,
        out_dir=repo / "reports" / "followup_queues",
        prefix=f"{summary_prefix}_{stamp}",
        source_summary_path=str(out),
        run_label=args.run_label,
        baseline_sample_size=min(25, max(5, len(results) // 20)),
    )
    summary["followup_queue_manifest_paths"] = followup_paths
    summary["accepted_sample_audit_manifest_path"] = accepted_sample_path
    write_json(out, summary)
    write_json(latest, summary)
    print(json.dumps({"ok": summary["ok"], "summary_path": str(out), "latest_path": str(latest), "terminal_status_counts": summary["terminal_status_counts"], "result_status_counts": summary["result_status_counts"], "refined_status_counts": summary["refined_status_counts"], "followup_queue_manifest_paths": followup_paths, "accepted_sample_audit_manifest_path": accepted_sample_path}, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
