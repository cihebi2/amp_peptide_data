# Unresolved records review: doi__10.1038_s41522-024-00637-y

Scope: only `papers/doi__10.1038_s41522-024-00637-y` and `paper_packets/doi__10.1038_s41522-024-00637-y` were reviewed for this task. No other paper was edited.

## Decision

I did not edit `papers/doi__10.1038_s41522-024-00637-y/final/database_record_verification.json`.

Reason: the current packet/source materials do not provide new primary/source-packet evidence that can safely promote or remap the unresolved rows. The strongest local primary evidence is main-text/Table 1 for colistin + DJK-5 planktonic MIC/FICI values. The unresolved rows still need either the real supplementary material or row-level partner/medium mapping that is absent from the local DBAASP snapshots.

## Materials checked

- `papers/doi__10.1038_s41522-024-00637-y/final/database_record_verification.json`
- `papers/doi__10.1038_s41522-024-00637-y/final/activity_toxicity_evidence.json`
- `papers/doi__10.1038_s41522-024-00637-y/final/review_report.json`
- `papers/doi__10.1038_s41522-024-00637-y/work/supplementary_methods/supplementary_evidence.json`
- `papers/doi__10.1038_s41522-024-00637-y/work/review/quality_feedback.json`
- `paper_packets/doi__10.1038_s41522-024-00637-y/packet_manifest.json`
- `paper_packets/doi__10.1038_s41522-024-00637-y/analysis/database_record_audit.json`
- `paper_packets/doi__10.1038_s41522-024-00637-y/analysis/adjudication_report.json`
- `paper_packets/doi__10.1038_s41522-024-00637-y/extracted/xml_sections.json`
- `paper_packets/doi__10.1038_s41522-024-00637-y/extracted/pdf_text/landing-1.txt`
- `paper_packets/doi__10.1038_s41522-024-00637-y/extracted/supplementary_index.json`
- `paper_packets/doi__10.1038_s41522-024-00637-y/extracted/supplementary_text.jsonl`
- `paper_packets/doi__10.1038_s41522-024-00637-y/extracted/supplementary_tables.json`
- `paper_packets/doi__10.1038_s41522-024-00637-y/database/linked_assay_records.jsonl`
- `paper_packets/doi__10.1038_s41522-024-00637-y/database/linked_experiment_records.jsonl`
- `paper_packets/doi__10.1038_s41522-024-00637-y/database/linked_sequence_records.jsonl`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1038_s41522-024-00637-y/asset_manifest.csv`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1038_s41522-024-00637-y/metadata.json`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1038_s41522-024-00637-y/pdf/landing-1.pdf`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1038_s41522-024-00637-y/xml/local-DBAASP-PMC11711674.xml`
- `/mnt/d/work/抗菌肽/数据库/merged_amp_corpus/landed_assets/papers/doi__10.1038_s41522-024-00637-y/supplementary/landing-*.bin`

Note: `papers/doi__10.1038_s41522-024-00637-y/source/` is not present in this checkout, although several existing final/packet notes reference `papers/.../source/paper.xml` and `papers/.../source/paper.pdf`. The usable local primary materials are the packet extracts and the landed XML/PDF paths listed above.

## Current unresolved classes

From `final/database_record_verification.json`:

- `synergy_partner_ambiguous_or_supplement_unavailable`: 14 unresolved rows.
- `daptomycin_exact_values_require_missing_supplement`: 14 unresolved rows.
- `not_row_level_source_verified`: 2 unresolved rows.
- Additional cross-cutting blocker: `linked_sequence_records.jsonl` has zero rows, so exact DJK-5 sequence/modification cannot be primary-source verified from local packet material.

## Evidence review by blocker class

### 1. DJK-5 synergy/FICI partner mapping

Affected rows: DBAASP `DBAASPS_11338` rows in both `linked_assay_records.jsonl` and `linked_experiment_records.jsonl`.

What local source supports:

- Main-text Table 1 supports a colistin + DJK-5 planktonic table with two strains, two media conditions, MIC columns for colistin and DJK-5, and FICI columns for the combination.
- The Table 1 values visible in the extracted PDF/XML align with four colistin + DJK-5 FICI cells: P. aeruginosa LESB58 in MHB/DFG and S. aureus USA300 LAC in MHB/DFG.

Why this remains unresolved:

