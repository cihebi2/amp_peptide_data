
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
doi__10.1186_1471-2164-8-119

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Identification of the transcripts predicted to be involved in common cellular processes and those similar to known venom components. The putative identity corresponds to the eukaryotic orthologous group (KOG), as detailed in Methods.", "footnotes": [], "header_rows": [["Sequence Id", "GenBank", "Descriptor"], ["Gene products predicted to be involved in common cellular processes"], ["HGE001|Contig13", "EL698878", "KOG1376 Alpha tubulin"], ["HGE003|Contig21", "EL698880", "KOG3412 60S ribosomal protein L28"], ["HGE004|Contig12", "EL698881", "KOG0279 G protein beta subunit-like protein"], ["HGE005|Contig19", "EL698882", "KOG1954 Endocytosis/signaling protein EHD1"], ["HGE006|2203", "EL698883", "KOG3418 60S ribosomal protein L27"], ["HGE007|2225", "EL698884", "KOG3449 60S acidic ribosomal protein P2"], ["HGE008|2233", "EL698944", "KOG0714 Molecular chaperone (DnaJ superfamily)"], ["HGE009|2404", "EL698885", "KOG3458 NADH:ubiquinone oxidoreductase, NDUFA8/PGIV/19 kDa subunit"], ["HGE010|2258", "EL698886", "KOG0863 20S proteasome, regulatory subunit alpha type PSMA1/PRE5"], ["HGE011|2268", "EL698887", "KOG3311 Ribosomal protein S18 (40S)"], ["HGE012|2330", "EL698888", "KOG1629 Bax-mediated apoptosis inhibitor TEGT/BI-1"], ["HGE013|2397", "EL698889", "KOG0898 40S ribosomal protein S15"], ["HGE014|2453", "EL698890", "KOG2597 Predicted aminopeptidase of the M17 family"], ["HGE015|2217", "EL698891", "KOG3752 Ribonuclease H"], ["HGE017|2209", "EL698945", "KOG0876 Manganese superoxide dismutase"], ["HGE018|2232", "EL698892", "KOG2941 Beta-1,4-mannosyltransferase"], ["HGE020|2328", "EL698894", "KOG4075 Cytochrome c oxidase, subunit IV/COX5b"], ["HGE021|2448", "EL698895", "KOG2667 COPII vesicle protein"], ["HGE022|contig17", "EL698896", "KOG2403 Succinate dehydrogenase, flavoprotein subunit"], ["HGE023|2323", "EL698897", "KOG2486 Predicted GTPase"], ["HGE033|2208", "EL698907", "KOG4604 Uncharacterized conserved protein"], ["Gene products similar to known venom components"], ["HGE024|Contig2", "EL698898", "α-KTx 6 subfamily"], ["HGE025|Contig5", "EL698899", "Novel α-KTx"], ["HGE034|Hgscplike1", "EL698908", "Scorpine-like group"], ["HGE026|Hgscplike2", "EL698900", "Scorpine-like group"], ["HGE035|HgbetaKTx1", "EL698909", "Novel β-KTx"], ["HGE027|NDPB_5.5", "EL698901", "Novel NDBP group 5"], ["HGE028|NDPB_5.6", "EL698902", "Novel NDBP group 5"], ["HGE029|NDPB_3.7", "EL698903", "Novel NDBP group 3"], ["HGE031|PLA2", "EL698905", "Novel group III heterodimeric phospholipase"], ["HGE030|Hg1", "EL698904", "KOG4295 Serine proteinase inhibitor (KU family)"]], "longform_cells": []}]

=== PRIMARY PAPER FULL TEXT (context only) ===
Use this ONLY to (a) confirm whether an organism/target/assay was tested in this paper (prevents false 'absent' calls), and (b) read an endpoint label. You may NOT cite full text as the `evidence` cell for is_database_error=true; that still requires a structured longform cell.
BMC Genomics

BioMed Central

Research article

Open Access

Transcriptome analysis of the venom gland of the Mexican scorpion
Hadrurus gertschi (Arachnida: Scorpiones)
Elisabeth F Schwartz1,2, Elia Diego-Garcia1, Ricardo C Rodríguez de la Vega1
and Lourival D Possani*1
Address: 1Departamento de Medicina Molecular y Bioprocesos, Instituto de Biotecnología, Universidad Nacional Autónoma de México, Avenida
Universidad, 2001 Cuernavaca 62210, Mexico and 2Departamento de Ciências Fisiológicas, Instituto de Ciências Biológicas, Universidade de
Brasília, Brasília, DF, 70910-900, Brasil
Email: Elisabeth F Schwartz - efschwa@unb.br; Elia Diego-Garcia - elia@ibt.unam.mx; Ricardo C Rodríguez de la Vega - delavega@ibt.unam.mx;
Lourival D Possani* - possani@ibt.unam.mx
* Corresponding author

Published: 16 May 2007
BMC Genomics 2007, 8:119

doi:10.1186/1471-2164-8-119

Received: 17 March 2007
Accepted: 16 May 2007

This article is available from: http://www.biomedcentral.com/1471-2164/8/119
© 2007 Schwartz et al; licensee BioMed Central Ltd.
This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/2.0),
which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.

Abstract
Background: Scorpions like other venomous animals posses a highly specialized organ that
produces, secretes and disposes the venom components. In these animals, the last postabdominal
segment, named telson, contains a pair of venomous glands connected to the stinger. The isolation
of numerous scorpion toxins, along with cDNA-based gene cloning and, more recently, proteomic
analyses have provided us with a large collection of venom components sequences. However, all
of them are secreted, or at least are predicted to be secretable gene products. Therefore very little
is known about the cellular processes that normally take place inside the glands for production of
the venom mixture. To gain insights into the scorpion venom gland biology, we have decided to
perform a transcriptomic analysis by constructing a cDNA library and conducting a random
sequencing screening of the transcripts.
Results: From the cDNA library prepared from a single venom gland of the scorpion Hadrurus
gertschi, 160 expressed sequence tags (ESTs) were analyzed. These transcripts were further
clustered into 68 unique sequences (20 contigs and 48 singlets), with an average length of 919 bp.
Half of the ESTs can be confidentially assigned as homologues of annotated gene products.
Annotation of these ESTs, with the aid of Gene Ontology terms and homology to eukaryotic
orthologous groups, reveals some cellular processes important for venom gland function; including
high protein synthesis, tuned posttranslational processing and trafficking. Nonetheless, the main
group of the identified gene products includes ESTs similar to known scorpion toxins or other
previously characterized scorpion venom components, which account for nearly 60% of the
identified proteins.
Conclusion: To the best of our knowledge this report contains the first transcriptome analysis of
genes transcribed by the venomous gland of a scorpion. The data were obtained for the species
Hadrurus gertschi, belonging to the family Caraboctonidae. One hundred and sixty ESTs were
analyzed, showing enrichment in genes that encode for products similar to known venom
components, but also provides the first sketch of cellular components, molecular functions,
biological processes and some unique sequences of the scorpion venom gland.

