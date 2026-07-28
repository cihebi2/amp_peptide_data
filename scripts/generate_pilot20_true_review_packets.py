#!/usr/bin/env python3
"""Build true source-review packets for the pilot-20 validation sample.

The packet is a handoff surface for a fresh Codex CLI reviewer. It does not
change paper finals. It collects the sampled audit row, release row, final-row
context, material inventory, output schema, and a strict review prompt.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "reports" / "nar_resource_freeze_v1" / "manual_validation"
PILOT_DIR = VALIDATION_DIR / "pilot20"
PILOT_MANIFEST = PILOT_DIR / "pilot20_manifest_latest.csv"
PILOT_RESULTS = PILOT_DIR / "pilot20_results_latest.csv"
RELEASE_TABLE = ROOT / "releases" / "amp_evidence_atlas_v1_rc1" / "database_record_audits.tsv"
OUTDIR = PILOT_DIR / "source_review_packets"

MERGED_CORPUS_ROOT = Path("/mnt/d/work/抗菌肽/数据库/merged_amp_corpus")

RESULT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Pilot20TrueSourceReviewResult",
    "type": "object",
    "required": [
        "paper_id",
        "pilot_sample_id",
        "audit_record_id",
        "reviewed_at",
        "review_model",
        "reasoning_effort",
        "decision",
        "material_review",
        "layer1_database_record_review",
        "layer2_activity_toxicity_review",
        "layer3_mechanism_review",
        "worker6_adjudication",
        "rework_targets",
        "caution_findings",
        "checked_inputs",
    ],
    "properties": {
        "paper_id": {"type": "string"},
        "pilot_sample_id": {"type": "string"},
        "audit_record_id": {"type": "string"},
        "reviewed_at": {"type": "string"},
        "review_model": {"const": "gpt-5.5"},
        "reasoning_effort": {"const": "xhigh"},
        "decision": {
            "enum": [
                "pass_source_review",
                "accepted_with_cautions_confirmed",
                "needs_targeted_rework",
                "blocked_missing_primary_material",
                "unverifiable_best_effort",
            ]
        },
        "confidence": {"enum": ["high", "medium", "low"]},
        "material_review": {"type": "object"},
        "layer1_database_record_review": {"type": "object"},
        "layer2_activity_toxicity_review": {"type": "object"},
        "layer3_mechanism_review": {"type": "object"},
        "worker6_adjudication": {"type": "object"},
        "rework_targets": {"type": "array"},
        "caution_findings": {"type": "array"},
        "checked_inputs": {"type": "array", "items": {"type": "string"}},
        "best_effort_limits": {"type": "array"},
    },
    "additionalProperties": True,
}


STANDARD_PACKET_PATHS = [
    "packet_manifest.json",
    "raw/paper.xml",
    "raw/paper.pdf",
    "raw/oa_package",
    "raw/supplementary_original",
    "extracted/xml_sections.json",
    "extracted/pdf_text.jsonl",
    "extracted/pdf_tables.json",
    "extracted/figure_captions.json",
    "extracted/supplementary_index.json",
    "extracted/supplementary_text.jsonl",
    "extracted/supplementary_tables.json",
    "extracted/archive_manifest.json",
    "extracted/ocr",
    "database/database_source_manifest.json",
    "database/linked_sequence_records.jsonl",
    "database/linked_literature_records.jsonl",
    "database/linked_experiment_records.jsonl",
    "database/linked_assay_records.jsonl",
    "database/linked_dramp_activity_records.jsonl",
    "locators/locator_index.json",
    "locators/citation_map.json",
    "extraction/extraction_status.json",
    "extraction/extraction_quality_report.json",
    "extraction/extraction_errors.jsonl",
    "analysis/analysis_status.json",
    "analysis/database_record_audit.json",
    "analysis/activity_toxicity_evidence.json",
    "analysis/mechanism_evidence.json",
    "analysis/adjudication_report.json",
    "final/database_record_verification.json",
    "final/activity_toxicity_evidence.json",
    "final/mechanism_evidence.json",
    "final/review_report.json",
    "rework/rework_requests.jsonl",
    "rework/rework_responses.jsonl",
]

STANDARD_PAPER_PATHS = [
    "final/database_record_verification.json",
    "final/activity_toxicity_evidence.json",
    "final/mechanism_evidence.json",
    "final/mechanism_ontology_record.json",
    "final/review_report.json",
    "work/review/quality_feedback.json",
    "source/paper.xml",
    "source/paper.pdf",
]


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


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_rel(path: Path | str) -> str:
    text = str(path)
    try:
        p = Path(text)
    except TypeError:
        return text
    try:
        return str(p.resolve().relative_to(ROOT))
    except (ValueError, RuntimeError, OSError):
        return text


def line_count(path: Path, limit: int = 2_000_000) -> int | None:
    try:
        if not path.is_file() or path.stat().st_size > limit:
            return None
        with path.open("rb") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return None


def dir_stats(path: Path, sample_limit: int = 12, scan_limit: int = 250) -> dict[str, Any]:
    file_count = 0
    total_bytes = 0
    sample_paths: list[str] = []
    truncated = False
    try:
        for child in path.rglob("*"):
            if child.is_file():
                file_count += 1
                try:
                    total_bytes += child.stat().st_size
                except OSError:
                    pass
                if len(sample_paths) < sample_limit:
                    sample_paths.append(safe_rel(child))
                if file_count >= scan_limit:
                    truncated = True
                    break
    except OSError:
        pass
    return {
        "file_count_sampled": file_count,
        "total_bytes_sampled": total_bytes,
        "scan_limit": scan_limit,
        "scan_truncated": truncated,
        "sample_paths": sample_paths,
    }


def path_info(path: Path, *, scan_dirs: bool = True) -> dict[str, Any]:
    info: dict[str, Any] = {"path": safe_rel(path), "exists": path.exists()}
    if not path.exists():
        return info
    try:
        stat = path.stat()
        info["mtime"] = datetime.fromtimestamp(stat.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError:
        pass
    if path.is_file():
        info.update({"kind": "file", "bytes": path.stat().st_size})
        count = line_count(path)
        if count is not None:
            info["line_count"] = count
    elif path.is_dir():
        info["kind"] = "directory"
        if scan_dirs:
            info.update(dir_stats(path))
        else:
            info["dir_scan_skipped"] = True
    else:
        info["kind"] = "other"
    return info


def read_json_if_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = load_json(path)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def count_jsonl(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    count = 0
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.strip():
                count += 1
    return count


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


def final_records(final_data: dict[str, Any]) -> list[dict[str, Any]]:
    records = final_data.get("record_audits") or final_data.get("records") or []
    return [record for record in records if isinstance(record, dict)]


def find_final_record(final_data: dict[str, Any], sample: dict[str, str]) -> dict[str, Any] | None:
    records = final_records(final_data)
    try:
        idx = int(sample.get("record_index", "0")) - 1
    except ValueError:
        idx = -1
    wanted = sample.get("source_id", "").split(":")[-1]
    status = sample.get("status", "")
    if 0 <= idx < len(records):
        record = records[idx]
        source_id = str(record.get("source_id") or record.get("sequence_key") or "")
        record_status = str(record.get("status") or record.get("layer1_status") or "")
        if wanted and (wanted in source_id or source_id.split(":")[-1] in wanted):
            if not status or not record_status or status == record_status:
                return record
    for record in records:
        source_id = str(record.get("source_id") or record.get("sequence_key") or "")
        record_status = str(record.get("status") or record.get("layer1_status") or "")
        if wanted and (wanted in source_id or source_id.split(":")[-1] in wanted):
            if not status or not record_status or status == record_status:
                return record
    return None


def decode_jsonish(value: str) -> Any:
    if not value:
        return ""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def source_locator_hints(release_row: dict[str, str]) -> dict[str, Any]:
    keys = [
        "source_locator",
        "traceability",
        "citation_traceability",
        "sequence_check",
        "modification_check",
        "source_organism_check",
        "activity_check",
        "conflict_flags",
        "conflict_context",
        "conflict_interpretation",
        "review_notes",
    ]
    return {key: decode_jsonish(release_row.get(key, "")) for key in keys if release_row.get(key, "")}


def compact_jsonish(value: Any, limit: int = 8000) -> Any:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if len(text) <= limit:
        return value
    return {"_truncated": True, "json_prefix": text[:limit]}


def build_inventory(paper_id: str) -> dict[str, Any]:
    packet_dir = ROOT / "paper_packets" / paper_id
    paper_dir = ROOT / "papers" / paper_id
    packet_manifest = read_json_if_object(packet_dir / "packet_manifest.json")
    review_report = read_json_if_object(paper_dir / "final" / "review_report.json")
    extraction_status = read_json_if_object(packet_dir / "extraction" / "extraction_status.json")
    analysis_status = read_json_if_object(packet_dir / "analysis" / "analysis_status.json")

    packet_files = {rel: path_info(packet_dir / rel) for rel in STANDARD_PACKET_PATHS}
    paper_files = {rel: path_info(paper_dir / rel) for rel in STANDARD_PAPER_PATHS}
    rework_request_count = count_jsonl(packet_dir / "rework" / "rework_requests.jsonl")
    rework_response_count = count_jsonl(packet_dir / "rework" / "rework_responses.jsonl")
    extraction_error_count = count_jsonl(packet_dir / "extraction" / "extraction_errors.jsonl")

    source_roots = []
    for item in packet_manifest.get("source_roots", []) if isinstance(packet_manifest.get("source_roots", []), list) else []:
        source_roots.append(path_info(Path(str(item)), scan_dirs=False))

    raw_files = {}
    if isinstance(packet_manifest.get("raw_files"), dict):
        raw_files = {key: path_info(Path(str(value))) for key, value in packet_manifest["raw_files"].items()}

    review_summary = {}
    if review_report:
        source_depth = review_report.get("source_review_depth") or {}
        if isinstance(source_depth, dict):
            source_depth_keys: list[str] = sorted(source_depth.keys())
        elif isinstance(source_depth, list):
            source_depth_keys = [str(item) for item in source_depth[:20]]
        else:
            source_depth_keys = [str(source_depth)]
        review_summary = {
            "review_status": review_report.get("review_status"),
            "publication_grade": review_report.get("publication_grade"),
            "validator_contract_passed": review_report.get("validator_contract_passed"),
            "source_reviewed": review_report.get("source_reviewed"),
            "reviewed_at": review_report.get("reviewed_at"),
            "review_model": review_report.get("review_model"),
            "reasoning_effort": review_report.get("reasoning_effort"),
            "source_review_depth_keys": source_depth_keys,
            "checked_input_count": len(review_report.get("checked_inputs") or []),
            "rework_target_count": len(review_report.get("rework_targets") or []),
            "caution_finding_count": len(review_report.get("caution_findings") or []),
        }

    known_risks = []
    material_status = packet_manifest.get("material_queue_status") or extraction_status.get("status")
    analysis_queue_status = packet_manifest.get("analysis_queue_status") or analysis_status.get("status")
    if material_status and "gaps" in str(material_status):
        known_risks.append("material_queue_status_contains_gaps")
    if packet_manifest.get("test_scope"):
        known_risks.append("packet_manifest_has_test_scope_note")
    if rework_request_count:
        known_risks.append("packet_rework_requests_present")
    if (paper_dir / "work" / "review" / "quality_feedback.json").exists():
        known_risks.append("paper_quality_feedback_present")
    if review_summary.get("review_model") != "gpt-5.5" or review_summary.get("reasoning_effort") != "xhigh":
        known_risks.append("review_model_or_reasoning_not_strict")

    return {
        "paper_id": paper_id,
        "packet_dir": safe_rel(packet_dir),
        "paper_dir": safe_rel(paper_dir),
        "packet_manifest_summary": {
            "exists": bool(packet_manifest),
            "packet_version": packet_manifest.get("packet_version"),
            "material_queue_status": material_status,
            "analysis_queue_status": analysis_queue_status,
            "known_missing_or_blocked_materials": packet_manifest.get("known_missing_or_blocked_materials", []),
            "open_rework_ticket_ids": packet_manifest.get("open_rework_ticket_ids", []),
            "resolved_rework_ticket_ids": packet_manifest.get("resolved_rework_ticket_ids", []),
            "test_scope": packet_manifest.get("test_scope"),
            "title": packet_manifest.get("title"),
            "doi": packet_manifest.get("doi"),
            "pmid": packet_manifest.get("pmid"),
            "pmcid": packet_manifest.get("pmcid"),
            "year": packet_manifest.get("year"),
            "journal": packet_manifest.get("journal"),
        },
        "review_report_summary": review_summary,
        "counts": {
            "rework_request_count": rework_request_count,
            "rework_response_count": rework_response_count,
            "extraction_error_count": extraction_error_count,
        },
        "source_roots": source_roots,
        "raw_files_from_packet_manifest": raw_files,
        "packet_paths": packet_files,
        "paper_paths": paper_files,
        "known_risks_for_reviewer": known_risks,
    }


def owner_worker_hint(sample: dict[str, str]) -> dict[str, Any]:
    categories = set(filter(None, sample.get("difference_categories", "").split(";")))
    status = sample.get("status", "")
    owners = ["worker-4/database_record_auditor"]
    if categories & {"activity_value_or_unit", "target_or_organism", "row_granularity"}:
        owners.append("worker-2/main_text_assay_extractor")
    if "mechanism_or_claim_scope" in categories:
        owners.append("worker-5/mechanism_ontology_extractor")
    if status in {"database_only_no_primary_source", "unresolved_record"}:
        owners.append("worker-1/material_intake_linkage")
        owners.append("worker-3/supplementary_methods_extractor")
    owners.append("worker-6/adjudicator_review")
    return {
        "primary_owner": owners[0],
        "owner_lanes_to_consult": list(dict.fromkeys(owners)),
        "status_specific_focus": status,
        "difference_categories": sorted(categories),
    }


def prompt_text(
    *,
    packet_dir: Path,
    sample: dict[str, str],
    release_row: dict[str, str],
    inventory: dict[str, Any],
    output_schema_path: Path,
) -> str:
    rel_packet = safe_rel(packet_dir)
    result_path = packet_dir / "true_review_result.json"
    ticket_path = packet_dir / "rework_ticket.json"
    sample_path = packet_dir / "validation_sample.json"
    release_path = packet_dir / "release_row.json"
    final_record_path = packet_dir / "sample_final_record.json"
    inventory_path = packet_dir / "material_inventory.json"
    locator_path = packet_dir / "source_locator_hints.json"
    owner_hint = owner_worker_hint(sample)
    raw_status = inventory["packet_manifest_summary"].get("material_queue_status")
    analysis_status = inventory["packet_manifest_summary"].get("analysis_queue_status")
    review_status = inventory["review_report_summary"].get("review_status")
    publication_grade = inventory["review_report_summary"].get("publication_grade")
    return f"""# Pilot20 True Source Review Prompt

