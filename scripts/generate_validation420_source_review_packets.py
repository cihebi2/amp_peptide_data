#!/usr/bin/env python3
"""Build paper-level true source-review packets for the 420-row validation manifest."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation"
VALIDATION_MANIFEST = VALIDATION_DIR / "validation_manifest_latest.csv"
RELEASE_TABLE = ROOT / "releases" / "amp_evidence_atlas_v1_rc1" / "database_record_audits.tsv"
OUTDIR = VALIDATION_DIR / "validation420" / "source_review_packets"
MERGED_CORPUS_ROOT = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus")

HELPER_PATH = ROOT / "scripts" / "generate_pilot20_true_review_packets.py"
spec = importlib.util.spec_from_file_location("pilot_packet_helpers", HELPER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import helpers from {HELPER_PATH}")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)

RESULT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Validation420PaperSourceReviewResult",
    "type": "object",
    "required": [
        "paper_id",
        "review_sample_id",
        "reviewed_at",
        "review_model",
        "reasoning_effort",
        "final_decision",
        "sample_row_decisions",
        "material_review",
        "worker6_adjudication",
        "rework_targets",
        "caution_findings",
        "checked_inputs",
    ],
    "properties": {
        "review_model": {"const": "gpt-5.5"},
        "reasoning_effort": {"const": "xhigh"},
        "final_decision": {
            "enum": [
                "accepted_clean",
                "accepted_with_cautions",
                "needs_targeted_rework",
                "blocked_missing_primary_material",
                "unverifiable_best_effort",
                "deferred_not_safe_to_edit",
            ]
        },
        "sample_row_decisions": {"type": "array"},
        "rework_targets": {"type": "array"},
        "caution_findings": {"type": "array"},
        "checked_inputs": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": True,
}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def read_csv(path: Path, dialect: str | None = None) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        if dialect == "excel-tab":
            return list(csv.DictReader(fh, dialect="excel-tab"))
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_rel(path: Path | str) -> str:
    try:
        p = Path(str(path))
        return str(p.resolve().relative_to(ROOT))
    except (ValueError, RuntimeError, OSError):
        return str(path)


def packet_name(paper_id: str) -> str:
    return paper_id.replace("/", "_")


def load_release_rows(audit_ids: set[str]) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with RELEASE_TABLE.open(encoding="utf-8", newline="") as fh:
        for row_num, row in enumerate(csv.DictReader(fh, dialect="excel-tab"), start=2):
            audit_id = row.get("audit_record_id", "")
            if audit_id in audit_ids:
                row["_release_tsv_row_number"] = str(row_num)
                rows[audit_id] = row
                if len(rows) == len(audit_ids):
                    break
    return rows


def grouped_samples(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["paper_id"]].append(row)
    return dict(sorted(grouped.items()))


def owner_lane_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    lanes: Counter[str] = Counter()
    for row in rows:
        hint = helper.owner_worker_hint(row)
        for lane in hint.get("owner_lanes_to_consult", []):
            lanes[str(lane)] += 1
    return {"lane_counts": dict(lanes), "primary_lanes": sorted(lanes)}


def sample_contexts(samples: list[dict[str, str]], release_rows: dict[str, dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    sample_payloads: list[dict[str, Any]] = []
    final_records: list[dict[str, Any]] = []
    locator_hints: dict[str, Any] = {}
    for sample in samples:
        audit_id = sample["audit_record_id"]
        release_row = release_rows.get(audit_id, {})
        final_path = ROOT / sample.get("final_artifact_path", "")
        final_data = helper.read_json_if_object(final_path)
        final_record = helper.find_final_record(final_data, sample) if final_data else None
        sample_payloads.append({**sample, "release_row_found": bool(release_row), "final_record_found": bool(final_record)})
        final_records.append({
            "sample_id": sample.get("sample_id", ""),
            "audit_record_id": audit_id,
            "final_artifact_path": sample.get("final_artifact_path", ""),
            "sample_final_record": helper.compact_jsonish(final_record or {}),
        })
        locator_hints[sample.get("sample_id", audit_id)] = {
            "audit_record_id": audit_id,
            "source_locator_summary": sample.get("source_locator_summary", ""),
            "release_row_hints": helper.source_locator_hints(release_row) if release_row else {},
        }
    return sample_payloads, final_records, locator_hints


def prompt_text(packet_dir: Path, paper_id: str, review_sample_id: str, sample_count: int, schema_path: Path) -> str:
    result_path = packet_dir / "true_review_result.json"
    ticket_path = packet_dir / "rework_tickets.jsonl"
    return f"""# Validation420 True Source Review Prompt

