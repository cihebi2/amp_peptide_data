
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
doi__10.1155_2009_136284

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "The antimicrobial activity of Coprisin peptides against E. coli and S. aureus.", "footnotes": [], "header_rows": [["Peptides", "Amino acid sequence", "MIC (μg/mL)", "MIC (μg/mL)"], ["E. coli", "S. aureus"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "CopN5(22–30)", "col_header": "Amino acid sequence", "value": "LHCIALRKK-NH2"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "CopN5(22–30)", "col_header": "MIC (μg/mL)", "value": "8–16"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "CopN5(22–30)", "col_header": "MIC (μg/mL)", "value": ">64"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "CopA1", "col_header": "Amino acid sequence", "value": "LHLIALRKK-NH2 (C24 → L24)"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "CopA1", "col_header": "MIC (μg/mL)", "value": ">64"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "CopA1", "col_header": "MIC (μg/mL)", "value": ">64"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "CopA2", "col_header": "Amino acid sequence", "value": "LHRIALRKK-NH2 (C24 → R24)"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "CopA2", "col_header": "MIC (μg/mL)", "value": ">64"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "CopA2", "col_header": "MIC (μg/mL)", "value": ">64"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "CopA3", "col_header": "Amino acid sequence", "value": "LLCIALRKK-NH2 (H23 → L23)"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "CopA3", "col_header": "MIC (μg/mL)", "value": "4–8"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "CopA3", "col_header": "MIC (μg/mL)", "value": "4–8"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "CopA4", "col_header": "Amino acid sequence", "value": "LRCIALRKK-NH2 (H24 → R24)"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "CopA4", "col_header": "MIC (μg/mL)", "value": "16–32"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "CopA4", "col_header": "MIC (μg/mL)", "value": ">64"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Escherichia coli", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "CopA4"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "CopA4"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Escherichia coli", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "CopA4"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus", "db_measure": "MIC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "CopA4"}, {"assertion_index": 4, "database": "APD6", "db_subject_text": "", "db_measure": "NMR", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Coprisin mature peptide"}, {"assertion_index": 5, "database": "APD6", "db_subject_text": "", "db_measure": "Unknown", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "CopA3 dimer entry"}, {"assertion_index": 6, "database": "CAMP", "db_subject_text": "Escherichia coli[MIC = Aug-16 microg/ml], Staphylococcus aureus[MIC >64 microg/ml]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "CAMP", "db_subject_text": "Escherichia coli[MIC >64 microg/ml], Staphylococcus aureus[MIC >64 microg/ml]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "CAMP", "db_subject_text": "Escherichia coli[MIC >64 microg/ml], Staphylococcus aureus[MIC >64 microg/ml]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "CAMP", "db_subject_text": "Escherichia coli[MIC = 16-32 microg/ml], Staphylococcus aureus[MIC >64 microg/ml]", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "dbAMP", "db_subject_text": "Escherichia coli KCTC 1682 (MIC=3.1μM)\nSalmonella typhimurium KCTC 1926 (MIC=3.1μM)\nPseudomonas aeruginosa KCTC 1637 (MIC=3.1μM)\nStaphylococcus aureus KCTC 1621 (MIC=0.8μM)\nBacillus subtilis KCTC 3068 (MIC=1.6μM)\nStaphylococcus epidermidis KCTC 1917 (MIC=1.6μM)\nStaphylococcus aureus CCARM 3089 (MIC=1.0μM)\nStaphylococcus aureus CCARM 3090 (MIC=0.50μM)\nStaphylococcus aureus CCARM 3108 (MIC=1.0μM)\nStaphylococcus aureus CCARM 3114 (MIC=2.0μM)\nStaphylococcus aureus CCARM 3126 (MIC=0.50μM)\nSalmonella typhimurium CCARM 8003 (MIC=8.0μM)\nSalmonella typhimurium CCARM 8007 (MIC=4.0μM)\nSalmonella typhimurium CCARM 8009 (MIC=4.0μM)\nEscherichia coli CCARM 1229 (MIC=0.50μM)\nEscherichia coli CCARM 1238 (MIC=2.0μM)\nCandida albicans ATCC 90028 (MIC=10μM)\nCandida parapsilosis ATCC 22019 (MIC=10μM)\nMalassezia furfur KCTC 7744 (MIC=5μM)\nTrichosporon beigelii KCTC 7707 (MIC=10μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "dbAMP", "db_subject_text": "Escherichia coli (MIC=16-32μg/ml)\nStaphylococcus aureus (MIC=>64μg/ml)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "CopA4"}, {"assertion_index": 12, "database": "dbAMP", "db_subject_text": "Escherichia coli (MIC=4-8μg/ml)\nStaphylococcus aureus (MIC=4-8μg/ml)\nEscherichia coli KCTC 1682 (MIC=7.5μM)\nSalmonella typhimurium KCTC 1926 (MIC=15μM)\nPseudomonas aeruginosa KCTC 1637 (MIC=15μM)\nStaphylococcus aureus KCTC 1621 (MIC=15μM)\nStaphylococcus epidermidis KCTC 1917 (MIC=7.5μM)\nBacillus subtilis KCTC 3068 (MIC=15μM)\nEnterococcus faecium (MIC=7.5μM)\nEnterococcus faecalis (MIC=3.8μM)\nEnterococcus faecium VR (MIC=7.5μM)\nEnterococcus faecalis VR (MIC=7.5μM)\nStaphylococcus aureus MR (MIC=15μM)\nEnterococcus faecium KCCM 12118 (MIC=8μg/ml)\nEnterococcus faecalis KCCM 29212 (MIC=2μg/ml)\nEnterococcus faecium ATCC 51559 (MIC=4μg/ml)\nEnterococcus faecalis ATCC 51575 (MIC=2μg/ml)\nStaphylococcus aureus KCCM 40510 (MIC=16μg/ml)\nCandida albicans (MIC=8μM)\nHuman pancreatic adenocarcinoma CAPAN-1 (IC50=62μM)\nHuman pancreatic carcinoma Mia PaCa-2 (IC50=>100μM)\nHuman Pancreatic adenocarcinoma SNU-410 (IC50=40.8μM)\nHuman hepatocellular carcinoma HepG2 (IC50=>100μM)\nHuman liver carcinoma SK-HEP-1 (IC50=77μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "CopA3 mixed/later-paper entry"}]

Return ONLY the JSON array now (one object per assertion above).