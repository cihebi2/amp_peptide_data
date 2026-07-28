
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
doi__10.3389_fmicb.2018.00667

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Minimum inhibitory concentration (MIC) and minimum bactericidal concentration (MBC) of LyeTxI-b and chlorhexidine acetate.", "footnotes": ["Data of LyeTxI were obtained from (Consuegra et al., 2013) ∗; (Santos et al., 2010) ∗∗; (Cruz Olivo et al., 2017) ∗∗∗ and correspond to the same strain references used to LyeTxI-b."], "header_rows": [["", "E. coli", "E. coli", "S. aureus", "S. aureus", "A. actinomycetemcomitans", "A. actinomycetemcomitans", "S. sanguinis", "S. sanguinis"], ["", "MIC", "MBC", "MIC", "MBC", "MIC", "MBC", "MIC", "MBC"], ["Compound", "μmol.L-1", "μmol.L-1", "μmol.L-1", "μmol.L-1", "μmol.L-1", "μmol.L-1", "μmol.L-1", "μmol.L-1"]], "longform_cells": [{"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "LyeTxI", "col_header": "E. coli / MIC / μmol.L-1", "value": "7.81∗∗"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "LyeTxI", "col_header": "E. coli / MBC / μmol.L-1", "value": "–"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "LyeTxI", "col_header": "S. aureus / MIC / μmol.L-1", "value": "–"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "LyeTxI", "col_header": "S. aureus / MBC / μmol.L-1", "value": "–"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "LyeTxI", "col_header": "A. actinomycetemcomitans / MIC / μmol.L-1", "value": "10.6∗"}, {"table_index": 1, "row_index": 4, "col_index": 7, "row_label": "LyeTxI", "col_header": "A. actinomycetemcomitans / MBC / μmol.L-1", "value": "20.12∗"}, {"table_index": 1, "row_index": 4, "col_index": 8, "row_label": "LyeTxI", "col_header": "S. sanguinis / MIC / μmol.L-1", "value": "10.9∗∗∗"}, {"table_index": 1, "row_index": 4, "col_index": 9, "row_label": "LyeTxI", "col_header": "S. sanguinis / MBC / μmol.L-1", "value": "21.8∗∗∗"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "LyeTxI-b", "col_header": "E. coli / MIC / μmol.L-1", "value": "0.71"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "LyeTxI-b", "col_header": "E. coli / MBC / μmol.L-1", "value": "0.71"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "LyeTxI-b", "col_header": "S. aureus / MIC / μmol.L-1", "value": "2.85"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "LyeTxI-b", "col_header": "S. aureus / MBC / μmol.L-1", "value": "2.85"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "LyeTxI-b", "col_header": "A. actinomycetemcomitans / MIC / μmol.L-1", "value": "11.4"}, {"table_index": 1, "row_index": 5, "col_index": 7, "row_label": "LyeTxI-b", "col_header": "A. actinomycetemcomitans / MBC / μmol.L-1", "value": "11.4"}, {"table_index": 1, "row_index": 5, "col_index": 8, "row_label": "LyeTxI-b", "col_header": "S. sanguinis / MIC / μmol.L-1", "value": "5.7"}, {"table_index": 1, "row_index": 5, "col_index": 9, "row_label": "LyeTxI-b", "col_header": "S. sanguinis / MBC / μmol.L-1", "value": "5.7"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Chlorhexidine acetate", "col_header": "E. coli / MIC / μmol.L-1", "value": "125"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Chlorhexidine acetate", "col_header": "E. coli / MBC / μmol.L-1", "value": "–"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "Chlorhexidine acetate", "col_header": "S. aureus / MIC / μmol.L-1", "value": "31"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "Chlorhexidine acetate", "col_header": "S. aureus / MBC / μmol.L-1", "value": "–"}, {"table_index": 1, "row_index": 6, "col_index": 6, "row_label": "Chlorhexidine acetate", "col_header": "A. actinomycetemcomitans / MIC / μmol.L-1", "value": "125"}, {"table_index": 1, "row_index": 6, "col_index": 7, "row_label": "Chlorhexidine acetate", "col_header": "A. actinomycetemcomitans / MBC / μmol.L-1", "value": "–"}, {"table_index": 1, "row_index": 6, "col_index": 8, "row_label": "Chlorhexidine acetate", "col_header": "S. sanguinis / MIC / μmol.L-1", "value": "62.5"}, {"table_index": 1, "row_index": 6, "col_index": 9, "row_label": "Chlorhexidine acetate", "col_header": "S. sanguinis / MBC / μmol.L-1", "value": "–"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Sheep erythrocytes", "db_measure": "50-60% Hemolysis 42.54 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Toxin LyeTx 1"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Aggregatibacter actinomycetemcomitans ATCC 29522", "db_measure": "MIC 10.6 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Toxin LyeTx 1"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Aggregatibacter actinomycetemcomitans ATCC 29522", "db_measure": "MBC 20.12 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Toxin LyeTx 1"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Streptococcus sanguinis ATCC 10556", "db_measure": "MIC 10.9 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Toxin LyeTx 1"}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Streptococcus sanguinis ATCC 10556", "db_measure": "MBC 21.8 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Toxin LyeTx 1"}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Sheep erythrocytes", "db_measure": "50-60% Hemolysis 42.54 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "LyeTxI-b, a Synthetic Peptide Derived From Lycosa erythrognatha Spider Venom, Shows Potent Antibiotic Activity in Vitro and in Vivo."}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Aggregatibacter actinomycetemcomitans ATCC 29522", "db_measure": "MIC 10.6 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "LyeTxI-b, a Synthetic Peptide Derived From Lycosa erythrognatha Spider Venom, Shows Potent Antibiotic Activity in Vitro and in Vivo."}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Aggregatibacter actinomycetemcomitans ATCC 29522", "db_measure": "MBC 20.12 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "LyeTxI-b, a Synthetic Peptide Derived From Lycosa erythrognatha Spider Venom, Shows Potent Antibiotic Activity in Vitro and in Vivo."}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Streptococcus sanguinis ATCC 10556", "db_measure": "MIC 10.9 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "LyeTxI-b, a Synthetic Peptide Derived From Lycosa erythrognatha Spider Venom, Shows Potent Antibiotic Activity in Vitro and in Vivo."}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Streptococcus sanguinis ATCC 10556", "db_measure": "MBC 21.8 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "LyeTxI-b, a Synthetic Peptide Derived From Lycosa erythrognatha Spider Venom, Shows Potent Antibiotic Activity in Vitro and in Vivo."}, {"assertion_index": 10, "database": "dbAMP", "db_subject_text": "Escherichia coli ATCC 25922 (MIC=0.71μM)\nEscherichia coli ATCC 25922 (MBC=0.71μM)\nStaphylococcus aureus ATCC 25923 (MIC=2.85μM)\nStaphylococcus aureus ATCC 25923 (MBC=2.85μM)\nAggregatibacter actinomycetemcomitans ATCC 29522 (MIC=11.4μM)\nAggregatibacter actinomycetemcomitans ATCC 29522 (MBC=11.4μM)\nStreptococcus sanguinis ATCC 10556 (MIC=5.7μM)\nStreptococcus sanguinis ATCC 10556 (MBC=5.7μM)\nHuman glioblastoma U87-MG (IC50=29.20 ± 7.96μM)\nHuman neuroblastoma SH-SY5Y (IC50=93.80 ± 2.17μM)\nHuman astrocytoma U373-MG (IC50=20.94 ± 5.18μM)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "Toxin LyeTx 1 [H16Del]"}]

Return ONLY the JSON array now (one object per assertion above).