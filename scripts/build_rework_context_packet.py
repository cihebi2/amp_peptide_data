#!/usr/bin/env python3
"""Build a focused rework handoff packet for a new Codex CLI review.

The packet is deliberately path-heavy and excerpt-light: it tells the next
worker which local artifacts to reopen, which omissions caused rejection, and
which skill contract owns the repair. It does not copy paper text, sequences, or
long protocols into the message layer.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LANDED_ROOT = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets")
OUTPUT_ROOT = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/output")

WORKER_SKILLS = {
    "worker-2": {
        "role": "body/table activity-toxicity repair",
        "skill_path": ".codex/skills/paper-body-table-worker/SKILL.md",
        "owns": ["activity table shape", "activity row value/unit/target", "main-text table locators"],
    },
    "worker-3": {
        "role": "supplementary material repair",
        "skill_path": ".codex/skills/paper-supp-evidence-worker/SKILL.md",
        "owns": ["supplementary files", "archives", "office/OCR recovery", "supplement locators"],
    },
    "worker-4": {
        "role": "database record adjudication",
        "skill_path": ".codex/skills/paper-database-record-auditor/SKILL.md",
        "owns": ["APD6/DBAASP/DRAMP conflicts", "sequence/source status", "database-only rows"],
    },
    "worker-5": {
        "role": "mechanism ontology repair",
        "skill_path": ".codex/skills/paper-mechanism-ontology-worker/SKILL.md",
        "owns": ["mechanism evidence class", "direct assay type", "claim locator"],
    },
    "worker-6": {
        "role": "final adjudication and quality gate",
        "skill_path": ".codex/skills/paper-adjudicator-review-worker/SKILL.md",
        "owns": ["qc_failure_reasons", "rework_targets", "publication-grade decision"],
    },
}

SOURCE_SUFFIXES = {
    ".xml",
    ".nxml",
    ".pdf",
    ".html",
    ".htm",
    ".tar",
    ".tgz",
    ".gz",
    ".zip",
    ".rar",
    ".7z",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".txt",
    ".json",
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
}


def safe_dir_name(paper_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._=-]+", "_", paper_id.strip())
    return cleaned.strip("._") or "paper"


BEST_EFFORT_SOURCE_PROTOCOL = {
    "policy": "bounded_best_effort_source_recovery",
    "goal": "Recover every paper-local value that can be recovered with existing local materials before marking a gap unrecoverable.",
    "priority_order": [
        "paper-local packet manifest, locator index, extraction status, and prior rework tickets",
        "primary XML/NXML, publisher PDF text/tables, figure captions, and OA package members",
        "declared supplementary files, archives, spreadsheets, office documents, images, and OCR outputs",
        "linked APD6/DBAASP/DRAMP rows and merged experimental database snapshots",
        "prior final/work artifacts only as hypotheses that must be rechecked against source locators",
    ],
    "required_actions": [
        "Open paths from handoff_context.json; do not rely on chat summaries as evidence.",
        "Use local office/archive/OCR tools only when the missing evidence is relevant and the source path exists.",
        "Prefer high-value recoverable sources first; do not spend attempts on peripheral gaps that cannot affect the gate.",
        "Never fabricate missing sequence, activity, toxicity, mechanism, unit, target, or database evidence.",
        "If a source cannot be recovered after reasonable local attempts, record an unrecoverable_material_gaps entry and continue to the next paper.",
    ],
    "suggested_tools_by_surface": {
        "pdf": ["pdftotext", "pdfimages/OCR only when text extraction is insufficient"],
        "office": ["python stdlib OOXML readers", "antiword", "catdoc", "xls2csv"],
        "archive": ["/root/software/rar-tools/7zz", "/root/software/rar-tools/extract-rar", "python zipfile/tarfile"],
        "image_or_scan": ["/root/software/PaddleOCR/.venv/bin/python -m paddleocr"],
        "xml_or_html": ["xml parser", "rg over extracted text/html"],
    },
    "efficiency_guard": "Stop a paper after max_rework_attempts or after source exhaustion proves the blocking evidence is not locally recoverable; mark the gap and move on instead of looping.",
}

OBTAINABLE_ONLY_PROTOCOL = {
    "policy": "obtainable_material_only",
    "success_definition": "Capture source-supported facts available in local materials; do not require unsupported or missing-source values to be filled before the queue can advance.",
    "worker_contract": [
        "Treat locally opened XML/PDF/supplement/database artifacts as the only evidence surface unless the source file itself links to a recoverable local asset.",
        "Extract values, targets, units, mechanism classes, and database statuses only when the local material supports them.",
        "If an exact value exists only in a missing external supplement, image-only chart, unsupported scan, or absent primary source, preserve it as source_conflict/unresolved instead of inventing it.",
        "Once the relevant local sources are exhausted, write unrecoverable_material_gaps and stop this paper; the controller will advance to the next paper.",
    ],
    "not_success": [
        "fabricating exact numbers to satisfy a gate",
        "repeating broad worker-6 passes after the same source gap is documented",
        "turning parser/tool limitations into publication-grade acceptance",
    ],
}

UNRECOVERABLE_MATERIAL_GAP_SCHEMA = {
    "gap_code": "short_machine_code",
    "owner_worker": "worker-2|worker-3|worker-4|worker-5|worker-6",
    "source_paths_checked": ["paper-local paths actually opened"],
    "tools_attempted": ["tool or parser names actually attempted"],
    "why_unrecoverable": "specific local reason, for example missing file, scanned figure unreadable, unsupported archive, absent primary source, or gate still failing after bounded repair",
    "impact": "which layer remains non-publication-grade",
    "blocks_publication_grade": True,
    "next_action": "record_and_continue|external_source_needed|manual_domain_review_needed",
}

BOUNDED_REWORK_PROTOCOL = {
    "queue_start_policy": "start_once_per_manifest_or_paper; retries must not rerun the initial queue bootstrap unless explicitly reset",
    "handoff_policy": "each failed gate builds or refreshes rework_context/<paper_id>/ and sends CODEX_REVIEW_PROMPT.md to a fresh Codex CLI owner worker",
    "attempt_policy": "worker repairs the owner layer, writes rework_responses.jsonl/quality_feedback.json, then worker-6/gates recheck",
    "stop_policy": "accept only after open tickets are closed and strict gates pass; otherwise stop at max attempts as blocked/unrecoverable and advance to the next paper",
}

POLICY_SAFE_MINIMAL_PROTOCOL = {
    "policy": "policy_safe_minimal_context",
    "goal": (
        "Run source-backed curation without placing long biomedical source text, "
        "assay prose, peptide sequences, concentrations, or therapeutic claims in "
        "the prompt, chat, stdout, or stderr."
    ),
    "worker_contract": [
        "Use the prompt and policy_safe_handoff_context as a path index only.",
        "Open paper-local files as needed, but keep command output to counts, keys, locators, and pass/fail status.",
        "Write recovered curation evidence into paper-local JSON artifacts instead of quoting source text in terminal output.",
        "Do not print peptide sequences, detailed protocols, exact dose-response prose, or antiviral/therapeutic narrative text.",
        "If safety or source limitations prevent controlled review, leave the paper non-accepted with a concrete blocker and move on.",
    ],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - packet builder must preserve partial context
        return {"_parse_error": str(exc), "_path": str(path)}
    return data if isinstance(data, dict) else {"_not_object": True, "_path": str(path)}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
            rows.append(value if isinstance(value, dict) else {"value": value})
        except json.JSONDecodeError:
            rows.append({"raw": line[:500]})
    return rows


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def existing(path: Path, root: Path) -> str | None:
    return rel(path, root) if path.exists() else None


def summarize_source_tree(path: Path, repo: Path, *, max_samples: int = 80) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "path": rel(path, repo),
        "exists": path.exists(),
        "file_count": 0,
        "suffix_counts": {},
        "sample_files": [],
    }
    if not path.exists():
        return summary
    if path.is_file():
        suffix = path.suffix.lower()
        summary["file_count"] = 1
        summary["suffix_counts"] = {suffix or "<none>": 1}
        summary["sample_files"] = [rel(path, repo)]
        return summary
    for child in sorted(path.rglob("*")):
        if not child.is_file():
            continue
        suffix = child.suffix.lower() or "<none>"
        summary["file_count"] += 1
        summary["suffix_counts"][suffix] = int(summary["suffix_counts"].get(suffix, 0)) + 1
        if len(summary["sample_files"]) < max_samples and (suffix in SOURCE_SUFFIXES or suffix == "<none>"):
            summary["sample_files"].append(rel(child, repo))
    return summary


def collect_source_inventory(repo: Path, paper_id: str) -> dict[str, Any]:
    """Summarize source paths without copying source text into the handoff."""
    packet = repo / "paper_packets" / paper_id
    paper = repo / "papers" / paper_id
    roots = {
        "landed_paper_root": LANDED_ROOT / "papers" / paper_id,
        "local_packet_raw": packet / "raw",
        "local_packet_extracted": packet / "extracted",
        "local_packet_database": packet / "database",
        "local_packet_locators": packet / "locators",
        "local_paper_source": paper / "source",
        "local_paper_work": paper / "work",
        "local_paper_final": paper / "final",
    }
    inventory = {name: summarize_source_tree(path, repo) for name, path in roots.items()}
    inventory["merged_output_root"] = {
        "path": str(OUTPUT_ROOT),
        "exists": OUTPUT_ROOT.exists(),
        "note": "Large merged database output root; use specific linked rows or experiment manifests from packet/database before broad scans.",
    }
    return inventory


def load_audit_entry(audit_path: Path, paper_id: str) -> dict[str, Any]:
    audit = read_json(audit_path)
    for item in audit.get("papers") or []:
        if isinstance(item, dict) and item.get("paper_id") == paper_id:
            return item
    return {}


def collect_gate_failures(repo: Path, paper_id: str) -> dict[str, Any]:
    semantic_report = repo / "reports" / f"{paper_id}.semantic_gate.json"
    publication_report = repo / "reports" / f"{paper_id}.publication_quality.json"
    semantic = read_json(semantic_report)
    publication = read_json(publication_report)
    semantic_issues: list[dict[str, Any]] = []
    for result in semantic.get("results") or []:
        if isinstance(result, dict):
            semantic_issues.extend(issue for issue in result.get("issues") or [] if isinstance(issue, dict))
    return {
        "semantic_report": existing(semantic_report, repo),
        "publication_report": existing(publication_report, repo),
        "semantic_issue_count": len(semantic_issues),
        "semantic_issue_codes": sorted({str(issue.get("code")) for issue in semantic_issues if issue.get("code")}),
        "semantic_issue_examples": semantic_issues[:8],
        "publication_risk_counts": publication.get("risk_counts") or {},
        "publication_risk_examples": publication.get("risk_examples") or {},
    }


def compact_gate_failures(gate: dict[str, Any]) -> dict[str, Any]:
    """Keep gate evidence machine-readable without copying source-rich examples."""
    return {
        "semantic_report": gate.get("semantic_report"),
        "publication_report": gate.get("publication_report"),
        "semantic_issue_count": gate.get("semantic_issue_count"),
        "semantic_issue_codes": gate.get("semantic_issue_codes") or [],
        "publication_risk_counts": gate.get("publication_risk_counts") or {},
        "examples_omitted_for_policy_safe_prompt": True,
    }


def collect_artifacts(repo: Path, paper_id: str) -> dict[str, Any]:
    packet = repo / "paper_packets" / paper_id
    paper = repo / "papers" / paper_id
    workflow = repo / ".miaobi-paper-review" / "workflows" / safe_dir_name(paper_id)
    reports = repo / "reports"
    artifact_paths = {
        "packet_manifest": packet / "packet_manifest.json",
        "locator_index": packet / "locators" / "locator_index.json",
        "extraction_status": packet / "extraction" / "extraction_status.json",
        "extraction_quality_report": packet / "extraction" / "extraction_quality_report.json",
        "material_staging_status": packet / "extraction" / "material_staging_status.json",
        "raw_supplementary_original": packet / "raw" / "supplementary_original",
        "extracted_supplementary_index": packet / "extracted" / "supplementary_index.json",
        "extracted_supplementary_text": packet / "extracted" / "supplementary_text.jsonl",
        "extracted_supplementary_tables": packet / "extracted" / "supplementary_tables.json",
        "analysis_status": packet / "analysis" / "analysis_status.json",
        "packet_activity": packet / "analysis" / "activity_toxicity_evidence.json",
        "packet_database": packet / "analysis" / "database_record_audit.json",
        "packet_mechanism": packet / "analysis" / "mechanism_evidence.json",
        "packet_adjudication": packet / "analysis" / "adjudication_report.json",
        "rework_requests": packet / "rework" / "rework_requests.jsonl",
        "rework_responses": packet / "rework" / "rework_responses.jsonl",
        "manual_digitization_feasibility": packet / "manual_digitization" / "feasibility.json",
        "manual_digitization_tasks": packet / "manual_digitization" / "manual_digitization_tasks.json",
        "manual_digitization_evidence": packet / "manual_digitization" / "digitization_evidence.json",
        "final_review_report": paper / "final" / "review_report.json",
        "final_activity": paper / "final" / "activity_toxicity_evidence.json",
        "final_database": paper / "final" / "database_record_verification.json",
        "final_mechanism": paper / "final" / "mechanism_ontology_record.json",
        "quality_feedback": paper / "work" / "review" / "quality_feedback.json",
        "workflow_context": workflow / "workflow_context.json",
        "state_executions": workflow / "state_executions.jsonl",
        "chat_messages": workflow / "chat_messages.jsonl",
        "agent_logs": workflow / "agent_logs.jsonl",
        "latest_complete_report": reports / f"{paper_id}.complete_message_test_report.json",
        "latest_capped_rework_report": reports / f"{paper_id}.capped_rework_test_report.json",
    }
    return {
        "packet_root": rel(packet, repo),
        "paper_root": rel(paper, repo),
        "workflow_dir": rel(workflow, repo),
        "paths": {name: rel(path, repo) for name, path in artifact_paths.items() if path.exists()},
        "source_roots": {
            "landed_paper": str(LANDED_ROOT / "papers" / paper_id),
            "merged_output": str(OUTPUT_ROOT),
            "local_packet": rel(packet, repo),
            "local_paper": rel(paper, repo),
        },
    }


def collect_manual_digitization_context(repo: Path, paper_id: str) -> dict[str, Any]:
    """Load task-packet metadata without promoting it to scientific evidence."""
    packet = repo / "paper_packets" / paper_id / "manual_digitization"
    feasibility = read_json(packet / "feasibility.json")
    tasks = read_json(packet / "manual_digitization_tasks.json")
    evidence = read_json(packet / "digitization_evidence.json")
    if not any([feasibility, tasks, evidence]):
        return {"available": False, "strict_boundary": "No manual-digitization task packet is present."}
    return {
        "available": True,
        "feasibility_path": rel(packet / "feasibility.json", repo),
        "task_manifest_path": rel(packet / "manual_digitization_tasks.json", repo),
        "digitization_evidence_path": rel(packet / "digitization_evidence.json", repo),
        "classification": feasibility.get("classification"),
        "recommended_queue": feasibility.get("recommended_queue"),
        "recommended_action": feasibility.get("recommended_action"),
        "digitization_candidate": feasibility.get("digitization_candidate"),
        "analysis_rework_candidate": feasibility.get("analysis_rework_candidate"),
        "hard_missing_source_gap": feasibility.get("hard_missing_source_gap"),
        "target_surface_count": len(feasibility.get("target_surfaces") or []),
        "task_count": len(tasks.get("tasks") or []),
        "digitized_value_count": evidence.get("digitized_value_count"),
        "strict_boundary": (
            "Task packet only; exact values are not promoted without controlled QA, "
            "owner-worker source review, worker-6 adjudication, and strict gates."
        ),
    }


def owner_workers_from_reasons(reasons: list[Any], gate: dict[str, Any], quality_feedback: dict[str, Any]) -> list[str]:
    owners = {"worker-6"}
    for item in quality_feedback.get("qc_failure_reasons") or []:
        if not isinstance(item, dict):
            continue
        owner_text = str(item.get("owner_worker") or "").lower()
        for worker in WORKER_SKILLS:
            if worker in owner_text:
                owners.add(worker)

    for reason in [str(item).lower() for item in reasons]:
        generic_review_only = reason.startswith("review layer is deliberately") or reason.startswith("the framework test inventories")
        if not generic_review_only and any(token in reason for token in ("activity parser", "activity extraction", "activity-bearing table", "missing_activity", "target species", "mic table", "parser-supported activity")):
            owners.add("worker-2")
        if any(token in reason for token in ("likely activity is in prose/figures/supplement", "figures/prose/supplement", "supplement rather than parser", "ocr", "archive", "office", "xlsx")):
            owners.add("worker-3")
        if any(token in reason for token in ("database adjudication", "source_conflict", "database-only", "database_only", "linked database")):
            owners.add("worker-4")
        if not generic_review_only and any(token in reason for token in ("mechanism claim", "direct_mechanism", "ontology")):
            owners.add("worker-5")

    gate_blob = json.dumps(gate, ensure_ascii=False).lower()
    if any(token in gate_blob for token in ("missing_activity", "target_species", "generic_endpoint", "mic_like")):
        owners.add("worker-2")
    if any(token in gate_blob for token in ("supplement", "publisher_boilerplate")):
        owners.add("worker-3")
    if any(token in gate_blob for token in ("database", "source_verified_without", "source_conflict")):
        owners.add("worker-4")
    if any(token in gate_blob for token in ("mechanism", "direct_mechanism")):
        owners.add("worker-5")
    return sorted(owners)


def compact_qc_reasons(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in data.get("qc_failure_reasons") or []:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                key: item.get(key)
                for key in (
                    "code",
                    "failure_code",
                    "owner_worker",
                    "severity",
                    "layer",
                    "artifact_path",
                    "failing_object",
                    "issue_count",
                )
                if item.get(key) is not None
            }
        )
    return rows


def compact_rework_targets(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in data.get("rework_targets") or []:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                key: item.get(key)
                for key in (
                    "ticket_id",
                    "worker",
                    "owner_worker",
                    "layer",
                    "artifact_path",
                    "failing_object",
                    "failure_code",
                    "target_queue",
                    "severity",
                )
                if item.get(key) is not None
            }
        )
    return rows


def compact_material_gaps(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in data.get("unrecoverable_material_gaps") or []:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                key: item.get(key)
                for key in (
                    "gap_code",
                    "owner_worker",
                    "impact",
                    "blocks_publication_grade",
                    "next_action",
                )
                if item.get(key) is not None
            }
        )
    return rows


def compact_rework_requests(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for item in rows:
        compact.append(
            {
                key: item.get(key)
                for key in (
                    "ticket_id",
                    "target_queue",
                    "severity",
                    "requested_by",
                    "blocks",
                    "created_at",
                )
                if item.get(key) is not None
            }
        )
    return compact


def compact_review_state(review: dict[str, Any], quality_feedback: dict[str, Any], rework_requests: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "review_report": {
            "review_status": review.get("review_status"),
            "publication_grade": review.get("publication_grade"),
            "qc_failure_reasons": compact_qc_reasons(review),
            "rework_targets": compact_rework_targets(review),
            "unrecoverable_material_gaps": compact_material_gaps(review),
            "caution_count": len(review.get("caution_findings") or []),
        },
        "quality_feedback": {
            "bounded_rework_result": quality_feedback.get("bounded_rework_result"),
            "issue_count": quality_feedback.get("issue_count"),
            "qc_failure_reasons": compact_qc_reasons(quality_feedback),
            "rework_targets": compact_rework_targets(quality_feedback),
            "unrecoverable_material_gaps": compact_material_gaps(quality_feedback),
        },
        "rework_requests": compact_rework_requests(rework_requests),
        "long_text_omitted": True,
    }


def build_prompt(context: dict[str, Any]) -> str:
    if context.get("prompt_mode") == "policy_safe_minimal":
        return build_policy_safe_minimal_prompt(context)

    paper_id = context["paper_id"]
    owners = ", ".join(context["owner_workers"])
    skill_lines = "\n".join(
        f"- {worker}: `{meta['skill_path']}` ({meta['role']})"
        for worker, meta in context["owner_worker_skills"].items()
    )
    reason_lines = "\n".join(f"- {reason}" for reason in context["failure_reasons"][:12]) or "- See `handoff_context.json`."
    artifact_lines = "\n".join(f"- {name}: `{path}`" for name, path in context["artifacts"]["paths"].items())
    max_rework = context.get("max_rework_attempts", 5)
    obtainable_only = ""
    if context.get("obtainable_only_mode"):
        obtainable_only = f"""
