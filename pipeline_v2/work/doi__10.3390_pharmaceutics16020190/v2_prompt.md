
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
doi__10.3390_pharmaceutics16020190

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Residues in ACE2-PEP-S2 and SPIKE-PEP-S2 complexes with H-bonds and salt bridges of >10% occupancy throughout MD simulation.", "footnotes": [], "header_rows": [["ACE2-PEP-S2", "SPIKE-PEP-S2"], ["H-Bonds"], ["Donor", "Acceptor", "Occupancy", "Donor", "Acceptor", "Occupancy"]], "longform_cells": [{"table_index": 1, "row_index": 4, "col_index": 2, "row_label": "Ala16-PEP", "col_header": "Acceptor", "value": "Asp30-ACE2"}, {"table_index": 1, "row_index": 4, "col_index": 3, "row_label": "Ala16-PEP", "col_header": "Occupancy", "value": "93.72%"}, {"table_index": 1, "row_index": 4, "col_index": 4, "row_label": "Ala16-PEP", "col_header": "Donor", "value": "Arg42-PEP"}, {"table_index": 1, "row_index": 4, "col_index": 5, "row_label": "Ala16-PEP", "col_header": "Acceptor", "value": "Glu484-SPIKE"}, {"table_index": 1, "row_index": 4, "col_index": 6, "row_label": "Ala16-PEP", "col_header": "Occupancy", "value": "97.74%"}, {"table_index": 1, "row_index": 5, "col_index": 2, "row_label": "Thr15-PEP", "col_header": "Acceptor", "value": "Asp30-ACE2"}, {"table_index": 1, "row_index": 5, "col_index": 3, "row_label": "Thr15-PEP", "col_header": "Occupancy", "value": "93.28%"}, {"table_index": 1, "row_index": 5, "col_index": 4, "row_label": "Thr15-PEP", "col_header": "Donor", "value": "Thr500-SPIKE"}, {"table_index": 1, "row_index": 5, "col_index": 5, "row_label": "Thr15-PEP", "col_header": "Acceptor", "value": "Asp31-PEP"}, {"table_index": 1, "row_index": 5, "col_index": 6, "row_label": "Thr15-PEP", "col_header": "Occupancy", "value": "30.33%"}, {"table_index": 1, "row_index": 6, "col_index": 2, "row_label": "Lys26-ACE2", "col_header": "Acceptor", "value": "Asp31-PEP"}, {"table_index": 1, "row_index": 6, "col_index": 3, "row_label": "Lys26-ACE2", "col_header": "Occupancy", "value": "65.47%"}, {"table_index": 1, "row_index": 6, "col_index": 4, "row_label": "Lys26-ACE2", "col_header": "Donor", "value": "Phe1-PEP"}, {"table_index": 1, "row_index": 6, "col_index": 5, "row_label": "Lys26-ACE2", "col_header": "Acceptor", "value": "Asn501-SPIKE"}, {"table_index": 1, "row_index": 6, "col_index": 6, "row_label": "Lys26-ACE2", "col_header": "Occupancy", "value": "22.97%"}, {"table_index": 1, "row_index": 7, "col_index": 2, "row_label": "Gly5-PEP", "col_header": "Acceptor", "value": "Ala387-ACE2"}, {"table_index": 1, "row_index": 7, "col_index": 3, "row_label": "Gly5-PEP", "col_header": "Occupancy", "value": "64.17%"}, {"table_index": 1, "row_index": 7, "col_index": 4, "row_label": "Gly5-PEP", "col_header": "Donor", "value": "Arg42-PEP"}, {"table_index": 1, "row_index": 7, "col_index": 5, "row_label": "Gly5-PEP", "col_header": "Acceptor", "value": "Gly482-SPIKE"}, {"table_index": 1, "row_index": 7, "col_index": 6, "row_label": "Gly5-PEP", "col_header": "Occupancy", "value": "20.09%"}, {"table_index": 1, "row_index": 8, "col_index": 2, "row_label": "Arg42-PEP", "col_header": "Acceptor", "value": "Glu37-ACE2"}, {"table_index": 1, "row_index": 8, "col_index": 3, "row_label": "Arg42-PEP", "col_header": "Occupancy", "value": "62.71%"}, {"table_index": 1, "row_index": 8, "col_index": 4, "row_label": "Arg42-PEP", "col_header": "Donor", "value": "Phe1-PEP"}, {"table_index": 1, "row_index": 8, "col_index": 5, "row_label": "Arg42-PEP", "col_header": "Acceptor", "value": "Gln498-SPIKE"}, {"table_index": 1, "row_index": 8, "col_index": 6, "row_label": "Arg42-PEP", "col_header": "Occupancy", "value": "19.83%"}, {"table_index": 1, "row_index": 9, "col_index": 2, "row_label": "Arg14-PEP", "col_header": "Acceptor", "value": "Asp30-ACE2"}, {"table_index": 1, "row_index": 9, "col_index": 3, "row_label": "Arg14-PEP", "col_header": "Occupancy", "value": "62.67%"}, {"table_index": 1, "row_index": 9, "col_index": 4, "row_label": "Arg14-PEP", "col_header": "Donor", "value": "Asn450-SPIKE"}, {"table_index": 1, "row_index": 9, "col_index": 5, "row_label": "Arg14-PEP", "col_header": "Acceptor", "value": "Met44-PEP"}, {"table_index": 1, "row_index": 9, "col_index": 6, "row_label": "Arg14-PEP", "col_header": "Occupancy", "value": "19.13%"}, {"table_index": 1, "row_index": 10, "col_index": 2, "row_label": "Trp4-PEP", "col_header": "Acceptor", "value": "Gln388-ACE2"}, {"table_index": 1, "row_index": 10, "col_index": 3, "row_label": "Trp4-PEP", "col_header": "Occupancy", "value": "36.05%"}, {"table_index": 1, "row_index": 10, "col_index": 4, "row_label": "Trp4-PEP", "col_header": "Donor", "value": "Asn39-PEP"}, {"table_index": 1, "row_index": 10, "col_index": 5, "row_label": "Trp4-PEP", "col_header": "Acceptor", "value": "Glu484-SPIKE"}, {"table_index": 1, "row_index": 10, "col_index": 6, "row_label": "Trp4-PEP", "col_header": "Occupancy", "value": "17.19%"}, {"table_index": 1, "row_index": 11, "col_index": 2, "row_label": "Lys353-ACE2", "col_header": "Acceptor", "value": "Leu43-PEP"}, {"table_index": 1, "row_index": 11, "col_index": 3, "row_label": "Lys353-ACE2", "col_header": "Occupancy", "value": "27.77%"}, {"table_index": 1, "row_index": 11, "col_index": 4, "row_label": "Lys353-ACE2", "col_header": "Donor", "value": "Gln498-SPIKE"}, {"table_index": 1, "row_index": 11, "col_index": 5, "row_label": "Lys353-ACE2", "col_header": "Acceptor", "value": "Asp31-PEP"}, {"table_index": 1, "row_index": 11, "col_index": 6, "row_label": "Lys353-ACE2", "col_header": "Occupancy", "value": "14.91%"}, {"table_index": 1, "row_index": 12, "col_index": 2, "row_label": "Tyr33-PEP", "col_header": "Acceptor", "value": "Asp30-ACE2"}, {"table_index": 1, "row_index": 12, "col_index": 3, "row_label": "Tyr33-PEP", "col_header": "Occupancy", "value": "15.81%"}, {"table_index": 1, "row_index": 12, "col_index": 4, "row_label": "Tyr33-PEP", "col_header": "Donor", "value": "Asn501-SPIKE"}, {"table_index": 1, "row_index": 12, "col_index": 5, "row_label": "Tyr33-PEP", "col_header": "Acceptor", "value": "Phe1-PEP"}, {"table_index": 1, "row_index": 12, "col_index": 6, "row_label": "Tyr33-PEP", "col_header": "Occupancy", "value": "14.73%"}, {"table_index": 1, "row_index": 13, "col_index": 2, "row_label": "Trp4-PEP", "col_header": "Acceptor", "value": "Ala387-ACE2"}, {"table_index": 1, "row_index": 13, "col_index": 3, "row_label": "Trp4-PEP", "col_header": "Occupancy", "value": "15.35%"}, {"table_index": 1, "row_index": 13, "col_index": 4, "row_label": "Trp4-PEP", "col_header": "Donor", "value": "Tyr33-PEP"}, {"table_index": 1, "row_index": 13, "col_index": 5, "row_label": "Trp4-PEP", "col_header": "Acceptor", "value": "Gln498-SPIKE"}, {"table_index": 1, "row_index": 13, "col_index": 6, "row_label": "Trp4-PEP", "col_header": "Occupancy", "value": "12.20%"}, {"table_index": 1, "row_index": 14, "col_index": 4, "row_label": "", "col_header": "Donor", "value": "Thr15-PEP"}, {"table_index": 1, "row_index": 14, "col_index": 5, "row_label": "", "col_header": "Acceptor", "value": "Gly446-SPIKE"}, {"table_index": 1, "row_index": 14, "col_index": 6, "row_label": "", "col_header": "Occupancy", "value": "11.32%"}, {"table_index": 1, "row_index": 15, "col_index": 4, "row_label": "", "col_header": "Donor", "value": "Asn39-PEP"}, {"table_index": 1, "row_index": 15, "col_index": 5, "row_label": "", "col_header": "Acceptor", "value": "Glu484-SPIKE"}, {"table_index": 1, "row_index": 15, "col_index": 6, "row_label": "", "col_header": "Occupancy", "value": "10.58%"}, {"table_index": 1, "row_index": 17, "col_index": 2, "row_label": "Residues", "col_header": "Acceptor", "value": "Occupancy"}, {"table_index": 1, "row_index": 17, "col_index": 3, "row_label": "Residues", "col_header": "Occupancy", "value": "Residues"}, {"table_index": 1, "row_index": 17, "col_index": 4, "row_label": "Residues", "col_header": "Donor", "value": "Occupancy"}, {"table_index": 1, "row_index": 18, "col_index": 2, "row_label": "Asp31-PEP/Lys26-ACE2", "col_header": "Acceptor", "value": "82.18%"}, {"table_index": 1, "row_index": 18, "col_index": 3, "row_label": "Asp31-PEP/Lys26-ACE2", "col_header": "Occupancy", "value": "Glu484-SPIKE/Arg42-PEP"}, {"table_index": 1, "row_index": 18, "col_index": 4, "row_label": "Asp31-PEP/Lys26-ACE2", "col_header": "Donor", "value": "93.90%"}, {"table_index": 1, "row_index": 19, "col_index": 2, "row_label": "Asp30-ACE2/Arg14-PEP", "col_header": "Acceptor", "value": "68.21%"}, {"table_index": 1, "row_index": 20, "col_index": 2, "row_label": "Glu37-ACE2/Arg42-PEP", "col_header": "Acceptor", "value": "61.13%"}]}]