You are a fresh Codex CLI worker-6 reviewer for AMP Evidence Atlas / NAR Resource v1.
This packet reviews one paper and all validation-manifest rows sampled for that paper.

## Required model/provenance

- The runner launches `codex exec -m gpt-5.5 -c model_reasoning_effort=\"xhigh\"`.
- Record `review_model: \"gpt-5.5\"` and `reasoning_effort: \"xhigh\"` in the result.
- Treat the runner command/header as sufficient model/effort provenance unless a runtime status contradicts it.

## Working directory

`/root/work/抗菌肽/数据库/batch/4-team`

## Packet

- paper_id: `{paper_id}`
- review_sample_id: `{review_sample_id}`
- sampled validation rows for this paper: `{sample_count}`
- packet directory: `{safe_rel(packet_dir)}`
- validation samples: `{safe_rel(packet_dir / 'validation_samples.json')}`
- release rows: `{safe_rel(packet_dir / 'release_rows.json')}`
- sample final records: `{safe_rel(packet_dir / 'sample_final_records.json')}`
- source locator hints: `{safe_rel(packet_dir / 'source_locator_hints.json')}`
- material inventory: `{safe_rel(packet_dir / 'material_inventory.json')}`
- result schema: `{safe_rel(schema_path)}`
- write result JSON: `{safe_rel(result_path)}`
- if hard failures exist, write tickets JSONL: `{safe_rel(ticket_path)}`

## Instructions to read before deciding

1. `.codex/skills/amp-three-layer-curation/SKILL.md`
2. `.codex/skills/paper-adjudicator-review-worker/SKILL.md`
3. `.codex/skills/amp-three-layer-curation/references/publication-grade-source-review.md`
4. `.codex/skills/amp-three-layer-curation/references/publication-grade-quality-gate.md`
5. `.codex/skills/amp-three-layer-curation/references/team-rework-message-contract.md`
6. `.codex/skills/amp-three-layer-curation/references/two-queue-paper-packet-contract.md`
7. Owner skills if relevant: `paper-database-record-auditor`, `paper-body-table-worker`, `paper-supp-evidence-worker`, `paper-mechanism-ontology-worker`.

## Review task

Use only local materials; do not browse the web.

1. Re-open `material_inventory.json`, the packet sources, final artifacts, database JSONL rows, and source locators relevant to the sampled rows.
2. For every row in `validation_samples.json`, decide whether the row is source-backed, caution-preserving, repairable, blocked by missing material, or only best-effort unverifiable.
3. Check layer 1 database identity/status, layer 2 activity/toxicity row-level evidence, and layer 3 mechanism ontology where relevant to sampled rows.
4. Act as worker-6 for this paper: preserve conflicts and uncertainty; do not convert database-only or conflict rows into clean source_verified.
5. Do not edit canonical `papers/<paper_id>/final/` artifacts in this phase. This is validation/source-review evidence collection. Hard failures must be tickets, not silent edits.

## Decision rules

Each `sample_row_decisions[]` item should include:

- `sample_id`
- `audit_record_id`
- `row_decision`: `confirmed`, `confirmed_with_caution`, `needs_targeted_rework`, `blocked_missing_primary_material`, `unverifiable_best_effort`, or `not_applicable`
- `evidence_summary`
- `locators_checked`
- `cautions`
- `rework_target_ids`

Use one paper-level `final_decision`:

- `accepted_clean`: all sampled rows confirmed, no hard rework and no cautions.
- `accepted_with_cautions`: no hard rework, but conflicts/cautions/material limits are preserved.
- `needs_targeted_rework`: one or more repairable defects exist.
- `blocked_missing_primary_material`: required local primary/supplementary material is absent/unreadable after best effort.
- `unverifiable_best_effort`: bounded effort could not decide; explain exactly what was inspected and why it remains unresolved.
- `deferred_not_safe_to_edit`: runner/source inconsistency prevents safe judgement.

Hard failures requiring `needs_targeted_rework` include missing primary-source locator for `source_verified`, unsupported unresolved/database-only reason, sentence-fragment targets, generic endpoints, MIC-like rows without unit/rationale, non-standard mechanism evidence classes in accepted outputs, direct mechanism without direct assay type, templated worker-6 review, missing provenance, or open hard rework targets.

If any row has `needs_targeted_rework` or `blocked_missing_primary_material`, write `rework_tickets.jsonl` with durable tickets containing target_queue, owner worker, reason, requested_outputs, blocks, and created_at.

