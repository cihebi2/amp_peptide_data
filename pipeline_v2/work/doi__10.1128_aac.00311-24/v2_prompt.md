
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
doi__10.1128_aac.00311-24

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "TABLE 1", "caption": "Sequences and physicochemical properties of peptidesa", "footnotes": ["MW, molecular weight; PI, isoelectric point; GRAVY, grand average of hydropathicity; –, derived peptide, no Gene ID."], "header_rows": [["Name", "Gene ID", "Sequence", "Net charge", "MW (Da)", "PI", "GRAVY"], ["An-cecA", "XP_040173531", "GRLKKLGKKIEGAGKRVFKAAEKALPVVAGVKAL-NH2", "+8", "3,783.61", "10.79", "−0.021"], ["An-cecB", "XP_040173530", "APRWKFGKRLEKLGRNVFRAAKKALPVIAGYKAL-NH2", "+9", "4,105.94", "11.61", "−0.309"], ["An-cecC", "XP_040172706", "RRFKKFLKKVEGAGRRVANAAQKGLPLAAGVKGL-NH2", "+9", "3,887.64", "12.02", "−0.332"]], "longform_cells": [{"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "An-cecB-1", "col_header": "Gene ID / XP_040173531 / XP_040173530 / XP_040172706", "value": "–"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "An-cecB-1", "col_header": "Sequence / GRLKKLGKKIEGAGKRVFKAAEKALPVVAGVKAL-NH2 / APRWKFGKRLEKLGRNVFRAAKKALPVIAGYKAL-NH2 / RRFKKFLKKVEGAGRRVANAAQKGLPLAAGVKGL-NH2", "value": "APRWKFGKRLEKLGRNVF-NH2"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "An-cecB-1", "col_header": "Net charge / +8 / +9", "value": "+5"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "An-cecB-1", "col_header": "MW (Da) / 3,783.61 / 4,105.94 / 3,887.64", "value": "2,453.88"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "An-cecB-1", "col_header": "PI / 10.79 / 11.61 / 12.02", "value": "11.73"}, {"table_index": 1, "row_index": 5, "col_index": 7, "row_label": "An-cecB-1", "col_header": "GRAVY / −0.021 / −0.309 / −0.332", "value": "−0.906"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "An-cecB-2", "col_header": "Gene ID / XP_040173531 / XP_040173530 / XP_040172706", "value": "–"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "An-cecB-2", "col_header": "Sequence / GRLKKLGKKIEGAGKRVFKAAEKALPVVAGVKAL-NH2 / APRWKFGKRLEKLGRNVFRAAKKALPVIAGYKAL-NH2 / RRFKKFLKKVEGAGRRVANAAQKGLPLAAGVKGL-NH2", "value": "RAAKKALPVIAGYKAL-NH2"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "An-cecB-2", "col_header": "Net charge / +8 / +9", "value": "+4"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "An-cecB-2", "col_header": "MW (Da) / 3,783.61 / 4,105.94 / 3,887.64", "value": "1,921.32"}, {"table_index": 1, "row_index": 6, "col_index": 6, "row_label": "An-cecB-2", "col_header": "PI / 10.79 / 11.61 / 12.02", "value": "10.46"}, {"table_index": 1, "row_index": 6, "col_index": 7, "row_label": "An-cecB-2", "col_header": "GRAVY / −0.021 / −0.309 / −0.332", "value": "0.362"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "An-cecB-3", "col_header": "Gene ID / XP_040173531 / XP_040173530 / XP_040172706", "value": "–"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "An-cecB-3", "col_header": "Sequence / GRLKKLGKKIEGAGKRVFKAAEKALPVVAGVKAL-NH2 / APRWKFGKRLEKLGRNVFRAAKKALPVIAGYKAL-NH2 / RRFKKFLKKVEGAGRRVANAAQKGLPLAAGVKGL-NH2", "value": "GKRLEKLGRNVFRAAKK-NH2"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "An-cecB-3", "col_header": "Net charge / +8 / +9", "value": "+6"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "An-cecB-3", "col_header": "MW (Da) / 3,783.61 / 4,105.94 / 3,887.64", "value": "2,222.63"}, {"table_index": 1, "row_index": 7, "col_index": 6, "row_label": "An-cecB-3", "col_header": "PI / 10.79 / 11.61 / 12.02", "value": "11.74"}, {"table_index": 1, "row_index": 7, "col_index": 7, "row_label": "An-cecB-3", "col_header": "GRAVY / −0.021 / −0.309 / −0.332", "value": "−1.100"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 6538", "db_measure": "MIC | >200 | µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 6538", "db_measure": "MIC | MIC | >200 | µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "APD6", "db_subject_text": "Antimalarial activity of cecropin antimicrobial peptides derived from Anopheles mosquitoes.", "db_measure": "Unknown | Sequence analysis: APD analysis reveals that this sequence is similar (52.94%) to An-cecB K=A: 18%, R=L: 12%. GRAVY: -0.309; Mol Wt: 3854.68; mol formula: C181H300N53O39; mol ex coeff: 7040. Activity: inhibited P. falciparum 3D7 (IC50 68.63 uM). In addiiton, it inhibited bacterial growth S.aureus (MIC >200 uM), B. subtilis (MIC 18.94 uM), and E. coli (MIC 12.7 uM). Animal model:mouse: showed a dose-dependent inhibition by 17.03%, 39.35%, and 54.19% when IP treated at 10, 20, and 50 mg/", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).