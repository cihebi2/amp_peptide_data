
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
doi__10.3390_toxins10060227

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Comparison of lethal concentration (CL, μM) of MeuTxKα3, P30N, and Kα3-KFGGI on different bacterial species.", "footnotes": ["1 N.A.: no activity, indicating that no inhibition zone was observed at 1.0 nmol peptide each well."], "header_rows": [["Species", "MeuTxKα3", "P30N", "Kα3-KFGGI"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Methicillin-resistant Staphylococcus aureus (MRSA), P1374", "col_header": "MeuTxKα3", "value": "N.A. 1"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Methicillin-resistant Staphylococcus aureus (MRSA), P1374", "col_header": "P30N", "value": "N.A."}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "Methicillin-resistant Staphylococcus aureus (MRSA), P1374", "col_header": "Kα3-KFGGI", "value": "3.69"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Penicillin-resistant Staphylococcus aureus (PRSA), P1383", "col_header": "MeuTxKα3", "value": "5.39"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Penicillin-resistant Staphylococcus aureus (PRSA), P1383", "col_header": "P30N", "value": "0.87"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Penicillin-resistant Staphylococcus aureus (PRSA), P1383", "col_header": "Kα3-KFGGI", "value": "1.34"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Penicillin-resistant Staphylococcus epidermidis (PRSE), P1389", "col_header": "MeuTxKα3", "value": "N.A."}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Penicillin-resistant Staphylococcus epidermidis (PRSE), P1389", "col_header": "P30N", "value": "N.A."}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "Penicillin-resistant Staphylococcus epidermidis (PRSE), P1389", "col_header": "Kα3-KFGGI", "value": "5.35"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Staphylococcus warneri, CGMCC 1.2824", "col_header": "MeuTxKα3", "value": "N.A."}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Staphylococcus warneri, CGMCC 1.2824", "col_header": "P30N", "value": "N.A."}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "Staphylococcus warneri, CGMCC 1.2824", "col_header": "Kα3-KFGGI", "value": "5.39"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Streptococcus mutans, CGMCC 1.2499", "col_header": "MeuTxKα3", "value": "33.80"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Streptococcus mutans, CGMCC 1.2499", "col_header": "P30N", "value": "24.06"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "Streptococcus mutans, CGMCC 1.2499", "col_header": "Kα3-KFGGI", "value": "8.84"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Streptococcus salivarius, CGMCC 1.2498", "col_header": "MeuTxKα3", "value": "N.A."}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "Streptococcus salivarius, CGMCC 1.2498", "col_header": "P30N", "value": "N.A."}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "Streptococcus salivarius, CGMCC 1.2498", "col_header": "Kα3-KFGGI", "value": "0.71"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Streptococcus sanguinis, CGMCC 1.2497", "col_header": "MeuTxKα3", "value": "3.72"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "Streptococcus sanguinis, CGMCC 1.2497", "col_header": "P30N", "value": "N.A."}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "Streptococcus sanguinis, CGMCC 1.2497", "col_header": "Kα3-KFGGI", "value": "2.14"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "CAMP", "db_subject_text": "Staphylococcus aureus P1374, Staphylococcus aureus P1383[LC = 5.39 microM], Staphylococcus epidermidis P1389, Staphylococcus warneri CGMCC 1.2824, Streptococcus mutans CGMCC 1.2499[LC = 33.8 microM], Streptococcus salivarius CGMCC 1.2498, Streptococcus sanguinis CGMCC 1.2497[LC = 3.72 microM], Bacillus megaterium CGMCC 1.0459[LC = 14.26 microM], Bacillus subtilis CGMCC 1.2428[LC = 10.28 microM], Micrococcus luteus CGMCC 1.0290[LC = 4.66 microM], Xanthomonas oryzae[LC = 52.01 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "Staphylococcus aureus P1374, Staphylococcus aureus P1383[LC = 0.87 microM], Staphylococcus epidermidis P1389, Staphylococcus warneri CGMCC 1.2824, Streptococcus mutans CGMCC 1.2499[LC = 24.06 microM], Streptococcus salivarius CGMCC 1.2498, Streptococcus sanguinis CGMCC 1.2497, Bacillus megaterium CGMCC 1.0459[LC = 4.95 microM], Bacillus subtilis CGMCC 1.2428[LC = 6.11 microM], Micrococcus luteus CGMCC 1.0290[LC = 5.5 microM], Xanthomonas oryzae[LC = 17.68 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "dbAMP", "db_subject_text": "Staphylococcus aureus P1383 (LC=5.39μM)\nStreptococcus mutans CGMCC 1.2499 (LC=33.80μM)\nStreptococcus sanguinis CGMCC 1.2497 (LC=3.72μM)\nBacillus megaterium CGMCC 1.0459 (LC=14.26μM)\nBacillus subtilis CGMCC 1.2428 (LC=10.28μM)\nMicrococcus luteus CGMCC 1.0290 (LC=4.66μM)\nXanthomonas oryzae (LC=52.01μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "dbAMP", "db_subject_text": "Staphylococcus aureus P1383 (LC=0.87μM)\nStreptococcus mutans CGMCC 1.2499 (LC=24.06μM)\nBacillus megaterium CGMCC 1.0459 (LC=4.95μM)\nBacillus subtilis CGMCC 1.2428 (LC=6.11μM)\nMicrococcus luteus CGMCC 1.0290 (LC=5.50μM)\nXanthomonas oryzae (LC=17.68μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).