## Obtainable-Only Mode

- Success means: extract every value and claim that is supported by local material, then explicitly mark what local material cannot support.
- Do not keep chasing absent external supplements, unsupported scans, or figure-only exact values after the relevant local paths have been opened.
- If a blocker is a true material gap, write `unrecoverable_material_gaps` and leave the paper non-accepted; the controller will move to the next paper.
- Keep partial recoveries: supported activity/database/mechanism rows should remain recorded even when another layer is `source_conflict` or unresolved.
"""
    return f"""# Codex CLI Re-review Prompt

You are a new Codex CLI paper-review worker for Batch 4-Team. Re-review exactly one paper: `{paper_id}`.

## Controller-Safe Execution Guardrails

- Keep the run narrow: read only the worker skill files listed below, `rework_context/{paper_id}/handoff_context.json`, and the artifact/source paths named in that JSON.
- Do not run broad repository searches. Avoid unbounded `rg`, `find`, `ls -R`, `cat` over large JSONL/CSV/report trees, or any command that can emit thousands of lines.
- If you need search, scope it to one listed source file or one paper-local directory and limit output, for example `rg -n --max-count 20 "MIC|IC50" <listed-path>`.
- This checkout may not contain `AGENTS.md` or a `.git` repository. Do not fail on missing `AGENTS.md`, and do not run `git status` as a completion check.
- Keep tool output small. Prefer Python snippets that print counts, selected keys, and short examples instead of dumping whole JSON/JSONL files.
- Do not inspect unrelated papers. Your write scope is only `papers/{paper_id}/`, `paper_packets/{paper_id}/`, `.miaobi-paper-review/workflows/{paper_id}/`, and paper-specific `reports/{paper_id}.*` gate outputs.
- A valid run must finish with a final assistant message. End with a concise final line starting `DONE {paper_id}` and include one of: `accepted_clean`, `accepted_with_cautions`, `needs_targeted_rework`, or `blocked_missing_primary_material`.
- Do not spend time discovering quality-gate script locations. The only gate commands for this checkout are the exact commands in "Gate Commands To Run" below.

