
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
doi__10.1186_s13071-015-0669-9

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Primer sequences used for cloning and qPCR in this study", "footnotes": ["*Where Y stands for C or T, W stands for A or T, S stands for C or G , H stands for A, C or T, N stands for A, C, G or T, and I stands for hypoxanthine."], "header_rows": [["Primer", "Sequence (5′ → 3′)", "Application"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "3′ PCR primer", "col_header": "Sequence (5′ → 3′)", "value": "CGGGGTACGATGAGACACCA"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "3′ PCR primer", "col_header": "Application", "value": "3′ end screening"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "SibaDef -F1", "col_header": "Sequence (5′ → 3′)", "value": "TIYTIWSIATHWSNACNCC*"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "SibaDef -F1", "col_header": "Application", "value": "3′ end screening"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "SibaDef -R1", "col_header": "Sequence (5′ → 3′)", "value": "TCGTACATCAGTCAGATCCACCG"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "SibaDef -R1", "col_header": "Application", "value": "5′ end screening"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "5′ PCR primer", "col_header": "Sequence (5′ → 3′)", "value": "AAGCAGTGGTATCAACGCAGAGT"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "5′ PCR primer", "col_header": "Application", "value": "5′ end screening"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "SibaDef - F2", "col_header": "Sequence (5′ → 3′)", "value": "AGAAGAGCAACCTGCGACCTG"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "SibaDef - F2", "col_header": "Application", "value": "qPCR"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "SibaDef - R2", "col_header": "Sequence (5′ → 3′)", "value": "AGTCAGATCCACCGCCCGAAT"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "SibaDef - R2", "col_header": "Application", "value": "qPCR"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Actin-F", "col_header": "Sequence (5′ → 3′)", "value": "TGTTGTCACTGTACGCCTCCG"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "Actin-F", "col_header": "Application", "value": "qPCR"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Actin-R", "col_header": "Sequence (5′ → 3′)", "value": "TGATGTCGCGAACGATTTCCC"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "Actin-R", "col_header": "Application", "value": "qPCR"}]}, {"table_index": 2, "label": "Table 2", "caption": "Antimicrobial activity of Siba Def", "footnotes": ["*MIC: minimal inhibitory concentration. These MICs represent mean values of three independent experiments performed in duplicates. ND: no detectable activity."], "header_rows": [["Microorganisms", "MIC (μM)*"], ["Gram-positive bacteria", "Gram-positive bacteria"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Staphylococcus aureus ATCC 6538", "col_header": "MIC (μM)* / Gram-positive bacteria", "value": "0.83"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Bacillus subtilis ATCC 6633", "col_header": "MIC (μM)* / Gram-positive bacteria", "value": "1.04"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Bacillus cereus ATCC 14579", "col_header": "MIC (μM)* / Gram-positive bacteria", "value": "2.08"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Micrococcus luteus ATCC 4698", "col_header": "MIC (μM)* / Gram-positive bacteria", "value": "2.29"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "Gram-negative bacteria", "col_header": "MIC (μM)* / Gram-positive bacteria", "value": "Gram-negative bacteria"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "Escherichia coli ATCC 8739", "col_header": "MIC (μM)* / Gram-positive bacteria", "value": "ND"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "Pseudomonas aeruginosa ATCC 9027", "col_header": "MIC (μM)* / Gram-positive bacteria", "value": "ND"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Purification and characterization of a novel defensin from the salivary glands of the black fly, Simulium bannaense", "db_measure": "entry_text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "Staphylococcus aureus/Bacillus/Micrococcus plus Gram-negative target aggregate", "db_measure": "entry_text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "dbAMP", "db_subject_text": "Gram-positive target aggregate plus MammalianCells activity labels", "db_measure": "entry_text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).