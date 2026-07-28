
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
6. ABSENCE IS NOT ERROR (critical): you are given ONLY some tables, never the whole paper. If a DB
   organism/target/value is not in the provided cells, you MUST return "not_in_provided_tables" with
   is_database_error=false. NEVER conclude the database is wrong merely because something is missing
   from the tables you were given -- it may be in a figure, supplement, or a table not provided.
7. Output ONLY a JSON array of these objects as your final message. No prose, no markdown fences.


=== PAPER ID ===
doi__10.1186_s12864-022-08310-4

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Performance comparison among different tools on the test set. Performance of different tools are presented with five metrics in percentage: accuracy (acc), sensitivity (sens), specificity (spec), F1 score (F1) and area under the receiver operating characteristic curve (AUROC)", "footnotes": ["aModels presented in the referenced papers are available through online servers", "bThe best hyperparameter as stated in the referenced paper", "cThe optimal number of training epochs determined by early stopping is 16"], "header_rows": [["Tool", "Model", "Acc", "Sens", "Spec", "F1", "AUROC"]], "longform_cells": [{"table_index": 1, "row_index": 2, "col_index": 2, "row_label": "iAMPpred", "col_header": "Model", "value": "originala"}, {"table_index": 1, "row_index": 2, "col_index": 3, "row_label": "iAMPpred", "col_header": "Acc", "value": "74.01"}, {"table_index": 1, "row_index": 2, "col_index": 4, "row_label": "iAMPpred", "col_header": "Sens", "value": "87.90"}, {"table_index": 1, "row_index": 2, "col_index": 5, "row_label": "iAMPpred", "col_header": "Spec", "value": "60.12"}, {"table_index": 1, "row_index": 2, "col_index": 6, "row_label": "iAMPpred", "col_header": "F1", "value": "77.18"}, {"table_index": 1, "row_index": 2, "col_index": 7, "row_label": "iAMPpred", "col_header": "AUROC", "value": "80.70"}, {"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "iAMP-2L", "col_header": "Model", "value": "originala"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "iAMP-2L", "col_header": "Acc", "value": "77.96"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "iAMP-2L", "col_header": "Sens", "value": "88.26"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "iAMP-2L", "col_header": "Spec", "value": "67.66"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "iAMP-2L", "col_header": "F1", "value": "80.02"}, {"table_index": 1, "row_index": 3, "col_index": 7, "row_label": "iAMP-2L", "col_header": "AUROC", "value": "–"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "AMP Scanner Vr.2", "col_header": "Model", "value": "originala"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "AMP Scanner Vr.2", "col_header": "Acc", "value": "78.50"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "AMP Scanner Vr.2", "col_header": "Sens", "value": "90.66"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "AMP Scanner Vr.2", "col_header": "Spec", "value": "66.35"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "AMP Scanner Vr.2", "col_header": "F1", "value": "80.83"}, {"table_index": 1, "row_index": 4, "col_index": 7, "row_label": "AMP Scanner Vr.2", "col_header": "AUROC", "value": "88.33"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "re-trained, 10 epochsb", "col_header": "Model", "value": "90.66"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "re-trained, 10 epochsb", "col_header": "Acc", "value": "91.14"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "re-trained, 10 epochsb", "col_header": "Sens", "value": "90.18"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "re-trained, 10 epochsb", "col_header": "Spec", "value": "90.70"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "re-trained, 10 epochsb", "col_header": "F1", "value": "97.40"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "re-trained, early stoppedc", "col_header": "Model", "value": "91.20"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "re-trained, early stoppedc", "col_header": "Acc", "value": "90.42"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "re-trained, early stoppedc", "col_header": "Sens", "value": "91.98"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "re-trained, early stoppedc", "col_header": "Spec", "value": "91.13"}, {"table_index": 1, "row_index": 6, "col_index": 6, "row_label": "re-trained, early stoppedc", "col_header": "F1", "value": "97.03"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "AMPlify", "col_header": "Model", "value": "single sub-model 1"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "AMPlify", "col_header": "Acc", "value": "92.40"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "AMPlify", "col_header": "Sens", "value": "90.90"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "AMPlify", "col_header": "Spec", "value": "93.89"}, {"table_index": 1, "row_index": 7, "col_index": 6, "row_label": "AMPlify", "col_header": "F1", "value": "92.28"}, {"table_index": 1, "row_index": 7, "col_index": 7, "row_label": "AMPlify", "col_header": "AUROC", "value": "97.54"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "single sub-model 2", "col_header": "Model", "value": "91.98"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "single sub-model 2", "col_header": "Acc", "value": "91.02"}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "single sub-model 2", "col_header": "Sens", "value": "92.93"}, {"table_index": 1, "row_index": 8, "col_index": 5, "row_label": "single sub-model 2", "col_header": "Spec", "value": "91.90"}, {"table_index": 1, "row_index": 8, "col_index": 6, "row_label": "single sub-model 2", "col_header": "F1", "value": "97.40"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "single sub-model 3", "col_header": "Model", "value": "92.51"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "single sub-model 3", "col_header": "Acc", "value": "92.69"}, {"table_index": 1, "row_index": 9, "col_index": 4, "row_label": "single sub-model 3", "col_header": "Sens", "value": "92.34"}, {"table_index": 1, "row_index": 9, "col_index": 5, "row_label": "single sub-model 3", "col_header": "Spec", "value": "92.53"}, {"table_index": 1, "row_index": 9, "col_index": 6, "row_label": "single sub-model 3", "col_header": "F1", "value": "97.82"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "single sub-model 4", "col_header": "Model", "value": "92.10"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "single sub-model 4", "col_header": "Acc", "value": "90.90"}, {"table_index": 1, "row_index": 10, "col_index": 4, "row_label": "single sub-model 4", "col_header": "Sens", "value": "93.29"}, {"table_index": 1, "row_index": 10, "col_index": 5, "row_label": "single sub-model 4", "col_header": "Spec", "value": "92.00"}, {"table_index": 1, "row_index": 10, "col_index": 6, "row_label": "single sub-model 4", "col_header": "F1", "value": "97.27"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "single sub-model 5", "col_header": "Model", "value": "92.57"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "single sub-model 5", "col_header": "Acc", "value": "92.57"}, {"table_index": 1, "row_index": 11, "col_index": 4, "row_label": "single sub-model 5", "col_header": "Sens", "value": "92.57"}, {"table_index": 1, "row_index": 11, "col_index": 5, "row_label": "single sub-model 5", "col_header": "Spec", "value": "92.57"}, {"table_index": 1, "row_index": 11, "col_index": 6, "row_label": "single sub-model 5", "col_header": "F1", "value": "97.98"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "ensemble", "col_header": "Model", "value": "93.71"}, {"table_index": 1, "row_index": 12, "col_index": 3, "row_label": "ensemble", "col_header": "Acc", "value": "92.93"}, {"table_index": 1, "row_index": 12, "col_index": 4, "row_label": "ensemble", "col_header": "Sens", "value": "94.49"}, {"table_index": 1, "row_index": 12, "col_index": 5, "row_label": "ensemble", "col_header": "Spec", "value": "93.66"}, {"table_index": 1, "row_index": 12, "col_index": 6, "row_label": "ensemble", "col_header": "F1", "value": "98.37"}]}, {"table_index": 2, "label": "Table 2", "caption": "Putative and reported AMP sequences discovered from Rana [Lithobates] catesbeiana. Genomic and transcriptomic resources from Rana [Lithobates] catesbeiana [33] were mined using the AMP discovery pipeline based on AMPlify. Top-scoring peptide sequences were selected for synthesis and validation in vitro", "footnotes": ["*Previously reported amphibian peptide sequences [34, 38, 39]", "+Previously reported as a full-length AMP precursor sequence. Uniprot ID: C5IB07", "aNet charge at pH = 7"], "header_rows": [["Peptide Name", "Sequence", "# aa", "Net Chargea", "MW (Da)", "AMPlify Score"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "RaCa-1", "col_header": "Sequence", "value": "GLLDIIKTTGKDFAVKILDNLKCKLAGGCPP"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "RaCa-1", "col_header": "# aa", "value": "31"}, {"table_index": 2, "row_index": 2, "col_index": 4, "row_label": "RaCa-1", "col_header": "Net Chargea", "value": "2"}, {"table_index": 2, "row_index": 2, "col_index": 5, "row_label": "RaCa-1", "col_header": "MW (Da)", "value": "3242.93"}, {"table_index": 2, "row_index": 2, "col_index": 6, "row_label": "RaCa-1", "col_header": "AMPlify Score", "value": "1.0000"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "RaCa-2", "col_header": "Sequence", "value": "FFPIIARLAAKVIPSLVCAVTKKC"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "RaCa-2", "col_header": "# aa", "value": "24"}, {"table_index": 2, "row_index": 3, "col_index": 4, "row_label": "RaCa-2", "col_header": "Net Chargea", "value": "4"}, {"table_index": 2, "row_index": 3, "col_index": 5, "row_label": "RaCa-2", "col_header": "MW (Da)", "value": "2589.28"}, {"table_index": 2, "row_index": 3, "col_index": 6, "row_label": "RaCa-2", "col_header": "AMPlify Score", "value": "1.0000"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "Ranatuerin-2PRc*", "col_header": "Sequence", "value": "AFLSTVKNTLTNVAGTMIDTFKCKITGVC"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "Ranatuerin-2PRc*", "col_header": "# aa", "value": "29"}, {"table_index": 2, "row_index": 4, "col_index": 4, "row_label": "Ranatuerin-2PRc*", "col_header": "Net Chargea", "value": "2"}, {"table_index": 2, "row_index": 4, "col_index": 5, "row_label": "Ranatuerin-2PRc*", "col_header": "MW (Da)", "value": "3077.66"}, {"table_index": 2, "row_index": 4, "col_index": 6, "row_label": "Ranatuerin-2PRc*", "col_header": "AMPlify Score", "value": "1.0000"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "Temporin-1Cb*+", "col_header": "Sequence", "value": "FLFPLITSFLSKFLGK"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "Temporin-1Cb*+", "col_header": "# aa", "value": "16"}, {"table_index": 2, "row_index": 5, "col_index": 4, "row_label": "Temporin-1Cb*+", "col_header": "Net Chargea", "value": "2"}, {"table_index": 2, "row_index": 5, "col_index": 5, "row_label": "Temporin-1Cb*+", "col_header": "MW (Da)", "value": "1858.30"}, {"table_index": 2, "row_index": 5, "col_index": 6, "row_label": "Temporin-1Cb*+", "col_header": "AMPlify Score", "value": "1.0000"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "Palustrin-Ca*", "col_header": "Sequence", "value": "GFLDIIKDTGKEFAVKILNNLKCKLAGGCPP"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "Palustrin-Ca*", "col_header": "# aa", "value": "31"}, {"table_index": 2, "row_index": 6, "col_index": 4, "row_label": "Palustrin-Ca*", "col_header": "Net Chargea", "value": "2"}, {"table_index": 2, "row_index": 6, "col_index": 5, "row_label": "Palustrin-Ca*", "col_header": "MW (Da)", "value": "3303.97"}, {"table_index": 2, "row_index": 6, "col_index": 6, "row_label": "Palustrin-Ca*", "col_header": "AMPlify Score", "value": "1.0000"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "Ranatuerin-2RC*", "col_header": "Sequence", "value": "GLFLDTLKGAAKDVAGKLLEGLKCKITGCKP"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "Ranatuerin-2RC*", "col_header": "# aa", "value": "31"}, {"table_index": 2, "row_index": 7, "col_index": 4, "row_label": "Ranatuerin-2RC*", "col_header": "Net Chargea", "value": "3"}, {"table_index": 2, "row_index": 7, "col_index": 5, "row_label": "Ranatuerin-2RC*", "col_header": "MW (Da)", "value": "3188.88"}, {"table_index": 2, "row_index": 7, "col_index": 6, "row_label": "Ranatuerin-2RC*", "col_header": "AMPlify Score", "value": "1.0000"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "RaCa-3", "col_header": "Sequence", "value": "GLWETIKTTGKSIALNLLDKIKCKIAGGCPP"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "RaCa-3", "col_header": "# aa", "value": "31"}, {"table_index": 2, "row_index": 8, "col_index": 4, "row_label": "RaCa-3", "col_header": "Net Chargea", "value": "3"}, {"table_index": 2, "row_index": 8, "col_index": 5, "row_label": "RaCa-3", "col_header": "MW (Da)", "value": "3269.95"}, {"table_index": 2, "row_index": 8, "col_index": 6, "row_label": "RaCa-3", "col_header": "AMPlify Score", "value": "1.0000"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "Ranatuerin-2C*", "col_header": "Sequence", "value": "GVFLDTLKGLAGKMLESLKCKIAGCKP"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "Ranatuerin-2C*", "col_header": "# aa", "value": "27"}, {"table_index": 2, "row_index": 9, "col_index": 4, "row_label": "Ranatuerin-2C*", "col_header": "Net Chargea", "value": "3"}, {"table_index": 2, "row_index": 9, "col_index": 5, "row_label": "Ranatuerin-2C*", "col_header": "MW (Da)", "value": "2821.49"}, {"table_index": 2, "row_index": 9, "col_index": 6, "row_label": "Ranatuerin-2C*", "col_header": "AMPlify Score", "value": "0.9999"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "RaCa-4", "col_header": "Sequence", "value": "FLTFPGMTFGKLLGK"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "RaCa-4", "col_header": "# aa", "value": "15"}, {"table_index": 2, "row_index": 10, "col_index": 4, "row_label": "RaCa-4", "col_header": "Net Chargea", "value": "2"}, {"table_index": 2, "row_index": 10, "col_index": 5, "row_label": "RaCa-4", "col_header": "MW (Da)", "value": "1657.05"}, {"table_index": 2, "row_index": 10, "col_index": 6, "row_label": "RaCa-4", "col_header": "AMPlify Score", "value": "0.9997"}, {"table_index": 2, "row_index": 11, "col_index": 2, "row_label": "RaCa-5", "col_header": "Sequence", "value": "GLLDIIKDTGKTTGILMDTLKCQMTGRCPPSS"}, {"table_index": 2, "row_index": 11, "col_index": 3, "row_label": "RaCa-5", "col_header": "# aa", "value": "32"}, {"table_index": 2, "row_index": 11, "col_index": 4, "row_label": "RaCa-5", "col_header": "Net Chargea", "value": "1"}, {"table_index": 2, "row_index": 11, "col_index": 5, "row_label": "RaCa-5", "col_header": "MW (Da)", "value": "3395.02"}, {"table_index": 2, "row_index": 11, "col_index": 6, "row_label": "RaCa-5", "col_header": "AMPlify Score", "value": "0.9996"}, {"table_index": 2, "row_index": 12, "col_index": 2, "row_label": "RaCa-6", "col_header": "Sequence", "value": "ATAWRIPPPGMQPIIPIRIRPLCGKQ"}, {"table_index": 2, "row_index": 12, "col_index": 3, "row_label": "RaCa-6", "col_header": "# aa", "value": "26"}, {"table_index": 2, "row_index": 12, "col_index": 4, "row_label": "RaCa-6", "col_header": "Net Chargea", "value": "4"}, {"table_index": 2, "row_index": 12, "col_index": 5, "row_label": "RaCa-6", "col_header": "MW (Da)", "value": "2910.58"}, {"table_index": 2, "row_index": 12, "col_index": 6, "row_label": "RaCa-6", "col_header": "AMPlify Score", "value": "0.9994"}, {"table_index": 2, "row_index": 13, "col_index": 2, "row_label": "RaCa-7", "col_header": "Sequence", "value": "FFPRVLPLANKFLPTIYCALPKSVGN"}, {"table_index": 2, "row_index": 13, "col_index": 3, "row_label": "RaCa-7", "col_header": "# aa", "value": "26"}, {"table_index": 2, "row_index": 13, "col_index": 4, "row_label": "RaCa-7", "col_header": "Net Chargea", "value": "3"}, {"table_index": 2, "row_index": 13, "col_index": 5, "row_label": "RaCa-7", "col_header": "MW (Da)", "value": "2906.52"}, {"table_index": 2, "row_index": 13, "col_index": 6, "row_label": "RaCa-7", "col_header": "AMPlify Score", "value": "0.9985"}, {"table_index": 2, "row_index": 14, "col_index": 2, "row_label": "RaCa-8", "col_header": "Sequence", "value": "FPAIICKVSKNC"}, {"table_index": 2, "row_index": 14, "col_index": 3, "row_label": "RaCa-8", "col_header": "# aa", "value": "12"}, {"table_index": 2, "row_index": 14, "col_index": 4, "row_label": "RaCa-8", "col_header": "Net Chargea", "value": "2"}, {"table_index": 2, "row_index": 14, "col_index": 5, "row_label": "RaCa-8", "col_header": "MW (Da)", "value": "1322.65"}, {"table_index": 2, "row_index": 14, "col_index": 6, "row_label": "RaCa-8", "col_header": "AMPlify Score", "value": "0.9961"}, {"table_index": 2, "row_index": 15, "col_index": 2, "row_label": "RaCa-9", "col_header": "Sequence", "value": "FYFPVSRKFGGK"}, {"table_index": 2, "row_index": 15, "col_index": 3, "row_label": "RaCa-9", "col_header": "# aa", "value": "12"}, {"table_index": 2, "row_index": 15, "col_index": 4, "row_label": "RaCa-9", "col_header": "Net Chargea", "value": "3"}, {"table_index": 2, "row_index": 15, "col_index": 5, "row_label": "RaCa-9", "col_header": "MW (Da)", "value": "1432.69"}, {"table_index": 2, "row_index": 15, "col_index": 6, "row_label": "RaCa-9", "col_header": "AMPlify Score", "value": "0.9412"}, {"table_index": 2, "row_index": 16, "col_index": 2, "row_label": "RaCa-10", "col_header": "Sequence", "value": "ALVAKIQKFPVFNTLKLCKLELEII"}, {"table_index": 2, "row_index": 16, "col_index": 3, "row_label": "RaCa-10", "col_header": "# aa", "value": "25"}, {"table_index": 2, "row_index": 16, "col_index": 4, "row_label": "RaCa-10", "col_header": "Net Chargea", "value": "2"}, {"table_index": 2, "row_index": 16, "col_index": 5, "row_label": "RaCa-10", "col_header": "MW (Da)", "value": "2872.59"}, {"table_index": 2, "row_index": 16, "col_index": 6, "row_label": "RaCa-10", "col_header": "AMPlify Score", "value": "0.6063"}, {"table_index": 2, "row_index": 17, "col_index": 2, "row_label": "RaCa-11", "col_header": "Sequence", "value": "SNRDFFKVNIFRLCG"}, {"table_index": 2, "row_index": 17, "col_index": 3, "row_label": "RaCa-11", "col_header": "# aa", "value": "15"}, {"table_index": 2, "row_index": 17, "col_index": 4, "row_label": "RaCa-11", "col_header": "Net Chargea", "value": "2"}, {"table_index": 2, "row_index": 17, "col_index": 5, "row_label": "RaCa-11", "col_header": "MW (Da)", "value": "1816.11"}, {"table_index": 2, "row_index": 17, "col_index": 6, "row_label": "RaCa-11", "col_header": "AMPlify Score", "value": "0.6058"}]}, {"table_index": 3, "label": "Table 3", "caption": "Minimum inhibitory concentrations (MIC) and minimum bactericidal concentrations (MBC) of selected AMP candidates following antimicrobial susceptibility testing (AST) in vitro. Candidate antimicrobial peptides were synthesized and purchased from Genscript. AST, and MIC/MBC determination was performed as outlined by the Clinical and Laboratory Standards Institute (CLSI) [40], with modification as recommended by Hancock [41]. Data is presented as the lowest effective peptide concentration range (μM) observed in three independent experiments. LL37, human cathelicidin and a peptide from Tp0751 from Treponema pallidum were used as the positive and negative control peptides [34], respectively", "footnotes": ["aBacteria obtained and tested at the University of Victoria", "bUnknown strain; hospital isolate", "cATCC quality control strain #25922 purchased from Cedarlane Laboratories (Burlington, Ontario, Canada)", "dClinical isolate obtained and tested at the British Columbia Centre for Disease Control", "NI, no inhibition observed in vitro", "‘—’ = not tested", "Abbreviations: Staphylococcus aureus, Streptococcus pyogenes, Pseudomonas aeruginosa, Escherichia coli, ATCC American Type Culture Collection, CPO carbapenemase-producing organism, MDR multi-drug resistant, NDM New-Delhi Metallo-beta-lactamase"], "header_rows": [["", "S. aureusa ATCC 6538P", "S. pyogenesb", "P. aeruginosaa ATCC 10148", "E. colia ATCC 9723H", "E. colic ATCC 25922", "MDR E. colid (CPO-NDM)"], ["", "Gram-positive", "Gram-positive", "Gram-negative", "Gram-negative", "Gram-negative", "Gram-negative"], ["(μM)", "MIC", "MBC", "MIC", "MBC", "MIC", "MBC", "MIC", "MBC", "MIC", "MBC", "MIC", "MBC"]], "longform_cells": [{"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "RaCa-1", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 4, "col_index": 3, "row_label": "RaCa-1", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 4, "col_index": 4, "row_label": "RaCa-1", "col_header": "MIC", "value": "79"}, {"table_index": 3, "row_index": 4, "col_index": 5, "row_label": "RaCa-1", "col_header": "MBC", "value": "≥ 79"}, {"table_index": 3, "row_index": 4, "col_index": 6, "row_label": "RaCa-1", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 4, "col_index": 7, "row_label": "RaCa-1", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 4, "col_index": 8, "row_label": "RaCa-1", "col_header": "MIC", "value": "20 – 39"}, {"table_index": 3, "row_index": 4, "col_index": 9, "row_label": "RaCa-1", "col_header": "MBC", "value": "39 – 79"}, {"table_index": 3, "row_index": 4, "col_index": 10, "row_label": "RaCa-1", "col_header": "MIC", "value": "10 – 20"}, {"table_index": 3, "row_index": 4, "col_index": 11, "row_label": "RaCa-1", "col_header": "MBC", "value": "10 – 39"}, {"table_index": 3, "row_index": 4, "col_index": 12, "row_label": "RaCa-1", "col_header": "MIC", "value": "20 – 39"}, {"table_index": 3, "row_index": 4, "col_index": 13, "row_label": "RaCa-1", "col_header": "MBC", "value": "20 – 39"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "RaCa-2", "col_header": "MIC", "value": "1 – 2"}, {"table_index": 3, "row_index": 5, "col_index": 3, "row_label": "RaCa-2", "col_header": "MBC", "value": "1 – 2"}, {"table_index": 3, "row_index": 5, "col_index": 4, "row_label": "RaCa-2", "col_header": "MIC", "value": "25 – 49"}, {"table_index": 3, "row_index": 5, "col_index": 5, "row_label": "RaCa-2", "col_header": "MBC", "value": "25 – 49"}, {"table_index": 3, "row_index": 5, "col_index": 6, "row_label": "RaCa-2", "col_header": "MIC", "value": "25 – 49"}, {"table_index": 3, "row_index": 5, "col_index": 7, "row_label": "RaCa-2", "col_header": "MBC", "value": "49 – ≥99"}, {"table_index": 3, "row_index": 5, "col_index": 8, "row_label": "RaCa-2", "col_header": "MIC", "value": "3 – 6"}, {"table_index": 3, "row_index": 5, "col_index": 9, "row_label": "RaCa-2", "col_header": "MBC", "value": "3 – 6"}, {"table_index": 3, "row_index": 5, "col_index": 10, "row_label": "RaCa-2", "col_header": "MIC", "value": "2 – 6"}, {"table_index": 3, "row_index": 5, "col_index": 11, "row_label": "RaCa-2", "col_header": "MBC", "value": "2 – 6"}, {"table_index": 3, "row_index": 5, "col_index": 12, "row_label": "RaCa-2", "col_header": "MIC", "value": "2 – 6"}, {"table_index": 3, "row_index": 5, "col_index": 13, "row_label": "RaCa-2", "col_header": "MBC", "value": "2 – 6"}, {"table_index": 3, "row_index": 6, "col_index": 2, "row_label": "RaCa-3", "col_header": "MIC", "value": "≥78"}, {"table_index": 3, "row_index": 6, "col_index": 3, "row_label": "RaCa-3", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 6, "col_index": 4, "row_label": "RaCa-3", "col_header": "MIC", "value": "39"}, {"table_index": 3, "row_index": 6, "col_index": 5, "row_label": "RaCa-3", "col_header": "MBC", "value": "39 – ≥ 78"}, {"table_index": 3, "row_index": 6, "col_index": 6, "row_label": "RaCa-3", "col_header": "MIC", "value": "20 – ≥78"}, {"table_index": 3, "row_index": 6, "col_index": 7, "row_label": "RaCa-3", "col_header": "MBC", "value": "39 – ≥78"}, {"table_index": 3, "row_index": 6, "col_index": 8, "row_label": "RaCa-3", "col_header": "MIC", "value": "5 – 10"}, {"table_index": 3, "row_index": 6, "col_index": 9, "row_label": "RaCa-3", "col_header": "MBC", "value": "5 – 10"}, {"table_index": 3, "row_index": 6, "col_index": 10, "row_label": "RaCa-3", "col_header": "MIC", "value": "2 – 5"}, {"table_index": 3, "row_index": 6, "col_index": 11, "row_label": "RaCa-3", "col_header": "MBC", "value": "2 – 5"}, {"table_index": 3, "row_index": 6, "col_index": 12, "row_label": "RaCa-3", "col_header": "MIC", "value": "5 – 10"}, {"table_index": 3, "row_index": 6, "col_index": 13, "row_label": "RaCa-3", "col_header": "MBC", "value": "5 – 20"}, {"table_index": 3, "row_index": 7, "col_index": 2, "row_label": "RaCa-4", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 7, "col_index": 3, "row_label": "RaCa-4", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 7, "col_index": 4, "row_label": "RaCa-4", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 7, "col_index": 5, "row_label": "RaCa-4", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 7, "col_index": 6, "row_label": "RaCa-4", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 7, "col_index": 7, "row_label": "RaCa-4", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 7, "col_index": 8, "row_label": "RaCa-4", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 7, "col_index": 9, "row_label": "RaCa-4", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 7, "col_index": 10, "row_label": "RaCa-4", "col_header": "MIC", "value": "–"}, {"table_index": 3, "row_index": 7, "col_index": 11, "row_label": "RaCa-4", "col_header": "MBC", "value": "–"}, {"table_index": 3, "row_index": 7, "col_index": 12, "row_label": "RaCa-4", "col_header": "MIC", "value": "–"}, {"table_index": 3, "row_index": 7, "col_index": 13, "row_label": "RaCa-4", "col_header": "MBC", "value": "–"}, {"table_index": 3, "row_index": 8, "col_index": 2, "row_label": "RaCa-5", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 3, "row_label": "RaCa-5", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 4, "row_label": "RaCa-5", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 5, "row_label": "RaCa-5", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 6, "row_label": "RaCa-5", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 7, "row_label": "RaCa-5", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 8, "row_label": "RaCa-5", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 9, "row_label": "RaCa-5", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 10, "row_label": "RaCa-5", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 11, "row_label": "RaCa-5", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 12, "row_label": "RaCa-5", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 8, "col_index": 13, "row_label": "RaCa-5", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 2, "row_label": "RaCa-6", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 3, "row_label": "RaCa-6", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 4, "row_label": "RaCa-6", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 5, "row_label": "RaCa-6", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 6, "row_label": "RaCa-6", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 7, "row_label": "RaCa-6", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 8, "row_label": "RaCa-6", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 9, "row_label": "RaCa-6", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 10, "row_label": "RaCa-6", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 11, "row_label": "RaCa-6", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 12, "row_label": "RaCa-6", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 9, "col_index": 13, "row_label": "RaCa-6", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 10, "col_index": 2, "row_label": "RaCa-7", "col_header": "MIC", "value": "≥ 88"}, {"table_index": 3, "row_index": 10, "col_index": 3, "row_label": "RaCa-7", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 10, "col_index": 4, "row_label": "RaCa-7", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 10, "col_index": 5, "row_label": "RaCa-7", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 10, "col_index": 6, "row_label": "RaCa-7", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 10, "col_index": 7, "row_label": "RaCa-7", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 10, "col_index": 8, "row_label": "RaCa-7", "col_header": "MIC", "value": "11 – 22"}, {"table_index": 3, "row_index": 10, "col_index": 9, "row_label": "RaCa-7", "col_header": "MBC", "value": "11 – 88"}, {"table_index": 3, "row_index": 10, "col_index": 10, "row_label": "RaCa-7", "col_header": "MIC", "value": "6 – 44"}, {"table_index": 3, "row_index": 10, "col_index": 11, "row_label": "RaCa-7", "col_header": "MBC", "value": "6 – 44"}, {"table_index": 3, "row_index": 10, "col_index": 12, "row_label": "RaCa-7", "col_header": "MIC", "value": "6 – 44"}, {"table_index": 3, "row_index": 10, "col_index": 13, "row_label": "RaCa-7", "col_header": "MBC", "value": "6 – 44"}, {"table_index": 3, "row_index": 11, "col_index": 2, "row_label": "RaCa-8", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 3, "row_label": "RaCa-8", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 4, "row_label": "RaCa-8", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 5, "row_label": "RaCa-8", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 6, "row_label": "RaCa-8", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 7, "row_label": "RaCa-8", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 8, "row_label": "RaCa-8", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 9, "row_label": "RaCa-8", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 10, "row_label": "RaCa-8", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 11, "row_label": "RaCa-8", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 12, "row_label": "RaCa-8", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 11, "col_index": 13, "row_label": "RaCa-8", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 12, "col_index": 2, "row_label": "RaCa-9", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 12, "col_index": 3, "row_label": "RaCa-9", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 12, "col_index": 4, "row_label": "RaCa-9", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 12, "col_index": 5, "row_label": "RaCa-9", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 12, "col_index": 6, "row_label": "RaCa-9", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 12, "col_index": 7, "row_label": "RaCa-9", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 12, "col_index": 8, "row_label": "RaCa-9", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 12, "col_index": 9, "row_label": "RaCa-9", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 12, "col_index": 10, "row_label": "RaCa-9", "col_header": "MIC", "value": "–"}, {"table_index": 3, "row_index": 12, "col_index": 11, "row_label": "RaCa-9", "col_header": "MBC", "value": "–"}, {"table_index": 3, "row_index": 12, "col_index": 12, "row_label": "RaCa-9", "col_header": "MIC", "value": "–"}, {"table_index": 3, "row_index": 12, "col_index": 13, "row_label": "RaCa-9", "col_header": "MBC", "value": "–"}, {"table_index": 3, "row_index": 13, "col_index": 2, "row_label": "RaCa-10", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 3, "row_label": "RaCa-10", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 4, "row_label": "RaCa-10", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 5, "row_label": "RaCa-10", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 6, "row_label": "RaCa-10", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 7, "row_label": "RaCa-10", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 8, "row_label": "RaCa-10", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 9, "row_label": "RaCa-10", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 10, "row_label": "RaCa-10", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 11, "row_label": "RaCa-10", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 12, "row_label": "RaCa-10", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 13, "col_index": 13, "row_label": "RaCa-10", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 14, "col_index": 2, "row_label": "RaCa-11", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 14, "col_index": 3, "row_label": "RaCa-11", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 14, "col_index": 4, "row_label": "RaCa-11", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 14, "col_index": 5, "row_label": "RaCa-11", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 14, "col_index": 6, "row_label": "RaCa-11", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 14, "col_index": 7, "row_label": "RaCa-11", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 14, "col_index": 8, "row_label": "RaCa-11", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 14, "col_index": 9, "row_label": "RaCa-11", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 14, "col_index": 10, "row_label": "RaCa-11", "col_header": "MIC", "value": "–"}, {"table_index": 3, "row_index": 14, "col_index": 11, "row_label": "RaCa-11", "col_header": "MBC", "value": "–"}, {"table_index": 3, "row_index": 14, "col_index": 12, "row_label": "RaCa-11", "col_header": "MIC", "value": "–"}, {"table_index": 3, "row_index": 14, "col_index": 13, "row_label": "RaCa-11", "col_header": "MBC", "value": "–"}, {"table_index": 3, "row_index": 15, "col_index": 2, "row_label": "LL37", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 15, "col_index": 3, "row_label": "LL37", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 15, "col_index": 4, "row_label": "LL37", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 15, "col_index": 5, "row_label": "LL37", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 15, "col_index": 6, "row_label": "LL37", "col_header": "MIC", "value": "7 – ≥57"}, {"table_index": 3, "row_index": 15, "col_index": 7, "row_label": "LL37", "col_header": "MBC", "value": "7 – ≥57"}, {"table_index": 3, "row_index": 15, "col_index": 8, "row_label": "LL37", "col_header": "MIC", "value": "2 – 4"}, {"table_index": 3, "row_index": 15, "col_index": 9, "row_label": "LL37", "col_header": "MBC", "value": "4 – 7"}, {"table_index": 3, "row_index": 15, "col_index": 10, "row_label": "LL37", "col_header": "MIC", "value": "2 – 4"}, {"table_index": 3, "row_index": 15, "col_index": 11, "row_label": "LL37", "col_header": "MBC", "value": "2 – 4"}, {"table_index": 3, "row_index": 15, "col_index": 12, "row_label": "LL37", "col_header": "MIC", "value": "2 – 4"}, {"table_index": 3, "row_index": 15, "col_index": 13, "row_label": "LL37", "col_header": "MBC", "value": "2 – 4"}, {"table_index": 3, "row_index": 16, "col_index": 2, "row_label": "Tp0751", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 3, "row_label": "Tp0751", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 4, "row_label": "Tp0751", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 5, "row_label": "Tp0751", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 6, "row_label": "Tp0751", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 7, "row_label": "Tp0751", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 8, "row_label": "Tp0751", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 9, "row_label": "Tp0751", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 10, "row_label": "Tp0751", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 11, "row_label": "Tp0751", "col_header": "MBC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 12, "row_label": "Tp0751", "col_header": "MIC", "value": "NI"}, {"table_index": 3, "row_index": 16, "col_index": 13, "row_label": "Tp0751", "col_header": "MBC", "value": "NI"}]}, {"table_index": 4, "label": "PDF p9 table1", "caption": "from 12864_2022_8310_MOESM1_ESM.pdf", "footnotes": [], "header_rows": [["", "S. aureusa ATCC 6538P Gram-positive", "", "S. pyogenesb Gram-positive", "", "P. aeruginosaa ATCC 10148 Gram-negative", "", "E. colia ATCC 9723H Gram-negative", "", "E. colic ATCC 25922 Gram-negative", "", "MDR E. colid (CPO-NDM) Gram-negative", ""], ["(µg/mL)", "MIC", "MBC", "MIC", "MBC", "MIC", "MBC", "MIC", "MBC", "MIC", "MBC", "MIC", "MBC"]], "longform_cells": [{"table_index": 4, "row_index": 3, "col_index": 2, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MIC", "value": "NI 2 – 4 ≥256 NI NI NI ≥ 256 NI NI NI NI NI NI"}, {"table_index": 4, "row_index": 3, "col_index": 3, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MBC", "value": "NI 2 – 4 NI NI NI NI NI NI NI NI NI NI NI"}, {"table_index": 4, "row_index": 3, "col_index": 4, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MIC", "value": "256 64 – 128 128 NI NI NI NI NI NI NI NI NI NI"}, {"table_index": 4, "row_index": 3, "col_index": 5, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MBC", "value": "≥ 256 64 – 128 128 – ≥ 256 NI NI NI NI NI NI NI NI NI NI"}, {"table_index": 4, "row_index": 3, "col_index": 6, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MIC", "value": "NI 64 – 128 64 – ≥256 NI NI NI NI NI NI NI NI 32 – ≥256 NI"}, {"table_index": 4, "row_index": 3, "col_index": 7, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MBC", "value": "NI 128 – ≥256 128 – ≥256 NI NI NI NI NI NI NI NI 32 – ≥256 NI"}, {"table_index": 4, "row_index": 3, "col_index": 8, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MIC", "value": "64 – 128 8 – 16 16 – 32 NI NI NI 32 – 64 NI NI NI NI 8 – 16 NI"}, {"table_index": 4, "row_index": 3, "col_index": 9, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MBC", "value": "128 – 256 8 – 16 16 – 32 NI NI NI 32 – 256 NI NI NI NI 16 – 32 NI"}, {"table_index": 4, "row_index": 3, "col_index": 10, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MIC", "value": "32 – 64 4 – 16 8 – 16 — NI NI 16 – 128 NI — NI — 8 – 16 NI"}, {"table_index": 4, "row_index": 3, "col_index": 11, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MBC", "value": "32 – 128 4 – 16 8 – 16 — NI NI 16 – 128 NI — NI — 8 – 16 NI"}, {"table_index": 4, "row_index": 3, "col_index": 12, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MIC", "value": "64 – 128 4 – 16 16 – 32 — NI NI 16 – 128 NI — NI — 8 – 16 NI"}, {"table_index": 4, "row_index": 3, "col_index": 13, "row_label": "RaCa-1 RaCa-2 RaCa-3 RaCa-4 RaCa-5 RaCa-6 RaCa-7 RaCa-8 RaCa-9 RaCa-10 RaCa-11 LL37 Tp0751", "col_header": "MBC", "value": "64 – 128 4 – 16 16 – 64 — NI NI 16 – 128 NI — NI — 8 – 16 NI"}]}, {"table_index": 5, "label": "PDF p10 table1", "caption": "from 12864_2022_8310_MOESM1_ESM.pdf", "footnotes": [], "header_rows": [["Serial Number", "Peptide Namea", "Active?b", "AMPlify", "", "AMP Scanner Vr.2c", "", "iAMPpredd", "", "", ""], ["", "", "", "Score", "Prediction", "Score", "Prediction", "Score", "", "", "Prediction"], ["", "", "", "", "", "", "", "ABP", "AVP", "AFP", ""]], "longform_cells": [{"table_index": 5, "row_index": 4, "col_index": 2, "row_label": "0", "col_header": "Peptide Namea", "value": "GGN5"}, {"table_index": 5, "row_index": 4, "col_index": 3, "row_label": "0", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 4, "col_index": 4, "row_label": "0", "col_header": "AMPlify", "value": "1.0000"}, {"table_index": 5, "row_index": 4, "col_index": 5, "row_label": "0", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 4, "col_index": 6, "row_label": "0", "col_header": "AMP Scanner Vr.2c", "value": "1.0000"}, {"table_index": 5, "row_index": 4, "col_index": 7, "row_label": "0", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 4, "col_index": 8, "row_label": "0", "col_header": "iAMPpredd", "value": "1.00"}, {"table_index": 5, "row_index": 4, "col_index": 9, "row_label": "0", "col_header": "", "value": "0.78"}, {"table_index": 5, "row_index": 4, "col_index": 10, "row_label": "0", "col_header": "", "value": "1.00"}, {"table_index": 5, "row_index": 4, "col_index": 11, "row_label": "0", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 5, "col_index": 2, "row_label": "1", "col_header": "Peptide Namea", "value": "GGN5N9"}, {"table_index": 5, "row_index": 5, "col_index": 4, "row_label": "1", "col_header": "AMPlify", "value": "0.9940"}, {"table_index": 5, "row_index": 5, "col_index": 5, "row_label": "1", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 5, "col_index": 6, "row_label": "1", "col_header": "AMP Scanner Vr.2c", "value": "0.9979"}, {"table_index": 5, "row_index": 5, "col_index": 7, "row_label": "1", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 5, "col_index": 8, "row_label": "1", "col_header": "iAMPpredd", "value": "0.69"}, {"table_index": 5, "row_index": 5, "col_index": 9, "row_label": "1", "col_header": "", "value": "0.75"}, {"table_index": 5, "row_index": 5, "col_index": 10, "row_label": "1", "col_header": "", "value": "0.65"}, {"table_index": 5, "row_index": 5, "col_index": 11, "row_label": "1", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 6, "col_index": 2, "row_label": "2", "col_header": "Peptide Namea", "value": "GGN5N11"}, {"table_index": 5, "row_index": 6, "col_index": 4, "row_label": "2", "col_header": "AMPlify", "value": "0.9819"}, {"table_index": 5, "row_index": 6, "col_index": 5, "row_label": "2", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 6, "col_index": 6, "row_label": "2", "col_header": "AMP Scanner Vr.2c", "value": "0.9999"}, {"table_index": 5, "row_index": 6, "col_index": 7, "row_label": "2", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 6, "col_index": 8, "row_label": "2", "col_header": "iAMPpredd", "value": "0.96"}, {"table_index": 5, "row_index": 6, "col_index": 9, "row_label": "2", "col_header": "", "value": "0.82"}, {"table_index": 5, "row_index": 6, "col_index": 10, "row_label": "2", "col_header": "", "value": "0.95"}, {"table_index": 5, "row_index": 6, "col_index": 11, "row_label": "2", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 7, "col_index": 2, "row_label": "3", "col_header": "Peptide Namea", "value": "GGN5N12"}, {"table_index": 5, "row_index": 7, "col_index": 4, "row_label": "3", "col_header": "AMPlify", "value": "0.9934"}, {"table_index": 5, "row_index": 7, "col_index": 5, "row_label": "3", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 7, "col_index": 6, "row_label": "3", "col_header": "AMP Scanner Vr.2c", "value": "1.0000"}, {"table_index": 5, "row_index": 7, "col_index": 7, "row_label": "3", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 7, "col_index": 8, "row_label": "3", "col_header": "iAMPpredd", "value": "0.94"}, {"table_index": 5, "row_index": 7, "col_index": 9, "row_label": "3", "col_header": "", "value": "0.76"}, {"table_index": 5, "row_index": 7, "col_index": 10, "row_label": "3", "col_header": "", "value": "0.91"}, {"table_index": 5, "row_index": 7, "col_index": 11, "row_label": "3", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 8, "col_index": 2, "row_label": "4", "col_header": "Peptide Namea", "value": "GGN5N13"}, {"table_index": 5, "row_index": 8, "col_index": 3, "row_label": "4", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 8, "col_index": 4, "row_label": "4", "col_header": "AMPlify", "value": "0.9962"}, {"table_index": 5, "row_index": 8, "col_index": 5, "row_label": "4", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 8, "col_index": 6, "row_label": "4", "col_header": "AMP Scanner Vr.2c", "value": "1.0000"}, {"table_index": 5, "row_index": 8, "col_index": 7, "row_label": "4", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 8, "col_index": 8, "row_label": "4", "col_header": "iAMPpredd", "value": "0.95"}, {"table_index": 5, "row_index": 8, "col_index": 9, "row_label": "4", "col_header": "", "value": "0.77"}, {"table_index": 5, "row_index": 8, "col_index": 10, "row_label": "4", "col_header": "", "value": "0.92"}, {"table_index": 5, "row_index": 8, "col_index": 11, "row_label": "4", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 9, "col_index": 2, "row_label": "5", "col_header": "Peptide Namea", "value": "GGN5N11(3-13)"}, {"table_index": 5, "row_index": 9, "col_index": 3, "row_label": "5", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 9, "col_index": 4, "row_label": "5", "col_header": "AMPlify", "value": "0.9580"}, {"table_index": 5, "row_index": 9, "col_index": 5, "row_label": "5", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 9, "col_index": 6, "row_label": "5", "col_header": "AMP Scanner Vr.2c", "value": "0.9793"}, {"table_index": 5, "row_index": 9, "col_index": 7, "row_label": "5", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 9, "col_index": 8, "row_label": "5", "col_header": "iAMPpredd", "value": "0.99"}, {"table_index": 5, "row_index": 9, "col_index": 9, "row_label": "5", "col_header": "", "value": "0.74"}, {"table_index": 5, "row_index": 9, "col_index": 10, "row_label": "5", "col_header": "", "value": "0.95"}, {"table_index": 5, "row_index": 9, "col_index": 11, "row_label": "5", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 10, "col_index": 2, "row_label": "6", "col_header": "Peptide Namea", "value": "GGN5N13(2-14)"}, {"table_index": 5, "row_index": 10, "col_index": 4, "row_label": "6", "col_header": "AMPlify", "value": "0.7552"}, {"table_index": 5, "row_index": 10, "col_index": 5, "row_label": "6", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 10, "col_index": 6, "row_label": "6", "col_header": "AMP Scanner Vr.2c", "value": "0.9994"}, {"table_index": 5, "row_index": 10, "col_index": 7, "row_label": "6", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 10, "col_index": 8, "row_label": "6", "col_header": "iAMPpredd", "value": "0.97"}, {"table_index": 5, "row_index": 10, "col_index": 9, "row_label": "6", "col_header": "", "value": "0.62"}, {"table_index": 5, "row_index": 10, "col_index": 10, "row_label": "6", "col_header": "", "value": "0.88"}, {"table_index": 5, "row_index": 10, "col_index": 11, "row_label": "6", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 11, "col_index": 2, "row_label": "7", "col_header": "Peptide Namea", "value": "GGN5N13(3-15)"}, {"table_index": 5, "row_index": 11, "col_index": 4, "row_label": "7", "col_header": "AMPlify", "value": "0.9879"}, {"table_index": 5, "row_index": 11, "col_index": 5, "row_label": "7", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 11, "col_index": 6, "row_label": "7", "col_header": "AMP Scanner Vr.2c", "value": "0.9968"}, {"table_index": 5, "row_index": 11, "col_index": 7, "row_label": "7", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 11, "col_index": 8, "row_label": "7", "col_header": "iAMPpredd", "value": "0.91"}, {"table_index": 5, "row_index": 11, "col_index": 9, "row_label": "7", "col_header": "", "value": "0.38"}, {"table_index": 5, "row_index": 11, "col_index": 10, "row_label": "7", "col_header": "", "value": "0.73"}, {"table_index": 5, "row_index": 11, "col_index": 11, "row_label": "7", "col_header": "", "value": "ABP, AFP"}, {"table_index": 5, "row_index": 12, "col_index": 2, "row_label": "8", "col_header": "Peptide Namea", "value": "GGN5N13(4-16)"}, {"table_index": 5, "row_index": 12, "col_index": 4, "row_label": "8", "col_header": "AMPlify", "value": "0.9944"}, {"table_index": 5, "row_index": 12, "col_index": 5, "row_label": "8", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 12, "col_index": 6, "row_label": "8", "col_header": "AMP Scanner Vr.2c", "value": "0.9982"}, {"table_index": 5, "row_index": 12, "col_index": 7, "row_label": "8", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 12, "col_index": 8, "row_label": "8", "col_header": "iAMPpredd", "value": "0.85"}, {"table_index": 5, "row_index": 12, "col_index": 9, "row_label": "8", "col_header": "", "value": "0.54"}, {"table_index": 5, "row_index": 12, "col_index": 10, "row_label": "8", "col_header": "", "value": "0.57"}, {"table_index": 5, "row_index": 12, "col_index": 11, "row_label": "8", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 13, "col_index": 2, "row_label": "9", "col_header": "Peptide Namea", "value": "GGN5N13(5-17)"}, {"table_index": 5, "row_index": 13, "col_index": 4, "row_label": "9", "col_header": "AMPlify", "value": "0.8087"}, {"table_index": 5, "row_index": 13, "col_index": 5, "row_label": "9", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 13, "col_index": 6, "row_label": "9", "col_header": "AMP Scanner Vr.2c", "value": "0.9995"}, {"table_index": 5, "row_index": 13, "col_index": 7, "row_label": "9", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 13, "col_index": 8, "row_label": "9", "col_header": "iAMPpredd", "value": "0.94"}, {"table_index": 5, "row_index": 13, "col_index": 9, "row_label": "9", "col_header": "", "value": "0.63"}, {"table_index": 5, "row_index": 13, "col_index": 10, "row_label": "9", "col_header": "", "value": "0.71"}, {"table_index": 5, "row_index": 13, "col_index": 11, "row_label": "9", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 14, "col_index": 2, "row_label": "10", "col_header": "Peptide Namea", "value": "G3K-GGN5N13"}, {"table_index": 5, "row_index": 14, "col_index": 3, "row_label": "10", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 14, "col_index": 4, "row_label": "10", "col_header": "AMPlify", "value": "0.9944"}, {"table_index": 5, "row_index": 14, "col_index": 5, "row_label": "10", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 14, "col_index": 6, "row_label": "10", "col_header": "AMP Scanner Vr.2c", "value": "1.0000"}, {"table_index": 5, "row_index": 14, "col_index": 7, "row_label": "10", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 14, "col_index": 8, "row_label": "10", "col_header": "iAMPpredd", "value": "0.98"}, {"table_index": 5, "row_index": 14, "col_index": 9, "row_label": "10", "col_header": "", "value": "0.87"}, {"table_index": 5, "row_index": 14, "col_index": 10, "row_label": "10", "col_header": "", "value": "0.95"}, {"table_index": 5, "row_index": 14, "col_index": 11, "row_label": "10", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 15, "col_index": 2, "row_label": "11", "col_header": "Peptide Namea", "value": "G3K/S10L-GGN5N13"}, {"table_index": 5, "row_index": 15, "col_index": 3, "row_label": "11", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 15, "col_index": 4, "row_label": "11", "col_header": "AMPlify", "value": "0.9984"}, {"table_index": 5, "row_index": 15, "col_index": 5, "row_label": "11", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 15, "col_index": 6, "row_label": "11", "col_header": "AMP Scanner Vr.2c", "value": "0.9999"}, {"table_index": 5, "row_index": 15, "col_index": 7, "row_label": "11", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 15, "col_index": 8, "row_label": "11", "col_header": "iAMPpredd", "value": "0.98"}, {"table_index": 5, "row_index": 15, "col_index": 9, "row_label": "11", "col_header": "", "value": "0.90"}, {"table_index": 5, "row_index": 15, "col_index": 10, "row_label": "11", "col_header": "", "value": "0.94"}, {"table_index": 5, "row_index": 15, "col_index": 11, "row_label": "11", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 16, "col_index": 2, "row_label": "12", "col_header": "Peptide Namea", "value": "F1A-GGN5N13"}, {"table_index": 5, "row_index": 16, "col_index": 3, "row_label": "12", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 16, "col_index": 4, "row_label": "12", "col_header": "AMPlify", "value": "0.9948"}, {"table_index": 5, "row_index": 16, "col_index": 5, "row_label": "12", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 16, "col_index": 6, "row_label": "12", "col_header": "AMP Scanner Vr.2c", "value": "0.9998"}, {"table_index": 5, "row_index": 16, "col_index": 7, "row_label": "12", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 16, "col_index": 8, "row_label": "12", "col_header": "iAMPpredd", "value": "0.98"}, {"table_index": 5, "row_index": 16, "col_index": 9, "row_label": "12", "col_header": "", "value": "0.79"}, {"table_index": 5, "row_index": 16, "col_index": 10, "row_label": "12", "col_header": "", "value": "0.91"}, {"table_index": 5, "row_index": 16, "col_index": 11, "row_label": "12", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 17, "col_index": 2, "row_label": "13", "col_header": "Peptide Namea", "value": "F1W-GGN5N13"}, {"table_index": 5, "row_index": 17, "col_index": 3, "row_label": "13", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 17, "col_index": 4, "row_label": "13", "col_header": "AMPlify", "value": "0.8293"}, {"table_index": 5, "row_index": 17, "col_index": 5, "row_label": "13", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 17, "col_index": 6, "row_label": "13", "col_header": "AMP Scanner Vr.2c", "value": "1.0000"}, {"table_index": 5, "row_index": 17, "col_index": 7, "row_label": "13", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 17, "col_index": 8, "row_label": "13", "col_header": "iAMPpredd", "value": "0.93"}, {"table_index": 5, "row_index": 17, "col_index": 9, "row_label": "13", "col_header": "", "value": "0.81"}, {"table_index": 5, "row_index": 17, "col_index": 10, "row_label": "13", "col_header": "", "value": "0.77"}, {"table_index": 5, "row_index": 17, "col_index": 11, "row_label": "13", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 18, "col_index": 2, "row_label": "14", "col_header": "Peptide Namea", "value": "F1W-GGN5N11"}, {"table_index": 5, "row_index": 18, "col_index": 3, "row_label": "14", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 18, "col_index": 4, "row_label": "14", "col_header": "AMPlify", "value": "0.9356"}, {"table_index": 5, "row_index": 18, "col_index": 5, "row_label": "14", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 18, "col_index": 6, "row_label": "14", "col_header": "AMP Scanner Vr.2c", "value": "1.0000"}, {"table_index": 5, "row_index": 18, "col_index": 7, "row_label": "14", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 18, "col_index": 8, "row_label": "14", "col_header": "iAMPpredd", "value": "0.96"}, {"table_index": 5, "row_index": 18, "col_index": 9, "row_label": "14", "col_header": "", "value": "0.83"}, {"table_index": 5, "row_index": 18, "col_index": 10, "row_label": "14", "col_header": "", "value": "0.86"}, {"table_index": 5, "row_index": 18, "col_index": 11, "row_label": "14", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 19, "col_index": 2, "row_label": "15", "col_header": "Peptide Namea", "value": "L2W-GGN5N11"}, {"table_index": 5, "row_index": 19, "col_index": 3, "row_label": "15", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 19, "col_index": 4, "row_label": "15", "col_header": "AMPlify", "value": "0.9957"}, {"table_index": 5, "row_index": 19, "col_index": 5, "row_label": "15", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 19, "col_index": 6, "row_label": "15", "col_header": "AMP Scanner Vr.2c", "value": "0.9999"}, {"table_index": 5, "row_index": 19, "col_index": 7, "row_label": "15", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 19, "col_index": 8, "row_label": "15", "col_header": "iAMPpredd", "value": "0.85"}, {"table_index": 5, "row_index": 19, "col_index": 9, "row_label": "15", "col_header": "", "value": "0.86"}, {"table_index": 5, "row_index": 19, "col_index": 10, "row_label": "15", "col_header": "", "value": "0.69"}, {"table_index": 5, "row_index": 19, "col_index": 11, "row_label": "15", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 20, "col_index": 2, "row_label": "16", "col_header": "Peptide Namea", "value": "G3W-GGN5N11"}, {"table_index": 5, "row_index": 20, "col_index": 3, "row_label": "16", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 20, "col_index": 4, "row_label": "16", "col_header": "AMPlify", "value": "0.9971"}, {"table_index": 5, "row_index": 20, "col_index": 5, "row_label": "16", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 20, "col_index": 6, "row_label": "16", "col_header": "AMP Scanner Vr.2c", "value": "1.0000"}, {"table_index": 5, "row_index": 20, "col_index": 7, "row_label": "16", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 20, "col_index": 8, "row_label": "16", "col_header": "iAMPpredd", "value": "0.76"}, {"table_index": 5, "row_index": 20, "col_index": 9, "row_label": "16", "col_header": "", "value": "0.89"}, {"table_index": 5, "row_index": 20, "col_index": 10, "row_label": "16", "col_header": "", "value": "0.60"}, {"table_index": 5, "row_index": 20, "col_index": 11, "row_label": "16", "col_header": "", "value": "ABP, AVP, AFP"}, {"table_index": 5, "row_index": 21, "col_index": 2, "row_label": "17", "col_header": "Peptide Namea", "value": "A4W-GGN5N11"}, {"table_index": 5, "row_index": 21, "col_index": 3, "row_label": "17", "col_header": "Active?b", "value": "✓"}, {"table_index": 5, "row_index": 21, "col_index": 4, "row_label": "17", "col_header": "AMPlify", "value": "0.9917"}, {"table_index": 5, "row_index": 21, "col_index": 5, "row_label": "17", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 21, "col_index": 6, "row_label": "17", "col_header": "AMP Scanner Vr.2c", "value": "1.0000"}, {"table_index": 5, "row_index": 21, "col_index": 7, "row_label": "17", "col_header": "", "value": "AMP"}, {"table_index": 5, "row_index": 21, "col_index": 8, "row_label": "17", "col_header": "iAMPpredd", "value": "0.85"}, {"table_index": 5, "row_index": 21, "col_index": 9, "row_label": "17", "col_header": "", "value": "0.88"}, {"table_index": 5, "row_index": 21, "col_index": 10, "row_label": "17", "col_header": "", "value": "0.70"}, {"table_index": 5, "row_index": 21, "col_index": 11, "row_label": "17", "col_header": "", "value": "ABP, AVP, AFP"}]}, {"table_index": 6, "label": "PDF p11 table1", "caption": "from 12864_2022_8310_MOESM1_ESM.pdf", "footnotes": [], "header_rows": [], "longform_cells": [{"table_index": 6, "row_index": 1, "col_index": 2, "row_label": "18", "col_header": "L5W-GGN5N11", "value": "L5W-GGN5N11"}, {"table_index": 6, "row_index": 1, "col_index": 4, "row_label": "18", "col_header": "0.9819", "value": "0.9819"}, {"table_index": 6, "row_index": 1, "col_index": 5, "row_label": "18", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 1, "col_index": 6, "row_label": "18", "col_header": "1.0000", "value": "1.0000"}, {"table_index": 6, "row_index": 1, "col_index": 7, "row_label": "18", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 1, "col_index": 8, "row_label": "18", "col_header": "0.85", "value": "0.85"}, {"table_index": 6, "row_index": 1, "col_index": 9, "row_label": "18", "col_header": "0.86", "value": "0.86"}, {"table_index": 6, "row_index": 1, "col_index": 10, "row_label": "18", "col_header": "0.69", "value": "0.69"}, {"table_index": 6, "row_index": 1, "col_index": 11, "row_label": "18", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 2, "col_index": 2, "row_label": "19", "col_header": "L5W-GGN5N11", "value": "F6W-GGN5N11"}, {"table_index": 6, "row_index": 2, "col_index": 3, "row_label": "19", "col_header": "", "value": "✓"}, {"table_index": 6, "row_index": 2, "col_index": 4, "row_label": "19", "col_header": "0.9819", "value": "0.9888"}, {"table_index": 6, "row_index": 2, "col_index": 5, "row_label": "19", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 2, "col_index": 6, "row_label": "19", "col_header": "1.0000", "value": "1.0000"}, {"table_index": 6, "row_index": 2, "col_index": 7, "row_label": "19", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 2, "col_index": 8, "row_label": "19", "col_header": "0.85", "value": "0.96"}, {"table_index": 6, "row_index": 2, "col_index": 9, "row_label": "19", "col_header": "0.86", "value": "0.83"}, {"table_index": 6, "row_index": 2, "col_index": 10, "row_label": "19", "col_header": "0.69", "value": "0.86"}, {"table_index": 6, "row_index": 2, "col_index": 11, "row_label": "19", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 3, "col_index": 2, "row_label": "20", "col_header": "L5W-GGN5N11", "value": "K7W-GGN5N11"}, {"table_index": 6, "row_index": 3, "col_index": 4, "row_label": "20", "col_header": "0.9819", "value": "0.9909"}, {"table_index": 6, "row_index": 3, "col_index": 5, "row_label": "20", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 3, "col_index": 6, "row_label": "20", "col_header": "1.0000", "value": "0.9999"}, {"table_index": 6, "row_index": 3, "col_index": 7, "row_label": "20", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 3, "col_index": 8, "row_label": "20", "col_header": "0.85", "value": "0.55"}, {"table_index": 6, "row_index": 3, "col_index": 9, "row_label": "20", "col_header": "0.86", "value": "0.71"}, {"table_index": 6, "row_index": 3, "col_index": 10, "row_label": "20", "col_header": "0.69", "value": "0.28"}, {"table_index": 6, "row_index": 3, "col_index": 11, "row_label": "20", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP"}, {"table_index": 6, "row_index": 4, "col_index": 2, "row_label": "21", "col_header": "L5W-GGN5N11", "value": "V8W-GGN5N11"}, {"table_index": 6, "row_index": 4, "col_index": 3, "row_label": "21", "col_header": "", "value": "✓"}, {"table_index": 6, "row_index": 4, "col_index": 4, "row_label": "21", "col_header": "0.9819", "value": "0.9967"}, {"table_index": 6, "row_index": 4, "col_index": 5, "row_label": "21", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 4, "col_index": 6, "row_label": "21", "col_header": "1.0000", "value": "1.0000"}, {"table_index": 6, "row_index": 4, "col_index": 7, "row_label": "21", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 4, "col_index": 8, "row_label": "21", "col_header": "0.85", "value": "0.86"}, {"table_index": 6, "row_index": 4, "col_index": 9, "row_label": "21", "col_header": "0.86", "value": "0.88"}, {"table_index": 6, "row_index": 4, "col_index": 10, "row_label": "21", "col_header": "0.69", "value": "0.78"}, {"table_index": 6, "row_index": 4, "col_index": 11, "row_label": "21", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 5, "col_index": 2, "row_label": "22", "col_header": "L5W-GGN5N11", "value": "A9W-GGN5N11"}, {"table_index": 6, "row_index": 5, "col_index": 4, "row_label": "22", "col_header": "0.9819", "value": "0.9974"}, {"table_index": 6, "row_index": 5, "col_index": 5, "row_label": "22", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 5, "col_index": 6, "row_label": "22", "col_header": "1.0000", "value": "0.9999"}, {"table_index": 6, "row_index": 5, "col_index": 7, "row_label": "22", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 5, "col_index": 8, "row_label": "22", "col_header": "0.85", "value": "0.85"}, {"table_index": 6, "row_index": 5, "col_index": 9, "row_label": "22", "col_header": "0.86", "value": "0.88"}, {"table_index": 6, "row_index": 5, "col_index": 10, "row_label": "22", "col_header": "0.69", "value": "0.70"}, {"table_index": 6, "row_index": 5, "col_index": 11, "row_label": "22", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 6, "col_index": 2, "row_label": "23", "col_header": "L5W-GGN5N11", "value": "S10W-GGN5N11"}, {"table_index": 6, "row_index": 6, "col_index": 3, "row_label": "23", "col_header": "", "value": "✓"}, {"table_index": 6, "row_index": 6, "col_index": 4, "row_label": "23", "col_header": "0.9819", "value": "0.9810"}, {"table_index": 6, "row_index": 6, "col_index": 5, "row_label": "23", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 6, "col_index": 6, "row_label": "23", "col_header": "1.0000", "value": "0.9999"}, {"table_index": 6, "row_index": 6, "col_index": 7, "row_label": "23", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 6, "col_index": 8, "row_label": "23", "col_header": "0.85", "value": "0.85"}, {"table_index": 6, "row_index": 6, "col_index": 9, "row_label": "23", "col_header": "0.86", "value": "0.94"}, {"table_index": 6, "row_index": 6, "col_index": 10, "row_label": "23", "col_header": "0.69", "value": "0.74"}, {"table_index": 6, "row_index": 6, "col_index": 11, "row_label": "23", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 7, "col_index": 2, "row_label": "24", "col_header": "L5W-GGN5N11", "value": "K11W-GGN5N11"}, {"table_index": 6, "row_index": 7, "col_index": 4, "row_label": "24", "col_header": "0.9819", "value": "0.9824"}, {"table_index": 6, "row_index": 7, "col_index": 5, "row_label": "24", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 7, "col_index": 6, "row_label": "24", "col_header": "1.0000", "value": "0.9999"}, {"table_index": 6, "row_index": 7, "col_index": 7, "row_label": "24", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 7, "col_index": 8, "row_label": "24", "col_header": "0.85", "value": "0.54"}, {"table_index": 6, "row_index": 7, "col_index": 9, "row_label": "24", "col_header": "0.86", "value": "0.70"}, {"table_index": 6, "row_index": 7, "col_index": 10, "row_label": "24", "col_header": "0.69", "value": "0.28"}, {"table_index": 6, "row_index": 7, "col_index": 11, "row_label": "24", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP"}, {"table_index": 6, "row_index": 8, "col_index": 2, "row_label": "25", "col_header": "L5W-GGN5N11", "value": "A4L-GGN5N11"}, {"table_index": 6, "row_index": 8, "col_index": 3, "row_label": "25", "col_header": "", "value": "✓"}, {"table_index": 6, "row_index": 8, "col_index": 4, "row_label": "25", "col_header": "0.9819", "value": "0.9789"}, {"table_index": 6, "row_index": 8, "col_index": 5, "row_label": "25", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 8, "col_index": 6, "row_label": "25", "col_header": "1.0000", "value": "0.9999"}, {"table_index": 6, "row_index": 8, "col_index": 7, "row_label": "25", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 8, "col_index": 8, "row_label": "25", "col_header": "0.85", "value": "0.98"}, {"table_index": 6, "row_index": 8, "col_index": 9, "row_label": "25", "col_header": "0.86", "value": "0.81"}, {"table_index": 6, "row_index": 8, "col_index": 10, "row_label": "25", "col_header": "0.69", "value": "0.97"}, {"table_index": 6, "row_index": 8, "col_index": 11, "row_label": "25", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 9, "col_index": 2, "row_label": "26", "col_header": "L5W-GGN5N11", "value": "A4K-GGN5N11"}, {"table_index": 6, "row_index": 9, "col_index": 3, "row_label": "26", "col_header": "", "value": "✓"}, {"table_index": 6, "row_index": 9, "col_index": 4, "row_label": "26", "col_header": "0.9819", "value": "0.9957"}, {"table_index": 6, "row_index": 9, "col_index": 5, "row_label": "26", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 9, "col_index": 6, "row_label": "26", "col_header": "1.0000", "value": "1.0000"}, {"table_index": 6, "row_index": 9, "col_index": 7, "row_label": "26", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 9, "col_index": 8, "row_label": "26", "col_header": "0.85", "value": "0.99"}, {"table_index": 6, "row_index": 9, "col_index": 9, "row_label": "26", "col_header": "0.86", "value": "0.86"}, {"table_index": 6, "row_index": 9, "col_index": 10, "row_label": "26", "col_header": "0.69", "value": "0.99"}, {"table_index": 6, "row_index": 9, "col_index": 11, "row_label": "26", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 10, "col_index": 2, "row_label": "27", "col_header": "L5W-GGN5N11", "value": "A4F-GGN5N11"}, {"table_index": 6, "row_index": 10, "col_index": 3, "row_label": "27", "col_header": "", "value": "✓"}, {"table_index": 6, "row_index": 10, "col_index": 4, "row_label": "27", "col_header": "0.9819", "value": "0.8982"}, {"table_index": 6, "row_index": 10, "col_index": 5, "row_label": "27", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 10, "col_index": 6, "row_label": "27", "col_header": "1.0000", "value": "1.0000"}, {"table_index": 6, "row_index": 10, "col_index": 7, "row_label": "27", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 10, "col_index": 8, "row_label": "27", "col_header": "0.85", "value": "0.84"}, {"table_index": 6, "row_index": 10, "col_index": 9, "row_label": "27", "col_header": "0.86", "value": "0.85"}, {"table_index": 6, "row_index": 10, "col_index": 10, "row_label": "27", "col_header": "0.69", "value": "0.88"}, {"table_index": 6, "row_index": 10, "col_index": 11, "row_label": "27", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 11, "col_index": 2, "row_label": "28", "col_header": "L5W-GGN5N11", "value": "V8L-GGN5N11"}, {"table_index": 6, "row_index": 11, "col_index": 3, "row_label": "28", "col_header": "", "value": "✓"}, {"table_index": 6, "row_index": 11, "col_index": 4, "row_label": "28", "col_header": "0.9819", "value": "0.9936"}, {"table_index": 6, "row_index": 11, "col_index": 5, "row_label": "28", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 11, "col_index": 6, "row_label": "28", "col_header": "1.0000", "value": "0.9999"}, {"table_index": 6, "row_index": 11, "col_index": 7, "row_label": "28", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 11, "col_index": 8, "row_label": "28", "col_header": "0.85", "value": "0.97"}, {"table_index": 6, "row_index": 11, "col_index": 9, "row_label": "28", "col_header": "0.86", "value": "0.80"}, {"table_index": 6, "row_index": 11, "col_index": 10, "row_label": "28", "col_header": "0.69", "value": "0.96"}, {"table_index": 6, "row_index": 11, "col_index": 11, "row_label": "28", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 12, "col_index": 2, "row_label": "29", "col_header": "L5W-GGN5N11", "value": "V8K-GGN5N11"}, {"table_index": 6, "row_index": 12, "col_index": 3, "row_label": "29", "col_header": "", "value": "✓"}, {"table_index": 6, "row_index": 12, "col_index": 4, "row_label": "29", "col_header": "0.9819", "value": "0.9998"}, {"table_index": 6, "row_index": 12, "col_index": 5, "row_label": "29", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 12, "col_index": 6, "row_label": "29", "col_header": "1.0000", "value": "0.9999"}, {"table_index": 6, "row_index": 12, "col_index": 7, "row_label": "29", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 12, "col_index": 8, "row_label": "29", "col_header": "0.85", "value": "0.99"}, {"table_index": 6, "row_index": 12, "col_index": 9, "row_label": "29", "col_header": "0.86", "value": "0.86"}, {"table_index": 6, "row_index": 12, "col_index": 10, "row_label": "29", "col_header": "0.69", "value": "0.98"}, {"table_index": 6, "row_index": 12, "col_index": 11, "row_label": "29", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 13, "col_index": 2, "row_label": "30", "col_header": "L5W-GGN5N11", "value": "V8F-GGN5N11"}, {"table_index": 6, "row_index": 13, "col_index": 3, "row_label": "30", "col_header": "", "value": "✓"}, {"table_index": 6, "row_index": 13, "col_index": 4, "row_label": "30", "col_header": "0.9819", "value": "0.9943"}, {"table_index": 6, "row_index": 13, "col_index": 5, "row_label": "30", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 13, "col_index": 6, "row_label": "30", "col_header": "1.0000", "value": "0.9999"}, {"table_index": 6, "row_index": 13, "col_index": 7, "row_label": "30", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 13, "col_index": 8, "row_label": "30", "col_header": "0.85", "value": "0.84"}, {"table_index": 6, "row_index": 13, "col_index": 9, "row_label": "30", "col_header": "0.86", "value": "0.84"}, {"table_index": 6, "row_index": 13, "col_index": 10, "row_label": "30", "col_header": "0.69", "value": "0.88"}, {"table_index": 6, "row_index": 13, "col_index": 11, "row_label": "30", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP, AFP"}, {"table_index": 6, "row_index": 14, "col_index": 2, "row_label": "31", "col_header": "L5W-GGN5N11", "value": "A4W/V8W-GGN5N11"}, {"table_index": 6, "row_index": 14, "col_index": 3, "row_label": "31", "col_header": "", "value": "✓"}, {"table_index": 6, "row_index": 14, "col_index": 4, "row_label": "31", "col_header": "0.9819", "value": "0.9970"}, {"table_index": 6, "row_index": 14, "col_index": 5, "row_label": "31", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 14, "col_index": 6, "row_label": "31", "col_header": "1.0000", "value": "1.0000"}, {"table_index": 6, "row_index": 14, "col_index": 7, "row_label": "31", "col_header": "AMP", "value": "AMP"}, {"table_index": 6, "row_index": 14, "col_index": 8, "row_label": "31", "col_header": "0.85", "value": "0.86"}, {"table_index": 6, "row_index": 14, "col_index": 9, "row_label": "31", "col_header": "0.86", "value": "0.91"}, {"table_index": 6, "row_index": 14, "col_index": 10, "row_label": "31", "col_header": "0.69", "value": "0.30"}, {"table_index": 6, "row_index": 14, "col_index": 11, "row_label": "31", "col_header": "ABP, AVP, AFP", "value": "ABP, AVP"}]}]

