#!/usr/bin/env python3
"""Fail-closed executor for the frozen 200-paper strict review campaign.

Each paper is deliberately sequential internally. Distinct papers may run in
parallel under separate paper locks. Each untouched paper receives six
sequential canonical workers, a fresh mechanical acceptance run, a separate
structured leader semantic audit, and a separate independent verifier. A paper
is recorded terminal only when every layer passes. Audit failures are converted
into targeted owner-worker tickets; they are never promoted by a green generic
gate.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from pipeline_v2.deepmine.grok_readonly_review import (
        GrokStructuredReviewError,
        run_grok_structured_review,
    )
except ModuleNotFoundError:  # Direct script execution from the deepmine directory.
    from grok_readonly_review import (
        GrokStructuredReviewError,
        run_grok_structured_review,
    )


ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot"
PILOT_CLI = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot.py"
LEDGER_CLI = ROOT / "pipeline_v2/deepmine/remaining_200_strict_controller.py"
STATE = PILOT / "manifests/remaining_200_strict_review_state_20260726.json"
CAMPAIGN_DIR = PILOT / "reports/remaining_200_campaign"
LEADER_SCHEMA = PILOT / "contracts/leader_semantic_audit.schema.json"
VERIFIER_SCHEMA = PILOT / "contracts/independent_paper_verifier.schema.json"
CANONICAL_WORKERS = [f"worker-{number}" for number in range(1, 7)]
OWNER_WORKERS = CANONICAL_WORKERS[:-1]
REQUIRED_LEADER_CHECKS = {
    "paper_identity_and_entity_linkage",
    "body_table_activity_coverage",
    "toxicity_selectivity_coverage",
    "supplementary_surface_exhaustion",
    "database_record_verification",
    "mechanism_ontology_boundaries",
    "source_conflicts_and_cautions",
    "provenance_locator_and_normalization_integrity",
    "final_mirror_and_count_consistency",
    "recursive_authority_and_release_boundary",
}


class StructuredReviewRunError(RuntimeError):
    """A recorded structured-review failure with provider runtime evidence."""

    def __init__(self, message: str, runtime: dict[str, Any]):
        super().__init__(message)
        self.runtime = runtime


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


@contextmanager
def paper_campaign_lock(paper_id: str):
    """Prevent duplicate executors for one paper without blocking other papers."""
    safe_id = re.sub(r"[^0-9A-Za-z_.-]+", "_", paper_id)
    lock_path = CAMPAIGN_DIR / "paper_locks" / f"{safe_id}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(
                f"another strict campaign executor owns paper lock: {paper_id}"
            ) from error
        handle.seek(0)
        handle.truncate()
        handle.write(
            json.dumps(
                {"pid": os.getpid(), "paper_id": paper_id, "acquired_at": utc_now()}
            )
            + "\n"
        )
        handle.flush()
        yield


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        value
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for value in [json.loads(line)]
        if isinstance(value, dict)
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def run_command(
    command: list[str], log_dir: Path, label: str, timeout: int
) -> dict[str, Any]:
    started_at = utc_now()
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
    except subprocess.TimeoutExpired as error:
        returncode = 124
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        timed_out = True
    stdout_path = log_dir / f"{label}.stdout.txt"
    stderr_path = log_dir / f"{label}.stderr.txt"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    return {
        "label": label,
        "command": command,
        "started_at": started_at,
        "finished_at": utc_now(),
        "returncode": returncode,
        "timed_out": timed_out,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }


def evidence_paths_exist(paths: list[Any]) -> bool:
    return bool(paths) and all(
        (ROOT / str(path)).exists() if not Path(str(path)).is_absolute() else Path(str(path)).exists()
        for path in paths
    )


def paper_input_fingerprint(paper_id: str) -> str:
    roots = [
        PILOT / "papers" / paper_id / "source",
        PILOT / "papers" / paper_id / "work",
        PILOT / "papers" / paper_id / "final",
        PILOT / "packets" / paper_id,
        PILOT / "worker_logs" / paper_id,
        PILOT / "reports" / f"{paper_id}_strict_acceptance_audit_latest.json",
    ]
    digest = hashlib.sha256()
    for root in roots:
        paths = [root] if root.is_file() else sorted(root.rglob("*")) if root.exists() else []
        for path in paths:
            if not path.is_file():
                continue
            digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def validate_leader_payload(paper_id: str, payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if payload.get("paper_id") != paper_id:
        failures.append("paper_id_mismatch")
    checks = payload.get("field_checks")
    checks = checks if isinstance(checks, list) else []
    check_ids = {
        str(check.get("check_id"))
        for check in checks
        if isinstance(check, dict) and check.get("check_id")
    }
    missing = sorted(REQUIRED_LEADER_CHECKS - check_ids)
    if missing:
        failures.append(f"missing_required_field_checks:{','.join(missing)}")
    for check in checks:
        if not isinstance(check, dict) or not evidence_paths_exist(
            check.get("evidence_paths") or []
        ):
            failures.append("field_check_has_missing_evidence_path")
            break
    findings = payload.get("blocking_findings")
    findings = findings if isinstance(findings, list) else []
    finding_ids = [
        str(finding.get("finding_id") or "")
        for finding in findings
        if isinstance(finding, dict)
    ]
    if any(not value for value in finding_ids) or len(finding_ids) != len(
        set(finding_ids)
    ):
        failures.append("blocking_finding_ids_invalid_or_duplicate")
    for finding in findings:
        if not isinstance(finding, dict):
            failures.append("blocking_finding_not_object")
            continue
        if finding.get("owner_worker") not in OWNER_WORKERS:
            failures.append("blocking_finding_owner_invalid")
        if not evidence_paths_exist(finding.get("evidence_paths") or []):
            failures.append("blocking_finding_has_missing_evidence_path")
        if not finding.get("source_locators"):
            failures.append("blocking_finding_has_no_source_locator")
    required_true = [
        "independently_reviewed_primary_source",
        "reviewed_every_current_final_record",
    ]
    if not all(payload.get(key) is True for key in required_true):
        failures.append("leader_source_or_final_review_not_completed")
    pass_required_true = required_true + [
        "recursive_authority_boundary_false",
        "fallback_release_boundary_preserved",
    ]
    pass_semantics = (
        payload.get("verdict") == "PASS"
        and payload.get("publication_grade_ready") is True
        and not findings
        and all(payload.get(key) is True for key in pass_required_true)
        and not any(check.get("status") == "FAIL" for check in checks)
    )
    fail_semantics = (
        payload.get("verdict") == "FAIL"
        and payload.get("publication_grade_ready") is False
        and bool(findings)
        and any(check.get("status") == "FAIL" for check in checks)
    )
    if not (pass_semantics or fail_semantics):
        failures.append("leader_verdict_semantics_invalid")
    return sorted(set(failures))


def validate_verifier_payload(paper_id: str, payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if payload.get("paper_id") != paper_id:
        failures.append("paper_id_mismatch")
    checks = payload.get("checks")
    checks = checks if isinstance(checks, list) else []
    for check in checks:
        if not isinstance(check, dict) or not evidence_paths_exist(
            check.get("evidence_paths") or []
        ):
            failures.append("verifier_check_has_missing_evidence_path")
            break
    required_true = [
        "independently_reviewed_primary_source",
        "independently_reviewed_current_finals",
        "leader_audit_is_supported",
        "six_worker_runtime_is_valid",
        "worker6_is_fresh",
        "zero_open_tickets",
        "mechanical_acceptance_passes",
        "recursive_authority_boundary_false",
        "fallback_release_boundary_preserved",
    ]
    blocking = payload.get("blocking_reasons")
    blocking = blocking if isinstance(blocking, list) else []
    pass_semantics = (
        payload.get("verdict") == "PASS"
        and not blocking
        and all(payload.get(key) is True for key in required_true)
        and not any(check.get("status") == "FAIL" for check in checks)
    )
    fail_semantics = payload.get("verdict") == "FAIL" and bool(blocking)
    if not (pass_semantics or fail_semantics):
        failures.append("verifier_verdict_semantics_invalid")
    return sorted(set(failures))


def leader_prompt(paper_id: str) -> str:
    relative = PILOT.relative_to(ROOT)
    checks = "\n".join(f"- `{value}`" for value in sorted(REQUIRED_LEADER_CHECKS))
    return f"""You are the independent leader field-level scientific auditor for one AMP paper.

