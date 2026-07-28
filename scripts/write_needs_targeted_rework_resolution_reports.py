#!/usr/bin/env python3
"""Write resolution plan artifacts for needs_targeted_rework papers.

This does not promote papers to publication-grade. It closes the release-level
triage by separating papers that need new material/digitization from papers that
can enter owner-worker activity/database/adjudication rework.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'reports' / 'nar_resource_freeze_v1'
WORK = BASE / 'needs_targeted_rework_work'
TRIAGE = BASE / 'needs_targeted_rework_triage_latest.csv'

QUEUE_POLICY = {
    'material_or_exact_value_unrecoverable': ('backlog_requires_new_source_or_digitization', False),
    'figure_exact_value_or_digitization_needed': ('digitization_or_backlog', False),
    'missing_supplement_or_unparsed_table': ('source_staging_required', False),
    'activity_extraction_missing_or_unparsed': ('owner_worker_rework_queue', True),
    'early_framework_full_review_incomplete': ('owner_worker_rework_queue', True),
    'material_repaired_ready_for_owner_rework': ('owner_worker_rework_queue_after_material_repair', True),
    'material_repaired_text_only_ready_for_owner_rework': ('owner_worker_rework_queue_after_text_material_repair', True),
    'analysis_rework_from_current_packet': ('owner_worker_rework_queue', True),
    'manual_triage_required': ('owner_worker_review_required', True),
}


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with TRIAGE.open(encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh))
    decisions=[]
    for row in rows:
        queue, can_rework_now = QUEUE_POLICY.get(row['triage_class'], ('owner_worker_review_required', True))
        status_change_applied = False
        if can_rework_now:
            decision = 'queued_for_owner_worker_rework_not_accepted'
            next_action = 'Build/reuse rework context and run worker-2 activity extraction plus worker-4/6 adjudication before changing publication_grade.'
        else:
            decision = 'kept_non_publication_grade_until_new_material'
            next_action = row['recommended_next_action']
        decisions.append({
            'paper_id': row['paper_id'],
            'triage_class': row['triage_class'],
            'target_queue': row['target_queue'],
            'resolution_queue': queue,
            'can_rework_from_current_packet': can_rework_now,
            'resolution_decision': decision,
            'status_change_applied': status_change_applied,
            'activity_records': int(row['activity_records'] or 0),
            'database_audit_records': int(row['database_audit_records'] or 0),
            'packet_material_staging_status': row.get('packet_material_staging_status', ''),
            'packet_material_staging_generated_at': row.get('packet_material_staging_generated_at', ''),
            'packet_material_staged_asset_count': row.get('packet_material_staged_asset_count', ''),
            'packet_material_staged_text_record_count': row.get('packet_material_staged_text_record_count', ''),
            'packet_material_staged_table_count': row.get('packet_material_staged_table_count', ''),
            'bounded_rework_result_updated_at': row.get('bounded_rework_result_updated_at', ''),
            'material_staging_newer_than_bounded_rework': row.get('material_staging_newer_than_bounded_rework', ''),
            'failure_codes': row['failure_codes'],
            'recommended_next_action': next_action,
            'review_report': row['review_report'],
            'quality_feedback': row['quality_feedback'],
        })
    by_class = Counter(d['triage_class'] for d in decisions)
    by_resolution = Counter(d['resolution_queue'] for d in decisions)
    owner_queue = [d for d in decisions if d['can_rework_from_current_packet']]
    material_queue = [d for d in decisions if not d['can_rework_from_current_packet']]
    summary={
        'generated_at': generated_at,
        'needs_targeted_rework_count': len(decisions),
        'status_change_applied_count': sum(1 for d in decisions if d['status_change_applied']),
        'owner_worker_rework_queue_count': len(owner_queue),
        'new_material_or_digitization_queue_count': len(material_queue),
        'triage_class_counts': dict(by_class),
        'resolution_queue_counts': dict(by_resolution),
        'outputs': {
            'summary_json': 'reports/nar_resource_freeze_v1/needs_targeted_rework_work/summary_latest.json',
            'summary_md': 'reports/nar_resource_freeze_v1/needs_targeted_rework_work/summary_latest.md',
            'owner_worker_queue_csv': 'reports/nar_resource_freeze_v1/needs_targeted_rework_work/owner_worker_rework_queue_latest.csv',
            'material_backlog_csv': 'reports/nar_resource_freeze_v1/needs_targeted_rework_work/material_or_digitization_backlog_latest.csv',
        }
    }
    (WORK/'summary_latest.json').write_text(json.dumps({'summary': summary, 'decisions': decisions}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    fields=list(decisions[0]) if decisions else []
    for path, subset in [(WORK/'owner_worker_rework_queue_latest.csv', owner_queue), (WORK/'material_or_digitization_backlog_latest.csv', material_queue)]:
        with path.open('w', encoding='utf-8', newline='') as fh:
            writer=csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader(); writer.writerows(subset)
    lines=['# Needs Targeted Rework Resolution Plan','',f"Generated at: `{generated_at}`",'', '## Decision', '', f"The {len(decisions)} papers remain non-publication-grade in the current freeze. This step does not promote any paper to accepted/public v1. It separates papers into an owner-worker rework queue versus source-staging/digitization backlog.", '', '| Metric | Count |', '| --- | ---: |', f"| needs_targeted_rework papers | {len(decisions)} |", f"| status changes applied | {summary['status_change_applied_count']} |", f"| owner-worker rework queue | {len(owner_queue)} |", f"| source/digitization backlog | {len(material_queue)} |", '', '## Resolution Queues', '', '| queue | count |', '| --- | ---: |']
    for q,c in sorted(by_resolution.items()):
        lines.append(f"| `{q}` | {c} |")
    lines.extend(['', '## Owner-worker rework queue', '', 'These papers have current-packet rework potential, mainly worker-2 activity extraction followed by worker-4/6 adjudication. They are not accepted until re-reviewed.', '', '| paper_id | class | activity | db rows |', '| --- | --- | ---: | ---: |'])
    for d in owner_queue:
        lines.append(f"| `{d['paper_id']}` | `{d['triage_class']}` | {d['activity_records']} | {d['database_audit_records']} |")
    lines.extend(['', '## Source/digitization backlog', '', '| paper_id | class | required action |', '| --- | --- | --- |'])
    for d in material_queue:
        lines.append(f"| `{d['paper_id']}` | `{d['triage_class']}` | {d['recommended_next_action']} |")
    (WORK/'summary_latest.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