=== PRIMARY PAPER FULL TEXT (context only) ===
Use this ONLY to (a) confirm whether an organism/target/assay was tested in this paper (prevents false 'absent' calls), and (b) read an endpoint label. You may NOT cite full text as the `evidence` cell for is_database_error=true; that still requires a structured longform cell.
(2022) 23:77
Li et al. BMC Genomics
https://doi.org/10.1186/s12864-022-08310-4

RESEARCH ARTICLE

Open Access

AMPlify: attentive deep learning model
for discovery of novel antimicrobial peptides
effective against WHO priority pathogens
Chenkai Li1,2, Darcy Sutherland1,3,4, S. Austin Hammond1, Chen Yang1,2, Figali Taho1,2, Lauren Bergman5,
Simon Houston5, René L. Warren1, Titus Wong4,6, Linda M. N. Hoang3,4, Caroline E. Cameron5,7,
Caren C. Helbing5 and Inanc Birol1,3,4,8*

Abstract
Background: Antibiotic resistance is a growing global health concern prompting researchers to seek alternatives
to conventional antibiotics. Antimicrobial peptides (AMPs) are attracting attention again as therapeutic agents with
promising utility in this domain, and using in silico methods to discover novel AMPs is a strategy that is gaining interest. Such methods can sift through large volumes of candidate sequences and reduce lab screening costs.
Results: Here we introduce AMPlify, an attentive deep learning model for AMP prediction, and demonstrate its utility
in prioritizing peptide sequences derived from the Rana [Lithobates] catesbeiana (bullfrog) genome. We tested the
bioactivity of our predicted peptides against a panel of bacterial species, including representatives from the World
Health Organization’s priority pathogens list. Four of our novel AMPs were active against multiple species of bacteria,
including a multi-drug resistant isolate of carbapenemase-producing Escherichia coli.
Conclusions: We demonstrate the utility of deep learning based tools like AMPlify in our fight against antibiotic
resistance. We expect such tools to play a significant role in discovering novel candidates of peptide-based alternatives to classical antibiotics.
Keywords: Antimicrobial peptide, Deep learning, Attention mechanism
Background
As reported by the World Health Organization (WHO),
the decreasing effectiveness of antibiotics and other antimicrobial agents indicates the world is at a risk of entering a “post-antibiotic era” [1]. To counter this threat, new
drugs or effective substitutes for conventional antibiotics are urgently needed. Antimicrobial peptides (AMPs)
are one such alternative. AMPs are host defense molecules produced by all forms of life, including multicellular organisms as part of their innate immunity against
*Correspondence: ibirol@bcgsc.ca
8
Department of Medical Genetics, University of British Columbia,
Vancouver, BC V6H 3N1, Canada
Full list of author information is available at the end of the article

