#!/usr/bin/env python3
"""Local Miaobi-style message bus for Batch 4 paper review.

The real Miaobi backend stores workflow context, state executions, artifacts,
chat messages, logs, and websocket events in its database. This bridge writes
compatible JSON/JSONL records locally so the paper-review process can use the
same message-passing discipline before a backend integration exists.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_ROOT = Path(".miaobi-paper-review")
JSONL_FILES = {
    "chat": "chat_messages.jsonl",
    "state": "state_executions.jsonl",
    "log": "agent_logs.jsonl",
    "artifact": "artifacts.jsonl",
    "event": "events.jsonl",
}

MATERIAL_STATUS = {
    "material_queued",
    "material_extracting",
    "material_extracted_complete",
    "material_extracted_with_gaps",
    "material_needs_rework",
    "material_blocked_missing_source",
}
ANALYSIS_STATUS = {
    "analysis_queued",
    "analysis_running",
    "analysis_artifacts_present",
    "analysis_needs_material_rework",
    "analysis_needs_analysis_rework",
    "analysis_adjudicated_with_cautions",
    "analysis_source_reviewed_accepted",
    "analysis_accepted",
    "analysis_blocked",
}
GATE_KEYS = {
    "structural_ready",
    "validator_contract_ready",
    "semantic_gate_ready",
    "publication_grade_ready",
}
FINAL_APPROVAL_REQUIRED_GATES = (
    "structural_ready",
    "validator_contract_ready",
    "semantic_gate_ready",
    "publication_grade_ready",
)
BLOCKING_QUEUE_STATUSES = {
    "material_needs_rework",
    "material_blocked_missing_source",
    "analysis_needs_material_rework",
    "analysis_needs_analysis_rework",
    "analysis_blocked",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def safe_dir_name(paper_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._=-]+", "_", paper_id.strip())
    return cleaned.strip("._") or "paper"


def workflow_dir(root: Path, paper_id: str) -> Path:
    return root / "workflows" / safe_dir_name(paper_id)


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing context file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"expected object in {path}")
    return data


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def packet_root_path(ctx: dict[str, Any]) -> Path | None:
    packet_root = ctx.get("packet_root")
    if not packet_root:
        return None
    path = Path(str(packet_root))
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def final_approval_blockers(ctx: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    open_tickets = list(ctx.get("open_rework_tickets") or [])
    if open_tickets:
        blockers.append(f"open_rework_tickets={','.join(map(str, open_tickets))}")

    gates = ctx.get("gate_summary") or {}
    missing_gates = [key for key in FINAL_APPROVAL_REQUIRED_GATES if gates.get(key) is not True]
    if missing_gates:
        blockers.append(f"gates_not_ready={','.join(missing_gates)}")

    queue_status = ctx.get("queue_status") or {}
    bad_statuses = [f"{key}={value}" for key, value in queue_status.items() if value in BLOCKING_QUEUE_STATUSES]
    if bad_statuses:
        blockers.append(f"blocking_queue_status={','.join(bad_statuses)}")
    return blockers


def guard_final_approval(ctx: dict[str, Any], args: argparse.Namespace) -> None:
    if args.state != "final_approval" or args.status != "completed":
        return
    blockers = final_approval_blockers(ctx)
    if blockers:
        raise SystemExit(
            "final_approval_guard: refusing completed final_approval because "
            + "; ".join(blockers)
        )


def parse_key_value(items: Iterable[str] | None, *, label: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"{label} must be KEY=VALUE, got: {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"{label} has empty key: {item}")
        result[key] = value.strip()
    return result


def parse_artifact_specs(items: Iterable[str] | None) -> list[tuple[str, str]]:
    specs: list[tuple[str, str]] = []
    for item in items or []:
        if "=" in item:
            kind, path = item.split("=", 1)
        elif ":" in item:
            kind, path = item.split(":", 1)
        else:
            raise SystemExit(f"artifact must be KIND=PATH or KIND:PATH, got: {item}")
        kind = kind.strip()
        path = path.strip()
        if not kind or not path:
            raise SystemExit(f"artifact has empty kind/path: {item}")
        specs.append((kind, path))
    return specs


def load_context(root: Path, paper_id: str) -> tuple[Path, dict[str, Any]]:
    wdir = workflow_dir(root, paper_id)
    ctx = read_json(wdir / "workflow_context.json")
    return wdir, ctx


def save_context(wdir: Path, ctx: dict[str, Any]) -> None:
    ctx["updated_at"] = now_iso()
    write_json(wdir / "workflow_context.json", ctx)


def append_event(wdir: Path, ctx: dict[str, Any], event: str, state: str | None = None, payload: dict[str, Any] | None = None) -> None:
    append_jsonl(
        wdir / JSONL_FILES["event"],
        {
            "record_type": "workflow_event",
            "workflow_id": ctx["workflow_id"],
            "paper_id": ctx["paper_id"],
            "state": state or ctx.get("current_state"),
            "event": event,
            "payload": payload or {},
            "created_at": now_iso(),
        },
    )


def add_artifact_record(
    wdir: Path,
    ctx: dict[str, Any],
    artifact_type: str,
    artifact_path: str,
    state: str,
    status: str,
    summary: str = "",
) -> None:
    append_jsonl(
        wdir / JSONL_FILES["artifact"],
        {
            "record_type": "artifact",
            "workflow_id": ctx["workflow_id"],
            "paper_id": ctx["paper_id"],
            "artifact_type": artifact_type,
            "path": artifact_path,
            "produced_by_state": state,
            "status": status,
            "summary": summary,
            "created_at": now_iso(),
        },
    )
    ctx.setdefault("artifacts", {})[artifact_type] = artifact_path
    append_event(wdir, ctx, "artifact_created" if status == "created" else "artifact_updated", state, {"artifact_type": artifact_type, "path": artifact_path, "status": status})


def init_paper(args: argparse.Namespace) -> None:
    root = Path(args.root)
    paper_id = args.paper_id
    wdir = workflow_dir(root, paper_id)
    wdir.mkdir(parents=True, exist_ok=True)
    created_at = now_iso()
    workflow_id = args.workflow_id or f"paper-review-{safe_dir_name(paper_id)}"
    packet_root = args.packet_root or f"paper_packets/{safe_dir_name(paper_id)}"

    ctx = {
        "workflow_id": workflow_id,
        "paper_id": paper_id,
        "paper_dir_name": safe_dir_name(paper_id),
        "packet_root": packet_root,
        "current_state": "select_paper",
        "current_round": "paper_review",
        "queue_status": {
            "material": "material_queued",
            "analysis": "analysis_queued",
        },
        "gate_summary": {
            "structural_ready": False,
            "validator_contract_ready": False,
            "semantic_gate_ready": False,
            "publication_grade_ready": False,
        },
        "open_rework_tickets": [],
        "artifacts": {
            "packet_manifest": f"{packet_root}/packet_manifest.json",
        },
        "provider_policy": {
            "core_provider": "codex-cli",
            "narrative_provider": "claude-cli",
            "final_approval_provider": "codex-cli",
        },
        "metadata": {
            "title": args.title or "",
            "doi": args.doi or "",
        },
        "created_at": created_at,
        "updated_at": created_at,
    }
    write_json(wdir / "workflow_context.json", ctx)
    for filename in JSONL_FILES.values():
        (wdir / filename).touch(exist_ok=True)
    append_event(wdir, ctx, "workflow_initialized", "select_paper", {"packet_root": packet_root})
    append_jsonl(
        wdir / JSONL_FILES["chat"],
        {
            "record_type": "chat_message",
            "workflow_id": workflow_id,
            "paper_id": paper_id,
            "state": "select_paper",
            "role": "agent",
            "message": f"Initialized paper review workflow for {paper_id}; packet_root={packet_root}",
            "created_at": now_iso(),
        },
    )
    print(wdir)


def record_state(args: argparse.Namespace) -> None:
    root = Path(args.root)
    wdir, ctx = load_context(root, args.paper_id)
    started_at = args.started_at or now_iso()
    finished_at = args.finished_at or now_iso()
    artifacts = parse_artifact_specs(args.artifact)
    rework_ids = list(args.rework_ticket or [])

    ctx["current_state"] = args.state
    status_updates = parse_key_value(args.set_status, label="--set-status")
    for key, value in status_updates.items():
        if key == "material":
            if value not in MATERIAL_STATUS:
                raise SystemExit(f"invalid material status: {value}")
            ctx["queue_status"]["material"] = value
        elif key == "analysis":
            if value not in ANALYSIS_STATUS:
                raise SystemExit(f"invalid analysis status: {value}")
            ctx["queue_status"]["analysis"] = value
        else:
            raise SystemExit(f"--set-status supports material=... or analysis=..., got: {key}")

    gate_updates = parse_key_value(args.set_gate, label="--set-gate")
    for key, value in gate_updates.items():
        if key not in GATE_KEYS:
            raise SystemExit(f"invalid gate key: {key}")
        ctx["gate_summary"][key] = value.lower() in {"1", "true", "yes", "pass", "passed"}

    for ticket_id in rework_ids:
        if ticket_id not in ctx.setdefault("open_rework_tickets", []):
            ctx["open_rework_tickets"].append(ticket_id)

    guard_final_approval(ctx, args)

    artifact_refs = [path for _, path in artifacts]
    append_jsonl(
        wdir / JSONL_FILES["state"],
        {
            "record_type": "state_execution",
            "workflow_id": ctx["workflow_id"],
            "paper_id": ctx["paper_id"],
            "state": args.state,
            "role": args.role,
            "provider": args.provider,
            "model": args.model,
            "reasoning_effort": args.reasoning_effort or "",
            "status": args.status,
            "attempt": args.attempt,
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_ms": args.duration_ms,
            "output_summary": args.output_summary or "",
            "artifact_refs": artifact_refs,
            "rework_ticket_ids": rework_ids,
            "created_at": finished_at,
        },
    )

    event = {
        "started": "state_started",
        "completed": "state_completed",
        "failed": "state_failed",
        "blocked": "state_blocked",
        "needs_rework": "rework_opened" if rework_ids else "state_needs_rework",
        "skipped": "state_completed",
    }[args.status]
    append_event(wdir, ctx, event, args.state, {"status": args.status, "summary": args.output_summary or ""})

    for kind, path in artifacts:
        add_artifact_record(wdir, ctx, kind, path, args.state, args.artifact_status, args.output_summary or "")

    if args.chat:
        append_jsonl(
            wdir / JSONL_FILES["chat"],
            {
                "record_type": "chat_message",
                "workflow_id": ctx["workflow_id"],
                "paper_id": ctx["paper_id"],
                "state": args.state,
                "role": "agent",
                "message": args.chat,
                "created_at": now_iso(),
            },
        )
    save_context(wdir, ctx)
    print(wdir / "workflow_context.json")


def add_artifact(args: argparse.Namespace) -> None:
    wdir, ctx = load_context(Path(args.root), args.paper_id)
    add_artifact_record(wdir, ctx, args.kind, args.path, args.state, args.status, args.summary or "")
    save_context(wdir, ctx)
    print(wdir / JSONL_FILES["artifact"])


def add_chat(args: argparse.Namespace) -> None:
    wdir, ctx = load_context(Path(args.root), args.paper_id)
    append_jsonl(
        wdir / JSONL_FILES["chat"],
        {
            "record_type": "chat_message",
            "workflow_id": ctx["workflow_id"],
            "paper_id": ctx["paper_id"],
            "state": args.state or ctx.get("current_state"),
            "role": args.role,
            "message": args.message,
            "created_at": now_iso(),
        },
    )
    print(wdir / JSONL_FILES["chat"])


def add_log(args: argparse.Namespace) -> None:
    wdir, ctx = load_context(Path(args.root), args.paper_id)
    append_jsonl(
        wdir / JSONL_FILES["log"],
        {
            "record_type": "agent_log",
            "workflow_id": ctx["workflow_id"],
            "paper_id": ctx["paper_id"],
            "state": args.state or ctx.get("current_state"),
            "level": args.level,
            "category": args.category,
            "message": args.message,
            "path_refs": args.path_ref or [],
            "created_at": now_iso(),
        },
    )
    print(wdir / JSONL_FILES["log"])


def resolve_rework(args: argparse.Namespace) -> None:
    wdir, ctx = load_context(Path(args.root), args.paper_id)
    resolved_at = now_iso()
    ticket_ids = list(args.ticket_id or [])
    if not ticket_ids:
        raise SystemExit("resolve-rework requires at least one --ticket-id")

    open_tickets = list(ctx.get("open_rework_tickets") or [])
    if args.status in {"resolved", "closed"}:
        for ticket_id in ticket_ids:
            if ticket_id in open_tickets:
                open_tickets.remove(ticket_id)
    ctx["open_rework_tickets"] = open_tickets

    response = {
        "record_type": "rework_response",
        "workflow_id": ctx["workflow_id"],
        "paper_id": ctx["paper_id"],
        "ticket_ids": ticket_ids,
        "status": args.status,
        "resolved_by": args.resolved_by,
        "state": args.state,
        "message": args.message or "",
        "artifact_refs": args.artifact_ref or [],
        "created_at": resolved_at,
    }
    packet_root = packet_root_path(ctx)
    if packet_root:
        append_jsonl(packet_root / "rework" / "rework_responses.jsonl", response)

    append_event(wdir, ctx, "rework_resolved" if args.status in {"resolved", "closed"} else "rework_response_recorded", args.state, response)
    append_jsonl(
        wdir / JSONL_FILES["chat"],
        {
            "record_type": "chat_message",
            "workflow_id": ctx["workflow_id"],
            "paper_id": ctx["paper_id"],
            "state": args.state,
            "role": args.resolved_by,
            "message": args.message or f"Rework response recorded for {', '.join(ticket_ids)}: {args.status}",
            "created_at": resolved_at,
        },
    )
    save_context(wdir, ctx)
    print(json.dumps({"ok": True, "workflow_dir": str(wdir), "open_rework_tickets": ctx["open_rework_tickets"]}, ensure_ascii=False, indent=2))


def validate_jsonl(path: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    count = 0
    if not path.exists():
        return 0, [f"missing {path}"]
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{lineno}: invalid JSONL: {exc}")
            continue
        if not isinstance(obj, dict):
            errors.append(f"{path}:{lineno}: expected object")
            continue
        if "record_type" not in obj:
            errors.append(f"{path}:{lineno}: missing record_type")
        if "created_at" not in obj:
            errors.append(f"{path}:{lineno}: missing created_at")
        count += 1
    return count, errors


def validate(args: argparse.Namespace) -> None:
    root = Path(args.root)
    wdir, ctx = load_context(root, args.paper_id)
    errors: list[str] = []
    for key in ["workflow_id", "paper_id", "packet_root", "current_state", "queue_status", "gate_summary", "open_rework_tickets", "artifacts"]:
        if key not in ctx:
            errors.append(f"workflow_context.json missing {key}")
    if ctx.get("paper_id") != args.paper_id:
        errors.append(f"workflow_context paper_id mismatch: {ctx.get('paper_id')} != {args.paper_id}")
    if not isinstance(ctx.get("queue_status"), dict):
        errors.append("queue_status must be object")
    if not isinstance(ctx.get("gate_summary"), dict):
        errors.append("gate_summary must be object")

    counts: dict[str, int] = {}
    for name, filename in JSONL_FILES.items():
        count, file_errors = validate_jsonl(wdir / filename)
        counts[name] = count
        errors.extend(file_errors)

    if args.strict_paths:
        base = Path.cwd()
        for kind, path_text in ctx.get("artifacts", {}).items():
            path = Path(path_text)
            if not path.is_absolute():
                path = base / path
            if not path.exists():
                errors.append(f"artifact path missing for {kind}: {path_text}")

    if errors:
        print(json.dumps({"ok": False, "workflow_dir": str(wdir), "counts": counts, "errors": errors}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(json.dumps({"ok": True, "workflow_dir": str(wdir), "counts": counts}, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local Miaobi-style message bus for Batch 4 paper review")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="message bus root, default .miaobi-paper-review")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init-paper", help="initialize workflow files for one paper")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--packet-root")
    p.add_argument("--workflow-id")
    p.add_argument("--title")
    p.add_argument("--doi")
    p.set_defaults(func=init_paper)

    p = sub.add_parser("record-state", help="record a state execution and update context")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--state", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--provider", default="codex-cli")
    p.add_argument("--model", default="gpt-5.5")
    p.add_argument("--reasoning-effort", default="xhigh")
    p.add_argument("--status", choices=["started", "completed", "failed", "blocked", "needs_rework", "skipped"], required=True)
    p.add_argument("--attempt", type=int, default=1)
    p.add_argument("--started-at")
    p.add_argument("--finished-at")
    p.add_argument("--duration-ms", type=int, default=0)
    p.add_argument("--output-summary")
    p.add_argument("--artifact", action="append", help="KIND=PATH; may repeat")
    p.add_argument("--artifact-status", default="updated", choices=["created", "updated", "present", "missing", "passed", "failed", "accepted", "blocked"])
    p.add_argument("--rework-ticket", action="append")
    p.add_argument("--set-status", action="append", help="material=<status> or analysis=<status>")
    p.add_argument("--set-gate", action="append", help="gate_name=true|false")
    p.add_argument("--chat")
    p.set_defaults(func=record_state)

    p = sub.add_parser("add-artifact", help="append an artifact record")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--path", required=True)
    p.add_argument("--state", required=True)
    p.add_argument("--status", default="present", choices=["created", "updated", "present", "missing", "passed", "failed", "accepted", "blocked"])
    p.add_argument("--summary")
    p.set_defaults(func=add_artifact)

    p = sub.add_parser("add-chat", help="append a front-end chat message")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--state")
    p.add_argument("--role", default="agent", choices=["system", "agent", "user", "reviewer"])
    p.add_argument("--message", required=True)
    p.set_defaults(func=add_chat)

    p = sub.add_parser("add-log", help="append a debug/tool log message")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--state")
    p.add_argument("--level", default="info", choices=["debug", "info", "warning", "error"])
    p.add_argument("--category", default="runtime")
    p.add_argument("--message", required=True)
    p.add_argument("--path-ref", action="append")
    p.set_defaults(func=add_log)

    p = sub.add_parser("resolve-rework", help="record a rework response and remove resolved tickets from workflow context")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--ticket-id", action="append", required=True)
    p.add_argument("--status", default="resolved", choices=["resolved", "closed", "retry_requested", "acknowledged"])
    p.add_argument("--state", default="rework_queue")
    p.add_argument("--resolved-by", default="reviewer", choices=["system", "agent", "user", "reviewer"])
    p.add_argument("--message")
    p.add_argument("--artifact-ref", action="append")
    p.set_defaults(func=resolve_rework)

    p = sub.add_parser("validate", help="validate local message bus files")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--strict-paths", action="store_true")
    p.set_defaults(func=validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
