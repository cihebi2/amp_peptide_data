
You are a STRICT database-record auditor (pipeline v2). You compare what a peptide database ASSERTS
against the PRIMARY PAPER's deterministically-parsed tables that are given to you below. You must not
read raw XML or invent values: the ONLY admissible source evidence is the `longform_cells` provided.

For EACH database assertion, output one JSON object with this exact schema:
{
 "assertion_index": <int, 0-based position in db_assertions>,
 "db_claimed": {"organism": "...", "endpoint": "...", "value": "...", "peptide": "..."},
 "verification_outcome": one of
     "value_match"            (source has the SAME value for the same peptide+organism+endpoint),
     "value_mismatch"         (source has a DIFFERENT value -> candidate real DB error),
     "endpoint_mismatch"      (source reports this value under a DIFFERENT endpoint than the DB claims,
                               e.g. DB says IC50 but the source column header says GI50/EC50/MBC),
     "variant_misattribution" (the value EXISTS in source but belongs to a DIFFERENT peptide/variant
                               than the DB row names),
     "not_in_provided_tables" (the organism/target/value is NOT in the tables provided to you;
                               this is NOT evidence of a database error -- the value may live in a
                               figure, supplement, or a table not provided. Treat as undetermined.),
     "cannot_determine"       (value lives only in a figure image, or no matching cell exists in the
                               provided tables, or the table structure is too ambiguous to match),
 "normalization_note": one of
     "strain_id_differs_value_same", "modification_representation_only", "unit_differs", "none",
 "is_database_error": <bool>,
 "evidence": {"table_index": <int>, "row_label": "...", "col_header": "...", "source_value": "..."},
 "short_reason": "<=200 chars"
}

HARD RULES (these encode the fixes over the old pipeline):
1. GROUNDING: the `evidence` object MUST be copied verbatim from one of the provided `longform_cells`.
   If no provided cell supports a comparison, you MUST return "cannot_determine" and leave evidence null.
   Never guess a number that is not in the provided cells.
2. ENDPOINT FROM SOURCE: take the endpoint from the table column header / caption / footnote, NOT from
   the database. If the DB endpoint label differs from the source header for the same value -> endpoint_mismatch.
3. STRAIN-ID NORMALIZATION: if the source has the SAME value for the same GENUS+SPECIES and SAME endpoint
   but a different strain/collection id (e.g. DB "ATCC 6258" vs source "CCM 8271"; ATCC/CCM/PCM/DSM/KCTC/CGMCC),
   this is NOT an error: verification_outcome="value_match", normalization_note="strain_id_differs_value_same",
   is_database_error=false.
4. MODIFICATION NORMALIZATION: a DB "core sequence" vs a source "core sequence + terminal -NH2 / N-acetyl"
   is representation, not error: normalization_note="modification_representation_only", is_database_error=false
   (unless the residue letters themselves differ).
5. is_database_error=true ONLY for value_mismatch / endpoint_mismatch / variant_misattribution that
   (a) are NOT explained by a normalization_note AND (b) carry a positive `evidence` cell copied from
   longform_cells showing the CONFLICTING source value.