microbes. Within their respective hosts, eukaryotic
AMPs have co-evolved with microorganisms to serve
as a defense against bacterial [2], fungal [3] and even
viral infections [4]. Unlike most conventional antibiotics, which have specific functional or structural targets,
AMPs act directly on the microorganisms, often causing cell lysis, or modulate the host immunity to enhance
defense against microorganisms [5]. Also, they act faster
than conventional antibiotics [6], have a narrower active
concentration window for killing [7], and do not typically
damage the DNA of their targets [8, 9]. As a result, they
do not induce resistance to the extent that is observed
with conventional antibiotics [10]. Nevertheless, if bacteria are exposed to AMPs for extended periods of time,

© The Author(s) 2022. Open Access This article is licensed under a Creative Commons Attribution 4.0 International License, which
permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the
original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or
other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line
to the material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory
regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this
licence, visit http://​creat​iveco​mmons.​org/​licen​ses/​by/4.​0/. The Creative Commons Public Domain Dedication waiver (http://​creat​iveco​
mmons.​org/​publi​cdoma​in/​zero/1.​0/) applies to the data made available in this article, unless otherwise stated in a credit line to the data.

Li et al. BMC Genomics

(2022) 23:77

they can and do develop resistance even to peptide-based
drugs including the last resort and life-saving drug, colistin [10, 11]. Hence, fast and accurate methods would be
valuable tools to discover and design effective AMPs to
enhance our repertoire of alternative therapeutics.
Direct, large scale discovery of novel AMPs through
wet lab screening is time-consuming, labor-intensive
and costly [12]. For these reasons, various computational
models have been developed over the last few years [12]
to streamline in silico AMP prediction. Despite the rapid
progress in the field, currently available models still have
substantial room for improvement.
The AMP prediction module in the Collection of Antimicrobial Peptides (CAMP) database [13] includes four
different models: random forest, support vector machine,
discriminant analysis, and a single-hidden-layer feed-forward neural network with 64 designed features [14]. The
iAMP-2L online server adopts fuzzy K-nearest neighbor algorithm, taking pseudo amino acid compositions
(PseAAC) with five physicochemical properties as input
features to predict AMPs as well as their potential microorganism targets [15]. The iAMPpred online server for
AMP prediction and classification is based on support
vector machine and uses PseAAC with compositional,
physicochemical, and structural features [16]. All three of
these tools employ conventional machine learning methods and rely on pre-designed features, requiring prior
expertise in AMP structure and mechanism for effective
engineering.
Alternatively, deep learning methods can automatically learn high-level features and usually outperform
conventional methods in many bioinformatics tasks [17].
Recently, few teams developed deep learning models
for the AMP prediction task. Youmans and co-workers
demonstrated the feasibility of using a bidirectional long
short-term memory [18–20] (Bi-LSTM) recurrent neural
network (RNN) for AMP prediction [21], but the authors
do not offer any public code or tool that implements their
model. The Deep-AmPEP30 online server applies a convolutional neural network (CNN) for AMP prediction
[22], though the tool is restricted to working with short
peptides up to 30 amino acids (aa) in length. The DeepABPpred online server adopts Bi-LSTM with word2vec
[23], also for short (≤ 30 aa) peptides [24]. The Bi-LSTM
model from Wang and co-workers is designed for even
shorter peptides (≤ 20 aa) and specializes to predicting
AMPs against Escherichia coli [25]. They also provide
a workflow for designing novel AMPs. Veltri and coworkers introduced a deep neural network classifier with
embedding, convolutional, max pooling, and long shortterm memory (LSTM) recurrent layers which is available
as an online server, AMP Scanner Vr.2, as its user interface [26]. AMP Scanner Vr.2 is the only tool in the deep