Page 1 of 12
(page number not for citation purposes)

BMC Genomics 2007, 8:119

Background
Scorpion venoms are very complex mixtures with hundreds of different components produced by the highly
specialized venom glands. The most prominent components of scorpion venoms are the peptides responsible for
the neurotoxic effects associated with their sting, for
which more than 350 different have been described
(extensive databases can be found in Tox-Prot [1] and
SCORPION [2]). Most of these toxins are structurally
related disulphide-rich short proteins (23–75 amino acid
residues long), which affect cellular communication by
modulating Na+ or K+ ion-channels permeability [3]. Due
to their importance in scorpion envenomation and their
usefulness as molecular and pharmacological probes for
studying ion-channels, most of the work performed to
date are focused at these neurotoxins, with relative few
other components ever described; among which are heterodimeric phospholipases A2 (v.gr. [4-6]), non-disulphide short peptides with cytolytic activity and a few other
functions [7,8]. Recent proteomic analyses [9-16] have
documented the overall composition for nine scorpion
species, all of them from the family Buthidae and most of
them belonging to the Tityus genus. These analyses confirmed the gross estimation of an average of one hundred
different proteins in each one of the venoms [17]. Approximately half of them comprehend components with
molecular masses in the range of commonly found scorpion toxins (2,000–8,000 Da). These numbers contrast
heavily with the known universe of protein components
(near four hundreds) described to exist in scorpion venoms, from which only about 12% are not classified within
the known scorpion toxin families.
Further insights into scorpion venom compositions have
been achieved by gene cloning by PCR-based methods
conducted with cDNA libraries. For example, almost one
hundred toxin precursors have been sequenced from
venom gland libraries of the buthid scorpion Mesobuthus
martensii (v.gr. [18-20]). Unfortunately the spectrum of
sequences obtained through PCR-based approach is limited by the specificity of the PCR primers used. It is worth
noticing that although PCR-based methods along with the
abundant isolation and characterization of scorpion toxins and, more recently, proteomic profiling of whole venoms, have provided us with a large number of sequences,
all these components are secreted from the venom glands.
Little is known about the biological processes that are taking place inside the venom gland cells. Therefore, we
elected to use a transcriptome approach to improve the
understanding of the composition of Hadrurus gertschi
venom gland.
The scorpion H. gertschi Soleglad (1976) belongs to the
family Caraboctonidae [21] and is considered no dangerous to humans. H. gertschi is endemic to Mexico, occurring exclusively in the State of Guerrero, and lives

http://www.biomedcentral.com/1471-2164/8/119

underground in tunnels excavated in the soil. From the
venom of this scorpion few components have been isolated and studied: hadrurin, an antimicrobial and cytolytic peptide [22]; HgeTx1, a K+ channel blocker [23];
hadrucalcine, a peptide capable of activating skeletal
Ryanodine receptors [Schwartz et al., in preparation], and;
the precursors HgeScplp and HgeβKTx, which encode for
long-chain peptides similar to Scorpine and βKTx's,
respectively [24]. Although hadrurin was reported as component of H. aztecus venom [22], the specimens used in
that work were not taxonomically identified and latter it
was realized that scorpions from that geographical region
should be named H. gertschi; this species assignment was
confirmed by identification of relevant taxonomic keys in
the specimens.
In the present work we randomly generated and analyzed
160 expressed sequence tags (ESTs) from a cDNA library
of the venom gland of H. gertschi. These 160 ESTs corresponded to 0.15% of the whole non-amplified cDNA
library and were generated from a non-normalized cDNA
library. After clustering the resulting dataset, we identified
transcripts possibly associated with different cellular functions. The possible roles of some of the transcripts are discussed, although many have unknown functions.
Furthermore, we present 8 full length sequences of new
toxins.
Single-pass gene sequencing from cDNA libraries is an
affordable strategy to mine the transcript profile of a given
tissue [25]. This strategy has been used to analyze the transcripts profiles for few other venomous organisms, such as
cnidarians [26,27], cone snails [28], fishes [29], snakes
(v.gr. [30-32]) and spiders [33]. To the best of our knowledge, this is the first report of an ESTs strategy conducted
with any scorpion venom gland. Moreover, this is the first
comprehensive molecular study of a non-buthid scorpion, which could serve for comparative purposes when
studying the details of the process by which buthid scorpions have been assembling their neurotoxic arsenal.

Results
cDNA library and EST analysis
The H. gertschi venom gland library constructed was not
amplified (2.8 × 105 cfu/mL with 99% recombinant
clones); therefore the cluster size might reflect the relative
abundance of the corresponding mRNA population (see
[34,35], but also [36,37]). After sequencing, 160 electropherograms were submitted to bioinformatics analysis to
remove vector and poor quality sequences, resulting in
147 high-quality ESTs which were used to analyze gene
expression profile in the H. gertschi venom glands. The
mean read length of ESTs was 919 nucleotides (ranging
from 225 to 1613 nucleotides, Figure 1). After clusterization 20 clusters showing more than one EST and 48 singlets were grouped (Table 1). Among the 147 ESTs, in

Page 2 of 12
(page number not for citation purposes)

BMC Genomics 2007, 8:119

http://www.biomedcentral.com/1471-2164/8/119

