
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
doi__10.18632_oncotarget.2039

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 2", "caption": "Amino acid sequences of synthetic peptides used in this study", "footnotes": ["all peptides were synthesized with an amidated C-terminus", "The net charge of the peptides was calculated by subtracting the number of Asp residues (the only negatively charged amino acid residues present in the peptides) from all the positive charges (Lys, Arg and the peptide's N-terminus). Since the C-terminus of all peptides used was amidated, it did not bear a negative charge."], "header_rows": [["Peptide", "", "Sequence1", "Net charge2"], ["", "NK-2", "KILRGVCKKIMRTFLRRISKDILTGKK", "+10"], ["#1", "C7A", "KILRGVAKKIMRTFLRRISKDILTGKK", "+10"], ["#2", "C7A-D21K", "KILRGVAKKIMRTFLRRISKKILTGKK", "+12"], ["#3", "C7A-Δ", "KILRGVAKKIMRTFLRR ILTGKK", "+10"], ["#4", "NK11", "KISKRILTGKK", "+6"], ["#5", "Melittin", "GIGAVLKVLTTGLPALISWIKRKRQQ", "+6"]], "longform_cells": []}, {"table_index": 2, "label": "Table 1", "caption": "Clinical characteristics of patients and molecular data of the corresponding tumor", "footnotes": ["m – male, f – female, spStd – sporadic standard, spMMR-D – sporadic mismatch repair deficient, CIMP-H – CpG island methylator phenotype high, HNPCC – hereditary non-polyposis colorectal carcinoma"], "header_rows": [["Tumor-ID", "Age/Gender", "Tumor location", "TNM-Stage", "Tumor type", "Molecular type"], ["HROC18", "65/f", "caecum", "G2T2N0M0", "primary adenocarcinoma", "spStd"], ["HROC24", "98/m", "colon ascendens", "G2T2N0M0", "primary adenocarcinoma", "spMMR-D"], ["HROC32", "83/f", "colon ascendens", "G2T4N2M1", "primary adenocarcinoma", "spStd"], ["HROC40", "69/m", "colon ascendens", "G3T4N0M0", "primary adenocarcinoma", "CIMP-H"], ["HROC60", "71/m", "colon ascendens", "G2T2N0M0", "primary adenocarcinoma", "CIMP-H"], ["HROC69", "62/m", "colon ascendens", "G3T3NoMx", "primary adenocarcinoma", "spStd"], ["HROC80", "72/m", "caecum", "G2T3N2Mx", "primary adenocarcinoma", "spStd"], ["HROC87", "76/f", "colon ascendens", "G3T3N0M0", "primary adenocarcinoma", "spMMR-D"], ["HROC107", "81/f", "colon ascendens", "G3T3N0M0", "primary adenocarcinoma", "spMMR-D"], ["HROC113", "41/f", "colon ascendens", "G3T4N2Mx", "primary adenocarcinoma", "Lynch Syndrome"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "DRAMP target text lists many approximate tumor-cell viability thresholds plus hemolysis/lymphotoxicity text.", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "C7A"}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "DRAMP target text lists many approximate tumor-cell viability thresholds plus hemolysis/lymphotoxicity text.", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "C7A-Δ"}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "DRAMP target text lists many approximate tumor-cell viability thresholds plus hemolysis/lymphotoxicity text.", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "C7A-D21K"}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "Duplicate DRAMP experiment snapshot carries the same approximate target text as the DRAMP activity row.", "db_measure": "database experiment text row", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "C7A"}, {"assertion_index": 4, "database": "DRAMP", "db_subject_text": "Duplicate DRAMP experiment snapshot carries the same approximate target text as the DRAMP activity row.", "db_measure": "database experiment text row", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "C7A-Δ"}, {"assertion_index": 5, "database": "DRAMP", "db_subject_text": "Duplicate DRAMP experiment snapshot carries the same approximate target text as the DRAMP activity row.", "db_measure": "database experiment text row", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "C7A-D21K"}, {"assertion_index": 6, "database": "dbAMP", "db_subject_text": "Staphylococcus aureus MIC/MBC values plus C7A identity and broad activity labels.", "db_measure": "AntiGram + Antimicrobial Anticancer Antiangiogenesis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "C7A"}, {"assertion_index": 7, "database": "dbAMP", "db_subject_text": "C7A-D21K identity text without row-level assay values.", "db_measure": "Antimicrobial Anticancer Antiangiogenesis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "C7A-D21K"}]

Return ONLY the JSON array now (one object per assertion above).