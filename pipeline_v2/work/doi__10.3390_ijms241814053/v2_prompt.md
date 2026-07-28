
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
doi__10.3390_ijms241814053

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Physiochemical properties of Octominin II.", "footnotes": [], "header_rows": [["Property", "Octominin(Value/Units)", "Octominin II(Value/Units)", "Measurement"], ["Net charge", "+5.00", "+2.46", "Sum of the charges of a peptide amino acid"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Isoelectric point", "col_header": "Octominin(Value/Units) / +5.00", "value": "12.48"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Isoelectric point", "col_header": "Octominin II(Value/Units) / +2.46", "value": "11.66"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Isoelectric point", "col_header": "Measurement / Sum of the charges of a peptide amino acid", "value": "pH value that a molecule carries no or neutral net electrical charge"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Aliphatic index", "col_header": "Octominin(Value/Units) / +5.00", "value": "114.78"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Aliphatic index", "col_header": "Octominin II(Value/Units) / +2.46", "value": "134.38"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "Aliphatic index", "col_header": "Measurement / Sum of the charges of a peptide amino acid", "value": "Relative volume of a peptide occupied by the aliphatic side chains"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Instability index", "col_header": "Octominin(Value/Units) / +5.00", "value": "78.99"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Instability index", "col_header": "Octominin II(Value/Units) / +2.46", "value": "12.51"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "Instability index", "col_header": "Measurement / Sum of the charges of a peptide amino acid", "value": "Stability of a peptide"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Boman index", "col_header": "Octominin(Value/Units) / +5.00", "value": "1.86 kcal/mol"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Boman index", "col_header": "Octominin II(Value/Units) / +2.46", "value": "−0.28 kcal/mol"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "Boman index", "col_header": "Measurement / Sum of the charges of a peptide amino acid", "value": "Potential peptide-interaction of a peptide"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Hydrophobicity index", "col_header": "Octominin(Value/Units) / +5.00", "value": "0.43"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "Hydrophobicity index", "col_header": "Octominin II(Value/Units) / +2.46", "value": "0.46"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "Hydrophobicity index", "col_header": "Measurement / Sum of the charges of a peptide amino acid", "value": "Relative solubility of the peptide"}]}, {"table_index": 2, "label": "Table 2", "caption": "Gene-specific primers of C. albicans used in this study.", "footnotes": [], "header_rows": [["Name of the Gene", "Forward Sequence (5′-3′)", "Reverse Sequence (3′-5′)", "Accession Number"], ["Multidrug resistance protein-CDR1", "ACAATACAAGACCAGCATCTCC", "AGACCCATTACAAGTTGACCG", "XM_718116.2"], ["Chromatin-silencing transcriptional regulator-TUP1", "ATACATTGTCAACCCCACCC", "AGTCTTTGGAGAACGCTGG", "XM_713975.2"], ["ADP-ribosylation factor GTPase-activating, protein encoding gene/ARF-GAP-encoding gene AGE3", "TCCATGATCCAGAAACTCGTAG", "ACTCCACACATTCTAAACAAATG", "XM_708684.2"], ["Beta-1,3-glucan synthase catalytic subunit-GSC1", "ACTGCTTACAACTCCCCAAC", "CCATTCGAAAAGTGTGGCAAG", "XM_716336.2"], ["Secreted aspartyl proteinase-2-SAP2", "CAAGGAGTCATTGCTAAGAATGC", "AGCATTATCAACCCCACCG", "XM_705955.2"], ["Secreted aspartyl proteinase-9-SAP9", "CATCTTCATCTGGCACCTCTAC", "CGAAAGCAACAACCCATACAC", "XM_707636.2"], ["Actin 1", "TGAAGCCCAATCCAAAAGAGG", "TTTCCATATCGTCCCAGTTGG", "XM_019475182.1"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Candida albicans", "db_measure": "MBIC50 50 µg/ml", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Chrysophsin-2 (3-20), Octominin II"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Candida albicans", "db_measure": "MBEC50 120 µg/ml", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Chrysophsin-2 (3-20), Octominin II"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Candida albicans", "db_measure": "MBIC50 50 µg/ml", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_21413"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Candida albicans", "db_measure": "MBEC50 120 µg/ml", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_21413"}, {"assertion_index": 4, "database": "APD6", "db_subject_text": "Antifungal Efficacy of Antimicrobial Peptide Octominin II against Candida albicans", "db_measure": "Unknown", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "AP03722"}]

Return ONLY the JSON array now (one object per assertion above).