5b. VARIANT MISATTRIBUTION needs an identity anchor: only use "variant_misattribution" when the DB
   assertion provides a peptide name (db_claimed_peptide_name) that maps to a SPECIFIC source row/column.
   If the DB record has no peptide name, or the source columns are coded (e.g. #1..#25) without a legend
   you can resolve, you CANNOT know which variant the value belongs to -> use "cannot_determine".
6. ABSENCE IS NOT ERROR (critical): you are given ONLY some tables, never the whole paper. If a DB
   organism/target/value is not in the provided cells, you MUST return "not_in_provided_tables" with
   is_database_error=false. NEVER conclude the database is wrong merely because something is missing
   from the tables you were given -- it may be in a figure, supplement, or a table not provided.
7. Output ONLY a JSON array of these objects as your final message. No prose, no markdown fences.


=== PAPER ID ===
doi__10.1371_journal.pone.0162007

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Median lethal dose (LD50) of WRK on cancer cell lines tested.", "footnotes": [], "header_rows": [["", "Glial cells", "Glial cells", "Prostatic cells", "Prostatic cells", "Leukocytes", "Leukocytes", "Leukocytes", "Leukocytes"], ["Cell line", "C6", "Astrocytes", "LNCaP", "RWPE", "Jurkat", "KG1", "K562", "MNC"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "LD50 (μM)", "col_header": "Glial cells / C6", "value": "4.14"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "LD50 (μM)", "col_header": "Glial cells / Astrocytes", "value": "3.36"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "LD50 (μM)", "col_header": "Prostatic cells / LNCaP", "value": "3.98"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "LD50 (μM)", "col_header": "Prostatic cells / RWPE", "value": "6.37"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "LD50 (μM)", "col_header": "Leukocytes / Jurkat", "value": "2.11"}, {"table_index": 1, "row_index": 3, "col_index": 7, "row_label": "LD50 (μM)", "col_header": "Leukocytes / KG1", "value": "2.18"}, {"table_index": 1, "row_index": 3, "col_index": 8, "row_label": "LD50 (μM)", "col_header": "Leukocytes / K562", "value": "4.22"}, {"table_index": 1, "row_index": 3, "col_index": 9, "row_label": "LD50 (μM)", "col_header": "Leukocytes / MNC", "value": "ND"}]}, {"table_index": 2, "label": "Table 2", "caption": "Primary sequences and biological activities of WRK and analogs WarnG20D and WarnF14V.", "footnotes": ["a Cytotoxic activity was determined on Jurkat cells.", "b 10% Hemolysis concentration corresponds to the peptide concentration which induces the lysis of 10% of the red cells in the sample.", "c Anti-leukemia index corresponds to the ratio: 10% Hemolysis concentration / LD50."], "header_rows": [["Name", "Sequence", "LD50a (μM)", "10% Hemolysis concentrationb (μM)", "Anti-leukemia indexc"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "WRK", "col_header": "Sequence", "value": "MQFITDLIKKAVDFFKGLFGNK"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "WRK", "col_header": "LD50a (μM)", "value": "2.11"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "WRK", "col_header": "10% Hemolysis concentrationb (μM)", "value": "2.78"}, {"table_index": 2, "row_index": 2, "col_index": 5, "row_label": "WRK", "col_header": "Anti-leukemia indexc", "value": "1.317"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "WarnG20D", "col_header": "Sequence", "value": "MQFITDLIKKAVDFFKGLFDNK"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "WarnG20D", "col_header": "LD50a (μM)", "value": "5.39"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "WarnG20D", "col_header": "10% Hemolysis concentrationb (μM)", "value": "12.36"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "WarnG20D", "col_header": "Anti-leukemia indexc", "value": "2.293"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "WarnF14V", "col_header": "Sequence", "value": "MQFITDLIKKAVDVFKGLFGNK"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "WarnF14V", "col_header": "LD50a (μM)", "value": "8.79"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "WarnF14V", "col_header": "10% Hemolysis concentrationb (μM)", "value": "12.5"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "WarnF14V", "col_header": "Anti-leukemia indexc", "value": "1.422"}]}, {"table_index": 3, "label": "Table 3", "caption": "Raman band assignments according to references [47–49].", "footnotes": [], "header_rows": [["Band (cm-1)", "Assignment"], ["725", "DNA/RNA (adenine ring breathing)"], ["755", "Proteins (tryptophan symmetric ring breathing)"], ["788", "DNA/RNA (thymine, uracil, cytosine ring breathing) and DNA backbone (O-P-O stretching)"], ["1010", "Proteins (phenylalanine symmetric ring breathing)"], ["1100", "Lipids, Proteins (C-C stretching)"], ["1137", "Lipids, Proteins (C-C stretching)"], ["1263", "Proteins (Amide III)"], ["1311", "Lipids, Proteins, DNA/RNA"], ["1348", "Lipids, Proteins, DNA/RNA"], ["1457", "Lipids (CH2 CH3 binding)"], ["1583", "DNA/RNA (guanine, adenine)"], ["1665", "Proteins (Amide I)"], ["2850–2950", "Lipids, proteins (CH2, CH3, symmetric and antisymmetric stretching and CH stretching)"], ["3080", "Lipids (C = C-H, CH stretching)"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "Tumor cells: Jurkat (LD50=5.39µM)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Warnericin RK [G20D]"}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Tumor cells: Jurkat (LD50=8.79µM)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Warnericin RK [F14V]"}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "Tumor cells: Jurkat (LD50=5.39µM)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Specific Anti-Leukemic Activity of the Peptide Warnericin RK and Analogues and Visualization of Their Effect on Cancer Cells by Chemical Raman Imaging"}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "Tumor cells: Jurkat (LD50=8.79µM)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Specific Anti-Leukemic Activity of the Peptide Warnericin RK and Analogues and Visualization of Their Effect on Cancer Cells by Chemical Raman Imaging"}, {"assertion_index": 4, "database": "CAMP", "db_subject_text": "Jurkat cancer cells[LD50 = 5.39 microM], Legionella pneumophila Lens[MIC = 1.19 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Warnericin RK"}, {"assertion_index": 5, "database": "CAMP", "db_subject_text": "Jurkat cancer cells[LD50 = 8.79 microM], Legionella pneumophila Lens[MIC = 1.23 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Warnericin RK"}, {"assertion_index": 6, "database": "dbAMP", "db_subject_text": "Jurkat cancer cells (LD50=8.79μM)\nLegionella pneumophila Lens (MIC=1.23μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Warnericin RK [F14V]"}, {"assertion_index": 7, "database": "dbAMP", "db_subject_text": "Jurkat cancer cells (LD50=5.39μM)\nLegionella pneumophila Lens (MIC=1.19μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Warnericin RK [G20D]"}]

Return ONLY the JSON array now (one object per assertion above).