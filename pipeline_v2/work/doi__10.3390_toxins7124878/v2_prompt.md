
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
doi__10.3390_toxins7124878

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Minimal inhibitory concentrations (MIC) and minimal bactericidal concentrations (MBC) values of Phylloseptin-PBa against the Gram-positive bacterium, Staphylococcus aureus, the Gram-negative bacterium, Escherichia coli, and the yeast, Candida albicans.", "footnotes": [], "header_rows": [["Peptide Name", "MIC (mg/L)", "MBC (mg/L)"], ["S. aureus", "E. coli", "C. albicans", "S. aureus", "E. coli", "C. albicans"]], "longform_cells": [{"table_index": 1, "row_index": 3, "col_index": 2, "row_label": "Phylloseptin-PBa", "col_header": "S. aureus", "value": "8"}, {"table_index": 1, "row_index": 3, "col_index": 3, "row_label": "Phylloseptin-PBa", "col_header": "E. coli", "value": "128"}, {"table_index": 1, "row_index": 3, "col_index": 4, "row_label": "Phylloseptin-PBa", "col_header": "C. albicans", "value": "8"}, {"table_index": 1, "row_index": 3, "col_index": 5, "row_label": "Phylloseptin-PBa", "col_header": "S. aureus", "value": "8"}, {"table_index": 1, "row_index": 3, "col_index": 6, "row_label": "Phylloseptin-PBa", "col_header": "E. coli", "value": ">512"}, {"table_index": 1, "row_index": 3, "col_index": 7, "row_label": "Phylloseptin-PBa", "col_header": "C. albicans", "value": "8"}]}]

=== PRIMARY PAPER FULL TEXT (context only) ===
Use this ONLY to (a) confirm whether an organism/target/assay was tested in this paper (prevents false 'absent' calls), and (b) read an endpoint label. You may NOT cite full text as the `evidence` cell for is_database_error=true; that still requires a structured longform cell.
Article

Phylloseptin-PBa—A Novel Broad-Spectrum
Antimicrobial Peptide from the Skin Secretion
of the Peruvian Purple-Sided Leaf Frog
(Phyllomedusa Baltea) Which Exhibits Cancer
Cell Cytotoxicity
Yuantai Wan 1,† , Chengbang Ma 1,† , Mei Zhou 1 , Xinping Xi 1 , Lei Li 1 , Di Wu 1 , Lei Wang 1, *,
Chen Lin 2, *, Juan Chavez Lopez 3 , Tianbao Chen 1 and Chris Shaw 1
Received: 14 October 2015; Accepted: 23 November 2015; Published: 1 December 2015
Academic Editor: Stephen P. Mackessy
1

2
3

*
†

Natural Drug Discovery Group, School of Pharmacy, Queen’s University, Belfast BT9 7BL,
Northern Ireland, UK; ywan01@qub.ac.uk (Y.W.); c.ma@qub.ac.uk (C.M.); m.zhou@qub.ac.uk (M.Z.);
xxi01@qub.ac.uk (X.X.); lli12@qub.ac.uk (L.L.); dwu03@qub.ac.uk (D.W.); t.chen@qub.ac.uk (T.C.);
chris.shaw@qub.ac.uk (C.S.)
College of Basic Medical Science, Zhejiang Chinese Medial University, Hangzhou 310053, China
Perubiotech Eirl, Santiago de Surco, Lima 33, Peru; perubiotech@gmail.com
Correspondence: l.wang@qub.ac.uk (L.W.); clin011@163.com (C.L.); Tel.: +44-28-9097-2200 (L.W.);
+86-571-8661-3609 (C.L.); Fax: +86-571-8661-3770 (C.L.)
These authors contributed equally to this work.

Abstract:
Antimicrobial peptides from amphibian skin secretion display remarkable
broad-spectrum antimicrobial activity and are thus promising for the discovery of new antibiotics.
In this study, we report a novel peptide belonging to the phylloseptin family of antimicrobial
peptides, from the skin secretion of the purple-sided leaf frog, Phyllomedusa baltea, which was
named Phylloseptin-PBa. Degenerate primers complementary to putative signal peptide sites of
frog skin peptide precursor-encoding cDNAs were designed to interrogate a skin secretion-derived
cDNA library from this frog. Subsequently, the peptide was isolated and identified using reverse
phase HPLC and MS/MS fragmentation. The synthetic replicate was demonstrated to have activity
against S. aureus, E. coli and C. albicans at concentrations of 8, 128 and 8 mg/L, respectively.
In addition, it exhibited anti-proliferative activity against the human cancer cell lines, H460,
PC3 and U251MG, but was less active against a normal human cell line (HMEC). Furthermore,
a haemolysis assay was performed to assess mammalian cell cytotoxicity of Phylloseptin-PBa.
This peptide contained a large proportion of α-helical domain, which may explain its antimicrobial
and anticancer activities.
Keywords: amphibian; antimicrobial; anticancer; peptides; molecular cloning; mass spectrometry

1. Introduction
The skins of frogs secrete a profusion of bioactive peptides, especially antimicrobial peptides,
which function in the killing of bacteria and their biofilms. In the 30 years since the discovery
of the first antimicrobial peptide (AMP) from this source, hundreds of such peptides have
been identified [1]. Phyllomedusinae is a sub-family of the Hylidae. It consists of 57 species
in seven genera: Agalychnis, Cruziohyla, Hylomantis, Pachymedusa, Phasmahyla, Phrynomedusa and
Phyllomedusa [2] which are widely distributed across Central and South America. The skin secretions
of phyllomedusine frogs have been found to produce a large number of AMPs with various
Toxins 2015, 7, 5182–5193; doi:10.3390/toxins7124878

www.mdpi.com/journal/toxins

Toxins 2015, 7, 5182–5193

