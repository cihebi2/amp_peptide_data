
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
doi__10.1186_s12917-020-02620-z

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Synthetic peptides tested for antibacterial activity", "footnotes": ["aThe cysteines forming a disulfide bond are shadowed; bthe glycine mutation from the cysteine is boxed"], "header_rows": [["Peptides", "Amino acid sequences (N-terminal to C-terminal)", "Length (AA)", "Molecular weight", "Purity(%)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "bLfcin", "col_header": "Amino acid sequences (N-terminal to C-terminal)", "value": "FKCRRWQWRMKKLGAPSITCVRRAF"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "bLfcin", "col_header": "Length (AA)", "value": "25"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "bLfcin", "col_header": "Molecular weight", "value": "3125.82"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "bLfcin", "col_header": "Purity(%)", "value": ">â€‰95"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "bLfcin DB", "col_header": "Amino acid sequences (N-terminal to C-terminal)", "value": "FKCRRWQWRMKKLGAPSITCVRRAF (with a disulfide bond)a"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "bLfcin DB", "col_header": "Length (AA)", "value": "25"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "bLfcin DB", "col_header": "Molecular weight", "value": "3123.82"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "bLfcin DB", "col_header": "Purity(%)", "value": ">â€‰95"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "bLfcin C36G", "col_header": "Amino acid sequences (N-terminal to C-terminal)", "value": "FKCRRWQWRMKKLGAPSITGVRRAFb"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "bLfcin C36G", "col_header": "Length (AA)", "value": "25"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "bLfcin C36G", "col_header": "Molecular weight", "value": "3079.73"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "bLfcin C36G", "col_header": "Purity(%)", "value": ">â€‰95"}]}, {"table_index": 2, "label": "Table 2", "caption": "Antibacterial activity of the designed synthetic peptides against T. pyogenes and E. coli", "footnotes": ["Note: The MIC50 and MIC90 represent the concentrations required to inhibit 50 and 90% of the strains, respectively; MIC50, MIC90, and MBC in Âµg/mL (ÂµM)"], "header_rows": [["Strain", "Antibacterial index", "Lfcin", "Lfcin DB", "Lfcin C36G"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Trueperella pyogenesisolate", "col_header": "Antibacterial index", "value": "MIC50"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Trueperella pyogenesisolate", "col_header": "Lfcin", "value": "3.9 (1.2)"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "Trueperella pyogenesisolate", "col_header": "Lfcin DB", "value": "3.9 (1.2)"}, {"table_index": 2, "row_index": 2, "col_index": 5, "row_label": "Trueperella pyogenesisolate", "col_header": "Lfcin C36G", "value": "7.8 (2.5)"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "MIC90", "col_header": "Antibacterial index", "value": "7.8 (2.5)"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "MIC90", "col_header": "Lfcin", "value": "3.9 (1.2)"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "MIC90", "col_header": "Lfcin DB", "value": "15.6 (5.0)"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "MBC", "col_header": "Antibacterial index", "value": "7.8 (2.5)"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "MBC", "col_header": "Lfcin", "value": "3.9 (1.2)"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "MBC", "col_header": "Lfcin DB", "value": "15.6 (5.0)"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Trueperella pyogenesATCC 19,411", "col_header": "Antibacterial index", "value": "MIC50"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Trueperella pyogenesATCC 19,411", "col_header": "Lfcin", "value": "3.9 (1.2)"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "Trueperella pyogenesATCC 19,411", "col_header": "Lfcin DB", "value": "3.9 (1.2)"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "Trueperella pyogenesATCC 19,411", "col_header": "Lfcin C36G", "value": "7.8 (2.5)"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "MIC90", "col_header": "Antibacterial index", "value": "3.9 (2.5)"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "MIC90", "col_header": "Lfcin", "value": "3.9 (1.2)"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "MIC90", "col_header": "Lfcin DB", "value": "7.8 (5.0)"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "MBC", "col_header": "Antibacterial index", "value": "7.8 (2.5)"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "MBC", "col_header": "Lfcin", "value": "3.9 (1.2)"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "MBC", "col_header": "Lfcin DB", "value": "15.6 (5.0)"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "Escherichia coliATCC 25,922", "col_header": "Antibacterial index", "value": "MIC50"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "Escherichia coliATCC 25,922", "col_header": "Lfcin", "value": "62.5 (20.0)"}, {"table_index": 2, "row_index": 8, "col_index": 4, "row_label": "Escherichia coliATCC 25,922", "col_header": "Lfcin DB", "value": "125.0 (40.0)"}, {"table_index": 2, "row_index": 8, "col_index": 5, "row_label": "Escherichia coliATCC 25,922", "col_header": "Lfcin C36G", "value": "125.0 (40.6)"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "MIC90", "col_header": "Antibacterial index", "value": "62.5 (20.0)"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "MIC90", "col_header": "Lfcin", "value": "250.0 (80.0)"}, {"table_index": 2, "row_index": 9, "col_index": 4, "row_label": "MIC90", "col_header": "Lfcin DB", "value": "125.0 (40.6)"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "MBC", "col_header": "Antibacterial index", "value": "62.5 (20.0)"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "MBC", "col_header": "Lfcin", "value": "250.0 (80.0)"}, {"table_index": 2, "row_index": 10, "col_index": 4, "row_label": "MBC", "col_header": "Lfcin DB", "value": "125.0 (40.6)"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "CAMP", "db_subject_text": "Trueperella pyogenes ATCC 19411[MIC50 = 7.8 microg/ml], Trueperella pyogenes ATCC 19411[MIC90 = 7.8 microg/ml], Trueperella pyogenes ATCC 19411[MBC = 15.6 microg/ml], Trueperella pyogenes[MIC50 = 7.8 microg/ml], Trueperella pyogenes[MIC90 = 15.6 microg/ml], Trueperella pyogenes[MBC = 15.6 microg/ml], Escherichia coli ATCC 25922[MIC50 = 125 microg/ml], Escherichia coli ATCC 25922[MIC90 = 125 microg/ml], Escherichia coli ATCC 25922[MBC = 125 microg/ml]", "db_measure": "TEXT", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Lfcin-B"}]

Return ONLY the JSON array now (one object per assertion above).