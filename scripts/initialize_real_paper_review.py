#!/usr/bin/env python3
"""Initialize a real landed-assets paper for the local Miaobi message workflow."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LANDED_ROOT = Path('/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets')
DEFAULT_PAPER_ID = 'doi__10.1002_advs.202205301'


def safe_dir_name(paper_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._=-]+", "_", paper_id.strip())
    return cleaned.strip("._") or "paper"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def first_file(paths: list[Path]) -> Path | None:
    return sorted(paths)[0] if paths else None


def safe_symlink(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        if dst.is_symlink() and Path(os.readlink(dst)) == src:
            return
        dst.unlink()
    os.symlink(src, dst)


def choose_paper(landed_root: Path, requested: str | None) -> Path:
    papers = landed_root / 'papers'
    if requested:
        paper = papers / requested
        if not paper.exists():
            raise SystemExit(f'paper not found: {paper}')
        return paper
    preferred = papers / DEFAULT_PAPER_ID
    if preferred.exists():
        return preferred
    for paper in sorted(p for p in papers.iterdir() if p.is_dir()):
        if (paper / 'metadata.json').exists() and list((paper / 'xml').glob('*')) and list((paper / 'pdf').glob('*')):
            return paper
    raise SystemExit(f'no landed paper with metadata/xml/pdf under {papers}')


def build_packet(repo_root: Path, paper_dir: Path) -> dict[str, Any]:
    metadata = read_json(paper_dir / 'metadata.json')
    paper_id = paper_dir.name
    packet_root = repo_root / 'paper_packets' / paper_id
    raw = packet_root / 'raw'
    xml = first_file(list((paper_dir / 'xml').glob('*.xml')))
    pdf = first_file(list((paper_dir / 'pdf').glob('*.pdf')))
    packages = sorted((paper_dir / 'package').glob('*')) if (paper_dir / 'package').exists() else []
    supps = sorted([p for p in (paper_dir / 'supplementary').rglob('*') if p.is_file()]) if (paper_dir / 'supplementary').exists() else []

    if xml:
        safe_symlink(xml, raw / 'paper.xml')
    if pdf:
        safe_symlink(pdf, raw / 'paper.pdf')
    for src in packages:
        safe_symlink(src, raw / 'oa_package' / src.name)
    for src in supps:
        safe_symlink(src, raw / 'supplementary_original' / src.name)

    packet_root.joinpath('locators').mkdir(parents=True, exist_ok=True)
    packet_root.joinpath('extraction').mkdir(parents=True, exist_ok=True)
    packet_root.joinpath('database').mkdir(parents=True, exist_ok=True)
    packet_root.joinpath('analysis').mkdir(parents=True, exist_ok=True)
    packet_root.joinpath('final').mkdir(parents=True, exist_ok=True)
    packet_root.joinpath('rework').mkdir(parents=True, exist_ok=True)

    raw_files = {}
    if xml:
        raw_files['paper_xml'] = str(raw / 'paper.xml')
    if pdf:
        raw_files['paper_pdf'] = str(raw / 'paper.pdf')
    if packages:
        raw_files['oa_package'] = str(raw / 'oa_package')
    if supps:
        raw_files['supplementary_original'] = str(raw / 'supplementary_original')

    locator_index = {
        'paper_id': paper_id,
        'created_at': now_iso(),
        'locator_policy': 'initial real-paper smoke test locator index; downstream workers must replace with section/table/row locators',
        'raw_sources': [
            {'kind': 'xml', 'locator': 'raw:paper.xml', 'path': raw_files.get('paper_xml', '')},
            {'kind': 'pdf', 'locator': 'raw:paper.pdf', 'path': raw_files.get('paper_pdf', '')},
        ] + [
            {'kind': 'oa_package', 'locator': f'raw:oa_package:{p.name}', 'path': str(raw / 'oa_package' / p.name)} for p in packages
        ] + [
            {'kind': 'supplementary', 'locator': f'raw:supplementary_original:{p.name}', 'path': str(raw / 'supplementary_original' / p.name)} for p in supps
        ],
    }
    (packet_root / 'locators' / 'locator_index.json').write_text(json.dumps(locator_index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    extraction_status = {
        'paper_id': paper_id,
        'status': 'material_queued',
        'created_at': now_iso(),
        'source_inventory': {
            'xml_files': 1 if xml else 0,
            'pdf_files': 1 if pdf else 0,
            'oa_package_files': len(packages),
            'supplementary_files': len(supps),
        },
        'note': 'Real landed-assets smoke test initialized; extraction is queued, not publication-grade reviewed.',
    }
    (packet_root / 'extraction' / 'extraction_status.json').write_text(json.dumps(extraction_status, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for name in ['rework_requests.jsonl', 'rework_responses.jsonl']:
        (packet_root / 'rework' / name).touch()

    manifest = {
        'paper_id': paper_id,
        'doi': metadata.get('canonical_doi', ''),
        'pmid': metadata.get('canonical_pmid', ''),
        'pmcid': metadata.get('canonical_pmcid', ''),
        'title': metadata.get('title', ''),
        'journal': metadata.get('journal', ''),
        'year': metadata.get('year', ''),
        'packet_version': 'v001-real-smoke',
        'updated_at': now_iso(),
        'material_queue_status': 'material_queued',
        'analysis_queue_status': 'analysis_queued',
        'source_roots': [str(paper_dir), str(LANDED_ROOT)],
        'raw_files': raw_files,
        'database_snapshot_inputs': {
            'source_databases': metadata.get('source_databases', ''),
            'landed_metadata': str(paper_dir / 'metadata.json'),
            'asset_manifest': str(paper_dir / 'asset_manifest.csv'),
        },
        'locator_index_path': str(packet_root / 'locators' / 'locator_index.json'),
        'open_rework_ticket_ids': [],
        'known_missing_or_blocked_materials': [],
        'test_scope': 'message-transfer real-paper smoke test; not a scientific acceptance claim',
    }
    (packet_root / 'packet_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'paper_id': paper_id, 'packet_root': str(packet_root), 'metadata': metadata, 'manifest': manifest}


def run_bridge(repo_root: Path, *args: str) -> None:
    cmd = [sys.executable, str(repo_root / 'scripts' / 'miaobi_message_bridge.py'), *args]
    subprocess.run(cmd, cwd=repo_root, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--landed-root', default=str(LANDED_ROOT))
    parser.add_argument('--paper-id', help='landed paper folder name; defaults to a stable real paper if present')
    args = parser.parse_args()

    repo_root = Path.cwd()
    landed_root = Path(args.landed_root)
    paper_dir = choose_paper(landed_root, args.paper_id)
    result = build_packet(repo_root, paper_dir)
    paper_id = result['paper_id']
    packet_root = result['packet_root']
    title = result['metadata'].get('title', '')
    doi = result['metadata'].get('canonical_doi', '')

    workflow_dir = repo_root / '.miaobi-paper-review' / 'workflows' / safe_dir_name(paper_id)
    if not (workflow_dir / 'workflow_context.json').exists():
        run_bridge(repo_root, 'init-paper', '--paper-id', paper_id, '--packet-root', packet_root, '--title', title, '--doi', doi)
    else:
        print(workflow_dir)

    run_bridge(
        repo_root,
        'record-state',
        '--paper-id', paper_id,
        '--state', 'select_paper',
        '--role', 'material_worker',
        '--provider', 'codex-cli',
        '--model', 'gpt-5.5',
        '--reasoning-effort', 'xhigh',
        '--status', 'completed',
        '--output-summary', f'Selected real landed paper {paper_id} from {paper_dir}',
        '--artifact', f'packet_manifest={packet_root}/packet_manifest.json',
        '--artifact', f'locator_index={packet_root}/locators/locator_index.json',
        '--artifact-status', 'created',
        '--chat', f'Real-paper smoke test selected {paper_id}; packet initialized from landed assets.',
    )
    run_bridge(
        repo_root,
        'record-state',
        '--paper-id', paper_id,
        '--state', 'material_intake',
        '--role', 'material_worker',
        '--provider', 'codex-cli',
        '--model', 'gpt-5.5',
        '--reasoning-effort', 'xhigh',
        '--status', 'completed',
        '--set-status', 'material=material_extracting',
        '--output-summary', 'Staged real XML/PDF/OA package paths into packet manifest; no scientific acceptance claimed.',
        '--artifact', f'extraction_status={packet_root}/extraction/extraction_status.json',
        '--artifact-status', 'created',
        '--chat', 'material_intake completed for real paper; extraction remains queued for source review.',
    )
    run_bridge(
        repo_root,
        'add-log',
        '--paper-id', paper_id,
        '--state', 'material_intake',
        '--level', 'info',
        '--category', 'real-paper-smoke-test',
        '--message', 'Initialized from landed_assets with real metadata and symlinked source files.',
        '--path-ref', str(paper_dir),
        '--path-ref', f'{packet_root}/packet_manifest.json',
    )
    run_bridge(repo_root, 'validate', '--paper-id', paper_id)

    print(json.dumps({
        'paper_id': paper_id,
        'title': title,
        'doi': doi,
        'packet_root': packet_root,
        'workflow_dir': str(workflow_dir),
        'message': 'initialized real-paper workflow smoke test',
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
