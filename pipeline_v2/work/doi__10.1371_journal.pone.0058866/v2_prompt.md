
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
doi__10.1371_journal.pone.0058866

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Amino acid sequences of parent soricidin (accession number P0C2P6), SOR-C27 and SOR-C13.", "footnotes": [], "header_rows": [["Peptide", "Sequence", "Activity", "Calculated Molecular Mass g mol−1"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Soricidin", "col_header": "Sequence", "value": "DCSQD CAACS ILARP AELNT ETCIL ECEGK LSSND TEGGL CKEFL HPSKV DLPR"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Soricidin", "col_header": "Activity", "value": "Pain/ Cancer"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "Soricidin", "col_header": "Calculated Molecular Mass g mol−1", "value": "5812.66"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "SOR-C27", "col_header": "Sequence", "value": "EGK LSSND TEGGL CKEFL HPSKV DLPR"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "SOR-C27", "col_header": "Activity", "value": "Cancer"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "SOR-C27", "col_header": "Calculated Molecular Mass g mol−1", "value": "2957.33"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "SOR-C13", "col_header": "Sequence", "value": "KEFL HPSKV DLPR"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "SOR-C13", "col_header": "Activity", "value": "Cancer"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "SOR-C13", "col_header": "Calculated Molecular Mass g mol−1", "value": "1568.85"}]}, {"table_index": 2, "label": "Table 2", "caption": "Long (τ1) and short (τ2) fluorescence lifetime components and their weighted average value τav (%) measured in ex vivo organs of mice bearing SKOV-3 xenograft tumors after injection with SOR-C27-Cy5.5 derived from a two-exponent model.", "footnotes": [], "header_rows": [["", "Weighted Lifetime Average, τav (%)", "Weighted Lifetime Average, τav (%)"], ["Tissue", "Short lifetime (τ2)", "Long Lifetime (τ1)"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Tumor", "col_header": "Weighted Lifetime Average, τav (%) / Short lifetime (τ2)", "value": "1.15 ns (32.3%)"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Tumor", "col_header": "Weighted Lifetime Average, τav (%) / Long Lifetime (τ1)", "value": "1.89 ns (67.8%)"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Lymph Node", "col_header": "Weighted Lifetime Average, τav (%) / Short lifetime (τ2)", "value": "1.16 ns (37.2%)"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Lymph Node", "col_header": "Weighted Lifetime Average, τav (%) / Long Lifetime (τ1)", "value": "1.96 ns (62.8%)"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Kidney", "col_header": "Weighted Lifetime Average, τav (%) / Short lifetime (τ2)", "value": "0.58 ns (61.5%)"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Kidney", "col_header": "Weighted Lifetime Average, τav (%) / Long Lifetime (τ1)", "value": "1.52 ns (38.5%)"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Liver", "col_header": "Weighted Lifetime Average, τav (%) / Short lifetime (τ2)", "value": "0.32 ns (58.7%)"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "Liver", "col_header": "Weighted Lifetime Average, τav (%) / Long Lifetime (τ1)", "value": "1.16 ns (41.3%)"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "Tumor cells: HeLa (~95%Inhibition=100 µM)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "SOR-C27"}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Tumor cells: HeLa (~18%Inhibition=100 µM)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "SOR-C13"}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "Tumor cells: HeLa (~95%Inhibition=100 µM)", "db_measure": "SOR-C13 and SOR-C27 high-affinity antagonists of human TRPV6 channels; database row has no structured assay/value/unit fields.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "Tumor cells: HeLa (~18%Inhibition=100 µM)", "db_measure": "SOR-C13 and SOR-C27 high-affinity antagonists of human TRPV6 channels; database row has no structured assay/value/unit fields.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).