Page 2 of 15

learning category that does not have a strong limitation
in input sequence lengths; it can handle sequences up to
200 aa.
While AMP Scanner Vr.2 outperforms the conventional machine learning methods cited above, we note
that its neural network architecture is not designed
for extracting long-range information along peptide sequences. Common deep learning methods for
sequence classification include recurrent neural networks
(RNNs) and convolutional neural networks (CNNs), as
employed in combination by AMP Scanner Vr.2. RNNs
can learn remote dependencies inside a sequence, but
suffer from vanishing gradients [27]. Similarly, while
CNNs can extract local information well, it ignores longrange dependencies [28].
Recently, deep neural networks with attention mechanisms have gained interest, notably for natural language
processing [29–31] and computer vision [32] applications. Attention mechanisms, as the name suggests, are
inspired by our brains’ ability to prioritize segments of
information when processing textual or visual input. In
sequence analysis, attention mechanisms are modeled
by weights assigned to different positions in a sequence.
These weights amplify or attenuate information from a
given position to help encode the global information of
the sequence.
Here, we introduce AMPlify, an attentive deep learning model that improves in silico AMP prediction by
applying two types of attention mechanisms layered on
a bidirectional long short-term memory [18–20] (BiLSTM) layer (Fig. 1). The Bi-LSTM layer in the model,
as a variant of RNN, encodes positional information
from the input sequence in a recurrent manner. Subsequently, the multi-head scaled dot-product attention [30]
(MHSDPA) layer computes a refined representation of
the sequence using multiple weight vectors. The last hidden layer of context attention [31] (CA) generates a single
summary vector using weighted average, learning contextual information gained from the previous layer. The
AMPlify model is trained on a set of known AMPs and a
select list of non-AMP sequences, and adopts ensemble
learning to further improve its performance. To the best
of our knowledge, AMPlify is the first machine learning
application that applies attention mechanisms for in silico AMP prediction. We note that non-standard amino
acids are not taken into consideration in this study, and
we mainly focus on AMPs from multicellular organisms
for discovery.
To illustrate the utility of our model, a discovery pipeline based on AMPlify was used to mine the
AMP-rich North American bullfrog (Rana [Lithobates]
catesbeiana) genome for novel natural AMPs. Previously, the North American bullfrog has been described

