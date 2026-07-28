#!/usr/bin/env python3
"""Validate unresolved-record processing artifacts for the NAR freeze."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "reports" / "nar_resource_freeze_v1"
WORK = BASE / "unresolved_work"
EXPECTED_BY_PAPER = {
    "doi__10.1038_s41522-024-00637-y": 30,
    "doi__10.1038_s41598-017-16784-6": 24,
    "doi__10.21203_rs.3.rs-578319_v1": 2,
}


def fail(message: str) -> None:
    print(f"FAIL {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path):
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        fail(f"cannot parse JSON {path}: {exc}")


def main() -> None:
    triage_csv = BASE / "unresolved_records_triage_latest.csv"
    if not triage_csv.exists():
        fail(f"missing {triage_csv}")
    with triage_csv.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 56:
        fail(f"expected 56 triage rows, got {len(rows)}")
    by_paper = Counter(row["paper_id"] for row in rows)
    if dict(by_paper) != EXPECTED_BY_PAPER:
        fail(f"unexpected per-paper distribution {dict(by_paper)}")
    if any(row.get("public_v1_included") != "False" for row in rows):
        fail("all unresolved triage rows must have public_v1_included=False")

    triage = load_json(BASE / "unresolved_records_triage_latest.json")["summary"]
    if triage.get("unresolved_record_count") != 56 or triage.get("paper_count") != 3:
        fail(f"unexpected triage summary {triage}")
    if triage.get("database_counts") != {"DBAASP": 56}:
        fail(f"unexpected database counts {triage.get('database_counts')}")

    summary = load_json(WORK / "summary_latest.json")
    if summary.get("unresolved_record_count") != 56:
        fail("resolution summary unresolved_record_count must be 56")
    if summary.get("paper_count") != 3:
        fail("resolution summary paper_count must be 3")
    if summary.get("status_change_applied_count") != 0:
        fail("status_change_applied_count must remain 0")
    for decision in summary.get("decisions", []):
        pid = decision.get("paper_id")
        if pid not in EXPECTED_BY_PAPER:
            fail(f"unexpected decision paper {pid}")
        if decision.get("status_change_applied") is not False:
            fail(f"status change applied for {pid}")
        for suffix in [".md", ".json"]:
            hand_or_generated = WORK / (f"generated_{pid}{suffix}" if suffix == ".json" else f"generated_{pid}{suffix}")
            if not hand_or_generated.exists():
                fail(f"missing generated report {hand_or_generated}")
        hand_report = WORK / f"{pid}.md"
        if not hand_report.exists():
            fail(f"missing hand-reviewed worker report {hand_report}")

    release_summary = load_json(BASE / "unified_scope_summary_latest.json")
    if release_summary.get("database_status_counts", {}).get("unresolved_record") != 56:
        fail("release summary unresolved_record count must be 56")
    manifest = load_json(BASE / "release_manifest_latest.json")
    outputs = manifest.get("outputs", {})
    required_outputs = [
        "unresolved_triage_csv",
        "unresolved_triage_json",
        "unresolved_triage_md",
        "unresolved_resolution_summary_json",
        "unresolved_resolution_summary_md",
        "unresolved_final_resolution_md",
    ]
    missing = [key for key in required_outputs if key not in outputs]
    if missing:
        fail(f"manifest missing unresolved outputs: {missing}")

    print(json.dumps({
        "ok": True,
        "triage_rows": len(rows),
        "paper_distribution": dict(by_paper),
        "status_change_applied_count": summary.get("status_change_applied_count"),
        "release_unresolved_record_count": release_summary["database_status_counts"]["unresolved_record"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
