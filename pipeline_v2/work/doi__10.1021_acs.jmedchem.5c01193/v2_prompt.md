
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
doi__10.1021_acs.jmedchem.5c01193

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "1", "caption": "Minimum Inhibitory Concentration (MIC) of the Novltex Analogues (1–10) against MRSA along with Their Configuration", "footnotes": ["Indicates the presence of l-Ile8 for analogue 10."], "header_rows": [["", "analogues configuration", "analogues configuration", "analogues configuration", "analogues configuration", "analogues configuration", "analogues configuration", "analogues configuration", "analogues configuration", ""], ["synthesized Novltex analogues", "Phe1", "Leu2", "Lys3", "Ser4", "Thr5", "Ala6", "Leu7", "Leu8/Ile8", "MIC against MRSA ATCC 33591 (μg/mL)"], ["1", "L", "D", "D", "L", "L", "L", "D", "L", "8"], ["2", "L", "D", "D", "L", "D", "L", "D", "L", "32"], ["3", "D", "L", "L", "D", "D", "L", "L", "L", "32"], ["4", "L", "D", "D", "L", "D", "L", "L", "L", "2–4"], ["5", "D", "L", "D", "L", "D", "L", "L", "L", ">32"], ["6", "L", "D", "L", "D", "D", "L", "L", "L", ">32"], ["7", "D", "D", "L", "L", "D", "L", "L", "L", "32"], ["8", "L", "L", "L", "L", "D", "L", "L", "L", ">32"], ["9", "D", "D", "D", "D", "D", "L", "L", "L", "16"], ["10", "L", "D", "D", "L", "D", "L", "L", "L", "8"]], "longform_cells": [{"table_index": 1, "row_index": 13, "col_index": 10, "row_label": "vancomycin", "col_header": "MIC against MRSA ATCC 33591 (μg/mL) / 8 / 32 / 2–4 / >32 / 16", "value": "0.5–1"}]}, {"table_index": 2, "label": "2", "caption": "Minimum Inhibitory Concentration (MIC) Values of the Synthesized Novltex Analogues (11–16) against MRSA", "footnotes": ["All compounds have the same configuration based on analogue 4."], "header_rows": [["synthesized Novltex analogues", "name/composition", "MIC against MRSA ATCC 33591"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "11", "col_header": "name/composition", "value": "Leu2Chg–Novltex"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "11", "col_header": "MIC against MRSA ATCC 33591", "value": "8"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "12", "col_header": "name/composition", "value": "Leu2Cha–Novltex"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "12", "col_header": "MIC against MRSA ATCC 33591", "value": "0.25"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "13", "col_header": "name/composition", "value": "Leu2Trp–Novltex"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "13", "col_header": "MIC against MRSA ATCC 33591", "value": ">32"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "14", "col_header": "name/composition", "value": "Leu2Phe–Novltex"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "14", "col_header": "MIC against MRSA ATCC 33591", "value": "8"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "15", "col_header": "name/composition", "value": "Leu2Tyr–Novltex"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "15", "col_header": "MIC against MRSA ATCC 33591", "value": ">32"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "16", "col_header": "name/composition", "value": "Leu2 d-allo-Ile–Novltex"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "16", "col_header": "MIC against MRSA ATCC 33591", "value": "16"}]}, {"table_index": 3, "label": "3", "caption": "Antibacterial Activity of Novltex Analogue 12, Clovibactin, and Clinically Used Antibiotics against Multidrug-Resistant (MDR) S. aureus and E. faecium (Clinical Isolates)", "footnotes": ["The colors represent the MIC activity profile: 0.0625–1 μg/mL (potent activity, green), 2–4 μg/mL (moderate activity, yellow), and 8–>32 μg/mL (poor activity, red)."], "header_rows": [], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human dermal fibroblasts", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Novltex 12, Clovibactin [D-Cha2, D-Thr5]"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human embryonic kidney HEK293T cells", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Novltex 12, Clovibactin [D-Cha2, D-Thr5]"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Novltex 12, Clovibactin [D-Cha2, D-Thr5]"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "10-20% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Novltex 12, Clovibactin [D-Cha2, D-Thr5]"}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Novltex 12, Clovibactin [D-Cha2, D-Thr5]"}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Human dermal fibroblasts", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_24475"}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Human embryonic kidney HEK293T cells", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_24475"}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_24475"}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "10-20% Hemolysis", "db_value": "", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_24475"}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_24475"}]

Return ONLY the JSON array now (one object per assertion above).