Li et al. BMC Genomics

(2022) 23:77

Page 3 of 15

Fig. 1 Model architecture of AMPlify. Residues of a peptide sequence are one-hot encoded and passed to three hidden layers in order: the
bidirectional long short-term memory (Bi-LSTM) layer, the multi-head scaled dot-product attention (MHSDPA) layer and the context attention (CA)
layer. The output layer generates the probability that the input sequence is an AMP

as a rich source for natural AMPs, yielding potent
classes of bioactive molecules such as ranateurins,
ranacyclins, temporins, and palustrins [33, 34]. In our
tests, AMPlify successfully identified these previously
reported AMPs, along with four novel AMPs with biological activity in vitro.
The WHO has a published list of priority pathogens
for which new antibiotics are urgently needed [35].
This list includes bacterial species that are increasingly
resistant to multiple antibiotics. We tested the efficacy
of our discovered, putative AMPs against selected Priority Pathogens, including: 1) Pseudomonas aeruginosa
and Escherichia coli strains, including a multi-drug
resistant (MDR) carbapenemase-producing (CPO)
strain of E. coli reflective of WHO’s “Priority 1” pathogens; and 2) a Staphylococcus aureus strain reflective
of WHO’s “Priority 2” methicillin-resistant (MRSA)
and vancomycin-resistant (VRSA) strains. A Streptococcus pyogenes strain was included as an additional
Gram-positive bacterial species that causes human
disease, while this bacterial species has demonstrated
antibiotic resistance in some earlier works [36].
In our tests, four of the 16 novel AMPs discovered
show considerable antimicrobial potency against one
or more of the organisms examined, including the
clinical MDR isolate of CPO E. coli. These results
highlight the potential of AMPlify to accelerate AMP
discovery, the first step towards facilitating peptidebased therapeutics.