29% (4 contigs and 19 singlets) we were unable to identify any open reading frame (ORF). The remaining
sequences encode for protein precursors with an average
of 131 residues (from 66 to 285 amino acid residues
long). The complete dbEST submission with 68 nucleotide sequences and annotations is included in Additional file 2 as raw text.
Similarity searches and sequence annotation
All sequences were submitted for blastn and blastx
searches against nr database; an e-value < 10-5 was used as
cut-off for confidential homologue detection. In addition
to the ESTs for which no clear ORF have been identified,
nearly 19% of the new sequences (in 3 contigs and 10 singlets) do not match with any entry in the database. Altogether, unassigned ESTs account for close to 48% of the
total dataset, a value similar to other transcriptome studies which show values varying from 13% to 56% of non
matched sequences [26-33,35]. Noteworthy, these putative gene products signify a source of new information
about scorpion venom gland specific genes. In addition to
ESTs with no database match, 2 reads presented identity

with sequences that have been already described but with
no functional assessment, hereby named unknown proteins. One of these, HGE032|2273, is the clone which
codes for a protein similar to the CG9896-like proteins
identified in the scorpions Mesobuthus gibbosus and M.
cyprius. The other one, HGE033|2208, encodes for a scorpion homologue of short proteins conserved in eukaryotic organisms (KOG4604, pfam04418.6), but whose
function is not known yet.
The identified putative proteins (50% of the total) were
assorted into two main groups (Table 1 and Figure 2): 1)
precursors similar to gene products implicated in common cellular processes account for 18% of transcripts (in
5 contigs and 15 singlets) and; 2) putative toxins or other
venom components, representing 31% of total ESTs (in 8
contigs and 2 singlets). For most of these sequences, the
putative identity deposited into the dbEST correspond to
the eukaryotic orthologous group (KOG [38]) each would
belong (see Materials and Methods), with relevant Gene
Ontology (GO [39]) terms assigned with the aid of
AmiGO and GOblet [40] web servers.

Table 1: Identification of the transcripts predicted to be involved in common cellular processes and those similar to known venom
components. The putative identity corresponds to the eukaryotic orthologous group (KOG), as detailed in Methods.

Sequence Id

HGE001|Contig13
HGE003|Contig21
HGE004|Contig12
HGE005|Contig19
HGE006|2203
HGE007|2225
HGE008|2233
HGE009|2404
HGE010|2258
HGE011|2268
HGE012|2330
HGE013|2397
HGE014|2453
HGE015|2217
HGE017|2209
HGE018|2232
HGE020|2328
HGE021|2448
HGE022|contig17
HGE023|2323
HGE033|2208
HGE024|Contig2
HGE025|Contig5
HGE034|Hgscplike1
HGE026|Hgscplike2
HGE035|HgbetaKTx1
HGE027|NDPB_5.5
HGE028|NDPB_5.6
HGE029|NDPB_3.7
HGE031|PLA2
HGE030|Hg1

GenBank

Descriptor

Gene products predicted to be involved in common cellular processes
EL698878
KOG1376 Alpha tubulin
KOG3412 60S ribosomal protein L28
EL698880
KOG0279 G protein beta subunit-like protein
EL698881
KOG1954 Endocytosis/signaling protein EHD1
EL698882
KOG3418 60S ribosomal protein L27
EL698883
KOG3449 60S acidic ribosomal protein P2
EL698884
KOG0714 Molecular chaperone (DnaJ superfamily)
EL698944
KOG3458 NADH:ubiquinone oxidoreductase, NDUFA8/PGIV/19 kDa subunit
EL698885
KOG0863 20S proteasome, regulatory subunit alpha type PSMA1/PRE5
EL698886
KOG3311 Ribosomal protein S18 (40S)
EL698887
KOG1629 Bax-mediated apoptosis inhibitor TEGT/BI-1
EL698888
KOG0898 40S ribosomal protein S15
EL698889
KOG2597 Predicted aminopeptidase of the M17 family
EL698890
KOG3752 Ribonuclease H
EL698891
KOG0876 Manganese superoxide dismutase
EL698945
KOG2941 Beta-1,4-mannosyltransferase
EL698892
KOG4075 Cytochrome c oxidase, subunit IV/COX5b
EL698894
KOG2667 COPII vesicle protein
EL698895
KOG2403 Succinate dehydrogenase, flavoprotein subunit
EL698896
KOG2486 Predicted GTPase
EL698897
KOG4604 Uncharacterized conserved protein
EL698907
Gene products similar to known venom components
EL698898
α-KTx 6 subfamily
Novel α-KTx
EL698899
Scorpine-like group
EL698908
Scorpine-like group
EL698900
Novel β-KTx
EL698909
Novel NDBP group 5
EL698901
Novel NDBP group 5
EL698902
Novel NDBP group 3
EL698903
Novel group III heterodimeric phospholipase
EL698905
KOG4295 Serine proteinase inhibitor (KU family)
EL698904

Page 3 of 12
(page number not for citation purposes)

BMC Genomics 2007, 8:119

http://www.biomedcentral.com/1471-2164/8/119

matched ESTs as a possible source for new toxins, it can be
assumed that these molecules are preferentially expressed
over proteins related with the other cellular functions.

Figurelength
Reads
1
distribution of H. gertschi venom gland ESTs
Reads length distribution of H. gertschi venom gland
ESTs. A total of 147 ESTs were analyzed in the current
study. Abscissa is the length of sequences in 50 bp intervals,
whereas the total number of ESTs for each cluster is shown
in the Y-coordinate.

It is worth noticing that in the group of identified proteins, toxins account for 59.7% of the transcripts (30% of
the unique sequences). The distribution of all ESTs is
depicted in Figure 2, it can be observed that ESTs coding
for toxins are well represented in the H. gertschi venom
gland transcriptome. Further, considering the non-

A
Unknown
function
1.4%

GO-sorted annotated sequences
All non-toxin nr-matched gene products were annotated
in each of the three ontologies of GO: cellular component
(CC), molecular function (MF) and biological processes
(BP). Within each of these ontologies the categories with
highest prevalence are: "intracellular" (11% of total ESTs
and 19% of unique sequences), "ribosome" (4.1% and
7.4%), "mitochondrion" (4.1% and 7.4%) and "extracellular part" (6.1% and 2.9%) within CC; "catalytic activity"
(16% of total ESTs and unique sequences), "hydrolase
activity" (10.9% and 10.3%), "protein binding" (4.8%
and 10.3%) and "ion binding" (7.5% and 5.9%) within
MF, and; "primary metabolic process" (7.5% of total ESTs
and 13.2% of unique sequences), "biosynthetic process"
(4.8% and 8.8%), "transport" (4.1% and 8.8%) and
"translation" (4.1% and 7.4%) within BP (Figure 3).

