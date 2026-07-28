**Findings**

APPROVE

No Critical/High/Medium findings in the current files.

Low:
- `pipeline_v2/deepmine/restart_remaining_200_parallel_at_drain.py`: drain restart has good unit coverage for proc parsing, child detection, journal finish detection, and new-attempt detection, but no full live-process SIGSTOP/SIGCONT/SIGKILL integration test. Risk is mostly operational regression in a Linux process edge case. Minimal fix: add a small subprocess-based handoff integration test with fake supervisor/campaign children.

**Verification Evidence**

- Read the current implementations and corresponding tests for the requested files.
- Ran full focused suite: `142 tests OK`.
- Confirmed current fixes now cover:
  - partial canonical resume rejects out-of-order report lists and duplicate sessions;
  - exact `codex exec`, `gpt-5.5`, `xhigh`, rc 0, unique sessions are gated;
  - mechanical failure + open tickets skips leader but does not terminal-promote;
  - leader finding dedupe is exact and only against open tickets;
  - closure receipts require strict worker-6 terminal schema, owner repair where applicable, gate artifacts, final mirror/count consistency, and duplicate/tamper rejection;
  - scheduler preserves fresh lane even with high rework cap and deduplicates malformed state rows;
  - drain restart waits for campaign drain and normal journal before replacement, with failure recovery via SIGCONT.

**Remaining Risk**

Independent subagent review lanes were unavailable in this environment, so this is my direct read-only review. The only material residual risk is lack of a live end-to-end drain restart test; I did not find evidence that the speed-up changes weaken scientific acceptance gates.