Results
Evaluation of model architecture

To demonstrate the effectiveness of each component
within our model, we evaluated the model architecture
starting from a single Bi-LSTM layer and then gradually
adding attention layers over it. Supplementary Table S1
summarizes the results of our ablation study, comparing different model architectures using stratified 5-fold
cross-validation on the training set with regard to five
different measures of (1) accuracy, (2) sensitivity, (3)
specificity, (4) F1 score, and (5) area under the receiver
operating characteristic curve (AUROC). The first section of the table compares the performance of the complete architecture of AMPlify, with and without ensemble
learning, with simpler variations, which include fewer
hidden layers. The architecture of the only deep learning based comparator, AMP Scanner Vr.2, was crossvalidated on our training set for comparison using two
different stopping settings: the optimal fixed number of
epochs as stated in their manuscript [26] and early stopping as described in this paper (Supplementary Table S1,
second section). Although overall performance of AMP
Scanner Vr.2 is not strongly influenced by early stopping,
it does lead to smaller performance variability as measured by standard deviation values in tests, indicating that
the model trained using early stopping is more robust
than using a default of 10 epochs.
By adding a single CA layer atop the Bi-LSTM layer,
the model performs similarly to AMP Scanner Vr.2
based on cross-validation results, with differences

Li et al. BMC Genomics

(2022) 23:77

Page 4 of 15

smaller than 1% in all metrics except specificity
(< 1.4%). After inserting an MHSDPA layer in the middle, the cross-validation results for our model reach
91.70% in accuracy, 91.40% in sensitivity, 92.00% in
specificity, 91.68% in F1 score, and 96.92% in AUROC
– an overall improvement compared with the architecture without this layer. This indicates that the attention layer learns discriminating features of sequences
processed by the Bi-LSTM layer. We note that the final
AMPlify architecture already outperforms the AMP
Scanner Vr.2 architecture in all metrics in our crossvalidation tests. After applying ensemble learning to
the proposed architecture, the cross-validation performance is further improved to 92.79% for accuracy,
92.12% for sensitivity, 93.47% for specificity, 92.74% for
F1 score and 97.44% for AUROC.
To test whether the improvement of our model is
statistically significant, we performed paired Student
t-tests based on cross-validation results. These tests indicate statistically significant increase in performance of
AMPlify over AMP Scanner Vr.2 (early stopped) with
regard to all five metrics (p < 0.05). The better performance of AMPlify without ensemble learning (i.e. BiLSTM+MHSDPA+CA) over the simple Bi-LSTM model
is also statistically significant in all metrics (p < 0.05), suggesting that the attention layers play an important role in
the model’s performance.
Further, we cross-validated AMPlify on the dataset
provided by AMP Scanner Vr.2 and observed that the
deep neural network architecture chosen in AMPlify
is overall better for the AMP prediction task compared

