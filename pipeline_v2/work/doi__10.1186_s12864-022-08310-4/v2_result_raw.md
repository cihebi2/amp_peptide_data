[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC 6538P; Streptococcus pyogenes; Pseudomonas aeruginosa ATCC 10148; Escherichia coli ATCC 9723H/ATCC 25922/MDR CPO-NDM",
      "endpoint": "MIC",
      "value": "S. aureus >2560 ug/ml; S. pyogenes 79 ug/ml; P. aeruginosa >2560 ug/ml; E. coli 10-39 ug/ml",
      "peptide": "RaCa-1"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB reports ug/ml values, but provided tables report uM ranges; no matching source cell supports direct value comparison."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC 6538P",
      "endpoint": "MIC",
      "value": "1-2/1-2 ug/ml",
      "peptide": "RaCa-2"
    },
    "verification_outcome": "value_match",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-2",
      "col_header": "MIC",
      "source_value": "1 – 2"
    },
    "short_reason": "Same peptide and MIC value range is present; DB unit differs from source table unit."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC 6538P",
      "endpoint": "MIC",
      "value": ">78 ug/ml",
      "peptide": "RaCa-3"
    },
    "verification_outcome": "value_match",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-3",
      "col_header": "MIC",
      "source_value": "≥78"
    },
    "short_reason": "Same peptide and MIC threshold is present; DB uses >78 and ug/ml while source reports ≥78 in uM."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC 6538P",
      "endpoint": "MIC",
      "value": ">88 ug/ml",
      "peptide": "RaCa-7"
    },
    "verification_outcome": "value_match",
    "normalization_note": "unit_differs",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "RaCa-7",
      "col_header": "MIC",
      "source_value": "≥ 88"
    },
    "short_reason": "Same peptide and MIC threshold is present; DB uses >88 and ug/ml while source reports ≥ 88 in uM."
  },
  {
    "assertion_index": 4,
    "db_claimed": {
      "organism": "Escherichia coli NDM",
      "endpoint": "MIC",
      "value": "19-39 µM",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "No peptide is named in the database assertion, so the matching source row cannot be determined."
  },
  {
    "assertion_index": 5,
    "db_claimed": {
      "organism": "Escherichia coli NDM",
      "endpoint": "MBC",
      "value": "19-39 µM",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "No peptide is named in the database assertion, so the matching source row cannot be determined."
  },
  {
    "assertion_index": 6,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC 6538P",
      "endpoint": "MIC",
      "value": "1-3 µM",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "No peptide is named in the database assertion, so the matching source row cannot be determined."
  },
  {
    "assertion_index": 7,
    "db_claimed": {
      "organism": "",
      "endpoint": "literature DOI/PMID/PMCID link",
      "value": "",
      "peptide": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Provided longform cells contain table data only and no DOI/PMID/PMCID link evidence."
  },
  {
    "assertion_index": 8,
    "db_claimed": {
      "organism": "",
      "endpoint": "literature DOI/PMID/PMCID link",
      "value": "",
      "peptide": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Provided longform cells contain table data only and no DOI/PMID/PMCID link evidence."
  },
  {
    "assertion_index": 9,
    "db_claimed": {
      "organism": "",
      "endpoint": "literature DOI/PMID/PMCID link",
      "value": "",
      "peptide": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Provided longform cells contain table data only and no DOI/PMID/PMCID link evidence."
  },
  {
    "assertion_index": 10,
    "db_claimed": {
      "organism": "",
      "endpoint": "literature DOI/PMID/PMCID link",
      "value": "",
      "peptide": "AMPlify: attentive deep learning model for discovery of novel antimicrobial peptides effective against WHO priority pathogens"
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Provided longform cells contain table data only and no DOI/PMID/PMCID link evidence."
  },
  {
    "assertion_index": 11,
    "db_claimed": {
      "organism": "Staphylococcus aureus ATCC 6538P",
      "endpoint": "activity",
      "value": "NA",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "No peptide is named and activity NA is not a table endpoint/value that can be matched to a provided source cell."
  }
]