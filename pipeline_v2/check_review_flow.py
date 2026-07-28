#!/usr/bin/env python3
"""QA gates for review provenance, AI-assisted exports, portal tiers, and DBAASP IDs.

Default mode reports structural errors and quality warnings. Use `--strict-final`
to treat publication-readiness warnings as failures.
"""
import argparse
import csv
import json
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "pipeline_v2"
WORKSHEET = PIPE / "HUMAN_REVIEW_worksheet.tsv"
HUMAN_VERDICTS = PIPE / "review_verdicts.json"
REVIEW_LOG = PIPE / "review_log.jsonl"
CODEX_REVIEW = PIPE / "codex_review_dual_todo_latest.json"
COMBINED_AI = PIPE / "review_verdicts_ai_assisted.json"
AI_TSV = PIPE / "ai_reviewed_db_errors.tsv"
PORTAL_DB = ROOT / "portal" / "atlas.db"
DBAASP_WORKLIST = PIPE / "deepmine" / "dbaasp_worklist.json"
DBAASP_STATE = PIPE / "deepmine" / "dbaasp_state.json"
DBAASP_EXTRACTED = PIPE / "deepmine" / "dbaasp_extracted.tsv"
DBAASP_EMPTY_DONE = PIPE / "deepmine" / "dbaasp_empty_done.tsv"

