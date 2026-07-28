
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
doi__10.3390_molecules20022775

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Tabulated sequences for the peptides tested including accurate mass data. The doubly charged ion was used for accurate mass measurements, i.e., [M+2H]2+. All peptides are amidated at the C terminus. Lysine (K) and arginine (R) are positively charged side chains.", "footnotes": [], "header_rows": [["Peptide", "Sequence", "Empirical Formula", "Mass Calculated [M+2H]2+", "Accurate Mass Found [M+2H]2+"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Temporin A", "col_header": "Sequence", "value": "FLPLIGRVLSGIL-NH2"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Temporin A", "col_header": "Empirical Formula", "value": "C68H117N17O14"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "Temporin A", "col_header": "Mass Calculated [M+2H]2+", "value": "698.9561"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "Temporin A", "col_header": "Accurate Mass Found [M+2H]2+", "value": "698.9548"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Temporin B", "col_header": "Sequence", "value": "LLPIVGNLLKSLL-NH2"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Temporin B", "col_header": "Empirical Formula", "value": "C67H122N16O15"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Temporin B", "col_header": "Mass Calculated [M+2H]2+", "value": "696.4716"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "Temporin B", "col_header": "Accurate Mass Found [M+2H]2+", "value": "696.4735"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Temporin 1Sa", "col_header": "Sequence", "value": "FLSGIVGMLGKLF-NH2"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Temporin 1Sa", "col_header": "Empirical Formula", "value": "C67H109N15O14S"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "Temporin 1Sa", "col_header": "Mass Calculated [M+2H]2+", "value": "690.9078"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "Temporin 1Sa", "col_header": "Accurate Mass Found [M+2H]2+", "value": "690.9075"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Temporin F", "col_header": "Sequence", "value": "FLPLIGKVLSGIL-NH2"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Temporin F", "col_header": "Empirical Formula", "value": "C68H117N15O14"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "Temporin F", "col_header": "Mass Calculated [M+2H]2+", "value": "684.9531"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "Temporin F", "col_header": "Accurate Mass Found [M+2H]2+", "value": "684.9504"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Temporin L", "col_header": "Sequence", "value": "FVQWFSKFLGRIL-NH2"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Temporin L", "col_header": "Empirical Formula", "value": "C83H122N20O15"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "Temporin L", "col_header": "Mass Calculated [M+2H]2+", "value": "820.9792"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "Temporin L", "col_header": "Accurate Mass Found [M+2H]2+", "value": "820.9792"}]}, {"table_index": 2, "label": "Table 2", "caption": "ED50 for temporins against wild type and mutant L. mexicana promastigotes and amastigotes. Mean ED50 (and range) shown for the values from at least 3 independent experiments performed in triplicate.", "footnotes": [], "header_rows": [["Peptide", "ED50 (µM)", "ED50 (µM)", "ED50 (µM)", "ED50 (µM)"], ["L. mexicana Promastiogte", "L. mexicana Amastigote", "L. mexicana ∆lpg1", "L. mexicana ∆lpg2"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Temporin A", "col_header": "ED50 (µM) / L. mexicana Promastiogte", "value": "8 (6–14)"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Temporin A", "col_header": "ED50 (µM) / L. mexicana Amastigote", "value": "~100"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "Temporin A", "col_header": "ED50 (µM) / L. mexicana ∆lpg1", "value": "11 (8–16)"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "Temporin A", "col_header": "ED50 (µM) / L. mexicana ∆lpg2", "value": "26 (21–39)"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Temporin B", "col_header": "ED50 (µM) / L. mexicana Promastiogte", "value": "38 (24–64)"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Temporin B", "col_header": "ED50 (µM) / L. mexicana Amastigote", "value": ">100"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "Temporin B", "col_header": "ED50 (µM) / L. mexicana ∆lpg1", "value": "39 (28–70)"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "Temporin B", "col_header": "ED50 (µM) / L. mexicana ∆lpg2", "value": "41 (40–41)"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Temporin 1Sa", "col_header": "ED50 (µM) / L. mexicana Promastiogte", "value": "4 (3–13)"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Temporin 1Sa", "col_header": "ED50 (µM) / L. mexicana Amastigote", "value": "42 (35–44)"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "Temporin 1Sa", "col_header": "ED50 (µM) / L. mexicana ∆lpg1", "value": "6 (3–18)"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "Temporin 1Sa", "col_header": "ED50 (µM) / L. mexicana ∆lpg2", "value": "31 (28–35)"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Temporin F", "col_header": "ED50 (µM) / L. mexicana Promastiogte", "value": "14 (10–27)"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "Temporin F", "col_header": "ED50 (µM) / L. mexicana Amastigote", "value": ">100"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "Temporin F", "col_header": "ED50 (µM) / L. mexicana ∆lpg1", "value": "17 (13–29)"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "Temporin F", "col_header": "ED50 (µM) / L. mexicana ∆lpg2", "value": "23 (16–49)"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "Temporin L", "col_header": "ED50 (µM) / L. mexicana Promastiogte", "value": "5 (5–6)"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "Temporin L", "col_header": "ED50 (µM) / L. mexicana Amastigote", "value": "83 (46–93)"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "Temporin L", "col_header": "ED50 (µM) / L. mexicana ∆lpg1", "value": "4 (3–6)"}, {"table_index": 2, "row_index": 7, "col_index": 5, "row_label": "Temporin L", "col_header": "ED50 (µM) / L. mexicana ∆lpg2", "value": "9 (8–12)"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Leishmania mexicana MNYC/BZ/62/M379 (amastigote)", "db_measure": "ED50", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "Temporin-1Tl, Temporin-L"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Leishmania mexicana MNYC/BZ/62/M379 (amastigote)", "db_measure": "ED50", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "Temporin-1Tl, Temporin-L"}]

Return ONLY the JSON array now (one object per assertion above).