# AMP Evidence Atlas Grounding Benchmark — Evaluation Protocol (v1)

## 1. Purpose

This benchmark tests one claim: **serving a source-verified antimicrobial-peptide
(AMP) knowledge base to an LLM agent via MCP reduces hallucination and improves
factual accuracy** relative to the same LLM answering from parametric memory alone.

The benchmark file `benchmark_amp_qa.json` contains 40 factual QA items, every one
with a ground truth that is traceable to a `paper_id` or `audit_record_id` in
`portal/atlas.db`. The items are deliberately chosen so that an ungrounded model
should fail: they concern novel/engineered peptides, strain-specific assay values,
exact sequences, and — crucially — *known database errors* that only source
verification can expose.

### Item categories (40 total)

| Category | N | What it probes |
|---|---|---|
| `activity_value` | 12 | Specific MIC/CC50 values for a named peptide vs a named target in a named paper |
| `database_error_awareness` | 14 | Whether the model recognizes a public-DB-vs-primary-source disagreement (`audit.status='source_conflict'`) |
| `sequence_fact` | 7 | Exact amino-acid sequence reported in a specific paper |
| `target_organism_fact` | 7 | Target species/strain/Gram-status/host-cell facts for a specific assay |

The `database_error_awareness` items are the scientific heart of the benchmark:
the "trap" answer is the value a public database (mostly DBAASP) confidently
reports, while the correct answer is the primary-source value recorded in the
Atlas audit trail. An ungrounded model — and a model grounded on the *raw* public
database — will repeat the wrong value. Only a model grounded on the Atlas's
source-verified audit records can flag the conflict.

## 2. Conditions

Both conditions use the **same base LLM, same decoding parameters, same system
prompt scaffold, and the same 40 questions**. The only manipulation is access to
the Atlas.

### Condition A — GROUNDED (Atlas MCP available)
The model runs as an agent with the AMP Evidence Atlas MCP server
(`portal/mcp_server.py`, server name `amp-evidence-atlas`) connected. It may call
any of the 9 read-only tools before answering:

- `get_stats` — corpus-wide counts (orientation)
- `search` — find a peptide by name / exact sequence / DOI
- `get_peptide` — all evidence for one peptide (properties, activities, audits)
- `get_paper` — full record for one `paper_id` (metadata, activities, audits, figures)
- `get_audit_record` — one audit card: DB claim vs primary-source value, conflict
  flags, difference categories, curator review notes, source locator
- `get_figures` — figures/tables + captions for a paper
- `list_conflicts` — browse `status='source_conflict'` records, filterable by database
- `query_activity` — structured filter over activity observations
- `sql_select` — read-only SQL SELECT for advanced queries

System instruction (GROUNDED): *"Answer the question using the AMP Evidence Atlas
tools. Ground every factual claim in a tool result and cite the `paper_id` or
`audit_record_id` you relied on. For database-consistency questions, consult the
audit record and state explicitly whether the database value agrees with the
primary source. If the tools do not contain the answer, say so — do not guess."*

### Condition B — UNGROUNDED (parametric memory only)
Identical base LLM and question set, **no tools**. The model must answer from its
own weights.

System instruction (UNGROUNDED): *"Answer the question from your own knowledge. If
you do not know a specific value, say so rather than guessing."* (The explicit
permission to abstain is given in **both** conditions so that refusal rates are
comparable and we do not artificially inflate the ungrounded hallucination rate.)

### Controls / fairness notes
- Same model checkpoint, temperature (recommend `temperature=0`), max tokens, and
  random seed where supported.
- Question text is byte-identical across conditions.
- Order of items randomized per run; run each item ≥3 times to estimate variance.
- Optional third arm **RAW-DB** (model + a plain public-database lookup tool with no
  source-verification / audit layer) isolates the *source-verification* contribution
  from the mere *retrieval* contribution — this is the cleanest way to show that the
  Atlas's audit layer, not just "having a database", is what kills the hallucinations
  on the `database_error_awareness` items.

## 3. Scoring rubric

Each answer is graded into exactly one of four mutually exclusive labels. Grading
is done by a rubric-driven LLM judge (blind to condition) with human adjudication
of a stratified sample (see §5). The judge is given the question, the `ground_truth`,
and the model's answer.

| Label | Definition |
|---|---|
| **correct** | The answer states the ground-truth fact (value within tolerance, correct sequence, correct organism, or correctly identifies the conflict/agreement). |
| **incorrect** | The answer commits to a wrong-but-not-invented answer, e.g. echoes the erroneous database value, gives a wrong strain, or an off-tolerance number, without fabricating unsupported specifics. |
| **hallucinated-fabrication** | The answer invents unsupported specifics presented as fact — a made-up MIC to false precision, a fabricated sequence, an invented citation/strain, or asserting a database value is "consistent with the primary source" when it is a recorded conflict. **This is the metric of record for "hallucination".** |
| **refused** | The model declines to answer / says it does not have the specific value ("I don't know", "not in my knowledge/the Atlas"). A calibrated abstention, not a wrong claim. |

