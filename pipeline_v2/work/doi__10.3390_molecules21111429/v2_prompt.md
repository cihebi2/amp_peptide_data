
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
doi__10.3390_molecules21111429

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Physicochemical properties of frenatin peptides and their analogues.", "footnotes": ["H represents hydrophobicity and μH represents hydrophobic moment."], "header_rows": [["Peptide", "H", "μH", "Net Charge (z)", "Helicity (%)"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "Frenatin 4.1", "col_header": "H", "value": "0.300"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "Frenatin 4.1", "col_header": "μH", "value": "0.491"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "Frenatin 4.1", "col_header": "Net Charge (z)", "value": "2"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "Frenatin 4.1", "col_header": "Helicity (%)", "value": "43.87%"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Frenatin 4.1a", "col_header": "H", "value": "0.244"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Frenatin 4.1a", "col_header": "μH", "value": "0.540"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Frenatin 4.1a", "col_header": "Net Charge (z)", "value": "3"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "Frenatin 4.1a", "col_header": "Helicity (%)", "value": "55.41%"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Frenatin 4.2", "col_header": "H", "value": "0.315"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Frenatin 4.2", "col_header": "μH", "value": "0.525"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "Frenatin 4.2", "col_header": "Net Charge (z)", "value": "3"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "Frenatin 4.2", "col_header": "Helicity (%)", "value": "42.58%"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Frenatin 4.2a", "col_header": "H", "value": "0.599"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Frenatin 4.2a", "col_header": "μH", "value": "0.294"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "Frenatin 4.2a", "col_header": "Net Charge (z)", "value": "5"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "Frenatin 4.2a", "col_header": "Helicity (%)", "value": "61.87%"}]}, {"table_index": 2, "label": "Table 2", "caption": "Minimal inhibitory concentrations (MICs) of the frenatin peptides and their analogues as determined for three different test microorganisms. Mass concentration (μg/mL) was employed, and molarity (μM) was calculated and showed in brackets.", "footnotes": [], "header_rows": [["Peptide", "Minimal inhibitory concontrations (MICs)-μg/mL(μM)", "Minimal inhibitory concontrations (MICs)-μg/mL(μM)", "Minimal inhibitory concontrations (MICs)-μg/mL(μM)"], ["S. aureus", "E. coli", "C. albicans"]], "longform_cells": [{"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Frenatin 4.1", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / S. aureus", "value": ">512 (>202.4)"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Frenatin 4.1", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / E. coli", "value": ">512 (>202.4)"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "Frenatin 4.1", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / C. albicans", "value": ">512 (>202.4)"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Frenatin 4.1a", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / S. aureus", "value": ">512 (>202.9)"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Frenatin 4.1a", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / E. coli", "value": "128 (50.7)"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "Frenatin 4.1a", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / C. albicans", "value": "256 (101.5)"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Frenatin 4.2", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / S. aureus", "value": ">512 (>216.0)"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Frenatin 4.2", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / E. coli", "value": "128 (54.0)"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "Frenatin 4.2", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / C. albicans", "value": "256 (108.0)"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Frenatin 4.2a", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / S. aureus", "value": "16 (6.8)"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "Frenatin 4.2a", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / E. coli", "value": "32 (13.5)"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "Frenatin 4.2a", "col_header": "Minimal inhibitory concontrations (MICs)-μg/mL(μM) / C. albicans", "value": "16 (6.8)"}]}, {"table_index": 3, "label": "Table 3", "caption": "Known frenatins, their sequences and sources.", "footnotes": [], "header_rows": [["Name", "Sequence", "Source", "Reference"], ["Frenatin 1", "GLLDALSGILGL.NH2", "Litoria infrafrenata", "[6]"], ["Frenatin 1.1", "GLLDTLGGILGL.NH2", "Litoria infrafrenata", "[4]"], ["Frenatin 2", "GLLGTLGNLLNGLGL.NH2", "Litoria infrafrenata", "[6]"], ["Frenatin 2D", "DLLGTLGNLPLPFI.NH2", "Discoglossus sardus", "[7]"], ["Frenatin 2.1D", "GTLGNLPAPFPG", "Discoglossus sardus", "[7]"], ["Frenatin 2.1S", "GLVGTLLGHIGKAILG.NH2", "Sphaenorhynchus lacteus", "[8]"], ["Frenatin 2.2S", "GLVGTLLGHIGKAILS.NH2", "Sphaenorhynchus lacteus", "[8]"], ["Frenatin 2.3S", "GLVGTLLGHIGKAILG", "Sphaenorhynchus lacteus", "[8]"], ["Frenatin 3", "GLMSVLGHAVGNVLGGLFKPKS", "Litoria infrafrenata", "[6]"], ["Frenatin 3.1", "GLMSILGKVAGNVLGGLFKPKENVQKM", "Litoria infrafrenata", "[4]"], ["Frenatin 4", "GFLDKLKKGASDFANALVNSIKGT", "Litoria infrafrenata", "[6]"], ["Frenatin 4.1", "GFLEKLKTGAKDFASAFVNSIKGT", "Litoria infrafrenata", "[4]"], ["Frenatin 4.2", "GFLEKLKTGAKDFASAFVNSIK.NH2", "Litoria infrafrenata", ""]], "longform_cells": []}, {"table_index": 4, "label": "Table 4", "caption": "", "footnotes": [], "header_rows": [["MIC", "Minimal inhibitory concentration"], ["RACE", "Rapid Amplification of cDNA Ends"], ["MALDI-TOF", "Matrix Assisted Laser Desorption Ionization—Time of Flight"]], "longform_cells": [{"table_index": 4, "row_index": 4, "col_index": 2, "row_label": "Fmoc", "col_header": "Minimal inhibitory concentration / Rapid Amplification of cDNA Ends / Matrix Assisted Laser Desorption Ionization—Time of Flight", "value": "9-Fluorenylmethyloxycarbonyl"}, {"table_index": 4, "row_index": 5, "col_index": 2, "row_label": "NUP", "col_header": "Minimal inhibitory concentration / Rapid Amplification of cDNA Ends / Matrix Assisted Laser Desorption Ionization—Time of Flight", "value": "Nested Universal Primer"}, {"table_index": 4, "row_index": 6, "col_index": 2, "row_label": "TFA", "col_header": "Minimal inhibitory concentration / Rapid Amplification of cDNA Ends / Matrix Assisted Laser Desorption Ionization—Time of Flight", "value": "Trifluoroacetic Acid"}, {"table_index": 4, "row_index": 7, "col_index": 2, "row_label": "CHCA", "col_header": "Minimal inhibitory concentration / Rapid Amplification of cDNA Ends / Matrix Assisted Laser Desorption Ionization—Time of Flight", "value": "α-Cyano-4-hydroxycinnamic Acid"}, {"table_index": 4, "row_index": 8, "col_index": 2, "row_label": "CFU", "col_header": "Minimal inhibitory concentration / Rapid Amplification of cDNA Ends / Matrix Assisted Laser Desorption Ionization—Time of Flight", "value": "Colony Forming Unit"}]}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "CAMP", "db_subject_text": "Staphylococcus aureus (MIC = 16 microg/ml), E. coli (MIC = 32 microg/ml), C. albicans (MIC = 16 microg/ml)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "Staphylococcus aureus (MIC = >512 microg/ml), E. coli (MIC = 128 microg/ml), C. albicans (MIC = 256 microg/ml)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).