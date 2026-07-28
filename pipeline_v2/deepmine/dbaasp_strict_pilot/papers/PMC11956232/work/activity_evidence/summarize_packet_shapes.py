#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4] / "packets" / "PMC11956232"
WORK = Path(__file__).resolve().parent


TEXTY = (
    "text",
    "caption",
    "paragraph",
    "sentence",
    "abstract",
    "title",
    "body",
    "content",
    "raw",
    "value_text",
    "cell_text",
)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path, limit=None):
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if limit and len(rows) >= limit:
                break
    return rows


def scalar_shape(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return type(value).__name__
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return {"list_len": len(value), "item_shape": scalar_shape(value[0]) if value else None}
    if isinstance(value, dict):
        return {"dict_keys": sorted(value.keys())}
    return type(value).__name__


def safe_projection(obj, depth=0):
    if depth > 2:
        return scalar_shape(obj)
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if any(marker in key.lower() for marker in TEXTY):
                out[key] = scalar_shape(value)
            elif isinstance(value, (dict, list)):
                out[key] = safe_projection(value, depth + 1)
            else:
                out[key] = value if key.lower().endswith(("id", "ids", "locator", "locators", "path", "paths", "status")) else scalar_shape(value)
        return out
    if isinstance(obj, list):
        return {"list_len": len(obj), "first": safe_projection(obj[0], depth + 1) if obj else None}
    return scalar_shape(obj)


def summarize_json(rel):
    path = ROOT / rel
    data = load_json(path)
    return {
        "path": str(path),
        "top_shape": safe_projection(data),
    }


def summarize_jsonl(rel):
    path = ROOT / rel
    rows = load_jsonl(path, limit=3)
    total = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return {
        "path": str(path),
        "row_count": total,
        "sample_shapes": [safe_projection(row) for row in rows],
    }


def main():
    summary = {
        "paper_id": "PMC11956232",
        "json_files": {},
        "jsonl_files": {},
    }
    for rel in [
        "packet_manifest.json",
        "analysis/activity_safe_candidate_handoff.json",
        "database/database_source_manifest.json",
        "database/authoritative_match_report.json",
        "extracted/xml_sections.json",
        "extracted/pdf_tables.json",
        "extracted/supplementary_index.json",
        "extracted/supplementary_tables.json",
        "locators/locator_index.json",
    ]:
        summary["json_files"][rel] = summarize_json(rel)
    for rel in [
        "database/dbaasp_machine_extracted_rows.jsonl",
        "database/linked_article_records.jsonl",
        "database/linked_assay_records.jsonl",
        "database/linked_sequence_records.jsonl",
        "database/linked_literature_records.jsonl",
        "extracted/pdf_text.jsonl",
        "extracted/supplementary_text.jsonl",
    ]:
        summary["jsonl_files"][rel] = summarize_jsonl(rel)
    out = WORK / "packet_shape_summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(out))


if __name__ == "__main__":
    main()
