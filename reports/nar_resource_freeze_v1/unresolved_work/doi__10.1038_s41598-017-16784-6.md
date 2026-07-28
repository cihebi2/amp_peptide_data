# Unresolved DBAASP records audit: doi__10.1038_s41598-017-16784-6

## Scope

- Paper: `doi__10.1038_s41598-017-16784-6`
- Task: inspect target paper `paper_packets/` and `papers/` source/final/work materials for the 24 DBAASP `unresolved_record` rows.
- Final edit decision: no edit to `papers/doi__10.1038_s41598-017-16784-6/final/database_record_verification.json`; local primary/source packet evidence does not support a more accurate source-verified or source-conflict status for these rows.

## Current unresolved set

The final database verification file contains 74 record audits with this status summary:

- `source_verified`: 26
- `source_conflict`: 24
- `unresolved_record`: 24

The 24 unresolved DBAASP rows are duplicate audit surfaces for 12 DBAASP synergy assay IDs:

| Source table | Count | DBAASP source_record_id range | Organisms | Evidence need |
| --- | ---: | --- | --- | --- |
| `linked_assay_records.jsonl` | 12 | `495`-`506` | `Staphylococcus aureus 547582`; `Pseudomonas aeruginosa 3320` | row-level checkerboard MIC/FICI values |
| `linked_experiment_records.jsonl` | 12 | `495`-`506` | `Staphylococcus aureus 547582`; `Pseudomonas aeruginosa 3320` | same rows mirrored as experiment records |

The linked DBAASP assay rows carry FICI values for six antibiotic combinations for each organism:

- `S. aureus 547582`: gentamicin `1.02`, tobramycin `1.06`, ciprofloxacin `1.13`, oxacillin `0.52`, piperacillin `0.53`, levofloxacin `1.13`.
- `P. aeruginosa 3320`: gentamicin `0.53`, tobramycin `0.52`, ciprofloxacin `1.01`, oxacillin `0.52`, piperacillin `0.52`, levofloxacin `1.01`.

## Evidence checked

Target paper materials checked:

- `paper_packets/doi__10.1038_s41598-017-16784-6/raw/paper.xml`
- `paper_packets/doi__10.1038_s41598-017-16784-6/raw/paper.pdf`
- `paper_packets/doi__10.1038_s41598-017-16784-6/raw/supplementary_original/`
- `paper_packets/doi__10.1038_s41598-017-16784-6/locators/locator_index.json`
- `paper_packets/doi__10.1038_s41598-017-16784-6/extracted/xml_sections.json`
- `paper_packets/doi__10.1038_s41598-017-16784-6/extracted/pdf_text.jsonl`
- `paper_packets/doi__10.1038_s41598-017-16784-6/extracted/supplementary_index.json`
- `paper_packets/doi__10.1038_s41598-017-16784-6/extracted/supplementary_text.jsonl`
- `paper_packets/doi__10.1038_s41598-017-16784-6/extracted/supplementary_tables.json`
- `paper_packets/doi__10.1038_s41598-017-16784-6/database/linked_assay_records.jsonl`
- `paper_packets/doi__10.1038_s41598-017-16784-6/database/linked_experiment_records.jsonl`
- `paper_packets/doi__10.1038_s41598-017-16784-6/analysis/database_record_audit.json`
- `paper_packets/doi__10.1038_s41598-017-16784-6/final/database_record_verification.json`
- `papers/doi__10.1038_s41598-017-16784-6/final/database_record_verification.json`
- `papers/doi__10.1038_s41598-017-16784-6/final/review_report.json`
- `papers/doi__10.1038_s41598-017-16784-6/work/review/quality_feedback.json`
- `papers/doi__10.1038_s41598-017-16784-6/work/supplementary_methods/supplementary_evidence.json`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1038_s41598-017-16784-6/supplementary/landing-*.bin`

## Findings

- The packet has XML/PDF evidence for Macropin identity and main-text activity tables, including Table 1 sequence/modification and main Tables 2-5.
- The unresolved rows are specifically checkerboard synergy MIC/FICI rows that the article routes to supplementary Tables S1/S2.
- `supplementary_tables.json` has `table_count: 0`; `supplementary_text.jsonl` is only a small indexed supplement extraction, not row-level Tables S1/S2 data.
- `supplementary_index.json` lists ten `landing-*.bin` supplementary assets, but `file` identifies them as HTML documents, not PDF/XLSX/table files.
- Local search found no `MOESM` or `41598_2017_16784_MOESM1_ESM.pdf` file under the target `paper_packets/`, `papers/`, or landed-assets target DOI directories.
- Existing review/work materials already record the same blocker: the local packet lacks MOESM1, and linked DBAASP FICI rows cannot be source-verified from local material.

## Can this be fixed from current source packet?

No. The blocker is a true missing-primary-material blocker, not a parser-only gap. Main text and figure captions provide partial narrative support for selected combinations, but they do not provide the complete row-level Tables S1/S2 matrix required to verify all 12 DBAASP synergy rows or their mirrored experiment rows. Because the current packet lacks the supplementary PDF/table source, changing the final statuses would weaken provenance.

## Next step

Acquire or add the actual supplementary file identified by the paper as MOESM1, expected as `41598_2017_16784_MOESM1_ESM.pdf`, then parse Tables S1/S2 and rerun row-level worker-4/worker-6 database verification for DBAASP source_record_id `495`-`506` across both `linked_assay_records.jsonl` and `linked_experiment_records.jsonl`.
