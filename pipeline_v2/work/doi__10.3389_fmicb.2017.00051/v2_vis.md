[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Escherichia coli ATCC 8739; Bacillus subtilis ATCC 11774; Saccharomyces cerevisiae ATCC 9763",
      "endpoint": "MIC",
      "value": "128 microM; 16 microM; >128 microM",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Provided cells contain no E. coli, B. subtilis, or S. cerevisiae MIC rows."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "multiple organisms",
      "endpoint": "multiple endpoints",
      "value": "multiple values",
      "peptide": ""
    },
    "verification_outcome": "value_match",
    "normalization_note": "strain_id_differs_value_same",
    "is_database_error": false,
    "evidence": {
      "table_index": 3,
      "row_label": "NCR335 (μM)",
      "col_header": "MIC and MBC (μM) / Gram-negative / S. enterica / MIC",
      "source_value": "16"
    },
    "short_reason": "Salmonella MIC/MBC and Listeria MIC/MBC values match provided NCR335 cells despite DB strain IDs; other listed targets are not in provided tables."
  }
]