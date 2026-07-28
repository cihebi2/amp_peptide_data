
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
doi__10.3390_molecules24112077

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Sarconesin II’s antibacterial activity spectrum.", "footnotes": ["1 MIC, minimum inhibitory concentration; The MIC refers to the minimal peptide concentration without visible bacterial growth in a liquid medium."], "header_rows": [["Microorganism", "MIC (µM) 1"], ["Gram-negative bacteria", ""]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Escherichia coli K12 MG1655", "col_header": "MIC (µM) 1", "value": "7.8"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Escherichia coli DH5α", "col_header": "MIC (µM) 1", "value": "3.9"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Pseudomonas aeruginosa PA14", "col_header": "MIC (µM) 1", "value": "15.6"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Pseudomonas aeruginosa ATCC 27853", "col_header": "MIC (µM) 1", "value": "7.8"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Staphylococcus aureus ATCC 29213", "col_header": "MIC (µM) 1", "value": "3.9"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Micrococcus luteus A270", "col_header": "MIC (µM) 1", "value": "1.9"}]}, {"table_index": 2, "label": "Table 2", "caption": "Sarconesin II’s theoretical physicochemical properties.", "footnotes": ["The ProtParam tool in ExPASy was used to obtain physicochemical parameters [41]."], "header_rows": [["Peptide Properties", "Peptide Properties"], ["Sequence", "VALTGLTVAEYFR"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Length", "col_header": "Peptide Properties / VALTGLTVAEYFR", "value": "13"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Molecular weight", "col_header": "Peptide Properties / VALTGLTVAEYFR", "value": "1439.67"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Formula", "col_header": "Peptide Properties / VALTGLTVAEYFR", "value": "C67H106N16O19"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Theoretical isoelectric point (pI)", "col_header": "Peptide Properties / VALTGLTVAEYFR", "value": "5.97"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "Net charge", "col_header": "Peptide Properties / VALTGLTVAEYFR", "value": "0"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "Molar extinction coefficient (ε)", "col_header": "Peptide Properties / VALTGLTVAEYFR", "value": "1490 M-1 cm-1"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "Instability index", "col_header": "Peptide Properties / VALTGLTVAEYFR", "value": "2.70"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "Aliphatic index", "col_header": "Peptide Properties / VALTGLTVAEYFR", "value": "120.00"}, {"table_index": 2, "row_index": 11, "col_index": 2, "row_label": "Grand average of hydropathicity (GRAVY)", "col_header": "Peptide Properties / VALTGLTVAEYFR", "value": "0.869"}]}, {"table_index": 3, "label": "Table 3", "caption": "Known antimicrobial peptides having similarity with sarconesin II, as identified in the Antimicrobial Peptide Database (APD2) (Wang et al., 2009).", "footnotes": ["The Antimicrobial Peptide Database (APD) prediction tool was used to align sarconesin II [45]."], "header_rows": [["Peptide Name", "Sequence Alignment", "Source Organism", "APD Identifier", "Percentage Similarity"], ["Temporin-HN1 (14 aa)", "+ A I L T T L A N W A R K F L V A + L T G L + T V A E Y F R", "Frog Odorrana hainanensis [46]", "AP01959", "40%"], ["H4-(86-100) (15 aa)", "V V Y A L K R N G R T + + L Y G F + + V + A L + + T G L T V A E Y + F R", "Rat [47]", "AP02806", "38.8%"], ["CcAMP1 (17 aa)", "M W I T N G + G V A N W Y F V L A R V A L T + G L T V A + E Y F + + + R", "Stink bug Coridius chinensis [48]", "AP02595", "38.88%"], ["Plantaricin DL3 (20 aa)", "V G P G A I N A G + T Y L V S R E L F E R V + + + A + L T G L T + + V + A E Y F + R", "Probiotic Lactobacillus plantarum DL3 [49]", "AP02979", "38.09%"], ["VmCT1 (13 aa)", "+ F L + G A L W N V A K S V F + V A L T G + L + T V A + E Y F R", "Scorpion Vaejovis mexicanus smithi [50]", "AP02216", "37.5%"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "0-10% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "Sarconesin II"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Escherichia coli DH5alpha", "db_measure": "MBC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "Sarconesin II"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "0-10% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "Sarconesin II, a New Antimicrobial Peptide Isolated from Sarconesiopsis magellanica Excretions and Secretions."}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Escherichia coli DH5alpha", "db_measure": "MBC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "Sarconesin II, a New Antimicrobial Peptide Isolated from Sarconesiopsis magellanica Excretions and Secretions."}]

Return ONLY the JSON array now (one object per assertion above).