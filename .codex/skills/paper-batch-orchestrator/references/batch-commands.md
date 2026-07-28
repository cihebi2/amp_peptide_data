# Batch Commands

Run from repo root: `/root/work/抗菌肽/数据库`.

## Create a manifest

Basic:

```bash
python workspace-guide/team-paper-sample/paper_batch_v1.py manifest \
  --limit 10 \
  --output workspace-guide/team-paper-sample/batch-v1/<manifest>.json
```

Strict worker review:

```bash
python workspace-guide/team-paper-sample/paper_batch_v1.py manifest \
  --limit 10 \
  --strict-worker-review \
  --output workspace-guide/team-paper-sample/batch-v1/<manifest>.json
```

## Controller reconciliation

Single pass:

```bash
python workspace-guide/team-paper-sample/paper_batch_controller.py once \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
```

Continuous loop:

```bash
python workspace-guide/team-paper-sample/paper_batch_controller.py loop \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl \
  --interval-seconds 15
```

## Batch-level inspection

Inspect issue log frequency:

```bash
python - <<'PY'
from pathlib import Path
import json
from collections import Counter
p=Path('workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl')
rows=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
print(Counter(r.get('issue_type') for r in rows).most_common(20))
PY
```

Inspect completion over a manifest:

```bash
python - <<'PY'
from pathlib import Path
import importlib.util, json
spec=importlib.util.spec_from_file_location('pbc','workspace-guide/team-paper-sample/paper_batch_controller.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
root=Path('.')
manifest=json.loads(Path('workspace-guide/team-paper-sample/batch-v1/<manifest>.json').read_text(encoding='utf-8'))
problems=[]
for pid in manifest['paper_ids']:
    structural=mod.final_artifacts_structurally_ready(root,pid)
    ready=mod.final_artifacts_ready(root,pid)
    issues=mod.final_artifacts_quality_issues(root,pid) if structural else ['not_structurally_ready']
    if (not structural) or (not ready) or issues:
        problems.append({'paper_id': pid, 'structural': structural, 'ready': ready, 'issues': issues})
print(json.dumps({'total': len(manifest['paper_ids']), 'problem_count': len(problems), 'problems': problems}, ensure_ascii=False, indent=2))
PY
```

Check active team sessions:

```bash
tmux list-sessions -F '#{session_name}' 2>/dev/null | rg '^omx-team-' || true
```

## Existing batch artifacts to reuse

Look under:

- `workspace-guide/team-paper-sample/batch-v1/*.json`
- `workspace-guide/team-paper-sample/batch-v1/*.jsonl`
- `workspace-guide/team-paper-sample/batch-v1/*.md`

These often already contain manifests, audits, aggregate views, and prior verification notes.

## Skill helper scripts

Fresh batch validation:

```bash
python .codex/skills/paper-batch-orchestrator/scripts/verify_batch.py \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json
```

Locator coverage summary:

```bash
python .codex/skills/paper-batch-orchestrator/scripts/check_locator_coverage.py \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json
```

Issue-log summary:

```bash
python .codex/skills/paper-batch-orchestrator/scripts/summarize_issue_log.py \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
```
