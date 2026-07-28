#!/usr/bin/env python3
"""Triage unresolved database audit rows for the NAR freeze backlog.

This script is read-only over paper finals. It extracts rows whose status is
`unresolved_record`, classifies the likely blocker, and writes CSV/JSON/MD
reports for targeted source-staging or owner-worker rework.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers"
REPORTS = ROOT / "reports" / "nar_resource_freeze_v1"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def compact(value: Any, limit: int = 1200) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value)
    text = " ".join(text.split())
    return text[:limit]


def infer_database(record: dict[str, Any]) -> str:
    explicit = compact(record.get("database"), 200).strip()
    if explicit:
        return explicit
    text = " ".join(
        compact(record.get(k), 500)
        for k in ("source_id", "sequence_key", "source_table", "audit_id")
    ).lower()
    source_id = compact(record.get("source_id"), 200)
    if "dbaasp" in text or source_id.startswith("DBAAS"):
        return "DBAASP"
    if "dramp" in text:
        return "DRAMP"
    if "dbamp" in text:
        return "dbAMP"
    if "camp" in text:
        return "CAMP"
    if "apd6" in text or source_id.startswith("AP"):
        return "APD6"
    return "unknown"


def status_of(record: dict[str, Any]) -> str:
    return compact(record.get("status") or record.get("layer1_status") or "unknown", 200)


def classify_blocker(record: dict[str, Any]) -> tuple[str, str, str]:
    text = " ".join(
        compact(record.get(k), 2000)
        for k in (
            "conflict_context",
            "review_notes",
            "source_value_support_status",
            "source_value_locator",
            "sequence_check",
            "database_measure",
            "database_subject",
        )
    ).lower()
    if "supplement" in text and ("unavailable" in text or "missing" in text):
        return (
            "missing_or_unparsed_supplement",
            "source_staging_or_supplement_recovery",
            "recover supplementary table/package or document unrecoverable source gap",
        )
    if "partner" in text or "synergy" in text or "fici" in text:
        return (
            "synergy_partner_or_fici_mapping_ambiguous",
            "database_row_mapping_rework",
            "map database synergy row to source partner/table row or keep unresolved with partner ambiguity",
        )
    if "unique source table" in text or "row-level" in text or "not_row_level" in text:
        return (
            "row_level_source_mapping_ambiguous",
            "database_row_mapping_rework",
            "map database row to exact source row/value or preserve unresolved status",
        )
    if "sequence" in text and ("not embedded" in text or "absent" in text or "not_primary_source_verified" in text):
        return (
            "sequence_or_modification_evidence_missing",
            "sequence_source_recovery",
            "recover primary sequence/modification evidence or keep non-source-verified status",
        )
    if "material" in text or "missing" in text or "unavailable" in text:
        return (
            "material_gap_unspecified",
            "source_staging",
            "inspect packet material inventory and classify exact missing source",
        )
    return (
        "manual_adjudication_needed",
        "owner_worker_recheck",
        "re-open owner-worker review with this row context and preserve unresolved unless source evidence is found",
    )


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows: list[dict[str, Any]] = []
    for db_path in sorted(PAPERS.glob("*/final/database_record_verification.json")):
        paper_id = db_path.parts[-3]
        review = load_json(db_path.parent / "review_report.json", {}) or {}
        review_status = compact(review.get("review_status") or review.get("status"), 200)
        public_v1_included = bool(review.get("publication_grade")) and review_status in {
            "accepted",
            "accepted_clean",
            "accepted_with_cautions",
        }
        db_data = load_json(db_path, {}) or {}
        for idx, record in enumerate(db_data.get("record_audits") or db_data.get("records") or [], 1):
            if not isinstance(record, dict) or status_of(record) != "unresolved_record":
                continue
            blocker, target_queue, next_action = classify_blocker(record)
            rows.append(
                {
                    "paper_id": paper_id,
                    "record_index": idx,
                    "database": infer_database(record),
                    "source_table": compact(record.get("source_table"), 300),
                    "source_id": compact(record.get("source_id") or record.get("sequence_key"), 500),
                    "sequence_key": compact(record.get("sequence_key"), 500),
                    "database_subject": compact(record.get("database_subject"), 800),
                    "database_measure": compact(record.get("database_measure"), 500),
                    "source_value_support_status": compact(record.get("source_value_support_status"), 500),
                    "source_value_locator": compact(record.get("source_value_locator"), 1000),
                    "conflict_context": compact(record.get("conflict_context") or record.get("review_notes"), 1200),
                    "blocker_class": blocker,
                    "target_queue": target_queue,
                    "recommended_next_action": next_action,
                    "review_status": review_status,
                    "public_v1_included": public_v1_included,
                    "final_database_artifact": str(db_path.relative_to(ROOT)),
                }
            )

    by_paper = Counter(row["paper_id"] for row in rows)
    by_database = Counter(row["database"] for row in rows)
    by_blocker = Counter(row["blocker_class"] for row in rows)
    by_target = Counter(row["target_queue"] for row in rows)
    summary = {
        "generated_at": generated_at,
        "unresolved_record_count": len(rows),
        "paper_count": len(by_paper),
        "database_counts": dict(sorted(by_database.items())),
        "blocker_class_counts": dict(sorted(by_blocker.items())),
        "target_queue_counts": dict(sorted(by_target.items())),
        "top_papers": dict(by_paper.most_common(20)),
        "outputs": {
            "csv": "reports/nar_resource_freeze_v1/unresolved_records_triage_latest.csv",
            "json": "reports/nar_resource_freeze_v1/unresolved_records_triage_latest.json",
            "md": "reports/nar_resource_freeze_v1/unresolved_records_triage_latest.md",
        },
    }

    csv_path = REPORTS / "unresolved_records_triage_latest.csv"
    fieldnames = list(rows[0].keys()) if rows else []
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    (REPORTS / "unresolved_records_triage_latest.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Unresolved Record Triage",
        "",
        f"Generated at: `{generated_at}`",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| unresolved records | {len(rows)} |",
        f"| papers with unresolved records | {len(by_paper)} |",
        "",
        "## By Database",
        "",
        "| database | count |",
        "| --- | ---: |",
    ]
    for key, value in sorted(by_database.items()):
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## By Blocker Class", "", "| blocker_class | count | target |", "| --- | ---: | --- |"])
    for key, value in sorted(by_blocker.items()):
        target = next((row["target_queue"] for row in rows if row["blocker_class"] == key), "")
        lines.append(f"| `{key}` | {value} | `{target}` |")
    lines.extend(["", "## Top Papers", "", "| paper_id | unresolved rows |", "| --- | ---: |"])
    for key, value in by_paper.most_common(20):
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Next Action Policy",
            "",
            "- Do not convert `unresolved_record` to `source_verified` without locating primary-source evidence.",
            "- Missing supplements or row-level ambiguity should be routed to source staging / database-row mapping rework.",
            "- If the required material remains unavailable after best effort, keep unresolved and disclose it in the release notes.",
            "",
        ]
    )
    (REPORTS / "unresolved_records_triage_latest.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
