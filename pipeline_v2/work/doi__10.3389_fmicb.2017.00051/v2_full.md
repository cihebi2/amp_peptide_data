[
  {
    "assertion_index": 0,
    "db_claimed": {
      "organism": "Escherichia coli ATCC 8739; B. subtilis ATCC 11774; S. cerevisiae ATCC 9763",
      "endpoint": "MIC",
      "value": "128 microM; 16 microM; >128 microM",
      "peptide": ""
    },
    "verification_outcome": "not_in_provided_tables",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Provided tables only include Salmonella enterica and Listeria monocytogenes activity cells for NCR247/NCR335."
  },
  {
    "assertion_index": 1,
    "db_claimed": {
      "organism": "Salmonella enterica; Listeria monocytogenes; Candida albicans; Escherichia coli; Bacillus subtilis; Saccharomyces cerevisiae",
      "endpoint": "MIC; MBC; MFC",
      "value": "multiple values in db_subject_text",
      "peptide": ""
    },
    "verification_outcome": "cannot_determine",
    "normalization_note": "none",
    "is_database_error": false,
    "evidence": null,
    "short_reason": "Assertion lacks peptide identity; matching Salmonella/Listeria values require knowing whether the row is NCR247 or NCR335."
  }
]