
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
doi__10.1128_aac.00424-24

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "TABLE 1", "caption": "Synergistic activity of LC-AMP-I1 with antibiotics", "footnotes": [], "header_rows": [["Bacterial strain", "Antibiotic", "FIC in combination with:", "FIC in combination with:"], ["LC-AMP-I1", "Melittin"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "E. coli", "col_header": "Antibiotic", "value": "Erythromycin"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "E. coli", "col_header": "FIC in combination with:", "value": "0.625"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "E. coli", "col_header": "FIC in combination with:", "value": "0.625"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Levofloxacin", "col_header": "Antibiotic", "value": "0.75"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Levofloxacin", "col_header": "FIC in combination with:", "value": "1.0625"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "S. aureus", "col_header": "Antibiotic", "value": "Erythromycin"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "S. aureus", "col_header": "FIC in combination with:", "value": "0.625"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "S. aureus", "col_header": "FIC in combination with:", "value": "1.125"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Levofloxacin", "col_header": "Antibiotic", "value": "0.3125"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Levofloxacin", "col_header": "FIC in combination with:", "value": "0.3125"}]}, {"table_index": 2, "label": "TABLE 2", "caption": "Biological activities of Lycosidae venom AMPsa", "footnotes": ["Biological activities of Lycosidae venom AMPs are indicated as follows: B, antibacterial; Bf, antibiofilm; F, antifungal; C, anticancer; P, antiparasitic; I, antiinflammatory; and n.d., no data available.", "Peptide that was identified in our previous or this study by our group."], "header_rows": [["Name", "Source", "Amino acid sequence", "Helical content (%)", "Activity", "Hemolysis (%) (concentration)", "References"], ["Lycocitin 1", "L. singoriensis", "GKLQAFLAKMKEIAAQTL-NH2", "100.00", "B, F", "n.d.", "(50)"], ["Lycocitin 2", "L. singoriensis", "GRLQAFLAKMKEIAAQTL-NH2", "100.00", "B, F", "n.d.", "(50)"], ["Lycosin-Ib", "L. singoriensis", "RKGWFKAMKSIAKFIAKEKLKEHL-NH2", "91.67", "B, F, Bf, C, P, I", "37.00 (200 µM or 577.34 µg/mL)", "(19–21, 51–53)"], ["Lycosin-IIb", "L. singoriensis", "VWLSALKFIGKHLAKHQLSKL-NH2", "95.24", "B, F, Bf, I", "20.00 (50 µM or 120.82 µg/mL)", "(54–56)"], ["LyeTx I", "Lycosa erythrognatha", "IWLTALKFLGKNLGKHLAKQQLAKL-NH2", "100.00", "B, F", "50.00 (130 µM or 368.12 µg/mL)", "(57)"], ["LVTX-8b", "L. vittata", "IWLTALKFLGKNLGKHLAKQQLSKL-NH2", "100.00", "C", "66.70 (5 μM or 14.24 µg/mL)", "(58, 59)"], ["LVTX-9b", "L. vittata", "ASIGALIQKAIALIKAKAA-NH2", "100.00", "C", "0.00 (200 µM or 370.03 µg/mL)", "(49)"], ["LS-AMP-E1b", "L. sinensis", "AGMKNIIDAIKKKLGGKL-NH2", "72.22", "B, Bf", "34.92 (200 µM or 379.43 µg/mL)", "(23)"], ["LS-AMP-F1b", "L. sinensis", "TGLGKIGYLMKKLLSKAKV-NH2", "89.47", "B, Bf", "17.00 (200 µM or 409.45 µg/mL)", "(23)"], ["XYP1b", "L. coelestis", "KIKWFKAMKSIAKFIAKDQLKKHL-NH2", "95.83", "P", "6.15 (160 µM or 463.96 µg/mL)", "(25)"], ["LC-AMP-F1b", "L. coelestis", "AGLGKIGALIQKVIAKYKA-NH2", "78.95", "B, Bf", "0.00 (160 µM or 310.79 µg/mL)", "(26)"], ["LC-AMP-I1b", "L. coelestis", "GRMQEFIKKLKAYLRKMKEKFSQIS-NH2", "96.00", "B, Bf, C", "10.13 (320 µM or 987.75 µg/mL)", "This work"], ["Lycotoxin I", "Hogna carolinensis", "IWLTALKFLGKHAAKHLAKQQLSKL-NH2", "100.00", "B, F", "55.00 (200 µM or 568.54 µg/mL)", "(60)"], ["Lycotoxin II", "Hogna carolinensis", "KIKWFKTMKSIAKFIAKEQMKKHLGGE-OH", "77.78", "B, F", "n.d.", "(60)"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Escherichia coli CCTCCC AB 2018675", "db_measure": "MBIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CMCC 26003", "db_measure": "MBIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Escherichia coli CCTCCC AB 2018675", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Escherichia coli CCTCCC AB 2018675", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CMCC 26003", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CMCC 26003", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "10-20% Cytotoxicity", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Human Nasopharyngeal carcinoma HONE-1", "db_measure": "10-20% Cytotoxicity", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Escherichia coli CCTCCC AB 2018675", "db_measure": "MBIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CMCC 26003", "db_measure": "MBIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "DBAASP", "db_subject_text": "Escherichia coli CCTCCC AB 2018675", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DBAASP", "db_subject_text": "Escherichia coli CCTCCC AB 2018675", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 12, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CMCC 26003", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 13, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CMCC 26003", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 14, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "10-20% Cytotoxicity", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 15, "database": "DBAASP", "db_subject_text": "Human Nasopharyngeal carcinoma HONE-1", "db_measure": "10-20% Cytotoxicity", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 16, "database": "APD6", "db_subject_text": "LC-AMP-I1, a novel venom-derived antimicrobial peptide from the wolf spider Lycosa coelestis.", "db_measure": "CD", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).