=== PRIMARY PAPER FULL TEXT (context only) ===
Use this ONLY to (a) confirm whether an organism/target/assay was tested in this paper (prevents false 'absent' calls), and (b) read an endpoint label. You may NOT cite full text as the `evidence` cell for is_database_error=true; that still requires a structured longform cell.
pharmaceutics
Article

Antiviral Action against SARS-CoV-2 of a Synthetic Peptide
Based on a Novel Defensin Present in the Transcriptome of the
Fire Salamander (Salamandra salamandra)
Ana Luisa A. N. Barros 1,2 , Vladimir C. Silva 3 , Atvaldo F. Ribeiro-Junior 1 , Miguel G. Cardoso 1,4 ,
Samuel R. Costa 5 , Carolina B. Moraes 6 , Cecília G. Barbosa 7 , Alex P. Coleone 8 , Rafael P. Simões 9 ,
Wanessa F. Cabral 1 , Raul M. Falcão 10 , Andreanne G. Vasconcelos 1,11 , Jefferson A. Rocha 12 ,
Daniel D. R. Arcanjo 13 , Augusto Batagin-Neto 8,14 , Tatiana Karla S. Borges 1 , João Gonçalves 4 ,
Guilherme D. Brand 5 , Lucio H. G. Freitas-Junior 7 , Peter Eaton 15,16 , Mariela Marani 17 , Massuo J. Kato 18 ,
Alexandra Plácido 15 and José Roberto S. A. Leite 1, *
1

2

3

4

5

6

Citation: Barros, A.L.A.N.; Silva, V.C.;

7

Ribeiro-Junior, A.F.; Cardoso, M.G.;
Costa, S.R.; Moraes, C.B.; Barbosa,
C.G.; Coleone, A.P.; Simões, R.P.;

8

Cabral, W.F.; et al. Antiviral Action
against SARS-CoV-2 of a Synthetic

9

Peptide Based on a Novel Defensin
Present in the Transcriptome of the

10

Fire Salamander (Salamandra
salamandra). Pharmaceutics 2024, 16,

11

190. https://doi.org/10.3390/
pharmaceutics16020190

12

Academic Editor: Giancarlo Morelli

13

Received: 14 December 2023

14

Revised: 19 January 2024

15

Accepted: 26 January 2024
Published: 29 January 2024
16
17

Copyright: © 2024 by the authors.

18

Licensee MDPI, Basel, Switzerland.
This article is an open access article

*