## Immediate Contract

- Read the listed worker skill files before editing.
- Reopen source artifacts from paths; do not trust chat summaries as evidence.
- Fix only the owned layer(s): {owners}.
- Preserve separate layers: material packet, validator contract, semantic gate, publication-grade review.
- Do not mark the paper accepted while any blocking/major issue or open rework ticket remains.
- Write a rework response and rerun gates after repair; if quality is still not controllable, keep the ticket open.
- The initial queue has already been started once. Do not rerun the initial workflow/bootstrap unless the leader explicitly asks for a reset.

## Worker Skills To Load

{skill_lines}

## Single Queue + Bounded Best-Effort Source Recovery Contract

- Treat `rework_context/{paper_id}/handoff_context.json` as the message packet and reopen the source/artifact paths listed there.
- Do best-effort recovery from paper-local materials: XML/NXML, PDF text/tables, OA package members, supplementary files, archives, spreadsheets, office files, images/OCR outputs, locator indexes, and linked database snapshots.
- Use local tools only where relevant to the blocker; prioritize sources that can change the gate result.
- Do not fabricate missing values. If sequence/activity/toxicity/mechanism/database evidence cannot be recovered from local material, write `unrecoverable_material_gaps` with `gap_code`, `source_paths_checked`, `tools_attempted`, `why_unrecoverable`, `impact`, `owner_worker`, and `blocks_publication_grade`.
- Stop after a bounded repair attempt. The controller caps the paper at {max_rework} total rework attempts; if still uncontrollable, mark blocked/unrecoverable and move to the next paper instead of looping.
{obtainable_only}

