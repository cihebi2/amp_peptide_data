# Troubleshooting By Symptom

Use this reference when the paper extraction runtime is noisy and you need the shortest path from symptom to action.

## Symptom: team says stalled, but you are not sure it is real

Check in this order:

```bash
omx team status audit-real-paper-<pmcid-lower>-w --json
find .omx/state/team/audit-real-paper-<pmcid-lower>-w/tasks -maxdepth 1 -type f | sort
find .omx/state/team/audit-real-paper-<pmcid-lower>-w/mailbox -maxdepth 1 -type f | sort
ls -lah papers/<PMC...>/work papers/<PMC...>/final
```

Interpretation:

- if task JSON, mailbox, or artifacts are still changing, the stalled hint is probably stale noise
- if nothing changes and upstream artifacts are missing, inspect the blocked worker lane directly

## Symptom: worker-2 or worker-3 looks done, but task is still `in_progress`

Check the owned outputs first:

```bash
python -m json.tool papers/<PMC...>/work/body_evidence/evidence.json >/dev/null
python -m json.tool papers/<PMC...>/work/table_evidence/evidence.json >/dev/null
python -m json.tool papers/<PMC...>/work/supp_evidence/evidence.json >/dev/null
```

Then reconcile state:

```bash
python workspace-guide/team-paper-sample/paper_batch_controller.py once \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
```

Prefer controller reconciliation over hand-editing task files.

## Symptom: worker-4 is blocked forever

Check in order:

1. `.omx/state/team/<team>/tasks/task-4.json`
2. `papers/<PMC...>/work/review/quality_feedback.json` if it exists
3. upstream outputs from task 1/2/3
4. validator status for final files

Useful commands:

```bash
python -m json.tool papers/<PMC...>/final/materials_manifest.json >/dev/null
python -m json.tool papers/<PMC...>/final/mechanism_record.json >/dev/null
python -m json.tool papers/<PMC...>/final/vc_projection.json >/dev/null
python -m json.tool papers/<PMC...>/final/review_report.json >/dev/null
```

Do not force worker-4 if task 1/2/3 artifacts are still rejected.

## Symptom: supplementary says no local asset, but source has files

Check all three sources of truth:

```bash
find papers/<PMC...>/source/supplementary -maxdepth 2 -type f | sort
python -m json.tool papers/<PMC...>/work/supp_evidence/evidence.json | sed -n '1,220p'
python -m json.tool papers/<PMC...>/final/materials_manifest.json | sed -n '1,220p'
```

Recovery:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-3
python workspace-guide/team-paper-sample/paper_batch_controller.py once \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
```

Only rerun worker-4 after task-3 is corrected.

## Symptom: files exist, but quality gate still fails

Most common causes:

- `worker_deterministic_generated`
- `controller_fallback_generated`
- `source_direct_fallback`
- generic lead entity
- ad hoc final schema

Inspect:

```bash
python - <<'PY'
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('pbc','workspace-guide/team-paper-sample/paper_batch_controller.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
root=Path('.')
paper='<'+'PMC...'+'>'
print(mod.final_artifacts_structurally_ready(root, paper))
print(mod.final_artifacts_quality_issues(root, paper))
PY
```

Then repair the smallest upstream or final artifact needed instead of rerunning the whole paper.

## Symptom: one worker lane is clearly the blocker

Rerun only that lane:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-1
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-2
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-3
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-4
```

Then advance controller once.

## Symptom: many papers are reopening for similar reasons

Use the issue log and the extraction issues summary:

```bash
python -m json.tool workspace-guide/team-paper-sample/extraction-issues-20260423/issue-summary.json | sed -n '1,240p'
python - <<'PY'
from pathlib import Path
import json
from collections import Counter
p=Path('workspace-guide/team-paper-sample/batch-v1/issues_fresh50_strict_reaudit_excluding_final_ready_20260422.jsonl')
rows=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
print(Counter(r.get('issue_type') for r in rows).most_common(20))
PY
```

Use this when deciding whether you need a code fix instead of another one-off rescue.
