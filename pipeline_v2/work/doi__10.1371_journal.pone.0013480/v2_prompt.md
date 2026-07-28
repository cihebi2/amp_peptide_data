
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
doi__10.1371_journal.pone.0013480

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Antimicrobial activity of rVpBD against Gram-positive and Gram-negative bacteria measured by liquid growth inhibition assay.", "footnotes": [], "header_rows": [["Tested microorganisms", "MIC value"], ["Gram-positive bacteria", ""]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Staphyloccocus aureus", "col_header": "MIC value", "value": "1.64–3.28 µM"}, {"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Micrococcus luteus", "col_header": "MIC value", "value": ">26.26 µM"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Bacillus sp.", "col_header": "MIC value", "value": "13.13–26.26 µM"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Vibrio anguillarum", "col_header": "MIC value", "value": "13.13–26.26 µM"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Entherobacter cloacae", "col_header": "MIC value", "value": ">26.26 µM"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Vibrio ichthyoenteri", "col_header": "MIC value", "value": "3.28–6.56 µM"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Pseudomonas putida", "col_header": "MIC value", "value": "1.64–3.28 µM"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "Proteus mirabilis", "col_header": "MIC value", "value": ">26.26 µM"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "Enterobacter sp.", "col_header": "MIC value", "value": "13.13–26.26 µM"}]}, {"table_index": 2, "label": "Table 2", "caption": "Primers used in the present study.", "footnotes": [], "header_rows": [["Primer", "Sequence (5′—3′)", "Sequence information"]], "longform_cells": [{"table_index": 2, "row_index": 2, "col_index": 2, "row_label": "P1(reverse)", "col_header": "Sequence (5′—3′)", "value": "ACCTCTACCACTAAGGCATCG"}, {"table_index": 2, "row_index": 2, "col_index": 3, "row_label": "P1(reverse)", "col_header": "Sequence information", "value": "5′ RACE primer"}, {"table_index": 2, "row_index": 3, "col_index": 2, "row_label": "P2(reverse)", "col_header": "Sequence (5′—3′)", "value": "CAAATAGCGAATGAGTTAGGAA"}, {"table_index": 2, "row_index": 3, "col_index": 3, "row_label": "P2(reverse)", "col_header": "Sequence information", "value": "5′ RACE primer"}, {"table_index": 2, "row_index": 4, "col_index": 2, "row_label": "P3(forward)", "col_header": "Sequence (5′—3′)", "value": "GCTGAATTGAAACTAATTTGACT"}, {"table_index": 2, "row_index": 4, "col_index": 3, "row_label": "P3(forward)", "col_header": "Sequence information", "value": "Full-length verified primer"}, {"table_index": 2, "row_index": 5, "col_index": 2, "row_label": "P4(reverse)", "col_header": "Sequence (5′—3′)", "value": "TTTTTTTTTTTTTTTTTTTTTT"}, {"table_index": 2, "row_index": 5, "col_index": 3, "row_label": "P4(reverse)", "col_header": "Sequence information", "value": "Full-length verified primer"}, {"table_index": 2, "row_index": 6, "col_index": 2, "row_label": "P5(forward)", "col_header": "Sequence (5′—3′)", "value": "CTGGTCGCCATGACGACTCTATC"}, {"table_index": 2, "row_index": 6, "col_index": 3, "row_label": "P5(forward)", "col_header": "Sequence information", "value": "Real time primer"}, {"table_index": 2, "row_index": 7, "col_index": 2, "row_label": "P6(reverse)", "col_header": "Sequence (5′—3′)", "value": "CGTTGTCGGGATGGTTCAAGTGC"}, {"table_index": 2, "row_index": 7, "col_index": 3, "row_label": "P6(reverse)", "col_header": "Sequence information", "value": "Real time primer"}, {"table_index": 2, "row_index": 8, "col_index": 2, "row_label": "P7(forward)", "col_header": "Sequence (5′—3′)", "value": "CTCCCTTGAGAAGAGCTACGA"}, {"table_index": 2, "row_index": 8, "col_index": 3, "row_label": "P7(forward)", "col_header": "Sequence information", "value": "Real time actin primer"}, {"table_index": 2, "row_index": 9, "col_index": 2, "row_label": "P8(reverse)", "col_header": "Sequence (5′—3′)", "value": "GATACCAGCAGATTCCATACCC"}, {"table_index": 2, "row_index": 9, "col_index": 3, "row_label": "P8(reverse)", "col_header": "Sequence information", "value": "Real time actin primer"}, {"table_index": 2, "row_index": 10, "col_index": 2, "row_label": "P9(forward)", "col_header": "Sequence (5′—3′)", "value": "CATATGCTGTGTCTGGACCAAAAGCC"}, {"table_index": 2, "row_index": 10, "col_index": 3, "row_label": "P9(forward)", "col_header": "Sequence information", "value": "Recombinant primer"}, {"table_index": 2, "row_index": 11, "col_index": 2, "row_label": "P10(reverse)", "col_header": "Sequence (5′—3′)", "value": "CTCGAGTTATGGTGGTGGTGGTGGTGGTGACGTCCTGTAATGTG"}, {"table_index": 2, "row_index": 11, "col_index": 3, "row_label": "P10(reverse)", "col_header": "Sequence information", "value": "Recombinant primer"}]}, {"table_index": 3, "label": "PDF p3 table2", "caption": "from paper.pdf", "footnotes": [], "header_rows": [["Testedmicroorganisms", "MICvalue"], ["Gram-positivebacteria", ""]], "longform_cells": [{"table_index": 3, "row_index": 3, "col_index": 2, "row_label": "Staphyloccocusaureus", "col_header": "MICvalue", "value": "1.64–3.28mM"}, {"table_index": 3, "row_index": 4, "col_index": 2, "row_label": "Micrococcusluteus", "col_header": "MICvalue", "value": ".26.26mM"}, {"table_index": 3, "row_index": 5, "col_index": 2, "row_label": "Bacillussp.", "col_header": "MICvalue", "value": "13.13–26.26mM"}, {"table_index": 3, "row_index": 7, "col_index": 2, "row_label": "Vibrioanguillarum", "col_header": "MICvalue", "value": "13.13–26.26mM"}, {"table_index": 3, "row_index": 8, "col_index": 2, "row_label": "Entherobactercloacae", "col_header": "MICvalue", "value": ".26.26mM"}, {"table_index": 3, "row_index": 9, "col_index": 2, "row_label": "Vibrioichthyoenteri", "col_header": "MICvalue", "value": "3.28–6.56mM"}, {"table_index": 3, "row_index": 10, "col_index": 2, "row_label": "Pseudomonasputida", "col_header": "MICvalue", "value": "1.64–3.28mM"}, {"table_index": 3, "row_index": 11, "col_index": 2, "row_label": "Proteusmirabilis", "col_header": "MICvalue", "value": ".26.26mM"}, {"table_index": 3, "row_index": 12, "col_index": 2, "row_label": "Enterobactersp.", "col_header": "MICvalue", "value": "13.13–26.26mM"}]}, {"table_index": 4, "label": "PDF p5 table2", "caption": "from paper.pdf", "footnotes": [], "header_rows": [["Primer", "Sequence(59—39)", "Sequenceinformation"]], "longform_cells": [{"table_index": 4, "row_index": 2, "col_index": 2, "row_label": "P1(reverse)", "col_header": "Sequence(59—39)", "value": "ACCTCTACCACTAAGGCATCG"}, {"table_index": 4, "row_index": 2, "col_index": 3, "row_label": "P1(reverse)", "col_header": "Sequenceinformation", "value": "59RACEprimer"}, {"table_index": 4, "row_index": 3, "col_index": 2, "row_label": "P2(reverse)", "col_header": "Sequence(59—39)", "value": "CAAATAGCGAATGAGTTAGGAA"}, {"table_index": 4, "row_index": 3, "col_index": 3, "row_label": "P2(reverse)", "col_header": "Sequenceinformation", "value": "59RACEprimer"}, {"table_index": 4, "row_index": 4, "col_index": 2, "row_label": "P3(forward)", "col_header": "Sequence(59—39)", "value": "GCTGAATTGAAACTAATTTGACT"}, {"table_index": 4, "row_index": 4, "col_index": 3, "row_label": "P3(forward)", "col_header": "Sequenceinformation", "value": "Full-lengthverifiedprimer"}, {"table_index": 4, "row_index": 5, "col_index": 2, "row_label": "P4(reverse)", "col_header": "Sequence(59—39)", "value": "TTTTTTTTTTTTTTTTTTTTTT"}, {"table_index": 4, "row_index": 5, "col_index": 3, "row_label": "P4(reverse)", "col_header": "Sequenceinformation", "value": "Full-lengthverifiedprimer"}, {"table_index": 4, "row_index": 6, "col_index": 2, "row_label": "P5(forward)", "col_header": "Sequence(59—39)", "value": "CTGGTCGCCATGACGACTCTATC"}, {"table_index": 4, "row_index": 6, "col_index": 3, "row_label": "P5(forward)", "col_header": "Sequenceinformation", "value": "Realtimeprimer"}, {"table_index": 4, "row_index": 7, "col_index": 2, "row_label": "P6(reverse)", "col_header": "Sequence(59—39)", "value": "CGTTGTCGGGATGGTTCAAGTGC"}, {"table_index": 4, "row_index": 7, "col_index": 3, "row_label": "P6(reverse)", "col_header": "Sequenceinformation", "value": "Realtimeprimer"}, {"table_index": 4, "row_index": 8, "col_index": 2, "row_label": "P7(forward)", "col_header": "Sequence(59—39)", "value": "CTCCCTTGAGAAGAGCTACGA"}, {"table_index": 4, "row_index": 8, "col_index": 3, "row_label": "P7(forward)", "col_header": "Sequenceinformation", "value": "Realtimeactinprimer"}, {"table_index": 4, "row_index": 9, "col_index": 2, "row_label": "P8(reverse)", "col_header": "Sequence(59—39)", "value": "GATACCAGCAGATTCCATACCC"}, {"table_index": 4, "row_index": 9, "col_index": 3, "row_label": "P8(reverse)", "col_header": "Sequenceinformation", "value": "Realtimeactinprimer"}, {"table_index": 4, "row_index": 10, "col_index": 2, "row_label": "P9(forward)", "col_header": "Sequence(59—39)", "value": "CATATGCTGTGTCTGGACCAAAAGCC"}, {"table_index": 4, "row_index": 10, "col_index": 3, "row_label": "P9(forward)", "col_header": "Sequenceinformation", "value": "Recombinantprimer"}, {"table_index": 4, "row_index": 11, "col_index": 2, "row_label": "P10(reverse)", "col_header": "Sequence(59—39)", "value": "CTCGAGTTATGGTGGTGGTGGTGGTGGTGACGTCCTGTAATGTG"}, {"table_index": 4, "row_index": 11, "col_index": 3, "row_label": "P10(reverse)", "col_header": "Sequenceinformation", "value": "Recombinantprimer"}]}, {"table_index": 5, "label": "PDF p3 table2", "caption": "from pone.0013480.pdf", "footnotes": [], "header_rows": [["Testedmicroorganisms", "MICvalue"], ["Gram-positivebacteria", ""]], "longform_cells": [{"table_index": 5, "row_index": 3, "col_index": 2, "row_label": "Staphyloccocusaureus", "col_header": "MICvalue", "value": "1.64–3.28mM"}, {"table_index": 5, "row_index": 4, "col_index": 2, "row_label": "Micrococcusluteus", "col_header": "MICvalue", "value": ".26.26mM"}, {"table_index": 5, "row_index": 5, "col_index": 2, "row_label": "Bacillussp.", "col_header": "MICvalue", "value": "13.13–26.26mM"}, {"table_index": 5, "row_index": 7, "col_index": 2, "row_label": "Vibrioanguillarum", "col_header": "MICvalue", "value": "13.13–26.26mM"}, {"table_index": 5, "row_index": 8, "col_index": 2, "row_label": "Entherobactercloacae", "col_header": "MICvalue", "value": ".26.26mM"}, {"table_index": 5, "row_index": 9, "col_index": 2, "row_label": "Vibrioichthyoenteri", "col_header": "MICvalue", "value": "3.28–6.56mM"}, {"table_index": 5, "row_index": 10, "col_index": 2, "row_label": "Pseudomonasputida", "col_header": "MICvalue", "value": "1.64–3.28mM"}, {"table_index": 5, "row_index": 11, "col_index": 2, "row_label": "Proteusmirabilis", "col_header": "MICvalue", "value": ".26.26mM"}, {"table_index": 5, "row_index": 12, "col_index": 2, "row_label": "Enterobactersp.", "col_header": "MICvalue", "value": "13.13–26.26mM"}]}, {"table_index": 6, "label": "PDF p5 table2", "caption": "from pone.0013480.pdf", "footnotes": [], "header_rows": [["Primer", "Sequence(59—39)", "Sequenceinformation"]], "longform_cells": [{"table_index": 6, "row_index": 2, "col_index": 2, "row_label": "P1(reverse)", "col_header": "Sequence(59—39)", "value": "ACCTCTACCACTAAGGCATCG"}, {"table_index": 6, "row_index": 2, "col_index": 3, "row_label": "P1(reverse)", "col_header": "Sequenceinformation", "value": "59RACEprimer"}, {"table_index": 6, "row_index": 3, "col_index": 2, "row_label": "P2(reverse)", "col_header": "Sequence(59—39)", "value": "CAAATAGCGAATGAGTTAGGAA"}, {"table_index": 6, "row_index": 3, "col_index": 3, "row_label": "P2(reverse)", "col_header": "Sequenceinformation", "value": "59RACEprimer"}, {"table_index": 6, "row_index": 4, "col_index": 2, "row_label": "P3(forward)", "col_header": "Sequence(59—39)", "value": "GCTGAATTGAAACTAATTTGACT"}, {"table_index": 6, "row_index": 4, "col_index": 3, "row_label": "P3(forward)", "col_header": "Sequenceinformation", "value": "Full-lengthverifiedprimer"}, {"table_index": 6, "row_index": 5, "col_index": 2, "row_label": "P4(reverse)", "col_header": "Sequence(59—39)", "value": "TTTTTTTTTTTTTTTTTTTTTT"}, {"table_index": 6, "row_index": 5, "col_index": 3, "row_label": "P4(reverse)", "col_header": "Sequenceinformation", "value": "Full-lengthverifiedprimer"}, {"table_index": 6, "row_index": 6, "col_index": 2, "row_label": "P5(forward)", "col_header": "Sequence(59—39)", "value": "CTGGTCGCCATGACGACTCTATC"}, {"table_index": 6, "row_index": 6, "col_index": 3, "row_label": "P5(forward)", "col_header": "Sequenceinformation", "value": "Realtimeprimer"}, {"table_index": 6, "row_index": 7, "col_index": 2, "row_label": "P6(reverse)", "col_header": "Sequence(59—39)", "value": "CGTTGTCGGGATGGTTCAAGTGC"}, {"table_index": 6, "row_index": 7, "col_index": 3, "row_label": "P6(reverse)", "col_header": "Sequenceinformation", "value": "Realtimeprimer"}, {"table_index": 6, "row_index": 8, "col_index": 2, "row_label": "P7(forward)", "col_header": "Sequence(59—39)", "value": "CTCCCTTGAGAAGAGCTACGA"}, {"table_index": 6, "row_index": 8, "col_index": 3, "row_label": "P7(forward)", "col_header": "Sequenceinformation", "value": "Realtimeactinprimer"}, {"table_index": 6, "row_index": 9, "col_index": 2, "row_label": "P8(reverse)", "col_header": "Sequence(59—39)", "value": "GATACCAGCAGATTCCATACCC"}, {"table_index": 6, "row_index": 9, "col_index": 3, "row_label": "P8(reverse)", "col_header": "Sequenceinformation", "value": "Realtimeactinprimer"}, {"table_index": 6, "row_index": 10, "col_index": 2, "row_label": "P9(forward)", "col_header": "Sequence(59—39)", "value": "CATATGCTGTGTCTGGACCAAAAGCC"}, {"table_index": 6, "row_index": 10, "col_index": 3, "row_label": "P9(forward)", "col_header": "Sequenceinformation", "value": "Recombinantprimer"}, {"table_index": 6, "row_index": 11, "col_index": 2, "row_label": "P10(reverse)", "col_header": "Sequence(59—39)", "value": "CTCGAGTTATGGTGGTGGTGGTGGTGGTGACGTCCTGTAATGTG"}, {"table_index": 6, "row_index": 11, "col_index": 3, "row_label": "P10(reverse)", "col_header": "Sequenceinformation", "value": "Recombinantprimer"}]}]

=== PRIMARY PAPER FULL TEXT (context only) ===
Use this ONLY to (a) confirm whether an organism/target/assay was tested in this paper (prevents false 'absent' calls), and (b) read an endpoint label. You may NOT cite full text as the `evidence` cell for is_database_error=true; that still requires a structured longform cell.
Molecular Characterization of a Novel Big Defensin from
Clam Venerupis philippinarum
Jianmin Zhao1, Chenghua Li1,2*, Aiqin Chen1, Lingyun Li3, Xiurong Su2, Taiwu Li2
1 Yantai Institute of Coastal Zone Research, Chinese Academy of Sciences, Yantai, China, 2 Faculty of Life Science and Biotechnology, Ningbo University, Ningbo, China,
3 College of Animal Science and Technology, Northeast Agriculture University, Harbin, China

Abstract
Antimicrobial peptides (AMPs) are important mediators of the primary defense mechanism against microbial invasion. In the
present study, a big defensin was identified from Venerupis philippinarum haemocytes (denoted as VpBD) by RACE and EST
approaches. The VpBD cDNA contained an open reading frame (ORF) of 285 bp encoding a polypeptide of 94 amino acids.
The deduce amino acid sequence of VpBD shared the common features of big defensin including disulfide array
organization and helix structure, indicating that VpBD should be a new member of the big defensin family. The mRNA
transcript of VpBD was up-regulated significantly during the first 24 hr after Vibrio anguillarum challenge, which was 7.4-fold
increase compared to that of the control group. Then the expression decreased gradually from 24 hr to 96 hr, and the
lowest expression level was detected at 96 hr post-infection, which was still 3.9-fold higher than that of control. The mature
peptide of VpBD was recombined in Escherichia coli and purified for minimum inhibitory concentration (MIC) determination.
The rVpBD displayed broad-spectrum inhibitory activity towards all tested bacteria with the highest activity against
Staphyloccocus aureus and Pseudomonas putida. These results indicated that VpBD was involved in the host immune
response against bacterial infection and might contribute to the clearance of invading bacteria.
Citation: Zhao J, Li C, Chen A, Li L, Su X, et al. (2010) Molecular Characterization of a Novel Big Defensin from Clam Venerupis philippinarum. PLoS ONE 5(10):
e13480. doi:10.1371/journal.pone.0013480
Editor: Richard Cordaux, University of Poitiers, France
Received June 30, 2010; Accepted September 10, 2010; Published October 20, 2010
Copyright: ß 2010 Zhao et al. This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits
unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.
Funding: The project was supported by Chinese Academy of Sciences Innovation Program (kzcx2-yw-225) and NSFC grant (No. 30901115). The funders had no
role in study design, data collection and analysis, decision to publish, or preparation of the manuscript.
Competing Interests: The authors have declared that no competing interests exist.
* E-mail: chli@yic.ac.cn

from bay scallop Argopecten irradians. The recombinant AiBD could
inhibit the growth of both Gram-positive and Gram-negative
bacteria, and also showed strong fungicidal activity towards yeast
[15]. However, little information is available about the molecular
features and immune response against pathogen infection in the
commercially cultured clam Venerupis philippinarum. The main
objectives of the present study are to: (1) clone the full-length cDNA
of big defensin from V. philippinarum (VpBD); (2) investigate the
expression profile of VpBD post infection of Vibrio pathogen; (3)
elucidate the antibacterial activity of the recombinant VpBD in vitro.

Introduction
The Manila clam, Venerupis philippinarum, is an important marine
bivalve for commercial fisheries, accounting for about 80% of
mudflat fishery production in China (China Bureau of Fisheries,
2004). In the last decades, clam culture in China is sustaining a
severe mortality problem, and suffering great economic losses [1].
Although positive results have come from treatment of antibiotics,
increasing concerns of antibiotics use have prompted interests in
developing alternative strategies for growth and health management
[2,3,4]. The gene-encoded cationic antimicrobial peptides (AMPs)
are major humoral components of the innate defense systems [5,6],
which were considered as promising therapeutic candidates for their
innate advantages of less bacterial resistance and very specific
targets [3]. Moreover, the discovery of antimicrobial peptides
provides new clues for a fundamental understanding of the species
immunity response and for further establishment of disease control
in the practice of aquaculture industry.
As cationic and amphiphilic molecules, AMPs showed attractive
perspective as substitutes for antibiotics in aquaculture for their
biochemical diversity, broad specificity against bacteria, fungi or
even virus [6,7,8,9,10,11,12]. In mollusk, the presence of lower
molecular mass AMPs started to be investigated from last decade
[13]. To date, approximately 20 AMPs have been isolated or
cloned from mollusks, mainly from mussels (for review see [14]).
Big defensin is one of the AMPs which possess remarkable
microbicidal activity against Gram-positive, Gram-negative bacteria
and fungi. Until now, only one molluscan big defensin was identified
PLoS ONE | www.plosone.org

Results
cDNA cloning and sequence analysis of VpBD
A 640 bp fragment representing the complete cDNA of VpBD
was obtained by 59RACE from a cDNA library of V. philippinarum.
The sequence was deposited in GenBank under accession
no. HM562672. The deduced amino acid sequence of VpBD
was shown in Fig. 1. The complete sequence of VpBD cDNA
contained a 59 untranslated region (UTR) of 126 bp, a 39 UTR of
229 bp with a canonical polyA tail, and an open reading frame
(ORF) of 285 bp encoded a polypeptide of 94 amino acids with the
predicted molecular weight of 11.35 kDa and the theoretical
isoelectric point of 9.46. The putative signal peptide was identified
at the N-terminal sequence with the cleavage site at amino acid
position 20. The mature peptide was analyzed using the
antimicrobial peptide predictor program (http://aps.unmc.edu/
AP/prediction/prediction_main.php). The results showed that
1

October 2010 | Volume 5 | Issue 10 | e13480

A Novel Big Defensin from Clam

similarities were found between VpBD and other counterparts
(14% –20%). The consensus pattern C-X6-C-X3-C-X13(14)-CX4-C-C in defensin domain was relatively conserved as typically
observed in big defensin from horseshoe crab and bay scallop
(Fig. 2). The disulfide array in VpBD was postulated to be identical
to that of big defensin from horseshoe crab (C1–C5, C2–C4, and
C3–C6).

The expression profile of VpBD after Vibrio challenge
The temporal mRNA expression of VpBD in the haemocytes
post-Vibrio challenge was shown in Fig. 3. During the first 24 hr
after pathogen challenge, the expression level of VpBD mRNA
was obviously up-regulated and reached 7.4-fold compared to that
of control group. After that, the expression level was decreased
gradually from 24 hr to 96 hr, and the lowest expression level was
detected at 96 hr post-bacterial infection, which was 3.9-fold
higher than that of control group. Significant differences of the
expression level of VpBD were observed at 6 hr (P,0.01), 12 hr
(P,0.05), 24 hr (P,0.01), 48 hr (P,0.05), 72 hr (P,0.05) and
96 hr (P,0.05) post the challenge of Vibrio compared to the
control group.

Characterization of recombinant peptide by
electrophoresis
The recombinant plasmid pET-21a-VpBD was transformed
and expressed in E. coli BL21(DE3)-pLysS. After IPTG
induction for 3 h, the whole cell lysate analyzed by SDS-PAGE
revealed a distinct band with a molecular weight of 9.75 kDa
(Fig. 4 lane B), which was further purified to homogeneity by
HiTrap Chelating Columns (Fig. 4 lane C). Total of 0.9 mg
purified protein was yield from 50 ml bacterial culture in the
end.

Figure 1. The nucleotide sequence (above) and its deduced
amino acid sequence (below) of VpBD. Nucleotides were
numbered from the first base at the 59end. The signal peptide was
underlined. The asterisk indicated the stop codon.
doi:10.1371/journal.pone.0013480.g001

MIC assay of the rVpBD
VpBD possessed characteristic features of AMPs including helix
structure formation, a net positive charge (+5) and a high
percentage of hydrophobic residues (36%).

The spectrum of antimicrobial activity of the purified rVpBD
was investigated against several Gram-positive and Gram-negative
bacteria. The rVpBD could inhibit the growth of all tested
microorganisms (Table 1), indicating that rVpBD was a broadspectrum antibacterial peptide. The highest activity was found
against Staphyloccocus aureus and Pseudomonas with the MIC of 1.64–
3.28 mM.

Homology analysis of VpBD
The deduced amino acid sequence of VpBD was aligned with
other known big defensins by CLUSTALW program and low

Figure 2. Multiple alignment of VpBD with other known big defensins. Identical amino acids were in white letters with black background,
and gray background indicated high levels of amino acid similarity.
doi:10.1371/journal.pone.0013480.g002

PLoS ONE | www.plosone.org

2

October 2010 | Volume 5 | Issue 10 | e13480

A Novel Big Defensin from Clam

Figure 3. Time-course expression level of VpBD transcript in haemocytes after Vibrio anguillarum infection measured by quantitative
real-time PCR at 0 hr, 6 hr, 12 hr, 24 hr, 48 hr, 72 hr and 96 hr. Each symbol and vertical bar represented the mean 6 S.D (n = 5). Significant
differences between challenged group and control group were indicated by an asterisk (P,0.05) and two asterisks (P,0.01), respectively.
doi:10.1371/journal.pone.0013480.g003

Discussion
Living in an aquatic environment rich in microorganisms,
mollusk has developed effective systems to eliminate noxious
microorganisms [16]. However, knowledge advance on the
function, expression and regulation of immune effectors in
mollusk, especially for AMPs, are still deficient compared with
those of insects and vertebrates. In the present study, the cDNA
encoding a potential big defensin was identified from V.
philippinarum (denoted as VpBD). The deduced amino acid of
VpBD shared common features of AMPs, such as a-helical
structure, net positive charge and high hydrophobic residue ratio.
The arrangement of cysteine residues, their neighboring amino
acid residues and the spacing between cysteine residues are
conserved to previously identified homologues [15,17], which
further indicated that VpBD was a new member of the big
defensin family. However, unlike other known big defensin
sequences, no prepropeptide sequence was identified from the
deduced amino acid of VpBD. The hydrophobic region
Table 1. Antimicrobial activity of rVpBD against Grampositive and Gram-negative bacteria measured by liquid
growth inhibition assay.

Tested microorganisms

MIC value

Gram-positive bacteria
Staphyloccocus aureus

1.64–3.28 mM

Micrococcus luteus

.26.26 mM

Bacillus sp.

13.13–26.26 mM

Gram-negative bacteria

Figure 4. SDS-PAGE analysis of recombinant VpBD. After
electrophoresis, the gel was visualized by Coomassie brilliant blue
R250 staining. Lane M: protein molecular standard; lane A: negative
control for rVpBD (without induction); lane B: induced expression of
rVpBD; lane C: purified rVpBD.
doi:10.1371/journal.pone.0013480.g004

PLoS ONE | www.plosone.org

Vibrio anguillarum

13.13–26.26 mM

Entherobacter cloacae

.26.26 mM

Vibrio ichthyoenteri

3.28–6.56 mM

Pseudomonas putida

1.64–3.28 mM

Proteus mirabilis

.26.26 mM

Enterobacter sp.

13.13–26.26 mM

doi:10.1371/journal.pone.0013480.t001

3

October 2010 | Volume 5 | Issue 10 | e13480

A Novel Big Defensin from Clam

GAAAVT(A)AA at N-terminus of other counterparts was also
absent from VpBD. The above differences and the lower
homology between VpBD and other big defensins collectively
indicated that VpBD should be a novel big defensin.
Generally, AMPs could be induced by physical stresses and
infectious pathogens. The transcript of big defensin from scallop
was up-regulated after V. anguillarum challenge with a 131.1-fold
increase at 32 h compared to the control group [15]. Similar
expression pattern was also observed in abalone defensin when
received Vibrios infection [18]. In contrast, significant decrease of
AMPs mRNA expression after Vibrio challenge was observed in
crustin, mytilin B and penaeidin, respectively [19,20,21,22,23]. In
the present study, the expression level of VpBD mRNA was
obviously up-regulated post bacterial challenge, and the peak
expression level was detected at 24 hr with a 7.4-fold increase
compared with that of control group. The recruitment of VpBDproducing haemocytes into circulating system probably contributed to the drastic increase of VpBD transcript in the early stage of
bacterial challenge. After that, the expression level gradually
down-regulated, and the lowest expression level was detected at
96 hr post-infection, which was still 3.9-fold higher than the
control group. It was postulated that the decreased expression of
VpBD was related to the progressive clearance of the invasive
pathogens. All these results indicated that VpBD was one of the
acute phase proteins involved in the elimination of invasive
pathogens.
It is important to understand the microbicidal activities of
VpBD in vitro. In the present study, the mature peptide of VpBD
was expressed in E. coli BL21(DE3)-pLysS, and the purified
rVpBD exhibited broad-spectrum bactericidal activity towards
various bacteria, which was almost consistent with recombinant
big defensin from scallop [15] and native protein from horseshoe
crab [17]. The same potency and inhibitory effect on growth of
Gram-negative (P. putida) and Gram-positive bacteria (S. aureus)
was also detected for VpBD as big defensin from horseshoe crab
[17]. Compared to other molluscan AMPs, the inhibitory activity
of VpBD was similar or even more efficient. The MIC of mytilin A
towards different bacteria ranged from 0.6 mM to 10 mM
[20,24], while the recombinant defensin from Crassostrea gigas
showed inhibitory activity towards tested microorganism at mM
level [25]. The potent antimicrobial activities of VpBD made it
valuable to control outbreak of pathogenic microorganisms in
clam culture.

cDNA library construction and EST analysis

Materials and Methods

The expression of VpBD transcript in haemocytes after Vibrio
challenge was measured by quantitative real time RT-PCR in
Applied Biosystem 7500 fast Real-time PCR System. Gene-specific
primers P5 and P6 (Table 2) were designed to amplify a PCR
product of 101 bp. The product was purified and sequenced to
verify the PCR specificity. Two clam b-actin primers, P7 and P8
(Table 2) were used to amplify a 121 bp fragment as internal control
to verify the successful reverse transcription and to calibrate the
cDNA template. The reaction component, thermal profile, and the
data analysis were conducted as previously described [26]. All data
were given in terms of relative mRNA expression as means 6 S.E.
The results were subjected to One-way Analysis of Variance
(ANOVA) to determine differences in the mean values among the
treatments. Significance was concluded at P,0.05. Statistical
analysis was performed using SPSS 11.5 for Windows.

One clam was randomly selected for cDNA library construction at
8 hr post V. anguillarum challenge. The cDNA library was constructed
using the ZAP-cDNA synthesis kit and ZAP-cDNA GigapackIII
Gold cloning kit (Stratagene). Random sequencing of the library
using T3 primer yielded 3226 successful sequencing reactions.
BLAST analysis of all the 3226 EST sequences revealed that one
EST of 387 bp was highly similar to the previously identified big
defensins. Therefore, the EST sequence was selected for further
cloning of the full-length cDNA of big defensin from V. philippinarum.

RNA isolation and cDNA synthesis
Total RNA was isolated from the haemocytes of clams using the
TRIzol reagent (Invitrogen). First-strand cDNA synthesis was
performed according to Promega M-MLV RT Usage information
with the RQ1 RNase-Free DNase (Promega)-treated total RNA
(1 mg) as template and oligo (dT) primer. The reactions were
incubated at 42uC for 1 hr, terminated by heating at 95uC for
5 min. For 59 RACE, terminal deoxynucleotidyl transferase
(Takara) was used to add homopolymer dCTP tails to the 3’
end of the purified first-strand cDNA.

Cloning of the full-length cDNA of VpBD by 59RACE
Gene-specific primers, P1 and P2 (Table 2), were designed
based on the EST to clone the full-sequence cDNA of VpBD.
Semi-nested PCR approaches were employed to get the 59end of
VpBD with 1:50 dilution of the first round PCR products as
templates and oligodG as anchored primer. The PCR programs
and PCR product sequencing were performed according to
previously described [26]. The validity of VpBD cDNA was
further verified with primer sets of P3 and P4.

Sequence analysis of VpBD
The VpBD sequence was analyzed using the BLAST algorithm
at NCBI web site (http://www.ncbi.nlm.nih.gov/blast), and the
deduced amino acid sequence was analyzed with the Expert Protein
Analysis System (http://www.expasy.org/). Sequence alignment of
VpBD was performed with the ClustalW Multiple Alignment
program (http://www.ebi.ac.uk/clustalw/) and Multiple Alignment show program (http://www.biosoft.net/sms/index.html).

mRNA expression profile of VpBD post V. anguillarum
challenge

Clams and bacterial challenge
The clams V. philippinarum (7.5–11 g in weight) were purchased
from a local market and acclimated for a week before
commencement of the experiment. The temperature was held at
20–22uC throughout the whole experiment. The salinity for the
supplied seawater was kept at 30%. For the bacterial challenge
experiment, the clams were randomly divided into six flatbottomed rectangular tanks with 50 liter capacity, each containing
50 clams. One tank served as control, while the other five tanks
were immersed with high density of V. anguillarum with a final
concentration of 107CFU mL21. The infected clams were
randomly sampled at 6 hr, 12 hr, 24 hr, 48 hr, 72 hr and 96 hr,
respectively. The clams cultured in the normal seawater were used
as control group. The haemolymphs from the control and the
treated groups were collected using a syringe individually and
centrifuged at 20006g, 4uC for 10 min to harvest the haemocytes.
There were five replicates for each treatment and the control
group.
PLoS ONE | www.plosone.org

Recombinant expression of VpBD and protein
purification
PCR fragment encoding the mature peptide of VpBD was
amplified with gene-specific primers P9 and P10 with Nde I and
4

October 2010 | Volume 5 | Issue 10 | e13480

A Novel Big Defensin from Clam

Table 2. Primers used in the present study.

Primer

Sequence (59—39)

Sequence information

P1(reverse)

ACCTCTACCACTAAGGCATCG

59 RACE primer

P2(reverse)

CAAATAGCGAATGAGTTAGGAA

59 RACE primer

P3(forward)

GCTGAATTGAAACTAATTTGACT

Full-length verified primer

P4(reverse)

TTTTTTTTTTTTTTTTTTTTTT

Full-length verified primer

P5(forward)

CTGGTCGCCATGACGACTCTATC

Real time primer

P6(reverse)

CGTTGTCGGGATGGTTCAAGTGC

Real time primer

P7(forward)

CTCCCTTGAGAAGAGCTACGA

Real time actin primer

P8(reverse)

GATACCAGCAGATTCCATACCC

Real time actin primer

P9(forward)

CATATGCTGTGTCTGGACCAAAAGCC

Recombinant primer

P10(reverse)

CTCGAGTTATGGTGGTGGTGGTGGTGGTGACGTCCTGTAATGTG

Recombinant primer

doi:10.1371/journal.pone.0013480.t002

Xho I sites at their 59 end, respectively (Table 2). The PCR
product was cloned into pMD18-T simple vector (Takara),
digested completely by restriction enzymes Nde I and Xho I
(NEB), and then subcloned into the Nde I/Xho I sites of
expression vector pET-21a(+) (Novagen). The recombinant
plasmid (pET-21a-VpBD) was transformed into Escherichia coli
BL21 (DE3)-plysS (Novagen) and subjected to DNA sequencing.
After sequencing to ensure in-frame insertion, positive clones were
incubated in SOB medium (containing 50 mg/L ampicillin) at
37uC with shaking at 220 rpm. When the culture reached OD600
of 0.6, IPTG with final concentration of 1 mmol/L was added to
the culture, and incubated for additional 3 hr under the same
conditions. Cells were harvested by centrifugation at 10,000 g for
2 min, and suspended in 50 mM Tris containing 5 mM EDTA,
50 mM NaCl, and 5% Glycerol (pH 7.9). After being sonicated at
4uC for 60 min, the rVpBD was purified by HisTrap Chelating
Columns (Amersham Biosciences) according to the manufacturer’s
instruction. The purified protein was subjected to 15% SDSPAGE according to the method of Laemmli [27]. The
concentration of rVpBD was measured by BCA Protein Assay Kit.

Antimicrobial activity of rVpBD
Antibacterial testing was carried out using three Gram-positive
bacteria (Staphyloccocus aureus, Micrococcus luteus and Bacillus sp) and
six Gram-negative bacteria (Vibrio anguillarum, Entherobacter cloacae,
Pseudomonas putida, Proteus mirabilis, Vibrio ichthyoenteri and Enterobacter
sp.). The MIC was determined according to the method of
Hancock (http://cmdr.ubc.ca/bobh/methods/). The assay was
done with triplicates in three independent experiments. The MIC
value was recorded as the range between the highest concentration
of the protein where bacterial growth was observed and the lowest
concentration that caused 100% inhibition of bacteria growth.

Author Contributions
Conceived and designed the experiments: JZ CL. Performed the
experiments: JZ AC LL. Analyzed the data: JZ CL. Contributed
reagents/materials/analysis tools: XS TL. Wrote the paper: CL.

References
1. Zhang G, Li X, Xue Z (1999) Potential reasons and controlling strategies of
mollusk dramatic death in China. Chinese fishery 9: 34–39.
2. Handcock REW, Chapple DS (1999) Peptide antibiotics. Antimicrob Agents
Chemother 43: 1317–1323.
3. Jenssen H, Hamill P, Hancock REW (2006) Peptide antimicrobial agents. Clin
Microbiol Rev 19: 491–511.
4. Bachère E, Gueguen Y, Gonzalez M, Lorgeril J, Garnier J, et al. (2004) Insights
into the anti-microbial defense of marine invertebrates: the penaeid shrimps and
the oyster Crassostrea gigas. Immunol Rev 198: 149–168.
5. Hancock REW, Diamond G (2000) The role of cationic antimicrobial peptides
in innate host defences. Trends Microbiol 8: 402–410.
6. Zasloff M (2002) Antimicrobial peptides of multicellular organisms. Nature 415:
389–395.
7. Terras FRG, Torrekens S, van Leuven F, Osborn RW, Vanderleyden J, et al.
(1993) A new family of basic cysteine-rich plant antifungal proteins from
Brassicaceae species. FEBS Lett 316: 233–240.
8. Mor A, Nicolas P (1994) Isolation and structure of novel defensive peptides from
frog skin. J Biochem 219: 145–154.
9. Casteels-Josson K, Zhang W, Capaci T, Casteels P, Tempst P (1994) Acute
transcriptional response of the honeybee peptideantibiotics gene repertoire and
required post-translational conversion of the precursor structures. J Biol Chem
269: 28569–28575.
10. Storici P, Tossi A, Lenarcic B, Romeo D (1996) Purification and structural
characterization of bovine cathelicidins, precursors of antimicrobial peptides.
J Biochem 238: 769–776.
11. Sitaram N, Nagaraj R (2002) Host-defense antimicrobial peptides: importance of
structure for activity. Curr Pharm Design 8: 727–742.
12. Liu H, Jiravanichpaisal P, Söderhäll I, Cerenius L, Söderhäll K (2006)
Antilipopolysaccharide factor interferes with white spot syndrome virus

PLoS ONE | www.plosone.org

13.
14.

15.

16.

17.

18.

19.

20.

21.

5

replication in vitro and in vivo in the crayfish Pacifastacus leniusculus. J Virol 80:
10365–10371.
Hubert F, Noel T, Roch P (1996) A member of the arthropod defensin family from
edible Mediterranean mussels (Mytilus galloprovincialis). J Biochem 240: 302–306.
Li C, Song L, Zhao J (2009) A review of advances in research on marine
molluscan antimicrobial peptides and their potential application in aquaculture.
Molluscan Res 29: 17–26.
Zhao J, Song L, Li C, Ni D, Wu L, et al. (2007) Molecular cloning, expression of
a big defensin gene from bay scallop Argopecten irradians and the antimicrobial
activity of its recombinant protein. Mol Immunol 44: 360–368.
Destoumieux D, Bulet P, Loew D, Van Dorsselaer A, Rodriguez J, et al. (1997)
Penaeidins, a new family of antimicrobial peptides isolated from the shrimp
Penaeus vannamei (Decapoda). J Biol Chem 272: 28398–28406.
Saito T, Kawabata S, Shigenaga T, Takayenoki Y, Cho J, et al. (1995) A novel
big defensin identified in horseshoe crab hemocytes: isolation, amino acid
sequence and antibacterial activity. J Biochem 117: 1131–1137.
De Zoysa M, Whang I, Youngdeuk L, Sukkyoung L, Lee J-S, et al. (2010)
Defensin from disk abalone Haliotis discus discus: Molecular cloning, sequence
characterization and immune response against bacterial infection. Fish Shellfish
Immunol 28: 261–266.
Destoumieux D, Munoz M, Cosseau C, Rodriguez J, Bulet P, et al. (2000) Penaeidins,
antimicrobial peptides with chitin-binding activity, are produced and stored in shrimp
granulocytes and released after microbial challenge. J Cell Sci 113: 461–469.
Mitta G, Hubert F, Dyrynda E, Boudry P, Roch P (2000) Mytilin B and MGD2,
two antimicrobial peptides of marine mussels: gene structure and expression
analysis. Dev Comp Immunol 24: 381–393.
Muñoz M, Vandenbulcke F, Saulnier D, Bachère E (2002) Expression and
distribution of penaeidin antimicrobial peptides are regulated by haemocyte
reactions in microbial challenged shrimp. J Biochem 269: 2678–2689.

October 2010 | Volume 5 | Issue 10 | e13480

A Novel Big Defensin from Clam

22. Supungul P, Klinbunga S, Pichyangkura R, Hirono I, Aoki T, et al. (2004)
Antimicrobial peptides discovered in the black tiger shrimp Penaeus monodon using
the EST approach. Dis Aquat Organ 61: 123–135.
23. Mu C, Zheng P, Zhao J, Wang L, Zhang H, et al. (2010) Molecular
characterization and expression of a crustin-like gene from Chinese mitten crab,
Eriocheir sinensis. Dev Comp Immunol 34: 734–740.
24. Mitta G, Vandenbulcke F, Roch P (2000) Original involvement of antimicrobial
peptides in mussel innate immunity. FEBS Lett 486: 185–190.
25. Gueguen Y, Herpin A, Aumelas A, Garnier J, Fievet J, et al. (2006)
Characterization of a defensin from the oyster Crassostrea gigas. Recombinant

PLoS ONE | www.plosone.org

production, folding, solution structure, antimicrobial activities, and gene
expression. J Bio Chem 281: 313–323.
26. Li C, Sun H, Chen A, Ning X, Wu H, et al. (2009) Identification and
characterization of an intracellular Cu, Zn-superoxide dismutase (icCu/ZnSOD) gene from clam Venerupis philippinarum. Fish Shellfish Immunol 28:
499–503.
27. Laemmli UK (1970) Cleavage of structural proteins during the assembly of
bacteriophage T4. Nature 227: 680–685.

6

October 2010 | Volume 5 | Issue 10 | e13480



=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DRAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "APD6", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DRAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "CAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "dbAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "APD6", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "DRAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DRAMP", "db_subject_text": "", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now.