Paper: {paper_id}
Workspace: {ROOT}

Read and obey:
- `.codex/skills/amp-three-layer-curation/SKILL.md`
- `.codex/skills/paper-batch-orchestrator/SKILL.md`
- all publication-grade and two-queue contracts referenced by those skills.

This is a read-only audit. Do not edit, repair, or create project files. First
prove that the listed paths are readable. Infrastructure/access failures are
not scientific worker findings and must not be assigned to worker-1..5.
Independently inspect:
- `{relative}/papers/{paper_id}/source/` (the primary XML/PDF and every staged supplement);
- `{relative}/packets/{paper_id}/extracted/`, `database/`, `locators/`, `analysis/`, and `rework/`;
- `{relative}/papers/{paper_id}/work/`;
- every current JSON record in `{relative}/papers/{paper_id}/final/` and both final mirrors;
- `{relative}/worker_logs/{paper_id}/run_sequence_latest.json`;
- `{relative}/reports/{paper_id}_strict_acceptance_audit_latest.json`.

Do not infer correctness from worker summaries or green gates. Use scripts to enumerate every final record, compare identities, sequences/modifications, endpoints, values/units, target/strain, assay conditions, locators, exact-vs-approximate status, exclusions, toxicity, database-record evidence, mechanism strength, conflicts/cautions, mirror equality, and recursive authority flags against the source surfaces. Fallback rows must remain excluded from RC2/portal/authoritative ingest.
For every object containing both a plain one-letter `sequence` and
`sequence_length`, independently count residues and require exact agreement;
terminal modifications such as amidation are not residues. Reconcile every
hard finding in the current strict acceptance artifact rather than reporting
PASS around it. Also require any final review-report
`open_rework_ticket_count` to equal the live packet ticket state.

