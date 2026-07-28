
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
doi__10.1021_acs.jmedchem.8b00890

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Inhibitory Activities of Lipopeptides on MERS-CoV S Protein-Mediated Cell–Cell Fusiona", "footnotes": ["The number of 293T/MERS/EGFP cells fused or unfused with Huh-7 cells were countered, and the percentage of inhibition was calculated as described in the experimental section. Data were derived from the results of three independent experiments and are expressed as the mean ± standard deviation.", "These peptides have an acetyl group at the N-terminus and carboxyamide at the C-terminus. The letters a-g indicate the positions of the corresponding residues in a helical wheel presentation. βA, β-alanine.", "Cytotoxicity to Huh-7 cells."], "header_rows": [], "longform_cells": []}, {"table_index": 2, "label": "Table 2", "caption": "Inhibitory Activities of Lipopeptides against Influenza A Virus Strains Infection in Cell Culturea", "footnotes": ["Data were derived from the results of three independent experiments and are expressed as the mean ± standard deviation.", "The cytotoxicity of compounds on MDCK cells."], "header_rows": [["", "EC50 (μM) for inhibiting", "EC50 (μM) for inhibiting", ""], ["compd", "A/Puerto Rico/8/34 (H1N1)", "A/Hong Kong/8/68 (H3N2)", "CC50 (μM)b"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "IIS", "col_header": "EC50 (μM) for inhibiting / A/Puerto Rico/8/34 (H1N1)", "value": "1.96 ± 0.28"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "IIS", "col_header": "EC50 (μM) for inhibiting / A/Hong Kong/8/68 (H3N2)", "value": "6.38 ± 1.06"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "IIS", "col_header": "CC50 (μM)b", "value": ">100"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "IIY", "col_header": "EC50 (μM) for inhibiting / A/Puerto Rico/8/34 (H1N1)", "value": "3.15 ± 1.79"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "IIY", "col_header": "EC50 (μM) for inhibiting / A/Hong Kong/8/68 (H3N2)", "value": "12.9 ± 5.55"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "IIY", "col_header": "CC50 (μM)b", "value": ">100"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "IIQ", "col_header": "EC50 (μM) for inhibiting / A/Puerto Rico/8/34 (H1N1)", "value": "1.73 ± 0.81"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "IIQ", "col_header": "EC50 (μM) for inhibiting / A/Hong Kong/8/68 (H3N2)", "value": "0.70 ± 0.09"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "IIQ", "col_header": "CC50 (μM)b", "value": ">100"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "oseltamivir", "col_header": "EC50 (μM) for inhibiting / A/Puerto Rico/8/34 (H1N1)", "value": "1.48 ± 0.05"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "oseltamivir", "col_header": "EC50 (μM) for inhibiting / A/Hong Kong/8/68 (H3N2)", "value": "0.01 ± 0.004"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "oseltamivir", "col_header": "CC50 (μM)b", "value": ">100"}]}, {"table_index": 3, "label": "Table 3", "caption": "Pharmacokinetic Parameters of IIQ in Rats Following a Single Dose iv Administration Calculated by Noncompartmental Analysis by Using DAS, Version 3.2.8a", "footnotes": ["MRT, mean residence time; CL, clearance; Vd, volume of distribution."], "header_rows": [["compd", "AUC (0–t) ((μg/mL)·h)", "MRT (0–t) (h)", "t1/2 (h)", "CL ((mL/h)/kg)", "Cmax (μg/mL)", "Vd (mL/kg)"]], "longform_cells": [{"table_index": 3, "row_index": 2, "col_index": 2, "row_label": "IIQ", "col_header": "AUC (0–t) ((μg/mL)·h)", "value": "234.7 ± 7.8"}, {"table_index": 3, "row_index": 2, "col_index": 3, "row_label": "IIQ", "col_header": "MRT (0–t) (h)", "value": "4.1 ± 0.1"}, {"table_index": 3, "row_index": 2, "col_index": 4, "row_label": "IIQ", "col_header": "t1/2 (h)", "value": "6.6 ± 0.2"}, {"table_index": 3, "row_index": 2, "col_index": 5, "row_label": "IIQ", "col_header": "CL ((mL/h)/kg)", "value": "20.7 ± 0.6"}, {"table_index": 3, "row_index": 2, "col_index": 6, "row_label": "IIQ", "col_header": "Cmax (μg/mL)", "value": "97.6 ± 8.4"}, {"table_index": 3, "row_index": 2, "col_index": 7, "row_label": "IIQ", "col_header": "Vd (mL/kg)", "value": "197.8 ± 9.3"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "CAMP", "db_subject_text": "MERS-CoV[IC50 F = 2.93+-0.95 microM], Human hepatocellular carcinoma Huh7[50-60% Cytotoxicity >100 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "IIE"}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "MERS-CoV PsV[IC50 >40 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "IIQΔ"}]

Return ONLY the JSON array now (one object per assertion above).