- DBAASP synergy rows for `DBAASPS_11338` do not carry the partner drug or the medium condition in the local snapshots.
- The same strain can have multiple FICI rows, including duplicates and values that overlap Table 1 but cannot be assigned to a unique source row without partner/medium metadata.
- Some DJK-5-associated FICI rows likely require the missing supplementary table rather than Table 1, but the local rows do not identify which are colistin partners versus other partners.

Can fix now: no. Table 1 confirms that some values exist, but it does not provide enough database-row metadata to make a safer final-state edit.

Recommended rework/source-staging:

- Database mapping rework: add or recover partner-drug and medium fields for DBAASP synergy assay IDs `5263`-`5270` and linked experiment records `1`-`8`.
- If partner/medium cannot be recovered from database provenance, keep these rows unresolved rather than promoting by value matching alone.

### 2. Daptomycin + DJK-5 exact MIC/FICI rows

Affected rows: DBAASP `DBAASPN_20908` daptomycin rows in both `linked_assay_records.jsonl` and `linked_experiment_records.jsonl`.

What local source supports:

- The main text discusses daptomycin + DJK-5 and points planktonic daptomycin + DJK-5 details to Supplementary Table 1.
- The extracted main text also supports qualitative co-biofilm/in vivo daptomycin + DJK-5 activity, but those claims do not replace Supplementary Table 1 for exact planktonic MIC/FICI database rows.

Why this remains unresolved:

- `supplementary_tables.json` has `table_count: 0`.
- `supplementary_text.jsonl` marks all ten supplementary assets as `indexed_only`.
- `file` classifies the ten landed `supplementary/landing-*.bin` files as HTML article landing pages, not recovered PDF/spreadsheet supplementary data.
- `metadata.json` records the PMC OA package fetch failure.
- The Nature article HTML captured in the `.bin` files contains a source URL for `41522_2024_637_MOESM1_ESM.pdf`, but that PDF is not staged as local source-packet material in this checkout.

Can fix now: no. The local packet does not contain Supplementary Table 1, so exact daptomycin MIC/FICI rows cannot be source-reviewed.

Recommended rework/source-staging:

- Source-staging should fetch/stage the supplementary PDF from the article link present in the local HTML: `https://static-content.springer.com/esm/art%3A10.1038%2Fs41522-024-00637-y/MediaObjects/41522_2024_637_MOESM1_ESM.pdf`.
- After staging, rerun supplementary extraction/OCR/table parsing and then remap DBAASP `DBAASPN_20908` rows by strain, medium, partner, MIC, and FICI.

### 3. `not_row_level_source_verified`

Affected rows: one `DBAASPS_11338` S. aureus synergy row in `linked_assay_records.jsonl` and the corresponding linked experiment row.

What local source supports:

- Table 1 contains S. aureus USA300 LAC colistin + DJK-5 FICI values for MHB and DFG.

Why this remains unresolved:

- The database row lacks enough row-level fields to distinguish medium and partner context.
- Value matching alone is unsafe because multiple S. aureus DJK-5 FICI rows exist, including values that could be Table 1 cells and values that may require supplementary context.

Can fix now: no. The blocker is row-level database mapping, not lack of awareness that Table 1 exists.

Recommended rework/source-staging:

- Database-row mapping rework should join DBAASP assay IDs to original partner/medium/checkerboard metadata.
- Preserve `unresolved_record` if a unique source row cannot be reconstructed.

### 4. Exact DJK-5 sequence/modification verification

Affected scope: all DJK-5-linked rows where source verification would require exact sequence/modification evidence.

What local source supports:

- The article names DJK-5 and gives D-enantiomeric peptide context.

Why this remains unresolved:

- `linked_sequence_records.jsonl` is empty.
- The local XML/PDF extracts do not embed the exact DJK-5 sequence or full modification record.

Can fix now: no.

Recommended rework/source-staging:

- Recover linked DBAASP sequence material for `DBAASPS_11338`, or a primary/source packet locator that states the exact DJK-5 sequence/modification.
- Do not mark these rows `source_verified` until that source exists locally.

## Final recommendation

Do not change `final/database_record_verification.json` from current packet evidence. The honest state is still blocked/unresolved:

- Table 1 can support known colistin + DJK-5 values at source level, but cannot uniquely resolve all DBAASP DJK-5 synergy rows because partner and medium are absent in the local database snapshots.
- Daptomycin + DJK-5 exact values require Supplementary Table 1, which is not locally staged/extracted.
- Exact DJK-5 sequence/modification remains unsupported because linked sequence records are absent.

Next concrete action: stage the real supplementary PDF/table asset, then rerun supplementary table extraction and DBAASP row-level partner/medium mapping before any final-status promotion.
