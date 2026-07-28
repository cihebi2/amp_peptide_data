#!/usr/bin/env bash
set -u
cd '/home/cihebi/抗菌肽/数据集/batch/5-team'
report_dir='pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor'
old_pid='2937486'
current_paper='PMC12715223'
journal="$report_dir/supervisor_journal.jsonl"
log="$report_dir/restart_after_${current_paper}.log"
exec >>"$log" 2>&1
printf '%s watcher_started old_pid=%s paper=%s\n' "$(date -Is)" "$old_pid" "$current_paper"
while kill -0 "$old_pid" 2>/dev/null; do
  if grep -q '"event": "paper_attempt_finished".*"paper_id": "PMC12715223"' "$journal" 2>/dev/null; then
    printf '%s current_paper_finished\n' "$(date -Is)"
    # The supervisor journals completion before its configured 15-second sleep.
    # Stop only when the just-finished campaign child has exited.
    for _ in $(seq 1 10); do
      if ! pgrep -P "$old_pid" >/dev/null 2>&1; then break; fi
      sleep 1
    done
    if pgrep -P "$old_pid" >/dev/null 2>&1; then
      printf '%s unsafe_restart_child_still_present; watcher_exits_without_signal\n' "$(date -Is)"
      exit 3
    fi
    python3 - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import json, os
p=Path('pipeline_v2/deepmine/dbaasp_strict_pilot/reports/remaining_200_campaign/supervisor/supervisor_journal.jsonl')
row={'event':'supervisor_safe_restart_requested','created_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'old_pid':2937486,'completed_boundary_paper':'PMC12715223','reason':'activate bounded immediate retries for nonterminal repair papers'}
with p.open('a',encoding='utf-8') as f:
 f.write(json.dumps(row,ensure_ascii=False)+'\n'); f.flush(); os.fsync(f.fileno())
PY
    kill -TERM "$old_pid"
    for _ in $(seq 1 30); do
      if ! kill -0 "$old_pid" 2>/dev/null; then break; fi
      sleep 1
    done
    if kill -0 "$old_pid" 2>/dev/null; then
      printf '%s old_supervisor_did_not_exit; watcher_exits\n' "$(date -Is)"
      exit 4
    fi
    printf '%s old_supervisor_exited\n' "$(date -Is)"
    nohup setsid env PYTHONUNBUFFERED=1 python3 pipeline_v2/deepmine/supervise_remaining_200_strict_campaign.py \
      --max-sweeps 100 \
      --max-attempts-per-paper 12 \
      --max-consecutive-attempts 3 \
      --max-rework-rounds 3 \
      --worker-timeout 5400 \
      --audit-timeout 5400 \
      --sleep-seconds 15 \
      >>"$report_dir/supervisor_process.stdout.log" \
      2>>"$report_dir/supervisor_process.stderr.log" \
      </dev/null &
    new_pid=$!
    echo "$new_pid" > "$report_dir/supervisor_process.pid"
    printf '%s new_supervisor_launched pid=%s\n' "$(date -Is)" "$new_pid"
    sleep 5
    if ! kill -0 "$new_pid" 2>/dev/null; then
      printf '%s new_supervisor_failed_early\n' "$(date -Is)"
      exit 5
    fi
    printf '%s restart_complete\n' "$(date -Is)"
    exit 0
  fi
  sleep 2
done
printf '%s old_supervisor_exited_before_boundary; launching_replacement\n' "$(date -Is)"
nohup setsid env PYTHONUNBUFFERED=1 python3 pipeline_v2/deepmine/supervise_remaining_200_strict_campaign.py \
  --max-sweeps 100 --max-attempts-per-paper 12 --max-consecutive-attempts 3 \
  --max-rework-rounds 3 --worker-timeout 5400 --audit-timeout 5400 --sleep-seconds 15 \
  >>"$report_dir/supervisor_process.stdout.log" 2>>"$report_dir/supervisor_process.stderr.log" </dev/null &
new_pid=$!
echo "$new_pid" > "$report_dir/supervisor_process.pid"
printf '%s replacement_launched pid=%s\n' "$(date -Is)" "$new_pid"
