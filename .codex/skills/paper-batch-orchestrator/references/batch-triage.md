# Batch Triage

Use this reference when you need to decide what kind of batch intervention is actually warranted.

## Case 1: Batch looks stuck, but some papers are still finishing

Signals:

- issue log still grows
- controller `once` still changes paper state
- some team directories or tmux sessions are active

Action:

- do not declare the batch stuck yet
- run controller `once`
- summarize which papers remain active and why

## Case 2: Batch looks done, but monitor rows disagree

Signals:

- final validation over the manifest says all papers are ready
- stale monitor rows still report open quality feedback or active teams

Action:

- trust fresh local validation over old monitor rows
- verify active modes, active tmux teams, and validator output
- document the stale monitor artifact instead of reopening papers blindly

## Case 3: Many papers fail for the same reason

Signals:

- repeated issue types such as `contract_rewrite_rescue`, `worker_bootstrap_rescue`, or `quality_feedback_generated`
- multiple papers blocked on the same quality code

Action:

- summarize the repeated pattern first
- check `workspace-guide/team-paper-sample/extraction-issues-20260423/README.md`
- prefer one systemic fix or one repeatable rescue recipe over isolated manual treatment

## Case 4: Only a few papers are still failing

Action:

- identify exactly which papers remain open
- classify each one by blocker:
  - upstream artifacts missing
  - supplementary mismatch
  - deterministic/fallback final rejected
  - claim drift / runtime drift
  - schema or locator weakness
- then hand off or perform one-paper rescue with `$paper-omx-team-extraction`

## Case 5: A paper was reopened by re-audit

Action:

- do not assume prior success still holds
- rerun fresh local validation for that paper
- inspect issue rows after the reopen event
- check whether the reopen is real or only caused by stale monitor/runtime state

## Recommended batch summary format

When reporting batch status, include:

- manifest path
- issues log path
- total papers
- completed and ready count
- problem count
- top repeated issue types
- active team count
- one-sentence verdict

Example verdicts:

- `Batch complete and locally validated; stale monitor rows do not reflect current state.`
- `Batch progressing; 6 papers remain active, mostly blocked on task-4 source-reviewed reruns.`
- `Batch blocked by systemic worker bootstrap drift; paper-level rescues would be repetitive until runtime behavior is stabilized.`
