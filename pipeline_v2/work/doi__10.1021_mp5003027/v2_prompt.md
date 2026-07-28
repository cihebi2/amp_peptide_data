
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
doi__10.1021_mp5003027

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Synthesized Peptides Used for Antimicrobial Activity", "footnotes": [], "header_rows": [["peptide", "peptide sequence", "abbreviation"], ["1", "[RRRRWWWW]", "[R4W4]"], ["2", "RRRRWWWW-COOH", "R4W4"], ["3", "[RRRRWWW]", "[R4W3]"], ["4", "RRRRWWW-COOH", "R4W3"], ["5", "[EEEEWWWW]", "[E4W4]"], ["6", "[EEEEWWW]", "[E4W3]"], ["7", "[KRRRRR]", "[KR5]"], ["8", "octanoyl-[KRRRRR]", "C8-[R5]"], ["9", "dodecanoyl-[KRRRRR]", "C12-[R5]"], ["10", "hexadecanoyl-[KRRRRR]", "C16-[R5]"], ["11", "N-acetyl-l-tryptophanyl-12-aminododecanoyl-[KRRRRR]", "W-C12-[R5]"], ["12", "N-acetyl-WWWW-[KRRRRR]", "W4-[R5]"], ["13", "dodecanoyl-[KRRRRRR]", "C12-[R6]"], ["14", "dodecanoyl-KRRRRR-COOH", "C12-(R5)"]], "longform_cells": []}, {"table_index": 2, "label": "Table 2", "caption": "Antibacterial Activities of Synthetic Peptides against Gram-Positive and Gram-Negative Strains", "footnotes": ["Values in parentheses are MICs in units of micromolar.", "Tetracycline and tobramycin were used as controls for MRSA and P. aeruginosa, respectively."], "header_rows": [["", "MIC (μg/mL) (μM)a", "MIC (μg/mL) (μM)a"], ["peptide", "methicillin-resistant S. aureus", "P. aeruginosa"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "1", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "2.67 (1.95)"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "1", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": "42.8 (31.3)"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "2", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "43.4 (31.3)"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "2", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": "21.7 (15.6)"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "3", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "18.5 (15.6)"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "3", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": "37.0 (31.3)"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "4", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "150 (125)"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "4", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": "150 (125)"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "5", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": ">158 (>125)"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "5", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": ">158 (>125)"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "6", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": ">134 (>125)"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "6", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": ">134 (>125)"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "7", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": ">114 (>125)"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "7", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": ">114 (>125)"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "8", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "129 (125)"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "8", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": ">129 (>125)"}, {"table_index": 2, "row_index": 11, "col_index": 2, "row_label": "9", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "8.53 (7.81)"}, {"table_index": 2, "row_index": 11, "col_index": 3, "row_label": "9", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": "136 (125)"}, {"table_index": 2, "row_index": 12, "col_index": 2, "row_label": "10", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "8.97 (7.81)"}, {"table_index": 2, "row_index": 12, "col_index": 3, "row_label": "10", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": ">143 (>125)"}, {"table_index": 2, "row_index": 13, "col_index": 2, "row_label": "11", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "83.4 (62.5)"}, {"table_index": 2, "row_index": 13, "col_index": 3, "row_label": "11", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": "167 (125)"}, {"table_index": 2, "row_index": 14, "col_index": 2, "row_label": "12", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "53.0 (31.3)"}, {"table_index": 2, "row_index": 14, "col_index": 3, "row_label": "12", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": ">212 (>125)"}, {"table_index": 2, "row_index": 15, "col_index": 2, "row_label": "13", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "9.75 (7.81)"}, {"table_index": 2, "row_index": 15, "col_index": 3, "row_label": "13", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": "156 (125)"}, {"table_index": 2, "row_index": 16, "col_index": 2, "row_label": "14", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "69.3 (62.5)"}, {"table_index": 2, "row_index": 16, "col_index": 3, "row_label": "14", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": ">139 (>125)"}, {"table_index": 2, "row_index": 17, "col_index": 2, "row_label": "controlb", "col_header": "MIC (μg/mL) (μM)a / methicillin-resistant S. aureus", "value": "0.156 (0.352)"}, {"table_index": 2, "row_index": 17, "col_index": 3, "row_label": "controlb", "col_header": "MIC (μg/mL) (μM)a / P. aeruginosa", "value": "0.731 (1.56)"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "KRRRRR", "db_claimed_peptide_name": "KR5"}]

Return ONLY the JSON array now (one object per assertion above).