Núcleo de Pesquisa em Morfologia e Imunologia Aplicada, NuPMIA, Faculdade de Medicina,
Universidade de Brasília, UnB, Brasília 70910-900, DF, Brazil; analuisaanbarros@gmail.com (A.L.A.N.B.);
atvaldo.junior@aluno.unb.br (A.F.R.-J.); mgcardoso@ff.ulisboa.pt (M.G.C.); wanessa.felix@unb.br (W.F.C.);
andreannegv@gmail.com (A.G.V.); tatianakarlab@gmail.com (T.K.S.B.)
Programa de Pós-graduação em Medicina Tropical, PGMT, Faculdade de Medicina, Universidade de Brasília,
UnB, Brasília 70910-900, DF, Brazil
Laboratório de Vigilância Genômica e Biologia Molecular-Fundação Oswaldo Cruz Piauí,
Teresina 64001-350, PI, Brazil; vladimir.costa@fiocruz.br
imed.ULisboa-Research Institute for Medicines, Faculty of Pharmacy, University of Lisbon,
1649-003 Lisbon, Portugal; jgoncalv@ff.ulisboa.pt
Instituto de Química, IQ, Universidade de Brasília, UnB, Brasília 70910-900, DF, Brazil;
samuel.r.costa@hotmail.com (S.R.C.); gdbrand@gmail.com (G.D.B.)
Department of Pharmaceutical Sciences, Federal University of São Paulo, Diadema 09913-030, SP, Brazil;
carolinaborsoi@gmail.com
Department of Microbiology, Institute of Biomedical Sciences, University of Sao Paulo,
São Paulo 05508-000, SP, Brazil; cecigomes.barbosa@gmail.com (C.G.B.);
luciofreitasjunior@gmail.com (L.H.G.F.-J.)
Programa de Pós-Graduação em Ciência e Tecnologia de Materiais (POSMAT), School of Sciences,
São Paulo State University (UNESP), Bauru 17033-360, SP, Brazil; alex.coleone@unesp.br (A.P.C.);
netobat@gmail.com (A.B.-N.)
School of Agriculture, Department of Bioprocess and Biotechnology, São Paulo State University (UNESP),
Botucatu 18618-689, SP, Brazil; rafael.simoes@unesp.br
Bioinformatics Postgraduate Program, Metrópole Digital Institute, Federal University of Rio Grande do
Norte, Natal 59078-900, RN, Brazil; raul.maia.089@ufrn.edu.br
People&Science Pesquisa Desenvolvimento e Inovação LTDA, Centro de Desenvolvimento
Tecnológico (CDT), Universidade de Brasília, UnB, Brasília 70910-900, DF, Brazil
Campus São Bernardo, Universidade Federal do Maranhão, UFMA, São Bernardo 65550-000, MA, Brazil;
jeffersonbiotec@gmail.com
Department of Biophysics and Physiology, Federal University of Piauí, Teresina 64049-550, PI, Brazil;
daniel.arcanjo@ufpi.edu.br
Institute of Sciences and Engineering, São Paulo State University (UNESP), Itapeva 18409-010, SP, Brazil
Laboratório Associado para a Química Verde/Rede de Química e Tecnologia (LAQV/REQUIMTE),
Departamento de Química e Bioquímica, Faculdade de Ciências, Universidade do Porto,
4169-007 Porto, Portugal; pete.eaton@gmail.com (P.E.); alexandra.nascimento@fc.up.pt (A.P.)
School of Chemistry, The Bridge, University of Lincoln, Lincoln LN6 7EL, UK
IPEEC-CONICET, Consejo Nacional de Investigaciones Científicas y Técnicas,
Puerto Madryn 9120, Argentina; mmarani@cenpat-conicet.gob.ar
Instituto de Química (IQ), Universidade de São Paulo (USP), São Paulo 05508-900, SP, Brazil;
massuojorge@gmail.com
Correspondence: jrsaleite@gmail.com

distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license (https://
creativecommons.org/licenses/by/
4.0/).

Abstract: The potential emergence of zoonotic diseases has raised significant concerns, particularly in
light of the recent pandemic, emphasizing the urgent need for scientific preparedness. The bioprospection and characterization of new molecules are strategically relevant to the research and development
of innovative drugs for viral and bacterial treatment and disease management. Amphibian species

Pharmaceutics 2024, 16, 190. https://doi.org/10.3390/pharmaceutics16020190

https://www.mdpi.com/journal/pharmaceutics

Pharmaceutics 2024, 16, 190

2 of 19

possess a diverse array of compounds, including antimicrobial peptides. This study identified the
first bioactive peptide from Salamandra salamandra in a transcriptome analysis. The synthetic peptide
sequence, which belongs to the defensin family, was characterized through MALDI TOF/TOF mass
spectrometry. Molecular docking assays hypothesized the interaction between the identified peptide
and the active binding site of the spike WT RBD/hACE2 complex. Although additional studies are
required, the preliminary evaluation of the antiviral potential of synthetic SS-I was conducted through
an in vitro cell-based SARS-CoV-2 infection assay. Additionally, the cytotoxic and hemolytic effects of
the synthesized peptide were assessed. These preliminary findings highlighted the potential of SS-I as
a chemical scaffold for drug development against COVID-19, hindering viral infection. The peptide
demonstrated hemolytic activity while not exhibiting cytotoxicity at the antiviral concentration.
Keywords: amphibians; transcriptomics; antimicrobial peptides; bioinformatics; antiviral action;
SARS-CoV-2 infection

1. Introduction
The indiscriminate utilization of antimicrobial agents and, as a consequence, antimicrobialresistant pathogens pose a significant threat to the effectiveness of treating prevalent infectious diseases [1]. In addition, the recent rise of zoonotic diseases, including severe
acute respiratory syndrome coronavirus (SARS-CoV) and Middle East respiratory syndrome coronavirus (MERS-CoV) [2], has exacerbated the situation due to the absence of
appropriate resources for the rapid and effective development of new drugs.
Resistance to conventional antibiotics is a major global public health concern, leading to
prolonged hospitalization times and a high mortality rate with consequent economic impacts.
Similar to other coronaviruses, SARS-CoV-2 relies on the surface spike glycoprotein
to access the host cells, mainly through the interaction between its receptor-binding domain (RBD) and the host cell receptor angiotensin-converting enzyme 2 (ACE2) [3–5].
SARS-CoV-2 infection triggers a deep downstream pro-inflammatory cytokine storm. Elevated levels of pro-inflammatory cytokines can result in detrimental tissue damage,
including lung tissue damage, respiratory failure, and, ultimately, multi-organ failure in
COVID-19 patients. Therefore, molecular entities that can interfere with the binding of the
SARS-CoV-2 spike protein to ACE2 have the potential to inhibit viral entry, thus reducing
viral infectivity.
One promising approach to blocking viral activity is the application of natural peptide molecules due to their general advantages, such as high specificity and effectiveness.
They are also characterized by easy and rapid production (despite high costs), low toxicity
(minimal side effects and easy metabolism), and a particular mechanism of action that
delays the emergence of resistant mutants. Moreover, natural peptides can be used synergistically with other drugs [6]. Natural peptides can serve as models for the development
of modified synthetic antimicrobial peptides (AMPs). Peptides are highly versatile and
amenable to improvement through design, which allows limitations to be addressed, such
as a short half-life or poor oral absorption [7,8]. As a result, numerous peptide-based drugs
are currently commercially available for treating numerous ailments, such as hepatitis
C, myeloma, skin infections, and diabetes [9], with several hundred more in either the
preclinical or clinical stage of development [10,11].
AMPs have been isolated from most life forms and are categorized into different
peptide families according to their particular sequences and structures. The defensin
AMP family is identified as abundant cysteine-rich AMPs divided into three groups,
including α-, β-, and θ-defensins, based on the differential connections of their three
disulfide bridges. Defensins and defensin-like peptides have been identified in fungi [12],
plants [13], and numerous animals [14], including humans [15]. These peptides have
demonstrated antimicrobial activity against multiple microorganisms [14,16–19].

