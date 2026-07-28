
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
doi__10.1371_journal.pone.0023417

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Antibacterial activity of asCATH1 and 2.", "footnotes": ["Bacteria were incubated with varying concentrations of cathelicidin peptides for 18 h before absorbance was read at 600 nm to determine bacterial growth. MIC values are shown as the range of concentrations which produced a 50% reduction in growth compared to a control without cathelicidin."], "header_rows": [["Bacteria", "asCATH1", "MIC (µM) asCATH2", "LL-37"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Y. ruckeri", "col_header": "asCATH1", "value": ">80"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Y. ruckeri", "col_header": "MIC (µM) asCATH2", "value": ">80"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "Y. ruckeri", "col_header": "LL-37", "value": "40–80"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "V. anguillarum", "col_header": "asCATH1", "value": "5–10"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "V. anguillarum", "col_header": "MIC (µM) asCATH2", "value": "10–20"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "V. anguillarum", "col_header": "LL-37", "value": "0.63–1.25"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "E. coli (ATCC 25922)", "col_header": "asCATH1", "value": "1.25–2.5"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "E. coli (ATCC 25922)", "col_header": "MIC (µM) asCATH2", "value": "10–20"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "E. coli (ATCC 25922)", "col_header": "LL-37", "value": "0.63–1.25"}]}, {"table_index": 2, "label": "Table 2", "caption": "Oligonucleotide primers used in real-time pcr experiments.", "footnotes": [], "header_rows": [["Target mRNA", "Accession #", "Forward primer (5′→3′)", "Reverse primer (5′→3′)"], ["asCATH1", "AY728057", "CTTAATTGGTCGCCTG", "ACGTTGATCTGTGATAAAT"], ["asCATH2", "AY360357", "TGGCAACACCCTCAA", "GAATCTTTACTACCCATCT"], ["β-actin", "AF012125", "TTGCGGTATCCACGAGAC", "TAGAGGGAGCCAGAGAGG"], ["RPL2", "BT056485", "TAACGCCTGCCTCTTCC", "ATGAGGGACCTTGTAGCC"], ["PolyUb", "BT049644", "TCTTCATCTGGTCCTGC", "AATGGGTGGGATTGGAGG"], ["EF1a", "AF321836", "TGATTGTGCTGTGCTTA", "AACGCTTCTGGCTGTAGG"], ["IL-8", "BT046706", "ACCAGCGAGATAACAA", "CCAGGAGCACAATGACAA"], ["IL-1", "AY617117", "AACTAAGGACTGAATA", "GAGGTGTTCTTTATTAAAC"], ["IL-18", "BT125392", "AACGGAATAAGGAGCT", "TGATGTCACAGAGAGAAT"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Salmon erythrocytes", "db_measure": "50% Hemolysis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Salmon erythrocytes", "db_measure": "50% Hemolysis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).