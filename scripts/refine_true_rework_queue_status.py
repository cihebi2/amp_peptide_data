#!/usr/bin/env python3
"""Build a refined status report from true-rework queue lane summaries.

The lane summaries are evidence artifacts and are not mutated by this script.
It adds an interpretation layer that separates clean initial acceptance,
post-rework acceptance, source/material blockers, process timeouts, and
infrastructure retry exhaustion.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_CATALOG: dict[str, dict[str, str]] = {
    "accepted_clean_initial_gate_pass": {
        "category": "accepted_clean",
        "meaning": "Strict gates already passed before owner-worker rework.",
        "next_action": "none",
    },
    "accepted_after_rework_attempt1": {
        "category": "accepted_after_rework",
        "meaning": "One owner-worker re-review repaired the paper and strict gates passed.",
        "next_action": "sample_audit_only",
    },
    "accepted_after_rework_attempt1_with_infra_retry": {
        "category": "accepted_after_rework_with_infra_noise",
        "meaning": "One owner-worker re-review eventually passed after transient Codex/API/process retry noise.",
        "next_action": "sample_audit_plus_infra_log_check",
    },
    "accepted_after_rework_multi_attempt": {
        "category": "accepted_after_rework",
        "meaning": "More than one bounded rework attempt was needed before strict gates passed.",
        "next_action": "targeted_sample_audit",
    },
    "accepted_after_rework_multi_attempt_with_infra_retry": {
        "category": "accepted_after_rework_with_infra_noise",
        "meaning": "Multiple rework attempts plus transient infra retries were needed before strict gates passed.",
        "next_action": "targeted_sample_audit_plus_infra_log_check",
    },
    "blocked_process_timeout_1800s_retryable": {
        "category": "blocked_process_timeout",
        "meaning": "Owner-worker hit the 1800s watchdog; this is retryable and not proof that material is absent.",
        "next_action": "retry_with_longer_watchdog_or_narrower_prompt",
    },
    "blocked_process_timeout_retryable": {
        "category": "blocked_process_timeout",
        "meaning": "Owner-worker hit the configured watchdog; this is retryable and not proof that material is absent.",
        "next_action": "retry_with_longer_watchdog_or_narrower_prompt",
    },
    "blocked_source_gap_figure_chart_exact_value": {
        "category": "blocked_source_gap",
        "meaning": "Remaining exact values are figure/chart-only or not safely promotable from local structured material.",
        "next_action": "retry_only_with_digitization_or_external_source",
    },
    "blocked_source_gap_missing_external_supplement": {
        "category": "blocked_source_gap",
        "meaning": "A specific supplementary source/table is absent or only present as a non-data placeholder.",
        "next_action": "retry_only_after_source_staging",
    },
    "blocked_parser_gap_activity_table": {
        "category": "blocked_parser_or_manual_extraction_gap",
        "meaning": "Activity/toxicity rows are present or expected but unsafe under current parser/table handling.",
        "next_action": "retry_with_worker2_table_shape_or_manual_vision_fallback",
    },
    "blocked_quality_gate_rework_cap_unresolved": {
        "category": "blocked_quality_gate_unresolved",
        "meaning": "Strict gates remained blocked after the bounded obtainable-only rework cap.",
        "next_action": "retry_only_with_more_specific_owner_context",
    },
    "blocked_model_prompt_safety_restriction_quality_gates_open": {
        "category": "infrastructure_model_policy_blocked",
        "meaning": (
            "Codex owner-worker hit a model prompt/content safety restriction while strict "
            "scientific gates remained open; this is not proof that source material is absent."
        ),
        "next_action": "retry_with_policy_safe_minimized_context_or_manual_queue",
    },
    "blocked_worker_nonzero_strict_gates_open": {
        "category": "infrastructure_worker_nonzero_with_quality_gates_open",
        "meaning": (
            "Codex owner-worker exited non-zero and strict gates still failed after bounded "
            "best-effort review; inspect worker logs before treating this as a scientific blocker."
        ),
        "next_action": "defer_to_infrastructure_recovery_queue",
    },
    "infrastructure_retry_exhausted_api_or_network": {
        "category": "infrastructure_retry_exhausted",
        "meaning": "Codex/API/network-like failures exhausted the configured infra retry cap.",
        "next_action": "defer_to_infrastructure_recovery_queue",
    },
    "infrastructure_retry_exhausted_worker_nonzero_exit": {
        "category": "infrastructure_retry_exhausted",
        "meaning": "Codex worker exited non-zero until the configured infra retry cap was exhausted.",
        "next_action": "defer_to_infrastructure_recovery_queue",
    },
    "infrastructure_retry_exhausted_worker_interrupted": {
        "category": "infrastructure_retry_exhausted",
        "meaning": "Codex worker interruption exhausted the configured infra retry cap.",
        "next_action": "defer_to_infrastructure_recovery_queue",
    },
    "infrastructure_retry_exhausted_mixed": {
        "category": "infrastructure_retry_exhausted",
        "meaning": "Multiple infrastructure failure families exhausted the configured retry cap.",
        "next_action": "defer_to_infrastructure_recovery_queue",
    },
    "infrastructure_retry_exhausted_paper_runtime": {
        "category": "infrastructure_retry_exhausted",
        "meaning": "Per-paper controller/runtime exceptions exhausted the configured retry cap.",
        "next_action": "defer_to_infrastructure_recovery_queue",
    },
    "infrastructure_initial_queue_failed": {
        "category": "infrastructure_failed",
        "meaning": "Initial workflow/bootstrap failed before owner-worker review could run.",
        "next_action": "defer_to_infrastructure_recovery_queue",
    },
    "unclassified_queue_status": {
        "category": "unclassified",
        "meaning": "No refined rule matched this queue result.",
        "next_action": "inspect_result_payload",
    },
}


FOLLOWUP_QUEUE_CATALOG: dict[str, dict[str, str]] = {
    "infra_recovery": {
        "meaning": "Infrastructure/API/bootstrap/runtime failures that should be retried outside the paper-quality lane.",
        "default_next_action": "retry_after_infrastructure_stabilization",
    },
    "watchdog_retry": {
        "meaning": "Owner-worker watchdog timeouts that need a longer watchdog or a narrower prompt.",
        "default_next_action": "retry_with_longer_watchdog_or_narrower_owner_prompt",
    },
    "source_staging_needed": {
        "meaning": "Missing external supplement or figure/chart exact-value blockers that require source staging or digitization.",
        "default_next_action": "stage_missing_source_or_digitize_chart_then_retry",
    },
    "parser_manual_extraction_needed": {
        "meaning": "Activity/table extraction blockers that need parser repair or manual/vision fallback.",
        "default_next_action": "repair_table_parser_or_manual_extract_then_retry",
    },
    "owner_context_rework_needed": {
        "meaning": "Quality gates remain unresolved after bounded rework and need more specific owner context.",
        "default_next_action": "build_more_specific_owner_context_then_retry",
    },
    "safe_prompt_rework_needed": {
        "meaning": (
            "Owner-worker review was interrupted by model prompt/content safety restrictions; "
            "retry with a minimized, non-operational paper-evidence prompt or route to manual review."
        ),
        "default_next_action": "retry_with_policy_safe_minimized_context_or_manual_queue",
    },
}

ACCEPTED_SAMPLE_AUDIT_POLICY = {
    "meaning": (
        "Accepted papers are not automatically clean; audit all accepted rows with "
        "infra retry or multi-attempt evidence, plus a deterministic baseline sample."
    ),
    "default_next_action": "run_sample_audit_before_publication_grade_claim",
    "does_not_reopen_by_itself": True,
}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def gate_passed(result: dict[str, Any], gate_name: str) -> bool:
    for attempt in result.get("attempts") or []:
        if (attempt.get(gate_name) or {}).get("passed") is True:
            return True
    return False


def has_worker_result(result: dict[str, Any]) -> bool:
    return any(bool(attempt.get("worker_result")) for attempt in result.get("attempts") or [])


def infra_family(codes: list[str]) -> str:
    normalized = {str(code) for code in codes if code}
    if len(normalized) > 1:
        return "mixed"
    code = next(iter(normalized), "")
    if code == "codex_api_or_network_error":
        return "api_or_network"
    if code == "codex_worker_nonzero_exit":
        return "worker_nonzero_exit"
    if code == "codex_worker_interrupted":
        return "worker_interrupted"
    return "mixed" if code else "worker_nonzero_exit"


def attempt_gate_issue_codes(result: dict[str, Any]) -> list[str]:
    codes: set[str] = set()
    for attempt in result.get("attempts") or []:
        for gate_name in ("gate_after", "gate_before"):
            gate = attempt.get(gate_name) or {}
            for code in gate.get("semantic_issue_codes") or []:
                if code:
                    codes.add(str(code))
            for code in (gate.get("publication_risk_counts") or {}).keys():
                if code:
                    codes.add(str(code))
    for code in result.get("semantic_issue_codes") or []:
        if code:
            codes.add(str(code))
    for code in result.get("qc_codes") or []:
        if code:
            codes.add(str(code))
    for code in result.get("gap_codes") or []:
        if code:
            codes.add(str(code))
    return sorted(codes)


def attempt_worker_reason_codes(result: dict[str, Any]) -> list[str]:
    codes: set[str] = set()
    for code in result.get("worker_infra_reason_codes") or []:
        if code:
            codes.add(str(code))
    for attempt in result.get("attempts") or []:
        worker = attempt.get("worker_result") or {}
        if worker.get("infra_reason_code"):
            codes.add(str(worker.get("infra_reason_code")))
        for run in worker.get("infra_runs") or []:
            if run.get("infra_reason_code"):
                codes.add(str(run.get("infra_reason_code")))
    return sorted(codes)


def attempt_stderr_text(result: dict[str, Any]) -> str:
    parts: list[str] = []
    for attempt in result.get("attempts") or []:
        worker = attempt.get("worker_result") or {}
        for key in ("stderr_tail", "stdout_tail"):
            value = worker.get(key)
            if value:
                parts.append(str(value))
        for run in worker.get("infra_runs") or []:
            for key in ("stderr_tail", "stdout_tail"):
                value = run.get(key)
                if value:
                    parts.append(str(value))
    return "\n".join(parts)


def has_model_safety_restriction(result: dict[str, Any]) -> bool:
    text = attempt_stderr_text(result).lower()
    return (
        "invalid prompt" in text
        and "limited access to this content for safety reasons" in text
    )


def refined_for_result(result: dict[str, Any]) -> dict[str, Any]:
    terminal = str(result.get("terminal_status") or "")
    status = str(result.get("result_status") or terminal)
    attempt_count = as_int(result.get("attempt_count"), len(result.get("attempts") or []))
    infra_retry_count = as_int(result.get("worker_infra_retry_count"))
    watchdog_seconds = as_int(result.get("watchdog_seconds"))
    before_passed = gate_passed(result, "gate_before")
    evidence_codes = attempt_gate_issue_codes(result)
    worker_reason_codes = attempt_worker_reason_codes(result)

    refined_status = "unclassified_queue_status"
    reason_code = status or terminal or "unknown"

    if status.startswith("accepted") or terminal.startswith("accepted"):
        if terminal == "accepted_before_worker_rework" or (before_passed and not has_worker_result(result)):
            refined_status = "accepted_clean_initial_gate_pass"
            reason_code = "clean_initial_gate_pass"
        elif attempt_count > 1 and infra_retry_count > 0:
            refined_status = "accepted_after_rework_multi_attempt_with_infra_retry"
            reason_code = "strict_gates_passed_after_multi_rework_with_infra_retry"
        elif attempt_count > 1:
            refined_status = "accepted_after_rework_multi_attempt"
            reason_code = "strict_gates_passed_after_multi_rework"
        elif infra_retry_count > 0:
            refined_status = "accepted_after_rework_attempt1_with_infra_retry"
            reason_code = "strict_gates_passed_after_single_rework_with_infra_retry"
        else:
            refined_status = "accepted_after_rework_attempt1"
            reason_code = "strict_gates_passed_after_single_rework"
    elif status == "blocked_watchdog_timeout_retryable":
        refined_status = (
            "blocked_process_timeout_1800s_retryable"
            if watchdog_seconds == 1800
            else "blocked_process_timeout_retryable"
        )
        reason_code = "codex_worker_timeout"
    elif status == "blocked_figure_chart_value_gap":
        refined_status = "blocked_source_gap_figure_chart_exact_value"
        reason_code = "figure_or_chart_exact_value_unrecoverable"
    elif status == "blocked_missing_external_supplement":
        refined_status = "blocked_source_gap_missing_external_supplement"
        reason_code = "missing_external_supplement"
    elif status == "blocked_activity_table_extraction_gap":
        refined_status = "blocked_parser_gap_activity_table"
        reason_code = "activity_table_rows_not_safely_extracted"
    elif status == "blocked_rework_cap_unresolved":
        refined_status = "blocked_quality_gate_rework_cap_unresolved"
        reason_code = "bounded_rework_limit_reached"
    elif status == "blocked_after_best_effort" or terminal == "blocked_after_best_effort":
        if has_model_safety_restriction(result):
            refined_status = "blocked_model_prompt_safety_restriction_quality_gates_open"
            reason_code = "codex_prompt_safety_restriction_with_open_quality_gates"
        elif worker_reason_codes:
            refined_status = "blocked_worker_nonzero_strict_gates_open"
            reason_code = "codex_worker_nonzero_with_open_quality_gates"
        elif any(code in evidence_codes for code in ("missing_activity_records", "missing_target_species")):
            refined_status = "blocked_parser_gap_activity_table"
            reason_code = "activity_or_target_rows_not_safely_extracted"
        elif evidence_codes:
            refined_status = "blocked_quality_gate_rework_cap_unresolved"
            reason_code = "strict_quality_gate_issues_remain"
    elif status == "infrastructure_codex_worker_retry_exhausted":
        family = infra_family(result.get("worker_infra_reason_codes") or [])
        refined_status = f"infrastructure_retry_exhausted_{family}"
        reason_code = "codex_worker_infra_retry_exhausted"
    elif status == "infrastructure_paper_runtime_retry_exhausted":
        refined_status = "infrastructure_retry_exhausted_paper_runtime"
        reason_code = "paper_runtime_exception_retry_exhausted"
    elif status in {"infrastructure_initial_queue_failed", "infrastructure_missing_initial_queue"}:
        refined_status = "infrastructure_initial_queue_failed"
        reason_code = status

    catalog = STATUS_CATALOG[refined_status]
    return {
        "refined_status": refined_status,
        "refined_category": catalog["category"],
        "refined_reason_code": reason_code,
        "refined_reason_summary": catalog["meaning"],
        "recommended_next_action": catalog["next_action"],
        "refined_evidence_codes": evidence_codes,
        "refined_worker_reason_codes": worker_reason_codes,
        "clean_initial_gate_pass": refined_status == "accepted_clean_initial_gate_pass",
        "post_rework_acceptance": refined_status.startswith("accepted_after_rework"),
    }


def existing_refined_for_result(result: dict[str, Any]) -> dict[str, Any] | None:
    """Return a previously computed refined status without re-inferencing it.

    `build_report()` stores flattened paper rows. Follow-up and accepted-audit
    builders may receive those rows later; re-running raw-result inference on a
    flattened row loses attempt stderr/gate detail and can downgrade precise
    statuses back to generic worker-nonzero buckets.
    """
    refined_status = str(result.get("refined_status") or "")
    if refined_status not in STATUS_CATALOG:
        return None
    catalog = STATUS_CATALOG[refined_status]
    return {
        "refined_status": refined_status,
        "refined_category": str(result.get("refined_category") or catalog["category"]),
        "refined_reason_code": str(result.get("refined_reason_code") or refined_status),
        "refined_reason_summary": str(result.get("refined_reason_summary") or catalog["meaning"]),
        "recommended_next_action": str(result.get("recommended_next_action") or catalog["next_action"]),
        "refined_evidence_codes": result.get("refined_evidence_codes") or [],
        "refined_worker_reason_codes": result.get("refined_worker_reason_codes") or [],
        "clean_initial_gate_pass": refined_status == "accepted_clean_initial_gate_pass",
        "post_rework_acceptance": refined_status.startswith("accepted_after_rework"),
    }


def attach_refined_statuses_to_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Mutate and return a queue summary with refined status fields/counts."""
    refined_status_counts: Counter[str] = Counter()
    refined_category_counts: Counter[str] = Counter()
    recommended_next_action_counts: Counter[str] = Counter()
    clean_initial_pass_count = 0
    post_rework_acceptance_count = 0
    blocked_or_infrastructure_count = 0

    for result in summary.get("results") or []:
        if not isinstance(result, dict):
            continue
        refined = existing_refined_for_result(result) or refined_for_result(result)
        result.update(refined)
        refined_status_counts[refined["refined_status"]] += 1
        refined_category_counts[refined["refined_category"]] += 1
        recommended_next_action_counts[refined["recommended_next_action"]] += 1
        if refined["clean_initial_gate_pass"]:
            clean_initial_pass_count += 1
        if refined["post_rework_acceptance"]:
            post_rework_acceptance_count += 1
        if not str(refined["refined_status"]).startswith("accepted"):
            blocked_or_infrastructure_count += 1

    summary["refined_status_counts"] = dict(sorted(refined_status_counts.items()))
    summary["refined_category_counts"] = dict(sorted(refined_category_counts.items()))
    summary["recommended_next_action_counts"] = dict(sorted(recommended_next_action_counts.items()))
    summary["clean_initial_pass_count"] = clean_initial_pass_count
    summary["post_rework_acceptance_count"] = post_rework_acceptance_count
    summary["blocked_or_infrastructure_count"] = blocked_or_infrastructure_count
    summary["status_catalog"] = STATUS_CATALOG
    quality_control = summary.setdefault("quality_control", {})
    if isinstance(quality_control, dict):
        quality_control["refined_status"] = (
            "refined_status/refined_category are first-class queue outputs; "
            "accepted_after_rework must not be reported as clean initial acceptance."
        )
        quality_control["followup_queues"] = FOLLOWUP_QUEUE_CATALOG
    return summary


