#!/usr/bin/env python3
"""Build a versioned public-release candidate package for AMP Evidence Atlas.

The package is a derived-data export: it contains curation tables, schemas,
checksums, and release metadata. It intentionally does not copy PDFs, XML full
text, source tables, images, or supplementary files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from build_nar_resource_freeze_v1 import (
    FINAL_FILES,
    OUTDIR as FREEZE_DIR,
    PAPERS,
    PUBLICATION_GRADE_ACCEPTED,
    ROOT,
    compact,
    difference_categories,
    infer_database,
    load_json,
    sha256_file,
    status_of,
)


RELEASE_VERSION = "v1_rc2"
RELEASE_ID = "amp-evidence-atlas-v1-rc2"
DEFAULT_OUTDIR = ROOT / "releases" / "amp_evidence_atlas_v1_rc2"


def _human_review(record):
    """Aggregate the per-record human_review list (may hold multiple verdicts) into a scalar dict."""
    hr = record.get("human_review")
    if isinstance(hr, dict):
        hr = [hr]
    if not isinstance(hr, list) or not hr:
        return {}
    verdicts = [b.get("verdict", "") for b in hr if isinstance(b, dict)]
    verdict = "confirmed" if "confirmed" in verdicts else (verdicts[0] if verdicts else "")
    first = hr[0]
    return {
        "verdict": verdict,
        "severity": first.get("severity", ""),
        "reviewer": first.get("reviewer", ""),
        "notes": " || ".join(b.get("notes", "") for b in hr if isinstance(b, dict) and b.get("notes")),
        "reviewed_at": first.get("reviewed_at", ""),
        "review_id": ",".join(b.get("review_id", "") for b in hr if isinstance(b, dict) and b.get("review_id")),
        "link_confidence": first.get("link_confidence", ""),
    }
GENERATOR_MARKER = ".generated_by_build_nar_public_release_package"

PUBLIC_SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"

COPY_FREEZE_TABLES = {
    "database_denominators_latest.csv": "database_denominators.tsv",
    "crosstab_status_by_database_latest.csv": "crosstab_status_by_database.tsv",
    "crosstab_category_by_database_latest.csv": "crosstab_category_by_database.tsv",
    "crosstab_status_by_source_table_latest.csv": "crosstab_status_by_source_table.tsv",
    "crosstab_review_status_by_database_latest.csv": "crosstab_review_status_by_database.tsv",
}

PUBLIC_LOCATOR_DROP_KEYS = {
    "abstract",
    "caption",
    "content",
    "excerpt",
    "full_text",
    "quote",
    "quoted_text",
    "raw_text",
    "sentence",
    "sentences",
    "snippet",
    "support_text",
    "supporting_text",
    "supports",
    "table_text",
    "text",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def clean_public_value(value: Any) -> Any:
    """Strip source-text-like fields while preserving locator/provenance shape."""
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, nested in value.items():
            if str(key).lower() in PUBLIC_LOCATOR_DROP_KEYS:
                continue
            cleaned[key] = clean_public_value(nested)
        return cleaned
    if isinstance(value, list):
        return [clean_public_value(item) for item in value]
    return value


def tsv_cell(value: Any) -> str:
    if value is None:
        return ""
    value = clean_public_value(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return str(value)


def as_bool_text(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value in ("True", "true", "1", 1):
        return "true"
    if value in ("False", "false", "0", 0):
        return "false"
    return ""


def safe_first(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return ""


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> int:
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=fieldnames,
            dialect="excel-tab",
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: tsv_cell(row.get(key, "")) for key in fieldnames})
            count += 1
    return count


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def collect_paper_context() -> dict[str, dict[str, Any]]:
    context: dict[str, dict[str, Any]] = {}
    for row in read_csv_rows(FREEZE_DIR / "paper_scope_latest.csv"):
        context[row["paper_id"]] = {
            "doi": row.get("doi", ""),
            "review_status": row.get("review_status", ""),
            "publication_grade": as_bool_text(row.get("publication_grade")),
            "source_reviewed": as_bool_text(row.get("source_reviewed")),
            "public_v1_included": as_bool_text(row.get("public_v1_included")),
            "exclusion_reason": row.get("exclusion_reason", ""),
        }
    return context


def final_json(paper_id: str, kind: str) -> dict[str, Any]:
    return load_json(PAPERS / paper_id / "final" / FINAL_FILES[kind], {}) or {}


def paper_rows(paper_context: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in read_csv_rows(FREEZE_DIR / "paper_scope_latest.csv"):
        paper_id = source["paper_id"]
        review = final_json(paper_id, "review")
        rows.append(
            {
                "release_id": RELEASE_ID,
                "paper_id": paper_id,
                "doi": source.get("doi", ""),
                "review_status": source.get("review_status", ""),
                "publication_grade": as_bool_text(source.get("publication_grade")),
                "source_reviewed": as_bool_text(source.get("source_reviewed")),
                "public_v1_included": as_bool_text(source.get("public_v1_included")),
                "exclusion_reason": source.get("exclusion_reason", ""),
                "database_audit_records": source.get("database_audit_records", ""),
                "activity_records": source.get("activity_records", ""),
                "mechanism_claims": source.get("mechanism_claims", ""),
                "reviewed_at": review.get("reviewed_at") or review.get("last_re_reviewed_at") or "",
                "review_model": review.get("review_model", ""),
                "reasoning_effort": review.get("reasoning_effort", ""),
                "materials_exhausted": as_bool_text(review.get("materials_exhausted")),
                "validator_contract_passed": as_bool_text(review.get("validator_contract_passed")),
                "final_outputs_ready": tsv_cell(review.get("final_layer_outputs_ready", "")),
                "caution_count": len(review.get("caution_findings") or []),
                "open_rework_ticket_count": len(review.get("remaining_open_rework_ticket_ids") or []),
                "source_final_review_path": rel(PAPERS / paper_id / "final" / FINAL_FILES["review"]),
            }
        )
    return rows


def database_audit_rows(paper_context: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for db_path in sorted(PAPERS.glob("*/final/database_record_verification.json")):
        paper_id = db_path.parts[-3]
        context = paper_context.get(paper_id, {})
        db_data = load_json(db_path, {}) or {}
        review = final_json(paper_id, "review")
        records = db_data.get("record_audits") or db_data.get("records") or []
        for idx, record in enumerate(records, 1):
            if not isinstance(record, dict):
                continue
            database = infer_database(record)
            status = status_of(record)
            cats = sorted(difference_categories(record))
            _hr = _human_review(record)
            rows.append(
                {
                    "release_id": RELEASE_ID,
                    "paper_id": paper_id,
                    "doi": context.get("doi", ""),
                    "audit_record_id": f"{paper_id}:database_audit:{idx}",
                    "record_index": idx,
                    "public_v1_included": context.get("public_v1_included", ""),
                    "review_status": context.get("review_status") or review.get("review_status", ""),
                    "publication_grade": context.get("publication_grade", ""),
                    "database": database,
                    "source_id": safe_first(record.get("source_id"), record.get("sequence_key")),
                    "sequence_key": record.get("sequence_key", ""),
                    "source_table": record.get("source_table", ""),
                    "status": status,
                    "layer1_status": safe_first(record.get("layer1_status"), status),
                    "difference_categories": ";".join(cats),
                    "record_name": safe_first(record.get("record_name"), record.get("paper_short_name")),
                    "database_subject": record.get("database_subject", ""),
                    "database_measure": record.get("database_measure", ""),
                    "database_value": record.get("database_value", ""),
                    "database_unit": record.get("database_unit", ""),
                    "primary_source_subject": record.get("primary_source_subject", ""),
                    "primary_source_value": record.get("primary_source_value", ""),
                    "primary_source_unit": record.get("primary_source_unit", ""),
                    "matched_activity_record_id": record.get("matched_activity_record_id", ""),
                    "sequence": safe_first(record.get("sequence"), record.get("database_sequence")),
                    "primary_source_sequence": record.get("primary_source_sequence", ""),
                    "name_check": record.get("name_check", ""),
                    "sequence_check": record.get("sequence_check", ""),
                    "modification_check": record.get("modification_check", ""),
                    "source_organism_check": record.get("source_organism_check", ""),
                    "activity_check": record.get("activity_check", ""),
                    "conflict_flags": record.get("conflict_flags", ""),
                    "conflict_context": record.get("conflict_context", ""),
                    "conflict_interpretation": record.get("conflict_interpretation", ""),
                    "review_notes": record.get("review_notes", ""),
                    "human_verdict": _hr.get("verdict", ""),
                    "human_severity": _hr.get("severity", ""),
                    "human_reviewer": _hr.get("reviewer", ""),
                    "human_review_notes": _hr.get("notes", ""),
                    "human_reviewed_at": _hr.get("reviewed_at", ""),
                    "human_review_id": _hr.get("review_id", ""),
                    "human_link_confidence": _hr.get("link_confidence", ""),
                    "source_locator": record.get("source_locator", ""),
                    "traceability": record.get("traceability", ""),
                    "citation_traceability": record.get("citation_traceability", ""),
                    "source_final_path": rel(db_path),
                }
            )
    return rows


def activity_rows(paper_context: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for act_path in sorted(PAPERS.glob("*/final/activity_toxicity_evidence.json")):
        paper_id = act_path.parts[-3]
        context = paper_context.get(paper_id, {})
        act_data = load_json(act_path, {}) or {}
        for idx, record in enumerate(act_data.get("activity_records") or act_data.get("records") or [], 1):
            if not isinstance(record, dict):
                continue
            rows.append(
                {
                    "release_id": RELEASE_ID,
                    "paper_id": paper_id,
                    "doi": context.get("doi", ""),
                    "activity_record_id": safe_first(record.get("record_id"), f"{paper_id}:activity:{idx}"),
                    "record_index": idx,
                    "public_v1_included": context.get("public_v1_included", ""),
                    "review_status": context.get("review_status", ""),
                    "publication_grade": context.get("publication_grade", ""),
                    "entity": safe_first(record.get("entity"), record.get("agent"), record.get("peptide")),
                    "peptide": safe_first(record.get("peptide"), record.get("agent"), record.get("entity")),
                    "sequence": record.get("sequence", ""),
                    "entity_type": safe_first(record.get("entity_type"), record.get("agent_class")),
                    "endpoint": record.get("endpoint", ""),
                    "raw_value": record.get("raw_value", ""),
                    "raw_unit": record.get("raw_unit", ""),
                    "normalized_value": record.get("normalized_value", ""),
                    "normalized_unit": record.get("normalized_unit", ""),
                    "normalization_status": record.get("normalization_status", ""),
                    "target": record.get("target", ""),
                    "assay_conditions": record.get("assay_conditions", ""),
                    "replicates_statistics": record.get("replicates_statistics", ""),
                    "evidence_ladder": record.get("evidence_ladder", ""),
                    "source_locator": record.get("source_locator", ""),
                    "database_traceability": record.get("database_traceability", ""),
                    "curation_notes": record.get("curation_notes", ""),
                    "source_final_path": rel(act_path),
                }
            )
    return rows


def mechanism_rows(paper_context: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for mech_path in sorted(PAPERS.glob("*/final/mechanism_ontology_record.json")):
        paper_id = mech_path.parts[-3]
        context = paper_context.get(paper_id, {})
        mech_data = load_json(mech_path, {}) or {}
        for idx, claim in enumerate(mech_data.get("mechanism_claims") or mech_data.get("claims") or [], 1):
            if not isinstance(claim, dict):
                continue
            rows.append(
                {
                    "release_id": RELEASE_ID,
                    "paper_id": paper_id,
                    "doi": context.get("doi", ""),
                    "mechanism_claim_id": safe_first(claim.get("claim_id"), f"{paper_id}:mechanism:{idx}"),
                    "record_index": idx,
                    "public_v1_included": context.get("public_v1_included", ""),
                    "review_status": context.get("review_status", ""),
                    "publication_grade": context.get("publication_grade", ""),
                    "claim_text": claim.get("claim_text", ""),
                    "entity_scope": claim.get("entity_scope", ""),
                    "evidence_class": claim.get("evidence_class", ""),
                    "direct_assay_types": claim.get("direct_assay_types", ""),
                    "source_locator": safe_first(claim.get("source_locator"), claim.get("source_locators")),
                    "limitations": claim.get("limitations", ""),
                    "source_reviewed": as_bool_text(safe_first(claim.get("source_reviewed"), mech_data.get("source_reviewed"))),
                    "source_final_path": rel(mech_path),
                }
            )
    return rows


def summarize_issue(record: dict[str, Any]) -> str:
    for key in (
        "conflict_summary",
        "conflict_context",
        "review_notes",
        "conflict_interpretation",
        "sequence_check",
        "activity_check",
        "primary_source_anchor",
    ):
        value = record.get(key)
        if value:
            return compact(clean_public_value(value))
    return ""


def conflict_and_caution_rows(
    paper_context: dict[str, dict[str, Any]],
    database_rows_cache: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in database_rows_cache:
        # Normally skip source_verified rows — but keep any a human reviewer CONFIRMED as an error
        # (these are automated false-negatives the human pass caught; they must remain visible).
        if row["status"] == "source_verified" and row.get("human_verdict") != "confirmed":
            continue
        rows.append(
            {
                "release_id": RELEASE_ID,
                "issue_id": row["audit_record_id"],
                "issue_scope": "database_record_audit",
                "paper_id": row["paper_id"],
                "doi": row["doi"],
                "public_v1_included": row["public_v1_included"],
                "database": row["database"],
                "source_id": row["source_id"],
                "status": row["status"],
                "difference_categories": row["difference_categories"],
                "severity_hint": "unresolved" if row["status"] == "unresolved_record" else "caution_or_conflict",
                "summary": summarize_issue(row),
                "source_locator": safe_first(row.get("source_locator"), row.get("traceability"), row.get("citation_traceability")),
                "source_final_path": row["source_final_path"],
            }
        )

    for review_path in sorted(PAPERS.glob("*/final/review_report.json")):
        paper_id = review_path.parts[-3]
        context = paper_context.get(paper_id, {})
        review = load_json(review_path, {}) or {}
        issue_groups = [
            ("paper_caution", review.get("caution_findings") or []),
            ("paper_qc_failure", review.get("qc_failure_reasons") or []),
            ("paper_rework_target", review.get("rework_targets") or []),
            ("paper_unrecoverable_gap", review.get("unrecoverable_material_gaps") or []),
            ("paper_open_rework_ticket", review.get("remaining_open_rework_ticket_ids") or []),
        ]
        for group, values in issue_groups:
            if isinstance(values, dict):
                values = [values]
            if isinstance(values, str):
                values = [values]
            if not isinstance(values, list):
                continue
            for idx, value in enumerate(values, 1):
                rows.append(
                    {
                        "release_id": RELEASE_ID,
                        "issue_id": f"{paper_id}:{group}:{idx}",
                        "issue_scope": group,
                        "paper_id": paper_id,
                        "doi": context.get("doi", ""),
                        "public_v1_included": context.get("public_v1_included", ""),
                        "database": "",
                        "source_id": "",
                        "status": context.get("review_status", ""),
                        "difference_categories": "",
                        "severity_hint": "paper_level_caution_or_blocker",
                        "summary": compact(clean_public_value(value)),
                        "source_locator": "",
                        "source_final_path": rel(review_path),
                    }
                )
    return rows


def excluded_rows() -> list[dict[str, Any]]:
    rows = []
    for row in read_csv_rows(FREEZE_DIR / "excluded_or_non_publication_grade_papers_latest.csv"):
        rows.append(
            {
                "release_id": RELEASE_ID,
                "paper_id": row.get("paper_id", ""),
                "doi": row.get("doi", ""),
                "review_status": row.get("review_status", ""),
                "publication_grade": as_bool_text(row.get("publication_grade")),
                "source_reviewed": as_bool_text(row.get("source_reviewed")),
                "public_v1_included": as_bool_text(row.get("public_v1_included")),
                "exclusion_reason": row.get("exclusion_reason", ""),
                "database_audit_records": row.get("database_audit_records", ""),
                "activity_records": row.get("activity_records", ""),
                "mechanism_claims": row.get("mechanism_claims", ""),
                "source_final_review_path": rel(PAPERS / row.get("paper_id", "") / "final" / FINAL_FILES["review"]),
            }
        )
    return rows


def copy_freeze_tsvs(outdir: Path) -> dict[str, dict[str, Any]]:
    copied: dict[str, dict[str, Any]] = {}
    for source_name, dest_name in COPY_FREEZE_TABLES.items():
        rows = read_csv_rows(FREEZE_DIR / source_name)
        if rows:
            fields = list(rows[0].keys())
        else:
            fields = []
        count = write_tsv(outdir / dest_name, rows, fields)
        copied[dest_name] = {"row_count": count, "fieldnames": fields}
    return copied


def infer_json_schema_type(field: str) -> str | list[str]:
    if field.endswith("_count") or field in {"record_index", "database_audit_records", "activity_records", "mechanism_claims"}:
        return ["integer", "string"]
    if field in {
        "publication_grade",
        "source_reviewed",
        "public_v1_included",
        "materials_exhausted",
        "validator_contract_passed",
    }:
        return ["boolean", "string"]
    return "string"


def write_schema(path: Path, title: str, fieldnames: list[str], description: str) -> None:
    schema = {
        "$schema": PUBLIC_SCHEMA_DRAFT,
        "title": title,
        "description": description,
        "type": "object",
        "additionalProperties": False,
        "properties": {
            field: {
                "type": infer_json_schema_type(field),
                "description": f"TSV column `{field}`.",
            }
            for field in fieldnames
        },
        "required": fieldnames,
    }
    write_json(path, schema)


def checksums(outdir: Path) -> list[dict[str, Any]]:
    rows = []
    excluded = {"checksums.txt", "release_manifest.json"}
    for path in sorted(p for p in outdir.rglob("*") if p.is_file() and p.name not in excluded):
        rows.append(
            {
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
                "path": str(path.relative_to(outdir)),
            }
        )
    with (outdir / "checksums.txt").open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(f"{row['sha256']}  {row['path']}\n")
    return rows


def write_licenses(outdir: Path) -> int:
    rows = [
        {
            "component": "release_package_metadata_and_derived_curation_tables",
            "license_or_status": "project_license_pending",
            "redistribution_note": "Derived curation facts, status labels, locators, and database-vs-literature audit fields only.",
        },
        {
            "component": "primary_literature_full_text_pdf_xml_images_supplements",
            "license_or_status": "not_redistributed_in_this_package",
            "redistribution_note": "This package provides paths/locators only and does not copy copyrighted source materials.",
        },
        {
            "component": "source_database_records_apd6_dbaasp_dramp_camp_dbamp",
            "license_or_status": "source_database_license_review_required_before_public_hosting",
            "redistribution_note": "Export uses audit-row identifiers and derived curation fields; verify source database terms before public deployment.",
        },
    ]
    return write_tsv(
        outdir / "LICENSES.tsv",
        rows,
        ["component", "license_or_status", "redistribution_note"],
    )


def write_readme(outdir: Path, manifest: dict[str, Any]) -> None:
    scope = manifest["source_freeze_summary"]["scope"]
    lines = [
        "# AMP Evidence Atlas v1 RC1 Release Package",
        "",
        f"Release id: `{manifest['release_id']}`",
        f"Generated at: `{manifest['generated_at']}`",
        "Status: `release_package_candidate_not_public_nar_submission_ready`",
        "",
        "This directory is a versioned derived-data package for review and resource",
        "planning. It is not yet a hosted public NAR Database Resource. Public",
        "submission still requires a website/API, manual stratified validation,",
        "database source-version/license review, and manuscript disclosure.",
        "",
        "## Scope",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
    ]
    for key, value in scope.items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Downloads",
            "",
            "| File | Rows | Description |",
            "| --- | ---: | --- |",
        ]
    )
    for item in manifest["tables"]:
        lines.append(f"| `{item['path']}` | {item['row_count']} | {item['description']} |")
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- `accepted_with_cautions` is not clean; cautions and conflicts remain visible.",
            "- Non-`source_verified` rows are evidence discordance/provenance gaps, not automatically database errors.",
            "- Difference categories are multilabel and must not be summed as unique record counts.",
            "- Denominators are audit-row denominators from existing final artifacts, not raw source-database universe sizes.",
            "- This package does not redistribute PDFs, XML full text, figures, images, or supplementary files.",
            "",
            "## Rebuild",
            "",
            "```bash",
            "python scripts/build_nar_resource_freeze_v1.py",
            "python scripts/build_nar_public_release_package.py",
            "```",
            "",
            "Validate with:",
            "",
            "```bash",
            "python -m json.tool releases/amp_evidence_atlas_v1_rc1/release_manifest.json >/dev/null",
            "(cd releases/amp_evidence_atlas_v1_rc1 && sha256sum -c checksums.txt)",
            "```",
            "",
        ]
    )
    (outdir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def build_release(outdir: Path) -> dict[str, Any]:
    if outdir.exists():
        marker = outdir / GENERATOR_MARKER
        prior_manifest = load_json(outdir / "release_manifest.json", {}) or {}
        if not marker.exists() and prior_manifest.get("release_id") != RELEASE_ID:
            raise RuntimeError(
                f"refusing to overwrite non-generated release directory: {outdir}"
            )
        shutil.rmtree(outdir)
    (outdir / "schemas").mkdir(parents=True, exist_ok=True)
    (outdir / GENERATOR_MARKER).write_text(
        "Generated by scripts/build_nar_public_release_package.py\n",
        encoding="utf-8",
    )

    freeze_manifest = load_json(FREEZE_DIR / "release_manifest_latest.json", {}) or {}
    freeze_summary = load_json(FREEZE_DIR / "unified_scope_summary_latest.json", {}) or {}
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    paper_context = collect_paper_context()

    table_specs: list[dict[str, Any]] = []

    papers_fields = [
        "release_id",
        "paper_id",
        "doi",
        "review_status",
        "publication_grade",
        "source_reviewed",
        "public_v1_included",
        "exclusion_reason",
        "database_audit_records",
        "activity_records",
        "mechanism_claims",
        "reviewed_at",
        "review_model",
        "reasoning_effort",
        "materials_exhausted",
        "validator_contract_passed",
        "final_outputs_ready",
        "caution_count",
        "open_rework_ticket_count",
        "source_final_review_path",
    ]
    count = write_tsv(outdir / "papers.tsv", paper_rows(paper_context), papers_fields)
    write_schema(outdir / "schemas" / "papers.schema.json", "papers.tsv", papers_fields, "One row per paper final artifact.")
    table_specs.append({"path": "papers.tsv", "row_count": count, "schema": "schemas/papers.schema.json", "description": "Paper-level review and inclusion metadata."})

    db_fields = [
        "release_id",
        "paper_id",
        "doi",
        "audit_record_id",
        "record_index",
        "public_v1_included",
        "review_status",
        "publication_grade",
        "database",
        "source_id",
        "sequence_key",
        "source_table",
        "status",
        "layer1_status",
        "difference_categories",
        "record_name",
        "database_subject",
        "database_measure",
        "database_value",
        "database_unit",
        "primary_source_subject",
        "primary_source_value",
        "primary_source_unit",
        "matched_activity_record_id",
        "sequence",
        "primary_source_sequence",
        "name_check",
        "sequence_check",
        "modification_check",
        "source_organism_check",
        "activity_check",
        "conflict_flags",
        "conflict_context",
        "conflict_interpretation",
        "review_notes",
        "human_verdict",
        "human_severity",
        "human_reviewer",
        "human_review_notes",
        "human_reviewed_at",
        "human_review_id",
        "human_link_confidence",
        "source_locator",
        "traceability",
        "citation_traceability",
        "source_final_path",
    ]
    db_rows = database_audit_rows(paper_context)
    count = write_tsv(outdir / "database_record_audits.tsv", db_rows, db_fields)
    write_schema(outdir / "schemas" / "database_record_audits.schema.json", "database_record_audits.tsv", db_fields, "Database audit rows aligned to paper evidence.")
    table_specs.append({"path": "database_record_audits.tsv", "row_count": count, "schema": "schemas/database_record_audits.schema.json", "description": "Database record audit rows with evidence status and sanitized locators."})

    activity_fields = [
        "release_id",
        "paper_id",
        "doi",
        "activity_record_id",
        "record_index",
        "public_v1_included",
        "review_status",
        "publication_grade",
        "entity",
        "peptide",
        "sequence",
        "entity_type",
        "endpoint",
        "raw_value",
        "raw_unit",
        "normalized_value",
        "normalized_unit",
        "normalization_status",
        "target",
        "assay_conditions",
        "replicates_statistics",
        "evidence_ladder",
        "source_locator",
        "database_traceability",
        "curation_notes",
        "source_final_path",
    ]
    count = write_tsv(outdir / "activity_observations.tsv", activity_rows(paper_context), activity_fields)
    write_schema(outdir / "schemas" / "activity_observations.schema.json", "activity_observations.tsv", activity_fields, "Activity and toxicity evidence observations.")
    table_specs.append({"path": "activity_observations.tsv", "row_count": count, "schema": "schemas/activity_observations.schema.json", "description": "Activity/toxicity observations extracted from source-reviewed final artifacts."})

    mechanism_fields = [
        "release_id",
        "paper_id",
        "doi",
        "mechanism_claim_id",
        "record_index",
        "public_v1_included",
        "review_status",
        "publication_grade",
        "claim_text",
        "entity_scope",
        "evidence_class",
        "direct_assay_types",
        "source_locator",
        "limitations",
        "source_reviewed",
        "source_final_path",
    ]
    count = write_tsv(outdir / "mechanism_claims.tsv", mechanism_rows(paper_context), mechanism_fields)
    write_schema(outdir / "schemas" / "mechanism_claims.schema.json", "mechanism_claims.tsv", mechanism_fields, "Mechanism claims with evidence class and sanitized locators.")
    table_specs.append({"path": "mechanism_claims.tsv", "row_count": count, "schema": "schemas/mechanism_claims.schema.json", "description": "Mechanism evidence claims and direct-assay classifications."})

    issue_fields = [
        "release_id",
        "issue_id",
        "issue_scope",
        "paper_id",
        "doi",
        "public_v1_included",
        "database",
        "source_id",
        "status",
        "difference_categories",
        "severity_hint",
        "summary",
        "source_locator",
        "source_final_path",
    ]
    count = write_tsv(outdir / "conflicts_and_cautions.tsv", conflict_and_caution_rows(paper_context, db_rows), issue_fields)
    write_schema(outdir / "schemas" / "conflicts_and_cautions.schema.json", "conflicts_and_cautions.tsv", issue_fields, "Non-source-verified rows and paper-level cautions or blockers.")
    table_specs.append({"path": "conflicts_and_cautions.tsv", "row_count": count, "schema": "schemas/conflicts_and_cautions.schema.json", "description": "Database discordance/provenance gaps plus paper-level cautions and blockers."})

    excluded_fields = [
        "release_id",
        "paper_id",
        "doi",
        "review_status",
        "publication_grade",
        "source_reviewed",
        "public_v1_included",
        "exclusion_reason",
        "database_audit_records",
        "activity_records",
        "mechanism_claims",
        "source_final_review_path",
    ]
    count = write_tsv(outdir / "excluded_blocked_papers.tsv", excluded_rows(), excluded_fields)
    write_schema(outdir / "schemas" / "excluded_blocked_papers.schema.json", "excluded_blocked_papers.tsv", excluded_fields, "Papers excluded from the public v1 candidate subset.")
    table_specs.append({"path": "excluded_blocked_papers.tsv", "row_count": count, "schema": "schemas/excluded_blocked_papers.schema.json", "description": "Excluded or non-publication-grade papers and reasons."})

    copied_counts = copy_freeze_tsvs(outdir)
    for path, meta in copied_counts.items():
        count = meta["row_count"]
        fields = meta["fieldnames"]
        schema_path = f"schemas/{Path(path).stem}.schema.json"
        write_schema(outdir / schema_path, path, fields, f"Freeze support table copied from {FREEZE_DIR.name}.")
        table_specs.append({"path": path, "row_count": count, "schema": schema_path, "description": "Freeze support denominator/crosstab table."})

    write_licenses(outdir)

    manifest = {
        "release_id": RELEASE_ID,
        "release_version": RELEASE_VERSION,
        "generated_at": generated_at,
        "status": "release_package_candidate_not_public_nar_submission_ready",
        "source_freeze_manifest": rel(FREEZE_DIR / "release_manifest_latest.json"),
        "source_freeze_manifest_sha256": sha256_file(FREEZE_DIR / "release_manifest_latest.json"),
        "source_freeze_summary": freeze_summary,
        "source_freeze_manifest_generated_at": freeze_manifest.get("generated_at", ""),
        "package_policy": {
            "no_full_text_or_pdf_redistribution": True,
            "sanitized_locator_fields": True,
            "checksums_exclude": ["release_manifest.json", "checksums.txt"],
            "license_review_required_before_public_hosting": True,
            "accepted_with_cautions_is_not_clean": True,
            "non_source_verified_is_not_automatic_database_error": True,
        },
        "tables": table_specs,
        "schemas_dir": "schemas",
        "license_table": "LICENSES.tsv",
    }
    write_json(outdir / "release_manifest.json", manifest)
    write_readme(outdir, manifest)
    checksum_rows = checksums(outdir)
    manifest["checksums"] = checksum_rows
    write_json(outdir / "release_manifest.json", manifest)

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    args = parser.parse_args()
    manifest = build_release(args.outdir)
    print(
        json.dumps(
            {
                "release_id": manifest["release_id"],
                "outdir": rel(args.outdir),
                "status": manifest["status"],
                "tables": {item["path"]: item["row_count"] for item in manifest["tables"]},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
