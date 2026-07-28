
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
doi__10.1038_s41598-017-02373-0

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "MIC of C14KKc12K against a representative panel of bacteria.", "footnotes": ["aMIC was determined by the microdilution method. Values represent the average of at least 2 independent experiments performed in duplicate."], "header_rows": [["Species (number of strains tested)", "MICa range (µM)"], ["Gram-positive bacteria"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Streptococci (9)", "col_header": "MICa range (µM)", "value": "0.78–3.12"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Staphylococci (10)", "col_header": "MICa range (µM)", "value": "1.56–3.12"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Enterococci (3)", "col_header": "MICa range (µM)", "value": "3.12–6.25"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Bacilli (2)", "col_header": "MICa range (µM)", "value": "6.25"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Listeria (6)", "col_header": "MICa range (µM)", "value": "3.12"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Escherichia (9)", "col_header": "MICa range (µM)", "value": "3.12–6.25"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Pseudomonas (3)", "col_header": "MICa range (µM)", "value": "6.25–12.5"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "Klebsiella (3)", "col_header": "MICa range (µM)", "value": "3.12–12.5"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "Acinetobacter (5)", "col_header": "MICa range (µM)", "value": "3.12–>25"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "Salmonella (1)", "col_header": "MICa range (µM)", "value": "3.12"}, {"table_index": 1, "row_index": 14, "col_index": 2, "row_label": "Fusobacterium (2)", "col_header": "MICa range (µM)", "value": "6.25"}, {"table_index": 1, "row_index": 15, "col_index": 2, "row_label": "Porphyromonas (1)", "col_header": "MICa range (µM)", "value": "3.12"}]}, {"table_index": 2, "label": "Table 2", "caption": "Modulating biophysical properties of a core sequence by conjugating an N-terminal acyl.", "footnotes": ["aR = N-terminal acyl, X = KKc12K;", "bHydrophobicity, defined as % acetonitrile eluent in C18 HPLC column;", "cMinimal inhibitory concentration as determined by the microdilution method over S. mutans and E. coli representing GPB and GNB, respectively."], "header_rows": [["RXa", "Hb (%)", "MICc (µM)", "Effect observed at low concentrations (<3 µM)"], ["S.m.", "E.c."]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "HX", "col_header": "RXa", "value": "27"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "HX", "col_header": "Hb (%)", "value": ">50"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "HX", "col_header": "MICc (µM)", "value": ">5040"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "HX", "col_header": "Effect observed at low concentrations (<3 µM)", "value": "Not observed (normal growth)"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "C8X", "col_header": "RXa", "value": "41"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "C8X", "col_header": "Hb (%)", "value": "50"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "C8X", "col_header": "MICc (µM)", "value": ">5040"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "C8X", "col_header": "Effect observed at low concentrations (<3 µM)", "value": "Weak perturbations of GNB outer membrane (normal growth)"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "C10X", "col_header": "RXa", "value": "46"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "C10X", "col_header": "Hb (%)", "value": "6.25"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "C10X", "col_header": "MICc (µM)", "value": ">5040"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "C10X", "col_header": "Effect observed at low concentrations (<3 µM)", "value": "Weak growth inhibition of some GPB and transient membrane damages including partial depolarization of CM (slight delay in GNB growth)"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "C12X", "col_header": "RXa", "value": "51"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "C12X", "col_header": "Hb (%)", "value": "1.56"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "C12X", "col_header": "MICc (µM)", "value": "1640"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "C12X", "col_header": "Effect observed at low concentrations (<3 µM)", "value": "Impairing membrane damages leading to a bacteriostatic mode of action in GPB; OM permeabilization & delayed growth in GNB"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "C14X", "col_header": "RXa", "value": "54"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "C14X", "col_header": "Hb (%)", "value": "0.78"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "C14X", "col_header": "MICc (µM)", "value": "3.12"}, {"table_index": 2, "row_index": 7, "col_index": 5, "row_label": "C14X", "col_header": "Effect observed at low concentrations (<3 µM)", "value": "High efficacy in membranes disruption leading to a bactericidal mode of action in both GPB & GNB"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "C16X", "col_header": "RXa", "value": "62"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "C16X", "col_header": "Hb (%)", "value": "1.56"}, {"table_index": 2, "row_index": 8, "col_index": 4, "row_label": "C16X", "col_header": "MICc (µM)", "value": "2524"}, {"table_index": 2, "row_index": 8, "col_index": 5, "row_label": "C16X", "col_header": "Effect observed at low concentrations (<3 µM)", "value": "Trend reversal (reduced potency) due to excess hydrophobicity as self-assembly approaches the critical aggregation concentration"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Streptococcus mutans ATCC 35668", "db_measure": "MBEC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Streptococcus mutans ATCC 35668", "db_measure": "MBEC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now.