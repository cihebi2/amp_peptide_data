
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
doi__10.1371_journal.pone.0033351

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Plasmids used in this study.", "footnotes": ["Ampr = ampicillin resistance; Cmr = chloramphenicol resistance; ORF = open reading frame; PBAD = araC PBAD activator-promoter."], "header_rows": [["Plasmid", "Resistance", "Relevant genotype", "Origin"], ["pSYM1", "None", "mcsS, mcsI, mcsA, mcsB", "This work"], ["pST76–A", "Ampr", "oriTS (30°C)", "[43]"], ["pSYM1–ST76An", "Ampr", "mcsS, mcsI, mcsA, mcsB", "This work"], ["pAZ6", "Ampr", "mcsS, mcsI, mcsA, mcsB", "This work"], ["pAZ8", "Ampr", "mcsI, mcsA, mcsB", "This work"], ["pAZ9", "Cmr", "mcsS", "This work"], ["pAZ10", "Cmr", "ORF1", "This work"], ["pAZ11", "Cmr", "ORF2", "This work"], ["pAZ12", "Cmr", "mcsS 193–363", "This work"], ["pAZ13", "Ampr", "mcsI", "This work"], ["pAZ14", "Ampr", "mcsI 361–651", "This work"], ["pGS1", "Ampr", "PBAD", "This work"], ["pAZ15", "Ampr", "PBAD, mcsS", "This work"]], "longform_cells": []}, {"table_index": 2, "label": "Table 2", "caption": "Bacterial strains used in this study.", "footnotes": ["DSM17252; EcNDS = E. coli Nissle 1917 deletion strain; Ampr = ampicillin resistance; Kanar = kanamycin resistance; Cmr = chloramphenicol resistance."], "header_rows": [["Strain", "Relevant genotype", "Origin"], ["E. coli Nissle 1917 DSM6601 [42]", "Wild-type", "Mutaflor, Ardeypharm"], ["EcNDS20", "?mcmA, ?mchB", "This work"], ["EcNDS23", "?mcmA", "This work"], ["EcNDS24", "?mchB", "This work"], ["E. coli G1/2", "Wild-type", "Symbioflor 2a, SymbioPharm"], ["E. coli G3/10", "Wild-type", "Symbioflor 2a, SymbioPharm"], ["E. coli G4/9", "Wild-type", "Symbioflor 2a, SymbioPharm"], ["E. coli G5", "Wild-type", "Symbioflor 2a, SymbioPharm"], ["E. coli G6/7", "-type Wild", "Symbioflor 2a, SymbioPharm"], ["E. coli G8", "Wild-type", "Symbioflor 2a, SymbioPharm"], ["E. coli MDS42 [23]", "E. coli K-12 multiple deletion strain", "F. Blattner, University of Wisconsin - Madison, USA"], ["EPEC E2348/69 [20]", "Ampr (pUC19), Kanar (pUC4k) or Cmr (pACYC184)", "Human isolate"]], "longform_cells": []}, {"table_index": 3, "label": "Table 3", "caption": "Oligonucleotide primers used in this study.", "footnotes": ["Oligonucleotides were synthesized by Biomers, Ulm, Germany."], "header_rows": [["Oligonucleotide", "Sequence (5′→ 3′)", "Function"], ["mcm-H1", "cttaaagcgttacataggcaccattatcatataatgaagcaccgattgtgtaggctggagctgcttc", "EcN deletion primer"], ["mcm-H2", "gaatttttacttcttcacaaatcttatagcgaaggtgttgaaatggtccatatgaatatcctcctta", "EcN deletion primer"], ["mch-H1", "atcaacgactgtaaatcatatcttcatcagtaaagtgttgaacgattgtgtaggctggagctgcttc", "EcN deletion primer"], ["mch-H2", "ggtcaggctggaaaaacggaagttaaatatgatggagtttatatggtccatatgaatatcctcctta", "EcN deletion primer"], ["mcm_for", "cgttcggaggagcctaac", "EcN deletion primer/sequencing"], ["mcm_rev", "gattcatgggattcgaagg", "EcN deletion primer/sequencing"], ["Contig49_for", "cagctggatatcctgcgcg", "pSYM1 sequencing primer"], ["Contig49_rev", "ggttgcccggcatccaacg", "pSYM1 sequencing primer"], ["pSYM1-SalIHF", "tcaattgtgtcgactcaattactcttgtgag", "pAZ6/pAZ8 cloning primer"], ["pSYM1-NheI", "catgtaatagtgctagcatgttaaaatttataag", "pAZ6 cloning primer"], ["pSYM1-NheIac", "caaaaataatagctagcaagtgatgttttgtaatg", "pAZ8, pAZ12 cloning primer"], ["ac-EcoRI", "ctcgaattcatccattacaaaacatcac", "pAZ9 cloning primer"], ["ac-PstI", "ctggctgcagtaattgttcaggaagtaacg", "pAZ9 cloning primer"], ["pSYM1_44–EcoRI", "taggaattcagaggaactattggtggg", "pAZ10 cloning primer"], ["pSYM1_44–PstI", "ctccgctgcagacttacttatcgactacaggtaccac", "pAZ10 cloning primer"], ["ab-EcoRI", "gttagaattcataagagggatttttatgtcaaatatc", "pAZ11 cloning primer"], ["ab-PstI", "gttgatactgcagcttatcgactacaggtaccacc", "pAZ11 cloning primer"], ["pAZ9-HindIII", "cccaagcttagttaaatgtgctaatgctgtc", "pAZ12 cloning primer"], ["pAZ9-SalI", "ggcatcggtcgacgcaac", "pAZ12 cloning primer"], ["pSYM1_43–NheI", "cattgctagccatcacagataaactggataac", "pAZ14 cloning primer"], ["pSYM1_43–SalI", "ccctgagtcgactcatggttataaaatattttg", "pAZ13, pAZ14 cloning primer"], ["recA–ff", "atggctatcgacgaaaacaaac", "Multiplex PCR inhibition control"], ["recA–rev", "ttaaaaatcttcgttagtttctgc", "Multiplex PCR inhibition control"], ["mcsS–ff", "atgtcaaatatcagagaattgag", "mcsS PCR screening primer"], ["mcsS–rev", "ttatcgactacaggtaccacc", "mcsS PCR screening primer"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "Microcin S (MccS)", "db_measure": "Anti-Gram-", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "Microcin S", "db_measure": "Antibacterial; predicted", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "dbAMP", "db_subject_text": "Microcin S", "db_measure": "Antibacterial AntiGram -", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).