Re-review completed for `doi__10.3389_fmicb.2020.01353`. I did not rerun the initial bootstrap.

I added a reproducible repair script at [repair_doi_10_3389_fmicb_2020_01353_worker246.py](/root/work/抗菌肽/数据库/batch/4-team/scripts/repair_doi_10_3389_fmicb_2020_01353_worker246.py) and updated the worker-2/4/6 artifacts. Key outcomes:

- Worker-2: activity rows repaired to `26` total, including Table 1 MIC/MBC, Table 2 MLC, and Table 3 FITC-SM-985 cell-killing rows.
- Worker-4: `36` linked database records reconciled as `source_verified`, with endpoint-label/database-entry cautions preserved.
- Worker-6: final adjudication rewritten as `accepted_with_cautions`, `publication_grade: true`, no open `rework_targets`.
- `quality_feedback.json` now has `issue_count: 0`.
- `rework_responses.jsonl` closes `rwk-complete-test-0001`.
- Non-fabricated gap recorded: local material has no SM-985 toxicity/hemolysis/cytotoxicity assay; this is recorded as nonblocking.

Verification passed:

- Semantic gate: `publication_grade_pass_count=1`, `fail_count=0`, `issue_count=0`.
- Publication QA: `publication_grade_pass=true`, `risk_counts={}`.
- Packet/report state: `open_rework_ticket_count=0`, terminal status `accepted_with_cautions`.