You are a fresh Codex CLI reviewer for AMP Evidence Atlas / NAR Resource v1.
This is a true source-review packet, not the previous automated structural pass.

## Required model/provenance

- Use `gpt-5.5` with `model_reasoning_effort=xhigh`.
- Record `review_model: "gpt-5.5"` and `reasoning_effort: "xhigh"` in the result.
- The launch command uses `codex exec -m gpt-5.5 -c model_reasoning_effort="xhigh"`;
  that runner command is sufficient model/effort provenance for this review
  unless a Codex header or runtime status contradicts it. Do not downgrade
  solely because the model cannot introspect itself.

## Working directory

`/root/work/抗菌肽/数据库/batch/4-team`

## Packet

- packet directory: `{rel_packet}`
- validation sample: `{safe_rel(sample_path)}`
- release row: `{safe_rel(release_path)}`
- sample final record: `{safe_rel(final_record_path)}`
- source locator hints: `{safe_rel(locator_path)}`
- material inventory: `{safe_rel(inventory_path)}`
- result schema: `{safe_rel(output_schema_path)}`
- write final result to: `{safe_rel(result_path)}`
- if hard failure, write rework ticket to: `{safe_rel(ticket_path)}`

## Sample identity

- pilot_sample_id: `{sample.get('pilot_sample_id', '')}`
- paper_id: `{sample.get('paper_id', '')}`
- database/source_id: `{sample.get('database', '')} / {sample.get('source_id', '')}`
- audit_record_id: `{sample.get('audit_record_id', '')}`
- status under review: `{sample.get('status', '')}`
- categories: `{sample.get('difference_categories', '')}`
- owner lanes: `{', '.join(owner_hint['owner_lanes_to_consult'])}`