def followup_queue_name(row: dict[str, Any]) -> str | None:
    refined_status = str(row.get("refined_status") or "")
    refined_category = str(row.get("refined_category") or "")
    if refined_category in {"infrastructure_retry_exhausted", "infrastructure_failed"}:
        return "infra_recovery"
    if refined_category == "blocked_process_timeout":
        return "watchdog_retry"
    if refined_status in {
        "blocked_source_gap_figure_chart_exact_value",
        "blocked_source_gap_missing_external_supplement",
    }:
        return "source_staging_needed"
    if refined_status == "blocked_parser_gap_activity_table":
        return "parser_manual_extraction_needed"
    if refined_status == "blocked_quality_gate_rework_cap_unresolved":
        return "owner_context_rework_needed"
    if refined_category == "infrastructure_model_policy_blocked":
        return "safe_prompt_rework_needed"
    if refined_category == "infrastructure_worker_nonzero_with_quality_gates_open":
        return "infra_recovery"
    return None


def followup_item_from_result(result: dict[str, Any], source_summary_path: str | None = None) -> dict[str, Any]:
    return {
        "paper_id": result.get("paper_id"),
        "terminal_status": result.get("terminal_status"),
        "result_status": result.get("result_status"),
        "result_category": result.get("result_category"),
        "refined_status": result.get("refined_status"),
        "refined_category": result.get("refined_category"),
        "refined_reason_code": result.get("refined_reason_code"),
        "refined_reason_summary": result.get("refined_reason_summary"),
        "recommended_next_action": result.get("recommended_next_action"),
        "retryability": result.get("retryability"),
        "attempt_count": result.get("attempt_count"),
        "max_rework_attempts": result.get("max_rework_attempts"),
        "worker_infra_retry_count": result.get("worker_infra_retry_count"),
        "worker_infra_reason_codes": result.get("worker_infra_reason_codes") or [],
        "watchdog_seconds": result.get("watchdog_seconds"),
        "qc_codes": result.get("qc_codes") or [],
        "gap_codes": result.get("gap_codes") or [],
        "semantic_issue_codes": result.get("semantic_issue_codes") or [],
        "refined_evidence_codes": result.get("refined_evidence_codes") or [],
        "refined_worker_reason_codes": result.get("refined_worker_reason_codes") or [],
        "manifest": result.get("manifest"),
        "source_summary": source_summary_path,
    }