antimicrobial activities. As a consequence of their structural similarities and secondary structural
characteristics, these AMPs have been classified into six families [3,4]. The peptides from different
families have distinctive primary structures. However, their biosynthetic precursors display strong
evolutionary homologies, particularly in their highly conserved signal peptide and N-terminal
pro-regions [5].
Phylloseptins are a family of AMPs recently discovered from the skin secretion of phyllomedusine
frogs. They were first isolated from the skin secretion of Phyllomedusa hypochondrialis and
Phyllomedusa oreades by Leite in 2005 [6]. As time passed, more phylloseptins were isolated and
identified from other species. The biosynthetic precursors of these phyllposeptins exhibited common
characteristic structures and shared highly-conversed domains within their precursor-encoding
cDNAs [7]. The primary structure of phylloseptins usually comprises 19–21 amino acid residues
and they are positively charged, C-terminally amidated, and additionally contain a α-helical domain.
The natural characteristic of amphiphilicity of these peptides was proposed to account for their
bioactivity via combination with cytoplasmic membranes, prior to their disruption. Since they display
little haemolytic activity, phylloseptins are regarded as preferentially targeting prokaryotic rather
than eukaryotic membranes [6,7].
In this study, a novel phylloseptin, named Phylloseptin-PBa, was isolated from the skin secretion
of Phyllomedusa baltea—the first report of phylloseptin peptides from this frog. The structure of the
peptide was obtained via “shotgun” cloning using 31 RACE and 51 RACE. The predicted primary
structure was confirmed by MS/MS fragmentation sequencing. The synthetic replicate of the peptide
was subjected to antimicrobial, anticancer and haemolysis assays in order to determinate its biological
function. Phylloseptin-PBa displayed inhibitory activity against E. coli, S. aureus and C. albicans.
Specifically, the growth of the standard Gram-positive bacterium, S. aureus, was significantly
inhibited by Phylloseptin-PBa, but the peptide also inhibited the pathogenic yeast, C. albicans,
at the same minimal inhibitory concentration (MIC). A further study was carried out to determine
the concentration of Phylloseptin-PBa at which no growth of S. aureus and C. albicans occurred and
this was found to be 8 mg/L in both cases. However, Phylloseptin-PBa was not active against
E. coli at concentrations up to 128 mg/L. It also possessed a relatively low potency of haemolysis at
concentrations that were effective against S. aureus and C. albicans. Meanwhile, the anticancer activity
assay of this peptide indicated that it was active on all three human cancer cell lines tested (H460, PC3
and U251MG) but was less active on a normal human microvessel endothelial cell line (HMEC-1).
2. Results
2.1. Shotgun Cloning of Novel Peptide Precursor-Encoding cDNA
Using a Phyllomedusinae-specific degenerate primer, designed to the highly conserved signal
region from previously sequenced peptides from phyllomedusine frogs, a full-length cDNA encoding
Phylloseptin-PBa was successfully and repeatedly cloned (at least 25 clones were represented) from
the skin secretion-derived cDNA library of Phyllomedusa baltea. Through bioinformatic searches, the
putative mature peptide was analysed using the NCBI BLASTp program, which demonstrated that
Phylloseptin-PBa was a new member of the phylloseptin family. The nucleotide and translated
open reading frame amino acid sequences of precursor-encoding cDNA are shown in Figure 1.
Essentially, there were several defining characteristics of note: (1) the open reading frame of the
precursor consisted of 66 amino acid residues, which containing the mature peptide of 19 amino acids;
(2) A highly- conserved putative signal peptide region of 21 amino acid residues; (3) An acidic
amino acid residue-rich “spacer” peptide containing 22 residues; (4) A classical propeptide convertase
processing site (-KR-); (5) A mature active peptide encoding domain that contained 19 amino
acid residues with a typical phylloseptin N-terminal; (6) A C-terminal G residue that acts as an
amide donor for the L residue that terminates the mature peptide. According to the results of
BLAST analyses, Phylloseptin-PBa showed a high level of structural homology to phylloseptins

5183

Toxins 2015, 7, 5182–5193

from other frogs of the sub-family, Phyllomedusinae, including PS-7 to PS-11 from Phyllomedusa
hypochondrialis, PS-7, 8, 12 and 15 from Phyllomedusa azurea, PS-1 from Phyllomedusa sauvagei and PS-B
from 2015,
Phyllomedusa
bicolor [3]. The alignment of amino acid sequences of the precursor isolated from
Toxins
7, page–page
Toxins 2015, 7, page–page
Phyllomedusa
baltea with the top hits found in the database, are shown in Figure 2. The nucleotide
sequence of
thebeen
Phylloseptin-PBa
precursor
has been
deposited
in the
European(EMBL)
Molecular
Biology
precursor
has
deposited in the
European
Molecular
Biology
Laboratory
Nucleotide
precursor
has
been
deposited
in
the
European
Molecular
Biology
Laboratory
(EMBL)
Nucleotide
Laboratory
(EMBL) under
Nucleotide
Sequencecode
Database
under the accession code LN810553.
Sequence
Database
the accession
LN810553.
Sequence Database under the accession code LN810553.

