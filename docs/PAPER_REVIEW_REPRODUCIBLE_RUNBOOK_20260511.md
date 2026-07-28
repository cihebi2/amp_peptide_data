# Batch 4-Team 论文审查可复现运行手册

更新时间：2026-05-11
适用目录：`/root/work/抗菌肽/数据库/batch/4-team`

本手册记录当前 Batch 4-Team AMP 论文审查流程的完整复现方法：如何选择未审查文献、生成 manifest、启动 10 路队列、执行 bounded 打回、处理中断/infra retry、做收尾质量审计，并汇总结果。

重要原则：`accepted_after_rework` 是队列终态，不等于“整批 clean”。只有通过 full artifact audit、accepted sample audit、semantic gate、publication QA，且无 open rework ticket 的 accepted 集合，才能称为当前证据下闭环通过。blocked 论文必须保留 blocked 标签，不得用补齐统计的方式伪装为通过。

## 1. 运行环境

必须在项目根目录执行：

```bash
cd /root/work/抗菌肽/数据库/batch/4-team
```

当前生产队列使用的关键参数：

- 模型：`gpt-5.5`
- 推理强度：`xhigh`
- Codex worker 命令显式传入：`-c model_reasoning_effort="xhigh"`
- Fast：按当前配置为 opt-out；不要只从模型名推断 Fast 状态，应以 `/root/.codex/config.toml` 与 `codex exec` 实际命令为准
- watchdog：`--worker-timeout-seconds 1800`
- infra retry：`--worker-infra-retries 5`
- worker timeout 也可重试：`--retry-worker-timeouts`
- paper runtime retry：`--paper-runtime-retries 5`
- 打回上限：`--max-rework 5`
- 仅提取本地材料中能可靠获得的内容：`--obtainable-only`

确认配置：

```bash
rg -n 'model|model_reasoning_effort|fast_default_opt_out' /root/.codex/config.toml
rg -n 'model_reasoning_effort|codex exec|worker-timeout|worker-infra' scripts/run_true_rework_queue.py
codex exec --help | sed -n '1,120p'
```

当前关键脚本：

- `scripts/run_true_rework_queue.py`：核心队列控制器；一次初始化、最多 5 次打回、infra retry、严格 gate 后决定 accepted/blocked。
- `scripts/build_rework_context_packet.py`：构建每篇的 `rework_context/<paper_id>/CODEX_REVIEW_PROMPT.md`，交给新的 Codex CLI owner worker。
- `scripts/miaobi_message_bridge.py`：本地妙笔式消息总线；记录 workflow context、state、artifact、chat、log、rework ticket closure。
- `scripts/accepted_sample_audit.py`：accepted 样本二次审计；只验证，不提升论文状态。
- `.codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py`：三层语义 gate。
- `.codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py`：publication QA gate。

## 2. 队列状态语义

必须区分这些层级：

| 层级 | 含义 | 是否能声称 publication-grade clean |
| --- | --- | --- |
| `accepted_after_rework` | 队列控制器认为 bounded rework 后通过当前 gate | 不能单独声称 |
| `accepted_with_cautions` | worker-6 保留 caution 后通过 | 仅对该论文 accepted 集合可说通过 |
| full artifact audit `issue_count=0` | paper final、packet final、complete report、ticket 状态结构闭环 | 仍需 sample audit / gate |
| accepted sample audit `failed_count=0` | 抽查 accepted 集合无字段/ticket/gate 问题 | 仅证明抽查通过 |
| semantic gate pass | 三层语义 gate 通过 | 需结合 publication QA |
| publication QA pass | publication quality checker 无风险 | blocked 存在时整批仍为 false |
| `blocked_after_best_effort` | 本地材料、parser、infra 或打回上限仍阻断 | 不可提升为 accepted |
| `initial_queue_failed` | 初始化/材料 eligibility 问题 | 需修复初始化或剔除 |

常见 blocked 细分：

- `blocked_figure_chart_value_gap`：图/曲线精确值无法从本地材料安全恢复。
- `blocked_missing_external_supplement`：缺外部补充材料。
- `blocked_activity_table_extraction_gap`：activity/table 结构解析不安全。
- `blocked_rework_cap_unresolved`：5 次打回后仍无法通过。
- `blocked_watchdog_timeout_retryable`：watchdog 超时，可单独重试。
- `infrastructure_codex_worker_retry_exhausted`：Codex/API/worker 非零退出，5 次 infra retry 耗尽。

