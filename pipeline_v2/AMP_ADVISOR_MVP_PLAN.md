# AMP Activity-Improvement Advisor — MVP Plan

*A source-verified, LLM-powered assistant that answers: "How do I improve the activity/selectivity of
this antimicrobial peptide — which strategies, which modifications, and what precedent cases exist?"*

Built on the AMP Evidence Atlas (source-verified paper corpus + per-value provenance + MCP interface).
Scope-controlled first version. Grounded in a 7-agent web-research round (2026-07-03; see project memory
`amp-field-needs-and-positioning`).

---

## 0. The decisions that shape the MVP (from the research — non-negotiable)

1. **Retrieve-and-cite, do NOT predict.** Generic LLMs predict AMP activity/toxicity poorly and
   irreproducibly (RSC Med Chem 2024, PMC11187562). The advisor must answer from retrieved, cited
   evidence and **refuse when the corpus has none** — never invent SAR from parametric memory.
2. **What is groundable vs not.** Design *rules* (charge/hydrophobicity/helicity/µH optima; selectivity
   levers) are well-grounded and quantitative → the advisor gives **directional, rule-based, case-cited
   advice**. Precise **per-mutation ΔMIC prediction is NOT data-grounded** (no harmonized parent→variant
   MIC corpus exists) → do not promise exact fold-changes.
3. **The differentiator = a matched-pair SAR layer.** No AMP database maintains parent↔variant/analog
   links (DRAMP makes every modified peptide a new independent entry). No AMP-specific citation-grounded
   literature-QA assistant exists. Both niches are empty → this is our defensible, publishable angle.
4. **Architecture: MCP structured-tools backbone + thin agent.** We already did the hard part
   (extraction + provenance + MCP). CLADD (arXiv:2502.17506) shows off-the-shelf LLMs + structured
   grounding beats fine-tuned models with no training. Query numeric activity via tools/SQL (never
   vector-embed the numbers); use vectors only to discover relevant papers.
5. **Eval from day one.** RAGAS faithfulness + ALCE citation recall/precision + a ~150-question
   abstain-aware gold set built from our own verified records.

---

## 1. What the MVP IS (and is NOT)

**IS:** given a peptide (sequence + optional target organism), return
- **Diagnosis**: computed physicochemistry (charge, hydrophobicity, µH, length, helicity proxy) vs. the
  literature optima → "your peptide is at charge +3 / hydrophobicity high; likely under-active + hemolytic".
