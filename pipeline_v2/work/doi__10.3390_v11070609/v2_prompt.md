
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
doi__10.3390_v11070609

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Thermodynamic parameters of the interactions between the N- and C- terminal heptad repeats (NHR- and CHR-derived) peptides determined by isothermal titration calorimetry (ITC).", "footnotes": [], "header_rows": [["Peptide Pair", "N", "K (M−1)", "△H (Kcal/mol)", "△S (cal/mol/deg)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "N39/T20", "col_header": "N", "value": "0.9"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "N39/T20", "col_header": "K (M−1)", "value": "3.2 × 106"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "N39/T20", "col_header": "△H (Kcal/mol)", "value": "−22.6"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "N39/T20", "col_header": "△S (cal/mol/deg)", "value": "−45.9"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "N39/T20N145A", "col_header": "N", "value": "2.6"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "N39/T20N145A", "col_header": "K (M−1)", "value": "3.6 × 104"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "N39/T20N145A", "col_header": "△H (Kcal/mol)", "value": "−13.5"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "N39/T20N145A", "col_header": "△S (cal/mol/deg)", "value": "−30.7"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "N36/C34", "col_header": "N", "value": "1.3"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "N36/C34", "col_header": "K (M−1)", "value": "3.3 × 106"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "N36/C34", "col_header": "△H (Kcal/mol)", "value": "−15.4"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "N36/C34", "col_header": "△S (cal/mol/deg)", "value": "−15.5"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "N36/C34N145A", "col_header": "N", "value": "1.1"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "N36/C34N145A", "col_header": "K (M−1)", "value": "2.2 × 106"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "N36/C34N145A", "col_header": "△H (Kcal/mol)", "value": "−13.1"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "N36/C34N145A", "col_header": "△S (cal/mol/deg)", "value": "−14.8"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "N36/SC29EK", "col_header": "N", "value": "1.1"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "N36/SC29EK", "col_header": "K (M−1)", "value": "2.6 × 106"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "N36/SC29EK", "col_header": "△H (Kcal/mol)", "value": "−15.8"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "N36/SC29EK", "col_header": "△S (cal/mol/deg)", "value": "−23.6"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "N36/SC28EK", "col_header": "N", "value": "1.3"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "N36/SC28EK", "col_header": "K (M−1)", "value": "5.2 × 105"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "N36/SC28EK", "col_header": "△H (Kcal/mol)", "value": "−9.0"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "N36/SC28EK", "col_header": "△S (cal/mol/deg)", "value": "−3.66"}]}, {"table_index": 2, "label": "Table 2", "caption": "Crystallographic data collection and refinement statistics.", "footnotes": ["a Values in parentheses are the statistics in the highest-resolution shell. b Rmerge =∑hkl∑j |Ihkl,j- I hkl |/∑ hkl∑j Ihkl,j, and Ihkl is the average of symmetry-related observations of a unique reflection. c Rwork = ∑hkl||Fobs|−|Fcalc||/∑hkl|Fobs|, where h, k, and l are the indices of the reflections and Fobs and Fcalc are the observed and calculated structure factors deduced from the model, respectively. Rfree is defined as cross-validation R factor for 5% of reflections against which the model was not refined."], "header_rows": [["Parameter", "Value a"], ["Data Collection", ""], ["Beamline", "SSRF BL17U"]], "longform_cells": [{"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Wavelength (Å)", "col_header": "Value a / SSRF BL17U", "value": "0.97915"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Resolution rage", "col_header": "Value a / SSRF BL17U", "value": "45.000–2.33 (2.47–2.33)"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Space group", "col_header": "Value a / SSRF BL17U", "value": "P212121"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "a, b, c (Å)", "col_header": "Value a / SSRF BL17U", "value": "36.500, 39.860, 171.503"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "a, b, g (°)", "col_header": "Value a / SSRF BL17U", "value": "90.00, 90.00, 90.00"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "Redundancy", "col_header": "Value a / SSRF BL17U", "value": "3.19"}, {"table_index": 2, "row_index": 11, "col_index": 2, "row_label": "Total no of reflections", "col_header": "Value a / SSRF BL17U", "value": "66,040"}, {"table_index": 2, "row_index": 12, "col_index": 2, "row_label": "No. of unique reflections", "col_header": "Value a / SSRF BL17U", "value": "20,721"}, {"table_index": 2, "row_index": 13, "col_index": 2, "row_label": "Rmergeb(%)", "col_header": "Value a / SSRF BL17U", "value": "8.3 (86.1)"}, {"table_index": 2, "row_index": 14, "col_index": 2, "row_label": "I/SIGMA", "col_header": "Value a / SSRF BL17U", "value": "10.16 (1.53)"}, {"table_index": 2, "row_index": 15, "col_index": 2, "row_label": "Completeness (%)", "col_header": "Value a / SSRF BL17U", "value": "98.0 (90.6)"}, {"table_index": 2, "row_index": 17, "col_index": 2, "row_label": "Resolution (Å)", "col_header": "Value a / SSRF BL17U", "value": "38.825–2.330 (2.44–2.33)"}, {"table_index": 2, "row_index": 18, "col_index": 2, "row_label": "No. of reflections", "col_header": "Value a / SSRF BL17U", "value": "11,172"}, {"table_index": 2, "row_index": 19, "col_index": 2, "row_label": "Rwork/Rfreec", "col_header": "Value a / SSRF BL17U", "value": "0.2330/0.2859"}, {"table_index": 2, "row_index": 21, "col_index": 2, "row_label": "Protein", "col_header": "Value a / SSRF BL17U", "value": "1762"}, {"table_index": 2, "row_index": 22, "col_index": 2, "row_label": "Water", "col_header": "Value a / SSRF BL17U", "value": "10"}, {"table_index": 2, "row_index": 24, "col_index": 2, "row_label": "Protein", "col_header": "Value a / SSRF BL17U", "value": "67.28"}, {"table_index": 2, "row_index": 25, "col_index": 2, "row_label": "Water", "col_header": "Value a / SSRF BL17U", "value": "60.77"}, {"table_index": 2, "row_index": 27, "col_index": 2, "row_label": "Bond lengths (Å)", "col_header": "Value a / SSRF BL17U", "value": "0.003"}, {"table_index": 2, "row_index": 28, "col_index": 2, "row_label": "Bond angles (°)", "col_header": "Value a / SSRF BL17U", "value": "0.491"}, {"table_index": 2, "row_index": 30, "col_index": 2, "row_label": "Favored", "col_header": "Value a / SSRF BL17U", "value": "97.95%"}, {"table_index": 2, "row_index": 31, "col_index": 2, "row_label": "Allowed", "col_header": "Value a / SSRF BL17U", "value": "1.54%"}, {"table_index": 2, "row_index": 32, "col_index": 2, "row_label": "Disallowed", "col_header": "Value a / SSRF BL17U", "value": "0.51%"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "CAMP", "db_subject_text": "HIV-1 NL4-3 PsV[IC50 E = 0.0012 microM], HIV-1 HxB2[IC50 F = 0.0008 microM]", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "HIV-1 NL4-3 PsV[IC50 E = 0.001 microM], HIV-1 HxB2[IC50 F = 0.0007 microM]", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).