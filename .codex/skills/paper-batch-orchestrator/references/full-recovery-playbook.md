# Full Recovery Playbook

Use this playbook when you need to reproduce the real batch workflow, not just the happy-path commands.

## Core idea

Keep the recovery ladder narrow:

1. validate fresh local state
2. reconcile with controller `once`
3. rescue only the blocked paper
4. rerun only the blocked worker lane when possible
5. reopen or rewrite final artifacts only when validation proves it is necessary

Do not skip directly to broad reruns.

## Recovery ladder

### Step 1: Rebuild the current truth snapshot

For the batch you are handling, establish:

- manifest path
- issues log path
- total papers in manifest
- fresh final-ready count
- current active team count
- repeated issue types in the issue log

Use:

- `scripts/verify_batch.py`
- `scripts/summarize_issue_log.py`

### Step 2: Decide whether the problem is batch-wide or paper-local

Treat it as **batch-wide** if many papers share the same issue type, such as:

- `contract_rewrite_rescue`
- `worker_bootstrap_rescue`
- `quality_feedback_generated`

Treat it as **paper-local** if only a few papers remain open and each has a concrete blocker.

### Step 3: Run controller reconciliation first

Before manual rescue, run:

```bash
python workspace-guide/team-paper-sample/paper_batch_controller.py once \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
```

The controller can often:

- auto-close drifted tasks
- generate or dispatch quality feedback
- shut down completed teams
- launch the next paper

### Step 4: If only one paper is blocked, switch to one-paper rescue

At this point, hand off mentally to `$paper-omx-team-extraction`.

Check for these common blockers:

- task 1/2/3 not accepted yet
- supplementary mismatch
- deterministic/fallback final blocked by quality gate
- claim drift after artifacts already exist
- final schema or locator weakness

### Step 5: Use the smallest deterministic lane rescue possible

Preferred order:

- `worker-1` if intake/materials manifest is wrong or missing
- `worker-2` if body/table evidence is missing or weak
- `worker-3` if supplementary evidence is missing or inconsistent with staged assets
- `worker-4` only after upstream artifacts are accepted

Pattern:

```bash
python workspace-guide/team-paper-sample/paper_worker_v1.py run-role --paper-id <PMC...> --worker worker-<n>
python workspace-guide/team-paper-sample/paper_batch_controller.py once \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
```

### Step 6: Reopen only when fresh validation says the paper is not ready

Never reopen purely because:

- a stale tmux injection says stalled
- an old monitor row says open feedback exists
- a historical team directory still exists under archive paths

Reopen only when current local validation fails.

### Step 7: If archive outputs are trustworthy, restore them carefully

Allowed only when:

- they belong to the same paper
- they are from the correct recovery window
- they still pass current validator logic

After restore:

1. rerun validators
2. run controller `once`
3. let controller decide closure/shutdown

## Recovery recipes by failure family

### A. Worker contract / bootstrap drift

Symptoms:

- generic inboxes or generic task text remain
- issue log records `contract_rewrite_rescue` or `worker_bootstrap_rescue`

Response:

1. inspect current team state
2. prefer launcher/controller rewrite path
3. only if needed, use low-level `team_api_json.py` operations
4. retrigger the intended worker after rewrite verification

### B. Claim drift

Symptoms:

- final artifacts exist
- lifecycle stays open under the wrong owner
- issue log records `task4_claim_drift`

Response:

1. validate final files first
2. run controller `once`
3. if controller cannot settle it, use low-level team rescue to inspect current claim owner and close from the current owner side

### C. Supplementary mismatch

Symptoms:

- `source/supplementary/` has assets
- `supp_evidence` says no local supplementary asset

Response:

1. verify source files, XML linkage, and manifest
2. rerun `worker-3`
3. rerun controller `once`
4. only then allow task 4 to proceed

### D. Deterministic or fallback final rejected

Symptoms:

- `final/` files exist
- quality issues include `worker_deterministic_generated`, `controller_fallback_generated`, or `source_direct_fallback`

Response:

1. identify which upstream evidence or final schema is inadequate
2. source-review and normalize only the affected outputs
3. rerun validation
4. run controller `once`

### E. Batch looks complete but monitoring disagrees

Symptoms:

- manifest-wide validation shows all ready
- stale monitor rows still show open quality feedback or active team

Response:

1. trust fresh local validation
2. check active team sessions directly
3. document stale monitoring artifact rather than reopening papers

## What to report after recovery

Always end with:

- manifest path
- issues log path
- completed/ready count
- remaining problem count
- whether any active teams remain
- exact papers still open, if any
- whether the blocker is paper-local or systemic
