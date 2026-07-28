
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
doi__10.1039_d1sc07190d

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "a", "caption": "MIC values for laspartomycin C, compounds 2–9, and friulimicin B", "footnotes": ["Minimum inhibitory concentration reported in μg mL−1 against MRSA USA 300 at a Ca2+ concentration of 10 mM. All compounds tested in triplicate.", "Natural product."], "header_rows": [["Compound", "AA1", "AA4", "AA9", "AA10", "MICa"], ["1 (LaspC)", "l-Asp", "Gly", "d-allo-Thr", "l-Ile", "2"], ["2", "l-Asn", "Gly", "d-allo-Thr", "l-Ile", "4"], ["3", "l-Asp", "l-Asp", "d-allo-Thr", "l-Ile", "16"], ["4", "l-Asp", "Gly", "d-Dap", "l-Ile", "4"], ["5", "l-Asp", "l-Asp", "d-Dap", "l-Ile", "8"], ["6", "l-Asp", "l-Asp", "d-Dap", "l-Val", "1"], ["7", "l-Asn", "l-Asp", "d-Dap", "l-Val", "2"], ["8", "l-Asp", "l-Asp", "d-allo-Thr", "l-Val", "4"], ["9", "l-Asp", "Gly", "d-Dap", "l-Val", "8"], ["Friulimicin Bb", "l-Asn", "MeAsp", "d-Dab", "l-Val", "1–2"]], "longform_cells": []}, {"table_index": 2, "label": "a", "caption": "MIC values for laspartomycin C position 10 variants", "footnotes": ["Minimum inhibitory concentration reported in μg mL−1 against MRSA USA 300 at the Ca2+ concentration indicated. All compounds tested in triplicate."], "header_rows": [["Compound", "AA10", "R", "MICa", "MICa"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "1 mM Ca2+", "col_header": "AA10", "value": "10 mM Ca2+"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "1 (LaspC)", "col_header": "AA10", "value": "l-Ile"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "1 (LaspC)", "col_header": "MICa", "value": "8"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "1 (LaspC)", "col_header": "MICa", "value": "2"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "10", "col_header": "AA10", "value": "Gly"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "10", "col_header": "MICa", "value": ">64"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "10", "col_header": "MICa", "value": ">64"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "11", "col_header": "AA10", "value": "l-Ala"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "11", "col_header": "MICa", "value": "64"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "11", "col_header": "MICa", "value": "8"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "12", "col_header": "AA10", "value": "l-Abu"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "12", "col_header": "MICa", "value": "32"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "12", "col_header": "MICa", "value": "8"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "13", "col_header": "AA10", "value": "l-Nval"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "13", "col_header": "MICa", "value": "16"}, {"table_index": 2, "row_index": 7, "col_index": 5, "row_label": "13", "col_header": "MICa", "value": "4"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "14", "col_header": "AA10", "value": "l-Val"}, {"table_index": 2, "row_index": 8, "col_index": 4, "row_label": "14", "col_header": "MICa", "value": "8"}, {"table_index": 2, "row_index": 8, "col_index": 5, "row_label": "14", "col_header": "MICa", "value": "2"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "15", "col_header": "AA10", "value": "l-Phe"}, {"table_index": 2, "row_index": 9, "col_index": 4, "row_label": "15", "col_header": "MICa", "value": "16"}, {"table_index": 2, "row_index": 9, "col_index": 5, "row_label": "15", "col_header": "MICa", "value": "8"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Enterococcus faecium", "db_measure": "MIC", "db_value": "4", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Enterococcus faecium", "db_measure": "MIC", "db_value": "2", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).