Current packet signals to verify, not trust blindly:

- material_queue_status: `{raw_status}`
- analysis_queue_status: `{analysis_status}`
- existing final review_status: `{review_status}`
- existing publication_grade: `{publication_grade}`
- known risks: `{'; '.join(inventory.get('known_risks_for_reviewer', [])) or 'none listed'}`

## Skills/instructions to read before reviewing

Read these local files yourself before making a terminal decision:

1. `.codex/skills/amp-three-layer-curation/SKILL.md`
2. `.codex/skills/amp-three-layer-curation/references/publication-grade-source-review.md`
3. `.codex/skills/amp-three-layer-curation/references/publication-grade-quality-gate.md`
4. `.codex/skills/amp-three-layer-curation/references/team-rework-message-contract.md`
5. `.codex/skills/amp-three-layer-curation/references/two-queue-paper-packet-contract.md`
6. `.codex/skills/paper-adjudicator-review-worker/SKILL.md`
7. If the owner lane is worker-4, read `.codex/skills/paper-database-record-auditor/SKILL.md`.
8. If the owner lane includes worker-2/3/5, read the corresponding worker skill under `.codex/skills/`.

## Review task

Perform a best-effort source review for this one sampled audit row and its
paper-level final artifacts. Use only local materials; do not browse the web.

