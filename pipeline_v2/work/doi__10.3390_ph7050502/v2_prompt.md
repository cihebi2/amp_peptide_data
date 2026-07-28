
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
doi__10.3390_ph7050502

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "The amino acid sequences and properties of the peptides employed in this study.", "footnotes": [], "header_rows": [["Peptide", "Sequence", "Hydrophobicity (H)", "Hydrophobic moment (MH)", "Helicity"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "AamAP1", "col_header": "Sequence", "value": "FLFSLIPHAIGGLISAFK"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "AamAP1", "col_header": "Hydrophobicity (H)", "value": "0.9"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "AamAP1", "col_header": "Hydrophobic moment (MH)", "value": "0.44"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "AamAP1", "col_header": "Helicity", "value": "66.60%"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "AamAP1-Lysine", "col_header": "Hydrophobicity (H)", "value": "0.61"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "AamAP1-Lysine", "col_header": "Hydrophobic moment (MH)", "value": "0.61"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "AamAP1-Lysine", "col_header": "Helicity", "value": "88.3%"}]}, {"table_index": 2, "label": "Table 2", "caption": "Minimum inhibitory concentrations (MICs) of AamAP1-Lysine against the test microorganisms employed in this study.", "footnotes": [], "header_rows": [["Strain (Gram positive)", "ATCC", "MIC (µM)"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Staphylococcus epidermidis", "col_header": "ATCC", "value": "12228"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Staphylococcus epidermidis", "col_header": "MIC (µM)", "value": "5"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Staphylococcus aureus", "col_header": "ATCC", "value": "29213"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Staphylococcus aureus", "col_header": "MIC (µM)", "value": "5"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Staphylococcus aureus", "col_header": "ATCC", "value": "43300"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Staphylococcus aureus", "col_header": "MIC (µM)", "value": "5"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Staphylococcus aureus", "col_header": "ATCC", "value": "33591"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Staphylococcus aureus", "col_header": "MIC (µM)", "value": "5"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Enterococcus faecalis", "col_header": "ATCC", "value": "19433"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "Enterococcus faecalis", "col_header": "MIC (µM)", "value": "5"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "Strain(Gram negative)", "col_header": "ATCC", "value": "ATCC"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "Eshereschia coli", "col_header": "ATCC", "value": "25922"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "Eshereschia coli", "col_header": "MIC (µM)", "value": "7.5"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "Salmonella enterica", "col_header": "ATCC", "value": "10708"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "Salmonella enterica", "col_header": "MIC (µM)", "value": "7.5"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "Pseudomonas aeruginosa", "col_header": "ATCC", "value": "9027"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "Pseudomonas aeruginosa", "col_header": "MIC (µM)", "value": "5"}, {"table_index": 2, "row_index": 11, "col_index": 2, "row_label": "Klebsiella pneumoniae", "col_header": "ATCC", "value": "13883"}, {"table_index": 2, "row_index": 11, "col_index": 3, "row_label": "Klebsiella pneumoniae", "col_header": "MIC (µM)", "value": "5"}]}, {"table_index": 3, "label": "Table 3", "caption": "Hemolytic effect of AamAP1-Lysine on human erythrocytes after 60 min of incubation.", "footnotes": [], "header_rows": [["Peptide concentration (µM)", "Hemolysis (%)"]], "longform_cells": [{"table_index": 3, "row_index": 2, "col_index": 2, "row_label": "1", "col_header": "Hemolysis (%)", "value": "0"}, {"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "5", "col_header": "Hemolysis (%)", "value": "0"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "10", "col_header": "Hemolysis (%)", "value": "1.38"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "20", "col_header": "Hemolysis (%)", "value": "7.25"}, {"table_index": 3, "row_index": 6, "col_index": 2, "row_label": "40", "col_header": "Hemolysis (%)", "value": "16.58"}, {"table_index": 3, "row_index": 7, "col_index": 2, "row_label": "60", "col_header": "Hemolysis (%)", "value": "21.29"}, {"table_index": 3, "row_index": 8, "col_index": 2, "row_label": "80", "col_header": "Hemolysis (%)", "value": "29.32"}, {"table_index": 3, "row_index": 9, "col_index": 2, "row_label": "100", "col_header": "Hemolysis (%)", "value": "38.25"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Vero cells", "db_measure": "50% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human embryonic kidney HEK293 cells", "db_measure": "50% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Vero cells", "db_measure": "50% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human embryonic kidney HEK293 cells", "db_measure": "50% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "dbAMP", "db_subject_text": "Staphylococcus epidermidis ATCC 12228 (MIC=5μM)\nStaphylococcus aureus ATCC 29213 (MIC=5μM)\nStaphylococcus aureus ATCC 43300 (MIC=5μM)\nStaphylococcus aureus ATCC 33591 (MIC=5μM)\nEnterococcus faecalis ATCC 19433 (MIC=5μM)\nEscherichia coli ATCC 25922 (MIC=7.5μM)\nSalmonella enterica subsp. enterica serovar Choleraesuis ATCC 10708 (MIC=7.5μM)\nPseudomonas aeruginosa ATCC 9027 (MIC=5μM)\nKlebsiella pneumoniae ATCC 13883 (MIC=5μM)\nStaphylococcus aureus ATCC 29213 (MIC=3μM)\nStaphylococcus aureus ATCC 33591 (MIC=3μM)\nPseudomonas aeruginosa ATCC 27853 (MIC=35μM)\nPseudomonas aeruginosa ATCC BAA-2114 (MIC=35μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).