M A F L
K K S
L F L
V L F F
G L V ·
M A F LTGAAGAAATC
K K S TCTTTTCCTT
L F L GTACTATTCT
V L F FTTGGATTGGT
G L V ·
1ATGGCTTTCT
1ATGGCTTTCT
TGAAGAAATC
TCTTTTCCTT
GTACTATTCT
TTGGATTGGT
TACCGAAAGA ACTTCTTTAG AGAAAAGGAA CATGATAAGA AACCTAACCA
TACCGAAAGA
·
S L S ACTTCTTTAG
I C E E AGAAAAGGAA
E K R CATGATAAGA
E T E AACCTAACCA
E E E N ·
·
S
L
S
I
C
E
E
E
K
R
E T E GAAGAAGAAA
E E E N ·
51TTCCCTTTCC ATCTGTGAAG AAGAGAAAAG AGAGACAGAA
51TTCCCTTTCC
ATCTGTGAAG TTCTCTTTTC
AAGAGAAAAG TCTCTGTCTT
AGAGACAGAA CTTCTTCTTT
GAAGAAGAAA
AAGGGAAAGG TAGACACTTC
AAGGGAAAGG
·
N Q E TAGACACTTC
E D D TTCTCTTTTC
K S E E TCTCTGTCTT
K R F CTTCTTCTTT
F S M
·
N
Q
E
E
D
D
K
S
E
E
K R F CTTCAGCATG
F S M
101ATAATCAAGA GGAAGATGAC AAAAGTGAAG AGAAGAGATT
101ATAATCAAGA
GGAAGATGAC
AAAAGTGAAG
AGAAGAGATT
CTTCAGCATG
TATTAGTTCT CCTTCTACTG TTTTCACTTC TCTTCTCTAA GAAGTCGTAC
TATTAGTTCT
I P K I CCTTCTACTG
A G G TTTTCACTTC
I A S TCTTCTCTAA
L V K N GAAGTCGTAC
L G *
I
P
K
I
A
G
G
I
A
S
L V K NACTTAGGTTA
L G *
151ATACCAAAGA TAGCAGGTGG AATAGCTTCA CTTGTTAAAA
151ATACCAAAGA
TAGCAGGTGG TTATCGAAGT
AATAGCTTCA GAACAATTTT
CTTGTTAAAA TGAATCCAAT
ACTTAGGTTA
TATGGTTTCT ATCGTCCACC
TATGGTTTCT ATCGTCCACC TTATCGAAGT GAACAATTTT TGAATCCAAT
201ATACAATGTA ACATTTCATA ACTCTAAGGA GCACAATTAT CAATAATTGT
201ATACAATGTA
ACATTTCATA TGAGATTCCT
ACTCTAAGGA CGTGTTAATA
GCACAATTAT GTTATTAACA
CAATAATTGT
TATGTTACAT TGTAAAGTAT
TATGTTACAT
TGTAAAGTAT
TGAGATTCCT
CGTGTTAATA
GTTATTAACA
251TCCCAAAATA CATTAAAGCA TATTTAACCA AAAAAAAAAA AAAAAAAAAA
251TCCCAAAATA
CATTAAAGCA ATAAATTGGT
TATTTAACCA TTTTTTTTTT
AAAAAAAAAA TTTTTTTTTT
AAAAAAAAAA
AGGGTTTTAT GTAATTTCGT
AGGGTTTTAT GTAATTTCGT ATAAATTGGT TTTTTTTTTT TTTTTTTTTT
Figure
1. Nucleotide
cDNA
Figure 1.
Nucleotide and
and translated
translated open‐reading
open-reading frame
frame amino
amino acid
acid sequences
sequences of
of cloned
cloned cDNA
Figure 1. the
Nucleotide
and precursor
translatedofopen‐reading
frameDouble
aminounderlining
acid sequences
of cloned
cDNA
encoding
biosynthetic
Phylloseptin‐PBa.
indicates
the
putative
encoding the biosynthetic precursor of Phylloseptin-PBa. Double underlining indicates the putative
encoding the biosynthetic
precursor of Phylloseptin‐PBa.
Double underlining
indicates
signal
peptide sequence
sequence
andthe
an putative
asterisk
signal peptide
peptide sequence,
sequence, single
single underlining
underlining indicates
indicates the
the mature
mature peptide
and
an
asterisk
signal
peptide
sequence,
single
underlining
indicates
the
mature
peptide
sequence
and
an asterisk
indicates
the
stop
codon.
indicates the stop codon.
indicates the stop codon.
LN810553
LN810553
AFR78285
AFR78285
P84567
P84567
CAI26288
CAI26288
AAO62959
AAO62959
ACG50814
ACG50814
CAI77674
CAI77674
B5LUQ9
B5LUQ9
Q0VZ41
Q0VZ41
CAP17493
CAP17493

1
69
1
69
(1) MAFLKKSLFLVLFFGLVSLSICEEEKRETEEEENNQEEDDK---SEEKRFFSMIPKIAGGIASLVKNLG
MAFLKKSLFLVLFFGLVSLSICEEEKRETEEEENNQEEDDK---SEEKRFFSMIPKIAGGIASLVKNLG
(1) MAFLKKSLFFVLFLGLVSLSIRGEKKRETEEKEYDQGEDDK---SEEKRFLSLIPHIVSGVASIAKHFG
(1) MAFLKKSLFLVLFLGLATLSICEEEKRETEEEEYNQEEDDK---SEEKRFLSLIPHAINAVSTLVHHFG
MAFLKKSLFFVLFLGLVSLSIRGEKKRETEEKEYDQGEDDK---SEEKRFLSLIPHIVSGVASIAKHFG
MAFLKKSLFLVLFLGLATLSICEEEKRETEEEEYNQEEDDK---SEEKRFLSLIPHAINAVSTLVHHFG
(1) MAFLKKSLFLILFLGLVPLSFCENDKREGENEE--EQDDDQ---SEEKRALGTLLKGVGSGKMVADQFG
MAFLKKSLFLILFLGLVPLSFCENDKREGENEE--EQDDDQ---SEEKRALGTLLKGVGSGKMVADQFG
(1) MAFLKKSLFLVLFLGLVSLSICEEEKRETEEKEYDQGEDDK---SEEKRFLSLIPHIVSGVAALAKHLG
MAFLKKSLFLVLFLGLVSLSICEEEKRETEEKEYDQGEDDK---SEEKRFLSLIPHIVSGVAALAKHLG
(1) MAFLKKSLFLVLFLGFVSVSICEEEKRQEDEDEHVEEGENQEEGSEEKRGLLSVLGSVAKVPVIAEHLG
MAFLKKSLFLVLFLGFVSVSICEEEKRQEDEDEHVEEGENQEEGSEEKRGLLSVLGSVAKVPVIAEHLG
(1) MHFLKKSIFLVLFLGLVSLSICEKEKREDQNEEEVDENE---EASEEKRGLMSILGKVAGFKPKENVQK
(1) MASLKKSFFLVLFLGLVSLSMCEEKKRENEDDAEDGNHE---EESEEKRGLVDFAKHVIGIASKLG--MHFLKKSIFLVLFLGLVSLSICEKEKREDQNEEEVDENE---EASEEKRGLMSILGKVAGFKPKENVQK
MASLKKSFFLVLFLGLVSLSMCEEKKRENEDDAEDGNHE---EESEEKRGLVDFAKHVIGIASKLG--(1) MAFLKKSLFLVLFLGLVSLSICEEEKRETEEEEYNQEDDDK---SEEKRFLSLIPTAINAVSALAKHFG
MAFLKKSLFLVLFLGLVSLSICEEEKRETEEEEYNQEDDDK---SEEKRFLSLIPTAINAVSALAKHFG
(1) MAFLKKSLFLVLFLGLVSLSICEEEKRETEEEEHDQEEDDK---SEEKRFLSMIPHIVSGVAALAKHLG
(1) MAFLKKSLFLVLFLGLVSLSICEEEKRETEEEEHDQEEDDK---SEEKRFLSMIPHIVSGVAALAKHLG

