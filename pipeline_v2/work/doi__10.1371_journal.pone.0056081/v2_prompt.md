
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
doi__10.1371_journal.pone.0056081

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Characteristics of various peptides identified by phage-display.", "footnotes": ["MW – Molecular weight (theoretical)."], "header_rows": [["Clone", "Sequence", "Frequency", "Net charge", "Hydrophobicity", "MW*"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "EC2", "col_header": "Sequence", "value": "SGHQLLLNKMPN"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "EC2", "col_header": "Frequency", "value": "1/10"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "EC2", "col_header": "Net charge", "value": "+2"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "EC2", "col_header": "Hydrophobicity", "value": "33%"}, {"table_index": 1, "row_index": 2, "col_index": 6, "row_label": "EC2", "col_header": "MW*", "value": "1345.59"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "EC5", "col_header": "Sequence", "value": "RLLFRKIRRLKR"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "EC5", "col_header": "Frequency", "value": "5/10"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "EC5", "col_header": "Net charge", "value": "+7"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "EC5", "col_header": "Hydrophobicity", "value": "41%"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "EC5", "col_header": "MW*", "value": "1994.58"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "EC6", "col_header": "Sequence", "value": "MDMRTTDIRDTS"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "EC6", "col_header": "Frequency", "value": "1/10"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "EC6", "col_header": "Net charge", "value": "−1"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "EC6", "col_header": "Hydrophobicity", "value": "25%"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "EC6", "col_header": "MW*", "value": "1441.61"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "EC8", "col_header": "Sequence", "value": "RNHPATLTGTGG"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "EC8", "col_header": "Frequency", "value": "1/10"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "EC8", "col_header": "Net charge", "value": "+2"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "EC8", "col_header": "Hydrophobicity", "value": "16%"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "EC8", "col_header": "MW*", "value": "1175.28"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "EC9", "col_header": "Sequence", "value": "GILSELGKALGG"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "EC9", "col_header": "Frequency", "value": "1/10"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "EC9", "col_header": "Net charge", "value": "0"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "EC9", "col_header": "Hydrophobicity", "value": "41%"}, {"table_index": 1, "row_index": 6, "col_index": 6, "row_label": "EC9", "col_header": "MW*", "value": "1174.36"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "EC10", "col_header": "Sequence", "value": "GAPALSTPPLSR"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "EC10", "col_header": "Frequency", "value": "1/10"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "EC10", "col_header": "Net charge", "value": "+1"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "EC10", "col_header": "Hydrophobicity", "value": "33%"}, {"table_index": 1, "row_index": 7, "col_index": 6, "row_label": "EC10", "col_header": "MW*", "value": "1148.35"}]}, {"table_index": 2, "label": "Table 2", "caption": "MIC of EC5 against bacteria (µg/ml).", "footnotes": [], "header_rows": [["Organism", "MIC"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "S. aureus ATCC 25923", "col_header": "MIC", "value": ">128–256"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "S. aureus ATCC 35548", "col_header": "MIC", "value": ">128–256"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "S. epidermidis ATCC 35983", "col_header": "MIC", "value": "64"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "B. cereus ATCC 11778", "col_header": "MIC", "value": "64"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "E. coli ATCC 700928", "col_header": "MIC", "value": "8"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "E. coli ATCC 25922", "col_header": "MIC", "value": "8"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "P. aeruginosa ATCC 27853", "col_header": "MIC", "value": "8"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "P. aeruginosa ATCC 12121", "col_header": "MIC", "value": "8–16"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "K. pneumoniae ATCC 10031", "col_header": "MIC", "value": "32–64"}, {"table_index": 2, "row_index": 11, "col_index": 2, "row_label": "K. pneumoniae ATCC 13885", "col_header": "MIC", "value": "32–64"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "CAMP", "db_subject_text": "Staphylococcus aureus ATCC 25923[MIC >128-256 microg/ml], Staphylococcus aureus ATCC 35548[MIC >128-256 microg/ml], Staphylococcus epidermidis ATCC 35983[MIC = 64 microg/ml], Bacillus cereus ATCC 11778[MIC = 64 microg/ml], Escherichia coli ATCC 700928[MIC = 8 microg/ml], Escherichia coli ATCC 25922[MIC = 8 microg/ml], Pseudomonas aeruginosa ATCC 27853[MIC = 8 microg/ml], Pseudomonas aeruginosa ATCC 12121[MIC = Aug-16 microg/ml], Klebsiella pneumoniae ATCC 10031[MIC = 32-64 microg/ml], Klebsiella pneumoniae ATCC 13885[MIC = 32-64 microg/ml], Escherichia coli LMG 15862[MIC = 64 microM], Klebsiella pneumoniae LMG 20218[MIC >256 microM], Pseudomonas aeruginosa LMG 6395[MIC >128 microM], Acinetobacter baumannii LMG 01041[MIC >128 microM], Klebsiella aerogenes LMG 02094[MIC >256 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "dbAMP", "db_subject_text": "Staphylococcus aureus ATCC 25923 (MIC=>128-256μg/ml)\nStaphylococcus aureus ATCC 35548 (MIC=>128-256μg/ml)\nStaphylococcus epidermidis ATCC 35983 (MIC=64μg/ml)\nBacillus cereus ATCC 11778 (MIC=64μg/ml)\nEscherichia coli ATCC 700928 (MIC=8μg/ml)\nEscherichia coli ATCC 25922 (MIC=8μg/ml)\nPseudomonas aeruginosa ATCC 27853 (MIC=8μg/ml)\nPseudomonas aeruginosa ATCC 12121 (MIC=8-16μg/ml)\nKlebsiella pneumoniae ATCC 10031 (MIC=32-64μg/ml)\nKlebsiella pneumoniae ATCC 13885 (MIC=32-64μg/ml)\nEscherichia coli LMG 15862 (MIC=64μM)\nKlebsiella pneumoniae LMG 20218 (MIC=>256μM)\nPseudomonas aeruginosa LMG 6395 (MIC=>128μM)\nAcinetobacter baumannii LMG 01041 (MIC=>128μM)\nKlebsiella aerogenes LMG 02094 (MIC=>256μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).