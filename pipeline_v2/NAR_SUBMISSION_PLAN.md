# AMP Evidence Atlas → NAR submission plan

Synthesis of 9 web-research agents (2026-07-03). Companion to `AMP_ADVISOR_MVP_PLAN.md` and memory
`amp-field-needs-and-positioning`. Goal: get a source-verified, AI-ready, MCP-enabled AMP database
accepted in the **NAR Database Issue**.

## 1. Venue decision
- **Target: NAR Database Issue (D1).** Our core contribution is a *curated, provenance-rich data
  resource* ("an interface into a single database" → NAR sends this to the Database Issue). The MCP/agent
  layer, physicochemistry, and the design-advisor are *features*, not a compute-on-user-input server, so
  NOT Web Server Issue (keep that only as a fallback if the interactive advisor becomes the dominant piece).
- **Fallback: *Database* (Oxford).** Its house style explicitly welcomes "standards for curation,
  annotation best practices, annotation consistency" — data-quality-as-novelty is the perfect fit (IF ~3.6
  vs NAR ~16.6). Avoid *Scientific Data* (dataset descriptors only) and *Briefings* (reviews).
- **Hard logistics (reconfirm yearly on the live page):** free public access, **no login/registration**,
  HTTPS, **fully live & functional at review**; bulk download + stated license; ≥5-year maintenance
  commitment named in the paper; pre-submission inquiry to the Executive Editor (~July 1); new-DB
  manuscript (~Aug 15); publishes as January D1 issue. Novelty-over-rivals + a competitor benchmark are
  the hard bars; login/paywall/dead-links/no-maintenance-plan are the usual desk-rejects.

## 2. The non-redundant niche (why we get in)
Incumbents leave exactly **two axes open**, and we sit on both:
1. **Measured curation quality.** No AMP database (DRAMP 4.0, dbAMP 3.0, APD6, CAMPR4, DBAASP v3) reports a
   *measured curation precision / error rate* or an *evidence-tier* system. The precedent for reporting it
   exists outside AMP (Database 2014 "curation accuracy", UniProtKB conflict curation) — never done for AMPs.
   → We report **per-value source-verification at ~99% human precision, and the real errors we caught in
   existing AMP DBs**. This is the load-bearing, unique evidence.
2. **Agent-queryability.** MCPmed (Brief Bioinform 2026) attacks NAR norms for lacking programmatic/agent
   access — but MCPmed is a position paper with *no data-quality story*. → We are the first AMP resource
   that is **both source-verified AND natively agent-queryable via MCP**. Publishing this *in* NAR directly
   answers MCPmed's critique.

## 3. Title + 3 headline claims
Title (name first): **"[NAME]: a source-verified, provenance-tracked antimicrobial peptide atlas with
agent-queryable (MCP) access."**
1. **First AMP resource with per-value verification against the primary literature at measured ~99%
   precision — catching documented errors in existing AMP databases** (quantify: N errors / M facts, by type).
2. **Per-value provenance + explicit evidence tiers** (beyond DRAMP's single PubMed_ID / dbAMP's
   article-count curation) **+ a matched-pair SAR layer** (parent→variant→Δactivity) that no incumbent offers.
3. **FAIR, ontology-mapped, natively LLM/agent-queryable via MCP, with computed physicochemistry** —
   backed (unlike MCPmed) by verified data; one core serving both ML training data and cited QA.

## 4. Figures/tables/metrics reviewers will want (build these)
- **Competitor comparison table** vs DRAMP 4.0 / dbAMP 3.0 / APD6 / CAMPR4 / DBAASP v3 on: entry count,
  provenance granularity (per-value vs per-record vs none), evidence tiers (y/n), **measured curation
  precision**, error-catch count, MCP/API access, download formats, license. (Effectively mandatory.)
- **Quality-evidence figure** (unique): precision/recall of verification vs human ground truth (~99%) +
  breakdown of real errors found in incumbent DBs by type. No AMP paper has this.
- **Architecture/data-flow figure**: curation → source-verification → evidence tiers → ontology KG →
  MCP endpoints → (ML export + agent QA).
- **Query-output screenshot** (NAR allows, not the homepage) + an **MCP/agent walkthrough** (a design-advisor
  query answered with cited provenance).
