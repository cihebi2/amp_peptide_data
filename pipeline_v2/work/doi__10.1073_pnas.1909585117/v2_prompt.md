
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
doi__10.1073_pnas.1909585117

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Pseudomonas aeruginosa CICC 21625", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "VCKRWKKWKRKWKKWCV", "db_claimed_peptide_name": "Cathelicidin-BF-15-a4, ZY4"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Pseudomonas aeruginosa CMCC 10104", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "VCKRWKKWKRKWKKWCV", "db_claimed_peptide_name": "Cathelicidin-BF-15-a4, ZY4"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Pseudomonas aeruginosa", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "VCKRWKKWKRKWKKWCV", "db_claimed_peptide_name": "Cathelicidin-BF-15-a4, ZY4"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Acinetobacter baumannii CICC 22933", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "VCKRWKKWKRKWKKWCV", "db_claimed_peptide_name": "Cathelicidin-BF-15-a4, ZY4"}, {"assertion_index": 4, "database": "CAMP", "db_subject_text": "Escherichia coli ATCC 25922[MIC = 4.6 microM], Bacillus subtilis[MIC = 9.2 microM], Staphylococcus aureus ATCC 2592[MIC = 9.2 microM], Candida albicans SC5314[MIC = 4.6 microM], Listeria monocytogenes[MIC = 16 microg/ml], Staphylococcus aureus BNCC 186335[MIC = 4 microg/ml], Staphylococcus aureus[MIC = 8 microg/ml], Pseudomonas aeruginosa BNCC 125486[MIC = 8 microg/ml], Escherichia coli BNCC 133264[MIC = 2 microg/ml], Escherichia coli[MIC = 16 microg/ml], Listeria monocytogenes[MIC = 4 microg/ml], Staphylococcus aureus BNCC 186335[MIC = 2 microg/ml], Staphylococcus aureus[MIC = 2 microg/ml], Pseudomonas aeruginosa BNCC 125486[MIC = 16 microg/ml], Escherichia coli[MIC = 8 microg/ml], Staphylococcus aureus[MIC = 4 microg/ml], Escherichia coli BNCC 133264[MIC = 4 microg/ml], Escherichia coli BNCC 133264[MIC = 8 microg/ml], Listeria monocytogenes[MIC = 2 microg/ml], Listeria monocytogenes[MIC = 8 microg/ml]", "db_measure": "Gram+, Gram-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "LS-Cathelicidin-BF-15-a1-6"}, {"assertion_index": 5, "database": "CAMP", "db_subject_text": "Escherichia coli ATCC 25922[MIC = 2.1 microM], Bacillus subtilis[MIC = 4.3 microM], Staphylococcus aureus ATCC 2592[MIC = 8.5 microM], Candida albicans SC5314[MIC = 4.3 microM]", "db_measure": "Gram+, Gram-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Cathelicidin-BF-15-a2"}, {"assertion_index": 6, "database": "CAMP", "db_subject_text": "Escherichia coli ATCC 25922[MIC = 1.6 microM], Bacillus subtilis[MIC = 2.8 microM], Staphylococcus aureus ATCC 2592[MIC = 2.8 microM], Candida albicans SC5314[MIC = 2.8 microM]", "db_measure": "Gram+, Gram-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Cathelicidin-BF-15-a3"}, {"assertion_index": 7, "database": "CAMP", "db_subject_text": "Escherichia coli ATCC 25922[MIC = 1.5 microM], Bacillus subtilis[MIC = 2 microM], Staphylococcus aureus ATCC 2592[MIC = 2 microM], Candida albicans SC5314[MIC = 2 microM], Pseudomonas aeruginosa CICC 21625[MIC = 1.9 microM], Pseudomonas aeruginosa CMCC 10104[MIC = 1.9 microM], Pseudomonas aeruginosa[MIC = 0.8-1.3 microM], Acinetobacter baumannii CICC 22933[MIC = 1.9 microM], Acinetobacter baumannii[MIC = 1.9 microM]", "db_measure": "Gram+, Gram-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Cathelicidin-BF-15-a4, ZY4"}]

Return ONLY the JSON array now (one object per assertion above).