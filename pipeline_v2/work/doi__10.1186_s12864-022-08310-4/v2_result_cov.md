[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "S. aureus ATCC 6538P; S. pyogenes; P. aeruginosa ATCC 10148; E. coli ATCC 9723H/25922/MDR CPO-NDM",
      "endpoint": "MIC",
      "value": "MIC>2560 ug/ml; 79 ug/ml; >2560 ug/ml; 10-39 ug/ml",
      "peptide": "RaCa-1"
    },
    "verification_outcome": "unit_differs",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-1",
      "col_header": "MIC",
      "source_value": "79"
    },
    "short_reason": "RaCa-1 MIC values are present, but DB mixes ug/ml with source µM, so numeric comparison cannot be direct."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "S. aureus ATCC 6538P; S. pyogenes; P. aeruginosa ATCC 10148; E. coli ATCC 9723H/25922/MDR",
      "endpoint": "MIC",
      "value": "1-2/1-2 ug/ml; 25-49 ug/ml; 20->78/39 ug/ml; 2-6 ug/ml",
      "peptide": "RaCa-2"
    },
    "verification_outcome": "unit_differs",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-2",
      "col_header": "MIC",
      "source_value": "1 – 2"
    },
    "short_reason": "RaCa-2 activity values are present, but DB states ug/ml while source Table 3 reports µM."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "S. aureus ATCC 6538P; S. pyogenes; P. aeruginosa ATCC 10148; E. coli ATCC 9723H/25922/MDR",
      "endpoint": "MIC",
      "value": ">78 ug/ml; 39 ug/ml; 20->78/39 ug/ml; 5-10 ug/ml; 2-10 ug/ml",
      "peptide": "RaCa-3"
    },
    "verification_outcome": "unit_differs",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-3",
      "col_header": "MIC",
      "source_value": "39"
    },
    "short_reason": "RaCa-3 values appear in provided cells, but DB reports ug/ml and source Table 3 reports µM."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "S. aureus ATCC 6538P; S. pyogenes; P. aeruginosa ATCC 10148; E. coli ATCC 9723H/25922/MDR",
      "endpoint": "MIC",
      "value": ">88 ug/ml; >2560 ug/ml; >2560 ug/ml; 6-44 ug/ml",
      "peptide": "RaCa-7"
    },
    "verification_outcome": "unit_differs",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-7",
      "col_header": "MIC",
      "source_value": "≥ 88"
    },
    "short_reason": "RaCa-7 source values are present, but DB uses ug/ml while source Table 3 uses µM."
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
    "short_reason": "No peptide is named, and no provided longform cell contains MIC 19-39 µM for E. coli NDM."
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
    "short_reason": "No peptide is named, and no provided longform cell contains MBC 19-39 µM for E. coli NDM."
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
    "short_reason": "No peptide is named, and no provided S. aureus MIC cell has value 1-3 µM."
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
    "short_reason": "Provided longform cells contain table data only, not DOI/PMID/PMCID database-link assertions."
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
    "short_reason": "Provided longform cells contain table data only, not DOI/PMID/PMCID database-link assertions."
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
    "short_reason": "Provided longform cells contain table data only, not DOI/PMID/PMCID database-link assertions."
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
    "short_reason": "Provided longform cells contain table data only, not DOI/PMID/PMCID database-link assertions."
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
    "short_reason": "No peptide is named, and the provided cells do not contain an activity NA value."
  }
]