Pharmaceutics 2024, 16, 190

3 of 19

Amphibians are an important source of AMPs that possess the ability to neutralize or
kill microorganisms [20]. They present granular glands in their skin that synthesize and
secrete a diverse array of peptides as part of their innate immune defense system. These
AMPs, which vary in structure and size, exhibit a diversity of bioactivities, including antiviral, antifungal, anticancer, antioxidant, immune modulation, and inflammation responses.
Moreover, they employ various mechanisms of action [21]. Each anuran species thus far
exhibits a specific composition of peptides, although many of these peptides display similarities among closely related species, highlighting their common origin [22]. The widespread
European fire salamander, Salamandra salamandra [23], is characterized by its conspicuously
yellow and black skin and possesses specific glands that produce a defensive poison. The
secretion of salamanders has been found to contain a variety of compounds [24], including
peptides and alkaloids [25] with toxic, antimicrobial [14,26], and antioxidant properties [27].
The bioprospection and characterization of new molecules from amphibian species are of
utmost strategic relevance to provide essential tools for immediate use in the research and
development of drugs for viral and bacterial treatment and management. It is crucial to
encourage academic endeavors in this direction, considering that, between 2015 and 2019,
several of the new peptide-based drugs accepted by the FDA came about from the efforts
of academic groups [10].
Here, we report the description and characterization of a new β-defensin-bioactive
peptide identified from the transcriptome analysis of S. salamandra. We describe the 3D
molecular docking in silico assay of its interaction with the complex spike WT RBD/hACE2.
Moreover, we assess the SS-I synthetic peptide antiviral action through a Vero-CCL-81
cell-based SARS-CoV-2 infection test and its cytotoxic and hemolytic effects.
2. Materials and Methods
2.1. Transcriptome Assembly and Identification of Transcript Sequence by Homology
An RNA-seq dataset of S. salamandra was obtained from the Sequence Read Archive
(SRA) under accession number SRR11118085. This database was derived from the collection,
processing of biological material, and gene identification obtained from the tail-tip of the
S. salamandra salamander [28]. The transcriptome data in this dataset were generated
using paired-end total RNA sequencing (Illumina HiSeq2000, San Diego, CA, USA), and
microarrays utilized for gene expression analysis were designed by Czypionka et al. [29].
Raw-read quality control and adapter trimming were carried out, respectively, in
FastQC (v0.11.4) [30] and Trim Galore (v0.4.1) [31] using the option to execute Cutadapt
(v1.8.3) [32] with default values. The reads were assembled using rnaSPAdes (v3.14.0) [33]
without the read error correction mode (only the assembler parameter). Finally, a database
was created from the assembled transcripts using makeblastdb (v2.6.0) [34], followed
by a local tblastn search using the CFBD-1 defensin sequence from C. fudingensis as the
query [14]. The best hit transcript obtained from the search was selected for further analysis.
The Expasy translation tool was used to confirm the findings (https://web.expasy.org/
translate/ (accessed on 23 April 2023)). Multiple sequence alignment was performed
between the identified ORFs and amino acid sequences with the C. fundingensis sequence
to assess identity and homology.
2.2. Sequence Alignment and Phylogenetic Analysis
A protein-BLAST (BLASTp) search [35] was conducted using the CFBD-1 amino acid
sequence as the query against the non-redundant protein sequence database at the NCBI
(National Center for Biotechnology Information). The search utilized default parameters.
From the BLAST results, the 12 sequences with the lowest E values were selected for further
analysis. The selected sequences were then subjected to the multiple sequence alignment
program Clustal Omega [36] from the European Molecular Biology Laboratory—European
Bioinformatics Institute (EMBL-EBI), employing default settings. For the phylogenetic tree,
the results were visualized using EvolView [37–39]. To facilitate alignment visualization,
Jalview 2.11.2.6 [40] was employed. In the alignment, the conserved amino acids, meaning

Pharmaceutics 2024, 16, 190

4 of 19

