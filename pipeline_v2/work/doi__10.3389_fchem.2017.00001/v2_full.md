[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "multiple organisms, including Klebsiella pneumoniae ATCC 13883",
      "endpoint": "MIC",
      "value": "multiple MIC claims including Klebsiella pneumoniae ATCC 13883 values 0.8+-0.0 microM, >100 microM, and 11.8+-0.1 microM",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "DB text aggregates many MICs and gives no peptide name; source MIC table uses coded variants, so same-peptide comparison cannot be verified."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Klebsiella pneumoniae 1102; Acinetobacter baumannii 30008; Klebsiella pneumoniae ATCC 13883",
      "endpoint": "MIC",
      "value": "Klebsiella pneumoniae 1102[MIC = 32-64 microg/ml], Klebsiella pneumoniae 1102[MIC >512 microg/ml], Acinetobacter baumannii 30008[MIC = 64 microg/ml], Acinetobacter baumannii 30008[MIC >512 microg/ml], Klebsiella pneumoniae ATCC 13883[MIC >100 microM]",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "The K. pneumoniae ATCC 13883 >100 value is only under coded variant columns; DB gives no peptide name, and other targets are not in provided cells."
  },
  {
    "assertion_index": 2,
    "db_claimed": {
      "organism": "Klebsiella pneumoniae 1102; Acinetobacter baumannii 30008; Klebsiella pneumoniae ATCC 13883",
      "endpoint": "MIC",
      "value": "Klebsiella pneumoniae 1102 (MIC=32-64μg/ml); Klebsiella pneumoniae 1102 (MIC=>512μg/ml); Acinetobacter baumannii 30008 (MIC=64μg/ml); Acinetobacter baumannii 30008 (MIC=>512μg/ml); Klebsiella pneumoniae ATCC 13883 (MIC=>100μM)",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "The K. pneumoniae ATCC 13883 >100 value is only under coded variant columns; DB gives no peptide name, and other targets are not in provided cells."
  }
]