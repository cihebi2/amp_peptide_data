
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
doi__10.1002_advs.202507457

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Performance comparison of KPPepGen and baseline methods for generated peptides.", "footnotes": ["The best‐performing results are marked in bold and the suboptimal results are underlined. The superscript ‘†’ indicates methods that support the one‐against‐all strategy in peptide generation, while all unlabeled methods follow the one‐against‐one strategy. ‘#’ denotes methods that were originally designed for protein generation and subsequently adapted for peptide design. ‘All’ indicates the average performance across all 56 pathogens. ns, no statistical significance; * p<5e‐2; ** p<1e‐2; *** p<1e‐3."], "header_rows": [["Methods", "Methods", "Similarity ↓", "Similarity ↓", "Instability ↓", "Instability ↓", "TM_tend ↓", "TM_tend ↓", "Physicochemical property", "Physicochemical property", "Physicochemical property", "Physicochemical property", "Physicochemical property", "Physicochemical property", "Physicochemical property", "Physicochemical property"], ["", "", "", "", "", "", "", "", "Charge", "Charge", "Isoelectric", "Isoelectric", "Hydrophobic", "Hydrophobic", "Aromaticity", "Aromaticity"], ["", "", "All", "Least‐10", "All", "Least‐10", "All", "Least‐10", "All", "Least‐10", "All", "Least‐10", "All", "Least‐10", "All", "Least‐10"], ["Positive‐only learning", "LSTM‐RNN", "48.96", "57.33", "51.03", "53.77", "0.694", "0.711", "***", "***", "ns", "*", "**", "***", "*", "*"], ["AMPGen", "46.23", "55.76", "49.81", "51.07", "0.725", "0.741", "***", "***", "**", "***", "***", "***", "**", "*"], ["ProtGPT2#", "46.45", "54.12", "49.11", "50.62", "0.733", "0.749", "***", "***", "***", "***", "***", "***", "***", "***"], ["EvoDiff#", "46.23", "55.66", "48.37", "49.42", "0.588", "0.612", "*", "**", "*", "**", "***", "***", "**", "***"], ["Discriminator ‐guided filtering", "AMPTrans", "47.61", "54.27", "49.25", "50.11", "0.727", "0.764", "***", "***", "***", "***", "*", "***", "***", "***"], ["LSTM‐Pep", "48.15", "56.53", "49.97", "52.62", "0.719", "0.757", "***", "***", "***", "***", "***", "***", "*", "**"], ["AMPGAN", "51.19", "59.70", "51.72", "54.04", "0.740", "0.788", "**", "**", "***", "***", "***", "***", "***", "***"], ["RLGen", "46.72", "54.39", "50.13", "52.88", "0.746", "0.750", "***", "***", "***", "***", "*", "**", "ns", "*"], ["Latent space sampling", "WAE‐PSO", "56.91", "63.28", "49.34", "50.75", "0.753", "0.766", "***", "***", "***", "***", "***", "***", "**", "**"], ["ProteoGAN#", "41.29", "46.18", "44.90", "46.73", "0.553", "0.637", "***", "***", "***", "***", "**", "**", "***", "***"], ["AMPGAN‐v2", "43.03", "45.62", "44.53", "46.79", "0.549", "0.651", "***", "***", "*", "**", "ns", "ns", "***", "***"], ["Conditional generation", "ProGen†,#", "40.56", "44.16", "43.49", "45.94", "0.524", "0.622", "*", "*", "ns", "**", "ns", "ns", "*", "**"], ["HydrAMP", "41.95", "45.07", "44.02", "46.47", "0.572", "0.667", "***", "***", "***", "***", "***", "**", "**", "***"], ["AR-VAE†,#", "41.93", "47.85", "45.45", "47.05", "0.554", "0.658", "**", "*", "***", "***", "**", "**", "***", "***"], ["Cut&CLIP†", "41.52", "45.19", "43.92", "46.40", "0.550", "0.651", "**", "**", "**", "***", "*", "**", "**", "***"], ["Prefixprot†,#", "40.67", "44.25", "43.78", "46.14", "0.540", "0.644", "***", "***", "***", "***", "**", "**", "ns", "ns"], ["KPPepGen†", "34.54", "37.27", "40.55", "42.52", "0.440", "0.513", "ns", "ns", "ns", "ns", "ns", "ns", "ns", "ns"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human bronchial epithelial cells BEAS-2B", "db_measure": "50% Cytotoxicity", "db_value": ">50", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Pep2"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Enterococcus faecalis ATCC 29212", "db_measure": "MIC", "db_value": "128", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Pep2"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human bronchial epithelial cells BEAS-2B", "db_measure": "50% Cytotoxicity", "db_value": "300", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Pep10"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human bronchial epithelial cells BEAS-2B", "db_measure": "50% Cytotoxicity", "db_value": ">50", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Pep2"}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Enterococcus faecalis ATCC 29212", "db_measure": "MIC", "db_value": "128", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Pep2"}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Human bronchial epithelial cells BEAS-2B", "db_measure": "50% Cytotoxicity", "db_value": "300", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Pep10"}, {"assertion_index": 6, "database": "APD6", "db_subject_text": "Controllable Generation of Pathogen-Specific Antimicrobial Peptides Through Knowledge-Aware Prompt Diffusion Model.", "db_measure": "Sequence analysis: APD analysis reveals that this sequence is similar (41.67%) to synthetic CGS14. S: 14%, R: 29%. Activity: active against E. coli (MIC 16 ug/ml) and S.aureus (MIC 256 ug/ml). Warning: other bacteria not tested.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Pep3 (Predicted AMPs, Arg-rich, UCLL1)"}, {"assertion_index": 7, "database": "APD6", "db_subject_text": "Controllable Generation of Pathogen-Specific Antimicrobial Peptides Through Knowledge-Aware Prompt Diffusion Model.", "db_measure": "Sequence analysis: APD analysis reveals that this sequence is similar (42.11%) to synthetic CGS9. W: 17%, R: 28%. Activity: active against E. coli (MIC 32 ug/ml) and S.aureus (MIC 128 ug/ml). Warning: other bacteria not tested.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Pep9 (Predicted AMPs, Arg-rich, UCLL1)"}]

Return ONLY the JSON array now (one object per assertion above).