
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
doi__10.1186_s40409-016-0058-7

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "The antimicrobial activity of Es-termicin", "footnotes": ["Ampicillin was used as a positive control. ND means no activity was detectable under the tested dosage of samples up to 400 μg/mL. aMIC, minimum inhibitory concentration required for total inhibition of cell growth in liquid medium"], "header_rows": [["Microorganisms", "aMIC (μg/mL)", "aMIC (μg/mL)"], ["Ampicillin", "Termicin"], ["Gram-positive bacteria", "", ""]], "longform_cells": [{"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Staphylococcus aureus ATCC 25923", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "4"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Staphylococcus aureus ATCC 25923", "col_header": "aMIC (μg/mL) / Termicin", "value": "ND"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Enterococcus faecalis ATCC 29212", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "32"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Enterococcus faecalis ATCC 29212", "col_header": "aMIC (μg/mL) / Termicin", "value": "200"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Staphylococcus aureus (IS 10#)", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "ND"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Staphylococcus aureus (IS 10#)", "col_header": "aMIC (μg/mL) / Termicin", "value": "ND"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Staphylococcus aureus (IS 39#)", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "ND"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "Staphylococcus aureus (IS 39#)", "col_header": "aMIC (μg/mL) / Termicin", "value": "ND"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Haemophilus influenza ATCC 49767", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "32"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "Haemophilus influenza ATCC 49767", "col_header": "aMIC (μg/mL) / Termicin", "value": "ND"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Pseudomonas aeruginosa CMCCB1010", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "32"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "Pseudomonas aeruginosa CMCCB1010", "col_header": "aMIC (μg/mL) / Termicin", "value": "ND"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "Escherichia coli (IS 121#)", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "ND"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "Escherichia coli (IS 121#)", "col_header": "aMIC (μg/mL) / Termicin", "value": "ND"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "Pseudomonas aeruginosa (IS 320#)", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "ND"}, {"table_index": 1, "row_index": 12, "col_index": 3, "row_label": "Pseudomonas aeruginosa (IS 320#)", "col_header": "aMIC (μg/mL) / Termicin", "value": "ND"}, {"table_index": 1, "row_index": 14, "col_index": 2, "row_label": "Candida albicans ATCC 2002", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "32"}, {"table_index": 1, "row_index": 14, "col_index": 3, "row_label": "Candida albicans ATCC 2002", "col_header": "aMIC (μg/mL) / Termicin", "value": "50"}, {"table_index": 1, "row_index": 15, "col_index": 2, "row_label": "Candida albicans ATCC 90028", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "32"}, {"table_index": 1, "row_index": 15, "col_index": 3, "row_label": "Candida albicans ATCC 90028", "col_header": "aMIC (μg/mL) / Termicin", "value": "25"}, {"table_index": 1, "row_index": 16, "col_index": 2, "row_label": "Candida albicans ATCC 90030", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "32"}, {"table_index": 1, "row_index": 16, "col_index": 3, "row_label": "Candida albicans ATCC 90030", "col_header": "aMIC (μg/mL) / Termicin", "value": "50"}, {"table_index": 1, "row_index": 17, "col_index": 2, "row_label": "Candida parapsilosis ATCC 22019", "col_header": "aMIC (μg/mL) / Ampicillin", "value": "32"}, {"table_index": 1, "row_index": 17, "col_index": 3, "row_label": "Candida parapsilosis ATCC 22019", "col_header": "aMIC (μg/mL) / Termicin", "value": "100"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Cloning and purification of the first termicin-like peptide from the cockroach Eupolyphaga sinensis", "db_measure": "Bridge", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Cloning and purification of the first termicin-like peptide from the cockroach Eupolyphaga sinensis"}]

Return ONLY the JSON array now (one object per assertion above).