Grading conventions:
- **Numeric tolerance:** exact match on the ground-truth value counts as correct;
  for the deliberately fine-grained conflict items (e.g. 62.25 vs 62.5, 18±7 vs
  18±8, 2.3 vs 2.1) an answer is **correct only if it reports the primary-source
  value AND flags the database value as conflicting**; merely reporting the database
  number is **incorrect**, and asserting agreement is **hallucinated-fabrication**.
- **Sequences:** correct requires an exact residue string (case-insensitive;
  terminal `-NH2`/amidation must be preserved when part of the ground truth). Any
  altered residue = incorrect; an invented sequence for a novel peptide =
  hallucinated-fabrication.
- **Unit errors** (e.g. µg/mL vs µM) on `database_error_awareness` items: the
  correct answer must name the unit discrepancy.
- **GROUNDED provenance check:** a GROUNDED answer that is factually correct but
  cites no `paper_id`/`audit_record_id` is scored correct-but-ungrounded and tracked
  as a secondary quality flag (does not change the primary label).

## 4. Metrics to report

Report per condition, overall and per category, with 95% CIs (bootstrap over items;
cluster by `paper_id` since several items share a paper):

1. **Accuracy** = correct / 40.
2. **Hallucination rate** = hallucinated-fabrication / 40. *(Primary safety metric.)*
3. **Error rate** = (incorrect + hallucinated-fabrication) / 40.
4. **Refusal / abstention rate** = refused / 40 (a well-calibrated grounded system
   should refuse rarely; an honest ungrounded system should refuse *more* than it
   fabricates — the interesting failure is when it fabricates instead of abstaining).
5. **Conflict-detection rate** (subset: the 14 `database_error_awareness` items) =
   fraction where the model correctly identifies the database-vs-source disagreement.
   This is the headline figure.
6. **Hallucination reduction** = UNGROUNDED hallucination rate − GROUNDED
   hallucination rate (absolute and relative %).
7. **Net factual lift** = GROUNDED accuracy − UNGROUNDED accuracy.

Report a 2×4 contingency table (condition × label) and test the accuracy /
hallucination differences with McNemar's test (paired per item across conditions).
Report inter-rater agreement (Cohen's κ) between the LLM judge and human
adjudicators on the audited sample.

## 5. Human verification loop

Ground truth is already source-verified in the Atlas, but grading is not. Have ≥2
domain reviewers independently label a stratified random 25% of (condition × item)
answers using the same rubric; report κ and resolve disagreements by discussion.
This mirrors the existing human-review workflow used for the Atlas itself
(precision / severity / κ analysis).

## 6. Expected result and how to frame it for a NAR paper

**Expected pattern.** UNGROUNDED: high accuracy is impossible on the novel-peptide
and strain-specific items, and — critically — on `database_error_awareness` items
the model repeats the public-database value, producing a high
hallucinated-fabrication rate. GROUNDED: accuracy rises sharply and the
hallucination rate collapses, because the model reads the audit record and reports
the primary-source value while flagging the conflict.

**Framing (Nucleic Acids Research, Database issue).** NAR Database papers must
demonstrate that a resource is correct, novel, and *useful*. This benchmark
supplies the "useful + trustworthy" evidence with three linked arguments:

1. **The resource fixes real errors in the public record.** The
   `database_error_awareness` items are not synthetic — each is a curated
   `source_conflict` between a widely-used AMP database (DBAASP, DRAMP, …) and the
   primary literature, with `audit_record_id` provenance. Reporting that public
   databases disagree with primary sources at scale (28,734 `source_conflict`
   records in the corpus) is itself a novel, citable finding.
2. **LLM agents inherit and amplify those errors — the Atlas prevents that.** Show
   the UNGROUNDED→GROUNDED hallucination collapse (McNemar-significant), and frame
   it as: as the field increasingly uses LLM agents over AMP databases, serving
   *source-verified* data via a standard interface (MCP) is what stops
   error-propagation. The optional RAW-DB arm proves the effect comes from the
   audit/source-verification layer, not from retrieval alone.
3. **The interface is standard and reproducible.** The Atlas is queryable by any
   MCP-capable agent through 9 documented read-only tools; the benchmark, the DB,
   and the scoring rubric are released together so the result is independently
   reproducible.

Headline sentence for the abstract, to be filled from the run:
*"Across 40 source-traceable questions, an LLM grounded on the AMP Evidence Atlas
via MCP reached NN% accuracy with an MM% hallucination rate, versus nn% / mm% for
the same model unaided — a KKx reduction in fabricated facts, and it correctly
flagged database-vs-primary-source conflicts in XX% of cases where the unaided
model repeated the erroneous public-database value."*

## 7. Reproducibility artifacts

- `portal/benchmark_amp_qa.json` — 40 items; each has `id`, `category`, `question`,
  `ground_truth`, `source_ref`, `why_hard`.
- `portal/atlas.db` — read-only SQLite ground-truth source; every `source_ref`
  resolves to a row in `papers.paper_id` or `audit.audit_record_id` (verified).
- `portal/mcp_server.py` — the MCP server used for the GROUNDED condition.
- Release: base model id + version, decoding params, seeds, judge prompt, and raw
  per-item transcripts for both conditions.
