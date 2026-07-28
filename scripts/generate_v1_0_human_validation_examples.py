#!/usr/bin/env python3
"""Generate a compact, stratified human-check example pack for Atlas v1.0.

The pack contains pending cases and blank label templates. It never promotes AI
review, worker agreement, or release status to a human gold label.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "releases" / "amp_evidence_atlas_v1_0"
AUDITS = RELEASE / "database_record_audits.tsv"
OUTDIR = (
    ROOT
    / "reports"
    / "nar_resource_freeze_v1"
    / "manual_validation"
    / "v1_0_human_check_examples"
)
DATABASES = ["APD6", "CAMP", "DBAASP", "DRAMP", "dbAMP"]
STATUSES = [
    "source_verified",
    "source_conflict",
    "sequence_modified_not_normalized",
    "database_only_no_primary_source",
]

OUTPUT_FIELDS = [
    "case_id",
    "release_id",
    "database",
    "atlas_status",
    "difference_categories",
    "paper_id",
    "doi",
    "audit_record_id",
    "source_id",
    "record_name",
    "database_subject",
    "database_measure",
    "database_value",
    "database_unit",
    "primary_source_subject",
    "primary_source_value",
    "primary_source_unit",
    "sequence",
    "primary_source_sequence",
    "modification_check",
    "activity_check",
    "conflict_flags",
    "conflict_interpretation",
    "source_locator",
    "traceability",
    "citation_traceability",
    "matched_activity_record_id",
    "source_final_path",
    "human_decision",
    "human_correct_status",
    "human_error_class",
    "human_severity",
    "human_notes",
    "reviewer_id",
    "reviewed_at",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compact(value: Any, limit: int = 600) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def completeness_score(row: dict[str, str]) -> tuple[int, str]:
    common = [
        "source_id",
        "record_name",
        "source_locator",
        "traceability",
        "citation_traceability",
        "conflict_interpretation",
    ]
    status_specific = {
        "source_verified": [
            "database_subject",
            "database_measure",
            "database_value",
            "primary_source_subject",
            "primary_source_value",
            "matched_activity_record_id",
        ],
        "source_conflict": [
            "database_subject",
            "database_measure",
            "database_value",
            "primary_source_subject",
            "primary_source_value",
            "conflict_flags",
            "activity_check",
        ],
        "sequence_modified_not_normalized": [
            "sequence",
            "primary_source_sequence",
            "modification_check",
        ],
        "database_only_no_primary_source": [
            "database_subject",
            "database_measure",
            "database_value",
        ],
        "unresolved_record": [
            "database_subject",
            "database_measure",
            "database_value",
            "conflict_flags",
            "activity_check",
        ],
    }
    fields = common + status_specific.get(row["status"], [])
    score = sum(3 if row.get(field, "").strip() else 0 for field in fields)
    if row.get("public_v1_included", "").lower() == "true":
        score += 4
    if row.get("doi", ""):
        score += 2
    # Stable lexical tie-breaker makes regeneration deterministic.
    return score, row.get("audit_record_id", "")


def select_cases() -> list[dict[str, str]]:
    candidates: dict[tuple[str, str], list[dict[str, str]]] = {}
    with AUDITS.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, dialect="excel-tab"):
            key = (row["database"], row["status"])
            if key in {
                *((database, status) for database in DATABASES for status in STATUSES),
                ("DBAASP", "unresolved_record"),
            }:
                candidates.setdefault(key, []).append(row)

    selected: list[dict[str, str]] = []
    used_papers: set[str] = set()
    strata = [
        *((database, status) for database in DATABASES for status in STATUSES),
        ("DBAASP", "unresolved_record"),
    ]
    for key in strata:
        rows = candidates.get(key, [])
        if not rows:
            raise RuntimeError(f"no candidate for stratum {key}")
        rows.sort(key=completeness_score, reverse=True)
        unique = [row for row in rows if row["paper_id"] not in used_papers]
        chosen = unique[0] if unique else rows[0]
        selected.append(chosen)
        used_papers.add(chosen["paper_id"])
    return selected


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            dialect="excel-tab",
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def case_markdown(row: dict[str, str]) -> str:
    def value(field: str) -> str:
        return compact(row.get(field, "")) or "—"

    return f"""# {row['case_id']}：{row['database']} / {row['atlas_status']}

> 状态：等待独立人工核对。本文档不包含人工金标签。

## 定位

- paper_id：`{row['paper_id']}`
- DOI：`{value('doi')}`
- audit_record_id：`{row['audit_record_id']}`
- 数据库 source_id：`{value('source_id')}`
- final artifact：`{value('source_final_path')}`

## Atlas 当前重构

