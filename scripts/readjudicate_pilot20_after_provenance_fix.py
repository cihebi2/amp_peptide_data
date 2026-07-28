#!/usr/bin/env python3
"""Worker-6 style readjudication after fixing the model-provenance rule."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "pilot20" / "source_review_packets"
RESULTS_CSV = PACKET_ROOT / "summary" / "pilot20_true_source_review_results_latest.csv"
OUTDIR = PACKET_ROOT / "worker6_readjudication"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except (ValueError, RuntimeError, OSError):
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
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def runner_header_proves_model(packet_dir: Path) -> bool:
    stderr = packet_dir / "codex_exec.stderr.log"
    if not stderr.exists():
        return False
    text = stderr.read_text(encoding="utf-8", errors="replace")[:5000].lower()
    return "model: gpt-5.5" in text and "reasoning effort: xhigh" in text


def result_path_for(row: dict[str, str]) -> Path:
    path = Path(row["result_path"])
    return path if path.is_absolute() else ROOT / path


def packet_dir_for(row: dict[str, str]) -> Path:
    path = Path(row["packet_dir"])
    return path if path.is_absolute() else ROOT / path


def text_blob(result: dict[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, sort_keys=True).lower()


def readjudicate(row: dict[str, str], result: dict[str, Any], model_provenance_ok: bool) -> tuple[str, str, str]:
    decision = str(result.get("decision", ""))
    rework_targets = result.get("rework_targets") or []
    text = text_blob(result)
    if not model_provenance_ok:
        return "unverifiable_best_effort", "model_provenance_not_proven_by_runner_header", "Runner header did not prove gpt-5.5/xhigh."
    if decision == "blocked_missing_primary_material":
        return "blocked_missing_primary_material", "blocked_by_missing_primary_material", "Reviewer marked missing primary material."
    if decision == "needs_targeted_rework" or rework_targets:
        return "needs_targeted_rework", "rework_targets_present", "Source review contains hard or repairable rework targets."
    if "needs_targeted_rework" in text or "not confirmed as-is" in text:
        return "needs_targeted_rework", "worker6_text_mentions_rework", "Worker-6 rationale mentions targeted rework even without structured targets."
    if decision == "pass_source_review":
        return "pass_source_review", "clean_source_review_confirmed", "Reviewer explicitly marked clean pass."
    if decision == "accepted_with_cautions_confirmed" or "accepted_with_cautions" in text:
        return "accepted_with_cautions_confirmed", "cautions_preserved", "No structured hard rework remains, but cautions/conflicts remain preserved."
    return "unverifiable_best_effort", "no_clean_acceptance_evidence", "No hard rework target, but result lacks clean or cautioned acceptance proof."


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    run_id = stamp()
    rows = read_csv(RESULTS_CSV)
    out_rows: list[dict[str, Any]] = []
    for row in rows:
        result_path = result_path_for(row)
        packet_dir = packet_dir_for(row)
        result = load_json(result_path)
        model_ok = runner_header_proves_model(packet_dir)
        new_decision, reason_code, rationale = readjudicate(row, result, model_ok)
        out_rows.append(
            {
                "pilot_sample_id": row["pilot_sample_id"],
                "paper_id": row["paper_id"],
                "database": row["database"],
                "source_id": row["source_id"],
                "audit_record_id": row["audit_record_id"],
                "status": row["status"],
                "original_decision": row["decision"],
                "readjudicated_decision": new_decision,
                "reason_code": reason_code,
                "rationale": rationale,
                "runner_model_provenance_ok": str(model_ok).lower(),
                "rework_target_count": row.get("rework_target_count", ""),
                "caution_count": row.get("caution_count", ""),
                "best_effort_limit_count": row.get("best_effort_limit_count", ""),
                "result_path": row["result_path"],
                "packet_dir": row["packet_dir"],
            }
        )

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
        "rationale",
        "runner_model_provenance_ok",
        "rework_target_count",
        "caution_count",
        "best_effort_limit_count",
        "result_path",
        "packet_dir",
    ]
    csv_path = OUTDIR / f"pilot20_worker6_readjudication_{run_id}.csv"
    latest_csv = OUTDIR / "pilot20_worker6_readjudication_latest.csv"
    write_csv(csv_path, out_rows, fields)
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")

    summary = {
        "generated_at": now_utc(),
        "completion_claim": "pilot20_worker6_readjudication_after_provenance_fix_not_artifact_repair",
        "input_results_csv": rel(RESULTS_CSV),
        "result_count": len(out_rows),
        "original_decision_counts": dict(Counter(row["original_decision"] for row in out_rows)),
        "readjudicated_decision_counts": dict(Counter(row["readjudicated_decision"] for row in out_rows)),
        "reason_code_counts": dict(Counter(row["reason_code"] for row in out_rows)),
        "runner_model_provenance_ok_count": sum(1 for row in out_rows if row["runner_model_provenance_ok"] == "true"),
        "outputs": {
            "readjudication_csv": rel(csv_path),
            "latest_readjudication_csv": rel(latest_csv),
            "summary_json": rel(OUTDIR / f"pilot20_worker6_readjudication_summary_{run_id}.json"),
            "latest_summary_json": rel(OUTDIR / "pilot20_worker6_readjudication_summary_latest.json"),
            "report_md": rel(OUTDIR / f"pilot20_worker6_readjudication_report_{run_id}.md"),
            "latest_report_md": rel(OUTDIR / "pilot20_worker6_readjudication_report_latest.md"),
        },
    }
    summary_path = OUTDIR / f"pilot20_worker6_readjudication_summary_{run_id}.json"
    latest_summary = OUTDIR / "pilot20_worker6_readjudication_summary_latest.json"
    write_json(summary_path, summary)
    write_json(latest_summary, summary)

    lines = [
        "# Pilot20 Worker-6 Readjudication After Provenance Fix",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "This is a batch-level worker-6 style readjudication of the 20 true-review results after treating the `codex exec` runner header as valid model/effort provenance. It does not repair paper artifacts.",
        "",
        "## Counts",
        "",
        "| decision | count |",
        "| --- | ---: |",
    ]
    for decision, count in sorted(summary["readjudicated_decision_counts"].items()):
        lines.append(f"| `{decision}` | {count} |")
    lines.extend(["", "## Per-Paper", "", "| pilot | status | paper | original | readjudicated | reason |", "| --- | --- | --- | --- | --- | --- |"])
    for row in out_rows:
        lines.append(
            f"| `{row['pilot_sample_id']}` | `{row['status']}` | `{row['paper_id']}` | `{row['original_decision']}` | `{row['readjudicated_decision']}` | `{row['reason_code']}` |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- Model-provenance downgrade was removed only when the packet `codex_exec.stderr.log` header proved `model: gpt-5.5` and `reasoning effort: xhigh`.",
        "- Any non-empty `rework_targets` still forces `needs_targeted_rework`.",
        "- `accepted_with_cautions_confirmed` is not clean; it means cautions/conflicts remain publication-visible.",
        "- This readjudication does not edit `papers/<paper_id>/final/`; owner-worker repair and worker-6 artifact update remain separate steps.",
        "",
    ])
    report_path = OUTDIR / f"pilot20_worker6_readjudication_report_{run_id}.md"
    latest_report = OUTDIR / "pilot20_worker6_readjudication_report_latest.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    latest_report.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
