
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
doi__10.1038_s41598-020-70314-5

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Antibacterial spectrum of the Ae. tauschii antimicrobial genes.", "footnotes": ["−, Representative effect is not significant; +, Representative effect is significant; +p < 0.05, ++p < 0.01, +++p < 0.001. The results are the mean values from three independent experiments. Significance analysis was performed by SPSS22.0 (SPSS Inc., Chicago, IL, USA)."], "header_rows": [["Gene ID", "Gram-positive bacteria", "Gram-positive bacteria", "Gram-positive bacteria", "Gram-positive bacteria", "Gram-positive bacteria", "Gram-positive bacteria", "Gram-positive bacteria", "Gram-negative bacteria", "Gram-negative bacteria", "Gram-negative bacteria", "Gram-negative bacteria"], ["B. subtilis IA274", "Clavibater michiganensis", "B. cereus 905", "Clavibacter fangii", "B. subtilis 330-2", "B. subtilis RIK1285", "B. subtilis 168", "Xanthomonas oryzae pv. oryzae", "X. oryzae pv. oryzicola", "Rastonia solanacearum", "X. campestris pv. holcicola"], ["AtR100", "−", "+++", "−", "+++", "+", "−", "+++", "−", "+++", "+", "−"], ["AtR472", "−", "−", "−", "+++", "+", "−", "+++", "+", "+++", "+", "−"]], "longform_cells": []}, {"table_index": 2, "label": "Table 2", "caption": "Bioinformatics prediction of antimicrobial peptides.", "footnotes": ["AA No., number of amino acids; GRAVY, grand average of hydropathicity; pI, theoretical pI; MV, molecular weight; S–S No., number of cysteine disulfides."], "header_rows": [["Protein name", "AA no", "S–S no", "Secondary structure", "MV", "pI", "GRAVY"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "AtR31", "col_header": "AA no", "value": "15"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "AtR31", "col_header": "S–S no", "value": "0"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "AtR31", "col_header": "Secondary structure", "value": "β-strand"}, {"table_index": 2, "row_index": 2, "col_index": 5, "row_label": "AtR31", "col_header": "MV", "value": "1861.19"}, {"table_index": 2, "row_index": 2, "col_index": 6, "row_label": "AtR31", "col_header": "pI", "value": "8.60"}, {"table_index": 2, "row_index": 2, "col_index": 7, "row_label": "AtR31", "col_header": "GRAVY", "value": "0.127"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "AtR78", "col_header": "AA no", "value": "20"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "AtR78", "col_header": "S–S no", "value": "1"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "AtR78", "col_header": "Secondary structure", "value": "β-strand"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "AtR78", "col_header": "MV", "value": "2,282.63"}, {"table_index": 2, "row_index": 3, "col_index": 6, "row_label": "AtR78", "col_header": "pI", "value": "6.89"}, {"table_index": 2, "row_index": 3, "col_index": 7, "row_label": "AtR78", "col_header": "GRAVY", "value": "0.270"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "AtR222", "col_header": "AA no", "value": "13"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "AtR222", "col_header": "S–S no", "value": "0"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "AtR222", "col_header": "Secondary structure", "value": "β-strand"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "AtR222", "col_header": "MV", "value": "1595.96"}, {"table_index": 2, "row_index": 4, "col_index": 6, "row_label": "AtR222", "col_header": "pI", "value": "6.73"}, {"table_index": 2, "row_index": 4, "col_index": 7, "row_label": "AtR222", "col_header": "GRAVY", "value": "1.577"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "AtR352", "col_header": "AA no", "value": "16"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "AtR352", "col_header": "S–S no", "value": "0"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "AtR352", "col_header": "Secondary structure", "value": "β-strand"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "AtR352", "col_header": "MV", "value": "1917.31"}, {"table_index": 2, "row_index": 5, "col_index": 6, "row_label": "AtR352", "col_header": "pI", "value": "8.75"}, {"table_index": 2, "row_index": 5, "col_index": 7, "row_label": "AtR352", "col_header": "GRAVY", "value": "0.719"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "AtR100", "col_header": "AA no", "value": "21"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "AtR100", "col_header": "S–S no", "value": "1"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "AtR100", "col_header": "Secondary structure", "value": "α-helix β-strand"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "AtR100", "col_header": "MV", "value": "2,432.75"}, {"table_index": 2, "row_index": 6, "col_index": 6, "row_label": "AtR100", "col_header": "pI", "value": "5.97"}, {"table_index": 2, "row_index": 6, "col_index": 7, "row_label": "AtR100", "col_header": "GRAVY", "value": "0.148"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "AtR472", "col_header": "AA no", "value": "45"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "AtR472", "col_header": "S–S no", "value": "2"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "AtR472", "col_header": "Secondary structure", "value": "α-helix β-strand"}, {"table_index": 2, "row_index": 7, "col_index": 5, "row_label": "AtR472", "col_header": "MV", "value": "5,210.08"}, {"table_index": 2, "row_index": 7, "col_index": 6, "row_label": "AtR472", "col_header": "pI", "value": "8.42"}, {"table_index": 2, "row_index": 7, "col_index": 7, "row_label": "AtR472", "col_header": "GRAVY", "value": "0.158"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Two antimicrobial genes from Aegilops tauschii Cosson identified by the Bacillus subtilis expression system", "db_measure": "APD6 linked experiment row 1 maps to AtR100 by molecular weight and activity annotation.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "APD6", "db_subject_text": "Two antimicrobial genes from Aegilops tauschii Cosson identified by the Bacillus subtilis expression system", "db_measure": "APD6 linked experiment row 2 maps to AtR472 by molecular weight and activity annotation.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).