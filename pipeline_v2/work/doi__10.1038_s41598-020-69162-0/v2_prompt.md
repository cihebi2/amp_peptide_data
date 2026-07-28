
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
doi__10.1038_s41598-020-69162-0

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Synthesized peptides used in this study.", "footnotes": [], "header_rows": [["Peptide", "Sequence", "Length (amino acids)", "Net charge", "Molecular weight (g/mol)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "KL6", "col_header": "Sequence", "value": "KLKLKL-NH2"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "KL6", "col_header": "Length (amino acids)", "value": "6"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "KL6", "col_header": "Net charge", "value": "+ 4"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "KL6", "col_header": "Molecular weight (g/mol)", "value": "741.0"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "KL10", "col_header": "Sequence", "value": "KLKLKLKLKL-NH2"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "KL10", "col_header": "Length (amino acids)", "value": "10"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "KL10", "col_header": "Net charge", "value": "+ 6"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "KL10", "col_header": "Molecular weight (g/mol)", "value": "1,223.7"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "KL14", "col_header": "Sequence", "value": "KLKLKLKLKLKLKL-NH2"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "KL14", "col_header": "Length (amino acids)", "value": "14"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "KL14", "col_header": "Net charge", "value": "+ 8"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "KL14", "col_header": "Molecular weight (g/mol)", "value": "1706.3"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "KL18", "col_header": "Sequence", "value": "KLKLKLKLKLKLKLKLKL-NH2"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "KL18", "col_header": "Length (amino acids)", "value": "18"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "KL18", "col_header": "Net charge", "value": "+ 10"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "KL18", "col_header": "Molecular weight (g/mol)", "value": "2,189.0"}]}, {"table_index": 2, "label": "Table 2", "caption": "Time constants (in s) of random coil ↔ β-sheet transition for KL peptides in solution in the presence of phosphate.", "footnotes": ["aFor KL6 no folding was observed after 900 s; τ values could not be fitted properly but are essentially infinite."], "header_rows": [["Peptide", "Phosphate concentration (mM)", "Phosphate concentration (mM)", "Phosphate concentration (mM)", "Phosphate concentration (mM)"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "1.0", "col_header": "Phosphate concentration (mM)", "value": "2.5"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "1.0", "col_header": "Phosphate concentration (mM)", "value": "5.0"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "1.0", "col_header": "Phosphate concentration (mM)", "value": "10.0"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "KL6a", "col_header": "Phosphate concentration (mM)", "value": "∞"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "KL6a", "col_header": "Phosphate concentration (mM)", "value": "∞"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "KL6a", "col_header": "Phosphate concentration (mM)", "value": "∞"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "KL6a", "col_header": "Phosphate concentration (mM)", "value": "∞"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "KL10", "col_header": "Phosphate concentration (mM)", "value": "23,500"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "KL10", "col_header": "Phosphate concentration (mM)", "value": "12,900"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "KL10", "col_header": "Phosphate concentration (mM)", "value": "273"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "KL10", "col_header": "Phosphate concentration (mM)", "value": "96"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "KL14", "col_header": "Phosphate concentration (mM)", "value": "248"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "KL14", "col_header": "Phosphate concentration (mM)", "value": "44"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "KL14", "col_header": "Phosphate concentration (mM)", "value": "15.5"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "KL14", "col_header": "Phosphate concentration (mM)", "value": "7.0"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "KL18", "col_header": "Phosphate concentration (mM)", "value": "158"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "KL18", "col_header": "Phosphate concentration (mM)", "value": "39.5"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "KL18", "col_header": "Phosphate concentration (mM)", "value": "16.5"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "KL18", "col_header": "Phosphate concentration (mM)", "value": "7.0"}]}, {"table_index": 3, "label": "Table 3", "caption": "Partitioning constants, Kp, of KL peptides towards POPC/POPG (1/1) vesicles, calculated from the fluorescence binding curves of NBD-labeled peptides.", "footnotes": ["Average values and standard deviations are given."], "header_rows": [["Peptide", "Kp"]], "longform_cells": [{"table_index": 3, "row_index": 2, "col_index": 2, "row_label": "KL6", "col_header": "Kp", "value": "138,000 ± 12,000"}, {"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "KL10", "col_header": "Kp", "value": "365,000 ± 46,000"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "KL14", "col_header": "Kp", "value": "255,000 ± 23,000"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "KL18", "col_header": "Kp", "value": "503,000 ± 67,000"}]}, {"table_index": 4, "label": "Table 4", "caption": "Summary of aggregation propensity and activities of KL peptides of length 6–18 amino acids, measured at constant peptide mass.", "footnotes": ["In bold print are shown the straightforward correlations between length and activity, once phosphate-induced aggregation artefacts have been eliminated."], "header_rows": [["Aggregation in PB (pH 7) or water (pH 10)", "KL6 << KL10 < KL14 < KL18"], ["Aggregation in presence of lipids", "KL6 << KL10 < KL14 < KL18"], ["Antimicrobial activity (with phosphate)", "KL6 << KL10 >> KL14 ≈ KL18"], ["Antimicrobial activity (reduced phosphate exposure)", "KL6 << KL10 > KL14 > KL18"], ["Hemolysis (no initial phosphate)", "KL6 << KL10 < KL14 < KL18"], ["Vesicle leakage (with PB)", "KL6 << KL10 > KL14 < KL18"], ["Vesicle leakage (no phosphate)", "KL6 << KL10 ≈ KL14 ≈ KL18"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Bacillus subtilis DSM 347", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Bacillus subtilis DSM 347", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Bacillus subtilis DSM 347", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).