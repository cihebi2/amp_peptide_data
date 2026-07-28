
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
doi__10.1038_ki.2012.410

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "The antimicrobial activity of RNase 7 against common uropathogensTo evaluate the antimicrobial activity of RNase 7 against uropathogenic bacteria, uropathogens were incubated with serial dilutions of recombinant RNase 7 ranging from 0.1–10 μM. Repeat testing was performed on all bacterial isolates in triplicate.", "footnotes": ["Minimal inhibitory concentration (MIC) necessary to prevent growth of 90% of the bacteria (90% lethal dose [LD90]).", "Minimal bactericidal concentration (MBC) necessary to kill ≥99.9% of the bacteria."], "header_rows": [["Strain", "MIC(μM)a", "MBC(μM)b"], ["Gram-Negative Bacteria", "", ""]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Escherichia coli PEDUTI-89", "col_header": "MIC(μM)a", "value": "0.5 – 1.0"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Escherichia coli PEDUTI-89", "col_header": "MBC(μM)b", "value": "1.25 – 2.5"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Pseudomonas aeruginosa PEDUTI-961", "col_header": "MIC(μM)a", "value": "0.6 – 0.8"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Pseudomonas aeruginosa PEDUTI-961", "col_header": "MBC(μM)b", "value": "1.25 – 2.5"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Klebsiella pneumoniae PEDUTI-965", "col_header": "MIC(μM)a", "value": "0.2 – 0.4"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Klebsiella pneumoniae PEDUTI-965", "col_header": "MBC(μM)b", "value": "0.8–1.25"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Proteus mirabilis PEDUTI-971", "col_header": "MIC(μM)a", "value": "0.3–0.6"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Proteus mirabilis PEDUTI-971", "col_header": "MBC(μM)b", "value": "1.0–1.25"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Enterococcus faecalis PEDUTI-983", "col_header": "MIC(μM)a", "value": "0.1 – 0.2"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "Enterococcus faecalis PEDUTI-983", "col_header": "MBC(μM)b", "value": "0.5 – 0.75"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Staphylococcus saprophyticus PEDUTI-989", "col_header": "MIC(μM)a", "value": "0.1 – 0.2"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "Staphylococcus saprophyticus PEDUTI-989", "col_header": "MBC(μM)b", "value": "0.5 – 0.75"}]}, {"table_index": 2, "label": "Table 2", "caption": "Urinary antimicrobial peptide concentrations during sterility and infectionPreviously defined urinary AMP concentrations for human alpha defensin 5 (HD5), human beta defensin 1 (hBD-1), cathelicidin (LL-37), and RNase 7. HD5 is not detectable (N.D.) in sterile urine.", "footnotes": [], "header_rows": [["AMP", "Sterile Urine", "Infected Urine"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "HD5", "col_header": "Sterile Urine", "value": "N.D.9"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "HD5", "col_header": "Infected Urine", "value": "110.67–276.67 ng/mL9"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "hBD-1", "col_header": "Sterile Urine", "value": "10–100 ng/mL8"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "hBD-1", "col_header": "Infected Urine", "value": "~300 ng/mL25"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "LL-37", "col_header": "Sterile Urine", "value": "0.2–5.9 ng/mL5"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "LL-37", "col_header": "Infected Urine", "value": "0–312.5 ng/mL5"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "RNase 7", "col_header": "Sterile Urine", "value": "235 –3467.2 ng/mL7"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "RNase 7", "col_header": "Infected Urine", "value": "6254–11240 ng/mL"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Proteus mirabilis PEDUTI-971", "db_measure": "MIC", "db_value": "1.0-1.25", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Proteus mirabilis PEDUTI-971", "db_measure": "MIC", "db_value": "1.0-1.25", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).