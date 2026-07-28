#!/usr/bin/env python3
"""Summarize database-vs-literature differences from source-reviewed audits."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPERS_ROOT = ROOT / "papers"
REPORTS_ROOT = ROOT / "reports"

STATUS_ORDER = [
    "source_conflict",
    "sequence_modified_not_normalized",
    "database_only_no_primary_source",
    "unresolved_record",
]

CURATED_TARGETS = [
    ("doi__10.1002_cbic.202100151", "DBAASPS_18493"),
    ("doi__10.1007_s12602-025-10542-1", "DBAASPR_23863"),
    ("doi__10.1002_advs.202205301", "DBAASPS_20504"),
    ("doi__10.1002_advs.202507457", "AP05698"),
    ("doi__10.1002_advs.202507457", "AP05696"),
    ("doi__10.3389_fmicb.2016.01801", "DBAASPS_9765"),
    ("doi__10.1038_srep09761", "DBAASPS_10050"),
    ("doi__10.1038_s41586-019-1791-1", "DBAASPR_17389"),
    ("doi__10.1021_acsomega.0c00442", "DBAASPS_22113"),
    ("doi__10.3390_md16090290", "DBAASPR_20074"),
    ("doi__10.3390_ijms22136679", "DBAASPS_10746"),
    ("doi__10.3390_antibiotics11010076", "DBAASPR_919"),
    ("doi__10.3389_fmicb.2017.00051", "AP02787"),
    ("doi__10.1007_s12539-016-0163-x", "dbAMP_17886"),
    ("doi__10.1007_s00262-014-1540-0", "DRAMP31842"),
    ("doi__10.21203_rs.3.rs-2194162_v1", "DBAASPR_2135"),
    ("doi__10.1007_s00018-020-03755-w", "CAMPSQ12854"),
    ("doi__10.1007_s00018-022-04440-w", "DBAASPS_22793"),
    ("doi__10.3389_fmicb.2018.00329", "dbAMP_03323"),
    ("doi__10.3389_fmicb.2018.01440", "dbAMP_27187"),
    ("doi__10.3390_molecules26195767", "DRAMP32346"),
    ("doi__10.3892_mmr.2017.7418", "DRAMP35619"),
    ("doi__10.1038_s41598-017-16784-6", "DBAASPR_3442"),
    ("doi__10.1038_s41522-024-00637-y", "DBAASPS_11338"),
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise TypeError(f"expected object in {path}")
    return data


def compact(value: Any, limit: int = 420) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value)
    text = " ".join(text.split())
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text


def md_cell(value: Any, limit: int = 420) -> str:
    """Make compact text safe for a Markdown table cell."""
    return compact(value, limit).replace("|", "\\|")


def infer_database(record: dict[str, Any]) -> str:
    text = " ".join(
        compact(record.get(k), 200)
        for k in ("source_id", "sequence_key", "source_table")
    ).lower()
    source_id = compact(record.get("source_id"), 80)
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


def record_status(record: dict[str, Any]) -> str:
    return compact(record.get("status") or record.get("layer1_status") or "unknown", 80)


def raw_database_rows(paper_id: str, source_id: str) -> list[dict[str, Any]]:
    packet = ROOT / "paper_packets" / paper_id / "database"
    rows: list[dict[str, Any]] = []
    if not packet.exists() or not source_id:
        return rows
    needles = {source_id, source_id.replace("DBAASP:", ""), source_id.replace("DRAMP:", "")}
    needles |= {n.split(":")[-1] for n in list(needles)}
    for path in sorted(packet.glob("*.jsonl")):
        with path.open(encoding="utf-8", errors="replace") as fh:
            for idx, line in enumerate(fh, 1):
                if not any(n and n in line for n in needles):
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                row["_packet_database_path"] = str(path.relative_to(ROOT))
                row["_packet_database_row"] = idx
                rows.append(row)
                if len(rows) >= 3:
                    return rows
    return rows


def original_annotation(record: dict[str, Any], paper_id: str) -> str:
    source_id = compact(record.get("source_id"), 120)
    raw_rows = raw_database_rows(paper_id, source_id)
    if raw_rows:
        row = raw_rows[0]
        fields = []
        for key in (
            "database",
            "dbaasp_id",
            "DRAMP_ID",
            "source_id",
            "sequence_key",
            "peptide_name",
            "Name",
            "name",
            "Sequence",
            "sequence",
            "subject_name",
            "Target_Organism",
            "target_organism_text",
            "measure_group",
            "measure_value",
            "Activity",
            "activity_text",
            "concentration",
            "unit",
            "assay_text",
            "comments_text",
        ):
            val = row.get(key)
            if val not in (None, ""):
                fields.append(f"{key}={compact(val, 120)}")
        return "; ".join(fields) or compact(row)

    parts = []
    for key in (
        "source_id",
        "sequence_key",
        "source_table",
        "database_subject",
        "database_measure",
        "database_value",
        "database_unit",
    ):
        val = record.get(key)
        if val not in (None, ""):
            parts.append(f"{key}={compact(val, 160)}")
    return "; ".join(parts)


def reviewed_finding(record: dict[str, Any]) -> str:
    parts = []
    for key in ("conflict_summary", "conflict_context", "review_notes"):
        val = record.get(key)
        if val:
            parts.append(compact(val, 260))
    for key in (
        "name_check",
        "sequence_check",
        "modification_check",
        "source_organism_check",
        "activity_check",
        "primary_source_anchor",
    ):
        val = record.get(key)
        if val:
            parts.append(f"{key}: {compact(val, 260)}")
    return " | ".join(parts[:4])


def conflict_categories(record: dict[str, Any]) -> list[str]:
    status = record_status(record)
    text = " ".join(
        [
            status,
            compact(record.get("conflict_context"), 1000),
            compact(record.get("conflict_summary"), 1000),
            compact(record.get("review_notes"), 1000),
            compact(record.get("conflict_flags"), 1000),
            compact(record.get("sequence_check"), 1000),
            compact(record.get("activity_check"), 1000),
            compact(record.get("primary_source_anchor"), 1000),
            compact(record.get("database_subject"), 500),
            compact(record.get("database_measure"), 500),
        ]
    ).lower()
    cats: list[str] = []
    if status == "database_only_no_primary_source" or "database-only" in text or "database_only" in text:
        cats.append("database_only_no_primary_source")
    if status == "unresolved_record" or "unresolved" in text or "missing supplementary" in text:
        cats.append("unresolved_or_missing_material")
    if (
        status == "sequence_modified_not_normalized"
        or "sequence" in text
        or "modification" in text
        or "amidation" in text
        or "d-amino" in text
        or "terminal" in text
        or "variant label" in text
    ):
        cats.append("sequence_or_modification")
    if (
        "subject" in text
        or "target" in text
        or "species" in text
        or "organism" in text
        or "cell line" in text
        or "isolate" in text
    ):
        cats.append("target_or_organism")
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
        cats.append("activity_value_or_unit")
    if "species-level" in text or "range-style" in text or "aggregat" in text or "row-level" in text:
        cats.append("row_granularity")
    if "mechanism" in text or "membrane" in text or "biofilm" in text:
        cats.append("mechanism_or_claim_scope")
    return cats or ["other"]


def severity(record: dict[str, Any], cats: list[str]) -> str:
    status = record_status(record)
    if status == "unresolved_record":
        return "A"
    if "sequence_or_modification" in cats or "target_or_organism" in cats:
        return "A"
    if "database_only_no_primary_source" in cats:
        return "B"
    if "activity_value_or_unit" in cats:
        return "B"
    return "C"


def artifact_paths(paper_id: str) -> str:
    paths = [
        f"papers/{paper_id}/final/database_record_verification.json",
        f"papers/{paper_id}/final/activity_toxicity_evidence.json",
        f"papers/{paper_id}/final/mechanism_ontology_record.json",
        f"paper_packets/{paper_id}/database",
    ]
    return "; ".join(p for p in paths if (ROOT / p).exists())


def iter_records() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(PAPERS_ROOT.glob("*/final/database_record_verification.json")):
        paper_id = path.parts[-3]
        data = load_json(path)
        for idx, record in enumerate(data.get("record_audits") or data.get("records") or [], 1):
            if not isinstance(record, dict):
                continue
            status = record_status(record)
            db = infer_database(record)
            cats = conflict_categories(record)
            rows.append(
                {
                    "paper_id": paper_id,
                    "record_index": idx,
                    "database": db,
                    "source_id": compact(record.get("source_id") or record.get("sequence_key"), 120),
                    "source_table": compact(record.get("source_table"), 160),
                    "status": status,
                    "difference_categories": ";".join(cats),
                    "severity": severity(record, cats),
                    "original_database_annotation": original_annotation(record, paper_id),
                    "paper_reviewed_finding": reviewed_finding(record),
                    "artifact_paths": artifact_paths(paper_id),
                }
            )
    return rows


def pick_curated_examples(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for paper_id, source_fragment in CURATED_TARGETS:
        candidates = [
            row
            for row in rows
            if row["paper_id"] == paper_id
            and row["status"] != "source_verified"
            and source_fragment in row["source_id"]
        ]
        if not candidates:
            candidates = [
                row
                for row in rows
                if row["paper_id"] == paper_id and row["status"] != "source_verified"
            ]
        if not candidates:
            continue
        row = sorted(candidates, key=lambda r: (r["severity"], len(r["paper_reviewed_finding"])), reverse=True)[0]
        key = (row["paper_id"], row["source_id"])
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)
    return selected


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "paper_id",
        "record_index",
        "database",
        "source_id",
        "source_table",
        "status",
        "difference_categories",
        "severity",
        "original_database_annotation",
        "paper_reviewed_finding",
        "artifact_paths",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, summary: dict[str, Any], examples: list[dict[str, str]]) -> None:
    lines: list[str] = []
    lines.append("# 数据库标注 vs 论文审查差异整理")
    lines.append("")
    lines.append(f"生成时间：{summary['generated_at']}")
    lines.append("")
    lines.append("本报告聚合现有 worker-4 / worker-6 source-reviewed artifacts；不是新一轮全文重审。")
    lines.append("`source_verified` 表示当前论文证据可支持数据库记录；其他状态表示数据库原字段和论文证据之间存在冲突、缺失、粒度差异或标准化问题。")
    lines.append("")
    lines.append("## 总体规模")
    lines.append("")
    lines.append("| 指标 | 数量 |")
    lines.append("| --- | ---: |")
    for key, label in [
        ("paper_artifacts", "有 database audit artifact 的论文"),
        ("record_total", "审计数据库记录行"),
        ("source_verified_records", "source_verified 记录"),
        ("non_source_verified_records", "非 source_verified / 需保留差异记录"),
        ("papers_with_non_source_verified", "含差异记录的论文"),
    ]:
        lines.append(f"| {label} | {summary[key]} |")
    lines.append("")
    lines.append("## 按状态")
    lines.append("")
    lines.append("| 状态 | 记录数 | 论文数 | 含义 |")
    lines.append("| --- | ---: | ---: | --- |")
    meaning = {
        "source_verified": "论文证据支持数据库记录",
        "source_conflict": "数据库字段和论文证据冲突或粒度不一致",
        "sequence_modified_not_normalized": "序列字母可能匹配，但修饰/构型/末端未正确标准化",
        "database_only_no_primary_source": "数据库有记录，但当前论文材料未能验证",
        "unresolved_record": "缺失关键材料或仍需人工确认",
    }
    for status, count in summary["status_counts"]:
        papers = summary["status_paper_counts"].get(status, 0)
        lines.append(f"| `{status}` | {count} | {papers} | {meaning.get(status, '')} |")
    lines.append("")
    lines.append("## 按数据库来源的差异规模")
    lines.append("")
    lines.append("| 数据库 | 差异记录数 | 涉及论文数 |")
    lines.append("| --- | ---: | ---: |")
    for db, count in summary["non_source_verified_by_database"]:
        lines.append(f"| `{db}` | {count} | {summary['non_source_verified_papers_by_database'].get(db, 0)} |")
    lines.append("")
    lines.append("## 差异类别")
    lines.append("")
    lines.append("| 类别 | 记录数 | 说明 |")
    lines.append("| --- | ---: | --- |")
    category_meaning = {
        "activity_value_or_unit": "MIC/IC50/FICI/MBIC 等数值、单位、阈值或表格行不完全一致",
        "target_or_organism": "物种、菌株、分离株、细胞系或目标对象不一致",
        "sequence_or_modification": "序列、变体名、D/L 构型、酰胺化、环化、非天然残基等不一致",
        "row_granularity": "数据库把论文多行 isolate/table 结果压缩成范围或文本摘要",
        "database_only_no_primary_source": "数据库记录当前不能被论文原文定位验证",
        "mechanism_or_claim_scope": "数据库机制/功能标签比论文直接证据更宽或更窄",
        "unresolved_or_missing_material": "缺少补充表、PDF、附件或其他关键材料",
        "other": "其他非完全验证差异",
    }
    for cat, count in summary["category_counts"]:
        lines.append(f"| `{cat}` | {count} | {category_meaning.get(cat, '')} |")
    lines.append("")
    lines.append("## 代表性实际例子")
    lines.append("")
    lines.append("| # | 论文 | 数据库 / ID | 状态 | 原数据库标注 | 论文审查结果 | 差异判断 | 证据文件 |")
    lines.append("| ---: | --- | --- | --- | --- | --- | --- | --- |")
    for idx, row in enumerate(examples, 1):
        dbid = f"{row['database']} / {row['source_id']}"
        original = compact(row["original_database_annotation"], 180)
        finding = compact(row["paper_reviewed_finding"], 220)
        diff = f"{row['difference_categories']} / severity={row['severity']}"
        paths = compact(row["artifact_paths"], 180)
        lines.append(
            f"| {idx} | `{row['paper_id']}` | `{md_cell(dbid, 180)}` | `{row['status']}` | "
            f"{md_cell(original, 180)} | {md_cell(finding, 220)} | {md_cell(diff, 180)} | {md_cell(paths, 180)} |"
        )
    lines.append("")
    lines.append("## 使用建议")
    lines.append("")
    lines.append("- `source_verified` 可作为论文支持的数据库字段候选。")
    lines.append("- `source_conflict` 不应直接覆盖；需要按差异类别决定修正数据库、拆分记录或保留 caution。")
    lines.append("- `sequence_modified_not_normalized` 优先进入序列/修饰标准化队列。")
    lines.append("- `database_only_no_primary_source` 只能作为数据库背景，不能提升为论文原文证据。")
    lines.append("- `unresolved_record` 需要补材料或人工复核后再决定是否修正。")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    rows = iter_records()
    non_source_rows = [row for row in rows if row["status"] != "source_verified"]
    status_counts = Counter(row["status"] for row in rows)
    status_papers: dict[str, set[str]] = defaultdict(set)
    db_counts = Counter()
    db_papers: dict[str, set[str]] = defaultdict(set)
    category_counts = Counter()
    papers_with_non = set()
    for row in rows:
        status_papers[row["status"]].add(row["paper_id"])
        if row["status"] != "source_verified":
            papers_with_non.add(row["paper_id"])
            db_counts[row["database"]] += 1
            db_papers[row["database"]].add(row["paper_id"])
            for cat in row["difference_categories"].split(";"):
                category_counts[cat] += 1

    summary: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "completion_claim": "database_vs_literature_difference_summary_from_existing_source_review_artifacts",
        "paper_artifacts": len(list(PAPERS_ROOT.glob("*/final/database_record_verification.json"))),
        "record_total": len(rows),
        "source_verified_records": status_counts.get("source_verified", 0),
        "non_source_verified_records": len(non_source_rows),
        "papers_with_non_source_verified": len(papers_with_non),
        "status_counts": status_counts.most_common(),
        "status_paper_counts": {k: len(v) for k, v in sorted(status_papers.items())},
        "non_source_verified_by_database": db_counts.most_common(),
        "non_source_verified_papers_by_database": {k: len(v) for k, v in sorted(db_papers.items())},
        "category_counts": category_counts.most_common(),
    }

    examples = pick_curated_examples(rows)
    write_csv(REPORTS_ROOT / "database_vs_literature_difference_records_latest.csv", non_source_rows)
    write_csv(REPORTS_ROOT / "database_vs_literature_difference_examples_latest.csv", examples)
    (REPORTS_ROOT / "database_vs_literature_difference_summary_latest.json").write_text(
        json.dumps({**summary, "example_count": len(examples)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown(REPORTS_ROOT / "database_vs_literature_difference_examples_latest.md", summary, examples)
    print(
        json.dumps(
            {
                "summary": "reports/database_vs_literature_difference_summary_latest.json",
                "examples_md": "reports/database_vs_literature_difference_examples_latest.md",
                "examples_csv": "reports/database_vs_literature_difference_examples_latest.csv",
                "records_csv": "reports/database_vs_literature_difference_records_latest.csv",
                "paper_artifacts": summary["paper_artifacts"],
                "record_total": summary["record_total"],
                "non_source_verified_records": summary["non_source_verified_records"],
                "example_count": len(examples),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
