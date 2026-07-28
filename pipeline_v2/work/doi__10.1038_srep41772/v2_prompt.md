
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
doi__10.1038_srep41772

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Selected up-regulated genes of macrophages phagocytizing iRBC as determined by DNA microarray analysis and qRT-PCR.", "footnotes": ["aFold change indicates the mean expression level of the gene in macrophages co-cultured with iRBCs normalized to that in macrophages co-cultured with RBCs.", "bResults of qRT-PCR are from the same samples used for the microarray. Results represent the mean fold change ± SEM of three independent experiments.", "cResults of qRT-PCR are from pooled data of samples collected from three individual donors. Results represent the mean fold change ± SEM (n = 3)."], "header_rows": [["Gene", "Genbank Accession number", "Fold changeaa", "Fold changeaa", "Fold changeaa"], ["Microarray", "qRT-PCRb", "qRT-PCRc"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "SMTNL2", "col_header": "Genbank Accession number", "value": "NM_198501"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "SMTNL2", "col_header": "Fold changeaa", "value": "4.613"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "SMTNL2", "col_header": "Fold changeaa", "value": "7.20 ± 8.59"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "SMTNL2", "col_header": "Fold changeaa", "value": "14.57 ± 11.72"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "DEFB130", "col_header": "Genbank Accession number", "value": "NM_001037804"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "DEFB130", "col_header": "Fold changeaa", "value": "4.569"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "DEFB130", "col_header": "Fold changeaa", "value": "4.49 ± 3.93"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "DEFB130", "col_header": "Fold changeaa", "value": "3.45 ± 1.75"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "RIT2", "col_header": "Genbank Accession number", "value": "NM_002930"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "RIT2", "col_header": "Fold changeaa", "value": "4.543"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "RIT2", "col_header": "Fold changeaa", "value": "5.74 ± 2.53"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "RIT2", "col_header": "Fold changeaa", "value": "4.11 ± 6.60"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "SYTL4", "col_header": "Genbank Accession number", "value": "NM_080737"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "SYTL4", "col_header": "Fold changeaa", "value": "4.459"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "SYTL4", "col_header": "Fold changeaa", "value": "5.87 ± 3.77"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "SYTL4", "col_header": "Fold changeaa", "value": "6.20 ± 4.60"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "PRSS41", "col_header": "Genbank Accession number", "value": "NM_001135086"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "PRSS41", "col_header": "Fold changeaa", "value": "3.912"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "PRSS41", "col_header": "Fold changeaa", "value": "1.71 ± 0.85"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "PRSS41", "col_header": "Fold changeaa", "value": "3.44 ± 3.06"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "GRP", "col_header": "Genbank Accession number", "value": "NM_002091"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "GRP", "col_header": "Fold changeaa", "value": "2.726"}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "GRP", "col_header": "Fold changeaa", "value": "4.62 ± 4.95"}, {"table_index": 1, "row_index": 8, "col_index": 5, "row_label": "GRP", "col_header": "Fold changeaa", "value": "3.38 ± 1.80"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "ADAM19", "col_header": "Genbank Accession number", "value": "NM_033274"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "ADAM19", "col_header": "Fold changeaa", "value": "2.209"}, {"table_index": 1, "row_index": 9, "col_index": 4, "row_label": "ADAM19", "col_header": "Fold changeaa", "value": "1.54 ± 1.30"}, {"table_index": 1, "row_index": 9, "col_index": 5, "row_label": "ADAM19", "col_header": "Fold changeaa", "value": "1.72 ± 0.73"}]}, {"table_index": 2, "label": "Table 2", "caption": "Antimalarial activity of DEFB130.", "footnotes": ["The IC50 values of synthetic DEFB130, scrambled peptide, and N-terminal and C-terminal domain peptides against different strains of P. falciparum parasites in vitro."], "header_rows": [["", "Parasite strains (IC50 μM)", "Parasite strains (IC50 μM)", "Parasite strains (IC50 μM)"], ["3D7", "Dd2", "HB3"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "DEFB130", "col_header": "Parasite strains (IC50 μM) / 3D7", "value": "47.12 ± 2.22"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "DEFB130", "col_header": "Parasite strains (IC50 μM) / Dd2", "value": "43.53 ± 3.81"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "DEFB130", "col_header": "Parasite strains (IC50 μM) / HB3", "value": "49.22 ± 3.16"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "sDEFB130", "col_header": "Parasite strains (IC50 μM) / 3D7", "value": ">200"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "sDEFB130", "col_header": "Parasite strains (IC50 μM) / Dd2", "value": ">200"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "sDEFB130", "col_header": "Parasite strains (IC50 μM) / HB3", "value": ">200"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Nt-DEFB130", "col_header": "Parasite strains (IC50 μM) / 3D7", "value": "93.02 ± 0.88"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Nt-DEFB130", "col_header": "Parasite strains (IC50 μM) / Dd2", "value": "91.31 ± 2.09"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "Nt-DEFB130", "col_header": "Parasite strains (IC50 μM) / HB3", "value": "90.55 ± 1.63"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Ct-DEFB130", "col_header": "Parasite strains (IC50 μM) / 3D7", "value": ">200"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "Ct-DEFB130", "col_header": "Parasite strains (IC50 μM) / Dd2", "value": ">200"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "Ct-DEFB130", "col_header": "Parasite strains (IC50 μM) / HB3", "value": ">200"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "APD6 entry text for Human Beta-defensin 130", "db_measure": "mixed activity/mechanism/free-text annotation", "db_value": "P. falciparum IC50 range source-supported; later bacterial, antibiofilm, anti-inflammatory, yeast-expression and 2022-linked claims are not supported by this 2017 primary paper.", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Human Beta-defensin 130 (DEFB130, hBD130)"}]

Return ONLY the JSON array now (one object per assertion above).