Discussion
Transcriptome analysis suggest cellular processes relevant
for scorpion venom glands function
Although our sampling of the venom glands library is still
incomplete, the diversity and nature of the annotated

B

ESTs (%)
GO-sorted
17.7%
D- and E-KTx
17.7%

Unknown
function
2.9%

Unique sequences (%)
GO-sorted
29.4%

D- and E-KTx
7.4%

NDBP
7.5%

NoORF
29.9%

Other venom
components
6.1%
No match
19.7%

NDBP
4.4%
NoORF
33.8%

Other venom
components
2.9%
No match
19.1%

Figure
Relative 2proportion of each category of the transcripts from H. gertschi venom gland library
Relative proportion of each category of the transcripts from H. gertschi venom gland library. A) Relative proportion of each category of the 147 total transcripts from H. gertschi venom gland. B) Relative proportion of the unique sequences
(20 contigs and 48 singlets). "Unknown function" includes ESTs that presented identity with already described sequences with
no functional assessment. "NoORF" includes sequences with non identified open reading frame. "No match" includes ESTs that
did not match with currently known sequences. "GO-sorted" includes transcripts coding for proteins involved in cellular processes. "α and β-KTx" transcripts encode for putative K+ toxins from α and β-families, respectively. "NDBP" comprises nondisulfide-bridged peptides. "Other venom components" includes both H. gertschi PLA2 and the Kunitz-type serine proteinase
inhibitor.

Page 4 of 12
(page number not for citation purposes)

BMC Genomics 2007, 8:119

http://www.biomedcentral.com/1471-2164/8/119

GO-sorted sequence annotation
45

Number

40
35

ESTs

30

Unique sequences

25
20
15
10

om

rib
os

nr
-m
at

ch
ed

/G

O

an
no

ta

0

tio
n
To
xi
in
e
n
tra
(0
00
ce
pr
58
llu
ot
ei
la
40
n
r(
)
co
00
ex
m
0
tra
5
p
62
le
ce
x
2)
llu
(0
la
0
rp
43
m
ito
ar
23
in
ch
t(
te
4)
gr
00
st
o
n
ru
al
05
dr
ct
t
i
o
5
o
ur
76
n
m
al
(0
em
)
m
00
ol
br
57
ec
an
39
ul
e
e
)
(0
C
ac
01
at
tiv
al
60
yt
i
t
21
y
ic
(0
)
ac
00
Pr
tiv
ot
5
ity
19
ei
n
8)
(0
bi
00
nd
38
C
i
n
I
24
aon
g
H
de
(0
)
bi
yd
00
pe
nd
r
o
5
nd
in
la
5
g
15
en
se
(0
)
de
pr
ac
04
im
nt
t
3
i
vi
ar
ph
1
P
ty
67
y
LA
os
(0
m
)
2
ph
01
et
ac
ab
ol
67
t
ip
i
ol
vi
87
id
ic
ty
)
m
pr
(0
et
o
0
ab
ce
47
bi
ol
ss
49
os
ic
8)
(0
yn
pr
0
th
oc
44
et
ge
es
23
ic
s
ne
8)
pr
(0
ra
oc
00
tio
es
66
n
s
tra
of
44
(0
ns
00
pr
)
la
ec
9
05
tio
ur
re
tra
8)
n
so
sp
(0
ns
rm
on
06
po
se
et
41
r
ab
t(
to
2)
00
ol
st
ite
im
06
s
u
81
lu
an
0)
s
d
(0
en
0
50
er
gy
89
6)
(0
00
60
91
)

5

cellular component

molecular function

biological process

GO term and ID

Figure
Gene
Ontology-sorted
3
sequence annotation
Gene Ontology-sorted sequence annotation. Functional classification of all nr-matched transcripts from the H. gertschi
venom gland. The vertical axis shows the relative proportion of ESTs. The abscissa shows the categories within each of three
ontologies: cellular component, molecular function and biological processes. For comparison, the relative proportion of toxinlike ESTs is also shown. All toxin-like sequences were assigned to the special set of the "biological process" ontology called
"multi-organism process" (GO:0051704).
transcripts provide the first glimpse about molecular processes taking part in the scorpion venom gland cells. Since
we constructed a non-amplified library, it could be
expected that clone number reflects the actual prevalence
of a given transcript. Moreover, by extension, different
transcripts belonging to the same – confidentially
assigned – GO category might suggest this category as
important within the biological processes of scorpion
venom glands.
For example, intuitively, the venom glands should support high protein synthesis and secretion in order to produce the large amounts of, secreted and renewable,
venom proteins. In concordance, 8.2% of the total transcripts and 16.2% of the unique sequences match with
either ribosomal components (1 contig and 4 singlets) or

proteins involved in cellular trafficking (2 contigs and 1
singlet). Both processes are energetically costly and, consistently, 4.1% of whole ESTs and 7.4% of identified protein precursors match with components of the energyproducer organelle mitochondrion, whereas 2.7% and
4.4%, respectively, are putative homologues of proteins
directly involved in the energy-producer oxidative phosphorilation or tricarboxilyc acid cycle. Indeed, scorpions
whose venoms were artificially depleted shows increased
oxygen consumption [41].
The importance of correct protein processing in the context of scorpion venom gland is emphasized by the presence of transcripts encoding for proteins involved in
correct folding (HGE008|2233), posttranslational
processing (HGE014|2453 and HGE018|2232) or protea-

Page 5 of 12
(page number not for citation purposes)

BMC Genomics 2007, 8:119

http://www.biomedcentral.com/1471-2164/8/119

some-dependent
degradation
of
proteins
(HGE010|2258). One of these (HGE014|2453), match
with aminopeptidases of the M17 family (KOG2597),
which are exopeptidases involved in the processing and
regular turnover of intracellular proteins, although their
precise role in cellular metabolism is unclear. In particular
aminopeptidases of the M17 family cleave leucine residues from the N-terminal of polypeptide chains, but substantial rates are evident for all amino acids [42]. We
predicted, by SignalP 3.0, its signal peptide-processing
sequence (VAS-LK) suggesting that this transcript is
secreted as a venom component, and indeed it could be
important for posttranslational modifications of venomous gland components. Moreover, HGE018|2232 match
with the glycosylating enzymes β-1,4-mannosyltransferases (KOG2941); which is consistent with the presence
of glycosylated proteins in scorpion venoms (v.gr. [6]).

