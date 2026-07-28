#!/usr/bin/env python3
"""Triage papers with review_status=needs_targeted_rework for freeze cleanup."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "reports" / "nar_resource_freeze_v1"
PAPER_SCOPE = BASE / "paper_scope_latest.csv"
OUT_CSV = BASE / "needs_targeted_rework_triage_latest.csv"
OUT_JSON = BASE / "needs_targeted_rework_triage_latest.json"
OUT_MD = BASE / "needs_targeted_rework_triage_latest.md"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows=[]
    with path.open(encoding='utf-8') as fh:
        for line in fh:
            line=line.strip()
            if not line:
                continue
            try:
                value=json.loads(line)
            except Exception:
                continue
            if isinstance(value, dict):
                rows.append(value)
    return rows


def compact(value: Any, limit: int = 1000) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value)
    text = " ".join(text.split())
    return text[:limit]


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def staging_newer_than_bounded(staging: dict[str, Any], bounded: dict[str, Any]) -> bool:
    candidate_times = [parse_timestamp(staging.get("material_change_at") or staging.get("generated_at"))]
    if to_int(staging.get("locator_index_repair_count")) > 0:
        candidate_times.append(parse_timestamp(staging.get("locator_index_repair_at")))
    staged_at = max((value for value in candidate_times if value is not None), default=None)
    bounded_at = parse_timestamp(bounded.get("updated_at"))
    return staged_at is not None and bounded_at is not None and staged_at > bounded_at


def to_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def codes_from(items: Any) -> list[str]:
    codes=[]
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                code=item.get('code') or item.get('failure_code') or item.get('omission_code')
                if code:
                    codes.append(str(code))
    return codes


def target_queue_counts(*sources: Any) -> Counter[str]:
    counts: Counter[str] = Counter()
    for source in sources:
        if isinstance(source, list):
            for item in source:
                if isinstance(item, dict) and item.get('target_queue'):
                    counts[str(item['target_queue'])] += 1
    return counts


def classify(row: dict[str, str], review: dict[str, Any], qf: dict[str, Any], rework_requests: list[dict[str, Any]], staging: dict[str, Any]) -> tuple[str, str, str]:
    queues=target_queue_counts(review.get('rework_targets'), qf.get('rework_targets'), rework_requests)
    text = " ".join([
        compact(review.get('qc_failure_reasons'), 4000),
        compact(review.get('rework_targets'), 4000),
        compact(review.get('semantic_quality_checks'), 4000),
        compact(qf, 4000),
        compact(rework_requests, 4000),
    ]).lower()
    activity_count=to_int(row.get('activity_records'))
    bounded=qf.get('bounded_rework_result') if isinstance(qf.get('bounded_rework_result'), dict) else {}
    staging_status = str(staging.get('status') or '')
    staging_has_material = staging_status in {'material_staged', 'material_already_staged'}
    staging_is_new_material = staging_has_material and staging_newer_than_bounded(staging, bounded)
    staged_tables = to_int(staging.get('table_count_added_or_indexed'))
    staged_assets = to_int(staging.get('staged_asset_count'))
    if bounded.get('status') == 'blocked_after_best_effort':
        if staging_is_new_material and staged_tables > 0:
            return ('material_repaired_ready_for_owner_rework', 'owner_worker_review_after_material_repair', 'New supplementary/table material was staged after the previous blocked_after_best_effort result; run a fresh policy-safe owner-worker source review before any acceptance.')
        if staging_is_new_material and staged_assets > 0:
            return ('material_repaired_text_only_ready_for_owner_rework', 'owner_worker_review_after_text_material_repair', 'New text-only supplementary material was staged after the previous blocked_after_best_effort result; run a fresh source review to recover any obtainable facts, but do not assume table-level values.')
        if 'figure' in text and ('exact' in text or 'digitization' in text or 'image' in text or 'chart' in text):
            return ('figure_exact_value_or_digitization_needed', 'manual_digitization_or_keep_backlog', 'Owner-worker already exhausted the current packet; use validated manual digitization or keep conflict/unresolved.')
        if 'supplement' in text and ('missing' in text or 'absent' in text or 'not local' in text):
            return ('missing_supplement_or_unparsed_table', 'source_staging', 'Owner-worker already exhausted current material; recover and parse named supplement/table before another review.')
        return ('material_or_exact_value_unrecoverable', 'keep_non_publication_grade_backlog', 'Owner-worker already ran after material repair and strict gates remained blocked; preserve blocker until new source, digitization, or explicit curation policy changes.')
    if staging_status == 'material_staged' and staged_tables > 0:
        return ('material_repaired_ready_for_owner_rework', 'owner_worker_review_after_material_repair', 'Staged/parsed supplementary material is now present; build policy-safe rework context and run owner-worker source review before any acceptance.')
    if staging_status == 'material_staged' and staged_assets > 0:
        return ('material_repaired_text_only_ready_for_owner_rework', 'owner_worker_review_after_text_material_repair', 'Text-only supplementary material is now present; build policy-safe rework context and run owner-worker source review for obtainable facts before any acceptance.')

    if queues.get('analysis', 0) and not queues.get('material_extraction', 0) and (
        'activity_table_artifact_not_publication_grade' in text
        or 'mechanism_claims_pending_worker5_adjudication' in text
        or 'activity_extraction_requires_worker2_rework' in text
    ):
        return ('analysis_rework_from_current_packet', 'owner_worker_review', 'Packet already has source locators and analysis-owned tickets; build policy-safe owner-worker context and re-adjudicate.')
    if 'unrecoverable' in text or 'not locally recoverable' in text or 'local materials are exhausted' in text:
        return ('material_or_exact_value_unrecoverable', 'keep_non_publication_grade_backlog', 'Do not retry until new source/digitization material is staged; preserve blocker and release as excluded/backlog.')
    if 'figure' in text and ('exact' in text or 'digitization' in text or 'image' in text):
        return ('figure_exact_value_or_digitization_needed', 'manual_digitization_or_keep_backlog', 'Use validated manual digitization or keep conflict/unresolved; do not promote exact values from image-only evidence.')
    if 'supplement' in text and ('missing' in text or 'absent' in text or 'not local' in text):
        return ('missing_supplement_or_unparsed_table', 'source_staging', 'Recover and parse named supplement/table before owner-worker re-review.')
    if activity_count == 0 or 'no_supported_activity_rows_extracted' in text or 'activity_extraction_requires_worker2_rework' in text:
        return ('activity_extraction_missing_or_unparsed', 'worker2_activity_rework', 'Inspect XML/PDF/table/prose and extract source-located activity rows before adjudication.')
    if 'full_source_review_not_completed' in text or 'database_conflicts_require_adjudication' in text:
        return ('early_framework_full_review_incomplete', 'worker4_worker6_re_adjudication', 'Run owner-worker database reconciliation and final adjudication on existing packet before acceptance.')
    return ('manual_triage_required', 'owner_worker_review', 'Open a paper-specific rework context and preserve non-publication-grade until source-reviewed.')


def main() -> None:
    generated_at=datetime.now(timezone.utc).isoformat(timespec='seconds')
    with PAPER_SCOPE.open(encoding='utf-8', newline='') as fh:
        scope_rows=list(csv.DictReader(fh))
    target=[r for r in scope_rows if r.get('review_status')=='needs_targeted_rework']
    rows=[]
    for row in target:
        pid=row['paper_id']
        paper=ROOT/'papers'/pid
        packet=ROOT/'paper_packets'/pid
        review=load_json(paper/'final'/'review_report.json', {}) or {}
        qf=load_json(paper/'work'/'review'/'quality_feedback.json', {}) or {}
        staging=load_json(packet/'extraction'/'material_staging_status.json', {}) or {}
        rework_requests=read_jsonl(packet/'rework'/'rework_requests.jsonl')
        failure_codes=codes_from(review.get('qc_failure_reasons')) + codes_from(review.get('rework_targets')) + codes_from(qf.get('qc_failure_reasons')) + codes_from(qf.get('rework_targets'))
        rework_codes=[]
        for req in rework_requests:
            code=req.get('failure_code') or req.get('omission_code') or req.get('code')
            if code:
                rework_codes.append(str(code))
        cls, target_queue, next_action=classify(row, review, qf, rework_requests, staging)
        bounded=qf.get('bounded_rework_result') if isinstance(qf.get('bounded_rework_result'), dict) else {}
        rows.append({
            'paper_id': pid,
            'review_status': row['review_status'],
            'publication_grade': row['publication_grade'],
            'source_reviewed': row['source_reviewed'],
            'database_audit_records': row['database_audit_records'],
            'activity_records': row['activity_records'],
            'mechanism_claims': row['mechanism_claims'],
            'triage_class': cls,
            'target_queue': target_queue,
            'recommended_next_action': next_action,
            'failure_codes': ';'.join(sorted(set(failure_codes))),
            'rework_request_codes': ';'.join(sorted(set(rework_codes))),
            'rework_request_count': len(rework_requests),
            'packet_material_staging_status': staging.get('status', ''),
            'packet_material_staging_generated_at': staging.get('generated_at', ''),
            'packet_material_change_at': staging.get('material_change_at', ''),
            'packet_material_changed': str(bool(staging.get('material_changed'))).lower() if staging else '',
            'packet_locator_index_repair_at': staging.get('locator_index_repair_at', ''),
            'packet_locator_index_repair_count': staging.get('locator_index_repair_count', ''),
            'packet_material_staged_asset_count': staging.get('staged_asset_count', ''),
            'packet_material_staged_text_record_count': staging.get('text_record_count_added_or_indexed', ''),
            'packet_material_staged_table_count': staging.get('table_count_added_or_indexed', ''),
            'bounded_rework_result_status': bounded.get('status', ''),
            'bounded_rework_result_updated_at': bounded.get('updated_at', ''),
            'material_staging_newer_than_bounded_rework': str(staging_newer_than_bounded(staging, bounded)).lower(),
            'review_report': str((paper/'final'/'review_report.json').relative_to(ROOT)),
            'quality_feedback': str((paper/'work'/'review'/'quality_feedback.json').relative_to(ROOT)) if (paper/'work'/'review'/'quality_feedback.json').exists() else '',
        })
    fieldnames=list(rows[0]) if rows else []
    with OUT_CSV.open('w', encoding='utf-8', newline='') as fh:
        writer=csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(rows)
    summary={
        'generated_at': generated_at,
        'needs_targeted_rework_count': len(rows),
        'triage_class_counts': dict(Counter(r['triage_class'] for r in rows)),
        'target_queue_counts': dict(Counter(r['target_queue'] for r in rows)),
        'activity_zero_count': sum(1 for r in rows if int(r['activity_records'] or 0)==0),
        'outputs': {'csv': str(OUT_CSV.relative_to(ROOT)), 'json': str(OUT_JSON.relative_to(ROOT)), 'md': str(OUT_MD.relative_to(ROOT))},
    }
    OUT_JSON.write_text(json.dumps({'summary': summary, 'rows': rows}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines=['# Needs Targeted Rework Triage','',f"Generated at: `{generated_at}`",'', '| Metric | Count |', '| --- | ---: |', f"| needs_targeted_rework papers | {len(rows)} |", f"| zero activity rows | {summary['activity_zero_count']} |", '', '## By Class', '', '| triage_class | count | target_queue |', '| --- | ---: | --- |']
    for cls,count in sorted(summary['triage_class_counts'].items()):
        tq=next(r['target_queue'] for r in rows if r['triage_class']==cls)
        lines.append(f"| `{cls}` | {count} | `{tq}` |")
    lines.extend(['', '## Papers', '', '| paper_id | activity | db rows | class | next action |', '| --- | ---: | ---: | --- | --- |'])
    for r in rows:
        lines.append(f"| `{r['paper_id']}` | {r['activity_records']} | {r['database_audit_records']} | `{r['triage_class']}` | {r['recommended_next_action']} |")
    OUT_MD.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
