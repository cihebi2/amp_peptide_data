
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
doi__10.1371_journal.pone.0047047

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Toxicity and minimum inhibitory concentrations (MIC) of Pa-MAP against mammalian cells, tumor cells, fungi (yeast and mycelium), Gram-positive and -negative bacteria and viruses.", "footnotes": ["Non-toxic concentration at 115 µM.", "Concentration used for ED50 = Effective Dose."], "header_rows": [["Organism", "MIC value (µM)"], ["Mammalian", ""], ["Erythrocytes", "nt*"], ["RAW 264.7", "nt*"], ["Vero Cells", "nt*"], ["Cancer Cells in Culture **", ""]], "longform_cells": [{"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "CaCo-2", "col_header": "MIC value (µM) / nt*", "value": "60"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "HCT-116", "col_header": "MIC value (µM) / nt*", "value": ">115"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "MCF-7", "col_header": "MIC value (µM) / nt*", "value": "115"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "T. mentagrophytes", "col_header": "MIC value (µM) / nt*", "value": "115"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "T. rubrum", "col_header": "MIC value (µM) / nt*", "value": "115"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "C. parapsilosis", "col_header": "MIC value (µM) / nt*", "value": ">115"}, {"table_index": 1, "row_index": 15, "col_index": 2, "row_label": "E. coli", "col_header": "MIC value (µM) / nt*", "value": "30"}, {"table_index": 1, "row_index": 16, "col_index": 2, "row_label": "S. aureus", "col_header": "MIC value (µM) / nt*", "value": ">115"}, {"table_index": 1, "row_index": 18, "col_index": 2, "row_label": "HSV-1", "col_header": "MIC value (µM) / nt*", "value": "90"}, {"table_index": 1, "row_index": 19, "col_index": 2, "row_label": "HSV-2", "col_header": "MIC value (µM) / nt*", "value": "90"}]}, {"table_index": 2, "label": "Table 2", "caption": "Secondary structure content of Pa-MAP using the method described by Morrisett and coworkers 1973.", "footnotes": [], "header_rows": [["Peptide", "[θ]222", "Environment", "Fraction helix (%)"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Pa-MAP", "col_header": "[θ]222", "value": "−21912.6"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Pa-MAP", "col_header": "Environment", "value": "SDS (7.0 mM)"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "Pa-MAP", "col_header": "Fraction helix (%)", "value": "60.9"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Pa-MAP", "col_header": "[θ]222", "value": "−22742.3"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Pa-MAP", "col_header": "Environment", "value": "SDS (28.0 mM)"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "Pa-MAP", "col_header": "Fraction helix (%)", "value": "63.2"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Pa-MAP", "col_header": "[θ]222", "value": "−20121.0"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Pa-MAP", "col_header": "Environment", "value": "TFE (50%)"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "Pa-MAP", "col_header": "Fraction helix (%)", "value": "55.9"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Vero cells", "db_measure": "-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human colon adenocarcinoma Caco-2", "db_measure": "ED50", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human breast adenocarcinoma MCF-7", "db_measure": "ED50", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Vero cells", "db_measure": "-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Human colon adenocarcinoma Caco-2", "db_measure": "ED50", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Human breast adenocarcinoma MCF-7", "db_measure": "ED50", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "CAMP", "db_subject_text": "Escherichia coli ATCC 8739[MIC = 30 microM], Staphylococcus aureus ATCC 25923[MIC >115 microM], Trichophyton mentagrophytes[MIC = 115 microM], Trichophyton rubrum[MIC = 115 microM], Candida parapsilosis ATCC 22019[MIC >115 microM], Human co", "db_measure": "Has anticancer activity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "dbAMP", "db_subject_text": "Escherichia coli ATCC 8739 (MIC=30μM)\nStaphylococcus aureus ATCC 25923 (MIC=>115μM)\nTrichophyton mentagrophytes (MIC=115μM)\nTrichophyton rubrum (MIC=115μM)\nCandida parapsilosis ATCC 22019 (MIC=>115μM)\nHuman colon adenocarcinoma Caco-2 (ED50", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).