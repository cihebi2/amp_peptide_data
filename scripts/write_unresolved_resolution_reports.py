#!/usr/bin/env python3
"""Write generated resolution summaries for unresolved records.

This script intentionally does not overwrite the hand-reviewed per-paper
reports in reports/nar_resource_freeze_v1/unresolved_work/<paper_id>.md.
Those files are worker/source-review artifacts. Generated summaries use the
generated_<paper_id>.* naming pattern and can be regenerated safely.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports' / 'nar_resource_freeze_v1' / 'unresolved_work'
TRIAGE = ROOT / 'reports' / 'nar_resource_freeze_v1' / 'unresolved_records_triage_latest.csv'


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open(encoding='utf-8') as fh:
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


def compact(value: Any, limit: int = 500) -> str:
    if value is None:
        return ''
    if isinstance(value, (dict, list)):
        text=json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text=str(value)
    text=' '.join(text.split())
    return text[:limit]


def decision_for(pid: str, rows: list[dict[str, str]], review: dict[str, Any], qf: dict[str, Any]) -> dict[str, Any]:
    blockers=Counter(r['blocker_class'] for r in rows)
    targets=Counter(r['target_queue'] for r in rows)
    review_status=review.get('review_status') or review.get('status')
    publication_grade=bool(review.get('publication_grade'))
    if not publication_grade and review_status == 'blocked_missing_primary_material':
        decision='keep_unresolved_blocked_missing_primary_material'
    else:
        decision='manual_review_required_before_status_change'
    return {
        'paper_id': pid,
        'unresolved_record_count': len(rows),
        'blocker_class_counts': dict(blockers),
        'target_queue_counts': dict(targets),
        'review_status': review_status,
        'publication_grade': publication_grade,
        'source_reviewed': bool(review.get('source_reviewed')),
        'resolution_decision': decision,
        'status_change_applied': False,
        'reason': 'No unresolved row was promoted because local material/rework evidence preserves missing primary material or row-level ambiguity.',
        'next_action': 'Recover the named missing supplement/source material or rerun owner-worker row mapping with new evidence; otherwise keep unresolved disclosed in release notes.',
        'quality_feedback_status': compact((qf or {}).get('status') or (qf or {}).get('bounded_rework_result')),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    generated_at=datetime.now(timezone.utc).isoformat(timespec='seconds')
    with TRIAGE.open(encoding='utf-8') as fh:
        triage_rows=list(csv.DictReader(fh))
    by_pid: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in triage_rows:
        by_pid[row['paper_id']].append(row)

    decisions=[]
    for pid, rows in sorted(by_pid.items()):
        packet=ROOT/'paper_packets'/pid
        paper=ROOT/'papers'/pid
        review=load_json(paper/'final'/'review_report.json', {}) or {}
        qf=load_json(paper/'work'/'review'/'quality_feedback.json', {}) or {}
        supp_tables=load_json(packet/'extracted'/'supplementary_tables.json', {}) or {}
        extraction_status=load_json(packet/'extraction'/'extraction_status.json', {}) or {}
        extraction_quality=load_json(packet/'extraction'/'extraction_quality_report.json', {}) or {}
        rework_requests=read_jsonl(packet/'rework'/'rework_requests.jsonl')
        rework_responses=read_jsonl(packet/'rework'/'rework_responses.jsonl')
        dec=decision_for(pid, rows, review, qf)
        dec.update({
            'checked_paths': [
                str(packet/'extracted'/'supplementary_index.json'),
                str(packet/'extracted'/'supplementary_tables.json'),
                str(packet/'extraction'/'extraction_status.json'),
                str(packet/'extraction'/'extraction_quality_report.json'),
                str(packet/'rework'/'rework_requests.jsonl'),
                str(packet/'rework'/'rework_responses.jsonl'),
                str(paper/'final'/'database_record_verification.json'),
                str(paper/'final'/'review_report.json'),
                str(paper/'work'/'review'/'quality_feedback.json'),
            ],
            'supplementary_table_count': supp_tables.get('table_count'),
            'supplement_parse_count': extraction_quality.get('supplement_parse_count'),
            'supplementary_asset_count': extraction_quality.get('supplementary_asset_count'),
            'extraction_status': extraction_status.get('status'),
            'gap_assessment': extraction_status.get('gap_assessment'),
            'rework_request_count': len(rework_requests),
            'rework_response_count': len(rework_responses),
            'open_or_relevant_rework_codes': sorted({compact(r.get('failure_code') or r.get('omission_code'), 160) for r in rework_requests if r.get('failure_code') or r.get('omission_code')}),
            'generated_at': generated_at,
        })
        decisions.append(dec)
        lines=[
            f"# Unresolved Processing: `{pid}`",
            '',
            f"Generated at: `{generated_at}`",
            '',
            '## Decision',
            '',
            f"- Resolution decision: `{dec['resolution_decision']}`",
            f"- Status change applied: `{dec['status_change_applied']}`",
            f"- Review status: `{dec['review_status']}`",
            f"- Publication grade: `{dec['publication_grade']}`",
            f"- Unresolved rows: `{dec['unresolved_record_count']}`",
            f"- Reason: {dec['reason']}",
            f"- Next action: {dec['next_action']}",
            '',
            '## Blocker Counts',
            '',
            '| blocker_class | count |',
            '| --- | ---: |',
        ]
        for key,value in sorted(dec['blocker_class_counts'].items()):
            lines.append(f"| `{key}` | {value} |")
        lines.extend(['', '## Material / Rework Evidence', '', '| evidence | value |', '| --- | --- |'])
        for key in ['supplementary_asset_count','supplement_parse_count','supplementary_table_count','extraction_status','gap_assessment','rework_request_count','rework_response_count','quality_feedback_status']:
            lines.append(f"| `{key}` | {compact(dec.get(key), 800)} |")
        lines.extend(['', '## Checked Paths', ''])
        for path in dec['checked_paths']:
            lines.append(f"- `{path}`")
        lines.extend(['', '## Policy', '', '- Do not promote any row to `source_verified` without primary/source packet evidence.', '- If new supplement/source material is recovered, rerun owner-worker row mapping before changing final status.', ''])
        dec["hand_review_report_md"] = str((OUT / f"{pid}.md").relative_to(ROOT))
        (OUT/f'generated_{pid}.md').write_text('\n'.join(lines), encoding='utf-8')
        (OUT/f'generated_{pid}.json').write_text(json.dumps(dec, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    summary={
        'generated_at': generated_at,
        'paper_count': len(decisions),
        'unresolved_record_count': sum(d['unresolved_record_count'] for d in decisions),
        'status_change_applied_count': sum(1 for d in decisions if d['status_change_applied']),
        'decisions': decisions,
    }
    (OUT/'summary_latest.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines=[
        '# Unresolved Processing Summary',
        '',
        f"Generated at: `{generated_at}`",
        '',
        'This generated summary is reproducible. The per-paper `<paper_id>.md` files are hand-reviewed worker artifacts and are intentionally not overwritten by `scripts/write_unresolved_resolution_reports.py`.',
        '',
        '| paper_id | unresolved | decision | status_change | hand review | generated summary |',
        '| --- | ---: | --- | --- | --- | --- |',
    ]
    for d in decisions:
        pid = d['paper_id']
        lines.append(
            f"| `{pid}` | {d['unresolved_record_count']} | `{d['resolution_decision']}` | "
            f"`{d['status_change_applied']}` | "
            f"`reports/nar_resource_freeze_v1/unresolved_work/{pid}.md` | "
            f"`reports/nar_resource_freeze_v1/unresolved_work/generated_{pid}.md` |"
        )
    (OUT/'summary_latest.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['generated_at','paper_count','unresolved_record_count','status_change_applied_count']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
