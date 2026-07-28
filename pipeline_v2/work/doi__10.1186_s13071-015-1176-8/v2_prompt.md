
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
doi__10.1186_s13071-015-1176-8

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Antimicrobial activity of SibaCec", "footnotes": ["a MIC minimal inhibitory concentration. These MICs represent mean values of three independent experiments performed in duplicates"], "header_rows": [["Microorganisms", "MIC (μM)a"], ["Gram-negative bacteria", "Gram-negative bacteria"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Escherichia coli ATCC 25922", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "0.87"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "E. coli clinical strain 1", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "1.45"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "E. coli clinical strain 2", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "1.45"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "E. coli clinical strain 3", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "2.33"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Pseudomonas aeruginosa ATCC 9027", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "1.74"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Salmonella typhimurium ATCC 14028", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "2.33"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Acinetobacter baumannii ATCC 17978", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "2.33"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Gram-positive bacteria", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "Gram-positive bacteria"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "Staphylococcus aureus ATCC 6538", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "43.70"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "Bacillus subtilis ATCC 6633", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "29.13"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "Micrococcus luteus ATCC 4698", "col_header": "MIC (μM)a / Gram-negative bacteria", "value": "14.56"}]}, {"table_index": 2, "label": "Table 2", "caption": "Secondary structural components of SibaCec in different solutions", "footnotes": ["aJasco-810 software was used to deconvolute CD spectra into fractional contents and these data are the average value of three scans"], "header_rows": [["Solution", "Helix (%)a", "Beta (%)a", "Turn (%)a", "Random (%)a"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "H2O", "col_header": "Helix (%)a", "value": "0.0"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "H2O", "col_header": "Beta (%)a", "value": "15.3"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "H2O", "col_header": "Turn (%)a", "value": "25.3"}, {"table_index": 2, "row_index": 2, "col_index": 5, "row_label": "H2O", "col_header": "Random (%)a", "value": "59.4"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "5", "col_header": "Helix (%)a", "value": "71.6"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "5", "col_header": "Beta (%)a", "value": "0.0"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "5", "col_header": "Turn (%)a", "value": "0.0"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "5", "col_header": "Random (%)a", "value": "28.4"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "10", "col_header": "Helix (%)a", "value": "71.6"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "10", "col_header": "Beta (%)a", "value": "0.0"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "10", "col_header": "Turn (%)a", "value": "0.0"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "10", "col_header": "Random (%)a", "value": "28.4"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "20", "col_header": "Helix (%)a", "value": "69.9"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "20", "col_header": "Beta (%)a", "value": "0.0"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "20", "col_header": "Turn (%)a", "value": "0.0"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "20", "col_header": "Random (%)a", "value": "30.1"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "40", "col_header": "Helix (%)a", "value": "64.1"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "40", "col_header": "Beta (%)a", "value": "6.1"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "40", "col_header": "Turn (%)a", "value": "0.0"}, {"table_index": 2, "row_index": 7, "col_index": 5, "row_label": "40", "col_header": "Random (%)a", "value": "29.8"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "50", "col_header": "Helix (%)a", "value": "0.0"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "50", "col_header": "Beta (%)a", "value": "23.6"}, {"table_index": 2, "row_index": 9, "col_index": 4, "row_label": "50", "col_header": "Turn (%)a", "value": "18.8"}, {"table_index": 2, "row_index": 9, "col_index": 5, "row_label": "50", "col_header": "Random (%)a", "value": "57.6"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "100", "col_header": "Helix (%)a", "value": "0.0"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "100", "col_header": "Beta (%)a", "value": "41.3"}, {"table_index": 2, "row_index": 10, "col_index": 4, "row_label": "100", "col_header": "Turn (%)a", "value": "9.8"}, {"table_index": 2, "row_index": 10, "col_index": 5, "row_label": "100", "col_header": "Random (%)a", "value": "48.9"}, {"table_index": 2, "row_index": 11, "col_index": 2, "row_label": "200", "col_header": "Helix (%)a", "value": "9.8"}, {"table_index": 2, "row_index": 11, "col_index": 3, "row_label": "200", "col_header": "Beta (%)a", "value": "42.0"}, {"table_index": 2, "row_index": 11, "col_index": 4, "row_label": "200", "col_header": "Turn (%)a", "value": "5.6"}, {"table_index": 2, "row_index": 11, "col_index": 5, "row_label": "200", "col_header": "Random (%)a", "value": "42.8"}, {"table_index": 2, "row_index": 12, "col_index": 2, "row_label": "400", "col_header": "Helix (%)a", "value": "35.1"}, {"table_index": 2, "row_index": 12, "col_index": 3, "row_label": "400", "col_header": "Beta (%)a", "value": "30.9"}, {"table_index": 2, "row_index": 12, "col_index": 4, "row_label": "400", "col_header": "Turn (%)a", "value": "2.1"}, {"table_index": 2, "row_index": 12, "col_index": 5, "row_label": "400", "col_header": "Random (%)a", "value": "31.9"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Escherichia coli clinical strains 1 and 2", "db_measure": "MIC", "db_value": "1.45", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Escherichia coli clinical strains 1 and 2", "db_measure": "MIC", "db_value": "1.45", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "3% Hemolysis", "db_value": "3", "db_unit": "% hemolysis at 200 µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "3% Hemolysis", "db_value": "3", "db_unit": "% hemolysis at 200 µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "APD6", "db_subject_text": "SibaCec APD6 entry text", "db_measure": "entry_text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "CAMP", "db_subject_text": "CAMP SibaCec entry text", "db_measure": "entry_text MIC list and hemolysis summary", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).