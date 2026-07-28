
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
doi__10.3390_ph16101356

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Amino acid sequences and physicochemical properties of BMAP-18 and BMAP-18-FL.", "footnotes": ["a Retention time (tR) was measured by analytical RP-HPLC with C18 column, b Molecular masses were determined by electrospray ionization mass spectrometry (ESI-MS). Z: ion charge, m/z: mass-to-charge ratio, c Hydrophobic moment (μH) was calculated online at: http://heliquest.ipmc.cnrs.fr/cgi-bin/ComputParams.py (accessed on 17 July 2023)."], "header_rows": [["Peptides", "Amino Acid Sequence", "tR(min) a", "MolecularMass(g/mol)", "MS Analysis b", "MS Analysis b", "MS Analysis b", "Net Charge", "HydrophobicMoment (µH) c"], ["Z", "m/zCalculated", "m/zFound"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "BMAP-18", "col_header": "Amino Acid Sequence", "value": "GRFKRFRKKFKKLFKKLS"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "BMAP-18", "col_header": "tR(min) a", "value": "18.1"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "BMAP-18", "col_header": "MolecularMass(g/mol)", "value": "2342.92"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "BMAP-18", "col_header": "MS Analysis b", "value": "[M + 4H]4+"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "BMAP-18", "col_header": "MS Analysis b", "value": "585.73"}, {"table_index": 1, "row_index": 3, "col_index": 7, "row_label": "BMAP-18", "col_header": "MS Analysis b", "value": "586.45"}, {"table_index": 1, "row_index": 3, "col_index": 8, "row_label": "BMAP-18", "col_header": "Net Charge", "value": "+10"}, {"table_index": 1, "row_index": 3, "col_index": 9, "row_label": "BMAP-18", "col_header": "HydrophobicMoment (µH) c", "value": "0.710"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "BMAP-18-FL", "col_header": "Amino Acid Sequence", "value": "GRLKRLRKKLKKLLKKLS"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "BMAP-18-FL", "col_header": "tR(min) a", "value": "20.2"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "BMAP-18-FL", "col_header": "MolecularMass(g/mol)", "value": "2206.85"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "BMAP-18-FL", "col_header": "MS Analysis b", "value": "[M + 4H]4+"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "BMAP-18-FL", "col_header": "MS Analysis b", "value": "551.71"}, {"table_index": 1, "row_index": 4, "col_index": 7, "row_label": "BMAP-18-FL", "col_header": "MS Analysis b", "value": "552.40"}, {"table_index": 1, "row_index": 4, "col_index": 8, "row_label": "BMAP-18-FL", "col_header": "Net Charge", "value": "+10"}, {"table_index": 1, "row_index": 4, "col_index": 9, "row_label": "BMAP-18-FL", "col_header": "HydrophobicMoment (µH) c", "value": "0.693"}]}, {"table_index": 2, "label": "Table 2", "caption": "Minimum inhibitory concentration (MIC: µM) * of BMAP-18 peptides and common antibiotics against resistant strains.", "footnotes": ["* Minimum inhibitory concentrations (MICs) were determined as the lowest concentration of the antimicrobial agent that inhibited bacterial growth."], "header_rows": [["", "Minimum Inhibitory Concentrations (MICs:µM) *", "Minimum Inhibitory Concentrations (MICs:µM) *", "Minimum Inhibitory Concentrations (MICs:µM) *", "Minimum Inhibitory Concentrations (MICs:µM) *", "Minimum Inhibitory Concentrations (MICs:µM) *", "Minimum Inhibitory Concentrations (MICs:µM) *"], ["Strains", "Ciprofloxacin", "Oxacillin", "Tetracycline", "BMAP-18", "BMAP-18FL", "Melittin"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "MRSA (CCARM 3090)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / Ciprofloxacin", "value": ">1024"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "MRSA (CCARM 3090)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / Oxacillin", "value": ">1024"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "MRSA (CCARM 3090)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / Tetracycline", "value": ">1024"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "MRSA (CCARM 3090)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / BMAP-18", "value": "16"}, {"table_index": 2, "row_index": 3, "col_index": 6, "row_label": "MRSA (CCARM 3090)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / BMAP-18FL", "value": "16"}, {"table_index": 2, "row_index": 3, "col_index": 7, "row_label": "MRSA (CCARM 3090)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / Melittin", "value": "4"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "MDRPA (CCARM 2095)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / Ciprofloxacin", "value": ">1024"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "MDRPA (CCARM 2095)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / Oxacillin", "value": ">1024"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "MDRPA (CCARM 2095)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / Tetracycline", "value": ">1024"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "MDRPA (CCARM 2095)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / BMAP-18", "value": "32"}, {"table_index": 2, "row_index": 4, "col_index": 6, "row_label": "MDRPA (CCARM 2095)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / BMAP-18FL", "value": "32"}, {"table_index": 2, "row_index": 4, "col_index": 7, "row_label": "MDRPA (CCARM 2095)", "col_header": "Minimum Inhibitory Concentrations (MICs:µM) * / Melittin", "value": "8"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Pseudomonas aeruginosa CCARM 2095", "db_measure": "MBIC90", "db_value": "", "db_unit": "µM", "db_sequence": "GRFKRFRKKFKKLFKKLS", "db_claimed_peptide_name": "BMAP-18"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Murine macrophage cells RAW 264.7", "db_measure": "96% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "GRFKRFRKKFKKLFKKLS", "db_claimed_peptide_name": "BMAP-18"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Murine macrophage cells RAW 264.7", "db_measure": "92% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "GRLKRLRKKLKKLLKKLS", "db_claimed_peptide_name": "BMAP-18-FL"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Pseudomonas aeruginosa CCARM 2095", "db_measure": "MBIC90", "db_value": "", "db_unit": "µM", "db_sequence": "GRFKRFRKKFKKLFKKLS", "db_claimed_peptide_name": "BMAP-18"}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Murine macrophage cells RAW 264.7", "db_measure": "96% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "GRFKRFRKKFKKLFKKLS", "db_claimed_peptide_name": "BMAP-18"}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Murine macrophage cells RAW 264.7", "db_measure": "92% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "GRLKRLRKKLKKLLKKLS", "db_claimed_peptide_name": "BMAP-18-FL"}, {"assertion_index": 6, "database": "APD6", "db_subject_text": "Multifunctional Properties of BMAP-18 and Its Aliphatic Analog against Drug-Resistant Bacteria", "db_measure": "APD6 peptide summary narrative", "db_value": "", "db_unit": "", "db_sequence": "GRLKRLRKKLKKLLKKLS", "db_claimed_peptide_name": "BMAP-18-FL"}]

Return ONLY the JSON array now (one object per assertion above).