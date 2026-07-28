[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Klebsiella pneumoniae M6",
      "endpoint": "MIC in MHB",
      "value": "128 microg/ml",
      "peptide": "Temporin B L1FK"
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "Klebsiella pneumoniae M6",
      "col_header": "MHB",
      "source_value": "128"
    },
    "short_reason": "DB names L1FK, but the MIC series uses KKG6A values; e.g. K. pneumoniae M6 MHB 128 is in the KKG6A columns, not L1FK."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Klebsiella pneumoniae M6",
      "endpoint": "MIC in MHB",
      "value": "32 microg/ml",
      "peptide": "Temporin B KKG6A"
    },
    "verification_outcome": "variant_misattribution",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 2,
      "row_label": "Klebsiella pneumoniae M6",
      "col_header": "MHB",
      "source_value": "32"
    },
    "short_reason": "DB names KKG6A, but the MIC series uses L1FK values; e.g. K. pneumoniae M6 MHB 32 belongs to the L1FK columns, not KKG6A."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Klebsiella pneumoniae M6",
      "endpoint": "MIC in MHB",
      "value": "32 microg/ml",
      "peptide": "Temporin B L1FK"
    },
    "verification_outcome": "value_match",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": {
      "table_index": 2,
      "row_label": "Klebsiella pneumoniae M6",
      "col_header": "MHB",
      "source_value": "32"
    },
    "short_reason": "Provided MIC cells match the L1FK series; extra MBC/IC50 entries are not in the provided tables and are not used as error evidence."
  }
]