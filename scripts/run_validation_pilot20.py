#!/usr/bin/env python3
"""Run a 20-paper validation pilot over the v1 RC1 manual-validation sample.

This is a pilot verifier, not a replacement for human/source-reviewed audit. It
selects unique papers from the stratified validation manifest, checks release-row
and final-artifact consistency, applies status-specific evidence heuristics, and
emits rework tickets for major/critical failures.
"""

from __future__ import annotations

import csv
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation"
SOURCE_MANIFEST = VALIDATION_DIR / "validation_manifest_latest.csv"
RELEASE_TABLE = ROOT / "releases" / "amp_evidence_atlas_v1_rc1" / "database_record_audits.tsv"
OUTDIR = VALIDATION_DIR / "pilot20"

PILOT_QUOTAS = [
    ("source_verified", "true", 4),
    ("source_conflict", "true", 5),
    ("sequence_modified_not_normalized", "true", 4),
    ("database_only_no_primary_source", "true", 4),
    ("unresolved_record", "false", 3),
]

PREFERRED_DATABASE_ORDER = ["DBAASP", "DRAMP", "dbAMP", "APD6", "CAMP", "unknown"]

ACCEPTED_PUBLIC_STATUSES = {"accepted", "accepted_clean", "accepted_with_cautions"}
TICKET_DECISIONS = {"major_error", "critical_error", "needs_rework"}

PILOT_FIELDS = [
    "sample_id", "pilot_sample_id", "sample_role", "status", "public_v1_included",
    "database", "paper_id", "doi", "source_id", "audit_record_id", "record_index",
    "primary_validation_category", "difference_categories", "release_table_path",
    "release_row_locator", "final_artifact_path",
]