those with more than 50% identity at a specific position, were highlighted using the Clustal
coloring method. The sequences were organized into four groups, each sorted by similarity
to SS-I. The first group comprises the sequences of SS-I and CFBD-1. The second group
includes all the β-defensin peptides. The third group consists of the identified hypothetical
proteins, while the fourth group comprises β-defensin-unrelated peptides.
2.3. In Silico Studies
2.3.1. Docking
The structural model of SS-I was generated using homology modeling with the assistance of the MPI Bioinformatics Toolkit [41,42], and subsequent refinement was performed
using the PyMOL software, version 2.5 [43]. The protonation states of the residues were
evaluated at neutral pH using the PDB2PQR server [44].
The protein–peptide interactions between hACE2 and SS-I (ACE2-PEP), as well as the
binding structure of SS-I and SARS-CoV-2 spike RBD (SPIKE-PEP), were evaluated through
protein–peptide flexible docking using the HADDOCK2.4 server [45,46]. The ACE2 and
spike structures were obtained from Protein Data Bank files (6LZG) [47] and isolated via
the PyMOL software. Active interfacial residues at the ACE2/SPIKE were selected for
docking analysis.
2.3.2. Molecular Dynamics Simulations
Molecular dynamics (MD) simulations were performed using the conformational structure complexes obtained in the previous step of molecular docking, henceforth referred to
as ACE2-PEP-S1 and ACE2-PEP-S2 (representing the two best solutions from the docking
between the ACE2 protein and the peptide of interest) and SPIKE-PEP-S1 and SPIKE-PEPS2 (representing the two best solutions from the docking between the spike protein and
the peptide of interest). All MD simulations were conducted using the GROMACS v.2018
software [48]. The protonation states of the amino acid residues at pH 7.0 were evaluated
using the PDB2PQR server [44]. The structures of the ACE2-PEP-S1, ACE2-PEP-S2, SPIKEPEP-S1, and SPIKE-PEP-S2 complexes were energetically optimized using a combination of
steepest descent (SD) and adopted basis Newton–Raphson (ABNR)-based energy minimization (500 steps). Subsequently, the complexes were subjected to a 100 ps MD simulation
for temperature equilibration at 300 K, using the Charmm force field [49] with explicit solvent (TIP3P). Then, 100 ns MD simulations were performed under a constant temperature
(T = 300 K) and pressure (1.0 bar), also employing the Charmm force field. The stability
of the complexes during the MD simulations was evaluated by analyzing parameters
between the molecules’ interfacing residues, such as residues making hydrogen/disulfide
bonds, salt bridges, and covalent links. These analyses were performed using the tools
of the PDBePISA web service [50] and the VMD software, version 1.9.3 [51]. Hydrogen
bonds were considered present if the donor–acceptor distance was approximately 3.5 Å,
the angle was around 30◦ , and the salt-bridge cutoff was <4.0 Å [52]. Two-dimensional
ligand–protein interaction diagrams were made using the LigPlot+ web service [53].
2.3.3. Electronic Structure Calculations
The initial (pre-optimized) structures employed in the MD of ACE2-PEP-S1, ACE2PEP-S2, SPIKE-PEP-S1, and SPIKE-PEP-S2 were employed as inputs for the calculation
of local chemical reactivity descriptors. Four structures with slightly different conformations were evaluated using the density functional theory (DFT) framework. The B3LYP
exchange–correlation functional [54–56] and the 6-31G(d,p) basis set were applied to all
atoms. The calculations were performed in water, utilizing the polarizable continuum
model (PCM) [57].
Chemical reactivity was assessed using condensed-to-atoms Fukui indexes (CAFIs) [58].
These indexes provide valuable information about the reactivity of peptide sites towards nucleophilic (f + ) or electrophilic (f − ) agents and have been widely used in peptide studies [27,59,60].

Pharmaceutics 2024, 16, 190

5 of 19

The CAFIs were calculated based on finite differences in the atomic populations obtained
through Hirshfeld’s partition method, following a procedure described elsewhere [61,62].
2.4. Synthesis and Characterization of Peptide
The peptide SS-I was synthesized manually, with a standard Fmoc (N-(9-fluorenyl)
methoxycarbonyl) chemistry. The synthesis was initiated with 215 mg of resin (0.70 mmol/g,
Peptides International). Fmoc-protected amino acids (Peptides International) were used in
a four-fold to six-fold molar excess relative to the nominal synthesis scale (1.2 mmol). Couplings were performed with 1,3-diisopropyl carbodiimide/ethyl 2-cyano-2-(hydroxyimino)
acetate (DIC/Oxyma® ) in N,N-dimethylformamide (DMF) for 2–3 h. Amino group deprotections were carried out using a mixture of 4-methyl piperidine/DMF (1:4, v:v) for
20–30 min. Each deprotection and coupling were confirmed through a Kaiser test. The
cleavage of the peptide from the resin and the removal of side-chain protecting groups
were performed using 10.0 mL of a cleavage cocktail (Reagent K), shaken at room temperature for 90 min [63,64]. After solvent evaporation under nitrogen, the peptide was
precipitated by adding cold diisopropyl ether, collected through filtration, and washed
four times with the same solvent. Extraction was performed using a mixture of 200 mL of
water and acetonitrile (1:1, v:v), and the crude peptide was lyophilized. The synthesized
products were purified using reverse-phase HPLC with a C18 column (250 × 20 mm i.d.,
15 µm, Shim-Pack PREP-ODS). To confirm the presence of the purified molecules, MALDITOF/TOF mass spectrometry (Ultraflex III Extreme Bruker Daltonics) was used in the
positive, reflector mode [65].
2.5. In Vitro Synthetic SS-I Viability Evaluation
C20 cells were cultured in a DMEM-F12 medium supplemented with L-glutamine,
10% FBS, and 1% Pen/Strep at 37 ◦ C and 5% CO2 . For the experiments, 5 × 104 cells were
seeded in each well. After four hours, the cells were treated with different concentrations
of the SS-I synthetic peptide (5, 10, 50, and 100 µM). The cells were then incubated for 24 h.
For the MTT assay, 100 µL of 3-(4,5-dimethylthiazol-2-yl)-2,5-diphenyltetrazolium
bromide (MTT) at 0.5 mg/mL was added to the cells. After four hours of incubation with
MTT, DMSO was added to the wells to solubilize the formazan crystals, and the plate was
measured at 570 nm. Cells treated with 30% DMSO were used as the positive control. The
viability percentage was calculated through normalization to the basal value. Statistical
analyses of five independent experiments were performed using GraphPad Prism version
9.5 (GraphPad Software, San Diego, CA, USA), including Brown–Forsythe and Welch
ANOVA tests associated with Dunnett’s T3 multiple comparisons test.
2.6. In Vitro Vero-CCL-81 Cell-Based SARS-CoV-2 Infection Assay
The purified SS-I synthetic peptide was initially diluted to a concentration of 2 mM
in DMSO and subsequently diluted in PBS to achieve a concentration of 60 µM. From this
prepared working solution, 10 µL was added to the assay plates. The initial concentration
for the dose–response assay was set at 10 µM. DMSO-treated infected cells and DMSOtreated non-infected cells were used as positive and negative controls, respectively.
Vero CCL-81 cells were plated in a 384-well plate and, after 24 h, the compounds
were added to the cells previously described. Following that, the SARS-CoV-2 virus
(SP02/human/2020/BR; GenBank Accession No. MT126808.1) was added at a multiplicity
of infection of 0.1 viral particles per cell. The final DMSO concentration in the assay was
0.5% (v/v). After 33 h, the cells were fixed in 4% paraformaldehyde (in PBS pH 7.4) and
immunofluorescence was performed using serum from a convalescent COVID-19 patient
diluted at 1:1000 in 5% bovine serum albumin (BSA) in PBS, which served as the primary
antibody. After 30 min, the wells were washed. A solution of Alexa488-conjugated goat
anti-human IgG (Thermo Fisher Scientific, Waltham, MA, USA), and 5 µg/mL of DAPI (4′ ,6
diamidino-2-phenylindole; Sigma-Aldrich, St. Louis, MO, USA) diluted at 1:1000 in 5%
BSA (v/v) was added to each well and incubated for 30 min. All wells were washed twice

Pharmaceutics 2024, 16, 190

6 of 19

