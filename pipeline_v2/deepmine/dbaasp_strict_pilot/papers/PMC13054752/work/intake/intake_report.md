# Worker-1 Intake Report - PMC13054752

Generated: 2026-07-08T08:55:18Z

## Scope

- Worker lane: `worker-1` / intake.
- Paper reviewed: `PMC13054752` only.
- Internet access: not used.
- Write scope used: `papers/PMC13054752/work/intake/`.
- `analysis_status.json` was not changed; it remains `analysis_queued`.
- No `source_verified`, database acceptance, mechanism, or publication-grade claims are made in this lane.

## Paper Identity

Packet and database manifests identify the paper as:

- Title: Analysis of the virulence potential, ability to form biofilms and susceptibility to bacteriocins of Staphylococcus aureus strains isolated from livestock and wildlife
- Journal/year: Journal of Veterinary Research, 2026
- DOI: `10.2478/jvetres-2026-0005`
- PMID: `41953746`
- PMCID: `PMC13054752`
- Publisher ID: `jvetres-2026-0005`

Cross-check evidence:

- `packet_manifest.json` and `database_source_manifest.json` agree on DOI, PMID, PMCID, title, journal, and year.
- `paper.xml` article metadata contains PMCID `PMC13054752`, PMID `41953746`, DOI `10.2478/jvetres-2026-0005`, 2026 publication metadata, page count 11, and `pmc-prop-has-supplement=yes`.
- `pdf_text.jsonl` page 1 contains the DOI and the same title surface.
- `paper_meta.json` is staging metadata only and has `title`, `year`, and `doi` as null; use packet/XML metadata as canonical for this packet.

## Source Assets

Paper source assets staged under `papers/PMC13054752/source/`:

| Asset | Path | Size | SHA-256 |
| --- | --- | ---: | --- |
| XML | `paper.xml` | 199407 | `cbb5d13bc4e2de7f800aa8ad23130fa0733bdd773aac7d07d3cf48501495e6b5` |
| PDF | `paper.pdf` | 754349 | `2aeb084df541d68d66d9b3d52f844cf187a2203b1391a3364bc5ce76cc5c3c59` |
| Metadata | `paper_meta.json` | 1304 | `89c9be5909df23b174bcfc86a079a82e26577da13c5ae8d3b378c5c2309193bc` |
| Supplement PDF | `supplementary/jvetres-2026-0005_sm.pdf` | 98827 | `c8a90cc09156c8ec02b377c193428d342ec2462e5a18a40ad8cc8d0163b19d24` |

The packet raw mirror has same-size copies at:

- `packets/PMC13054752/raw/paper.xml`
- `packets/PMC13054752/raw/paper.pdf`
- `packets/PMC13054752/raw/paper_meta.json`
- `packets/PMC13054752/raw/supplementary_original/jvetres-2026-0005_sm.pdf`

The manifest declares the original local source root as `/mnt/d/work/抗菌肽/数据库/DBAASP/analysis/runtime/oa_200paper_batch_20260413_round14/source_pool/PMC13054752`.

## Extracted Surfaces

- XML: `extracted/xml_sections.json`, 131 sections, no XML extraction errors.
- XML tag counts: 1 abstract, 50 article-title, 9 captions, 2 figures, 48 paragraphs, 15 sections, 6 table-wraps.
- PDF text: `extracted/pdf_text.jsonl`, 11 pages.
- PDF/XML table artifact: `extracted/pdf_tables.json`, 6 tables.
- Figure/caption artifact: `extracted/figure_captions.json`, 11 entries including `xml:fig:1` and `xml:fig:2`.
- Supplement index: one PDF, `jvetres-2026-0005_sm.pdf`, 98827 bytes, one text page reported.
- Supplement generic text: `extracted/supplementary_text.jsonl` is empty.
- Supplement OCR text: `extracted/ocr/jvetres-2026-0005_sm.pdf_text.jsonl` has one line/page and contains Supplementary Table S1 text.
- Supplement table-normalized output: `extracted/supplementary_tables.json` has zero tables and notes that spreadsheet/table normalization is a rework item if needed.
- Locator index: `locators/locator_index.json`, 142 locators: 131 from XML sections and 11 from PDF text.
- Citation map: present, but explicitly marked not normalized in this DBAASP strict pilot.

Packet extraction status is `material_extracted_complete` with `error_count: 0`. No open rework tickets were present in `rework/rework_requests.jsonl`.

## Database Provenance

Database snapshot files are present under `packets/PMC13054752/database/`.

Authoritative match report:

- `dbaasp_article_refs`: path exists
- `dbaasp_assay_refs`: path exists
- `dbaasp_peptides_summary`: path exists
- merged DBAASP assay, sequence/literature, availability, and sequence inputs: paths exist
- linked authoritative rows: 0 article, 0 assay, 0 sequence, 0 literature
- `source_record_links_present`: false

Candidate machine evidence:

- `dbaasp_machine_extracted_rows.jsonl`: 16 rows
- `dbaasp_review_queue_rows.jsonl`: 16 rows
- `dbaasp_empty_done.jsonl`: 0 rows
- `codex_session_audit.jsonl`: 2 sessions

Strict interpretation: the 16 Codex fallback rows are candidate machine evidence only. They include sampled `missing_sequence` flags and must not be treated as primary-source or authoritative DBAASP-linked rows.

## Cautions And Gaps

- OA package: no `package_source` is declared and no `raw/oa_package` path is present. This is an explicit strict-gate caution for any downstream claim that OA package members were inspected.
- `paper_meta.json`: staging metadata is minimal/null for title/year/DOI; packet/XML metadata should be used.
- Supplement text routing: `supplementary_text.jsonl` is empty, but OCR text exists under `extracted/ocr/`.
- Supplement table normalization: Supplementary Table S1 is not table-normalized; downstream workers should request targeted table extraction if row-level supplement data are needed.
- Citation map: present but not normalized.
- Authoritative database linkage: zero linked DBAASP/merged rows; worker-4 must not infer source linkage from Codex fallback rows.

## Handoff Status

Worker-1 intake is source-reviewed complete for the local packet inventory, with the cautions above. This is a material/intake handoff only, not analysis acceptance and not publication-grade completion.
