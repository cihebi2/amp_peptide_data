
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
doi__10.1155_2013_939804

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Anticancer peptide and proteins from bovine milk [5].", "footnotes": ["ζCharacteristic cluster sequence of CPPs.", "†Molecular weight expressed in kDa."], "header_rows": [["Family proteins", "Protein precursors", "", "Concentration (g/L)", "M.W.†", "Peptide fragments", "Amino acid sequence"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "", "col_header": "Concentration (g/L)", "value": "24–28"}, {"table_index": 1, "row_index": 2, "col_index": 6, "row_label": "", "col_header": "Peptide fragments", "value": "Caseinphosphopeptides"}, {"table_index": 1, "row_index": 2, "col_index": 7, "row_label": "", "col_header": "Amino acid sequence", "value": "PPPEEζ"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "", "col_header": "Protein precursors", "value": "α s1-casein"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "", "col_header": "", "value": "α s1-CN"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "", "col_header": "Concentration (g/L)", "value": "12–15"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "", "col_header": "M.W.†", "value": "22.1–23.7"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "", "col_header": "Peptide fragments", "value": "α s1-casein f(90–95)"}, {"table_index": 1, "row_index": 3, "col_index": 7, "row_label": "", "col_header": "Amino acid sequence", "value": "RYLGYL"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "", "col_header": "Peptide fragments", "value": "α s1-casein f(90–96)"}, {"table_index": 1, "row_index": 4, "col_index": 7, "row_label": "", "col_header": "Amino acid sequence", "value": "RYLGYLE"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "Caseins", "col_header": "Peptide fragments", "value": "α s1-casomorphin f(158–162)"}, {"table_index": 1, "row_index": 5, "col_index": 7, "row_label": "Caseins", "col_header": "Amino acid sequence", "value": "YVPFP"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "", "col_header": "Protein precursors", "value": "β-casein"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "", "col_header": "", "value": "β-CN"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "", "col_header": "Concentration (g/L)", "value": "9–11"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "", "col_header": "M.W.†", "value": "23.9–24.1"}, {"table_index": 1, "row_index": 6, "col_index": 6, "row_label": "", "col_header": "Peptide fragments", "value": "β-Casomorphins 5 f(60–64)"}, {"table_index": 1, "row_index": 6, "col_index": 7, "row_label": "", "col_header": "Amino acid sequence", "value": "YPFPG"}, {"table_index": 1, "row_index": 7, "col_index": 6, "row_label": "", "col_header": "Peptide fragments", "value": "β-Casomorphins 7 f(60–66)"}, {"table_index": 1, "row_index": 7, "col_index": 7, "row_label": "", "col_header": "Amino acid sequence", "value": "YPFPGPI"}, {"table_index": 1, "row_index": 8, "col_index": 6, "row_label": "", "col_header": "Peptide fragments", "value": "Morphiceptin f(60–63)-NH2"}, {"table_index": 1, "row_index": 8, "col_index": 7, "row_label": "", "col_header": "Amino acid sequence", "value": "YPFP-NH2"}, {"table_index": 1, "row_index": 9, "col_index": 4, "row_label": "", "col_header": "Concentration (g/L)", "value": "5–7"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "", "col_header": "Protein precursors", "value": "β-lactoglobulin"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "", "col_header": "", "value": "β-lg"}, {"table_index": 1, "row_index": 10, "col_index": 4, "row_label": "", "col_header": "Concentration (g/L)", "value": "2–4"}, {"table_index": 1, "row_index": 10, "col_index": 5, "row_label": "", "col_header": "M.W.†", "value": "18.3"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "Whey proteins", "col_header": "Protein precursors", "value": "α-lactalbumin"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "Whey proteins", "col_header": "", "value": "α-la"}, {"table_index": 1, "row_index": 11, "col_index": 4, "row_label": "Whey proteins", "col_header": "Concentration (g/L)", "value": "1–1.5"}, {"table_index": 1, "row_index": 11, "col_index": 5, "row_label": "Whey proteins", "col_header": "M.W.†", "value": "14.2"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "", "col_header": "Protein precursors", "value": "Bovine serum albumin"}, {"table_index": 1, "row_index": 12, "col_index": 3, "row_label": "", "col_header": "", "value": "BSA"}, {"table_index": 1, "row_index": 12, "col_index": 4, "row_label": "", "col_header": "Concentration (g/L)", "value": "0.1–0.4"}, {"table_index": 1, "row_index": 12, "col_index": 5, "row_label": "", "col_header": "M.W.†", "value": "66"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "", "col_header": "Protein precursors", "value": "Lactoferrin"}, {"table_index": 1, "row_index": 13, "col_index": 3, "row_label": "", "col_header": "", "value": "Lf"}, {"table_index": 1, "row_index": 13, "col_index": 4, "row_label": "", "col_header": "Concentration (g/L)", "value": "0.1"}, {"table_index": 1, "row_index": 13, "col_index": 5, "row_label": "", "col_header": "M.W.†", "value": "80"}, {"table_index": 1, "row_index": 13, "col_index": 6, "row_label": "", "col_header": "Peptide fragments", "value": "Bovine lactoferricin (LfcinB)"}, {"table_index": 1, "row_index": 13, "col_index": 7, "row_label": "", "col_header": "Amino acid sequence", "value": "FKCRRWQWRMKKLGAPSITCVRRAF"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "Tumor cells: AZ-97 (Inhibition at 24-28 g/l)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Caseinphosphopeptides"}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Tumor cells: AZ-97 (Inhibition at 12-15 g/l)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "αs1-casein f(90_95)"}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "Tumor cells: AZ-97 (Inhibition at 9-11 g/l)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "β-Casomorphins 5 f(60_64)"}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "Tumor cells: AZ-97 (Inhibition at 24-28 g/l)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Potential anticarcinogenic peptides from bovine milk"}, {"assertion_index": 4, "database": "DRAMP", "db_subject_text": "Tumor cells: AZ-97 (Inhibition at 12-15 g/l)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Potential anticarcinogenic peptides from bovine milk"}, {"assertion_index": 5, "database": "DRAMP", "db_subject_text": "Tumor cells: AZ-97 (Inhibition at 9-11 g/l)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Potential anticarcinogenic peptides from bovine milk"}, {"assertion_index": 6, "database": "dbAMP", "db_subject_text": "Colon Cancer (Inhibition at 9-11g/l)", "db_measure": "Nonrecorded", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Bovine milk\n-Casomorphins 5 f(60_64)"}, {"assertion_index": 7, "database": "dbAMP", "db_subject_text": "Colon Cancer (Inhibition at 24-28g/l)", "db_measure": "Nonrecorded", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Caseinphosphopeptides\nBovine milk"}, {"assertion_index": 8, "database": "dbAMP", "db_subject_text": "Colon Cancer (Inhibition at 12-15g/l)", "db_measure": "Nonrecorded", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Bovine milk\ns1-casein f(90_95)"}]

Return ONLY the JSON array now (one object per assertion above).