## 3. 检查是否有旧队列仍在运行

启动新队列前，必须确认没有旧 tmux 或 Codex worker 干扰：

```bash
date '+%F %T %Z'
tmux ls 2>/dev/null | rg 'n100_|next100_|true_rework|queue_next' || true
ps -eo pid,etime,args | rg '[r]un_true_rework_queue.py|[a]ccepted_sample_audit.py|[c]odex exec' || true
```

如果发现旧队列还在跑，先只做状态汇总，不要覆盖 latest 指针。

## 4. 严格选择未审查论文

材料来源：

```bash
SOURCE_POOL=/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers
```

严格 eligibility：

- `metadata.json` 存在
- primary `xml/*.xml` 存在
- primary `pdf/*.pdf` 存在
- 不使用 supplementary-only XML/PDF 凑数
- 不复用本目录已有 review 痕迹的 paper

已审查/已处理的排除信号：

- `paper_packets/<paper_id>/`
- `papers/<paper_id>/`
- `rework_context/<paper_id>/`
- `.miaobi-paper-review/workflows/<paper_id>/`
- `reports/*.json`、历史 manifest、lane summary、accepted sample audit 中出现过的 paper id

生成新 100 篇 / 10 lane manifest 的可复现命令如下。若严格 fresh pool 不足 100，必须记录 shortfall，不得用已审查或 supplementary-only 材料凑数。