## Why The Previous QC Failed

{reason_lines}

## Artifact Paths To Reopen

{artifact_lines}

## Gate Commands To Run

Use these exact commands after any repair. Do not try historical paths such as `paper-batch-orchestrator/scripts/...` or `workspace-guide/...`; those are not valid in this scoped checkout.

```bash
python .codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py --root . --manifest reports/{paper_id}.true_rework_queue_manifest.json --json > reports/{paper_id}.owner_worker.semantic_gate.json
python .codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py --root . --manifest reports/{paper_id}.true_rework_queue_manifest.json --json-out reports/{paper_id}.owner_worker.publication_quality.json
```

If the manifest path is absent, create `reports/{paper_id}.true_rework_queue_manifest.json` containing `{{"paper_ids":["{paper_id}"]}}` before running the gates.

## Required Output

1. Repair the owner-layer artifact(s) under the paper-local packet/final/work paths.
2. Update `paper_packets/{paper_id}/rework/rework_responses.jsonl` with what was checked and what remains.
3. Update `papers/{paper_id}/work/review/quality_feedback.json` if final QC still fails, with concrete `qc_failure_reasons`.
4. Rerun semantic and publication gates for this paper.
5. If gates still fail, create/keep a targeted rework ticket with owner worker, omission code, artifact path, and source paths to check.
6. If the local source cannot support the missing value after best effort, record `unrecoverable_material_gaps` and leave the paper non-accepted rather than retrying indefinitely.
"""


def build_policy_safe_minimal_prompt(context: dict[str, Any]) -> str:
    paper_id = context["paper_id"]
    owners = ", ".join(context["owner_workers"])
    skill_lines = "\n".join(
        f"- {worker}: `{meta['skill_path']}` ({meta['role']})"
        for worker, meta in context["owner_worker_skills"].items()
    )
    artifact_lines = "\n".join(f"- {name}: `{path}`" for name, path in context["artifacts"]["paths"].items())
    max_rework = context.get("max_rework_attempts", 5)
    context_name = context.get("context_filename", "policy_safe_handoff_context.json")
    return f"""# Policy-Safe Minimal Codex Re-review Prompt

