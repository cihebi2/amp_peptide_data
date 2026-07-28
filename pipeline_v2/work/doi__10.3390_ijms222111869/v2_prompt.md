
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
doi__10.3390_ijms222111869

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Sequences of 25-HC-modified EK1 peptides.", "footnotes": ["Note: The sequence of EK1 is SLDQINVTFLDLEYEMKKLEEAIKKLEESYIDLKEL; 25-HC is attached to the C terminus by different linkers."], "header_rows": [["Name", "Sequence", "MW"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "EK1P4HC", "col_header": "Sequence", "value": "SLDQINVTFLDLEYEMKKLEEAIKKLEESYIDLKELGSGSG-PEG4-25-HC"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "EK1P4HC", "col_header": "MW", "value": "5453"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "EK1P8HC", "col_header": "Sequence", "value": "SLDQINVTFLDLEYEMKKLEEAIKKLEESYIDLKELGSGSG-PEG8-25-HC"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "EK1P8HC", "col_header": "MW", "value": "5689"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "EK1P12HC", "col_header": "Sequence", "value": "SLDQINVTFLDLEYEMKKLEEAIKKLEESYIDLKELGSGSG-PEG12-25-HC"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "EK1P12HC", "col_header": "MW", "value": "5865"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "EK1P24HC", "col_header": "Sequence", "value": "SLDQINVTFLDLEYEMKKLEEAIKKLEESYIDLKELGSGSG-PEG24-25-HC"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "EK1P24HC", "col_header": "MW", "value": "6393"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:##SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=0.8 ¦ÌM);##SARS-CoV-2 B.1.1.7 (Alpha):inhibition of Pseudoviruse infection in Caco2 cells(IC50=2.28 ¦ÌM);##SARS-CoV-2 B.1.351 (Beta):inhibition of Pse", "db_measure": "The peptide targets two different sites when mediating virus¨Ccell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=3.7 ¦ÌM).", "db_measure": "The peptide targets two different sites when mediating virus¨Ccell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=5.2 ¦ÌM).", "db_measure": "The peptide targets two different sites when mediating virus¨Ccell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=10.3 ¦ÌM).", "db_measure": "The peptide targets two different sites when mediating virus¨Ccell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:##SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=0.8 μM);##SARS-CoV-2 B.1.1.7 (Alpha):inhibition of Pseudoviruse infection in Caco2 cells(IC50=2.28 μM);##SARS-CoV-2 B.1.351 (Beta):inhibition of Pseud", "db_measure": "The peptide targets two different sites when mediating virus–cell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=3.7 μM).", "db_measure": "The peptide targets two different sites when mediating virus–cell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=5.2 μM).", "db_measure": "The peptide targets two different sites when mediating virus–cell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=10.3 μM).", "db_measure": "The peptide targets two different sites when mediating virus–cell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:##SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=0.8 μM);##SARS-CoV-2 B.1.1.7 (Alpha):inhibition of Pseudoviruse infection in Caco2 cells(IC50=2.28 μM);##SARS-CoV-2 B.1.351 (Beta):inhibition of Pseud", "db_measure": "The peptide targets two different sites when mediating virus–cell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=3.7 μM).", "db_measure": "The peptide targets two different sites when mediating virus–cell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=5.2 μM).", "db_measure": "The peptide targets two different sites when mediating virus–cell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DRAMP", "db_subject_text": "[Ref.34769299]Virus:SARS-CoV-2:inhibition of Pseudoviruse infection in Caco2 cells(IC50=10.3 μM).", "db_measure": "The peptide targets two different sites when mediating virus–cell fusion,which are blocking viral 6-HB formation and reducing the membrane cholesterol level.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).