Figure 2. Multiple alignment of the cloned cDNA‐deduced amino acid sequence of Phylloseptin‐PBa
Figure 2.
2. in
Multiple
alignment
of the
theofcloned
cloned
cDNA‐deduced
amino
acid sequence
sequence
of Phylloseptin-PBa
Phylloseptin‐PBa
Figure
Multiple
alignment
of
cDNA-deduced
acid
of
obtained
this study,
with those
the top
hits following amino
NCBI‐BLASTp
analysis.
Gaps have been
obtained
in
this
study,
with
those
of
the
top
hits
following
NCBI‐BLASTp
analysis.
Gaps have
have been
been
obtained in
study, alignments.
with those ofBlack
the top
hits following
Gaps
included
to this
maximize
shading
indicates NCBI-BLASTp
identical aminoanalysis.
acid residues
among
all
included
to
maximize
alignments.
Black
shading
indicates
identical
amino
acid
residues
among
all
included
to maximize
alignments.
Black
shading amino
indicates
identical
amino
acid residues
all
acid
residues,
and green
shadingamong
indicates
the
sequences,
blue shading
indicates
consensus
amino acid
acid residues,
residues, and
and green
green shading
shading indicates
indicates
the sequences,
sequences,
blueresidues.
shading indicates
indicates consensus
consensus amino
the
blue
shading
similar
amino acid
similar amino
amino acid
acid residues.
residues.
similar

2.2. Isolation and Structural Characterization of Phylloseptin‐PBa from Reverse Phase HPLC Fractions of
2.2. Isolation
and Structural Characterization of Phylloseptin‐PBa from Reverse Phase HPLC Fractions of
2.2.
Isolation
Skin
Secretionand Structural Characterization of Phylloseptin-PBa from Reverse Phase HPLC Fractions of
Skin Secretion
The elution position of Phylloseptin‐PBa is shown on the RP‐HPLC chromatogram of the skin
Phylloseptin‐PBa
RP‐HPLC
chromatogram
The elution
positionbaltea
of Phylloseptin-PBa
is shown
on the
RP-HPLC
chromatogram
the skin
secretion
of Phyllomedusa
(Figure 3). The peptide
in the
indicated
fraction
with a massof
coincident
Phyllomedusa
baltea
(Figure
3).
secretion
of
Phyllomedusa
baltea
(Figure
3).
The
peptide
in
the
indicated
fraction
with
a
mass
coincident
with the approximate molecular mass of Phylloseptin‐PBa from its cloned precursor, was further
with the approximate
molecular mass
of Phylloseptin-PBa
Phylloseptin‐PBa
from
its cloned
precursor,
further
precursor,
analyzed
by MS/MS fragmentation
sequencing
(Figure 4). The
amino
acid sequence
of was
the mature
by thus
MS/MS
fragmentation
sequencing
(Figure
The
amino
analyzedwas
by
MS/MS
fragmentation
4).(G)
The
aminoinacid
of the mature
peptide
unequivocally
identified
and the
glycine
residue
the sequence
terminal position
of the
peptide
was
thus
unequivocally
identified
and
the
glycine
(G)
residue
in
the
terminal
position
of the
Phylloseptin‐PBa precursor was also confirmed as a donor for C‐terminal amidation.
Phylloseptin‐PBa precursor
precursor was
was also
also confirmed
confirmed as
as aa donor
donor for
for C-terminal
C‐terminal amidation.
amidation.
Phylloseptin-PBa
5184

Toxins
2015,
7, 5182–5193
Toxins
2015,
7, page–page
Toxins 2015, 7, page–page

Figure
3. Region
of of
reverse
phase
HPLC
chromatogram
of of
Phyllomedusa baltea
skin secretion
showing
Figure
Region
reverse
phase
HPLC
chromatogram
Figure 3.
3. Region
of reverse
phase
HPLC
chromatogram
of Phyllomedusa
Phyllomedusa baltea
baltea skin
skin secretion
secretion showing
showing
thethe
absorbance
peak
(arrow)
corresponding
to
Phylloseptin‐PBa.
The
Y‐axis
shows
the
relative
absorbance
peak
(arrow)
corresponding
to
Phylloseptin-PBa.
The
Y-axis
shows
the
the absorbance peak (arrow) corresponding to Phylloseptin‐PBa. The Y‐axis shows the relative
relative
absorbance
in milli‐absorbance
units at at
214 nmnm
and thethe
X‐axis shows
the retention
time.
absorbance
absorbance in
in milli-absorbance
milli‐absorbance units
units at 214
214 nm and
and the X-axis
X‐axis shows
shows the
the retention
retention time.
time.

Figure 4. Predicted singly‐ and doubly‐charged y‐ions and b‐ions arising from MS/MS fragmentation
Figure 4.
4. Predicted
singly‐ and
and doubly-charged
doubly‐charged y-ions
y‐ions and
and b-ions
b‐ionsarising
arisingfrom
fromMS/MS
MS/MS fragmentation
fragmentation
PredictedActual
singlyof Figure
Phylloseptin‐PBa.
fragment
ions observed following
MS/MS fragmentation
are indicated in
of Phylloseptin‐PBa.
Actual
fragmentation
areare
indicated
in
of
Phylloseptin-PBa.
Actualfragment
fragmentions
ionsobserved
observedfollowing
followingMS/MS
MS/MS
fragmentation
indicated
blue
and
red.
blue
and
red.
in blue and red.