REQUIRED_WORKSHEET_COLUMNS = {
    "review_id", "priority", "paper_id", "doi", "database", "error_type",
    "db_peptide", "db_organism", "db_endpoint", "db_value", "source_value",
    "reason", "local_pdf",
}
ALLOWED_VERDICTS = {"confirmed", "not_an_error", "uncertain"}
ALLOWED_SEVERITIES = {"critical", "major", "minor"}


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def read_tsv(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def issue(issues, level, code, message, **detail):
    issues.append({"level": level, "code": code, "message": message, "detail": detail})


def work_key(item):
    if isinstance(item, list) and item:
        return str(item[0])
    if isinstance(item, dict):
        return str(item.get("paper_id") or item.get("doi_key") or item.get("doi") or item.get("id") or "")
    return str(item)


def check_worksheet(issues):
    rows = read_tsv(WORKSHEET)
    if not rows:
        issue(issues, "ERROR", "worksheet_missing_or_empty", "worksheet is missing or empty", path=str(WORKSHEET))
        return rows, {}
    missing = sorted(REQUIRED_WORKSHEET_COLUMNS - set(rows[0]))
    if missing:
        issue(issues, "ERROR", "worksheet_missing_columns", "worksheet is missing required columns", columns=missing)
    ids = [r.get("review_id", "") for r in rows]
    dupes = sorted(k for k, v in Counter(ids).items() if v > 1)
    if dupes:
        issue(issues, "ERROR", "worksheet_duplicate_review_ids", "worksheet has duplicate review_id values", review_ids=dupes[:20], count=len(dupes))
    return rows, {r.get("review_id", ""): r for r in rows}


def check_human_verdicts(issues, worksheet_by_id):
    verdicts = load_json(HUMAN_VERDICTS, {})
    if not isinstance(verdicts, dict):
        issue(issues, "ERROR", "human_verdicts_not_mapping", "review_verdicts.json is not a review_id mapping")
        return {}
    for rid, v in verdicts.items():
        if rid not in worksheet_by_id:
            issue(issues, "ERROR", "human_verdict_unknown_id", "human verdict references unknown review_id", review_id=rid)
        if not isinstance(v, dict):
            issue(issues, "ERROR", "human_verdict_not_object", "human verdict entry is not an object", review_id=rid)
            continue
        verdict = v.get("verdict", "")
        severity = v.get("severity", "")
        if verdict not in ALLOWED_VERDICTS:
            issue(issues, "ERROR", "human_verdict_invalid_label", "human verdict has invalid label", review_id=rid, verdict=verdict)
        if verdict == "confirmed" and severity not in ALLOWED_SEVERITIES:
            issue(issues, "WARN", "human_confirmed_missing_severity", "confirmed human verdict is missing severity", review_id=rid)
        if verdict in {"not_an_error", "uncertain"} and not (v.get("notes") or "").strip():
            issue(issues, "WARN", "human_nonconfirmed_missing_notes", "non-confirmed human verdict lacks notes", review_id=rid)
        if v.get("source", "legacy_human_review_ui") == "codex_cli_ai_assisted" or v.get("is_human_verdict") is False:
            issue(issues, "ERROR", "ai_record_in_human_file", "AI-assisted record appears in human verdict file", review_id=rid)
        for field in ("reviewed_at", "source", "provenance"):
            if not v.get(field):
                issue(issues, "WARN", "human_verdict_legacy_missing_field", "legacy human verdict lacks provenance field", review_id=rid, field=field)
    return verdicts


def check_review_log(issues, worksheet_by_id):
    if not REVIEW_LOG.exists():
        issue(issues, "WARN", "review_log_missing", "append-only review_log.jsonl does not exist yet; future saves should create it")
        return []
    rows = []
    for n, line in enumerate(REVIEW_LOG.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as ex:
            issue(issues, "ERROR", "review_log_invalid_json", "review_log.jsonl contains invalid JSON", line=n, error=str(ex))
            continue
        rid = item.get("review_id") or (item.get("entry") or {}).get("review_id")
        if rid and rid not in worksheet_by_id:
            issue(issues, "ERROR", "review_log_unknown_id", "review log references unknown review_id", line=n, review_id=rid)
        rows.append(item)
    return rows


def check_codex_review(issues, worksheet_by_id, human_verdicts):
    codex = load_json(CODEX_REVIEW, {})
    records = codex.get("records", []) if isinstance(codex, dict) else []
    if not isinstance(records, list):
        issue(issues, "ERROR", "codex_records_not_list", "Codex review records are not a list")
        return {}
    if codex.get("count") not in (None, len(records)):
        issue(issues, "ERROR", "codex_count_mismatch", "Codex count does not match records length", count=codex.get("count"), records=len(records))
    for rec in records:
        rid = rec.get("review_id", "")
        if rid not in worksheet_by_id:
            issue(issues, "ERROR", "codex_unknown_review_id", "Codex review references unknown review_id", review_id=rid)
        if rid in human_verdicts:
            issue(issues, "WARN", "codex_overlaps_human", "Codex recommendation overlaps existing human verdict; human must remain authoritative", review_id=rid)
        if rec.get("codex_recommendation") not in ALLOWED_VERDICTS:
            issue(issues, "ERROR", "codex_invalid_recommendation", "Codex recommendation has invalid label", review_id=rid, recommendation=rec.get("codex_recommendation"))
        if rec.get("codex_recommendation") == "confirmed" and rec.get("recommended_severity") not in ALLOWED_SEVERITIES:
            issue(issues, "ERROR", "codex_confirmed_missing_severity", "Codex confirmed recommendation lacks valid severity", review_id=rid)
        ev = rec.get("evidence_file", "")
        if not ev or not (ROOT / ev).exists():
            issue(issues, "ERROR", "codex_evidence_file_missing", "Codex recommendation lacks readable evidence file", review_id=rid, evidence_file=ev)
        if "not_human" not in (codex.get("reviewer", "") + rec.get("safe_to_import_to_human_verdicts", "")):
            issue(issues, "WARN", "codex_not_explicitly_nonhuman", "Codex artifact should explicitly state it is not human review", review_id=rid)
    return codex


def check_exports(issues, worksheet_by_id):
    if COMBINED_AI.exists():
        combined = load_json(COMBINED_AI, {})
        if not isinstance(combined, dict):
            issue(issues, "ERROR", "combined_ai_not_mapping", "combined AI-assisted export is not a review_id mapping")
        else:
            for rid, v in combined.items():
                if rid not in worksheet_by_id:
                    issue(issues, "ERROR", "combined_unknown_review_id", "combined export references unknown review_id", review_id=rid)
                if not v.get("is_human_verdict") and v.get("source") != "codex_cli_ai_assisted":
                    issue(issues, "ERROR", "combined_ai_missing_source", "AI row in combined export lacks AI source label", review_id=rid)
    else:
        issue(issues, "WARN", "combined_ai_export_missing", "AI-assisted combined export has not been generated yet", path=str(COMBINED_AI))
    if AI_TSV.exists():
        rows = read_tsv(AI_TSV)
        for r in rows:
            if r.get("review_id") not in worksheet_by_id:
                issue(issues, "ERROR", "ai_tsv_unknown_review_id", "AI TSV references unknown review_id", review_id=r.get("review_id", ""))
            if r.get("ai_source") != "codex_cli_ai_assisted":
                issue(issues, "ERROR", "ai_tsv_missing_source", "AI TSV row lacks AI source label", review_id=r.get("review_id", ""))
    else:
        issue(issues, "WARN", "ai_tsv_missing", "AI-assisted TSV export has not been generated yet", path=str(AI_TSV))


def check_dbaasp(issues):
    if not DBAASP_WORKLIST.exists():
        return {}
    work = load_json(DBAASP_WORKLIST, [])
    keys = [work_key(x) for x in work]
    bad_work = [k for k in keys if k.endswith(")")]
    if bad_work:
        issue(issues, "WARN", "dbaasp_malformed_worklist_keys", "DBAASP worklist has DOI keys ending with ')'", count=len(bad_work), samples=bad_work[:10])
    state = load_json(DBAASP_STATE, [])
    done = [str(x) for x in state] if isinstance(state, list) else [str(x) for x in state.get("done", [])]
    bad_done = [k for k in done if k.endswith(")")]
    if bad_done:
        issue(issues, "WARN", "dbaasp_malformed_state_keys", "DBAASP state has done keys ending with ')'", count=len(bad_done), samples=bad_done[:10])
    rows = read_tsv(DBAASP_EXTRACTED)
    bad_rows = [r.get("paper_id", "") for r in rows if ")" in r.get("paper_id", "")]
    if bad_rows:
        issue(issues, "WARN", "dbaasp_malformed_extracted_paper_ids", "DBAASP extracted rows contain malformed paper_id values", count=len(bad_rows), unique_count=len(set(bad_rows)), samples=sorted(set(bad_rows))[:10])
    empty_rows = read_tsv(DBAASP_EMPTY_DONE)
    empty_ids = [r.get("paper_id", "") for r in empty_rows]
    extracted_ids = {r.get("paper_id", "") for r in rows}
    work_ids = set(keys)
    done_ids = set(done)
    missing_empty = sorted(set(empty_ids) - work_ids)
    if missing_empty:
        issue(issues, "ERROR", "dbaasp_empty_done_not_in_worklist", "empty-done log references paper IDs outside worklist", count=len(missing_empty), samples=missing_empty[:10])
    empty_not_done = sorted(set(empty_ids) - done_ids)
    if empty_not_done:
        issue(issues, "ERROR", "dbaasp_empty_done_not_in_state", "empty-done log references paper IDs not marked done", count=len(empty_not_done), samples=empty_not_done[:10])
    empty_with_rows = sorted(set(empty_ids) & extracted_ids)
    if empty_with_rows:
        issue(issues, "WARN", "dbaasp_empty_done_has_extracted_rows", "empty-done IDs also have extracted rows", count=len(empty_with_rows), samples=empty_with_rows[:10])
    return {
        "worklist": len(keys),
        "done": len(done),
        "todo": max(len(keys) - len(done), 0),
        "extracted_rows": len(rows),
        "empty_done_rows": len(empty_rows),
    }


def check_portal(issues):
    if not PORTAL_DB.exists():
        issue(issues, "WARN", "portal_db_missing", "portal atlas.db is missing", path=str(PORTAL_DB))
        return {}
    con = sqlite3.connect(PORTAL_DB)
    tables = {r[0] for r in con.execute("select name from sqlite_master where type='table'")}
    required = {"papers", "activity", "audit", "mechanism", "stats"}
    missing = sorted(required - tables)
    if missing:
        issue(issues, "ERROR", "portal_missing_tables", "portal DB is missing required tables", tables=missing)
    stats = {}
    if "stats" in tables:
        cols = [r[1] for r in con.execute("pragma table_info(stats)")]
        if cols[:2] == ["k", "v"]:
            stats = dict(con.execute("select k,v from stats"))
        else:
            issue(issues, "ERROR", "portal_stats_schema_unexpected", "portal stats table has unexpected columns", columns=cols)
    counts = {}
    for table in sorted(required & tables):
        counts[table] = con.execute(f"select count(*) from {table}").fetchone()[0]
    con.close()
    return {"counts": counts, "stats": stats}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict-final", action="store_true", help="treat quality warnings as failures")
    ap.add_argument("--json-out", type=Path, default=PIPE / "review_flow_qa_latest.json")
    args = ap.parse_args()

    issues = []
    worksheet_rows, worksheet_by_id = check_worksheet(issues)
    human_verdicts = check_human_verdicts(issues, worksheet_by_id)
    review_log = check_review_log(issues, worksheet_by_id)
    codex = check_codex_review(issues, worksheet_by_id, human_verdicts)
    check_exports(issues, worksheet_by_id)
    dbaasp = check_dbaasp(issues)
    portal = check_portal(issues)

    levels = Counter(i["level"] for i in issues)
    human_counts = Counter(v.get("verdict", "") for v in human_verdicts.values() if isinstance(v, dict))
    codex_records = codex.get("records", []) if isinstance(codex, dict) else []
    summary = {
        "created_at": now_iso(),
        "strict_final": args.strict_final,
        "worksheet_rows": len(worksheet_rows),
        "human_verdicts": len(human_verdicts),
        "human_verdict_counts": dict(human_counts),
        "review_log_entries": len(review_log),
        "codex_records": len(codex_records),
        "dbaasp": dbaasp,
        "portal": portal,
        "issue_counts": dict(levels),
        "issues": issues,
    }
    args.json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("review/data flow QA")
    print(f"  worksheet_rows={summary['worksheet_rows']} human_verdicts={summary['human_verdicts']} codex_records={summary['codex_records']}")
    print(f"  issues: ERROR={levels.get('ERROR', 0)} WARN={levels.get('WARN', 0)} INFO={levels.get('INFO', 0)}")
    print(f"  report: {args.json_out}")
    for item in issues[:20]:
        print(f"  {item['level']}: {item['code']} - {item['message']} {item.get('detail', {})}")
    if len(issues) > 20:
        print(f"  ... {len(issues) - 20} more issues in JSON report")

    failed = levels.get("ERROR", 0) > 0 or (args.strict_final and levels.get("WARN", 0) > 0)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
