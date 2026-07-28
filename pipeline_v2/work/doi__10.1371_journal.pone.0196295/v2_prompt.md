
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
doi__10.1371_journal.pone.0196295

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "Amino acidic sequences of peptides belonging to the NCPs family.", "footnotes": ["The substitutions in the amino acids composition, compared to the Original CTX-1 stretch, are marked in bold and underlined."], "header_rows": [["Sequence ID", "Primary Structure"], ["Original CTX-1 stretch", "KLIPIASKTCPAGKNLCYKM"], ["NCP-0", "KLIPIASKTCPAGKNLCYKI"], ["NCP-2", "KLIPILSKTIPAIKNLFYKI"], ["NCP-3", "KLIWILSKTIPAIKNLFYKI"], ["NCP-3a", "KLIFILSKTIPAIKNLFYKI"], ["NCP-3b", "KLILILSKTIPAIKNLFYKI"]], "longform_cells": []}]

=== PRIMARY PAPER FULL TEXT (context only) ===
Use this ONLY to (a) confirm whether an organism/target/assay was tested in this paper (prevents false 'absent' calls), and (b) read an endpoint label. You may NOT cite full text as the `evidence` cell for is_database_error=true; that still requires a structured longform cell.
CORRECTION

Correction: Novel Naja atra cardiotoxin 1 (CTX1) derived antimicrobial peptides with broad
spectrum activity
The PLOS ONE Staff

ln Table 1, the sequences of NCP-2, NCP-3, NCP-3a and NCP-3b are incorrect. Specifically,
the glycine (G) residue in position 13 is incorrectly substituted with isoleucine (I). Additionally, the substitutions in these sequences are not formatted correctly. They should be marked
in bold and underlined. The publisher apologizes for this error. Please see the corrected
Table 1 here.
Table 1. Amino acidic sequences of peptides belonging to the NCPs family.
Sequence ID

Primary Structure

Original CTX-1 stretch

KLIPIASKTCPAGKNLCYKM

NCP-0

KLIPIASKTCPAGKNLCYKI

NCP-2

KLIPILSKTIPAIKNLFYKI

NCP-3

KLIWILSKTIPAIKNLFYKI

NCP-3a

KLIFILSKTIPAIKNLFYKI

NCP-3b

KLILILSKTIPAIKNLFYKI

The substitutions in the amino acids composition, compared to the Original CTX-1 stretch, are marked in bold and
underlined.

a1111111111
a1111111111
a1111111111
a1111111111
a1111111111

https://doi.org/10.1371/journal.pone.0196295.t001

Reference
1.

Sala A, Cabassi CS, Santospirito D, Polverini E, Flisi S, Cavirani S, et al. (2018) Novel Naja atra cardiotoxin 1 (CTX-1) derived antimicrobial peptides with broad spectrum activity. PLoS ONE 13(1):
e0190778. https://doi.org/10.1371/journal.pone.0190778 PMID: 29364903

OPEN ACCESS
Citation: The PLOS ONE Staff (2018) Correction:
Novel Naja atra cardiotoxin 1 (CTX-1) derived
antimicrobial peptides with broad spectrum
activity. PLoS ONE 13(4): e0196295. https://doi.
org/10.1371/journal.pone.0196295
Published: April 18, 2018
Copyright: © 2018 The PLOS ONE Staff. This is an
open access article distributed under the terms of
the Creative Commons Attribution License, which
permits unrestricted use, distribution, and
reproduction in any medium, provided the original
author and source are credited.

PLOS ONE | https://doi.org/10.1371/journal.pone.0196295 April 18, 2018

1/1



