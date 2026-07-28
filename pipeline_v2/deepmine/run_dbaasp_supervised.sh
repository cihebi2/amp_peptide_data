#!/bin/bash
# Supervisor: re-run the DBAASP driver until every paper is done. Rate-limited papers stay
# un-done and get retried each round; when claude quota resets (~40 min), they succeed.
# Never stops on rate limits — only stops when all done or genuinely stuck (no progress for many rounds).
cd /home/cihebi/抗菌肽/数据集/batch/5-team/pipeline_v2/deepmine
LOG=dbaasp.log
TOTAL=$(python3 -c "import json;print(len(json.load(open('dbaasp_worklist.json'))))" 2>/dev/null || echo 0)
stale=0
while true; do
  before=$(python3 -c "import json,os;print(len(json.load(open('dbaasp_state.json'))) if os.path.exists('dbaasp_state.json') else 0)" 2>/dev/null || echo 0)
  if [ "$before" -ge "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then echo "$(date +%H:%M) ALL DONE $before/$TOTAL" >> $LOG; break; fi
  echo "$(date +%H:%M) round start: $before/$TOTAL done" >> $LOG
  DEEPMINE_CONC=24 python3 extract_dbaasp.py >> $LOG 2>&1
  after=$(python3 -c "import json,os;print(len(json.load(open('dbaasp_state.json'))) if os.path.exists('dbaasp_state.json') else 0)" 2>/dev/null || echo 0)
  echo "$(date +%H:%M) round end: $after/$TOTAL done" >> $LOG
  if [ "$after" -ge "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then echo "$(date +%H:%M) ALL DONE" >> $LOG; break; fi
  if [ "$after" -le "$before" ]; then
    stale=$((stale+1))
    echo "$(date +%H:%M) no progress (round $stale) — likely rate-limited, waiting 300s for quota reset" >> $LOG
    if [ "$stale" -ge 20 ]; then echo "$(date +%H:%M) STUCK after 20 stale rounds, stopping" >> $LOG; break; fi
    sleep 300
  else
    stale=0
    sleep 20
  fi
done
