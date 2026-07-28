
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
doi__10.3390_toxins13120867

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Sequences, molecular masses, and retention times of peptides.", "footnotes": ["a The retention time (TR) of each peptide was determined by the maximum height of the peaks from RP-HPLC, which indicates the hydrophobicity of the peptides."], "header_rows": [["Peptides", "Sequence", "Mw (Da)", "TR a (min)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "LVTX-9", "col_header": "Sequence", "value": "NH2-ASIGALIQKAIALIKAKAA-CONH2"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "LVTX-9", "col_header": "Mw (Da)", "value": "1851.28"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "LVTX-9", "col_header": "TR a (min)", "value": "15.21"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "LVTX-9-C12", "col_header": "Sequence", "value": "CH3-(CH2)10-CONHASIGALIQKAIALIKAKAA-CONH2"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "LVTX-9-C12", "col_header": "Mw (Da)", "value": "2033.64"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "LVTX-9-C12", "col_header": "TR a (min)", "value": "36.52"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "LVTX-9-C14", "col_header": "Sequence", "value": "CH3-(CH2)12-CONHASIGALIQKAIALIKAKAA-CONH2"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "LVTX-9-C14", "col_header": "Mw (Da)", "value": "2061.65"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "LVTX-9-C14", "col_header": "TR a (min)", "value": "36.15"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "LVTX-9-C16", "col_header": "Sequence", "value": "CH3-(CH2)14-CONHASIGALIQKAIALIKAKAA-CONH2"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "LVTX-9-C16", "col_header": "Mw (Da)", "value": "2089.70"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "LVTX-9-C16", "col_header": "TR a (min)", "value": "40.21"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "LVTX-9-C18", "col_header": "Sequence", "value": "CH3-(CH2)16-CONHASIGALIQKAIALIKAKAA-CONH2"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "LVTX-9-C18", "col_header": "Mw (Da)", "value": "2117.76"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "LVTX-9-C18", "col_header": "TR a (min)", "value": "41.89"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "LVTX-9-C20", "col_header": "Sequence", "value": "CH3-(CH2)18-CONHASIGALIQKAIALIKAKAA-CONH2"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "LVTX-9-C20", "col_header": "Mw (Da)", "value": "2145.81"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "LVTX-9-C20", "col_header": "TR a (min)", "value": "43.06"}]}, {"table_index": 2, "label": "Table 2", "caption": "The cytotoxic activities (IC50) of LVTX-9 and LVTX-9-C18.", "footnotes": [], "header_rows": [["IC50 (μM)", "IC50 (μM)", "IC50 (μM)", "IC50 (μM)", "IC50 (μM)", "IC50 (μM)"], ["Peptides", "L-929", "A549", "4T1", "HepG2", "Hela"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "LVTX-9", "col_header": "IC50 (μM) / L-929", "value": ">100"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "LVTX-9", "col_header": "IC50 (μM) / A549", "value": "51.7 ± 4.3"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "LVTX-9", "col_header": "IC50 (μM) / 4T1", "value": ">100"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "LVTX-9", "col_header": "IC50 (μM) / HepG2", "value": ">100"}, {"table_index": 2, "row_index": 3, "col_index": 6, "row_label": "LVTX-9", "col_header": "IC50 (μM) / Hela", "value": ">100"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "LVTX-9-C18", "col_header": "IC50 (μM) / L-929", "value": "3.6 ± 1.0"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "LVTX-9-C18", "col_header": "IC50 (μM) / A549", "value": "6.2 ± 1.4"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "LVTX-9-C18", "col_header": "IC50 (μM) / 4T1", "value": "7.6 ± 1.3"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "LVTX-9-C18", "col_header": "IC50 (μM) / HepG2", "value": "7.0 ± 1.0"}, {"table_index": 2, "row_index": 4, "col_index": 6, "row_label": "LVTX-9-C18", "col_header": "IC50 (μM) / Hela", "value": "4.7 ± 1.4"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "0% Hemolysis 200 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "10% Hemolysis 25 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "50% Hemolysis 50 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "0% Hemolysis 200 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "10% Hemolysis 25 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "50% Hemolysis 50 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).