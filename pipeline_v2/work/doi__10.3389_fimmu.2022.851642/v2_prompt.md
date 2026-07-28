
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
doi__10.3389_fimmu.2022.851642

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "MICs of Bomidin against various bacteria and fungi.", "footnotes": ["The effects of Bomidin on other bacterial strains, including 8 Gram-positive bacteria and 4 Gram-negative bacteria, and the MICs were in the range of 1-4 μM. For the more tolerant Gram-positive bacteria Enterococcus faecalis and the fungi Candida albicans, the MIC value ranges from 8-32μM. For the drug-resistant bacteria, the MIC value is greater than or equal to 50μM."], "header_rows": [["Organism", "Organism", "MIC range (μM)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Gram Positive Bacteria", "col_header": "Organism", "value": "Staphylococcus aureus (4 strains)"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Gram Positive Bacteria", "col_header": "MIC range (μM)", "value": "2∼4"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Bacillus megaterium Bm 11", "col_header": "Organism", "value": "2"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Bacillus subtilis KCTC 3068", "col_header": "Organism", "value": "4"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Staphylococcus epidermidis KCTC 1917", "col_header": "Organism", "value": "4"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Enterococcus faecalis (10 strains)", "col_header": "Organism", "value": "8∼> 32"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Enterococcus faecium (5 strains)", "col_header": "Organism", "value": "8∼> 32"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Streptococcus agalactiae (3 strains)", "col_header": "Organism", "value": "1∼4"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Acinetobacter baumanni (10 strains)", "col_header": "Organism", "value": "0.5∼16"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Gram Negative Bacteria", "col_header": "Organism", "value": "Escherichia coli (3 strains)"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "Gram Negative Bacteria", "col_header": "MIC range (μM)", "value": "2∼4"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "Salmonella typhimurium ATCC 14028", "col_header": "Organism", "value": "4"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "Pseudomonas aeruginosa ATCC 27853", "col_header": "Organism", "value": "1"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "Serratia marcescens ATCC 8100", "col_header": "Organism", "value": "2"}, {"table_index": 1, "row_index": 14, "col_index": 2, "row_label": "Fungi", "col_header": "Organism", "value": "Candida albicans"}, {"table_index": 1, "row_index": 14, "col_index": 3, "row_label": "Fungi", "col_header": "MIC range (μM)", "value": "16"}, {"table_index": 1, "row_index": 15, "col_index": 2, "row_label": "Cryptococcus neoformans", "col_header": "Organism", "value": "4"}, {"table_index": 1, "row_index": 16, "col_index": 2, "row_label": "Drug-resistant Bacteria", "col_header": "Organism", "value": "Vancomycin-resistant Staphylococcus aureus"}, {"table_index": 1, "row_index": 16, "col_index": 3, "row_label": "Drug-resistant Bacteria", "col_header": "MIC range (μM)", "value": "> 50"}, {"table_index": 1, "row_index": 17, "col_index": 2, "row_label": "Extended-spectrum β-lactamases (ESBLs)-producing Escherichia coli", "col_header": "Organism", "value": "> 50"}, {"table_index": 1, "row_index": 18, "col_index": 2, "row_label": "Multiple drug-resistant Pseudomonas aeruginosa", "col_header": "Organism", "value": "> 50"}, {"table_index": 1, "row_index": 19, "col_index": 2, "row_label": "Multiple drug-resistant Acinetobacter baumanni", "col_header": "Organism", "value": "> 50"}, {"table_index": 1, "row_index": 20, "col_index": 2, "row_label": "Multiple drug-resistant Klebsiella", "col_header": "Organism", "value": "50"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Enterococcus faecalis", "db_measure": "MIC", "db_value": "8-32", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Enterococcus faecium", "db_measure": "MIC", "db_value": "8-32", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus VRSA1", "db_measure": "MIC", "db_value": ">50", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "SARS-CoV-2", "db_measure": "IC50 REP", "db_value": "80", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Enterococcus faecalis", "db_measure": "MIC", "db_value": "8-32", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Enterococcus faecium", "db_measure": "MIC", "db_value": "8-32", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus VRSA1", "db_measure": "MIC", "db_value": ">50", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "SARS-CoV-2", "db_measure": "IC50 REP", "db_value": "80", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DRAMP", "db_subject_text": "[Ref.35663971]Dengue virus 2(DENV2):inhibition of viral infection in Huh7 cells(50% inhibition at 10 μM);##HSV:inhibition of viral infection in Huh7 cells(50% inhibition at 10 μM);##SARS-CoV-2:inhibition of viral infection in Huh7 cells(80% inhibition at 10 μM).", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DRAMP", "db_subject_text": "[Ref.35663971]Dengue virus 2(DENV2):inhibition of viral infection in Huh7 cells(50% inhibition at 10 μM);##HSV:inhibition of viral infection in Huh7 cells(50% inhibition at 10 μM);##SARS-CoV-2:inhibition of viral infection in Huh7 cells(80% inhibition at 10 μM).", "db_measure": "DRAMP general activity text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).