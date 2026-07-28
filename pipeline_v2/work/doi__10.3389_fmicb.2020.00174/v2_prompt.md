
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
doi__10.3389_fmicb.2020.00174

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "TABLE 1", "caption": "Minimum inhibitory concentrations of the strains to antibiotics and antimicrobial peptides.", "footnotes": [], "header_rows": [["Strains", "MIC(μg/ml)", "MIC(μg/ml)", "MIC(μg/ml)", "MIC(μg/ml)"], ["", "AMO", "CHL", "BSN-37", "Pexiganan"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "E. coli ATCC25922", "col_header": "MIC(μg/ml) / AMO", "value": "8"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "E. coli ATCC25922", "col_header": "MIC(μg/ml) / CHL", "value": "3.13"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "E. coli ATCC25922", "col_header": "MIC(μg/ml) / BSN-37", "value": "33.33"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "E. coli ATCC25922", "col_header": "MIC(μg/ml) / Pexiganan", "value": "10.41"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "ST", "col_header": "MIC(μg/ml) / AMO", "value": "0.83"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "ST", "col_header": "MIC(μg/ml) / CHL", "value": "1.67"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "ST", "col_header": "MIC(μg/ml) / BSN-37", "value": "16.67"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "ST", "col_header": "MIC(μg/ml) / Pexiganan", "value": "6.25"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "S. enterica serovar Typhimurium CMCC50097", "col_header": "MIC(μg/ml) / AMO", "value": "2.67"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "S. enterica serovar Typhimurium CMCC50097", "col_header": "MIC(μg/ml) / CHL", "value": "2.67"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "S. enterica serovar Typhimurium CMCC50097", "col_header": "MIC(μg/ml) / BSN-37", "value": "8.33"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "S. enterica serovar Typhimurium CMCC50097", "col_header": "MIC(μg/ml) / Pexiganan", "value": "6.25"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "S. pullorum BNCC124693", "col_header": "MIC(μg/ml) / AMO", "value": "1.67"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "S. pullorum BNCC124693", "col_header": "MIC(μg/ml) / CHL", "value": "4"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "S. pullorum BNCC124693", "col_header": "MIC(μg/ml) / BSN-37", "value": "25"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "S. pullorum BNCC124693", "col_header": "MIC(μg/ml) / Pexiganan", "value": "50"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "S. aureus ATCC25923", "col_header": "MIC(μg/ml) / AMO", "value": "0.67"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "S. aureus ATCC25923", "col_header": "MIC(μg/ml) / CHL", "value": "13.33"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "S. aureus ATCC25923", "col_header": "MIC(μg/ml) / BSN-37", "value": ">200"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "S. aureus ATCC25923", "col_header": "MIC(μg/ml) / Pexiganan", "value": "20.83"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "S. albus CMCC26101", "col_header": "MIC(μg/ml) / AMO", "value": "0.5"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "S. albus CMCC26101", "col_header": "MIC(μg/ml) / CHL", "value": "16"}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "S. albus CMCC26101", "col_header": "MIC(μg/ml) / BSN-37", "value": "50"}, {"table_index": 1, "row_index": 8, "col_index": 5, "row_label": "S. albus CMCC26101", "col_header": "MIC(μg/ml) / Pexiganan", "value": "10.45"}]}, {"table_index": 2, "label": "TABLE 2", "caption": "Minimum inhibitory concentrations of BSN-37 in the presence and absence of physiological concentrations of different serum salts.", "footnotes": [], "header_rows": [["Culture medium", "Strains (unit: μg/ml)", "Strains (unit: μg/ml)"], ["", "E. coli ATCC25922", "ST"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "MH broth + NaCl (150 mM)", "col_header": "Strains (unit: μg/ml) / E. coli ATCC25922", "value": "200"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "MH broth + NaCl (150 mM)", "col_header": "Strains (unit: μg/ml) / ST", "value": "20.83"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "MH broth + KCl (4.5 mM)", "col_header": "Strains (unit: μg/ml) / E. coli ATCC25922", "value": "50"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "MH broth + KCl (4.5 mM)", "col_header": "Strains (unit: μg/ml) / ST", "value": "16.67"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "MH broth + NH4Cl (6 μM)", "col_header": "Strains (unit: μg/ml) / E. coli ATCC25922", "value": "50"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "MH broth + NH4Cl (6 μM)", "col_header": "Strains (unit: μg/ml) / ST", "value": "16.67"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "MH broth + MgCl2 (1 mM)", "col_header": "Strains (unit: μg/ml) / E. coli ATCC25922", "value": "200"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "MH broth + MgCl2 (1 mM)", "col_header": "Strains (unit: μg/ml) / ST", "value": "25"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "MH broth + CaCl2 (2.5 mM)", "col_header": "Strains (unit: μg/ml) / E. coli ATCC25922", "value": ">200"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "MH broth + CaCl2 (2.5 mM)", "col_header": "Strains (unit: μg/ml) / ST", "value": "66.67"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "MH broth + FeCl3 (4 μM)", "col_header": "Strains (unit: μg/ml) / E. coli ATCC25922", "value": "50"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "MH broth + FeCl3 (4 μM)", "col_header": "Strains (unit: μg/ml) / ST", "value": "12.5"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "MH broth", "col_header": "Strains (unit: μg/ml) / E. coli ATCC25922", "value": "33.33"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "MH broth", "col_header": "Strains (unit: μg/ml) / ST", "value": "16.67"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Salmonella enterica subsp. enterica serovar Pullorum BNCC124693", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 25923", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Staphylococcus epidermidis CMCC 261015", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Salmonella enterica subsp. enterica serovar Pullorum BNCC124693", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 25923", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Staphylococcus epidermidis CMCC 261015", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).