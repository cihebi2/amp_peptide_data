
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
doi__10.1186_s40064-016-1854-9

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "The equilibrium model parameters for SODSs and rSODSs", "footnotes": ["aGibbs’ free energy of activation for an enzyme-catalyzed reaction", "bGibbs’ free energy of activation for the irreversible thermal inactivation of an enzyme", "cChange in enthalpy for the Eact to Einact transition", "dThe temperature at which the Eact–Einact equilibrium is at its midpoint"], "header_rows": [["Enzyme", "ΔG cat‡a (kJ mol−1)", "ΔG inact‡b (kJ mol−1)", "ΔH eqc (kJ mol−1)", "T eqd (°C)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "SODSs", "col_header": "ΔG cat‡a (kJ mol−1)", "value": "67.2"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "SODSs", "col_header": "ΔG inact‡b (kJ mol−1)", "value": "119.1"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "SODSs", "col_header": "ΔH eqc (kJ mol−1)", "value": "83.2"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "SODSs", "col_header": "T eqd (°C)", "value": "65.8"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "rSODSs", "col_header": "ΔG cat‡a (kJ mol−1)", "value": "67.1"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "rSODSs", "col_header": "ΔG inact‡b (kJ mol−1)", "value": "183.9"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "rSODSs", "col_header": "ΔH eqc (kJ mol−1)", "value": "112.7"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "rSODSs", "col_header": "T eqd (°C)", "value": "76.7"}]}, {"table_index": 2, "label": "Table 2", "caption": "Thermodynamic parameters of SODSs and rSODSs", "footnotes": ["a k d is the deactivation rate constant (min−1)", "bDecimal reduction time (D) is defined by Belitz and Gosch as the holding time required to reduce the enzymatic activity by one order of magnitude", "c t 1/2 is the half-life time", "d E d is the deactivation energy required to inactive the enzyme during a thermal inactivation process"], "header_rows": [["Enzymes", "T (°C)", "k d × 10−3a (min−1)", "D b (h)", "t 1/2c (h)", "E dd (kJ mol−1)"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "SODSs", "col_header": "T (°C)", "value": "90"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "SODSs", "col_header": "k d × 10−3a (min−1)", "value": "0.3"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "SODSs", "col_header": "D b (h)", "value": "127.9"}, {"table_index": 2, "row_index": 2, "col_index": 5, "row_label": "SODSs", "col_header": "t 1/2c (h)", "value": "38.5"}, {"table_index": 2, "row_index": 2, "col_index": 6, "row_label": "SODSs", "col_header": "E dd (kJ mol−1)", "value": "215.3"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "95", "col_header": "T (°C)", "value": "0.7"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "95", "col_header": "k d × 10−3a (min−1)", "value": "54.8"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "95", "col_header": "D b (h)", "value": "16.5"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "100", "col_header": "T (°C)", "value": "1.6"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "100", "col_header": "k d × 10−3a (min−1)", "value": "23.9"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "100", "col_header": "D b (h)", "value": "7.2"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "105", "col_header": "T (°C)", "value": "5.3"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "105", "col_header": "k d × 10−3a (min−1)", "value": "7.2"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "105", "col_header": "D b (h)", "value": "2.1"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "rSODSs", "col_header": "T (°C)", "value": "90"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "rSODSs", "col_header": "k d × 10−3a (min−1)", "value": "0.06"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "rSODSs", "col_header": "D b (h)", "value": "639.6"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "rSODSs", "col_header": "t 1/2c (h)", "value": "192.5"}, {"table_index": 2, "row_index": 6, "col_index": 6, "row_label": "rSODSs", "col_header": "E dd (kJ mol−1)", "value": "246.7"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "95", "col_header": "T (°C)", "value": "0.3"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "95", "col_header": "k d × 10−3a (min−1)", "value": "127.9"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "95", "col_header": "D b (h)", "value": "38.5"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "100", "col_header": "T (°C)", "value": "0.4"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "100", "col_header": "k d × 10−3a (min−1)", "value": "95.9"}, {"table_index": 2, "row_index": 8, "col_index": 4, "row_label": "100", "col_header": "D b (h)", "value": "28.8"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "105", "col_header": "T (°C)", "value": "2.0"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "105", "col_header": "k d × 10−3a (min−1)", "value": "19.1"}, {"table_index": 2, "row_index": 9, "col_index": 4, "row_label": "105", "col_header": "D b (h)", "value": "5.7"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Enhancing the antimicrobial activity of Sus scrofa lysozyme by N-terminal fusion of a sextuple unique homologous peptide", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "APD6", "db_subject_text": "S. scrofa lysozyme antimicrobial protein record; length 128 aa; organism Sus scrofa", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).