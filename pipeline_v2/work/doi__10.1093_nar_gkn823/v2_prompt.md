
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
doi__10.1093_nar_gkn823

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1.", "caption": "Letter keys for searching antimicrobial peptides with chemical modification and peptide binding targets in APD2", "footnotes": [], "header_rows": [["Code", "Chemical modification", "Code", "Binding target"], ["XXA", "C-end amidation", "BBMm", "Membranes"], ["XXC", "Cyclization", "BBB", "Peptide aggregation"], ["XXO", "Oxidation", "BBPP", "Proteins/enzymes"], ["XXP", "Phosphorylation", "BBN", "RNA/DNA"], ["XXD", "d-amino acids", "BBS", "Sugars"], ["XXG", "Glycosylation", "BBL", "Lipopolysaccharides (LPS)"], ["XXL", "Lipidation", "BBII", "Metal ions (e.g. Fe3+)"]], "longform_cells": []}, {"table_index": 2, "label": "Table 2.", "caption": "Frequently used amino acid residues in naturally occurring antimicrobial peptides isolated from bacteria, plants, insects, or frogs", "footnotes": ["The bold face is letter ‘G’ indicates amino acid is common in all life kingdom."], "header_rows": [["Kingdom", "Number of peptides in APD2", "Frequently used amino acids", "Predicted structure"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Bacteria", "col_header": "Number of peptides in APD2", "value": "112"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Bacteria", "col_header": "Frequently used amino acids", "value": "A, G"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Plants", "col_header": "Number of peptides in APD2", "value": "203"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Plants", "col_header": "Frequently used amino acids", "value": "C, G"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "Plants", "col_header": "Predicted structure", "value": "β-Sheet"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Insects", "col_header": "Number of peptides in APD2", "value": "118"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Insects", "col_header": "Frequently used amino acids", "value": "A, G, K"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Frogs", "col_header": "Number of peptides in APD2", "value": "398"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Frogs", "col_header": "Frequently used amino acids", "value": "A, G, K, L"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "Frogs", "col_header": "Predicted structure", "value": "α-Helix"}]}, {"table_index": 3, "label": "Table 3.", "caption": "Minimal inhibitory concentrations (μm) of a few peptides designed based on frequently occurring residues and their combinations", "footnotes": ["aData from reference 26. The region in the LL-37 sequence that corresponds to KR-12 is underlined."], "header_rows": [["Name", "Peptide sequence", "E. coli K12", "MRSA USA-300"]], "longform_cells": [{"table_index": 3, "row_index": 2, "col_index": 2, "row_label": "LL-37", "col_header": "Peptide sequence", "value": "LLGDLLRKSKEKIGKEF KRIVQRIKDFLRNLVPRTES"}, {"table_index": 3, "row_index": 2, "col_index": 3, "row_label": "LL-37", "col_header": "E. coli K12", "value": "40a"}, {"table_index": 3, "row_index": 2, "col_index": 4, "row_label": "LL-37", "col_header": "MRSA USA-300", "value": "–"}, {"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "KR-12", "col_header": "Peptide sequence", "value": "KRIVQRIKDFLR"}, {"table_index": 3, "row_index": 3, "col_index": 3, "row_label": "KR-12", "col_header": "E. coli K12", "value": "40a"}, {"table_index": 3, "row_index": 3, "col_index": 4, "row_label": "KR-12", "col_header": "MRSA USA-300", "value": ">190"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "KL-12", "col_header": "Peptide sequence", "value": "KKLLKKLKKLLK"}, {"table_index": 3, "row_index": 4, "col_index": 3, "row_label": "KL-12", "col_header": "E. coli K12", "value": ">160"}, {"table_index": 3, "row_index": 4, "col_index": 4, "row_label": "KL-12", "col_header": "MRSA USA-300", "value": ">160"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "GLK-19", "col_header": "Peptide sequence", "value": "GLKKLLGKLLKKL GKLLLK"}, {"table_index": 3, "row_index": 5, "col_index": 3, "row_label": "GLK-19", "col_header": "E. coli K12", "value": "10"}, {"table_index": 3, "row_index": 5, "col_index": 4, "row_label": "GLK-19", "col_header": "MRSA USA-300", "value": "160"}, {"table_index": 3, "row_index": 6, "col_index": 2, "row_label": "MULTI-18", "col_header": "Peptide sequence", "value": "GLFDAAKKIVGKLITSLN"}, {"table_index": 3, "row_index": 6, "col_index": 3, "row_label": "MULTI-18", "col_header": "E. coli K12", "value": "80"}, {"table_index": 3, "row_index": 6, "col_index": 4, "row_label": "MULTI-18", "col_header": "MRSA USA-300", "value": ">160"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "Gram-negative bacterium: Escherichia coli K12", "db_measure": "Antimicrobial/Antibacterial/Anti-Gram-/Anticancer labels; E. coli K12 MIC=10 µM in target text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Gram-negative bacterium: Escherichia coli K12", "db_measure": "Antimicrobial/Antibacterial/Anti-Gram-/Anticancer labels; E. coli K12 MIC=10 µM in target text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "Gram-negative bacterium: Escherichia coli K12", "db_measure": "Antimicrobial/Antibacterial/Anti-Gram-/Anticancer labels; E. coli K12 MIC=10 µM in target text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "Gram-negative bacterium: Escherichia coli K12", "db_measure": "Antimicrobial/Antibacterial/Anti-Gram-/Anticancer labels; E. coli K12 MIC=10 µM in target text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DRAMP", "db_subject_text": "Gram-negative bacterium: Escherichia coli K12", "db_measure": "Antimicrobial/Antibacterial/Anti-Gram-/Anticancer labels; E. coli K12 MIC=10 µM in target text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DRAMP", "db_subject_text": "Gram-negative bacterium: Escherichia coli K12", "db_measure": "Function text plus E. coli K12 MIC=10 µM in database target text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DRAMP", "db_subject_text": "Gram-negative bacterium: Escherichia coli K12", "db_measure": "Function text plus E. coli K12 MIC=10 µM in database target text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DRAMP", "db_subject_text": "Gram-negative bacterium: Escherichia coli K12", "db_measure": "Function text plus E. coli K12 MIC=10 µM in database target text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DRAMP", "db_subject_text": "Gram-negative bacterium: Escherichia coli K12", "db_measure": "Function text plus E. coli K12 MIC=10 µM in database target text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DRAMP", "db_subject_text": "Gram-negative bacterium: Escherichia coli K12", "db_measure": "Function text plus E. coli K12 MIC=10 µM in database target text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "dbAMP", "db_subject_text": "E. coli K-12; Staphylococcus aureus USA 300; HIV-1 IIIB", "db_measure": "E. coli K-12 MIC 10 µM; Staphylococcus aureus USA 300 MIC 160 µM; HIV-1 IC50 REP >47.5 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).