```bash
python - <<'PY'
import json, re
from datetime import datetime, timezone
from pathlib import Path

repo = Path.cwd()
source = Path('/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers')
requested = 100
lane_count = 10
run_base = 'next100_10lane_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def safe_dir_name(paper_id: str) -> str:
    cleaned = re.sub(r'[^A-Za-z0-9._=-]+', '_', paper_id.strip())
    return cleaned.strip('._') or 'paper'

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}

source_dirs = [p for p in source.iterdir() if p.is_dir()]
eligible, weak = [], []
for p in sorted(source_dirs, key=lambda x: x.name):
    has_meta = (p / 'metadata.json').exists()
    has_primary_xml = bool(list((p / 'xml').glob('*.xml')))
    has_primary_pdf = bool(list((p / 'pdf').glob('*.pdf')))
    if has_meta and has_primary_xml and has_primary_pdf:
        eligible.append(p.name)
    elif has_meta and (bool(list(p.glob('**/*.xml'))) or bool(list(p.glob('**/*.pdf')))) and not (has_primary_xml and has_primary_pdf):
        weak.append(p.name)

sets = {}
sets['paper_packets_dirs'] = {p.name for p in (repo / 'paper_packets').iterdir() if p.is_dir()} if (repo / 'paper_packets').exists() else set()
sets['papers_dirs'] = {p.name for p in (repo / 'papers').iterdir() if p.is_dir()} if (repo / 'papers').exists() else set()
sets['rework_context_dirs'] = {p.name for p in (repo / 'rework_context').iterdir() if p.is_dir()} if (repo / 'rework_context').exists() else set()
wf = repo / '.miaobi-paper-review' / 'workflows'
sets['workflow_ids'] = {p.name for p in wf.iterdir() if p.is_dir()} if wf.exists() else set()

json_ids = set()
for p in (repo / 'reports').glob('*.json'):
    name = p.name
    if name.startswith(('doi__', 'pmid__')):
        pid = name.split('.complete_message_test_report.json')[0]
        pid = pid.split('.true_rework_queue_attempt_')[0]
        pid = pid.split('.semantic_gate.json')[0]
        pid = pid.split('.publication_quality.json')[0]
        if pid.startswith(('doi__', 'pmid__')):
            json_ids.add(pid)
    if 'true_rework_queue' in name or 'manifest' in name:
        d = read_json(p)
        if isinstance(d.get('paper_ids'), list):
            json_ids.update(str(x) for x in d['paper_ids'] if isinstance(x, str))
        if isinstance(d.get('results'), list):
            json_ids.update(str(x.get('paper_id')) for x in d['results'] if isinstance(x, dict) and x.get('paper_id'))
        if isinstance(d.get('papers'), list):
            for x in d['papers']:
                if isinstance(x, str):
                    json_ids.add(x)
                elif isinstance(x, dict) and x.get('paper_id'):
                    json_ids.add(str(x['paper_id']))
for p in (repo / 'reports' / 'accepted_sample_audit').glob('*.json'):
    d = read_json(p)
    for key in ('items', 'results'):
        if isinstance(d.get(key), list):
            json_ids.update(str(x.get('paper_id')) for x in d[key] if isinstance(x, dict) and x.get('paper_id'))
sets['json_reports_or_manifests'] = json_ids

excluded = set().union(*sets.values())
fresh = [pid for pid in eligible if pid not in excluded]
selected = fresh[:requested]
if not selected:
    raise SystemExit('no strict fresh eligible papers remain')

queue_contract = {
    'parallel_lanes': lane_count,
    'requested_paper_count': requested,
    'selected_count': len(selected),
    'model': 'gpt-5.5',
    'reasoning_effort': 'xhigh',
    'fast_default_opt_out_required': True,
    'max_rework': 5,
    'worker_timeout_seconds': 1800,
    'worker_infra_retries': 5,
    'retry_worker_timeouts': True,
    'paper_runtime_retries': 5,
    'obtainable_only': True,
    'acceptance_not_clean_by_default': True,
    'post_lane_required_gates': ['full_artifact_audit', 'packet_final_sync_check', 'accepted_sample_audit'],
}

base = {
    'generated_at': now(),
    'run_base': run_base,
    'requested_count': requested,
    'paper_count': len(selected),
    'selected_count': len(selected),
    'shortfall_count': max(0, requested - len(selected)),
    'shortfall_reason': None if len(selected) >= requested else 'strict_fresh_primary_xml_pdf_pool_exhausted; not padding with reviewed or supplementary-only material',
    'paper_ids': selected,
    'source_pool': str(source),
    'source_metadata_count': sum(1 for p in source_dirs if (p / 'metadata.json').exists()),
    'eligible_source_count': len(eligible),
    'weak_supplementary_only_xml_pdf_count': len(weak),
    'excluded_existing_count': len(excluded & set(eligible)),
    'fresh_available_before_selection': len(fresh),
    'selection_policy': 'first requested-count sorted landed papers with metadata + primary xml/*.xml + primary pdf/*.pdf, excluding local review artifacts; no padding from supplementary-only or already-reviewed papers',
    'strict_eligibility': 'metadata.json + primary xml/*.xml + primary pdf/*.pdf, matching run_one_paper_complete_message_test bootstrap',
    'exclusion_sources': {k: len(v & set(eligible)) for k, v in sets.items()},
    'queue_contract': queue_contract,
}

reports = repo / 'reports'
parent = reports / f'true_rework_queue_manifest_{run_base}.json'
parent.write_text(json.dumps(base, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
(reports / 'true_rework_queue_manifest_next100_10lane_latest.json').write_text(json.dumps(base, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')

n = len(selected)
start = 0
lanes = []
for lane in range(1, lane_count + 1):
    size = n // lane_count + (1 if lane <= n % lane_count else 0)
    ids = selected[start:start + size]
    start += size
    lane_doc = dict(base)
    lane_doc.update({
        'parent_manifest': str(parent),
        'lane': lane,
        'lane_count': lane_count,
        'run_label': f'{run_base}_lane{lane:02d}',
        'paper_count': len(ids),
        'paper_ids': ids,
    })
    lp = reports / f'true_rework_queue_manifest_{run_base}_lane{lane:02d}.json'
    lp.write_text(json.dumps(lane_doc, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    lanes.append({'lane': lane, 'manifest': str(lp), 'paper_count': len(ids), 'paper_ids': ids})

plan = {
    'generated_at': now(),
    'state': 'manifest_prepared_not_launched',
    'run_base': run_base,
    'requested_count': requested,
    'selected_count': len(selected),
    'shortfall_count': max(0, requested - len(selected)),
    'parent_manifest': str(parent),
    'lanes': lanes,
    'queue_contract': queue_contract,
}
plan_path = reports / f'true_rework_queue_{run_base}_launch_plan.json'
plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(json.dumps({'run_base': run_base, 'parent_manifest': str(parent), 'launch_plan': str(plan_path), 'selected_count': len(selected), 'shortfall_count': max(0, requested - len(selected)), 'lane_counts': [x['paper_count'] for x in lanes]}, ensure_ascii=False, indent=2))
PY
```

