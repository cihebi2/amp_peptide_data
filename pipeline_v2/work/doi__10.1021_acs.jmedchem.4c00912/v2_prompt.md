
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
doi__10.1021_acs.jmedchem.4c00912

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "TBP-Stabilizing Activity in MD Simulationsa", "footnotes": ["Peptide termini were either unmodified (i.e., positively charged N-terminus and negatively charged C-terminus) or capped (acetylated N-terminus, Ac–, and amidated C-terminus, −NH2). C indicates peptide net charge. Pore stability in the POPC lipid membrane using the standard and “scaled” CG Martini force fields is separated by a slash (/) symbol. TMP represents the number of transmembrane peptides after 51 μs. The average number of water beads inside the pore and the transmembrane peptide–peptide interaction energy were calculated over the last 3 μs (i.e., 48–51 μs).", "Pore-stabilizing activity of the mutated peptides compared to LP1 in the “scaled” Martini simulations is colored as follows: green for increased, yellow for equivalent, and red for decreased TBP stability."], "header_rows": [], "longform_cells": []}, {"table_index": 2, "label": "Table 2", "caption": "In Vitro Activity and Toxicitya", "footnotes": ["Activities of the mutated peptides compared to LP1 are colored as follows: green for increased, yellow for equivalent, and red for decreased activity.", "Pore stability in POPC lipid membrane compared to LP1 in the “scaled” Martini simulations (see Table 1).", "At physiological pH 7.4, the H residues in LP40 are only partially charged (i.e., carry less than +1 e charge). However, in the presence of negatively charged lipids, the charge of H residues is likely to be higher due to protonation."], "header_rows": [], "longform_cells": []}, {"table_index": 3, "label": "Table 3", "caption": "Mobile Phase Gradient Used to Assess the Resistance of Peptide to Proteolytic Degradation", "footnotes": [], "header_rows": [["time (minutes)", "A (%)", "B (%)", "flow rate (mL min–1)"]], "longform_cells": [{"table_index": 3, "row_index": 2, "col_index": 2, "row_label": "0", "col_header": "A (%)", "value": "95"}, {"table_index": 3, "row_index": 2, "col_index": 3, "row_label": "0", "col_header": "B (%)", "value": "5"}, {"table_index": 3, "row_index": 2, "col_index": 4, "row_label": "0", "col_header": "flow rate (mL min–1)", "value": "0.5"}, {"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "0.5", "col_header": "A (%)", "value": "95"}, {"table_index": 3, "row_index": 3, "col_index": 3, "row_label": "0.5", "col_header": "B (%)", "value": "5"}, {"table_index": 3, "row_index": 3, "col_index": 4, "row_label": "0.5", "col_header": "flow rate (mL min–1)", "value": "0.5"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "2.5", "col_header": "A (%)", "value": "5"}, {"table_index": 3, "row_index": 4, "col_index": 3, "row_label": "2.5", "col_header": "B (%)", "value": "95"}, {"table_index": 3, "row_index": 4, "col_index": 4, "row_label": "2.5", "col_header": "flow rate (mL min–1)", "value": "0.5 (linear gradient)"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "3", "col_header": "A (%)", "value": "5"}, {"table_index": 3, "row_index": 5, "col_index": 3, "row_label": "3", "col_header": "B (%)", "value": "95"}, {"table_index": 3, "row_index": 5, "col_index": 4, "row_label": "3", "col_header": "flow rate (mL min–1)", "value": "0.5"}, {"table_index": 3, "row_index": 6, "col_index": 2, "row_label": "3.25", "col_header": "A (%)", "value": "5"}, {"table_index": 3, "row_index": 6, "col_index": 3, "row_label": "3.25", "col_header": "B (%)", "value": "95"}, {"table_index": 3, "row_index": 6, "col_index": 4, "row_label": "3.25", "col_header": "flow rate (mL min–1)", "value": "0.5"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Klebsiella pneumoniae E1120", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Klebsiella pneumoniae E1267", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Klebsiella pneumoniae 4371", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Acinetobacter baumannii Z13", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).