
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
doi__10.1186_s12951-024-02896-5

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Summary of the design, structure and property of self-assembled peptide discussed in this study", "footnotes": [], "header_rows": [["Peptide", "Design", "Structure", "Improvements", "Ref"], ["W-4", "wkwkwNGwkwkw-NH2", "Nanofibers", "Reduce toxicity and increase stability", "14"], ["CPC-1", "Chitosan-GPLGVRGC-PEG2000- CGGG(KLAKLAK)2", "Nanoparticle to nanofiber transition induced by enzyme", "Improve the stability and prolong the half-retention time", "23"], ["HDMP", "BP-KLVFF -RLYLRIGRR", "Nanoparticle to nanofiber transition induced by LTA", "LTA-induced in situ self-assembling nanofibers trap bacteria", "24"], ["PTP-7", "FLGALFRALSRLL", "Nanofiber", "Dramatically alter activity and stability in comparison with single molecule CL-1", "27"], ["BET", "BP-KFFVLK-RLKLILKSK", "Nanoparticle to nanofiber transition induced by LPS", "Transform in situ from nanoparticles to nanofibrous networks to trap bacteria and induce aggregation", "32"], ["BTT2", "LKLKLKVpPTKLKLKL-NH2", "LTA and LPS as nucleation sites, inducing BTT self-assembly into nanonet", "Bacteria-induced in situ self-assembly form nanonet trap-and-kill bacteria and display robust stability against trypsin", "34"], ["FF", "FF", "Nanofiber", "FF as the minimal model for antibacterial supramolecular polymers", "35"], ["NPs1", "C14-(PF)4P-K(PEG8-NH2)(KP)5-NH2", "Nanoparticle", "Display broad-spectrum antibacterial activity and high stability", "38"], ["SAP", "(WVHH)3PG(HHVV)3-NH2", "Nanospheres to nanofiber transition triggered by pH", "Display the entrapment property and excellent biocompatibility", "51"], ["Assembling Peptide", "C14-(HHHF)4HHH-K-(PEG8)-QRKLAAKLT-NH2", "Nanofiber to nanoparticle transition triggered by pH", "Exhibit pH responsiveness and high biocompatibility", "53"], ["RW-1", "RRRRWWWW", "Micelle", "High and rapid bacteria-killing activity", "54"], ["Defensin", "HD6", "Nanofiber", "HD6 self-assembly to form fibrils and nanonets that surround and entangle bacteria", "56"], ["Z(WR)2", "WRWRCNSKSFCRWRW", "Nanofiber", "LPS and LTA-induced nanofibers to trap bacteria", "57"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "FKN-N6"}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Bovine mammary epithelial cells MAC-T", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "FKN-N6"}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Mouse erythrocytes", "db_measure": "10-20% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "FKN-N6"}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 25922", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "FKN-N6"}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Murine macrophage cells RAW 264.7", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "FKN-N6"}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "FFN-N6"}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Bovine mammary epithelial cells MAC-T", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "FFN-N6"}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 25922", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "FFN-N6"}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Murine macrophage cells RAW 264.7", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": "FFN-N6"}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "DBAASP", "db_subject_text": "Bovine mammary epithelial cells MAC-T", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DBAASP", "db_subject_text": "Mouse erythrocytes", "db_measure": "10-20% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 12, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 25922", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 13, "database": "DBAASP", "db_subject_text": "Murine macrophage cells RAW 264.7", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 14, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 15, "database": "DBAASP", "db_subject_text": "Bovine mammary epithelial cells MAC-T", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 16, "database": "DBAASP", "db_subject_text": "Escherichia coli ATCC 25922", "db_measure": "MIC", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 17, "database": "DBAASP", "db_subject_text": "Murine macrophage cells RAW 264.7", "db_measure": "LC90", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).