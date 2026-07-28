[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "80% Hemolysis",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Hemolysis data are not present in provided longform table cells."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Tumor cells: U-251MG; PC-3; NCI-H460",
      "endpoint": "Antimicrobial, Anticancer",
      "value": "IC50=1.8µM; IC50=2.9µM; IC50=4.3µM",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Cancer-cell IC50 data are not present in provided longform table cells."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Human erythrocytes",
      "endpoint": "80% Hemolysis",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Hemolysis data are not present in provided longform table cells."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "Tumor cells: U-251MG; PC-3; NCI-H460",
      "endpoint": "Antimicrobial, Anticancer",
      "value": "IC50=1.8µM; IC50=2.9µM; IC50=4.3µM",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Cancer-cell IC50 data are not present in provided longform table cells."
  },
  {
    "assertion_index": 4,
    "db_claimed": {
      "organism": "S. aureus; E. coli; C. albicans",
      "endpoint": "MIC",
      "value": "8mg/L; 128mg/L; 8g/L",
      "peptide": ""
    },
    "verification_outcome": "value_mismatch",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "Phylloseptin-PBa",
      "col_header": "C. albicans",
      "source_value": "8"
    },
    "short_reason": "C. albicans MIC value matches numerically, but DB unit says g/L while source table is MIC (mg/L)."
  },
  {
    "assertion_index": 5,
    "db_claimed": {
      "organism": "Human microvascular endothelial cells HMEC-1",
      "endpoint": "IC50",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "HMEC-1 IC50 data are not present in provided longform table cells."
  },
  {
    "assertion_index": 6,
    "db_claimed": {
      "organism": "Horse erythrocytes",
      "endpoint": "1.4% Hemolysis",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Horse erythrocyte hemolysis data are not present in provided longform table cells."
  },
  {
    "assertion_index": 7,
    "db_claimed": {
      "organism": "Staphylococcus aureus NCTC 10788",
      "endpoint": "MBC",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "Phylloseptin-PBa",
      "col_header": "S. aureus",
      "source_value": "8"
    },
    "short_reason": "Provided table reports Phylloseptin-PBa MBC for S. aureus as 8 mg/L."
  },
  {
    "assertion_index": 8,
    "db_claimed": {
      "organism": "Escherichia coli NCTC 10418",
      "endpoint": "MBC",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "Phylloseptin-PBa",
      "col_header": "E. coli",
      "source_value": ">512"
    },
    "short_reason": "Provided table reports Phylloseptin-PBa MBC for E. coli as >512 mg/L."
  },
  {
    "assertion_index": 9,
    "db_claimed": {
      "organism": "Candida albicans NCYC 1467",
      "endpoint": "MBC",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 1,
      "row_label": "Phylloseptin-PBa",
      "col_header": "C. albicans",
      "source_value": "8"
    },
    "short_reason": "Provided table reports Phylloseptin-PBa MBC for C. albicans as 8 mg/L."
  },
  {
    "assertion_index": 10,
    "db_claimed": {
      "organism": "Human lung carcinoma NCI-H460",
      "endpoint": "IC50",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "NCI-H460 IC50 data are not present in provided longform table cells."
  },
  {
    "assertion_index": 11,
    "db_claimed": {
      "organism": "Human prostate adenocarcinoma PC-3",
      "endpoint": "IC50",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "PC-3 IC50 data are not present in provided longform table cells."
  }
]