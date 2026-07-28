
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
doi__10.3390_molecules23123314

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "FIGURE(vision:labeled_chart) molecules-23-03314-g001.jpg", "caption": "codex-vision extracted from /home/cihebi/抗菌肽/数据集/batch/5-team/paper_packets/doi__10.3390_molecules23123314/extracted/oa_package/local-DBAASP-PMC6321396/PMC6321396/molecules-23-03314-g001.jpg", "footnotes": [], "header_rows": [], "longform_cells": [{"table_index": 1, "row_index": "", "col_index": "", "row_label": "HAP-1", "col_header": "intervening peptide", "value": "GRK", "confidence": "printed"}, {"table_index": 1, "row_index": "", "col_index": "", "row_label": "BmKn1", "col_header": "intervening peptide", "value": "GKR", "confidence": "printed"}, {"table_index": 1, "row_index": "", "col_index": "", "row_label": "BmKb1", "col_header": "intervening peptide", "value": "GRR", "confidence": "printed"}]}, {"table_index": 2, "label": "FIGURE(vision:table_image) molecules-23-03314-g002.jpg", "caption": "codex-vision extracted from /home/cihebi/抗菌肽/数据集/batch/5-team/paper_packets/doi__10.3390_molecules23123314/extracted/oa_package/local-DBAASP-PMC6321396/PMC6321396/molecules-23-03314-g002.jpg", "footnotes": [], "header_rows": [], "longform_cells": [{"table_index": 2, "row_index": "", "col_index": "", "row_label": "HAP-1", "col_header": "A Identities", "value": "100%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "AMX81473.1", "col_header": "A Identities", "value": "98%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ABR21055.1", "col_header": "A Identities", "value": "95%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "HjVP", "col_header": "A Identities", "value": "83%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "MeVP-8", "col_header": "A Identities", "value": "95%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ALX72366.1", "col_header": "A Identities", "value": "87%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ADY62660.1", "col_header": "A Identities", "value": "83%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ABR21012.1", "col_header": "A Identities", "value": "95%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ALY87545.1", "col_header": "A Identities", "value": "85%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ACJ23161.1", "col_header": "A Identities", "value": "81%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "Mevtoxinlip-4", "col_header": "A Identities", "value": "89%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "BoiTx776", "col_header": "A Identities", "value": "76%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "HAP-1", "col_header": "B Identities", "value": "100%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "AMX81473.1", "col_header": "B Identities", "value": "100%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ABR21055.1", "col_header": "B Identities", "value": "100%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "HjVP", "col_header": "B Identities", "value": "94%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "MeVP-8", "col_header": "B Identities", "value": "100%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ALX72366.1", "col_header": "B Identities", "value": "79%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ADY62660.1", "col_header": "B Identities", "value": "79%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ABR21012.1", "col_header": "B Identities", "value": "95%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ALY87545.1", "col_header": "B Identities", "value": "84%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "ACJ23161.1", "col_header": "B Identities", "value": "74%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "Mevtoxinlip-4", "col_header": "B Identities", "value": "95%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "BoiTx776", "col_header": "B Identities", "value": "75%", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "C", "col_header": "sequence", "value": "QKDDEEESRFFFNFIFSAE", "confidence": "printed"}, {"table_index": 2, "row_index": "", "col_index": "", "row_label": "C", "col_header": "secondary structure", "value": "CCCCCCCCEEEEEEEECC", "confidence": "printed"}]}, {"table_index": 3, "label": "FIGURE(vision:labeled_chart) molecules-23-03314-g003.jpg", "caption": "codex-vision extracted from /home/cihebi/抗菌肽/数据集/batch/5-team/paper_packets/doi__10.3390_molecules23123314/extracted/oa_package/local-DBAASP-PMC6321396/PMC6321396/molecules-23-03314-g003.jpg", "footnotes": [], "header_rows": [], "longform_cells": [{"table_index": 3, "row_index": "", "col_index": "", "row_label": "ApHt_20", "col_header": "MIC (µM)", "value": "8", "confidence": "chart_estimate"}, {"table_index": 3, "row_index": "", "col_index": "", "row_label": "ApHt_20+HAP-1", "col_header": "MIC (µM)", "value": "16", "confidence": "chart_estimate"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus AB94004, Bacillus magaterium AB90008, Bacillus thuringiensis AB93100, Escherichia coli DH5alpha, Pseudomonas putida, Pseudomonas fluorescens, Klebsiella oxytoca AB2010143, Enterobacter cloacae AB2010162, Salmonella enterica AB2010185, Candida tropicalis AY91009", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "HAP-1"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus AB94004\nSalmonella enterica AB2010185\nPseudomonas putida\nPseudomonas fluorescens\nKlebsiella oxytoca AB2010143\nEscherichia coli DH5alpha\nEnterobacter cloacae AB2010162\nCandida tropicalis AY91009\nBacillus thuringiensis AB93100\nBacillus magaterium AB90008", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "HAP-1 (1-19)"}]

Return ONLY the JSON array now (one object per assertion above).