Write `{safe_rel(result_path)}` as JSON matching the schema. Keep final chat response short and point to the result path.
"""


def single_run_script_text(prompt_path: Path, last_message_path: Path) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
cd {ROOT}
codex exec \
  -C {ROOT} \
  --skip-git-repo-check \
  --add-dir {ROOT} \
  --add-dir {MERGED_CORPUS_ROOT} \
  -m gpt-5.5 \
  -c 'model_reasoning_effort="xhigh"' \
  -c 'approval_policy="never"' \
  -o {last_message_path} \
  - < {prompt_path}
"""


def build_packet(paper_id: str, samples: list[dict[str, str]], release_rows: dict[str, dict[str, str]], out_root: Path, run_id: str, force: bool) -> dict[str, Any]:
    review_sample_id = f"V420P{len(build_packet.rows) + 1:04d}"
    packet_dir = out_root / f"{review_sample_id}__{packet_name(paper_id)}"
    if packet_dir.exists() and force:
        shutil.rmtree(packet_dir)
    packet_dir.mkdir(parents=True, exist_ok=True)

    sample_payloads, final_records, locator_hints = sample_contexts(samples, release_rows)
    inventory = helper.build_inventory(paper_id)
    owner_summary = owner_lane_summary(samples)
    schema_path = packet_dir / "true_review_result.schema.json"
    result_path = packet_dir / "true_review_result.json"

    packet_manifest = {
        "packet_schema": "validation420_paper_source_review_packet_v1",
        "generated_at": now_utc(),
        "run_id": run_id,
        "review_sample_id": review_sample_id,
        "paper_id": paper_id,
        "sample_count": len(samples),
        "sample_ids": [row.get("sample_id", "") for row in samples],
        "audit_record_ids": [row.get("audit_record_id", "") for row in samples],
        "status_counts": dict(Counter(row.get("status", "") for row in samples)),
        "category_counts": dict(Counter(row.get("primary_validation_category", "") for row in samples)),
        "owner_lane_summary": owner_summary,
        "inputs": {
            "validation_manifest": safe_rel(VALIDATION_MANIFEST),
            "release_table": safe_rel(RELEASE_TABLE),
            "paper_packet_dir": f"paper_packets/{paper_id}",
            "paper_dir": f"papers/{paper_id}",
        },
        "outputs_expected": {
            "true_review_result": safe_rel(result_path),
            "rework_tickets": safe_rel(packet_dir / "rework_tickets.jsonl"),
            "codex_last_message": safe_rel(packet_dir / "CODEX_LAST_MESSAGE.md"),
        },
        "completion_claim": "validation420_source_review_packet_ready_not_scientific_acceptance",
    }

    write_json(packet_dir / "packet_manifest.json", packet_manifest)
    write_json(packet_dir / "validation_samples.json", sample_payloads)
    write_json(packet_dir / "release_rows.json", {row["audit_record_id"]: release_rows.get(row["audit_record_id"], {}) for row in samples})
    write_json(packet_dir / "sample_final_records.json", final_records)
    write_json(packet_dir / "source_locator_hints.json", locator_hints)
    write_json(packet_dir / "material_inventory.json", inventory)
    write_json(schema_path, RESULT_SCHEMA)
    (packet_dir / "CODEX_REVIEW_PROMPT.md").write_text(prompt_text(packet_dir, paper_id, review_sample_id, len(samples), schema_path), encoding="utf-8")
    run_script = packet_dir / "run_codex_review.sh"
    run_script.write_text(single_run_script_text(packet_dir / "CODEX_REVIEW_PROMPT.md", packet_dir / "CODEX_LAST_MESSAGE.md"), encoding="utf-8")
    os.chmod(run_script, 0o755)

    release_found = sum(1 for row in sample_payloads if row.get("release_row_found"))
    final_found = sum(1 for row in sample_payloads if row.get("final_record_found"))
    build_packet.rows.append(paper_id)
    return {
        "review_sample_id": review_sample_id,
        "paper_id": paper_id,
        "sample_count": len(samples),
        "sample_ids": ";".join(row.get("sample_id", "") for row in samples),
        "audit_record_ids": ";".join(row.get("audit_record_id", "") for row in samples),
        "status_counts": json.dumps(dict(Counter(row.get("status", "") for row in samples)), ensure_ascii=False, sort_keys=True),
        "category_counts": json.dumps(dict(Counter(row.get("primary_validation_category", "") for row in samples)), ensure_ascii=False, sort_keys=True),
        "packet_dir": safe_rel(packet_dir),
        "prompt_path": safe_rel(packet_dir / "CODEX_REVIEW_PROMPT.md"),
        "result_path": safe_rel(result_path),
        "rework_tickets_path": safe_rel(packet_dir / "rework_tickets.jsonl"),
        "run_script_path": safe_rel(run_script),
        "sample_release_rows_found": release_found,
        "sample_final_records_found": final_found,
        "material_queue_status": inventory["packet_manifest_summary"].get("material_queue_status") or "",
        "analysis_queue_status": inventory["packet_manifest_summary"].get("analysis_queue_status") or "",
        "existing_review_status": inventory["review_report_summary"].get("review_status") or "",
        "existing_publication_grade": str(inventory["review_report_summary"].get("publication_grade", "")),
        "known_risk_count": len(inventory.get("known_risks_for_reviewer", [])),
        "known_risks": ";".join(inventory.get("known_risks_for_reviewer", [])),
        "ready_for_codex_review": str(release_found == len(samples) and final_found == len(samples)).lower(),
    }


