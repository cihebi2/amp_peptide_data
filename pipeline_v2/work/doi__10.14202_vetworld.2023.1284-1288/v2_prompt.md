
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
doi__10.14202_vetworld.2023.1284-1288

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table-1", "caption": "The MIC and MFC values of KW-23 and fluconazole against Candida albicans.", "footnotes": ["MIC=Minimum Inhibitory concentration,", "MFC=Minimum fungicidal concentration"], "header_rows": [["Anti-fungal agent", "Candida albicans (ATCC 10231) MIC*/MFC** (µg/mL)", "Candida albicans (ATCC MYA-574) MIC*/MFC** (µg/mL)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "KW-23", "col_header": "Candida albicans (ATCC 10231) MIC*/MFC** (µg/mL)", "value": "5/5"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "KW-23", "col_header": "Candida albicans (ATCC MYA-574) MIC*/MFC** (µg/mL)", "value": "15/15"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Fluconazole", "col_header": "Candida albicans (ATCC 10231) MIC*/MFC** (µg/mL)", "value": "14/65"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Fluconazole", "col_header": "Candida albicans (ATCC MYA-574) MIC*/MFC** (µg/mL)", "value": "MIC ≥64 µg/mL"}]}, {"table_index": 2, "label": "Table-2", "caption": "MIC and FIC index of KW-23 and fluconazole against standard and resistant strains of Candida albicans.", "footnotes": ["FIC=Fraction Inhibitory concentration, MIC=Minimum inhibitory concentrations"], "header_rows": [["Candida strain", "Fluconazole MIC (µg/mL)", "Fluconazole synergistic MIC (µg/mL)", "KW-23 MIC (µ g/mL)", "KW-23 synergistic MIC (µg/mL)", "FIC* index", "Action"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Candida albicans (ATCC 10231)", "col_header": "Fluconazole MIC (µg/mL)", "value": "14"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Candida albicans (ATCC 10231)", "col_header": "Fluconazole synergistic MIC (µg/mL)", "value": "5"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "Candida albicans (ATCC 10231)", "col_header": "KW-23 MIC (µ g/mL)", "value": "5"}, {"table_index": 2, "row_index": 2, "col_index": 5, "row_label": "Candida albicans (ATCC 10231)", "col_header": "KW-23 synergistic MIC (µg/mL)", "value": "0.025"}, {"table_index": 2, "row_index": 2, "col_index": 6, "row_label": "Candida albicans (ATCC 10231)", "col_header": "FIC* index", "value": "0.37"}, {"table_index": 2, "row_index": 2, "col_index": 7, "row_label": "Candida albicans (ATCC 10231)", "col_header": "Action", "value": "Synergistic"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Candida albicans (ATCC MYA-574)", "col_header": "Fluconazole MIC (µg/mL)", "value": "35"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Candida albicans (ATCC MYA-574)", "col_header": "Fluconazole synergistic MIC (µg/mL)", "value": "15"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "Candida albicans (ATCC MYA-574)", "col_header": "KW-23 MIC (µ g/mL)", "value": "15"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "Candida albicans (ATCC MYA-574)", "col_header": "KW-23 synergistic MIC (µg/mL)", "value": "2.5"}, {"table_index": 2, "row_index": 3, "col_index": 6, "row_label": "Candida albicans (ATCC MYA-574)", "col_header": "FIC* index", "value": "0.6"}, {"table_index": 2, "row_index": 3, "col_index": 7, "row_label": "Candida albicans (ATCC MYA-574)", "col_header": "Action", "value": "Additive"}]}, {"table_index": 3, "label": "Table-3", "caption": "The effect of different concentrations of KW-23 on human erythrocytes.", "footnotes": [], "header_rows": [["Concentration of KW-23 (µ M)", "Hemolysis (%)"]], "longform_cells": [{"table_index": 3, "row_index": 2, "col_index": 2, "row_label": "0", "col_header": "Hemolysis (%)", "value": "0"}, {"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "5", "col_header": "Hemolysis (%)", "value": "0"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "10", "col_header": "Hemolysis (%)", "value": "0"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "20", "col_header": "Hemolysis (%)", "value": "0"}, {"table_index": 3, "row_index": 6, "col_index": 2, "row_label": "40", "col_header": "Hemolysis (%)", "value": "0"}, {"table_index": 3, "row_index": 7, "col_index": 2, "row_label": "60", "col_header": "Hemolysis (%)", "value": "0"}, {"table_index": 3, "row_index": 8, "col_index": 2, "row_label": "80", "col_header": "Hemolysis (%)", "value": "1"}, {"table_index": 3, "row_index": 9, "col_index": 2, "row_label": "100", "col_header": "Hemolysis (%)", "value": "3"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Candida albicans ATCC MYA-573", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "KWKWKW", "db_claimed_peptide_name": "KW-23"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Candida albicans ATCC MYA-573", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "KWKWKW", "db_claimed_peptide_name": "KW-23"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Candida albicans ATCC MYA-573", "db_measure": "MBC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "KWKWKW", "db_claimed_peptide_name": "KW-23"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Candida albicans ATCC MYA-573", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "KWKWKW", "db_claimed_peptide_name": "KW-23"}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Candida albicans ATCC MYA-573", "db_measure": "MIC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "KWKWKW", "db_claimed_peptide_name": "KW-23"}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Candida albicans ATCC MYA-573", "db_measure": "MBC", "db_value": "", "db_unit": "µg/ml", "db_sequence": "KWKWKW", "db_claimed_peptide_name": "KW-23"}]

Return ONLY the JSON array now (one object per assertion above).