
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
doi__10.1155_2013_251398

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Oligonucleotides sequences corresponding to L-2 and L-20.", "footnotes": [], "header_rows": [["Name", "Sequence"], ["L-2", "CATGCACGCTAGAATCAAGCCAACCTTCAGAAGATTGAAGTGGAAGTACAAGGGTAAGTTCTGGTAA"], ["L-2C", "GATCTTACCAGAACTTACCCTTGTACTTCCACTTCAATCTTCTGAAGGTTGGCTTGATTCTAGCGTG"], ["L-20", "ATGCACTACAGAATCAAGCCAACCTTCAGAAGATTGAAGTGGAAGTACAAGGGTAAGTTCGCTTAA"], ["L-20C", "GATCTTAAGCGAACTTACCCTTGTACTTCCACTTCAATCTTCTGAAGGTTGGCTTGATTCTGTAGTG"]], "longform_cells": []}, {"table_index": 2, "label": "Table 2", "caption": "Effect of L-2 and CIGB-552 on the cell viability in different tumor cell lines.", "footnotes": ["The peptides were added to 10,000 cells in a range of concentrations from 0 to 200 μM. After 48 hours of incubation, cell viability was determined by SRB (sulforhodamine B, sodium salt) assay. Finally, absorbance was measured at 492 nm, and the IC50 values were calculated from the growth curves.", "*Mean ± SD of three determinations. Data were obtained from two different experiments."], "header_rows": [["Tumor cell line", "Origin", "L-2 IC50 (μM)*", "CIGB-552 IC50 (μM)*"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "H460", "col_header": "Origin", "value": "Human nonsmall-cell lung cancer"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "H460", "col_header": "L-2 IC50 (μM)*", "value": "57 ± 6"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "H460", "col_header": "CIGB-552 IC50 (μM)*", "value": "23 ± 8"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "H-125", "col_header": "Origin", "value": "Human nonsmall-cell lung cancer"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "H-125", "col_header": "L-2 IC50 (μM)*", "value": "75 ± 9"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "H-125", "col_header": "CIGB-552 IC50 (μM)*", "value": "42 ± 6"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "H-82", "col_header": "Origin", "value": "Human small-cell lung cancer"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "H-82", "col_header": "L-2 IC50 (μM)*", "value": "50 ± 6"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "H-82", "col_header": "CIGB-552 IC50 (μM)*", "value": "15 ± 3"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "LS174T", "col_header": "Origin", "value": "Human colon adenocarcinoma"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "LS174T", "col_header": "L-2 IC50 (μM)*", "value": "56 ± 3"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "LS174T", "col_header": "CIGB-552 IC50 (μM)*", "value": "22 ± 4"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "MDA-231", "col_header": "Origin", "value": "Human breast adenocarcinoma"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "MDA-231", "col_header": "L-2 IC50 (μM)*", "value": "125 ± 3"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "MDA-231", "col_header": "CIGB-552 IC50 (μM)*", "value": "40 ± 9"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "PBMC", "col_header": "Origin", "value": "Human mononuclear cells"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "PBMC", "col_header": "L-2 IC50 (μM)*", "value": "234 ± 9"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "PBMC", "col_header": "CIGB-552 IC50 (μM)*", "value": "249 ± 6"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human PBMC", "db_measure": "IC50", "db_value": "249±6", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "Anti-lipopolysaccharide factor (32-51)[Y2A,P6p,L11l], CIGB-552"}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Not available", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Anti-lipopolysaccharide factor (32-51)[Y2A], L-2"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human PBMC", "db_measure": "IC50", "db_value": "249±6", "db_unit": "µg/ml", "db_sequence": "", "db_claimed_peptide_name": "CIGB-552"}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "Not available", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "L-2"}]

Return ONLY the JSON array now (one object per assertion above).