Your `field_checks` must contain these exact check_ids:
{checks}

For either a scientifically valid PASS or FAIL,
`independently_reviewed_primary_source` and
`reviewed_every_current_final_record` must be true. PASS is allowed only if
there are zero blocking findings, every current final record was reviewed, the
primary source and all staged supplements were independently inspected,
mechanical/runtime/ticket evidence is current, mirrors/counts agree, recursive
authority is false, and publication-grade source coverage is exhausted. If any
material value/field/surface is omitted, placeholder-like, unsupported,
conflated, or scientifically not source-reviewable, return FAIL and one
concrete blocking finding per repair lane. Each finding must cite existing
evidence paths, concrete primary-source locators (not "not inspected" text),
exactly one owner worker-1..worker-5, required repair actions, and
executable/field-level acceptance checks.

Every `evidence_paths` entry must be an exact existing file or directory path
relative to the workspace. Before returning, verify every one with
`Path(path).exists()`. Never append a line number, JSON pointer, page number,
colon suffix, URI fragment, wildcard, or glob to an evidence path. Put line
numbers, JSON locations, pages, table/figure labels, and source coordinates
only in the prose summary/reason or in `source_locators`.

Return only the JSON object required by the supplied schema.
"""


def verifier_prompt(paper_id: str, leader_audit: Path) -> str:
    relative = PILOT.relative_to(ROOT)
    return f"""You are the final independent verifier for one AMP paper.

Paper: {paper_id}
Leader audit: `{leader_audit.relative_to(ROOT)}` (SHA-256 {sha256(leader_audit)})

This is read-only. Do not edit project files. Read the AMP curation and batch-orchestrator skills, then independently inspect the primary XML/PDF, every staged supplement, packet extracted/database/locator/rework surfaces, all current work and final artifacts, both mirrors, six-worker run sequence, current single-paper acceptance audit, and the leader audit. Do not accept the leader conclusion on authority: reproduce enough source and field checks to decide whether it is supported.

Review locations:
- `{relative}/papers/{paper_id}/source/`
- `{relative}/papers/{paper_id}/work/`
- `{relative}/papers/{paper_id}/final/`
- `{relative}/packets/{paper_id}/`
- `{relative}/worker_logs/{paper_id}/run_sequence_latest.json`
- `{relative}/reports/{paper_id}_strict_acceptance_audit_latest.json`

PASS requires: valid six unique sequential canonical gpt-5.5/xhigh sessions; worker-6 later than every latest upstream worker; current acceptance pass; zero open tickets/rework targets; every current final record source-supported with correct identity/value/unit/endpoint/target/locator/evidence-strength semantics; mirrors/counts consistent; source conflicts/cautions preserved; recursive authority=false; and fallback release boundaries preserved. Otherwise return FAIL with explicit blocking reasons. Include at least nine independent checks with existing evidence paths.