with PBS, and images were acquired using the HCS Operetta (PerkinElmer, Waltham, MA,
EUA) and subsequently analyzed with the Harmony software (Perkin Elmer, Waltham, MA,
USA), version 3.5.2. The measured parameters in each well were the total cell number and
the total number of infected cells. The ratio between the number of infected cells and the
total cell number was defined as the infection rate (IR). The antiviral activity was calculated
based on the IR normalization to the negative control (DMSO-treated infected cells). The
cell survival ratio was calculated by normalizing the total cell number in each well to the
average number of cells in the positive control wells. A nonlinear regression analysis and
sigmoidal dose–response (variable slope) were performed using GraphPad Prism version
7.0, considering three independent experiments.
2.7. Hemolysis Assay
To assess the hemolytic activity of synthetic SS-I, 4 mL of whole blood was collected in
EDTA (1.8 mg/mL) tubes and then centrifuged at 1500 rpm for 10 min. Red blood cells
(RBCs) were washed three times with PBS (pH 7.2) at 37 ◦ C, replacing the removed plasma
volume. A two-fold serial dilution of synthetic SS-I was prepared in a round-bottom plate
starting at 100 µM. Then, 75 µL of 10% RBCs in PBS was added to each well containing
75 µL of the sample, PBS (negative control), or 0.1% Triton-X (positive control), and mixed
carefully. All concentrations and controls were tested in triplicate. The plate was incubated
for 1 h at 37 ◦ C under gentle agitation. After the incubation, the plate was centrifuged at
4500 rpm for 5 min, 100 µL was transferred to a new flat-bottom plate, and finally measured
at 550 nm. Hemolytic activity (%) = (Abs sample − Abs PBS )/(Abs Triton-X − Abs PBS ) × 100.
3. Results and Discussion
3.1. Identification and Characterization of the Defensin SS-I
The identification of CFBD-1 as the first defensin with antimicrobial properties from
Cynops fudingensis [14] and the subsequent discovery of Salamandrin-I from S. salamandra [27],
where a sequence similarity between these two peptides was described by Plácido et al.,
was the starting point for this work. C. fudingensis, commonly known as the Fuding
fire-bellied newt, has been described to live predominantly in an aquatic environment. Contrarily, fire salamanders are known to live in hilly forest areas (Figure 1). When compared to
its aquatic counterpart, the terrestrial environment is associated with higher UV radiation
levels and more significant variations in temperature and humidity. Besides the selection
pressure on the animal species to adapt better to their settings, microbial pathogens undergo thorough adaptative evolution [66]. The conditions where fire salamanders live have
been proven to provide these amphibians with antioxidant peptides (AOPs) and AMPs
with much richer diversity and greater potency [67]. Considering this, the strategy was to
use the CFBD-1 sequence to identify a similar peptide in the S. salamandra RNA-seq dataset
through bioinformatic prospection.
A novel β-defensin antimicrobial peptide, named SS-I, was identified from the tail-tip
of S. salamandra larvae by combining RNA sequencing and bioinformatics. A BLAST search
revealed a significant sequence similarity between SS-I and several β-defensin AMPs from
other animals (Figure 2A). The multiple alignment was sorted by similarity to SS-I, with the
aligned sequences from Zhangixalus puerensis to Plecoglossus altivelis representing β-defensin
peptides. The displayed sequences from Xenopus laevis, Megalops atlanticus, and Alosa alosa
correspond to hypothetical proteins. During genome sequencing, it is common to identify
open reading frames (ORFs) that encode proteins that have not yet been proven to be
expressed in the organism or whose function remains unknown.

Pharmaceutics 2024, 16, x190
FOR PEER REVIEW

(A)

7 7ofof 20
19

(B)

Figure 1. (A) Peneda-Gerês
fire
salamanders
(S.(S.
salamandra).
Figure
Peneda-Gerês National
NationalPark,
Park,Portugal.
Portugal.(B)
(B)Specimens
Specimensofof
fire
salamanders
salamandra).
Photo
credit:
Eaton.
Photo
credit:
PeterPeter
Eaton.

A
novel
β-defensin
antimicrobial
SS-I, similarity
was identified
from
the tailSince
these
identified
hypothetical peptide,
proteins named
exhibit high
to other
β-defensin
tip
of
S.
salamandra
larvae
by
combining
RNA
sequencing
and
bioinformatics.
A
BLAST
peptides, it is plausible that they may share a similar function. However, it should
be
search
revealed
a
significant
sequence
similarity
between
SS-I
and
several
β-defensin
noted that similarity and the presence of multiple conserved residues do not directly
AMPs
from
other animals
(Figure
The multiple
alignment
was of
sorted
by similarity
imply a
functional
association.
For2A).
instance,
the peptide
sequences
Alligator
mississipto
SS-I,
with
the
aligned
sequences
from
Zhangixalus
puerensis
to
Plecoglossus
altivelis repiensis and Chelonia mydas represent an ADAM9-like (disintegrin and metalloproteinase
resenting
β-defensinprotein
peptides.
The displayed
sequences
from Xenopus
laevis,delta
Megalops
atdomain-containing
9-like)
protein and
POLD3 (DNA
polymerase
subunit
lanticus,
and
Alosa
alosa
correspond
to
hypothetical
proteins.
During
genome
sequencing,
3), respectively. Despite exhibiting highly conserved amino acids, such as glycine and
itcysteine,
is common
to play
identify
open reading
(ORFs) that
encode
proteins
thatfunctional
have not
which
an important
roleframes
in determining
peptide
structure,
their
yet
been proven
to be
expressed
in 2B
theshows
organism
or separation
whose function
remains
unknown.
connection
remains
unclear.
Figure
a clear
between
exclusively
aquatic
species and those capable of exploiting both aquatic and terrestrial habitats. Moreover, it is
apparent that S. salamandra exhibits a closer phylogenetic relationship with frogs and toads,
followed by turtles and, lastly, alligators.
Figure 3 illustrates the homology-predicted 3D structure of the identified mature peptide consisting of 44 residues. The complete sequence of the peptide is NH2 -FVVWGCADYRGSCRTACFAYEYSLGAKGCADGYICCVPNTFRLM-COOH, which contains six cysteines,
four basic, and three acidic residues. The theoretical mass of the peptide is [M + H]+ (average mass) 4870.684 and [M + H]+ (monoisotopic) 4867.1515 [68]. The predicted peptide
identified in the transcriptome analysis was synthesized, purified, and characterized via
mass spectrometry for subsequent use in biological assays, as per the section on the materials and methods. The predicted structure presents disulfide bonds that define its global
conformation. However, after the peptide synthesis, the cysteine oxidation was unsuccessful; thus, the correct folding was not attained, as the disulfide bonds were not formed.
3.2. Interactions between SS-I with ACE2 and SARS-CoV-2 Spike Protein (S1)
The spike protein of SARS-CoV-2 comprises two subunits, S1 and S2, which play a two(A)
step process: (i) receptor recognition and (ii) cell membrane fusion. The S1 subunit contains
a receptor-binding domain that recognizes and binds to the host receptor, ACE2, while the
S2 subunit mediates viral cell membrane fusion by forming a six-helical bundle via the
two-heptad repeat domain [69,70]. S1 can be divided into an N-terminal domain (NTD)
and a C-terminal domain (CTD), and SARS-CoV-2 utilizes the S1 CTD to recognize the
receptor (also called the receptor-binding domain (RBD)) [71]. In this way, the RBD region
is a critical target for neutralizing SARS-CoV-2. For all explained here, we use a 2.5 Å crystal
structure of SARS-CoV-2-CTD in complex with ACE2 (S1 subunit), reported in a previous
study [71], to perform our analysis. In this study, we are also interested in identifying
possible interactions between the proposed peptide (PEP) and the ACE2 cell receptor. Thus,
as explained in more detail in the methodology, the docking solutions were identified
as two different complexes: (i) the peptide complexed with the cell receptor (ACE2-PEP)
and (ii) the peptide complexed with the SARS-CoV-2-CTD (SPIKE-PEP). The molecular