- **Ranked improvement strategies**: each = a cited rule + expected direction on MIC and on selectivity/TI
  + the trade-off (e.g. "insert a Lys in the hydrophobic-face center → raises TI, precedent up to ~700×;
  little MIC cost").
- **Precedent cases**: real peptides from our corpus where that modification changed activity, with the
  actual MIC/hemolysis/TI numbers **and a link to the source paper/table** (supporting *and* contradicting).

**IS NOT (deferred):** generative de-novo design; precise ΔMIC regression; full 431k-row supplementary
mining; structure prediction; clinical/PK layer; cross-DB ID mapping. (All are Phase-2+ / separate work.)

---

## 2. Build phases (priority = value ÷ effort, highest first)

### Phase 0 — Foundation (mostly DONE)
- Source-verified corpus on rc2, MCP live (9 tools), physicochemistry computed, human verdicts surfaced.
- Add an explicit `evidence_tier` field (experimental-core / computed-derived / machine-recovered) so the
  advisor can filter and label confidence. **Effort: S.**

### Phase 1 — The two data assets that make the advisor possible (HIGHEST VALUE)

**1a. Matched-pair SAR layer** (the unique differentiator, and the "which modifications / precedent
cases" engine).
- Within each paper (and later cross-paper), align peptide sequences to find **parent↔variant pairs**
  (single- or multi-residue substitutions, terminal mods, D-substitution, truncation, cyclization…).
- For each pair compute: Δcharge, Δhydrophobicity, ΔµH, Δlength + **ΔMIC / Δhemolysis / ΔTI** (from our
  activity records, same organism/assay where possible) + **modification_type** + provenance to both source rows.
- Output table `sar_pairs(parent_id, variant_id, modification_type, delta_features, delta_activity, target, source, confidence)`.
- Method: deterministic sequence alignment for pairing (Python) + our activity/physchem data; use the
  **dual-model CLI (codex+claude)** only where the modification/effect must be read from prose/tables.
- **Effort: M. Value: very high** (nobody has this; directly powers the core use-case; publishable).

**1b. Design-rules knowledge module** (the "common strategies" content).
- Encode the well-grounded rules as structured, **cited** knowledge cards: charge optima (natural ~+5,
  engineered +7–8; cap before hemolysis spike), hydrophobicity inverted-U, µH≥~0.2, helicity↔hemolysis,
  length 10–50; selectivity levers ranked (non-polar-face Lys ≈ up to 700–980× TI; D-substitution;
  reduce hydrophobicity from the toxic end; polar-face charge; helix-breakers). Each card carries its
  citations (Hodges/Shai/Dathe literature — already gathered).
- Plus a `diagnose_peptide()` that scores a given sequence against these ranges using our physchem.
- **Effort: S–M. Value: high** (this is the "strategies" half of the answer, and it's citable).

### Phase 2 — The advisor agent (THIN — leverages existing MCP)
- Add/confirm MCP tools: `analyze_peptide(seq)` (physchem + rule diagnosis), `find_precedents(modification, target)`
  (queries `sar_pairs`), `search_records`, `get_provenance`, `semantic_search_papers` (vector discovery only).
- Thin **ReAct / tool-calling agent** (Claude Opus/Sonnet or codex via your tokens) with:
  **cite-then-answer**, **refuse when tools return nothing**, surface supporting *and* contradicting cases.
- Delivery: an MCP tool `improve_peptide(seq, target)` + a minimal chat UI page on the Atlas.
- **Effort: M. Value: high** (this is the product surface).

### Phase 3 — Eval & hardening
- ~150 abstain-aware gold Q&A built from our verified records (we have ground truth), e.g. "which
  C-terminal amidation precedents improved MIC vs *S. aureus*?".
- Metrics: RAGAS faithfulness, ALCE citation recall/precision, accuracy/precision-with-abstention (LitQA2 style).
- Cap agent tool-iterations (cost); calibrate LLM-judge against a human-labeled subset.
- **Effort: M. Value: high** (this is what makes it publishable and trustworthy).

---

## 3. Resource mapping (your ML env + codex/chatgpt/claude/API tokens)

- **codex + claude CLIs (dual-model)** → Phase 1a/1b structured extraction where prose/tables must be
  read (reuse `pipeline_v2/deepmine/extract_supp_dual.py` pattern + cross-review confidence). Run in your
  cloud shell (codex ~5 min/paper).
- **ML environment** → physchem (done), embeddings for the optional vector discovery layer, running the eval.
- **API tokens (Claude/OpenAI)** → power the advisor agent + RAGAS/ALCE LLM-judge eval.
- **Atlas VPS / lab server** → host the advisor MCP tool + chat UI (VPS is 1-core/1GB — keep the advisor
  stateless calling the LLM API; heavy batch extraction runs on the lab/cloud-shell side).

---

## 4. Suggested timeline (scope-controlled MVP)
- **Week 1:** Phase 0 (evidence_tier) + Phase 1b (design-rule cards + diagnose_peptide). Demoable rule-based diagnosis.
- **Week 2:** Phase 1a matched-pair SAR extraction (start within-paper pairs; the high-yield subset).
- **Week 3:** Phase 2 advisor agent + MCP tools + minimal UI.
- **Week 4:** Phase 3 eval set + metrics + hardening. → publishable MVP.

## 5. Why this is defensible / publishable
- Fills TWO empty niches: (a) first source-verified **matched-pair SAR** layer for AMPs; (b) first
  **citation-grounded AMP design assistant** (retrieve-and-cite, not predict).
- Rides the validated trends: AI-ready data foundation (Bridge2AI/FAIR), MCP-for-bio (MCPmed, Brief
  Bioinform 2026), RAG-to-cut-hallucination.
- Ships with quantified trust metrics (faithfulness, citation recall, abstention) + the DB-error-catch story.

## Key sources
PaperQA2 (arXiv:2409.13740); CLADD (arXiv:2502.17506); Anthropic Contextual Retrieval; RAGAS (arXiv:2309.15217);
ALCE (arXiv:2305.14627); RSC Med Chem 2024 (PMC11187562, GPT predicts AMP poorly); Hodges charge/hydrophobicity
(PMC2761230, PMC1855469); selectivity levers Jiang/Hodges 2014 (PMC4014698); Gagat 2024 (PMC11476776);
dmSLAY (PMC10402124); Hilpert 2005 (Nat Biotechnol); GRAMPA (bioRxiv 2019); DBAASP NAR 2021; MCPmed (bbag076).
