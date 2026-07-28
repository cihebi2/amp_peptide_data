
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
doi__10.1371_journal.pone.0138911

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Sequences and biophysical data of peptides used in the study.", "footnotes": ["a t R (min) denotes the retention time at 25°C by reversed-phase HPLC."], "header_rows": [["Peptide", "Amino acid sequence", "Mw", "t R (min) a"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "TAT", "col_header": "Amino acid sequence", "value": "Ac-RKKRRQRRR-amide"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "TAT", "col_header": "Mw", "value": "1380.66"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "TAT", "col_header": "t R (min) a", "value": "13"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "HPRP-A1", "col_header": "Amino acid sequence", "value": "Ac-FKKLKKLFSKLWNWK-amide"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "HPRP-A1", "col_header": "Mw", "value": "2035.53"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "HPRP-A1", "col_header": "t R (min) a", "value": "41"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "HPRP-A1-TAT", "col_header": "Amino acid sequence", "value": "Ac-FKKLKKLFSKLWNWKRKKRRQRRR-amide"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "HPRP-A1-TAT", "col_header": "Mw", "value": "3357.13"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "HPRP-A1-TAT", "col_header": "t R (min) a", "value": "31.5"}]}, {"table_index": 2, "label": "Table 2", "caption": "Anticancer (IC50) and hemolytic activities (MHC) of peptides against cancer cells and human red blood cells.", "footnotes": ["aAnticancer activity (IC50) represents the concentration of peptides at which cell viability was inhibited by 50% in comparison with the untreated cells. The MTT assay was repeated in triplicate, and IC50 value was determined by averaging three repeated experiments.", "bGM of the anticancer activity (IC50) for the four cancer cell lines.", "cHemolytic activity (MHC) was determined using human red blood cells after incubation with peptides for 1 h. If no hemolytic activity was observed at 500 μM, a value of 1000 μM was used for calculating the therapeutic index.", "dTherapeutic index = MHC/IC50. Larger values indicate greater anticancer specificity.", "GM, geometric mean; MHC, minimal hemolytic concentration."], "header_rows": [["Peptide", "IC50 a (μM)", "MHC c (μM)", "Therapeutic index d"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "", "col_header": "Peptide", "value": "24 h"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "", "col_header": "IC50 a (μM)", "value": "1 h"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "", "col_header": "IC50 a (μM)", "value": "B16"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "", "col_header": "MHC c (μM)", "value": "SGC-7901"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "", "col_header": "Therapeutic index d", "value": "HepG2"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "", "col_header": "col4", "value": "HeLa"}, {"table_index": 2, "row_index": 3, "col_index": 6, "row_label": "", "col_header": "col5", "value": "GM b"}, {"table_index": 2, "row_index": 3, "col_index": 7, "row_label": "", "col_header": "col6", "value": "HeLa"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "HPRP-A1", "col_header": "IC50 a (μM)", "value": "6.1 ±0.02"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "HPRP-A1", "col_header": "MHC c (μM)", "value": "5.2 ±0.14"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "HPRP-A1", "col_header": "Therapeutic index d", "value": "7.7 ±0.23"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "HPRP-A1", "col_header": "col4", "value": "3.5 ±0.03"}, {"table_index": 2, "row_index": 4, "col_index": 6, "row_label": "HPRP-A1", "col_header": "col5", "value": "5.6"}, {"table_index": 2, "row_index": 4, "col_index": 7, "row_label": "HPRP-A1", "col_header": "col6", "value": "7.4 ± 0.12"}, {"table_index": 2, "row_index": 4, "col_index": 8, "row_label": "HPRP-A1", "col_header": "col7", "value": "64 ±6.80"}, {"table_index": 2, "row_index": 4, "col_index": 9, "row_label": "HPRP-A1", "col_header": "col8", "value": "8.6"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "HPRP-A1-TAT", "col_header": "IC50 a (μM)", "value": "3.9 ±0.02"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "HPRP-A1-TAT", "col_header": "MHC c (μM)", "value": "4.8 ±0.08"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "HPRP-A1-TAT", "col_header": "Therapeutic index d", "value": "5.8 ±0.36"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "HPRP-A1-TAT", "col_header": "col4", "value": "1.8 ±0.02"}, {"table_index": 2, "row_index": 5, "col_index": 6, "row_label": "HPRP-A1-TAT", "col_header": "col5", "value": "4.1"}, {"table_index": 2, "row_index": 5, "col_index": 7, "row_label": "HPRP-A1-TAT", "col_header": "col6", "value": "3.9 ± 0.07"}, {"table_index": 2, "row_index": 5, "col_index": 8, "row_label": "HPRP-A1-TAT", "col_header": "col7", "value": ">500"}, {"table_index": 2, "row_index": 5, "col_index": 9, "row_label": "HPRP-A1-TAT", "col_header": "col8", "value": "256"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "5% Hemolysis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "5% Hemolysis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "5% Hemolysis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "5% Hemolysis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DRAMP", "db_subject_text": "Tumor-cell activity text plus human RBC MHC", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DRAMP", "db_subject_text": "Tumor-cell activity text plus human RBC MHC", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DRAMP", "db_subject_text": "Tumor-cell activity plus human RBC MHC", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DRAMP", "db_subject_text": "Tumor-cell activity plus human RBC MHC", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now.