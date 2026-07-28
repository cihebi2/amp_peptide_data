
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
doi__10.1038_s41598-017-04274-8

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Anti-HCV peptides in our screen.", "footnotes": [], "header_rows": [["Peptides", "Sequence (15 aa)", "Position (aa-aa)", "AVPid", "Sequence"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "E1-14", "col_header": "Sequence (15 aa)", "value": "GLRTHIDMVVMSATF"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "E1-14", "col_header": "Position (aa-aa)", "value": "257–271"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "E1-17", "col_header": "Sequence (15 aa)", "value": "CSALYVGDLCGGVML"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "E1-17", "col_header": "Position (aa-aa)", "value": "272–286"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "E1-17", "col_header": "AVPid", "value": "AVP1461"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "E1-17", "col_header": "Sequence", "value": "GSATLCSALYVGDLCGSV"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "E1-18", "col_header": "Sequence (15 aa)", "value": "VGDLCGGVMLAAQVF"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "E1-18", "col_header": "Position (aa-aa)", "value": "277–291"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "E1-18", "col_header": "AVPid", "value": "AVP1462"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "E1-18", "col_header": "Sequence", "value": "ALYVGDLCGSVFLVGQLF"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "E1-27", "col_header": "Sequence (15 aa)", "value": "MMMNWSPTATMILAY"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "E1-27", "col_header": "Position (aa-aa)", "value": "322–336"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "E1-27", "col_header": "AVPid", "value": "AVP1469"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "E1-27", "col_header": "Sequence", "value": "MMNWSPTAALVVAQLLRI"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "E1-28", "col_header": "Sequence (15 aa)", "value": "SPTATMILAYVMRVP"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "E1-28", "col_header": "Position (aa-aa)", "value": "327–341"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "E1-28", "col_header": "AVPid", "value": "AVP1469"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "E1-28", "col_header": "Sequence", "value": "MMNWSPTAALVVAQLLRI"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "E2-31", "col_header": "Sequence (15 aa)", "value": "VCGPVYCFTPSPVVV"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "E2-31", "col_header": "Position (aa-aa)", "value": "504–518"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "E2-42", "col_header": "Sequence (15 aa)", "value": "QGSWFGCTWMNSTGF"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "E2-42", "col_header": "Position (aa-aa)", "value": "548–562"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "E2-43", "col_header": "Sequence (15 aa)", "value": "FGCTWMNSTGFTKTC"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "E2-43", "col_header": "Position (aa-aa)", "value": "552–566"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "E2-60", "col_header": "Sequence (15 aa)", "value": "WHYPCTVNFTIFKIR"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "E2-60", "col_header": "Position (aa-aa)", "value": "620–634"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "E2-72", "col_header": "Sequence (15 aa)", "value": "PLLHSTTEWAILPCT"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "E2-72", "col_header": "Position (aa-aa)", "value": "668–682"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "E2-78", "col_header": "Sequence (15 aa)", "value": "GLLHLHQNIVDVQYM"}, {"table_index": 1, "row_index": 12, "col_index": 3, "row_label": "E2-78", "col_header": "Position (aa-aa)", "value": "692–706"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "E2-79", "col_header": "Sequence (15 aa)", "value": "LHQNIVDVQYMYGLS"}, {"table_index": 1, "row_index": 13, "col_index": 3, "row_label": "E2-79", "col_header": "Position (aa-aa)", "value": "696–710"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "[Ref.28638089]HCV(Hepatitis C virus): inhibition of HCVcc infection in Huh7.5/CD81 cells (IC50=1~5nM)", "db_measure": "Antimicrobial, Antiviral; Mechanism: Inhibits HCV entry at the post-attachment step and block cell-to-cell transmission, inhibit the late steps of HCV life cycle, such as HCV package and release.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "[Ref.28638089]HCV(Hepatitis C virus): inhibition of HCVcc infection in Huh7.5/CD81 cells (IC50=1~5nM)", "db_measure": "Antimicrobial, Antiviral; Mechanism: Inhibits HCV entry at the post-attachment step and block cell-to-cell transmission, inhibit the late steps of HCV life cycle, such as HCV package and release.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "[Ref.28638089]HCV(Hepatitis C virus): inhibition of HCVcc infection in Huh7.5/CD81 cells (IC50=1~5nM)", "db_measure": "Antimicrobial, Antiviral; Mechanism: Inhibits HCV entry at the post-attachment step and block cell-to-cell transmission, inhibit the late steps of HCV life cycle, such as HCV package and release.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "[Ref.28638089]HCV(Hepatitis C virus): inhibition of HCVcc infection in Huh7.5/CD81 cells (IC50=1~5nM)", "db_measure": "Antimicrobial, Antiviral; Mechanism: Inhibits HCV entry at the post-attachment step and block cell-to-cell transmission, inhibit the late steps of HCV life cycle, such as HCV package and release.", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "CAMP", "db_subject_text": "Hepatitis C virus (HCV)[IC50 I = 0.005 microM], Human hepatocellular carcinoma Huh7.5/CD81[50% Cell death >0.1 microM]", "db_measure": "text; Gram+; Antiviral; Has anticancer activity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "CAMP", "db_subject_text": "Hepatitis C virus (HCV)[IC50 I = 0.005 microM], Human hepatocellular carcinoma Huh7.5/CD81[50% Cell death >0.1 microM]", "db_measure": "text; Gram+; Antiviral; Has anticancer activity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "CAMP", "db_subject_text": "Hepatitis C virus (HCV)[IC50 I = 0.006 microM], Human hepatocellular carcinoma Huh7.5/CD81[50% Cell death >0.1 microM]", "db_measure": "text; Gram+; Antiviral; Has anticancer activity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "CAMP", "db_subject_text": "Hepatitis C virus (HCV)[IC50 I = 0.007 microM], Human hepatocellular carcinoma Huh7.5/CD81[50% Cell death >0.1 microM]", "db_measure": "text; Gram+; Antiviral; Has anticancer activity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).