transposon (nLTRrt) of clade R1 (sensu [43]). This nLTRrt
clade is usually found inserted into telomeres and has
been identified in several arthropods (including one
arachnid) and some fungi [44]. It is worth noticing that
mobile elements and their remnants account for large
proportions of most eukaryotic genomes, in which they
have had central roles in genome evolution and hypervariation. The expression of transposases indicates that
mobile elements might contribute to the diversification of
venom toxins. Recently, Glushkov et al., [45] reported the
search for nLTRrt in 22 scorpion species, in which degenerate oligonucleotides based on consensus sequences of
seven clades of nLTRrt were used to a PCR-based fishing
approach. Unfortunately, even though these authors
reported that PCR products of the expected size where
obtained with R1-based degenerate primers, they only
presented data for CR1, I and Jockey nLTRrt clades.

An interesting finding in our database was a transcript
encoding the ribonuclease H domain of a non-LTR retro-

A

PSI-BLAST
e-value

HGE024|Contig2
Q10726|6.1|Pi1
P80719|6.2|MaurTx(1txm)
P59867|6.3|HsTx1(1quz)
P58498|6.4|Pi4(1n8m)
P58490|6.5|Pi7(1qky)
Q6XLL9|6.6|OcKTx1
Q6XLL8|6.7|OcKTx2
Q6XLL7|6.8|OcKTx3
Q6XLL6|6.9|OcKTx4
Q6XLL5|6.10|OcKTx5
P0C194|6.11|IsTx(1wmt)
P0C166|6.12|AnurocTx
P84094|6.13|Spinoxin(1v56)
P84864|6.14|HgeTx1

|
10
|
20
|
30
|
40
|
-ETLFTANCLDRKDCKKHC-KSKGCKEMKCEQIIKPTWRCLCIM-CSK------VKCRGTSDCGRPCQQQTGCPNSKCIN-----RMCKCYG-C--------VSCTGSKDCYAPCRKQTGCPNAKCIN-----KSCKCYG-C--------ASCRTPKDCADPCRKETGCPYGKCMN-----RKCKCNR-C-----IEAIRCGGSRDCYRPCQKRTGCPNAKCIN-----KTCKCYG-CS----DEAIRCTGTKDCYIPCRYITGCFNSRCIN-----KSCKCYG-CT----AEVIKCRTPKDCAGPCRKQTGCPHGKCMN-----RTCRCNR-C-----AEVIKCRTPKDCADPCRKQTGCPHGKCMN-----RTCRCNR-C-----AEVIKCRTPKDCAGPCRKQTGCPHAKCMN-----KTCRCHR-C-----AEIIRCSGTRECYAPCQKLTGCLNAKCMN-----KACKCYG-CV----AEVIRCSGSKQCYGPCKQQTGCTNSKCMN-------CKCYG-C----VHTNIPCRGTSDCYEPCEKKTNCARAKCMN-----RHCNCYNNCPW-----QKECTGPQHCTNFCRKNK-CTHGKCMN-----RKCKCFN-CK-------IRCSGSRDCYSPCMKQTGCPNAKCIN-----KSCKCYG-C------TGTSCISPKQCTEPCRAK-GCKHGKCMN-----RKCHCML-CL--

0.15
0.14
0.49
0.005
0.033
7e-12
2e-12
3e-12
7e-06
2e-05
5e-07
>0.5
0.076
0.33

HGE025|Contig5
P0C166|6.12|AnurocTx

DTMKKRSDYCSNDFCFFSCRRDR-CARGDCEN-----GKCVCKN-CHLN
-----QKECTGPQHCTNFCRKNK-CTHGKCMN-----RKCKCFN-CK--

1.1*

B
Hg scorpine like 2
P56972|Scorpine
Q5WR03|Opiscorpine1|ts
Q5WR02|Opiscorpine2|ts
Q5WQZ7|Opiscorpine3|ts
Q5WQZ9|Opiscorpine4|ts
Q0GY40|HgeScpl-1
Q0GY41|HgeEKTx

|

10

|

20

|

30

|

40

|

50

|

60

|

70

|

%Identity
with Scorpine
YAHKAIDVLTPMIGVPVVSKIVNNAAKQLVHKIAKNQQLCMFNKDVAGWCEKSCQQSAHQKGYCHGTKCKCGIPLNYK
46
GWINEEKIQKKIDERMGNTVLGGMAKAIV-HKMAKNEFQCMANMDMLGNCEKHCQ-TSGEKGYCHGTKCKCGTPLSY- 100
KWFNEKSIQNKIDEKIGKNFLGGMAKAVV-HKLAKNEFMCVANVDMTKSCDTHCQKASGEKGYCHGTKCKCGVPLSY70
KWLNEKSIQNKIDEKIGKNFLGGMAKAVV-HKLAKNEFMCMANMDPTGSCETHCQKASGEKGYCHGTKCKCGVPLSY73
70
KWLNEKSIQNKIDEKIGKNFLGGMAKAVV-HKLAKNEFMCVANVDMTKSCDTHCQKASGEKGYCHGTKCKCGVPLSY70
KWLNEKSIQNKIDEKIGKNFLGGMAKAVV-HKLAKNEFMCVANIDMTKSCDTHCQKASGEKGYCHGTKCKCGVPLSY51
GWMSEKKVQGILDKKLPEGIIRNAAKAIV-HKMAKNQFGCFANVDVKGDCKRHCK-AEDKEGICHGTKCKCGVPISYL
26
----KSTVGQKLKKKLNQ--AVDKVK----EVLNKSEYMCPV---VSSFCKQHCA-RLGKSGQCDLLECICS------

Figure 4 toxin-like precursors in H. gertschi venom gland library
Scorpion
Scorpion toxin-like precursors in H. gertschi venom gland library. A) Predicted amino acid sequences of the potential
α-KTx. HGE024|Contig2 predicted sequence is aligned with all members of the α-KTx 6 subfamily. HGE025|Contig5 is aligned
with anuroctoxin (α-KTx 6.12). PSI-BLAST e-values for the third iteration are shown. B) Predicted amino acid sequence of Hg
scorpine like 2 and its alignment with others members of the scorpine-like group. The percentage of identity with scorpine is
shown. See Supplementary Figure 1 for the complete nucleotide sequences of HGE024|Contig2, HGE025|Contig5 and Hg
scorpine like 2. Each sequence starts with its SwissProt accession number followed by common names and Protein Data Bank
codes between parentheses (where available). Systematic numbering (sensu [47,49]) for α-KTx is included between accession
numbers and common names. Identical amino acids are in red colour and conserved ones in green.