Review exactly one paper: `{paper_id}`.

This is a source-backed curation repair, not a request to design, optimize, or provide operational biomedical methods. Keep biomedical source content out of the chat/terminal.

## Mandatory Narrow Scope

- Read only the worker skill files listed below and `rework_context/{paper_id}/{context_name}`.
- Use that JSON as a path index. Open only paper-local artifact/source paths named there.
- Do not run broad repository searches, `git status`, unbounded `find`, or large `cat`/JSONL dumps.
- If search is needed, scope to one listed file/directory and print only counts/keys/locator IDs, not source prose.
- Your write scope is only `papers/{paper_id}/`, `paper_packets/{paper_id}/`, `.miaobi-paper-review/workflows/{paper_id}/`, and `reports/{paper_id}.*`.

## Content-Safe Output Rules

- Do not print or quote peptide sequences, detailed protocols, dose-response prose, antiviral/therapeutic narrative text, or long assay snippets.
- Do not paste source text into the final answer. Put recovered evidence in the required JSON artifacts with locators.
- Terminal output should show only short status lines, counts, field names, issue codes, and gate pass/fail results.
- If a local source cannot be reviewed safely or cannot support the missing field, keep the paper non-accepted and record the blocker; do not guess.

## Worker Skills To Load

{skill_lines}