def build_followup_queue_manifests(
    summary: dict[str, Any],
    *,
    source_summary_path: str | None = None,
    run_label: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Build follow-up queue manifests from a refined queue summary."""
    attach_refined_statuses_to_summary(summary)
    queues: dict[str, list[dict[str, Any]]] = {name: [] for name in FOLLOWUP_QUEUE_CATALOG}
    for result in summary.get("results") or []:
        if not isinstance(result, dict):
            continue
        queue_name = followup_queue_name(result)
        if queue_name:
            queues[queue_name].append(followup_item_from_result(result, source_summary_path))

    generated_at = now_utc()
    manifests: dict[str, dict[str, Any]] = {}
    for queue_name, items in queues.items():
        catalog = FOLLOWUP_QUEUE_CATALOG[queue_name]
        manifests[queue_name] = {
            "generated_at": generated_at,
            "queue_name": queue_name,
            "run_label": run_label,
            "source_summary": source_summary_path,
            "completion_claim": "followup_queue_manifest_not_publication_grade_acceptance",
            "queue_policy": catalog,
            "paper_count": len(items),
            "paper_ids": [str(item.get("paper_id")) for item in items if item.get("paper_id")],
            "items": items,
        }
    return manifests


def write_followup_queue_manifests(
    summary: dict[str, Any],
    *,
    out_dir: Path,
    prefix: str,
    source_summary_path: str | None = None,
    run_label: str | None = None,
) -> dict[str, str]:
    manifests = build_followup_queue_manifests(
        summary,
        source_summary_path=source_summary_path,
        run_label=run_label,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    for queue_name, manifest in manifests.items():
        path = out_dir / f"{prefix}_{queue_name}.json"
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        latest = out_dir / f"{prefix}_{queue_name}_latest.json"
        latest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        paths[queue_name] = str(path)
    return paths


def stable_sample_key(paper_id: str, seed: str) -> str:
    return hashlib.sha256(f"{seed}:{paper_id}".encode("utf-8")).hexdigest()


def build_accepted_sample_audit_manifest(
    summary: dict[str, Any],
    *,
    source_summary_path: str | None = None,
    run_label: str | None = None,
    baseline_sample_size: int = 25,
    seed: str = "accepted-sample-audit-v1",
) -> dict[str, Any]:
    """Create a deterministic QA sample from accepted results.

    The risk sample is exhaustive for accepted results with infra noise or
    multiple rework attempts. The baseline sample is deterministic so future
    agents can reproduce which accepted papers were selected.
    """
    attach_refined_statuses_to_summary(summary)
    accepted = [
        result
        for result in summary.get("results") or []
        if isinstance(result, dict) and str(result.get("refined_status") or "").startswith("accepted")
    ]
    risk_rows: list[dict[str, Any]] = []
    baseline_pool: list[dict[str, Any]] = []
    for result in accepted:
        refined_status = str(result.get("refined_status") or "")
        if (
            "with_infra_retry" in refined_status
            or "multi_attempt" in refined_status
            or int(result.get("worker_infra_retry_count") or 0) > 0
            or int(result.get("attempt_count") or 0) > 1
        ):
            risk_rows.append(result)
        else:
            baseline_pool.append(result)

    baseline_sorted = sorted(
        baseline_pool,
        key=lambda row: stable_sample_key(str(row.get("paper_id") or ""), seed),
    )
    baseline_rows = baseline_sorted[: max(0, baseline_sample_size)]

    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    for reason, rows in (("accepted_risk_audit", risk_rows), ("accepted_baseline_sample", baseline_rows)):
        for result in rows:
            paper_id = str(result.get("paper_id") or "")
            if not paper_id or paper_id in seen:
                continue
            seen.add(paper_id)
            items.append(
                {
                    "paper_id": paper_id,
                    "audit_reason": reason,
                    "terminal_status": result.get("terminal_status"),
                    "result_status": result.get("result_status"),
                    "refined_status": result.get("refined_status"),
                    "refined_category": result.get("refined_category"),
                    "attempt_count": result.get("attempt_count"),
                    "worker_infra_retry_count": result.get("worker_infra_retry_count"),
                    "worker_infra_reason_codes": result.get("worker_infra_reason_codes") or [],
                    "recommended_next_action": result.get("recommended_next_action"),
                    "qc_codes": result.get("qc_codes") or [],
                    "semantic_issue_codes": result.get("semantic_issue_codes") or [],
                    "source_summary": source_summary_path,
                    "sample_key": stable_sample_key(paper_id, seed),
                    "audit_requirements": [
                        "reopen paper-local final/review_report.json",
                        "verify worker-6 provenance and checked_inputs are paper-specific",
                        "rerun semantic and publication-quality gates without allow-risk shortcuts",
                        "confirm accepted_after_rework is not reported as accepted_clean",
                    ],
                }
            )

    return {
        "generated_at": now_utc(),
        "queue_name": "accepted_sample_audit",
        "run_label": run_label,
        "source_summary": source_summary_path,
        "completion_claim": "accepted_sample_audit_manifest_not_publication_grade_acceptance",
        "queue_policy": ACCEPTED_SAMPLE_AUDIT_POLICY,
        "accepted_total": len(accepted),
        "risk_sample_count": len({str(row.get("paper_id") or "") for row in risk_rows if row.get("paper_id")}),
        "baseline_sample_size": baseline_sample_size,
        "paper_count": len(items),
        "paper_ids": [item["paper_id"] for item in items],
        "items": items,
    }


def write_accepted_sample_audit_manifest(
    summary: dict[str, Any],
    *,
    out_dir: Path,
    prefix: str,
    source_summary_path: str | None = None,
    run_label: str | None = None,
    baseline_sample_size: int = 25,
    seed: str = "accepted-sample-audit-v1",
) -> str:
    manifest = build_accepted_sample_audit_manifest(
        summary,
        source_summary_path=source_summary_path,
        run_label=run_label,
        baseline_sample_size=baseline_sample_size,
        seed=seed,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{prefix}_accepted_sample_audit.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    latest = out_dir / f"{prefix}_accepted_sample_audit_latest.json"
    latest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(path)


def lane_number(path: Path) -> int | None:
    name = path.name
    marker = "lane"
    if marker not in name:
        return None
    tail = name.split(marker, 1)[1]
    digits = []
    for char in tail:
        if char.isdigit():
            digits.append(char)
        else:
            break
    return int("".join(digits)) if digits else None


def build_report(paths: list[Path]) -> dict[str, Any]:
    refined_rows: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        lane = lane_number(path)
        results = data.get("results") or []
        source_summaries.append(
            {
                "lane": lane,
                "path": str(path),
                "ok": data.get("ok"),
                "generated_at": data.get("generated_at"),
                "paper_count": len(results),
                "terminal_status_counts": data.get("terminal_status_counts") or {},
                "result_status_counts": data.get("result_status_counts") or {},
            }
        )
        for result in results:
            refined = refined_for_result(result)
            refined_rows.append(
                {
                    "paper_id": result.get("paper_id"),
                    "lane": lane,
                    "terminal_status": result.get("terminal_status"),
                    "result_status": result.get("result_status"),
                    "result_category": result.get("result_category"),
                    "attempt_count": result.get("attempt_count"),
                    "worker_infra_retry_count": result.get("worker_infra_retry_count"),
                    "worker_infra_reason_codes": result.get("worker_infra_reason_codes") or [],
                    "watchdog_seconds": result.get("watchdog_seconds"),
                    "retryability": result.get("retryability"),
                    "qc_codes": result.get("qc_codes") or [],
                    "gap_codes": result.get("gap_codes") or [],
                    "semantic_issue_codes": result.get("semantic_issue_codes") or [],
                    **refined,
                }
            )

    refined_status_counts = Counter(row["refined_status"] for row in refined_rows)
    refined_category_counts = Counter(row["refined_category"] for row in refined_rows)
    terminal_status_counts = Counter(row["terminal_status"] for row in refined_rows)
    result_status_counts = Counter(row["result_status"] for row in refined_rows)
    next_action_counts = Counter(row["recommended_next_action"] for row in refined_rows)

    accepted_rows = [row for row in refined_rows if row["refined_status"].startswith("accepted")]
    blocked_rows = [row for row in refined_rows if not row["refined_status"].startswith("accepted")]

    return {
        "generated_at": now_utc(),
        "source_lane_summary_count": len(paths),
        "source_lane_summaries": source_summaries,
        "paper_count": len(refined_rows),
        "completion_claim": "refined_status_interpretation_not_blanket_publication_grade_clean_acceptance",
        "status_catalog": STATUS_CATALOG,
        "terminal_status_counts": dict(sorted(terminal_status_counts.items())),
        "result_status_counts": dict(sorted(result_status_counts.items())),
        "refined_status_counts": dict(sorted(refined_status_counts.items())),
        "refined_category_counts": dict(sorted(refined_category_counts.items())),
        "recommended_next_action_counts": dict(sorted(next_action_counts.items())),
        "accepted_count": len(accepted_rows),
        "blocked_or_infrastructure_count": len(blocked_rows),
        "clean_initial_pass_count": refined_status_counts.get("accepted_clean_initial_gate_pass", 0),
        "post_rework_acceptance_count": sum(
            count for status, count in refined_status_counts.items() if status.startswith("accepted_after_rework")
        ),
        "followup_queue_catalog": FOLLOWUP_QUEUE_CATALOG,
        "papers": refined_rows,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Refined True-Rework Queue Status",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- source_lane_summary_count: `{report['source_lane_summary_count']}`",
        f"- paper_count: `{report['paper_count']}`",
        f"- completion_claim: `{report['completion_claim']}`",
        f"- clean_initial_pass_count: `{report['clean_initial_pass_count']}`",
        f"- post_rework_acceptance_count: `{report['post_rework_acceptance_count']}`",
        f"- blocked_or_infrastructure_count: `{report['blocked_or_infrastructure_count']}`",
        "",
        "## Refined Status Counts",
    ]
    for status, count in report["refined_status_counts"].items():
        catalog = report["status_catalog"].get(status, {})
        lines.append(f"- `{status}`: `{count}` - {catalog.get('meaning', '')}")
    lines.extend(["", "## Refined Category Counts"])
    for category, count in report["refined_category_counts"].items():
        lines.append(f"- `{category}`: `{count}`")
    lines.extend(["", "## Recommended Next Actions"])
    for action, count in report["recommended_next_action_counts"].items():
        lines.append(f"- `{action}`: `{count}`")
    if report.get("followup_queue_manifest_paths"):
        lines.extend(["", "## Follow-Up Queue Manifests"])
        for queue_name, queue_path in sorted(report["followup_queue_manifest_paths"].items()):
            lines.append(f"- `{queue_name}`: `{queue_path}`")
    if report.get("accepted_sample_audit_manifest_path"):
        lines.extend(["", "## Accepted Sample Audit"])
        lines.append(f"- `accepted_sample_audit`: `{report['accepted_sample_audit_manifest_path']}`")
    lines.extend(["", "## Lane Sources"])
    for lane in sorted(report["source_lane_summaries"], key=lambda item: item.get("lane") or 0):
        lines.append(
            f"- lane{lane.get('lane')}: papers=`{lane.get('paper_count')}` "
            f"path=`{lane.get('path')}`"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lane-glob",
        default="reports/true_rework_queue_queue_next500_1800_lane*_latest.json",
        help="Glob for lane latest summary JSON files.",
    )
    parser.add_argument(
        "--out-json",
        default="reports/true_rework_queue_next500_obtainable_refined_status_20260505.json",
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--out-md",
        default="reports/true_rework_queue_next500_obtainable_refined_status_20260505.md",
        help="Output Markdown report path.",
    )
    parser.add_argument(
        "--followup-dir",
        default="reports/followup_queues",
        help="Directory for generated follow-up queue manifests.",
    )
    parser.add_argument(
        "--followup-prefix",
        default="true_rework_queue_next500_obtainable_20260505",
        help="Filename prefix for generated follow-up queue manifests.",
    )
    parser.add_argument(
        "--no-followup-queues",
        action="store_true",
        help="Do not write follow-up queue manifests.",
    )
    parser.add_argument(
        "--accepted-baseline-sample-size",
        type=int,
        default=25,
        help="Number of low-risk accepted papers to include in the deterministic baseline audit sample.",
    )
    parser.add_argument(
        "--no-accepted-sample-audit",
        action="store_true",
        help="Do not write the accepted-sample audit manifest.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [Path(path) for path in sorted(glob.glob(args.lane_glob))]
    if not paths:
        raise SystemExit(f"No lane summaries matched: {args.lane_glob}")
    report = build_report(paths)
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, out_md)
    followup_paths: dict[str, str] = {}
    if not args.no_followup_queues:
        followup_summary = {"results": report["papers"], "quality_control": {}}
        followup_paths = write_followup_queue_manifests(
            followup_summary,
            out_dir=Path(args.followup_dir),
            prefix=args.followup_prefix,
            source_summary_path=str(out_json),
            run_label=args.followup_prefix,
        )
        report["followup_queue_manifest_paths"] = followup_paths
        out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_markdown(report, out_md)
    accepted_sample_path = ""
    if not args.no_accepted_sample_audit:
        accepted_sample_summary = {"results": report["papers"], "quality_control": {}}
        accepted_sample_path = write_accepted_sample_audit_manifest(
            accepted_sample_summary,
            out_dir=Path(args.followup_dir),
            prefix=args.followup_prefix,
            source_summary_path=str(out_json),
            run_label=args.followup_prefix,
            baseline_sample_size=args.accepted_baseline_sample_size,
        )
        report["accepted_sample_audit_manifest_path"] = accepted_sample_path
        out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_markdown(report, out_md)
    print(
        json.dumps(
            {
                "ok": True,
                "out_json": str(out_json),
                "out_md": str(out_md),
                "followup_queue_manifest_paths": followup_paths,
                "accepted_sample_audit_manifest_path": accepted_sample_path,
                "paper_count": report["paper_count"],
                "clean_initial_pass_count": report["clean_initial_pass_count"],
                "post_rework_acceptance_count": report["post_rework_acceptance_count"],
                "blocked_or_infrastructure_count": report["blocked_or_infrastructure_count"],
                "refined_status_counts": report["refined_status_counts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
