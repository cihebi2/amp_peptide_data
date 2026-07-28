#!/bin/bash
for p in $(ps -eo pid,args | grep -F "openai/codex-linux" | grep -v grep | awk '{print $1}'); do sudo -n kill -9 "$p" 2>/dev/null; done
for p in $(ps -eo pid,args | grep -F "codex exec" | grep -v grep | awk '{print $1}'); do sudo -n kill -9 "$p" 2>/dev/null; done
sleep 2
echo "codex left: $(ps -eo args|grep -F openai/codex-linux|grep -v grep|wc -l)"
