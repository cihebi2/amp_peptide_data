[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "multiple organisms",
      "endpoint": "MIC",
      "value": "S. aureus ATCC 6538P >2560 ug/ml; S. pyogenes 79 ug/ml; P. aeruginosa ATCC 10148 >2560 ug/ml; E. coli ATCC 9723H/25922/MDR CPO-NDM 10-39 ug/ml",
      "peptide": "RaCa-1"
    },
    "verification_outcome": "value_match",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-1",
      "col_header": "MIC",
      "source_value": "10 – 39"
    },
    "short_reason": "RaCa-1 MIC range 10-39 is present in Table 3, but source reports values in μM while DB text uses ug/ml."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "multiple organisms",
      "endpoint": "MIC",
      "value": "S. aureus ATCC 6538P 1-2/1-2 ug/ml; S. pyogenes 25-49 ug/ml; P. aeruginosa ATCC 10148 20->78/39 ug/ml; E. coli ATCC 9723H/ATCC 25922/MDR 2-6 ug/ml",
      "peptide": "RaCa-2"
    },
    "verification_outcome": "value_mismatch",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-2",
      "col_header": "MIC",
      "source_value": "25 – 49"
    },
    "short_reason": "For RaCa-2, Table 3 reports P. aeruginosa MIC 25-49, not the DB-claimed 20->78/39."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "multiple organisms",
      "endpoint": "MIC",
      "value": "S. aureus ATCC 6538P >78 ug/ml; S. pyogenes 39 ug/ml; P. aeruginosa ATCC 10148 20->78/39 ug/ml; E. coli ATCC 9723H 5-10 ug/ml; E. coli ATCC 25922 or MDR 2-10 ug/ml",
      "peptide": "RaCa-3"
    },
    "verification_outcome": "value_match",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-3",
      "col_header": "MIC",
      "source_value": "5 – 10"
    },
    "short_reason": "RaCa-3 claimed MIC values are represented in Table 3, but source reports μM while DB text uses ug/ml."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "multiple organisms",
      "endpoint": "MIC",
      "value": "S. aureus ATCC 6538P >88 ug/ml; S. pyogenes >2560 ug/ml; P. aeruginosa ATCC 10148 >2560 ug/ml; E. coli ATCC 9723H/ATCC 25922/MDR 6-44 ug/ml",
      "peptide": "RaCa-7"
    },
    "verification_outcome": "value_match",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-7",
      "col_header": "MIC",
      "source_value": "6 – 44"
    },
    "short_reason": "RaCa-7 claimed MIC range 6-44 is present in Table 3, but source reports μM while DB text uses ug/ml."
  },
  {
    "assertion_index": 4,
    "db_claimed": {
      "organism": "Escherichia coli NDM",
      "endpoint": "MIC",
      "value": "19-39 µM",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "No peptide is specified in the DB assertion, so no same peptide+organism+endpoint cell can be matched."
  },
  {
    "assertion_index": 5,
    "db_claimed": {
      "organism": "Escherichia coli NDM",
      "endpoint": "MBC",
      "value": "19-39 µM",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "No peptide is specified in the DB assertion, so no same peptide+organism+endpoint cell can be matched."
  },
  {
    "assertion_index": 6,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC 6538P",
      "endpoint": "MIC",
      "value": "1-3 µM",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "No peptide is specified in the DB assertion, so no same peptide+organism+endpoint cell can be matched."
  },
  {
    "assertion_index": 7,
    "db_claimed": {
      "organism": "",
      "endpoint": "literature DOI/PMID/PMCID link",
      "value": "",
      "peptide": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens"
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Provided longform cells contain table data only and no DOI/PMID/PMCID link cell for this assertion."
  },
  {
    "assertion_index": 8,
    "db_claimed": {
      "organism": "",
      "endpoint": "literature DOI/PMID/PMCID link",
      "value": "",
      "peptide": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens"
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Provided longform cells contain table data only and no DOI/PMID/PMCID link cell for this assertion."
  },
  {
    "assertion_index": 9,
    "db_claimed": {
      "organism": "",
      "endpoint": "literature DOI/PMID/PMCID link",
      "value": "",
      "peptide": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens"
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Provided longform cells contain table data only and no DOI/PMID/PMCID link cell for this assertion."
  },
  {
    "assertion_index": 10,
    "db_claimed": {
      "organism": "",
      "endpoint": "literature DOI/PMID/PMCID link",
      "value": "",
      "peptide": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens"
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Provided longform cells contain table data only and no DOI/PMID/PMCID link cell for this assertion."
  },
  {
    "assertion_index": 11,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC 6538P",
      "endpoint": "activity",
      "value": "NA",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "No peptide is specified in the DB assertion, so no same peptide+organism+endpoint cell can be matched."
  }
]