with the architecture of AMP Scanner Vr.2 (Supplementary Note S1, Supplementary Table S2).
Comparison with state‑of‑the‑art methods

With the set of hyperparameters tuned through stratified
5-fold cross-validation, the final model of AMPlify was
trained using the entire training set, with each of the five
single sub-models trained on five different subsets. Here,
single sub-model refers to the model with full architecture (Bi-LSTM+MHSDPA+CA) before ensemble learning. AMPlify, along with its single sub-models, were
compared on our test set with three other state-of-theart tools: iAMP-2L [15], iAMPpred [16] and AMP Scanner Vr.2 [26] (Table 1). All the tools were evaluated with
their original trained models reported. In this list of comparators, AMP Scanner Vr.2 could be trained using third
party datasets through a utility provided by the authors
(personal communication with Daniel Veltri), and was
re-trained on our training set with two different stopping
conditions, as previously stated.
Among the original models of the three comparators,
AMP Scanner Vr.2 performs the best on our data in
general, except for its specificity, which is 1.31% lower
than iAMP-2L. The accuracy, specificity, F1 score, and
AUROC of AMP Scanner Vr.2 were all improved after retraining, with only small changes in sensitivity (< 0.5%).
Still, in our benchmarks AMPlify outperforms the comparators tested, including the two re-trained versions of
AMP Scanner Vr.2. AMPlify achieves the highest accuracy (93.71%), F1 score (93.66%) and AUROC (98.37%),
improving upon the performance of the next-best, the
re-trained versions of AMP Scanner Vr.2, by 2.51, 2.53

Table 1 Performance comparison among different tools on the test set. Performance of different tools are presented with five metrics
in percentage: accuracy (acc), sensitivity (sens), specificity (spec), F1 score (F1) and area under the receiver operating characteristic
curve (AUROC)
Tool

Model

Acc

Sens

Spec

F1

AUROC

iAMPpred

originala

74.01

87.90

60.12

77.18

80.70

iAMP-2L

originala

77.96

88.26

67.66

80.02

–

AMP Scanner Vr.2

originala

78.50

90.66

66.35

80.83

88.33

re-trained, 10 ­epochsb

90.66

91.14

90.18

90.70

97.40

re-trained, early ­stoppedc

91.20

90.42

91.98

91.13

97.03

single sub-model 1

92.40

90.90

93.89

92.28

97.54

AMPlify

a

single sub-model 2

91.98

91.02

92.93

91.90

97.40

single sub-model 3

92.51

92.69

92.34

92.53

97.82

single sub-model 4

92.10

90.90

93.29

92.00

97.27

single sub-model 5

92.57

92.57

92.57

92.57

97.98

ensemble

93.71

92.93

94.49

93.66

98.37

Models presented in the referenced papers are available through online servers

b

The best hyperparameter as stated in the referenced paper

c

The optimal number of training epochs determined by early stopping is 16

Li et al. BMC Genomics

(2022) 23:77

Page 5 of 15

Fig. 2 Performance comparison of different AMP prediction tools based on the test sequence similarities to their corresponding training sets. F1
scores of AMP prediction tools were calculated on test subsets based on similarities to sequences in the training sets. All the AMP/non-AMP test
subsets were derived from the AMPlify test data, with subsets containing 10 or fewer sequences removed. The size of the round makers indicates
the number of sequences remaining in the test subset given the similarity threshold

and 0.97% respectively. AMPlify also shows the highest
sensitivity (92.93%) and specificity (94.49%) in our tests,
suggesting that the model can concurrently reduce false
negative and false positive predictions. We have also analyzed the performance of different tools by stratifying the
test set based on sequence similarities to their training
sets, again showing how AMPlify performs favourably
across this spectrum (Fig. 2, Supplementary Note S2).
Further, all five single sub-models of AMPlify yield
favourable performance in accuracy (91.98–92.57%),
specificity (92.34–93.89%) and F1 score (91.90–92.57%),
despite each single sub-model being trained on 80% of the
entire training set (see 9). The sensitivity values of the five
single sub-models range from 90.90 to 92.69%, with two
of them being better than the performance of all comparators, while the remaining three being slightly lower
than the performance of the re-trained, 10 epochs model
of AMP Scanner Vr.2 (< 0.25%). Still, the lower standard
deviation values from cross-validation analysis indicate
that those single sub-models of AMPlify are more robust
compared with the re-trained, 10 epochs model of AMP
Scanner Vr.2 (Supplementary Table S1). Similarly, our
single sub-models score higher than the comparators in

AUROC, except one of them being on par with the best
AMP Scanner Vr.2 model and another scoring lower by
0.13%. The specificity values of the original models of the
three comparators are relatively low (< 70%), likely due to
their less stringent selection criteria when building their
non-AMP sets. The specificity values of AMP Scanner
Vr.2 improved substantially after being re-trained on our
training set (90.18% or 91.98%, depending on the number of epochs trained, Table 1). We have also conducted
a cross-comparison of AMPlify with AMP Scanner Vr.2,
re-training our tool on the dataset provided by the AMP
Scanner Vr.2 publication [26], illustrating the improved
learning capability of our chosen architecture for the
AMP prediction task (Supplementary Note S1, Supplementary Table S3, Supplementary Fig. S1).
For a comparison of the classification performance of
each tool with regard to different classification thresholds, Fig. 3a presents a series of receiver operating characteristic (ROC) curves for the models compared. The
AUROC results shown in Table 1 correspond to these
ROC curves. Note that the iAMP-2L online server does
not allow for parameterization, hence the tool is represented by a single data point and no AUROC value. The

Li et al. BMC Genomics

(2022) 23:77

Page 6 of 15

Fig. 3 Visualization of AMPlify model performance and the AMP discovery pipeline application results. a Receiver operating characteristic (ROC)
curves of AMPlify and comparators are plotted, with round dots marking the performance at the threshold of 0.5. The iAMP-2L online server only
output labels of AMP/non-AMP without the corresponding probabilities, so it appears as a single point on the plot. b AMPlify prediction scores
against peptide lengths of 101 sequences analyzed by AMPlify. The grey dotted line represents the score threshold of 0.5 used to distinguish AMPs
from non-AMPs. Inset shows amplified view of the upper left region of the plot to enhance visualization of the majority of the selected sequences

ROC curves indicate that AMPlify is Pareto-optimal in
our tests for any classification threshold.
AMP discovery

Previous studies have shown that the skin secretions of
amphibians are rich in AMPs, which help the animals
prevent infection by harmful microorganisms [37]. For
this reason, mining the genomes of various frog species
for novel AMPs is an attractive proposition. To demonstrate AMPlify’s practical application, it was embedded
into a bioinformatics pipeline to find novel AMPs from
the North American bullfrog (Rana [Lithobates] catesbeiana) genome [33, 34]. For antimicrobial susceptibility
testing (AST), we focus on cationic AMPs acting directly
on biological membranes, the activities of which can be
directly observed in vitro. Most amphibian AMP precursors possess highly conserved N-terminal prepro regions
and hypervariable C-terminal antimicrobial domains
[37]. The prepro regions usually end with a lysine-arginine signal for cleavage to produce bioactive AMPs [37].
Based on this, we identified candidate precursors from
the bullfrog genome using homology search and genome
annotation tools. We then derived candidate mature
sequences from those precursors to use as input for
AMPlify (see 9 for pipeline details). This resulted in 101
candidate mature sequences, which we fed into AMPlify,
predicting 75 of them to be putative AMPs. We selected
peptides between five to 35 amino acids in length with

a positive charge for further analysis, yielding a final list
of 16 peptides (Table 2), five of which were previously
reported sequences [34, 38, 39]. The remaining 11 peptides were synthesized and evaluated in vitro. The UpSet
plot in Supplementary Fig. S2 summarizes the results
obtained by applying different combinations of the aforementioned three filters (AMPlify prediction score, length,
and charge) to the 101 candidate mature sequences.
Figure 3b shows a visualization of AMPlify prediction
results for the 101 candidate mature sequences.
Antimicrobial susceptibility testing (AST)

A panel composed of six bacteria was selected to test candidate AMP sequences identified using AMPlify: Staphylococcus aureus ATCC 6538P, Streptococcus pyogenes
(unknown strain; hospital isolate), Pseudomonas aeruginosa ATCC 10148, Escherichia coli ATCC 9723H and
ATCC 29522, and an MDR carbapenemase-producing
New-Delhi metallobetalactamase (CPO-NDM) Escherichia coli clinical isolate. E. coli ATCC 29522 was used as
a wild-type drug susceptible control strain. Results from
AST are presented in Table 3. Supplementary Table S4
provides additional data with results shown in μg/mL.
The 11 putative AMP sequences were selected for
in vitro AST experiments, and four of them displayed
antimicrobial activity against the targets tested: RaCa1, RaCa-2, RaCa-3, and RaCa-7. RaCa-1 was antibacterial against all E. coli strains tested (MIC = 10–39 μM,

Li et al. BMC Genomics

(2022) 23:77

Page 7 of 15

Table 2 Putative and reported AMP sequences discovered from Rana [Lithobates] catesbeiana. Genomic and transcriptomic resources
from Rana [Lithobates] catesbeiana [33] were mined using the AMP discovery pipeline based on AMPlify. Top-scoring peptide
sequences were selected for synthesis and validation in vitro
Peptide Name

Sequence

# aa

Net ­Chargea

MW (Da)

AMPlify Score

RaCa-1

GLLDIIKTTGKDFAVKILDNLKCKLAGGCPP

31

2

3242.93

1.0000

RaCa-2

FFPIIARLAAKVIPSLVCAVTKKC

24

4

2589.28

1.0000
1.0000

Ranatuerin-2PRc*

AFLSTVKNTLTNVAGTMIDTFKCKITGVC

29

2

3077.66

Temporin-1Cb*+

FLFPLITSFLSKFLGK

16

2

1858.30

1.0000

Palustrin-Ca*

GFLDIIKDTGKEFAVKILNNLKCKLAGGCPP

31

2

3303.97

1.0000

Ranatuerin-2RC*

GLFLDTLKGAAKDVAGKLLEGLKCKITGCKP

31

3

3188.88

1.0000

RaCa-3

GLWETIKTTGKSIALNLLDKIKCKIAGGCPP

31

3

3269.95

1.0000

Ranatuerin-2C*

GVFLDTLKGLAGKMLESLKCKIAGCKP

27

3

2821.49

0.9999

RaCa-4

FLTFPGMTFGKLLGK

15

2

1657.05

0.9997

RaCa-5

GLLDIIKDTGKTTGILMDTLKCQMTGRCPPSS

32

1

3395.02

0.9996

RaCa-6

ATAWRIPPPGMQPIIPIRIRPLCGKQ

26

4

2910.58

0.9994

RaCa-7

FFPRVLPLANKFLPTIYCALPKSVGN

26

3

2906.52

0.9985

RaCa-8

FPAIICKVSKNC

12

2

1322.65

0.9961

RaCa-9

FYFPVSRKFGGK

12

3

1432.69

0.9412

RaCa-10

ALVAKIQKFPVFNTLKLCKLELEII

25

2

2872.59

0.6063

RaCa-11

SNRDFFKVNIFRLCG

15

2

1816.11

0.6058

*Previously reported amphibian peptide sequences [34, 38, 39]
+

Previously reported as a full-length AMP precursor sequence. Uniprot ID: C5IB07

a

Net charge at pH = 7

MBC = 10–79 μM). RaCa-1 also showed minimal antimicrobial activity against S. pyogenes (MIC/MBC ≥ 79 μM)
with no observed inhibition against the S. aureus and
P. aeruginosa isolates. RaCa-2 and RaCa-3 inhibited all
bacterial strains tested. RaCa-2 possessed the strongest antibacterial activity against S. aureus and E. coli
isolates, preventing growth of both species of bacteria
at concentrations of 1–2 μM and 2–6 μM, respectively.
Specifically, this peptide was bactericidal against E. coli
ATCC 9723H (MIC/MBC = 3–6 μM), with similar activity observed against E. coli ATCC 25922 and the MDR E.
coli CPO-NDM isolates (MIC/MBC = 2–6 μM). RaCa-2
was also the only AMP tested to have robust bactericidal action against both S. aureus (MIC/MBC = 1–2 μM)
and S. pyogenes (MIC/MBC = 25–49 μM). Comparably, RaCa-3 was considerably potent in vitro against S.
pyogenes (MIC = 39 μM, MBC = 39–≥78 μM), P. aeruginosa (MIC = 20–≥78 μM, MBC = 39–≥78 μM), E.
coli (MIC = 2–10 μM, MBC = 2–20 μM), and to a lesser
extent S. aureus (MIC ≥78 μM, MBC = NI). RaCa-7
was active against all strains of E. coli (MIC = 6–44 μM,
MBC = 6–88 μM), with minimal inhibition of S. aureus
(MIC ≥88 μM, MBC = NI), and no activity against the
other two species. Overall, the four novel AMP sequences
displayed the strongest activity against the tested E. coli
strains. RaCa-2 and RaCa-3 each had potent antibacterial
action against the MDR E. coli (CPO-NDM) inhibiting

bacterial growth at ≤10 μM. Of particular note, there was
little or no observed shift in MIC and MBC values when
comparing the CPO-NDM E. coli isolate to the ATCC
25922 wild-type control strain.
The positive control peptide LL37 [34] displayed
potent antimicrobial activity against all strains of E.
coli (MIC = 2–4 μM, MBC = 2–7 μM) and P. aeruginosa
(MIC = 7–≥57 μM, MBC = 7–≥57 μM). However, this
peptide had no activity against the tested strains of S.
aureus and S. pyogenes, respectively. The negative control
peptide, Tp0751, a non-functional truncated section of a
Treponema pallidum protein with similar characteristics
to AMPs [42], was inactive against all organisms.

