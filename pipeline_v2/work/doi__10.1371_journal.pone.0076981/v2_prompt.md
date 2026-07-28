
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
doi__10.1371_journal.pone.0076981

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Minimum inhibitory concentration (MIC) and minimum fungicidal concentration (MFC) for Mucorales isolates (µg/ml).", "footnotes": [], "header_rows": [["Isolate", "Test medium", "Test medium", "Test medium", "Test medium"], ["", "RPMI 1640", "RPMI 1640", "YAG", "YAG"], ["", "MIC", "MFC", "MIC", "MFC"]], "longform_cells": [{"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Mucor circinelloides 4030", "col_header": "Test medium / RPMI 1640 / MIC", "value": "300"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Mucor circinelloides 4030", "col_header": "Test medium / RPMI 1640 / MFC", "value": "600"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "Mucor circinelloides 4030", "col_header": "Test medium / YAG / MIC", "value": "600"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "Mucor circinelloides 4030", "col_header": "Test medium / YAG / MFC", "value": "Not active"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Mucor circinelloides 4480", "col_header": "Test medium / RPMI 1640 / MIC", "value": "300"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Mucor circinelloides 4480", "col_header": "Test medium / RPMI 1640 / MFC", "value": "600"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "Mucor circinelloides 4480", "col_header": "Test medium / YAG / MIC", "value": "600"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "Mucor circinelloides 4480", "col_header": "Test medium / YAG / MFC", "value": "Not active"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Mucor circinelloides 5904", "col_header": "Test medium / RPMI 1640 / MIC", "value": "300"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Mucor circinelloides 5904", "col_header": "Test medium / RPMI 1640 / MFC", "value": "600"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "Mucor circinelloides 5904", "col_header": "Test medium / YAG / MIC", "value": "600"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "Mucor circinelloides 5904", "col_header": "Test medium / YAG / MFC", "value": "Not active"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Rhizopus oryzae 3140", "col_header": "Test medium / RPMI 1640 / MIC", "value": "300"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "Rhizopus oryzae 3140", "col_header": "Test medium / RPMI 1640 / MFC", "value": "600"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "Rhizopus oryzae 3140", "col_header": "Test medium / YAG / MIC", "value": "300"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "Rhizopus oryzae 3140", "col_header": "Test medium / YAG / MFC", "value": "Not active"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Rhizopus oryzae 4153", "col_header": "Test medium / RPMI 1640 / MIC", "value": "300"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "Rhizopus oryzae 4153", "col_header": "Test medium / RPMI 1640 / MFC", "value": "600"}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "Rhizopus oryzae 4153", "col_header": "Test medium / YAG / MIC", "value": "300"}, {"table_index": 1, "row_index": 8, "col_index": 5, "row_label": "Rhizopus oryzae 4153", "col_header": "Test medium / YAG / MFC", "value": "Not active"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Rhizopus sp. 4523", "col_header": "Test medium / RPMI 1640 / MIC", "value": "300"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "Rhizopus sp. 4523", "col_header": "Test medium / RPMI 1640 / MFC", "value": "600"}, {"table_index": 1, "row_index": 9, "col_index": 4, "row_label": "Rhizopus sp. 4523", "col_header": "Test medium / YAG / MIC", "value": "300"}, {"table_index": 1, "row_index": 9, "col_index": 5, "row_label": "Rhizopus sp. 4523", "col_header": "Test medium / YAG / MFC", "value": "Not active"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Rhizopus homothallicus 5790", "col_header": "Test medium / RPMI 1640 / MIC", "value": "300"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "Rhizopus homothallicus 5790", "col_header": "Test medium / RPMI 1640 / MFC", "value": "600"}, {"table_index": 1, "row_index": 10, "col_index": 4, "row_label": "Rhizopus homothallicus 5790", "col_header": "Test medium / YAG / MIC", "value": "300"}, {"table_index": 1, "row_index": 10, "col_index": 5, "row_label": "Rhizopus homothallicus 5790", "col_header": "Test medium / YAG / MFC", "value": "Not active"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "Rhizopus oryzae 5799", "col_header": "Test medium / RPMI 1640 / MIC", "value": "300"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "Rhizopus oryzae 5799", "col_header": "Test medium / RPMI 1640 / MFC", "value": "600"}, {"table_index": 1, "row_index": 11, "col_index": 4, "row_label": "Rhizopus oryzae 5799", "col_header": "Test medium / YAG / MIC", "value": "300"}, {"table_index": 1, "row_index": 11, "col_index": 5, "row_label": "Rhizopus oryzae 5799", "col_header": "Test medium / YAG / MFC", "value": "Not active"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "Rhizopus oryzae 6093", "col_header": "Test medium / RPMI 1640 / MIC", "value": "300"}, {"table_index": 1, "row_index": 12, "col_index": 3, "row_label": "Rhizopus oryzae 6093", "col_header": "Test medium / RPMI 1640 / MFC", "value": "600"}, {"table_index": 1, "row_index": 12, "col_index": 4, "row_label": "Rhizopus oryzae 6093", "col_header": "Test medium / YAG / MIC", "value": "300"}, {"table_index": 1, "row_index": 12, "col_index": 5, "row_label": "Rhizopus oryzae 6093", "col_header": "Test medium / YAG / MFC", "value": "Not active"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "CAMP", "db_subject_text": "Acinetobacter baumannii ATCC 19606[MIC = 300 microg/ml], Escherichia coli ATCC 25922[MIC = 150 microg/ml], Klebsiella pneumoniae[MIC = 300 microg/ml], Pseudomonas aeruginosa PAO1[MIC = 150 microg/ml], Pseudomonas aeruginosa PA14[MIC = 150 microg/ml], Stenotrophomonas maltophilia[MIC = 300 microg/ml], Enterococcus faecalis, Staphylococcus aureus, Staphylococcus epidermidis, Streptococcus pneumoniae, Human breast adenocarcinoma MDA-MB-231[80-90% Killing = 10 microM], Human breast adenocarcinoma MDA-MB-231[90-100% Killing = 50 microM], Mucor circinelloides[MIC = 300 microg/ml], Mucor circinelloides[MFC = 600 microg/ml], Mucor circinelloides[MIC = 600 microg/ml], Rhizopus oryzae[MIC = 300 microg/ml], Rhizopus oryzae[MFC = 600 microg/ml], Rhizopus homothallicus[MIC = 300 microg/ml], Rhizopus homothallicus[MFC = 600 microg/ml], Pseudomonas aeruginosa PAO1[MIC = 300 microg/ml], Pseudomonas aeruginosa NCGM2.S1[MIC = 300 microg/ml], Pseudomonas aeruginosa[MIC >300 microg/ml], Pseudomonas aeruginosa PAO4290[MIC = 300 microg/ml], Acinetobacter baumannii ATCC 15308[MIC = 300 microg/ml], Acinetobacter baumannii[MIC = 64-128 microg/ml], Escherichia coli ATCC 25922[MIC >300 microg/ml], Escherichia coli[MIC = 64 microg/ml], Klebsiella pneumoniae ATCC 15380[MIC >128 microg/ml], Klebsiella pneumoniae ATCC BAA-2146[MIC >128 microg/ml], Serratia marcescens NBRC 102204[MIC >256 microg/ml], Staphylococcus aureus ATCC 25923[MIC >128 microg/ml], Human hepatocellular carcinoma HepG2[LD50 >256 microg/ml], Human hepatocellular carcinoma HepG2[10-20% Killing = 250 microg/ml], Bacillus subtilis PS832[MIC = 0.5 microM], Bacillus subtilis PS832[MIC = 0.25 microM], Staphylococcus epidermidis ATCC 12228[MIC = 4 microM], Escherichia coli DL7[MIC = 1 microM], Klebsiella aerogenes ATCC 13048[MIC >32 microM], Escherichia coli ATCC 25922[MIC = 6 microM], Pseudomonas aeruginosa ATCC 27853[MIC = 6 microM], Staphylococcus aureus ATCC 25923[MIC = 6 microM], Escherichia coli ATCC 25922[MBC = 10 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Pro-apoptotic peptide AMD, PAP AMD"}]

Return ONLY the JSON array now (one object per assertion above).