RESULT_FIELDS = PILOT_FIELDS + [
    "reviewer_decision", "reviewer_error_class", "reviewer_notes", "issue_codes",
    "checked_release_row", "checked_final_artifact", "checked_review_report",
    "record_found_in_final", "status_specific_pass", "reviewed_by", "reviewed_at",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def read_csv(path: Path, dialect: str | None = None) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        if dialect == "excel-tab":
            return list(csv.DictReader(fh, dialect="excel-tab"))
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def compact(value: Any, limit: int = 320) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = " ".join(text.split())
    if len(text) > limit:
        return text[: limit - 1] + "..."
    return text


def select_pilot_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    used_papers: set[str] = set()
    used_audit_ids: set[str] = set()
    rows_by_status_public: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        rows_by_status_public[(row["status"], row["public_v1_included"])].append(row)
    for key in rows_by_status_public:
        rows_by_status_public[key].sort(
            key=lambda row: (
                row.get("database", ""),
                row.get("primary_validation_category", ""),
                row.get("paper_id", ""),
                row.get("audit_record_id", ""),
            )
        )

    for status, public_flag, quota in PILOT_QUOTAS:
        picked = 0
        group = rows_by_status_public.get((status, public_flag), [])
        by_database: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in group:
            by_database[row.get("database", "")].append(row)
        database_order = [db for db in PREFERRED_DATABASE_ORDER if by_database.get(db)]
        database_order += sorted(db for db in by_database if db not in database_order)

        for pass_name in ("database_round_robin", "fallback_any_database"):
            while picked < quota:
                progressed = False
                iterable = database_order if pass_name == "database_round_robin" else sorted(by_database)
                for database in iterable:
                    for row in by_database.get(database, []):
                        if row["paper_id"] in used_papers or row["audit_record_id"] in used_audit_ids:
                            continue
                        selected_row = dict(row)
                        role = "public_candidate_status_stratum" if public_flag == "true" else "non_public_unresolved_sentinel"
                        selected_row["sample_role"] = role
                        selected.append(selected_row)
                        used_papers.add(row["paper_id"])
                        used_audit_ids.add(row["audit_record_id"])
                        picked += 1
                        progressed = True
                        break
                    if picked >= quota:
                        break
                if not progressed:
                    break
            if picked >= quota:
                break
        if picked < quota:
            raise RuntimeError(f"insufficient unique papers for {status}/{public_flag}: {picked} < {quota}")

    for idx, row in enumerate(selected, 1):
        row["pilot_sample_id"] = f"PILOT20-{idx:03d}"
    return selected


def load_release_rows(audit_ids: set[str]) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    with RELEASE_TABLE.open(encoding="utf-8", newline="") as fh:
        for idx, row in enumerate(csv.DictReader(fh, dialect="excel-tab"), start=2):
            audit_id = row.get("audit_record_id", "")
            if audit_id in audit_ids:
                row["_release_row_number"] = str(idx)
                found[audit_id] = row
                if len(found) == len(audit_ids):
                    break
    return found


def final_records(final_data: dict[str, Any]) -> list[dict[str, Any]]:
    records = final_data.get("record_audits") or final_data.get("records") or []
    return [record for record in records if isinstance(record, dict)]


def find_final_record(final_data: dict[str, Any], sample: dict[str, str], release_row: dict[str, str] | None) -> tuple[bool, dict[str, Any] | None]:
    records = final_records(final_data)
    try:
        idx = int(sample.get("record_index", "0")) - 1
    except ValueError:
        idx = -1
    if 0 <= idx < len(records):
        record = records[idx]
        source_id = str(record.get("source_id") or record.get("sequence_key") or "")
        if sample.get("source_id", "").split(":")[-1] in source_id or source_id.split(":")[-1] in sample.get("source_id", ""):
            return True, record
    if release_row:
        wanted = sample.get("source_id", "").split(":")[-1]
        status = sample.get("status", "")
        for record in records:
            source_id = str(record.get("source_id") or record.get("sequence_key") or "")
            record_status = str(record.get("status") or record.get("layer1_status") or "")
            if wanted and wanted in source_id and (not status or status == record_status):
                return True, record
    return False, None


def has_any(row: dict[str, str], keys: list[str]) -> bool:
    return any(bool(str(row.get(key, "")).strip()) for key in keys)


def status_specific_check(sample: dict[str, str], release_row: dict[str, str] | None, final_record: dict[str, Any] | None) -> tuple[bool, list[str]]:
    issues: list[str] = []
    status = sample.get("status", "")
    category_text = sample.get("difference_categories", "")
    row = release_row or {}
    record_text = compact(final_record or {}, 2000).lower()
    row_text = " ".join(str(row.get(k, "")) for k in [
        "source_locator", "traceability", "citation_traceability", "matched_activity_record_id",
        "primary_source_subject", "primary_source_value", "primary_source_sequence", "conflict_context",
        "conflict_interpretation", "review_notes", "sequence_check", "modification_check", "activity_check",
    ]).lower()
    evidence_text = f"{row_text} {record_text}"

    if status == "source_verified":
        if not has_any(row, ["source_locator", "traceability", "citation_traceability", "matched_activity_record_id", "primary_source_subject", "primary_source_value", "primary_source_sequence"]):
            issues.append("source_verified_lacks_locator_or_primary_field")
    elif status == "source_conflict":
        if not has_any(row, ["conflict_context", "conflict_interpretation", "review_notes", "conflict_flags"]):
            issues.append("source_conflict_lacks_conflict_rationale")
    elif status == "sequence_modified_not_normalized":
        if "sequence_or_modification" not in category_text:
            issues.append("sequence_modified_missing_category")
        if not any(token in evidence_text for token in ["sequence", "modification", "terminal", "amid", "nh2", "d-amino", "variant"]):
            issues.append("sequence_modified_lacks_sequence_or_modification_rationale")
    elif status == "database_only_no_primary_source":
        if "database_only_no_primary_source" not in category_text:
            issues.append("database_only_missing_category")
        if not any(token in evidence_text for token in ["database-only", "database_only", "no primary", "not promoted", "not support", "unmatched"]):
            issues.append("database_only_lacks_no_primary_rationale")
    elif status == "unresolved_record":
        if "unresolved_or_missing_material" not in category_text:
            issues.append("unresolved_missing_category")
        if not any(token in evidence_text for token in ["missing", "unresolved", "supplement", "material", "not recover", "fici", "cannot"]):
            issues.append("unresolved_lacks_material_gap_rationale")
    else:
        issues.append(f"unknown_status:{status}")
    return not issues, issues


def decision_from_issues(issue_codes: list[str], sample: dict[str, str]) -> tuple[str, str]:
    if not issue_codes:
        return "pass", "none"
    critical_prefixes = ["release_row_missing", "final_artifact_missing", "final_artifact_unreadable", "record_not_found_in_final"]
    if any(code in issue_codes for code in critical_prefixes):
        return "critical_error", "source_locator_error"
    if any("status_mismatch" in code for code in issue_codes):
        return "major_error", "status_misclassification"
    if sample.get("status") == "unresolved_record":
        return "unverifiable", "missing_material"
    return "major_error", "overclaim"


def audit_one(sample: dict[str, str], release_rows: dict[str, dict[str, str]]) -> dict[str, Any]:
    issue_codes: list[str] = []
    audit_id = sample["audit_record_id"]
    release_row = release_rows.get(audit_id)
    checked_release_row = release_row is not None
    if not release_row:
        issue_codes.append("release_row_missing")
    else:
        for key in ["paper_id", "database", "status", "source_id"]:
            if str(release_row.get(key, "")) != str(sample.get(key, "")):
                issue_codes.append(f"release_row_{key}_mismatch")

    final_path = ROOT / sample["final_artifact_path"]
    checked_final_artifact = final_path.exists()
    final_data: dict[str, Any] = {}
    if not checked_final_artifact:
        issue_codes.append("final_artifact_missing")
    else:
        try:
            final_data = load_json(final_path)
        except Exception:
            issue_codes.append("final_artifact_unreadable")

    review_path = ROOT / "papers" / sample["paper_id"] / "final" / "review_report.json"
    checked_review_report = review_path.exists()
    if not checked_review_report:
        issue_codes.append("review_report_missing")
    else:
        try:
            review = load_json(review_path)
            if sample.get("public_v1_included") == "true":
                if str(review.get("review_status", "")) not in ACCEPTED_PUBLIC_STATUSES:
                    issue_codes.append("public_sample_review_status_not_accepted_like")
                if review.get("publication_grade") is not True:
                    issue_codes.append("public_sample_publication_grade_not_true")
        except Exception:
            issue_codes.append("review_report_unreadable")

    record_found = False
    final_record = None
    if final_data:
        record_found, final_record = find_final_record(final_data, sample, release_row)
        if not record_found:
            issue_codes.append("record_not_found_in_final")

    status_pass = False
    if release_row and final_record is not None:
        status_pass, status_issues = status_specific_check(sample, release_row, final_record)
        issue_codes.extend(status_issues)

    decision, error_class = decision_from_issues(issue_codes, sample)
    notes = "status-specific evidence and paths passed" if not issue_codes else "; ".join(issue_codes)
    result = dict(sample)
    result.update({
        "reviewer_decision": decision,
        "reviewer_error_class": error_class,
        "reviewer_notes": notes,
        "issue_codes": ";".join(sorted(set(issue_codes))),
        "checked_release_row": str(checked_release_row).lower(),
        "checked_final_artifact": str(checked_final_artifact).lower(),
        "checked_review_report": str(checked_review_report).lower(),
        "record_found_in_final": str(record_found).lower(),
        "status_specific_pass": str(status_pass).lower(),
        "reviewed_by": "codex_validation_pilot20_structural_status_checker",
        "reviewed_at": now_utc(),
    })
    return result


def ticket_for(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticket_id": f"pilot20-{result['pilot_sample_id']}-{result['audit_record_id']}",
        "created_at": now_utc(),
        "target_queue": "owner_worker_rework_then_worker6_adjudication",
        "severity": result["reviewer_decision"],
        "paper_id": result["paper_id"],
        "database": result["database"],
        "source_id": result["source_id"],
        "audit_record_id": result["audit_record_id"],
        "status": result["status"],
        "issue_codes": [code for code in result.get("issue_codes", "").split(";") if code],
        "context": {
            "release_table_path": result["release_table_path"],
            "release_row_locator": result["release_row_locator"],
            "final_artifact_path": result["final_artifact_path"],
            "validation_sample_id": result["sample_id"],
            "pilot_sample_id": result["pilot_sample_id"],
        },
        "worker_instruction": "Reopen only the listed audit row; verify database-side fields, primary-source locator support, status classification, and preserve caution/unresolved status if material is insufficient.",
    }


def write_report(path: Path, summary: dict[str, Any], results: list[dict[str, Any]], tickets: list[dict[str, Any]]) -> None:
    lines = [
        "# Pilot 20-Paper Validation Report",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "This is a 20-paper pilot over the v1 RC1 manual-validation manifest. It checks release-row/final-artifact consistency and status-specific evidence heuristics. It is not the final 420-row manual validation result.",
        "",
        "## Scope",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| selected papers | {summary['selected_paper_count']} |",
        f"| selected validation rows | {summary['selected_row_count']} |",
        f"| pass | {summary['decision_counts'].get('pass', 0)} |",
        f"| minor_error | {summary['decision_counts'].get('minor_error', 0)} |",
        f"| major_error | {summary['decision_counts'].get('major_error', 0)} |",
        f"| critical_error | {summary['decision_counts'].get('critical_error', 0)} |",
        f"| needs_rework | {summary['decision_counts'].get('needs_rework', 0)} |",
        f"| unverifiable | {summary['decision_counts'].get('unverifiable', 0)} |",
        f"| rework tickets | {len(tickets)} |",
        "",
        "## Status Coverage",
        "",
        "| status | rows |",
        "| --- | ---: |",
    ]
    for status, count in sorted(summary["status_counts"].items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Database Coverage", "", "| database | rows |", "| --- | ---: |"])
    for database, count in sorted(summary["database_counts"].items()):
        lines.append(f"| `{database}` | {count} |")
    lines.extend(["", "## Pilot Results", "", "| pilot | paper | database/source | status | decision | notes |", "| --- | --- | --- | --- | --- | --- |"])
    for result in results:
        notes = compact(result.get("reviewer_notes", ""), 180).replace("|", "\\|")
        lines.append(
            f"| `{result['pilot_sample_id']}` | `{result['paper_id']}` | `{result['database']} / {result['source_id']}` | `{result['status']}` | `{result['reviewer_decision']}` | {notes} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- `pass` means the pilot checker found matching release/final rows and enough status-specific rationale for this row.",
        "- `unverifiable` for unresolved sentinel rows means the material gap must remain visible rather than being guessed away.",
        "- Any `major_error`, `critical_error`, or `needs_rework` row is written to the pilot rework-ticket JSONL for owner-worker repair and worker-6 adjudication.",
        "- This pilot does not prove the full 420-row validation set passed; it tests the validation workflow on 20 unique papers.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    source_rows = read_csv(SOURCE_MANIFEST)
    selected = select_pilot_rows(source_rows)
    audit_ids = {row["audit_record_id"] for row in selected}
    release_rows = load_release_rows(audit_ids)
    results = [audit_one(row, release_rows) for row in selected]
    tickets = [ticket_for(result) for result in results if result["reviewer_decision"] in TICKET_DECISIONS]

    run_stamp = stamp()
    manifest_path = OUTDIR / f"pilot20_manifest_{run_stamp}.csv"
    results_csv = OUTDIR / f"pilot20_results_{run_stamp}.csv"
    summary_json = OUTDIR / f"pilot20_summary_{run_stamp}.json"
    tickets_jsonl = OUTDIR / f"pilot20_rework_tickets_{run_stamp}.jsonl"
    report_md = OUTDIR / f"pilot20_report_{run_stamp}.md"

    write_csv(manifest_path, selected, PILOT_FIELDS)
    write_csv(results_csv, results, RESULT_FIELDS)
    with tickets_jsonl.open("w", encoding="utf-8") as fh:
        for ticket in tickets:
            fh.write(json.dumps(ticket, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "generated_at": now_utc(),
        "completion_claim": "pilot20_validation_workflow_test_not_full_manual_validation",
        "source_manifest": str(SOURCE_MANIFEST.relative_to(ROOT)),
        "release_table": str(RELEASE_TABLE.relative_to(ROOT)),
        "selected_paper_count": len({row["paper_id"] for row in selected}),
        "selected_row_count": len(selected),
        "decision_counts": dict(Counter(result["reviewer_decision"] for result in results)),
        "status_counts": dict(Counter(result["status"] for result in results)),
        "database_counts": dict(Counter(result["database"] for result in results)),
        "issue_counts": dict(Counter(code for result in results for code in result.get("issue_codes", "").split(";") if code)),
        "ticket_count": len(tickets),
        "outputs": {
            "manifest_csv": str(manifest_path.relative_to(ROOT)),
            "results_csv": str(results_csv.relative_to(ROOT)),
            "summary_json": str(summary_json.relative_to(ROOT)),
            "tickets_jsonl": str(tickets_jsonl.relative_to(ROOT)),
            "report_md": str(report_md.relative_to(ROOT)),
            "latest_manifest_csv": str((OUTDIR / "pilot20_manifest_latest.csv").relative_to(ROOT)),
            "latest_results_csv": str((OUTDIR / "pilot20_results_latest.csv").relative_to(ROOT)),
            "latest_summary_json": str((OUTDIR / "pilot20_summary_latest.json").relative_to(ROOT)),
            "latest_tickets_jsonl": str((OUTDIR / "pilot20_rework_tickets_latest.jsonl").relative_to(ROOT)),
            "latest_report_md": str((OUTDIR / "pilot20_report_latest.md").relative_to(ROOT)),
        },
    }
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report_md, summary, results, tickets)

    latest_pairs = [
        (manifest_path, OUTDIR / "pilot20_manifest_latest.csv"),
        (results_csv, OUTDIR / "pilot20_results_latest.csv"),
        (summary_json, OUTDIR / "pilot20_summary_latest.json"),
        (tickets_jsonl, OUTDIR / "pilot20_rework_tickets_latest.jsonl"),
        (report_md, OUTDIR / "pilot20_report_latest.md"),
    ]
    for src, dst in latest_pairs:
        shutil.copyfile(src, dst)

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