Return only the JSON object required by the supplied schema.
"""


def run_structured_codex(
    paper_id: str,
    role: str,
    schema: Path,
    prompt: str,
    timeout: int,
) -> tuple[Path, dict[str, Any]]:
    stamp = run_stamp()
    paper_dir = CAMPAIGN_DIR / paper_id
    paper_dir.mkdir(parents=True, exist_ok=True)
    last_message = paper_dir / f"{stamp}.{role}.json"
    stdout_path = paper_dir / f"{stamp}.{role}.stdout.log"
    stderr_path = paper_dir / f"{stamp}.{role}.stderr.log"
    command = [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "-m",
        "gpt-5.5",
        "-c",
        'model_reasoning_effort="xhigh"',
        "--dangerously-bypass-approvals-and-sandbox",
        "--output-schema",
        str(schema),
        "-C",
        str(ROOT),
        "-o",
        str(last_message),
        "-",
    ]
    started_at = utc_now()
    input_fingerprint_before = paper_input_fingerprint(paper_id)
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        timed_out = False
    except subprocess.TimeoutExpired as error:
        returncode = 124
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        timed_out = True
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    session_match = re.search(r"session id:\s*([0-9a-f-]+)", stderr, re.I)
    input_fingerprint_after = paper_input_fingerprint(paper_id)
    runtime = {
        "paper_id": paper_id,
        "role": role,
        "command": command,
        "started_at": started_at,
        "finished_at": utc_now(),
        "returncode": returncode,
        "timed_out": timed_out,
        "codex_session_id": session_match.group(1) if session_match else None,
        "codex_model": "gpt-5.5",
        "codex_reasoning_effort": "xhigh",
        "review_provider": "openai_codex_cli",
        "review_model": "gpt-5.5",
        "review_reasoning_mode": "xhigh",
        "review_session_id": (
            f"codex:{session_match.group(1)}" if session_match else None
        ),
        "schema_path": str(schema),
        "schema_sha256": sha256(schema),
        "paper_input_fingerprint_before": input_fingerprint_before,
        "paper_input_fingerprint_after": input_fingerprint_after,
        "paper_inputs_unchanged_during_review": (
            input_fingerprint_before == input_fingerprint_after
        ),
        "last_message_path": str(last_message),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }
    atomic_write_json(paper_dir / f"{stamp}.{role}.runtime.json", runtime)
    if (
        returncode != 0
        or not last_message.exists()
        or not runtime["codex_session_id"]
        or not runtime["paper_inputs_unchanged_during_review"]
    ):
        raise StructuredReviewRunError(
            f"{role} Codex run failed: {runtime}", runtime
        )
    payload = read_json(last_message)
    semantic_failures = (
        validate_leader_payload(paper_id, payload)
        if role == "leader_semantic_auditor"
        else validate_verifier_payload(paper_id, payload)
    )
    runtime["local_semantic_validation_failures"] = semantic_failures
    atomic_write_json(paper_dir / f"{stamp}.{role}.runtime.json", runtime)
    if semantic_failures:
        raise StructuredReviewRunError(
            f"{role} structured payload failed local checks: {semantic_failures}",
            runtime,
        )
    latest = paper_dir / f"{role}_latest.json"
    atomic_write_json(latest, payload)
    return last_message, runtime


def codex_biology_safety_access_rejected(runtime: dict[str, Any]) -> bool:
    """Classify only the known biology-content access rejection."""

    stderr_path = Path(str(runtime.get("stderr_path") or ""))
    if not stderr_path.is_file():
        return False
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    return (
        "Invalid prompt: we've limited access to this content for safety reasons"
        in stderr
        and (
            "future-ai-capabilities-in-biology" in stderr
            or "biology" in stderr.casefold()
        )
    )


def run_structured_review(
    paper_id: str,
    role: str,
    schema: Path,
    prompt: str,
    timeout: int,
    enable_grok_safety_fallback: bool,
) -> tuple[Path, dict[str, Any]]:
    """Prefer Codex and use Grok only for the classified safety false-positive."""

    try:
        return run_structured_codex(paper_id, role, schema, prompt, timeout)
    except StructuredReviewRunError as error:
        if (
            not enable_grok_safety_fallback
            or not codex_biology_safety_access_rejected(error.runtime)
        ):
            raise
        validator = (
            validate_leader_payload
            if role == "leader_semantic_auditor"
            else validate_verifier_payload
        )
        return run_grok_structured_review(
            root=ROOT,
            pilot=PILOT,
            campaign_dir=CAMPAIGN_DIR,
            paper_id=paper_id,
            role=role,
            schema_path=schema,
            prompt=prompt,
            timeout=timeout,
            semantic_validator=validator,
            fallback_reason=(
                "Codex biology-content safety access rejection; benign "
                "read-only literature/data verification delegated to Grok. "
                f"Codex runtime: {error.runtime}"
            ),
        )


def refresh_ledger(log_dir: Path, label: str = "ledger_status") -> dict[str, Any]:
    run = run_command(
        ["python3", str(LEDGER_CLI), "status"], log_dir, label, timeout=900
    )
    if run["returncode"] != 0:
        raise RuntimeError(f"ledger refresh failed: {run}")
    return read_json(Path(run["stdout_path"]))


def state_row(paper_id: str) -> dict[str, Any]:
    state = read_json(STATE)
    rows = [row for row in state.get("papers", []) if row.get("paper_id") == paper_id]
    if len(rows) != 1:
        raise RuntimeError(f"paper is not uniquely present in frozen state: {paper_id}")
    return rows[0]


def unresolved_ticket_owners(paper_id: str) -> list[str]:
    row = state_row(paper_id)
    return list((row.get("tickets") or {}).get("ordered_missing_owner_workers") or [])


def canonical_resume_workers_from_reports(
    reports: list[dict[str, Any]],
) -> list[str]:
    """Return the failed/missing canonical suffix that must be rerun in order."""
    if any(
        not isinstance(report, dict) or not report.get("worker")
        for report in reports
    ):
        return list(CANONICAL_WORKERS)
    report_workers = [str(report["worker"]) for report in reports]
    if report_workers != CANONICAL_WORKERS[: len(report_workers)]:
        return list(CANONICAL_WORKERS)
    by_worker = {
        str(report.get("worker")): report
        for report in reports
        if isinstance(report, dict) and report.get("worker")
    }
    seen_sessions: set[str] = set()
    for index, worker in enumerate(CANONICAL_WORKERS):
        report = by_worker.get(worker) or {}
        command = report.get("command")
        command = command if isinstance(command, list) else []
        session_id = str(report.get("codex_session_id") or "")
        clean = (
            report.get("returncode") == 0
            and bool(session_id)
            and session_id not in seen_sessions
            and report.get("codex_model") == "gpt-5.5"
            and report.get("codex_reasoning_effort") == "xhigh"
            and len(command) >= 2
            and Path(str(command[0])).name == "codex"
            and command[1] == "exec"
        )
        if not clean:
            return CANONICAL_WORKERS[index:]
        seen_sessions.add(session_id)
    return []


def canonical_resume_workers(paper_id: str) -> list[str]:
    sequence = read_json(
        PILOT / "worker_logs" / paper_id / "run_sequence_latest.json"
    )
    reports = sequence.get("reports")
    return canonical_resume_workers_from_reports(
        reports if isinstance(reports, list) else []
    )


def should_run_leader_review(
    acceptance_returncode: int, current_row: dict[str, Any]
) -> bool:
    """Do not spend a full audit on a paper with known unresolved tickets."""
    open_count = int(
        ((current_row.get("tickets") or {}).get("open_ticket_count") or 0)
    )
    return acceptance_returncode == 0 or open_count == 0


def audit_finding_fingerprint(finding: dict[str, Any]) -> str:
    payload = {
        "finding_id": str(
            finding.get("finding_id")
            or finding.get("leader_finding_id")
            or ""
        ),
        "owner_worker": str(finding.get("owner_worker") or ""),
        "reason": str(finding.get("reason") or ""),
        "source_locators": finding.get("source_locators") or [],
        "evidence_paths": finding.get("evidence_paths") or [],
        "required_actions": finding.get("required_actions") or [],
        "acceptance_checks": finding.get("acceptance_checks") or [],
    }
    return hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def new_audit_findings(
    findings: list[dict[str, Any]],
    existing_open_requests: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Filter only exact duplicates of findings that are already open."""
    existing = {
        str(request.get("leader_finding_fingerprint") or "")
        or audit_finding_fingerprint(request)
        for request in existing_open_requests
    }
    return [
        finding
        for finding in findings
        if audit_finding_fingerprint(finding) not in existing
    ]


