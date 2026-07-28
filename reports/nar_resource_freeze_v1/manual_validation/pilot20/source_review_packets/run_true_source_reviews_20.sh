#!/usr/bin/env bash
set -euo pipefail
cd /root/work/抗菌肽/数据库/batch/4-team
python scripts/run_pilot20_true_source_reviews.py \
  --packet-index reports/nar_resource_freeze_v1/manual_validation/pilot20/source_review_packets/packet_index_latest.csv \
  --parallel 4
