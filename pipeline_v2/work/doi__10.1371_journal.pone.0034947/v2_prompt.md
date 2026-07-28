
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
doi__10.1371_journal.pone.0034947

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "The charge, first and predict secondary structure of scorpion venom peptides.", "footnotes": ["h: alpha helix, c: random coil, e: extended strand."], "header_rows": [["Peptide", "Amino Acid Sequence", "Charge", "Cationic(%)", "Structure Prediction"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "BmKn2", "col_header": "Amino Acid Sequence", "value": "FIGAIARLLSKIF"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "BmKn2", "col_header": "Charge", "value": "2"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "BmKn2", "col_header": "Cationic(%)", "value": "15.38"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "BmKn2", "col_header": "Structure Prediction", "value": "chhhhhhhhhhcc"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Kn2-7", "col_header": "Amino Acid Sequence", "value": "FIKRIARLLRKIF"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Kn2-7", "col_header": "Charge", "value": "5"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Kn2-7", "col_header": "Cationic(%)", "value": "38.46"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "Kn2-7", "col_header": "Structure Prediction", "value": "chhhhhhhhhhhc"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "mucroporin", "col_header": "Amino Acid Sequence", "value": "LFGLIPSLIGGLVSAFK"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "mucroporin", "col_header": "Charge", "value": "1"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "mucroporin", "col_header": "Cationic(%)", "value": "5.88"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "mucroporin", "col_header": "Structure Prediction", "value": "cccchhhhhhhhhhhhc"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "mucroporin-M1", "col_header": "Amino Acid Sequence", "value": "LFRLIKSLIKRLVSAFK"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "mucroporin-M1", "col_header": "Charge", "value": "5"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "mucroporin-M1", "col_header": "Cationic(%)", "value": "29.41"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "mucroporin-M1", "col_header": "Structure Prediction", "value": "chhhhhhhhhhhhhhhc"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "mucropotin-S1", "col_header": "Amino Acid Sequence", "value": "SLIGGLVSAFK"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "mucropotin-S1", "col_header": "Charge", "value": "1"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "mucropotin-S1", "col_header": "Cationic(%)", "value": "9.09"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "mucropotin-S1", "col_header": "Structure Prediction", "value": "ccccccceccc"}]}, {"table_index": 2, "label": "Table 2", "caption": "Anti-HIV-1 PV activities and cytotoxicity of Kn2-7 peptide on TZM-bl cells.", "footnotes": ["EC50: peptide concentration required to reduce virus infection by 50%; CC50: peptide concentration required to reduce cell viability by 50%; SI (selectivity index) = CC50/EC50; I: inactive.", "All the data represent mean values for at least three independent experiments."], "header_rows": [["", "EC50 a(µg/ml)", "CC50 a(µg/ml)", "SI"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Kn2-7", "col_header": "EC50 a(µg/ml)", "value": "2.76"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Kn2-7", "col_header": "CC50 a(µg/ml)", "value": "38.46"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "Kn2-7", "col_header": "SI", "value": "13.93"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "mucroporin-S1", "col_header": "EC50 a(µg/ml)", "value": "I"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "mucroporin-S1", "col_header": "CC50 a(µg/ml)", "value": ">100"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "HIV-1 PsV", "db_measure": "IC50 I 2.76 µg/ml", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human adenocarcinoma TZM-bl", "db_measure": "IC50 38.46 µg/ml", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human adenocarcinoma TZM-bl", "db_measure": "IC50 >100 µg/ml", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "HIV-1 PsV", "db_measure": "IC50 I 2.76 µg/ml", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Human adenocarcinoma TZM-bl", "db_measure": "IC50 38.46 µg/ml", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Human adenocarcinoma TZM-bl", "db_measure": "IC50 >100 µg/ml", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "CAMP", "db_subject_text": "SARS-CoV PsV, Human Influenza A Virus H5N1 PsV, HIV-1 PsV, Human adenocarcinoma TZM-bl[IC50 >100 microg/ml]", "db_measure": "entry text: Antiviral; Has anticancer activity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).