Do all of the following:

1. Re-open `{safe_rel(inventory_path)}` and verify which XML/PDF/OA/supplement/database-row surfaces actually exist.
2. Re-open the packet sources referenced by source locators, especially XML tables/sections, PDF text, supplementary index/tables/text, and database JSONL rows.
3. Verify the sampled release row against `sample_final_record.json` and the primary material.
4. For layer 1, decide whether the status `{sample.get('status', '')}` is justified. Do not turn conflicts into clean source_verified.
5. For layer 2, spot-check whether activity/toxicity values, units, endpoint, target species/strain, and locators are source-backed when relevant to this row.
6. For layer 3, check whether mechanism claims stay in the correct evidence class and direct mechanisms have direct assay types and locators.
7. Act as worker-6 for this sample: decide whether the existing final artifact can be confirmed, must be cautioned, needs targeted rework, is blocked by missing primary material, or is only best-effort unverifiable.

## Decision rules

Use exactly one `decision` value:

- `pass_source_review`: sampled row and relevant layers are source-backed; no blocking cautions remain for this sample.
- `accepted_with_cautions_confirmed`: no hard repair is needed, but source conflict, database-only, unresolved, material-gap, or non-clean caution remains and must be preserved.
- `needs_targeted_rework`: a repairable worker-owned defect exists. Write `rework_targets`.
- `blocked_missing_primary_material`: source/supplement/raw material required for this sample is absent or unreadable after best effort.
- `unverifiable_best_effort`: you made a bounded best effort but cannot decide; explain what was inspected and why it remains unresolved. Do not loop indefinitely.