Figure 1. (A) Peneda-Gerês National Park, Portugal. (B) Specimens of fire salamanders (S. salam
dra). Photo credit: Peter Eaton.

Pharmaceutics 2024, 16, 190

A novel β-defensin antimicrobial peptide, named SS-I, was identified from the
tip of S. salamandra larvae by combining RNA sequencing and bioinformatics. A BLA
search revealed a significant sequence similarity between SS-I and several
8 of 19 β-defen
AMPs from other animals (Figure 2A). The multiple alignment was sorted by simila
to SS-I, with the aligned sequences from Zhangixalus puerensis to Plecoglossus altivelis r
resenting
β-defensin
peptides.
displayed
from(ACE2-PEP-S1,
Xenopus laevis, Megalop
complexes obtained
through
the docking
andThe
used
for MDsequences
simulations
lanticus,
and
Alosa
alosa
correspond
to
hypothetical
proteins.
During
genome sequenc
ACE2-PEP-S2, SPIKE-PEP-S1, and SPIKE-PEP-S2) are presented in the supplementary
it
is
common
to
identify
open
reading
frames
(ORFs)
that
encode
proteins
material (Figure S1). Here, S1 and S2 represent the two best docking solutions, respectively,that have
for each complex.yet been proven to be expressed in the organism or whose function remains unknown

Pharmaceutics 2024, 16, x FOR PEER REVIEW

8 of

(A)

(B)

2. Results
of BLASTp
analysis.
(A) Multiple
was
performed
using the Clu
Figure 2. Results Figure
of BLASTp
analysis.
(A) Multiple
alignment
wasalignment
performed
using
the Clustal
Omega tool. The sequences were categorized into four groups, each sorted by similarity to SS-I. T
Omega tool. The sequences were categorized into four groups, each sorted by similarity to SS-I.
CFDB-1 peptide, highlighted in bold, was used to identify SS-I. The first group comprises the
The CFDB-1 peptide,
highlighted
in bold,
was
used to identify
SS-I.group,
The first
group amino
comprises
quences
of SS-I and
CFBD-1
(gray-lined
box). In this
conserved
acidsthe
are colored. T
sequences of SS-I and
CFBD-1
(gray-lined
box).
In
this
group,
conserved
amino
acids
are
colored.
second group consists of β-defensin peptides spanning from Zhangixalus puerensis
to Plecoglos
altivelis. of
The
third group
includes
hypothetical
of Xenopus
laevis,
Megalops atlanticus, a
The second group consists
β-defensin
peptides
spanning
fromproteins
Zhangixalus
puerensis
to Plecoglossus
The fourth
group encompasses
whose
peptides
do atlanticus,
not belong and
to the β-defen
altivelis. The third Alosa
groupalosa.
includes
hypothetical
proteins ofspecies
Xenopus
laevis,
Megalops
family.
For
all
sequences,
the
conserved
amino
acids,
meaning
those
present
in
more
Alosa alosa. The fourth group encompasses species whose peptides do not belong to the β-defensin than 50%
the sequences at a specific position, were colored. The numbers following the species name indic
family. For all sequences, the conserved amino acids, meaning those present in more than 50% of the
the aligned sequence limits. (B) Phylogenetic tree generated from the Clustal Omega alignment
sequences at a specific
sults.position, were colored. The numbers following the species name indicate the
aligned sequence limits. (B) Phylogenetic tree generated from the Clustal Omega alignment results.

