
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
doi__10.1371_journal.pone.0095737

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Antimicrobial activity of alvinellacin.", "footnotes": ["Assays were performed against bacteria routinely used for antimicrobial assays or having a medical incidence, and against the scarce hydrothermal strains (asterisk*) cultivable under the conditions of a microbial assay. The minimal inhibitory concentration (MIC) and the minimal bactericidal concentration (MBC) are expressed as final concentration in µM. > denotes no activity detected at the given concentration. The MBC and MIC values are the same, indicating that the bacterial growth inhibition is due to the killing of bacteria."], "header_rows": [["", "MIC, µM", "MBC, µM"], ["Gram-negative bacteria", "", ""]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Escherichia coli D31", "col_header": "MIC, µM", "value": "0.012–0.024"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Escherichia coli D31", "col_header": "MBC, µM", "value": "0.048"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Escherichia coli D31 (300 mM NaCl)", "col_header": "MIC, µM", "value": "0.012–0.024"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Escherichia coli D31 (300 mM NaCl)", "col_header": "MBC, µM", "value": "0.048"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Escherichia coli D31 (500 mM NaCl)", "col_header": "MIC, µM", "value": "0.012–0.024"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Escherichia coli D31 (500 mM NaCl)", "col_header": "MBC, µM", "value": "0.048"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Pseudomonas sp.*", "col_header": "MIC, µM", "value": "0.001–0.003"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Pseudomonas sp.*", "col_header": "MBC, µM", "value": "0.012"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Vibrio diabolicus*", "col_header": "MIC, µM", "value": "0.048–0.096"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "Vibrio diabolicus*", "col_header": "MBC, µM", "value": ">0.19"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Vibrio MPV19", "col_header": "MIC, µM", "value": "0.012–0.024"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "Vibrio MPV19", "col_header": "MBC, µM", "value": "0.024"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Bacillus megaterium", "col_header": "MIC, µM", "value": "0.012–0.024"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "Bacillus megaterium", "col_header": "MBC, µM", "value": "0.024"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "Bacillus megaterium (300 mM NaCl)", "col_header": "MIC, µM", "value": "0.024–0.048"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "Bacillus megaterium (300 mM NaCl)", "col_header": "MBC, µM", "value": "0.048"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "Bacillus megaterium (500 mM NaCl)", "col_header": "MIC, µM", "value": "0.048–0.096"}, {"table_index": 1, "row_index": 12, "col_index": 3, "row_label": "Bacillus megaterium (500 mM NaCl)", "col_header": "MBC, µM", "value": "0.096"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "Staphylococcus aureus", "col_header": "MIC, µM", "value": "0.048–0.096"}, {"table_index": 1, "row_index": 13, "col_index": 3, "row_label": "Staphylococcus aureus", "col_header": "MBC, µM", "value": ">0.19"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Characterization and function of the first antibiotic isolated from a vent organism: the extremophile metazoan Alvinella pompejana", "db_measure": "NMR", "db_value": "APD6 entry text summary", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Alvinellacin"}]

Return ONLY the JSON array now (one object per assertion above).