## 5. 启动 10 路 tmux 队列

把上一步输出的 `run_base` 写入变量：

```bash
RUN=<上一步输出的 run_base>
```

启动命令：

```bash
python - <<'PY'
import json, shlex, subprocess
from datetime import datetime, timezone
from pathlib import Path

repo = Path.cwd()
run = '<替换为 RUN>'
logs = repo / 'logs'
logs.mkdir(exist_ok=True)

def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

launches, errors = [], []
for lane in range(1, 11):
    manifest = repo / 'reports' / f'true_rework_queue_manifest_{run}_lane{lane:02d}.json'
    session = f'n100_{run.replace("next100_10lane_", "").replace("Z", "")}_l{lane:02d}'
    log = logs / f'{run}_lane{lane:02d}.log'
    cmd = [
        'python', 'scripts/run_true_rework_queue.py',
        '--manifest', str(manifest.relative_to(repo)),
        '--max-rework', '5',
        '--model', 'gpt-5.5',
        '--reasoning-effort', 'xhigh',
        '--sandbox', 'danger-full-access',
        '--codex-bypass-approvals-and-sandbox',
        '--worker-timeout-seconds', '1800',
        '--worker-infra-retries', '5',
        '--retry-worker-timeouts',
        '--paper-runtime-retries', '5',
        '--run-label', f'{run}_lane{lane:02d}',
        '--obtainable-only',
    ]
    shell_cmd = 'cd ' + shlex.quote(str(repo)) + ' && PYTHONUNBUFFERED=1 ' + ' '.join(shlex.quote(x) for x in cmd) + ' > ' + shlex.quote(str(log)) + ' 2>&1'
    proc = subprocess.run(['tmux', 'new-session', '-d', '-s', session, 'bash', '-lc', shell_cmd], text=True, capture_output=True)
    item = {'lane': lane, 'session': session, 'manifest': str(manifest.relative_to(repo)), 'log': str(log.relative_to(repo)), 'command': shell_cmd, 'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
    launches.append(item)
    if proc.returncode:
        errors.append(item)

active = subprocess.run(['bash', '-lc', f"tmux ls 2>/dev/null | rg '{run.replace('next100_10lane_', 'n100_').replace('Z', '')}|{run}' || true"], text=True, capture_output=True, cwd=repo).stdout.splitlines()
launch_report = {
    'generated_at': now(),
    'run_base': run,
    'state': 'launched_running' if len(active) == 10 and not errors else 'launch_partial_or_failed',
    'parent_manifest': f'reports/true_rework_queue_manifest_{run}.json',
    'lane_count': 10,
    'active_lane_sessions': len(active),
    'active_tmux_lines': active,
    'launches': launches,
    'errors': errors,
}
out = repo / 'reports' / f'true_rework_queue_{run}_launch.json'
latest = repo / 'reports' / 'true_rework_queue_next100_10lane_launch_latest.json'
for p in [out, latest]:
    p.write_text(json.dumps(launch_report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(json.dumps({'run_base': run, 'state': launch_report['state'], 'active_lane_sessions': len(active), 'errors': len(errors), 'launch_report': str(out)}, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)
PY
```

如果不想使用上面的 Python launcher，也可以逐 lane 直接执行：

```bash
tmux new-session -d -s n100_<STAMP>_l01 \
  "cd /root/work/抗菌肽/数据库/batch/4-team && PYTHONUNBUFFERED=1 python scripts/run_true_rework_queue.py \
  --manifest reports/true_rework_queue_manifest_${RUN}_lane01.json \
  --max-rework 5 --model gpt-5.5 --reasoning-effort xhigh \
  --sandbox danger-full-access --codex-bypass-approvals-and-sandbox \
  --worker-timeout-seconds 1800 --worker-infra-retries 5 --retry-worker-timeouts \
  --paper-runtime-retries 5 --run-label ${RUN}_lane01 --obtainable-only \
  > logs/${RUN}_lane01.log 2>&1"
```

## 6. 启动后验证

