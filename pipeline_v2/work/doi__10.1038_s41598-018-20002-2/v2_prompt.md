
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
doi__10.1038_s41598-018-20002-2

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Minimal inhibitory concentrations (MIC) of PAFB and PAF on fungi and bacteria.", "footnotes": ["§0.2 × Vogel’s medium.", "#Due to slow proliferation rate the MIC of T. rubrum was determined after 8 days of incubation."], "header_rows": [["Organisms", "MIC [µM]", "MIC [µM]"], ["PAFB", "PAF"], ["Filamentous fungi", "Filamentous fungi", "Filamentous fungi"]], "longform_cells": [{"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "A. fumigatus", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": "0.25"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "A. fumigatus", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": "1"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "A. niger", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": "0.50"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "A. niger", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": "0.25"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "A. terreus", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": "1"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "A. terreus", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": "32"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "N. crassa", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": "0.12/0.25§"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "N. crassa", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": "0.06/0.06§"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "P. chrysogenum", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": "0.50"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "P. chrysogenum", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": ">32"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "T. rubrum#", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": "0.5"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "T. rubrum#", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": "0.25"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Yeasts", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": "Yeasts"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "Yeasts", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": "Yeasts"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "C. albicans", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": "1"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "C. albicans", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": "4"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "S. cerevisiae", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": "1"}, {"table_index": 1, "row_index": 12, "col_index": 3, "row_label": "S. cerevisiae", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": "2"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "Bacteria", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": "Bacteria"}, {"table_index": 1, "row_index": 13, "col_index": 3, "row_label": "Bacteria", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": "Bacteria"}, {"table_index": 1, "row_index": 14, "col_index": 2, "row_label": "E. coli", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": ">32"}, {"table_index": 1, "row_index": 14, "col_index": 3, "row_label": "E. coli", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": ">32"}, {"table_index": 1, "row_index": 15, "col_index": 2, "row_label": "B. subtilis", "col_header": "MIC [µM] / PAFB / Filamentous fungi", "value": ">32"}, {"table_index": 1, "row_index": 15, "col_index": 3, "row_label": "B. subtilis", "col_header": "MIC [µM] / PAF / Filamentous fungi", "value": ">32"}]}, {"table_index": 2, "label": "Table 2", "caption": "The effect of the MIC of PAFB and PAF on the colony establishment of N. crassa.", "footnotes": ["aThe germination efficiency is indicated in (%) compared to the total conidial count used, which was set to be 100%. bThe values are given as mean ± SD (n = 3). Significant differences (p-values) between values were determined by comparison with the untreated control.*p ≤ 0.05, **p < 0.0001."], "header_rows": [["", "Germination efficiency [%]a,b", "Germ tube length [µm]b"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "control", "col_header": "Germination efficiency [%]a,b", "value": "83.30 ± 2.69"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "control", "col_header": "Germ tube length [µm]b", "value": "60.32 ± 10.04"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "PAFB", "col_header": "Germination efficiency [%]a,b", "value": "53.14 ± 5.70**"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "PAFB", "col_header": "Germ tube length [µm]b", "value": "17.99 ± 2.41**"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "PAF", "col_header": "Germination efficiency [%]a,b", "value": "85.56 ± 1.07"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "PAF", "col_header": "Germ tube length [µm]b", "value": "48.22 ± 7.34*"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Candida albicans CBS 5982", "db_measure": "", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Candida albicans CBS 5982", "db_measure": "", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "CAMP", "db_subject_text": "Aspergillus fumigatus ATCC 46645[MIC = 0.25 microM], Aspergillus niger CSB 12049[MIC = 0.5 microM], Aspergillus terreus T90[MIC = 1 microM], Neurospora crassa FGSC 4200[MIC = 0.12 microM], Penicillium chrysogenum ATCC 10002[MIC = 0.5 microM], Trichophyton rubrum ATCC 28188[MIC = 0.5 microM], Candida albicans CBS 5982[MIC = 1 microM], Candida albicans CBS 5982[80-90% Killing = 1 microM], Saccharomyces cerevisiae BY4741[MIC = 1 microM], Escherichia coli DH5alpha[MIC >32 microM], Bacillus subtilis ATCC 6633[MIC >32 microM], HCoV-229E[20-30% Inhibition = 8 microM]", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).