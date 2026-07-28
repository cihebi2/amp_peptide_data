
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
doi__10.1038_s41598-023-45875-w

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 3", "caption": "List of some of the major AMPs identified from C. splendens using APD3, CAMP R3 and LAMP databases.", "footnotes": [], "header_rows": [["Unigenes ID", "AMP"], ["CL35Contig1", "Ubiquitin"], ["CL10522Contig1", "Ubiquicidin"], ["CL516Contig1", "Histone H2B 1/2/3/4/6"], ["CL1Contig2038", "Histone H4"], ["CL17878Contig1", "Histone H2B type 2-E"], ["CL10566Contig1", "HNr (histone-derived)"], ["CL10566Contig1", "Histone H2A"], ["CL516Contig2", "Histone H3"], ["CL63204Contig1", "Beta-defensin (Fragment)"], ["CL60147Contig1", "Gallinacin-2"], ["CL64604Contig1", "Gallinacin-13"], ["CL59522Contig1", "Gallinacin-5"], ["CL1Contig2041", "Beta-defensin 9"], ["CL1Contig2041", "Gallinacin 6"], ["CL26196Contig1", "Defensin-like fragment"], ["CL48257Contig1", "Beta-amyloid peptide (1–42)"], ["CL60229Contig1", "Beta-amyloid peptide (1–40)"], ["CL31589Contig1", "Cathelicidin-2"], ["CL8444Contig1", "rtCATH-1b (cathelicidin, fish, animals)"], ["CL26031Contig1", "Liver-expressed antimicrobial peptide 2"], ["CL26031Contig1", "Hepcidin"], ["CL23973Contig1", "Neuropeptide Y"], ["CL44565Contig1", "Enkelytin"], ["CL44565Contig1", "Proenkephalin-A"], ["CL23973Contig1", "Bradykinin"], ["CL44349Contig1", "Vasoactive intestinal polypeptide"], ["CL52025Contig1", "Vasostatin-1"], ["CL44349Contig1", "Calcitonin gene-related peptide"], ["CL540Contig1", "Enhancer of rudimentary homolog"], ["CL22143Contig1", "Ovotransferrin"], ["CL50263Contig1", "CCL8"], ["CL7703Contig1", "Pleiotrophin-A"], ["CL50263Contig1", "CXCL12"], ["CL44565Contig1", "Bombinin H7"]], "longform_cells": []}, {"table_index": 2, "label": "Table 1", "caption": "Raw read summary.", "footnotes": [], "header_rows": [["Samples", "Total sequences", "Sequence length", "% GC"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "Set1_R1.fastq.gz", "col_header": "Total sequences", "value": "23,785,322"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "Set1_R1.fastq.gz", "col_header": "Sequence length", "value": "76"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "Set1_R1.fastq.gz", "col_header": "% GC", "value": "47"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "Set1_R2.fastq.gz", "col_header": "Total sequences", "value": "23,785,322"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "Set1_R2.fastq.gz", "col_header": "Sequence length", "value": "76"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "Set1_R2.fastq.gz", "col_header": "% GC", "value": "47"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Set2_R1.fastq.gz", "col_header": "Total sequences", "value": "59,779,517"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Set2_R1.fastq.gz", "col_header": "Sequence length", "value": "100"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "Set2_R1.fastq.gz", "col_header": "% GC", "value": "51"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Set2_R2.fastq.gz", "col_header": "Total sequences", "value": "59,779,517"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Set2_R2.fastq.gz", "col_header": "Sequence length", "value": "100"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "Set2_R2.fastq.gz", "col_header": "% GC", "value": "51"}]}, {"table_index": 3, "label": "Table 2", "caption": "Assembly statistics of transcripts and unigenes.", "footnotes": [], "header_rows": [["Assembly statistics", "Transcripts", "Unigenes"]], "longform_cells": [{"table_index": 3, "row_index": 2, "col_index": 2, "row_label": "Total sequence length", "col_header": "Transcripts", "value": "353,951,778"}, {"table_index": 3, "row_index": 2, "col_index": 3, "row_label": "Total sequence length", "col_header": "Unigenes", "value": "126,484,523"}, {"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "Minimum sequence length", "col_header": "Transcripts", "value": "185"}, {"table_index": 3, "row_index": 3, "col_index": 3, "row_label": "Minimum sequence length", "col_header": "Unigenes", "value": "201"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "Maximum sequence length", "col_header": "Transcripts", "value": "38,885"}, {"table_index": 3, "row_index": 4, "col_index": 3, "row_label": "Maximum sequence length", "col_header": "Unigenes", "value": "38,887"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "Average sequence length", "col_header": "Transcripts", "value": "1030.40"}, {"table_index": 3, "row_index": 5, "col_index": 3, "row_label": "Average sequence length", "col_header": "Unigenes", "value": "1687.40"}, {"table_index": 3, "row_index": 6, "col_index": 2, "row_label": "N10", "col_header": "Transcripts", "value": "7826"}, {"table_index": 3, "row_index": 6, "col_index": 3, "row_label": "N10", "col_header": "Unigenes", "value": "8828"}, {"table_index": 3, "row_index": 7, "col_index": 2, "row_label": "N20", "col_header": "Transcripts", "value": "5796"}, {"table_index": 3, "row_index": 7, "col_index": 3, "row_label": "N20", "col_header": "Unigenes", "value": "6704"}, {"table_index": 3, "row_index": 8, "col_index": 2, "row_label": "N30", "col_header": "Transcripts", "value": "4547"}, {"table_index": 3, "row_index": 8, "col_index": 3, "row_label": "N30", "col_header": "Unigenes", "value": "5370"}, {"table_index": 3, "row_index": 9, "col_index": 2, "row_label": "N40", "col_header": "Transcripts", "value": "3603"}, {"table_index": 3, "row_index": 9, "col_index": 3, "row_label": "N40", "col_header": "Unigenes", "value": "4335"}, {"table_index": 3, "row_index": 10, "col_index": 2, "row_label": "N50", "col_header": "Transcripts", "value": "2747"}, {"table_index": 3, "row_index": 10, "col_index": 3, "row_label": "N50", "col_header": "Unigenes", "value": "3467"}, {"table_index": 3, "row_index": 11, "col_index": 2, "row_label": "Percent GC", "col_header": "Transcripts", "value": "46.62%"}, {"table_index": 3, "row_index": 11, "col_index": 3, "row_label": "Percent GC", "col_header": "Unigenes", "value": "46.36%"}]}, {"table_index": 4, "label": "Table 4", "caption": "Primer sequences for real time PCR.", "footnotes": [], "header_rows": [["Gene name", "Forward primer", "Reverse primer"], ["Avian beta-defensin 2 (AvBD-2)", "ACAGCCATGAAGATCCTTTACC", "GGCAAAGACAAACCTGGAGA"], ["Avian beta-defensin 13 (AvBD-13)", "CAGCAGTGCAGAAGCAACC", "ATTGCTGCAGCTCCCTTC"], ["Cathelicidin 2 (CATH-2)", "CCGTGGATTCCTACAACCAG", "TCCATCATGCTGAAGTTGAGTC"], ["β- actin", "CCCCACCTGAGCGTAAATACT", "CCTGCTTGCTGATCCACAT"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "APD6 entry text for Corvus CATH-2", "db_measure": "MIC values in µg/ml match converted primary values; hemolysis text says 2% human RBC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "CATH-2 (Cathelicidin 2)"}]

Return ONLY the JSON array now (one object per assertion above).