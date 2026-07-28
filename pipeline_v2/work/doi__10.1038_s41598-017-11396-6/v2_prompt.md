
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
doi__10.1038_s41598-017-11396-6

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Characteristics of the selected peptides encoded by immunoglobulin genes.", "footnotes": ["a0: hydrophobic, *polar, +, and −: positively charged and negatively charged residues; pI: isoelectric point; M.M.: molecular mass (Daltons)."], "header_rows": [["Peptide", "Locus", "Gene", "Amino acid sequence", "Hydrophobicitya", "pI", "M.M.", "Net charge"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "L12P", "col_header": "Locus", "value": "Lambda"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "L12P", "col_header": "Gene", "value": "IGLJ1"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "L12P", "col_header": "Amino acid sequence", "value": "LCLRNWDQGHRP"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "L12P", "col_header": "Hydrophobicitya", "value": "0*0+*0-*0++0"}, {"table_index": 1, "row_index": 2, "col_index": 6, "row_label": "L12P", "col_header": "pI", "value": "8.26"}, {"table_index": 1, "row_index": 2, "col_index": 7, "row_label": "L12P", "col_header": "M.M.", "value": "1494.7"}, {"table_index": 1, "row_index": 2, "col_index": 8, "row_label": "L12P", "col_header": "Net charge", "value": "2+"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "W12K", "col_header": "Locus", "value": "Kappa"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "W12K", "col_header": "Gene", "value": "IGKJ1"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "W12K", "col_header": "Amino acid sequence", "value": "WTFGQGTKVEIK"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "W12K", "col_header": "Hydrophobicitya", "value": "0*00*0*+0-0+"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "W12K", "col_header": "pI", "value": "8.59"}, {"table_index": 1, "row_index": 3, "col_index": 7, "row_label": "W12K", "col_header": "M.M.", "value": "1393.7"}, {"table_index": 1, "row_index": 3, "col_index": 8, "row_label": "W12K", "col_header": "Net charge", "value": "+"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "G10S", "col_header": "Locus", "value": "Heavy"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "G10S", "col_header": "Gene", "value": "IGHD2-15"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "G10S", "col_header": "Amino acid sequence", "value": "GYCSGGSCYS"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "G10S", "col_header": "Hydrophobicitya", "value": "00**00**0*"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "G10S", "col_header": "pI", "value": "5.51"}, {"table_index": 1, "row_index": 4, "col_index": 7, "row_label": "G10S", "col_header": "M.M.", "value": "983.2"}, {"table_index": 1, "row_index": 4, "col_index": 8, "row_label": "G10S", "col_header": "Net charge", "value": "0"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "L18R", "col_header": "Locus", "value": "Heavy"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "L18R", "col_header": "Gene", "value": "IGHJ2"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "L18R", "col_header": "Amino acid sequence", "value": "LLVLRSLGPWHPGHCLLR"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "L18R", "col_header": "Hydrophobicitya", "value": "0000+*0000+00+*00+"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "L18R", "col_header": "pI", "value": "10.35"}, {"table_index": 1, "row_index": 5, "col_index": 7, "row_label": "L18R", "col_header": "M.M.", "value": "2068.1"}, {"table_index": 1, "row_index": 5, "col_index": 8, "row_label": "L18R", "col_header": "Net charge", "value": "4+"}]}, {"table_index": 2, "label": "Table 2", "caption": "In vitro fungicidal activity of the selected peptides L12P and L18R.", "footnotes": ["*EC50, half maximal effective concentration, calculated by nonlinear regression analysis using Graph Pad Prism 4.01 software."], "header_rows": [["Yeast strain", "EC50* (95% confidence intervals) [mol/liter] × 10−6", "EC50* (95% confidence intervals) [mol/liter] × 10−6"], ["L12P", "L18R"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Candida albicans SC5314", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L12P", "value": "0.489 (0.445–0.538)"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Candida albicans SC5314", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L18R", "value": "0.443 (0.437–0.549)"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "C. albicans CA-6", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L12P", "value": "0.556 (0.522–0.591)"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "C. albicans CA-6", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L18R", "value": "0.294 (0.292–0.296)"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "C. albicans SA40", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L12P", "value": "0.537 (0.531–0.544)"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "C. albicans SA40", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L18R", "value": "0.315 (0.271–0.366)"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "C. albicans AIDS68", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L12P", "value": "0.501 (0.468–0.537)"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "C. albicans AIDS68", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L18R", "value": "0.449 (0.435–0.463)"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "C. albicans UM4", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L12P", "value": "0.627 (0.534–0.736)"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "C. albicans UM4", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L18R", "value": "0.454 (0.414–0.499)"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "C. glabrata OMNI32", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L12P", "value": "0.546 (0.520–0.574)"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "C. glabrata OMNI32", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L18R", "value": "0.356 (0.339–0.373)"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "Cryptococcus neoformans 6995", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L12P", "value": "0.364 (0.353–0.375)"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "Cryptococcus neoformans 6995", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L18R", "value": "0.188 (0.180–0.196)"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "Malassezia furfur 101", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L12P", "value": "0.658 (0.574–0.754)"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "Malassezia furfur 101", "col_header": "EC50* (95% confidence intervals) [mol/liter] × 10−6 / L18R", "value": "0.527 (0.472–0.586)"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Malassezia furfur 101", "db_measure": "EC50", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "Candida albicans SC5314, C. albicans CA-6, C. albicans SA40, C. albicans AIDS68 0.501,C. albicans UM4, C. glabrata OMNI32, Cryptococcus neoformans 6995, Malassezia furfur 101, Herpes simplex virus 1, Coxsackievirus B5", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).