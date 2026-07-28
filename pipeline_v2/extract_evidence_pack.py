#!/usr/bin/env python3
"""pipeline_v2 step 1: deterministic evidence-pack builder.

Root-cause fixes addressed here:
- RC2/RC3: parse JATS tables into GROUNDED grids + long-form cells (table,row_label,col_header,value)
  so the LLM never has to index raw XML positionally (kills column-offset errors).
- Provides the exact cell inventory the v2 adjudicator uses for locator round-trip validation.

Output: pipeline_v2/work/<paper_id>/evidence_pack.json
"""
import csv, json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_TSV = ROOT / "releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv"
csv.field_size_limit(10**9)


def clean(s: str) -> str:
    return " ".join((s or "").split())


def parse_tables(xml_path: Path):
    raw = xml_path.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r'xmlns="[^"]+"', "", raw)
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        # fallback: strip namespace prefixes from tags too, then drop ns decls
        raw2 = re.sub(r"<(/?)[a-zA-Z0-9]+:", r"<\1", raw)
        raw2 = re.sub(r"\sxmlns:[a-zA-Z0-9]+=\"[^\"]+\"", "", raw2)
        raw2 = re.sub(r"\s[a-zA-Z0-9]+:[a-zA-Z0-9-]+=\"[^\"]*\"", "", raw2)
        try:
            root = ET.fromstring(raw2)
        except ET.ParseError as e:
            return [], f"parse_error:{e}"
    tables = []
    for ti, tw in enumerate(root.findall(".//table-wrap"), 1):
        lab = tw.find(".//label")
        cap = tw.find(".//caption")
        label = clean("".join(lab.itertext())) if lab is not None else f"Table {ti}"
        caption = clean("".join(cap.itertext())) if cap is not None else ""
        tbl = tw.find(".//table")
        grid = []
        if tbl is not None:
            for tr in tbl.findall(".//tr"):
                # expand colspan so header group-labels (e.g. EC50 spanning 4 sub-columns) align to data columns
                cells = []
                for c in tr:
                    if c.tag in ("td", "th"):
                        txt = clean("".join(c.itertext()))
                        try:
                            cs = max(1, int(c.get("colspan", "1") or "1"))
                        except ValueError:
                            cs = 1
                        cells.extend([txt] * cs)
                if any(cells):
                    grid.append(cells)
        # footnotes
        fns = [clean("".join(fn.itertext())) for fn in tw.findall(".//table-wrap-foot//p")]
        # data-cell test: a real measured value, not an organism/strain label that happens to contain an ID number
        def is_value_cell(c: str) -> bool:
            c = c.strip()
            if not c:
                return False
            if re.match(r"^[<>≥≤~=±]?\s*\d", c):              # 7.8, >50, ≥256, 0.78
                return True
            if re.fullmatch(r"(?i)(na|nd|n\.d\.|-|–|—|nt|non-?inhibitory|not\s+(detected|active|inhibitory)|inactive)", c):
                return True
            return False
        # a row is DATA if its non-first non-empty cells are mostly value cells (allow single-value rows)
        def is_data_row(row):
            rest = [c for c in row[1:] if c.strip()]
            if len(rest) < 1:
                return False
            vals = sum(1 for c in rest if is_value_cell(c))
            return vals >= max(1, len(rest) // 2)
        header_rows = []
        data_start = len(grid)
        for i, row in enumerate(grid):
            if is_data_row(row):
                data_start = i
                break
            header_rows.append(row)
        # data width = modal length of data rows (after colspan expansion)
        data_rows = grid[data_start:]
        if data_rows:
            from collections import Counter as _C
            data_width = _C(len(r) for r in data_rows).most_common(1)[0][0]
        else:
            data_width = max((len(r) for r in grid), default=0)
        # COMPOSITE header: align every header row to data_width (group row spans + sub row organisms),
        # then join per column so a cell carries BOTH the endpoint group and the specific target,
        # e.g. "EC50 / Viral entry" or "MIC100 [µg/mL] / C.krusei CCM 8271". offset is 0 afterwards.
        aligned = []
        for hr in header_rows:
            if len(hr) == data_width:
                aligned.append(hr)
            elif len(hr) == data_width - 1:
                aligned.append([""] + hr)        # sub-header that omits the row-label column
        headers = []
        if aligned and data_width:
            for i in range(data_width):
                parts = []
                for hr in aligned:
                    v = hr[i] if i < len(hr) else ""
                    if v and v not in parts:
                        parts.append(v)
                headers.append(" / ".join(parts))
        elif header_rows:
            headers = max(header_rows, key=lambda r: sum(1 for c in r if c.strip()))
        # long-form cells with header/data offset handling
        longform = []
        for ri in range(data_start, len(grid)):
            row = grid[ri]
            if not row:
                continue
            row_label = row[0]
            ncol = len(row)
            offset = 1 if ncol == len(headers) + 1 else 0
            for ci in range(1, ncol):
                hidx = ci - offset
                col_header = headers[hidx] if 0 <= hidx < len(headers) else f"col{ci}"
                val = row[ci]
                if val == "":
                    continue
                longform.append({
                    "table_index": ti,
                    "row_index": ri + 1,           # 1-based, includes header rows
                    "col_index": ci + 1,           # 1-based cell position
                    "row_label": row_label,
                    "col_header": col_header,
                    "value": val,
                })
        tables.append({
            "table_index": ti,
            "label": label,
            "caption": caption,
            "footnotes": fns,
            "header_rows": header_rows,
            "grid": grid,
            "longform_cells": longform,
        })
    return tables, "ok"


def load_db_assertions(paper_id: str):
    rows = []
    with RELEASE_TSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["paper_id"] != paper_id:
                continue
            rows.append({
                "audit_record_id": r["audit_record_id"],
                "database": r["database"],
                "source_id": r["source_id"],
                "original_status": r["status"],
                "original_flags": r["conflict_flags"],
                "db_subject": r["database_subject"],
                "db_measure": r["database_measure"],
                "db_value": r["database_value"],
                "db_unit": r["database_unit"],
                "db_sequence": r["sequence"],
                "primary_source_sequence": r["primary_source_sequence"],
                "record_name": r["record_name"],
                "name_check": (r["name_check"] or "")[:500],
                "sequence_check": (r["sequence_check"] or "")[:500],
                "activity_check": (r["activity_check"] or "")[:500],
            })
    return rows


def main():
    paper_id = sys.argv[1]
    xml_path = ROOT / f"papers/{paper_id}/source/paper.xml"
    tables, status = parse_tables(xml_path)
    assertions = load_db_assertions(paper_id)
    pack = {
        "paper_id": paper_id,
        "xml_path": str(xml_path.relative_to(ROOT)),
        "parse_status": status,
        "table_count": len(tables),
        "tables": tables,
        "db_assertions": assertions,
        "db_assertion_count": len(assertions),
    }
    out = ROOT / f"pipeline_v2/work/{paper_id}/evidence_pack.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
    total_cells = sum(len(t["longform_cells"]) for t in tables)
    print(f"{paper_id}: tables={len(tables)} longform_cells={total_cells} db_assertions={len(assertions)} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
