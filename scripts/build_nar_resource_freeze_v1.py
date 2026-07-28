#!/usr/bin/env python3
"""Build a conservative NAR-facing AMP evidence resource freeze snapshot.

This script does not change paper-level review artifacts. It reads existing
source-reviewed finals and reports, then emits release-level counts, denominator
tables, cross-tabs, and a freeze manifest for manuscript/resource planning.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers"
REPORTS = ROOT / "reports"
OUTDIR = REPORTS / "nar_resource_freeze_v1"
LANDED_PAPERS = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers")

KEY_INPUTS = [
    "reports/database_vs_literature_difference_summary_latest.json",
    "reports/database_vs_literature_difference_records_latest.csv",
    "reports/database_vs_literature_difference_examples_latest.md",
    "reports/all_reviewed_papers_aggregate_latest.json",
    "reports/source_recovery/material_source_recovery_status_latest.json",
    "docs/PAPER_REVIEW_MECHANISM_V1.md",
    "docs/PAPER_REVIEW_REPRODUCIBLE_RUNBOOK_20260511.md",
    "docs/PAPER_REVIEW_RESULTS_SUMMARY_20260511.md",
    "docs/MANUAL_DIGITIZATION_AND_ANALYSIS_REWORK_RUNBOOK_20260621.md",
]

FINAL_FILES = {
    "database": "database_record_verification.json",
    "activity": "activity_toxicity_evidence.json",
    "mechanism": "mechanism_ontology_record.json",
    "review": "review_report.json",
}

PUBLICATION_GRADE_ACCEPTED = {
    "accepted_clean",
    "accepted",
    "accepted_with_cautions",
    # publication_grade* statuses are a HIGHER grade than accepted_with_cautions; they were
    # previously excluded only because they weren't in this whitelist (a filter bug that dropped
    # 4 publication-grade papers / ~350 records). They pair with publication_grade=true.
    "publication_grade",
    "publication_grade_ready",
    "publication_grade_with_cautions",
}


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def compact(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def infer_database(record: dict[str, Any]) -> str:
    explicit = compact(record.get("database")).strip()
    if explicit:
        return explicit
    text = " ".join(
        compact(record.get(k))
        for k in ("source_id", "sequence_key", "source_table", "audit_id")
    ).lower()
    source_id = compact(record.get("source_id"))
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
    return compact(record.get("status") or record.get("layer1_status") or "unknown")


def difference_categories(record: dict[str, Any]) -> set[str]:
    """Use the current report categorization logic for cross-tab consistency."""
    status = status_of(record)
    text = " ".join(
        [
            status,
            compact(record.get("conflict_context")),
            compact(record.get("conflict_summary")),
            compact(record.get("review_notes")),
            compact(record.get("conflict_flags")),
            compact(record.get("sequence_check")),
            compact(record.get("activity_check")),
            compact(record.get("primary_source_anchor")),
            compact(record.get("database_subject")),
            compact(record.get("database_measure")),
        ]
    ).lower()
    cats: set[str] = set()
    if status == "database_only_no_primary_source" or "database-only" in text or "database_only" in text:
        cats.add("database_only_no_primary_source")
    if status == "unresolved_record" or "unresolved" in text or "missing supplementary" in text:
        cats.add("unresolved_or_missing_material")
    if (
        status == "sequence_modified_not_normalized"
        or "sequence" in text
        or "modification" in text
        or "amidation" in text
        or "d-amino" in text
        or "terminal" in text
        or "variant label" in text
    ):
        cats.add("sequence_or_modification")
    if (
        "subject" in text
        or "target" in text
        or "species" in text
        or "organism" in text
        or "cell line" in text
        or "isolate" in text
    ):
        cats.add("target_or_organism")
    if (
        "mic" in text
        or "ic50" in text
        or "fici" in text
        or "mbic" in text
        or "value" in text
        or "unit" in text
        or "range" in text
        or "table" in text
    ):
        cats.add("activity_value_or_unit")
    if "species-level" in text or "range-style" in text or "aggregat" in text or "row-level" in text:
        cats.add("row_granularity")
    if "mechanism" in text or "membrane" in text or "biofilm" in text:
        cats.add("mechanism_or_claim_scope")
    return cats or {"other"}


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str] | None = None) -> int:
    rows = list(rows)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def add_count(counter: dict[tuple[str, ...], int], *keys: str) -> None:
    counter[tuple(keys)] += 1


def collect_paper_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    paper_rows: list[dict[str, Any]] = []
    aggregate = load_json(ROOT / "reports/all_reviewed_papers_aggregate_latest.json", {})
    for paper_dir in sorted(PAPERS.glob("*")):
        if not paper_dir.is_dir():
            continue
        paper_id = paper_dir.name
        final = paper_dir / "final"
        paths = {kind: final / filename for kind, filename in FINAL_FILES.items()}
        review = load_json(paths["review"], {}) or {}
        db = load_json(paths["database"], {}) or {}
        act = load_json(paths["activity"], {}) or {}
        mech = load_json(paths["mechanism"], {}) or {}
        review_status = compact(review.get("review_status") or review.get("status"))
        publication_grade = bool(review.get("publication_grade"))
        public_v1_included = publication_grade and review_status in PUBLICATION_GRADE_ACCEPTED
        exclusion_reason = ""
        if not public_v1_included:
            if not paths["review"].exists():
                exclusion_reason = "missing_review_report"
            elif not publication_grade:
                exclusion_reason = review_status or "not_publication_grade"
            else:
                exclusion_reason = f"review_status_not_in_public_set:{review_status}"
        activity_records = act.get("activity_records") or act.get("records") or []
        mechanism_claims = mech.get("mechanism_claims") or mech.get("claims") or []
        record_audits = db.get("record_audits") or db.get("records") or []
        paper_rows.append(
            {
                "paper_id": paper_id,
                "doi": compact(review.get("doi") or db.get("doi") or act.get("doi") or mech.get("doi")),
                "review_status": review_status,
                "publication_grade": publication_grade,
                "source_reviewed": bool(review.get("source_reviewed")),
                "public_v1_included": public_v1_included,
                "exclusion_reason": exclusion_reason,
                "database_audit_records": len(record_audits),
                "activity_records": len(activity_records),
                "mechanism_claims": len(mechanism_claims),
                "database_final_exists": paths["database"].exists(),
                "activity_final_exists": paths["activity"].exists(),
                "mechanism_final_exists": paths["mechanism"].exists(),
                "review_report_exists": paths["review"].exists(),
            }
        )
    return paper_rows, aggregate


def build_scope_reconciliation(paper_rows: list[dict[str, Any]], aggregate: dict[str, Any]) -> dict[str, Any]:
    """Reconcile legacy queue paper counts with current final-artifact counts."""
    final_ids = {row["paper_id"] for row in paper_rows}
    aggregate_rows = [
        row for row in aggregate.get("papers", [])
        if isinstance(row, dict) and row.get("paper_id")
    ]
    aggregate_ids = {str(row["paper_id"]) for row in aggregate_rows}

    only_in_aggregate = []
    for paper_id in sorted(aggregate_ids - final_ids):
        rows = [row for row in aggregate_rows if str(row.get("paper_id")) == paper_id]
        landed_dir = LANDED_PAPERS / paper_id
        primary_xml_dir = landed_dir / "xml"
        primary_pdf_dir = landed_dir / "pdf"
        only_in_aggregate.append(
            {
                "paper_id": paper_id,
                "queue_rows": len(rows),
                "terminal_statuses": sorted({compact(row.get("terminal_status")) for row in rows}),
                "result_statuses": sorted({compact(row.get("result_status")) for row in rows}),
                "refined_statuses": sorted({compact(row.get("refined_status")) for row in rows}),
                "recommended_next_actions": sorted({compact(row.get("recommended_next_action")) for row in rows}),
                "run_bases": sorted({compact(row.get("run_base")) for row in rows}),
                "lanes": sorted({compact(row.get("lane")) for row in rows}),
                "lane_summaries": sorted({compact(row.get("lane_summary")) for row in rows}),
                "paper_dir_exists": (PAPERS / paper_id).exists(),
                "final_dir_exists": (PAPERS / paper_id / "final").exists(),
                "review_report_exists": (PAPERS / paper_id / "final" / FINAL_FILES["review"]).exists(),
                "landed_dir": str(landed_dir),
                "landed_dir_exists": landed_dir.exists(),
                "primary_xml_dir_exists": primary_xml_dir.exists(),
                "primary_pdf_dir_exists": primary_pdf_dir.exists(),
                "supplementary_dir_exists": (landed_dir / "supplementary").exists(),
                "reconciliation_class": "legacy_queue_initial_failure_without_final_artifacts",
                "release_inclusion_decision": "exclude_from_final_artifact_universe_route_to_source_staging_or_infra_recovery",
            }
        )

    only_in_final = []
    for paper_id in sorted(final_ids - aggregate_ids):
        only_in_final.append(
            {
                "paper_id": paper_id,
                "review_status": next(row["review_status"] for row in paper_rows if row["paper_id"] == paper_id),
                "public_v1_included": next(row["public_v1_included"] for row in paper_rows if row["paper_id"] == paper_id),
            }
        )

    return {
        "legacy_queue_unique_paper_count": aggregate.get("unique_paper_count"),
        "final_artifact_paper_count": len(final_ids),
        "only_in_legacy_queue_count": len(only_in_aggregate),
        "only_in_final_artifacts_count": len(only_in_final),
        "only_in_legacy_queue": only_in_aggregate,
        "only_in_final_artifacts": only_in_final,
        "interpretation": (
            "The legacy queue aggregate includes papers that reached terminal queue status even when "
            "bootstrap failed before final paper artifacts were created. The freeze paper universe is "
            "defined by current papers/*/final review artifacts."
        ),
    }


def write_scope_reconciliation_md(reconciliation: dict[str, Any]) -> None:
    lines = [
        "# Scope Reconciliation: 1471 vs 1472",
        "",
        "This note reconciles the historical queue aggregate paper count with the current",
        "freeze final-artifact paper universe.",
        "",
        "| Count | Value |",
        "| --- | ---: |",
        f"| Legacy queue unique papers | {reconciliation['legacy_queue_unique_paper_count']} |",
        f"| Current final artifact papers | {reconciliation['final_artifact_paper_count']} |",
        f"| Only in legacy queue | {reconciliation['only_in_legacy_queue_count']} |",
        f"| Only in final artifacts | {reconciliation['only_in_final_artifacts_count']} |",
        "",
        "## Decision",
        "",
        "The v1 freeze paper universe uses current `papers/*/final/review_report.json`",
        "artifacts, so the main release count remains 1471. Historical queue-only",
        "items remain visible in this reconciliation note and should be routed to",
        "source staging or infrastructure recovery before they can enter a future",
        "publication-grade release.",
        "",
        "## Queue-only papers",
        "",
        "| paper_id | terminal_status | result_status | action | material state |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in reconciliation["only_in_legacy_queue"]:
        material_state = (
            f"landed={row['landed_dir_exists']}; "
            f"primary_xml={row['primary_xml_dir_exists']}; "
            f"primary_pdf={row['primary_pdf_dir_exists']}; "
            f"supplementary={row['supplementary_dir_exists']}"
        )
        lines.append(
            "| `{paper_id}` | `{terminal}` | `{result}` | `{action}` | {material} |".format(
                paper_id=row["paper_id"],
                terminal=";".join(row["terminal_statuses"]),
                result=";".join(row["result_statuses"]),
                action=";".join(row["recommended_next_actions"]),
                material=material_state,
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            reconciliation["interpretation"],
            "",
        ]
    )
    (OUTDIR / "scope_reconciliation_1471_vs_1472_latest.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def collect_database_audit_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    audit_rows: list[dict[str, Any]] = []
    status_by_database: dict[tuple[str, ...], int] = defaultdict(int)
    status_by_source_table: dict[tuple[str, ...], int] = defaultdict(int)
    category_by_database: dict[tuple[str, ...], int] = defaultdict(int)
    review_status_by_database: dict[tuple[str, ...], int] = defaultdict(int)
    database_papers: dict[str, set[str]] = defaultdict(set)
    database_status_papers: dict[tuple[str, str], set[str]] = defaultdict(set)
    database_totals: Counter[str] = Counter()

    for db_path in sorted(PAPERS.glob("*/final/database_record_verification.json")):
        paper_id = db_path.parts[-3]
        db_data = load_json(db_path, {}) or {}
        review_path = db_path.parent / "review_report.json"
        review = load_json(review_path, {}) or {}
        paper_review_status = compact(review.get("review_status") or db_data.get("review_status") or "")
        public_v1_included = bool(review.get("publication_grade")) and paper_review_status in PUBLICATION_GRADE_ACCEPTED
        for idx, record in enumerate(db_data.get("record_audits") or db_data.get("records") or [], 1):
            if not isinstance(record, dict):
                continue
            database = infer_database(record)
            status = status_of(record)
            source_table = compact(record.get("source_table") or "unknown")
            cats = difference_categories(record)
            database_papers[database].add(paper_id)
            database_status_papers[(database, status)].add(paper_id)
            database_totals[database] += 1
            add_count(status_by_database, database, status)
            add_count(status_by_source_table, source_table, status)
            add_count(review_status_by_database, database, paper_review_status or "unknown")
            for cat in cats:
                add_count(category_by_database, database, cat)
            audit_rows.append(
                {
                    "paper_id": paper_id,
                    "record_index": idx,
                    "database": database,
                    "source_table": source_table,
                    "status": status,
                    "difference_categories": ";".join(sorted(cats)),
                    "source_id": compact(record.get("source_id") or record.get("sequence_key")),
                    "sequence_key": compact(record.get("sequence_key")),
                    "review_status": paper_review_status,
                    "public_v1_included": public_v1_included,
                }
            )

    crosstabs = {
        "status_by_database": status_by_database,
        "status_by_source_table": status_by_source_table,
        "category_by_database": category_by_database,
        "review_status_by_database": review_status_by_database,
    }
    metadata = {
        "database_papers": {k: len(v) for k, v in database_papers.items()},
        "database_status_papers": {f"{k[0]}::{k[1]}": len(v) for k, v in database_status_papers.items()},
        "database_totals": dict(database_totals),
    }
    return audit_rows, {"crosstabs": crosstabs, "metadata": metadata}


def make_database_denominators(audit_rows: list[dict[str, Any]], paper_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_db: dict[str, Counter[str]] = defaultdict(Counter)
    db_papers: dict[str, set[str]] = defaultdict(set)
    included_by_db: dict[str, Counter[str]] = defaultdict(Counter)
    for row in audit_rows:
        db = row["database"]
        status = row["status"]
        by_db[db]["total_audit_rows"] += 1
        by_db[db][status] += 1
        if status != "source_verified":
            by_db[db]["non_source_verified"] += 1
        db_papers[db].add(row["paper_id"])
        if row["public_v1_included"]:
            included_by_db[db]["public_v1_audit_rows"] += 1
            if status != "source_verified":
                included_by_db[db]["public_v1_non_source_verified"] += 1

    rows: list[dict[str, Any]] = []
    for db in sorted(by_db):
        total = by_db[db]["total_audit_rows"]
        non = by_db[db]["non_source_verified"]
        rows.append(
            {
                "database": db,
                "total_audit_rows_denominator": total,
                "paper_count_with_rows": len(db_papers[db]),
                "source_verified": by_db[db]["source_verified"],
                "source_conflict": by_db[db]["source_conflict"],
                "sequence_modified_not_normalized": by_db[db]["sequence_modified_not_normalized"],
                "database_only_no_primary_source": by_db[db]["database_only_no_primary_source"],
                "unresolved_record": by_db[db]["unresolved_record"],
                "non_source_verified": non,
                "non_source_verified_rate": round(non / total, 6) if total else "",
                "public_v1_audit_rows": included_by_db[db]["public_v1_audit_rows"],
                "public_v1_non_source_verified": included_by_db[db]["public_v1_non_source_verified"],
                "denominator_note": "Audit-row denominator from existing final/database_record_verification.json record_audits; not raw source-database universe size.",
            }
        )
    return rows


def rows_from_counter(counter: dict[tuple[str, ...], int], names: list[str]) -> list[dict[str, Any]]:
    rows = []
    for key, count in sorted(counter.items()):
        row = {name: value for name, value in zip(names, key)}
        row["count"] = count
        rows.append(row)
    return rows


def artifact_record(path: Path) -> dict[str, Any]:
    if path.name == "release_manifest_latest.json":
        return {
            "path": rel(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else None,
            "sha256": None,
            "checksum_note": "self-referential manifest checksum omitted",
        }
    return {
        "path": rel(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }


def write_readme(summary: dict[str, Any], manifest: dict[str, Any], row_counts: dict[str, int]) -> None:
    """Write a human-readable companion for the machine-readable freeze files."""
    unresolved_triage = OUTDIR / "unresolved_records_triage_latest.csv"
    unresolved_triage_rows = ""
    if unresolved_triage.exists():
        with unresolved_triage.open(encoding="utf-8", newline="") as fh:
            unresolved_triage_rows = str(sum(1 for _ in csv.DictReader(fh)))
    needs_rework_triage = OUTDIR / "needs_targeted_rework_triage_latest.csv"
    needs_rework_rows = ""
    if needs_rework_triage.exists():
        with needs_rework_triage.open(encoding="utf-8", newline="") as fh:
            needs_rework_rows = str(sum(1 for _ in csv.DictReader(fh)))
    lines = [
        "# NAR Resource Freeze v1 Candidate",
        "",
        f"Generated at: `{summary['generated_at']}`",
        f"Release id: `{summary['release_id']}`",
        "Status: `freeze_candidate`",
        "",
        "This directory is a conservative release-planning snapshot. It is not a",
        "submission-ready public NAR database package until the public website/API,",
        "bulk downloads, manual stratified validation, database source licenses, and",
        "the 1471-vs-1472 scope reconciliation is disclosed in the manuscript.",
        "",
        "## Scope",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
    ]
    for key, value in summary["scope"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Core Outputs",
            "",
            "| File | Rows | Purpose |",
            "| --- | ---: | --- |",
            f"| `{manifest['outputs']['manifest']}` | 1 | Release inputs, checksums, output paths, and inclusion rule. |",
            f"| `{manifest['outputs']['summary']}` | 1 | Unified paper/record/activity/mechanism scope summary. |",
            f"| `{manifest['outputs']['paper_scope']}` | {row_counts.get('paper_scope', '')} | One row per paper final artifact with inclusion and artifact counts. |",
            f"| `{manifest['outputs']['excluded_papers']}` | {row_counts.get('excluded_papers', '')} | Papers excluded from the public v1 candidate subset. |",
            f"| `{manifest['outputs']['database_denominators']}` | {row_counts.get('database_denominators', '')} | Audit-row denominators by database; not raw source-database universe sizes. |",
            f"| `{manifest['outputs']['status_by_database']}` | {row_counts.get('status_by_database', '')} | Database audit status cross-tab by database. |",
            f"| `{manifest['outputs']['category_by_database']}` | {row_counts.get('category_by_database', '')} | Multilabel difference-category cross-tab by database. |",
            f"| `{manifest['outputs']['status_by_source_table']}` | {row_counts.get('status_by_source_table', '')} | Audit status cross-tab by source table. |",
            f"| `{manifest['outputs']['review_status_by_database']}` | {row_counts.get('review_status_by_database', '')} | Paper review-status cross-tab over audit rows by database. |",
            f"| `{manifest['outputs']['scope_reconciliation_md']}` | 1 | Explains why legacy queue count is 1472 while final-artifact universe is 1471. |",
            f"| `reports/nar_resource_freeze_v1/unresolved_records_triage_latest.md` | {unresolved_triage_rows} | Triage of unresolved audit rows by paper, database, blocker class, and next queue. |",
            f"| `reports/nar_resource_freeze_v1/needs_targeted_rework_triage_latest.md` | {needs_rework_rows} | Triage of needs-targeted-rework papers into owner-worker queue versus material/digitization backlog. |",
            "",
            "## Interpretation Guardrails",
            "",
            "- `public_v1_candidate_papers` requires `publication_grade=true` and accepted-like `review_status` in `papers/*/final/review_report.json`.",
            "- `accepted_with_cautions` is not clean; cautions and conflicts remain visible.",
            "- Non-`source_verified` rows are evidence discordance/provenance gaps, not automatically database errors.",
            "- Difference categories are multilabel and must not be summed as unique record counts.",
            "- Denominators are audit-row denominators from existing final artifacts, not the full raw universe of APD6/DBAASP/DRAMP/CAMP/dbAMP.",
            "- The `1471` vs `1472` gap is one queue-only initial failure without final artifacts; see the scope reconciliation files.",
            "- The 56 `unresolved_record` rows are triaged separately; they should not be promoted to `source_verified` without primary-source evidence.",
            "",
            "## Rebuild",
            "",
            "```bash",
            "python scripts/build_nar_resource_freeze_v1.py",
            "```",
            "",
            "Validate with:",
            "",
            "```bash",
            "python -m json.tool reports/nar_resource_freeze_v1/release_manifest_latest.json >/dev/null",
            "python -m json.tool reports/nar_resource_freeze_v1/unified_scope_summary_latest.json >/dev/null",
            "```",
            "",
            "## Unresolved Record Processing",
            "",
            "Rebuild and validate the unresolved-record closure package with:",
            "",
            "```bash",
            "python scripts/triage_unresolved_records.py",
            "python scripts/write_unresolved_resolution_reports.py",
            "python scripts/build_nar_resource_freeze_v1.py",
            "python scripts/validate_unresolved_processing.py",
            "```",
            "",
            "The three `<paper_id>.md` files under `reports/nar_resource_freeze_v1/unresolved_work/` are hand-reviewed worker/source-review artifacts. The `generated_<paper_id>.*` files are script-generated summaries and may be safely regenerated.",
            "",
            "## Needs-Targeted-Rework Processing",
            "",
            f"Rebuild and validate the current {needs_rework_rows or 'needs-targeted-rework'}-paper needs-targeted-rework closure package with:",
            "",
            "```bash",
            "python scripts/triage_needs_targeted_rework.py",
            "python scripts/write_needs_targeted_rework_resolution_reports.py",
            "python scripts/build_nar_resource_freeze_v1.py",
            "python scripts/validate_needs_targeted_rework_processing.py",
            "```",
            "",
            "This package does not promote papers to accepted/publication-grade. It separates the current-packet owner-worker rework queue from source-staging/digitization backlog.",
            "",
            "The current owner-worker rework queue is split into 5 lanes at `reports/nar_resource_freeze_v1/needs_targeted_rework_work/owner_worker_rework_manifest_latest.json`; each paper has a refreshed `rework_context/<paper_id>/CODEX_REVIEW_PROMPT.md`.",
            "",
        ]
    )
    (OUTDIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    paper_rows, aggregate = collect_paper_rows()
    scope_reconciliation = build_scope_reconciliation(paper_rows, aggregate)
    audit_rows, audit_meta = collect_database_audit_rows()
    denominators = make_database_denominators(audit_rows, paper_rows)

    review_status_counts = Counter(row["review_status"] or "unknown" for row in paper_rows)
    public_v1_included = [row for row in paper_rows if row["public_v1_included"]]
    excluded = [row for row in paper_rows if not row["public_v1_included"]]
    status_counts = Counter(row["status"] for row in audit_rows)
    category_counts: Counter[str] = Counter()
    for row in audit_rows:
        for cat in row["difference_categories"].split(";"):
            category_counts[cat] += 1

    input_files = []
    for item in KEY_INPUTS:
        path = ROOT / item
        input_files.append(
            {
                "path": item,
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else None,
                "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
            }
        )

    summary = {
        "generated_at": generated_at,
        "release_id": "amp-evidence-audit-v1-freeze-candidate",
        "completion_claim": "freeze_candidate_summary_not_public_nar_submission_ready",
        "scope": {
            "paper_final_artifact_count": len(paper_rows),
            "public_v1_candidate_papers": len(public_v1_included),
            "excluded_or_non_publication_grade_papers": len(excluded),
            "database_audit_rows": len(audit_rows),
            "source_verified_rows": status_counts.get("source_verified", 0),
            "non_source_verified_rows": len(audit_rows) - status_counts.get("source_verified", 0),
            "activity_records": sum(int(row["activity_records"]) for row in paper_rows),
            "mechanism_claims": sum(int(row["mechanism_claims"]) for row in paper_rows),
        },
        "review_status_counts": dict(review_status_counts),
        "database_status_counts": dict(status_counts),
        "difference_category_counts_multilabel": dict(category_counts),
        "legacy_queue_aggregate": {
            "unique_paper_count": aggregate.get("unique_paper_count"),
            "accepted_after_rework_count": aggregate.get("accepted_after_rework_count"),
            "nonaccepted_count": aggregate.get("nonaccepted_count"),
            "completion_claim": aggregate.get("completion_claim"),
        },
        "scope_reconciliation": {
            "legacy_queue_unique_paper_count": scope_reconciliation["legacy_queue_unique_paper_count"],
            "final_artifact_paper_count": scope_reconciliation["final_artifact_paper_count"],
            "only_in_legacy_queue_count": scope_reconciliation["only_in_legacy_queue_count"],
            "only_in_final_artifacts_count": scope_reconciliation["only_in_final_artifacts_count"],
            "decision": "Use final_artifact_paper_count for the v1 freeze paper universe; queue-only failures remain a recovery backlog.",
        },
        "interpretation_notes": [
            "public_v1_candidate_papers uses final/review_report.json publication_grade=true and accepted-like review_status.",
            "database denominators are audit-row denominators, not the full raw universe of each source database.",
            "difference categories are multilabel and must not be summed as unique records.",
            "non_source_verified means evidence discordance/provenance gap, not necessarily database error.",
        ],
    }

    manifest = {
        "release_id": summary["release_id"],
        "generated_at": generated_at,
        "status": "freeze_candidate",
        "not_submission_ready_until": [
            "public website/API/download release exists",
            "manual stratified validation completed",
            "database source versions/licenses frozen",
            "1471-vs-1472 scope reconciliation disclosed in manuscript",
        ],
        "inclusion_rule_public_v1_candidate": {
            "publication_grade": True,
            "review_status_in": sorted(PUBLICATION_GRADE_ACCEPTED),
            "source": "papers/*/final/review_report.json",
        },
        "outputs": {
            "summary": rel(OUTDIR / "unified_scope_summary_latest.json"),
            "manifest": rel(OUTDIR / "release_manifest_latest.json"),
            "paper_scope": rel(OUTDIR / "paper_scope_latest.csv"),
            "excluded_papers": rel(OUTDIR / "excluded_or_non_publication_grade_papers_latest.csv"),
            "database_denominators": rel(OUTDIR / "database_denominators_latest.csv"),
            "status_by_database": rel(OUTDIR / "crosstab_status_by_database_latest.csv"),
            "category_by_database": rel(OUTDIR / "crosstab_category_by_database_latest.csv"),
            "status_by_source_table": rel(OUTDIR / "crosstab_status_by_source_table_latest.csv"),
            "review_status_by_database": rel(OUTDIR / "crosstab_review_status_by_database_latest.csv"),
            "scope_reconciliation_json": rel(OUTDIR / "scope_reconciliation_1471_vs_1472_latest.json"),
            "scope_reconciliation_md": rel(OUTDIR / "scope_reconciliation_1471_vs_1472_latest.md"),
            "unresolved_triage_csv": rel(OUTDIR / "unresolved_records_triage_latest.csv"),
            "unresolved_triage_json": rel(OUTDIR / "unresolved_records_triage_latest.json"),
            "unresolved_triage_md": rel(OUTDIR / "unresolved_records_triage_latest.md"),
            "unresolved_resolution_summary_json": rel(OUTDIR / "unresolved_work" / "summary_latest.json"),
            "unresolved_resolution_summary_md": rel(OUTDIR / "unresolved_work" / "summary_latest.md"),
            "unresolved_final_resolution_md": rel(OUTDIR / "unresolved_work" / "final_resolution_summary.md"),
            "needs_rework_triage_csv": rel(OUTDIR / "needs_targeted_rework_triage_latest.csv"),
            "needs_rework_triage_json": rel(OUTDIR / "needs_targeted_rework_triage_latest.json"),
            "needs_rework_triage_md": rel(OUTDIR / "needs_targeted_rework_triage_latest.md"),
            "needs_rework_resolution_summary_json": rel(OUTDIR / "needs_targeted_rework_work" / "summary_latest.json"),
            "needs_rework_resolution_summary_md": rel(OUTDIR / "needs_targeted_rework_work" / "summary_latest.md"),
            "needs_rework_owner_queue_csv": rel(OUTDIR / "needs_targeted_rework_work" / "owner_worker_rework_queue_latest.csv"),
            "needs_rework_material_backlog_csv": rel(OUTDIR / "needs_targeted_rework_work" / "material_or_digitization_backlog_latest.csv"),
            "needs_rework_context_build_json": rel(OUTDIR / "needs_targeted_rework_work" / "context_build_latest.json"),
            "needs_rework_owner_lane_manifest_json": rel(OUTDIR / "needs_targeted_rework_work" / "owner_worker_rework_manifest_latest.json"),
            "needs_rework_material_backlog_audit_json": rel(OUTDIR / "needs_targeted_rework_work" / "material_backlog_audit_latest.json"),
            "needs_rework_material_backlog_audit_csv": rel(OUTDIR / "needs_targeted_rework_work" / "material_backlog_audit_latest.csv"),
            "needs_rework_material_backlog_audit_md": rel(OUTDIR / "needs_targeted_rework_work" / "material_backlog_audit_latest.md"),
            "needs_rework_material_source_staging_json": rel(OUTDIR / "needs_targeted_rework_work" / "material_source_staging_latest.json"),
            "needs_rework_material_source_staging_csv": rel(OUTDIR / "needs_targeted_rework_work" / "material_source_staging_latest.csv"),
            "needs_rework_material_source_staging_md": rel(OUTDIR / "needs_targeted_rework_work" / "material_source_staging_latest.md"),
            "needs_rework_manual_digitization_candidates_csv": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_candidates_latest.csv"),
            "needs_rework_source_staging_candidates_csv": rel(OUTDIR / "needs_targeted_rework_work" / "source_staging_candidates_latest.csv"),
            "needs_rework_still_unrecoverable_backlog_csv": rel(OUTDIR / "needs_targeted_rework_work" / "still_unrecoverable_backlog_latest.csv"),
            "needs_rework_material_repaired_ready_csv": rel(OUTDIR / "needs_targeted_rework_work" / "material_repaired_ready_for_retriage_latest.csv"),
            "needs_rework_manual_digitization_processing_json": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_processing_latest.json"),
            "needs_rework_manual_digitization_processing_csv": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_processing_latest.csv"),
            "needs_rework_manual_digitization_processing_md": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_processing_latest.md"),
            "needs_rework_manual_digitization_feasibility_json": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_feasibility_latest.json"),
            "needs_rework_manual_digitization_task_manifest_json": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_task_manifest_latest.json"),
            "needs_rework_manual_digitization_analysis_rework_candidates_csv": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_analysis_rework_candidates_latest.csv"),
            "needs_rework_manual_digitization_controlled_tasks_csv": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_controlled_tasks_latest.csv"),
            "needs_rework_manual_digitization_not_digitizable_csv": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_not_digitizable_latest.csv"),
            "needs_rework_manual_digitization_analysis_rework_closeout_json": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_analysis_rework_closeout_20260621.json"),
            "needs_rework_manual_digitization_analysis_rework_closeout_md": rel(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_analysis_rework_closeout_20260621.md"),
            "needs_rework_accepted_sample_audit_material_repaired_json": rel(OUTDIR / "needs_targeted_rework_work" / "accepted_sample_audit_material_repaired_20260621" / "accepted_sample_audit_latest.json"),
            "needs_rework_accepted_sample_audit_source_staged_json": rel(OUTDIR / "needs_targeted_rework_work" / "accepted_sample_audit_source_staged_20260621" / "accepted_sample_audit_latest.json"),
            "needs_rework_accepted_sample_audit_source_staging_locator_repair_json": rel(OUTDIR / "needs_targeted_rework_work" / "accepted_sample_audit_source_staging_locator_repair_20260621" / "accepted_sample_audit_latest.json"),
            "needs_rework_accepted_sample_audit_manual_digitization_analysis_rework_json": rel(OUTDIR / "needs_targeted_rework_work" / "accepted_sample_audit_manual_digitization_analysis_rework_20260621" / "accepted_sample_audit_latest.json"),
        },
        "inputs": input_files,
        "summary": summary,
    }

    (OUTDIR / "unified_scope_summary_latest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUTDIR / "release_manifest_latest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUTDIR / "scope_reconciliation_1471_vs_1472_latest.json").write_text(
        json.dumps(scope_reconciliation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_scope_reconciliation_md(scope_reconciliation)
    row_counts = {
        "paper_scope": write_csv(OUTDIR / "paper_scope_latest.csv", paper_rows),
        "excluded_papers": write_csv(OUTDIR / "excluded_or_non_publication_grade_papers_latest.csv", excluded),
        "database_denominators": write_csv(OUTDIR / "database_denominators_latest.csv", denominators),
    }
    row_counts["status_by_database"] = write_csv(
        OUTDIR / "crosstab_status_by_database_latest.csv",
        rows_from_counter(audit_meta["crosstabs"]["status_by_database"], ["database", "status"]),
    )
    row_counts["category_by_database"] = write_csv(
        OUTDIR / "crosstab_category_by_database_latest.csv",
        rows_from_counter(audit_meta["crosstabs"]["category_by_database"], ["database", "difference_category"]),
    )
    row_counts["status_by_source_table"] = write_csv(
        OUTDIR / "crosstab_status_by_source_table_latest.csv",
        rows_from_counter(audit_meta["crosstabs"]["status_by_source_table"], ["source_table", "status"]),
    )
    row_counts["review_status_by_database"] = write_csv(
        OUTDIR / "crosstab_review_status_by_database_latest.csv",
        rows_from_counter(audit_meta["crosstabs"]["review_status_by_database"], ["database", "review_status"]),
    )
    write_readme(summary, manifest, row_counts)
    manifest["output_artifacts"] = [
        artifact_record(OUTDIR / "unified_scope_summary_latest.json"),
        artifact_record(OUTDIR / "release_manifest_latest.json"),
        artifact_record(OUTDIR / "paper_scope_latest.csv"),
        artifact_record(OUTDIR / "excluded_or_non_publication_grade_papers_latest.csv"),
        artifact_record(OUTDIR / "database_denominators_latest.csv"),
        artifact_record(OUTDIR / "crosstab_status_by_database_latest.csv"),
        artifact_record(OUTDIR / "crosstab_category_by_database_latest.csv"),
        artifact_record(OUTDIR / "crosstab_status_by_source_table_latest.csv"),
        artifact_record(OUTDIR / "crosstab_review_status_by_database_latest.csv"),
        artifact_record(OUTDIR / "scope_reconciliation_1471_vs_1472_latest.json"),
        artifact_record(OUTDIR / "scope_reconciliation_1471_vs_1472_latest.md"),
        artifact_record(OUTDIR / "unresolved_records_triage_latest.csv"),
        artifact_record(OUTDIR / "unresolved_records_triage_latest.json"),
        artifact_record(OUTDIR / "unresolved_records_triage_latest.md"),
        artifact_record(OUTDIR / "unresolved_work" / "summary_latest.json"),
        artifact_record(OUTDIR / "unresolved_work" / "summary_latest.md"),
        artifact_record(OUTDIR / "unresolved_work" / "final_resolution_summary.md"),
        artifact_record(OUTDIR / "needs_targeted_rework_triage_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_triage_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_triage_latest.md"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "summary_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "summary_latest.md"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "owner_worker_rework_queue_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "material_or_digitization_backlog_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "context_build_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "owner_worker_rework_manifest_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "material_backlog_audit_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "material_backlog_audit_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "material_backlog_audit_latest.md"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "material_source_staging_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "material_source_staging_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "material_source_staging_latest.md"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_candidates_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "source_staging_candidates_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "still_unrecoverable_backlog_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "material_repaired_ready_for_retriage_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_processing_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_processing_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_processing_latest.md"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_feasibility_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_feasibility_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_feasibility_latest.md"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_task_manifest_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_analysis_rework_candidates_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_controlled_tasks_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_not_digitizable_latest.csv"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_analysis_rework_closeout_20260621.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "manual_digitization_analysis_rework_closeout_20260621.md"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "accepted_sample_audit_material_repaired_20260621" / "accepted_sample_audit_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "accepted_sample_audit_source_staged_20260621" / "accepted_sample_audit_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "accepted_sample_audit_source_staging_locator_repair_20260621" / "accepted_sample_audit_latest.json"),
        artifact_record(OUTDIR / "needs_targeted_rework_work" / "accepted_sample_audit_manual_digitization_analysis_rework_20260621" / "accepted_sample_audit_latest.json"),
        artifact_record(OUTDIR / "README.md"),
    ]
    (OUTDIR / "release_manifest_latest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "release_id": summary["release_id"],
                "outdir": rel(OUTDIR),
                "paper_final_artifact_count": len(paper_rows),
                "public_v1_candidate_papers": len(public_v1_included),
                "excluded_or_non_publication_grade_papers": len(excluded),
                "database_audit_rows": len(audit_rows),
                "source_verified_rows": status_counts.get("source_verified", 0),
                "non_source_verified_rows": len(audit_rows) - status_counts.get("source_verified", 0),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