Discussion
Here we present AMPlify, a robust attentive deep learning model for AMP prediction, and demonstrate its utility in identifying novel AMPs with broad antimicrobial
activities. It implements ensemble learning by partitioning its training set – a novel approach – and outperforms
existing machine learning methods, including a leading
deep learning based model. The two attention mechanisms in AMPlify are inspired by how humans perceive
natural language, paying closer attention to regions or
words of interest in a sentence. We have observed that
single sub-models of AMPlify were able to outperform
the state-of-the-art methods without ensemble learning,

Li et al. BMC Genomics

(2022) 23:77

Page 8 of 15

Table 3 Minimum inhibitory concentrations (MIC) and minimum bactericidal concentrations (MBC) of selected AMP candidates
following antimicrobial susceptibility testing (AST) in vitro. Candidate antimicrobial peptides were synthesized and purchased from
Genscript. AST, and MIC/MBC determination was performed as outlined by the Clinical and Laboratory Standards Institute (CLSI) [40],
with modification as recommended by Hancock [41]. Data is presented as the lowest effective peptide concentration range (μM)
observed in three independent experiments. LL37, human cathelicidin and a peptide from Tp0751 from Treponema pallidum were
used as the positive and negative control peptides [34], respectively
S. aureusaATCC
6538P

S. pyogenesb

P. aeruginosaaATCC
10148

E. coliaATCC 9723H

E. colicATCC 25922

MDR E. colid(CPONDM)

Gram-positive

Gram-positive

Gram-negative

Gram-negative

Gram-negative

Gram-negative

(μM)

MIC

MBC

MIC

MBC

MIC

MBC

MIC

MBC

MIC

MBC

MIC

MBC

RaCa-1

NI

NI

79

NI

20 – 39

39 – 79

10 – 20

10 – 39

20 – 39

20 – 39

1–2

1–2

25 – 49

≥ 79

NI

RaCa-2

25 – 49

25 – 49

3–6

3–6

2–6

2–6

2–6

2–6

RaCa-3

≥78

NI

39

2–5

2–5

5 – 10

5 – 20

NI

39 – ≥78

5 – 10

NI

20 – ≥78

5 – 10

NI

39 – ≥ 78

49 – ≥99
NI

NI

NI

–

–

–

–

RaCa-5

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

RaCa-6

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

RaCa-7

≥ 88

NI

NI

NI

NI

NI

11 – 22

11 – 88

6 – 44

6 – 44

6 – 44

6 – 44

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

RaCa-9

NI

NI

NI

NI

NI

NI

NI

NI

–

–

–

–

RaCa-10

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

NI

RaCa-11

NI

NI

NI

NI

NI

NI

NI

NI

–

–

–

–

LL37

NI

NI

NI

NI

4–7

2–4

2–4

2–4

2–4

NI

NI

NI

NI

7 – ≥57

2–4

Tp0751

7 – ≥57

NI

NI

NI

NI

NI

NI

RaCa-4

RaCa-8

a

NI

NI

NI

NI

Bacteria obtained and tested at the University of Victoria

b

Unknown strain; hospital isolate

c

ATCC quality control strain #25922 purchased from Cedarlane Laboratories (Burlington, Ontario, Canada)

d

Clinical isolate obtained and tested at the British Columbia Centre for Disease Control

NI, no inhibition observed in vitro
‘—’ = not tested

Abbreviations: Staphylococcus aureus, Streptococcus pyogenes, Pseudomonas aeruginosa, Escherichia coli, ATCC​American Type Culture Collection, CPO carbapenemaseproducing organism, MDR multi-drug resistant, NDM New-Delhi Metallo-beta-lactamase

and we were able to trace the source of this favourable
performance to the inclusion of attention layers.
Although machine learning methods in general, and
AMPlify in particular, perform well in predicting AMPs,
their performance can be limited by a paucity of detailed
AMP sequence data available for training. First, the models do not usually consider the potential target microorganisms for the predicted AMPs. Although some
methods report success at that level of granularity using
public data [15, 16], incomplete and incorrect annotations in AMP databases are confounding. Second, the
models cannot distinguish whether an AMP acts directly
on biological membranes and/or by modulating the host
immunity, since there is no consistently available data
on these features. AMPs acting only in the latter mode
require separate assays and might differ in activity within
different species. Third, the size of the training data is
still small relative to the data typically employed in most
deep learning applications. Specially, having more similar sequences with different antimicrobial activities (i.e.

non-AMPs that are similar to known AMPs) in the training set might help the model to be more sensitive to small
changes in the sequences for prediction. However, availability of such information is limited. As a result, all the
publicly available AMP prediction tools face difficulty in
differentiating between AMPs and non-AMPs that are
highly similar in their sequences (Supplementary Note
S3, Supplementary Table S5). We expect this limitation to
be gradually alleviated as more AMPs are discovered and
more AMP mutation and truncation studies are done,
inspired by tools like AMPlify. Although the size of the
training data is unlikely to ever match what is available
in natural language processing, image classification, and
social network analysis domains, to name a few, AMP
prediction tools can still find practical applications as
demonstrated here.
Using AMPlify, four novel AMPs were identified with
proven activity against a variety of bacterial isolates.
Promisingly, two of the four presented AMPs demonstrate potent antibacterial activity against the MDR E.

Li et al. BMC Genomics

(2022) 23:77

coli tested, and there was little or no observed shift in
MIC when comparing the MDR and drug-susceptible
strains. This suggests that the mechanism-of-action of
these AMPs is unlike those used by conventional antibiotics. Thus, AMPs, such as those presented in the current
study, have the potential to be used in future drug and
clinical development studies as peptide-based substitutes
to classical antibiotics. Although several candidates identified using this pipeline did not show any in vitro activity against the bacteria tested, we speculate that they still
may possess activity against other bacterial species or
other microorganisms (e.g. fungi, virus), or may demonstrate activity in vivo via host immune response modulation. Further, the structures of these sequences are
highly dynamic and susceptible to change in response to
the surrounding microenvironment, as is frequently the
case with amphipathic alpha helices. These AMPs may
act as monomers or form multimeric complexes, with
their secondary structure flexibly changing in response to
interaction with membranes or free divalent cations [43].
Further studies are required to interrogate AMP mechanisms as these phenomena are not readily observed using
classical in vitro methods.
Of course, the utility of tools like AMPlify is not limited
to discovering AMPs from the bullfrog genome; they can
be generically applied to any input sequence. As such,
they have the potential to play a role in de novo AMP
design or enhancement. In conclusion, with their various
use cases, we foresee tools like AMPlify as being instrumental in expanding the current arsenal of antimicrobial
agents effective against WHO priority pathogens.

Conclusions
This study introduces a novel attentive deep learning
model, AMPlify, for AMP prediction, and has identified
four novel AMPs from the bullfrog genome with promising antibacterial activity against an MDR WHO priority
pathogen. We illustrate the value of attention mechanisms and a novel ensemble approach in mining genome
resources for novel AMPs, comparing the performance
of AMPlify to the state-of-the art machine learning models. AMPlify is released as an open source tool (https://​
github.​com/​bcgsc/​AMPli​f y) under the GPL-3.0 license.
Methods
Generation of the datasets

We used publicly available AMP sequences to train and
test AMP predictors. In order to build a non-redundant AMP dataset, we first downloaded all available
sequences from two manually curated databases: Antimicrobial Peptide Database [44] (APD3, http://​aps.​unmc.​
edu/​AP) and Database of Anuran Defense Peptides [39]
(DADP, http://​split4.​pmfst.​hr/​dadp). Since APD3 is

Page 9 of 15

being frequently updated, we used a static version that
was scraped from the website on March 20, 2019 comprising 3061 sequences. Version 1.6 of DADP contains
1923 distinct mature AMPs. We concatenated these
two sets and removed duplicate sequences, producing
a non-redundant (positive) set of 4173 distinct, mature
AMP sequences, all 200 amino acid residues in length or
shorter. AMPs that are highly similar to each other at the
sequence level were kept as separate entries, since small
changes in amino acid compositions may lead to large
changes in AMP activity [45]. Also, it is important to
maintain as big a dataset as possible for better training of
a deep learning model [17].
Training and testing binary classification models
require a negative set, a collection of peptides known
not to have any antimicrobial activity. Since there are no
sequence catalogs for peptides devoid of antimicrobial
activity, studies in the field typically select their nonAMP sequences from UniProt [46] (https://​www.​unipr​
ot.​org). This may involve excluding several simple keywords (e.g. antimicrobial, antibiotic) to filter out potential AMPs [14, 15], or additionally removing all secretory
proteins [26] as AMPs are characteristically secreted
peptides [47]. The former proposition is not sufficiently
rigorous, because AMP annotation is not consistent and
varies between sources. While keyword filtering may
leave in the set some differently annotated AMPs, filtering of secretory proteins creates a learning gap for the
model regarding such proteins without antimicrobial
activities. Thus, it is important to balance these two strategies when selecting non-AMP sequences.
We designed a rigorous selection strategy for our
non-AMP sequences (Supplementary Fig. S3), using
sequences from the UniProtKB/Swiss-Prot database [46]
(2019_02 release), which only contains manually annotated and reviewed records from the UniProt database.
First, we downloaded sequences that are 200 amino acid
residues or shorter in length (matching the maximum
peptide length in the AMP set), excluding those with
annotations containing any of the 16 following keywords
related to antimicrobial activities: {antimicrobial, antibiotic, antibacterial, antiviral, antifungal, antimalarial,
antiparasitic, anti-protist, anticancer, defense, defensin,
cathelicidin, histatin, bacteriocin, microbicidal, fungicide}. Second, duplicates and sequences with residues
other than the 20 standard amino acids were removed.
Third, a set of potential AMP sequences annotated with
any of the 16 selected keywords were downloaded and
compared with our candidate negative set. We noted
instances where a sequence with multiple functions was
annotated separately in multiple records within the database, and removed sequences in common between candidate non-AMPs and potential AMPs. The candidate

Li et al. BMC Genomics

(2022) 23:77

non-AMP sequences were also checked against the positive set to remove AMP sequences that lack the annotation in UniProtKB/Swiss-Prot. Finally, 4173 sequences
were sampled from the remaining set of 128,445 nonAMPs, matching the number and length distribution of
sequences in the positive set. An exception to the length
distribution matching occurred when the length of a
particular AMP sequence did not have a perfect match
in the set of non-AMP sequences. In these instances, we
chose the non-AMP sequence with the closest length.
The matched length distributions were selected so that
the model did not learn to distinguish classes based on
sequence lengths.
The

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "RaCa-1", "db_measure": "Sequence analysis: APD analysis reveals this sequence is most similar (87.1%) to Palustrin-Ca GRAVY: 0.271; Mol form: C146H250N36O41S2; Mol Wt: 3242.926; molar extinction coefficient: 125. Activity: Active against Gram+ S.aureus ATCC 6538P (MIC>2560 ug/ml), S. pyogenes (MIC 79 ug/ml), Gram- P.aeruginosa ATCC 10148 (MIC>2560 ug/ml), E. coli ATCC 9723H or 25922 or MDR CPO-NDM (MIC 10-39 ug/ml). Updated 6/2024", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "APD6", "db_subject_text": "RaCa-2", "db_measure": "Sequence analysis: APD analysis reveals this sequence is most similar (75%) to Brevinin-1SPa GRAVY: 1.275; Mol form: C122H206N30O27S2; Mol Wt: 2589.289; molar extinction coefficient: 125. Activity: Active against Gram+ S. aureus ATCC 6538P (MIC 1-2/1-2 ug/ml), S. pyogenes (MIC 25-49 ug/ml), Gram- P. aeruginosa ATCC 10148 (MIC 20- >78/39 ug/ml), E. coli ATCC 9723H or ATCC 25922 or MDR (MIC 2-6 ug/ml). Updated 6/2024", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "APD6", "db_subject_text": "RaCa-3", "db_measure": "Sequence analysis: APD analysis reveals this sequence is most similar (74.19%) to Palustrin-2CE GRAVY: 0.103; Mol form: C147H252N37O41S2; Mol Wt: 3269.95; molar extinction coefficient: 5675. Activity: Active against Gram+ S-aureus ATCC 6538P (MIC >78 ug/ml), S. pyogenes (MIC 39 ug/ml), Gram- P. aeruginosa ATCC 10148 (MIC 20->78/39 ug/ml), E. coli ATCC 9723H (MIC 5-10 ug/ml), E. coli ATCC 25922 or MDR (MIC 2-10 ug/ml). Updated 6/2024", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "APD6", "db_subject_text": "RaCa-7", "db_measure": "Sequence analysis: APD analysis reveals this sequence is most similar (51.85%) to Brevinin-1Wa GRAVY: 0.527; Mol form: C140H219N31O32S1; Mol Wt: 2906.53; molar extinction coefficient: 1552.5. Activity: Active against Gram+ S-aureus ATCC 6538P (MIC>88 ug/ml), S.pyogenes (MIC>2560 ug/ml), Gram- P.aeruginosa ATCC 10148 (MIC>2560 ug/ml), E. coli ATCC 9723H or ATCC 25922 or MDR (MIC 6-44 ug/ml). Updated 6/2024", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Escherichia coli NDM", "db_measure": "MIC 19-39 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Escherichia coli NDM", "db_measure": "MBC 19-39 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 6538P", "db_measure": "MIC 1-3 µM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "APD6", "db_subject_text": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens", "db_measure": "literature DOI/PMID/PMCID link", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "APD6", "db_subject_text": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens", "db_measure": "literature DOI/PMID/PMCID link", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "APD6", "db_subject_text": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens", "db_measure": "literature DOI/PMID/PMCID link", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "APD6", "db_subject_text": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens", "db_measure": "literature DOI/PMID/PMCID link", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 6538P", "db_measure": "activity NA", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now.