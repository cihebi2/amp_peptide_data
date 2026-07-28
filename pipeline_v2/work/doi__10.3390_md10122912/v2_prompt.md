
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
doi__10.3390_md10122912

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "1H and 13C NMR spectroscopic data for lajollamide A (1) a.", "footnotes": ["a Measured at 300 (1H) and 75 (13C) MHz in CDCl3; b Multiplicities were deduced from DEPT135 and HSQC experiments; c Assignments within a column may be interchanged."], "header_rows": [["Unit", "Position", "δCb", "δH (mult, J in Hz)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Leu-1", "col_header": "Position", "value": "C=O"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Leu-1", "col_header": "δCb", "value": "171.7, C"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "α", "col_header": "Position", "value": "53.6, CH"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "α", "col_header": "δCb", "value": "4.23, m"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "β", "col_header": "Position", "value": "40.7, CH2"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "β", "col_header": "δCb", "value": "1.56, m; 1.77, m"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "γ", "col_header": "Position", "value": "24.9, CH"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "γ", "col_header": "δCb", "value": "1.54 m"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "δ", "col_header": "Position", "value": "23.0, CH3 c"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "δ", "col_header": "δCb", "value": "0.94, d c"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "", "col_header": "Position", "value": "21.3, CH3 c"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "", "col_header": "δCb", "value": "0.90, d c"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "NH", "col_header": "δCb", "value": "6.21, brs"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Leu-2", "col_header": "Position", "value": "C=O"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "Leu-2", "col_header": "δCb", "value": "172.5, C"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "α", "col_header": "Position", "value": "51.2, CH"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "α", "col_header": "δCb", "value": "4.48, m"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "β", "col_header": "Position", "value": "39.9, CH2"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "β", "col_header": "δCb", "value": "1.49, m; 1.86, m"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "γ", "col_header": "Position", "value": "25.2, CH"}, {"table_index": 1, "row_index": 12, "col_index": 3, "row_label": "γ", "col_header": "δCb", "value": "1.59, m"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "δ", "col_header": "Position", "value": "22.1, CH3c"}, {"table_index": 1, "row_index": 13, "col_index": 3, "row_label": "δ", "col_header": "δCb", "value": "0.86, d c"}, {"table_index": 1, "row_index": 14, "col_index": 2, "row_label": "", "col_header": "Position", "value": "22.8, CH3c"}, {"table_index": 1, "row_index": 14, "col_index": 3, "row_label": "", "col_header": "δCb", "value": "0.90, d c"}, {"table_index": 1, "row_index": 15, "col_index": 3, "row_label": "NH", "col_header": "δCb", "value": "7.42, d (8.3)"}, {"table_index": 1, "row_index": 16, "col_index": 2, "row_label": "Leu-3", "col_header": "Position", "value": "C=O"}, {"table_index": 1, "row_index": 16, "col_index": 3, "row_label": "Leu-3", "col_header": "δCb", "value": "173.1, C"}, {"table_index": 1, "row_index": 17, "col_index": 2, "row_label": "α", "col_header": "Position", "value": "50.1, CH"}, {"table_index": 1, "row_index": 17, "col_index": 3, "row_label": "α", "col_header": "δCb", "value": "4.58, m"}, {"table_index": 1, "row_index": 18, "col_index": 2, "row_label": "β", "col_header": "Position", "value": "37.2, CH2"}, {"table_index": 1, "row_index": 18, "col_index": 3, "row_label": "β", "col_header": "δCb", "value": "1.48, m; 1.69, m"}, {"table_index": 1, "row_index": 19, "col_index": 2, "row_label": "γ", "col_header": "Position", "value": "24.6, CH"}, {"table_index": 1, "row_index": 19, "col_index": 3, "row_label": "γ", "col_header": "δCb", "value": "1.51, m"}, {"table_index": 1, "row_index": 20, "col_index": 2, "row_label": "δ", "col_header": "Position", "value": "23.2, CH3c"}, {"table_index": 1, "row_index": 20, "col_index": 3, "row_label": "δ", "col_header": "δCb", "value": "0.92, d c"}, {"table_index": 1, "row_index": 21, "col_index": 2, "row_label": "", "col_header": "Position", "value": "21.9, CH3c"}, {"table_index": 1, "row_index": 21, "col_index": 3, "row_label": "", "col_header": "δCb", "value": "0.88, d c"}, {"table_index": 1, "row_index": 22, "col_index": 3, "row_label": "NH", "col_header": "δCb", "value": "7.27, m"}, {"table_index": 1, "row_index": 23, "col_index": 2, "row_label": "Val", "col_header": "Position", "value": "C=O"}, {"table_index": 1, "row_index": 23, "col_index": 3, "row_label": "Val", "col_header": "δCb", "value": "173.6, C"}, {"table_index": 1, "row_index": 24, "col_index": 2, "row_label": "α", "col_header": "Position", "value": "55.3, C"}, {"table_index": 1, "row_index": 24, "col_index": 3, "row_label": "α", "col_header": "δCb", "value": "4.48, m"}, {"table_index": 1, "row_index": 25, "col_index": 2, "row_label": "β", "col_header": "Position", "value": "30.3, CH"}, {"table_index": 1, "row_index": 25, "col_index": 3, "row_label": "β", "col_header": "δCb", "value": "1.89, m"}, {"table_index": 1, "row_index": 26, "col_index": 2, "row_label": "γ", "col_header": "Position", "value": "18.5, CH3"}, {"table_index": 1, "row_index": 26, "col_index": 3, "row_label": "γ", "col_header": "δCb", "value": "0.94"}, {"table_index": 1, "row_index": 27, "col_index": 2, "row_label": "19.2, CH3", "col_header": "Position", "value": "0.92"}, {"table_index": 1, "row_index": 28, "col_index": 3, "row_label": "NH", "col_header": "δCb", "value": "6.92, d (8.9)"}, {"table_index": 1, "row_index": 29, "col_index": 2, "row_label": "N-Me-Leu", "col_header": "Position", "value": "C=O"}, {"table_index": 1, "row_index": 29, "col_index": 3, "row_label": "N-Me-Leu", "col_header": "δCb", "value": "171.2, C"}, {"table_index": 1, "row_index": 30, "col_index": 2, "row_label": "α", "col_header": "Position", "value": "65.2, CH"}, {"table_index": 1, "row_index": 30, "col_index": 3, "row_label": "α", "col_header": "δCb", "value": "3.49, dd (4.1, 3.6)"}, {"table_index": 1, "row_index": 31, "col_index": 2, "row_label": "β", "col_header": "Position", "value": "37.6, CH2"}, {"table_index": 1, "row_index": 31, "col_index": 3, "row_label": "β", "col_header": "δCb", "value": "1.44, m; 2.24, m"}, {"table_index": 1, "row_index": 32, "col_index": 2, "row_label": "γ", "col_header": "Position", "value": "25.3, CH"}, {"table_index": 1, "row_index": 32, "col_index": 3, "row_label": "γ", "col_header": "δCb", "value": "1.59, m"}, {"table_index": 1, "row_index": 33, "col_index": 2, "row_label": "δ", "col_header": "Position", "value": "23.5, CH3c"}, {"table_index": 1, "row_index": 33, "col_index": 3, "row_label": "δ", "col_header": "δCb", "value": "0.96, d c"}, {"table_index": 1, "row_index": 34, "col_index": 2, "row_label": "21.7, CH3c", "col_header": "Position", "value": "0.97, d c"}, {"table_index": 1, "row_index": 35, "col_index": 2, "row_label": "N-Me", "col_header": "Position", "value": "40.9, CH3"}, {"table_index": 1, "row_index": 35, "col_index": 3, "row_label": "N-Me", "col_header": "δCb", "value": "3.29, s"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "Not active up to 100 µM", "db_value": "NA", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "", "db_value": "NA", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).