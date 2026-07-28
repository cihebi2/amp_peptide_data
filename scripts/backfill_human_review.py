#!/usr/bin/env python3
"""Backfill human-review verdicts into per-paper database_record_verification.json files.

Reads pipeline_v2/human_verified_db_errors.tsv (192 verdicts) and writes a `human_review` LIST
into the matched record_audits[] entries of papers/<id>/final/database_record_verification.json.

Matching:
  Tier 1 — audit_record_id "<paper>:database_audit:<1-based idx into record_audits[]>" (exact).
  Tier 2 — unlinked rows: fuzzy match within the paper on database + normalized database_value
           and primary source value (database_value / primary_activity_check.source_value).
Idempotent: keyed on review_id inside each record's human_review list (re-runs replace, not duplicate).
Multiple verdicts per record are preserved (list). Nothing else in the record is modified.

Usage:
  python3 scripts/backfill_human_review.py            # apply
  python3 scripts/backfill_human_review.py --dry-run  # report only, no writes
"""
import csv, json, sys, re, unicodedata
from pathlib import Path
from collections import defaultdict

csv.field_size_limit(10**9)
ROOT = Path(__file__).resolve().parents[1]
TSV = ROOT / "pipeline_v2" / "human_verified_db_errors.tsv"
REVIEWED_AT = "2026-07-03T00:00:00Z"


def norm(s):
    s = unicodedata.normalize("NFKC", (s or "")).lower()
    s = s.replace("μ", "u").replace("µ", "u").replace("–", "-").replace("—", "-")
    s = s.replace("microm", "um").replace(" ", "")
    return s


def rec_primary_value(rec):
    v = rec.get("primary_source_value")
    if v:
        return v
    pac = rec.get("primary_activity_check") or {}
    return pac.get("source_value", "")


def load_json(p):
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


def records_of(data):
    return data.get("record_audits") or data.get("records") or []


def main():
    dry = "--dry-run" in sys.argv
    rows = list(csv.DictReader(TSV.open(encoding="utf-8"), delimiter="\t"))
    by_paper = defaultdict(list)
    for r in rows:
        by_paper[r["paper_id"]].append(r)

    linked = fuzzy = unmatched = 0
    unmatched_rows = []
    # paper -> {record_index: [human_review dicts]}
    to_write = defaultdict(lambda: defaultdict(list))

    for pid, prs in by_paper.items():
        fp = ROOT / "papers" / pid / "final" / "database_record_verification.json"
        if not fp.exists():
            for r in prs:
                unmatched += 1; unmatched_rows.append((r["review_id"], pid, "no_json"))
            continue
        data = load_json(fp)
        recs = records_of(data)
        for r in prs:
            block = {
                "verdict": r["human_verdict"], "severity": r.get("human_severity", ""),
                "reviewer": r.get("human_reviewer", "") or "expert", "notes": r.get("human_notes", ""),
                "reviewed_at": REVIEWED_AT, "review_id": r["review_id"],
                "link_confidence": r.get("link_confidence", "") or "unlinked",
            }
            aid = (r.get("audit_record_id") or "").strip()
            idx = None
            if aid and ":database_audit:" in aid:
                try:
                    idx = int(aid.rsplit(":database_audit:", 1)[1]) - 1
                except ValueError:
                    idx = None
            if idx is not None and 0 <= idx < len(recs):
                block["match_method"] = "audit_record_id"
                to_write[pid][idx].append(block); linked += 1
                continue
            # Tier 2 — fuzzy within paper
            dbn, dvn, svn = norm(r["database"]), norm(r["db_value"]), norm(r["source_value"])
            cands = []
            for i, rec in enumerate(recs):
                if dbn and dbn not in norm(rec.get("source_id", "") + rec.get("source_table", "") + str(rec.get("database_subject", ""))):
                    # loose db gate: also accept if db name appears in source_id
                    if dbn not in norm(str(rec.get("source_id", ""))):
                        continue
                dv_ok = dvn and dvn == norm(rec.get("database_value", ""))
                sv_ok = svn and svn == norm(rec_primary_value(rec))
                if dv_ok or sv_ok:
                    cands.append(i)
            if len(cands) == 1:
                block["match_method"] = "fuzzy_paper_value"
                to_write[pid][cands[0]].append(block); fuzzy += 1
            else:
                unmatched += 1
                unmatched_rows.append((r["review_id"], pid, f"cands={len(cands)}"))

    print(f"match summary: tier1(audit_record_id)={linked}  tier2(fuzzy)={fuzzy}  unmatched={unmatched}  (total {len(rows)})")
    if unmatched_rows:
        outp = ROOT / "pipeline_v2" / "human_review_unmatched.tsv"
        if not dry:
            with outp.open("w", encoding="utf-8") as f:
                f.write("review_id\tpaper_id\treason\n")
                for rid, pid, why in unmatched_rows:
                    f.write(f"{rid}\t{pid}\t{why}\n")
        print(f"  unmatched → {outp if not dry else '(dry-run, not written)'} ({len(unmatched_rows)} rows)")

    if dry:
        print("dry-run: no files modified.")
        return

    files = 0
    for pid, idxmap in to_write.items():
        fp = ROOT / "papers" / pid / "final" / "database_record_verification.json"
        data = load_json(fp)
        recs = records_of(data)
        for idx, blocks in idxmap.items():
            rec = recs[idx]
            existing = rec.get("human_review")
            existing = existing if isinstance(existing, list) else ([existing] if existing else [])
            keep = [b for b in existing if isinstance(b, dict) and b.get("review_id") not in {x["review_id"] for x in blocks}]
            rec["human_review"] = keep + blocks
        with fp.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        files += 1
    print(f"wrote human_review into {files} paper JSON files "
          f"({sum(len(v) for m in to_write.values() for v in m.values())} verdict blocks across "
          f"{sum(len(m) for m in to_write.values())} records).")


if __name__ == "__main__":
    main()
