
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
doi__10.1371_journal.pone.0218479

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Amino acid sequence and predicted physico-chemical properties of BmKn-2 peptide and its derivatives.", "footnotes": [], "header_rows": [["Peptides", "Amino acid sequence", "Molecular weight (Da)", "Length", "Net charge", "Hydrophobicity (%)", "Helix", "Structure prediction"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "BmKn-2", "col_header": "Amino acid sequence", "value": "FIGAIARLLSKIF"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "BmKn-2", "col_header": "Molecular weight (Da)", "value": "1448.81"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "BmKn-2", "col_header": "Length", "value": "13"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "BmKn-2", "col_header": "Net charge", "value": "+2"}, {"table_index": 1, "row_index": 2, "col_index": 6, "row_label": "BmKn-2", "col_header": "Hydrophobicity (%)", "value": "56.23"}, {"table_index": 1, "row_index": 2, "col_index": 7, "row_label": "BmKn-2", "col_header": "Helix", "value": "76.92"}, {"table_index": 1, "row_index": 2, "col_index": 8, "row_label": "BmKn-2", "col_header": "Structure prediction", "value": "CHHHHHHHHHHCC"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "BmKn-21", "col_header": "Amino acid sequence", "value": "FIGAIARLLSKI"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "BmKn-21", "col_header": "Molecular weight (Da)", "value": "1301.64"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "BmKn-21", "col_header": "Length", "value": "12"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "BmKn-21", "col_header": "Net charge", "value": "+2"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "BmKn-21", "col_header": "Hydrophobicity (%)", "value": "66.67"}, {"table_index": 1, "row_index": 3, "col_index": 7, "row_label": "BmKn-21", "col_header": "Helix", "value": "75"}, {"table_index": 1, "row_index": 3, "col_index": 8, "row_label": "BmKn-21", "col_header": "Structure prediction", "value": "CHHHHHHHHHCC"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "BmKn-22", "col_header": "Amino acid sequence", "value": "FIGAIARLLSK"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "BmKn-22", "col_header": "Molecular weight (Da)", "value": "1188.48"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "BmKn-22", "col_header": "Length", "value": "11"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "BmKn-22", "col_header": "Net charge", "value": "+2"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "BmKn-22", "col_header": "Hydrophobicity (%)", "value": "48.64"}, {"table_index": 1, "row_index": 4, "col_index": 7, "row_label": "BmKn-22", "col_header": "Helix", "value": "63.64"}, {"table_index": 1, "row_index": 4, "col_index": 8, "row_label": "BmKn-22", "col_header": "Structure prediction", "value": "CCHHHHHHHCC"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "BmKn-23", "col_header": "Amino acid sequence", "value": "FIGAIARLLS"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "BmKn-23", "col_header": "Molecular weight (Da)", "value": "1060.3"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "BmKn-23", "col_header": "Length", "value": "10"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "BmKn-23", "col_header": "Net charge", "value": "+1"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "BmKn-23", "col_header": "Hydrophobicity (%)", "value": "55.8"}, {"table_index": 1, "row_index": 5, "col_index": 7, "row_label": "BmKn-23", "col_header": "Helix", "value": "70"}, {"table_index": 1, "row_index": 5, "col_index": 8, "row_label": "BmKn-23", "col_header": "Structure prediction", "value": "CHHHHHHHCC"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "BmKn-24", "col_header": "Amino acid sequence", "value": "FIGAIARLL"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "BmKn-24", "col_header": "Molecular weight (Da)", "value": "973.23"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "BmKn-24", "col_header": "Length", "value": "9"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "BmKn-24", "col_header": "Net charge", "value": "+1"}, {"table_index": 1, "row_index": 6, "col_index": 6, "row_label": "BmKn-24", "col_header": "Hydrophobicity (%)", "value": "62.56"}, {"table_index": 1, "row_index": 6, "col_index": 7, "row_label": "BmKn-24", "col_header": "Helix", "value": "66.67"}, {"table_index": 1, "row_index": 6, "col_index": 8, "row_label": "BmKn-24", "col_header": "Structure prediction", "value": "CHHHHHHCC"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "BmKn-25", "col_header": "Amino acid sequence", "value": "FIGAIARL"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "BmKn-25", "col_header": "Molecular weight (Da)", "value": "860.07"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "BmKn-25", "col_header": "Length", "value": "8"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "BmKn-25", "col_header": "Net charge", "value": "+1"}, {"table_index": 1, "row_index": 7, "col_index": 6, "row_label": "BmKn-25", "col_header": "Hydrophobicity (%)", "value": "57.88"}, {"table_index": 1, "row_index": 7, "col_index": 7, "row_label": "BmKn-25", "col_header": "Helix", "value": "0"}, {"table_index": 1, "row_index": 7, "col_index": 8, "row_label": "BmKn-25", "col_header": "Structure prediction", "value": "CCCCCCCC"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "BmKn-26", "col_header": "Amino acid sequence", "value": "FIGAIAR"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "BmKn-26", "col_header": "Molecular weight (Da)", "value": "746.91"}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "BmKn-26", "col_header": "Length", "value": "7"}, {"table_index": 1, "row_index": 8, "col_index": 5, "row_label": "BmKn-26", "col_header": "Net charge", "value": "+1"}, {"table_index": 1, "row_index": 8, "col_index": 6, "row_label": "BmKn-26", "col_header": "Hydrophobicity (%)", "value": "51.86"}, {"table_index": 1, "row_index": 8, "col_index": 7, "row_label": "BmKn-26", "col_header": "Helix", "value": "0"}, {"table_index": 1, "row_index": 8, "col_index": 8, "row_label": "BmKn-26", "col_header": "Structure prediction", "value": "CCCCCCC"}]}, {"table_index": 2, "label": "Table 2", "caption": "List of primers used in this study.", "footnotes": [], "header_rows": [["Target gene", "Primer sequence 5’ to 3’", "Reference"], ["lasI", "F: CTACAGCCTGCAGAACGACA", "[27]"], ["R: ATCTGGGTCTTGGCATTGAG"], ["lasR", "F: ACGCTCAAGTGGAAAATTGG", "[27]"], ["R: GTAGATGGACGGTTCCCAGA"], ["rhlI", "F: CTC TCTGAATCGCTGGAAGG", "[27]"], ["R: GACGTCCTTGAGCAGGTAGG"], ["rhlR", "F: AGGAATGACGGAGGCTTTTT", "[27]"], ["R: CCCGTAGTTCTGCATCTGGT"], ["16S rRNA", "F: CGTCCGGAAACGGCCGCT", "[28]"], ["R: CTCTCAGACCAGTTACGG"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "A scorpion venom peptide derivative BmKn-22 with potent antibiofilm activity against Pseudomonas aeruginosa.", "db_measure": "Antibiofilm", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "BmKn-23"}, {"assertion_index": 1, "database": "APD6", "db_subject_text": "A scorpion venom peptide derivative BmKn-22 with potent antibiofilm activity against Pseudomonas aeruginosa.", "db_measure": "Antibiofilm", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "BmKn-25"}, {"assertion_index": 2, "database": "APD6", "db_subject_text": "A scorpion venom peptide derivative BmKn-22 with potent antibiofilm activity against Pseudomonas aeruginosa.", "db_measure": "Antibiofilm", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "BmKn-26"}]

Return ONLY the JSON array now (one object per assertion above).