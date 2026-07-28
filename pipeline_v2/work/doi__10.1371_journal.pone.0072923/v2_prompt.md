
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
doi__10.1371_journal.pone.0072923

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Antimicrobial activities of LZ1 against skin bacteria.", "footnotes": ["MIC: minimal peptide concentration required for total inhibition of cell growth in liquid medium. These concentrations represent mean values of three independent experiments performed in duplicates. IS: clinically isolated strain, DR: drug resistance for clindamycin, CL: clindamycin, ND: no detectable activity"], "header_rows": [["", "MIC (μg/ml)", "MIC (μg/ml)"], ["Bacteria", "LZ1", "CL"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "P. acnes ATCC6919", "col_header": "MIC (μg/ml) / LZ1", "value": "0.6"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "P. acnes ATCC6919", "col_header": "MIC (μg/ml) / CL", "value": "2.3"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "P. acnes ATCC11827", "col_header": "MIC (μg/ml) / LZ1", "value": "0.6"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "P. acnes ATCC11827", "col_header": "MIC (μg/ml) / CL", "value": "2.3"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "P. acnes (IS, DR)", "col_header": "MIC (μg/ml) / LZ1", "value": "0.6"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "P. acnes (IS, DR)", "col_header": "MIC (μg/ml) / CL", "value": "ND"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "S. epidermidis 09A3726", "col_header": "MIC (μg/ml) / LZ1", "value": "4.7"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "S. epidermidis 09A3726", "col_header": "MIC (μg/ml) / CL", "value": "ND"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "S. epidermidis 09B2490", "col_header": "MIC (μg/ml) / LZ1", "value": "2.3"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "S. epidermidis 09B2490", "col_header": "MIC (μg/ml) / CL", "value": "1.2"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "S. aureus 09B2499", "col_header": "MIC (μg/ml) / LZ1", "value": "2.3"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "S. aureus 09B2499", "col_header": "MIC (μg/ml) / CL", "value": "1.2"}]}, {"table_index": 2, "label": "Table 2", "caption": "The number of P. acnes colonized within the ear after epicutaneous application of LZ1.", "footnotes": ["Data represent mean of four individual experiments."], "header_rows": [["", "P. acnes (103 CFU per ear)", "P. acnes (103 CFU per ear)", "P. acnes (103 CFU per ear)", "P. acnes (103 CFU per ear)", "P. acnes (103 CFU per ear)"], ["", "Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Vehicle", "col_header": "P. acnes (103 CFU per ear) / Day 1", "value": "844±89"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Vehicle", "col_header": "P. acnes (103 CFU per ear) / Day 2", "value": "78±8.2"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "Vehicle", "col_header": "P. acnes (103 CFU per ear) / Day 3", "value": "34±2.0"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "Vehicle", "col_header": "P. acnes (103 CFU per ear) / Day 4", "value": "21±1.8"}, {"table_index": 2, "row_index": 3, "col_index": 6, "row_label": "Vehicle", "col_header": "P. acnes (103 CFU per ear) / Day 5", "value": "3±0.3"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Clindamycin", "col_header": "P. acnes (103 CFU per ear) / Day 1", "value": "360±77"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Clindamycin", "col_header": "P. acnes (103 CFU per ear) / Day 2", "value": "32±4.1"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "Clindamycin", "col_header": "P. acnes (103 CFU per ear) / Day 3", "value": "14±1.7"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "Clindamycin", "col_header": "P. acnes (103 CFU per ear) / Day 4", "value": "6±0.5"}, {"table_index": 2, "row_index": 4, "col_index": 6, "row_label": "Clindamycin", "col_header": "P. acnes (103 CFU per ear) / Day 5", "value": "1.5±0.1"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "LZ1", "col_header": "P. acnes (103 CFU per ear) / Day 1", "value": "210±34"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "LZ1", "col_header": "P. acnes (103 CFU per ear) / Day 2", "value": "29±5.4"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "LZ1", "col_header": "P. acnes (103 CFU per ear) / Day 3", "value": "10±1.5"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "LZ1", "col_header": "P. acnes (103 CFU per ear) / Day 4", "value": "5±0.4"}, {"table_index": 2, "row_index": 5, "col_index": 6, "row_label": "LZ1", "col_header": "P. acnes (103 CFU per ear) / Day 5", "value": "1.3±0.1"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "<5.6% Cytotoxicity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 2592", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "<5.6% Cytotoxicity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 2592", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "CAMP", "db_subject_text": "Cutibacterium acnes ATCC 6919[MIC = 0.6 microg/ml], Cutibacterium acnes ATCC 11827[MIC = 0.6 microg/ml], Cutibacterium acnes[MIC = 0.6 microg/ml], Staphylococcus epidermidis 09A3726[MIC = 4.7 microg/ml], Staphylococcus epidermidis 09B2490[MIC = 2.3 microg/ml], Staphylococcus aureus ATCC 2592[MIC = 2.3 microg/ml]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).