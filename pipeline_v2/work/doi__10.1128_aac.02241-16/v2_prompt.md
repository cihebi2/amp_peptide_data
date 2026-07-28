
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
doi__10.1128_aac.02241-16

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "TABLE 1", "caption": "Amino acid sequences, α-helical contents, and KD values of stapled peptides derived from subdomains 1, 2, and 3c", "footnotes": ["aThe N-terminal Glu residue is not present in the HR2 native sequence; Glu was added to each subdomain to stabilize the macrodipole of the α-helix.", "bThe shaded area highlights the overlapping regions of subdomains 2 and 3.", "8, R-octenyl-alanine; X, S-pentenylalanine; +, R-pentenylalanine; KD, equilibrium dissociation constant; NA, not applicable; ND, not determined."], "header_rows": [], "longform_cells": []}, {"table_index": 2, "label": "TABLE 2", "caption": "Design, alpha-helicity, and inhibitory activity of double-stapled peptides in Hep-2 cells", "footnotes": ["aThe EC50 inhibitory activity was assessed using an RSV-Cherry virus at an MOI of 0.2. The peptide and the virus were removed following the infection, and fresh peptide was immediately added to maintain the pressure of inhibition. Each experiment was performed at least twice in duplicate."], "header_rows": [], "longform_cells": []}, {"table_index": 3, "label": "TABLE 3", "caption": "Ala-scanning mutagenesis of double-stapled peptide 4 analogs", "footnotes": ["aThe shaded area shows the HR2 amino acid that makes hydrophobic contact with trimeric HR1.", "bThe numbers in bold refer to the mutant peptides that lose >10-fold inhibitory activity relative to their double-stapled peptide 4 analogs."], "header_rows": [], "longform_cells": []}, {"table_index": 4, "label": "TABLE 4", "caption": "Protease resistance of double-stapled peptides", "footnotes": ["ND, not determined."], "header_rows": [["Peptide", "Half-life (h)", "Half-life (h)"], ["Chymotrypsin", "Trypsin"]], "longform_cells": [{"table_index": 4, "row_index": 3, "col_index": 2, "row_label": "4", "col_header": "Half-life (h) / Chymotrypsin", "value": "0.08"}, {"table_index": 4, "row_index": 3, "col_index": 3, "row_label": "4", "col_header": "Half-life (h) / Trypsin", "value": "0.08"}, {"table_index": 4, "row_index": 4, "col_index": 2, "row_label": "4a", "col_header": "Half-life (h) / Chymotrypsin", "value": "74.7"}, {"table_index": 4, "row_index": 4, "col_index": 3, "row_label": "4a", "col_header": "Half-life (h) / Trypsin", "value": "1.3"}, {"table_index": 4, "row_index": 5, "col_index": 2, "row_label": "4bb", "col_header": "Half-life (h) / Chymotrypsin", "value": "50.1"}, {"table_index": 4, "row_index": 5, "col_index": 3, "row_label": "4bb", "col_header": "Half-life (h) / Trypsin", "value": "0.3"}, {"table_index": 4, "row_index": 6, "col_index": 2, "row_label": "4ca", "col_header": "Half-life (h) / Chymotrypsin", "value": "179.9"}, {"table_index": 4, "row_index": 6, "col_index": 3, "row_label": "4ca", "col_header": "Half-life (h) / Trypsin", "value": "38.0"}, {"table_index": 4, "row_index": 7, "col_index": 2, "row_label": "4ef", "col_header": "Half-life (h) / Chymotrypsin", "value": "NDa"}, {"table_index": 4, "row_index": 7, "col_index": 3, "row_label": "4ef", "col_header": "Half-life (h) / Trypsin", "value": "ND"}, {"table_index": 4, "row_index": 8, "col_index": 2, "row_label": "4bf", "col_header": "Half-life (h) / Chymotrypsin", "value": "ND"}, {"table_index": 4, "row_index": 8, "col_index": 3, "row_label": "4bf", "col_header": "Half-life (h) / Trypsin", "value": "ND"}, {"table_index": 4, "row_index": 9, "col_index": 2, "row_label": "T118", "col_header": "Half-life (h) / Chymotrypsin", "value": "ND"}, {"table_index": 4, "row_index": 9, "col_index": 3, "row_label": "T118", "col_header": "Half-life (h) / Trypsin", "value": "ND"}, {"table_index": 4, "row_index": 10, "col_index": 2, "row_label": "RSV-SAHBD (Z)", "col_header": "Half-life (h) / Chymotrypsin", "value": "7.4"}, {"table_index": 4, "row_index": 10, "col_index": 3, "row_label": "RSV-SAHBD (Z)", "col_header": "Half-life (h) / Trypsin", "value": "0.08"}, {"table_index": 4, "row_index": 11, "col_index": 2, "row_label": "RSV-SAHBD (E)", "col_header": "Half-life (h) / Chymotrypsin", "value": "6.5"}, {"table_index": 4, "row_index": 11, "col_index": 3, "row_label": "RSV-SAHBD (E)", "col_header": "Half-life (h) / Trypsin", "value": "0.02"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "10-20% Cytotoxicity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "RSV Fgp (497-515)[N4,A8,R11,E15 - S-ALA-4-pen]"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "40-50% Cytotoxicity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "RSV Fgp (497-515)[N4,A8,R11,E15 - S-ALA-4-pen]"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "0-10% Cytotoxicity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "RSV Fgp (497-515)[K2R-ALA-4-pen; Q5,A8,K12 -S-ALA-4-pen]"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "0-10% Cytotoxicity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "RSV Fgp (497-515)[K2R-ALA-4-pen; Q5,A8,K12 -S-ALA-4-pen]"}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Respiratory syncytial virus (RSV)", "db_measure": "IC50 I", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "RSV Fgp (488-522)"}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Respiratory syncytial virus (RSV)", "db_measure": "IC50 I", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "RSV Fgp (488-522)[A3,R20- R-ALA-7-oct;E10,H27- S-ALA-4-pen]"}, {"assertion_index": 6, "database": "DRAMP", "db_subject_text": "[Ref.28137809]Respiratory syncytial virus (RSV):inhibition of virus infection in Hep-2 cells(EC50>50 µM).", "db_measure": "[Ref.28137809]Respiratory syncytial virus (RSV):inhibition of virus infection in Hep-2 cells(EC50>50 µM).", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "peptide 4(RSV fusion protein(497-515))"}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "10-20% Cytotoxicity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_15680"}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "40-50% Cytotoxicity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_15680"}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "0-10% Cytotoxicity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_15681"}, {"assertion_index": 10, "database": "DBAASP", "db_subject_text": "Human hepatocellular carcinoma HepG2", "db_measure": "0-10% Cytotoxicity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_15681"}, {"assertion_index": 11, "database": "DBAASP", "db_subject_text": "Respiratory syncytial virus (RSV)", "db_measure": "IC50 I", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_15703"}, {"assertion_index": 12, "database": "DRAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DRAMP30491"}, {"assertion_index": 13, "database": "DBAASP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_15703"}]

Return ONLY the JSON array now (one object per assertion above).