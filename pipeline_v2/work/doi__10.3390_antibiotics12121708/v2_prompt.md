
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
doi__10.3390_antibiotics12121708

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Functional prediction results of Lytx-Pa2a.", "footnotes": ["1 Prediction target: Human erythrocytes."], "header_rows": [["Antimicrobial Activity", "Antimicrobial Activity", "Antimicrobial Activity", "Anti-Inflammatory Activity", "Anti-Inflammatory Activity", "HemolyticActivity"], ["ADAM", "sAMPred-GAT", "AmpGram", "PreAIP", "PreTP-Stack", "DBAASP 1"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "0.7 (AMP)", "col_header": "Antimicrobial Activity / sAMPred-GAT", "value": "AMP"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "0.7 (AMP)", "col_header": "Antimicrobial Activity / AmpGram", "value": "0.9894"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "0.7 (AMP)", "col_header": "Anti-Inflammatory Activity / PreAIP", "value": "0.589 (AIP)"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "0.7 (AMP)", "col_header": "Anti-Inflammatory Activity / PreTP-Stack", "value": "AIP"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "0.7 (AMP)", "col_header": "HemolyticActivity / DBAASP 1", "value": "Not active"}]}, {"table_index": 2, "label": "Table 2", "caption": "MIC values for Lytx-Pa2a and melittin against pathogenic strains.", "footnotes": [], "header_rows": [["MIC (μM)", "E. coli", "P. aeruginosa", "B. cereus", "S. aureus"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Lytx-Pa2a", "col_header": "E. coli", "value": "1"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Lytx-Pa2a", "col_header": "P. aeruginosa", "value": "1"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "Lytx-Pa2a", "col_header": "B. cereus", "value": "1"}, {"table_index": 2, "row_index": 2, "col_index": 5, "row_label": "Lytx-Pa2a", "col_header": "S. aureus", "value": "8"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Melittin", "col_header": "E. coli", "value": "1"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Melittin", "col_header": "P. aeruginosa", "value": "8"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "Melittin", "col_header": "B. cereus", "value": "1"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "Melittin", "col_header": "S. aureus", "value": "2"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "The Identification of a Novel Spider Toxin Peptide, Lycotoxin-Pa2a, with Antibacterial and Anti-Inflammatory Activities.", "db_measure": "Unknown", "db_value": "Discovery: in silico mine the venom gland transcriptome library by comparing with known spider genomes for similar AMPs. Sequence analysis: APD analysis reveals that this sequence is most similar (37.5%) to LtTx-1a k: 15%; c: 12%. GRAVY: -0.538; mol Wt: 7306.515; mol formula: C314H503N93O91S8; mol ex coeff: 1990. Chemical modification: four disulfide bonds are predicted: C1–C4, C2–C5, C3–C8, C6–C7. Activity: strongly active against E. coli (MIC 1 uM), P. aeruginosa (MIC 1 uM), B. cereus (MIC 1 uM), and S. aureus (MIC 8 uM). As strong as melittin. It also suppressed LPS-induced inflammation by down-regulating TNF-alpha, IL-1beta, and IL-6 MOA:bacteria: it permeated bacterial membranes and depolarized bacterial membranes of multiple bacteria. ROS release. In vitro Toxicity: bovine RBC: 10% hemolysis at 20 uM peptide. LDH release: up to 20 uM, it did not show toxicity to human adipose-derived mesenchymal stem cells (hADMSCs) and murine macrophage RAW264.7 cells.", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Lycotoxin-Pa2a"}]

Return ONLY the JSON array now (one object per assertion above).