- Coverage stats + **Zenodo/Figshare DOI'd downloadable dump** (mirror DRAMP's CC BY 4.0).
- (If advisor eval done) faithfulness / citation-recall / abstention numbers.

## 5. Ontology + one-core-two-projections (the "ML + QA combined" architecture)
No AMP-specific ontology exists → **reuse OBO ontologies, map our fields onto them.** MVV set (adopt first):
**NCBI Taxonomy** (target/strain) · **BAO** (assay/endpoint MIC/HC50/TI) · **UO** (units) · **PSI-MOD (+ChEBI)**
(modifications: D-aa/amidation/cyclization/lipidation) · **ECO** (evidence tier = experimental/predicted/
author-asserted). Later add PRO/SO/RO/OBI/GO.
- **Reify** each ActivityMeasurement and each SAR-delta as a node carrying unit/endpoint/evidence/provenance.
- **One ontology-backed core → two projections:** (a) flatten to an **ML-ready table** (canonical labels,
  harmonized units, ECO-filterable to experimental-only, homology-aware splits); (b) same triples as a **KG
  for GraphRAG/agent QA** with per-answer citations. Hybrid vector+KG retrieval (KG for multi-hop SAR,
  vector for discovery) — evidence shows hybrid beats either alone. Precedents: PrimeKG/KGARevion, Hetionet.

## 6. What to BUILD before submitting (maps to the MVP work; scope-controlled)
Priority order (value ÷ effort):
1. **Quantify the verification metric** (the headline): finalize precision/recall vs human ground truth on
   the reviewed set + tabulate the real errors caught in incumbent DBs by type. *(Mostly have it: 99% on 192.)*
2. **Evidence tiers** (`evidence_tier` = experimental-core / computed-derived / machine-recovered; = ECO). *(started)*
3. **Competitor comparison table + coverage stats.**
4. **Ontology mapping** of the 5 MVV ontologies onto our fields (a curated CSV crosswalk).
5. **Matched-pair SAR layer** (parent↔variant + Δactivity) — the differentiator + advisor engine.
6. **Public compliance**: free/no-login/HTTPS, Zenodo DOI dump + license, docs/help, maintenance statement.
7. **(Advisor MVP + eval)** — strengthens the paper but the DB paper can ship first; advisor can be a
   second paper (Web Server / Bioinformatics) or a highlighted feature.
8. **Spot-check** the "incumbents don't report precision/evidence tiers" claim in full text before making it
   load-bearing.

## 7. Timeline (align to NAR windows — reconfirm dates)
- **Now → pre-submission window:** lock quality metrics + evidence tiers + comparison table + ontology
  crosswalk + public compliance + DOI dump. Send pre-submission inquiry (~July 1).
- **→ manuscript deadline (~Aug 15):** write 4–5 pp (name-first title, URL in abstract, graphical abstract,
  the figures above), resource fully live for review.
- **Parallel / next:** matched-pair SAR + advisor MVP + eval → either fold into revision or a second paper.

## 8. Risks
- **Novelty bar** is the #1 killer — the comparison table + measured-quality figure must make "substantially
  better than all rivals" undeniable. Our two open axes are the argument.
- **Maintenance credibility** — name an institution + 5-year commitment (the current 1-core VPS is a demo;
  the lab server is the real host — state that).
- **The precision-claim caveat** — verify incumbents truly don't report it before asserting first-ness.
- 2026 "flexibility on free access in exceptional cases" is new — do NOT rely on it; design for full open access.

## Key sources
NAR Database criteria/scope (academic.oup.com/nar/pages/Criteria_Scope, /ms_prep_database); NAR 2026 editorial
54(D1):D1; DRAMP 4.0 (NAR 53(D1):D403), dbAMP 3.0 (53(D1):D364), APD6 (54(D1):D363), CAMPR4 (51(D1):D377),
DBAASP v3 (49(D1):D288); MCPmed (Brief Bioinform 27(1):bbag076); Curation accuracy (Database 2014, PMC4207230);
FAIR (Sci Data 2016); Ten Simple Rules for Public Biological Databases (PLOS Comput Biol 2016); BAO/ECO/PSI-MOD/
ChEBI/PRO (OBO Foundry); PrimeKG/KGARevion (arXiv 2410.04660); RAG-vs-GraphRAG eval (arXiv 2502.11371).
