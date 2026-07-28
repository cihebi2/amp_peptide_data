#!/usr/bin/env python3
"""Normalize malformed DBAASP DOI keys across worklist/state/extracted TSV.

The known bug is DOI keys captured from filenames like
`... (10.1038_s41598-024-73766-1).pdf`, leaving a trailing `)` in the key.

Default mode is dry-run and writes an audit report plus mapping TSV. Use
`--apply` to rewrite the three canonical artifacts after creating timestamped
backups under `pipeline_v2/deepmine/backups/`.
"""
import argparse
import csv
import json
import os
import re
import shutil
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "pipeline_v2" / "deepmine"
WORKLIST = HERE / "dbaasp_worklist.json"
STATE = HERE / "dbaasp_state.json"
EXTRACTED = HERE / "dbaasp_extracted.tsv"
REPORT = HERE / "dbaasp_id_normalization_report_latest.json"
MAPPING = HERE / "dbaasp_id_normalization_mapping_latest.tsv"


def now_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_key(value):
    """Return canonical key for DBAASP paper IDs without altering PMC IDs."""
    raw = (value or "").strip()
    if not raw.lower().startswith("10."):
        return raw
    key = raw.lower()
    key = re.sub(r'^https?://(dx\.)?doi\.org/', '', key)
    key = key.replace("_", "/", 1)
    return re.sub(r'[\]\)\}>,;:.]+$', '', key)


def load_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def read_tsv(path):
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return list(reader), list(reader.fieldnames or [])


def atomic_write_text(path, text):
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


def write_tsv(path, rows, fields):
    from io import StringIO
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in fields})
    atomic_write_text(path, buf.getvalue())


def key_from_work_item(item):
    if isinstance(item, list) and item:
        return str(item[0])
    if isinstance(item, dict):
        for field in ("paper_id", "doi_key", "doi", "id"):
            if item.get(field):
                return str(item[field])
    return str(item)


def set_work_item_key(item, new_key):
    if isinstance(item, list) and item:
        out = list(item)
        out[0] = new_key
        return out
    if isinstance(item, dict):
        out = dict(item)
        for field in ("paper_id", "doi_key", "doi", "id"):
            if out.get(field):
                out[field] = new_key
                return out
        return out
    return item


def collect_mapping(label, values):
    rows = []
    for value in values:
        new = normalize_key(value)
        if value != new:
            rows.append({"artifact": label, "old_id": value, "new_id": new})
    return rows


def collision_report(values):
    by_new = defaultdict(list)
    for value in values:
        by_new[normalize_key(value)].append(value)
    return {new: sorted(set(old)) for new, old in by_new.items() if len(set(old)) > 1}


def backup_files(paths):
    backup_dir = HERE / "backups" / f"dbaasp_id_normalization_{now_stamp()}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    manifest = {"created_at": now_iso(), "backup_dir": str(backup_dir), "files": []}
    for path in paths:
        if path.exists():
            dest = backup_dir / path.name
            shutil.copy2(path, dest)
            manifest["files"].append({"source": str(path), "backup": str(dest), "bytes": path.stat().st_size})
    atomic_write_json(backup_dir / "backup_manifest.json", manifest)
    return backup_dir, manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="rewrite canonical DBAASP artifacts after backup")
    ap.add_argument("--report", type=Path, default=REPORT)
    ap.add_argument("--mapping", type=Path, default=MAPPING)
    args = ap.parse_args()

    work = load_json(WORKLIST, [])
    state = load_json(STATE, [])
    extracted_rows, extracted_fields = read_tsv(EXTRACTED)
    work_keys = [key_from_work_item(item) for item in work]
    done_keys = [str(x) for x in state] if isinstance(state, list) else [str(x) for x in state.get("done", [])]
    extracted_ids = [r.get("paper_id", "") for r in extracted_rows]

    collisions = {
        "worklist": collision_report(work_keys),
        "state": collision_report(done_keys),
        "extracted": collision_report(sorted(set(extracted_ids))),
    }
    collision_count = sum(len(v) for v in collisions.values())
    mapping_rows = []
    mapping_rows.extend(collect_mapping("worklist", work_keys))
    mapping_rows.extend(collect_mapping("state", done_keys))
    mapping_rows.extend(collect_mapping("extracted", extracted_ids))

    before = {
        "worklist_items": len(work_keys),
        "state_done": len(done_keys),
        "extracted_rows": len(extracted_rows),
        "worklist_trailing_paren": sum(k.endswith(")") for k in work_keys),
        "state_trailing_paren": sum(k.endswith(")") for k in done_keys),
        "extracted_rows_with_paren": sum(")" in k for k in extracted_ids),
        "extracted_unique_with_paren": sum(")" in k for k in set(extracted_ids)),
    }
    changed = Counter(row["artifact"] for row in mapping_rows)
    report = {
        "created_at": now_iso(),
        "mode": "apply" if args.apply else "dry_run",
        "before": before,
        "changed_counts": dict(changed),
        "collision_count": collision_count,
        "collisions": collisions,
        "mapping_path": str(args.mapping),
        "applied": False,
    }

    if collision_count:
        report["blocked_reason"] = "normalization would merge distinct old IDs"
        atomic_write_json(args.report, report)
        write_tsv(args.mapping, mapping_rows, ["artifact", "old_id", "new_id"])
        print(f"BLOCKED: {collision_count} normalization collisions; report={args.report}")
        return 2

    write_tsv(args.mapping, mapping_rows, ["artifact", "old_id", "new_id"])

    if args.apply:
        backup_dir, backup_manifest = backup_files([WORKLIST, STATE, EXTRACTED])
        norm_work = [set_work_item_key(item, normalize_key(key_from_work_item(item))) for item in work]
        if isinstance(state, list):
            norm_state = sorted({normalize_key(str(x)) for x in state})
        else:
            norm_state = dict(state)
            if isinstance(norm_state.get("done"), list):
                norm_state["done"] = sorted({normalize_key(str(x)) for x in norm_state["done"]})
        norm_rows = []
        for row in extracted_rows:
            out = dict(row)
            out["paper_id"] = normalize_key(out.get("paper_id", ""))
            norm_rows.append(out)
        atomic_write_json(WORKLIST, norm_work)
        atomic_write_json(STATE, norm_state)
        write_tsv(EXTRACTED, norm_rows, extracted_fields)
        report["applied"] = True
        report["backup_dir"] = str(backup_dir)
        report["backup_manifest"] = backup_manifest
        report["after"] = {
            "worklist_trailing_paren": sum(key_from_work_item(x).endswith(")") for x in norm_work),
            "state_trailing_paren": sum(str(x).endswith(")") for x in norm_state) if isinstance(norm_state, list) else None,
            "extracted_rows_with_paren": sum(")" in r.get("paper_id", "") for r in norm_rows),
            "extracted_unique_with_paren": sum(")" in r.get("paper_id", "") for r in {r.get("paper_id", ""): r for r in norm_rows}.values()),
        }

    atomic_write_json(args.report, report)
    print(f"DBAASP ID normalization {'applied' if args.apply else 'dry-run'}")
    print(f"  worklist changes: {changed.get('worklist', 0)}")
    print(f"  state changes:    {changed.get('state', 0)}")
    print(f"  extracted changes:{changed.get('extracted', 0)}")
    print(f"  collisions:       {collision_count}")
    print(f"  mapping:          {args.mapping}")
    print(f"  report:           {args.report}")
    if args.apply:
        print(f"  backup:           {report['backup_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
