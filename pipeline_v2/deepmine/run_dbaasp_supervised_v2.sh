#!/bin/bash
# DBAASP supervisor v2 — concurrency read from dbaasp_conc.txt each round (tunable live).
# Waits for the currently-running driver round to finish first (never runs two drivers at once),
# then continues at the reduced lane count.
#
# Safety knobs:
#   DBAASP_LIMIT=N          process at most N todo papers per round (probe mode)
#   DBAASP_MAX_ROUNDS=N     stop after N rounds (default 30; 0 means unlimited)
#   DBAASP_STALE_LIMIT=N    stop after N no-progress rounds (default 30)
#   DBAASP_SLEEP_SECONDS=N  wait after stale/rate-limited rounds (default 300)
#   DBAASP_ONESHOT=1        stop after one driver round
#   DBAASP_PREFLIGHT=0      skip provider/quota preflight (default 1 for nonzero work)
#   DBAASP_PREFLIGHT_TIMEOUT=N  seconds for tiny provider check (default 45)
#   DBAASP_PROVIDER=claude|codex  extraction/preflight provider (default claude)
cd /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine
LOG=dbaasp.log
LOCK=dbaasp_supervisor.lock
MAX_ROUNDS=${DBAASP_MAX_ROUNDS:-30}
STALE_LIMIT=${DBAASP_STALE_LIMIT:-30}
SLEEP_SECONDS=${DBAASP_SLEEP_SECONDS:-300}
ONESHOT=${DBAASP_ONESHOT:-0}
PREFLIGHT=${DBAASP_PREFLIGHT:-1}
PREFLIGHT_TIMEOUT=${DBAASP_PREFLIGHT_TIMEOUT:-45}
PROVIDER=${DBAASP_PROVIDER:-claude}
LIMIT_ARG=()
if [ -n "${DBAASP_LIMIT:-}" ]; then
  LIMIT_ARG=(--limit "$DBAASP_LIMIT")
fi
# single-instance guard: if a live supervisor holds the lock, exit
if [ -f "$LOCK" ] && kill -0 "$(cat $LOCK 2>/dev/null)" 2>/dev/null; then
  echo "$(date +%H:%M) supervisor already running (pid $(cat $LOCK)), exiting duplicate" >> $LOG; exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
TOTAL=$(python3 -c "import json;print(len(json.load(open('dbaasp_worklist.json'))))" 2>/dev/null || echo 0)
# let the in-flight 24-lane round finish before taking over
extract_running() {
  ps -eo comm,args | awk '$1 ~ /^python/ && $0 ~ /(^|[\\/ ])extract_dbaasp\\.py([ ]|$)/ {found=1} END{exit !found}'
}
while extract_running; do sleep 20; done
echo "$(date +%H:%M) v2 supervisor taking over (MAX_ROUNDS=$MAX_ROUNDS STALE_LIMIT=$STALE_LIMIT SLEEP_SECONDS=$SLEEP_SECONDS LIMIT=${DBAASP_LIMIT:-all} ONESHOT=$ONESHOT PREFLIGHT=$PREFLIGHT PROVIDER=$PROVIDER)" >> $LOG
stale=0
round=0
while true; do
  round=$((round+1))
  if [ "$MAX_ROUNDS" -gt 0 ] && [ "$round" -gt "$MAX_ROUNDS" ]; then
    echo "$(date +%H:%M) max rounds reached ($MAX_ROUNDS), stopping" >> $LOG; break
  fi
  CONC=$(cat dbaasp_conc.txt 2>/dev/null || echo 12)
  if ! [[ "$CONC" =~ ^[0-9]+$ ]] || [ "$CONC" -lt 1 ]; then
    echo "$(date +%H:%M) invalid CONC=$CONC, using 1" >> $LOG
    CONC=1
  fi
  before=$(python3 -c "import json,os;print(len(json.load(open('dbaasp_state.json'))) if os.path.exists('dbaasp_state.json') else 0)" 2>/dev/null || echo 0)
  if [ "$before" -ge "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then echo "$(date +%H:%M) ALL DONE $before/$TOTAL" >> $LOG; break; fi
  if [ "$PREFLIGHT" != "0" ] && [ "${DBAASP_LIMIT:-all}" != "0" ]; then
    echo "$(date +%H:%M) provider preflight start (provider=$PROVIDER timeout=${PREFLIGHT_TIMEOUT}s)" >> $LOG
    if ! python3 preflight_dbaasp_provider.py --provider "$PROVIDER" --timeout "$PREFLIGHT_TIMEOUT" >> $LOG 2>&1; then
      echo "$(date +%H:%M) provider preflight failed; stopping before extraction round" >> $LOG
      break
    fi
    echo "$(date +%H:%M) provider preflight ok" >> $LOG
  fi
  echo "$(date +%H:%M) round $round start: $before/$TOTAL (CONC=$CONC LIMIT=${DBAASP_LIMIT:-all})" >> $LOG
  DEEPMINE_CONC=$CONC python3 extract_dbaasp.py "${LIMIT_ARG[@]}" >> $LOG 2>&1
  after=$(python3 -c "import json,os;print(len(json.load(open('dbaasp_state.json'))) if os.path.exists('dbaasp_state.json') else 0)" 2>/dev/null || echo 0)
  echo "$(date +%H:%M) round $round end: $after/$TOTAL" >> $LOG
  if [ "$ONESHOT" = "1" ]; then echo "$(date +%H:%M) oneshot requested, stopping" >> $LOG; break; fi
  if [ "$after" -ge "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then echo "$(date +%H:%M) ALL DONE" >> $LOG; break; fi
  if [ "$after" -le "$before" ]; then
    stale=$((stale+1))
    echo "$(date +%H:%M) no progress (stale round $stale) — rate-limited, waiting ${SLEEP_SECONDS}s" >> $LOG
    if [ "$stale" -ge "$STALE_LIMIT" ]; then echo "$(date +%H:%M) STUCK $STALE_LIMIT stale rounds, stopping" >> $LOG; break; fi
    sleep "$SLEEP_SECONDS"
  else
    stale=0; sleep 20
  fi
done