```bash
date '+%F %T %Z'
tmux ls 2>/dev/null | rg "$RUN|n100_" || true
ps -eo pid,etime,args | rg '[r]un_true_rework_queue.py|[c]odex exec' | rg "$RUN|true_rework_queue_attempt" || true

python - <<'PY'
from pathlib import Path
run = '<替换为 RUN>'
for lane in range(1, 11):
    p = Path(f'logs/{run}_lane{lane:02d}.log')
    text = p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''
    lines = [line for line in text.splitlines() if line.strip()]
    print(f'lane{lane:02d} size={p.stat().st_size if p.exists() else 0} lines={len(lines)} tail={lines[-3:] if lines else []}')
PY
```

启动成功的最低证据：

- 10 个 tmux session 存活；
- 每个 lane log 至少出现 `[1/N] true rework queue <paper_id>`；
- 进程里能看到 `python scripts/run_true_rework_queue.py` 和/或 `codex exec`；
- status 只能写成 `launched_running` 或 `launched_running_verified`，不能写 completed。

## 7. 运行中检查进度

```bash
RUN=<run_base>
python - <<'PY'
import json
from collections import Counter
from pathlib import Path
run = '<替换为 RUN>'
keys = ['terminal_status_counts','result_status_counts','result_category_counts','refined_status_counts','refined_category_counts','recommended_next_action_counts']
merged = {k: Counter() for k in keys}
lanes, missing, nonaccepted = [], [], []
for i in range(1, 11):
    p = Path(f'reports/true_rework_queue_{run}_lane{i:02d}_latest.json')
    log = Path(f'logs/{run}_lane{i:02d}.log')
    log_lines = [x for x in log.read_text(encoding='utf-8', errors='replace').splitlines() if x.strip()] if log.exists() else []
    if not p.exists():
        missing.append(str(p))
        lanes.append({'lane': f'{i:02d}', 'summary_exists': False, 'log_tail': log_lines[-8:]})
        continue
    d = json.loads(p.read_text(encoding='utf-8'))
    results = d.get('results') or []
    lanes.append({'lane': f'{i:02d}', 'summary_exists': True, 'generated_at': d.get('generated_at'), 'paper_count': len(results), 'terminal_status_counts': d.get('terminal_status_counts') or {}, 'refined_status_counts': d.get('refined_status_counts') or {}, 'log_tail': log_lines[-8:]})
    for k in keys:
        merged[k].update(d.get(k) or {})
    for r in results:
        if r.get('terminal_status') != 'accepted_after_rework':
            nonaccepted.append({k: r.get(k) for k in ['paper_id','terminal_status','result_status','refined_status','result_reason_code','refined_reason_code','recommended_next_action','attempt_count','worker_infra_retry_count','worker_infra_retry_exhausted','gap_codes']})
print(json.dumps({'run': run, 'missing_summary_count': len(missing), 'lane_count_with_summary': 10 - len(missing), 'merged': {k: dict(v) for k,v in merged.items()}, 'nonaccepted': nonaccepted, 'lanes': lanes}, ensure_ascii=False, indent=2, sort_keys=True))
PY
```

解释：

- 没有 lane summary：队列还在跑，结合 tmux/log 判断。
- 10 个 lane summary 都存在：lane 级终态完成，但仍需第 8-10 节的收尾审计。

## 8. 队列结束后的严格 gate 复核

```bash
RUN=<run_base>
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
MAN=reports/true_rework_queue_manifest_${RUN}.json
SEM=reports/${RUN}.full_manifest_recheck_${STAMP}.semantic_gate.json
PUB=reports/${RUN}.full_manifest_recheck_${STAMP}.publication_quality.json

set +e
python .codex/skills/paper-batch-orchestrator/scripts/semantic_three_layer_gate.py \
  --root . --manifest "$MAN" --json > "$SEM"
SEM_RC=$?
python .codex/skills/paper-batch-orchestrator/scripts/check_three_layer_publication_quality.py \
  --root . --manifest "$MAN" --json-out "$PUB"
PUB_RC=$?
python - <<PY
import json
from pathlib import Path
for label, path, rc in [('semantic', Path('$SEM'), $SEM_RC), ('publication', Path('$PUB'), $PUB_RC)]:
    d = json.loads(path.read_text(encoding='utf-8')) if path.exists() and path.stat().st_size else {}
    keys = ['paper_count','publication_grade_pass_count','publication_grade_fail_count','publication_grade_pass','risk_counts','review_status']
    print(json.dumps({'label': label, 'path': str(path), 'returncode': rc, **{k: d.get(k) for k in keys if k in d}}, ensure_ascii=False, indent=2))
PY
```

