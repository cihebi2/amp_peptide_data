#!/usr/bin/env python3
"""Generate a deterministic stratified validation manifest for NAR v1 RC1.

The manifest is for downstream manual/source-reviewed validation. It samples
database audit rows across database, audit status, and primary validation
category, with deliberate oversampling of rare and high-risk non-source-
verified strata.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "releases" / "amp_evidence_atlas_v1_rc1"
FREEZE_DIR = ROOT / "reports" / "nar_resource_freeze_v1"
OUTDIR = FREEZE_DIR / "manual_validation"
AUDIT_TABLE = RELEASE_DIR / "database_record_audits.tsv"
RELEASE_MANIFEST = RELEASE_DIR / "release_manifest.json"

DEFAULT_SEED = "amp-evidence-atlas-v1-rc1-validation-20260622"
DEFAULT_STATUS_QUOTAS = {
    "source_verified": 120,
    "source_conflict": 120,
    "sequence_modified_not_normalized": 70,
    "database_only_no_primary_source": 60,
    "unresolved_record": 50,
}

MIN_DATABASE_QUOTAS = {
    "APD6": 25,
    "CAMP": 25,
    "DBAASP": 0,
    "DRAMP": 45,
    "dbAMP": 25,
    "unknown": 3,
}

NON_SOURCE_CATEGORY_PRIORITY = [
    "unresolved_or_missing_material",
    "database_only_no_primary_source",
    "mechanism_or_claim_scope",
    "row_granularity",
    "target_or_organism",
    "sequence_or_modification",
    "activity_value_or_unit",
    "other",
]

FIELDNAMES = [
    "sample_id",
    "release_id",
    "release_version",
    "sampling_seed",
    "sample_set",
    "sample_reason",
    "database",
    "status",
    "primary_validation_category",
    "difference_categories",
    "paper_id",
    "doi",
    "source_id",
    "audit_record_id",
    "record_index",
    "public_v1_included",
    "review_status",
    "publication_grade",
    "database_subject",
    "database_measure",
    "database_value",
    "database_unit",
    "primary_source_subject",
    "primary_source_value",
    "primary_source_unit",
    "sequence",
    "primary_source_sequence",
    "matched_activity_record_id",
    "release_table_path",
    "release_row_locator",
    "final_artifact_path",
    "source_locator_summary",
    "reviewer_decision",
    "reviewer_error_class",
    "reviewer_notes",
    "reviewed_by",
    "reviewed_at",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise TypeError(f"expected object in {path}")
    return data


def read_rows() -> list[dict[str, str]]:
    with AUDIT_TABLE.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, dialect="excel-tab"))
    for idx, row in enumerate(rows, 1):
        row["_release_row_number"] = str(idx + 1)  # include header row
    return rows


def categories(row: dict[str, str]) -> list[str]:
    return [item for item in row.get("difference_categories", "").split(";") if item]


def primary_validation_category(row: dict[str, str]) -> str:
    status = row.get("status", "")
    if status == "source_verified":
        return "source_verified_baseline"
    cats = set(categories(row))
    for cat in NON_SOURCE_CATEGORY_PRIORITY:
        if cat in cats:
            return cat
    return "other"


def stable_key(row: dict[str, str], seed: str) -> str:
    text = "|".join(
        [
            seed,
            row.get("audit_record_id", ""),
            row.get("paper_id", ""),
            row.get("source_id", ""),
            row.get("record_index", ""),
        ]
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compact(value: str, limit: int = 260) -> str:
    text = " ".join((value or "").split())
    if len(text) > limit:
        return text[: limit - 1] + "..."
    return text


def decode_jsonish(value: str) -> Any:
    if not value:
        return ""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def public_locator_summary(row: dict[str, str]) -> str:
    parts = []
    for key in ("source_locator", "traceability", "citation_traceability"):
        value = row.get(key, "")
        if not value:
            continue
        decoded = decode_jsonish(value)
        if isinstance(decoded, list):
            decoded = [
                {k: v for k, v in item.items() if k in {"kind", "path", "locator", "source_path", "source_record_id"}}
                if isinstance(item, dict)
                else item
                for item in decoded[:2]
            ]
        elif isinstance(decoded, dict):
            decoded = {
                k: v
                for k, v in decoded.items()
                if k in {"kind", "path", "locator", "source_path", "source_record_id", "canonical_doi", "canonical_pmid"}
            }
        parts.append(f"{key}={compact(json.dumps(decoded, ensure_ascii=False, sort_keys=True), 220)}")
    return " ; ".join(parts[:2])


def row_to_sample(row: dict[str, str], sample_id: str, seed: str, release_meta: dict[str, str], reason: str) -> dict[str, str]:
    return {
        "sample_id": sample_id,
        "release_id": release_meta["release_id"],
        "release_version": release_meta["release_version"],
        "sampling_seed": seed,
        "sample_set": "manual_stratified_validation_v1_rc1",
        "sample_reason": reason,
        "database": row.get("database", ""),
        "status": row.get("status", ""),
        "primary_validation_category": primary_validation_category(row),
        "difference_categories": row.get("difference_categories", ""),
        "paper_id": row.get("paper_id", ""),
        "doi": row.get("doi", ""),
        "source_id": row.get("source_id", ""),
        "audit_record_id": row.get("audit_record_id", ""),
        "record_index": row.get("record_index", ""),
        "public_v1_included": row.get("public_v1_included", ""),
        "review_status": row.get("review_status", ""),
        "publication_grade": row.get("publication_grade", ""),
        "database_subject": row.get("database_subject", ""),
        "database_measure": row.get("database_measure", ""),
        "database_value": row.get("database_value", ""),
        "database_unit": row.get("database_unit", ""),
        "primary_source_subject": row.get("primary_source_subject", ""),
        "primary_source_value": row.get("primary_source_value", ""),
        "primary_source_unit": row.get("primary_source_unit", ""),
        "sequence": row.get("sequence", ""),
        "primary_source_sequence": row.get("primary_source_sequence", ""),
        "matched_activity_record_id": row.get("matched_activity_record_id", ""),
        "release_table_path": "releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv",
        "release_row_locator": f"tsv_row={row.get('_release_row_number', '')}",
        "final_artifact_path": row.get("source_final_path", ""),
        "source_locator_summary": public_locator_summary(row),
        "reviewer_decision": "",
        "reviewer_error_class": "",
        "reviewer_notes": "",
        "reviewed_by": "",
        "reviewed_at": "",
    }


def add_row(
    selected: list[dict[str, str]],
    used: set[str],
    row: dict[str, str],
    seed: str,
    release_meta: dict[str, str],
    reason: str,
) -> bool:
    audit_id = row.get("audit_record_id", "")
    if audit_id in used:
        return False
    sample_id = f"VAL{len(selected) + 1:04d}"
    selected.append(row_to_sample(row, sample_id, seed, release_meta, reason))
    used.add(audit_id)
    return True


def choose_from_group(group: list[dict[str, str]], used: set[str]) -> dict[str, str] | None:
    for row in group:
        if row.get("audit_record_id", "") not in used:
            return row
    return None


def build_sample(rows: list[dict[str, str]], seed: str, status_quotas: dict[str, int], release_meta: dict[str, str]) -> list[dict[str, str]]:
    for row in rows:
        row["_primary_validation_category"] = primary_validation_category(row)
        row["_stable_key"] = stable_key(row, seed)

    by_db_status: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    by_status_category: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    by_status: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_db: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_db_status[(row["database"], row["status"])].append(row)
        by_status_category[(row["status"], row["_primary_validation_category"])].append(row)
        by_status[row["status"]].append(row)
        by_db[row["database"]].append(row)

    for groups in (by_db_status, by_status_category, by_status, by_db):
        for key in groups:
            groups[key].sort(key=lambda row: row["_stable_key"])

    selected: list[dict[str, str]] = []
    used: set[str] = set()
    status_counts: Counter[str] = Counter()
    database_counts: Counter[str] = Counter()

    def can_add(row: dict[str, str]) -> bool:
        return status_counts[row["status"]] < status_quotas.get(row["status"], 0)

    for (database, status), group in sorted(by_db_status.items()):
        row = choose_from_group(group, used)
        if row and can_add(row):
            if add_row(selected, used, row, seed, release_meta, f"coverage:database_status:{database}:{status}"):
                status_counts[row["status"]] += 1
                database_counts[row["database"]] += 1

    for (status, category), group in sorted(by_status_category.items()):
        row = choose_from_group(group, used)
        if row and can_add(row):
            if add_row(selected, used, row, seed, release_meta, f"coverage:status_category:{status}:{category}"):
                status_counts[row["status"]] += 1
                database_counts[row["database"]] += 1

    for database, group in sorted(by_db.items()):
        row = choose_from_group(group, used)
        if row and can_add(row):
            if add_row(selected, used, row, seed, release_meta, f"coverage:database:{database}"):
                status_counts[row["status"]] += 1
                database_counts[row["database"]] += 1

    for database, min_quota in sorted(MIN_DATABASE_QUOTAS.items()):
        while database_counts[database] < min_quota:
            row = choose_from_group(by_db.get(database, []), used)
            if not row or not can_add(row):
                break
            if add_row(selected, used, row, seed, release_meta, f"min_database_quota:{database}"):
                status_counts[row["status"]] += 1
                database_counts[row["database"]] += 1

    while any(status_counts[status] < quota for status, quota in status_quotas.items()):
        progressed = False
        for status, quota in status_quotas.items():
            if status_counts[status] >= quota:
                continue
            groups = [
                group
                for (group_status, _category), group in sorted(by_status_category.items())
                if group_status == status
            ] or [by_status[status]]
            for group in groups:
                row = choose_from_group(group, used)
                if row:
                    if add_row(selected, used, row, seed, release_meta, f"quota_fill:status:{status}"):
                        status_counts[status] += 1
                        database_counts[row["database"]] += 1
                        progressed = True
                        break
            if status_counts[status] < quota and not by_status[status]:
                status_counts[status] = quota
        if not progressed:
            break

    return selected


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def summarize(samples: list[dict[str, str]], source_rows: list[dict[str, str]], manifest: dict[str, Any]) -> dict[str, Any]:
    status_counts = Counter(row["status"] for row in samples)
    database_counts = Counter(row["database"] for row in samples)
    category_counts = Counter(row["primary_validation_category"] for row in samples)
    db_status_counts = Counter(f"{row['database']}::{row['status']}" for row in samples)
    status_category_counts = Counter(f"{row['status']}::{row['primary_validation_category']}" for row in samples)
    source_status_counts = Counter(row["status"] for row in source_rows)
    source_db_counts = Counter(row["database"] for row in source_rows)
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "release_id": manifest.get("release_id"),
        "release_version": manifest.get("release_version"),
        "source_table": str(AUDIT_TABLE.relative_to(ROOT)),
        "source_row_count": len(source_rows),
        "sample_count": len(samples),
        "target_sample_range": "300-500",
        "status_counts": dict(status_counts),
        "database_counts": dict(database_counts),
        "primary_validation_category_counts": dict(category_counts),
        "database_status_counts": dict(db_status_counts),
        "status_category_counts": dict(status_category_counts),
        "source_status_counts": dict(source_status_counts),
        "source_database_counts": dict(source_db_counts),
        "reviewer_decision_allowed_values": [
            "pass",
            "minor_error",
            "major_error",
            "critical_error",
            "needs_rework",
            "unverifiable",
        ],
        "reviewer_error_class_allowed_values": [
            "",
            "none",
            "source_locator_error",
            "status_misclassification",
            "database_field_mismatch",
            "paper_field_mismatch",
            "normalization_error",
            "missing_material",
            "overclaim",
            "other",
        ],
    }


def write_protocol(path: Path, summary: dict[str, Any], manifest_csv: Path, summary_json: Path) -> None:
    lines = [
        "# Manual Stratified Validation Protocol: AMP Evidence Atlas v1 RC1",
        "",
        f"Generated at: `{summary['generated_at']}`",
        f"Release id: `{summary['release_id']}`",
        f"Release version: `{summary['release_version']}`",
        "",
        "## Purpose",
        "",
        "This manifest defines a reproducible 300-500 row validation sample for",
        "estimating quality boundaries before public NAR Database Resource claims.",
        "It validates curation decisions; it does not reopen every source paper.",
        "",
        "## Inputs",
        "",
        f"- Source release table: `{summary['source_table']}`",
        f"- Validation manifest: `{manifest_csv.relative_to(ROOT)}`",
        f"- Machine-readable summary: `{summary_json.relative_to(ROOT)}`",
        "",
        "## Sampling Design",
        "",
        f"- Total sample rows: `{summary['sample_count']}`",
        "- Deterministic seed recorded in every manifest row.",
        "- Stratification axes: database, audit status, and primary validation category.",
        "- `source_verified` rows are sampled as a baseline false-positive/false-negative check.",
        "- Non-source-verified statuses are deliberately oversampled because they define the resource novelty and risk boundary.",
        "- Rare `unresolved_record` rows are high-priority because they test whether material gaps are correctly preserved.",
        "",
        "## Sample Counts by Status",
        "",
        "| status | sampled rows |",
        "| --- | ---: |",
    ]
    for status, count in sorted(summary["status_counts"].items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend(
        [
            "",
            "## Sample Counts by Database",
            "",
            "| database | sampled rows |",
            "| --- | ---: |",
        ]
    )
    for database, count in sorted(summary["database_counts"].items()):
        lines.append(f"| `{database}` | {count} |")
    lines.extend(
        [
            "",
            "## Sample Counts by Primary Validation Category",
            "",
            "| category | sampled rows |",
            "| --- | ---: |",
        ]
    )
    for category, count in sorted(summary["primary_validation_category_counts"].items()):
        lines.append(f"| `{category}` | {count} |")
    lines.extend(
        [
            "",
            "## Reviewer Instructions",
            "",
            "For each row, the reviewer should open the release row and final artifact, then check whether the recorded status and extracted database/paper fields are supported by the available source locators.",
            "",
            "Fill these columns:",
            "",
            "| column | allowed values / meaning |",
            "| --- | --- |",
            "| `reviewer_decision` | `pass`, `minor_error`, `major_error`, `critical_error`, `needs_rework`, `unverifiable` |",
            "| `reviewer_error_class` | `none`, `source_locator_error`, `status_misclassification`, `database_field_mismatch`, `paper_field_mismatch`, `normalization_error`, `missing_material`, `overclaim`, `other` |",
            "| `reviewer_notes` | Short evidence-backed note. Do not paste copyrighted text. |",
            "| `reviewed_by` | Reviewer identifier. |",
            "| `reviewed_at` | ISO timestamp. |",
            "",
            "Decision guidance:",
            "",
            "- `pass`: status and key fields are supported by the final artifact and locators.",
            "- `minor_error`: typo or presentation issue that does not change status/category.",
            "- `major_error`: field or locator problem that changes interpretation for this row.",
            "- `critical_error`: row should not support a manuscript/resource claim without repair.",
            "- `needs_rework`: send to owner-worker or adjudicator for targeted correction.",
            "- `unverifiable`: local material is insufficient; preserve the gap instead of guessing.",
            "",
            "## Guardrails",
            "",
            "- Do not infer exact values from plots unless controlled digitization and QA exist.",
            "- Do not convert `database_only_no_primary_source` or `unresolved_record` into source-verified without primary-source evidence.",
            "- Do not treat `accepted_with_cautions` as clean.",
            "- Do not describe all non-source-verified rows as database errors.",
            "- Do not copy full text, PDFs, images, or supplementary tables into the validation output.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_outputs(sample_size: int, seed: str) -> dict[str, Any]:
    if sample_size != sum(DEFAULT_STATUS_QUOTAS.values()):
        raise ValueError(
            f"this version expects sample_size={sum(DEFAULT_STATUS_QUOTAS.values())}; "
            "adjust status quotas in the script before changing sample size"
        )
    OUTDIR.mkdir(parents=True, exist_ok=True)
    manifest = load_json(RELEASE_MANIFEST)
    rows = read_rows()
    release_meta = {
        "release_id": manifest.get("release_id", ""),
        "release_version": manifest.get("release_version", ""),
    }
    samples = build_sample(rows, seed, DEFAULT_STATUS_QUOTAS, release_meta)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    manifest_csv = OUTDIR / f"validation_manifest_{stamp}.csv"
    summary_json = OUTDIR / f"validation_summary_{stamp}.json"
    protocol_md = OUTDIR / f"validation_protocol_{stamp}.md"
    write_csv(manifest_csv, samples)
    summary = summarize(samples, rows, manifest)
    summary["sampling_seed"] = seed
    summary["status_quotas"] = DEFAULT_STATUS_QUOTAS
    summary["min_database_quotas"] = MIN_DATABASE_QUOTAS
    summary["outputs"] = {
        "manifest_csv": str(manifest_csv.relative_to(ROOT)),
        "summary_json": str(summary_json.relative_to(ROOT)),
        "protocol_md": str(protocol_md.relative_to(ROOT)),
    }
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_protocol(protocol_md, summary, manifest_csv, summary_json)

    latest_csv = OUTDIR / "validation_manifest_latest.csv"
    latest_json = OUTDIR / "validation_summary_latest.json"
    latest_md = OUTDIR / "validation_protocol_latest.md"
    shutil.copyfile(manifest_csv, latest_csv)
    shutil.copyfile(summary_json, latest_json)
    shutil.copyfile(protocol_md, latest_md)
    summary["outputs"].update(
        {
            "latest_manifest_csv": str(latest_csv.relative_to(ROOT)),
            "latest_summary_json": str(latest_json.relative_to(ROOT)),
            "latest_protocol_md": str(latest_md.relative_to(ROOT)),
        }
    )
    latest_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-size", type=int, default=sum(DEFAULT_STATUS_QUOTAS.values()))
    parser.add_argument("--seed", default=DEFAULT_SEED)
    args = parser.parse_args()
    summary = build_outputs(args.sample_size, args.seed)
    print(
        json.dumps(
            {
                "sample_count": summary["sample_count"],
                "outputs": summary["outputs"],
                "status_counts": summary["status_counts"],
                "database_counts": summary["database_counts"],
                "primary_validation_category_counts": summary["primary_validation_category_counts"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
