
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
doi__10.1007_s00253-020-10685-x

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "", "footnotes": [], "header_rows": [["Key Points•Higher antibacterial activity and lower hemolysis of ID13 than DLP4.•ID13 could downregulate the genes of bacterial survival and infection.•ID13 could alleviate the S. aureus-induced endometritis of mice.•ID13 could regulate the cytokines and suppress the TLR2-NF-κB signal pathway.", "Key Points•Higher antibacterial activity and lower hemolysis of ID13 than DLP4.•ID13 could downregulate the genes of bacterial survival and infection.•ID13 could alleviate the S. aureus-induced endometritis of mice.•ID13 could regulate the cytokines and suppress the TLR2-NF-κB signal pathway."]], "longform_cells": []}, {"table_index": 2, "label": "Table 1", "caption": "Antibacterial activity of peptides against pathogenic strains.", "footnotes": ["aVancomycin"], "header_rows": [["Peptides", "MICs (μM)", "MICs (μM)", "MICs (μM)", "MICs (μM)", "MICs (μM)", "MICs (μM)", "MICs (μM)"], ["S. aureus CVCC 546", "S. epidermidis ATCC 12228", "S. pneumonia CVCC 2350", "S. suis CVCC 3928", "E. coli ATCC 25922", "S. pullorum CVCC 533", "S. Enteritidis CVCC 3377"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "ID13", "col_header": "MICs (μM) / S. aureus CVCC 546", "value": "0.95"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "ID13", "col_header": "MICs (μM) / S. epidermidis ATCC 12228", "value": "1.91"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "ID13", "col_header": "MICs (μM) / S. pneumonia CVCC 2350", "value": "0.95"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "ID13", "col_header": "MICs (μM) / S. suis CVCC 3928", "value": "0.95"}, {"table_index": 2, "row_index": 3, "col_index": 6, "row_label": "ID13", "col_header": "MICs (μM) / E. coli ATCC 25922", "value": ">30.50"}, {"table_index": 2, "row_index": 3, "col_index": 7, "row_label": "ID13", "col_header": "MICs (μM) / S. pullorum CVCC 533", "value": ">30.50"}, {"table_index": 2, "row_index": 3, "col_index": 8, "row_label": "ID13", "col_header": "MICs (μM) / S. Enteritidis CVCC 3377", "value": ">30.50"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "DLP4", "col_header": "MICs (μM) / S. aureus CVCC 546", "value": "3.75"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "DLP4", "col_header": "MICs (μM) / S. epidermidis ATCC 12228", "value": "14.99"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "DLP4", "col_header": "MICs (μM) / S. pneumonia CVCC 2350", "value": "7.50"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "DLP4", "col_header": "MICs (μM) / S. suis CVCC 3928", "value": "3.75"}, {"table_index": 2, "row_index": 4, "col_index": 6, "row_label": "DLP4", "col_header": "MICs (μM) / E. coli ATCC 25922", "value": ">29.98"}, {"table_index": 2, "row_index": 4, "col_index": 7, "row_label": "DLP4", "col_header": "MICs (μM) / S. pullorum CVCC 533", "value": ">29.98"}, {"table_index": 2, "row_index": 4, "col_index": 8, "row_label": "DLP4", "col_header": "MICs (μM) / S. Enteritidis CVCC 3377", "value": ">29.98"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Vana", "col_header": "MICs (μM) / S. aureus CVCC 546", "value": "0.67"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Vana", "col_header": "MICs (μM) / S. epidermidis ATCC 12228", "value": "0.67"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "Vana", "col_header": "MICs (μM) / S. pneumonia CVCC 2350", "value": "0.34"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "Vana", "col_header": "MICs (μM) / S. suis CVCC 3928", "value": "0.17"}, {"table_index": 2, "row_index": 5, "col_index": 6, "row_label": "Vana", "col_header": "MICs (μM) / E. coli ATCC 25922", "value": "86.15"}, {"table_index": 2, "row_index": 5, "col_index": 7, "row_label": "Vana", "col_header": "MICs (μM) / S. pullorum CVCC 533", "value": "86.15"}, {"table_index": 2, "row_index": 5, "col_index": 8, "row_label": "Vana", "col_header": "MICs (μM) / S. Enteritidis CVCC 3377", "value": "86.15"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CVCC 546", "db_measure": "FICI=0.25 with Vancomycin", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Defensin-like peptide 4/DLP4 [K32G], ID13"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CVCC 546", "db_measure": "FICI=0.375 with Ampicillin", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Defensin-like peptide 4/DLP4 [K32G], ID13"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CVCC 546", "db_measure": "FICI=0.1875 with Rifampin", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Defensin-like peptide 4/DLP4 [K32G], ID13"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CVCC 546", "db_measure": "FICI=0.25 with Ciprofloxacin", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Defensin-like peptide 4/DLP4 [K32G], ID13"}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CVCC 546", "db_measure": "DBAASP synergy assay for Vancomycin; exact value carried by linked_assay_records row 1", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CVCC 546", "db_measure": "DBAASP synergy assay for Ampicillin; exact value carried by linked_assay_records row 2", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CVCC 546", "db_measure": "DBAASP synergy assay for Rifampin; exact value carried by linked_assay_records row 3", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus CVCC 546", "db_measure": "DBAASP synergy assay for Ciprofloxacin; exact value carried by linked_assay_records row 4", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "CAMP", "db_subject_text": "Staphylococcus aureus CVCC 546[MIC = 4 microg/ml], Staphylococcus epidermidis ATCC 12228[MIC = 8 microg/ml], Streptococcus pneumoniae CVCC 2350 [MIC = 4 microg/ml], Streptococcus suis CVCC 3928[MIC = 4 microg/ml], Escherichia coli ATCC 25922[MIC >128 microg/ml], Escherichia coli K88[MIC >128 microg/ml], Salmonella enterica subsp. enterica serovar Pullorum CVCC 533[MIC >128 microg/ml], Salmonella enterica subsp. enterica serovar Enteritidis CVCC 3377[MIC >128 microg/ml], Murine macrophage cells RAW 264.7[20-30% Killing = 256 microg/ml]", "db_measure": "Staphylococcus aureus CVCC 546[MIC = 4 microg/ml], Staphylococcus epidermidis ATCC 12228[MIC = 8 microg/ml], Streptococcus pneumoniae CVCC 2350 [MIC = 4 microg/ml], Streptococcus suis CVCC 3928[MIC = 4 microg/ml], Escherichia coli ATCC 25922[MIC >128 microg/ml], Escherichia coli K88[MIC >128 microg/ml], Salmonella enterica subsp. enterica serovar Pullorum CVCC 533[MIC >128 microg/ml], Salmonella enterica subsp. enterica serovar Enteritidis CVCC 3377[MIC >128 microg/ml], Murine macrophage cells RAW 264.7[20-30% Killing = 256 microg/ml]", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).