def stage_audit_tickets(
    paper_id: str, audit_path: Path, payload: dict[str, Any], round_number: int
) -> list[str]:
    packet = PILOT / "packets" / paper_id
    request_path = packet / "rework/rework_requests.jsonl"
    requests = read_jsonl(request_path)
    existing_ids = {
        str(row.get("ticket_id")) for row in requests if row.get("ticket_id")
    }
    open_ids = set(
        str(value)
        for value in (
            (state_row(paper_id).get("tickets") or {}).get(
                "open_ticket_ids"
            )
            or []
        )
    )
    existing_open_requests = [
        request
        for request in requests
        if str(request.get("ticket_id") or "") in open_ids
    ]
    staged: list[str] = []
    queue_by_worker = {
        "worker-1": "paper",
        "worker-2": "analysis",
        "worker-3": "material",
        "worker-4": "database",
        "worker-5": "mechanism",
    }
    for finding in new_audit_findings(
        payload["blocking_findings"], existing_open_requests
    ):
        finding_fingerprint = audit_finding_fingerprint(finding)
        slug = re.sub(r"[^0-9A-Za-z]+", "-", str(finding["finding_id"])).strip("-")[:60]
        ticket_id = f"rwk-{paper_id}-campaign-r{round_number:02d}-{slug}"
        suffix = 2
        while ticket_id in existing_ids:
            ticket_id = (
                f"rwk-{paper_id}-campaign-r{round_number:02d}-{slug}-{suffix}"
            )
            suffix += 1
        owner = str(finding["owner_worker"])
        ticket = {
            "ticket_id": ticket_id,
            "paper_id": paper_id,
            "created_at": utc_now(),
            "requested_by": "structured_leader_field_level_semantic_audit",
            "target_queue": queue_by_worker[owner],
            "owner_worker": owner,
            "severity": "blocking",
            "reason": finding["reason"],
            "leader_finding_id": str(finding["finding_id"]),
            "leader_finding_fingerprint": finding_fingerprint,
            "source_locators": finding["source_locators"],
            "evidence_paths": list(
                dict.fromkeys(
                    [str(audit_path.relative_to(ROOT))]
                    + list(finding["evidence_paths"])
                )
            ),
            "required_actions": finding["required_actions"],
            "acceptance_checks": finding["acceptance_checks"],
            "blocks": [
                "publication_grade_acceptance",
                "leader_semantic_pass",
                "independent_verifier_pass",
                "remaining_200_batch_progress",
            ],
            "owner_response_contract": (
                "Append one evidence-bearing repair_ready_for_adjudication "
                "response; only a later fresh worker-6 may close this ticket."
            ),
        }
        append_jsonl(request_path, ticket)
        existing_ids.add(ticket_id)
        staged.append(ticket_id)
    return staged


def canonical_runtime_sessions(paper_id: str) -> set[str]:
    path = PILOT / "worker_logs" / paper_id / "run_sequence_latest.json"
    payload = read_json(path)
    return {
        str(report.get("codex_session_id"))
        for report in payload.get("reports", [])
        if isinstance(report, dict) and report.get("codex_session_id")
    }