build_packet.rows = []  # type: ignore[attr-defined]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=VALIDATION_MANIFEST)
    parser.add_argument("--outdir", type=Path, default=OUTDIR)
    parser.add_argument("--limit-papers", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.manifest)
    grouped = grouped_samples(rows)
    if args.limit_papers:
        grouped = dict(list(grouped.items())[: args.limit_papers])
    audit_ids = {row["audit_record_id"] for samples in grouped.values() for row in samples}
    release_rows = load_release_rows(audit_ids)
    run_id = stamp()
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / ".generated_by_generate_validation420_source_review_packets").write_text(now_utc() + "\n", encoding="utf-8")

    build_packet.rows = []  # type: ignore[attr-defined]
    index_rows = [build_packet(paper_id, samples, release_rows, args.outdir, run_id, args.force) for paper_id, samples in grouped.items()]
    fields = [
        "review_sample_id",
        "paper_id",
        "sample_count",
        "sample_ids",
        "audit_record_ids",
        "status_counts",
        "category_counts",
        "packet_dir",
        "prompt_path",
        "result_path",
        "rework_tickets_path",
        "run_script_path",
        "sample_release_rows_found",
        "sample_final_records_found",
        "material_queue_status",
        "analysis_queue_status",
        "existing_review_status",
        "existing_publication_grade",
        "known_risk_count",
        "known_risks",
        "ready_for_codex_review",
    ]
    index_path = args.outdir / f"packet_index_{run_id}.csv"
    latest_index = args.outdir / "packet_index_latest.csv"
    write_csv(index_path, index_rows, fields)
    shutil.copyfile(index_path, latest_index)
    write_json(args.outdir / "true_review_result.schema.json", RESULT_SCHEMA)

    summary = {
        "generated_at": now_utc(),
        "run_id": run_id,
        "completion_claim": "validation420_source_review_packets_ready_not_review_completed",
        "manifest": safe_rel(args.manifest),
        "packet_root": safe_rel(args.outdir),
        "manifest_row_count": len(rows),
        "packet_count": len(index_rows),
        "sample_rows_in_packets": sum(int(row["sample_count"]) for row in index_rows),
        "ready_for_codex_review_count": sum(1 for row in index_rows if row["ready_for_codex_review"] == "true"),
        "status_counts": dict(Counter(row.get("status", "") for samples in grouped.values() for row in samples)),
        "known_risk_counts": dict(Counter(risk for row in index_rows for risk in row["known_risks"].split(";") if risk)),
        "outputs": {
            "packet_index_csv": safe_rel(index_path),
            "latest_packet_index_csv": safe_rel(latest_index),
            "runner_command": f"python scripts/run_validation420_source_reviews.py --packet-index {safe_rel(latest_index)} --parallel 4",
        },
    }
    summary_path = args.outdir / f"packet_summary_{run_id}.json"
    write_json(summary_path, summary)
    shutil.copyfile(summary_path, args.outdir / "packet_summary_latest.json")

    readme = [
        "# Validation420 Source-Review Packets",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "These packets group the 420 validation rows by paper. They are inputs for fresh Codex CLI source-review runs and do not prove acceptance by themselves.",
        "",
        "```bash",
        f"python scripts/run_validation420_source_reviews.py --packet-index {safe_rel(latest_index)} --parallel 4",
        "```",
        "",
    ]
    (args.outdir / "README.md").write_text("\n".join(readme), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
