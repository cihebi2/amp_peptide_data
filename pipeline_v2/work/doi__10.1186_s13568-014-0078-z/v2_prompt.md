
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
doi__10.1186_s13568-014-0078-z

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "MIC values of SP1 tested against bacterial strains", "footnotes": ["MIC values for each strain are the means of three different assays performed in duplicate"], "header_rows": [["Bacterial strains", "MIC (mg/ml)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "S. aureus ATCC 25923", "col_header": "MIC (mg/ml)", "value": "12.5"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "S. aureus ATCC 29213", "col_header": "MIC (mg/ml)", "value": "12.5"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "S. aureus ATCC 6538", "col_header": "MIC (mg/ml)", "value": "12.5"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "S. epidermidis RP62A", "col_header": "MIC (mg/ml)", "value": "6.2"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "S. aureus 100", "col_header": "MIC (mg/ml)", "value": "12.5"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "S. aureus 657", "col_header": "MIC (mg/ml)", "value": "6.2"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "S. aureus 700", "col_header": "MIC (mg/ml)", "value": "12.5"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "S. aureus 702", "col_header": "MIC (mg/ml)", "value": "12.5"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "P. aeruginosa ATCC15442", "col_header": "MIC (mg/ml)", "value": "12.5"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Rabbit erythrocytes", "db_measure": "-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Rabbit erythrocytes", "db_measure": "-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "APD6", "db_subject_text": "", "db_measure": "APD analysis reveals that the sequence of this peptide most resembles (38.5% similarity) Jelleine-III. Three peptides (5-CC) were initially isolated (D. Schillaci et al., J Applied Microbiol 108:17-24; Schillaci D et al. 2012 Ann N Y Acad Sci 1270:79-85) and the smallest one (called SP1) was chemically synthesized here. SP1 inhibits S. aureus and P. aeruginosa in the planktonic and biofilm forms (0.75-3.1 ug/ml). Planktonic bacteria include S. aureus ATCC 25923, S. aureus ATCC 29213, S. aureus ATCC 6538, S. epidermidis RP62A, S. aureus 100, S. aureus 657,S. aureus 700, S. aureus 702, and P. aeruginosa ATCC15442 (MIC 6.2-12.5 mg/ml). Provided by Luigi Inguglia and Vincenzo Arizza.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "CAMP", "db_subject_text": "Staphylococcus aureus ATCC 25923(MIC = 12.5 microg/ml), S. epidermidis RP62A (MIC = 6.2 microg/ml), P. aeruginosa ATCC15442 (MIC = 12.5 microg/ml)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).