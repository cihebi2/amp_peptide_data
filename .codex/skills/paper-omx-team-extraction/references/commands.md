# Commands

Run these from repo root: `/root/work/抗菌肽/数据库`.

## Launch one paper team

```bash
python workspace-guide/team-paper-sample/launch_paper_team_v2.py \
  --paper-id <PMC...> \
  --source-pool-root DBAASP/analysis/runtime/oa_100paper_batch_20260407_round3/source_pool
```

## Build a manifest

```bash
python workspace-guide/team-paper-sample/paper_batch_v1.py manifest \
  --limit 10 \
  --output workspace-guide/team-paper-sample/batch-v1/<manifest-name>.json
```

Use strict worker review when needed:

```bash
python workspace-guide/team-paper-sample/paper_batch_v1.py manifest \
  --limit 10 \
  --strict-worker-review \
  --output workspace-guide/team-paper-sample/batch-v1/<manifest-name>.json
```

## Run the batch controller

One reconciliation cycle:

```bash
python workspace-guide/team-paper-sample/paper_batch_controller.py once \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
```

Loop mode:

```bash
python workspace-guide/team-paper-sample/paper_batch_controller.py loop \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl \
  --interval-seconds 15
```

## Inspect a team

```bash
omx team status audit-real-paper-<pmcid-lower>-w --json
```

Useful repo-local checks:

```bash
ls -lah papers/<PMC...>/final
find .omx/state/team/audit-real-paper-<pmcid-lower>-w -maxdepth 3 -type f | sort
```

## Re-run one worker lane

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-1
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-2
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-3
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-4
```

Typical use:

- `worker-1`: rebuild intake and `final/materials_manifest.json`
- `worker-2`: rebuild `body_evidence` and `table_evidence`
- `worker-3`: rebuild `supp_evidence`
- `worker-4`: rebuild merge/review and `final/`

After any repair, advance the controller once:

```bash
python workspace-guide/team-paper-sample/paper_batch_controller.py once \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
```

## Validate final JSON syntax quickly

```bash
python -m json.tool papers/<PMC...>/final/materials_manifest.json >/dev/null
python -m json.tool papers/<PMC...>/final/mechanism_record.json >/dev/null
python -m json.tool papers/<PMC...>/final/vc_projection.json >/dev/null
python -m json.tool papers/<PMC...>/final/review_report.json >/dev/null
```
