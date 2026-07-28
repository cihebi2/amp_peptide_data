
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
doi__10.1016_j.isci.2021.102480

=== DETERMINISTICALLY PARSED SOURCE TABLES (admissible evidence cells) ===
[{"table_index": 1, "label": "Table 1", "caption": "", "footnotes": [], "header_rows": [["REAGENT or RESOURCE", "SOURCE", "IDENTIFIER"], ["Bacterial and virus strains", "Bacterial and virus strains", "Bacterial and virus strains"], ["Bacterial strains are listed in Table S5", "", "N/A"], ["Deposited data", "Deposited data", "Deposited data"], ["Whole genome sequence of Bacillus thuringiensis sv. andalousiensis NRRL B23193", "NCBI", "GenBank: NZ_CP035727.2"], ["Annotated andalusicin biosynthetic gene cluster", "MIBiG", "MIBiG: BGC0002111"], ["Experimental models: organisms/strains", "Experimental models: organisms/strains", "Experimental models: organisms/strains"], ["Bacillus thuringiensis sv. andalousiensis NRRL B23193", "NRRL", "NRRL B-23139"], ["Oligonucleotides", "Oligonucleotides", "Oligonucleotides"], ["For oligonucleotides, see Table S6", "", "N/A"], ["Recombinant DNA", "Recombinant DNA", "Recombinant DNA"], ["pHT01 vector", "MoBiTech, GmbH", "cat# PBS001"], ["pET_His6_TEV_LIC", "Scott Gradia, Addgene", "RRID:Addgene_29653"], ["pHT-ancKCA1", "This study", "N/A"], ["pHT-ancKCA1(S17A)", "This study", "N/A"], ["pHT-ancKCA1(S20A)", "This study", "N/A"], ["pHT-ancKCA1(S17A-S20A)", "This study", "N/A"], ["pHT-ancKCA1MT", "This study", "N/A"], ["pHT-ancKCA1(S20A)MT", "This study", "N/A"], ["pET_His6_ancMT", "This study", "N/A"], ["Software and algorithms", "Software and algorithms", "Software and algorithms"], ["ImageJ", "(Schneider et al., 2012)", "https://imagej.nih.gov/ij/"], ["SPAdes v. 3.9.1", "(Bankevich et al., 2012)", "https://cab.spbu.ru/software/spades/"], ["RAST", "(Overbeek et al., 2014)", "https://rast.nmpdr.org/rast.cgi"], ["MEME Suite v. 5.0.2", "(Bailey et al., 2009)", "https://meme-suite.org/meme/tools/meme"], ["EFI-EST", "(Gerlt et al., 2015)", "https://efi.igb.illinois.edu/efi-est/"], ["Cytoscape", "(Shannon et al., 2003)", "https://cytoscape.org/"], ["MMseqs2 version 12.113e3", "(Steinegger and Söding, 2017)", "https://github.com/soedinglab/MMseqs2"], ["MUSCLE v3.8.31", "(Edgar, 2004)", "http://www.drive5.com/muscle/"], ["ClipKIT v1.0.7", "(Steenwyk et al., 2020)", "https://github.com/JLSteenwyk/ClipKIT"], ["RaxML", "(Stamatakis, 2014)", "https://cme.h-its.org/exelixis/web/software/raxml/"], ["Batch CD-Search", "(Lu et al., 2020)", "https://www.ncbi.nlm.nih.gov/Structure/bwrpsb/bwrpsb.cgi"], ["iTOL", "(Letunic and Bork, 2019)", "https://itol.embl.de/"], ["SciPy v.1.3.1", "(Virtanen et al., 2020)", "https://www.scipy.org/"], ["statsmodels v. 0.10.1", "(Seabold and Perktold, 2010)", "https://www.statsmodels.org/stable/index.html"], ["custom scripts for bioinformatic analysis", "This study", "https://github.com/bikdm12/andalusicin"]], "longform_cells": []}]

=== DATABASE ASSERTIONS TO VERIFY ===
[{"assertion_index": 0, "database": "DBAASP", "db_subject_text": "Staphylococcus aureus ATCC 25923", "db_measure": "MIC", "db_value": "48.6", "db_unit": "ug/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 1, "database": "DBAASP", "db_subject_text": "Paenibacillus polymyxa ATCC 842", "db_measure": "MIC", "db_value": "32.4", "db_unit": "ug/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 2, "database": "DBAASP", "db_subject_text": "Arthrobacter sp. ATCC 21022", "db_measure": "MIC", "db_value": "32.4", "db_unit": "ug/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 3, "database": "DBAASP", "db_subject_text": "Bacillus mycoides DSM 2048", "db_measure": "MIC", "db_value": "16.2", "db_unit": "ug/ml", "db_sequence": "", "db_claimed_peptide_name": ""}, {"assertion_index": 4, "database": "DBAASP", "db_subject_text": "Bacillus cereus ATCC 14579", "db_measure": "MIC", "db_value": "16.2", "db_unit": "ug/ml", "db_sequence": "", "db_claimed_peptide_name": ""}]

Return ONLY the JSON array now (one object per assertion above).