Since these identified hypothetical proteins exhibit high similarity to other β-defen
peptides, it is plausible that they may share a similar function. However, it should
noted that similarity and the presence of multiple conserved residues do not directly i
ply a functional association. For instance, the peptide sequences of Alligator mississipien
and Chelonia mydas represent an ADAM9-like (disintegrin and metalloproteinase doma

Pharmaceutics 2024, 16, 190

characterized via mass spectrometry for subsequent use in biological assays, as per the
section on the materials and methods. The predicted structure presents disulfide bonds
that define its global conformation. However, after the peptide synthesis, the cysteine ox9 of 19
idation was unsuccessful; thus, the correct folding was not attained, as the disulfide bonds
were not formed.
(A)

(B)

(C)

Figure
representationsofofSS-I
SS-Ipeptide.
peptide.(A)
(A)Ball-and-stick
Ball-and-stick
representation.
RibFigure 3.
3. Hypothesized
Hypothesized representations
representation.
(B)(B)
Ribbon
bon representation. (C) Overlap of ball-and-stick and ribbon diagrams.
representation. (C) Overlap of ball-and-stick and ribbon diagrams.

3.2. Interactions
between
SS-I with ACE2
and SARS-CoV-2
Spike
(S1)bonds (H-bonds),
Protein–protein
interactions
are essentially
stabilized
by Protein
hydrogen
disulfide
bonds,
salt bridges,
and, in rare
cases, two
covalent
linksS1
[72].
case play
of the
The spike
protein
of SARS-CoV-2
comprises
subunits,
andIn
S2,the
which
a
molecularprocess:
complexes
under study,
only hydrogen
bonds
and salt bridges
wereS1identified
two-step
(i) receptor
recognition
and (ii) cell
membrane
fusion. The
subunit
betweenathe
interface residues.
Therefore,
the analysis
presented
in Figure
4A ACE2,
shows
contains
receptor-binding
domain
that recognizes
and binds
to the host
receptor,
significant
differences
in
the
number
of
H-bonds
observed
during
the
MD
simulations
while the S2 subunit mediates viral cell membrane fusion by forming a six-helical bundle
of the
interactions
between
the proteins
oninto
the an
complexes
ACE2-PEPvia
the complexes.
two-heptad The
repeat
domain [69,70].
S1 can
be divided
N-terminal
domain
S1 andand
SPIKE-PEP-S1
a lowand
frequency
of H-bonds
zero
three,
(NTD)
a C-terminalpresented
domain (CTD),
SARS-CoV-2
utilizesbetween
the S1 CTD
to and
recognize
which
makes(also
the called
interaction
between the proteins
of (RBD))
the complex
quite
Conthe
receptor
the receptor-binding
domain
[71]. In
this unstable.
way, the RBD
versely,is the
ACE2-PEP-S2
SPIKE-PEP-S2
complexes
showed
a higher
of
region
a critical
target forand
neutralizing
SARS-CoV-2.
For all
explained
here,frequency
we use a 2.5
H-bonds,
predominantly
ranging
between
four
and
ten,
despite
the
peptide
consisting
Å crystal structure of SARS-CoV-2-CTD in complex with ACE2 (S1 subunit), reported in
only 44 amino
behavior
was observed
for the we
frequency
salt bridges
aofprevious
study acids.
[71], toSimilar
perform
our analysis.
In this study,
are alsoofinterested
in
monitored
throughout
the
simulation.
Figure
4A
shows
that
the
ACE2-PEP-S2
complex
has
identifying possible interactions between the proposed peptide (PEP) and the ACE2 cell
a predominant
of salt
bridges
equal
three,
while the ACE2-PEP-S1
complex
receptor.
Thus, frequency
as explained
in more
detail
in to
the
methodology,
the docking solutions
has aidentified
predominant
frequency
to one.(i)Inthe
thepeptide
case ofcomplexed
the complexes
the
were
as two
differentequal
complexes:
with containing
the cell recepSPIKE
protein,
it
was
observed
that
both
the
SPIKE-PEP-S1
and
SPIKE-PEP-S2
complexes
tor (ACE2-PEP) and (ii) the peptide complexed with the SARS-CoV-2-CTD (SPIKE-PEP).
havemolecular
a predominant
frequency
of one.
However,
SPIKE-PEP-S1
showed
The
complexes
obtained
through
the the
docking
and usedcomplex
for MD also
simulations
a
significant
frequency
of
0;
that
is,
this
complex
remains
for
a
considerable
time
(ACE2-PEP-S1, ACE2-PEP-S2, SPIKE-PEP-S1, and SPIKE-PEP-S2) are presented during
in the
simulation without
making
salt bridge
interactions.
docking
solutions
are
supplementary
material
(Figure
S1). Here,
S1 and S2Although
represent these
the two
best docking
soluenergetically
viable,
these
results
suggest
that
the
formation
of
the
complexes
ACE2-PEP-S1
tions, respectively, for each complex.
and SPIKE-PEP-S1 may not be promising. On the other hand, these results suggest that the
ACE2-PEP-S2 and SPIKE-PEP-S2 complexes are more stable, evidencing that the peptide
can interact effectively with both the spike and the ACE2 proteins.

Pharmaceutics 2024, 16, 190

throughout the 100 ns of simulation. In contrast, despite its smaller size, the peptide displayed higher RMSD values in both simulations, indicating more remarkable conformational changes during the MD. This is attributed to the outstanding flexibility of the peptide, as it recursively rearranged itself to maintain the H-bonds and salt bridges. Finally,
Figure 4C presents a 2D representation of the frames with the highest number of H-bonds
10 of 19
and salt bridges during MD for the ACE2-PEP-S2 and SPIKE-PEP-S2 complexes, where
the amino acids involved in chemical contacts are highlighted.

Pharmaceutics 2024, 16, x FOR PEER REVIEW

11 of 20

(A)

(B)

(C)
Figure 4. (A) Frequency of H-bonds and salt bridges during MD simulations in the ACE2-PEP-S1,
Figure 4. (A) Frequency of H-bonds and salt bridges during MD simulations in the ACE2-PEPACE2-PEP-S2, SPIKE-PEP-S1, and SPIKE-PEP-S2 complexes. (B) Root-mean-square deviation
S1, ACE2-PEP-S2, SPIKE-PEP-S1, and SPIKE-PEP-S2 complexes. (B) Root-mean-square deviation
(RMSD) from MD simulations of the two best docking solutions: ACE2-PEP-S2 and SPIKE-PEP-S2.
(RMSD)
from MD
of each
the two
best docking
solutions: ACE2-PEP-S2
and SPIKE-PEP-S2.
RMSD values
aresimulations
presented for
protein:
ACE2, PEP(ACE2)
(peptide complexed
with ACE2
RMSD
values
areand
presented
for each
protein:
ACE2,with
PEP(ACE2)
(peptide
complexedligand–prowith ACE2
protein),
SPIKE,
PEP(SPIKE)
(peptide
complexed
spike. (C)
Two-dimensional
tein interaction
diagrams
for the(peptide
complexes
ACE2-PEP-S2
and SPIKE-PEP-S2.
protein),
SPIKE, and
PEP(SPIKE)
complexed
with spike.
(C) Two-dimensional ligand–protein
interaction diagrams for the complexes ACE2-PEP-S2 and SPIKE-PEP-S2.
Table 1. Residues in ACE2-PEP-S2 and SPIKE-PEP-S2 complexes with H-bonds and salt bridges of
>10% occupancy throughout MD simulation.

ACE2-PEP-S2
Donor

Acceptor

SPIKE-PEP-S2
H-Bonds
Occupancy
Donor

Acceptor

Occupancy

Pharmaceutics 2024, 16, 190

11 of 19

H-bonds and salt bridges with an occupancy higher than 10% during the MD between residues o

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "APD6", "db_subject_text": "SARS-CoV-2 and toxicity summary", "db_measure": "EC50 2.7 uM; TC50 10 uM; little hemolytic till 100 uM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "90% Hemolysis at 1-10 uM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Human erythrocytes", "db_measure": "100% Hemolysis at 100 uM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Human microglial cells HMC20", "db_measure": "50% Cytotoxicity at 100 uM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "SARS-CoV-2", "db_measure": "IC50 I 2.7 uM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 5, "database": "APD6", "db_subject_text": "SS-I", "db_measure": "sequence identity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "SS-I", "db_measure": "sequence identity", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Vero CCL-81 cells", "db_measure": "50% Cytotoxicity at 10 uM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Human microglial cells HMC20", "db_measure": "15% Cytotoxicity at 5 uM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 9, "database": "DBAASP", "db_subject_text": "Human microglial cells HMC20", "db_measure": "21% Cytotoxicity at 10 uM", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 10, "database": "APD6", "db_subject_text": "literature record", "db_measure": "DOI/PMID/PMCID match", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 11, "database": "DBAASP", "db_subject_text": "literature record", "db_measure": "DOI/PMID/PMCID match", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now.