Page 6 of 12
(page number not for citation purposes)

BMC Genomics 2007, 8:119

http://www.biomedcentral.com/1471-2164/8/119

Toxins and other venom components
Our H. gertschi scorpion venom gland library is clearly
enriched on toxin-like sequences, with more than 17% (in
4 contigs and 1 singlet) of the sequenced ESTs being similar to known families of scorpion toxins. Another 14% of
the total ESTs (in 4 contigs) encodes for precursors which
are homologues of previously characterized non-toxin
scorpion venom components (see below). Considering
that all these sequences contain putative signal peptides –
identified by SignalP 3.0 [46] – and their relative abundance, we suggest that these ESTs may encode secreted
venom components. In fact, 3 of these clusters encode
peptides already found in the venom of H. gertschi, which
are currently being studied by our group [24 and unpublished].

α-KTxs
Two clusters encoding potential α-KTx peptides [47-49]
were found and their translated sequences are shown in
Figure 4 (and Supplementary Figure 1 in Additional file
1). One of those (HGE024|Contig2) is composed by 2
reads, and the other one (HGE025|Contig5) by 17 reads.
Although the blastx search against public databases
showed that HGE024|Contig2 sequence presents poor evalues (> 10-5) with haemocyte defensins of insects and
with some OcKTx's – predicted K+ channel toxins from the

A
HGE027|NDBP 5.5|
HGE028|NDBP 5.6|
Q8MMJ7|IsCT
Q8MTX2|IsCT2
Q9GQW4|BmKn1
Q6JQN2|BmKn2

scorpion Opistophthalmus carinatus [50], PSI-BLAST [51]
with the translated sequence retrieved most of the members of the α-KTx 6 subfamily (see [1,47-49]) within the
first three iterations with good expectance values. Therefore, we propose that HGE024|Contig2 constitutes the
precursor of a novel member of this subfamily of K+ channel blockers. Similarly, the search of HGE025|Contig5
sequence against database revealed low similarity with
anuroctoxin (α-KTx 6.12) from the scorpion Anuroctonus
phaiodactylus, a high-affinity blocker of Kv1.3 channels of
human T lymphocytes [52]. Again, the expectancy values
were rather poor, but in this case, we were already able to
purify the mature peptide from the venom of H. gertschi,
and it is now under study. The prediction of its signal peptide and the N-terminal amino acid sequence determined
by automatic Edman degradation (data not shown) reveal
that this toxin is in fact produced as a propeptide. This
encode for a 67 amino acid-long peptide, containing three
segments: an N-terminal signal peptide of 25 amino acid
residues, a putative propeptide of 6-amino acids and a
mature peptide containing 36 residues (Supplementary
Figure 1B in Additional file 1). The mature peptide
encoded by HGE025|Contig5 shows several conserved
features of α-KTx peptides, nonetheless its sequence is
quite unique. We suspect that it might be the first member

%Identity
|
10 |
20 |
30 |
40 |
50 |
60 |
70
IsCT
MKTQFIVLIVAIVFLQLLSQSEAIFSAIAGLLSNLLGKRDLRH-LDLDQFDDMFDQPEISAADMKFLQDLLR-49
MKTQVIIFIMAVVFLQLLSQSEAF---IFDLLKKLVGKRELRN-IDLDQFDDMFDEPEISAADMRFLQELLK-46
MKTQFAILLVALVLFQMFAQSDAILGKIWEGIKSLFGKRGLS---DLDGLDELFDG-EISKADRDFLRELMR-- 100
MKTQFAILLVALVLFQMFAQSEAIFGAIWNGIKSLFGRRALNNDLDLDGLDELFDG-EISQADVDFLKELMR-81
MKSQTFFLLFLVVLLLAISQSEAFIGAVAGLLSKIFGKRSMR---DMDTMKYLYDP-SLSAADLKTLQKLMENY
36
37
MKSQTFFLLFLVVLLLAISQSEAFIGAIANLLSKIFGKRSMR---DMDTMKYLYDP-SLSAADLKTLQKLMENY

B
HGE029|NDBP 3.7|
P82656|Hadrurin
P83239|Pandinin-1
P83312|Parabutoporin
Q9Y0X4|BmK3
Q5VJS8|Opistoporin3

|
10 |
20 |
30 |
40 |
50 |
60
-GWWNAFKSIGKKLLKSKLAKDITKMAKQRAKEYVVKKLNGPPEEEVAAIDALMNSLDYG-ILDTIKSIASKVWNSKTVQDLKRKGIN----WVANKLGVSPQAA-------------GKVWDWIKSAAKKIWSSEPVSQLKGQVLNAAKNYVAEKIGATPT-------------------FKLGSFLKKAWKSKLAKKLRAKGKEMLKDYAKGLLEGGSEE--VPGQ------------FRFGSFLKKVWKSKLAKKLRSKGKQLLKDYANKVLNGPEEEAAAPAERRR-----GKVWDWIKSTAKKLWNSEPVKELKNTALNAAKNLVAEKIGATPSEAGQMPFDEFMDILYE

%Identity
NDBP 3.7
100
21
22
27
38
32

Figure
Predicted
5 amino acid sequences of the novel non-disulfide-bridged peptides (NDBP)
Predicted amino acid sequences of the novel non-disulfide-bridged peptides (NDBP). A) NDBP-5.5 and NDBP-5.6
are aligned with others scorpion cytolytic peptides; the percentage of identity with IsCT is shown. Putative signal peptides are
in italics, whereas identified C-terminal prosequences and mature forms are underlined or in bold characters, respectively. B)
Alignment of NDBP-3.7 with members of the NDBP 3 subfamily. See Supplementary Figure 2 for the complete nucleotide
sequences encoding for NDBP-5.5, NDBP-5.6 and NDBP-3.7. Each sequence starts with its SwissProt accession number followed by common names. Identical amino acids are in red colour and conserved ones in green.

Page 7 of 12
(page number not for citation purposes)

BMC Genomics 2007, 8:119

http://www.biomedcentral.com/1471-2164/8/119

of a new αKTx subfamily, but this remains to be clarified
by ongoing analyses.

