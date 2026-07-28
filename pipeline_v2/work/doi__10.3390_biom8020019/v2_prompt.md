
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
doi__10.3390_biom8020019

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Sequences and characteristics of the antimicrobial peptides (AMPs) used in this study.", "footnotes": ["a Net charge is calculated for physiological conditions; b 3D structure determined by nuclear magnetic resonance (NMR) spectroscopy in the presence of sodium dodecyl sulfate (SDS) or dodecylphosphocholine (DPC) micelles; c C-terminal amidated version of the peptide tritrpticin."], "header_rows": [["Peptide", "Sequence", "NetCharge a", "3D Structure b", "Mechanism of Action", "Ref."], ["Magainin2", "GIGKFLHSAKKFGKAFVGEIMNS", "+3", "α-helix (I2–N22)", "Membranolytic", "[26,27]"], ["Indolicidin", "ILPWKWPWWPWRR-NH2", "+4", "β-turns (K5, W8)", "Intracellular target", "[28,29]"], ["PuroA", "FPVTWKWWKWWKG-NH2", "+5", "β-turn (T4–W7)helical turn (W8–W10)", "Membranolytic", "[30,31]"], ["Tritrp1 c", "VRRFPWWWPFLRR-NH2", "+5", "β-turn (P5–W8)helical turn (W9–R12)", "Membranolytic", "[25]"], ["Tritrp3", "VRRFAWWWAFLRR-NH2", "+5", "α-helix (F4–L11)", "Membranolytic", "[25]"], ["Tritrp7", "VRRFAWWWPFLRR-NH2", "+5", "α-helix-like (F4–L11)", "Membranolytic", "[25]"], ["Tritrp8", "VRRFPWWWAFLRR-NH2", "+5", "β-turn (P5–W8)helical turn (W9–R12)", "Membranolytic", "[25]"]], "longform_cells": []}, {"table_index": 2, "label": "Table 2", "caption": "Peptide sequence and minimal inhibitory concentration (MIC) against Escherichia coli ATCC 25922 in Mueller-Hinton broth media. The MICs were run in triplicate and the range of all three experiments is presented.", "footnotes": [], "header_rows": [["Peptide", "Sequence", "MIC (µM)"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Magainin2-F5W–Arg", "col_header": "Sequence", "value": "GIGRFLHSARRFGRAFVGEIMNS"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Magainin2-F5W–Arg", "col_header": "MIC (µM)", "value": "8"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Magainin2-F5W–Lys", "col_header": "Sequence", "value": "GIGKFLHSAKKFGKAFVGEIMNS"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Magainin2-F5W–Lys", "col_header": "MIC (µM)", "value": "16"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Indolicidin", "col_header": "Sequence", "value": "ILPWKWPWWPWRR-NH2"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Indolicidin", "col_header": "MIC (µM)", "value": "8"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Indolicidin–Lys", "col_header": "Sequence", "value": "ILPWKWPWWPWKK-NH2"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Indolicidin–Lys", "col_header": "MIC (µM)", "value": "16"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "PuroA–Arg", "col_header": "Sequence", "value": "FPVTWRWWRWWRG-NH2"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "PuroA–Arg", "col_header": "MIC (µM)", "value": "8–16"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "PuroA–Lys", "col_header": "Sequence", "value": "FPVTWKWWKWWKG-NH2"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "PuroA–Lys", "col_header": "MIC (µM)", "value": "8"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "Tritrp3–Arg", "col_header": "Sequence", "value": "V R R FAWWWAFL R R -NH2"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "Tritrp3–Arg", "col_header": "MIC (µM)", "value": "2"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "Tritrp3–Lys", "col_header": "Sequence", "value": "V K K FAWWWAFL K K -NH2"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "Tritrp3–Lys", "col_header": "MIC (µM)", "value": "2"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "Tritrp7–Arg", "col_header": "Sequence", "value": "V R R FAWWWPFL R R -NH2"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "Tritrp7–Arg", "col_header": "MIC (µM)", "value": "8"}, {"table_index": 2, "row_index": 11, "col_index": 2, "row_label": "Tritrp7–Lys", "col_header": "Sequence", "value": "V K K FAWWWPFL K K -NH2"}, {"table_index": 2, "row_index": 11, "col_index": 3, "row_label": "Tritrp7–Lys", "col_header": "MIC (µM)", "value": "32"}, {"table_index": 2, "row_index": 12, "col_index": 2, "row_label": "Tritrp8–Arg", "col_header": "Sequence", "value": "V R R FPWWWAFL R R -NH2"}, {"table_index": 2, "row_index": 12, "col_index": 3, "row_label": "Tritrp8–Arg", "col_header": "MIC (µM)", "value": "2–4"}, {"table_index": 2, "row_index": 13, "col_index": 2, "row_label": "Tritrp8–Lys", "col_header": "Sequence", "value": "V K K FPWWWAFL K K -NH2"}, {"table_index": 2, "row_index": 13, "col_index": 3, "row_label": "Tritrp8–Lys", "col_header": "MIC (µM)", "value": "4"}, {"table_index": 2, "row_index": 14, "col_index": 2, "row_label": "Tritrp–Agb", "col_header": "Sequence", "value": "V (Agb) (Agb) FPWWWPFL (Agb) (Agb) -NH2"}, {"table_index": 2, "row_index": 14, "col_index": 3, "row_label": "Tritrp–Agb", "col_header": "MIC (µM)", "value": "4"}, {"table_index": 2, "row_index": 15, "col_index": 2, "row_label": "Tritrp–Arg", "col_header": "Sequence", "value": "V R R FPWWWPFL R R -NH2"}, {"table_index": 2, "row_index": 15, "col_index": 3, "row_label": "Tritrp–Arg", "col_header": "MIC (µM)", "value": "2–4"}, {"table_index": 2, "row_index": 16, "col_index": 2, "row_label": "Tritrp–hArg", "col_header": "Sequence", "value": "V (hArg)(hArg)FPWWWPFL(hArg)(hArg) -NH2"}, {"table_index": 2, "row_index": 16, "col_index": 3, "row_label": "Tritrp–hArg", "col_header": "MIC (µM)", "value": "4"}, {"table_index": 2, "row_index": 17, "col_index": 2, "row_label": "Tritrp–Dap", "col_header": "Sequence", "value": "V (Dap) (Dap) FPWWWPFL (Dap) (Dap) -NH2"}, {"table_index": 2, "row_index": 17, "col_index": 3, "row_label": "Tritrp–Dap", "col_header": "MIC (µM)", "value": "4"}, {"table_index": 2, "row_index": 18, "col_index": 2, "row_label": "Tritrp–Dab", "col_header": "Sequence", "value": "V (Dab) (Dab) FPWWWPFL (Dab) (Dab) -NH2"}, {"table_index": 2, "row_index": 18, "col_index": 3, "row_label": "Tritrp–Dab", "col_header": "MIC (µM)", "value": "4–8"}, {"table_index": 2, "row_index": 19, "col_index": 2, "row_label": "Tritrp–Orn", "col_header": "Sequence", "value": "V (Orn) (Orn) FPWWWPFL (Orn) (Orn) -NH2"}, {"table_index": 2, "row_index": 19, "col_index": 3, "row_label": "Tritrp–Orn", "col_header": "MIC (µM)", "value": "16"}, {"table_index": 2, "row_index": 20, "col_index": 2, "row_label": "Tritrp–Lys", "col_header": "Sequence", "value": "V K K FPWWWPFL K K -NH2"}, {"table_index": 2, "row_index": 20, "col_index": 3, "row_label": "Tritrp–Lys", "col_header": "MIC (µM)", "value": "16"}, {"table_index": 2, "row_index": 21, "col_index": 2, "row_label": "Melittin", "col_header": "Sequence", "value": "GIGAVLKVLTTGLPALISWIKRKRQQ-NH2"}, {"table_index": 2, "row_index": 21, "col_index": 3, "row_label": "Melittin", "col_header": "MIC (µM)", "value": "2"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 25922", "db_measure": "MIC", "db_value": "2-4", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 25922", "db_measure": "MIC", "db_value": "2-4", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).