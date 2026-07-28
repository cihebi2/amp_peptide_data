
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
doi__10.1371_journal.pone.0073136

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Structural statistics for the ensemble of OAIP-1 structures1.", "footnotes": ["All statistics are given as mean ±S.D.", "Only structurally relevant restraints, as defined by CYANA, are included.", "Two restraints were used per hydrogen bond.", "According to MolProbity (http://molprobity.biochem.duke.edu).", "Defined as the number of steric overlaps >0.4 Å per thousand atoms."], "header_rows": [["Experimental restraints2", ""], ["Interproton distance restraints", ""]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Intraresidue", "col_header": "", "value": "135"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Sequential", "col_header": "", "value": "202"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Medium range (i–j<5)", "col_header": "", "value": "103"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Long range (i–j≥5)", "col_header": "", "value": "173"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Hydrogen-bond restraints3", "col_header": "", "value": "10"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Disulfide-bond restraints", "col_header": "", "value": "9"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Dihedral-angle restraints (φ,Ψ, χ1)", "col_header": "", "value": "49"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Total number of restraints per residue", "col_header": "", "value": "20.0"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "Backbone atoms (residues 1–33)", "col_header": "", "value": "0.14±0.02"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "All heavy atoms (residues 1–33)", "col_header": "", "value": "0.62±0.07"}, {"table_index": 1, "row_index": 15, "col_index": 2, "row_label": "Residues in most favored Ramachandran region (%)", "col_header": "", "value": "93.4±0.7"}, {"table_index": 1, "row_index": 16, "col_index": 2, "row_label": "Ramachandran outliers (%)", "col_header": "", "value": "0±0"}, {"table_index": 1, "row_index": 17, "col_index": 2, "row_label": "Unfavorable sidechain rotamers (%)", "col_header": "", "value": "13.4±2.9"}, {"table_index": 1, "row_index": 18, "col_index": 2, "row_label": "Clashscore, all atoms5", "col_header": "", "value": "0.1±0.5"}, {"table_index": 1, "row_index": 19, "col_index": 2, "row_label": "Overall MolProbity score", "col_header": "", "value": "1.8±0.1"}]}, {"table_index": 2, "label": "Table 2", "caption": "Comparison of OAIP-1 with pyrethroid insecticides.", "footnotes": ["Pyrethroid-resistant strain BK99R9.", "Susceptible strain BK77."], "header_rows": [["Insecticide", "Class of insecticide", "Strain", "Oral LD50 (nmol/g)", "Reference"], ["Bifenthrin", "Pyrethroid", "R1", "20.6", "[61]"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "", "col_header": "Strain / R1", "value": "S2"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "", "col_header": "Oral LD50 (nmol/g) / 20.6", "value": "1.1"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Deltamethrin", "col_header": "Class of insecticide / Pyrethroid", "value": "Pyrethroid"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Deltamethrin", "col_header": "Strain / R1", "value": "R"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "Deltamethrin", "col_header": "Oral LD50 (nmol/g) / 20.6", "value": "0.46"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "Deltamethrin", "col_header": "Reference / [61]", "value": "[61]"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "", "col_header": "Strain / R1", "value": "S"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "", "col_header": "Oral LD50 (nmol/g) / 20.6", "value": "0.35"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Etofenprox", "col_header": "Class of insecticide / Pyrethroid", "value": "Pyrethroid"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "Etofenprox", "col_header": "Strain / R1", "value": "R"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "Etofenprox", "col_header": "Oral LD50 (nmol/g) / 20.6", "value": "55.9"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "Etofenprox", "col_header": "Reference / [61]", "value": "[61]"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "", "col_header": "Strain / R1", "value": "S"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "", "col_header": "Oral LD50 (nmol/g) / 20.6", "value": "0.31"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "Fenvalerate", "col_header": "Class of insecticide / Pyrethroid", "value": "Pyrethroid"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "Fenvalerate", "col_header": "Strain / R1", "value": "R"}, {"table_index": 2, "row_index": 8, "col_index": 4, "row_label": "Fenvalerate", "col_header": "Oral LD50 (nmol/g) / 20.6", "value": "41.9"}, {"table_index": 2, "row_index": 8, "col_index": 5, "row_label": "Fenvalerate", "col_header": "Reference / [61]", "value": "[61]"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "", "col_header": "Strain / R1", "value": "S"}, {"table_index": 2, "row_index": 9, "col_index": 4, "row_label": "", "col_header": "Oral LD50 (nmol/g) / 20.6", "value": "7.8"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "OAIP-1", "col_header": "Class of insecticide / Pyrethroid", "value": "Peptide"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "OAIP-1", "col_header": "Strain / R1", "value": "–"}, {"table_index": 2, "row_index": 10, "col_index": 4, "row_label": "OAIP-1", "col_header": "Oral LD50 (nmol/g) / 20.6", "value": "0.10"}, {"table_index": 2, "row_index": 10, "col_index": 5, "row_label": "OAIP-1", "col_header": "Reference / [61]", "value": "Current study"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "Helicoverpa armigera (LD50=104.2 +/- 0.6 pmol/g; database encoding mojibake normalized by source review)", "db_measure": "Function text includes probable ion-channel inhibitor, insecticidal activity, imidacloprid synergy, non-repellent/non-attractant behavior, and stability.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Helicoverpa armigera (LD50=104.2 +/- 0.6 pmol/g; database encoding mojibake normalized by source review)", "db_measure": "Function text includes probable ion-channel inhibitor, insecticidal activity, imidacloprid synergy, non-repellent/non-attractant behavior, and stability.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "dbAMP", "db_subject_text": "Helicoverpa armigera (LD50=104.2 +/- 0.6 pmol/g)", "db_measure": "AntiSARS_COV Insecticidal; assay_text=NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).