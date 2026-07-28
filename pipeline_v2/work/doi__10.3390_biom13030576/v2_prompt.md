
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
doi__10.3390_biom13030576

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Physicochemical properties of Raniseptins-3 and -6.", "footnotes": [], "header_rows": [["Peptide", "Mass calc.(Da)", "Mass obs.(Da)", "Net Charge", "HydrophobicFace", "Hydrophobicity <H>", "GRAVY"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Raniseptin-3", "col_header": "Mass calc.(Da)", "value": "2958.77"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Raniseptin-3", "col_header": "Mass obs.(Da)", "value": "2958.7"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "Raniseptin-3", "col_header": "Net Charge", "value": "+4"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "Raniseptin-3", "col_header": "HydrophobicFace", "value": "VIPWVVLLA"}, {"table_index": 1, "row_index": 2, "col_index": 6, "row_label": "Raniseptin-3", "col_header": "Hydrophobicity <H>", "value": "43.77"}, {"table_index": 1, "row_index": 2, "col_index": 7, "row_label": "Raniseptin-3", "col_header": "GRAVY", "value": "0.300"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Raniseptin-6", "col_header": "Mass calc.(Da)", "value": "3119.85"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Raniseptin-6", "col_header": "Mass obs.(Da)", "value": "3119.5"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Raniseptin-6", "col_header": "Net Charge", "value": "+4"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "Raniseptin-6", "col_header": "HydrophobicFace", "value": "VLPLVVLYA"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "Raniseptin-6", "col_header": "Hydrophobicity <H>", "value": "43.60"}, {"table_index": 1, "row_index": 3, "col_index": 7, "row_label": "Raniseptin-6", "col_header": "GRAVY", "value": "0.169"}]}, {"table_index": 2, "label": "Table 2", "caption": "Antimicrobial activities of Raniseptins-3 and -6 (MIC in μM).", "footnotes": [], "header_rows": [["Microorganisms", "Rsp-3", "Rsp-6"], ["Gram-negative bacteria", "", ""]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "E. coli (ATCC 25922)", "col_header": "Rsp-3", "value": "2"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "E. coli (ATCC 25922)", "col_header": "Rsp-6", "value": "2"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "K. pneumoniae (ATCC 13883)", "col_header": "Rsp-3", "value": "1"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "K. pneumoniae (ATCC 13883)", "col_header": "Rsp-6", "value": "1"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "K. pneumoniae carbapanemase (KPC CAPB053)", "col_header": "Rsp-3", "value": "4"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "K. pneumoniae carbapanemase (KPC CAPB053)", "col_header": "Rsp-6", "value": "4"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "S. aureus (ATCC 25923)", "col_header": "Rsp-3", "value": "4"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "S. aureus (ATCC 25923)", "col_header": "Rsp-6", "value": "32"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "S. epidermidis (ATCC 12228)", "col_header": "Rsp-3", "value": "8"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "S. epidermidis (ATCC 12228)", "col_header": "Rsp-6", "value": "8"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "C. albicans (ATCC 14053)", "col_header": "Rsp-3", "value": ">128"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "C. albicans (ATCC 14053)", "col_header": "Rsp-6", "value": ">128"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "18% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "18% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "18% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "18% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "APD6", "db_subject_text": "Purification and Biological Properties of Raniseptins-3 and -6, Two Antimicrobial Peptides from Boana raniceps (Cope, 1862) Skin Secretion", "db_measure": "Discovery: The same sequence was initially reported in a different frog without activty data (see AP2384). In the current study, the peptide is isolated, sequenced and charaterized. Sequence analysis: APD analysis reveals this sequence is most similar (89.66%) to Raniseptin 1 L: 21%; V: 17%; K: 14%; G: 10%. GRAVY: 0.168; M Wt: 3121.752; Mol formula: C142H248N38O38; molar extinction coeff: 1490. Activity: Gram- E. coli ATCC 25922 (MIC 2 uM), K. pneumoniae ATCC 13883 (MIC 1 uM), K. pneumoniae ATCC 13883 (MIC 4 uM), Gram+ S. aureus ATCC 25923 (MIC 32 uM), S. epidermidis ATCC 12228 (MIC 8 uM), and yeast C.albicans ATCC 14053 (MIC > 128 uM). In vitro Toxicity: human RBC, low hemo.lytic (20% heolysis at 128 uM; HC50 >128 uM). Toxic to murine skin melanoma B16F10 cells (IC50 8.69 uM) and NIH3T3 mouse fibroblasts cells (IC50 5.94 uM). Structure: random coil in water and helical in 35 mM SDS. Found in multiple species.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "APD6", "db_subject_text": "Purification and Biological Properties of Raniseptins-3 and -6, Two Antimicrobial Peptides from Boana raniceps (Cope, 1862) Skin Secretion", "db_measure": "Discovery: The same sequence was initially reported in a different frog without activty data (see AP2384). In the current study, the peptide is isolated, sequenced and charaterized. Sequence analysis: APD analysis reveals this sequence is most similar (82.76%) to Raniseptin 1 V=L: 14%; K: 18%; G: 11%. GRAVY: 0.3; M Wt: 2960.586; Mol formula: C137H238N35O35; molar extinction coeff: 5550. Activity: Gram- E. coli ATCC 25922 (MIC 2 uM), K. pneumoniae ATCC 13883 (MIC 1 uM), K. pneumoniae ATCC 13883 (MIC 4 uM), Gram+ S. aureus ATCC 25923 (MIC 4 uM), S. epidermidis ATCC 12228 (MIC 8 uM), and yeast C.albicans ATCC 14053 (MIC > 128 uM). In vitro Toxicity: human RBC, low hemo.lytic (20% heolysis at 128 uM; HC50 >128 uM). Toxic to murine skin melanoma B16F10 cells (IC50 6.56 uM) and NIH3T3 mouse fibroblasts cells (IC50 4.21 uM). Structure: random coil in water and helical in 35 mM SDS. Found in multiple species.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).