# Team Rework Message Contract

Use this reference for batch/2-team AMP three-layer runs when Worker-6 finds a
hard failure. The desired behavior is not silent repair or fast acceptance; it is
durable team-mediated rework with paper-local evidence.

## Native Subagents vs OMX Team

- Native Codex subagents are acceptable for bounded diagnostic fanout, such as
  independent spot reviews whose only output returns to the leader.
- Native subagents are not the production message bus for six-worker curation.
  They do not own `.omx/state/team/<team>/` task files, worker inboxes, worker
  mailbox delivery state, or durable task transitions.
- Production six-worker processing must use `omx team` / controller-managed team
  state, `omx team api ... --json`, worker inboxes, task files, and mailbox
  messages for handoff and rework.

## Worker-6 Send-Back Rule

When Worker-6 detects any hard gate failure, it must do all of the following
before the paper can be considered terminal:

1. Set `review_status: needs_targeted_rework` and `publication_grade: false`.
2. Write `work/review/quality_feedback.json` with one entry per failed owner
   lane.
3. Write `final/review_report.json` with non-empty `rework_targets`.
4. Send a durable team message to the responsible worker lane.
5. Keep or move the paper/task out of accepted status until the owner lane
   repairs the artifact and Worker-6 re-adjudicates.

Worker-6 must not mark `accepted_clean` or `accepted_with_cautions` when
`rework_targets` is non-empty or when the semantic gate reports any hard issue.

## Required Rework Target Schema

Each `rework_targets[]` item should be specific enough that the owner worker can
repair without guessing:

```json
{
  "worker": "worker-2",
  "layer": "activity",
  "artifact_path": "papers/<paper_id>/final/activity_toxicity_evidence.json",
  "failing_object": "activity_records[66]",
  "failure_code": "sentence_fragment_species",
  "source_evidence_to_check": [
    "papers/<paper_id>/source/paper.xml::table/Tab2",
    "papers/<paper_id>/source/supplementary/<file>"
  ],
  "required_action": "Rebuild the row from the source table, recover endpoint/unit/target, and remove prose-derived false rows.",
  "acceptance_check": "semantic_three_layer_gate.py has no hard activity issue for this paper"
}
```

## Team API Dispatch Pattern

Prefer controller/runtime APIs. Do not use blind `tmux send-keys` as the primary
message path.

```bash
omx team api send-message --input '{
  "team_name": "<team>",
  "from_worker": "worker-6",
  "to_worker": "worker-2",
  "body": "needs_targeted_rework: <paper_id> activity_records[66] sentence_fragment_species; see work/review/quality_feedback.json"
}' --json
```

If the runtime supports creating or updating tasks, Worker-6 or the controller
should also create/update a repair task assigned to the failed lane, then verify
the task returns to Worker-6 for re-adjudication.

## Material Exhaustion Contract

Every worker report should state which materials were actually inspected:

- `paper.xml` and table/figure locators.
- paper PDF when XML/table extraction is incomplete.
- PMC/OA package members and staged supplementary files.
- true supplementary PDF/DOCX/XLSX/CSV/ZIP members, not landing pages.
- merged APD6/DBAASP/DRAMP source rows and literature links.
- unavailable or unreadable assets with a reason and impact assessment.

If a material exists but cannot be parsed, mark `blocked_missing_primary_material`
or `needs_targeted_rework` with the exact file and required extraction method.
Do not replace unavailable evidence with database rows or publisher page text.
