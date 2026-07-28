
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
doi__10.1186_1477-7827-4-7

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Gene specific primer sequences for rat β-defensins", "footnotes": [], "header_rows": [["Gene", "Primer sequence"], ["Defb21", "Forward – 5' ATA CCT GGA TCT ACT GTC CTA CCT 3' Reverse – 5' TTA TGT GTC CAT CCG TGA AGT C 3'"], ["Defb24", "Forward – 5' GTC ATC ACC TTC ACC CCG GGA 3' Reverse – 5' CAG CTT CTC TGG AAG TCT GTG CAT 3'"], ["Defb27", "Forward – 5' CAC GAG GAA CAC CCT GGA TTT CC 3' Reverse – 5' TGC CTA GGT CC ACCT TCG TTT CTG 3'"], ["Defb30", "Forward – 5' GAG TGA CTT TCC TTT CCT CAG 3' Reverse – 5' TCA GAA TTC CCA GAG GAA CCC TGG A 3'"], ["Defb36", "Forward – 5' TTG GGC CTT CTC CCA CCA TGA AGC 3' Reverse – 5' TGC ATC GTC TGG GCT TCC GGC TT 3'"]], "longform_cells": []}, {"table_index": 2, "label": "Table 2", "caption": "General characteristic features of rat β-defensin protein isoforms.", "footnotes": ["a amino acids in mature protein not including the signal peptide", "b number of cysteines in the C termini"], "header_rows": [["", "DEFB21", "DEFB24", "DEFB27", "DEFB30", "DEFB36"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Lengtha(aa)", "col_header": "DEFB21", "value": "64"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Lengtha(aa)", "col_header": "DEFB24", "value": "64"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "Lengtha(aa)", "col_header": "DEFB27", "value": "47"}, {"table_index": 2, "row_index": 2, "col_index": 5, "row_label": "Lengtha(aa)", "col_header": "DEFB30", "value": "53"}, {"table_index": 2, "row_index": 2, "col_index": 6, "row_label": "Lengtha(aa)", "col_header": "DEFB36", "value": "45"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "MW (kD)a", "col_header": "DEFB21", "value": "7.48"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "MW (kD)a", "col_header": "DEFB24", "value": "7.50"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "MW (kD)a", "col_header": "DEFB27", "value": "5.59"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "MW (kD)a", "col_header": "DEFB30", "value": "6.32"}, {"table_index": 2, "row_index": 3, "col_index": 6, "row_label": "MW (kD)a", "col_header": "DEFB36", "value": "5.47"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "pIa", "col_header": "DEFB21", "value": "8.58"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "pIa", "col_header": "DEFB24", "value": "9.06"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "pIa", "col_header": "DEFB27", "value": "8.26"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "pIa", "col_header": "DEFB30", "value": "9.06"}, {"table_index": 2, "row_index": 4, "col_index": 6, "row_label": "pIa", "col_header": "DEFB36", "value": "9.74"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Cysteinesb", "col_header": "DEFB21", "value": "6"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Cysteinesb", "col_header": "DEFB24", "value": "6"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "Cysteinesb", "col_header": "DEFB27", "value": "6"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "Cysteinesb", "col_header": "DEFB30", "value": "6"}, {"table_index": 2, "row_index": 5, "col_index": 6, "row_label": "Cysteinesb", "col_header": "DEFB36", "value": "6"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Net Chargea", "col_header": "DEFB21", "value": "+3"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "Net Chargea", "col_header": "DEFB24", "value": "+5"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "Net Chargea", "col_header": "DEFB27", "value": "+2"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "Net Chargea", "col_header": "DEFB30", "value": "+5"}, {"table_index": 2, "row_index": 6, "col_index": 6, "row_label": "Net Chargea", "col_header": "DEFB36", "value": "+10"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "dbAMP", "db_subject_text": "Rattus norvegicus (Rat)\nRattus norvegicus\nQ32ZG5_RAT\nBeta-defensin 27 (DEFB27; Protein Defb27; rodents, mammals, animals)", "db_measure": "Antimicrobial", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "dbAMP", "db_subject_text": "Rattus norvegicus (Rat)\nRattus norvegicus\nQ32ZH1_RAT\nBeta-defensin 21 (DEFB21; Protein Defb21; rodents, mammals, animals)", "db_measure": "Antimicrobial", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).