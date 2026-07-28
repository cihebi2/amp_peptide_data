
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
doi__10.1111_j.1582-4934.2008.00341.x

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "1", "caption": "Minimal inhibitory concentrations (MIC*: μg/ml) of AG-30 and LL-37", "footnotes": ["MIC was defined as the lowest concentration of peptide that inhibited the bacterial visible growth after incubation for 16 hrs at 37°C with vigorous shaking."], "header_rows": [["", "AG30", "LL37", "Control"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "E. coli (ATCC 25922)", "col_header": "AG30", "value": "40.0"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "E. coli (ATCC 25922)", "col_header": "LL37", "value": "5.00"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "E. coli (ATCC 25922)", "col_header": "Control", "value": ">80"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "P. aeruginosa (ATCC 27853)", "col_header": "AG30", "value": "5.00"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "P. aeruginosa (ATCC 27853)", "col_header": "LL37", "value": "2.50"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "P. aeruginosa (ATCC 27853)", "col_header": "Control", "value": ">10"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "S. aureus (ATCC 29213)", "col_header": "AG30", "value": "20.0"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "S. aureus (ATCC 29213)", "col_header": "LL37", "value": ">80"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "S. aureus (ATCC 29213)", "col_header": "Control", "value": ">80"}]}, {"table_index": 2, "label": "2", "caption": "Cluster analysis using GeneSpring software to detect a twofold increased or decreased in gene expression at 72 hrs after AG-30 treatment", "footnotes": [], "header_rows": [], "longform_cells": [{"table_index": 2, "row_index": 1, "col_index": 2, "row_label": "", "col_header": "col1", "value": "6 hrs"}, {"table_index": 2, "row_index": 1, "col_index": 3, "row_label": "", "col_header": "col2", "value": "24 hrs"}, {"table_index": 2, "row_index": 1, "col_index": 4, "row_label": "", "col_header": "col3", "value": "72 hrs"}, {"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Angiopoietin 2", "col_header": "col1", "value": "1.03"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Angiopoietin 2", "col_header": "col2", "value": "2.18"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "Angiopoietin 2", "col_header": "col3", "value": "8.52"}, {"table_index": 2, "row_index": 2, "col_index": 5, "row_label": "Angiopoietin 2", "col_header": "col4", "value": "NM_001147"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Angiopoietin-like 4, transcript variant", "col_header": "col1", "value": "0.80"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Angiopoietin-like 4, transcript variant", "col_header": "col2", "value": "1.64"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "Angiopoietin-like 4, transcript variant", "col_header": "col3", "value": "5.46"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "Angiopoietin-like 4, transcript variant", "col_header": "col4", "value": "NM_139314"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Interleukin 8", "col_header": "col1", "value": "1.00"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Interleukin 8", "col_header": "col2", "value": "1.45"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "Interleukin 8", "col_header": "col3", "value": "3.92"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "Interleukin 8", "col_header": "col4", "value": "NM_000584"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Jagged 1", "col_header": "col1", "value": "1.73"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Jagged 1", "col_header": "col2", "value": "1.31"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "Jagged 1", "col_header": "col3", "value": "3.90"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "Jagged 1", "col_header": "col4", "value": "NM_000214"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Epiregulin", "col_header": "col1", "value": "1.27"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "Epiregulin", "col_header": "col2", "value": "1.72"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "Epiregulin", "col_header": "col3", "value": "2.45"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "Epiregulin", "col_header": "col4", "value": "NM_001432"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "Vascular endothelial growth factor", "col_header": "col1", "value": "1.36"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "Vascular endothelial growth factor", "col_header": "col2", "value": "0.87"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "Vascular endothelial growth factor", "col_header": "col3", "value": "2.07"}, {"table_index": 2, "row_index": 7, "col_index": 5, "row_label": "Vascular endothelial growth factor", "col_header": "col4", "value": "NM_003376"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "Insulin-like growth factor", "col_header": "col1", "value": "0.85"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "Insulin-like growth factor", "col_header": "col2", "value": "1.17"}, {"table_index": 2, "row_index": 8, "col_index": 4, "row_label": "Insulin-like growth factor", "col_header": "col3", "value": "2.07"}, {"table_index": 2, "row_index": 8, "col_index": 5, "row_label": "Insulin-like growth factor", "col_header": "col4", "value": "NM_00061"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "Neuropilin-1 soluble isoform 11", "col_header": "col1", "value": "0.15"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "Neuropilin-1 soluble isoform 11", "col_header": "col2", "value": "0.21"}, {"table_index": 2, "row_index": 9, "col_index": 4, "row_label": "Neuropilin-1 soluble isoform 11", "col_header": "col3", "value": "0.20"}, {"table_index": 2, "row_index": 9, "col_index": 5, "row_label": "Neuropilin-1 soluble isoform 11", "col_header": "col4", "value": "AF280547"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "CAMP", "db_subject_text": "Escherichia coli ATCC 25922[MIC = 40 microg/ml], Staphylococcus aureus ATCC 29213[MIC = 20 microg/ml], Pseudomonas aeruginosa ATCC 27853[MIC = 5 microg/ml], Pseudomonas aeruginosa ATCC 27853", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "AG-30"}]

Return ONLY the JSON array now (one object per assertion above).