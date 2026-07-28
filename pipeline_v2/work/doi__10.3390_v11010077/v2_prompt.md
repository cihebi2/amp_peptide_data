
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
doi__10.3390_v11010077

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Sequences of the primers used for transcriptomic analysis of the innate anti-viral immune response in keratinocytes.", "footnotes": [], "header_rows": [["IFNB1", "Interferon beta 1", "Forward", "ATT GCT CTC CTG TTG TGC TCT CC"], ["Reverse", "TGC GGC GTC CTC CTT CTG G"], ["IRF7", "Interferon regulatory factor 7", "Forward", "TAC CAT CTA CCT GGG CTT CG"], ["Reverse", "GCT CCA TAA GGA AGC ACT CG"], ["IFIT1", "Interferon-induced protein with tetratricopeptide repeats 1", "Forward", "AGT CGT AGA AAG AAC AAT GCA AGA C"], ["Reverse", "TCA TTC ATA ATT TCC TTC CAA TTT GT"], ["RSAD2", "Radical S-adenosyl methionine domain containing 2", "Forward", "GGC AAG TTG GTG AGG TTC TG"], ["Reverse", "ACC ACC TCC TCA GCT TTT GA"]], "longform_cells": [{"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "OAS 1", "col_header": "Interferon beta 1 / Interferon regulatory factor 7 / Interferon-induced protein with tetratricopeptide repeats 1 / Radical S-adenosyl methionine domain containing 2", "value": "2′-5′-oligoadenylate synthetase 1"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "OAS 1", "col_header": "Forward", "value": "Forward"}, {"table_index": 1, "row_index": 9, "col_index": 4, "row_label": "OAS 1", "col_header": "ATT GCT CTC CTG TTG TGC TCT CC / TAC CAT CTA CCT GGG CTT CG / AGT CGT AGA AAG AAC AAT GCA AGA C / GGC AAG TTG GTG AGG TTC TG", "value": "TTG ACT GGC GGC TAT AAA CC"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Reverse", "col_header": "Interferon beta 1 / Interferon regulatory factor 7 / Interferon-induced protein with tetratricopeptide repeats 1 / Radical S-adenosyl methionine domain containing 2", "value": "GAG CTC CAG GGC ATA CTG AG"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "ISG20", "col_header": "Interferon beta 1 / Interferon regulatory factor 7 / Interferon-induced protein with tetratricopeptide repeats 1 / Radical S-adenosyl methionine domain containing 2", "value": "Interferon-stimulated gene 20 kDa protein"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "ISG20", "col_header": "Forward", "value": "Forward"}, {"table_index": 1, "row_index": 11, "col_index": 4, "row_label": "ISG20", "col_header": "ATT GCT CTC CTG TTG TGC TCT CC / TAC CAT CTA CCT GGG CTT CG / AGT CGT AGA AAG AAC AAT GCA AGA C / GGC AAG TTG GTG AGG TTC TG", "value": "TGA GGG AGA GAT CAC CGA TT"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "Reverse", "col_header": "Interferon beta 1 / Interferon regulatory factor 7 / Interferon-induced protein with tetratricopeptide repeats 1 / Radical S-adenosyl methionine domain containing 2", "value": "TAG CCG CTC ATG TCC TCT TT"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human Primary Epidermal Keratinocytes (HEK)", "db_measure": "20% Cytotoxicity", "db_value": "5", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "HSV-1", "db_measure": "IC90 REP", "db_value": "2.5", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human Primary Epidermal Keratinocytes (HEK)", "db_measure": "23% Cytotoxicity", "db_value": "20", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "HSV-1", "db_measure": "IC50 REP", "db_value": "10", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Human Primary Epidermal Keratinocytes (HEK)", "db_measure": "26% Cytotoxicity", "db_value": "10", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "HSV-1", "db_measure": "IC50 REP", "db_value": "2.5", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DRAMP", "db_subject_text": "[Ref.30669255]HSV-1:inhibition of HSV-1 replication in human keratinocytes(48% inhibition at 2.5 µM,57% inhibition at 5 µM).", "db_measure": "Antimicrobial, Antiviral", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Human Primary Epidermal Keratinocytes (HEK)", "db_measure": "20% Cytotoxicity", "db_value": "5", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "HSV-1", "db_measure": "IC90 REP", "db_value": "2.5", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Human Primary Epidermal Keratinocytes (HEK)", "db_measure": "23% Cytotoxicity", "db_value": "20", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "DBAASP", "db_subject_text": "HSV-1", "db_measure": "IC50 REP", "db_value": "10", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DBAASP", "db_subject_text": "Human Primary Epidermal Keratinocytes (HEK)", "db_measure": "26% Cytotoxicity", "db_value": "10", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 12, "database": "DBAASP", "db_subject_text": "HSV-1", "db_measure": "IC50 REP", "db_value": "2.5", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 13, "database": "DRAMP", "db_subject_text": "[Ref.30669255]HSV-1:inhibition of HSV-1 replication in human keratinocytes(48% inhibition at 2.5 µM,57% inhibition at 5 µM).", "db_measure": "Antimicrobial, Antiviral", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).