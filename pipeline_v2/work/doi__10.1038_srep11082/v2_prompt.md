
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
doi__10.1038_srep11082

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Antimicrobial activities of Cl-CATH2.", "footnotes": ["MIC, minimal inhibitory concentration,these concentrations represent the mean values of three independent experiments performed in duplicate. CI: clinically isolated strain. DR: drug resistance for ampicillin and benzylpencillin."], "header_rows": [["Microorganisms", "MICª(ug/ml)"], ["Gram-Negative Bacteria", "Gram-Negative Bacteria"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Escherichia coli ATCC25922", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "18.75"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "E. coli 08040726 (CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "37.50"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Klebsiella Trevisan 1400 (CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "18.75"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Pseudomonsa aeruginosa ATCC27853", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "18.75"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Stenotrophomonas maltophilia 7407(CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "75"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Gram-Positive Bacteria", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "Gram-Positive Bacteria"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Staphylococcus aureus ATCC27853", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "9.38"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "S. aureus 08032706 (CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "18.75"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "S. aureus 08032712 (CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "18.75"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "S. aureus 08032810 (CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "9.38"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "S. aureus gz130623 (CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "18.75"}, {"table_index": 1, "row_index": 14, "col_index": 2, "row_label": "Bacillus cereus 1373(CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "9.38"}, {"table_index": 1, "row_index": 15, "col_index": 2, "row_label": "Bacillus subtilis 1345 (CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "75"}, {"table_index": 1, "row_index": 16, "col_index": 2, "row_label": "Enterococcus faecalis 1396 (CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "75"}, {"table_index": 1, "row_index": 17, "col_index": 2, "row_label": "Fungi", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "Fungi"}, {"table_index": 1, "row_index": 18, "col_index": 2, "row_label": "Candida albicans ATCC2002", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "37.50"}, {"table_index": 1, "row_index": 19, "col_index": 2, "row_label": "C. albicans 08022821(CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "75"}, {"table_index": 1, "row_index": 20, "col_index": 2, "row_label": "C. albicans 08030809(CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "75"}, {"table_index": 1, "row_index": 21, "col_index": 2, "row_label": "C. albicans 08030102(CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "150"}, {"table_index": 1, "row_index": 22, "col_index": 2, "row_label": "Candida glabrata 08A802(CI, DR)", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "18.75"}, {"table_index": 1, "row_index": 23, "col_index": 2, "row_label": "C. glabrata 091223", "col_header": "MICª(ug/ml) / Gram-Negative Bacteria", "value": "150"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Klebsiella pneumoniae 1400", "db_measure": "MIC", "db_value": "18.75", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Cathelicidin 2 Cl, Cl-CATH2"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Pseudomonas aeruginosa ATCC 27853", "db_measure": "MIC", "db_value": "18.75", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Cathelicidin 2 Cl, Cl-CATH2"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 25923", "db_measure": "MIC", "db_value": "9.38", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Cathelicidin 2 Cl, Cl-CATH2"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Klebsiella pneumoniae 1400", "db_measure": "MIC", "db_value": "18.75", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Novel Cathelicidins from Pigeon Highlights Evolutionary Convergence in Avain Cathelicidins and Functions in Modulation of Innate Immunity."}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Pseudomonas aeruginosa ATCC 27853", "db_measure": "MIC", "db_value": "18.75", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Novel Cathelicidins from Pigeon Highlights Evolutionary Convergence in Avain Cathelicidins and Functions in Modulation of Innate Immunity."}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 25923", "db_measure": "MIC", "db_value": "9.38", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Novel Cathelicidins from Pigeon Highlights Evolutionary Convergence in Avain Cathelicidins and Functions in Modulation of Innate Immunity."}, {"assertion_index": 6, "database": "CAMP", "db_subject_text": "Escherichia coli ATCC 25922[MIC = 18.75 microg/ml], Escherichia coli 08040726[MIC = 37.5 microg/ml], Klebsiella pneumoniae 1400[MIC = 18.75 microg/ml], Pseudomonas aeruginosa ATCC 27853[MIC = 18.75 microg/ml], Stenotrophomonas maltophilia 7407[MIC = 75 microg/ml], Staphylococcus aureus ATCC 25923[MIC = 9.38 microg/ml], Staphylococcus aureus 08032706[MIC = 18.75 microg/ml], Staphylococcus aureus 08032810[MIC = 9.38 microg/ml], Bacillus cereus 1373[MIC = 9.38 microg/ml], Bacillus subtilis 1345[MIC = 75 microg/ml], Enterococcus faecalis 1396[MIC = 75 microg/ml], Candida albicans ATCC 2002[MIC = 37.5 microg/ml], Candida albicans 08022821[MIC = 75 microg/ml], Candida albicans 08030102[MIC = 150 microg/ml], Candida glabrata 08A802[MIC = 18.75 microg/ml], Candida glabrata 091223[MIC = 150 microg/ml]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Cathelicidin 2 Cl, Cl-CATH2"}]

Return ONLY the JSON array now (one object per assertion above).