#!/usr/bin/env python3
"""Check mechanism evidence_class vocabulary for pilot20 dispatch papers."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DISPATCH_INDEX = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "pilot20" / "source_review_packets" / "owner_rework_dispatch" / "dispatch_index_latest.csv"
PACKET_INDEX = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "pilot20" / "source_review_packets" / "packet_index_latest.csv"
READJUDICATION_STATUS = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation" / "pilot20" / "source_review_packets" / "worker6_readjudication" / "pilot20_worker6_readjudication_latest.csv"
OUTDIR = DISPATCH_INDEX.parent / "ontology_qc"
WORKER6_STATUS = DISPATCH_INDEX.parents[1] / "worker6_final_mirror" / "runner" / "worker6_final_runner_status_latest.csv"
NON_DISPATCH_STATUS = DISPATCH_INDEX.parents[1] / "worker6_non_dispatch_final_review" / "runner" / "worker6_non_dispatch_status_latest.csv"
ALLOWED = {"direct_mechanism", "phenotype_supported", "inferred_mechanism", "computational_only", "unknown_or_not_tested"}
MECHANISM_PATHS = [
    "paper_packets/{paper_id}/analysis/mechanism_evidence.json",
    "paper_packets/{paper_id}/final/mechanism_evidence.json",
    "papers/{paper_id}/final/mechanism_evidence.json",
    "papers/{paper_id}/final/mechanism_ontology_record.json",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except (OSError, RuntimeError, ValueError):
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


def load_final_decisions() -> dict[str, str]:
    decisions: dict[str, str] = {}
    if READJUDICATION_STATUS.exists():
        for row in read_csv(READJUDICATION_STATUS):
            paper_id = row.get("paper_id", "")
            decision = row.get("readjudicated_decision", "")
            if decision == "accepted_with_cautions_confirmed":
                decision = "accepted_with_cautions"
            if paper_id:
                decisions[paper_id] = decision
    if NON_DISPATCH_STATUS.exists():
        for row in read_csv(NON_DISPATCH_STATUS):
            paper_id = row.get("paper_id", "")
            if paper_id:
                decisions[paper_id] = row.get("final_decision", "")
    if WORKER6_STATUS.exists():
        for row in read_csv(WORKER6_STATUS):
            paper_id = row.get("paper_id", "")
            if paper_id:
                decisions[paper_id] = row.get("final_decision", "")
    return decisions


def decision_bucket(decision: str) -> str:
    if decision in {"accepted_clean", "accepted_with_cautions"}:
        return "accepted"
    if decision:
        return "nonterminal"
    return "unknown"


def evidence_classes(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        if "evidence_class" in value:
            found.append(str(value.get("evidence_class")))
        for child in value.values():
            found.extend(evidence_classes(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(evidence_classes(child))
    return found


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    run_id = stamp()
    paper_source = PACKET_INDEX if PACKET_INDEX.exists() else DISPATCH_INDEX
    paper_rows = read_csv(paper_source)
    paper_ids = sorted({row["paper_id"] for row in paper_rows})
    final_decisions = load_final_decisions()
    rows: list[dict[str, Any]] = []
    for paper_id in paper_ids:
        final_decision = final_decisions.get(paper_id, "")
        bucket = decision_bucket(final_decision)
        for tmpl in MECHANISM_PATHS:
            path = ROOT / tmpl.format(paper_id=paper_id)
            if not path.exists():
                rows.append({
                    "paper_id": paper_id,
                    "final_decision": final_decision,
                    "decision_bucket": bucket,
                    "path": rel(path),
                    "exists": "false",
                    "classes": "",
                    "bad_classes": "",
                    "bad_count": 0,
                })
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                classes = sorted(set(c for c in evidence_classes(data) if c))
                bad = [item for item in classes if item not in ALLOWED]
                rows.append({
                    "paper_id": paper_id,
                    "final_decision": final_decision,
                    "decision_bucket": bucket,
                    "path": rel(path),
                    "exists": "true",
                    "classes": ";".join(classes),
                    "bad_classes": ";".join(bad),
                    "bad_count": len(bad),
                })
            except Exception as exc:  # noqa: BLE001
                rows.append({
                    "paper_id": paper_id,
                    "final_decision": final_decision,
                    "decision_bucket": bucket,
                    "path": rel(path),
                    "exists": "true",
                    "classes": "",
                    "bad_classes": f"JSON_ERROR:{type(exc).__name__}",
                    "bad_count": 1,
                })

    fields = ["paper_id", "final_decision", "decision_bucket", "path", "exists", "classes", "bad_classes", "bad_count"]
    csv_path = OUTDIR / f"mechanism_ontology_class_qc_{run_id}.csv"
    latest_csv = OUTDIR / "mechanism_ontology_class_qc_latest.csv"
    write_csv(csv_path, rows, fields)
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")
    summary = {
        "generated_at": now_utc(),
        "allowed_classes": sorted(ALLOWED),
        "paper_source_csv": rel(paper_source),
        "paper_count": len(paper_ids),
        "file_count": len(rows),
        "files_with_bad_classes": sum(1 for row in rows if int(row["bad_count"]) > 0),
        "files_with_bad_classes_by_decision": dict(Counter(
            str(row["final_decision"] or "unknown") for row in rows if int(row["bad_count"]) > 0
        )),
        "files_with_bad_classes_by_bucket": dict(Counter(
            str(row["decision_bucket"]) for row in rows if int(row["bad_count"]) > 0
        )),
        "accepted_file_count": sum(1 for row in rows if row["decision_bucket"] == "accepted"),
        "accepted_files_with_bad_classes": sum(
            1 for row in rows if row["decision_bucket"] == "accepted" and int(row["bad_count"]) > 0
        ),
        "nonterminal_file_count": sum(1 for row in rows if row["decision_bucket"] == "nonterminal"),
        "nonterminal_files_with_bad_classes": sum(
            1 for row in rows if row["decision_bucket"] == "nonterminal" and int(row["bad_count"]) > 0
        ),
        "bad_class_counts": dict(Counter(cls for row in rows for cls in str(row["bad_classes"]).split(";") if cls)),
        "worker6_status_csv": rel(WORKER6_STATUS) if WORKER6_STATUS.exists() else "",
        "non_dispatch_status_csv": rel(NON_DISPATCH_STATUS) if NON_DISPATCH_STATUS.exists() else "",
        "readjudication_status_csv": rel(READJUDICATION_STATUS) if READJUDICATION_STATUS.exists() else "",
        "outputs": {
            "qc_csv": rel(csv_path),
            "latest_qc_csv": rel(latest_csv),
            "summary_json": rel(OUTDIR / f"mechanism_ontology_class_qc_summary_{run_id}.json"),
            "latest_summary_json": rel(OUTDIR / "mechanism_ontology_class_qc_summary_latest.json"),
            "report_md": rel(OUTDIR / f"mechanism_ontology_class_qc_report_{run_id}.md"),
            "latest_report_md": rel(OUTDIR / "mechanism_ontology_class_qc_report_latest.md"),
        },
    }
    write_json(OUTDIR / f"mechanism_ontology_class_qc_summary_{run_id}.json", summary)
    write_json(OUTDIR / "mechanism_ontology_class_qc_summary_latest.json", summary)
    lines = [
        "# Pilot20 Mechanism Ontology Class QC",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        f"- Papers checked: `{summary['paper_count']}`",
        f"- Paper source: `{summary['paper_source_csv']}`",
        f"- Mechanism files checked: `{summary['file_count']}`",
        f"- Files with non-standard classes: `{summary['files_with_bad_classes']}`",
        f"- Accepted files with non-standard classes: `{summary['accepted_files_with_bad_classes']}` / `{summary['accepted_file_count']}`",
        f"- Nonterminal files with non-standard classes: `{summary['nonterminal_files_with_bad_classes']}` / `{summary['nonterminal_file_count']}`",
        "",
        "## Bad Classes By Final Decision",
        "",
        "| final decision | files |",
        "| --- | ---: |",
    ]
    for decision, count in sorted(summary["files_with_bad_classes_by_decision"].items()):
        lines.append(f"| `{decision}` | {count} |")
    lines.extend([
        "",
        "## Bad Class Counts",
        "",
        "| class | files |",
        "| --- | ---: |",
    ])
    for cls, count in sorted(summary["bad_class_counts"].items()):
        lines.append(f"| `{cls}` | {count} |")
    lines.extend(["", "## Files With Bad Classes", "", "| paper | final decision | path | bad classes |", "| --- | --- | --- | --- |"])
    for row in rows:
        if int(row["bad_count"]) > 0:
            lines.append(f"| `{row['paper_id']}` | `{row['final_decision'] or 'unknown'}` | `{row['path']}` | `{row['bad_classes']}` |")
    report = OUTDIR / f"mechanism_ontology_class_qc_report_{run_id}.md"
    latest_report = OUTDIR / "mechanism_ontology_class_qc_report_latest.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    latest_report.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
