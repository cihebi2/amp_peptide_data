#!/usr/bin/env python3
"""Run the complete real-material message-transfer test on 10 landed papers."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LANDED_ROOT = Path('/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets')
PREFERRED = [
    'doi__10.1002_cmdc.201900465',
    'doi__10.1002_advs.202205301',
    'doi__10.1002_advs.202401793',
    'doi__10.1002_cbic.202100609',
    'doi__10.1002_cbic.202100151',
    'doi__10.1002_cbic.202400586',
    'doi__10.1002_cmdc.201600498',
    'doi__10.1002_cmdc.202200291',
    'doi__10.1002_gch2.202200213',
    'doi__10.1002_anie.201901589',
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def candidate_papers(limit: int) -> list[str]:
    papers_root = LANDED_ROOT / 'papers'
    selected: list[str] = []
    for pid in PREFERRED:
        p = papers_root / pid
        if p.exists() and list((p / 'xml').glob('*.xml')) and list((p / 'pdf').glob('*.pdf')):
            selected.append(pid)
    if len(selected) >= limit:
        return selected[:limit]
    for p in sorted(pp for pp in papers_root.iterdir() if pp.is_dir()):
        if p.name in selected:
            continue
        if (p / 'metadata.json').exists() and list((p / 'xml').glob('*.xml')) and list((p / 'pdf').glob('*.pdf')):
            selected.append(p.name)
            if len(selected) >= limit:
                break
    return selected


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()
    repo = Path.cwd()
    paper_ids = candidate_papers(args.limit)
    if len(paper_ids) < args.limit:
        raise SystemExit(f'only found {len(paper_ids)} eligible papers')
    results = []
    failures = []
    for idx, pid in enumerate(paper_ids, start=1):
        cmd = [sys.executable, 'scripts/run_one_paper_complete_message_test.py', '--paper-id', pid]
        if args.reset:
            cmd.append('--reset')
        print(f'[{idx}/{len(paper_ids)}] running {pid}', flush=True)
        proc = subprocess.run(cmd, cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        report_path = repo / 'reports' / f'{pid}.complete_message_test_report.json'
        if proc.returncode != 0:
            failures.append({'paper_id': pid, 'returncode': proc.returncode, 'stdout_tail': proc.stdout[-2000:], 'stderr_tail': proc.stderr[-2000:]})
            continue
        try:
            report = read_json(report_path)
            results.append(report)
        except Exception as exc:
            failures.append({'paper_id': pid, 'returncode': proc.returncode, 'error': str(exc), 'stdout_tail': proc.stdout[-2000:], 'stderr_tail': proc.stderr[-2000:]})
    summary = {
        'ok': not failures,
        'generated_at': now_iso(),
        'test_type': 'ten_paper_real_material_message_transfer_batch',
        'completion_claim': 'message_transfer_workflow_exercised_not_publication_grade_review',
        'requested_limit': args.limit,
        'paper_count': len(results),
        'failure_count': len(failures),
        'paper_ids': paper_ids,
        'terminal_status_counts': {},
        'total_material': {
            'sections': 0,
            'tables': 0,
            'figures': 0,
            'archive_members': 0,
            'supplementary_assets': 0,
            'supplementary_tables': 0,
            'locators': 0,
        },
        'total_analysis': {
            'activity_records': 0,
            'mechanism_claims': 0,
        },
        'gate_counts': {
            'packet_hard_finding_papers': 0,
            'semantic_pass_papers': 0,
            'semantic_fail_papers': 0,
            'publication_quality_pass_papers': 0,
        },
        'rework_counts': {
            'open_rework_tickets': 0,
            'papers_with_open_rework': 0,
            'final_approval_refused_papers': 0,
            'rework_queue_papers': 0,
        },
        'results': results,
        'failures': failures,
    }
    for report in results:
        status = report.get('terminal_status', 'unknown')
        summary['terminal_status_counts'][status] = summary['terminal_status_counts'].get(status, 0) + 1
        for key in summary['total_material']:
            summary['total_material'][key] += int((report.get('material') or {}).get(key) or 0)
        for key in summary['total_analysis']:
            summary['total_analysis'][key] += int((report.get('analysis') or {}).get(key) or 0)
        gates = report.get('gate_results') or {}
        if int(gates.get('packet_hard_finding_count') or 0) > 0:
            summary['gate_counts']['packet_hard_finding_papers'] += 1
        if int(gates.get('semantic_publication_grade_pass_count') or 0) > 0:
            summary['gate_counts']['semantic_pass_papers'] += 1
        if int(gates.get('semantic_publication_grade_fail_count') or 0) > 0:
            summary['gate_counts']['semantic_fail_papers'] += 1
        if gates.get('publication_quality_pass') is True:
            summary['gate_counts']['publication_quality_pass_papers'] += 1
        open_rework = int(report.get('open_rework_ticket_count') or 0)
        summary['rework_counts']['open_rework_tickets'] += open_rework
        if open_rework:
            summary['rework_counts']['papers_with_open_rework'] += 1
        if report.get('final_approval_status') == 'refused_needs_rework':
            summary['rework_counts']['final_approval_refused_papers'] += 1
        if report.get('current_state') == 'rework_queue':
            summary['rework_counts']['rework_queue_papers'] += 1
    out = repo / 'reports' / f'ten_paper_message_transfer_test_{now_iso().replace(":", "").replace("-", "")}.json'
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    latest = repo / 'reports' / 'ten_paper_message_transfer_test_latest.json'
    latest.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({
        'ok': not failures,
        'summary_path': str(out),
        'latest_path': str(latest),
        'paper_count': len(results),
        'failure_count': len(failures),
        'terminal_status_counts': summary['terminal_status_counts'],
        'gate_counts': summary['gate_counts'],
        'rework_counts': summary['rework_counts'],
        'total_material': summary['total_material'],
        'total_analysis': summary['total_analysis'],
    }, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