β-KTx and scorpine-like peptides
One cluster (2 reads) coding the HgeβKTx and another (4
reads) coding the Hge scorpine like were identified in the
transcriptome of H. gertschi and their sequence have
already been reported [24]. Here we present a distinct EST,
homologous to the scorpine-like group of long-chain
three disulphide-bridged scorpion venom peptides,
named Hge scorpine like 2 (Figure 4b and Supplementary
Figure 1C in Additional file 1).
Cytolytic peptides
Two clusters encoding IsCT-like precursors were found in
H. gertschi transcriptome. IsCT and IsCT2 are antimicrobial linear peptides isolated from the scorpion Opisthacanthus madagascariensis [53]. They possess broad activity
spectra against Gram positive and negative bacteria as well
as fungi and relatively weak haemolytic activity against
sheep red blood cells. Additionally to the signal peptide,
their precursors contain an uncommon acidic propeptide
at the C-terminal (Supplementary Figure 2A in Additional
file 1). Figure 5a shows both IsCT-like translated
sequences, the more abundant comprising 7 reads and the
other one represented by 2 reads, classified as nondisulfide-bridged peptides (NDBP) NDBP-5.5 and NDBP5.6, respectively (following the nomenclature rules of
[7]).
Bradykinin-potentiating peptide like
One cluster (HGE029|NDBP_3.7, 2 reads; see Supplementary Figure 2B in Additional file 1) encodes a homo-