2.3.
Peptide
Synthesis
2.3.
Peptide
Synthesis
2.3. Peptide Synthesis
The
solid‐phase
Fmoc
peptide
synthesis
of of
Phylloseptin‐PBa
was
found
to to
bebe
straightforward
The
solid‐phase
Fmoc
peptide
synthesis
Phylloseptin‐PBa
was
found
straightforward
The solid-phase
Fmoc
peptide
synthesis
of
Phylloseptin-PBa
was found to bewas
straightforward
and
deemed
to
be
highly
successful.
The
observed
molecular
weight
of
Phylloseptin‐PBa
2004.66
DaDa
and deemed to be highly successful. The observed molecular weight of Phylloseptin‐PBa was
2004.66
and
deemed
to
be
highly
successful.
The
observed
molecular
weight
of
Phylloseptin-PBa
was
(Figure
5).5).
Purification
of of
thethe
crude
product
was
achieved
byby
reverse
phase
HPLC.
Once
thethe
purified
(Figure
Purification
crude
product
was
achieved
reverse
phase
HPLC.
Once
purified
peptide
obtained,
it it
was
subjected
full
msms
scan
and
mass
spectrometry
peptidewas
was
obtained,
was
subjectedto to
full
scan
andtandem
tandem
mass
spectrometrypeptide
peptide
5185
4 4

Toxins 2015, 7, 5182–5193

Toxins 2015, 7, page–page

2004.66 Da (Figure 5). Purification of the crude product was achieved by reverse phase HPLC.
Toxins 2015, 7, page–page
Once the purified
peptide
was obtained,
it was
subjected
full ms
scan and
mass
fragmentation
(MS/MS
fragmentation),
in order
to confirm
its to
primary
structure
andtandem
thus identity
spectrometry
peptide
fragmentation
(MS/MS
in order
to confirm
itsidentity
primary
fragmentation
(MS/MS
fragmentation),
in order fragmentation),
to confirm its primary
structure
and thus
within
the natural
peptide.
structure
and
thus
identity
within
the
natural
peptide.
within the natural peptide.
2062 #1 RT: 0.00 AV: 1 NL: 6.02E4
T: ITMS + p ESI Full ms [150.00-2000.00]
2062 #1 RT: 0.00 AV: 1 NL: 6.02E4
100T: ITMS + p ESI Full ms [150.00-2000.00]
95
90
85
80
75

669.33
669.33

100
95
90
85
80
75

70
70

65
65
60
Relative Abundance

Relative Abundance

60
55
50
45
40

55
50
45
40

35

35

30

30

25

25

20

20

15

15

10

10

5

5

0

0

1003.33
1003.33

631.75 687.75
631.75
687.75
761.83
761.83

883.17
883.17
817.42
817.42

502.25 588.42
502.25
588.42
444.33
337.08
444.33
227.33337.08
227.33

200

200

300

300

400

400

500
500

600
600

700
700

800
800

900
900

1032.17
1032.17
1000
1000

1142.33
1142.33
1199.25
1199.25

1100
1100
m/z
m/z

1200

1200

1403.83
1994.83
1403.83 1476.00
1315.17
1476.001584.92
1584.92 1730.08 1788.00
1788.001893.42
1893.42 1994.83
1315.17

1730.08

1300

1300

1400

1400

1500

1500

1600

1600

1700

1700

1800

1800

1900

1900

2000

2000

Figure
5.The
The
MS
fullscan
scanof
syntheticphylloseptin‐PBa
phylloseptin‐PBa obtained
Figure
5. The
MS
full
scan
ofofsynthetic
synthetic
phylloseptin-PBa
obtainedfrom
fromthe
theLCQ
LCQFleet
Fleetelectrospray
electrospray
Figure
5.
MS
full
obtained
from
the
LCQ
Fleet
electrospray
ion‐trap
mass
spectrometer.
The
ions
of
m/z
669.33
and
1003.33
were
triply
charged
and
doubly
ion-trap mass
mass spectrometer.
spectrometer. The
The ions
ions of
of m/z
m/z669.33
669.33 and
and 1003.33
1003.33 were
were triply
triply charged
charged and
and
doubly
ion‐trap
doubly
charged,
respectively.
charged, respectively.
respectively.
charged,

2.4. Secondary Structure Prediction of the Peptide
2.4. Secondary
Secondary Structure
Structure Prediction
Prediction of the Peptide
2.4.
The predicted secondary structure of Phylloseptin‐PBa, obtained through software modeling on
The predicted
predicted secondary
secondary structure
structure of Phylloseptin‐PBa,
Phylloseptin-PBa, obtained
obtained through
through software modeling on
The
the I‐TASSER server, revealed that it contained a large proportion of α‐helical domain (Figure 6).
the I‐TASSER
I-TASSER server, revealed that it contained a large proportion of α‐helical
α-helical
the
(Figure
The side chains of the amino acids of the peptide partitioned into two planes,domain
indicating
their6).
The
side
chains
indicating
The
side
chains
of
the
amino
acids
of
the
peptide
partitioned
into
two
planes,
indicating
their
amphipathic nature. One side consisted of hydrophobic residue side chains within the helix axis,
amphipathic
Oneresidue
side consisted
consisted
of hydrophobic
hydrophobic
residue
side
chains
within
the helix
amphipathic
nature. One
side
of
chains
within
the
axis,
while the hydrophilic
side chains
were locatedresidue
on the side
opposite
side.
A helical
wheel
while
the
hydrophilic
residue
side
chains
were
located
on
the
opposite
side.
A
helical
wheel
projection
while
the
hydrophilic
residue
side
chains
were
located
on
the
opposite
side.
A
helical
wheel
projection revealed that the peptide had a typical propensity for α‐helix formation often found in
revealed
the(Figure
peptide
hadpeptide
a typical
propensity
α-helix formation
often
found inoften
typical
AMPs
projection
revealed
that7).the
had
a typicalfor
propensity
for α‐helix
formation
found
in
typicalthat
AMPs
(FigureAMPs
7).
typical
(Figure 7).

Figure 6. Predicted secondary structure of Phylloseptin‐PBa using the on‐line protein secondary
structure prediction tool, I‐TASSER.
Figure
Figure 6. Predicted
Predictedsecondary
secondary structure
structure of
of Phylloseptin‐PBa
Phylloseptin-PBa using
using the
the on‐line
on-line protein
protein secondary
secondary
structure
structure prediction tool, I‐TASSER.
I-TASSER.

5186
5

5

Toxins 2015, 7, 5182–5193
Toxins 2015, 7, page–page

Figure 7. Helical wheel plot of Phylloseptin‐PBa. An amphipathic character was observed with side
chains
of the plot
hydrophobic
residues (M4, L15, I8, F1,
I12, I5, V16, A9) character
partitioning towas
one side
of
Figure 7. Helical
wheel
of Phylloseptin-PBa.
AnL19amphipathic
observed
with side
the molecule and the cationic amino acid groups (α‐amino of G10, side‐chain groups of amino acids
chains of the hydrophobic
residues (M4, L15, I8, F1, L19 I12, I5, V16, A9) partitioning to one side of
K7 and K17) appearing on the opposite side.
the molecule and the cationic amino acid groups (α-amino of G10, side-chain groups of amino acids
Antimicrobialon
andthe
Haemolytic
Activity
of Phylloseptin‐PBa
K7 and K17)2.5.appearing
opposite
side.

MICs, minimal bactericidal concentrations (MBCs) and haemolytic effects of Phylloseptin‐PBa
were assessed. Their effects on the Gram‐positive bacterium, Staphylococcus aureus, the
2.5. Antimicrobial
and Haemolytic
Activity
of coli,
Phylloseptin-PBa
Gram‐negative
bacterium,
Escherichia
and the yeast, Candida albicans, are shown in Table 1.
Phylloseptin‐PBa exhibited potent antimicrobial activity against Staphylococcus aureus and Candida
MICs, minimal
(MBCs)
andMIC
haemolytic
effects
ofboth
Phylloseptin-PBa
albicans. bactericidal
More specifically,concentrations
Phylloseptin‐PBa possessed
the same
values of 8 mg/L
against
organisms,
these
values
being
identical
to
their
MBCs
(Table
1).
Meanwhile,
Phylloseptin‐PBa
were assessed. Their effects on the Gram-positive bacterium, Staphylococcus aureus, the Gram-negative
showed much weaker antimicrobial activity against Escherichia coli with an MIC value of 128 mg/L.
bacterium, Escherichia
and the was
yeast,
Candida
in (1.4%)
Tableon1.horse
Phylloseptin-PBa
However, coli,
Phylloseptin‐PBa
associated
with albicans,
a relativelyare
low shown
cytotoxicity
erythrocytes
at a concentration
8 mg/L, but
this rose to around
80% at and
a concentration
exhibited potent
antimicrobial
activityof against
Staphylococcus
aureus
Candida ofalbicans. More
128 mg/L (Figure 8).

specifically, Phylloseptin-PBa possessed the same MIC values of 8 mg/L against both organisms,
1. Minimal inhibitory concentrations (MIC) and minimal bactericidal concentrations (MBC)
these values beingTable
identical
to their MBCs (Table 1). Meanwhile, Phylloseptin-PBa showed much
values of Phylloseptin‐PBa against the Gram‐positive bacterium, Staphylococcus aureus, the
Gram‐negative
bacterium,
Escherichia
coli, and the yeast,
weaker antimicrobial
activity
against
Escherichia
coli Candida
with albicans.
an MIC value of 128 mg/L. However,
Phylloseptin-PBa was associated with a relatively
low cytotoxicity
(1.4%) on horse erythrocytes at
MIC (mg/L)
MBC (mg/L)
Peptide name
a concentration of 8 mg/L,
but thisS.Aureus
rose to around
80%
at
a
concentration
of 128 mg/L (Figure 8).
E.Coli C.Albicans S.Aureus E.coli C.Albicans
Phylloseptin‐PBa

8

128

8

8

>512

8

Table 1.
Minimal inhibitory concentrations (MIC) and minimal bactericidal concentrations
(MBC) values of Phylloseptin-PBa against the Gram-positive bacterium, Staphylococcus aureus,
the Gram-negative bacterium, Escherichia coli, and the yeast, Candida albicans.
Peptide Name
Phylloseptin-PBa

S. aureus
8

MIC (mg/L)
E. coli
C. albicans
128

8

S. aureus
8

MBC (mg/L)
E. coli
C. albicans
>512

8

Toxins 2015, 7, page–page

6

Figure 8. Haemolytic activity of Phylloseptin‐PBa. Percentage of haemolysis was calculated in

Figure 8. Haemolytic activity of Phylloseptin-PBa. Percentage of haemolysis was calculated in
comparison to the positive control using TritonX‐100.
comparison to the positive control using TritonX-100.
2.6. Anti‐Proliferative Effects of Phylloseptin‐PBa on Human Cancer Cells
Eleven human cancer cell lines were used to examine the anti‐proliferative effects of
5187
Phylloseptin‐PBa and they showed obvious activity in three of these: the lung cancer cell line (H460),
the prostate cancer cell line (PC3) and the neurospongioma cell line (U251MG), respectively.
The human microvessel endothelial cell line (HMEC‐1) was used to evaluate inherent cytotoxicity of
Phylloseptin‐PBa against normal human cells. It showed selective cytotoxicity against the three

Toxins 2015, 7, 5182–5193

2.6. Anti-Proliferative Effects of Phylloseptin-PBa on Human Cancer Cells

Figure 8. Haemolytic activity of Phylloseptin‐PBa. Percentage of haemolysis was calculated in
comparison to the positive control using TritonX‐100.

Eleven human cancer cell lines were used to examine the anti-proliferative effects of
the lung cancer cell line
(H460),
prostate
cancer
line
neurospongioma
cell line (U251MG), respectively.
Eleven
humanthe
cancer
cell lines
werecell
used
to (PC3)
examineand
the the
anti‐proliferative
effects of
Phylloseptin‐PBa
and they
showed obvious
activity in three
of these:
lung cancer was
cell line
(H460),
The human
microvessel
endothelial
cell
line the
(HMEC-1)
used
to evaluate inherent cytotoxicity
the prostate cancer cell line (PC3) and the neurospongioma cell line (U251MG), respectively.
of Phylloseptin-PBa against normal human cells. It showed selective cytotoxicity against the three
The human microvessel endothelial cell line (HMEC‐1) was used to evaluate inherent cytotoxicity of
different
cancer
cellhuman
lines cells.
and Itlower
against
HMEC-1
cells (Figure 9). The IC50 values
Phylloseptin‐PBa
against
normal
showedcytotoxicity
selective cytotoxicity
against
the three
differentafter
canceracell
and lower cytotoxicity
against
HMEC‐1
cells1.8
(Figure
The 36.6
IC50 values
24lines
h incubation,
were 4.3
µM,
2.9 µM,
µM9).and
µM,after
respectively.
Phylloseptin-PBa
and they on
showed
obvious
2.6. Anti‐Proliferative
Effects of Phylloseptin‐PBa
Human Cancer
Cells activity in three of these:

Toxins
page–page
a 24 h incubation, were 4.3 μM, 2.9 μM, 1.8 μM and
36.62015,
μM,7,respectively.

(C) U251MG-24h

100

100

75

75

Cell Viability%

Cell Viability%

(A) H460-24h

50
25
0
-10

-9

-8

-7

-6

-5

50
25
0
-10

-4

-9

Log[peptides] M

(B) PC3-24h

-6

-5

-4

-5

-4

125

75

Cell Viability %

Cell Viability%

-7

(D) HMEC-1-24h

100

50
25
0
-10

-8

Log[peptides] M

-9

-8

-7

-6

-5

-4

Log[peptides] M

100
75
50
25
0
-10

-9

-8

-7

-6

Log[peptides] M

Figure 9. Dose‐response curves of Phylloseptin‐PBa on human cancer cell lines after a 24 h incubation.

7
Figure 9. Dose-response curves
ofPanels
Phylloseptin-PBa
onthe
human
lines
a 24
incubation.
A, B, C and D show
peptide cancer
effects oncell
H460
(lungafter
cancer),
PC3h(prostate
cancer), U251MG
Panels A, B, C and D show the peptide
effects onand
H460
(lung
cancer), endothelial
PC3 (prostate
cancer),
(neurospongioma),
HMEC‐1
(microvessel
cells). IC
50 values U251MG
were 4.3 μM, 2.9 μM,
μM and 36.6 μM,
respectively. cells). IC
(neurospongioma), and HMEC-11.8(microvessel
endothelial
50 values were 4.3 µM, 2.9 µM,
1.8 µM and 36.6 µM, respectively.
3. Experimental Section

3. Experimental Section

3.1. Specimen Acquisition

Specimens of Phyllomedusa baltea were collected in Peru by PeruBiotech E.I.R.L. The skin
secretion (40 mg lyophilised dry weight) of captured adults was subsequently harvested using mild
electrical stimulation of the dorsal skin surface. Briefly, the moistened skin was stimulated by
platinum
(6 V DC; 4 msinpulse‐width;
Hz) for two periods
of 20 s The
duration.
After this,
Specimens of Phyllomedusa
balteaelectrodes
were collected
Peru by50PeruBiotech
E.I.R.L.
skin
stimulated secretion was collected by washing from the frog skin using distilled, deionised water.
secretion (40 mg lyophilised dry
weight) of captured adults was subsequently harvested using mild
These skin secretions were snap‐frozen in liquid nitrogen, lyophilised and stored at −20 °C prior
electrical stimulation of the dorsal
skin surface. Briefly, the moistened skin was stimulated by
to analysis.

3.1. Specimen Acquisition

platinum electrodes (6 V DC; 4 ms pulse-width; 50 Hz) for two periods of 20 s duration. After this,
3.2. Shotgun Cloning of Phylloseptin‐PBa Precursor‐Encoding cDNA
stimulated secretion was collected by washing from the frog skin using distilled, deionised water.
Five mg of lyophilised Phyllomedusa baltea skin secretion were dissolved
in 1 mL of cell
These skin secretions were snap-frozen
in liquid nitrogen, lyophilised and stored at ´20 ˝ C prior
lysis/mRNA stabilisation buffer (Dynal, Merseyside, UK). Magnetic oligo‐dT beads were used to
to analysis.
isolate polyadenylated mRNA in accordance with the manufacturer’s description (Dynal,
Merseyside, UK) and the isolated mRNA was subsequently subjected to RACE procedures to acquire
full‐length Precursor-Encoding
prepropeptide nucleic acid
sequence data by using a SMART‐RACE kit (Clontech, Oxford,
3.2. Shotgun Cloning of Phylloseptin-PBa
cDNA
UK) essentially as outlined by the manufacturer. Briefly, the 3′‐RACE reactions employed a
UPM
primer baltea
(supplied
with
the were
kit) dissolved
and
degenerate
Five mg of lyophilised Phyllomedusa
skin secretion
in 1 mL sense
of cell primer
(5′‐ACTTTCYGAWTTRYAAGMSCARABATG‐3′) that were designed to highly‐conserved segments
lysis/mRNA stabilisation buffer
(Dynal, Merseyside, UK). Magnetic oligo-dT beads were used
of the signal peptides of cDNAs cloned previously from other Phyllomedusa frogs within our group [7].
to isolate polyadenylated mRNA in accordance with the manufacturer’s description (Dynal,
8
Merseyside, UK) and the isolated mRNA was subsequently subjected to RACE procedures

5188

Toxins 2015, 7, 5182–5193

to acquire full-length prepropeptide nucleic acid sequence data by using a SMART-RACE kit
(Clontech, Oxford, UK) essentially as outlined by the manufacturer. Briefly, the 31 -RACE
reactions employed a UPM primer (supplied with the kit) and degenerate sense primer
(51 -ACTTTCYGAWTTRYAAGMSCARABATG-31 ) that were designed to highly-conserved segments
of the signal peptides of cDNAs cloned previously from other Phyllomedusa frogs within our group [7].
The PCR cycling procedure was as follows: step one: initial denaturation: 90 s at 94 ˝ C; 35 cycles:
denaturation 30 s at 94 ˝ C; step two: primer annealing for 30 s at 58 ˝ C; step three; extension
for 180 s at 72 ˝ C. PCR products were gel-purified and cloned using a pGEM-T vector system
(Promega Corporation, Southampton, UK) and sequenced using an ABI 3100 automated sequencer
(Applied Biosystems, Foster City, CA, USA).
3.3. Identification and Structural Analysis of Phylloseptin-PBa
Five mg of lyophilised skin secretion from Phyllomedusa baltea, were dissolved in 0.5 mL
of TFA/water and cleared of microparticulates by centrifugation (2500ˆ g for 5 min).
The clear supernatants were pumped onto an analytical reverse phase HPLC Jupiter C5
column (250 mm ˆ 4.6 mm, Phenomenex, UK). Peptides were eluted from the HPLC column
with a linear gradient formed from 0.05/99.95 (v/v) TFA/water to 0.05/19.95/80.00 (v/v/v)
TFA/water/acetonitrile over 240 min at a flow rate of 1 mL/min. A Cecil CE4200 Adept gradient
reverse phase HPLC (Cecil, Cambridge, UK) was used and automatic collection of fractions was
performed at 1 min intervals. The calculated molecular masses of predicted novel mature peptides
from open-reading frames of cloned cDNAs were used to interrogate a mass spectral library of
skin secretion peptides from reverse phase HPLC fractions using MALDI-TOF mass spectrometry
(Perseptive Biosystems, MA, USA) in positive detection mode. The fraction containing a peptide
with a molecular mass identical to that of the deduced novel cDNA-encoded peptide was analysed
by MS/MS fragmentation sequencing using an LCQ-Fleet electrospray ion-trap mass spectrometer
(Thermo Fisher Scientific, San Francisco, CA, USA).
3.4. Solid-Phase Peptide Synthesis of Phylloseptin-PBa
Following confirmation of the unequivocal primary structure of this novel peptide, it was
chemically-synthesised by solid phase Fmoc chemistry using a PS4 automated solid-phase
synthesiser (Protein Technologies, Inc., Tucson, AZ, USA). All of the dry amino acids were weighed
and mixed with 2-(1H-benzotriazol-1-yl)-1,1,3,3-tetramethyluronium hexafluorophosphate (HBTU)
activator and added to the reaction vessel on the PS4 machine. Deprotection of the Fmoc groups
from the amino acids was performed in 20% piperidine in dimethylformamide (DMF). The coupling
of peptide bonds was performed in 1 M N-Methylmorpholine (NMM) in DMF. After the reaction
was complete, the peptide-resin mixture was washed by 30 mL of degassed dichloromethane (DCM)
and subsequently dried in a vacuum desiccator overnight. Peptide was cleaved from the resin using
95% trifluoroacetic acid (TFA), 2.5% triisopropylsilane (TIPS) and 2.5% water. The confirmation of
structure of the synthetic peptide was accomplished using both reverse-phase HPLC and electrospray
mass spectrometry. This also established its degree of purity.
3.5. Antimicrobial Assays
Antimicrobial activity of the synthetic peptide was evaluated by means of determining MICs
using standard strains of Gram-negative bacteria, Gram-positive bacteria and pathogenic yeast.
The peptide was prepared in a concentration range of 1–512 mg/L and organisms were grown
in Mueller-Hinton broth (MHB) for 18 h. Peptide solutions were then mixed with microorganism
cultures (105 colony forming units (CFU)/mL) and placed into 96-well microtitre cell culture plates.
Plates were incubated for 18 h at 37 ˝ C in an orbital incubator. Subsequently, the growth of
bacteria/yeast was assessed by determination of optical density (OD) at λ550 nm. The MIC values
were obtained according to the lowest concentrations of peptide at which no growth was detectable.
5189

Toxins 2015, 7, 5182–5193

Subsequently, 10 µL of each clear solution was inoculated onto Mueller Hinton agar (MHA) plates.
After 24 h, the minimum bactericidal concentrations (MBCs) were obtained, based on the definition
of MBC as the concentration of peptide in which colonies grew.
3.6. Haemolysis Assays
A 4% (v/v) suspension of red blood cells was prepared from defibrinated horse blood
(TCS Biosciences Ltd, Buckingham, UK) by repeated washings and centrifugations in sodium
phosphate-buffered saline (PBS). Peptide solutions of different concentrations were prepared
according to the description in the antimicrobial assay in a previous section. Horse red blood cell
suspension samples (200 µL) were incubated with a range of peptide concentrations, similar to the
antimicrobial activity assays, at 37 ˝ C for 60 min and 120 min. Lysis of red cells was detected by
measurement of supernatants using an ELISA plate reader (Biolise BioTek EL808, Winooski, VT, USA)
with optical density set at λ550 nm. Positive controls consisted of a 2% (v/v) red cell suspension and
an equal volume of PBS containing 2% (v/v) of the non-ionic detergent, Triton X-100 (Sigma Aldrich,
St. Louis, MO, USA). Negative controls employed consisted of a 2% (v/v) red cell suspension and
PBS in equal volumes. The percentage of haemolysis was computed by the following formula:
% Haemolysis “ pA ´ A0q { pAx ´ A0q ˆ 100%

(1)

where A is the OD (λ570) for the mixture of peptide and suspensions, Ax is OD (λ570) for the positive
control and A0 is OD (λ570) for the negative control.
3.7. Cells Lines and Cell Culture
The human breast cancer cell lines (MB231, MB435s, MCF-7), the human prostate cancer cell
lines (DU145, PC3, LNCap), the human lung cancer cell lines (H838, H460 and H157), and the human
neuropongioma cell line (U251MG), were separately cultured employing RPMI-1640 culture medium
(Invitrogen, Paisley, UK), or Dulbecco’s Modified Eagle’s Medium (DMEM) (Sigma, St. Louis, MO,
USA), with 1% penicillin streptomycin solution (Sigma) and 10% fetal bovine serum (FBS) (Sigma)
added. The human microvessel endothelial cell (HMEC-1) was employed to evaluate the cytotoxicity
of the peptide against normal human cells, and these cells were grown in 10% FBS, 10 ng/mL EGF,
10 mM L-Glutamine, 1% penicillin streptomycin supplemented MCDB131 medium (Gibco, Paisley,
UK). The selected cells were inoculated into 90 mm culture dishes (Nunc, Roskilde, Denmark) or into
75 cm2 culture flasks (Nunc). Following this, flasks were placed in an incubator with a humidified
environment containing 5% CO2 .
3.8. Assessment of Cancer Cell Antiproliferative Activity Using the MTT Cell Viability Assay
Cancer cell line proliferation and viability were assessed using the MTT cell viability assay [8].
Briefly, each of the cancer cell lines was seeded at a density of 5 ˆ 103 cells per well onto 96 well plates.
Following this, cell lines were prepared with gradient concentrations of peptide and incubated over
24 h. After this, 10 µL of 5 mg/mL yellow coloured MTT solution (Sigma) were added to all wells and
incubated again for 4 h. Once the supernatants were removed by a syringe, 100 µL of DMSO were
added to all wells after gently agitating in order to completely mix the formazan crystals that had
developed. A Synergy HT plate reader (BioTek, Winooski, VT, USA) was set at 550 nm for recording
the absorbance, and the statistical analysis of results was performed using Student’s t-test through
GraphPad Prism 5.0 software. The final results were considered to be statistically significant if the
p value was <0.05.
4. Discussion
Phyllosep

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "80% Hemolysis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "Tumor cells: U-251MG (IC50=1.8µM); PC-3 (IC50=2.9µM); NCI-H460 (IC50=4.3µM)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "80% Hemolysis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "Tumor cells: U-251MG (IC50=1.8µM); PC-3 (IC50=2.9µM); NCI-H460 (IC50=4.3µM)", "db_measure": "Antimicrobial, Anticancer", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "CAMP", "db_subject_text": "S. aureus (MIC = 8mg/L), E. coli (MIC = 128mg/L), C. albicans (MIC =8g/L)", "db_measure": "text", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Human microvascular endothelial cells HMEC-1", "db_measure": "IC50", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Horse erythrocytes", "db_measure": "1.4% Hemolysis", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus NCTC 10788", "db_measure": "MBC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Escherichia coli NCTC 10418", "db_measure": "MBC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Candida albicans NCYC 1467", "db_measure": "MBC", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "DBAASP", "db_subject_text": "Human lung carcinoma NCI-H460", "db_measure": "IC50", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DBAASP", "db_subject_text": "Human prostate adenocarcinoma PC-3", "db_measure": "IC50", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now.