
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
doi__10.3389_fmicb.2016.02006

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Peptide 35409 antibacterial activity against Gram-negative and Gram-positive bacteria.", "footnotes": ["Mean ± SD of three experiments", "G: growth"], "header_rows": [["", "", "MIC (μM)", "MIC (μM)", "MIC (μM)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Bacteria", "col_header": "", "value": "Bacteria"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Bacteria", "col_header": "MIC (μM)", "value": "35409"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "Bacteria", "col_header": "MIC (μM)", "value": "38659"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "Bacteria", "col_header": "MIC (μM)", "value": "C (-)"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Gram-negative", "col_header": "", "value": "Escherichia coli ML 35 (43827)"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Gram-negative", "col_header": "MIC (μM)", "value": "22 ± 1"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Gram-negative", "col_header": "MIC (μM)", "value": "G"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "Gram-negative", "col_header": "MIC (μM)", "value": "G"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "", "col_header": "", "value": "Pseudomonas aeruginosa 15442"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "", "col_header": "MIC (μM)", "value": "44 ± 1"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "", "col_header": "MIC (μM)", "value": "G"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "", "col_header": "MIC (μM)", "value": "G"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Gram-positive", "col_header": "", "value": "Staphylococcus aureus 29213"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Gram-positive", "col_header": "MIC (μM)", "value": "350 ± 1"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "Gram-positive", "col_header": "MIC (μM)", "value": "G"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "Gram-positive", "col_header": "MIC (μM)", "value": "G"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "Tumor cells: HeLa (Not active up to 44 µg/ml); HepG2 (Not active up to 44 µg/ml)", "db_measure": "Antimicrobial, Anticancer", "db_value": "Not available", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Peptide 35409"}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Tumor cells: HeLa (Not active up to 44 µg/ml); HepG2 (Not active up to 44 µg/ml)", "db_measure": "Antimicrobial, Anticancer", "db_value": "Not available", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "CAMP", "db_subject_text": "Staphylococcus aureus ATCC 29213[MIC = 350+-1 microM], Pseudomonas aeruginosa ATCC 15442[MIC = 44+-1 microM], Escherichia coli ML-35[MIC = 22+-1 microM], Human cervical carcinoma HeLa, Human hepatocellular carcinoma HepG2, Escherichia coli ATCC 25922[MIC = 25 microM], Escherichia coli ATCC 25922[MBC = 50 microM], Pseudomonas aeruginosa ATCC 27853[MIC >100 microM], Escherichia coli ATCC 43827[MIC = 25 microM], Escherichia coli ATCC 43827[MBC = 25 microM], Escherichia coli ATCC 35218[MIC = 6 microM], Escherichia coli ATCC 35218[MBC = 6 microM], Escherichia coli ATCC 11775[MIC >100 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "dbAMP", "db_subject_text": "Escherichia coli ATCC 25922 (MIC=25μM)\nEscherichia coli ATCC 25922 (MBC=50μM)\nPseudomonas aeruginosa ATCC 27853 (MIC=>100μM)\nEscherichia coli ATCC 43827 (MIC=25μM)\nEscherichia coli ATCC 43827 (MBC=25μM)\nEscherichia coli ATCC 35218 (MIC=6μM)\nEscherichia coli ATCC 35218 (MBC=6μM)\nEscherichia coli ATCC 11775 (MIC=>100μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).