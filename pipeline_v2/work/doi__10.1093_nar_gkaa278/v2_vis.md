[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Staphylococcus aureus FusA88700",
      "endpoint": "MIC",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "No provided cell reports a blank MIC assertion for S. aureus FusA88700."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Staphylococcus aureus FusA88700",
      "endpoint": "MIC",
      "value": "",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "No provided cell reports a blank MIC assertion for S. aureus FusA88700."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Escherichia coli MG1655",
      "endpoint": "MIC",
      "value": "14.5 microM",
      "peptide": ""
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 5,
      "row_label": "R11",
      "col_header": "E. coli MG1655 MIC (µM)",
      "source_value": "14.5"
    },
    "short_reason": "DB text includes E. coli MG1655 MIC 14.5 microM; provided cell reports the same MIC value."
  },
  {
    "assertion_index": 3,
    "db_claimed": {
      "organism": "Staphylococcus aureus FusA88700",
      "endpoint": "MIC",
      "value": "3 microM",
      "peptide": ""
    },
    "verification_outcome": "value_match",
    "normalization_note": "strain_id_differs_value_same",
    "is_database_error": false,
    "evidence": {
      "table_index": 5,
      "row_label": "S.aureus FusA88799",
      "col_header": "RWLVK MIC (µM)",
      "source_value": "3"
    },
    "short_reason": "Same species, endpoint, and MIC value are present; only the FusA strain identifier differs."
  }
]