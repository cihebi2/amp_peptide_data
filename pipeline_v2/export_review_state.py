#!/usr/bin/env python3
"""Export human and AI-assisted review state without mixing provenance.

Outputs are intentionally separate from `review_verdicts.json` so AI-assisted
recommendations cannot be mistaken for human validation.
"""
import argparse
import csv
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "pipeline_v2"
WORKSHEET = PIPE / "HUMAN_REVIEW_worksheet.tsv"
HUMAN_VERDICTS = PIPE / "review_verdicts.json"
CODEX_REVIEW = PIPE / "codex_review_dual_todo_latest.json"
OUT_COMBINED = PIPE / "review_verdicts_ai_assisted.json"
OUT_AI_TSV = PIPE / "ai_reviewed_db_errors.tsv"
OUT_MANIFEST = PIPE / "review_state_export_manifest.json"

WORKSHEET_FIELDS = [
    "review_id", "priority", "paper_id", "doi", "database", "error_type",
    "db_peptide", "db_organism", "db_endpoint", "db_value", "source_table",
    "source_row", "source_col", "source_value", "reason", "local_pdf",
]
AI_FIELDS = [
    "ai_recommendation", "ai_severity", "ai_confidence", "ai_reviewer",
    "ai_reviewed_at", "ai_source", "ai_provenance", "ai_evidence_type",
    "ai_evidence_file", "ai_notes", "safe_to_import_to_human_verdicts",
]


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def load_worksheet(path=WORKSHEET):
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    return rows, {r["review_id"]: r for r in rows}


def atomic_write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path, data):
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def human_entry(review_id, verdict):
    source = verdict.get("source") or "legacy_human_review_ui"
    entry = dict(verdict)
    entry.update({
        "review_id": review_id,
        "source": source,
        "provenance": verdict.get("provenance") or "manual_or_legacy_ui_save",
        "schema_version": verdict.get("schema_version") or "review_verdict_legacy_or_v2",
        "is_human_verdict": True,
    })
    return entry


def ai_entry(record, created_at, reviewer):
    recommendation = (record.get("codex_recommendation") or "").strip()
    severity = (record.get("recommended_severity") or "").strip()
    return {
        "review_id": record["review_id"],
        "verdict": recommendation,
        "severity": severity,
        "reviewer": reviewer or "codex_cli_ai_assisted_not_human",
        "notes": record.get("codex_notes", ""),
        "reviewed_at": created_at or now_iso(),
        "source": "codex_cli_ai_assisted",
        "provenance": "separate_ai_recommendation_export_not_human_review",
        "schema_version": "review_verdict_ai_assisted_v1",
        "is_human_verdict": False,
        "ai_confidence": record.get("confidence", ""),
        "ai_evidence_type": record.get("evidence_type", ""),
        "ai_evidence_file": record.get("evidence_file", ""),
        "safe_to_import_to_human_verdicts": record.get("safe_to_import_to_human_verdicts", ""),
    }


def build_ai_tsv_rows(codex, worksheet_by_id):
    rows = []
    created_at = codex.get("created_at", "")
    reviewer = codex.get("reviewer", "codex_cli_ai_assisted_not_human")
    for rec in codex.get("records", []):
        rid = rec.get("review_id", "")
        if rid not in worksheet_by_id:
            continue
        base = {k: worksheet_by_id[rid].get(k, "") for k in WORKSHEET_FIELDS}
        base.update({
            "ai_recommendation": rec.get("codex_recommendation", ""),
            "ai_severity": rec.get("recommended_severity", ""),
            "ai_confidence": rec.get("confidence", ""),
            "ai_reviewer": reviewer,
            "ai_reviewed_at": created_at,
            "ai_source": "codex_cli_ai_assisted",
            "ai_provenance": "separate_ai_recommendation_export_not_human_review",
            "ai_evidence_type": rec.get("evidence_type", ""),
            "ai_evidence_file": rec.get("evidence_file", ""),
            "ai_notes": rec.get("codex_notes", ""),
            "safe_to_import_to_human_verdicts": rec.get("safe_to_import_to_human_verdicts", ""),
        })
        rows.append(base)
    return rows


def write_tsv(path, rows, fields):
    lines = []
    from io import StringIO
    buf = StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, delimiter="\t", lineterminator="\n")
    w.writeheader()
    for row in rows:
        w.writerow({k: row.get(k, "") for k in fields})
    lines.append(buf.getvalue())
    atomic_write_text(path, "".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worksheet", type=Path, default=WORKSHEET)
    ap.add_argument("--human", type=Path, default=HUMAN_VERDICTS)
    ap.add_argument("--codex", type=Path, default=CODEX_REVIEW)
    ap.add_argument("--combined-out", type=Path, default=OUT_COMBINED)
    ap.add_argument("--ai-tsv-out", type=Path, default=OUT_AI_TSV)
    ap.add_argument("--manifest-out", type=Path, default=OUT_MANIFEST)
    args = ap.parse_args()

    worksheet_rows, worksheet_by_id = load_worksheet(args.worksheet)
    human = load_json(args.human, {})
    codex = load_json(args.codex, {"records": []})

    combined = {}
    skipped_unknown_human = []
    for rid, verdict in sorted(human.items()):
        if rid not in worksheet_by_id:
            skipped_unknown_human.append(rid)
            continue
        combined[rid] = human_entry(rid, verdict)

    ai_records = []
    skipped_ai_existing_human = []
    skipped_ai_unknown = []
    for rec in codex.get("records", []):
        rid = rec.get("review_id", "")
        if rid not in worksheet_by_id:
            skipped_ai_unknown.append(rid)
            continue
        ai_records.append(rec)
        if rid in combined:
            skipped_ai_existing_human.append(rid)
            continue
        combined[rid] = ai_entry(rec, codex.get("created_at", ""), codex.get("reviewer", ""))

    ai_tsv_rows = build_ai_tsv_rows(codex, worksheet_by_id)
    write_tsv(args.ai_tsv_out, ai_tsv_rows, WORKSHEET_FIELDS + AI_FIELDS)
    atomic_write_json(args.combined_out, combined)
    manifest = {
        "created_at": now_iso(),
        "worksheet": str(args.worksheet),
        "human_verdicts": str(args.human),
        "codex_review": str(args.codex),
        "combined_out": str(args.combined_out),
        "ai_tsv_out": str(args.ai_tsv_out),
        "worksheet_rows": len(worksheet_rows),
        "human_verdicts_included": sum(1 for v in combined.values() if v.get("is_human_verdict")),
        "ai_recommendations_seen": len(ai_records),
        "ai_recommendations_included_in_combined": sum(1 for v in combined.values() if not v.get("is_human_verdict")),
        "ai_tsv_rows": len(ai_tsv_rows),
        "skipped_unknown_human_review_ids": skipped_unknown_human,
        "skipped_ai_existing_human_review_ids": skipped_ai_existing_human,
        "skipped_ai_unknown_review_ids": skipped_ai_unknown,
        "policy": "human verdicts remain authoritative; AI rows are separate ai_assisted recommendations, not human validation",
    }
    atomic_write_json(args.manifest_out, manifest)

    print("review state export complete")
    print(f"  combined: {args.combined_out} ({len(combined)} review_ids)")
    print(f"  ai tsv:   {args.ai_tsv_out} ({len(ai_tsv_rows)} rows)")
    print(f"  manifest: {args.manifest_out}")
    print(f"  human included={manifest['human_verdicts_included']} ai included={manifest['ai_recommendations_included_in_combined']}")


if __name__ == "__main__":
    main()
