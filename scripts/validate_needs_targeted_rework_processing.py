#!/usr/bin/env python3
"""Validate needs_targeted_rework triage/resolution artifacts."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reports'/'nar_resource_freeze_v1'
WORK=BASE/'needs_targeted_rework_work'

def fail(msg:str)->None:
    print('FAIL '+msg, file=sys.stderr)
    raise SystemExit(1)

def load_json(path:Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        fail(f'cannot parse {path}: {e}')

def main()->None:
    triage_csv=BASE/'needs_targeted_rework_triage_latest.csv'
    if not triage_csv.exists(): fail(f'missing {triage_csv}')
    rows=list(csv.DictReader(triage_csv.open(encoding='utf-8', newline='')))
    classes=Counter(r['triage_class'] for r in rows)
    if any(r['publication_grade']!='False' for r in rows): fail('all needs_targeted_rework rows must remain publication_grade=False')
    if any(r.get('review_status')!='needs_targeted_rework' for r in rows): fail('all rows must be needs_targeted_rework')
    res=load_json(WORK/'summary_latest.json')
    summary=res['summary']
    if summary['needs_targeted_rework_count']!=len(rows):
        fail(f"summary count {summary['needs_targeted_rework_count']} != triage rows {len(rows)}")
    if dict(classes)!=summary.get('triage_class_counts'):
        fail(f"triage class counts mismatch csv={dict(classes)} summary={summary.get('triage_class_counts')}")
    if summary['status_change_applied_count']!=0: fail('status_change_applied_count must be 0')
    owner=list(csv.DictReader((WORK/'owner_worker_rework_queue_latest.csv').open(encoding='utf-8', newline='')))
    backlog=list(csv.DictReader((WORK/'material_or_digitization_backlog_latest.csv').open(encoding='utf-8', newline='')))
    if len(owner)!=summary['owner_worker_rework_queue_count']:
        fail(f"owner queue csv rows {len(owner)} != summary {summary['owner_worker_rework_queue_count']}")
    if len(backlog)!=summary['new_material_or_digitization_queue_count']:
        fail(f"backlog csv rows {len(backlog)} != summary {summary['new_material_or_digitization_queue_count']}")
    if len(owner)+len(backlog)!=len(rows):
        fail('owner queue + material/digitization backlog must equal triage rows')
    context_build=load_json(WORK/'context_build_latest.json')
    if context_build.get('count') != len(owner) or context_build.get('failed'):
        fail(f"context build must cover current owner queue ({len(owner)}) with zero failures")
    lane_manifest=load_json(WORK/'owner_worker_rework_manifest_latest.json')
    if lane_manifest.get('paper_count') != len(owner) or lane_manifest.get('lane_count') != 5:
        fail(f"owner-worker lane manifest must contain current owner queue ({len(owner)}) across 5 lanes")
    lane_counts=[int(lane.get('paper_count') or 0) for lane in lane_manifest.get('lanes', [])]
    if sum(lane_counts)!=len(owner):
        fail(f'owner-worker lane counts {lane_counts} do not sum to owner queue {len(owner)}')
    lane_ids=[
        paper_id
        for lane in lane_manifest.get('lanes', [])
        for paper_id in (lane.get('paper_ids') or [])
    ]
    owner_ids=[row['paper_id'] for row in owner]
    if sorted(lane_ids)!=sorted(owner_ids):
        fail('owner-worker lane manifest paper_ids must match owner queue csv')
    for row in owner:
        prompt_dir=ROOT/'rework_context'/row['paper_id']
        prompt=prompt_dir/'CODEX_REVIEW_PROMPT.md'
        policy_prompt=prompt_dir/'CODEX_REVIEW_PROMPT_POLICY_SAFE.md'
        if not prompt.exists() and not policy_prompt.exists():
            fail(f"missing CODEX_REVIEW_PROMPT or CODEX_REVIEW_PROMPT_POLICY_SAFE for {row['paper_id']}")
    release=load_json(BASE/'unified_scope_summary_latest.json')
    if release['review_status_counts'].get('needs_targeted_rework')!=len(rows):
        fail('release needs_targeted_rework count must match current triage rows')
    manifest=load_json(BASE/'release_manifest_latest.json')
    outputs=manifest.get('outputs', {})
    required=['needs_rework_triage_csv','needs_rework_triage_json','needs_rework_triage_md','needs_rework_resolution_summary_json','needs_rework_resolution_summary_md','needs_rework_owner_queue_csv','needs_rework_material_backlog_csv','needs_rework_context_build_json','needs_rework_owner_lane_manifest_json']
    missing=[x for x in required if x not in outputs]
    if missing: fail(f'manifest missing outputs {missing}')
    print(json.dumps({'ok':True,'triage_rows':len(rows),'class_counts':dict(classes),'owner_worker_rework_queue_count':len(owner),'new_material_or_digitization_queue_count':len(backlog),'lane_counts':lane_counts,'status_change_applied_count':summary['status_change_applied_count']}, ensure_ascii=False, indent=2))

if __name__=='__main__': main()
