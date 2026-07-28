
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
doi__10.1371_journal.pone.0151639

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Sequences of the cyclolipopeptides.", "footnotes": ["a CO-C3H7, butanoyl; CO-C4H9, pentanoyl; CO-nC5H11, hexanoyl; CO-isoC5H11, 4-methylpentanoyl; CO-C6H13, 2-methylhexanoyl; CO-C7H15, octanoyl; CO-C8H17, 4-methyloctanoyl; CO-C11H22OH, 12-hydroxylauroyl; CO-C11H23, lauroyl; CO-C15H31, palmitoyl; CO-C17H33, oleoyl."], "header_rows": [["Peptide", "Structurea", "Peptide", "Structurea"], ["Parent peptide", "Parent peptide", "", ""], ["BPC194", "c(KKLKKFKKLQ)", "", ""], ["Cyclolipopeptides with a different acyl chain at Lys5", "Cyclolipopeptides with a different acyl chain at Lys5", "Cyclolipopeptides with a different acyl chain at Lys5", "Cyclolipopeptides with a different acyl chain at Lys5"], ["BPC498", "c(KKLKK(CO-C7H15)FKKLQ)", "BPC592", "c(KKLKK(CO-C6H13)FKKLQ)"], ["BPC500", "c(KKLKK(CO-C3H7)FKKLQ)", "BPC594", "c(KKLKK(CO-C8H17)FKKLQ)"], ["BPC526", "c(KKLKK(CO-C4H9)FKKLQ)", "BPC530", "c(KKLKK(CO-C11H23)FKKLQ)"], ["BPC504", "c(KKLKK(CO-isoC5H11)FKKLQ)", "BPC524", "c(KKLKK(CO-C11H22OH)FKKLQ)"], ["BPC528", "c(KKLKK(CO-nC5H11)FKKLQ)", "BPC502", "c(KKLKK(CO-C15H31)FKKLQ)"], ["BPC596", "c(KKLKK(LK-CO-nC5H11)FKKLQ)", "BPC622", "c(KKLKK(CO-C17H33)FKKLQ)"], ["Cyclolipopeptides with an acyl chain at a different Lys", "Cyclolipopeptides with an acyl chain at a different Lys", "Cyclolipopeptides with an acyl chain at a different Lys", "Cyclolipopeptides with an acyl chain at a different Lys"], ["BPC582", "c(KKLKKFKK(CO-nC5H11)LQ)", "BPC708", "c(KK(CO-C3H7)LKKFKKLQ)"], ["BPC584", "c(KKLKKFK(CO-nC5H11)KLQ)", "BPC590", "c(K(CO-nC5H11)KLKKFKKLQ)"], ["BPC586", "c(KKLK(CO-nC5H11)KFKKLQ)", "BPC710", "c(K(CO-C3H7)KLKKFKKLQ)"], ["BPC588", "c(KK(CO-nC5H11)LKKFKKLQ)", "", ""], ["Cyclolipopeptides with a D-Phe", "Cyclolipopeptides with a D-Phe", "Cyclolipopeptides with a D-Phe", "Cyclolipopeptides with a D-Phe"], ["BPC712", "c(KKLKK(CO-C3H7)fKKLQ)", "BPC668", "c(KKLKK(CO-C7H15)fKKLQ)"], ["BPC726", "c(KKLKK(LK-CO-C3H7)fKKLQ)", "BPC714", "c(KK(CO-C3H7)LKKfKKLQ)"], ["BPC624", "c(KKLKK(CO-nC5H11)fKKLQ)", "BPC680", "c(KK(CO-nC5H11)LKKfKKLQ)"], ["BPC626", "c(KKLKK(CO-isoC5H11)fKKLQ)", "BPC716", "c(K(CO-C3H7)KLKKfKKLQ)"], ["BPC674", "c(KKLKK(LK-CO-nC5H11)fKKLQ)", "BPC686", "c(K(CO-nC5H11)KLKKfKKLQ)"], ["Cyclolipopeptides with a D-Lys", "Cyclolipopeptides with a D-Lys", "Cyclolipopeptides with a D-Lys", ""], ["BPC702", "c(KKLKk(CO-C3H7)FKKLQ)", "BPC666", "c(KKLKk(CO-C7H15)FKKLQ)"], ["BPC724", "c(KKLKk(LK-CO-C3H7)FKKLQ)", "BPC678", "c(Kk(CO-nC5H11)LKKFKKLQ)"], ["BPC628", "c(KKLKk(CO-nC5H11)FKKLQ)", "BPC704", "c(Kk(CO-C3H7)LKKFKKLQ)"], ["BPC630", "c(KKLKk(CO-isoC5H11)FKKLQ)", "BPC684", "c(k(CO-nC5H11)KLKKFKKLQ)"], ["BPC672", "c(KKLKk(LK-CO-nC5H11)FKKLQ)", "BPC706", "c(k(CO-C3H7)KLKKFKKLQ)"], ["Cyclolipopeptides with a D-Phe and a D-Lys", "Cyclolipopeptides with a D-Phe and a D-Lys", "Cyclolipopeptides with a D-Phe and a D-Lys", ""], ["BPC632", "c(KKLKk(CO-nC5H11)fKKLQ)", "BPC634", "c(KKLKk(CO-isoC5H11)fKKLQ)"], ["Cyclolipopeptides with a His", "Cyclolipopeptides with a His", "Cyclolipopeptides with a His", ""], ["BPC718", "c(KKLKK(CO-C3H7)HKKLQ)", "BPC670", "c(KKLKK(CO-C7H15)HKKLQ)"], ["BPC728", "c(KKLKK(LK-CO-C3H7)HKKLQ)", "BPC682", "c(KK(CO-nC5H11)LKKHKKLQ)"], ["BPC636", "c(KKLKK(CO-nC5H11)HKKLQ)", "BPC720", "c(KK(CO-C3H7)LKKHKKLQ)"], ["BPC638", "c(KKLKK(CO-isoC5H11)HKKLQ)", "BPC688", "c(K(CO-nC5H11)KLKKHKKLQ)"], ["BPC676", "c(KKLKK(LK-CO-nC5H11)HKKLQ)", "BPC722", "c(K(CO-C3H7)KLKKHKKLQ)"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Xanthomonas campestris pv. Vesicatoria 2133-2", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Xanthomonas campestris pv. Vesicatoria 2133-2", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Xanthomonas campestris pv. Vesicatoria 2133-2", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Xanthomonas campestris pv. Vesicatoria 2133-2", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Xanthomonas campestris pv. Vesicatoria 2133-2", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Xanthomonas campestris pv. Vesicatoria 2133-2", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Xanthomonas campestris pv. Vesicatoria 2133-2", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Xanthomonas campestris pv. Vesicatoria 2133-2", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Xanthomonas campestris pv. Vesicatoria 2133-2", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Xanthomonas campestris pv. Vesicatoria 2133-2", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).