#!/bin/bash
# kill by PID (from a script file so this shell's args don't self-match the grep)
for p in $(ps -eo pid,args | grep -F "recover_excluded_dual.py" | grep -v grep | awk '{print $1}'); do kill "$p" 2>/dev/null; done
for p in $(ps -eo pid,args | grep -F "openai/codex-linux" | grep -v grep | awk '{print $1}'); do kill -9 "$p" 2>/dev/null; done
for p in $(ps -eo pid,args | grep -F "claude -p" | grep -v grep | awk '{print $1}'); do kill "$p" 2>/dev/null; done
sleep 3
echo "after kill: driver=$(ps -eo args|grep -F recover_excluded_dual.py|grep -v grep|wc -l) codex=$(ps -eo args|grep -F openai/codex-linux|grep -v grep|wc -l) claude_p=$(ps -eo args|grep -F 'claude -p'|grep -v grep|wc -l)"
