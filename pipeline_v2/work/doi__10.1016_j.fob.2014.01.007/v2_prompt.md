
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
doi__10.1016_j.fob.2014.01.007

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1.", "caption": "Peptide sequences and molecular mass.", "footnotes": [], "header_rows": [["Name", "Sequence", "Mass (Da)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "WT1-pTj", "col_header": "Sequence", "value": "KDCERRFSRSDQLKRHQRRHTGVKPFQ-NH2"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "WT1-pTj", "col_header": "Mass (Da)", "value": "3395.84"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "b-WT1-pTj", "col_header": "Sequence", "value": "biotin-CGGKDCERRFSRSDQLKRHQRRHTGVKPFQ-NH2"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "b-WT1-pTj", "col_header": "Mass (Da)", "value": "3839.38"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "FITC-WT1-pTj", "col_header": "Sequence", "value": "KDCERRFSRSDQLKRHQRRHTGVKPFQK-FITC"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "FITC-WT1-pTj", "col_header": "Mass (Da)", "value": "3914.53"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "C PEP", "col_header": "Sequence", "value": "KDAERRFSRSDQLKRAQRRHTGVKPFQ-NH2"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "C PEP", "col_header": "Mass (Da)", "value": "3297.71"}]}, {"table_index": 2, "label": "Table 2.", "caption": "Antiproliferative activity of WT1-pTj on WT1-expressing tumor cell lines and nontumor forming cell lines.", "footnotes": ["EC50 is the concentration that decreases viability by 50% in a dose-dependent survival curve."], "header_rows": [["Cell lines", "EC50a (mol/l x 10−3)"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "A2058 human melanoma", "col_header": "EC50a (mol/l x 10−3)", "value": "0.455 ± 0.032"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "SK-MEL-28 human melanoma", "col_header": "EC50a (mol/l x 10−3)", "value": "0.680 ± 0.020"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "B16F10-Nex2 murine melanoma", "col_header": "EC50a (mol/l x 10−3)", "value": "0.466 ± 0.067"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "MCF-7 human breast cancer", "col_header": "EC50a (mol/l x 10−3)", "value": "0.247 ± 0.058"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "MDA-MB231 human breast cancer", "col_header": "EC50a (mol/l x 10−3)", "value": "0.759 ± 1.40"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "OVCAR-3 human ovarian cancer", "col_header": "EC50a (mol/l x 10−3)", "value": "0.208 ± 0.02"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "HL-60 human acute leukemia", "col_header": "EC50a (mol/l x 10−3)", "value": ">1"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "HFF human foreskin fibroblast", "col_header": "EC50a (mol/l x 10−3)", "value": ">1"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "MEF murine embryonic fibroblast", "col_header": "EC50a (mol/l x 10−3)", "value": ">1"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "Not available", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Not available", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "Not available", "db_measure": "Not available", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "Not available", "db_measure": "Not available", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).