def record_ledger_verdict(
    paper_id: str,
    kind: str,
    verdict: str,
    artifact: Path,
    log_dir: Path,
    label: str,
) -> dict[str, Any]:
    command = [
        "python3",
        str(LEDGER_CLI),
        f"record-{kind}",
        "--paper-id",
        paper_id,
        "--verdict",
        verdict,
        "--audit-path",
        str(artifact),
    ]
    run = run_command(command, log_dir, label, timeout=900)
    if run["returncode"] != 0:
        raise RuntimeError(f"could not record {kind} verdict: {run}")
    return run


def _process_paper_unwrapped(
    args: argparse.Namespace, paper_id: str
) -> dict[str, Any]:
    process_id = run_stamp()
    log_dir = CAMPAIGN_DIR / paper_id / f"process_{process_id}"
    log_dir.mkdir(parents=True, exist_ok=False)
    report: dict[str, Any] = {
        "paper_id": paper_id,
        "process_id": process_id,
        "started_at": utc_now(),
        "finished_at": None,
        "status": "in_progress",
        "rounds": [],
        "commands": [],
    }
    report_path = log_dir / "process_report.json"
    atomic_write_json(report_path, report)
    refresh_ledger(log_dir, "ledger_initial")
    row = state_row(paper_id)

    if row["workflow_status"] == "ready_for_six_worker_review":
        build = run_command(
            [
                "python3",
                str(PILOT_CLI),
                "build",
                "--paper-id",
                paper_id,
                "--raw-mode",
                "copy",
                "--append-manifest",
            ],
            log_dir,
            "build",
            timeout=1800,
        )
        report["commands"].append(build)
        if build["returncode"] != 0:
            raise RuntimeError(f"packet build failed: {build}")
        workers = run_command(
            [
                "python3",
                str(PILOT_CLI),
                "run",
                "--paper-id",
                paper_id,
                "--workers",
                ",".join(CANONICAL_WORKERS),
                "--timeout",
                str(args.worker_timeout),
                "--merge-existing",
            ],
            log_dir,
            "canonical_six_workers",
            timeout=args.worker_timeout * 6 + 1800,
        )
        report["commands"].append(workers)
        if workers["returncode"] != 0:
            report.update(status="worker_failure", finished_at=utc_now())
            atomic_write_json(report_path, report)
            return report
    elif row["workflow_status"] in {
        "six_worker_review_in_progress",
        "awaiting_worker6_repair_or_mechanical_acceptance",
    }:
        resume_workers = canonical_resume_workers(paper_id)
        if resume_workers:
            resume = run_command(
                [
                    "python3",
                    str(PILOT_CLI),
                    "run",
                    "--paper-id",
                    paper_id,
                    "--workers",
                    ",".join(resume_workers),
                    "--timeout",
                    str(args.worker_timeout),
                    "--merge-existing",
                ],
                log_dir,
                (
                    f"resume_canonical_{resume_workers[0]}"
                    f"_through_{resume_workers[-1]}"
                ),
                timeout=args.worker_timeout * len(resume_workers) + 900,
            )
            report["commands"].append(resume)
            if resume["returncode"] != 0:
                report.update(status="worker_failure", finished_at=utc_now())
                atomic_write_json(report_path, report)
                return report

    for round_number in range(1, args.max_rework_rounds + 1):
        refresh_ledger(log_dir, f"ledger_round_{round_number}_pre")
        owners = unresolved_ticket_owners(paper_id)
        for owner in owners:
            owner_run = run_command(
                [
                    "python3",
                    str(PILOT_CLI),
                    "run",
                    "--paper-id",
                    paper_id,
                    "--workers",
                    owner,
                    "--timeout",
                    str(args.worker_timeout),
                    "--merge-existing",
                ],
                log_dir,
                f"round_{round_number}_{owner}",
                timeout=args.worker_timeout + 900,
            )
            report["commands"].append(owner_run)
            if owner_run["returncode"] != 0:
                report.update(status="owner_worker_failure", finished_at=utc_now())
                atomic_write_json(report_path, report)
                return report
            refresh_ledger(log_dir, f"ledger_round_{round_number}_{owner}")

        current = state_row(paper_id)
        current_tickets = current.get("tickets") or {}
        worker6_needed = bool(owners) or (
            int(current_tickets.get("open_ticket_count") or 0) > 0
            and not owners
        ) or (
            current["workflow_status"]
            in {
                "six_worker_review_in_progress",
                "awaiting_worker6_repair_or_mechanical_acceptance",
            }
            and not (current.get("worker_runtime") or {}).get(
                "strict_six_worker_runtime_pass"
            )
        )
        if worker6_needed:
            worker6 = run_command(
                [
                    "python3",
                    str(PILOT_CLI),
                    "run",
                    "--paper-id",
                    paper_id,
                    "--workers",
                    "worker-6",
                    "--timeout",
                    str(args.worker_timeout),
                    "--merge-existing",
                ],
                log_dir,
                f"round_{round_number}_fresh_worker6",
                timeout=args.worker_timeout + 900,
            )
            report["commands"].append(worker6)
            if worker6["returncode"] != 0:
                report.update(status="worker6_failure", finished_at=utc_now())
                atomic_write_json(report_path, report)
                return report

        acceptance = run_command(
            ["python3", str(PILOT_CLI), "acceptance", "--paper-id", paper_id],
            log_dir,
            f"round_{round_number}_acceptance",
            timeout=1800,
        )
        report["commands"].append(acceptance)
        refresh_ledger(
            log_dir,
            f"ledger_round_{round_number}_post_acceptance",
        )
        post_acceptance_row = state_row(paper_id)
        if not should_run_leader_review(
            acceptance["returncode"], post_acceptance_row
        ):
            report["rounds"].append(
                {
                    "round": round_number,
                    "acceptance_returncode": acceptance["returncode"],
                    "leader_verdict": "SKIPPED_KNOWN_OPEN_TICKETS",
                    "ticket_ids_staged": [],
                }
            )
            atomic_write_json(report_path, report)
            continue

        try:
            audit_path, audit_runtime = run_structured_review(
                paper_id,
                "leader_semantic_auditor",
                LEADER_SCHEMA,
                leader_prompt(paper_id),
                args.audit_timeout,
                not args.disable_grok_safety_fallback,
            )
        except (StructuredReviewRunError, GrokStructuredReviewError) as error:
            report.update(
                status="leader_structured_review_failure_fail_closed",
                finished_at=utc_now(),
                structured_review_error=(
                    f"{type(error).__name__}: {error}"[:4000]
                ),
                structured_review_runtime=getattr(error, "runtime", None),
            )
            atomic_write_json(report_path, report)
            return report
        audit = read_json(audit_path)
        record_ledger_verdict(
            paper_id,
            "leader",
            str(audit["verdict"]),
            audit_path,
            log_dir,
            f"round_{round_number}_record_leader",
        )
        round_report: dict[str, Any] = {
            "round": round_number,
            "acceptance_returncode": acceptance["returncode"],
            "leader_audit_path": str(audit_path),
            "leader_audit_runtime": audit_runtime,
            "leader_verdict": audit["verdict"],
            "ticket_ids_staged": [],
        }
        report["rounds"].append(round_report)
        atomic_write_json(report_path, report)

        if audit["verdict"] == "FAIL":
            round_report["ticket_ids_staged"] = stage_audit_tickets(
                paper_id, audit_path, audit, round_number
            )
            sync_status = run_command(
                [
                    "python3",
                    str(PILOT_CLI),
                    "status",
                    "--paper-id",
                    paper_id,
                ],
                log_dir,
                f"round_{round_number}_sync_staged_tickets",
                timeout=1800,
            )
            report["commands"].append(sync_status)
            if sync_status["returncode"] != 0:
                raise RuntimeError(
                    f"could not synchronize staged tickets: {sync_status}"
                )
            refresh_ledger(log_dir, f"ledger_round_{round_number}_tickets")
            atomic_write_json(report_path, report)
            continue

        if acceptance["returncode"] != 0:
            report.update(
                status="leader_pass_but_mechanical_acceptance_failed",
                finished_at=utc_now(),
            )
            atomic_write_json(report_path, report)
            return report

        try:
            verifier_path, verifier_runtime = run_structured_review(
                paper_id,
                "independent_paper_verifier",
                VERIFIER_SCHEMA,
                verifier_prompt(paper_id, audit_path),
                args.audit_timeout,
                not args.disable_grok_safety_fallback,
            )
        except (StructuredReviewRunError, GrokStructuredReviewError) as error:
            report.update(
                status="verifier_structured_review_failure_fail_closed",
                finished_at=utc_now(),
                structured_review_error=(
                    f"{type(error).__name__}: {error}"[:4000]
                ),
                structured_review_runtime=getattr(error, "runtime", None),
            )
            atomic_write_json(report_path, report)
            return report
        verifier = read_json(verifier_path)
        canonical_sessions = canonical_runtime_sessions(paper_id)
        review_sessions = {
            str(audit_runtime["review_session_id"]),
            str(verifier_runtime["review_session_id"]),
        }
        if (
            len(canonical_sessions) != 6
            or len(review_sessions) != 2
            or any(session in {"", "None"} for session in review_sessions)
            or {
                f"codex:{session}" for session in canonical_sessions
            }
            & review_sessions
        ):
            raise RuntimeError("canonical/audit/verifier session independence failed")
        record_ledger_verdict(
            paper_id,
            "verifier",
            str(verifier["verdict"]),
            verifier_path,
            log_dir,
            f"round_{round_number}_record_verifier",
        )
        round_report.update(
            verifier_path=str(verifier_path),
            verifier_runtime=verifier_runtime,
            verifier_verdict=verifier["verdict"],
        )
        refresh_ledger(log_dir, f"ledger_round_{round_number}_terminal_check")
        final_row = state_row(paper_id)
        if (
            verifier["verdict"] == "PASS"
            and final_row["workflow_status"]
            == "terminal_scientific_review_complete"
        ):
            report.update(status="terminal_complete", finished_at=utc_now())
        else:
            report.update(
                status="independent_verifier_failed_or_terminal_contract_not_met",
                finished_at=utc_now(),
            )
        atomic_write_json(report_path, report)
        return report

    report.update(status="max_rework_rounds_exhausted", finished_at=utc_now())
    atomic_write_json(report_path, report)
    return report