Hard failures requiring `needs_targeted_rework` include:

- `source_verified` without primary-source locator support.
- unresolved/database-only status without a source-backed reason or material-gap evidence.
- activity rows with sentence-fragment target/species, generic endpoint, missing raw value, missing raw unit for MIC-like rows, or missing locator.
- mechanism claims without claim_id, claim_text, evidence_class, locator, or direct assay type for direct mechanisms.
- templated worker-6 review, missing reviewed_at/model/reasoning provenance, or open rework targets.
- copied/fallback artifacts accepted without fresh source-review evidence.

## Output requirements

Write `{safe_rel(result_path)}` as JSON matching `{safe_rel(output_schema_path)}`.

If `decision` is `needs_targeted_rework` or `blocked_missing_primary_material`, also write `{safe_rel(ticket_path)}` with:

- `ticket_id`
- `paper_id`
- `audit_record_id`
- `target_queue`: one of `material_extraction`, `analysis`, `adjudication`
- `severity`: `blocking`, `major`, `minor`, or `caution`
- `requested_by`: `pilot20_true_source_review`
- `reason`
- `requested_outputs`
- `blocks`
- `created_at`

Keep evidence concise: cite paths and locators; do not copy long source text.
If exact source text is needed, quote only short snippets and prefer locator IDs.

Final chat response should be brief and point to the JSON result path.
"""


def run_script_text(packet_index: Path) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
cd {ROOT}
python scripts/run_pilot20_true_source_reviews.py \\
  --packet-index {safe_rel(packet_index)} \\
  --parallel 4
"""


def single_run_script_text(prompt_path: Path, last_message_path: Path) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
cd {ROOT}
codex exec \\
  -C {ROOT} \\
  --skip-git-repo-check \\
  --add-dir {ROOT} \\
  --add-dir {MERGED_CORPUS_ROOT} \\
  -m gpt-5.5 \\
  -c 'model_reasoning_effort="xhigh"' \\
  -c 'approval_policy="never"' \\
  -o {last_message_path} \\
  - < {prompt_path}
