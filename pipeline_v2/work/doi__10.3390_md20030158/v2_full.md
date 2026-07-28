[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Human breast adenocarcinoma MDA-MB-231",
      "endpoint": "IC50",
      "value": "11.33±2.95 μg/mL",
      "peptide": "Galaxamide"
    },
    "verification_outcome": "value_mismatch",
    "normalization_note": "none",
    "is_database_error": true,
    "evidence": {
      "table_index": 1,
      "row_label": "galaxamide",
      "col_header": "MD-MBA-231",
      "source_value": "8.73 ± 0.29"
    },
    "short_reason": "For galaxamide in MD-MBA-231, source IC50 is 8.73 ± 0.29, not the DB value 11.33±2.95."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Human breast adenocarcinoma MDA-MB-231",
      "endpoint": "IC50",
      "value": "11.33±2.95 μg/mL",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB assertion has no peptide name or sequence, so the value cannot be anchored to a specific source row."
  }
]