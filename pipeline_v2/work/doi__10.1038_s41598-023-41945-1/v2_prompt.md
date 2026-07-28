
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
doi__10.1038_s41598-023-41945-1

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "List of PMAP-36 analogues and of their physico-chemical properties.", "footnotes": ["*Omitted N-terminal sequence = GRFRRLRKKTR. a Retention time refers to 5%—95%B (CH3CN/H2O, 9:1) over 30 min gradient, C18 column; relative to compound a: bΔtR = tR(x)−tR(a), where x stays for peptides b–h; ccalculated from the [θ]222 value in SDS solution17; dND, not determined for mixed helices. Aun: 11-aminoundecanoic acid; Aib, U: α-aminoisobutyric acid."], "header_rows": [["", "Peptide sequence", "Theoretical MW", "Experimental MW", "Retention timea", "Hydrophobicityb", "Helicity (%)c"], ["[M + H]+calcd", "[M + H]+exp", "tR (min)", "ΔtR"], ["PMAP-36", "*KRLKKIGKVLKWIPPIVGSIPLGCG-NH2", "", "", "", "", ""]], "longform_cells": [{"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "a", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWIPPIVGSI-NH2"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "a", "col_header": "Theoretical MW", "value": "2314.5"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "a", "col_header": "Experimental MW", "value": "2314.8"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "a", "col_header": "Retention timea", "value": "13.2"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "a", "col_header": "Hydrophobicityb", "value": "0"}, {"table_index": 1, "row_index": 4, "col_index": 7, "row_label": "a", "col_header": "Helicity (%)c", "value": "18"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "b", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "b", "col_header": "Theoretical MW", "value": "2319.5"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "b", "col_header": "Experimental MW", "value": "2319.7"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "b", "col_header": "Retention timea", "value": "17.2"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "b", "col_header": "Hydrophobicityb", "value": "4.0"}, {"table_index": 1, "row_index": 5, "col_index": 7, "row_label": "b", "col_header": "Helicity (%)c", "value": "94"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "c", "col_header": "Peptide sequence", "value": "Oct-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "c", "col_header": "Theoretical MW", "value": "2404.2"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "c", "col_header": "Experimental MW", "value": "2403.8"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "c", "col_header": "Retention timea", "value": "22.3"}, {"table_index": 1, "row_index": 6, "col_index": 6, "row_label": "c", "col_header": "Hydrophobicityb", "value": "9.1"}, {"table_index": 1, "row_index": 6, "col_index": 7, "row_label": "c", "col_header": "Helicity (%)c", "value": "71"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "d", "col_header": "Peptide sequence", "value": "Lau-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "d", "col_header": "Theoretical MW", "value": "2460.3"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "d", "col_header": "Experimental MW", "value": "2459.7"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "d", "col_header": "Retention timea", "value": "22.8"}, {"table_index": 1, "row_index": 7, "col_index": 6, "row_label": "d", "col_header": "Hydrophobicityb", "value": "9.6"}, {"table_index": 1, "row_index": 7, "col_index": 7, "row_label": "d", "col_header": "Helicity (%)c", "value": "47"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "e", "col_header": "Peptide sequence", "value": "Pal-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "e", "col_header": "Theoretical MW", "value": "2516.4"}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "e", "col_header": "Experimental MW", "value": "2516.9"}, {"table_index": 1, "row_index": 8, "col_index": 5, "row_label": "e", "col_header": "Retention timea", "value": "25.8"}, {"table_index": 1, "row_index": 8, "col_index": 6, "row_label": "e", "col_header": "Hydrophobicityb", "value": "12.6"}, {"table_index": 1, "row_index": 8, "col_index": 7, "row_label": "e", "col_header": "Helicity (%)c", "value": "53"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "f", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWIAKIVGSI-Aun-NH2"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "f", "col_header": "Theoretical MW", "value": "2503.3"}, {"table_index": 1, "row_index": 9, "col_index": 4, "row_label": "f", "col_header": "Experimental MW", "value": "2503.8"}, {"table_index": 1, "row_index": 9, "col_index": 5, "row_label": "f", "col_header": "Retention timea", "value": "20.3"}, {"table_index": 1, "row_index": 9, "col_index": 6, "row_label": "f", "col_header": "Hydrophobicityb", "value": "7.1"}, {"table_index": 1, "row_index": 9, "col_index": 7, "row_label": "f", "col_header": "Helicity (%)c", "value": "82"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "g", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWI-NH2"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "g", "col_header": "Theoretical MW", "value": "1650.2"}, {"table_index": 1, "row_index": 10, "col_index": 4, "row_label": "g", "col_header": "Experimental MW", "value": "1650.5"}, {"table_index": 1, "row_index": 10, "col_index": 5, "row_label": "g", "col_header": "Retention timea", "value": "12.1"}, {"table_index": 1, "row_index": 10, "col_index": 6, "row_label": "g", "col_header": "Hydrophobicityb", "value": "− 1.1"}, {"table_index": 1, "row_index": 10, "col_index": 7, "row_label": "g", "col_header": "Helicity (%)c", "value": "NDd"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "h", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVUKWI-NH2"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "h", "col_header": "Theoretical MW", "value": "1623.1"}, {"table_index": 1, "row_index": 11, "col_index": 4, "row_label": "h", "col_header": "Experimental MW", "value": "1623.4"}, {"table_index": 1, "row_index": 11, "col_index": 5, "row_label": "h", "col_header": "Retention timea", "value": "11.7"}, {"table_index": 1, "row_index": 11, "col_index": 6, "row_label": "h", "col_header": "Hydrophobicityb", "value": "− 1.5"}, {"table_index": 1, "row_index": 11, "col_index": 7, "row_label": "h", "col_header": "Helicity (%)c", "value": "ND"}]}, {"table_index": 2, "label": "Table 2", "caption": "Antibacterial activity (MIC) of PMAP-36 derivatives against Gram-negative and Gram-positive bacteria.", "footnotes": ["*MIC, minimum inhibitory concentration is the lowest peptide concentration causing no visible growth after 18 h incubation in Mueller–Hinton broth at 37 °C. Values indicate the mode of three independent tests. Coloured boxes indicate different antimicrobial activity: high activity (green) low or no activity (red). Lipopeptides have not been tested above 32 µM due to their low solubility (see Supporting Information for evaluation of aggregation)."], "header_rows": [], "longform_cells": []}, {"table_index": 3, "label": "Table 3", "caption": "Selective antibacterial activity of PMAP-36 derivatives.", "footnotes": ["*Minimum selectivity index is calculated as ratio between cytotoxicity/haemolytic activity and MIC on at least five out of six bacterial species. The IC50 was considered as the peptide concentration at which cell viability is reduced by 50% compared to the untreated control. MHC was taken as the lowest concentration of peptides which induced 10% of haemolysis of red blood cells31."], "header_rows": [["Peptide", "Minimum selectivity index*"], ["IC50 /MIC", "MHC/MIC"]], "longform_cells": [{"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "a", "col_header": "Peptide", "value": "> 16"}, {"table_index": 3, "row_index": 3, "col_index": 3, "row_label": "a", "col_header": "Minimum selectivity index*", "value": "> 8"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "b", "col_header": "Peptide", "value": "≥ 1.6"}, {"table_index": 3, "row_index": 4, "col_index": 3, "row_label": "b", "col_header": "Minimum selectivity index*", "value": "≥ 1"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "c", "col_header": "Peptide", "value": "≤ 1.6"}, {"table_index": 3, "row_index": 5, "col_index": 3, "row_label": "c", "col_header": "Minimum selectivity index*", "value": "< 0.5"}, {"table_index": 3, "row_index": 6, "col_index": 2, "row_label": "d", "col_header": "Peptide", "value": "< 0.2"}, {"table_index": 3, "row_index": 6, "col_index": 3, "row_label": "d", "col_header": "Minimum selectivity index*", "value": "≤ 0.1"}, {"table_index": 3, "row_index": 7, "col_index": 2, "row_label": "e", "col_header": "Peptide", "value": "< 0.2"}, {"table_index": 3, "row_index": 7, "col_index": 3, "row_label": "e", "col_header": "Minimum selectivity index*", "value": "< 0.2"}, {"table_index": 3, "row_index": 8, "col_index": 2, "row_label": "f", "col_header": "Peptide", "value": "< 1"}, {"table_index": 3, "row_index": 8, "col_index": 3, "row_label": "f", "col_header": "Minimum selectivity index*", "value": "< 0.5"}, {"table_index": 3, "row_index": 9, "col_index": 2, "row_label": "g", "col_header": "Peptide", "value": "> 8"}, {"table_index": 3, "row_index": 9, "col_index": 3, "row_label": "g", "col_header": "Minimum selectivity index*", "value": "> 4"}, {"table_index": 3, "row_index": 10, "col_index": 2, "row_label": "h", "col_header": "Peptide", "value": "≥ 6.8"}, {"table_index": 3, "row_index": 10, "col_index": 3, "row_label": "h", "col_header": "Minimum selectivity index*", "value": "> 4"}]}, {"table_index": 4, "label": "PDF p2 table1", "caption": "from paper.pdf", "footnotes": [], "header_rows": [["", "Peptide sequence", "Theoretical MW", "Experimental MW", "Retention timea", "Hydrophobicityb", "Helicity (%)c"], ["", "", "[M + H]+ calcd", "[M + H]+ exp", "tR (min)", "ΔtR", ""], ["PMAP-36", "*KRLKKIGKVLKWIPPIVGSIPLGCG-NH2", "", "", "", "", ""]], "longform_cells": [{"table_index": 4, "row_index": 4, "col_index": 2, "row_label": "a", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWIPPIVGSI-NH2"}, {"table_index": 4, "row_index": 4, "col_index": 3, "row_label": "a", "col_header": "Theoretical MW", "value": "2314.5"}, {"table_index": 4, "row_index": 4, "col_index": 4, "row_label": "a", "col_header": "Experimental MW", "value": "2314.8"}, {"table_index": 4, "row_index": 4, "col_index": 5, "row_label": "a", "col_header": "Retention timea", "value": "13.2"}, {"table_index": 4, "row_index": 4, "col_index": 6, "row_label": "a", "col_header": "Hydrophobicityb", "value": "0"}, {"table_index": 4, "row_index": 4, "col_index": 7, "row_label": "a", "col_header": "Helicity (%)c", "value": "18"}, {"table_index": 4, "row_index": 5, "col_index": 2, "row_label": "b", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 4, "row_index": 5, "col_index": 3, "row_label": "b", "col_header": "Theoretical MW", "value": "2319.5"}, {"table_index": 4, "row_index": 5, "col_index": 4, "row_label": "b", "col_header": "Experimental MW", "value": "2319.7"}, {"table_index": 4, "row_index": 5, "col_index": 5, "row_label": "b", "col_header": "Retention timea", "value": "17.2"}, {"table_index": 4, "row_index": 5, "col_index": 6, "row_label": "b", "col_header": "Hydrophobicityb", "value": "4.0"}, {"table_index": 4, "row_index": 5, "col_index": 7, "row_label": "b", "col_header": "Helicity (%)c", "value": "94"}, {"table_index": 4, "row_index": 6, "col_index": 2, "row_label": "c", "col_header": "Peptide sequence", "value": "Oct-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 4, "row_index": 6, "col_index": 3, "row_label": "c", "col_header": "Theoretical MW", "value": "2404.2"}, {"table_index": 4, "row_index": 6, "col_index": 4, "row_label": "c", "col_header": "Experimental MW", "value": "2403.8"}, {"table_index": 4, "row_index": 6, "col_index": 5, "row_label": "c", "col_header": "Retention timea", "value": "22.3"}, {"table_index": 4, "row_index": 6, "col_index": 6, "row_label": "c", "col_header": "Hydrophobicityb", "value": "9.1"}, {"table_index": 4, "row_index": 6, "col_index": 7, "row_label": "c", "col_header": "Helicity (%)c", "value": "71"}, {"table_index": 4, "row_index": 7, "col_index": 2, "row_label": "d", "col_header": "Peptide sequence", "value": "Lau-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 4, "row_index": 7, "col_index": 3, "row_label": "d", "col_header": "Theoretical MW", "value": "2460.3"}, {"table_index": 4, "row_index": 7, "col_index": 4, "row_label": "d", "col_header": "Experimental MW", "value": "2459.7"}, {"table_index": 4, "row_index": 7, "col_index": 5, "row_label": "d", "col_header": "Retention timea", "value": "22.8"}, {"table_index": 4, "row_index": 7, "col_index": 6, "row_label": "d", "col_header": "Hydrophobicityb", "value": "9.6"}, {"table_index": 4, "row_index": 7, "col_index": 7, "row_label": "d", "col_header": "Helicity (%)c", "value": "47"}, {"table_index": 4, "row_index": 8, "col_index": 2, "row_label": "e", "col_header": "Peptide sequence", "value": "Pal-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 4, "row_index": 8, "col_index": 3, "row_label": "e", "col_header": "Theoretical MW", "value": "2516.4"}, {"table_index": 4, "row_index": 8, "col_index": 4, "row_label": "e", "col_header": "Experimental MW", "value": "2516.9"}, {"table_index": 4, "row_index": 8, "col_index": 5, "row_label": "e", "col_header": "Retention timea", "value": "25.8"}, {"table_index": 4, "row_index": 8, "col_index": 6, "row_label": "e", "col_header": "Hydrophobicityb", "value": "12.6"}, {"table_index": 4, "row_index": 8, "col_index": 7, "row_label": "e", "col_header": "Helicity (%)c", "value": "53"}, {"table_index": 4, "row_index": 9, "col_index": 2, "row_label": "f", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWIAKIVGSI-Aun-NH2"}, {"table_index": 4, "row_index": 9, "col_index": 3, "row_label": "f", "col_header": "Theoretical MW", "value": "2503.3"}, {"table_index": 4, "row_index": 9, "col_index": 4, "row_label": "f", "col_header": "Experimental MW", "value": "2503.8"}, {"table_index": 4, "row_index": 9, "col_index": 5, "row_label": "f", "col_header": "Retention timea", "value": "20.3"}, {"table_index": 4, "row_index": 9, "col_index": 6, "row_label": "f", "col_header": "Hydrophobicityb", "value": "7.1"}, {"table_index": 4, "row_index": 9, "col_index": 7, "row_label": "f", "col_header": "Helicity (%)c", "value": "82"}, {"table_index": 4, "row_index": 10, "col_index": 2, "row_label": "g", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWI-NH2"}, {"table_index": 4, "row_index": 10, "col_index": 3, "row_label": "g", "col_header": "Theoretical MW", "value": "1650.2"}, {"table_index": 4, "row_index": 10, "col_index": 4, "row_label": "g", "col_header": "Experimental MW", "value": "1650.5"}, {"table_index": 4, "row_index": 10, "col_index": 5, "row_label": "g", "col_header": "Retention timea", "value": "12.1"}, {"table_index": 4, "row_index": 10, "col_index": 6, "row_label": "g", "col_header": "Hydrophobicityb", "value": "− 1.1"}, {"table_index": 4, "row_index": 10, "col_index": 7, "row_label": "g", "col_header": "Helicity (%)c", "value": "NDd"}, {"table_index": 4, "row_index": 11, "col_index": 2, "row_label": "h", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVUKWI-NH2"}, {"table_index": 4, "row_index": 11, "col_index": 3, "row_label": "h", "col_header": "Theoretical MW", "value": "1623.1"}, {"table_index": 4, "row_index": 11, "col_index": 4, "row_label": "h", "col_header": "Experimental MW", "value": "1623.4"}, {"table_index": 4, "row_index": 11, "col_index": 5, "row_label": "h", "col_header": "Retention timea", "value": "11.7"}, {"table_index": 4, "row_index": 11, "col_index": 6, "row_label": "h", "col_header": "Hydrophobicityb", "value": "− 1.5"}, {"table_index": 4, "row_index": 11, "col_index": 7, "row_label": "h", "col_header": "Helicity (%)c", "value": "ND"}]}, {"table_index": 5, "label": "PDF p8 table1", "caption": "from paper.pdf", "footnotes": [], "header_rows": [["A 100 80 editpep 60 a tcatni b f 40 d % c e 20 g h control 0 0 20 40 60 80 Time (min) B 0 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 Acyl K R L K K I G K V L(U) K W I P P I V G S I (Aun) NH 2 Peptide a Ac-21* 22-31 Peptide b Ac-21 22-31 15-21 24-31 Peptide c Oct-21* 22-31 Oct-14 15-23 15-21 Peptide d Lau-21 22-31 Lau-14 15-21 24-31 Peptide e Pal-31 Pal-14 15-21 24-31 Peptide f Ac-21 22-32 Aun Ac-23 15-21 24-32 Aun Peptide g Ac-21 22-24 Peptide h Ac-14* 15-24 15-23 *Not observed", "", "", "a b f d c e g h control", "", "", "", "", "", "", "", ""]], "longform_cells": [{"table_index": 5, "row_index": 2, "col_index": 2, "row_label": "", "col_header": "", "value": "0 12 13 14"}, {"table_index": 5, "row_index": 2, "col_index": 5, "row_label": "", "col_header": "", "value": "15 16 17 18 19 20 21"}, {"table_index": 5, "row_index": 2, "col_index": 6, "row_label": "", "col_header": "", "value": "22 23"}, {"table_index": 5, "row_index": 2, "col_index": 7, "row_label": "", "col_header": "", "value": "24"}, {"table_index": 5, "row_index": 2, "col_index": 8, "row_label": "", "col_header": "", "value": "25 26 27 28 29 30 31 32"}, {"table_index": 5, "row_index": 3, "col_index": 2, "row_label": "", "col_header": "", "value": "Acyl K R L K K I G K V L(U) K W I P P I V G S I (Aun) NH 2"}, {"table_index": 5, "row_index": 4, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide a"}, {"table_index": 5, "row_index": 4, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-21*"}, {"table_index": 5, "row_index": 4, "col_index": 6, "row_label": "", "col_header": "", "value": "22-31"}, {"table_index": 5, "row_index": 5, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide b"}, {"table_index": 5, "row_index": 5, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-21"}, {"table_index": 5, "row_index": 5, "col_index": 6, "row_label": "", "col_header": "", "value": "22-31"}, {"table_index": 5, "row_index": 6, "col_index": 5, "row_label": "", "col_header": "", "value": "15-21"}, {"table_index": 5, "row_index": 6, "col_index": 7, "row_label": "", "col_header": "", "value": "24-31"}, {"table_index": 5, "row_index": 7, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide c"}, {"table_index": 5, "row_index": 7, "col_index": 3, "row_label": "", "col_header": "", "value": "Oct-21*"}, {"table_index": 5, "row_index": 7, "col_index": 6, "row_label": "", "col_header": "", "value": "22-31"}, {"table_index": 5, "row_index": 8, "col_index": 3, "row_label": "", "col_header": "", "value": "Oct-14"}, {"table_index": 5, "row_index": 8, "col_index": 5, "row_label": "", "col_header": "", "value": "15-23"}, {"table_index": 5, "row_index": 9, "col_index": 5, "row_label": "", "col_header": "", "value": "15-21"}, {"table_index": 5, "row_index": 10, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide d"}, {"table_index": 5, "row_index": 10, "col_index": 3, "row_label": "", "col_header": "", "value": "Lau-21"}, {"table_index": 5, "row_index": 10, "col_index": 6, "row_label": "", "col_header": "", "value": "22-31"}, {"table_index": 5, "row_index": 11, "col_index": 3, "row_label": "", "col_header": "", "value": "Lau-14"}, {"table_index": 5, "row_index": 11, "col_index": 5, "row_label": "", "col_header": "", "value": "15-21"}, {"table_index": 5, "row_index": 11, "col_index": 7, "row_label": "", "col_header": "", "value": "24-31"}, {"table_index": 5, "row_index": 12, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide e Pal-31"}, {"table_index": 5, "row_index": 13, "col_index": 3, "row_label": "", "col_header": "", "value": "Pal-31"}, {"table_index": 5, "row_index": 14, "col_index": 3, "row_label": "", "col_header": "", "value": "Pal-14"}, {"table_index": 5, "row_index": 14, "col_index": 5, "row_label": "", "col_header": "", "value": "15-21"}, {"table_index": 5, "row_index": 14, "col_index": 7, "row_label": "", "col_header": "", "value": "24-31"}, {"table_index": 5, "row_index": 15, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide f"}, {"table_index": 5, "row_index": 15, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-21"}, {"table_index": 5, "row_index": 15, "col_index": 6, "row_label": "", "col_header": "", "value": "22-32 Aun"}, {"table_index": 5, "row_index": 16, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-23"}, {"table_index": 5, "row_index": 17, "col_index": 5, "row_label": "", "col_header": "", "value": "15-21"}, {"table_index": 5, "row_index": 17, "col_index": 7, "row_label": "", "col_header": "", "value": "24-32 Aun"}, {"table_index": 5, "row_index": 18, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide g"}, {"table_index": 5, "row_index": 18, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-21"}, {"table_index": 5, "row_index": 18, "col_index": 6, "row_label": "", "col_header": "", "value": "22-24"}, {"table_index": 5, "row_index": 19, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide h"}, {"table_index": 5, "row_index": 19, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-14*"}, {"table_index": 5, "row_index": 19, "col_index": 5, "row_label": "", "col_header": "", "value": "15-24"}, {"table_index": 5, "row_index": 20, "col_index": 5, "row_label": "", "col_header": "", "value": "15-23"}, {"table_index": 5, "row_index": 21, "col_index": 2, "row_label": "", "col_header": "", "value": "*Not observed"}]}, {"table_index": 6, "label": "PDF p9 table1", "caption": "from paper.pdf", "footnotes": [], "header_rows": [["Peptide", "Minimum selectivity index*", ""], ["", "IC50 /MIC", "MHC/MIC"]], "longform_cells": [{"table_index": 6, "row_index": 3, "col_index": 2, "row_label": "a", "col_header": "Minimum selectivity index*", "value": "> 16"}, {"table_index": 6, "row_index": 3, "col_index": 3, "row_label": "a", "col_header": "", "value": "> 8"}, {"table_index": 6, "row_index": 4, "col_index": 2, "row_label": "b", "col_header": "Minimum selectivity index*", "value": "≥ 1.6"}, {"table_index": 6, "row_index": 4, "col_index": 3, "row_label": "b", "col_header": "", "value": "≥ 1"}, {"table_index": 6, "row_index": 5, "col_index": 2, "row_label": "c", "col_header": "Minimum selectivity index*", "value": "≤ 1.6"}, {"table_index": 6, "row_index": 5, "col_index": 3, "row_label": "c", "col_header": "", "value": "< 0.5"}, {"table_index": 6, "row_index": 6, "col_index": 2, "row_label": "d", "col_header": "Minimum selectivity index*", "value": "< 0.2"}, {"table_index": 6, "row_index": 6, "col_index": 3, "row_label": "d", "col_header": "", "value": "≤ 0.1"}, {"table_index": 6, "row_index": 7, "col_index": 2, "row_label": "e", "col_header": "Minimum selectivity index*", "value": "< 0.2"}, {"table_index": 6, "row_index": 7, "col_index": 3, "row_label": "e", "col_header": "", "value": "< 0.2"}, {"table_index": 6, "row_index": 8, "col_index": 2, "row_label": "f", "col_header": "Minimum selectivity index*", "value": "< 1"}, {"table_index": 6, "row_index": 8, "col_index": 3, "row_label": "f", "col_header": "", "value": "< 0.5"}, {"table_index": 6, "row_index": 9, "col_index": 2, "row_label": "g", "col_header": "Minimum selectivity index*", "value": "> 8"}, {"table_index": 6, "row_index": 9, "col_index": 3, "row_label": "g", "col_header": "", "value": "> 4"}, {"table_index": 6, "row_index": 10, "col_index": 2, "row_label": "h", "col_header": "Minimum selectivity index*", "value": "≥ 6.8"}, {"table_index": 6, "row_index": 10, "col_index": 3, "row_label": "h", "col_header": "", "value": "> 4"}]}, {"table_index": 7, "label": "PDF p2 table1", "caption": "from 41598_2023_Article_41945.pdf", "footnotes": [], "header_rows": [["", "Peptide sequence", "Theoretical MW", "Experimental MW", "Retention timea", "Hydrophobicityb", "Helicity (%)c"], ["", "", "[M + H]+ calcd", "[M + H]+ exp", "tR (min)", "ΔtR", ""], ["PMAP-36", "*KRLKKIGKVLKWIPPIVGSIPLGCG-NH2", "", "", "", "", ""]], "longform_cells": [{"table_index": 7, "row_index": 4, "col_index": 2, "row_label": "a", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWIPPIVGSI-NH2"}, {"table_index": 7, "row_index": 4, "col_index": 3, "row_label": "a", "col_header": "Theoretical MW", "value": "2314.5"}, {"table_index": 7, "row_index": 4, "col_index": 4, "row_label": "a", "col_header": "Experimental MW", "value": "2314.8"}, {"table_index": 7, "row_index": 4, "col_index": 5, "row_label": "a", "col_header": "Retention timea", "value": "13.2"}, {"table_index": 7, "row_index": 4, "col_index": 6, "row_label": "a", "col_header": "Hydrophobicityb", "value": "0"}, {"table_index": 7, "row_index": 4, "col_index": 7, "row_label": "a", "col_header": "Helicity (%)c", "value": "18"}, {"table_index": 7, "row_index": 5, "col_index": 2, "row_label": "b", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 7, "row_index": 5, "col_index": 3, "row_label": "b", "col_header": "Theoretical MW", "value": "2319.5"}, {"table_index": 7, "row_index": 5, "col_index": 4, "row_label": "b", "col_header": "Experimental MW", "value": "2319.7"}, {"table_index": 7, "row_index": 5, "col_index": 5, "row_label": "b", "col_header": "Retention timea", "value": "17.2"}, {"table_index": 7, "row_index": 5, "col_index": 6, "row_label": "b", "col_header": "Hydrophobicityb", "value": "4.0"}, {"table_index": 7, "row_index": 5, "col_index": 7, "row_label": "b", "col_header": "Helicity (%)c", "value": "94"}, {"table_index": 7, "row_index": 6, "col_index": 2, "row_label": "c", "col_header": "Peptide sequence", "value": "Oct-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 7, "row_index": 6, "col_index": 3, "row_label": "c", "col_header": "Theoretical MW", "value": "2404.2"}, {"table_index": 7, "row_index": 6, "col_index": 4, "row_label": "c", "col_header": "Experimental MW", "value": "2403.8"}, {"table_index": 7, "row_index": 6, "col_index": 5, "row_label": "c", "col_header": "Retention timea", "value": "22.3"}, {"table_index": 7, "row_index": 6, "col_index": 6, "row_label": "c", "col_header": "Hydrophobicityb", "value": "9.1"}, {"table_index": 7, "row_index": 6, "col_index": 7, "row_label": "c", "col_header": "Helicity (%)c", "value": "71"}, {"table_index": 7, "row_index": 7, "col_index": 2, "row_label": "d", "col_header": "Peptide sequence", "value": "Lau-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 7, "row_index": 7, "col_index": 3, "row_label": "d", "col_header": "Theoretical MW", "value": "2460.3"}, {"table_index": 7, "row_index": 7, "col_index": 4, "row_label": "d", "col_header": "Experimental MW", "value": "2459.7"}, {"table_index": 7, "row_index": 7, "col_index": 5, "row_label": "d", "col_header": "Retention timea", "value": "22.8"}, {"table_index": 7, "row_index": 7, "col_index": 6, "row_label": "d", "col_header": "Hydrophobicityb", "value": "9.6"}, {"table_index": 7, "row_index": 7, "col_index": 7, "row_label": "d", "col_header": "Helicity (%)c", "value": "47"}, {"table_index": 7, "row_index": 8, "col_index": 2, "row_label": "e", "col_header": "Peptide sequence", "value": "Pal-KRLKKIGKVLKWIAKIVGSI-NH2"}, {"table_index": 7, "row_index": 8, "col_index": 3, "row_label": "e", "col_header": "Theoretical MW", "value": "2516.4"}, {"table_index": 7, "row_index": 8, "col_index": 4, "row_label": "e", "col_header": "Experimental MW", "value": "2516.9"}, {"table_index": 7, "row_index": 8, "col_index": 5, "row_label": "e", "col_header": "Retention timea", "value": "25.8"}, {"table_index": 7, "row_index": 8, "col_index": 6, "row_label": "e", "col_header": "Hydrophobicityb", "value": "12.6"}, {"table_index": 7, "row_index": 8, "col_index": 7, "row_label": "e", "col_header": "Helicity (%)c", "value": "53"}, {"table_index": 7, "row_index": 9, "col_index": 2, "row_label": "f", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWIAKIVGSI-Aun-NH2"}, {"table_index": 7, "row_index": 9, "col_index": 3, "row_label": "f", "col_header": "Theoretical MW", "value": "2503.3"}, {"table_index": 7, "row_index": 9, "col_index": 4, "row_label": "f", "col_header": "Experimental MW", "value": "2503.8"}, {"table_index": 7, "row_index": 9, "col_index": 5, "row_label": "f", "col_header": "Retention timea", "value": "20.3"}, {"table_index": 7, "row_index": 9, "col_index": 6, "row_label": "f", "col_header": "Hydrophobicityb", "value": "7.1"}, {"table_index": 7, "row_index": 9, "col_index": 7, "row_label": "f", "col_header": "Helicity (%)c", "value": "82"}, {"table_index": 7, "row_index": 10, "col_index": 2, "row_label": "g", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVLKWI-NH2"}, {"table_index": 7, "row_index": 10, "col_index": 3, "row_label": "g", "col_header": "Theoretical MW", "value": "1650.2"}, {"table_index": 7, "row_index": 10, "col_index": 4, "row_label": "g", "col_header": "Experimental MW", "value": "1650.5"}, {"table_index": 7, "row_index": 10, "col_index": 5, "row_label": "g", "col_header": "Retention timea", "value": "12.1"}, {"table_index": 7, "row_index": 10, "col_index": 6, "row_label": "g", "col_header": "Hydrophobicityb", "value": "− 1.1"}, {"table_index": 7, "row_index": 10, "col_index": 7, "row_label": "g", "col_header": "Helicity (%)c", "value": "NDd"}, {"table_index": 7, "row_index": 11, "col_index": 2, "row_label": "h", "col_header": "Peptide sequence", "value": "Ac-KRLKKIGKVUKWI-NH2"}, {"table_index": 7, "row_index": 11, "col_index": 3, "row_label": "h", "col_header": "Theoretical MW", "value": "1623.1"}, {"table_index": 7, "row_index": 11, "col_index": 4, "row_label": "h", "col_header": "Experimental MW", "value": "1623.4"}, {"table_index": 7, "row_index": 11, "col_index": 5, "row_label": "h", "col_header": "Retention timea", "value": "11.7"}, {"table_index": 7, "row_index": 11, "col_index": 6, "row_label": "h", "col_header": "Hydrophobicityb", "value": "− 1.5"}, {"table_index": 7, "row_index": 11, "col_index": 7, "row_label": "h", "col_header": "Helicity (%)c", "value": "ND"}]}, {"table_index": 8, "label": "PDF p8 table1", "caption": "from 41598_2023_Article_41945.pdf", "footnotes": [], "header_rows": [["A 100 80 editpep 60 a tcatni b f 40 d % c e 20 g h control 0 0 20 40 60 80 Time (min) B 0 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 Acyl K R L K K I G K V L(U) K W I P P I V G S I (Aun) NH 2 Peptide a Ac-21* 22-31 Peptide b Ac-21 22-31 15-21 24-31 Peptide c Oct-21* 22-31 Oct-14 15-23 15-21 Peptide d Lau-21 22-31 Lau-14 15-21 24-31 Peptide e Pal-31 Pal-14 15-21 24-31 Peptide f Ac-21 22-32 Aun Ac-23 15-21 24-32 Aun Peptide g Ac-21 22-24 Peptide h Ac-14* 15-24 15-23 *Not observed", "", "", "a b f d c e g h control", "", "", "", "", "", "", "", ""]], "longform_cells": [{"table_index": 8, "row_index": 2, "col_index": 2, "row_label": "", "col_header": "", "value": "0 12 13 14"}, {"table_index": 8, "row_index": 2, "col_index": 5, "row_label": "", "col_header": "", "value": "15 16 17 18 19 20 21"}, {"table_index": 8, "row_index": 2, "col_index": 6, "row_label": "", "col_header": "", "value": "22 23"}, {"table_index": 8, "row_index": 2, "col_index": 7, "row_label": "", "col_header": "", "value": "24"}, {"table_index": 8, "row_index": 2, "col_index": 8, "row_label": "", "col_header": "", "value": "25 26 27 28 29 30 31 32"}, {"table_index": 8, "row_index": 3, "col_index": 2, "row_label": "", "col_header": "", "value": "Acyl K R L K K I G K V L(U) K W I P P I V G S I (Aun) NH 2"}, {"table_index": 8, "row_index": 4, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide a"}, {"table_index": 8, "row_index": 4, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-21*"}, {"table_index": 8, "row_index": 4, "col_index": 6, "row_label": "", "col_header": "", "value": "22-31"}, {"table_index": 8, "row_index": 5, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide b"}, {"table_index": 8, "row_index": 5, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-21"}, {"table_index": 8, "row_index": 5, "col_index": 6, "row_label": "", "col_header": "", "value": "22-31"}, {"table_index": 8, "row_index": 6, "col_index": 5, "row_label": "", "col_header": "", "value": "15-21"}, {"table_index": 8, "row_index": 6, "col_index": 7, "row_label": "", "col_header": "", "value": "24-31"}, {"table_index": 8, "row_index": 7, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide c"}, {"table_index": 8, "row_index": 7, "col_index": 3, "row_label": "", "col_header": "", "value": "Oct-21*"}, {"table_index": 8, "row_index": 7, "col_index": 6, "row_label": "", "col_header": "", "value": "22-31"}, {"table_index": 8, "row_index": 8, "col_index": 3, "row_label": "", "col_header": "", "value": "Oct-14"}, {"table_index": 8, "row_index": 8, "col_index": 5, "row_label": "", "col_header": "", "value": "15-23"}, {"table_index": 8, "row_index": 9, "col_index": 5, "row_label": "", "col_header": "", "value": "15-21"}, {"table_index": 8, "row_index": 10, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide d"}, {"table_index": 8, "row_index": 10, "col_index": 3, "row_label": "", "col_header": "", "value": "Lau-21"}, {"table_index": 8, "row_index": 10, "col_index": 6, "row_label": "", "col_header": "", "value": "22-31"}, {"table_index": 8, "row_index": 11, "col_index": 3, "row_label": "", "col_header": "", "value": "Lau-14"}, {"table_index": 8, "row_index": 11, "col_index": 5, "row_label": "", "col_header": "", "value": "15-21"}, {"table_index": 8, "row_index": 11, "col_index": 7, "row_label": "", "col_header": "", "value": "24-31"}, {"table_index": 8, "row_index": 12, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide e Pal-31"}, {"table_index": 8, "row_index": 13, "col_index": 3, "row_label": "", "col_header": "", "value": "Pal-31"}, {"table_index": 8, "row_index": 14, "col_index": 3, "row_label": "", "col_header": "", "value": "Pal-14"}, {"table_index": 8, "row_index": 14, "col_index": 5, "row_label": "", "col_header": "", "value": "15-21"}, {"table_index": 8, "row_index": 14, "col_index": 7, "row_label": "", "col_header": "", "value": "24-31"}, {"table_index": 8, "row_index": 15, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide f"}, {"table_index": 8, "row_index": 15, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-21"}, {"table_index": 8, "row_index": 15, "col_index": 6, "row_label": "", "col_header": "", "value": "22-32 Aun"}, {"table_index": 8, "row_index": 16, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-23"}, {"table_index": 8, "row_index": 17, "col_index": 5, "row_label": "", "col_header": "", "value": "15-21"}, {"table_index": 8, "row_index": 17, "col_index": 7, "row_label": "", "col_header": "", "value": "24-32 Aun"}, {"table_index": 8, "row_index": 18, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide g"}, {"table_index": 8, "row_index": 18, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-21"}, {"table_index": 8, "row_index": 18, "col_index": 6, "row_label": "", "col_header": "", "value": "22-24"}, {"table_index": 8, "row_index": 19, "col_index": 2, "row_label": "", "col_header": "", "value": "Peptide h"}, {"table_index": 8, "row_index": 19, "col_index": 3, "row_label": "", "col_header": "", "value": "Ac-14*"}, {"table_index": 8, "row_index": 19, "col_index": 5, "row_label": "", "col_header": "", "value": "15-24"}, {"table_index": 8, "row_index": 20, "col_index": 5, "row_label": "", "col_header": "", "value": "15-23"}, {"table_index": 8, "row_index": 21, "col_index": 2, "row_label": "", "col_header": "", "value": "*Not observed"}]}, {"table_index": 9, "label": "PDF p9 table1", "caption": "from 41598_2023_Article_41945.pdf", "footnotes": [], "header_rows": [["Peptide", "Minimum selectivity index*", ""], ["", "IC50 /MIC", "MHC/MIC"]], "longform_cells": [{"table_index": 9, "row_index": 3, "col_index": 2, "row_label": "a", "col_header": "Minimum selectivity index*", "value": "> 16"}, {"table_index": 9, "row_index": 3, "col_index": 3, "row_label": "a", "col_header": "", "value": "> 8"}, {"table_index": 9, "row_index": 4, "col_index": 2, "row_label": "b", "col_header": "Minimum selectivity index*", "value": "≥ 1.6"}, {"table_index": 9, "row_index": 4, "col_index": 3, "row_label": "b", "col_header": "", "value": "≥ 1"}, {"table_index": 9, "row_index": 5, "col_index": 2, "row_label": "c", "col_header": "Minimum selectivity index*", "value": "≤ 1.6"}, {"table_index": 9, "row_index": 5, "col_index": 3, "row_label": "c", "col_header": "", "value": "< 0.5"}, {"table_index": 9, "row_index": 6, "col_index": 2, "row_label": "d", "col_header": "Minimum selectivity index*", "value": "< 0.2"}, {"table_index": 9, "row_index": 6, "col_index": 3, "row_label": "d", "col_header": "", "value": "≤ 0.1"}, {"table_index": 9, "row_index": 7, "col_index": 2, "row_label": "e", "col_header": "Minimum selectivity index*", "value": "< 0.2"}, {"table_index": 9, "row_index": 7, "col_index": 3, "row_label": "e", "col_header": "", "value": "< 0.2"}, {"table_index": 9, "row_index": 8, "col_index": 2, "row_label": "f", "col_header": "Minimum selectivity index*", "value": "< 1"}, {"table_index": 9, "row_index": 8, "col_index": 3, "row_label": "f", "col_header": "", "value": "< 0.5"}, {"table_index": 9, "row_index": 9, "col_index": 2, "row_label": "g", "col_header": "Minimum selectivity index*", "value": "> 8"}, {"table_index": 9, "row_index": 9, "col_index": 3, "row_label": "g", "col_header": "", "value": "> 4"}, {"table_index": 9, "row_index": 10, "col_index": 2, "row_label": "h", "col_header": "Minimum selectivity index*", "value": "≥ 6.8"}, {"table_index": 9, "row_index": 10, "col_index": 3, "row_label": "h", "col_header": "", "value": "> 4"}]}, {"table_index": 10, "label": "SUPP docx:41598_2023_41945_MOESM1_ESM.docx:t1", "caption": "supplement 41598_2023_41945_MOESM1_ESM.docx", "footnotes": [], "header_rows": [["Residue", "NH", "α", "β", "other"]], "longform_cells": [{"table_index": 10, "row_index": 2, "col_index": 5, "row_label": "Ac0", "col_header": "other", "value": "2.14"}, {"table_index": 10, "row_index": 3, "col_index": 2, "row_label": "Lys12", "col_header": "NH", "value": "7.66"}, {"table_index": 10, "row_index": 3, "col_index": 3, "row_label": "Lys12", "col_header": "α", "value": "4.15"}, {"table_index": 10, "row_index": 3, "col_index": 4, "row_label": "Lys12", "col_header": "β", "value": "1.95"}, {"table_index": 10, "row_index": 3, "col_index": 5, "row_label": "Lys12", "col_header": "other", "value": "γ 1.66; δ 1.86; ε -"}, {"table_index": 10, "row_index": 4, "col_index": 2, "row_label": "Arg13", "col_header": "NH", "value": "8.02"}, {"table_index": 10, "row_index": 4, "col_index": 3, "row_label": "Arg13", "col_header": "α", "value": "4.20"}, {"table_index": 10, "row_index": 4, "col_index": 4, "row_label": "Arg13", "col_header": "β", "value": "2.07, 2.00"}, {"table_index": 10, "row_index": 4, "col_index": 5, "row_label": "Arg13", "col_header": "other", "value": "γ 1.88, 1.82; δ 3.29; NHε 7.21"}, {"table_index": 10, "row_index": 5, "col_index": 2, "row_label": "Leu14", "col_header": "NH", "value": "7.36"}, {"table_index": 10, "row_index": 5, "col_index": 3, "row_label": "Leu14", "col_header": "α", "value": "4.25"}, {"table_index": 10, "row_index": 5, "col_index": 4, "row_label": "Leu14", "col_header": "β", "value": "-"}, {"table_index": 10, "row_index": 5, "col_index": 5, "row_label": "Leu14", "col_header": "other", "value": "γ -; δ 1.05, 0.97"}, {"table_index": 10, "row_index": 6, "col_index": 2, "row_label": "Lys15", "col_header": "NH", "value": "7.72"}, {"table_index": 10, "row_index": 6, "col_index": 3, "row_label": "Lys15", "col_header": "α", "value": "4.20"}, {"table_index": 10, "row_index": 6, "col_index": 4, "row_label": "Lys15", "col_header": "β", "value": "2.02"}, {"table_index": 10, "row_index": 6, "col_index": 5, "row_label": "Lys15", "col_header": "other", "value": "γ 1.70, 1.58; δ 1.85; ε 3.08; NHε 7.43"}, {"table_index": 10, "row_index": 7, "col_index": 2, "row_label": "Lys16", "col_header": "NH", "value": "8.21"}, {"table_index": 10, "row_index": 7, "col_index": 3, "row_label": "Lys16", "col_header": "α", "value": "3.92"}, {"table_index": 10, "row_index": 7, "col_index": 4, "row_label": "Lys16", "col_header": "β", "value": "-"}, {"table_index": 10, "row_index": 7, "col_index": 5, "row_label": "Lys16", "col_header": "other", "value": "γ -; δ -; ε -"}, {"table_index": 10, "row_index": 8, "col_index": 2, "row_label": "Ile17", "col_header": "NH", "value": "8.58"}, {"table_index": 10, "row_index": 8, "col_index": 3, "row_label": "Ile17", "col_header": "α", "value": "3.79"}, {"table_index": 10, "row_index": 8, "col_index": 4, "row_label": "Ile17", "col_header": "β", "value": "-"}, {"table_index": 10, "row_index": 8, "col_index": 5, "row_label": "Ile17", "col_header": "other", "value": "γ -"}, {"table_index": 10, "row_index": 9, "col_index": 2, "row_label": "Gly18", "col_header": "NH", "value": "8.11"}, {"table_index": 10, "row_index": 9, "col_index": 3, "row_label": "Gly18", "col_header": "α", "value": "4.03, 3.87"}, {"table_index": 10, "row_index": 10, "col_index": 2, "row_label": "Lys19", "col_header": "NH", "value": "7.77"}, {"table_index": 10, "row_index": 10, "col_index": 3, "row_label": "Lys19", "col_header": "α", "value": "4.22"}, {"table_index": 10, "row_index": 10, "col_index": 4, "row_label": "Lys19", "col_header": "β", "value": "2.04"}, {"table_index": 10, "row_index": 10, "col_index": 5, "row_label": "Lys19", "col_header": "other", "value": "γ 1.66, 1.56; ε 3.06; NHε 7.39"}, {"table_index": 10, "row_index": 11, "col_index": 2, "row_label": "Val20", "col_header": "NH", "value": "7.96"}, {"table_index": 10, "row_index": 11, "col_index": 3, "row_label": "Val20", "col_header": "α", "value": "3.92"}, {"table_index": 10, "row_index": 11, "col_index": 4, "row_label": "Val20", "col_header": "β", "value": "2.01"}, {"table_index": 10, "row_index": 11, "col_index": 5, "row_label": "Val20", "col_header": "other", "value": "γ 1.05"}, {"table_index": 10, "row_index": 12, "col_index": 2, "row_label": "Leu21", "col_header": "NH", "value": "7.72"}, {"table_index": 10, "row_index": 12, "col_index": 3, "row_label": "Leu21", "col_header": "α", "value": "4.20"}, {"table_index": 10, "row_index": 12, "col_index": 4, "row_label": "Leu21", "col_header": "β", "value": "1.85"}, {"table_index": 10, "row_index": 12, "col_index": 5, "row_label": "Leu21", "col_header": "other", "value": "-"}, {"table_index": 10, "row_index": 13, "col_index": 2, "row_label": "Lys22", "col_header": "NH", "value": "-"}, {"table_index": 10, "row_index": 13, "col_index": 3, "row_label": "Lys22", "col_header": "α", "value": "-"}, {"table_index": 10, "row_index": 13, "col_index": 4, "row_label": "Lys22", "col_header": "β", "value": "-"}, {"table_index": 10, "row_index": 13, "col_index": 5, "row_label": "Lys22", "col_header": "other", "value": "ND for overlapping"}, {"table_index": 10, "row_index": 14, "col_index": 2, "row_label": "Trp23", "col_header": "NH", "value": "8.07"}, {"table_index": 10, "row_index": 14, "col_index": 3, "row_label": "Trp23", "col_header": "α", "value": "4.57"}, {"table_index": 10, "row_index": 14, "col_index": 4, "row_label": "Trp23", "col_header": "β", "value": "3.67, 3.50"}, {"table_index": 10, "row_index": 14, "col_index": 5, "row_label": "Trp23", "col_header": "other", "value": "H1 9.16; H2 7.43; H4 7.7; H5 7.15; H6 7.24; H7 7.48"}, {"table_index": 10, "row_index": 15, "col_index": 2, "row_label": "Ile24", "col_header": "NH", "value": "8.61"}, {"table_index": 10, "row_index": 15, "col_index": 3, "row_label": "Ile24", "col_header": "α", "value": "3.71"}, {"table_index": 10, "row_index": 15, "col_index": 4, "row_label": "Ile24", "col_header": "β", "value": "2.11"}, {"table_index": 10, "row_index": 15, "col_index": 5, "row_label": "Ile24", "col_header": "other", "value": "γ 1.37; γ(CH3) 1.10; δ 1.02"}, {"table_index": 10, "row_index": 16, "col_index": 2, "row_label": "Ala25", "col_header": "NH", "value": "8.27"}, {"table_index": 10, "row_index": 16, "col_index": 3, "row_label": "Ala25", "col_header": "α", "value": "4.09"}, {"table_index": 10, "row_index": 16, "col_index": 4, "row_label": "Ala25", "col_header": "β", "value": "1.57"}, {"table_index": 10, "row_index": 17, "col_index": 2, "row_label": "Lys26", "col_header": "NH", "value": "7.77"}, {"table_index": 10, "row_index": 17, "col_index": 3, "row_label": "Lys26", "col_header": "α", "value": "4.10"}, {"table_index": 10, "row_index": 17, "col_index": 4, "row_label": "Lys26", "col_header": "β", "value": "-"}, {"table_index": 10, "row_index": 17, "col_index": 5, "row_label": "Lys26", "col_header": "other", "value": "-"}, {"table_index": 10, "row_index": 18, "col_index": 2, "row_label": "Ile27", "col_header": "NH", "value": "8.47"}, {"table_index": 10, "row_index": 18, "col_index": 3, "row_label": "Ile27", "col_header": "α", "value": "4.23"}, {"table_index": 10, "row_index": 18, "col_index": 4, "row_label": "Ile27", "col_header": "β", "value": "1.97"}, {"table_index": 10, "row_index": 18, "col_index": 5, "row_label": "Ile27", "col_header": "other", "value": "γ 1.62; γ(CH3) 1.15; δ 0.97"}, {"table_index": 10, "row_index": 19, "col_index": 2, "row_label": "Val28", "col_header": "NH", "value": "7.89"}, {"table_index": 10, "row_index": 19, "col_index": 3, "row_label": "Val28", "col_header": "α", "value": "3.91"}, {"table_index": 10, "row_index": 19, "col_index": 4, "row_label": "Val28", "col_header": "β", "value": "2.40"}, {"table_index": 10, "row_index": 19, "col_index": 5, "row_label": "Val28", "col_header": "other", "value": "γ 1.16"}, {"table_index": 10, "row_index": 20, "col_index": 2, "row_label": "Gly29", "col_header": "NH", "value": "8.08"}, {"table_index": 10, "row_index": 20, "col_index": 3, "row_label": "Gly29", "col_header": "α", "value": "3.79"}, {"table_index": 10, "row_index": 21, "col_index": 2, "row_label": "Ser30", "col_header": "NH", "value": "7.79"}, {"table_index": 10, "row_index": 21, "col_index": 3, "row_label": "Ser30", "col_header": "α", "value": "4.55"}, {"table_index": 10, "row_index": 21, "col_index": 4, "row_label": "Ser30", "col_header": "β", "value": "4.12, 3.99"}, {"table_index": 10, "row_index": 22, "col_index": 2, "row_label": "Ile31", "col_header": "NH", "value": "7.62"}, {"table_index": 10, "row_index": 22, "col_index": 3, "row_label": "Ile31", "col_header": "α", "value": "4.28"}, {"table_index": 10, "row_index": 22, "col_index": 4, "row_label": "Ile31", "col_header": "β", "value": "2.02"}, {"table_index": 10, "row_index": 22, "col_index": 5, "row_label": "Ile31", "col_header": "other", "value": "γ 1.64, 1.30; γ(CH3) 1.03; δ 0.94"}, {"table_index": 10, "row_index": 23, "col_index": 5, "row_label": "-NH2", "col_header": "other", "value": "7.25, 6.14"}]}, {"table_index": 11, "label": "SUPP docx:41598_2023_41945_MOESM1_ESM.docx:t2", "caption": "supplement 41598_2023_41945_MOESM1_ESM.docx", "footnotes": [], "header_rows": [["Residue", "NH", "α", "β", "other"]], "longform_cells": [{"table_index": 11, "row_index": 2, "col_index": 5, "row_label": "Ac0", "col_header": "other", "value": "2.15"}, {"table_index": 11, "row_index": 3, "col_index": 2, "row_label": "Lys12", "col_header": "NH", "value": "7.98"}, {"table_index": 11, "row_index": 3, "col_index": 3, "row_label": "Lys12", "col_header": "α", "value": "4.08"}, {"table_index": 11, "row_index": 3, "col_index": 4, "row_label": "Lys12", "col_header": "β", "value": "1.88, 1.79"}, {"table_index": 11, "row_index": 3, "col_index": 5, "row_label": "Lys12", "col_header": "other", "value": "γ 1.52; δ 1.64; ε 3.05"}, {"table_index": 11, "row_index": 4, "col_index": 2, "row_label": "Arg13", "col_header": "NH", "value": "7.93"}, {"table_index": 11, "row_index": 4, "col_index": 3, "row_label": "Arg13", "col_header": "α", "value": "4.12"}, {"table_index": 11, "row_index": 4, "col_index": 4, "row_label": "Arg13", "col_header": "β", "value": "1.98, 1.93"}, {"table_index": 11, "row_index": 4, "col_index": 5, "row_label": "Arg13", "col_header": "other", "value": "γ 1.78; δ 3.26; NHε 7.00"}, {"table_index": 11, "row_index": 5, "col_index": 2, "row_label": "Leu14", "col_header": "NH", "value": "7.31"}, {"table_index": 11, "row_index": 5, "col_index": 3, "row_label": "Leu14", "col_header": "α", "value": "4.25"}, {"table_index": 11, "row_index": 5, "col_index": 4, "row_label": "Leu14", "col_header": "β", "value": "1.87, 1.72"}, {"table_index": 11, "row_index": 5, "col_index": 5, "row_label": "Leu14", "col_header": "other", "value": "γ 1.67; δ 1.03, 0.95"}, {"table_index": 11, "row_index": 6, "col_index": 2, "row_label": "Lys15", "col_header": "NH", "value": "7.78"}, {"table_index": 11, "row_index": 6, "col_index": 3, "row_label": "Lys15", "col_header": "α", "value": "4.18"}, {"table_index": 11, "row_index": 6, "col_index": 4, "row_label": "Lys15", "col_header": "β", "value": "1.99"}, {"table_index": 11, "row_index": 6, "col_index": 5, "row_label": "Lys15", "col_header": "other", "value": "γ 1.61, 1.50; δ 1.77; ε 3.05"}, {"table_index": 11, "row_index": 7, "col_index": 2, "row_label": "Lys16", "col_header": "NH", "value": "7.62"}, {"table_index": 11, "row_index": 7, "col_index": 3, "row_label": "Lys16", "col_header": "α", "value": "4.16"}, {"table_index": 11, "row_index": 7, "col_index": 4, "row_label": "Lys16", "col_header": "β", "value": "1.93, 1.86"}, {"table_index": 11, "row_index": 7, "col_index": 5, "row_label": "Lys16", "col_header": "other", "value": "γ 1.38; δ 1.67; ε 3.05"}, {"table_index": 11, "row_index": 8, "col_index": 2, "row_label": "Ile17", "col_header": "NH", "value": "7.92"}, {"table_index": 11, "row_index": 8, "col_index": 3, "row_label": "Ile17", "col_header": "α", "value": "3.93"}, {"table_index": 11, "row_index": 8, "col_index": 4, "row_label": "Ile17", "col_header": "β", "value": "-"}, {"table_index": 11, "row_index": 8, "col_index": 5, "row_label": "Ile17", "col_header": "other", "value": "γ 1.01"}, {"table_index": 11, "row_index": 9, "col_index": 2, "row_label": "Gly18", "col_header": "NH", "value": "8.17"}, {"table_index": 11, "row_index": 9, "col_index": 3, "row_label": "Gly18", "col_header": "α", "value": "3.86"}, {"table_index": 11, "row_index": 10, "col_index": 2, "row_label": "Lys19", "col_header": "NH", "value": "7.71"}, {"table_index": 11, "row_index": 10, "col_index": 3, "row_label": "Lys19", "col_header": "α", "value": "4.15"}, {"table_index": 11, "row_index": 10, "col_index": 4, "row_label": "Lys19", "col_header": "β", "value": "1.98"}, {"table_index": 11, "row_index": 10, "col_index": 5, "row_label": "Lys19", "col_header": "other", "value": "γ 1.52; δ 1.79, 1.67; ε 3.06"}, {"table_index": 11, "row_index": 11, "col_index": 2, "row_label": "Val20", "col_header": "NH", "value": "7.49"}, {"table_index": 11, "row_index": 11, "col_index": 3, "row_label": "Val20", "col_header": "α", "value": "4.21"}, {"table_index": 11, "row_index": 11, "col_index": 4, "row_label": "Val20", "col_header": "β", "value": "1.92"}, {"table_index": 11, "row_index": 11, "col_index": 5, "row_label": "Val20", "col_header": "other", "value": "γ 0.96, 0.91"}, {"table_index": 11, "row_index": 12, "col_index": 2, "row_label": "Leu21", "col_header": "NH", "value": "7.83"}, {"table_index": 11, "row_index": 12, "col_index": 3, "row_label": "Leu21", "col_header": "α", "value": "3.93"}, {"table_index": 11, "row_index": 12, "col_index": 4, "row_label": "Leu21", "col_header": "β", "value": "2.30"}, {"table_index": 11, "row_index": 12, "col_index": 5, "row_label": "Leu21", "col_header": "other", "value": "γ 1.52; δ 1.12, 1.06"}, {"table_index": 11, "row_index": 13, "col_index": 2, "row_label": "Lys22", "col_header": "NH", "value": "8.10"}, {"table_index": 11, "row_index": 13, "col_index": 3, "row_label": "Lys22", "col_header": "α", "value": "4.25"}, {"table_index": 11, "row_index": 13, "col_index": 4, "row_label": "Lys22", "col_header": "β", "value": "1.81"}, {"table_index": 11, "row_index": 13, "col_index": 5, "row_label": "Lys22", "col_header": "other", "value": "γ 1.50; δ -; ε 3.06"}, {"table_index": 11, "row_index": 14, "col_index": 2, "row_label": "Trp23", "col_header": "NH", "value": "7.78"}, {"table_index": 11, "row_index": 14, "col_index": 3, "row_label": "Trp23", "col_header": "α", "value": "4.73"}, {"table_index": 11, "row_index": 14, "col_index": 4, "row_label": "Trp23", "col_header": "β", "value": "3.14"}, {"table_index": 11, "row_index": 14, "col_index": 5, "row_label": "Trp23", "col_header": "other", "value": "H1 9.10; H2 7.21; H4 7.18; H5 7.70; H6 7.24; H7 7.46"}, {"table_index": 11, "row_index": 15, "col_index": 2, "row_label": "Ile24", "col_header": "NH", "value": "7.49"}, {"table_index": 11, "row_index": 15, "col_index": 3, "row_label": "Ile24", "col_header": "α", "value": "4.20"}, {"table_index": 11, "row_index": 15, "col_index": 4, "row_label": "Ile24", "col_header": "β", "value": "1.93"}, {"table_index": 11, "row_index": 15, "col_index": 5, "row_label": "Ile24", "col_header": "other", "value": "γ 1.21"}, {"table_index": 11, "row_index": 16, "col_index": 5, "row_label": "-NH2", "col_header": "other", "value": "6.89"}]}, {"table_index": 12, "label": "SUPP docx:41598_2023_41945_MOESM1_ESM.docx:t3", "caption": "supplement 41598_2023_41945_MOESM1_ESM.docx", "footnotes": [], "header_rows": [["Residue", "NH", "α", "β", "other"]], "longform_cells": [{"table_index": 12, "row_index": 2, "col_index": 5, "row_label": "Ac0", "col_header": "other", "value": "2.14"}, {"table_index": 12, "row_index": 3, "col_index": 2, "row_label": "Lys12", "col_header": "NH", "value": "8.01"}, {"table_index": 12, "row_index": 3, "col_index": 3, "row_label": "Lys12", "col_header": "α", "value": "4.07"}, {"table_index": 12, "row_index": 3, "col_index": 4, "row_label": "Lys12", "col_header": "β", "value": "1.88"}, {"table_index": 12, "row_index": 3, "col_index": 5, "row_label": "Lys12", "col_header": "other", "value": "γ 1.53; δ 1.64; ε 3.05"}, {"table_index": 12, "row_index": 4, "col_index": 2, "row_label": "Arg13", "col_header": "NH", "value": "7.34"}, {"table_index": 12, "row_index": 4, "col_index": 3, "row_label": "Arg13", "col_header": "α", "value": "4.25"}, {"table_index": 12, "row_index": 4, "col_index": 4, "row_label": "Arg13", "col_header": "β", "value": "1.86"}, {"table_index": 12, "row_index": 4, "col_index": 5, "row_label": "Arg13", "col_header": "other", "value": "γ 1.69; δ 3.07; NHε 7.31"}, {"table_index": 12, "row_index": 5, "col_index": 2, "row_label": "Leu14", "col_header": "NH", "value": "7.95"}, {"table_index": 12, "row_index": 5, "col_index": 3, "row_label": "Leu14", "col_header": "α", "value": "4.12"}, {"table_index": 12, "row_index": 5, "col_index": 4, "row_label": "Leu14", "col_header": "β", "value": "1.94"}, {"table_index": 12, "row_index": 5, "col_index": 5, "row_label": "Leu14", "col_header": "other", "value": "γ 1.77; δ -"}, {"table_index": 12, "row_index": 6, "col_index": 2, "row_label": "Lys15", "col_header": "NH", "value": "7.65"}, {"table_index": 12, "row_index": 6, "col_index": 3, "row_label": "Lys15", "col_header": "α", "value": "4.28"}, {"table_index": 12, "row_index": 6, "col_index": 4, "row_label": "Lys15", "col_header": "β", "value": "1.98"}, {"table_index": 12, "row_index": 6, "col_index": 5, "row_label": "Lys15", "col_header": "other", "value": "γ 1.51; δ 1.67, 1.77; ε 3.05"}, {"table_index": 12, "row_index": 7, "col_index": 2, "row_label": "Lys16", "col_header": "NH", "value": "7.76"}, {"table_index": 12, "row_index": 7, "col_index": 3, "row_label": "Lys16", "col_header": "α", "value": "4.19"}, {"table_index": 12, "row_index": 7, "col_index": 4, "row_label": "Lys16", "col_header": "β", "value": "1.98"}, {"table_index": 12, "row_index": 7, "col_index": 5, "row_label": "Lys16", "col_header": "other", "value": "γ 1.60, 1.50; δ 1.77; ε 3.04"}, {"table_index": 12, "row_index": 8, "col_index": 2, "row_label": "Ile17", "col_header": "NH", "value": "7.85"}, {"table_index": 12, "row_index": 8, "col_index": 3, "row_label": "Ile17", "col_header": "α", "value": "3.97"}, {"table_index": 12, "row_index": 8, "col_index": 4, "row_label": "Ile17", "col_header": "β", "value": "1.98"}, {"table_index": 12, "row_index": 8, "col_index": 5, "row_label": "Ile17", "col_header": "other", "value": "γ 1.02"}, {"table_index": 12, "row_index": 9, "col_index": 2, "row_label": "Gly18", "col_header": "NH", "value": "8.08"}, {"table_index": 12, "row_index": 9, "col_index": 3, "row_label": "Gly18", "col_header": "α", "value": "3.91"}, {"table_index": 12, "row_index": 10, "col_index": 2, "row_label": "Lys19", "col_header": "NH", "value": "7.25"}, {"table_index": 12, "row_index": 10, "col_index": 3, "row_label": "Lys19", "col_header": "α", "value": "4.16"}, {"table_index": 12, "row_index": 10, "col_index": 4, "row_label": "Lys19", "col_header": "β", "value": "1.81"}, {"table_index": 12, "row_index": 10, "col_index": 5, "row_label": "Lys19", "col_header": "other", "value": "γ 1.33; δ 1.65; ε 3.38; NHε 7.10"}, {"table_index": 12, "row_index": 11, "col_index": 2, "row_label": "Val20", "col_header": "NH", "value": "7.68"}, {"table_index": 12, "row_index": 11, "col_index": 3, "row_label": "Val20", "col_header": "α", "value": "9.91"}, {"table_index": 12, "row_index": 11, "col_index": 4, "row_label": "Val20", "col_header": "β", "value": "2.25"}, {"table_index": 12, "row_index": 11, "col_index": 5, "row_label": "Val20", "col_header": "other", "value": "γ 1.11, 1.06"}, {"table_index": 12, "row_index": 12, "col_index": 2, "row_label": "Aib21", "col_header": "NH", "value": "8.07"}, {"table_index": 12, "row_index": 12, "col_index": 3, "row_label": "Aib21", "col_header": "α", "value": "-"}, {"table_index": 12, "row_index": 12, "col_index": 4, "row_label": "Aib21", "col_header": "β", "value": "1.54, 1.48"}, {"table_index": 12, "row_index": 13, "col_index": 2, "row_label": "Lys22", "col_header": "NH", "value": "7.66"}, {"table_index": 12, "row_index": 13, "col_index": 3, "row_label": "Lys22", "col_header": "α", "value": "4.16"}, {"table_index": 12, "row_index": 13, "col_index": 4, "row_label": "Lys22", "col_header": "β", "value": "1.95"}, {"table_index": 12, "row_index": 13, "col_index": 5, "row_label": "Lys22", "col_header": "other", "value": "γ 1.67, 1.51; δ 1.77; ε 3.06; NHε 7.03"}, {"table_index": 12, "row_index": 14, "col_index": 2, "row_label": "Trp23", "col_header": "NH", "value": "7.94"}, {"table_index": 12, "row_index": 14, "col_index": 3, "row_label": "Trp23", "col_header": "α", "value": "4.76"}, {"table_index": 12, "row_index": 14, "col_index": 4, "row_label": "Trp23", "col_header": "β", "value": "3.45, 3.38"}, {"table_index": 12, "row_index": 14, "col_index": 5, "row_label": "Trp23", "col_header": "other", "value": "H1 9.11; H2 7.25; H4 7.13; H5 7.72; H6 7.25; H7 7.45"}, {"table_index": 12, "row_index": 15, "col_index": 2, "row_label": "Ile24", "col_header": "NH", "value": "7.51"}, {"table_index": 12, "row_index": 15, "col_index": 3, "row_label": "Ile24", "col_header": "α", "value": "4.25"}, {"table_index": 12, "row_index": 15, "col_index": 4, "row_label": "Ile24", "col_header": "β", "value": "1.97"}, {"table_index": 12, "row_index": 15, "col_index": 5, "row_label": "Ile24", "col_header": "other", "value": "γ 1.25; γ(CH3) 0.97; δ 0.91"}, {"table_index": 12, "row_index": 16, "col_index": 5, "row_label": "-NH2", "col_header": "other", "value": "7.00, 6.00"}]}]

=== PRIMARY PAPER FULL TEXT (context only) ===
Use this ONLY to (a) confirm whether an organism/target/assay was tested in this paper (prevents false 'absent' calls), and (b) read an endpoint label. You may NOT cite full text as the `evidence` cell for is_database_error=true; that still requires a structured longform cell.
www.nature.com/scientificreports

OPEN

Structural and biological
characterization of shortened
derivatives of the cathelicidin
PMAP‑36
Barbara Biondi 1, Luigi de Pascale 2, Mario Mardirossian 2, Adriana Di Stasi 2, Matteo Favaro 3,
Marco Scocchi 2* & Cristina Peggion 1,3*
Cathelicidins, a family of host defence peptides in vertebrates, play an important role in the innate
immune response, exhibiting antimicrobial activity against many bacteria, as well as viruses and
fungi. This work describes the design and synthesis of shortened analogues of porcine cathelicidin
PMAP-36, which contain structural changes to improve the pharmacokinetic properties. In particular,
20-mers based on PMAP-36 (residues 12-31) and 13-mers (residues 12-24) with modification of amino
acid residues at critical positions and introduction of lipid moieties of different lengths were studied
to identify the physical parameters, including hydrophobicity, charge, and helical structure, required
to optimise their antibacterial activity. Extensive conformational analysis, performed by CD and
NMR, revealed that the substitution of Pro25-Pro26 with Ala25-Lys26 increased the α-helix content
of the 20-mer peptides, resulting in broad-spectrum antibacterial activity against Escherichia coli,
Staphylococcus aureus, Klebsiella pneumoniae, Acinetobacter baumannii, Pseudomonas aeruginosa
and Staphylococcus epidermidis strains. Interestingly, shortening to just 13 residues resulted in only
a slight decrease in antibacterial activity. Furthermore, two sequences, a 13-mer and a 20-mer,
did not show cytotoxicity against HaCat cells up to 64 µM, indicating that both derivatives are not
only effective but also selective antimicrobial peptides. In the short peptide, the introduction of the
helicogenic α-aminoisobutyric acid forced the helix toward a prevailing ­310 structure, allowing the
antimicrobial activity to be maintained. Preliminary tests of resistance to Ser protease chymotrypsin
indicated that this modification resulted in a peptide with an increased in vivo lifespan. Thus, some of
the PMAP-36 derivatives studied in this work show a good balance between chain length, antibacterial
activity, and selectivity, so they represent a good starting point for the development of even more
effective and proteolysis-resistant active peptides.
Antimicrobial resistance (AMR) is a serious threat to human health worldwide. Therefore, the interest in new
drug candidates with antimicrobial activity, as new agents that could substitute or complement conventional
antibiotics, is steadily ­increasing1. Antimicrobial peptides (AMPs) are an ancient class of molecules that form
a first line of defence in eukaryotes to combat microorganisms. Attention on this class of compounds has risen
because their most common mechanism of action targets bacterial membranes or other general structures, in
a manner different to most antibiotics, that typically target specific proteins or membrane ­components2. This
specific mode of action makes the development of bacterial resistance less likely to occur, thus making AMPs
promising antibacterial ­drugs3. Thousands of AMPs have now been isolated from a variety of natural sources
comprising microorganisms, plants, and animals including m
­ ammals4. The vast pool of natural antimicrobial
peptides offers a broad spectrum of biological activities to choose from, but often these compounds are not stable,
with a short half-life, and when used out of their innate immune context are often quite toxic to host cells. To
allow for clinical applications, it would be important to develop new artificial, optimised and long lived AMP
analogues that overcome the drawbacks of the natural p
­ eptides5.
Cathelicidins are a family of antimicrobial peptides in vertebrates that plays an important role in the innate
immune ­response6, 7. They contain highly variable C-terminal domains displaying direct antimicrobial activity
1
Institute of Biomolecular Chemistry, CNR, Padova Unit, Padova, Italy. 2Department of Life Sciences, University of
Trieste, Trieste, Italy. 3Department of Chemical Sciences, University of Padova, Padova, Italy. *email: mscocchi@
units.it; cristina.peggion@unipd.it

Scientific Reports |

(2023) 13:15132

| https://doi.org/10.1038/s41598-023-41945-1

1
Vol.:(0123456789)

www.nature.com/scientificreports/
against a variety of bacteria, fungi, and some virus and ­parasites8. Porcine myeloid PMAP-36 is a highly cationic,
36-amino acid long cathelicidin displaying antimicrobial activity (in vitro and in vivo)9, 10 as well as immunomodulatory ­properties11, 12. The N-terminal region is characterised by several charged residues and is organised as
an α-helical structure, interrupted by three proline residues (Pro25, Pro26 and Pro32) located at the C-terminal
­end12, 13. Helicity was predicted by helical wheel projections and then verified by circular dichroism measurements in phosphate buffer pH 7, with addition of 25% TFE. The presence of a cysteine (Cys35) determines the
formation of peptide homodimers with a total net charge of + 26. Dimerization probably occurs in storage form
of the peptide’s precursors in peripheral white blood c­ ells13.
The peptide displayed a broad spectrum of antibacterial activity against Gram+ and Gram− bacteria at µM
concentrations and against Candida as ­well10, 12–15, but it also exhibited a significant cytotoxicity which is likely
associated to its membranolytic ­activity13–16.
Structure–activity studies have been performed to improve the antimicrobial activity and reduce the cytotoxic
effects of this peptide. Monomerization did not affect the antibacterial properties of PMAP-3610, 12–15. On the
other hand, the N-terminal segment 1-24 fully retained a comparable antimicrobial activity to the entire peptide
and increased its selectivity for prokaryotic cells by showing lower haemolytic a­ ctivity15, while the shorter fragment 1-20 exhibited decreased p
­ otency13. Further truncation of the first six N-terminal residues of the peptide
1-24 to obtain the 18-mer peptide encompassing residues 7-24 of the native peptide instead resulted in a fully
active peptide, suggesting that hydrophobic residues upstream of the two prolines are more important for activity
than the six N-terminal ­residues14. In addition, Scheenstra et al. showed that the N-terminal truncation of 11
residues in the PMAP-36 monomer had little effect on killing of E. coli, while further truncation of the peptide
completely blocked its antibacterial ­activity12. All these data are consistent with the indication that the central
part of the molecules is the pharmacophore.
In this work, we designed and tested a series of shortened PMAP-36 analogues focusing on the 12-31 and
12-24 regions, which constitute the central and most active portion of PMAP-36.
The aim was to clarify the importance of the α-helical structure and to find the most active while least cytotoxic derivatives. The structures of these new analogues were analysed by CD and NMR and their antibacterial
effects, cytotoxicity and stability were studied. The results provide interesting new data for further optimization
of these molecules for future use as therapeutics.

Results

Design, synthesis, and physicochemical parameters of PMAP‑36 derivatives. The peptides
designed for this study are shortened analogues of PMAP-36, lacking the dispensable N-terminal portion 1-11
and covering the region between Lys12 and Ile31. The C-terminal portion 32-36 of the original PMAP-36 was
also removed to prevent kinking of the helical structure due to Pro32 and to avoid dimerization caused by Cys35.
The remaining 20-mer (12-31) (compound a, Table 1) contains two prolines that interrupt the helical structure
(Fig. 1). To evaluate the effects of extending the α-helical conformation to the entire sequence, a new compound
was designed in which Pro25 was replaced by Ala25 and Pro26 by Lys26 (compound b, Table 1), to also increase
the charge, which is important for antimicrobial activity. The hydrophobic and the cationic residues were inserted
in a manner that would increase the amphiphilic character of the resulting α-helix, as perceived in the helical
wheel projections (Fig. 1).
Furthermore, we prepared a series of analogues based on compound b ([A25,K26]-PMAP12-31) modified
by linking an acyl chain of different length. Analogues c, d, and e were prepared by respectively linking octanoic,
lauric, and palmitic acid to the N-terminus of the sequence. Thus, we investigated whether variations in the lipid
moiety could modulate the insertion of the derivatives into bacterial membranes, and if it could also influence
their antimicrobial potency. To investigate if the position of the lipid chain impacts the biologic effects, 11-aminoundecanoic acid (Aun) was linked to the C-terminus of compound b giving the analogue f. This analogue was
intended to be compared with analogue d to evaluate the different effects of lipidation at the N- and C-termini.

Peptide sequence

Theoretical MW

Experimental MW

Retention ­timea

Hydrophobicityb

[M + ­H] calcd

[M + ­H] exp

tR (min)

ΔtR

Helicity
(%)c

+

+

PMAP-36

*KRLKKIGKVLKWIPPIVGSIPLGCG-NH2

a

Ac-KRLKKIGKVLKWIPPIVGSI-NH2

2314.5

2314.8

13.2

0

18

b

Ac-KRLKKIGKVLKWIAKIVGSI-NH2

2319.5

2319.7

17.2

4.0

94

c

Oct-KRLKKIGKVLKWIAKIVGSI-NH2

2404.2

2403.8

22.3

9.1

71

d

Lau-KRLKKIGKVLKWIAKIVGSI-NH2

2460.3

2459.7

22.8

9.6

47

e

Pal-KRLKKIGKVLKWIAKIVGSI-NH2

2516.4

2516.9

25.8

12.6

53

f

Ac-KRLKKIGKVLKWIAKIVGSI-Aun-NH2

2503.3

2503.8

20.3

7.1

82

g

Ac-KRLKKIGKVLKWI-NH2

1650.2

1650.5

12.1

− 1.1

NDd

h

Ac-KRLKKIGKVUKWI-NH2

1623.1

1623.4

11.7

− 1.5

ND

Table 1.  List of PMAP-36 analogues and of their physico-chemical properties. *Omitted N-terminal
sequence = GRFRRLRKKTR. a Retention time refers to 5%—95%B ­(CH3CN/H2O, 9:1) over 30 min gradient,
C18 column; relative to compound a: bΔtR = ­tR(x)−tR(a), where x stays for peptides b–h; ccalculated from the
[θ]222 value in SDS ­solution17; dND, not determined for mixed helices. Aun: 11-aminoundecanoic acid; Aib, U:
α-aminoisobutyric acid.

Scientific Reports |
Vol:.(1234567890)

(2023) 13:15132 |

https://doi.org/10.1038/s41598-023-41945-1

2

www.nature.com/scientificreports/

Figure 1.  Helical wheel projections of [P25,P26]-PMAP12-31, compound a, (left) and [A25,K26]-PMAP12-31,
compound b (right). Cationic residues are in blue, hydrophobic residues in green. (https://​www.​donar​mstro​ng.​
com/​cgi-​bin/​wheel.​pl).
To exclude the possibility that any difference between lipidated and non lipidated peptides might be due to
the lack of the free positively charged N-terminal amino group, all non-lipidated analogues were acetylated at
their N-terminus. In this way the number of amides in peptides of the same length remained unmodified. Furthermore, all peptides were amidated at their C-terminus as is the natural PMAP-3613.
A shorter analogue with only 13 amino acids (derivative g) was also designed to test whether a further
shortening of the 20-mer derivative (a) could produce a compound capable of maintaining antibacterial activity. Since peptide shortening often leads to a decrease in helix stability, derivative h was also prepared, in which
Leu21 was replaced by α-aminoisobutyric acid (Aib, U). This non-proteinogenic amino acid is known for its
strong ability to promote helix folding in synthetic and natural s­ equences18–20. The complete series of PMAP-36
analogues is described in Table 1.

Conformational analysis of PMAP‑36 derivatives. The secondary structure of the peptides was

investigated by circular dichroism (CD) spectroscopy in various environments, including 0.2 mM potassiumphosphate buffer (aqueous solution, pH 7), 100 mM sodium dodecyl sulphate (SDS), and 2,2,2-trifluoroethanol
(TFE). As these peptides are active on membranes, we chose SDS, as SDS micelles represent a model mimicking the prokaryotic cell membrane. TFE, on the other hand, is a solvent that induces the formation of helical
­structures21.
All analogues showed an unordered conformation in aqueous solution with a negative peak in the region
around 200 nm (Fig. 2A).
Peptide a showed a modest helical structure (18% helicity) in the presence of SDS micelles, which are a first
approximation of the amphiphilic environment of biological membranes, while the substitution of Pro25 and
Pro26, respectively, by Ala and Lys, significantly increased the helical content (94% helicity) (Fig. 2A). The CD
spectrum of peptides b–f in SDS showed the typical three-band shape with two negative maxima at 208 and
222 nm, assigned to the n → π* transition and to the parallel component of the π→π* transition respectively, and
a positive maximum around 195 nm attributed to the antiparallel component of the π→π* transition (Fig. 2A).
The presence of an acyl chain of different lengths at the N-terminus in the analogues c, d, and e resulted in a
perturbation of the helical structure in the form of a decrease in helicity. In contrast, the introduction of Aun
at the C-terminus (peptide f) did not significantly affect the conformation of the peptide (Fig. 2A). A similar
behaviour was observed for the analogues c–f analysed in TFE, condition that however evidenced an anomalous
CD spectrum for peptide b (Fig. 2A), in which the observed ratio between molar ellipticities at 222 and 208 nm
was > 1, suggesting an aggregation phenomenon compatible with the presence of a coiled-coil ­structure16, 22.
The short peptides g and h showed an ordered conformation in SDS and TFE (Fig. 2B). CD spectra deviated
from those of a pure α-helix in both peptides. We observed a shift of one of the two negative maxima to around
205 nm, accompanied by a shoulder centred near 222 nm. Furthermore, the value of the ratio R([Θ]222/[Θ]204–206)
moves away from the ideal 1 of the α-helix with values around 0.4–0.5 typical of the ­310-helix, values that were
first ­theorised23 and then determined in the first unequivocal experimental CD spectrum reported for an ideal
right-handed ­310-helical ­peptide24, 25. The contribution of the ­310-helix conformation was different for peptides
g and h, and in the two different membrane mimetic environments studied.
CD spectra of peptide g in SDS showed a contribution, albeit modest, of the 3­ 10-helix, as evidenced by the
R([Θ]222/[Θ]204–206) value of 0.55 and by the shift of the negative maxima. At the same time, there was still a
relevant contribution of α-helix as evidenced by the very intense positive band at 195 nm. The contribution of
­310-helix appeared to be more significant in peptide h. Furthermore, to a R value of 0.55, the ellipticity at about
Scientific Reports |

(2023) 13:15132 |

https://doi.org/10.1038/s41598-023-41945-1

3
Vol.:(0123456789)

www.nature.com/scientificreports/

80

40

20

0

a
b
c
d
e
f

SDS
60

[θ]R x 10-3 (deg x cm2 x dmol-1)

60

[θ]R x 10-3 (deg x cm2 x dmol-1)

80

80

a
b
c
d
e
f

pH 7

40

20

0

60

40

20

0

-20

-20

-20

-40

-40

-40

200

220

240

200

260

220

240

260

200

Wavelength (nm)

Wavelength (nm)

a
b
c
d
e
f

TFE

[θ]R x 10-3 (deg x cm2 x dmol-1)

A

220

240

260

Wavelength (nm)

B
80

80

20

0

70

40

20

0

a
g
h

TFE

60

[θ]R x 10-3 (deg x cm2 x dmol-1)

40

a
g
h

60

[ θ]R x 10-3 (deg x cm2 x dmol-1)

[θ]R x 10-3 (deg x cm2 x dmol-1)

60

80

SDS

a
g
h

pH 7

50
40
30
20
10
0

-10
-20

-20

-40

-40

-20
-30

200

220

240

Wavelength (nm)

260

-40
200

220

240

260

Wavelength (nm)

200

220

240

260

Wavelength (nm)

Figure 2.  (A) CD spectra of PMAP12-31 a–f analogues in PBS, SDS and TFE, at 25 °C. (B) CD spectra of
peptides a, g and h in PBS, SDS and TFE, at 25 °C.
195 nm was only slightly positive in the case of peptide h. Both g and h showed low ellipticity at 195 nm in TFE
and R ratios of 0.55 and 0.58, respectively. These results could be due to an equilibrium of ­310- and α-helices and/
or from ­310 and α-helix segments that coexist in the same molecule.
We performed a 2D-NMR analysis in TFE-d2 solution to obtain a more in-depth view of the conformational
preference of some of the analogues, focussing on peptides a, b, g, and h.
The NMR spectra of a evidenced little dispersion of the proton resonances and extensive overlapping, suggesting poor organisation in helical structure (data not shown).
In contrast, peptides b, g, and h exhibited greater signal dispersion, indicating well-organised structures.
Complete assignment of proton resonances was established based on TOCSY and NOESY spectra, using the
Wüthrich’s ­procedure26 (Table S1–S3 and Figs. S1–S5 in Supporting Information).
In general, helical structures are readily identified by a series of consecutive NN(i, i + 1) NOEs, concomitant with αN(i, i + 3) N
­ OEs26–28. These connectivities, evident for b, g and h, reveal short interproton distances
(< 3.5 Å) that demonstrate helical structure, without distinguishing between the different helix t­ ypes27.
310-helix and α-helix are distinguished by the relative intensities of the intermediate range αN(i, i + 2) and
αN(i, i + 4) NOEs. It is known that ­310 -helices should display αN(i, i + 2) and αN(i, i + 3), whereas α-helices display
only αN(i, i + 3) and αN(i, i + 4) N
­ OEs26, 27, 29.

Scientific Reports |
Vol:.(1234567890)

(2023) 13:15132 |

https://doi.org/10.1038/s41598-023-41945-1

4

www.nature.com/scientificreports/

Figure 3.  (A) Fingerprint region of the NOESY spectrum (600 MHz) of peptide g in TFE solution (c = 1.2 mM,
T = 308 K). αN(i, i + 2), αN(i, i + 3), and αN(i, i + 4), cross-peaks are highlighted in red, green, and blue,
respectively. (B) Regions of the NOESY spectrum (600 MHz) of peptide h in TFE solution (c = 1.2 mM, T = 308
K). α/βN(i, i + 2) and α/βN(i, i + 3) cross-peaks are highlighted in red, and green, respectively.
In Fig. 3A the fingerprint region of the NOESY spectrum of peptide g is reported. Together with all sequential
cross peaks αN(i, i + 1), we observed two αN(i, i + 2), Leu14/Lys16 and Lys16/Gly18, several long range correlations involving αN(i, i + 3), Lys12/Lys15 and Leu14/Ile17, and αN(i, i + 4), Leu14/Gly18 and Gly18/Leu22. These
findings confirmed the adoption of a mixed 3­ 10-/ɑ-helical conformation for g.
Figure 3B shows regions of the NOESY spectrum of h. In the fingerprint region we observed all sequential
cross peaks αN(i, i + 1), three αN(i, i + 2), Lys12/Leu14, Leu14/Lys16 and Lys22/Ile24, and several intermediate-range correlations involving αN(i, i + 3), Ile17/Val20, Val20/Trp23 and Lys22/NH(C-terminus amide).
The βN(i, i + 3) signals involving Aib21 are observed in the aliphatic region. The absence of the long range α/
βN(i, i + 4) correlations is indicative of a more pronounced 3­ 10-helical character for peptide h, with respect to
peptide g.

Antibacterial and cytotoxicity of PMAP‑36 derivatives. All derivatives were tested on a representa-

tive panel of reference strains of Gram-positive and Gram-negative bacteria (Table 2). For this purpose, the
minimum concentration needed to inhibit bacterial growth (MIC) was measured. Peptide a effectively inhibited
all tested bacterial strains (MIC = 1–4 µM) with the sole exception of S. aureus (MIC = 64 µM). The substitution
of the two prolines in peptide b markedly changed the spectrum of activity, making the peptide active against S.
aureus but, at the same time, decreasing its antimicrobial activity against all other bacterial species by 2–8 times
(Table 2).
Lipopeptides c, d, and e generally decreased their antibacterial potency proportionally to the length of the
carbon chain. Interestingly, lipopeptide f with Aun at the C-terminus showed better activity than compound d,
bearing a lipid tail of the same length but at its N-terminus. The overall results with these lipopeptides suggest
that the addition of a lipid moiety to the peptides at the C-terminus of PMAP12-31 is less detrimental than at its
N-terminus, but does not improve antibacterial activity. The low solubility of compounds c, d and e in MüllerHinton broth (see Supporting Information Fig. S6) also limited the MIC assay to peptide concentrations below
64 µM and may have contributed to the scarce antimicrobial activity of these compounds.
Interestingly, the shorter derivatives g and h still resulted in active peptides with a comparable activity
spectrum to that of peptide a and only a slightly reduced activity (MIC = 2–8 µM, except against S. aureus
MIC > 64 µM). The substitution of Leu21 with Aib in peptide h did not substantially modify its antimicrobial
activity compared to peptide g (Table 2).
The effects of PMAP-36 derivatives were also observed in eukaryotic cells. To determine the viability of the
cells in the presence of the peptides, the metabolic MTT assay was performed using the HaCaT cell line incubated with different concentrations of each compound (Fig. 4A). Peptides a and g did not decrease cell viability
even at 64 µM after 24 h of incubation. On the contrary, peptide b affected cell viability, which dropped to 30%

Scientific Reports |

(2023) 13:15132 |

https://doi.org/10.1038/s41598-023-41945-1

5
Vol.:(0123456789)

www.nature.com/scientificreports/

Table 2.  Antibacterial activity (MIC) of PMAP-36 derivatives against Gram-negative and Gram-positive
bacteria. *MIC, minimum inhibitory concentration is the lowest peptide concentration causing no visible
growth after 18 h incubation in Mueller–Hinton broth at 37 °C. Values indicate the mode of three independent
tests. Coloured boxes indicate different antimicrobial activity: high activity (green) low or no activity (red).
Lipopeptides have not been tested above 32 µM due to their low solubility (see Supporting Information for
evaluation of aggregation).

(compared to an untreated control) at 16 µM and even further at higher concentrations of the compounds.
Lipopeptides c, d, e, and f showed significant cytotoxicity in the same range of concentrations required for
antimicrobial activity (8–16 µM), with HC50 values < 32 μM. Surprisingly, peptide h containing Aib, decreased
cell viability at a concentration of 8 µM to just 70% (compared to an untreated control) and is at or above the
50% viability value up to 32 μM. To determine whether the mechanism of cytotoxicity was due to membrane
disruption, a haemolysis assay was performed on red blood cells (RBCs). It was confirmed that peptides a, g,
and h had no membranolytic effect on erythrocytes (Fig. 4B). On the other hand, peptides b, and lipopeptides c,
d, e, and f showed a significant lytic effect at all concentrations tested, suggesting that the cytotoxicity observed
in eukaryotic cells were mainly due to membrane damage. Interestingly, peptide h, albeit slightly metabolically
cytotoxic to HaCaT cells, did not appear to damage erythrocytes (Fig. 4B). Therefore, further studies will be
needed to understand the mechanism of cytotoxicity of peptide h on the HaCaT cells.
Resistance to protease. The stability of the peptides in the presence of chymotrypsin was monitored by HPLC–
MS, analysing the fragments derived from the degradation of the peptide. All 20-mer analogues (a–f) are sensitive to chymotrypsin. The rate of peptide degradation was calculated as the percentage of intact peptide detected
at defined time points. All peptides were mostly degraded within the first 15 min of incubation, with the exception of the lipopeptide e and the short peptide h. After 90 min, 65% of the peptide e was still intact, indicating that palmitoylation protects against hydrolysis. For peptide h, which was designed with an Aib residue to
improve proteolytic resistance, 50% of the peptide was still intact after 90 min (Fig. 5A). The other peptides were
cleaved on the C-terminal side of Leu21 or Trp23 as the first cleavage observed. Successive degradations involve
Leu14 for all peptides (with the exception of a and h). Concerning 13-mer peptides (g and h), degradation at
position 21 occurred only for g and not for the Aib containing peptide h, for which Leu14 is the sensitive point
for chymotrypsin attack. A summary of the fragments detected for each peptide is shown in Fig. 5B.

Discussion. It is well known that the transition of AMP use from the laboratory to real applications is hampered by their poor pharmacokinetic properties. An effective way to overcome this weakness of AMPs is to
introduce structural changes that increase resistance to proteases, while maintaining or improving activity and,
at the same time limiting toxicity.
In this study, we synthesised and tested a series of PMAP-36 derivatives by shortening the sequence length,
changing amino acid residues at critical positions, and inserting lipid moieties. This helped to identify physical
parameters, including hydrophobicity, charge, and helicity, required to optimise the antibacterial activity and
selectivity of this peptide.
We first showed that the shortened PMAP12-31 peptide a, which is the monomeric central part of the natural
PMAP-36, exhibited extensive broad-spectrum antibacterial activity against E. coli, A. baumannii, K. pneumoniae,
P. aeruginosa, and S. epidermidis strains with MIC values of 1–4 µM. Interestingly, we found that this peptide
could be further shortened to 13-mer 12-24 (compound g) with only a 1–8-fold decrease in antibacterial potency,
depending on the pathogen. Interestingly, both compounds a and g were not cytotoxic against HaCaT cells up to
64 µM and not haemolytic, indicating that both derivatives are effective and selective antimicrobial compounds
(see Table 3 and Figs. S9, S10 in Supporting Information) and useful leads for further development. In addition,
A. baumannii and K. pneumoniae, which are among the most worrying pathogens due to their high degree of
­resistance30, and have never been tested against PMAP-36 derivatives, were found to be highly sensitive to both
compounds a and g. Peptide g is almost identical to the 12-mer peptide RI12 reported in Lyu et al.14 and Lv
et al.15, however, it contains an additional acetylated lysine at the N-terminus. Both peptides are not haemolytic
and are active against Gram-negative but are only scarcely active against Gram positive bacteria. The addition
of a charged residue in g increased the antimicrobial activity against the S. epidermidis strain.
Pro25 and Pro26 of peptide a were replaced by the two helical promoting residues Ala and Lys (compound
b) attempting to increase the amphipatic α-helix content of the peptide. CD analysis and NOESY spectrum
Scientific Reports |
Vol:.(1234567890)

(2023) 13:15132 |

https://doi.org/10.1038/s41598-023-41945-1

6

www.nature.com/scientificreports/

Figure 4.  Effects of PMAP-36 derivatives on the viability of the HaCaT cell line (A) and red blood cells (B). (A)
Cell viability was measured as absorbance at 570 nm after 24 h from the exposure to the peptides. Results are
reported as percentages of viable cells with respect to the untreated control cells (Unt) set as 100% of viability.
Data are the average ± SD of at least three independent experiments in internal duplicate (n = 6). *p < 0.05,
**p < 0.01, ***p < 0.001 versus the untreated control (Test t-student). (B) Haemolysis assay was performed
against 4% v/v suspension of ram red blood cells (RBCs) in PBS. Absorbance of released haemoglobin (540 nm)
were measured after 1 h exposure to the peptides. RBCs suspension with 1% Triton or without peptide
treatment were used to achieve 100% haemolysis and as negative haemolysis control (Unt), respectively. The
results are shown as a percentage with respect to of RBCs treated for 1 h with 1% Triton X-100. Data are the
average ± SD of three experiments (n = 3). *p < 0.05, ** p < 0.01, *** p < 0.001 versus the untreated sample (Test
t-student).
confirmed the significant increase in peptide structuration with 94% α-helical conformation in the presence of
membrane-mimetic environments. In addition, compound b displayed hydrophobicity higher than that of peptide a likely due to the enhanced amphipathicity of the helix, acquiring biological activity against S. aureus (MIC 4
µM), but at the same time decreasing activity 2–8-fold against the other strains. Furthermore, this compound also
showed an increase in cytotoxicity compared to compound a. Because compounds a and b have a similar charge,
the main differences are the increased helicity and hydrophobicity of b, which did not result in a more selective
peptide (Table 3). These results are consistent with those of other ­studies32, 33 in which high hydrophobicity and

Scientific Reports |

(2023) 13:15132 |

https://doi.org/10.1038/s41598-023-41945-1

7
Vol.:(0123456789)

www.nature.com/scientificreports/
A

100

% intact peptide

80

60
a
b
f
d
c
e
g
h
control

40

20

0
0

20

40

60

80

Time (min)
0 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32
Acyl K R L K K I G K V L(U) K W I P P I V G S I (Aun) NH2

B
Peptide a

Ac-21*

Peptide b

Ac-21

Peptide c

Oct-21*
Oct-14

22-31
22-31
24-31

15-21

22-31
15-23
15-21

Peptide d

La u-21
La u-14

15-21

22-31
24-31

Peptide e

Pa l -31
Pa l -14

15-21

24-31

Peptide f

Ac-21
Ac-23

Peptide g

Ac-21

Peptide h

Ac-14*

22-32
15-21

24-32

Aun
Aun

22-24
15-24
15-23

*Not obs erved

Figure 5.  (A) Chymotrypsin degradation of compounds a–h. The percentage of preserved peptide is
represented over time. We estimated the residual amount of intact peptide in a sample as the HPLC peak area.
(An example of the HPLC profiles with labelled peaks corresponding to hydrolysis products is reported in the
Supporting Information, Fig. S8). As a positive control we used the C-terminal portion of natural Endonuclease
V involved in the DNA repair mechanism that occurs after DNA damage caused by ultraviolet radiation. (B).
General sequences of peptides a–h and their degradation products by chymotrypsin. All peptide fragments
were detected by HPLC–MS (see Materials and Methods). Fragments obtained within a 30-min incubation with
chymotrypsin are indicated by dark grey colour; fragments obtained after longer incubation times are indicated
by light grey colour. White boxes indicate hypothetical fragments not detected. Vertical red bars in the general
sequence (top) indicate the position of observed cleavage sites.

amphipathicity (hydrophobic moment) were observed to be correlated with increased haemolytic activity, while
antimicrobial activity was found to be less dependent on these factors.
Scientific Reports |
Vol:.(1234567890)

(2023) 13:15132 |

https://doi.org/10.1038/s41598-023-41945-1

8

www.nature.com/scientificreports/

Minimum selectivity index*
Peptide

IC50 /MIC

a

> 16

>8

b

≥ 1.6

≥1
< 0.5

MHC/MIC

c

≤ 1.6

d

< 0.2

≤ 0.1

e

< 0.2

< 0.2
< 0.5

f

<1

g

>8

>4

h

≥ 6.8

>4

Table 3.  Selective antibacterial activity of PMAP-36 derivatives. *Minimum selectivity index is calculated as
ratio between cytotoxicity/haemolytic activity and MIC on at least five out of six bacterial species. The I­ C50 was
considered as the peptide concentration at which cell viability is reduced by 50% compared to the untreated
control. MHC was taken as the lowest concentration of peptides which induced 10% of haemolysis of red
blood ­cells31.

Structure–activity comparison was also performed on short 13-mer g and h compounds. Despite the short
sequences, both peptides exhibited a helical structure. To increase the helicity of peptide g, which may be hampered by end-effects due to its short length, we replaced Leu21 with the helicogenic residue Aib. Short peptides
containing Aib tend to adopt the ­310-helical ­conformation17–19, and, in fact, we could show, although the substitution did not have a significant effect on hydrophobicity, the presence of Aib induced the helix to adopt the
prevailing ­310 conformation, as demonstrated by CD analysis and the NOESY ­spectrum18–20. Similar to what
was observed above, the substitution of Leu21 increased helicity but again did not affect antimicrobial activity
although it somewhat increased cytotoxicity against HaCaT cells (even remaining non-haemolytic, see Fig. 4).
This result was unexpected and differs from the temporin-1DRa results obtained with the membranolytic frog
skin peptides, in which Aib substitutions increased both its antimicrobial and cytolytic a­ ctivities34.
We also tested the effects of elongating the acyl chain at the N-terminus of compound b (peptides c, d,
and e) and a lipid chain insertion at the C-terminus (peptide f) of length similar to that of compound d. The
lipopeptides showed a gradual decrease in helicity related to their lipid chain length compared with compound
b under membrane-like conditions (SDS micelles). At the same time, all lipidated derivatives tended to aggregate. Moreover, the lipidated derivatives showed lower antimicrobial activity and increased cytotoxicity with
respect to the compound b. However, in this respect, C-terminal lipidation was significantly less deleterious
than N-terminal modification.
Lipidation and acylation have been shown to promote the antimicrobial activity of several ­AMPs35, 36 and to
boost or modulate the antibacterial potential and the properties of already active ­AMPs37, also including some
­cathelicidins38, 39. However, this is not the case with our derivatives. The additional lipid chain has been shown
to promote aggregation (see Supporting Information) even at low concentrations, and the acylated peptides are
poorly active. The gradual decrease in helicity as a function of the length of the lipid tail length suggests that the
alkyl chains interfere with helical structuration reducing the antimicrobial activity of the peptides. This hypothesis is also supported by the behaviour of peptide f, in which the addition of a hydrophobic tail at the C-terminus
(Aun) did not affect helicity and partially affected its antibacterial potency. It resulted in higher antimicrobial
activity and lower cytotoxicity than that of peptide d endowed with an acyl chain (lauric acid) of comparable
length. These differences in activity are probably due to the higher helical content of compound f (82% versus
47%) compared to that of the related analogue d. However, in all cases, modification of compound b with lipid
tails did not improve the biological activity of the peptide.
The proteolytic degradation of bioactive peptides shortens their in vivo lifespan and may alter their pharmacological ­profile3. The tests of resistance to the serine protease chymotrypsin presented here indicated that most
PMAP-36 derivatives were susceptible to degradation and were hydrolysed by this protease within 10–20 min.
The only exceptions were palmitoylated peptide e and Aib-containing peptide h, which were less than 50%
degraded after 90 min.
The proteolytic fragment profile suggests that cleavage occurred at canonical ­sites40 between Leu14 and Lys15
and between Leu21 and Lys22. The introduction of Aib into the 13-mer compound h significantly reduced
susceptibility to chymotrypsin. In the future, Aib or other non-proteinogenic residues could be introduced to
obtain more stable peptides that retain antimicrobial activity and selectivity, ensuring that the peptides are not
cytotoxic. As a preliminary assessment of the pharmacokinetic potential of the peptides, we also performed
proteolytic degradation tests in serum for the most promising peptides g and h. Peptide g is rapidly degraded,
as already observed in the presence of chymotrypsin. On the contrary, peptide h is capable of withstanding up
to 180 min. Although this period is shorter than that observed in the presence of chymotrypsin, the result is
still interesting, since the composition of the serum places the peptide in a more unfavourable environment
(Supporting Information, Fig. S10). The observed resistance is reasonably attributable to the presence of the
Aib residue. To obtain a more detailed profile of peptide stability, this preliminary study in serum needs to be
extended to all peptide series.

Scientific Reports |

(2023) 13:15132 |

https://doi.org/10.1038/s41598-023-41945-1

9
Vol.:(0123456789)

www.nature.com/scientificreports/
In conclusion, we demonstrate that the α-helical cathelicidin PAMP-36 can be shortened to either side and
that its central part (residues from 12 to 24) substantially retains its structural characteristics and antimicrobial
activity against a wide spectrum of bacteria. We have also shown that the onset of a stable helical conformation
is an essential prerequisite for the maintenance of antibacterial activity, but also that an additional increase in
helicity and/or hydrophobicity does not improve the biological activities of peptides, as also indicated in the
­literature33. The derivatives g and h, which show the best ratio between activity/selectivity and peptide length,
emerged as an interesting starting point for further optimisation to make them more resistant to proteolysis.

Methods. Peptide synthesis. The solid phase peptide synthesis of the PMAP-36 analogues was performed
on the Rink Amide MBHA resin, using standard Fmoc chemistry p
­ rotocols41, 42. Deprotection of the Fmoc group
was carried out with a 20% piperidine solution in N,N-dimethylformamide (2 × 10 min), and for the activation
of the carboxylic groups, a mixture in a three-fold molar excess of amino acid and coupling reagent was used in
the presence of a six-fold excess of DIPEA. Reaction time for each coupling was 50 min. On-resin Nα-acetylation
was achieved using an A
­ c2O/DIPEA/DMF (1:0.5:20 ratio) mixture in DMF, reaction time 30 min. For the lipidated analogues, the introduction of the acyl chain was carried out on resin and required the pre-activation of
octanoic acid, lauric acid and palmitic acid in the presence of HBTU, HOBT, and DIPEA. Fmoc-Aun-OH is
commercially available (Iris Biotech GmbH, Marktredwitz, Germany) and requires the same activation protocol
as the other Fmoc-amino acids.
At the end of the synthesis, each peptide was cleaved from the resin using a mixture of TFA, TIS, and water
in a 95:2.5:2.5 ratio. The filtrates were collected and concentrated under a flow of nitrogen, and the crude peptide was precipitated by the addition of diethyl ether. The crude peptides were purified by flash chromatography
on an Isolera Prime chromatographer (Biotage, Uppsala, Sweden) using a SNAP Cartridge KP-C18-HS 12g or
preparative RP-HPLC on a Phenomenex C18 column (22.1 mm × 250 mm, 10 μm, 300 Å) using an Akta Pure
GE Healthcare (Little Chalfont, U.K.) LC system equipped with an ultraviolet detector (flow rate of 15 mL/
min) and a binary elution system: A, H
­ 2O; B, C
­ H3CN/H2O [9:1 (v/v)]; gradient from 25 to 55% B in 30 min.
The purified fractions were characterised by analytical HPLC–MS on a Phenomenex Kinetex XB-C18 column
(4.6 mm × 100 mm, 3.5 μm, 100 Å) with an Agilent Technologies 1260 Infinity II HPLC system and a 6130
quadrupole LC/MS instrument. All compounds were > 95% pure.
The lyophilised peptides were then resuspended in DMSO (Sigma-Aldrich) and quantified using an Ultrospec
2100 pro spectrophotometer (Amersham Biosciences, Amersham, UK). Peptide concentrations were calculated
spectrophotometrically using the absorbance at 280 nm and the molar extinction coefficients of tryptophan
(ε = 5500/M cm). All peptides were stored frozen at – 20 °C.
Circular dichroism. The electronic CD curves in the far-UV region (below 260 nm) were obtained on a Jasco
(Tokyo, Japan) model J-1500 spectropolarimeter with a fused quartz cell of 0.02 cm pathlength (Hellma, Mühlheim, Germany). The values are expressed in terms of [θ]R, the molar ellipticity per residue (deg × ­cm2/dmol).
Spectra were recorded at room temperature in water, in spectrograde TFE (99.9% Acros Organics, Geel, Belgium) and 100 mM SDS solution at 3 × ­10−4 M peptide concentration. The final molar peptide-to-lipid ratio is
1:300.
NMR. The monodimensional and correlated spectroscopy (COSY)/total correlation spectroscopy (TOCSY)
and NOESY 2D NMR spectra of the

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Sheep erythrocytes", "db_measure": "57% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "100% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Sheep erythrocytes", "db_measure": "65% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "100% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Sheep erythrocytes", "db_measure": "60% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "100% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Sheep erythrocytes", "db_measure": "80% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "100% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Sheep erythrocytes", "db_measure": "0% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "NA", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "DBAASP", "db_subject_text": "Sheep erythrocytes", "db_measure": "0% Hemolysis", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DBAASP", "db_subject_text": "Human keratinocytes HaCat", "db_measure": "45% Cell death", "db_value": "", "db_unit": "µM", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).