如果有 blocked 论文，整批 `publication_grade_pass` 通常为 `false`；这不是 accepted 集合失败，而是整批仍含 blocked。

## 9. stale ticket、packet final、complete report 收尾

队列 accepted 后可能出现历史 `workflow_context.open_rework_tickets` 未清空、packet final 与 paper final 不同步、complete report gate 状态陈旧。必须在 accepted 集合上做 closure repair。

可复用逻辑：

1. 读取所有 lane summary 的 accepted paper。
2. 用 `scripts/run_true_rework_queue.py::open_ticket_ids()` 做 reconciled open-ticket 判断。
3. 若 `workflow_context.open_rework_tickets` 有历史票据，但 reconciled open ticket 为 `[]`，用 `scripts/miaobi_message_bridge.py resolve-rework` 关闭。
4. 对 semantic pass 的 accepted 论文，把 `papers/<paper_id>/final/review_report.json` 同步到 `paper_packets/<paper_id>/final/review_report.json`。
5. 更新 `reports/<paper_id>.complete_message_test_report.json` 的 gate summary 和 ticket count。
6. 记录：`reports/true_rework_queue_${RUN}_artifact_closure_repair_latest.json` 和 `reports/true_rework_queue_${RUN}_packet_complete_sync_latest.json`。

单篇关闭 stale ticket 示例：

```bash
python scripts/miaobi_message_bridge.py resolve-rework \
  --paper-id <paper_id> \
  --ticket-id rwk-complete-test-0001 \
  --status resolved \
  --state final_approval \
  --resolved-by system \
  --message "post-run artifact closure repair: strict gates/reconciled ticket state show ticket is closed" \
  --artifact-ref papers/<paper_id>/final/review_report.json \
  --artifact-ref papers/<paper_id>/work/review/quality_feedback.json
```

复核 open ticket：

```bash
PYTHONPATH=scripts python - <<'PY'
from pathlib import Path
from run_true_rework_queue import open_ticket_ids
print(open_ticket_ids(Path.cwd(), '<paper_id>'))
PY
```

## 10. full artifact audit

收尾后必须检查 accepted 论文的 artifact 闭环。

检查项：

- `papers/<paper_id>/final/review_report.json` 存在且可读。
- `paper_packets/<paper_id>/final/review_report.json` 存在且关键字段与 paper final 一致。
- `publication_grade=true`。
- `validator_contract_passed=true`。
- `source_reviewed=true` 或 `source_review_depth` 足够明确。
- `checked_inputs` 非空。
- `rework_targets=[]`。
- reconciled `open_ticket_ids()` 为空。
- raw `workflow_context.open_rework_tickets` 为空。
- `quality_feedback.issue_count` 为 0 或空。
- complete report 的 `structural_ready`、`validator_contract_ready`、`semantic_gate_ready`、`publication_grade_ready` 均为 true。

当前仓库已按此逻辑生成这些报告：

```bash
ls reports/true_rework_queue_*_full_artifact_audit_latest.json
```

通过条件：

```text
issue_count=0
papers_with_issues=0
```

如果不满足，先修复 ticket/packet/complete report，再重跑 audit；不要直接报告 completed。

## 11. accepted sample audit

把各 lane 的 accepted sample audit manifest 合并：

```bash
RUN=<run_base>
python - <<'PY'
import json
from pathlib import Path
run = '<替换为 RUN>'
items, sources, seen = [], [], set()
for i in range(1, 11):
    d = json.loads(Path(f'reports/true_rework_queue_{run}_lane{i:02d}_latest.json').read_text(encoding='utf-8'))
    ap = d.get('accepted_sample_audit_manifest_path')
    if not ap:
        continue
    p = Path(ap)
    sources.append(str(p))
    if p.exists():
        for item in json.loads(p.read_text(encoding='utf-8')).get('items') or []:
            key = item.get('paper_id')
            if key and key not in seen:
                items.append(item)
                seen.add(key)
out = Path(f'reports/accepted_sample_audit/{run}_combined_manifest.json')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({'run_label': run + '_combined', 'source_lane_manifests': sources, 'item_count': len(items), 'items': items}, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(json.dumps({'out': str(out), 'source_count': len(sources), 'item_count': len(items)}, ensure_ascii=False, indent=2))
PY
```