logue of the bradykinin-potentiating peptide precursor
(BmK3 or BmKpbb) from the scorpion Mesobuthus martensii, classified as NDBP-3.3 [7]. The angiotensin-bradykinin system is a central hormonal system for the
regulation of blood pressure. The angiotensin-converting
enzyme (ACE) converts angiotensin I to angiotensin II
and degrades bradykinin. Bradykinin potentiating peptides have been isolated from Tityus serrulatus (peptide T
[54]) and Buthus occitanus (K12 [55]). Peptide T, a 13amino acid linear peptide, potentiates the contractile
activity of bradykinin on isolated smooth muscle, inhibits
the hydrolysis of bradykinin by ACE, and enhances the
depressor effect of bradykinin on arterial blood pressure
in the anesthetized rats [54]. Peptide K12 displays similar
bradykinin potentiating activities [55]. BmKbpp was identified from B. martensii Karsch by cDNA cloning based on
the peptide K12 amino acid sequence [56]. The last 21 residues of C-terminal region of BmKbpp showed 57% similarity with peptide K12. Based on the fact that BmKbpp
also exhibits high similarity with parabutoporin and others antimicrobial peptides from scorpions, it was suggested that BmKbpp may be a molecule with a dualfunction, and that the BmKbpp precursor may be processed in two alternative ways to produces two different
mature molecules: BmKbpp and a peptide with only the
C-terminal 21 residues of BmKbpp [7]. Figure 5b shows
the bradykinin-potentiating peptide like from H. gertschi,
here named NDBP-3.7.
Phospholipases
A cluster (8 reads) of a new homologue of scorpion
venom phospholipases A2 (ScpPLA2) was identified in
the H. gertschi library (see Supplementary Figure 3 in

HGEO31|PLA2_Hadge
P59888|Imparatoxin I
Q6PXP0|Phospholipin
Q3YAU5|PLA2_Hetfu|ts
Q6T178|PLA2_Mesta|ts

|
10 |
20 |
30 |
40 |
50 |
60 |
70 |
80
--TVLGTKWCGAGNEAANYSDLGYFNNVDRCCREHDHCDNIPAGETKYGLKNEGTYTMMNCKCEKAFDKCLSDISG------TMWGTKWCGSGNEATDISELGYWSNLDSCCRTHDHCDNIPSGQTKYGLTNEGKYTMMNCKCETAFEQCLRNVTG----FLIVSGTKWCGNNNIAANYSDLG-FLEADKCCRDHDHCDHIASGETKYGLENKGLFTILNCDCDEAFDHCLKEISNNVTTD
--TMWGTKWCGSGNKAINYTDLGYFSNLDSCCRTHDHCDNIAAGETKYGLTNEGKYTMMNCKCEATFQQCLRDVHG------TMWGTKWCGSGNEAINYTDLGYFSNLDSCCRTHDHCDSIPAGETKYGLTNEGKYTMMNCKCESAFEKCLRDVRG-----

HGEO31|PLA2_Hadge
P59888|Imparatoxin I
Q6PXP0|Phospholipin
Q3YAU5|PLA2_Hetfu|ts
Q6T178|PLA2_Mesta|ts

BLAST
|
90 |
100 |
110 |
120 |
130 |
140 e-value
YFTRKAVSAVKFTYFTLYGNGCYNVKCEngr--spSNECPNGVAEYTGETGLGAkvinfgkGMEGPAAGFVRKTYFDLYGNGCYNVQCPSQrrlarSEECPDGVATYTGEAGYGAWAINKLNG 5e-40
IRQKGGAENVWRFYFQWYNANCYRLYCKdek-sarDEACTNQYAVVKKN-----FTVQ---- 1e-23
PLEGKAAFTIRKLYFGLYGNGCFNVQCPSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa 2e-31
ILEGKAAAAVRKTYFDLYGNGCFNVKCPSgarsarSEECTNGMATYTGETGYGAWAINKLNG 3e-43

Figure 6mature sequence of phospholipase A2 precursor
Putative
Putative mature sequence of phospholipase A2 precursor. Predicted amino acid sequence of H. gertschi PLA2
(HGE031|PLA2) aligned with other scorpion venom PLA2. BLAST e-values are shown. See Supplementary Figure 3 for the
nucleotide sequence of HGE031|PLA2. Each sequence starts with its SwissProt accession number followed by common names.
Identical amino acids are in red colour and conserved ones in green.

Page 8 of 12
(page number not for citation purposes)

BMC Genomics 2007, 8:119

http://www.biomedcentral.com/1471-2164/8/119

| 10 | 20 | 30 | 40 | 50 | 60 |
HGE030|Hg1|
GHHNRVNCLLPPKTGPCKGSFARYYFDIETGSCKAFIYGGCEGNSNNFSEKHHCEKRCRGFRKFGGK
P68425|Huwentoxin-XI ----IDTCRLPSDRGRCKASFERWYFNGRT--CAKFIYGGCGGNGNKFPTQEACMKRCAKA-----P31713|SHPI-1
-----SICSEPKKVGRCKGYFPRFYFDSETGKCTPFIYGGCGGNGNNFETLHQCRAICRA------P00981|Dendrotoxin-K ---AAKYCKLPLRIGPCKRKIPSFYYKWKAKQCLPFDYSGCGGNANRFKTIEECRRTCVG------P0C1X2|Conkunitzin-S1 -KDRPSLCDLPADSGSGTKAEKRIYYNSARKQCLRFDYTGQGGNENNFRRTYDCQRTCLYT------

BLAST
e-value
9e-9
3e-7
4e-7
2e-4

Figure 7sequence alignment of the KU-type proteins of venomous organisms
Multiple
Multiple sequence alignment of the KU-type proteins of venomous organisms. Predicted amino acid sequence of
HGE030|Hg1 aligned with other venom-derived members of the Kunitz-type serine proteinase inhibitors. BLAST e-values with
P68425 (spider Ornithoctonus huwena), P31713 (sea anemone Stichodactyla helianthus), P00981 (snake Dendroaspis polylepis
polylepis) and P0C1X2 (cone snail Conus striatus) are shown. See Supplementary Figure 4 for the complete nucleotide sequence
of HGE030|Hg1. Each sequence starts with its SwissProt accession number followed by common names. Identical amino acids
are in red colour and conserved ones in green.

Additional file 1). The mature form of ScpPLA2 are composed by two subunits, the large ones consisting of
approximately 105 amino acid residues, whereas the
small subunits have between 18 and 27 residues; their
heterodimeric form is stabilized by one interchain disulphide bridge [5,6]. The ScpPLA2 are expressed from a single message, from which the N-terminal propeptide, a
penta or hexapeptide internal segment and a short C-terminal region are excised to give the heterodimeric mature
form of the enzyme. In Figure 6, these regions are identified on the sequence of the predicted H. gertschi PLA2; the
assignment was based on multiple sequence alignment of
known ScpPLA2. PLA2s are enzymes that catalyze the
hydrolysis of the sn-2 acyl bonds of sn-3 phospholipids,
and are normal cellular mediators involved in different
responses, such as inflammation, blood hemostasis and
others. Many animal venoms posses PLA2s that mediate
several toxic responses, like cytotoxicity, neurotoxicity,
myotoxicity, edema and blood coagulation disturbs.
Based on their primary structure, these toxins can be classified in tree distinct classes: class I is found in Elapidae
snakes venom; class II is found in the Viperidae family of
snakes; and class III that was identified for the first time in
the bee venom. Latter they were found in other invertebrates such as jellyfish, marine snails, and scorpion venoms, but they are also present in vertebrates, like the
venomous lizard Heloderma [57].
Kunitz-type carboxypeptidase inhibitor
One EST (HGE030|Hg1 (Supplementary Figure 4 in Additional file 1), is homologous to KOG4295, which contains serine proteinase inhibitors of the Kunitz type (KU
family). Proteins with KU have been identified in several
venomous organisms, like snakes [58], sea anemones

[59], cone snails [60] and spiders [61]. However, this is
the first report of a KU-type precursor in scorpions. Figure
7 shows the multiple sequence alignment of
HGE030|Hg1 with other KU-type venom components.
Although the precise role of HGE030|Hg1 in the context
of scorpion venom remains to be determined – whether it
display neurotoxic or proteinase inhibitor activity –, the
ubiquitous presence of proteinase inhibitors suggest a
common trend in venomous organisms, deserving further
studies.

Conclusion
Gene cloning of animal toxins has been extensively performed by PCR method, using primers deduced from
direct protein sequencing, usually by Edman degradation
or mass spectrometry analysis. These studies are aimed at
the isolation of specific active components. However, this
approach is not entirely suitable for search of unforeseen
components that could be present in the venomous gland
under study. The strategy is biased by the fact that only
those genes that are sharing sequence similarities are usually discovered by this technique. For this reason, we
adopted the molecular approach of generating and analyzing ESTs from the H. gertschi venom gland as the strategy to produce a general overview of the venom gland
transcriptome. This strategy confirms the highly specialized nature of scorpion venom glands as toxin-producer,
allowing the description, for the first time, of putative proteins that certainly are involved in cellular processes relevant for the venom glands' function. Additionally, the
unguided mining also reveals novel predicted venom
c

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DRAMP", "db_subject_text": "No MICs found in DRAMP database", "db_measure": "Antimicrobial, Antibacterial", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DRAMP", "db_subject_text": "No MICs found in DRAMP database", "db_measure": "Antimicrobial, Antibacterial", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DRAMP", "db_subject_text": "Yeasts", "db_measure": "Antimicrobial, Antibacterial, Antifungal", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DRAMP", "db_subject_text": "No MICs found in DRAMP database", "db_measure": "Unknown", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DRAMP", "db_subject_text": "No MICs found in DRAMP database", "db_measure": "Antimicrobial, Antibacterial", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "DRAMP", "db_subject_text": "No MICs found in DRAMP database", "db_measure": "Antimicrobial, Antibacterial", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DRAMP", "db_subject_text": "No MICs found in DRAMP database", "db_measure": "Antimicrobial, Antibacterial", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DRAMP", "db_subject_text": "Yeasts", "db_measure": "Antimicrobial, Antibacterial, Antifungal", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "dbAMP", "db_subject_text": "", "db_measure": "Antibacterial AntiGram + AntiGram - Antimicrobial", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "dbAMP", "db_subject_text": "Yeasts", "db_measure": "Antibacterial Antimicrobial Antifungal", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "dbAMP", "db_subject_text": "Bacillus subtilis (MIC=0.5μM)", "db_measure": "Antibacterial AntiGram + Antimicrobial MammalianCells", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "dbAMP", "db_subject_text": "Mycobacterium abscessus subsp. massiliense CRM0020 (MBC=200μM)\nMycobacterium abscessus subsp. massiliense GO06 (MBC=200μM)", "db_measure": "Antibacterial AntiGram + AntiGram - Antimicrobial MammalianCells", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 12, "database": "dbAMP", "db_subject_text": "", "db_measure": "Antibacterial AntiGram + Antimicrobial MammalianCells", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 13, "database": "dbAMP", "db_subject_text": "", "db_measure": "Nonrecorded", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).