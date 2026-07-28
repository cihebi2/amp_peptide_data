# Low-Level Team Rescue

Use this only when normal launcher/controller reconciliation is not enough.

Primary tool:

```bash
python workspace-guide/team-paper-sample/team_api_json.py <operation> --input-file <json-file> --json
```

This wrapper exists to avoid shell quoting issues and to keep low-level team API usage structured.

## When to use low-level rescue

Use it only for cases such as:

- task claim drift that controller `once` did not settle
- worker inbox/identity rewrite needs explicit reassertion
- mailbox delivery state needs inspection during debugging
- you need exact team API control-plane visibility before modifying state

Do not start with this layer if controller reconciliation is still working.

## Safe pattern

1. inspect current task JSON and worker status first
2. snapshot any relevant task/worker files before low-level intervention
3. perform one bounded team API operation
4. re-read task/worker/mailbox state
5. run controller `once` again

## High-level guidance

- Use `launch_paper_team_v2.py` and `paper_batch_controller.py` as the primary control plane.
- Use `team_api_json.py` only as a repair surface, not as the normal orchestration path.
- Never do broad manual rewrites when a single task- or worker-scoped repair will do.

## Typical situations

### Claim drift after task 4 outputs exist

Check:

- `tasks/task-4.json`
- worker identities
- current owner/claim token fields
- whether final files are already valid

If artifacts are valid but state is wrong, prefer a narrow claim/transition repair and then let controller `once` finish convergence.

### Generic worker contract reappeared

Check:

- worker inbox contents
- worker identity metadata
- task subject/description text

Use low-level rewrite only if the launcher/controller cannot reassert the fixed contract.

### Mailbox ambiguity

If a team appears idle but delivery state is unclear, inspect mailbox files before assuming the worker never saw the instruction.

## Required follow-up

After any low-level rescue, always run:

```bash
python workspace-guide/team-paper-sample/paper_batch_controller.py once \
  --manifest workspace-guide/team-paper-sample/batch-v1/<manifest>.json \
  --issues workspace-guide/team-paper-sample/batch-v1/<issues>.jsonl
```

That final reconciliation is what returns the runtime to the normal control plane.
