#!/usr/bin/env bash
set -euo pipefail
cd /root/work/抗菌肽/数据库/batch/4-team
codex exec   -C /root/work/抗菌肽/数据库/batch/4-team   --skip-git-repo-check   --add-dir /root/work/抗菌肽/数据库/batch/4-team   --add-dir /mnt/d/work/抗菌肽/数据库/merged_amp_corpus   -m gpt-5.5   -c 'model_reasoning_effort="xhigh"'   -c 'approval_policy="never"'   -o /root/work/抗菌肽/数据库/batch/4-team/reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0051__doi__10.1038_s41598-020-60570-w/CODEX_LAST_MESSAGE.md   - < /root/work/抗菌肽/数据库/batch/4-team/reports/nar_resource_freeze_v1/manual_validation/validation420/source_review_packets/V420P0051__doi__10.1038_s41598-020-60570-w/CODEX_REVIEW_PROMPT.md