=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "CAMP", "db_subject_text": "[Refer PubMed ID: 29364903] Escherichia coli ATCC 25922 (MBC >100 microg/ml), Pseudomonas aeruginosa ATCC 27853 (MBC >100 microg/ml), Acinetobacter baumannii (MBC >100 microg/ml), Klebsiella pneumoniae subsp.pneumoniae (MBC >100 microg/ml), Enterobacter cloacae (MBC >100 microg/ml), Burkholderia cepacia ATCC 17759 (MBC=50microg/ml), Proteus mirabilis ATCC 14153 (MBC >100 microg/ml), Moraxella catarrhalis ATCC 25238 ( MBC=1.6microg/ml), Methicillin-resistant Staphylococcus aureus ATCC 43300 (MBC >100 microg/ml), Staphylococcus aureus ATCC 22953 (MBC >100 microg/ml), Enterococcus hirae ATCC 10541 (MBC >100 microg/ml), Streptococcus agalactiae ATCC 13813 (MBC >100 microg/ml), Candida albicans ATCC 10231 (MBC >100 microg/ml), Candida glabrata ATCC 90030 (MBC >100 microg/ml), Malassezia pachydermatis DSMZ 6172 (MBC >100 microg/ml)", "db_measure": "MBC aggregate text", "db_value": "", "db_unit": "microg/ml", "db_sequence": "", "db_claimed_peptide_name": "NCP-0"}, {"assertion_index": 1, "database": "CAMP", "db_subject_text": "[Refer PubMed ID: 29364903] Escherichia coli ATCC 25922 (MBC=12.5 microg/ml), Pseudomonas aeruginosa ATCC 27853 (MBC=12.5 microg/ml), Acinetobacter baumannii (MBC=1.6 microg/ml), Klebsiella pneumoniae subsp.pneumoniae (MBC >100 microg/ml), Enterobacter cloacae (MBC >100 microg/ml), Burkholderia cepacia ATCC 17759 (MBC=50microg/ml), Proteus mirabilis ATCC 14153 (MBC >100 microg/ml), Moraxella catarrhalis ATCC 25238 ( MBC=1.6microg/ml), Methicillin-resistant Staphylococcus aureus ATCC 43300 (MBC >100 microg/ml), Staphylococcus aureus ATCC 22953 (MBC=50 microg/ml), Enterococcus hirae ATCC 10541 (MBC >100 microg/ml), Streptococcus agalactiae ATCC 13813 (MBC=12.5 microg/ml), Candida albicans ATCC 10231 (MBC=50 microg/ml), Candida glabrata ATCC 90030 (MBC >100 microg/ml), Malassezia pachydermatis DSMZ 6172 (MBC=6.3 microg/ml)", "db_measure": "MBC aggregate text", "db_value": "", "db_unit": "microg/ml", "db_sequence": "", "db_claimed_peptide_name": "NCP-2"}, {"assertion_index": 2, "database": "CAMP", "db_subject_text": "[Refer PubMed ID: 29364903] Escherichia coli ATCC 25922 (MBC=12.5 microg/ml), Pseudomonas aeruginosa ATCC 27853 (MBC=12.5 microg/ml), Acinetobacter baumannii (MBC=1.6 microg/ml), Klebsiella pneumoniae subsp.pneumoniae (MBC=50 microg/ml), Enterobacter cloacae (MBC=25 microg/ml), Burkholderia cepacia ATCC 17759 (MBC=50 microg/ml), Proteus mirabilis ATCC 14153 (MBC >100 microg/ml), Moraxella catarrhalis ATCC 25238 ( MBC=1.6microg/ml), Methicillin-resistant Staphylococcus aureus ATCC 43300 (MBC=6.3 microg/ml), Staphylococcus aureus ATCC 22953 (MBC=1.6 microg/ml), Enterococcus hirae ATCC 10541 (MBC=1.6 microg/ml), Streptococcus agalactiae ATCC 13813 (MBC=1.6 microg/ml), Candida albicans ATCC 10231 (MBC=12.5 microg/ml), Candida glabrata ATCC 90030 (MBC=50 microg/ml), Malassezia pachydermatis DSMZ 6172 (MBC=6.3 microg/ml)", "db_measure": "MBC aggregate text", "db_value": "", "db_unit": "microg/ml", "db_sequence": "", "db_claimed_peptide_name": "NCP-3"}, {"assertion_index": 3, "database": "CAMP", "db_subject_text": "[Refer PubMed ID: 29364903] Escherichia coli ATCC 25922 (MBC=6.3 microg/ml), Pseudomonas aeruginosa ATCC 27853 (MBC=25 microg/ml), Acinetobacter baumannii (MBC=25 microg/ml), Klebsiella pneumoniae subsp.pneumoniae (MBC=50 microg/ml), Burkholderia cepacia ATCC 17759 (MBC=50 microg/ml), Proteus mirabilis ATCC 14153 (MBC >100 microg/ml), Moraxella catarrhalis ATCC 25238 ( MBC=3.1 microg/ml), Methicillin-resistant Staphylococcus aureus ATCC 43300 (MBC=6.3 microg/ml), Staphylococcus aureus ATCC 22953 (MBC=12.5 microg/ml), Enterococcus hirae ATCC 10541 (MBC=6.3 microg/ml), Streptococcus agalactiae ATCC 13813 (MBC=3.1 microg/ml), Candida albicans ATCC 10231 (MBC=6.3 microg/ml), Candida glabrata ATCC 90030 (MBC=25 microg/ml), Malassezia pachydermatis DSMZ 6172 (MBC=6.3 microg/ml)", "db_measure": "MBC aggregate text", "db_value": "", "db_unit": "microg/ml", "db_sequence": "", "db_claimed_peptide_name": "NCP-3a"}, {"assertion_index": 4, "database": "CAMP", "db_subject_text": "[Refer PubMed ID: 29364903] Escherichia coli ATCC 25922 (MBC=12.5 microg/ml), Pseudomonas aeruginosa ATCC 27853 (MBC=25 microg/ml), Acinetobacter baumannii (MBC=25 microg/ml), Klebsiella pneumoniae subsp.pneumoniae (MBC=25 microg/ml), Burkholderia cepacia ATCC 17759 (MBC=25 microg/ml), Proteus mirabilis ATCC 14153 (MBC >100 microg/ml), Moraxella catarrhalis ATCC 25238 ( MBC=12.5 microg/ml), Methicillin-resistant Staphylococcus aureus ATCC 43300 (MBC=6.3 microg/ml), Staphylococcus aureus ATCC 22953 (MBC=50 microg/ml), Enterococcus hirae ATCC 10541 (MBC=12.5 microg/ml), Streptococcus agalactiae ATCC 13813 (MBC=12.5 microg/ml), Candida albicans ATCC 10231 (MBC=12.5 microg/ml), Candida glabrata ATCC 90030 (MBC=100 microg/ml), Malassezia pachydermatis DSMZ 6172 (MBC=25 microg/ml)", "db_measure": "MBC aggregate text", "db_value": "", "db_unit": "microg/ml", "db_sequence": "", "db_claimed_peptide_name": "NCP-3b"}, {"assertion_index": 5, "database": "DBAASP", "db_subject_text": "Correction: Novel Naja atra cardiotoxin 1 (CTX-1) derived antimicrobial peptides with broad spectrum activity.", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_11044"}, {"assertion_index": 6, "database": "DBAASP", "db_subject_text": "Correction: Novel Naja atra cardiotoxin 1 (CTX-1) derived antimicrobial peptides with broad spectrum activity.", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_11045"}, {"assertion_index": 7, "database": "DBAASP", "db_subject_text": "Correction: Novel Naja atra cardiotoxin 1 (CTX-1) derived antimicrobial peptides with broad spectrum activity.", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_11046"}, {"assertion_index": 8, "database": "DBAASP", "db_subject_text": "Correction: Novel Naja atra cardiotoxin 1 (CTX-1) derived antimicrobial peptides with broad spectrum activity.", "db_measure": "", "db_value": "", "db_unit": "", "db_sequence": "", "db_claimed_peptide_name": "DBAASPS_11047"}]

Return ONLY the JSON array now.