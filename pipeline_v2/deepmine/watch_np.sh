#!/bin/bash
cd /home/cihebi/抗菌肽/数据集/batch/5-team
P=pipeline_v2/deepmine/np_progress.txt; : > "$P"
while pgrep -f extract_newpapers_dual.py >/dev/null 2>&1; do
  d=$(python3 -c "import json;print(len(json.load(open('pipeline_v2/deepmine/newpapers_state.json'))))" 2>/dev/null||echo 0)
  e=$(( $(wc -l < pipeline_v2/deepmine/newpapers_extracted.tsv 2>/dev/null||echo 1) - 1 ))
  echo "$(date +%H:%M) done=${d}/431 extracted=${e} codex=$(pgrep -f openai/codex-linux|wc -l)" >> "$P"
  sleep 180
done
echo "$(date +%H:%M) FINISHED" >> "$P"
