
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
doi__10.3389_fphar.2021.783108

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "TABLE 1", "caption": "Antimicrobial activity of brevinin-2MP.", "footnotes": [], "header_rows": [["Microorganism", "MIC/MBC (μM)", "MIC/MBC (μM)"], ["Brevinin-2MP", "AMP"], ["Gram-negative bacteria", "Gram-negative bacteria", "Gram-negative bacteria"]], "longform_cells": [{"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Escherichia coli ATCC 25922", "col_header": "MIC/MBC (μM) / Brevinin-2MP / Gram-negative bacteria", "value": "47.78/47.78"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Escherichia coli ATCC 25922", "col_header": "MIC/MBC (μM) / AMP / Gram-negative bacteria", "value": "100/100"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Pseudomonas aeruginosa ATCC 27853", "col_header": "MIC/MBC (μM) / Brevinin-2MP / Gram-negative bacteria", "value": ">100/>100"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Pseudomonas aeruginosa ATCC 27853", "col_header": "MIC/MBC (μM) / AMP / Gram-negative bacteria", "value": ">100/>100"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Gram-positive bacteria", "col_header": "MIC/MBC (μM) / Brevinin-2MP / Gram-negative bacteria", "value": "Gram-positive bacteria"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Gram-positive bacteria", "col_header": "MIC/MBC (μM) / AMP / Gram-negative bacteria", "value": "Gram-positive bacteria"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Staphylococcus aureus ATCC 25923", "col_header": "MIC/MBC (μM) / Brevinin-2MP / Gram-negative bacteria", "value": "47.78/47.78"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "Staphylococcus aureus ATCC 25923", "col_header": "MIC/MBC (μM) / AMP / Gram-negative bacteria", "value": "100/100"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Propionibacterium acnes ATCC 6919", "col_header": "MIC/MBC (μM) / Brevinin-2MP / Gram-negative bacteria", "value": "14.93/14.93"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "Propionibacterium acnes ATCC 6919", "col_header": "MIC/MBC (μM) / AMP / Gram-negative bacteria", "value": "25/50"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Bacillus subtilis CMCC 63501", "col_header": "MIC/MBC (μM) / Brevinin-2MP / Gram-negative bacteria", "value": "4.97/4.97"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "Bacillus subtilis CMCC 63501", "col_header": "MIC/MBC (μM) / AMP / Gram-negative bacteria", "value": "25/50"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Fungi", "col_header": "MIC/MBC (μM) / Brevinin-2MP / Gram-negative bacteria", "value": "Fungi"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "Fungi", "col_header": "MIC/MBC (μM) / AMP / Gram-negative bacteria", "value": "Fungi"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "Candida albicans ATCC 10231", "col_header": "MIC/MBC (μM) / Brevinin-2MP / Gram-negative bacteria", "value": "59.73/59.73"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "Candida albicans ATCC 10231", "col_header": "MIC/MBC (μM) / AMP / Gram-negative bacteria", "value": "50/100"}]}, {"table_index": 2, "label": "TABLE 2", "caption": "Hemolytic activity of brevinin-2MP.", "footnotes": [], "header_rows": [["Brevinin-2MP (μM)", "Hemolysis ratio (%)"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "100", "col_header": "Hemolysis ratio (%)", "value": "1.42 ± 0.16"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "50", "col_header": "Hemolysis ratio (%)", "value": "0.78 ± 0.07"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "25", "col_header": "Hemolysis ratio (%)", "value": "0.63 ± 0.16"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "12.5", "col_header": "Hemolysis ratio (%)", "value": "0.39 ± 0.17"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "6.25", "col_header": "Hemolysis ratio (%)", "value": "0.10 ± 0.20"}]}, {"table_index": 3, "label": "TABLE 3", "caption": "Cytotoxicity of brevinin-2MP.", "footnotes": ["The results represent mean ± SEM, values from three separate experiments.", "RAW 264.7, mouse leukemic monocyte macrophage cells; H460, human lung adenocarcinoma cells; MDA-MB-231, human breast cancer cells; M21, human melanoma cells;IC50; half-maximum inhibitory concentration."], "header_rows": [["Cells", "IC50 (μM)"]], "longform_cells": [{"table_index": 3, "row_index": 2, "col_index": 2, "row_label": "RAW 264.7", "col_header": "IC50 (μM)", "value": "72.53 ± 2.16"}, {"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "Mouse splenocytes", "col_header": "IC50 (μM)", "value": "60.32 ± 5.67"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "MDA-MB-231", "col_header": "IC50 (μM)", "value": "26.36 ± 4.91"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "H460", "col_header": "IC50 (μM)", "value": "5.77 ± 1.21"}, {"table_index": 3, "row_index": 6, "col_index": 2, "row_label": "M21", "col_header": "IC50 (μM)", "value": "60.41 ± 8.78"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Antimicrobial and Anti-inflammatory Effects of a Novel Peptide From the Skin of Frog Microhyla pulchra.", "db_measure": "database entry text with sequence, broad activity labels, and database-computed annotations", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Brevinin-2MP"}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Not available", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Brevinin-2MP"}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "Not available", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Brevinin-2MP"}]

Return ONLY the JSON array now (one object per assertion above).