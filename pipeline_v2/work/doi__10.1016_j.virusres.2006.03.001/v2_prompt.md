
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
doi__10.1016_j.virusres.2006.03.001

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Amino acid sequences of peptides corresponding to sequences of the S2 subunits of SARS-CoV or MHV with significant WWIHS scores", "footnotes": ["The SARS-CoV (SARSWW) and MHV (MHVWW) peptides were synthesized based on the amino acid sequence determined from GenBank accession no. AY278741 (SARS-CoV strain Urbani) or AY700211 (MHV strain A59).", "Amino acid change to tryptophan (W) is shown in underlined text."], "header_rows": [["Peptidea", "Amino acid sequence", "Net charge", "Description", "Position"], ["SARSWW-I", "MWKTPTLKYFGGFNFSQILb", "+2", "N-terminal", "770–788"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "SARSWW-II", "col_header": "Amino acid sequence / MWKTPTLKYFGGFNFSQILb", "value": "ATAGWTFGAGAALQIPFAMQMAY"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "SARSWW-II", "col_header": "Net charge / +2", "value": "0"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "SARSWW-II", "col_header": "Description / N-terminal", "value": "N-terminal"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "SARSWW-II", "col_header": "Position / 770–788", "value": "864–886"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "SARSWW-III", "col_header": "Amino acid sequence / MWKTPTLKYFGGFNFSQILb", "value": "GYHLMSFPQAAPHGVVFLHVTW"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "SARSWW-III", "col_header": "Net charge / +2", "value": "+3"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "SARSWW-III", "col_header": "Description / N-terminal", "value": "Loop"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "SARSWW-III", "col_header": "Position / 770–788", "value": "1028–1049"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "SARSWW-IV", "col_header": "Amino acid sequence / MWKTPTLKYFGGFNFSQILb", "value": "GVFVFNGTSWFITQRNFFS"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "SARSWW-IV", "col_header": "Net charge / +2", "value": "+1"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "SARSWW-IV", "col_header": "Description / N-terminal", "value": "Loop"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "SARSWW-IV", "col_header": "Position / 770–788", "value": "1075–1093"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "SARSWW-Va", "col_header": "Amino acid sequence / MWKTPTLKYFGGFNFSQILb", "value": "NEVAKNLNESLIDLQELGKYEQYIKWPWYVW"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "SARSWW-Va", "col_header": "Net charge / +2", "value": "−2"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "SARSWW-Va", "col_header": "Description / N-terminal", "value": "HR2- Aromatic"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "SARSWW-Va", "col_header": "Position / 770–788", "value": "1169–1199"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "SARSWW-Vb", "col_header": "Amino acid sequence / MWKTPTLKYFGGFNFSQILb", "value": "AACEVAKNLNESLIDLQELGKYEQYIKW"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "SARSWW-Vb", "col_header": "Net charge / +2", "value": "−2"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "SARSWW-Vb", "col_header": "Description / N-terminal", "value": "HR2- ΔAromatic"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "SARSWW-Vb", "col_header": "Position / 770–788", "value": "1169–1194"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "MHVWW-III", "col_header": "Amino acid sequence / MWKTPTLKYFGGFNFSQILb", "value": "GNHILSLVQNAPYGLYFIHFSW"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "MHVWW-III", "col_header": "Net charge / +2", "value": "+2"}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "MHVWW-III", "col_header": "Description / N-terminal", "value": "Loop"}, {"table_index": 1, "row_index": 8, "col_index": 5, "row_label": "MHVWW-III", "col_header": "Position / 770–788", "value": "1096–1117"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "MHVWW-IV", "col_header": "Amino acid sequence / MWKTPTLKYFGGFNFSQILb", "value": "GYFVQDDGEWKFTGSSYYY"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "MHVWW-IV", "col_header": "Net charge / +2", "value": "−3"}, {"table_index": 1, "row_index": 9, "col_index": 4, "row_label": "MHVWW-IV", "col_header": "Description / N-terminal", "value": "Loop"}, {"table_index": 1, "row_index": 9, "col_index": 5, "row_label": "MHVWW-IV", "col_header": "Position / 770–788", "value": "1144–1162"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "[Ref.16616792]SARS-CoV:inhibition of plaque information on Vero E6 cells(IC50=4 μM).", "db_measure": "Comment: No comments found on DRAMP database", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "Murine Hepatitis Virus (MHV/M-CoV)[90-100% Inhibition = 30 microM], Murine Hepatitis Virus (MHV/M-CoV)[IC50 I = 4 microM]", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "CAMP", "db_subject_text": "SARS-CoV[50-60% Inhibition = 30 microM]", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "CAMP", "db_subject_text": "Murine Hepatitis Virus (MHV/M-CoV)[20-30% Inhibition = 30 microM]", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "dbAMP", "db_subject_text": "SARS-CoV (83% Inhibition=30μM)\nSARS-CoV (IC50 I=2μM)", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "dbAMP", "db_subject_text": "Murine Hepatitis Virus (MHV/M-CoV) (98% Inhibition=30μM)\nMurine Hepatitis Virus (MHV/M-CoV) (IC50 I=4μM)", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "dbAMP", "db_subject_text": "SARS-CoV (90% Inhibition=30μM)\nSARS-CoV (IC50 I=2μM)", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "dbAMP", "db_subject_text": "SARS coronavirus", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "dbAMP", "db_subject_text": "SARS-CoV (39% Inhibition=30μM)", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "dbAMP", "db_subject_text": "Murine Hepatitis Virus (MHV/M-CoV) (22% Inhibition=30μM)", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "dbAMP", "db_subject_text": "SARS-CoV (42% Inhibition=30μM)", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "dbAMP", "db_subject_text": "SARS-CoV\nSARS coronavirus", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).