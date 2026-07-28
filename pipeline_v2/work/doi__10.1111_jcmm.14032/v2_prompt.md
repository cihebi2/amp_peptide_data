
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
doi__10.1111_jcmm.14032

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "The primer sequences used in conducting the qPCR experiments", "footnotes": [], "header_rows": [["Target protein", "Sense primer", "Antisense primer"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "APAF‐1", "col_header": "Sense primer", "value": "5′‐CCTGTTGTCTCTTCTTCCAGTGT‐3′"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "APAF‐1", "col_header": "Antisense primer", "value": "5′‐AAAACAACTGGCCTCTGTGG‐3′"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "TNFR1", "col_header": "Sense primer", "value": "5′‐TGCCAGGAGAAACAGAACAC‐3′"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "TNFR1", "col_header": "Antisense primer", "value": "5′‐TCCTCAGTGCCCTTAACATTC‐3′"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Fas", "col_header": "Sense primer", "value": "5′‐ACTCACCAGCAACACCAAG‐3′"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Fas", "col_header": "Antisense primer", "value": "5′‐TCATGACTCCAGCAATAGTGG‐3′"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Bax", "col_header": "Sense primer", "value": "5′‐GAGCAGATCATGAAGACAGGG‐3′"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Bax", "col_header": "Antisense primer", "value": "5′‐AGTAGAAAAGGGCGACAACC‐3′"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Bcl‐2", "col_header": "Sense primer", "value": "5′‐GTGGATGACTGAGTACCTGAAC‐3′"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Bcl‐2", "col_header": "Antisense primer", "value": "5′‐CCTGCAGCTTTGTTTCATGG‐3′"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Bid", "col_header": "Sense primer", "value": "5′‐ATTAACCAGAACCTACGCACC‐3′"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "Bid", "col_header": "Antisense primer", "value": "5′‐TCTAGGAACGCTGTTGACATG‐3′"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Caspase 8", "col_header": "Sense primer", "value": "5′‐ATCCTGAAAAGAGTCTGTGCC‐3′"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "Caspase 8", "col_header": "Antisense primer", "value": "5′‐ATTCCTGTCCCTAATGCTGTG‐3′"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Caspase 9", "col_header": "Sense primer", "value": "5′‐CCTAGAAAACCTTACCCCAGTG‐3′"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "Caspase 9", "col_header": "Antisense primer", "value": "5′‐CACGGCAGAAGTTCACATTG‐3′"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "18S", "col_header": "Sense primer", "value": "5′‐CGGCTACCACATCCAAGGAA‐3′"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "18S", "col_header": "Antisense primer", "value": "5′‐AGCTGGAATTACCGCGGC‐3′"}]}, {"table_index": 2, "label": "Table 2", "caption": "Secondary structure analysis of Dermaseptin‐PS1 by using DICHROWEB online server", "footnotes": [], "header_rows": [["Percentage (%)", "α‐helix", "β‐sheet", "Random coil"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "NH4Ac", "col_header": "α‐helix", "value": "4"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "NH4Ac", "col_header": "β‐sheet", "value": "48"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "NH4Ac", "col_header": "Random coil", "value": "48"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "50% TFE +NH4Ac", "col_header": "α‐helix", "value": "25"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "50% TFE +NH4Ac", "col_header": "β‐sheet", "value": "15"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "50% TFE +NH4Ac", "col_header": "Random coil", "value": "60"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "", "db_measure": "CD", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Not available", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus NCTC 10788[MIC = 10 microM], Staphylococcus aureus NCTC 10788[MBC = 100 microM], Escherichia coli NCTC 10418[MIC = 10 microM], Escherichia coli NCTC 10418[MBC = 100 microM], Candida albicans NCPF 1467[MIC = 100 microM], Human glioblastoma U251-MG[IC50 = 5.419 microM]", "db_measure": "Gram+, Gram-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus NCTC 10788 (MIC=10μM)\nStaphylococcus aureus NCTC 10788 (MBC=100μM)\nEscherichia coli NCTC 10418 (MIC=10μM)\nEscherichia coli NCTC 10418 (MBC=100μM)\nCandida albicans NCPF 1467 (MIC=100μM)\nHuman glioblastoma U251-MG (IC50=5.419μM)", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "APD6", "db_subject_text": "Novel peptide dermaseptin-PS1 exhibits anticancer activity via induction of intrinsic apoptosis signalling", "db_measure": "Anti-Gram+ & Gram-, Antifungal, candidacidal, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).