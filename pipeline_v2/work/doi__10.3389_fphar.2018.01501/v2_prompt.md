
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
doi__10.3389_fphar.2018.01501

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Comparison of IC50 values determined for ChMAP-28 and melittin.", "footnotes": ["IC50 values are represented as the means ± standard deviations (SD) of at least three independent experiments. In the case of NHA cells, 50% inhibition was not reached even at the peptide concentration of 10 μM, thus the IC50 value could not be determined."], "header_rows": [["Cell line", "HL-60", "SKBR-3", "A431", "B16F1", "HEK293T", "HEF", "NHA"], ["Peptide", "IC50, μM", "IC50, μM", "IC50, μM", "IC50, μM", "IC50, μM", "IC50, μM", "IC50, μM"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "ChMAP-28", "col_header": "HL-60 / IC50, μM", "value": "3.39 ± 0.15"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "ChMAP-28", "col_header": "SKBR-3 / IC50, μM", "value": "5.63 ± 1.05"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "ChMAP-28", "col_header": "A431 / IC50, μM", "value": "6.49 ± 0.09"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "ChMAP-28", "col_header": "B16F1 / IC50, μM", "value": "4.82 ± 1.01"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "ChMAP-28", "col_header": "HEK293T / IC50, μM", "value": "5.09 ± 0.40"}, {"table_index": 1, "row_index": 3, "col_index": 7, "row_label": "ChMAP-28", "col_header": "HEF / IC50, μM", "value": "8.95 ± 2.68"}, {"table_index": 1, "row_index": 3, "col_index": 8, "row_label": "ChMAP-28", "col_header": "NHA / IC50, μM", "value": "ND (>10)"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Melittin", "col_header": "HL-60 / IC50, μM", "value": "1.86 ± 0.03"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Melittin", "col_header": "SKBR-3 / IC50, μM", "value": "2.03 ±0.09"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "Melittin", "col_header": "A431 / IC50, μM", "value": "1.09 ± 0.17"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "Melittin", "col_header": "B16F1 / IC50, μM", "value": "1.46 ± 0.07"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "Melittin", "col_header": "HEK293T / IC50, μM", "value": "1.42 ± 0.18"}, {"table_index": 1, "row_index": 4, "col_index": 7, "row_label": "Melittin", "col_header": "HEF / IC50, μM", "value": "1.64 ± 0.10"}, {"table_index": 1, "row_index": 4, "col_index": 8, "row_label": "Melittin", "col_header": "NHA / IC50, μM", "value": "1.83 ± 0.15"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "Tumor cells: HL-60 (IC50=3.39±0.15 μM); B16-F1 (IC50=4.82±1.01 μM); SK-BR-3 (IC50=5.63±1.05 μM); A431 (IC50=6.49±0.09 μM)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "GRFKRFRKKLKRLWHKVGPFVGPILHY", "db_claimed_peptide_name": "ChMAP-28"}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Tumor cells: HL-60 (IC50=3.39±0.15 μM); B16-F1 (IC50=4.82±1.01 μM); SK-BR-3 (IC50=5.63±1.05 μM); A431 (IC50=6.49±0.09 μM)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "GRFKRFRKKLKRLWHKVGPFVGPILHY", "db_claimed_peptide_name": "ChMAP-28"}, {"assertion_index": 2, "database": "dbAMP", "db_subject_text": "Micrococcus luteus B-1314 (MIC=0.25μM)\nMicrococcus luteus B-1314 (MIC=0.5μM)\nBacillus subtilis B-886 (MIC=0.25μM)\nBacillus subtilis B-886 (MIC=1μM)\nEnterococcus faecalis ATCC 29212 (MIC=4μM)\nEnterococcus faecalis ATCC 29212 (MIC=>8μM)\nStaphylococcus aureus ATCC 29213 (MIC=1μM)\nStaphylococcus aureus ATCC 29213 (MIC=2μM)\nStaphylococcus aureus 209P (MIC=0.06μM)\nStaphylococcus aureus 209P (MIC=0.5μM)\nEscherichia coli C600 (MIC=0.06μM)\nEscherichia coli C600 (MIC=0.125μM)\nEscherichia coli ML-35p (MIC=0.06μM)\nPseudomonas aeruginosa PAO1 (MIC=0.25μM)\nPseudomonas aeruginosa PAO1 (MIC=1μM)\nAcinetobacter baumannii 2675 (MIC=0.03μM)\nAcinetobacter baumannii 2675 (MIC=0.25μM)\nKlebsiella pneumoniae 287 (MIC=0.125μM)\nKlebsiella pneumoniae 287 (MIC=0.5μM)\nEnterobacter cloacae 4172 (MIC=0.125μM)\nEnterobacter cloacae 4172 (MIC=0.25μM)\nEscherichia coli 1057 (MIC=0.125μM)\nHuman promyelocytic leukemia HL-60 (IC50=3.39±0.15μM)\nHuman breast adenocarcinoma SK-BR-3 (IC50=5.63±1.05μM)\nHuman epidermoid carcinoma A431 (IC50=6.49±0.09μM)\nMouse skin melanoma B16-F10 (IC50=4.82±1.01μM)\nEscherichia coli BL21(DE3) (MIC=0.06μM)\nEscherichia coli 214 (MIC=0.06μM)", "db_measure": "AntiGram + AntiGram - MammalianCells Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "ChMAP-28, MAP28 Protein (102-128)"}]

Return ONLY the JSON array now (one object per assertion above).