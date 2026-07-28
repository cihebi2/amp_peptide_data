
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
doi__10.3390_cimb47080673

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "The characteristic of interested antimicrobial brevinin-1 E8.13 peptide.", "footnotes": [], "header_rows": [], "longform_cells": [{"table_index": 1, "row_index": 1, "col_index": 2, "row_label": "1FLGALFKVASKLVPAAICSFSKKC24", "col_header": "col1", "value": "1FLGALFKVASKLVPAAICSFSKKC24"}, {"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Length (residues)", "col_header": "col1", "value": "24"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Molecular weight", "col_header": "col1", "value": "2529.141"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Net charge", "col_header": "col1", "value": "+4"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Hydrophobic residue (%)", "col_header": "col1", "value": "62%"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Boman Index (kcal/mol)", "col_header": "col1", "value": "−0.62 kcal/mol"}]}, {"table_index": 2, "label": "Table 2", "caption": "The Agadir prediction of brevinin-1 E8.13 peptide.", "footnotes": ["* at 310 °K, ** at pH = 7."], "header_rows": [["pH *", "Predicted Helical Content", "Temperature (°K) **", "Predicted Helical Content"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "5.00", "col_header": "Predicted Helical Content", "value": "30%"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "5.00", "col_header": "Temperature (°K) **", "value": "273"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "5.00", "col_header": "Predicted Helical Content", "value": "69%"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "6.00", "col_header": "Predicted Helical Content", "value": "31%"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "6.00", "col_header": "Temperature (°K) **", "value": "278"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "6.00", "col_header": "Predicted Helical Content", "value": "71%"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "6.50", "col_header": "Predicted Helical Content", "value": "32%"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "6.50", "col_header": "Temperature (°K) **", "value": "290"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "6.50", "col_header": "Predicted Helical Content", "value": "54%"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "7.00", "col_header": "Predicted Helical Content", "value": "34%"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "7.00", "col_header": "Temperature (°K) **", "value": "310"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "7.00", "col_header": "Predicted Helical Content", "value": "36%"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "7.40", "col_header": "Predicted Helical Content", "value": "36%"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "7.40", "col_header": "Temperature (°K) **", "value": "320"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "7.40", "col_header": "Predicted Helical Content", "value": "30%"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "7.80", "col_header": "Predicted Helical Content", "value": "37%"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "7.80", "col_header": "Temperature (°K) **", "value": "330"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "7.80", "col_header": "Predicted Helical Content", "value": "25%"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "8.00", "col_header": "Predicted Helical Content", "value": "38%"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "8.00", "col_header": "Temperature (°K) **", "value": "340"}, {"table_index": 2, "row_index": 8, "col_index": 4, "row_label": "8.00", "col_header": "Predicted Helical Content", "value": "21%"}]}, {"table_index": 3, "label": "Table 3", "caption": "Antibacterial activity of brevinin-1 E8.13 and GA-K4AL.", "footnotes": ["Note: MIC is defined as the lowest peptide concentration that completely inhibits bacterial growth after 24 h of incubation."], "header_rows": [["Treatments", "MIC (μM)", "MIC (μM)", "MIC (μM)", "MIC (μM)", "MIC (μM)", "MIC (μM)"], ["S. aureus", "B. subtilis", "E. coli", "A. baumanii", "K. pneumonia", "P. aeruginosa"]], "longform_cells": [{"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "Brevinin-1 E8.13", "col_header": "MIC (μM) / S. aureus", "value": "1.5"}, {"table_index": 3, "row_index": 3, "col_index": 3, "row_label": "Brevinin-1 E8.13", "col_header": "MIC (μM) / B. subtilis", "value": ">24.8"}, {"table_index": 3, "row_index": 3, "col_index": 4, "row_label": "Brevinin-1 E8.13", "col_header": "MIC (μM) / E. coli", "value": ">24.8"}, {"table_index": 3, "row_index": 3, "col_index": 5, "row_label": "Brevinin-1 E8.13", "col_header": "MIC (μM) / A. baumanii", "value": ">24.8"}, {"table_index": 3, "row_index": 3, "col_index": 6, "row_label": "Brevinin-1 E8.13", "col_header": "MIC (μM) / K. pneumonia", "value": ">24.8"}, {"table_index": 3, "row_index": 3, "col_index": 7, "row_label": "Brevinin-1 E8.13", "col_header": "MIC (μM) / P. aeruginosa", "value": ">24.8"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "GA-K4AL", "col_header": "MIC (μM) / S. aureus", "value": "2.5"}, {"table_index": 3, "row_index": 4, "col_index": 3, "row_label": "GA-K4AL", "col_header": "MIC (μM) / B. subtilis", "value": ">41.8"}, {"table_index": 3, "row_index": 4, "col_index": 4, "row_label": "GA-K4AL", "col_header": "MIC (μM) / E. coli", "value": "10.1"}, {"table_index": 3, "row_index": 4, "col_index": 5, "row_label": "GA-K4AL", "col_header": "MIC (μM) / A. baumanii", "value": ">24.8"}, {"table_index": 3, "row_index": 4, "col_index": 6, "row_label": "GA-K4AL", "col_header": "MIC (μM) / K. pneumonia", "value": ">24.8"}, {"table_index": 3, "row_index": 4, "col_index": 7, "row_label": "GA-K4AL", "col_header": "MIC (μM) / P. aeruginosa", "value": ">24.8"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Cloning and Functional Characterization of a Novel Brevinin-1-Type Peptide from Sylvirana guentheri with Anticancer Activity.", "db_measure": "Unknown", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).