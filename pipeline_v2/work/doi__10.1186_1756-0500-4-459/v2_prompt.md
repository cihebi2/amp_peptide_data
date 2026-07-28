
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
doi__10.1186_1756-0500-4-459

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Peptide parameters of the newly isolated Hc-AFP defensin peptides", "footnotes": [], "header_rows": [["Defensin", "Signal peptide (amino acids)", "Mature peptide (amino acids)", "MW (Da)", "pI", "Charge at pH7"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Hc-AFP1", "col_header": "Signal peptide (amino acids)", "value": "1-29"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Hc-AFP1", "col_header": "Mature peptide (amino acids)", "value": "30-80"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "Hc-AFP1", "col_header": "MW (Da)", "value": "5479.32"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "Hc-AFP1", "col_header": "pI", "value": "8.50"}, {"table_index": 1, "row_index": 2, "col_index": 6, "row_label": "Hc-AFP1", "col_header": "Charge at pH7", "value": "3.2"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Hc-AFP2", "col_header": "Signal peptide (amino acids)", "value": "1-29"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Hc-AFP2", "col_header": "Mature peptide (amino acids)", "value": "30-81"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Hc-AFP2", "col_header": "MW (Da)", "value": "5718.31"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "Hc-AFP2", "col_header": "pI", "value": "8.73"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "Hc-AFP2", "col_header": "Charge at pH7", "value": "4.2"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Hc-AFP3", "col_header": "Signal peptide (amino acids)", "value": "1-29"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Hc-AFP3", "col_header": "Mature peptide (amino acids)", "value": "30-80"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "Hc-AFP3", "col_header": "MW (Da)", "value": "5524.33"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "Hc-AFP3", "col_header": "pI", "value": "8.20"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "Hc-AFP3", "col_header": "Charge at pH7", "value": "2.2"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Hc-AFP4", "col_header": "Signal peptide (amino acids)", "value": "1-29"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Hc-AFP4", "col_header": "Mature peptide (amino acids)", "value": "30-81"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "Hc-AFP4", "col_header": "MW (Da)", "value": "5731.61"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "Hc-AFP4", "col_header": "pI", "value": "8.94"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "Hc-AFP4", "col_header": "Charge at pH7", "value": "5.2"}]}, {"table_index": 2, "label": "Table 2", "caption": "Antifungal activity of the Heliophila coronopifolia defensins", "footnotes": ["aMP = Membrane permeabilization"], "header_rows": [["", "Botrytis cinerea", "Botrytis cinerea", "Botrytis cinerea", "Botrytis cinerea", "Fusarium solani", "Fusarium solani", "Fusarium solani", "Fusarium solani"], ["Defensin", "IC50μg ml-1", "Hyphal morphology", "Spore lysis", "MPa", "IC50μg ml-1", "Hyphal morphology", "Spore lysis", "MPa"], ["Hc-AFP1", "> 25", "Tip swelling", "No", "Yes", "> 25", "Mild hyper-branching", "No", "No"], ["Hc-AFP2", "10-15", "Severe hyper-branchingTip swellingLysis", "Yes", "Yes", "10-15", "Severe hyper-branching", "No", "Yes"], ["Hc-AFP3", "20-25", "Severe hyper-branchingTip swelling and disruption", "Yes", "Yes", "> 25", "Mild hyper-branching", "No", "No"], ["Hc-AFP4", "15-20", "Mild hyper-branchingTip swelling", "No", "Yes", "5-10", "Severe hyper-branching", "No", "Yes"]], "longform_cells": []}, {"table_index": 3, "label": "Table 3", "caption": "Primers used in the q-RT-PCR analysis of the Hc-AFP defensin genes", "footnotes": [], "header_rows": [["Primer set", "Sequence 5'→3'", "Primer", "Target gene", "PCR eff."]], "longform_cells": [{"table_index": 3, "row_index": 2, "col_index": 2, "row_label": "Helio EF FwHelio EF Rv", "col_header": "Sequence 5'→3'", "value": "ATGGGTAAAGAGAAGTTTCACATCAAGTTGGGTCCTTCTTGTCAACACTC"}, {"table_index": 3, "row_index": 2, "col_index": 3, "row_label": "Helio EF FwHelio EF Rv", "col_header": "Primer", "value": "150 nm200 nm"}, {"table_index": 3, "row_index": 2, "col_index": 4, "row_label": "Helio EF FwHelio EF Rv", "col_header": "Target gene", "value": "H. coronopifolia elongation factor 1α"}, {"table_index": 3, "row_index": 2, "col_index": 5, "row_label": "Helio EF FwHelio EF Rv", "col_header": "PCR eff.", "value": "0.99"}, {"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "Hc-AFP1 Rt FwHc-AFP1 Rt Rv", "col_header": "Sequence 5'→3'", "value": "TCAGGAGTTTGTGGAAACAGTGGGCAGCCAACATAAACATATTTTGGA"}, {"table_index": 3, "row_index": 3, "col_index": 3, "row_label": "Hc-AFP1 Rt FwHc-AFP1 Rt Rv", "col_header": "Primer", "value": "200 nm150 nm"}, {"table_index": 3, "row_index": 3, "col_index": 4, "row_label": "Hc-AFP1 Rt FwHc-AFP1 Rt Rv", "col_header": "Target gene", "value": "Hc-AFP1"}, {"table_index": 3, "row_index": 3, "col_index": 5, "row_label": "Hc-AFP1 Rt FwHc-AFP1 Rt Rv", "col_header": "PCR eff.", "value": "0.98"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "Hc-AFP2 Rt FwHc-AFP2 Rt Rv", "col_header": "Sequence 5'→3'", "value": "CGTGTAGGAACCAGTGCATCAACTAGGATTTTTCTGGTATGGCCG"}, {"table_index": 3, "row_index": 4, "col_index": 3, "row_label": "Hc-AFP2 Rt FwHc-AFP2 Rt Rv", "col_header": "Primer", "value": "150 nm200 nm"}, {"table_index": 3, "row_index": 4, "col_index": 4, "row_label": "Hc-AFP2 Rt FwHc-AFP2 Rt Rv", "col_header": "Target gene", "value": "Hc-AFP2"}, {"table_index": 3, "row_index": 4, "col_index": 5, "row_label": "Hc-AFP2 Rt FwHc-AFP2 Rt Rv", "col_header": "PCR eff.", "value": "0.99"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "Hc-AFP3 Rt FwHc-AFP3 Rt Rv", "col_header": "Sequence 5'→3'", "value": "TCAGGAGTTTGTGGAAACACTGAATCATTAGAAGCTGCCAACATAAACTAG"}, {"table_index": 3, "row_index": 5, "col_index": 3, "row_label": "Hc-AFP3 Rt FwHc-AFP3 Rt Rv", "col_header": "Primer", "value": "150 nm200 nm"}, {"table_index": 3, "row_index": 5, "col_index": 4, "row_label": "Hc-AFP3 Rt FwHc-AFP3 Rt Rv", "col_header": "Target gene", "value": "Hc-AFP3"}, {"table_index": 3, "row_index": 5, "col_index": 5, "row_label": "Hc-AFP3 Rt FwHc-AFP3 Rt Rv", "col_header": "PCR eff.", "value": "0.97"}, {"table_index": 3, "row_index": 6, "col_index": 2, "row_label": "Hc-AFP4 Rt FwHc-AFP4 Rt Rv", "col_header": "Sequence 5'→3'", "value": "ATGGTGGAAGCTCAGAAGTTGTGTGCTAGCAGCAAAGATGTTTGTTTG"}, {"table_index": 3, "row_index": 6, "col_index": 3, "row_label": "Hc-AFP4 Rt FwHc-AFP4 Rt Rv", "col_header": "Primer", "value": "200 nm150 nm"}, {"table_index": 3, "row_index": 6, "col_index": 4, "row_label": "Hc-AFP4 Rt FwHc-AFP4 Rt Rv", "col_header": "Target gene", "value": "Hc-AFP4"}, {"table_index": 3, "row_index": 6, "col_index": 5, "row_label": "Hc-AFP4 Rt FwHc-AFP4 Rt Rv", "col_header": "PCR eff.", "value": "0.92"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Antifungal", "db_measure": "Bridge", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "APD6", "db_subject_text": "Antifungal", "db_measure": "Bridge", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "APD6", "db_subject_text": "Antifungal", "db_measure": "Bridge", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "APD6", "db_subject_text": "Antifungal", "db_measure": "Bridge", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "CAMP", "db_subject_text": "Botrytis cinerea ( IC50 = 15-20 microg/ml ), Fusarium solani ( IC50 = 5-10 microg/ml )", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).