## Repair Target

- Owner layer(s): {owners}.
- Main objective: repair locally supportable activity/toxicity table evidence and then rerun worker-4/worker-6 adjudication as needed.
- Preserve database conflicts and database-only rows; do not convert them to source-verified without a primary-source locator.
- Do not mark accepted while open hard rework targets or strict gate issues remain.
- Stop after a bounded best-effort pass; controller cap is `{max_rework}` attempts.

## Artifact Paths To Reopen

{artifact_lines}

## Gate Commands To Run

Use exactly:

```bash
python .codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py --root . --manifest reports/{paper_id}.true_rework_queue_manifest.json --json > reports/{paper_id}.owner_worker.semantic_gate.json
python .codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py --root . --manifest reports/{paper_id}.true_rework_queue_manifest.json --json-out reports/{paper_id}.owner_worker.publication_quality.json
```

If the manifest path is absent, create `reports/{paper_id}.true_rework_queue_manifest.json` containing `{{"paper_ids":["{paper_id}"]}}`.

## Required Local Writes

1. Update paper-local final/work artifacts for only the source-supported repair.
2. Append `paper_packets/{paper_id}/rework/rework_responses.jsonl` with paths checked, fields repaired, and remaining blockers.
3. If gates still fail, update `papers/{paper_id}/work/review/quality_feedback.json` with concrete codes/owners/artifact paths, not long source prose.
4. Leave unresolved or unsupported facts as conflicts/gaps; do not fabricate values.
5. End final assistant message with `DONE {paper_id} <status>` where status is one of `accepted_clean`, `accepted_with_cautions`, `needs_targeted_rework`, `blocked_missing_primary_material`.
"""

def update_message_bus(repo: Path, paper_id: str, context_path: Path, prompt_path: Path, ticket_ids: list[str]) -> dict[str, Any]:
    bridge = repo / "scripts" / "miaobi_message_bridge.py"
    if not bridge.exists():
        return {"ok": False, "reason": "message bridge missing"}
    common = [sys.executable, str(bridge), "--root", ".miaobi-paper-review"]
    commands = [
        common + [
            "add-artifact",
            "--paper-id",
            paper_id,
            "--kind",
            "rework_context_packet",
            "--path",
            rel(context_path, repo),
            "--state",
            "rework_context_prepared",
            "--status",
            "created",
            "--summary",
            "Context packet for targeted Codex CLI re-review.",
        ],
        common + [
            "add-artifact",
            "--paper-id",
            paper_id,
            "--kind",
            "codex_re_review_prompt",
            "--path",
            rel(prompt_path, repo),
            "--state",
            "rework_context_prepared",
            "--status",
            "created",
            "--summary",
            "Prompt to send to a new Codex CLI worker.",
        ],
        common + [
            "add-log",
            "--paper-id",
            paper_id,
            "--state",
            "rework_context_prepared",
            "--level",
            "info",
            "--category",
            "rework_context",
            "--message",
            "Built targeted rework context packet and Codex CLI prompt.",
            "--path-ref",
            rel(context_path, repo),
            "--path-ref",
            rel(prompt_path, repo),
        ],
    ]
    result = {"ok": True, "commands": []}
    for cmd in commands:
        proc = subprocess.run(cmd, cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result["commands"].append({"returncode": proc.returncode, "stdout": proc.stdout.strip()[-500:], "stderr": proc.stderr.strip()[-500:]})
        if proc.returncode != 0:
            result["ok"] = False
    record_cmd = common + [
        "record-state",
        "--paper-id",
        paper_id,
        "--state",
        "rework_context_prepared",
        "--role",
        "quality_gate",
        "--provider",
        "codex-cli",
        "--model",
        "gpt-5.5",
        "--reasoning-effort",
        "xhigh",
        "--status",
        "needs_rework",
        "--artifact",
        f"rework_context_packet={rel(context_path, repo)}",
        "--artifact",
        f"codex_re_review_prompt={rel(prompt_path, repo)}",
        "--output-summary",
        "Final QC prepared a targeted context packet for upstream re-review.",
        "--chat",
        "QC 已生成定向打回上下文包，可发送给新的 Codex CLI 重新审查。",
    ]
    for ticket_id in ticket_ids:
        record_cmd += ["--rework-ticket", ticket_id]
    proc = subprocess.run(record_cmd, cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result["commands"].append({"returncode": proc.returncode, "stdout": proc.stdout.strip()[-500:], "stderr": proc.stderr.strip()[-500:]})
    if proc.returncode != 0:
        result["ok"] = False
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--audit", default="reports/ten_paper_real_rework_reason_audit_latest.json")
    parser.add_argument("--output-root", default="rework_context")
    parser.add_argument("--max-rework", type=int, default=5)
    parser.add_argument("--obtainable-only", action="store_true", help="Tell workers to extract only locally supportable facts and mark source gaps instead of looping.")
    parser.add_argument(
        "--prompt-mode",
        default="standard",
        choices=["standard", "policy_safe_minimal"],
        help="Use policy_safe_minimal to avoid copying source-rich biomedical text into prompts/context.",
    )
    parser.add_argument("--no-message-bus", action="store_true")
    args = parser.parse_args()

    repo = Path.cwd()
    paper_id = args.paper_id
    audit_entry = load_audit_entry(repo / args.audit, paper_id)
    artifacts = collect_artifacts(repo, paper_id)
    gate = collect_gate_failures(repo, paper_id)
    review = read_json(repo / "papers" / paper_id / "final" / "review_report.json")
    quality_feedback = read_json(repo / "papers" / paper_id / "work" / "review" / "quality_feedback.json")
    rework_requests = read_jsonl(repo / "paper_packets" / paper_id / "rework" / "rework_requests.jsonl")

    failure_reasons: list[Any] = []
    failure_reasons.extend(audit_entry.get("real_rework_reasons") or [])
    failure_reasons.extend(item.get("reason") for item in quality_feedback.get("qc_failure_reasons") or [] if isinstance(item, dict))
    failure_reasons.extend(item.get("reason") for item in review.get("qc_failure_reasons") or [] if isinstance(item, dict))
    failure_reasons = [reason for reason in failure_reasons if reason]

    owner_workers = owner_workers_from_reasons(failure_reasons, gate, quality_feedback)
    owner_worker_skills = {worker: WORKER_SKILLS[worker] for worker in owner_workers if worker in WORKER_SKILLS}
    ticket_ids = [str(row.get("ticket_id")) for row in rework_requests if row.get("ticket_id")]

    out_dir = repo / args.output_root / paper_id
    policy_safe = args.prompt_mode == "policy_safe_minimal"
    context_path = out_dir / ("policy_safe_handoff_context.json" if policy_safe else "handoff_context.json")
    prompt_path = out_dir / ("CODEX_REVIEW_PROMPT_POLICY_SAFE.md" if policy_safe else "CODEX_REVIEW_PROMPT.md")
    manifest_path = out_dir / "artifact_manifest.json"

    common_context = {
        "generated_at": now_iso(),
        "paper_id": paper_id,
        "max_rework_attempts": args.max_rework,
        "prompt_mode": args.prompt_mode,
        "context_filename": context_path.name,
        "prompt_filename": prompt_path.name,
        "purpose": "targeted rework context packet for a new Codex CLI worker",
        "queue_policy": {
            "start_once": True,
            "retry_from_rework_context_only": True,
            "advance_on_unrecoverable_gap": True,
        },
        "source_roots": artifacts["source_roots"],
        "source_inventory": collect_source_inventory(repo, paper_id),
        "manual_digitization_context": collect_manual_digitization_context(repo, paper_id),
        "artifacts": artifacts,
        "owner_workers": owner_workers,
        "owner_worker_skills": owner_worker_skills,
        "supporting_worker_skills": WORKER_SKILLS,
        "do_not_copy_long_source_text": True,
    }

    if policy_safe:
        context = {
            **common_context,
            "purpose": "policy-safe minimal targeted rework context packet for a new Codex CLI worker",
            "policy_safe_minimal_protocol": POLICY_SAFE_MINIMAL_PROTOCOL,
            "obtainable_only_mode": args.obtainable_only,
            "obtainable_only_protocol": OBTAINABLE_ONLY_PROTOCOL if args.obtainable_only else {},
            "bounded_rework_protocol": {**BOUNDED_REWORK_PROTOCOL, "max_rework_attempts": args.max_rework},
            "unrecoverable_material_gap_schema": UNRECOVERABLE_MATERIAL_GAP_SCHEMA,
            "gate_failures": compact_gate_failures(gate),
            "review_state": compact_review_state(review, quality_feedback, rework_requests),
            "failure_reason_count": len(failure_reasons),
            "failure_reason_text_omitted_for_policy_safe_prompt": True,
            "audit_entry_omitted_for_policy_safe_prompt": True,
            "codex_cli_command": (
                f"codex exec --skip-git-repo-check -C {repo} -m gpt-5.5 "
                f"-o reports/{paper_id}.codex_re_review_last_message.md - < {rel(prompt_path, repo)}"
            ),
        }
    else:
        context = {
            **common_context,
        "best_effort_source_protocol": BEST_EFFORT_SOURCE_PROTOCOL,
        "obtainable_only_mode": args.obtainable_only,
        "obtainable_only_protocol": OBTAINABLE_ONLY_PROTOCOL if args.obtainable_only else {},
        "bounded_rework_protocol": {**BOUNDED_REWORK_PROTOCOL, "max_rework_attempts": args.max_rework},
        "unrecoverable_material_gap_schema": UNRECOVERABLE_MATERIAL_GAP_SCHEMA,
        "gate_failures": gate,
        "audit_entry": audit_entry,
        "failure_reasons": failure_reasons,
        "rework_requests": rework_requests,
        "quality_feedback": quality_feedback,
        "codex_cli_command": (
            f"codex exec --skip-git-repo-check -C {repo} -m gpt-5.5 -s danger-full-access "
            f"-o reports/{paper_id}.codex_re_review_last_message.md - < {rel(prompt_path, repo)}"
        ),
        }
    write_json(context_path, context)
    prompt_path.write_text(build_prompt(context), encoding="utf-8")
    write_json(manifest_path, {"paper_id": paper_id, "context": rel(context_path, repo), "prompt": rel(prompt_path, repo), "artifacts": artifacts["paths"]})

    message_bus = {"ok": None, "skipped": True}
    if not args.no_message_bus:
        message_bus = update_message_bus(repo, paper_id, context_path, prompt_path, ticket_ids)
        context["message_bus_update"] = message_bus
        write_json(context_path, context)

    print(json.dumps({
        "ok": True,
        "paper_id": paper_id,
        "context": rel(context_path, repo),
        "prompt": rel(prompt_path, repo),
        "owner_workers": owner_workers,
        "failure_reason_count": len(failure_reasons),
        "message_bus_update": message_bus,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
