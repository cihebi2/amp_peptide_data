
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
doi__10.3390_molecules21040512

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Percent α-helix of mastoparans in different environments.", "footnotes": ["The r.c. indicates random coil conformation."], "header_rows": [["Buffers", "MP-L", "MP-L", "MP-X(V)", "MP-X(V)", "MP-V1", "MP-V1", "MP-B", "MP-B"], ["[θ]222", "% α-Helix", "[θ]222", "% α-Helix", "[θ]222", "% α-Helix", "[θ]222", "% α-Helix"], ["Water", "−2792.88", "r.c.", "−1828.33", "r.c.", "−1480.77", "r.c.", "−1477.65", "r.c."]], "longform_cells": [{"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "8 mM SDS", "col_header": "MP-L / [θ]222 / −2792.88", "value": "−9450.15"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "8 mM SDS", "col_header": "MP-L / % α-Helix / r.c.", "value": "19.55"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "8 mM SDS", "col_header": "MP-X(V) / [θ]222 / −1828.33", "value": "−11459.40"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "8 mM SDS", "col_header": "MP-X(V) / % α-Helix / r.c.", "value": "25.63"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "8 mM SDS", "col_header": "MP-V1 / [θ]222 / −1480.77", "value": "−9965.03"}, {"table_index": 1, "row_index": 4, "col_index": 7, "row_label": "8 mM SDS", "col_header": "MP-V1 / % α-Helix / r.c.", "value": "21.11"}, {"table_index": 1, "row_index": 4, "col_index": 8, "row_label": "8 mM SDS", "col_header": "MP-B / [θ]222 / −1477.65", "value": "−9963.52"}, {"table_index": 1, "row_index": 4, "col_index": 9, "row_label": "8 mM SDS", "col_header": "MP-B / % α-Helix / r.c.", "value": "21.10"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "40% TFE", "col_header": "MP-L / [θ]222 / −2792.88", "value": "−8896.83"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "40% TFE", "col_header": "MP-L / % α-Helix / r.c.", "value": "17.87"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "40% TFE", "col_header": "MP-X(V) / [θ]222 / −1828.33", "value": "−12974.80"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "40% TFE", "col_header": "MP-X(V) / % α-Helix / r.c.", "value": "30.23"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "40% TFE", "col_header": "MP-V1 / [θ]222 / −1480.77", "value": "−10261.60"}, {"table_index": 1, "row_index": 5, "col_index": 7, "row_label": "40% TFE", "col_header": "MP-V1 / % α-Helix / r.c.", "value": "22.00"}, {"table_index": 1, "row_index": 5, "col_index": 8, "row_label": "40% TFE", "col_header": "MP-B / [θ]222 / −1477.65", "value": "−5615.77"}, {"table_index": 1, "row_index": 5, "col_index": 9, "row_label": "40% TFE", "col_header": "MP-B / % α-Helix / r.c.", "value": "7.93"}]}, {"table_index": 2, "label": "Table 2", "caption": "", "footnotes": [], "header_rows": [["AMP", "antimicrobial peptide"], ["CD", "circular dichroism"], ["MP", "mastoparan"]], "longform_cells": [{"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "TFE", "col_header": "antimicrobial peptide / circular dichroism / mastoparan", "value": "2,2,2-trifluoroethanol"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "Active against S. mutans, S. enterica, and S. aureus (MIC 50 uM), and C. albicans, C. grabrata (MIC 50 uM), and C. neoformans (MIC 0.5 uM).", "db_measure": "Antimicrobial, Antibacterial, Antifungal", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Mastoparan V1 (MP-V1, insects, arthropods, invertebrates, animals)"}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Active against S. mutans, S. enterica, and S. aureus (MIC 50 uM), and C. albicans, C. grabrata (MIC 50 uM), and C. neoformans (MIC 0.5 uM).", "db_measure": "Antimicrobial, Antibacterial, Antifungal", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Mastoparan V1 (MP-V1, insects, arthropods, invertebrates, animals)"}]

Return ONLY the JSON array now (one object per assertion above).