运行审计：

```bash
PYTHONPATH=scripts python scripts/accepted_sample_audit.py \
  --manifest reports/accepted_sample_audit/${RUN}_combined_manifest.json \
  --run-label ${RUN}_combined
```

通过条件：

```text
failed_count=0
issue_counts={}
```

## 12. 最终状态报告

最终 status 必须包含：

- `state`
- manifest / launch report 路径
- lane count / paper count
- terminal status counts
- active tmux/process counts
- artifact closure repair 结果
- packet complete sync 结果
- full artifact audit 结果
- semantic gate pass/fail
- publication QA 结果
- accepted sample audit 结果
- nonaccepted 明细

状态用语建议：

- 只有 lane summary：`lane_terminal_pending_post_audit`
- artifact audit 和 sample audit 都通过但有 blocked：`lane_terminal_full_artifact_audit_clean_accepted_sample_audit_passed_with_blocked_cases`
- 有初始化失败：`...with_initial_queue_failed_case`
- 全部 accepted 且 gate / QA / artifact / sample audit 都通过：才可写 clean completion。

## 13. 汇总所有审查过的论文

当前汇总命令会扫描 `reports/true_rework_queue_*_lane*_latest.json`，按 paper_id 去重，保留最新 lane 结果，并输出 JSON/CSV：

```bash
python - <<'PY'
import csv, json, re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

repo = Path.cwd()
reports = repo / 'reports'

def now(): return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def stamp(): return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
def load(path):
    try: return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception as e: return {'_load_error': str(e)}
def run_from_lane_name(p):
    m = re.match(r'true_rework_queue_(.+)_lane(\d+)_latest\.json$', p.name)
    if not m: return None, None
    return m.group(1), int(m.group(2))

lane_files = []
for p in sorted(reports.glob('true_rework_queue_*_lane*_latest.json')):
    run, lane = run_from_lane_name(p)
    if run:
        lane_files.append((run, lane, p))

rows = []
for run, lane, p in lane_files:
    d = load(p)
    for r in d.get('results') or []:
        rows.append({
            'paper_id': r.get('paper_id'),
            'run_base': run,
            'lane': lane,
            'lane_summary': str(p),
            'lane_generated_at': d.get('generated_at'),
            'terminal_status': r.get('terminal_status') or '',
            'result_status': r.get('result_status') or '',
            'result_category': r.get('result_category') or '',
            'result_reason_code': r.get('result_reason_code') or '',
            'refined_status': r.get('refined_status') or '',
            'refined_category': r.get('refined_category') or '',
            'refined_reason_code': r.get('refined_reason_code') or '',
            'recommended_next_action': r.get('recommended_next_action') or '',
            'attempt_count': r.get('attempt_count'),
            'worker_infra_retry_count': r.get('worker_infra_retry_count'),
            'worker_infra_retry_exhausted': r.get('worker_infra_retry_exhausted'),
            'gap_codes': ';'.join(r.get('gap_codes') or []),
            'worker_infra_reason_codes': ';'.join(r.get('worker_infra_reason_codes') or []),
        })

by_pid = defaultdict(list)
for row in rows:
    if row['paper_id']:
        by_pid[row['paper_id']].append(row)

def sort_key(row):
    return (row.get('lane_generated_at') or '', row.get('run_base') or '', str(row.get('lane') or ''))

unique, duplicates = [], {}
for pid, rs in by_pid.items():
    rs_sorted = sorted(rs, key=sort_key)
    unique.append(rs_sorted[-1])
    if len(rs) > 1:
        duplicates[pid] = rs_sorted
unique = sorted(unique, key=lambda r: (r['run_base'], int(r['lane']), r['paper_id'] or ''))

accepted = [r for r in unique if r['terminal_status'] == 'accepted_after_rework']
blocked = [r for r in unique if r['terminal_status'] != 'accepted_after_rework']
summary = {
    'generated_at': now(),
    'scope': 'reports/true_rework_queue_*_lane*_latest.json',
    'completion_claim': 'aggregate_of_queue_terminal_results_not_blanket_publication_grade_clean_claim',
    'lane_summary_file_count': len(lane_files),
    'lane_result_rows': len(rows),
    'unique_paper_count': len(unique),
    'duplicate_paper_count': len(duplicates),
    'accepted_after_rework_count': len(accepted),
    'nonaccepted_count': len(blocked),
    'terminal_status_counts': dict(sorted(Counter(r['terminal_status'] or 'unknown' for r in unique).items())),
    'result_status_counts': dict(sorted(Counter(r['result_status'] or 'unknown' for r in unique).items())),
    'blocked_result_status_counts': dict(sorted(Counter((r['result_status'] or r['refined_status'] or r['terminal_status'] or 'unknown') for r in blocked).items())),
    'duplicate_paper_ids': sorted(duplicates),
}

out_json = reports / f'all_reviewed_papers_aggregate_{stamp()}.json'
out_csv = reports / f'all_reviewed_papers_aggregate_{stamp()}.csv'
latest_json = reports / 'all_reviewed_papers_aggregate_latest.json'
latest_csv = reports / 'all_reviewed_papers_aggregate_latest.csv'
for p in [out_json, latest_json]:
    p.write_text(json.dumps({**summary, 'papers': unique}, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
fields = ['paper_id','run_base','lane','terminal_status','result_status','result_category','result_reason_code','refined_status','refined_category','refined_reason_code','recommended_next_action','attempt_count','worker_infra_retry_count','worker_infra_retry_exhausted','gap_codes','worker_infra_reason_codes','lane_generated_at','lane_summary']
for p in [out_csv, latest_csv]:
    with p.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{k: r.get(k, '') for k in fields} for r in unique])
print(json.dumps({'json_latest': str(latest_json), 'csv_latest': str(latest_csv), 'unique_paper_count': len(unique), 'accepted_after_rework_count': len(accepted), 'nonaccepted_count': len(blocked)}, ensure_ascii=False, indent=2))
PY
```

