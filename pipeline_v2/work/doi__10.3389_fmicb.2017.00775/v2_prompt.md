
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
doi__10.3389_fmicb.2017.00775

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Viral protein-derived peptides used in this study.", "footnotes": [], "header_rows": [["Name", "Sequence", "Length", "Net charge", "Source (protein:position)"], ["vCPP 0275", "KKRYKKKYKAYKPYKKKKKF-NH2", "20", "+14", "Cauliflower mosaic virus (Capsid: aa367–387)"], ["vCPP 0417", "SPRRRTPSPRRRRSQSPRRR-NH2", "20", "+11", "Hepatitis B virus genotype C (Capsid: aa155–175)"], ["vCPP 0667", "RPRRRATTRRRITTGTRRRR-NH2", "20", "+12", "Human Adenovirus C serotype 1 (Minor Core Protein – Capsid: aa314–334)"], ["vCPP 0769", "RRLTLRQLLGLGSRRRRRSR-NH2", "20", "+10", "Fowl adenovirus A serotype 1 (Major Capsid Protein: aa17–37)"], ["vCPP 1779", "GRRGPRRANQNGTRRRRRRT-NH2", "20", "+11", "Barley Virus (Capsid: aa5–25)"], ["vCPP 2319", "WRRRYRRWRRRRRWRRRPRR-NH2", "20", "+16", "Torque teno douroucouli vírus (Capsid: aa16–36)"], ["vAMP 059", "INWKKWWQVFYTVV-NH2", "14", "+3", "Rotavirus VP7 (Capsid: aa94–107)"]], "longform_cells": []}, {"table_index": 2, "label": "Table 2", "caption": "Antibacterial activity of vCPPs.", "footnotes": [], "header_rows": [["Peptide", "MIC (μM)", "MIC (μM)", "MIC (μM)", "MIC (μM)"], ["", "S. aureus", "MRSA", "E. coli", "P. aeruginosa"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "vCPP 0275", "col_header": "MIC (μM) / S. aureus", "value": "25–50"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "vCPP 0275", "col_header": "MIC (μM) / MRSA", "value": "50"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "vCPP 0275", "col_header": "MIC (μM) / E. coli", "value": "12.5"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "vCPP 0275", "col_header": "MIC (μM) / P. aeruginosa", "value": "100"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "vCPP 0417", "col_header": "MIC (μM) / S. aureus", "value": ">100"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "vCPP 0417", "col_header": "MIC (μM) / MRSA", "value": ">100"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "vCPP 0417", "col_header": "MIC (μM) / E. coli", "value": "25"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "vCPP 0417", "col_header": "MIC (μM) / P. aeruginosa", "value": "100"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "vCPP 0667", "col_header": "MIC (μM) / S. aureus", "value": "50"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "vCPP 0667", "col_header": "MIC (μM) / MRSA", "value": "100"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "vCPP 0667", "col_header": "MIC (μM) / E. coli", "value": "12.5"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "vCPP 0667", "col_header": "MIC (μM) / P. aeruginosa", "value": "25"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "vCPP 0769", "col_header": "MIC (μM) / S. aureus", "value": "3.13"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "vCPP 0769", "col_header": "MIC (μM) / MRSA", "value": "3.13"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "vCPP 0769", "col_header": "MIC (μM) / E. coli", "value": "25"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "vCPP 0769", "col_header": "MIC (μM) / P. aeruginosa", "value": "3.13"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "vCPP 1779", "col_header": "MIC (μM) / S. aureus", "value": "100–>100"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "vCPP 1779", "col_header": "MIC (μM) / MRSA", "value": ">100"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "vCPP 1779", "col_header": "MIC (μM) / E. coli", "value": "25"}, {"table_index": 2, "row_index": 7, "col_index": 5, "row_label": "vCPP 1779", "col_header": "MIC (μM) / P. aeruginosa", "value": "25"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "vCPP 2319", "col_header": "MIC (μM) / S. aureus", "value": "1.56"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "vCPP 2319", "col_header": "MIC (μM) / MRSA", "value": "1.56"}, {"table_index": 2, "row_index": 8, "col_index": 4, "row_label": "vCPP 2319", "col_header": "MIC (μM) / E. coli", "value": "3.13"}, {"table_index": 2, "row_index": 8, "col_index": 5, "row_label": "vCPP 2319", "col_header": "MIC (μM) / P. aeruginosa", "value": "3.13"}]}, {"table_index": 3, "label": "Table 3", "caption": "Bactericidal activity of vCPP 0769, vCPP 2319, and vAMP 059.", "footnotes": [], "header_rows": [["Peptide", "MBC (μM)", "MBC (μM)", "MBC (μM)", "MBC (μM)"], ["", "S. aureus", "MRSA", "E. coli", "P. aeruginosa"]], "longform_cells": [{"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "vCPP 0769", "col_header": "MBC (μM) / S. aureus", "value": ">100"}, {"table_index": 3, "row_index": 3, "col_index": 3, "row_label": "vCPP 0769", "col_header": "MBC (μM) / MRSA", "value": ">100"}, {"table_index": 3, "row_index": 3, "col_index": 4, "row_label": "vCPP 0769", "col_header": "MBC (μM) / E. coli", "value": "50"}, {"table_index": 3, "row_index": 3, "col_index": 5, "row_label": "vCPP 0769", "col_header": "MBC (μM) / P. aeruginosa", "value": "6.25"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "vCPP 2319", "col_header": "MBC (μM) / S. aureus", "value": "3.13"}, {"table_index": 3, "row_index": 4, "col_index": 3, "row_label": "vCPP 2319", "col_header": "MBC (μM) / MRSA", "value": "3.13"}, {"table_index": 3, "row_index": 4, "col_index": 4, "row_label": "vCPP 2319", "col_header": "MBC (μM) / E. coli", "value": "3.13"}, {"table_index": 3, "row_index": 4, "col_index": 5, "row_label": "vCPP 2319", "col_header": "MBC (μM) / P. aeruginosa", "value": "3.13"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "vAMP 059", "col_header": "MBC (μM) / S. aureus", "value": "1.56"}, {"table_index": 3, "row_index": 5, "col_index": 3, "row_label": "vAMP 059", "col_header": "MBC (μM) / MRSA", "value": "–"}, {"table_index": 3, "row_index": 5, "col_index": 4, "row_label": "vAMP 059", "col_header": "MBC (μM) / E. coli", "value": "–"}, {"table_index": 3, "row_index": 5, "col_index": 5, "row_label": "vAMP 059", "col_header": "MBC (μM) / P. aeruginosa", "value": "6.25"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "CAMP", "db_subject_text": "S. aureus (MBC = 1.56 microM), P. aeruginosa (MBC = 25 microM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "S. aureus (MIC = >100 microM), MRSA (MIC = >100 microM), E. coli (MIC = 25 microM), P. aeruginosa (MIC = 25 microM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "dbAMP", "db_subject_text": "Staphylococcus aureus ATCC 25923 (MIC=1.56μM)\nStaphylococcus aureus ATCC 25923 (MBC=3.13μM)\nStaphylococcus aureus ATCC 33591 (MIC=1.56μM)\nStaphylococcus aureus ATCC 33591 (MBC=3.13μM)\nEscherichia coli ATCC 25922 (MIC=3.13μM)\nEscherichia coli ATCC 25922 (MBC=3.13μM)\nPseudomonas aeruginosa ATCC 27853 (MIC=3.13μM)\nPseudomonas aeruginosa ATCC 27853 (MBC=3.13μM)\nHuman breast adenocarcinoma MDA-MB-231 (IC50= 5.02±1.04μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).