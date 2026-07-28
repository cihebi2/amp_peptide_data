
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
doi__10.3390_toxins8090255

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "The minimal inhibitory concentrations (MICs) of PS-Du, PS-Co, PS-Du K7H and PS-Co K7H, against the three different microorganisms.", "footnotes": [], "header_rows": [["Peptide Name", "Molecular Mass(Da)", "MIC", "MIC", "MIC"], ["S. aureus", "E. coli", "C. albicans"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "PS-Du", "col_header": "Molecular Mass(Da)", "value": "2049.5"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "PS-Du", "col_header": "MIC", "value": "8 mg/L"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "PS-Du", "col_header": "MIC", "value": "128 mg/L"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "PS-Du", "col_header": "MIC", "value": "16 mg/L"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "(3.90 µM)", "col_header": "Molecular Mass(Da)", "value": "(62.45 µM)"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "(3.90 µM)", "col_header": "MIC", "value": "(7.81 µM)"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "PS-Co", "col_header": "Molecular Mass(Da)", "value": "1971.5"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "PS-Co", "col_header": "MIC", "value": "8 mg/L"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "PS-Co", "col_header": "MIC", "value": "128 mg/L"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "PS-Co", "col_header": "MIC", "value": "16 mg/L"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "(4.06 µM)", "col_header": "Molecular Mass(Da)", "value": "(64.93 µM)"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "(4.06 µM)", "col_header": "MIC", "value": "(8.12 µM)"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "PS-Du K7H", "col_header": "Molecular Mass(Da)", "value": "2057.1"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "PS-Du K7H", "col_header": "MIC", "value": "32 mg/L"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "PS-Du K7H", "col_header": "MIC", "value": "512 mg/L"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "PS-Du K7H", "col_header": "MIC", "value": "64 mg/L"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "(15.56 µM)", "col_header": "Molecular Mass(Da)", "value": "(248.89 µM)"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "(15.56 µM)", "col_header": "MIC", "value": "(31.12 µM)"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "PS-Co K7H", "col_header": "Molecular Mass(Da)", "value": "1979.1"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "PS-Co K7H", "col_header": "MIC", "value": "32 mg/L"}, {"table_index": 1, "row_index": 9, "col_index": 4, "row_label": "PS-Co K7H", "col_header": "MIC", "value": "512 mg/L"}, {"table_index": 1, "row_index": 9, "col_index": 5, "row_label": "PS-Co K7H", "col_header": "MIC", "value": "64 mg/L"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "(16.17 µM)", "col_header": "Molecular Mass(Da)", "value": "(258.70 µM)"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "(16.17 µM)", "col_header": "MIC", "value": "(32.34 µM)"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "0% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "4% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "15% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "55% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "0% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "5% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "20% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "100% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "0% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "5% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "7% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "10% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 12, "database": "APD6", "db_subject_text": "Discovery of Novel Bacterial Cell-Penetrating Phylloseptins in Defensive Skin Secretions of the South American Hylid Frogs, Phyllomedusa duellmani and Phyllomedusa", "db_measure": "Unknown", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 13, "database": "CAMP", "db_subject_text": "Staphylococcus aureus NCTC 10788[MIC = 32 microg/ml], Escherichia coli NCTC 10418[MIC = 512 microg/ml], Candida albicans NCPF 1467[MIC = 64 microg/ml]", "db_measure": "Gram+, Gram-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 14, "database": "CAMP", "db_subject_text": "Staphylococcus aureus NCTC 10788[MIC = 32 microg/ml], Escherichia coli NCTC 10418[MIC = 512 microg/ml], Candida albicans NCPF 1467[MIC = 64 microg/ml]", "db_measure": "Gram+, Gram-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).