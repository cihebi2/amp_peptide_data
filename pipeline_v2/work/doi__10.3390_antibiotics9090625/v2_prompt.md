
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
doi__10.3390_antibiotics9090625

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Biophysical properties of Figainin 1.", "footnotes": ["a MM (calc) is the calculated monoisotopic molecular mass based on the proposed structure of Figainin 1. b MM (obs) is the observed monoisotopic molecular mass of the deprotonated form of Figainin 1."], "header_rows": [["Peptide", "MM (calc) a(Da)", "MM (obs) b(Da)", "Net Charge", "Hydrophobic Ratio(%)", "GRAVY"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Figainin 1", "col_header": "MM (calc) a(Da)", "value": "1915.19"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Figainin 1", "col_header": "MM (obs) b(Da)", "value": "1914.20"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "Figainin 1", "col_header": "Net Charge", "value": "+3"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "Figainin 1", "col_header": "Hydrophobic Ratio(%)", "value": "61"}, {"table_index": 1, "row_index": 2, "col_index": 6, "row_label": "Figainin 1", "col_header": "GRAVY", "value": "1.46"}]}, {"table_index": 2, "label": "Table 2", "caption": "Minimal inhibitory concentration (MIC, µM and g/L) for representative pathogenic microorganisms, and half maximal inhibitory concentration (IC50, µM and g/L) against epimastigote forms of T. cruzi displayed by Figainin 1.", "footnotes": ["a NA: no activity observed at a maximum concentration of 64 µM (0.123 g/L)."], "header_rows": [["", "Figainin 1", "Figainin 1"], ["Microorganisms", "µM", "g/L"], ["Gram-positive bacteria (MIC)", "", ""]], "longform_cells": [{"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "E. faecalis (ATCC 29212)", "col_header": "Figainin 1 / µM", "value": "8"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "E. faecalis (ATCC 29212)", "col_header": "Figainin 1 / g/L", "value": "0.015"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "S. aureus (ATCC 25923)", "col_header": "Figainin 1 / µM", "value": "4"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "S. aureus (ATCC 25923)", "col_header": "Figainin 1 / g/L", "value": "0.008"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "S. epidermidis (ATCC 12228)", "col_header": "Figainin 1 / µM", "value": "2"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "S. epidermidis (ATCC 12228)", "col_header": "Figainin 1 / g/L", "value": "0.004"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "E. casseliflavus (ATCC 700327)", "col_header": "Figainin 1 / µM", "value": "16"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "E. casseliflavus (ATCC 700327)", "col_header": "Figainin 1 / g/L", "value": "0.030"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "E. coli (ATCC 25922)", "col_header": "Figainin 1 / µM", "value": "16"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "E. coli (ATCC 25922)", "col_header": "Figainin 1 / g/L", "value": "0.030"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "P. aeruginosa (ATCC 27853)", "col_header": "Figainin 1 / µM", "value": "NA a"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "P. aeruginosa (ATCC 27853)", "col_header": "Figainin 1 / g/L", "value": "NA a"}, {"table_index": 2, "row_index": 11, "col_index": 2, "row_label": "K. pneumoniae (ATCC 13883)", "col_header": "Figainin 1 / µM", "value": "4"}, {"table_index": 2, "row_index": 11, "col_index": 3, "row_label": "K. pneumoniae (ATCC 13883)", "col_header": "Figainin 1 / g/L", "value": "0.008"}, {"table_index": 2, "row_index": 13, "col_index": 2, "row_label": "C. albicans (ATCC 90028)", "col_header": "Figainin 1 / µM", "value": "NA a"}, {"table_index": 2, "row_index": 13, "col_index": 3, "row_label": "C. albicans (ATCC 90028)", "col_header": "Figainin 1 / g/L", "value": "NA a"}, {"table_index": 2, "row_index": 14, "col_index": 2, "row_label": "C. parapsilosis (ATCC 22019)", "col_header": "Figainin 1 / µM", "value": "NA a"}, {"table_index": 2, "row_index": 14, "col_index": 3, "row_label": "C. parapsilosis (ATCC 22019)", "col_header": "Figainin 1 / g/L", "value": "NA a"}, {"table_index": 2, "row_index": 15, "col_index": 2, "row_label": "Trypanosoma epimastigotes (IC50) T. cruzi", "col_header": "Figainin 1 / µM", "value": "15.9"}, {"table_index": 2, "row_index": 15, "col_index": 3, "row_label": "Trypanosoma epimastigotes (IC50) T. cruzi", "col_header": "Figainin 1 / g/L", "value": "0.030"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "Tumor cells: B16-F10 (IC50=10.5 µM (0.020 g/L)); HeLa (IC50=11.1 µM (0.021 g/L)); MCF-7 (IC50=13.7 µM (0.026 g/L))", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Figainin 1 "}, {"assertion_index": 1, "database": "APD6", "db_subject_text": "Figainin 1, a Novel Amphibian Skin Peptide with Antimicrobial and Antiproliferative Properties", "db_measure": "CD", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Figainin 1, a Novel Amphibian Skin Peptide with Antimicrobial and Antiproliferative Properties"}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "Tumor cells: B16-F10 (IC50=10.5 µM (0.020 g/L)); HeLa (IC50=11.1 µM (0.021 g/L)); MCF-7 (IC50=13.7 µM (0.026 g/L))", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Figainin 1, a Novel Amphibian Skin Peptide with Antimicrobial and Antiproliferative Properties"}]

Return ONLY the JSON array now (one object per assertion above).