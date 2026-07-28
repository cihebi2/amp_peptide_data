
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
doi__10.18632_oncotarget.6794

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "dbAMP", "db_subject_text": "Acute myeloid leukemia AML-2 (100% Killing=10μM)\nAcute myeloid leukemia AML-3 (90% Killing=10μM)\nHuman cervical carcinoma HeLa (100% Killing=50μM)\nHuman colon adenocarcinoma HCT 116 (30% Killing=10μM)\nHuman colon adenocarcinoma HCT 116-/-p53 (30% Killing=10μM)", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "dbAMP", "db_subject_text": "Human colon adenocarcinoma HCT 116-/-p53\nHuman colon adenocarcinoma HCT 116\nHuman cervical carcinoma HeLa\nAcute myeloid leukemia AML-3\nAcute myeloid leukemia AML-2", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "dbAMP", "db_subject_text": "Human breast adenocarcinoma MCF-7 (10% Killing=10μM)\nHuman breast adenocarcinoma MCF-7 (50% Killing=50μM)\nHuman breast adenocarcinoma MDA-MB-231 (40% Killing=10μM)\nHuman breast adenocarcinoma MDA-MB-231 (90% Killing=50μM)\nHuman multiple myeloma OPM-2 (30% Killing=50μM)", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "dbAMP", "db_subject_text": "Human breast adenocarcinoma MDA-MB-231\nHuman breast adenocarcinoma MCF-7", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "dbAMP", "db_subject_text": "Human colon adenocarcinoma HCT 116 (78% Killing=10μM)\nHuman colon adenocarcinoma HCT 116 (100% Killing=50μM)\nHuman colon adenocarcinoma HCT 116-/-p53 (65% Killing=10μM)\nHuman colon adenocarcinoma HCT 116-/-p53 (100% Killing=50μM)", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "dbAMP", "db_subject_text": "Human colon adenocarcinoma HCT 116 (100% Killing=10μM)\nHuman colon adenocarcinoma HCT 116-/-p53 (100% Killing=10μM)", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "dbAMP", "db_subject_text": "Human breast adenocarcinoma MCF-7 (18% Killing=10μM)\nHuman breast adenocarcinoma MCF-7 (30% Killing=100μM)\nHuman breast adenocarcinoma MDA-MB-231 (10% Killing=100μM)\nHuman multiple myeloma OPM-2 (0% Killing=50μM)", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "dbAMP", "db_subject_text": "Human breast adenocarcinoma MCF-7 (45% Killing=10μM)\nHuman breast adenocarcinoma MCF-7 (100% Killing=50μM)\nHuman breast adenocarcinoma MDA-MB-231 (78% Killing=10μM)\nHuman breast adenocarcinoma MDA-MB-231 (100% Killing=50μM)", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "dbAMP", "db_subject_text": "Escherichia coli ATCC 25922 (MIC=>128μM)\nEscherichia coli ATCC 25922 (MBC=>128μM)\nPseudomonas aeruginosa ATCC 27853 (MIC=>128μM)\nPseudomonas aeruginosa ATCC 27853 (MBC=>128μM)\nStaphylococcus aureus ATCC 29213 (MIC=128μM)\nStaphylococcus aureus ATCC 29213 (MBC=>128μM)\nEnterococcus faecalis (MIC=>128μM)\nEnterococcus faecalis (MBC=>128μM)\nEscherichia coli ATCC BAA-2523 (MIC=>128μM)\nEscherichia coli ATCC BAA-2523 (MBC=>128μM)\nPseudomonas aeruginosa (MIC=>128μM)\nPseudomonas aeruginosa (MBC=>128μM)\nStaphylococcus aureus ATCC 43300 (MIC=128μM)\nStaphylococcus aureus ATCC 43300 (MBC=>128μM)\nEnterococcus faecalis VR (MIC=>128μM)\nEnterococcus faecalis VR (MBC=>128μM)\nHuman breast adenocarcinoma MDA-MB-231 (5% Killing=100μM)", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "dbAMP", "db_subject_text": "Human multiple myeloma OPM-2 (78% Killing=10μM)\nHuman multiple myeloma OPM-2 (100% Killing=50μM)\nHuman breast adenocarcinoma MDA-MB-231 (100% Killing=10μM)", "db_measure": "NO", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).