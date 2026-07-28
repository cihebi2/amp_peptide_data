# AMP Evidence Atlas Grounding Benchmark — v1.0 Pilot Protocol

## 1. Status and purpose

`benchmark_amp_qa.json` is a **40-item pilot**, not a load-bearing validation of
Atlas curation quality. It tests whether an LLM can answer source-specific AMP
questions more accurately and recognize recorded database–primary-source
conflicts when it can query the Atlas.

The benchmark must not describe every `source_conflict` as a confirmed database
error. Human validation of Atlas extraction and adjudication is a separate study.

All reported denominators must be read from the frozen v1.0 manifest and the
portal database `metadata`/`stats` tables at run time. Do not copy historical
RC1/RC2 counts into benchmark prose.

## 2. Pilot item set

| Category | N | Target |
| --- | ---: | --- |
| `activity_value` | 12 | Paper-specific MIC/CC50 values |
| `database_error_awareness` | 14 | Recorded `source_conflict` audit rows |
| `sequence_fact` | 7 | Exact paper-specific sequences |
| `target_organism_fact` | 7 | Species, strain, host-cell or Gram-status facts |

Every `source_ref` must resolve in the canonical v1.0 portal projection:

- conflict items: `audit.audit_record_id`;
- other items: `papers.paper_id` or an explicitly documented evidence-row id.

## 3. Required three-arm comparison

The following three conditions are mandatory. They use the same model checkpoint,
system-prompt scaffold, decoding parameters and byte-identical question text.

### A. NO_RETRIEVAL

No tools. The model answers from parametric memory and may abstain.

### B. RAW_DB

The model can query a frozen snapshot of the relevant source database record, but
cannot see Atlas primary-source values, conflict labels or curator interpretation.
This arm separates retrieval benefit from evidence-audit benefit.

### C. ATLAS

The model can use the read-only Atlas MCP tools. For database-consistency
questions it must cite an `audit_record_id`, report both claims where available,
and state the audit status without upgrading it to a human-confirmed error.

RAW_DB is not optional: without it, the experiment only establishes that
retrieval helps, not that the evidence-audit layer adds value.

## 4. Run controls

- Use at least three model families for the expanded benchmark.
- Temperature 0 where supported; otherwise publish all decoding parameters.
- Randomize question order and use at least three repeats per item.
- Preserve raw prompts, tool traces, responses, model version and run timestamp.
- Cluster uncertainty estimates by paper because several items share a paper.
- Record whether a model predates or postdates each source; do not claim that an
  item is absent from model pretraining unless independently demonstrated.

## 5. Scoring

Primary mutually exclusive labels:

| Label | Definition |
| --- | --- |
| `correct` | Ground-truth fact reported within the predeclared tolerance |
| `incorrect` | A committed but unsupported/wrong answer |
| `hallucinated_fabrication` | Invented specific value, sequence, strain or provenance |
| `refused` | Explicit abstention without unsupported factual commitment |

Secondary flags:

- missing required provenance;
- correct value but wrong unit or target;
- conflict detected but claims reversed;
- overclaiming a recorded conflict as a confirmed database error.

Numeric tolerances and sequence/modification rules must be declared before runs.
For conflict items, merely repeating the raw database value is not correct.

Report accuracy, error, fabrication, abstention, conflict-detection and provenance
rates by arm and category, with cluster-bootstrap 95% confidence intervals.
Paired comparisons should use a paired test such as McNemar where applicable.

## 6. Human blind review

The answer grader must be blind to experimental arm. At least two reviewers
independently score a predeclared stratified sample, report agreement and send
disagreements to adjudication. An LLM judge may assist but is not the gold
standard.

## 7. Expansion before manuscript use

The 40 items are retained as a smoke-test set. Before using the benchmark as a
major resource-utility result:

1. expand to approximately 150–300 questions;
2. balance databases, endpoint types, natural/designed peptides and conflict types;
3. limit repeated papers and close sequence analogues;
4. include agreement controls as well as conflict cases;
5. freeze RAW_DB snapshots with versions and checksums;
6. reserve a hidden human-reviewed test partition;
7. run multiple model families and publish all transcripts.

The benchmark belongs in the Evidence Atlas resource paper as a supporting
utility experiment; it is not presently a separate “Agent paper”.

## 8. Reproducibility artifacts

- `portal/benchmark_amp_qa.json` — 40-item pilot
- `portal/atlas.db` — canonical v1.0 public projection
- `portal/mcp_server.py` — read-only Atlas tools
- frozen RAW_DB snapshots and checksums — required before the full run
- model/run manifests, raw traces and blind human labels — required for reporting
