
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
doi__10.1177_11779322251315291

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1.", "caption": "The structure of the 2-layer membrane of gram-positive and gram-negative bacteria.", "footnotes": [], "header_rows": [["Membrane", "Lipids", "Lipids", "Lipids"], ["POPE", "POPG", "TOCL1"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Gram-negative bacteria", "col_header": "Lipids / POPE", "value": "62"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Gram-negative bacteria", "col_header": "Lipids / POPG", "value": "12"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Gram-negative bacteria", "col_header": "Lipids / TOCL1", "value": "4"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Gram-positive bacteria", "col_header": "Lipids / POPE", "value": "0"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Gram-positive bacteria", "col_header": "Lipids / POPG", "value": "46"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "Gram-positive bacteria", "col_header": "Lipids / TOCL1", "value": "32"}]}, {"table_index": 2, "label": "Table 2.", "caption": "Yields of antimicrobial peptide at different stages of purification from 400 g U. Dioica leaves.", "footnotes": [], "header_rows": [["Purification stage", "Amount of crude proteins (mg/400 g powder)"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Ammonium sulfate precipitation", "col_header": "Amount of crude proteins (mg/400 g powder)", "value": "8120"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Ultrafiltration (under 10 kDa)", "col_header": "Amount of crude proteins (mg/400 g powder)", "value": "963"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "C18-HPLC", "col_header": "Amount of crude proteins (mg/400 g powder)", "value": "5"}]}, {"table_index": 3, "label": "Table 3.", "caption": "MIC and MBC values (µM) of cliotide U1 and gentamicin against different bacterial strains.", "footnotes": [], "header_rows": [["Bacterial strain", "MIC (mM)", "MIC (mM)", "MBC (mM)", "MBC (mM)"], ["Cliotide U1", "Gentamicin", "Cliotide U1", "Gentamicin"]], "longform_cells": [{"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "E. coli ATCC 25922", "col_header": "MIC (mM) / Cliotide U1", "value": "1"}, {"table_index": 3, "row_index": 3, "col_index": 3, "row_label": "E. coli ATCC 25922", "col_header": "MIC (mM) / Gentamicin", "value": "1"}, {"table_index": 3, "row_index": 3, "col_index": 4, "row_label": "E. coli ATCC 25922", "col_header": "MBC (mM) / Cliotide U1", "value": "2"}, {"table_index": 3, "row_index": 3, "col_index": 5, "row_label": "E. coli ATCC 25922", "col_header": "MBC (mM) / Gentamicin", "value": "4"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "S. aureus ATCC 25923", "col_header": "MIC (mM) / Cliotide U1", "value": "4"}, {"table_index": 3, "row_index": 4, "col_index": 3, "row_label": "S. aureus ATCC 25923", "col_header": "MIC (mM) / Gentamicin", "value": "2"}, {"table_index": 3, "row_index": 4, "col_index": 4, "row_label": "S. aureus ATCC 25923", "col_header": "MBC (mM) / Cliotide U1", "value": "8"}, {"table_index": 3, "row_index": 4, "col_index": 5, "row_label": "S. aureus ATCC 25923", "col_header": "MBC (mM) / Gentamicin", "value": "8"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "A. baumannii ATCC 19606", "col_header": "MIC (mM) / Cliotide U1", "value": "2"}, {"table_index": 3, "row_index": 5, "col_index": 3, "row_label": "A. baumannii ATCC 19606", "col_header": "MIC (mM) / Gentamicin", "value": "8"}, {"table_index": 3, "row_index": 5, "col_index": 4, "row_label": "A. baumannii ATCC 19606", "col_header": "MBC (mM) / Cliotide U1", "value": "8"}, {"table_index": 3, "row_index": 5, "col_index": 5, "row_label": "A. baumannii ATCC 19606", "col_header": "MBC (mM) / Gentamicin", "value": "32"}, {"table_index": 3, "row_index": 6, "col_index": 2, "row_label": "P. aeruginosa ATCC 27853", "col_header": "MIC (mM) / Cliotide U1", "value": "1"}, {"table_index": 3, "row_index": 6, "col_index": 3, "row_label": "P. aeruginosa ATCC 27853", "col_header": "MIC (mM) / Gentamicin", "value": "4"}, {"table_index": 3, "row_index": 6, "col_index": 4, "row_label": "P. aeruginosa ATCC 27853", "col_header": "MBC (mM) / Cliotide U1", "value": "2"}, {"table_index": 3, "row_index": 6, "col_index": 5, "row_label": "P. aeruginosa ATCC 27853", "col_header": "MBC (mM) / Gentamicin", "value": "8"}]}, {"table_index": 4, "label": "Table 4.", "caption": "The probability of antimicrobial activity and physicochemical features of cliotide U1.", "footnotes": ["ExPASy server was used to estimate physicochemical parameters (charge, pI, hydrophobicity, Boman index, Aliphatic index, and instability index). In silico tools described in the methodology section were used to predict whether the peptide had antimicrobial properties.", "Abbreviations: SVM, support vector machine; RF, random forest; ANN, artificial neural network;"], "header_rows": [["Name of peptide", "Sequence", "Molecular weight (Da)", "Net charge", "Hydrophobicity (%)", "Boman index", "Aliphatic index", "Instability index", "Score of algorithms", "Score of algorithms", "Score of algorithms"], ["SVM", "RF", "ANA"]], "longform_cells": [{"table_index": 4, "row_index": 3, "col_index": 2, "row_label": "Cliotide U1", "col_header": "Sequence", "value": "LIVAASLVYDFYTWIAKKVALLRIAKKVLYLARNA"}, {"table_index": 4, "row_index": 3, "col_index": 3, "row_label": "Cliotide U1", "col_header": "Molecular weight (Da)", "value": "3995.89"}, {"table_index": 4, "row_index": 3, "col_index": 4, "row_label": "Cliotide U1", "col_header": "Net charge", "value": "5 +"}, {"table_index": 4, "row_index": 3, "col_index": 5, "row_label": "Cliotide U1", "col_header": "Hydrophobicity (%)", "value": "63%"}, {"table_index": 4, "row_index": 3, "col_index": 6, "row_label": "Cliotide U1", "col_header": "Boman index", "value": "0.13"}, {"table_index": 4, "row_index": 3, "col_index": 7, "row_label": "Cliotide U1", "col_header": "Aliphatic index", "value": "153.43"}, {"table_index": 4, "row_index": 3, "col_index": 8, "row_label": "Cliotide U1", "col_header": "Instability index", "value": "16.52"}, {"table_index": 4, "row_index": 3, "col_index": 9, "row_label": "Cliotide U1", "col_header": "Score of algorithms", "value": "0.86"}, {"table_index": 4, "row_index": 3, "col_index": 10, "row_label": "Cliotide U1", "col_header": "Score of algorithms", "value": "0.82"}, {"table_index": 4, "row_index": 3, "col_index": 11, "row_label": "Cliotide U1", "col_header": "Score of algorithms", "value": "AMP"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Cliotide U1, a Novel Antimicrobial Peptide Isolated From Urtica Dioica Leaves", "db_measure": "Discovery: Purified by (NH4)2SO4 precipitation and chromatographic methods. Sequence analysis: APD analysis reveals that this sequence is similar (40%) to Cliotide T10. A: 20%, L: 17%, V=K: 11%. GRAVY: 0.87, mol Wt: 3995.89; mol formula: C193H315N46O44; mol ex coeff: 10020. Activity: active against E. coli ATCC 25922 (MIC 1 uM), S. aureus ATCC 25923 (MIC 4 uM), A. baumannii ATCC 19606 (MIC 2 ug/ml), and P. aeruginosa ATCC 27853 (MIC 1 uM). MBC was 2-fold higher. Peptide stability: not heat stable at 90oC treatment for 1 h. Antimicrobial robustness: activity is lost at pH 2-5. pH-senstive to acidic conditions. activity is human serum-sensitive (25%). In vitro toxicity: human RBC: 18% lysis at 32 uM. HEK293 cells: 94% alive treated at 1-4 uM. Structure: predicted to be helical.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Cliotide U1"}]

Return ONLY the JSON array now (one object per assertion above).