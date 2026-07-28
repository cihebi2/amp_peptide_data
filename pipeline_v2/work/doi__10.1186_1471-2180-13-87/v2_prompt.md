
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
doi__10.1186_1471-2180-13-87

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "The minimum inhibitory concentrations (MICs) of lipopeptide antibiotics (PE1 and PE2) produced by Paenibacillus ehimensis B7", "footnotes": [], "header_rows": [["Indicator strain", "MIC (μg/mL)", "MIC (μg/mL)", "MIC (μg/mL)"], ["", "PE1", "PE2", "polymyxin B"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Staphylococcus epidermidis CMCC 26069", "col_header": "MIC (μg/mL) / PE1", "value": "1"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Staphylococcus epidermidis CMCC 26069", "col_header": "MIC (μg/mL) / PE2", "value": "1"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Staphylococcus epidermidis CMCC 26069", "col_header": "MIC (μg/mL) / polymyxin B", "value": "4"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Staphylococcus aureus ATCC 25923", "col_header": "MIC (μg/mL) / PE1", "value": "8"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Staphylococcus aureus ATCC 25923", "col_header": "MIC (μg/mL) / PE2", "value": "8"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "Staphylococcus aureus ATCC 25923", "col_header": "MIC (μg/mL) / polymyxin B", "value": "64"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Staphylococcus aureus ATCC 43300", "col_header": "MIC (μg/mL) / PE1", "value": "4"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Staphylococcus aureus ATCC 43300", "col_header": "MIC (μg/mL) / PE2", "value": "4"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "Staphylococcus aureus ATCC 43300", "col_header": "MIC (μg/mL) / polymyxin B", "value": "32"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Escherichia coli ATCC 35318", "col_header": "MIC (μg/mL) / PE1", "value": "8"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Escherichia coli ATCC 35318", "col_header": "MIC (μg/mL) / PE2", "value": "8"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "Escherichia coli ATCC 35318", "col_header": "MIC (μg/mL) / polymyxin B", "value": "2"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Escherichia coli 5539", "col_header": "MIC (μg/mL) / PE1", "value": "4"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "Escherichia coli 5539", "col_header": "MIC (μg/mL) / PE2", "value": "4"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "Escherichia coli 5539", "col_header": "MIC (μg/mL) / polymyxin B", "value": "1"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Pseudomonas aeruginosa ATCC 27853", "col_header": "MIC (μg/mL) / PE1", "value": "8"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "Pseudomonas aeruginosa ATCC 27853", "col_header": "MIC (μg/mL) / PE2", "value": "4"}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "Pseudomonas aeruginosa ATCC 27853", "col_header": "MIC (μg/mL) / polymyxin B", "value": "2"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Pseudomonas aeruginosa 5215", "col_header": "MIC (μg/mL) / PE1", "value": "2"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "Pseudomonas aeruginosa 5215", "col_header": "MIC (μg/mL) / PE2", "value": "2"}, {"table_index": 1, "row_index": 9, "col_index": 4, "row_label": "Pseudomonas aeruginosa 5215", "col_header": "MIC (μg/mL) / polymyxin B", "value": "4"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Candida albicans ATCC 10231", "col_header": "MIC (μg/mL) / PE1", "value": "8"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "Candida albicans ATCC 10231", "col_header": "MIC (μg/mL) / PE2", "value": "8"}, {"table_index": 1, "row_index": 10, "col_index": 4, "row_label": "Candida albicans ATCC 10231", "col_header": "MIC (μg/mL) / polymyxin B", "value": "64"}]}, {"table_index": 2, "label": "Table 2", "caption": "Effect of divalent cations on antibacterial activity of lipopeptide antibiotics (PE1 and PE2) produced by Paenibacillus ehimensis B7", "footnotes": [], "header_rows": [["Antibiotic", "MIC (μg/mL)", "MIC (μg/mL)"], ["", "P. aeruginosa ATCC 27853", "S. aureus ATCC 43300"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "PE1", "col_header": "MIC (μg/mL) / P. aeruginosa ATCC 27853", "value": "8"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "PE1", "col_header": "MIC (μg/mL) / S. aureus ATCC 43300", "value": "4"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "PE1 + 10 mM CaCl2", "col_header": "MIC (μg/mL) / P. aeruginosa ATCC 27853", "value": ">64"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "PE1 + 10 mM CaCl2", "col_header": "MIC (μg/mL) / S. aureus ATCC 43300", "value": "8"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "PE1 + 10 mM MgCl2", "col_header": "MIC (μg/mL) / P. aeruginosa ATCC 27853", "value": ">64"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "PE1 + 10 mM MgCl2", "col_header": "MIC (μg/mL) / S. aureus ATCC 43300", "value": "8"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 35218", "db_measure": "MIC", "db_value": "8", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 35218", "db_measure": "MIC", "db_value": "8", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 35218", "db_measure": "MIC", "db_value": "8", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 35218", "db_measure": "MIC", "db_value": "8", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "CAMP", "db_subject_text": "Staphylococcus epidermidis CMCC 26069[MIC = 1 microg/ml], Staphylococcus aureus ATCC 25923[MIC = 8 microg/ml], Staphylococcus aureus ATCC 43300[MIC = 4 microg/ml], Staphylococcus aureus ATCC 43300[MIC = 8 microg/ml], Escherichia coli ATCC 35218[MIC = 8 microg/ml], Escherichia coli[MIC = 4 microg/ml], Pseudomonas aeruginosa ATCC 27853[MIC = 8 microg/ml], Pseudomonas aeruginosa ATCC 27853[MIC >64 microg/ml], Pseudomonas aeruginosa[MIC = 2 microg/ml], Candida albicans ATCC 10231[MIC = 8 microg/ml], Pseudomonas aeruginosa ATCC 27853[MIC = 4 microg/ml]", "db_measure": "Gram+, Gram-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "dbAMP", "db_subject_text": "Staphylococcus epidermidis CMCC 26069 (MIC=1μg/ml)\nStaphylococcus aureus ATCC 25923 (MIC=8μg/ml)\nStaphylococcus aureus ATCC 43300 (MIC=4μg/ml)\nEscherichia coli ATCC 35218 (MIC=8μg/ml)\nEscherichia coli (MIC=4μg/ml)\nPseudomonas aeruginosa ATCC 27853 (MIC=4μg/ml)\nPseudomonas aeruginosa (MIC=2μg/ml)\nCandida albicans ATCC 10231 (MIC=8μg/ml)", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).