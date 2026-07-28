# deepmine — recover UNSURFACED AMP data from already-acquired papers

## ⭐ RECOMMENDED: dual-model extractor with cross-review — `extract_supp_dual.py`

Runs **both** CLIs on each sheet and reconciles them into a confidence-tagged TSV. Verified on a real
headerless activity matrix: claude (sonnet) is fast but conservative (12 shallow rows, leaves
endpoint/target blank); codex (agentic) reads the source paper and recovers full records (125 rows:
CC50/IC50/IC90/TI, real sequences incl. non-standard residues, viral targets) — spot-checked accurate
against the curated release. Values **both models agree on → `confidence=high`**; codex-only values
(incl. any hallucination) → `codex_only` and are flagged, not trusted.

```bash
cd /home/cihebi/抗菌肽/数据集/batch/5-team
python3 pipeline_v2/deepmine/extract_supp_dual.py --list       # preview (no CLI calls)
python3 pipeline_v2/deepmine/extract_supp_dual.py --limit 3    # smoke test (3 papers)
python3 pipeline_v2/deepmine/extract_supp_dual.py             # full run, resumable
# faster single-model variants:
python3 pipeline_v2/deepmine/extract_supp_dual.py --models claude   # fast bulk, shallow
python3 pipeline_v2/deepmine/extract_supp_dual.py --models codex    # deep, ~4-5 min/paper
```
Output `supp_recovered.tsv` (cols incl. `confidence`, `models`), state `supp_recovered_state.json`.
Tunables (env): `DEEPMINE_CONC` (papers in parallel, default 3), `DEEPMINE_CODEX_TIMEOUT` (default 480s),
`DEEPMINE_CLAUDE_TIMEOUT` (180s), `DEEPMINE_MAX_ROWS` (400).

**RUN IN CLOUD SHELL, not a 2-min-capped session** — codex is ~4-5 min/paper (≈4 h for all 52).
Operational notes learned the hard way:
- codex must run with `--dangerously-bypass-approvals-and-sandbox -o <file> --skip-git-repo-check` and
  from an **empty cwd** (else it scans the huge repo and is far slower). The driver does all of this.
- codex needs root creds: the driver calls `sudo -n HOME=/root codex …`. Ensure passwordless sudo works.
- **Never `pkill -f "codex exec"`** — the pattern matches your own shell and kills it. Kill by PID.

`extract_supp_tables.py` (below) is the earlier claude-only single-model driver — superseded by the dual one.

---

## ⭐ recover excluded papers WITH dual-model approval — `recover_excluded_dual.py`

Recovers the ~6,423 already-extracted activity records from the **97 excluded papers** (30 needs-rework +
67 blocked), but **re-verifies each record against the primary paper with BOTH models and only APPROVES on
dual consensus** ("supported" from claude AND codex); disagreements/unverifiable → a human review queue
(the 复核审批 gate). claude verifies against inlined source text + figure/table captions; codex reads the
paper's source file directly. **5 codex + 5 claude lanes** (`DEEPMINE_CONC=5` → 5 papers in flight × 2 models).

```bash
cd /home/cihebi/抗菌肽/数据集/batch/5-team
python3 pipeline_v2/deepmine/recover_excluded_dual.py --list        # 64 papers with records / 6423 recs
python3 pipeline_v2/deepmine/recover_excluded_dual.py --limit 2     # smoke test
python3 pipeline_v2/deepmine/recover_excluded_dual.py               # full, resumable, 5+5 lanes
python3 pipeline_v2/deepmine/recover_excluded_dual.py --models claude   # fast claude-only pass
```
Outputs: `recovered_approved.tsv` (dual-consensus supported → ingest as a `machine-recovered` evidence tier),
`recovered_review_queue.tsv` (needs human 审批), `recovered_state.json` (resume). Expect MANY records to
land in the review queue — 67/97 papers are `blocked_missing_primary_material`, so their values genuinely
can't be source-confirmed; that separation is the point. Same codex operational rules as below.

---

These drivers re-mine data that was **already fetched but never surfaced** into the curated corpus.
They reuse the project's established CLI-driver pattern (`pipeline_v2/claude_audit.py`,
`residual_driver.py`): a resumable state json of done `paper_id`s, per-paper `try/except`, hard
subprocess timeouts, and append-only TSV output. The claude CLI runs with **Sonnet** (cheap, high
concurrency — never Opus, per project norm).

---

## Target 1 (implemented): supplementary spreadsheet tables

**Source:** `paper_packets/<paper_id>/extracted/supplementary_tables.json`
53 papers carry parsed supplementary sheets — **675 sheets / ~431,061 rows** in total — that never
made it into the corpus. Shape:

```json
{
  "note": "Structured supplementary spreadsheet sheets are parsed ... PDF supplements are text-indexed.",
  "paper_id": "doi__10.1038_s41467-020-17736-x",
  "table_count": 41,
  "tables": [
    {
      "sheet_name": "S2-19.7.19",
      "row_count": 210,
      "source_path": "/.../supplementary/local-...MOESM7_ESM.xlsx",
      "rows": [ ["User: USER"], ["Path: C:\\..."], ["AMSIN", "36", "3.2", "4065.59"], ... ]
    },
    ...
  ]
}
```