def process_paper(args: argparse.Namespace, paper_id: str) -> dict[str, Any]:
    """Finalize a newly created process report even when execution raises."""
    paper_dir = CAMPAIGN_DIR / paper_id
    before = set(paper_dir.glob("process_*/process_report.json"))
    try:
        return _process_paper_unwrapped(args, paper_id)
    except Exception as error:
        after = set(paper_dir.glob("process_*/process_report.json"))
        for report_path in sorted(after - before):
            report = read_json(report_path)
            if report.get("status") != "in_progress":
                continue
            report.update(
                status="campaign_exception_fail_closed",
                finished_at=utc_now(),
                error=f"{type(error).__name__}: {error}"[:4000],
            )
            atomic_write_json(report_path, report)
        raise


def select_papers(limit: int, explicit: list[str] | None) -> list[str]:
    state = read_json(STATE)
    if explicit:
        frozen = {str(row["paper_id"]) for row in state.get("papers", [])}
        missing = [paper_id for paper_id in explicit if paper_id not in frozen]
        if missing:
            raise SystemExit(f"papers outside frozen queue: {missing}")
        return explicit[:limit]
    priorities = [
        "needs_targeted_semantic_rework",
        "awaiting_worker6_repair_or_mechanical_acceptance",
        "six_worker_review_in_progress",
        "awaiting_leader_field_semantic_audit",
        "awaiting_independent_verifier",
        "ready_for_six_worker_review",
    ]
    selected: list[str] = []
    for status in priorities:
        for row in state.get("papers", []):
            if row.get("workflow_status") == status:
                selected.append(str(row["paper_id"]))
                if len(selected) == limit:
                    return selected
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-id", action="append")
    parser.add_argument("--max-papers", type=int, default=1)
    parser.add_argument("--max-rework-rounds", type=int, default=3)
    parser.add_argument("--worker-timeout", type=int, default=3600)
    parser.add_argument("--audit-timeout", type=int, default=3600)
    parser.add_argument("--sleep-seconds", type=int, default=0)
    parser.add_argument("--disable-grok-safety-fallback", action="store_true")
    args = parser.parse_args()
    if args.max_papers < 1:
        raise SystemExit("--max-papers must be positive")

    CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)

    campaign_run_id = run_stamp()
    campaign_report_path = CAMPAIGN_DIR / f"campaign_run_{campaign_run_id}.json"
    campaign_report: dict[str, Any] = {
        "run_id": campaign_run_id,
        "started_at": utc_now(),
        "finished_at": None,
        "requested_max_papers": args.max_papers,
        "paper_reports": [],
        "status": "in_progress",
        "grok_safety_fallback_enabled": not args.disable_grok_safety_fallback,
        "quality_boundary": (
            "Distinct papers may execute in parallel, but each paper remains "
            "internally sequential. No terminal promotion without canonical "
            "six-worker runtime, mechanical acceptance, structured leader PASS, "
            "and separate verifier PASS. Grok may replace only a leader/verifier "
            "call rejected by the classified Codex biology-content safety access "
            "error; it never replaces a canonical worker."
        ),
    }
    atomic_write_json(campaign_report_path, campaign_report)
    refresh_dir = CAMPAIGN_DIR / f"refresh_{campaign_run_id}"
    refresh_dir.mkdir(parents=True, exist_ok=True)
    refresh_ledger(refresh_dir)
    selected = select_papers(args.max_papers, args.paper_id)
    for index, paper_id in enumerate(selected):
        try:
            with paper_campaign_lock(paper_id):
                result = process_paper(args, paper_id)
            paper_report = {
                "paper_id": paper_id,
                "status": result["status"],
                "process_id": result["process_id"],
            }
        except Exception as error:  # noqa: BLE001 - preserve and continue queue
            paper_report = {
                "paper_id": paper_id,
                "status": "campaign_exception_fail_closed",
                "process_id": None,
                "error": f"{type(error).__name__}: {error}"[:4000],
            }
        campaign_report["paper_reports"].append(paper_report)
        atomic_write_json(campaign_report_path, campaign_report)
        if index + 1 < len(selected) and args.sleep_seconds:
            time.sleep(args.sleep_seconds)
    campaign_report["finished_at"] = utc_now()
    campaign_report["status"] = "finished"
    atomic_write_json(campaign_report_path, campaign_report)
    atomic_write_json(CAMPAIGN_DIR / "campaign_run_latest.json", campaign_report)
    print(json.dumps(campaign_report, ensure_ascii=False, indent=2))
    return 0 if all(
        row["status"] == "terminal_complete"
        for row in campaign_report["paper_reports"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
