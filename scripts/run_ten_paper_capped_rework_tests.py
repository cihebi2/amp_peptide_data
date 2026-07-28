#!/usr/bin/env python3
"""Run 10 real-material paper workflows with a capped rework loop.

The initial workflow opens the first rework decision when publication-grade
gates fail. Each retry re-runs the strict gates against the same real artifacts,
records a retry request, and refuses final approval again unless all quality
conditions are met. The loop stops at --max-rework decisions and leaves
uncontrolled papers blocked instead of force-accepted.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_ten_paper_message_tests import candidate_papers


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
            rows.append({"raw": line})
    return rows


def run(cmd: list[str], cwd: Path, *, allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode and not allow_fail:
        raise SystemExit(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc


def bridge(repo: Path, *args: str, allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    return run([sys.executable, str(repo / "scripts" / "miaobi_message_bridge.py"), *args], repo, allow_fail=allow_fail)


def run_gate_retry(repo: Path, paper_id: str, manifest: Path, decision_no: int) -> dict[str, Any]:
    reports = repo / "reports"
    semantic_report = reports / f"{paper_id}.rework_{decision_no}.semantic_gate.json"
    publication_report = reports / f"{paper_id}.rework_{decision_no}.publication_quality.json"

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
    semantic = json.loads(semantic_report.read_text(encoding="utf-8"))
    publication = read_json(publication_report)
    passed = (
        int(semantic.get("publication_grade_pass_count") or 0) == int(semantic.get("paper_count") or 0) == 1
        and publication.get("publication_grade_pass") is True
    )
    return {
        "decision_no": decision_no,
        "semantic_report": str(semantic_report),
        "publication_report": str(publication_report),
        "semantic_returncode": semantic_proc.returncode,
        "publication_returncode": publication_proc.returncode,
        "semantic_pass_count": int(semantic.get("publication_grade_pass_count") or 0),
        "semantic_fail_count": int(semantic.get("publication_grade_fail_count") or 0),
        "publication_quality_pass": publication.get("publication_grade_pass"),
        "semantic_issue_codes": sorted({
            str(issue.get("code"))
            for result in semantic.get("results") or []
            if isinstance(result, dict)
            for issue in result.get("issues") or []
            if isinstance(issue, dict) and issue.get("code")
        }),
        "publication_risk_counts": publication.get("risk_counts") or {},
        "passed": passed,
    }


def build_rework_context(repo: Path, paper_id: str) -> dict[str, Any]:
    proc = run(
        [
            sys.executable,
            "scripts/build_rework_context_packet.py",
            "--paper-id",
            paper_id,
        ],
        repo,
        allow_fail=True,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {}
    return {
        "returncode": proc.returncode,
        "context": payload.get("context"),
        "prompt": payload.get("prompt"),
        "owner_workers": payload.get("owner_workers") or [],
        "failure_reason_count": payload.get("failure_reason_count"),
        "stdout_tail": proc.stdout[-1000:],
        "stderr_tail": proc.stderr[-1000:],
    }


def is_accepted(report: dict[str, Any]) -> bool:
    gates = report.get("gate_results") or {}
    return (
        report.get("final_approval_status") == "completed"
        and int(report.get("open_rework_ticket_count") or 0) == 0
        and int(gates.get("semantic_publication_grade_pass_count") or 0) > 0
        and gates.get("publication_quality_pass") is True
    )


def workflow_counts(workflow_dir: Path, packet_root: Path) -> dict[str, int]:
    return {
        "state_executions": len(read_jsonl(workflow_dir / "state_executions.jsonl")),
        "chat_messages": len(read_jsonl(workflow_dir / "chat_messages.jsonl")),
        "events": len(read_jsonl(workflow_dir / "events.jsonl")),
        "artifacts": len(read_jsonl(workflow_dir / "artifacts.jsonl")),
        "rework_requests": len(read_jsonl(packet_root / "rework" / "rework_requests.jsonl")),
        "rework_responses": len(read_jsonl(packet_root / "rework" / "rework_responses.jsonl")),
    }


def run_one_with_capped_rework(repo: Path, paper_id: str, max_rework: int, *, reset: bool) -> dict[str, Any]:
    cmd = [sys.executable, "scripts/run_one_paper_complete_message_test.py", "--paper-id", paper_id]
    if reset:
        cmd.append("--reset")
    proc = run(cmd, repo, allow_fail=True)
    report_path = repo / "reports" / f"{paper_id}.complete_message_test_report.json"
    if proc.returncode != 0:
        return {
            "paper_id": paper_id,
            "terminal_status": "workflow_failed_before_rework",
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
        }

    initial = read_json(report_path)
    manifest = Path(initial["manifest"])
    packet_root = Path(initial["packet_root"])
    workflow_dir = Path(initial["workflow_dir"])
    decisions = [
        {
            "decision_no": 1,
            "source": "initial_workflow",
            "semantic_pass_count": (initial.get("gate_results") or {}).get("semantic_publication_grade_pass_count"),
            "semantic_fail_count": (initial.get("gate_results") or {}).get("semantic_publication_grade_fail_count"),
            "publication_quality_pass": (initial.get("gate_results") or {}).get("publication_quality_pass"),
            "final_approval_status": initial.get("final_approval_status"),
            "terminal_status": initial.get("terminal_status"),
            "passed": is_accepted(initial),
        }
    ]

    if decisions[0]["passed"]:
        terminal = "accepted_after_initial_gate"
    else:
        terminal = "awaiting_targeted_rework"

    for decision_no in range(2, max_rework + 1):
        if terminal.startswith("accepted"):
            break

        bridge(
            repo,
            "resolve-rework",
            "--paper-id",
            paper_id,
            "--ticket-id",
            "rwk-complete-test-0001",
            "--status",
            "retry_requested",
            "--state",
            f"rework_attempt_{decision_no}",
            "--resolved-by",
            "agent",
            "--message",
            f"Rework retry {decision_no}/{max_rework}: rerun quality gates; keep ticket open unless all gates pass.",
        )
        gate = run_gate_retry(repo, paper_id, manifest, decision_no)
        if gate["passed"]:
            bridge(
                repo,
                "resolve-rework",
                "--paper-id",
                paper_id,
                "--ticket-id",
                "rwk-complete-test-0001",
                "--status",
                "resolved",
                "--state",
                f"rework_attempt_{decision_no}",
                "--resolved-by",
                "agent",
                "--message",
                f"Rework retry {decision_no}/{max_rework}: gates passed; closing ticket.",
                "--artifact-ref",
                gate["semantic_report"],
                "--artifact-ref",
                gate["publication_report"],
            )
            bridge(
                repo,
                "record-state",
                "--paper-id",
                paper_id,
                "--state",
                f"final_approval_retry_{decision_no}",
                "--role",
                "quality_gate",
                "--status",
                "completed",
                "--set-status",
                "analysis=analysis_source_reviewed_accepted",
                "--set-gate",
                "semantic_gate_ready=true",
                "--set-gate",
                "publication_grade_ready=true",
                "--artifact",
                f"semantic_gate={gate['semantic_report']}",
                "--artifact",
                f"publication_quality={gate['publication_report']}",
                "--output-summary",
                f"Final approval completed after rework retry {decision_no}.",
                "--chat",
                f"第 {decision_no} 次打回后通过所有 gate，关闭 rework。",
            )
            terminal = "accepted_after_rework"
        else:
            context_packet = build_rework_context(repo, paper_id)
            artifact_args: list[str] = []
            if context_packet.get("context"):
                artifact_args += ["--artifact", f"rework_context_packet={context_packet['context']}"]
            if context_packet.get("prompt"):
                artifact_args += ["--artifact", f"codex_re_review_prompt={context_packet['prompt']}"]
            bridge(
                repo,
                "record-state",
                "--paper-id",
                paper_id,
                "--state",
                f"rework_attempt_{decision_no}",
                "--role",
                "quality_gate",
                "--status",
                "needs_rework",
                "--rework-ticket",
                "rwk-complete-test-0001",
                "--set-status",
                "analysis=analysis_needs_analysis_rework",
                "--set-gate",
                "semantic_gate_ready=false",
                "--set-gate",
                "publication_grade_ready=false",
                "--artifact",
                f"semantic_gate={gate['semantic_report']}",
                "--artifact",
                f"publication_quality={gate['publication_report']}",
                *artifact_args,
                "--output-summary",
                f"Rework decision {decision_no}/{max_rework}: gates still fail; final approval refused; context packet prepared for owner workers={context_packet.get('owner_workers')}; retries must use rework context without restarting the initial queue.",
                "--chat",
                f"第 {decision_no}/{max_rework} 次打回：gate 仍未通过，已生成上下文包给前序 worker/新 Codex CLI；不重启初始队列。",
            )
            state = "capped_rework_limit" if decision_no == max_rework else f"rework_queue_retry_{decision_no}"
            status = "blocked" if decision_no == max_rework else "blocked"
            summary = (
                f"Reached max rework decisions ({max_rework}); paper is uncontrolled and blocked."
                if decision_no == max_rework
                else f"Paper returned to rework queue after decision {decision_no}/{max_rework}."
            )
            bridge(
                repo,
                "record-state",
                "--paper-id",
                paper_id,
                "--state",
                state,
                "--role",
                "quality_gate",
                "--status",
                status,
                "--set-status",
                "analysis=analysis_blocked" if decision_no == max_rework else "analysis=analysis_needs_analysis_rework",
                "--set-gate",
                "semantic_gate_ready=false",
                "--set-gate",
                "publication_grade_ready=false",
                "--output-summary",
                summary,
                "--chat",
                summary,
            )
            terminal = "capped_rework_limit_reached" if decision_no == max_rework else "awaiting_targeted_rework"

        decision_row = {**gate, "source": "retry_gate_loop", "terminal_after_decision": terminal}
        if not gate["passed"]:
            decision_row["rework_context_packet"] = context_packet
        decisions.append(decision_row)

    context = read_json(workflow_dir / "workflow_context.json")
    final = {
        "paper_id": paper_id,
        "title": initial.get("title"),
        "doi": initial.get("doi"),
        "pmcid": initial.get("pmcid"),
        "workflow_dir": str(workflow_dir),
        "packet_root": str(packet_root),
        "max_rework_decisions": max_rework,
        "rework_decision_count": len(decisions),
        "terminal_status": terminal,
        "accepted": terminal.startswith("accepted"),
        "uncontrolled": terminal == "capped_rework_limit_reached",
        "current_state": context.get("current_state"),
        "queue_status": context.get("queue_status"),
        "gate_summary": context.get("gate_summary"),
        "open_rework_ticket_count": len(context.get("open_rework_tickets") or []),
        "open_rework_tickets": context.get("open_rework_tickets") or [],
        "decisions": decisions,
        "message_counts": workflow_counts(workflow_dir, packet_root),
        "material": initial.get("material") or {},
        "analysis": initial.get("analysis") or {},
    }
    write_json(repo / "reports" / f"{paper_id}.capped_rework_test_report.json", final)
    return final


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--max-rework", type=int, default=5)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    if args.max_rework < 1:
        raise SystemExit("--max-rework must be >= 1")

    repo = Path.cwd()
    paper_ids = candidate_papers(args.limit)
    if len(paper_ids) < args.limit:
        raise SystemExit(f"only found {len(paper_ids)} eligible papers")

    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for idx, paper_id in enumerate(paper_ids, start=1):
        print(f"[{idx}/{len(paper_ids)}] capped rework test {paper_id}", flush=True)
        result = run_one_with_capped_rework(repo, paper_id, args.max_rework, reset=args.reset)
        if result.get("terminal_status") == "workflow_failed_before_rework":
            failures.append(result)
        else:
            results.append(result)

    summary = {
        "ok": not failures,
        "generated_at": now_iso(),
        "test_type": "ten_paper_capped_rework_message_transfer_batch",
        "completion_claim": "capped_rework_workflow_exercised_not_publication_grade_acceptance",
        "requested_limit": args.limit,
        "max_rework_decisions": args.max_rework,
        "paper_count": len(results),
        "failure_count": len(failures),
        "paper_ids": paper_ids,
        "terminal_status_counts": {},
        "quality_control": {
            "force_acceptance": False,
            "acceptance_requires": [
                "open_rework_ticket_count=0",
                "semantic_gate pass",
                "publication_quality_gate pass",
                "final_approval completed",
            ],
            "uncontrolled_policy": f"keep reworking until {args.max_rework} decisions, then mark blocked/capped",
            "queue_start_policy": "start once; retries consume rework_context only",
            "best_effort_policy": "owner workers must recover local source evidence when possible; if unrecoverable, record unrecoverable_material_gaps and advance",
        },
        "rework_counts": {
            "total_rework_decisions": 0,
            "open_rework_tickets": 0,
            "accepted_papers": 0,
            "uncontrolled_papers": 0,
        },
        "total_material": {
            "sections": 0,
            "tables": 0,
            "figures": 0,
            "archive_members": 0,
            "supplementary_assets": 0,
            "supplementary_tables": 0,
            "locators": 0,
        },
        "total_analysis": {
            "activity_records": 0,
            "mechanism_claims": 0,
        },
        "uncontrolled_paper_ids": [],
        "results": results,
        "failures": failures,
    }
    for result in results:
        status = result.get("terminal_status", "unknown")
        summary["terminal_status_counts"][status] = summary["terminal_status_counts"].get(status, 0) + 1
        summary["rework_counts"]["total_rework_decisions"] += int(result.get("rework_decision_count") or 0)
        summary["rework_counts"]["open_rework_tickets"] += int(result.get("open_rework_ticket_count") or 0)
        if result.get("accepted"):
            summary["rework_counts"]["accepted_papers"] += 1
        if result.get("uncontrolled"):
            summary["rework_counts"]["uncontrolled_papers"] += 1
            summary["uncontrolled_paper_ids"].append(result["paper_id"])
        for key in summary["total_material"]:
            summary["total_material"][key] += int((result.get("material") or {}).get(key) or 0)
        for key in summary["total_analysis"]:
            summary["total_analysis"][key] += int((result.get("analysis") or {}).get(key) or 0)

    out = repo / "reports" / f"ten_paper_capped_rework_test_{now_iso().replace(':', '').replace('-', '')}.json"
    write_json(out, summary)
    latest = repo / "reports" / "ten_paper_capped_rework_test_latest.json"
    write_json(latest, summary)
    print(
        json.dumps(
            {
                "ok": not failures,
                "summary_path": str(out),
                "latest_path": str(latest),
                "paper_count": len(results),
                "failure_count": len(failures),
                "terminal_status_counts": summary["terminal_status_counts"],
                "rework_counts": summary["rework_counts"],
                "uncontrolled_paper_ids": summary["uncontrolled_paper_ids"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