Key points about the shape:
- `tables` is a list of **sheets**; each sheet has `sheet_name`, `row_count`, `source_path`, `rows`.
- `rows` is a **list of cell-lists** — each row is a Python list of cell values in column order
  (strings/numbers). There are no named columns; header rows are just ordinary rows.
- Content is heterogeneous: some sheets are genuine MIC/charge/MW tables, others are raw plate-reader
  instrument dumps (`User:`, `Path:`, `Test ID:`, OD grids) that carry no extractable records.
- All 1471 packets contain the file, but only **53 have a non-empty `tables` list** (the rest are
  `"tables": []` placeholders). The driver auto-filters to the 53.

**Driver:** `extract_supp_tables.py` — for each of the 53 papers it walks every sheet, chunks the
rows, and asks the claude CLI to convert raw cells into structured AMP records
(`peptide, sequence, endpoint, value, unit, target, source_sheet, source_row, notes`). Output is
appended to `supp_recovered.tsv`; done paper_ids are checkpointed in `supp_recovered_state.json`.

### How to run (cloud shell)

From the project root `.../batch/5-team`:

```bash
# 0) auth: make sure the claude CLI is logged in in this shell (Sonnet is selected by the driver)
claude --version

# 1) preview the worklist (read-only, calls nothing)
python3 pipeline_v2/deepmine/extract_supp_tables.py --list

# 2) smoke test on a few papers first
python3 pipeline_v2/deepmine/extract_supp_tables.py --limit 3

# 3) FULL RUN (resumable) — this is the exact command to run in cloud shell:
claude --dangerously-skip-permissions -- \
  python3 pipeline_v2/deepmine/extract_supp_tables.py
```

> The driver itself shells out to `claude -p --dangerously-skip-permissions --model sonnet` for each
> chunk, so it works whether you launch it directly with `python3 ...` or wrap it in a
> `claude --dangerously-skip-permissions -- python3 ...` session. Either form is fine; the wrapped
> form above matches how the other drivers in this project are launched in cloud shell.

### Resume / progress / output

- **Resume:** just re-run the same command. Completed paper_ids in `supp_recovered_state.json` are
  skipped. Rows for a paper are appended to the TSV **only after the whole paper finishes**, then the
  paper is marked done — so an interrupted paper leaves no half-written rows and is simply retried.
- **Progress:** `python3 pipeline_v2/deepmine/extract_supp_tables.py --list` shows a `DONE` column
  and the done count; the run itself prints one line per paper (`<pid>: ok sheets=N recovered=M`).
- **Check output:** `wc -l pipeline_v2/deepmine/supp_recovered.tsv` and
  `column -t -s$'\t' pipeline_v2/deepmine/supp_recovered.tsv | less -S`.
- **Full re-extract:** delete `supp_recovered_state.json` (and optionally `supp_recovered.tsv`).

### Tunables (env vars, same convention as `claude_audit.py`)

| var | default | meaning |
|-----|---------|---------|
| `CLAUDE_MODEL` | `sonnet` | CLI model (keep Sonnet; do not use Opus for concurrency) |
| `DEEPMINE_CONC` | `6` | papers processed in parallel |
| `DEEPMINE_ROWS` | `120` | rows per claude call (chunk size) |
| `DEEPMINE_MAX_ROWS` | `3000` | max rows read per sheet (cost cap; raise to mine giant sheets) |
| `DEEPMINE_MAX_CELL` | `200` | truncate long cell text to N chars |
| `DEEPMINE_TIMEOUT` | `420` | per-call CLI timeout (seconds) |

Note the cost cap: several sheets are huge (up to ~128k rows in one paper). At the default
`DEEPMINE_MAX_ROWS=3000` those are truncated. Raise it (and expect a much longer/costlier run) to go
deeper on the big Nature-family datasets.

### Flags

- `--list` — print worklist (paper_id, sheets, rows, done?) and exit. Calls no CLI.
- `--limit N` — process at most N not-yet-done papers this run (for smoke tests / rate control).

---

## Target 2 (future driver, not yet written): mechanism non-promoted evidence

**Source:** `papers/<paper_id>/final/mechanism_ontology_record.json`, field `non_promoted_evidence[]`.

This is a **much lighter** target: only **6 papers** currently carry a non-empty
`non_promoted_evidence` list (**14 items total**), and the items are short free-text notes about
evidence the mechanism extractor saw but did not promote into a claim, e.g.:

```
"Exact curve coordinates and bar heights in figure images were not OCR-derived because source
 text/captions were sufficient for mechanism class but not exact quantitative extraction."
```

A future `extract_mech_nonpromoted.py` would follow the identical pattern (worklist = the 6 papers,
per-paper state json, Sonnet CLI, append to a `mech_nonpromoted_recovered.tsv`) and prompt the CLI to
judge each note: is there a concrete, recoverable mechanism/quantity being deferred (worth a targeted
re-extraction from the cited source), or is it a genuine dead end? Given the tiny volume this can run
single-threaded with no chunking. Not implemented here to keep this change scoped to the high-value
supplementary-tables target.
