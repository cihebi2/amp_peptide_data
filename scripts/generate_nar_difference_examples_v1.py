#!/usr/bin/env python3
"""Generate NAR-facing database-vs-paper difference examples for v1 RC1.

This script reads the versioned release package, not stale pre-freeze reports.
It selects concrete non-source-verified examples across high-risk categories
and writes both CSV and Markdown outputs with traceable final-artifact paths.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "releases" / "amp_evidence_atlas_v1_rc1"
FREEZE_DIR = ROOT / "reports" / "nar_resource_freeze_v1"
RELEASE_AUDIT_TABLE = RELEASE_DIR / "database_record_audits.tsv"
RELEASE_MANIFEST = RELEASE_DIR / "release_manifest.json"

CATEGORY_ORDER_FOR_SELECTION = [
    "unresolved_or_missing_material",
    "database_only_no_primary_source",
    "mechanism_or_claim_scope",
    "row_granularity",
    "target_or_organism",
    "sequence_or_modification",
    "activity_value_or_unit",
]

CATEGORY_ORDER_FOR_REPORT = [
    "sequence_or_modification",
    "activity_value_or_unit",
    "target_or_organism",
    "mechanism_or_claim_scope",
    "database_only_no_primary_source",
    "row_granularity",
    "unresolved_or_missing_material",
]

REPORT_CATEGORY_RANK = {
    category: idx for idx, category in enumerate(CATEGORY_ORDER_FOR_REPORT)
}

PUBLIC_DROP_KEYS = {
    "primary_source_statement",
    "primary_source_support",
    "quote",
    "quoted_text",
    "raw_text",
    "sentence",
    "snippet",
    "support_text",
    "supports",
    "text",
}

CATEGORY_LABELS = {
    "sequence_or_modification": "序列/修饰/端基/构型",
    "activity_value_or_unit": "活性数值/单位/endpoint",
    "target_or_organism": "靶标/物种/菌株粒度",
    "mechanism_or_claim_scope": "机制标签/证据范围",
    "database_only_no_primary_source": "数据库有断言但 primary source 不支持",
    "row_granularity": "数据库行粒度 vs 论文行粒度",
    "unresolved_or_missing_material": "材料缺失或仍无法判定",
}

STATUS_GUARDRAILS = {
    "source_conflict": "表示数据库字段与当前论文证据存在冲突或粒度差异；不能自动等同于数据库错误。",
    "sequence_modified_not_normalized": "表示序列、修饰、端基、D/L 构型或变体标签未能安全标准化；不能直接当作活性冲突。",
    "database_only_no_primary_source": "表示当前 primary source 中没有可定位支持；不能证明原断言一定错误或从未存在。",
    "unresolved_record": "表示关键材料或行级映射不足；不能猜测补齐或提升为 source_verified。",
}

PREFERRED_TARGETS = [
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

PREFERRED_RANK = {
    (paper_id, source_id.lower()): idx
    for idx, (paper_id, source_id) in enumerate(PREFERRED_TARGETS)
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise TypeError(f"expected object in {path}")
    return data


def compact(value: Any, limit: int = 360) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = " ".join(text.split())
    if len(text) > limit:
        return text[: limit - 1] + "..."
    return text


def md_cell(value: Any, limit: int = 360) -> str:
    return compact(value, limit).replace("|", "\\|")


def clean_public(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: clean_public(nested)
            for key, nested in value.items()
            if str(key).lower() not in PUBLIC_DROP_KEYS
        }
    if isinstance(value, list):
        return [clean_public(item) for item in value]
    return value


def normalize_source_id(source_id: str) -> str:
    source_id = (source_id or "").strip()
    if ":" in source_id:
        source_id = source_id.split(":")[-1]
    return source_id.lower()


def categories(row: dict[str, str]) -> list[str]:
    return [item for item in row.get("difference_categories", "").split(";") if item]


def read_release_rows() -> list[dict[str, str]]:
    with RELEASE_AUDIT_TABLE.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, dialect="excel-tab"))


def decode_jsonish(value: str) -> Any:
    if not value:
        return ""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def locator_summary(row: dict[str, str]) -> str:
    parts = []
    for key in ("source_locator", "traceability", "citation_traceability"):
        value = row.get(key, "")
        if not value:
            continue
        decoded = clean_public(decode_jsonish(value))
        parts.append(f"{key}={compact(decoded, 260)}")
    return " ; ".join(parts[:2])


def database_annotation(row: dict[str, str]) -> str:
    fields = []
    for label, key in (
        ("database", "database"),
        ("source_id", "source_id"),
        ("record_name", "record_name"),
        ("sequence", "sequence"),
        ("subject", "database_subject"),
        ("measure", "database_measure"),
        ("value", "database_value"),
        ("unit", "database_unit"),
    ):
        value = row.get(key, "")
        if value:
            fields.append(f"{label}={compact(value, 120)}")
    return "; ".join(fields)


def paper_review_result(row: dict[str, str]) -> str:
    fields = []
    for label, key in (
        ("primary_sequence", "primary_source_sequence"),
        ("primary_subject", "primary_source_subject"),
        ("primary_value", "primary_source_value"),
        ("primary_unit", "primary_source_unit"),
        ("matched_activity", "matched_activity_record_id"),
    ):
        value = row.get(key, "")
        if value:
            fields.append(f"{label}={compact(value, 120)}")
    for key in (
        "conflict_context",
        "conflict_interpretation",
        "review_notes",
        "sequence_check",
        "modification_check",
        "activity_check",
        "source_organism_check",
    ):
        value = row.get(key, "")
        if value:
            fields.append(f"{key}: {compact(clean_public(decode_jsonish(value)), 240)}")
        if len(fields) >= 5:
            break
    return " | ".join(fields)


def why_difference(row: dict[str, str], category: str) -> str:
    status = row.get("status", "")
    base = {
        "sequence_or_modification": "数据库的序列、变体名、修饰或端基信息与论文审查结果不能安全等同。",
        "activity_value_or_unit": "数据库的活性 endpoint、数值、单位或阈值与论文行级证据存在差异或需要保留 caution。",
        "target_or_organism": "数据库的物种、菌株、分离株、细胞系或对象粒度与论文证据不完全一致。",
        "mechanism_or_claim_scope": "数据库或记录层面的功能/机制标签宽于、窄于或不同于论文中的直接机制证据。",
        "database_only_no_primary_source": "数据库断言无法在当前 primary source 中定位支持。",
        "row_granularity": "数据库把论文多行、多个 isolate 或多个条件压缩为单行/范围/文本摘要。",
        "unresolved_or_missing_material": "关键补充材料、图表精确值或行级映射不足，当前不能安全判定。",
    }.get(category, "数据库字段与论文审查字段存在需保留的差异。")
    return f"{base} 当前状态为 `{status}`。"


def score_row(row: dict[str, str], category: str) -> tuple[int, int, str, str]:
    pref_rank = PREFERRED_RANK.get((row["paper_id"], normalize_source_id(row.get("source_id", ""))), 10_000)
    score = 0
    if pref_rank < 10_000:
        score += 100
    if row.get("public_v1_included") == "true":
        score += 10
    if row.get("conflict_context"):
        score += 8
    if row.get("review_notes"):
        score += 5
    if row.get("source_locator") or row.get("traceability") or row.get("citation_traceability"):
        score += 5
    if row.get("database_subject") or row.get("database_measure") or row.get("database_value"):
        score += 4
    if row.get("primary_source_subject") or row.get("primary_source_value") or row.get("primary_source_sequence"):
        score += 4
    if category in categories(row):
        score += 3
    return (-score, pref_rank, row.get("paper_id", ""), row.get("source_id", ""))


def select_examples(rows: list[dict[str, str]], per_category: int) -> list[dict[str, str]]:
    candidates = [row for row in rows if row.get("status") != "source_verified"]
    by_category: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        for cat in categories(row):
            if cat in CATEGORY_ORDER_FOR_SELECTION:
                by_category[cat].append(row)

    selected: list[dict[str, str]] = []
    used_ids: set[str] = set()
    used_source_keys: set[tuple[str, str]] = set()
    for cat in CATEGORY_ORDER_FOR_SELECTION:
        ranked = sorted(by_category.get(cat, []), key=lambda row: score_row(row, cat))
        taken = 0
        for pass_name in ("new_source", "allow_same_source"):
            for row in ranked:
                audit_id = row.get("audit_record_id") or f"{row.get('paper_id')}:{row.get('record_index')}"
                source_key = (row.get("paper_id", ""), normalize_source_id(row.get("source_id", "")))
                if audit_id in used_ids:
                    continue
                if pass_name == "new_source" and source_key in used_source_keys:
                    continue
                selected_row = dict(row)
                selected_row["example_category"] = cat
                selected.append(selected_row)
                used_ids.add(audit_id)
                used_source_keys.add(source_key)
                taken += 1
                if taken >= per_category:
                    break
            if taken >= per_category:
                break
    return selected


def example_rows(selected: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    selected = sorted(
        selected,
        key=lambda row: (
            REPORT_CATEGORY_RANK.get(row["example_category"], 999),
            score_row(row, row["example_category"]),
        ),
    )
    for idx, row in enumerate(selected, 1):
        cat = row["example_category"]
        rows.append(
            {
                "example_id": f"EX{idx:03d}",
                "example_category": cat,
                "example_category_label": CATEGORY_LABELS.get(cat, cat),
                "paper_id": row.get("paper_id", ""),
                "doi": row.get("doi", ""),
                "database": row.get("database", ""),
                "source_id": row.get("source_id", ""),
                "status": row.get("status", ""),
                "difference_categories": row.get("difference_categories", ""),
                "database_annotation": database_annotation(row),
                "paper_review_result": paper_review_result(row),
                "why_difference": why_difference(row, cat),
                "source_locator_summary": locator_summary(row),
                "final_artifact_path": row.get("source_final_path", ""),
                "release_table_path": "releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv",
                "guardrail": STATUS_GUARDRAILS.get(row.get("status", ""), "保留为 caution/conflict；不得直接夸大为数据库错误。"),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "example_id",
        "example_category",
        "example_category_label",
        "paper_id",
        "doi",
        "database",
        "source_id",
        "status",
        "difference_categories",
        "database_annotation",
        "paper_review_result",
        "why_difference",
        "source_locator_summary",
        "final_artifact_path",
        "release_table_path",
        "guardrail",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, str]], manifest: dict[str, Any], row_stats: dict[str, Any], generated_at: str) -> None:
    scope = manifest.get("source_freeze_summary", {}).get("scope", {})
    by_category = defaultdict(list)
    for row in rows:
        by_category[row["example_category"]].append(row)

    lines = [
        "# AMP Evidence Atlas v1 RC1：数据库标注 vs 论文审查差异例子",
        "",
        f"生成时间：{generated_at}",
        "",
        "本报告从 `releases/amp_evidence_atlas_v1_rc1/database_record_audits.tsv` 选择真实案例，",
        "用于说明数据库原标注与 primary-literature source-reviewed 审查结果之间的差异类型。",
        "它不是新一轮全文重审，也不把 non-source-verified 自动解释为数据库错误。",
        "",
        "## 当前 release 口径",
        "",
        "| 指标 | 数值 |",
        "| --- | ---: |",
    ]
    for key in (
        "paper_final_artifact_count",
        "public_v1_candidate_papers",
        "excluded_or_non_publication_grade_papers",
        "database_audit_rows",
        "source_verified_rows",
        "non_source_verified_rows",
        "activity_records",
        "mechanism_claims",
    ):
        lines.append(f"| `{key}` | {scope.get(key, '')} |")

    lines.extend(
        [
            "",
            "## 选择和解释边界",
            "",
            "- 只选择 `status != source_verified` 的记录作为差异案例。",
            "- 每条案例都保留 `release_table_path` 和 `final_artifact_path`，便于复核。",
            "- locator 只保留路径/定位信息，不复制论文全文、PDF、图片或补充材料原件。",
            "- 一条记录可有多个差异标签；本报告为阅读方便给每条案例指定一个主展示类别。",
            "- `source_conflict`、`database_only_no_primary_source`、`unresolved_record` 都不能被简单说成数据库错误。",
            "",
            "## 当前非 source-verified 记录中的差异类别规模",
            "",
            "| 类别 | 非 source-verified rows | 本报告例子数 |",
            "| --- | ---: | ---: |",
        ]
    )
    category_counts = row_stats["non_source_category_counts"]
    for cat in CATEGORY_ORDER_FOR_REPORT:
        lines.append(
            f"| `{cat}` / {CATEGORY_LABELS.get(cat, cat)} | {category_counts.get(cat, 0)} | {len(by_category.get(cat, []))} |"
        )

    lines.extend(
        [
            "",
            "## 代表性例子",
            "",
        ]
    )
    for cat in CATEGORY_ORDER_FOR_REPORT:
        cat_rows = by_category.get(cat, [])
        if not cat_rows:
            continue
        lines.extend(
            [
                f"### {CATEGORY_LABELS.get(cat, cat)}",
                "",
                "| ID | 论文 | 数据库/ID | 状态 | 数据库原标注 | 论文审查结果 | 为什么不同 | 证据路径 |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in cat_rows:
            evidence = f"{row['release_table_path']} ; {row['final_artifact_path']}"
            lines.append(
                "| {id} | `{paper}` | `{db} / {sid}` | `{status}` | {dbann} | {paperres} | {why} | {evidence} |".format(
                    id=row["example_id"],
                    paper=row["paper_id"],
                    db=row["database"],
                    sid=row["source_id"],
                    status=row["status"],
                    dbann=md_cell(row["database_annotation"], 380),
                    paperres=md_cell(row["paper_review_result"], 420),
                    why=md_cell(row["why_difference"], 280),
                    evidence=md_cell(evidence, 260),
                )
            )
        lines.append("")

    lines.extend(
        [
            "## 可用于论文写作的谨慎表述",
            "",
            "可以说：",
            "",
            "> The resource preserves source-verified records separately from evidence discordance, provenance gaps, modification-normalization issues, database-only assertions, and unresolved records.",
            "",
            "不应说：",
            "",
            "- “所有 non-source-verified 记录都是数据库错误”；",
            "- “accepted_with_cautions 等于 clean”；",
            "- “数据库行数等于各数据库原始全库分母”；",
            "- “缺失材料的图表精确值已经被补齐”。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_outputs(per_category: int) -> dict[str, Any]:
    rows = read_release_rows()
    manifest = load_json(RELEASE_MANIFEST)
    selected = select_examples(rows, per_category)
    examples = example_rows(selected)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = FREEZE_DIR / f"database_vs_paper_difference_examples_v1_{stamp}.csv"
    md_path = FREEZE_DIR / f"database_vs_paper_difference_examples_v1_{stamp}.md"

    non_source_rows = [row for row in rows if row.get("status") != "source_verified"]
    status_counts = Counter(row.get("status", "") for row in non_source_rows)
    cat_counts: Counter[str] = Counter()
    for row in non_source_rows:
        cat_counts.update(categories(row))

    write_csv(csv_path, examples)
    write_md(
        md_path,
        examples,
        manifest,
        {
            "non_source_status_counts": dict(status_counts),
            "non_source_category_counts": dict(cat_counts),
        },
        generated_at,
    )

    latest_csv = FREEZE_DIR / "database_vs_paper_difference_examples_v1_latest.csv"
    latest_md = FREEZE_DIR / "database_vs_paper_difference_examples_v1_latest.md"
    shutil.copyfile(csv_path, latest_csv)
    shutil.copyfile(md_path, latest_md)

    coverage = Counter(row["example_category"] for row in examples)
    return {
        "generated_at": generated_at,
        "csv": str(csv_path.relative_to(ROOT)),
        "md": str(md_path.relative_to(ROOT)),
        "latest_csv": str(latest_csv.relative_to(ROOT)),
        "latest_md": str(latest_md.relative_to(ROOT)),
        "example_count": len(examples),
        "category_coverage": dict(coverage),
        "non_source_status_counts": dict(status_counts),
        "non_source_category_counts": dict(cat_counts),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-category", type=int, default=3)
    args = parser.parse_args()
    result = build_outputs(args.per_category)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
