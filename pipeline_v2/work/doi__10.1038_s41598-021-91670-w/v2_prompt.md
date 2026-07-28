
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
doi__10.1038_s41598-021-91670-w

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "IC50 for P1 and P3 acting on cancer cells in the apo- and holo-forms.", "footnotes": ["The range of concentrations corresponding to the 95% confidence interval are provided in parentheses.", "aFrom this work. Comparison to data in Lin et al.39 is provided in the text.", "bFirst data point at 0.16 µmol/L was not used to extract IC50 values due to large deviation from the trend line but all data points are displayed in Fig. 1."], "header_rows": [["IC50 (µmol/L)", "HT1080", "MDA-MB-231", "A549", "HeLa"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "P1", "col_header": "HT1080", "value": "5.58a (5.41–5.77)"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "P1", "col_header": "MDA-MB-231", "value": "5.83b (4.82–7.04)"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "P1", "col_header": "A549", "value": "4.20a (3.71–4.65)"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "P1", "col_header": "HeLa", "value": "2.22a (1.37–3.61)"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "P1-Cu2+", "col_header": "HT1080", "value": "5.31 (4.91–5.75)"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "P1-Cu2+", "col_header": "MDA-MB-231", "value": "3.92b (3.54–4.33)"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "P1-Cu2+", "col_header": "A549", "value": "2.15 (1.94–2.30)"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "P1-Cu2+", "col_header": "HeLa", "value": "2.17 (1.32–3.60)"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "P3", "col_header": "HT1080", "value": "26.01 (23.7–28.6)"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "P3", "col_header": "MDA-MB-231", "value": "17.5b (11.8–26.0)"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "P3", "col_header": "A549", "value": "21.6 (20.4–23.7)"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "P3", "col_header": "HeLa", "value": "18.1b (10.8–30.4)"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "P3-Cu2+", "col_header": "HT1080", "value": "5.52 (5.03–6.05)"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "P3-Cu2+", "col_header": "MDA-MB-231", "value": "5.25b (4.32–6.37)"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "P3-Cu2+", "col_header": "A549", "value": "2.99 (2.60–3.34)"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "P3-Cu2+", "col_header": "HeLa", "value": "1.97 (1.24–3.12)"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human fibrosarcoma HT1080", "db_measure": "IC50", "db_value": "5.52", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human breast adenocarcinoma MDA-MB-231", "db_measure": "IC50", "db_value": "5.25", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human lung carcinoma A549", "db_measure": "IC50", "db_value": "2.99", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human cervical carcinoma HeLa", "db_measure": "IC50", "db_value": "1,97", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).