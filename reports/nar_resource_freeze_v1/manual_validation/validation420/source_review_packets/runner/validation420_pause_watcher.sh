#!/usr/bin/env bash
set -euo pipefail
RUNNER_PID="3373866"
CHILD_PIDS_CSV="${CHILD_PIDS_CSV:-}"
ROOT="/root/work/抗菌肽/数据库/batch/4-team"
cd "$ROOT"
IFS=',' read -r -a CHILD_PIDS <<< "$CHILD_PIDS_CSV"
while true; do
  running=0
  for pid in "${CHILD_PIDS[@]}"; do
    [[ -z "$pid" ]] && continue
    if ps -p "$pid" >/dev/null 2>&1; then
      stat=$(ps -o stat= -p "$pid" | awk '{print $1}')
      if [[ "$stat" != Z* ]]; then
        running=$((running+1))
      fi
    fi
  done
  if [[ "$running" -eq 0 ]]; then
    break
  fi
  sleep 30
done
python scripts/summarize_validation420_source_reviews.py >/tmp/validation420_pause_watcher_summary.out 2>&1 || true
python - <<'PY'
import json, os
from pathlib import Path
marker=Path('reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/runner/validation420_queue_pause_marker_latest.json')
try:
    payload=json.loads(marker.read_text(encoding='utf-8'))
except Exception:
    payload={}
payload.update({
    'state':'soft_paused_active_children_finished_parent_still_stopped',
    'active_children_finished_at_local':os.popen('date -Iseconds').read().strip(),
    'active_children_finished_at_utc':os.popen('date -u +%Y-%m-%dT%H:%M:%SZ').read().strip(),
    'runner_parent_status':os.popen('ps -o pid,stat,etime,args -p 3373866 2>/dev/null | tail -n +2').read().strip(),
})
marker.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
status=Path('reports/nar_resource_freeze_v1/manual_validation/validation420/VALIDATION420_RUN_STATUS.md')
with status.open('a',encoding='utf-8') as fh:
    fh.write('\n## Queue Pause Completed '+payload['active_children_finished_at_local']+'\n\n')
    fh.write('- Runner parent remains stopped with `SIGSTOP`; no new packets are being dispatched.\n')
    fh.write('- The four already launched child Codex jobs have exited or are zombie-ready for the stopped parent to reap.\n')
    fh.write('- Pause marker: `reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/runner/validation420_queue_pause_marker_latest.json`.\n')
PY
