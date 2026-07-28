# PMC11735859 Worker-1 Intake Report

Generated at: 2026-07-08T07:32:05Z

## Scope

This report covers only the worker-1 material intake lane for `PMC11735859`.
It uses the local packet and paper source files only. It does not assign any
database-record verification status and does not claim publication-grade
completion.

## Paper Metadata

- Title: Deep eutectic solvent enhances antibacterial activity of a modular lytic enzyme against Acinetobacter baumannii
- Journal/year: Scientific Reports, 2025
- DOI: `10.1038/s41598-024-80440-z`
- PMID: `39814769`
- PMCID: `PMC11735859`

The packet manifest and XML front matter carry the DOI, PMID, PMCID, title,
journal, and year. `paper_meta.json` is staging metadata and has null
title/year/DOI fields, so downstream workers should prefer the packet manifest
and XML/PDF locators for bibliographic metadata.

## Source Inventory

- XML: `papers/PMC11735859/source/paper.xml`, 128101 bytes, SHA-256 `42638f2168d302c8ddb0e34d359f1a2dbeed3892d9a6734d4e65c03ea7fa7c4f`.
- PDF: `papers/PMC11735859/source/paper.pdf`, 3567801 bytes, SHA-256 `4f2dd51dd05b29c19174591813a1888897431577ee5504a458be478c25a05e19`.
- Paper metadata: `papers/PMC11735859/source/paper_meta.json`, 1300 bytes, SHA-256 `125efccda1d1f9b32bf0463b83d755970274712d12bd705cee9d981707a10e5f`.
- Supplement: `papers/PMC11735859/source/supplementary/41598_2024_80440_MOESM1_ESM.docx`, 1169496 bytes, SHA-256 `bdeaa0aea78510b64c9754a3fe6cef3c1ce0f59e8456d11cac383f6cc7475ab8`.

The packet raw copies have matching SHA-256 hashes for all four staged assets.
The original source root declared by the packet is
`/mnt/d/work/抗菌肽/数据库/DBAASP/analysis/runtime/oa_200paper_batch_20260413_round9/source_pool/PMC11735859`.
No PMC OA package path is declared; the packet records `package_source` /
`pmc_oa_package` as null.

## Extracted Surfaces

- XML sections: 134 total, including 2 table-wrap locators, 11 fig locators,
  and 14 captions.
- PDF text: 18 page records.
- Supplementary index/text: 1 DOCX file, text extracted.
- Supplementary structured tables: 0; `supplementary_tables.json` states that
  table normalization is a rework item if needed.
- Locator index: 153 locators.
- Extraction errors: 0 recorded.

Important handoff surfaces include `xml:table-wrap:1` for the MLE-15 component
and sequence table, `xml:table-wrap:2` for the MIC table, and
`supp:41598_2024_80440_MOESM1_ESM.docx` for supplementary table/figure text.

## Database Provenance

The local authoritative match report says the DBAASP/merged index inputs exist,
but linked authoritative rows are all empty for this paper:

- linked article records: 0
- linked assay records: 0
- linked sequence records: 0
- linked literature records: 0

Five DBAASP Codex fallback rows are present in
`packets/PMC11735859/database/dbaasp_machine_extracted_rows.jsonl`. They are
candidate machine evidence only. They should be re-opened against primary
packet locators before any downstream database, activity, or adjudication
decision.

## Cautions And Blockers

No worker-1 blocking material gap was found in the declared packet. Cautions:

- No OA package path is staged or declared.
- Supplementary DOCX text is present, but structured supplementary table rows
  are not normalized.
- Authoritative DBAASP/merged linked rows are absent; only machine fallback rows
  exist.
- Analysis remains queued and must be performed by workers 4-6 before any
  reliable-result or publication-grade claim.

## Handoff Decision

Worker-1 intake is complete for material inventory with cautions. No
`analysis_status.json` update was made because the intake status did not change
from a handoff perspective; the packet remains `analysis_queued` for downstream
source-reviewed analysis.
