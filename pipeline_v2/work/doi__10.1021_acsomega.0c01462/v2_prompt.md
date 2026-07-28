
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
doi__10.1021_acsomega.0c01462

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Name, Sequence, Molecular Mass, and Charge of the Palmitoylated Analogues and their Parent Peptides", "footnotes": [], "header_rows": [["name", "sequence", "molecular mass (Da)", "charge"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "α-MSH", "col_header": "sequence", "value": "Ac-S1-Y2-S3-M4-E5-H6-F7-R8-W9-G10-K11-P12-V13-NH2"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "α-MSH", "col_header": "molecular mass (Da)", "value": "1664.88"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "α-MSH", "col_header": "charge", "value": "+1"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "α-MSH(6-13)", "col_header": "sequence", "value": "Ac-H6-F7-R8-W9-G10-K11-P12-V13-NH2"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "α-MSH(6-13)", "col_header": "molecular mass (Da)", "value": "1067.25"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "α-MSH(6-13)", "col_header": "charge", "value": "+2"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "α-MSH(11-13)", "col_header": "sequence", "value": "Ac-K11-P12-V13-NH2"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "α-MSH(11-13)", "col_header": "molecular mass (Da)", "value": "383.49"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "α-MSH(11-13)", "col_header": "charge", "value": "+1"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Pal-α-MSH(6-13)", "col_header": "sequence", "value": "palmitoyl-H6-F7-R8-W9-G10-K11-P12-V13-NH2"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Pal-α-MSH(6-13)", "col_header": "molecular mass (Da)", "value": "1263.77"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "Pal-α-MSH(6-13)", "col_header": "charge", "value": "+2"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Pal-α-MSH(11-13)", "col_header": "sequence", "value": "palmitoyl-K11-P12-V13-NH2"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Pal-α-MSH(11-13)", "col_header": "molecular mass (Da)", "value": "579.9"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "Pal-α-MSH(11-13)", "col_header": "charge", "value": "+1"}]}, {"table_index": 2, "label": "Table 2", "caption": "Minimum Inhibitory Concentration (MIC) Values of the Palmitoylated Peptides against MSSA ATCC 29213 and MRSA ATCC 33591", "footnotes": [], "header_rows": [["", "Mueller-Hinton broth", "Mueller-Hinton broth", "tryptic soy broth", "tryptic soy broth"], ["peptide/antibiotics", "MSSA", "MRSA", "MSSA", "MRSA"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Pal-α-MSH(6-13)", "col_header": "Mueller-Hinton broth / MSSA", "value": ">45.45 μM"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Pal-α-MSH(6-13)", "col_header": "Mueller-Hinton broth / MRSA", "value": ">45.45 μM"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "Pal-α-MSH(6-13)", "col_header": "tryptic soy broth / MSSA", "value": ">45.45 μM"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "Pal-α-MSH(6-13)", "col_header": "tryptic soy broth / MRSA", "value": ">45.45 μM"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Pal-α-MSH(11-13)", "col_header": "Mueller-Hinton broth / MSSA", "value": "11.36 μM"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Pal-α-MSH(11-13)", "col_header": "Mueller-Hinton broth / MRSA", "value": "11.36 μM"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "Pal-α-MSH(11-13)", "col_header": "tryptic soy broth / MSSA", "value": "11.36 μM"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "Pal-α-MSH(11-13)", "col_header": "tryptic soy broth / MRSA", "value": "11.36 μM"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "vancomycin", "col_header": "Mueller-Hinton broth / MSSA", "value": "0.48 μM"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "vancomycin", "col_header": "Mueller-Hinton broth / MRSA", "value": "0.48−0.96 μM"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "vancomycin", "col_header": "tryptic soy broth / MSSA", "value": "0.48 μM"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "vancomycin", "col_header": "tryptic soy broth / MRSA", "value": "0.48−0.96 μM"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "oxacillin", "col_header": "Mueller-Hinton broth / MSSA", "value": "<0.8 μM (<0.35 μg/mL)"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "oxacillin", "col_header": "Mueller-Hinton broth / MRSA", "value": "134.1–268.3 μM (56.8–113.6 μg/mL)"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "oxacillin", "col_header": "tryptic soy broth / MSSA", "value": "<0.8 μM (<0.35 μg/mL)"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "oxacillin", "col_header": "tryptic soy broth / MRSA", "value": "134.1–268.3 μM (56.8–113.6 μg/mL)"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "CAMP", "db_subject_text": "Escherichia coli UB1005[MIC >2000 microg/ml], Staphylococcus aureus SAP 0017[MIC >2000 microg/ml], Candida albicans 105[MIC >2000 microg/ml], Cutibacterium acnes[MIC >2000 microg/ml], Escherichia coli UB1005[MIC = 128 microg/ml], Staphylococcus aureus SAP 0017[MIC = 8 microg/ml], Candida albicans 105[MIC = 16 microg/ml], Cutibacterium acnes[MIC = 01-2microg/ml], Staphylococcus aureus ATCC 29213[MIC = 11.36 microM], Staphylococcus aureus ATCC 33591[MIC = 11.36 microM], Cutibacterium acnes[MIC = 1", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Melanotropin alpha"}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "Staphylococcus aureus ATCC 29213[MIC >45.45 microM], Staphylococcus aureus ATCC 33591[MIC >45.45 microM]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Melanotropin alpha"}]

Return ONLY the JSON array now (one object per assertion above).