## 14. 故障处理

### 14.1 Codex/API/worker 非零退出

表现：`infrastructure_codex_worker_retry_exhausted` 或 `codex_worker_nonzero_exit`。

处理：

1. 保留该论文 blocked，不要改为 accepted。
2. 查看对应 `reports/<paper_id>.true_rework_queue_attempt_*.codex_last_message.md` 和 lane log。
3. 进入 infra recovery 队列单独重试，仍使用原 paper 的 `CODEX_REVIEW_PROMPT.md`。

### 14.2 watchdog timeout

表现：`blocked_watchdog_timeout_retryable`。

处理：

1. 保留 blocked。
2. 单独加长 watchdog 或缩小 prompt/context 后重试。
3. 记录 retry 次数；超过 5 次仍失败则保留 blocked。

### 14.3 source gap / external supplement gap

表现：`blocked_missing_external_supplement`、`blocked_figure_chart_value_gap`。

处理：

1. 不编造精确值。
2. 如果本地材料没有，则写入 `quality_feedback.json` 的 `unrecoverable_material_gaps`。
3. 只有外部补充材料或图表数字化完成后才能重试。

### 14.4 parser / table extraction gap

表现：`blocked_activity_table_extraction_gap`。

处理：

1. 先定位表格来源：XML、PDF text、supplementary table、OOXML、archive。
2. 修 parser 或手工视觉/表格抽取。
3. worker-2 更新 activity/toxicity rows 后，再交给 worker-6 复审。

### 14.5 bounded rework cap unresolved

表现：`blocked_rework_cap_unresolved`。

处理：

1. 读取 `quality_feedback.json` 和 `rework_context/<paper_id>/CODEX_REVIEW_PROMPT.md`。
2. 改进 owner context，明确 worker 技能、历史疏漏、材料路径、未过 gate 的具体原因。
3. 重新启动新 Codex CLI owner worker；最多 5 次，仍不通过则保留 blocked。

## 15. 最终汇报模板

```text
当前 run <RUN> 已终止：tmux=0，相关进程=0。
队列结果：N 篇，accepted_after_rework=A，blocked_after_best_effort=B，initial_queue_failed=I。
收尾：stale ticket closed=X，packet final synced=Y，complete report updated=Z。
full artifact audit：issue_count=0，papers_with_issues=0。
accepted sample audit：pass=P，fail=0。
semantic gate：pass=S，fail=F。
publication QA：整批为 false/true；如果 false，原因是 blocked/open_rework_targets。
结论：accepted 集合闭环通过；整批不能说全 clean，blocked 论文按原因进入后续队列。
```