"""


def build_packet(sample: dict[str, str], pilot_result: dict[str, str], release_row: dict[str, str], out_root: Path, run_id: str, force: bool) -> dict[str, Any]:
    packet_name = f"{sample['pilot_sample_id']}__{sample['paper_id']}"
    packet_dir = out_root / packet_name
    if packet_dir.exists() and force:
        shutil.rmtree(packet_dir)
    packet_dir.mkdir(parents=True, exist_ok=True)

    final_path = ROOT / sample["final_artifact_path"]
    final_data = read_json_if_object(final_path)
    final_record = find_final_record(final_data, sample) if final_data else None
    inventory = build_inventory(sample["paper_id"])
    owner_hint = owner_worker_hint(sample)

    sample_payload = {**sample, "pilot_structural_result": pilot_result}
    source_hints = source_locator_hints(release_row)
    packet_manifest = {
        "packet_schema": "pilot20_true_source_review_packet_v1",
        "generated_at": now_utc(),
        "run_id": run_id,
        "paper_id": sample["paper_id"],
        "pilot_sample_id": sample["pilot_sample_id"],
        "audit_record_id": sample["audit_record_id"],
        "database": sample["database"],
        "source_id": sample["source_id"],
        "status_under_review": sample["status"],
        "primary_validation_category": sample.get("primary_validation_category", ""),
        "difference_categories": sample.get("difference_categories", ""),
        "owner_worker_hint": owner_hint,
        "inputs": {
            "pilot_manifest": safe_rel(PILOT_MANIFEST),
            "pilot_results": safe_rel(PILOT_RESULTS),
            "release_table": safe_rel(RELEASE_TABLE),
            "original_final_artifact_path": sample.get("final_artifact_path", ""),
            "paper_packet_dir": f"paper_packets/{sample['paper_id']}",
            "paper_dir": f"papers/{sample['paper_id']}",
        },
        "outputs_expected": {
            "true_review_result": safe_rel(packet_dir / "true_review_result.json"),
            "rework_ticket": safe_rel(packet_dir / "rework_ticket.json"),
            "codex_last_message": safe_rel(packet_dir / "CODEX_LAST_MESSAGE.md"),
        },
        "completion_claim": "source_review_packet_ready_not_scientific_acceptance",
    }

    write_json(packet_dir / "packet_manifest.json", packet_manifest)
    write_json(packet_dir / "validation_sample.json", sample_payload)
    write_json(packet_dir / "release_row.json", release_row)
    write_json(packet_dir / "source_locator_hints.json", source_hints)
    write_json(packet_dir / "sample_final_record.json", compact_jsonish(final_record or {}))
    write_json(packet_dir / "material_inventory.json", inventory)
    write_json(packet_dir / "true_review_result.schema.json", RESULT_SCHEMA)

    prompt = prompt_text(
        packet_dir=packet_dir,
        sample=sample,
        release_row=release_row,
        inventory=inventory,
        output_schema_path=packet_dir / "true_review_result.schema.json",
    )
    (packet_dir / "CODEX_REVIEW_PROMPT.md").write_text(prompt, encoding="utf-8")
    run_one = single_run_script_text(packet_dir / "CODEX_REVIEW_PROMPT.md", packet_dir / "CODEX_LAST_MESSAGE.md")
    run_one_path = packet_dir / "run_codex_review.sh"
    run_one_path.write_text(run_one, encoding="utf-8")
    os.chmod(run_one_path, 0o755)

    return {
        "pilot_sample_id": sample["pilot_sample_id"],
        "sample_id": sample.get("sample_id", ""),
        "paper_id": sample["paper_id"],
        "database": sample.get("database", ""),
        "source_id": sample.get("source_id", ""),
        "audit_record_id": sample.get("audit_record_id", ""),
        "status": sample.get("status", ""),
        "primary_validation_category": sample.get("primary_validation_category", ""),
        "difference_categories": sample.get("difference_categories", ""),
        "packet_dir": safe_rel(packet_dir),
        "prompt_path": safe_rel(packet_dir / "CODEX_REVIEW_PROMPT.md"),
        "result_path": safe_rel(packet_dir / "true_review_result.json"),
        "rework_ticket_path": safe_rel(packet_dir / "rework_ticket.json"),
        "run_script_path": safe_rel(run_one_path),
        "material_queue_status": inventory["packet_manifest_summary"].get("material_queue_status") or "",
        "analysis_queue_status": inventory["packet_manifest_summary"].get("analysis_queue_status") or "",
        "existing_review_status": inventory["review_report_summary"].get("review_status") or "",
        "existing_publication_grade": str(inventory["review_report_summary"].get("publication_grade", "")),
        "known_risk_count": len(inventory.get("known_risks_for_reviewer", [])),
        "known_risks": ";".join(inventory.get("known_risks_for_reviewer", [])),
        "ready_for_codex_review": str(bool(release_row) and bool(final_record)).lower(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-manifest", type=Path, default=PILOT_MANIFEST)
    parser.add_argument("--pilot-results", type=Path, default=PILOT_RESULTS)
    parser.add_argument("--outdir", type=Path, default=OUTDIR)
    parser.add_argument("--force", action="store_true", help="Remove existing packet directories before rebuilding.")
    args = parser.parse_args()

    pilot_rows = read_csv(args.pilot_manifest)
    pilot_results = {row["audit_record_id"]: row for row in read_csv(args.pilot_results)}
    release_rows = load_release_rows({row["audit_record_id"] for row in pilot_rows})
    if len(pilot_rows) != 20:
        raise RuntimeError(f"expected 20 pilot rows, got {len(pilot_rows)}")
    missing_release = sorted({row["audit_record_id"] for row in pilot_rows} - set(release_rows))
    if missing_release:
        raise RuntimeError(f"missing release rows for {len(missing_release)} audit ids: {missing_release[:3]}")

    run_id = stamp()
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / ".generated_by_generate_pilot20_true_review_packets").write_text(now_utc() + "\n", encoding="utf-8")

    index_rows = []
    for sample in pilot_rows:
        index_rows.append(
            build_packet(
                sample=sample,
                pilot_result=pilot_results.get(sample["audit_record_id"], {}),
                release_row=release_rows[sample["audit_record_id"]],
                out_root=args.outdir,
                run_id=run_id,
                force=args.force,
            )
        )

    fields = [
        "pilot_sample_id",
        "sample_id",
        "paper_id",
        "database",
        "source_id",
        "audit_record_id",
        "status",
        "primary_validation_category",
        "difference_categories",
        "packet_dir",
        "prompt_path",
        "result_path",
        "rework_ticket_path",
        "run_script_path",
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

    summary = {
        "generated_at": now_utc(),
        "run_id": run_id,
        "completion_claim": "pilot20_true_source_review_packets_ready_not_review_completed",
        "packet_root": safe_rel(args.outdir),
        "packet_count": len(index_rows),
        "ready_for_codex_review_count": sum(1 for row in index_rows if row["ready_for_codex_review"] == "true"),
        "status_counts": dict(Counter(row["status"] for row in index_rows)),
        "database_counts": dict(Counter(row["database"] for row in index_rows)),
        "known_risk_counts": dict(Counter(risk for row in index_rows for risk in row["known_risks"].split(";") if risk)),
        "outputs": {
            "packet_index_csv": safe_rel(index_path),
            "latest_packet_index_csv": safe_rel(latest_index),
            "run_all_script": safe_rel(args.outdir / "run_true_source_reviews_20.sh"),
        },
    }
    summary_path = args.outdir / f"packet_summary_{run_id}.json"
    write_json(summary_path, summary)
    shutil.copyfile(summary_path, args.outdir / "packet_summary_latest.json")
    write_json(args.outdir / "true_review_result.schema.json", RESULT_SCHEMA)

    readme_lines = [
        "# Pilot20 True Source-Review Packets",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "These packets are inputs for fresh Codex CLI source-review runs. They do not prove scientific acceptance by themselves.",
        "",
        "## Run all 20 with 4-way concurrency",
        "",
        "```bash",
        f"bash {safe_rel(args.outdir / 'run_true_source_reviews_20.sh')}",
        "```",
        "",
        "## Run one packet manually",
        "",
        "```bash",
        "bash reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/PILOT20-001__*/run_codex_review.sh",
        "```",
        "",
        "Each reviewer must write `true_review_result.json`; hard failures also write `rework_ticket.json`.",
        "",
    ]
    (args.outdir / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")

    run_all = run_script_text(latest_index)
    run_all_path = args.outdir / "run_true_source_reviews_20.sh"
    run_all_path.write_text(run_all, encoding="utf-8")
    os.chmod(run_all_path, 0o755)

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
