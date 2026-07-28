
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
doi__10.3892_ol.2012.1042

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table I.", "caption": "Cliotides involved in the present study.", "footnotes": ["MW, molecular weight, reported as monoisotopic mass; B, bracelet; M, Möbius. Cysteine residues are in bold."], "header_rows": [["Cliotide", "Sequence", "MWa", "Net charge", "Subfamily"], ["CT2", "GEFLKCGESCVQGEC–YT– –PGCSCDWPICKKN", "3260", "−1", "M"], ["CT4", "GIP– – CGESCVFIPC–ITAAIGCSCKSKVCYRN", "3098", "+2", "B"], ["CT7", "GIP– – CGESCVFIPCTVTALLGCSCKDKVCYKN", "3227", "+1", "B"]], "longform_cells": [{"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "CT10", "col_header": "Sequence / GEFLKCGESCVQGEC–YT– –PGCSCDWPICKKN / GIP– – CGESCVFIPC–ITAAIGCSCKSKVCYRN / GIP– – CGESCVFIPCTVTALLGCSCKDKVCYKN", "value": "GVP– –CAESCVWIPCTVTALLGCSCKDKVCYLN"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "CT10", "col_header": "MWa / 3260 / 3098 / 3227", "value": "3251"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "CT10", "col_header": "Net charge / −1 / +2 / +1", "value": "0"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "CT10", "col_header": "Subfamily / M / B", "value": "B"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "CT12", "col_header": "Sequence / GEFLKCGESCVQGEC–YT– –PGCSCDWPICKKN / GIP– – CGESCVFIPC–ITAAIGCSCKSKVCYRN / GIP– – CGESCVFIPCTVTALLGCSCKDKVCYKN", "value": "GIP– –CGESCVYIPCTVTALLGCSCKDKVCYKN"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "CT12", "col_header": "MWa / 3260 / 3098 / 3227", "value": "3243"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "CT12", "col_header": "Net charge / −1 / +2 / +1", "value": "+1"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "CT12", "col_header": "Subfamily / M / B", "value": "B"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "CT19", "col_header": "Sequence / GEFLKCGESCVQGEC–YT– –PGCSCDWPICKKN / GIP– – CGESCVFIPC–ITAAIGCSCKSKVCYRN / GIP– – CGESCVFIPCTVTALLGCSCKDKVCYKN", "value": "GSVIKCGESCLLGKC–YT– –PGCTCSRPICKKD"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "CT19", "col_header": "MWa / 3260 / 3098 / 3227", "value": "3125"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "CT19", "col_header": "Net charge / −1 / +2 / +1", "value": "+4"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "CT19", "col_header": "Subfamily / M / B", "value": "B"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "CT20", "col_header": "Sequence / GEFLKCGESCVQGEC–YT– –PGCSCDWPICKKN / GIP– – CGESCVFIPC–ITAAIGCSCKSKVCYRN / GIP– – CGESCVFIPCTVTALLGCSCKDKVCYKN", "value": "GSAIRCGESCLLGKC–YT– –PGCTCDRPICKKN"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "CT20", "col_header": "MWa / 3260 / 3098 / 3227", "value": "3152"}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "CT20", "col_header": "Net charge / −1 / +2 / +1", "value": "+3"}, {"table_index": 1, "row_index": 8, "col_index": 5, "row_label": "CT20", "col_header": "Subfamily / M / B", "value": "B"}]}, {"table_index": 2, "label": "Table II.", "caption": "Half maximal inhibitory concentration (IC50μM) of cliotides in the human lung cell line (A549) and its drug resistant cell (A549/paclitaxel).", "footnotes": [], "header_rows": [["Cyclotides", "A549", "A549/paclitaxel", "Coexposure to paclitaxel"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "CT2", "col_header": "A549", "value": "7.59"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "CT2", "col_header": "A549/paclitaxel", "value": "7.92"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "CT2", "col_header": "Coexposure to paclitaxel", "value": "1.62"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "CT4", "col_header": "A549", "value": "0.21"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "CT4", "col_header": "A549/paclitaxel", "value": "0.45"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "CT4", "col_header": "Coexposure to paclitaxel", "value": "0.12"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "CT7", "col_header": "A549", "value": "0.73"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "CT7", "col_header": "A549/paclitaxel", "value": "1.76"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "CT7", "col_header": "Coexposure to paclitaxel", "value": "0.75"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "CT10", "col_header": "A549", "value": "0.70"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "CT10", "col_header": "A549/paclitaxel", "value": "2.53"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "CT10", "col_header": "Coexposure to paclitaxel", "value": "1.01"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "CT12", "col_header": "A549", "value": "0.78"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "CT12", "col_header": "A549/paclitaxel", "value": "1.6"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "CT12", "col_header": "Coexposure to paclitaxel", "value": "0.86"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "Paclitaxel", "col_header": "A549", "value": "1.21"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "Paclitaxel", "col_header": "A549/paclitaxel", "value": ">10"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "Paclitaxel", "col_header": "Coexposure to paclitaxel", "value": ">10"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Lett. 2013 Feb;5(2):641-644. Epub 2012 Nov 22. Chemosensitizing activities of cyclotides from Clitoria ternatea in paclitaxel-resistant lung cancer cells.", "db_measure": "Anti-Gram-, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Tumor cells: A549 (IC50=0.78 µM )", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "Tumor cells: A549 (IC50=9.59 µM )", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "Tumor cells: A549 (IC50>10 µM )", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DRAMP", "db_subject_text": "Tumor cells: A549 (IC50=0.78 µM )", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Cliotides T12, CT12"}, {"assertion_index": 5, "database": "DRAMP", "db_subject_text": "Tumor cells: A549 (IC50=9.59 µM )", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Cliotides T19, CT19"}, {"assertion_index": 6, "database": "DRAMP", "db_subject_text": "Tumor cells: A549 (IC50>10 µM )", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Cliotides T20, CT20"}]

Return ONLY the JSON array now (one object per assertion above).