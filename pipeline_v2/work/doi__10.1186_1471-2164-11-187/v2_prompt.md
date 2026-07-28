
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
doi__10.1186_1471-2164-11-187

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Antibacterial activity of pronavicin.", "footnotes": ["* indicates the semi-inhibition of pronavicin against Stenotrophomonus. sp. LZ-1."], "header_rows": [["Microorganism", "Lethal conc. (CL) (μM)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "B. megaterium", "col_header": "Lethal conc. (CL) (μM)", "value": "3.11 (y = 1.0867x + 1.019, R2 = 0.998)"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "M. luteus", "col_header": "Lethal conc. (CL) (μM)", "value": "42.4 (y = 0.65x + 0.0175, R2 = 0.9956)"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Bacillus sp.", "col_header": "Lethal conc. (CL) (μM)", "value": "19.5 (y = 0.7125x - 0.2313, R2 = 0.995)"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "S. typhimurium", "col_header": "Lethal conc. (CL) (μM)", "value": "15.8 (y = 0.3458x + 0.2525, R2 = 0.9993)"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "E. coli", "col_header": "Lethal conc. (CL) (μM)", "value": "61.8 (y = 0.2375x + 0.0712, R2 = 0.9774)"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Stenotrophomonus sp. YC-1", "col_header": "Lethal conc. (CL) (μM)", "value": "78.0 (y = 0.3x + 0.0292, R2 = 0.9959)"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Stenotrophomonus sp. LZ-1", "col_header": "Lethal conc. (CL) (μM)", "value": "12.0 (y = 0.3625x + 0.3, R2 = 0.9542)*"}]}, {"table_index": 2, "label": "Table 2", "caption": "Maximum likelihood estimates of parameters and sites inferred to be under positive selection in the amino-terminal abaecin unit.", "footnotes": ["Note: l is the log likelihood; LRT is a likelihood ratio test, which is twice the log likelihood difference (2Δl) between null models (M1a and M7) and their alternative models (M2a and M8): M1a/M2a = 2.7 (χ2 significant value: P < 0.3); M7/M8 = 5.16 (0.05 < P < 0.1). Positively selected sites identified by the BEB method under M2a and M8 with posterior probabilities (p) > 0.6 are shown, in which those with p > 0.95 are indicated by bold and *."], "header_rows": [["Model", "l", "LRT", "Parameters", "Positive selected sites"], ["M0", "-312.78", "", "ω = 0.15", ""], ["M1a", "-306.30", "", "p0 = 0.80, ω0 = 0.046p1 = 0.20, ω1 = 1.00", ""]], "longform_cells": [{"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "M2a", "col_header": "l / -312.78 / -306.30", "value": "-304.95"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "M2a", "col_header": "LRT", "value": "2.7"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "M2a", "col_header": "Parameters / ω = 0.15 / p0 = 0.80, ω0 = 0.046p1 = 0.20, ω1 = 1.00", "value": "p0 = 0.80, ω0 = 0.05p1 = 0.00, ω1 = 0.05315p2 = 0.20, ω2 = 5.91067"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "M2a", "col_header": "Positive selected sites", "value": "4Y, 6P*, 8R, 11Q, 12K"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "M7", "col_header": "l / -312.78 / -306.30", "value": "-306.58"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "M7", "col_header": "Parameters / ω = 0.15 / p0 = 0.80, ω0 = 0.046p1 = 0.20, ω1 = 1.00", "value": "p = 0.48 q = 1.62"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "M8", "col_header": "l / -312.78 / -306.30", "value": "-304.00"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "M8", "col_header": "LRT", "value": "5.16"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "M8", "col_header": "Parameters / ω = 0.15 / p0 = 0.80, ω0 = 0.046p1 = 0.20, ω1 = 1.00", "value": "p0 = 0.80, p = 1.06, q = 14.00(p1 = 0.20), ω = 6.69"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "M8", "col_header": "Positive selected sites", "value": "4Y, 6P*, 8R, 11Q, 12K"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Bacillus megaterium", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Micrococcus luteus", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Bacillus subtilis", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Salmonella typhimurium", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 25922", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Stenotrophomonas sp. YC-1", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Stenotrophomonas sp. LZ-1", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 25922", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Stenotrophomonas sp. LZ-1", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Bacillus megaterium", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "DBAASP", "db_subject_text": "Micrococcus luteus", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DBAASP", "db_subject_text": "Bacillus subtilis", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 12, "database": "DBAASP", "db_subject_text": "Salmonella typhimurium", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 13, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 25922", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 14, "database": "DBAASP", "db_subject_text": "Stenotrophomonas sp. YC-1", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 15, "database": "DBAASP", "db_subject_text": "Stenotrophomonas sp. LZ-1", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 16, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 25922", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 17, "database": "DBAASP", "db_subject_text": "Stenotrophomonas sp. LZ-1", "db_measure": "LC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 18, "database": "CAMP", "db_subject_text": "Bacillus megaterium[LC = 3.11 microM], Micrococcus luteus[LC = 42.4 microM], Bacillus subtilis[LC = 19.5 microM], Salmonella typhimurium[LC = 15.8 microM], Escherichia coli ATCC 25922[LC = 61.8 microM], Stenotrophomonas sp. YC-1[LC = 78 microM], Stenotrophomonas sp. LZ-1[LC = 12 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 19, "database": "CAMP", "db_subject_text": "Escherichia coli ATCC 25922[LC = 15.4 microM], Stenotrophomonas sp. LZ-1[LC = 1.52 microM], Bacillus megaterium, Micrococcus luteus, Bacillus subtilis", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).