
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
doi__10.3389_fchem.2021.741290

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "TABLE 1", "caption": "Pagoamide A (1) was tested against a number of common pathogens.", "footnotes": ["The highest concentration tested was 64 μg/ml."], "header_rows": [["Name of pathogen", "MICa (μg/ml)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Bacillus subtilis BCRC 10614", "col_header": "MICa (μg/ml)", "value": "64"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Escherichia coli DH5α", "col_header": "MICa (μg/ml)", "value": ">"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Enterococcus faecalis BCRC 10789", "col_header": "MICa (μg/ml)", "value": ">"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Staphylococcus aureus BCRC 11863", "col_header": "MICa (μg/ml)", "value": ">"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Klebsiella pneumoniae BCRC 11546", "col_header": "MICa (μg/ml)", "value": ">"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Acinetobacter baumannii BCRC 10591", "col_header": "MICa (μg/ml)", "value": ">"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Pseudomonas aeruginosa BCRC 11864", "col_header": "MICa (μg/ml)", "value": ">"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Enterobacter cloacae BCRC 10401", "col_header": "MICa (μg/ml)", "value": ">"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Candida albicans BCRC 21538", "col_header": "MICa (μg/ml)", "value": ">"}]}, {"table_index": 2, "label": "FIGURE(vision:other) fchem-09-741290-g002.jpg", "caption": "codex-vision extracted from /home/cihebi/抗菌肽/数据集/batch/5-team/paper_packets/doi__10.3389_fchem.2021.741290/extracted/oa_package/local-DBAASP-PMC8476950/PMC8476950/fchem-09-741290-g002.jpg", "footnotes": [], "header_rows": [], "longform_cells": [{"table_index": 2, "row_index": "", "col_index": "", "row_label": "a", "col_header": "yield", "value": "92%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "c", "col_header": "yield", "value": "73%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "a", "col_header": "yield", "value": "81%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "d", "col_header": "yield", "value": "96%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "10", "col_header": "yield", "value": "63%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "3", "col_header": "yield", "value": "92%", "confidence": "printed"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "APD6 free-text activity/comment field", "db_measure": "APD6 free text embeds current-paper antimicrobial activity but the row citation/title point to the prior discovery paper.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Bacillus subtilis BCRC 10614", "db_measure": "MIC 64 μg/mL", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Escherichia coli DH5α", "db_measure": "Not active up to 64 μg/mL", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Enterococcus faecalis BCRC 10789", "db_measure": "Not active up to 64 μg/mL", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus BCRC 11863", "db_measure": "Not active up to 64 μg/mL", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Klebsiella pneumoniae BCRC 11546", "db_measure": "Not active up to 64 μg/mL", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Acinetobacter baumannii BCRC 10591", "db_measure": "Not active up to 64 μg/mL", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Pseudomonas aeruginosa BCRC 11864", "db_measure": "Not active up to 64 μg/mL", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Enterobacter cloacae BCRC 10401", "db_measure": "Not active up to 64 μg/mL", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Candida albicans BCRC 21538", "db_measure": "Not active up to 64 μg/mL", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).