| 项目 | 数据库主张 | 原文重构 |
| --- | --- | --- |
| subject | {value('database_subject')} | {value('primary_source_subject')} |
| measure | {value('database_measure')} | — |
| value | {value('database_value')} | {value('primary_source_value')} |
| unit | {value('database_unit')} | {value('primary_source_unit')} |
| sequence | {value('sequence')} | {value('primary_source_sequence')} |

- Atlas 状态：`{row['atlas_status']}`
- 差异类别：`{value('difference_categories')}`
- modification_check：{value('modification_check')}
- activity_check：{value('activity_check')}
- conflict_flags：{value('conflict_flags')}
- conflict_interpretation：{value('conflict_interpretation')}

## 证据入口

- source_locator：{value('source_locator')}
- traceability：{value('traceability')}
- citation_traceability：{value('citation_traceability')}
- matched_activity_record_id：`{value('matched_activity_record_id')}`

## 人工需要回答

1. 数据库主张是否被准确抄录？
2. Atlas 的原文值、单位、subject、序列和修饰是否可在指定位置复现？
3. 当前 `atlas_status` 是否正确？
4. 如果不正确，正确状态、错误类别和严重度是什么？
5. 材料不足时必须标记 `insufficient_evidence`，不得猜测。
"""


def main() -> None:
    if OUTDIR.exists():
        marker = OUTDIR / ".generated_by_generate_v1_0_human_validation_examples"
        if not marker.exists():
            raise RuntimeError(f"refusing to overwrite unmanaged directory: {OUTDIR}")
        shutil.rmtree(OUTDIR)
    (OUTDIR / "cases").mkdir(parents=True)
    selected = select_cases()
    output_rows: list[dict[str, str]] = []
    for index, source in enumerate(selected, 1):
        row = {field: source.get(field, "") for field in OUTPUT_FIELDS}
        row["case_id"] = f"ATLASV1-HC-{index:03d}"
        row["release_id"] = "amp-evidence-atlas-v1.0"
        row["atlas_status"] = source["status"]
        output_rows.append(row)
        (OUTDIR / "cases" / f"{row['case_id']}.md").write_text(
            case_markdown(row), encoding="utf-8"
        )

    write_tsv(OUTDIR / "case_manifest.tsv", output_rows, OUTPUT_FIELDS)
    label_fields = [
        "case_id",
        "audit_record_id",
        "database",
        "atlas_status",
        "human_decision",
        "human_correct_status",
        "human_error_class",
        "human_severity",
        "human_notes",
        "reviewer_id",
        "reviewed_at",
    ]
    write_tsv(OUTDIR / "human_labels_template.tsv", output_rows, label_fields)

    readme = """# AMP Evidence Atlas v1.0 人工核对案例包

该案例包从冻结的 v1.0 数据中确定性选出21条待核对记录：

- APD6、CAMP、DBAASP、DRAMP、dbAMP 各覆盖4种主要状态；
- 额外包含1条 DBAASP `unresolved_record`；
- 优先选择字段和证据入口较完整、并尽量不重复论文的记录。

这些案例的 Atlas 状态是**待验证主张**，不是人工标签。

## 建议双人盲审

两名评审者分别复制 `human_labels_template.tsv`，独立填写后再合并裁决。

`human_decision` 允许值：

- `agree_with_atlas`
- `status_should_change`
- `insufficient_evidence`
- `cannot_access_source`

`human_correct_status` 允许使用 Atlas 五类状态，或在方案预注册后新增类别。

`human_error_class` 建议值：

- `no_error`
- `sequence_or_modification`
- `activity_value_or_unit`
- `target_or_organism`
- `mechanism_or_claim_scope`
- `row_granularity`
- `citation_or_locator`
- `other`

严重度建议为 `none/minor/major/critical`。任何自动脚本都不得预填人工字段。
"""
    (OUTDIR / "README.md").write_text(readme, encoding="utf-8")
    (OUTDIR / ".generated_by_generate_v1_0_human_validation_examples").write_text(
        datetime.now(timezone.utc).isoformat(timespec="seconds") + "\n",
        encoding="utf-8",
    )
    files = sorted(path for path in OUTDIR.rglob("*") if path.is_file())
    manifest = {
        "schema": "amp_evidence_atlas_v1_human_check_example_pack_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "release_id": "amp-evidence-atlas-v1.0",
        "completion_claim": "pending_human_check_examples_not_human_validation",
        "case_count": len(output_rows),
        "database_counts": dict(Counter(row["database"] for row in output_rows)),
        "status_counts": dict(Counter(row["atlas_status"] for row in output_rows)),
        "unique_paper_count": len({row["paper_id"] for row in output_rows}),
        "human_fields_prefilled": False,
        "files": [
            {
                "path": str(path.relative_to(OUTDIR)),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in files
        ],
    }
    (OUTDIR / "case_pack_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
