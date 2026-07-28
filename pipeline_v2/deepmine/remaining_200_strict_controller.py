#!/usr/bin/env python3
"""Durable ledger/controller for the frozen 200-paper strict review queue.

The controller never treats final-file presence or mechanical gates as
scientific completion.  A paper is terminal only after strict six-worker
runtime proof, mechanical acceptance, a recorded leader semantic audit PASS,
and a recorded independent verifier PASS.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot"
DEFAULT_QUEUE = PILOT / "manifests/remaining_200_strict_review_queue_20260726.json"
DEFAULT_STATE = PILOT / "manifests/remaining_200_strict_review_state_20260726.json"
DEFAULT_JOURNAL = PILOT / "reports/remaining_200_strict_review_journal_20260726.jsonl"
PILOT_CLI = ROOT / "pipeline_v2/deepmine/dbaasp_strict_pilot.py"
WORKLIST = ROOT / "pipeline_v2/deepmine/dbaasp_worklist.json"
MATERIAL_OVERLAY = PILOT / "manifests/material_recovery_worklist_overlay.json"
WORKERS = [f"worker-{number}" for number in range(1, 7)]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            rows.append(value)
    return rows


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def worklist_map() -> dict[str, tuple[Path, str]]:
    rows = json.loads(WORKLIST.read_text(encoding="utf-8"))
    work = {
        str(item[0]): (Path(str(item[1])), str(item[2]))
        for item in rows
        if isinstance(item, list) and len(item) >= 3
    }
    if MATERIAL_OVERLAY.exists():
        overlay = read_json(MATERIAL_OVERLAY)
        overlay_rows = overlay.get("rows")
        for item in overlay_rows if isinstance(overlay_rows, list) else []:
            if isinstance(item, list) and len(item) >= 3 and Path(str(item[1])).exists():
                work[str(item[0])] = (Path(str(item[1])), str(item[2]))
    return work


@lru_cache(maxsize=512)
def declared_supplement_names(xml_path_text: str) -> tuple[str, ...]:
    xml_path = Path(xml_path_text)
    if not xml_path.exists():
        return ()
    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError:
        return ()
    names: set[str] = set()
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag not in {"supplementary-material", "media", "ext-link"}:
            continue
        href = next(
            (
                str(value)
                for key, value in element.attrib.items()
                if key.endswith("href") or "href" in key
            ),
            "",
        )
        text = " ".join(" ".join(element.itertext()).split())[:500]
        name = Path(href).name
        # Match the pilot's canonical inventory semantics: every JATS
        # <media> payload is material, including TIFF/CIF files without a
        # conventional supplementary suffix or label.
        if tag == "media" and name:
            names.add(name)
        blob = f"{href} {text}".lower()
        suffix = Path(href).suffix.lower()
        looks_supplementary = bool(
            (
                tag in {"supplementary-material", "media"}
                and suffix
                in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".tsv", ".zip"}
            )
            or "suppl_file" in blob
            or (
                suffix in {".doc", ".docx", ".xls", ".xlsx", ".zip"}
                and re.search(
                    r"(supp|moesm|esm|si_|s\d{2,}|table\s*s|fig(?:ure)?\s*s)",
                    blob,
                )
            )
            or (
                suffix == ".pdf"
                and re.search(
                    r"(supp|moesm|esm|si_|s\d{2,}|supporting information|table\s*s|fig(?:ure)?\s*s)",
                    blob,
                )
            )
        )
        if not looks_supplementary:
            continue
        if not name:
            match = re.search(
                r"([A-Za-z0-9_.-]+\.(?:pdf|docx?|xlsx?|zip|csv|tsv))",
                text,
                re.I,
            )
            name = match.group(1) if match else ""
        if name:
            names.add(name)
    raw_xml = xml_path.read_text(encoding="utf-8", errors="replace")
    names.update(
        value.strip()
        for value in re.findall(r"<\?suppdata-name\s+([^?]+?)\?>", raw_xml, re.I)
        if value.strip()
    )
    return tuple(sorted(names))


def response_validation_passes(response: dict[str, Any]) -> bool:
    raw = response.get("validation_artifacts")
    if isinstance(raw, dict):
        entries = [(str(key), str(value)) for key, value in raw.items()]
    elif isinstance(raw, list):
        entries = [("", str(value)) for value in raw]
    else:
        return False
    leader_paths = [
        ROOT / path
        for key, path in entries
        if path.endswith(".json")
        and ("leader" in key.lower() or "leader" in Path(path).name.lower())
    ]
    if not leader_paths:
        return False
    for path in leader_paths:
        if not path.exists():
            return False
        payload = read_json(path)
        if (
            payload.get("passed") is not True
            or payload.get("blocking_failure_count") not in {0, None}
        ):
            return False
    return True


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def append_journal(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


@contextmanager
def state_lock(state_path: Path) -> Iterator[None]:
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield


def initial_state(queue_path: Path) -> dict[str, Any]:
    queue = read_json(queue_path)
    rows = queue.get("papers")
    rows = rows if isinstance(rows, list) else []
    ids = queue.get("paper_ids")
    ids = ids if isinstance(ids, list) else []
    by_id = {
        str(row.get("paper_id")): row
        for row in rows
        if isinstance(row, dict) and row.get("paper_id")
    }
    if len(ids) != 200 or len(set(ids)) != 200:
        raise ValueError("frozen queue must contain exactly 200 unique paper IDs")
    papers = []
    for index, paper_id in enumerate(ids, 1):
        snapshot = by_id.get(str(paper_id), {})
        papers.append(
            {
                "queue_index": index,
                "paper_id": str(paper_id),
                "title": snapshot.get("title"),
                "doi": snapshot.get("doi"),
                "pmid": snapshot.get("pmid"),
                "source_snapshot": {
                    "source_dir": snapshot.get("source_dir"),
                    "xml_exists": snapshot.get("xml_exists") is True,
                    "pdf_exists": snapshot.get("pdf_exists") is True,
                    "missing_declared_supplements": snapshot.get(
                        "missing_declared_supplements"
                    )
                    or [],
                },
                "leader_semantic_audit": None,
                "independent_verifier": None,
                "workflow_status": "queued",
            }
        )
    return {
        "schema_version": "remaining_200_strict_review_state_v1",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "frozen_queue_path": str(queue_path),
        "frozen_queue_sha256": file_sha256(queue_path),
        "frozen_denominator": 200,
        "completion_contract": {
            "six_unique_sequential_codex_exec_workers_gpt55_xhigh_rc0": True,
            "worker6_after_latest_upstream": True,
            "mechanical_acceptance_pass": True,
            "zero_open_tickets_and_rework_targets": True,
            "leader_field_level_semantic_audit_pass": True,
            "independent_verifier_pass": True,
            "authority_default_false": True,
        },
        "counts": {},
        "papers": papers,
    }


def source_material_state(row: dict[str, Any]) -> dict[str, Any]:
    paper_id = str(row["paper_id"])
    snapshot = row.get("source_snapshot") or {}
    source_dir = Path(str(snapshot.get("source_dir") or ""))
    local_source = PILOT / "papers" / paper_id / "source"
    worklist_path, worklist_kind = worklist_map().get(
        paper_id, (Path("/nonexistent"), "unknown")
    )
    worklist_xml = (
        worklist_path
        if worklist_kind == "xml"
        else worklist_path.with_suffix(".xml")
    )
    worklist_pdf = (
        worklist_path
        if worklist_kind == "pdf"
        else worklist_path.parent / "paper.pdf"
    )
    xml_exists = bool(
        snapshot.get("xml_exists")
        or (source_dir / "paper.xml").exists()
        or (local_source / "paper.xml").exists()
        or worklist_xml.exists()
    )
    pdf_exists = bool(
        snapshot.get("pdf_exists")
        or (source_dir / "paper.pdf").exists()
        or (local_source / "paper.pdf").exists()
        or worklist_pdf.exists()
    )
    missing_supplements = set(snapshot.get("missing_declared_supplements") or [])
    declared = declared_supplement_names(str(worklist_xml))
    staged_supplement_dir = worklist_xml.parent / "supplementary"
    missing_supplements.update(
        name
        for name in declared
        if not (staged_supplement_dir / name).exists()
    )
    missing_supplements = {
        name
        for name in missing_supplements
        if not (staged_supplement_dir / name).exists()
        if not (local_source / "supplementary" / name).exists()
    }
    return {
        "xml_exists": xml_exists,
        "pdf_exists": pdf_exists,
        "worklist_source_file": str(worklist_path),
        "worklist_source_kind": worklist_kind,
        "declared_supplement_count": len(declared),
        "missing_declared_supplements": sorted(missing_supplements),
        "primary_material_ready": xml_exists or pdf_exists,
        "structured_fulltext_recovery_required": pdf_exists and not xml_exists,
        "strict_material_ready": xml_exists and pdf_exists and not missing_supplements,
    }


def worker_runtime_state(paper_id: str) -> dict[str, Any]:
    path = PILOT / "worker_logs" / paper_id / "run_sequence_latest.json"
    sequence = read_json(path) if path.exists() else {}
    reports = sequence.get("reports")
    reports = reports if isinstance(reports, list) else []
    report_workers = [
        str(report.get("worker") or "")
        for report in reports
        if isinstance(report, dict)
    ]
    canonical_worker_order = report_workers == WORKERS
    by_worker = {
        str(report.get("worker")): report
        for report in reports
        if isinstance(report, dict) and report.get("worker")
    }
    sessions = [
        str(by_worker[worker].get("codex_session_id") or "")
        for worker in WORKERS
        if worker in by_worker
    ]
    clean_workers = [
        worker
        for worker in WORKERS
        if worker in by_worker
        and by_worker[worker].get("returncode") == 0
        and by_worker[worker].get("codex_model") == "gpt-5.5"
        and by_worker[worker].get("codex_reasoning_effort") == "xhigh"
        and by_worker[worker].get("codex_session_id")
        and isinstance(by_worker[worker].get("command"), list)
        and len(by_worker[worker]["command"]) >= 2
        and Path(str(by_worker[worker]["command"][0])).name == "codex"
        and by_worker[worker]["command"][1] == "exec"
    ]
    worker6_fresh = False
    if all(worker in by_worker for worker in WORKERS):
        worker6_start = str(by_worker["worker-6"].get("started_at") or "")
        upstream_finish = max(
            str(by_worker[worker].get("finished_at") or "") for worker in WORKERS[:-1]
        )
        worker6_fresh = bool(worker6_start and worker6_start >= upstream_finish)
    return {
        "run_sequence_path": str(path),
        "worker_report_count": len(reports),
        "canonical_worker_order": canonical_worker_order,
        "clean_workers": clean_workers,
        "unique_session_count": len(set(filter(None, sessions))),
        "worker6_after_latest_upstream": worker6_fresh,
        "strict_six_worker_runtime_pass": canonical_worker_order
        and len(reports) == 6
        and len(clean_workers) == 6
        and len(set(filter(None, sessions))) == 6
        and worker6_fresh,
    }


def open_ticket_state(paper_id: str) -> dict[str, Any]:
    packet = PILOT / "packets" / paper_id
    manifest_path = packet / "packet_manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {}
    ids = manifest.get("open_rework_ticket_ids")
    ids = ids if isinstance(ids, list) else []
    requests = read_jsonl(packet / "rework/rework_requests.jsonl")
    responses = read_jsonl(packet / "rework/rework_responses.jsonl")
    owners: list[str] = []
    ready_owner_workers: list[str] = []
    for request in requests:
        if request.get("ticket_id") not in ids:
            continue
        owner = str(request.get("owner_worker") or "")
        for worker in WORKERS[:-1]:
            if worker not in owner:
                continue
            owner_ready = any(
                response.get("ticket_id") == request.get("ticket_id")
                and response.get("response_by") == worker
                and response.get("response_status") == "repair_ready_for_adjudication"
                and response.get("analysis_can_resume") is True
                and response_validation_passes(response)
                and any(
                    response.get(key)
                    for key in (
                        "evidence",
                        "evidence_paths",
                        "repaired_artifacts",
                        "artifacts_written",
                        "added_files",
                        "validation_artifacts",
                        "reason",
                        "notes",
                    )
                )
                for response in responses
            )
            if owner_ready:
                if worker not in ready_owner_workers:
                    ready_owner_workers.append(worker)
            elif worker not in owners:
                owners.append(worker)
    return {
        "open_ticket_count": len(ids),
        "open_ticket_ids": ids,
        "ordered_missing_owner_workers": owners,
        "ready_owner_workers": ready_owner_workers,
    }


def acceptance_state(paper_id: str) -> dict[str, Any]:
    path = PILOT / "reports" / f"{paper_id}_strict_acceptance_audit_latest.json"
    payload = read_json(path) if path.exists() else {}
    return {
        "acceptance_audit_path": str(path),
        "mechanical_acceptance_pass": payload.get(
            "acceptance_ready_for_paper_level_source_review"
        )
        is True,
        "authority_ready": payload.get("authoritative_dbaasp_ingest_ready") is True,
    }


def recorded_pass(record: Any) -> bool:
    return isinstance(record, dict) and record.get("verdict") == "PASS"


def derive_status(row: dict[str, Any]) -> str:
    material = row["material"]
    runtime = row["worker_runtime"]
    tickets = row["tickets"]
    acceptance = row["acceptance"]
    leader_pass = recorded_pass(row.get("leader_semantic_audit"))
    verifier_pass = recorded_pass(row.get("independent_verifier"))
    leader_fail = isinstance(row.get("leader_semantic_audit"), dict) and row[
        "leader_semantic_audit"
    ].get("verdict") == "FAIL"

    if (
        material["strict_material_ready"]
        and runtime["strict_six_worker_runtime_pass"]
        and tickets["open_ticket_count"] == 0
        and acceptance["mechanical_acceptance_pass"]
        and not acceptance["authority_ready"]
        and leader_pass
        and verifier_pass
    ):
        return "terminal_scientific_review_complete"
    if tickets["open_ticket_count"] or leader_fail:
        return "needs_targeted_semantic_rework"
    if acceptance["mechanical_acceptance_pass"]:
        return (
            "awaiting_independent_verifier"
            if leader_pass
            else "awaiting_leader_field_semantic_audit"
        )
    if runtime["strict_six_worker_runtime_pass"]:
        return "awaiting_worker6_repair_or_mechanical_acceptance"
    if runtime["worker_report_count"]:
        return "six_worker_review_in_progress"
    if material["strict_material_ready"]:
        return "ready_for_six_worker_review"
    if material["primary_material_ready"]:
        if material["structured_fulltext_recovery_required"]:
            return "needs_structured_fulltext_recovery"
        return "needs_declared_supplement_recovery"
    return "needs_primary_material_recovery"


def refresh_state(state: dict[str, Any]) -> dict[str, Any]:
    queue_path = Path(str(state["frozen_queue_path"]))
    if not queue_path.exists() or file_sha256(queue_path) != state["frozen_queue_sha256"]:
        raise RuntimeError("frozen queue is missing or its SHA-256 changed")
    for row in state["papers"]:
        row["material"] = source_material_state(row)
        row["worker_runtime"] = worker_runtime_state(str(row["paper_id"]))
        row["tickets"] = open_ticket_state(str(row["paper_id"]))
        row["acceptance"] = acceptance_state(str(row["paper_id"]))
        row["workflow_status"] = derive_status(row)
        row["refreshed_at"] = utc_now()
    counts = Counter(str(row["workflow_status"]) for row in state["papers"])
    state["counts"] = {
        "frozen_denominator": 200,
        "terminal_scientific_review_complete": counts.get(
            "terminal_scientific_review_complete", 0
        ),
        "remaining_nonterminal": 200
        - counts.get("terminal_scientific_review_complete", 0),
        "strict_material_ready": sum(
            bool(row["material"]["strict_material_ready"]) for row in state["papers"]
        ),
        "primary_material_recovery_required": counts.get(
            "needs_primary_material_recovery", 0
        ),
        "structured_fulltext_recovery_required": counts.get(
            "needs_structured_fulltext_recovery", 0
        ),
        "declared_supplement_recovery_required": counts.get(
            "needs_declared_supplement_recovery", 0
        ),
        "open_ticket_count": sum(row["tickets"]["open_ticket_count"] for row in state["papers"]),
        "workflow_status": dict(sorted(counts.items())),
    }
    state["updated_at"] = utc_now()
    return state


def select_next(state: dict[str, Any]) -> dict[str, Any] | None:
    priorities = [
        "needs_targeted_semantic_rework",
        "awaiting_worker6_repair_or_mechanical_acceptance",
        "ready_for_six_worker_review",
        "six_worker_review_in_progress",
        "awaiting_leader_field_semantic_audit",
        "awaiting_independent_verifier",
        "needs_declared_supplement_recovery",
        "needs_structured_fulltext_recovery",
        "needs_primary_material_recovery",
    ]
    for status in priorities:
        for row in state["papers"]:
            if row["workflow_status"] == status:
                return row
    return None


def next_action(row: dict[str, Any]) -> dict[str, Any]:
    paper_id = str(row["paper_id"])
    status = str(row["workflow_status"])
    relative_cli = PILOT_CLI.relative_to(ROOT)
    if status == "needs_targeted_semantic_rework":
        workers = list(row["tickets"]["ordered_missing_owner_workers"])
        if workers:
            command = [
                "python3",
                str(relative_cli),
                "run",
                "--paper-id",
                paper_id,
                "--workers",
                workers[0],
                "--timeout",
                "3600",
                "--merge-existing",
            ]
            action = "run_next_ticket_owner_then_recheck_leader_validator"
        elif row["tickets"]["ready_owner_workers"]:
            command = [
                "python3",
                str(relative_cli),
                "run",
                "--paper-id",
                paper_id,
                "--workers",
                "worker-6",
                "--timeout",
                "3600",
                "--merge-existing",
            ]
            action = "all_ticket_owners_validated_run_fresh_worker6_only"
        else:
            command = []
            action = "leader_must_define_targeted_rework_ticket"
    elif status == "ready_for_six_worker_review":
        command = [
            "python3",
            str(relative_cli),
            "controller",
            "once",
            "--paper-id",
            paper_id,
            "--timeout",
            "3600",
            "--keep-going",
        ]
        action = "build_and_run_six_workers_then_mechanical_acceptance"
    elif status == "needs_declared_supplement_recovery":
        command = [
            "python3",
            str(relative_cli),
            "recover-materials",
            "--paper-id",
            paper_id,
            "--apply",
        ]
        action = "recover_declared_supplements_before_strict_review"
    elif status == "needs_primary_material_recovery":
        command = []
        action = "recover_primary_xml_and_pdf_before_strict_review"
    elif status == "needs_structured_fulltext_recovery":
        command = []
        action = "recover_xml_oa_package_and_supplements_or_record_durable_unavailability_for_existing_pdf"
    elif status == "awaiting_leader_field_semantic_audit":
        command = []
        action = "perform_and_record_leader_field_level_semantic_audit"
    elif status == "awaiting_independent_verifier":
        command = []
        action = "perform_and_record_independent_verifier"
    else:
        command = [
            "python3",
            str(relative_cli),
            "acceptance",
            "--paper-id",
            paper_id,
        ]
        action = "repair_worker6_or_rerun_mechanical_acceptance"
    return {
        "paper_id": paper_id,
        "queue_index": row["queue_index"],
        "workflow_status": status,
        "action": action,
        "command": command,
        "shell_command": " ".join(command),
    }


def load_or_initialize(args: argparse.Namespace) -> dict[str, Any]:
    if args.state.exists():
        return read_json(args.state)
    state = refresh_state(initial_state(args.queue))
    atomic_write_json(args.state, state)
    append_journal(
        args.journal,
        {
            "event_at": utc_now(),
            "event": "queue_state_initialized",
            "state_path": str(args.state),
            "queue_path": str(args.queue),
            "queue_sha256": state["frozen_queue_sha256"],
            "counts": state["counts"],
        },
    )
    return state


def save_refresh(args: argparse.Namespace, event: str) -> dict[str, Any]:
    with state_lock(args.state):
        state = refresh_state(load_or_initialize(args))
        atomic_write_json(args.state, state)
        append_journal(
            args.journal,
            {
                "event_at": utc_now(),
                "event": event,
                "state_path": str(args.state),
                "counts": state["counts"],
            },
        )
    return state


def cmd_init(args: argparse.Namespace) -> int:
    state = save_refresh(args, "queue_state_init_or_refresh")
    print(json.dumps({"state_path": str(args.state), "counts": state["counts"]}, ensure_ascii=False, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    state = save_refresh(args, "queue_state_refreshed")
    selected = select_next(state)
    output = {
        "state_path": str(args.state),
        "journal_path": str(args.journal),
        "updated_at": state["updated_at"],
        "counts": state["counts"],
        "next": next_action(selected) if selected else None,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    state = save_refresh(args, "queue_next_selected")
    selected = select_next(state)
    output = next_action(selected) if selected else {"action": "queue_complete", "paper_id": None}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def record_verdict(args: argparse.Namespace, field: str, event: str) -> int:
    audit_path = args.audit_path.resolve()
    if not audit_path.exists():
        raise SystemExit(f"missing audit artifact: {audit_path}")
    with state_lock(args.state):
        state = load_or_initialize(args)
        matches = [row for row in state["papers"] if row["paper_id"] == args.paper_id]
        if len(matches) != 1:
            raise SystemExit(f"paper is not in frozen queue: {args.paper_id}")
        record = {
            "verdict": args.verdict,
            "recorded_at": utc_now(),
            "artifact_path": str(audit_path),
            "artifact_sha256": file_sha256(audit_path),
            "notes": args.notes,
        }
        matches[0][field] = record
        state = refresh_state(state)
        atomic_write_json(args.state, state)
        append_journal(
            args.journal,
            {
                "event_at": utc_now(),
                "event": event,
                "paper_id": args.paper_id,
                "record": record,
                "workflow_status": matches[0]["workflow_status"],
                "counts": state["counts"],
            },
        )
    print(
        json.dumps(
            {
                "paper_id": args.paper_id,
                field: record,
                "workflow_status": matches[0]["workflow_status"],
                "counts": state["counts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_record_leader(args: argparse.Namespace) -> int:
    return record_verdict(args, "leader_semantic_audit", "leader_semantic_audit_recorded")


def cmd_record_verifier(args: argparse.Namespace) -> int:
    return record_verdict(args, "independent_verifier", "independent_verifier_recorded")


def add_paths(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--journal", type=Path, default=DEFAULT_JOURNAL)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, function in (("init", cmd_init), ("status", cmd_status), ("next", cmd_next)):
        child = sub.add_parser(name)
        add_paths(child)
        child.set_defaults(function=function)
    for name, function in (
        ("record-leader", cmd_record_leader),
        ("record-verifier", cmd_record_verifier),
    ):
        child = sub.add_parser(name)
        add_paths(child)
        child.add_argument("--paper-id", required=True)
        child.add_argument("--verdict", choices=("PASS", "FAIL"), required=True)
        child.add_argument("--audit-path", type=Path, required=True)
        child.add_argument("--notes")
        child.set_defaults(function=function)
    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
