#!/bin/bash
cd /home/cihebi/抗菌肽/数据集/batch/5-team
P=pipeline_v2/deepmine/progress.txt
: > "$P"
while pgrep -f recover_excluded_dual.py >/dev/null 2>&1; do
  d=$(python3 -c "import json;print(len(json.load(open('pipeline_v2/deepmine/recovered_state.json'))))" 2>/dev/null || echo 0)
  a=$(( $(wc -l < pipeline_v2/deepmine/recovered_approved.tsv 2>/dev/null || echo 1) - 1 ))
  r=$(( $(wc -l < pipeline_v2/deepmine/recovered_review_queue.tsv 2>/dev/null || echo 1) - 1 ))
  echo "$(date +%H:%M) done=${d}/64 approved=${a} review=${r} codex=$(pgrep -f openai/codex-linux|wc -l)" >> "$P"
  sleep 150
done
d=$(python3 -c "import json;print(len(json.load(open('pipeline_v2/deepmine/recovered_state.json'))))" 2>/dev/null || echo 0)
a=$(( $(wc -l < pipeline_v2/deepmine/recovered_approved.tsv 2>/dev/null || echo 1) - 1 ))
r=$(( $(wc -l < pipeline_v2/deepmine/recovered_review_queue.tsv 2>/dev/null || echo 1) - 1 ))
echo "$(date +%H:%M) FINISHED done=${d}/64 approved=${a} review=${r}" >> "$P"
